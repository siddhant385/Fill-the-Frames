from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import xarray as xr

from src.config.settings import DataConfig, Settings, TrainingConfig
from src.data.s3_manager import S3Manager


@pytest.fixture
def mock_settings():
    return Settings(
        training=TrainingConfig(
            epochs=1, batch_size=1, learning_rate=0.001, checkpoints_dir="chkpt"
        ),
        data=DataConfig(
            s3_bucket="test-bucket", download_dir="test_dir", chunk_size_days=1
        ),
    )


def test_process_nc_to_pt(mock_settings, tmp_path):
    manager = S3Manager(mock_settings)

    # Create mock dataset
    ds = xr.Dataset(
        {"Rad": (("y", "x"), np.ones((512, 512)) * 10)},
        coords={"y": np.arange(512), "x": np.arange(512)},
    )
    ds["planck_fk1"] = 1.0
    ds["planck_fk2"] = 100.0
    ds["planck_bc1"] = 0.1
    ds["planck_bc2"] = 1.0

    nc_path = tmp_path / "test.nc"
    ds.to_netcdf(nc_path)

    pt_path = tmp_path / "test.pt"

    # The actual triplet extraction takes 3 files usually, testing just the converter here
    manager._convert_nc_to_bt_tensor(str(nc_path), str(pt_path))

    assert pt_path.exists()
