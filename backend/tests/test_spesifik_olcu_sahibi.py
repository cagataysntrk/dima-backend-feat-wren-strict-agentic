"""FAZ 2a-3 — KİMLİK ASİMETRİSİ: tek cube eşleşmesi ölçü-kanıtını atlıyordu.

## Ölçülen kusur (2026-08-02)

`_match_cube` `len(hits) == 1` dalında **koşulsuz** dönüyordu. Ölçü-kanıtı mekanizması —
*"jenerik cube-sinonimi spesifik ölçüyü GÖLGELİYORDU"* diye zaten yazılmış ve yorumlanmış
kural — YALNIZ `len(hits) > 1` dalında çalışıyordu. Yani kural bir dalda uygulanıyor,
kardeş dalında uygulanmıyordu.

    "sapma yüzdesi"  →  `parti` kimliğinde ÇIPLAK "sapma" var        → hits=[parti]
                     →  tek aday, KOŞULSUZ dönülüyor
                     →  parti'de "yuzdesi" açıklanamıyor             → R10, cevap YOK
    oysa `enerji_sapma.sapma_yuzde`'nin sinonimi BİREBİR "sapma yuzdesi"

Sistem **doğru cevabı elinde tutup atıyordu**. Boşluğu `typo_correct` dolduruyordu:
*"sapma yüzdesi → KAR YÜZDESİ mi demek istediniz?"* — başka cube, başka ölçü, kendinden
emin ve yanlış. Planın §2.1'i bunu *"bulanık eşleştirici yanlış düzeltme öneriyor"* diye
kaydetmişti; ölçüm gösterdi ki **öneri bir semptom**, kök neden kimlik asimetrisi.

## Kural

Kısa eşleşme uzun eşleşmenin **alt-dizisiyse** en spesifik kazanır — `_match_cube`'un
çok-aday dalındaki kuralın **aynısı**. Alt-dizi şartı zorunlu: iki AYRI ifade çapraz
cube'dur, kırılmaz. Rakip **tek** olmalı; iki rakip de daha spesifikse bu bir tahmin anı
değil belirsizliktir (ADR-0008).
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


def _cube(schema, ad):
    return next((c for c in schema["cubes"] if c["name"] == ad), None)


# --- ASIL VAKA ------------------------------------------------------------------

@pytest.mark.parametrize("soru", ["sapma yüzdesi", "sapma yuzdesi",
                                  "sapma oranı", "sapma orani"])
def test_SPESIFIK_olcu_kisa_kimligi_YENER(schema, soru):
    """`sapma yüzdesi` katalogda BİREBİR var (`enerji_sapma.sapma_yuzde`). Kısa kimlik
    sinonimi (`parti`→"sapma") onu gölgeleyemez."""
    cr.reddi_sifirla()
    r = cr.route(f"bu yil {soru}", schema)
    assert r is not None, f"{soru!r} cevapsız kaldı (red={cr.red_gerekcesi()})"
    assert r["cube_query"]["cube"] == "enerji_sapma", (
        f"{soru!r} → {r['cube_query']['cube']}; ölçü katalogda enerji_sapma'da")
    assert r["measure"] == "sapma_yuzde"


def test_YANLIS_typo_onerisi_KAYBOLDU(schema):
    """Kök neden kapanınca semptom da kapanır: doğru cevap varken *"kar yüzdesi mi demek
    istediniz"* önerisi üretilmemeli — doğru cevabın üstüne yanlış yönlendirme."""
    _, duzeltmeler = cr.typo_correct(cr._norm("sapma yuzdesi"), schema)
    hedefler = [d.get("to") for d in duzeltmeler]
    assert "kar yuzdesi" not in hedefler, (
        f"hâlâ yanlış cube'un ölçüsüne yönlendiriyor: {duzeltmeler}")


# --- DOKUNULMAMASI GEREKENLER (gerileme kapısı) ---------------------------------

@pytest.mark.parametrize("soru,beklenen_cube,beklenen_olcu", [
    ("sapma", "parti", "ort_renk_sapmasi"),       # daha spesifik rakip YOK → değişmez
    ("kar yüzdesi", "parti", "kar_marji_yuzde"),  # kendi cube'unun ölçüsü → değişmez
    ("karlılık", "parti", "kar_marji_yuzde"),
    ("fire oranı", "parti", "fire_orani_yuzde"),
])
def test_DEGISMEMESI_gerekenler(schema, soru, beklenen_cube, beklenen_olcu):
    cr.reddi_sifirla()
    r = cr.route(f"bu yil {soru}", schema)
    assert r is not None, f"{soru!r} cevapsız kaldı (red={cr.red_gerekcesi()})"
    assert (r["cube_query"]["cube"], r["measure"]) == (beklenen_cube, beklenen_olcu)


