# DIMA BRAIN V2.1 — DISCOVERY SIMPLIFICATION + FINAL PRE-BENCHMARK ROADMAP

**Status:** ACTIVE / FORWARD AUTHORITY ON THIS BRANCH  
**Branch:** feat/dima-brain-v2-1-discovery-simplification  
**Branch point:** ed60bc1e5fc868deaead0cc321fdf58785cd5d8b  
**Engine:** d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88 / 0.63.18-dima.9  
**Engine digest:** sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7  
**Engine certification:** 36812902584 = SUCCESS  
**Frontend/UI/UX:** FORBIDDEN  
**30-case:** FORBIDDEN until separate explicit user authorization

## 1. Why V2.1 exists

Brain V2 is not being rewritten.

The accepted architecture already proved:
- LangGraph can orchestrate current Dima domain owners;
- scope/currentness can be durable;
- ONE_PASS can bypass P17 discovery;
- ADAPTIVE can use bounded re-entry;
- P18/P19/P20 owners can remain explicit;
- current engine dima.9 is certified and frozen.

The remaining high-leverage simplification is DISCOVERY.

Current graph still contains:

~~~text
ADMIT_EVIDENCE
  ↓
P17_DISCOVERY  (provider-backed stochastic cognition)
  ↓
P19
~~~

This creates a second cognition layer after Metabot has already produced broad governed analytical material.

The V2.1 decision is:

~~~text
METABASE / METABOT
= SINGLE ANALYTICAL COGNITION ENGINE

LANGGRAPH
= ORCHESTRATION ONLY

DIMA
= INTENT
= SCOPE
= MATERIAL CONTRACT
= EVIDENCE
= CANDIDATE IDENTITY
= PROVENANCE
= COMPLETION

P19
= EPISTEMIC JUDGE

P18
= RELATIONSHIP JUDGE

P20
= GOVERNED SYNTHESIS / REPORT

P17
= INVESTIGATION CONTROLLER
= NEXT-TEST / DISCOVERY RECORD
≠ SECOND ANALYST
~~~

## 2. Current evidence

The historical T4 failure family showed:

~~~text
Intake = correct
Scope = correct
Material = correct
Metabot/native result = correct
Evidence = correct

P17 discovery:
fault_count
fault_count
fault_count
~~~

The analytical material already exposed several governed candidate surfaces, while provider-backed P17 discovery repeatedly selected the same mechanism.

Current T1/T2/T3 architecture evidence is strong enough that this is not a reason to create Brain V3.

V2.1 is a bounded simplification spike over Brain V2.

## 3. Merge policy

This branch may replace the current discovery route only if it:
- preserves or improves T4 manual quality;
- removes provider-backed P17 DISCOVERY from the normal route;
- does not weaken P19 epistemic authority;
- does not add a second analytical engine;
- does not increase duplicate native acquisitions;
- does not regress ONE_PASS or ADAPTIVE;
- does not weaken security/scope/Evidence invariants.

If those gates fail, discard this branch and keep the current Brain V2 path.

Do not force the refactor because it is architecturally attractive.

---

# PHASE A — REMOVE THE SECOND DISCOVERY ANALYST

## 4. CandidateSetProjector

Create a deterministic Dima projection over already governed state.

Conceptually:

~~~text
CandidateSet
=
allowed_discovery_surface
∩ current_scope
∩ VERIFIED observed bindings
∩ candidate-eligible governed semantics
- effect/outcome identity
~~~

Do NOT implement:

~~~text
all result metrics - effect metric
~~~

That would cause hypothesis explosion.

The allowed discovery surface must be bounded by accepted typed authority.

## 5. Candidate eligibility

A projected candidate must satisfy all of:
- semantic identity is already governed;
- semantic identity is allowed by current discovery material authority;
- semantic identity is visible in VERIFIED Evidence/material bindings;
- semantic identity belongs to current ScopeVersion;
- semantic identity is candidate-eligible;
- semantic identity is not the effect/outcome identity;
- tenant/principal/currentness are legal.

No text similarity.
No fuzzy matching.
No embeddings.
No regex/morphology.

## 6. Candidate projection authority

Candidate projection creates only identity/provenance.

Conceptual record:

~~~text
CandidateHypothesisIdentity

semantic_id
source = OBSERVED_GOVERNED_MATERIAL
scope_version_id
evidence_refs
material_requirement_ref
~~~

It means only:

~~~text
this governed mechanism is eligible for epistemic evaluation
~~~

