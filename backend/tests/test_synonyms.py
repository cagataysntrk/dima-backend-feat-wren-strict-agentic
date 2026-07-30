"""Canlı sinonim overlay testleri (ADR-0018 katman 3).

Overlay: pack+arketip üstüne DB'den additive biner; yalnız approved=True uygulanır;
tenant kapsamı company_slug ile filtrelenir. Determinizm koruması: aday (approved=False)
canlıya İNMEZ.
"""

from __future__ import annotations

import json

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


def _admin_h(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_overlay_schema_birlesir_ve_onay_kapisi():
    """Onaysız overlay uygulanmaz; onaylanınca measure_synonyms'e additive katılır."""
    import uuid as _uuid

    from sqlmodel import Session

    from app.config import get_settings
    from app.wren_service import WrenService
    from control_plane.db import engine, init_db
    from control_plane.models import SynonymOverride

    init_db()
    s = get_settings()

    def _syns():
        svc = WrenService(s.resolved_project_dir(), s.datasource, {}, company_slug=s.company)
        cube = next(c for c in svc.schema()["cubes"] if c["name"] == "parti")
        return cube["measure_synonyms"]["toplam_ciro"]

    base = _syns()
    assert "acayipbirkelime" not in base

    with Session(engine) as db:
        o = SynonymOverride(scope_type="global", cube="parti", field_kind="measure",
                            field_name="toplam_ciro",
                            synonyms_json=json.dumps(["acayipbirkelime"]), approved=False)
        db.add(o); db.commit(); db.refresh(o)
        oid = o.id
    try:
        assert "acayipbirkelime" not in _syns()  # ADAY canlıya inmez
        with Session(engine) as db:
            row = db.get(SynonymOverride, oid)
            row.approved = True
            db.add(row); db.commit()
        merged = _syns()
        assert "acayipbirkelime" in merged  # onaylı → additive
        assert set(base) <= set(merged)  # base SİLİNMEDİ
    finally:
        with Session(engine) as db:
            row = db.get(SynonymOverride, oid)
            if row:
                db.delete(row); db.commit()


def test_overlay_tenant_kapsami():
    """tenant kapsamlı overlay yalnız o slug'ın servisinde görünür."""
    import uuid as _uuid

    from sqlmodel import Session

    from app.config import get_settings
    from app.wren_service import WrenService
    from control_plane.db import engine, init_db
    from control_plane.models import SynonymOverride

    init_db()
    s = get_settings()
    with Session(engine) as db:
        o = SynonymOverride(scope_type="tenant", scope_id="baska-tenant", cube="parti",
                            field_kind="measure", field_name="toplam_ciro",
                            synonyms_json=json.dumps(["tenantaozel"]), approved=True)
        db.add(o); db.commit(); db.refresh(o)
        oid = o.id
    try:
        # Aktif şirket (settings.company) ≠ baska-tenant → görünmez
        svc = WrenService(s.resolved_project_dir(), s.datasource, {}, company_slug=s.company)
        cube = next(c for c in svc.schema()["cubes"] if c["name"] == "parti")
        assert "tenantaozel" not in cube["measure_synonyms"]["toplam_ciro"]
        # baska-tenant servisi → görünür
        svc2 = WrenService(s.resolved_project_dir(), s.datasource, {}, company_slug="baska-tenant")
        cube2 = next(c for c in svc2.schema()["cubes"] if c["name"] == "parti")
        assert "tenantaozel" in cube2["measure_synonyms"]["toplam_ciro"]
    finally:
        with Session(engine) as db:
            row = db.get(SynonymOverride, oid)
            if row:
                db.delete(row); db.commit()


def test_admin_synonym_crud(admin_client):
    h = _admin_h(admin_client)
    # Bilinmeyen cube reddedilir
    r = admin_client.post("/sadmin/synonyms", headers=h, json={
        "cube": "yok-cube", "field_kind": "measure", "field_name": "x", "synonyms": ["y"]})
    assert r.status_code == 400
    # Geçerli oluştur (aday)
    r = admin_client.post("/sadmin/synonyms", headers=h, json={
        "scope_type": "global", "cube": "parti", "field_kind": "measure",
        "field_name": "toplam_ciro", "synonyms": ["hasilatimiz"], "source": "mined"})
    assert r.status_code == 201 and r.json()["approved"] is False
    oid = r.json()["id"]
    # Aday kuyruğunda görünür
    pend = admin_client.get("/sadmin/synonyms?only_pending=true", headers=h).json()
    assert any(o["id"] == oid for o in pend)
    # Onayla
    r = admin_client.post(f"/sadmin/synonyms/{oid}/approve", headers=h)
    assert r.status_code == 200 and r.json()["approved"] is True
    # Sil
    assert admin_client.delete(f"/sadmin/synonyms/{oid}", headers=h).status_code == 204


def test_admin_synonym_lang_roundtrips(admin_client):
    """§7b — dil-etiketli overlay: lang oluşturmada kabul edilir, yanıtta+listede döner."""
    h = _admin_h(admin_client)
    r = admin_client.post("/sadmin/synonyms", headers=h, json={
        "scope_type": "global", "cube": "parti", "field_kind": "measure",
        "field_name": "toplam_ciro", "synonyms": ["gross revenue"], "lang": "en"})
    assert r.status_code == 201 and r.json()["lang"] == "en"
    oid = r.json()["id"]
    listed = admin_client.get("/sadmin/synonyms", headers=h).json()
    assert any(o["id"] == oid and o["lang"] == "en" for o in listed)
    admin_client.delete(f"/sadmin/synonyms/{oid}", headers=h)


def test_synonym_public_planeden_erisilemez(client):
    assert client.get("/sadmin/synonyms").status_code in (401, 403, 404)
