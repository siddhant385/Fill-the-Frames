from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np
from satpy import Scene

from app.schemas.metadata import DimensionInfo, VariableInfo, CoordinateInfo, TemporalInfo

class BaseDatasetParser(ABC):
    def __init__(self):
        self.scene: Scene = None

    @abstractmethod
    def load_dataset(self, file_path: str) -> None:
        pass
        
    def extract_metadata(self) -> Dict[str, Any]:
        if self.scene is None:
            raise ValueError("Dataset not loaded")
            
        variables = []
        for var_id in self.scene.available_dataset_ids():
            # 🚨 FIX: Dictionary access use kiya
            var_name = str(var_id["name"])
            
            # self.scene[var_id] use kiya taaki SatPy khush rahe
            variables.append(VariableInfo(
                name=var_name,
                datatype="float32",
                dimensions=["y", "x"],
                shape=list(self.scene[var_id].shape) if var_id in self.scene else [],
                attributes={k: str(v) for k, v in self.scene[var_id].attrs.items()} if var_id in self.scene else {},
                min_value=None,
                max_value=None
            ))

        global_attrs = {k: str(v) for k, v in self.scene.attrs.items()}
        area = self.scene.max_area() if hasattr(self.scene, 'max_area') else None
        
        coordinates = CoordinateInfo(
            latitude="y",
            longitude="x",
            projection=str(area.name if area else "Geostationary")
        )
        
        temporal_info = TemporalInfo(
            start_time=str(self.scene.start_time) if self.scene.start_time else None,
            end_time=str(self.scene.end_time) if self.scene.end_time else None,
            time_steps=1
        )
        
        dimensions = [
            DimensionInfo(name="y", size=variables[0].shape[0] if variables else 0),
            DimensionInfo(name="x", size=variables[0].shape[1] if variables else 0)
        ]

        return {
            "global_attributes": global_attrs,
            "dimensions": dimensions,
            "variables": variables,
            "coordinates": coordinates,
            "temporal_info": temporal_info,
            "variable_count": len(variables),
            "dimension_count": 2,
            "coordinate_count": 2
        }

    def get_variable_names(self) -> List[str]:
        if self.scene is None:
            raise ValueError("Dataset not loaded")
        # 🚨 FIX: Yahan var.name ki jagah var["name"] kar diya
        return [str(var["name"]) for var in self.scene.available_dataset_ids()]

    def extract_time_slice(self, variable: str, time_index: int) -> np.ndarray:
        if self.scene is None:
            raise ValueError("Dataset not loaded")
        if variable not in self.scene:
            self.scene.load([variable])
        return self.scene[variable].values.astype(np.float32)

    def extract_timestamp(self, time_index: int) -> Optional[str]:
        if self.scene is None:
            return None
        return self.scene.start_time.isoformat() + "Z" if self.scene.start_time else None

    def close(self):
        self.scene = None
