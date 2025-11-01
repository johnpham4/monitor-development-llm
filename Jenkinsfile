pipeline {
    agent any

    parameters {
        string(name: 'AWS_ACCESS_KEY_ID', defaultValue: '', description: 'AWS Access Key')
        string(name: 'AWS_SECRET_ACCESS_KEY', defaultValue: '', description: 'AWS Secret Key')
    }

    environment {
        DOCKER_REPOSITORY = "minhjohn427/fastapi_app"
        IMAGE_TAG = "${BUILD_NUMBER}"

        MODEL_NAME = "health-llm-gguf"
        AWS_ACCESS_KEY_ID = "${params.AWS_ACCESS_KEY_ID}"
        AWS_SECRET_ACCESS_KEY = "${params.AWS_SECRET_ACCESS_KEY}"
        AWS_DEFAULT_REGION = "ap-southeast-2"
        AWS_BUCKET_NAME = "mlflow-artifacts-monitor"
        MLFLOW_TRACKING_URI = "https://victoria-communicable-sometimes.ngrok-free.dev"
        KUBECONFIG = "/root/.kube/config"
    }

    stages {

        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo ">>> Building Docker image..."
                    sh """
                        docker build -t ${DOCKER_REPOSITORY}:${IMAGE_TAG} \
                            --build-arg MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
                            --build-arg AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
                            --build-arg AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
                            --build-arg AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
                            --build-arg AWS_BUCKET_NAME=${AWS_BUCKET_NAME} \
                            --build-arg MODEL_NAME=${MODEL_NAME} .
                    """

                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub') {
                        img.push()
                        img.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    echo ">>> Deploying to Minikube..."
                    sh 'kubectl version --client'
                    sh 'kubectl get nodes'
                    sh 'helm version'

                    sh """
                        helm upgrade --install txtapp ./helm \
                        --namespace model-serving --create-namespace \
                        --set image.repository=${DOCKER_REPOSITORY} \
                        --set image.tag=${IMAGE_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed. Check logs above."
        }
    }
}
