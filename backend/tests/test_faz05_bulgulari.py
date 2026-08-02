"""FAZ 0.5 — senaryo süitinin ÖLÇEREK bulduğu iki kusur. İkisi de aynı sınıf.

`lab/konusma_senaryolari.py` ilk koşumunda iki senaryo sınıfını **tamamen kırık**
buldu — ve ikisi de bu deponun en pahalı kusur ailesinden: `route()` bir boşluk
bırakıyor, boşluğu başka bir mekanizma **kendinden emin ve yanlış** dolduruyor.

## Bulgu 1 — `coklu_ay_trendli` **0/6**

*"ocak şubat mart arıza sayısı **değişim** trendi"* → kapsam kapısı `değişim`i tanımıyor
(`_uncovered = [ariza, degisim, sayisi]`) → `route()` `None` → `typo_correct` boşluğu
dolduruyor: ***"'değişim' yerine 'KISIM' mi demek istedin?"***

`trend` dolgu sözlüğündeydi ama **kardeşleri yoktu**. Hepsi aynı sınıf: bir ölçünün
zamandaki hareketini anlatan **anlatı kelimeleri**. Bu, 2a-3'ün (`sapma yüzdesi →
kar yüzdesi`) aynı sınıfı — öneri bir **semptom**, kök neden sözlük boşluğu.

**`fark` BİLEREK EKLENMEDİ**: ölçüldü, `enerji_sapma.toplam_enpg`'nin gerçek ölçü
sinonimi. Dolgu saymak onu gölgelerdi — 2a-1'in (`elektrik`) ölçümle reddedilen hatası.

## Bulgu 2 — `gorunum_donusumu` **0/5**

*"pasta grafik"* takibi → *"Bu takip mesajını önceki raporla ilişkilendiremedim."*
**Saf görünüm değişikliği TÜM RAPORU siliyordu.** Plan §4.7-1(e)(i) bunu
*"`deterministic_refine`'ın saf görünüm değişikliğini 'değişti' sayıp saymadığı
ÖLÇÜLMEDİ"* diye işaretlemişti. Ölçüldü: **saymıyor.**

Bu aynı zamanda §4.4'ün Faz 5 şartının doğrudan ihlaliydi: *"konuşma-modu metni SİLMEZ,
yalnız ÜSTÜNE biner — sonraki bir 'grafiğe çevir' isteği çalışabilsin."*
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


# --- BULGU 1: değişim ailesi ------------------------------------------------------

@pytest.mark.parametrize("kelime", ["degisim", "degisme", "artis", "azalis",
                                    "gelisim", "seyir", "yukselis", "dusus"])
def test_DEGISIM_ailesi_DOLGU(kelime):
    """`trend` ile aynı sınıf: ölçü/boyut adı değil, anlatı kelimesi."""
    assert kelime in cr._misc_hit_words(kelime)


def test_FARK_dolgu_DEGIL(schema):
    """`fark` `enerji_sapma.toplam_enpg`'nin GERÇEK ölçü sinonimi — dolgu saymak onu
    gölgelerdi (2a-1'in ölçümle reddedilen hatası). Bu test o kararı kilitler."""
    assert "fark" not in cr._misc_hit_words("bu yil fark")
    sahipli = any(cr._norm(str(s)) == "fark"
                  for c in schema["cubes"]
                  for syns in (c.get("measure_synonyms") or {}).values()
                  for s in syns)
    assert sahipli, "vaka bayat: `fark` artık katalog sinonimi değil, karar gözden geçirilmeli"


def test_DEGISIM_TRENDI_sorusu_CEVAPLANIYOR(schema):
    """Senaryo sınıfının kendisi: §1.6'nın canlı örneğinin bugünkü hâli."""
    cr.reddi_sifirla()
    r = cr.route(cr._norm("ocak subat mart ariza sayisi degisim trendi"), schema)
    assert r is not None, f"hâlâ cevapsız (red={cr.red_gerekcesi()})"
    f = r["cube_query"].get("filters") or []
    assert any(x["operator"] == "gte" for x in f) and any(x["operator"] == "lte" for x in f), \
        f"bitişik ay aralığı kurulmadı: {f}"


def test_KISIM_onerisi_KAYBOLDU(schema):
    """Kök neden kapanınca semptom da kapanır."""
    _, duzeltmeler = cr.typo_correct(
        cr._norm("ocak subat mart ariza sayisi degisim trendi"), schema)
    assert not [d for d in duzeltmeler if d.get("to") == "kisim"], \
        f"hâlâ 'değişim'→'kısım' öneriliyor: {duzeltmeler}"


# --- BULGU 2: saf görünüm değişikliği ---------------------------------------------

def test_SAF_GORUNUM_degisikligi_RAPORU_KORUR(client):
    """En sert kapı: grafik tipi isteği tüm raporu SİLMEMELİ."""
    ilk = client.post("/ask", json={"question": "bu yıl makine bazında arıza sayısı",
                                    "session_id": "g1", "execute": False}).json()
    assert ilk.get("cube_query"), f"hazırlık adımı başarısız: {ilk.get('note')!r}"
    ikinci = client.post("/ask", json={"question": "pasta grafik", "session_id": "g1",
                                       "execute": False,
                                       "cube_query": ilk["cube_query"],
                                       "history": ["önceki"]}).json()
    assert ikinci.get("cube_query"), \
        f"görünüm değişince YAPI KAYBOLDU: not={ikinci.get('note')!r}"
    assert ikinci["cube_query"]["cube"] == ilk["cube_query"]["cube"]
    assert ikinci.get("view_hint") == "pie"


@pytest.mark.parametrize("istek,beklenen", [
    ("tablo olarak göster", "table"),
    ("çizgi grafik", "line"),
    ("grafik ver", "chart"),
])
def test_GORUNUM_varyantlari(client, istek, beklenen):
    ilk = client.post("/ask", json={"question": "bu yıl makine bazında arıza sayısı",
                                    "session_id": "g2", "execute": False}).json()
    d = client.post("/ask", json={"question": istek, "session_id": "g2", "execute": False,
                                  "cube_query": ilk["cube_query"],
                                  "history": ["önceki"]}).json()
    assert d.get("cube_query"), f"{istek!r} raporu sildi"
    assert d.get("view_hint") == beklenen


def test_GORUNUM_ile_BIRLIKTE_yapisal_istek_NORMAL_zincire_gider(client):
    """Kapı fazla geniş olmamalı: *"pasta grafik olarak VARDİYA bazında"* bir YAPISAL
    düzenlemedir — saf görünüm değişikliği sayılıp kırılım YUTULMAMALI."""
    ilk = client.post("/ask", json={"question": "bu yıl makine bazında arıza sayısı",
                                    "session_id": "g3", "execute": False}).json()
    d = client.post("/ask", json={"question": "vardiya bazında pasta grafik",
                                  "session_id": "g3", "execute": False,
                                  "cube_query": ilk["cube_query"],
                                  "history": ["önceki"]}).json()
    dims = (d.get("cube_query") or {}).get("dimensions") or []
    assert "vardiya" in dims, f"kırılım yutuldu: dims={dims}"


def test_SENARYO_ARACI_calisiyor():
    """Faz 0.5'in aracı bir beyan değil, koşan bir üreteç olmalı."""
    from lab import konusma_senaryolari as ks

    assert callable(ks._uret) and callable(ks.kos) and callable(ks._rapor_yaz)
    assert ks.LIVE_BEKLE > 0, "--live hız sınırı yok — API'ye yığılır"
