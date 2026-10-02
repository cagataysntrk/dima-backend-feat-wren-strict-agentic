# DIMA BRAIN V2.1 — FINAL ARCHITECTURE & PRODUCT FOUNDATION

> **Status:** FINAL / ARCHITECTURE FROZEN  
> **Branch:** `feat/dima-brain-v2-1-discovery-simplification`  
> **Documentation consolidation source HEAD:** `ed95d22a3dee4c3e3cac8932ebd3050a6c0d691e`  
> **Final semantic Product SHA:** `ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9`  
> **Engine:** `d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88` / `0.63.18-dima.9`  
> **Engine digest:** `sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7`  
> **Engine builds in V2.1:** `0`

This document is the canonical technical explanation of the final Brain V2.1 architecture.
It explains the architecture from first principles, identifies the permanent owner of every
truth and transition, maps the codebase to those responsibilities, and records how the
backend foundation supports the future Product/UX layer.

It is intentionally not a historical diary. Superseded decisions, roadmaps, receipts,
pre-development reviews and recovery notes are archived under `legacy/`. Nothing under
`legacy/` is current execution authority unless this current documentation set explicitly
cites it as historical evidence.

For new development, read this document together with:

- `DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md`
- `DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md`
- `DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md`

The authoritative documentation entry point is `README.md` in this directory.

---

## 1. What Dima Brain V2.1 is

Dima Brain V2.1 is the governed company-intelligence runtime behind Dima.

It is not a chatbot runtime and it is not a second BI engine. It is a controlled system that:

1. accepts a user's business requirement;
2. resolves the governed business meaning and scope;
3. compiles the minimum analytical material need;
4. obtains analytical material from Metabase/Metabot;
5. admits only provenance-valid Evidence;
6. dispatches each requirement to the correct deterministic/epistemic owner;
7. tracks whether each USER_MUST requirement is actually terminal;
8. produces governed synthesis only after upstream outcomes are terminal;
9. persists enough reference state for checkpoint/resume without replaying paid work.

The core design goal is **one truth owner per responsibility**.

---

## 2. Permanent architecture in one picture

~~~text
USER
  |
  v
DIMA INTENT / RESEARCH INTAKE
  |
  v
SCOPE / ScopeVersion
  |
  v
USER_MUST REQUIREMENTS
  |
  v
REQUIREMENT DISPATCH
  |
  +----------------------+-----------------------+----------------------+
  |                      |                       |                      |
  | DIRECT / RANKING     | RELATIONSHIP          | ROOT CAUSE           | REPORT
  |                      |                       |                      |
  v                      v                       v                      |
MATERIAL GROUPS       MATERIAL GROUPS        MATERIAL GROUPS            |
  |                      |                       |                      |
  +-----------+----------+-----------+-----------+                      |
              |                      |                                  |
              v                      v                                  |
        METABASE / METABOT   METABASE / METABOT                        |
              |                      |                                  |
              +-----------+----------+                                  |
                          v                                             |
                   VERIFIED EVIDENCE                                   |
                          |                                             |
             +------------+-------------+                               |
             |                          |                               |
             v                          v                               |
      Direct Evidence terminal        P18                              |
             |                 RelationshipResult                      |
             |                          |                               |
             |                          +---------------+               |
             |                                          |               |
             |          CandidateSetProjector           |               |
             |                    |                     |               |
             |                    v                     |               |
             |                   P19                    |               |
             |              RCA epistemics              |               |
             |                    |                     |               |
             |          genuine information gap         |               |
             |                    |                     |               |
             |                    v                     |               |
             |             P17 NextTest only            |               |
             |                    |                     |               |
             |                    v                     |               |
             |             METABOT -> EVIDENCE ---------+               |
             |                                                          |
             +---------------------------+------------------------------+
                                         v
                                COMPLETION LEDGER
                                         |
                             all required upstream terminal
                                         |
                                         v
                                        P20
                                 GOVERNED SYNTHESIS
                                         |
                                         v
                                      REPORT
~~~

The graph is intentionally asymmetric.

- Analytics flows through Metabot.
- Relationship epistemics flows through P18.
- RCA epistemics flows through P19.
- P17 appears only when P19 identifies a real information gap.
- P20 appears only after terminal governed state exists.
- Presentation-only continuation does not reopen analytics.

---

## 3. The authority matrix

