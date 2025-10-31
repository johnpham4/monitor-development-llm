FROM jenkins/jenkins:lts

USER root

RUN jenkins-plugin-cli --plugins "git:latest docker-workflow:latest workflow-aggregator:latest"

USER jenkins

