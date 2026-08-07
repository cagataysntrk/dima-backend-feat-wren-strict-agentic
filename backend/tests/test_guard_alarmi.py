"""🔴 `Ö5` — **GUARD DÜŞME ORANI**: kapı sessizce her şeyi düşürürse görülür.

## Kapının kendi sözü tutulmamıştı

`app/iddia.py`: *"Düşme oranı **ölçülür** — kapı agresifse gevşetilir, ama **ölçüyle**,
sezgiyle değil."* Söz yazıldı, ölçüm kurulmadı (`grep dusme_orani|drop_rate` → **0**).

## Korunan risk — *sessiz soğuma*

Model sürümü ya da prompt biçimi değişirse guard'lar **tüm** anlatıyı düşürmeye
başlayabilir: kullanıcı **yanlış sayı görmez** (güvenlik sağlam), sistem sürekli
*"soğuk"* cevap verir, ve **hiçbir şey hata vermez**.

*Bir kapının sessizce her şeyi düşürmesi, hiç olmamasından farksızdır — tek fark,
sistemin kendini güvende sanmasıdır.*
"""

from __future__ import annotations

import pathlib

import pytest

from app import guard_alarmi


@pytest.fixture(autouse=True)
def _temiz():
    guard_alarmi.sifirla()
    yield
    guard_alarmi.sifirla()


# --- ORAN ---------------------------------------------------------------------------


def test_ORAN_dusen_bolu_TOPLAM():
    """Oran cevap başına değil **cümle başına**: iki cümlelik bir anlatıda 1 düşmek ile
    yirmi cümlelikte 1 düşmek aynı sayıdır, aynı şey değildir."""
    guard_alarmi.kaydet(1, 2)
    guard_alarmi.kaydet(0, 8)
    d = guard_alarmi.durum()
    assert d["dusen_cumle"] == 1 and d["toplam_cumle"] == 10
    assert d["oran"] == 0.1


def test_ANLATISIZ_CEVAP_PAYDAYA_GIRMEZ():
    """🔴 `toplam == 0` (anlatı hiç üretilmedi) pencereye **girmez**: anlatısız bir cevap,
    düşmüş bir anlatı değildir. *Paydaya girmeyen bir vaka, oranı bozmaz.*"""
    for _ in range(20):
        guard_alarmi.kaydet(0, 0)
    assert guard_alarmi.durum()["ornek"] == 0


def test_HAM_SAYILAR_da_DONER():
    """⚠ Eşik **ölçülmemiş bir tahmindir**; onu düzeltecek kişi **paydayı** görmeden
    karar veremez. *Bir eşiği ölçmeden koymak, onu ölçmenin önüne geçmektir.*"""
    guard_alarmi.kaydet(3, 5)
    d = guard_alarmi.durum()
    for alan in ("dusen_cumle", "toplam_cumle", "ornek", "pencere", "esik", "kapsam"):
        assert alan in d, f"`{alan}` yok — eşik ölçümle düzeltilemez"
    assert d["kapsam"] == "surec-ici", "kapsam yazılı olmalı, yoksa yanlış okunur"


# --- ALARM ------------------------------------------------------------------------


def test_PENCERE_DOLMADAN_ALARM_YOK():
    """🔴 Üç cevaplık örneklemde %100 bir sinyal değil **gürültüdür**.
    *Az veriyle verilen bir alarm, alarmın kendisine olan güveni harcar.*"""
    for _ in range(3):
        guard_alarmi.kaydet(5, 5)
    assert guard_alarmi.durum()["alarm"] is False


def test_PENCERE_DOLUNCA_ESIK_ASILIRSA_ALARM():
    for _ in range(guard_alarmi.PENCERE):
        guard_alarmi.kaydet(4, 5)          # %80 düşme
    d = guard_alarmi.durum()
    assert d["ornek"] == guard_alarmi.PENCERE
    assert d["alarm"] is True, f"eşik aşıldı ama alarm yok: {d}"


def test_SAGLIKLI_AKISTA_ALARM_YOK():
    for _ in range(guard_alarmi.PENCERE):
        guard_alarmi.kaydet(0, 5)
    assert guard_alarmi.durum()["alarm"] is False


def test_PENCERE_KAYAR_ve_ALARM_DUSER():
    """Alarm **yapışkan değildir**: durum düzelirse iner. Yapışkan bir alarm, düzelmeyi
    görünmez yapar."""
    for _ in range(guard_alarmi.PENCERE):
        guard_alarmi.kaydet(5, 5)
    assert guard_alarmi.durum()["alarm"] is True
    for _ in range(guard_alarmi.PENCERE):
        guard_alarmi.kaydet(0, 5)
    assert guard_alarmi.durum()["alarm"] is False


# --- BAĞLANTI — yetim değil ---------------------------------------------------------


def test_PAYDA_BOLMEYI_YAPAN_YERDE_URETILIYOR():
    """🔴 Çağıranın metni **yeniden bölmesi**, `_CUMLE_RE`'nin ikinci bir sahibi demekti —
    bu deponun bir numaralı kusur sınıfı. *Bir sayıyı, onu zaten bilen yerden iste.*"""
    from app.iddia import Rapor as IRapor
    from app.narration_guard import Rapor as NRapor

    assert "toplam_cumle" in NRapor.__dataclass_fields__
    assert "toplam_cumle" in IRapor.__dataclass_fields__

    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/answer.py").read_text(encoding="utf-8")
    assert "_CUMLE_RE" not in kaynak, (
        "🔴 `answer.py` cümleyi kendisi bölüyor — payda ikinci kez hesaplanıyor")


def test_URETIM_YOLUNDA_CAGRILIYOR():
    """Yetim yasağı: ölçüm kurulduysa **beslenmeli**."""
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/answer.py").read_text(encoding="utf-8")
    assert "guard_alarmi" in kaynak and "_alarm.kaydet(" in kaynak, (
        "🔴 alarm modülü var ama üretimde beslenmiyor — ölçüm hiç dolmaz")


def test_SAGLIK_YUZEYINDE_GORUNUYOR_ve_STATUSU_ETKILEMIYOR():
    """⚠ Anlatının soğuması bir **kesinti değildir**; sistem doğru cevap vermeye devam
    eder. Alarmı `status`'e bağlamak, bir üslup sorununu bir kullanılabilirlik sorunu
    gibi raporlardı. *Bir sinyali yanlış şiddette çalmak, onu susturmanın bir başka
    yoludur.*"""
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/routers/health.py").read_text(encoding="utf-8")
    assert 'body["guard"]' in kaynak, "🔴 düşme oranı sağlık yüzeyinde YOK — yetim ölçüm"
    i = kaynak.index('body["guard"]')
    assert 'ok = mdl_ready and db_ready' in kaynak[:i], "çapa kaymış"
    assert "guard" not in kaynak[kaynak.index("ok = mdl_ready"):i].split("body = {")[0], (
        "🔴 alarm `status` hesabına karışıyor — soğuk anlatı bir kesinti değildir")
