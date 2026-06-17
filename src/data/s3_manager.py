import glob
import logging
import os
import random

import boto3
import numpy as np
import torch
import xarray as xr
from botocore import UNSIGNED
from botocore.config import Config

from src.config.settings import Settings

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        self.bucket_name = settings.data.s3_bucket
        
        self.pt_dir = settings.data.download_dir
        self.raw_dir = os.path.join(self.pt_dir, "raw_nc")
        
        os.makedirs(self.pt_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)

    def download_chunk(self, prefix: str) -> None:
        logger.info(f"Fetching chunk from S3: {prefix}")
        
        # 1. Fetch File List from AWS
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        c13_files = [obj['Key'] for obj in response.get('Contents', []) if 'M6C13' in obj['Key'] and obj['Key'].endswith('.nc')]
        c13_files = sorted(c13_files) # IMPORTANT: Ensure chronological order
        
        if len(c13_files) < 3:
            logger.warning(f"Not enough files in prefix {prefix} to form a triplet.")
            return

        step = self.settings.data.frame_step
        crop_size = self.settings.data.crop_size

        # 2. Download Raw .nc files (Downloads full day, safe for Kaggle limits ~3-4GB)
        local_nc_paths = []
        for key in c13_files:
            filename = key.split('/')[-1]
            local_path = os.path.join(self.raw_dir, filename)
            local_nc_paths.append(local_path)
            
            if not os.path.exists(local_path):
                logger.info(f"Downloading {filename}...")
                self.s3_client.download_file(self.bucket_name, key, local_path)

        # 3. Create Triplets with Temporal Gap and Random Cropping
        for i in range(len(local_nc_paths) - 2 * step):
            # Dynamic Random Crop (Applied identically to t0, t1, t2)
            # Safe bounds for GOES CONUS (1500x2500)
            start_y = random.randint(0, 1000) 
            start_x = random.randint(0, 1500)

            try:
                t0 = self._process_single_frame(local_nc_paths[i], start_y, start_x, crop_size)
                t1 = self._process_single_frame(local_nc_paths[i + step], start_y, start_x, crop_size)
                t2 = self._process_single_frame(local_nc_paths[i + 2 * step], start_y, start_x, crop_size)
                
                triplet_tensor = torch.stack([t0, t1, t2], dim=0) # [3, 1, H, W]
                safe_prefix = prefix.replace("/", "_")
                pt_filename = os.path.join(self.pt_dir, f'triplet_{safe_prefix}_{i:03d}.pt')
                
                torch.save(triplet_tensor, pt_filename)
            except Exception as e:
                logger.error(f"Error processing triplet {i}: {e}")
                continue

        # 4. Purge .nc files
        self.purge_raw_files()
        logger.info(f"Chunk converted to .pt triplets. Raw .nc files purged.")

    def _process_single_frame(self, nc_path: str, start_y: int, start_x: int, crop_size: int) -> torch.Tensor:
        ds = xr.open_dataset(nc_path)

        try:
            ds_cropped = ds.isel(y=slice(start_y, start_y + crop_size), x=slice(start_x, start_x + crop_size))
        except (ValueError, IndexError):
            ds_cropped = ds

        rad = ds_cropped["Rad"]
        fk1 = ds_cropped["planck_fk1"].values
        fk2 = ds_cropped["planck_fk2"].values
        bc1 = ds_cropped["planck_bc1"].values
        bc2 = ds_cropped["planck_bc2"].values

        rad_safe = rad.where(rad > 0)
        bt = (fk2 / np.log((fk1 / rad_safe) + 1) - bc1) / bc2

        min_bt, max_bt = 180.0, 330.0
        bt_norm = (bt - min_bt) / (max_bt - min_bt)
        bt_norm = bt_norm.clip(0, 1)

        tensor = torch.from_numpy(bt_norm.values).float().unsqueeze(0)
        ds.close()
        return tensor

    def purge_raw_files(self) -> None:
        for f in glob.glob(os.path.join(self.raw_dir, "*.nc")):
            os.remove(f)
            
    def purge_chunk(self) -> None:
        for f in glob.glob(os.path.join(self.pt_dir, "*.pt")):
            os.remove(f)
        logger.info("Purged trained .pt chunk from disk.")