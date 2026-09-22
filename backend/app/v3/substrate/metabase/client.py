"""Version-aware REST/Agent API client for Metabase v3 substrate work.

This client owns HTTP transport only. It does not accept raw user language, resolve Dima
semantic handles, author SQL, or mutate Metabase semantic/content resources.
"""

from __future__ import annotations

import time
from typing import Any, Iterable

import httpx

from app.v3.substrate.metabase.errors import MetabaseClientError, MetabaseErrorCode
from app.v3.substrate.metabase.models import (
    ConstructedQuery,
    ContinuationToken,
    ExecutionStatus,
    MetabaseCapabilityHandshake,
    MetabaseExecutionResponse,
    MetabaseQueryPage,
    MetabaseRuntimePolicy,
    ReadResourceResponse,
    SearchResponse,
)
from app.v3.substrate.metabase.telemetry import (
    MetabaseTelemetryEvent,
    MetabaseTelemetrySink,
    NullMetabaseTelemetry,
)


class MetabaseAgentClient:
    """Authenticated REST Agent API transport.

    Session identity is injected by the caller. P3 deliberately does not own password login,
    tenant mapping, impersonation, or API-key provisioning.
    """

    def __init__(
        self,
        *,
        base_url: str,
        session_token: str,
        policy: MetabaseRuntimePolicy,
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        telemetry: MetabaseTelemetrySink | None = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("Metabase base_url is required")
        if not session_token.strip():
            raise ValueError("Metabase session token is required")
        self._base_url = base_url.rstrip("/")
        self._session_token = session_token
        self._policy = policy
        self._telemetry = telemetry or NullMetabaseTelemetry()
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout_seconds,
            transport=transport,
            headers={
                "Accept": "application/json",
                "X-Metabase-Session": session_token,
            },
        )

    @property
    def policy(self) -> MetabaseRuntimePolicy:
        return self._policy

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "MetabaseAgentClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb
        self.close()

    def _emit(
        self,
        *,
        operation: str,
        started: float,
        ok: bool,
        status_code: int | None = None,
        error_code: str | None = None,
    ) -> None:
        self._telemetry.emit(
            MetabaseTelemetryEvent(
                operation=operation,
                ok=ok,
                status_code=status_code,
                duration_ms=max(0, int((time.monotonic() - started) * 1000)),
                error_code=error_code,
            )
        )

    @staticmethod
    def _decode(response: httpx.Response) -> Any:
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise MetabaseClientError(
                code=MetabaseErrorCode.INTERNAL,
                operation="decode_response",
                message="Metabase returned non-JSON response",
                status_code=response.status_code,
                body=response.text[:1000],
            ) from exc

    def _request(
        self,
        method: str,
        path: str,
        *,
        operation: str,
        payload: dict[str, Any] | None = None,
        expected: Iterable[int] = (200,),
    ) -> Any:
        started = time.monotonic()
        try:
            response = self._client.request(method, path, json=payload)
        except httpx.TimeoutException as exc:
            self._emit(
                operation=operation,
                started=started,
                ok=False,
                error_code=MetabaseErrorCode.TIMEOUT.value,
            )
            raise MetabaseClientError(
                code=MetabaseErrorCode.TIMEOUT,
                operation=operation,
                message="Metabase request timed out",
            ) from exc
        except httpx.RequestError as exc:
            self._emit(
                operation=operation,
                started=started,
                ok=False,
                error_code=MetabaseErrorCode.TRANSPORT.value,
            )
            raise MetabaseClientError(
                code=MetabaseErrorCode.TRANSPORT,
                operation=operation,
                message=str(exc),
            ) from exc

        body = self._decode(response)
        if response.status_code not in set(expected):
            error = MetabaseClientError.from_http(
                operation=operation,
                status_code=response.status_code,
                body=body,
            )
            self._emit(
                operation=operation,
                started=started,
                ok=False,
                status_code=response.status_code,
                error_code=error.code.value,
            )
            raise error

        self._emit(
            operation=operation,
            started=started,
            ok=True,
            status_code=response.status_code,
        )
        return body

    @staticmethod
    def _execution(
        body: Any,
        *,
        operation: str,
        page: bool = False,
    ) -> MetabaseExecutionResponse | MetabaseQueryPage:
        if not isinstance(body, dict):
            raise MetabaseClientError(
                code=MetabaseErrorCode.INTERNAL,
                operation=operation,
                message="Metabase execution response is not an object",
                body=body,
            )
        status = str(body.get("status") or "")
        if status == ExecutionStatus.FAILED.value:
            raise MetabaseClientError(
                code=MetabaseErrorCode.QUERY_INVALID,
                operation=operation,
                message=str(body.get("error") or "Metabase query execution failed"),
                body=body,
            )
        if status != ExecutionStatus.COMPLETED.value:
            raise MetabaseClientError(
                code=MetabaseErrorCode.INTERNAL,
                operation=operation,
                message=f"unexpected execution status {status!r}",
                body=body,
            )

        common = {
            "status": status,
            "data": body.get("data") or {},
            "row_count": int(body.get("row_count") or 0),
            "running_time": body.get("running_time"),
            "error": None,
        }
        if page:
            token = body.get("continuation_token")
            return MetabaseQueryPage(
                **common,
                continuation=(
                    ContinuationToken(token=str(token))
                    if token
                    else None
                ),
            )
        return MetabaseExecutionResponse(**common)

    def health(self) -> bool:
        body = self._request(
            "GET",
            "/api/health",
            operation="health",
            expected=(200,),
        )
        return isinstance(body, dict)

    def ping(self) -> bool:
        body = self._request(
            "GET",
            "/api/agent/v1/ping",
            operation="agent_ping",
            expected=(200,),
        )
        return isinstance(body, dict) and body.get("message") == "pong"

    def search(
        self,
        *,
        term_queries: tuple[str, ...] = (),
        semantic_queries: tuple[str, ...] = (),
    ) -> SearchResponse:
        if not term_queries and not semantic_queries:
            raise ValueError("Metabase search requires at least one query")
        body = self._request(
            "POST",
            "/api/agent/v1/search",
            operation="search",
            payload={
                "term_queries": list(term_queries),
                "semantic_queries": list(semantic_queries),
            },
        )
        if not isinstance(body, dict):
            raise MetabaseClientError(
                code=MetabaseErrorCode.INTERNAL,
                operation="search",
                message="search response is not an object",
                body=body,
            )
        return SearchResponse(
            data=tuple(dict(item) for item in (body.get("data") or ())),
            total_count=int(body.get("total_count") or 0),
        )

    def read_resource(self, uris: tuple[str, ...]) -> ReadResourceResponse:
        if not uris or len(uris) > 5:
            raise ValueError("read_resource requires 1..5 URIs")
        body = self._request(
            "POST",
            "/api/agent/v1/read-resource",
            operation="read_resource",
            payload={"uris": list(uris)},
        )
        if not isinstance(body, dict):
            raise MetabaseClientError(
                code=MetabaseErrorCode.INTERNAL,
                operation="read_resource",
                message="read-resource response is not an object",
                body=body,
            )
        return ReadResourceResponse(
            resources=tuple(dict(item) for item in (body.get("resources") or ())),
        )

    def construct_query(self, portable_query: dict[str, Any]) -> ConstructedQuery:
        body = self._request(
            "POST",
            "/api/agent/v2/construct-query",
            operation="construct_query",
            payload={"query": portable_query},
        )
        if not isinstance(body, dict) or not isinstance(body.get("query"), str):
            raise MetabaseClientError(
                code=MetabaseErrorCode.INTERNAL,
                operation="construct_query",
                message="construct-query response has no serialized query",
                body=body,
            )
        return ConstructedQuery(serialized_query=body["query"])

    def execute_serialized(
        self,
        query: ConstructedQuery,
    ) -> MetabaseExecutionResponse:
        body = self._request(
            "POST",
            "/api/agent/v1/execute",
            operation="execute",
            payload={"query": query.serialized_query},
            expected=(202,),
        )
        result = self._execution(body, operation="execute", page=False)
        assert isinstance(result, MetabaseExecutionResponse)
        return result

    def query(self, portable_query: dict[str, Any]) -> MetabaseQueryPage:
        body = self._request(
            "POST",
            "/api/agent/v2/query",
            operation="combined_query",
            payload={"query": portable_query},
            expected=(202,),
        )
        result = self._execution(body, operation="combined_query", page=True)
        assert isinstance(result, MetabaseQueryPage)
        return result

    def continue_query(self, continuation: ContinuationToken) -> MetabaseQueryPage:
        body = self._request(
            "POST",
            "/api/agent/v2/query",
            operation="continue_query",
            payload={"continuation_token": continuation.token},
            expected=(202,),
        )
        result = self._execution(body, operation="continue_query", page=True)
        assert isinstance(result, MetabaseQueryPage)
        return result

    def startup_handshake(
        self,
        *,
        portable_probe_query: dict[str, Any],
    ) -> MetabaseCapabilityHandshake:
        healthy = self.health()
        agent = self.ping()
        constructed = self.construct_query(portable_probe_query)
        executed = self.execute_serialized(constructed)
        page = self.query(portable_probe_query)

        verified = (
            "health",
            "agent_ping",
            "construct_query",
            "execute",
            "combined_query",
        )
        ready = (
            healthy
            and agent
            and executed.status == ExecutionStatus.COMPLETED
            and page.status == ExecutionStatus.COMPLETED
            and self._policy.raw_sql_policy in ("disabled", "unused")
        )
        return MetabaseCapabilityHandshake(
            ready=ready,
            process_healthy=healthy,
            agent_api_enabled=agent,
            construct_query=True,
            execute_query=True,
            combined_query=True,
            read_resource=True,
            raw_sql_policy=self._policy.raw_sql_policy,
            observed_page_size=self._policy.observed_page_size,
            observed_total_row_cap=self._policy.observed_total_row_cap,
            runtime_version=self._policy.runtime_version,
            runtime_image_digest=self._policy.runtime_image_digest,
            verified_operations=verified,
        )
