"""Canlı bulgu (31 Temmuz 2026): `interpretation`/`next_steps`/`recommendations` ÖNCEDEN
yalnız `/cube` (chip düzenlemesi) endpoint'inin kapanışında ekleniyordu — `/ask`'in TEK
choke-point'i olan `_finish()` bunları hiç çağırmıyordu. Sonuç: `/ask`'ten gelen HİÇBİR yanıt
(ilk mesaj dahil) bu alanları taşımıyordu; kullanıcı bunları yalnız BİR SONRAKİ `/cube`
isteğinde (bir chip'e tıklayınca) görüyordu. Bu testler `/ask`'in kendisinin artık bu alanları
doldurduğunu kanıtlar — `/cube`'un davranışına dokunulmadı (zaten doğruydu, regresyon riski yok)."""

from __future__ import annotations

from tests.conftest import ask


def test_ask_fresh_cube_response_has_interpretation(client):
    """İLK mesaj (henüz hiçbir /cube çağrısı yapılmamış) — `interpretation` DOLU gelmeli
    (flag `cikti_yorumlama` demo'da varsayılan `beta` — resolve_for() bunu zaten açık sayar)."""
    d1 = ask(client, "makine bazında ortalama oee")
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    assert d["source"] == "cube"
    assert d["interpretation"] is not None
    assert d["interpretation"].get("summary")


def test_ask_fresh_cube_response_has_next_steps(client):
    """`next_steps` (K2, flag `next_steps`) — kullanılmayan boyut/ölçü/zaman chip'leri."""
    d1 = ask(client, "makine bazında ortalama oee")
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    assert d["source"] == "cube"
    assert len(d["next_steps"]) > 0
    assert all("cube_query" in s for s in d["next_steps"])


def test_ask_takip_response_also_has_interpretation(client):
    """Yapısal takip (deterministic_refine yolu) da AYNI `_finish()`'ten geçer — ilk
    mesajla SINIRLI bir düzeltme olmadığını kanıtlar."""
    d1 = ask(client, "makine bazında ortalama oee")
    d1 = ask(client, "tüm zamanlar", cube_query=d1["cube_query"])
    assert d1["source"] == "cube"
    d2 = ask(client, "hat bazında da göster", cube_query=d1["cube_query"], history=[d1["question"]])
    assert d2["source"] == "cube"
    assert d2["interpretation"] is not None