| Concern | Permanent owner | Owns | Must not own |
|---|---|---|---|
| Business requirement | Dima Research/Requirement contracts | accepted USER_MUST intent | SQL/MBQL/query cognition |
| Scope | Dima ScopeVersion + reducer | entity, period, metric, dimensions, currentness | report formatting |
| Material need | Dima typed material contracts | minimum required analytical surface | analytical answer |
| Analytical computation | Metabase / Metabot | query cognition, analytical material, native result | product/business meaning |
| Evidence | Dima Evidence/provenance layer | currentness, tenant/principal/scope/material/receipt/result identity | causal judgment |
| Candidate identity | CandidateSetProjector | legal governed candidate identity | support score, probability, causal rank |
| Relationship meaning | P18 | observational relationship epistemics | new analytics, causality promotion, scope mutation |
| RCA meaning | P19 | hypothesis epistemics and terminal RCA judgment | query execution |
| Investigation re-entry | P17 | typed NextTest control only | normal discovery or relationship analysis |
| Requirement completion | Completion Ledger | per-MUST terminal accounting | analytical interpretation |
| Synthesis/report | P20 | governed presentation from terminal state | reopening analytics |
| Orchestration | LangGraph | node routing, checkpoint, resume | business truth |
| Observability | BoundaryTrace/OpenTelemetry | boundary telemetry | Product authority |
| Sequence testing | Hypothesis | transition-space exploration | runtime behavior |

Permanent shorthand:

~~~text
METABOT = ANALYST
LANGGRAPH = ORCHESTRATOR
DIMA = MEANING + SCOPE + EVIDENCE + PROVENANCE + COMPLETION
P18 = RELATIONSHIP JUDGE
P19 = RCA JUDGE
P17 = INFORMATION-GAIN CONTROLLER
P20 = GOVERNED SYNTHESIS
~~~

---

## 4. Why the architecture is split this way

Earlier generations repeatedly failed when one layer silently started doing another
layer's job. The final architecture therefore separates six different kinds of truth:

~~~text
Requirement
!= Scope
!= Material Need
!= Evidence
!= Epistemic Outcome
!= Presentation
~~~

Important consequences:

- a user requirement is not a query;
- a goal is not a material plan;
- ordering is not ranking;
- association is not business policy;
- association is not causality;
- process completion is not USER_MUST fulfillment;
- a report request is not new analytics;
- one shared material package does not automatically fulfill every requirement.

This separation is the single most important rule in the codebase.

---

## 5. Forward runtime: one orchestrator only

The only forward Product runtime is:

~~~text
BrainV2Service
-> LangGraph StateGraph
-> typed activities / owners
~~~

Key files:

- `backend/app/v3/brain_v2/service.py`
- `backend/app/v3/brain_v2/graph.py`
- `backend/app/v3/brain_v2/state.py`
- `backend/app/v3/brain_v2/activities.py`
- `backend/app/v3/brain_v2/owner_adapter.py`

`HeadlessProductComposer` is historical fallback/reference only.
It is not a valid place for new Product capability, semantic fixes or final certification.

Final CI guards enforce:

~~~text
all final probes -> BrainV2Service / LangGraph
legacy final calls = 0
Agent API calls = 0
~~~

---

## 6. State design: references, revisions and authority

Brain state is not a dumping ground for owner internals.

The graph should carry durable references and monotonic revisions, not duplicate domain truth.

Representative state responsibilities include:

- thread identity;
- tenant/principal binding;
- research session reference;
- ScopeVersion;
- USER_MUST requirement refs;
- MaterialGroup refs;
- Evidence refs/revision;
- candidate/hypothesis refs/revision;
- P18/P19 terminal refs;
- completion revision;
- presentation revision;
- report ref;
- activity fingerprints;
- workflow terminal status.

The state object must never become a second store for:

- raw SQL/MBQL result bodies;
- provider hidden reasoning;
- full owner-internal objects;
- duplicated relationship/result truth;
- duplicated P19 truth.

Canonical stores remain authoritative.

---

## 7. Scope and follow-up semantics

Scope is versioned product truth.

A follow-up is a typed patch, not a free reconstruction.

Permanent mutation semantics:

~~~text
omitted facet -> inherit
explicit CLEAR -> clear
explicit replacement -> replace
no-op patch -> no semantic mutation
same mutation twice -> idempotent result
~~~

One deterministic reducer produces the next ScopeVersion.

