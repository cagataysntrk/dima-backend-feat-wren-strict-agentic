# DIMA BRAIN V2.1 — DEVELOPER EXECUTION DIRECTIVE

**Status:** ACTIVE  
**Branch:** feat/dima-brain-v2-1-discovery-simplification  
**Decision:** DMP-DEC-0077_DIMA_BRAIN_V2_1_DISCOVERY_SIMPLIFICATION.md  
**Roadmap:** DIMA_BRAIN_V2_1_DISCOVERY_SIMPLIFICATION_ROADMAP.md  
**Handoff:** DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md

## Mission

Do not create Brain V3.

Do not redesign the accepted Brain V2 architecture.

Close the remaining high-leverage duplication:

~~~text
Metabot already produces governed analytical material
+
P17 provider-backed DISCOVERY reinterprets that same material
=
second stochastic analyst
~~~

Target:

~~~text
Metabot
→ VERIFIED Evidence
→ deterministic CandidateSetProjector
→ P19
~~~

P17 remains the typed Investigation Controller for NextTest/escalation.

## Exact branch baseline

~~~text
source HEAD
ed60bc1e5fc868deaead0cc321fdf58785cd5d8b

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9

digest
sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7

certification
36812902584 SUCCESS
~~~

Expected engine changes/builds:

~~~text
0
~~~

## Execution order

1. Read DEC-0077, roadmap and handoff.
2. Write CandidateSetProjector failing provider-free tests first.
3. Define candidate eligibility only from typed governed authority.
4. Implement deterministic candidate identity projection.
5. Ground candidates only as CONTEXT to exact VERIFIED Evidence.
6. Add PROJECT_CANDIDATES graph node/activity.
7. Route DISCOVERY after Evidence to PROJECT_CANDIDATES, not P17 provider discovery.
8. Route legal candidate set to P19.
9. Route zero legal candidates to an honest governed terminal.
10. Keep P17 NEXT_TEST/ADAPTIVE route intact.
11. Remove/disable provider-backed P17 DISCOVERY from normal V2.1 Product path.
12. Expand Hypothesis stateful sequence tests.
13. Add OpenTelemetry bridge over existing BoundaryTrace/BrainRunTelemetry.
14. Run full affected provider-free closure.
15. Freeze one semantic candidate.
16. Run exactly one fresh T4 DISCOVERY live.
17. Manually adjudicate T4.
18. Accept or reject simplification using the merge gate.
19. Only if T4 is accepted, audit T5 for redundant P17.
20. Do not change T5 unless redundancy is proven provider-free.
21. Freshly recertify T6 on final semantic candidate.
22. Recertify T7 if shared Product/intake/report code changed; otherwise produce exact non-affection proof.
23. Prove or recertify T1/T2/T3/T5 carry-forward through backend/app non-affection.
24. Run final Hypothesis/metamorphic closure.
25. Seal final Product SHA.
26. Declare readiness only if roadmap thresholds are earned.
27. STOP at 30-CASE READY.

## CandidateSetProjector invariant

~~~text
CandidateSet
=
allowed_discovery_surface
∩ current_scope
∩ VERIFIED observed bindings
∩ candidate-eligible governed semantics
- effect/outcome identity
~~~

Never use:

~~~text
all metrics minus effect
fuzzy matching
regex
morphology
embedding similarity
LLM candidate ranking
prompt keyword routing
~~~

Candidate projection creates identity/provenance only.

It must not create causal belief.

## Candidate cardinality

Do not optimize for a benchmark-specific count.

~~~text
0 candidates
→ honest stop

1 candidate
→ no fake competitor

2+ candidates
→ all legal candidates reach P19
~~~

If VERIFIED material exposes three legal candidates, do not arbitrarily reduce them to two unless an existing typed authority requires a bounded set.

## P19

P19 remains the epistemic owner.

Projected hypotheses may carry:

~~~text
candidate semantic identity
scope version
Evidence refs
source = OBSERVED_GOVERNED_MATERIAL
~~~

Deterministic Product code may not assign:

~~~text
SUPPORTS
CHALLENGES
probability
strength
dominant cause
causal conclusion
~~~

unless an existing sealed deterministic authority already owns that exact relation.

## P17

Normal discovery:

~~~text
P17 provider calls = 0
~~~

Keep P17 for:

~~~text
typed NextTest control
bounded investigation depth
durable investigation audit
adaptive escalation
~~~

Do not delete working ADAPTIVE behavior.

## Native acquisition

Do not hardcode one acquisition as a universal law.

Permanent rules:

~~~text
minimum necessary native work
duplicate acquisition = 0
new acquisition only from typed legal need
~~~

Historical T4 should normally close with one initial bounded acquisition.

## Hypothesis test plane

Hypothesis is already installed.

Extend stateful tests so these sequence families are explored before paid live:

~~~text
discovery → scope mutation → resume
discovery → NextTest → resume
discovery → checkpoint restart
scope mutation → discovery
report-only continuation
historical/current transition
same mutation twice
entity + period mutation
multi-intent continuation
~~~

Required invariants:

