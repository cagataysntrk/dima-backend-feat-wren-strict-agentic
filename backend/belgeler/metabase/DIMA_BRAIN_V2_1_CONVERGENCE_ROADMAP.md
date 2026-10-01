# DIMA BRAIN V2.1 CONVERGENCE ROADMAP

Status: ACTIVE / FORWARD AUTHORITY  
Branch: feat/dima-brain-v2-1-convergence  
Branch point: f910f705da5840b30ea776a85ff61aa545ced9f2  
Source branch: feat/dima-brain-v2  
Engine: d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88 / 0.63.18-dima.9  
Engine state: FROZEN. The one certified dima.9 build remains authoritative. A second engine build is forbidden without a new supervisor decision.

## 1. Final architecture decision

Brain V2 is preserved. There is no Brain V3.

V2.1 is a convergence and simplification track.

~~~text
METABASE / METABOT
= SINGLE ANALYTICAL COGNITION ENGINE

LANGGRAPH
= ORCHESTRATION
= ROUTING
= CHECKPOINT
= RESUME

DIMA
= INTENT
= SCOPE
= MATERIAL CONTRACT
= EVIDENCE
= CANDIDATE IDENTITY
= PROVENANCE
= COMPLETION
= DECISION / MEMORY

P19
= EPISTEMIC JUDGE

P18
= RELATIONSHIP JUDGE

P20
= GOVERNED SYNTHESIS / REPORT

P17
= INVESTIGATION CONTROLLER
= NEXT-TEST / RE-ENTRY CONTROL
!= SECOND ANALYST
~~~

Permanent law:

~~~text
Metabase computes.
LangGraph orchestrates.
Dima owns meaning and epistemics.
P17 no longer acts as a second stochastic analyst.
~~~

## 2. Why V2.1 exists

Brain V2 already proves the architecture can work.

The accepted/root-closure history includes strong results for Scope Repair, ONE_PASS, ADAPTIVE, Relationship, Reporting and Multi-intent.

The chronic weak family is DISCOVERY.

The recurring pattern is:

~~~text
Metabot produces useful governed analytical material
-> provider-backed P17 re-reads the same material
-> P17 chooses or rewrites candidate claims
-> candidate/claim/manager state diverges
-> new guards and retry-state are added
-> another transition edge fails
~~~

V2.1 removes this duplicate cognition responsibility instead of adding more guards.

## 3. Current branch-point RED

The V2.1 branch is intentionally based on the newest Brain V2 HEAD so that root-closure, T3/T4 fixes, typed P18 work and latest P20 work are not lost.

The current deterministic RED at the branch point is:

~~~text
report_document.py
NameError:
ResearchClaimRecord is not defined
~~~

This is a baseline code defect, not a new architecture problem.

It must be closed before semantic work.

## 4. Agent API remains forbidden

The Metabase Agent API is not authorized.

Brain V2.1 continues to use the certified self-hosted engine and Metabot native execution path.

Do not introduce:

~~~text
Metabase Agent API
parallel Metabase agent runtime
raw SQL fallback
Agent API fallback
MCP analytical production fallback
second query cognition engine
~~~

## 5. Engine remains frozen

~~~text
engine SHA
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88

release
0.63.18-dima.9

additional engine builds
0 authorized
~~~

No dima.10 is authorized.

If a single deduplicated native acquisition later proves an engine-owned defect, stop and produce an exact reproducer.

---

# STAGE 0 - CLEAN BASELINE

## 6. Close the current P20 deterministic RED

Before any refactor:

1. reproduce the NameError;
2. restore the missing P20 dependency/import;
3. run focused P20 and Brain V2 owner-integration tests;
4. run full Brain V2 provider-free closure;
5. prove the fix did not change Product semantics merely to satisfy CI.

No paid calls are authorized in Stage 0.

Stage-0 exit:

~~~text
provider-free GREEN
engine unchanged
paid calls = 0
~~~

---

# STAGE 1 - RETIRE PROVIDER-BACKED P17 DISCOVERY

## 7. Discovery owner decision

Provider-backed P17 candidate discovery is retired from the normal V2.1 DISCOVERY path.

Keep P17 for:

