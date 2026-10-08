from __future__ import annotations

import json

import httpx
import pytest

from lab.metabase.core_b.runtime.openrouter_counting_proxy import (
    CountingOpenRouterProxy,
    ProviderCeilingExceeded,
    affordable_completion_tokens,
    bounded_chat_request_body,
    ProviderRequestLedger,
    response_usage,
    source_and_upstream_path,
)


def _client(calls: list[httpx.Request]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json"},
            json={
                "choices": [
                    {
                        "message": {"content": "{\"ok\":true}"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 11,
                    "completion_tokens": 7,
                    "completion_tokens_details": {
                        "reasoning_tokens": 3,
                    },
                    "cost": 0.00123,
                },
            },
        )

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_source_prefix_counts_dima_structured_and_metabase_separately(tmp_path):
    calls: list[httpx.Request] = []
    client = _client(calls)
    ledger = ProviderRequestLedger(
        ceiling=4,
        receipt_path=tmp_path / "receipt.json",
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=client,
    )

    proxy.forward(
        method="POST",
        request_path="/source/research_intake/v1/chat/completions",
        headers={"Authorization": "Bearer SECRET"},
        body=b'{"messages":[{"role":"user","content":"private"}]}',
    )
    proxy.forward(
        method="POST",
        request_path="/v1/chat/completions",
        headers={"Authorization": "Bearer SECRET"},
        body=b'{"messages":[{"role":"user","content":"private"}]}',
    )

    receipt = ledger.snapshot()
    assert receipt["actual_provider_request_count"] == 2
    assert receipt["provider_requests_by_source"] == {
        "metabase": 1,
        "research_intake": 1,
    }
    assert len(calls) == 2
    assert calls[0].url.path == "/api/v1/chat/completions"
    assert calls[1].url.path == "/api/v1/chat/completions"


@pytest.mark.parametrize(
    ("payload", "expected_max_tokens"),
    [
        ({"messages": []}, 16000),
        ({"messages": [], "max_tokens": 4096}, 4096),
        ({"messages": [], "max_tokens": 65536}, 16000),
    ],
)
def test_completion_ceiling_is_enforced_on_wire_only(payload, expected_max_tokens):
    original = json.loads(json.dumps(payload))
    bounded = json.loads(
        bounded_chat_request_body(
            json.dumps(payload).encode("utf-8"),
            completion_token_ceiling=16000,
        )
    )
    assert bounded["max_tokens"] == expected_max_tokens
    assert bounded.get("messages") == original.get("messages")
    for key, value in original.items():
        if key != "max_tokens":
            assert bounded[key] == value


def test_proxy_applies_completion_ceiling_before_upstream(tmp_path):
    calls: list[httpx.Request] = []
    ledger = ProviderRequestLedger(
        ceiling=2,
        receipt_path=tmp_path / "receipt.json",
        completion_token_ceiling=16000,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=_client(calls),
    )
    proxy.forward(
        method="POST",
        request_path="/v1/chat/completions",
        headers={},
        body=json.dumps(
            {
                "messages": [{"role": "user", "content": "opaque"}],
                "max_tokens": 65536,
            }
        ).encode("utf-8"),
    )
    forwarded = json.loads(calls[0].content)
    assert forwarded["max_tokens"] == 16000
    assert forwarded["messages"] == [{"role": "user", "content": "opaque"}]
    assert ledger.snapshot()["completion_token_ceiling"] == 16000


def test_ceiling_rejects_n_plus_one_before_upstream(tmp_path):
    calls: list[httpx.Request] = []
    client = _client(calls)
    ledger = ProviderRequestLedger(
        ceiling=1,
        receipt_path=tmp_path / "receipt.json",
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=client,
    )

    proxy.forward(
        method="POST",
        request_path="/source/p17_manager/v1/chat/completions",
        headers={"Authorization": "Bearer SECRET"},
        body=b"{}",
    )
    with pytest.raises(ProviderCeilingExceeded):
        proxy.forward(
            method="POST",
            request_path="/v1/chat/completions",
            headers={"Authorization": "Bearer SECRET"},
            body=b"{}",
        )

    receipt = ledger.snapshot()
    assert len(calls) == 1
    assert receipt["actual_provider_request_count"] == 1
    assert receipt["blocked_request_count"] == 1
    assert receipt["blocked_requests_by_source"] == {"metabase": 1}


def test_zero_ceiling_physically_blocks_background_chat_without_spend(tmp_path):
    calls: list[httpx.Request] = []
    client = _client(calls)
    ledger = ProviderRequestLedger(
        ceiling=0,
        receipt_path=tmp_path / "setup.json",
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=client,
    )

    with pytest.raises(ProviderCeilingExceeded):
        proxy.forward(
            method="POST",
            request_path="/v1/chat/completions",
            headers={"Authorization": "Bearer SECRET"},
            body=b'{"background":"suggested-prompts"}',
        )

    receipt = ledger.snapshot()
    assert calls == []
    assert receipt["actual_provider_request_count"] == 0
    assert receipt["blocked_request_count"] == 1


def test_non_chat_provider_requests_do_not_consume_chat_ceiling(tmp_path):
    calls: list[httpx.Request] = []
    client = _client(calls)
    ledger = ProviderRequestLedger(
        ceiling=0,
        receipt_path=tmp_path / "receipt.json",
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=client,
    )

    proxy.forward(
        method="GET",
        request_path="/v1/models",
        headers={"Authorization": "Bearer SECRET"},
        body=b"",
    )
    assert len(calls) == 1
    assert ledger.snapshot()["actual_provider_request_count"] == 0


def test_receipt_never_persists_api_keys_prompts_or_reasoning_text(tmp_path):
    calls: list[httpx.Request] = []
    client = _client(calls)
    receipt_path = tmp_path / "receipt.json"
    ledger = ProviderRequestLedger(
        ceiling=2,
        receipt_path=receipt_path,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=client,
    )
    secret = "sk-or-v1-THIS-MUST-NEVER-BE-PERSISTED"
    private_prompt = "private customer prompt"
    private_reasoning = "private model reasoning"

    proxy.forward(
        method="POST",
        request_path="/source/p19_manager/v1/chat/completions",
        headers={"Authorization": f"Bearer {secret}"},
        body=json.dumps(
            {
                "messages": [{"role": "user", "content": private_prompt}],
                "reasoning": private_reasoning,
            }
        ).encode(),
    )

    serialized = receipt_path.read_text(encoding="utf-8")
    assert secret not in serialized
    assert private_prompt not in serialized
    assert private_reasoning not in serialized
    receipt = json.loads(serialized)
    assert receipt["privacy_contract"] == {
        "request_headers_persisted": False,
        "request_body_persisted": False,
        "response_body_persisted": False,
        "prompt_text_persisted": False,
        "reasoning_text_persisted": False,
        "api_keys_persisted": False,
    }


def test_numeric_usage_and_cost_are_aggregated_without_response_content(tmp_path):
    calls: list[httpx.Request] = []
    client = _client(calls)
    ledger = ProviderRequestLedger(
        ceiling=1,
        receipt_path=tmp_path / "receipt.json",
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=client,
    )
    proxy.forward(
        method="POST",
        request_path="/source/research_intake/v1/chat/completions",
        headers={},
        body=b"{}",
    )
    receipt = ledger.snapshot()
    assert receipt["prompt_tokens"] == 11
    assert receipt["completion_tokens"] == 7
    assert receipt["reasoning_tokens"] == 3
    assert receipt["provider_reported_cost"] == pytest.approx(0.00123)
    assert receipt["responses_with_usage_telemetry"] == 1


def test_streaming_usage_parser_reads_only_numeric_usage():
    body = (
        b'data: {"choices":[{"delta":{"content":"private"}}]}\n\n'
        b'data: {"usage":{"prompt_tokens":9,"completion_tokens":4,'
        b'"completion_tokens_details":{"reasoning_tokens":2},"cost":0.0004}}\n\n'
        b'data: [DONE]\n\n'
    )
    usage = response_usage("text/event-stream", body)
    assert usage == {
        "prompt_tokens": 9,
        "completion_tokens": 4,
        "reasoning_tokens": 2,
        "provider_reported_cost": pytest.approx(0.0004),
    }


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (
            "/source/research_intake/v1/chat/completions",
            ("research_intake", "/v1/chat/completions"),
        ),
        ("/v1/chat/completions", ("metabase", "/v1/chat/completions")),
        ("/v1/models", ("other", "/v1/models")),
    ],
)
def test_source_routing_is_structural(path, expected):
    assert source_and_upstream_path(path) == expected