ScopeVersion, ResearchRevision and PresentationRevision are intentionally independent.

Therefore:

- narrowing entity changes ScopeVersion;
- changing period changes ScopeVersion;
- report-only continuation does not change ScopeVersion;
- report-only continuation does not create a new analytical acquisition;
- previous Evidence becomes historical after a scope change and cannot silently become current.

Relevant files:

- `backend/app/v3/research_contracts.py`
- `backend/app/v3/research_intake.py`
- `backend/app/v3/research_product.py`
- `backend/tests/test_v3_research_scope_patch.py`
- `backend/tests/test_v3_research_scope_patch_stateful.py`

---

## 8. Requirements: USER_MUST is immutable authority

Every accepted user obligation that must be satisfied is represented as a requirement.

Examples:

- direct analytical fact;
- ranking;
- observational relationship;
- root-cause analysis;
- report/presentation.

The accepted USER_MUST set is authority.
Analytical lifecycle state must not erase a presentation requirement or silently add a new MUST.

Requirement routing is deterministic and typed.

File:

- `backend/app/v3/brain_v2/requirement_dispatch.py`

Permanent routing:

~~~text
DIRECT / RANKING -> Evidence terminal
RELATIONSHIP     -> P18
ROOT_CAUSE       -> CandidateSetProjector -> P19
REPORT           -> P20 after analytical completion
~~~

No LLM decides the owner by reading source wording.

---

## 9. MaterialGroup: minimum analytical work

A MaterialGroup is a transient execution projection.

It is **not** semantic truth and it is **not** another query planner.

It binds:

~~~text
MaterialGroup
  material_group_id
  anchor_requirement_id
  ScopeVersion
  consumer_requirement_ids[]
  required metrics
  required dimensions
  required periods
  required filters
  material_fingerprint
~~~

Compatible requirements may share one group.

Example:

~~~text
Ranking downtime by department ----+
                                    +-> MaterialGroup M1 -> one native acquisition
Downtime/fault relationship --------+
~~~

But shared material does not imply shared fulfillment.

The Evidence produced by M1 has explicit consumers.
Ranking may terminate directly from Evidence while relationship still requires P18.

Files:

- `backend/app/v3/brain_v2/material_groups.py`
- `backend/app/v3/research_analytical_scope.py`
- `backend/app/v3/analytical_request_contract.py`
- `backend/tests/test_v3_brain_v2_material_groups.py`
- `backend/tests/test_v3_brain_v2_material_stateful.py`

Permanent invariant:

~~~text
same semantic material fingerprint + same legal revisions
-> duplicate native execution = 0
~~~

---

## 10. Metabase / Metabot boundary

Metabase/Metabot is the only analytical cognition engine.

Dima may define the analytical requirement.
Dima may validate the result.
Dima may decide what the result is allowed to mean.

Dima may not become a SQL/MBQL planner or hidden statistics engine.

Metabot owns:

- analytical exploration;
- native analytical material;
- query cognition;
- provider-assisted analytics within the Metabase boundary.

Dima owns:

- allowed semantic surface;
- tenant/principal/scope;
- material contract;
- Evidence admission;
- epistemic interpretation.

Files:

- `backend/app/v3/research_native_gateway.py`
- `backend/app/v3/substrate/metabase/native_engine.py`

Final runtime rule:

~~~text
MB_AGENT_API_ENABLED = false
Agent API request count = 0
~~~

---

## 11. Native material validation

Physical query shape is not semantic authority.

Dima evaluates normalized native observations against typed expectations.

Permanent relationship:

~~~text
required semantic observation
subset-of
observed semantic observation
subset-of
allowed semantic observation
~~~

Equivalent physical query forms may be accepted.
Wrong business identity may not.

Hard-fail drift includes:

- wrong tenant;
- wrong entity;
- wrong metric;
- wrong time range/grain;
- ungoverned semantic identity;
- scope mismatch;
- material fingerprint mismatch.

This rule prevents overfitting Product correctness to one SQL/MBQL spelling.

---

## 12. Evidence: the provenance firewall

Evidence is admitted only after the native occurrence is verified against current authority.

Each current Evidence item is bound to:

~~~text
tenant
principal
research session
ScopeVersion
material fingerprint
receipt
result hash
execution timestamp
currentness
~~~

Evidence is not just data.
It is governed data plus provenance plus currentness.

After a scope mutation:

~~~text
old Evidence -> historical
new Evidence -> current
~~~

