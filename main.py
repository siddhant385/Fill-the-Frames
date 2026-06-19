import os
import logging
import datetime
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

    sat_type = settings.data.satellite_type.lower()
    prefix_type = settings.data.prefix_type
    
    # Universal Date Setup
    start_date = datetime.date(settings.data.year, settings.data.month, settings.data.start_day)
    end_date = datetime.date(settings.data.year, settings.data.month, settings.data.end_day)
    delta = end_date - start_date

    chunks = []
    
    for i in range(delta.days + 1):
        current_date = start_date + datetime.timedelta(days=i)
        
        if sat_type == "goes":
            # GOES strictly needs Julian Day (e.g., 1 Jan = 001, 1 Feb = 032)
            julian_day = current_date.timetuple().tm_yday
            chunks.append(f"{prefix_type}/{current_date.year}/{julian_day:03d}/")
            
        elif sat_type == "himawari":
            # Himawari strictly needs YYYY/MM/DD
            chunks.append(f"{prefix_type}/{current_date.year}/{current_date.month:02d}/{current_date.day:02d}/")
            
        else:
            raise ValueError(f"Unsupported satellite type: {sat_type}")

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