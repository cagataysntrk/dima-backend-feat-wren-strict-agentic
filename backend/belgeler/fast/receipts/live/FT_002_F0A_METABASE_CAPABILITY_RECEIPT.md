# FT-002 F0A — PINNED METABASE CAPABILITY LIVE RECEIPT

Status: GREEN / SEALED
Date: 2026-09-22

## Authority

Branch:
`feat/dima-metabase-product-fast-track`

Workflow:
`.github/workflows/dima-fast-f0a.yml`

Workflow run:
`35761155049`

Tested commit:
`c8175ea2a05be79eeae7c61d8fb568c36fbe3773`

Artifact:
`dima-fast-f0a-capability-c8175ea2a05be79eeae7c61d8fb568c36fbe3773`

Artifact digest:
`sha256:98f6f68402a426cb903d12bff4cb20095db88d7b3c4561ca6e893bef21e8947b`

## Exact runtime

Metabase:
- v0.63.18
- metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73

Postgres:
- 17.11
- postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675

## Live observations — first probe

- process_health = true
- unauthenticated_agent_denied = true
- agent_api_ping = true
- search = true
- read_resource = true
- construct_query = true
- execute_query = true
- combined_query = true
- continuation_observed = true
- raw_sql_disabled = true
- observed_page_rows = 200
- observed_second_page_rows = 5
- metabase_runtime = v0.63.18

## Restart proof

After restarting Metabase, the same required capability fields were GREEN again.

Observed again:
- page rows = 200
- second page rows = 5
- raw SQL disabled = true
- search/read/construct/execute/query = true

## Persistence proof

- app DB backup: PASS
- restore smoke: PASS
- restored public tables observed: 176

## Isolation proof

Before lab execution the workflow verified:
- Fast Track branch name
- immutable runtime pins
- source lineage from the pinned parent snapshot

No source branch write occurred.

## Scope statement

This receipt proves only the Fast Track F0A substrate gate.

It does NOT prove:
- Dima natural-language resource selection
- conversation correctness
- root-cause quality
- multi-tenant security
- production readiness

## Decision

F0A = CLOSED / GREEN.

Functional Fast Track transport integration may begin.

Next:
FT-002B — Fast-owned Metabase Gateway.

Still forbidden:
- Ask
- Analyst
- Root Cause
until the Gateway contract and its own live proof are green.
