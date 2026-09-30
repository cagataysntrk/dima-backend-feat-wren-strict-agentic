# DIMA BRAIN V2 — TWO-PHASE ROADMAP

**Status:** ACTIVE / FORWARD AUTHORITY  
**Branch:** feat/dima-brain-v2  
**Branch point:** 8d1e011053b01005179ff7a31b7921bb3a7307b9  
**Legacy Product candidate at branch point:** c5069e8e4606e21bdd8ce41f4c1dc4bf7d23c789  
**Frozen analytical engine:** 0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c / 0.63.18-dima.8

## 1. Final decision

Dima V1 does **not** return to the historical ~70.8 Product candidate.

The historical candidate remains a golden control only.

The current domain primitives remain the forward foundation:

- Metabase / Metabot native analytics;
- ResearchBrief / ScopeVersion;
- native execution receipts;
- Evidence and current/historical lineage;
- P18 relationship semantics;
- P19 hypothesis/root-cause epistemics;
- P20 ReportDocument;
- Decision / Action / Outcome / Memory primitives;
- tenant, principal and security boundaries.

The component being replaced incrementally is the custom orchestration plumbing that decides which owner executes next, how progress is checkpointed, how workflow state resumes, and how the minimum context is projected to each cognition owner.

The V2 architecture is:

~~~text
METABASE / METABOT
= analytical cognition + native execution

LANGGRAPH
= orchestration runtime
= graph routing
= checkpoint / resume
= node execution state

DIMA DB
= canonical business + epistemic truth

THIN DIMA BRAIN
= accepted business semantics
= scope/currentness
= Evidence
= hypotheses / epistemics
= decisions / memory
= permissions
= owner-specific state views

DIMA UX
= projection of governed state
= no business truth authority
~~~

Permanent rule:

~~~text
LANGGRAPH STATE != DIMA TRUTH DATABASE
~~~

LangGraph checkpoints may store orchestration progress and references to Dima entities. They must not become a second Evidence, Scope, Hypothesis, Decision, or business-truth authority.

## 2. Why current branch, not the 70.8 historical candidate

The historical ~70.8 Product did not contain the current safety and intelligence foundations in their present form. Returning to it would require rebuilding scope lineage, current/historical Evidence, typed causal surfaces, direct-P19 user-seeded RCA, relationship intent separation, material observation and the dima.8 runtime corrections.

The current codebase already owns those assets.

The latest custom-orchestration live evidence also shows why the orchestration layer is the migration target rather than the domain model:

- historical ONE_PASS live: 20 provider requests, 16 Metabot/Metabase requests, 289,626 prompt tokens;
- latest F10 live on c5069e8...: 8 provider requests, 113,149 prompt tokens, but the next transition still failed with INTAKE_SCOPE_MUTATION_INVALID / NARROW_ENTITY must only narrow entity values.

The custom system is improving, but state-transition complexity continues to expose new orchestration seams. Brain V2 is a strangler migration over the current domain state, not a rollback and not a clean-room rewrite.

## 3. Framework decision

### LangGraph — ADOPT as orchestration runtime

Use low-level LangGraph primitives directly.

Do not adopt high-level generic agent abstractions as Dima authority.

Target pattern:

~~~text
State -> Node -> Partial State Update -> Conditional Edge
~~~

Use:

- StateGraph / explicit nodes;
- checkpointer;
- interrupt/resume where needed;
- node-local retry for transient transport failures;
- explicit conditional routing;
- small node-specific state projections.

### OpenHands / Letta / Temporal — patterns only in V1

Do not add these runtimes in Phase 1 or Phase 2.

Harvest only the relevant patterns:

- OpenHands: bounded event/state thinking and context condensation;
- Letta: small in-context working set + external/on-demand detail;
- Temporal: idempotent side-effect/activity discipline.

A second durable workflow runtime is forbidden in V1.

## 4. Licensing / distribution gate

LangGraph core is MIT-licensed and compatible with the backend Python runtime.

Metabase Open Source Edition remains subject to AGPL obligations. Before customer distribution/embedding, Dima must make an explicit commercial/legal decision between AGPL-compliant distribution and an appropriate Metabase commercial/embedding license.

This is a release/business gate, not a reason to duplicate Metabase analytics in Dima.

---

# PHASE 1 — LANGGRAPH ORCHESTRATION V2

## 5. Phase-1 objective

Prove that the same or better Dima analytical/research quality can be delivered with a materially simpler, cheaper and more durable orchestration path.

