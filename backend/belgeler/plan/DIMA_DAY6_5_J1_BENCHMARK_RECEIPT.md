# DIMA DAY 6.5 — J1S / J1T BENCHMARK RECEIPT

**Status:** PRE-RUN CORRECTED / VALID LIVE RESULTS NOT YET RUN  
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