Historical Evidence may be shown explicitly as history, but cannot silently support current P18/P19/P20 judgment.

Core files:

- `backend/app/v3/research_manager.py`
- `backend/app/v3/claim_lineage.py`
- `backend/app/v3/brain_v2/owner_adapter.py`

---

## 13. Direct and ranking requirements

Direct and ranking requirements are analytically fulfilled from governed Evidence when their typed material need is satisfied.

They do not require P18 or P19 merely because those engines exist.

This matters for multi-intent flows.

Example T7:

~~~text
Ranking requirement
-> Evidence terminal

Relationship requirement
-> P18 RelationshipResult

Report requirement
-> P20 after both terminal
~~~

The graph must not force all requirements through one generic analyst.

---

## 14. Discovery: CandidateSetProjector

Normal Discovery was one of the major V2.1 simplifications.

Permanent path:

~~~text
Metabot
-> VERIFIED Evidence
-> CandidateSetProjector
-> P19
~~~

P17 provider calls in normal Discovery:

~~~text
0
~~~

CandidateSetProjector is deterministic governed identity projection.

Its legal set is:

~~~text
allowed discovery surface
intersection current ScopeVersion
intersection VERIFIED observed material
intersection candidate-eligible governed semantics
minus effect/outcome identity
~~~

It may produce only identity/provenance such as:

- semantic id;
- current scope version;
- exact Evidence refs;
- material requirement ref;
- source = observed governed material.

It may not produce:

- probability;
- support/challenge score;
- root-cause ranking;
- correlation;
- causal conclusion;
- dominant cause.

Files:

- `backend/app/v3/brain_v2/discovery_candidate_design.py`
- `backend/tests/test_v3_brain_v2_discovery_candidate_design.py`
- `backend/tests/test_v3_brain_v2_discovery_stateful.py`

Cardinality rules:

~~~text
0 -> honest terminal
1 -> one real candidate; never fabricate a rival
2+ -> all legal candidates may reach P19
~~~

---

## 15. P19: root-cause epistemic owner

P19 consumes governed candidate identities and current Evidence.

It owns the epistemic judgment:

- what Evidence supports;
- what Evidence challenges;
- what remains open;
- whether a discriminating test is needed;
- whether the current case is sufficient/inconclusive.

P19 does not execute analytics.

Files:

- `backend/app/v3/hypothesis_root_cause.py`
- `backend/app/v3/hypothesis_root_cause_provider.py`
- `backend/app/v3/brain_v2/p19_context.py`
- `backend/tests/test_v3_p19_hypothesis_root_cause.py`
- `backend/tests/test_v3_p19_provider.py`

Important epistemic law:

~~~text
observational association != causality
~~~

A useful RCA may end with uncertainty if the Evidence does not justify causal promotion.

---

## 16. P17: information-gain controller only

P17 no longer owns normal discovery.
P17 no longer owns normal observational relationship analysis.

Permanent use:

~~~text
P19 detects exact information gap
-> typed NextTestRequest
-> P17 controls one bounded re-entry
-> Metabot acquisition
-> new VERIFIED Evidence
-> P19 reassessment
~~~

P17 may own:

- bounded adaptive depth;
- typed next-test control;
- durable investigation audit;
- explicit investigation-control audit surfaces.

P17 may not own:

- free-form normal discovery;
- normal relationship cognition;
- second-analyst re-reading of Metabot results;
- retry-until-lucky behavior.

T3 ADAPTIVE proves this topology: exactly one discriminating re-entry.

---

## 17. P18: relationship epistemic owner

Normal observational relationship is now:

~~~text
Metabot
-> VERIFIED Evidence
-> bounded P18 interpretation
-> immutable RelationshipResult
-> Completion / P20
~~~

P17 relationship provider calls:

~~~text
0
~~~

P18 owns relationship meaning, not analytics.

P18 may classify the current Evidence into a governed relationship outcome and record:

- requirement id;
- scope version;
- relationship intent;
- disposition;
- support Evidence refs;
- challenge Evidence refs;
- limitations;
- policy resolution;
- epistemic ceiling;
- fingerprint.

P18 may not:

- execute Metabot;
- request new analytics directly;
- mutate scope;
- invent metrics;
- create RCA hypotheses;
- promote causality;
- silently apply business policy;
- compute hidden statistics and present them as governed truth.

Relationship material modes remain explicit.

