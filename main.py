import logging
import torch
from src.config.settings import load_settings
from src.utils import setup_logging
from src.data.s3_manager import S3Manager
from src.model.ifnet import IFNet
from src.training.trainer import Trainer

def main():
    logger = setup_logging()
    settings = load_settings()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    logger.info("Starting Autonomous Satellite Interpolation Pipeline...")
    
    s3_manager = S3Manager(settings)
    model = IFNet()
    trainer = Trainer(settings, model, device)
    
    # 🤖 Auto-generating chunks from YAML config (Day-level chunking)
    chunks = [f"ABI-L1b-RadC/2022/{day}/" for day in settings.data.target_days]
    
    for chunk_idx, chunk in enumerate(chunks):
        logger.info(f"=== Fetching and Processing Chunk {chunk_idx + 1}/{len(chunks)}: {chunk} ===")
        
        s3_manager.download_chunk(chunk)
        
        for epoch in range(1, settings.training.epochs + 1):
            logger.info(f"--- Chunk {chunk_idx + 1} | Starting Epoch {epoch}/{settings.training.epochs} ---")
            trainer.train_chunk(settings.data.download_dir, epoch)
            trainer.save_checkpoint("latest_model.pth")
            
        s3_manager.purge_chunk()
            
    logger.info("🔥 1-Week Hardcore Training Complete! Model is ready for phase 2 testing.")

if __name__ == "__main__":
    main()