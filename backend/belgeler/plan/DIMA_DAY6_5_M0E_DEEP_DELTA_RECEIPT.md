# DIMA DAY 6.5 — M0E-DEEP-DELTA RECEIPT

**Status:** PARTIAL / SOURCE AUDIT IN PROGRESS  
**Date:** 2026-09-22  
**Metabase pin:** `74216b30981d8310c4cf724d63ca282e2e63529d`  
**M0E-v1:** PRESERVED  
**Product code changes:** NONE  
**Metabase runtime:** NOT STARTED

This receipt is append-only by capability batch. It records exact upstream behavior separately from
Dima design disposition. Final GREEN is forbidden until all 25 required mechanisms are classified
and the contract exit counters are zero.

## Batch 1 — Access lens / derived-result authorization / cache / persistence / missing principal

### DD-01 — effective data-access lens fingerprint

- **mechanism:** effective data-access lens fingerprint
- **exact upstream source/function:**
  - `src/metabase/permissions/data_access_token.clj::data-access-token`
  - `::data-access-compatible?`
  - `::data-access-token-transform`
- **observed behavior:** Metabase fingerprints the current user's effective access context over
  touched tables/database across sandboxing, connection impersonation and database routing. Raw
  contributor values are canonicalized and SHA-256 digested before persistence. Compatibility is
  strict equality; absence is a real lens, not a wildcard. Parse failure / token computation failure
  is documented to deny rather than widen access.
- **problem solved:** a persisted result can only be replayed to a viewer whose effective row/data
  lens is compatible with the lens under which the result was computed.
- **Dima equivalent/owner:** `DIMA_CORE_NATIVE` trust plane; planned
  `ExecutionAccessFingerprint` owner Day12–14. QueryContract/Evidence may carry the non-secret
  fingerprint reference/digest, but the reference itself is not authorization.
- **Wren equivalent/owner:** Wren owns current execution-time RLS/CLS / connection route semantics;
  it does **not** own Dima replay authorization or persisted fingerprint lifecycle.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0. Result/evidence/handle reuse across a changed tenant, role,
  attribute policy, RLS/CLS version, route/destination or impersonation context must fail closed.
- **semantic duplication risk:** none; this is authorization state, not semantic truth.
- **native implementation cost:** MEDIUM.
- **Metabase runtime dependency:** NONE for Dima trust-plane ownership. If Metabase is used later,
  its own token remains an inner runtime guard, not Dima's outer authority.
- **required executable proof:** generate/reuse under access fingerprint A; alter at least one
  effective lens dimension; replay/read under B must be denied. Persisted fingerprint contains no
  raw sensitive attribute values.
- **timing:** Day12–14. X0 receipts should reserve a provisional non-secret access-lens field now.

### DD-02 — derived Evidence / Report / result viewer reauthorization

- **mechanism:** derived Evidence/Report/result viewer reauthorization
- **exact upstream source/function:**
  - `src/metabase/queries/cached_result.clj::viewer-can-run-underlying-query?`
  - `::viewer-lens-compatible?`
  - `::cached-result-blocked-reason`
  - `::assert-can-view-cached-result!`
  - `src/metabase/explorations/derived_perms.clj::thread-ids-with-visible-derived-data`
  - `::artifact-visible?`
- **observed behavior:** cached/derived data is rechecked for the **current viewer**, including the
  creator. Non-superusers must both retain permission to run the underlying query and match the
  creator's captured access lens. Missing/unreadable lens, unresolvable query, or thrown permission
  computation denies. Exploration derived text/pages/summary content are gated using the same
  current-viewer rule; creator status is not a permanent pass.
- **problem solved:** persisted derived artifacts cannot outlive the permission context that made
  them safe to view.
- **Dima equivalent/owner:** Dima Evidence/Report/Decision read boundary + current Principal / trust
  plane. ReportDocument/Evidence persistence must not imply future read authorization.
- **Wren equivalent/owner:** Wren can authorize live query execution; Dima owns authorization of
  persisted Dima artifacts and current-viewer revalidation.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0. `evidence_id`, `query_contract_id`, saved report, cached
  result or decision record != authorization.
- **semantic duplication risk:** none.
- **native implementation cost:** MEDIUM.
- **Metabase runtime dependency:** NONE for Dima-owned artifacts; Metabase must separately enforce
  its own runtime reads if adopted.
- **required executable proof:** creator produces Evidence/Report; revoke data permission or change
  effective access lens; subsequent creator/viewer read is denied/redacted. Foreign-principal
  artifact reference cannot bypass current authorization.
- **timing:** Day9 ReportDocument design + Day12–14 security seal.

### DD-03 — permission-sensitive cache identity / cache replay safety

- **mechanism:** permission-sensitive cache keying
- **exact upstream source/function:**
  - `src/metabase/query_processor/middleware/cache.clj::run-query-with-cache`
  - `::maybe-return-cached-results`
  - paired with `metabase.permissions.data-access-token` for stored snapshots
- **observed behavior:** generic QP cache computes its query hash **after normalization**, explicitly
  because sandboxed users need different normalized queries/cache identities. Cache middleware also
  documents that the query must already be permission-checked because cache hits bypass normal query
  execution middleware. Separately persisted stored-result snapshots carry a data-access token and
  are viewer-reauthorized.
- **problem solved:** avoid serving a cache entry produced under a materially different permission /
  sandbox context and avoid treating a cache hit as permission.
- **Dima equivalent/owner:** future Dima cache/result reuse policy. Cache identity must include or be
  guarded by the effective access fingerprint; current Principal authorization is still required.
- **Wren equivalent/owner:** Wren current execution/RLS can influence live results; it is not a Dima
  cache-authorization owner.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** if Dima adds caching, P0 invariant =
  `CACHE_HIT != AUTHORIZATION`; permission/lens-sensitive identity or reauthorization mandatory.
- **semantic duplication risk:** none.
- **native implementation cost:** MEDIUM if/when Dima introduces shared result caching.
- **Metabase runtime dependency:** NONE now. Metabase runtime may provide its own inner cache if X0
  is adopted; Dima must not assume that protects Dima-level artifact reuse.
- **required executable proof:** identical analytical request under two different effective access
  fingerprints cannot share an unsafe Dima result; cache hit after permission revocation must deny or
  recompute under current authority.
- **timing:** Day14 or post-MVP cache work; not an X0 selection criterion by itself.

### DD-09 — non-serializable security-bound query/result → persistence forbidden

- **mechanism:** non-serializable security-bound query → persistence forbidden
- **exact upstream source/function:**
  - `src/metabase/explorations/models/exploration_query_result.clj::composite-data-access-token`
  - `::create-ephemeral-card-for-exploration-queries!`
