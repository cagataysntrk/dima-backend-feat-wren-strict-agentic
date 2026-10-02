# DIMA V1 — PHASE-1 GAP MAP

Status: CANONICAL PRE-IMPLEMENTATION GAP MAP  
Date: 2026-09-27  
Branch baseline: `feat/dima-metabase-platform@7a3b956a06b5f8850534124776e1006d5a016fd9`  
Roadmap authority: `23256335e57213f5a09dfc6daba29313afff5e6a`  
Roadmap blob: `a1586f69ad8ccd24e78b0a74beacc46d564b0054`

This document is the mandatory code-grounded Phase-1 gap map. It does not reopen the
Metabase/Metabot engine decision and it does not authorize UI work.

Classification vocabulary is exact:

- `ALREADY_PROVEN`
- `PARTIAL_MUST_EXTEND`
- `MISSING`
- `CONTRACT_MISMATCH`
- `DEFERRED_BY_ROADMAP`

## 1. Executive classification

| ID | Phase-1 requirement | Classification | Owning change |
|---|---|---|---|
| P1 | P17 provider-contract reliability | CONTRACT_MISMATCH | P17 provider adapter |
| P2 | ScopeVersion + TurnScopeContract + ScopeMutation | MISSING | Research entry/scope contract |
| P3 | AnalyticalRequestContract / anti-second-planner boundary | CONTRACT_MISMATCH | analytical request boundary |
| P4 | USER_MUST requirement/completion ledger | PARTIAL_MUST_EXTEND | Product completion contract |
| P5 | Adaptive P17 investigation | PARTIAL_MUST_EXTEND | P17 budget/trace legality |
| P6 | single P17→P19 eligibility predicate | CONTRACT_MISMATCH | Product process manager |
| P7 | multi-factor P19 RCA | PARTIAL_MUST_EXTEND | P19 epistemic contract |
| P8 | P19→P17 discriminating-test recursion | MISSING | Product/P17/P19 bridge |
| P9 | P18 relationship closure | PARTIAL_MUST_EXTEND | P18 + composition proof |
| P10 | Evidence-backed P20 reporting | ALREADY_PROVEN | retain; add scope regression |
| P11 | FAST / GUIDED / INVESTIGATION modes | PARTIAL_MUST_EXTEND | Product execution-mode router |
| P12a | Round-2 30-prompt Phase-1 benchmark | PARTIAL_MUST_EXTEND | V1 eval harness |
| P12b | new metamorphic validation corpus | MISSING | V1 eval harness |
| P13 | immutable Phase-1 candidate + receipt | MISSING | phase governance after GREEN |
| X1 | UI/frontend | DEFERRED_BY_ROADMAP | none |
| X2 | connectors / Company Map / sector productization | DEFERRED_BY_ROADMAP | none |
| X3 | external side-effect execution / Resend / Slack | DEFERRED_BY_ROADMAP | none |
| X4 | new specialized finance/manufacturing engines | DEFERRED_BY_ROADMAP | none |

The table is intentionally conservative. Existing class/module names do not count as proof;
the details below identify actual semantics, tests and gaps.

---

## 2. P1 — P17 provider-contract reliability

### Roadmap requirement
The LLM proposes semantic cognition only. Deterministic Dima state owns system identities.
Provider values that are known from state are closed-world. Invalid provider output may receive
at most one bounded repair; a second invalid output becomes governed `INCONCLUSIVE`, not a 500,
retry loop or silent fallback.

### Current implementation paths
- `backend/app/v3/research_manager_provider.py`
- `backend/app/v3/structured_transport.py`
- `backend/app/v3/research_manager.py`

### Current owner
P17 provider adapter + P17 domain validator.

### Current durable objects
- `ResearchReasoningStepRecord`
- `ResearchInvestigationTaskRecord`
- durable P17 proposal JSON / step/task identities

### Current tests
- `backend/tests/test_v3_p17_autonomous_provider_schema.py`
- `backend/tests/test_v3_p17_authorization_transport.py`
- `backend/tests/test_v3_p17_autonomous_manager_eval.py`
- `backend/tests/test_v3_p17_research_manager.py`