It MUST NOT mean:
- this mechanism caused the effect;
- this mechanism is likely;
- this candidate is stronger;
- support probability = X;
- dominant cause.

Those belong to P19.

## 7. Grounding

Projected candidate hypotheses may be created in the existing P19/Hypothesis store.

Ground them to exact VERIFIED Evidence as CONTEXT unless an existing sealed owner has already created a stronger governed relation.

Do not deterministically manufacture SUPPORTS or CHALLENGES.

P19 owns epistemic interpretation.

## 8. Graph change

Target discovery graph:

~~~text
ADMIT_EVIDENCE
  ↓
PROJECT_CANDIDATES
  ├── 0 legal candidates → HONEST_STOP
  └── >=1 legal candidate → P19_ASSESS
                               ├── SUFFICIENT → REPORT/ANSWER
                               ├── INCONCLUSIVE → HONEST_STOP
                               └── NEXT_TEST_REQUIRED
                                      ↓
                               P17_NEXT_TEST
                                      ↓
                                   METABOT
                                      ↓
                                   EVIDENCE
                                      ↓
                                     P19
~~~

Normal DISCOVERY path:

~~~text
p17_manager provider calls = 0
~~~

The old provider-backed discovery route may remain behind a temporary comparison/fallback seam during the spike, but it must not remain in the accepted normal V2.1 Product path.

## 9. Candidate cardinality

Do not force exactly two candidates.

Legal results:
- 0 candidates → honest no-governed-candidate terminal;
- 1 candidate → assess if legal, otherwise honest insufficient-diversity terminal;
- 2+ candidates → normal P19 competition assessment.

Never fabricate a competitor to satisfy a benchmark.

## 10. Native acquisition invariant

Do NOT make native acquisitions = exactly 1 a universal architecture law.

For the historical T4 certification fixture, one initial acquisition is the expected efficient result.

Permanent invariant:

~~~text
minimum necessary bounded native work

duplicate analytical acquisition = 0

additional acquisition
ONLY after a typed P19 NextTestRequest
or an exact deterministic missing-material requirement
allowed by current authority
~~~

No second acquisition simply because P17 wants another look.

## 11. Provider accounting

Track separately:

~~~text
Dima analytical acquisitions
duplicate acquisitions
Metabot internal provider requests
Research Intake requests
P17 discovery provider requests
P17 next-test requests
P19 provider requests
P20 provider requests
~~~

Metabot may internally use several provider turns to complete one analytical acquisition.

That is separate from Dima opening multiple acquisitions.

## 12. P17 permanent role

Keep:

~~~text
durable investigation record
bounded depth/budget
typed NextTest execution/control
discovery provenance/audit
~~~

Retire from normal Product path:

~~~text
provider-backed free-form candidate discovery
general autonomous second-analyst loop
~~~

P17 is an Investigation Controller, not another analytical engine.

## 13. ADAPTIVE must remain intact

Do not collapse ADAPTIVE into deterministic candidate projection.

ADAPTIVE remains:

~~~text
P19 identifies exact epistemic gap
→ typed NextTestRequest
→ P17 controller
→ one high-information Metabot acquisition
→ new Evidence
→ P19 reassessment
~~~

Recursion remains escalation, not ceremony.

---

# PHASE B — ENGINEERING QUALITY PLANE + FINAL RECERTIFICATION

## 14. Hypothesis — formalize what is already present

Hypothesis is already a backend dependency and stateful tests already exist.

Do not add a new runtime.

Expand the state-machine/property suite so recurring transition bugs fail before paid live.

Required rule families:

~~~text
narrow entity
expand entity
change period
change metric
entity + period mutation
no-op mutation
same mutation twice
report-only continuation
checkpoint restart
resume
adaptive NextTest
historical/current transition
discovery candidate projection
relationship continuation
multi-intent continuation
~~~

Required invariants:

~~~text
scope version monotonicity
historical Evidence never becomes current silently
duplicate native acquisition = 0
accepted semantic refs remain governed
candidate projector never leaves allowed discovery surface
effect identity never becomes its own candidate
P19 cannot see stale-scope Evidence
report-only continuation does not start analytics
restart/resume does not repeat completed paid/native activity
~~~

Hypothesis is a testing plane, not Product authority.

## 15. OpenTelemetry — adopt now as observability bridge

The repo already has Brain V2 BoundaryTrace and BrainRunTelemetry.

Do not replace them.

Bridge them to OpenTelemetry.

Use spans for duration-bearing operations:

