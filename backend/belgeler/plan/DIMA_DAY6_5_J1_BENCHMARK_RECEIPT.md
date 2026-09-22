# DIMA DAY 6.5 — J1S / J1T BENCHMARK RECEIPT

**Status:** PREPARED / LIVE RESULTS NOT YET RUN  
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
C = openai/gpt-5.6-sol
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
| J1S | Sol | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1T | Gemini Flash-Lite | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1T | Jev 1.13 | NOT RUN | — | — | — | — | — | — | — | — | — |
| J1T | Sol | NOT RUN | — | — | — | — | — | — | — | — | — |

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
