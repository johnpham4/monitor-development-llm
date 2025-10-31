
kubectl apply -f jenkins-deployment.yaml
kubectl apply -f jenkins-service.yaml
minikube service jenkins -n jenkins
kubectl exec -n jenkins -it jenkins-657fdfb988-nw8bc -- /bin/cat /var/jenkins_home/secrets/initialAdminPassword


# tạo namespace Jenkins nếu chưa có
kubectl create namespace jenkins

# tạo service account
kubectl create sa jenkins -n jenkins

# tạo token
kubectl create token jenkins -n jenkins --duration=8760h

# tạo rolebinding
kubectl create rolebinding jenkins-admin-binding \
  --clusterrole=admin \
  --serviceaccount=jenkins:jenkins \
  --namespace=jenkins