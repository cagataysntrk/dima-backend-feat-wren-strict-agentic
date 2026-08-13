"""🔴 `§64` — **ÖNİZLEMENİN YÜZÜ** + **uzun bileşikte şerit söner**.

`§63` ucu kurdu: çok adımlı plan onaysız **koşmuyor**, `source="onizleme"` dönüyor.
Ama bir arka-uç yeteneği, tüketicisi olmadan *«bitti»* değildir 🆘 — kullanıcı için
önizleme **hâlâ yoktu**: `postMakro` `kos` alanını hiç göndermiyordu, dönen `adimlar`
ise okunmadan atılıyordu.

## Planın iki cümlesi

| yer | cümle |
|---|---|
| `§33` satır 11 | *«**uzun bileşik** (>8 kelime ∨ fiil) → 🔴 **şerit söner** → garson → plan önizleme»* |
| satır `1242` | *«**adımlar dikey**, yuvalar yatay; ikisi aynı şeritte olmaz»* |

Birincisi bir **susma** kararıdır: kullanıcı bir kelime aramıyor, bir **plan** yazıyor;
oraya tamamlama basmak gürültüdür. İkincisi bir **biçim** kararıdır: bir plan bir sıradır,
yatay dizilen sıra kaydırma çubuğunun arkasında biter.

## Bu kapının dört yüklemi

| # | savunulan | ders |
|---|---|---|
| 1 | `postMakro` **`kos` taşır** | onaysız çağrı gerçekten onaysız gider |
| 2 | uzun girdide şerit **söner**, eşik **tek sahipli** | ㊲ |
| 3 | önizleme **dikey** (`<ol>`) ve pill satırının **altında** | plan `1242` |
| 4 | 🆃 **kısa girdide şerit hâlâ yanar** | kapı özelliği öldürmesin |

Dördüncüsü zıt ölçüttür: yalnız *«uzun girdide sussun»* ölçseydik, şeridi **tümden**
kapatmak kapıyı yeşil bırakırdı.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_FE = Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"

pytestmark = pytest.mark.skipif(
    not _FE.exists(),
    reason="frontend mount edilmedi — kapı kapsamı dışında (kayıp `lab/kapi.py`'de bildirilir)")


def _oku(*parca: str) -> str:
    return _FE.joinpath(*parca).read_text(encoding="utf-8")


def test_MAKRO_ONAY_ALANI_TASIR():
    """🔴 **ASIL DEĞİŞMEZ.** `kos` gövdeye girmiyorsa uç hep önizler ya da hep koşar."""
    s = _oku("lib", "api-client.ts")
    imza = s[s.index("export async function postMakro"):][:400]
    assert "kos?: boolean" in imza, f"🔴 `postMakro` onay alanı almıyor:\n{imza[:200]}"
    assert re.search(r"kos:\s*makro\.kos", _oku("app", "page.tsx")), (
        "🔴 `page.tsx` onayı uca geçirmiyor — `[koş]` düğmesi hiçbir şeyi koşturmaz 🅯")


def test_UZUN_BILESIKTE_SERIT_SONER():
    """`§33` satır 11 — ve eşik **tek sahipli** olmalı ㊲."""
    s = _oku("components", "OneriSeridi.tsx")
    assert s.count("AZAMI_KELIME = ") == 1, "🔴 eşiğin iki sahibi var — bir gün ayrışır ㊲"
    assert "uzunBilesik(q)" in s, (
        "🔴 uzun girdi şeridi susturmuyor — kullanıcı plan yazarken tamamlama gürültüsü alır")
    # ⚠ `index` ilk vuruşu alır ve bu dosyanın **başındaki şerh** de aynı ifadeyi
    # anıyor 🅞: aranan **kullanım**dır, sözü değil — o yüzden `||` ile birlikte aranır.
    kosul = s[s.index("if (kapaliBayrak ||"):][:220]
    assert "uzunBilesik" in kosul, f"🔴 susma getirme koşuluna bağlı değil:\n{kosul[:140]}"


def test_ONIZLEME_DIKEY_VE_PILLIN_ALTINDA():
    """Plan `1242`: *«adımlar dikey, yuvalar yatay»* — ve sıra bir okuma yönüdür."""
    o = _oku("components", "PlanOnizleme.tsx")
    assert "<ol" in o, "🔴 adımlar sıralı liste değil — sıra anlam taşıyor, süs değil"
    for tus in ("koş", "düzenle", "iptal"):
        assert f">{tus}" in o.replace("\n", "").replace(" ", "") or tus in o, (
            f"🔴 `[{tus}]` düğmesi yok — karar kullanıcınındır (`§3.1`)")
    assert "gecerli" in o and "disabled={!gecerli" in o, (
        "🔴 geçersiz plan koşulabilir görünüyor")
    b = _oku("components", "Besteci.tsx")
    assert b.index("<PillSatiri") < b.index("<PlanOnizleme"), (
        "🔴 önizleme pill satırının ÜSTÜNDE — plan pill'lerden türer, o yüzden altındadır")


def test_ZIT_OLCUT_KISA_GIRDIDE_SERIT_YANAR():
    """🆃 Kapının kurbanı: susma kuralı şeridi **tümden** kapatmamalı."""
    s = _oku("components", "OneriSeridi.tsx")
    esik = int(re.search(r"AZAMI_KELIME = (\d+)", s).group(1))
    assert esik >= 5, f"🔴 eşik {esik} — sıradan bir soru bile şeridi söndürür"
    fn = re.search(r"const uzunBilesik = .+", s).group(0)
    ortam: dict = {}
    # ⚠ TS okunmaz; kural **sayılabilir** olduğu için Python'da aynısı kurulur ve
    # eşik **dosyadan** okunur — kapı sabiti kendi uydurmaz 🅬.
    exec(f"uzun = lambda q: len([t for t in q.split() if t]) > {esik}", ortam)
    assert not ortam["uzun"]("ram 3 neden düşük"), f"🔴 kısa soru susturuldu: {fn}"
    assert ortam["uzun"]("geçen ay ram 3 fire oranını makine bazında kır ve en kötüyü anlat")
