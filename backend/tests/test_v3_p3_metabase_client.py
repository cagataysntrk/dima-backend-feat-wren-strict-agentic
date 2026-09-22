from __future__ import annotations

import inspect

import httpx
import pytest

from app.v3.substrate.metabase.adapter import MetabaseRuntimeAdapter
from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.errors import MetabaseClientError, MetabaseErrorCode
from app.v3.substrate.metabase.models import (
    ConstructedQuery,
    ContinuationToken,
    MetabaseRuntimePolicy,
)


DIGEST = "sha256:" + "1" * 64


def policy():
    return MetabaseRuntimePolicy(
        runtime_version="v0.63.18",
        runtime_image_digest=DIGEST,
        raw_sql_policy="disabled",
        observed_page_size=200,
        observed_total_row_cap=2000,
    )


def client(handler):
    return MetabaseAgentClient(
        base_url="http://metabase.test",
        session_token="session-secret",
        policy=policy(),
        transport=httpx.MockTransport(handler),
    )


def _probe():
    return {
        "lib/type": "mbql/query",
        "stages": [{
            "lib/type": "mbql.stage/mbql",
            "source-table": ["Lab", "public", "orders"],
            "limit": 1,
        }],
    }


def test_public_surface_has_no_raw_sql_or_admin_content_mutation_methods():
    public = {
        name
        for name, value in inspect.getmembers(MetabaseAgentClient)
        if not name.startswith("_") and callable(value)
    }
    forbidden = {
        "execute_sql",
        "raw_sql",
        "create_metric",
        "update_metric",
        "create_question",
        "update_question",
        "create_dashboard",
        "update_dashboard",
        "set_setting",
        "resolve_semantic_handle",
    }
    assert not (public & forbidden)

    adapter_source = inspect.getsource(MetabaseRuntimeAdapter)
    assert "ResolvedAnalyticsIntent" not in adapter_source
    assert "semantic_handle" not in adapter_source
    assert "app.v2" not in adapter_source


def test_serialized_query_and_continuation_are_distinct_contracts():
    query = ConstructedQuery(serialized_query="abc")
    token = ContinuationToken(token="def")
    assert query.model_fields.keys() == {"serialized_query"}
    assert token.model_fields.keys() == {"token"}
    assert not hasattr(query, "continuation_token")
    assert not hasattr(token, "serialized_query")
    assert "query_handle" not in query.model_fields
    assert "query_handle" not in token.model_fields


def test_happy_transport_and_handshake():
    resource_uri = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/health":
            return httpx.Response(200, json={"status": "ok"})
        if path == "/api/agent/v1/ping":
            return httpx.Response(200, json={"message": "pong"})
        if path == "/api/agent/v1/read-resource":
            return httpx.Response(200, json={
                "resources": [{
                    "uri": resource_uri,
                    "content": {
                        "structured-output": {
                            "result-type": "metabot-entity",
                            "name": "Lab",
                        }
                    },
                }],
                "output": "<resources>ok</resources>",
            })
        if path == "/api/agent/v2/construct-query":
            return httpx.Response(200, json={"query": "serialized"})
        if path == "/api/agent/v1/execute":
            return httpx.Response(202, json={
                "status": "completed",
                "data": {"cols": [], "rows": []},
                "row_count": 0,
                "running_time": 1,
            })
        if path == "/api/agent/v2/query":
            return httpx.Response(202, json={
                "status": "completed",
                "data": {"cols": [], "rows": []},
                "row_count": 0,
                "running_time": 1,
            })
        raise AssertionError(path)

    with client(handler) as c:
        handshake = MetabaseRuntimeAdapter(client=c).inspect_runtime(
            portable_probe_query=_probe(),
            resource_probe_uri=resource_uri,
        )

    assert handshake.ready is True
    assert handshake.agent_api_enabled is True
    assert handshake.read_resource is True
    assert "read_resource" in handshake.verified_operations
    assert handshake.api_surface == "REST_AGENT_API"
    assert handshake.raw_sql_policy == "disabled"
    assert handshake.observed_page_size == 200
    assert handshake.observed_total_row_cap == 2000


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (400, MetabaseErrorCode.QUERY_INVALID),
        (401, MetabaseErrorCode.AUTH),
        (403, MetabaseErrorCode.PERMISSION),
        (404, MetabaseErrorCode.RESOURCE_NOT_FOUND),
        (500, MetabaseErrorCode.INTERNAL),
    ],
)
def test_http_error_taxonomy(status, code):
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(status, json={"error": "x"})

    with client(handler) as c:
        with pytest.raises(MetabaseClientError) as exc:
            c.ping()
    assert exc.value.code == code
    assert exc.value.status_code == status


