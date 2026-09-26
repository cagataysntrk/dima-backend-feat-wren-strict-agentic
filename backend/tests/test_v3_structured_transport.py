from __future__ import annotations

import json

import httpx
import pytest

from app.v3.structured_trace import (
    build_provider_bound_payload,
    request_identity,
)
from app.v3.structured_transport import (
    OpenRouterStructuredJSONTransport,
    StructuredProviderError,
    schema_fingerprint,
    validate_provider_strict_schema,
)


API_KEY = "sk-or-v1-super-secret-1234567890"
MODEL = "openai/gpt-5.6-luna"
SYSTEM = "SYSTEM SECRET PROMPT DO NOT LEAK"
USER = "USER SECRET PROMPT DO NOT LEAK"
SCHEMA_NAME = "diagnostic_schema"
SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string"},
    },
    "required": ["value"],
    "additionalProperties": False,
}


def _transport(handler):
    return OpenRouterStructuredJSONTransport(
        api_key=API_KEY,
        model=MODEL,
        transport=httpx.MockTransport(handler),
        timeout_seconds=0.1,
    )


def _call(client, *, schema=SCHEMA):
    return client.structured_json(
        SYSTEM,
        USER,
        schema=schema,
        schema_name=SCHEMA_NAME,
    )


def test_400_structured_json_error_retains_bounded_typed_diagnostic():
    def handler(request: httpx.Request):
        return httpx.Response(
            400,
            headers={"x-request-id": "req_123"},
            json={
                "error": {
                    "code": "invalid_request",
                    "message": "response format rejected",
                    "metadata": {"provider": "example"},
                }
            },
        )

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)

    error = caught.value
    assert error.code == "COGNITION_PROVIDER_REJECTED"
    assert error.detail == "provider returned HTTP 400"
    assert error.diagnostic is not None
    diagnostic = error.diagnostic
    assert diagnostic.status_code == 400
    assert diagnostic.provider_error_code == "invalid_request"
    assert diagnostic.provider_error_message == "response format rejected"
    assert diagnostic.provider_error_metadata == {"provider": "example"}
    assert diagnostic.provider_request_id == "req_123"
    assert diagnostic.model == MODEL
    assert diagnostic.schema_name == SCHEMA_NAME
    assert diagnostic.response_format_family == "json_schema"
    assert diagnostic.schema_fingerprint == schema_fingerprint(SCHEMA)
    assert diagnostic.bounded_response_excerpt is None


def test_nested_provider_metadata_is_sanitized_and_bounded():
    huge = "x" * 12000

    def handler(request: httpx.Request):
        return httpx.Response(
            400,
            json={
                "error": {
                    "code": "provider_error",
                    "message": "bad request",
                    "metadata": {
                        "nested": {
                            "safe": huge,
                            "Authorization": f"Bearer {API_KEY}",
                            "api_key": API_KEY,
                            "system_prompt": SYSTEM,
                            "user_prompt": USER,
                        }
                    },
                }
            },
        )

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)

    diagnostic = caught.value.diagnostic
    assert diagnostic is not None
    serialized = json.dumps(
        diagnostic.provider_error_metadata,
        ensure_ascii=False,
        sort_keys=True,
    )
    assert len(serialized.encode("utf-8")) <= 8192
    assert API_KEY not in serialized
    assert SYSTEM not in serialized
    assert USER not in serialized
    assert "Bearer " + API_KEY not in serialized
    assert "[REDACTED]" in serialized


def test_plain_text_error_retains_only_bounded_sanitized_excerpt():
    body = (
        "provider plain error "
        + API_KEY
        + " "
        + SYSTEM
        + " "
        + USER
        + " "
        + ("z" * 12000)
    )

    def handler(request: httpx.Request):
        return httpx.Response(400, text=body)

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)

    diagnostic = caught.value.diagnostic
    assert diagnostic is not None
    excerpt = diagnostic.bounded_response_excerpt
    assert excerpt is not None
    assert len(excerpt.encode("utf-8")) <= 8192
    assert API_KEY not in excerpt
    assert SYSTEM not in excerpt
    assert USER not in excerpt
    assert diagnostic.provider_error_metadata is None