~~~text
durable investigation state
typed next-test / re-entry control
budget and depth guards
resume semantics
adaptive continuation
~~~

Retire from normal DISCOVERY:

~~~text
provider-backed mechanism selection
FORM_CLAIM candidate discovery loop
repeat-candidate manager loop
free stochastic candidate-vocabulary selection
~~~

Legacy discovery code may remain temporarily for comparison tests, but must not remain on the accepted V2.1 Product route.

## 8. Deterministic CandidateSetProjector

Create one bounded deterministic projector.

The projector is not an analytics engine.

Conceptually:

~~~text
CandidateSet
=
accepted governed candidate vocabulary
INTERSECT
current ScopeVersion
INTERSECT
VERIFIED observed governed material
MINUS
effect / outcome identity
~~~

Use the existing accepted ResearchBrief and scope semantic refs as the candidate vocabulary boundary.

Do not promote arbitrary query columns into causal candidates.

## 9. Candidate eligibility

A candidate may be projected only if all are true:

~~~text
candidate identity is already governed
candidate identity belongs to the accepted discovery surface
candidate identity is current-scope legal
VERIFIED Evidence actually exposes that governed material identity
candidate is not the effect/outcome identity
~~~

This prevents hypothesis explosion.

## 10. Candidate projector output

The projector emits identity and provenance only.

Conceptual form:

~~~text
semantic_id
source = OBSERVED_GOVERNED_MATERIAL
evidence_refs
scope_lineage_id
scope_version_id
~~~

It must NOT emit:

~~~text
causal strength
support probability
winner
dominant cause
correlation score
causal probability
~~~

Those belong to P19 or to Metabot analytical output where appropriate.

## 11. Durable hypotheses

For each projected candidate:

1. create or reuse the existing HypothesisRecord;
2. bind the exact candidate identity;
3. attach exact VERIFIED Evidence references;
4. use CONTEXT as the initial deterministic grounding ceiling where no stronger governed relation already exists;
5. invoke P19 once over the bounded candidate set.

Do not create a new Candidate truth store.

Do not create a Discovery graph database.

## 12. P19 owns epistemic assessment

P19 evaluates the complete bounded candidate set.

Legal outcomes include:

~~~text
supported observational candidate
challenged candidate
contested candidate
insufficient identification
honest inconclusive
typed discriminating Evidence gap
~~~

P19 must not exceed causal identification authority.

## 13. Discovery recursion

Recursion occurs only when P19 identifies a real information gap.

~~~text
P19 gap
-> existing P17 next-test controller
-> one bounded Metabot acquisition
-> new Evidence
-> P19 reassessment
~~~

Recursion is escalation, not ceremony.

## 14. Discovery KPI

Initial DISCOVERY target:

~~~text
P17 discovery provider calls = 0
duplicate Dima analytical acquisitions = 0
P19 initial assessments = 1
~~~

Do not make exactly-one-native-acquisition a universal business invariant.

Correct invariant:

~~~text
initial discovery uses minimum necessary bounded native work

additional acquisition occurs only because
a typed P19 Evidence gap requires it
~~~

## 15. Separate KPI layers

Always report separately:

~~~text
Dima analytical acquisitions
duplicate Dima analytical acquisitions
Metabot provider requests
P17 provider requests
P19 provider requests
~~~

Metabot may internally use multiple cognition/tool turns for one Dima acquisition.

That is different from Dima opening duplicate analytical acquisitions.

---

# STAGE 2 - RELATIONSHIP PATH AUDIT

## 16. Do not refactor a historical 4/4 capability blindly

First characterize the observational relationship path.

Question:

~~~text
When Metabot already produced
typed governed relationship material,
does a P17 provider call create
new analytical or epistemic value?
~~~

If yes, keep it until an owner-correct replacement exists.

If no, remove it from the normal observational path.

## 17. Preferred relationship flow

~~~text
Metabot native relationship analysis
-> VERIFIED typed relationship Evidence
-> P18
-> P20 / Product projection
~~~

P18 owns:

~~~text
association
co-movement
business-policy relationship
causal boundary
~~~

## 18. No Product-side statistics

Never replace P17 with deterministic Python analytics.

Forbidden:

~~~text
raw Evidence rows
-> Dima correlation/statistics
-> relationship conclusion
~~~

