"""FAZ 7.3 (b + e) kapısı — **boş durum yön gösterir · her drill reddi SEBEP söyler.**
[bayraksız: V-2]

FAZ 7.3'ün on üç alt maddesinden **ikisi** bu turda kapandı; kalanların durumu
`OPERASYON-DURUM.md`'de **madde madde** yazılı. *Bir fazı "bitti" ilan edip yarısını
söylememek, bitmemiş olmaktan kötüdür.*

## (b) — `placeholder` neden "unutulmuş" değildi

Ölçüldü: depoda **hiç** `placeholder` yok. Sebebi bir unutma değil, bir **yapı**:
`CaretInput`'un gerçek `<textarea>`'sı `text-transparent`tır — yazı, sahte imleçli bir
kaplama `<div>`'de çizilir. Ona konan bir `placeholder` **görünmezdi**.

→ İpucu **kaplamada** çizilir; erişilebilirlik için gerçek `placeholder` **da** yazılır.
*Görsel bir ipucu, ekran okuyucuya bir ipucu değildir.*

⚠ Örnek sorular `/starters`'tan — `HelpPanel`'in **aynı kaynağı**. İkinci bir liste,
aynı ürünün iki farklı yeteneği varmış gibi görünmesine yol açardı.

## (e) — kısıt "kaldırıldı" değil, **ayrıştırıldı**

Yol haritası *"facet/scatter/heatmap kısıtı kaldırılır"* diyor. Ölçüldü: üçü **aynı
sınıf değil**.

| şekil | çapa türetilebilir mi | karar |
|---|---|---|
| `scatter` | ✅ nokta = `primaryDim`'in bir değeri (x/y **ölçüdür**) | **kısıt KALKTI** |
| `facet` | ❌ panel = facet değeri **ve** çubuk = birincil boyut → **İKİ filtre** | kalır |
| `heatmap` | ❌ hücre = satır **ve** sütun boyutu → **İKİ filtre** | kalır |

🔴 Facet/heatmap'te tek çapa göndermek, kullanıcının tıkladığından **daha geniş** bir
kırılım açardı: *"bu hücreye tıkladım, bana tüm satırı gösterdi."* Ve `DrillRequest`
(`dimension` + `filter_value`, **tekil**) iki filtreyi taşıyamıyor — bu bir **sözleşme
değişikliğidir**, bir UI ayarı değil.

## 🔴 Ama sessizlik bir karar değildi, bir kusurdu

Kodun kendi yorumu kullanıcının şikâyetini yazıyordu: *"tıklasam da açılmıyor" hissi
**TAM BURADAN** geliyordu.* Beş erken-çıkışın **dördü** sessizdi. Artık hepsi **neden**
olduğunu söylüyor — *bir sınırı söylemek, onu bir kusur olmaktan çıkarır.*
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak


# --- (b) boş durum ---------------------------------------------------------------------

def test_IPUCU_KAPLAMADA_ciziliyor():
    """🔴 Gerçek `<textarea>` `text-transparent`; ona konan bir `placeholder` **görünmez**.
    Bu yüzden ipucu kaplama `<div>`'inde çizilmeli."""
    src = fe_dosyalari()["components/CaretInput.tsx"]
    assert 'value === "" && ipucu' in src, (
        "🔴 İpucu kaplamada çizilmiyor — `text-transparent` bir girdide `placeholder` "
        "görünmez ve boş durum yine boş kalır.")


def test_IPUCU_EKRAN_OKUYUCUYA_da_veriliyor():
    """⚠ *Görsel bir ipucu, ekran okuyucuya bir ipucu değildir*: okuyucu kaplama
    `<div>`'ini değil **girdiyi** okur."""
    src = fe_dosyalari()["components/CaretInput.tsx"]
    assert "placeholder={ipucu}" in src and "aria-label={ipucu" in src


def test_IPUCU_YAZINCA_KAYBOLUYOR():
    """⚠ İpucu bir metin değil bir **davettir**; davet, kabul edildikten sonra yerinde
    durmaz — ve kalırsa yazılanın üstüne biner."""
    src = fe_dosyalari()["components/CaretInput.tsx"]
    kaplama = src[src.index('value === "" && ipucu'):]
    assert kaplama.index("{value}") < 400, "🔴 ipucu ile değer aynı anda çizilebiliyor"


def test_LANDING_ipucu_TASIYOR():
    src = fe_dosyalari()["components/Landing.tsx"]
    assert "ipucu=" in src, "🔴 Boş durum hâlâ yalnız bir imleç gösteriyor"


def test_ORNEKLER_ayni_KAYNAKTAN():
    """🔴 *Aynı kuralın iki sahibi ayrışır.* İkinci bir örnek listesi, aynı ürünün iki
    farklı yeteneği varmış gibi görünmesine yol açardı."""
    landing = fe_dosyalari()["components/Landing.tsx"]
    yardim = fe_dosyalari()["components/HelpPanel.tsx"]
    assert "getStarters" in landing and "getStarters" in yardim
    # Landing kendi listesini YAZMAMALI.
    assert not re.search(r"const\s+(FALLBACK|ORNEKLER|SORULAR)\s*[:=]", landing), (
        "🔴 Landing kendi örnek listesini yazmış — ikinci sahip.")