- **observed behavior:** when multiple source snapshots cannot be described by one honest
  `data_access_token` (missing token or different tokens), Metabase refuses to persist the composite
  snapshot instead of choosing one token and creating an artifact the read gate cannot adjudicate.
- **problem solved:** prevent durable/replayable derived state whose security context cannot be
  faithfully represented.
- **Dima equivalent/owner:** QueryContract/Evidence/Report persistence boundary.
  `runtime-only security binding cannot be faithfully serialized → replay persistence FORBIDDEN`.
- **Wren equivalent/owner:** Wren owns live secure execution; Dima owns whether the resulting
  execution context is safe to persist/replay.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0. No "best effort" security stamp and no silent downgrade to an
  unrestricted replayable artifact.
- **semantic duplication risk:** none.
- **native implementation cost:** LOW–MEDIUM once access fingerprint contract exists.
- **Metabase runtime dependency:** NONE.
- **required executable proof:** compose/persist artifacts with incompatible or unrepresentable
  security contexts → persistence/replayability rejected; live one-shot delivery may remain possible
  only if current execution is authorized and no unsafe durable replay is created.
- **timing:** Day12–14.

### DD-14 — missing creator / principal → fail closed

- **mechanism:** missing creator/principal → fail closed
- **exact upstream source/function:**
  - `src/metabase/explorations/runner.clj::run-query!`
  - `::compute-query-result`
- **observed behavior:** exploration execution resolves the owning creator and runs inside
  `request/with-current-user`. If the creator cannot be resolved, it throws rather than executing
  unbound/unrestricted. The result's data-access token is computed inside the creator binding.
- **problem solved:** async/retried work must not lose identity and accidentally execute with broader
  default privileges.
- **Dima equivalent/owner:** Research async/task runner + governed execution boundary. Every
  background/queued query needs an explicit immutable principal/tenant binding or fail-closed state.
- **Wren equivalent/owner:** Wren execution requires the passed Principal; task ownership/recovery is
  Dima-owned.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0. Missing creator/principal/tenant is terminal security failure,
  never anonymous/default/admin execution.
- **semantic duplication risk:** none.
- **native implementation cost:** LOW for invariant, MEDIUM for durable async identity/recovery.
- **Metabase runtime dependency:** NONE.
- **required executable proof:** delete/unresolve task creator or drop principal binding before async
  execution → zero DB query + typed fail-closed outcome; retry cannot widen identity.
- **timing:** Day7 async Research + Day12–14 security hardening.

### Batch 1 counters

```text
classified in this batch = 5
mechanisms closed        = 1,2,3,9,14
product code written     = 0
Metabase runtime started = 0
```


## Batch 2 — Retrieval/index authority and source-of-truth lifecycle

### DD-04 — retrieval index → current-principal hydration

- **mechanism:** retrieval index → current-principal hydration
- **exact upstream source/function:**
  - `src/metabase/metabot/tools/entity_retrieval.clj::build-matches`
  - `src/metabase/entity_retrieval/mirror.clj::search-unfiltered`
  - `src/metabase/entity_retrieval/core.clj` namespace contract
- **observed behavior:** the pgvector/entity index is explicitly user-agnostic. Raw hits are only
  candidate refs. `build-matches` hydrates the entire deduped candidate set through
  `tools.search/entity-refs->search-results`, which permission-filters for the **current user**, then
  post-filters against live `library-entity-keys` so stale/unpublished entities do not surface.
  Only readable/current entities survive to the agent.
- **problem solved:** a stale/global index cannot itself authorize entity visibility or semantic use.
- **Dima equivalent/owner:** Dima SemanticCatalogRetriever / semantic discovery boundary followed by
  current tenant/principal/context hydration and `SemanticBindingGate`.
- **Wren equivalent/owner:** Wren MDL/catalog/knowledge is the retained semantic source against which
  live candidate identity/membership is checked.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0. `INDEX_HIT != CURRENT_AUTHORITY`. Candidate discovery cannot
  mint `sem_*` handles or bypass tenant/principal/current-context checks.
- **semantic duplication risk:** LOW if index stores opaque refs only; HIGH if it becomes an
  independent business-semantic source.
- **native implementation cost:** MEDIUM.
- **Metabase runtime dependency:** NONE for Dima's authority boundary; Metabase search may later be a
  retrieval provider only.
- **required executable proof:** index returns a stale/foreign/unreadable entity ID → current
  hydration drops it before CandidateSet/handle minting; readable current entity survives.
- **timing:** Day6.5 retrieval invariant / Day12–14 security hardening.

### DD-05 — retrieval UNAVAILABLE != semantic NO_MATCH

- **mechanism:** retrieval UNAVAILABLE != semantic NO_MATCH
- **exact upstream source/function:**
  - `src/metabase/metabot/tools/entity_retrieval.clj::retrieve-library-entities-tool`
  - `enterprise/backend/src/metabase_enterprise/entity_retrieval/core.clj::retrieval-status`
  - `::entity-retrieval-available?`
  - `::search-unfiltered`
- **observed behavior:** the tool distinguishes a successful empty result from subsystem failure.
  Search/tool exceptions return an explicit “temporarily unavailable; this does not mean the library
  is empty” output and omit successful structured search payload. Retrieval health separately
  distinguishes missing/incompatible/empty/populated/unreachable index states. Unexpected SQL/store
  failures propagate as unavailability; only known index-not-ready states degrade to empty/no result.
- **problem solved:** infrastructure outage cannot be misinterpreted as semantic absence and cause a
  false “nothing matches” conclusion.
- **Dima equivalent/owner:** typed retrieval outcome in Dima semantic-discovery layer:
  `MATCHES | NO_MATCH | UNAVAILABLE | ERROR`. Only `NO_MATCH` may support semantic absence;
  `UNAVAILABLE` is transport/infrastructure evidence.
- **Wren equivalent/owner:** Wren catalog availability can be an input signal, but Dima owns the
  user-facing/agent-facing typed distinction and fallback policy.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** avoids silent fallback to weaker semantic authority during retrieval
  outage.
- **semantic duplication risk:** none.
- **native implementation cost:** LOW.
- **Metabase runtime dependency:** NONE.
- **required executable proof:** force retrieval backend unavailable → typed UNAVAILABLE and zero
  semantic absence claim; empty healthy catalog/search → typed NO_MATCH; no hidden fallback authority.
- **timing:** semantic retrieval boundary / release hardening.

### DD-06 — indexed high-cardinality candidate → live current-user re-read

- **mechanism:** indexed high-cardinality entity candidate → live current-user re-read
- **exact upstream source/function:**
  - `src/metabase/indexed_entities/models/model_index.clj::value-for-pk`
  - `::values-query`
