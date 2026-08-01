"""Faz 4.5 (31 Temmuz 2026) — tenant-kendi-hizmeti DB bağlama sihirbazı (`app/routers/
connections.py`, PUBLIC plane). `tests/test_connections.py`'nin (admin_app `/sadmin/
connections`, SÜPERADMIN-only) TENANT-PLANE karşılığı — AYRI dosya, o testlere dokunmaz.

Bu ortamda canlı bir Postgres sunucusu YOK — testler `app.db_introspect.check_connection`/
`introspect_schema`'yı (router'ın kendi modülünden İTHAL edildiği noktada) monkeypatch'ler:
gerçek şema okuma mantığı zaten `tests/test_db_introspect.py`'de GERÇEK SQLite üzerinden
kanıtlandı — burada yalnız ROUTER'IN ORKESTRASYONU (dry-run→persist, draft, confirm→YAML
yazımı, tenant izolasyonu) test edilir. Dosya yazımı her zaman bir TEMP dizine yönlendirilir
(gerçek demo/companies/ ASLA dokunulmaz — `app.config.get_settings` monkeypatch'lenir)."""

from __future__ import annotations

import uuid

import pytest


def _body(**overrides) -> dict:
    base = {"datasource": "postgres", "host": "db.example.com", "port": 5432,
            "database": "satis", "user": "dima", "password": "gizli-parola"}
    base.update(overrides)
    return base


def test_create_connection_dry_run_failure_never_persists_secret(client):
    """Fail-closed: bağlantı kurulamazsa (gerçek DNS çözümlenemeyen host) DB'ye HİÇBİR
    satır yazılmaz — sır asla diske düşmez."""
    r = client.post("/connections", json=_body(host="bu-host-kesinlikle-yok.invalid"))
    assert r.status_code == 400, r.text

    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import DbConnection

    with Session(engine) as s:
        rows = s.exec(select(DbConnection).where(
            DbConnection.conn_meta_json.contains("bu-host-kesinlikle-yok"))).all()
    assert rows == []


def test_create_connection_success_and_list(client, monkeypatch):
    import app.db_introspect as di

    monkeypatch.setattr(di, "check_connection", lambda url, timeout=5: None)
    r = client.post("/connections", json=_body(database="test_4_5_musteri_db"))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["has_secret"] is True
    assert body["database"] == "test_4_5_musteri_db"
    assert "password" not in body and "gizli-parola" not in str(body)

    lst = client.get("/connections").json()
    assert any(c["id"] == body["id"] for c in lst)

    d = client.delete(f"/connections/{body['id']}")
    assert d.status_code == 204
    assert not any(c["id"] == body["id"] for c in client.get("/connections").json())


def test_test_endpoint_does_not_persist(client, monkeypatch):
    """POST /connections/test yalnız dry-run'dır — hiçbir DbConnection satırı YARATMAZ."""
    import app.db_introspect as di

    monkeypatch.setattr(di, "check_connection", lambda url, timeout=5: None)
    before = len(client.get("/connections").json())
    r = client.post("/connections/test", json=_body(database="test_4_5_yalniz_test_ucu"))
    assert r.status_code == 200 and r.json()["ok"] is True
    after = len(client.get("/connections").json())
    assert before == after


def test_get_own_rejects_other_tenants_connection():
    """Tenant izolasyonu — DOĞRUDAN birim testi (ikinci gerçek company.yml'li tenant
    kurmadan): `_get_own` başka tenant_id'ye ait bir DbConnection'ı 404 sayar."""
    from types import SimpleNamespace

    from fastapi import HTTPException
    from sqlmodel import Session

    from app.routers.connections import _get_own
    from control_plane.db import engine
    from control_plane.models import DbConnection

    owner_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    conn = DbConnection(tenant_id=owner_tenant, datasource="postgres",
                        conn_meta_json="{}", secret_ciphertext=b"x")
    with Session(engine) as s:
        s.add(conn)
        s.commit()
        s.refresh(conn)

    fake_request = SimpleNamespace(state=SimpleNamespace(
        principal=SimpleNamespace(tenant_id=str(other_tenant))))
    with Session(engine) as s:
        with pytest.raises(HTTPException) as exc:
            _get_own(s, fake_request, str(conn.id))
        assert exc.value.status_code == 404

    fake_request_owner = SimpleNamespace(state=SimpleNamespace(
        principal=SimpleNamespace(tenant_id=str(owner_tenant))))
    with Session(engine) as s:
        got = _get_own(s, fake_request_owner, str(conn.id))
        assert got.id == conn.id


@pytest.fixture
def sqlite_source_url(tmp_path):
    """Draft/confirm testleri için gerçek FK'li 2-tablolu bir SQLite DB — monkeypatch'lenen
    `introspect_schema` bu URL'i (gerçek Postgres URL'i YERİNE) okuyacak."""
    from sqlalchemy import create_engine, text

    db_path = tmp_path / "kaynak.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE test45_musteriler (id INTEGER PRIMARY KEY, ad VARCHAR(100))"))
        conn.execute(text(
            "CREATE TABLE test45_siparisler ("
            " id INTEGER PRIMARY KEY, musteri_id INTEGER, tutar NUMERIC, tarih DATE,"
            " FOREIGN KEY (musteri_id) REFERENCES test45_musteriler(id))"))
    engine.dispose()
    return f"sqlite:///{db_path}"