Do **not** migrate every capability at once.

Initial graph scope is deliberately narrow:

~~~text
START
  ↓
INTAKE
  ↓
CANONICALIZE
  ↓
ACQUIRE_MATERIAL
  ↓
ADMIT_EVIDENCE
  ↓
P19_ASSESS
  ├── SUFFICIENT ─────────────→ SYNTHESIZE / REPORT → END
  ├── INCONCLUSIVE ───────────→ HONEST_STOP → END
  └── NEXT_TEST_REQUIRED
             ↓
          P17_NEXT_TEST
             ↓
          ACQUIRE_MATERIAL
             ↓
          ADMIT_EVIDENCE
             ↓
          P19_ASSESS
~~~

Initial use cases:

1. user-seeded ONE_PASS RCA;
2. ADAPTIVE RCA with one discriminating re-entry;
3. DISCOVERY RCA with no user-seeded candidates;
4. one multi-turn scope mutation/resume case.

P18 relationship, general multi-intent, Action, Watch and full Decision Desk are not Phase-1 migration prerequisites unless required by the acceptance cases.

## 6. Code boundary

Create a new isolated package:

~~~text
backend/app/v3/brain_v2/
~~~

Recommended modules:

~~~text
state.py
views.py
keys.py
activities.py
nodes/
  intake.py
  canonicalize.py
  material.py
  evidence.py
  p19.py
  p17.py
  report.py
  terminal.py
graph.py
service.py
telemetry.py
~~~

No legacy Product file is deleted during the spike.

Legacy path remains available as frozen reference until the V2 acceptance gate is passed.

## 7. BrainGraphState

LangGraph state should be reference-oriented.

It may contain:

~~~text
thread_id
principal_ref
tenant_binding
research_session_id
scope_version_id
accepted_brief_ref
open_requirement_ids
material_requirement_ids
evidence_revision
evidence_ids
hypothesis_revision
hypothesis_ids
latest_p19_assessment_ref
pending_next_test_ref
report_ref
workflow_status
last_completed_node
activity_fingerprints
telemetry refs
~~~

It must not duplicate canonical Dima objects as an independent truth store.

Avoid storing full raw Evidence bodies, entire historical conversations, complete native result bodies, or formatted prompts in graph state.

## 8. Canonical truth ownership

All authoritative writes still go through the current Dima stores/owners.

Examples:

~~~text
ScopeVersion             -> existing Research authority
DimaQueryReceipt          -> existing execution/provenance authority
Evidence                  -> existing Evidence authority
HypothesisRecord          -> existing P19/Hypothesis store
RootCauseAssessment       -> existing P19 authority
ReportDocument            -> existing P20 authority
Decision / Action / Memory-> existing sealed owners
~~~

LangGraph nodes orchestrate these owners. They do not replace them.

## 9. Owner-specific StateView compiler

Each cognition node receives only its minimum working set.

### IntakeView

~~~text
current user input
current scope reference/summary
governed semantic catalog required for interpretation
prior accepted intent delta when relevant
~~~

### P19View

~~~text
objective
current scope
candidate hypotheses
deterministic EvidenceDigest index
support/challenge/context relations already governed
missing discrimination state
legal actions
~~~

### P17NextTestView

~~~text
objective
unresolved epistemic gap
current hypotheses
relevant EvidenceDigest[]
legal analytical actions
budget/depth
~~~

### ReportView

~~~text
accepted findings
epistemic state
Evidence refs/digests
limitations
decision implications
~~~

No node receives full conversation history by default.

## 10. Evidence paging

Create a deterministic EvidenceDigest projection.

It must be derived from governed Evidence and receipts, not LLM-written summary prose.

Conceptual fields:

~~~text
evidence_id
scope_version_id
state
metric_ids
dimension_ids
entity_ids
compact exact observation summary
hypothesis relations
receipt_ref
result_hash
~~~

Raw Evidence/native payload remains in the existing durable store and is loaded only when the node requests the exact Evidence IDs required for the current cognition step.

## 11. Cognition and activity idempotency

Create typed request keys.

Example:

~~~text
CognitionRequestKey:
  owner
  objective_id
  scope_version_id
  evidence_revision
  hypothesis_revision
  legal_action_profile_hash
  model_profile

NativeMaterialRequestKey:
  tenant
  principal
  scope_version_id
  material_requirement_fingerprint
  engine_identity
