# DIMA BRAIN V2.1 — ENGINEERING PLAYBOOK

> **Status:** CURRENT / MANDATORY DEVELOPMENT METHOD  
> **Branch family:** Brain V2.1 forward runtime  
> **Current recovery branch:** `feat/dima-brain-v2-1-specification-closure`  
> **Active semantic candidate:** `eee7583cb67d50779784805c469230ef2b82a5a2` — Fix A/B provider-free GREEN, not final-frozen  
> **Certified engine:** `686671fa7e55f715e4fb5ac155f9e66019fd12d8` / `0.63.18-dima.11.2`  
> **Read first:** `DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md`; for execution status read `DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md`

This playbook explains **how Dima must be developed** after Brain V2.1 closure.
It is deliberately stricter than an ordinary coding guide. Most expensive historical
failures came from changing the correct code in the wrong authority layer, treating one
paid RED as a prompt-tuning exercise, or allowing a second truth to grow beside the
canonical owner.

The permanent objective is not “make the test green.” It is:

~~~text
preserve one owner per truth
preserve one forward runtime
make the first wrong boundary observable
prove generic invariants provider-free
use paid live only for information that deterministic tests cannot provide
~~~

---

## 1. Start every change by naming the authority

Before editing code, answer:

~~~text
What USER_MUST changed?
What ScopeVersion is current?
What MaterialGroup is required?
What owner owns the missing terminal artifact?
What is the first invalid boundary?
What existing store is canonical truth?
~~~

If these cannot be answered, do not patch.

Permanent owner map:

| Concern | Owner |
|---|---|
| accepted requirement | Dima Research / Requirement contracts |
| scope/currentness | ScopeVersion + canonical reducer |
| canonical business WHAT/currentness | ResearchBrief / ResearchScope |
| execution-facing WHAT projection | AnalyticalIntentV1 (projection, not second truth) |
| minimum acquisition grouping | MaterialGroup execution projection |
| analytical cognition/execution | Metabase / Metabot |
| execution observation | ExecutionManifest |
| Intent <-> execution admission | `verify_analytical_fulfillment_v1` only |
| Evidence identity/currentness/provenance | Dima Evidence layer |
| candidate identity | CandidateSetProjector |
| relationship epistemics | P18 |
| RCA epistemics | P19 |
| exact information-gain re-entry | P17 NextTest controller |
| USER_MUST terminal accounting | Completion Ledger |
| governed presentation | P20 |
| routing/checkpoint/resume | LangGraph |
| observability | BoundaryTrace + OpenTelemetry bridge |

Do not fix an owner-A defect in owner B because B is easier to edit.

---

## 1A. Semantic-owner admission gate

Before adding any validator, contract, store or runtime gate, answer:

~~~text
Which canonical semantic fact do I own?
Does that fact already have an owner?
~~~

If the fact already has an owner, **do not add a new semantic validator**.
Project the existing authority into the consumer boundary instead.

Allowed downstream responsibilities:

- projection;
- transport;
- structural provenance/identity checks;
- one canonical fulfillment check;
- Evidence consumption;
- ledger accounting.

Forbidden downstream responsibilities:

- reinterpreting accepted metric/entity/time/ranking meaning;
- inferring business meaning from physical query shape;
- turning a representation mismatch into a new semantic owner;
- creating a second currentness/scope truth;
- using closed grammar as a runtime capability whitelist.

Canonical analytical chain:

~~~text
ResearchScope / ResearchBrief
-> AnalyticalIntentV1
-> Metabase / Metabot
-> ExecutionManifest
-> verify_analytical_fulfillment_v1
-> Evidence
~~~

If a proposed change creates another semantic judge between these nodes, redesign it.

---

## 2. One forward runtime

Forward Product execution is:

~~~text
BrainV2Service
-> LangGraph
-> typed activities
-> canonical owners/stores
~~~

`HeadlessProductComposer` is historical reference/fallback. It is not a strategic
extension point and must never reappear in final certification.

Permanent final runtime invariants:

~~~text
legacy final calls = 0
Agent API calls = 0
MB_AGENT_API_ENABLED = false
~~~

Do not create Brain V3 to avoid a local invariant defect.

---

## 3. Analytics boundary

