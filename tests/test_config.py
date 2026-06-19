from src.config.settings import load_settings


def test_load_settings(tmp_path):
    yaml_content = """
training:
  epochs: 100
  batch_size: 4
  learning_rate: 0.0001
  weight_decay: 0.001
  num_workers: 4
  checkpoints_dir: "/tmp/checkpoints"
  load_model_path: ""

data:
  satellite_type: "goes"
  s3_bucket: "noaa-goes16"
  download_dir: "/tmp/data"
  prefix_type: "ABI-L1b-RadF"
  year: 2024
  start_day: 264
  end_day: 294
  frame_step: 3
  crop_size: 512
  crop_stride_divisor: 4
  static_motion_threshold: 0.005
  min_bt: 180.0
  max_bt: 330.0
"""

    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)

    settings = load_settings(str(config_file))

    assert settings.training.weight_decay == 0.001
    assert settings.training.num_workers == 4
    assert settings.data.satellite_type == "goes"
    assert settings.data.crop_stride_divisor == 4