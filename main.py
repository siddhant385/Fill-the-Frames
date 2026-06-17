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
    
    logger.info("Starting Satellite Interpolation Pipeline...")
    
    s3_manager = S3Manager(settings)
    model = IFNet()
    trainer = Trainer(settings, model, device)
    
    # Train-and-Purge Chunking Loop (Mock Example)
    chunks = ["chunk1_prefix", "chunk2_prefix"]
    
    # Corrected Train-and-Purge Chunking Loop
    chunks = ["chunk1_prefix", "chunk2_prefix"]
    
    for chunk_idx, chunk in enumerate(chunks):
        logger.info(f"=== Fetching and Processing Chunk {chunk_idx + 1}/{len(chunks)}: {chunk} ===")
        
        # 1. Download and Process ONE chunk fully
        s3_manager.download_chunk(chunk)
        
        # 2. Train on this specific chunk for all epochs
        for epoch in range(1, settings.training.epochs + 1):
            logger.info(f"--- Chunk {chunk_idx + 1} | Starting Epoch {epoch}/{settings.training.epochs} ---")
            
            trainer.train_chunk(settings.data.download_dir, epoch)
            
            # Save checkpoint
            trainer.save_checkpoint(f"chunk_{chunk_idx}_epoch_{epoch}_latest.pth")
            
        # 3. Purge local data to save Kaggle 30GB disk space BEFORE moving to next chunk
        logger.info(f"Purging {chunk} data from disk...")
        s3_manager.purge_chunk()
            
    logger.info("Training complete.")

if __name__ == "__main__":
    main()
