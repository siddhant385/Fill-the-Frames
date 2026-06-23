from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.config import UPLOAD_DIR
from app.schemas.common import ApiResponse
from app.services.scientific.metadata_service import MetadataService

router = APIRouter()


@router.get("/{file_id}", response_model=ApiResponse)
async def get_metadata(file_id: str):
    # Us UUID wale folder ka path banao
    target_dir = Path(UPLOAD_DIR) / file_id

    # Check karo ki folder exist karta hai ya nahi
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="File directory not found")

    # Us folder ke andar ki pehli file utha lo
    files = list(target_dir.glob("*.*"))
    if not files:
        raise HTTPException(
            status_code=404, detail="File not found inside the directory"
        )

    file_path = str(files[0])

    try:
        metadata_response = MetadataService.extract_metadata(file_id, file_path)
        return ApiResponse(
            success=True,
            message="Metadata retrieved successfully",
            data=metadata_response,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to extract metadata: {str(e)}"
        )
