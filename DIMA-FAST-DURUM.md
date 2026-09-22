# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_HEAD_BASELINE:
`6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5`

CURRENT_BACKEND_GATE:
`FT-002B CLOSED / GREEN`

CURRENT_PRODUCT_GATE:
`FT-UI-002 / POC-A — Local Modular Workspace + Context Bridge POC`

FRONTEND_PRODUCT_IMPLEMENTATION:
PAUSED

FT-003:
BLOCKED until FT-UI-002 / POC-A GREEN

PRODUCTION EMBEDDING:
`FT-UI-002 / POC-B` required before external pilot / F9

TARGET:
`Metabase-first Analytics Workspace + Dima Intelligence Experience`

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

OLD:
`Existing Dima frontend = primary BI/product workspace`

NEW:
`Metabase-first Analytics Workspace + Dima Intelligence Experience`

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
- Dima backend must run without embed;
- external pilot before F9 = forbidden.

## OPEN DEBT / RISKS

1. POC-A must empirically determine whether the existing pinned major-63 runtime exposes enough modular capability for local evaluation.
2. SDK `63-stable` resolves to exact package `0.63.1`; lockfile integrity still must be sealed in functional POC commit.
3. Current F0A runtime remains immutable even if modular capability is absent.
4. Production authenticated embedding remains UNQUALIFIED and belongs to POC-B before F9.
5. Full-app postMessage/location may be tested as fallback; iframe DOM scraping remains forbidden.
6. SameSite/cross-domain production session behavior belongs to POC-B.
7. Metabase workspace + Dima sidecar responsive composition must be tested in POC-A.
8. Modular SDK is client-side; Next.js SSR must not own SDK components.
9. Typed analytics context schema must be proven against real callbacks before FT-003.

## NEXT_EXACT_ACTION

1. Commit FT-UI-002 POC-A predev + capability-lock skeleton + roadmap nuance.
2. Keep F0A runtime/image pin unchanged.
3. Pin SDK exact version `0.63.1` and capture lockfile integrity in the functional POC commit.
4. Build only isolated `/fast-poc` + `src/features/fast-poc/**`.
5. Execute UX-0 native Metabase baseline.
6. Prove Collection Browser + Dashboard + Question/query surface.
7. Capture at least three real typed context event families and normalize `AnalyticsContext`.
8. Select Model C / Hybrid / B by the automatic decision rule.
9. If POC-A GREEN, immediately open FT-003 predev.
10. Complete POC-B production embedding qualification before F9.

## FILES_NEXT_ALLOWED

Until FT-UI-002 predev is committed:
- `backend/belgeler/fast/**`

After FT-UI-002 predev:
- isolated UI POC files explicitly listed by that review;
- no production UI migration.

## FILES_NEXT_FORBIDDEN

- source branch writes;
- `backend/app/v2/**`;
- V3 semantic/compiler mutation;
- Wren mutation;
- Metabase frontend source;
- Metabase internal React patch;
- FT-003 implementation;
- production frontend migration before FT-UI-002 GREEN.