~~~

If canonical semantic input is unchanged and a safe persisted result already exists:

~~~text
provider call = 0
native duplicate execution = 0
~~~

No fuzzy equivalence.

No prompt-text similarity.

## 12. Information-gain gate

Every non-trivial cognition call has a typed purpose.

Allowed examples:

~~~text
INTERPRET_NEW_INTENT
ASSESS_NEW_EVIDENCE
DISCOVER_HYPOTHESES
DESIGN_DISCRIMINATING_TEST
REPAIR_SCOPE
SYNTHESIZE_REPORT
~~~

A call must not be made simply to re-read the same state, restate a previous result, or check whether unchanged state has changed.

For user-seeded ONE_PASS:

~~~text
P17 discovery = 0
P17 analytical re-entry = 0
~~~

unless P19 produces a legal NextTest requirement.

## 13. Side effects and checkpointing

Treat provider calls and native Metabase execution as idempotent external activities.

Node state must record the semantic request key and durable result reference before downstream routing.

Resume rules:

- a completed native execution must not be silently re-executed;
- a completed cognition request with unchanged semantic input must not be paid for twice;
- an interrupted graph resumes from durable progress;
- LangGraph checkpoint may be rebuilt from Dima truth + activity receipts if necessary.

For tests, an in-memory or SQLite checkpointer is acceptable.

For production candidate, use a supported Postgres-backed checkpointer in a separate orchestration schema/table namespace.

The checkpointer is operational state only.

## 14. Model policy

Default Phase-1 model:

~~~text
Luna
~~~

Run Terra only as a controlled same-candidate A/B when:

~~~text
mechanical architecture = GREEN
Luna manual quality <= 2/4
deterministic architecture defect = not found
~~~

Terra must provide a material quality increase to earn routing.

Sol is reference-ceiling only after Luna and Terra both prove insufficient on a genuine high-ambiguity cognition task.

No automatic cascade.

## 15. Graph safety

LangGraph must not introduce:

- silent retries of semantic failures;
- retry-until-lucky behavior;
- automatic mutation of Evidence/hypothesis truth;
- broad exception masking;
- unbounded cycles.

Transient network retry may be bounded at the activity/node boundary.

Semantic retry requires a changed typed state or explicit new information.

## 16. Legacy strangler strategy

Expose V2 through a separate service/route or explicit feature flag.

Conceptually:

~~~text
legacy:
HeadlessProductComposer / current Product path

v2:
BrainV2Service / LangGraph graph
~~~

No legacy call site is deleted until V2 wins the acceptance comparison.

The rollback mechanism during migration is routing back to the frozen legacy path, not git rollback to the historical 70.8 Product.

## 17. Phase-1 test ladder

### A. Provider-free characterization

Prove:

- state schema;
- Dima truth vs checkpoint boundary;
- idempotent cognition request reuse;
- idempotent native activity reuse;
- crash/resume;
- scope replacement;
- historical/current Evidence;
- user-seeded hypotheses;
- ONE_PASS;
- ADAPTIVE;
- DISCOVERY;
- security / tenant / principal;
- no duplicate native execution;
- no stale Evidence reuse;
- no unsupported causal promotion.

### B. Replay / shadow comparison

Replay the same deterministic fixtures through legacy and V2.

Compare:

~~~text
accepted scope
material requirement
Evidence identities/coverage
hypothesis identities
epistemic terminal
ReportDocument coverage
security outcome
~~~

V2 may be more efficient. It may not weaken correctness.

### C. Surgical live comparison

Run the same frozen ONE_PASS / ADAPTIVE / DISCOVERY requests on V2.

Luna first.

Do not run the 30-case benchmark.

## 18. Phase-1 acceptance

### ONE_PASS target

~~~text
Research Intake calls        <= 1
initial native acquisitions  = 1
P17 calls                    = 0
P19 assessments              = 1
duplicate native execution   = 0
blocked provider requests    = 0
~~~

Engineering SLO:

~~~text
total actual provider requests <= 8
prompt tokens                  <= 150k
~~~

Preferred target:

~~~text
total requests <= 6
~~~

The SLO is not business truth; it is an efficiency gate.

### ADAPTIVE target

Exactly one justified discriminating re-entry in the certification case.

~~~text
initial investigation
+ P19
+ one P17 NextTest
+ one new native material acquisition
+ P19 reassessment
~~~

Target:

~~~text
total provider requests <= 12
~~~

