# DIMA BRAIN V2.1 — CURRENT HANDOFF

Updated: 2026-10-05

## 0. Current status — read first

Current branch:

\`feat/dima-brain-v2-1-specification-closure\`

Current frozen semantic Product:

\`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`

Current certified engine:

- SHA: \`4c49b8da6b424b0fa4d8ef340ca1b238d12980c1\`
- release: \`0.63.18-dima.11.1\`
- runtime tag: \`v0.63.18-dima.11.1.1\`
- digest: \`sha256:0ff1e378b532cc986d871ed3945e677a7a6d0bfb28686b344dfa4ec8d397327d\`

Current release decision:

\`30-CASE READY = NO\`

\`paid authorization = OFF\`

\`broad 30-case = CLOSED\`

\`frontend = NOT AUTHORIZED\`

Reason:

The supervisor-authorized durable WAITING/resume lifecycle closure is provider-free GREEN and fully recertified. The one authorized final paid 9-sentinel panel, run \`37348187000\`, stopped at S3 with:

\`PINPOINT_ORCHESTRATION_BOUNDARY_BUDGET_EXHAUSTED\`

\`metabot would exceed the 12-unit live ceiling\`

S1 and S2 completed GREEN. S3 raised an exception before terminal Product adjudication. Matrix fail-fast cancelled S4-S9.

The supervisor exception explicitly forbids another fix round after a failed final panel.

Therefore the next legal action is:

\`STOP / ARCHITECTURE REASSESSMENT / NEW SUPERVISOR DECISION REQUIRED\`

Do not retry the panel and do not change a ceiling merely to make the benchmark pass.

---

## 1. Development purpose

The purpose of this branch is to make Brain V2 backend 30-case-ready through architecture closure, not through benchmark-specific patching.

The intended backend proves:

- one canonical owner for analytical meaning;
- Metabase owns native analytical HOW;
- Dima owns business semantic authority and Evidence admission;
- result-dependent continuation is source-backed by SelectionBinding;
- Completion Ledger is canonical lifecycle authority;
- LangGraph owns durable orchestration/checkpoint/resume;
- security/currentness/provenance fail closed;
- broad quality is measured only after deterministic/provider-free closure.

This phase is backend-only.

UX/demo references mean **contract-ready for future UX**, not permission to build UI.

Forbidden:

- frontend;
- web UI;
- Ask screen;
- Investigation screen;
- Evidence Drawer;
- Report/Decision UI;
- dashboard UI integration;
- demo frontend;
- visual Product work.

---

## 2. Permanent architecture

Canonical authority path:

\`user/business request\`
→ \`ResearchBrief / ResearchScope\`
→ \`AnalyticalIntentV1\`
→ \`Metabase native HOW\`
→ \`attested material / AnalyticalExecutionManifestV1\`
→ \`governed Evidence\`
→ \`SelectionBindingV1\`
→ \`Completion Ledger\`
→ \`P20\`

Permanent ownership:

- Metabase/Metabot: native analytics/query cognition and physical query representation.
- LangGraph: orchestration, routing, durable checkpoint/resume lifecycle.
- Dima domain stores: canonical business/research truth.
- Thin Dima Brain: business semantics, scope/currentness, Evidence, epistemics, decisions, permissions and orchestration policy.

Dima does not become:

- a SQL/MBQL planner;
- a second analytics engine;
- a physical-query reverse-engineer;
- a second semantic authority;
- a benchmark vocabulary router.

Physical implementation details are not Product semantic authority:

- Lib UUID;
- exact expression tree;
- exact stage topology;
- JVM datetime class;
- physical metric expansion count;
- exact aggregation placement.

---

## 3. Frozen Product identities

Semantic Product:

\`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`

Migration head:

