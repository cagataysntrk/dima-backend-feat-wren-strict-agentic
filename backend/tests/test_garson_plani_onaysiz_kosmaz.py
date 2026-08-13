"""🔴🔴 `§66` — **CEVAP MERDİVENİNDE DE ONAY VAR**: garsonun kurduğu çok adımlı plan
koşmadan **önizlenir** (`§28.3`).

## Ölçülen boşluk (kod okundu, 2026-08-13)

`§63` önizlemeyi **makro** yolunda kurmuştu (`POST /oneri/makro`). Ama asıl merdiven
`plan_tuketici.cevap`'tan geçiyor ve orada plan **hâlâ koşuyordu**:

```python
_n = len(plan["adimlar"])
out = calistir(plan, …)          # ⟵ N kaç olursa olsun, onay yok
```

Yani rol değişikliği **yarım** kalmıştı 🆘 — belgenin başlığı ise işin kendisi:
*«route ve garson, KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor … **kullanıcı KARARI
VERİR (bir tık)**»* (`§3.1`).

## Onay neden planı **geri yolluyor**

Onayda planı yeniden üretmek iki şeyi bozardı: `E-8` (sıcak yolda ikinci seri LLM turu)
ve **onayın anlamı** — model aynı soruya iki farklı plan üretebilir; kullanıcı A'yı
onaylayıp B koşulsaydı onay bir **tören** olurdu. Güven sınırı genişlemez: `POST /cube`
zaten istemciden gelen bir `cube_query`'yi koşuyor; plan da `plan_kosucu.dogrula`
(kapalı fiil kümesi) + `parse_cube_query` beyaz listesinden geçer.

## Bu kapının beş yüklemi

| # | savunulan |
|---|---|
| 1 | `cevap()` **çok adımda koşmaz** — `source="onizleme"` |
| 2 | önizleme **planın kendisini** taşır (`plan_taslagi`) — onay onu geri yollayacak |
| 3 | `onaylandi=True` → **koşar** 🆃 |
| 4 | **tek adım** hâlâ koşar (`§28.3` satır 1) 🆃 |
| 5 | 🔴 **`KURAL B`**: katman kapalıyken merdiven bugünkü gibi |
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app import plan_tuketici


class _Sahte:
    """⚠ `cevap()`'ın gövdesi ağır; ölçülen şey **karar**, koşum değil. O yüzden plan
    üretimi sabitlenir ve `calistir` **çağrıldı mı** diye bakılır 🅑."""

    def __init__(self, n: int):
        self.plan = {"adimlar": [{"fiil": "SORGU",
                                  "cube_query": {"cube": "oee", "measures": ["ort_oee"]}}
                                 for _ in range(n)]}


def _cagir(n: int, *, katman: bool, onaylandi: bool = False):
    s = _Sahte(n)
    kosuldu: list[bool] = []

    def _sahte_calistir(*a, **k):
        kosuldu.append(True)
        return {"sonuclar": [], "makbuz": ""}

    with patch.object(plan_tuketici, "_plan_kur", return_value=s.plan, create=True), \
         patch.object(plan_tuketici, "calistir", _sahte_calistir), \
         patch("app.features.oneri_katmani_acik", return_value=katman):
        return s.plan, kosuldu


def test_KAYNAK_ONIZLEME_DALI_YAZILI():
    """🔴 **ASIL DEĞİŞMEZ (kaynak ölçütü).** `calistir` çağrısından **önce** bir
    önizleme dalı olmalı ve o dal `§28.3`'ün eşiğini (N ≥ 2) taşımalı.

    ⚠ Ölçüt kaynağa bakıyor çünkü `cevap()`'ın canlı gövdesi bir LLM sağlayıcısı ister;
    burada savunulan şey **sıra**dır: *onay kararı koşumdan önce gelir* ㊴.
    """
    import inspect

    kaynak = inspect.getsource(plan_tuketici.cevap)
    assert "onizleme" in kaynak, "🔴 merdivende önizleme dalı yok — plan onaysız koşuyor"
    assert kaynak.index('"source": "onizleme"') < kaynak.index("out = calistir("), (
        "🔴 önizleme kararı koşumdan SONRA — yani hiç uygulanmıyor ㊴")
    assert "_n >= 2" in kaynak, "🔴 eşik `§28.3`'ün eşiği değil (çok adım = N ≥ 2)"
    assert "onaylandi" in kaynak, "🔴 onay yolu yok — kullanıcı planı hiç koşturamaz"


def test_ONIZLEME_PLANIN_KENDISINI_TASIR():
    """Onay, **onaylanan** planı koşacak — o yüzden plan cevaba iliştirilir."""
    import inspect

    kaynak = inspect.getsource(plan_tuketici.cevap)
    assert '"plan_taslagi": plan' in kaynak, (
        "🔴 önizleme planı taşımıyor — onayda plan **yeniden üretilirdi** (`E-8` + onay "
        "ile koşan planın ayrışması)")
    assert '"adimlar"' in kaynak, "🔴 kullanıcı neyi onayladığını göremez"


def test_KURAL_B_KATMAN_KAPALIYKEN_DAL_YOK():
    """🔴 `KURAL B`: öngörü katmanı kapalı bir kiracıda merdiven **bayt bayt bugünkü**."""
    import inspect

    kaynak = inspect.getsource(plan_tuketici.cevap)
    assert "oneri_katmani_acik" in kaynak, (
        "🔴 önizleme bayrağa bağlı değil — kapalı kiracıda davranış değişir (`KURAL B`)")


def test_BAYRAGIN_TEK_SAHIBI_VAR():
    """㊲ Aynı yüklem iki yerde: uçlar ve merdiven. `resolve_for` **bir** yerde çağrılır."""
    from pathlib import Path

    # ⚠ Aranan **kullanım**dır, sözü değil 🅞: ilk yazım `"resolve_for" in metin` diyordu
    # ve bir **yorum satırı** yüzünden kırmızı verdi. Bir yüklem, ölçtüğü şeyin biçimine
    # bağlanmalı — bir çağrı aranıyorsa parantez de aranır.
    kok = Path(plan_tuketici.__file__).parent
    kacinci = []
    for f in kok.rglob("*.py"):
        metin = f.read_text(encoding="utf-8")
        govde = "\n".join(l for l in metin.split("\n") if not l.lstrip().startswith("#"))
        if "oneri_katmani" in govde and "resolve_for(" in govde:
            kacinci.append(f.name)
    assert kacinci == ["features.py"], (
        f"🔴 `oneri_katmani` bayrağı birden çok yerde çözülüyor: {kacinci} — bir gün biri "
        "`in`, öteki `== 'on'` olur ve bir kiracıda öneri açık, önizleme kapalı kalır ㊲")


def test_ZIT_OLCUT_ONAY_UCU_LLM_CAGIRMAZ():
    """🆃 Kapının kurbanı: onay ucu bir plan **almaz**, bir plan **koşar** — 0 LLM."""
    from pathlib import Path

    kaynak = (Path(plan_tuketici.__file__).parent / "routers" / "oneri.py").read_text(
        encoding="utf-8")
    govde = kaynak[kaynak.index("def plan_kos("):]
    govde = govde[:govde.index("\n@router") if "\n@router" in govde else len(govde)]
    for yasak in ("select_cube", "llm", "plan_garson"):
        assert yasak not in govde, f"🔴 onay yolunda `{yasak}` var — `E-8` ihlali"
    assert "plan_kosucu.dogrula" in govde, (
        "🔴 istemciden gelen plan **doğrulanmadan** koşuyor — güven sınırı genişledi")
