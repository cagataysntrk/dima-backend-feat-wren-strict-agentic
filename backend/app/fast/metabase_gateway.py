"""Fast Track-owned typed Metabase Agent API boundary.

This module owns transport only. It intentionally does not interpret raw user language,
resolve business meaning, author SQL, or depend on Wren/V2/V3 semantic owners.
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from typing import Any

import httpx
from pydantic import ValidationError

from app.fast.auth_context import FastMetabaseAuthContext
from app.fast.metabase_errors import FastMetabaseError, FastMetabaseErrorCode
from app.fast.metabase_models import (
    CapabilityHandshake,
    ConstructedQuery,
    ContinuationToken,
    ExecutionResponse,
    ExecutionStatus,
    FastMetabaseRuntimePolicy,
    QueryPage,
    ReadResourceResponse,
    SearchResponse,
)
from app.fast.metabase_telemetry import (
    FastMetabaseTelemetryEvent,
    FastMetabaseTelemetrySink,
    NullFastMetabaseTelemetry,
)


class FastMetabaseGateway:
    """Authenticated, bounded Metabase Agent API transport."""

    def __init__(
        self,
        *,
        base_url: str,
        auth: FastMetabaseAuthContext,
        policy: FastMetabaseRuntimePolicy | None = None,
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        telemetry: FastMetabaseTelemetrySink | None = None,
        max_transport_retries: int = 1,
    ) -> None:
        if not base_url.strip():
            raise ValueError("Metabase base_url is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_transport_retries < 0 or max_transport_retries > 2:
            raise ValueError("max_transport_retries must be between 0 and 2")

        self._base_url = base_url.rstrip("/")
        self._auth = auth
        self._policy = policy or FastMetabaseRuntimePolicy()
        self._telemetry = telemetry or NullFastMetabaseTelemetry()
        self._max_transport_retries = max_transport_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout_seconds,
            transport=transport,
            headers={
                "Accept": "application/json",
                **auth.headers(),
            },
        )

    @property
    def policy(self) -> FastMetabaseRuntimePolicy:
        return self._policy

    @property
    def access_fingerprint(self):
        return self._auth.access_fingerprint()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FastMetabaseGateway":
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
            FastMetabaseTelemetryEvent(
                operation=operation,
                ok=ok,
                status_code=status_code,
                duration_ms=max(0, int((time.monotonic() - started) * 1000)),
                error_code=error_code,
            )
        )

    @staticmethod
    def _decode(response: httpx.Response, *, operation: str) -> Any:
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation=operation,
                message="Metabase returned a non-JSON response",
                status_code=response.status_code,
                body=response.text[:1000],
            ) from exc

    @staticmethod
    def _timeout_code(operation: str) -> FastMetabaseErrorCode:
        if operation in {"execute", "combined_query", "continue_query"}:
            return FastMetabaseErrorCode.DB_TIMEOUT
        return FastMetabaseErrorCode.METABASE_UNAVAILABLE

    def _request(
        self,
        method: str,
        path: str,
        *,
        operation: str,
        payload: dict[str, Any] | None = None,
        expected: Iterable[int] = (200,),
        retryable: bool = False,
    ) -> Any:
        started = time.monotonic()
        expected_codes = set(expected)
        attempts = 1 + (self._max_transport_retries if retryable else 0)

        for attempt in range(attempts):
            try:
                response = self._client.request(method, path, json=payload)
            except httpx.TimeoutException as exc:
                if attempt + 1 < attempts:
                    continue
                code = self._timeout_code(operation)
                self._emit(
                    operation=operation,
                    started=started,
                    ok=False,
                    error_code=code.value,
                )
                raise FastMetabaseError(
                    code=code,
                    operation=operation,
                    message="Metabase request timed out",
                ) from exc
            except httpx.RequestError as exc:
                if attempt + 1 < attempts:
                    continue
                self._emit(
                    operation=operation,
                    started=started,
                    ok=False,
                    error_code=FastMetabaseErrorCode.METABASE_UNAVAILABLE.value,
                )
                raise FastMetabaseError(
                    code=FastMetabaseErrorCode.METABASE_UNAVAILABLE,
                    operation=operation,
                    message=str(exc),
                ) from exc

            if retryable and response.status_code in {502, 503, 504} and attempt + 1 < attempts:
                continue

            body = self._decode(response, operation=operation)
            if response.status_code not in expected_codes:
                error = FastMetabaseError.from_http(
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

        raise AssertionError("unreachable Metabase request loop")

    def _execution(
        self,
        body: Any,
        *,
        operation: str,
        page: bool,
    ) -> ExecutionResponse | QueryPage:
        if not isinstance(body, dict):
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation=operation,
                message="Metabase execution response is not an object",
                body=body,
            )

        status = str(body.get("status") or "")
        if status == ExecutionStatus.FAILED.value:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.QUERY_EXECUTION_FAILED,
                operation=operation,
                message=str(body.get("error") or "Metabase query execution failed"),
                body=body,
            )
        if status != ExecutionStatus.COMPLETED.value:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation=operation,
                message=f"unexpected execution status {status!r}",
                body=body,
            )

        try:
            row_count = int(body.get("row_count") or 0)
        except (TypeError, ValueError) as exc:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation=operation,
                message="row_count is not an integer",
                body=body,
            ) from exc

        if page and row_count > self._policy.max_page_rows:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.PAGINATION_INVALID,
                operation=operation,
                message=(
                    f"page row_count {row_count} exceeds pinned "
                    f"limit {self._policy.max_page_rows}"
                ),
                body=body,
            )

        common = {
            "status": status,
            "data": body.get("data") or {},
            "row_count": row_count,
            "running_time": body.get("running_time"),
            "error": None,
        }

        try:
            if page:
                token = body.get("continuation_token")
                return QueryPage(
                    **common,
                    continuation=ContinuationToken(token=str(token)) if token else None,
                )
            return ExecutionResponse(**common)
        except ValidationError as exc:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation=operation,
                message="malformed Metabase execution envelope",
                body=body,
            ) from exc

    def health(self) -> bool:
        body = self._request(
            "GET",
            "/api/health",
            operation="health",
            expected=(200,),
            retryable=True,
        )
        return isinstance(body, dict)

    def ping(self) -> bool:
        body = self._request(
            "GET",
            "/api/agent/v1/ping",
            operation="agent_ping",
            expected=(200,),
            retryable=True,
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
        if any(not query.strip() for query in (*term_queries, *semantic_queries)):
            raise ValueError("Metabase search queries must be non-empty")

        body = self._request(
            "POST",
            "/api/agent/v1/search",
            operation="search",
            payload={
                "term_queries": list(term_queries),
                "semantic_queries": list(semantic_queries),
            },
            retryable=True,
        )
        if not isinstance(body, dict):
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation="search",
                message="search response is not an object",
                body=body,
            )
        try:
            return SearchResponse(
                data=tuple(dict(item) for item in (body.get("data") or ())),
                total_count=int(body.get("total_count") or 0),
            )
        except (TypeError, ValueError) as exc:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation="search",
                message="malformed search response",
                body=body,
            ) from exc

    def read_resource(self, uris: tuple[str, ...]) -> ReadResourceResponse:
        if not uris or len(uris) > 5:
            raise ValueError("read_resource requires 1..5 URIs")
        if any(not uri.strip() for uri in uris):
            raise ValueError("resource URIs must be non-empty")

        body = self._request(
            "POST",
            "/api/agent/v1/read-resource",
            operation="read_resource",
            payload={"uris": list(uris)},
            retryable=True,
        )
        if not isinstance(body, dict):
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation="read_resource",
                message="read-resource response is not an object",
                body=body,
            )
        try:
            parsed = ReadResourceResponse.model_validate(body)
        except ValidationError as exc:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation="read_resource",
                message="malformed read-resource envelope",
                body=body,
            ) from exc

        observed = tuple(item.uri for item in parsed.resources)
        if len(parsed.resources) != len(uris) or observed != uris:
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation="read_resource",
                message="read-resource URI/count mismatch",
                body={"requested_uris": uris, "observed_uris": observed},
            )
        return parsed

    def construct_query(self, portable_query: dict[str, Any]) -> ConstructedQuery:
        if not isinstance(portable_query, dict) or not portable_query:
            raise ValueError("portable_query must be a non-empty object")
        body = self._request(
            "POST",
            "/api/agent/v2/construct-query",
            operation="construct_query",
            payload={"query": portable_query},
            retryable=True,
        )
        if not isinstance(body, dict) or not isinstance(body.get("query"), str):
            raise FastMetabaseError(
                code=FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED,
                operation="construct_query",
                message="construct-query response has no serialized query",
                body=body,
            )
        return ConstructedQuery(serialized_query=body["query"])

    def execute_serialized(self, query: ConstructedQuery) -> ExecutionResponse:
        body = self._request(
            "POST",
            "/api/agent/v1/execute",
            operation="execute",
            payload={"query": query.serialized_query},
            expected=(202,),
            retryable=True,
        )
        result = self._execution(body, operation="execute", page=False)
        assert isinstance(result, ExecutionResponse)
        return result

    def query(self, portable_query: dict[str, Any]) -> QueryPage:
        if not isinstance(portable_query, dict) or not portable_query:
            raise ValueError("portable_query must be a non-empty object")
        body = self._request(
            "POST",
            "/api/agent/v2/query",
            operation="combined_query",
            payload={"query": portable_query},
            expected=(202,),
            retryable=True,
        )
        result = self._execution(body, operation="combined_query", page=True)
        assert isinstance(result, QueryPage)
        return result

    def continue_query(self, continuation: ContinuationToken) -> QueryPage:
        body = self._request(
            "POST",
            "/api/agent/v2/query",
            operation="continue_query",
            payload={"continuation_token": continuation.token},
            expected=(202,),
            retryable=True,
        )
        result = self._execution(body, operation="continue_query", page=True)
        assert isinstance(result, QueryPage)
        return result

    def startup_handshake(
        self,
        *,
        portable_probe_query: dict[str, Any],
        resource_probe_uri: str,
    ) -> CapabilityHandshake:
        if not resource_probe_uri.strip():
            raise ValueError("resource_probe_uri is required")

        healthy = self.health()
        agent = self.ping()
        resource = self.read_resource((resource_probe_uri,))
        resource_ok = (
            len(resource.resources) == 1
            and resource.resources[0].uri == resource_probe_uri
            and not resource.resources[0].failed
        )
        constructed = self.construct_query(portable_probe_query)
        executed = self.execute_serialized(constructed)
        page = self.query(portable_probe_query)

        verified = ["health", "agent_ping"]
        if resource_ok:
            verified.append("read_resource")
        verified.extend(["construct_query", "execute", "combined_query"])

        ready = (
            healthy
            and agent
            and resource_ok
            and executed.status == ExecutionStatus.COMPLETED
            and page.status == ExecutionStatus.COMPLETED
            and self._policy.raw_sql_policy == "disabled"
        )
        return CapabilityHandshake(
            ready=ready,
            process_healthy=healthy,
            agent_api_enabled=agent,
            read_resource=resource_ok,
            construct_query=True,
            execute_query=True,
            combined_query=True,
            raw_sql_policy="disabled",
            observed_page_limit=self._policy.max_page_rows,
            runtime_version=self._policy.runtime_version,
            runtime_image_digest=self._policy.runtime_image_digest,
            verified_operations=tuple(verified),
        )