~~~text
CROSS_SECTIONAL_ASSOCIATION
TEMPORAL_CO_MOVEMENT
~~~

Cross-sectional material may justify cross-sectional association only.
It must not be phrased as established temporal co-movement.

If a relationship interpretation genuinely needs missing analytical material, the correct action is a typed material gap routed back to Metabot — not a hidden calculation inside P18.

Files:

- `backend/app/v3/p18_relationship_interpreter.py`
- `backend/app/v3/business_relationship_v1.py`
- `backend/app/v3/business_relationship_policy.py`
- `backend/tests/test_v3_p18_relationship_interpreter.py`
- `backend/tests/test_v3_p18_relationship_result.py`
- `backend/tests/test_v3_p18_relationship_stateful.py`

### Exact salient Evidence cells

For manager-quality synthesis, P18 may select only legal references to exact current Evidence cells.

The model is not allowed to invent row/column coordinates.

Permanent chain:

~~~text
current VERIFIED Evidence
-> deterministic closed legal EvidenceCellRef set
-> P18 selects only legal refs
-> refs resolve to exact current Evidence/receipt/result
-> P20 may render exact values with provenance
~~~

This closes the magnitude/provenance problem without creating a second analytics engine.

---

## 18. Business policy remains separate from observational relationship

For normal observational relationship:

~~~text
business_policy_required = false
~~~

A NOT_REQUIRED audit result is legal.

P18 relationship judgment must not imply that a business policy was actually applied.

Business relationship policy and observational association are separate concepts even if they share infrastructure.

This distinction prevents:

~~~text
association -> accidental business-policy truth
~~~

and:

~~~text
business-policy relation -> accidental causality
~~~

---

## 19. Completion Ledger: terminal accounting

Process termination and requirement fulfillment are different concepts.

Every USER_MUST must end as one of:

~~~text
FULFILLED
LIMITED
INCONCLUSIVE
BLOCKED
~~~

with either:

- a `fulfilled_by_ref`, or
- an explicit limitation/block reason.

One shared Evidence package must never blanket-fulfill unrelated requirements.

Completion consumes the terminal refs for each owner.

Typical multi-intent result:

~~~text
g_ranking      -> FULFILLED by Evidence ref
g_relationship -> FULFILLED/LIMITED by RelationshipResult ref
d_report       -> FULFILLED by P20 report ref
~~~

P20 is not allowed to decide whether its own upstream requirements were fulfilled.

---

## 20. P20: governed synthesis

P20 consumes terminal governed state.

It does not reopen analytics.

Permanent precondition:

~~~text
required analytical obligations terminal
-> Completion Ledger
-> P20
~~~

P20 may synthesize:

- what happened;
- where;
- exact governed magnitude;
- relationship/RCA finding;
- Evidence/provenance;
- limitations;
- conservative management implication.

Raw governed numeric statements may exist as internal primitives.
The user-facing projection should synthesize them into management meaning without dropping provenance.

Files:

- `backend/app/v3/report_document.py`
- `backend/tests/test_v3_p20_report_document.py`

---

## 21. Presentation-only continuation

A report-only follow-up is not a research turn.

Permanent behavior:

~~~text
existing terminal governed state
-> new PresentationRevision
-> Completion/P20
~~~

No change to:

- Research authority;
- ScopeVersion;
- native acquisitions;
- P17;
- P18;
- P19.

T6 final proof seals:

~~~text
report-turn native delta = 0
P17 delta = 0
P18 delta = 0
P19 delta = 0
scope delta = 0
P20 report = 1
~~~

This is a critical future UX primitive: users can ask Dima to turn an existing investigation into a management report without paying for or mutating analytics.

---

## 22. LangGraph orchestration model

LangGraph owns orchestration, not meaning.

The graph routes typed state through nodes such as:

- intake;
- scope/canonicalize;
- requirements plan;
- material-group execution;
- Evidence admission;
- candidate projection;
- P18 adjudication;
- P19 assessment;
- P17 NextTest;
- completion evaluation;
- P20 report;
- terminal nodes.

Key file:

- `backend/app/v3/brain_v2/graph.py`

Node design rules:

1. one node should have one owner-responsibility;
2. state transition must be explicit;
3. business truth stays in canonical owner/store;
4. checkpoint/resume must not replay completed paid/native activity;
5. routing decisions should be derived from typed state, not keyword matching.

---

