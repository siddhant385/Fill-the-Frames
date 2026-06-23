from pydantic import BaseModel, Field
from typing import List, Optional

class VariableMetadata(BaseModel):
    name: str = Field(..., description="Name of the scientific variable")
    shape: List[int] = Field(..., description="Dimensions of the variable")
    datatype: str = Field(..., description="Data type of the variable")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "brightness_temperature",
                "shape": [24, 512, 512],
                "datatype": "float32"
            }
        }

class VariablesResponse(BaseModel):
    variables: List[VariableMetadata] = Field(..., description="List of available variables")

    class Config:
        json_schema_extra = {
            "example": {
                "variables": [
                    {
                        "name": "brightness_temperature",
                        "shape": [24, 512, 512],
                        "datatype": "float32"
                    }
                ]
            }
        }

class FrameStatistics(BaseModel):
    min: float = Field(..., description="Minimum value in the frame")
    max: float = Field(..., description="Maximum value in the frame")
    mean: float = Field(..., description="Mean value of the frame")
    std: float = Field(..., description="Standard deviation of the frame")

    class Config:
        json_schema_extra = {
            "example": {
                "min": 180.3,
                "max": 321.7,
                "mean": 245.2,
                "std": 18.4
            }
        }

class FrameDataResponse(BaseModel):
    file_id: str = Field(..., description="ID of the dataset file")
    variable: str = Field(..., description="Name of the variable")
    time_index: int = Field(..., description="Time index of the extracted frame")
    timestamp: Optional[str] = Field(None, description="ISO timestamp if available")
    shape: List[int] = Field(..., description="Shape of the 2D frame (height, width)")
    min: float = Field(..., description="Minimum value in the frame")
    max: float = Field(..., description="Maximum value in the frame")
    mean: float = Field(..., description="Mean value of the frame")
    std: float = Field(..., description="Standard deviation of the frame")
    z: List[List[float]] = Field(..., description="2D matrix of frame values")

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "variable": "brightness_temperature",
                "time_index": 5,
                "timestamp": "2024-01-01T00:15:00Z",
                "shape": [512, 512],
                "min": 180.3,
                "max": 321.7,
                "mean": 245.2,
                "std": 18.4,
                "z": [[240.1, 241.5], [239.8, 240.2]]
            }
        }
