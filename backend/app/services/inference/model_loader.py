import os

import onnxruntime as ort
from fastapi import HTTPException
from loguru import logger

from app.core.config import DEFAULT_MODEL_PATH


class ModelLoader:
    _session = None

    @classmethod
    def load_model(cls, model_path: str = DEFAULT_MODEL_PATH):
        if cls._session is not None:
            logger.info("AI Model is already loaded in memory.")
            return cls._session

        if not os.path.exists(model_path):
            logger.error(f"ONNX Model file not found at: {model_path}")
            # Ensure folder exists
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            raise HTTPException(
                status_code=500,
                detail="AI Model file missing from the models directory.",
            )

        try:
            logger.info(
                f"Waking up the AI Brain. Loading ONNX model from {model_path}..."
            )

            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 2
            sess_options.inter_op_num_threads = 1
            sess_options.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            )

            providers = ["CPUExecutionProvider"]

            cls._session = ort.InferenceSession(
                model_path, sess_options=sess_options, providers=providers
            )

            # Loguru ka mast .success() method
            logger.success("✅ ONNX model successfully loaded into memory!")
            return cls._session

        except Exception as e:
            logger.error(f"Failed to load ONNX model: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize AI model engine."
            )

    @classmethod
    def get_session(cls):
        if cls._session is None:
            raise HTTPException(
                status_code=503, detail="AI Model not loaded into memory."
            )
        return cls._session

    @classmethod
    def unload_model(cls):
        if cls._session is not None:
            cls._session = None
            logger.info("AI Model unloaded. RAM freed.")

