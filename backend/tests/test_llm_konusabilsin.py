"""🔴 **LLM'İN KONUŞMASINA İZİN VAR MI** — ölçülen kusur *yanlış anlama* değil **RED**.

## Ölçülen

Canlı: *"verimlilik"* sorusunda **9/9 Intent çağrısı `{"cube":null}`**. Ve 42 gerçek
soruda merdiven **darboğaz değil**: `route()` çözdü %0 · netleştirme kesti %0 · yetenek
sınırı kesti %2,4 · **LLM'e gidiyor %97,6**.

> Elimizde *"LLM yanlış anlıyor"* diye bir kanıt **yok**; elimizdeki kanıt *"LLM'in
> konuşmasına izin verilmiyor"*.

Üç sebep, üçü de `select_cube`'ün **kendi** yolunda:

| # | kusur | kanıt |
|---|---|---|
| `AJ3.3` | **dönemi yazacak alan yok** — prompt *"tarih yazma"* diyor, `period_expr` yalnız TAKİP yolunda var | model *"geçen çeyrek"*i hiçbir yere koyamıyor |
| `AJ3.4` | **red yanlılığı** — reddetmek üç kez söylenmiş (metin · şema ilk dalı · araç açıklaması), yorumlamak **sıfır** kez | *Üç kez hayır demeyi öğretip bir kez evet demeyi öğretmemek, susturmaktır.* |
| `AJ3.5` | **sıfır örnek** — `refine_cube`'de 4, burada 0 | zor işi yapana örnek verilmemiş |

## ⚠ VE HİÇBİRİNİN KAZANCI BU KOŞUMDA ÖLÇÜLEMEZ

`nl_corpus` tanımı gereği `rule` sağlayıcıyla koşar; `eval --slice llm` **4 vaka**.
Bu dosya **mekanizmayı** kilitler, kazancı değil — `test_sema_kisitli.py`'nin aynı şerhi.

*Bir düzeltmeyi ölçemeden uygulamak, kusurun yerini değiştirmenin pahalı bir biçimidir* —
bu yüzden üçü de **geri alınabilir** (prompt metni + bir alan) ve hiçbiri deterministik
yola dokunmuyor.
"""

from __future__ import annotations

import json

import pytest

from app import cube_router as cr
from app.llm import _cube_select_system


@pytest.fixture(scope="module")
def prompt(schema):
    from app.katalog_metni import build_catalog

    return _cube_select_system(build_catalog(schema, sozluk=True)[0])


def test_AJ3_4_RED_TEK_YANLI_DEGIL(prompt):
    """🔴 Reddetmenin karşısında **yorumlama** da yazılı olmalı."""
    assert "ASIL İŞİN" in prompt and "ÇEVİRMEK" in prompt, (
        "🔴 modele işinin ne olduğu söylenmiyor — yalnız ne zaman reddedeceği")
    assert "KAÇIŞ değil" in prompt, (
        "🔴 `{cube:null}` hâlâ koşulsuz bir kaçış kapısı gibi sunuluyor")
    assert "Emin olamadığın için değil" in prompt, (
        "🔴 belirsizlik ile yanıtlanamazlık ayrılmamış — model şüphelenince reddeder")


def test_AJ3_5_ORNEK_VAR(prompt):
    """Dar düzenleme yapan prompt'ta 4 örnek vardı, doğal dili yorumlayanda 0."""
    assert prompt.count("→") >= 4, f"🔴 örnek sayısı yetersiz: {prompt.count('→')}"


def test_AJ3_3_DONEM_IFADESI_YAZILABILIYOR(prompt, schema):
    """🔴 Alan olmadan *"tarih yazma"* kuralı modele **çıkışsız** bir emirdi."""
    assert "period_expr" in prompt, "🔴 prompt dönem alanını hiç anmıyor"
    _, index = cr.build_catalog(schema)
    sema = cr.cube_query_json_schema(index)
    zamanli = [d for d in sema["oneOf"][1:] if "timeDimensions" in d["properties"]]
    assert zamanli, "⊘ zaman boyutlu cube yok — vaka bayat"
    assert all("period_expr" in d["properties"] for d in zamanli), (
        "🔴 şemada alan yok — model onu üretemez (araç kullanımı şema dışına çıkamaz)")


def test_AJ3_3_ALAN_TASINIR_ama_SORGUYA_GIRMEZ(schema):
    """⚠ `period_expr` bir **niyet taşıyıcısıdır**, bir sorgu alanı değil: `cube_sql` onu
    tanımaz. Beyaz listeden geçer (yoksa düşer ve model boşuna söyler), sonra `ask()`
    onu **çıkarıp** `_resolve_period`'e verir."""
    _, index = cr.build_catalog(schema)
    ad = next(a for a, s in index.items() if s.get("measures") and s.get("time_dimensions"))
    cq = {"cube": ad, "measures": index[ad]["measures"][:1], "period_expr": "geçen çeyrek"}
    out = cr.parse_cube_query(json.dumps(cq), index)
    assert out and out.get("period_expr") == "geçen çeyrek", (
        "🔴 beyaz liste alanı düşürdü — model dönemi söylese bile sistem duymaz")


def test_COZUCU_IKINCI_KEZ_YAZILMADI():
    """🔴 `KAT-1`. Dönem ifadesini çözen **tek** yer `_resolve_period` (o da
    `date_filters`'a sorar). İkinci bir çözücü, aynı ifadenin iki farklı tarihe
    çözülmesi demekti — ve bu turda `yılbaşından bugüne` zaten bir sessiz-yanlış
    üretmişti."""
    import inspect

    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    assert src.count("def _resolve_period") == 1
    i = src.index('parsed.pop("period_expr")')
    assert "_resolve_period" in src[i:i + 300], (
        "🔴 taze yol dönemi başka bir yolla çözüyor")


def test_KAZANC_OLCULEMEZ_ve_bu_YAZILI():
    """⚠ Dürüstlük kapısı: bu dosya **mekanizmayı** kilitler, kazancı değil.
    `eval --slice llm` bugün 4 vaka; kazanç ancak o dilim büyüyünce ölçülür."""
    import pathlib

    d = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "ÖLÇÜLEMEZ" in d and "eval --slice llm" in d
