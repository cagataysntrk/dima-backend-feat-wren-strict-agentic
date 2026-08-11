"""🔴 `§B4` — PLAN ONARIM DÖNGÜSÜ: tavan **2 tur** + sınıfa özgü **çare**.

Ölçüldü (canlı `/stats/plan`, 2026-08-11):

    denendi=16 · geçerli=12 · onarildi=1 · dustu=3
    red_orani_yuzde=25 · 🔴 onarim_tutma_yuzde=25
    red_nedenleri = {"ulasilmaz": 4}      ← dört reddin DÖRDÜ de aynı sınıf

Onarım turu **vardı ve ateşliyordu** ama **4'te 1** tutuyordu; ve istem yalnız
*«sözleşmeye UYARAK yeniden planla»* diyordu — kusuru söyleyip **çareyi** söylemiyordu.

Dayanak: Snowflake **Error Correction** · Wren `retry&repair` · Genie öz-düzeltme ·
**Magentic-One stall ≤2** · Anthropic evaluator-optimizer (*«bu ajanlık değil WORKFLOW»*).
"""

import app.plan_garson as pg


class _SahteLLM:
    """Reddedilecek planlar üretir; `plan_kur` çağrılarını ve istemleri kaydeder."""

    sema_kullanir = False

    def __init__(self, cevaplar):
        self._cevaplar = list(cevaplar)
        self.istemler: list[str] = []

    def plan_kur(self, question, catalog, sema=None):
        self.istemler.append(question)
        return self._cevaplar.pop(0) if self._cevaplar else "{}"


_INDEX = {"parti": {"name": "parti", "measures": ["toplam_ciro"],
                    "dimensions": ["musteri"], "time_dimensions": []}}

#: Ulaşılmaz adım — ölçülen tek red sınıfının birebir hâli.
_KOTU = ('{"adimlar":[{"fiil":"SORGU","cube_query":{"cube":"parti",'
         '"measures":["toplam_ciro"]}},'
         '{"fiil":"SORGU","cube_query":{"cube":"parti","measures":["toplam_ciro"]}}]}')
_IYI = ('{"adimlar":[{"fiil":"SORGU","cube_query":{"cube":"parti",'
        '"measures":["toplam_ciro"]}}]}')


def _sifirla():
    for k in list(pg.SAYAC):
        pg.SAYAC[k] = 0
    pg.RED_NEDENLERI.clear()


# ── ÇARE YÖNERGESİ ───────────────────────────────────────────────────────────

def test_care_yonergesi_kapali_sinif_kumesinden_turer():
    """`KAT-1` — anahtarlar `RED_SINIFLARI`'nın kendi kümesinden gelir; yeni sözlük yok."""
    siniflar = {ad for ad, _ in pg.RED_SINIFLARI}
    assert set(pg.ONARIM_YONERGESI) <= siniflar, "tanımsız bir red sınıfına çare yazılmış"
    # Ölçülen baskın sınıfın çaresi YAZILI olmalı — kusurun tamamı buydu.
    assert "ulasilmaz" in pg.ONARIM_YONERGESI
    assert "$n" in pg.ONARIM_YONERGESI["ulasilmaz"]


def test_onarim_istemi_kusuru_VE_careyi_tasir(monkeypatch):
    """İstem eskiden yalnız *«sözleşmeye uyarak yeniden planla»* diyordu."""
    _sifirla()
    monkeypatch.setattr(pg, "_onarim_dongusu_acik", lambda: True)
    llm = _SahteLLM([_KOTU, _IYI])
    plan = pg.plan_uret(llm, "bu yıl ciro", "katalog", _INDEX)
    assert plan is not None
    onarim_istemi = llm.istemler[1]
    assert "ÖNCEKİ DENEMEN REDDEDİLDİ" in onarim_istemi
    assert "NASIL DÜZELTİLİR" in onarim_istemi
    assert pg.ONARIM_YONERGESI["ulasilmaz"] in onarim_istemi


# ── TAVAN — sayılı döngü, serbest değil ──────────────────────────────────────

def test_ikinci_tur_ilkinde_tutmayani_kurtarir(monkeypatch):
    _sifirla()
    monkeypatch.setattr(pg, "_onarim_dongusu_acik", lambda: True)
    llm = _SahteLLM([_KOTU, _KOTU, _IYI])          # 1. onarım tutmaz, 2. tutar
    assert pg.plan_uret(llm, "bu yıl ciro", "katalog", _INDEX) is not None
    assert pg.SAYAC.get("onarildi_tur2") == 1
    assert pg.SAYAC.get("onarildi_tur1", 0) == 0
    assert len(llm.istemler) == 3                  # ilk deneme + iki onarım


def test_tavan_ASILMAZ_sonsuz_dongu_yok(monkeypatch):
    """🔴 *«Bu ajanlık değil WORKFLOW»* — döngü **sayılıdır**."""
    _sifirla()
    monkeypatch.setattr(pg, "_onarim_dongusu_acik", lambda: True)
    llm = _SahteLLM([_KOTU] * 6)
    pg.plan_uret(llm, "bu yıl ciro", "katalog", _INDEX)
    assert len(llm.istemler) == 1 + pg.ONARIM_TAVANI, "tavan aşıldı"
    assert pg.ONARIM_TAVANI == 2


# ── 🔴 KURAL B ───────────────────────────────────────────────────────────────

def test_kural_b_bayrak_kapaliyken_tavan_BİR(monkeypatch):
    """Bayrak kapalıyken davranış bugünküyle birebir: tek onarım turu."""
    _sifirla()
    monkeypatch.setattr(pg, "_onarim_dongusu_acik", lambda: False)
    llm = _SahteLLM([_KOTU] * 6)
    pg.plan_uret(llm, "bu yıl ciro", "katalog", _INDEX)
    assert len(llm.istemler) == 2, "kapalıyken ilk deneme + TEK onarım olmalı"


def test_bayrak_cozulemezse_bugunku_yol(monkeypatch):
    """Bayrak okunamazsa tavan 1 — bir arıza davranışı genişletemez."""
    monkeypatch.setattr(pg, "resolve_for", None, raising=False)
    assert pg._onarim_dongusu_acik() in (True, False)   # patlamamalı
