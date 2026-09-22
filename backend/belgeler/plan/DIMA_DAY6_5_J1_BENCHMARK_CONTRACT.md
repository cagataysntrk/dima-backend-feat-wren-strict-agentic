# DIMA DAY 6.5 — J1S / J1T BENCHMARK CONTRACT

**Status:** PRE-RUN CONTRACT CORRECTED / LAB-EVAL ONLY  
**Freeze:** `d65-j1-freeze-v2`  
**Amendment reason:** `PRE_RESULT_CHALLENGER_ROLE_CORRECTION`  
**Product semantic/temporal/authority code:** NO-TOUCH

## 1. Purpose

Measure bounded decision-model fitness without changing Dima's authority architecture or tuning
product code to named benchmark cases.

Primary full peer set:

```text
A = google/gemini-2.5-flash-lite
    current cheap incumbent

B = typesafe/jev-1.13
    specialized bounded-decision challenger

C = openai/gpt-5.6-luna
    cost/high-volume general-model peer
```

Non-peer roles:

```text
openai/gpt-5.6-sol
  role = REFERENCE_CEILING
  only the pre-frozen small stratified subset may be used
  never enters cheap-tier latency/cost winner ranking

openai/gpt-5.6-terra
  role = CONDITIONAL_SECOND_STAGE
  run only after explicit consultation if the primary cheap tier is inconclusive
  or no primary model clears the capability floor
```

Moving alias `~typesafe/jev-latest` is forbidden.

Jev uses the native OpenRouter Decisions API. It is never routed through Dima's generic chat /
`structured_json()` transport.

## 2. Frozen architecture rule

J1 does not confer authority.

```text
decision model = bounded proposal only
SemanticBindingGate = semantic authority
TemporalBindingEngine = deterministic date arithmetic
DB/Wren = numeric truth
```

No model may mint `sem_*`, escape the supplied candidate/ontology boundary, write SQL, see raw
DB truth, bypass tenant/context boundaries, or silently cascade to another model.

## 3. Reasoning fairness

Primary bounded-decision peers are compared without a model-specific reasoning advantage.

```text
Gemini Flash-Lite  reasoning.enabled=false
Jev 1.13           native Decisions transport; no chat reasoning layer
GPT-5.6 Luna       reasoning.enabled=false
```

If the frozen Sol reference-ceiling subset is run, it is explicitly tagged
`REFERENCE_CEILING`; its reasoning policy is recorded separately and its latency/cost cannot be
mixed into primary peer ranking. Terra, if explicitly opened, uses bounded-decision reasoning
disabled and is reported as a second-stage challenger.

Every live receipt records the exact reasoning policy used.

## 4. J1S — bounded semantic candidate decision

Input:

```text
exact user surface
+ frozen CandidateSet cards
→ supplied candidate_id | ABSTAIN
```

Candidate-card fields remain:

```text
candidate_id
target_kind
label
verified_aliases
cube_labels
```

No canonical DB identifier is supplied.

### Production-fidelity scoring split

Production `BoundedSemanticLinker` does not call the model for a unique verified exact match.
Therefore exact fast-bind controls remain in the frozen corpus but are not allowed to inflate the
model winner score.

Report separately:

```text
all_cases_accuracy                     diagnostic only
deterministic_bypass_controls          exact verified fast-bind controls
model_needed_accuracy                  only cases that genuinely need LINKER cognition
model_needed_turkish_accuracy
ambiguity_abstain_accuracy
no_match_abstain_accuracy
retrieval_miss_behavior                diagnostic; no fake linker admission
sensitive_exact_only_controls          diagnostic; model normally does not see them
high_cardinality_accuracy
metamorphic_consistency
repeat_agreement
```

The scoring classifier may only use frozen case metadata and conservative exact identity
normalization matching product exact-bind semantics. It may not invent a new semantic heuristic.

## 5. J1T — typed temporal decision

J1T produces **two different evidence lanes**.

### 5.1 J1T-CHOICE

The existing frozen 34-case benchmark remains unchanged:

```text
surface
→ case-frozen closed choices
→ one choice / ABSTAIN
```

