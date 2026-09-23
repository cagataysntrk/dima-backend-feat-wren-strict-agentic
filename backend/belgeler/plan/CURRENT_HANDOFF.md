# CURRENT HANDOFF

## ACTIVE AUTHORITY

Read in this order:

1. `backend/belgeler/plan/CURRENT_HANDOFF.md`
2. `backend/belgeler/plan/DIMA_DAY7_FINAL_CLOSURE_AND_DAY8_HANDOFF.md`
3. `backend/belgeler/plan/DIMA_DAY8_ROOT_CAUSE_ARCHITECTURE_AND_PRIMITIVE_INVENTORY.md`
4. `backend/belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md`
5. `backend/belgeler/plan/DIMA_CORRECTNESS_HARVEST_AND_ABLATION_PROTOCOL.md`
6. Roadmap P11
7. Architecture report R13

## SEALED DAY7

```text
DAY7 / P10                  CLOSED / SEALED
Day7 product behavior SHA   ce82d48bb8ab127a2dd5f7a63ebb25604a6557a6
provider-free seal          35872766887 = GREEN
production /ask-v2          OFF
```

Do not reopen Day7.

## CURRENT DAY8 STATE

```text
P11 — DAY8 ROOT-CAUSE BRANCH

D8-A1 HypothesisLedger                 GREEN
D8-A2 EpistemicLabelGate               GREEN
D8-B hypothesis proposal boundary      GREEN
D8-C execution-mode                    GREEN
D8-C bootstrap/applicability           GREEN
D8-C server-owned next-test identity   GREEN
D8-C Manager-loop wiring               GREEN
D8-C real-Wren sentinel                GREEN

latest Day8 PRODUCT behavior SHA
810fa70ded3bca53542316d32a5497302b4eb9c7

latest post-RED focused
35898621489 = GREEN

full affected Day7 regression
35898591894 = GREEN

paid Sol calls total                   9
live certification                     OPEN / VALID RED
ROOT_CAUSE direct executable           false
ResearchTaskKind.ROOT_CAUSE            DOES NOT EXIST
ROOT_CAUSE → QUERY alias               DOES NOT EXIST
CONFIRMED_CAUSE                        ALWAYS DENY
```

Current Day8 product surface now includes:
- `backend/app/v2/models.py`
- `backend/app/v2/epistemics.py`
- `backend/app/v2/hypothesis_proposals.py`
- `backend/app/v2/manager_policy.py`
- `backend/app/v2/capability_bindings.py`
- `backend/app/v2/acceptance.py`
- `backend/app/v2/manager_preacceptance.py`
- `backend/app/v2/representability.py`
- `backend/app/v2/research_tasks.py`
- `backend/app/v2/root_cause_orchestration.py`
- `backend/app/v2/manager_loop.py`

### D8-C architecture now implemented

```text
ROOT_CAUSE = ORCHESTRATED
spec.executable = derived compatibility view (DIRECT only)

accepted ROOT_CAUSE
→ current inspected VERIFIED Evidence, if present
  OR deterministic unique lossless observational bootstrap
→ bounded hypothesis proposal
→ server-owned next-test identity
→ existing Day7 task/fanout/registry/tool machinery
→ VERIFIED Evidence
→ inspection
→ explicit SUPPORTS / CONTRADICTS
→ CANDIDATE_CAUSE ceiling
```

Permanent distinctions remain:
- trigger Evidence is not SUPPORTS Evidence,
- proposal is not task,
- task is not Evidence,
- completed-but-unverified result is not epistemic Evidence,
- priority/interestingness is not truth,
- association/contribution is not causation,
- model cannot mint SemanticHandle/Evidence/ResearchTask/Hypothesis identity,
- `CONFIRMED_CAUSE -> CAUSAL_NOT_IDENTIFIED`.

### Metabase reference used

Upstream Metabase was used only as an architecture/pattern reference:
candidate → applicability → materialization → execution → stored result → optional
interestingness. Metabase runtime is NOT an analytical substrate in this release.

### Live Sol receipt

`35894577133`:
- INVALID measurement,
- class = EVAL/HARNESS/FIXTURE,
- 2 Sol calls,
- trust plane correctly rejected an inadmissible TREND next-test proposal,
- harness was fixed generically to feed rejection back into bounded replanning.

`35895279649`:
- VALID measurement,
- RED before full root-cause cognition closure,
- 5 Sol calls,
- first actionable gap exposed provider/task contract mismatch; the model did not remain on an
  admissible governed next-test path.

