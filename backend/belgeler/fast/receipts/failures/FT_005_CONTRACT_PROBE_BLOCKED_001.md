# FT-005 FAILURE RECEIPT — CONTRACT_PROBE_BLOCKED_001

Status: BLOCKED / TRANSPORT_PROVIDER_FAILURE
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`

RUN:
`35817686083`

PROBE_SHA:
`7340ba428537c2f129f64581d37427f948247c33`

MODEL_ROLE:
`LUNA_BASELINE`

REQUEST_MODEL:
`openai/gpt-5.6-luna`

PROMPT_VARIANT:
`contract_probe`

## Provider-free result

`GREEN`

The eval-only contract probe itself is syntactically/structurally valid.

## Live result

Every live case, beginning with q1, returned:

`HTTP 403 — Key limit exceeded (total limit)`

Therefore:

```text
TRANSPORT_SUCCESS = false
PARSE_SUCCESS = false
STRUCTURED_VALID = not evaluated
SEMANTIC_RESULT = not evaluated
```

This is NOT:
- Luna semantic RED;
- contract-probe semantic RED;
- evidence that the prompt repair failed;
- permission to substitute another provider/model.

## Existing evidence that still authorizes a minimal generic repair

Independent of this blocked probe:

1. Full Luna/Sol matrix run `35816894471` showed both model families repeatedly emit
   semantically useful executable drafts plus non-null diagnostic reason, while the current
   Pydantic validator requires executable reason=null.

2. Production follow-up prompt does not state that cross-field invariant.

3. The same prompt does not explicitly state that unsupported operations must use top-level
   UNSUPPORTED with effective_draft=null.

4. Real pinned-Metabase retrieval probe `35817396762` proves Turkish-only terms miss direct
   SEARCH while an English entity/table term hits.

5. Sealed FT-003 Ask cognition already contains the generic entity/table retrieval wording.

## Authorized repair

Minimal production prompt-contract clarification in:
`backend/app/fast/followup_cognition.py`

Allowed additions only:
- explicit executable/non-executable cross-field shape;
- outer UNSUPPORTED representation;
- COUNT/SUM measure-hint shape;
- FT-003-equivalent cross-language entity/table lookup wording;
- ambiguity fail-closed wording;
- clarification-answer completion semantics.

Forbidden:
- Pydantic schema relaxation merely to accept bad output;
- deterministic planner;
- slot engine;
- translation dictionary;
- phrase patch;
- regex glossary;
- query/execution changes.

## Re-proof

Provider-free FT-005 must stay GREEN immediately.
Real-model Luna/Sol re-proof remains BLOCKED until canonical OpenRouter credential capacity is available.
