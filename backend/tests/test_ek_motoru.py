"""🔴 `G7` — **TÜRKÇE EK MOTORU**: enjekte edilen yuvalar doğru çekimlenir.

⚠ Danışman belgesinin *"son harfe bakar"* önerisi **yanlıştı**: ek sayının **okunuşuna**
göre değişir. `3` → *üç* → `3'te`; `1.000.000` → *milyon* → `1.000.000'a`.

🔴 Kapsam **KAPALI**: metrik adı · boyut değeri · sayı · tarih. Serbest metne
uygulanmaz — o, bu motorun işi değil.
"""

from __future__ import annotations

import pytest

from app.ek import ek_bagla, son_okunus


# --- ÜNLÜ UYUMU -------------------------------------------------------------------


@pytest.mark.parametrize("sozcuk,ek,beklenen", [
    ("Merkez", "de", "Merkezde"),        # ince, yumuşak
    ("Ankara", "de", "Ankarada"),        # kalın
    ("Mart", "de", "Martta"),            # 🔴 sert ünsüz → d→t
    ("fire", "e", "fireye"),             # ünlüyle biter → tampon y
    ("ciro", "e", "ciroya"),             # kalın + tampon
    ("şube", "i", "şubeyi"),
    ("makine", "in", "makinenin"),       # ünlüyle biter → tampon n
    ("ürün", "in", "ürünün"),            # 4'lü uyum: ü
    ("stok", "in", "stoğun"),            # 🔴 yumuşama k→ğ
])
def test_temel_cekimler(sozcuk, ek, beklenen):
    assert ek_bagla(sozcuk, ek) == beklenen


def test_ISTISNA_yumusamaz():
    """🔴 TDK'nın belgelediği kapalı liste: `saat`→`saati` (❌ `saadi`).
    Bir kuralla değil bir LİSTEyle bilinir."""
    assert ek_bagla("saat", "i") == "saati"
    assert ek_bagla("devlet", "i") == "devleti"
    # Ama listede olmayan çok heceli p/ç/t/k YUMUŞAR
    assert ek_bagla("kitap", "i") == "kitabı"


# --- SAYI → OKUNUŞ ----------------------------------------------------------------


@pytest.mark.parametrize("sayi,beklenen", [
    (3, "üç"), (40, "kırk"), (100, "yüz"), (1000, "bin"),
    (1_000_000, "milyon"), (2026, "altı"), (12, "iki"), (0, "sıfır"),
    ("12.430", "otuz"), ("1.000.000", "milyon"),
])
def test_son_okunus(sayi, beklenen):
    assert son_okunus(sayi) == beklenen


@pytest.mark.parametrize("sayi,ek,beklenen", [
    (3, "de", "3'te"),                   # üç → sert ç → te
    (40, "de", "40'ta"),                 # kırk → sert k → ta
    (1_000_000, "e", "1000000'a"),       # milyon → kalın
    (2026, "de", "2026'da"),             # altı → kalın, yumuşak
    (12, "e", "12'ye"),                  # iki → ünlüyle biter → tampon y
])
def test_SAYI_OKUNUSA_gore_cekimlenir(sayi, ek, beklenen):
    """🔴 Danışman belgesinin *"son harfe bakar"* önerisi bunları yanlış yazardı."""
    assert ek_bagla(sayi, ek, sayi=True) == beklenen


def test_sayi_KESME_ISARETI_alir():
    assert "'" in ek_bagla(3, "de", sayi=True)
    assert "'" not in ek_bagla("Mart", "de")


# --- SINIRLAR ---------------------------------------------------------------------


def test_BILINMEYEN_EK_sozcugu_BOZMAZ():
    """🔴 Fail-same: bir eki yanlış yazmaktansa hiç yazmamak yeğdir. Yanlış çekim,
    uydurma bir sayı kadar görünür bir kusurdur."""
    assert ek_bagla("Merkez", "uydurma_ek") == "Merkez"
    assert ek_bagla("", "de") == ""
    assert ek_bagla(None, "de") == ""
    assert ek_bagla("123", "de") == "123"          # ünlüsüz gövde, sayi=False


def test_TABLO_PAYLASILAMADI_gerekcesi_YAZILI():
    """🔴 Yol haritası *"kural tablosu ORTAK olmalı"* diyordu; uygulanamaz.

    `_SUFFIX_ATOMS` **ASCII-normalize** (ı→i, ü→u) ve **doğrulama** yapar; ünlü uyumu
    ise tam olarak normalizasyonun **sildiği** bilgiye dayanır. Aynı kural değil,
    **ters iki kural** — ve gerekçe modülde yazılı olmalı.
    """
    import pathlib
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "ek.py").read_text(encoding="utf-8")
    assert "_SUFFIX_ATOMS" in kaynak and "PAYLAŞILAMADI" in kaynak
    assert "ters iki kural" in kaynak


def test_ZEMBEREK_ALINMADI_gerekcesi_YAZILI():
    """Reddedilen bir seçenek de bir karardır ve gerekçesi kayıtlı olmalı."""
    import pathlib
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "ek.py").read_text(encoding="utf-8")
    for gerekce in ("0.17.1", "JVM", "--network none"):
        assert gerekce in kaynak
