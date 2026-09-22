# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_GATE: F0A CLOSED — FT-002B Fast-owned Metabase Gateway
F0_GREEN_BASELINE: a7bf0ccac99fa757f06919d0a043fd24e134bba0
F0A_TESTED_COMMIT: c8175ea2a05be79eeae7c61d8fb568c36fbe3773
F0A_WORKFLOW_RUN: 35761155049
F0A_ARTIFACT_DIGEST: sha256:98f6f68402a426cb903d12bff4cb20095db88d7b3c4561ca6e893bef21e8947b
PARENT_SNAPSHOT: 352205f112fe735d8f80065c7d255d78905398b9
LAST_GREEN: pinned Metabase F0A live capability + restart + backup/restore
OPEN_RED: none
OPEN_DEBT: Fast-owned Gateway not yet implemented

## COMPLETED

- F0 branch isolation sealed.
- F0A exact pinned Metabase live gate passed.
- Agent API auth denial without session verified.
- Agent API authenticated ping verified.
- resource search verified.
- resource read verified.
- construct-query verified.
- execute verified.
- combined query verified.
- explicit pagination verified: 200 + 5 rows.
- raw SQL disabled verified.
- restart persistence verified.
- app DB backup and restore smoke verified.
- source branches remain read-only.

## CURRENT_INVARIANTS

- Writes only to Fast Track branch.
- Wren/V2/V3 semantic hot-path dependency = 0.
- Silent fallback = 0.
- Native SQL default = OFF.
- No user-language analytics until Fast-owned Gateway is green.
- External pilot before F9 = forbidden.

## NEXT_EXACT_ACTION

1. Read `backend/belgeler/fast/predev/FT_002B_GATEWAY_PREDEVELOPMENT_REVIEW.md`.
2. Implement Fast-owned typed Metabase Gateway under `backend/app/fast/**`.
3. Add provider-free tests.
4. Add real pinned-Metabase live test.
5. Seal FT-002B receipt.
6. Only then open FT-003 real Ask vertical slice.

## FILES_NEXT_ALLOWED

- backend/app/fast/metabase_*.py
- backend/app/fast/auth_context.py
- backend/tests/test_fast_metabase_gateway*.py
- .github/workflows/dima-fast-ft002-gateway.yml
- backend/belgeler/fast/**

## FILES_NEXT_FORBIDDEN

- backend/app/v2/**
- backend/app/v3 semantic/compiler owners
- app.fast runtime import of app.v3
- WrenAI-main/**
- legacy ask behavior
- source branch writes
