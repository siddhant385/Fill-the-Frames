from dataclasses import dataclass
import yaml

@dataclass
class TrainingConfig:
    epochs: int
    batch_size: int
    learning_rate: float
    checkpoints_dir: str
    load_model_path: str = ""  # 🚨 Naya path variable yahan add ho gaya

@dataclass
class DataConfig:
    s3_bucket: str
    download_dir: str
    year: int          # Pura saal as integer
    start_day: int     # Start Julian day
    end_day: int       # End Julian day
    frame_step: int
    crop_size: int

@dataclass
class Settings:
    training: TrainingConfig
    data: DataConfig

def load_settings(config_path: str = "src/config/config.yaml") -> Settings:
    with open(config_path, 'r') as file:
        raw_config = yaml.safe_load(file)
        
    return Settings(
        training=TrainingConfig(**raw_config.get("training", {})),
        data=DataConfig(**raw_config.get("data", {}))
    )