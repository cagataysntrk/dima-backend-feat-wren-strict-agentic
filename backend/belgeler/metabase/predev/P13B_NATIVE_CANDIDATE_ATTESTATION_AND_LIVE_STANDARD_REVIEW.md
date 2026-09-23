# P13B NATIVE CANDIDATE ATTESTATION AND LIVE STANDARD REVIEW

**Milestone:** P13B-0  
**Date:** 2026-09-23  
**Decision:** DMP-DEC-0037  
**Status:** **SEALED / P13B NATIVE ATTESTATION DESIGN / IMPLEMENTATION PENDING SUPERVISOR AUTHORIZATION**

This review is source-audit + predevelopment + governance only.

It does **not** authorize:
- P13B live Standard orchestration;
- an engine gitlink bump;
- an engine source patch;
- Evidence promotion;
- P13 Standard closure.

## 1. Audited state

```text
Platform branch      = feat/dima-metabase-platform
Platform source HEAD = 86faaa339b75d261e31da1dd0dec8939f58620e6

engine repo           = UpcyTech/dima-metabase-engine
engine gitlink        = c56b71ab23bf2a2d266bac2fba8d165ac059d613
engine upstream base  = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime tag           = v0.63.18-dima.0

Fast Track read-only  = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34
ask-v2 read-only      = b069b1cdce097f7ce02c055a2614d8f990b1eb3f
merge/cherry-pick/rebase = 0
```

P13A remains GREEN and is not reopened.

## 2. Binding architecture

```text
Metabase tells us what query it actually built.

Dima decides whether that actual query
is allowed to become business truth.
```

Therefore:

```text
Native Metabot
→ construct_notebook_query
→ exact resolved pMBQL
→ Metabase-native observation/attestation
→ NativeExecutionManifest
→ NativeQueryCandidate
→ Dima mapping/comparison
→ ALLOW | CLARIFY_REPLAN | BLOCK
```

Dima will not parse MBQL recursively in Python and will not recreate Metabase Lib.

## 3. Exact pinned-source audit

All Metabase source conclusions below were read from:

```text
metabase/metabase@
2ba2485c78d7e00a9a25f82c00fc201da71590c4
```

The fork gitlink remains `c56b71ab...`; no engine source was edited during this review.

### 3.1 Native query creation and native state

`src/metabase/metabot/tools/construct.clj`

- `execute-representations-query` repairs the portable query;
- resolves the DB from the first source;
- performs source-table permission checking;
- validates the repaired representation;
- resolves portable FKs to numeric pMBQL;
- checks query-builder runability;
- runs expression-editor diagnostics;
- emits `:structured-output` containing:
  - `:query-id`;
  - exact resolved `:query` pMBQL;
  - portable `:query-json`;
  - result columns.

`src/metabase/metabot/agent/core.clj`

- `extract-queries` reads successful tool `:structured-output`;
- successful `query-id + query` pairs are written to native memory;
- the final state part contains the memory state.

`src/metabase/metabot/agent/memory.clj`

- `remember-query` stores the query at `[:state :queries query-id]`;
- `get-state` exposes that exact native state.

`src/metabase/metabot/persistence.clj`

- persisted structured output explicitly retains `:query-id` and `:query`;
- `finalize-assistant-turn!` writes the final native state to the
  `MetabotConversation.state` row;
- the persisted assistant message retains the successful tool-output identity.

**Conclusion:** the exact query occurrence can be identified server-side by
`conversation_id + native_query_id`. The P13B attestation seam must not accept caller-supplied
semantic facts or a caller-supplied query body as proof.

### 3.2 Metabase Lib inspection surfaces

Pinned source exposes the required bounded inspection primitives:

`src/metabase/lib/database.cljc`
- `database-id`.

`src/metabase/lib/core.cljc`
- `primary-source-table-id`;
- `aggregations`;
- `breakouts`;
- `filters` / `atomic-filters`;
- `joins`;
- `order-bys`;
- `referenced-columns`;
- `stage-count`.

`src/metabase/lib/filter.cljc`
- `atomic-filters`;
- `filter-parts`, which yields typed operator/column/args.

`src/metabase/lib/referenced_columns.cljc`
- resolves column-metadata leaves for filter/aggregation/expression clauses.

`src/metabase/lib/limit.cljc`
- `current-limit`.

