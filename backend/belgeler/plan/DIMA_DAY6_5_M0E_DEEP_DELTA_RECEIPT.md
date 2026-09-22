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