Metabase / Metabot is the single analytical cognition engine.

Dima may:

- constrain legal semantics;
- compile a bounded material requirement;
- ask Metabot for analytical material;
- verify the native occurrence;
- admit Evidence;
- judge what the Evidence is allowed to mean.

Dima may not:

- become an SQL/MBQL planner;
- create a second analytics engine;
- compute hidden correlations/statistics inside P18/P19/P20;
- infer query shape from benchmark wording;
- restore Wren execution;
- use Agent API.

If more analytical information is genuinely required, create typed authority for the need,
then obtain new material through Metabot.

---

## 4. Requirement != query

A USER_MUST requirement is business authority. It is not one native query.

The canonical sequence is:

~~~text
USER_MUST
-> typed requirement owner
-> MaterialGroup(s)
-> native material
-> VERIFIED Evidence
-> owner terminal artifact
-> Completion Ledger
-> P20 only if presentation is required
~~~

Multiple requirements may consume one MaterialGroup.
One MaterialGroup may drive one native acquisition for multiple compatible consumers,
but each consumer must pass its own fulfillment verifier before the single governed
Evidence package is admitted for that consumer.

This distinction is essential for multi-intent requests.

---

## 5. MaterialGroup rules

MaterialGroup is execution projection, not semantic truth.

Allowed:

- exact governed metric/dimension/time/filter needs;
- exact consumer requirement refs;
- deterministic material fingerprint;
- deduplication when typed compatibility is proven.

Forbidden:

- fuzzy clause similarity;
- keyword/regex/morphology matching;
- embedding similarity;
- benchmark-specific material splitting/merging;
- treating presentation requirements as analytical material.

Invariant:

~~~text
same legal semantic material + same relevant revisions
-> duplicate native execution = 0
~~~

A report request contributes **zero analytical material** unless it also introduces an
explicit new analytical requirement.

---

## 6. Scope mutation rules

Scope mutation is a typed partial update.

Permanent semantics:

~~~text
omitted facet          -> inherit
explicit CLEAR         -> clear
explicit replacement   -> replace
no-op patch            -> no semantic change
same patch twice       -> idempotent
~~~

Never reconstruct the whole scope from free text on a follow-up.

ResearchRevision, ScopeVersion and PresentationRevision are separate concepts.

Presentation-only continuation:

~~~text
Research delta = 0
Scope delta = 0
native acquisition delta = 0
P17 delta = 0
P18 delta = 0
P19 delta = 0
P20 may change presentation
~~~

---

## 7. Evidence is a provenance firewall

Evidence is valid only when bound to the current:

- tenant;
- principal;
- research session;
- ScopeVersion;
- material fingerprint;
- native receipt;
- result hash;
- execution time/currentness.

A scope change makes prior Evidence historical.

Historical Evidence may be shown explicitly as history. It may not silently support current
P18/P19/P20 judgment.

Never copy raw provider/model output into Evidence authority.

---

## 8. Discovery law

Normal discovery:

~~~text
Metabot
-> VERIFIED Evidence
-> CandidateSetProjector
-> P19
~~~

Normal discovery P17 provider calls:

~~~text
0
~~~

CandidateSetProjector produces identity/provenance only.

It may not produce:

- support scores;
- challenge scores;
- probability;
- likelihood;
- causal ranking;
- dominant cause;
- causal conclusion.

Cardinality:

~~~text
0 -> honest governed terminal
1 -> keep one real candidate; never invent a competitor
2+ -> preserve every legal materially relevant candidate
~~~

---

## 9. P19 law

P19 owns RCA epistemics.

P19 may:

- evaluate support/challenge;
- preserve uncertainty;
- decide whether current material is sufficient/inconclusive;
- issue one typed NextTestRequest when more information is genuinely useful.

P19 may not execute analytics directly.

Observational association never becomes causality merely because P19 is confident.

---

## 10. P17 law

P17 is not a second analyst.

Normal use:

~~~text
P19
-> typed NextTestRequest
-> P17 controls bounded re-entry
-> Metabot
-> new VERIFIED Evidence
-> P19 revision
~~~

Keep adaptive depth bounded.

Forbidden P17 uses:

