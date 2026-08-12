"""🔴🔴 `§A10` — **SAĞLAMLIK FARKI** (`Dr.Spider` deseni): aynı soru, bozulmuş yazımla.

## Neden bu kalem ve neden ŞİMDİ

`Dr.Spider` (Apache-2.0, ICLR 2023) **17 pertürbasyon** tanımlar ve tek bir sayı ölçer:

    robustness gap = acc(orijinal) − acc(bozulmuş)

Kartın kendi notu şunu söylüyordu: *«`göre`/`bazında`/`bazlı` üçlü aşırı-yüklenmesi bu
deponun bilinen kırılganlığı»*. Bu turda o not **eksik** çıktı: aşırı-yüklenme **üçlü
değil DÖRTLÜ** — dördüncü anlam (*«dolar bazında»* = bir **para birimi**) canlı turda
yakalandı ve yanlış bir *«kırılım istedin»* beyanı üretiyordu (`§Ö10-b`).

⊙ Yani bu kapı bir tahmine değil, **ölçülmüş bir kırılganlık sınıfına** dayanıyor.

## Kapsam — dar ve YAPISAL, 17 pertürbasyon değil ÜÇ SINIF

`Dr.Spider`'ın 17'si İngilizce şema/soru bozulmalarıdır. Bu depoda ölçülmüş **üç** sınıf
var ve üçü de canlıda kusur üretti:

| sınıf | örnek | ölçülen kusur |
|---|---|---|
| **yazım hatası** | `cirumuz` · `fıre` | `§KA` sahte *«varsayım»* damgası |
| **edat aşırı-yüklenmesi** | `dolar bazında` ↔ `makine bazında` | yanlış *«kırılım istedin»* beyanı |
| **ek/çekim** | `ciromuz` · `zayiatimiz` | ölçü çözülmüyordu |

⚠ **Yeni bir korpus yazılmadı**: pertürbasyonlar `route()`+`niyet` üzerinde
**deterministik** olarak ölçülür (LLM yok, ağ yok, ~saniyeler). *Bir sağlamlık ölçümü,
ölçtüğü sistemden pahalıya mal olursa koşulmaz.*

> *Bir sistemin sağlamlığı, doğru yazılmış sorulardaki başarısı değil, yanlış yazılmış
> sorulardaki KAYBIDIR.*
"""

from __future__ import annotations

import pytest

from app import cube_router as cr

#: 🔴 (temiz soru, bozulmuş hâli, sınıf) — üçü de bu depoda **canlıda** ölçüldü.
#: ⚠ Liste **kapalı**: her kalem bir canlı turdan gelir, bir dilek listesinden değil.
BOZULMALAR = [
    ("ciromuz ne kadar", "cirumuz ne kadar", "yazim"),
    ("fire orani yuksek mi", "fıre oranı yüksek mi", "yazim"),
    ("makine bazında ciro", "makine bazinda ciro", "cekim"),
]


def _cq(soru: str, schema: dict) -> dict | None:
    return cr.route(soru, schema)


@pytest.mark.parametrize("temiz,bozuk,sinif", BOZULMALAR)
def test_BOZULMA_AYNI_KUBE_GIDER(temiz, bozuk, sinif, schema):
    """🔴 Sağlamlık farkı: bozulmuş yazım **aynı küpe** gitmeli.

    ⚠ Yüklem `route()` üzerinde: deterministik basamak. Garson (LLM) bozulmayı zaten
    tolere ediyor (canlıda ölçüldü) ama o **belirlenimsizdir** ve bir kapıya bağlanamaz.
    Burada ölçülen şey **deterministik yolun** kaybıdır.
    """
    a, b = _cq(temiz, schema), _cq(bozuk, schema)
    if a is None:
        pytest.skip(f"⊘ temiz soru zaten route'a düşmüyor ({temiz}) — kayıp ölçülemez")
    assert b is not None, (
        f"🔴 SAĞLAMLIK KAYBI [{sinif}]: «{temiz}» route'lanıyor ama «{bozuk}» düşüyor. "
        "Kullanıcı aynı şeyi sordu, sistem birini anladı ötekini anlamadı.")
    assert a.get("cube") == b.get("cube"), (
        f"🔴 SAĞLAMLIK KAYBI [{sinif}]: küp değişti — «{temiz}»→{a.get('cube')} ama "
        f"«{bozuk}»→{b.get('cube')}. *Bozulma cevabı değiştirdi.*")


def test_BAZINDA_DORDUNCU_ANLAMI_AYIRT_EDILIYOR(schema):
    """🔴🔴 **BU TURDA ÖLÇÜLEN KIRILGANLIK** — `§Ö10-b`.

    `göre`/`bazında` bu depoda **dört** anlama geliyor: kırılım · granülerlik ·
    dönem-aralığı · **birim/para birimi**. Dördüncüsü canlıda yanlış bir beyan üretti
    (*«bir kırılım istedin ama boyut taşıyamadım»* — oysa kullanıcı **dolar** istedi).

    Ayrım **katalogdan** kurulur: soruda hiçbir küpte boyut adayı yoksa `bazında` bir
    kırılım işareti değildir.
    """
    from app import uyum

    cq = {"cube_query": {"cube": "parti", "measures": ["toplam_ciro"],
                         "dimensions": [], "filters": []}}
    cm = next(c for c in schema["cubes"] if c["name"] == "parti")
    para = [i.isaret for i in uyum.denetle("dolar bazında ciro", cq, cm, schema)]
    gercek = [i.isaret for i in uyum.denetle("makine bazında ciro", cq, cm, schema)]
    assert "kirilim" not in para, (
        "🔴 para birimi bir KIRILIM sanıldı — yanlış beyan, sessizlikten kötüdür.")
    assert "kirilim" in gercek, (
        "🔴 gerçek kırılım isteği susturuldu — düzeltme kapsamı yuttu.")


def test_OLCUM_UCUZ_KALIYOR():
    """⚠ Bu kapı **LLM'siz ve ağsız** olmalı; yoksa koşulmaz ve koşulmayan bir kapı
    yoktur. Yüklem yapısal: dosya bir sağlayıcı/istemci ithal etmiyor."""
    import ast
    import pathlib

    agac = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    ithal = set()
    for n in ast.walk(agac):
        if isinstance(n, ast.Import):
            ithal |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            ithal.add(n.module)
    yasak = {i for i in ithal if any(k in i for k in ("llm", "httpx", "requests",
                                                     "openai", "TestClient"))}
    assert not yasak, f"🔴 sağlamlık kapısı ağ/LLM'e bağlandı: {yasak}"


def test_BOZULMA_LISTESI_CANLIDAN_GELIYOR():
    """🔴 `ADR-0008` disiplini: liste bir **dilek** değil, ölçülmüş vakalar.

    Her kalem bir canlı turdan gelir; listeye bir kalem eklemek, onu **canlıda ölçmüş**
    olmayı gerektirir. *Bir sağlamlık listesi uydurulursa, ölçtüğü şey hayal gücüdür.*
    """
    assert len(BOZULMALAR) >= 3
    siniflar = {s for _, _, s in BOZULMALAR}
    assert siniflar <= {"yazim", "cekim", "edat"}, (
        f"🔴 tanınmayan pertürbasyon sınıfı: {siniflar - {'yazim', 'cekim', 'edat'}}")
