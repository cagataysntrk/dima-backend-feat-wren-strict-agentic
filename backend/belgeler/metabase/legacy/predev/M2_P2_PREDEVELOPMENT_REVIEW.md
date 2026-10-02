# M2 / P2 — PRE-DEVELOPMENT REVIEW

**Milestone:** M2 / P2 — Metabase source/runtime pin policy + self-host lab bootstrap  
**Branch:** `feat/dima-metabase-platform`  
**M1 certified implementation:** `17942f179b13fd2cb81fd284789ba0f6366d2ed8`  
**M1 closure/status commit before M2 review:** `fc584361b57d0fc85758bafeb0644121a702d206`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY  
**Metabase source-audit SHA:** `74216b30981d8310c4cf724d63ca282e2e63529d`  
**Metabase runtime release:** UNSELECTED  
**Metabase runtime image digest:** UNSELECTED

Status: SEALED / RUNTIME RESEARCH AUTHORIZED

## 1. Normative sources re-read

Roadmap P2:
- self-host topology: `dima-api / metabase / metabase-app-db(Postgres) / analytics-db`;
- source-audit SHA is distinct from runtime release/image digest;
- private network;
- persistent Metabase application DB is a sensitive store;
- bootstrap/admin/test user/group/DB connection/backup-restore/health checks;
- runtime tests include startup, restart, persistence, query, permission denial,
  backup/restore, Agent API capability, raw-SQL policy and row/pagination observation;
- **no Dima product routing in P2**.

Architecture report reviewed:
- R3.23: process health != Agent API usability;
- R3.24: serialized query identity != pagination continuation != MCP handle;
- R3.25: row/page caps are runtime-observed capability, not hard-coded product facts;
- R3.26: Metabase app DB may contain derived analytical results and is sensitive;
- R4.3: tenant/principal mapping remains a later P0 proof;
- R4.6: pinned version + backup + migration rehearsal + rollback;
- R4.11: fast-moving Agent API/MCP behavior must be certified on exact runtime;
- R4.13: final connection ownership must be explicit.

## 2. Existing repository infrastructure inspected

Observed:
- root `docker-compose.yml` is the existing Dima dev stack and contains qdrant + dima backend;
- `backend/lab/docker-compose.yml` is an existing SQL Server restore lab and may contain real
  customer restore data under gitignored directories;
- neither existing compose file should be repurposed for M2;
- existing `backend/.env.example` is product configuration and is not an appropriate place
  for lab-only Metabase admin/app-DB secrets.

Decision:
M2 gets an isolated stack under `backend/lab/metabase/`.
No existing compose, v2, router, main, config, WrenAI or ask-v2 source file is modified.

## 3. Lab topology boundary

Target lab package:

```text
backend/lab/metabase/
  docker-compose.yml
  .env.example
  README.md
  init/
    analytics-db/
      001_schema.sql
  scripts/
    health.sh
    backup.sh
    restore-smoke.sh
    capability_probe.py
```

Logical services:

```text
metabase
metabase-app-db (PostgreSQL)
analytics-db     (PostgreSQL representative warehouse)
```

Dima backend is **not** wired to this stack in M2.
If network tests need a Dima-side caller, they are lab scripts/CI probes, not product imports.

## 4. Runtime pin protocol

Before compose implementation:
1. verify current official supported Metabase release from authoritative upstream;
2. choose an exact release tag — never `latest`;
3. resolve the exact multi-arch/platform image digest for the selected artifact;
4. record both in SOURCE_LOCK;
5. record source-audit SHA separately; do not pretend source master == runtime artifact;
6. runtime behavior is tested on the selected digest, not inferred from audited source.

No digest means no M2 implementation commit.

## 5. Security / persistence boundary

M2 rules:
- Metabase and both Postgres services share a dedicated private Docker network;
- host port exposure is lab-only and minimized;
- Metabase app DB volume is persistent;
- analytics DB volume is separate;
- secrets are environment-injected and examples contain placeholders/default lab-only values;
- app DB backup/restore is explicitly tested;
- no real customer data is committed;
- app DB backup is treated as sensitive analytical material;
- raw SQL capability is not silently assumed disabled: exact runtime settings/endpoints are probed.

## 6. Agent API boundary

P2 proves capability availability, not Dima semantic integration.

Must distinguish:
```text
process healthy
Agent API enabled
required endpoint/version present
auth/scopes usable
construct-query available
execute/query available
raw-SQL path disabled or unused
observed pagination/page/row behavior
```

A healthy Metabase with unusable Agent API is a typed M2 runtime capability failure, not a
semantic failure and not permission to fall back.

## 7. Files allowed to touch in M2

```text
backend/lab/metabase/**
.github/workflows/dima-metabase-m2.yml
backend/belgeler/metabase/predev/M2_P2_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/M2_P2_METABASE_LAB_BOOTSTRAP.md
backend/belgeler/metabase/DIMA_METABASE_SOURCE_LOCK.md  # runtime pin fields only
backend/belgeler/metabase/DIMA_METABASE_*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

## 8. Files forbidden in M2

```text
backend/app/v2/**
backend/app/v3/**                 # M2 is infrastructure lab, not client integration
backend/app/routers/**
backend/app/main.py
backend/app/config.py
docker-compose.yml                # existing root stack
backend/lab/docker-compose.yml    # existing SQL Server restore lab
WrenAI-main/**
feat/ask-v2-mvp
```

If any forbidden file becomes necessary: STOP, open Decision Receipt, re-read P2/P3 boundary.

## 9. M2 exit gate

```text
exact supported runtime release pinned
immutable image digest pinned
source-audit SHA remains distinct
isolated lab starts
restart preserves app DB
representative analytical query executes
permission-denial negative test observed
app DB backup + restore smoke passes
health check passes
Agent API capability handshake recorded
raw-SQL policy explicitly observed
row/pagination limits observed
Dima product routing = 0
v2/v3 product code changes = 0
source branch writes = 0
```

## 10. Authorization

This review authorizes **runtime research and isolated lab infrastructure only** after the review
commit governance is GREEN. It does not authorize P3 client code, P3A bridge work, semantic
mapping, Metabase primary routing or Wren retirement.
