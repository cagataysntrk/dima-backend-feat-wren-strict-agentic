# DIMA DAY 6.5 — J1S / J1T BENCHMARK RECEIPT

**Status:** **FULL CORRECTED RESULTS RECORDED — J1S JEV PROMISING / J1T JEV REJECTED / CONSULTATION STOP**  
**Entry checkpoint:** `f2b246a7f186705f8ddd98a61e60d950f606d326`  
**Current prep HEAD at receipt creation:** `22eacce89f8fef9506c3490f0fe4e32c61fd67a5`

## Frozen before any benchmark result

```text
J1S corpus
  file       = eval/v2_day6_5_j1s_frozen.json
  cases      = 36
  commit     = 33ebebecd3dbc9dba989e7c168e153460265a282
  blob sha   = 0dd53d5b1bb2ac39ba35f2c17c870c45c249d686

J1T corpus
  file       = eval/v2_day6_5_j1t_frozen.json
  cases      = 34
  commit     = 3aad6d9f4f5274e19801e2611fc830df6771a85f
  blob sha   = d18db04d26da1059e4ebb47d058f305e2e5a5bfb

freeze manifest
  file       = eval/v2_day6_5_j1_freeze_manifest.json
  commit     = 9656113d897d302596418a1cff96aaa11b119e92
```

Repeated-run subset and metamorphic groups are in the freeze manifest and are not edited after
first result.

## Challengers

```text
A = google/gemini-2.5-flash-lite
B = typesafe/jev-1.13
C = openai/gpt-5.6-luna

REFERENCE_CEILING = openai/gpt-5.6-sol (frozen small subset only)
CONDITIONAL = openai/gpt-5.6-terra (consult-gated)
```

Jev transport:
`POST https://openrouter.ai/api/alpha/decisions`

Generic chat/`structured_json()` is not used for Jev.

## Harness

```text
lab/v2_day6_5_j1_benchmark.py
manual live workflow = .github/workflows/v2-day6-5-j1-live-benchmark.yml
provider-free gate   = .github/workflows/v2-day6-5-j1-provider-free.yml
```

Provider fallbacks are disabled in the benchmark request. Transport/provider errors are recorded
as `TRANSPORT/PROVIDER`, not semantic wrong.

## Provider-free preparation gate

GitHub Actions:

```text
run = 35703887323
result = GREEN
pytest = 4 passed in 7.23s
compile = PASS
```

This proves frozen corpus integrity, J1T compatibility with the current closed temporal contract,
and harness transport isolation. It is not a live model-quality result.

## Product-code touch check

During corpus/harness preparation:

```text
semantic_linker.py             NO TOUCH
SemanticBindingGate            NO TOUCH
temporal_intent.py product     NO TOUCH
manager semantic authority     NO TOUCH
production /ask-v2             NO TOUCH
```

## Live execution table

Fill only from manual-only workflow artifacts.

| Track | Model | Run | Evaluable | Accuracy | Abstain P/R | Turkish | Metamorphic | Repeat | p50/p95 | Cost | Failure class |
|---|---|---:|---:|---:|---|---:|---:|---:|---|---:|---|
| J1S | Gemini Flash-Lite | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1S | Jev 1.13 | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1S | Luna | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1T | Gemini Flash-Lite | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1T | Jev 1.13 | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1T | Luna | NOT RUN | — | — | — | — | — | — | — | — | — |

Jev-only calibration fields:
- Brier;
- ECE;
- high-confidence-wrong count;
- raw probability distribution evidence.

## Decision gate

No decision yet.

```text
Jev poor
→ reject
→ product code unchanged

Jev promising
→ STOP
→ present evidence
→ consult user
→ D65-J1B remains closed until approval
```

No production model topology/cascade/threshold is authorized by this receipt.


## Pre-result challenger-role correction

Before any corrected decision-authority benchmark result:

```text
freeze = d65-j1-freeze-v2
reason = PRE_RESULT_CHALLENGER_ROLE_CORRECTION
corpus blobs = UNCHANGED
```

Run `35704627396` was started by a superseded one-shot workflow using
`Gemini / Jev / Sol` as equal peers. It is **INVALID J1 DECISION AUTHORITY** even if it
finishes successfully. It must not populate the table above or influence prompt/corpus/product
changes.

