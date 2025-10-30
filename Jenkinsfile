pipeline {
    agent any

    environment {
        HELM_CHART_PATH = './helm'
        KUBERNETES_NAMESPACE = "model-serving"
        IMAGE_NAME = "fastapi_app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_REPOSITORY = "minhjohn427/fastapi_app"
    }

    stages {
        stage('Setup Minikube Docker Env') {
            steps {
                script {
                    // Thiết lập Docker của Minikube
                    sh 'eval $(minikube -p minikube docker-env)'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build trực tiếp trong Minikube Docker
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub') {
                        sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REPOSITORY}:${IMAGE_TAG}"
                        sh "docker push ${DOCKER_REPOSITORY}:${IMAGE_TAG}"
                        sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REPOSITORY}:latest"
                        sh "docker push ${DOCKER_REPOSITORY}:latest"
                    }
                }
            }
        }

        stage('Deploy with Helm') {
            steps {
                script {
                    sh """
                        helm upgrade --install txtapp ${HELM_CHART_PATH} \
                            --namespace ${KUBERNETES_NAMESPACE} --create-namespace \
                            --set image.repository=${IMAGE_NAME} \
                            --set image.tag=${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Check Deployment') {
            steps {
                sh "kubectl get pods -n ${KUBERNETES_NAMESPACE}"
            }
        }
    }
}
