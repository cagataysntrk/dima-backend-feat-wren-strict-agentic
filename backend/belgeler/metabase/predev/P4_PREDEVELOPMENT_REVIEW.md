# P4 — PRE-DEVELOPMENT REVIEW

**Milestone:** P4 — ResolvedAnalyticsIntent → Metabase canonical structured query  
**Branch:** `feat/dima-metabase-platform`  
**P3 certified implementation:** `7a4d1d12e59b52edf8493c0aa0b147947ff4ecf9`  
**P3A result:** `PASS_B_SEAM`  
**P3A proof HEAD:** `480ea9a12c8a23458319df445c34ec67ef720695`  
**P3A closure:** `51ca847163dc0564c1bdb458ac5abcf8744102d4`  
**Metabase runtime:** `v0.63.18` / immutable digest pinned  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY

Status: SEALED / P4 IMPLEMENTATION AUTHORIZED AFTER GOVERNANCE GREEN

## 1. Normative P4 flow re-read

```text
AcceptedStandardAuthority
→ sealed StandardProjection
→ Dima semantic-handle resolution exactly once
→ ResolvedAnalyticsIntent
→ MetabaseProjectionCompiler
→ SourceLineage + current catalog snapshot
→ deterministic portable MBQL
→ Metabase validate / repair / resolve
→ canonical serialized MBQL
```

Hard invariants:
- execution projection hash stays the sealed authority projection hash;
- semantic meaning comes from Dima, not Metabase labels/search;
- Metabase compiler resolves zero Dima semantic handles;
- portable refs are never LLM-invented;
- source rename/rebind drift is fail-closed;
- unapproved implicit joins = 0;
- silent field drop = 0.

## 2. P3A promotion rule — no parallel contract

P3A proved the architecture with prototype contracts. P4 must **promote, not fork** them.

Production ownership:
```text
backend/app/v3/substrate/metabase/execution_binding.py
backend/app/v3/substrate/metabase/compiler.py
backend/app/v3/substrate/metabase/canonical.py
```

P3A modules become test/preflight consumers or compatibility re-exports of production primitives.
There must not be one P3A binding model and a second P4 binding model with independent semantics.

## 3. Execution-binding identity

Accepted seam remains:

```text
ResolvedAnalyticsIntent
+ immutable Dima-owned execution binding snapshot
→ MetabaseProjectionCompiler
```

Rules:
- `source_candidate_id` is a context-scoped lookup key only;
- durable semantic identity is `MetricSpec.metric_id` / `DimensionSpec.dimension_id`;
- `canonical_name`, display labels and `source_scopes` are never physical locators;
- period/time compatibility keys require an explicit Dima-owned mapping;
- request text/source text are provenance only and never compiler input.

## 4. Current-catalog anti-drift contract

`SourceLineage` expresses expected Dima lineage but names alone are not enough for silent-rebind safety.

P4 therefore requires an immutable current catalog snapshot keyed by `SourceLineage.source_id`.

Conceptually:

```text
CurrentCatalogObject
  source_id
  database_ref
  schema_name
  table_name
  column_name
  resource_entity_id?
  resource_fingerprint
```

Before emitting a portable ref:
1. stable semantic id resolves to Dima SourceLineage;
2. SourceLineage.source_id must exist in current catalog snapshot;
3. expected and current DB/schema/table/column must match exactly;
4. resource fingerprint is carried into compiler proof material;
5. mismatch is `SOURCE_LINEAGE_DRIFT`, never a search/rebind attempt.

A current Metabase metadata read may validate a physical binding, but may not choose business meaning.

## 5. Portable → canonical proof

Pinned v0.63.18 `/api/agent/v2/construct-query` runs
`validate → convert → repair → resolve` and returns base64 serialized MBQL.

P4 will:
- emit canonical portable syntax itself;
- call `construct-query`;
- decode the returned base64 JSON locally only for structural proof;
- construct the same portable query twice and require deterministic canonical serialization;
- compare a Dima-owned semantic-slot manifest before/after canonicalization.

Manifest at minimum tracks:
```text
source count
aggregation count/type
breakout count
filter leaf count
time predicate count
comparison query count
ranking/order presence
limit
explicit join count
semantic ids
source fingerprints
```

