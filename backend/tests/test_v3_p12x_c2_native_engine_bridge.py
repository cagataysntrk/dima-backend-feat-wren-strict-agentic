from __future__ import annotations

import json
from uuid import UUID

import httpx
import pytest
from pydantic import ValidationError

from app.v3.substrate.metabase.native_engine import (
    NativeEngineBridge,
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
        assert request.headers["X-Metabase-Session"] == "restricted-session"
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
        session_token="restricted-session",
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
        session_token="restricted-session",
        expected_identity=IDENTITY,
        transport=transport([], runtime_tag="v0.63.18"),
    ) as bridge:
        with pytest.raises(NativeEngineIdentityMismatch):
            bridge.invoke(req())


def test_c2_bridge_fails_closed_on_native_stream_error_and_keeps_observation():
    lines = ['3:{"message":"provider failed"}']
    with NativeEngineBridge(
        base_url="http://metabase",
        session_token="restricted-session",
        expected_identity=IDENTITY,
        transport=transport(lines),
    ) as bridge:
        with pytest.raises(NativeEngineStreamError) as exc:
            bridge.invoke(req())
    assert exc.value.observation.errors == ({"message": "provider failed"},)


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
        session_token="restricted-session",
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
        assert request.headers["X-Metabase-Session"] == "restricted-session"
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
        session_token="restricted-session",
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
