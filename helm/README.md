# Tạo namespace nếu chưa có
kubectl create namespace model-serving --dry-run=client -o yaml | kubectl apply -f -

# Deploy với Helm
helm upgrade --install qa-chatbot ./helm \
  --namespace model-serving --create-namespace  \
  --set image.repository=minhjohn427/fastapi_app \
  --set image.tag=latest \
  --set service.type=LoadBalancer \
  --set service.port=8000

