"""FAZ 4.7 kapısı — **teknik rapor, §C/16 ölçülmeden YAYIMLANAMAZ.**

Rapor bir **yayın**dır: bir kez dışarı çıkınca geri alınamaz. Bu yüzden kapısı, kodun
değil **belgenin** üstündedir ve dört şeyi kilitler:

1. 🔴 **Ön koşul:** §C/16 (uçtan uca doğruluk) **ölçülmüş** olmalı — aleti ve sayısı var mı.
2. 🔴 **Netleştirme AYRI SATIR** — manşet sayı *"cevaplananlar içinde"* olamaz.
3. 🔴 **Her sayı bir KOMUTLA gelir** (kural D2) — komutsuz sayı bir cümledir.
4. 🔴 **Sınırlar bölümü** — *sınırlarını yazmayan bir ölçüm raporu, bir pazarlama
   belgesidir.*
"""

from __future__ import annotations

from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]
_RAPOR = _KOK / "docs/teknik-rapor.md"


@pytest.fixture(scope="module")
def metin() -> str:
    assert _RAPOR.exists(), (
        "🔴 `docs/teknik-rapor.md` yok — FAZ 4.7 geri alınmış olabilir.")
    return _RAPOR.read_text(encoding="utf-8")


def test_ON_KOSUL_C16_olculmus(metin):
    """🔴 *Rapor, §C/16 ölçülmeden YAYIMLANAMAZ* — yol haritasının bağlayıcı şartı."""
    assert (_KOK / "lab/uctan_uca.py").exists(), (
        "🔴 §C/16'nın ölçüm aleti (`lab/uctan_uca.py`) YOK — rapor dayanaksız.")
    assert "§C/16" in metin, "rapor §C/16'ya atıf yapmıyor"
    # Ve gerçek bir sayı taşımalı: alet var ama ölçüm yoksa rapor yine dayanaksızdır.
    assert "n=155" in metin or "**155**" in metin, (
        "🔴 §C/16 ölçümünün ÖRNEKLEM BÜYÜKLÜĞÜ raporda yok — 'ölçtük' demek yetmez.")


def test_MANSET_sayi_netlestirmeyi_PAYDADA_tutar(metin):
    """🔴 *Rakiplerin manşet sayılarını kıyaslanamaz yapan şey tam olarak budur.*"""
    assert "netleştirme paydada" in metin.lower(), (
        "🔴 Manşet sayının hangisi olduğu YAZILI DEĞİL. `%76,1` ile `%91,5` arasındaki "
        "fark tam olarak netleştirmenin paydada olup olmamasıdır ve okuyucu bunu "
        "raporun kendisinden bilmelidir.")
    assert "AYRI SATIR" in metin.upper()
    # İkincil sayı da görünmeli — gizlemek de bir çarpıtmadır.
    assert "cevaplanan içinde" in metin


def test_HER_SAYI_bir_KOMUTLA_gelir(metin):
    """Kural D2 — komutsuz bir sayı bu raporda **yoktur**."""
    for komut in ("lab/kapi.py --tam", "lab/uctan_uca.py",
                  "lab/risk_kapsam.py", "lab/sharding.py"):
        assert komut in metin, f"`{komut}` raporda yok — o bölümün sayısı doğrulanamaz"
    assert "--network none" in metin, (
        "🔴 Yeniden üretilebilirlik şartı: koşumların ağsız olduğu yazılı olmalı.")
    assert "HEAD" in metin, "sayılar HEAD damgası taşımalı (kural D2)"


def test_KOTU_SONUC_raporda_DURUYOR(metin):
    """🔴 Kendi hedefini tutturamayan ölçüm **raporda kalır**."""
    assert "−%18,2" in metin or "-%18,2" in metin, (
        "🔴 Çok-turlu ölçümün DÜŞÜŞÜ rapordan çıkarılmış. §C/16'nın *ilan edilmiş "
        "puanlama kuralı* şartı sonucun YÖNÜNDEN bağımsızdır.")
    assert "KALDI" in metin, "hedefin tutturulamadığı açıkça yazılmalı"


def test_SINIRLAR_bolumu_var(metin):
    """*Sınırlarını yazmayan bir ölçüm raporu, bir pazarlama belgesidir.*"""
    assert "sınırları" in metin, "raporun kendi sınırları bölümü yok"
    for sinir in ("typo", "aynı motoru", "⊘"):
        assert sinir in metin, f"bilinen sınır raporda yazılı değil: {sinir}"


def test_DOGRULANMAMIS_iddialar_DAMGALI(metin):
    """Rakip iddiaları birincil kaynak okunmadan **dayanak yapılamaz**."""
    assert "[DOĞRULANMADI]" in metin
    # Snowflake BIRD sıçraması özellikle: sık anılıyor, kaynağı okunmadı.
    assert "Snowflake" in metin and "DOĞRULANMADI" in metin


def test_GURULTU_TABANI_yazili(metin):
    """10 puanın altındaki fark **yorumlanmaz** — ne lehimize ne aleyhimize."""
    assert "10 PUAN" in metin.upper() or "10 puan" in metin
    assert "%52,8" in metin, "BIRD/Spider anotasyon hata oranı kaynak olarak yazılmalı"


def test_KURAL_A_paydanin_donduruldugu_yazili(metin):
    """🔴 Korpusun tek gerçek yakalaması payda **sabitliğine** dayanıyor."""
    assert "KURAL A" in metin
    assert "445" in metin and "342" in metin, (
        "🔴 *Payda düştü ve doğruluk YÜKSELDİ* olayı raporda yok — o olay, neden "
        "seyreltmenin yasak olduğunun tek kanıtı.")
