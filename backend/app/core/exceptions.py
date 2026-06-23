from fastapi import HTTPException, status

class ModelNotLoadedError(HTTPException):
    """Jab ONNX model memory me load na ho paye."""
    def __init__(self, detail: str = "AI Model is not loaded into memory. Server might be starting up or lacking resources."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=detail
        )

class InvalidFileFormatError(HTTPException):
    """Jab user NetCDF (.nc) ke alawa koi kachra file upload kare."""
    def __init__(self, detail: str = "Invalid file format. Only .nc (NetCDF) files are supported."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=detail
        )

class ProcessingPipelineError(HTTPException):
    """Jab SatPy ya ONNX inference ke beech me koi math error aa jaye."""
    def __init__(self, detail: str = "Internal error occurred during image interpolation."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=detail
        )
