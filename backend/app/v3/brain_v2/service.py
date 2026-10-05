"""Thin execution facade for the Brain V2 LangGraph runtime."""
from __future__ import annotations

import hashlib

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command

from .activities import BrainActivities
from .graph import DURABLE_OBSERVATION_RESUME, build_brain_v2_graph
from .state import BrainGraphState, BrainWorkflowStatus


class BrainV2ThreadError(RuntimeError):
    pass


class BrainV2Service:
    """Runs the graph while keeping checkpoint state operational-only."""

    def __init__(self, *, activities: BrainActivities, checkpointer=None) -> None:
        self._checkpointer = checkpointer or InMemorySaver(
            serde=JsonPlusSerializer(allowed_msgpack_modules=None)
        )
        self._graph = build_brain_v2_graph(
            activities=activities,
            checkpointer=self._checkpointer,
        )

    @property
    def graph(self):
        return self._graph

    @staticmethod
    def _config(thread_id: str) -> dict:
        if not str(thread_id or "").strip():
            raise BrainV2ThreadError("Brain V2 thread id is required")
        return {"configurable": {"thread_id": thread_id}}

    def state(self, *, thread_id: str) -> BrainGraphState | None:
        snapshot = self._graph.get_state(self._config(thread_id))
        values = getattr(snapshot, "values", None)
        if not values:
            return None
        return BrainGraphState.model_validate(values)

    @staticmethod
    def _assert_identity(
        state: BrainGraphState,
        *,
        tenant_binding: str,
        principal_ref: str,
    ) -> None:
        if (
            state.tenant_binding != tenant_binding
            or state.principal_ref != principal_ref
        ):
            raise BrainV2ThreadError(
                "Brain V2 thread is outside the current tenant/principal scope"
            )

    def _state_after_invoke(self, *, thread_id: str, result) -> BrainGraphState:
        if isinstance(result, dict) and "__interrupt__" in result:
            restored = self.state(thread_id=thread_id)
            if restored is None:
                raise BrainV2ThreadError("Brain V2 interrupted state was not checkpointed")
            return restored
        return BrainGraphState.model_validate(result)

    def run(self, state: BrainGraphState) -> BrainGraphState:
        result = self._graph.invoke(
            state.model_dump(mode="python"),
            config=self._config(state.thread_id),
        )
        return self._state_after_invoke(thread_id=state.thread_id, result=result)

    def continue_turn(
        self,
        *,
        thread_id: str,
        tenant_binding: str,
        principal_ref: str,
        user_input: str,
    ) -> BrainGraphState:
        """Start one new user turn from the latest durable orchestration state."""

        prior = self.state(thread_id=thread_id)
        if prior is None:
            raise BrainV2ThreadError("Brain V2 thread does not exist")
        self._assert_identity(
            prior,
            tenant_binding=tenant_binding,
            principal_ref=principal_ref,
        )
        if prior.workflow_status not in {
            BrainWorkflowStatus.COMPLETE,
            BrainWorkflowStatus.INCONCLUSIVE,
            BrainWorkflowStatus.BLOCKED,
        }:
            raise BrainV2ThreadError(
                "Brain V2 thread is not terminal; resume interrupted execution first"
            )
        current = str(user_input or "").strip()
        if not current:
            raise BrainV2ThreadError("Brain V2 current user input is required")

        result = self._graph.invoke(
            {
                "thread_id": thread_id,
                "tenant_binding": tenant_binding,
                "principal_ref": principal_ref,
                "current_user_input": current,
                "workflow_status": BrainWorkflowStatus.NEW,
            },
            config=self._config(thread_id),
        )
        return self._state_after_invoke(thread_id=thread_id, result=result)

    def continue_report_turn(
        self,
        *,
        thread_id: str,
        tenant_binding: str,
        principal_ref: str,
        user_input: str,
    ) -> BrainGraphState:
        """Run one typed presentation-only continuation on the current authority.

        This path cannot invoke intake, mutate Research/Scope, or reopen native
        analytics. The user-facing/API layer chooses this explicit action; the
        LangGraph still owns completion -> P20 -> completion routing.
        """

        prior = self.state(thread_id=thread_id)
        if prior is None:
            raise BrainV2ThreadError("Brain V2 thread does not exist")
        self._assert_identity(
            prior,
            tenant_binding=tenant_binding,
            principal_ref=principal_ref,
        )
        if prior.workflow_status not in {
            BrainWorkflowStatus.COMPLETE,
            BrainWorkflowStatus.INCONCLUSIVE,
        }:
            raise BrainV2ThreadError(
                "Brain V2 presentation continuation requires terminal analytical state"
            )
        analytical = set(
            (
                *prior.direct_requirement_ids,
                *prior.relationship_requirement_ids,
                *prior.root_cause_requirement_ids,
            )
        )
        if not analytical.issubset(set(prior.terminal_requirement_ids)):
            raise BrainV2ThreadError(
                "Brain V2 presentation continuation cannot bypass open analytics"
            )
        current = str(user_input or "").strip()
        if not current:
            raise BrainV2ThreadError("Brain V2 presentation request is required")
        next_revision = prior.presentation_revision + 1
        raw = (
            f"{thread_id}\x1f{next_revision}\x1f{current}"
        ).encode("utf-8")
        requirement_id = "d_report_" + hashlib.sha256(raw).hexdigest()[:24]

        result = self._graph.invoke(
            {
                "thread_id": thread_id,
                "tenant_binding": tenant_binding,
                "principal_ref": principal_ref,
                "current_user_input": None,
                "open_requirement_ids": tuple(
                    dict.fromkeys((*prior.open_requirement_ids, requirement_id))
                ),
                "report_requirement_ids": tuple(
                    dict.fromkeys((*prior.report_requirement_ids, requirement_id))
                ),
                "presentation_revision": next_revision,
                "report_ref": None,
                "workflow_status": BrainWorkflowStatus.RUNNING,
                "last_completed_node": "PRESENTATION_REQUEST",
            },
            config=self._config(thread_id),
        )
        return self._state_after_invoke(thread_id=thread_id, result=result)

    def resume_waiting(
        self,
        *,
        thread_id: str,
        tenant_binding: str,
        principal_ref: str,
    ) -> BrainGraphState:
        """Resume one retryable material-observation wait on the same thread."""

        config = self._config(thread_id)
        snapshot = self._graph.get_state(config)
        values = getattr(snapshot, "values", None)
        if not values:
            raise BrainV2ThreadError("Brain V2 thread does not exist")
        prior = BrainGraphState.model_validate(values)
        self._assert_identity(
            prior,
            tenant_binding=tenant_binding,
            principal_ref=principal_ref,
        )
        if prior.workflow_status != BrainWorkflowStatus.WAITING:
            raise BrainV2ThreadError("Brain V2 thread is not waiting for durable observation")
        expected_pending = (
            "wait_material_group"
            if prior.last_completed_node == "MATERIAL_GROUP_WAITING"
            else "wait_material"
            if prior.last_completed_node == "MATERIAL_WAITING"
            else None
        )
        if expected_pending is None:
            raise BrainV2ThreadError(
                "Brain V2 WAITING state has no resumable material boundary"
            )
        pending = tuple(getattr(snapshot, "next", ()) or ())
        if pending != (expected_pending,):
            raise BrainV2ThreadError(
                "Brain V2 WAITING checkpoint does not expose the expected resume boundary"
            )

        result = self._graph.invoke(
            Command(resume=DURABLE_OBSERVATION_RESUME),
            config=config,
        )
        resumed = self._state_after_invoke(thread_id=thread_id, result=result)
        self._assert_identity(
            resumed,
            tenant_binding=tenant_binding,
            principal_ref=principal_ref,
        )
        if resumed.thread_id != prior.thread_id:
            raise BrainV2ThreadError("Brain V2 durable resume changed thread identity")
        if resumed.research_session_id != prior.research_session_id:
            raise BrainV2ThreadError("Brain V2 durable resume changed Research identity")
        if resumed.scope_version_id != prior.scope_version_id:
            raise BrainV2ThreadError("Brain V2 durable resume changed scope version")
        return resumed

    def resume_interrupted(
        self,
        *,
        thread_id: str,
        tenant_binding: str,
        principal_ref: str,
    ) -> BrainGraphState:
        """Resume pending graph work without manufacturing a new user turn."""

        config = self._config(thread_id)
        snapshot = self._graph.get_state(config)
        values = getattr(snapshot, "values", None)
        if not values:
            raise BrainV2ThreadError("Brain V2 thread does not exist")
        prior = BrainGraphState.model_validate(values)
        self._assert_identity(
            prior,
            tenant_binding=tenant_binding,
            principal_ref=principal_ref,
        )
        if prior.workflow_status == BrainWorkflowStatus.WAITING:
            raise BrainV2ThreadError(
                "Brain V2 durable material wait requires resume_waiting()"
            )
        pending = tuple(getattr(snapshot, "next", ()) or ())
        if not pending:
            return prior

        result = self._graph.invoke(None, config=config)
        return self._state_after_invoke(thread_id=thread_id, result=result)
