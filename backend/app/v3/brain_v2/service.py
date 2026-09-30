"""Thin execution facade for the Brain V2 LangGraph runtime."""
from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from .activities import BrainActivities
from .graph import build_brain_v2_graph
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

    def run(self, state: BrainGraphState) -> BrainGraphState:
        result = self._graph.invoke(
            state.model_dump(mode="python"),
            config=self._config(state.thread_id),
        )
        return BrainGraphState.model_validate(result)

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
        return BrainGraphState.model_validate(result)

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
        pending = tuple(getattr(snapshot, "next", ()) or ())
        if not pending:
            return prior

        result = self._graph.invoke(None, config=config)
        return BrainGraphState.model_validate(result)
