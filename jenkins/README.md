
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
### Set up Minikube connection
1. Go to `Manage Jenkins` → `Clouds` → `New Cloud` → `Kubernetes`
2. **Kubernetes URL:** `https://kubernetes.default.svc`
3. **Credentials:** Add → Secret text → Paste token from above
4. Check "Disable https certificate check"
5. add credentails -> secret text -> go to section 8 for token.
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

## 6. Setup GitHub Auto-Trigger

### Enable GitHub Webhook for Auto-Build

**Configure Jenkins for GitHub Integration:**

1. **Install GitHub Plugin:**
   - Go to `Manage Jenkins` → `Plugins`
   - Install: `GitHub`, `GitHub Integration`

2. **Configure GitHub Webhook:**
   ```bash
   # Get Jenkins webhook URL (replace with your setup)
   # Format: http://your-jenkins-url/github-webhook/
   kubectl port-forward svc/jenkins 8080:8080 -n jenkins
   # Webhook URL: http://localhost:8080/github-webhook/
   ```

3. **Setup GitHub Repository Webhook:**
   - Go to your GitHub repository: `https://github.com/johnpham4/monitor-development-llm`
   - Navigate to `Settings` → `Webhooks` → `Add webhook`
   - **Payload URL:** `http://your-public-jenkins-url/github-webhook/`
   - **Content type:** `application/json`
   - **Events:** Select `Just the push event`
   - **Active:** Check this box
   - Click `Add webhook`

4. **Configure Jenkins Job for GitHub Trigger:**
   - Edit your Pipeline job
   - Go to `Build Triggers` section
   - Check `GitHub hook trigger for GITScm polling`
   - **Save**

### Alternative: Polling Method (If webhook not accessible)

If your Jenkins is not publicly accessible, use polling:

1. **Configure SCM Polling:**
   - Edit Pipeline job → `Build Triggers`
   - Check `Poll SCM`
   - **Schedule:** `H/5 * * * *` (poll every 5 minutes)
   - **Save**

### Expose Jenkins Publicly (For Webhook)

**Option 1: Using ngrok (Development)**
```bash
# Install ngrok and expose Jenkins
ngrok http 8080
# Use the ngrok URL for GitHub webhook
```

**Option 2: Using Minikube tunnel (Local)**
```bash
# Expose Jenkins service
minikube tunnel
kubectl get svc jenkins -n jenkins
# Use the external IP for webhook
```

### Test Auto-Trigger

1. **Make a code change** in your repository
2. **Commit and push** to main branch:
   ```bash
   git add .
   git commit -m "Test auto-trigger"
   git push origin main
   ```
3. **Check Jenkins** - Build should start automatically
4. **Monitor logs** in Jenkins console output

### Verify Webhook

**Check GitHub webhook delivery:**
- Go to GitHub repo → `Settings` → `Webhooks`
- Click on your webhook → `Recent Deliveries`
- Verify successful delivery (green checkmark)

**Check Jenkins logs:**
```bash
kubectl logs deployment/jenkins -n jenkins | grep -i github
```

## 7. Run Pipeline

### Manual Build
1. Click **Build with Parameters**
2. **Pass the key**
3. Pipeline will automatically:
   - Build Docker image
   - Push to DockerHub
   - Deploy to `model-serving` namespace using Helm

### Auto-Build (After GitHub integration)
- Pipeline will trigger automatically on code push
- Monitor build progress in Jenkins dashboard
- Check deployment status: `kubectl get pods -n model-serving`

## 8. Troubleshooting

### Jenkins can't connect to Kubernetes:
```bash
# Check service account
kubectl get sa jenkins -n jenkins
kubectl describe sa jenkins -n jenkins

# Create new token if needed
kubectl create token jenkins -n jenkins --duration=8760h
```

### Docker build fails:
- Ensure DockerHub credentials are configured correctly
- Check AWS credentials in Jenkins environment variables
