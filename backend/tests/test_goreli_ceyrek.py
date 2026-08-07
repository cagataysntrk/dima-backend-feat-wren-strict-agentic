"""🔴 **GÖRELİ ÇEYREK** — bir birim, bir ailede tanınıp ötekinde tanınmıyordu.

## Curl'de ölçüldü

| soru | önce |
|---|---|
| `2. çeyrek toplam fire` | ✅ `2026-04-01..06-30` (`_QUARTER_RE`) |
| 🔴 `geçen çeyrek toplam fire` | **dönem hiç yok** → *"hangi dönem için?"* |

⊙ Kök: `ceyrek` bu dosyada **zaten bilinen** bir takvim birimi (`_QUARTER_RE` ·
`_GRAN_LADDER` · `mali_takvim`). Göreli dönem ailesi (`geçen ay`/`geçen yıl`/`geçen
hafta`) onu **taşımıyordu**.

⚠ Bu bir kelime eklemek **değil**, var olan **birim kümesini tutarlı kılmaktır**:
`ay`·`hafta`·`yil`·`gun` göreli olabiliyorsa `ceyrek` de olabilmeli.

*Bir birimi bir ailede tanıyıp ötekinde tanımamak, kullanıcıya dilin kurallarını değil
bizim dosya düzenimizi öğretmektir.*
"""

from __future__ import annotations

from datetime import date

from app import cube_router as cr
from app import mali_takvim


def test_GECEN_CEYREK_DONEM_URETIYOR():
    f = cr.date_filters(cr._norm("geçen çeyrek toplam fire"))
    ops = {x["operator"]: x["value"] for x in f}
    assert ops.get("gte") and ops.get("lte"), f"🔴 dönem yok: {f}"
    assert ops["gte"] < ops["lte"]


def test_UC_AYLIK_PENCERE():
    """Çeyrek **üç aydır** — pencere ne iki ne dört ay olmalı."""
    f = cr.date_filters(cr._norm("önceki çeyrek ciro"))
    g = date.fromisoformat([x for x in f if x["operator"] == "gte"][0]["value"])
    l = date.fromisoformat([x for x in f if x["operator"] == "lte"][0]["value"])
    ay = (l.year - g.year) * 12 + l.month - g.month
    assert ay == 2, f"🔴 pencere {ay+1} ay — çeyrek üç aydır ({g} … {l})"
    assert g.day == 1, "🔴 çeyrek ayın 1'inde başlamalı"


def test_MALI_YILA_DAYANIYOR():
    """🔴 `FAZ 2.6`'nın aynı dersi: takvim yılı sabiti, Ocak'ta başlamayan bir mali yılda
    pencereyi kaydırırdı. Hesap tek sahipte (`mali_takvim`)."""
    import inspect

    src = inspect.getsource(cr._prev_period_filters)
    i = src.index('elif unit == "ceyrek"')
    assert "mali_takvim.yil_basi" in src[i:i + 500], "🔴 takvim yılı varsayılmış"
    assert "30" not in src[i:i + 500] and "31" not in src[i:i + 500], (
        "🔴 ay sonu elle yazılmış — `calendar` kullanılmalı")


def test_ORDINAL_CEYREK_BOZULMADI():
    """⚠ Genişlemenin sınırı: `2. çeyrek` bugünkü davranışını korumalı."""
    f = cr.date_filters(cr._norm("2. çeyrek toplam fire"))
    ops = {x["operator"]: x["value"] for x in f}
    assert ops["gte"].endswith("-04-01"), ops


def test_BIRIM_KUMESI_TUTARLI():
    """Göreli dönem ailesi, dosyanın **tanıdığı** takvim birimlerini taşımalı."""
    assert "ceyrek" in cr._PREV_RE.pattern
    for birim in ("ay", "hafta", "yil", "gun"):
        assert birim in cr._PREV_RE.pattern
