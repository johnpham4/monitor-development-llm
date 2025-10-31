FROM jenkins/jenkins:lts

# Chạy dưới quyền root để cài đặt
USER root

# Cài plugin Jenkins
RUN jenkins-plugin-cli --plugins "git:latest docker-workflow:latest workflow-aggregator:latest"

# Cài các công cụ cần thiết
RUN apt-get update && \
    apt-get install -y docker.io curl unzip apt-transport-https gnupg lsb-release && \
    rm -rf /var/lib/apt/lists/*

# Cài kubectl trực tiếp (tránh lỗi repo 404)
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl

# Cài Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Quay lại user Jenkins
USER jenkins
