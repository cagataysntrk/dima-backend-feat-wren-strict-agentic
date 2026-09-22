#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
set -a
source ./.env
set +a

out="${1:-artifacts/metabase-app-db.dump}"
mkdir -p "$(dirname "$out")"

docker compose --env-file .env exec -T metabase-app-db   pg_dump -U "$MB_APP_DB_USER" -d "$MB_APP_DB_NAME" -Fc > "$out"

test -s "$out"
echo "backup: PASS ($out)"
