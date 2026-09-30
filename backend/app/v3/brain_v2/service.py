"""Thin execution facade for the Brain V2 LangGraph runtime."""
from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver

from .activities import BrainActivities
from .graph import build_brain_v2_graph
from .state import BrainGraphState


class BrainV2Service:
    """Runs the graph while keeping checkpoint state operational-only."""

    def __init__(self, *, activities: BrainActivities, checkpointer=None) -> None:
        self._checkpointer = checkpointer or InMemorySaver()
        self._graph = build_brain_v2_graph(
            activities=activities,
            checkpointer=self._checkpointer,
        )

    @property
    def graph(self):
        return self._graph

    def run(self, state: BrainGraphState) -> BrainGraphState:
        result = self._graph.invoke(
            state.model_dump(mode="python"),
            config={"configurable": {"thread_id": state.thread_id}},
        )
        return BrainGraphState.model_validate(result)
