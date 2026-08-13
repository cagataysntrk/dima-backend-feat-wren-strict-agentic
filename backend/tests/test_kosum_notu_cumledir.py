"""🔴 `§67` — **`note` BİR CÜMLEDİR, BİR KOŞUCU İÇ LİSTESİ DEĞİL.**

## Ölçülen kusur (canlı `s30`, curl — `/plan/kos` **ve** `/oneri/makro`)

```
note = [{'sira': 1, 'fiil': 'SORGU', 'satir': 1}, {'sira': 2, 'fiil': 'SORGU', …}]
```

Arayüz `note`'u **düz metin** basıyor; kullanıcı bir Python listesi okuyordu. Sebep tek
satırdı ve **adaşlıktan** doğdu:

| ad | ne | kim okuyor |
|---|---|---|
| `plan_kosucu.kos()["makbuz"]` | adım başına **kayıt listesi** (`sira·fiil·satir`) | koşucu içi |
| `plan_tuketici.makbuz(plan)` | **cümle** (*«Bu cevap 5 adımda üretildi…»*) | kullanıcı |

`kosum_yaniti` `out.get("makbuz")` okuyordu — yani **veriyi**, cümleyi değil. Merdiven
yolu (`cevap()`) aynı cümleyi **doğru** kuruyordu; iki yol ayrışmıştı ㊲.

> *Aynı adı taşıyan iki şeyden biri veri, öteki cümle ise, `get` ile okunan her zaman
> yanlış olanıdır* 🅬 — çünkü sözlük erişimi tip sormaz.

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | `note` **metin**, ve makbuz cümlesiyle başlıyor |
| 2 | içinde **koşucu iç alanı** (`'sira':` · `'satir':`) yok |
| 3 | iki yol **aynı sahibi** çağırıyor (`cevap_notu`) ㊲ |
| 4 | 🆃 makbuz **hâlâ** adımları sayıyor — temizlik notu boşaltmasın |
"""

from __future__ import annotations

import pytest

_CAPA = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}


@pytest.fixture
def kosum(client):
    return client.post("/oneri/makro", json={
        "ad": "neden", "capa": _CAPA, "boyut": "makine",
        "metin": "OEE neden bu seviyede?", "kos": True}).json()


def test_NOTE_METINDIR(kosum):
    """🔴 **ASIL DEĞİŞMEZ.** Kullanıcı bir liste okumaz."""
    note = kosum.get("note")
    assert isinstance(note, str), f"🔴 `note` {type(note).__name__} — arayüz onu düz basar"
    assert "adımda üretildi" in note, f"🔴 makbuz cümlesi yok: {note[:120]!r}"


def test_KOSUCU_IC_ALANI_SIZMAZ(kosum):
    """⚠ `sira`/`satir` bir **koşucu iç sözleşmesidir**; kullanıcı cümlesinde işi yok."""
    note = str(kosum.get("note"))
    for iz in ("'sira'", "'satir'", "'fiil'", "{'"):
        assert iz not in note, f"🔴 iç alan sızdı ({iz!r}): {note[:160]!r}"


def test_IKI_YOL_AYNI_SAHIBI_CAGIRIYOR():
    """㊲ Merdiven ve koşum uçları **tek** cümle üreticisini çağırmalı; iki gövde bir gün
    ayrışır — ve bu kusur tam olarak öyle doğdu."""
    import inspect

    from app import plan_tuketici as pt

    for ad in ("cevap", "kosum_yaniti"):
        kaynak = inspect.getsource(getattr(pt, ad))
        assert "cevap_notu(plan, out)" in kaynak, (
            f"🔴 `{ad}` notu kendi kuruyor — iki cümle bir gün ayrışır ㊲")


def test_ZIT_OLCUT_MAKBUZ_HALA_ADIM_SAYIYOR():
    """🆃 Kapının kurbanı: `note`'u *«temizlemek»* adına boşaltmak da kapıyı yeşil
    bırakırdı. Makbuz `O-5`'in zeminidir — kaç adımda ve **hangi** adımlarla."""
    from app.plan_tuketici import makbuz

    m = makbuz({"adimlar": [{"fiil": "SORGU", "cube_query": _CAPA},
                            {"fiil": "ANLAT", "kaynaklar": ["$1"]}]})
    assert "2 adımda üretildi" in m and "1." in m and "2." in m, (
        f"🔴 makbuz adımları saymıyor: {m!r}")