~~~text
dima.intent.interpret
dima.scope.resolve
dima.material.compile
dima.native.execute
dima.evidence.admit
dima.p19.assess
dima.p17.next_test
dima.p20.report
~~~

Use events for point-in-time state transitions/outcomes.

Suggested low-cardinality attributes:

~~~text
scope_version_id
scope_fingerprint
material_fingerprint
evidence_revision
hypothesis_revision
candidate_count
native_acquisition_count
provider_call_count
dedup_hit
terminal_state
error.type
first_invalid_boundary
~~~

Never export:
- raw user data;
- full Evidence payload;
- provider prompt;
- hidden reasoning;
- SQL result bodies;
- secrets.

Existing public receipts remain deterministic Product/test artifacts.

OpenTelemetry is observability only.

## 16. First-invalid-boundary rule

Every mechanical RED receipt should identify:

~~~text
last_valid_boundary
first_invalid_boundary
expected typed identity/fingerprint
observed typed identity/fingerprint
owner
error.type
~~~

The developer should not need thousands of log lines to identify the first wrong transition.

## 17. Relationship path — audit, do not refactor blindly

Historical T5 quality is strong.

Do NOT change observational relationship architecture merely because a provider-backed P17 call may still appear.

First prove whether that P17 call:
- creates new analytical material;
- creates unique governed epistemic information;
- or only restates already VERIFIED relationship material.

If it adds no material value, authorize a separate bounded simplification:

~~~text
Metabot relationship analysis
→ VERIFIED typed relationship Evidence
→ P18
→ P20
~~~

No deterministic Dima code may compute a new analytical association from raw numbers.

If the call is useful or removing it reduces quality, leave T5 unchanged for this release.

## 18. P20/reporting

Do not reopen P20 architecture without a reproduced defect.

Current head contains later P20/contextual-report changes after an older readiness receipt.

Therefore final V2.1 readiness must recertify affected contextual report behavior on the final semantic candidate.

## 19. Current readiness authority warning

Historical 30-CASE READY receipts reference older semantic Product states.

The current branch contains substantial backend semantic changes after those receipts.

Therefore:

~~~text
historical readiness = reference
current V2.1 readiness = must be freshly sealed
~~~

Do not copy an old READY claim onto the new branch without revalidation.

---

# OPEN-SOURCE STACK DECISION

## 20. ADOPT NOW

~~~text
Metabase / Metabot
= analytics/query cognition

LangGraph
= Brain orchestration/checkpoint

Hypothesis
= stateful/property-based sequence testing

OpenTelemetry
= tracing/observability
~~~

These replace commodity responsibilities without redefining Dima business/epistemic authority.

## 21. ADOPT LATER / CONDITIONAL

### Schemathesis

Adopt after the backend Thin Product API contract is frozen.

Use for OpenAPI/property/stateful API testing.

It does not authorize frontend work.

### DSPy

Do not add to the production runtime.

Consider later as an OFFLINE optimizer only if, after V2.1 architectural closure, a specific cognition module remains manually weak.

Training/optimization data must be independent from the frozen 30-case benchmark.

### Temporal

Do not put Temporal inside Brain reasoning.

Future role:

~~~text
Decision
→ Action
→ approvals
→ ERP/email/Slack
→ scheduled follow-up
→ retry/receipt
~~~

Brain reasoning remains LangGraph.

### OpenLineage / DataHub

Future data-platform lineage/catalog layer only.

Never replace Dima Evidence epistemics.

### Cedar / OPA

Future authorization-policy layer only if policy complexity materially exceeds current code.

Do not migrate stable security now.

## 22. DO NOT ADD NOW

~~~text
Cube
MetricFlow
another semantic/query engine
another agent runtime
Letta runtime
OpenHands runtime
Temporal inside Brain
new graph database
new Evidence authority
~~~

Metabase + Cube/MetricFlow would create two analytics/semantic truths.

If Metabase is ever replaced, that must be a deliberate future migration, not additive architecture.

## 23. Wren role

Wren remains an architecture-review oracle, not a production runtime.

Keep learning from:

~~~text
explicit business context
schema linking
profiling
planning
validation
execution
memory/recall
golden evals
~~~

Do not copy Wren execution topology blindly into Dima.

---

# PROVIDER-FREE ACCEPTANCE

## 24. Candidate projector matrix

Prove at minimum:

