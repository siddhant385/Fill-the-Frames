from starlette.config import Config
from starlette.datastructures import Secret

# Root directory se .env load karega
config = Config(".env")

APP_VERSION = "0.0.1"
APP_NAME = "Fill-the-Frames"
# Ise dynamic bana diya taaki kal ko v2 aaye toh ek jagah change karna pade
API_PREFIX = config("API_PREFIX", cast=str, default="/api/v1")

# Default values add kar di hain safety ke liye
API_KEY: Secret = config("API_KEY", cast=Secret, default="dev_secret_key")
IS_DEBUG: bool = config("IS_DEBUG", cast=bool, default=True)

# Path configurations defaults ke saath
UPLOAD_DIR: str = config("UPLOAD_DIR", cast=str, default="storage/uploads")
MODEL_DIR: str = config("MODEL_DIR", cast=str, default="models")
DEFAULT_MODEL_PATH: str = config("DEFAULT_MODEL_PATH", cast=str, default="models/ifnet_satellite_512.onnx")