Generic root fix after the valid RED:
- one task-kind → existing capability/tool mapping now drives both advertisement and runtime admission,
- provider schema no longer advertises next-test task kinds that Day8 cannot materialize,
- `ROOT_CAUSE_NEXT_TEST_CONTRACT` exposes admissible DIRECT task families and required semantic shapes,
- no test sentence, keyword, business literal, causal threshold or provider-specific branch was added.

Post-fix deterministic proof:
`35895808495 = GREEN`, including affected Day7 regressions, Day8 contracts, Manager-loop,
provider-free live harness, and the one real-Wren root-cause sentinel.

Combined paid model calls = 7.
No third paid run was executed.

## LATEST SUPERVISED LIVE RE-MEASUREMENT

Run `35898027005`:

```text
measurement_valid       = true
measurement_validity    = VALID
result                  = RED
Manager model           = openai/gpt-5.6-sol
Manager calls           = 2
semantic-linker calls   = 0
temporal-model calls    = 0
model-call ceiling      = 5

product_behavior_sha    = 3091651aea93e42e00521654af8d5dc2c51dc9c3
run head                = d5ac338ac5b242e86c77469075e6c3e8b405a72c
scenario_hash           = 8379daa7fc70a678514b7f87dcb41fcdfec4d317d8ded4cc2712ee7cfb4c8d6a
harness_version         = 4ae479eb171eccb709eb326309734779533079ab
```

The re-measurement used the exact same canonical scenario and exact same harness blob as
`35895279649`.

First incorrect transition:

```text
inspected VERIFIED initial Evidence
→ bounded hypothesis proposal                  CORRECT
→ server-owned hypothesis identity             CORRECT
→ expected governed hypothesis next-test
→ model selected resolve_semantics             FIRST INCORRECT TRANSITION
```

Initial surface reading looked like MODEL_COGNITION. Cross-check of the actual provider contract
showed the deeper single-owner defect, so final classification is:

```text
CONTRACT/ARCHITECTURE
```

Single owner:
post-acceptance Manager-safe semantic-handle projection.

Broken invariant:
opaque governed handles may hide canonical values, but cognition must receive the non-secret
type/provenance metadata required to use those handles against the deterministic capability/task
contract. Otherwise the Manager is forced to re-resolve semantic information the trust plane
already owns.

Generic post-RED fix:
- `HypothesisLedger.semantic_handle_metadata()` exposes only governed non-secret metadata;
- `SEMANTIC_HANDLE_CATALOG` maps Manager aliases such as `h1` to `target_kind` and provenance;
- canonical semantic values remain inside `SemanticHandleRegistry`;
- ROOT_CAUSE policy now prefers already-governed handles when they satisfy the advertised next-test
  contract, and semantic expansion remains an evidence-grounded fallback;
- no user phrase, business literal, provider-specific branch or prompt example was added.

Deterministic proof after this fix:

```text
35898621489 = GREEN   Day8 focused + live-harness contract + real-Wren sentinel
35898591894 = GREEN   full affected Day7 regression
```

Current product behavior SHA after the generic fix:
`810fa70ded3bca53542316d32a5497302b4eb9c7`.

Paid Day8 total is now 9 Sol calls:
2 + 5 + 2.

## CURRENT SUPERVISOR AUTHORITY — DAY9/P12-A OPEN

The prior "no Day9" stop is superseded.

Current authority:

```text
DAY8 deterministic engineering = GREEN
DAY8 real-Wren                  = GREEN
DAY8 live Sol                   = OPEN / NOT GREEN
DAY8 final seal                 = DEFERRED TO INTEGRATED LIVE GATE

CURRENT ACTIVE TICKET
= DAY9 / P12-A
  deterministic ReportDocument authority
```

Day8 behavior is frozen at:

`810fa70ded3bca53542316d32a5497302b4eb9c7`.

No more standalone paid Day8 root-cause tests are authorized. The remaining live cognition debt
must be re-exercised later inside the canonical Day10 integrated Product-MVP live gate.

Day9-A is provider-free only. It may add a deterministic immutable report projection over existing
governed Evidence/Findings/semantic scope and presentation artifact refs. It may NOT add:
- an LLM report writer,
- DB/Wren execution,
- semantic resolution,
- a new Evidence store,
- PDF/HTML export,
- frontend/report routing,
- Day10 behavior.

Expected file boundary:
- `backend/app/v2/report_builder.py`,
- `backend/app/v2/models.py` only if canonical report models belong there,
- focused Day9 tests,
- living docs / Harvest.

