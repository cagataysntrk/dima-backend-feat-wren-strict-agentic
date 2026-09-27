"""Day15 tenant pilot / rollback policy.

This module decides admission only. It never mutates canonical V2 state and never
implements a per-request fallback to legacy execution.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from app.v2.models import FrozenModel


class PilotAdmissionMode(StrEnum):
    DISABLED = "DISABLED"
    DEVELOPMENT_MASTER = "DEVELOPMENT_MASTER"
    TENANT_PILOT = "TENANT_PILOT"


class PilotDecision(FrozenModel):
    enabled: bool
    mode: PilotAdmissionMode
    tenant_binding: str
    pipeline: str
    reason: str
    contract_version: str = Field(min_length=1)


class PilotConfigurationReceipt(FrozenModel):
    master_enabled: bool
    pilot_enabled: bool
    pilot_tenants: tuple[str, ...]
    contract_version: str
    rollback_behavior: str = (
        "disable new Ask-V2 work; preserve immutable contracts/evidence/reports/checkpoints"
    )
    request_level_legacy_fallback: bool = False


def _tenant_binding(principal) -> str:
    tenant_id = getattr(principal, "tenant_id", None)
    if tenant_id is not None:
        return f"id:{tenant_id}"
    return f"slug:{getattr(principal, 'tenant_slug', '') or ''}"


def configured_pilot_tenants(settings) -> tuple[str, ...]:
    raw = str(getattr(settings, "ask_v2_pilot_tenants", "") or "")
    return tuple(
        dict.fromkeys(
            item.strip()
            for item in raw.split(",")
            if item.strip()
        )
    )


def configuration_receipt(settings) -> PilotConfigurationReceipt:
    return PilotConfigurationReceipt(
        master_enabled=bool(getattr(settings, "ask_v2_enabled", False)),
        pilot_enabled=bool(
            getattr(settings, "ask_v2_pilot_enabled", False)
        ),
        pilot_tenants=configured_pilot_tenants(settings),
        contract_version=str(
            getattr(
                settings,
                "ask_v2_pilot_contract_version",
                "day15-pilot-v1",
            )
        ),
    )


def evaluate_pilot(settings, principal) -> PilotDecision:
    binding = _tenant_binding(principal)
    version = str(
        getattr(
            settings,
            "ask_v2_pilot_contract_version",
            "day15-pilot-v1",
        )
    )
    if not bool(getattr(settings, "ask_v2_enabled", False)):
        return PilotDecision(
            enabled=False,
            mode=PilotAdmissionMode.DISABLED,
            tenant_binding=binding,
            pipeline="disabled",
            reason="Ask-V2 master switch is OFF",
            contract_version=version,
        )

    if not bool(getattr(settings, "ask_v2_pilot_enabled", False)):
        # Preserve the sealed Day10 development/dark-launch master behavior. The actual
        # pilot layer is still OFF and no tenant is claimed as activated.
        return PilotDecision(
            enabled=True,
            mode=PilotAdmissionMode.DEVELOPMENT_MASTER,
            tenant_binding=binding,
            pipeline="v2",
            reason="Day10 master enabled; tenant pilot layer OFF",
            contract_version=version,
        )

    allowlist = frozenset(configured_pilot_tenants(settings))
    if binding not in allowlist:
        return PilotDecision(
            enabled=False,
            mode=PilotAdmissionMode.TENANT_PILOT,
            tenant_binding=binding,
            pipeline="disabled",
            reason="tenant is outside Ask-V2 pilot envelope",
            contract_version=version,
        )

    return PilotDecision(
        enabled=True,
        mode=PilotAdmissionMode.TENANT_PILOT,
        tenant_binding=binding,
        pipeline="v2",
        reason="tenant admitted by explicit Ask-V2 pilot envelope",
        contract_version=version,
    )
