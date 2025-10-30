#!/usr/bin/env python3
"""
Model downloader for build-time model deployment.
Uses MLflow model registry to get S3 path, then downloads directly via boto3.
"""
import os
import sys
import re
import boto3
import mlflow
from tqdm import tqdm

def download_model():
    """
    Download model from S3 using MLflow model registry metadata.

    Returns:
        bool: True if successful, False otherwise
    """

    # Validate environment
    required_envs = ["MLFLOW_TRACKING_URI", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"]
    missing = [env for env in required_envs if not os.getenv(env)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        return False

    model_name = os.getenv("MODEL_NAME", "health-llm-gguf")

    try:
        # Step 1: Query MLflow for S3 path (minimal MLflow usage)
        print(f"Querying MLflow for model: {model_name}")
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        client = mlflow.tracking.MlflowClient()

        versions = client.get_latest_versions(model_name)
        if not versions:
            print(f"ERROR: No versions found for model '{model_name}'")
            return False

        s3_path = versions[0].source
        print(f"Model S3 path: {s3_path}")

        # Step 2: Parse S3 path
        match = re.match(r"s3://([^/]+)/(.*)", s3_path)
        if not match:
            print(f"ERROR: Invalid S3 path format: {s3_path}")
            return False

        bucket, prefix = match.groups()
        print(f"S3 Bucket: {bucket}, Prefix: {prefix}")

        # Step 3: Direct S3 connection (faster than MLflow)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION")
        )

        # Step 4: Find .gguf files
        print("Scanning for .gguf files...")
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' not in response:
            print(f"ERROR: No files found in s3://{bucket}/{prefix}")
            return False

        gguf_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.gguf')]
        if not gguf_files:
            print("ERROR: No .gguf files found")
            all_files = [obj['Key'] for obj in response['Contents'][:10]]  # Show first 10
            print(f"Available files (first 10): {all_files}")
            return False

        # Step 5: Download largest .gguf file (typically the main model)
        gguf_file = max(gguf_files, key=lambda f: next(obj['Size'] for obj in response['Contents'] if obj['Key'] == f))
        file_size = next(obj['Size'] for obj in response['Contents'] if obj['Key'] == gguf_file)

        print(f"Downloading: {gguf_file} ({file_size / 1024 / 1024:.1f} MB)")

        # Step 6: Download with progress bar
        def progress_callback(bytes_transferred):
            pbar.update(bytes_transferred)

        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
            s3_client.download_file(
                Bucket=bucket,
                Key=gguf_file,
                Filename="./gguf_model.gguf",
                Callback=progress_callback
            )

        print("Model downloaded successfully")
        return True

    except Exception as e:
        print(f"ERROR: Download failed: {e}")
        return False

if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)