### Current evidence / historical seal
P17 provider schema and GLOBAL_CONTROL legality are sealed by DMP-DEC-0061 and the
comparison-ready provider-free closure.

### Classification
`CONTRACT_MISMATCH`.

### Why
The existing provider schema is strongly closed-world, but the model still emits bookkeeping /
machine-authority fields including:

- `proposal_id`
- `source_revision`
- `target_parent_obligation`
- `parent_step_id`
- `branch_key`
- `objective_key`

State narrows many of them to legal enums, which is good historical correctness, but V1 requires
Dima to bind these identities deterministically rather than asking the model to reproduce them.
The current path also performs one provider call and lets malformed structured output propagate;
there is no generic max-one-repair → governed-INCONCLUSIVE contract.

### Required owner
P17 provider adapter. P17 domain legality remains final and must not be moved into Product.

### Minimal contract delta
1. introduce semantic-only provider proposal DTO;
2. derive machine IDs/revision/parent/branch/task identities from current action profile + state;
3. preserve state-derived closed legal choices for semantic refs;
4. add one generic bounded repair;
5. deterministically produce an INCONCLUSIVE terminal proposal after the repair budget is exhausted.

### Sealed invariants that must survive
- P17 chooses WHAT; Metabase chooses HOW;
- provider cannot broaden `InvestigationActionProfile`;
- no model-minted Evidence/claim/semantic authority IDs;
- no prompt-specific repair;
- no fallback model/cascade;
- branch terminality / GLOBAL_CONTROL invariant remains intact;
- restart-safe durable step/task identities.

### Focused proof
A provider-free suite proving:
- provider schema contains no system identity output fields;
- state deterministically binds all machine IDs;
- illegal semantic choice is rejected;
- first malformed response may repair once;
- second malformed response yields governed INCONCLUSIVE;
- exactly 0/1/2 model calls according to valid/repair/exhausted path.

### Affected regression
Full P17 provider/schema/manager suites + Core-B composition/process tests.

### Duplicate-authority risk
High if Product or prompt logic starts owning parent/branch legality. Keep legality in P17.

---

## 3. P2 — ScopeVersion + TurnScopeContract + ScopeMutation

### Roadmap requirement
First-class governed scope identity and typed scope mutation. Old-scope Evidence remains
historically valid but cannot silently become current Evidence after mutation.

### Current implementation paths
- `backend/app/v3/research_contracts.py`
- `backend/app/v3/research_intake.py`
- `backend/app/v3/research.py`
- `backend/app/v3/research_store.py`
- P16/P17/P19/P20/P21 objects bind to Research session / context

### Current owner
No first-class conversational scope owner exists.

### Current durable objects
- durable `ResearchBrief` persisted with the Research session;
- `ResearchScope.semantic_refs` and `time_surfaces`;
- session `context_version`;
- downstream objects bind session/obligation/context.

### Current tests
- P14 persistence/resume suites;
- `test_v3_owner_scoped_must_accounting.py`;
- P16/P19/P20/P21 scope/security tests.

### Current evidence / historical seal
Durable resume and tenant non-oracle behavior are sealed, but they prove session/context
ownership rather than explicit turn-scope mutation semantics.

### Classification
`MISSING`.

### Missing behavior
There is no:
- `ScopeVersion`;
- `TurnScopeContract`;
- `ScopeMutation`;
- typed ADD/REMOVE/REPLACE/NARROW_ENTITY/EXPAND_ENTITY/CHANGE_PERIOD/
  CHANGE_METRIC/CHANGE_BREAKDOWN/RESET transition authority.

### Required owner
Research entry contract / scope authority, persisted through the accepted `ResearchBrief`.
No second semantic analytics owner.

### Minimal contract delta
- add immutable first-class scope contract models;
- add deterministic mutation application;
- bind accepted brief to one current `scope_version`;
- preserve parent scope lineage;
- expose downstream scope identity by durable Research authority/session reference rather than
  duplicating mutable scope blobs into every owner where an equivalent sealed reference suffices.

