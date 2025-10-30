pipeline {
    agent any

    parameters {
        string(name: 'AWS_ACCESS_KEY_ID', defaultValue: '', description: 'AWS Access Key')
        string(name: 'AWS_SECRET_ACCESS_KEY', defaultValue: '', description: 'AWS Secret Key')
    }

    environment {
        DOCKER_CREDENTIAL_ID = 'dockerhub'
        KUBERNETES_NAMESPACE = "model-serving"
        HELM_CHART_PATH = './helm'
        IMAGE_TAG = "${BUILD_NUMBER}"

        DOCKER_REPOSITORY = "minhjohn427/fastapi_app"
        MODEL_NAME = "health-llm-gguf"
        AWS_ACCESS_KEY_ID = "${params.AWS_ACCESS_KEY_ID}"
        AWS_SECRET_ACCESS_KEY = "${params.AWS_SECRET_ACCESS_KEY}"
        AWS_DEFAULT_REGION = "ap-southeast-2"
        AWS_BUCKET_NAME = "mlflow-artifacts-monitor"
        MLFLOW_TRACKING_URI = "https://victoria-communicable-sometimes.ngrok-free.dev"
    }

    stages {

        stage('Build & Push') {
            steps {
                script {
                    echo ">>> Building Docker image..."
                    def img = docker.build(
                        "${env.DOCKER_REPOSITORY}:${IMAGE_TAG}",
                        "--build-arg MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} " +
                        "--build-arg AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} " +
                        "--build-arg AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} " +
                        "--build-arg AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} " +
                        "--build-arg AWS_BUCKET_NAME=${AWS_BUCKET_NAME} " +
                        "--build-arg MODEL_NAME=${MODEL_NAME} ."
                    )

                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIAL_ID) {
                        img.push()
                        img.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Minikube') {
            agent {
                docker {
                    image 'lachlanevenson/k8s-helm:latest'
                    args '-v $HOME/.kube:/root/.kube'
                }
            }
            steps {
                script {
                    sh '''
                    echo ">>> Checking Kubernetes nodes..."
                    kubectl get nodes

                    echo ">>> Deploying with Helm..."
                    helm upgrade --install txtapp ${HELM_CHART_PATH} \
                        --namespace ${KUBERNETES_NAMESPACE} --create-namespace \
                        --set image.repository=${DOCKER_REPOSITORY} \
                        --set image.tag=${IMAGE_TAG}
                    '''
                }
            }
        }
    }
}
