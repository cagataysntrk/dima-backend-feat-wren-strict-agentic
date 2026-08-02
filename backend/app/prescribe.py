"""REÇETELİ ANALİZ — *"ne yapmalıyız?"* sorusunun ölçülebilir yarısı (Faz G3).

## Neden bu modül DAR

Bir "karar matrisi" kolayca uydurulur: seçenekler × kriterler × ağırlıklar tablosu her
zaman bir sayı üretir. Ama o sayıların **ölçülmüş bir zemini yoksa** ürün, kanıtlanabilir
bir BI aracından kanaat üreten bir araca dönüşür — ve bu depoda kayıtlı en temel değişmez
*"cevap bir makbuzdur"*dır.

Bu yüzden burada yalnız **veriden ya da BEYANDAN gelen** boyutlar kullanılır:

| Boyut | Kaynak | Uydurma payı |
|---|---|---|
| **Etki** | `contribution` deltası — ölçülmüş | yok |
| **Yön** (iyi/kötü) | `lower_is_better` — cube metadata'sında **beyan edilmiş** | yok |
| **Yoğunlaşma** | en büyük segmentin brüt harekete oranı — hesaplanmış | yok |

**Kasten DIŞARIDA bırakılanlar:** "kontrol edilebilirlik", "uygulama maliyeti", "risk".
Bunların hiçbiri veride yok ve tahmin edilemez. Bir ağırlık tablosuna konsalardı üretilen
sıralama **uydurma** olurdu — üstelik `source="cube"` rozetiyle. Gerçek bir müşteride bu
boyutlar **beyan edilerek** eklenebilir (metadata), tahmin edilerek değil.

## En önemli çıktı bir öneri değil bir REDDİR

Değişim **dağınıksa** (hiçbir segment brüt hareketin anlamlı bir payını açıklamıyorsa),
*"şu segmente odaklan"* demek **yanlış tavsiyedir**: sorun sistemiktir ve tek bir segmenti
düzeltmek toplamı kayda değer biçimde değiştirmez. Bu modül o durumda öneri üretmez,
**neden üretmediğini söyler**.

Bu, `contribution`'ın toplanabilirlik kapısıyla (*"AVG'de katkı payı TANIMSIZDIR"*) aynı
disiplinin reçete seviyesindeki karşılığıdır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Yoğunlaşma eşiği: en büyük segment brüt hareketin bu kadarını açıklamıyorsa değişim
# DAĞINIK sayılır. 1/3 seçildi — üç eşit segmentte hiçbiri "sürükleyici" değildir ve
# birine odaklanmak diğer üçte ikisini görmezden gelmek olur.
YOGUNLASMA_ESIGI = 1 / 3

# En çok kaç öneri: liste uzadıkça "önceliklendirme" iddiası zayıflar. İlk üç segment
# odaklanılabilir bir gündemdir; onuncu segment bir gündem değil bir dökümdür.
AZAMI_ONERI = 3


@dataclass(frozen=True)
class Oneri:
    """Tek bir segment için ölçülmüş öneri. **Her alan bir kaynağa dayanır.**"""

    segment: str
    etki: float                 # contribution deltası (ölçülmüş)
    pay: float | None           # net değişime oranı (net ~0 ise None — UYDURULMAZ)
    yon: str                    # "kotulesti" | "iyilesti" — `lower_is_better` BEYANINDAN
    cube_query: dict[str, Any]  # tıklanınca tek başına açılır, kendi makbuzunu üretir

    def makbuza(self) -> dict[str, Any]:
        return {"segment": self.segment, "impact": self.etki,
                "share": self.pay, "direction": self.yon}


@dataclass
class Recete:
    """Reçetenin tamamı: öneriler + **neden bu kadarı** + neden daha fazlası değil."""

    oneriler: list[Oneri] = field(default_factory=list)
    yogunlasma: float | None = None      # en büyük segmentin brüt paydaki oranı
    dagitik: bool = False
    gerekce: str = ""

    def makbuza(self) -> dict[str, Any]:
        return {"prescription": {
            "options": [o.makbuza() for o in self.oneriler],
            "concentration": self.yogunlasma,
            "diffuse": self.dagitik,
            "rationale": self.gerekce,
        }}


def _yon(delta: float, lower_is_better: bool) -> str:
    """Bir artış İYİ mi KÖTÜ mü? Cevap **veride değil BEYANDA**: `lower_is_better`.

    Bu alan `schema()`'da Faz 1'den beri var ve MIMARI §13.4'te *"`recommend()`'e ulaşıyor
    ama renk kararına dönüşmüyor"* diye kayıtlıydı. Burada **anlama** dönüşüyor: fire
    artışı kötüdür, ciro artışı iyidir — ve bunu ad tahmininden değil beyandan biliyoruz.
    """
    artti = delta > 0
    return "kotulesti" if (artti != (not lower_is_better)) else "iyilesti"


def recete(rapor: dict, *, lower_is_better: bool = False,
           azami: int = AZAMI_ONERI, esik: float = YOGUNLASMA_ESIGI) -> Recete:
    """Bir `ContributionReport` sözlüğünden ölçülmüş reçete üretir.

    `rapor`: `{net_degisim, brut_hareket, bulgular:[{label, delta, net_pay, cube_query}]}`.

    **Dağınık değişimde öneri ÜRETİLMEZ** — bu bir eksiklik değil bir karardır:
    hiçbir segment brüt hareketin anlamlı bir payını açıklamıyorsa sorun sistemiktir ve
    *"şu segmente odaklan"* demek yanlış tavsiyedir.
    """
    bulgular = [b for b in (rapor.get("bulgular") or []) if b.get("cube_query")]
    if not bulgular:
        return Recete(gerekce="Ayrıştırılabilir bir segment bulunamadı.")

    brut = float(rapor.get("brut_hareket") or 0.0)
    en_buyuk = max(abs(float(b.get("delta") or 0.0)) for b in bulgular)
    yogunlasma = (en_buyuk / brut) if brut else None

    if yogunlasma is not None and yogunlasma < esik:
        # DÜRÜST RED — `contribution`'ın toplanabilirlik kapısıyla aynı disiplin.
        return Recete(
            yogunlasma=yogunlasma, dagitik=True,
            gerekce=(f"Değişim dağınık: en büyük segment brüt hareketin yalnız "
                     f"%{yogunlasma*100:.0f}'ini açıklıyor. Tek bir segmente odaklanmak "
                     "toplamı kayda değer biçimde değiştirmez — sorun büyük olasılıkla "
                     "sistemik. Önce kırılımı değiştirip (başka bir boyut) bakmak gerekir."))

    sirali = sorted(bulgular, key=lambda b: abs(float(b.get("delta") or 0.0)), reverse=True)
    oneriler = [
        Oneri(segment=str(b.get("label") or "?"),
              etki=float(b.get("delta") or 0.0),
              pay=(float(b["net_pay"]) if b.get("net_pay") is not None else None),
              yon=_yon(float(b.get("delta") or 0.0), lower_is_better),
              cube_query=b["cube_query"])
        for b in sirali[:azami]
    ]
    kotu = [o for o in oneriler if o.yon == "kotulesti"]
    gerekce = (f"Değişim yoğunlaşmış (en büyük segment brüt hareketin "
               f"%{(yogunlasma or 0)*100:.0f}'i). "
               + (f"{len(kotu)} segment ters yönde hareket etmiş; önce onlara bakmak "
                  "en yüksek getirili adım." if kotu else
                  "Segmentlerin hepsi istenen yönde hareket etmiş."))
    return Recete(oneriler=oneriler, yogunlasma=yogunlasma, gerekce=gerekce)
