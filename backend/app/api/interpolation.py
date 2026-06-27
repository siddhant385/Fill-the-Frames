import asyncio
import json
import uuid
from typing import Any, Dict
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException
from fastapi.responses import StreamingResponse
from huggingface_hub import HfFileSystem

from app.core.config import HF_BUCKET_ID, HF_TOKEN
from app.schemas.common import ApiResponse
from app.schemas.interpolation import (
    InterpolationRequest,
    JobResponse,
    JobStatusResponse,
)
from app.services.inference.interpolation_service import InterpolationService

router = APIRouter()
fs = HfFileSystem(token=HF_TOKEN)

# In-memory Database for job tracking
JOB_STORE: Dict[str, Dict[str, Any]] = {}


@router.post("/generate", response_model=ApiResponse)
async def generate_interpolation(
    background_tasks: BackgroundTasks,
    file_id_1: str = Form(..., description="First file ID (e.g., 00_min)"),
    file_id_2: str = Form(..., description="Second file ID (e.g., 20_min)"),
    variable: str = Form("C13", description="The satellite channel to interpolate"),
):
    # 1. Naya Unique Job ID banao
    job_id = str(uuid.uuid4())

    # 2. Store me default status daal do
    JOB_STORE[job_id] = {
        "status": "processing",
        "progress": 0.0,
        "result_file_id": None,
        "error": None,
    }

    # 3. Pydantic schema me input pack kar lo taaki backend logic intact rahe
    request_obj = InterpolationRequest(
        file_id_1=file_id_1, file_id_2=file_id_2, variable=variable
    )

    # 4. Asli AI ka heavy kaam background me bhej do (API yahan rukegi nahi)
    background_tasks.add_task(
        InterpolationService.run_job,
        job_id=job_id,
        req=request_obj,
        job_store=JOB_STORE,
    )

    # 5. Frontend ko turant response de do
    return ApiResponse(
        success=True,
        message="Interpolation job queued successfully. Please check status periodically.",
        data=JobResponse(job_id=job_id, status="queued").model_dump(),
    )


@router.get("/status/{job_id}", response_model=ApiResponse)
async def get_status(job_id: str):
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail="Job ID not found")

    job_data = JOB_STORE[job_id]

    return ApiResponse(
        success=True,
        message="Job status retrieved",
        data=JobStatusResponse(
            status=job_data["status"],
            progress=job_data["progress"],
            result_file_id=job_data.get("result_file_id"),
            error=job_data.get("error"),
        ).model_dump(),
    )


@router.get("/events/{job_id}")
async def get_events(job_id: str):
    """
    SSE Endpoint: Streams real-time job progress to the frontend.
    """

    async def event_generator():
        while True:
            if job_id not in JOB_STORE:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            job_data = JOB_STORE[job_id]
            # Payload banake stream karo
            payload = {
                "status": job_data["status"],
                "progress": job_data["progress"],
                "result_file_id": job_data.get("result_file_id"),
                "error": job_data.get("error"),
            }
            yield f"data: {json.dumps(payload)}\n\n"

            # Agar job complete ya fail ho gayi, toh connection close kar do
            if job_data["status"] in ["completed", "failed"]:
                break

            # Har 2 second me update bhejo (server overload bachane ke liye)
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/list", response_model=ApiResponse)
async def list_interpolated_files():
    """
    Get a list of all interpolated dataset folders and their sizes from Hugging Face.
    """
    try:
        bucket_path = f"hf://buckets/{HF_BUCKET_ID}/interpolations/"
        if not fs.exists(bucket_path):
            return ApiResponse(success=True, message="No files generated yet", data=[])

        folders = fs.ls(bucket_path, detail=False)
        files_info = []

        for folder_path in folders:
            folder_name = Path(folder_path).name  # The UUID
            inner_files = fs.glob(f"{folder_path}/*")

            if inner_files:
                actual_file = inner_files[0]
                file_metadata = fs.info(actual_file)

                files_info.append(
                    {
                        "fileId": folder_name,
                        "filename": Path(actual_file).name,
                        "size_bytes": file_metadata.get("size", 0),
                    }
                )

        return ApiResponse(
            success=True,
            message="Files retrieved successfully",
            data=files_info,
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"Failed to list interpolated files: {str(e)}",
            data=[],
        )
