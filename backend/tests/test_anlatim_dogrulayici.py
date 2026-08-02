"""FAZ G4 — anlatım doğrulayıcı: "LLM sayı uydurabilir" bir umut değil bir KAPI olsun.

Ürünün asıl vaadi grafik değil **konuşma**: kullanıcı hesaplanmış bir sonuca bakıp *"bu
neden böyle?"*, *"normal mi?"*, *"ne yapmalıyız?"* diyebilmeli. Bunun için LLM'in
**sayıları görmesi** gerekir — ama sayıları görmek onları **uydurabilmesi** demektir.

Kural: *üretilen metindeki her sayı sonuç kümesinde bulunmalı ya da beyan edilmiş bir
işlemle ondan türetilebilmeli; doğrulanamayan sayı içeren cümle YAYIMLANMAZ.*

`viz.py`'nin *"grafik üretimini LLM'e verme"* disipliniyle (ADR-0024) aynı felsefenin metin
tarafı: **LLM üslubu yazar, SAYIYI sistem koyar.**

Planın istediği asıl sınama burada: **mutasyon testi** — doğru bir cümledeki sayıyı kasten
boz, cümle reddedilsin.
"""

from __future__ import annotations

import pytest

from app import narration_guard as ng

SONUC = {
    "columns": ["makine", "ciro"],
    "rows": [
        {"makine": "M-01", "ciro": 15576000},
        {"makine": "M-02", "ciro": 9800000},
        {"makine": "M-03", "ciro": 4624000},
    ],
    "row_count": 3,
}


# --- ASIL KAPI: mutasyon testi ---------------------------------------------------

def test_MUTASYON_bozulan_sayi_reddedilir():
    """Planın açıkça istediği sınama: sayıyı kasten boz, cümle YAYIMLANMASIN."""
    dogru = "M-01 makinesi 15.576.000 ciro üretti."
    assert ng.dogrula(dogru, SONUC).gecti, "doğru cümle reddedildi — kapı kullanılamaz"

    bozuk = "M-01 makinesi 15.999.000 ciro üretti."
    r = ng.dogrula(bozuk, SONUC)
    assert not r.gecti
    assert r.temiz_metin == "", "uydurma sayı içeren cümle yayımlandı"
    assert 15999000.0 in r.dogrulanamayan_sayilar


def test_tamamen_UYDURMA_cumle_dusurulur():
    r = ng.dogrula("Toplam 42.000.000 TL'lik bir kayıp var.", SONUC)
    assert not r.gecti and r.temiz_metin == ""


# --- CERRAHİ: yalnız kötü cümle düşer -------------------------------------------

def test_yalniz_KOTU_cumle_dusuruluyor():
    """Bir cümlede uydurma varsa diğer doğru cümleleri de atmak kullanıcıya bilgi
    kaybettirir. Kapı cerrahi olmalı ki KULLANILABİLİR kalsın — kullanılamayan kapı
    kapatılır ve o zaman hiç yoktur."""
    metin = ("M-01 makinesi 15.576.000 ciro üretti. Buna karşılık M-02 yalnız 99.999.999 "
             "yaptı. M-03 ise 4.624.000 ile sonuncu.")
    r = ng.dogrula(metin, SONUC)
    assert not r.gecti
    assert "15.576.000" in r.temiz_metin and "4.624.000" in r.temiz_metin
    assert "99.999.999" not in r.temiz_metin
    assert len(r.reddedilen) == 1


def test_SAYISIZ_cumle_gecer():
    """Bu kapı sayı uydurmasını engeller, ÜSLUBU değil."""
    r = ng.dogrula("Üretim genel olarak dengeli görünüyor ve dikkat çeken bir kırılma yok.",
                   SONUC)
    assert r.gecti and r.temiz_metin


# --- TÜRKÇE / İNGİLİZCE biçim -----------------------------------------------------

@pytest.mark.parametrize("yazim", ["15.576.000", "15576000", "15,576,000", "15576000.00"])
def test_AYNI_sayinin_farkli_yazimlari_kabul(yazim):
    """LLM her iki biçimi de üretir; ayrımı yapamayan bir doğrulayıcı DOĞRU cümleleri
    reddeder — kapının en tehlikeli hâli budur, çünkü kapatılır."""
    assert ng.dogrula(f"Ciro {yazim} oldu.", SONUC).gecti, yazim


@pytest.mark.parametrize("metin,beklenen", [
    ("1.234,56", 1234.56),      # TR: nokta binlik, virgül ondalık
    ("1,234.56", 1234.56),      # EN: virgül binlik, nokta ondalık
    ("1234,5", 1234.5),
    ("1.234", 1234.0),          # üçlü gruplama → binlik
    ("1,5", 1.5),               # gruplama değil → ondalık
])
def test_sayi_cozumleme(metin, beklenen):
    assert ng._coz(metin) == pytest.approx(beklenen)


# --- YUVARLAMA meşrudur ----------------------------------------------------------

