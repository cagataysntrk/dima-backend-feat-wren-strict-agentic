"""FT-005 conversation service: identity, lineage, typed context and new-run semantics."""

from __future__ import annotations

from typing import Any, Protocol

from app.fast.ask_cognition import FastCognition
from app.fast.ask_models import (
    AggregationKind,
    AskOutcomeStatus,
    FastAskErrorPayload,
    FastAskResponse,
)
from app.fast.ask_service import FastAskService, GatewayFactory
from app.fast.conversation_models import (
    FastAcceptedContext,
    FastConversationDetail,
    FastConversationSnapshot,
    FastFollowupResolution,
    FastFollowupStatus,
    FastTurnCreateRequest,
    FastTurnSnapshot,
)
from app.fast.conversation_store import (
    FastConversationNotFound,
    FastConversationStore,
)
from app.fast.followup_cognition import (
    ContextBoundFastCognition,
    FastFollowupCognition,
)
from app.fast.run_manager import FastRunManager, FastRunOperation
from app.fast.run_models import (
    FastRunCreateRequest,
    FastRunState,
    TERMINAL_RUN_STATES,
)
from app.fast.run_store import FastRunOwner


class FastConversationConflict(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class FastConversationOperationFactory(Protocol):
    def build(
        self,
        *,
        resolution: FastFollowupResolution,
        accepted_context: FastAcceptedContext | None,
        source_questions: tuple[str, ...],
        clarification_question: str | None,
    ) -> FastRunOperation:
        ...


class FastConversationAskFactory:
    """Builds a context-bound FastAskService without duplicating Ask authority logic."""

    def __init__(
        self,
        *,
        selector_cognition: FastCognition,
        gateway_factory: GatewayFactory,
        max_resource_candidates: int = 8,
    ) -> None:
        self._selector = selector_cognition
        self._gateway_factory = gateway_factory
        self._max_resource_candidates = max_resource_candidates

    def build(
        self,
        *,
        resolution: FastFollowupResolution,
        accepted_context: FastAcceptedContext | None,
        source_questions: tuple[str, ...],
        clarification_question: str | None,
    ) -> FastRunOperation:
        if resolution.effective_draft is None:
            raise ValueError("executable conversation operation requires effective draft")
        cognition = ContextBoundFastCognition(
            draft=resolution.effective_draft,
            selector=self._selector,
            accepted_context=accepted_context,
            source_questions=source_questions,
            clarification_question=clarification_question,
        )
        return FastAskService(
            cognition=cognition,
            gateway_factory=self._gateway_factory,
            max_resource_candidates=self._max_resource_candidates,
        )


class _StaticOutcomeOperation:
    def __init__(self, *, status: AskOutcomeStatus, code: str, message: str) -> None:
        self._status = status
        self._code = code
        self._message = message

    def ask(self, request, *, principal: Any) -> FastAskResponse:
        return FastAskResponse(
            status=self._status,
            question=request.question.strip(),
            error=FastAskErrorPayload(
                code=self._code,
                message=self._message,
            ),
        )


def _accepted_context_from_response(
    *,
    response: FastAskResponse,
    source_turn_ids: tuple[str, ...],
) -> FastAcceptedContext | None:
    if response.status != AskOutcomeStatus.SUCCESS or response.evidence is None:
        return None
    evidence = response.evidence
    try:
        stage = evidence.portable_query["stages"][0]
        aggregation_name = str(stage["aggregation"][0][0]).upper()
        aggregation = AggregationKind(aggregation_name)
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    return FastAcceptedContext(
        source_turn_ids=source_turn_ids,
        resource_ref=evidence.resource_ref,
        accepted_field_refs=dict(evidence.field_refs),
        exact_time_bounds=(
            dict(evidence.exact_time_bounds)
            if evidence.exact_time_bounds is not None
            else None
        ),
        aggregation=aggregation,
        evidence_ids=(evidence.evidence_id,),
        query_fingerprints=(evidence.query_fingerprint,),
    )


class FastConversationService:
    _ACTIVE_CONFLICT_STATES = {
        FastRunState.CREATED,
        FastRunState.RUNNING,
        FastRunState.PARTIAL,
        FastRunState.CANCEL_REQUESTED,
    }

    def __init__(
        self,
        *,
        store: FastConversationStore,
        run_manager: FastRunManager,
        followup_cognition: FastFollowupCognition,
        operation_factory: FastConversationOperationFactory,
    ) -> None:
        self._store = store
        self._runs = run_manager
        self._followup = followup_cognition
        self._operations = operation_factory

    def create_conversation(
        self,
        *,
        principal: Any,
        title: str | None = None,
    ) -> FastConversationSnapshot:
        return self._store.create_conversation(
            owner=FastRunOwner.from_principal(principal),
            title=title,
        )

    def _refresh_turn(
        self,
        turn: FastTurnSnapshot,
        *,
        principal: Any,
    ) -> FastTurnSnapshot:
        run = self._runs.get_run(turn.run_id, principal=principal)
        accepted = None
        if run.state == FastRunState.COMPLETED and run.response is not None:
            accepted = _accepted_context_from_response(
                response=run.response,
                source_turn_ids=(turn.turn_id,),
            )
        return self._store.update_turn_from_run(
            turn_id=turn.turn_id,
            owner=FastRunOwner.from_principal(principal),
            status=run.state,
            accepted_context=accepted,
        )

    def _refresh_active(
        self,
        conversation_id: str,
        *,
        principal: Any,
    ) -> FastTurnSnapshot | None:
        owner = FastRunOwner.from_principal(principal)
        active = self._store.active_turn(conversation_id, owner)
        if active is None:
            return None
        return self._refresh_turn(active, principal=principal)

    def conversation(
        self,
        conversation_id: str,
        *,
        principal: Any,
    ) -> FastConversationDetail:
        self._refresh_active(conversation_id, principal=principal)
        return self._store.detail(
            conversation_id,
            FastRunOwner.from_principal(principal),
        )

    def turn(
        self,
        turn_id: str,
        *,
        principal: Any,
    ) -> FastTurnSnapshot:
        owner = FastRunOwner.from_principal(principal)
        turn = self._store.turn(turn_id, owner)
        return self._refresh_turn(turn, principal=principal)

    def _context_source(
        self,
        conversation_id: str,
        *,
        principal: Any,
        reply_to_turn_id: str | None,
    ) -> FastTurnSnapshot | None:
        owner = FastRunOwner.from_principal(principal)
        if reply_to_turn_id is not None:
            turn = self._store.turn(reply_to_turn_id, owner)
            if turn.conversation_id != conversation_id:
                raise FastConversationNotFound("turn not found")
            return self._refresh_turn(turn, principal=principal)
        latest = self._store.latest_accepted_turn(conversation_id, owner)
        if latest is None:
            return None
        return self._refresh_turn(latest, principal=principal)

    def submit_turn(
        self,
        conversation_id: str,
        payload: FastTurnCreateRequest,
        *,
        principal: Any,
    ) -> FastTurnSnapshot:
        owner = FastRunOwner.from_principal(principal)
        conversation = self._store.conversation(conversation_id, owner)
        active = self._refresh_active(conversation_id, principal=principal)

        clarification_question = None
        clarification_turn: FastTurnSnapshot | None = None
        if active is not None:
            if active.status in self._ACTIVE_CONFLICT_STATES:
                raise FastConversationConflict(
                    "ACTIVE_RUN_EXISTS",
                    "conversation already has an active analytical run",
                )
            if active.status == FastRunState.WAITING_CLARIFICATION:
                if payload.clarifies_run_id != active.run_id:
                    raise FastConversationConflict(
                        "WAITING_CLARIFICATION_EXISTS",
                        "conversation has a waiting clarification run",
                    )
                clarification_turn = active
                clarification_question = active.user_question
                cancelled = self._runs.cancel_run(
                    active.run_id,
                    principal=principal,
                )
                self._store.update_turn_from_run(
                    turn_id=active.turn_id,
                    owner=owner,
                    status=cancelled.state,
                    accepted_context=None,
                )

        latest_turn = self._store.latest_turn(conversation_id, owner)
        parent_turn_id = latest_turn.turn_id if latest_turn is not None else None

        source_turn: FastTurnSnapshot | None = None
        if payload.reply_to_turn_id is not None:
            source_turn = self._context_source(
                conversation_id,
                principal=principal,
                reply_to_turn_id=payload.reply_to_turn_id,
            )
        elif clarification_turn is not None:
            for source_turn_id in clarification_turn.context_source_turn_ids:
                candidate = self._store.turn(source_turn_id, owner)
                candidate = self._refresh_turn(candidate, principal=principal)
                if candidate.accepted_context is not None:
                    source_turn = candidate
                    break
        else:
            source_turn = self._context_source(
                conversation_id,
                principal=principal,
                reply_to_turn_id=None,
            )

        accepted_context = (
            source_turn.accepted_context
            if source_turn is not None
            else None
        )
        source_questions = (
            (source_turn.user_question,)
            if source_turn is not None
            else ()
        )
        if clarification_question is not None:
            source_questions = (*source_questions, clarification_question)

        resolution = self._followup.resolve(
            question=payload.question,
            accepted_context=accepted_context,
            source_questions=source_questions,
            clarification_question=clarification_question,
        )

        context_source_turn_ids: tuple[str, ...] = ()
        if (
            resolution.status == FastFollowupStatus.CONTEXTUAL
            and source_turn is not None
            and source_turn.accepted_context is not None
        ):
            context_source_turn_ids = (source_turn.turn_id,)

        if resolution.status in {
            FastFollowupStatus.SELF_CONTAINED,
            FastFollowupStatus.CONTEXTUAL,
        }:
            operation = self._operations.build(
                resolution=resolution,
                accepted_context=accepted_context,
                source_questions=source_questions,
                clarification_question=clarification_question,
            )
        elif resolution.status == FastFollowupStatus.CLARIFICATION_REQUIRED:
            operation = _StaticOutcomeOperation(
                status=AskOutcomeStatus.CLARIFICATION_REQUIRED,
                code="FOLLOWUP_CONTEXT_REQUIRED",
                message=resolution.reason or "follow-up context requires clarification",
            )
        else:
            operation = _StaticOutcomeOperation(
                status=AskOutcomeStatus.UNSUPPORTED,
                code="UNSUPPORTED",
                message=resolution.reason or "follow-up is unsupported",
            )

        run_payload = FastRunCreateRequest(
            question=payload.question,
            as_of_date=payload.as_of_date,
        )
        run = self._runs.create_run_with_operation(
            run_payload,
            principal=principal,
            operation=operation,
        )
        try:
            return self._store.append_turn(
                conversation_id=conversation.conversation_id,
                owner=owner,
                user_question=payload.question,
                as_of_date=payload.as_of_date,
                run_id=run.run_id,
                status=run.state,
                parent_turn_id=parent_turn_id,
                reply_to_turn_id=payload.reply_to_turn_id,
                clarifies_run_id=payload.clarifies_run_id,
                context_source_turn_ids=context_source_turn_ids,
            )
        except Exception:
            self._runs.cancel_run(run.run_id, principal=principal)
            raise
