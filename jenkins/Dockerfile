FROM jenkins/jenkins:lts

USER root

# 1. Cài plugin Jenkins
RUN jenkins-plugin-cli --plugins "git:latest docker-workflow:latest workflow-aggregator:latest"

# 2. Cài Docker và các tool cơ bản
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        docker.io \
        curl \
        unzip \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release && \
    rm -rf /var/lib/apt/lists/*

# 3. Cài kubectl (phiên bản mới)
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list || true && \
    apt-get update || true && \
    apt-get install -y kubectl || true

# THAY THẾ bằng lệnh cài trực tiếp binary (ổn định hơn)
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl

# 4. Cài Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

USER jenkins
