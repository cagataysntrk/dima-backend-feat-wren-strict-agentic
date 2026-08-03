"""FAZ F — KATALOG BELİRSİZLİĞİ, LLM TAHMİNİNİ ÖNCELER (bayraklı).

## Canlıda ölçülen vaka (3 Ağustos 2026)

    "bu yıl bakiye" → source=cube+llm · cube=mizan · confidence=0.85 · chip YOK

Oysa `bakiye` katalogda **iki** cube'un ölçüsüdür (`cari` · `mizan`) ve §6.1g'nin
netleştirme chip'i tam bunun için var. CI'da (LLM yok) chip ateşliyor; **üretimde
Intent-JSON onu gölgeliyor** — olasılıksal bir 2/3 oyu, **deterministik olarak BİLİNEN**
bir belirsizliği eziyor.

Bu, §1.7'nin dersinin yeni bir kapıdan girişi (*"yapısal geçerlilik ≠ semantik doğruluk"*).
Gerçekten belirsiz bir kelimede **doğru cevap yoktur**; herhangi bir seçim yazı-turadır ve
`0.85` rozetiyle sunulması onu **daha kötü** yapar.

## Nüfus ÖLÇÜLDÜ (LLM'siz, 384 ölçü sinonimi taranarak)

    katalogda ≥2 SAHİP + route ÇÖZEMİYOR : 53   ← bu kapının nüfusu
    katalogda ≥2 SAHİP ama route ÇÖZÜYOR : 20   ← DOKUNULMAZ

İkincisi kritik: `route()` çözebiliyorsa belirsizlik **zaten kırılmıştır** (2a-3'ün
*"en spesifik ölçü kazanır"* kuralı) ve kapı oraya karışmaz.

## Bu testler neden SAHTE bir `select_cube` kullanıyor

Kural-tabanlı sağlayıcıda `select_cube` **yoktur** → Intent yolu offline zaten atlanır ve
bayrak farkı **görünmez**. Gerçek sağlayıcıyla ölçmek kota harcar. Sahte bir seçici,
sırayı **API'ye hiç dokunmadan** kanıtlar: bayrak kapalıyken LLM çağrılır, açıkken
**çağrılmadan** netleştirme döner.
"""

from __future__ import annotations

import json

import pytest

from lab.nl_accuracy import _BayrakZorla


class _SahteSecici:
    """`select_cube` taşıyan minimal sağlayıcı — çağrıldığını KAYDEDER."""

    def __init__(self, cevap: dict):
        self.cevap, self.cagri = cevap, 0

    def select_cube(self, question, catalog, sema=None):
        self.cagri += 1
        return json.dumps(self.cevap)


@pytest.fixture
def sahte_llm(client, monkeypatch):
    s = _SahteSecici({"cube": "mizan", "measures": ["bakiye"],
                      "dimensions": [], "timeDimensions": [], "filters": []})
    monkeypatch.setattr(client.app.state, "llm", s, raising=False)
    return s


def test_BAYRAK_KAPALI_iken_LLM_CAGRILIYOR(client, sahte_llm):
    """Bugünkü davranış — KURAL B'nin tabanı: kapalıyken hiçbir şey değişmemeli."""
    from tests.conftest import ask

    with _BayrakZorla("netlestirme_onceligi", acik=False):
        ask(client, "bu yıl bakiye", execute=False)
    assert sahte_llm.cagri > 0, "bayrak kapalıyken Intent-JSON çağrılmalıydı"


def test_BAYRAK_ACIK_iken_LLM_HIC_CAGRILMIYOR(client, sahte_llm):
    """Kapının ASIL iddiası: belirsizlik biliniyorsa LLM'e **sorulmaz bile**.
    Yalnız cevabı değiştirmek yetmez — maliyet de doğmamalı."""
    from tests.conftest import ask

    with _BayrakZorla("netlestirme_onceligi", acik=True):
        d = ask(client, "bu yıl bakiye", execute=False)
    assert sahte_llm.cagri == 0, (
        "bayrak AÇIKKEN Intent-JSON yine çağrıldı — netleştirme ÖNCELEMİYOR")
    chips = [s["label"] for s in (d.get("suggestions") or [])]
    assert len(chips) >= 2, f"netleştirme chip'i gelmedi: {chips}"
    assert any("cari" in c for c in chips) and any("mizan" in c for c in chips), \
        f"chip'ler AYIRT EDİCİ değil (cube ile nitelenmeli): {chips}"


def test_ACIKKEN_de_ROUTE_cozdugune_DOKUNMUYOR(client, sahte_llm):
    """`route()` belirsizliği ZATEN kırdıysa (2a-3 spesifiklik) kapı karışmamalı —
    ölçüldü: 20 sinonim bu sınıfta ve kapsam kaybı yaşamamalı."""
    from tests.conftest import ask

    for q, beklenen in (("bu yıl sapma yüzdesi", "enerji_sapma"),
                        ("bu yıl elektrik tüketimi", "enerji_makine")):
        with _BayrakZorla("netlestirme_onceligi", acik=True):
            d = ask(client, q, execute=False)
        assert (d.get("cube_query") or {}).get("cube") == beklenen, \
            f"{q!r} kapıya takıldı — route çözmüştü, dokunulmamalıydı"
    assert sahte_llm.cagri == 0, "route çözdüğü hâlde LLM çağrıldı"


def test_KAPI_route_COZEMEDIGINDE_calisiyor():
    """Koşul `route_hit is None` ile bağlı olmalı — aksi hâlde çözülmüş soruları da keser."""
    import inspect

    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod.ask)
    i = govde.index('"netlestirme_onceligi" in resolve_for')
    pencere = govde[max(0, i - 200):i + 100]
    assert "route_hit is None" in pencere, \
        "kapı `route_hit is None` koşuluna bağlı değil — çözülmüş soruları da keser"


def test_KURAL_TEK_YERDE_yasiyor():
    """Aynı netleştirme iki yerden çağrılıyor (bayraklı: Intent'ten ÖNCE; bayraksız:
    bugünkü yerinde). İki kopya yazmak, bu deponun defalarca ölçtüğü *kimlik
    asimetrisi*ni üretirdi."""
    import inspect

    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod.ask)
    assert govde.count("_olcu_belirsizligi_netlestir(") >= 3, (
        "ortak yardımcı iki çağrı yerinden birinde kullanılmıyor olabilir "
        "(tanım + iki çağrı bekleniyor)")


def test_VARSAYILAN_KAPALI_ve_gerekcesi_YAZILI():
    """KURAL B. Kapsam kaybı ile kazanç kıyası gerçek sağlayıcıyla ÖLÇÜLMEDİ (kota);
    ölçmeden açmak 2a-1'in `elektrik` hatasını tekrarlamak olurdu."""
    import pathlib

    import yaml

    kok = pathlib.Path(__file__).resolve().parents[1]
    veri = yaml.safe_load((kok / "demo" / "packs" / "features.yml").read_text(
        encoding="utf-8")) or {}
    blok = veri.get("features") or veri
    assert blok.get("netlestirme_onceligi") == "off", \
        "bayrak varsayılan AÇIK — kapsam kaybı ölçülmeden açılamaz"

    from app.features import FLAG_REGISTRY

    kayit = FLAG_REGISTRY.get("netlestirme_onceligi")
    assert kayit and kayit["description"], "admin panelinde adsız bayrak"
    assert "ölçül" in kayit["description"].lower(), \
        "açılma ön koşulu (kapsam kaybı ölçümü) kayıtta yazılı değil"
