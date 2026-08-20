# Taskly API

A production-grade task management API deployed on Azure Kubernetes Service (AKS) with full observability, CI/CD, and incident response capabilities.

## Architecture

![Architecture Diagram](docs/architecture.png)
┌─────────────────────────────────────────────────────────────────┐
│ Users / API Clients │
└─────────────────────────┬───────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Azure Load Balancer │
└─────────────────────────┬───────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ AKS Cluster │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Taskly API (3 replicas) │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │ │
│ │ │ Pod 1 │ │ Pod 2 │ │ Pod 3 │ │ │
│ │ │ :8000 │ │ :8000 │ │ :8000 │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Redis (Cache) │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ PostgreSQL (Database) │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Observability Stack │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Prometheus │ │ Grafana │ │ Loki │ │
│ │ Metrics │ │ Dashboards │ │ Logs │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Alertmanager (Email Alerts) │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

text

## Features

- ✅ **Task Management**: Create, read, update, and delete tasks
- ✅ **PostgreSQL Database**: Persistent storage with async support
- ✅ **Redis Caching**: Read-through cache for optimal performance
- ✅ **Prometheus Metrics**: Request count, duration, and custom business metrics
- ✅ **Structured Logging**: JSON logs with trace_id for distributed tracing
- ✅ **CI/CD Pipeline**: GitHub Actions with staging and production environments
- ✅ **Observability Stack**: Prometheus, Grafana, Loki, and Alertmanager
- ✅ **Email Alerts**: Real-time notifications for critical issues

## Prerequisites

- Azure CLI (`az`)
- Terraform (`terraform`)
- Kubernetes CLI (`kubectl`)
- Helm (`helm`)
- Docker
- Python 3.12+

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/obenenoh2/bootcamp-tasks-api.git
cd bootcamp-tasks-api
2. Provision Infrastructure
bash
# Login to Azure
az login

# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Apply infrastructure (staging)
terraform apply -var="environment=staging"

# Apply infrastructure (production)
terraform apply -var="environment=production"
3. Deploy the Application
bash
# Get AKS credentials
az aks get-credentials --resource-group rg-kingsly-staging --name aks-kingsly-staging

# Create namespace
kubectl create namespace taskly

# Deploy application
kubectl apply -f k8s-deployment.yaml -n taskly

# Get the external IP
kubectl get svc taskly-api -n taskly
4. Set Up Observability
bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.enabled=true \
  --set grafana.adminPassword=admin123

# Install Loki
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set promtail.enabled=true
Accessing Services
Service	URL	Credentials
Staging API	http://135.233.73.55	Public
Production API	http://52.230.138.43	Public
Grafana Dashboard	http://20.15.197.58	admin / admin123
Swagger UI	http://135.233.73.55/docs	Public
Metrics	http://135.233.73.55/metrics	Public
CI/CD Pipeline
The GitHub Actions pipeline runs automatically on push to main:

Build & Test: Builds the Docker image and runs tests

Scan: Vulnerability scanning with Trivy

Push: Pushes image to Azure Container Registry

Deploy to Staging: Automatic deployment to staging environment

Manual Approval: Manual approval required for production

Deploy to Production: Deployment to production environment

Pipeline Status
View pipeline runs at: https://github.com/obenenoh2/bootcamp-tasks-api/actions

Rollback
To rollback to a previous version:

bash
# Check deployment history
kubectl rollout history deployment taskly-api -n production

# Rollback to previous version
kubectl rollout undo deployment taskly-api -n production

# Rollback to specific revision
kubectl rollout undo deployment taskly-api -n production --to-revision=3
Trigger an Alert
To test email alerts:

bash
# Scale down the deployment to trigger ServiceDown alert
kubectl scale deployment taskly-api -n taskly --replicas=0

# Wait 30-60 seconds
# Check Alertmanager: http://localhost:9093 (port-forward)
# Check your email: obenEnohkingsly@gmail.com

# Scale back up
kubectl scale deployment taskly-api -n taskly --replicas=3
Alert Rules
Alert	Severity	Description
ServiceDown	Critical	API service is down for more than 30 seconds
HighErrorRate	Critical	Error rate exceeds 5% for 5 minutes
HighLatency	Warning	P95 latency exceeds 2 seconds for 5 minutes
Observability Dashboards
Grafana Dashboard
Access the Grafana dashboard at: http://20.15.197.58

Dashboard panels:

Request Rate: HTTP requests per second

Error Rate (5xx): Error percentage

P95 Latency: 95th percentile response time

Active Tasks: Current active tasks count

Prometheus Targets
Check Prometheus targets: http://localhost:9090/targets (port-forward required)

bash
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
Loki Logs
Query Loki logs:

bash
# In Grafana Explore, select Loki data source
# Query: {app="taskly-api"}
Environment Variables
Variable	Description	Default
DATABASE_URL	PostgreSQL connection string	Required
REDIS_URL	Redis connection string	Required
Development
Local Development
bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload
Running Tests
bash
pytest tests/
Troubleshooting
Common Issues
Pod CrashLoopBackOff
Check logs:

bash
kubectl logs -n taskly -l app=taskly-api --tail=50
Database Connection Issues
Check PostgreSQL firewall rules:

bash
az postgres flexible-server firewall-rule list \
  --resource-group rg-kingsly-staging \
  --server-name postgres-kingsly-staging
Redis Connection Issues
Check Redis is running:

bash
kubectl get pods -n taskly | grep redis
Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Create a Pull Request

License
This project is licensed under the MIT License.

Contact
Author: Kingsly Obene

Email: obenEnohkingsly@gmail.com

GitHub: https://github.com/obenenoh2