### Sealed invariants that must survive
- accepted brief is immutable durable user contract;
- raw prompt is not reparsed on resume;
- tenant/principal authority remains explicit;
- old Evidence cannot be rebound to another Research authority;
- no silent source/currentness upgrade.

### Focused proof
All Departments → Assembly mutation creates a new scope version; old Evidence stays historical
and cannot satisfy the new scope. Restart preserves both versions and current scope identity.

### Affected regression
Research intake/P14 persistence, P16 claim lineage, P17 snapshot, P19 scope checks, P20/P21
currentness, headless Product resume.

### Duplicate-authority risk
High if every downstream owner invents its own scope parser. One Research scope contract only.

---

## 4. P3 — AnalyticalRequestContract / anti-second-planner boundary

### Roadmap requirement
Dima carries only accepted material request invariants: metric, dimension, time, filters,
comparison intent, ranking basis, grain, requested output surfaces and scope version.
Metabase/Metabot owns query implementation. Dima must not judge SQL, MBQL, join plans,
aggregation implementation, temporal implementation or query optimality.

### Current implementation paths
- `backend/app/v3/analytics_contract.py`
- `backend/app/v3/native_execution.py`
- `backend/app/v3/native_standard/trust.py`
- `backend/app/v3/native_standard/contracts.py`

### Current owner
Standard analytical semantic boundary + native trust boundary.

### Current durable objects
- `StandardProjection`
- `ResolvedAnalyticsIntent`
- `AuthorizedExecutionArtifact`
- `DimaQueryReceipt`

### Current tests
- P13A/P13B/P13C/P13D native trust suites;
- analytical contract / semantic binding tests.

### Current evidence / historical seal
Current Dima correctly avoids parsing raw MBQL in Python and binds exact execution artifacts.
However P13D currently interprets engine-attested physical query facts to enforce exact
aggregation, temporal predicate, breakout/filter and ranking shapes.

### Classification
`CONTRACT_MISMATCH`.

### Why
`ResolvedAnalyticsIntent` already contains most requested semantic material, but V1 has no
explicit `AnalyticalRequestContract` with scope/output-surface identity. More importantly,
current forward Dima trust performs implementation-shape validation that the hardened V1 roadmap
now forbids for this boundary.

### Required owner
One V1 analytical request-invariant contract above Metabase. Existing engine attestation may
continue to prove execution identity/security facts, but must not become a second analytical
planner or implementation-quality judge.

### Minimal contract delta
- create explicit immutable `AnalyticalRequestContract`;
- derive it from accepted semantic authority;
- compare only request invariants against a semantic/native candidate observation;
- keep exact execution identity and security/provenance checks;
- remove forward V1 dependence on Dima-owned aggregation/temporal/join-plan implementation
  judgments;
- allow one native repair on material request mismatch, then typed limitation/failure.

### Sealed invariants that must survive
- exact authorized artifact identity;
- engine pin;
- principal/tenant/security checks;
- semantic handle authority;
- no SQL/raw-SQL fallback;
- Metabase remains sole analytical implementation owner.

### Focused proof
Architecture/static tests must fail if V1 request-invariant modules add SQL/MBQL parsing,
join-plan validation, aggregation-implementation validation, temporal-computation validation or
query optimality scoring. Behavioral tests cover metric/dimension/time/filter/ranking/grain/scope
preservation and bounded mismatch repair.

### Affected regression
P13 trust/security, P14 native execution, execution receipt/Evidence lineage.

### Duplicate-authority risk
Critical. This is the primary anti-second-query-planner gate.

---

## 5. P4 — USER_MUST requirement / completion ledger

### Roadmap requirement
Every accepted requirement must remain individually traceable and end in
FULFILLED/LIMITED/UNSUPPORTED/INCONCLUSIVE before trusted completion.

