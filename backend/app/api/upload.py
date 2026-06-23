import asyncio
import os
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import UPLOAD_DIR
from app.schemas.common import ApiResponse
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("", response_model=ApiResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a single satellite dataset (.nc, .h5, .hdf5) to the server.
    """
    try:
        upload_data = await UploadService.process_upload(file)

        return ApiResponse(
            success=True,
            message="Dataset uploaded successfully",
            data=upload_data.model_dump(by_alias=True),
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        return ApiResponse(success=False, message=f"Upload failed: {str(e)}", data=None)


@router.post("/batch", response_model=ApiResponse)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple satellite datasets at once.
    """
    try:
        # Saari files ko parallel me process karenge
        tasks = [UploadService.process_upload(file) for file in files]
        results = await asyncio.gather(*tasks)

        return ApiResponse(
            success=True,
            message=f"{len(results)} files uploaded successfully",
            data=[res.model_dump(by_alias=True) for res in results],
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        return ApiResponse(
            success=False, message=f"Batch upload failed: {str(e)}", data=None
        )


@router.get("", response_model=ApiResponse)
async def list_uploaded_files():
    """
    Get a list of all uploaded dataset folders and their sizes.
    """
    upload_path = Path(UPLOAD_DIR)
    if not upload_path.exists():
        return ApiResponse(success=True, message="No files found", data=[])

    files_info = []
    # Saare UUID folders ko scan karenge
    for folder in upload_path.iterdir():
        if folder.is_dir():
            inner_files = list(folder.glob("*.*"))
            if inner_files:
                actual_file = inner_files[0]
                files_info.append(
                    {
                        "fileId": folder.name,
                        "filename": actual_file.name,
                        "size_bytes": os.path.getsize(actual_file),
                    }
                )

    return ApiResponse(
        success=True,
        message="Files retrieved successfully",
        data=files_info,
    )


@router.delete("/{file_id}", response_model=ApiResponse)
async def delete_file(file_id: str):
    """
    Delete an uploaded dataset and clear space.
    """
    target_dir = Path(UPLOAD_DIR) / file_id

    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail="File directory not found")

    try:
        # Poora UUID folder uda do
        shutil.rmtree(target_dir)
        return ApiResponse(
            success=True,
            message=f"File {file_id} deleted successfully",
            data=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not delete file: {str(e)}")