1. effect + three observed governed candidate metrics → exactly those three eligible candidates;
2. unobserved governed metric → not projected;
3. observed metric outside allowed discovery surface → not projected;
4. effect metric → excluded;
5. unrelated dimension → not projected as mechanism;
6. wrong scope version → rejected;
7. historical Evidence → not a current candidate source;
8. duplicate observed binding → one candidate identity;
9. 30 observed metrics with only three allowed candidates → at most those three projected;
10. zero candidates → honest terminal;
11. one candidate → no fabricated competitor;
12. multiple candidates → all legal identities reach P19.

## 25. Sequence/stateful acceptance

Hypothesis must explore combinations:

~~~text
discovery
→ scope change
→ resume
→ report

discovery
→ NextTest
→ resume

discovery
→ checkpoint restart

scope change
→ discovery

report-only
→ discovery history remains stable
~~~

Section 14 invariants must hold after every step.

## 26. Non-regression

Provider-free prove:

~~~text
T1 scope/currentness family
T2 ONE_PASS
T3 ADAPTIVE
T4 DISCOVERY
T5 observational relationship
T6 contextual report
T7 multi-intent
security
restart/resume
P14 material legality
P18
P19
P20
completion
governance
~~~

No paid run while deterministic RED exists.

---

# LIVE A/B + FINAL READINESS

## 27. T4 V2.1 live

After provider-free GREEN and candidate freeze, run exactly one fresh T4 DISCOVERY live on V2.1.

Compare with the historical accepted T4 reference.

Required:

~~~text
native duplicate acquisitions = 0
P17 discovery provider calls = 0
CandidateSet contains >=2 distinct governed candidates
WHEN VERIFIED material exposes >=2 eligible candidates
P19 initial assessments = 1
causal overclaim = 0
mechanical = GREEN
manual quality >= 3/4
prefer 4/4
~~~

Efficiency must be materially no worse and should improve:

~~~text
provider requests
prompt tokens
latency
cost
~~~

## 28. T4 merge gate

Merge V2.1 discovery simplification only if:

~~~text
manual quality >= current accepted T4 quality
P17 discovery provider = 0
duplicate native = 0
candidate diversity improved or preserved
P19 reached legally
no safety regression
provider/token cost materially reduced or not increased
~~~

If not, reject the simplification branch.

Do not sacrifice quality for architectural purity.

## 29. Relationship optional live

Only if the T5 audit proves a redundant P17 provider call and a generic provider-free simplification is implemented:

run one fresh T5.

Require manual >= historical quality and no causality overclaim.

Otherwise do not spend on T5 for this reason.

## 30. Final affected live recertification

Because current head contains semantic changes after older READY receipts, final V2.1 candidate must have fresh evidence for every affected capability.

Minimum:

~~~text
T4 DISCOVERY fresh

T6 contextual reporting fresh
because current head changed P20/report synthesis

T7 multi-intent fresh
if shared Product/report/intake code changed
~~~

T1/T2/T3/T5 may be carried forward only with explicit backend/app non-affection proof from their sealed Product SHA to the final candidate.

If non-affection cannot be proved cheaply, run the affected surgical probe instead.

Do not broad-run.

## 31. 90+ readiness gate

On one final V2.1 semantic candidate:

~~~text
all affected mechanical gates GREEN
all targeted manual scores >= 3
targeted average >= 3.6/4
at least 5/7 FULL
T1 = 4
T2 = 4
T4 preferably = 4
T6 = 4
no exception
no silent wrong
no security violation
no unsupported causal promotion
duplicate native = 0
P17 discovery provider calls = 0
stateful/metamorphic panel GREEN
no unresolved architecture family
~~~

Then seal:

~~~text
90+ HIGH-CONFIDENCE READINESS = YES
30-CASE READY = YES
30-case = NOT RUN
frontend = NOT IMPLEMENTED
~~~

## 32. 30-case rule

The frozen 30-case remains forbidden until the user separately gives explicit authorization.

V2.1 work stops at:

~~~text
30-CASE READY
~~~

Only the separately authorized frozen benchmark can prove:

~~~text
90+ PROVEN
~~~

## 33. Frontend rule

Frontend / UI / UX remains absolutely forbidden.

No web UI, dashboard, Ask screen, Investigation screen, Evidence drawer, Report/Decision UI, demo frontend or visual polish until:

1. user authorizes the 30-case;
2. frozen benchmark scores >=90.0;
3. critical safety gates pass;
4. user separately authorizes UI/UX.

---

# PERMANENT ANTI-LOOP RULES

## 34. First ask who already owns the capability

Before adding code:

~~~text
Does Metabot already perform this analytics/exploration?

Does LangGraph already solve this orchestration/checkpoint problem?

Does Dima already have the canonical business/epistemic owner?

Can Hypothesis find this transition family before live?

