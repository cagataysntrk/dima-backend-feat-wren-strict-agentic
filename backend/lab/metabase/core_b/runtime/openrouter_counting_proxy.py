#!/usr/bin/env python3
"""Eval-only fail-closed counting proxy for OpenRouter Chat Completions.

The proxy is deliberately outside Product semantics. It forwards request bodies
unchanged, never retries, never persists prompts/headers/reasoning text, and
rejects chat-completion request N+1 locally before forwarding once the configured
hard ceiling has been consumed.
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from collections import Counter
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

import httpx


SCHEMA_VERSION = "dima_openrouter_counting_proxy_v1"
_CHAT_PATH = "/v1/chat/completions"
_CONTROL_PREFIX = "/__dima__/"
_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def _non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _non_negative_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and value >= 0:
        return float(value)
    return None


def _usage_from_mapping(body: Any) -> dict[str, int | float | None]:
    usage = body.get("usage") if isinstance(body, dict) else None
    if not isinstance(usage, dict):
        return {
            "prompt_tokens": None,
            "completion_tokens": None,
            "reasoning_tokens": None,
            "provider_reported_cost": None,
        }
    details = usage.get("completion_tokens_details")
    if not isinstance(details, dict):
        details = usage.get("completionTokensDetails")
    reasoning = None
    if isinstance(details, dict):
        reasoning = _non_negative_int(details.get("reasoning_tokens"))
        if reasoning is None:
            reasoning = _non_negative_int(details.get("reasoningTokens"))
    if reasoning is None:
        reasoning = _non_negative_int(usage.get("reasoning_tokens"))
    cost = _non_negative_number(usage.get("cost"))
    if cost is None:
        cost_details = usage.get("cost_details")
        if isinstance(cost_details, dict):
            cost = _non_negative_number(cost_details.get("upstream_inference_cost"))
    return {
        "prompt_tokens": _non_negative_int(usage.get("prompt_tokens")),
        "completion_tokens": _non_negative_int(usage.get("completion_tokens")),
        "reasoning_tokens": reasoning,
        "provider_reported_cost": cost,
    }


def response_usage(content_type: str, body: bytes) -> dict[str, int | float | None]:
    """Extract only numeric usage telemetry. Never return response text/content."""
    found = {
        "prompt_tokens": None,
        "completion_tokens": None,
        "reasoning_tokens": None,
        "provider_reported_cost": None,
    }
    if not body:
        return found
    if "text/event-stream" in content_type.casefold():
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line.startswith(b"data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == b"[DONE]":
                continue
            try:
                parsed = json.loads(payload)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            candidate = _usage_from_mapping(parsed)
            for key, value in candidate.items():
                if value is not None:
                    found[key] = value
        return found
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return found
    return _usage_from_mapping(parsed)


def source_and_upstream_path(path: str) -> tuple[str, str]:
    """Decode an optional eval-only source prefix without touching request body."""
    clean = urlsplit(path).path
    if clean.startswith("/source/"):
        parts = clean.split("/")
        # /source/<source>/v1/chat/completions
        if len(parts) < 5 or not parts[2]:
            raise ValueError("invalid source-prefixed proxy path")
        source = parts[2]
        upstream = "/" + "/".join(parts[3:])
        return source, upstream
    if clean == _CHAT_PATH:
        return "metabase", clean
    return "other", clean


@dataclass(frozen=True)
class Reservation:
    ordinal: int
    source: str


class ProviderCeilingExceeded(RuntimeError):
    pass


class ProviderRequestLedger:
    """Thread-safe fail-closed provider budgets and privacy-safe numeric receipt."""

    def __init__(
        self,
        *,
        ceiling: int,
        receipt_path: Path,
        source_ceilings: Mapping[str, int] | None = None,
        prompt_token_ceiling: int | None = None,
        completion_token_ceiling: int | None = None,
        reasoning_token_ceiling: int | None = None,
        provider_cost_ceiling: float | None = None,
    ) -> None:
        if ceiling < 0:
            raise ValueError("provider request ceiling must be non-negative")
        for name, value in (
            ("prompt token", prompt_token_ceiling),
            ("completion token", completion_token_ceiling),
            ("reasoning token", reasoning_token_ceiling),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} ceiling must be non-negative")
        if provider_cost_ceiling is not None and provider_cost_ceiling < 0:
            raise ValueError("provider cost ceiling must be non-negative")
        normalized_sources = None
        if source_ceilings is not None:
            normalized_sources = {}
            for source, limit in source_ceilings.items():
                source = str(source).strip()
                if not source or int(limit) < 0:
                    raise ValueError("source ceilings require non-empty sources and non-negative limits")
                normalized_sources[source] = int(limit)
        self.ceiling = ceiling
        self.receipt_path = receipt_path
        self.source_ceilings = normalized_sources
        self.prompt_token_ceiling = prompt_token_ceiling
        self.completion_token_ceiling = completion_token_ceiling
        self.reasoning_token_ceiling = reasoning_token_ceiling
        self.provider_cost_ceiling = provider_cost_ceiling
        self._lock = threading.Lock()
        self._actual = 0
        self._blocked = 0
        self._by_source: Counter[str] = Counter()
        self._blocked_by_source: Counter[str] = Counter()
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._reasoning_tokens = 0
        self._provider_reported_cost = 0.0
        self._cost_observed = False
        self._responses_with_usage = 0
        self._events: list[dict[str, Any]] = []
        self.persist()

    def _blocked_reason_locked(self, source: str) -> str | None:
        if self._actual >= self.ceiling:
            return "PROVIDER_REQUEST_CEILING_EXHAUSTED"
        if self.source_ceilings is not None:
            source_limit = self.source_ceilings.get(source, 0)
            if self._by_source[source] >= source_limit:
                return "PROVIDER_SOURCE_CEILING_EXHAUSTED"
        if self.prompt_token_ceiling is not None and self._prompt_tokens >= self.prompt_token_ceiling:
            return "PROVIDER_PROMPT_TOKEN_CEILING_REACHED"
        if self.completion_token_ceiling is not None and self._completion_tokens >= self.completion_token_ceiling:
            return "PROVIDER_COMPLETION_TOKEN_CEILING_REACHED"
        if self.reasoning_token_ceiling is not None and self._reasoning_tokens >= self.reasoning_token_ceiling:
            return "PROVIDER_REASONING_TOKEN_CEILING_REACHED"
        if (
            self.provider_cost_ceiling is not None
            and self._cost_observed
            and self._provider_reported_cost >= self.provider_cost_ceiling
        ):
            return "PROVIDER_COST_CEILING_REACHED"
        return None

    def _block_locked(self, source: str, reason: str) -> None:
        self._blocked += 1
        self._blocked_by_source[source] += 1
        self._events.append(
            {
                "ordinal": self._actual + self._blocked,
                "source": source,
                "forwarded": False,
                "blocked_reason": reason,
            }
        )
        self._persist_locked()

    def reserve(self, source: str) -> Reservation:
        with self._lock:
            reason = self._blocked_reason_locked(source)
            if reason is not None:
                self._block_locked(source, reason)
                raise ProviderCeilingExceeded(
                    f"{reason}: provider request blocked locally for source={source}"
                )
            self._actual += 1
            self._by_source[source] += 1
            reservation = Reservation(self._actual, source)
            self._events.append(
                {
                    "ordinal": reservation.ordinal,
                    "source": source,
                    "forwarded": True,
                    "upstream_status": None,
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "reasoning_tokens": None,
                    "provider_reported_cost": None,
                }
            )
            self._persist_locked()
            return reservation

    def complete(
        self,
        reservation: Reservation,
        *,
        upstream_status: int | None,
        usage: dict[str, int | float | None],
    ) -> None:
        with self._lock:
            event = next(
                item for item in self._events
                if item.get("forwarded") is True and item.get("ordinal") == reservation.ordinal
            )
            event["upstream_status"] = upstream_status
            observed = False
            for key in ("prompt_tokens", "completion_tokens", "reasoning_tokens"):
                value = usage.get(key)
                if isinstance(value, int):
                    event[key] = value
                    observed = True
                    if key == "prompt_tokens":
                        self._prompt_tokens += value
                    elif key == "completion_tokens":
                        self._completion_tokens += value
                    else:
                        self._reasoning_tokens += value
            cost = usage.get("provider_reported_cost")
            if isinstance(cost, (int, float)):
                event["provider_reported_cost"] = float(cost)
                self._provider_reported_cost += float(cost)
                self._cost_observed = True
                observed = True
            if observed:
                self._responses_with_usage += 1
            self._persist_locked()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return self._snapshot_locked()

    def persist(self) -> None:
        with self._lock:
            self._persist_locked()

    def _snapshot_locked(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "hard_provider_request_ceiling": self.ceiling,
            "source_request_ceilings": (
                dict(sorted(self.source_ceilings.items()))
                if self.source_ceilings is not None else None
            ),
            "prompt_token_ceiling": self.prompt_token_ceiling,
            "completion_token_ceiling": self.completion_token_ceiling,
            "reasoning_token_ceiling": self.reasoning_token_ceiling,
            "provider_cost_ceiling": self.provider_cost_ceiling,
            "actual_provider_request_count": self._actual,
            "provider_requests_by_source": dict(sorted(self._by_source.items())),
            "blocked_request_count": self._blocked,
            "blocked_requests_by_source": dict(sorted(self._blocked_by_source.items())),
            "prompt_tokens": self._prompt_tokens,
            "completion_tokens": self._completion_tokens,
            "reasoning_tokens": self._reasoning_tokens,
            "provider_reported_cost": (
                round(self._provider_reported_cost, 12) if self._cost_observed else None
            ),
            "responses_with_usage_telemetry": self._responses_with_usage,
            "privacy_contract": {
                "request_headers_persisted": False,
                "request_body_persisted": False,
                "response_body_persisted": False,
                "prompt_text_persisted": False,
                "reasoning_text_persisted": False,
                "api_keys_persisted": False,
            },
            "events": list(self._events),
        }

    def _persist_locked(self) -> None:
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.receipt_path.with_suffix(self.receipt_path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(self._snapshot_locked(), ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(self.receipt_path)


class CountingOpenRouterProxy:
    """Transport-independent forwarding seam, injectable for provider-free tests."""

    def __init__(
        self,
        *,
        upstream_base_url: str,
        ledger: ProviderRequestLedger,
        client: httpx.Client | None = None,
    ) -> None:
        self.upstream_base_url = upstream_base_url.rstrip("/")
        self.ledger = ledger
        self.client = client or httpx.Client(
            timeout=httpx.Timeout(120.0, connect=15.0),
            follow_redirects=False,
        )
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def forward(
        self,
        *,
        method: str,
        request_path: str,
        headers: dict[str, str],
        body: bytes,
    ) -> tuple[int, list[tuple[str, str]], bytes]:
        source, upstream_path = source_and_upstream_path(request_path)
        split = urlsplit(request_path)
        suffix = f"?{split.query}" if split.query else ""
        reservation = None
        if method.upper() == "POST" and upstream_path == _CHAT_PATH:
            reservation = self.ledger.reserve(source)

        outbound_headers = {
            key: value
            for key, value in headers.items()
            if key.casefold() not in _HOP_BY_HOP
        }
        try:
            response = self.client.request(
                method.upper(),
                self.upstream_base_url + upstream_path + suffix,
                headers=outbound_headers,
                content=body,
            )
            response_body = response.content
        except Exception:
            if reservation is not None:
                self.ledger.complete(
                    reservation,
                    upstream_status=None,
                    usage={
                        "prompt_tokens": None,
                        "completion_tokens": None,
                        "reasoning_tokens": None,
                        "provider_reported_cost": None,
                    },
                )
            raise

        if reservation is not None:
            self.ledger.complete(
                reservation,
                upstream_status=response.status_code,
                usage=response_usage(
                    response.headers.get("content-type", ""),
                    response_body,
                ),
            )
        response_headers = [
            (key, value)
            for key, value in response.headers.items()
            if key.casefold() not in _HOP_BY_HOP
            and key.casefold() != "content-encoding"
        ]
        return response.status_code, response_headers, response_body


def make_handler(proxy: CountingOpenRouterProxy):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DimaCountingProxy/1"

        def log_message(self, _format: str, *_args: Any) -> None:
            # Never emit request paths/headers/bodies to logs.
            return

        def _json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _handle(self) -> None:
            if self.path.startswith(_CONTROL_PREFIX):
                if self.path == "/__dima__/health":
                    self._json(200, {"status": "ok"})
                    return
                if self.path == "/__dima__/receipt":
                    self._json(200, proxy.ledger.snapshot())
                    return
                self._json(404, {"error": "not_found"})
                return

            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = max(0, int(raw_length))
            except ValueError:
                self._json(400, {"error": "invalid_content_length"})
                return
            body = self.rfile.read(length) if length else b""
            try:
                status, headers, response_body = proxy.forward(
                    method=self.command,
                    request_path=self.path,
                    headers={key: value for key, value in self.headers.items()},
                    body=body,
                )
            except ProviderCeilingExceeded:
                self._json(
                    429,
                    {
                        "error": {
                            "code": "DIMA_PROVIDER_REQUEST_CEILING_EXHAUSTED",
                            "message": "provider request blocked locally",
                        }
                    },
                )
                return
            except Exception:
                self._json(
                    502,
                    {
                        "error": {
                            "code": "DIMA_PROVIDER_PROXY_UPSTREAM_FAILED",
                            "message": "provider proxy upstream request failed",
                        }
                    },
                )
                return

            self.send_response(status)
            for key, value in headers:
                if key.casefold() == "content-length":
                    continue
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        do_GET = _handle
        do_POST = _handle

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen-host", default="127.0.0.1")
    ap.add_argument("--listen-port", type=int, required=True)
    ap.add_argument(
        "--upstream-base-url",
        default="https://openrouter.ai/api",
    )
    ap.add_argument("--ceiling", type=int, required=True)
    ap.add_argument("--source-ceiling", action="append", default=[], metavar="SOURCE=LIMIT")
    ap.add_argument("--prompt-token-ceiling", type=int)
    ap.add_argument("--completion-token-ceiling", type=int)
    ap.add_argument("--reasoning-token-ceiling", type=int)
    ap.add_argument("--provider-cost-ceiling", type=float)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    source_ceilings: dict[str, int] | None = None
    if args.source_ceiling:
        source_ceilings = {}
        for raw in args.source_ceiling:
            if "=" not in raw:
                raise SystemExit("--source-ceiling requires SOURCE=LIMIT")
            source, raw_limit = raw.split("=", 1)
            source = source.strip()
            if not source or source in source_ceilings:
                raise SystemExit("source ceilings must be unique and non-empty")
            source_ceilings[source] = int(raw_limit)

    ledger = ProviderRequestLedger(
        ceiling=args.ceiling,
        receipt_path=args.receipt,
        source_ceilings=source_ceilings,
        prompt_token_ceiling=args.prompt_token_ceiling,
        completion_token_ceiling=args.completion_token_ceiling,
        reasoning_token_ceiling=args.reasoning_token_ceiling,
        provider_cost_ceiling=args.provider_cost_ceiling,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url=args.upstream_base_url,
        ledger=ledger,
    )
    server = ThreadingHTTPServer(
        (args.listen_host, args.listen_port),
        make_handler(proxy),
    )
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
        proxy.close()
        ledger.persist()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
