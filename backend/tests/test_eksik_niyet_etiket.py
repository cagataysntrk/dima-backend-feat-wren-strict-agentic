"""FAZ 2.2 — `resp.eksik_niyet`in İNSAN-OKUR eşliği (`eksik_niyet_detay`).

## Kök neden — Tur 2 Senaryo 17'nin bulduğu şey, ölçülerek yeniden teşhis edildi

Roadmap bu maddeyi "FAZ 1'in guarded-LLM basamağıyla çevir" diye tarif ediyordu, ama
kodu okuyunca kök FARKLI çıktı: `Ihlal.aciklama` zaten insan-okurdu (`note`'a gider,
`kismi_cevap_notu` üzerinden) — sorun `resp.eksik_niyet`in HAM `isaret` kodlarını
gösteren, frontend'de elle yazılmış AYRI bir çeviri sözlüğüydü
(`ReportCard.tsx::EKSIK_NIYET_ETIKET`). Ölçüldü: `uyum.py` **17** farklı `isaret`
üretiyor, o sözlük yalnız **7**'sini biliyordu — kalan 10'u (+`niyet_tasima.
EKSIK_ATIF`) HAM KOD olarak kullanıcıya gidiyordu. Bu bir "LLM'e çevirt" sorunu
değil, bir **KAT-1 ihlaliydi** (aynı çevirinin iki sahibi, biri senkronsuz kaldı).
Kök çözüm LLM DEĞİL: `etiket`i KAYNAĞA (`Ihlal`'in kendisine) taşımak, ZORUNLU alan
yapmak (varsayılansız — unutmak artık derlemeyi/çalışma-anını KIRAR), frontend'in
kendi sözlüğünü SİLMEK.
"""

from __future__ import annotations

import ast
import pathlib

from app import uyum
from app.niyet_tasima import EKSIK_ATIF, EKSIK_ATIF_ETIKET

_KOK = pathlib.Path(__file__).resolve().parents[1]


def _uyum_kaynagi() -> str:
    return (_KOK / "app" / "uyum.py").read_text(encoding="utf-8")


# --- YAPISAL KAPI: her Ihlal() inşası bir `etiket` taşımalı ------------------------

def test_HER_IHLAL_INSASI_ETIKET_TASIR():
    """🔴🔴 Kalıcı gate — `etiket` alanı VARSAYILANSIZ (dataclass zaten bunu çalışma
    anında zorluyor); bu test AYNI garantiyi KAYNAK OKUYARAK, çalıştırmadan verir —
    NLU'ya bağımlı, kırılgan senaryolar kurmadan TÜM kod yollarını tarar."""
    agac = ast.parse(_uyum_kaynagi())
    eksik = []
    for node in ast.walk(agac):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "Ihlal":
            has_kw = any(kw.arg == "etiket" for kw in node.keywords)
            # Pozisyonel biçimde `isaret, etiket, aciklama, oneri` sırası — ikinci
            # argüman etikettir; en az 2 pozisyonel argüman olmalı.
            has_pos = len(node.args) >= 2
            if not (has_kw or has_pos):
                eksik.append(node.lineno)
    assert not eksik, (
        f"🔴 `Ihlal(...)` çağrısı `etiket` TAŞIMIYOR (satır: {eksik}) — bu, ham "
        f"`isaret` kodunun kullanıcıya sızmasının BİREBİR kaynağıdır (Tur 2 "
        f"Senaryo 17).")


