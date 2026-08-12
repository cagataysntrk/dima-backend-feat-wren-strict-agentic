r"""🔴🔴 `§C3`/`§D13` — MCP'DE YAYIMLANAN SÖZLEŞME **GERÇEK İMZAYLA** TUTMALI.

## Ölçülen kusur (2026-08-12)

`§38 D13` *«🟢 CANLI DOĞRULANDI — `POST /mcp/call` çalışıyor»* diyordu. Bir denetim
ajanı 31 aracın **tamamını** yokladı; kendi ölçümüm doğruladı:

    mcp.araclar() alan tipleri:  {'string': 77}      ← HEPSİ string
    gerçek imzalar             :  object 31 · array 14 · boolean 7 · sayısal 5

Canlı ikili kanıt (aynı araç, iki çağrı):

    {"name":"stats.ozet","arguments":{"degerler":"[1,2,3]"}}   ← ŞEMAYA UYUYOR  → isError
    {"name":"stats.ozet","arguments":{"degerler":[1,2,3,10]}}  ← ŞEMAYI YOK SAYIYOR → 200

Yani **sözleşmeye uyan çağrı düşüyor, uymayan çalışıyordu** — ve merdivenin birinci
basamağı `route` bile MCP'den çağrılamıyordu (`AttributeError: 'str' object has no
attribute 'get'`).

> *Yanlış yayımlanmış bir sözleşme, hiç yayımlanmamış bir sözleşmeden kötüdür:
> birincisine uyulur.*

⊙ Tek bir başarılı çağrı, **31 araçlık bir sözleşme için kanıt değildir** — `D13`'ün
işareti tam bu yüzden fazla iyimserdi.

## Onarım ve bu kapı

`tools._json_tipi` tipi **gerçek imzadan** türetiyor (`modul.fonksiyon` →
`inspect.signature` → annotation). Bu kapı ayrışmayı ölçer: yayımlanan her alanın
tipi, o alanın **çalışan imzasıyla** aynı olmalı.

⚠ İmzası çözülemeyen araçlar (**4/31**) bugünkü `"string"`e düşüyor — sessiz bir geri
adım değil, aşağıda **sayılarak** kayıtlı bir kapsam.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

_TIP = {"list": "array", "dict": "object", "int": "integer",
        "float": "number", "bool": "boolean", "str": "string"}


def _gercek_tip(arac) -> dict[str, str]:
    """→ `{alan: gerçek JSON tipi}`; imza çözülemezse boş sözlük."""
    try:
        fn = getattr(importlib.import_module(arac.modul), arac.fonksiyon, None)
        if fn is None:
            return {}
        par = inspect.signature(fn).parameters
    except Exception:                                        # noqa: BLE001
        return {}
    out = {}
    for ad in arac.girdi:
        p = par.get(ad)
        if p is None or p.annotation is inspect.Parameter.empty:
            continue
        ann = str(p.annotation)
        for anahtar, tip in _TIP.items():
            if ann.startswith(anahtar) or ann.startswith(f"<class '{anahtar}'>"):
                out[ad] = tip
                break
    return out


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — sıfır araç yayımlayan bir kapı her sözleşmeyi doğrular."""
    from app import mcp

    a = mcp.araclar()
    assert len(a) >= 25, f"⊘ ölçüm tabanı çöktü: yalnız {len(a)} araç yayımlanıyor"
    alan = sum(len(x["inputSchema"]["properties"]) for x in a)
    assert alan >= 50, f"⊘ yalnız {alan} alan yayımlanıyor"


