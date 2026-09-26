# DIMA — DAY 8 ROOT-CAUSE ARCHITECTURE AND PRIMITIVE INVENTORY

**Date:** 2026-09-23  
**Ticket:** `P11 — DAY8 ROOT-CAUSE BRANCH`  
**Phase:** **D8-A GREEN / D8-B PRECONDITIONS AUTHORIZED**  
**Product implementation:** **D8-A1 + D8-A2 GREEN; ROOT_CAUSE EXECUTION REMAINS DISABLED**

Authority:
1. `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` — P11
2. `DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md` — R13
3. `DIMA_DAY7_FINAL_CLOSURE_AND_DAY8_HANDOFF.md`
4. this receipt

---

## 1. DAY8 PURPOSE

Day8 does **not** build a generic “cause generator”.

Its purpose is:

```text
investigate candidate explanations
WITHOUT selling correlation as causation
```

Canonical output:

```text
HypothesisLedger
+ evidence_for / evidence_against
+ epistemic finding label
```

Hard invariant:

```text
ASSOCIATION != CAUSATION
```

Canonical labels:

```text
OBSERVATION
COMPARISON
ASSOCIATION
CONTRIBUTION
CANDIDATE_CAUSE
CONFIRMED_CAUSE
```

`CONFIRMED_CAUSE` is exceptional. It is not a normal LLM conclusion and must remain
unavailable unless a deterministic/mechanistic confirmation contract is proven.

---

## 2. WHAT DAY7 ALREADY PROVIDES

Day8 must build **on** these existing authorities, not replace them.

### Evidence authority

Current `EvidenceArtifact` already carries:
- artifact/task identity,
- obligation refs,
- QueryContract lineage,
- verified bit,
- bounded payload,
- limitations,
- execution vs derived source kind,
- parent evidence/query refs,
- typed derived transformation.

Derived Evidence already preserves parent QueryContract lineage.

### Research-task provenance

Current `ResearchTask` already distinguishes:
- `USER_SEED`,
- `AGENT_DERIVED`,
- parent task,
- parent obligation,
- trigger evidence,
- branch depth,
- lifecycle state.

An AGENT_DERIVED task cannot exist without parent task + obligation + evidence provenance.

### Result-aware state

`ResearchStateView` already separates:

```text
accumulated state
!=
latest evidence delta
```

The latest delta carries availability, inspection state, verification, task/obligation refs,
QueryContract refs, row/query counts, limitations and a bounded payload.

`UNAVAILABLE` is not silently converted to “no evidence” or semantic gap.

### Deterministic derived analytics

`DerivedEvidenceService` already supports zero-query transforms over VERIFIED parent
Evidence:

```text
TREND
CONTRIBUTION
PEER_COMPARE
```

Important existing claims:
- trend R² is explicitly not significance/confidence,
- contribution is explicitly non-causal observed-change decomposition,
- peer comparison is explicitly descriptive/non-causal,
- peer membership and time ordering must be upstream governed.

### Cross-domain safety

`CrossDomainJoinGate` already requires:
- explicit Wren path,
- safe many-to-one cardinality,
- measured healthy fanout,
- bounded path depth,
- governed grain,
- required aggregation,
- time compatibility,
- unit compatibility.

Physical FK/name similarity is not relationship authority.

### Current ROOT_CAUSE boundary

`ManagerCapabilityRegistry` recognizes ROOT_CAUSE as a Research capability but keeps:

```text
executable = false
```

`CapabilityBindingGate` therefore fails closed before direct execution.

This is the correct Day8 starting point. Do not make ROOT_CAUSE executable until the
epistemic ledger/gates below exist.

---

## 3. CURRENT MODEL GAP

Existing models are intentionally insufficient for Day8:

`Finding` currently has:
```text
finding_id
question_id
statement
evidence_artifact_refs
```

`Hypothesis` currently has:
```text
hypothesis_id
question_id
statement
evidence_for_refs
evidence_against_refs
```

