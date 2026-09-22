from __future__ import annotations

import inspect
import json

import httpx
import pytest

from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_errors import FastMetabaseError, FastMetabaseErrorCode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import (
    ConstructedQuery,
    ContinuationToken,
    FastMetabaseRuntimePolicy,
)


def auth(mode: FastMetabaseAuthMode = FastMetabaseAuthMode.SESSION):
    return FastMetabaseAuthContext(
        tenant_id="tenant-a",
        dima_user_id="user-a",
        principal_id="metabase-user-1",
        mode=mode,
        secret="super-secret-value",
        role_scope_digest="role-scope-v1",
    )


def policy():
    return FastMetabaseRuntimePolicy(
        max_page_rows=200,
        max_total_rows_per_run=1000,
    )


def gateway(handler, *, mode=FastMetabaseAuthMode.SESSION, retries=0):
    return FastMetabaseGateway(
        base_url="http://metabase.test",
        auth=auth(mode),
        policy=policy(),
        transport=httpx.MockTransport(handler),
        max_transport_retries=retries,
    )


def probe():
    return {
        "lib/type": "mbql/query",
        "stages": [{
            "lib/type": "mbql.stage/mbql",
            "source-table": ["Lab", "public", "orders"],
            "limit": 1,
        }],
    }


def completed(*, rows=0, token=None):
    body = {
        "status": "completed",
        "data": {"cols": [], "rows": []},
        "row_count": rows,
        "running_time": 1,
    }
    if token is not None:
        body["continuation_token"] = token
    return body


def test_public_surface_has_no_raw_sql_admin_or_semantic_methods():
    public = {
        name
        for name, value in inspect.getmembers(FastMetabaseGateway)
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
        "interpret_user_language",
    }
    assert not (public & forbidden)

    source = inspect.getsource(FastMetabaseGateway)
    assert "app.v3" not in source
    assert "app.v2" not in source
    assert "wren" not in source.lower()


def test_access_fingerprint_is_stable_and_excludes_secret():
    ctx = auth()
    first = ctx.access_fingerprint()
    second = ctx.access_fingerprint()

    assert first.digest == second.digest
    assert first.tenant_id == "tenant-a"
    assert "super-secret-value" not in repr(ctx)
    assert "super-secret-value" not in first.model_dump_json()
    assert "super-secret-value" not in first.digest


@pytest.mark.parametrize(
    ("mode", "header"),
    [
        (FastMetabaseAuthMode.SESSION, "x-metabase-session"),
        (FastMetabaseAuthMode.API_KEY, "x-api-key"),
    ],
)
def test_auth_header_contract(mode, header):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers[header] == "super-secret-value"
        return httpx.Response(200, json={"status": "ok"})

    with gateway(handler, mode=mode) as client:
        assert client.health() is True


def test_serialized_query_and_continuation_are_distinct():
    query = ConstructedQuery(serialized_query="serialized")
    token = ContinuationToken(token="continuation")
    assert not hasattr(query, "token")
    assert not hasattr(token, "serialized_query")


def test_happy_transport_search_read_construct_execute_query_and_handshake():
    resource_uri = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/api/health":
            return httpx.Response(200, json={"status": "ok"})
        if path == "/api/agent/v1/ping":
            return httpx.Response(200, json={"message": "pong"})
        if path == "/api/agent/v1/search":
            return httpx.Response(200, json={
                "data": [{"type": "table", "name": "orders", "database_id": 1}],
                "total_count": 1,
            })
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
            return httpx.Response(202, json=completed())
        if path == "/api/agent/v2/query":
            return httpx.Response(202, json=completed())
        raise AssertionError(path)

    with gateway(handler) as client:
        found = client.search(term_queries=("orders",))
        assert found.total_count == 1
        resources = client.read_resource((resource_uri,))
        assert resources.resources[0].failed is False
        constructed = client.construct_query(probe())
        assert constructed.serialized_query == "serialized"
        executed = client.execute_serialized(constructed)
        assert executed.status.value == "completed"
        page = client.query(probe())
        assert page.status.value == "completed"

        handshake = client.startup_handshake(
            portable_probe_query=probe(),
            resource_probe_uri=resource_uri,
        )

    assert handshake.ready is True
    assert handshake.observed_page_limit == 200
    assert handshake.verified_operations == (
        "health",
        "agent_ping",
        "read_resource",
        "construct_query",
        "execute",
        "combined_query",
    )


def test_continuation_uses_token_only():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        seen.append(payload)
        if "query" in payload:
            return httpx.Response(202, json=completed(rows=200, token="next"))
        return httpx.Response(202, json=completed(rows=5))

    with gateway(handler) as client:
        first = client.query(probe())
        assert first.row_count == 200
        assert first.continuation is not None
        second = client.continue_query(first.continuation)

    assert second.row_count == 5
    assert seen[1] == {"continuation_token": "next"}


@pytest.mark.parametrize(
    ("status", "operation", "expected_code"),
    [
        (401, "agent_ping", FastMetabaseErrorCode.AUTH_FAILED),
        (403, "agent_ping", FastMetabaseErrorCode.PERMISSION_DENIED),
        (404, "read_resource", FastMetabaseErrorCode.RESOURCE_NOT_FOUND),
        (429, "agent_ping", FastMetabaseErrorCode.RATE_LIMITED),
        (503, "agent_ping", FastMetabaseErrorCode.METABASE_UNAVAILABLE),
        (400, "construct_query", FastMetabaseErrorCode.QUERY_CONSTRUCT_FAILED),
        (422, "combined_query", FastMetabaseErrorCode.QUERY_EXECUTION_FAILED),
    ],
)
def test_http_error_taxonomy(status, operation, expected_code):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "x"})

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            if operation == "construct_query":
                client.construct_query(probe())
            elif operation == "combined_query":
                client.query(probe())
            elif operation == "read_resource":
                client.read_resource(("metabase://database/1",))
            else:
                client.ping()

    assert exc.value.code == expected_code
    assert exc.value.status_code == status


def test_agent_disabled_is_not_permission_or_semantic_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": "Agent API is not enabled"})

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            client.ping()

    assert exc.value.code == FastMetabaseErrorCode.AGENT_API_DISABLED


def test_non_json_response_is_contract_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>oops</html>")

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            client.health()

    assert exc.value.code == FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED


def test_failed_202_body_is_not_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            202,
            json={"status": "failed", "error": "invalid query"},
        )

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            client.execute_serialized(ConstructedQuery(serialized_query="broken"))

    assert exc.value.code == FastMetabaseErrorCode.QUERY_EXECUTION_FAILED


def test_page_budget_violation_is_rejected():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(202, json=completed(rows=201))

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            client.query(probe())

    assert exc.value.code == FastMetabaseErrorCode.PAGINATION_INVALID


def test_read_resource_uri_mismatch_is_rejected():
    requested = "metabase://database/1"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "resources": [{
                "uri": "metabase://database/2",
                "content": {"structured-output": {"name": "Other"}},
            }],
            "output": "<resources>other</resources>",
        })

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            client.read_resource((requested,))

    assert exc.value.code == FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED


def test_timeout_is_typed():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    with gateway(handler) as client:
        with pytest.raises(FastMetabaseError) as exc:
            client.query(probe())

    assert exc.value.code == FastMetabaseErrorCode.DB_TIMEOUT


def test_transport_retry_is_bounded_for_retryable_operation():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503, json={"error": "busy"})
        return httpx.Response(200, json={"message": "pong"})

    with gateway(handler, retries=1) as client:
        assert client.ping() is True

    assert calls == 2
