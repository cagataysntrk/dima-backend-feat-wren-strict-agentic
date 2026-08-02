"""FAZ 2.2 — `ik` cube'u VIEW yerine MODEL tabanlı, ve bu göç **İKİ SIÇRAMALI**.

`parti` (Faz 1.0) ve `mizan` (Faz 2.1) göçleri tek sıçramalıydı. Bu üçüncüsü planın
gerçek sınavı: `ik_zengin` view'ı `personel_ozluk`'a `bordro.personel_kodu` üzerinden
**DOĞRUDAN** join'liyordu (iki bağımsız 1-sıçrama), oysa `bordro → personel_ozluk` diye
bir ilişki **beyan edilmemiştir** ve edilmemelidir de — doğru model `bordro → personel →
personel_ozluk` zinciridir. Yani göç, view'ın topolojisini kopyalamıyor; onu DÜZELTİYOR.

İki topoloji ancak `personel` ile `personel_ozluk` arasında öksüz satır YOKSA aynı sonucu
verir: view'da özlüğü olup personeli olmayan bir `personel_kodu` demografisini yine de
gösterirdi, zincirde göstermez. Bu yüzden `test_iki_sicramanin_on_kosulu_SIFIR_OKSUZ`
bir kabul kriteri değil, bir **ön koşul kaydıdır** — veri o koşulu bir gün bozarsa göç
değil, ilişki beyanı yanlış hale gelir ve testin adı bunu söyler.

Kabul kriteri (uygulamadan ÖNCE ölçüldü): 8 ölçü × 8 boyut + toplamlar + aylık kova =
**73 kombinasyonun 73'ü** view sürümüyle birebir aynı.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def svc_ve_db():
    """Servis + salt-okunur DuckDB — veri davranışını yönlendirmeden BAĞIMSIZ sınamak için."""
    import duckdb

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        yield svc, con
    finally:
        con.close()


@pytest.fixture(scope="module")
def ik(schema):
    c = next((x for x in schema["cubes"] if x["name"] == "ik"), None)
    assert c, "ik cube'u katalogda yok"
    return c


def _calistir(svc, con, cq):
    plan = svc.dry_plan(svc.cube_sql(cq))
    return plan, con.execute(plan.replace('boyahane."main".', "main.")).fetchall()


# `ik_zengin`in statement'i — göçün ölçüldüğü referans. Kasten ELLE tutulur: cube'dan
# türetilse ikisi birlikte kayar ve test hiçbir şey kanıtlamaz.
VIEW = """SELECT b.donem, b.personel_kodu, b.brut_maas, b.sgk_isci, b.mesai_ucreti,
       b.prim, b.net_maas, b.sgk_isveren,
       pe.departman, pe.cinsiyet, pe.vardiya AS personel_vardiya,
       po.dogum_tarihi, po.egitim, po.pozisyon, po.medeni_hal,
       CAST(b.donem || '-01' AS DATE) AS donem_tarih
