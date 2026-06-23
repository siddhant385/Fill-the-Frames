import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt  # 🚨 NAYA IMPORT
import numpy as np
from fastapi import HTTPException

from app.core.config import UPLOAD_DIR  # Config se path import kiya
from app.schemas.visualization import (
    FrameDataResponse,
    FrameStatistics,
    VariableMetadata,
    VariablesResponse,
)
from app.services.scientific.metadata_service import MetadataService

logger = logging.getLogger(__name__)


class VisualizationService:

    @staticmethod
    def _get_file_path(file_id: str) -> str:
        # UUID folder wale system se file uthani hai
        target_dir = Path(UPLOAD_DIR) / file_id

        if not target_dir.exists() or not target_dir.is_dir():
            raise HTTPException(status_code=404, detail="File directory not found")

        # Folder ke andar jo bhi file (jaise .nc ya .h5) ho usko utha lo
        files = list(target_dir.glob("*.*"))
        if not files:
            raise HTTPException(
                status_code=404, detail="File not found inside the directory"
            )

        return str(files[0])

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
                variables.append(
                    VariableMetadata(
                        name=var.name, shape=var.shape, datatype=var.datatype
                    )
                )

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
            std=float(np.std(valid_data)),
        )

    @staticmethod
    def get_frame(file_id: str, variable: str, time_index: int) -> FrameDataResponse:
        file_path = VisualizationService._get_file_path(file_id)
        logger.info(f"Dataset opened: {file_id}")

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
                raise HTTPException(
                    status_code=400, detail="Frame is not 2D after slicing"
                )

            timestamp = parser.extract_timestamp(time_index)
            stats = VisualizationService.compute_statistics(frame)

            frame_small = frame[::10, ::10]

            frame_clean = np.where(
                np.isnan(frame_small) | np.isinf(frame_small), -9999.0, frame_small
            ).tolist()

            response = FrameDataResponse(
                file_id=file_id,
                variable=variable,
                time_index=time_index,
                timestamp=timestamp,
                shape=list(frame_small.shape),
                min=stats.min,
                max=stats.max,
                mean=stats.mean,
                std=stats.std,
                z=frame_clean,
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

    # 🚨 NAYA METHOD PHASE 4 KE LIYE
    @staticmethod
    def get_thumbnail_path(file_id: str, variable: str) -> str:
        """
        File se data nikal kar JPEG image banata hai, aur path return karta hai.
        """
        target_dir = Path(UPLOAD_DIR) / file_id
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail="File directory not found")

        thumb_path = target_dir / f"thumb_{variable}.jpg"

        # Agar thumbnail pehle se bani hui hai (Cache), toh seedha path do
        if thumb_path.exists():
            return str(thumb_path)

        file_path = VisualizationService._get_file_path(file_id)

        parser = None
        try:
            parser = MetadataService.get_parser(file_path)
            parser.load_dataset(file_path)
            VisualizationService.validate_variable(parser, variable)

            # Data nikalo
            frame = parser.extract_time_slice(variable, 0)

            # Downsample for Speed (fast processing)
            frame_small = frame[::5, ::5]

            # Image banao aur disk par save karo
            plt.figure(figsize=(8, 8))
            plt.imshow(frame_small, cmap="gray", vmin=90, vmax=313)
            plt.axis("off")

            plt.savefig(
                thumb_path, bbox_inches="tight", pad_inches=0, format="jpg", dpi=100
            )
            plt.close()

            return str(thumb_path)

        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate thumbnail")
        finally:
            if parser is not None:
                parser.close()
