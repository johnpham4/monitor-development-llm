# Set up
- Create a new `.env` file based on `.env.example` and populate the variables there
- Set up env var $ROOT_DIR: `export ROOT_DIR=$(pwd) && sed "s|^ROOT_DIR=.*|ROOT_DIR=$ROOT_DIR|" .env > .tmp && mv .tmp .env`
- Run `export $(grep -v '^#' .env | xargs)` to load the variables
- Create a new Python 3.11.9 environment: `conda create --prefix .venv python=3.11.9`
- Make sure Poetry use the new Python 3.11.9 environment: `poetry env use .venv/bin/python`
- Install Python dependencies with Poetry: `poetry install`

# Start services
## Common services
```shell
conda activate /mnt/d/projects/monitor_2_deployment/.venv
pip install -r requirements.txt
# Create data directory by current user to avoid permission issue when Docker Compose creates the data folder itself
mkdir -p data

docker network create monitoring

# Start supporting services
make ngrok && make ml-platform-up && make ml-platform-logs
# Wait until you see "Booting worker with pid..." then you can Ctrl + C to exit the logs following process

apt update -y && apt install -y curl
curl http://mlflow_server:5000
```

jenkins

install kubernetes, Docker Pipeline. plugin

set kuberbenete nội bộ là https://kubernetes.default.svc

Credentials
Secret Text → paste token từ bước 2

Test Connection
✓ chọn “Disable https certificate check” nếu self-signed

vào tạo global credential id dockerhub password = token, username = username dockerhub

add websocket, jenkins url
# Terminal 1: Backend API
kubectl port-forward svc/txtapp 8000:8000 -n model-serving

# Terminal 2: Frontend Gradio
kubectl port-forward svc/txtapp 7860:7860 -n model-serving