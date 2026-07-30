"""#59 — bildirim/teslim logu: notify() control-plane'e yazar + /sadmin/notifications
filtreli okur. Admin plane AYRI servis → ortak store Postgres (ADR-0020)."""

from __future__ import annotations

import pytest

from tests.conftest import TEST_SUPERADMIN
from tests.test_auth import _ensure_test_users


@pytest.fixture(scope="module")
def admin_client():
    from fastapi.testclient import TestClient

    from admin_app.main import create_app

    with TestClient(create_app()) as c:
        _ensure_test_users()
        yield c


def _h(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_notify_writes_to_db_and_admin_lists(admin_client):
    from app.schedules import ScheduleStore
    from control_plane.db import init_db

    init_db()
    store = ScheduleStore("test-co")  # tek-kaynak DB (dosya-yolu param'ı yok)
    rec = store.notify({
        "schedule_id": "s-abc", "tenant_id": None, "kind": "anomaly",
        "message": "⚠ enerji: olağandışı değerler", "row_count": 3,
        "delivery": [{"channel": "email", "ok": True, "to": ["a@x.com"], "provider_id": "em_1"}],
    })
    assert rec["id"] is not None  # DB'nin atadığı id döner (tek-kaynak; jsonl dual-write kaldırıldı)

    h = _h(admin_client)
    out = admin_client.get("/sadmin/notifications?company=test-co", headers=h).json()
    assert out["total"] >= 1
    item = next(i for i in out["items"] if i["schedule_id"] == "s-abc")
    assert item["kind"] == "anomaly"
    assert item["delivery"][0]["channel"] == "email" and item["delivery"][0]["ok"] is True
    assert "anomaly" in out["facets"]["kinds"]


def test_admin_notifications_filter_kind(admin_client):
    h = _h(admin_client)
    out = admin_client.get("/sadmin/notifications?kind=anomaly", headers=h).json()
    assert all(i["kind"] == "anomaly" for i in out["items"])


def test_admin_notifications_public_plane_forbidden(client):
    # Public plane'den erişilemez (admin-only yüzey).
    assert client.get("/sadmin/notifications").status_code in (401, 403, 404)