Can OpenTelemetry make the first wrong boundary obvious?
~~~

Only write new Dima code for Dima-specific value.

## 35. One owner per truth

~~~text
Metabot
= analytical truth/material

Dima Scope/Research
= accepted business meaning

Evidence
= provenance/currentness

P19
= epistemic judgment

P18
= relationship semantics

P20
= governed synthesis/report

LangGraph
= orchestration

OpenTelemetry
= observation

Hypothesis
= test generation
~~~

Never duplicate an owner because integration is inconvenient.

## 36. No second analyst

Permanent:

~~~text
P17 != SECOND ANALYST
~~~

P17 may control investigation.

It may not redo Metabot analytics merely to choose candidate identities already visible in governed material.

## 37. No patch semantics

Forbidden:

~~~text
regex semantic routing
fuzzy matching
morphological routing
embedding threshold truth
prompt wording branch
fixture-specific branch
benchmark-specific branch
hardcoded metric/date/department
retry-until-lucky
provider ceiling inflation
~~~

## 38. No RED-by-RED paid debugging

A paid RED must produce:

~~~text
first_invalid_boundary
owner
generic invariant
provider-free reproducer
metamorphic sibling tests
~~~

Then fix the whole family.

No fresh paid run until deterministic family closure.

## 39. No architecture change because one stochastic answer was weak

Separate:

~~~text
mechanical architecture defect
vs
manual cognition quality
~~~

Architecture changes need a reproduced structural defect.

Model changes need a mechanically clean but cognitively weak case.

## 40. Engine rule

Engine dima.9 remains frozen for V2.1.

Expected:

~~~text
engine builds = 0
~~~

If a single deduplicated native acquisition still has an engine-owned defect:

STOP with exact reproducer.

Do not open dima.10 automatically.

---

# EXECUTION ORDER

## 41. Exact sequence

~~~text
1. seal V2.1 decision/branch
2. add CandidateSetProjector provider-free tests
3. implement deterministic candidate identity projection
4. route DISCOVERY: Evidence → CandidateSetProjector → P19
5. remove provider-backed P17 DISCOVERY from normal graph
6. keep P17 NextTest controller
7. expand Hypothesis sequence/stateful invariants
8. bridge existing BoundaryTrace/BrainRunTelemetry to OpenTelemetry
9. full affected provider-free closure
10. freeze V2.1 candidate
11. fresh T4 DISCOVERY live
12. accept/reject discovery simplification
13. audit T5 P17 call; modify only if redundancy is proven
14. fresh affected T6/T7 certification or exact non-affection proof
15. final stateful/metamorphic confidence
16. seal one final semantic Product
17. declare 90+ readiness / 30-CASE READY if earned
18. STOP
~~~

No 30-case.
No frontend.

## 42. Final handoff

Return only with:

~~~text
final branch HEAD
final semantic Product SHA
engine SHA/release/digest
engine builds = 0

CandidateSetProjector contract

P17 discovery provider calls
before / after

native acquisitions
before / after

T4 run/artifact/mechanical/manual

T5 audit result

T6 run/artifact/manual or non-affection proof

T7 run/artifact/manual or non-affection proof

Hypothesis stateful suite results

OpenTelemetry boundary instrumentation proof

provider calls/tokens/latency/cost

metamorphic panel

known remaining limitations

90+ HIGH-CONFIDENCE READINESS
YES/NO

30-CASE READY
YES/NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
~~~

# FINAL LAW

~~~text
METABASE / METABOT
IS THE SINGLE ANALYTICAL COGNITION ENGINE.

LANGGRAPH
ORCHESTRATES.

DIMA
OWNS MEANING, EVIDENCE, CANDIDATE IDENTITY,
EPISTEMICS, COMPLETION AND DECISIONS.

P19
JUDGES.

P18
JUDGES RELATIONSHIPS.

P20
SYNTHESIZES GOVERNED STATE.

P17
CONTROLS INVESTIGATION.

P17
DOES NOT COMPETE WITH METABOT.

HYPOTHESIS
FINDS STATE-MACHINE BUGS BEFORE LIVE MONEY.

OPENTELEMETRY
SHOWS THE FIRST WRONG BOUNDARY.

DO NOT SOLVE COMMODITY PROBLEMS TWICE.

DO NOT CREATE TWO TRUTHS.

DO NOT CREATE TWO ANALYSTS.

DO NOT PAY TO DISCOVER A BUG
THAT A PROVIDER-FREE SEQUENCE TEST CAN FIND.
~~~
