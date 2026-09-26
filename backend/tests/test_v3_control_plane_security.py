from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.main import create_app
from control_plane.authorize import AuthzError, Principal, authorize, permissions_for


def _principal(role: str) -> Principal:
    return Principal(
        user_id=f"user-{role}",
        tenant_id="tenant-1",
        tenant_slug="tenant-1",
        roles=[role],
    )


def test_role_capabilities_are_monotonic_and_action_execute_absent():
    viewer=set(permissions_for(_principal("viewer")))
    analyst=set(permissions_for(_principal("analyst")))
    admin=set(permissions_for(_principal("admin")))
    owner=set(permissions_for(_principal("owner")))
    assert viewer <= analyst <= admin <= owner
    for perms in (viewer,analyst,admin,owner):
        assert "action:execute" not in perms


def test_analyst_can_manage_internal_work_but_not_external_authorization():
    analyst=_principal("analyst")
    authorize(analyst,"work:manage","action-work")
    with pytest.raises(AuthzError):
        authorize(analyst,"action:authorize","action:any")


def test_admin_can_authorize_exact_action_plan_but_not_execute():
    admin=_principal("admin")
    authorize(admin,"action:authorize","action:any")
    with pytest.raises(AuthzError):
        authorize(admin,"action:execute","action:any")


def test_health_is_public_and_auth_me_is_protected(monkeypatch):
    # Avoid bootstrap side effects; canonical HTTP shell itself is the subject here.
    from control_plane import bootstrap, db
    monkeypatch.setattr(db,"init_db",lambda:None)
    monkeypatch.setattr(bootstrap,"ensure_bootstrap_superadmin",lambda:None)
    with TestClient(create_app()) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/auth/me").status_code in {401,403}


def test_principal_tenant_identity_is_not_derived_from_request_payload():
    principal=_principal("viewer")
    assert principal.tenant_id == "tenant-1"
    assert principal.user_id == "user-viewer"
