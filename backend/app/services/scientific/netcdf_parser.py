from loguru import logger
from satpy import Scene
from pathlib import Path
from .base_parser import BaseDatasetParser

class NetCDFParser(BaseDatasetParser):
    def load_dataset(self, file_path: str):
        filename = Path(file_path).name
        logger.info(f"Loading NetCDF via SatPy: {filename}")
        
        # 🚨 FIX YAHAN HAI: Dynamic Reader Selection
        try:
            if "Interpolated_AI" in filename:
                # AI generated file 'cf' (Climate and Forecast) standard mein save hui thi
                self.scene = Scene(filenames=[file_path], reader="cf")
            else:
                # Original GOES/INSAT files ke liye strict reader
                self.scene = Scene(filenames=[file_path], reader="abi_l1b")
            
            # Load the variables (like C13) into memory
            available_vars = [var["name"] for var in self.scene.available_dataset_ids()]
            
            if available_vars:
                self.scene.load(available_vars)
                
        except Exception as e:
            logger.error(f"Failed to load dataset {filename} with SatPy: {str(e)}")
            raise
