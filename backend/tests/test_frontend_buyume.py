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
# ⟳ FAZ 5 — TAVANLAR **YENİDEN ÖLÇÜLDÜ ve HEPSİ İNDİ (ya da sabit kaldı).**
# Sebep bir kod değişikliği değil, **aletin onarımı**: `yorumsuz()` çok satırlı JSX
# yorumlarının sarmalayıcısını (`{` ve `}`) kod sayıyordu. Yani bu depodaki tavanlar
# gerçekte olmayan **54 satıra kadar** hava taşıyordu — ve o hava, gerekçe yazıldıkça
# şişiyordu.
#
# 🔴 Her yeni sayı **ölçülen** değerdir; hiçbiri yuvarlanmadı, hiçbiri yükselmedi:
#   ReportCard 883→829 · page 522→512 · InterpretationBar 472→468 ·
#   ReviewPanel 555→553 · ResultView 476→474 · (api-client · chart · types sabit)
#
# *Bir tavanın hava taşıdığı, ancak aleti onarınca görülür; ve o hava fark edilmeden
# harcanır — çünkü kapı yeşil kaldığı sürece kimse ölçüye bakmaz.*
# ⟳ FAZ 4B — dört tavan **ölçülen** değere çekildi; ikisi ise MUAFİYETE gitti.
# Büyümenin tamamı yeni bir YETENEĞİN kendi evindeki karşılığıdır:
#   ReportCard 829→836 · chart.ts 688→702 · page 512→513 · ResultView 474→477
# 🔴 `lib/types.ts` (+27) ve `lib/api-client.ts` (+7) tavana DEĞİL muafiyete yazıldı,
# çünkü onlar **bölünemez** (`dima-frontend/CLAUDE.md`: tipler tek dosyada senkron
# tutulur · tüm HTTP tek dosyadan geçer). Bir mimari kuralın zorladığı büyümeyi sessiz
# bir tavan artışına çevirmek, borcu gerekçesiyle birlikte kaybetmek olurdu.
TAVANLAR = {
    "components/ReportCard.tsx": 836,
    "lib/api-client.ts": 791,
    "lib/chart.ts": 702,
    "lib/types.ts": 579,
    "components/ReviewPanel.tsx": 553,
    "app/page.tsx": 513,
    "components/ResultView.tsx": 477,
    "components/InterpretationBar.tsx": 468,
}

#: `(dosya, Δ, gerekçe)` — her satır **bir maddeye** aittir ve nedeni yazılıdır.
#: ⚠ Kapı `Δ > 0` ister: **hiçbir şey vermeyen bir muafiyet muafiyet değildir** — ve
#: bu kuralı FAZ 5'te bizzat kendi kapımız uyguladı (Δ'yı 0'a çekince kırmızı verdi;
#: doğru yanıt onu **listeden çıkarmaktı**, sıfırlamak değil).
MUAFIYET: list[tuple[str, int, str]] = [
    ("lib/types.ts", 27,
     "FAZ 4B — kök-neden sözleşmesi: `KokNedenDurum` · `KokNedenDugum` · "
     "`KokNedenResponse` + `DrillRequestInput.ek_filtreler`. 🔴 TAŞINAMAZ: "
     "`dima-frontend/CLAUDE.md` birebir «Backend tipleri `src/lib/types.ts`'te SENKRON "
     "tutulur» diyor. İkinci bir tip dosyası açmak, sözleşmenin iki yerde yaşamasına ve "
     "birinin güncellenip ötekinin unutulmasına kapı açardı — bu deponun ölçülmüş "
     "«aynı kuralın iki sahibi» sınıfı. ⚠ Bir sözleşme büyüdüğünde tip dosyası büyür; "
     "bunu bir tavan artışıyla saklamak, borcu gerekçesiyle birlikte kaybetmek olurdu."),
    ("lib/api-client.ts", 7,
     "FAZ 4B — `kokNedenHaritasi()` (`POST /ask/kok-neden`). 🔴 TAŞINAMAZ: "
     "«Tüm HTTP `src/lib/api-client.ts`'ten geçer — dağınık `fetch` yok» (CLAUDE.md). "
     "⚠ Bu dosyada daha önce kapanmış bir muafiyet var (aşağıdaki kayıt); o zaman tavan "
     "ölçülene çekilmişti. Bu kez tavan DEĞİL muafiyet büyüyor — aynı hatayı ikinci kez "
     "yapmamak için: tavan artışı sessizdir, muafiyet gerekçelidir."),
]

# ═══ KAPANMIŞ MUAFİYETLER — kayıt, MIMARI §10: *"kapananlar işaretlenir, silinmez"* ═══
#
# ⟳ `lib/api-client.ts` · Δ 14 · **KAPANDI (FAZ 5)**
#   Açılış gerekçesi: denetim F2 — pano ve widget GERİ ALMA sarmalayıcıları
#   (`restoreDashboard`, `restoreDashboardWidget`). Bu iki fonksiyon TAŞINAMAZDI:
#   `dima-frontend/CLAUDE.md` birebir «Tüm HTTP `src/lib/api-client.ts`'ten geçer —
#   dağınık `fetch` yok» diyor; ikinci bir HTTP dosyası açmak bir tavan borcunu bir
#   MİMARİ İHLALİNE çevirirdi.
#   🔴 Kapanış sebebi: muafiyet açıldığında tavan **778**'di. Sonra tavan ölçülen
#   **791**'e çekildi ve o 14 satır **tavanın içine girdi** — yani muafiyet aynı
#   satırları ikinci kez affediyordu. Etkin tavan sessizce 805 olmuştu.
#   *Bir muafiyet, gerekçesi tükendiğinde kapanır — unutulduğunda değil.*


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


def test_JSX_YORUMU_TAVANI_YEMIYOR():
    """🔴 **Ölçüldü, tahmin değil.** Çok satırlı bir `{/* … */}` bloğu tavana **2 satır**
    yazıyordu: ayıklayıcı `/*`nin solundaki `{`yi ve `*/`nin sağındaki `}`yi kod sayıyordu.

    Sonuç ters yönlüydü: kapı, gerekçe yazmayı **cezalandırıyordu** — oysa `yorumsuz()`
    tam da bunu önlemek için yazılmıştı. *Bir aletin niyeti, davranışının kanıtı değildir.*"""
    kaynak = fe_dosyalari()["components/ReportCard.tsx"]
    jsx = "\n      {/* çok\n          satırlı\n          JSX yorumu */}\n"
    assert _kod_satiri(kaynak + jsx) == _kod_satiri(kaynak), \
        "🔴 JSX yorum sarmalayıcısı hâlâ kod sayılıyor"


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
