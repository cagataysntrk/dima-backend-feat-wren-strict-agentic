"""Thin typed bridge to Metabase's native Metabot runtime.

The bridge delegates to /api/metabot/agent-streaming. It does not implement analytical
planning, semantic resolution, Agent API fallback, Wren fallback, or raw SQL execution.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any
from uuid import UUID

import httpx

from app.v3.substrate.metabase.native_models import (
    NativeDatasetExecutionObservation,
    NativeEngineIdentity,
    NativeExactOccurrenceExecutionObservation,
    NativeEngineObservation,
    NativeProducedQuery,
    NativeEngineRequest,
    NativeStreamEvent,
)


class NativeEngineBridgeError(RuntimeError):
    pass


class NativeEngineIdentityMismatch(NativeEngineBridgeError):
    pass


class NativeDatasetExecutionError(NativeEngineBridgeError):
    def __init__(self, *, status_code: int, detail: str) -> None:
        super().__init__(
            f"native dataset execution returned HTTP {status_code}: {detail}"
        )
        self.status_code = status_code
        self.detail = detail


class NativeEngineStreamError(NativeEngineBridgeError):
    def __init__(self, observation: NativeEngineObservation) -> None:
        super().__init__("native Metabot stream returned error events")
        self.observation = observation


class NativeEngineBridge:
    def __init__(
        self,
        *,
        base_url: str,
        session_token: str,
        expected_identity: NativeEngineIdentity,
        timeout_seconds: float = 240.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url is required")
        if not session_token.strip():
            raise ValueError("session_token is required")
        self._expected = expected_identity
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            transport=transport,
            headers={"X-Metabase-Session": session_token},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "NativeEngineBridge":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb
        self.close()

    def _verify_runtime(self) -> dict[str, Any]:
        response = self._client.get("/api/session/properties")
        if response.status_code != 200:
            raise NativeEngineBridgeError(
                f"runtime identity probe failed with HTTP {response.status_code}"
            )
        body = response.json()
        version = body.get("version") if isinstance(body, dict) else None
        if not isinstance(version, dict):
            raise NativeEngineIdentityMismatch("runtime version identity is missing")
        observed_tag = str(version.get("tag") or "")
        if observed_tag != self._expected.runtime_tag:
            raise NativeEngineIdentityMismatch(
                f"runtime tag {observed_tag!r} != expected {self._expected.runtime_tag!r}"
            )
        return version

    @staticmethod
    def _decode_line(index: int, line: str) -> NativeStreamEvent:
        prefix, payload = (line.split(":", 1) + [""])[:2] if ":" in line else ("", line)
        try:
            value: Any = json.loads(payload)
        except Exception:
            value = payload
        return NativeStreamEvent(index=index, prefix=prefix, raw_line=line, value=value)

    @staticmethod
    def _final_state(data_parts: list[Any]) -> dict[str, Any] | None:
        states = [
            x.get("value")
            for x in data_parts
            if isinstance(x, dict) and x.get("type") == "state" and isinstance(x.get("value"), dict)
        ]
        return states[-1] if states else None

    def current_user(self) -> dict[str, Any]:
        """Read the native user bound to this exact pass-through session."""
        try:
            response = self._client.get("/api/user/current")
        except httpx.TimeoutException as exc:
            raise NativeEngineBridgeError("current-user request timed out") from exc
        except httpx.RequestError as exc:
            raise NativeEngineBridgeError(f"current-user transport failed: {exc}") from exc
        if response.status_code != 200:
            raise NativeEngineBridgeError(
                f"current-user returned HTTP {response.status_code}: {response.text[:500]}"
            )
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("id"), int):
            raise NativeEngineBridgeError("current-user response has no numeric user id")
        return body

    def engine_identity(self) -> dict[str, Any]:
        """Read the isolated Dima engine identity seam with this exact session."""
        try:
            response = self._client.get("/api/dima/engine/v1/identity")
        except httpx.TimeoutException as exc:
            raise NativeEngineBridgeError("engine identity request timed out") from exc
        except httpx.RequestError as exc:
            raise NativeEngineBridgeError(
                f"engine identity transport failed: {exc}"
            ) from exc
        if response.status_code != 200:
            raise NativeEngineBridgeError(
                f"engine identity returned HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )
        body = response.json()
        if not isinstance(body, dict):
            raise NativeEngineBridgeError("engine identity response is not an object")
        return body

    @staticmethod
    def _query_fingerprint(query: dict[str, Any]) -> str:
        try:
            raw = json.dumps(
                query,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise NativeEngineBridgeError(
                "native produced query is not deterministic JSON"
            ) from exc
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def capture_produced_query(
        cls,
        observation: NativeEngineObservation,
    ) -> NativeProducedQuery:
        """Capture the query Metabot actually emitted; never reconstruct it.

        Pinned Metabot's generated_entity data part embeds the executable legacy
        dataset_query. The conversation state is a source-backed fallback only when
        no generated_entity query was emitted.
        """

        generated: list[tuple[str, dict[str, Any]]] = []
        for part in observation.data_parts:
            if not isinstance(part, dict) or part.get("type") != "generated_entity":
                continue
            value = part.get("value")
            query_ref = value.get("query") if isinstance(value, dict) else None
            if not isinstance(query_ref, dict):
                continue
            query_id = query_ref.get("id")
            query = query_ref.get("query")
            if isinstance(query_id, str) and query_id.strip() and isinstance(query, dict):
                generated.append((query_id, query))

        if generated:
            by_id: dict[str, dict[str, Any]] = {}
            for query_id, query in generated:
                prior = by_id.get(query_id)
                if prior is not None and prior != query:
                    raise NativeEngineBridgeError(
                        "Metabot stream emitted conflicting payloads for one native query id"
                    )
                by_id[query_id] = query
            if len(by_id) != 1:
                raise NativeEngineBridgeError(
                    "expected exactly one generated native query occurrence"
                )
            query_id, query = next(iter(by_id.items()))
            return NativeProducedQuery(
                native_query_id=query_id,
                query=query,
                query_fingerprint=cls._query_fingerprint(query),
                source="generated_entity",
            )

        state = observation.final_state or {}
        queries = state.get("queries") if isinstance(state, dict) else None
        if isinstance(queries, dict):
            candidates = [
                (str(query_id), query)
                for query_id, query in queries.items()
                if str(query_id).strip() and isinstance(query, dict)
            ]
            if len(candidates) == 1:
                query_id, query = candidates[0]
                return NativeProducedQuery(
                    native_query_id=query_id,
                    query=query,
                    query_fingerprint=cls._query_fingerprint(query),
                    source="state",
                )

        raise NativeEngineBridgeError(
            "native Metabot turn did not expose exactly one executable query payload"
        )

    def execute_dataset(
        self,
        query: dict[str, Any],
    ) -> NativeDatasetExecutionObservation:
        """Execute the captured Metabot query unchanged through native /api/dataset."""

        fingerprint = self._query_fingerprint(query)
        started = time.monotonic()
        try:
            response = self._client.post("/api/dataset", json=query)
        except httpx.TimeoutException as exc:
            raise NativeEngineBridgeError("native dataset execution timed out") from exc
        except httpx.RequestError as exc:
            raise NativeEngineBridgeError(
                f"native dataset execution transport failed: {exc}"
            ) from exc
        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        if response.status_code < 200 or response.status_code >= 300:
            raise NativeDatasetExecutionError(
                status_code=response.status_code,
                detail=response.text[:1000],
            )
        body = response.json()
        if not isinstance(body, dict):
            raise NativeEngineBridgeError(
                "native dataset execution response is not an object"
            )
        return NativeDatasetExecutionObservation(
            status_code=response.status_code,
            latency_ms=latency_ms,
            query_fingerprint=fingerprint,
            payload=body,
        )

    def attest_native_query(
        self,
        *,
        conversation_id: UUID,
        native_query_id: str,
    ) -> dict[str, Any]:
        """Attest one server-side query occurrence by locator only."""
        if not native_query_id.strip():
            raise ValueError("native_query_id is required")
        try:
            response = self._client.post(
                "/api/dima/engine/v1/native-query-attestation",
                json={
                    "conversation_id": str(conversation_id),
                    "native_query_id": native_query_id,
                },
            )
        except httpx.TimeoutException as exc:
            raise NativeEngineBridgeError("native attestation request timed out") from exc
        except httpx.RequestError as exc:
            raise NativeEngineBridgeError(
                f"native attestation transport failed: {exc}"
            ) from exc
        if response.status_code != 200:
            raise NativeEngineBridgeError(
                f"native attestation returned HTTP {response.status_code}: "
                f"{response.text[:1000]}"
            )
        body = response.json()
        if not isinstance(body, dict):
            raise NativeEngineBridgeError("native attestation response is not an object")
        return body

    def execute_native_query(
        self,
        *,
        conversation_id: UUID,
        native_query_id: str,
        expected_pmbql_fingerprint: str,
        expected_attestation_id: str,
    ) -> NativeExactOccurrenceExecutionObservation:
        """Execute one already-authorized server-side query occurrence by identity only."""
        if not native_query_id.strip():
            raise ValueError("native_query_id is required")
        if not expected_pmbql_fingerprint.strip():
            raise ValueError("expected_pmbql_fingerprint is required")
        if not expected_attestation_id.strip():
            raise ValueError("expected_attestation_id is required")
        started = time.monotonic()
        try:
            response = self._client.post(
                "/api/dima/engine/v1/native-query-execution",
                json={
                    "conversation_id": str(conversation_id),
                    "native_query_id": native_query_id,
                    "expected_pmbql_fingerprint": expected_pmbql_fingerprint,
                    "expected_attestation_id": expected_attestation_id,
                },
            )
        except httpx.TimeoutException as exc:
            raise NativeEngineBridgeError("native exact-occurrence execution timed out") from exc
        except httpx.RequestError as exc:
            raise NativeEngineBridgeError(
                f"native exact-occurrence execution transport failed: {exc}"
            ) from exc
        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        if response.status_code != 200:
            raise NativeEngineBridgeError(
                f"native exact-occurrence execution returned HTTP {response.status_code}: "
                f"{response.text[:1000]}"
            )
        body = response.json()
        if not isinstance(body, dict):
            raise NativeEngineBridgeError(
                "native exact-occurrence execution response is not an object"
            )
        result = body.get("result")
        if not isinstance(result, dict):
            raise NativeEngineBridgeError(
                "native exact-occurrence execution response has no result object"
            )
        return NativeExactOccurrenceExecutionObservation(
            status_code=response.status_code,
            latency_ms=latency_ms,
            native_conversation_id=body.get("native_conversation_id"),
            native_query_id=body.get("native_query_id"),
            attestation_id=body.get("attestation_id"),
            executed_pmbql_fingerprint=body.get("executed_pmbql_fingerprint"),
            runtime_identity=body.get("runtime_identity"),
            payload=result,
            attestation=body.get("attestation"),
        )

    def invoke(self, request: NativeEngineRequest) -> NativeEngineObservation:
        runtime = self._verify_runtime()
        payload: dict[str, Any] = {
            "profile_id": request.profile_id,
            "message": request.message,
            "context": request.context,
            "conversation_id": str(request.conversation_id),
            "history": request.history,
            "state": request.state,
            "debug": False,
        }
        if request.metabot_id is not None:
            payload["metabot_id"] = request.metabot_id

        started = time.monotonic()
        try:
            with self._client.stream(
                "POST",
                "/api/metabot/agent-streaming",
                json=payload,
            ) as response:
                status_code = response.status_code
                if status_code != 202:
                    body = response.read().decode("utf-8", "replace")[:1000]
                    raise NativeEngineBridgeError(
                        f"native Metabot returned HTTP {status_code}: {body}"
                    )
                events = [
                    self._decode_line(index, line)
                    for index, line in enumerate(response.iter_lines())
                    if line
                ]
        except httpx.TimeoutException as exc:
            raise NativeEngineBridgeError("native Metabot request timed out") from exc
        except httpx.RequestError as exc:
            raise NativeEngineBridgeError(f"native Metabot transport failed: {exc}") from exc

        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        text_parts: list[str] = []
        data_parts: list[Any] = []
        tool_calls: list[Any] = []
        tool_results: list[Any] = []
        errors: list[Any] = []
        finishes: list[Any] = []

        for event in events:
            if event.prefix == "0" and isinstance(event.value, str):
                text_parts.append(event.value)
            elif event.prefix == "2":
                data_parts.append(event.value)
            elif event.prefix == "9":
                tool_calls.append(event.value)
            elif event.prefix == "a":
                tool_results.append(event.value)
            elif event.prefix == "3":
                errors.append(event.value)
            elif event.prefix == "d":
                finishes.append(event.value)

        observation = NativeEngineObservation(
            engine_identity=self._expected,
            status_code=status_code,
            latency_ms=latency_ms,
            runtime_version=runtime,
            events=tuple(events),
            text_parts=tuple(text_parts),
            data_parts=tuple(data_parts),
            tool_calls=tuple(tool_calls),
            tool_results=tuple(tool_results),
            errors=tuple(errors),
            finish_parts=tuple(finishes),
            final_state=self._final_state(data_parts),
        )
        if observation.errors:
            raise NativeEngineStreamError(observation)
        return observation
