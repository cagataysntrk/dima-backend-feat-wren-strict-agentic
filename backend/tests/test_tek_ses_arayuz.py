"""**TEK SES — arayüz yarısı.** `app/soz.py`'nin jargon yasağı frontend'de de geçerli.
*(denetim F4)*

## 🔴 Ölçülen çürüme yüzeyi

`app/soz.py` (FAZ 5.17) *"tek ses"* katalogunu tutuyor ve **12 jargon kelimesini**
kullanıcıya göstermeyi yasaklıyor. Frontend'de karşılığı **yoktu**: kullanıcıya görünen
Türkçe metnin yarısı tek sahipli (backend), yarısı **42 bileşene dağılmış**.

> ⚠ Denetimin ifadesiyle bu *"bugün bir hata değil, bir **çürüme yüzeyi**"* — aynı kavram
> iki yerde iki farklı kelimeyle anılabilir ve **hiçbir kapı bunu görmez**.
> (Deponun 1 numaralı kusur sınıfı **"aynı kural iki sahip"**in metin hâli.)

## Neden metnin tamamı taşınmadı

42 bileşenin metnini `soz.py`'ye taşımak, **ikinci bir sahip** yaratma riskini çözmez —
yalnız yerini değiştirir; ve JSX'te satır içi metin okunabilirliğin kendisidir. Uygulanan
şey **kuralın kendisi**: jargon kullanıcıya **görünmez**.

## ⚠ Beyanlı muafiyet — `/review` bir UZMAN yüzeyidir

`measure:read` izni ister ve *"Discovery"* orada bir **terimdir**, jargon değil: ölçü
küratörü hangi yoldan gelen adayı incelediğini bilmek **zorundadır**. Muafiyet **yazılı**;
*gerekçesiz bir muafiyet, muafiyet değil sessiz bir istisnadır.*
"""

from __future__ import annotations

import re

from app.soz import JARGON
from tests.kapi_ortak import fe_dosyalari

#: `dosya → gerekçe` — jargonun **terim** olduğu uzman yüzeyleri.
MUAF = {
    "app/review/page.tsx":
        "ölçü inceleme (`measure:read`) — küratör adayın hangi yoldan geldiğini "
        "bilmek ZORUNDADIR; burada 'Discovery' bir terimdir, jargon değil",
    "components/ReviewPanel.tsx":
        "aynı uzman yüzeyinin paneli — adayın kökeni gizlenirse küratör neyi "
        "onayladığını bilemez",
}

#: Görünür metin: JSX metin düğümü **ve** kullanıcıya okunan öznitelikler.
_METIN = re.compile(r">\s*([^<>{}\n][^<>{}]{6,}?)\s*<")
_ETIKET = re.compile(r'(?:title|aria-label|placeholder)="([^"]{4,})"')

#: 🔴 **KOD İŞARETLERİ** — bunları taşıyan bir parça JSX metni **değildir**.
#: İlk sürüm yalnız `{}` dışlıyordu ve `neYaptim(item.cube_query)` gibi **kodu**
#: yakaladı: `fe_dosyalari()` yorumları ayıklayıp satırları sıkıştırdığı için `>`…`<`
#: aralığı bazen süslü parantezsiz kod kapsıyor.
#: *Bir taramanın kendi deseni de bir bağımlılıktır* — ve bu, bu operasyonda
#: **on birinci** kez ölçüm aracının kusuru oldu.
_KOD = (";", "=>", "const ", "??", "return ", "() =>", "].", ").")


def _gorunur_metinler(src: str) -> list[str]:
    cikti: list[str] = []
    for rx in (_METIN, _ETIKET):
        for m in rx.finditer(src):
            metin = " ".join(m.group(1).split())
            if any(k in metin for k in _KOD):
                continue
            cikti.append(metin)
    return cikti


def test_JARGON_KULLANICIYA_gorunmuyor():
    """🔴 *Kullanıcının bilmediği bir kelimeyle yazılmış bir cevap, cevap değildir.*"""
    bulgular: list[str] = []
    for yol, src in fe_dosyalari().items():
        if yol in MUAF:
            continue
        for metin in _gorunur_metinler(src):
            dusuk = metin.lower()
            for j in JARGON:
                if j in dusuk:
                    bulgular.append(f"{yol}: «{j}» → {metin[:60]}")
    assert not bulgular, (
        "🔴 Kullanıcıya görünen metinde JARGON:\n  " + "\n  ".join(bulgular)
        + "\n\n`app/soz.py::JARGON` bu kelimeleri yasaklıyor. Gerçekten bir UZMAN "
          "yüzeyiyse `MUAF`'a **gerekçesiyle** yazılır.")


def test_MUAFIYETLER_GEREKCELI_ve_GERCEK():
    """*Gerekçesiz bir muafiyet, muafiyet değil sessiz bir istisnadır.* Ve muaf dosya
    **var olmalı**: silinmiş bir dosyanın muafiyeti, bayat bir izindir."""
    dosyalar = fe_dosyalari()
    for yol, gerekce in MUAF.items():
        assert yol in dosyalar, f"🔴 muaf dosya YOK: {yol} — bayat muafiyet"
        assert len(gerekce) > 40, f"🔴 yüzeysel gerekçe: {yol}"


def test_KAPI_GERCEKTEN_KIRMIZI_VERIYOR():
    """⚠ *Kırmızı veremeyen bir kapı, olmayan bir kapıdır.*"""
    sahte = '<p title="cube_query hatası">bir şey</p>'
    assert any(j in " ".join(_gorunur_metinler(sahte)).lower() for j in JARGON)


def test_KOD_IFADESI_METIN_SAYILMIYOR():
    """🔴 İlk sürüm `neYaptim(item.cube_query)` gibi **kodu** yakaladı — `{...}` içeren
    parça bir JS ifadesidir, kullanıcı metni değil. *Bir taramanın kendi deseni de bir
    bağımlılıktır.*"""
    kod = ">{const x = item.cube_query?.measures}<"
    assert not _gorunur_metinler(kod)


def test_HITAP_TEK():
    """⚠ `soz.py` hitabı **`sen`** olarak sabitliyor; arayüzde *"siz"* ile karışması,
    aynı ürünün iki farklı sesi olurdu.

    ⊘ **Bu kapı bugün yalnız BEYANI kilitliyor**: 42 bileşenin hitap tutarlılığını
    ölçmek bir dil analizidir ve burada **yapılmıyor** — sınır yazılı, gizli değil.
    """
    from app.soz import HITAP

    assert HITAP == "sen"
