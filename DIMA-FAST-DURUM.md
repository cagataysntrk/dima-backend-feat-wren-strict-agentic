# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

CURRENT_HEAD_BASELINE:
`6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5`

CURRENT_BACKEND_GATE:
`FT-002B CLOSED / GREEN`

CURRENT_PRODUCT_GATE:
`FT-UI-002 — Metabase/Dima Workspace POC`

FRONTEND_PRODUCT_IMPLEMENTATION:
PAUSED

FT-003:
BLOCKED until FT-UI-002 GREEN

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

1. FT-UI-002 needs an embedding-capable exact runtime.
2. Matching exact Metabase SDK package/version must be pinned.
3. Current F0A OSS image proves Agent API, not authenticated embedding entitlement.
4. Full-app iframe does not provide the same typed host callback surface as modular SDK.
5. SameSite/cross-domain session behavior must be tested.
6. Metabase workspace + Dima sidecar responsive composition must be tested.
7. Modular SDK is client-side; Next.js SSR must not own SDK components.
8. Typed analytics context schema must be proven against supported callbacks before FT-003.

## NEXT_EXACT_ACTION

1. Create `backend/belgeler/fast/predev/FT_UI_002_WORKSPACE_POC_PREDEVELOPMENT_REVIEW.md`.
2. Record a separate UI POC source/capability lock:
   - exact embedding-capable Metabase runtime;
   - exact image digest;
   - exact matching SDK version;
   - auth mode;
   - origin/SameSite assumptions.
3. Execute UX-0 native Metabase baseline.
4. Execute workspace/frame + Dima sidecar POC.
5. Prove typed current-resource context.
6. Seal FT-UI-002 only if its hard gate is GREEN.
7. Only then open FT-003.

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
