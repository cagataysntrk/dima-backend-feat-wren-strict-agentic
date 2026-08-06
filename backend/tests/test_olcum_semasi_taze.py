"""🔴 ÖLÇÜM ARACININ ŞEMASI **TAZE** OLMALI — bayat okuma, yanlış sonuçtan kötüdür.

## Ölçülen kusur (2026-08-06) — *ölçüm aracının kendisi yalan söyledi*

`lab/gercek_dunya.py` şemayı `settings.resolved_project_dir()`ten, yani paylaşılan
`demo/wren-project`ten okuyordu. O dizin **gitignore'lu bir DERLEME ARTEFAKTIDIR**
(`backend/.gitignore:15`) ve pack'ler değiştiğinde kendiliğinden yenilenmez.

`lab/nl_corpus.py` ise ta baştan `izole_proje_ayna` ile **taze** derliyordu. Yani:

> 🔴 İki ölçüm aracı, **iki farklı şema kaynağından** okuyordu — ve biri bayat olabiliyordu.
> Bu, deponun kendi ölçülmüş kusur sınıfının (*"aynı kuralın iki sahibi"*) **ölçüm
> katmanına** düşmüş hâlidir.

## Bedeli — ölçüldü, tahmin değil

Bir katalog turunda `git checkout` ile geri alınan sinonimler artefakta **yazılı kaldı**
(geri alma onu görmez: dosya izlenmiyor). Aynı kaynak durumda ardışık koşumlar:

| ölçü | koşum A | koşum B |
|---|---|---|
| `sessiz_yanlis` | **8** | **17** |
| `dogru` | **83** | **80** |

Ve **tertemiz bir ağaçta kapı KIRMIZI görünüyordu.** Altı ayrı ölçüm yanlış okundu;
biri, sağlam bir değişikliğin **geri alınmasına** yol açtı.

> 🔴 *Bir ölçüm aracının bayat okuması, yanlış bir sonuçtan daha kötüdür: yanlış sonuç
> sorgulanır, bayat okuma GÜVENİLİR.*

⚠ Ve neden bir **kod-yapısı** kapısı: davranış testi bunu göremez. Bayat artefakt
**geçerli** bir şemadır — sadece **başka bir anın** şemasıdır. Kırmızı vermez, *farklı*
verir. Yakalanabilecek tek yer, şemanın **nereden** alındığıdır.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

LAB = pathlib.Path(__file__).resolve().parents[1] / "lab"

#: Katalog/şema üzerinden ölçüm yapan araçlar. Her biri şemasını **kendi derlemesinden**
#: almalıdır. ⚠ Bu liste büyüdükçe kapı da büyür — yeni bir ölçüm aracı yazan geliştirici
#: buraya eklemeyi unutursa, kapı onu **büyüme** üzerinden değil, listeye eklenmediği için
#: kaçırır; bu bilinen ve yazılı sınırdır.
OLCUM_ARACLARI = ["gercek_dunya.py", "nl_corpus.py"]


def _kaynak(ad: str) -> str:
    p = LAB / ad
    if not p.exists():
        pytest.skip(f"⊘ {ad} yok")
    return p.read_text(encoding="utf-8")


@pytest.mark.parametrize("ad", OLCUM_ARACLARI)
def test_OLCUM_ARACI_TAZE_DERLIYOR(ad):
    """🔴 **ASIL KAPI** — her ölçüm aracı `izole_proje_ayna` ile kendi ağacına derler."""
    src = _kaynak(ad)
    assert "izole_proje_ayna" in src, (
        f"🔴 `{ad}` şemayı paylaşılan `demo/wren-project`ten okuyor. O dizin GİTIGNORE'LU "
        f"bir derleme artefaktıdır ve pack değişiminde yenilenmez — ölçüm sessizce BAYAT "
        f"bir katalogla koşar. `os.environ['DIMA_PROJECT_DIR'] = izole_proje_ayna(...)` "
        f"+ `compose_and_build(...)` kullan.")


def test_GERCEK_DUNYA_DERLEMEYI_DE_YAPIYOR():
    """⚠ Ayna yalnız **boş** bir çıktı dizini kurar; derlemeyi çağıran yapar (ADR-0005,
    `tests/conftest.py` ile aynı sözleşme).

    Aynayı kurup derlemeyi atlamak, bayat şemayı **yok** şemayla değiştirirdi — daha
    dürüst, ama yine yanlış. Ve ilk denemede tam olarak bu oldu:
    `FileNotFoundError: MDL derlenmemiş`."""
    src = _kaynak("gercek_dunya.py")
    i, j = src.find("izole_proje_ayna("), src.find("compose_and_build(")
    assert j != -1, "🔴 ayna kuruluyor ama derleme yok — şema BOŞ olur"
    assert i < j, "🔴 derleme aynadan ÖNCE çağrılıyor — gerçek ağaca yazar, izolasyon ölür"


def test_PAYLASILAN_ARTEFAKTA_GERI_DONULMUYOR():
    """🔴 Regresyon kapısı: `resolved_project_dir()` ölçüm aracında **doğrudan** şema
    kaynağı olamaz. Ayna kurulduktan SONRA çağrılması meşrudur (ayna zaten onu
    yönlendirir); yasak olan, **ayna kurulmadan** çağrılmasıdır."""
    src = _kaynak("gercek_dunya.py")
    agac = ast.parse(src)
    fn = next((n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name == "kos"), None)
    assert fn is not None, "⊘ `kos()` bulunamadı — kapı bayatlamış"
    govde = ast.unparse(fn)
    i, j = govde.find("izole_proje_ayna("), govde.find("resolved_project_dir(")
    assert i != -1 and (j == -1 or i < j), \
        "🔴 şema, ayna kurulmadan paylaşılan artefakttan okunuyor"


def test_ARTEFAKT_GERCEKTEN_IZLENMIYOR():
    """⊙ Kusurun **öncülü**: `demo/wren-project` izlenmiyor olmasaydı `git checkout` onu
    da geri alırdı ve bu sınıf hiç doğmazdı. Öncül değişirse kapı gereksizleşir — ve
    bunu bilmek, kapıyı körü körüne taşımaktan iyidir."""
    gi = (pathlib.Path(__file__).resolve().parents[1] / ".gitignore")
    if not gi.exists():
        pytest.skip("⊘ .gitignore yok")
    assert "demo/wren-project" in gi.read_text(encoding="utf-8"), \
        "⟳ artefakt artık izleniyor — bu kapının gerekçesini gözden geçir"