- **observed behavior:** the shared `model_index_value` table is explicitly lens-free. For a concrete
  indexed entity value, `value-for-pk` deliberately does **not** read the shared index row; it runs
  the model query through the QP under the current user, so data permissions, sandboxing,
  impersonation and routing apply. Missing permission/no row yields nil.
- **problem solved:** a shared search index cannot leak sensitive/high-cardinality dimension/entity
  values or serve stale values as current authorized truth.
- **Dima equivalent/owner:** entity/filter resolution boundary. Search/index may propose opaque entity
  IDs; sensitive/high-cardinality display/value confirmation must use a current-principal authoritative
  read before becoming a governed filter/handle.
- **Wren equivalent/owner:** Wren/current DB execution is the authoritative live read; Dima owns the
  candidate-to-filter trust decision.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0 for sensitive entity values. Index text is discovery evidence only.
- **semantic duplication risk:** LOW when index stores IDs/text only.
- **native implementation cost:** MEDIUM.
- **Metabase runtime dependency:** NONE; if Metabase provides candidate IDs later, Dima/Wren current
  authority still re-reads as needed.
- **required executable proof:** index candidate exists for principal A; principal B lacks row/value
  access → live re-read returns no authorized value and no filter/semantic handle is minted.
- **timing:** Day7–14 entity/filter hardening; large-catalog retrieval later.

### DD-07 — AI-context source-of-truth → derived index lifecycle

- **mechanism:** AI-context source-of-truth → derived index lifecycle
- **exact upstream source/function:**
  - `enterprise/backend/src/metabase_enterprise/entity_retrieval/reconcile.clj` namespace contract
  - `::library-entity`, `::library-entity-keys`, `::reconcile!`, `::reconcile-entity!`
  - `src/metabase/entity_retrieval/core.clj::ai-context-instructions`
  - `src/metabase/osi/ai_context/api.clj`
- **observed behavior:** Metabase declares appdb library membership + `osi_ai_context` as the
  authoritative source. The vector index is derived by diff/reconcile and garbage-collects stale docs.
  Curator `instructions` are intentionally **not** embedded/indexed; they are read live from
  `osi_ai_context` per request. Targeted reconcile is eventually consistent and a periodic/full diff
  is the backstop.
- **problem solved:** retrieval indexes remain disposable projections of authoritative metadata rather
  than independent semantic truth.
- **Dima equivalent/owner:** retained Wren MDL/models/relationships/cubes/knowledge/business context
  is the semantic source of truth. Any future vector/BM25/entity index is derived/rebuildable.
- **Wren equivalent/owner:** **Wren owns** authoritative semantic/business context.
- **disposition:** **WREN_OWNS**
- **security/authority effect:** index drift/staleness can affect recall, never authority. Live Wren
  membership/context wins over index contents.
- **semantic duplication risk:** HIGH if Dima/Metabase index stores separately curated metric formulas,
  relationships, grain, time semantics or business rules.
- **native implementation cost:** N/A for semantic ownership; MEDIUM-HIGH for optional derived index
  lifecycle.
- **Metabase runtime dependency:** NONE. Metabase index implementation may be a future retrieval
  candidate, not semantic owner.
- **required executable proof:** remove/alter authoritative Wren semantic object while stale index
  still contains it → current catalog/hydration rejects it; rebuild may lag without widening authority.
  Rebuild-from-Wren produces the index state from scratch.
- **timing:** permanent ownership decision; retrieval/index implementation is later optimization.

### Batch 2 counters

```text
classified in this batch = 4
mechanisms closed        = 4,5,6,7
cumulative classified    = 9 / 25
remaining                = 16
product code written     = 0
Metabase runtime started = 0
```


## Batch 3 — Agent state / async idempotency / bounded fanout / interestingness

### DD-08 — accumulated agent state vs per-turn state delta

- **mechanism:** agent accumulated state vs per-turn state delta
- **exact upstream source/function:**
  - `src/metabase/metabot/persistence.clj::conversation-state`
  - `::finalize-assistant-turn!`
  - `src/metabase/metabot/agent/core.clj::init-agent`
  - `::seed-state`, `::seed-chart-configs`, `::client-content-ids`
- **observed behavior:** Metabot persists a turn's produced state separately on the assistant row and
  reconstructs accumulated conversation state by merging replayable prior turn states. At a new request,
  current viewing context is seeded into a fresh agent memory on top of prior state, and IDs coming from
  the current client turn are tracked separately from prior accumulated IDs.
- **problem solved:** preserve useful multi-turn working state without losing the distinction between
  previously accumulated memory and what the current request explicitly supplied.
- **Dima equivalent/owner:** Dima ConversationState / ResearchState memory plus current-turn
  `AcceptedTurnContract` authority. Prior memory may guide cognition but cannot silently add/modify
  current USER_MUST obligations or canonical semantics.
- **Wren equivalent/owner:** Wren supplies semantic/context facts; conversation memory ownership remains Dima.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** prior state is non-authoritative unless revalidated/rebound under current
  context/tenant/principal. Current-turn source refs/authority remain explicit.
- **semantic duplication risk:** MEDIUM if accumulated memory is allowed to carry stale canonical semantics
  without context-version checks.
- **native implementation cost:** MEDIUM; Dima already has ConversationState/ResearchState foundations.
- **Metabase runtime dependency:** NONE.
- **required executable proof:** prior state contains metric/filter/query; current turn omits or contradicts
  it → no silent USER_MUST creation or authority mutation. Context-version/tenant change invalidates stale
  semantic handles while non-authoritative conversational memory may remain.
- **timing:** Day7 Research loop / Day10 dispatcher integration.

### DD-13 — async exploration idempotency / cancellation / race handling

- **mechanism:** async exploration idempotency/cancel/race
- **exact upstream source/function:**
  - `src/metabase/explorations/query_plan.clj::lock-thread-for-planning!`
  - `::insert-plan-rows!`
  - `src/metabase/explorations/runner.clj::plan-thread!`
  - `::run-query!`, `::canceled-mid-plan-cleanup!`
  - `src/metabase/explorations/queues.clj::deliver-batch!`, `::publish-pending-queries!`
- **observed behavior:** queue delivery is treated as at-least-once. Planning takes a DB row lock and
  re-checks under the lock so concurrent duplicate planners cannot both materialize work. Redelivered
  terminal query messages do not rerun the query; they only re-run completion checks. Cancellation races
  are repaired by flipping queries inserted after cancel. Pending rows, rather than "just inserted" rows,
  drive republish so crash/retry is idempotent.
- **problem solved:** durable async analysis must tolerate duplicate delivery, crash between write/publish,
  cancel/plan races and peer completion without duplicate query side effects or resurrected work.
