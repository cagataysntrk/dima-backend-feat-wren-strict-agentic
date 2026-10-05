# DIMA BRAIN V2.1 — CURRENT HANDOFF

Updated: 2026-10-05

## 0. Read this first

Branch:

\`feat/dima-brain-v2-1-specification-closure\`

Frozen semantic Product:

\`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`

The Product is still frozen. Do not modify it without a new supervisor decision.

Certified engine remains:

- SHA: \`4c49b8da6b424b0fa4d8ef340ca1b238d12980c1\`
- release: \`0.63.18-dima.11.1\`
- runtime tag: \`v0.63.18-dima.11.1.1\`
- digest: \`sha256:0ff1e378b532cc986d871ed3945e677a7a6d0bfb28686b344dfa4ec8d397327d\`

Current release decision:

\`30-CASE READY = NO\`

\`paid authorization = OFF\`

\`full 9-sentinel panel = NOT AUTHORIZED\`

\`frontend = NOT AUTHORIZED\`

Current reason:

The prior 12-unit final-panel stop was a harness correctness/efficiency coupling defect. That harness defect is now fixed without touching Product semantics.

A single supervisor-authorized S3 diagnostic then ran on the unchanged frozen Product. It proved there is no provider runaway, but S3 still ends in retryable \`MATERIAL_GROUP_WAITING\` with the one parent native occurrence durably \`EXECUTED\` and not \`VERIFIED\`.

Therefore S3 remains \`2/4 PARTIAL\`, below the required \`>=3/4\` gate.

The full 9-sentinel panel was NOT run.

Architecture reassessment is now open. Architecture implementation/refactor is NOT authorized.

---

## 1. Development purpose

This branch exists to make the Brain V2 backend 30-case-ready through generic architecture laws and independent proof, not benchmark patching.

Permanent goals:

- one canonical semantic authority;
- Metabase owns native analytical HOW;
- Dima admits only governed Evidence;
- result-dependent continuation is backed by exact SelectionBinding;
- LangGraph owns durable orchestration/checkpoint/resume;
- native cognition/execution is effectively-once;
- scope/currentness/security/provenance fail closed;
- correctness and efficiency are measured separately.

This phase is backend-only.

Frontend, UI, demo frontend, visual Product work and 30-case execution remain forbidden until explicitly authorized.

---

## 2. Permanent architecture

Authority direction:

\`ResearchBrief / ResearchScope\`
→ \`AnalyticalIntentV1\`
→ \`Metabase native HOW\`
→ \`durable native occurrence\`
→ \`material observation / Evidence admission\`
→ \`SelectionBindingV1\`
→ \`dependent continuation\`
→ \`Completion Ledger\`
→ \`P20\`

Owners:

- Metabase/Metabot: native query cognition and physical query representation.
- LangGraph: orchestration, checkpoint, interrupt/resume.
- Dima stores: canonical Research/domain truth.
- Thin Dima Brain: business semantics, scope/currentness, Evidence, epistemics, permissions and orchestration policy.

Forbidden architecture moves:

- second semantic authority;
- Dima SQL/MBQL planner;
- raw-schema escape;
- Wren analytical fallback;
- Agent API restoration;
- benchmark fuzzy/regex/morph routing;
- prompt patching for a specific sentinel;
- engine rebuild without literal substrate proof.

---

## 3. Durable-resume Product closure

Supervisor-authorized Product change is frozen at:

\`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`

The implemented law:

