"""Auth golden testleri (ADR-0014/0015) — güvenlik-kritik kod testsiz kalamaz.

Kapsam: login kapıları (superadmin/public ayrımı, MFA, rate limit), refresh
rotation + reuse detection + grace + family cap, plane secret izolasyonu,
audit izleri, VQR kimlik damgası.
"""

from __future__ import annotations

import time
from datetime import timedelta

import pytest
from sqlmodel import Session, select

from tests.conftest import (
    TEST_SUPERADMIN,
    TEST_USER,
    _ensure_test_users,
    make_tenant_user,
)


@pytest.fixture(autouse=True)
def _clean_limiter():
    from control_plane.ratelimit import login_limiter

    login_limiter.clear()
    yield
    login_limiter.clear()


@pytest.fixture()
def anon(client):
    """Aynı app üzerinde kimliksiz, çerezleri izole ikinci istemci."""
    from fastapi.testclient import TestClient

    return TestClient(client.app)


@pytest.fixture(scope="session")
def admin_client():
    from fastapi.testclient import TestClient

    from admin_app.main import create_app

    with TestClient(create_app()) as c:
        _ensure_test_users()
        yield c


# --- Erişim kontrolü ------------------------------------------------------

def test_protected_endpoints_require_token(anon):
    for path in ("/schema", "/contracts", "/schedules", "/notifications"):
        assert anon.get(path).status_code == 401, path
    assert anon.post("/ask", json={"question": "ciro"}).status_code == 401


def test_health_public_features_authed(anon, client):
    assert anon.get("/health").status_code == 200
    # /features artık PRINCIPAL'a özel çözülür (ADR-0009 DB fazı) → kimlik ister.
    assert anon.get("/features").status_code == 401
    assert client.get("/features").status_code == 200


def test_me_returns_principal(client):
    r = client.get("/auth/me")
    assert r.status_code == 200
    body = r.json()
    assert body["tenant_id"] and not body["is_superadmin"]
    assert "owner" in body["roles"]


# --- Login kapıları -------------------------------------------------------

def test_login_wrong_password_generic_401(anon):
    r = anon.post("/auth/login", json={"email": TEST_USER["email"], "password": "yanlis-parola"})
    assert r.status_code == 401
    r2 = anon.post("/auth/login", json={"email": "yok@dima.local", "password": "x"})
    assert r2.status_code == 401
    # Bilinen/bilinmeyen e-posta AYNI mesajı döner (hesap-enumerasyonu yok).
    assert r.json()["detail"] == r2.json()["detail"]


def test_superadmin_public_login_requires_ip_allowlist(anon, monkeypatch):
    """IP kapısı fail-closed: allowlist boşsa superadmin public login GENERIC 401
    (tenant kullanıcıları etkilenmez)."""
    from control_plane.config import get_auth_settings

    monkeypatch.setattr(get_auth_settings(), "superadmin_ip_allowlist", "")
    assert anon.post("/auth/login", json=TEST_SUPERADMIN).status_code == 401
    assert anon.post("/auth/login", json=TEST_USER).status_code == 200
    anon.post("/auth/logout")


def test_superadmin_public_access_is_allowed_and_logged(anon):
    """Log-only doktrini (ADR-0015 K7 güncellemesi): allowlist'li IP'den giren
    superadmin engellenmez, her veri erişimi audit'e superadmin olarak düşer."""
    from control_plane.db import engine
    from control_plane.models import AuditLog

    r = anon.post("/auth/login", json=TEST_SUPERADMIN)
    assert r.status_code == 200
    assert "vqr:write" in r.json()["user"]["permissions"]  # tüm izinler
    anon.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    assert anon.post("/ask", json={"question": "toplam ciro bu ay",
                                   "execute": True}).status_code == 200
    with Session(engine) as s:
        rows = s.exec(select(AuditLog).where(AuditLog.action == "query")).all()
        assert rows and rows[-1].actor_kind == "superadmin"
    anon.headers.pop("Authorization", None)


def test_login_rate_limited_after_failures(anon):
    from control_plane.config import get_auth_settings

    limit = get_auth_settings().login_max_attempts
    email = TEST_USER["email"]
    for _ in range(limit):
        anon.post("/auth/login", json={"email": email, "password": "yanlis"})
    r = anon.post("/auth/login", json=TEST_USER)  # doğru parola bile artık beklemeli
    assert r.status_code == 429


