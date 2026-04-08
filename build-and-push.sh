#!/usr/bin/env bash
set -euo pipefail

REGION=${REGION:-us-west-2}
ACCOUNT_ID=${ACCOUNT_ID:?Set ACCOUNT_ID}
REGISTRY="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REGISTRY"

services=(auth-service enter-service analytics-service show-service)
for svc in "${services[@]}"; do
  aws ecr create-repository --repository-name "$svc" --region "$REGION" >/dev/null 2>&1 || true
  docker build -t "$svc:latest" "services/$svc"
  docker tag "$svc:latest" "$REGISTRY/$svc:latest"
  docker push "$REGISTRY/$svc:latest"
done
