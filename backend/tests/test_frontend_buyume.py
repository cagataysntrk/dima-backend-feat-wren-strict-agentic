"""**FRONTEND MODÜL BÜYÜME KAPISI** — `0.21`'in arayüz yarısı. *(denetim F5)*

## 🔴 Ölçülen risk

`ask.py` **2.498 satıra** çıktı ve ancak bir kapı kurulunca durdu. Frontend'de o kapı
**hiç yoktu**:

```
ls backend/tests/test_modul_buyume.py                    # var — yalnız backend
grep -rn "ReportCard" backend/tests/test_modul_buyume.py # → 0
```

`ReportCard.tsx` bugün **948 kod satırı · 25 buton**: cevap-sonrası **tüm** etkileşim
orada (zamanla · panoya ekle · doğrula · yanlış bildir · drill · makbuz · karta yanıt ·
onay kartı · SQL · sözleşme · çapa · hücre kırılımı).

> ⚠ Denetimin kendi ifadesiyle bu *"bir kusur değil bir **risktir**"* — ve `ask.py`
> **tam bu şekilde** büyüdü. *Bir tavan, aşıldıktan sonra konursa bir tavan değil bir
> onaydır.*

## 🔴 TAVAN = BUGÜNKÜ ÖLÇÜM, hedef değil

Küçültmek serbesttir ve ayrı bir maddedir; bu kapı **büyümeyi** durdurur. Sayılar
`kapi_ortak.yorumsuz()` ile **yorumsuz** ölçülür — bu depoda yorumlar gerekçe taşır ve
onları saymak, **belgelemeyi cezalandırırdı**.

⚠ Tavan aşıldığında yapılacak şey **tavanı yükseltmek değil**, davranışı bir modüle
çıkarmaktır (`Makbuz.tsx` · `SertifikaBandi.tsx` · `HataSeridi.tsx` · `GeriAlSeridi.tsx`
bu turda tam olarak böyle doğdu). Gerçekten muaf bir iş ise `MUAFIYET`'e **gerekçesiyle**
yazılır — *gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.*
"""

from __future__ import annotations

import pytest

from tests.kapi_ortak import fe_dosyalari, yorumsuz

#: `dosya → tavan` (kod satırı, yorumsuz). **Ölçülen değerler** — 2026-08-05.
#: ⚠ Yalnız *"ağırlık merkezi"* dosyalar: her dosyaya tavan koymak, kapıyı bir
#: bürokrasiye çevirir ve **hiçbirine bakılmaz** hâle getirir.
# ⟳ 2026-08-05 · FAZ 4 — İKİ TAVAN **İNDİRİLDİ**, biri yükseltildi.
#
# 🔴 Kapının kendi kuralı: *"tavanda boşluk varsa kapı büyümeyi durdurmuyor; tavan
# ÖLÇÜLEN DEĞERE çekilmeli."* `ReportCard` makinesi (`KartMakinesi`) ve zamanlama
# açılır kutusu (`KartZamanlama`) ayrı bileşenlere çıkınca dosya 948 → **883**'e indi;
# tavanı 948'de bırakmak 65 satırlık **sessiz bir büyüme izni** olurdu.
#   ReportCard 948 → 883   (makine + zamanlama çıkarıldı)
#   page.tsx   534 → 522   (ayarlar bölümü çıkarıldı)
#
# ⚠ `api-client.ts` 778 → 791: geri-alma sarmalayıcıları eklenmişti ve bu depoda TÜM
# HTTP oradan geçer (`dima-frontend/CLAUDE.md`) — yani bu bir muafiyet değil, kuralın
# kendi maliyeti. *Bir tavan, kuralın gerektirdiği büyümeyi de yasaklıyorsa kuralı
# yasaklamış olur.*
TAVANLAR = {
    "components/ReportCard.tsx": 883,
    "lib/api-client.ts": 791,
    "lib/chart.ts": 688,
    "lib/types.ts": 579,
    "components/ReviewPanel.tsx": 555,
    "app/page.tsx": 522,
    "components/ResultView.tsx": 476,
    "components/InterpretationBar.tsx": 472,
}

