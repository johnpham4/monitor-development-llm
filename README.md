# Vietnamese Legal QA Chatbot

## Introduction

Our project focuses on implementing a Vietnamese Legal Question-Answering chatbot using fine-tuned LLM models in GGUF format. The system leverages MLOps practices with FastAPI backend, Gradio frontend, and comprehensive CI/CD pipeline using Jenkins and Kubernetes. This chatbot aims to provide accurate legal consultation in Vietnamese, making legal information more accessible to users through an intuitive web interface.

## Table of Contents

1. **Vietnamese Legal QA Chatbot**
   - Introduction
   - Project Structure
2. **Local**
   - Demo
   - Running in Docker
   - Monitoring
   - CI/CD
3. **Production**
   - Deploying to Kubernetes

## Project Structure

```
monitor_2_deployment/
├── demo.ipynb                     - Jupyter notebook for running the demo
├── docker-compose.yml             - Docker Compose configuration file
├── Dockerfile                     - Dockerfile for building the image
├── src/                           - Directory for application source code
│   ├── main.py                    - FastAPI backend server
│   ├── frontend.py                - Gradio web interface
│   └── chat_service.py            - LLM service logic
├── jenkins/                       - Directory for Jenkins configuration
│   ├── README.md                  - Jenkins setup guide
│   ├── Dockerfile                 - Custom Jenkins image
│   └── *.yaml                     - Kubernetes manifests
├── helm/                          - Directory for Helm chart deployment
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── mlflow/                        - Directory for MLflow tracking server
├── monitor/                       - Directory for monitoring (Prometheus, Grafana)
├── notebook/                      - Directory for model training notebooks
├── scripts/                       - Directory for utility scripts
├── Jenkinsfile                    - Jenkins pipeline script for CI/CD process
├── README.md                      - This README file
└── requirements.txt               - Python requirements file
```

# Local

First, set up the environment and install required packages:

**Python Version:** 3.11+

```bash
- Create a new `.env` file based on `.env.example` and populate the variables there
- Run `export $(grep -v '^#' .env | xargs)` to load the variables
```

## Running in Docker

To run the application in a Docker container, build the Docker image:

```bash
docker build -t vietnamese-legal-qa .
```

After building the Docker image, run the container:

```bash
docker run -p 8000:8000 -p 7860:7860 vietnamese-legal-qa
```

*[Image placeholder: Docker container running]*

The application will be available at:
- **Frontend:** `http://localhost:7860`
- **API Documentation:** `http://localhost:8000/docs`

*[Image placeholder: FastAPI docs interface]*

## Monitoring

To monitor the system, use Prometheus and Grafana. First, start the monitoring stack:

```bash
cd monitor
docker compose up -d
```

Access the monitoring dashboards:
- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3000` (admin/admin)

The Grafana dashboard displays application metrics, request rates, and system performance.

*[Image placeholder: Grafana dashboard]*

## CI/CD

We have build and deploy stages in our CI/CD pipeline using Jenkins. The pipeline automatically triggers on code commits and deploys to Kubernetes.

### Setup Jenkins

For detailed Jenkins configuration, see [jenkins/README.md](jenkins/README.md)

**Required Jenkins Plugins:**
- Docker Pipeline
- Kubernetes
- Kubernetes CLI

**Setup Credentials:**
- DockerHub credentials
- Kubernetes service account token

*[Image placeholder: Jenkins pipeline execution]*

*[Image placeholder: Local architecture diagram]*

# Production

## Deploying to Kubernetes

Deploy the application to Kubernetes cluster using Jenkins CI/CD pipeline:

### Prerequisites

- Minikube or Kubernetes cluster running
- Jenkins configured with Kubernetes access
- DockerHub credentials configured

### Deployment Process

1. **Automatic Pipeline Trigger:**
   - Push code to GitHub repository
   - Jenkins automatically detects changes
   - Pipeline builds Docker image and pushes to registry

2. **Kubernetes Deployment:**
   - Helm chart deploys application to `model-serving` namespace
   - Service exposes application ports
   - ConfigMaps and Secrets manage configuration

3. **Access Production App:**

```bash
# Check deployment status
kubectl get pods -n model-serving

# Access application
kubectl port-forward svc/txtapp 7860:7860 -n model-serving
```

The production application will be available at `http://localhost:7860`

*[Image placeholder: Kubernetes deployment]*

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │───▶│   FastAPI       │───▶│   GGUF Model    │
│   (Frontend)    │    │   (Backend)     │    │   (Vietnamese)  │
│   Port: 7860    │    │   Port: 8000    │    │   Legal QA      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Kubernetes Pod        │
                    │   (model-serving ns)      │
                    └───────────────────────────┘
```

### CI/CD Pipeline Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Code     │───▶│   Jenkins   │───▶│   Docker    │───▶│ Kubernetes  │
│   (GitHub)  │    │  Pipeline   │    │   Build     │    │   Deploy    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

*[Image placeholder: Production architecture diagram]*

---

**Quick Links:**
- [Jenkins Setup Guide](jenkins/README.md)
- [MLflow UI](http://localhost:5002) (when running)
- [Grafana Dashboard](http://localhost:3000) (when running)