def test_YAYIMLANAN_TIP_GERCEK_IMZAYLA_TUTUYOR():
    """🔴🔴 **ASIL KAPI.** Yayımlanan her alan tipi, çalışan imzayla aynı olmalı.

    Kırmızı verirse bir ajan **sözleşmeye uyarak** çağrı yapıp `isError` alır — ve
    nedenini bilemez, çünkü yanlış olan onun çağrısı değil **bizim ilanımızdır**.
    """
    from app import mcp, tools

    kayit = {a.ad: a for a in tools.KAYIT}
    sapan = []
    for yayim in mcp.araclar():
        arac = kayit.get(yayim["name"])
        if arac is None:
            continue
        gercek = _gercek_tip(arac)
        for alan, sema in yayim["inputSchema"]["properties"].items():
            beklenen = gercek.get(alan)
            if beklenen and sema.get("type") != beklenen:
                sapan.append(f"{yayim['name']}.{alan}: yayım "
                             f"{sema.get('type')!r} ↔ imza {beklenen!r}")
    assert not sapan, (
        "🔴 MCP SÖZLEŞMESİ İMZAYLA AYRIŞTI:\n  " + "\n  ".join(sapan) +
        "\n*Yanlış yayımlanmış bir sözleşme, hiç yayımlanmamış bir sözleşmeden "
        "kötüdür: birincisine uyulur.*")


def test_YAPISAL_TIPLER_GERCEKTEN_YAYIMLANIYOR():
    """🔴 Ters yön: **hepsi `string`** hâline geri dönülemez.

    Kusurun kendisi buydu — üretec her alanı `"string"` ilan ediyordu ve kapı bunu
    göremiyordu. Bu yüklem, tipin **türetildiğini** ölçer: en az bir `object` ve en az
    bir `array` yayımlanmalı (ölçüldü: `object` 24 · `array` 11).
    """
    from app import mcp

    tipler = {s.get("type") for a in mcp.araclar()
              for s in a["inputSchema"]["properties"].values()}
    eksik = {"object", "array"} - tipler
    assert not eksik, (
        f"🔴 yapısal tipler yayımlanmıyor ({sorted(eksik)} yok) — üretec büyük olasılıkla "
        "yine her alanı `\"string\"` ilan ediyor. *Bir sözleşmeyi tek tiple yayımlamak, "
        "onu hiç yayımlamamaktır.*")


def test_MERDIVENIN_BIRINCI_BASAMAGI_CAGRILABILIR():
    """🔴 `route` — *«her soruda İLK basamak»* — MCP'den **çağrılabilir** olmalı.

    Ölçülen kusur birebir buydu: `schema` `"string"` ilan ediliyordu, ajan dize
    gönderiyordu, `route` `dict` bekliyordu → `AttributeError`.
    """
    from app import mcp

    r = next((a for a in mcp.araclar() if a["name"] == "route"), None)
    if r is None:
        pytest.skip("⊘ `route` MCP yüzeyinde yayımlanmıyor (yetki süzgeci?)")
    props = r["inputSchema"]["properties"]
    assert props.get("schema", {}).get("type") == "object", (
        f"🔴 `route.schema` **{props.get('schema', {}).get('type')!r}** ilan ediliyor, "
        "oysa `dict` bekleniyor. Merdivenin birinci basamağı çağrılamaz hâle gelir.")


def test_COZULEMEYEN_IMZA_SAYISI_KAYITLI():
    """⚠ **Beyan kültürü:** kapsamın sınırı sayıyla yazılı olmalı.

    İmzası çözülemeyen araçlar bugünkü `"string"`e düşüyor. Sayı **büyürse** kapsam
    sessizce daralmış demektir — o yüzden bir tavan var.
    """
    from app import tools

    cozulemeyen = [a.ad for a in tools.KAYIT if not _gercek_tip(a) and a.girdi]
    assert len(cozulemeyen) <= 8, (
        f"🔴 imzası çözülemeyen araç sayısı arttı ({len(cozulemeyen)}): {cozulemeyen}. "
        "Bu araçların şeması `\"string\"`e düşüyor — *bir kapsamı daraltmak meşrudur; "
        "daraltmanın BÜYÜMESİNİ fark etmemek değildir.*")
