"""Deterministik istatistik çekirdeği — **tek kaynak** (Faz C2).

`app/drill.py::flag_outliers`'ın docstring'i şöyle diyordu:

> *"`app/schedules.py::detect_anomalies` İLE AYNI istatistiksel yöntemi kullanır …
> yeni bir istatistik motoru İCAT EDİLMEZ"*

…ama **çağırmıyordu**: aynı formül (ortalama, popülasyon std, z-skoru, `n<4` ve `std==0`
kapıları) elle ikinci kez yazılmıştı. Niyet doğruydu, uygulama niyeti tanımıyordu.
`app/interpret.py` ise gerçekten çağırıyordu — yani üç tüketiciden ikisi paylaşıyor, biri
kopyalıyordu.

Bu modül o çekirdeği ortaya alır. Çıktı **şekilleri** tüketiciye özgü kalır (drill bir
`{value, amount, direction, z}` listesi, schedules bir etiket listesi ister) — paylaşılan
şey **sayısal karardır**, sunum değil.
"""

from __future__ import annotations

from collections.abc import Iterable

# Aykırılık eşiği: |z| ≥ 2 → dağılımın ~%5'i. Anlamlı ama gürültüye boğmayan bir sınır.
VARSAYILAN_K = 2.0

# En az bu kadar gözlem olmadan std anlamsızdır (3 noktada her şey "aykırı" görünür).
ASGARI_GOZLEM = 4


def z_skorlari(degerler: Iterable[float], *, k: float = VARSAYILAN_K,
               asgari: int = ASGARI_GOZLEM) -> list[tuple[int, float]] | None:
    """`[(indeks, z), …]` — **yalnız `|z| ≥ k` olanlar**. Kapılara takılırsa `None`.

    `None` ile boş liste FARKLIDIR: `None` = *"bu veri üzerinde aykırılık sorusu
    sorulamaz"* (çok az gözlem ya da sıfır varyans), `[]` = *"soruldu, aykırılık yok"*.
    Çağıranlar bu ayrımı kullanıcıya yansıtabilir.
    """
    vals = [float(v) for v in degerler]
    if len(vals) < asgari:
        return None
    ort = sum(vals) / len(vals)
    std = (sum((v - ort) ** 2 for v in vals) / len(vals)) ** 0.5  # popülasyon std
    if std == 0:
        return None
    return [(i, (v - ort) / std) for i, v in enumerate(vals) if abs((v - ort) / std) >= k]


def ortalama_std(degerler: Iterable[float]) -> tuple[float, float]:
    """`(ortalama, popülasyon_std)` — örneklem değil popülasyon (n'e böler).

    Seçim bilinçli: elimizdeki satırlar bir örneklem değil, sorgunun **tamamıdır**.
    """
    vals = [float(v) for v in degerler]
    if not vals:
        return 0.0, 0.0
    ort = sum(vals) / len(vals)
    return ort, (sum((v - ort) ** 2 for v in vals) / len(vals)) ** 0.5
