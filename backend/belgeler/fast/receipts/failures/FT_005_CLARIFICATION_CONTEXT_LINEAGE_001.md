# FT-005 FAILURE RECEIPT — CLARIFICATION_CONTEXT_LINEAGE_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

OBSERVED_RUN:
`35784270076`

OBSERVED_SHA:
`8fecf36f2fcbf665f2cb2d2912bcbf4eaf9574c7`

FAILURE_CLASS:
`CLARIFICATION_CONTEXT_LINEAGE`

FAILED_TEST:
`test_contextual_clarification_preserves_accepted_source_for_new_child_run`

## Scenario

1. Q1 succeeds and produces accepted context/evidence.
2. A context-dependent follow-up is ambiguous and becomes WAITING_CLARIFICATION.
3. User supplies clarification.
4. Old WAITING run must be finalized/cancelled.
5. New child turn + new run must reuse the prior accepted source as cognition context and revalidate current authority.

## Observed

The WAITING turn had:

`context_source_turn_ids = ()`

Expected:

`context_source_turn_ids = (prior_accepted_turn_id,)`

Therefore the clarification continuation could not recover the prior accepted context.

## Root cause

FastConversationService records context_source_turn_ids only when resolution status is CONTEXTUAL.

But CLARIFICATION_REQUIRED can itself be a contextual outcome: the model may know which accepted prior turn is relevant while still needing one missing slot from the user.

The waiting run is not execution authority, but its turn must retain provenance of the accepted context source that caused the clarification.

## Normative rule

```text
contextual clarification
-> WAITING turn records accepted source turn provenance
-> old WAITING run never reopens
-> clarification answer cancels/finalizes old run
-> new child turn
-> new run
-> same accepted source provided as cognition context
-> current resource/field authority revalidated
```

Missing-context clarification with no safe source remains source-less.

## Authorized patch

Conversation owner only:
- when resolution is CLARIFICATION_REQUIRED and a selected source turn has accepted context,
  preserve that immediate source turn in context_source_turn_ids;
- do not execute against that source;
- clarification answer may recover it through the existing explicit clarifies_run_id path.

Do not mutate FastRunManager state semantics.
Do not reopen WAITING run.
Do not copy assistant prose.

## Re-proof

- waiting turn keeps prior accepted source;
- old run becomes CANCELLED after clarification answer;
- new turn/run are distinct;
- new resolver call sees accepted context + accepted user-question lineage + original clarification question;
- topic-switch and FT-003/004 regressions remain GREEN.
