"""🔴🔴 `A1` — **KASET**: kaydet, sonra diskten oynat. Ve *ölçtüğünü değiştirme*.

Bu dosya, kaseti yazarken **ölçülerek** bulunmuş dört kusurun kapısıdır. Dördü de
canlı koşumda görüldü, hiçbiri tahmin değil.

| # | kusur | ölçüm |
|---|---|---|
| 1 | Anlam yüzeyleri sarıldı, **taşıma** değil | canlı koşum **0 kayıt** verdi (`plan_kur` sarılmamıştı; `llm.py`'de 11+ yüzey var) |
| 2 | `k=3` örneklemesi **tek kayda çöktü** | oynatmada oy birliği zorla %100 → yol ayrıştı → **10 ıska** |
| 3 | Kayıt her seferinde **sıfırlıyordu** | tek bir boşluk için bütün korpus yeniden ödeniyordu |
| 4 | Kaset kurulamazsa **sessizdi** | oynatma modunda canlıya düşen bir koşum *"kayıttan geldi"* sanılırdı |
"""

from __future__ import annotations

import json

import pytest

from app.kaset import SURUM, Kaset, KasetEksik, _anahtar, _sar_tasima


class SahteUretec:
    """`_chat` taşıyan minik bir sağlayıcı; kaç kez konuştuğunu sayar."""

    def __init__(self, cevaplar: list[str]) -> None:
        self.cevaplar = list(cevaplar)
        self.cagri = 0

    def _chat(self, system: str, user: str, model: str | None = None) -> str:
        self.cagri += 1
        return self.cevaplar.pop(0) if self.cevaplar else "son"


def _kaset(tmp_path, mod):
    return Kaset(tmp_path / "k.json", mod)


# ── 1 · taşıma yüzeyi ─────────────────────────────────────────────────────────
def test_TASIMA_YUZEYI_SARILIR(tmp_path):
    """🔴 Anlam yüzeyleri çoğalır, **tel** çoğalmaz."""
    u, k = SahteUretec(["a"]), _kaset(tmp_path, "kayit")
    assert _sar_tasima(u, k) is True
    assert u._chat("s", "q") == "a"
    assert len(k.kayitlar) == 1


def test_IKI_KEZ_SARMAZ(tmp_path):
    """⚠ Çift sarma, her çağrıyı iki kez sayardı."""
    u, k = SahteUretec(["a"]), _kaset(tmp_path, "kayit")
    _sar_tasima(u, k)
    assert _sar_tasima(u, k) is False


# ── 2 · k=3 örneklemesi ───────────────────────────────────────────────────────
def test_AYNI_ISTEM_UC_KEZ_UC_AYRI_KAYITTIR(tmp_path):
    """🔴🔴 Kusurun kendisi: `consistency_k=3` aynı istemi üç kez sorar.

    İçerikle anahtarlanınca üçü tek kayda çöküyordu; oynatmada üçü de aynı cevabı
    alıyor, oy birliği zorla **%100** oluyor ve sistem farklı karar veriyordu.
    *Bir kayıt, söylenenleri değil söyleniş **sırasını** da tutmalıdır.*
    """
    u, k = SahteUretec(["A", "B", "C"]), _kaset(tmp_path, "kayit")
    _sar_tasima(u, k)
    assert [u._chat("s", "q") for _ in range(3)] == ["A", "B", "C"]
    assert len(k.kayitlar) == 3, "üç örnek üç ayrı kayıt olmalı"

    k.yaz()
    u2, k2 = SahteUretec([]), Kaset(tmp_path / "k.json", "oynat")
    _sar_tasima(u2, k2)
    assert [u2._chat("s", "q") for _ in range(3)] == ["A", "B", "C"], \
        "oynatma AYNI SIRAYLA geri vermeli"
    assert u2.cagri == 0, "oynatmada sağlayıcı hiç konuşmamalı"


# ── 3 · biriktirici kayıt ─────────────────────────────────────────────────────
def test_KAYIT_BIRIKTIRIR_SIFIRLAMAZ(tmp_path):
    """🔴 Tek bir boşluk için bütün korpusu yeniden ödemek, kaseti anlamsız kılar."""
    u, k = SahteUretec(["A"]), _kaset(tmp_path, "kayit")
    _sar_tasima(u, k)
    u._chat("s", "q1")
    k.yaz()

    u2, k2 = SahteUretec(["B"]), Kaset(tmp_path / "k.json", "kayit")
    _sar_tasima(u2, k2)
    assert u2._chat("s", "q1") == "A" and u2.cagri == 0, "var olan kayıt API'ye GİTMEZ"
    assert u2._chat("s", "q2") == "B" and u2.cagri == 1, "yalnız EKSİK olan gider"
    assert len(k2.kayitlar) == 2


# ── 4 · sessizlik yasağı ──────────────────────────────────────────────────────
def test_OYNATMADA_EKSIK_KAYIT_PATLAR(tmp_path):
    """🔴 *Sessizce geçmek, ölçülmemiş bir soruda YEŞİL vermek olurdu.*"""
    k = _kaset(tmp_path, "kayit")
    k.yaz()
    k2 = Kaset(tmp_path / "k.json", "oynat")
    with pytest.raises(KasetEksik):
        k2.coz(_anahtar("_chat", "s", "q", ""), lambda: "olmamalı")
    assert k2.iska == 1


def test_BAYAT_SURUM_REDDEDILIR(tmp_path):
    """⚠ *Bir kaset, kaydedildiği günün modelini ölçer.*"""
    (tmp_path / "k.json").write_text(json.dumps({"surum": SURUM + 99, "kayitlar": {}}))
    with pytest.raises(KasetEksik, match="BAYAT"):
        Kaset(tmp_path / "k.json", "oynat")


def test_ANAHTAR_SOZLUK_SIRASINA_BAGIMLI_DEGIL():
    """⚠ Sözlük sırası değişirse kaset o gün **tamamen** ıskalardı."""
    assert _anahtar("_chat", {"a": 1, "b": 2}) == _anahtar("_chat", {"b": 2, "a": 1})
