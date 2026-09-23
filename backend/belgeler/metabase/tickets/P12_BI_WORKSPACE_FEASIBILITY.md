# P12-001 — BI workspace feasibility

**Milestone:** P12  
**Status:** CLOSED / CLASSIFICATION GREEN / NO INTEGRATION IMPLEMENTATION

## Decision

Initial product composition:
`DIMA_SHELL + HEADLESS_API`.

Native Metabase workspace:
`LINK_OUT` escape hatch for capabilities not yet composed into Dima.

`EMBED`:
optional future escalation after an explicit continuity/context/auth/session need is measured.

## Why

Fast Track already provides moving-branch evidence that Dima-native result rendering and run lifecycle
are viable. Pinned Metabase already provides mature workspace primitives. The Platform therefore does
not need to choose between "rebuild all BI" and "make Metabase the whole product".

## Ownership

Dima:
conversation, evidence, research, report/decision UX, semantic/security truth.

Metabase:
query execution, native BI workspace capability, optional rendering/workspace surfaces.

## Next

P13 owns production Standard integration, including P11 integration requirement
`DMP-P11-INTEGRATION-005`.

No Fast Track harvest is authorized by this feasibility ticket alone.


## Closure

Decision receipt: `DMP-DEC-0028`.

Certified wording:
```text
P12 BI WORKSPACE FEASIBILITY = CLOSED / CLASSIFICATION GREEN
```

Closure changed no frontend/product integration code and authorized no Fast Track harvest.
Next real integration owner: P13 Production Standard.
