import glob
import logging
import os
import concurrent.futures

import boto3
import numpy as np
import torch
import torch.nn.functional as F
import xarray as xr
from botocore import UNSIGNED
from botocore.config import Config

from src.config.settings import Settings

logger = logging.getLogger(__name__)

class S3Manager:
    """Manages downloading GOES data, Argmax Motion-Guided Cropping, and purging."""

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
        
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        c13_files = [obj['Key'] for obj in response.get('Contents', []) if 'M6C13' in obj['Key'] and obj['Key'].endswith('.nc')]
        c13_files = sorted(c13_files)
        
        if len(c13_files) < 3:
            logger.warning(f"Not enough files in prefix {prefix} to form a triplet.")
            return

        step = self.settings.data.frame_step
        crop_size = self.settings.data.crop_size

        def fetch_file(key):
            filename = key.split('/')[-1]
            local_path = os.path.join(self.raw_dir, filename)
            if not os.path.exists(local_path):
                logger.info(f"Downloading {filename}...")
                thread_s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
                thread_s3.download_file(self.bucket_name, key, local_path)
            return local_path

        # Concurrent downloading (Fixes network bottleneck)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            local_nc_paths = list(executor.map(fetch_file, c13_files))

        # 3. Create Triplets using Argmax Motion Map (Solves Problem 3 & 4)
        for i in range(len(local_nc_paths) - 2 * step):
            try:
                # SOLVING PROBLEM 3: Load full array into RAM exactly ONCE per file.
                t0_full = self._load_full_tensor(local_nc_paths[i])
                t2_full = self._load_full_tensor(local_nc_paths[i + 2 * step])
                
                # SOLVING PROBLEM 4: Create full motion map abs(t2 - t0)
                motion_map = torch.abs(t2_full - t0_full) # Shape: [1, H, W]
                
                # Ignore empty space (Outer space padding = 0.0)
                space_mask = (t0_full > 0.0).float()
                motion_map = motion_map * space_mask
                
                # Add batch dimension for pooling: [1, 1, H, W]
                motion_map_4d = motion_map.unsqueeze(0) 
                
                # Use PyTorch AvgPool2d to find the 256x256 window with maximum average motion
                stride = 64
                pooled_motion = F.avg_pool2d(motion_map_4d, kernel_size=crop_size, stride=stride)
                
                # Find argmax (highest motion density) - BUG FIXED WITH .item()
                b, c, h_out, w_out = pooled_motion.shape
                flat_idx = torch.argmax(pooled_motion).item() # <--- Added .item() here
                y_out = flat_idx // w_out
                x_out = flat_idx % w_out
                
                # Map pooled coordinates back to actual image coordinates
                best_start_y = y_out * stride
                best_start_x = x_out * stride
                
                # SOLVING PROBLEM 1: Log the exact motion score to study distribution instead of magic numbers
                best_motion = pooled_motion.flatten()[flat_idx].item()
                logger.info(f"Motion-Guided Argmax Crop mapped at Y:{best_start_y}, X:{best_start_x} | Motion Score: {best_motion:.5f}")
                
                # Slice the exact best crop directly from RAM
                t0_crop = t0_full[:, best_start_y:best_start_y+crop_size, best_start_x:best_start_x+crop_size]
                t2_crop = t2_full[:, best_start_y:best_start_y+crop_size, best_start_x:best_start_x+crop_size]
                
                # SAFETY FILTER: Agar argmax ne bhi low-motion kachra uthaya hai, toh reject karo
                crop_motion = torch.abs(t2_crop - t0_crop).mean().item()
                if crop_motion < 0.005:
                    logger.warning(f"⏩ Argmax crop too static (Score: {crop_motion:.5f}). Skipping.")
                    continue
                    
              
                # Load T1 (Present) and slice using the exact same coordinates
                t1_full = self._load_full_tensor(local_nc_paths[i + step])
                t1_crop = t1_full[:, best_start_y:best_start_y+crop_size, best_start_x:best_start_x+crop_size]                
                # Save Triplet
                triplet_tensor = torch.stack([t0_crop, t1_crop, t2_crop], dim=0)
                safe_prefix = prefix.replace("/", "_")
                pt_filename = os.path.join(self.pt_dir, f'triplet_{safe_prefix}_{i:03d}.pt')
                
                torch.save(triplet_tensor, pt_filename)
                
            except Exception as e:
                logger.error(f"Error processing argmax triplet {i}: {e}")
                continue

        self.purge_raw_files()
        logger.info(f"Chunk converted to .pt triplets. Raw .nc files purged.")

    def _load_full_tensor(self, nc_path: str) -> torch.Tensor:
        """Loads the ENTIRE NetCDF image into memory ONCE to prevent 30x disk reads."""
        with xr.open_dataset(nc_path) as ds:
            rad = ds["Rad"]
            fk1 = ds["planck_fk1"].values
            fk2 = ds["planck_fk2"].values
            bc1 = ds["planck_bc1"].values
            bc2 = ds["planck_bc2"].values

            rad_safe = rad.where(rad > 0)
            bt = (fk2 / np.log((fk1 / rad_safe) + 1) - bc1) / bc2

            min_bt, max_bt = 180.0, 330.0
            bt_norm = (bt - min_bt) / (max_bt - min_bt)
            bt_norm = bt_norm.clip(0, 1)

            clean_numpy_array = np.nan_to_num(bt_norm.values, nan=0.0, posinf=1.0, neginf=0.0)
            tensor = torch.from_numpy(clean_numpy_array).float().unsqueeze(0)
            
        return tensor

    def purge_raw_files(self) -> None:
        for f in glob.glob(os.path.join(self.raw_dir, "*.nc")):
            os.remove(f)
            
    def purge_chunk(self) -> None:
        for f in glob.glob(os.path.join(self.pt_dir, "*.pt")):
            os.remove(f)
        logger.info("Purged trained .pt chunk from disk.")