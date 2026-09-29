# DIMA R5 — Material Semantic Observation Engine Proposal

Date: 2026-09-29

Status:

```text
PROPOSAL ONLY
NO ENGINE IMPLEMENTATION AUTHORIZED
CANONICAL ENGINE REMAINS dima.6
R5 = IN_PROGRESS / BLOCKED ON SUPERVISOR ENGINE DECISION
```

## 1. Authority and problem

R5 restores the DMP-DEC-0048 split:

```text
Metabase executes legal native query A.
P13 exact attestation remains a strict certification/debug/forensics microscope.
Ordinary Research execution does not use P13 as an execution permission gate.
Dima promotes a result to VERIFIED Evidence only after material request semantics match.
```

The regression was introduced by `3b33639f934bb67d292de14b5142ea129dc9e65e`,
which inserted `NativeResearchMaterialExecutor._attest_scope()` before
`bridge.execute_dataset(...)`. The later locator correction
`6308b705e3c61aaa36825493421cde8288744561` fixed bridge correlation but did not remove the
mandatory P13 hot-path dependency.

Immutable Terra V3 run `36481553724`, artifact `10996548690`, demonstrated two ordinary
Research occurrences that were stopped before any material execution:

1. `NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED` for `absolute-datetime`;
2. `NATIVE_METRIC_EXPANSION_UNSUPPORTED` with one governed native metric reference and three
   physical aggregations.

These are reproduction classes, not production semantic special cases.

## 2. Provider-free regression proof

Platform test commits:

- `2fb8e5d54bf07c8c78e18ec98fa631754d27ad60` — reproduces the mandatory P13 hot-path gate for
  both immutable V3 failure families and proves `/api/dataset` is not reached;
- `f8f8b21fa4380a13715a9e5e2f993cdae492f0f3` — proves the historical DMP-DEC-0048 sequence can
  durably traverse
  `CANDIDATE_CAPTURED -> EXECUTION_STARTED -> exact dataset execution -> EXECUTED -> one
  DimaQueryReceipt` without a P13 call.

No Product behavior was changed by either commit.

Provider-free receipts on the corrected proof HEAD:
- Phase-1 focused `36522384031 = SUCCESS`;
- governance `36522384015 = SUCCESS`;
- Core-B focused `36522384035 = SUCCESS`;
- Core-B provider-free seal `36522384032 = SUCCESS`;
- Core-A final `36522384072 = SUCCESS`.

## 3. Existing dima.6 / Metabase-native surface audit

### 3.1 Exact dataset execution

Existing surface:

```text
POST /api/dataset
```

Strengths:
- principal-scoped Metabase permission authority;
- executes exact captured query A;
- normal dataset result;
- current Platform bridge already checks the exact query fingerprint.

Gap:
- it does not expose a typed material-semantic observation of the query occurrence.

### 3.2 Query metadata

Existing public surface:

```text
POST /api/dataset/query_metadata
```

Metabase internally walks the query and returns dependent:
- databases;
- tables;
- fields;
- snippets.

This is useful metadata but insufficient for R5 correctness. It does not tell Dima, as a stable
typed material contract:
- which governed native metric identity was used;
- which dimension is breakout vs filter vs ranking target;
- filter values/material entity scope;
- canonical temporal lower/upper bounds and inclusivity;
- ranking target/direction/limit;
- requested temporal grain.

### 3.3 Metabot construct_notebook_query structured output

Metabot already returns:
- `query-id`;
- resolved pMBQL `query`;
- portable `query-json`;
- `result-columns`.

That is sufficient for Metabase itself to execute and reason about its query. It is not an
authorized R5 observation surface for Platform. Extracting material semantics from `query` or
`query-json` in Python would create an MBQL/query-shape parser and a second interpretation
authority.

### 3.4 P13 exact attestation

Existing P13 surface can expose physical implementation facts, but R5 explicitly requires it to
remain a strict microscope rather than ordinary Research permission middleware. Reusing it as the
production material observer would preserve the architectural regression.

## 4. Why existing surfaces cannot satisfy the required contract

The missing facts are **observed usage facts**, not expected catalog facts. Dima already has:
- accepted `AnalyticalRequestContract`;
- `NativeResourceBinding`;
- Research scope lineage/version;
- Dima principal and `NativeSubjectBinding`;
- exact captured query fingerprint.

