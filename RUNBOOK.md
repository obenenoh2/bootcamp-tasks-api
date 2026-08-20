# Incident Runbook: API Error Rate Exceeds 5%

## Overview

This runbook provides step-by-step instructions for responding to the **HighErrorRate** alert, which triggers when the Taskly API error rate exceeds 5% for 5 minutes.

## Alert Details

| Property | Value |
|----------|-------|
| **Alert Name** | HighErrorRate |
| **Severity** | Critical |
| **Trigger Condition** | Error rate > 5% for 5 minutes |
| **Notification** | Email to obenEnohkingsly@gmail.com |

## Incident Response Steps

### 1. Acknowledge the Alert

- Check your email for the alert notification
- Acknowledge the incident in your team's communication channel
- Start a timer (SLA: 15 minutes to respond)

### 2. Initial Assessment (0-5 minutes)

#### Check Application Health

```bash
# Get API IP
API_IP=$(kubectl get svc taskly-api -n taskly -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Check health endpoint
curl http://$API_IP/health

# Check error rate
curl http://$API_IP/metrics | grep -E "http_requests_total.*5.."
Check Pod Status
bash
# Check pod status
kubectl get pods -n taskly

# Check pod logs
kubectl logs -n taskly -l app=taskly-api --tail=50
Check Database
bash
# Check PostgreSQL status
az postgres flexible-server show \
  --resource-group rg-kingsly-staging \
  --name postgres-kingsly-staging \
  --query "{state:state, version:version}" -o table
Check Redis
bash
# Check Redis status
kubectl get pods -n taskly | grep redis
kubectl logs -n taskly redis-<pod-id> --tail=20
3. Determine the Root Cause (5-15 minutes)
Common Causes
Issue	How to Check	Action
Database Connection Issues	Check PostgreSQL firewall rules	Add firewall rule if needed
Database Performance	Check PostgreSQL CPU/memory	Scale up database SKU
Redis Connection Issues	Check Redis connectivity	Restart Redis pod
Application Code Error	Check application logs	Rollback deployment
Resource Exhaustion	Check pod CPU/memory usage	Increase pod resources
Investigate Logs
bash
# Check application logs with trace_id
kubectl logs -n taskly -l app=taskly-api --tail=100 | grep -E "ERROR|error"

# Check database logs
az postgres flexible-server show-logs \
  --resource-group rg-kingsly-staging \
  --server-name postgres-kingsly-staging \
  --max 50
Investigate Metrics
bash
# Check error rate metric
curl http://$API_IP/metrics | grep -E "http_requests_total.*5.."

# Check request rate
curl http://$API_IP/metrics | grep -E "http_requests_total.*2.."

# Check response times
curl http://$API_IP/metrics | grep -E "http_request_duration_seconds"
4. Implement Mitigation (15-30 minutes)
Option A: Rollback Deployment
bash
# If the issue started after a recent deployment
kubectl rollout undo deployment taskly-api -n taskly

# Verify rollback
kubectl rollout status deployment taskly-api -n taskly
Option B: Scale Resources
bash
# Scale pods if resource constrained
kubectl scale deployment taskly-api -n taskly --replicas=5

# Increase pod resources
kubectl set resources deployment taskly-api -n taskly \
  -c taskly-api \
  --requests=cpu=500m,memory=256Mi \
  --limits=cpu=1000m,memory=512Mi
Option C: Restart Services
bash
# Restart API pods
kubectl rollout restart deployment taskly-api -n taskly

# Restart Redis if needed
kubectl delete pod -n taskly -l app=redis
5. Verification (30-45 minutes)
Verify Error Rate Decreased
bash
# Check error rate again
curl http://$API_IP/metrics | grep -E "http_requests_total.*5.."

# Check the alert status
# In Prometheus: http://localhost:9090/alerts
# The HighErrorRate alert should be resolved
Verify Application Health
bash
# Check all endpoints
curl http://$API_IP/health
curl http://$API_IP/tasks
curl -X POST http://$API_IP/tasks -H "Content-Type: application/json" -d '{"title":"Test"}'
Verify User Experience
bash
# Check response times
curl -w "Response time: %{time_total}s\n" -o /dev/null -s http://$API_IP/tasks
6. Communication
Send status update to stakeholders

Document the incident in your team's incident log

Provide a summary of the issue and resolution

7. Post-Mortem (Within 24 hours)
Document the Incident
What happened? - Describe the issue

Why did it happen? - Root cause analysis

How was it fixed? - Resolution steps

What will be done to prevent recurrence? - Action items

Action Items Template
Action Item	Owner	Due Date
Example: Add more logging	Team	1 week
Example: Increase database resources	Team	2 weeks
Example: Create automated test for error handling	Team	1 month
Escalation Path
Level	Contact	Response Time
Level 1: DevOps Engineer	On-call engineer	5 minutes
Level 2: Team Lead	Senior engineer	15 minutes
Level 3: Management	Engineering Manager	30 minutes
Alert Resolution
The alert is automatically resolved when:

Error rate drops below 5% for 5 minutes

The deployment is rolled back successfully

The issue is fixed and confirmed by monitoring

Prevention
Regular Maintenance
Weekly: Review error logs and metrics

Monthly: Performance review and capacity planning

Quarterly: Security review and dependency updates

Preventive Measures
✅ Implement proper error handling

✅ Use circuit breakers for external dependencies

✅ Set up proper monitoring and alerting

✅ Regular load testing

✅ Automated rollback on deployment failure

Resources
Grafana Dashboard: http://20.15.197.58

Prometheus: http://localhost:9090 (port-forward)

Alertmanager: http://localhost:9093 (port-forward)

Azure Portal: https://portal.azure.com
