from __future__ import annotations

import json
from uuid import UUID

import httpx
import pytest
from pydantic import ValidationError

from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridge,
    NativeEngineBridgeError,
    NativeEngineIdentityMismatch,
    NativeEngineStreamError,
)
from app.v3.substrate.metabase.native_models import NativeEngineIdentity, NativeEngineRequest


IDENTITY = NativeEngineIdentity(
    engine_sha="6bb6924452e5b9dc42b3745bb88c3125a468b297",
    upstream_base_sha="2ba2485c78d7e00a9a25f82c00fc201da71590c4",
    runtime_tag="v0.63.18-dima.0",
)


def req() -> NativeEngineRequest:
    return NativeEngineRequest(
        message="Haziran 2026'da kaç satış siparişi açıldı?",
        conversation_id="00000000-0000-4000-8000-000000000001",
        dima_request_id="req-1",
        dima_trace_id="trace-1",
    )


def transport(stream_lines: list[str], *, runtime_tag: str = "v0.63.18-dima.0"):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Metabase-Session"] == "fixture-session"
        if request.url.path == "/api/session/properties":
            return httpx.Response(200, json={"version": {"tag": runtime_tag, "hash": "?"}})
        assert request.url.path == "/api/metabot/agent-streaming"
        body = json.loads(request.content)
        assert body["profile_id"] == "nlq"
        assert body["message"] == req().message
        assert body["conversation_id"] == "00000000-0000-4000-8000-000000000001"
        assert "query" not in body
        assert "sql" not in body
        return httpx.Response(202, text="\n".join(stream_lines) + "\n")
    return httpx.MockTransport(handler)


def test_c2_request_observer_receives_exact_native_http_paths():
    seen = []

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(['d:{"finishReason":"stop"}']),
        request_observer=lambda method, path: seen.append((method, path)),
    ) as bridge:
        bridge.invoke(req())

    assert seen == [
        ("GET", "/api/session/properties"),
        ("POST", "/api/metabot/agent-streaming"),
    ]
    assert all(not path.startswith("/api/agent") for _, path in seen)


def test_c2_request_requires_dima_correlation_ids():
    with pytest.raises(ValidationError):
        NativeEngineRequest(
            message="x",
            conversation_id="00000000-0000-4000-8000-000000000001",
            dima_request_id="",
            dima_trace_id="trace",
        )


def test_c2_request_rejects_non_uuid_native_conversation_id():
    with pytest.raises(ValidationError):
        NativeEngineRequest(
            message="x",
            conversation_id="not-a-native-uuid",
            dima_request_id="req",
            dima_trace_id="trace",
        )


def test_c2_request_normalizes_native_conversation_id_to_uuid():
    request = req()
    assert isinstance(request.conversation_id, UUID)
    assert str(request.conversation_id) == "00000000-0000-4000-8000-000000000001"



@pytest.mark.parametrize(
    ("chat_messages", "expected"),
    [
        (
            [
                {"id": "u1", "role": "user", "type": "text", "message": "Compare downtime."},
                {"id": "a1", "role": "agent", "type": "text", "message": "I will inspect it."},
                {
                    "id": "tool-1",
                    "role": "agent",
                    "type": "tool_call",
                    "name": "search",
                    "args": "{\"query\":\"downtime\"}",
                    "result": "{\"output\":\"found\"}",
                    "status": "ended",
                    "is_error": False,
                },
                {
                    "id": "d1",
                    "role": "agent",
                    "type": "data_part",
                    "part": {"type": "navigate_to", "version": 1, "value": "/question/1"},
                },
            ],
            [
                {"role": "user", "content": "Compare downtime."},
                {"role": "assistant", "content": "I will inspect it."},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "tool-1",
                            "name": "search",
                            "arguments": "{\"query\":\"downtime\"}",
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "tool-1", "content": "{\"output\":\"found\"}"},
            ],
        ),
        (
            [
                {"id": "u2", "role": "user", "type": "text", "message": "Use prior query."},
                {
                    "id": "tool-2",
                    "role": "agent",
                    "type": "tool_call",
                    "name": "construct_notebook_query",
                    "args": "{}",
                    "result": "{\"query-id\":\"q2\"}",
                    "status": "ended",
                    "is_error": False,
                },
            ],
            [
                {"role": "user", "content": "Use prior query."},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "tool-2",
                            "name": "construct_notebook_query",
                            "arguments": "{}",
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "tool-2", "content": "{\"query-id\":\"q2\"}"},
            ],
        ),
    ],
)
def test_c2_source_backed_conversation_history_projects_losslessly(chat_messages, expected):
    conversation_id = "00000000-0000-4000-8000-000000000001"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Metabase-Session"] == "fixture-session"
        if request.url.path == "/api/session/properties":
            return httpx.Response(200, json={"version": {"tag": IDENTITY.runtime_tag}})
        if request.url.path == f"/api/metabot/conversations/{conversation_id}":
            return httpx.Response(
                200,
                json={
                    "conversation_id": conversation_id,
                    "chat_messages": chat_messages,
                },
            )
        return httpx.Response(599)

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=httpx.MockTransport(handler),
    ) as bridge:
        history = bridge.conversation_history(UUID(conversation_id))

    assert history == expected


