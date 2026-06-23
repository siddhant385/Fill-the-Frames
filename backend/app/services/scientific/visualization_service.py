import os
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from app.schemas.visualization import VariableMetadata, VariablesResponse, FrameStatistics, FrameDataResponse
from .metadata_service import MetadataService

logger = logging.getLogger(__name__)

class VisualizationService:
    
    @staticmethod
    def _get_file_path(file_id: str) -> str:
        storage_dir = os.path.join(os.getcwd(), "storage", "uploads")
        for ext in [".nc", ".h5", ".hdf5"]:
            possible_path = os.path.join(storage_dir, f"{file_id}{ext}")
            if os.path.exists(possible_path):
                return possible_path
        raise HTTPException(status_code=404, detail="File not found")

    @staticmethod
    def get_variables(file_id: str) -> VariablesResponse:
        file_path = VisualizationService._get_file_path(file_id)
        logger.info(f"Dataset opened for variable discovery: {file_id}")
        
        parser = None
        try:
            parser = MetadataService.get_parser(file_path)
            parser.load_dataset(file_path)
            
            metadata = parser.extract_metadata()
            variables = []
            for var in metadata["variables"]:
                variables.append(VariableMetadata(
                    name=var["name"],
                    shape=var["shape"],
                    datatype=var["datatype"]
                ))
                
            logger.info(f"Visualization variable request completed for {file_id}")
            return VariablesResponse(variables=variables)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Visualization variable request failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Dataset Read Failure")
        finally:
            if parser is not None:
                parser.close()

    @staticmethod
    def validate_variable(parser, variable: str):
        var_names = parser.get_variable_names()
        if variable not in var_names:
            logger.error(f"Invalid variable requested: {variable}")
            raise HTTPException(status_code=400, detail="Invalid Variable")

    @staticmethod
    def validate_time_index(time_index: int):
        if time_index < 0:
            logger.error(f"Invalid time index requested: {time_index}")
            raise HTTPException(status_code=400, detail="Invalid Time Index")

    @staticmethod
    def compute_statistics(frame: np.ndarray) -> FrameStatistics:
        valid_data = frame[~np.isnan(frame)]
        if valid_data.size == 0:
            return FrameStatistics(min=0.0, max=0.0, mean=0.0, std=0.0)
            
        return FrameStatistics(
            min=float(np.min(valid_data)),
            max=float(np.max(valid_data)),
            mean=float(np.mean(valid_data)),
            std=float(np.std(valid_data))
        )

    @staticmethod
    def get_frame(file_id: str, variable: str, time_index: int) -> FrameDataResponse:
        file_path = VisualizationService._get_file_path(file_id)
        logger.info(f"Dataset opened: {file_id}")
        logger.info(f"Variable requested: {variable}")
        logger.info(f"Time index requested: {time_index}")
        
        parser = None
        try:
            parser = MetadataService.get_parser(file_path)
            parser.load_dataset(file_path)
            
            VisualizationService.validate_variable(parser, variable)
            VisualizationService.validate_time_index(time_index)
            
            try:
                frame = parser.extract_time_slice(variable, time_index)
                logger.info("Frame extracted successfully")
            except Exception as e:
                logger.error(f"Time slice extraction failed: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid Time Index")
                
            if len(frame.shape) != 2:
                logger.error(f"Frame is not 2D after slicing. Shape: {frame.shape}")
                raise HTTPException(status_code=400, detail="Frame is not 2D after slicing")
                
            timestamp = parser.extract_timestamp(time_index)
            stats = VisualizationService.compute_statistics(frame)
            logger.info("Statistics calculated")
            
            frame_clean = np.where(np.isnan(frame) | np.isinf(frame), None, frame).tolist()
            
            response = FrameDataResponse(
                file_id=file_id,
                variable=variable,
                time_index=time_index,
                timestamp=timestamp,
                shape=list(frame.shape),
                min=stats.min,
                max=stats.max,
                mean=stats.mean,
                std=stats.std,
                z=frame_clean
            )
            
            logger.info("Visualization request completed")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Visualization request failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Dataset Read Failure")
        finally:
            if parser is not None:
                parser.close()
