"""Kaynak faseti testleri (ADR-0017): compose katmanları + lehçe adaptörü.

Fixture şirketleri gerçek müşteri kapsamlarıdır: atiksan (mikro-v16 ⊕ geri-donusum)
ve gulteks (logo-3 ⊕ kumas-ticareti, firma 121 / dönem 01 bağlamalı). Lab SQL
Server'ına BAĞLANMAZ — compose/build ve SQL üretimi tamamen yereldir.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.compose import build, compose

DEMO = Path(__file__).resolve().parents[1] / "demo"


@pytest.fixture(scope="module")
def atiksan_project(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("atiksan-project")
    compose("atiksan", DEMO, out)
    build(out)
    return out


@pytest.fixture(scope="module")
def gulteks_project(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("gulteks-project")
    compose("gulteks", DEMO, out)
    build(out)
    return out


def test_atiksan_kaynak_ve_sektor_katmanlari(atiksan_project: Path):
    mdl = json.loads((atiksan_project / "target" / "mdl.json").read_text())
    model_names = {m["name"] for m in mdl["models"]}
    assert {"cari_hesaplar", "cari_hesap_hareketleri", "stoklar", "stok_hareketleri"} <= model_names
    # karlilik: jenerik türev-metrik cube (mikro turev.yml binding'inden üretildi)
    assert {c["name"] for c in mdl["cubes"]} == {"cari", "ticaret", "karlilik", "cari_finans"}
    assert any(v["name"] == "karlilik_src" for v in mdl.get("views", []))  # üretilen view
    # Fiziksel bağ: model adı soyut, tablo gerçek Mikro adı
    stoklar = next(m for m in mdl["models"] if m["name"] == "stoklar")
    assert stoklar["tableReference"]["table"] == "STOKLAR"
    assert stoklar["tableReference"]["schema"] == "dbo"
    # Sektör paketi içeriği bindi (geri dönüşüm kuralları)
    assert (atiksan_project / "knowledge" / "rules" / "geri-donusum.md").exists()


def test_gulteks_sablon_binding_ayrimi(gulteks_project: Path):
    """logo-3 pack'i model taşımaz; şirket katmanı firma/dönem bağlamalı modelleri
    getirir — soyut ad (faturalar) → fiziksel önekli tablo (LG_121_01_INVOICE)."""
    mdl = json.loads((gulteks_project / "target" / "mdl.json").read_text())
    model_names = {m["name"] for m in mdl["models"]}
    assert {"cari_kartlar", "cari_hareketleri", "stok_kartlari", "faturalar",
            "fatura_satirlari"} <= model_names
    # karlilik: jenerik türev-metrik (logo turev.yml binding'inden üretildi, row_filter=CANCELLED=0)
    assert {c["name"] for c in mdl["cubes"]} == {"cari", "ticaret", "mal", "karlilik", "cari_finans"}
    assert any(v["name"] == "karlilik_src" and "CANCELLED" in (v.get("statement") or "")
               for v in mdl.get("views", []))
    faturalar = next(m for m in mdl["models"] if m["name"] == "faturalar")
    assert faturalar["tableReference"]["table"] == "LG_121_01_INVOICE"
    kartlar = next(m for m in mdl["models"] if m["name"] == "cari_kartlar")
    assert kartlar["tableReference"]["table"] == "LG_121_CLCARD"  # kart tablosu dönemsiz
    # İlişkiler soyut adlarla pack'ten geldi ve derlendi
    assert {r["name"] for r in mdl["relationships"]} == {
        "cari_hareket_cari", "fatura_cari", "fatura_satir_stok", "fatura_satir_cari"}


def test_gereksinim_ve_pack_dosyalari_ciktiya_sizmaz(atiksan_project: Path):
    assert not (atiksan_project / "gereksinim.yml").exists()
    assert not (atiksan_project / "pack.yml").exists()


def test_kesisim_katmani_yalniz_eslesen_sektorle_biner(tmp_path: Path):
    base = tmp_path / "demo"
    # Asgari faset ağacı: kaynak k1 (kesişim içerikli), sektörler s1/s2, şirket k1+s1 seçer.
    (base / "packs" / "kaynak" / "k1" / "sektor" / "s1").mkdir(parents=True)
    (base / "packs" / "kaynak" / "k1" / "sektor" / "s2").mkdir(parents=True)
    (base / "packs" / "kaynak" / "k1" / "models").mkdir(parents=True)
    (base / "packs" / "kaynak" / "k1" / "models" / "m.yml").write_text("kaynak: k1")
    (base / "packs" / "kaynak" / "k1" / "sektor" / "s1" / "binding.yml").write_text("kesisim: s1")
    (base / "packs" / "kaynak" / "k1" / "sektor" / "s2" / "binding.yml").write_text("kesisim: s2")
    (base / "packs" / "sektor" / "s1").mkdir(parents=True)
    (base / "packs" / "sektor" / "s1" / "pack.yml").write_text("name: s1\nmoduller: []\n")
    (base / "companies" / "acme").mkdir(parents=True)
    (base / "companies" / "acme" / "company.yml").write_text(
        "name: acme\nkaynaklar: [k1]\nsektorler: [s1]\n"
    )

    out = tmp_path / "out"
    info = compose("acme", base, out)

    assert (out / "models" / "m.yml").exists()  # kaynak ana içeriği bindi
    assert (out / "binding.yml").read_text() == "kesisim: s1"  # yalnız SEÇİLİ sektörün kesişimi
    # Kaynağın sektor/ alt-ağacı olduğu gibi kopyalanmadı (kesişim değilken sızmaz):
    assert not (out / "sektor").exists()
    assert "packs/kaynak/k1/sektor/s1" in " ".join(info["layers"])


# ⟳ FAZ 2.1(c2) AD GÖÇÜ: aşağıdaki İKİ test `atiksan` (mikro-v16) fixture'ını kullanır ve
# oradaki ölçü `satis_tutari` → `satis_tutari_hareket` oldu (grain: stok hareketi).
# Öteki testler logo-3/netsis `ticaret`'ini kullanıyor — orada ad DEĞİŞMEDİ (grain: fatura).
def test_dialect_sql_mssql_donusumu(atiksan_project: Path):
    from app.wren_service import WrenService

    svc = WrenService(atiksan_project, datasource="mssql", connection_info={})
    sql = svc.cube_sql(
        {
            "cube": "ticaret",
            "measures": ["satis_tutari_hareket"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
        }
    )
    assert "DATEADD(MONTH, DATEDIFF(MONTH," in sql and "sth_tarih" in sql
    assert "GROUP BY 1" not in sql  # T-SQL ordinal kabul etmez — ifade genişletilir
    assert "DATE_TRUNC" not in sql and "DATETRUNC" not in sql  # 2022-öncesi sunucu uyumu

    # Sıralama+limit sarmalayıcısı: LIMIT, T-SQL'de TOP'a çevrilir.
    top5 = svc.cube_sql(
        {"cube": "cari", "measures": ["bakiye"], "dimensions": ["cari_kodu"],
         "order": {"measure": "bakiye", "direction": "desc"}, "limit": 5}
    )
    assert "TOP 5" in top5.upper()


def test_dialect_sql_gulteks_iptal_filtreli(gulteks_project: Path):
    from app.wren_service import WrenService

    svc = WrenService(gulteks_project, datasource="mssql", connection_info={})
    sql = svc.cube_sql(
        {
            "cube": "ticaret",
            "measures": ["satis_tutari", "alim_tutari"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
        }
    )
    assert "DATEADD(MONTH, DATEDIFF(MONTH," in sql and "DATE_" in sql
    assert "TRCODE = 8" in sql and "TRCODE = 1" in sql  # satış/alım ayrımı
    assert "CANCELLED = 0" in sql  # iptal faturalar dışarıda


def test_dialect_sql_duckdb_noop(atiksan_project: Path):
    from app.wren_service import WrenService

    svc = WrenService(atiksan_project, datasource="duckdb", connection_info={})
    sql = svc.cube_sql(
        {
            "cube": "ticaret",
            "measures": ["satis_tutari_hareket"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
        }
    )
    assert "DATE_TRUNC('month', sth_tarih)" in sql  # DuckDB yolu değişmedi


def test_gitas_calculated_ad_kolonlari(tmp_path_factory):
    """Netsis pilotu (ADR-0017 §6-1): relationship'li calculated kolon — cube boyutu
    cari/stok ADI kullanır, JOIN'i motor model CTE'sinin içinde üretir."""
    from app.wren_service import WrenService

    out = tmp_path_factory.mktemp("gitas-project")
    compose("gitas", DEMO, out)
    build(out)
    mdl = json.loads((out / "target" / "mdl.json").read_text())
    faturalar = next(m for m in mdl["models"] if m["name"] == "faturalar")
    cari_adi = next(c for c in faturalar["columns"] if c["name"] == "cari_adi")
    assert cari_adi["isCalculated"] is True
    assert cari_adi["expression"] == "cari_kartlar.CARI_ISIM"
    handle = next(c for c in faturalar["columns"] if c["name"] == "cari_kartlar")
    assert handle["type"] == "cari_kartlar"  # lineage kuralı: type = model adı

    svc = WrenService(out, datasource="mssql", connection_info={})
    sql = svc.cube_sql({"cube": "ticaret", "measures": ["satis_tutari"],
                        "dimensions": ["cari_adi"]})
    plan = svc.dry_plan(sql)  # DB'ye dokunmaz — transpile + model CTE'leri
    assert "JOIN" in plan.upper()  # ad, JOIN'le geliyor
    assert "CARI_ISIM" in plan


def test_fix_tr_kod_sayfasi_onarimi():
    """Gitaş bulgusu: CP1254 verisi CP1252 collation'lı kolondan mojibake gelir
    (Ð=Ğ, Ý=İ, Þ=Ş). Onarım yalnız bozuk string'lere dokunur — düzgün Türkçe
    cp1252'ye encode edilemediği için değişmeden kalır."""
    from app.wren_service import WrenService

    fix = WrenService._fix_tr
    assert fix("MES YAÐ VE GIDA SANAYÝ VE TÝC. A.Þ.") == "MES YAĞ VE GIDA SANAYİ VE TİC. A.Ş."
    assert fix("SOYA FASULYESÝ KÜSPESÝ") == "SOYA FASULYESİ KÜSPESİ"
    assert fix("ýþýk ýðne") == "ışık ığne"
    dogru = "DOĞRU ŞĞİ üğçöşi metni"
    assert fix(dogru) == dogru  # düzgün metne dokunulmaz
    assert fix(12345) == 12345 and fix(None) is None  # sayı/None geçer