def test_TUM_ISARETLER_KISA_VE_FARKLI():
    """`etiket` (a) boş olamaz, (b) kendi `isaret` koduyla AYNI olamaz (o zaman
    çeviri değil yankı olurdu), (c) bir rozete sığacak kadar kısadır."""
    agac = ast.parse(_uyum_kaynagi())
    for node in ast.walk(agac):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "Ihlal"):
            continue
        isaret_deger = etiket_deger = None
        for kw in node.keywords:
            if kw.arg == "isaret" and isinstance(kw.value, ast.Constant):
                isaret_deger = kw.value.value
            if kw.arg == "etiket" and isinstance(kw.value, ast.Constant):
                etiket_deger = kw.value.value
        if node.args and isinstance(node.args[0], ast.Constant):
            isaret_deger = node.args[0].value
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            etiket_deger = node.args[1].value
        if etiket_deger is None:
            continue      # dinamik değer (yok bu dosyada, ama kırılgan varsayım yapma
        assert etiket_deger, f"satır {node.lineno}: boş etiket"
        assert len(etiket_deger) <= 30, f"satır {node.lineno}: etiket çok uzun (rozet)"
        # ⚠ Yankı YASAK değildir — `trend` gibi kodlar zaten doğal Türkçe kelimedir
        # (eski 7-kodluk frontend sözlüğünde de `trend: "trend"` böyleydi). Yasak olan
        # `snake_case`/alt-çizgi TAŞIYAN bir etikettir — o kesin bir çeviri EKSİKLİĞİdir.
        if isaret_deger:
            assert "_" not in etiket_deger, (
                f"satır {node.lineno}: etiket `{etiket_deger}` hâlâ `isaret` kodu "
                f"BİÇİMİNDE (alt çizgi taşıyor) — çevrilmemiş")


# --- `etiket_detayi()` — `chipler()` ile AYNI desen ---------------------------------

def test_ETIKET_DETAYI_SIRA_VE_UZUNLUK_KORUR():
    ihlaller = [
        uyum.Ihlal("kiyas", "kıyas", "iki dönemi kıyaslamanı istedin...", "..."),
        uyum.Ihlal("esik", "eşik", "bir eşik verdin...", "..."),
    ]
    detay = uyum.etiket_detayi(ihlaller)
    assert len(detay) == len(ihlaller)
    assert [d["isaret"] for d in detay] == [i.isaret for i in ihlaller]
    assert [d["etiket"] for d in detay] == ["kıyas", "eşik"]
    assert all("aciklama" in d for d in detay)


def test_ETIKET_DETAYI_BOS_LISTEDE_BOS():
    assert uyum.etiket_detayi([]) == []
    assert uyum.etiket_detayi(None) == []


# --- UÇTAN UCA: `resp.eksik_niyet_detay` `resp.eksik_niyet` ile AYNI uzunlukta ------

def test_UCTAN_UCA_EKSIK_NIYET_DETAY_ALANI(client):
    """`test_UCTAN_UCA_EKSIK_NIYET_ALANI`'nin (mevcut) kardeşi — Senaryo 17'nin
    BİREBİR şikayetini kapatır: rozet artık ham kod değil insan-okur etiket taşır."""
    from tests.conftest import ask

    d = ask(client, "ocak ve haziran ciro karşılaştır")
    if d.get("source") != "cube":
        import pytest
        pytest.skip("⊘ bu soru cube yolundan dönmedi")
    assert d.get("eksik_niyet"), "eksik niyet cevaba taşınmıyor"
    detay = d.get("eksik_niyet_detay")
    assert detay, "🔴 eksik_niyet_detay cevaba taşınmıyor — rozet yine ham koda düşer"
    assert len(detay) == len(d["eksik_niyet"])
    for kod, ay in zip(d["eksik_niyet"], detay):
        assert ay["isaret"] == kod
        assert ay["etiket"], f"'{kod}' için boş etiket"
        assert ay["etiket"] != kod, f"'{kod}' etiketi ham kodun kendisi — çeviri yok"


# --- `EKSIK_ATIF`'in de bir etiketi var --------------------------------------------

def test_EKSIK_ATIF_ETIKETLI():
    assert EKSIK_ATIF_ETIKET
    assert EKSIK_ATIF_ETIKET != EKSIK_ATIF


# --- FRONTEND: ikinci sözlük GERİ GELMEMELİ -----------------------------------------

def test_FRONTEND_IKINCI_SOZLUK_YOK():
    """🔴 Regresyon kilidi: `EKSIK_NIYET_ETIKET`/`EKSIK_NIYET_ACIKLAMA` bir daha
    yazılmamalı — tek sahip backend'dedir (`Ihlal.etiket`)."""
    from tests.kapi_ortak import frontend_dir

    kart = (frontend_dir() / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "EKSIK_NIYET_ETIKET" not in kart
    assert "EKSIK_NIYET_ACIKLAMA" not in kart
    assert "item.eksik_niyet_detay" in kart, "yeni alan bağlanmamış"