## 23. Checkpoint, resume and idempotency

Checkpoint/resume is a first-class Product requirement.

A resumed run must not:

- repeat an already completed native acquisition;
- repeat a completed provider activity;
- revive stale Evidence as current;
- lose tenant/principal binding;
- skip USER_MUST completion accounting.

Identity is protected through:

- activity fingerprints;
- revisions;
- scope/material fingerprints;
- durable refs;
- graph checkpointer.

Files:

- `backend/app/v3/brain_v2/checkpoint.py`
- `backend/tests/test_v3_brain_v2_postgres_checkpoint.py`

Permanent law:

~~~text
same semantic activity + same revisions/fingerprint
-> duplicate provider/native work = 0
~~~

---

## 24. Telemetry and first-wrong-boundary debugging

Observability exists to reveal the first authority break.

The Product must not require reading thousands of log lines to understand a RED.

Key boundaries include:

~~~text
dima.intent.interpret
dima.scope.resolve
dima.requirements.plan
dima.material.compile / material.group
dima.native.execute
dima.evidence.admit
dima.discovery.project_candidates
dima.p18.adjudicate
dima.p19.assess
dima.p17.next_test
dima.completion.evaluate
dima.p20.report
~~~

A useful RED receipt should expose:

- last_valid_boundary;
- first_invalid_boundary;
- requirement_id;
- material_group_id;
- scope fingerprint;
- material fingerprint;
- expected owner;
- observed owner;
- error.type.

Never export:

- raw provider prompts;
- hidden model reasoning;
- secrets;
- full Evidence payloads;
- raw SQL result bodies.

Files:

- `backend/app/v3/brain_v2/telemetry.py`
- `backend/tests/test_v3_brain_v2_telemetry.py`

---

## 25. Security and tenant isolation

Every current-state path is tenant/principal bound.

The architecture must hard-fail:

- cross-tenant state reuse;
- foreign principal resume;
- Evidence ownership mismatch;
- scope/currentness mismatch;
- unauthorized semantic identity reuse.

Security is not a reporting concern and may not be relaxed to make a Product test pass.

Final readiness receipt:

~~~text
security violation = 0
cross-tenant violation = 0
~~~

---

## 26. Stateful and metamorphic quality plane

Provider-free sequence testing is a core architectural layer, not optional test polish.

Final floors:

~~~text
Material/state reducer = 1000 examples, 24 steps
Scope patch reducer    = 1000 examples, 30 steps
Discovery lifecycle    = 200 examples, 30 steps
P18 relationship owner = 200 examples, 12 steps
Completion owner       = 200 examples, 12 steps
~~~

Important invariants explored include:

- scope mutation;
- scope resume;
- report-only continuation;
- relationship interpretation;
- shared material;
- discovery;
- adaptive NextTest;
- completion;
- Evidence currentness;
- dedup.

Metamorphic variants cover at least:

- scope/currentness;
- ONE_PASS RCA;
- ADAPTIVE;
- relationship;
- reporting;
- multi-intent;
- alternate RCA family.

Changing requirement order must not silently change:

- owner;
- material count;
- terminal outcome.

Relevant tests:

- `backend/tests/test_v3_brain_v2_material_stateful.py`
- `backend/tests/test_v3_research_scope_patch_stateful.py`
- `backend/tests/test_v3_brain_v2_discovery_stateful.py`
- `backend/tests/test_v3_p18_relationship_stateful.py`
- `backend/tests/test_v3_brain_v2_completion_stateful.py`
- `backend/tests/test_v3_v1_phase1_metamorphic.py`
- `backend/tests/test_v3_v1_capability_metamorphic.py`

---

## 27. Permanent runtime guardrails

CI must RED if any of these reappear:

~~~text
final probe uses legacy composer
Agent API is enabled
Agent API call count > 0
normal Discovery invokes P17 provider
normal observational Relationship invokes P17 provider
report-only opens native acquisition
duplicate material executes
stale Evidence is treated as current
hidden USER_MUST exists
Product code contains benchmark/case-specific IDs
Dima introduces SQL/MBQL planning
~~~

Key test:

- `backend/tests/test_v3_brain_v2_runtime_guardrails.py`

Key workflows:

- `.github/workflows/dima-brain-v2-provider-free.yml`
- `.github/workflows/dima-brain-v2-phase1-provider-free.yml`
- `.github/workflows/dima-brain-v2-phase2-headless.yml`
- `.github/workflows/dima-brain-v2-phase1-live.yml`

