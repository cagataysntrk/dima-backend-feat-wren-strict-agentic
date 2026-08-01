"""Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-14) — `app/routers/health.py` (health/
health-ready/features) için özel bir test dosyası yoktu (yalnız başka testlerde incidental
kullanılıyordu). `/health` ve `/health/ready` load-balancer/orkestrasyon için kritik
(yanlış bir 200/503 trafiği yanlış yönlendirir) — burada doğrudan test edilir."""

from __future__ import annotations


def test_health_always_200(client):
    """Liveness: bağımlılık kontrolü YAPMAZ, süreç ayaktaysa her zaman 200."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_ready_ok_when_mdl_and_db_fine(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["mdl_ready"] is True
    assert body["db_ready"] is True
    assert "db_error" not in body


def test_health_ready_503_when_db_down(client, monkeypatch):
    """Readiness DB erişilemezse 503 dönmeli (prod'da Postgres down artık sessizce
    200 dönmüyor — bkz. health.py docstring'i)."""
    import app.routers.health as health_mod

    monkeypatch.setattr(health_mod, "_db_ping", lambda: (False, "connection refused"))
    r = client.get("/health/ready")
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "degraded"
    assert body["db_ready"] is False
    assert body["db_error"] == "connection refused"


def test_health_ready_503_when_mdl_missing(client, monkeypatch, tmp_path):
    """MDL derlenmemiş/silinmişse de degraded (503) — yalnız DB değil, ikisi de şart."""
    fake_mdl = tmp_path / "hic-var-olmayan-mdl.json"
    monkeypatch.setattr(
        type(client.app.state.wren), "mdl_path",
        property(lambda self: fake_mdl),
    )
    r = client.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["mdl_ready"] is False
