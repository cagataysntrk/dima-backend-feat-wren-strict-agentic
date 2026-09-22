# FT-005 FAILURE RECEIPT — SELF_CONTAINED_CONTEXT_LEAK_001

Status: CLOSED / FOLLOWUP_AUTHORITY_CONTEXT_LEAK
Date: 2026-09-22

OBSERVED_RUN:
`35783245084`

OBSERVED_SHA:
`d06922c228ccdc6a49ebeabe501ce4760aef6081`

FAILURE_CLASS:
`FOLLOWUP_AUTHORITY_CONTEXT_LEAK`

FAILED_TEST:
`test_self_contained_topic_switch_does_not_pass_prior_context_to_execution_factory`

## What passed

In the same provider-free semantic run:
- first turn conversation/run/evidence;
- contextual "Peki geçen ay?" lineage;
- contextual "Bölgelere göre?" lineage;
- explicit reply to older turn;
- missing-context clarification;
- owner/tenant isolation;
- mutable superadmin claim ownership stability;
- active-run conflict;
- clarification continuation;
- retry/follow-up separation;
- accepted-context handle/prose hygiene.

Only the self-contained topic-switch execution boundary failed.

## Observed

The resolver correctly returned:

`SELF_CONTAINED`

The stored turn correctly had:

`context_source_turn_ids = ()`

But the operation factory still received the previous:

`FastAcceptedContext`

Expected:

`accepted_context = None`

and:

`source_questions = ()`

for execution composition of a SELF_CONTAINED turn.

## Root cause

FastConversationService computes prior accepted context before follow-up classification, which is correct because the classifier may need it to decide whether the new utterance is contextual or a topic switch.

After classification, however, the same pre-classification context was passed unconditionally into the context-bound FastAskService operation.

That creates a hidden authority channel where a turn declared SELF_CONTAINED can still influence resource/field selection through prior context hints.

## Normative rule

```text
follow-up classifier may inspect prior accepted context

SELF_CONTAINED resolution
-> execution accepted_context = None
-> execution source_questions = ()
-> context_source_turn_ids = ()
```

CONTEXTUAL may pass only the explicitly selected accepted source context.

## Authorized patch

Owner:
`backend/app/fast/conversation_service.py`

After resolution:
- derive execution_context / execution_source_questions from resolution status;
- SELF_CONTAINED => clear both;
- CONTEXTUAL => retain selected accepted context/source user question;
- clarification metadata remains separate and explicit.

Do not change FastAskService or FT-003 authority.

## Re-proof

Required:
- self-contained topic-switch test GREEN;
- all other FT-005 provider-free semantic tests GREEN;
- FT-004 lifecycle regressions GREEN;
- FT-003 regressions GREEN.


## Closure

Corrective commit:
`148576f66701ad082f4a99685ef19a482edd156f`

Provider-free proof:
`35783433696 GREEN`

Verified:
- SELF_CONTAINED resolution carries no execution accepted_context;
- SELF_CONTAINED execution source_questions = empty;
- stored context_source_turn_ids = empty;
- contextual follow-ups still inherit explicit accepted source context;
- FT-004 lifecycle regression GREEN;
- FT-003 regression GREEN.

Failure CLOSED.
