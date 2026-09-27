"""Provider-free D10-E live Product control and answer-now contracts."""

from __future__ import annotations

import pytest

from app.v2.product_control import ProductControlError, ProductRunControlRegistry
from app.v2.product_models import ProductControlAction


def test_live_control_is_principal_and_tenant_bound():
    registry = ProductRunControlRegistry(max_active=2)
    control = registry.register(
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
    )

    same = registry.resolve(
        control.control_ref,
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
    )
    assert same is control

    for principal, tenant in (
        ("user-b", "id:tenant-a"),
        ("user-a", "id:tenant-b"),
    ):
        with pytest.raises(ProductControlError, match="not found"):
            registry.resolve(
                control.control_ref,
                principal_subject=principal,
                tenant_binding=tenant,
            )


def test_answer_now_and_cancel_are_ephemeral_signals_not_run_state():
    registry = ProductRunControlRegistry()
    control = registry.register(
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
    )

    assert control.answer_now_requested() is False
    assert control.cancelled() is False

    registry.signal(
        control.control_ref,
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
        action=ProductControlAction.ANSWER_NOW,
    )
    assert control.answer_now_requested() is True
    assert control.cancelled() is False

    registry.signal(
        control.control_ref,
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
        action=ProductControlAction.CANCEL,
    )
    assert control.cancelled() is True

    registry.release(control.control_ref)
    with pytest.raises(ProductControlError, match="not found"):
        registry.resolve(
            control.control_ref,
            principal_subject="user-a",
            tenant_binding="id:tenant-a",
        )


def test_registry_refuses_capacity_instead_of_evicting_active_control():
    registry = ProductRunControlRegistry(max_active=1)
    first = registry.register(
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
    )

    with pytest.raises(ProductControlError, match="capacity"):
        registry.register(
            principal_subject="user-b",
            tenant_binding="id:tenant-b",
        )

    # First active control remains intact; no silent eviction.
    assert registry.resolve(
        first.control_ref,
        principal_subject="user-a",
        tenant_binding="id:tenant-a",
    ) is first