def test_source_ceiling_and_unknown_source_fail_before_upstream(tmp_path):
    calls: list[httpx.Request] = []
    ledger = ProviderRequestLedger(
        ceiling=24,
        receipt_path=tmp_path / "receipt.json",
        source_ceilings={
            "research_intake": 1,
            "metabase": 2,
            "p17_manager": 1,
            "p19_manager": 1,
        },
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=_client(calls),
    )
    proxy.forward(
        method="POST",
        request_path="/source/research_intake/v1/chat/completions",
        headers={},
        body=b"{}",
    )
    with pytest.raises(ProviderCeilingExceeded):
        proxy.forward(
            method="POST",
            request_path="/source/research_intake/v1/chat/completions",
            headers={},
            body=b"{}",
        )
    with pytest.raises(ProviderCeilingExceeded):
        proxy.forward(
            method="POST",
            request_path="/source/unexpected/v1/chat/completions",
            headers={},
            body=b"{}",
        )
    receipt = ledger.snapshot()
    assert len(calls) == 1
    assert receipt["actual_provider_request_count"] == 1
    assert receipt["blocked_request_count"] == 2
    assert receipt["source_request_ceilings"]["research_intake"] == 1
    assert receipt["events"][-1]["blocked_reason"] == "PROVIDER_SOURCE_CEILING_EXHAUSTED"


