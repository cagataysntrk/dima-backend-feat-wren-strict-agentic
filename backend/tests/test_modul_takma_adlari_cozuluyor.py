"""🔴 **ÇÖZÜLMEYEN İSİM YOK** — `F821`, ve sıfır tabanla.

## Bu kapı ölçülmüş dört kusurdan doğdu, ve ikisi ÜRÜN kusuruydu

`O-4`'te `ask.py`'ye bir çağrı yazıldı, importu unutuldu ve canlı `curl` turunun
**birinci** sorusunda patladı. Elle bir AST kapısı yazdım; o kapı **ikinci** kusuru
(`trace`) kaçırdı — çünkü modül geneline bakıyordu, **kapsama** değil. Sonra `ruff`'ın
`F821`'i denendi ve ikisini de tek satırda buldu — üstüne **beş** tane daha:

| yer | isim | sonuç |
|---|---|---|
| `ask.py:3799` | `_plan_tuketici` | 🔴 `NameError` — benim kusurum, canlı yakalandı |
| `ask.py:3804` | `trace` | 🔴 `NameError` — elle yazdığım kapı **göremedi** |
| `ask.py:1391…1401` | `_MAX_UPLOAD` · `_UPLOAD_DIR` | 🔴🔴 **`POST /ask/upload` HER İSTEKTE 500** *(canlı doğrulandı)* |
| `ask.py:394` | `_answer_from_cube_query` | 🔴 çapraz-alan pilotu cevap üretirse çöker |
| `answer.py:192` | `AskRequest` | ⚠ yalnız açıklama (annotation) — çökmez, ama yanlış |

⊙ **`/ask/upload` bir demet boyunca değil, kim bilir ne kadardır kırıktı** ve süit onu
hiç görmedi. Bu, deponun kendi yazılı dersinin (*"bir HTTP ucu bir demet boyunca kırıktı
ve kimse görmedi"*) birebir tekrarı.

## Neden `ruff`, neden elle yazılmış bir yüklem DEĞİL

Elle yazdığım kapı çalışıyordu — ama **kapsam bilmiyordu**. `ruff` Python'un kapsam
kurallarını zaten uyguluyor. İkisini birlikte tutmak `KAT-1` olurdu: aynı kuralın iki
sahibi, biri **eksik**. Zayıf olan kaldırıldı.

*Kendi yazdığın bir yüklem, kaçırdığını sana söylemez; kaçırdığını ancak onu geçen bir
kusur söyler.*

## Taban SIFIR — ve sıfır kalmalı

Yedi bulgunun **yedisi de düzeltildi**. Bir muafiyet listesi bilerek yok: bir istisna
listesi olsaydı, sıradaki `NameError` oraya yazılarak susturulabilirdi.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[1]
#: ⚠ `tests` de dahil — ve bu bir ölçümden geldi: `test_plan_tuketici.py`'de `import json`
#: unutuldu, hata **fail-open bir `except`e düştü** ve test *"cevap None döndü"* diye
#: kırıldı. Yani asıl sebep bir başka kusur gibi göründü. *Fail-open bir dal, içindeki
#: isim hatasını da açık bırakır — o yüzden isimler dalın DIŞINDA doğrulanmalıdır.*
ALANLAR = ("app", "control_plane", "admin_app", "lab", "eval", "tests")


def _f821(hedefler: list[str]) -> str:
    p = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--no-cache",
         "--output-format=concise", "--select", "F821", *hedefler],
        cwd=BACKEND, capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def test_COZULMEYEN_ISIM_YOK():
    """🔴 `NameError` bir çalıştırma sürprizi değil, **okunabilir** bir gerçektir."""
    cikti = _f821([a for a in ALANLAR if (BACKEND / a).is_dir()])
    satirlar = [s for s in cikti.splitlines() if ": F821" in s]
    assert not satirlar, (
        "🔴 Çözülemeyen isim(ler) — o satır koştuğu an `NameError`:\n"
        + "\n".join(satirlar)
        + "\n\nBir bayrak kapalı olsa bile patlar: çağrı koşulsuzdur.\n"
          "⚠ Bu kapının muafiyet listesi YOKTUR ve olmamalıdır — bir istisna listesi, "
          "sıradaki `NameError`'ın susturulacağı yerdir.")


def test_KAPI_GERCEKTEN_KAPI_MI(tmp_path):
    """⚠ Meta-kapı: yüklem **gerçek bir eksiği** yakalıyor mu?

    Bu olmasaydı kapı bir gün sessizce **her şeyi onaylayan** bir kapıya dönüşür ve
    yeşil kalarak yanlış bir güven üretirdi (bu depoda ölçülmüş bir desen: *sistem
    bozulurken sayı iyileşir*).
    """
    kotu = tmp_path / "kotu.py"
    kotu.write_text("def f():\n    return _hic_olmayan.bir_sey()\n", encoding="utf-8")
    assert "F821" in _f821([str(kotu)]), "kapı sahte bir eksiği bile görmedi"

    iyi = tmp_path / "iyi.py"
    iyi.write_text("def f():\n    _x = 1\n    return _x\n", encoding="utf-8")
    assert "F821" not in _f821([str(iyi)]), "yerel değişken çözülemedi sanıldı"
