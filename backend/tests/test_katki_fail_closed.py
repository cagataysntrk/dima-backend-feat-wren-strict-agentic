"""🔴 KATKI KAPISI ARTIK FAIL-CLOSED — ve kapatan şey bir ÖLÇÜMDÜ.

`ayristirilabilir_mi` `BILINMIYOR` sınıfında **fail-OPEN**ti: docstring *«emin
olunamayan durumda ayrıştırma yapılmaz»* diyor, kod ayrıştırıyordu. Yorumun kendi şartı
*«davranış değişikliği kendi ölçümünü ister»*di — ölçüm yapıldı (2026-08-11):

    canlı katalog (demo-boyahane) → TAM 74 · YOK 60 · YARI 2 · **BİLİNMİYOR 0**

⊙ Fail-open dalı **pratikte hiç ulaşılmıyordu**; kapatmanın kapsam maliyeti **sıfır**,
kapatmamanın bedeli ise bir gün beyansız bir pack geldiğinde **sessizce yayımlanan** bir
katkı yüzdesi.

⚠ Ölçüm kolay yanılttı: ilk prob `measure_expressions`'ı geçmedi ve 77 ölçü *«bilinmiyor»*
göründü. `toplanabilirlik` sınıfı oradan okur — küpün **kendisi** meta olarak verilmelidir.
"""

from app.contribution import BILINMIYOR, ayristirilabilir_mi, toplanabilirlik


def test_BEYANSIZ_olcude_ayristirma_YAPILMAZ():
    """🔴 Kusurun ta kendisi: beyansız bir ölçüde katkı payı yayımlanıyordu."""
    ok, gerekce = ayristirilabilir_mi("gizemli_olcu", {})
    assert ok is False
    assert "beyan" in gerekce.lower()
    # Gerekçe EYLEME ÇEVRİLEBİLİR: ne yazılacağını söyler
    assert "measure_expressions" in gerekce


def test_TAM_olcude_ayristirma_YAPILIR():
    meta = {"measure_expressions": {"toplam_ciro": "SUM(ciro_tl)"}}
    assert ayristirilabilir_mi("toplam_ciro", meta)[0] is True


def test_ORAN_olcusu_zaten_reddediliyordu():
    meta = {"measure_expressions": {"ort_oee": "AVG(oee)"}}
    ok, gerekce = ayristirilabilir_mi("ort_oee", meta)
    assert ok is False and "ortalama" in gerekce


def test_YARI_toplanabilir_stok_reddediliyor():
    meta = {"semi_additive": ["bakiye"]}
    ok, gerekce = ayristirilabilir_mi("bakiye", meta)
    assert ok is False and "stok" in gerekce


def test_sinif_okuyucusu_TEK_KAYNAK():
    """`KAT-1` — sınıf yalnız `toplanabilirlik`'ten gelir; ikinci bir tablo yok."""
    assert toplanabilirlik("gizemli", {})[0] == BILINMIYOR
    assert toplanabilirlik("", {})[0] != BILINMIYOR      # ölçüsüz → YOK
