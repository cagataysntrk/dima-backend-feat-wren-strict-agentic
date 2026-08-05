"""🔴 KÖK-7c — **ÇOK-GEÇİŞ**: ikinci dönem sessizce kaybolmaz. (denetim raporu KN-3)

## Ölçülen kusur

⊡ `cube_router.py`: `.search(` **34**, `.finditer(` **10**.
⊡ `_period_hit_words` yedi dönem kalıbını **`.search`** ile tarıyordu → *ilk eşleşme
kazanır, ikincisi yok sayılır*.

⊙ Hata ay adları için **bir kez** bulunup düzeltilmişti (`:2096` yorumu, 1 Ağustos canlı
bulgusu) — **kalan altı kalıpta düzeltilmemişti.** Yani doğru teşhis konmuş, tek bir
yerde uygulanmış, **bir kapıya bağlanmamıştı**. Bu dosya o kapıdır.

| soru | önce | sonra |
|---|---|---|
| `ilk ceyrek ve ikinci ceyrek ciro` | `['ceyrek','ilk']` → **R10** | `+ ikinci` → çözülür |
| `gecen ay ve gecen yil ciro` | `['ay','gecen']` | `+ yil` |
| `son 3 ay ve son 6 ay ciro` | `['ay','son']` | `['ay','son']` *(kelime aynı)* |

## 🔴 VE AÇILAN KAPSAM BİR SESSİZ-YANLIŞ ÜRETECEKTİ — kapı onu yakaladı

`ilk ceyrek ve ikinci ceyrek` R10'dan kurtulunca `route()` yine yalnız **ilk** çeyreği
çözüyor (`_quarter_period_filters` tek `.search`). `uyum._cok_donem` çeyreği **saymıyordu**
→ soru dürüst bir **reddden** sessiz bir **yanlışa terfi edecekti**.

> *Bir kapsamı açan değişiklik, açtığı kapsamın beyan sayacını da beslemek zorundadır.*

⚠ **Görmek ≠ çözebilmek, ve bu kasıtlıdır.** `CubeQuery` filtreleri VE'lenir; iki ayrık
dönem tek sorguda ifade **edilemez**. Sözleşme: *gördüğünü söyle, taşıyamadığını da söyle.*
"""

from __future__ import annotations

import re

import pytest

import app.cube_router as cr
from app.cube_router import route
from app.uyum import _cok_donem, denetle

#: Raporun KN-3 tablosundaki üç vaka + ölçüm sırasında eklenen iki biçim.
COK_DONEMLI = [
    ("son 3 ay ve son 6 ay ciro", 2),
    ("ilk ceyrek ve ikinci ceyrek ciro", 2),
    ("gecen ay ve gecen yil ciro", 2),
    ("2025 ve 2026 ciro", 2),
    ("ocak ve haziran ciro", 2),
]


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · ÇOK-GEÇİŞ — kalıplar ikinci varlığı GÖRÜYOR
# ═══════════════════════════════════════════════════════════════════════════════

DONEM_KALIPLARI = [
    ("REL", "_REL_DATE", "son 3 ay ve son 6 ay ciro", 2),
    ("QUARTER", "_QUARTER_RE", "ilk ceyrek ve ikinci ceyrek ciro", 2),
    ("PREV", "_PREV_RE", "gecen ay ve gecen yil ciro", 2),
    ("YEAR", "_YEAR_RE", "2025 yilinda ve 2026 yilinda ciro", 2),
]


@pytest.mark.parametrize("ad,attr,q,beklenen", DONEM_KALIPLARI)
def test_KALIP_IKINCIYI_DE_GORUYOR(ad, attr, q, beklenen):
    """🔴 **ASIL KAPI.** Her dönem kalıbı `finditer` ile taranmalı.

    ⚠ Bu test kalıbın **kendisini** ölçer, `_period_hit_words`in çıktısını değil: iki
    eşleşmenin kelimeleri aynı olabilir (`son 3 ay` / `son 6 ay` → ikisi de `{son, ay}`)
    ve o zaman çıktıya bakan bir test **yeşil yalan** söylerdi."""
    rx = getattr(cr, attr)
    assert len(list(rx.finditer(q))) == beklenen, f"🔴 {ad} ikinci eşleşmeyi görmüyor: {q}"


