.PHONY:
.ONESHELL:

env:
	poetry env use .venv/bin/python

mlflow_server:
	docker compose -f mlflow/compose.yml up -d

mlflow_url:
	@MLFLOW_URL=$$(curl -s http://localhost:4040/api/tunnels | sed -n 's/.*"public_url":"\([^"]*\)".*/\1/p' | head -1); \
	if [ -n "$$MLFLOW_URL" ]; then \
		sed -i "s|^MLFLOW_TRACKING_URI=.*|MLFLOW_TRACKING_URI=$$MLFLOW_URL|" .env; \
	else \
		echo "No tunnel found. Try: make mlflow-debug"; \
	fi

metric:
	docker compose -f monitor/compose.yml up -d
	@echo "Grafana will be available at: http://localhost:3000"
	@echo "Prometheus will be available at: http://localhost:9090"
	@echo "Grafana Login: admin / admin"

app:
	docker compose -f compose.yml up -d

build-push:
	@if [ -f .env ]; then export $$(cat .env | xargs); fi && \
	docker build \
		--build-arg MLFLOW_TRACKING_URI=$$MLFLOW_TRACKING_URI \
		--build-arg AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID \
		--build-arg AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY \
		--build-arg AWS_DEFAULT_REGION=$$AWS_DEFAULT_REGION \
		--build-arg AWS_BUCKET_NAME=$$AWS_BUCKET_NAME \
		-t minhjohn427/fastapi_app:latest . && \
	docker push minhjohn427/fastapi_app:latest

down:
	docker compose -f monitor/compose.yml down || true
	docker compose -f mlflow/compose.yml down || true
	docker compose -f compose.yml down || true

# Jenkins CI/CD
jenkins_server:
	docker compose -f jenkins/compose.yml up -d

jenkins_down:
	docker compose -f jenkins/compose.yml down

jenkins_down:
	docker compose -f jenkins/compose.yml down

jenkins_password:
	docker exec -it jenkins-master cat /var/jenkins_home/secrets/initialAdminPassword

cloudfare:
	cloudflared tunnel --url localhost:5002

remove-data:
	rm -rf data/mlflow

clean: down remove-data jenkins-down