Missing authority:
- parent USER_MUST / ROOT_CAUSE obligation,
- hypothesis lifecycle status,
- typed epistemic label,
- limitations,
- provenance,
- next-test linkage,
- deterministic evidence validation,
- causal-confirmation gate.

Therefore the current shells MUST NOT be treated as Day8 completion truth.

---

## 4. PROPOSED CANONICAL DAY8 DATA MODEL

Do not implement until reviewed.

### HypothesisStatus

```text
OPEN
SUPPORTED
REFUTED
INCONCLUSIVE
```

### EpistemicLabel

```text
OBSERVATION
COMPARISON
ASSOCIATION
CONTRIBUTION
CANDIDATE_CAUSE
CONFIRMED_CAUSE
```

### HypothesisEntry

Review-corrected minimum contract:

```text
hypothesis_id
parent_obligation_id

statement
semantic_handle_refs

trigger_evidence_refs

status
epistemic_label

evidence_links[]
  evidence_ref
  relation = SUPPORTS | CONTRADICTS

next_test_task_refs

limitations
provenance
```

`parent_obligation_id` is the mandatory root authority. A ROOT_CAUSE obligation is an
orchestration owner and therefore does not require a synthetic parent ResearchTask.

`trigger_evidence_refs` records why cognition considered the hypothesis. Trigger Evidence is
NOT automatically supporting Evidence and MUST NOT be silently copied into SUPPORTS links.

`statement` is human-readable cognition, not semantic authority.
`semantic_handle_refs` must resolve through the existing governed SemanticHandle registry.
`next_test_task_refs` must resolve through the existing ResearchTask registry; the Manager
cannot mint task IDs.

### HypothesisLedger

One run-scoped ledger per accepted root-cause research authority.

Responsibilities:
- register hypothesis,
- validate and preserve trigger Evidence provenance,
- attach typed `SUPPORTS` / `CONTRADICTS` Evidence links,
- link already-registered governed next-test ResearchTasks,
- apply only structurally admissible status transitions,
- expose OPEN / accounted hypotheses,
- preserve provenance.

It does **not**:
- execute DB or generate SQL,
- mint SemanticHandles, ResearchTask IDs or Evidence IDs,
- decide Wren paths / relationships,
- change USER_MUST,
- manufacture evidence,
- run causal inference,
- deterministically decide what Evidence semantically entails.

---

## 5. DETERMINISTIC EPISTEMIC GATE

Day8 needs one explicit owner for:

```text
what is the strongest CLASS OF CLAIM this governed Evidence is admissible for?
```

Proposed owner:
`EpistemicLabelGate` / equivalent deterministic service.

Critical split:

```text
Manager cognition
= proposes that Evidence supports/contradicts a hypothesis

Deterministic epistemic layer
= validates admissibility, provenance, lineage and claim-class ceiling
```

The deterministic layer does NOT perform semantic entailment and must not use thresholds
such as correlation > X, contribution > Y or score > Z to decide causal truth.

Minimum rules:

### OBSERVATION
May be emitted from verified direct Evidence describing a measured state.

### COMPARISON
Requires governed comparison/peer Evidence and its stated baseline.

### ASSOCIATION
May be emitted from governed relationship Evidence.
It **never** upgrades itself to cause.

### CONTRIBUTION
Requires governed decomposition Evidence.
It means “observed change decomposition”, not cause.

### CANDIDATE_CAUSE
Requires:
- a parent ROOT_CAUSE obligation,
- a typed hypothesis,
- at least one relevant verified supporting Evidence reference,
- explicit limitations,
- no semantic laundering from prioritization score.

It remains a candidate even if strongly supported.

### CONFIRMED_CAUSE

Current Day8 policy:

```text
DENY
reason = CAUSAL_NOT_IDENTIFIED
```

There is currently no proven intervention, experiment-assignment, causal-graph identification,
instrumental-variable or validated causal-model contract in this repo. Do not build a large
placeholder CausalConfirmationGate. A small explicit typed deny boundary is the correct
implementation.

