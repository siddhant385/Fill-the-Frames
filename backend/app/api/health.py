from fastapi import APIRouter, Request
from app.schemas.common import ApiResponse
from app.core.config import APP_NAME, APP_VERSION

router = APIRouter()

@router.get("/", response_model=ApiResponse)
async def health_check():
    """Basic API health check."""
    return ApiResponse(
        success=True, 
        message="API is healthy", 
        data={
            "service": APP_NAME,
            "version": APP_VERSION,
            "status": "online"
        }
    )

@router.get("/gpu", response_model=ApiResponse)
async def health_gpu(request: Request):
    """Checks if CUDA/GPU is actually available and being used by the model."""
    cuda_available = False
    
    # Check if model is loaded and if it's using CUDA
    model_instance = getattr(request.app.state, "model", None)
    if model_instance and hasattr(model_instance, "session"):
        providers = model_instance.session.get_providers()
        if "CUDAExecutionProvider" in providers:
            cuda_available = True

    return ApiResponse(
        success=True, 
        message="GPU status retrieved", 
        data={"cuda_available": cuda_available}
    )

@router.get("/models", response_model=ApiResponse)
async def health_models(request: Request):
    """Checks if the heavy ONNX models are loaded into RAM."""
    model_instance = getattr(request.app.state, "model", None)
    rife_status = "loaded" if model_instance else "not_loaded"
    
    return ApiResponse(
        success=True, 
        message="Models status retrieved", 
        data={"rife": rife_status}
    )
