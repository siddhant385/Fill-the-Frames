from loguru import logger
from satpy import Scene

from .base_parser import BaseDatasetParser


class HDFParser(BaseDatasetParser):
    def load_dataset(self, file_path: str):
        logger.info(f"Loading ISRO INSAT HDF5 via SatPy: {file_path}")
        self.scene = Scene(filenames=[file_path], reader="insat3d_imager_l1b")

        # 🚨 FIX: Yahan var.name ki jagah var["name"] kar diya
        available_vars = [var["name"] for var in self.scene.available_dataset_ids()]

        if available_vars:
            self.scene.load(available_vars)
