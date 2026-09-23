"""Parser and direct client for Metabase native AI streaming protocol.

Mirrors the public frontend stream framing. It stores structured tool traffic and
state/history only; no debug mode or private reasoning capture.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import httpx


PREFIX = {
    "0": "text",
    "2": "data",
    "3": "error",
    "d": "finish_message",
    "f": "start_message",
    "9": "tool_call",
    "a": "tool_result",
}


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class NativeTurn:
    question: str
    conversation_id: str
    profile_id: str
    input_history_count: int
    input_state_digest: str
    http_status: int | None = None
    text: str = ""
    data_parts: list[dict[str, Any]] = field(default_factory=list)
    tool_sequence: list[str] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    response_history: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    errors: list[Any] = field(default_factory=list)
    finish_reason: str | None = None
    latency_ms: int | None = None

    def receipt(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "conversation_id": self.conversation_id,
            "profile_id": self.profile_id,
            "input_history_count": self.input_history_count,
            "input_state_digest": self.input_state_digest,
            "http_status": self.http_status,
            "tool_sequence": self.tool_sequence,
            "tool_call_count": len(self.tool_calls),
            "tool_result_count": len(self.tool_results),
            "data_part_types": [str(x.get("type")) for x in self.data_parts],
            "iteration_proxy": len(self.tool_calls),
            "final_state_digest": digest(self.state),
            "final_answer": self.text,
            "finish_reason": self.finish_reason,
            "latency_ms": self.latency_ms,
            "errors": self.errors,
            "private_reasoning_recorded": False,
        }


def apply_stream_line(turn: NativeTurn, line: str) -> None:
    if not line:
        return
    prefix, sep, encoded = line.partition(":")
    if not sep or prefix not in PREFIX:
        return
    try:
        value = json.loads(encoded)
    except json.JSONDecodeError:
        turn.errors.append(
            {"class": "STREAM_PARSE_ERROR", "line_digest": digest(line)}
        )
        return

    kind = PREFIX[prefix]
    if kind == "text":
        text = str(value)
        turn.text += text
        if (
            turn.response_history
            and turn.response_history[-1].get("role") == "assistant"
            and "content" in turn.response_history[-1]
        ):
            turn.response_history[-1]["content"] += text
        else:
            turn.response_history.append(
                {"role": "assistant", "content": text}
            )
    elif kind == "data":
        if isinstance(value, dict):
            turn.data_parts.append(value)
            if (
                value.get("type") == "state"
                and isinstance(value.get("value"), dict)
            ):
                turn.state = value["value"]
    elif kind == "tool_call":
        if isinstance(value, dict):
            turn.tool_calls.append(value)
            tool_name = str(value.get("toolName") or "")
            turn.tool_sequence.append(tool_name)
            turn.response_history.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": value.get("toolCallId"),
                            "name": value.get("toolName"),
                            "arguments": value.get("args"),
                        }
                    ],
                }
            )
    elif kind == "tool_result":
        if isinstance(value, dict):
            turn.tool_results.append(value)
            turn.response_history.append(
                {
                    "role": "tool",
                    "content": value.get("result"),
                    "tool_call_id": value.get("toolCallId"),
                }
            )
    elif kind == "error":
        turn.errors.append(value)
    elif kind == "finish_message" and isinstance(value, dict):
        turn.finish_reason = value.get("finishReason")


class NativeMetabotSession:
    def __init__(self, *, base_url: str, session: str, profile_id: str = "nlq") -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.profile_id = profile_id
        self.conversation_id = str(uuid.uuid4())
        self.history: list[dict[str, Any]] = []
        self.state: dict[str, Any] = {}

    def ask(self, question: str, *, context: dict[str, Any] | None = None) -> NativeTurn:
        turn = NativeTurn(
            question=question,
            conversation_id=self.conversation_id,
            profile_id=self.profile_id,
            input_history_count=len(self.history),
            input_state_digest=digest(self.state),
            state=dict(self.state),
        )
        payload = {
            "profile_id": self.profile_id,
            "message": question,
            "context": context or {},
            "conversation_id": self.conversation_id,
            "history": self.history,
            "state": self.state,
        }
        started = time.monotonic()
        with httpx.Client(timeout=120.0) as client:
            with client.stream(
                "POST",
                self.base_url + "/api/metabot/agent-streaming",
                headers={
                    "X-Metabase-Session": self.session,
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                turn.http_status = response.status_code
                if response.status_code != 202:
                    body = response.read().decode(errors="replace")
                    turn.errors.append(
                        {
                            "class": "PERMISSION_BLOCKED"
                            if response.status_code in (401, 402, 403)
                            else "HARNESS_OR_ENDPOINT_FAILURE",
                            "status": response.status_code,
                            "body": body[:1000],
                        }
                    )
                    turn.latency_ms = int((time.monotonic() - started) * 1000)
                    return turn

                for line in response.iter_lines():
                    apply_stream_line(turn, line)

        turn.latency_ms = int((time.monotonic() - started) * 1000)
        if not turn.errors:
            self.history = [
                *self.history,
                {"role": "user", "content": question},
                *turn.response_history,
            ]
            self.state = dict(turn.state)
        return turn