- **Dima equivalent/owner:** Dima Research async runner/task store. Task identity + accepted authority +
  principal binding must make plan/query actions idempotent and cancel-safe.
- **Wren equivalent/owner:** Wren executes a governed query; task delivery/idempotency/cancel lifecycle is
  Dima-owned.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** duplicate/redelivered task cannot mint a second authority, rerun after
  terminal cancel, or execute under a broader/missing principal.
- **semantic duplication risk:** none.
- **native implementation cost:** MEDIUM-HIGH.
- **Metabase runtime dependency:** NONE for Dima Research. Metabase exploration runtime may later inform UX,
  not own Dima Research execution state.
- **required executable proof:** duplicate plan delivery → one materialized task set; crash after durable
  task write before publish → retry publishes pending work without replanning; cancel during plan → late rows
  become canceled; terminal query redelivery → zero duplicate DB query.
- **timing:** Day7 Research loop; strengthened Day12–14.

### DD-15 — cardinality-bounded Research fanout

- **mechanism:** cardinality-bounded Research fanout
- **exact upstream source/function:**
  - `src/metabase/explorations/query_plan/mechanical.clj::default-eligible?`
  - `::time-facet-eligible?`
  - `::top-n-other-eligible?`
  - `::items-for-pair`
  - `src/metabase/explorations/query_plan/variants.clj::default-max-rows`
  - `::cached-discovery`
  - `::plan-rows` for `per-value-time-series`
- **observed behavior:** low/known cardinality can use direct/default views; high or unknown categorical
  cardinality routes to bounded `top-n-other` with fixed K. Unknown cardinality fails safe into a bounded
  form instead of an unbounded breakout. Variant execution also has row-count safety caps. Discovery Top-K
  cache keys include current user and scope/filter chain because live warehouse values are lens-dependent.
- **problem solved:** exploratory breadth must remain bounded even when metadata/cardinality is missing or
  large, while preserving a useful "head + Other" view instead of exploding queries/rows.
- **Dima equivalent/owner:** Dima Research planner / derived-task budget. Semantic/metadata cardinality informs
  deterministic fanout budgets; high-cardinality work becomes Top-K + Other / sampled bounded tasks.
- **Wren equivalent/owner:** Wren/DB metadata may provide cardinality/source statistics; Dima owns how many
  research tasks/queries are spawned.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** bounded fanout is also a cost/DoS guard. Unknown cardinality must not imply
  unlimited exploration.
- **semantic duplication risk:** LOW.
- **native implementation cost:** MEDIUM.
- **Metabase runtime dependency:** NONE.
- **required executable proof:** low cardinality → complete bounded family; high/unknown cardinality →
  deterministic Top-K + Other (or equivalent) with explicit max tasks/query count; same user/filter scope
  cannot leak cached discovered values across principals.
- **timing:** Day7 Research planning.

### DD-16 — interestingness is non-authoritative prioritization only

- **mechanism:** interestingness = non-authoritative prioritization only
- **exact upstream source/function:**
  - `src/metabase/explorations/runner.clj::safe-score`
  - `::safe-score+describe`
  - `src/metabase/contextual_interestingness/llm.clj::llm-call!`
- **observed behavior:** statistical/contextual interestingness is computed after query execution as a
  best-effort score/description. Scoring failures are swallowed/logged and **must never flip a successful
  query to error**. The LLM scorer returns relevance/description metadata; it does not validate numeric
  truth or query correctness.
- **problem solved:** rank/prioritize which already-computed findings deserve user attention without making
  the prioritizer part of the truth path.
- **Dima equivalent/owner:** Day8 epistemic/prioritization layer may rank verified Evidence/ResearchTasks;
  Verification/QueryContract/Evidence gates remain truth owners.
- **Wren equivalent/owner:** Wren/DB provide executed result truth; no interestingness authority.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** score cannot override permission, verification, evidence provenance or
  USER_MUST completion.
- **semantic duplication risk:** none when applied only after verified evidence.
- **native implementation cost:** LOW-MEDIUM.
- **Metabase runtime dependency:** NONE.
- **required executable proof:** scoring/LLM failure leaves verified query/evidence lifecycle intact; high
  score on unverified/empty/invalid evidence cannot mark obligation VERIFIED, create a causal finding or
  satisfy CompletionGate.
- **timing:** Day8 root-cause / evidence prioritization.

### Batch 3 counters

```text
classified in this batch = 4
mechanisms closed        = 8,13,15,16
cumulative classified    = 13 / 25
remaining                = 12
product code written     = 0
Metabase runtime started = 0
```


## Batch 4 — Agent API / MCP transport, authorization, provenance, feature gates

### DD-10 — REST serialized continuation vs MCP server-side query_handle

- **mechanism:** REST serialized query/continuation vs MCP server-side query_handle
- **exact upstream source/function:**
  - `src/metabase/agent_api/api.clj::generate-continuation-token`
  - `::decode-continuation-token`
  - `::initial-page-state`
  - `::/v2/query` endpoint
  - `src/metabase/mcp/v2/queries.clj::mint-query-handle!`
  - `::resolve-query-handle!`
  - `src/metabase/mcp/session.clj::store-handle!`
  - `::resolve-query-handle`, `::find-handle-row`
- **observed behavior:** Agent API REST continuation tokens are client-carried serialized state
  containing the resolved query plus pagination state; decoding validates shape and re-checks current
  query permissions before reuse, with QP execution as the authoritative backstop. MCP v2 query
  handles are different: the server stores the exact encoded serialized query under an opaque UUID,
  binds the row to a materialized user-owned core session, resolves handles by **user_id**, and on
  MBQL reuse re-runs native-query/shape/permission guards. Cross-session reuse by the same user is
  allowed; cross-user lookup is denied by the DB join/filter.
- **problem solved:** give agents a compact continuation/reuse primitive without treating the token or
  opaque handle as authorization and without forcing the model to carry full query payloads.
- **Dima equivalent/owner:** Dima QueryContract/Evidence IDs and any future execution continuation.
  For X0-REST, Dima should use REST semantics explicitly rather than accidentally depending on MCP
  server-side handle persistence.
- **Wren equivalent/owner:** Wren execution/query identifiers are current incumbent internals; Dima
  owns cross-turn provenance/replay identity.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** `HANDLE/TOKEN != AUTHORIZATION`. Every reuse must validate current
  Principal/access and query shape. REST and MCP semantics must not be conflated in the X0 receipt.
- **semantic duplication risk:** none if payload already represents accepted Dima semantics.
- **native implementation cost:** LOW-MEDIUM for Dima-owned opaque provenance; HIGH if duplicating a
  full durable handle/session product unnecessarily.
