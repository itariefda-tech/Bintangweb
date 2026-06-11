#!/bin/bash
set -euo pipefail

APP_NAME="bintangweb-app"
IMAGE_NAME="bintangweb-app"
APP_DIR="/opt/apps/Bintangweb"
NETWORK_NAME="hosting_web"
HOST_PORT="5080"
CONTAINER_PORT="5080"
DEPLOY_ID="$(date +%Y%m%d%H%M%S)"
CANDIDATE_IMAGE="${IMAGE_NAME}:${DEPLOY_ID}"
BACKUP_NAME="${APP_NAME}-previous-${DEPLOY_ID}"

cd "$APP_DIR"

echo "==> Sync repository"
git fetch origin
git reset --hard origin/main
git clean -fd

echo "==> Ensure Docker network exists"
docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 || \
  docker network create "$NETWORK_NAME"

echo "==> Build candidate image"
docker build --pull -t "$CANDIDATE_IMAGE" .

had_previous=false
if docker container inspect "$APP_NAME" >/dev/null 2>&1; then
  had_previous=true
  echo "==> Preserve previous container for rollback"
  docker rename "$APP_NAME" "$BACKUP_NAME"
  docker stop "$BACKUP_NAME" >/dev/null
fi

rollback() {
  echo "==> Rolling back deployment"
  docker rm -f "$APP_NAME" >/dev/null 2>&1 || true
  docker image rm "$CANDIDATE_IMAGE" >/dev/null 2>&1 || true

  if [ "$had_previous" = true ]; then
    docker rename "$BACKUP_NAME" "$APP_NAME"
    docker start "$APP_NAME" >/dev/null
    echo "Previous container restored."
  fi
}

echo "==> Start candidate container on port $HOST_PORT"
if ! docker run -d \
  --name "$APP_NAME" \
  --restart unless-stopped \
  --network "$NETWORK_NAME" \
  -p "$HOST_PORT:$CONTAINER_PORT" \
  "$CANDIDATE_IMAGE" >/dev/null; then
  rollback
  exit 1
fi

echo "==> Wait for application health check"
for attempt in $(seq 1 20); do
  if docker exec "$APP_NAME" wget -qO- \
    "http://127.0.0.1:$CONTAINER_PORT/health" >/dev/null 2>&1; then
    break
  fi

  if [ "$attempt" -eq 20 ]; then
    echo "Deployment failed: application did not become healthy."
    docker logs "$APP_NAME"
    rollback
    exit 1
  fi

  sleep 2
done

echo "==> Promote candidate image"
docker tag "$CANDIDATE_IMAGE" "$IMAGE_NAME:latest"
docker image rm "$CANDIDATE_IMAGE" >/dev/null

if [ "$had_previous" = true ]; then
  docker rm "$BACKUP_NAME" >/dev/null
fi

echo "==> Cleanup unused Docker images"
docker image prune -f

echo ""
echo "DEPLOY SUCCESS"
echo "http://202.74.75.203:$HOST_PORT"