def test_always_filter_ve_additive_metadata(gulteks_project):
    """cube-katalog §3/§8: always_filter WHERE'e enjekte edilir (CANCELLED=0 ölçü
    ifadelerinden çıkar); bakiye ölçüleri schema'da semi_additive listelenir."""
    from app.wren_service import WrenService

    svc = WrenService(gulteks_project, datasource="mssql", connection_info={})
    schema = svc.schema()
    cari = next(c for c in schema["cubes"] if c["name"] == "cari")
    # SADECE net bakiye semi-additive (zaman kovasında dönem-sonu snapshot, düz SUM değil).
    # toplam_borc/toplam_alacak AKIŞtır (additive:full) — "aylara göre borç" meşru additive
    # kırılım; panel bunları semi işaretlemenin gereksiz LLM'e ittiğini gösterdi.
    assert set(cari["semi_additive"]) == {"bakiye"}
    # ticaret always_filter → üretilen SQL'in WHERE'inde CANCELLED, ölçü ifadesinde DEĞİL
    sql = svc.cube_sql({"cube": "ticaret", "measures": ["satis_tutari"]})
    assert "CANCELLED" in sql.upper()  # always_filter enjekte edildi
    # ölçü ifadesi artık CANCELLED içermiyor (cube YAML'ında temizlendi)
    tic_mdl = next(c for c in __import__("json").loads((gulteks_project / "target" / "mdl.json").read_text())["cubes"] if c["name"] == "ticaret")
    assert all("CANCELLED" not in m["expression"] for m in tic_mdl["measures"])
