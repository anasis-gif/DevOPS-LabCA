#!/usr/bin/env bash
set -euo pipefail
cd /opt/url-shortener
image="${1:?Pass a commit-specific GHCR image}"
[[ "$image" =~ ^ghcr\.io/[a-z0-9._/-]+:[a-f0-9]{40}$ ]] || { echo 'Invalid image tag' >&2; exit 1; }
exec 9>.deploy.lock
flock -w 120 9 || { echo 'Another deployment holds the host lock' >&2; exit 1; }
test -f .env || { echo 'Create /opt/url-shortener/.env first' >&2; exit 1; }
export IMAGE="$image"
previous="$(docker compose ps -q web | xargs -r docker inspect --format '{{.Config.Image}}')"
if [[ -n "$previous" ]]; then printf '%s\n' "$previous" > previous-image.txt; fi
if ! docker compose pull web || ! docker compose up -d --wait --wait-timeout 90 web; then
  echo 'Deployment FAILED. Inspect logs and use previous-image.txt to roll back.' >&2
  docker compose logs --tail 100 web || true
  exit 1
fi
printf '%s\n' "$image" > current-image.txt
echo "Deployment healthy: $image"