def test_SEARCH_KULLANIMI_GERI_GELMEDI():
    """🔴 Regresyon kapısı — *kusur değil, kusurun tekrarına izin veren boşluk*.

    Raporun kendi teşhisi: *"desen tanınmış, tek tek düzeltilmiş, ama bir KAPIYA
    bağlanmamış — bu yüzden her yeni özellik onu yeniden doğuruyor."*"""
    src = (cr.__file__ or "")
    with open(src, encoding="utf-8") as fh:
        satirlar = fh.read().splitlines()
    govde = _fonksiyon_govdesi(satirlar, "def _period_hit_words")
    assert govde, "⊘ fonksiyon bulunamadı — test bayatlamış"
    kotu = [s for s in govde if re.search(r"\brx\.search\(|_RE\.search\(", s)]
    assert not kotu, f"🔴 dönem kalıbı yine tek-geçiş taranıyor:\n  " + "\n  ".join(kotu)


def test_AY_TARAMASININ_TEK_SAHIBI_VAR():
    """🔴 7e'den kalan **ölü ikinci sahip** silindi: `\\b(month)\\b(\\s+ayi\\w*)?` kalıbı
    `_ek_gecerli` süzgecini **atlayarak** eşleşiyordu. Ölü ama sahipsiz değil — bir gün
    `_ek_gecerli` sıkılaştırılsa onu sessizce delerdi."""
    with open(cr.__file__, encoding="utf-8") as fh:
        govde = _fonksiyon_govdesi(fh.read().splitlines(), "def _period_hit_words")
    ay_taramasi = [s for s in govde if "_MONTH_ALT" in s and s.strip().startswith("for ")]
    assert not ay_taramasi, f"🔴 ikinci ay taraması geri gelmiş: {ay_taramasi}"
    assert any("_AY_ADI_RE" in s for s in govde), "⊘ tek sahip de kaybolmuş"


def _fonksiyon_govdesi(satirlar: list[str], imza: str) -> list[str]:
    """İmzadan bir sonraki üst-seviye `def`e kadar. ⚠ Metnin **tamamında** aramak, testi
    kendi belgelendirmesine yakalatır — bu depoda bir kez oldu."""
    try:
        bas = next(i for i, s in enumerate(satirlar) if s.startswith(imza))
    except StopIteration:
        return []
    out = []
    for s in satirlar[bas + 1:]:
        if s and not s[0].isspace() and not s.startswith(")"):
            break
        out.append(s)
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · AÇILAN KAPSAM SESSİZ-YANLIŞ ÜRETMİYOR — 7c'nin BEDELİ ödendi mi
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("q,adet", COK_DONEMLI)
def test_SAYAC_HEPSINI_SAYIYOR(q, adet):
    """🔴 `uyum._cok_donem` dört biçimi de saymalı. Çeyrek biçimi **7c açınca** eksik
    çıktı: soru R10'dan kurtuldu ama sayaç görmüyordu → dürüst ret, sessiz yanlışa
    **terfi** edecekti."""
    assert _cok_donem(q) >= adet, f"🔴 «{q}» {adet} dönem taşıyor, sayaç {_cok_donem(q)}"


@pytest.mark.parametrize("q,_", COK_DONEMLI)
def test_COK_DONEM_SESSIZCE_CEVAPLANMIYOR(q, _, schema):
    """🔴 **Sözleşme:** ya `route()` reddeder ya `uyum` etiketler. Tek bir birleşik sayının
    `source=cube` rozetiyle dönmesi kabul edilemez."""
    cq = route(q, schema)
    if cq is None:
        return                                   # dürüst ret — kabul
    ic = (cq.get("cube_query") or cq)
    cm = next((c for c in schema["cubes"] if c["name"] == ic.get("cube")), None)
    isaretler = [i.isaret for i in denetle(q, cq, cm)]
    assert "cok_donem" in isaretler or isaretler, \
        f"🔴 «{q}» sessizce tek sayıya çöktü — filtreler: {ic.get('filters')}"


