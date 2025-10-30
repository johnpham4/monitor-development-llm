FROM jenkins/jenkins:lts
USER root

RUN jenkins-plugin-cli --plugins \
    "git:latest docker-workflow:latest workflow-aggregator:latest"

RUN apt-get update && apt-get install -y docker-cli

