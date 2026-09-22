#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
set -a
source ./.env
set +a

url="http://localhost:${METABASE_PORT:-3300}/api/health"
for _ in $(seq 1 120); do
  if curl --fail --silent "$url" >/dev/null; then
    echo "metabase health: PASS"
    docker compose --env-file .env ps
    exit 0
  fi
  sleep 2
done

echo "metabase health: TIMEOUT" >&2
docker compose --env-file .env ps >&2 || true
docker compose --env-file .env logs --tail=200 metabase >&2 || true
exit 1
