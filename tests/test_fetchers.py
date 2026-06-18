import numpy as np
import xarray as xr
import torch
from src.data.fetchers.goes_fetcher import GOESFetcher
import pytest
from unittest.mock import MagicMock

from src.data.fetchers.himawari_fetcher import HimawariFetcher



def test_goes_planck(tmp_path):
    ds = xr.Dataset(
        {
            "Rad": (
                ("y", "x"),
                np.ones((32, 32)) * 10
            )
        }
    )

    ds["planck_fk1"] = 1.0
    ds["planck_fk2"] = 100.0
    ds["planck_bc1"] = 0.1
    ds["planck_bc2"] = 1.0

    nc_path = tmp_path / "test.nc"
    ds.to_netcdf(nc_path)

    fetcher = GOESFetcher()

    tensor = fetcher.apply_planck_function(
        str(nc_path)
    )

    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 32, 32)




def test_himawari_missing_segments(tmp_path):
    fetcher = HimawariFetcher("dummy")

    fetcher.s3_client.get_paginator = MagicMock()
    fetcher.s3_client.get_paginator.return_value.paginate.return_value = [
        {
            "Contents": [
                {
                    "Key": f"HS_H09_20260618_1200_B14_FLDK_R20_S{i:04d}.DAT.bz2"
                }
                for i in range(8)
            ]
        }
    ]

    result = fetcher.fetch_chunk("prefix", str(tmp_path))

    assert result == []
        



def test_goes_corrupt_file(tmp_path):
    corrupt_file = tmp_path / "bad.nc"
    corrupt_file.write_text("corrupted")

    fetcher = GOESFetcher("dummy")

    with pytest.raises(Exception):
        fetcher.apply_planck_function(str(corrupt_file))
        



def test_himawari_corrupt_frame(tmp_path):
    frame_dir = tmp_path / "frame"
    frame_dir.mkdir()

    for i in range(5):
        (frame_dir / f"seg_{i}.DAT.bz2").write_text("bad")

    fetcher = HimawariFetcher("dummy")

    with pytest.raises(ValueError):
        fetcher.apply_planck_function(str(frame_dir))