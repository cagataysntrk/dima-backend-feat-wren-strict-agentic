"""FAZ C2 — sayı biçimi ve istatistik çekirdeği TEK kaynaktan.

## Ölçülen sorun

**Aynı sayı iki yüzeyde farklı görünüyordu.** `150.5` sohbette **`150`**, e-postada
**`150,50`**. `interpret._fmt`'in kuralı `abs(n) >= 100` iken ondalığı atıyordu; yani
kullanıcıya gösterilen değeri **sessizce değiştiriyordu** (%0,33 hata). Bir BI ürününde
aynı raporun iki yüzeyde farklı okunması, sayıya duyulan güveni doğrudan aşındırır.

Ayrıca sayısal-mı testi **yedi kopya / üç semantikti** (`"1,5"` → `interpret` evet,
`viz`/`schedules` hayır), ay kısaltmaları **üç yerde**, ve `drill.flag_outliers`
docstring'inde *"`schedules.detect_anomalies` İLE AYNI yöntem … yeni bir istatistik motoru
İCAT EDİLMEZ"* yazmasına rağmen formülü **elle ikinci kez yazmıştı**.

## Seçilen kural

Tam sayı → 0 ondalık; değilse → 2 ondalık. Kesirli kısmı **asla sessizce atmaz**. Büyük
tutarlarda iki hane biraz ayrıntılı görünür ama *"gösterilen sayı gerçek sayıdır"* garantisi
ondan önemlidir.
"""

from __future__ import annotations

import datetime as dt

import pytest

from app import fmt, interpret, schedules, viz
from app.result_shape import is_num
from app.stats import ASGARI_GOZLEM, ortalama_std, z_skorlari

# --- biçim: yüzeyler arası TUTARLILIK -------------------------------------------

@pytest.mark.parametrize("v", [150.5, 12.34, 1234567.0, 0.5, 0, -42.25, 1e7])
def test_sohbet_ve_EPOSTA_ayni_sayiyi_gosterir(v):
    """ASIL KAPI. `150.5` sohbette `150`, e-postada `150,50` görünüyordu."""
    assert interpret._fmt(v) == schedules._fmt_deger(v), (
        f"{v}: sohbet={interpret._fmt(v)!r} e-posta={schedules._fmt_deger(v)!r}")


def test_kesirli_kisim_SESSIZCE_atilmaz():
    """Eski kural `abs(n) >= 100` iken ondalığı atıyordu — gösterilen değer gerçek
    değerden farklı oluyordu."""
    assert fmt.sayi(150.5) == "150,50"
    assert fmt.sayi(1234.56) == "1.234,56"
    assert fmt.sayi(1234.0) == "1.234"


def test_turkce_ayirac():
    assert fmt.sayi(15576000) == "15.576.000"
    assert "e+" not in fmt.sayi(1.5576e7), "bilimsel gösterim sızdı"


def test_para_birimi_ONE_digeri_ARKAYA():
    assert fmt.olcu(1500, "₺") == "₺1.500"
    assert fmt.olcu(12.5, "kg") == "12,50 kg"
    assert fmt.olcu(None) == "—"


@pytest.mark.parametrize("girdi,beklenen", [
    ("2026-04-01", "Nis 2026"),
    (dt.date(2026, 4, 1), "Nis 2026"),
    ("2026-04-15", "15.04.2026"),
    ("Pzt", "Pzt"),
])
def test_zaman_kovasi_etiketi(girdi, beklenen):
    assert fmt.kova(girdi) == beklenen


def test_ay_kisaltmalari_TEK_yerde():
    """Üç ayrı tanım vardı (`interpret._MONTHS_TR`, `schedules._AY_KISA`, `kpi._MONTHS_TR`);
    biri güncellenip diğerleri unutulabilirdi."""
    assert len(fmt.AY_KISA) == 12 and fmt.AY_KISA[0] == "Oca" and fmt.AY_KISA[11] == "Ara"


# --- sayısal test: TEK semantik --------------------------------------------------

@pytest.mark.parametrize("v", ["1,5", "2", 2, 2.5, True, None, "abc", ""])
def test_sayisal_testi_HER_YERDE_ayni(v):
    """`"1,5"` → `interpret` evet, `viz`/`schedules` hayır diyordu. Yüklenen Türkçe CSV'de
    aynı kolon bir motorda ölçü, diğerinde kategoriydi."""
    ref = is_num(v)
    assert interpret._is_num(v) is ref
    assert viz._is_num(v) is ref
    assert schedules._is_sayi(v) is ref


def test_turkce_ondalik_kabul_edilir():
    assert is_num("1,5") and is_num("1.234,56")
    assert not is_num(True), "bool sayı sayılmamalı (Python'da int alt sınıfı)"


# --- istatistik çekirdeği --------------------------------------------------------

def test_z_skoru_aykiriyi_bulur():
    z = z_skorlari([10, 10, 10, 10, 100])
    assert z is not None and len(z) == 1 and z[0][0] == 4


def test_AZ_GOZLEMDE_None_doner():
    """`None` ile `[]` FARKLI: `None` = "bu veride aykırılık sorusu sorulamaz",
    `[]` = "soruldu, yok". Çağıran bu ayrımı kullanıcıya yansıtabilir."""
    assert z_skorlari([1, 2, 3]) is None
    assert z_skorlari([10] * ASGARI_GOZLEM) is None, "sıfır varyansta None dönmeli"
    assert z_skorlari([10, 10, 10, 11]) == []


def test_populasyon_std_kullanilir():
    """Elimizdeki satırlar bir örneklem değil, sorgunun TAMAMI — n'e bölünür (n-1 değil)."""
    _ort, std = ortalama_std([2, 4, 4, 4, 5, 5, 7, 9])
    assert std == pytest.approx(2.0), "örneklem std'sine (n-1) kaymış olabilir"


def test_drill_ve_schedules_AYNI_cekirdegi_kullanir():
    """`drill.flag_outliers` docstring'i "yeni bir istatistik motoru İCAT EDİLMEZ" diyordu
    ama formülü elle ikinci kez yazmıştı."""
    import inspect

    from app.drill import flag_outliers

    assert "stats" in inspect.getsource(flag_outliers), \
        "drill hâlâ kendi z-skorunu hesaplıyor"


def test_drill_ciktisi_BOZULMADI():
    """Devir sonrası davranış birebir aynı kalmalı."""
    from app.drill import flag_outliers

    rows = [{"m": k, "v": v} for k, v in
            (("a", 10), ("b", 10), ("c", 10), ("d", 10), ("e", 100))]
    out = flag_outliers(rows, "m", "v")
    assert len(out) == 1 and out[0]["value"] == "e" and out[0]["direction"] == "above"
