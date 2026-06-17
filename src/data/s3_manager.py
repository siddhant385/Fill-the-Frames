import glob
import logging
import os

import boto3
import numpy as np
import torch
import xarray as xr
from botocore import UNSIGNED
from botocore.config import Config

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class S3Manager:
    """Manages downloading GOES data from AWS S3, converting it, and purging raw files."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        self.bucket_name = settings.data.s3_bucket
        
        self.pt_dir = settings.data.download_dir
        self.raw_dir = os.path.join(self.pt_dir, "raw_nc")
        
        os.makedirs(self.pt_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)

    def download_chunk(self, prefix: str) -> None:
        """Downloads a chunk of .nc files, creates .pt triplets, and deletes .nc files."""
        logger.info(f"Fetching chunk from S3: {prefix}")
        
        # 1. Fetch File List from AWS
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        c13_files = [obj['Key'] for obj in response.get('Contents', []) if 'M6C13' in obj['Key'] and obj['Key'].endswith('.nc')]
        
        if len(c13_files) < 3:
            logger.warning(f"Not enough files in prefix {prefix} to form a triplet.")
            return

        # Let's take the first 6 files to form a good chunk of triplets
        c13_files = c13_files[:6]
        local_nc_paths = []

        # 2. Download Raw .nc files
        for key in c13_files:
            filename = key.split('/')[-1]
            local_path = os.path.join(self.raw_dir, filename)
            local_nc_paths.append(local_path)
            
            if not os.path.exists(local_path):
                logger.info(f"Downloading {filename}...")
                self.s3_client.download_file(self.bucket_name, key, local_path)

        # 3. Create Triplets and Convert to .pt
        for i in range(len(local_nc_paths) - 2):
            try:
                t0 = self._process_single_frame(local_nc_paths[i])
                t1 = self._process_single_frame(local_nc_paths[i+1])
                t2 = self._process_single_frame(local_nc_paths[i+2])
                
                triplet_tensor = torch.stack([t0, t1, t2], dim=0) # Shape: [3, 1, H, W]
                safe_prefix = prefix.replace("/", "_")
                pt_filename = os.path.join(self.pt_dir, f'triplet_{safe_prefix}_{i:03d}.pt')
                
                torch.save(triplet_tensor, pt_filename)
            except Exception as e:
                logger.error(f"Error processing triplet {i}: {e}")
                continue

        # 4. Immediately delete massive .nc files to save Kaggle storage
        self.purge_raw_files()
        logger.info(f"Chunk converted to .pt triplets. Raw .nc files purged.")

    def _process_single_frame(self, nc_path: str) -> torch.Tensor:
        """Converts raw radiance .nc file to normalized Brightness Temperature .pt tensor."""
        ds = xr.open_dataset(nc_path)

        start_y, start_x = 500, 500
        try:
            ds_cropped = ds.isel(y=slice(start_y, start_y + 256), x=slice(start_x, start_x + 256))
        except (ValueError, IndexError):
            ds_cropped = ds

        rad = ds_cropped["Rad"]
        fk1 = ds_cropped["planck_fk1"].values
        fk2 = ds_cropped["planck_fk2"].values
        bc1 = ds_cropped["planck_bc1"].values
        bc2 = ds_cropped["planck_bc2"].values

        rad_safe = rad.where(rad > 0)
        bt = (fk2 / np.log((fk1 / rad_safe) + 1) - bc1) / bc2

        # Normalize
        min_bt, max_bt = 180.0, 330.0
        bt_norm = (bt - min_bt) / (max_bt - min_bt)
        bt_norm = bt_norm.clip(0, 1)

        tensor = torch.from_numpy(bt_norm.values).float().unsqueeze(0)
        ds.close()
        return tensor

    def purge_raw_files(self) -> None:
        """Deletes massive .nc files."""
        for f in glob.glob(os.path.join(self.raw_dir, "*.nc")):
            os.remove(f)
            
    def purge_chunk(self) -> None:
        """Deletes processed .pt files AFTER the trainer is done with them."""
        for f in glob.glob(os.path.join(self.pt_dir, "*.pt")):
            os.remove(f)
        logger.info("Purged trained .pt chunk from disk.")