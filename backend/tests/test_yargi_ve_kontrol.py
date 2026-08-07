"""🔴 İki canlı curl bulgusu: **yargı sınırı** (§18.2) ve **kontrol karakteri** (§16.3).

## Yargı — *"bu ay iyi miyiz kötü müyüz"* → *"ort oee çıkarabilirim — hangi dönem için?"*

Kullanıcı **yargı** istedi; sistemde eşik/hedef yok ve korpusun **açık yasağı** var:
*"iyi/kötü yargısını bir eşik uydurarak vermek."* Sistem ölçü + dönem soruyor; kullanıcı
ikisini de verirse sonunda **yargı yerine bir sayı** alır.

*Bir eşiği uydurarak verilen yargı, yanlış bir sayıdan daha zor fark edilir: sayı
sorgulanır, yargı benimsenir.*

## Kontrol karakteri — `JSONDecodeError: Invalid control character`

Kullanıcıya görünen bir metne ham bir C0 karakteri sızınca **katı** bir çözücü
(`curl | jq`, ön yüz) yanıtın **tamamını** düşürür ve kullanıcı bunu *"sunucu hatası"*
diye görür — oysa cevap doğruydu.

⚠ Temizlik **çıkışta**: metin üç ayrı üreticiden gelebiliyor (katalog · LLM · şablon) ve
üçünde ayrı ayrı temizlemek, bir gün ikisinde temizlemek demekti.
*Bir çıkışı korumanın yeri, çıkıştır.*
"""

from __future__ import annotations

import json

import pytest

from app import cube_router as cr
from app import yetenek
from tests.conftest import ask


@pytest.mark.parametrize("soru", ["bu ay iyi miyiz kötü müyüz",
                                  "oee iyi mi", "fire normal mi"])
def test_YARGI_SORUSU_SINIR_BEYANI_ALIR(schema, soru):
    s = yetenek.kapsam_disi(cr._norm(soru), schema)
    assert s is not None and s.tur == "yargi", f"🔴 yargı sınırı konuşmadı: {s}"
    assert "eşik" in s.mesaj or "hedef" in s.mesaj
    assert "uydur" in s.mesaj.lower(), "🔴 eşik uydurmadığımız SÖYLENMİYOR"


def test_SAYI_SORUSU_ETKILENMEDI(schema):
    """⚠ Genişlemenin sınırı: *"bu ay ciro"* bir yargı değil. *Bir kuralı düzeltmek,
    komşusunu bozma hakkı vermez.*"""
    assert yetenek.kapsam_disi(cr._norm("bu ay ciro"), schema) is None
    assert yetenek.kapsam_disi(cr._norm("makine bazında oee"), schema) is None


def test_UCTAN_UCA_YARGI_DONEM_SORMUYOR(client):
    d = ask(client, "bu ay iyi miyiz kötü müyüz")
    assert "hangi dönem" not in (d.get("note") or "").lower(), (
        f"🔴 yargı sorusuna dönem soruldu: {d.get('note')!r}")


def test_CIKIS_KATI_JSON_COZUCUYU_KIRMIYOR(client):
    """🔴 Kapının asıl iddiası: yanıt `json.loads`'tan **katı** modda geçer."""
    for q in ("bu neden düşük", "peki bu neden düşük", "teşekkürler"):
        d = ask(client, q)
        ham = json.dumps(d, ensure_ascii=False)
        json.loads(ham, strict=True)      # kontrol karakteri varsa BURADA patlar
        for alan in ("note", "soz"):
            v = d.get(alan)
            if isinstance(v, str):
                assert not any(ch < " " and ch not in "\n\t" for ch in v), (
                    f"🔴 {q!r} → `{alan}` alanında ham kontrol karakteri")
