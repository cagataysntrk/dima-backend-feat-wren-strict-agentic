"""🔴 **YTD SESSİZ-YANLIŞI** — *"yılbaşından bugüne"* bugünden İLERİYE bakıyordu.

## Ölçülen

    'yilbasindan bugune hasilat' → [{'operator': 'gte', 'value': '2026-08-07'}]

`bugune` çekimi `_current_period_filter`'ın `bugun` kuralına takılıyor ve *"bugün ve
sonrası"* filtresi kuruluyordu. Kullanıcı **yıl başından bugüne** sorup **bugünden
ileriye** bakan bir sayı alıyordu — ve o sayı neredeyse her zaman boş olduğu için
*"veri yok"* gibi okunuyordu. **Rozet `◆ CUBE`, güven yüksek, sayı yanlış.**

## ⚠ Yeni sözlük YAZILMADI

*"Yıl başı"* kavramının sahibi zaten `app/mali_takvim.py` — `yoy.compute` YTD'yi tam
böyle kuruyor. Yapılan şey var olan sahibi bir ifadeye **bağlamak**. `ADR-0008`'in
yasakladığı şey sözlük **icat etmek**tir; sahibini çağırmak değil.
"""

from __future__ import annotations

from datetime import date

import pytest

from app import cube_router as cr
from app import mali_takvim


@pytest.mark.parametrize("soru", [
    "yilbasindan bugune hasilat",
    "yil basindan bugune ciro",
    "yılbaşından bugüne fire",
])
def test_YTD_GERIYE_BAKAR_ILERIYE_DEGIL(soru):
    f = cr.date_filters(cr._norm(soru))
    ops = {x["operator"]: x["value"] for x in f}
    assert ops.get("gte") == mali_takvim.yil_basi(date.today()).isoformat(), (
        f"🔴 YTD yıl başından başlamıyor: {f}")
    assert ops.get("lte") == date.today().isoformat(), (
        "🔴 `lte bugün` YOK — gelecek tarihli kayıtlar (bütçe/hedef/planlanan sevkiyat) "
        "sessizce toplama girerdi")


def test_BUGUN_TEK_BASINA_HALA_BUGUN():
    """⚠ Genişlemenin sınırı: *"bugünkü ciro"* hâlâ **bugün**dür. Bir kuralı düzeltmek,
    komşusunu bozma hakkı vermez."""
    f = cr.date_filters(cr._norm("bugunku ciro"))
    assert f and f[0]["value"] == date.today().isoformat()
    assert f[0]["operator"] == "gte"


def test_YENI_SOZLUK_DEGIL_MEVCUT_SAHIP():
    """🔴 `ADR-0008`. Hesap `mali_takvim`'de; burada yalnız bir **bağ** var."""
    import inspect

    src = inspect.getsource(cr.date_filters)
    assert "mali_takvim.yil_basi" in src, "🔴 yıl başı ikinci kez hesaplanmış"
    assert "01-01" not in src, "🔴 takvim yılı sabiti gömülmüş — mali yıl müşterisinde yanlış"
