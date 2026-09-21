"""Day 4 query-necessity policy.

This layer does not understand raw language or select semantic refs. It consumes the
typed TurnInterpretation and bounded ConversationState, then decides whether this turn
should talk, clarify, explain existing evidence, execute standard analytics, or stop.
"""

from __future__ import annotations

from app.v2.models import (
    ConversationStateV2,
    DialogueAction,
    SemanticResolutionBundle,
    TurnAct,
    TurnInterpretation,
)


class DialoguePolicyV0:
    def before_grounding(
        self,
        *,
        turn: TurnInterpretation,
        conversation: ConversationStateV2,
    ) -> DialogueAction | None:
        if turn.dialogue_act == TurnAct.SOCIAL:
            return DialogueAction.TALK
        if turn.dialogue_act == TurnAct.RESULT_EXPLAIN:
            if (
                conversation.has_active_result
                and conversation.last_result is not None
                and conversation.last_result.verified
            ):
                return DialogueAction.EXPLAIN_EXISTING
            return DialogueAction.UNSUPPORTED
        if turn.dialogue_act == TurnAct.UNSUPPORTED:
            return DialogueAction.UNSUPPORTED
        if turn.dialogue_act == TurnAct.CLARIFICATION_ANSWER:
            if (
                conversation.pending_clarification
                and conversation.clarification_state is not None
                and conversation.pending_analytical is not None
            ):
                return None
            return DialogueAction.UNSUPPORTED
        return None

    def after_grounding(
        self,
        *,
        turn: TurnInterpretation,
        bundle: SemanticResolutionBundle,
    ) -> DialogueAction:
        # Research keeps every requested MUST goal visible in ResearchBrief even when
        # one semantic ref is blocking. The brief itself becomes BLOCKED; Day 6 does
        # not collapse a complex request into the first clarification.
        if turn.dialogue_act in {
            TurnAct.COMPLEX_ANALYSIS,
            TurnAct.REPORT_REQUEST,
        }:
            return DialogueAction.RESEARCH_BRIEF
        if bundle.clarification is not None:
            return DialogueAction.CLARIFY
        if turn.dialogue_act in {
            TurnAct.ANALYTIC_NEW,
            TurnAct.ANALYTIC_REFINE,
            TurnAct.USER_REPAIR,
            TurnAct.CLARIFICATION_ANSWER,
        }:
            return DialogueAction.ANALYTIC_STANDARD
        return DialogueAction.UNSUPPORTED
