from __future__ import annotations

import ast
import inspect
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from app.v3.action_authorization import (
    ActionAuthorityError,
    DEFAULT_ACTION_CAPABILITY_REGISTRY,
)
from app.v3.action_connectors.resend_email import (
    RESEND_API_ORIGIN,
    ResendConnectorError,
    ResendEmailConnector,
    ResendEmailRequest,
    ResendSendState,
    ResendTag,
    canonical_provider_payload,
    idempotency_identity,
)
from control_plane.authorize import permissions_for
from control_plane.authorize import Principal

STAMP = datetime(2026, 9, 26, 6, 40, tzinfo=timezone.utc)
EMAIL_ID = "49a3999c-0ce1-4ea6-ab68-afcd6dc2e794"
OTHER_ID = "c11a2b12-c014-41df-9386-2b9b8240cbd5"


def settings():
    return SimpleNamespace(
        resend_api_key="re_provider_free_only",
        resend_from="Dima <cert@dima.example>",
    )


def request(**overrides):
    data = {
        "from_address": "Dima <cert@dima.example>",
        "to": ("delivered@resend.dev",),
        "subject": "Dima connector certification",
        "html": "<p>connector certification</p>",
        "text": "connector certification",
        "tags": (ResendTag(name="purpose", value="connector-certification"),),
    }
    data.update(overrides)
    return ResendEmailRequest(**data)


def connector(handler):
    return ResendEmailConnector(
        settings=settings(),
        transport=httpx.MockTransport(handler),
        timeout_seconds=0.25,
    )


def json_response(status: int, body: dict) -> httpx.Response:
    return httpx.Response(status, json=body)


def principal(role: str):
    return Principal(
        user_id="00000000-0000-4000-8000-000000006001",
        tenant_id="00000000-0000-4000-8000-000000006002",
        tenant_slug="resend-cert",
        roles=[role],
    )


def test_provider_origin_is_fixed_and_request_path_is_fixed():
    seen = {}

    def handler(req: httpx.Request):
        seen["url"] = str(req.url)
        return json_response(200, {"id": EMAIL_ID})

    with connector(handler) as client:
        client.send(request=request(), attempt_id="attempt-1", idempotency_created_at=STAMP)

    assert RESEND_API_ORIGIN == "https://api.resend.com"
    assert seen["url"] == "https://api.resend.com/emails"
    assert "base_url" not in ResendEmailRequest.model_fields
    assert "url" not in ResendEmailRequest.model_fields
    assert "headers" not in ResendEmailRequest.model_fields


def test_credential_is_server_side_and_never_in_provider_payload():
    seen = {}

    def handler(req: httpx.Request):
        seen["auth"] = req.headers["Authorization"]
        seen["body"] = req.content.decode()
        return json_response(200, {"id": EMAIL_ID})

    with connector(handler) as client:
        client.send(request=request(), attempt_id="attempt-2", idempotency_created_at=STAMP)

    assert seen["auth"] == "Bearer re_provider_free_only"
    assert "re_provider_free_only" not in seen["body"]
    assert "api_key" not in ResendEmailRequest.model_fields


def test_missing_trusted_credential_fails_before_network():
    called = False

    def handler(req: httpx.Request):
        nonlocal called
        called = True
        return json_response(200, {"id": EMAIL_ID})

    client = ResendEmailConnector(
        settings=SimpleNamespace(resend_api_key="", resend_from="x@y.test"),
        transport=httpx.MockTransport(handler),
    )
    with client:
        with pytest.raises(ResendConnectorError) as exc:
            client.send(request=request(), attempt_id="attempt-3", idempotency_created_at=STAMP)
    assert exc.value.code == "RESEND_CREDENTIAL_UNAVAILABLE"
    assert called is False


@pytest.mark.parametrize(
    "extra",
    [
        {"base_url": "https://evil.example"},
        {"url": "https://evil.example"},
        {"headers": {"Authorization": "attacker"}},
        {"api_key": "attacker"},
        {"cc": ["person@example.com"]},
        {"bcc": ["person@example.com"]},
    ],
)
def test_typed_request_rejects_arbitrary_transport_or_extra_fields(extra):
    raw = request().model_dump(mode="json")
    raw.update(extra)
    with pytest.raises(ValidationError):
        ResendEmailRequest.model_validate(raw)


def test_canonical_payload_is_stable():
    first, first_fp = canonical_provider_payload(request())
    second, second_fp = canonical_provider_payload(
        request(tags=(ResendTag(value="connector-certification", name="purpose"),))
    )
    assert first == second
    assert first_fp == second_fp


