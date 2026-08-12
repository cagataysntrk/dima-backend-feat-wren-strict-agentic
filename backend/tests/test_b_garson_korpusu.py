r"""🔴🔴 `§B.6/②` · `A1` — **GARSON KORPUSU**: kapı `route()`'u ölçüyordu, garsonu değil.

Deponun **kendi** ilan ettiği ön koşul (`demo/packs/features.yml:222`):

> *«kapı `route()`'u ölçer, **garsonu ölçmez** — bu bayrağın gerilemesi kapıda
> **GÖRÜNMEZ**.»*

`§B.5` ölçtü: garson **geliştirilmiş** (istem 161 satır · tool-calling · few-shot ·
`consistency_k=3` · oylama · şema daraltma) ama **ölçülmüyor**.

> 🆕 *Ölçülmeyen bir bileşen geliştirilebilir ama iyileştirilemez.*

✅ `lab/garson_korpusu.py` — **kuru mod varsayılan**, `E-8` korunur, payda ayrı.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

_KOK = pathlib.Path(__file__).resolve().parents[1]


def test_KOSUCU_VAR_ve_KURU_MOD_VARSAYILAN():
    """🔴 Varsayılan koşum **hiçbir LLM çağırmamalı** — yoksa bir CI koşumu sessizce
    kota harcar."""
    from lab import garson_korpusu

    assert inspect.signature(garson_korpusu.kos).parameters["canli"].default is False
    govde = inspect.getsource(garson_korpusu.kos)
    kuru = govde.split("if not canli:")[1].split("return rapor")[0]
    assert "build_generator" not in kuru and "select_cube" not in kuru, (
        "🔴 kuru dalda LLM izi var — kuru mod adını hak etmiyor.")


def test_SAGLAYICI_YOKSA_KOSMUYOR():
    """🔴🔴 **ASIL GÜVENLİK YÜKLEMİ.** `nl_accuracy`'nin dersi: *«sessizce `rule` ile
    koşan bir kazanç ölçümü, hiç koşmamaktan kötüdür çünkü bayrak kararı ona dayanır.»*
    """
    from lab import garson_korpusu

    govde = inspect.getsource(garson_korpusu.kos)
    assert "_canli_ortami_geri_yukle" in govde, (
        "🔴 canlı ortam geri yüklenmiyor — ölçüm test sağlayıcısıyla koşabilir.")
    assert "if not _sag" in govde, (
        "🔴 sağlayıcı yokluğunda KOŞMAMA kapısı yok — sessizce `rule` ile ölçülebilir.")


def test_VAKALAR_KATALOGDAN_ve_TEK_SAHIPLI(schema):
    """🔴 Vaka **uydurulmaz**: *«bu ölçü hangi küpte»* katalogun beyanıdır (`KAT-1`).
    Ve **yalnız tek sahipli** ölçüler vaka olur — çok sahipli bir terimde *«doğru cube»*
    diye bir şey **yoktur** (`§B.1`: route zaten çekiliyor).

    *Bir ölçütü, cevabı belirsiz olan girdilerle sınamak, ölçümü gürültüye çevirir.*
    """
    from lab.garson_korpusu import _vakalar

    v = _vakalar(schema)
    assert len(v) >= 20, f"⊘ ölçüm tabanı çöktü: {len(v)} vaka (beklenen ≥20)"
    sahip: dict[str, set[str]] = {}
    for c in schema["cubes"]:
        for m in c.get("measures") or []:
            ad = m if isinstance(m, str) else (m or {}).get("name")
            if ad:
                sahip.setdefault(str(ad), set()).add(str(c.get("name")))
    for vaka in v:
        assert len(sahip[vaka["olcu"]]) == 1, (
            f"🔴 ÇOK SAHİPLİ ölçü vaka olmuş: {vaka['olcu']} → {sahip[vaka['olcu']]}. "
            "Bu girdide «doğru cube» diye bir şey yok; ölçüm gürültüye döner.")
        assert vaka["cube"] in sahip[vaka["olcu"]]


def test_E8_KORUNUYOR_uretim_bu_modulu_cagirmiyor():
    """🔴🔴 `E-8` — çevrimdışı ölçüm, sıcak yola bağlanamaz."""
    kacak = []
    for kd in ("app", "admin_app", "control_plane"):
        d = _KOK / kd
        if not d.is_dir():
            continue
        for f in d.rglob("*.py"):
            if "garson_korpusu" in f.read_text(encoding="utf-8"):
                kacak.append(str(f.relative_to(_KOK)))
    assert not kacak, f"🔴 `E-8` İHLALİ: üretim kodu garson korpusunu import ediyor → {kacak}"


def test_PAYDA_AYRI_nl_corpus_a_dokunmuyor():
    """⚠ 🅜 **PAYDA KUTSAL.** Yeni ölçüm mevcut korpusun paydasına dokunmamalı; ayrı bir
    rapor üretir. Yüklem `ast`: koşucu `nl_corpus`'u import etmiyor."""
    kaynak = (_KOK / "lab" / "garson_korpusu.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    adlar: set[str] = set()
    for n in ast.walk(agac):
        if isinstance(n, ast.ImportFrom):
            if n.module:
                adlar.add(n.module.split(".")[-1])
            adlar |= {a.name.split(".")[-1] for a in n.names}
        elif isinstance(n, ast.Import):
            adlar |= {a.name.split(".")[-1] for a in n.names}
    assert "nl_corpus" not in adlar, (
        "🔴 garson korpusu `nl_corpus`'u import ediyor — iki ölçüm bir paydayı "
        "paylaşırsa biri ötekini bozar.")
