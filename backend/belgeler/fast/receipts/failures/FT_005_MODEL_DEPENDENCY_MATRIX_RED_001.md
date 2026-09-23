# FT-005 FAILURE RECEIPT — MODEL_DEPENDENCY_MATRIX_RED_001

Status: OPEN / FAILURE FAMILIES CLASSIFIED
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`

OBSERVED_RUN:
`35816894471`

OBSERVED_SHA:
`946cb933441381078941767e8ac6205349ff81e3`

## Matrix roles

```text
LUNA
request_model_id = openai/gpt-5.6-luna
canonical_model  = gpt-5.6-luna
role             = LUNA_BASELINE
measurement      = MODEL_COMPARABLE
reasoning        = disabled

SOL COMPARABLE
request_model_id = openai/gpt-5.6-sol
canonical_model  = gpt-5.6-sol
role             = SOL_CEILING
measurement      = MODEL_COMPARABLE
reasoning        = disabled

SOL CEILING
request_model_id = openai/gpt-5.6-sol
canonical_model  = gpt-5.6-sol
role             = SOL_CEILING
measurement      = MODEL_CEILING
reasoning        = ceiling_enabled
```

Transport smoke was already GREEN for both model families.
Therefore HTTP-200 typed failures below are evaluable model/contract evidence.

## Family A — EXECUTABLE_REASON_CONTRACT_MISMATCH

Observed across Luna and Sol.

Current product contract:

```text
SELF_CONTAINED / CONTEXTUAL
=> effective_draft required
=> reason MUST be null
```

Observed model behavior repeatedly:

```text
status = CONTEXTUAL or SELF_CONTAINED
effective_draft = semantically useful
reason = short explanation
```

Examples:
- Luna q2_previous_month:
  - CONTEXTUAL;
  - SUM;
  - amount;
  - PREVIOUS_MONTH;
  - correct slot intent;
  - HTTP 200 / parseable JSON;
  - rejected because executable result also carried reason.
- Luna/Sol q3_breakdown:
  - CONTEXTUAL;
  - SUM;
  - regional breakdown;
  - PREVIOUS_MONTH;
  - HTTP 200 / parseable JSON;
  - rejected by root cross-field validation.
- Luna/Sol explicit_reply_older_turn:
  - CONTEXTUAL;
  - LAST_N_DAYS 30;
  - regional breakdown;
  - rejected by the same executable-reason invariant.

Interpretation:

`SHARED CONTRACT / PROMPT / REPRESENTATION ISSUE SIGNAL`

This is NOT evidence that Luna is uniquely too weak, because Sol exhibits the same family.

No product schema/prompt patch is authorized by this receipt alone.

## Family B — RETRIEVAL_LANGUAGE / ENTITY LOOKUP DRIFT

The frozen semantic oracle currently requires the generated metadata lookup terms to directly carry
the English synthetic table identity.

Observed:
- Luna Q1: `["sipariş", "order"]` -> oracle PASS.
- Sol comparable Q1: `["sipariş", "siparişler"]` -> oracle RED.
- Sol topic switch: `["müşteri"]` -> oracle RED.
- Sol ceiling Q1/topic switch similarly used Turkish-only entity terms.

This may be:
1. a real product retrieval failure if Metabase SEARCH cannot resolve those terms against the
   English synthetic catalog; or
2. an over-constrained eval oracle if actual metadata discovery succeeds.

Do NOT decide from string equality.

Required next proof:
`generated terms -> real pinned Metabase metadata SEARCH -> candidate resources`

No translation dictionary or phrase patch is authorized.

## Family C — UNSAFE_AMBIGUITY_PICK

Sol MODEL_CEILING case:
`ambiguous_contextual_followup = "Peki diğeri?"`

Observed raw typed action:
- status = CONTEXTUAL;
- inferred "other temporal option" as LAST_N_DAYS;
- produced executable SUM draft.

Expected safety behavior:
`CLARIFICATION_REQUIRED`

This is a real semantic safety failure independent of the executable-reason mismatch.

Do not normalize it away.

## Family D — UNSUPPORTED REPRESENTATION MISMATCH

Luna `unsupported_avg` produced:
- outer status SELF_CONTAINED;
- inner AskDraft.status UNSUPPORTED;
- unsupported_reason present;
- an effective draft still present.

Current FastFollowupResolution requires non-executable UNSUPPORTED at the outer resolution layer.

This is not a provider failure. It is a typed representation mismatch and must remain evaluable.

Sol's corresponding late case did not yield model-quality evidence because provider quota failed first.

## Family E — CLARIFICATION ANSWER SEMANTIC MISMATCH

Luna `clarification_answer` produced:
- CONTEXTUAL;
- SUM amount;
- LAST_N_DAYS 30.

Frozen expected effective temporal intent:
`PREVIOUS_MONTH`

This is a semantic mismatch in addition to executable-reason contract invalidity.

It remains a hard failure.

## Family F — TRANSPORT_PROVIDER_FAILURE / OPENROUTER KEY LIMIT

Sol comparable and Sol ceiling later calls returned:

`HTTP 403 — Key limit exceeded (total limit)`

Observed on at least:
- unsupported_avg;
- clarification_answer;
- subsequent repeatability calls.

These rows are:
`NOT EVALUABLE AS MODEL WRONG`

Do not count them as Sol semantic RED.

Do not silently substitute another provider/model.

## Current model-dependency conclusion

The current evidence does NOT support:

```text
LUNA RED / SOL GREEN
=> stronger model required
```

Instead, before provider-limit rows:

```text
Luna + Sol share executable typed-contract failures
=> strong CONTRACT / PROMPT / REPRESENTATION issue signal

Sol ceiling additionally has an unsafe ambiguity pick
=> stronger reasoning is not automatically safer
```

Therefore:

`FAST_REQUIRES_STRONGER_MODEL_FOR_THIS_FAMILY = NOT PROVEN`

`SHARED_TYPED_CONTRACT_REPRESENTATION_DEBT = PROVEN`

`RETRIEVAL_DRIFT_PRODUCT_IMPACT = PENDING REAL METABASE SEARCH PROOF`

## Patch authorization

NOT YET authorized:
- production follow-up prompt;
- product Pydantic contract;
- deterministic inheritance algorithm;
- translation dictionary;
- special topic classifier.

Authorized next:
1. real pinned-Metabase search proof for observed Turkish/English retrieval terms;
2. inspect prompt/schema representation for executable reason and outer UNSUPPORTED semantics;
3. provider-free contract experiment before any product patch;
4. only then authorize smallest generic repair.

FT-005 remains OPEN.
