# M1 / P1 — PRE-DEVELOPMENT REVIEW

**Milestone:** M1 / P1 — engine-independent Dima contracts + Wren adapter  
**Branch:** `feat/dima-metabase-platform`  
**Certified base:** `3774484167f1056d89da0e0609246fb4a05057ec`  
**Platform HEAD before product code:** `8d5a4b956ba88276f1b7b1f3868072a15c49f487`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY  
**Observed source HEAD:** `4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a`

Status: SEALED / IMPLEMENTATION AUTHORIZED

## 1. Normative sources re-read

Roadmap:
- P1 — Engine-independent Dima core.
- Required modules: `app/v3/semantic_spec.py`, `authority.py`, `analytics_contract.py`,
  `evidence.py`, `substrate/base.py`, `substrate/wren.py`.
- Minimum substrate contract: `inspect_capabilities`, `validate_execution_intent`,
  `execute_execution_intent`, `inspect_execution`.
- Semantic handle resolution must not happen inside the substrate adapter.
- First Wren adapter must preserve current behavior.
- Exit gate: Wren sentinel green, behavior drift=0, partial semantic-surface silent-loss=0,
  Standard/Research double-authority=0.

Architecture report:
- R0.2 evidence-based inheritance; no legacy authority or silent fallback.
- R2 exactly-one authority, deterministic trust plane, semantic-surface completeness,
  Standard/Research XOR, role separation.
- R5 Wren semantic behavior that must eventually be preserved.
- R6 DimaSemanticSpec owns meaning; adapters execute representations.
- R6.1 semantic handles resolve exactly once into `ResolvedAnalyticsIntent`.
- R7 Standard path places `ResolvedAnalyticsIntent` between accepted authority and substrate.

## 2. Certified-base implementation inspected

Inspected on platform branch / certified-base lineage:
- `app/v2/manager_models.py::StandardProjection`
- `app/v2/manager_models.py::AcceptedTurnContract`
- `app/v2/standard_authority.py`
- `app/v2/semantic_handles.py`
- `app/v2/standard_execution.py`
- `app/v2/cube_planner.py`
- `app/v2/models.py::{ResolvedSemanticRef,ResolvedFilterRef,ResolvedPeriod,ResolvedComparison,ResolvedRanking,AnalyticsIR,EvidenceArtifact,MinimumQueryContract}`
- existing real-Wren sentinel workflow/tests.

Key finding:
the v2 `WrenStandardExecutionAdapter` is the behavioral reference but it still performs
semantic-handle resolution internally. M1 must preserve its query/planner/validator/contract behavior
while moving handle resolution into the Dima-owned pre-substrate contract boundary.

## 3. Moving source delta inspected READ-ONLY

Compared certified base to observed source HEAD. Useful correctness deltas:
1. material semantic surfaces are individually accounted for; same-kind partial success cannot hide a gap;
2. shared Standard/Research arbiter gained non-mutating `validate` + idempotent `commit`;
3. Research semantic and temporal providers are assembled from distinct model roles.

Not inherited:
- no merge/rebase/cherry-pick;
- no source-side front-door ownership;
- no source-side full-live result used as certification;
- full-live source run `35724830736` is RED and remains source evidence only.

Decision authority: `DMP-DEC-0003`.

## 4. M1 single owner

**Owner:** engine-independent analytics/authority contracts and Wren compatibility substrate.

### Files allowed to touch

```text
backend/app/v3/__init__.py
backend/app/v3/semantic_spec.py
backend/app/v3/authority.py
backend/app/v3/analytics_contract.py
backend/app/v3/evidence.py
backend/app/v3/substrate/__init__.py
backend/app/v3/substrate/base.py
backend/app/v3/substrate/wren.py
backend/tests/test_v3_m1_*.py
.github/workflows/dima-metabase-m1.yml
DIMA-METABASE-DURUM.md
backend/belgeler/metabase/*receipts*.md
backend/belgeler/metabase/predev/*
```

### Files forbidden in M1 implementation

```text
backend/app/v2/**
backend/app/routers/ask_v2.py
backend/app/main.py
backend/app/config.py
WrenAI-main/**
Metabase product/runtime files (none are introduced in M1)
feat/ask-v2-mvp branch refs
```

If a forbidden file becomes necessary, STOP and open a new Decision Receipt before modification.

## 5. Contract design boundary

M1 will create:
- engine-independent canonical semantic contract shells (`DimaSemanticSpec`);
- v3 `StandardProjection`, `AcceptedStandardAuthority`, existing Research
  `AcceptedTurnContract` alias, and `SharedAuthorityArbiter`;
- explicit `SemanticSurfaceCoverage`;
- Dima-owned `ResolvedAnalyticsIntent`;
- `DimaQueryReceipt` and v3 `EvidenceArtifact` contract;
- `AnalyticsSubstrate` protocol;
- Wren substrate that receives only `ResolvedAnalyticsIntent`.

M1 will **not**:
- build Metabase client/compiler/runtime;
- migrate front-door ownership;
- retire Wren;
- create Wren MDL importer (P7);
- claim semantic equivalence (P8);
- implement full P5 durable receipt/security semantics beyond the foundational contract.

## 6. Hard invariants for M1

```text
ask-v2 source writes                         = 0
v2 product path changes                     = 0
second Research contract type               = 0
same-turn Standard + Research authority     = 0
material semantic surface silent-loss       = 0
substrate semantic-handle resolution        = 0
raw user language in substrate              = 0
Wren query/planner/result semantic drift    = 0
Metabase runtime dependency                 = 0
```

## 7. Baseline and proof plan

Baseline:
- focused/provider-free: `35718675540 = 25/25 PASS`;
- real Wren sentinels: `35718883950 = 2/2 PASS` at certified base.

M1 proof:
1. compile all `app/v3` modules;
2. provider-free contract tests:
   - authority XOR + idempotence,
   - material semantic-surface accounting,
   - projection seal/hash,
   - resolve-once intent construction,
   - substrate protocol no semantic resolution;
3. Wren parity tests on same accepted authority/resolved intent:
   - same canonical AnalyticsIR meaning,
   - same planner queries,
   - same row/result shape,
   - same legacy QueryContract sealing behavior;
4. rerun retained v2 real-Wren sentinels to prove old behavior remains green;
5. M1 is not GREEN if any parity mismatch is hidden by fallback.

## 8. Implementation authorization

All mandatory pre-development reading and source inspection for M1 has been completed.
Product implementation may begin **only after this review commit's governance CI is GREEN**.