def test_c2_source_backed_conversation_history_fails_closed_on_tool_error():
    conversation_id = "00000000-0000-4000-8000-000000000001"

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == f"/api/metabot/conversations/{conversation_id}":
            return httpx.Response(
                200,
                json={
                    "conversation_id": conversation_id,
                    "chat_messages": [
                        {
                            "id": "tool-err",
                            "role": "agent",
                            "type": "tool_call",
                            "name": "search",
                            "args": "{}",
                            "result": "{\"message\":\"boom\"}",
                            "status": "ended",
                            "is_error": True,
                        }
                    ],
                },
            )
        return httpx.Response(599)

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=httpx.MockTransport(handler),
    ) as bridge:
        with pytest.raises(Exception, match="errored tool"):
            bridge.conversation_history(UUID(conversation_id))


def test_c2_bridge_preserves_ordered_native_stream_and_final_state():
    lines = [
        'f:{"messageId":"m1"}',
        '9:{"toolName":"search"}',
        'a:{"ok":true}',
        '2:{"type":"state","value":{"query-id":"q1"}}',
        '0:"126"',
        'd:{"finishReason":"stop"}',
    ]
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(lines),
    ) as bridge:
        out = bridge.invoke(req())

    assert [x.raw_line for x in out.events] == lines
    assert out.text_parts == ("126",)
    assert out.tool_calls[0]["toolName"] == "search"
    assert out.final_state == {"query-id": "q1"}
    assert out.runtime_version["tag"] == "v0.63.18-dima.0"


def test_c2_bridge_fails_closed_on_runtime_identity_mismatch():
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport([], runtime_tag="v0.63.18"),
    ) as bridge:
        with pytest.raises(NativeEngineIdentityMismatch):
            bridge.invoke(req())


def test_c2_bridge_fails_closed_on_native_stream_error_and_keeps_observation():
    lines = ['3:{"message":"provider failed"}']
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(lines),
    ) as bridge:
        with pytest.raises(NativeEngineStreamError) as exc:
            bridge.invoke(req())
    assert exc.value.observation.errors == ({"message": "provider failed"},)



def test_c2_bridge_consumes_natural_terminal_stream_after_generated_query_artifact():
    query = {
        "database": 1,
        "type": "query",
        "query": {
            "source-table": 10,
            "aggregation": [["count"]],
        },
    }
    generated = {
        "type": "generated_entity",
        "value": {"query": {"id": "q-stop", "query": query}},
    }
    finish = {"finishReason": "terminal-tool"}
    lines = [
        "2:" + json.dumps(generated, separators=(",", ":")),
        "d:" + json.dumps(finish, separators=(",", ":")),
    ]

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(lines),
    ) as bridge:
        observation = bridge.invoke(req())
        produced = bridge.capture_produced_query(observation)

    assert produced.native_query_id == "q-stop"
    assert produced.query == query
    assert produced.source == "generated_entity"
    assert observation.errors == ()
    assert [event.prefix for event in observation.events] == ["2", "d"]
    assert observation.finish_parts == (finish,)


def test_c2_continued_turn_rejects_prior_state_query_as_new_acquisition():
    prior_query = {
        "database": 1,
        "type": "query",
        "query": {"source-table": 10, "aggregation": [["count"]]},
    }
    prior_state = {"queries": {"q-prior": prior_query}}
    state_part = {
        "type": "state",
        "value": {"queries": {"q-prior": prior_query}},
    }
    request = req().model_copy(update={"state": prior_state})
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(
            [
                "2:" + json.dumps(state_part, separators=(",", ":")),
                'd:{"finishReason":"stop"}',
            ]
        ),
    ) as bridge:
        observation = bridge.invoke(request)
        with pytest.raises(
            NativeEngineBridgeError,
            match="new executable query",
        ):
            bridge.capture_produced_query(
                observation,
                prior_state=request.state,
            )


