from fastapi import APIRouter, HTTPException, Query
from app.schemas.common import ApiResponse
from app.schemas.visualization import VariablesResponse, FrameDataResponse
from app.services.scientific.visualization_service import VisualizationService

router = APIRouter()

@router.get("/{file_id}/variables", response_model=VariablesResponse)
async def get_variables(file_id: str):
    """
    Get a list of available variables in the uploaded dataset.
    """
    return VisualizationService.get_variables(file_id)

@router.get("/{file_id}/frame", response_model=FrameDataResponse)
async def get_frame(
    file_id: str, 
    variable: str = Query(..., description="The variable to extract"), 
    time_index: int = Query(0, description="The time index to extract")
):
    """
    Extract a 2D frame matrix for a specific variable and time index.
    """
    return VisualizationService.get_frame(file_id, variable, time_index)

@router.get("/{file_id}/thumbnail", response_model=ApiResponse)
async def get_thumbnail(file_id: str):
    # Placeholder
    return ApiResponse(
        success=True,
        message="Thumbnail retrieved",
        data={"url": "dummy_url"}
    )
