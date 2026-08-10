"""🔴🔴 `§ÜK` — **«HANGİSİ» SORUSUNA «NE KADAR» CEVABI.**

## Ölçülen kusur (curl turu, 2026-08-10)

    «bu yıl en yüksek enerji tüketimi» → {elektrik_tuketimi_kwh: 5.500.126}
    cq: order desc · dimensions: YOK · beyan: YOK

Kullanıcı **hangisi** diye sordu, sistem **ne kadar** diye cevapladı. `order desc` tek
satırlık bir toplamın üstünde çalıştı — bir **yok-işlem**, ama cevapta sıralanmış bir
sonuç gibi duruyor.

🔴 Var olan `ustunluk` beyanı bunu **göremiyordu**: o yalnız *«sıralama hiç yapılamadı»*
durumunu sayıyor. Burada sıralama **yapıldı** — anlamsız bir yerde.

⚠ Ve davranış **tutarsızdı**: aynı turda *«bu yıl en iyi kâr marjı»* → *«Hangi kırılımı
istiyorsun?»* diye **sordu** (garson kırılımda uyuşamadı). Aynı şekildeki soru bir yolda
soruluyor, ötekinde sessizce toplamla cevaplanıyordu.

*Bir üstünlük sorusu bir SEÇİM ister; seçilecek bir küme yoksa cevap bir sayı değil, bir
yanlış anlamadır.*
"""

from app import uyum

_META = {"name": "enerji_tesis", "measures": ["elektrik_tuketimi_kwh"],
         "dimensions": ["tesis"], "time_dimensions": ["tarih"],
         "measure_synonyms": {"elektrik_tuketimi_kwh": ["elektrik tuketimi", "enerji tuketimi"]},
         "dimension_synonyms": {"tesis": ["tesis"]}}
_SEMA = {"cubes": [_META]}


def _isaretler(soru, cq):
    return {i.isaret for i in uyum.denetle(soru, {"cube_query": cq}, _META, _SEMA)}


def test_KIRILIMSIZ_USTUNLUK_BEYAN_EDILIR():
    """🔴 Kusurun kendisi: sıralama var, kırılım yok → **beyan** zorunlu."""
    cq = {"cube": "enerji_tesis", "measures": ["elektrik_tuketimi_kwh"],
          "order": {"measure": "elektrik_tuketimi_kwh", "direction": "desc"}}
    assert "ustunluk_kirilimsiz" in _isaretler("bu yil en yuksek enerji tuketimi", cq)


def test_BOYUT_VARSA_BEYAN_YOK():
    """⚠ `dimensions` varsa sıralanacak bir küme **vardır** — beyan yazılmaz."""
    cq = {"cube": "enerji_tesis", "measures": ["elektrik_tuketimi_kwh"],
          "dimensions": ["tesis"],
          "order": {"measure": "elektrik_tuketimi_kwh", "direction": "desc"}}
    assert "ustunluk_kirilimsiz" not in _isaretler("bu yil en yuksek enerji tuketimi", cq)


def test_ZAMAN_KIRILIMI_DA_BIR_KIRILIMDIR():
    """🔴🔴 **Yanlış-pozitif kapısı** (`§101.1`): *«en yüksek aylık tüketim»* ay ay
    sıralanır — `timeDimensions` de bir kırılımdır ve beyan **yazılmamalıdır**."""
    cq = {"cube": "enerji_tesis", "measures": ["elektrik_tuketimi_kwh"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
          "order": {"measure": "elektrik_tuketimi_kwh", "direction": "desc"}}
    assert "ustunluk_kirilimsiz" not in _isaretler("bu yil en yuksek aylik enerji tuketimi", cq)


def test_USTUNLUK_ISTENMEDIYSE_BEYAN_YOK():
    """Düz bir toplam sorusu sıralama istemez — kapı ona hiç dokunmaz."""
    cq = {"cube": "enerji_tesis", "measures": ["elektrik_tuketimi_kwh"]}
    assert "ustunluk_kirilimsiz" not in _isaretler("bu yil toplam enerji tuketimi", cq)
