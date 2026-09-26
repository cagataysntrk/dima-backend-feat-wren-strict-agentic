"""Day15 tenant pilot / rollback provider-free contract."""

from __future__ import annotations

from types import SimpleNamespace

from app.v2.persistence import (
    CanonicalResumeState,
    CheckpointScope,
    DurableCheckpointStore,
)
from app.v2.pilot import (
    PilotAdmissionMode,
    configuration_receipt,
    evaluate_pilot,
)


def _principal(*, tenant_id="tenant-a", user_id="user-a"):
    return SimpleNamespace(
        tenant_id=tenant_id,
        tenant_slug=None,
        user_id=user_id,
    )


def _settings(**updates):
    values = {
        "ask_v2_enabled": False,
        "ask_v2_pilot_enabled": False,
        "ask_v2_pilot_tenants": "",
        "ask_v2_pilot_contract_version": "day15-pilot-v1",
    }
    values.update(updates)
    return SimpleNamespace(**values)


def test_comparison_seal_configuration_is_dark_by_default():
    decision = evaluate_pilot(_settings(), _principal())
    receipt = configuration_receipt(_settings())

    assert decision.enabled is False
    assert decision.mode == PilotAdmissionMode.DISABLED
    assert decision.pipeline == "disabled"
    assert receipt.master_enabled is False
    assert receipt.pilot_enabled is False
    assert receipt.request_level_legacy_fallback is False


def test_tenant_pilot_requires_exact_allowlist_and_never_falls_back_to_legacy():
    settings = _settings(
        ask_v2_enabled=True,
        ask_v2_pilot_enabled=True,
        ask_v2_pilot_tenants="id:tenant-a,id:tenant-c",
    )

    admitted = evaluate_pilot(settings, _principal(tenant_id="tenant-a"))
    denied = evaluate_pilot(settings, _principal(tenant_id="tenant-b"))

    assert admitted.enabled is True
    assert admitted.mode == PilotAdmissionMode.TENANT_PILOT
    assert admitted.pipeline == "v2"

    assert denied.enabled is False
    assert denied.mode == PilotAdmissionMode.TENANT_PILOT
    assert denied.pipeline == "disabled"
    assert denied.pipeline != "legacy"


def test_day10_development_master_remains_compatible_when_pilot_layer_off():
    decision = evaluate_pilot(
        _settings(ask_v2_enabled=True),
        _principal(),
    )

    assert decision.enabled is True
    assert decision.mode == PilotAdmissionMode.DEVELOPMENT_MASTER
    assert decision.pipeline == "v2"


def test_rollback_switch_does_not_delete_durable_authoritative_state(tmp_path):
    scope = CheckpointScope(
        tenant_binding="id:tenant-a",
        principal_subject="user-a",
        session_id="s",
        thread_id="t",
        context_version="ctx",
        lineage_id="atl",
    )
    store = DurableCheckpointStore(tmp_path)
    before = store.commit(
        scope=scope,
        state=CanonicalResumeState(),
        expected_revision=0,
    )

    disabled = evaluate_pilot(_settings(), _principal())
    after = store.load(scope)

    assert disabled.enabled is False
    assert after == before


def test_pilot_configuration_receipt_is_machine_readable_and_explicit():
    receipt = configuration_receipt(
        _settings(
            ask_v2_enabled=True,
            ask_v2_pilot_enabled=True,
            ask_v2_pilot_tenants="id:tenant-a, id:tenant-b,id:tenant-a",
        )
    )

    assert receipt.pilot_tenants == ("id:tenant-a", "id:tenant-b")
    assert receipt.contract_version == "day15-pilot-v1"
    assert receipt.request_level_legacy_fallback is False
    assert "preserve immutable" in receipt.rollback_behavior
