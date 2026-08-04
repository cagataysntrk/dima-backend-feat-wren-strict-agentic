"""FAZ 3.3 — **TERFİ KUYRUĞU KAPANIŞ ORANI** kapısı. [bayraksız: ölçüm]

MIMARI §9 ilke 4: *"her Discovery cevabı bir **kapsam boşluğunun belgesidir**"* — ve o
belge `MeasureCandidate` olarak kuyruğa giriyor. Ama **kaçının kapandığını kimse
ölçmüyordu**: kuyruk büyüyor mu, eriyor mu, yoksa yalnız **birikiyor** mu?

*Ölçülmeyen bir kuyruk, kuyruk değil bir çöp kutusudur.*
"""

from __future__ import annotations

import pathlib

from app import terfi_kapanis as tk

KOK = pathlib.Path(__file__).resolve().parents[1]


# ── 1 · RED DE KAPANIŞTIR ───────────────────────────────────────────────────

def test_REDDEDILEN_DE_KAPANIS():
    """🔴 **Maddenin en kritik kararı.** *"Bu bir metrik değil"* kararı boşluğun kapandığı
    anlamına gelir — aday kuyruktan çıkmıştır. Yalnız onayları saymak, **doğru reddi bir
    başarısızlık gibi** gösterir ve incelemeciyi **onaylamaya** iterdi."""
    r = tk.oran({"approved": 2, "rejected": 3, "deprecated": 1, "draft": 4})
    assert r["kapali"] == 6 and r["acik"] == 4
    assert r["kapanis_orani"] == 0.6


def test_PENDING_REVIEW_ACIK_SAYILIYOR():
    """⚠ *Bakılmayı bekleyen bir karar, verilmiş bir karar değildir.*"""
    r = tk.oran({"pending_review": 5, "approved": 5})
    assert r["acik"] == 5 and r["kapanis_orani"] == 0.5


def test_HIC_ADAY_YOKKEN_ORAN_NONE():
    """🔴 `0.0` **değil** `None`: hiç aday yokken *"%0 kapanış"* demek, çalışmayan bir
    kuyruğu **başarısız** gibi gösterirdi. *Yokluk bir başarısızlık değildir.*"""
    assert tk.oran({})["kapanis_orani"] is None
    assert tk.oran({"draft": 0})["kapanis_orani"] is None


def test_BILINMEYEN_DURUM_TOPLAMA_GIRIYOR():
    """⚠ Bilinmeyen bir durum ne açık ne kapalı sayılır **ama toplama girer** — sessizce
    düşürmek oranı **olduğundan yüksek** gösterirdi."""
    r = tk.oran({"approved": 1, "acayip_durum": 1})
    assert r["toplam"] == 2 and r["kapali"] == 1 and r["kapanis_orani"] == 0.5


def test_DURUM_ADLARI_MODELDEN():
    """🔴 Uydurma durum adı, kapıyı **yeşil tutup** ölçümü **ölü** bırakırdı (`1.12`'de
    birebir bu yaşandı: `done`/`error` yazmıştım, model `completed`/`failed` diyordu)."""
    kaynak = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    beyan = next(s for s in kaynak.splitlines()
                 if s.strip().startswith("status:") and "draft" in s)
    for d in tk.ACIK_DURUMLAR + tk.KAPALI_DURUMLAR:
        assert d in beyan, f"{d!r} `MeasureCandidate` sözlüğünde YOK — uydurma durum"


# ── 2 · EŞİK KONMADI — ve nedeni yazılı ────────────────────────────────────

def test_ESIK_KONMADI_ve_GEREKCESI_YAZILI():
    """⚠ Eşik bir **iş kararıdır** (haftada kaç aday kapatılmalı?) ve **veri olmadan
    konulamaz**. Bugün ölçüm başlıyor; eşik, taban oluştuktan sonra bir sonraki turun işi.
    *Ölçülmemiş bir eşik, uydurulmuş bir hedeftir.*"""
    kaynak = (KOK / "app" / "terfi_kapanis.py").read_text(encoding="utf-8")
    assert "EŞİK KOYMAZ" in kaynak and "uydurulmuş bir hedeftir" in kaynak
    for uydurma in ("HEDEF_ORAN", "MIN_KAPANIS", "esik ="):
        assert uydurma not in kaynak, f"ölçülmemiş bir eşik konmuş ({uydurma!r})"


