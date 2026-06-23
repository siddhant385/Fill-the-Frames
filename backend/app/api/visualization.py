from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse  # 🚨 NAYA IMPORT

from app.schemas.common import ApiResponse
from app.services.scientific.visualization_service import VisualizationService

router = APIRouter()


@router.get("/{file_id}/variables", response_model=ApiResponse)
async def get_variables(file_id: str):
    """
    Get a list of available variables/channels in the uploaded dataset.
    """
    try:
        variables_data = VisualizationService.get_variables(file_id)
        return ApiResponse(
            success=True,
            message="Variables successfully retrieved.",
            data=variables_data.model_dump(),
        )
    except Exception as e:
        return ApiResponse(
            success=False, message=f"Failed to retrieve variables: {str(e)}", data=None
        )


@router.get("/{file_id}/frame", response_model=ApiResponse)
async def get_frame(
    file_id: str,
    variable: str = Query(..., description="The variable to extract"),
    time_index: int = Query(0, description="The time index to extract"),
):
    """
    Extract a 2D frame matrix for a specific variable and time index.
    """
    try:
        frame_data = VisualizationService.get_frame(file_id, variable, time_index)
        return ApiResponse(
            success=True,
            message=f"Frame data for {variable} extracted successfully.",
            data=frame_data.model_dump(),
        )
    except Exception as e:
        return ApiResponse(
            success=False, message=f"Failed to extract frame: {str(e)}", data=None
        )


# 🚨 RESPONSE MODEL HATA DIYA HAI AUR FILE RESPONSE BHEJ RAHE HAIN
@router.get("/{file_id}/thumbnail")
async def get_thumbnail(
    file_id: str, variable: str = Query("C13", description="The variable to preview")
):
    """
    Generate and return a JPEG thumbnail image for the dataset preview.
    """
    try:
        thumb_path = VisualizationService.get_thumbnail_path(file_id, variable)
        return FileResponse(path=thumb_path, media_type="image/jpeg")
    except Exception as e:
        return ApiResponse(
            success=False, message=f"Failed to generate thumbnail: {str(e)}", data=None
        )
