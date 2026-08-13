"""🔴 `§52` — **FAZ 6'NIN KENDİ `KURAL B` KAPISI** (bugüne kadar hiç yazılmamıştı).

## Ölçülen boşluk

Bir denetim ajanı fazın kapı listesini taradı: `test_oneri_katmani_kural_b.py` **yok**.
Ölçtüm, sebebi daha kötüydü — **savunacak bir şey de yoktu**:

    grep oneri_katmani app/routers/oneri.py  →  0

Bayrak `features.yml`'de tanımlı, `features.py`'de ilan edilmiş, ön yüzde okunuyor
(`OneriSeridi.tsx:169`, `PillSatiri.tsx:73`) — ama **sunucuda hiç denetlenmiyordu**.
Üstelik ön yüzün kendi yorumu şunu iddia ediyordu: *«`oneri_katmani` **sunucu tarafıdır
ve bir YETKİdir**»*.

*Bir yetkiyi istemcide uygulamak, onu uygulamamaktır* — kapalı bir kiracı ucu doğrudan
çağırdığında öneri **yine** üretiliyordu.

## Bu kapının savunduğu üç şey

| # | savunulan |
|---|---|
| 1 | bayrak **kapalıyken** `/oneri` hiçbir öneri/aday döndürmez (`KURAL B`) |
| 2 | kapalı hâl **404 değil**: şekli aynı, içeriği boş — kapalı bir özellik bir arıza değildir |
| 3 | bayrak **açıkken** uç çalışır 🆃 — kapının kendisi özelliği öldürmesin |

⚠ Üçüncüsü **zıt ölçüttür**: yalnız *«kapalıyken boş»* ölçseydi, ucu tamamen kırmak da
kapıyı yeşil bırakırdı 🆐.
"""

from __future__ import annotations

import pytest

from app.routers import oneri as _uc


class _Sahte:
    """Bayrak çözümünü **taklit etmez, yerine geçer**: kapı bir kiracı kurulumunu değil
    *«bayrak kapalıysa ne olur»* sözleşmesini ölçer."""

    def __init__(self, acik: bool) -> None:
        self.acik = acik


@pytest.fixture
def bayrak(monkeypatch):
    def _ayarla(acik: bool) -> None:
        monkeypatch.setattr(_uc, "_katman_acik", lambda *_a, **_k: acik)
    return _ayarla


def test_KAPALIYKEN_BOS_DONER(client, bayrak):
    """🔴 `KURAL B` — kapalı bayrak, faz öncesiyle **eşdeğer** davranış."""
    bayrak(False)
    d = client.get("/oneri", params={"q": "fire"}).json()
    assert d.get("oneriler") == [], f"🔴 kapalıyken cümle döndü: {d.get('oneriler')}"
    assert d.get("adaylar") == [], f"🔴 kapalıyken aday döndü: {d.get('adaylar')}"


def test_KAPALIYKEN_404_DEGIL(client, bayrak):
    """Kapalı bir özellik bir **arıza** değildir: istemci hata dalına düşmemeli."""
    bayrak(False)
    r = client.get("/oneri", params={"q": "fire"})
    assert r.status_code == 200, f"🔴 kapalı katman {r.status_code} döndürdü — arıza gibi"
    assert set(r.json()) >= {"oneriler", "adaylar"}, "🔴 yanıt şekli değişti"


def test_ZIT_OLCUT_ACIKKEN_CALISIR(client, bayrak):
    """🆃 Kapı özelliği **öldürmesin**: bayrak açıkken uç gerçekten cümle üretmeli."""
    bayrak(True)
    d = client.get("/oneri", params={"q": "fire"}).json()
    assert d.get("oneriler"), "🔴 bayrak açıkken hiç öneri yok — kapı özelliği kırmış"


def test_BAYRAK_SUNUCUDA_OKUNUYOR():
    """🆆 Zincir: uç bayrağı **gerçekten** soruyor mu.

    Ölçülen kusur tam buydu — ön yüz *«sunucu tarafı»* diyordu, sunucu bakmıyordu.
    """
    from pathlib import Path

    kaynak = Path(_uc.__file__).read_text(encoding="utf-8")
    assert "oneri_katmani" in kaynak, (
        "🔴 uç bayrağı hiç anmıyor — yetki yine yalnız istemcide")
    assert "resolve_for" in kaynak, "🔴 bayrak çözücü çağrılmıyor"
