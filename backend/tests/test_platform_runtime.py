from __future__ import annotations

from control_plane.audit_chain import GENESIS, kayit_hash
from control_plane.model_access import karar


def test_canonical_health_shell(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "product": "dima-metabase-platform",
        "ui": "not_implemented",
    }


def test_authenticated_identity_shell(client):
    response = client.get("/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "test@dima.local"
    assert body["tenant_id"]
    assert "analyst" not in body["roles"] or isinstance(body["roles"], list)


def test_model_access_allowlist_semantics_are_fail_closed_once_configured():
    assert karar({"sales"}, None)[0] is True
    assert karar({"sales"}, {"sales"})[0] is True
    allowed, reason = karar({"sales"}, set())
    assert allowed is False
    assert "sales" in reason


def test_audit_hash_is_canonical_and_mutation_sensitive():
    payload_a = {
        "tenant_id": "tenant-a",
        "action": "read",
        "rows_returned": 2,
    }
    payload_b = {
        "rows_returned": 2,
        "action": "read",
        "tenant_id": "tenant-a",
    }
    first = kayit_hash(payload_a, GENESIS)
    second = kayit_hash(payload_b, GENESIS)
    changed = kayit_hash({**payload_a, "rows_returned": 3}, GENESIS)
    assert first == second
    assert first != changed
