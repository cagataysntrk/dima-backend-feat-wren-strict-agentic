# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_BACKEND_GATE:
`FT-002B CLOSED / GREEN`

CURRENT_PRODUCT_GATE:
`FT-003 — First Real Dima Ask Vertical Slice`

FT-UI-002:
`CLOSED / GREEN`

FT-003:
`OPEN`

TARGET:
`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

SELECTED_RENDERING:
`OPTION_A — Dima-native chart/table`

## SEALED BASELINES

F0_GREEN_BASELINE:
`a7bf0ccac99fa757f06919d0a043fd24e134bba0`

F0A_TESTED_COMMIT:
`c8175ea2a05be79eeae7c61d8fb568c36fbe3773`

FT-002B_TESTED_COMMIT:
`6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5`

FT-002B_WORKFLOW_RUN:
`35763124599`

FT-UI-002_TESTED_COMMIT:
`3f4a34356d7b32a78c3c18f1c96a1879253001a2`

FT-UI-002_WORKFLOW_RUN:
`35768067813`

FT-UI-002_ARTIFACT_DIGEST:
`sha256:2ecaec2ad248f5d22d12503fa3dad3dab46539b85f3999b7b404f556a03780b3`

PARENT_SNAPSHOT:
`352205f112fe735d8f80065c7d255d78905398b9`

LAST_GREEN:
Dima-native rendering POC over real pinned Metabase result.

## COMPLETED

- F0 branch isolation.
- F0A pinned OSS Metabase substrate.
- FT-002B Fast-owned typed Gateway.
- Dima-native product boundary reconciliation.
- zero-license core invariant.
- real Metabase result fixture proof.
- Dima-native chart rendering.
- Dima-native table rendering.
- safe table fallback.
- Next production build.
- protected-route browser proof.
- 390px responsive proof.
- guest embed feasibility evaluated.
- rendering strategy selected: Option A.
- no generic Metabase workspace dependency.
- no paid Metabase dependency.

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
- Metabase frontend fork/source patch = 0;
- browser service/admin secret = 0;
- Metabase AI is not Dima research owner;
- Dima owns user-facing analyst UX.

## OPEN DEBT / RISKS

1. FT-003 must bind a real user question to bounded resource candidates.
2. Temporal intent must be typed and date arithmetic deterministic.
3. No model may invent Metabase resource identity.
4. User-visible numeric claims require evidence.
5. Guest embed remains optional only; do not promote it without a measured visualization gap.

## NEXT_EXACT_ACTION

1. Open `backend/belgeler/fast/predev/FT_003_PREDEVELOPMENT_REVIEW.md`.
2. Implement a bounded first Ask family end-to-end:
   question -> candidates -> temporal -> construct -> execute -> evidence -> answer -> Option-A rendering.
3. Use the existing Fast Gateway as transport authority.
4. Do not implement Analyst loop or Root Cause yet.
5. Seal FT-003 only with real pinned-Metabase + frontend proof.

## FILES_NEXT_ALLOWED

After FT-003 predev:
- new Fast Ask/orchestration files under `backend/app/fast/**`;
- Fast route/schema files;
- focused Fast tests/workflow;
- isolated `src/app/fast-poc/**` and `src/features/fast-poc/**` evolution;
- minimal shared router registration only if predev explicitly authorizes it;
- `backend/belgeler/fast/**`.

## FILES_NEXT_FORBIDDEN

- source branch writes;
- V2/V3/Wren modification;
- legacy Ask behavior modification;
- generic Metabase Collections/Questions/Search/Query Builder UI;
- paid Metabase embedding dependency;
- main frontend migration before FT-003 vertical slice is proven.
