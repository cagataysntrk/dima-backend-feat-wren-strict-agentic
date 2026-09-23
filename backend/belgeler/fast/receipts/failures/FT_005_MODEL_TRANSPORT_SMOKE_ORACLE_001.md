# FT-005 FAILURE RECEIPT — MODEL_TRANSPORT_SMOKE_ORACLE_001

Status: CLOSED / EVAL_ORACLE_STAGE_MIX
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`

OBSERVED_RUN:
`35816477325`

OBSERVED_SHA:
`3fc686c9fa4f86927a5ea51f43cf688b9c010a6c`

## Scope

This run was intended to prove only:

- canonical OpenRouter credential is available;
- exact Luna/Sol request model identity;
- strict JSON-schema transport accepted;
- provider fallback disabled;
- parseable structured JSON;
- current Pydantic contract valid.

It was NOT intended to be the full semantic/retrieval quality gate.

## Provider-free gate

`GREEN`

Validated:
- strict recursive schema normalization;
- exact OpenRouter model IDs;
- fallback disabled;
- explicit reasoning policy;
- provider HTTP failure classification.

## Luna lane

Request model:
`openai/gpt-5.6-luna`

Result:
`GREEN`

Transport identity verifier:
`PASS`

## Sol lane

Request model:
`openai/gpt-5.6-sol`

Observed structured transport:

```text
HTTP = 200
transport_success = true
parse_success = true
structured_valid = true
request_model_id = openai/gpt-5.6-sol
response_model_id = openai/gpt-5.6-sol
provider_fallbacks = false
```

Safe non-executable case:
`PASS`

Executable Q1 effective semantics:
- SELF_CONTAINED;
- SUM;
- LAST_N_DAYS 30;
- measure = sipariş tutarı.

Observed retrieval term:
`["sipariş"]`

The generic focused sentinel's full semantic oracle then failed:

`entity-centric retrieval miss for orders: ['sipariş']`

## Root cause

`EVAL_ORACLE_STAGE_MIX`

The transport smoke reused the full semantic certification exit code.

That incorrectly made a later-stage retrieval-quality assertion part of the earlier transport gate.

This is not:
- a provider failure;
- a credential failure;
- a strict-schema transport failure;
- a Sol typed-output failure;
- permission to patch the product prompt.

## Authorized patch

Workflow-only:

1. always preserve the two-case receipt even if the focused semantic oracle returns RED;
2. transport smoke verifier decides this stage using only:
   - transport_success;
   - parse_success;
   - structured_valid;
   - exact request model;
   - canonical model;
   - HTTP 200;
   - fallback disabled;
   - non-empty response model identity.
3. semantic/retrieval quality remains hard in the later frozen focused matrix.

## Forbidden

- weaken retrieval gate in full matrix;
- change production prompt;
- add translation dictionary;
- label Sol semantic quality GREEN from this smoke;
- treat transport smoke as FT-005 seal evidence.

## Closure condition

Re-run both Luna and Sol transport lanes with the corrected stage-specific oracle.


## Closure

Workflow-only corrective SHA:
`57943518e9c4ca85710795423f1cd0ee2090f809`

Canonical rerun:
`35816680632 GREEN`

Luna transport:
`PASS`

Sol transport:
`PASS`

The full semantic/retrieval oracle was not weakened; it remains reserved for the frozen focused matrix.

Product prompt/schema/algorithm touch:
`0`

Receipt CLOSED.
