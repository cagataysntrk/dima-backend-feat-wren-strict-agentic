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
TAVANLAR = {
    # 🔴 **948 → 1009 (2026-08-06) ve bu ARTIŞIN İKİ AYRI SAHİBİ VAR — ikisi de yazılı.**
    #
    # ⊙ +37 · `7595250` (KÖK-2/KÖK-3): `eksik_niyet` uyarı şeridi. Backend cevabı artık
    #   *"sayı doğru ama sorunun bir parçası taşınmadı"* diyor ve bunun bir TÜKETİCİSİ
    #   olmadan özellik "bitti" değildir (deponun *arka-ön bütünlüğü* kuralı).
    #   🔴 Ve bu artış kapıyı KIRMIZIYA ÇEVİRDİ, kimse görmedi: yerel kapı 2026-08-04'te
    #   **yalnız korpusa** indirildi ve süit gecelik CI'ya taşındı. Üç commit boyunca
    #   kırmızı kaldı. *Bir kapıyı ucuzlaştırmak, onu görünmez yapmanın da yoludur.*
    #
    # ⊙ +24 · KÖK-9 belirsizlik chip'i: `suggestions[].kind === "tanim"` bloğu.
    #   TAŞINAMAZ ve sebebi ÜÇÜNCÜ BİR EDİM olması: "devam sorusu" bu cevabın ÜSTÜNDE
    #   konuşur, "sonraki adım" bu SORGUYU düzenler, bu ise AYNI SORUYU BAŞKA BİR TANIMLA
    #   yeniden sorar. Var olan kutuya koymak, o kutunun kullanıcıya verdiği sözü
    #   ("yeni sorgu yazılmaz") YALAN yapardı. *Bir chip'in yanındaki açıklama, chip'in
    #   kendisi kadar bir vaattir.*
    #
    # ⚠ Tavan MUAFIYET listesine değil buraya yazıldı: `test_KAPI_SAHTE_DEGIL` bu dosyada
    # `n == TAVANLAR[dosya]` arıyor (boşluksuz tavan), muafiyet toplamına değil.
    # ⊙ +24 · KÖK-7d TÜRETME chip'i (`kind === "turetme"`). ÜÇÜNCÜ değil DÖRDÜNCÜ bir
    # edim ve kendi kutusunu hak ediyor: "devam sorusu" bir CEVABIN üstünde konuşur,
    # "sonraki adım" bir SORGUYU düzenler, "başka tanım" aynı soruyu başka tanımla sorar
    # — bu ise bir REDDİN yanında durur ve sorunun KENDİSİNİ düzeltir ("ne kadar sattık"
    # → "ciro"). Var olan bir kutuya konsa kullanıcı bir cevabın devamı sanardı; oysa
    # ortada cevap yok, red var. *Bir chip'in bulunduğu kutu, ne vaat ettiğini söyler.*
    "components/ReportCard.tsx": 1033,
    "lib/api-client.ts": 778,
    "lib/chart.ts": 688,
    # ⊙ 579 → 581: +1 `eksik_niyet?: string[]` (KÖK-3) · +1 `Suggestion.kind?` (KÖK-9).
    # ⚠ İkisi de bir ALAN BEYANIDIR, mantık değil — tip dosyasının büyümesi burada
    # backend sözleşmesinin büyümesidir ve onu cezalandırmak, sözleşmeyi belgesiz
    # bırakmayı ödüllendirirdi.
    "lib/types.ts": 581,
    "components/ReviewPanel.tsx": 555,
    "app/page.tsx": 534,
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
