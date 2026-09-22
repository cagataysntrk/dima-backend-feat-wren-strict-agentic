# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

OBSERVED_BRANCH_HEAD:
`96cb65f2b05d8bc56e1dd86ced7b13b5c0f3fb3a`

CURRENT_PRODUCT_GATE:
`FT-003 — OPEN / FINAL MODEL E2E PENDING`

FT-003_CORE:
`GREEN`
run: `35775125103`
tested SHA: `1adc55467a02363db9a1fb76c09615a568696c35`

FT-003_REAL_METABASE_LIVE:
`GREEN`
run: `35775124979`
tested SHA: `1adc55467a02363db9a1fb76c09615a568696c35`

FT-003_BROWSER_REAL_FAST_ASK:
`GREEN`
run: `35775350763`
tested SHA: `11bd33a697ae91bb3dec611d0714c5dd6236bb79`

FT-003_GATEWAY_REGRESSION:
`GREEN`
run: `35775125074`
tested SHA: `1adc55467a02363db9a1fb76c09615a568696c35`

FT-003_REAL_MODEL_DIAGNOSTIC:
`GREEN`
run: `35775125029`
tested SHA: `1adc55467a02363db9a1fb76c09615a568696c35`

FT-UI-002:
`SEALED / MANUAL HISTORICAL GATE`
freeze commit: `96cb65f2b05d8bc56e1dd86ced7b13b5c0f3fb3a`

FT-003_FINAL:
`OPEN`

OPEN_RED:
`NONE CURRENTLY`

OPEN_BLOCKER:
`REAL_MODEL_PRIMARY_E2E_NOT_YET_CERTIFIED`

## WHAT IS ALREADY PROVEN

- deterministic Ask core;
- Fast-only application;
- auth negative/positive path;
- opaque resource authority;
- opaque field authority;
- deterministic temporal binding;
- deterministic portable query construction;
- real pinned Metabase execution;
- independent DB equality for COUNT/SUM/BREAKDOWN;
- evidence/query/access/result fingerprints;
- raw SQL = 0;
- joins = 0 for FT-003;
- Wren/V2/V3 runtime dependency = 0;
- duplicate canonical resource URI dedupe;
- unknown field handle fail-closed before construct;
- multi-resource ambiguity fail-closed at service authority;
- typed UNSUPPORTED before query work;
- isolated /fast-poc over real /fast/ask;
- desktop/mobile browser proof;
- loading/clarification/unsupported/failure UI states;
- old FT-UI-002 workflow frozen to workflow_dispatch only;
- small real-model structured cognition diagnostic GREEN;
- invented model IDs observed = 0 in the GREEN diagnostic.

## IMPORTANT REMAINING DISTINCTION

The current real-model sentinel proves:

```text
REAL MODEL
-> typed cognition
-> real Metabase metadata discovery
-> opaque resource/field selection diagnostics
```

It explicitly does NOT yet prove:

```text
REAL MODEL
-> FastAskService
-> real Metabase construct/execute
-> independent DB oracle equality
-> deterministic answer/evidence
```

Therefore FT-003 is not sealed yet.

## RETRIEVAL STATUS

The latest GREEN model diagnostic still shows many Turkish cases with:

```text
direct_search_hit = false
retrieval_mode = CATALOG_FALLBACK
```

The bounded catalog fallback is safe and remains allowed, but it must not substitute for the intended generic metadata-discovery contract.

The draft prompt must still be tightened generically so `search_terms` means:
- primary business/data entity lookup terms;
- user-language entity terminology where useful;
- likely English metadata equivalents when schema language may differ;
- no measure/dimension pollution unless required to distinguish the table;
- maximum four terms.

No translation dictionary / phrase patch / regex glossary is allowed.

## CONSERVATIVE DEBT

MULTI_CANDIDATE_RESOLUTION:
`CONSERVATIVE_CLARIFICATION`

For FT-003, more than one remaining permitted resource candidate is clarification-required even if the model guesses one.

This is intentional safety, not a current blocker.

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

1. Tighten Fast Ask `search_terms` prompt semantics generically; no phrase map.
2. Extend model receipt with search terms, candidate count/names/URIs, selected handle.
3. Make ambiguity/unsupported hard certification service-authority-level; cognition abstention remains diagnostic only.
4. Add provider-free regression tests for the retrieval prompt/authority contract.
5. Add three-prompt primary real-model E2E:
   - COUNT last 30 days;
   - SUM last 30 days;
   - SUM by region last 30 days.
6. Run those through real `FastAskService` + real pinned Metabase.
7. Compare all results against independent DB oracle:
   - COUNT = 20
   - SUM = 16270
   - East = 4085
   - North = 4015
   - South = 4050
   - West = 4120
8. Recheck core/live/browser/gateway/model gates.
9. Seal FT-003 only after primary real-model E2E is GREEN.
10. Then open FT-004 pre-development review immediately.

## DO NOT START YET

- FT-004 implementation before FT-003 seal;
- Analyst;
- Research manager;
- Root Cause;
- AVG/MIN/MAX;
- arbitrary filters;
- joins;
- multi-table execution;
- ontology/synonym/translation system;
- main frontend migration;
- UI redesign.