def test_c2_continued_turn_state_fallback_accepts_exactly_one_new_query_id():
    prior_query = {
        "database": 1,
        "type": "query",
        "query": {"source-table": 10, "aggregation": [["count"]]},
    }
    new_query = {
        "database": 1,
        "type": "query",
        "query": {
            "source-table": 10,
            "aggregation": [["sum", ["field", 7, None]]],
        },
    }
    prior_state = {"queries": {"q-prior": prior_query}}
    final_state = {
        "queries": {
            "q-prior": prior_query,
            "q-new": new_query,
        }
    }
    request = req().model_copy(update={"state": prior_state})
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(
            [
                "2:"
                + json.dumps(
                    {"type": "state", "value": final_state},
                    separators=(",", ":"),
                ),
                'd:{"finishReason":"stop"}',
            ]
        ),
    ) as bridge:
        observation = bridge.invoke(request)
        produced = bridge.capture_produced_query(
            observation,
            prior_state=request.state,
        )

    assert produced.native_query_id == "q-new"
    assert produced.query == new_query
    assert produced.source == "state"


def test_c2_fresh_turn_state_fallback_preserves_single_query_capture():
    query = {
        "database": 1,
        "type": "query",
        "query": {"source-table": 10, "aggregation": [["count"]]},
    }
    final_state = {"queries": {"q-fresh": query}}
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=transport(
            [
                "2:"
                + json.dumps(
                    {"type": "state", "value": final_state},
                    separators=(",", ":"),
                ),
                'd:{"finishReason":"stop"}',
            ]
        ),
    ) as bridge:
        observation = bridge.invoke(req())
        produced = bridge.capture_produced_query(
            observation,
            prior_state={},
        )

    assert produced.native_query_id == "q-fresh"
    assert produced.query == query
    assert produced.source == "state"


def test_c2_bridge_has_no_agent_api_wren_or_raw_sql_fallback():
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path == "/api/session/properties":
            return httpx.Response(200, json={"version": {"tag": "v0.63.18-dima.0"}})
        if request.url.path == "/api/metabot/agent-streaming":
            return httpx.Response(202, text='0:"ok"\n')
        return httpx.Response(599)

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=httpx.MockTransport(handler),
    ) as bridge:
        bridge.invoke(req())

    assert requested == ["/api/session/properties", "/api/metabot/agent-streaming"]
    assert all("/api/agent/" not in path for path in requested)