def test_response_over_8kb_is_deterministically_truncated():
    body = "A" * 10000

    def handler(request: httpx.Request):
        return httpx.Response(400, text=body)

    excerpts = []
    for _ in range(2):
        with _transport(handler) as client:
            with pytest.raises(StructuredProviderError) as caught:
                _call(client)
        excerpt = caught.value.diagnostic.bounded_response_excerpt
        assert excerpt is not None
        excerpts.append(excerpt)

    assert excerpts[0] == excerpts[1]
    assert len(excerpts[0].encode("utf-8")) == 8192


def test_authorization_api_key_and_prompts_never_appear_in_diagnostic():
    def handler(request: httpx.Request):
        return httpx.Response(
            400,
            json={
                "error": {
                    "code": "x",
                    "message": (
                        f"Bearer {API_KEY} :: {SYSTEM} :: {USER}"
                    ),
                    "metadata": {
                        "headers": {
                            "Authorization": f"Bearer {API_KEY}",
                        },
                        "api_key": API_KEY,
                        "system": SYSTEM,
                        "user": USER,
                    },
                }
            },
        )

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)

    diagnostic = caught.value.diagnostic
    assert diagnostic is not None
    serialized = json.dumps(
        diagnostic.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
    )
    for forbidden in (API_KEY, SYSTEM, USER, f"Bearer {API_KEY}"):
        assert forbidden not in serialized


def test_schema_fingerprint_is_deterministic_under_key_order():
    a = {
        "type": "object",
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "integer"},
        },
    }
    b = {
        "properties": {
            "b": {"type": "integer"},
            "a": {"type": "string"},
        },
        "type": "object",
    }
    assert schema_fingerprint(a) == schema_fingerprint(b)


def test_different_schema_has_different_fingerprint():
    a = {"type": "object", "properties": {"a": {"type": "string"}}}
    b = {"type": "object", "properties": {"a": {"type": "integer"}}}
    assert schema_fingerprint(a) != schema_fingerprint(b)


def test_successful_structured_output_behavior_is_unchanged():
    raw = '{"value":"ok"}'

    def handler(request: httpx.Request):
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": raw}}]},
        )

    with _transport(handler) as client:
        result = _call(client)

    assert result == raw
    assert client.call_count == 1


def test_timeout_error_code_and_detail_are_unchanged():
    def handler(request: httpx.Request):
        raise httpx.ReadTimeout("timeout", request=request)

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)

    assert caught.value.code == "COGNITION_TIMEOUT"
    assert caught.value.detail == "structured cognition request timed out"
    assert caught.value.diagnostic is None


def test_transport_error_code_and_detail_are_unchanged():
    def handler(request: httpx.Request):
        raise httpx.ConnectError("connect", request=request)

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)

    assert caught.value.code == "COGNITION_TRANSPORT_FAILED"
    assert caught.value.detail == "structured cognition transport failed"
    assert caught.value.diagnostic is None


def test_request_payload_still_uses_same_sealed_structured_parameters():
    seen = {}

    def handler(request: httpx.Request):
        seen["json"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": '{"value":"ok"}'}}
                ]
            },
        )

    with _transport(handler) as client:
        _call(client)

    assert seen["json"]["model"] == MODEL
    assert seen["json"]["provider"] == {"require_parameters": True}
    assert seen["json"]["reasoning"] == {"enabled": False}
    assert seen["json"]["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": SCHEMA_NAME,
            "strict": True,
            "schema": SCHEMA,
        },
    }