### DISCOVERY target

P17 discovers governed candidates only because the user supplied none.

No fake candidates and no duplicate investigation.

### Quality

Every live certification case:

~~~text
mechanical = GREEN
manual Product quality >= 3/4
~~~

Combined three-mode average:

~~~text
>= 3.3/4
~~~

At least ONE_PASS must be FULL / 4 before V2 migration is accepted.

## 19. Phase-1 exit

Phase 1 is GREEN only when:

- the V2 graph passes provider-free closure;
- ONE_PASS / ADAPTIVE / DISCOVERY are live-certified;
- V2 correctness is no worse than the legacy reference;
- ONE_PASS has material request/token/latency reduction;
- no second truth authority exists;
- resume/idempotency are proven;
- engine remains dima.8;
- 30-case remains unrun.

Then:

~~~text
LANGGRAPH ORCHESTRATION V2 = ACCEPTED
LEGACY CUSTOM ORCHESTRATOR = MAINTENANCE/FALLBACK ONLY
~~~

If V2 cannot match legacy quality or state correctness, stop the migration and retain current domain/runtime while reassessing the exact failure. Do not force framework adoption.

---

# PHASE 2 — THIN DIMA BRAIN + DEMO / UX LAYER

## 20. Phase-2 objective

Move engineering effort from orchestration plumbing into the actual Dima product experience.

Phase 2 does not thicken the backend.

It exposes the already-governed Brain V2 state through a thin Product/API projection and a minimal user-facing demo.

Target architecture:

~~~text
DIMA UX
   ↓
THIN PRODUCT API
   ↓
BRAIN V2 / LANGGRAPH
   ↓
DIMA DOMAIN STORES
   ↓
METABASE / METABOT
~~~

The UX never owns business or epistemic truth.

## 21. Thin Product API

Expose stable contracts for:

~~~text
Ask / submit intent
stream run progress
current scope
investigation timeline
Evidence list/detail
hypothesis / epistemic state
report
resume / clarification
current limitations
~~~

Prefer IDs/revisions and governed projections over raw internal traces.

Do not expose provider prompts/reasoning.

## 22. Streaming

Provide a bounded event stream suitable for UI.

Example event families:

~~~text
INTENT_ACCEPTED
SCOPE_UPDATED
ANALYSIS_STARTED
EVIDENCE_ADMITTED
HYPOTHESIS_STATE_UPDATED
NEXT_TEST_REQUESTED
REPORT_READY
LIMITATION_RECORDED
TERMINAL
~~~

Events are Product projections, not a new source of truth.

## 23. Demo UX surfaces

Minimum demo:

### 1. Ask

- user question;
- current company/scope context;
- progress states;
- final concise answer.

### 2. Investigation

- current question;
- scope;
- Evidence;
- candidate hypotheses;
- support/challenge state;
- requested next test if any.

### 3. Evidence Drawer

- Evidence digest;
- source/provenance;
- exact underlying values;
- current/historical status.

### 4. Report / Decision View

- observations;
- findings;
- hypotheses;
- limitations;
- next action / decision implications.

### 5. Conversation Scope Repair

- user narrows/changes scope;
- prior state remains historical;
- new state becomes current;
- UI makes the change visible.

Do not attempt the full 50-UX surface in this phase.

## 24. Demo-layer rules

The demo layer may:

- render;
- sort presentation-only data where semantics are already determined;
- request existing Brain actions;
- show progress;
- show provenance and limitations.

It may not:

- infer business semantics;
- invent claims;
- run SQL/MBQL;
- alter Evidence state;
- decide causality;
- override P18/P19/P20;
- silently repair failed backend semantics.

## 25. Demo data modes

Support two explicit modes:

~~~text
DEMO_FIXTURE
CONNECTED_COMPANY
~~~

Both must use the same Brain/API contracts.

No separate fake Product behavior for the demo.

## 26. Phase-2 capability certification

Before declaring 90+ readiness, certify on one frozen Brain V2 candidate:

1. scope/conversation repair;
2. ONE_PASS RCA;
3. ADAPTIVE RCA;
4. DISCOVERY RCA;
5. observational relationship;
6. contextual report;
7. multi-intent management synthesis.

Each receives two independent verdicts:

~~~text
mechanical verdict
manual Product-quality score 0–4
~~~

Workflow success is not Product-quality success.

## 27. 80+ readiness

Declare:

~~~text
80+ HIGH-CONFIDENCE READINESS
~~~

