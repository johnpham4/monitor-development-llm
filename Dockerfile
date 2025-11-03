FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libopenblas-dev libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/download_model.py ./src/

# Build arguments
ARG MLFLOW_TRACKING_URI
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG AWS_BUCKET_NAME
ARG MODEL_NAME=health-llm-gguf

# Download model if MLflow URI provided
RUN if [ -n "$MLFLOW_TRACKING_URI" ]; then \
        export MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI \
               AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
               AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
               AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
               AWS_BUCKET_NAME=$AWS_BUCKET_NAME \
               MODEL_NAME=$MODEL_NAME && \
        echo ">>> Downloading model..." && \
        python3 src/download_model.py || { \
            echo "ERROR: Model download failed. Build stopped."; \
            exit 1; \
        } && \
        echo ">>> Model downloaded successfully"; \
    else \
        echo "WARNING: No MLflow URI provided. Skipping model download."; \
    fi

EXPOSE 8000 7860

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 & sleep 3 && cd src && python frontend.py"]
