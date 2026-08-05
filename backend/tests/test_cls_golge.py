"""**CLS GÖLGE ÖLÇÜMÜ** — §C ölçüt 4'ün ön koşulu. [bayrak: `motor_cls=shadow`]

## 🔴 `shadow` bir HİÇLİKTİ

Ölçüldü (ölçüt 4'ün **üçüncü** teşhisi): `rls.cls_manifeste_yaz` `shadow` kademesinde
manifesti **dokunmadan** döndürüyor — yani **`shadow ≡ off`**. Kademe vardı, **ölçümü
yoktu**. Ölçütün hedefi ise *"`on`; **gölge modda 7 gün · sapma 0**"*.

> 🔴 *Ölçmeyen bir gölge modu, ilerleme gibi görünen bir hiçliktir.*
> `off → shadow` yapmak, ölçmeden bir kutu işaretlemek olurdu.

## Neden kolon SAYISI değil, PLAN kıyaslanıyor

CLS `pii.py`'den **kategorik olarak farklıdır**: maskeleme kolonu **gösterir**
(`123****89`), CLS onu **plandan düşürür** — ve düşme **sessizdir**. Gölge bu yüzden iki
planı kıyaslar; **planlama hatası da bir bulgudur** (`on`'da o sorgu çalışmazdı) ve
sessizce geçmek, geçişin maliyetini **sıfır** göstermek olurdu.

## Kapanış sırası

(1) gölge ölçümü **✅ bu commit** → (2) `shadow` açılır → (3) **7 gün · sapma 0** →
(4) `on`. Üçüncü adım **beklemektir**, kod değil.
"""

from __future__ import annotations

import ast
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]


def _fn(ad: str) -> str:
    agac = ast.parse((_KOK / "app/wren_service.py").read_text(encoding="utf-8"))
    cls = next(n for n in agac.body if isinstance(n, ast.ClassDef) and n.name == "WrenService")
    return ast.unparse(next(n for n in cls.body
                            if isinstance(n, ast.FunctionDef) and n.name == ad))


def test_GOLGE_OLCUMU_VAR():
    """🔴 Önce **hiç yoktu**: `shadow` manifesti dokunmadan döndürüyordu."""
    assert "clac_manifesti" in _fn("_cls_golge_denetimi")


def test_HER_IKI_MOTOR_KAPISINDA_kosuyor():
    """⚠ `dry_plan` **ve** `query`: birinde ölçüp ötekinde ölçmemek, 7 günlük sayıyı
    **yarım** yapardı."""
    src = (_KOK / "app/wren_service.py").read_text(encoding="utf-8")
    assert src.count("self._cls_golge_denetimi(sql,") == 2


def test_KADEMEYE_BAGLI():
    src = (_KOK / "app/wren_service.py").read_text(encoding="utf-8")
    assert 'if self._cls_kademesi() == "shadow":' in src


def test_AYNI_OZELLIKLERLE_kiyasliyor():
    """🔴 Farklı özelliklerle planlanan iki SQL'i kıyaslamak, CLS farkı yerine **özellik
    farkını** ölçerdi."""
    govde = _fn("_cls_golge_denetimi")
    assert govde.count("dry_plan(sql, properties)") == 2


def test_PLANLAMA_HATASI_da_BULGU():
    """🔴 *Sessizce geçmek, `on`'a geçişin maliyetini **sıfır** göstermek olurdu.*"""
    govde = _fn("_cls_golge_denetimi")
    i = govde.index("except BaseException")
    assert "PLANLANAMAZDI" in govde[i:i + 700]


def test_AKISI_DEGISTIRMIYOR():
    """⚠ Gölge **ölçer, davranmaz**: dönüş yok, istisna yok, `resp` yok."""
    govde = _fn("_cls_golge_denetimi")
    assert "-> None" in govde.split("\n")[0]
    assert "raise" not in govde, "🔴 gölge akışı kesiyor"


def test_BaseException_yakalaniyor():
    """⚠ Rust PANIC `Exception` **değildir** — kardeş desenin kendi dersi."""
    assert "except BaseException" in _fn("_cls_golge_denetimi")


def test_KAYIT_YERI_KARDESIYLE_ayni():
    """⚠ İkinci bir JSONL **açılmadı**: gölge bulgularının bu depoda zaten bir sahibi var
    ve ikincisi *"aynı kuralın iki sahibi"* olurdu. 7 günlük ölçüt aynı greple ölçülür."""
    govde = _fn("_cls_golge_denetimi")
    assert "_log.warning" in govde and "CLS (gölge)" in govde
    # ⚠ **Kelime değil DOSYA YAZMA** aranır: ilk sürüm `"jsonl" not in govde` yazdı ve
    # kendi gerekçe cümlesini (*"ikinci bir JSONL açılmadı"*) yakaladı — bu operasyonda
    # **on ikinci** kez bir tarama kendi belgesini ölçtü.
    assert ".jsonl" not in govde and "open(" not in govde, (
        "🔴 gölge ikinci bir kayıt mekanizması açmış — aynı kuralın iki sahibi")


def test_MALIYET_IDDIASI_GERCEK():
    """🔴 **Belgemi düzelttim.** İlk yazımda *"ucuz ön eleme (kardeş desen)"* yazdım ve
    **uygulamadım**: RLS `alwaysFilter` baytını tarayabiliyor, CLS'in sınıflandırması ise
    **ad tabanlıdır** ve manifestte taranacak bir işaret **yok**.

    *Belgede olup kodda olmayan bir iyileştirme, kodda olmayan bir iyileştirmeden
    kötüdür — çünkü var sanılır.*

    Gerçek çözüm **bellekleme**: `json.loads` manifest başına **bir kez**.
    """
    src = (_KOK / "app/wren_service.py").read_text(encoding="utf-8")
    assert "_CLAC_ONBELLEK" in src
    govde = _fn("_cls_golge_denetimi")
    assert "_CLAC_ONBELLEK[anahtar]" in govde
    # ⚠ Yine **kelime değil**: belgede o ifade artık *düzeltmenin kendisini* anlatıyor.
    # Ölçülen şey iddianın **kodda karşılığı**: bellekleme var mı.
    assert "hashlib.sha256(ham)" in govde, "🔴 bellekleme anahtarı yok — iddia karşılıksız"


def test_ONBELLEK_SINIRLI():
    """⚠ Sınırsız bir sözlük, uzun ömürlü bir süreçte **sessiz bir sızıntıdır**."""
    govde = _fn("_cls_golge_denetimi")
    assert "_CLAC_ONBELLEK.clear()" in govde


def test_KAPANIS_SIRASI_yazili():
    """⊘ (3) *"7 gün · sapma 0"* **beklemektir**, kod değil."""
    doc = __doc__ or ""
    assert "beklemektir" in doc and "sapma 0" in doc
