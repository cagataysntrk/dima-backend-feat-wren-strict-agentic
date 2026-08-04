"""FAZ 0.15 — **DÖRT ÖLÇÜM KAPISI CI'DA.**

## Sıralama hatası düzeltiliyor

Bu madde başta **FAZ 4.1**'di — yani regresyon ağı, belgenin kendi ifadesiyle *"en yüksek
etki alanlı faz"* olan **FAZ 2**'nin semantik ameliyatından **SONRA** kurulacaktı. Oysa
`elektrik` deneyi tam orada erişimi **%64 → %56**'ya düşürmüştü. Doktrin
(*"düzelt → kapıya çevir"*) burada **tersine** işliyordu: ağ, en riskli ameliyattan
**ÖNCE** kurulmalı.

## Yeni kod YOK

Koşucu (`lab/kapi.py --tam`) **zaten yazılmıştı** ve dört kapıyı sırayla koşuyordu;
eksik olan tek şey onu **çağıran workflow**du (ölçüldü: `grep -rn "kapi.py"
.github/workflows/` → boş).

## ⚠ Bu maddenin en öğretici kısmı: ölçüm aracının kendisi

`olcut_8_ci` probe'u **iki kez** yanıldı ve ikisi de aynı sınıftandı — *"bir kapıyı,
onu çağıran KOMUTA göre aramak"*:

1. Yalnız `eval.run|nl_corpus|kapi.py` dizelerini arıyordu → `pytest -q` içinde koşan
   `test_eval_gate.py`'yi göremedi ve **"0 kapı"** dedi.
2. Düzeltilince bu kez `kapi.py --tam`'ın **dördünü birden** koştuğunu göremedi ve
   **"korpus eksik"** dedi.

Doğru ölçüm: **koşucunun NE KAPSADIĞINI** bilmek.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

KOK = pathlib.Path(__file__).resolve().parents[2]
WF = KOK / ".github" / "workflows"


def _workflow(ad: str) -> dict:
    p = WF / ad
    if not p.exists():
        pytest.skip(f"{ad} bulunamadı (repo kökü mount edilmemiş olabilir)")
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def test_GECELIK_WORKFLOW_VAR_ve_TAM_KAPIYI_kosuyor():
    """🔴 **ASIL KAPI.** Koşucu vardı, çağıranı yoktu."""
    d = _workflow("nightly.yml")
    adimlar = d["jobs"]["kapi"]["steps"]
    komutlar = " ".join(str(s.get("run", "")) for s in adimlar)
    assert "kapi.py --tam" in komutlar, (
        "gecelik workflow TAM kapıyı koşmuyor — dört kapının biri bile eksikse "
        "FAZ 2'nin semantik ameliyatı ağsız kalır")


def test_GECELIK_TETIK_hem_ZAMANLI_hem_ELLE():
    """Zamanlı koşum ağı kurar; `workflow_dispatch` onu **kırmızıyı doğrularken**
    kullanılabilir kılar. Yalnız cron olsaydı, bir düzeltmeyi doğrulamak için ertesi
    günü beklemek gerekirdi."""
    d = _workflow("nightly.yml")
    tetik = d.get(True) or d.get("on") or {}
    assert "schedule" in tetik, "zamanlı koşum yok — ağ kurulmaz"
    assert "workflow_dispatch" in tetik, "elle tetikleme yok — kırmızı doğrulanamaz"


def test_GECELIK_HER_PUSHTA_KOSMUYOR():
    """⚠ Tam kapı ~15 dk. Her push'ta koşmak geliştirmeyi **boğar** — bu operasyonun
    kendi ölçümü: sürenin **%75'i** kapıda değil, madde başına tekrarlanan döngüdeydi.
    Gecelik + elle tetik, yavaşlatmayan bir ağ verir."""
    d = _workflow("nightly.yml")
    tetik = d.get(True) or d.get("on") or {}
    assert "push" not in tetik, (
        "gecelik kapı HER PUSH'ta koşuyor — 15 dakikalık bir kapıyı her commit'e "
        "bağlamak, demet disiplinini araç seviyesinde çiğnemektir")


def test_RAPORLAR_KIRMIZIDA_da_YUKLENIYOR():
    """*"Korpus %92,8'e düştü"* bilgisi, **hangi soruların** kaydığı bilinmeden
    düzeltilemez. Sessiz kırpma yok: artefakt `if: always()` ile yüklenir."""
    d = _workflow("nightly.yml")
    yukle = [s for s in d["jobs"]["kapi"]["steps"]
             if "upload-artifact" in str(s.get("uses", ""))]
    assert yukle, "kapı raporları YÜKLENMİYOR — kırmızıda kanıt kaybolur"
    assert str(yukle[0].get("if", "")).strip() == "always()", (
        "raporlar yalnız YEŞİLDE yükleniyor — asıl lazım olduğu an KIRMIZIDIR")


def test_KURULUM_RECETESI_TEK_SAHIP():
    """İkinci bir kurulum reçetesi yazmak, *"aynı kuralın iki sahibi"* kusurunun CI
    tarafındaki hâli olurdu. `nightly.yml` ile `backend-ci.yml` **aynı** sırayı izler:
    Rust binding ÖNCE sabitlenir."""
    gece = _workflow("nightly.yml")["jobs"]["kapi"]["steps"]
    ci = _workflow("backend-ci.yml")["jobs"]["test"]["steps"]

    def _pin(adimlar: list[dict]) -> int:
        for i, s in enumerate(adimlar):
            if "wren-core-py==" in str(s.get("run", "")):
                return i
        return -1

    def _kur(adimlar: list[dict]) -> int:
        for i, s in enumerate(adimlar):
            if 'pip install -e ".[dev]"' in str(s.get("run", "")):
                return i
        return -1

    for ad, adimlar in (("nightly", gece), ("backend-ci", ci)):
        i, j = _pin(adimlar), _kur(adimlar)
        assert i >= 0, f"{ad}: Rust binding sabitleme adımı YOK"
        assert j > i, (
            f"{ad}: `wren-core-py` sabitlemesi kurulumdan SONRA — pip onu sessizce "
            "test edilmemiş bir sürüme yükseltebilir (Dockerfile'ın kendi gerekçesi)")


def test_OLCUT_8_ARTIK_4_4():
    """§C/8'in hedefi *"4 kapı GECELİK"*. Ölçüm aracı da düzeltildi: bir kapıyı **onu
    çağıran komuta göre** aramak iki kez yanlış sonuç verdi."""
    from lab.faz0_taban import olcut_8_ci

    o = olcut_8_ci()
    if o.deger.startswith("⊘"):
        pytest.skip("repo kökü mount edilmemiş — kanonik koşum host'tadır")
    assert o.deger.startswith("4/4"), f"§C/8 hedefine ulaşılmadı: {o.deger} · {o.not_}"
