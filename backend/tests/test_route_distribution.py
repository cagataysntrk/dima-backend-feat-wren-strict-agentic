"""FAZ 0.1 — `/sadmin/interactions/route-distribution` KPI regresyon kilidi.

Bu endpoint, ürünün ANA KPI'sının ("Intent ≥%70 · Discovery <%30", strateji belgesi §KPI)
tek ölçüm noktasıdır. 2 Ağustos 2026'da iki kusuru vardı:

  1. `drill` / `upload` / `verify` kaynakları `other`'a düşüyordu. Bunlar bir NL sorusunun
     yönlendirilmesi DEĞİL, verilmiş bir cevabın üstündeki kullanıcı aksiyonlarıdır; KPI
     paydasında sayılınca Intent-payını olduğundan DÜŞÜK gösterirler.
  2. KPI'nın kendisi hesaplanmıyordu — çağıranın `by_path`'ten aritmetik yapması gerekiyordu,
     ve endpoint'in repo genelinde HİÇ tüketicisi yoktu.

Ayrıca: küçük örneklemde "hedef tutuyor" demek yanıltıcıdır (n=7 ile %100 Intent görmek
mümkün — nitekim bulunduğunda tabloda tam olarak 7 satır vardı). `meets_target` bu yüzden
n<30'da bilinçli olarak None döner.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

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


def _h(admin_client) -> dict:
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed(rows: list[tuple[str | None, int]], tenant_id: uuid.UUID) -> None:
    """(source, adet) çiftlerini interaction_log'a yaz — hepsi aynı tenant'a damgalı."""
    from sqlmodel import Session

    from control_plane.db import engine, init_db
    from control_plane.models import InteractionLog

    init_db()
    ts = datetime.utcnow() - timedelta(hours=1)
    with Session(engine) as s:
        for source, n in rows:
            for _ in range(n):
                s.add(InteractionLog(ts=ts, source=source, tenant_id=tenant_id,
                                     question="q", kind=None))
        s.commit()


def _dist(admin_client, tenant_id: uuid.UUID) -> dict:
    r = admin_client.get(
        f"/sadmin/interactions/route-distribution?days=7&tenant={tenant_id}",
        headers=_h(admin_client),
    )
    assert r.status_code == 200, r.text
    return r.json()


def _paths(out: dict) -> dict[str, int]:
    return {row["path"]: row["count"] for row in out["by_path"]}


def test_soru_disi_aksiyonlar_ayri_path_alir_ve_kpi_paydasina_girmez(admin_client):
    """drill/upload/verify artık `other` değil; ve KPI paydasını şişirmiyorlar."""
    tid = uuid.uuid4()
    _seed([("cube", 6), ("llm:gemini", 2),
           ("drill", 5), ("upload", 3), ("verify", 4)], tid)
    out = _dist(admin_client, tid)

    paths = _paths(out)
    assert paths.get("drill") == 5
    assert paths.get("upload") == 3
    assert paths.get("verify") == 4
    assert "other" not in paths, f"soru-dışı aksiyonlar hâlâ other'a düşüyor: {paths}"

    # Payda YALNIZ veri cevabı beklenen sorular: cube(6) + llm(2) = 8, aksiyonlar HARİÇ.
    assert out["kpi"]["denominator"] == 8
    assert out["kpi"]["intent_pct"] == 75.0
    assert out["kpi"]["discovery_pct"] == 25.0


def test_meta_ve_katalog_kpi_paydasindan_dislanir(admin_client):
    """Selamlama/katalog soruları veri sorusu değildir; Intent-payını sulandırmamalı."""
    tid = uuid.uuid4()
    _seed([("cube", 4), ("meta", 10), ("catalog", 10)], tid)
    out = _dist(admin_client, tid)

    assert _paths(out).get("meta_katalog") == 20
    assert out["kpi"]["denominator"] == 4      # yalnız cube
    assert out["kpi"]["intent_pct"] == 100.0


def test_cube_llm_intent_sayilir_vqr_cache_sayilir(admin_client):
    """`cube+llm` (Intent-JSON) Intent'tir — SQL yazmaz. `vqr` ayrı bir kova (cache)."""
    tid = uuid.uuid4()
    _seed([("cube", 2), ("cube+llm", 3), ("vqr", 5), ("llm:anthropic", 2), ("rule", 1)], tid)
    out = _dist(admin_client, tid)

    paths = _paths(out)
    assert paths.get("intent") == 5          # cube + cube+llm
    assert paths.get("cache") == 5
    assert paths.get("discovery") == 2
    assert paths.get("rule") == 1
    # Ham kırılım cube ile cube+llm'i AYRI tutmalı (güvenleri farklı: 1.0 vs 0.85).
    by_source = {row["source"]: row["count"] for row in out["by_source"]}
    assert by_source["cube"] == 2 and by_source["cube+llm"] == 3


def test_kucuk_orneklemde_hedef_karari_verilmez(admin_client):
    """n<30 → meets_target None. Bulgu anındaki gerçek durum n=7'ydi; %100 Intent
    görünüyordu ama bu bir kanıt değildi."""
    tid = uuid.uuid4()
    _seed([("cube", 7)], tid)
    out = _dist(admin_client, tid)

    assert out["kpi"]["denominator"] == 7
    assert out["kpi"]["intent_pct"] == 100.0
    assert out["kpi"]["meets_target"] is None, "yetersiz örneklemde hedef 'tuttu' denmemeli"


def test_yeterli_orneklemde_hedef_karari_verilir(admin_client):
    """n≥30 → gerçek karar. %75 Intent / %25 Discovery hedefi tutar."""
    tid = uuid.uuid4()
    _seed([("cube", 30), ("llm:gemini", 10)], tid)
    out = _dist(admin_client, tid)

    assert out["kpi"]["denominator"] == 40
    assert out["kpi"]["intent_pct"] == 75.0
    assert out["kpi"]["discovery_pct"] == 25.0
    assert out["kpi"]["meets_target"] is True


def test_hedef_tutmadiginda_false_doner(admin_client):
    tid = uuid.uuid4()
    _seed([("cube", 10), ("llm:gemini", 30)], tid)
    out = _dist(admin_client, tid)

    assert out["kpi"]["intent_pct"] == 25.0
    assert out["kpi"]["discovery_pct"] == 75.0
    assert out["kpi"]["meets_target"] is False


def test_hic_veri_yokken_patlamaz(admin_client):
    """Bugünkü gerçek durum: tablo neredeyse boş. Endpoint sıfıra bölmemeli."""
    out = _dist(admin_client, uuid.uuid4())  # hiç satırı olmayan tenant
    assert out["total"] == 0
    assert out["kpi"]["denominator"] == 0
    assert out["kpi"]["intent_pct"] == 0.0
    assert out["kpi"]["meets_target"] is None