@pytest.fixture
def isolated_company_base(tmp_path, monkeypatch):
    """`confirm_draft`'ın yazdığı dosyaları GERÇEK repodan tamamen izole eder — settings.
    resolved_project_dir().parent'ı bir TEMP dizine yönlendirir (gerçek demo/companies/
    ASLA dokunulmaz)."""
    import app.config as config_mod

    fake_project_dir = tmp_path / "wren-project"

    class _FakeSettings:
        company = "test-4-5-company"

        def resolved_project_dir(self):
            return fake_project_dir

    monkeypatch.setattr(config_mod, "get_settings", lambda: _FakeSettings())
    return tmp_path


def _patch_introspection(monkeypatch, sqlite_source_url):
    import app.db_introspect as di

    monkeypatch.setattr(di, "check_connection", lambda url, timeout=5: None)
    real_introspect = di.introspect_schema
    monkeypatch.setattr(di, "introspect_schema",
                        lambda url, max_tables=50: real_introspect(sqlite_source_url))


def test_draft_reflects_real_introspected_schema(client, monkeypatch, sqlite_source_url):
    _patch_introspection(monkeypatch, sqlite_source_url)
    created = client.post("/connections", json=_body(database="test_4_5_draft_db")).json()

    draft = client.get(f"/connections/{created['id']}/draft")
    assert draft.status_code == 200, draft.text
    d = draft.json()
    names = {c["name"] for c in d["cubes"]}
    assert {"test45_musteriler", "test45_siparisler"} <= names
    siparisler = next(c for c in d["cubes"] if c["name"] == "test45_siparisler")
    assert "tutar" in siparisler["measures"]
    assert "tarih" in siparisler["time_dimensions"]
    assert any(set(r["models"]) == {"test45_siparisler", "test45_musteriler"}
              for r in d["relationships"])

    client.delete(f"/connections/{created['id']}")


def test_confirm_writes_real_yaml_files_and_relationships(
    client, monkeypatch, sqlite_source_url, isolated_company_base,
):
    _patch_introspection(monkeypatch, sqlite_source_url)
    created = client.post("/connections", json=_body(database="test_4_5_confirm_db")).json()
    draft = client.get(f"/connections/{created['id']}/draft").json()

    r = client.post(f"/connections/{created['id']}/confirm", json=draft)
    assert r.status_code == 200, r.text
    result = r.json()
    assert set(result["written_cubes"]) == {"test45_musteriler", "test45_siparisler"}
    assert result["written_relationships"] == 1

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import DbConnection, Tenant

    with Session(engine) as s:
        conn = s.get(DbConnection, uuid.UUID(created["id"]))
        tenant_id = conn.tenant_id
    with Session(engine) as s:
        tenant = s.get(Tenant, tenant_id)
        company = tenant.slug

    base = isolated_company_base
    cube_path = base / "companies" / company / "cubes" / "test45_siparisler" / "metadata.yml"
    model_path = base / "companies" / company / "models" / "test45_siparisler" / "metadata.yml"
    rel_path = base / "companies" / company / "relationships.yml"
    assert cube_path.exists()
    assert model_path.exists()
    assert rel_path.exists()

    from ruamel.yaml import YAML

    y = YAML()
    cube_data = y.load(cube_path.read_text())
    assert cube_data["base_object"] == "test45_siparisler"
    assert any(m["name"] == "tutar" for m in cube_data["measures"])

    rel_data = y.load(rel_path.read_text())
    assert len(rel_data["relationships"]) == 1
    assert rel_data["relationships"][0]["condition"] == (
        "test45_siparisler.musteri_id = test45_musteriler.id")


def test_confirm_never_overwrites_existing_cube(
    client, monkeypatch, sqlite_source_url, isolated_company_base,
):
    """Var olan bir cube/model dosyasıyla isim çakışması SESSİZCE atlanır — üstüne
    YAZILMAZ (written_cubes bu ismi İÇERMEZ)."""
    _patch_introspection(monkeypatch, sqlite_source_url)
    created = client.post("/connections", json=_body(database="test_4_5_conflict_db")).json()
    draft = client.get(f"/connections/{created['id']}/draft").json()

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import DbConnection, Tenant

    with Session(engine) as s:
        conn = s.get(DbConnection, uuid.UUID(created["id"]))
        company = s.get(Tenant, conn.tenant_id).slug

    conflict_dir = isolated_company_base / "companies" / company / "cubes" / "test45_musteriler"
    conflict_dir.mkdir(parents=True, exist_ok=True)
    (conflict_dir / "metadata.yml").write_text("name: test45_musteriler\nbase_object: onceden_var\n")

    r = client.post(f"/connections/{created['id']}/confirm", json=draft)
    assert r.status_code == 200, r.text
    result = r.json()
    assert "test45_musteriler" not in result["written_cubes"]
    assert "test45_siparisler" in result["written_cubes"]
    # çakışan dosya BOZULMADI
    assert "onceden_var" in (conflict_dir / "metadata.yml").read_text()
