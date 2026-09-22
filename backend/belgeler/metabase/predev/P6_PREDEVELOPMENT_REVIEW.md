# P6 — PRE-DEVELOPMENT REVIEW

**Milestone:** P6 — Wren vs Metabase Standard parity  
**Branch:** `feat/dima-metabase-platform`  
**P5 contract closure:** `440f50c2891a32426b06e80e7b0b36a48eb77f51`  
**P5 closure workflow:** `35759691357 = SUCCESS`  
**P5 closure governance:** `35760197601 = SUCCESS`  
**Metabase runtime:** `v0.63.18` immutable digest pinned  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY

Status: **SEALED / CORPUS FREEZE + PARITY HARNESS AUTHORIZED AFTER GOVERNANCE GREEN**

## 1. Normative boundary re-read

P6 freezes:
```text
same AcceptedStandardAuthority
same StandardProjection
same ResolvedAnalyticsIntent
same semantic refs
same approved relationship paths
same principal/access snapshot contract
same database snapshot
```

Only execution substrate changes:
```text
WrenSubstrateAdapter
vs
MetabaseSubstrateAdapter
```

P6 measures execution parity. It does not decide Wren retirement.

## 2. Existing-state audit

Current Wren live sentinels use:
`demo/data/boyahane.duckdb` + composed boyahane MDL.

Current Metabase P4 live proof uses:
isolated PostgreSQL `Dima Analytics Lab` + synthetic `orders`.

Therefore existing live suites do **not** share a database snapshot and cannot be treated as
Wren-vs-Metabase numeric parity evidence.

Classification: `DATA/FIXTURE_GAP`.

## 3. Same-snapshot decision

P6 will use the existing pinned M2 PostgreSQL analytics service as the single physical data snapshot.

A P6-only Compose override may bind **analytics-db only** to loopback for the duration of the parity
workflow. Base M2 compose is unchanged.

Wren connects to that exact PostgreSQL through the repository's native Wren PostgreSQL connector.
Metabase remains connected to the same `analytics-db`.

P6-specific seed tables and Wren manifest are test/lab artifacts only.

## 4. Frozen parity dataset

P6 fixture owns deterministic:
```text
p6_orders
p6_customers
```

Minimum fields support:
- numeric metric aggregation;
- two categorical dimensions;
- date/time periods;
- ranking/top-N;
- literal entity filters;
- one explicit orders→customers relationship surface for gap measurement.

No customer/production data.

## 5. Corpus freeze

Exactly 80 cases:
```text
30 standard
10 time/comparison
10 ranking/top-N
10 filters/entity
10 join/relationship
10 error/edge
```

Corpus records are post-cognition structural specs, not raw prompts.

Every case deterministically yields the frozen post-authority bundle:
```text
AcceptedStandardAuthority
StandardProjection
ResolvedAnalyticsIntent
DimaExecutionBindingSnapshot
ExecutionAccessSnapshot fixture
database snapshot id
```

A corpus fingerprint is stored and tested. Changing a frozen case requires an explicit P6 corpus
decision, never a prompt-specific patch.

## 6. Mismatch taxonomy

Only:
```text
AUTHORITY_GAP
SEMANTIC_SPEC_GAP
COMPILER_GAP
RELATIONSHIP_GAP
TEMPORAL_CONTRACT_GAP
ACCESS/PERMISSION_GAP
SUBSTRATE_RUNTIME_GAP
DATA/FIXTURE_GAP
ORACLE_GAP
```

Forbidden:
regex, fuzzy matching, morphology authority, synonyms added for a failing case, prompt text branches,
similar-name binding, silent fallback, different-meaning retry.

## 7. P6 result semantics

Per case:
```text
MATCH
TYPED_GAP
UNEXPLAINED_MISMATCH
```

`TYPED_GAP` is not feature parity and is never counted as MATCH.

P6 measurement closes only when:
- corpus = exactly 80 and fingerprint-frozen;
- both arms consume the same frozen input ids/hashes;
- both arms execute the same physical DB snapshot where execution is supported;
- numeric/row/aggregation/time/ranking/filter outputs are compared canonically;
- every non-match has one typed owner/classification;
- `UNEXPLAINED_MISMATCH = 0`;
- no prompt-specific patch exists.

Typed relationship/security gaps are carried forward visibly to P8/P10; P6 does not fabricate
support to make the matrix green.

## 8. Access boundary

P6 uses an explicit complete P5 `ExecutionAccessSnapshot` fixture as frozen comparison input.

It does **not** issue or prove production access. DMP-P5-BLOCK-001 remains P10-owned.

Permission-sensitive cases may produce `ACCESS/PERMISSION_GAP`; P6 cannot certify production
tenant/RLS/CLS/revocation parity.

## 9. Metabase substrate boundary

P6 may add one production `MetabaseSubstrateAdapter` implementing the existing
`AnalyticsSubstrate` seam from:
`ResolvedAnalyticsIntent + DimaExecutionBindingSnapshot + ExecutionAccessSnapshot + RuntimeIdentity`.

It may:
compile → canonicalize → execute → P5 seal → evidence.

It may not:
resolve semantic handles, inspect raw language, search Metabase for meaning, issue access snapshots,
guess resources, or silently fall back.

## 10. Files allowed

```text
backend/app/v3/substrate/metabase/execution_adapter.py
backend/app/v3/parity/**
backend/tests/fixtures/p6/**
backend/tests/test_v3_p6_*.py
backend/lab/metabase/p6/**
.github/workflows/dima-metabase-p6.yml
backend/belgeler/metabase/predev/P6_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P6_WREN_METABASE_PARITY.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

## 11. Forbidden without new receipt

```text
backend/app/v2/**
backend/app/v3/authority.py
backend/app/v3/analytics_contract.py
backend/app/v3/semantic_spec.py
backend/app/v3/substrate/wren.py
backend/app/v3/substrate/metabase/compiler.py
backend/app/v3/substrate/metabase/canonical.py
backend/app/v3/execution_identity.py
backend/control_plane/**
backend/app/routers/**
backend/app/main.py
backend/app/config.py
backend/lab/metabase/docker-compose.yml
backend/lab/metabase/init/**
WrenAI-main/**
feat/ask-v2-mvp
```

## 12. First implementation order

1. freeze 80-case corpus + corpus fingerprint;
2. build same-PostgreSQL P6 fixture and minimal structured Wren manifest;
3. prove both engines see identical snapshot identity/count/checksum;
4. add MetabaseSubstrateAdapter;
5. execute supported corpus families A/B;
6. classify every mismatch;
7. close only with zero unexplained mismatch.

No P7 code before the P6 parity report is sealed.
