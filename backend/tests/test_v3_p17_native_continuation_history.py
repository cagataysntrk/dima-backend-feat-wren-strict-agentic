from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.v3.research_product import NativeResearchOccurrenceRunner
from app.v3.research_store import ResearchPersistenceError
from app.v3.substrate.metabase.native_models import NativeEngineRequest


CONVERSATION_ID = UUID("00000000-0000-4000-8000-000000000701")
LINK_ID = UUID("00000000-0000-4000-8000-000000000702")


class StopAfterInvoke(RuntimeError):
    pass


class FakeStore:
    def __init__(self, state: dict) -> None:
        self.state = state
        self.calls = []

    def latest_verified_agent_state(
        self,
        *,
        session_id,
        obligation_id,
        native_conversation_id,
    ):
        self.calls.append(
            (session_id, obligation_id, native_conversation_id)
        )
        return self.state, "state-fingerprint"


class FakeBridge:
    def __init__(self, history) -> None:
        self.history = history
        self.history_calls = []
        self.invoked = []

    def conversation_history(self, conversation_id):
        self.history_calls.append(conversation_id)
        return self.history

    def invoke(self, request):
        self.invoked.append(request)
        raise StopAfterInvoke("captured request")


class FakeBridgeFactory:
    def __init__(self, bridge) -> None:
        self.bridge = bridge

    def open(self, **kwargs):
        del kwargs
        return nullcontext(self.bridge)


class BombMaterialExecutor:
    def execute(self, **kwargs):
        del kwargs
        raise AssertionError("material execution must not run in continuation wiring test")


def runner(*, state, history):
    bridge = FakeBridge(history)
    store = FakeStore(state)
    return (
        NativeResearchOccurrenceRunner(
            store=store,
            bridge_factory=FakeBridgeFactory(bridge),
            material_executor=BombMaterialExecutor(),
        ),
        store,
        bridge,
    )


def link():
    return SimpleNamespace(
        id=LINK_ID,
        native_query_id=None,
        execution_kind="P17_FOLLOWUP",
        native_conversation_id=CONVERSATION_ID,
    )


def request(**updates):
    values = {
        "message": "Run one discriminating governed follow-up.",
        "conversation_id": CONVERSATION_ID,
        "dima_request_id": "req-p17-followup",
        "dima_trace_id": "trace-p17-followup",
    }
    values.update(updates)
    return NativeEngineRequest(**values)


def test_p17_followup_binds_verified_state_and_source_backed_history_ephemerally():
    state = {
        "queries": {"q-parent": {"database": 1, "type": "query", "query": {}}},
        "charts": {},
    }
    history = [
        {"role": "user", "content": "Initial governed question."},
        {"role": "assistant", "content": "I inspected the governed material."},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "tool-parent",
                    "name": "construct_notebook_query",
                    "arguments": "{}",
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "tool-parent",
            "content": "{\"query-id\":\"q-parent\"}",
        },
    ]
    occurrence, store, bridge = runner(state=state, history=history)

    with pytest.raises(StopAfterInvoke):
        occurrence.execute(
            session=SimpleNamespace(session_id="research-session-1"),
            principal=SimpleNamespace(),
            obligation_id="goal-1",
            link=link(),
            request=request(),
            native_session_token="fixture-session",
        )

    assert store.calls == [
        ("research-session-1", "goal-1", CONVERSATION_ID)
    ]
    assert bridge.history_calls == [CONVERSATION_ID]
    assert len(bridge.invoked) == 1
    invoked = bridge.invoked[0]
    assert invoked.state == state
    assert invoked.history == history


@pytest.mark.parametrize(
    "updates",
    [
        {"state": {"queries": {}}},
        {"history": []},
        {"state": {"queries": {}}, "history": []},
    ],
)
def test_p17_followup_rejects_caller_supplied_continuation(updates):
    occurrence, store, bridge = runner(
        state={"queries": {"q-parent": {}}},
        history=[{"role": "user", "content": "prior"}],
    )

    with pytest.raises(ResearchPersistenceError) as exc:
        occurrence.execute(
            session=SimpleNamespace(session_id="research-session-1"),
            principal=SimpleNamespace(),
            obligation_id="goal-1",
            link=link(),
            request=request(**updates),
            native_session_token="fixture-session",
        )

    assert exc.value.code == "P17_NATIVE_CONTINUATION_CALLER_FORBIDDEN"
    assert store.calls == []
    assert bridge.history_calls == []
    assert bridge.invoked == []


def test_p17_followup_requires_nonempty_source_backed_history():
    occurrence, store, bridge = runner(
        state={"queries": {"q-parent": {}}},
        history=[],
    )

    with pytest.raises(ResearchPersistenceError) as exc:
        occurrence.execute(
            session=SimpleNamespace(session_id="research-session-1"),
            principal=SimpleNamespace(),
            obligation_id="goal-1",
            link=link(),
            request=request(),
            native_session_token="fixture-session",
        )

    assert exc.value.code == "P17_NATIVE_CONTINUATION_HISTORY_REQUIRED"
    assert store.calls
    assert bridge.history_calls == [CONVERSATION_ID]
    assert bridge.invoked == []
