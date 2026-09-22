# P3 / P3A — PRE-DEVELOPMENT REVIEW

**Milestones:** P3 Metabase client/adaptor boundary + P3A semantic-duplication bridge preflight  
**Branch:** `feat/dima-metabase-platform`  
**M1 certified SHA:** `17942f179b13fd2cb81fd284789ba0f6366d2ed8`  
**M2 certified runtime SHA:** `a05bd12ff56ac3c66eef01f7340c1f991ae07681`  
**M2 closure commit:** `4f4b7a8760403e7175faff3fbec34c484bff3f9b`  
**Metabase runtime:** `v0.63.18`  
**Metabase image:** `metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY

Status: SEALED / P3 TRANSPORT IMPLEMENTATION AUTHORIZED AFTER GOVERNANCE GREEN

## 1. Normative sources re-read

Roadmap:
- P3 client/adaptor boundary;
- REST/Agent API primary candidate; MCP remains a separate optional lab surface;
- allowed initial capabilities: metadata inspect, construct/validate, execute, read resource,
  execution identity/continuation;
- forbidden initially: arbitrary admin mutation, raw SQL, dashboard write, semantic mutation;
- healthy process != usable Agent API;
- typed transport/auth/permission/query/resource/timeout/internal errors;
- P3A asks whether a Dima-accepted semantic request can reach structured Metabase execution
  without raw-language reparse, semantic redefinition, label guessing or a second authority;
- candidate B (`ResolvedAnalyticsIntent`) is the initial hypothesis;
- P3A hard-zero counters remain release blockers.

Architecture report:
- R3.2 validate→repair→resolve query representations;
- R3.3 durable receipt identity is Dima-owned, not a query/session handle;
- R3.16 REST serialized query, continuation token and MCP query handle are different lifecycles;
- R3.17 implicit FK repair touches relationship authority and is fail-closed unless Dima-approved;
- R3.18 repair must preserve meaning and be idempotent/bounded;
- R3.23 Agent API availability is a runtime capability;
- R3.24 canonical query representation/hash is durable; continuation is ephemeral;
- R3.25 row/page budgets are runtime-observed;
- R6/R6.1 DimaSemanticSpec owns meaning and semantic handles resolve before substrate execution.

## 2. Pinned v0.63.18 source/runtime rechecked

Exact v0.63.18 source confirms:
- `/api/agent/v1/ping`;
- `/api/agent/v1/read-resource`;
- `/api/agent/v1/search`;
- `/api/agent/v2/construct-query`;
- `/api/agent/v1/execute`;
- `/api/agent/v2/query`;
- portable MBQL 5 uses explicit DB/schema/table/field references;
- query representations are validated/repaired/resolved before execution;
- combined-query page size = 200 and total cap = 2000 in this runtime;
- raw SQL has a distinct `/v1/execute-sql` path and an explicit kill switch.

M2 live evidence confirms those structured surfaces work on the pinned image and raw SQL is disabled.

## 3. Current Dima v3 boundary rechecked

M1 provides:
- Dima-owned `ResolvedAnalyticsIntent`;
- exact authority/projection/resolved-intent hashes;
- source candidate provenance;
- Dima-owned `DimaSemanticSpec` shells including `SourceLineage`, `MetricSpec`,
  `DimensionSpec`, `RelationshipSpec`;
- `AnalyticsSubstrate` contract;
- no Metabase dependency in core.

Critical P3A observation:
`ResolvedAnalyticsIntent` intentionally does not contain Metabase portable FKs.
Therefore the Metabase bridge may not derive physical references by label/name guessing.
It requires a separate Dima-owned governed lineage/catalog snapshot.

This is not a defect to patch pre-emptively. It is the P3A question.

## 4. Candidate seam disposition before prototype

### A — StandardProjection + opaque handles
Rejected as the substrate seam.

Reason:
using opaque handles would force Metabase-side code to resolve Dima semantic handles, violating
M1/R6.1. Handle resolution belongs before the substrate.

### B — Dima-owned ResolvedAnalyticsIntent
**Only authorized P3A prototype candidate. Not yet accepted.**

Prototype may additionally consume a Dima-owned immutable lineage/execution snapshot keyed by
governed semantic identity. That snapshot may carry physical DB/schema/table/field lineage and
Dima-owned aggregation semantics; it may not contain Metabase-authored business meaning.

### C — Wren-specific planned representation
Rejected as canonical seam.

Reason:
it would preserve Wren object/query identity as Dima's execution contract and defeat engine independence.

## 5. What P3 is allowed to build

Transport-only package:

```text
backend/app/v3/substrate/metabase/
  __init__.py
  client.py
  models.py
  errors.py
  telemetry.py
  adapter.py
