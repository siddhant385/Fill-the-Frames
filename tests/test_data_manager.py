import torch
import pytest

from src.data.data_manager import DataManager
from src.config.settings import Settings, TrainingConfig, DataConfig


@pytest.fixture
def settings():
    return Settings(
        training=TrainingConfig(
            epochs=1,
            batch_size=1,
            learning_rate=1e-4,
            weight_decay=0.001,
            num_workers=2,
            checkpoints_dir="chkpt"
        ),
        data=DataConfig(
            satellite_type="goes",
            s3_bucket="test",
            download_dir="tmp",
            prefix_type="ABI",
            year=2024,
            start_unit=1,
            end_unit=2,
            frame_step=1,
            crop_size=64,
            crop_stride_divisor=4,
            static_motion_threshold=0.005
        )
    )


def test_motion_crop_detects_motion(settings):
    manager = DataManager(settings)

    img0 = torch.ones((1, 256, 256)) * 0.5
    img1 = img0.clone()
    gt = img0.clone()

    img1[:, 100:164, 100:164] = 1.0

    crop0, crop1, crop_gt = manager._motion_guided_argmax_crop(
        img0, img1, gt
    )

    motion = torch.abs(crop1 - crop0).mean().item()

    assert crop0.shape == (1, 64, 64)
    assert motion > settings.data.static_motion_threshold


def test_static_crop_rejection(settings):
    manager = DataManager(settings)

    img0 = torch.zeros((1, 256, 256))
    img1 = torch.zeros((1, 256, 256))
    gt = torch.zeros((1, 256, 256))

    with pytest.raises(ValueError):
        manager._motion_guided_argmax_crop(img0, img1, gt)