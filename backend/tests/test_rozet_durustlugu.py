"""CANLI TUR — `cube+llm` cevabı *"LLM kullanılmadı"* diye rozetleniyordu.

## Nasıl bulundu ve neden daha önce bulunamadı

Gerçek bir Gemini sağlayıcısıyla **ilk** canlı istekte çıktı. Test ortamı CI reçetesi
gereği `--network none` koşuyor (MIMARI §7), dolayısıyla **`cube+llm` orada HİÇ
üretilmiyor** — 1651 testin hiçbiri bu yolu koşturmuyordu. Kapsam yüksekti, **yol
yoktu**.

## Kusur

`_build_explain` `next((k for k in _EXPLAIN_PATH if s.startswith(k)), None)` ile **İLK**
eşleşen öneki alıyordu. Sözlükteki sıra `cube` → `cube+llm`, ve
`"cube+llm".startswith("cube")` **True**. Sonuç iki katlı bir **yanlış beyan**:

| alan | gösterilen | olması gereken |
|---|---|---|
| `explain.confidence` | **1.0** | 0.85 |
| `explain.path` | *"cube (route() — **LLM'siz, sıfır maliyet**)"* | *"cube + LLM-destekli alan seçimi"* |

Yani Intent-JSON cevabı, saf deterministik `route()` cevabıyla **aynı** güven rozetini
alıyor **ve** kullanıcıya *"LLM kullanılmadı"* deniyordu — oysa `consistency_k=3` ile LLM
**üç kez** çağrılmıştı.

Sözlüğün kendi yorumu ayrımı zaten **beyan ediyordu**: *"cube/cube+llm AYRIMI KORUNUR …
güvenleri farklı olduğundan burada AYRI tutulur."* Kod onu **uygulamıyordu** — §6.1'in
*"beyan var, kod onu tanımıyor"* sınıfı.

## Düzeltme

**En uzun önek kazanır.** Ayrıca bu dosya, sözlüğe ileride eklenecek her önek çifti için
tuzağı **açık** tutar: bir önek başka bir öneğin başlangıcıysa ve sıralamaya güveniliyorsa
aynı hata sessizce geri gelir.
"""

from __future__ import annotations

import pytest

from app.answer import _EXPLAIN_PATH, _build_explain
from app.schemas import AskResponse


def _resp(source: str) -> AskResponse:
    return AskResponse(question="s", sql="SELECT 1", planned_sql=None, result=None,
                       source=source)


@pytest.mark.parametrize("source,beklenen", [
    ("cube", 1.0),
    ("cube+llm", 0.85),          # ⚠️ CANLI TURDA 1.0 DÖNÜYORDU
    ("vqr", 0.95),
    ("statement", 1.0),
    ("meta", 1.0),
    ("catalog", 1.0),
    ("rule", None),
])
def test_GUVEN_kaynaga_gore_DOGRU(source, beklenen):
    e = _build_explain(_resp(source))
    assert e is not None and e.confidence == beklenen, \
        f"{source!r} → {e.confidence} (beklenen {beklenen})"


def test_CUBE_LLM_yolu_LLMSIZ_demiyor():
    """En sert kapı: bu bir sayı hatası değil, kullanıcıya **yanlış bir beyandı**."""
    e = _build_explain(_resp("cube+llm"))
    assert "LLM'siz" not in e.path, f"LLM çağrıldığı hâlde 'LLM'siz' deniyor: {e.path!r}"
    assert "LLM" in e.path, f"LLM katkısı gizleniyor: {e.path!r}"


def test_SAF_CUBE_hala_LLMSIZ_diyor():
    """Kapı fazla geniş olmamalı: saf `route()` cevabı gerçekten LLM'siz."""
    assert "LLM'siz" in _build_explain(_resp("cube")).path


def test_LLM_kaynagi_hala_OLCULEMEZ():
    """Discovery (`llm:*`) güveni **None** kalmalı — uydurma bir sayı gerekçeyi gizler."""
    e = _build_explain(_resp("llm:gemini"))
    assert e.confidence is None and "LLM" in e.path


def test_ONEK_TUZAGI_acik_kalsin():
    """Sözlükteki bir önek, başka bir öneğin **başlangıcıysa** sıraya güvenen her eşleşme
    sessizce yanlış dalı seçer. Bu test o çiftleri **görünür** tutar: yeni bir önek
    eklendiğinde ya eşleşme en-uzun-önek olmalı ya çift bilinçli kabul edilmeli."""
    anahtarlar = list(_EXPLAIN_PATH)
    cakisan = [(a, b) for a in anahtarlar for b in anahtarlar
               if a != b and b.startswith(a)]
    assert cakisan == [("cube", "cube+llm")], (
        f"yeni önek çakışması: {cakisan} — eşleşmenin EN UZUN öneki seçtiğini doğrula")

    # ve o çift GERÇEKTEN doğru çözülüyor:
    assert _build_explain(_resp("cube+llm")).confidence == 0.85


def test_KAYNAK_KODU_en_uzun_onek_kullaniyor():
    import inspect

    govde = inspect.getsource(_build_explain)
    assert "key=len" in govde, "eşleşme hâlâ SIRAYA güveniyor — tuzak geri gelir"
    assert "next((k for k in _EXPLAIN_PATH if s.startswith(k)), None)" not in govde


def test_VARSAYIM_ile_birlikte_de_dogru():
    """`assumptions` doluysa güven bir kademe düşer (−0.15). `cube+llm` için taban artık
    0.85 olduğuna göre sonuç 0.70 olmalı — eskiden 0.85 (yanlış tabandan) çıkıyordu."""
    r = _resp("cube+llm")
    r.cube_query = {"cube": "parti", "measures": ["toplam_ciro"], "period_confirmed": True}
    e = _build_explain(r)
    assert e.assumptions and e.confidence == 0.7, f"{e.confidence}"
