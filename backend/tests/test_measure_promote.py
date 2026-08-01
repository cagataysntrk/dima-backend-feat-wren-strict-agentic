"""Discovery→Promote (Faz 2d) — uçtan uca yaşam-döngüsü: capture → review (analyst) →
approve (admin, dry_plan + golden-case zorunlu) → GERÇEKTEN route()-lenebilir → deprecate
(NL-routing'ten gizlenir, eski kayıt kırılmaz).

DİKKAT: `approve` GERÇEK dosyalara yazar (cube YAML + eval/cases.yaml) ve `compose_and_build`
tetikler — bu testler repoyu KİRLETMEMEK için kendi oluşturdukları her şeyi (yeni YAML dosyası,
eklenen eval satırı, derlenmiş proje) `finally` içinde temizler ve orijinal derlenmiş durumu
geri kurar."""

from __future__ import annotations

import json
import uuid

import pytest

from tests.conftest import make_tenant_user
from tests.test_auth import _login_as

_TEST_MEASURE = "test_faz2d_gecici_olcu"
_TEST_CUBE = "parti"  # pack-katmanında yaşar (demo/packs/sektor/boyahane/cubes/parti) —
# resolve_cube_yaml_for_edit'in "derlenmişten şirket katmanına kopyala" yolunu da kanıtlar.
_GOLDEN_ID = "faz2d-test-gecici-vaka"


@pytest.fixture
def clean_promote_artifacts():
    """Testten ÖNCE ortamın temiz olduğunu doğrular, testten SONRA (başarılı/başarısız
    fark etmez) yaratılan her şeyi siler ve derlenmiş projeyi orijinal haline geri kurar."""
    from pathlib import Path

    from app.config import get_settings

    settings = get_settings()
    base = settings.resolved_project_dir().parent
    company_yaml = base / "companies" / "demo-boyahane" / "cubes" / _TEST_CUBE / "metadata.yml"
    cases_path = base.parent / "eval" / "cases.yaml"
    assert not company_yaml.exists(), (
        f"{company_yaml} ZATEN vardı — önceki bir test koşumu temizlenmemiş olabilir")
    original_cases_text = cases_path.read_text(encoding="utf-8")
    assert _GOLDEN_ID not in original_cases_text

    yield {"company_yaml": company_yaml, "cases_path": cases_path}

    try:
        if company_yaml.exists():
            company_yaml.unlink()
            # boş kalan cubes/<cube>/ dizinini de temizle (kirli kalmasın)
            try:
                company_yaml.parent.rmdir()
            except OSError:
                pass
        cases_path.write_text(original_cases_text, encoding="utf-8")
    finally:
        # Derlenmiş projeyi ORİJİNAL (test-öncesi) kaynaklardan yeniden kur — testin
        # `compose_and_build` çağrısı yeni ölçüyü derlenmiş çıktıya da yazmış olabilir.
        from app.compose import compose_and_build

        compose_and_build(settings)