If a required semantic slot disappears, changes cardinality, or an unexpected join appears:
fail `SILENT_FIELD_DROP_OR_REWRITE`.

This structural proof is not P8 numeric equivalence.

## 6. Filter/literal contract audit

Current `ResolvedFilterRef` carries `source_candidate_id`, `dimension_name`, and `value: str`;
the certified Wren path treats that payload as equality.

P4 must not invent predicate/operator/literal typing.

Safe now:
- categorical equality whose Dima DimensionSpec identifies a textual field;
- multiple equality filters;
- numeric metric aggregation from MetricSpec + SourceLineage;
- `schema_name = null` in a portable FK, preserved as JSON null.

Not yet proven by the current intent contract:
- SQL/semantic NULL predicate such as IS NULL / IS NOT NULL;
- typed numeric filter literal if upstream only supplies an untyped string;
- non-equality filter operators.

P4 fails closed for those cases instead of parsing strings such as `"null"` or `"42"`.
Metabase coercion/repair is not semantic authority.

## 7. Relationship scope

P3A proved same-table representative families only.

P4 initial compiler:
- same-table source lineage: allowed;
- cross-table lineage without an explicit approved Dima relationship path: fail closed;
- Metabase implicit FK auto-fill: forbidden;
- physical FK metadata is not Dima relationship authority.

Approved cross-table compilation requires a later explicit
`ApprovedRelationshipPath ↔ RelationshipSpec` proof and dedicated tests.

## 8. Formula scope

Simple mechanical aggregations proven in P3A may be promoted.
Arbitrary `MetricSpec.formula` translation remains fail-closed and belongs to later
semantic-equivalence work unless separately proven.

## 9. P4 allowed files

