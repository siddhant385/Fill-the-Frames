import torch
from src.training.trainer import Trainer
from src.model.ifnet import IFNet
from src.config.settings import Settings, TrainingConfig, DataConfig
import os


def test_trainer_init():
    settings = Settings(
        training=TrainingConfig(
            epochs=1,
            batch_size=2,
            learning_rate=1e-4,
            weight_decay=0.001,
            num_workers=2,
            checkpoints_dir="chkpt"
        ),
        data=DataConfig(
            satellite_type="goes",
            s3_bucket="bucket",
            download_dir="data",
            prefix_type="ABI",
            year=2024,
            start_unit=1,
            end_unit=2,
            frame_step=1,
            crop_size=256
        )
    )

    trainer = Trainer(
        settings,
        IFNet(),
        torch.device("cpu")
    )

    assert trainer.global_step == 0
    


def test_checkpoint_save(tmp_path):
    settings = Settings(
        training=TrainingConfig(
            epochs=1,
            batch_size=2,
            learning_rate=1e-4,
            weight_decay=0.001,
            num_workers=2,
            checkpoints_dir=str(tmp_path)
        ),
        data=DataConfig(
            satellite_type="goes",
            s3_bucket="b",
            download_dir="d",
            prefix_type="ABI",
            year=2024,
            start_unit=1,
            end_unit=2,
            frame_step=1,
            crop_size=256,
            crop_stride_divisor=4,
            static_motion_threshold=0.005
        )
    )

    trainer = Trainer(
        settings,
        model=IFNet(),
        device=torch.device("cpu")
    )

    trainer.save_checkpoint("test_model.pth")
    trainer.shutdown()

    assert os.path.exists(
        os.path.join(tmp_path, "test_model.pth")
    )