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
        self.download_dir = settings.data.download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def download_chunk(self, prefix: str) -> list[str]:
        """Downloads a chunk of .nc files from S3 based on a prefix."""
        logger.info(f"Downloading chunk with prefix: {prefix}")
        # Implementation of boto3 list_objects and download_file goes here
        # Return list of downloaded file paths
        return []

    def _convert_nc_to_bt_tensor(self, nc_path: str, pt_path: str) -> None:
        """Converts raw radiance .nc file to normalized Brightness Temperature .pt tensor."""
        logger.debug(f"Processing physical BT for {nc_path}")
        ds = xr.open_dataset(nc_path)

        # Simplified cropping logic assuming the data is already somewhat manageable
        # or cropping is handled by specific lat/lon boundaries.
        # For demonstration, selecting a 512x512 slice
        start_y, start_x = 500, 500
        try:
            ds_cropped = ds.isel(
                y=slice(start_y, start_y + 512), x=slice(start_x, start_x + 512)
            )
        except (ValueError, IndexError):
            ds_cropped = ds  # Fallback if dimensions are smaller

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

        # Convert to tensor and save
        tensor = (
            torch.from_numpy(bt_norm.values).float().unsqueeze(0)
        )  # Shape: [1, H, W]
        torch.save(tensor, pt_path)
        ds.close()

    def purge_raw_files(self) -> None:
        """Deletes massive .nc files to save disk space."""
        files = glob.glob(os.path.join(self.download_dir, "*.nc"))
        for f in files:
            os.remove(f)
        logger.info(f"Purged {len(files)} raw .nc files.")

    def purge_chunk(self) -> None:
        """Deletes .pt files after training chunk is complete."""
        files = glob.glob(os.path.join(self.download_dir, "*.pt"))
        for f in files:
            os.remove(f)
        logger.info(f"Purged {len(files)} processed .pt files.")
