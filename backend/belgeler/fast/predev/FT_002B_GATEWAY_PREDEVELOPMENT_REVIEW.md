# FT-002B — FAST-OWNED METABASE GATEWAY PRE-DEVELOPMENT REVIEW

Status: CLOSED / GREEN
Prerequisite: F0A GREEN
F0A run: 35761155049
Gateway certification run: 35763124599
Gateway tested commit: 6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5

## Goal

Create a Fast Track-owned typed Metabase transport boundary.

This is transport/infrastructure only.

It MUST NOT interpret raw user language, choose business meaning, build Dima semantics, author SQL, or call Wren/V2/V3.

## Architecture

```text
future Fast orchestrator
  -> FastMetabaseGateway
      -> Metabase Agent API
          -> customer analytics DB
```

Gateway owns:
- auth header injection
- timeouts
- typed upstream errors
- safe telemetry
- search
- read-resource
- construct query
- execute
- combined query
- continuation
- pinned runtime handshake

Gateway does NOT own:
- semantic resource selection
- temporal intent
- root cause
- conversation
- report/decision
- asset mutation in this ticket
- password login
- tenant mapping policy

## Implemented files

- backend/app/fast/metabase_errors.py
- backend/app/fast/metabase_models.py
- backend/app/fast/metabase_telemetry.py
- backend/app/fast/metabase_gateway.py
- backend/app/fast/auth_context.py
- backend/tests/test_fast_metabase_gateway.py
- backend/tests/test_fast_metabase_gateway_live.py
- backend/tests/test_fast_boundary_static.py
- .github/workflows/dima-fast-ft002-gateway.yml

## Files not touched

- backend/app/v3/substrate/metabase/**
- backend/app/v2/**
- WrenAI-main/**
- legacy routers
- backend/app/main.py
- backend/app/config.py
- source branches

## Verified invariants

- [x] raw SQL method absent
- [x] admin/content mutation methods absent
- [x] no user-language input method
- [x] no semantic handle minting
- [x] continuation != serialized query
- [x] non-JSON upstream response -> typed contract error
- [x] 202 failed body != success
- [x] page row_count > pinned page size -> reject
- [x] secret excluded from repr/fingerprint
- [x] missing principal cannot silently become admin
- [x] no app.v3 import
- [x] no app.v2 import
- [x] no Wren import

## Certification evidence

Static boundary:
`3 passed in 7.97s`

Provider-free Gateway:
`21 passed in 8.07s`

Live pinned Metabase:
`1 passed in 9.25s`

Live path verified:
- session login outside Gateway
- search orders
- inspect database resource
- construct portable query
- execute
- query 205 rows
- first page 200
- explicit continuation
- second page 5
- raw SQL method absent
- handshake ready

## Exit

FT-002B = GREEN / CLOSED.

The old statement “Then FT-003 may begin” is superseded by the later UI architecture reconciliation.

Current normative next product gate:
`FT-UI-002 — Metabase/Dima Workspace POC`

FT-003 remains blocked until FT-UI-002 is GREEN.

## Rollback

If Gateway later regresses, revert only Fast Track Gateway/test/workflow commits.
Never modify source branches.
