#!/bin/bash
set -euo pipefail

APP_NAME="${APP_NAME:-bintangweb-app}"
IMAGE_NAME="${IMAGE_NAME:-bintangweb-app}"
APP_DIR="${APP_DIR:-/opt/apps/Bintangweb}"
NETWORK_NAME="${NETWORK_NAME:-hosting_web}"
BIND_HOST="${BIND_HOST:-127.0.0.1}"
HOST_PORT="${HOST_PORT:-5080}"
CONTAINER_PORT="${CONTAINER_PORT:-5080}"
DATA_VOLUME="${DATA_VOLUME:-${APP_NAME}-data}"
PUBLIC_URL="${PUBLIC_URL:-https://feira.my.id}"

DEPLOY_ID="$(date +%Y%m%d%H%M%S)"
CANDIDATE_IMAGE="${IMAGE_NAME}:${DEPLOY_ID}"
BACKUP_NAME="${APP_NAME}-previous-${DEPLOY_ID}"

log() {
  printf '\n==> %s\n' "$1"
}

fail() {
  echo "Deployment failed: $1" >&2
  exit 1
}

for command in git docker; do
  command -v "$command" >/dev/null 2>&1 || fail "$command tidak ditemukan."
done

[ -d "$APP_DIR/.git" ] || fail "$APP_DIR bukan repository Git."
cd "$APP_DIR"

# Sinkron repo satu kali, lalu jalankan ulang deploy.sh versi terbaru
if [ "${DEPLOY_SYNCED:-0}" != "1" ]; then
  log "Sync repository with origin/main"
  git fetch origin main
  git reset --hard origin/main

  # .env diabaikan Git, tapi tetap kita lindungi eksplisit
  git clean -fd -e .env

  exec env DEPLOY_SYNCED=1 bash "$APP_DIR/deploy.sh"
fi

[ -f "$APP_DIR/.env" ] || fail "$APP_DIR/.env tidak ditemukan."

if ! grep -Eq '^[[:space:]]*OWNER_PASSWORD[[:space:]]*=[[:space:]]*[^[:space:]]' "$APP_DIR/.env"; then
  fail "OWNER_PASSWORD belum diatur di $APP_DIR/.env."
fi

chmod 600 "$APP_DIR/.env"

log "Ensure Docker network exists: $NETWORK_NAME"
docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 || \
  docker network create "$NETWORK_NAME" >/dev/null

log "Ensure persistent data volume exists: $DATA_VOLUME"
docker volume inspect "$DATA_VOLUME" >/dev/null 2>&1 || \
  docker volume create "$DATA_VOLUME" >/dev/null

log "Build candidate image: $CANDIDATE_IMAGE"
docker build --pull -t "$CANDIDATE_IMAGE" .

had_previous=false

if docker container inspect "$APP_NAME" >/dev/null 2>&1; then
  had_previous=true

  log "Preserve previous container for rollback"
  docker rename "$APP_NAME" "$BACKUP_NAME"
  docker stop "$BACKUP_NAME" >/dev/null
fi

rollback() {
  echo ""
  echo "==> Rolling back deployment"

  docker rm -f "$APP_NAME" >/dev/null 2>&1 || true
  docker image rm "$CANDIDATE_IMAGE" >/dev/null 2>&1 || true

  if [ "$had_previous" = true ] && docker container inspect "$BACKUP_NAME" >/dev/null 2>&1; then
    docker rename "$BACKUP_NAME" "$APP_NAME"
    docker start "$APP_NAME" >/dev/null
    echo "Previous container restored."
  else
    echo "No previous container available to restore."
  fi
}

log "Start candidate on ${BIND_HOST}:${HOST_PORT} -> ${CONTAINER_PORT}"

if ! docker run -d \
  --name "$APP_NAME" \
  --restart unless-stopped \
  --network "$NETWORK_NAME" \
  --env-file "$APP_DIR/.env" \
  -v "$DATA_VOLUME:/app/data" \
  -p "$BIND_HOST:$HOST_PORT:$CONTAINER_PORT" \
  "$CANDIDATE_IMAGE" >/dev/null; then

  rollback
  exit 1
fi

log "Wait for application health check"

healthy=false

for attempt in $(seq 1 30); do
  if docker exec "$APP_NAME" wget -qO- \
    "http://127.0.0.1:$CONTAINER_PORT/health" >/dev/null 2>&1; then

    healthy=true
    break
  fi

  if ! docker container inspect "$APP_NAME" >/dev/null 2>&1; then
    break
  fi

  sleep 2
done

if [ "$healthy" != true ]; then
  echo "Application did not become healthy. Recent logs:"
  docker logs --tail 200 "$APP_NAME" 2>&1 || true

  rollback
  exit 1
fi

log "Promote candidate image to ${IMAGE_NAME}:latest"

docker tag "$CANDIDATE_IMAGE" "$IMAGE_NAME:latest"
docker image rm "$CANDIDATE_IMAGE" >/dev/null 2>&1 || true

if [ "$had_previous" = true ] && docker container inspect "$BACKUP_NAME" >/dev/null 2>&1; then
  log "Remove previous container after successful health check"
  docker rm "$BACKUP_NAME" >/dev/null
fi

log "Cleanup dangling Docker images"
docker image prune -f >/dev/null

log "Verify local application"

docker exec "$APP_NAME" wget -qO- \
  "http://127.0.0.1:$CONTAINER_PORT/health"

echo ""

# Public check hanya informasional.
# Jika Cloudflare sementara bermasalah, deploy lokal tetap dianggap sukses.
if command -v curl >/dev/null 2>&1; then
  log "Public smoke check: ${PUBLIC_URL%/}/health"

  if curl -fsS --max-time 15 "${PUBLIC_URL%/}/health" >/dev/null; then
    echo "Public endpoint OK."
  else
    echo "WARNING: local deployment is healthy, but public endpoint check failed." >&2
    echo "Check cloudflared/DNS if ${PUBLIC_URL} is not reachable." >&2
  fi
fi

echo ""
echo "DEPLOY SUCCESS"
echo "App       : $APP_NAME"
echo "Image     : ${IMAGE_NAME}:latest"
echo "Local     : http://${BIND_HOST}:${HOST_PORT}"
echo "Public    : $PUBLIC_URL"
echo "Data      : $DATA_VOLUME -> /app/data"