- **Metabase runtime dependency:** REST continuation needs no MCP handle store; MCP handles require
  Metabase app DB/session state. X0-REST should not take this dependency unless separately justified.
- **required executable proof:** (a) REST continuation after permission revocation is denied;
  (b) malformed/native continuation rejected; (c) MCP handle resolves for same user, not foreign user;
  (d) X0-REST adapter works without MCP handle persistence.
- **timing:** X0 preflight/runtime design; full durable replay hardening Day12–14.

### DD-11 — client-declared capability != authorization

- **mechanism:** client-declared capability != authorization
- **exact upstream source/function:**
  - `src/metabase/mcp/v2/registry.clj` namespace contract
  - `::list-tools`, `::dispatch-tool-call`
  - `src/metabase/mcp/session.clj::session-parts`
  - `::supports-mcp-ui?`
  - `src/metabase/mcp/transport.clj::handle-initialize`
- **observed behavior:** Metabase explicitly documents that client extension/capability declarations
  are UX/rendering hints, not authorization boundaries. Tool listing may hide tools a client cannot
  render, but call-time authorization is enforced from verified token scopes. The session capability
  payload is server-signed before being trusted; invalid/unsigned capability claims downgrade rather
  than grant capability. Tool dispatch checks OAuth/token scope separately from required client
  extensions.
- **problem solved:** prevent a client from self-declaring a capability/extension and thereby obtaining
  data/action authority.
- **Dima equivalent/owner:** Dima tool/profile capability registry + authenticated Principal/policy
  checks. Model/tool availability, UI capability, requested feature flags and client metadata are all
  non-authoritative hints.
- **Wren equivalent/owner:** Wren executes under an explicit Principal; it does not decide Dima client
  capabilities.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** P0. A caller/model saying “I support/can use X” never grants X.
  Authorization comes from server-owned policy/Principal only.
- **semantic duplication risk:** none.
- **native implementation cost:** LOW-MEDIUM.
- **Metabase runtime dependency:** NONE for Dima outer authorization. Metabase scopes remain an inner
  defense if runtime is adopted.
- **required executable proof:** unsigned/forged capability changes tool visibility at most, never
  privilege; missing scope/principal permission denies call even when client advertises support.
- **timing:** permanent invariant; X0 scope mapping proof.

### DD-12 — Dima-owned Agent API telemetry / provenance

- **mechanism:** Dima-owned Agent API telemetry/provenance
- **exact upstream source/function:**
  - `src/metabase/agent_api/api.clj` construct endpoints using
    `metabase.ai-tracing.core/record!` with resolved query payload
  - `src/metabase/agent_api/usage.clj::wrap-record-cli-usage`
  - `::record-agent-api-call!`
  - `enterprise/backend/src/metabase_enterprise/agent_api/usage.clj::record-agent-api-call!`
  - `src/metabase/mcp/transport.clj` eval tracing/redaction path
- **observed behavior:** Metabase has two different observability families: AI/eval tracing can capture
  resolved query/tool data for evaluation, while Agent API usage middleware records caller/operation/
  status/duration (EE write, OSS no-op) and explicitly treats self-reported User-Agent only as analytics,
  never access control. Logging is best-effort and failures are swallowed so telemetry cannot fail the
  request. Sensitive fields are retention-gated/redacted.
- **problem solved:** operational usage/debug/eval observability without making logging a correctness or
  authorization dependency.
- **Dima equivalent/owner:** Dima QueryContract, EvidenceArtifact, audit/DecisionRecord and request
  telemetry. Dima must own the authoritative provenance chain that ties accepted authority → execution
  adapter → result/evidence. Metabase trace/call logs are supplemental runtime telemetry only.
- **Wren equivalent/owner:** Wren can contribute compiler/execution metadata; Dima seals final provenance.
- **disposition:** **DIMA_CORE_NATIVE**
- **security/authority effect:** telemetry cannot authorize, verify or replace QueryContract/Evidence.
  Secrets/credentials/raw sensitive attributes must not leak into durable traces.
- **semantic duplication risk:** none; provenance references semantic authority, it does not redefine it.
- **native implementation cost:** MEDIUM; core QueryContract/Evidence already exists.
- **Metabase runtime dependency:** NONE for authoritative provenance. If X0 uses Metabase, collect
  operation/request/runtime IDs as secondary evidence.
- **required executable proof:** X0 result carries Dima authority ID + adapter ID + Metabase operation/
  request correlation + current Principal/access fingerprint reference into QueryContract/Evidence;
  turning Metabase usage logging off/failing must not break Dima provenance or execution. Credential/
  secret redaction test mandatory.
- **timing:** X0 receipt field + Day9/12–14 audit hardening.

### DD-20 — Agent API global AI-feature dependency

- **mechanism:** Agent API global AI-feature dependency
- **exact upstream source/function:**
  - `src/metabase/agent_api/settings.clj::agent-api-enabled?`
  - `src/metabase/agent_api/validation.clj::check-agent-api-enabled`
  - `::enforce-agent-api-enabled`
- **observed behavior:** `agent-api-enabled?` is not an independent switch: its getter ANDs the
  Agent API setting with global `llm.settings/ai-features-enabled?`. External Agent API routes are
  middleware-gated and return 403 when either global AI features or Agent API itself is disabled.
- **problem solved:** central operational enable/disable control for the whole external Agent API.
- **Dima equivalent/owner:** no equivalent semantic/trust owner. This is a **runtime prerequisite and
  blast-radius dependency** introduced only if Metabase Agent API becomes an execution substrate.
- **Wren equivalent/owner:** none; current Wren execution does not require enabling Metabase AI features.
- **disposition:** **METABASE_RUNTIME_CANDIDATE**
- **security/authority effect:** enabling the runtime may enable/affect a broader AI feature surface;
  this must be explicitly configured and threat-reviewed rather than silently inherited.
- **semantic duplication risk:** none directly.
- **native implementation cost:** N/A; this is adoption cost, not something Dima should rebuild.
- **Metabase runtime dependency:** YES — Agent API X0/full-X requires global AI features + Agent API
  enabled in the self-hosted service.
- **required executable proof:** pinned self-hosted X0 shows exact minimal settings needed; Agent API
  structured endpoints work with intended external-LLM configuration; disabling either gate fails
  closed; enabling them does not accidentally expose an unapproved tool/scope surface to Dima.
- **timing:** X0-REST mandatory operational receipt; full-X decision input.

### DD-21 — raw SQL kill-switch operational dependency

