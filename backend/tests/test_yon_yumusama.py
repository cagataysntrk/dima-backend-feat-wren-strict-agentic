"""🔴 `§YÖN` — «EN DÜŞÜĞÜ» SORUSU «EN YÜKSEĞİ» SIRALIYORDU.

Ölçülen sessiz yanlış (canlı, **üç koşumda da aynı** — 2026-08-11):

    «en düşük makine»    → ASC   ✅
    «en düşüğü hangisi»  → DESC  🔴  ilk satır en YÜKSEK OEE (ÖRGÜ HAT, 0,646)

Kullanıcı *en düşüğü* sordu, sistem *en yükseği* başa koydu — ve cevap **makul
görünüyor**: sıralı liste, doğru ölçü, doğru kırılım; yalnız **ters uçtan**.

Kök: `_direction` kutup sözcüğünü ön-ek eşleşmesiyle arıyor; `düşük` + iyelik Türkçede
**zorunlu olarak** yumuşuyor (`düşük → düşüğü`) ve normalize hâlde `dusugu` ile `dusuk`
tam o harfte ayrışıyor.

⚠ Çözüm sözlüğe `dusugu` eklemek **DEĞİL** (`ADR-0008`; ayrıca sınıfı kapatmazdı —
`küçüğü`, `düşüğün`, `düşüğe` ardından gelirdi). Yumuşama **kapalı bir dilbilgisi
kuralıdır** ve sahibi `app/ek.py::_yumusat`; burada **çağrılır**.
"""

from app.cube_router import (
    _AZLIK_KOKLERI,
    _AZLIK_KUTBU,
    _KOTULUK_KOKLERI,
    _direction,
    _norm,
)


def test_YUMUSAMIS_ustunluk_dogru_yonu_verir():
    """Ölçülen kusurun ta kendisi."""
    assert _direction(_norm("en düşüğü hangisi")) == "ASC"
    assert _direction(_norm("en küçüğü hangisi")) == "ASC"


def test_YUMUSAMAMIS_bicimler_AYNEN_calisir():
    """`KURAL B` ruhu: düzeltme mevcut davranışı bozmaz."""
    assert _direction(_norm("en düşük makine")) == "ASC"
    assert _direction(_norm("en az fire")) == "ASC"
    assert _direction(_norm("en kısa süre")) == "ASC"
    assert _direction(_norm("en yüksek makine")) == "DESC"
    assert _direction(_norm("en çok fire")) == "DESC"
    assert _direction(_norm("hangisi")) == "DESC"


def test_kume_BUYUMEZ_yalnizca_kendi_cekimini_tanir():
    """⚠ Yeni sözcük YOK: küme yalnız kendi köklerinin yumuşamışını taşır."""
    ek = _AZLIK_KOKLERI - _AZLIK_KUTBU
    assert ek == {"dusug", "kucug"}, f"beklenmeyen genişleme: {ek}"
    # Yumuşamayan kutup sözcükleri hiç değişmez
    assert "az" in _AZLIK_KOKLERI and "kisa" in _AZLIK_KOKLERI


def test_NITELIK_kutbu_yonu_OLCUNUN_beyanindan_alir():
    """`§W-C` — nitelik kutbunda yön sözlükten değil ölçü beyanından gelir."""
    assert _direction(_norm("en kötü makine"), az_iyi=None) == "ASC"
    assert _direction(_norm("en kötü makine"), az_iyi=True) == "DESC"
    assert "kotu" in _KOTULUK_KOKLERI


def test_yumusama_KURALI_ikinci_kez_yazilmadi():
    """`KAT-1` — Türkçenin yumuşaması bu depoda tek sahiptedir (`ek._yumusat`)."""
    import ast
    import inspect

    import app.cube_router as cr

    # ⚠ **DOCSTRING SOYULUR** — bu oturumda ÜÇÜNCÜ kez aynı ders (B2 · D3 · burada):
    # açıklama metni kuralı **anlatır**, uygulamaz; ona bakan bir kapı kendi yazarını
    # yanlış yere götürür. *Bir kapı, koda bakmalıdır; kodun hakkındaki cümleye değil.*
    govde = ast.parse(inspect.getsource(cr._yumusak_kutup).strip()).body[0]
    if (govde.body and isinstance(govde.body[0], ast.Expr)
            and isinstance(govde.body[0].value, ast.Constant)):
        govde.body = govde.body[1:]
    kaynak = ast.unparse(govde)
    assert "_yumusat" in kaynak, "yumuşama sahibi ÇAĞRILMALI"
    assert "ğ" not in kaynak, "yumuşama haritası burada YENİDEN yazılmamalı"