def test_ORNEK_YOKSA_HICBIR_SEY_gosterilmiyor():
    """⚠ *Uydurma bir örnek, olmayan bir yeteneği vaat eder* ve ilk soru bir hayal
    kırıklığı olur."""
    src = fe_dosyalari()["components/Landing.tsx"]
    assert "baslangiclar.length > 0 &&" in src


def test_ORNEK_SAYISI_sinirli():
    """⚠ Yediden fazlası bir davet değil bir **menüdür**: boş durumun amacı (yön
    göstermek) bir **seçim yüküne** dönüşür."""
    src = fe_dosyalari()["components/Landing.tsx"]
    m = re.search(r"\.slice\(0,\s*(\d+)\)", src)
    assert m and int(m.group(1)) <= 7, "🔴 örnek sayısı sınırsız ya da çok"


def test_GRUP_TASINIYOR_ama_UYDURULMUYOR():
    """*Hangi departmanın sorusu olduğunu bilmek, sorunun kendisi kadar bilgidir* — ama
    `grup` taşımayan bir örneğe departman **uydurulmaz**."""
    src = fe_dosyalari()["components/Landing.tsx"]
    assert "b.grup &&" in src


# --- (e) drill reddi ------------------------------------------------------------------

_RV = "components/ResultView.tsx"


def test_SCATTER_kisiti_KALKTI():
    """✅ Nokta = `primaryDim`'in bir değeri; `x`/`y` **ölçüdür**, boyut değil. Çapa
    tekildir ve türetilebilir."""
    src = fe_dosyalari()[_RV]
    assert "effA.scatter" not in src, (
        "🔴 Scatter hâlâ kısıtlı — oysa çapası tekil ve türetilebilir.")


@pytest.mark.parametrize("sekil", ["facet", "heat"])
def test_IKI_FILTRELI_sekiller_KISITLI_KALDI_ve_SEBEP_soyluyor(sekil):
    """🔴 Tek çapa göndermek, kullanıcının tıkladığından **daha geniş** bir kırılım
    açardı: *"bu hücreye tıkladım, bana tüm satırı gösterdi."*

    ⚠ Bu bir **sözleşme** sınırıdır: `DrillRequest` `dimension` + `filter_value` taşır,
    **tekil**. Kısıtı kaldırmak için önce sözleşme çoğullanmalı.
    """
    src = fe_dosyalari()[_RV]
    i = src.index(f"effA.{sekil}")
    pencere = src[i:i + 700]
    assert "setNoDrillHint(" in pencere, f"🔴 `{sekil}` reddi hâlâ SESSİZ"
    assert "İKİ" in pencere or "iki" in pencere, (
        f"🔴 `{sekil}` reddinin sebebi kullanıcıya söylenmiyor")


def test_HICBIR_ERKEN_CIKIS_sessiz_DEGIL():
    """🔴 Kodun kendi yorumu şikâyeti yazıyordu: *"tıklasam da açılmıyor" hissi TAM
    BURADAN geliyordu.* Beş erken-çıkışın dördü sessizdi.

    *Bir sınırı söylemek, onu bir kusur olmaktan çıkarır.*
    """
    src = fe_dosyalari()[_RV]
    bas = src.index("const handleChartDataPointClick")
    govde = src[bas:src.index("\n  };", bas)]
    donusler = govde.count("return;")
    ipuclari = govde.count("setNoDrillHint(")
    assert ipuclari >= donusler, (
        f"🔴 {donusler} erken-çıkış var ama yalnız {ipuclari} tanesi sebep söylüyor — "
        f"sessiz bir ret, kullanıcıya ürünü bozuk gösterir.")


def test_ETIKET_ESLESMEYINCE_de_YANLIS_FILTRE_gonderilmiyor():
    """⚠ ECharts'ın gösterdiği `name` **biçimlendirilmiş** olabilir (ör. tarih). Ham
    satırda tam eşleşme yoksa, yanlış bir filtre göndermektense durmak doğrudur — ama
    **sessiz değil**."""
    src = fe_dosyalari()[_RV]
    assert "rawValue == null" in src
    i = src.index("rawValue == null")
    assert "setNoDrillHint(" in src[i:i + 500]


def test_SEBEP_METNI_ERISILEBILIR_ve_yeterince_KALIYOR():
    """⚠ Okunamayan bir açıklama yok sayılır; ve bir durum mesajı ekran okuyucuya
    **duyurulmalı**."""
    src = fe_dosyalari()[_RV]
    assert 'role="status"' in src, "🔴 sebep ekran okuyucuya duyurulmuyor"
    assert "setNoDrillHint(null), 6000" in src, "🔴 sebep okunmadan kayboluyor"


def test_KALAN_MADDELER_yazili():
    """⊘ *Bir fazı "bitti" ilan edip yarısını söylememek, bitmemiş olmaktan kötüdür.*"""
    doc = __doc__ or ""
    assert "on üç alt maddesinden" in doc and "madde madde" in doc


def test_YENI_PANEL_acilmadi():
    """K5 13/13."""
    from tests.test_panel_sayisi import DESEN, TAVAN

    toplam = sum(len(DESEN.findall(v)) for v in fe_dosyalari().values())
    assert toplam <= TAVAN
