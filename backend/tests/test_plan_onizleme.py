"""🔴 `§63` — **ÇOK ADIM (N ≥ 2) → HER ZAMAN ÖNİZLEME** (`§28.3`).

## Planın kuralı — bir bayrak değil, bir KARAR TABLOSU

| garson çıktısı | davranış | gerekçe |
|---|---|---|
| **tek adım**, garson emin | 🟢 koşar, pill'ler makbuz olur | salt-okuma · ucuz |
| **tek adım**, garson kararsız | 🔵 pill'ler önerilir, kullanıcı onaylar | marj kapısı |
| **çok adım** (N ≥ 2) | 🔴 **her zaman önizleme** | bütçe + **%25 onarım tutma** |
| yazma fiili | 🔴 senkron onay | geri alınamaz iş |

Ve belgenin **başlığı** işin kendisi: *«route ve garson, KARAR VERİCİ olmaktan çıkıp
TAHMİNCİ oluyor … kullanıcı KARARI VERİR (bir tık)»* (`§3.1`).

⊙ Ölçülmüş gerekçe: *«bugün plan yazılıp KOŞUYOR; 7. adımda çökerse kullanıcı SONDA
öğreniyor — onarım tutma %25, payda 16.»*

> *Bir planı koşmadan önce görünür yapmak, onu onarmaktan ucuzdur.*

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | onaysız çağrı **koşmaz** — `source="onizleme"` |
| 2 | önizleme **adımları** taşır (kullanıcı neyi onayladığını görmeli) |
| 3 | `kos=true` **koşar** 🆃 — kapı özelliği öldürmesin |
| 4 | **geçersiz plan da gösterilir** — ürünün kendi gerekçesiyle |

⚠ Dördüncüsü `§7`'nin *«dürüst ret»* şartı: kullanıcı neyin tutmadığını görmeden
düzeltemez.
"""

from __future__ import annotations

import pytest

_CAPA = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}


@pytest.fixture
def makro_cagir(client):
    def _cagir(**ek):
        govde = {"ad": "neden", "capa": _CAPA, "boyut": "makine",
                 "metin": "OEE neden bu seviyede?", **ek}
        return client.post("/oneri/makro", json=govde).json()
    return _cagir


def test_ONAYSIZ_CAGRI_KOSMAZ(makro_cagir):
    """🔴 **ASIL DEĞİŞMEZ.** Çok adımlı plan onaysız koşmaz."""
    d = makro_cagir()
    assert d.get("source") == "onizleme", (
        f"🔴 plan onaysız koştu → source={d.get('source')!r}; `§28.3`: «çok adım → HER "
        "ZAMAN önizleme»")
    assert "result" not in d, "🔴 önizleme sonuç taşıyor — demek ki koşmuş"


def test_ONIZLEME_ADIMLARI_TASIR(makro_cagir):
    """Kullanıcı **neyi** onayladığını görmeli: adımlar sıralı ve fiilleriyle."""
    adimlar = makro_cagir().get("adimlar") or []
    assert len(adimlar) >= 2, f"🔴 önizleme adımsız: {adimlar}"
    assert [a["sira"] for a in adimlar] == list(range(1, len(adimlar) + 1)), (
        "🔴 adım sırası bozuk — kullanıcı hangi adımı onayladığını bilemez")
    for a in adimlar:
        assert a.get("fiil") and a.get("metin"), f"🔴 adım eksik: {a}"


def test_ZIT_OLCUT_ONAYLI_CAGRI_KOSAR(makro_cagir):
    """🆃 Kapı özelliği **öldürmesin**: onay geldiğinde plan gerçekten koşmalı."""
    d = makro_cagir(kos=True)
    assert d.get("source") != "onizleme", "🔴 onaylı çağrı da koşmadı — makro öldü"
    assert d.get("adim_sayisi"), f"🔴 koşum adım sayısı bildirmiyor: {d}"


def test_GECERSIZ_PLAN_DA_GOSTERILIR(client):
    """⊘ Dürüst ret: geçersiz plan **gizlenmez**, gerekçesiyle görünür.

    ⚠ `neden` makrosu **boyut** ister; boyutsuz çağrı ürünün kendi 400'ünü üretir —
    o mesaj kullanıcıya **ulaşmalı**, sessiz bir boş liste değil.
    """
    r = client.post("/oneri/makro", json={"ad": "neden", "capa": _CAPA, "metin": "x"})
    assert r.status_code in (200, 400), f"🔴 beklenmedik durum: {r.status_code}"
    govde = r.json()
    metin = str(govde.get("detail") or govde.get("note") or "")
    assert metin.strip(), f"🔴 gerekçesiz ret — kullanıcı neyi düzelteceğini bilemez: {govde}"
