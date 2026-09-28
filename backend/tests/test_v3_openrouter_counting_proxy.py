from __future__ import annotations

import json

import httpx
import pytest

from lab.metabase.core_b.runtime.openrouter_counting_proxy import (
    CountingOpenRouterProxy,
    ProviderCeilingExceeded,
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