This is sufficient for the bounded first vertical. No universal query AST is required.

### 3.3 Explicit and implicit joins

`src/metabase/query_processor/middleware/add_implicit_joins.clj`

The QP turns implicit FK usage into explicit join clauses during preprocessing and stamps
generated joins with:

```clojure
:qp/is-implicit-join true
```

Therefore P13B can distinguish:

```text
explicit joins in exact native pMBQL
vs
implicit joins materialized by native QP preprocessing
```

For the first vertical:

```text
explicit join count = 0
implicit joined table ids = empty
```

is mandatory.

### 3.4 Permission/source observation

`src/metabase/query_processor/preprocess.clj`

The native QP preprocess pipeline resolves source cards/tables, applies enterprise security hooks,
resolves joins, adds implicit joins, normalizes/desugars temporal/filter structures and prepares the
actual QP execution graph.

`src/metabase/query_processor/middleware/permissions.clj`

- permission checks bind to `api/*current-user-id*`;
- `check-query-permissions*` validates the current user's access;
- permission calculation runs after joins, including implicit joins, have been resolved.

`src/metabase/query_permissions/impl.clj`

- `query->source-table-ids` returns the full table-id set used by permission calculation.

**Conclusion:** permission provenance for P13B must be generated in the engine under the same
authenticated Metabase subject. A free-form caller string is not proof.

### 3.5 Exact serialized artifact fingerprint

`src/metabase/lib/serialize.cljc`

`prepare-for-serialization` is the native boundary that removes internal runtime-only data such as
metadata-provider handles while retaining the query that crosses REST/app-DB boundaries.

P13B exact-artifact fingerprint will be defined over:

```text
Metabase prepare-for-serialization(exact stored pMBQL)
→ deterministic recursive key ordering
→ canonical JSON
→ SHA-256
```

This is **not** Metabase cache `query-hash`. The cache hash intentionally removes/reduces some
material such as lib UUID identity and is not an exact query-occurrence identity.

The attestation response must include the exact serialized pMBQL used to compute the fingerprint.
Platform recomputes SHA-256 over the same JSON object and hard-fails on mismatch.

## 4. Existing surface vs required native seam

### Existing surface that is sufficient

The native agent already creates and retains the exact resolved pMBQL. No engine change is needed
to make Metabot produce a second query representation.

### Existing surface that is insufficient

There is no stable current endpoint that, for one native `conversation_id + query_id`, returns all
of these together as typed facts:

- exact query fingerprint;
- exact native producer identity;
- typed aggregation facts;
- typed filter/temporal facts;
- explicit join facts;
- implicit joined-table facts after QP preprocessing;
- material query count for the producing native turn;
- current authenticated Metabase subject;
- typed validation/permission provenance.

The public conversation endpoint intentionally returns flattened chat messages and does not expose
the conversation's native state as a trust API.

**Decision:** P13B query attestation requires a tiny isolated engine seam.

It must observe existing native state and Metabase Lib/QP output. It must not modify:
- run-agent-loop;
- profiles;
- skills;
- tool selection;
- `construct_notebook_query` semantics;
- repair semantics;
- Query Processor semantics;
- drivers.

## 5. Proposed bounded NativeExecutionManifest

This is first-vertical-only, not a universal query AST.

```text
NativeExecutionManifest v1

attestation_id
native_conversation_id
native_query_id
native_assistant_message_id
native_tool_call_id
producer_tool = construct_notebook_query

exact_pmbql_fingerprint
database_id
primary_source_table_id
referenced_source_table_ids

aggregation_count
aggregations[]:
  operator
  referenced_field_ids[]

breakout_count

material_filter_count
temporal_predicates[]:
  time_field_id
  operator
  lower_bound
  upper_bound
  lower_inclusive
  upper_inclusive
  temporal_unit
non_temporal_filter_count

explicit_join_count
implicit_joined_table_ids[]

order_by_count
limit
stage_count
material_query_count

validation:
  producer_structured_output = PASSED
  pmbql_schema = PASSED
  producer_query_id_match = PASSED

permission:
  current_metabase_user_id
  permission_check = PASSED
  checked_source_table_ids[]

runtime_identity:
  repository
  revision_sha
  upstream_base_sha
  runtime_tag
  immutable_image_digest
  runtime_instance_id
```

Transport envelope:

