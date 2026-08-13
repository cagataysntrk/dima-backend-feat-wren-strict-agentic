r"""🔴 **SOĞUK BAŞLANGIÇ ISITMASI** — kapının göremediği bir ürün kusuru 🅖.

## Ölçülen hikâye

`§18.7`'nin çok görünümlü temsili erişimi **`%68,4 → %89,5`** çıkardı. Bedeli:

| | önce | sonra |
|---|---|---|
| indeks kurulumu (ilk istek) | 1.514 ms | **24.167 ms** |
| ılık `p95` | 49,23 ms | 53,88 ms *(eşik 300 ✅)* |

🔴 **Ve `FAZ 5` kapısı `②` bunu göremiyordu**: eşik `p95`'e bakar, `p95` **ılık**
dağılımın ölçüsüdür ve ilk isteği tanım gereği saymaz. Yani kapı yeşildi, kullanıcı
**25 saniye** bekliyordu. *Bir ölçütün kapsamı dışındaki kusur, o ölçüt için yok
hükmündedir* 🅣.

Çözüm ölçüldü: ısıtma `main.py`'nin `lifespan`'ine kondu (arka plan iş parçacığı).
Isıtmadan sonra **ilk kullanıcı isteği 55,0 ms** (ölçüldü, aynı koşumda).

## Bu kapı neyi tutuyor

Isıtmanın **varlığını** değil — bir `_warm(...)` satırı yazmak kolaydır ve **sessizce
hiçbir şey yapmayabilir** 🅯. İki değişmez:

* **sıra**: gömücü hazır değilken `ara()` vektör ayağını atlar ve indeks **kurulmaz**;
  ısıtma önce `_embedder()`'ı çağırmalı.
* **hata yutmama**: ısıtma düşerse **nedeni görünmeli** (ADR-0020) — düşen ve susan bir
  ısıtma, hiç yazılmamış bir ısıtmadan **daha kötüdür**: yokluğu fark edilmez.
"""

from __future__ import annotations

import ast
import pathlib

_MAIN = pathlib.Path(__file__).resolve().parents[1] / "app" / "main.py"


def _isitma_govdesi() -> ast.FunctionDef:
    """`_oneri_indeksi` düğümünü **`ast` ile** bul — metin araması yorumları da yakalar ②."""
    agac = ast.parse(_MAIN.read_text(encoding="utf-8"))
    for d in ast.walk(agac):
        if isinstance(d, ast.FunctionDef) and d.name == "_oneri_indeksi":
            return d
    raise AssertionError(
        "🔴 `main.py` öneri indeksini ISITMIYOR — ilk yazan kullanıcı 24 sn bekler. "
        "Kapı `p95` bunu göremez: `p95` ılık dağılımın ölçüsüdür 🅣.")


def test_ONERI_INDEKSI_ISITILIYOR():
    """🔴🔴 **ASIL KAPI.** Isıtma var **ve çağrılıyor**.

    ⚠ Tanımlanıp çağrılmayan bir ısıtma, yazılmamış bir ısıtmadır 🆌 — ve okuyan onu
    yazılmış sanar.
    """
    _isitma_govdesi()
    kaynak = _MAIN.read_text(encoding="utf-8")
    assert "_warm(_oneri_indeksi)" in kaynak, (
        "🔴 `_oneri_indeksi` **tanımlı ama çağrılmıyor** — kurmak çalıştırmak değildir 🆌.")


def test_ISITMA_GOMUCUYU_ONCE_BEKLER():
    """🔴 **SIRA DEĞİŞMEZİ.** Gömücü hazır değilken `ara()` vektör ayağını **atlar** ve
    indeks kurulmaz — o hâlde ısıtma koşar, log basar, ve **hiçbir şey ısıtmaz** 🅯.

    🅑 Mutasyon: gövdedeki `_embedder()` kontrolü kaldırılırsa bu yüklem kırılır.
    """
    fn = _isitma_govdesi()
    cagrilar = [d.func.id for d in ast.walk(fn)
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Name)]
    assert "_embedder" in cagrilar, (
        "🔴 ısıtma gömücüyü beklemiyor — gömücü yüklenmeden `ara()` çağrılırsa vektör "
        "ayağı atlanır ve indeks KURULMAZ; ısıtma sessizce boşa koşar.")

    # ⚠ Ve `ara` **gerçekten** çağrılmalı: indeksi kuran şey odur.
    nitelikli = [f"{d.func.value.id}.{d.func.attr}" for d in ast.walk(fn)
                 if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                 and isinstance(d.func.value, ast.Name)]
    assert "oneri.ara" in nitelikli, (
        "🔴 ısıtma indeksi kurmuyor — `oneri.ara(...)` çağrılmalı.")


def test_ISITMA_HATASI_SESSIZ_DEGIL():
    """ADR-0020. Düşen ve **susan** bir ısıtma, hiç yazılmamış olandan kötüdür: yokluğu
    fark edilmez ve kusur bir kullanıcı şikâyetiyle geri döner 🅖."""
    fn = _isitma_govdesi()
    kacirilan = [d for d in ast.walk(fn) if isinstance(d, ast.ExceptHandler)]
    assert kacirilan, "🔴 ısıtma korumasız — düşerse uygulama açılışını bozar."
    for h in kacirilan:
        govde = ast.unparse(h)
        assert "_log." in govde, (
            "🔴 ısıtma istisnası **kütüksüz** yutuluyor (ADR-0020): duyurulmayan bir "
            "hata, olmamış bir hatadan ayırt edilemez.")


def test_COK_KIRACILI_EKSIK_YAZILI():
    """🅖🅗 **Eksiği yayına yaz.** Isıtılan şey **varsayılan** projenin indeksidir; başka
    bir tenant'ın indeksi hâlâ ilk istekte kurulur. Bu bir eksik ve **gizlenmemeli** —
    gizlenirse bir gün *«ısıtma var»* denip çok kiracılı kusur aranmaz.
    """
    fn = _isitma_govdesi()
    belge = ast.get_docstring(fn) or ""
    assert "tenant" in belge.lower(), (
        "🔴 çok kiracılı sınır yazılı değil — ödenmeyecek borcun **nedeni yazılır** 🅗.")