# ── 3 · UÇ VAR, YOL SIRASI DOĞRU ───────────────────────────────────────────

def test_UC_VAR():
    from app.main import create_app

    yollar = {y: {m.upper() for m in o} for y, o in create_app().openapi()["paths"].items()}
    assert "GET" in yollar.get("/measures/candidates/kapanis", set())


def test_SABIT_YOL_UUID_UCUNDAN_ONCE():
    """🔴 `kapanis` bir UUID **değildir**; sıra ters olsaydı FastAPI onu bir aday kimliği
    sanardı (ilk eşleşen kazanır) ve uç **hiç çalışmazdı**."""
    kaynak = (KOK / "app" / "routers" / "measures.py").read_text(encoding="utf-8")
    assert kaynak.index('"/candidates/kapanis"') < kaynak.index('"/candidates/{cid}"')


def test_TENANT_SINIRLI():
    """Bir tenant'ın kuyruk sağlığı başkasının sayılarıyla ölçülemez; superadmin hepsini
    görür (ADR-0015 K7 — engel değil görünürlük)."""
    kaynak = (KOK / "app" / "routers" / "measures.py").read_text(encoding="utf-8")
    i = kaynak.index("def kapanis_orani")
    assert "is_superadmin" in kaynak[i:i + 900] and "tenant_id" in kaynak[i:i + 900]


# ── 4 · RAPOR METNİ ─────────────────────────────────────────────────────────

def test_RAPOR_OLCULEMEDIYI_YUZDE_SIFIR_GOSTERMIYOR():
    """⊘ üçüncü durum rapor metninde de korunur."""
    assert "⊘ ÖLÇÜLEMEDİ" in tk.rapor_metni(tk.oran({}))
    assert "%0.0" not in tk.rapor_metni(tk.oran({}))


def test_RAPOR_RED_ACIKLAMASINI_TASIYOR():
    """Raporu okuyan kişi, **neden reddin de kapanış sayıldığını** görmeli — yoksa oranı
    *"onay oranı"* sanar ve incelemeciyi onaylamaya iter."""
    metin = tk.rapor_metni(tk.oran({"approved": 1, "rejected": 1}))
    assert "Reddedilen de KAPANIŞTIR" in metin


# ── 5 · K2 · EKRAN: oran görünüyor, "⊘" yüzde-sıfır sanılmıyor ────────────

def test_ORAN_EKRANDA():
    """🔴 **K2 — yetim uç yok.** Ölçülen ama **gösterilmeyen** bir oran, ölçülmemiş bir
    orandır: kimse ona bakmaz."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    panel = (fe / "components" / "ReviewPanel.tsx").read_text(encoding="utf-8")
    assert "getTerfiKapanis" in panel and "kapanış" in panel
    assert "getTerfiKapanis" in (fe / "lib" / "api-client.ts").read_text(encoding="utf-8")


def test_EKRAN_OLCULEMEDIYI_AYIRIYOR():
    """🔴 `null` = hiç aday yok. *"%0"* göstermek, çalışmayan bir kuyruğu **başarısız**
    gibi gösterirdi — *yokluk bir başarısızlık değildir.*"""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    panel = (fe / "components" / "ReviewPanel.tsx").read_text(encoding="utf-8")
    assert "oran === null" in panel and "ölçülemez" in panel


def test_EKRAN_REDDIN_KAPANIS_OLDUGUNU_SOYLUYOR():
    """⚠ Oranı *"onay oranı"* sanan bir incelemeci, **onaylamaya** itilir."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    panel = (fe / "components" / "ReviewPanel.tsx").read_text(encoding="utf-8")
    assert "Reddedilen de KAPANIŞTIR" in panel
