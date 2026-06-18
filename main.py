import os
import logging
import torch

from src.config.settings import load_settings
from src.utils import setup_logging
from src.data.data_manager import DataManager
from src.model.ifnet import IFNet
from src.training.trainer import Trainer


def main():
    logger = setup_logging()
    settings = load_settings()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    logger.info(
        "Starting Universal Satellite Interpolation Pipeline..."
    )

    # Universal Data Manager
    data_manager = DataManager(settings)

    # Model init
    model = IFNet()

    # Resume checkpoint if exists
    checkpoint_path = settings.training.load_model_path

    if os.path.exists(checkpoint_path):
        model.load_state_dict(
            torch.load(
                checkpoint_path,
                map_location=device
            )
        )

        logger.info(
            f"Loaded existing checkpoint: {checkpoint_path}"
        )
    else:
        logger.warning(
            f"No checkpoint found at {checkpoint_path}. "
            f"Starting from scratch."
        )

    trainer = Trainer(
        settings=settings,
        model=model,
        device=device
    )

    # Config-driven chunk generation
    sat_type = settings.data.satellite_type.lower()
    year = settings.data.year
    start_day = settings.data.start_unit
    end_day = settings.data.end_unit
    prefix_type = settings.data.prefix_type

    chunks = []

    if sat_type == "goes":
        # Example:
        # ABI-L1b-RadC/2026/150/
        chunks = [
            f"{prefix_type}/{year}/{day:03d}/"
            for day in range(
                start_day,
                end_day + 1
            )
        ]

    elif sat_type == "himawari":
        # Example:
        # AHI-L1b-FLDK/2026/06/18/
        month = settings.data.month

        chunks = [
            f"{prefix_type}/{year}/{month:02d}/{day:02d}/"
            for day in range(
                start_day,
                end_day + 1
            )
        ]

    else:
        raise ValueError(
            f"Unsupported satellite type: {sat_type}"
        )

    # Main chunk loop
    for chunk_idx, chunk in enumerate(chunks):
        logger.info(
            f"=== Processing Chunk "
            f"{chunk_idx + 1}/{len(chunks)}: {chunk} ==="
        )

        # Fetch -> Standardize -> Crop -> Save .pt triplets
        data_manager.process_chunk(chunk)

        # Train on generated triplets
        for epoch in range(
            1,
            settings.training.epochs + 1
        ):
            logger.info(
                f"--- Chunk {chunk_idx + 1} | "
                f"Epoch {epoch}/{settings.training.epochs} ---"
            )

            trainer.train_chunk(
                settings.data.download_dir,
                epoch
            )

            trainer.save_checkpoint(
                "latest_model.pth"
            )

        # Purge .pt files after training chunk
        logger.info(
            "Purging processed .pt triplets..."
        )

        for f in os.listdir(
            settings.data.download_dir
        ):
            if f.endswith(".pt"):
                os.remove(
                    os.path.join(
                        settings.data.download_dir,
                        f
                    )
                )

    trainer.shutdown()

    logger.info(
        "Universal multi-satellite training complete."
    )


if __name__ == "__main__":
    main()