from fastapi import APIRouter, HTTPException

from app.schemas.common import ApiResponse

# from app.schemas.animation import AnimationSequenceResponse

router = APIRouter()


@router.get("/{file_id}/sequence")
async def get_sequence(
    file_id: str, start_time: str = "", end_time: str = "", fps: int = 10
):
    """
    DEPRECATED: Animation sequences are currently orchestrated on the frontend using 
    cached interpolation workflow artifacts to avoid duplicate API requests.
    This route is retained for future server-side animation capabilities (e.g. streaming).
    """
    raise HTTPException(
        status_code=501, 
        detail="Server-side sequence generation is not implemented. Orchestration is handled by the frontend."
    )