This measures closed-choice discrimination. It is not by itself production contract fidelity.

Current product PERIOD ontology, exactly:

```text
THIS_WEEK
THIS_MONTH
THIS_QUARTER
THIS_YEAR
PREVIOUS_WEEK
PREVIOUS_MONTH
PREVIOUS_QUARTER
PREVIOUS_YEAR
LAST_N_DAYS
LAST_N_WEEKS
LAST_N_MONTHS
```

Current product COMPARISON ontology, exactly:

```text
PREVIOUS_PERIOD
PREVIOUS_YEAR_ALIGNED
```

The benchmark document follows product terminology. Product enums are not changed for the eval.

### 5.2 J1T-CONTRACT-FIDELITY

Question:

> Can this challenger's native transport express the actual
> `TemporalNormalizationChoice` fields without pre-enumerating the case answer?

Required fields:

```text
decision
period_kind
comparison_kind
n
implicit_base_period_kind
implicit_base_n
reason
```

For structured-chat models, the harness uses the real strict product schema and gives the model
the exact surface + closed ontology only — not a list such as 7/14/30 prepared from the answer.

For Jev, native primitive capability is assessed explicitly. OpenRouter's Jev decision surface
provides `choice`, `noul` and `score`; it is not a free-form/counting transport. A dynamic
positive integer `n` / `implicit_base_n` therefore cannot be represented faithfully without
enumerating possible answers.

If a required field cannot be represented:

```text
TEMPORAL_INTEGRATION_LIMITATION
```

is recorded. No prompt hack, regex, case-specific choice list or product enum change may hide it.

High J1T-CHOICE accuracy cannot override failed contract fidelity. In particular, failed dynamic
integer fidelity means:

```text
Jev temporal production candidate = NO
```

unless a later explicitly-authorized architecture changes the temporal contract.

Date/calendar arithmetic always remains deterministic in `TemporalBindingEngine`.

## 6. Fairness / frozen-case rules

- J1S/J1T corpus blob SHA values remain those sealed before any valid corrected result.
- repeated-run subset and metamorphic groups remain frozen;
- same logical case / bounded choice set across primary peers;
- no model-specific testcase wording except transport syntax;
- no named-case prompt tuning;
- no Validation50 / Hidden50 content;
- no production threshold tuning;
- provider/transport failures are not semantic wrongs;
- old run `35704627396` used the superseded Gemini/Jev/Sol peer topology and is invalid
  decision authority even if it completes.

## 7. Shared measurements

```text
accuracy / contract accuracy as applicable
ABSTAIN precision + recall
unsafe ambiguity pick
choice escape
Turkish robustness
metamorphic consistency
same-input repeat agreement
p50 / p95 latency
cost
provider failures
reasoning policy
```

Jev choice lane additionally records probability distribution, Brier/ECE diagnostic and
high-confidence-wrong count. No result automatically activates a confidence threshold.

## 8. P0

```text
choice outside supplied set = 0
silent ambiguity auto-pick = 0
cross-tenant semantic leak = 0
semantic authority minted by model = 0
hidden fallback/cascade = 0
case-derived rule = 0
```

## 9. Decision rule

```text
Jev poor / materially weaker
→ REJECT
→ product code unchanged
→ D65-SI may proceed on current topology without another micro-consult

Jev promising for a product role
→ STOP
→ present J1S/J1T choice + contract-fidelity + stability/cost evidence
→ consult user
→ D65-J1B remains closed until approval

primary cheap tier inconclusive / nobody clears floor
→ STOP
→ consult user before conditional Terra stage
```

Production cascade, confidence threshold and topology are never selected automatically.

## 10. Corrected execution order

```text
freeze-v2 metadata / corpus unchanged
→ provider-free harness/schema gate
→ small transport smoke on PRIMARY peers
→ J1S full primary bake-off
→ J1T-CHOICE full primary bake-off
→ J1T-CONTRACT-FIDELITY
→ repeated/metamorphic evidence
→ metrics/calibration receipts
→ decision gate
```

After the J1 decision, D65-SI Standard Integration Closure precedes X0.