---

## 28. Final T1–T7 capability panel

| Capability | Fresh run | Mechanical | Manual | Core product proof |
|---|---:|---|---:|---|
| T1 Scope/Resume | 37002719189 | GREEN | 4/4 | scope mutation, historical/current Evidence, resume |
| T2 ONE_PASS | 37003097196 | GREEN | 4/4 | bounded RCA without redundant re-entry |
| T3 ADAPTIVE | 37003440451 | GREEN | 4/4 | exactly one typed high-information NextTest |
| T4 DISCOVERY | 37003830042 | GREEN | 3/4 | deterministic governed candidates, P17 discovery=0 |
| T5 Relationship | 37017824173 | GREEN | 4/4 | P18-owned cross-sectional relationship, P17=0 |
| T6 Contextual Report | 37017824173 | GREEN | 4/4 | report-only analytical delta=0 |
| T7 Multi-intent | 37019171940 | GREEN | 3/4 | shared MaterialGroup, distinct owners, all MUST terminal |

Manual average:

~~~text
26 / 7 = 3.71 / 4
~~~

FULL 4/4 capabilities:

~~~text
5 / 7
T1 T2 T3 T5 T6
~~~

Final provider-free seals:

~~~text
Phase-1 provider-free: 37020220583 GREEN
Phase-2/headless + metamorphic: 37020220833 GREEN
~~~

Final zero-violation receipt:

~~~text
exception = 0
silent wrong = 0
security violation = 0
cross-tenant violation = 0
unsupported causal promotion = 0
duplicate native = 0
stale Evidence = 0
hidden MUST = 0
Agent API calls = 0
legacy final calls = 0
normal Discovery P17 = 0
normal Relationship P17 = 0
unresolved architecture family = 0
~~~

---

## 29. Product capability foundation

The backend now provides the stable primitives required for the first serious Dima UX.

### 29.1 Ask / governed analytical answer

Backend foundation:

- typed intent;
- ScopeVersion;
- MaterialGroup;
- Metabot acquisition;
- Evidence provenance;
- direct terminal answer.

UX implication:

A future Ask surface can show an answer without pretending the UI itself is the analytical authority.

### 29.2 Investigation / RCA

Backend foundation:

- governed candidate identity;
- CandidateSetProjector;
- P19 epistemics;
- P17 typed NextTest;
- bounded adaptive re-entry;
- Evidence currentness;
- checkpoint/resume.

UX implication:

An Investigation surface can show hypotheses, Evidence, limitations and next-test progression from real durable state rather than a chat transcript.

### 29.3 Relationship analysis

Backend foundation:

- explicit observational intent;
- cross-sectional vs temporal material semantics;
- P18 bounded interpretation;
- support/challenge Evidence refs;
- immutable RelationshipResult;
- business-policy separation.

UX implication:

A future relationship view can distinguish “association”, “co-movement”, “policy relation” and “causality” rather than collapsing them into one vague insight.

### 29.4 Evidence / provenance

Backend foundation:

- receipt;
- result hash;
- ScopeVersion;
- material fingerprint;
- tenant/principal;
- current/historical state;
- exact Evidence-cell refs.

UX implication:

An Evidence Drawer can be a projection of governed provenance rather than reconstructed UI metadata.

### 29.5 Contextual report

Backend foundation:

- terminal completion ledger;
- P20 synthesis;
- exact numeric provenance;
- limitations;
- presentation revision independent from research/scope;
- analytical delta zero.

UX implication:

A Report surface can regenerate or reformulate presentation without secretly rerunning analytics.

### 29.6 Multi-intent management query

Backend foundation:

- multiple USER_MUST requirements;
- shared MaterialGroup;
- explicit consumers;
- typed owner dispatch;
- per-requirement terminal outcomes;
- P20 after completion.

UX implication:

A single future user request can safely produce ranking + relationship + report without losing an intent or duplicating analytics.

### 29.7 Resume / durable interaction

Backend foundation:

- LangGraph checkpoint;
- activity fingerprints;
- state revisions;
- currentness;
- idempotency.

UX implication:

The future product can support durable investigations rather than stateless one-shot chat turns.

---

## 30. What “UX ready” means — and does not mean

The backend is **contract-ready** for a UX layer.
It does not mean frontend is already implemented.

Ready means:

- stable owner boundaries exist;
- UI-visible entities have durable IDs/refs;
- scope/currentness semantics are explicit;
- Evidence/provenance can be projected;
- investigations can resume;
- reports are separated from analytics;
- multi-intent completion is explicit;
- user-facing surfaces do not need to invent business truth.

Not yet implemented:

~~~text
frontend
web UI
Ask screen
Investigation screen
Evidence Drawer
Report/Decision UI
dashboard integration
demo frontend
visual Product layer
~~~

Future UX must consume these backend contracts.
It must not create alternate truth in client state.

---

## 31. Recommended future UX-to-backend mapping

This is an architectural mapping, not implemented UI.

| Future UX surface | Canonical backend authority |
|---|---|
| Ask | Requirement + ScopeVersion + terminal Evidence/outcome |
| Investigation | P19 case + P17 NextTest lineage + Evidence |
| Candidate list | CandidateSetProjector/P19 refs |
| Relationship view | RelationshipResult + Evidence refs |
| Evidence Drawer | Evidence + receipt/result-hash/currentness |
| Scope controls | typed scope patch reducer |
| Report | P20 ReportDocument + PresentationRevision |
| Resume/history | LangGraph checkpoint + Research/Scope revisions |
| Multi-intent status | Completion Ledger per USER_MUST |

Frontend must render these objects.
Frontend must not replace them.

---

## 32. Remaining known limitations

Architecture is frozen, but Product quality is not identical across every capability.

Known manual-quality distinction:

- T4 = 3/4: safe and useful Discovery, but candidate differentiation is not FULL.
- T7 = 3/4: mechanically correct multi-intent management synthesis, but ranking narrative is less explicit than FULL.

These are not permission to reopen architecture.

A future improvement must first prove which accepted owner is weak:

- T4 weak differentiation -> inspect P19 interpretation family;
- T7 weak management synthesis -> inspect P20/user-facing projection family.

Do not reopen CandidateSetProjector or MaterialGroup unless a generic mechanical reproducer proves those owners are wrong.

---

## 33. Readiness status

Final decision:

~~~text
BRAIN V2.1 ARCHITECTURE FROZEN

90+ HIGH-CONFIDENCE READINESS
YES

30-CASE READY
YES

90+ PROVEN
NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
~~~

Meaning:

- the architecture, targeted live panel, manual quality and stateful/metamorphic evidence justify proceeding to the frozen 30-case when separately authorized;
- no claim is made that the Product has already scored >=90 on that benchmark;
- 90+ PROVEN requires the separately authorized frozen 30-case to actually run and score >=90.0.

---

## 34. The final mental model

When changing Dima, ask in this order:

~~~text
1. What is the USER_MUST requirement?
2. What ScopeVersion is authoritative?
3. What minimum analytical MaterialGroup is required?
4. Does Metabot already own the analytical computation?
5. Is the result VERIFIED current Evidence?
6. Which typed owner receives this requirement?
7. Has that owner produced a terminal governed artifact?
8. Has Completion accounted for every USER_MUST?
9. Only then: does P20 need to synthesize presentation?
10. Can checkpoint/resume repeat anything? It must not.
~~~

If a proposed change cannot be located cleanly in this sequence, stop before coding.
The likely problem is an authority violation.

---

# FINAL ARCHITECTURE LAW

~~~text
ONE ANALYTICS ENGINE:
METABOT.

ONE FORWARD ORCHESTRATOR:
LANGGRAPH.

ONE PRODUCT SEMANTIC AUTHORITY:
DIMA.

DISCOVERY
DOES NOT NEED A SECOND ANALYST.

RELATIONSHIP
DOES NOT BELONG TO P17.

P18 OWNS RELATIONSHIP JUDGMENT.

P19 OWNS RCA JUDGMENT.

P17 EXISTS ONLY WHEN NEW INFORMATION
IS ACTUALLY NEEDED.

P20 WRITES FROM TERMINAL GOVERNED STATE.

A REPORT DOES NOT REOPEN ANALYTICS.

MULTIPLE REQUIREMENTS MAY SHARE MATERIAL.

SHARED MATERIAL DOES NOT MEAN
SHARED FULFILLMENT.

MECHANICAL GREEN IS NOT PRODUCT QUALITY.

NO SECOND TRUTH.
NO SECOND ANALYST.
NO SECOND ANALYTICS ENGINE.
NO BRAIN V3.
~~~
