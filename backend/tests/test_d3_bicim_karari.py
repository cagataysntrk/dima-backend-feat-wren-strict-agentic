"""§D3 — CEVAP BİÇİMİ KARARI. Öneri şeridinin kova kotaları soru türünden gelir.

Ölçüldü (raporun §18'inin sekiz sorusu, curl, 2026-08-11): chip dizisi
`6,6,6,6,5,6,6,5` — soru ne olursa olsun aynı boyda şerit (§18.1: *«katalog hissinin
birinci kaynağı»*). Ve asıl kusur sayı değil **alâkasız kova**: bir «ciro» sorusuna
`+ fire` önerilmesi.

Bu kapı üç şeyi kilitler: ① karar tablosunun anlamı ② çok-türlü sorularda indirgeme
③ 🔴 `KURAL B` — kota verilmezse çıktı **bayt bayt** eski.
"""

from app.bicim import (
    KOVA_KIRILIM,
    KOVA_KIYAS,
    KOVA_OLCU,
    KOVA_TOPN,
    KOVA_ZAMAN,
    KOVALAR,
    VARSAYILAN_KOTA,
    oneri_kotasi,
)
from app.cube_router import suggest_next_steps
from app.niyet import (
    TUR_KIRILIM,
    TUR_KIYAS,
    TUR_LISTE,
    TUR_TOPLAM,
    TUR_TREND,
    TUR_USTUNLUK,
)

_INDEX = {
    "parti": {
        "name": "parti",
        "measures": ["toplam_ciro", "toplam_adet", "ort_fiyat"],
        "dimensions": ["sehir", "musteri_adi"],
        "time_dimensions": ["tarih"],
        "dimension_labels": {"sehir": "şehir", "musteri_adi": "müşteri"},
        "measure_synonyms_display": {"toplam_ciro": "ciro", "toplam_adet": "adet",
                                     "ort_fiyat": "ortalama fiyat"},
    }
}


# ── ① karar tablosunun ANLAMI ────────────────────────────────────────────────

def test_tek_sayi_sorusunda_olcu_kovasi_kapanir():
    """*«bu yıl toplam ciro»* → `+ fire` teklif etmek soruyu DEĞİŞTİRİR.

    Ölçülen kusurun ta kendisi: canlıda o soruya `+ ortalama hız` ve `+ fire`
    chip'leri basılıyordu.
    """
    kota, gerekce = oneri_kotasi({TUR_TOPLAM})
    assert kota[KOVA_OLCU] == 0, "tek sayı istendi — başka ölçü önermek konu değiştirir"
    assert kota[KOVA_TOPN] == 0, "tek satırda sıralanacak bir şey yok"
    # derinleştiren kovalar AÇIK kalır — kural daraltıcıdır, kısırlaştırıcı değil
    assert kota[KOVA_KIRILIM] > 0 and kota[KOVA_ZAMAN] > 0 and kota[KOVA_KIYAS] > 0
    assert "+ölçü" in gerekce and "top-N" in gerekce


def test_kirilim_sorusu_bugunku_davranisi_korur():
    """En zengin dal: bir dağılımın üstünde beş kovanın beşi de anlamlı."""
    kota, _ = oneri_kotasi({TUR_KIRILIM})
    assert kota == VARSAYILAN_KOTA


def test_sıralama_ve_kiyas_kurulmussa_kendi_kovasi_kapanir():
    """Kullanıcının az önce yaptığı şeyi tekrar teklif etmek bir öneri değildir."""
    assert oneri_kotasi({TUR_USTUNLUK})[0][KOVA_TOPN] == 0
    assert oneri_kotasi({TUR_KIYAS})[0][KOVA_KIYAS] == 0
    # trend bir zaman serisidir; sıralama ekseni yoktur
    assert oneri_kotasi({TUR_TREND})[0][KOVA_TOPN] == 0
    # döküm: hepsi anlamlı
    assert oneri_kotasi({TUR_LISTE})[0] == VARSAYILAN_KOTA


# ── ② çok-türlü soruda indirgeme ─────────────────────────────────────────────

