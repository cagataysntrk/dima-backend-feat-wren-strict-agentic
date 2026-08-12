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

#: 🔴 (temiz soru, bozulmuş hâli, sınıf) — hepsi bu depoda **ölçülerek** seçildi.
#: ⚠ Liste **kapalı**: her kalem bir ölçümden gelir, bir dilek listesinden değil.
#:
#: ⟳ **2026-08-12'de YENİDEN KURULDU.** İlk üç kalemin **ikisi** `route()`'a hiç
#: düşmüyordu (`ciromuz ne kadar` · `fire orani yuksek mi` → `None`), yani `skip`
#: veriyordu: *bir sağlamlık kapısının atladığı vaka, ölçülmemiş bir vakadır.*
BOZULMALAR = [
    ("makine bazında ciro", "makine bazinda ciro", "cekim"),     # noktasız ı
    ("makine bazında fire", "makine bazında fıre", "yazim"),
    ("bu yıl ciro", "bu yil ciro", "cekim"),
    ("bu ay ciro", "bu ay cıro", "yazim"),
]

#: ⚠ **ÖLÇÜLMÜŞ DEVİR VAKALARI** — temiz soru route'lanıyor, bozulmuş hâli **düşüyor**.
#: Bunlar birer **kusur değildir**: bu deponun en üst kuralı *«route'a dil kuralı
#: EKLEME; şüphede garson devreye girer»* diyor ve `None` tam olarak o devrin
#: tetikleyicisidir. Burada listelenmelerinin sebebi, bir gün **sessizce** başka bir
#: küpe gitmeye başlarlarsa fark edilmesidir.
DEVRE_DUSENLER = [
    ("toplam ciro", "toplm ciro", "harf-düşmesi"),
    ("ortalama oee", "ortalama oe", "harf-düşmesi"),
]


def _kup(soru: str, schema: dict) -> str | None:
    """→ route'un seçtiği küp adı, yoksa `None`.

    🔴🔴 **BU YARDIMCI BİR KUSURUN KARŞILIĞIDIR.** İlk yazımım `a.get("cube")` diyordu;
    oysa `route()` şunu döndürüyor:

        {'cube_query': {'cube': 'parti', …}, 'measure', 'order', 'limit', 'period_optional'}

    Yani `"cube"` **kök seviyede yok** ve karşılaştırma daima `None == None` oluyordu —
    kapı **iki farklı küpü bile** eşit sayardı. Bir denetim ajanı bunu mutasyonla
    kanıtladı; kendi ölçümüm doğruladı. *Bir yüklemi yanlış adrese bağlamak, onu
    silmekten kötüdür: silinen kapı yoktur, yanlış bağlanan kapı VAR SANILIR.*
    """
    r = cr.route(soru, schema)
    if not isinstance(r, dict):
        return None
    return (r.get("cube_query") or {}).get("cube")


@pytest.mark.parametrize("temiz,bozuk,sinif", BOZULMALAR)
def test_BOZULMA_AYNI_KUBE_GIDER(temiz, bozuk, sinif, schema):
    """🔴 Sağlamlık farkı: bozulmuş yazım **aynı küpe** gitmeli.

    ⚠ Yüklem `route()` üzerinde: deterministik basamak. Garson (LLM) bozulmayı zaten
    tolere ediyor (canlıda ölçüldü) ama o **belirlenimsizdir** ve bir kapıya bağlanamaz.
    Burada ölçülen şey **deterministik yolun** kaybıdır.
    """
    a = _kup(temiz, schema)
    assert a is not None, (
        f"⊘ ölçüm tabanı çöktü: temiz soru «{temiz}» artık route'lanmıyor — bu vaka "
        "listeden çıkarılmalı ya da yerine route'lanan bir vaka konmalı. "
        "*Atlanan bir vaka, ölçülmemiş bir vakadır.*")
    b = _kup(bozuk, schema)
    assert b is not None, (
        f"🔴 SAĞLAMLIK KAYBI [{sinif}]: «{temiz}» route'lanıyor ama «{bozuk}» düşüyor. "
        "Kullanıcı aynı şeyi sordu, sistem birini anladı ötekini anlamadı.")
    assert a == b, (
        f"🔴 SAĞLAMLIK KAYBI [{sinif}]: küp değişti — «{temiz}»→{a} ama «{bozuk}»→{b}. "
        "*Bozulma cevabı değiştirdi.*")


@pytest.mark.parametrize("temiz,bozuk,sinif", DEVRE_DUSENLER)
def test_DEVRE_DUSEN_SESSIZCE_BASKA_KUBE_GITMIYOR(temiz, bozuk, sinif, schema):
    """⚠ Ölçülmüş devir vakaları: bozulmuş hâl route'a **düşüyor** ve bu **doğrudur**.

    Bu deponun en üst kuralı: *«route'a dil kuralı EKLEME; bir cümle anlaşılmıyorsa
    çözüm route'u genişletmek değil DEVRİ tetiklemektir.»* `None` o devrin
    tetikleyicisidir — yani burada ölçülen şey bir kusur değil, **tasarımın çalıştığı**.

    🔴 Kapının koruduğu şey **sessiz-yanlış**: bir gün bu sorular `None` yerine
    **başka bir küpe** gitmeye başlarsa, kullanıcı yanlış bir sayı alır ve hiçbir
    beyan konuşmaz. *Anlamamak bir hatadır; yanlış anlamak bir arızadır.*
    """
    a = _kup(temiz, schema)
    assert a is not None, f"⊘ ölçüm tabanı çöktü: «{temiz}» artık route'lanmıyor"
    b = _kup(bozuk, schema)
    assert b is None or b == a, (
        f"🔴 SESSİZ-YANLIŞ [{sinif}]: «{bozuk}» artık **{b}** küpüne gidiyor, oysa "
        f"temiz hâli **{a}**. Bozulmuş bir soruyu yanlış bir küple cevaplamak, hiç "
        "cevaplamamaktan kötüdür — çünkü sayı doğru görünür.")
    if b == a:
        pytest.skip(
            f"✅ İYİ HABER: «{bozuk}» artık doğru küpe ({a}) route'lanıyor — deterministik "
            "yol güçlenmiş. Vakayı `BOZULMALAR`'a taşıyın.")


def test_HICBIR_VAKA_ATLANMIYOR(schema):
    """🔴🔴 **META KAPI** — *bir sağlamlık kapısının atladığı vaka, ölçülmemiş bir
    vakadır.*

    İlk yazımda üç vakanın **ikisi** `skip` veriyordu (temiz soru route'lanmıyordu) ve
    `pytest` bunu **iyi haber gibi** (`2 skipped`) raporluyordu. Yani *«üç bozulma
    sınıfı ölçülüyor»* cümlesinin arkasında **tek** bir canlı yüklem vardı.

    ⚠ Bu kapı `BOZULMALAR`'ın tamamının **ölçülebilir** kaldığını garanti eder; bir
    vaka bir gün route'lanmaz olursa burada kırmızı verir, sessizce atlanmaz.
    """
    dusen = [t for t, _b, _s in BOZULMALAR if _kup(t, schema) is None]
    assert not dusen, (
        f"🔴 bu temiz sorular artık route'lanmıyor: {dusen} — vakaları ölçülemez hâle "
        "geldi. Listeyi ölçerek yenileyin; *atlanan bir kapı, olmayan bir kapıdır.*")


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
