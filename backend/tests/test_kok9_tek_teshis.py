"""🔴 KÖK-9 / KÇ-5 — **TEK TEŞHİS KAYNAĞI.** (denetim raporu KN-5)

## Ölçülen kusur

⊙ 2 116 reddedilen soruda, ham kapı kodu R10 (kapsam) **olmadığı hâlde** tanınmayan
kelime **vardı**: **914 soru — %43,2.**

| ham kod | ayrışık | örnek |
|---|---|---|
| `R1` | **646** | `ocaka mai ntenance cost…` → gerçek sorun: `mai` · `ntenance` · `cost` |
| `R2` | 149 | `net pay artmadı mı listele…` → `artmadi` · `alti` |
| `R4` | 61 | `ocaktan siparis ortlaamasi…` → `ortlaamasi` |
| `R9` | 44 | `enerji yoğunluğu 2025'tea göre…` → `tea` · `alemde` |

Telemetri *"cube eşleşmedi"* (R1) diyordu; **gerçek sorun kullanıcının yazdığı
kelimelerdi**. Ve bu kodları okuyan araçlar (`lab/r1_envanteri.py` · `lab/risk_kapsam.py`)
**geliştirme önceliğini** ona göre çıkarıyordu.

> 🔴 Raporun cümlesi: *"Kusuru gizlemekten daha kötüsü, YANLIŞ YERİ işaret etmektir."*
> Burada yanlış yer gösterilen **kullanıcı değil, geliştiriciydi** — kullanıcıya giden
> mesaj (`partial_unknowns` üzerinden) zaten dürüsttü.

## ⚠ Neden R10 kapı sırasında ÖNE ALINMADI

Raporun önerisi *"R10'u başa al"*dı. **Uygulanamaz:** kapsam denetimi `known_words` ister
ve o küme R1…R9'un yaptığı EŞLEŞMELERDEN doğar. R10 en sonda çünkü **ötekilerin çıktısına
bağımlı**; sırayı çevirmek eşleştirmeyi ikinci kez yazmak olurdu — deponun ölçülmüş
*"aynı kuralın iki sahibi"* sınıfı.

🔴 Doğru çözüm sırayı değil **kaynağı** tekleştirmek.
*İki sayı ayrışıyorsa çare ikisini de düzeltmek değil, birini ötekinden türetmektir.*
"""

from __future__ import annotations

import ast
import pathlib

import pytest

import app.cube_router as cr

#: Ölçülen dört ayrışık vaka — her biri farklı bir ham koddan.
AYRISIK = [
    "ocaka mai ntenance cost bizi hangi eden asagi cekiyo",
    "net pay artmadi mi listele 50.000 alti",
    "top lam brut gecen aya gore ne alemde",
    "enerji yogunlugu 2025'tea gore ne alemde getir",
]


@pytest.mark.parametrize("q", AYRISIK)
def test_TESHIS_TANINMAYAN_KELIMEYI_SOYLUYOR(q, schema):
    """🔴 **ASIL KAPI**: reddin gerekçesi, kullanıcıya söylenenle **aynı hesaptan**."""
    if cr.route(q, schema) is not None:
        pytest.skip(f"⊘ vaka bayatlamış — artık cevaplanıyor: {q}")
    bilinmeyen, _ = cr.partial_unknowns(cr._norm(q), schema)
    assert bilinmeyen, "⊘ vaka bayatlamış: artık tanınmayan kelime yok"
    assert cr.teshis(q, schema) == "R10", (
        f"🔴 «{q}» → teşhis {cr.teshis(q, schema)}, oysa anlaşılmayan kelime var: "
        f"{bilinmeyen[:3]}")


def test_TANINAN_SORUDA_HAM_KOD_KORUNUYOR(schema):
    """⚠ Ters yön: tanınmayan kelime **yoksa** ham kapı kodu **olduğu gibi** kalır.
    Her reddi R10 yapmak, teşhisi ikinci kez yanlış yapardı."""
    q = "mart cirosunu subata gore kiyasla"
    if cr.route(q, schema) is not None:
        pytest.skip("⊘ vaka bayatlamış")
    bilinmeyen, _ = cr.partial_unknowns(cr._norm(q), schema)
    if bilinmeyen:
        pytest.skip(f"⊘ bu soruda da tanınmayan kelime var: {bilinmeyen}")
    assert cr.teshis(q, schema) == cr.red_gerekcesi()


def test_ROUTE_BASARILIYSA_TESHIS_YOK(schema):
    """🔴 `route()` cevap ürettiyse teşhis **`None`** — bu kolonun doluluğu doğrudan
    *"deterministik yoldan çıkamayan sorular"* kümesini verir; bir cevaba gerekçe
    yazmak o kümeyi kirletirdi."""
    assert cr.route("bu yil toplam ciro", schema) is not None, "⊘ vaka bayatlamış"
    assert cr.teshis("bu yil toplam ciro", schema) is None


def test_HAM_KOD_SILINMEDI():
    """⚠ `red_gerekcesi()` ve `_reddet` zinciri **duruyor** — *kapananlar işaretlenir,
    silinmez* (MIMARI §10). Değişen tek şey telemetrinin hangisini yazdığı."""
    assert hasattr(cr, "red_gerekcesi") and hasattr(cr, "teshis")
    kaynak = pathlib.Path(cr.__file__).read_text(encoding="utf-8")
    assert kaynak.count('_reddet("R') > 5, "🔴 ham kod zinciri budanmış"


def test_TELEMETRI_TESHISI_YAZIYOR():
    """🔴 Yazma noktası kapıya bağlı: `answer.py` `reject_reason`a **`teshis()`** yazmalı.
    Ham koda geri dönülürse `lab/r1_envanteri.py` yine yanlış yeri işaret eder."""
    src = (pathlib.Path(cr.__file__).parent / "answer.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    yazim = [n for n in ast.walk(agac)
             if isinstance(n, ast.keyword) and n.arg == "reject_reason"]
    assert yazim, "⊘ `reject_reason` yazımı bulunamadı — kapı bayatlamış"
    metin = ast.unparse(yazim[0].value)
    assert "teshis" in metin, f"🔴 telemetri ham kodu yazıyor: {metin}"


def test_SEMA_OKUNAMAZSA_HAM_KODA_DUSUYOR(schema):
    """⚠ Teşhis bir **kayıt yazarken** koşuyor. Şema okunamıyorsa telemetriyi kaybetmek
    yerine ham koda düşmek doğrudur. *Bir kayıt satırı, kaydettiği şeyden daha kırılgan
    olmamalıdır.*"""
    assert cr.route("zombixyz ne kadar", schema) is None, "⊘ vaka bayatlamış"
    ham = cr.red_gerekcesi()
    assert cr.teshis("zombixyz ne kadar", {}) == ham