def test_cok_turlu_soruda_kova_basina_en_kucuk_alinir():
    """*«en kötü 3 makineyi analiz et»* → `kirilim+ustunluk`.

    Sıralama **kurulmuştur**, dolayısıyla top-N teklifi yine tekrardır — bir soru iki
    türü birden taşıyorsa iki karşılanma da geçerlidir.
    """
    kota, _ = oneri_kotasi({TUR_KIRILIM, TUR_USTUNLUK})
    assert kota[KOVA_TOPN] == 0
    assert kota[KOVA_KIRILIM] == 1     # min(2, 1)
    # *«geçen yıla göre nasıl gidiyoruz»* → kirilim+kiyas+trend
    kota2, _ = oneri_kotasi({TUR_KIRILIM, TUR_KIYAS, TUR_TREND})
    assert kota2[KOVA_KIYAS] == 0 and kota2[KOVA_TOPN] == 0


def test_tablo_disi_tur_yok_sayilir_hepsi_disariysa_none():
    assert oneri_kotasi({"boyle_bir_tur_yok"}) is None
    assert oneri_kotasi(set()) is None
    assert oneri_kotasi(None) is None
    # tanınan bir tür varsa tanınmayan YOK SAYILIR (kapı, sessiz düşüş değil)
    assert oneri_kotasi({TUR_TOPLAM, "boyle_bir_tur_yok"})[0][KOVA_OLCU] == 0


# ── ③ 🔴 KURAL B — kota verilmezse davranış BAYT BAYT eski ────────────────────

def test_kural_b_kota_verilmeden_cikti_degismez():
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": []}
    assert suggest_next_steps(cq, _INDEX) == suggest_next_steps(cq, _INDEX, None)
    # ve varsayılan kota, eski sabit dilimlerin ta kendisidir
    assert suggest_next_steps(cq, _INDEX) == suggest_next_steps(cq, _INDEX, VARSAYILAN_KOTA)


def test_toplam_kotasi_olcu_chiplerini_gercekten_dusurur():
    """Karar tablosunun canlı yoldaki karşılığı — ölçülen kusurun kapanması."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": []}
    eski = [s["label"] for s in suggest_next_steps(cq, _INDEX)]
    assert "+ adet" in eski and "+ ortalama fiyat" in eski      # bugünkü kusur
    kota, _ = oneri_kotasi({TUR_TOPLAM})
    yeni = [s["label"] for s in suggest_next_steps(cq, _INDEX, kota)]
    assert not [s for s in yeni if s.startswith("+ ")], "ölçü kovası kapanmalıydı"
    assert "şehir kırılımı" in yeni and "Aylık trend" in yeni   # derinleşme KORUNUR
    assert len(yeni) < len(eski)


def test_karar_semali_okumadan_verilir():
    """🔴 Biçim kararı **şemalı** niyetten gelir — `coz_soru` (şemasız) YETMEZ.

    Ölçüldü (curl, 2026-08-11): şemasız okumada *«hangi müşteri riskli»* — 8 satırlık
    bir **kırılım** — `tür=toplam` görünüp tek-sayı kotası alıyordu. `kirilim` ve
    `ustunluk` türleri **katalog eşleşmesiyle** doğar; sorunun salt dilinden değil.
    ⊙ Kusuru makbuz yakaladı: `niyet:` izi ile `§D3` izi ayrışıyordu.
    """
    import ast
    import inspect

    from app.answer import _bicim_kotasi

    govde = ast.parse(inspect.getsource(_bicim_kotasi).strip()).body[0]
    if (govde.body and isinstance(govde.body[0], ast.Expr)
            and isinstance(govde.body[0].value, ast.Constant)):
        govde.body = govde.body[1:]          # docstring `coz_soru`'yu ANLATIR, çağırmaz
    kaynak = ast.unparse(govde)
    assert "coz_soru" not in kaynak, "şemasız okuma kırılım/üstünlük türlerini KAÇIRIR"
    assert "coz" in kaynak


def test_kova_adlari_tek_kaynakta():
    """`KAT-1` — kova adları `bicim.py`'de tanımlı; `cube_router` onları İTHAL eder.

    İkinci bir liste yazılsaydı biri bayatlar ve kota sessizce yanlış kovaya
    uygulanırdı (bu deponun bir numaralı kusur sınıfı).
    """
    assert set(VARSAYILAN_KOTA) == set(KOVALAR)
    assert KOVALAR == (KOVA_KIRILIM, KOVA_OLCU, KOVA_ZAMAN, KOVA_KIYAS, KOVA_TOPN)
