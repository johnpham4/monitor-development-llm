.PHONY:
.ONESHELL:

env:
	poetry env use .venv/bin/python

mlflow_server:
	docker compose -f mlflow/compose.yml up -d

mlflow_url:
	@curl -s http://localhost:4040/api/tunnels || echo "Ngrok not running on port 4040"
	@echo "\nCurrent .env MLFLOW_TRACKING_URI:"
	@grep MLFLOW_TRACKING_URI .env || echo "MLFLOW_TRACKING_URI not found in .env"

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



jenkins_password:
	docker exec -it jenkins-master cat /var/jenkins_home/secrets/initialAdminPassword

cloudfare:
	cloudflared tunnel --url localhost:5002

remove-data:
	rm -rf data/mlflow

clean: down remove-data jenkins-down
