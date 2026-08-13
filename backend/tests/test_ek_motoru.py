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


# --- 🔴 DA-1 KAPANDI — motorun ÜRETİM TÜKETİCİSİ --------------------------------


def test_EK_MOTORUNUN_URETIM_CAGIRANI_VAR():
    """🔴 **Üç denetim ajanı da bağımsız olarak buldu:** `G7` bu modülü yazdı ve
    **hiçbir yerden çağırmadı**. Commit başlığı *"enjekte edilen yuvalar doğru
    çekimleniyor"* diyordu; hiçbir yuva çekimlenmiyordu.

    *Bir modülün testli olması, kullanıldığını kanıtlamaz.*
    """
    import ast
    import pathlib

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    cagiranlar = []
    for py in kok.rglob("*.py"):
        if py.name == "ek.py":
            continue
        try:
            agac = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for n in ast.walk(agac):
            if isinstance(n, ast.ImportFrom) and n.module == "app.ek":
                cagiranlar.append(py.name)
    assert cagiranlar, (
        "🔴 `app/ek.py` üretimde SIFIR çağıranı olan bir YETİM. Yetim yasağı: bir "
        "backend yeteneği tüketicisi olmadan «bitti» değildir.")


def test_YUVA_CEKIMI_GERCEK_DEGERE_GORE():
    """Model eki **yuvayı görerek** seçer, gerçek değeri görmeden. `Mart` ile `Kasım`
    aynı yuvada olabilir ama ekleri farklıdır."""
    from app.yayilim import geri_koy

    m, s = geri_koy("en yüksek {{DIM_1}}'de oldu", {"{{DIM_1}}": "Mart"})
    assert m == "en yüksek Mart'ta oldu", m
    assert not s

    m, _ = geri_koy("en yüksek {{DIM_1}}'de oldu", {"{{DIM_1}}": "Kasım"})
    assert m == "en yüksek Kasım'da oldu", m


def test_SAYI_YUVASI_OKUNUSA_GORE():
    """`3` → *üç* → `3'te`; `1.000.000` → *milyon* → `1.000.000'a`."""
    from app.yayilim import geri_koy

    m, _ = geri_koy("{{NUM_1}}'de arttı", {"{{NUM_1}}": "3"})
    assert m == "3'te arttı", m
    m, _ = geri_koy("{{NUM_1}}'e ulaştı", {"{{NUM_1}}": "1.000.000"})
    assert m == "1.000.000'a ulaştı", m


def test_EKSIZ_YUVA_ve_TANINMAYAN_KUYRUK_BOZULMAZ():
    """⚠ Kapsam kapalı: ek yoksa dokunulmaz, tanınmayan bir kuyruk **olduğu gibi** kalır.
    *Şüphede dokunmamak, yanlış çekimlemekten iyidir.*"""
    from app.yayilim import geri_koy

    m, _ = geri_koy("{{DIM_1}} en yüksek", {"{{DIM_1}}": "Mart"})
    assert m == "Mart en yüksek"
    m, _ = geri_koy("{{DIM_1}}'xyz", {"{{DIM_1}}": "Mart"})
    assert m == "Mart'xyz"


# ── 🔴 ÖLÇÜLEN DÖRT MORFOLOJİ KUSURU (`§5.1` cümle üreteci, 2026-08-13) ──────
#
# Dördü de **gerçek katalog etiketiyle** ölçüldü — uydurma vaka yok. Üçü şeridin
# cümlelerinde görünüyordu (`hat`·`renk`·`cinsiyet`), dördüncüsü (`kürk`) düzeltmeyi
# ölçerken ortaya çıktı: *bir kusuru düzeltirken komşusuna bakmak, ikinci kusuru
# bulmanın en ucuz yoludur* ⑯.

def test_GOVDESI_DEGISEN_SOZCUKLER():
    """`hat → hatta` (ünsüz **ikizleşmesi**) · `renk → renge` (`k → g`, `ğ` değil).

    🅑 Mutasyon: `_OZEL_GOVDE` boşaltılırsa motor `«hada»` ve `«renğe»` üretir ve bu
    yüklem kırılır.
    """
    from app.ek import ek_bagla

    assert ek_bagla("hat", "e") == "hatta"
    assert ek_bagla("renk", "e") == "renge"
    assert ek_bagla("Renk", "e") == "Renge", "başlık harfi korunmalı ⑧"


def test_CINSIYET_YUMUSAMAZ():
    """`cinsiyet → cinsiyete`. Motor `«cinsiyede»` üretiyordu; TDK: *cinsiyeti*."""
    from app.ek import ek_bagla

    assert ek_bagla("cinsiyet", "e") == "cinsiyete"


def test_UNSUZDEN_SONRAKI_K_YUMUSAMAZ():
    """🔴 **Kural, liste değil**: `k` yumuşaması ünlüden sonra olur, **ünsüzden** sonra
    olmaz. Listeye yazmak sonsuz bir sözcük sınıfını tek tek saymak olurdu 🆞.

    🅑 Mutasyon: `_yumusat`'taki `govde[-2] not in _UNLU` dalı kaldırılırsa `kürk`
    `«kürğe»`ye döner ve bu yüklem kırılır.
    """
    from app.ek import ek_bagla

    for sozcuk, beklenen in (("kürk", "kürke"), ("park", "parka"), ("Türk", "Türke")):
        assert ek_bagla(sozcuk, "e") == beklenen, f"{sozcuk} yanlış çekimlendi"
    # ⚠ Ve kural **korunmalı**: ünlüden sonraki `k` hâlâ yumuşar.
    assert ek_bagla("gök", "e") == "göğe"
    assert ek_bagla("ekmek", "e") == "ekmeğe"
