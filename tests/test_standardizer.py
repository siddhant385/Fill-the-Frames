import torch
from src.data.standardizer import UniversalStandardizer


def test_normalize_bt():
    bt = torch.tensor([180.0, 255.0, 330.0])

    out = UniversalStandardizer.normalize_bt(bt)

    assert out[0] == 0.0
    assert out[2] == 1.0
    assert 0.0 <= out[1] <= 1.0


def test_normalize_bt_clipping():
    bt = torch.tensor([100.0, 400.0])

    out = UniversalStandardizer.normalize_bt(bt)

    assert out[0] == 0.0
    assert out[1] == 1.0