That would create a second analytics engine.

Analytical relationship statements must originate from Metabot/native analytics.

Dima may project their governed identity and provenance into P18.

---

# STAGE 3 - P20 CONVERGENCE

## 19. P20 final role

P20 remains:

~~~text
GOVERNED STATE
-> REPORT / SYNTHESIS
~~~

P20 must not:

~~~text
start analytics merely because a report was requested
recompute metrics
strengthen P19 conclusions
strengthen P18 authority
invent counter-Evidence
~~~

## 20. Close current P20 work

After the Stage-0 import fix, validate contextual synthesis against:

~~~text
scope repair
ONE_PASS
ADAPTIVE
DISCOVERY
relationship
contextual report
~~~

P20 may synthesize already-governed claims and limitations.

It may not become a new claim authority.

---

# STAGE 4 - PREVENT ERROR CLASSES BEFORE LIVE

## 21. Hypothesis state-machine testing - ADOPT NOW

Hypothesis already exists in backend test dependencies.

Expand it into a Brain V2 state-machine test layer.

Use RuleBasedStateMachine to generate transition sequences before paid live tests.

## 22. Required generated actions

Cover combinations of:

~~~text
initial ask
narrow entity
expand entity
change period
change metric
change candidate mechanisms
no-op mutation
same mutation twice
report-only follow-up
relationship follow-up
checkpoint restart
resume
ONE_PASS
ADAPTIVE next-test
DISCOVERY
honest stop
historical/current transition
~~~

## 23. Permanent state-machine invariants

At every generated state prove:

~~~text
one current ScopeVersion per lineage
historical Evidence never becomes current again
completed native work is not duplicated
checkpoint/resume preserves canonical state
no cross-tenant or cross-principal leakage
no semantic expansion without typed authority
no duplicate hypothesis identity for same scope/candidate
P19 never assesses ungrounded candidates
P18 never promotes observational state to causality
P20 never strengthens upstream truth
report-only does not trigger unnecessary analytics
~~~

The goal is to find transition bug number 51 provider-free, not in a paid live run.

## 24. OpenTelemetry - ADOPT NOW

Add OpenTelemetry instrumentation to Brain V2.1.

Observability only.

No Product authority.

Never persist full prompts or hidden reasoning.

## 25. Canonical spans

Instrument operations such as:

~~~text
dima.intent.interpret
dima.scope.resolve
dima.material.compile
dima.native.acquire
dima.evidence.admit
dima.discovery.project
dima.p17.next_test
dima.p19.assess
dima.p18.resolve
dima.p20.report
dima.graph.checkpoint
~~~

## 26. Useful attributes and events

~~~text
thread_id
scope_lineage_id
scope_version_id
scope_fingerprint
material_fingerprint
native_acquisition_id
evidence_revision
candidate_count
hypothesis_revision
dedup_hit
provider_requests
terminal_state
last_valid_boundary
first_invalid_boundary
error.type
~~~

Do not store:

~~~text
full prompt
hidden reasoning
secrets
unbounded raw sensitive result payloads
~~~

Desired diagnosis:

~~~text
RED
-> first_invalid_boundary
-> exact owner
-> exact state revision
~~~

without manual artifact archaeology.

## 27. Schemathesis - ADOPT AFTER HEADLESS API FREEZE

Do not add it before the API contracts are stable.

After headless API freeze, use Schemathesis stateful OpenAPI tests for flows such as:

~~~text
create investigation
-> mutate scope
-> resume
-> request report
-> fetch Evidence
-> continue investigation
~~~

This remains backend/API hardening.

It does not authorize frontend work.

---

# STAGE 5 - OPEN-SOURCE BOUNDARY

## 28. Runtime/tooling authorized now

~~~text
Metabase / Metabot
= analytics engine

LangGraph
= Brain orchestration

Hypothesis
= stateful/property testing

OpenTelemetry
= observability
~~~

No additional Brain runtime is authorized.

## 29. Future, not now

Temporal:

~~~text
future Action / Watch / approval / long-running external work
not Brain reasoning
~~~

DSPy:

~~~text
optional offline cognition optimization after V2.1 closure
independent train/validation only
30-case never used as train/dev/optimizer feedback
~~~

