import os
import glob
import logging
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import numpy as np
import torch
from satpy import Scene

from src.data.fetchers.base_fetcher import SatelliteFetcher

logger = logging.getLogger(__name__)


class HimawariFetcher(SatelliteFetcher):
    """
    Himawari-8/9 AHI Full Disk Fetcher
    Band 14 (11.2 µm)
    """

    def __init__(self, bucket_name: str = "noaa-himawari9"):
        super().__init__(bucket_name)

        self.s3_client = boto3.client(
            "s3",
            config=Config(signature_version=UNSIGNED, max_pool_connections=50)
        )

    def fetch_chunk(self, chunk_prefix: str, output_dir: str = None) -> list[list[str]]:
        paginator = self.s3_client.get_paginator("list_objects_v2")
        all_b14_files = []

        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=chunk_prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if "B14" in key and key.endswith(".DAT.bz2"):
                    all_b14_files.append(key)

        if not all_b14_files:
            raise ValueError(f"No B14 files found for {chunk_prefix}")

        timestamp_groups = {}
        for key in all_b14_files:
            filename = os.path.basename(key)
            parts = filename.split("_")
            timestamp = f"{parts[2]}_{parts[3]}"

            if timestamp not in timestamp_groups:
                timestamp_groups[timestamp] = []
            timestamp_groups[timestamp].append(key)

        frames = []
        for timestamp in sorted(timestamp_groups.keys()):
            segment_files = sorted(timestamp_groups[timestamp])
            if len(segment_files) != 10:
                logger.warning(f"Skipping incomplete frame {timestamp} ({len(segment_files)} segments)")
                continue
            frames.append(segment_files)

        return frames

    def fetch_frame(self, frame_keys: list[str], output_dir: str) -> str:
        filename = os.path.basename(frame_keys[0])
        parts = filename.split("_")
        timestamp = f"{parts[2]}_{parts[3]}"
        timestamp_dir = os.path.join(output_dir, timestamp)
        os.makedirs(timestamp_dir, exist_ok=True)

        for file_key in frame_keys:
            filename = os.path.basename(file_key)
            local_path = os.path.join(timestamp_dir, filename)
            if not os.path.exists(local_path):
                self.s3_client.download_file(self.bucket_name, file_key, local_path)

        return timestamp_dir

    def fetch_single_file(self, exact_prefix: str, output_dir: str) -> str:
        frame_keys = self.fetch_chunk(exact_prefix)[0]
        return self.fetch_frame(frame_keys, output_dir)

    def apply_planck_function(self, raw_data_path: str) -> torch.Tensor:
        logger.debug(f"[Himawari] Loading frame from {raw_data_path}")
        file_paths = sorted(glob.glob(os.path.join(raw_data_path, "*_B14_FLDK_R20_S*.DAT.bz2")))

        if len(file_paths) != 10:
            raise ValueError(f"Incomplete Himawari frame: {len(file_paths)} segments found")

        scn = Scene(reader="ahi_hsd", filenames=file_paths)
        scn.load(["B14"], calibration="brightness_temperature")
        bt_data = scn["B14"].values
        clean_numpy_array = np.nan_to_num(bt_data, nan=0.0, posinf=330.0, neginf=180.0)

        tensor = torch.from_numpy(clean_numpy_array).float().unsqueeze(0)
        return tensor

    # 🚀 NAYA SOTA METHOD: In-Memory Streaming
    def stream_and_apply_planck(self, frame_keys: list[str]) -> torch.Tensor:
        """
        Streams 10 Himawari segment files directly from AWS S3 into RAM,
        decompresses them, stitches them, and applies Planck calibration
        WITHOUT writing a single byte to the hard disk.
        """
        logger.debug("[Himawari] Streaming 10 segments directly to RAM...")

        s3_uris = [f"s3://{self.bucket_name}/{key}" for key in frame_keys]

        scn = Scene(
            reader="ahi_hsd",
            filenames=s3_uris,
            reader_kwargs={'storage_options': {'anon': True}}
        )

        scn.load(["B14"], calibration="brightness_temperature")
        bt_data = scn["B14"].values
        clean_numpy = np.nan_to_num(bt_data, nan=0.0, posinf=330.0, neginf=180.0)
        
        tensor = torch.from_numpy(clean_numpy).float().unsqueeze(0)
        return tensor