\`ff5b8e2c1a73\`

Grammar/schema identities:

- \`dima_analytical_grammar_v1\`
- \`dima_analytical_intent_v1\`
- \`dima_analytical_execution_manifest_v1\`
- \`dima_selection_binding_v1\`

Model topology:

- Dima cognition: \`openai/gpt-5.6-luna\`
- Metabot: \`openrouter/openai/gpt-5.6-luna\`
- cascade: NONE

No dima.12.

Do not create a new engine build for a Product/orchestration defect.

---

## 4. Closed V1 grammar

Supported primitives:

- OBSERVE
- BREAKDOWN
- COMPARE
- RANK
- SELECT
- DRILLDOWN
- RELATE
- RCA
- REPORT
- SCOPE_PATCH

Important legal compositions:

- OBSERVE
- OBSERVE → BREAKDOWN
- COMPARE
- COMPARE → RANK
- COMPARE → RANK → SELECT → DRILLDOWN
- RELATE
- RCA
- RCA → NEXT_TEST → RCA
- REPORT(current governed state)
- SCOPE_PATCH → supported operation

Unsupported semantics fail closed as UNSUPPORTED or CLARIFY.

Do not invent a semantic family during benchmark recovery.

---

## 5. Supervisor durable-resume exception — implemented

The authorized scope was exactly:

\`WAITING → durable same-thread resume\`

Product semantic commits:

- \`80fa1df917aa22d2f414f9e8625c441607b156c4\`
  - explicit resumable material wait nodes;
  - \`MATERIAL_GROUP_WAITING\` and \`MATERIAL_WAITING\` no longer terminal END;
  - LangGraph dynamic \`interrupt()\` boundary.
- \`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`
  - explicit \`resume_waiting()\`;
  - same thread/tenant/principal/Research/scope verification;
  - \`Command(resume=...)\`;
  - WAITING cannot fall through generic crash-resume API.

Permanent lifecycle law:

1. material side effect may become durably EXECUTED;
2. if semantic observation is temporarily unavailable, Product returns retryable WAITING;
3. Brain V2 checkpoints at an explicit interrupt, not END;
4. a later explicit resume is **not** a new user turn;
5. Intake is not rerun;
6. accepted scope is not mutated;
7. same material group/request identity is resumed;
8. durable occurrence is re-observed;
9. Metabot cognition is not replayed for the already-EXECUTED parent;
10. dataset/native execution is not replayed;
11. if observation is still unavailable, one resume call returns to bounded WAITING and interrupts again;
12. no internal busy-loop;
13. once observation becomes legal/current, Evidence is admitted;
14. dependent continuation may proceed only from VERIFIED parent material.

---

## 6. Durable-resume provider-free proofs

Provider-free/state-machine proof added for:

- in-memory WAITING → interrupt → reconstructed service → same-thread resume → Evidence → completion;
- generic \`MATERIAL_WAITING\` sibling;
- repeated-unavailable resume remains WAITING after exactly one explicit resume;
- Postgres checkpointer close/reopen + reconstructed service;
- owner-level later \`run_next\` reuses exact native query/payload occurrence;
- \`resumed_exact_occurrence = true\`;
- Metabot post count remains 1 across the waiting/recovery boundary;
- live harness before/after identity checks;
- resume-provider delta protection.

Full post-exception recertification:

- focused Brain V2: \`37347542415\` — GREEN
- Phase-1 aggregate: \`37347542513\` — GREEN
  - deterministic closure: 186 passed
  - Research/Scope: 317 passed
  - P17: 145 passed
  - P19: 53 passed
  - P20/Core-B: 90 passed
  - security/hygiene: 26 passed
  - migration: single head \`ff5b8e2c1a73\`
- Phase-2/headless: \`37347542482\` — GREEN
- semantic conformance + Wave A + independent Wave B + mutation canaries: \`37347543030\` — GREEN
- frozen-family closure: \`37347542511\` — GREEN

Engine, prompts, semantic grammar, provider budgets, Metabot and model topology were unchanged.

---

## 7. Final paid panel

Authorized final run:

\`37348187000\`

Checkout:

\`5cb269f91524c0dfd76db658dcb0b34e5b8130a2\`

Frozen semantic Product:

\`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`

### S1 — Direct analytics

SUCCESS / mechanical GREEN.

- provider requests: 3
- prompt tokens: 37,866
- completion tokens: 680
- reasoning tokens: 125
- latency: 10,117 ms
- cost: $0.00876681
- one VERIFIED native occurrence
- duplicate native = 0

### S2 — Temporal comparison

SUCCESS / mechanical GREEN.

- provider requests: 4
- prompt tokens: 55,594
- completion tokens: 1,229
- reasoning tokens: 465
- latency: 16,134 ms
- cost: $0.00725577
- one VERIFIED native occurrence
- temporal projection closure remained GREEN

### S3 — CHANGE ranking + dependent drilldown

STOP / exception.

Exception:

