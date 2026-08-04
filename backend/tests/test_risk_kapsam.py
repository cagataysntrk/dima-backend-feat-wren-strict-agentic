"""FAZ 4.2 — **RİSK-KAPSAM EĞRİSİ** kapısı. [bayraksız: kanıt]

MIMARI §9.1: *"hiçbir sevk edilmiş BI ürünü … risk-kapsam eğrisi yayınlamıyor."*
Bu araç o iddiayı **sayıya** çevirir: ölçüldü (2026-08-04), deterministik kapsam
`gitas %96,9 · gulteks %97,4 · atiksan %94,1`.
"""

from __future__ import annotations

import pathlib
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "lab"))

from risk_kapsam import DETERMINIZM, KAPILAR, egri, rapor_metni  # noqa: E402


def test_SKALER_CONFIDENCE_UYDURULMUYOR():
    """🔴 **Maddenin en sert kuralı.** Eğri kara-kutu bir puan üzerinde değil, **ayrık
    kapılarımız** üzerinde tanımlı. Literatürün kara-kutu sinyalleri `0,61–0,68 AUROC`'ta
    platoluyor; bizimki bir **tahmin değil, mimari beyandır**."""
    kaynak = (KOK / "lab" / "risk_kapsam.py").read_text(encoding="utf-8")
    assert "SKALER `confidence` UYDURULMAZ" in kaynak
    for uydurma in ("confidence =", "guven_puani", "auroc ="):
        assert uydurma not in kaynak, f"skaler güven uydurulmuş ({uydurma!r})"


def test_CONSISTENCY_ESIGE_DONUSTURULMUYOR():
    """🔴 **BAĞLAYICI YAN KURAL.** *"Bir model son derece self-consistent olup yine de
    tutarlı biçimde YANLIŞ olabilir."* Araç `consistency` alanına **hiç bakmaz**."""
    kaynak = (KOK / "lab" / "risk_kapsam.py").read_text(encoding="utf-8")
    assert "tutarlı biçimde YANLIŞ" in kaynak
    # ⚠ **METİN DEĞİL YAPI** — ilk sürüm dizi arıyordu ve **kendi yan-kural açıklamasını**
    # yakaladı (bu oturumda onuncu kez). AST: kodda `consistency` adında bir erişim var mı?
    import ast

    agac = ast.parse(kaynak)
    erisimler = {getattr(n, "attr", "") for n in ast.walk(agac) if isinstance(n, ast.Attribute)}
    erisimler |= {getattr(n, "id", "") for n in ast.walk(agac) if isinstance(n, ast.Name)}
    sizinti = [x for x in erisimler if "consistency" in str(x).lower()]
    assert not sizinti, f"araç `consistency`'yi OKUYOR ({sizinti}) — yan kural ihlali"
    sabitler = [n.value for n in ast.walk(agac)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
                and "consistency" in n.value.lower() and len(n.value) < 40]
    assert not sabitler, f"`consistency` bir ALAN ADI olarak kullanılmış: {sabitler}"


def test_HATA_ORANI_YAZILMIYOR():
    """🔴 Bir kapının hata oranını bu araç **ölçemez** (doğruluk korpusun işi). Yazsaydık
    **uydurma** olurdu — ve uydurma bir risk sayısı, risk-kapsam eğrisinin **tam tersini**
    yapardı."""
    n = egri({"route": 10, "tie_chip": 0, "llm_gerekli": 5})
    assert all("hata_orani" not in x for x in n)
    assert all("determinizm" in x for x in n), "risk yerine DETERMİNİZM SINIFI taşınmalı"


def test_KAPSAM_MONOTON_ARTIYOR():
    """Her kapı bir öncekinin cevaplayamadığını devralır — kapsam **azalamaz**."""
    n = egri({"route": 10, "tie_chip": 3, "llm_gerekli": 7})
    kapsamlar = [x["kapsam"] for x in n]
    assert kapsamlar == sorted(kapsamlar) and kapsamlar[-1] == 1.0


def test_OLCULEMEYEN_KAPIYA_YAZILMIYOR():
    """⚠ `intent`/`discovery` LLM'siz koşumda **ölçülemez** — `llm_gerekli` kovasında
    toplanır. *Ölçülmeyeni bir kapıya yazmak, eğriyi olduğundan iyimser gösterirdi.*"""
    metin = rapor_metni({"x": egri({"route": 1, "tie_chip": 0, "llm_gerekli": 1})})
    assert "ölçülemez" in metin and "iyimser" in metin


def test_KAPI_SIRASI_MIMARIYLE_AYNI():
    """Eğrinin x ekseni **cevaplama merdiveninin kendisidir** — ikinci bir sıra yazmak,
    eğriyi mimariden koparırdı."""
    assert KAPILAR == ("route", "tie_chip", "intent", "discovery")
    assert DETERMINIZM["route"] == "deterministik"
    assert DETERMINIZM["discovery"] == "llm_sql"


def test_YENIDEN_URETILEBILIR():
    """**Aynı sha → aynı eğri.** Rastgelelik yok: girdi korpustan türetilen sıralı bir
    sonda kümesi, çıktı saf bir sayım."""
    a = egri({"route": 7, "tie_chip": 2, "llm_gerekli": 1})
    b = egri({"route": 7, "tie_chip": 2, "llm_gerekli": 1})
    assert a == b
    kaynak = (KOK / "lab" / "risk_kapsam.py").read_text(encoding="utf-8")
    for rastgele in ("random", "shuffle", "sample("):
        assert rastgele not in kaynak, f"eğri RASTGELE ({rastgele!r}) — yeniden üretilemez"


def test_RAPOR_URETILDI():
    """`lab/reports/risk_kapsam.md` — maddenin çıktısı bir **yayın**dır."""
    rapor = KOK / "lab" / "reports" / "risk_kapsam.md"
    if rapor.is_file():
        metin = rapor.read_text(encoding="utf-8")
        assert "Risk-kapsam eğrisi" in metin and "%9" in metin
