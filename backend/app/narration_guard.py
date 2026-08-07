"""ANLATIM DOĞRULAYICI — T2'nin sert kuralı (Faz G4).

## Kural

> **Üretilen metindeki her sayı, sonuç kümesinde bulunmalı ya da beyan edilmiş bir işlemle
> (fark, yüzde, toplam, oran) ondan türetilebilmelidir. Doğrulanamayan sayı içeren cümle
> YAYIMLANMAZ.**

Bu, *"LLM sayı uydurabilir"* riskini bir **umut meselesi** olmaktan çıkarıp **test edilebilir
bir kapıya** çevirir. `viz.py`'nin *"grafik üretimini LLM'e verme"* disipliniyle (ADR-0024)
aynı felsefenin metin tarafıdır:

> **LLM üslubu yazar, SAYIYI sistem koyar.**

## Neden gerekli — iki katmanlı gizlilik modelinin ikinci yarısı

| Katman | LLM ne görür | Ne göremez |
|---|---|---|
| **T1** sorgu üretimi | şema adları + `sensitivity: normal` değer listeleri | hücre verisi, kişisel veri, ham satır |
| **T2** yorum / sohbet | kullanıcının **zaten yetkiyle sorduğu ve zaten gördüğü**, PII maskeli, makbuz damgalı **AGREGE** sonuç | ham satır, alttaki tablolar, **SQL yazma yetkisi** |

T2 açılmadan *"bu neden böyle?"*, *"normal mi?"*, *"ne yapmalıyız?"* sorularına
konuşulamaz — LLM'in **sayıları görmesi gerekir**. Ama sayıları görmek onları
**uydurabilmesi** demektir; bu modül o kapıyı kapatır.

## Tasarım kararları

**Sayı çıkarma Türkçe-farkındadır.** `1.234,56` (TR) ve `1,234.56` (EN) aynı sayıdır ve
LLM ikisini de üretebilir; ayrımı yapamayan bir doğrulayıcı doğru cümleleri reddeder ve
kapı kullanılamaz hale gelir (kapının en tehlikeli hâli budur — kapatılır).

**Tolerans göreceli**, mutlak değil. LLM `15.576.000`'ı *"15,6 milyon"* diye yuvarlar; bunu
uydurma saymak kapıyı kullanılamaz kılardı. Ölçek-duyarlı bir eşik kullanılır.

**Türetilmiş değerler beyan edilir, tahmin edilmez.** İzinli türetmeler: iki değerin farkı,
yüzde değişimi, toplam, ortalama, ve bir değerin toplama oranı. Bu liste **kapalıdır** —
"her aritmetik kombinasyon" serbest bırakılsaydı yeterince sayı ile her şey türetilebilirdi
ve kapı hiçbir şeyi engellemezdi.

**Yıl ve sıra sayıları sayı sayılmaz.** *"2025'te"*, *"ilk 5"*, *"%3'lük"* gibi ifadeler
veri iddiası değildir. Bunları doğrulamaya çalışmak, gerçek uydurmaları gürültüye boğardı.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Göreceli tolerans: LLM'in yuvarlaması meşrudur ("15.576.000" → "15,6 milyon" = %0,15 sapma).
# %2 hem yuvarlamaya izin verir hem "yaklaşık doğru" bir uydurmayı geçirmez.
TOLERANS = 0.02

# Bu aralıktaki tam sayılar YIL sayılır ve doğrulanmaz — veri iddiası değil zaman etiketidir.
YIL_ARALIGI = (1900, 2100)

# Çok küçük tam sayılar sıra/adet ifadeleridir ("ilk 5", "3 makine"); veri iddiası olarak
# doğrulanmaları gürültü üretir. Sınır bilinçli olarak DAR tutulur: gerçek bir ölçü
# 10'un altında olabilir ve o zaman doğrulanmalıdır.
SIRA_ESIGI = 10

# TR (1.234,56) ve EN (1,234.56) biçimleri + düz/ondalık. LLM üçünü de üretir.
#
# DİKKAT — gruplama dalında `*` DEĞİL `+`: `*` ile `15576000` (ayıraçsız) ilk dala
# `155` diye eşleşiyor ve geri kalan `76000` ayrı bir sayı sanılıyordu. Yani doğrulayıcı
# doğru bir cümleyi "155 ve 760 uydurma" diye reddediyordu — kapının en tehlikeli hâli,
# çünkü kullanılamaz olduğu için kapatılırdı. `+` gruplama dalını GERÇEKTEN gruplu
# sayılara sınırlar; ayıraçsız sayılar ikinci dala düşer ve bütün olarak okunur.
_SAYI_RE = re.compile(
    r"[-+]?\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?"   # 1.234,56 · 15.576.000 · 1,234.56
    r"|[-+]?\d+(?:[.,]\d+)?"                     # 15576000 · 1,5 · 12.34
)

# Cümle sınırı: nokta ondalık ayırıcı da olabildiği için "rakam.rakam" bölünmemeli.
_CUMLE_RE = re.compile(r"(?<=[.!?…])\s+(?=[^\d])|\n+")


def _coz(metin: str) -> float | None:
    """Türkçe ya da İngilizce biçimli bir sayıyı float'a çevirir; olmazsa None."""
    t = metin.strip().replace(" ", "")
    if not t:
        return None
    son_nokta, son_virgul = t.rfind("."), t.rfind(",")
    if son_nokta >= 0 and son_virgul >= 0:
        # Hangisi SONDAYSA o ondalık ayırıcıdır; diğeri binlik ayırıcıdır.
        if son_virgul > son_nokta:
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif son_virgul >= 0:
        # Tek tür ayırıcı: 3 hanelik gruplama ise BİNLİK, değilse ondalık.
        t = t.replace(",", "") if re.fullmatch(r"[-+]?\d{1,3}(,\d{3})+", t) else t.replace(",", ".")
    elif son_nokta >= 0 and re.fullmatch(r"[-+]?\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def sayilari_cikar(metin: str) -> list[float]:
    """Metindeki DOĞRULANACAK sayılar — yıl ve küçük sıra sayıları hariç."""
    out: list[float] = []
    for m in _SAYI_RE.finditer(metin or ""):
        v = _coz(m.group())
        if v is None:
            continue
        if v.is_integer():
            if YIL_ARALIGI[0] <= v <= YIL_ARALIGI[1]:
                continue          # yıl etiketi
            if abs(v) < SIRA_ESIGI:
                continue          # sıra/adet ifadesi
        out.append(v)
    return out


def _yakin(a: float, b: float, tol: float = TOLERANS) -> bool:
    """Göreceli yakınlık — yuvarlamaya izin verir, uydurmaya vermez."""
    if a == b:
        return True
    olcek = max(abs(a), abs(b))
    return olcek > 0 and abs(a - b) / olcek <= tol


def izinli_degerler(result: dict | None, *, ek: list[float] | None = None) -> list[float]:
    """Sonuç kümesindeki değerler + **BEYAN EDİLMİŞ** türetmeler.

    Türetme listesi **KAPALIDIR**. "Her aritmetik kombinasyon" serbest bırakılsaydı
    yeterince sayıyla her şey türetilebilirdi ve kapı hiçbir şeyi engellemezdi.

    İzinli: ham değerler · ikili farklar · yüzde değişimleri · kolon toplamları ·
    kolon ortalamaları · bir değerin kolon toplamına oranı (yüzde).
    """
    ham: dict[str, list[float]] = {}
    for satir in ((result or {}).get("rows") or []):
        if not isinstance(satir, dict):
            continue
        for k, v in satir.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                continue
            ham.setdefault(str(k), []).append(float(v))

    degerler: list[float] = [v for vs in ham.values() for v in vs]
    degerler.extend(ek or [])

    for vs in ham.values():
        if not vs:
            continue
        toplam = sum(vs)
        degerler.append(toplam)
        degerler.append(toplam / len(vs))
        if toplam:
            degerler.extend(v / toplam * 100 for v in vs)      # paylar (%)
        for i, a in enumerate(vs):
            for b in vs[i + 1:]:
                degerler.append(a - b)
                degerler.append(b - a)
                if a:
                    degerler.append((b - a) / abs(a) * 100)    # % değişim
                if b:
                    degerler.append((a - b) / abs(b) * 100)
    return degerler


@dataclass
class Rapor:
    """Doğrulama sonucu. `temiz_metin` yayımlanabilir olan kısımdır."""

    gecti: bool
    temiz_metin: str
    reddedilen: list[str] = field(default_factory=list)
    dogrulanamayan_sayilar: list[float] = field(default_factory=list)
    #: 🔴 `Ö5` — **PAYDA.** Guard'a giren cümle sayısı. Düşme ORANI olmadan düşme SAYISI
    #: yorumlanamaz: iki cümlelik bir anlatıda 1 düşmek ile yirmi cümlelik birinde 1
    #: düşmek aynı sayıdır, aynı şey değildir.
    #:
    #: ⚠ Burada üretilir çünkü bölmeyi **bu fonksiyon** yapıyor. Çağıranın metni yeniden
    #: bölmesi, `_CUMLE_RE`'nin ikinci bir sahibi demekti — ve bu deponun bir numaralı
    #: kusur sınıfı tam olarak odur. *Bir sayıyı, onu zaten bilen yerden iste.*
    toplam_cumle: int = 0

    def makbuza(self) -> dict[str, Any]:
        return {"narration_verified": self.gecti,
                "rejected_sentences": len(self.reddedilen),
                # 🔴 `Ö5` — payda olmadan düşme sayısı yorumlanamaz.
                "total_sentences": self.toplam_cumle,
                "unverified_numbers": self.dogrulanamayan_sayilar[:10],
                # 🔴 G5.4 — MUAFİYETLER GÖRÜNÜR OLUR.
                #
                # Kapı iki sınıfı **hiç doğrulamıyor** ve bu bilinçli — ama BELGESİZDİ:
                # kullanıcı *"her sayı doğrulanır"* sanıyordu. Bir muafiyeti gizlemek,
                # onu bir garanti gibi göstermenin en kısa yoludur.
                "muaf": {"yil": list(YIL_ARALIGI), "sira_esigi": SIRA_ESIGI}}


def dogrula(metin: str | None, result: dict | None, *,
            ek_degerler: list[float] | None = None, tolerans: float = TOLERANS) -> Rapor:
    """Cümle cümle doğrular; **doğrulanamayan cümleyi DÜŞÜRÜR**, metnin tamamını değil.

    Cümle bazında olması bilinçli: bir cümlede uydurma bir sayı varsa diğer üç doğru
    cümleyi de atmak kullanıcıya bilgi kaybettirir. Kapı **cerrahi** olmalıdır ki
    kullanılabilir kalsın — kullanılamayan kapı kapatılır ve o zaman hiç yoktur.

    Sayı İÇERMEYEN cümleler geçer: bu kapı sayı uydurmasını engeller, üslubu değil.
    """
    if not metin or not metin.strip():
        return Rapor(gecti=True, temiz_metin="")

    izinli = izinli_degerler(result, ek=ek_degerler)
    kalan: list[str] = []
    reddedilen: list[str] = []
    kotu_sayilar: list[float] = []

    for cumle in (c for c in _CUMLE_RE.split(metin) if c.strip()):
        sayilar = sayilari_cikar(cumle)
        hatali = [s for s in sayilar if not any(_yakin(s, d, tolerans) for d in izinli)]
        if hatali:
            reddedilen.append(cumle.strip())
            kotu_sayilar.extend(hatali)
        else:
            kalan.append(cumle.strip())

    return Rapor(
        gecti=not reddedilen,
        temiz_metin=" ".join(kalan),
        reddedilen=reddedilen,
        dogrulanamayan_sayilar=kotu_sayilar,
        toplam_cumle=len(kalan) + len(reddedilen),
    )


def guvenli_anlatim(uretilen: str | None, result: dict | None, *,
                    yedek: str | None = None, **kw) -> tuple[str, Rapor]:
    """`(yayımlanacak_metin, rapor)`.

    Üretilen metin tamamen düşerse **deterministik yedeğe** (`interpret` çıktısı) geçilir —
    kullanıcı boş ekran değil, daha az süslü ama **doğru** bir cevap görür. Yedek de yoksa
    boş döner: sessizce uydurulmuş bir cümle yayımlamaktansa hiçbir şey söylememek yeğdir.
    """
    r = dogrula(uretilen, result, **kw)
    if r.temiz_metin:
        return r.temiz_metin, r
    return (yedek or ""), r