def test_CEYREK_KIMLIGI_NUMARASIDIR():
    """⚠ `1. çeyrek` ile `ilk çeyrek` **aynı** dönemdir; iki kez sayılırsa *"1. çeyrek
    yani ilk çeyrek"* diyen kullanıcı haksız yere ihlal alırdı."""
    assert _cok_donem("1. ceyrek yani ilk ceyrek ciro") == 1


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · YANLIŞ-POZİTİF — açılan kapsam meşru soruları bozmuyor
# ═══════════════════════════════════════════════════════════════════════════════

TEK_DONEMLI = [
    "son 6 ay ciro", "bu yil toplam ciro", "gecen ay toplam uretim",
    "ilk ceyrek ciro", "mart ayinda fire orani", "2025 yilinda toplam ciro",
]


@pytest.mark.parametrize("q", TEK_DONEMLI)
def test_TEK_DONEM_IHLAL_ALMIYOR(q, schema):
    """🔴 Kapının **asıl sınavı**: tek dönemli meşru sorular etiketlenmemeli.
    *Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*"""
    assert _cok_donem(q) <= 1, f"🔴 tek dönemli soru {_cok_donem(q)} sayıldı: {q}"
    cq = route(q, schema)
    if cq is None:
        pytest.skip(f"⊘ route çözemedi: {q}")
    ic = cq.get("cube_query") or cq
    cm = next((c for c in schema["cubes"] if c["name"] == ic.get("cube")), None)
    assert "cok_donem" not in [i.isaret for i in denetle(q, cq, cm)]


def test_ARALIK_IKI_DONEM_DEGIL():
    """⚠ `1 ocak 31 mart arası` iki ay adı taşır ama **tek aralıktır** — `_ARALIK`
    işaretleri bunu ayırır. *İki tarih, aralarında bir "arası" varsa iki istek değil bir
    aralıktır.*"""
    from app.uyum import denetle as _d
    cq = {"cube_query": {"cube": "x", "measures": ["m"],
                         "filters": [{"dimension": "tarih", "operator": "gte",
                                      "value": "2026-01-01"},
                                     {"dimension": "tarih", "operator": "lte",
                                      "value": "2026-03-31"}]}}
    assert "cok_donem" not in [i.isaret for i in _d("1 ocak 31 mart arasi uretim", cq)]


def test_GENIS_YANLIS_POZITIF_TABANI(schema):
    """🔴 **Bu dosyanın en pahalı kapısı** — 7c kapsamı açtı, bedelini burada ödüyor.
    Katalogdan üretilmiş **tek dönemli** sorularda `cok_donem` ihlali **sıfır** olmalı."""
    sorular = []
    for c in schema["cubes"]:
        for m, syns in list((c.get("measure_synonyms") or {}).items())[:4]:
            t = (syns or [m])[0].removesuffix("!")
            sorular += [f"bu yıl {t}", f"geçen ay {t}", f"son 6 ay {t}",
                        f"mart ayında {t}", f"ilk çeyrek {t}"]

    kotu, cozulen = [], 0
    for q in sorular:
        cq = route(q, schema)
        if not cq:
            continue
        cozulen += 1
        ic = cq.get("cube_query") or cq
        cm = next((c for c in schema["cubes"] if c["name"] == ic.get("cube")), None)
        if "cok_donem" in [i.isaret for i in denetle(q, cq, cm)]:
            kotu.append(q)
    assert cozulen > 200, f"⊘ ölçüm tabanı çöktü: yalnız {cozulen} soru çözüldü"
    assert not kotu, (f"🔴 tek dönemli meşru soruda cok_donem ihlali "
                      f"({len(kotu)}/{cozulen}):\n  " + "\n  ".join(kotu[:10]))