- normal discovery;
- normal relationship cognition;
- rereading the same governed packet “for insight”;
- retry-until-lucky;
- broad free-form analytical search outside a typed need.

---

## 11. P18 law

Normal observational relationship:

~~~text
Metabot
-> VERIFIED Evidence
-> bounded P18 interpretation
-> immutable RelationshipResult
-> Completion / P20
~~~

Normal relationship P17 provider calls:

~~~text
0
~~~

P18 may classify only the exact current Evidence identity set.

P18 may not:

- run Metabot;
- execute a query;
- mutate scope;
- invent metrics or dimensions;
- create RCA hypotheses;
- promote causality;
- infer temporal co-movement from cross-sectional material;
- require BUSINESS_POLICY for an OBSERVATIONAL-only request.

Exact observed magnitudes used in presentation must resolve back to legal current
Evidence-cell refs and receipts. Arbitrary model-generated row/column coordinates are forbidden.

---

## 12. Business policy is separate

Observed analytical relationship, business-policy relationship and causal relationship are
different authorities.

Never collapse:

~~~text
association
!= co-movement
!= business policy
!= causality
~~~

A relationship result must state its epistemic ceiling.

---

## 13. Completion Ledger law

Process completion is not requirement fulfillment.

Every USER_MUST must end explicitly as terminal.

Typical terminal accounting may include fulfilled, limited, inconclusive or blocked outcomes,
depending on the canonical contract.

P20 cannot decide that upstream analytics are complete.

The graph order is conceptually:

~~~text
terminal analytical owner
-> Completion Ledger
-> P20 if presentation is required
-> Completion Ledger final presentation accounting
~~~

Hidden MUST = 0 is a permanent gate.

---

## 14. P20 law

P20 is governed synthesis, not an analyst.

P20 consumes terminal governed artifacts and exact provenance.

It may:

- render findings;
- include exact observed magnitudes;
- include Evidence/provenance;
- state limitations;
- provide conservative management-use implications.

It may not:

- reopen analytics;
- create new Evidence;
- compute hidden statistics;
- strengthen an upstream epistemic claim;
- silently remove a USER_MUST;
- mutate ScopeVersion.

Manager quality must improve through better governed projection, not by adding a second LLM
analysis pass.

---

## 15. Checkpoint / resume / idempotency

LangGraph state carries refs and revisions, not duplicated owner truth.

A completed paid/native activity must not replay after resume.

Use deterministic activity fingerprints.

Always test:

- checkpoint restart;
- scope mutation then resume;
- NextTest then resume;
- presentation-only continuation;
- same mutation twice;
- completed material activity replay protection.

---

## 16. First-wrong-boundary debugging

Every RED must be reduced to:

~~~text
last_valid_boundary
first_invalid_boundary
owner
error.type
expected identity/state
observed identity/state
~~~

If debugging still requires manually reading thousands of log lines, telemetry is incomplete.

Required conceptual spans/events include:

- intent interpret;
- scope resolve;
- requirement plan;
- material compile/execute;
- Evidence admit;
- candidate projection;
- P18 adjudicate;
- P19 assess;
- P17 NextTest;
- completion evaluate;
- P20 report.

Never export raw prompts, hidden model reasoning, secrets or full Evidence payloads.

---

## 17. The RED loop

Never do:

~~~text
paid RED
-> patch exact case
-> paid RED
-> patch exact case
~~~

Always do:

~~~text
RED
-> locate first invalid boundary
-> identify owner
-> state generic invariant
-> write exact provider-free reproducer
-> add metamorphic/stateful siblings
-> make one generic root correction
-> run focused affected PF
-> run wider affected PF
-> freeze new semantic SHA
-> run one fresh surgical live proof
~~~

No same-SHA retry for “luck.”

---

## 18. Forbidden fix classes

Do not use:

- fuzzy string matching;
- regex/morphology semantic routing;
- prompt keyword patches;
- benchmark phrase patches;
- hardcoded case IDs;
- arbitrary provider ceiling increases;
- retry count increases as correctness fixes;
- synthetic/fake candidate padding;
- fake provenance IDs;
- raw SQL/MBQL rewriting in Dima;
- hidden fallback to legacy composer;
- a second semantic store beside the canonical owner;
- broad refactor while fixing one invariant.

