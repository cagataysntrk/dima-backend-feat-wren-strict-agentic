"""🔴🔴 `§YV` — SORUNUN VARSAYDIĞI YÖN, ÖLÇÜLENİN TERSİ OLDUĞUNDA **SÖYLENİR**.

## Canlıda ölçülen kusur (2026-08-12)

    «ciro neden düştü»
      → özet: «ciro: Oca 2024→Haz 2026 %117,4 ARTTI …»
      → «düşmedi» · «aksine» · «varsayım» — hiçbiri geçmiyor (arandı, yok)

Kullanıcı **yanlış bir öncülle** geliyor; sistem o öncülü **sessizce düzeltip** başka bir
soruyu cevaplıyor. `§101.1`'in sınıfı: cevap **doğru**, ama sorulan soru **bu değildi** —
ve bunu anlamanın hiçbir yolu yok.

## Yüklem YAPISAL — yeni sözlük yazılmadı

* **Soru tarafı:** `uyum._TREND`'in **zaten kapalı** fiil kümesi ikiye **bölündü**
  (`ADR-0008`: yeni liste yasak, var olanı bölmek serbest). Ayrım dilbilgiseldir:
  `azaldi`/`dustu` ve `artti`/`yukseldi` bir **yön** taşır; `trend`/`degisim`/`seyri`
  taşımaz. ⚠ *«en düşük»* gibi **üstünlük** ifadeleri buraya girmez — onlar bir sıralama
  isteğidir, bir yön **iddiası** değil (`cube_router._direction`'ın işi).
* **Cevap tarafı:** metin **ayrıştırılmaz**; `trend`/`delta` olguları sayısal `pct`
  taşır (`interpret.py:143,158`) ve eşik `interpret`'in **kendi** eşiğidir (`|pct| > 1`).

## 🔴 VE YERİ ÖLÇÜM SEÇTİ — ilk deneme HİÇ ATEŞLEMEDİ

Kural önce `uyum.denetle`'ye kondu. Canlı curl üç soruda da **`yok`** dedi: o çağrı
yerlerinde `resp.interpretation` **henüz yok**. Üstelik `denetle`'nin **üç** çağıranı var
(`beyan_ekle` · `ask.py` · `plan_tuketici`) ve kök-neden soruları **planlayıcı** yolundan
geçiyor — kural iki yerde kurulsa bile üçüncüde boşta kalırdı.

`_maybe_interpret` ise **tek** yerdir ve yorumu **kuran** yerdir.

> *Bir beyanı, dayandığı olgunun doğduğu yere koymak; onu üç kez bağlamaktan hem ucuz
> hem güvenlidir.*

⚠ Ve bu, oturumun **on beşinci** *«araç/varsayım önce yanıldı»* vakasıdır — ama bu kez
yanılgıyı **canlı curl** yakaladı, kapı değil. *Bir kapının yeşili, ulaşılamayan bir
kuralı da yeşil gösterir.*
"""

from __future__ import annotations

import types

from app.uyum import _olculen_yon, _yon_varsayimi, yon_beyani


def _resp(soru: str, pct: float | None, tip: str = "trend"):
    yorum = None if pct is None else {"facts": [{"type": tip, "pct": pct, "text": "x"}]}
    return types.SimpleNamespace(question=soru, interpretation=yorum, note=None)


# --- YÜKLEM ---------------------------------------------------------------------

def test_YON_FIILLERI_ayrilmis():
    assert _yon_varsayimi("ciro neden dustu") == -1
    assert _yon_varsayimi("ciro neden azaldi") == -1
    assert _yon_varsayimi("ciro neden artti") == 1
    assert _yon_varsayimi("ciro neden yukseldi") == 1


def test_YONSUZ_ifadeler_YON_TASIMAZ():
    """`trend`/`degisim`/`seyri` yönsüzdür — bir yön **iddiası** değil, bir eksen isteği."""
    for q in ("cironun trendi", "ciro degisimi", "ciro nasil gidiyor", "aylara gore ciro"):
        assert _yon_varsayimi(q) is None, q


def test_USTUNLUK_ifadesi_YON_SAYILMAZ():
    """⚠ *«en düşük müşteri»* bir **sıralama** isteğidir; yanlış sayılırsa her top-N
    sorusu sahte bir çelişki beyanı üretirdi (`§101.1`: yanlış pozitifin bedeli ağır)."""
    assert _yon_varsayimi("en dusuk cirolu musteri") is None
    assert _yon_varsayimi("en yuksek 5 musteri") is None


def test_OLCULEN_YON_sayidan_okunur():
    """Metin ayrıştırılmaz: `pct` sayısaldır ve eşik `interpret`'in kendi eşiğidir."""
    assert _olculen_yon({"facts": [{"type": "trend", "pct": 117.4}]}) == (1, 117.4)
    assert _olculen_yon({"facts": [{"type": "delta", "pct": -12.0}]}) == (-1, -12.0)
    assert _olculen_yon({"facts": [{"type": "trend", "pct": 0.5}]}) is None, "yatay → yön yok"
    assert _olculen_yon({"facts": [{"type": "top", "pct": 99}]}) is None, "ilgisiz tip"
    assert _olculen_yon(None) is None


# --- BEYAN ----------------------------------------------------------------------

def test_TERS_YONDE_beyan_EDILIR():
    """🔴 Kusurun ta kendisi."""
    r = _resp("ciro neden dustu", 117.4)
    assert yon_beyani(r) is True
    assert "ters yönde" in r.note and "117" in r.note and "arttı" in r.note


def test_AYNI_YONDE_SUSULUR():
    """⚠ Yanlış pozitif yok: varsayım doğruysa beyan bir gürültüdür."""
    r = _resp("ciro neden artti", 117.4)
    assert yon_beyani(r) is False and r.note is None


def test_YONSUZ_SORUDA_susulur():
    r = _resp("aylara gore ciro", 117.4)
    assert yon_beyani(r) is False and r.note is None


def test_OLCUM_YOKSA_susulur():
    """*Bir çelişkiyi ilan etmek için önce iki tarafın da ölçülmüş olması gerekir.*"""
    r = _resp("ciro neden dustu", None)
    assert yon_beyani(r) is False and r.note is None


def test_MEVCUT_NOT_EZILMEZ():
    r = _resp("ciro neden dustu", 117.4)
    r.note = "önceki beyan."
    yon_beyani(r)
    assert r.note.startswith("önceki beyan.") and "ters yönde" in r.note


def test_BEYAN_YORUMUN_DOGDUGU_YERE_bagli():
    """🔴 İlk deneme `denetle`'ye kondu ve **hiç ateşlemedi**. Bu kapı, çağrının
    `_maybe_interpret`'te — yorumun kurulduğu yerde — kaldığını kilitler."""
    import ast
    import pathlib
    src = (pathlib.Path(__file__).parent.parent / "app" / "answer.py").read_text(
        encoding="utf-8")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == "_maybe_interpret":
            govde = "\n".join(ast.dump(x) for x in n.body)
            assert "yon_beyani" in govde, "yön beyanı yorumun doğduğu yerden koptu"
            break
    else:
        raise AssertionError("_maybe_interpret bulunamadı")
