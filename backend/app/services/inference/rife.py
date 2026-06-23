import math

import dask.array as da
import numpy as np
from loguru import logger
from satpy import Scene

from app.services.inference.model_loader import ModelLoader


class SatelliteInterpolationModel:
    # Standard GOES C13 Brightness Temperature limits
    MIN_BT = 90.0
    MAX_BT = 313.0

    def __init__(self) -> None:
        # Naya session banane ki jagah RAM se pre-loaded model uthaya
        self.session = ModelLoader.get_session()

        # ONNX ke input aur output node ke naam dynamically nikal liye
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def _generate_weight_window(self, patch_size: int) -> np.ndarray:
        h = np.hanning(patch_size)
        window = np.outer(h, h)
        return window.astype(np.float32)

    def _norm(self, arr: np.ndarray) -> np.ndarray:
        return np.clip((arr - self.MIN_BT) / (self.MAX_BT - self.MIN_BT), 0, 1)

    def _denorm(self, arr: np.ndarray) -> np.ndarray:
        return arr * (self.MAX_BT - self.MIN_BT) + self.MIN_BT

    def predict_full_disk(
        self,
        img0: np.ndarray,
        img20: np.ndarray,
        patch_size=512,
        overlap=128,
        batch_size=1,
    ) -> np.ndarray:
        logger.info("Starting Sliding Window Inference...")

        # Deep space masks handling
        space_mask = np.isnan(img0) | np.isnan(img20) | np.isinf(img0) | np.isinf(img20)
        safe_img0 = np.nan_to_num(
            img0, nan=self.MIN_BT, posinf=self.MIN_BT, neginf=self.MIN_BT
        )
        safe_img20 = np.nan_to_num(
            img20, nan=self.MIN_BT, posinf=self.MIN_BT, neginf=self.MIN_BT
        )

        h_orig, w_orig = safe_img0.shape
        stride = patch_size - overlap

        pad_h = math.ceil(h_orig / stride) * stride + overlap - h_orig
        pad_w = math.ceil(w_orig / stride) * stride + overlap - w_orig

        img0_pad = np.pad(safe_img0, ((0, pad_h), (0, pad_w)), mode="reflect")
        img20_pad = np.pad(safe_img20, ((0, pad_h), (0, pad_w)), mode="reflect")
        h_pad, w_pad = img0_pad.shape

        canvas = np.zeros((h_pad, w_pad), dtype=np.float32)
        weight_sum = np.zeros((h_pad, w_pad), dtype=np.float32)
        window = self._generate_weight_window(patch_size)

        y_coords = list(range(0, h_pad - patch_size + 1, stride))
        x_coords = list(range(0, w_pad - patch_size + 1, stride))

        patches, coords = [], []

        for y in y_coords:
            for x in x_coords:
                p0 = self._norm(img0_pad[y : y + patch_size, x : x + patch_size])
                p20 = self._norm(img20_pad[y : y + patch_size, x : x + patch_size])

                t0 = np.expand_dims(p0, axis=(0, 1))
                t20 = np.expand_dims(p20, axis=(0, 1))
                merged = np.concatenate((t0, t20), axis=1)

                patches.append(merged)
                coords.append((y, x))

                if len(patches) == batch_size:
                    self._process_batch(
                        patches, coords, canvas, weight_sum, window, patch_size
                    )
                    patches, coords = [], []

        if len(patches) > 0:
            self._process_batch(patches, coords, canvas, weight_sum, window, patch_size)

        final_img_pad = canvas / np.clip(weight_sum, 1e-8, None)
        final_img = final_img_pad[:h_orig, :w_orig]
        final_img[space_mask] = np.nan

        logger.success("Sliding Window Inference Complete!")
        return final_img

    def _process_batch(
        self,
        patches: list,
        coords: list,
        canvas: np.ndarray,
        weight_sum: np.ndarray,
        window: np.ndarray,
        patch_size: int,
    ) -> None:
        batch_input = np.concatenate(patches, axis=0)

        # Dynamic input aur output names use kiye hain
        ort_outs = self.session.run([self.output_name], {self.input_name: batch_input})
        preds = ort_outs[0]

        for i in range(len(patches)):
            cy, cx = coords[i]
            pred_patch = self._denorm(preds[i, 0])
            canvas[cy : cy + patch_size, cx : cx + patch_size] += pred_patch * window
            weight_sum[cy : cy + patch_size, cx : cx + patch_size] += window

    def save_to_nc(
        self,
        image_array: np.ndarray,
        original_scene: Scene,
        output_path: str,
        channel: str = "C13",
        interpolated_time=None,
    ) -> str:
        """NumPy array ko SatPy Scene me wapas daal kar CF-compliant NetCDF (.nc) save karta hai"""
        logger.info(f"Injecting AI prediction back into SatPy Scene for {output_path}")

        # 1. Update Interpolated Time in Global and Channel Attributes
        if interpolated_time:
            original_scene.attrs["start_time"] = interpolated_time
            original_scene.attrs["end_time"] = interpolated_time
            if "start_time" in original_scene[channel].attrs:
                original_scene[channel].attrs["start_time"] = interpolated_time
            if "end_time" in original_scene[channel].attrs:
                original_scene[channel].attrs["end_time"] = interpolated_time

        # Update descriptions
        original_scene.attrs["description"] = "AI Interpolated Frame (RIFE Engine)"
        original_scene[channel].attrs["description"] = "AI Interpolated GOES Frame"

        # 2. Convert and Inject the Dask Array
        dask_array = da.from_array(image_array)
        original_scene[channel].data = dask_array

        # 3. Clean Attributes (To avoid NetCDF serialization crash with numpy datatypes)
        def clean_attrs(attrs_dict):
            for key in list(attrs_dict.keys()):
                val = attrs_dict[key]
                if isinstance(val, np.ndarray):
                    attrs_dict[key] = val.tolist()
                elif isinstance(val, (np.float32, np.float64, np.int32, np.int64)):
                    attrs_dict[key] = val.item()

        clean_attrs(original_scene.attrs)
        clean_attrs(original_scene[channel].attrs)

        # 4. Save
        logger.info("Saving CF-compliant NetCDF via SatPy...")
        original_scene.save_datasets(
            writer="cf", datasets=[channel], filename=output_path
        )

        logger.success(f"File saved successfully at {output_path}")
        return output_path
