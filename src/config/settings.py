from dataclasses import dataclass
from typing import Optional
import yaml


@dataclass
class TrainingConfig:
    epochs: int
    batch_size: int
    learning_rate: float
    weight_decay: float
    num_workers: int
    checkpoints_dir: str
    load_model_path: str = ""


@dataclass
class DataConfig:
    satellite_type: str
    s3_bucket: str
    download_dir: str
    prefix_type: str

    year: int
    month: Optional[int] = None

    start_day: int = 1
    end_day: int = 1

    frame_step: int = 1

    crop_size: int = 256
    crop_stride_divisor: int = 4
    static_motion_threshold: float = 0.005

    min_bt: float = 180.0
    max_bt: float = 330.0


@dataclass
class Settings:
    training: TrainingConfig
    data: DataConfig


def load_settings(
    config_path: str = "src/config/config.yaml"
) -> Settings:

    with open(config_path, "r") as file:
        raw_config = yaml.safe_load(file)

    return Settings(
        training=TrainingConfig(
            **raw_config["training"]
        ),
        data=DataConfig(
            **raw_config["data"]
        )
    )