LLM confidence, correlation strength, rank, R², contribution share, anomaly score or
interestingness are **never sufficient**.

---

## 6. HYPOTHESIS LIFECYCLE

ROOT_CAUSE is an orchestration umbrella, NOT a ResearchTaskKind and NOT an alias for QUERY.

```text
Accepted ROOT_CAUSE obligation
        ↓
verified trigger Evidence / current ResearchState
        ↓
Manager proposes candidate hypothesis
        ↓
semantic/provenance validation
        ↓
HypothesisLedger OPEN entry
        ↓
bounded next-test proposal
        ↓
existing governed ResearchTask family
QUERY / BREAKDOWN / COMPARE / RELATIONSHIP / CONTRIBUTION / PEER_COMPARE / later TREND
        ↓
new VERIFIED EvidenceArtifact
        ↓
Manager proposes SUPPORTS / CONTRADICTS relation
        ↓
ledger structural admission gate
        ↓
status proposal
        ↓
EpistemicLabelGate
        ↓
Evidence-linked Finding
```

Trigger Evidence explains why the hypothesis exists; it does not automatically count as
SUPPORTS. Candidate generation and evidence interpretation are cognition. Evidence validity,
task identity, semantic truth, lineage and epistemic claim ceilings remain deterministic.

Do NOT add `ResearchTaskKind.ROOT_CAUSE`. Do NOT map ROOT_CAUSE → QUERY.

Candidate root-cause orchestration may use:
- QUERY / BREAKDOWN / COMPARE,
- RELATIONSHIP,
- governed derived CONTRIBUTION,
- governed PEER_COMPARE,
- later governed TREND,

but only through existing typed task/tool/execution boundaries.

---

## 7. LEGACY PRIMITIVE INVENTORY

Classification vocabulary:

```text
PURE_EVIDENCE_TRANSFORM
GOVERNED_QUERY_REUSABLE
PRIORITIZATION_ONLY
LEGACY_QUERY_AUTHORITY_REJECT
CAUSAL_OVERREACH_RISK
PRIMITIVE_GAP
```

### app.kok_neden

| Primitive | Classification | Day8 disposition |
|---|---|---|
| `ayristir(...)` | PURE_EVIDENCE_TRANSFORM + CAUSAL_OVERREACH_RISK | Math can be reused only over already-governed target/peer/component Evidence. The legacy `suclu` naming/selection is not causal truth. |
| `bilesenler(...)` | PRIMITIVE_GAP / metadata utility | Useful formula-component idea, but current SQL-expression/string parsing is not a new V2 semantic authority. Day8 needs governed formula/decomposition provenance before adoption. |
| `arastir(...)` | LEGACY_QUERY_AUTHORITY_REJECT + CAUSAL_OVERREACH_RISK | Chooses dimensions, rewrites CubeQuery and executes follow-ups; cannot own V2 root-cause execution. |
| `derinles(...)` | LEGACY_QUERY_AUTHORITY_REJECT + PRIORITIZATION_ONLY | Candidate scanning and “most separating” selection may inspire scheduling, but execution must remain governed. |
| `kosucu(...)` / `cevap_verisi(...)` | LEGACY_QUERY_AUTHORITY_REJECT | Legacy execution/presentation path; do not route Day8 through it. |

Key lesson: a decomposition that “explains most variance/difference” is not automatically
a cause.

### app.contribution

| Primitive | Classification | Day8 disposition |
|---|---|---|
| `contributions(...)` | PURE_EVIDENCE_TRANSFORM | Already reused by V2 DerivedEvidence. Keep explicit non-causal semantics. |
| `pvm(...)` | PURE_EVIDENCE_TRANSFORM | Candidate for later governed derived Evidence when value/volume pair provenance is explicit. |
| `pvm_pairs(...)` | metadata utility | Can read explicit governed metadata; absence must not be guessed. |
| `rank_dimensions(...)` | PRIORITIZATION_ONLY | Interesting/explanatory ranking may schedule investigation; cannot change epistemic truth. |
| `toplanabilirlik(...)` | metadata utility with legacy heuristic risk | Explicit metadata is reusable; name-pattern fallback must not become V2 authority. |
| `decompose(...)`, `pvm_report(...)` | LEGACY_QUERY_AUTHORITY_REJECT | Legacy report/CubeQuery mutation path. |
| `_akran_kiyasi(...)`, `arastir(...)` | LEGACY_QUERY_AUTHORITY_REJECT + CAUSAL_OVERREACH_RISK | Executes/scans and uses “driver/explanation” semantics outside current V2 authority. |

