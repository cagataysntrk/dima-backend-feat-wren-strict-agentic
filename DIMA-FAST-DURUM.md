# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_HEAD_BEFORE_RECONCILIATION: `3f9b3d705f481da3d5939e90d9938025434fde61`

CURRENT_BACKEND_GATE:
`FT-002B — Fast-owned Metabase Gateway`

CURRENT_PRODUCT_GATE:
`FT-UI-001 CLOSED -> FT-UI-002 Workspace POC required before FT-003`

BACKEND_STATUS:
PRESERVED / IN PROGRESS

FRONTEND_PRODUCT_IMPLEMENTATION:
PAUSED

NEW_BLOCKER_BEFORE_FT-003:
`FT-UI-002`

TARGET:
`Metabase-first Analytics Workspace + Dima Intelligence Experience`

## SEALED BASELINES

F0_GREEN_BASELINE:
`a7bf0ccac99fa757f06919d0a043fd24e134bba0`

F0A_TESTED_COMMIT:
`c8175ea2a05be79eeae7c61d8fb568c36fbe3773`

F0A_WORKFLOW_RUN:
`35761155049`

F0A_ARTIFACT_DIGEST:
`sha256:98f6f68402a426cb903d12bff4cb20095db88d7b3c4561ca6e893bef21e8947b`

PARENT_SNAPSHOT:
`352205f112fe735d8f80065c7d255d78905398b9`

LAST_GREEN:
Pinned Metabase F0A capability + restart + backup/restore.

## BACKEND COMPLETED

- F0 branch isolation sealed.
- F0A pinned Metabase live gate passed.
- unauthenticated Agent API denial verified.
- authenticated Agent API ping verified.
- search/read-resource verified.
- construct/execute/combined query verified.
- explicit pagination verified: 200 + 5.
- raw SQL disabled verified.
- restart persistence verified.
- app DB backup/restore verified.
- source branches remain read-only.

## FT-002B IN-PROGRESS STATE

Fast-owned Gateway files have been started under `backend/app/fast/**`.

Provider-free and live test files have been drafted.

They are NOT yet certified GREEN.

The Gateway CI workflow/live proof remains to be completed.

This pre-existing backend work is preserved by the UI architecture reconciliation.

## UI ARCHITECTURE RECONCILIATION

OLD:
`Existing Dima frontend = primary BI/product workspace`

NEW:
`Metabase-first Analytics Workspace + Dima Intelligence Experience`

Reason:
Current Dima shell contains valuable Dima-native interaction surfaces but duplicates mature Metabase dashboard/query/navigation/search/asset UX.

Normative path:
`native baseline -> workspace/frame -> Dima sidecar -> typed context bridge -> Dima research/decision -> selective modularization`

Full-app:
acceleration strategy only.

Modular Metabase surfaces:
strategic typed-context composition target.

## CURRENT INVARIANTS

- writes only to Fast Track branch;
- Wren/V2/V3 semantic hot-path dependency = 0;
- silent fallback = 0;
- native SQL default = OFF;
- Metabase frontend fork = 0;
- Metabase source patch for Dima UI = 0;
- browser service/admin secret = 0;
- DOM context scraping = 0;
- typed Metabase resource context required;
- Metabase AI is not Dima research owner;
- Dima evidence/decision state remains Dima-owned;
- external pilot before F9 = forbidden.

## OPEN DEBT / RISKS

1. FT-002B Gateway still needs CI + live certification.
2. FT-UI-002 needs an embedding-capable exact runtime and exact SDK pin.
3. Current F0A OSS image proves Agent API, not authenticated full-app/modular embedding.
4. Full-app iframe context bridge is insufficient as a permanent typed context strategy.
5. SameSite/cross-domain session behavior must be tested.
6. Responsive Metabase + Dima sidecar composition must be measured.
7. Modular SDK is client-side; Next.js SSR must not own SDK components.

## NEXT_EXACT_ACTION

Backend first, because it is already authorized and independent of UI POC:

1. finish `.github/workflows/dima-fast-ft002-gateway.yml`;
2. run provider-free Fast Gateway suite;
3. run Fast Gateway against pinned Metabase live lab;
4. seal FT-002B if GREEN.

Parallel/next product action:
5. open FT-UI-002 predev;
6. pin embedding-capable runtime + matching SDK;
7. execute workspace/context POC.

Do NOT begin FT-003 until FT-UI-002 is GREEN.

## FILES_NEXT_ALLOWED

Backend FT-002B:
- `backend/app/fast/metabase_*.py`
- `backend/app/fast/auth_context.py`
- `backend/tests/test_fast_metabase_gateway*.py`
- `.github/workflows/dima-fast-ft002-gateway.yml`
- `backend/belgeler/fast/**`

UI documentation/POC preparation:
- `backend/belgeler/fast/**`
- isolated UI POC files only after FT-UI-002 predev

## FILES_NEXT_FORBIDDEN

- source branch writes;
- `backend/app/v2/**`;
- V3 semantic/compiler mutation;
- Wren mutation;
- Metabase frontend source;
- FT-003 product implementation;
- production UI integration before FT-UI-002 GREEN.