~~~text
no stale Evidence
no duplicate native execution
no candidate outside allowed surface
effect never becomes candidate
no cross-scope hypothesis reuse
report-only continuation creates no analytics
resume repeats no completed paid/native activity
~~~

## OpenTelemetry

Adopt observability only.

Do not replace Dima telemetry/contracts.

Map existing boundary operations to spans/events.

No raw prompt, hidden reasoning, Evidence body, SQL result body or secrets may be exported.

Every mechanical RED should make this queryable:

~~~text
last_valid_boundary
first_invalid_boundary
owner
error.type
expected fingerprint
observed fingerprint
~~~

## Open-source boundaries

Adopt now:

~~~text
Metabase/Metabot
LangGraph
Hypothesis
OpenTelemetry
~~~

Deferred:

~~~text
Schemathesis
→ after backend API freeze

Temporal
→ future Action/Watch plane

DSPy
→ offline only if architecture-clean cognition remains weak

OpenLineage/DataHub
→ future data lineage/catalog

Cedar/OPA
→ future authorization complexity
~~~

Do not add:

~~~text
Cube
MetricFlow
another analytics engine
another agent runtime
Temporal inside Brain
new Evidence authority
new graph database
~~~

## T4 live merge gate

Fresh T4 must satisfy:

~~~text
mechanical GREEN
manual >= 3/4
prefer 4/4

P17 discovery provider calls = 0
duplicate native = 0

P19 assessment = 1 initial assessment

>=2 distinct candidates
when VERIFIED material exposes >=2 eligible candidates

causal overclaim = 0
scope/currentness correct
Evidence lineage correct
~~~

Cost/latency must be no worse and should materially improve.

If quality regresses:

~~~text
REJECT V2.1 SIMPLIFICATION
~~~

Do not merge for architectural aesthetics.

## T5 relationship

Do not refactor T5 proactively.

Audit first.

Only simplify if P17 provider adds no new analytical material and no unique governed epistemic value.

If simplified:

~~~text
Metabot relationship analysis
→ VERIFIED typed Evidence
→ P18
→ P20
~~~

Dima must not calculate a new association from raw numbers.

## Final recertification

Historical READY receipts cannot automatically certify the final V2.1 SHA.

Freshly seal every affected capability.

Minimum fresh/live requirements:

~~~text
T4 DISCOVERY

T6 contextual report

T7 if shared Product/report/intake changed
~~~

T1/T2/T3/T5 may carry forward only with explicit non-affection proof or surgical recertification.

No broad test.

## Readiness target

Final V2.1:

~~~text
all affected mechanical GREEN
all targeted manual >=3
targeted average >=3.6/4
>=5/7 FULL

T1 = 4
T2 = 4
T4 preferably = 4
T6 = 4

no exception
no silent wrong
no security violation
no unsupported causal promotion
duplicate native = 0
P17 discovery provider = 0
stateful/metamorphic GREEN
no unresolved architecture family
~~~

Only then:

~~~text
90+ HIGH-CONFIDENCE READINESS = YES
30-CASE READY = YES
~~~

## Absolute prohibitions

~~~text
NO Agent API
NO 30-case
NO frontend/UI/UX
NO dima.10
NO engine build
NO SQL/MBQL planner in Dima
NO fuzzy/regex/morphological semantic authority
NO benchmark-specific behavior
NO provider limit inflation
NO retry-until-lucky
~~~

## Stop conditions

Stop only if:

~~~text
candidate identity requires a new semantic authority

P19 cannot consume projected candidates without weakening epistemic rules

one deduplicated native acquisition proves an engine-owned defect

engine source change is required

new analytics/query engine is required

security/P14/P18/P19 authority must be weakened
~~~

Normal provider-free RED is not a STOP.

Root it, fix the family, expand metamorphic/stateful tests, continue.

## Final return

Return only with:

~~~text
final branch HEAD
final semantic Product SHA
engine SHA/release/digest
engine builds = 0

CandidateSetProjector proof

P17 DISCOVERY provider
before / after

native acquisitions
before / after

T4 run/artifact/manual

T5 audit

T6 run/artifact/manual or exact non-affection

T7 run/artifact/manual or exact non-affection

T1/T2/T3/T5 non-affection/recertification

Hypothesis stateful results

OpenTelemetry instrumentation proof

provider calls
tokens
latency
cost

metamorphic closure

known limitations

90+ HIGH-CONFIDENCE READINESS
YES/NO

30-CASE READY
YES/NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
~~~

## Final architectural law

~~~text
METABASE / METABOT
= SINGLE ANALYTICAL COGNITION ENGINE

LANGGRAPH
= ORCHESTRATION

DIMA
= MEANING + EVIDENCE + CANDIDATE IDENTITY + COMPLETION

P19
= EPISTEMIC JUDGMENT

P18
= RELATIONSHIP JUDGMENT

P20
= GOVERNED SYNTHESIS

P17
= INVESTIGATION CONTROL
NOT A SECOND ANALYST

HYPOTHESIS
= FIND SEQUENCE BUGS BEFORE PAID LIVE

OPENTELEMETRY
= SHOW THE FIRST WRONG BOUNDARY

DO NOT SOLVE THE SAME RESPONSIBILITY TWICE.
~~~