### app.drill

| Primitive | Classification | Day8 disposition |
|---|---|---|
| `flag_outliers(...)` | PURE_EVIDENCE_TRANSFORM | May create OBSERVATION/candidate-priority signal over governed rows. Outlier != cause. |
| `available_dimensions(...)` | PRIORITIZATION_ONLY | Cost/fanout-based scheduling candidate; not explanatory truth. |
| `related_cubes(...)` | LEGACY_QUERY_AUTHORITY_REJECT | Shared dimension-name matching is weaker than current Wren relationship authority. |
| `expand_cube_query(...)`, `select_cube_query(...)`, `jump_to_related_cube(...)` | LEGACY_QUERY_AUTHORITY_REJECT | Query-shape utilities may only survive behind a governed compiler/adapter, never as Manager authority. |

### app.ilkeller — peer compare

| Primitive | Classification | Day8 disposition |
|---|---|---|
| `hesapla(...)` | PURE_EVIDENCE_TRANSFORM | Already reused in V2 DerivedEvidence; descriptive comparison only. |
| `bagla(...)` | PRIORITIZATION_ONLY | Target selection is cognition/policy; cannot silently choose semantic authority. |

### app.yoy

| Primitive | Classification | Day8 disposition |
|---|---|---|
| `_merge(...)` | PURE_EVIDENCE_TRANSFORM candidate | Only reusable when current/reference periods and alignment are already governed. Internal period-shift assumptions must not become temporal authority. |
| `compute(...)` | LEGACY_QUERY_AUTHORITY_REJECT | Mutates query/time filters and executes DB; V2 typed temporal + official Wren boundary remain owners. |

---

## 8. ALREADY-ADOPTED PURE PRIMITIVES

Day7 already proved the correct reuse pattern:

```text
legacy pure math
        ↓
typed V2 args
        ↓
VERIFIED parent Evidence
        ↓
strict preconditions
        ↓
DerivedEvidenceArtifact
        ↓
preserved QueryContract lineage
```

Current examples:
- `stats.trend`,
- `contribution.contributions`,
- `ilkeller.hesapla`.

Day8 should follow the same pattern for any additional primitive.
Do not import legacy orchestration merely because its inner mathematics is useful.

---

## 9. PRIMITIVE GAPS THAT DAY8 ACTUALLY OWNS

Day8 currently lacks:

1. canonical `HypothesisLedger`,
2. typed `HypothesisStatus`,
3. typed `EpistemicLabel`,
4. evidence-for/evidence-against validation,
5. parent ROOT_CAUSE obligation linkage,
6. next-test task linkage,
7. deterministic epistemic-label gate,
8. a default-deny `CONFIRMED_CAUSE` gate,
9. Evidence-linked finding construction,
10. governed ROOT_CAUSE orchestration over existing ResearchTask/tool boundaries.

It does **not** lack:
- another SQL engine,
- another semantic resolver,
- another relationship planner,
- another evidence store,
- another generic agent runtime.

---

## 10. TARGETED METABASE DAY8 REFERENCE

Current inspected upstream:

```text
metabase/metabase
cdc7f386afa705593e44fac6e627d386b780a3d7
```

Previously pinned:

```text
6ec07f75184dd7f06d84c551d57c58687cf4b859
```

Relevant Day8 files changed between these inspected points: `0`.
No source copying and no Metabase runtime dependency.