Corrected evidence also splits:
- J1S production model-needed score from deterministic/sensitive/retrieval controls;
- J1T-CHOICE from J1T-CONTRACT-FIDELITY;
- Sol reference ceiling from primary peer latency/cost ranking;
- Terra conditional second stage from all automatic runs.


## Corrected primary transport smoke

Run:
`35705416468` — **workflow GREEN / transport complete**

Primary set:
`Gemini Flash-Lite + Jev 1.13 + GPT-5.6 Luna`

Reasoning policy:
- Gemini = `reasoning.enabled=false`
- Jev = native Decisions, no chat reasoning layer
- Luna = `reasoning.enabled=false`

### J1S smoke

```text
Gemini  2/2 semantic cases, provider failures 0
Jev     2/2 semantic cases, provider failures 0
Luna    2/2 semantic cases, provider failures 0
```

### J1T-CHOICE smoke

```text
Gemini  1/2; unsafe ambiguity pick = 1
Jev     2/2; unsafe ambiguity pick = 0
Luna    2/2; unsafe ambiguity pick = 0
```

### J1T-CONTRACT-FIDELITY smoke

```text
Gemini  contract valid 2/2; exact 1/2; ABSTAIN reason miss
Jev     TEMPORAL_INTEGRATION_LIMITATION
        dynamic n / implicit_base_n not faithfully representable by native
        choice|noul|score without answer enumeration
Luna    contract valid 2/2; exact 2/2
```

### Failure classification before any patch

Gemini temporal smoke:
```text
failure_class = MODEL_COGNITION (provisional)
single_owner  = Gemini bounded temporal decision
evidence      = exact-same harness/cases; Luna succeeds
product patch = NONE
```

Jev temporal contract fidelity:
```text
failure_class = MODEL_CAPABILITY_FLOOR
subclass      = TEMPORAL_INTEGRATION_LIMITATION
single_owner  = Jev native Decisions transport capability
product patch = NONE
```

No architecture/Resolver/product semantic code is changed from smoke evidence. Smoke is not the
final winner decision; corrected full frozen primary bake-off remains required.


---

## Corrected full primary bake-off — decision receipt

Run:
`35705668833`

Tested SHA:
`bde3e5a21c159243002ef600ece007256d8482d0`

Freeze:
`d65-j1-freeze-v2`; J1S/J1T corpus blobs unchanged.

Workflow conclusion:
`FAILURE`, but the RED is **EVAL_ORACLE**, not provider outage and not an architecture regression.
See `DIMA_DAY6_5_FAILURE_TRIAGE_RECEIPTS.md / D65-J1-FULL-001`.

### J1S — production-relevant semantic decision

| Metric | Gemini Flash-Lite | Jev 1.13 | GPT-5.6 Luna |
|---|---:|---:|---:|
| model-needed accuracy | 86.67% (13/15) | **93.33% (14/15)** | 86.67% (13/15) |
| model-needed Turkish | 84.62% (11/13) | **92.31% (12/13)** | **92.31% (12/13)** |
| ambiguity abstain | 50% | 75% | **100%** |
| no-match abstain | 100% | 100% | 100% |
| metamorphic consistency | 100% | 100% | 100% |
| repeated-run agreement | 100% | 100% | 100% |
| p50 latency | 0.537s | **0.266s** | 1.013s |
| p95 latency | 0.675s | **0.363s** | 1.729s |
| measured total cost | $0.004084 | **$0.002282** | $0.007678 |

Jev vs current Gemini incumbent:
- +6.67 percentage points model-needed accuracy;
- ~49.5% of Gemini p50 latency;
- ~55.9% of Gemini measured cost;
- no high-confidence wrongs at the frozen 0.90 diagnostic threshold;
- Brier ≈ 0.1086; ECE-5bin ≈ 0.0857.

Jev's only **model-needed** miss:
- `j1s-019` — ambiguous "gelir"; expected ABSTAIN, selected Net Satış.
  Native confidence = 0.53; top choice probability = 0.65, ABSTAIN = 0.34.
  This is not a high-confidence silent wrong.

Jev's second all-corpus miss:
- `j1s-028` sensitive-exact control. This is not part of production model-needed winner scoring;
  production hides sensitive entity candidates from the ordinary linker unless exact-safe routing
  permits them.

Gemini model-needed misses:
- `j1s-019`
- `j1s-020`

