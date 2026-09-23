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
D8 structural seams                    GREEN
D8-B hypothesis proposal boundary      GREEN

latest Day8 product behavior SHA
e6e46c04ebabdac804545855d7fbbcf90c1b1b90

latest focused
35884577376 = GREEN

paid calls = 0
DB queries = 0
ROOT_CAUSE direct executable = false
ResearchTaskKind.ROOT_CAUSE = DOES NOT EXIST
ROOT_CAUSE → QUERY alias = DOES NOT EXIST
D8-C = AUTHORIZED / STARTING
```

Changed Day8 product files in this burst:
- `backend/app/v2/models.py`
- `backend/app/v2/epistemics.py`
- `backend/app/v2/hypothesis_proposals.py`

New sealed Day8 boundaries:
- mutable hypothesis state requires active ROOT_CAUSE USER_MUST:
  `ACCEPTED | READY | IN_PROGRESS`,
- current Evidence membership is a live read-only view of Day7 ManagerRuntime,
- newly committed same-run Evidence becomes visible without reconstructing HypothesisLedger,
- foreign-run/unverified Evidence remains inadmissible,
- cognition proposal Evidence must be current + VERIFIED + inspected,
- trigger Evidence is not automatically SUPPORTS Evidence,
- model cannot mint SemanticHandle, Evidence, ResearchTask or Hypothesis IDs,
- explicit SUPPORTS/CONTRADICTS relation proposal is structurally gated,
- priority/interestingness Evidence cannot become causal SUPPORTS truth,
- `CONFIRMED_CAUSE -> CAUSAL_NOT_IDENTIFIED`,
- ROOT_CAUSE remains orchestration umbrella; no `ResearchTaskKind.ROOT_CAUSE`, no QUERY alias.

## SUPERVISOR OVERRIDE — D8-C AUTHORIZED

The prior "STOP after D8-B / D8-C unauthorized" instruction is superseded.

D8-C is now authorized under the following unchanged hard boundaries:
- ROOT_CAUSE must remain an orchestration umbrella, never a direct query capability;
- no ResearchTaskKind.ROOT_CAUSE;
- no ROOT_CAUSE → QUERY alias;
- no new semantic owner, Evidence registry, scheduler, budget truth, SQL engine, or generic agent kernel;
- CONFIRMED_CAUSE remains hard-denied;
- provider-free orchestration proof precedes one deterministic real-Wren sentinel;
- Manager-loop wiring happens only after those lower seams are GREEN;
- only then one live Sol sentinel is permitted under the paid-call ceiling.

Authorized implementation order:
1. characterize capability execution consumers;
2. introduce one execution-mode truth;
3. add deterministic ROOT_CAUSE bootstrap/applicability ownership;
4. add server-owned hypothesis next-test proposal admission;
5. reuse the sealed Day7 ResearchTask/fanout/registry/tool machinery;
6. provider-free GREEN;
7. one deterministic real-Wren sentinel;
8. then Manager-loop wiring;
9. then one live Sol sentinel;
10. update living status/Harvest and STOP for supervisor receipt.


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
`e6e46c04ebabdac804545855d7fbbcf90c1b1b90`.

Latest focused provider-free proof:
`35884577376 = GREEN`.

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

D8-C is authorized. The implementation may add orchestration semantics and the narrow
adapters needed to reuse Day7 governed tasks.

Still forbidden:
- `ROOT_CAUSE executable=true` as a direct-execution bool flip,
- `ResearchTaskKind.ROOT_CAUSE`,
- ROOT_CAUSE → QUERY alias,
- new semantic or Evidence authority,
- new scheduler/budget/execution engine,
- raw-language downstream reparsing,
- CONFIRMED_CAUSE enablement,
- Day9.

Manager-loop wiring, real-Wren sentinel and one live Sol sentinel are authorized only in the
ordered gates above, not as shortcuts around provider-free lower-layer proof.

### Expected next phase after supervisor review

The current design direction for D8-C is documented, but is NOT authorization.

Likely sequence after review:

```text
capability-mode design receipt
(DIRECT / ORCHESTRATED / DEFERRED / PRESENTATION or smaller equivalent)
        ↓
ROOT_CAUSE = ORCHESTRATED
        ↓
reuse DerivedResearchTaskProposal
+ ResearchTaskService.materialize_derived
+ ResearchFanoutPolicy
        ↓
governed QUERY / BREAKDOWN / COMPARE /
RELATIONSHIP / CONTRIBUTION / PEER_COMPARE next tests
        ↓
one provider-free real-Wren sentinel
        ↓
only then one live Sol sentinel <= 8 total paid calls
```

D8-C is now explicitly open; implement it only through the ordered gates and STOP conditions above.

### New developer first actions

1. Read the seven authority sources at the top of this document in order.
2. Verify branch is `feat/ask-v2-mvp`.
3. Re-fetch exact HEAD before editing; documentation may be ahead of product behavior.
4. Verify latest product behavior SHA remains `e6e46c04...` unless supervisor explicitly
   authorized later product work.
5. Do NOT rerun paid tests merely to “check things”.
6. Apply the current supervisor override: D8-C is authorized.
7. Preserve the file boundary and ordered proof gates; do not reopen sealed Day7.