def test_mfa_required_and_verified(anon):
    from control_plane.db import engine
    from control_plane.models import User
    from control_plane.security import _totp_code, totp_secret

    secret = totp_secret()
    with Session(engine) as s:
        user = s.exec(select(User).where(User.email == TEST_USER["email"])).one()
        user.mfa_secret = secret
        s.add(user)
        s.commit()
    try:
        r = anon.post("/auth/login", json=TEST_USER)
        assert r.status_code == 401 and "OTP" in r.json()["detail"]
        code = _totp_code(secret, int(time.time() // 30))
        r = anon.post("/auth/login", json={**TEST_USER, "otp": code})
        assert r.status_code == 200
        r = anon.post("/auth/login", json={**TEST_USER, "otp": "000000"})
        assert r.status_code == 401
    finally:
        with Session(engine) as s:
            user = s.exec(select(User).where(User.email == TEST_USER["email"])).one()
            user.mfa_secret = None
            s.add(user)
            s.commit()


# --- Refresh rotation -----------------------------------------------------

def _login(anon) -> str:
    r = anon.post("/auth/login", json=TEST_USER)
    assert r.status_code == 200
    return anon.cookies.get("dima_refresh")


def test_refresh_rotates_and_reuse_revokes_family(anon, monkeypatch):
    from control_plane.config import get_auth_settings

    monkeypatch.setattr(get_auth_settings(), "refresh_grace_seconds", 0)
    old = _login(anon)
    r = anon.post("/auth/refresh")
    assert r.status_code == 200 and r.json()["access_token"]
    new = anon.cookies.get("dima_refresh")
    assert new != old
    # Eski token'ın grace dışı yeniden kullanımı → hırsızlık: tüm family iptal.
    r = anon.post("/auth/refresh", cookies={"dima_refresh": old})
    assert r.status_code == 401
    r = anon.post("/auth/refresh", cookies={"dima_refresh": new})
    assert r.status_code == 401  # family revoke edildi


def test_parallel_refresh_within_grace_survives(anon, monkeypatch):
    from control_plane.config import get_auth_settings

    monkeypatch.setattr(get_auth_settings(), "refresh_grace_seconds", 30)
    old = _login(anon)
    assert anon.post("/auth/refresh").status_code == 200
    # İkinci sekme aynı eski token'la geldi (grace içinde) → meşru yarış, düşürülmez.
    r = anon.post("/auth/refresh", cookies={"dima_refresh": old})
    assert r.status_code == 200


def test_family_absolute_lifetime_cap(anon):
    from control_plane.auth_service import _now
    from control_plane.config import get_auth_settings
    from control_plane.db import engine
    from control_plane.models import RefreshToken
    from control_plane.security import hash_token

    raw = _login(anon)
    cap = get_auth_settings().refresh_family_max_seconds
    with Session(engine) as s:
        row = s.exec(select(RefreshToken).where(
            RefreshToken.token_hash == hash_token(raw))).one()
        row.issued_at = _now() - timedelta(seconds=cap + 60)
        s.add(row)
        s.commit()
    assert anon.post("/auth/refresh").status_code == 401


def test_logout_revokes_family(anon):
    _login(anon)
    assert anon.post("/auth/logout").status_code == 200
    assert anon.post("/auth/refresh").status_code == 401


def test_refresh_token_not_valid_as_access(anon, client):
    _login(anon)
    raw = anon.cookies.get("dima_refresh")
    r = anon.get("/auth/me", headers={"Authorization": f"Bearer {raw}"})
    assert r.status_code == 401


# --- Plane izolasyonu (ADR-0015) -----------------------------------------

def test_public_minted_superadmin_token_rejected_by_admin_plane(admin_client):
    from control_plane.security import create_access_token

    forged = create_access_token(sub="x", tenant_id=None, is_superadmin=True,
                                 roles=["superadmin"], plane="public")
    r = admin_client.get("/sadmin/tenants", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401  # public secret'la basılmış token admin'de GEÇERSİZ


def test_admin_plane_login_and_access(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    assert r.status_code == 200
    token = r.json()["access_token"]
    r = admin_client.get("/sadmin/tenants", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    # Tenant kullanıcısı admin plane'e giremez.
    assert admin_client.post("/auth/login", json=TEST_USER).status_code == 401


def test_admin_refresh_uses_admin_cookie(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    assert r.status_code == 200
    assert admin_client.cookies.get("dima_admin_refresh")
    assert admin_client.post("/auth/refresh").status_code == 200


# --- Audit + VQR kimlik izleri -------------------------------------------

def test_query_paths_write_audit(client):
    from control_plane.db import engine
    from control_plane.models import AuditLog

    r = client.post("/ask", json={"question": "toplam ciro bu ay", "execute": True})
    assert r.status_code == 200
    with Session(engine) as s:
        rows = s.exec(select(AuditLog).where(AuditLog.action == "query")).all()
        assert rows, "sorgu audit izi yazılmalı (ADR-0014 Karar 6)"
        last = rows[-1]
        assert last.actor_user_id is not None and last.tenant_id is not None
        logins = s.exec(select(AuditLog).where(AuditLog.action == "login")).all()
        assert logins


def _login_as(client, email: str, password: str):
    """Aynı app üzerinde verilen kullanıcıyla kimlikli yeni istemci."""
    from fastapi.testclient import TestClient

    c = TestClient(client.app)
    r = c.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    return c


# --- Rol matrisi (uykuda: üründe yalnız owner; mantık testli kalır) --------

def test_viewer_can_query_but_cannot_mutate(client):
    make_tenant_user("viewer@dima.local", "viewer-parola-1", "viewer")
    c = _login_as(client, "viewer@dima.local", "viewer-parola-1")
    assert c.post("/ask", json={"question": "toplam ciro bu ay", "execute": True}).status_code == 200
    assert c.post("/verify", json={"label": "x", "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}}).status_code == 403
    assert c.post("/query", json={"sql": "select 1"}).status_code == 403
    assert c.post("/schedules", json={"label": "x", "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}}).status_code == 403


def test_analyst_can_delete_only_own_schedule(client):
    make_tenant_user("analyst@dima.local", "analyst-parola-1", "analyst")
    c = _login_as(client, "analyst@dima.local", "analyst-parola-1")
    cq = {"cube": "parti", "measures": ["toplam_ciro"]}
    own = c.post("/schedules", json={"label": "analistin", "cube_query": cq}).json()["schedule"]
    other = client.post("/schedules", json={"label": "ownerin", "cube_query": cq}).json()["schedule"]
    assert c.delete(f"/schedules/{other['id']}").status_code == 403
    assert c.delete(f"/schedules/{own['id']}").status_code == 200
    assert client.delete(f"/schedules/{other['id']}").status_code == 200  # owner herkesinkini


def test_admin_api_allows_only_owner_role(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    tid = admin_client.get("/sadmin/tenants", headers=h).json()[0]["id"]
    r = admin_client.post("/sadmin/users", headers=h, json={
        "email": "yeni@dima.local", "password": "parola-123", "tenant_id": tid,
        "role_key": "analyst"})
    assert r.status_code == 400  # bu fazda yalnız owner


def test_permissions_reflect_role_matrix(client):
    me = client.get("/auth/me").json()  # owner
    assert {"query:run", "vqr:write", "schedule:delete"} <= set(me["permissions"])
    make_tenant_user("perms-viewer@dima.local", "viewer-parola-2", "viewer")
    c = _login_as(client, "perms-viewer@dima.local", "viewer-parola-2")
    body = c.post("/auth/login", json={"email": "perms-viewer@dima.local",
                                       "password": "viewer-parola-2"}).json()
    perms = set(body["user"]["permissions"])
    assert "query:run" in perms and "vqr:write" not in perms


def test_feature_override_hierarchy_and_kill_switch(client, admin_client):
    """ADR-0009 DB fazı: en SPESİFİK kazanır (user > tenant > global > fabrika);
    spesifik 'off' = kill switch; override silinince miras (fabrika: beta) döner."""
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    me = client.get("/auth/me").json()
    created: list[str] = []

    def put(scope_type: str, scope_id: str | None, stage: str) -> None:
        rr = admin_client.put("/sadmin/features/verify_button", headers=h,
                              json={"scope_type": scope_type, "scope_id": scope_id,
                                    "stage": stage})
        assert rr.status_code == 200, rr.text
        created.append(rr.json()["id"])

    def stage() -> str | None:
        return client.get("/features").json()["features"].get("verify_button")

    try:
        put("global", None, "prod")
        assert stage() == "prod"                    # global, fabrika beta'yı ezdi
        put("tenant", me["tenant_id"], "off")
        assert stage() is None                      # kill switch: yalnız bu tenant kapalı
        put("user", me["user_id"], "beta")
        assert stage() == "beta"                    # en spesifik (user) kazandı
    finally:
        for oid in created:
            admin_client.delete(f"/sadmin/features/verify_button/overrides/{oid}",
                                headers=h)
    assert stage() == "beta"                        # miras: fabrika ayarına dönüş


def test_packs_discovery_and_tenant_config_flow(client, admin_client, tmp_path):
    """Onaylı tasarım: panel pack listesinden SEÇER → TenantConfig DB'ye yazılır →
    materializer company.yml'i türetir (DB kazanır; elle düzenleme ezilir)."""
    import json

    from app.config import get_settings
    from app.materialize import materialize_tenant_configs
    from control_plane.db import engine
    from control_plane.models import TenantConfig

    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    packs = admin_client.get("/sadmin/packs", headers=h).json()
    keys = [p["key"] for p in packs["sektorler"]]
    assert "boyahane" in keys
    boyahane = next(p for p in packs["sektorler"] if p["key"] == "boyahane")
    assert any(c["name"] == "parti" for c in boyahane["cubes"])  # cube önizlemesi
    assert boyahane["moduller"] == ["oee", "bakim", "ik", "enerji"]

    # Bilinmeyen pack reddedilir (sessiz çürüme yok).
    r = admin_client.post("/sadmin/tenants", headers=h, json={
        "slug": "cfg-test", "name": "Cfg Test", "sektorler": ["yok-boyle-pack"]})
    assert r.status_code == 400

    r = admin_client.post("/sadmin/tenants", headers=h, json={
        "slug": "cfg-test", "name": "Cfg Test", "sektorler": ["boyahane"]})
    assert r.status_code == 201 and r.json()["sektorler"] == ["boyahane"]

    with Session(engine) as s:
        assert s.exec(select(TenantConfig)).first() is not None

    # Materializer: DB → company.yml (izole dizine); içerik + türetilmiş başlık.
    changed = materialize_tenant_configs(get_settings(), companies_dir=tmp_path)
    assert changed == ["cfg-test"]
    text = (tmp_path / "cfg-test" / "company.yml").read_text()
    assert "TÜRETİLMİŞTİR" in text and "sektorler:" in text and "boyahane" in text
    # İkinci koşum no-op (değişiklik yok).
    assert materialize_tenant_configs(get_settings(), companies_dir=tmp_path) == []

    # Config güncelle → yeniden materialize eder.
    tid = r.json()["id"]
    r = admin_client.put(f"/sadmin/tenants/{tid}/config", headers=h,
                         json={"sektorler": ["boyahane"], "moduller": []})
    assert r.status_code == 200 and r.json()["moduller"] == []
    assert materialize_tenant_configs(get_settings(), companies_dir=tmp_path) == ["cfg-test"]
    assert "moduller: []" in (tmp_path / "cfg-test" / "company.yml").read_text()

    # ADR-0017 kaynak faseti: keşif + kapsam validasyonu + materialize çıktısı.
    assert any(k["key"] == "mikro-v16" and not k["onekli"] for k in packs["kaynaklar"])
    assert any(k["key"] == "logo-3" and k["onekli"] for k in packs["kaynaklar"])
    r = admin_client.put(f"/sadmin/tenants/{tid}/config", headers=h,
                         json={"sektorler": ["boyahane"], "kaynaklar": ["yok-kaynak"]})
    assert r.status_code == 400  # bilinmeyen kaynak reddedilir
    r = admin_client.put(f"/sadmin/tenants/{tid}/config", headers=h,
                         json={"sektorler": ["boyahane"], "kaynaklar": ["logo-3"]})
    assert r.status_code == 400 and "firma" in r.json()["detail"]  # önekli → kapsam şart
    r = admin_client.put(f"/sadmin/tenants/{tid}/config", headers=h,
                         json={"sektorler": ["kumas-ticareti"], "kaynaklar": ["logo-3"],
                               "firma_no": 121, "donem_no": 1})
    assert r.status_code == 200 and r.json()["kaynaklar"] == ["logo-3"]
    assert r.json()["firma_no"] == 121
    assert materialize_tenant_configs(get_settings(), companies_dir=tmp_path) == ["cfg-test"]
    text = (tmp_path / "cfg-test" / "company.yml").read_text()
    assert "kaynaklar:" in text and "logo-3" in text and "firma_no: 121" in text


def test_audit_screen_endpoint(client, admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    client.post("/ask", json={"question": "toplam ciro", "execute": True})
    data = admin_client.get("/sadmin/audit?limit=50", headers=h).json()
    assert "query" in data["actions"] and "login" in data["actions"]
    q = next(e for e in data["entries"] if e["action"] == "query")
    assert q["actor"] and q["tenant"]  # e-posta + slug (id değil)
    only_login = admin_client.get("/sadmin/audit?action=login", headers=h).json()
    assert all(e["action"] == "login" for e in only_login["entries"])


def test_schema_exposes_lower_is_better(client):
    cubes = client.get("/schema").json()["cubes"]
    parti = next(c for c in cubes if c["name"] == "parti")
    assert "fire_orani_yuzde" in parti["lower_is_better"]
    assert "toplam_ciro" not in parti["lower_is_better"]
    surd = next(c for c in cubes if c["name"] == "surdurulebilirlik")
    assert "su_yogunlugu_lt_kg" in surd["lower_is_better"]


# --- Tenant-RLS + askıya alma ---------------------------------------------

def test_other_tenant_cannot_touch_data_plane(client):
    make_tenant_user("baska@firma.local", "baska-parola-1", "owner",
                     tenant_slug="baska-firma")
    c = _login_as(client, "baska@firma.local", "baska-parola-1")
    # Veri düzlemi aktif şirkete bağlı: başka tenant sorgu koşamaz…
    assert c.post("/ask", json={"question": "toplam ciro"}).status_code == 403
    # …ve aktif şirketin kayıtlarını (contracts/schedules/bildirim) GÖREMEZ.
    client.post("/ask", json={"question": "toplam ciro bu ay", "execute": True})
    assert client.get("/contracts").json()["contracts"]  # sahibi görür
    assert c.get("/contracts").json()["contracts"] == []
    assert c.get("/schedules").json()["schedules"] == []
    assert c.get("/notifications").json()["notifications"] == []


def test_suspended_tenant_login_blocked_and_sessions_die(client):
    from app.auth.dependencies import _tenant_status_cache
    from control_plane.db import engine
    from control_plane.models import Tenant

    make_tenant_user("askida@firma.local", "askida-parola-1", "owner",
                     tenant_slug="askida-firma")
    c = _login_as(client, "askida@firma.local", "askida-parola-1")
    with Session(engine) as s:
        t = s.exec(select(Tenant).where(Tenant.slug == "askida-firma")).one()
        t.status = "suspended"
        s.add(t)
        s.commit()
    _tenant_status_cache.clear()
    try:
        # Açık oturum: access token hâlâ imzalı ama per-request kontrol düşürür…
        assert c.get("/auth/me").status_code == 401
        # …refresh de reddedilir (auto-logout) ve yeni login açık mesajla 403.
        assert c.post("/auth/refresh").status_code == 401
        r = c.post("/auth/login", json={"email": "askida@firma.local",
                                        "password": "askida-parola-1"})
        assert r.status_code == 403 and "iletişime geçin" in r.json()["detail"]
    finally:
        with Session(engine) as s:
            t = s.exec(select(Tenant).where(Tenant.slug == "askida-firma")).one()
            t.status = "active"
            s.add(t)
            s.commit()
        _tenant_status_cache.clear()


def test_legacy_token_without_slug_gets_401_to_refresh(client):
    from control_plane.security import create_access_token

    old = create_access_token(sub="x", tenant_id="00000000-0000-0000-0000-000000000000",
                              is_superadmin=False, roles=["owner"], plane="public",
                              tenant_slug=None)
    r = client.post("/ask", json={"question": "ciro"},
                    headers={"Authorization": f"Bearer {old}"})
    assert r.status_code == 401  # 403 değil: refresh zinciri tetiklensin


def test_admin_can_toggle_tenant_status(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    tenants = admin_client.get("/sadmin/tenants", headers=h).json()
    tid = next(t["id"] for t in tenants if t["slug"] == "askida-firma")
    r = admin_client.patch(f"/sadmin/tenants/{tid}", headers=h,
                           json={"status": "suspended"})
    assert r.status_code == 200 and r.json()["status"] == "suspended"
    r = admin_client.patch(f"/sadmin/tenants/{tid}", headers=h,
                           json={"status": "active"})
    assert r.status_code == 200 and r.json()["status"] == "active"


def test_verify_stamps_identity_into_vqr(client):
    # VQR artık Postgres'te (verified_query, ADR-0005/0008) — dosya değil, DB satırı okunur.
    from sqlmodel import Session, select

    from app.llm import _norm
    from control_plane.db import engine
    from control_plane.models import VerifiedQuery

    r = client.post("/verify", json={
        "label": "test kimlik damgası sorusu",
        "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]},
    })
    assert r.status_code == 200 and r.json()["stored"]
    with Session(engine) as s:
        row = s.exec(select(VerifiedQuery).where(
            VerifiedQuery.question_norm == _norm("test kimlik damgası sorusu"))).first()
    assert row is not None and row.verified_by and row.tenant_id
