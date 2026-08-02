"""FAZ 2a-4 — AYRIK AYLAR: sözleşme genişletmesi, ÖLÇÜLDÜKTEN sonra.

## Planın ön koşulu ölçüldü ve KARŞILANMADI

Plan bu kalemi *"`cube_query_to_sql`'in bu operatörü desteklediği ÖNCE doğrulanmalı"*
şartına bağlamıştı. Ölçüm (2026-08-02):

| deneme | sonuç |
|---|---|
| `{"operator": "in", "value": ["2026-01", "2026-03"]}` | derleniyor **ama** `WHERE tarih IN (...)` — HAM kolona, yalnız o iki GÜN |
| çoklu `dateRange` | `invalid type: sequence, expected a string` |
| `tarih__month` boyutuna filtre | `Unknown filter dimension` |
| `or` bloğu | `missing field 'dimension'` |

`in` operatörünün var olması **yanıltıcıydı**: kabul ediliyor ama ay kovasına değil ham
tarihe uygulanıyor. Motor ayrık ayı yerel olarak ifade **edemiyor**.

## Seçilen yol

Ay granülerliğinde grupla → kesilmiş kolona **dışarıdan** filtrele. Toplama gruplamadan
ÖNCE bittiği için sonuç kesindir; `measure_having` ile aynı sarma kalıbı. Gerçek veriyle
doğrulandı: aylık taban ile sarmalı sorgunun Ocak/Mart değerleri **birebir aynı**.

## Fail-closed

İşaret (`ayrik_aylar`) ve kapsayan aralık **birlikte** anlamlıdır. İşaret düşer de aralık
kalırsa cevap araya giren ayları da içerir — cube rozetli sessiz-yanlış. Bu yüzden
derleyici işaret varken ay granülerliği yoksa **`ValueError` atar**, sessizce kapsayan
aralığa düşmez. `blend_sql` de aynı gerekçeyle reddeder (CTE'ler işareti taşımaz).
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


def _plan(schema, soru):
    cr.reddi_sifirla()
    return cr.route(cr._norm(soru), schema)


# --- ASIL YETENEK ---------------------------------------------------------------

def test_AYRIK_aylar_artik_CEVAPLANIYOR(schema):
    """*"ocak ve mart"* meşru bir sorudur ve -0.5a'dan sonra bile cevaplanamıyordu
    (yalnız artık dürüstçe netleştirmeye düşüyordu). Sözleşme genişletildi."""
    r = _plan(schema, "ocak ve mart cirosu")
    assert r is not None, f"hâlâ cevapsız (red={cr.red_gerekcesi()})"
    cq = r["cube_query"]
    assert cq["ayrik_aylar"] == {"dimension": "tarih",
                                 "aylar": ["2026-01-01", "2026-03-01"]}
    assert cq["timeDimensions"] == [{"dimension": "tarih", "granularity": "month"}]


def test_SQL_gercekten_YALNIZ_o_aylari_donduruyor(schema, wren):
    """En sert kapı: derlenmesi yetmez, **satırlar** doğru olmalı. Kapsayan aralık
    (Ocak–Mart) Şubat'ı da içerir; sarma onu dışarıda bırakmalı."""
    r = _plan(schema, "ocak ve mart cirosu")
    sql = wren.cube_sql(dict(r["cube_query"]))
    rows = wren.query(sql)
    rows = rows.get("rows") if isinstance(rows, dict) else rows
    aylar = sorted(str(x["tarih__month"])[:7] for x in rows)
    assert aylar == ["2026-01", "2026-03"], f"araya giren ay sızdı: {aylar}"


def test_UC_ayrik_ay(schema):
    r = _plan(schema, "ocak mart mayıs cirosu")
    assert r and r["cube_query"]["ayrik_aylar"]["aylar"] == [
        "2026-01-01", "2026-03-01", "2026-05-01"]


# --- YIL ATFI: 2a-4'te bulunan sessiz-yanlış ------------------------------------

@pytest.mark.parametrize("soru,beklenen", [
    ("2025 ocak ve 2026 mart", ["2025-01-01", "2026-03-01"]),
    ("ocak 2025 ve mart 2026", ["2025-01-01", "2026-03-01"]),
    ("2025 aralık ayı ve 2026 ocak ayı", ["2025-12-01", "2026-01-01"]),
])
def test_YIL_her_aya_AYRI_atanir(soru, beklenen):
    """Eskiden yıl tek bir `re.search` ile bulunup TÜM aylara uygulanıyordu:
    *"2025 ocak ve 2026 mart"* → `[2025-01, 2025-03]`. Ayrık aylar netleştirmeye düştüğü
    için zararsızdı; 2a-4 onları cevaplanabilir yapınca aynı hata **kendinden emin yanlış
    bir sayı** üretirdi."""
    assert cr.ayrik_ay_kovalari(cr._norm(soru)) == beklenen


# --- DEĞİŞMEMESİ GEREKENLER (-0.5a korunuyor) -----------------------------------

def test_BITISIK_aylar_TEK_ARALIK_kalir(schema):
    """-0.5a'nın kararı: bitişik aylar tek `gte/lte` aralığı. Daha ucuz ve gruplama
    getirmiyor — sarma gereksiz."""
    r = _plan(schema, "ocak şubat mart cirosu")
    assert r and "ayrik_aylar" not in r["cube_query"]
    f = r["cube_query"]["filters"]
    assert f[0]["value"] == "2026-01-01" and f[1]["value"] == "2026-03-31"


