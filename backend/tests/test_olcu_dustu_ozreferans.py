"""🔴🔴 `§ÖB` — **SİSTEMİN SEÇTİĞİ ÖLÇÜ, KULLANICININ İSTEDİĞİ SAYILIYORDU.**

## Ölçülen kusur (curl turu, 2026-08-10)

    «bu yıl en kötü fire» → fire_orani_yuzde · RAM-2 · %22,12          ✅ DOĞRU
    note: «⚠ Sayı doğru ama EKSİK: soruda 2 ÖLÇÜ geçiyor ama cevapta 1 var
           — `toplam_fire_kg` rapora girmedi.»                          🔴 YANLIŞ

Kullanıcı **bir** şey söyledi: *«fire»*. Ve sinonimler **ayrık**:

    toplam_fire_kg   → ['fire', …]          ← soruda GEÇİYOR
    fire_orani_yuzde → ['fire orani', …]    ← soruda GEÇMİYOR

Yani sinonim eşleşmesi **tek** bir ölçü buluyordu; ikinciyi **birleşim** ekliyordu
(`| _verilen_olculer`) — yani **cevabın kendisi**.

🔴 Bir öz-referans: sistemin seçimi *«istenen»* kovasına giriyor, sonra o kovayla
kıyaslanıyor ve **her zaman** bir eksik çıkıyor.

*Bir talebi, cevabın kendisinden türetmek; sınavı kendi cevap anahtarından yazmaktır.*
"""

from app import uyum

_META = {
    "name": "parti",
    "measures": ["toplam_fire_kg", "fire_orani_yuzde", "toplam_ciro"],
    "dimensions": ["hat", "makine"],
    "time_dimensions": ["tarih"],
    "measure_synonyms": {"toplam_fire_kg": ["fire", "waste"],
                         "fire_orani_yuzde": ["fire orani", "fire yuzdesi"],
                         "toplam_ciro": ["ciro", "hasilat"]},
    "dimension_synonyms": {"hat": ["hat"], "makine": ["makine"]},
}
_SEMA = {"cubes": [_META]}


def _isaretler(soru, cq):
    return {i.isaret for i in uyum.denetle(soru, {"cube_query": cq}, _META, _SEMA)}


def test_TEK_KELIME_IKI_OLCU_SAYILMAZ():
    """🔴 **Kusurun kendisi.** Kullanıcı *«fire»* dedi; sistemin `fire_orani_yuzde`
    seçmesi onu *«iki ölçü istedi»* yapmaz."""
    cq = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    assert "olcu_dustu" not in _isaretler("bu yil en kotu fire", cq)


def test_GERCEKTEN_IKI_OLCU_ISTENDIYSE_BEYAN_EDILIR():
    """🔴🔴 **Kapı fazla ileri gitmemeli.** Kullanıcı iki ölçüyü de **adıyla** andıysa
    ve biri düştüyse beyan **yazılır** — bu, düzeltmenin kapatmadığı gerçek kusurdur.
    *Bir yanlış-pozitifi kapatırken gerçek pozitifi kapatmak, kapıyı dekora çevirir.*"""
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"]}
    assert "olcu_dustu" in _isaretler("bu yil ciro ve fire", cq)


def test_IKISI_DE_VERILDIYSE_BEYAN_YOK():
    """İkisi de rapora girdiyse düşen bir şey yoktur."""
    cq = {"cube": "parti", "measures": ["toplam_ciro", "toplam_fire_kg"],
          "dimensions": ["makine"]}
    assert "olcu_dustu" not in _isaretler("bu yil ciro ve fire", cq)


def test_IC_ICE_SINONIM_HALA_TEK_SAYILIR():
    """⚠ Var olan *«en uzun eşleşme kazanır»* kuralı korunuyor: *«fire oranı»* iki
    ölçüyü birden çağırmaz — `fire`, `fire orani`'nın **içindedir**."""
    cq = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    assert "olcu_dustu" not in _isaretler("bu yil makine bazinda fire orani", cq)
