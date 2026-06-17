import logging
import os

from src.config.settings import load_settings
from src.utils import setup_logging


def test_load_settings(tmp_path):
    # Setup dummy yaml
    yaml_content = """
    training:
      epochs: 100
      batch_size: 4
      learning_rate: 0.0001
      checkpoints_dir: "/kaggle/working/checkpoints"
      
    data:
      s3_bucket: "noaa-goes19"
      chunk_size_days: 7
      download_dir: "goes_data"
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    settings = load_settings(str(config_file))
    assert settings.training.epochs == 100
    assert settings.data.s3_bucket == "noaa-goes19"


def test_setup_logging():
    logger = setup_logging(level=logging.DEBUG)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0