Those sources can establish expected identity and correlation, but they cannot prove that the
native query occurrence actually used the accepted metric, material filter/time scope, ranking and
grain.

The only existing objects containing that information are Metabase query representations. Platform
must not parse those representations.

Therefore:

```text
NO EXISTING dima.6 PUBLIC/NATIVE SURFACE
PROVIDES THE COMPLETE R5 MATERIAL OBSERVATION CONTRACT
WITHOUT EITHER:
1. REUSING P13 AS THE HOT-PATH MICROSCOPE, OR
2. PARSING MBQL/query-json IN PLATFORM.
```

Both alternatives are forbidden.

## 5. Minimal proposed engine surface

Supervisor authorization is required before implementation.

Conceptual endpoint:

```text
POST /api/dima/engine/v1/native-query-material-observation
```

Request identity only:

```json
{
  "conversation_id": "<principal-scoped Metabot conversation UUID>",
  "native_query_id": "<persisted construct_notebook_query occurrence id>"
}
```

The endpoint must resolve the already-persisted successful native occurrence under the current
Metabase user and return a read-only semantic projection produced inside Metabase, where the query
representation is natively understood.

Proposed output family:

```text
schema_version
native_conversation_id
native_query_id
native_assistant_message_id
native_tool_call_id
query_fingerprint
database_id
authenticated_metabase_subject

used_native_metrics:
  stable native metric id/entity-id only

material_dimensions:
  stable table/field identity
  material role only (breakout/filter/ranking)
  requested grain when present

material_filters:
  stable field/resource identity
  canonical material value/scope
  no physical operator implementation leakage

material_temporal_bounds:
  stable time-dimension identity
  canonical start
  canonical end
  lower/upper inclusivity
  timezone meaning only when material

material_ranking:
  target identity
  direction
  limit

provenance:
  runtime identity
  exact occurrence identity
```

Platform may then compose these engine-observed facts with Dima-owned:
- tenant/principal correlation;
- `NativeResourceBinding` expected identities;
- accepted `AnalyticalRequestContract`;
- scope lineage/version.

## 6. Explicit exclusions

The proposed surface must not expose or make Product authority over:
- physical aggregation count;
- aggregation implementation/operator;
- metric formula algebra;
- JVM date classes;
- stage topology;
- preferred MBQL shape;
- join-plan quality;
- query optimality.

It must not:
- plan or rewrite a query;
- repair a query;
- execute a second analytics engine;
- compute Dima business metrics;
- introduce benchmark-specific behavior;
- parse SQL/MBQL in Platform;
- weaken P13 forensic strictness.

## 7. Why this is generic

The contract is representation-independent. It asks Metabase to report the **material meaning it
already resolved**, not to teach Dima every physical representation one by one.

Consequently:
- one native metric may expand to any legal physical aggregation topology without creating extra
  Dima metrics;
- legal Metabase date representations normalize to canonical material bounds inside Metabase;
- new internal MBQL/JVM representations do not require corresponding Python semantic branches.

## 8. Required validation if separately authorized

Before any paid validation, a future implementation must prove provider-free:

1. P13 can still reject unsupported physical shapes.
2. The same legal query can execute ordinary Research without a P13 permission call.
3. Evidence promotion succeeds only when the material observation matches the accepted request.
4. June -> all-period, department narrowing loss, metric substitution, ranking-target substitution,
   and scope-lineage mismatch all block VERIFIED Evidence.
5. Principal, tenant, engine identity and query fingerprint mismatches remain fail-closed.
6. `CANDIDATE_CAPTURED -> EXECUTION_STARTED -> EXECUTED` idempotency remains unchanged.
7. Platform contains no SQL/MBQL parser, metric-formula interpreter, representation-specific date
   switch, regex/fuzzy/morph semantic authority or benchmark branch.

## 9. Current disposition

```text
engine change required? = YES, for a new generic material-observation surface
engine implementation   = NOT AUTHORIZED
canonical engine         = cbe313af9ac2d5960f662068e433d328d896fb06
release                  = 0.63.18-dima.6
paid/model calls in R5   = 0
V4                       = NOT RUN
RCA_P19_HARD_V2          = NOT RUN
FINAL P13                = BLOCKED
DIMA BRAIN V1            = NOT SEALED
```