- **mechanism:** raw SQL kill-switch operational dependency
- **exact upstream source/function:**
  - `src/metabase/agent_api/settings.clj::mcp-execute-sql-enabled`
  - `src/metabase/agent_api/api.clj::/v1/execute-sql`
  - `src/metabase/agent_api/query_guards.clj::reject-native-query!`
  - `::check-mcp-ui-native-query!`
  - `src/metabase/mcp/v2/queries.clj::check-execute-sql-enabled!`
- **observed behavior:** raw SQL is a distinct capability with a dedicated instance kill-switch and
  native-query permission/scope. Structured MBQL execution explicitly rejects native queries,
  including buried/native markers in client-reachable serialized payloads, to prevent MBQL scopes
  from smuggling SQL and bypassing the kill-switch. MCP v2 applies the kill-switch to agent-authored
  SQL paths including validate-only/write staging; saved pre-existing native questions are a separate
  read/execution capability.
- **problem solved:** keep structured governed execution separate from an intentionally more powerful
  raw-SQL escape hatch and allow administrators to remove agent-authored SQL completely.
- **Dima equivalent/owner:** Dima Manager/Standard governed path has **no raw SQL tool**. SQL authoring
  is outside the selected Day6.5 architecture.
- **Wren equivalent/owner:** Wren compiles governed semantic requests; Dima does not delegate raw SQL
  cognition to the model.
- **disposition:** **REJECT**
- **security/authority effect:** P0 for X0:
  `MANAGER_RAW_SQL_EXECUTION=0`; `NATIVE_SQL_SMUGGLE=0`. Metabase raw-SQL tool must be disabled
  and structured endpoints must still reject native payloads.
- **semantic duplication risk:** raw SQL bypasses semantic authority entirely, hence unacceptable.
- **native implementation cost:** none — do not implement.
- **Metabase runtime dependency:** if X0-REST is run, configure `mcp-execute-sql-enabled=false` and
  do not grant SQL authoring scopes.
- **required executable proof:** execute-sql returns 403/absent under X0 config; native top-level and
  nested payloads sent through structured query endpoints fail closed; no Dima adapter invokes native
  construction/execution routes.
- **timing:** X0 preflight/runtime P0 and permanent production invariant.

### Batch 4 counters

```text
classified in this batch = 5
mechanisms closed        = 10,11,12,20,21
cumulative classified    = 18 / 25
remaining                = 7
product code written     = 0
Metabase runtime started = 0
```


## Batch 5 — Content curation, glossary ownership, lib_metric semantics, OSI watchlist

### DD-17 — content verification / official-content metadata

- **mechanism:** content verification / official-content metadata
- **exact upstream source/function:**
  - `src/metabase/queries/models/card.clj::card-is-verified?`
  - `::unverify-card-if-needed!`
  - Card search spec fields `:verified` and `:official-collection`
  - `src/metabase/content_verification/models/moderation_review.clj::create-review!`
  - collection `authority_level = "official"` surfaced through search/curation metadata
- **observed behavior:** Metabase carries explicit curation signals distinct from query execution:
  the latest moderation review can mark a Card `verified`; materially editing a verified query
  automatically creates an “Unverified due to edit” review. Search metadata separately exposes
  whether content lives in an official collection. These labels can be ranked/rendered as trust/
  curation metadata but do not replace data permissions or QP execution correctness.
- **problem solved:** let organizations distinguish reviewed/endorsed analytical content from ordinary
  user-authored content and invalidate endorsement when the underlying query changes.
- **Dima equivalent/owner:** Dima catalog/evidence/product metadata may later expose
  `certified/official/reviewed` status with source/version. Numeric/query truth still belongs to
  Wren/DB + QueryContract/Evidence; semantic truth remains Wren.
- **Wren equivalent/owner:** Wren owns semantic definitions; it may supply version/context identity but
  does not need Metabase moderation state to make a semantic object true.
- **disposition:** **PATTERN_ONLY**
- **security/authority effect:** `VERIFIED/OFFICIAL != AUTHORIZATION` and
  `VERIFIED/OFFICIAL != EVIDENCE`. Curation may affect ranking/presentation only.
- **semantic duplication risk:** LOW if it is metadata; HIGH if “official” starts minting semantic
  handles or bypassing Wren definitions.
- **native implementation cost:** LOW-MEDIUM.
- **Metabase runtime dependency:** NONE for Dima core. If Metabase workspace is later adopted, its
  curation metadata can remain workspace-local or be explicitly mapped.
- **required executable proof:** changing the underlying governed definition/query invalidates or
  version-splits certification; an unverified item can still execute if authorized; a verified item
  cannot bypass permissions/Evidence; ranking may prefer certified items without altering canonical
  semantic binding.
- **timing:** Day8/9 provenance UX or post-MVP workspace.

### DD-18 — glossary lifecycle vs retained Wren knowledge

- **mechanism:** glossary lifecycle vs Wren knowledge
- **exact upstream source/function:**
  - `src/metabase/glossary/core.clj::entries`
  - `::create-entry!`, `::update-entry!`, `::delete-entry!`
  - `src/metabase/glossary/models/glossary.clj` serialization lifecycle
  - `src/metabase/mcp/v2/tools/glossary.clj::glossary`
- **observed behavior:** Metabase maintains an independent durable glossary of unique business terms
  and definitions, with CRUD/events/serialization. The MCP glossary tool tells the agent these
  analyst-authored definitions should override its ordinary-language reading of a term.
- **problem solved:** centrally curate business-language definitions for AI/user interpretation.
- **Dima equivalent/owner:** retained Wren `knowledge` / business context + Dima semantic context.
  Business definitions that can affect interpretation or canonical binding must originate from the
  same retained semantic source, not an independently edited second glossary.
- **Wren equivalent/owner:** **WREN_OWNS** business-semantic knowledge.
- **disposition:** **WREN_OWNS**
- **security/authority effect:** a Metabase glossary term must never override an accepted Wren semantic
  definition or mint Dima authority. If surfaced later, it is either derived from Wren or explicitly
  non-authoritative workspace annotation.
- **semantic duplication risk:** **VERY HIGH** if Wren Knowledge and Metabase Glossary are both manually
  curated as authoritative.
- **native implementation cost:** N/A for ownership; syncing two systems would create ongoing cost and
  drift, which is precisely what must be avoided.
- **Metabase runtime dependency:** NONE for semantic truth. Optional workspace glossary is a separate
  later product decision.
- **required executable proof:** conflicting Metabase glossary text cannot alter Wren-derived handle/
  metric/relationship binding; `manual_dual_business_definition_maintenance = 0` in X0/full-X.
  Any future export to a workspace must be one-way/derived or explicitly non-authoritative.
- **timing:** permanent ownership decision; workspace integration post-MVP.

### DD-22 — Metabase lib_metric multi-source semantics