def test_measure_promote_full_lifecycle(client, clean_promote_artifacts):
    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import MeasureCandidate

    # 1) YAKALAMA'yı simüle et (gerçek Discovery capture'ın YAZDIĞI şekli birebir taklit
    # eder — bkz. app/routers/ask.py::_capture_measure_candidate): draft bir aday DB'de.
    with Session(engine) as s:
        cand = MeasureCandidate(
            company="demo-boyahane", question="test parti başına maks fire kg",
            sql="SELECT MAX(CASE WHEN ilk_seferde_tamam = 0 THEN kg ELSE 0 END) FROM parti_zengin",
            sample_rows_json=json.dumps({"columns": ["max_fire"], "rows": [[12.5]]}),
        )
        s.add(cand); s.commit(); s.refresh(cand)
        cid = str(cand.id)

    # 2) analyst: yalnız GÖRÜNTÜLEME (measure:read) — onaylayamaz (measure:approve gerektirir).
    make_tenant_user("faz2d-analyst@dima.local", "faz2d-parola-1", "analyst")
    analyst = _login_as(client, "faz2d-analyst@dima.local", "faz2d-parola-1")
    r = analyst.get("/measures/candidates")
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json()["candidates"])
    r = analyst.get(f"/measures/candidates/{cid}")
    assert r.status_code == 200 and r.json()["question"].startswith("test parti")
    approve_body = {
        "cube": _TEST_CUBE, "measure_name": _TEST_MEASURE,
        "expression": "MAX(CASE WHEN ilk_seferde_tamam = 0 THEN kg ELSE 0 END)", "type": "DOUBLE",
        "synonyms": ["test geçici azami fire"], "lower_is_better": True,
        "golden_case": {"id": _GOLDEN_ID, "q": "test geçici azami fire bu yıl",
                        "tags": ["faz2d-test"], "expect": "answer",
                        "shape": {"cube": _TEST_CUBE, "measures": [_TEST_MEASURE]}},
    }
    assert analyst.post(f"/measures/candidates/{cid}/approve", json=approve_body).status_code == 403

    # 3) admin: ONAYLAR — dry_plan gerçek şemaya karşı geçer, golden_case zorunlu (Pydantic
    # required alan), YAML'a yazılır (parti PACK katmanından şirket katmanına kopyalanarak).
    make_tenant_user("faz2d-admin@dima.local", "faz2d-parola-1", "admin")
    admin = _login_as(client, "faz2d-admin@dima.local", "faz2d-parola-1")
    r = admin.post(f"/measures/candidates/{cid}/approve", json=approve_body)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved"
    assert clean_promote_artifacts["company_yaml"].exists(), (
        "onay company-katmanı YAML'ını OLUŞTURMADI (pack'ten kopyalama başarısız)")
    assert _GOLDEN_ID in clean_promote_artifacts["cases_path"].read_text(encoding="utf-8")

    # 4) Aynı ad tekrar onaylanamaz (ad çakışması artık şemada gerçek).
    with Session(engine) as s:
        cand2 = MeasureCandidate(company="demo-boyahane", question="tekrar", sql="SELECT 1")
        s.add(cand2); s.commit(); s.refresh(cand2)
        cid2 = str(cand2.id)
    r = admin.post(f"/measures/candidates/{cid2}/approve", json=approve_body)
    assert r.status_code == 409

    # 5) YENİ ölçü GERÇEKTEN route()-lenebilir hale geldi mi? (en güçlü doğrulama — LLM'siz)
    r = admin.post("/ask", json={"question": "test geçici azami fire bu yıl", "execute": True})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["source"] == "cube", f"yeni ölçü deterministik route()'a düşmedi: {body}"
    assert body["cube_query"]["measures"] == [_TEST_MEASURE]

    # 6) DEPRECATE: NL-routing'ten gizlenir (MeasureOverride) ama route() ÖNCEDEN üretilen
    # cube_query ile YİNE de çalışır (ölçü YAML'dan silinmedi — yalnız keşfedilemez oldu).
    r = admin.post(f"/measures/candidates/{cid}/deprecate", json={"reason": "test temizliği"})
    assert r.status_code == 200 and r.json()["status"] == "deprecated"
    r = admin.post("/ask", json={"question": "test geçici azami fire bu yıl", "execute": True})
    assert r.status_code == 200
    assert r.json()["source"] != "cube", "deprecate edilen ölçü HÂLÂ NL ile bulunabiliyor"
    # Ama DOĞRUDAN cube_query ile (ör. panodaki eski widget/`/cube` chip düzenlemesi —
    # `parse_cube_query` katalog İNDEKSİNE karşı doğrular, `measure_synonyms`'a değil) hâlâ
    # ÇALIŞIR — kanıt kırılmadı (yalnız NL-KEŞFİ kapandı, ölçünün kendisi silinmedi).
    r = admin.post("/cube", json={
        "cube_query": {"cube": _TEST_CUBE, "measures": [_TEST_MEASURE]},
    })
    assert r.status_code == 200 and r.json().get("result") is not None, r.text