Harvested Day8 patterns:
- candidate generation is structural planning, not causal truth,
- interestingness is post-result prioritization, not Evidence strength,
- only applicable/hydrated candidates enter a plan,
- model-facing IDs must be server-owned governed IDs,
- result/Evidence and priority score remain separate records,
- composite evidence must preserve one compatible governed access context.

### Interestingness != truth

Metabase reference lesson for Day8:

```text
interestingness / ranking / salience
!=
truth
!=
causal confirmation
```

Use prioritization only to decide what to inspect/test next.

Never map:
- anomaly score,
- dimension rank,
- contribution magnitude,
- correlation strength,
- model confidence

directly to `CANDIDATE_CAUSE` or `CONFIRMED_CAUSE`.

No new broad Metabase audit is required for Day8.
No Metabase runtime dependency is introduced.

---

## 11. AUTHORIZED PROVIDER-FREE IMPLEMENTATION SLICES

### D8-A1

```text
typed epistemic models
+ HypothesisLedger
+ Evidence-link structural validation
```

Preferred file scope:
- `backend/app/v2/models.py`
- one focused owner module: `backend/app/v2/epistemics.py`
- `backend/tests/test_v2_day8_hypothesis_ledger.py`

D8-A1 must validate current EvidenceStore, current SemanticHandleRegistry and current
ResearchTaskRegistry identities. It creates none of those authorities.

### D8-A2

```text
EpistemicLabelGate
+ minimal Evidence-linked finding model/builder
+ CONFIRMED_CAUSE typed hard deny
```

Both slices are provider-free:
- no LLM,
- no DB query,
- no paid test,
- no ROOT_CAUSE execution,
- no legacy query path.

Forbidden during D8-A:
`manager_loop.py`, `manager_policy.py`, `manager_preacceptance.py`,
`research_tools.py`, ResearchTask execution mapping, semantic linker/retriever,
temporal modules, relationship/cross-domain modules, WrenService and /api/ask-v2 front door.

Minimum provider-free attacks:

```text
finding without Evidence                    -> reject
unknown/unverified Evidence ref             -> reject
ASSOCIATION -> CONFIRMED_CAUSE              -> reject
CONTRIBUTION -> CONFIRMED_CAUSE             -> reject
interestingness score -> causal truth       -> reject
supporting/refuting evidence lineage loss   -> reject
ROOT_CAUSE entry without parent obligation  -> reject
CANDIDATE_CAUSE without limitation/proof    -> reject
CONFIRMED_CAUSE without confirmation gate   -> reject
```

Only after D8-A is green should a bounded Manager candidate-hypothesis proposal layer be
designed.

---

## 12. DAY8 EXIT TARGETS — FOR LATER

Roadmap hard exits remain:

```text
unsupported_causality_rate       = 0
hypothesis evidence linkage      = 100%
finding without evidence         = 0
candidate-vs-confirmed labeling  = 100%
```

These cannot be solved by prompt wording alone.

---

## 13. STATUS TRANSITION ADMISSION RULES

Status is orthogonal to epistemic label. Do not vote-count Evidence.

```text
OPEN
= default

SUPPORTED
= proposed transition requires >=1 valid SUPPORTS link

REFUTED
= proposed transition requires >=1 valid CONTRADICTS link

INCONCLUSIVE
= explicit limitation + attempted/observed evidence state
```

These are structural admission rules, not evidence-weighting science.

## 14. REVIEW / IMPLEMENTATION GATE

This receipt is now reconciled with the Day8 supervisor review.

Authorized now:
```text
D8-A1
→ provider-free green
→ D8-A2
→ provider-free green
→ living status + Harvest
→ STOP / supervisor review
```

Not authorized:
- D8-B Manager hypothesis proposal,
- D8-C next-test orchestration wiring,
- ROOT_CAUSE executable=true,
- live Sol / paid tests,
- Day9.


---

## 15. CURRENT SUPERVISOR OVERRIDE — D8-B PRECONDITIONS

Current proof:

```text
D8-A1 HypothesisLedger       GREEN
D8-A2 EpistemicLabelGate     GREEN
focused run                  35880777420 = GREEN
paid calls                   0
ROOT_CAUSE executable        false
```

