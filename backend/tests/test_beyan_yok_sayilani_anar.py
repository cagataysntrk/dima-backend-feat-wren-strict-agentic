"""🔴 `§34` — **EKSİK BİR DOĞRU: beyan, YOK SAYDIĞINI da söylemeli.**

## Ölçülen kusur (`K3`'ün kalan kısmı, 2026-08-13)

`2019 cirosu` sorusunda ürün doğru davranıyordu ama **yarım konuşuyordu**:

    cube_query.filters = tarih ∈ [2025-06-01, 2026-06-30]
    note = "⏱ Dönemi çözemedim — verinin son 12 ayı alındı (…). Başka bir dönem
            yazarsan onu uygularım."

*"Dönemi çözemedim"* **doğruydu** — ama kullanıcı `2019` **yazmıştı** ve o token
düşürülmüştü. Beyan bunu söylemeyince kullanıcı, sorduğu yılın cevabını aldığını
sanabilir: sessiz-yanlışın en pahalı türü, **doğru sayının yanlış döneme ait olması**.

## Bu kapının savunduğu iki şey — ve savunMADIĞI bir şey

| # | savunulan |
|---|---|
| 1 | Yok sayılan dört hane beyanda **adıyla** anılır |
| 2 | Beyan düzeltmeyi **öğretir** (`«2019 yılı»`) — sınırı söylemek, aşma yolunu göstermekle tamamlanır |
| ⊘ | **Çıplak yıl bir döneme ÇEVRİLMEZ** — `㊸` sınırı korunur (`test_B_CIPLAK_YIL_BILEREK_KAPSAM_DISI`) |

Üçüncü satır bu kapının **zıt ölçütüdür** 🆃: eklenen cümle bir davranış değişikliği
değil, bir **görünürlük** değişikliğidir. `date_filters` hâlâ hiçbir şey üretmez.

⚠ Kapı **zincire bağlıdır** ㉕: metnin varlığı yetmez, `ask.py`'nin `soru`yu **geçtiği**
de `ast` ile ölçülür — çünkü geçmezse cümle üretilemez ve kapı yine yeşil kalırdı 🆆.
"""

from __future__ import annotations

import ast
from pathlib import Path

from app import donem_capasi as capa

_ASK = Path(__file__).resolve().parents[1] / "app" / "routers" / "ask.py"


def test_yok_sayilan_yil_adiyla_anilir():
    ek = capa._yok_sayilan_ek("2019 cirosu")
    assert "2019" in ek
    # Düzeltmeyi ÖĞRETİR: kullanıcı bir dahaki sefere ne yazacağını görür.
    assert "2019 yılı" in ek


def test_donem_cozulen_soruda_ek_YOK():
    """Yalnız çıplak dört hane anılır — soruda öyle bir şey yoksa beyan **bayt aynı**."""
    assert capa._yok_sayilan_ek("ciro") == ""
    assert capa._yok_sayilan_ek("") == ""


def test_ESIK_SAYISI_YIL_SANILMAZ():
    """`1500 uzeri ciro` bir eşiktir, bir yıl değil — `K6`'nın komşusu ⑯.

    `_CIPLAK_YIL_RE` bilerek `19xx|20xx` ile sınırlı: her dört haneli sayı yıl sayılsaydı
    eşikler, hesap kodları ve adetler beyanda **yıl diye** anılırdı.
    """
    assert capa._yok_sayilan_ek("1500 uzeri ciro") == ""
    assert capa._yok_sayilan_ek("3000 adet parti") == ""


def test_SINIR_KORUNUR_ciplak_yil_hala_donem_degil():
    """🔴 Zıt ölçüt 🆃 — anmak, uygulamak DEĞİLDİR."""
    from app import cube_router as cr

    assert cr.date_filters(cr._norm("2019 cirosu")) == []
    # Yıl işareti varsa **çevrilir** — sınırın öteki yüzü.
    assert cr.date_filters(cr._norm("2019 yili cirosu"))


def test_ZINCIR_ask_soruyu_GECIYOR():
    """Kapıyı zincire bağla ㉕: `soru` geçilmezse cümle hiç üretilemez."""
    agac = ast.parse(_ASK.read_text(encoding="utf-8"))
    gecti = False
    for d in ast.walk(agac):
        if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                and d.func.attr == "varsayilan_yerinde"):
            gecti = gecti or any(k.arg == "soru" for k in d.keywords)
    assert gecti, "ask.py `varsayilan_yerinde`'ye `soru=` geçmiyor → beyan yarım kalır"
