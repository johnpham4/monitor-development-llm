
# Jenkins CI/CD Setup on Kubernetes

## 1. Build Jenkins Image

```bash
minikube start
# Switch to Minikube Docker environment
eval $(minikube docker-env)

# Build custom Jenkins image with Docker + kubectl + Helm
cd jenkins
docker build -t jenkins-custom:latest .
```

## 2. Deploy Jenkins to Kubernetes

```bash
# Create namespace
kubectl create namespace jenkins

# Deploy Jenkins with RBAC and PVC
kubectl apply -f jenkins-rbac.yaml
kubectl apply -f jenkins-pvc.yaml
kubectl apply -f jenkins-deployment.yaml
kubectl apply -f jenkins-service.yaml
```

## 3. Access Jenkins

```bash
# Port forward to access Jenkins UI
kubectl port-forward svc/jenkins 8080:8080 -n jenkins

# Get initial admin password
kubectl logs deployment/jenkins -n jenkins | grep -A 5 "Jenkins initial setup"
```

Access Jenkins at: http://localhost:8080

## 4. Configure Jenkins

### Install Required Plugins
- Go to `Manage Jenkins` → `Plugins`
- Install: `Docker Pipeline`, `Kubernetes`

### Setup Kubernetes Connection

```bash
# Create service account token
kubectl create token jenkins -n jenkins --duration=8760h
# Copy this token
```

**In Jenkins UI:**
1. Go to `Manage Jenkins` → `Clouds` → `New Cloud` → `Kubernetes`
2. **Kubernetes URL:** `https://kubernetes.default.svc`
3. **Credentials:** Add → Secret text → Paste token from above
4. Check "Disable https certificate check"
5. add credentails -> secret text -> go to section 7 for token.
6. **Test Connection**
7. tick websocket
8. add jenkins url
9. **save**

### Setup DockerHub Credentials

1. Go to `Manage Jenkins` → `Credentials` → `Global`
2. Add → Username/Password
3. **ID:** `dockerhub`
4. **Username:** Your DockerHub username
5. **Password:** Your DockerHub access token

### Configure Build Environment Variables

1. Go to `Manage Jenkins` → `Configure System` → `Global properties`


## 5. Create Pipeline Job

1. **New Item** → **Pipeline**
2. **Pipeline script from SCM**
3. **This project is parameterized**
  String parameter - `AWS_ACCESS_KEY_ID`: Your AWS access key
  String parameter - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
4. **Git URL:** `https://github.com/johnpham4/monitor-development-llm.git`
5. **Pipeline:** `Pipeline script from SCM` -> `Git` -> `Repository` -> `main`
6. **Script file:** Jenkinsfile
7. **Save**

## 6. Run Pipeline

1. Click **Build with Parameters**
2. **Pass the key**
3. Pipeline will automatically:
   - Build Docker image
   - Push to DockerHub
   - Deploy to `model-serving` namespace using Helm

## 7. Troubleshooting

### Jenkins can't connect to Kubernetes:
```bash
# Check service account
kubectl get sa jenkins -n jenkins
kubectl describe sa jenkins -n jenkins

# Create new token if needed
kubectl create token jenkins -n jenkins --duration=8760h
```

### Pipeline fails with permission errors:
```bash
# Check RBAC
kubectl get clusterrolebinding jenkins-admin

# Recreate if needed
kubectl apply -f jenkins-rbac.yaml
```

### Docker build fails:
- Ensure DockerHub credentials are configured correctly
- Check AWS credentials in Jenkins environment variables
