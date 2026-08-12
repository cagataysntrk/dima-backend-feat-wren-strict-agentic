r"""🔴🔴 BİR HATA MESAJI, BAŞARAMADIĞI İŞLEMİN **YETKİSİNİ TAŞIMAZ**.

## Ölçülen kusur (2026-08-12, denetim ajanı + kendi ölçümüm)

`tools.get()` bilinmeyen bir araç adında şunu fırlatıyordu:

    raise KeyError(f"Kayıtlı olmayan araç: {ad!r}. … Mevcut: {sorted(_ARACLAR)}")

Yani **31 aracın tamamını**, `principal`'a göre **süzmeden**. Ve bu metin ölü değil:
`mcp.cagir`'ın hata dalı onu `hata = f"{type(exc).__name__}: {exc}"[:300]` ile alıp
MCP yanıtının `text`'ine koyuyor — yani **doğrudan ajana dönüyor**.

⊙ Sonuç: `/mcp/tools`'u görmemesi gereken bir kullanıcı, **bilerek hatalı** bir çağrıyla
envanteri **sayabilirdi**. Bugün ürünsel etkisi yoktu (yalnız `owner` kullanılıyor, rol
matrisi `CLAUDE.md`'ye göre **uykuda**) — ama matris açıldığı gün **sessiz** bir sızıntıya
dönerdi.

🔴 **Ve tek bir yer değildi.** Aynı desen ölçüldüğünde **üç** yerde çıktı:

    app/tools.py:839   Mevcut: {sorted(_ARACLAR)}     ← 31 araç
    app/eylem.py:125   Mevcut: {sorted(_BEYANLAR)}    ← eylem kaydı
    app/soz.py:170     Mevcut: {sorted(KATALOG)}      ← söz kataloğu

Üçü de **sayıya** indirildi (geliştiriciye yararlı kalan bilgi), adlar kaldırıldı.

> *Bir hata mesajı, başaramadığı işlemin yetkisini taşımaz.*

## Yüklem — `ast`, metin değil

`grep` bu deseni bir yorumda da yakalar (nitekim `tools.py:838`'de **bu kusuru
anlatan** bir yorum duruyor). Yüklem `Raise` düğümlerinin **içindeki** `sorted(...)`
çağrılarını arıyor.
"""

from __future__ import annotations

import ast
import pathlib

_APP = pathlib.Path(__file__).parent.parent / "app"

#: ⚠ Kapalı muafiyet listesi. Bir kayıt adı buraya ancak **kullanıcıya hiç ulaşmayan**
#: bir istisnada geçebilir — ve gerekçesi yazılmalıdır. Bugün boş.
MUAF: dict[str, str] = {}


def _sizinti() -> list[str]:
    """`raise …(… sorted(KAYIT) …)` — **yalnız MODÜL DÜZEYİ** kayıtlar.

    🔴 **İLK YAZIMIM ÜÇ YANLIŞ UYARI VERDİ** (ölçüldü): `compose.py:451 → carpisan`,
    `llm.py:76 → data`, `plan_kosucu.py:374 → _o`. Üçü de **yerel değişken** —
    sorunun kendisini anlatan bir teşhis (*«çakışan şu adlar»*), bir envanter değil.

    ⊙ Ayrım **yapısal**: bir kaydın adı **modül düzeyinde** atanır; teşhis verisi
    fonksiyon içinde doğar. Yüklem artık modül düzeyi atamaları toplayıp yalnız
    onları arıyor.

    ⚠ Daraltmanın gerekçesi `§101.1`: *bir yanlış-pozitif, kapattığı kusurdan
    pahalıdır* — üç meşru teşhisi susturan bir kapı, dördüncüsünde susturulur.
    """
    out = []
    for f in sorted(_APP.rglob("*.py")):
        try:
            agac = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):            # noqa: PERF203
            continue
        # modül düzeyi adlar = gerçek kayıtlar
        moduldeki = {h.id for d in agac.body if isinstance(d, ast.Assign)
                     for h in d.targets if isinstance(h, ast.Name)}
        moduldeki |= {d.target.id for d in agac.body
                      if isinstance(d, ast.AnnAssign) and isinstance(d.target, ast.Name)}
        for n in ast.walk(agac):
            if not isinstance(n, ast.Raise) or n.exc is None:
                continue
            for alt in ast.walk(n.exc):
                if (isinstance(alt, ast.Call)
                        and getattr(alt.func, "id", None) in ("sorted", "list")
                        and alt.args):
                    ad = getattr(alt.args[0], "id", None)
                    if ad and ad in moduldeki and ad not in MUAF:
                        out.append(f"{f.relative_to(_APP)}:{n.lineno} → {ad}")
    return out


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — hiç `raise` bulamayan bir tarayıcı her sızıntıyı doğrular."""
    sayi = 0
    for f in _APP.rglob("*.py"):
        try:
            sayi += sum(1 for n in ast.walk(ast.parse(f.read_text(encoding="utf-8")))
                        if isinstance(n, ast.Raise))
        except (SyntaxError, UnicodeDecodeError):            # noqa: PERF203
            continue
    assert sayi >= 50, f"⊘ ölçüm tabanı çöktü: yalnız {sayi} `raise` bulundu"


def test_HATA_MESAJI_KAYIT_ADLARINI_DOKMUYOR():
    """🔴🔴 **ASIL KAPI.** Hiçbir istisna mesajı bir kaydın **adlarını** dökmemeli.

    Kırmızı verirse: mesajı **sayıya** indirin (`len(...)`), ya da kayıt gerçekten
    kullanıcıya ulaşmayan bir yerde kalıyorsa `MUAF`'a **gerekçesiyle** yazın.

    ⚠ Sayı kalabilir — *«kayıtta 31 araç var»* bir yetenek envanteri değil, bir
    büyüklüktür; ad listesi ise **doğrudan bir yüzeydir**.
    """
    kacak = _sizinti()
    assert not kacak, (
        f"🔴 HATA MESAJI ENVANTER DÖKÜYOR: {kacak}\n"
        "Bu metinler `mcp.cagir`'ın hata dalından geçip **ajana dönebilir**; yetki "
        "süzgeci uygulanmaz. Adları `len(...)` ile sayıya indirin.\n"
        "*Bir hata mesajı, başaramadığı işlemin yetkisini taşımaz.*")


def test_UC_ONARILAN_YER_SAYIYA_INDI():
    """⚠ Onarımın **kalıcılığı**: üç yer de sayı basmalı, ad değil.

    Yüklem yapısal değil metinsel — ama burada doğrusu bu: ölçülen şey bir **mesaj
    biçimi**dir, bir davranış değil. *Bir metnin doğru olması istendiğinde, metin
    ölçülür.*
    """
    for dosya, kayit in (("tools.py", "_ARACLAR"), ("eylem.py", "_BEYANLAR"),
                         ("soz.py", "KATALOG")):
        m = (_APP / dosya).read_text(encoding="utf-8")
        assert f"len({kayit})" in m, (
            f"🔴 `{dosya}` artık `len({kayit})` basmıyor — hata mesajı ad listesine "
            "geri dönmüş olabilir.")
