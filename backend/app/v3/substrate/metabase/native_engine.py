"""Thin typed bridge to Metabase's native Metabot runtime.

The bridge delegates to /api/metabot/agent-streaming. It does not implement analytical
planning, semantic resolution, Agent API fallback, Wren fallback, or raw SQL execution.
"""
from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeEngineObservation,
    NativeEngineRequest,
    NativeStreamEvent,
)


class NativeEngineBridgeError(RuntimeError):
    pass


class NativeEngineIdentityMismatch(NativeEngineBridgeError):
    pass


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

    def invoke(self, request: NativeEngineRequest) -> NativeEngineObservation:
        runtime = self._verify_runtime()
        payload: dict[str, Any] = {
            "profile_id": request.profile_id,
            "message": request.message,
            "context": request.context,
            "conversation_id": request.conversation_id,
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
