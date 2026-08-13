"""🔴 `§69` — **ÖNİZLEME ZİNCİRİ UÇTAN UCA BAĞLI MI** (`§66`–`§68`'in tüketici kapısı).

Bu operasyonda aynı kusur **iki kez** ölçüldü ve ikisi de *«backend'de çalışıyor»* denen
şeylerdi 🆘:

| ne zaman | kusur |
|---|---|
| `§64` | `postMakro` `kos` alanını **hiç göndermiyordu**; dönen `adimlar` okunmadan atılıyordu |
| `§68-ek` | `kararsiz_onizleme` istisna atıyordu, dış `except` yutuyordu — kütük *«ONAYA düşüyor»* yazarken kullanıcı normal cevabı görüyordu 🅯 |

⚠ **Bu kapı bir tarayıcı testi DEĞİLDİR** ve onun yerine geçmez 🆂: bir zincirin **kodda**
bağlı olması, ekranda **göründüğünün** kanıtı değildir. Savunduğu şey daha dar ama gerçek:
*zincirin hiçbir halkası sessizce kopmadı.*

## Zincir

```
/ask ─▶ AskResponse.{adimlar,gecerli,plan_taslagi,piller}
      ─▶ page.tsx: onizleme.yakala(...)   (yakalanan cevap KAYDEDİLMEZ)
      ─▶ lib/onizleme.ts: durum + onayla()
      ─▶ Besteci: <PlanOnizleme …>        (pill satırının ALTINDA)
      ─▶ PlanOnizleme: <PillSatiri verilen={…}> + [koş] [düzenle] [iptal]
      ─▶ [koş] ─▶ api-client.postPlanKos ─▶ POST /plan/kos   (⊘ LLM)
```

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | her halka **var** ve bir sonrakini **çağırıyor** |
| 2 | onay ucu istemcide **gerçekten** çağrılıyor (yetim değil 🆘) |
| 3 | `[koş]` ile `[iptal]` **ayrı** işleyiciler — biri ötekinin yerine geçmez |
| 4 | 🆃 ölçüt **kullanım** arıyor, import/sözü değil 🅞 |
"""

from __future__ import annotations

import pathlib

import pytest

_FE = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"

pytestmark = pytest.mark.skipif(
    not _FE.exists(),
    reason="frontend mount edilmedi — kapı kapsamı dışında (kayıp `lab/kapi.py`'de bildirilir)")


def _oku(*p: str) -> str:
    return _FE.joinpath(*p).read_text(encoding="utf-8")


def _govde(metin: str) -> str:
    """Yorumsuz gövde — *sözü değil kullanımı ara* 🅞."""
    satir = [l for l in metin.split("\n")
             if not l.lstrip().startswith(("//", "*", "/*"))]
    return "\n".join(satir)


def test_HER_HALKA_BIR_SONRAKINI_CAGIRIYOR():
    """🔴 **ASIL DEĞİŞMEZ.** Bir halka koparsa özellik sessizce ölür."""
    zincir = [
        ("app/page.tsx", "onizleme.yakala("),
        ("lib/onizleme.ts", "cevap.plan_taslagi"),
        ("components/Besteci.tsx", "<PlanOnizleme"),
        ("components/PlanOnizleme.tsx", "<PillSatiri"),
        ("components/PillSatiri.tsx", "verilen"),
    ]
    for yol, aranan in zincir:
        assert aranan in _govde(_oku(*yol.split("/"))), (
            f"🔴 zincir koptu: {yol} artık `{aranan}` içermiyor")


def test_ONAY_UCU_YETIM_DEGIL():
    """🆘 Bir uç, tüketicisi olmadan *«bitti»* değildir."""
    assert "postPlanKos" in _govde(_oku("lib", "api-client.ts")), "🔴 sarmalayıcı yok"
    assert "postPlanKos(" in _govde(_oku("app", "page.tsx")), (
        "🔴 `POST /plan/kos` istemcide **çağrılmıyor** — onay düğmesi hiçbir şey koşturmaz 🅯")


def test_KOS_VE_IPTAL_AYRI():
    """⚠ İki edim, iki işleyici: `[koş]` koşar, `[iptal]` kapatır. Birini ötekine bağlamak
    bu depoda ölçülmüş bir kusur sınıfıdır (`§60`: zincir/thread)."""
    g = _govde(_oku("components", "PlanOnizleme.tsx"))
    assert "onClick={onKos}" in g and "onClick={onIptal}" in g, (
        "🔴 `[koş]`/`[iptal]` ayrı işleyicilere bağlı değil")
    b = _govde(_oku("components", "Besteci.tsx"))
    assert "onKos={onizleme.kos}" in b and "onIptal={onizleme.iptal}" in b, (
        "🔴 besteci iki edimi ayrı geçirmiyor")


def test_ZIT_OLCUT_YORUMDAKI_SOZ_SAYILMAZ():
    """🆃🅞 Kapının kendi ölçütü sınanır: bir **yorum** satırı yüklemi geçirmemeli.
    (Bu operasyonda tam olarak o oldu — `resolve_for` bir yorumda geçiyordu ve kapı
    yanlış kırmızı verdi.)"""
    assert "postPlanKos" not in _govde("// postPlanKos burada YALNIZ anılıyor\n")
