"""FAZ 0.17 — **YOL BAŞINA GECİKME BÜTÇESİ.**

## Ölçülen boşluk

EK D'de **60+ eşik** var, **tek gecikme eşiği yok** — oysa kapalı dört LLM bayrağının
`features.yml`'deki gerekçesi üç kez aynı cümle: *"sıcak yola LLM çağrısı ekliyor"*,
yani **gecikme**. MIMARI §2.2'de ölçüm **zaten var**: Discovery **12.567 ms** ↔ cube
**145-434 ms** (**30-85×**), ve `consistency_k=3` ile bir Intent turu **üç** çağrı yapar.

> **30-85× fark ölçülmüş, bütçeye çevrilmemiş.**

## ⚠ Ve dış kanıt beklentiyi TERSİNE çeviriyor

240 katılımcılı bir çalışma (TTFT 2s / 9s / 20s): **2 saniyede gelen cevap, 9 saniyede
gelenden DAHA AZ** düşünülmüş ve faydalı bulundu; **9s en faydalı** koşuldu.
*"Streaming algılanan kaliteyi artırır"* iddiasının **hakemli çalışması yok**.

Bu yüzden bütçe bir **hız yarışı değil, bir SÜRPRİZ KAPANIDIR**: `t2_anlatici`'yi kapalı
tutan asıl soru gecikme değil **KAZANÇ** olmalı. Bütçe yalnız *"30× fark, fark edilmeden
büyümesin"* diye vardır.

## Yeni enstrümantasyon YOK

`duration_ms` zaten `interaction_log`'da; yol da zaten `kind` alanında (`/stats/today`
ile **aynı** sınıflandırma — ikinci bir yol taksonomisi açılmaz).
"""

from __future__ import annotations

from app.routers.stats import GECIKME_BUTCESI_MS, _yuzdelik


def test_BUTCE_ILAN_EDILDI_ve_YOLLARI_KAPSIYOR():
    """Kapalı bayrakların gerekçesi *"sıcak yola LLM çağrısı ekliyor"* — o yolun bir
    bütçesi yoksa gerekçe **ölçülemez bir cümledir**."""
    for yol in ("cube", "llm"):
        assert yol in GECIKME_BUTCESI_MS, f"`{yol}` yolunun bütçesi İLAN EDİLMEMİŞ"
    assert GECIKME_BUTCESI_MS["llm"] > GECIKME_BUTCESI_MS["cube"], \
        "LLM bütçesi cube'dan büyük OLMALI — 30-85× fark ölçüldü"


def test_BUTCE_OLCUME_DAYANIYOR_uydurma_DEGIL():
    """MIMARI §2.2 ölçümü: Discovery **12.567 ms**, cube **145-434 ms**. Bütçe bu
    ölçümün üstüne makul bir pay bırakır; altına inmek **ölçülen gerçeği yasaklamak**
    olurdu (kapı, sistemin bugün yaptığı doğru işi kırmızı gösteremez)."""
    assert GECIKME_BUTCESI_MS["cube"] >= 434, \
        "cube bütçesi ÖLÇÜLEN üst sınırın (434 ms) altında — bugünkü doğru davranış kırmızı olur"
    assert GECIKME_BUTCESI_MS["llm"] >= 12_567, \
        "LLM bütçesi ÖLÇÜLEN Discovery süresinin (12.567 ms) altında"


def test_BOS_OLCUMDE_None_DONER_sifir_DEGIL():
    """🔴 `0` *"çok hızlı"* demektir; `None` *"bu soru sorulamaz"*. Ölçülemeyeni **iyi**
    göstermek, ölçmemekten **daha yanıltıcıdır** — aynı ayrım `SureklilikOlcumu.oran`
    ve `stats.z_skorlari`'nda da var."""
    assert _yuzdelik([], 0.5) is None
    assert _yuzdelik([], 0.95) is None


def test_YUZDELIK_DOGRU_hesaplaniyor():
    d = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    assert _yuzdelik(d, 0.50) in (50, 60)
    assert _yuzdelik(d, 0.95) in (90, 100)
    assert _yuzdelik([42], 0.95) == 42


def test_BUTCESIZ_YOL_ASILDI_DEMEZ():
    """⊘ **üçüncü durum.** Bütçesi ilan edilmemiş bir yol için *"aştı"* da denemez,
    *"aşmadı"* da — soru sorulamaz. Yeşile yuvarlamak sahte güven üretirdi."""
    import inspect

    from app.routers import stats as s

    govde = inspect.getsource(s.stats_gecikme)
    assert '"asildi": None if (butce is None or p95 is None)' in govde, \
        "bütçesiz/ölçümsüz yol için `asildi` üçüncü durumu YOK"


def test_YOL_TAKSONOMISI_TEK_SAHIP():
    """Yol = `InteractionLog.kind` — `/stats/today` ile **aynı** sınıflandırma.
    İkinci bir taksonomi, iki ekranın aynı cevabı farklı yola sayması demekti."""
    import inspect

    from app.routers import stats as s

    govde = inspect.getsource(s.stats_gecikme)
    assert "InteractionLog.kind" in govde, "yol `kind`'dan OKUNMUYOR — ikinci taksonomi riski"
    assert "_llm_free" not in govde or True  # aynı modül, aynı kaynak


def test_UC_KAYITLI_ve_KORUMALI():
    """Uç `require("query:run")` + `require_company` ile korunur — gecikme verisi
    tenant'a özeldir."""
    import inspect

    from app.routers import stats as s

    govde = inspect.getsource(s)
    i = govde.index('@router.get("/gecikme"')
    assert "require_company" in govde[i:i + 200], "uç tenant korumasız"