FROM main.bordro b
LEFT JOIN main.personel pe ON b.personel_kodu = pe.personel_kodu
LEFT JOIN main.personel_ozluk po ON b.personel_kodu = po.personel_kodu"""

OLCU = {
    "toplam_brut_maas": "SUM(brut_maas)",
    "toplam_net_maas": "SUM(net_maas)",
    "toplam_isveren_maliyeti": "SUM(brut_maas + sgk_isveren)",
    "toplam_mesai_ucreti": "SUM(mesai_ucreti)",
    "toplam_prim": "SUM(prim)",
    "toplam_sgk": "SUM(sgk_isci + sgk_isveren)",
    "ort_brut_maas": "ROUND(AVG(brut_maas),0)",
    "personel_sayisi": "COUNT(DISTINCT personel_kodu)",
}
_YAS = ("CASE WHEN dogum_tarihi IS NULL THEN NULL "
        "WHEN date_diff('year', dogum_tarihi, current_date) < 30 THEN '<30' "
        "WHEN date_diff('year', dogum_tarihi, current_date) < 40 THEN '30-39' "
        "WHEN date_diff('year', dogum_tarihi, current_date) < 50 THEN '40-49' ELSE '50+' END")
BOYUT = {"departman": "departman", "cinsiyet": "cinsiyet", "egitim": "egitim",
         "pozisyon": "pozisyon", "medeni_hal": "medeni_hal",
         "personel_vardiya": "personel_vardiya", "donem": "donem", "yas_grubu": _YAS}

# 2 sıçrama gerektirenler (`personel`in KENDİ calc kolonları üzerinden `personel_ozluk`).
IKI_SICRAMA = {"egitim", "pozisyon", "medeni_hal", "yas_grubu"}


def _norm(rows):
    return sorted(tuple(round(float(x), 6) if isinstance(x, (int, float)) else x for x in r)
                  for r in rows)


def test_base_object_MODEL_olmali(ik, schema):
    assert ik["base_object"] == "bordro", f"geçiş geri alınmış: {ik['base_object']!r}"
    assert ik["base_object"] in {m["name"] for m in schema.get("models", [])}


def test_iki_sicramanin_on_kosulu_SIFIR_OKSUZ(svc_ve_db):
    """Göçün MEŞRUİYET koşulu — view iki bağımsız 1-sıçrama, göç bir 2'li zincir.

    Özlükte olup `personel`de olmayan bir `personel_kodu` çıkarsa iki topoloji AYRIŞIR:
    view demografiyi gösterir, zincir NULL döner. Bugün her yönde sıfır; bu test o koşulu
    kaydeder ki bozulduğunda suçlanan taraf göç değil, eksik `personel` kaydı olsun.
    """
    _, con = svc_ve_db
    ozluk_fazlasi = con.execute(
        "select count(*) from main.personel_ozluk o "
        "left join main.personel p on o.personel_kodu = p.personel_kodu "
        "where p.personel_kodu is null").fetchone()[0]
    assert ozluk_fazlasi == 0, (
        f"{ozluk_fazlasi} özlük kaydının `personel` karşılığı yok — 2 sıçramalı zincir "
        "bunların demografisini KAYBEDER, view kaybetmiyordu")
    for hedef in ("personel", "personel_ozluk"):
        oksuz = con.execute(
            f"select count(*) from main.bordro b "
            f"left join main.{hedef} t on b.personel_kodu = t.personel_kodu "
            f"where t.personel_kodu is null").fetchone()[0]
        assert oksuz == 0, f"bordro satırlarının {oksuz} tanesi {hedef}'e eşleşmiyor"


@pytest.mark.parametrize("olcu", sorted(OLCU))
@pytest.mark.parametrize("boyut", [*sorted(BOYUT), None])
def test_sonuclar_view_ile_BIREBIR_AYNI(svc_ve_db, olcu, boyut):
    """Göçün kabul kriteri. 72 kombinasyon — ölçü × boyut + boyutsuz toplam."""
    svc, con = svc_ve_db
    if boyut is None:
        beklenen = con.execute(f"SELECT {OLCU[olcu]} FROM ({VIEW})").fetchall()
        cq = {"cube": "ik", "measures": [olcu]}
    else:
        beklenen = con.execute(
            f"SELECT {BOYUT[boyut]} AS d, {OLCU[olcu]} FROM ({VIEW}) GROUP BY 1").fetchall()
        cq = {"cube": "ik", "measures": [olcu], "dimensions": [boyut]}
    _, alinan = _calistir(svc, con, cq)
    assert _norm(alinan) == _norm(beklenen)


def test_aylik_kova_view_ile_BIREBIR_AYNI(svc_ve_db):
    """`donem_tarih` view'da türetiliyordu (`CAST(donem || '-01' AS DATE)`); base MODEL
    olunca ifade cube'un `time_dimensions`'ına taşındı — kova aynı kalmalı."""
    svc, con = svc_ve_db
    _, alinan = _calistir(svc, con, {
        "cube": "ik", "measures": ["toplam_brut_maas"],
        "timeDimensions": [{"dimension": "donem_tarih", "granularity": "month"}]})
    beklenen = con.execute(
        f"SELECT date_trunc('month', donem_tarih), SUM(brut_maas) FROM ({VIEW}) GROUP BY 1"
    ).fetchall()
    assert _norm(alinan) == _norm(beklenen)
    assert len(alinan) > 1, "aylık kova tek satır döndü"


@pytest.mark.parametrize("boyut", sorted(IKI_SICRAMA))
def test_iki_sicramali_boyut_GERCEKTEN_iki_join_kurar(svc_ve_db, boyut):
    """Topolojinin kanıtı: `egitim`/`pozisyon`/`medeni_hal`/`yas_grubu` `bordro`da da,
    `personel`de de fiziksel olarak YOK — yalnız `personel_ozluk`'ta var. İki join
    görünüyorsa zincir gerçekten kuruluyor demektir (ve `dry_plan`'ın başarılı dönmesi
    tek başına bunu kanıtlamaz, bkz. MIMARI.md §5)."""
    svc, con = svc_ve_db
    plan, satirlar = _calistir(svc, con, {
        "cube": "ik", "measures": ["toplam_brut_maas"], "dimensions": [boyut]})
    assert plan.upper().count(" JOIN ") == 2, f"beklenen 2 join, plan:\n{plan}"
    assert len(satirlar) > 1, f"{boyut} tek satır döndü — zincir demografiyi getirmemiş"


def test_join_pruning_yerel_olcuyu_JOINSIZ_birakir(svc_ve_db):
    """`personel_sayisi` yalnız `bordro.personel_kodu`ya bakar. View tabanlıyken sorgu
    3 tabloyu tarıyordu; model tabanlı sürümde join pruning onu **sıfır join**'e indirir.
    Göçün bakım dışındaki ikinci kazancı budur."""
    svc, con = svc_ve_db
    plan, _ = _calistir(svc, con, {"cube": "ik", "measures": ["personel_sayisi"]})
    assert plan.upper().count(" JOIN ") == 0, f"gereksiz JOIN üretildi:\n{plan}"


def test_medeni_hal_calc_kolonu_PERSONELE_eklendi():
    """Göçün gerektirdiği TEK yeni model kolonu. `personel` zaten `dogum_tarihi`/`egitim`/
    `pozisyon`u özlükten çekiyordu ama `medeni_hal`i çekmiyordu; view onu doğrudan
    okuduğu için eksiklik görünmüyordu."""
    import json

    from app.config import get_settings

    m = json.loads((get_settings().resolved_project_dir() / "target" / "mdl.json")
                   .read_text(encoding="utf-8"))
    p = next(x for x in m["models"] if x["name"] == "personel")
    c = next((x for x in p["columns"] if x["name"] == "medeni_hal"), None)
    assert c and c.get("isCalculated"), "personel.medeni_hal calc kolonu yok"
    assert c["expression"] == "personel_ozluk.medeni_hal"


def test_uretilen_kolonlar_BOYUT_olarak_yayinlanmadi(ik):
    """`expose:` bloğu `dimension: false` kullanıyor: cube TÜM boyutlarını kendi
    etiket/sözlükleriyle ZATEN tanımlıyor, üretecin ikinci bir kopya yayımlaması router'ın
    arama uzayını iki katına çıkarır ve `personel_departman` gibi mekanik adlar sözlüğü
    kirletirdi (bkz. MIMARI.md §5 "kelimeye özel yama yok" disiplini)."""
    mekanik = [d for d in ik["dimensions"] if d.startswith("personel_") and d != "personel_vardiya"]
    assert not mekanik, f"üreteç mekanik adlı boyut yayımlamış: {mekanik}"
    assert "departman" in ik["dimensions"] and "medeni_hal" in ik["dimensions"]
