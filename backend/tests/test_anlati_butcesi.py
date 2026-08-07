"""🔴 **SÜSÜN BÜTÇESİ** — canlı ölçüm: 2.936 / 22.564 / **69.399 ms**.

Aynı sağlayıcı (`deepseek-v4-flash`) aynı iş için 23 kat salındı. Ve anlatı bir
**süslemedir**: altındaki `summary` zaten yazılı ve doğru.

| tur | toplam | anlatı LLM | pay |
|---|---|---|---|
| *"makine bazında oee son 3 ay"* | 5.420 ms | 2.936 ms | %54 |
| *"aylara göre"* | 24.285 ms | 22.564 ms | %93 |
| *"çeyreklere böl"* | 🔴 **69.399 ms** | — | iki LLM çağrısı |

Aşılırsa anlatı **düşer**, cevap **düşmez** — `narration_guard`'ın kendi sözleşmesiyle
**aynı** en-kötü-durum: *"süssüz ama doğru"*.

⚠ Bütçe **çağırandadır**, sağlayıcıda değil: *"süs ne kadar bekletebilir"* bir **ürün
kararıdır**; sağlayıcıya koymak üç sağlayıcıda üç ayrı karar demekti.

*Bir süsün bütçesi, süslediği şeyin süresini aşamaz.*
"""

from __future__ import annotations

import inspect

from app import answer as answer_mod
from app.config import get_settings


def test_BUTCE_AYARLANABILIR_ve_MAKUL():
    s = get_settings()
    assert 0 < float(s.anlati_azami_saniye) <= 15, (
        "🔴 bütçe yok ya da süslemeye göre fazla geniş — ölçülen salınım 23 kat")


def test_BUTCE_ANLATI_CAGRISINA_UYGULANIYOR():
    src = inspect.getsource(answer_mod._anlati_ekle)
    # ⚠ Pencere çağrının **sonrasına** bakar: aşım dalı doğal olarak `result()`'tan
    # sonra gelir. İlk yazımda pencere geriye ağırlıklıydı ve kapı, koruduğu dalı
    # göremeden kırmızı verdi. *Bir kapı, aradığı şeyin bulunacağı yere bakmalı.*
    i = src.index('"llm.anlat"')
    yakin = src[i:i + 900]
    assert "result(timeout=" in yakin, "🔴 çağrı bir zaman sınırı olmadan koşuyor"
    assert "TimeoutError" in yakin, "🔴 aşım dalı yok"


def test_ASIMDA_CEVAP_DUSMEZ():
    """🔴 En kötü durum *"süssüz ama doğru"* olmalı — asla *"cevapsız"*."""
    src = inspect.getsource(answer_mod._anlati_ekle)
    i = src.index("TimeoutError")
    blok = src[i:i + 400]
    assert "return" in blok and "raise" not in blok, (
        "🔴 aşım cevabı düşürüyor — anlatı bir süs, cevap değil")


def test_ISIN_ARKA_PLANDA_BITMESI_KAYITLI():
    """⚠ Thread öldürülemez: iş arka planda biter, ama cevabı **bekletmez**. Bu bir
    sınırdır ve yazılı olmalı — okuyan kişi *"sızıntı mı"* diye sormadan görsün."""
    src = inspect.getsource(answer_mod._anlati_ekle)
    assert "arka planda" in src and "öldürülemez" in src