def test_numeric_ceiling_reached_blocks_next_request_locally(tmp_path):
    calls: list[httpx.Request] = []
    ledger = ProviderRequestLedger(
        ceiling=24,
        receipt_path=tmp_path / "receipt.json",
        prompt_token_ceiling=11,
        completion_token_ceiling=16,
        reasoning_token_ceiling=12,
        provider_cost_ceiling=1.0,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=_client(calls),
    )
    proxy.forward(
        method="POST",
        request_path="/v1/chat/completions",
        headers={},
        body=b"{}",
    )
    with pytest.raises(ProviderCeilingExceeded):
        proxy.forward(
            method="POST",
            request_path="/v1/chat/completions",
            headers={},
            body=b"{}",
        )
    receipt = ledger.snapshot()
    assert len(calls) == 1
    assert receipt["prompt_tokens"] == 11
    assert receipt["events"][-1]["blocked_reason"] == "PROVIDER_PROMPT_TOKEN_CEILING_REACHED"


def test_affordable_completion_tokens_extracts_only_numeric_hint():
    body = json.dumps(
        {
            "error": {
                "message": (
                    "This request requires more credits, or fewer max_tokens. "
                    "You requested up to 50000 tokens, but can only afford 7252."
                )
            }
        }
    ).encode()
    assert affordable_completion_tokens(body) == 7252
    assert affordable_completion_tokens(b'{"error":{"message":"other"}}') is None


def test_request_transport_cap_is_separate_from_case_completion_budget(tmp_path):
    calls: list[httpx.Request] = []
    ledger = ProviderRequestLedger(
        ceiling=4,
        receipt_path=tmp_path / "receipt.json",
        completion_token_ceiling=50000,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=_client(calls),
        request_max_tokens=2048,
    )
    proxy.forward(
        method="POST",
        request_path="/source/research_intake/v1/chat/completions",
        headers={},
        body=b'{"messages":[],"max_tokens":50000}',
    )
    forwarded = json.loads(calls[0].content)
    assert forwarded["max_tokens"] == 2048
    receipt = ledger.snapshot()
    assert receipt["completion_token_ceiling"] == 50000
    assert receipt["completion_tokens"] == 7


def test_402_affordability_hint_gets_one_audited_lower_token_retry(tmp_path):
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(
                402,
                headers={"Content-Type": "application/json"},
                json={
                    "error": {
                        "message": (
                            "This request requires more credits, or fewer "
                            "max_tokens. You requested up to 2048 tokens, "
                            "but can only afford 1500."
                        )
                    }
                },
            )
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json"},
            json={
                "choices": [{"message": {"content": "{}"}}],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "cost": 0.001,
                },
            },
        )

    ledger = ProviderRequestLedger(
        ceiling=4,
        receipt_path=tmp_path / "receipt.json",
        completion_token_ceiling=50000,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        request_max_tokens=2048,
    )
    status, _headers, _body = proxy.forward(
        method="POST",
        request_path="/source/research_intake/v1/chat/completions",
        headers={},
        body=b'{"messages":[],"max_tokens":50000}',
    )
    assert status == 200
    assert len(calls) == 2
    assert json.loads(calls[0].content)["max_tokens"] == 2048
    assert json.loads(calls[1].content)["max_tokens"] == 1372
    receipt = ledger.snapshot()
    assert receipt["actual_provider_request_count"] == 2
    assert receipt["transport_affordability_retry_count"] == 1
    assert receipt["last_affordable_completion_tokens"] == 1500
    assert receipt["last_applied_request_max_tokens"] == 1372
    assert [event["upstream_status"] for event in receipt["events"]] == [402, 200]


def test_402_without_numeric_hint_gets_one_512_token_fallback_retry(tmp_path):
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(
                402,
                headers={"Content-Type": "application/json"},
                json={"error": {"message": "OpenRouter has insufficient credits"}},
            )
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json"},
            json={
                "choices": [{"message": {"content": "{}"}}],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "cost": 0.001,
                },
            },
        )

    ledger = ProviderRequestLedger(
        ceiling=4,
        receipt_path=tmp_path / "receipt.json",
        completion_token_ceiling=50000,
    )
    proxy = CountingOpenRouterProxy(
        upstream_base_url="https://provider.invalid/api",
        ledger=ledger,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        request_max_tokens=2048,
    )
    status, _headers, _body = proxy.forward(
        method="POST",
        request_path="/source/research_intake/v1/chat/completions",
        headers={},
        body=b'{"messages":[],"max_tokens":50000}',
    )
    assert status == 200
    assert len(calls) == 2
    assert json.loads(calls[0].content)["max_tokens"] == 2048
    assert json.loads(calls[1].content)["max_tokens"] == 512
    receipt = ledger.snapshot()
    assert receipt["actual_provider_request_count"] == 2
    assert receipt["transport_affordability_retry_count"] == 1
    assert receipt["last_affordable_completion_tokens"] == 0
    assert receipt["last_applied_request_max_tokens"] == 512
    assert receipt["last_affordability_retry_mode"] == "fallback_low_credit"
    assert [event["upstream_status"] for event in receipt["events"]] == [402, 200]
