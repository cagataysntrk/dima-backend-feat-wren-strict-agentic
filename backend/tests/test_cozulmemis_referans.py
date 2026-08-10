"""🔴🔴 `R1` — **ÇÖZÜLMEMİŞ REFERANS SQL'E GİDEMEZ.**

## Ölçülen kusur — canlıda iki yerde

```
«ne yapmalıyız»            → filters: [{"dimension":"makine","value":"$2"}] · rows=0
thread C/4 «o makinede …»  → aynı süzgeç · rows=0
```

Her ikisi de üstünde *«Bu cevap 5 adımda üretildi»* makbuzuyla döndü. Yani kullanıcı
**boş bir tabloyu çalışmış bir plan** sanıyordu.

⊙ Sebep: `_referanslar` yalnız adımın **üst düzey** alanlarını tarar (`_REF.match`
bütün bir dizge bekler). `cube_query`'nin **içine** yazılmış bir `$n` ne DAG'a kenar
olarak girer, ne çözülür — sonra düz metin olarak süzgeç değeri olur.

*Boş bir sonuç bir cevap değildir; makbuzlu boş bir sonuç ise bir yanlıştır — çünkü
doğruluğunun kanıtı gibi görünür.*
"""

from __future__ import annotations

import pytest

from app.plan_kosucu import PlanHatasi, _cozulmemis_referans, dogrula


def test_SUZGEC_DEGERINDEKI_REFERANS_YAKALANIR():
    """Kusurun birebir şekli."""
    assert _cozulmemis_referans(
        {"cube": "parti", "filters": [{"dimension": "makine", "operator": "eq",
                                       "value": "$2"}]}) == "$2"


def test_DERIN_IC_ICE_DE_YAKALANIR():
    assert _cozulmemis_referans({"a": [{"b": {"c": ["$7"]}}]}) == "$7"


def test_TEMIZ_SORGU_GECER():
    assert _cozulmemis_referans(
        {"cube": "parti", "measures": ["toplam_fire_kg"],
         "filters": [{"dimension": "makine", "operator": "eq", "value": "RAM-2"}]}) is None


def test_DOLAR_ILE_BASLAYAN_HER_SEY_REFERANS_DEGILDIR():
    """⚠ `$` bir para birimi de olabilir; kural `_REF` desenidir, `startswith` değil."""
    assert _cozulmemis_referans({"filters": [{"value": "$ USD"}]}) is None
    assert _cozulmemis_referans({"filters": [{"value": "100$"}]}) is None


def test_PLAN_REDDEDILIR_VE_GEREKCE_YOL_GOSTERIR(schema):
    """🔴 Red **sessiz olamaz**: garsonun planı düzeltebilmesi için ne yapacağını söyler."""
    index = {c["name"]: c for c in schema["cubes"]}
    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "parti",
                                         "measures": ["toplam_fire_kg"],
                                         "filters": [{"dimension": "makine",
                                                      "operator": "eq",
                                                      "value": "$1"}]}}]}
    with pytest.raises(PlanHatasi) as hata:
        dogrula(plan, index=index)
    metin = str(hata.value)
    assert "çözülmemiş referans" in metin and "$1" in metin
    assert "BAGLA" in metin, "gerekçe düzeltme yolunu göstermeli"


def test_A9_SINIFI_VAR():
    """*Sayılmayan bir red, olmayan bir red gibi davranır.*"""
    from app.plan_garson import red_sinifi

    assert red_sinifi("adım 1: `cube_query` içinde çözülmemiş referans `$2` var.") \
        == "cozulmemis_referans"
