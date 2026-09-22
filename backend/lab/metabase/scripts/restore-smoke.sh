#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
set -a
source ./.env
set +a

dump="${1:-artifacts/metabase-app-db.dump}"
test -s "$dump"
smoke_db="metabase_restore_smoke"

docker compose --env-file .env exec -T metabase-app-db   dropdb -U "$MB_APP_DB_USER" --if-exists "$smoke_db"
docker compose --env-file .env exec -T metabase-app-db   createdb -U "$MB_APP_DB_USER" "$smoke_db"
cat "$dump" | docker compose --env-file .env exec -T metabase-app-db   pg_restore -U "$MB_APP_DB_USER" -d "$smoke_db" --no-owner --no-privileges

count="$(
  docker compose --env-file .env exec -T metabase-app-db     psql -U "$MB_APP_DB_USER" -d "$smoke_db" -Atc     "select count(*) from information_schema.tables where table_schema='public';"     | tr -d '[:space:]'
)"
if [ "${count:-0}" -le 0 ]; then
  echo "restore smoke: no restored public tables" >&2
  exit 1
fi

docker compose --env-file .env exec -T metabase-app-db   dropdb -U "$MB_APP_DB_USER" "$smoke_db"
echo "restore smoke: PASS ($count public tables)"