#: `(dosya, Δ, gerekçe)` — her satır **bir maddeye** aittir ve nedeni yazılıdır.
MUAFIYET: list[tuple[str, int, str]] = [
    ("lib/api-client.ts", 14,
     "denetim F2 — pano ve widget GERİ ALMA sarmalayıcıları (`restoreDashboard`, "
     "`restoreDashboardWidget`). 🔴 Bu iki fonksiyon TAŞINAMAZ: `dima-frontend/CLAUDE.md` "
     "birebir «Tüm HTTP `src/lib/api-client.ts`'ten geçer — dağınık `fetch` yok» diyor. "
     "İkinci bir HTTP dosyası açmak, bir tavan borcunu bir MİMARİ İHLALİNE çevirirdi. "
     "⚠ Ve kapı bunu ilk gününde yakaladı — yazarını dahil: bir tavan, kendi koyanını "
     "da bağlamıyorsa bir tavan değildir."),
]


def _kod_satiri(metin: str) -> int:
    """Yorum ve boş satır **hariç**. ⚠ Bu depoda yorumlar gerekçe taşır; onları saymak
    **belgelemeyi cezalandırırdı** ve kapı, iyi bir alışkanlığı bir borç gibi gösterirdi."""
    return len([s for s in yorumsuz(metin).split("\n") if s.strip()])


@pytest.mark.parametrize("dosya", sorted(TAVANLAR))
def test_TAVAN_ASILMADI(dosya):
    """🔴 **ASIL KAPI.** *Bir tavan, aşıldıktan sonra konursa bir tavan değil bir
    onaydır.*"""
    kaynak = fe_dosyalari().get(dosya)
    assert kaynak is not None, f"⊘ {dosya} yok — tavan bir şey korumuyor"
    n = _kod_satiri(kaynak)
    tavan = TAVANLAR[dosya] + sum(d for f, d, _ in MUAFIYET if f == dosya)
    assert n <= tavan, (
        f"🔴 {dosya}: {n} kod satırı — tavan {tavan}.\n"
        f"YAPILACAK: yeni davranışı bir **bileşene çıkar**, tavanı yükseltme. Bu turda "
        f"`Makbuz` · `SertifikaBandi` · `HataSeridi` · `GeriAlSeridi` tam böyle doğdu.\n"
        f"Gerçekten muaf bir iş ise `MUAFIYET`'e **dosya + Δ + GEREKÇE** ile yazılır; "
        f"gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.")


def test_KAPI_GERCEKTEN_KIRMIZI_VERIYOR():
    """⚠ *Kırmızı veremeyen bir kapı, olmayan bir kapıdır.* En büyük dosyaya bir **kod**
    satırı enjekte edilince tavan aşılmalı — yani tavanda **boşluk olmamalı**."""
    dosya = "components/ReportCard.tsx"
    kaynak = fe_dosyalari()[dosya]
    n = _kod_satiri(kaynak)
    assert n == TAVANLAR[dosya], (
        f"🔴 {dosya} tavanında {TAVANLAR[dosya] - n} satır BOŞLUK var — kapı büyümeyi "
        f"durdurmuyor. Tavan **ölçülen değere** çekilmeli.")
    assert _kod_satiri(kaynak + "\nconst _MUTASYON = 1;\n") > TAVANLAR[dosya]


def test_YORUM_SATIRI_TAVANI_YEMIYOR():
    """🔴 Birim kararının davranıştaki karşılığı: bir **yorum** eklemek kapıyı kırmazsa,
    *"yorumsuz sayım"* bir niyet beyanı değil bir ölçüdür."""
    kaynak = fe_dosyalari()["components/ReportCard.tsx"]
    assert _kod_satiri(kaynak + "\n// yalnız bir yorum\n") == _kod_satiri(kaynak)


def test_MUAFIYETLER_GEREKCELI():
    """*Gerekçesiz bir muafiyet, muafiyet değil sessiz bir tavan artışıdır.*"""
    for dosya, delta, gerekce in MUAFIYET:
        assert dosya in TAVANLAR and delta > 0 and len(gerekce) > 25, (dosya, delta)


def test_KAPSAM_agirlik_merkeziyle_SINIRLI():
    """⚠ Her dosyaya tavan koymak, kapıyı bir **bürokrasiye** çevirir ve hiçbirine
    bakılmaz hâle getirir. Kapsam: en büyük sekiz dosya."""
    hepsi = fe_dosyalari()
    en_buyuk = sorted(hepsi, key=lambda k: -_kod_satiri(hepsi[k]))[:8]
    eksik = sorted(set(en_buyuk) - set(TAVANLAR))
    assert not eksik, (
        f"🔴 Ağırlık merkezine yeni dosya girmiş ama tavanı yok: {eksik}. "
        f"Bir dosya en büyük sekize giriyorsa, büyümesi de ölçülmeli.")
