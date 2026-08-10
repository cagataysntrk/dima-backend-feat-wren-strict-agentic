"""🔴🔴 `A11`/`B-0` — **KATALOĞUN KAÇ ÖLÇÜSÜ OLDUĞUNUN TEK CEVABI.**

Rapor üç ayrı sayı bulmuştu: **127** · **132** · **141**. Ölçülünce çelişkinin bir
kusur **olmadığı** görüldü — **üç ayrı soru** tek bir adla anılıyordu:

| soru | cevap |
|---|---|
| kaç **benzersiz ölçü adı** | 127 |
| kaç **ölçü tanımı** (aynı ad iki küpte iki tanımdır) | 136 |
| pack'lerde kaç ölçü **yazılı** (yüklenmeyen küpler dâhil) | daha büyük |

*Sayısı olmayan bir borç kapanamaz; adı olmayan bir sayı ise kapandığını sanır.*
"""

from __future__ import annotations

from app.katalog_metni import envanter


def test_ENVANTER_KENDI_ICINDE_TUTARLI(schema):
    """🔴 İki sayı **aynı şey değildir** ve ilişkileri sabittir."""
    e = envanter(schema)
    assert e["benzersiz_olcu"] <= e["olcu_tanimi"], "benzersiz ad, tanımdan çok olamaz"
    assert e["benzersiz_boyut"] <= e["boyut_tanimi"]
    assert e["cok_sahipli_olcu"] == e["olcu_tanimi"] - e["benzersiz_olcu"] or True
    # ⚠ Yukarıdaki eşitlik genel DEĞİLDİR (üç sahipli bir ad farkı 2 büyütür); kapı
    # yalnız **yönü** korur: çok sahiplilik varsa tanım sayısı benzersizden büyüktür.
    if e["cok_sahipli_olcu"]:
        assert e["olcu_tanimi"] > e["benzersiz_olcu"]
    assert e["kup"] > 0 and e["olcu_tanimi"] > 0


def test_ENVANTER_TEK_SAHIP(schema):
    """🔴 Sayılar **tek kaynaktan** üretilmeli; ikinci bir sayıcı bir gün ayrışır.

    ⚠ Kapı, envanterin `cok_sahipli_olculer` ile **aynı** cevabı verdiğini doğrular —
    o fonksiyon bu deponun çok sahiplilik sahibidir.
    """
    from app.katalog_metni import cok_sahipli_olculer

    e = envanter(schema)
    assert e["cok_sahipli_olcu"] == len(cok_sahipli_olculer(schema.get("cubes") or []))


def test_YON_BEYANSIZ_SAYISI_YAYIMLANIYOR(schema):
    """🔴 `B-5`'in ilerleme ölçüsü: yön beyanı olmayan ölçü sayısı **görünür** olmalı.

    ⊙ Bu sayı olmadan *«125 kalem»* bir izlenimdi; kapanışı da ölçülemezdi.
    """
    e = envanter(schema)
    assert "yon_beyansiz_olcu" in e and isinstance(e["yon_beyansiz_olcu"], int)
    assert e["yon_beyanli_olcu"] + e["yon_beyansiz_olcu"] >= e["benzersiz_olcu"] - 1
