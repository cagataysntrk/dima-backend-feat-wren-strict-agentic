r"""🔴🔴 `§40.1` — *«KODDA İZ YOK»* BİR İDDİADIR; ve iddialar **çürür**.

## Neden bu kapı — ölçülmüş bir çelişki sınıfı

Bu turda aynı kusur **üç kez** göründü ve üçü de aynı sınıftandı: rapor bir şeyin
**yokluğunu** yazmış, o şey bu arada **var olmuş**, ve hiçbir kırmızı konuşmamış.

| yer | rapor diyordu | ölçüm |
|---|---|---|
| `§18.1` | *«cevap biçimi basamağı YOK»* | `app/bicim.py` **6.132 bayt**, `answer.py:864` tüketiyor |
| `§16.3` | *«`rls` hiç kullanılmadı»* | **11** çağrı yeri |
| `§40.7 F14` | *«`dry_run` ✅ kullanılıyor»* | `backend/app/` altında **0** çağrı |

⊙ Üçü de bir **yokluk/varlık iddiası**ydı ve üçü de **elle** yazılmıştı. Karnenin
manşetini koruyan bir kapı vardı (`test_karne_kendini_sayar.py`); ama karnenin
**kaynağı olan bölümleri** koruyan hiçbir şey yoktu.

> ㊿ *Bir özeti korumak, özetlediği şeyi korumaz.*

✅ Bu dosya `§40.1`'in makine-okunur envanterini **rapordan okur** ve **koddan** yeniden
ölçer. Bir sembol envanterde *«iz yok»* yazılıyken kodda belirirse, kapı konuşur.

## 🔴 YÜKLEM NEDEN `ast` — ve bu kapının kendi yanılması

İlk tasarımım kaba `grep` idi. Ölçüldü, **iki yanlış kırmızı** üretiyordu:

    LMDI      → `tests/test_e7_toplamsal_ayristirma.py` docstring'inde geçiyor
                (ama orada *«LMDI DEĞİLİZ»* yazıyor — bir **red** kaydı, bir kullanım değil)
    zemberek  → `test_ZEMBEREK_ALINMADI_gerekcesi_YAZILI` — adı bir **gerekçe kaydı**

İkisi de metindir; hiçbiri bir kod izi değildir. *Bir şeyi almadığını yazmak, onu almak
değildir* — ve bunu ayırt edemeyen bir yüklem, dürüstlüğü kusur diye raporlar.

⚠ İkinci yanılma **alt-dize**ydi: `m_schema` alt-dizesi `scenarios_from_schema`'yı
yakalıyordu. Eşleşme artık **tam addır**.

> *Bir yokluk iddiasını doğrularken, o iddianın kendi kaydını kanıt sanmamak gerekir.*
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

_BACKEND = pathlib.Path(__file__).parent.parent
_RAPOR = (_BACKEND.parent / "belgeler" / "arastirma"
          / "2026-08-11_REKABET-VE-MIMARI-ANALIZI.md")

pytestmark = pytest.mark.skipif(
    not _RAPOR.parent.is_dir(),
    reason="`belgeler/` bağlanmamış — konteynere `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin")

#: ⚠ Taranan ağaçlar: ürün · laboratuvar · kapılar. `demo/` **bilerek dışarıda** —
#: orası gitignore'lu bir derleme artefaktı barındırır (bu deponun ⑪ numaralı dersi).
_AGACLAR = ("app", "lab", "tests")


def _kod_adlari() -> set[str]:
    """Depodaki **kod adlarının** tamamı — yorumlar ve docstring'ler **hariç**.

    `ast` bunu bedava verir: bir docstring `ast.Constant`'tır, `ast.Name` değil.
    """
    adlar: set[str] = set()
    for kok in _AGACLAR:
        for f in (_BACKEND / kok).rglob("*.py"):
            try:
                agac = ast.parse(f.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):        # noqa: PERF203
                continue
            for n in ast.walk(agac):
                if isinstance(n, ast.Name):
                    adlar.add(n.id)
                elif isinstance(n, ast.Attribute):
                    adlar.add(n.attr)
                elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    adlar.add(n.name)
                elif isinstance(n, ast.arg):
                    adlar.add(n.arg)
                elif isinstance(n, ast.Import):
                    for a in n.names:
                        adlar |= set(a.name.split("."))
                elif isinstance(n, ast.ImportFrom) and n.module:
                    adlar |= set(n.module.split("."))
    return adlar


def _iz_yok_iddiasi() -> list[str]:
    """`§40.1` envanterinden *«kodda İZ YOK»* satırının sembollerini okur.

    ⚠ Yüklem **rapordan** okuyor, buraya kopyalamıyor: kopyalasaydım envanter
    değiştiğinde kapı **eski listeyi** ölçmeye devam ederdi — `KAT-1`'in belgelerdeki
    hâli. *Bir listeyi iki yere yazmak, ikisini de yanlış yapmanın en kolay yoludur.*
    """
    metin = _RAPOR.read_text(encoding="utf-8")
    bas = metin.index("### 40.1 ")
    blok = metin[bas:metin.index("### 40.2", bas)]
    satir = next((s for s in blok.splitlines() if "kodda İZ YOK" in s), None)
    assert satir, (
        "⊘ ölçüm tabanı çöktü: `§40.1`'de *«kodda İZ YOK»* satırı bulunamadı. "
        "Envanterin biçimi değiştiyse bu ayrıştırıcı düzeltilsin — kapı susturulmasın.")
    sol = satir.split("→")[0]
    return [p.strip().strip("`*") for p in sol.split("·") if p.strip()]


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı.** Sıfır sembol okuyan ya da sıfır ad tarayan bir yüklem, her
    envanteri doğrular."""
    semboller = _iz_yok_iddiasi()
    assert len(semboller) >= 4, (
        f"⊘ envanterden yalnız {len(semboller)} sembol okundu: {semboller}")
    assert len(_kod_adlari()) > 5000, "⊘ kod tarayıcısı boş döndü — yüklem boşa düşer"


