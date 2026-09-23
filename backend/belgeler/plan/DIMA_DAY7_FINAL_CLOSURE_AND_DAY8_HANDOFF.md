# DIMA — DAY 7 FINAL CLOSURE AND DAY 8 HANDOFF

**Date:** 2026-09-23  
**Branch:** `feat/ask-v2-mvp`  
**Day 7 product behavior SHA:** `ce82d48bb8ab127a2dd5f7a63ebb25604a6557a6`  
**Final Day7 authority-pointer baseline HEAD:** `d7568c51ccddaa25e06d25054b3b360222c9fe17`  
**Status:** **DAY7 / P10 = CLOSED / SEALED — ENGINEERING PHASE**  
**Closure diff audit:** `ce82d48... → d7568c...`, `backend/app/v2 changes = 0`

> This document is the single authoritative Day7 closure state.
> Historical Day7 urgent handoffs are retained for audit only and are superseded.

---

## 1. FINAL PRODUCT STATUS

```text
DAY7 / P10
= CLOSED / SEALED

RESULT-AWARE RESEARCH LOOP
= CLOSED FOR CURRENT GOVERNED SURFACE

PRODUCTION /ask-v2
= STILL OFF

DEV80
= NOT RUN

VALIDATION50
= NOT RUN

HIDDEN50
= NOT RUN
```

Day7 closure is an engineering-phase closure. It is **not** release certification.

Final Day7 correctness state:

```text
known hard invariant holes              = 0
unclassified Day7 LIVE RED              = 0
advertised executable dead ends         = 0
known cross-obligation authority leaks  = 0
unsafe semantic binding                 = 0
silent USER_MUST loss                   = 0
latest broad hard-safety regressions    = 0
```

---

## 2. SEALED DAY7 ARCHITECTURE

Canonical cognition/truth split:

```text
LLM / Manager             = bounded cognition + orchestration
Accepted authority        = immutable semantic authority
Semantic handles / gates  = canonical semantic truth
Planner / join gates      = analytical validity
Wren / DB                 = numeric truth
QueryContract / Evidence  = proof
Ledger / CompletionGate   = completion truth
```

Day7 Research loop:

```text
AcceptedResearchAuthority
→ bounded USER_MUST seed tasks
→ typed ResearchToolContract
→ governed execution
→ verified EvidenceArtifact
→ inspect
→ latest-result delta
→ evidence-grounded optional derived task
→ progress/budget/completion gates
→ terminal
```

Permanent boundaries:
- exactly one accepted semantic authority per turn,
- USER_MUST is immutable,
- AGENT_DERIVED work cannot replace a user obligation,
- post-acceptance raw prompt is not semantic authority,
- no raw SQL / direct DB authority for Manager,
- no unverified cross-domain path,
- no evidence-less official analytical claim,
- no causal claim from correlation alone.

---

## 3. PROVIDER TOPOLOGY

```text
RESEARCH_MANAGER     = openai/gpt-5.6-sol
SEMANTIC_LINKER      = openai/gpt-5.6-luna
TEMPORAL_NORMALIZER  = openai/gpt-5.6-sol
certification workers = 1
```

Provider/model identity does not appear as business-logic branching.

Execution substrate:

```text
semantic / analytical execution primary = Wren
official principal-aware boundary        = Dima WrenService path
Metabase runtime dependency              = NONE
```

---

## 4. FINAL MANAGER BUDGET

One canonical hard ceiling:

```text
max_total_manager_turns = 6

max_preacceptance_turns <= 2
max_research_manager_turns <= 6

preacceptance_turns + research_manager_turns <= 6
```

Phase counters remain observable but never expand the global allowance.

A seventh Manager cognition turn deterministically becomes:

```text
BUDGET_EXHAUSTED
```

Budget exhaustion cannot be rewritten into COMPLETED by a later `finish()`.

Other current Day7 bounds remain governed through the existing runtime/tool contracts,
including query/tool/branch-depth/fanout limits.

---

## 5. FINAL PROOF RECEIPTS

### Provider-free focused seal

