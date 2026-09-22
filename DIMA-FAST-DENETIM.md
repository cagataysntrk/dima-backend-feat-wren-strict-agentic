# DIMA FAST TRACK — DENETİM

Status: NORMATIVE AUDIT CHECKLIST

## A. Branch safety

- [x] Fast Track exact SHA'dan açıldı.
- [x] source branches read-only.
- [x] merge/rebase/cherry-pick source sync forbidden.
- [x] source-lock exists.
- [x] F0 branch-isolation receipt sealed.

## B. Backend foundation

- [x] F0A pinned Metabase OSS live.
- [x] Agent API search/read/construct/execute/query live.
- [x] pagination 200 + continuation.
- [x] raw SQL disabled.
- [x] FT-002B Fast-owned Gateway.
- [x] no V2/V3/Wren runtime import.

## C. Product boundary

- [x] Dima owns complete user-facing product.
- [x] Metabase hidden analytics/query/optional-rendering substrate.
- [x] zero-license core invariant.
- [x] no generic Metabase workspace.
- [x] no paid embedding dependency.
- [x] no Metabase frontend fork/source patch.
- [x] no browser Metabase service/admin secret.

## D. FT-UI-002

- [x] Dima-native analyst shell.
- [x] real Metabase result rendering.
- [x] chart/table.
- [x] responsive proof.
- [x] Option A selected.
- [x] historical workflow frozen to manual dispatch.

## E. FT-003 First Real Ask

- [x] deterministic core.
- [x] Fast-only application.
- [x] auth negative/positive.
- [x] opaque resource handles.
- [x] opaque field handles.
- [x] duplicate canonical URI dedupe.
- [x] unknown field handle fail-closed.
- [x] deterministic temporal authority.
- [x] deterministic portable query builder.
- [x] evidence/query/access/result fingerprints.
- [x] real Metabase COUNT.
- [x] real Metabase SUM.
- [x] real Metabase BREAKDOWN.
- [x] independent DB oracle equality.
- [x] generic entity-centric cross-language metadata retrieval.
- [x] direct SEARCH hit across supported model diagnostic corpus.
- [x] no phrase dictionary/regex translation patch.
- [x] real model primary E2E.
- [x] ambiguity blocked by service authority.
- [x] ambiguity construct = 0.
- [x] ambiguity execute = 0.
- [x] unsupported AVG -> UNSUPPORTED before Gateway.
- [x] invented IDs = 0 in final model diagnostic.
- [x] raw SQL = 0.
- [x] join = 0.
- [x] Wren/V2/V3 runtime dependency = 0.
- [x] browser real /fast/ask.
- [x] loading state.
- [x] chart/table.
- [x] clarification/unsupported/failed states.
- [x] desktop.
- [x] mobile.
- [x] failure receipts closed.
- [x] living status reconciled.
- [x] FT-003 final receipt sealed.

## F. Stop-the-line

- source branch write;
- cross-tenant leak;
- permission bypass;
- numeric claim outside tool result;
- invented resource ID;
- material ambiguity silent auto-pick;
- hidden native SQL fallback;
- unbounded loop;
- missing principal -> admin/service authority;
- browser service secret;
- paid capability enters core critical path.

## G. Release progression

```text
F0        governance                         GREEN
F0A       pinned Metabase OSS                GREEN
FT-002B   Fast-owned Gateway                 GREEN
FT-UI-002 Dima-native rendering              GREEN / SEALED
FT-003     First Real Ask                     GREEN / CLOSED
FT-004     run lifecycle / streaming / cancel GREEN / CLOSED
FT-005     conversation + follow-up context       OPEN
FT-006     evidence expansion
FT-007     Analyst
FT-008     Root Cause
FT-009     optional analytical assets
FT-010     decision
FT-011     report
FT-012     polish
FT-013     pilot security
FT-014     benchmark / failure injection
```

## H. Audit seal

BRANCH_ISOLATION: GREEN
METABASE_OSS_SUBSTRATE: GREEN
FAST_GATEWAY: GREEN
UI_RENDERING_POC: GREEN / SEALED
FT_003: GREEN / CLOSED
FT_004: GREEN / CLOSED
FT_005: OPEN
PRODUCTION: NOT CERTIFIED


## I. FT-004 Run Lifecycle / Streaming / Cancel

- [x] typed run models.
- [x] canonical transition table.
- [x] Dima-owned FastRunStore.
- [x] Dima-owned FastRunManager.
- [x] bounded ThreadPoolExecutor.
- [x] owner authorization.
- [x] foreign principal non-enumerating 404.
- [x] terminal exactly once.
- [x] terminal immutable.
- [x] monotonic event IDs.
- [x] duplicate-event dedupe.
- [x] CREATED -> RUNNING -> COMPLETED.
- [x] CLARIFICATION -> WAITING_CLARIFICATION.
- [x] FAILED mapping.
- [x] cooperative cancellation.
- [x] late success cannot overwrite cancellation.
- [x] WAITING -> CANCEL_REQUESTED -> CANCELLED.
- [x] retry lineage.
- [x] INTERRUPTED recovery.
- [x] POST /fast/runs.
- [x] GET /fast/runs/{id}.
- [x] GET /fast/runs/{id}/events.
- [x] POST /fast/runs/{id}/cancel.
- [x] SSE framing.
- [x] Last-Event-ID replay.
- [x] /fast/ask compatibility retained.
- [x] provider-free lifecycle tests.
- [x] provider-free API/SSE tests.
- [x] FT-003 regressions.
- [x] real pinned-Metabase lifecycle run.
- [x] independent DB oracle equality.
- [x] real clarification/cancel lifecycle.
- [x] failure receipts closed.
- [x] live receipt sealed.

Explicit non-production debt:
- [ ] persistent run/event store.
- [ ] process-restart durability.
- [ ] distributed workers.
- [ ] cross-instance SSE fanout.
- [ ] hard cancellation of already-running Metabase query.

These unchecked items are deliberate post-FT-004 debt, not hidden GREEN claims.


## J. FT-004 post-seal invariant audit

- [x] deterministic cancel/start barrier test.
- [x] cancel after worker pre-check but before RUNNING -> Ask calls = 0.
- [x] RUN_STARTED absent when cancel wins start race.
- [x] durable owner identity excludes mutable superadmin claim.
- [x] same user/tenant retains ownership after claim change.
- [x] foreign user remains non-enumerating denied.
- [x] retry question identity strict.
- [x] retry as_of_date identity strict.
- [x] retry remains distinct from follow-up.
- [x] core/API/SSE regression.
- [x] FT-003 regression.
- [x] real pinned-Metabase lifecycle regression.
- [x] Gateway regression.
- [x] browser regression.

Post-seal focused run:
`35781659952 GREEN`

Final audited SHA:
`f8018800c773019f0e79907fec3e15edec72dbb0`
