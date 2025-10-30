    pipeline {
        agent any

        parameters {
            string(name: 'AWS_ACCESS_KEY_ID', defaultValue: '', description: '')
            string(name: 'AWS_SECRET_ACCESS_KEY', defaultValue: '', description: '')
        }

        environment {
            DOCKER_CREDENTIAL_ID = 'dockerhub'
            KUBECONFIG_CREDENTIAL_ID = 'kubeconfig'
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
            stage('Build & Push Docker Image') {
                steps {
                    script {
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
            stage('Deploy with Helm') {
                steps {
                    withCredentials([file(credentialsId: KUBECONFIG_CREDENTIAL_ID, variable: 'KUBECONFIG')]) {
                        sh """
                            mkdir -p ~/.kube
                            cp \$KUBECONFIG ~/.kube/config
                            docker run --rm \
                                -v ~/.kube:/root/.kube \
                                -v $(pwd):/workspace \
                                -w /workspace \
                                alpine/helm:3.14.0 \
                                helm upgrade --install qa-chatbot ${HELM_CHART_PATH} \
                                    --namespace ${KUBERNETES_NAMESPACE} --create-namespace \
                                    --set image.repository=${env.DOCKER_REPOSITORY} \
                                    --set image.tag=${IMAGE_TAG}
                        """
                    }
                }
            }
        }
    }