```

P3 adapter is a runtime/transport boundary only. It does **not** compile
`ResolvedAnalyticsIntent` into Metabase query semantics yet.

Allowed methods:
- process health;
- Agent API ping/capability handshake;
- metadata search/read-resource;
- construct portable query supplied by a caller;
- execute serialized query;
- combined query + continuation;
- typed inspection/telemetry.

Forbidden methods:
- execute SQL;
- create/update metric/model/question/dashboard/collection;
- arbitrary admin setting mutation;
- semantic handle resolution;
- raw user language;
- field/metric label guessing.

## 6. P3A prototype rules

P3A begins only after P3 transport gate is GREEN.

Representative families:
1. metric;
2. metric+dimension;
3. metric+filter;
4. metric+period;
5. previous-period comparison;
6. ranking/limit;
7. two compatible dimensions;
8. filter+period+dimension.

Hard counters:
```text
raw_user_language_reinterpretation = 0
manual_metric_redefinition         = 0
manual_relationship_redefinition   = 0
metabase_label_name_guessing       = 0
unapproved_implicit_fk_join        = 0
second_semantic_authority          = 0
```

A deterministic representation compiler is allowed only if all business meaning comes from
Dima-owned accepted semantics + Dima-owned lineage/spec inputs. If it needs a parallel Metabase
semantic definition table, label heuristics, redefined metric formulas or relationship truth, the
structured-execution arm is rejected at P3A.

## 7. Identity gap to measure, not hide

Current v3 semantic refs include context-bound `semantic_ref` handles and
`source_candidate_id`. Candidate IDs include context version and are not durable global Dima
semantic IDs.

Therefore:
- P3 transport work is unblocked;
- P3A must explicitly measure whether a stable Dima-owned identity/lineage snapshot can be provided
  without mutating meaning or creating a second semantic owner;
- no compiler may silently key durable bindings by display label/canonical-name guess;
- if P3A requires a v3 contract correction, STOP and open a Decision/Failure Receipt before changing
  M1 contracts.

## 8. P3 files allowed to touch

```text
backend/app/v3/substrate/metabase/**
backend/tests/test_v3_p3_metabase_*.py
.github/workflows/dima-metabase-p3.yml
backend/pyproject.toml              # only explicit httpx production dependency if needed
backend/belgeler/metabase/predev/P3_P3A_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P3_METABASE_CLIENT_BOUNDARY.md
backend/belgeler/metabase/tickets/P3A_BRIDGE_PREFLIGHT.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

## 9. P3 files forbidden

```text
backend/app/v2/**
backend/app/routers/**
backend/app/main.py
backend/app/config.py
backend/app/v3/analytics_contract.py     # unless a new receipt explicitly authorizes correction
backend/app/v3/semantic_spec.py          # unless a new receipt explicitly authorizes correction
backend/app/v3/authority.py
backend/app/v3/substrate/wren.py
docker-compose.yml
backend/lab/docker-compose.yml
WrenAI-main/**
feat/ask-v2-mvp
```

The isolated M2 lab may be consumed by P3 CI but its certified files should not be changed unless a
runtime-harness failure is separately classified.

## 10. P3 exit gate

```text
typed error taxonomy                         PASS
REST Agent API only                          PASS
raw SQL method exposed                       0
admin mutation method exposed                 0
semantic handle import/resolution             0
raw user language dependency                  0
health != Agent API availability              proven
construct/read/execute/query/continuation      live PASS
serialized query vs continuation separation   PASS
runtime page limit observed, not guessed       PASS
M2 runtime remains GREEN                       PASS
v2/Wren behavior drift                         0
source branch writes                           0
```

## 11. Authorization

This review authorizes P3 transport-only implementation after governance GREEN.
It does **not** authorize the P3A representation compiler yet. P3A implementation requires P3 GREEN
and a fresh ticket-state transition based on measured transport results.
