#!/bin/bash
# Rollback script for Taskly API

ENVIRONMENT=${1:-production}
NAMESPACE=${2:-$ENVIRONMENT}

echo "🔄 Rolling back $ENVIRONMENT deployment..."

if [ "$ENVIRONMENT" == "production" ]; then
  az aks get-credentials --resource-group rg-kingsly-production --name aks-kingsly-production
else
  az aks get-credentials --resource-group rg-kingsly-staging --name aks-kingsly-staging
fi

kubectl rollout undo deployment/taskly-api -n $NAMESPACE
kubectl rollout status deployment/taskly-api -n $NAMESPACE --timeout=5m

echo "✅ Rollback completed for $ENVIRONMENT!"
