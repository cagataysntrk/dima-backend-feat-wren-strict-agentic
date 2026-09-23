from __future__ import annotations

import json

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
        conversation_id="conv-1",
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
        assert "query" not in body
        assert "sql" not in body
        return httpx.Response(202, text="\n".join(stream_lines) + "\n")
    return httpx.MockTransport(handler)


def test_c2_request_requires_dima_correlation_ids():
    with pytest.raises(ValidationError):
        NativeEngineRequest(
            message="x",
            conversation_id="conv",
            dima_request_id="",
            dima_trace_id="trace",
        )


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
