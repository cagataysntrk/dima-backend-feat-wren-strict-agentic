"""🔴🔴 `§A1` — KASETLİ GARSON KORPUSU **BİR KOŞUMA BAĞLI**; yazılıp unutulamaz.

## Ölçülen kusur (2026-08-12)

`lab/garson_korpusu.py` **yazılmıştı** (425 satır · 21 senaryo · çok turlu zincirler ·
Arapça · kök-neden · çapraz-küp), tabanı (`garson_korpus_baseline.json`) ve kaseti
(259 kayıt) commit'liydi. Ama:

    grep garson_korpusu lab/kapi.py tests/   →   SIFIR

⊙ Yani garson basamağı — **trafiğin %37'si** — hiçbir toplu koşumda ölçülmüyordu, ve
`lab/kapi.py` bunun sebebini şöyle yazıyordu: *«`--live` ister, kotaya bağlıdır ve
BELİRLENİMSİZDİR»*.

## 🔴 O gerekçe DOĞRUYDU — ama BAŞKA BİR DOSYA İÇİN

Gerekçe **canlı koşucu** `lab/garson.py` için yazılmıştı. Kasetli korpus kendi
başlığında *«her demet sonunda, **SIFIR API**»* diyor. Ölçüm (2026-08-12,
`--network none`):

| koşum | sonuç |
|---|---|
| kaset **kurulmadan** | `0 isabet · 0 ıska` → araç canlıya düşüyor, çöküyor |
| yanlış sağlayıcı | `0 isabet · **106 ıska**` → anahtar `model`i de taşıyor |
| kayıt ortamıyla | ✅ **`36 isabet · 0 ıska`** · çıkış kodu **0** |

> *Bir sınıfın ilk üyesi için yazılmış gerekçe, ikinci üyeye sessizce miras kalır.*

⚠ Bu, bu oturumun **㉓ numaralı** dersinin ikinci ödemesi.

## Bu kapı ne ölçer — ve ne ÖLÇMEZ

Ölçer: adım **kayıtlı** mı, `adimlar` demetinde **gerçekten** var mı, toplu koşumdan
dışlanmış mı, ve koşamayacağı ortamda **sessizce yeşil** mi sayılıyor.

Ölçmez: korpusun kendi sonucunu — o `lab/garson_korpusu.kapi()`'nin işi. *Bir kapının
kapısı, kapının yerini ölçer; ölçtüğü şeyi değil.*
"""

from __future__ import annotations

import pathlib

_KOK = pathlib.Path(__file__).resolve().parent.parent


def test_ADIM_KAYITLI_ve_KOMUTU_VAR():
    """🔴 Anahtar listede olup komutu olmayan bir adım, `zip(strict=True)` ile patlar —
    ama patlamadan **önce** burada söylenir."""
    from lab import kapi

    assert "garson_korpusu" in kapi.ADIM_ANAHTARLARI, (
        "🔴 kasetli garson korpusu adım listesinde YOK — garson basamağı (trafiğin "
        "%37'si) hiçbir toplu koşumda ölçülmez.")
    kaynak = (_KOK / "lab" / "kapi.py").read_text(encoding="utf-8")
    assert "lab/garson_korpusu.py" in kaynak and '"--kapi"' in kaynak, (
        "🔴 adım anahtarı var ama KOMUTU yok.")


def test_ADIM_SAYISI_ANAHTAR_SAYISIYLA_AYNI():
    """⚠ `tam()` ikisini `zip(..., strict=True)` ile eşliyor: biri büyür öteki büyümezse
    kapı **koşum anında** çöker. Burada **sayarak** ölçülür (ders ⑲)."""
    import ast

    agac = ast.parse((_KOK / "lab" / "kapi.py").read_text(encoding="utf-8"))
    fn = next(f for f in ast.walk(agac)
              if isinstance(f, ast.FunctionDef) and f.name == "tam")
    demet = next(n for n in ast.walk(fn)
                 if isinstance(n, ast.Assign)
                 and getattr(n.targets[0], "id", "") == "adimlar"
                 and isinstance(n.value, ast.Tuple))
    from lab.kapi import ADIM_ANAHTARLARI

    assert len(demet.value.elts) == len(ADIM_ANAHTARLARI), (
        f"🔴 adım komutu {len(demet.value.elts)}, anahtar {len(ADIM_ANAHTARLARI)} — "
        "`zip(strict=True)` koşum anında patlar.")