### Current implementation paths
- `backend/app/v3/research_contracts.py`
- `backend/app/v3/product/composition.py`
- `backend/app/v3/report_document.py`

### Current owner
Accepted `ResearchBrief.must_requirement_ids` + Product composition projection.

### Current durable objects
- immutable accepted `ResearchBrief`;
- P14 analytical obligations;
- P20 ReportDocument;
- Product requirement projection.

### Current tests
`backend/tests/test_v3_owner_scoped_must_accounting.py`.

### Current evidence / historical seal
Already proven:
- multiple analytical MUSTs remain separate;
- report deliverable remains in the immutable brief;
- P14 completion is analytical-only;
- P20 fulfills the report deliverable;
- restart before/after P20 preserves the original requirement contract;
- no governed publishable truth produces explicit limitation.

### Classification
`PARTIAL_MUST_EXTEND`.

### Missing / mismatched behavior
Current Product states are `VERIFIED / LIMITED / FULFILLED / PENDING`.
They do not provide the V1 final requirement vocabulary
`FULFILLED / LIMITED / UNSUPPORTED / INCONCLUSIVE`, and trusted final completion is not yet
expressed as a single explicit Completion Contract over every USER_MUST requirement.

### Required owner
Product completion contract. P14 remains owner only for analytical obligation lifecycle.

### Minimal contract delta
Preserve exact IDs and owner-scoped accounting; normalize final Product requirement disposition
without changing P14/P20 authority.

### Sealed invariants that must survive
No deliverable may become a P14 analytical obligation; no requirement may disappear on restart.

### Focused proof
Five-part request proves five durable requirements and no final trusted completion while any item
is unresolved; limitation/unsupported/inconclusive are explicit rather than dropped.

### Affected regression
Owner-scoped MUST accounting + Product composition + P20.

### Duplicate-authority risk
Medium if Product starts re-deriving the user contract instead of projecting the accepted brief.

---

## 6. P5 — Adaptive P17 investigation

### Roadmap requirement
Typed legal investigation actions, durable investigation trace, bounded adaptive branching.
P17 chooses WHAT; Metabase determines HOW.

### Current implementation paths
- `backend/app/v3/research_manager.py`
- `backend/app/v3/research_manager_provider.py`
- `backend/app/v3/product/composition.py`
- `backend/app/v3/product_routing_store.py`

### Current owner
P17.

### Current durable objects
Reasoning steps, tasks, branch graph, inspected Evidence/material/claims, stop state.

### Current tests / seal
P17 suites, Core-B adaptive routing, root recovery, comparison closure.

### Classification
`PARTIAL_MUST_EXTEND`.

### Already proven
- legal action profile exists;
- adaptive branches exist;
- counter-evidence is first class;
- STOP_BRANCH / STOP_INVESTIGATION are typed;
- durable step/task trace exists;
- Product can open typed adaptive investigation requirements.

### Missing / mismatch
- current `ResearchReasoningBudget.max_depth` defaults to and permits 5+; V1 hard maximum is 3;
- trace lacks first-class `scope_version`;
- V1 typed information-gain stop vocabulary is incomplete;
- provider identity mismatch from P1 must be corrected.

### Required owner
P17.

### Minimal contract delta
Hard max 3; scope-version binding; typed information-gain stop reasons; retain existing action
profile rather than creating a new manager.

### Focused proof
Depth starts at 1, legal deepening reaches at most 3, exhausted/no-gain paths stop without
executing another native query.

### Affected regression
All P17 + Core-B adaptive/root regressions.

### Duplicate-authority risk
High if Product invents a second branch/depth state machine.

---

## 7. P6 — P17 → P19 eligibility bridge

### Roadmap requirement
Exactly one executable P19 eligibility predicate over current scope, >=2 materially distinct
typed candidate explanations, governed P16 claim refs and governed Evidence refs.

### Current implementation paths
- `backend/app/v3/product/process_manager.py`
- `backend/app/v3/product/composition.py::_assess_root_cause`

### Current owner
Product process-manager callability.