def test_equivalent_requests_have_same_envelope_identity_across_instances():
    traces = []

    def handler(request: httpx.Request):
        return httpx.Response(
            200,
            headers={"x-request-id": "req_same"},
            json={
                "provider": "provider-a",
                "choices": [{"message": {"content": '{"value":"ok"}'}}],
            },
        )

    for _ in range(2):
        with OpenRouterStructuredJSONTransport(
            api_key=API_KEY,
            model=MODEL,
            owner="p17_research_manager",
            transport=httpx.MockTransport(handler),
        ) as client:
            _call(client)
            traces.append(client.last_trace)

    assert traces[0] is not None
    assert traces[1] is not None
    assert (
        traces[0].request_envelope_fingerprint
        == traces[1].request_envelope_fingerprint
    )
    assert traces[0].schema_fingerprint == traces[1].schema_fingerprint
    assert traces[0].system_prompt_hash == traces[1].system_prompt_hash
    assert traces[0].user_prompt_hash == traces[1].user_prompt_hash
    assert traces[0].provider_backend_identity == "provider-a"
    assert traces[0].provider_request_id == "req_same"
    assert traces[0].http_status == 200


def test_schema_prompt_and_routing_differences_change_expected_fingerprints():
    base_payload = build_provider_bound_payload(
        model=MODEL,
        system=SYSTEM,
        user=USER,
        schema=SCHEMA,
        schema_name=SCHEMA_NAME,
        max_tokens=4096,
        provider_routing_policy={"require_parameters": True},
    )
    base = request_identity(
        owner="p17_research_manager",
        payload=base_payload,
        schema_name=SCHEMA_NAME,
        schema=SCHEMA,
        system=SYSTEM,
        user=USER,
        call_ordinal_by_role=1,
    )

    changed_schema = {
        "type": "object",
        "properties": {"value": {"type": "integer"}},
        "required": ["value"],
        "additionalProperties": False,
    }
    schema_payload = build_provider_bound_payload(
        model=MODEL,
        system=SYSTEM,
        user=USER,
        schema=changed_schema,
        schema_name=SCHEMA_NAME,
        max_tokens=4096,
        provider_routing_policy={"require_parameters": True},
    )
    schema_identity = request_identity(
        owner="p17_research_manager",
        payload=schema_payload,
        schema_name=SCHEMA_NAME,
        schema=changed_schema,
        system=SYSTEM,
        user=USER,
        call_ordinal_by_role=1,
    )
    assert schema_identity.schema_fingerprint != base.schema_fingerprint
    assert (
        schema_identity.request_envelope_fingerprint
        != base.request_envelope_fingerprint
    )

    prompt_payload = build_provider_bound_payload(
        model=MODEL,
        system=SYSTEM,
        user=USER + " changed",
        schema=SCHEMA,
        schema_name=SCHEMA_NAME,
        max_tokens=4096,
        provider_routing_policy={"require_parameters": True},
    )
    prompt_identity = request_identity(
        owner="p17_research_manager",
        payload=prompt_payload,
        schema_name=SCHEMA_NAME,
        schema=SCHEMA,
        system=SYSTEM,
        user=USER + " changed",
        call_ordinal_by_role=1,
    )
    assert prompt_identity.user_prompt_hash != base.user_prompt_hash
    assert prompt_identity.system_prompt_hash == base.system_prompt_hash
    assert (
        prompt_identity.request_envelope_fingerprint
        != base.request_envelope_fingerprint
    )

    routing_payload = build_provider_bound_payload(
        model=MODEL,
        system=SYSTEM,
        user=USER,
        schema=SCHEMA,
        schema_name=SCHEMA_NAME,
        max_tokens=4096,
        provider_routing_policy={
            "require_parameters": True,
            "data_collection": "deny",
        },
    )
    routing_identity = request_identity(
        owner="p17_research_manager",
        payload=routing_payload,
        schema_name=SCHEMA_NAME,
        schema=SCHEMA,
        system=SYSTEM,
        user=USER,
        call_ordinal_by_role=1,
    )
    assert (
        routing_identity.provider_routing_policy_fingerprint
        != base.provider_routing_policy_fingerprint
    )
    assert (
        routing_identity.request_envelope_fingerprint
        != base.request_envelope_fingerprint
    )