```text
backend/app/v3/substrate/metabase/execution_binding.py
backend/app/v3/substrate/metabase/compiler.py
backend/app/v3/substrate/metabase/canonical.py
backend/app/v3/substrate/metabase/p3a_models.py
backend/app/v3/substrate/metabase/p3a_preflight.py
backend/app/v3/substrate/metabase/p3a_fixture.py
backend/tests/test_v3_p4_metabase_*.py
backend/tests/test_v3_p3a_bridge_preflight*.py
.github/workflows/dima-metabase-p4.yml
backend/belgeler/metabase/predev/P4_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P4_METABASE_PROJECTION_COMPILER.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

## 10. P4 forbidden files absent a new receipt

```text
backend/app/v2/**
backend/app/v3/analytics_contract.py
backend/app/v3/semantic_spec.py
backend/app/v3/authority.py
backend/app/v3/substrate/wren.py
backend/app/routers/**
backend/app/main.py
backend/app/config.py
docker-compose.yml
backend/lab/docker-compose.yml
WrenAI-main/**
feat/ask-v2-mvp
```

If P4 later proves the Dima intent contract itself must change, STOP and open a new
Decision/Failure Receipt before touching these files.

## 11. P4 focused proof matrix

Required:
- metric-only;
- breakdown;
- categorical equality filter;
- time;
- previous-period comparison;
- ranking;
- limit;
- multi-filter;
- nullable-schema portable ref;
- numeric metric lineage;
- missing candidate binding;
- missing time binding;
- source-lineage drift;
- cross-table unapproved relationship;
- arbitrary formula unsupported;
- untyped numeric/null predicate fail-closed.

Required invariants:
```text
semantic handle resolution in compiler = 0
Metabase search as semantic locator     = 0
label/name guessing                     = 0
portable ref invention                  = 0
silent source rebind                    = 0
implicit join                           = 0
silent field drop                       = 0
canonicalization deterministic          = 1
product routing change                  = 0
```

## 12. Exit semantics

P4 can close GREEN only for semantics actually represented and proven.
Unsupported semantic NULL/typed numeric/non-equality filter behavior remains explicitly fail-closed
unless an upstream typed-filter contract is separately authorized and proven.

P4 GREEN does not mean P5 receipt completion, P8 Wren/Metabase equivalence, security parity,
Metabase primary routing, or Wren retirement.

## 13. Authorization

After this review commit is governance GREEN, P4 implementation may begin only in the allowlist.
No production front-door routing is authorized.


---

## 14. Compiler implementation sub-gate review — SEALED

**Binding implementation HEAD:** `1771becb3e59395cf28f993345703449feb9a98d`  
**Binding closure commit:** `2c736fa0030c1b025349c56c739b30a0a68983d7`  
**Binding workflow:** `35742516216 = SUCCESS`  
**Binding governance:** `35742964747 = SUCCESS`

Status: **SEALED / COMPILER IMPLEMENTATION AUTHORIZED**

Before compiler code, the P4 roadmap, architecture report, this review, production
`execution_binding.py`, and pinned Metabase v0.63.18 representation source were re-read.

### Exact pinned-runtime contract revalidated

v0.63.18 `POST /api/agent/v2/construct-query`:
1. accepts a portable external-query object;
2. evaluates the representations pipeline;
3. performs validation/conversion/repair/resolution;
4. prepares the resolved MBQL query for serialization;
5. JSON-encodes it;
6. base64-encodes that JSON into response `query`.

The repair layer is capable of implicit-join source-field insertion. Therefore P4 proof must inspect
the returned canonical query for both:
- explicit `joins`;
- any `source-field`, `source-field-name`, or `source-field-join-alias` options.

Either is forbidden in the initial same-table P4 compiler.

### Production compiler split

```text
compiler.py
  pure Dima intent/binding → portable MBQL
  no HTTP
  no Metabase search/read-resource
  no semantic handle resolution
  no raw user language

canonical.py
  portable MBQL → client.construct_query
  exact double-construction determinism proof
  base64 JSON decode for structural proof only
  semantic-slot manifest comparison
  canonical query fingerprint
```

### Supported semantics in the first production slice

- exactly one metric;
- simple mechanical aggregation: count/sum/avg/min/max/distinct;
- same-table dimensions/breakdowns;
- textual categorical equality filters;
- multiple textual equality filters;
- resolved period bounds;
- previous-period comparison as base/reference query steps;
- ranking by aggregation index plus limit;
- nullable schema in portable references;
- numeric metric aggregation lineage.

### Explicit fail-closed semantics

- zero or multiple metrics;
- arbitrary metric formula;
- filter value `"null"` where the upstream contract cannot distinguish a semantic NULL predicate;
- non-textual dimension filter with untyped string value;
- non-equality predicate (not represented upstream);
- any approved relationship path in this initial same-table slice;
- any cross-table lineage;
- any grain constraint not represented by this compiler;
- missing candidate/time/current-catalog binding;
- source-lineage drift;
- any compiler attempt to use canonical/display names or `source_scopes` as locators.

### Semantic-slot manifest

The plan/canonical proof records at minimum:
- query count;
- source count;
- aggregation operator sequence;
- breakout count;
- filter leaf count;
- time predicate count;
- comparison query count;
- ranking/order count;
- per-query limit values;
- explicit join count;
- implicit-join source-field option count;
- stable Dima semantic ids;
- governed current-catalog resource fingerprints.

Canonicalization fails `SILENT_FIELD_DROP_OR_REWRITE` if structural counts/operators/limits change or
if any join/implicit-join reference appears.

### Determinism

For every portable query step P4 calls `construct-query` twice with the same input.

Required:
```text
serialized_query_call_1 == serialized_query_call_2
```

Mismatch is `NON_DETERMINISTIC_CANONICAL_SERIALIZATION`.

This is stronger than merely hashing sorted decoded JSON and is intentionally tied to the pinned
v0.63.18 runtime.

### Safety evidence policy

P4 does **not** inherit P3A's default-zero `BridgeSafetyCounters` as proof.
Safety is established by actual code-path restrictions + negative tests + canonical manifest checks.

### Compiler gate

Compiler/canonical implementation is now authorized only in the P4 allowlist. Product routing,
P5 receipt completion, P8 numeric equivalence, security parity and Wren retirement remain out of scope.


---

## 15. Filter sentinel clarification

DMP-DEC-0014 clarifies the filter/literal rule:

```text
text dimension + ResolvedFilterRef.value:str
→ literal equality payload
```

The compiler must not infer semantic NULL/operator/type from token spelling. Therefore `"NULL"`
remains a literal text value. Semantic NULL remains unavailable until an explicit typed upstream
filter contract is separately authorized.

The existing non-textual untyped-filter fail-closed rule remains unchanged.