### Current behavior
For ROOT_CAUSE, `len(observation.claim_ids) >= 2` routes to P19.
Composition then creates one P19 hypothesis per claim text and grounds it with P16 claim CONTEXT.

### Classification
`CONTRACT_MISMATCH`.

### Missing behavior
No current-scope check, no Evidence-per-candidate gate, no materially-distinct mechanism identity,
no explicit NEED_MORE_EVIDENCE disposition, and duplicate/reworded claims can accidentally make
P19 callable.

### Required owner
Product process-manager for callability. P19 remains epistemic assessment authority.

### Minimal contract delta
Implement one `P19Eligibility` / `eligible_candidates(snapshot)` function and one typed routing
disposition: CALL_P19 / NEED_MORE_EVIDENCE / INCONCLUSIVE.

Distinctness must use typed durable candidate mechanism/relation identity, never text similarity.

### Sealed invariants that must survive
- Product cannot create fake hypothesis B;
- P19 requires competing candidates;
- P16/P14 evidence authority remains unchanged;
- no regex/fuzzy/embedding threshold authority.

### Focused proof
1 candidate → NEED_MORE_EVIDENCE if legal discriminating path exists; otherwise INCONCLUSIVE.
Two wording variants with same mechanism remain one candidate. Two typed distinct current-scope
candidates with P16 + Evidence → CALL_P19.

### Affected regression
Product process-manager, composition root cause, P17/P19 suites.

### Duplicate-authority risk
Critical. There must be exactly one callability predicate.

---

## 8. P7 — multi-factor P19 RCA

### Roadmap requirement
P19 represents competing candidates with supporting/challenging/missing Evidence, temporal
consistency, alternatives, materiality and honest contribution/epistemic states.

### Current implementation paths
- `backend/app/v3/hypothesis_root_cause.py`
- `backend/app/v3/hypothesis_root_cause_provider.py`

### Current owner
P19.

### Current durable objects
Exactly three P19 durable record families: hypothesis, grounding, assessment.

### Current tests
P19 domain/provider/autonomous eval suites.

### Current evidence / seal
Already present:
- multiple candidate assessment;
- SUPPORTS / CHALLENGES / CONTEXT / INSUFFICIENT groundings;
- contribution classes;
- evidence strength;
- causal qualification and identification limitations;
- P18 policy dependency;
- no numeric causal authority without exact provenance;
- model must preserve all current hypotheses and cannot hide challenge groundings.

### Classification
`PARTIAL_MUST_EXTEND`.

### Missing behavior
No first-class current `scope_version`; no explicit missing-Evidence surface / temporal-consistency
field; no typed NextTestRequest output for unresolved competing hypotheses; current Product creates
hypotheses from claims rather than admitting pre-qualified candidate identities.

### Required owner
P19 for epistemic candidate assessment only; Product/P17 own pre-P19 routing.

### Minimal contract delta
Compose current P19 structures rather than rewrite them. Add scope binding and the minimum typed
assessment information needed to request a discriminating test without numeric probabilities.

### Focused proof
Competing supported/challenged candidates remain distinct; contradictory Evidence can weaken or
contest a candidate; absent causal identification cannot yield defensible causal conclusion.

### Affected regression
P19 + P20 causal publication legality.

### Duplicate-authority risk
High if P17/Product starts assigning final epistemic states.

---

## 9. P8 — P19 → P17 discriminating-test loop

### Roadmap requirement
P19 unresolved ambiguity → typed `NextTestRequest` → P17 legal step → Metabase → Evidence →
P19 reevaluation. Depth starts at 1 and deepens only on typed positive information gain;
hard max_depth 3.

### Current implementation
P17 already has `TEST_DISCRIMINATING_EVIDENCE`; P19 has grounded hypotheses; however no forward
typed P19→P17 request contract or recursive product coordinator exists.

### Classification
`MISSING`.

### Required owner
- P19 may identify the epistemic discrimination need;
- P17 owns legal investigation action;
- Metabase owns analytics;
- Product coordinates only.