Luna model-needed misses:
- `j1s-013`
- `j1s-031`

Frozen high-cardinality NPS cases are exact verified aliases and therefore land in deterministic
bypass controls; this corpus does **not** provide a model-needed high-cardinality score. Do not
invent or tune new cases after seeing results; record this as a benchmark limitation.

### J1T-CHOICE

| Metric | Gemini Flash-Lite | Jev 1.13 | GPT-5.6 Luna |
|---|---:|---:|---:|
| first-run accuracy | 97.06% | 94.12% | **100%** |
| ABSTAIN recall | 80% | 60% | **100%** |
| unsafe ambiguity pick | **1** | 0 | 0 |
| metamorphic consistency | 100% | 100% | 100% |
| repeated-run agreement | **100%** | **100%** | 91.67% |
| p50 latency | 0.488s | **0.286s** | 0.980s |
| p95 latency | 0.582s | **0.405s** | 1.508s |
| measured total cost | $0.003041 | **$0.001913** | $0.007108 |

Jev choice misses:
- `j1t-031` unsupported calendar-specific request;
- `j1t-032` absolute-quarter request.
Both should ABSTAIN.

Gemini miss:
- `j1t-028` ambiguous "son dönem" auto-picked THIS_MONTH — unsafe ambiguity pick.

Luna first-run is 34/34, but repeated-run stability is not perfect:
- `j1t-028` repeated choices = `ABSTAIN → PREVIOUS_MONTH → ABSTAIN`.

### J1T-CONTRACT-FIDELITY

Jev:
```text
status = TEMPORAL_INTEGRATION_LIMITATION
native primitives = choice | noul | score
dynamic n = NOT_DYNAMICALLY_REPRESENTABLE
implicit_base_n = NOT_DYNAMICALLY_REPRESENTABLE
case-answer enumeration would be required = YES
temporal production candidate = NO
```

Gemini:
- provider/network failures actually observed = 0;
- 6 responses violate Pydantic cross-field invariants;
- 3 additional valid typed responses are semantically wrong;
- exact contract over all frozen cases = **25/34 = 73.53%**.

Luna:
- provider/network failures actually observed = 0;
- 2 responses violate Pydantic cross-field invariants;
- all remaining valid typed responses exact;
- exact contract over all frozen cases = **32/34 = 94.12%**.

The existing harness incorrectly calls those 8 invalid typed responses
`TRANSPORT/PROVIDER`; this is the open EVAL_ORACLE receipt, not evidence to exclude them from
the denominator.

### Decision-gate interpretation

```text
Jev as universal semantic+temporal provider
= NO

Jev as bounded semantic CandidateSet decision primitive
= PROMISING

automatic production topology change
= FORBIDDEN

D65-J1B
= CONSULT REQUIRED

Terra conditional stage
= NOT TRIGGERED AUTOMATICALLY

D65-SI
= BLOCKED UNTIL J1 topology decision
```

Why "PROMISING" for J1S:
- it beats both primary peers on the frozen production model-needed accuracy;
- it preserves 100% repeated/metamorphic agreement;
- it is materially lower latency/cost in this run;
- wrong semantic evidence is low-confidence rather than high-confidence silent error;
- but it remains below an automatic production acceptance threshold and is weaker than Luna on
  ambiguity abstention.

Therefore no production model routing/cascade/threshold decision is taken here.


## Current consultation decision

Corrected evidence is sufficient to open a consultation, not to change production topology.

```text
J1S:
Jev bounded CandidateSet decision primitive = PROMISING

J1T:
Jev production temporal provider             = NO
reason                                       = TEMPORAL_INTEGRATION_LIMITATION

Luna typed temporal evidence                 = strongest primary peer
remaining concerns                           = invalid typed outputs + repeat instability

Gemini cheap universal role                  = materially challenged
automatic production topology change        = FORBIDDEN
```

Recommended next experiment if user approves:

```text
D65-J1B narrow split-topology engineering spike:
semantic candidate decision → JevDecisionProvider
temporal normalization      → structured temporal provider, with Luna as measured primary candidate
authority                   → unchanged deterministic gates
hidden fallback/cascade     → none
```

This does not authorize production activation. It only proves the provider seam and cost/quality
behavior under real Dima flow.

STOP/CONSULT remains active before J1B.
