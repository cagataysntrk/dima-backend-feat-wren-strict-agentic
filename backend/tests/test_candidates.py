"""#57 öğrenme döngüsü — /sadmin/synonyms/candidates triyaj + promote-vqr. Route-edilemeyen
+ LLM'e düşen sorular kümelenir, cube_query varsa 'vqr' yoksa 'synonym' etiketlenir; aday
VQR'a yükseltilince VerifiedQuery yazılır (public app LLM'siz cevaplar)."""

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


def _h(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed(kind, question, cube_query=None, note=None):
    from control_plane.db import engine, init_db
    from control_plane.models import InteractionLog
    from sqlmodel import Session

    init_db()
    with Session(engine) as s:
        s.add(InteractionLog(
            question=question, kind=kind, source=kind,
            sql=None if kind != "llm" else "SELECT 1", note=note,
            cube_query_json=json.dumps(cube_query) if cube_query else None))
        s.commit()


def test_candidates_triage_synonym_vs_vqr(admin_client):
    _seed("none", "makinalara gore fire", note="route yok")
    _seed("none", "makinalara gore fire")
    _seed("llm", "renk kirilimli verim", cube_query={"cube": "oee", "measures": ["ort_oee"]})
    h = _h(admin_client)
    out = admin_client.get("/sadmin/synonyms/candidates", headers=h).json()["candidates"]
    syn = next(c for c in out if c["question"] == "makinalara gore fire")
    vqr = next(c for c in out if c["question"] == "renk kirilimli verim")
    assert syn["triage"] == "synonym" and syn["count"] == 2  # cube_query yok → synonym
    assert vqr["triage"] == "vqr" and vqr["cube_query"]["cube"] == "oee"


def test_promote_candidate_to_vqr_writes_verified_query(admin_client):
    h = _h(admin_client)
    r = admin_client.post("/sadmin/synonyms/candidates/promote-vqr", headers=h, json={
        "company": "test-co", "question": "renk kırılımlı verim",
        "cube_query": {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["renk"],
                       "filters": [{"dimension": "tarih"}]}})
    assert r.status_code == 201
    from control_plane.db import engine
    from control_plane.models import VerifiedQuery
    from sqlmodel import Session, select
    with Session(engine) as s:
        row = s.exec(select(VerifiedQuery).where(VerifiedQuery.company == "test-co")).first()
    assert row is not None and row.source == "mined"
    cq = json.loads(row.cube_query_json)
    assert "filters" not in cq  # dönem filtresi düşürüldü (VQR sınıfı öğrenir)