A case-specific fix is acceptable only when the case reveals a genuinely generic typed invariant
that is then tested through siblings.

---

## 19. Pattern-research protocol

When a new architecture/reliability problem appears, research the exact pattern before coding.

Authority order:

~~~text
1. standards
   - IETF RFCs
   - Google AIPs / FieldMask semantics

2. official technology docs/source
   - Metabase / Metabot
   - LangGraph

3. directly analogous architecture
   - Wren AI / OSS

4. reliability/testing references
   - Temporal patterns
   - OpenTelemetry
   - Hypothesis
   - Schemathesis when API contract is frozen

5. pattern-only agent systems
   - OpenHands
   - Letta
~~~

Do not add a new runtime merely because its documentation contains a useful pattern.

Wren is an architecture oracle, not an execution dependency.

---

## 20. Provider-free before paid

A deterministic RED must never reach paid live.

Before a live proof, the exact semantic candidate must have GREEN affected gates including:

- owner/unit contract tests;
- graph routing;
- security/currentness;
- resume/idempotency;
- stateful sequences;
- metamorphic siblings;
- forbidden-surface guards;
- relevant P14/P18/P19/P20 regression;
- final mechanical receipt logic.

Broad paid batches are forbidden during diagnosis.

Live is for information that provider-free proof cannot supply.

---

## 21. Stateful floors

Final V2.1 closure established these floors:

~~~text
Material/state reducer      = 1000 examples, 24 steps
Scope patch reducer         = 1000 examples, 30 steps
Discovery lifecycle         = 200 examples, 30 steps
P18 relationship owner      = 200 examples, 12 steps
Completion owner            = 200 examples, 12 steps
~~~

Do not reduce floors to make CI pass.

When adding a new mutation/owner family, add it to the relevant state machine before relying on live.

---

## 22. Metamorphic testing

At least two executable variants are required for major semantic families where wording/order
should not change governed behavior.

Current required families include:

- scope/currentness;
- ONE_PASS RCA;
- ADAPTIVE;
- relationship;
- reporting;
- multi-intent;
- alternate RCA family.

A wording change must not create a new semantic owner or duplicate analytics.

---

## 23. Security rules

Security is Product correctness.

Always preserve:

- tenant isolation;
- principal isolation;
- exact ScopeVersion;
- current Evidence only;
- fail-closed native identity;
- no cross-tenant receipt reuse;
- no cross-scope candidate/hypothesis reuse.

Security violation = 0 is a final acceptance gate.

---

## 24. Engine policy

V2.1 engine is frozen:

~~~text
SHA
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88

release
0.63.18-dima.9

digest
sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7

V2.1 engine builds
0
~~~

Do not rebuild or create a new engine release for a Product-owned defect.

If a correction truly requires engine source change, stop and escalate rather than silently
expanding scope.

---

## 25. Small-commit discipline

Use small coherent commits.

Preferred sequence:

~~~text
test: exact reproducer
fix: generic owner correction
test: metamorphic/stateful siblings
ci: affected closure marker
cert: one fresh live proof
docs: seal receipt/handoff
~~~

Before each write:

1. re-read branch HEAD;
2. verify your parent SHA is still current;
3. do not overwrite concurrent progress;
4. never force-push shared work.

Do not hold an entire architecture change in one large uncommitted patch.

---

## 26. Stale-HEAD rule

This repository can advance while another developer is working.

If HEAD moved:

- stop writing;
- inspect intervening commits;
- classify whether your work is already landed, superseded or still needed;
- rebase conceptually onto the new authority;
- never replay stale patches blindly.

Duplicate implementations are architecture defects.

---

## 27. Stop conditions

Escalate instead of improvising when:

- engine modification appears necessary;
- Metabot capability itself is insufficient for a required legal analytical surface;
- a new analytics/query engine appears necessary;
- Dima semantic/Evidence/epistemic authority would need weakening;
- LangGraph would need to become business truth;
- the same capability remains structurally RED after two coherent generic candidates.

Ordinary test failure is not a STOP condition.

---

## 28. UX transition law

The backend is contract-ready for UX, not frontend-complete.

Future UI may project:

