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


#: `|z| ≥ k` eşiğinin **normal** bir dağılımda kendiliğinden işaretlediği pay.
#: ⚠ Bu bir varsayımdır ve beyanda **adıyla** söylenir — gizlenmiş bir varsayım,
#: yapılmamış bir varsayımdan tehlikelidir.
_SANS_PAYI = {2.0: 0.0455, 2.5: 0.0124, 3.0: 0.0027}


def tarama_beyani(n_aday: int, n_isaret: int, k: float = VARSAYILAN_K) -> str:
    """🔴🔴 `§E3` — **KAÇ ADAY TARANDI, KAÇI İŞARETLENDİ.** Tek sahip.

    ## Ölçülen boşluk

    Aykırılık sinyali `|z| ≥ 2` ile N nokta üzerinde koşuyor ve **N kullanıcıya hiç
    söylenmiyordu**. Oysa bir eşik, taranan aday sayısı büyüdükçe **aritmetik gereği**
    işaret üretir: kullanıcı *«3 aykırılık bulundu»* cümlesinin çok mu az mı olduğunu
    bilemez.

    > *«In our experiment, over 60% of user insights were false.»* — Zgraggen, Zhao,
    > Zeleznik, Kraska (Brown/MIT), **CHI 2018** (`§10.5`)

    ## 🔴 NEDEN BENJAMINI-HOCHBERG DEĞİL

    Kart `FDR düzeltmesi (BH)` diyor. **Ölçüldü: bu depoda p-değeri YOK** — eşik bir
    z-kesimidir, bir hipotez testi değil (`z_skorlari`). BH **p-değerlerini** sıralar;
    z'yi p'ye çevirmek **normallik varsayımını dayatmak** olurdu ve o varsayım
    ölçülmedi. ⊙ `§E2`'de forecast için verdiğim kararın aynısı: **elimizde olmayan bir
    tabanı uydurmaktansa, elimizdekini beyan etmek.**

    Kartın kendi azaltma satırı da bunu söylüyor: *«Elenen sayısını **beyan et** —
    "N aday incelendi, M'i istatistiksel eşiği geçti"»* (`§98.1` disiplini).

    ⚠ Ve şans payı **varsayımıyla birlikte** yazılır: `|z|≥2` normal bir dağılımda
    ~%4,6'yı kendiliğinden işaretler. Varsayımı saklamak, sayıyı olduğundan güçlü
    göstermek olurdu.

    Döner: beyan cümlesi ya da `""` (taranacak bir şey yoksa).
    """
    if n_aday < ASGARI_GOZLEM or n_isaret <= 0:
        return ""
    _s = f"{n_aday} aday tarandı, {n_isaret}'i **|z| ≥ {k:g}** eşiğini geçti"
    if (pay := _SANS_PAYI.get(float(k))) is not None:
        beklenen = n_aday * pay
        _s += (f" — ⚠ bu eşik **normal** bir dağılımda ~%{pay * 100:.1f}'ini "
               f"kendiliğinden işaretler (bu {n_aday} adayda ~{beklenen:.1f})")
    return _s + "."


#: 🔴 `§E3` — bir **seçim** ancak iki adaydan itibaren bir seçimdir. Altında cümle
#: kurmak, tek adayı *«taranmış»* gibi göstermek olurdu.
ASGARI_ADAY_SECIM = 2


def secim_beyani(n_aday: int, olcut: str) -> str:
    """🔴🔴 `§E3` — **MAX-SEÇİMİ TARAMALARININ GENİŞLİĞİ.** `tarama_beyani`'nin kardeşi,
    **rakibi değil** (`KAT-1`: cümlenin sahibi hâlâ bu modül).

    ## Neden ayrı bir kip — ölçülmüş bir yanlış cümle riski

    `tarama_beyani` bir **z-kesimine** bağlıdır ve cümlesinde *«|z| ≥ 2 eşiğini geçti»*
    yazar; şans payını da o eşiğin normal dağılımdaki oranından okur (`_SANS_PAYI`).
    Denetimde (⟳ 2026-08-12) sayılan **dört** tarama yerinin **üçü** bir eşik testi
    değil, bir **`max(...)` seçimi**dir:

    | tarama yeri | seçim kuralı |
    |---|---|
    | `kok_neden._en_ayristiran` | aday kırılımlar arasında **en çok ayrıştıran** |
    | `kok_neden.derinles` | `AZAMI_ADAY` kırılım arasında yine max yayılım |
    | `kok_neden.toplam_turu` | kırılımdaki **en büyük** segment |
    | `contribution.arastir` | `MAX_BOYUT` boyut × segment süpürmesi |

    Oralarda `tarama_beyani` çağırmak, olmayan bir eşiği **varmış gibi** yazmak olurdu:
    *«doğru hesaplanmış bir sayı yanlış bir cümlede hâlâ yanlıştır.»*

    ## Ne söyler, ne söylemez

    ✅ **genişlik**: kaç aday arasından seçildi — çünkü aday sayısı büyüdükçe en uçtaki
    değerin **şans eseri** uçta olma ihtimali büyür (CHI 2018, `§10.5`).
    ⊘ **şans payı YAZILMAZ**: bir max-seçiminde şans payı ancak adayların dağılımı
    hakkında bir varsayımla hesaplanır ve o varsayım **ölçülmedi**. `§E2`'de forecast
    için, `§E3`'te BH için verilen kararın aynısı — *elimizde olmayan bir tabanı
    uydurmaktansa, elimizdekini beyan etmek.*

    Döner: beyan cümlesi ya da `""` (seçilecek bir şey yoksa).
    """
    if n_aday < ASGARI_ADAY_SECIM or not olcut:
        return ""
    return (f"{n_aday} aday arasından {olcut} seçildi — ⚠ bu bir **eşik testi değil, "
            f"bir seçimdir**: aday sayısı arttıkça en uçtaki değerin şans eseri uçta "
            f"olma ihtimali de artar, ve bu pay hesaplanmadı (varsayım ölçülmedi).")
