# DIMA DAY 6.5 — X0 BRIDGE PREFLIGHT

**Status:** **FINAL / SUCCESSFUL NEGATIVE DECISION — HEAVY_SEMANTIC_DUPLICATION**  
**Date:** 2026-09-22  
**Metabase runtime spin-up:** **NOT RUN / NOT REQUIRED FOR CURRENT RELEASE**  
**Wren semantic backbone:** **RETAINED / PRIMARY**  
**Dima accepted authority/evidence:** UNCHANGED

## FINAL DECISION — SUCCESSFUL NEGATIVE PREFLIGHT

Verified checkpoint / CI:

```text
tested product checkpoint
= dd5c16bbe444b6d9183faea9e9937be11260f394

bridge CI
= 35761526816 SUCCESS

runtime_started
= false

metabase_api_called
= false

real_wren_plans_compiled
= true
```

Eight representative Standard families were evaluated from real sealed Dima/Wren artifacts.

```text
7 / 8 families
= thin / lossless

computed + semi-additive family
= cari.bakiye
= SUM(borc - alacak)

bridge_lossless              = false
metric_formula_duplication   = true
grain_additivity_duplication = true
unsupported semantic shape   = computed_metric_expression:bakiye

terminal
= HEAVY_SEMANTIC_DUPLICATION
```

Aggregate preflight safety result:

```text
manual semantic mappings          = 0
unapproved implicit FK joins      = 0
second semantic authority         = 0
semantic handle remint            = 0
raw-language reinterpretation     = 0
Metabase label/name guessing      = 0

duplicated semantic definitions   = 2
unsupported semantic shapes       = 1
```

Architecture decision for this release:

```text
Wren semantic backbone            = RETAINED
Wren analytical execution         = PRIMARY

Metabase structured execution     = REJECTED CURRENT RELEASE
Metabase Agent API prod dependency= NO
X0-REST                            = NOT RUN / NOT REQUIRED
```

Scope of REJECT:

> The architecture **retained Wren semantic truth → thin Metabase structured execution** is rejected
> for this release because full fidelity for computed/semi-additive semantics requires formula/grain
> reconstruction, which turns the bridge into a second semantic compiler/sync layer.

This does **not** mean:
- Metabase is bad;
- Metabase cannot compute metrics;
- Metabase is permanently rejected.

Future independent evidence may reopen the execution question if the semantic boundary changes
materially (for example, a lossless shared structured semantic representation becomes available).

Forbidden response to this negative preflight:
- copy Wren formulas into MBQL;
- shadow Metabase metric definitions;
- manual relationship mirrors;
- metric-specific bridge branches;
- Wren→MBQL semantic compiler;
- raw SQL shortcut;
- Metabase business-semantic inference.

The purpose of this gate was to veto exactly that semantic duplication before runtime integration cost.

---

## Current sealed authority

```text
HEAD                    6d65600842731112f2362261a30660217cbde05d
D65-SI                  FINAL GREEN / SEALED
M0E-DEEP-DELTA          FINAL GREEN / SEALED
Metabase runtime        OFF
production /ask-v2      OFF
DEV80                   FORBIDDEN
```

No semantic/SI/M0E reopening without new independent P0.

## Question

> Can one already-accepted Dima/Wren semantic request be translated into Metabase structured-query
> semantics deterministically and losslessly without creating a second semantic truth?

This is a design/prototype proof, not a Metabase runtime benchmark.

## Identity mapping is not semantic mapping

Allowed:
existing accepted Dima/Wren canonical identity → exact physical lineage → current Metabase
runtime identity, mechanically and tenant/version scoped.

Every mapping receipt is classified:
`IDENTITY_ONLY` or `SEMANTIC_DUPLICATION`.

Forbidden:
label/name lookup as meaning, manual metric formula recreation, manual relationship recreation,
or physical FK inference as business truth.

## Candidate seams

Evaluate at least:

```text
A. StandardProjection + opaque handles
B. resolved Dima AnalyticsIR
C. later Wren-specific planned representation
```

Current hypothesis: **B may be the narrowest** because the existing Wren Standard adapter already
resolves opaque handles once into canonical `AnalyticsIR`.

Evidence decides; do not force B if it duplicates semantics or leaks substrate ownership.

Target conceptual shape:

```text
AcceptedStandardAuthority
→ StandardProjection
→ resolve sem_* exactly once
→ Dima-owned canonical execution intent / AnalyticsIR
             ├→ Wren planner
             └→ thin Metabase bridge
```

Do not build a second handle resolver or large generic substrate framework automatically.

## Eight family preflight

Use the same planned X0 Standard families:
1. metric only
2. metric + dimension
3. metric + filter
4. metric + period
5. metric + period + previous-period comparison
6. metric + dimension + ranking/limit
7. metric + two compatible dimensions
8. metric + filter + period + dimension

No Research/root-cause/relationship case.

## Measurements per family

```text
bridge_lossless
metric_formula_duplication
relationship_duplication
grain_additivity_duplication
time_semantics_duplication
filter_fidelity
ranking_fidelity
comparison_fidelity
implicit_metabase_join_required
manual_metadata_mapping_required
bridge_LOC
conceptual_complexity
sync_surface
unsupported_wren_only_constructs
```

## Hard P0

```text
raw_user_language_reinterpretation = 0
manual_metric_redefinition         = 0
manual_relationship_redefinition   = 0
metabase_label_name_guessing       = 0
unapproved_implicit_FK_join        = 0
second_semantic_authority          = 0
```

If satisfying representative families requires:
- a new semantic compiler;
- dual metric/relationship/grain/time definitions;
- large metadata synchronization product;
- raw-label semantic guessing;
- physical FK joins outside Wren-approved relationship truth;

then:
```text
METABASE STRUCTURED EXECUTION ARM = REJECT BEFORE X0
```

This is a successful preflight outcome.

Metabase may still remain:
- workspace/product candidate;
- architecture reference;
- behavioral oracle;
- dashboard/collection/search candidate.

## If GREEN

Only then may `X0-REST` start:
- self-hosted Metabase;
- dedicated per-user session identity for principal-fidelity proof;
- raw SQL kill-switch explicit/off;
- Dima authority/evidence unchanged;
- access-lens receipt included;
- no source copy.

Promising X0 still requires STOP/CONSULT before full D65-X.
