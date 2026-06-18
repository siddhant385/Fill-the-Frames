import os
import glob
import shutil
import logging
import torch
import torch.nn.functional as F
import concurrent.futures

from src.config.settings import Settings
from src.data.fetchers.goes_fetcher import GOESFetcher
from src.data.fetchers.himawari_fetcher import HimawariFetcher
from src.data.standardizer import UniversalStandardizer

logger = logging.getLogger(__name__)


class DataManager:
    """
    Universal multi-satellite data pipeline manager.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.pt_dir = settings.data.download_dir
        self.raw_dir = os.path.join(self.pt_dir, "raw_data")

        os.makedirs(self.pt_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)

        sat_type = getattr(settings.data, "satellite_type", "goes").lower()

        if sat_type == "goes":
            self.fetcher = GOESFetcher(
                bucket_name=settings.data.s3_bucket
            )
        elif sat_type == "himawari":
            self.fetcher = HimawariFetcher(
                bucket_name=settings.data.s3_bucket
            )
        else:
            raise ValueError(f"Unsupported satellite type: {sat_type}")
    

    def process_chunk(self, chunk_prefix: str) -> None:
        logger.info(f"Processing chunk {chunk_prefix}")

        frame_keys = self.fetcher.fetch_chunk(chunk_prefix)

        if len(frame_keys) < 3:
            logger.warning("Not enough frames for triplets.")
            return

        frame_step = self.settings.data.frame_step
        tensor_cache = {}

        # 🚀 HELPER: Streams ONLY the missing frames for the current triplet in parallel
        def fetch_triplet_to_ram(keys):
            missing = [k for k in keys if k not in tensor_cache]
            if missing:
                def _stream(k):
                    # Convert back to list if it's a tuple (for Himawari 10 segments)
                    actual_key = list(k) if isinstance(k, tuple) else k
                    raw = self.fetcher.stream_and_apply_planck(actual_key)
                    return k, UniversalStandardizer.normalize_bt(
                        raw, self.settings.data.min_bt, self.settings.data.max_bt
                    )
                
                # Fetch only the missing 1, 2, or 3 frames concurrently into RAM
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    for k, tensor in executor.map(_stream, missing):
                        tensor_cache[k] = tensor

        logger.info("🔥 Starting Zero-Disk In-Memory Streaming...")
        
        # 2. Main Processing Loop
        for i in range(len(frame_keys) - 2 * frame_step):
            try:
                # 🚨 SOTA FIX: Convert list to tuple so it can be used as a Dictionary Key!
                k0 = tuple(frame_keys[i]) if isinstance(frame_keys[i], list) else frame_keys[i]
                k1 = tuple(frame_keys[i + frame_step]) if isinstance(frame_keys[i + frame_step], list) else frame_keys[i + frame_step]
                k2 = tuple(frame_keys[i + 2 * frame_step]) if isinstance(frame_keys[i + 2 * frame_step], list) else frame_keys[i + 2 * frame_step]

                # 1. Fetch exactly what is needed right now to RAM
                fetch_triplet_to_ram([k0, k1, k2])

                # 2. Extract from RAM cache
                img0 = tensor_cache[k0]
                gt   = tensor_cache[k1]
                img1 = tensor_cache[k2]

                # 3. Fast Crop
                img0_crop, img1_crop, gt_crop = self._motion_guided_argmax_crop(img0, img1, gt)

                # 4. Save Triplet directly to disk
                safe_prefix = chunk_prefix.replace("/", "_")
                pt_filename = os.path.join(self.pt_dir, f"triplet_{safe_prefix}_{i:03d}.pt")

                triplet_tensor = torch.stack([img0_crop, gt_crop, img1_crop], dim=0)
                torch.save(triplet_tensor, pt_filename)

                # 🚀 SMART MEMORY MANAGEMENT
                # k0 will not be used in future iterations, so clear it from RAM
                if k0 in tensor_cache:
                    del tensor_cache[k0]

            except Exception as e:
                logger.error(f"Triplet failed ({i}): {e}")
                continue
        
        # 3. Cleanup
        tensor_cache.clear()
        self.purge_raw_files() # Kept for fallback cleanup
        logger.info("Chunk processing complete. Zero raw files written to disk!")
    
    def _delete_temp(self, path: str):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def _motion_guided_argmax_crop(
        self,
        img0: torch.Tensor,
        img1: torch.Tensor,
        gt: torch.Tensor
    ):
        crop_size = self.settings.data.crop_size
        _, h, w = img0.shape

        if h < crop_size or w < crop_size:
            raise ValueError(f"Image smaller than crop size: {h}x{w}")

        motion_map = torch.abs(img1 - img0)
        space_mask = (img0 > 0.0).float()
        motion_map = motion_map * space_mask
        
        scale_factor = 8
        small_motion = F.avg_pool2d(
            motion_map.unsqueeze(0), 
            kernel_size=scale_factor, 
            stride=scale_factor
        )
        
        small_crop_size = crop_size // scale_factor
        divisor = getattr(self.settings.data, 'crop_stride_divisor', 8)
        small_stride = max(1, small_crop_size // divisor)

        pooled_motion = F.avg_pool2d(
            small_motion,
            kernel_size=small_crop_size,
            stride=small_stride
        )

        _, _, h_out, w_out = pooled_motion.shape

        flat_idx = torch.argmax(pooled_motion).item()

        y_out = flat_idx // w_out
        x_out = flat_idx % w_out

        y = y_out * small_stride * scale_factor
        x = x_out * small_stride * scale_factor

        y = max(0, min(y, h - crop_size))
        x = max(0, min(x, w - crop_size))

        img0_crop = img0[:, y:y+crop_size, x:x+crop_size]
        img1_crop = img1[:, y:y+crop_size, x:x+crop_size]
        gt_crop = gt[:, y:y+crop_size, x:x+crop_size]

        crop_motion = torch.abs(img1_crop - img0_crop).mean().item()
        static_threshold = getattr(self.settings.data, 'static_motion_threshold', 0.005)

        if crop_motion < static_threshold:
            raise ValueError(f"Static crop rejected: {crop_motion:.5f}")

        return img0_crop, img1_crop, gt_crop
    
    def purge_raw_files(self):
        logger.info("Purging raw files...")
        for f in glob.glob(os.path.join(self.raw_dir, "*")):
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)