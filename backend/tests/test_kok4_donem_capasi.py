"""🔴 KÖK-4 — **TAKİP TURUNDA DÖNEM ÇAPASI.** (denetim raporu KN-1)

Sondanın **en büyük tek kümesi**: 43 netleştirmenin 34'ü dönem sorusu, **26'sı takip
turunda** — ve **26/26'sında önceki turda dönem VARDI**.

```
tur 1  bu yıl makine bazında oee        ✅ dönem verildi
tur 2  en düşük hangisi                 ✅ aynı ölçü → dönem korunuyor
tur 3  o makinenin duruşları ne kadar   🔵 «Hangi dönem için?»   ← ölçü DEĞİŞTİ
```

⚠ Ve bileşik etkisi: dönem sorulunca `Bugün`/`Bu hafta`/`Bu ay` chip'i öneriliyor,
**üçü de veri aralığının dışında** (KN-5) → kullanıcı kendi ürününün önerisine tıklayıp
boş ekran görüyor. KÖK-4 tek başına bu döngüyü **kırar**.

## 🔴 `return None` KALDIRILMADI

Raporun anti-çözüm listesi **A4**: *"o dal bilinçli — farklı metrik gerçekten yeni bir
sorudur; kaldırmak ölçü karışması üretir."* Doğru çözüm dönemi soruya değil **OTURUMA**
bağlamaktır.
"""

from __future__ import annotations

import pytest

from app.donem_capasi import tasi
from tests.conftest import ask

ONCEKI = {"cube": "oee", "measures": ["ort_oee"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}


def test_UCTAN_UCA_OLCU_DEGISINCE_DONEM_KALIYOR(client):
    """🔴 **ASIL KAPI** — raporun ölçtüğü senaryonun birebir kendisi."""
    d1 = ask(client, "bu yıl makine bazında oee")
    assert d1["source"] == "cube"
    d2 = ask(client, "o makinenin duruşları ne kadar", cube_query=d1["cube_query"])
    assert d2["source"] == "cube", f"🔴 hâlâ netleştirmeye düşüyor: {d2.get('note')}"
    assert (d2.get("result") or {}).get("row_count", 0) > 0


def test_TASIMA_GORUNUR(client):
    """⚠ *Sessiz bir taşıma, sessiz bir varsayımdır.* Kullanıcı hangi dönemin geçerli
    olduğunu tahmin etmek zorunda kalmamalı — ve nasıl değiştireceğini bilmeli."""
    d1 = ask(client, "bu yıl makine bazında oee")
    d2 = ask(client, "o makinenin duruşları ne kadar", cube_query=d1["cube_query"])
    assert "dönemi korundu" in (d2.get("note") or ""), "🔴 taşıma sessiz"
    assert "01.01.2026" in (d2.get("note") or ""), "🔴 hangi dönem olduğu yazmıyor"


def test_ACIK_TALIMAT_CAPAYI_EZER(client):
    """🔴 *Bir bağlam, kendisini ezmek için verilmiş bir talimatı ezemez.*
    `tüm zamanlar` dendiğinde eski döneme geri dönmek, kullanıcının açık isteğini
    sessizce iptal etmek olurdu."""
    cq, tasindi = tasi({"cube": "oee", "measures": ["x"]}, ONCEKI, "tüm zamanlar")
    assert not tasindi and not (cq.get("filters") or [])


def test_KULLANICI_DONEM_VERDIYSE_DOKUNULMUYOR():
    """⚠ Bu turda dönem söylendiyse çapa **karışmaz** — yoksa iki dönem çakışırdı."""
    yeni = {"cube": "oee", "measures": ["x"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2025-01-01"}]}
    cq, tasindi = tasi(yeni, ONCEKI, "geçen yıl duruşlar")
    assert not tasindi and cq["filters"][0]["value"] == "2025-01-01"


def test_ONCEKI_TURDA_DONEM_YOKSA_TASINMAZ():
    cq, tasindi = tasi({"cube": "oee"}, {"cube": "oee", "measures": ["x"]}, "duruşlar")
    assert not tasindi


def test_YALNIZ_DONEM_TASINIR():
    """🔴 Cube · ölçü · kırılım · öteki filtreler **hiç dokunulmadan** kalır. Bu modülün
    tek işi, ölçü değişiminde düşen tek şeyi yerine koymaktır."""
    onceki = {**ONCEKI, "dimensions": ["makine"],
              "filters": [*ONCEKI["filters"],
                          {"dimension": "vardiya", "operator": "eq", "value": "Gece"}]}
    yeni = {"cube": "bakim", "measures": ["ariza_sayisi"], "dimensions": ["ariza_tipi"]}
    cq, tasindi = tasi(yeni, onceki, "arıza sayısı")
    assert tasindi
    assert cq["cube"] == "bakim" and cq["measures"] == ["ariza_sayisi"]
    assert cq["dimensions"] == ["ariza_tipi"]
    # ⚠ `vardiya=Gece` TAŞINMADI: o bir dönem değil, bir iş filtresidir.
    assert [f["dimension"] for f in cq["filters"]] == ["tarih"]


def test_ZAMAN_BOYUTU_ADI_HEDEF_CUBE_A_GORE(schema):
    """🔴 Zaman boyutunun ADI cube'a göre değişir (`tarih` · `donem_tarih` ·
    `acilis_tarihi`). Yeniden adlandırılmazsa var olmayan bir kolona filtre yazılır ve
    sorgu **çalışma anında** patlar — derlemede değil."""
    maliyet = next((c for c in schema["cubes"] if c["name"] == "maliyet"), None)
    if not maliyet:
        pytest.skip("⊘ maliyet cube yok")
    hedef = (maliyet.get("time_dimensions") or [None])[0]
    cq, tasindi = tasi({"cube": "maliyet", "measures": ["x"]}, ONCEKI, "birim maliyet",
                       cube_meta=maliyet)
    assert tasindi and cq["filters"][0]["dimension"] == hedef


def test_TASIYICI_ANAHTAR_SIZMIYOR(client):
    """🔴 `_capa_notu` bir **taşıyıcıdır**; vardığı yerde boşaltılmalı. Sızarsa
    `cube_query` cevaba kirli gider ve daha kötüsü SQL derleyicisine bilinmeyen bir
    alan olarak ulaşır."""
    d1 = ask(client, "bu yıl makine bazında oee")
    d2 = ask(client, "o makinenin duruşları ne kadar", cube_query=d1["cube_query"])
    assert "_capa_notu" not in (d2.get("cube_query") or {})