def test_IZ_YOK_DENEN_SEMBOL_GERCEKTEN_YOK():
    """🔴🔴 **ASIL KAPI.** Envanterde *«iz yok»* yazan her sembol, kodda **gerçekten**
    yok olmalı.

    Kırmızı verirse iki şeyden biri olmuştur ve **ikisi de iyi haberdir**:
    ① yetenek kuruldu → envanter satırı ✅'e çevrilsin, ilgili kart yeniden okunsun;
    ② sembol başka bir amaçla doğdu → ad çakışması yazılsın.

    ⚠ Yalnız *«yamalayıp geçmek»* yanlış olurdu: bu envanter `§40`'ın **karar
    tablosunun** dayanağıdır; bir satırı değişince üstündeki `⊘` kararı da yeniden
    gerekçelendirilmelidir.
    """
    adlar = _kod_adlari()
    bulunan = {}
    for s in _iz_yok_iddiasi():
        # `M-Schema` gibi tireli akademik adlar kodda `_` ile yazılırdı
        for aday in {s, s.replace("-", "_")}:
            if aday in adlar:
                bulunan[s] = aday
    assert not bulunan, (
        f"🔴 `§40.1` envanteri BAYAT: *«kodda İZ YOK»* denen sembol(ler) artık kodda "
        f"VAR → {bulunan}.\n"
        "*Bir yokluk iddiası, iddia edildiği yerde değil ÖLÇÜLDÜĞÜ yerde doğrudur.* "
        "Envanter satırını güncelleyin **ve** o sembole dayanan `§40` kararını yeniden "
        "okuyun — dayanağı değişen bir karar, verilmemiş bir karardır.")


def test_KURULU_DEGIL_DENEN_PAKET_GERCEKTEN_KURULU_DEGIL():
    """⚠ Envanterin ikinci satırı bağımlılıklar hakkında. Biri kurulursa *«ölçtük,
    almadık»* kararları dayanaksız kalır.

    ⊙ Yüklem `importlib.util.find_spec` — `pip list` ayrıştırmak yerine **çalışma
    zamanının kendi cevabını** sorar (ders ㊹: motor ≠ veri; burada da *ilan ≠ kurulum*).
    """
    import importlib.util

    metin = _RAPOR.read_text(encoding="utf-8")
    bas = metin.index("### 40.1 ")
    blok = metin[bas:metin.index("### 40.2", bas)]
    satir = next((s for s in blok.splitlines() if "HİÇBİRİ KURULU DEĞİL" in s), None)
    if not satir:
        pytest.skip("⊘ envanterde *«hiçbiri kurulu değil»* satırı yok")
    paketler = [p.strip().strip("`*") for p in satir.split("→")[0].split("·") if p.strip()]
    assert paketler, "⊘ ölçüm tabanı çöktü: paket listesi boş"
    kurulu = []
    for p in paketler:
        ad = re.sub(r"[^A-Za-z0-9_]", "_", p)
        try:
            if importlib.util.find_spec(ad) is not None:
                kurulu.append(p)
        except (ImportError, ValueError):                    # noqa: PERF203
            pass
    assert not kurulu, (
        f"🔴 `§40.1` *«hiçbiri kurulu değil»* diyor ama kurulu: {kurulu}. "
        "Bir bağımlılık sessizce girdiyse, onu reddeden karar da sessizce çürümüştür.")


def test_VAR_DENEN_DOSYA_GERCEKTEN_VAR():
    """⚠ Simetri: envanter yalnız yoklukları değil **varlıkları** da iddia ediyor.
    Bir dosya silinirse `✅ VAR` satırı yalan söylemeye başlar.

    ⊙ Bu kapı `§40.2`'nin `F16` kararını da taşıyor: o karar birebir
    `test_view_fanout_guard.py`'nin **varlığına** dayanıyor.
    """
    metin = _RAPOR.read_text(encoding="utf-8")
    bas = metin.index("### 40.1 ")
    blok = metin[bas:metin.index("### 40.2", bas)]
    eksik = []
    for dosya in set(re.findall(r"`(test_[a-z0-9_]+\.py)`", blok)):
        if not (_BACKEND / "tests" / dosya).is_file():
            eksik.append(dosya)
    assert not eksik, (
        f"🔴 `§40.1` var dediği kapı dosyası yok: {eksik}. "
        "*Bir kararın dayanağı silinirse, karar da silinmiştir — ilanı kalsa bile.*")
