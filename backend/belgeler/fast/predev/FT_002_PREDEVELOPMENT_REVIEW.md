# FT-002 — PRE-DEVELOPMENT REVIEW

Status: APPROVED TO IMPLEMENT F0A PROBE ONLY
Ticket: FT-002
Branch: feat/dima-metabase-product-fast-track
Observed Fast HEAD before this review: a7bf0ccac99fa757f06919d0a043fd24e134bba0

## Goal

Re-certify the exact pinned Metabase substrate from the Fast Track branch before any functional analytics code is written.

Then, only after F0A is GREEN, prepare a Fast-owned Metabase Gateway boundary.

## User scenario

A developer must be able to prove:

1. pinned Metabase actually boots;
2. Agent API is enabled;
3. unauthenticated Agent API access is denied;
4. authenticated search/read-resource works;
5. portable query construct works;
6. query execute works;
7. combined query works;
8. pagination is explicit and bounded;
9. native/raw SQL is disabled;
10. Metabase app DB survives restart and can be backed up/restored.

No Dima user question or LLM behavior is part of F0A.

## Source-lock

Fast parent:
352205f112fe735d8f80065c7d255d78905398b9

Pinned Metabase:
- version: v0.63.18
- image: metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73

Pinned Postgres:
- 17.11
- postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675

Read-only source references remain unchanged.

## Existing inherited lab evidence inspected

Fast branch already contains, inherited from the immutable parent snapshot:

- backend/lab/metabase/docker-compose.yml
- backend/lab/metabase/.env.example
- backend/lab/metabase/scripts/bootstrap.py
- backend/lab/metabase/scripts/capability_probe.py
- backend/lab/metabase/scripts/health.sh
- backend/lab/metabase/scripts/backup.sh
- backend/lab/metabase/scripts/restore-smoke.sh

The existing capability probe checks:
- process health
- unauthenticated denial
- Agent API ping
- search
- read-resource
- construct-query
- execute
- combined query
- continuation/pagination
- raw SQL disabled

The lab is NOT product code.

## Current owner

Pinned isolated Metabase lab:
backend/lab/metabase/**

## Target owner after F0A

Transport/product integration will later belong to:
backend/app/fast/metabase_*.py

F0A itself must NOT create an app.fast -> app.v3 dependency.

## Files to touch for F0A

Allowed:
- .github/workflows/dima-fast-f0a.yml
- backend/belgeler/fast/**
- DIMA-FAST-DURUM.md
- Fast-specific tests/docs if needed

Do not modify the inherited lab unless the live probe exposes a real lab defect and a failure receipt authorizes it.

## Files not to touch

Forbidden:
- backend/app/v2/**
- backend/app/v3 semantic/compiler owners
- WrenAI-main/**
- legacy ask routers/behavior
- feat/dima-metabase-platform branch
- feat/ask-v2-mvp branch

Functional Fast Ask/Analyst/Root-Cause code is also forbidden until F0A closes.

## Invariants

- Source branch writes = 0
- Metabase image tag latest = 0
- Raw SQL enabled = 0
- Browser/admin product secret work = 0
- LLM calls = 0
- Functional analytics = 0
- app.fast runtime dependency on app.v3 = 0
- Live proof uses exact pinned container digest

## Failure modes

Classify before patching:
- PIN_DRIFT
- DOCKER_BOOT_FAILURE
- METABASE_HEALTH_FAILURE
- AGENT_API_DISABLED
- AUTH_FAILURE
- SEARCH_FAILURE
- RESOURCE_READ_FAILURE
- CONSTRUCT_QUERY_FAILURE
- EXECUTION_FAILURE
- PAGINATION_FAILURE
- RAW_SQL_POLICY_FAILURE
- APP_DB_PERSISTENCE_FAILURE
- BACKUP_RESTORE_FAILURE
- CI_RUNTIME_FAILURE

Any failure gets a receipt before changing code.

## Focused proof

Static:
- workflow branch filter is Fast Track only
- exact digests visible in compose
- no :latest
- workflow calls inherited pinned lab
- source branches not targeted

## Live proof

GitHub Actions on Fast Track must execute:
1. compose config
2. docker compose up
3. health
4. bootstrap
5. capability probe
6. Metabase restart
7. second capability probe
8. app DB backup
9. restore smoke
10. teardown

Capability JSON must be uploaded as a workflow artifact.

## Exit gate F0A

GREEN only if all required live probe fields are true, page size <= 200, continuation is observed, raw SQL is denied, restart probe passes, and backup/restore smoke passes.

If workflow cannot execute because of CI/platform infrastructure, F0A remains OPEN; do not infer GREEN from inherited evidence.

## Rollback

Delete/revert only Fast Track workflow/docs commits.
Never alter source branches.

## Next after F0A

Open a separate implementation step inside FT-002 for the Fast-owned Metabase Gateway:
- errors
- models
- telemetry
- transport
- auth context inputs

No user-language interpretation yet.
