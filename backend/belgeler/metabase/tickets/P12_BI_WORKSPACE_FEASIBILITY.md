# P12-001 — BI workspace feasibility

**Milestone:** P12  
**Status:** FEASIBILITY CLASSIFICATION / NO INTEGRATION IMPLEMENTATION

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
