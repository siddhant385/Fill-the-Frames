# Use the official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /code

# Install system dependencies required by scientific libraries (SatPy, ONNX, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create the temporary storage directory for serverless 1GB caching
RUN mkdir -p /tmp/satellite_cache && chmod 777 /tmp/satellite_cache

# We only copy the backend folder to avoid bloating the server with frontend code
COPY backend /code

# Since you are using a pyproject.toml in the backend, we install dependencies directly from it. 
# (If you prefer requirements.txt, you can change this to: RUN pip install --no-cache-dir -r requirements.txt)
RUN pip install --no-cache-dir .

# Expose port 7860 (Hugging Face standard)
EXPOSE 7860

# Run the FastAPI server. 
# Since we copied 'backend' contents into '/code', the app module is directly accessible.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