- Requirement;
- ScopeVersion;
- Material/processing status;
- Evidence and provenance;
- Candidate/P19 state;
- RelationshipResult;
- Completion Ledger;
- ReportDocument;
- checkpoint/history.

Frontend must not create alternate truth in client state.

Examples:

~~~text
Ask screen          -> current requirement + scope + terminal outcome
Investigation       -> P19/P17 lineage + Evidence
Relationship view   -> RelationshipResult + Evidence
Evidence Drawer     -> Evidence + receipt/result hash/currentness
Report              -> P20 ReportDocument + PresentationRevision
History/resume      -> checkpoint + Research/Scope revisions
Multi-intent status -> Completion Ledger per USER_MUST
~~~

No frontend work is authorized by backend readiness alone.

---

## 29. Adding a new Product capability

Before adding code:

1. express the new USER_MUST;
2. decide whether an existing requirement kind already represents it;
3. identify the canonical owner;
4. define the minimum MaterialGroup need;
5. prove whether existing Evidence can legally satisfy it;
6. define terminal artifact/currentness semantics;
7. add Completion mapping;
8. define P20 projection if presentation is required;
9. add PF + stateful/metamorphic tests;
10. add live only if fresh provider behavior is material to correctness.

If step 3 creates “another analyst,” redesign before coding.

---

## 30. Code-review checklist

A reviewer should reject a change if any answer is unclear:

- Which owner is changed?
- What generic invariant was wrong?
- Where is the provider-free reproducer?
- What sibling/metamorphic case prevents benchmark overfit?
- Can this duplicate native work?
- Can it admit stale/cross-scope Evidence?
- Can it create a hidden MUST?
- Can it reopen analytics from presentation?
- Can it promote association to causality?
- Can it reintroduce P17 normal discovery/relationship cognition?
- Can it reintroduce Agent API or legacy composer?
- Does resume replay completed paid/native work?
- Is a new store duplicating existing truth?
- Does this add a second semantic veto for a fact that already has an owner?
- Could a closed grammar/composition table reject a typed intent at runtime?
- Is a structural attestation/observer trying to infer business meaning from query shape?
- Is `verify_analytical_fulfillment_v1` still the sole Intent <-> Execution semantic judge?
- Is the change observable at the first wrong boundary?

---

## 31. Documentation governance

Current docs are only:

- `README.md`;
- `DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md`;
- `DIMA_BRAIN_V2_1_SEMANTIC_AUTHORITY_CONSTITUTION.md`;
- `DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md`;
- `DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md`;
- `DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md`.

Everything under `legacy/` is historical.

Do not create a second “current handoff,” “final architecture,” or active roadmap.

When status changes, update the existing handoff.
When a permanent law changes, update the existing architecture/laws with executable proof.
When a document is superseded, move it to `legacy/` in the same commit.

---

## 32. New developer first-hour checklist

Do this before touching Product code:

~~~text
[ ] read metabase/README.md
[ ] read FINAL_ARCHITECTURE
[ ] read ENGINEERING_PLAYBOOK
[ ] read CURRENT_HANDOFF
[ ] read FORWARD_RUNTIME_LAWS
[ ] verify current branch HEAD
[ ] verify final semantic Product SHA/status
[ ] identify exact owner for the requested work
[ ] inspect existing owner tests/state machines
[ ] inspect first-wrong-boundary telemetry
[ ] research the relevant official/standard pattern
[ ] write provider-free reproducer before patching
~~~

Do not begin with old roadmap/recovery documents.

---

## 33. Current acceptance bar

Current closure:

~~~text
manual average = 3.71 / 4
FULL 4/4 capabilities = 5 / 7

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

Known quality ceilings are documented, not hidden:

- T4 Discovery = 3/4;
- T7 Multi-intent = 3/4.

Improve them only inside the accepted owner family after a generic reproducer.
Do not reopen the architecture merely because a capability is not yet 4/4.

---

# Engineering law

~~~text
FIND THE OWNER.
FIND THE FIRST WRONG BOUNDARY.
PROVE THE INVARIANT PROVIDER-FREE.
FIX THE ROOT GENERICALLY.
TEST THE SEQUENCE SPACE.
RUN ONE SURGICAL LIVE.
SEAL THE RECEIPT.
DO NOT CREATE A SECOND TRUTH.
~~~
