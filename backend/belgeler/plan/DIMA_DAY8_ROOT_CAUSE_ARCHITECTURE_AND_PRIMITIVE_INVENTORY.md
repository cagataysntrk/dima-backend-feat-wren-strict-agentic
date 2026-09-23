# DIMA — DAY 8 ROOT-CAUSE ARCHITECTURE AND PRIMITIVE INVENTORY

**Date:** 2026-09-23  
**Ticket:** `P11 — DAY8 ROOT-CAUSE BRANCH`  
**Phase:** **PROVIDER-FREE DESIGN / INVENTORY ONLY**  
**Product implementation:** **NOT AUTHORIZED BY THIS DOCUMENT**

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

Proposed minimum contract:

```text
hypothesis_id
parent_obligation_id
parent_task_id

statement
semantic_handle_refs

status
epistemic_label

evidence_for_refs
evidence_against_refs

next_test_task_refs

limitations
provenance
```

`statement` is human-readable presentation, not semantic authority.
Canonical semantic references must come from governed handles/provenance.

### HypothesisLedger

One ledger per accepted root-cause research authority.

Responsibilities:
- create candidate entries,
- attach supporting evidence,
- attach opposing evidence,
- attach governed next-test tasks,
- transition status,
- expose accounted/open hypotheses,
- preserve provenance.

It does **not**:
- execute SQL,
- mint canonical semantic IDs,
- decide Wren paths,
- change USER_MUST,
- manufacture evidence,
- independently assert causality.

---

## 5. DETERMINISTIC EPISTEMIC GATE

Day8 needs one explicit owner for:

```text
what may this Evidence justify us saying?
```

Proposed owner:
`EpistemicLabelGate` / equivalent deterministic service.

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

Default Day8 policy:

```text
DENY
```

until a separate `CausalConfirmationGate` has a proven mechanistic/interventional
evidence contract.

LLM confidence, correlation strength, rank, R², contribution share, anomaly score or
interestingness are **never sufficient**.

---

## 6. HYPOTHESIS LIFECYCLE

Proposed bounded flow:

```text
Accepted ROOT_CAUSE obligation
        ↓
verified parent Evidence / current ResearchState
        ↓
Manager proposes candidate hypothesis
        ↓
semantic/provenance validation
        ↓
HypothesisLedger OPEN entry
        ↓
bounded next-test proposal
        ↓
existing governed ResearchTask / tool path
        ↓
new verified EvidenceArtifact
        ↓
attach evidence_for / evidence_against
        ↓
deterministic status + epistemic-label gate
        ↓
SUPPORTED / REFUTED / INCONCLUSIVE
        ↓
Evidence-linked Finding
```

Candidate generation is cognition.
Evidence validity, task authority, semantic truth and epistemic label boundaries are not.

A “next test” should normally compile to existing governed task families rather than create
a second query authority.

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

## 10. INTERESTINGNESS != TRUTH

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

## 11. FIRST IMPLEMENTATION SLICE — PROPOSED, NOT YET AUTHORIZED

After review, the smallest correct provider-free vertical should be:

```text
D8-A
typed epistemic enums/models
→ HypothesisLedger deterministic service
→ EvidenceStore-backed evidence attachment validation
→ EpistemicLabelGate
→ default-deny CONFIRMED_CAUSE
→ provider-free unit/metamorphic attacks
```

No LLM call.
No DB query.
No new ROOT_CAUSE execution.
No legacy query path.

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

## 13. STOP / REVIEW POINT

This receipt completes the required **provider-free Day8 architecture + legacy primitive
inventory**.

No Day8 product code has been added by this phase.

Next action requires review of this architecture before implementation of D8-A.
