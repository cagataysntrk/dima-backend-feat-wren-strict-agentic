# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

PRE_SEAL_HEAD:
`9faa65eb8ac830285a55ce93940daf68da13f699`

CURRENT_PRODUCT_GATE:
`FT-004 — RUN LIFECYCLE / STREAMING / CANCEL`

FT-003_FINAL:
`CLOSED / GREEN`

FT-004:
`OPEN / PREDEVELOPMENT NEXT`

OPEN_RED:
`NONE`

TARGET:
`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

SELECTED_RENDERING:
`OPTION_A — Dima-native chart/table`

## FT-003 CERTIFIED RUNS

FT-003_CORE:
`GREEN`
run: `35776527074`
tested SHA: `f86475228074530a426542b9f5674ba12cbb7298`

FT-003_REAL_METABASE_LIVE:
`GREEN`
run: `35776518129`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`

FT-003_GATEWAY_REGRESSION:
`GREEN`
run: `35776518246`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`

FT-003_REAL_MODEL_RETRIEVAL:
`GREEN`
run: `35776518107`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`

FT-003_REAL_MODEL_E2E:
`GREEN`
run: `35776518184`
tested SHA: `2635ecc26f8093b67636ba581e705a4ed132be6f`
artifact digest:
`sha256:14c4ea5e455f15643c46538afaaabad17eef756c93842f9915f523cc94310c5a`

FT-003_BROWSER_REAL_FAST_ASK:
`GREEN`
run: `35777010348`
tested SHA: `9faa65eb8ac830285a55ce93940daf68da13f699`

FT-UI-002:
`SEALED / HISTORICAL / workflow_dispatch only`
freeze commit: `96cb65f2b05d8bc56e1dd86ced7b13b5c0f3fb3a`

## FT-003 PROVEN CHAIN

```text
Turkish question
-> real model bounded cognition
-> real Metabase metadata SEARCH
-> opaque Dima resource/field authority
-> deterministic temporal bounds
-> deterministic portable query
-> real Metabase construct/execute
-> independent DB equality
-> evidence
-> deterministic answer
-> Dima-native browser UI
```

Certified DB oracle:

```text
2026-08-09 <= order_date < 2026-09-08

COUNT = 20
SUM = 16270
East = 4085
North = 4015
South = 4050
West = 4120
```

Authority safety:
- ambiguous resources -> clarification before metadata read/query;
- construct = 0 on ambiguity;
- execute = 0 on ambiguity;
- unsupported AVG -> UNSUPPORTED before Gateway creation;
- invented IDs = 0 in final model diagnostic;
- raw SQL = 0;
- join = 0;
- Wren/V2/V3 runtime dependency = 0.

Browser:
- real `/fast/ask`;
- real pinned Metabase;
- loading PASS;
- COUNT PASS;
- SUM PASS;
- BREAKDOWN PASS;
- chart PASS;
- table PASS;
- clarification PASS;
- unsupported PASS;
- failed PASS;
- desktop 1440x900 PASS;
- mobile 390x844 PASS;
- scrollWidth = 390.

## CLOSED FAILURE FAMILIES

- FT_003_LIVE_SENTINEL_RED_001 -> EVAL_ORACLE -> CLOSED.
- FT_003_REAL_MODEL_SENTINEL_RED_001 -> retrieval/unsupported/ambiguity contract -> CLOSED.
- FT_003_MODEL_RETRIEVAL_RED_002 -> generic metadata retrieval contract -> CLOSED.
- FT_003_BROWSER_HYDRATION_RACE_001 -> E2E hydration timing oracle -> CLOSED.
- duplicate canonical resource candidate -> CLOSED by URI dedupe.
- invented field handle -> fail-closed regression sealed.

## OPEN DEBT / NOT FT-003 BLOCKERS

MULTI_CANDIDATE_RESOLUTION:
`CONSERVATIVE_CLARIFICATION`

CATALOG_FALLBACK:
`BOUNDED_SAFETY_FALLBACK`

The fallback is permission-filtered and bounded. It is not a translation or semantic dictionary.

Pilot-level broader model benchmark is still later roadmap work; the small FT-003 real-model certification is GREEN.

## CURRENT INVARIANTS

- writes only to Fast Track branch;
- source branches read-only;
- Wren/V2/V3 modification = forbidden;
- silent fallback = 0;
- raw SQL = 0;
- joins = 0 for FT-003;
- METABASE_LICENSE_BUDGET = 0;
- paid Metabase core dependency = 0;
- Metabase frontend fork = 0;
- browser Metabase service/admin secret = 0;
- Dima owns user-facing analyst UX;
- Metabase remains hidden OSS analytics substrate.

## NEXT_EXACT_ACTION

1. Open `FT_004_PREDEVELOPMENT_REVIEW.md`.
2. Add Dima-owned run lifecycle without changing FT-003 cognition/query semantics.
3. Target API:
   - `POST /fast/runs`
   - `GET /fast/runs/{id}`
   - `GET /fast/runs/{id}/events` via SSE
   - `POST /fast/runs/{id}/cancel`
4. Preserve `POST /fast/ask` as compatibility / simple quick adapter.
5. Enforce terminal exactly once.
6. Add cancellation, interruption, reconnect, retry lineage and duplicate-event handling.
7. Do not add new semantic logic, aggregation families, joins, Analyst, Root Cause or conversation semantics in FT-004.
