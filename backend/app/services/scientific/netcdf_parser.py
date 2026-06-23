from loguru import logger
from satpy import Scene
from .base_parser import BaseDatasetParser

class NetCDFParser(BaseDatasetParser):
    def load_dataset(self, file_path: str):
        logger.info(f"Loading GOES NetCDF via SatPy: {file_path}")
        self.scene = Scene(filenames=[file_path], reader="abi_l1b")
        
        # 🚨 FIX: Yahan var.name ki jagah var["name"] kar diya
        available_vars = [var["name"] for var in self.scene.available_dataset_ids()]
        
        if available_vars:
            self.scene.load(available_vars)