\`WAITING\`
→ durable LangGraph interrupt/checkpoint
→ same-thread explicit resume
→ same Research/scope/tenant/principal
→ same durable EXECUTED occurrence
→ read-only observation
→ VERIFIED Evidence
→ SelectionBinding
→ dependent continuation.

Resume is not a new user turn.

Intake is not replayed.

Scope is not changed.

Native cognition replay = 0 for the durable parent.

Dataset/native execution replay = 0.

If observation remains unavailable, one explicit resume returns to bounded WAITING; no busy-loop.

Provider-free recertification is GREEN:

- focused Brain V2: \`37347542415\`
- Phase-1 aggregate: \`37347542513\`
- Phase-2/headless: \`37347542482\`
- semantic conformance + Wave A/B + mutation: \`37347543030\`
- frozen-family: \`37347542511\`

Migration remains single-head:

\`ff5b8e2c1a73\`

---

## 4. Harness correction after the first final-panel attempt

Previous final-panel run:

\`37348187000\`

The run stopped at S3 because the harness used one value, \`12\`, as both an efficiency target and a correctness exception boundary.

That was wrong.

Harness-only correction:

- removed \`PinpointBudgetExceeded\`;
- \`12\` is now only \`ORCHESTRATION_EFFICIENCY_SLO_UNITS\`;
- orchestration-unit debt can make \`efficiency_green = false\` but cannot make Product correctness fail;
- real hard runaway safety remains in the provider proxy;
- exception artifacts now attempt to preserve:
  - orchestration units used;
  - units by owner;
  - partial Brain state;
  - native occurrences;
  - provider receipt.

There is no live \`model_budget\` CLI/contract in the current harness. No fake parameter was added.

Real safety caps stayed unchanged:

- provider total: 16
- research_intake: 2 (scope-resume special case 4)
- Metabase: 15
- P17: 3
- P18: 1
- P19: 2
- prompt tokens: 400000
- completion tokens: 40000
- reasoning tokens: 30000
- provider cost: $0.35

The orchestration tracker is a measurement layer, not a provider-call counter.

Its material owner is named \`material_executor\`; each read-only same-occurrence observation entry is counted.

---

## 5. S3-only diagnostic — canonical result

Run:

\`37353003472\`

Job:

\`111908606464\`

Probe:

\`CHANGE_DEPENDENT_DRILLDOWN_V1\`

Frozen Product:

\`e257a4754487ec4ac7bfe9fa93966e5ac4a5d1ea\`

Workflow:
SUCCESS.

Harness exception:
NONE.

Hard safety:
CLEAN.

Product mechanical result:
RED.

### Provider measurements

- total requests: 5
- research_intake: 1
- Metabase provider calls: 4
- blocked requests: 0
- prompt tokens: 74,600
- completion tokens: 2,976
- reasoning tokens: 1,530
- provider-reported cost: $0.01272674
- latency: 52,329 ms

This is not provider runaway.

### Orchestration-efficiency measurement

- SLO: 12 units
- observed: 16 units
- one Intake boundary
- fifteen material-executor boundary entries
- efficiency SLO: missed

The fifteen material entries are not fifteen Metabot provider calls.

The frozen Product performs up to five observation entries per \`run_next()\`:

- initial execution/observation attempt;
- read-only observation backoff at 0.2 / 0.6 / 1.2 / 2.4 seconds.

The live Brain path performs:

- initial graph run;
- up to two explicit same-thread resumes.

So:

\`3 × 5 = 15\`

material-executor entries are structurally explained.

---

## 6. Exact S3 state after diagnostic

Accepted semantics are correct:

- parent: May–June 2026 department CHANGE ranking;
- child: select first ranked department and drill one level into machine;
- dependency is explicit;
- scope remains \`scope_v1\`.

Exactly one parent native occurrence exists:

- execution_link_id: \`58d8e98f-c604-4a3c-a029-6389f7ed7e8e\`
- native_query_id: \`LHewV7dcCB1HRwZDgFn0d\`
- query fingerprint: \`f6ba3fb1327c04b9bb58adb1c83a4ed6dcbc0baa192fa742d938b293ef1a9455\`
- state: \`EXECUTED\`
- Evidence: absent
- receipt: absent

Duplicate native execution:
0.

Brain state:

- workflow_status: \`WAITING\`
- last_completed_node: \`MATERIAL_GROUP_WAITING\`
- Evidence revision: 0
- parent obligation: DELEGATED
- dependent child: READY
- SelectionBinding: absent
- child native drilldown: not executed
- P17/P19/P20: unopened

---

## 7. Current first unclosed boundary

The 12-unit correctness gate is no longer the blocker.

The current first unclosed Product/substrate boundary is:

\`durable EXECUTED parent occurrence\`
→ read-only \`/api/dima/engine/v1/native-query-material-observation\`
→ observation remains unavailable through all bounded same-occurrence attempts
→ parent never becomes VERIFIED
→ Evidence absent
→ SelectionBinding absent
→ dependent child cannot execute
→ Brain remains WAITING.

The Product correctly avoids replay.

What is NOT yet known:

The diagnostic artifact does not expose the underlying read-only observation error detail that caused each \`R1_NATIVE_MATERIAL_OBSERVATION_UNAVAILABLE\`.

Therefore do not guess whether the cause is:

- delayed native-occurrence visibility;
- an HTTP response such as 404/422;
- a material-observation shape/attestation issue;
- timeout/transport;
- or another read-only observation contract condition.

That missing lower-level reason is the first observability gap for architecture reassessment.

---

## 8. S3 quality decision

Existing canonical Product-quality rubric applies.

Passed:

- typed CHANGE ranking accepted;
- result dependency accepted;
- current scope preserved;
- one durable native occurrence;
- duplicate native = 0;
- provider safety clean;
- no P17/P19 contamination.

Missing:

- parent VERIFIED Evidence;
- receipt;
- SelectionBinding;
- child drilldown;
- terminal completion.

Quality:

\`2/4 PARTIAL\`

Required:

\`>=3/4\`

Result:

FAIL.

Therefore the supervisor condition for the full final panel was not met.

No new full 9-sentinel panel was run.

---

## 9. Current authorization

S3 diagnostic:
OFF.

Final 9-panel:
OFF.

Broad paid:
OFF.

30-case:
CLOSED.

Frontend:
NOT AUTHORIZED.

Product changes:
NOT AUTHORIZED.

Architecture reassessment:
OPEN, read-only until supervisor decision.

---

## 10. What architecture reassessment must answer

The next decision must locate the exact owner of persistent material-observation unavailability while preserving effectively-once execution.

Required questions:

1. What exact lower-level error does \`native-query-material-observation\` return for the persisted S3 parent occurrence?
2. Is that failure transient visibility, semantic material-shape rejection, currentness mismatch, or another contract condition?
3. Is the current 5-attempt × 3-turn observation policy the correct bounded lifecycle, or is it merely hiding a deterministic non-transient observation failure?
4. Can the failure reason be persisted/telemetried without changing query semantics or replaying native work?
5. Which owner must change, if any, while keeping:
   - native replay = 0;
   - parent cognition replay = 0;
   - same thread/Research/scope;
   - bounded WAITING;
   - fail-closed Evidence;
   - no second semantic authority?

Do not code the answer until a supervisor explicitly authorizes it.

---

## 11. Next legal action

STOP paid work.

Do not run S3 again.

Do not run the full panel.

Do not change Product \`e257a475...\`.

Do not change engine, prompt, grammar, Metabot or provider caps.

Perform architecture reassessment / obtain supervisor decision for the persistent:

\`EXECUTED → material observation unavailable\`

boundary.

One-line handoff:

\`Product e257a475... remains frozen; 12-unit harness correctness bug is closed; S3-only diagnostic 37353003472 is safety-clean but still 2/4 because one durable parent stays EXECUTED/not VERIFIED after bounded same-occurrence observation, so no Evidence/SelectionBinding/child; full panel was not run; all paid auth is OFF; architecture reassessment is open.\`