def test_p13d_transport_executes_only_server_side_occurrence_identity():
    query = {
        "lib/type": "mbql/query",
        "database": 1,
        "stages": [{"lib/type": "mbql.stage/mbql", "source-table": 10}],
    }
    fingerprint = "a" * 64
    attestation_id = "dima_att_exact_occurrence"
    conversation_id = "00000000-0000-4000-8000-000000000201"
    identity = {
        "repository": "UpcyTech/dima-metabase-engine",
        "revision_sha": "cbe313af9ac2d5960f662068e433d328d896fb06",
        "upstream_base_sha": "2ba2485c78d7e00a9a25f82c00fc201da71590c4",
        "runtime_tag": "v0.63.18-dima.6",
        "build_identity": "github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06",
        "image_identity": "sha256:" + "4" * 64,
        "runtime_instance_id": "00000000-0000-4000-8000-000000000131",
    }
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Metabase-Session"] == "fixture-session"
        body = json.loads(request.content) if request.content else None
        requested.append((request.url.path, body))
        if request.url.path == "/api/dima/engine/v1/identity":
            return httpx.Response(200, json=identity)
        if request.url.path == "/api/dima/engine/v1/native-query-attestation":
            assert body == {
                "conversation_id": conversation_id,
                "native_query_id": "native-px01",
            }
            return httpx.Response(
                200,
                json={
                    "exact_serialized_pmbql": query,
                    "manifest": {
                        "native_query_id": "native-px01",
                        "attestation_id": attestation_id,
                        "exact_pmbql_fingerprint": fingerprint,
                    },
                },
            )
        if request.url.path == "/api/dima/engine/v1/native-query-execution":
            assert body == {
                "conversation_id": conversation_id,
                "native_query_id": "native-px01",
                "expected_pmbql_fingerprint": fingerprint,
                "expected_attestation_id": attestation_id,
            }
            assert "query" not in body
            assert "exact_serialized_pmbql" not in body
            return httpx.Response(
                200,
                json={
                    "native_conversation_id": conversation_id,
                    "native_query_id": "native-px01",
                    "attestation_id": attestation_id,
                    "executed_pmbql_fingerprint": fingerprint,
                    "runtime_identity": identity,
                    "result": {"status": "completed", "data": {"rows": [[126]]}},
                    "attestation": {
                        "exact_serialized_pmbql": query,
                        "manifest": {
                            "native_query_id": "native-px01",
                            "attestation_id": attestation_id,
                            "exact_pmbql_fingerprint": fingerprint,
                        },
                    },
                },
            )
        return httpx.Response(599)

    expected = NativeEngineIdentity(
        engine_sha=identity["revision_sha"],
        upstream_base_sha=identity["upstream_base_sha"],
        runtime_tag=identity["runtime_tag"],
    )
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=expected,
        transport=httpx.MockTransport(handler),
    ) as client:
        assert client.engine_identity() == identity
        envelope = client.attest_native_query(
            conversation_id=UUID(conversation_id),
            native_query_id="native-px01",
        )
        assert envelope["exact_serialized_pmbql"] == query
        execution = client.execute_native_query(
            conversation_id=UUID(conversation_id),
            native_query_id="native-px01",
            expected_pmbql_fingerprint=fingerprint,
            expected_attestation_id=attestation_id,
        )

    assert execution.status_code == 200
    assert execution.payload["data"]["rows"] == [[126]]
    assert execution.executed_pmbql_fingerprint == fingerprint
    assert execution.attestation_id == attestation_id
    assert [path for path, _ in requested] == [
        "/api/dima/engine/v1/identity",
        "/api/dima/engine/v1/native-query-attestation",
        "/api/dima/engine/v1/native-query-execution",
    ]
    assert all("/api/dataset" not in path for path, _ in requested)
    assert all("/api/agent/" not in path for path, _ in requested)


def test_native_direct_metabot_query_reaches_dataset_unchanged():
    query = {
        "database": 1,
        "type": "query",
        "query": {
            "source-table": 10,
            "aggregation": [["count"]],
        },
    }
    query_id = "native-direct-q1"
    generated = {
        "type": "generated_entity",
        "value": {"query": {"id": query_id, "query": query}},
    }
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Metabase-Session"] == "fixture-session"
        requested.append(request.url.path)
        if request.url.path == "/api/session/properties":
            return httpx.Response(
                200,
                json={"version": {"tag": "v0.63.18-dima.0"}},
            )
        if request.url.path == "/api/metabot/agent-streaming":
            return httpx.Response(
                202,
                text=(
                    "2:"
                    + json.dumps(generated, separators=(",", ":"))
                    + "\n"
                    + 'd:{"finishReason":"stop"}\n'
                ),
            )
        if request.url.path == "/api/dataset":
            assert json.loads(request.content) == query
            return httpx.Response(
                202,
                json={
                    "status": "completed",
                    "database_id": 1,
                    "row_count": 1,
                    "data": {"rows": [[126]], "cols": []},
                },
            )
        return httpx.Response(599)

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=httpx.MockTransport(handler),
    ) as bridge:
        observation = bridge.invoke(req())
        produced = bridge.capture_produced_query(observation)
        result = bridge.execute_dataset(produced.query)

    assert produced.native_query_id == query_id
    assert produced.query == query
    assert produced.source == "generated_entity"
    assert result.query_fingerprint == produced.query_fingerprint
    assert result.payload["data"]["rows"] == [[126]]
    assert requested == [
        "/api/session/properties",
        "/api/metabot/agent-streaming",
        "/api/dataset",
    ]


def test_native_direct_dataset_permission_failure_stays_native_http_failure():
    from app.v3.substrate.metabase.native_engine import NativeDatasetExecutionError

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Metabase-Session"] == "fixture-session"
        assert request.url.path == "/api/dataset"
        return httpx.Response(
            403,
            json={"message": "You do not have permissions to run this query."},
        )

    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="fixture-session",
        expected_identity=IDENTITY,
        transport=httpx.MockTransport(handler),
    ) as bridge:
        with pytest.raises(NativeDatasetExecutionError) as exc:
            bridge.execute_dataset({"database": 1, "type": "query", "query": {}})
    assert exc.value.status_code == 403
    assert "permissions" in exc.value.detail
