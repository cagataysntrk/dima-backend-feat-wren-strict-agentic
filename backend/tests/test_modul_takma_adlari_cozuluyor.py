"""🔴 **BİR MODÜL TAKMA ADI, KULLANILDIĞI YERDE TANIMLI MI?**

## Neden bu kapı var — ölçülmüş bir kusurdan doğdu

`O-4`'te `ask.py`'ye `_plan_tuketici.cevap(...)` yazıldı ve **importu unutuldu**. Sonuç:

    NameError: name '_plan_tuketici' is not defined   (ask.py:3799, CANLI)

⊙ Ve bunu **hiçbir şey görmedi**:
* `import app.routers.ask` **başarılı** — `NameError` modül yüklenirken değil, o
  fonksiyon **koştuğunda** doğar.
* Hedefli testler **yeşil** — dal `_try_fresh_intent` içinde ve oraya ancak gerçek bir
  LLM turuyla girilir; süitin hiçbir testi oraya girmiyor.
* Bayrak **kapalıydı** ve yine de patladı: çağrı koşulsuz, `None` dönüşü içeride
  kararlaşıyordu. Yani `KURAL B` bir **isim hatasıyla** çiğnendi.

Kusur canlı `curl` turunda, birinci soruda çıktı.

## Ne ölçüyor — ve neden yanlış-pozitif üretemez

Modül **gerçekten import edilir**, sonra kaynağındaki `_ad.oznitelik` biçimindeki her
kullanım için `hasattr(modül, "_ad")` sorulur. Yani bu bir sezgi değil, **çalıştırılmış
bir gerçektir** (`§101.1`: kendi yanlış-pozitifini üreten bir yüklem, kusurdan pahalıdır).

⚠ Yalnız `_` ile başlayan adlar bakılır: yerel değişkenler de `_` ile başlayabilir, bu
yüzden **atanan** her ad hariç tutulur. Geriye yalnız *"hiçbir yerde atanmamış ama
kullanılmış"* adlar kalır — bir modül takma adının tam tanımı.

*Bir ismin çözülüp çözülmediğini, o satır koşana kadar bekleyerek öğrenmek, en pahalı
öğrenme biçimidir.*
"""

from __future__ import annotations

import ast
import importlib
import pathlib

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app"

#: Bu kusur sınıfının yaşadığı yerler: **büyük** ve **çok takma adlı** modüller.
MODULLER = [
    ("app.routers.ask", APP / "routers" / "ask.py"),
    ("app.cube_router", APP / "cube_router.py"),
    ("app.answer", APP / "answer.py"),
    ("app.llm", APP / "llm.py"),
]


def _cozulmemis(kaynak: str, modul) -> set[str]:
    agac = ast.parse(kaynak)
    atanan: set[str] = set()
    kullanilan: set[str] = set()
    for d in ast.walk(agac):
        if isinstance(d, ast.Name) and isinstance(d.ctx, (ast.Store, ast.Del)):
            atanan.add(d.id)
        elif isinstance(d, (ast.Import, ast.ImportFrom)):
            atanan |= {(a.asname or a.name).split(".")[0] for a in d.names}
        elif isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            atanan.add(d.name)
        elif isinstance(d, ast.arg):
            atanan.add(d.arg)
        elif isinstance(d, ast.ExceptHandler) and d.name:
            atanan.add(d.name)
        elif isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name):
            if d.value.id.startswith("_"):
                kullanilan.add(d.value.id)
    return {a for a in kullanilan - atanan if not hasattr(modul, a)}


@pytest.mark.parametrize("ad,yol", MODULLER, ids=[m[0] for m in MODULLER])
def test_KULLANILAN_HER_TAKMA_AD_TANIMLI(ad: str, yol: pathlib.Path):
    """🔴 `_ad.oznitelik` yazılmışsa `_ad` **gerçekten** çözülebilmeli."""
    modul = importlib.import_module(ad)
    eksik = _cozulmemis(yol.read_text(encoding="utf-8"), modul)
    assert not eksik, (
        f"🔴 `{ad}` içinde çözülemeyen modül takma adı: {sorted(eksik)}.\n"
        "Kullanılmış ama hiçbir yerde atanmamış/import edilmemiş — o satır koştuğu an "
        "`NameError`. Bir bayrak kapalı olsa bile patlar: çağrı koşulsuzdur.")


def test_KAPI_GERCEKTEN_KAPI_MI():
    """⚠ Meta-kapı: yüklem **gerçek bir eksiği** yakalıyor mu?

    Bu olmasaydı, `_cozulmemis` bir gün boş küme döndürmeye başlar ve kapı sessizce
    **her şeyi onaylayan** bir kapıya dönüşürdü.
    """
    import app.routers.ask as _m
    sahte = "def f():\n    return _hic_olmayan_modul.bir_sey()\n"
    assert _cozulmemis(sahte, _m) == {"_hic_olmayan_modul"}
    assert _cozulmemis("def f():\n    _x = 1\n    return _x.y\n", _m) == set(), (
        "yerel değişken takma ad sanıldı — yanlış-pozitif")