```text
NativeQueryAttestationEnvelope
  exact_serialized_pmbql
  manifest
```

The endpoint input is only the bounded server-side locator:

```text
conversation_id
native_query_id
```

plus normal authenticated HTTP context.

Forbidden input:
- semantic refs;
- authorized resource bindings;
- filter/join counts;
- time fingerprint;
- expected metric;
- expected source;
- expected answer.

Those belong to Dima comparison, not native observation.

## 6. Where each manifest fact comes from

| Manifest fact | Native source |
|---|---|
| query occurrence | persisted native conversation state + persisted successful tool output |
| exact pMBQL | `state.queries[native_query_id]` |
| fingerprint | serialized exact pMBQL, canonical JSON SHA-256 |
| database | `lib/database-id` |
| primary table | `lib/primary-source-table-id` |
| referenced tables | preprocessed graph + `query->source-table-ids` |
| aggregation | `lib/aggregations` + `lib/referenced-columns` |
| breakout | `lib/breakouts` |
| filters | `lib/atomic-filters` + `lib/filter-parts` |
| joins | original `lib/joins` + preprocessed `:qp/is-implicit-join` joins |
| order | `lib/order-bys` |
| limit | `lib/current-limit` |
| stage count | `lib/stage-count` |
| material query count | successful native query-generation tool outputs in the same assistant turn |
| validation provenance | persisted producer tool/output + current schema validation |
| permission provenance | current-user preprocess + `check-query-permissions*` |
| subject | `api/*current-user-id*` |

## 7. Dima mapping boundary

Metabase attests physical/query facts only.

Dima maps them using existing owned truth:

```text
database/table/field ids
→ CurrentCatalogSnapshot
→ exact governed source locator
→ SourceLineage
→ DimaSemanticSpec
→ accepted semantic authority
```

No display-name guessing.
No fuzzy matching.
No label matching.
No case-insensitive fallback outside an existing exact identity contract.

The first vertical uses **Case B bounded physical aggregation verification**:

```text
observed source table
+
observed aggregation operator
+
observed referenced field identity when applicable
→ compare with MetricSpec + SourceLineage
```

No arbitrary formula interpreter.

A complex calculated metric remains a typed gap.

## 8. Temporal attestation

PX-01 remains the first vertical and therefore time is material.

P13B must not copy `ResolvedPeriod` into the candidate.

The engine manifest must report the observed temporal filter facts. For P13B v1, only literal,
first-vertical temporal shapes that can be faithfully represented as bounds are certifiable.

Supported target meaning:

```text
time_field_id = exact field id mapped to satis_siparisleri.acilis_tarihi
lower_bound   = 2026-06-01
upper_bound   = 2026-07-01
interval      = [lower, upper)
```

Equivalent native operator shapes may normalize to that typed material meaning inside the
engine-native attestation seam. Unsupported relative/complex temporal shapes are a typed gap and
cause Dima to BLOCK or CLARIFY/REPLAN; they are not interpreted in Python.

Dima then compares the observed bounds with the accepted `ResolvedPeriod`.

## 9. Material query count

`material_query_count` is not the number of Metabot tool calls.

Search, read_resource, load_skill and similar cognition tools do not count.

For P13B v1 it is the number of successful executable query-generation artifacts in the same
assistant turn. The first vertical requires exactly:

```text
material_query_count = 1
producer_tool         = construct_notebook_query
```

SQL-query-producing tools or a second notebook query cause BLOCK for this vertical.

## 10. Runtime identity audit

Current upstream build identity:

`bin/build/src/build/version_properties.clj`

records:
- release tag;
- only a seven-character git hash.

Current Dima C0 wrapper:

`.dima/docker/Dockerfile.c0`

does not bake an immutable full source identity into the runtime API.

Current P12X C2 workflow can externally pin:
- engine checkout SHA;
- exact image reference/digest when available;
- a local image built from exact checkout as fallback.

That is strong **lab evidence**, but it is not a durable request-relevant production attestation
available to the execution envelope itself.

Therefore current deployment attestation is **INSUFFICIENT as the sole P13B production identity
scheme**.

## 11. Runtime identity decision

Decision:

```text
MINIMAL ENGINE IDENTITY SEAM
```

not a deployment-only scheme.

Proposed endpoint:

```text
GET /api/dima/engine/v1/identity
```