OpenLineage / DataHub:

~~~text
future enterprise data lineage/catalog
never Dima Evidence epistemics
~~~

Cedar / OPA:

~~~text
future policy layer only if authorization complexity requires it
~~~

## 30. Reference only

Do not add as parallel runtimes:

~~~text
Wren runtime
OpenHands
Letta
Cube
MetricFlow
second semantic/query engine
~~~

Wren remains an architecture review reference, not the Product runtime.

---

# STAGE 6 - ENGINE AND MODEL POLICY

## 31. Engine freeze

~~~text
dima.9
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88

additional build = forbidden
~~~

No dima.10.

## 32. Luna-first

Default cognition model:

~~~text
Luna
~~~

Terra gets one same-candidate A/B only when:

~~~text
mechanical architecture GREEN
Luna manual quality <= 2/4
no deterministic architecture defect explains weakness
~~~

Sol remains reference ceiling only.

Cascade remains NONE.

---

# STAGE 7 - PROVIDER-FREE CLOSURE

## 33. Required GREEN families

Before any fresh paid live:

~~~text
Brain V2/V2.1 owner integration
scope/currentness
material coverage
Evidence admission
CandidateSetProjector
P19
P18
P20
ONE_PASS
ADAPTIVE
DISCOVERY
checkpoint/resume
completion
security
Hypothesis state-machine suite
metamorphic variants
forbidden-surface audit
~~~

No deterministic RED enters paid testing.

## 34. Discovery metamorphic matrix

Vary:

~~~text
effect metric
candidate vocabulary
entity
period
dimension
number of legal candidates
number of observed candidates
candidate missing from Evidence
candidate observed but outside accepted vocabulary
historical Evidence
different ScopeVersion
three or more candidates
no defensible candidate
~~~

Prove:

~~~text
no candidate explosion
no arbitrary column promotion
no duplicate hypothesis identity
P19 receives all and only eligible observed candidates
P17 discovery provider calls = 0
no causal overclaim
~~~

---

# STAGE 8 - SURGICAL LIVE RECERTIFICATION

## 35. Do not rerun everything automatically

Fresh live is required only for semantically affected families.

V2.1 definitely affects:

~~~text
T4 DISCOVERY
T6 contextual report because current P20 semantics changed
~~~

T5 requires fresh live only if relationship simplification is merged.

T1/T2/T3/T7 may carry forward only with explicit backend/app non-affection proof plus provider-free metamorphic closure.

If their owning semantics change, recertify them.

## 36. T4 target

Fresh T4 must prove:

~~~text
minimum necessary initial native work
duplicate Dima acquisition = 0
P17 discovery provider calls = 0
candidate set >=2 when Evidence exposes >=2 eligible candidates
exact governed identities
P19 initial assessment = 1
blocked calls = 0
exception = 0
causal overclaim = 0
~~~

Manual target:

~~~text
4/4 FULL
~~~

A 3/4 outcome is acceptable only if the remaining limitation is genuinely data-identification limited rather than architecture limited.

## 37. T5 target if affected

~~~text
native typed relationship Evidence exists
P18 is the relationship authority
no Product-side statistics
P17 provider call = 0 if proven redundant
manual = 4/4
~~~

## 38. T6 target

~~~text
report-only new analytics = 0
governed claims preserved
limitations preserved
numeric provenance preserved
manual = 4/4
~~~

---

# STAGE 9 - FINAL READINESS

## 39. Desired panel

Target, without score hacking:

~~~text
T1 Scope Repair                4/4
T2 ONE_PASS                    4/4
T3 ADAPTIVE                    4/4
T4 DISCOVERY                   4/4 target
T5 Observational Relationship  4/4
T6 Contextual Report           4/4
T7 Multi-intent                4/4
~~~

Do not fabricate certainty to obtain a 4/4 when the data itself is identification-limited.

## 40. 90+ high-confidence readiness

Declare only when:

~~~text
all affected mechanical probes GREEN
all capabilities >=3
targeted average >=3.6/4
at least 5/7 FULL
independent metamorphic panel GREEN
Hypothesis state-machine suite GREEN
known architecture defect families = 0
exception = 0
silent wrong = 0
security violation = 0
unsupported causal promotion = 0
duplicate acquisition = 0 for identical material needs
provider headroom healthy
~~~