def test_measure_candidate_reject_lifecycle(client):
    """Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-14) — `reject_candidate` HTTP
    katmanında hiç test edilmemişti. Reddedilen bir aday YAZILMAZ (kabul edilenin AKSİNE,
    hiçbir dosya değişmez) — durumu "rejected"e döner, tekrar reddedilemez/onaylanamaz."""
    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import MeasureCandidate

    with Session(engine) as s:
        cand = MeasureCandidate(company="demo-boyahane", question="test reddedilecek aday",
                                sql="SELECT 1")
        s.add(cand); s.commit(); s.refresh(cand)
        cid = str(cand.id)

    make_tenant_user("faz2d-reject-analyst@dima.local", "faz2d-reject-1", "analyst")
    analyst = _login_as(client, "faz2d-reject-analyst@dima.local", "faz2d-reject-1")
    # analyst yalnız GÖRÜNTÜLEME (measure:read) — reddedemez (measure:approve gerektirir).
    assert analyst.post(f"/measures/candidates/{cid}/reject",
                        json={"note": "yetkisiz deneme"}).status_code == 403

    make_tenant_user("faz2d-reject-admin@dima.local", "faz2d-reject-1", "admin")
    admin = _login_as(client, "faz2d-reject-admin@dima.local", "faz2d-reject-1")
    r = admin.post(f"/measures/candidates/{cid}/reject", json={"note": "yanlış anlaşılmış"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "rejected"

    # zaten reddedilmiş bir aday TEKRAR reddedilemez/onaylanamaz (409 — durum makinesi).
    assert admin.post(f"/measures/candidates/{cid}/reject",
                      json={"note": "tekrar"}).status_code == 409
    approve_body = {"cube": _TEST_CUBE, "measure_name": "asla_yazilmayacak_olcu",
                    "expression": "1", "type": "DOUBLE",
                    "golden_case": {"id": "asla-yazilmayacak", "q": "x", "shape": {}}}
    assert admin.post(f"/measures/candidates/{cid}/approve",
                      json=approve_body).status_code == 409


def test_measure_blast_radius_counts_real_usage(client):
    """Doğrulama turu düzeltmesi (1 Ağustos 2026, P1-14) — `blast_radius` HTTP katmanında
    hiç test edilmemişti. Bir ölçüyü GERÇEKTEN kullanan bir Query Contract kaydı varsa,
    tarama bunu YAKALAMALI (deprecate-öncesi "kaç yerde kullanılıyor" uyarısının temeli)."""
    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import MeasureCandidate

    with Session(engine) as s:
        cand = MeasureCandidate(company="demo-boyahane", question="test blast-radius adayı",
                                sql="SELECT 1")
        s.add(cand); s.commit(); s.refresh(cand)
        cid = str(cand.id)

    # GERÇEK bir cube_query kullanımı üret (Query Contract'a kendi kaydını düşürür —
    # /cube ile AYNI çalıştırma yolu, ask.py'deki diğer contract testleriyle TUTARLI).
    client.post("/cube", json={"cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}})

    r = client.get(f"/measures/candidates/{cid}/blast-radius",
                   params={"cube": "parti", "measure_name": "toplam_ciro"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["contract_log_structured"] >= 1
    assert "note" in body

    # hiç kullanılmayan bir ölçü için hepsi SIFIR olmalı (yanlış-pozitif üretmemeli).
    r2 = client.get(f"/measures/candidates/{cid}/blast-radius",
                    params={"cube": "parti", "measure_name": "hic_kullanilmayan_olcu_xyz"})
    assert r2.json()["contract_log_structured"] == 0
    assert r2.json()["verified_query"] == 0