def test_payload_change_changes_fingerprint():
    _, first = canonical_provider_payload(request(subject="First"))
    _, second = canonical_provider_payload(request(subject="Second"))
    assert first != second


def test_idempotency_key_is_deterministic_and_bounded():
    key1, identity1 = idempotency_identity(attempt_id="authz-42", created_at=STAMP)
    key2, identity2 = idempotency_identity(attempt_id="authz-42", created_at=STAMP)
    assert key1 == key2
    assert identity1.key_fingerprint == identity2.key_fingerprint
    assert key1.startswith("dima-action/")
    assert len(key1) <= 256
    assert identity1.expires_at - identity1.created_at == timedelta(hours=24)


def test_different_attempts_have_different_idempotency_keys():
    key1, _ = idempotency_identity(attempt_id="attempt-a", created_at=STAMP)
    key2, _ = idempotency_identity(attempt_id="attempt-b", created_at=STAMP)
    assert key1 != key2


def test_send_emits_idempotency_header_and_captures_provider_id():
    seen = {}

    def handler(req: httpx.Request):
        seen["key"] = req.headers["Idempotency-Key"]
        return json_response(200, {"id": EMAIL_ID})

    with connector(handler) as client:
        result = client.send(
            request=request(),
            attempt_id="attempt-send",
            idempotency_created_at=STAMP,
        )
    expected_key, expected_identity = idempotency_identity(
        attempt_id="attempt-send",
        created_at=STAMP,
    )
    assert seen["key"] == expected_key
    assert result.state == ResendSendState.PROVIDER_ACCEPTED
    assert result.provider_email_id == EMAIL_ID
    assert result.idempotency_key_fingerprint == expected_identity.key_fingerprint


def test_400_invalid_idempotency_key_is_deterministic_error():
    def handler(req: httpx.Request):
        return json_response(400, {"name": "invalid_idempotency_key"})

    with connector(handler) as client:
        with pytest.raises(ResendConnectorError) as exc:
            client.send(request=request(), attempt_id="bad-key", idempotency_created_at=STAMP)
    assert exc.value.code == "RESEND_IDEMPOTENCY_KEY_REJECTED"


def test_409_payload_mismatch_fails_closed():
    def handler(req: httpx.Request):
        return json_response(409, {"name": "invalid_idempotent_request"})

    with connector(handler) as client:
        with pytest.raises(ResendConnectorError) as exc:
            client.send(request=request(), attempt_id="mismatch", idempotency_created_at=STAMP)
    assert exc.value.code == "RESEND_IDEMPOTENCY_IDENTITY_VIOLATION"


def test_409_concurrent_request_is_retryable_only_with_same_identity():
    seen = {}

    def handler(req: httpx.Request):
        seen["key"] = req.headers["Idempotency-Key"]
        return json_response(409, {"name": "concurrent_idempotent_requests"})

    with connector(handler) as client:
        result = client.send(
            request=request(),
            attempt_id="concurrent",
            idempotency_created_at=STAMP,
        )
    key, identity = idempotency_identity(attempt_id="concurrent", created_at=STAMP)
    assert result.state == ResendSendState.RETRYABLE_SAME_KEY
    assert result.provider_email_id is None
    assert seen["key"] == key
    assert result.idempotency_key_fingerprint == identity.key_fingerprint


@pytest.mark.parametrize("exc_type", [httpx.ReadTimeout, httpx.ConnectError])
def test_timeout_or_connection_loss_becomes_unknown_external_state(exc_type):
    def handler(req: httpx.Request):
        raise exc_type("transport uncertain", request=req)

    with connector(handler) as client:
        result = client.send(
            request=request(),
            attempt_id="unknown-state",
            idempotency_created_at=STAMP,
        )
    assert result.state == ResendSendState.UNKNOWN_EXTERNAL_STATE
    assert result.provider_email_id is None


def test_unknown_state_recovery_reuses_exact_same_key_and_payload():
    calls = []

    def handler(req: httpx.Request):
        calls.append((req.headers["Idempotency-Key"], req.content))
        if len(calls) == 1:
            raise httpx.ReadTimeout("uncertain", request=req)
        return json_response(200, {"id": EMAIL_ID})

    req = request()
    with connector(handler) as client:
        first = client.send(
            request=req,
            attempt_id="unknown-recovery",
            idempotency_created_at=STAMP,
        )
        second = client.send(
            request=req,
            attempt_id="unknown-recovery",
            idempotency_created_at=STAMP,
        )

    assert first.state == ResendSendState.UNKNOWN_EXTERNAL_STATE
    assert second.state == ResendSendState.PROVIDER_ACCEPTED
    assert len(calls) == 2
    assert calls[0] == calls[1]


