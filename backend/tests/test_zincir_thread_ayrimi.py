"""🔴 `§60` — **ZİNCİR SEMANTİK, THREAD GÖRSEL**: ikisi ayrı edimdir.

## Korunan karar (`app/context.py`, *«tartışmaya kapalı»*)

> **Thread bir UI GRUPLAMASIDIR, SEMANTİK SINIR DEĞİLDİR.** Bir thread cube/bağlam
> sınırı taşımaz; yeni thread **yalnız açık kullanıcı eylemiyle** doğar.

## Ölçülen ihlal (kullanıcı bildirdi, 2026-08-13)

İstemcide **iki farklı edim tek işleyiciyi** paylaşıyordu:

```tsx
const yeniKonu = () => { …bağlamı temizle…; setActiveThreadId(null); };
onYeniSohbet={yeniKonu}     // «+ yeni sohbet» → yeni THREAD   ✅
onClearContext={yeniKonu}   // «konudan çık»   → yeni THREAD   🔴
```

Yani kullanıcı bir konuyu bitirince **sohbetten de çıkıyordu**. Doğru model kullanıcının
kendi cümlesiyle: *«soru → cevap → takip → takibin takibi… zinciri keserse **aynı thread
içinde** yeni konuya geçmiş olur.»*

⚠ Ve eski yorum ihlali bir **karar** gibi savunuyordu (*«iki düğme, TEK sahip»*) — bir
yorumun kararlı görünmesi, onu doğru yapmaz ㊸🆪.

## Bu kapının üç yüklemi

| # | savunulan |
|---|---|
| 1 | *«konudan çık»* → **`zinciriKes`** |
| 2 | **`zinciriKes` `setActiveThreadId`'ye DOKUNMAZ** — asıl değişmez |
| 3 | *«+ yeni sohbet»* → **`yeniSohbet`**, ve o **thread'i düşürür** 🆃 |

Üçüncüsü zıt ölçüttür: yalnız ikinciyi ölçseydik, *«+ yeni sohbet»*i de thread'de
bırakmak kapıyı yeşil bırakırdı — ve o zaman **yeni sohbet açılamazdı**.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_SAYFA = (Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"
          / "app" / "page.tsx")

pytestmark = pytest.mark.skipif(
    not _SAYFA.exists(),
    reason="frontend mount edilmedi — kapı kapsamı dışında (kayıp `lab/kapi.py`'de bildirilir)")


def _kod() -> str:
    return _SAYFA.read_text(encoding="utf-8")


def _govde(ad: str) -> str:
    """`const <ad> = () => { … }` gövdesi — tek satırlık biçim de dâhil."""
    s = _kod()
    i = s.index(f"const {ad} = () =>")
    return s[i:s.index("\n  const ", i + 10)] if "\n  const " in s[i + 10:] else s[i:i + 400]


def test_KONUDAN_CIK_ZINCIRI_KESER():
    assert re.search(r"onClearContext=\{zinciriKes\}", _kod()), (
        "🔴 «konudan çık» `zinciriKes`'e bağlı değil — zincir/thread yeniden karışmış")


def test_ZINCIRI_KES_THREADE_DOKUNMAZ():
    """🔴 **ASIL DEĞİŞMEZ.** Zinciri kesmek sohbetten çıkarmaz."""
    g = _govde("zinciriKes")
    assert "setActiveThreadId" not in g, (
        "🔴 `zinciriKes` thread'i düşürüyor — kullanıcı konusunu bitirince sohbetten de "
        "çıkar. Karar: *thread bir UI gruplamasıdır, semantik sınır değildir*.")
    for alan in ("setContextCq", "setPrevSql"):
        assert alan in g, f"🔴 `zinciriKes` {alan} temizlemiyor — zincir gerçekten kesilmiyor"


def test_ZIT_OLCUT_YENI_SOHBET_THREADI_DUSURUR():
    """🆃 Kapının kurbanı: *«+ yeni sohbet»* **gerçekten** yeni thread açmalı."""
    assert re.search(r"onYeniSohbet=\{yeniSohbet\}", _kod()), (
        "🔴 «+ yeni sohbet» `yeniSohbet`'e bağlı değil")
    g = _govde("yeniSohbet")
    assert "setActiveThreadId" in g, (
        "🔴 `yeniSohbet` thread'i düşürmüyor — yeni sohbet açılamaz")
    assert "zinciriKes()" in g, (
        "🔴 `yeniSohbet` `zinciriKes`'i çağırmıyor — iki temizleme listesi bir gün ayrışır ㊲")
