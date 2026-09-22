# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_GATE: F0 CLOSED — next F0A / FT-002
CURRENT_IMPLEMENTATION_BASELINE: 6569d0505565d0917b9f4c032ad2f7366f540f23
LATEST_ISOLATION_RECEIPT_COMMIT: db79e05db9a1859a643629cac727c096ee476141
PARENT_SNAPSHOT: 352205f112fe735d8f80065c7d255d78905398b9
LAST_GREEN: F0 isolated governance/bootstrap
OPEN_RED: none
OPEN_DEBT: F0A pinned Metabase capability preflight has not yet been re-certified inside Fast Track

## COMPLETED

- New Fast Track branch created from exact SHA, not moving HEAD.
- Branch-local source lock created.
- Dima+Metabase and Ask-v2 branches declared read-only references.
- merge/rebase/cherry-pick source synchronization forbidden.
- Branch-local roadmap, operations, status and audit docs created.
- FT-001 pre-development review created and closed.
- Branch-isolation receipt sealed.
- `backend/app/fast` namespace created EMPTY BY DESIGN.
- Functional analytics intentionally not started.
- Source branches were re-read after bootstrap; no Fast Track write targeted them.

## OBSERVED READ-ONLY SOURCE HEADS AT F0 VERIFICATION

Pinned snapshots remain authoritative inputs:
- Dima+Metabase reference snapshot: `352205f112fe735d8f80065c7d255d78905398b9`
- Ask-v2 reference snapshot: `6d65600842731112f2362261a30660217cbde05d`

Moving branch heads observed later:
- feat/dima-metabase-platform: `94e9b3da892a80253495324b2a256f128b037d1b`
- feat/ask-v2-mvp: `875c446476b6ae4907f5cac5d1c7b512e5157538`

These are READ-ONLY observations and are not inherited automatically.

## CURRENT_INVARIANTS

- Writes only to Fast Track branch.
- Wren/V2/V3 semantic hot-path dependency = 0.
- Silent fallback = 0.
- Native SQL default = OFF.
- Functional analytics before F0A = forbidden.
- External pilot before F9 security = forbidden.
- Source branch moving HEAD sync = forbidden.

## NEXT_EXACT_ACTION

1. Open `backend/belgeler/fast/predev/FT_002_PREDEVELOPMENT_REVIEW.md`.
2. Re-probe pinned Metabase v0.63.18 from Fast Track.
3. Record branch-local F0A live receipt.
4. Only if F0A is green, build Fast-owned Metabase Gateway.
5. Do not implement Ask/Analyst/Root-Cause before the gateway/capability gate closes.

## FILES_NEXT_ALLOWED

- backend/belgeler/fast/**
- backend/app/fast/**
- Fast Track tests
- minimal Fast-specific lab/config files after FT-002 predev review

## FILES_NEXT_FORBIDDEN

- app.wren_*
- backend/app/v2/**
- backend/app/v3 semantic/compiler owners
- feat/dima-metabase-platform writes
- feat/ask-v2-mvp writes
- legacy ask behavior changes