Do not touch Day8 execution/cognition owners unless an independent P0 proves necessity.

---

## NEW DEVELOPER ONBOARDING — READ BEFORE TOUCHING CODE

### What this product is

Dima V2 is a governed analytical/research agent. Its architecture deliberately separates:

```text
LLM / Manager
= cognition, decomposition, proposal, observe/replan

deterministic trust plane
= semantic authority, execution validity, numeric truth, Evidence,
  lifecycle/completion truth, security and provenance
```

The product is NOT a raw-SQL agent and NOT a free-form causal reasoner.

Permanent ownership split:

```text
AcceptedTurnContract / accepted authority
→ exactly one downstream semantic authority per user turn

SemanticResolver / SemanticHandleRegistry
→ canonical semantic truth

ResearchTask / RequirementLedger / capability gates
→ governed analytical work identity and validity

Wren / DB
→ numeric execution truth

QueryContract / EvidenceArtifact / EvidenceStore
→ proof and lineage

ManagerRuntime / UserObligationLedger / CompletionGate
→ bounded research lifecycle and completion truth

HypothesisLedger / EpistemicLabelGate
→ Day8 epistemic admissibility and public claim ceiling
```

### Where Day7 ended

Day7/P10 is SEALED. Do not reopen it to make Day8 easier.

Sealed product behavior:
`ce82d48bb8ab127a2dd5f7a63ebb25604a6557a6`.

Key Day7 invariants that Day8 inherits:
- global Manager turn hard ceiling = 6 across preacceptance + research,
- Evidence existence != Manager inspection,
- current USER_MUST cannot silently disappear,
- agent-derived investigation cannot rewrite USER_MUST,
- derived Evidence preserves parent Evidence + QueryContract lineage,
- raw SQL / raw joins / security bypass are forbidden,
- paid evaluation uses smallest-falsifying-test progressive widening.

### Where Day8 actually is

Latest Day8 product behavior:
`810fa70ded3bca53542316d32a5497302b4eb9c7`.

Latest post-RED focused/provider-free proof:
`35898621489 = GREEN`.

Full affected Day7 regression:
`35898591894 = GREEN`.

Implemented and green:

```text
D8-A1
typed epistemic models
+ HypothesisLedger
+ Evidence structural validation

D8-A2
EpistemicLabelGate
+ EvidenceLinkedFindingBuilder
+ CONFIRMED_CAUSE hard deny

structural seams
active ROOT_CAUSE only
+ live current-run Evidence view
+ inspected-Evidence admission

D8-B
HypothesisProposal
+ HypothesisEvidenceRelationProposal
+ HypothesisProposalBoundary

D8-C
execution-mode authority
+ deterministic ROOT_CAUSE bootstrap
+ server-owned HypothesisNextTestProposal admission
+ Day7 ResearchTask/fanout/tool reuse
+ bounded Manager-loop cognition wiring
+ real-Wren root-cause sentinel
+ provider-facing next-test contract aligned with runtime admission
```

Current Day8 product files:
- `backend/app/v2/models.py`
- `backend/app/v2/epistemics.py`
- `backend/app/v2/hypothesis_proposals.py`

Focused tests:
- `backend/tests/test_v2_day8_hypothesis_ledger.py`
- `backend/tests/test_v2_day8_epistemic_label_gate.py`
- `backend/tests/test_v2_day8_hypothesis_proposals.py`

Provider-free CI:
- `.github/workflows/v2-day8-focused.yml`

### Day8 epistemic architecture in one flow

```text
accepted active ROOT_CAUSE USER_MUST
        ↓
current + VERIFIED + inspected Evidence
        ↓
model may PROPOSE hypothesis text + existing governed IDs
        ↓
HypothesisProposalBoundary
        ↓
HypothesisLedger mints hypothesis_id
        ↓
trigger Evidence stays trigger-only
        ↓
explicit SUPPORTS / CONTRADICTS proposal
        ↓
structural admission
        ↓
EpistemicLabelGate
        ↓
OBSERVATION / COMPARISON / ASSOCIATION /
CONTRIBUTION / CANDIDATE_CAUSE
        ↓
CONFIRMED_CAUSE always denied:
CAUSAL_NOT_IDENTIFIED
```

Hard distinctions:

```text
trigger Evidence != SUPPORTS Evidence
Hypothesis != Evidence
planned next test != Evidence
status != epistemic label
association != causation
contribution != causation
interestingness != truth
candidate cause != confirmed cause
```

### Why the live Evidence view exists

Do not restore a frozen `current_evidence_refs` constructor snapshot.

