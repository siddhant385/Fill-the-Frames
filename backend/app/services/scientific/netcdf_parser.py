import xarray as xr
import numpy as np
from typing import Dict, Any
from .base_parser import BaseDatasetParser

class NetCDFParser(BaseDatasetParser):
    def __init__(self):
        self.ds = None

    def load_dataset(self, file_path: str):
        self.ds = xr.open_dataset(file_path, engine="netcdf4")

    def _convert_type(self, val):
        if isinstance(val, (np.integer, int)):
            return int(val)
        if isinstance(val, (np.floating, float)):
            return float(val)
        if isinstance(val, np.ndarray):
            return val.tolist()
        return str(val)

    def extract_metadata(self) -> Dict[str, Any]:
        if self.ds is None:
            raise ValueError("Dataset not loaded")

        # Global Attributes
        global_attributes = {k: self._convert_type(v) for k, v in self.ds.attrs.items()}

        # Dimensions
        dimensions = [{"name": str(k), "size": int(v)} for k, v in self.ds.sizes.items()]

        # Variables
        variables = []
        for name, var in self.ds.variables.items():
            # Skip if it's purely a coordinate (optional, but requested all variables? Usually we list all)
            min_val = None
            max_val = None
            # Only calculate min/max if it's not a huge dataset or inexpensive. For metadata, we can sample or ignore.
            # To be safe and inexpensive, we might just skip or do min/max on small arrays.
            if var.size < 100000:  # arbitrary small limit
                try:
                    min_val = float(var.min().values)
                    max_val = float(var.max().values)
                except Exception:
                    pass

            variables.append({
                "name": str(name),
                "datatype": str(var.dtype),
                "dimensions": list(var.dims),
                "shape": list(var.shape),
                "attributes": {k: self._convert_type(v) for k, v in var.attrs.items()},
                "min_value": min_val,
                "max_value": max_val
            })

        # Coordinates
        lat_names = ["lat", "latitude", "y"]
        lon_names = ["lon", "longitude", "x"]
        
        lat_coord = next((c for c in self.ds.coords if c.lower() in lat_names), None)
        lon_coord = next((c for c in self.ds.coords if c.lower() in lon_names), None)
        
        # Look for projection attributes or standard grid mappings
        projection = global_attributes.get("projection") or global_attributes.get("grid_mapping_name")
        for var in variables:
            if "grid_mapping" in var["attributes"] or "grid_mapping_name" in var["attributes"]:
                projection = var["attributes"].get("grid_mapping_name") or var["attributes"].get("grid_mapping") or "mapped"
                break

        coordinates = {
            "latitude": lat_coord,
            "longitude": lon_coord,
            "projection": str(projection) if projection else None
        }

        # Temporal Information
        time_names = ["time", "valid_time", "timestamp", "forecast_time"]
        time_coord = next((c for c in self.ds.coords if c.lower() in time_names), None)
        
        temporal_info = {
            "start_time": None,
            "end_time": None,
            "time_steps": None
        }
        
        if time_coord is not None:
            t_var = self.ds[time_coord]
            temporal_info["time_steps"] = int(t_var.size)
            if t_var.size > 0:
                try:
                    temporal_info["start_time"] = str(t_var.values[0])
                    temporal_info["end_time"] = str(t_var.values[-1])
                except Exception:
                    pass

        return {
            "global_attributes": global_attributes,
            "dimensions": dimensions,
            "variables": variables,
            "coordinates": coordinates,
            "temporal_info": temporal_info,
            "variable_count": len(variables),
            "dimension_count": len(dimensions),
            "coordinate_count": len(self.ds.coords)
        }

    def get_variable_names(self) -> list[str]:
        if self.ds is None:
            raise ValueError("Dataset not loaded")
        return list(self.ds.variables.keys())

    def get_time_dimension(self) -> str | None:
        if self.ds is None:
            raise ValueError("Dataset not loaded")
        time_names = ["time", "valid_time", "timestamp", "forecast_time"]
        return next((c for c in self.ds.coords if c.lower() in time_names), None)

    def extract_time_slice(self, variable: str, time_index: int) -> np.ndarray:
        if self.ds is None:
            raise ValueError("Dataset not loaded")
        if variable not in self.ds.variables:
            raise ValueError(f"Variable {variable} not found")
        
        var_data = self.ds[variable]
        
        if len(var_data.shape) == 3:
            time_dim = self.get_time_dimension()
            if time_dim and time_dim in var_data.dims:
                return var_data.isel({time_dim: time_index}).values
            else:
                return var_data[time_index, :, :].values
        elif len(var_data.shape) == 2:
            if time_index != 0:
                raise ValueError("time_index must be 0 for 2D variables")
            return var_data.values
        else:
            raise ValueError(f"Variable {variable} has unsupported shape {var_data.shape}")

    def extract_timestamp(self, time_index: int) -> str | None:
        if self.ds is None:
            raise ValueError("Dataset not loaded")
        time_dim = self.get_time_dimension()
        if not time_dim:
            return None
        
        t_var = self.ds[time_dim]
        if time_index < 0 or time_index >= t_var.size:
            return None
        
        try:
            val = t_var.values[time_index]
            if isinstance(val, np.datetime64):
                # Try to return ISO format string
                import pandas as pd
                return pd.Timestamp(val).isoformat() + "Z"
            return str(val)
        except Exception:
            return None

    def close(self):
        if self.ds is not None:
            self.ds.close()