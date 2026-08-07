"""🔴 `Ö10` — *"…-e **göre**"* bir DÖNEM referansı mı, bir KIRILIM mı?

## Ölçülen kusur — kullanıcının kendi vakası

    "şubatta ciro ocağa göre nasıl değişti"

→ `niyet: tür=**kirilim**+trend`, cevap *"şubat toplamı"*, ve `uyum` kullanıcıya:

> *"bir kırılım istedin ama sorguya bir boyut taşıyamadım"*

Kullanıcı kırılım **istemedi**. `gore` bir kıyas edatıydı.

🔴 **Yanlış bir beyan, sessizlikten kötüdür**: sistem kullanıcıya *onun söylemediği bir
şeyi söylediğini* söylüyor — güvenin en hızlı tükendiği yer burasıdır.

## İkinci kusur aynı soruda: ünsüz yumuşaması

`ocağa` **hiç tanınmıyordu** — `ocak` + ünlüyle başlayan ek → `k`→`ğ`, ve `ocak\\w*` bunu
yakalamaz. Kural `app/ek.py`'nin (G7) belgelediği yumuşamanın **ters yönü**: o üretir,
`_MONTH_ALT` artık **söker**.

## ⚠ KAPSAM `Ö10`'UN KENDİ SÖZÜYLE SINIRLI

> *"`göre`'den sonra gelen **AY ADI** boyut adayı sayılmasın."*

Yani **adlandırılmış** dönem (ay · yıl · çeyrek) — göreli ifade **DEĞİL**.
🔴 *"son N ay'a göre"* göreli bir **aralıktır**, bir kıyas ucu değil; bu ifade bu depoyu
**üç kez** ısırdı. `date_filters` ikisini de çözer — yani tek başına onu ölçüt yapmak,
kapsamı `Ö10`'un istediğinden geniş tutardı ve bilinen tuzağa doğrudan basardı.

*Bir ayrımı, ayrımın yapıldığı belgeden daha geniş kurmak, düzeltme değil kumardır.*
"""

from __future__ import annotations

import pytest

from app import cube_router as cr
from app.niyet import coz_soru


@pytest.mark.parametrize("soru,donem_mi", [
    ("şubatta ciro ocağa göre nasıl değişti", True),    # kullanıcının vakası
    ("mart cirosu şubata göre", True),
    ("son 3 aya göre ciro", False),                      # 🔴 ÜÇ KEZ ISIRAN İFADE
    ("son 6 aya göre fire", False),
    ("makineye göre ciro", False),
    ("hat bazında verimlilik", False),
])
def test_GORE_AYRIMI(soru, donem_mi):
    assert cr.gore_donem_mi(cr._norm(soru)) is donem_mi, (
        f"🔴 {soru!r}: `gore` yanlış sınıflandı")


def test_KULLANICININ_VAKASI_ARTIK_KIRILIM_DEMIYOR():
    """🔴 Asıl kazanç: sistem artık **söylemediği bir şeyi** söylediğini iddia etmiyor."""
    n = coz_soru("şubatta ciro ocağa göre nasıl değişti")
    assert "kirilim" not in n.turler, f"🔴 hâlâ kırılım sanıyor: {n.turler}"
    assert "kiyas" in n.turler, "🔴 kıyas niyeti hâlâ görünmüyor"
    assert n.temsil_edilemeyen, (
        "🔴 kıyas görüldü ama temsil edilemediği SÖYLENMİYOR — sessiz-yanlış adayı")


def test_KIRILIM_TARAFI_BOZULMADI():
    """⚠ Genişlemenin sınırı: gerçek kırılım soruları etkilenmemeli. *Bir kuralı
    düzeltmek, komşusunu bozma hakkı vermez.*"""
    for q in ("makineye göre ciro", "hat bazında verimlilik", "vardiya kırılımında fire"):
        assert "kirilim" in coz_soru(q).turler, f"🔴 {q!r} kırılım olmaktan çıktı"


def test_AY_ADI_YUMUSAMASI():
    """`ocağa` = Ocak. Kural, liste değil: `k` ile biten ay adları ek alınca yumuşar."""
    assert cr._MONTHS.get("ocag") == 1 and cr._MONTHS.get("aralig") == 12
    assert "oca[kğ]" in cr._MONTH_ALT and "arali[kğ]" in cr._MONTH_ALT


def test_YENI_SOZLUK_YAZILMADI():
    """🔴 `ADR-0008`. Ayrımın ölçütü `date_filters`'ın **kendisi** — ikinci bir dönem
    tanıyıcısı yok."""
    import inspect

    src = inspect.getsource(cr._guvenli_donem)
    assert "date_filters" in src
    govde = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith(("#", '"'))]
    assert not any('"' in l and "," in l and "=" in l for l in govde), (
        "🔴 gövdeye sözlük yazılmış")
