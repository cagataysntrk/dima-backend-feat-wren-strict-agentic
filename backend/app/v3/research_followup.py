"""P17 adapter to the single sealed P14 native Research occurrence path.

This module adds no analytical planner or execution semantics. It binds one durable P17
investigation task to the shared P14 occurrence runner, then optionally asks sealed P15
to materialize native Exploration for that exact verified occurrence.
"""
from __future__ import annotations

from app.v3.research import ObligationState, ResearchManager, ResearchSession
from app.v3.research_exploration import NativeResearchExploration
from app.v3.research_manager import (
    FollowupResult,
    ResearchInvestigationTask,
    ResearchManagerMaturationError,
    ResearchReasoningStep,
)
from app.v3.research_product import NativeResearchOccurrenceRunner
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_models import NativeEngineRequest
from control_plane.authorize import Principal


class NativeResearchFollowupExecutor:
    """Attach P17 lineage to the same native occurrence implementation as P14."""

    def __init__(
        self,
        *,
        store: ResearchSessionStore,
        occurrence_runner: NativeResearchOccurrenceRunner,
        exploration: NativeResearchExploration | None = None,
    ) -> None:
        self._store = store
        self._runner = occurrence_runner
        self._exploration = exploration

    @staticmethod
    def _request(
        *,
        session: ResearchSession,
        step: ResearchReasoningStep,
        task: ResearchInvestigationTask,
    ) -> NativeEngineRequest:
        conversation = session.native_conversation
        if conversation is None:
            raise ResearchManagerMaturationError(
                "P17_NATIVE_CONVERSATION_REQUIRED",
                "P17 follow-up requires the sealed Research native conversation",
            )
        request_id = f"p17-{step.step_id}-{task.task_id}"
        return NativeEngineRequest(
            profile_id=conversation.profile_id,
            metabot_id=conversation.metabot_id,
            message=task.bounded_objective,
            context={},
            conversation_id=conversation.conversation_id,
            history=None,
            state={},
            dima_request_id=request_id,
            dima_trace_id=request_id + "-trace",
        )

    def _material_ref(
        self,
        *,
        session: ResearchSession,
        link_id,
        principal: Principal,
        native_session_token: str | None,
    ) -> tuple[str, ...]:
        if self._exploration is None:
            return ()
        lead = self._exploration.explore_followup(
            session_id=session.session_id,
            execution_link_id=link_id,
            principal=principal,
            native_session_token=native_session_token,
        )
        return (lead.lead_id,)

    def execute(
        self,
        *,
        session: ResearchSession,
        step: ResearchReasoningStep,
        task: ResearchInvestigationTask,
        principal: Principal,
        native_session_token: str | None,
    ) -> FollowupResult:
        obligation = ResearchManager.obligation(
            session,
            task.parent_obligation_id,
        )
        if obligation.state != ObligationState.VERIFIED:
            raise ResearchManagerMaturationError(
                "P17_PARENT_OBLIGATION_NOT_VERIFIED",
                task.parent_obligation_id,
            )
        if step.parent_obligation_id != task.parent_obligation_id:
            raise ResearchManagerMaturationError(
                "P17_STEP_TASK_OBLIGATION_MISMATCH",
                task.task_id,
            )

        request = self._request(
            session=session,
            step=step,
            task=task,
        )
        existing = self._store.execution_link_for_request(
            request.dima_request_id
        )
        created = existing is None
        link = self._store.begin_delegation(
            session=session,
            obligation_id=task.parent_obligation_id,
            dima_request_id=request.dima_request_id,
            dima_trace_id=request.dima_trace_id,
            native_conversation_id=request.conversation_id,
            execution_kind="P17_FOLLOWUP",
            reasoning_step_id=step.step_id,
            investigation_task_id=task.task_id,
        )

        if link.status == "VERIFIED":
            if not link.receipt_id or not link.evidence_id:
                raise ResearchManagerMaturationError(
                    "P17_VERIFIED_FOLLOWUP_PROVENANCE_INCOMPLETE",
                    str(link.id),
                )
            material_refs = self._material_ref(
                session=session,
                link_id=link.id,
                principal=principal,
                native_session_token=native_session_token,
            )
            return FollowupResult(
                native_execution_refs=(str(link.id),),
                material_refs=material_refs,
                evidence_refs=(link.evidence_id,),
            )

        if not created and link.native_query_id is None:
            raise ResearchManagerMaturationError(
                "P17_NATIVE_COGNITION_OUTCOME_UNKNOWN",
                (
                    "follow-up delegation exists without a captured native query; "
                    "unknown prior cognition is not replayed"
                ),
            )

        occurrence = self._runner.execute(
            session=session,
            principal=principal,
            obligation_id=task.parent_obligation_id,
            link=link,
            request=(request if created else None),
            native_session_token=native_session_token,
        )
        outcome = occurrence.outcome
        ResearchManager.check_evidence(
            session,
            task.parent_obligation_id,
            outcome.receipt,
            outcome.evidence,
        )
        link = self._store.mark_verified(
            occurrence.execution_link_id,
            receipt_id=outcome.receipt.receipt_id,
            evidence_id=outcome.evidence.artifact_id,
        )
        material_refs = self._material_ref(
            session=session,
            link_id=link.id,
            principal=principal,
            native_session_token=native_session_token,
        )
        return FollowupResult(
            native_execution_refs=(str(link.id),),
            material_refs=material_refs,
            evidence_refs=(outcome.evidence.artifact_id,),
        )
