# Dima M2 — Isolated Metabase Lab

This directory is a P2 infrastructure laboratory. It is deliberately not wired into
Dima product code.

## Pinned runtime

```text
Metabase:  v0.63.18
image:     metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
Postgres:  17.11
image:     postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
```

The Metabase source-audit SHA is separate and lives in
`backend/belgeler/metabase/DIMA_METABASE_SOURCE_LOCK.md`.

## Start

```bash
cp .env.example .env
docker compose --env-file .env up -d
./scripts/health.sh
set -a; source .env; set +a
python3 scripts/bootstrap.py
python3 scripts/capability_probe.py --json-out artifacts/capability.json
```

## Persistence + backup/restore

```bash
docker compose --env-file .env restart metabase
./scripts/health.sh
python3 scripts/capability_probe.py --json-out artifacts/capability-after-restart.json

./scripts/backup.sh artifacts/metabase-app-db.dump
./scripts/restore-smoke.sh artifacts/metabase-app-db.dump
```

## What the probe proves

Separately:
- process health;
- unauthenticated Agent API denial;
- authenticated Agent API ping;
- Agent search/read-resource;
- portable structured query construction;
- execute and combined query;
- observed pagination continuation and <=200 rows/page;
- raw SQL endpoint returns 403 because the lab kill-switch is explicitly off.

It does **not** prove Dima semantic bridge feasibility, semantic equivalence, tenant mapping,
or production readiness. Those remain later gates.

## Data/security

- Neither Postgres service exposes a host port.
- Metabase is bound to loopback only.
- Metabase application DB has its own persistent Docker volume.
- App-DB dumps may contain sensitive analytical/application state; do not commit them.
- `.env` and `artifacts/` are local/CI material and must not be committed.
- The seeded analytics DB contains synthetic data only.

## Stop

```bash
docker compose --env-file .env down
```

Use `down -v` only when intentionally destroying lab state.