def test_KASETLI_KORPUS_TOPLU_KOSUMDAN_DISLANMADI():
    """🔴🔴 **DÜZELTİLEN KUSURUN TA KENDİSİ.**

    `TOPLUDA_YOK` iki adımı dışlıyor ve gerekçesi *«gerçek sağlayıcı + kota ister»*.
    Kasetli korpus **istemez** — dışlanırsa bu dosyanın ölçtüğü kusur geri gelir.
    """
    from lab.kapi import TOPLUDA_YOK

    assert "garson_korpusu" not in TOPLUDA_YOK, (
        "🔴 kasetli korpus toplu koşumdan çıkarılmış. Gerekçe (`--live` · kota · "
        "belirlenimsiz) **canlı koşucu** içindir; kaset `--network none` altında "
        "`36 isabet · 0 ıska` ile koştu. *Bir sınıfın ilk üyesi için yazılmış gerekçe, "
        "ikinci üyeye sessizce miras kalır.*")
    assert "garson" in TOPLUDA_YOK, (
        "⊘ ölçüm tabanı çöktü: canlı koşucu artık dışlanmıyor — o gerçekten kota ister.")


def test_ORTAM_EKSIGI_SESSIZ_YESIL_URETMEZ():
    """🔴 Adım ortam ister (kaset · sağlayıcı · DB · yazılabilir rapor). Eksikse
    **düşürülür ama YAZILIR** — `ADR-0020`: sessiz yutma yok.

    ⚠ Yüklem çift yönlü: hem bildirim listesinde olmalı, hem koşulu **gerçekten**
    ortama bakmalı. Sabit `True` dönen bir koşul, bildirimi bir dekora çevirir.
    """
    import os

    from lab.kapi import ORTAMA_BAGLI_ADIMLAR

    assert "kasetli garson korpusu" in ORTAMA_BAGLI_ADIMLAR, (
        "🔴 adım ortam-koşullu listede YOK → ortam eksikken sessizce atlanır ve özet "
        "yeşil kalır. *Yeşil bir özet, koşmamış bir kapıyı koşmuş gibi okutur.*")
    kosul, ne, ipucu = ORTAMA_BAGLI_ADIMLAR["kasetli garson korpusu"]
    assert callable(kosul) and ne and ipucu, "bildirim eksik alanlı"
    # Koşul GERÇEKTEN ortama bakıyor mu — boş yeşil avı.
    eski = os.environ.pop("DIMA_LLM_PROVIDER", None)
    try:
        assert kosul() is False, (
            "🔴 sağlayıcı yokken bile koşul TRUE — kaset kurulamaz, araç canlıya düşer "
            "ve `--network none` altında çöker. Bu koşul bir DEKOR.")
    finally:
        if eski is not None:
            os.environ["DIMA_LLM_PROVIDER"] = eski


def test_BILDIRIM_IKI_LISTEYI_de_OKUYOR():
    """⚠ İki ayrı sözlük var (`ORTAMA_BAGLI_KAPILAR` dosyalar · `ORTAMA_BAGLI_ADIMLAR`
    adımlar). Bildirim yalnız birini okursa öteki **sessiz** kalır — bu, `_belgeler_
    bildirimi`nin *«iki çıkış, tek bildirim»* dersinin liste hâlidir."""
    kaynak = (_KOK / "lab" / "kapi.py").read_text(encoding="utf-8")
    i = kaynak.index("def _belgeler_bildirimi")
    govde = kaynak[i:i + 700]
    for ad in ("ORTAMA_BAGLI_KAPILAR", "ORTAMA_BAGLI_ADIMLAR"):
        assert ad in govde, (
            f"🔴 bildirim `{ad}` listesini okumuyor — o listedeki kayıplar sessiz kalır.")


def test_TABAN_ve_KASET_COMMITLI():
    """🔴 Kaset ve taban **gitignore dışında** olmalı: biri kaybolursa adım ya ölçemez
    ya da her koşumda kendi tabanını yeniden yazıp **hep yeşil** verir."""
    for yol in ("lab/kasetler/garson-korpus.json", "lab/garson_korpus_baseline.json"):
        assert (_KOK / yol).is_file(), f"🔴 {yol} YOK — adım ölçemez ya da dekora döner"
    gi = (_KOK / ".gitignore").read_text(encoding="utf-8")
    assert "lab/kasetler" not in gi and "garson_korpus_baseline" not in gi, (
        "🔴 kaset/taban gitignore'lu — commit edilemez, başka bir makinede adım koşamaz.")