### Minimal contract delta
Add immutable `NextTestRequest` with typed hypothesis/candidate refs, requested Evidence surface,
scope version and reason; Product feeds it into existing P17 legality rather than creating a second
investigation engine.

### Focused proof
Positive-gain request executes one new legal P17/Metabase Evidence step and reevaluates P19.
Duplicate/no-data/no-gain request stops with typed reason and no query. Depth never exceeds 3.

### Affected regression
P17 + P19 + Product root-cause composition.

### Duplicate-authority risk
Critical if P19 directly executes analytics or Product plans the query.

---

## 10. P9 — P18 relationship closure

### Roadmap requirement
Analytics and business relationship interpretation remain separate. Relationship conclusions
distinguish association/co-movement/relationship/contribution/causality and preserve supporting /
challenging Evidence, limitations and scope.

### Current implementation paths
- `backend/app/v3/business_relationship_policy.py`
- `backend/app/v3/product/composition.py::_resolve_relationship`
- P16/P17 claims + Evidence

### Current owner
P18 business relationship policy authority.

### Current proof
P18 explicitly performs no join discovery, analytics or causal semantics; requires exact
applicability scope; validates claim/session/obligation/context authority and persists policy use.

### Classification
`PARTIAL_MUST_EXTEND`.

### Gap
The policy surface proves applicability/legality but is not yet a complete V1 material relationship
artifact carrying explicit supporting/challenging Evidence refs and the full association →
causality distinction as a forward Product contract.

### Minimal contract delta
Prefer composing P16 Evidence links + P18 policy use instead of creating a second relationship
engine. Add only the typed V1 relationship-result projection required for reporting.

### Focused proof
Strong association with no causal identification cannot be promoted to causality; challenge
Evidence and exact scope survive into the relationship result/report.

### Affected regression
P18 + P19 relationship-dependent + P20 reporting.

### Duplicate-authority risk
High if correlation calculations or join discovery move into P18.

---

## 11. P10 — Evidence-backed P20 reporting

### Roadmap requirement
No trusted material analytical claim without Evidence. Report material must preserve Claim,
Evidence, Receipt, Scope and Freshness or sealed equivalents. Limited report is legal.

### Current implementation paths
`backend/app/v3/report_document.py`.

### Current owner
P20.

### Current tests / evidence
- P20 report suite;
- owner-scoped MUST accounting;
- currentness tests;
- numeric provenance tests.

P20:
- publishes from terminal Research only;
- validates exact P14 Evidence/receipt;
- supports P16/P17/P18/P19 sources;
- blocks unsupported numeric/causal publication;
- emits explicit limitations;
- reports currentness against source-set fingerprint.

### Classification
`ALREADY_PROVEN`.

### Required delta
No semantic rewrite. After P2, add an affected regression proving scope-version/currentness
propagation through the existing source authority.

### Focused proof
Existing no-governed-publishable-fact → LIMITED report remains GREEN under scope mutation.

### Duplicate-authority risk
High if Product generates confident narrative outside P20. Do not do so.

---

## 12. P11 — FAST / GUIDED / INVESTIGATION execution paths

### Roadmap requirement
Three distinct modes; simple analytics must not invoke the deepest research loop.

### Current implementation
Behavior is partially implicit:
- ordinary P14 analytical goals run native Metabase directly;
- RELATIONSHIP/ROOT_CAUSE and typed adaptive requirements enter P17;
- Product already avoids P17 for ordinary simple analytical goals.

### Classification
`PARTIAL_MUST_EXTEND`.

### Gap
No explicit stable `FAST / GUIDED / INVESTIGATION` routing contract or test matrix. Guided
multi-metric complex comparison is not a first-class mode.

### Required owner
Product execution-mode router over accepted ResearchBrief; no analytics ownership.

### Minimal contract delta
Add a deterministic typed routing classification. Reuse existing P14/P17/P18/P19 execution paths.

### Focused proof
Simple metric/breakdown/ranking/period comparison → FAST with zero P17/P19 calls.
Relationship/complex multi-metric → GUIDED bounded path.
RCA/adaptive/counter-evidence → INVESTIGATION.

