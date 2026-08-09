"""🔴🔴 **ARAÇ BEYANI BİR BELGE DEĞİL, BİR SÖZLEŞMEDİR.**

## Bu kapı ölçülmüş bir yalandan doğdu

`tools.KAYIT`'taki `girdi` alanı LLM'e giden `input_schema`'ya çevriliyor
(`tools.py::arac_semasi`). Yani model o adlara göre çağrı kuruyor. Ölçüldü (2026-08-09,
`FAZ O` demeti — 25 aracın hepsi `inspect.signature` ile karşılaştırıldı):

| araç | beyan | gerçek imza | sonuç |
|---|---|---|---|
| `prescribe.recete` | `{signals, cube_query}` | `recete(rapor, *, lower_is_better…)` | 🔴 `TypeError` |
| `schedules.uyari_nedeni` | `{result, measure}` | `uyari_nedeni(svc, cq, threshold)` | 🔴 `TypeError` |
| `viz.recommend` | `…, cube_meta` | `recommend(result, units, lower_set, cube_query…)` | 🔴 `TypeError` |
| `narration_guard.dogrula` | `…, ek` | `dogrula(…, *, ek_degerler…)` | 🔴 ad kayması |
| `statements.resolve` · `kpi.resolve` · `report.compose` | `svc`/`service`/`schema` yok | zorunlu | ⚠ enjeksiyon, beyansız |

⊙ Yedisi de **fark edilmemişti** çünkü bu araçların çoğu *"zaten var ama kayıtsız"* turunda
**sıfır yeni kod** ilkesiyle yazıldı — yani hiç **çağrılmadılar**. Beyan doğru sanıldı,
çünkü kimse denemedi.

## İki ayrı sınıf — ve `enjekte` olmadan ayırt edilemezler

| durum | anlamı |
|---|---|
| `girdi`de var, imzada **yok** | 🔴 **her zaman kusur** — model o adı yazarsa çağrı patlar |
| imzada **zorunlu**, `girdi`de yok | `enjekte` ise meşru (istek kapsamı), değilse kusur |

`svc`/`service`/`schema` gibi parametreleri `girdi`ye yazmak modele *"bir motor nesnesi
uydur"* demek olurdu. `Arac.enjekte` o ayrımı **beyan edilebilir** yapar.

## ⚠ Ne ölçmüyor — sınırı yazılı

Tip uyumunu ölçmüyor (`girdi` değerleri serbest Türkçe açıklama). Yalnız **ad kümesini**
ölçüyor. Ad yanlışsa çağrı **kesin** patlar; ad doğru ama tip yanlışsa patlamayabilir —
bu kapı ucuz ve kesin olanı alır.

*Bir sözleşmeyi hiç sınamamak, onu yazmamaktan kötüdür: yazılı olan güvenilir sanılır.*
"""

from __future__ import annotations

import importlib
import inspect

import pytest

from app import tools

#: `servis:*` bağlı araçlar bir SINIFIN metodudur; `self` sayılmaz.
_SERVIS_SINIFI = {
    "servis:wren": ("app.wren_service", "WrenService"),
}


def _imza(a: tools.Arac):
    """Aracın gerçek çağrılabilirinin imzası — ya da `None` (çözülemedi/ördek-tipli)."""
    if a.baglanma == "servis:llm":
        return None      # sağlayıcı değişir (ördek-tipli); tek bir imza YOK
    if a.baglanma == "modul":
        m = importlib.import_module(a.modul)
        f = getattr(m, a.fonksiyon, None)
        return inspect.signature(f) if callable(f) else None
    modul, sinif = _SERVIS_SINIFI[a.baglanma]
    f = getattr(getattr(importlib.import_module(modul), sinif), a.fonksiyon.split(".")[-1], None)
    return inspect.signature(f) if callable(f) else None


_ARACLAR = [a for a in tools.KAYIT if a.modul and a.fonksiyon]


@pytest.mark.parametrize("a", _ARACLAR, ids=[a.ad for a in _ARACLAR])
def test_BEYAN_EDILEN_HER_ALAN_IMZADA_VAR(a: tools.Arac):
    """🔴 Modele yazdırdığın bir adın karşılığı yoksa, çağrı **kesin** patlar."""
    sig = _imza(a)
    if sig is None:
        pytest.skip(f"{a.ad}: tek bir imzası yok ({a.baglanma})")
    par = set(sig.parameters) - {"self"}
    # `**kwargs` kabul eden bir fonksiyon her adı yutar — orada iddia edilemez.
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        pytest.skip(f"{a.ad}: `**kwargs` var, ad kümesi kısıtlanamaz")
    fazla = set(a.girdi or {}) - par
    assert not fazla, (
        f"🔴 `{a.ad}` beyanında olup imzada OLMAYAN alan(lar): {sorted(fazla)}.\n"
        f"   imza: {sorted(par)}\n"
        "Bu alan LLM'e `input_schema` olarak gidiyor; model onu yazarsa `TypeError`.")


@pytest.mark.parametrize("a", _ARACLAR, ids=[a.ad for a in _ARACLAR])
def test_ZORUNLU_PARAMETRE_YA_BEYANLI_YA_ENJEKTE(a: tools.Arac):
    """⚠ Zorunlu bir parametre ya modelden ya çalıştırıcıdan gelir — **üçüncüsü yok**."""
    sig = _imza(a)
    if sig is None:
        pytest.skip(f"{a.ad}: tek bir imzası yok ({a.baglanma})")
    zorunlu = {
        n for n, p in sig.parameters.items()
        if p.default is inspect.Parameter.empty and n != "self"
        and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
    }
    acikta = zorunlu - set(a.girdi or {}) - set(a.enjekte or ())
    assert not acikta, (
        f"🔴 `{a.ad}`: zorunlu ama ne beyanlı ne enjekte: {sorted(acikta)}.\n"
        "Modelden gelecekse `girdi`ye, istek kapsamından gelecekse `enjekte`ye yaz. "
        "Yazılmayan bir zorunluluk, çağrı anında bulunur.")


@pytest.mark.parametrize("a", _ARACLAR, ids=[a.ad for a in _ARACLAR])
def test_ENJEKTE_EDILEN_AD_IMZADA_VAR(a: tools.Arac):
    """⚠ Enjeksiyon listesi de bayatlar — bir parametre yeniden adlandırılırsa."""
    sig = _imza(a)
    if sig is None or not a.enjekte:
        pytest.skip("enjeksiyon yok ya da imza tekil değil")
    yok = set(a.enjekte) - (set(sig.parameters) - {"self"})
    assert not yok, f"🔴 `{a.ad}`: `enjekte` içinde imzada olmayan ad(lar): {sorted(yok)}"


def test_KAPI_GERCEKTEN_KAPI_MI():
    """🔴 Meta-kapı: yüklem gerçek bir uyuşmazlığı görüyor mu?

    Bu olmasaydı kapı bir gün sessizce **her şeyi onaylayan** bir kapıya dönüşürdü —
    bu depoda ölçülmüş bir desen (*sistem bozulurken sayı iyileşir*).
    """
    sahte = tools.Arac(
        ad="sahte", ozet="x", girdi={"hic_olmayan_alan": "x"}, cikti="x",
        determinizm="deterministik", maliyet="sifir", yan_etki="yok",
        izin="query:run", makbuz=None, modul="app.ilkeller", fonksiyon="bagla")
    with pytest.raises(AssertionError, match="hic_olmayan_alan"):
        test_BEYAN_EDILEN_HER_ALAN_IMZADA_VAR(sahte)