\`PINPOINT_ORCHESTRATION_BOUNDARY_BUDGET_EXHAUSTED\`

Detail:

\`metabot would exceed the 12-unit live ceiling\`

The live probe stopped before a terminal Product artifact was available:

- no final Brain state for scoring;
- no final native-occurrence projection;
- no final SelectionBinding/child result for scoring;
- no valid provider receipt projection.

The failing boundary is the certification live \`OrchestrationBudget.consume("metabot")\` guard.

The current guard:

- allows at most 12 orchestration boundary units;
- counts structured cognition boundaries;
- counts each bounded material executor call as one Metabot unit.

Runtime evidence showed multiple internal Metabot query-construction iterations before the boundary exhaustion, including an intermediate rejected query construction referencing unavailable column name \`metric\`.

This is distinct from the previously fixed WAITING/resume lifecycle.

### S4–S9

No same-run result.

They were cancelled by matrix fail-fast after the S3 job-level exception.

Do not carry older panel results forward as same-SHA proof.

---

## 8. Final acceptance result

Required:

- complete 9-case same-SHA panel;
- >=34/36;
- every case >=3/4;
- >=7 FULL;
- exception = 0;
- silent wrong = 0;
- security violation = 0;
- causal overclaim = 0;
- duplicate native = 0.

Actual:

- complete 9-case panel: FAIL
- >=34/36: NOT ADJUDICABLE
- every case >=3/4: NOT ADJUDICABLE
- >=7 FULL: NOT ADJUDICABLE
- exception = 0: FAIL
- observed silent wrong: 0
- observed security/cross-tenant violation: 0
- observed causal overclaim: 0
- observed duplicate native: 0 in completed cases

Therefore:

\`30-CASE READY = NO\`

Do not reinterpret S1/S2 success plus old panel results as a final seal.

---

## 9. Current blocker classification

The durable-resume Product law is provider-free GREEN.

The final paid seal was instead blocked by:

\`S3 Metabot/native cognition path → live OrchestrationBudget 12-unit guard\`

This is not permission to:

- raise the live limit;
- raise provider budgets;
- change prompts;
- change Metabot;
- change the engine;
- change grammar;
- add benchmark vocabulary;
- add fuzzy/regex/morph matching;
- special-case S3;
- retry the same panel hoping for a lower cognition path.

The supervisor exception explicitly required STOP if the final panel missed acceptance.

---

## 10. Authorization state

Final paid-panel authorization:

OFF.

Broad paid:

OFF.

30-case:

CLOSED.

Frontend:

NOT AUTHORIZED.

No new fix round is authorized.

---

## 11. Required architecture reassessment

A new supervisor decision must answer the bounded-cognition question before any further coding or paid run.

The next review should distinguish at least:

1. whether the 12-unit live orchestration guard is a certification-only diagnostic ceiling or a permanent release invariant;
2. whether a legal S3 path is required to fit under that invariant deterministically;
3. whether Metabot's variable internal query-construction cognition must be represented/measured differently from Dima owner-boundary work;
4. whether the S3 failure reveals a Product orchestration inefficiency, a Metabot cognition variance issue, or an evaluation-harness coupling problem;
5. how to preserve the permanent laws:
   - no engine change without proof;
   - no prompt/benchmark patch;
   - no provider-budget rescue;
   - no parent native replay;
   - no second semantic authority;
   - no unbounded retry.

Until that decision exists:

\`STOP\`

---

## 12. Development rules that remain permanent

Never:

- create Brain V3;
- restore Wren execution;
- add another analytics engine;
- restore Agent API;
- write SQL/MBQL planning inside Dima;
- make physical query shape semantic authority;
- duplicate canonical domain stores into graph state;
- route via fuzzy/regex/morph/prompt benchmark vocabulary;
- increase ceilings as a correctness fix;
- retry paid same-SHA hoping for luck;
- weaken tenant/principal/currentness/security;
- bypass Evidence admission;
- manufacture SelectionBinding from unverified material;
- let P20 reopen analytics;
- start frontend because backend is “almost ready.”

For any newly authorized future work:

\`RED → first invalid boundary → exact owner → generic invariant → provider-free reproducer → stateful/metamorphic siblings → generic fix → affected PF → wider PF → freeze → surgical live proof → receipt\`

---

## 13. Canonical documentation order

1. \`backend/belgeler/metabase/README.md\`
2. \`DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md\`
3. \`DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md\`
4. \`DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md\`
5. \`DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md\`
6. \`DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md\`

Historical documents under \`legacy/\` are forensic context only.

---

## 14. One-line handoff

\`Durable WAITING/resume closure = provider-free GREEN; final Product = e257a475...; final paid panel S1/S2 GREEN, S3 STOP on unchanged 12-unit live orchestration budget, S4-S9 cancelled; paid OFF; 30-case CLOSED; frontend forbidden; no further fix/retry authorized; architecture reassessment required.\`