## 41. 30-CASE READY

Declare 30-CASE READY only on one frozen Product candidate after the readiness gate is satisfied.

Then STOP.

The 30-case benchmark remains forbidden until the user separately and explicitly authorizes it.

Only a later frozen 30-case Product Quality Score >=90.0 may be called:

~~~text
90+ PROVEN
~~~

---

# STAGE 10 - FRONTEND / UI / UX FREEZE

## 42. Absolute ban

Do NOT implement:

~~~text
frontend
web UI
dashboard
Ask screen
Investigation screen
Evidence drawer
Report screen
Decision UI
demo frontend
React or Next.js Product surfaces
UX animations
~~~

during V2.1.

UI/UX requires all of:

~~~text
user explicitly authorizes 30-case
frozen 30-case score >=90.0
critical safety/mechanical gates pass
user separately authorizes UI/UX
~~~

Until then:

~~~text
frontend changes = 0
~~~

---

# STAGE 11 - PERMANENT ANTI-PATTERNS

Forbidden:

~~~text
regex semantic routing
fuzzy semantic authority
morphological patches
embedding-threshold truth
prompt wording branches
benchmark-specific logic
fixture-specific logic
hardcoded month/metric/department fixes
retry-until-lucky
provider-limit inflation
Dima SQL planner
Dima MBQL planner
Dima statistics/correlation engine
second analytics engine
second Evidence authority
second orchestration runtime
Metabase Agent API
~~~

Every fix must generalize to another company, metric, dimension, date range, wording and candidate set.

---

# STAGE 12 - COMMIT AND CI DISCIPLINE

## 43. Small coherent commits

Suggested order:

~~~text
fix(v2.1):
restore P20 baseline integrity

test(v2.1):
characterize deterministic discovery candidate projection

feat(v2.1):
project observed governed candidate set

feat(v2.1):
route DISCOVERY Evidence -> candidates -> P19

test(v2.1):
prove provider-backed discovery is absent

test(v2.1):
add discovery metamorphic siblings

test(v2.1):
expand Hypothesis Brain state machine

obs(v2.1):
add OpenTelemetry Brain boundary tracing

test(v2.1):
characterize relationship P17 value

fix(v2.1):
remove redundant relationship P17 only if proven redundant

test(v2.1):
close contextual P20 report

ci(v2.1):
full provider-free freeze
~~~

## 44. CI cadence

During development:

~~~text
focused local/provider-free
-> small commit
~~~

At coherent milestones:

~~~text
affected CI
~~~

At final candidate:

~~~text
full provider-free
+ stateful
+ metamorphic closure
~~~

Only then paid live.

---

# STAGE 13 - STOP CONDITIONS

Stop only if:

~~~text
engine source change becomes necessary
Metabot cannot expose governed observed candidate material without engine change
new analytical planner/statistics engine is proposed
P14/P18/P19 authority must be weakened
security boundary must be weakened
new durable truth family appears necessary
LangGraph would need to become business/epistemic truth
two coherent deterministic candidate-projection designs fail generically
~~~

Normal provider-free failures are not STOP conditions.

---

# FINAL LAW

~~~text
NO NEW BRAIN VERSION.

NO NEW ANALYTICS ENGINE.

NO SECOND STOCHASTIC ANALYST.

METABOT DOES ANALYTICS.

DIMA BOUNDS THE MATERIAL
AND PROJECTS GOVERNED IDENTITY.

P19 JUDGES THE EVIDENCE.

P17 CONTROLS INVESTIGATION
ONLY WHEN NEW INFORMATION IS REQUIRED.

LANGGRAPH ROUTES AND RESUMES.

HYPOTHESIS SEARCHES
THE STATE-TRANSITION SPACE
BEFORE USERS DO.

OPENTELEMETRY SHOWS
THE FIRST INVALID BOUNDARY.

P20 REPORTS GOVERNED TRUTH.

30-CASE IS THE FINAL PROOF,
NOT THE DEBUG LOOP.

FRONTEND DOES NOT START
UNTIL 30-CASE >=90
AND THE USER EXPLICITLY AUTHORIZES IT.
~~~