### Affected regression
Product composition + P14/P17 call-count expectations.

### Duplicate-authority risk
Low if router only chooses existing owner path; high if it plans analytics.

---

## 13. P12 — Round-2 benchmark and new metamorphic corpus

### Round-2 current evidence
Canonical neutral comparison already executed 30 common cases and exposed the Phase-1 weaknesses.
The active branch retains the final comparison report and fixture source, but does not currently
retain a canonical V1 Phase-1 benchmark harness/manifest as a forward development gate.

### Classification
- same 30-prompt benchmark harness: `PARTIAL_MUST_EXTEND`;
- new hidden-like/metamorphic corpus: `MISSING`.

### Required owner
V1 eval only; never Product semantics.

### Minimal contract delta
Recover the frozen Round-2 corpus/fixture from comparison history without benchmark-specific Product
patches. Build a new structural metamorphic corpus covering the roadmap families. Assert invariants,
not exact prose.

### P0 gate
Must explicitly record:
- provider contract exceptions = 0;
- silent semantic drift = 0;
- cross-tenant leak = 0;
- invented numeric fact = 0;
- unsupported causal promotion = 0;
- eligible P19 routed to P19;
- scope replacement correct;
- Evidence-free trusted report = 0;
- restart/resume stable.

### Duplicate-authority risk
Benchmark must observe contracts, never become runtime authority.

---

## 14. P13 — immutable Phase-1 seal

### Classification
`MISSING` until P1-P12 are accepted.

### Required final artifact
Exactly one canonical Phase-1 candidate SHA + one immutable Phase-1 acceptance receipt declaring
`SEALED DIMA BRAIN V1`.

The receipt must freeze engine identity, migration head, Brain/scope/P19 eligibility contract
versions, benchmark/metamorphic results, provider/model counts, P0 results, governed limitations and
technical debt.

No Phase 2 begins automatically.

---

## 15. Deferred by roadmap

The following are explicitly `DEFERRED_BY_ROADMAP` for Phase 1 and must have zero implementation
diff during Brain closure:

- React / TSX / CSS / frontend routes / dashboard UI / Metabase embedding UI;
- connector implementation and onboarding UI;
- Company Map / Today / Radar product surfaces;
- sector productization;
- new finance/manufacturing/textile/plastics specialized engines;
- Resend live;
- Slack execution;
- ERP write-back;
- generic tool executor;
- `action:execute`;
- autonomous external side effects;
- Wren runtime/code/query engine/semantic authority;
- DEV80 / Validation50 / Hidden50.

---

## 16. Implementation order / reopen ledger

The implementation order is fixed:

`P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 proof → P11 → P12 → P13`.

Formal owning-contract reopen requirements:

| Reopen | Reason | Close condition |
|---|---|---|
| P17 provider adapter | system identities still model-emitted; repair contract absent | focused provider GREEN + full P17 regression |
| Research scope contract | first-class V1 scope version/mutation missing | mutation/restart/currentness GREEN |
| analytical request boundary | current forward trust exceeds request-invariant boundary | anti-second-planner architecture proof + native affected GREEN |
| Product completion | final requirement dispositions incomplete | no silent requirement loss proof |
| Product P19 callability | current rule is claim-count only | single executable predicate proof |
| P19/P17 bridge | recursive NextTestRequest absent | discriminating loop GREEN |
| P18 V1 projection | relationship result contract incomplete | evidence/scope/epistemic relationship proof |

P20 itself is not reopened for redesign. It receives affected regression after scope propagation.

---

## 17. Gap-map exit

This map is complete enough to authorize implementation because every Phase-1 family has:
current owner, current objects/tests/evidence, classification, missing behavior, minimal owning
delta, invariants, focused proof, affected regression and duplicate-authority risk.

It is not a claim that every listed delta is necessarily implemented as a new table/class. During
implementation, an existing sealed reference that proves the same invariant must be reused rather
than duplicated.
