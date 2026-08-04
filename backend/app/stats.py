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


#: Regresyon eğimi için asgari gözlem. ⚠ `n<5 → YOK`: dört noktaya doğru çizmek, gürültüye
#: bir yön atfetmektir ve o yön **her zaman** bulunur.
ASGARI_TREND = 5


def trend(degerler: Iterable[float], *, asgari: int = ASGARI_TREND) -> dict | None:
    """En küçük kareler **eğimi** + anlamlılık. Kapıya takılırsa `None`.

    Döner: `{"egim", "r2", "yon", "n"}`.

    🔴 **`n < 5` → `None`.** Dört noktaya bir doğru çizmek, gürültüye bir **yön
    atfetmektir** — ve o yön her zaman bulunur. *Bir eğilim, bir eğim değildir.*

    ⚠ `r2` bir **anlamlılık testi değil**, bir uyum ölçüsüdür ve öyle raporlanmalı:
    yüksek `r2`'li bir eğim *"iyi oturuyor"* der, *"gerçek"* demez. Bir p-değeri üretmek
    için gereken varsayımlar (bağımsızlık, normallik) bir zaman serisinde **sağlanmaz**
    ve uydurma bir p-değeri, kalibre edilmemiş bir güven puanının aynısıdır.
    """
    vals = [float(v) for v in degerler]
    n = len(vals)
    if n < asgari:
        return None
    xs = list(range(n))
    x_ort = sum(xs) / n
    y_ort = sum(vals) / n
    pay = sum((x - x_ort) * (y - y_ort) for x, y in zip(xs, vals))
    payda = sum((x - x_ort) ** 2 for x in xs)
    if payda == 0:
        return None
    egim = pay / payda
    kesme = y_ort - egim * x_ort
    ss_tot = sum((y - y_ort) ** 2 for y in vals)
    ss_res = sum((y - (egim * x + kesme)) ** 2 for x, y in zip(xs, vals))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot else 0.0
    return {"egim": round(egim, 6), "r2": round(r2, 4), "n": n,
            "yon": "artan" if egim > 0 else "azalan" if egim < 0 else "yatay"}


def ozet(degerler: Iterable[float]) -> dict | None:
    """Tek çağrıda `{n, ortalama, std, min, maks, medyan}`. Boşsa `None`.

    ⚠ Medyan **çift sayıda gözlemde iki ortanın ortalamasıdır** — "alt orta"yı almak
    ucuz ama asimetrik dağılımda sistematik olarak yanlı bir sayı üretir.
    """
    vals = sorted(float(v) for v in degerler)
    if not vals:
        return None
    n = len(vals)
    ort, std = ortalama_std(vals)
    orta = (vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2)
    return {"n": n, "ortalama": round(ort, 6), "std": round(std, 6),
            "min": vals[0], "maks": vals[-1], "medyan": round(orta, 6)}
