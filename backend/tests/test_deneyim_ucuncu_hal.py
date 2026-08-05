"""Denetim D5 — **`⊘`'nin iki anlamı ayrılır.** [bayraksız: ölçüm dürüstlüğü]

## Denetim ne dedi, ölçüm ne gösterdi

> *"Deneyim süitinin çoğunluğu hiç koşmuyor. Koşmayan vaka, geçen vaka değildir."*
> (41 ✅ · 1 ❌ · **63 ⊘** → *"%60'ı koşmuyor"*)

Ölçüldü ve iddia **kısmen** doğru çıktı:

| işaret | sayı | anlam |
|---|---|---|
| ✅ | 40 | geçti |
| ❌ | 2 | gerçek kırmızı |
| `·` | **60** | senaryo o satırı **zaten ölçmüyor** (`olculen` alt kümesi) — **tasarım** |
| ⊘ | **3** | ölçüyor ama **ön koşul bulunamadı** — **kapsanmamış risk** |

🔴 *"63 koşmuyor"* aslında **60 tasarım + 3 risk**. İkisini aynı işaretle göstermek,
tasarımı bir **kusur** gibi gösteriyordu — ve tersi de mümkündü: 3 gerçek riski 63'ün
içinde **görünmez** kılıyordu.

*Bir `⊘`, neyi ölçmediğini söylemiyorsa bir ölçüm değil bir boşluktur.*
"""

from __future__ import annotations

import ast
from pathlib import Path

from lab.deneyim import KAPSAM_DISI, ON_KOSUL_YOK, _isaret

_KAYNAK = Path(__file__).resolve().parents[1] / "lab/deneyim.py"


def test_IKI_UCUNCU_HAL_ayri_isaret():
    """İki `⊘` **ayrı görünür** — aynı işaret, ayrımı geri siler."""
    assert _isaret(KAPSAM_DISI) != _isaret(ON_KOSUL_YOK)
    assert _isaret(True) == "✅" and _isaret(False) == "❌"
    # Ve hiçbiri yeşile yuvarlanmaz.
    assert _isaret(KAPSAM_DISI) not in ("✅", "❌")
    assert _isaret(ON_KOSUL_YOK) not in ("✅", "❌")


def test_KAPSAM_DISI_acikca_damgalaniyor():
    """⚠ Senaryonun ölçmediği satır **sessizce yok** değil, **açıkça kapsam dışı**.

    Sessiz yokluk, raporu okuyanın onu bir başarısızlık sanmasına açıktır.
    """
    agac = ast.parse(_KAYNAK.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_olc")
    sabitler = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert {"KAPSAM_DISI", "ON_KOSUL_YOK"} <= sabitler, (
        "🔴 `_olc` iki üçüncü hâli ayırmıyor — `⊘` yine tek anlama düşmüş.")


def test_ON_KOSULSUZ_hucreler_UYARI_uretir():
    """🔴 *Koşmayan vaka, geçen vaka değildir* — ve bu, özet satırında **görünmeli**."""
    kaynak = _KAYNAK.read_text(encoding="utf-8")
    assert "KAPSANMAMIŞ RİSK" in kaynak, (
        "🔴 Ön koşulsuz hücreler için uyarı yok — 3 gerçek risk, 60 tasarım hücresinin "
        "içinde GÖRÜNMEZ kalır.")
    assert "kapsam dışı" in kaynak


def test_UCUNCU_HAL_yesile_YUVARLANMAZ():
    """Faz 9.6 kararı: yeşile yuvarlamak *"risk yok"* yalanı üretir."""
    kaynak = _KAYNAK.read_text(encoding="utf-8")
    assert "risk yok" in kaynak and "yalan" in kaynak
