# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_HEAD_BASELINE:
`6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5`

CURRENT_BACKEND_GATE:
`FT-002B CLOSED / GREEN`

CURRENT_PRODUCT_GATE:
`FT-UI-002 — Dima-native rendering/composition POC`

FRONTEND_PRODUCT_IMPLEMENTATION:
PAUSED

FT-003:
BLOCKED until FT-UI-002 GREEN


TARGET:
`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

## SEALED BASELINES

F0_GREEN_BASELINE:
`a7bf0ccac99fa757f06919d0a043fd24e134bba0`

F0A_TESTED_COMMIT:
`c8175ea2a05be79eeae7c61d8fb568c36fbe3773`

F0A_INITIAL_RUN:
`35761155049`

F0A_RECONCILIATION_RECERT_RUN:
`35763007067`

F0A_ARTIFACT_DIGEST:
`sha256:98f6f68402a426cb903d12bff4cb20095db88d7b3c4561ca6e893bef21e8947b`

FT-002B_TESTED_COMMIT:
`6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5`

FT-002B_WORKFLOW_RUN:
`35763124599`

PARENT_SNAPSHOT:
`352205f112fe735d8f80065c7d255d78905398b9`

LAST_GREEN:
Fast-owned Metabase Gateway — static + provider-free + real pinned-Metabase live proof.

## BACKEND COMPLETED

- F0 branch isolation sealed.
- F0A pinned Metabase capability sealed.
- F0A re-certification after UI documentation reconciliation passed.
- Fast-owned auth/access-fingerprint contract implemented.
- Fast-owned typed Metabase error taxonomy implemented.
- Fast-owned transport/models/telemetry implemented.
- Fast-owned Metabase Gateway implemented.
- provider-free Gateway suite: 21 passed.
- static boundary suite: 3 passed.
- live pinned-Metabase Gateway suite: 1 passed.
- real pagination: 200 + continuation + 5.
- no V2/V3/Wren runtime import.
- no raw SQL/admin method on Gateway.
- source branches remain read-only.

## UI ARCHITECTURE

FT-UI-001:
CLOSED / GREEN.

SUPERSEDED:
`Metabase-first Analytics Workspace + Dima Intelligence Experience`

NORMATIVE:
`Dima-native Intelligence Workspace on hidden Metabase analytics substrate`

Metabase Collections/Questions/Query Builder/Search/native workspace are NOT Dima product requirements.

## CURRENT INVARIANTS

- writes only to Fast Track branch;
- Wren/V2/V3 semantic hot-path dependency = 0;
- silent fallback = 0;
- native SQL default = OFF;
- METABASE_LICENSE_BUDGET = 0;
- paid Metabase feature required for core product = 0;
- full-app embed required = 0;
- modular SDK required in production = 0;
- native Metabase workspace required for user = 0;
- Dima product must run on Metabase OSS;
- Metabase frontend fork = 0;
- Metabase source patch for Dima UI = 0;
- browser service/admin secret = 0;
- Metabase AI is not Dima research owner;
- Dima evidence/decision state remains Dima-owned;
- external pilot before F9 = forbidden.

## OPEN DEBT / RISKS

1. FT-UI-002 must prove the simplest rendering path against real Metabase result shape.
2. Guest visualization is OSS-compatible but view-only and must remain optional.
3. Guest JWT signing secret must remain server-side.
4. Existing legacy dashboard/navigation UI must not become the Fast Track product shell.
5. FT-003 remains the first real end-to-end Ask product flow.

## NEXT_EXACT_ACTION

1. Commit this scope correction.
2. Generate/seal a sanitized real Metabase result fixture from the pinned Gateway/lab path.
3. Build isolated `/fast-poc` analyst shell.
4. Prove native table + simple chart + safe fallback.
5. Evaluate OSS guest visualization as optional, not required.
6. Select A / B / C rendering strategy.
7. Seal FT-UI-002.
8. Immediately open FT-003 predev and continue to first real Ask vertical slice.

## FILES_NEXT_ALLOWED

Until FT-UI-002 predev is committed:
- `backend/belgeler/fast/**`

- `dima-frontend-demo-master/src/app/fast-poc/**`
- `dima-frontend-demo-master/src/features/fast-poc/**`
- focused Fast POC fixture/tests/workflow
- `backend/belgeler/fast/**`
- no production UI migration.

## FILES_NEXT_FORBIDDEN

- source branch writes;
- `backend/app/v2/**`;
- V3 semantic/compiler mutation;
- Wren mutation;
- Metabase frontend source;
- Metabase internal React patch;
- FT-003 implementation before FT-UI-002 GREEN;
- generic Metabase Collections/Questions/Search/Query Builder product UI;
- paid Metabase embedding dependency;
- production frontend migration before FT-UI-002 GREEN.
