# DIMA DAY 6.5 — SI FULL-LIVE FAILURE RECEIPT

## D65-SI-FULL-LIVE-001

**Date:** 2026-09-22  
**Branch:** `feat/ask-v2-mvp`  
**Tested SHA:** `4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a`  
**Workflow run:** `35724830736`  
**Workflow:** `v2-day6-5-si-full-live-standard-once`  
**Classification status:** ROOT FAMILY CLASSIFIED / EXACT SUBCAUSE OPEN  
**Product modification authorized by this receipt:** NO

## Observed failure

Frozen case:

```text
id       = si-live-001
family   = metric_only_non_exact
question = "tahsil edilmemiş cari bakiyeyi göster"

expected = ACCEPTED / cube=cari / metric=bakiye

actual:
status       = CLARIFICATION_REQUIRED
authority    = NONE
query_count  = 0
```

The test aborted immediately on this assertion, so:
- cases 002–006 remain UNKNOWN for this run;
- the JSON report was never written;
- upload-artifact found no report.

## Evidence that remains GREEN

Same run preflight:
```text
model-role / Standard harness tests = 6/6 PASS
```

Previously sealed:
```text
semantic surface completeness       GREEN
shared Standard/Research XOR        GREEN
Research temporal role split        GREEN
focused provider-free SI            GREEN
real Standard Wren sentinel         GREEN
retained Research Wren sentinel     GREEN
```

Do not reopen these without new invalidating evidence.

## Model/provider evidence

Only live model call before failure:
```text
REFERENCE_LANGUAGE
openai/gpt-5.6-sol
SUCCESS
```

No SEMANTIC_LINKER/Luna call occurred before the clarification.

Therefore:
```text
MODEL_COGNITION     != primary owner
PROVIDER_TRANSPORT  != primary owner
WREN_DB_EXECUTION   != primary owner
TEMPORAL            != primary owner
AUTHORITY_XOR       != primary owner

PRIMARY FAMILY:
CONTRACT/ARCHITECTURE
→ SEMANTIC_DISCOVERY_BREADTH / PRE-LINKER_CANDIDATE_BOUNDARY
```

Current single-owner boundary:
`SemanticCatalogRetriever / SemanticCandidateGenerator`.

## Exact subcause — OPEN

Do NOT guess between:

### Path A
```text
non-exact metric surface
→ exhaustive metric enumeration exceeds linker bound
→ CANDIDATE_SET_TOO_BROAD
→ semantic provider never called
```

### Path B
```text
surface collapses to overlapping exact phrase such as "bakiye"
→ multiple exact governed candidates
→ AMBIGUOUS_EXACT
→ semantic provider never called
```

### Path C
another structural pre-linker cause.

Exact trace must prove the path before product modification.

## Mandatory next sequence

1. Eval-only: make full-live harness collect all six frozen cases and always emit JSON.
2. Eval-only: record draft + declared semantic surface + bounded retrieval/selection telemetry.
3. Same frozen family diagnostic; no product behavior change.
4. Open root fix only after exact subcause is proven.
5. Provider-free family + metamorphic proofs before another paid six-case run.

## Forbidden fixes

Do NOT:
- raise `max_candidates` to hide the defect;
- add literal `cari/bakiye/mizan` code or fixture aliases;
- add regex/stemming/SequenceMatcher/fuzzy semantic authority;
- add named-case prompt examples;
- send the full catalog to Luna;
- auto-select retrieval top-1;
- modify the frozen corpus/expected results.

Retriever remains discovery-only; only the BindingGate may mint semantic authority.

## Gate impact

```text
D65-SI FINAL                         OPEN
full-live Standard composition      RED
semantic discovery scalability      OPEN
M0E-DEEP-DELTA                      still ACTIVE in parallel
X0                                  BLOCKED
DEV80 / Validation50 / Hidden50     FORBIDDEN
```


## Exact same-product-semantics diagnostic — Path A PROVEN

Diagnostic run:
`35728413368`

Artifact:
`v2-day6-5-si-semantic-diagnostic-001`

Precondition proved in workflow:
```text
git diff 4ad8238c... HEAD -- backend/app
= EMPTY
```

Therefore product semantic code was unchanged from the failed full-live SHA.

Observed trace:
```text
draft semantic surface
= "tahsil edilmemiş cari bakiye"

kind_hint
= metric

retriever backend
= deterministic_enumeration_v1

candidate_count_before_bound
= 136

exact_candidate_count
= 0

visible_candidate_count
= 48

too_broad
= true

semantic selection
= CANDIDATE_SET_TOO_BROAD

semantic_provider_called
= false

final
= CLARIFICATION_REQUIRED
authority = NONE
query_count = 0
```

Exact subcause:
```text
PATH A = PROVEN
PATH B = NOT OBSERVED
SEMANTIC_DECISION_CONTEXT_LOSS = NOT OBSERVED FOR CASE 001
```

Root owner remains:
`SemanticCatalogRetriever / SemanticCandidateGenerator discovery boundary`.

Authorized next product change:
implement the smallest generic bounded ranked retrieval backend over governed catalog metadata.
Retrieval rank remains discovery-only and may never mint semantic authority.


---

## D65-SI-FINAL-CAUSAL-CLOSURE

Final evidence:
- `35738044476 = 73/73 PASS`;
- `35738400321 = focused live 001+005 GREEN`;
- `35738912690 = frozen six-case full-live GREEN`;
- final HEAD `c72eb9133556bd892041cc0ef543f62dcfe5dbab`;
- final artifact `failed_case_ids=[]`, `accepted=5`, `clarified=1`.

The failure chain is CLOSED as a sequence of distinct owners, not one repeated bug:

1. exhaustive catalog breadth exposed pre-linker bounded discovery failure;
2. governed token-index discovery fixed scalability without minting authority;
3. later live evidence exposed draft/filter material-meaning and contextual dimension seams;
4. stale eval tracing caused an independent EVAL_ORACLE incident;
5. cheap attacks exposed exact-duplicate contextual bypass + coverage visibility gaps;
6. generic contracts were repaired;
7. family, focused-live and frozen-full-live proofs all went GREEN.

No more semantic-discovery tuning is authorized from this history alone.

Current state:
`D65-SI FINAL GREEN / receipts preserved for audit`.
