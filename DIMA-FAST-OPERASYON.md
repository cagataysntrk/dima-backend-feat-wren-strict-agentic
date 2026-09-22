# DIMA FAST TRACK — OPERASYON

Status: NORMATIVE
Branch: `feat/dima-metabase-product-fast-track`

## 1. Absolute branch isolation

READ/WRITE:
- `feat/dima-metabase-product-fast-track`

READ-ONLY REFERENCES:
- `feat/dima-metabase-platform@352205f112fe735d8f80065c7d255d78905398b9`
- `feat/ask-v2-mvp@6d65600842731112f2362261a30660217cbde05d`

Forbidden:
- commits/writes to source branches;
- update_ref / force push to source branches;
- merge/rebase/cherry-pick from source branches;
- moving-HEAD synchronization;
- source-port without receipt.

Allowed:
1. read-only inspection;
2. re-derive inside Fast Track abstraction;
3. explicit port receipt when necessary;
4. Fast Track-owned re-test.

## 2. Normative reading order

1. `backend/belgeler/fast/DIMA_FAST_TRACK_ROADMAP.md`
2. `backend/belgeler/fast/DIMA_FAST_SOURCE_LOCK.md`
3. `DIMA-FAST-DURUM.md`
4. `DIMA-FAST-OPERASYON.md`
5. `DIMA-FAST-DENETIM.md`
6. active pre-development review
7. open failure/decision/live receipts
8. read-only source branches only when needed

Before frontend/product work also read:
- `predev/FT_UI_METABASE_WORKSPACE_RECONCILIATION.md`
- `receipts/decisions/FT_UI_001_WORKSPACE_RECONCILIATION_RECEIPT.md`

## 3. Ticket protocol

Every implementation ticket requires a predev review with:
- CURRENT_HEAD
- USER_SCENARIO
- CURRENT_OWNER
- TARGET_OWNER
- FILES_TO_TOUCH
- FILES_NOT_TO_TOUCH
- INVARIANTS
- BASELINE
- FAILURE_MODES
- FOCUSED_TESTS
- LIVE_SENTINEL
- EXIT_GATE
- ROLLBACK

No implementation before its predev commit.

## 4. Current sequencing rule

Backend:
`FT-001 -> FT-002/F0A -> FT-002B Gateway`

Product/UI blocker before FT-003:
`FT-UI-001 -> FT-UI-002 Dima-native rendering POC -> FT-003`

FT-003 may not start before FT-UI-002 is GREEN.

Metabase Collections/Questions/Query Builder/Search/native workspace are not Fast Track product goals.

## 5. Failure protocol

After RED, no phrase-specific patch.

Receipt first:
- FAILURE_ID
- OBSERVED_SHA
- TEST/RUN
- FAILURE_CLASS
- SINGLE_OWNER
- ROOT_CAUSE_EVIDENCE
- FORBIDDEN_PATCHES
- ALLOWED_FILES
- FOCUSED_PROOF
- FAMILY_PROOF

Failure classes include:
- MODEL_COGNITION
- RESOURCE_RESOLUTION
- TEMPORAL_BINDING
- QUERY_CONSTRUCTION
- QUERY_EXECUTION
- AUTH_PERMISSION
- CONVERSATION_STATE
- EVIDENCE_PROVENANCE
- ROOT_CAUSE_LOGIC
- ASSET_PERSISTENCE
- TRANSPORT_RUNTIME
- EVAL_ORACLE
- EMBED_CAPABILITY
- EMBED_AUTH
- CONTEXT_BRIDGE
- SDK_RUNTIME_COMPAT
- WORKSPACE_NAVIGATION
- RESPONSIVE_COMPOSITION

## 6. Commit discipline

Prefer:
- one ticket;
- one owner;
- one coherent change.

Do not mix:
- prompt;
- backend;
- UI;
- unrelated refactor;
- dependency upgrade;
- substrate upgrade.

UI architecture reconciliation and UI POC are separate commits/tickets.

## 7. Backend runtime boundary

Fast hot path:
`backend/app/fast/**`

Runtime imports forbidden:
- `app.wren_*`
- `app.v2.semantic_*`
- `app.v2.manager_*`
- `app.v3.semantic_spec`
- V3 semantic/compiler owners as runtime dependency

Read-only design study is allowed. Fast Track owns its own implementation.

## 8. UI/product boundary

Normative:
- Dima owns the complete user-facing analyst experience.
- Metabase remains hidden analytics/query/optional-rendering substrate.

Forbidden core dependencies:
- Metabase Collections UI;
- Questions browser;
- Query Builder;
- Metabase Search;
- generic BI navigation/workspace;
- native Metabase drill workspace;
- paid Metabase features;
- Metabase frontend source fork/patch;
- service/admin secret in browser.

Required:
- Dima product runs on Metabase OSS.
- charts/tables support the analysis; they are not the product destination.
- guest visualization, if used, is optional and server-signed.

## 9. Silent fallback prohibition

Metabase failure does not fall back to:
- Wren;
- V2;
- V3 semantic owner;
- hidden native SQL;
- custom Dima BI UI merely to hide an embed failure.

Return/classify the typed failure.

## 10. Native SQL

Default:
`DIMA_FAST_ALLOW_NATIVE_SQL=0`

Native SQL may not become a hidden repair path.

## 11. Session handoff

Always update `DIMA-FAST-DURUM.md` with:
- CURRENT_HEAD;
- CURRENT_BACKEND_GATE;
- CURRENT_PRODUCT_GATE;
- LAST_GREEN;
- OPEN_RED;
- OPEN_DEBT;
- NEXT_EXACT_ACTION;
- FILES_NEXT_ALLOWED;
- FILES_NEXT_FORBIDDEN.
