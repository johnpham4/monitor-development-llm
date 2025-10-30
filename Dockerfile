FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libopenblas-dev libomp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/

# Accept build arguments for MLflow connection
ARG MLFLOW_TRACKING_URI
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG AWS_BUCKET_NAME

# Set as environment variables for the build process
ENV MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
ENV AWS_BUCKET_NAME=$AWS_BUCKET_NAME

# Copy optimized Python download script
COPY scripts/download_model.py /app/src/download_model.py

# Force model download at build-time and fail if not successful
RUN if [ -n "$MLFLOW_TRACKING_URI" ]; then \
        echo ">>> Downloading model using optimized Python script..."; \
        MODEL_NAME=health-llm-gguf python3 /app/src/download_model.py || { \
            echo "ERROR: Model download failed. Stopping build."; exit 1; }; \
        echo ">>> Model downloaded successfully and stored in /app/src/"; \
    else \
        echo "ERROR: No MLflow URI provided. Stopping build."; exit 1; \
    fi

EXPOSE 8000 7860

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 & sleep 3 && cd src && python frontend.py"]
