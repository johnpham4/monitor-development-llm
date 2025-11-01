
# Build
eval $(minikube docker-env)
docker build -t jenkins-custom:latest .


# Deploy
kubectl create namespace jenkins
kubectl apply -f jenkins-deployment.yaml
kubectl apply -f jenkins-service.yaml

# Access
minikube service jenkins -n jenkins
kubectl exec -n jenkins -it jenkin-podId -- /bin/cat /var/jenkins_home/secrets/initialAdminPassword


# tạo service account
kubectl create sa jenkins -n jenkins

# tạo token
kubectl create token jenkins -n jenkins --duration=8760h

# tạo rolebinding
kubectl create rolebinding jenkins-admin-binding \
  --clusterrole=admin \
  --serviceaccount=jenkins:jenkins \
  --namespace=jenkins
