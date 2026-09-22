# FT-005 FAILURE RECEIPT — ACCEPTED_CONTEXT_LINEAGE_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

OBSERVED_RUN:
`35783968049`

OBSERVED_SHA:
`e1261f754f368cc91bf14552c1e4666208ce811e`

FAILURE_CLASS:
`ACCEPTED_CONTEXT_LINEAGE_TRUNCATION`

FAILED_TEST:
`test_contextual_chain_supplies_accepted_user_question_lineage_not_only_last_fragment`

## Observed

Sequence:

```text
Q1 = Son 30 günde sipariş tutarı ne kadar?
Q2 = Peki geçen ay?
Q3 = Bölgelere göre?
```

At Q3 follow-up cognition received:

`source_questions = ("Peki geçen ay?",)`

Expected:

`source_questions = (Q1, Q2)`

## Why this matters

Q2 is intentionally elliptical. It carries temporal delta but not the original entity/measure wording.

The accepted context contains current accepted field/evidence authority, but the model still needs the accepted USER-question lineage to construct a complete bounded effective draft such as entity/table search terms.

This is not chat history and not assistant prose.

## Root cause

Accepted context was rebuilt on every successful turn with:

`source_turn_ids = (current_turn_id,)`

instead of carrying the accepted source lineage forward.

FastConversationService also supplied only the immediate source turn's user question.

## Normative rule

```text
accepted contextual turn lineage
= prior accepted source lineage + current accepted turn

model context text
= USER questions from accepted source_turn_ids only

assistant prose
= 0
```

Lineage is deduplicated and ordered.

## Authorized patch

Conversation owner only:
- when building accepted context, expand immediate context source turns through their accepted source_turn_ids;
- append current turn ID;
- dedupe preserving order;
- when a source accepted context is selected, supply user_question for each accepted source_turn_id.

Do not persist assistant answer text.
Do not pass full frontend history.
Do not alter FastAskService.

## Re-proof

- Q3 receives (Q1, Q2);
- Q2 accepted_context.source_turn_ids = (Q1_turn, Q2_turn);
- explicit older-turn reply still selects the requested lineage;
- topic-switch non-inheritance remains GREEN;
- FT-004 and FT-003 regressions GREEN.