def test_retrieve_uses_provider_id_and_reconciles_identity():
    seen = {}

    def handler(req: httpx.Request):
        seen["method"] = req.method
        seen["url"] = str(req.url)
        return json_response(
            200,
            {
                "id": EMAIL_ID,
                "message_id": "<message@example.test>",
                "to": ["delivered@resend.dev"],
                "from": "Dima <cert@dima.example>",
                "subject": "Dima connector certification",
                "last_event": "delivered",
            },
        )

    with connector(handler) as client:
        result = client.retrieve_email(email_id=EMAIL_ID, expected_request=request())

    assert seen == {
        "method": "GET",
        "url": f"https://api.resend.com/emails/{EMAIL_ID}",
    }
    assert result.provider_email_id == EMAIL_ID
    assert result.message_id == "<message@example.test>"
    assert result.reconciled is True


@pytest.mark.parametrize(
    "override",
    [
        {"id": OTHER_ID},
        {"to": ["other@resend.dev"]},
        {"from": "Other <other@example.test>"},
        {"subject": "Different"},
    ],
)
def test_retrieve_mismatch_fails_reconciliation(override):
    body = {
        "id": EMAIL_ID,
        "to": ["delivered@resend.dev"],
        "from": "Dima <cert@dima.example>",
        "subject": "Dima connector certification",
    }
    body.update(override)

    def handler(req: httpx.Request):
        return json_response(200, body)

    with connector(handler) as client:
        with pytest.raises(ResendConnectorError) as exc:
            client.retrieve_email(email_id=EMAIL_ID, expected_request=request())
    assert exc.value.code == "RESEND_RECONCILIATION_MISMATCH"


def test_retrieve_rejects_non_uuid_before_network():
    called = False

    def handler(req: httpx.Request):
        nonlocal called
        called = True
        return json_response(200, {})

    with connector(handler) as client:
        with pytest.raises(ResendConnectorError) as exc:
            client.retrieve_email(
                email_id="../../evil",
                expected_request=request(),
            )
    assert exc.value.code == "RESEND_EMAIL_ID_INVALID"
    assert called is False


def test_retrieve_transport_failure_is_reconciliation_unavailable():
    def handler(req: httpx.Request):
        raise httpx.ReadTimeout("read uncertain", request=req)

    with connector(handler) as client:
        with pytest.raises(ResendConnectorError) as exc:
            client.retrieve_email(email_id=EMAIL_ID, expected_request=request())
    assert exc.value.code == "RESEND_RECONCILIATION_UNAVAILABLE"


def test_default_action_registry_remains_empty_for_real_resend_action():
    with pytest.raises(ActionAuthorityError) as exc:
        DEFAULT_ACTION_CAPABILITY_REGISTRY.require("notification.email.send.v1")
    assert exc.value.code == "ACTION_CAPABILITY_UNAVAILABLE"


def test_action_execute_permission_does_not_exist():
    for role in ("viewer", "analyst", "admin", "owner"):
        assert "action:execute" not in permissions_for(principal(role))


def test_connector_is_not_an_action_executor_or_durable_owner():
    source = Path("app/v3/action_connectors/resend_email.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
            imported.update(alias.name for alias in node.names)

    forbidden = (
        "app.v3.action_authorization",
        "app.v3.decision_adoption",
        "app.v3.decision_intelligence",
        "app.v3.report_document",
        "app.v3.substrate.metabase",
        "app.v3.research",
        "app.wren",
        "sqlmodel",
        "sqlalchemy",
        "numpy",
        "pandas",
        "scipy",
        "statistics",
    )
    assert not any(name.startswith(forbidden) for name in imports)
    assert "ActionAuthorizationRecord" not in imported
    assert "DecisionAdoptionRecord" not in imported

    for token in (
        "ActionExecutionReceipt",
        "ActionAttempt",
        "action:execute",
        "DecisionAdoptionRecord(",
        "ActionAuthorizationRecord(",
        "DecisionBriefRecord(",
        "ReportDocumentRecord(",
        "DimaQueryReceipt(",
        "EvidenceArtifact(",
        "ResearchClaimRecord(",
        "RootCauseAssessment(",
        "openrouter",
        "openai/gpt",
        "Luna",
        "Sol",
        "C1",
    ):
        assert token not in source


def test_connector_constructor_exposes_no_provider_origin_override():
    parameters = inspect.signature(ResendEmailConnector).parameters
    assert "base_url" not in parameters
    assert "origin" not in parameters
    assert "url" not in parameters