def test_TEK_ay_degismedi(schema):
    r = _plan(schema, "temmuz ayı cirosu")
    assert r and "ayrik_aylar" not in r["cube_query"]


@pytest.mark.parametrize("soru", [
    "1 ocak 31 mart arası toplam üretim",   # eval `tarih-acik-aralik` — bu vaka KIRILDI
    "ocak ile mart arası ciro",
])
def test_ACIK_ARALIK_ayrik_sanilmaz(schema, soru):
    """Ölçülen gerileme (eval precision −0.9%): *"1 ocak 31 mart arası"* İKİ ay ADI taşır
    ve saf ay-taraması onu "ayrık" sanıyordu — oysa `_explicit_range_filters` onu zaten
    SÜREKLİ bir aralık olarak çözmüştü. Ayrık-ay yolu bir YEDEKTİR: yalnız başka hiçbir
    dönem çözülemediğinde çalışır."""
    r = _plan(schema, soru)
    assert r is not None, f"{soru!r} cevapsız (red={cr.red_gerekcesi()})"
    assert "ayrik_aylar" not in r["cube_query"], "açık aralık ayrık sanıldı"
    ops = [f["operator"] for f in r["cube_query"].get("filters") or []]
    assert ops.count("gte") == 1 and ops.count("lte") == 1, f"aralık bozuldu: {ops}"


# --- FAIL-CLOSED ----------------------------------------------------------------

def test_ISARET_varken_GRANULERLIK_yoksa_REDDEDILIR(wren):
    """Sessizce kapsayan aralığa düşmek Şubat'ı da katardı — cube rozetli yanlış cevap.
    Derlenmeyen bir sorgu, sessizce yanlış olandan iyidir."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"],
          "ayrik_aylar": {"dimension": "tarih", "aylar": ["2026-01-01", "2026-03-01"]},
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"},
                      {"dimension": "tarih", "operator": "lte", "value": "2026-03-31"}]}
    with pytest.raises(ValueError, match="granülerliği YOK"):
        wren.cube_sql(dict(cq))


def test_BLEND_ile_birlikte_REDDEDILIR(wren):
    """`blend_sql` CTE'leri açık alanlardan yeniden kurar ve işareti KOPYALAMAZ."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
          "ayrik_aylar": {"dimension": "tarih", "aylar": ["2026-01-01"]},
          "blend": [{"cube": "oee", "measures": ["ort_oee"]}]}
    with pytest.raises(ValueError, match="blend"):
        wren.blend_sql(cq)


def test_BOZUK_isaret_REDDEDILIR(wren):
    cq = {"cube": "parti", "measures": ["toplam_ciro"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
          "ayrik_aylar": {"dimension": "tarih", "aylar": []}}
    with pytest.raises(ValueError, match="eksik/bozuk"):
        wren.cube_sql(dict(cq))


# --- TAKİP: işaret BAYATLAYABİLİR --------------------------------------------------

@pytest.mark.parametrize("takip,neden", [
    ("tüm zamanlar", "dönem silinir ama sarma hâlâ Ocak+Mart'a daraltır"),
    ("geçen ay", "yeni dönem konur, sarma eski aylara daraltır → BOŞ sonuç"),
    ("yıllık", "granülerlik ay değil, sarma uygulanamaz → derleme hatası"),
])
def test_TAKIPTE_isaret_BAYATLARSA_deterministik_YOL_KAPANIR(schema, takip, neden):
    """`deterministic_refine` `prev`'i deep-copy eder, yani `ayrik_aylar` düzenlemeye
    TAŞINIR. Dönem/granülerlik değiştiyse işaret artık kullanıcının istediğini anlatmaz
    ve her üç vaka da SESSİZCE YANLIŞ üretir. Doğru davranış tahmin etmek değil,
    deterministik yolu kapatmak (`None` → dürüst zincir)."""
    ilk = _plan(schema, "ocak ve mart cirosu")
    assert ilk and ilk["cube_query"].get("ayrik_aylar")
    sonuc = cr.deterministic_refine(ilk["cube_query"], cr._norm(takip), schema)
    assert sonuc is None, f"{takip!r} ({neden}) sessizce uygulandı: {sonuc}"


def test_TAKIP_donemi_BOZMUYORSA_calisir(schema):
    """Kapı fazla geniş olmamalı: dönemi/granülerliği bozmayan bir düzenleme (boyut
    ekleme) çalışmaya devam etmeli."""
    ilk = _plan(schema, "ocak ve mart cirosu")
    sonuc = cr.deterministic_refine(ilk["cube_query"], cr._norm("müşteri bazında"), schema)
    assert sonuc is not None and sonuc.get("ayrik_aylar") == ilk["cube_query"]["ayrik_aylar"]


# --- UÇTAN UCA ------------------------------------------------------------------

def test_ASK_ZINCIRI_donem_kapisina_TAKILMIYOR(client):
    """`cozulemeyen_ay_listesi` bu soruyu netleştirmeye düşürüyordu. Artık `route()`
    dönem filtresi ürettiği için kapı geçilmeli ve YAPISAL cevap gelmeli."""
    d = client.post("/ask", json={"question": "ocak ve mart cirosu",
                                  "session_id": "t"}).json()
    assert d.get("cube_query"), f"yapısal cevap yok — not={d.get('note')!r}"
    assert d["cube_query"].get("ayrik_aylar")