```text
run 35872766887
SHA 85b52f596611020b075b0a100e395163b33087c2
RESULT = GREEN
```

This gate includes:
- Day7 compile,
- Research task lifecycle / registry / principal binding,
- directive and capability contracts,
- temporal USER_MUST owner isolation,
- obligation-local semantic recovery,
- relationship structured-action boundary,
- bounded fanout,
- seed lifecycle,
- Evidence/derived-evidence primitives,
- same-domain governed tools,
- CrossDomainJoinGate attacks,
- global six-turn Manager budget,
- result-aware adaptive loop,
- real Wren schema/grain proof,
- real Wren Day7 vertical,
- real two-Wren adaptive vertical,
- real governed relationship vertical,
- orchestration-ablation contract.

### Real Wren proof IDs

Historical real-Wren focused proof:
```text
35770029440
real Wren Research vertical = PASS
```

Final provider-free focused seal containing the completed Wren surfaces:
```text
35872766887 = GREEN
```

### Affected LIVE / cognition proofs

```text
35850683005
post-fix neutral-vs-causal cognition diagnostic
= VALID / 8 of 8 PASS

35853117857
insufficient-evidence affected LIVE
= VALID / 1 of 1 PASS

35857076622
adaptive-material affected LIVE
= VALID / 1 of 1 PASS
terminal = VERIFIED_COMPLETE
hard safety = 0
```

### Historical frozen13 receipt — DO NOT RERUN

```text
35855765109
measurement = VALID
evaluable   = 13 / 13
behavior    = 11 / 13
hard safety = 0
```

The two non-pass interpretations are already classified:
- `breakdown-region` → **Day9 PRESENTATION/TABLE debt**, not a Day7 analytical defect.
- `adaptive-material` → Day7 phase/action-surface contract defect, generically fixed;
  affected LIVE `35857076622` passed.

No second frozen13 is authorized.

---

## 6. FINAL DAY7 MICRO-ABLATION

### Zero-cost dry-run

```text
run                         35871834654 = SUCCESS
selected cases              2
arms                        2
maximum loop records        4
Manager hard turn cap       6
provider requests           0
model-call budget           16
```

### One-time paid measurement

```text
run                         35873755069 = SUCCESS
measurement_valid           true
selected/evaluable          2 / 2
completed records           4
shared accepted authority   verified
manager                     openai/gpt-5.6-sol
linker calls                0
temporal calls              0
total Manager model calls   16 / 16
service queries             3
eval budget exhausted       true
hard safety failures        0
```

Observed directional data:

```text
adaptive-material:
  FREE_COGNITION          quality=true  calls=10  queries=1
  GOVERNED_ORCHESTRATION  quality=true  calls=4   queries=1

stable-no-extra-branch:
  FREE_COGNITION          quality=true  calls=2   queries=1
  GOVERNED_ORCHESTRATION  censored by global eval budget before cognition
```

### Decision

```text
DAY7 MICRO-ABLATION
= INCONCLUSIVE

BROADER FREE vs GOVERNED ABLATION
= DEFER TO DAY11
```

Reason: the sequential shared 16-call evaluation budget censored the final governed arm.
That is an evaluation-budget outcome, not a product-quality failure.

No product architecture is changed from this one micro measurement.
No retry, no 20/30/50/80-call expansion, and no second Day7 ablation.

Day11 must use symmetric/order-independent comparative budget allocation before drawing
architecture conclusions.

---

## 7. SEALED DAY7 INVARIANTS

The following remain binding:

```text
exactly-one accepted semantic authority
rejected semantic attempt does not leak fields
raw user prompt is not downstream semantic authority
USER_MUST != ResearchDirective != AGENT_DERIVED
evidence inspection is distinct from evidence existence
latest result delta != accumulated Research state
retrieval/discovery != semantic truth
capability advertisement != authorization
no-progress/repetition is bounded
task execution identity is idempotent
cancelled work cannot resurrect
cross-domain execution requires governed path/grain/cardinality/time/unit proof
interestingness/prioritization != truth
association != causation
```

---

