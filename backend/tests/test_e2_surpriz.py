"""🔴 `§E2` — «EN BÜYÜK MÜŞTERİ HEP SUÇLU ÇIKIYOR» (Jensen-Shannon sürprizi).

Adtributor'ın (NSDI'14) **kurucu örneği** bu modüle verildi (2026-08-11) ve kusur
birebir üredi:

    toplam 100 → 50 ·  X: 94→47 · Mobile: 5→1 · Tablet: 1→2
    çıktımız →  «X — net değişimin %94,0'ı»   (1. sırada)

Ama X'in **payı hiç değişmedi**: `94/100 = %94` → `47/50 = %94`. X bir sebep değil,
**işin kendisidir**. Gerçek sinyal `Mobile` (%5→%2) ve `Tablet` (%1→%4).

> *«Yalnız explanatory power kullanan her katkı analizi, büyük segmentleri
> **sistematik olarak** suçlar.»* — raporun `§10.2`'si

⚠ **Sıralama DEĞİŞTİRİLMEDİ** (`E2`'nin kendi risk satırı: *«bugünkü cevapları
değiştirir — ölçüm gerekir»*). Eklenen şey bir **ölçü** ve onun **beyanı**dır.
"""

from app.contribution import SURPRIZ_ESIGI_PUAN, contributions, surpriz_notu

#: Adtributor'ın kurucu örneği — birebir.
_ROWS = [
    {"seg": "X", "v": 47.0, "v_gecen": 94.0},
    {"seg": "Mobile", "v": 1.0, "v_gecen": 5.0},
    {"seg": "Tablet", "v": 2.0, "v_gecen": 1.0},
]


def _kalemler():
    return contributions(_ROWS, "seg", "v")


def test_paylar_ve_surpriz_HESAPLANIYOR():
    k = {x["deger"]: x for x in _kalemler()}
    assert k["X"]["pay_onceki"] == 94.0 and k["X"]["pay_simdi"] == 94.0
    assert k["Mobile"]["pay_onceki"] == 5.0 and k["Mobile"]["pay_simdi"] == 2.0
    assert k["Tablet"]["pay_onceki"] == 1.0 and k["Tablet"]["pay_simdi"] == 4.0


def test_EN_BUYUK_kalem_SURPRIZSIZ_cikar():
    """🔴 Kusurun matematiksel adı: en büyük düşüş ≠ dağılım değişimi."""
    k = {x["deger"]: x for x in _kalemler()}
    assert k["X"]["surpriz"] == 0.0, "payı değişmeyen segmentin sürprizi sıfır olmalı"
    assert k["Tablet"]["surpriz"] > k["X"]["surpriz"]
    assert k["Mobile"]["surpriz"] > k["X"]["surpriz"]


def test_SIRALAMA_DEGISMEDI():
    """⚠ `E2` risk satırı: sessiz yeniden sıralama her mevcut cevabı oynatırdı."""
    assert [x["deger"] for x in _kalemler()] == ["X", "Mobile", "Tablet"]


def test_BEYAN_kurucu_ornegi_dogru_anlatiyor():
    n = surpriz_notu(_kalemler())
    assert "payı değişmedi" in n and "%94 → %94" in n
    assert "sebep değil" in n
    # Dağılımı en çok değişen aday da söylenir
    assert "Tablet" in n or "Mobile" in n


def test_DAGILIM_gercekten_degistiyse_BEYAN_YOK():
    """⚠ `§101.1` — yanlış pozitif kusurdan pahalıdır: gerçek bir kayma susturulmaz."""
    rows = [{"seg": "A", "v": 10.0, "v_gecen": 90.0},
            {"seg": "B", "v": 90.0, "v_gecen": 10.0}]
    assert surpriz_notu(contributions(rows, "seg", "v")) == ""


def test_NEGATIF_degerde_SUSULUR():
    """Pay tanımsızsa sürpriz hesaplanmaz — anlamsız bir yüzde yayımlanmaz."""
    rows = [{"seg": "A", "v": -5.0, "v_gecen": 10.0},
            {"seg": "B", "v": 3.0, "v_gecen": 4.0}]
    k = contributions(rows, "seg", "v")
    assert all(x["surpriz"] is None for x in k)
    assert surpriz_notu(k) == ""


def test_esik_bir_RED_degil_gorunurluk():
    """Eşiğin altındaki segment yine raporlanır; yalnız beyanı değişir."""
    assert SURPRIZ_ESIGI_PUAN == 1.0
    assert len(_kalemler()) == 3, "hiçbir segment elenmemeli"
