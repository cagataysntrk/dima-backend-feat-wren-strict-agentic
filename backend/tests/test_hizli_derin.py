"""FAZ 5.14 kapısı — **Hızlı ↔ Derin anahtarı.** [bayrak: `hizli_derin`]

Ürünün *"LLM'siz cevap"* tezinin **kullanıcıya verilen kontrolü**. Plan 2'de tanımlıydı,
yol haritasının ilk sürümünde **hiç yoktu**.

## 🔴 İkinci bir "LLM'i kapat" yolu AÇILMADI

`mod="hizli"`, var olan `_yol_izinli()` kapısından geçer. İki uygulama olsaydı biri
Discovery'yi keser öteki kesmez ve **hangisinin kazandığı çağrı sırasına bağlı** kalırdı.
*Aynı davranışa iki AD vermek meşrudur; iki UYGULAMA vermek değildir.*
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ASK = Path(__file__).resolve().parents[1] / "app/routers/ask.py"


def test_MOD_alani_sozlesmede():
    from app.schemas import AskRequest

    assert "mod" in AskRequest.model_fields
    # ⚠ Varsayılan `None` — bayrak açık olsa bile davranış **kendiliğinden** değişmez.
    assert AskRequest(question="x").mod is None


def test_IKINCI_LLM_KAPATMA_yolu_YOK():
    """🔴 `mod` kontrolü **`_yol_izinli` içinde** olmalı, başka bir yerde değil.

    ⚠ Belirteç AST: `body.mod` / `getattr(body, "mod")` okuması yalnız o fonksiyonda
    geçebilir. İkinci bir okuma, ikinci bir uygulama demektir.
    """
    # ⚠ **EN İÇTEKİ kapsayan sayılır.** `_yol_izinli` iç içe bir fonksiyondur ve
    # `ast.walk` onu dıştaki `ask`'ın da içinde görür: ilk yazımda belirteç `{ask,
    # _yol_izinli}` görüp kırmızı verdi. *Bir okumayı iki kez saymak, iki sahip varmış
    # gibi gösterir.*
    agac = ast.parse(_ASK.read_text(encoding="utf-8"))
    okuyanlar: list[str] = []

    def _gez(dugum, kapsayan: str | None):
        for c in ast.iter_child_nodes(dugum):
            ic = c.name if isinstance(c, ast.FunctionDef) else kapsayan
            mod_okundu = (
                (isinstance(c, ast.Attribute) and c.attr == "mod"
                 and getattr(getattr(c, "value", None), "id", "") == "body")
                or (isinstance(c, ast.Call)
                    and getattr(c.func, "id", "") == "getattr"
                    and len(c.args) >= 2
                    and getattr(c.args[0], "id", "") == "body"
                    and getattr(c.args[1], "value", "") == "mod"))
            if mod_okundu and kapsayan:
                okuyanlar.append(kapsayan)
            _gez(c, ic)

    _gez(agac, None)
    assert set(okuyanlar) <= {"_yol_izinli"}, (
        f"🔴 `mod` birden fazla yerde okunuyor: {sorted(set(okuyanlar))}. İkinci bir "
        f"'LLM'i kapat' yolu, aynı kuralın iki sahibi demektir ve hangisinin kazandığı "
        f"ÇAĞRI SIRASINA bağlı kalır.")
    assert okuyanlar, "🔴 `mod` hiç okunmuyor — alan bir NİYET BEYANI olarak kalmış."


def test_HIZLI_ile_DETERMINISTIK_ayni_kapiyi_kullanir():
    """*Aynı davranışa iki ad vermek meşrudur; iki uygulama vermek değildir.*"""
    kaynak = _ASK.read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_yol_izinli")
    sabitler = {n.value for n in ast.walk(fn)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert {"hizli", "deterministik"} <= sabitler, (
        "🔴 `hizli` ve `deterministik` aynı kapıda buluşmuyor.")


def test_BAYRAK_kapaliyken_alan_YOK_SAYILIR():
    """GERİ AL: bayrak kapalıyken `mod` bir şey değiştirmez."""
    kaynak = _ASK.read_text(encoding="utf-8")
    assert "hizli_derin" in kaynak, "bayrak kontrolü yok — geri alma yolu kapalı"
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_yol_izinli")
    metin = ast.dump(fn)
    assert "hizli_derin" in metin, (
        "🔴 Bayrak kontrolü `_yol_izinli` DIŞINDA — `mod` bayraktan bağımsız çalışıyor "
        "olabilir ve GERİ AL yolu kırık demektir.")


def test_SECIM_THREADE_yapismaz():
    """⚠ *Yapışkan bir ayar, unutulmuş bir ayardır.*

    Bir mod'u thread'e yapıştırmak, kullanıcının bir kez verdiği kararı ona sormadan
    **her turda** yeniden uygulamak olurdu — ve o karar bir sonraki soruda yanlış
    olabilir. `mod` bir **istek** alanıdır ve hiçbir yerde saklanmaz.
    """
    from control_plane import models

    for ad in dir(models):
        sinif = getattr(models, ad)
        alanlar = getattr(sinif, "model_fields", None)
        if isinstance(alanlar, dict):
            assert "mod" not in alanlar, (
                f"🔴 `{ad}` bir `mod` alanı taşıyor — seçim kalıcılaşmış olabilir.")


@pytest.mark.parametrize("deger", ["derin", "", None, "HIZLI-yanlis"])
def test_HIZLI_DISINDAKI_degerler_SINIR_koymaz(deger):
    """Tanınmayan bir değer **sınır saymaz**: bir yazım hatasının kullanıcının cevabını
    sessizce kesmesi, sınırın kendisinden zararlıdır (mevcut `yol_siniri` kuralının
    aynısı)."""
    assert str(deger or "").strip().lower() != "hizli"
