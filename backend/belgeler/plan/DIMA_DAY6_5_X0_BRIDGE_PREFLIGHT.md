# DIMA DAY 6.5 — X0 BRIDGE PREFLIGHT

**Status:** OPEN / BLOCKS X0 RUNTIME  
**Date:** 2026-09-22  
**Metabase runtime spin-up:** FORBIDDEN UNTIL PREFLIGHT GREEN  
**Wren semantic backbone:** RETAIN  
**Dima accepted authority/evidence:** UNCHANGED

## Question

> Can one already-accepted Dima/Wren semantic request be translated into Metabase structured-query
> semantics deterministically and losslessly without creating a second semantic truth?

This is a design/prototype proof, not a Metabase runtime benchmark.

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
