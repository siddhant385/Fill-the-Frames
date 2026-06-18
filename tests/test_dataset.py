import torch
from src.data.dataset import SatelliteTripletDataset
def test_dataset_augment(tmp_path):
    tensor_data = torch.ones((3, 1, 512, 512))
    torch.save(tensor_data, tmp_path / "triplet_001.pt")

    dataset = SatelliteTripletDataset(str(tmp_path), augment=True)

    img0, img1, gt = dataset[0]

    assert img0.shape == (1, 256, 256)
    assert img1.shape == (1, 256, 256)
    assert gt.shape == (1, 256, 256)

def test_dataset_loading(tmp_path):
    triplet = torch.zeros((3, 1, 256, 256))
    torch.save(triplet, tmp_path / "triplet_001.pt")

    dataset = SatelliteTripletDataset(
        str(tmp_path),
        augment=False
    )

    assert len(dataset) == 1

    img0, img1, gt = dataset[0]

    assert img0.shape == (1, 256, 256)
    assert img1.shape == (1, 256, 256)
    assert gt.shape == (1, 256, 256)