Root-cause work is iterative:

```text
hypothesis
→ governed next test
→ new VERIFIED Evidence
→ inspect
→ explicit evidence relation
→ further test
```

`CurrentRunEvidenceView` reads membership from the existing Day7 ManagerRuntime snapshot.
It creates no Evidence registry and exposes no arbitrary membership mutator.

Invariant:
new same-run Evidence becomes visible to the same HypothesisLedger without reconstructing
epistemic authority; foreign/unverified Evidence remains inadmissible.

### ROOT_CAUSE status rule

Mutable hypothesis state is legal only when the ROOT_CAUSE USER_MUST is:

```text
ACCEPTED
READY
IN_PROGRESS
```

Reject:
`PROPOSED`, `NEEDS_CLARIFICATION`, `BLOCKED_DATA_GAP`, `LIMITED`,
`UNSUPPORTED`, `SUPERSEDED`, terminal `VERIFIED`.

An unaccepted or terminal causal obligation cannot manufacture new epistemic state.

### What D8-B does NOT do

D8-B is proposal admission only.

It does NOT:
- call an LLM itself,
- execute a DB query,
- call Wren,
- create ResearchTasks,
- alter Manager loop execution mapping,
- make ROOT_CAUSE executable,
- perform causal inference,
- turn priority/interestingness into truth,
- mint model-owned IDs.

Manager/model may echo/select existing governed IDs only.
Server-owned registries/ledger own identity.

### Failure history you need to know

Focused run `35884376351` failed before D8-B execution because one stale private helper
call remained after exposing the priority-only classifier:

```text
self._is_priority_only
→ should have been
self.is_priority_only
```

Failure class:
`EVAL/CONTRACT REGRESSION`, not architecture/model/resolver failure.

Fix:
one generic owner-level rename completion only.

Proof after fix:
`35884577376 = GREEN`.

Do not reopen or overfit this failure.

### Permanent development protocol

Before any patch:

```text
RED
→ first incorrect transition
→ classify failure
→ identify one owner
→ state invariant
→ generic fix
→ narrow provider-free proof
```

Failure taxonomy:
- `MODEL_COGNITION`
- `CONTRACT/ARCHITECTURE`
- `RESOLVER_TRUTH`
- `EVAL_ORACLE`
- `TRANSPORT/PROVIDER`

Forbidden:
- testcase-derived prompt rules,
- keyword/regex/morphology patches,
- business-sentence special cases,
- model-specific business branches,
- increasing budgets to make a case pass,
- broad paid reruns while a narrow proof answers the question.

### STOP-THE-LINE architecture violations

Stop development and repair abstraction if any appears:
- second semantic owner,
- raw prompt reparsed downstream as semantic authority,
- silent USER_MUST loss,
- automatic ambiguity pick,
- model-minted canonical/semantic/task/Evidence identity,
- Evidence claim without verification/provenance,
- uninspected Evidence used by cognition proposal,
- no-path cross-domain join,
- tenant/RLS/CLS bypass,
- trigger Evidence silently becoming SUPPORTS,
- priority/interestingness becoming epistemic truth,
- causal claim strengthened by a threshold/model confidence,
- ROOT_CAUSE disguised as direct QUERY.

### Current authorization boundary

D8-C implementation authority has been consumed through the supervised live gate.

Current state is STOP:
- deterministic/provider-free and real-Wren D8-C engineering is GREEN,
- supervised post-fix live re-measurement `35898027005` is VALID RED,
- cumulative paid Sol calls = 9,
- generic contract fix is provider-free GREEN,
- no further paid rerun is authorized automatically,
- Day9 is not authorized.

All original architecture prohibitions remain active.

### Expected next phase after supervisor review

No automatic next phase is authorized.

The authorized post-fix re-measurement has been consumed and returned VALID RED.
No automatic next phase remains. Supervisor must review the receipt and the generic
post-RED contract fix before any further paid measurement or Day9 authorization.

### New developer first actions

1. Read the seven authority sources at the top of this document in order.
2. Verify branch is `feat/ask-v2-mvp`.
3. Re-fetch exact HEAD before editing; documentation may be ahead of product behavior.
4. Verify latest product behavior SHA remains `810fa70ded3bca53542316d32a5497302b4eb9c7`
   unless supervisor explicitly authorizes later product work.
5. Do NOT rerun paid tests merely to “check things”.
6. Treat D8-C as deterministic GREEN but live-certification STOP.
7. Preserve the authority boundaries; do not reopen sealed Day7 or start Day9 without new authority.