- **mechanism:** Metabase lib_metric multi-source semantics
- **exact upstream source/function:**
  - `src/metabase/lib_metric/core.cljc` module contract
  - `src/metabase/lib_metric/definition.cljc::expression-leaves`
  - `::->query-plan`
  - `src/metabase/lib_metric/ast/plan.cljc::validate-arithmetic-ast!`
  - `::plan-from-ast`, `::join-and-compute`
  - `src/metabase/lib_metric/metadata/provider.cljc::MetricContextMetadataProvider`
  - `::metric-context-metadata-provider`
  - `src/metabase/lib_metric/dimension.cljc::group-by-source`
  - `src/metabase/lib_metric/dimension/jvm.clj::compute-dimension-pairs`
- **observed behavior:** `lib_metric` is a semantic/query-planning subsystem, not just display
  metadata. A MetricDefinition can be a single metric/measure or an arithmetic expression over
  multiple metric/measure leaves. Arithmetic plans compile multiple leaf MBQL queries, require
  compatible breakout dimensions, then inner-join result tuples and compute the expression. Its
  metadata provider explicitly has **no single database context** and can route metadata across
  multiple databases. Metric dimensions have persistent UUIDs/mappings and can include explicit or
  implicitly joinable connection groups.
- **problem solved:** define reusable metric semantics, projections and arithmetic across multiple
  semantic sources/databases.
- **Dima equivalent/owner:** Dima consumes canonical metric/dimension/relationship semantics from
  retained Wren and keeps analytical validity in Dima planner/trust plane. This Metabase subsystem is
  a **competing semantic layer** for the same concepts.
- **Wren equivalent/owner:** **WREN_OWNS** metric formulas, relationships, cubes/models, grain/time/
  dimension semantics for Dima.
- **disposition:** **WREN_OWNS**
- **security/authority effect:** Metabase metric IDs/definitions/dimension mappings cannot become Dima
  semantic authority. X0 may execute a translated accepted query but must not require recreating the
  metric formula in `lib_metric`.
- **semantic duplication risk:** **CRITICAL/VERY HIGH** — dual formulas, dimension UUID mappings,
  implicit joins, compatible-breakout rules and multi-source arithmetic would create a second
  semantic compiler/source of truth.
- **native implementation cost:** N/A for ownership; adopting this layer would add large migration/
  synchronization cost.
- **Metabase runtime dependency:** structured X0 must work **without** maintaining parallel Metabase
  metrics. If it cannot, the execution arm is rejected at bridge preflight.
- **required executable proof:** representative Standard artifacts translate using accepted Dima/Wren
  semantics with `manual_metabase_metric_definitions=0`, `metric_formula_duplication=0`,
  `relationship_duplication=0`, `grain/time_duplication=0`. Any case requiring a Metabase metric
  shadow definition fails bridge P0.
- **timing:** permanent preflight ownership constraint.

### DD-23 — OSI/Ossie interoperability watchlist

- **mechanism:** OSI/Ossie interoperability watchlist
- **exact upstream source/function/evidence at pinned SHA:**
  - `src/metabase/osi/models/osi_ai_context.clj`
  - `src/metabase/osi/schema.clj::osi-ai-context.ai-context`
  - `src/metabase/osi/ai_context/api.clj`
  - serialization/retrieval hooks around `OsiAiContext`
  - repository search at the pinned source shows no production “Ossie” semantic model/interchange
    implementation; the only unrelated `ossie` token is test fixture data.
- **observed behavior:** the concrete OSI surface present in this source tree is a per-entity
  `ai_context` object containing bounded `instructions`, `synonyms` and `examples`, keyed to
  existing Metabase entities and serialized with them. Writes nudge a derived retrieval-index
  reconcile. The pinned source does **not** provide sufficient evidence of a full portable
  metric/relationship/grain semantic interchange contract that could replace Wren.
- **problem solved:** attach interoperable/portable AI-facing context to existing semantic entities and
  keep retrieval projections updated.
- **Dima equivalent/owner:** Wren Knowledge/business context remains authoritative. Dima may later
  export/import standardized AI annotations if a mature interoperability contract proves useful.
- **Wren equivalent/owner:** Wren owns current semantic model/knowledge; any future OSI adapter must be
  derived from or losslessly mapped to it.
- **disposition:** **DEFER_PRODUCT**
- **security/authority effect:** future external interoperability metadata cannot self-authorize or
  become a second semantic source.
- **semantic duplication risk:** currently LOW because this is annotations; could become HIGH if a
  future standard carries full metric/relationship semantics and is independently curated.
- **native implementation cost:** UNKNOWN until a mature target specification/runtime requirement is
  concrete; do not pre-build.
- **Metabase runtime dependency:** NONE today.
- **required executable proof before future adoption:** round-trip a representative Wren semantic pack
  through the target interoperability format with zero metric formula/relationship/grain/time loss and
  no second editable authority. If not lossless, keep it annotations-only.
- **timing:** watchlist / post-MVP; not an X0 blocker beyond confirming current source cannot replace Wren.

### Batch 5 counters

```text
classified in this batch = 4
mechanisms closed        = 17,18,22,23
cumulative classified    = 22 / 25
remaining                = 3
product code written     = 0
Metabase runtime started = 0
```


## Batch 6 — Wren→Metabase bridge / implicit-FK authority / repair fixed-point

### DD-19 — Wren→Metabase semantic bridge

- **mechanism:** Wren→Metabase semantic bridge
- **exact upstream source/function:**
  - `src/metabase/agent_api/api.clj::evaluate-external-query-to-live-query`
  - `::evaluate-external-query-for-execution`
  - `POST /v2/construct-query`
  - `src/metabase/metabot/tools/construct.clj::execute-representations-query`
  - `src/metabase/agent_lib/representations/repair.clj::repair`
  - `src/metabase/agent_lib/representations/resolve.clj::resolve-query`
- **observed behavior:** Metabase's supported agent-facing structured path accepts an external portable
  MBQL representation, validates/converts/repairs it, resolves portable references through Metabase
  metadata, then produces canonical numeric-ID MBQL for execution. This is a **query lifecycle
  boundary**, not evidence that Dima/Wren semantics can be mapped losslessly without a translation
  layer. Metabase's representation still expects Metabase tables/fields/metadata identities.
- **problem solved:** give an external agent a structured, repairable query contract without requiring
  raw SQL.
- **Dima equivalent/owner:** accepted Standard authority + `StandardProjection` + once-resolved
  canonical Dima `AnalyticsIR`. Dima owns the bridge adapter; raw user language and semantic
  discovery stay upstream and never enter Metabase.
- **Wren equivalent/owner:** Wren retains canonical metric/dimension/filter/time/relationship meaning
  and remains the incumbent planner/execution path. Bridge translation must consume already-accepted
  meaning, never recreate it.
