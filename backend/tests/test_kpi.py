"""Cross-cube KPI-kompozisyon testleri: compose gate + formül + eşleşme + resolver.

KPI (CCC = DSO + DIO − DPO) tek cube ölçüsü OLAMAZ — bileşenleri iki türev-view'dan
çeker. DB'ye BAĞLANMAZ: compose/load yereldir; resolver sahte svc ile doğrulanır.
"""

from __future__ import annotations

from pathlib import Path

from app.compose import build, compose
from app.kpi import eval_formula, load_kpis, resolve_kpi

DEMO = Path(__file__).resolve().parents[1] / "demo"


def _project(tmp_path_factory, company: str) -> Path:
    out = tmp_path_factory.mktemp(f"{company}-kpi")
    compose(company, DEMO, out)
    build(out)
    return out


def test_ccc_yalniz_iki_turev_view_uretilince_derlenir(tmp_path_factory):
    """gulteks (logo-3): karlilik_src + cari_finans_src ikisi de üretilir → CCC biner."""
    out = _project(tmp_path_factory, "gulteks")
    kpis = load_kpis(out)
    assert "ccc" in kpis
    spec = kpis["ccc"]
    assert spec["formula"] == "dso + dio - dpo"
    assert set(spec["components"]) == {"dso", "dio", "dpo"}
    # Bileşen SQL'i KANONİK view kolonlarına dayanır (ERP-özel değil) — DB-bağımsız.
    assert "cari_finans_src" in spec["components"]["dso"]["sql"]
    assert "karlilik_src" in spec["components"]["dio"]["sql"]
    assert "{where}" in spec["components"]["dpo"]["sql"]  # dönem yüklemi enjekte edilebilir


def test_likidite_kpileri_mizan_uzerinde(tmp_path_factory):
    """gitas (netsis): TBLMUHFIS bağlanınca mizan_src üretilir → 4 likidite KPI'sı
    (cari oran/asit-test/nakit oranı/net işletme sermayesi) derlenir. Bileşen SQL'i
    Tekdüzen hesap-aralıklarını (1xx/3xx/15x/10x) mizan_src kanonik kolonlarından toplar."""
    from app import cube_router as cr
    from app.llm import _norm

    out = _project(tmp_path_factory, "gitas")
    kpis = load_kpis(out)
    assert {"cari_oran", "asit_test", "nakit_orani", "net_isletme_sermayesi"} <= set(kpis)
    cari = kpis["cari_oran"]
    assert cari["formula"] == "donen_varlik / kv_yabanci_kaynak"
    assert cari.get("decimals") == 2  # oran 2 ondalık
    # bileşen SQL'i mizan_src + Tekdüzen sınıf filtresi (ERP-özel değil, ulusal standart)
    assert "mizan_src" in cari["components"]["donen_varlik"]["sql"]
    assert "LEFT(hesap_kodu, 1) = '1'" in cari["components"]["donen_varlik"]["sql"]
    # mizan cube de üretildi (borç/alacak/bakiye)
    import json
    mdl = json.loads((out / "target" / "mdl.json").read_text())
    assert "mizan" in {c["name"] for c in mdl["cubes"]}
    # routing: likidite adları KPI'ya (büyük harf İ dahil — combining-dot fix)
    schema = {"kpis": [{"name": k, "synonyms": [_norm(s) for s in v.get("synonyms", [])]}
                       for k, v in kpis.items()], "cubes": []}
    assert cr.match_kpi(_norm("cari oran"), schema) == "cari_oran"
    assert cr.match_kpi(_norm("CARİ ORAN NEDİR"), schema) == "cari_oran"
    assert cr.match_kpi(_norm("net işletme sermayesi"), schema) == "net_isletme_sermayesi"


