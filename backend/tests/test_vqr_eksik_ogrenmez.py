"""🔴 **EKSİK NİYETLİ CEVAP «DOĞRULANMIŞ» SAYILAMAZ.**

## Canlı denetimde bulundu

    "şubatta ciro ocağa göre nasıl değişti"  →  source=vqr · 434 ms
                                                eksik_niyet=['kiyas','trend']

Yani **beyanlı kısmi** bir cevap, doğrulanmış soru deposuna girmişti.

⚠ Zararı **bileşik**: VQR merdivenin **İLK** basamağıdır. Deterministik yol iyileşse bile
(bu turda `Ö10` ile tam o soru düzeldi) kayıt onu **es geçtirir** — yani depo,
düzelttiğimiz kusuru **dondurup korur**.

⊙ `app/vqr.py`'nin kendi şerhi zaten uyarıyordu — *"dondurulmuş kayıt İYİLEŞMEZ, router
İYİLEŞİR"* — ama kural yalnız **replay**'e uygulanmıştı, **yazmaya** değil.

*Bir öğrenme deposu, öğrendiği şeyin eksik olduğunu bilmiyorsa öğrenmez — ezberler.*
"""

from __future__ import annotations

import inspect

from app.routers import ask as ask_mod


def test_BEYANLI_KISMI_CEVAP_VQR_A_YAZILMAZ():
    """Kapı metin tarar çünkü koruduğu şey bir **sıra**: kontrol `vqr.store` çağrısından
    ÖNCE olmak zorunda. Bir satır aşağı kayarsa kayıt yine yazılır."""
    src = inspect.getsource(ask_mod)
    i = src.index('resp, "eksik_niyet"')
    j = src.index("vqr.store(body.question,", i)
    assert j - i < 1600, (
        "🔴 eksik-niyet kontrolü `vqr.store`'dan koptu — arada bir dal doğmuş olabilir")
    assert "learn = False" in src[i:j], "🔴 kontrol öğrenmeyi KAPATMIYOR"


def test_KURAL_REPLAY_ICIN_ZATEN_VARDI_ve_YAZMAYA_TASINDI():
    """⊙ `app/vqr.py` dondurulmuş kaydın iyileşmediğini biliyordu ve bunu **yalnız
    okuma** tarafında uyguluyordu. Aynı gerekçe yazma tarafında da geçerli — ve orada
    daha ucuz: yazılmayan bir kayıt, sonradan atlanması gereken bir kayıt olmaz."""
    from app import vqr

    src = inspect.getsource(vqr)
    assert "_FEW_SHOT_ONLY_SOURCES" in src, (
        "⊘ replay kısıtı kalkmış — bu kapının dayandığı gerekçe bayat")