only if:

- all seven mechanical probes GREEN;
- every manual score >= 3/4;
- targeted average >= 3.3/4;
- no exception/silent-wrong/security/causal-overclaim defect;
- efficiency headroom is healthy.

## 28. 90+ readiness

Declare:

~~~text
90+ HIGH-CONFIDENCE READINESS
~~~

only if:

- targeted manual average >= 3.6/4;
- no case < 3;
- at least five of seven = FULL / 4;
- scope-repair = FULL;
- ONE_PASS RCA = FULL;
- at least one of ADAPTIVE / DISCOVERY / contextual report = FULL;
- independent metamorphic variants are GREEN;
- historically strong direct analytics/ranking/safety capabilities show no material regression;
- no known unresolved architecture family remains.

This is high-confidence readiness, not the measured final benchmark score.

## 29. Metamorphic confidence

Before 30-case readiness, vary:

- wording;
- metric;
- dimension;
- entity;
- date range;
- candidate mechanisms;
- department/category.

At minimum cover:

- scope mutation;
- one-pass RCA;
- adaptive RCA;
- observational relationship;
- contextual report;
- multi-intent.

No production benchmark IDs or prompt-specific branches.

## 30. 30-case rule

The 30-case benchmark remains forbidden until the user separately authorizes it.

Phase-2 exit may declare:

~~~text
30-CASE READY
~~~

but must stop there.

Only a later explicitly authorized frozen 30-case execution can prove:

~~~text
90+ PROVEN
~~~

## 31. Final benchmark acceptance when separately authorized

Pre-register scoring before the run.

Primary score = manual Product quality, not orchestration ritual.

Architecture/process trace is a separate report.

A real 90+ seal requires:

~~~text
Product Quality Score >= 90.0

0 hard exception
0 silent wrong
0 security violation
0 cross-tenant leakage
0 invented numeric truth
0 unsupported causal promotion

no feature family < 80

historically weak:
F05 / F06 / F07 / F08 / F10 >= 85 each

historically strong:
F02 / F03 / F09 no material regression
~~~

No rubric modification after seeing results.

## 32. Model-routing acceptance

Luna is default.

For any capability where Luna is mechanically GREEN and manually >= 3/4, do not spend on Terra.

Terra A/B is allowed only when the architecture is clean and Luna is manually <= 2/4.

Terra earns a route only with a material improvement.

Sol is reference-ceiling only after both fail for a genuine cognition reason.

## 33. Performance telemetry

Every V2 run records:

~~~text
native acquisitions
provider requests by owner
prompt/completion/reasoning tokens
latency
provider cost
manual quality
quality / provider call
quality / dollar
checkpoint/resume events
dedup hits
~~~

Do not persist private prompt/reasoning bodies.

## 34. Permanent anti-patterns

Forbidden in both phases:

~~~text
regex business semantics
fuzzy semantic authority
morphological patches
embedding-threshold truth
benchmark-specific branches
hardcoded fixture/date/department rules
retry-until-lucky
provider-limit inflation
Dima SQL/MBQL planner
second analytics engine
second Evidence authority
LangGraph checkpoint as business truth
~~~

## 35. Two-phase final sequence

~~~text
CURRENT PLATFORM
8d1e011... / c5069e8... / dima.8
      ↓
BRANCH
feat/dima-brain-v2
      ↓
PHASE 1
LANGGRAPH ORCHESTRATION V2
      ↓
provider-free + live mode certification
      ↓
V2 ACCEPTED
      ↓
PHASE 2
THIN DIMA BRAIN / DEMO UX
      ↓
targeted capability panel
      ↓
metamorphic confidence
      ↓
90+ HIGH-CONFIDENCE READINESS
      ↓
30-CASE READY
      ↓
STOP
      ↓
USER EXPLICIT AUTHORIZATION
      ↓
one frozen 30-case proof
~~~

## 36. Final product principle

~~~text
METABASE COMPUTES.

LANGGRAPH ORCHESTRATES.

DIMA GOVERNS,
INTERPRETS,
REMEMBERS
AND DECIDES.

THE UX SHOWS
THE GOVERNED BRAIN STATE.

COMMODITY WORKFLOW PLUMBING
IS NOT DIMA'S MOAT.

COMPANY SEMANTICS,
EVIDENCE,
EPISTEMICS,
DECISIONS
AND PRODUCT EXPERIENCE
ARE.
~~~
