from pydantic import BaseModel, Field
from typing import Optional

class InterpolationRequest(BaseModel):
    # AI ko 2 files aur 1 channel chahiye
    file_id_1: str = Field(..., description="First file ID (e.g., 00_min)")
    file_id_2: str = Field(..., description="Second file ID (e.g., 20_min)")
    variable: str = Field(default="C13", description="The satellite channel to interpolate")

class JobResponse(BaseModel):
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    status: str
    progress: float
    # result_frame ki jagah result_file_id aayega
    result_file_id: Optional[str] = None
    error: Optional[str] = None