Before D8-B cognition wiring, close these provider-free seams:

1. a mutable hypothesis ledger may exist only while its ROOT_CAUSE USER_MUST is
   `ACCEPTED | READY | IN_PROGRESS`; every proposed/clarification/blocked/limited/
   unsupported/superseded/verified terminal state rejects new epistemic state,
2. current Evidence membership is a live read-only view of the same Day7 governed run;
   do not freeze refs at ledger construction and do not create another EvidenceStore,
3. D8-B cognition proposals may reference only current + VERIFIED + inspected Evidence.

After those are GREEN, D8-B may add one focused proposal-boundary owner. D8-C remains
unauthorized in this development burst.


---

## 16. D8-B GREEN — SUPERVISOR STOP

Current implementation receipt:

```text
Day8 product behavior SHA    e6e46c04ebabdac804545855d7fbbcf90c1b1b90
D8-A1                        GREEN
D8-A2                        GREEN
structural seams             GREEN
D8-B                         GREEN
focused run                  35884577376 = GREEN
paid calls                   0
DB queries                   0
ROOT_CAUSE executable        false
D8-C                         NOT STARTED
```

Delivered before D8-B:
- active ROOT_CAUSE status gate,
- live read-only current-run Evidence view,
- inspected-Evidence admission.

D8-B adds only:
- `HypothesisProposal`,
- `HypothesisEvidenceRelationProposal`,
- `HypothesisProposalBoundary`.

No Manager loop, ResearchTask execution mapping, semantic linker, cross-domain, temporal,
WrenService or /api/ask-v2 integration was opened.

This document now stops at the supervisor review boundary.
D8-C capability-mode design and next-test orchestration are explicitly deferred.


---

## 14. SUPERVISED POST-FIX LIVE RE-MEASUREMENT — VALID RED

This section supersedes earlier design-only / D8-C-deferred wording where they conflict.

Current engineering state:

```text
D8-A1 / D8-A2 / D8-B           GREEN
D8-C deterministic             GREEN
D8-C real-Wren                 GREEN
D8-C live Sol                  OPEN / VALID RED
DAY8 / P11                     NOT SEALED
DAY9                           NOT STARTED
```

Authorized live re-measurement:
`35898027005`.

Identity receipt:

```text
product behavior SHA   3091651aea93e42e00521654af8d5dc2c51dc9c3
run head               d5ac338ac5b242e86c77469075e6c3e8b405a72c
scenario hash          8379daa7fc70a678514b7f87dcb41fcdfec4d317d8ded4cc2712ee7cfb4c8d6a
harness blob           4ae479eb171eccb709eb326309734779533079ab
Manager                openai/gpt-5.6-sol
Manager calls          2
semantic calls         0
temporal calls         0
measurement            VALID RED
```

First incorrect transition:

```text
server-owned hypothesis identity
→ expected governed next-test proposal
→ resolve_semantics
```

The post-fix task-kind/provider surface was correct, but opaque Manager aliases still omitted
their governed semantic `target_kind`. The Manager therefore had the next-test shape contract
without the stable non-secret metadata needed to match an existing `h*` handle to that shape.

Final failure class:
`CONTRACT/ARCHITECTURE`.

Single owner:
Manager-safe projection of already-governed semantic-handle metadata.

Generic fix:
- opaque alias identity remains opaque,
- canonical semantic target remains private to `SemanticHandleRegistry`,
- `SEMANTIC_HANDLE_CATALOG` exposes only `target_kind`, provenance type, parent obligation and
  trigger-Evidence provenance,
- existing next-test contract consumes that metadata cognitively,
- semantic re-resolution is reserved for a materially missing concept grounded in inspected Evidence.

Latest product behavior SHA:
`810fa70ded3bca53542316d32a5497302b4eb9c7`.

Proof:
`35898621489 = GREEN` and affected Day7 `35898591894 = GREEN`.

No further paid re-measurement is authorized automatically.
