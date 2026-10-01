# DIMA BRAIN V2.1 — CURRENT HANDOFF

**Status:** ACTIVE  
**Branch:** feat/dima-brain-v2-1-discovery-simplification  
**Decision:** DMP-DEC-0077_DIMA_BRAIN_V2_1_DISCOVERY_SIMPLIFICATION.md  
**Roadmap:** DIMA_BRAIN_V2_1_DISCOVERY_SIMPLIFICATION_ROADMAP.md

## Exact baseline

~~~text
branch point
ed60bc1e5fc868deaead0cc321fdf58785cd5d8b

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9

engine digest
sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7

engine certification
36812902584 = SUCCESS

engine builds allowed in V2.1
0
~~~

## Why this branch exists

Brain V2 is retained.

The current graph still contains provider-backed P17 DISCOVERY after Metabot has already produced governed analytical material.

V2.1 tests whether this can be safely replaced with:

~~~text
VERIFIED Metabot Evidence
→ deterministic CandidateSetProjector
→ P19
~~~

P17 remains for typed NextTest / investigation control.

## Immediate implementation order

1. write CandidateSetProjector contract tests;
2. implement deterministic candidate identity projection;
3. create candidates only from governed allowed discovery surface + current VERIFIED observed bindings;
4. exclude effect/outcome identity;
5. ground projected hypotheses only as CONTEXT;
6. add graph node PROJECT_CANDIDATES;
7. route discovery Evidence → PROJECT_CANDIDATES → P19;
8. remove provider-backed P17 DISCOVERY from normal V2.1 route;
9. keep P17 NEXT_TEST path intact;
10. expand Hypothesis state-machine coverage around discovery/scope/resume/report;
11. bridge existing BoundaryTrace/BrainRunTelemetry to OpenTelemetry;
12. run full affected provider-free closure;
13. freeze one semantic candidate;
14. run one fresh T4 live;
15. accept/reject the simplification using the roadmap merge gate;
16. audit observational T5 for redundant P17 only after T4 acceptance;
17. recertify T6/T7 where current semantic changes affect them;
18. run final stateful/metamorphic closure;
19. seal 90+ readiness / 30-CASE READY if earned;
20. STOP.

## Non-negotiable boundaries

~~~text
Metabot = single analytical cognition engine
LangGraph = orchestration only
Dima = semantic / Evidence / candidate identity / completion
P19 = epistemic judge
P18 = relationship judge
P20 = governed report/synthesis
P17 = investigation controller, not second analyst
~~~

Forbidden:

~~~text
Agent API
new analytics engine
Dima SQL/MBQL planner
regex/fuzzy/morphological semantic patches
embedding threshold truth
benchmark-specific logic
provider ceiling inflation
retry-until-lucky
frontend/UI/UX
30-case
engine build
~~~

## Candidate projector acceptance

The projector must use:

~~~text
allowed discovery surface
∩ current scope
∩ VERIFIED observed bindings
∩ candidate-eligible governed semantics
- effect/outcome identity
~~~

It must not use:

~~~text
all metrics minus effect
text similarity
LLM candidate ranking
~~~

Projected candidates are identities, not causal claims.

## T4 live gate

After full provider-free GREEN:

~~~text
P17 discovery provider calls = 0
duplicate native = 0
P19 = 1 initial assessment
>=2 candidate identities when >=2 legal observed candidates exist
mechanical GREEN
manual quality >=3/4
prefer 4/4
causal overclaim = 0
~~~

If quality regresses, reject the refactor.

## Open-source quality additions

### Hypothesis

Already installed and in use.

Expand stateful testing.

Do not create a runtime dependency or authority.

### OpenTelemetry

Adopt as observability.

Bridge existing Brain telemetry.

Never export prompt/reasoning/raw Evidence payload.

### Schemathesis

Deferred until backend API freeze.

### Temporal

Future Action/Watch plane only.

### DSPy

Offline/conditional only after architecture closure.

### Cube / MetricFlow

Do not add while Metabase remains analytics owner.

## Readiness warning

Historical 30-CASE READY receipts refer to older semantic candidates.

Do not inherit READY automatically.

Final V2.1 candidate must have:
- fresh T4;
- fresh T6 because current P20 changed after older receipt;
- fresh T7 if shared Product/intake/report code is affected;
- explicit non-affection proof or surgical recertification for carried T1/T2/T3/T5 evidence.

## Stop conditions

Stop only if:

~~~text
candidate identity cannot be projected without new semantic authority

P19 cannot consume governed projected candidates without weakening epistemic rules

one deduplicated Metabot acquisition has an engine-owned defect

engine source change becomes necessary

new analytics/query engine would be required

security/P14/P18/P19 authority must be weakened
~~~

Normal provider-free RED is not a stop.

## Final return

Return only with:

~~~text
90+ HIGH-CONFIDENCE READINESS = YES/NO
30-CASE READY = YES/NO
30-case = NOT RUN
frontend = NOT IMPLEMENTED
~~~

and all receipts required by the V2.1 roadmap.