def test_call_ordinal_is_telemetry_not_provider_envelope_identity():
    payload = build_provider_bound_payload(
        model=MODEL,
        system=SYSTEM,
        user=USER,
        schema=SCHEMA,
        schema_name=SCHEMA_NAME,
        max_tokens=4096,
    )
    first = request_identity(
        owner="p17_research_manager",
        payload=payload,
        schema_name=SCHEMA_NAME,
        schema=SCHEMA,
        system=SYSTEM,
        user=USER,
        call_ordinal_by_role=1,
    )
    later = request_identity(
        owner="p17_research_manager",
        payload=payload,
        schema_name=SCHEMA_NAME,
        schema=SCHEMA,
        system=SYSTEM,
        user=USER,
        call_ordinal_by_role=9,
    )
    assert first.call_ordinal_by_role == 1
    assert later.call_ordinal_by_role == 9
    assert (
        first.request_envelope_fingerprint
        == later.request_envelope_fingerprint
    )


def test_trace_contains_no_raw_prompt_or_credential_material():
    def handler(request: httpx.Request):
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"value":"ok"}'}}]},
        )

    with OpenRouterStructuredJSONTransport(
        api_key=API_KEY,
        model=MODEL,
        owner="p17_research_manager",
        transport=httpx.MockTransport(handler),
    ) as client:
        _call(client)
        trace = client.last_trace

    assert trace is not None
    serialized = json.dumps(trace.model_dump(mode="json"), sort_keys=True)
    assert API_KEY not in serialized
    assert SYSTEM not in serialized
    assert USER not in serialized
    assert trace.owner == "p17_research_manager"
    assert len(trace.system_prompt_hash) == 64
    assert len(trace.user_prompt_hash) == 64
    assert len(trace.request_envelope_fingerprint) == 64


def test_rejected_call_trace_matches_diagnostic_request_identity():
    def handler(request: httpx.Request):
        return httpx.Response(
            400,
            headers={
                "x-request-id": "req_bad",
                "x-openrouter-provider": "provider-b",
            },
            json={
                "error": {
                    "code": "invalid_request",
                    "message": "schema rejected",
                }
            },
        )

    with OpenRouterStructuredJSONTransport(
        api_key=API_KEY,
        model=MODEL,
        owner="p17_research_manager",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client)
        trace = client.last_trace

    diagnostic = caught.value.diagnostic
    assert diagnostic is not None
    assert trace is not None
    assert (
        trace.request_envelope_fingerprint
        == diagnostic.request_envelope_fingerprint
    )
    assert trace.schema_fingerprint == diagnostic.schema_fingerprint
    assert trace.provider_request_id == "req_bad"
    assert trace.provider_backend_identity == "provider-b"
    assert trace.http_status == 400
    assert trace.provider_error_code == "invalid_request"
    assert trace.provider_error_message == "schema rejected"



def test_recursive_schema_guard_rejects_open_nested_object_before_network():
    called = False

    def handler(request: httpx.Request):
        nonlocal called
        called = True
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"value":"ok"}'}}]},
        )

    unsafe = {
        "type": "object",
        "properties": {
            "proposition": {
                "type": "object",
                "additionalProperties": True,
            }
        },
        "required": ["proposition"],
        "additionalProperties": False,
    }

    with _transport(handler) as client:
        with pytest.raises(StructuredProviderError) as caught:
            _call(client, schema=unsafe)
        assert client.call_count == 0

    assert called is False
    assert caught.value.code == "COGNITION_PROVIDER_SCHEMA_UNSAFE"
    assert "properties.proposition" in caught.value.detail


def test_recursive_schema_guard_rejects_unsupported_object_control_keyword():
    unsafe = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
        "patternProperties": {"^x": {"type": "string"}},
    }

    with pytest.raises(StructuredProviderError) as caught:
        validate_provider_strict_schema(unsafe)

    assert caught.value.code == "COGNITION_PROVIDER_SCHEMA_UNSAFE"
    assert "patternProperties" in caught.value.detail


def test_recursive_schema_guard_accepts_closed_refs_and_arrays():
    safe = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {"$ref": "#/$defs/Item"},
            }
        },
        "required": ["items"],
        "additionalProperties": False,
        "$defs": {
            "Item": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            }
        },
    }

    validate_provider_strict_schema(safe)