def test_YUVARLAMA_kabul_edilir():
    """LLM "15.576.000"ı "15,6 milyon" diye yuvarlar; bunu uydurma saymak kapıyı
    kullanılamaz kılardı. Tolerans GÖRECELİdir (%2), mutlak değil."""
    assert ng.dogrula("Ciro yaklaşık 15.580.000 TL.", SONUC).gecti


def test_TOLERANS_disi_reddedilir():
    assert not ng.dogrula("Ciro 16.500.000 TL.", SONUC).gecti


# --- BEYAN EDİLMİŞ türetmeler (liste KAPALI) -------------------------------------

def test_FARK_turetilebilir():
    fark = 15576000 - 9800000
    assert ng.dogrula(f"Aradaki fark {fark:,} TL.".replace(",", "."), SONUC).gecti


def test_TOPLAM_turetilebilir():
    toplam = 15576000 + 9800000 + 4624000
    assert ng.dogrula(f"Toplam {toplam} TL.", SONUC).gecti


def test_PAY_yuzdesi_turetilebilir():
    toplam = 15576000 + 9800000 + 4624000
    pay = 15576000 / toplam * 100
    assert ng.dogrula(f"M-01 toplamın %{pay:.1f}'ini oluşturuyor.", SONUC).gecti


def test_YUZDE_DEGISIM_turetilebilir():
    d = (9800000 - 15576000) / 15576000 * 100
    assert ng.dogrula(f"M-02, M-01'e göre %{d:.1f} geride.", SONUC).gecti


def test_turetme_listesi_KAPALI():
    """"Her aritmetik kombinasyon" serbest olsaydı yeterince sayıyla HER ŞEY türetilebilir
    ve kapı hiçbir şeyi engellemezdi. Çarpım izinli DEĞİLDİR."""
    carpim = 15576000 * 2
    assert not ng.dogrula(f"İki katı {carpim} eder.", SONUC).gecti


# --- YIL ve SIRA sayıları veri iddiası değildir ---------------------------------

@pytest.mark.parametrize("cumle", [
    "2025 yılında üretim arttı.",
    "İlk 3 makine listede.",
    "2026 hedefleri henüz belli değil.",
])
def test_yil_ve_sira_DOGRULANMAZ(cumle):
    """Bunları doğrulamaya çalışmak gerçek uydurmaları GÜRÜLTÜYE boğardı."""
    assert ng.dogrula(cumle, SONUC).gecti, cumle


def test_sayi_cikarma_yil_ve_kucuk_sayilari_ELER():
    assert ng.sayilari_cikar("2025 yılında ilk 5 makine 15.576.000 üretti.") == [15576000.0]


# --- sınır durumlar --------------------------------------------------------------

def test_BOS_metin_gecer():
    assert ng.dogrula("", SONUC).gecti
    assert ng.dogrula(None, SONUC).gecti


def test_SONUC_yoksa_her_sayi_reddedilir():
    """Sonuç kümesi yoksa doğrulanacak bir zemin de yoktur — sayı içeren HİÇBİR cümle
    yayımlanamaz. Fail-closed: kanıtsız sayı, uydurma sayıdır."""
    r = ng.dogrula("Ciro 15.576.000 TL.", None)
    assert not r.gecti and r.temiz_metin == ""
    assert ng.dogrula("Veri bulunamadı.", None).gecti, "sayısız cümle yine geçmeli"


def test_BOOL_deger_sayi_sayilmaz():
    """`True`/`False` Python'da int alt sınıfıdır; izinli değer havuzuna girerse
    `1` ve `0` her metinde doğrulanır hale gelirdi."""
    r = {"columns": ["ok"], "rows": [{"ok": True}], "row_count": 1}
    assert not ng.dogrula("Toplam 1000 adet.", r).gecti


# --- güvenli anlatım: yedek deterministik çıktı ---------------------------------

def test_guvenli_anlatim_YEDEGE_duser():
    """Üretilen metin tamamen düşerse kullanıcı boş ekran değil, daha az süslü ama
    DOĞRU bir cevap görür (deterministik `interpret` çıktısı)."""
    metin, r = ng.guvenli_anlatim("Ciro 99.999.999 TL.", SONUC,
                                  yedek="En yüksek ciro M-01 makinesinde.")
    assert metin == "En yüksek ciro M-01 makinesinde." and not r.gecti


def test_guvenli_anlatim_YEDEK_yoksa_BOS():
    """Sessizce uydurulmuş bir cümle yayımlamaktansa hiçbir şey söylememek yeğdir."""
    metin, r = ng.guvenli_anlatim("Ciro 99.999.999 TL.", SONUC)
    assert metin == "" and not r.gecti


def test_guvenli_anlatim_TEMIZ_kismi_korur():
    metin, _ = ng.guvenli_anlatim("Ciro 15.576.000 TL. Kayıp 99.999.999 TL.", SONUC,
                                  yedek="yedek")
    assert "15.576.000" in metin and "99.999.999" not in metin


# --- makbuz ----------------------------------------------------------------------

def test_makbuza_yazilabilir():
    import json

    r = ng.dogrula("Ciro 99.999.999 TL.", SONUC)
    m = r.makbuza()
    assert m["narration_verified"] is False and m["rejected_sentences"] == 1
    assert json.dumps(m)