def test_KATALOG_DISI_terim_hala_DURUST_reddediliyor(schema):
    """`bütçe sapması` katalogda YOK. Düzeltme "her sapma sorusunu bir yere yolla"
    demek DEĞİLDİR — uydurmak, cevapsız kalmaktan kötüdür."""
    for soru in ("bütçe sapması", "hedef sapması"):
        cr.reddi_sifirla()
        assert cr.route(f"bu yil {soru}", schema) is None, (
            f"{soru!r} katalogda yokken bir cube'a bağlandı — uydurma")


# --- KURALIN KENDİSİ ------------------------------------------------------------

def test_ALT_DIZI_sarti_ZORUNLU(schema):
    """İki AYRI ifade ("verim ve fire oranı") çapraz-cube'dur; alt-dizi değildir, kırılmaz.
    Alt-dizi şartı kalkarsa bu tür sorular sessizce tek cube'a bağlanır."""
    import inspect

    govde = inspect.getsource(cr._daha_spesifik_olcu_sahibi)
    assert "kanit in syn" in govde, "alt-dizi şartı kaldırılmış — çapraz konu kırılır"


def test_TEK_rakip_sarti_ZORUNLU(schema):
    """İki rakip de daha spesifikse bu bir tahmin anı değil BELİRSİZLİKTİR (ADR-0008).
    Sahte katalogla doğrudan ölçülür."""
    kazanan = {"name": "a", "synonyms": ["sapma"],
               "measure_synonyms": {"m_a": ["sapma"]}}
    rakip1 = {"name": "b", "synonyms": [], "measure_synonyms": {"m_b": ["sapma yuzdesi"]}}
    rakip2 = {"name": "c", "synonyms": [], "measure_synonyms": {"m_c": ["sapma yuzdesi"]}}
    q = cr._norm("bu yil sapma yuzdesi")

    tek = cr._daha_spesifik_olcu_sahibi(q, kazanan, {"cubes": [kazanan, rakip1]})
    assert tek is rakip1, "tek rakip devralmalı"

    iki = cr._daha_spesifik_olcu_sahibi(q, kazanan, {"cubes": [kazanan, rakip1, rakip2]})
    assert iki is None, "iki rakipte tahmin edilmemeli — bugünkü davranış korunur"


def test_RAKIP_sinonimi_SORUDA_gecmeli(schema):
    """Rakip yalnız "daha uzun bir sinonimi var" diye kazanamaz — o sinonim kullanıcının
    YAZDIĞI kelimelerde geçmeli (`_syn_hit`). Aksi halde kazanan, soruda hiç geçmeyen
    bir ifade yüzünden devrilirdi."""
    kazanan = {"name": "a", "synonyms": ["sapma"], "measure_synonyms": {"m_a": ["sapma"]}}
    rakip = {"name": "b", "synonyms": [], "measure_synonyms": {"m_b": ["sapma yuzdesi"]}}
    q = cr._norm("bu yil sapma")   # "yuzdesi" YOK
    assert cr._daha_spesifik_olcu_sahibi(q, kazanan, {"cubes": [kazanan, rakip]}) is None


def test_KIMLIK_esi_metin_ve_uzunluk_AYNI_tanimi_kullanir():
    """`_en_uzun_kimlik_esi` ile `_longest_syn_hit` ayrışırsa alt-dizi karşılaştırması
    beraberliği kıran kuralla farklı bir sinonimi ölçer."""
    cube = {"synonyms": ["sapma", "renk sapmasi", "yok bu"]}
    q = cr._norm("bu yil renk sapmasi")
    assert cr._en_uzun_kimlik_esi(q, cube) == "renk sapmasi"
    assert cr._longest_syn_hit(q, cube) == len("renk sapmasi")


# --- UÇTAN UCA ------------------------------------------------------------------

def test_ASK_ZINCIRI_yapisal_cevap_veriyor(client):
    """Uçtan uca: bu soru daha önce Discovery'ye düşüyordu (`cube_query=None`)."""
    d = client.post("/ask", json={"question": "bu yıl sapma yüzdesi",
                                  "session_id": "t"}).json()
    assert d.get("cube_query"), f"yapısal cevap yok — source={d.get('source')}"
    assert d["cube_query"]["cube"] == "enerji_sapma"