It exposes immutable/non-business facts only:

```text
repository
revision_sha              # exact 40-char runtime source SHA
upstream_base_sha
runtime_tag
build_identity
immutable_image_digest
runtime_instance_id
```

Design constraints:
- `revision_sha`, upstream base and release/build identity are baked into the Dima image/build
  manifest, not inferred from the seven-character Metabase version hash;
- immutable image digest is deployment-provided from the image actually launched and is mandatory
  in the certified production profile;
- `runtime_instance_id` is process/instance-scoped and changes on restart;
- missing or malformed full SHA/image/instance facts fail closed.

Required chain:

```text
candidate.runtime_identity
==
attestation runtime identity
==
runtime used by /api/dataset
==
receipt runtime identity
```

The Platform gitlink is checked independently against the certified runtime revision/build mapping.

No business or query logic belongs in the identity endpoint.

## 12. Exact same-artifact execution seam

Pinned source conclusion:

```text
POST /api/dataset = ACCEPTED P13B EXECUTION SEAM
```

Evidence from pinned source:

`src/metabase/query_processor/api.clj`
- POST `/` under the `/api/dataset` route accepts MBQL;
- it passes the submitted query to `qp/userland-query-with-default-constraints`;
- then executes through `qp/process-query`;
- execution info binds `executed-by` to `api/*current-user-id*`.

`src/metabase/lib_be/schema.clj`
- API-bound MBQL is normalized as MBQL5, not re-authored through Agent API.

`src/metabase/query_processor.clj`
- userland wrapping adds server-owned execution middleware/default constraints;
- it does not call Metabot or Agent API to reconstruct analytical intent.

Therefore the P13B execution rule is:

```text
Native attestation returns exact_serialized_pmbql A
→ Platform fingerprints A
→ Dima authorizes A
→ Platform POSTs A directly to /api/dataset
→ QP executes A under the same authenticated Metabase subject
```

QP-owned permission/security/preprocess/default-limit middleware is execution machinery, not a new
analytical author.

Forbidden:
- authorize A → Agent API construct-query → B;
- authorize A → SQL conversion → execute SQL;
- Agent API fallback;
- Wren fallback.

## 13. Engine patch required?

```text
YES — but only after supervisor authorization.
```

Reason:
- exact native query exists already;
- existing endpoint surfaces do not provide the bounded typed attestation manifest;
- current runtime API does not expose full request-relevant source/image/instance identity.

Proposed minimum engine patch surface:

```text
NEW:
src/metabase/dima/native_attestation.clj
src/metabase/dima/api.clj
test/metabase/dima/native_attestation_test.clj
test/metabase/dima/api_test.clj

MINIMAL REGISTRATION:
src/metabase/api_routes/routes.clj

BUILD-IDENTITY WRAPPER ONLY:
.dima/docker/Dockerfile.c0
```

The Dima namespace may read existing Metabot persistence/state, Lib, QP preprocess and permission
functions.

It may not edit native cognition/query semantics.

If implementation discovers that a required fact cannot be obtained without modifying
`construct_notebook_query`, run-agent-loop, repair or QP semantics:

```text
STOP-THE-LINE
```

and return for architecture review.

## 14. Future Platform owner and dependency quarantine

Future P13B live orchestration owner is reserved as:

```text
backend/app/v3/native_standard/
```

That future hot path may use:
- native engine bridge/attestation transport;
- `NativeExecutionManifest`;
- `NativeQueryCandidate`;
- P10 issuer;
- P5 receipt sealer;
- Evidence owner after separately authorized implementation.

It may not import/use:
- `app.v3.substrate.metabase.compiler`;
- `app.v3.substrate.metabase.canonical` for construction/introspection;
- `app.v3.substrate.metabase.execution_adapter`;
- `MetabaseAgentClient`.

The existing `native_execution.py` `CanonicalProjection` compatibility adapter is explicitly
grandfathered and is not moved for cosmetic dependency purity.

Platform governance is updated in P13B-0 to enforce this rule only when the future
`native_standard/` path exists.

## 15. Tests designed now

P13B implementation must include at least:

