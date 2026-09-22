# FT-005 FAILURE RECEIPT — MODEL_SENTINEL_RED_001

Status: OPEN / CLASSIFICATION IN PROGRESS
Date: 2026-09-23

OBSERVED_RUN:
`35786550995`

OBSERVED_SHA:
`19628e973b6ceee3b50620a7a544903364823e77`

MODEL_ROLE:
`THIRD_MODEL_DIAGNOSTIC`

EXACT_MODEL_ID:
`google/gemini-2.5-flash-lite`

PROVIDER:
`openrouter`

## Summary

The provider-free FT-005 conversation core is GREEN.

This real-model follow-up sentinel is RED.

Do not collapse this into a generic MODEL_FAILED class.

Observed candidate failure families are separated below.

## Family A — EVAL_ORACLE_OVERCONSTRAINT

Case:
`q2_previous_month`

Observed effective semantics:

```text
status = CONTEXTUAL
aggregation = SUM
measure_hint = amount
temporal = PREVIOUS_MONTH
```

Observed diagnostic slot metadata omitted ENTITY from inherited_slots.

The current execution path does not use inherited_slots/replaced_slots as execution authority.

Therefore exact slot-label membership is diagnostic unless/until that metadata becomes execution authority.

Hard product oracle must judge:
- effective analytical semantics;
- safe authority path;
- current revalidation;
- final query/result correctness.

## Family B — MODEL_STRUCTURED_OUTPUT_RELIABILITY

Observed `COGNITION_UNAVAILABLE` for multiple cases including:
- q3_breakdown;
- explicit_reply_older_turn;
- self_contained_topic_switch;
- ambiguous_contextual_followup;
- unsupported_avg.

Current production adapter intentionally collapses inner parsing/validation/provider causes behind COGNITION_UNAVAILABLE.

The exact cause is not yet observable.

Possible causes remain unclassified:
- provider transport;
- invalid JSON;
- schema violation;
- Pydantic validator;
- enum mismatch;
- missing field;
- stochastic model behavior.

No prompt patch is authorized before observability and repeatability measurement.

## Family C — RETRIEVAL_CONTRACT_DRIFT candidate

Observed structured outputs include search terms such as:
`sipariş tutarı`

The sealed FT-003 retrieval contract requires entity/table-centric metadata lookup terms.

This may be a real product-impacting failure because search terms feed resource discovery.

Do not fix with:
- Turkish-English dictionary;
- phrase patch;
- regex glossary;
- deterministic slot engine.

Measure model differential first.

## Required next proof

1. eval-only RecordingStructuredGenerator;
2. record structured action or digest, validation/provider cause, latency/tokens where available;
3. separate HARD vs DIAGNOSTIC assertions;
4. repeat exact structured failure input 3 sequential times, workers=1;
5. preserve Gemini result;
6. run frozen corpus on:
   - gpt-5.6-luna = LUNA_BASELINE;
   - gpt-5.6-sol = SOL_CEILING;
7. classify model dependency before product patch.