def test_healthy_process_does_not_mask_agent_permission_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/api/agent/v1/ping":
            return httpx.Response(403, json={"error": "Agent API is not enabled"})
        raise AssertionError(request.url.path)

    with client(handler) as c:
        assert c.health() is True
        with pytest.raises(MetabaseClientError) as exc:
            c.startup_handshake(
                portable_probe_query=_probe(),
                resource_probe_uri="metabase://database/1",
            )
    assert exc.value.code == MetabaseErrorCode.PERMISSION


def test_streaming_202_failed_body_is_not_treated_as_success():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/agent/v1/execute":
            return httpx.Response(
                202,
                json={"status": "failed", "error": "invalid query"},
            )
        raise AssertionError(request.url.path)

    with client(handler) as c:
        with pytest.raises(MetabaseClientError) as exc:
            c.execute_serialized(ConstructedQuery(serialized_query="broken"))
    assert exc.value.code == MetabaseErrorCode.QUERY_INVALID



def test_read_resource_parses_exact_structured_output_envelope():
    uri = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/agent/v1/read-resource"
        return httpx.Response(200, json={
            "resources": [{
                "uri": uri,
                "content": {
                    "structured-output": {
                        "result-type": "metabot-entity",
                        "name": "Dima Analytics Lab",
                    }
                },
            }],
            "output": "<resources>ok</resources>",
        })

    with client(handler) as c:
        response = c.read_resource((uri,))

    item = response.resources[0]
    assert item.uri == uri
    assert item.failed is False
    assert item.error is None
    assert item.content is not None
    assert item.content.structured_output is not None
    assert item.content.structured_output["name"] == "Dima Analytics Lab"


def test_read_resource_preserves_resource_level_error_on_http_200():
    uri = "metabase://database/999"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/agent/v1/read-resource"
        return httpx.Response(200, json={
            "resources": [{"uri": uri, "error": "resource unavailable"}],
            "output": "<resources>error</resources>",
        })

    with client(handler) as c:
        response = c.read_resource((uri,))

    item = response.resources[0]
    assert item.failed is True
    assert item.content is None
    assert item.error == "resource unavailable"


@pytest.mark.parametrize(
    "resource",
    [
        {"uri": "metabase://database/1"},
        {
            "uri": "metabase://database/1",
            "content": {"structured-output": {"name": "Lab"}},
            "error": "also failed",
        },
    ],
)
def test_read_resource_rejects_malformed_resource_state(resource):
    uri = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/agent/v1/read-resource"
        return httpx.Response(200, json={
            "resources": [resource],
            "output": "<resources>x</resources>",
        })

    with client(handler) as c:
        with pytest.raises(MetabaseClientError) as exc:
            c.read_resource((uri,))
    assert exc.value.code == MetabaseErrorCode.INTERNAL


def test_read_resource_rejects_uri_or_count_mismatch():
    requested = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/agent/v1/read-resource"
        return httpx.Response(200, json={
            "resources": [{
                "uri": "metabase://database/2",
                "content": {"structured-output": {"name": "Other"}},
            }],
            "output": "<resources>other</resources>",
        })

    with client(handler) as c:
        with pytest.raises(MetabaseClientError) as exc:
            c.read_resource((requested,))
    assert exc.value.code == MetabaseErrorCode.INTERNAL


def test_handshake_does_not_claim_read_resource_when_resource_item_failed():
    uri = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/health":
            return httpx.Response(200, json={"status": "ok"})
        if path == "/api/agent/v1/ping":
            return httpx.Response(200, json={"message": "pong"})
        if path == "/api/agent/v1/read-resource":
            return httpx.Response(200, json={
                "resources": [{"uri": uri, "error": "resource unavailable"}],
                "output": "<resources>error</resources>",
            })
        if path == "/api/agent/v2/construct-query":
            return httpx.Response(200, json={"query": "serialized"})
        if path in ("/api/agent/v1/execute", "/api/agent/v2/query"):
            return httpx.Response(202, json={
                "status": "completed",
                "data": {"cols": [], "rows": []},
                "row_count": 0,
                "running_time": 1,
            })
        raise AssertionError(path)

    with client(handler) as c:
        handshake = c.startup_handshake(
            portable_probe_query=_probe(),
            resource_probe_uri=uri,
        )

    assert handshake.ready is False
    assert handshake.read_resource is False
    assert "read_resource" not in handshake.verified_operations