def test_cross_cube_blend_ticaret_karlilik(tmp_path_factory, monkeypatch):
    """Canlı 2026-07-25 'kâr da ekle': iki cube'un ölçüsü TEK raporda. cross_cube_add,
    mevcut cube'da olmayan (karlilik.brut_kar) ölçüyü blend olarak katar; blend_sql
    paylaşılan zaman kovasında FULL OUTER JOIN üretir. Aynı-cube ekleme blend DEĞİL."""
    import app.wren_service as ws
    from app import cube_router as cr
    from app.llm import _norm
    from app.wren_service import WrenService

    monkeypatch.setattr(ws.WrenService, "_db_reachable", lambda *a, **k: False)
    out = _project(tmp_path_factory, "gitas")
    svc = WrenService(project_dir=out, datasource="mssql", connection_info={})
    schema = svc.schema()
    prev = {"cube": "ticaret", "measures": ["satis_tutari"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    blend = cr.cross_cube_add(prev, _norm("kâr da ekle"), schema)
    assert blend is not None
    assert blend["blend"] == [{"cube": "karlilik", "measures": ["brut_kar"]}]
    # aynı-cube ekleme (alım ticaret'te var) → blend DEĞİL (refine'a bırakılır)
    assert cr.cross_cube_add(prev, _norm("alım tutarı da ekle"), schema) is None
    # ekleme-niyeti yoksa → None
    assert cr.cross_cube_add(prev, _norm("kâr göster"), schema) is None
    # blend_sql: iki cube, paylaşılan tarih__month üstünde FULL OUTER JOIN, her iki ölçü
    sql = svc.blend_sql(blend)
    assert "FULL OUTER JOIN" in sql.upper()
    assert "satis_tutari" in sql and "brut_kar" in sql and "tarih__month" in sql

    # CROSS-CUBE BOYUT GEÇİŞİ: ticaret'te stok_adi yok → satış+stok_adi taşıyan cube'a geç.
    prev2 = {"cube": "ticaret", "measures": ["satis_tutari"]}
    dsw = cr.cross_cube_dim_switch(prev2, _norm("ürün bazlı"), schema)
    assert dsw is not None and dsw["cube"] in {"karlilik", "mal"}
    assert "stok_adi" in dsw["dimensions"] and dsw["measures"] == ["satis_tutari"]
    # müşteri ticaret'te ZATEN var (cari_adi) → geçiş YOK (normal refine)
    assert cr.cross_cube_dim_switch(prev2, _norm("müşteri bazlı"), schema) is None


def test_topn_ranking_measure_ayri(tmp_path_factory, monkeypatch):
    """Canlı 2026-07-25 (yanlış veri): "en çok SATILAN 10 ürünün aylık ORTALAMA FİYATI" →
    sıralama ölçütü GÖSTERİLEN ölçüyü (ort_satis_fiyati) alıp en PAHALI kalemleri seçiyordu.
    Sıralama "en çok X"ten (satılan→satis_miktari) gelmeli; gösterim ölçüsü ayrı kalmalı."""
    import app.wren_service as ws
    from app import cube_router as cr
    from app.llm import _norm
    from app.wren_service import WrenService

    monkeypatch.setattr(ws.WrenService, "_db_reachable", lambda *a, **k: False)
    out = _project(tmp_path_factory, "gitas")
    schema = WrenService(project_dir=out, datasource="mssql", connection_info={}).schema()
    p = cr.route(_norm("bu yıl en çok satılan 10 ürünün aylık ortalama fiyatlarını getir"), schema)
    cq = p["cube_query"]
    assert cq["measures"] == ["ort_satis_fiyati"]          # GÖSTERİLEN ölçü: ortalama fiyat
    assert cq["entity_limit"]["measure"] == "satis_miktari"  # SIRALAMA ölçütü: satılan (miktar)
    assert cq["entity_limit"]["n"] == 10


def test_compose_gate_eksik_view_kpi_uretmez(tmp_path, monkeypatch):
    """requires_views'in tamamı yoksa KPI atlanır (dürüst gate)."""
    from app import compose as cmod

    base = tmp_path / "demo"
    (base / "packs" / "modul" / "kpi").mkdir(parents=True)
    (base / "packs" / "modul" / "kpi" / "x.yml").write_text(
        "name: x\nrequires_views: [yok_src]\ncomponents: {}\n")
    out = tmp_path / "out"
    (out / "views" / "var_src").mkdir(parents=True)  # başka view var, yok_src YOK
    (out / "views" / "var_src" / "metadata.yml").write_text("name: var_src\n")
    cmod._compose_kpis(base, out)
    assert not (out / "kpis" / "x.yml").exists()


def test_eval_formula_guvenli_aritmetik():
    import pytest

    assert eval_formula("dso + dio - dpo", {"dso": 15.5, "dio": 0.2, "dpo": 38.2}) == pytest.approx(-22.5)
    assert eval_formula("a * 2 - b", {"a": 10, "b": 5}) == 15
    # İzinsiz ifade (fonksiyon çağrısı) reddedilir — eval YOK.
    with pytest.raises(ValueError):
        eval_formula("__import__('os').system('x')", {})
    with pytest.raises(KeyError):
        eval_formula("bilinmeyen + 1", {})


def test_match_kpi_en_uzun_sinonim_kazanir(tmp_path_factory):
    from app import cube_router as cr
    from app.llm import _norm

    schema = {"kpis": [{"name": "ccc", "synonyms": [_norm(s) for s in
              ["ccc", "nakit", "nakit dönüşüm döngüsü"]]}], "cubes": []}
    assert cr.match_kpi(_norm("nakit dönüşüm döngüsü bu yıl"), schema) == "ccc"
    assert cr.match_kpi(_norm("ccc kaç gün"), schema) == "ccc"
    assert cr.match_kpi(_norm("toplam satış"), schema) is None


def test_resolve_kpi_bilesenleri_calistirir_ve_formulu_kurar():
    """Sahte svc: her bileşen SQL'ine sabit skaler döner; resolver formülü kurar."""
    vals = {"dso": 15.5, "dio": 0.2, "dpo": 38.2}
    order = iter(["dso", "dio", "dpo"])  # components sırası

    class FakeSvc:
        def query(self, sql, limit=1):
            # SQL'den bileşeni ayırt et (view adı + payda ipucu).
            if "SUM(borc)" in sql or "bal > 0" in sql:
                v = vals["dso"]
            elif "bal < 0" in sql:
                v = vals["dpo"]
            else:
                v = vals["dio"]
            return {"rows": [{"value": v}]}

    spec = {
        "name": "ccc", "label": "CCC", "unit": "gün", "lower_is_better": True,
        "formula": "dso + dio - dpo",
        "components": {
            "dso": {"label": "DSO", "unit": "gün", "sql": "... bal > 0 SUM(borc) {where}"},
            "dio": {"label": "DIO", "unit": "gün", "sql": "... running_stok_deger {where}"},
            "dpo": {"label": "DPO", "unit": "gün", "sql": "... bal < 0 {where}"},
        },
    }
    card = resolve_kpi(FakeSvc(), spec)
    assert card["value"] == -22.5
    assert card["lower_is_better"] is True
    assert {c["key"]: c["value"] for c in card["components"]} == vals