## 8. TEST-ECONOMY INVARIANTS

Permanent progressive widening:

```text
provider-free local / contract / metamorphic
→ one LIVE sentinel
→ affected pair
→ micro canary / micro ablation
→ milestone corpus
→ certification corpus after freeze
```

Harvested permanent rules:
- **H-053:** evaluation scope must be proportional to the uncertainty.
- **H-054:** paid evaluation predeclares and enforces a model-call budget before provider use.
- **H-055:** broad/certification corpora are milestone resources, not debugging tools.
- **H-056:** comparative A/B budget allocation must not censor one arm by execution order.

Paid workflows are manual-only, explicitly scoped and budget guarded.
Blank input cannot silently mean “run all”.

After the one-time Day7 micro-ablation:

```text
NO MORE PAID DAY7 EVALUATION
```

unless an independently discovered P0 defect requires a tiny affected-family probe.

---

## 9. METABASE REFERENCE STATUS

Pinned mature-system reference:

```text
metabase/metabase
6ec07f75184dd7f06d84c551d57c58687cf4b859
```

Latest upstream inspected:

```text
d994a365f720b39ca3a3543f602b772e6b497180
```

The inspected upstream delta did not materially change relevant metabot/search/agent/
query-plan/queue/permissions/persistence areas, so the current harvested lessons remain valid.

Transferable invariants:
- retrieval hit != current truth,
- server-owned scope != semantic authority,
- current permission/entity hydration before use,
- capability advertisement != authorization,
- at-least-once work requires idempotency,
- cancelled work cannot resurrect,
- latest result delta != accumulated state,
- fanout is bounded,
- interestingness != truth.

No Metabase runtime dependency and no source copying.

---

## 10. ROADMAP DEBTS CARRIED FORWARD

```text
TABLE / PRESENTATION
→ Day9

ROOT_CAUSE direct execution
→ Day8

TREND direct Manager execution
→ governed ordered-series execution surface still incomplete

CONTRIBUTION executable Research path
→ future governed integration

PEER_COMPARE executable Research path
→ governed peer-universe contract required

broad FREE vs GOVERNED ablation
→ Day11

vector / BM25 / RRF retrieval
→ BENCHMARK_REQUIRED

full ExecutionAccessFingerprint
→ Day12–14

durable replay
→ Day14

front-door /ask-v2 ownership
→ Day10
```

These are not Day7 reopening items.

---

## 11. DAY8 EXACT ENTRY POINT

Canonical next ticket:

```text
P11 — DAY8 ROOT-CAUSE BRANCH
```

Purpose:

```text
investigate candidate explanations
WITHOUT selling correlation as causation
```

Required core output:

```text
HypothesisLedger
+ evidence_for / evidence_against
+ epistemic finding label
```

Canonical epistemic labels:

```text
OBSERVATION
COMPARISON
ASSOCIATION
CONTRIBUTION
CANDIDATE_CAUSE
CONFIRMED_CAUSE
```

Hard invariant:

```text
ASSOCIATION != CAUSATION
```

`CONFIRMED_CAUSE` is exceptional and requires unusually strong deterministic/mechanistic
evidence; it is not a normal LLM conclusion.

### First Day8 block

Provider-free design/inventory only.

Read/inspect:
- roadmap P11,
- architecture report R13,
- current `EvidenceArtifact`,
- `UserObligationLedger`,
- `ResearchTask`,
- `ResearchStateView`,
- `DerivedEvidenceService`,
- governed cross-domain Evidence,
- current deferred ROOT_CAUSE boundary,
- legacy `kok_neden`, `contribution`, `drill`, peer compare, `yoy`.

No Day8 product implementation is authorized until the architecture + primitive inventory
receipt is complete and reviewed.

---

## 12. FINAL SEAL

```text
DAY7 / P10
= CLOSED / SEALED

RESULT-AWARE RESEARCH LOOP
= CLOSED FOR CURRENT GOVERNED SURFACE

PRODUCTION /ask-v2
= OFF

DEV80 / VALIDATION50 / HIDDEN50
= NOT RUN
```
