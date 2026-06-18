import torch
from unittest.mock import MagicMock

from src.data.data_manager import DataManager
from src.config.settings import Settings, TrainingConfig, DataConfig
import pytest



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
            s3_bucket="dummy",
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

def test_pipeline_integration(tmp_path):
    settings = Settings(
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
            s3_bucket="dummy",
            download_dir=str(tmp_path),
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

    manager = DataManager(settings)

    manager.fetcher.fetch_chunk = MagicMock(
        return_value=["a.nc", "b.nc", "c.nc"]
    )

    img0 = torch.ones((1, 256, 256)) * 250.0
    gt = img0.clone()
    img1 = img0.clone()
    img1[:, 100:164, 100:164] = 300.0

    fake_tensors = [img0, gt, img1]

    manager.fetcher.apply_planck_function = MagicMock(
        side_effect=fake_tensors
    )

    manager.process_chunk("dummy_prefix")

    saved_files = list(tmp_path.glob("*.pt"))

    assert len(saved_files) == 1
    




def test_factory_goes(settings):
    settings.data.satellite_type = "goes"

    manager = DataManager(settings)

    assert manager.fetcher.__class__.__name__ == "GOESFetcher"


def test_factory_himawari(settings):
    settings.data.satellite_type = "himawari"

    manager = DataManager(settings)

    assert manager.fetcher.__class__.__name__ == "HimawariFetcher"