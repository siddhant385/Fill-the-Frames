from pydantic import BaseModel
from typing import List, Dict

class MetricsRequest(BaseModel):
    frame_a_id: str
    frame_b_id: str
    metrics: List[str]

class MetricsResponse(BaseModel):
    psnr_db: float
    ssim: float
    accuracy_percentage: float
