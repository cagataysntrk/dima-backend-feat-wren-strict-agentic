"""FAZ 5.15 kapısı — **`stats.py` tekilleştirme borcu.** [bayraksız: borç]

## Ölçülmüş borç

`schedules.detect_anomalies` **hâlâ kendi ortalama/std/z-skorunu satır içi hesaplıyordu**
ve `app.stats`'ı import etmiyordu — oysa `stats.py` **tam da bu kopyayı ortadan
kaldırmak için** yazılmıştı ve kendi docstring'i şöyle diyordu:

> *"yeni bir istatistik motoru İCAT EDİLMEZ"*

Yani **niyet üç yerde yazılıydı ve bir yerde uygulanmıyordu.**

🔴 *"Anomali işine dokunan her faz bunu tekilleştirmekle yükümlüdür"* — bu deponun
**altı kez ölçülmüş** hastalığı.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from app import stats

_KOK = Path(__file__).resolve().parents[1]
_SCHEDULES = _KOK / "app/schedules.py"


def test_SCHEDULES_kendi_istatistigini_HESAPLAMIYOR():
    """🔴 Kaynak taraması: `**0.5` ve `sum(nums)/len(nums)` **yok**.

    ⚠ Tarama **kod satırlarında**, yorumlarda değil: bu dosyanın kendi yorumu kopyanın
    silindiğini **anlatıyor** ve bir alt-dize taraması kendi belgesini ölçerdi (bu
    deponun on kez ödediği ders).
    """
    kaynak = _SCHEDULES.read_text(encoding="utf-8")
    kodsuz = "\n".join(
        satir for satir in kaynak.splitlines()
        if not satir.lstrip().startswith("#"))
    # Docstring'leri de düş.
    kodsuz = re.sub(r'"""(?:.|\n)*?"""', "", kodsuz)
    for desen in ("** 0.5", "**0.5"):
        assert desen not in kodsuz, (
            f"🔴 `schedules.py` hâlâ std'yi kendi hesaplıyor ({desen!r}). "
            f"`app.stats` tam da bu kopya için var.")
    assert not re.search(r"sum\(\s*nums\s*\)\s*/\s*len\(\s*nums\s*\)", kodsuz), (
        "🔴 `schedules.py` hâlâ ortalamayı kendi hesaplıyor.")


def test_SCHEDULES_stats_i_CAGIRIYOR():
    """⚠ Belirteç **AST**: import'un varlığı, kullanıldığını kanıtlamaz."""
    agac = ast.parse(_SCHEDULES.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "detect_anomalies")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "z_skorlari" in cagrilar, (
        "🔴 `detect_anomalies` `stats.z_skorlari` ÇAĞIRMIYOR — niyet yazılı, uygulama yok.")


def test_ANOMALI_davranisi_DEGISMEDI():
    """Tekilleştirme bir **davranış değişikliği değildir** — aynı girdi, aynı çıktı."""
    from app.schedules import detect_anomalies

    rows = [{"ay": f"2026-{i:02d}", "v": v} for i, v in
            enumerate([10, 11, 10, 12, 11, 40, 10], 1)]
    out = detect_anomalies({"rows": rows}, "v", k=2.0)
    assert len(out) == 1 and "40" in out[0], out
    assert "olağandışı yüksek" in out[0]

    # `n < 4` ve `std == 0` kapıları KORUNDU.
    assert detect_anomalies({"rows": rows[:3]}, "v") == []
    duz = [{"ay": f"2026-{i:02d}", "v": 5} for i in range(1, 6)]
    assert detect_anomalies({"rows": duz}, "v") == []


def test_NONE_degerler_satir_eslemesini_BOZMAZ():
    """🔴 En kolay kaçırılan kusur: `z_skorlari` **`None`'suz** listeye indeks verir.

    Ham satır indeksine geri haritalanmazsa etiketler **yanlış satıra** yapışır — ve bu
    sessizdir: sayı doğru, adı yanlış.
    """
    from app.schedules import detect_anomalies

    rows = [{"ad": "A", "v": 10}, {"ad": "B", "v": None}, {"ad": "C", "v": 11},
            {"ad": "D", "v": 10}, {"ad": "E", "v": 12}, {"ad": "F", "v": 40}]
    out = detect_anomalies({"rows": rows}, "v", k=1.9)
    assert out and "F" in out[0], (
        f"🔴 Etiket yanlış satıra yapıştı: {out}. `None` atlanan konumlar geri "
        f"haritalanmazsa sayı doğru, ADI yanlış olur — ve bu sessizdir.")


# --- yeni yüzey: trend + ozet ------------------------------------------------------

def test_TREND_n_bes_altinda_URETILMEZ():
    """🔴 *Dört noktaya doğru çizmek, gürültüye bir yön atfetmektir* — ve o yön **her
    zaman** bulunur."""
    assert stats.trend([1, 2, 3, 4]) is None
    assert stats.trend([1, 2, 3, 4, 5]) is not None


def test_TREND_yonu_ve_uyumu():
    t = stats.trend([1, 2, 3, 4, 5])
    assert t["yon"] == "artan" and t["egim"] == 1.0 and t["r2"] == 1.0
    assert stats.trend([5, 4, 3, 2, 1])["yon"] == "azalan"
    assert stats.trend([3, 3, 3, 3, 3])["yon"] == "yatay"


def test_TREND_p_degeri_URETMEZ():
    """⚠ Bir p-değeri için gereken varsayımlar (bağımsızlık, normallik) bir zaman
    serisinde **sağlanmaz**; uydurma bir p-değeri, kalibre edilmemiş bir güven puanının
    aynısıdır (MIMARI'nin açık yasağı)."""
    t = stats.trend([1, 2, 3, 4, 5])
    assert "p" not in t and "p_value" not in t and "anlamli" not in t


def test_OZET_medyani_CIFT_gozlemde_dogru():
    """⚠ *"Alt orta"* ucuzdur ama asimetrik dağılımda **sistematik olarak yanlı**."""
    assert stats.ozet([1, 2, 3, 4])["medyan"] == 2.5
    assert stats.ozet([1, 2, 3])["medyan"] == 2
    assert stats.ozet([]) is None


@pytest.mark.parametrize("fn", ["z_skorlari", "ortalama_std", "trend", "ozet"])
def test_stats_TEK_KAYNAK_yuzeyi(fn):
    assert callable(getattr(stats, fn))
