from dataclasses import dataclass

import yaml


@dataclass
class TrainingConfig:
    epochs: int
    batch_size: int
    learning_rate: float
    checkpoints_dir: str

@dataclass
class DataConfig:
    s3_bucket: str
    download_dir: str
    chunk_size_days: int

@dataclass
class Settings:
    training: TrainingConfig
    data: DataConfig

def load_settings(config_path: str = "src/config/config.yaml") -> Settings:
    """Loads YAML configuration into a Settings object.
    
    Args:
        config_path (str): Path to the configuration YAML file.
        
    Returns:
        Settings: A dataclass object containing configuration parameters.
    """
    with open(config_path, 'r') as file:
        raw_config = yaml.safe_load(file)
        
    return Settings(
        training=TrainingConfig(**raw_config.get("training", {})),
        data=DataConfig(**raw_config.get("data", {}))
    )