- **disposition:** **METABASE_RUNTIME_CANDIDATE**
- **security/authority effect:** P0:
  `RAW_LANGUAGE_REINTERPRETATION=0`,
  `SECOND_SEMANTIC_AUTHORITY=0`,
  `LABEL_GUESSING=0`.
- **semantic duplication risk:** potentially CRITICAL. A bridge that needs parallel metric formulas,
  relationship definitions, grain/additivity rules, time semantics, or large hand-maintained metadata
  mapping is rejected before runtime X0.
- **native implementation cost:** UNKNOWN until bridge preflight; target must remain THIN. A generic
  second semantic compiler is explicitly forbidden.
- **Metabase runtime dependency:** NONE for preflight; only if bridge is thin/lossless may X0-REST
  start a separate Metabase service.
- **required executable proof/question:** compare seams A/B/C using **real artifacts from the sealed
  Standard pipeline**:
  A=`StandardProjection + sem_* handles`,
  B=resolved canonical `AnalyticsIR`,
  C=later Wren-specific planned representation.
  For eight representative Standard families measure metric/dimension/filter/time/comparison/ranking
  fidelity, manual metadata mapping, semantic duplication, unsupported constructs, bridge LOC/
  conceptual complexity/sync surface. No fake easy IR as primary evidence.
- **timing:** **immediately after M0E FINAL GREEN** as
  `D65-X0-BRIDGE-PREFLIGHT`; runtime still OFF.

### DD-24 — implicit-FK join repair vs Wren relationship authority

- **mechanism:** implicit-FK join repair
- **exact upstream source/function:**
  - `src/metabase/agent_lib/representations/repair.clj::maybe-fill-source-field`
  - `::resolve-implicit-joins-in-stage`
  - `::resolve-implicit-joins*`
  - Pass 3.5 `resolve-source-field-join-alias*`
  - `test/metabase/agent_lib/representations/repair_test.clj`
    implicit-join happy/no-path/ambiguous/idempotency families
- **observed behavior:** when a field belongs to a table other than the stage source, Metabase can
  inspect physical metadata and, if exactly one outbound FK reaches that target table, automatically
  add `source-field` so QP performs an implicit join. Zero FK produces a typed `:no-fk-path`
  error; multiple FKs produce `:ambiguous-fk`; explicit/disambiguated join options are preserved.
  Pass 3.5 can similarly infer a unique FK through an explicit joined table.
- **problem solved:** repair an agent-authored query that names a reachable foreign-table column but
  omitted the MBQL join disambiguator.
- **Dima equivalent/owner:** relationship validity is already governed by retained Wren semantic
  relationships/cubes and Dima cross-domain/join gates. Physical FK metadata alone is insufficient
  semantic authority.
- **Wren equivalent/owner:** **WREN_OWNS** which relationships/paths are semantically approved for
  Dima.
- **disposition:** **REJECT** as an autonomous semantic/join-authority mechanism.
- **security/authority effect:** permanent P0:
  `UNAPPROVED_METABASE_IMPLICIT_JOIN=0`.
  A physical FK discovered by Metabase may not widen an accepted Dima/Wren query.
- **semantic duplication risk:** CRITICAL if Metabase physical-FK inference is allowed to create paths
  absent from or conflicting with Wren MDL.
- **native implementation cost:** none; do not reimplement physical-FK guessing as Dima authority.
- **Metabase runtime dependency:** if X0 uses Agent API repair, the adapter must compare any repaired
  relationship/join semantics with the Wren-approved accepted intent and reject divergence. Prefer an
  explicit bridge representation that does not rely on autonomous join invention.
- **required executable proof:** feed a bridge artifact whose target field is physically FK-reachable
  but whose relationship is not approved by Wren → zero execution. Approved Wren relationship may
  translate explicitly; a Metabase repair diff introducing an unapproved `source-field` or join is
  a P0 failure. Ambiguous/no-path remains fail-closed.
- **timing:** X0-BRIDGE-PREFLIGHT hard gate and X0 runtime P0 if runtime is reached.

### DD-25 — representation-repair idempotency / semantic-preserving repair

- **mechanism:** representation-repair idempotency
- **exact upstream source/function:**
  - `src/metabase/agent_lib/representations/repair.clj` namespace invariant
  - `::repair`
  - `test/metabase/agent_lib/representations/repair_test.clj::idempotency-property-test`
  - `::realistic-query-idempotency-property-test`
  - per-pass idempotency tests including implicit joins and cross-stage repair
- **observed behavior:** Metabase declares repair a fixed point:
  `repair(q) == repair(repair(q))`. The pipeline consists of bounded canonicalization/shape repair,
  metadata-aware field typing and join-disambiguation passes; property tests exercise generic and
  realistic query trees repeatedly. Existing canonical/disambiguated values are generally preserved
  rather than rewritten on subsequent passes.
- **problem solved:** make LLM-authored structured queries recoverable without oscillating across
  retries or accumulating new mutations each time repair runs.
- **Dima equivalent/owner:** Dima does **not** need to rebuild this generic BI repair engine if
  Metabase runtime proves useful. Dima only owns the invariant that repair cannot create new semantic
  authority or change accepted business meaning.
- **Wren equivalent/owner:** Wren dry-plan/compiler currently validates incumbent queries; it does not
  provide this same portable-MBQL repair breadth.
- **disposition:** **METABASE_RUNTIME_CANDIDATE**
- **security/authority effect:** repaired query remains subordinate to Dima accepted authority,
  current Principal and Wren-approved relationship semantics. Fixed-point behavior reduces retry-loop
  risk but is not proof of correctness.
- **semantic duplication risk:** LOW for pure shape canonicalization; HIGH for metadata-aware repairs
  that infer semantic joins/references. DD-24 veto applies.
- **native implementation cost:** HIGH to reproduce robustly; **do not port/transliterate**.
- **Metabase runtime dependency:** YES only if X0 bridge reaches runtime and repair value is material.
- **required executable proof:** for representative bridge artifacts:
  (a) first repair either safely fixes or typed-rejects;
  (b) second repair produces byte/structurally equivalent canonical query;
  (c) accepted Dima metric/dimension/filter/time/ranking meaning is unchanged;
  (d) any join-semantic diff is Wren-approved or rejected;
  (e) quantify how many failures repair fixes vs how much runtime/service complexity it adds.
- **timing:** X0-REST value measurement; potential full-X benefit only after consultation.

### Batch 6 counters

```text
classified in this batch = 3
mechanisms closed        = 19,24,25
cumulative classified    = 25 / 25
remaining                = 0
product code written     = 0
Metabase runtime started = 0
```

