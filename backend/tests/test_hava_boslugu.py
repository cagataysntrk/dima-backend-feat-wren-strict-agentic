"""`G0b` — **HAVA BOŞLUĞU**: gerçek değer ve sayı binadan ÇIKMAZ.

## Ölçülen kusur (2026-08-07)

`llm_guard.ihlalleri_bul` PII **kalıplarını** yakalıyordu (TCKN · e-posta · telefon ·
IBAN). Ama `interpret.py:248` şunu üretiyor ve olduğu gibi sağlayıcıya gidiyordu:

    "En yüksek Makine: RAM 3 (12.430 kg)"

`RAM 3` bir boyut **değeri**, `12.430` gerçek bir **sayı** — ikisi de hiçbir maskeye
uymuyor. Dış sağlayıcıya geçildiği an bu **binadan çıkan veridir**.

🔴 Ve yer tutucu `narration_guard`'ı **zayıflatmaz, güçlendirir**: model bir rakam
*üretemez*, yalnız verdiğimiz yuvayı taşıyabilir. Doğrulama ±%2 eşleştirmesinden
**yapısal** doğrulamaya yükselir.

⚠ Perdeleme `app/yayilim.py`'dedir, `llm_guard`'da DEĞİL — çünkü `test_llm_guard.py::
test_DESEN_SOZLUGU_KOPYALANMAMIS` o modüle regex yazılmasını kilitliyor ve **haklı**:
*"bu yük çıkabilir mi"* ile *"ne perdelenecek"* iki ayrı sorudur.
"""

from __future__ import annotations

from app.llm_guard import ihlalleri_bul
from app.yayilim import geri_koy, perdele


# --- PERDELEME ---------------------------------------------------------------------


def test_YER_TUTUCU_ICINE_SAYI_TARANMAZ():
    """🔴 Ölçülen kusur: `{{DIM_1}}` içindeki `1` sayı sanılıp `{{DIM_{{NUM_2}}}}`
    üretiliyordu — *bir maskenin kendi çıktısını yeniden maskelemesi maskeyi bozar.*"""
    perdeli, harita = perdele(["RAM 3 iyi"], degerler=["RAM 3"])
    assert perdeli[0] == "{{DIM_1}} iyi", perdeli[0]
    assert len(harita) == 1


def test_gercek_deger_ve_sayi_CIKMAZ():
    """Asıl vaka: `interpret` olgusunun birebir biçimi."""
    metinler = ["En yüksek Makine: RAM 3 (12.430 kg)"]
    perdeli, harita = perdele(metinler, degerler=["RAM 3"])
    giden = perdeli[0]
    assert "RAM 3" not in giden
    assert "12.430" not in giden
    assert "{{DIM_1}}" in giden
    assert any(v == "RAM 3" for v in harita.values())
    assert any(v == "12.430" for v in harita.values())


def test_ayni_deger_TEK_yuva_alir():
    """Aynı gerçek değer iki kez geçiyorsa yuva **tekrar edilmez** — yoksa geri koyma
    sırasında hangi yuvanın hangisi olduğu belirsizleşirdi."""
    _, harita = perdele(["RAM 3 ve yine RAM 3"], degerler=["RAM 3"])
    assert sum(1 for v in harita.values() if v == "RAM 3") == 1


def test_UZUN_deger_once_perdelenir():
    """`RAM` ⊂ `RAM 3`: kısa olan önce alınsaydı uzun değer **yarım** perdelenirdi."""
    perdeli, _ = perdele(["RAM 3 makinesi"], degerler=["RAM", "RAM 3"])
    assert "RAM 3" not in perdeli[0]
    assert perdeli[0].count("{{DIM_") == 1        # tek yuva, parçalanmadı


def test_harita_SAGLAYICIYA_gitmez():
    """Perdeleme (giden) ile harita (kalan) **ayrı** dönerler — karıştırılamaz."""
    perdeli, harita = perdele(["Ciro 1.000 TL"], degerler=[])
    assert "1.000" not in perdeli[0]
    assert "1.000" in harita.values()


# --- GERİ KOYMA --------------------------------------------------------------------


def test_geri_koyma_gercek_degeri_yerine_koyar():
    _, harita = perdele(["En yüksek Makine: RAM 3 (12.430 kg)"], degerler=["RAM 3"])
    yt_dim = next(k for k, v in harita.items() if v == "RAM 3")
    yt_num = next(k for k, v in harita.items() if v == "12.430")
    metin, sorunlar = geri_koy(f"{yt_dim} makinesi {yt_num} kg üretti.", harita)
    assert metin == "RAM 3 makinesi 12.430 kg üretti."
    assert sorunlar == []


def test_EKSIK_yuva_raporlanir():
    """Model bir yuvayı düşürdüyse cümle eksiktir — sessizce geçirmek yasak."""
    harita = {"{{NUM_1}}": "12.430", "{{DIM_1}}": "RAM 3"}
    _, sorunlar = geri_koy("{{DIM_1}} iyi gidiyor.", harita)
    assert "eksik:{{NUM_1}}" in sorunlar


def test_UYDURMA_yuva_raporlanir():
    """🔴 Model haritada olmayan bir yuva icat ettiyse — uydurma sayının yeni biçimi."""
    harita = {"{{NUM_1}}": "12.430"}
    _, sorunlar = geri_koy("{{NUM_1}} ve ayrıca {{NUM_7}} kg.", harita)
    assert "uydurma:{{NUM_7}}" in sorunlar


def test_uydurma_yuva_METINDE_KALIR():
    """Uydurma yuva **temizlenmez**: çağıran cümleyi düşürecek, biz gizlemeyeceğiz."""
    metin, _ = geri_koy("{{NUM_7}} kg", {"{{NUM_1}}": "1"})
    assert "{{NUM_7}}" in metin


# --- MEVCUT PII KAPISI BOZULMADI ---------------------------------------------------


def test_pii_kapisi_AYNEN_calisiyor():
    """`G0b` mevcut kapıyı genişletti, **değiştirmedi**."""
    assert ihlalleri_bul("iletisim: a@b.com") == ["e-posta"]
    assert ihlalleri_bul("merhaba") == []