1. caller copies expected semantic ref without native evidence → cannot authorize;
2. caller copies expected source binding without native evidence → cannot authorize;
3. fake time fingerprint → cannot authorize;
4. hidden filter while caller claims zero → manifest observes filter → BLOCK;
5. implicit join while caller claims zero → manifest observes joined source → BLOCK;
6. native exact-query fingerprint != manifest fingerprint → HARD FAIL;
7. manifest fingerprint != Platform candidate fingerprint → HARD FAIL;
8. candidate engine SHA != live runtime attestation SHA → HARD FAIL;
9. authorized image digest != runtime image digest → HARD FAIL;
10. artifact runtime != receipt runtime → HARD FAIL;
11. authenticated Metabase subject mismatch → HARD FAIL;
12. authorized pMBQL mutation before `/api/dataset` → HARD FAIL;
13. second material native analytical query → BLOCK;
14. SQL query producer on first vertical → BLOCK;
15. explicit join → BLOCK;
16. implicit joined source → BLOCK;
17. non-temporal arbitrary filter → BLOCK;
18. observed temporal bounds differ from accepted period → BLOCK;
19. result differs from independent oracle → no VERIFIED Evidence;
20. native prose before receipt/evidence → never official numeric truth.

## 16. First live Standard vertical

Selected:

```text
PX-01
question:
Haziran 2026'da kaç satış siparişi açıldı?

physical source:
satis_siparisleri

physical aggregation:
COUNT(*)

material time field:
acilis_tarihi

accepted period:
[2026-06-01, 2026-07-01)

expected independent scalar:
126
```

Frozen oracle source:

`backend/lab/metabase/p12x/corpus_v1.json`

```sql
SELECT COUNT(*)::BIGINT AS siparis_sayisi
FROM satis_siparisleri
WHERE acilis_tarihi >= DATE '2026-06-01'
  AND acilis_tarihi < DATE '2026-07-01'
```

Oracle execution owner:

`backend/lab/metabase/p12x/build_oracle.py`

It reads the frozen Boyahane DuckDB independently of Metabot/query-under-test.

P12X C2 live proof `35839639339` independently observed:

```text
observed_scalar = 126
oracle_scalar   = 126
```

P13B will not use the query under test to generate its expected answer.

Semantic verification strategy:
- the accepted Dima metric remains canonical business truth;
- observed `COUNT(*)` + exact source table is compared against its `MetricSpec + SourceLineage`;
- no assumption is made that a managed Metabase metric resource already exists;
- no metric formula is authored independently in Metabase.

## 17. Native prose rule

Native Metabot text is model candidate output only.

Official numeric answer requires:

```text
authorized exact artifact
→ access snapshot
→ exact /api/dataset execution
→ DimaQueryReceipt
→ independent correctness gate
→ VERIFIED EvidenceArtifact
```

P13B-0 implements none of those live orchestration steps.

## 18. Open blockers/debt

Still open:

```text
DMP-P13B-BLOCK-001 native candidate fact provenance
  = DESIGN SEALED / IMPLEMENTATION OPEN

DMP-P13B-BLOCK-002 artifact ↔ running runtime identity
  = DESIGN SEALED / IMPLEMENTATION OPEN

DMP-P5-BLOCK-001
DMP-P11-INTEGRATION-005          # P13C owner
EV-05 / EV-06 / EV-07
P10B2 RLS / CLS / impersonation / advanced routing / cache-result reauthorization
P9 dimension / time / relationship transport gaps
P7/P8 relationship / calculated / view semantic gaps
historical Wren typed gaps
```

No P13C textual/entity-value integration.
No high-cardinality resolver.
No fuzzy matching.
No relationship support.
No P14/Research.

## 19. P13B-0 closure

```text
P13B NATIVE ATTESTATION DESIGN = SEALED
P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
```

Do not claim:
- P13B GREEN;
- P13 Standard GREEN;
- production security GREEN;
- native correctness GREEN.


---

## P13B-0 CLOSURE PROOF

Predevelopment/governance commit:
`90c6da7d5bf50c305f4d91c02263660bf8b9232a`

Governance:
`35852118661 = SUCCESS`

Verified after push:
```text
changed files                    = docs/governance only
product-code changes             = 0
engine-source changes            = 0
engine gitlink bump              = 0
engine gitlink                   = c56b71ab23bf2a2d266bac2fba8d165ac059d613
ask-v2/Fast Track writes         = 0
live P13B orchestration          = 0
```

Certified closure wording:
```text
P13B NATIVE ATTESTATION DESIGN = SEALED
P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
```
