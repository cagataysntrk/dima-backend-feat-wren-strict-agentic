"""🔴 KAPININ KENDİSİ DENETLENİYOR — *"bu adım gerçekten kırmızı verebiliyor mu?"*

## Ne bulundu

`lab/kapi.py --tam` **dört** adım koşar: süit · `eval` · korpus · **konuşma senaryoları**.
Dördüncüsü **kapı değildi, RAPORDU**: `lab/konusma_senaryolari.py::main()` her yolda
`None` dönüyordu → süreç **her zaman `0`** ile çıkıyordu → adım **hiçbir koşulda**
kırmızı veremiyordu. Ölçüldü: `subprocess.run(...).returncode == 0`.

Kapının *"senaryo düşürülen 0"* satırının hiç kıpırdamamasının sebebi de buydu — o
satır bir gözlemdi, bir güvence değil.

> MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır."*
> Bu, o sınıfın **kapının kendi içindeki** örneğidir ve en pahalısıdır: dört bileşenli
> bir kapının **dörtte biri** sessizce dekordu.

## Bu dosya ne yapar

Her kapı adımının **çıkış kodu üretebildiğini** yapısal olarak kilitler. Bir adım
eklendiğinde ya da bir aracın `--kapi` bayrağı düştüğünde burası kırmızı verir.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from lab import kapi as kapi_mod
from lab import konusma_senaryolari as ks

LAB = pathlib.Path(kapi_mod.__file__).resolve().parent


def _tam_adimlari() -> list[list[str]]:
    """`--tam`'ın koştuğu komutlar — kaynaktan AST ile, metin taramasıyla değil."""
    agac = ast.parse(inspect.getsource(kapi_mod))
    out: list[list[str]] = []
    for d in ast.walk(agac):
        if not isinstance(d, ast.Tuple) or len(d.elts) != 2:
            continue
        komut, ad = d.elts
        if isinstance(komut, ast.List) and isinstance(ad, ast.Constant):
            parcalar = [e.value for e in komut.elts if isinstance(e, ast.Constant)]
            if any("lab/" in str(p) or "eval" in str(p) for p in parcalar):
                out.append([str(p) for p in parcalar] + [str(ad.value)])
    return out


def test_HER_KAPI_ADIMI_CIKIS_KODU_URETEBILIYOR():
    """🔴 Bir kapı adımı, başarısızlıkta **sıfırdan farklı** çıkış kodu üretemiyorsa
    o bir kapı değil, bir rapordur."""
    adimlar = _tam_adimlari()
    assert adimlar, "`--tam`'ın adımları AST ile bulunamadı — kapı çapası kaymış"
    for parcalar in adimlar:
        ad = parcalar[-1]
        arac = next((p for p in parcalar if p.endswith(".py")), None)
        if arac is None:                       # `python -m eval.run` gibi modül çağrıları
            continue
        kaynak = (LAB.parent / arac).read_text(encoding="utf-8")
        assert ("SystemExit" in kaynak or "sys.exit" in kaynak), (
            f"KAPI ADIMI '{ad}' ({arac}) hiçbir yolda sıfırdan farklı çıkış kodu "
            "üretmiyor — bu bir KAPI DEĞİL, bir RAPOR. `lab/kapi.py` onu yeşil sanar.")


def test_SENARYO_ADIMI_KAPI_BAYRAGIYLA_cagriliyor():
    """`--kapi` bayrağı olmadan senaryo aracı **her zaman 0** döner. Bayrağın
    düşürülmesi, kapıyı sessizce dekora çevirir — bu yüzden çağrı yeri kilitli."""
    parcalar = [p for adim in _tam_adimlari() for p in adim]
    i = [n for n, p in enumerate(parcalar) if p.endswith("konusma_senaryolari.py")]
    assert i, "senaryo adımı `--tam`'da bulunamadı"
    assert "--kapi" in parcalar, \
        "senaryo adımı `--kapi` OLMADAN çağrılıyor — her koşumda yeşil döner"


def test_TABAN_DOSYASI_IZLENEBILIR():
    """Dondurulmuş taban **commit'lenmeli**: `gitignore`'lu bir taban, her temiz
    checkout'ta *"taban yok, kapı öğrenir"* moduna düşer — yani kapı hiç koşmaz."""
    assert ks.KAPI_TABANI.name.endswith(".json")
    assert "reports" not in str(ks.KAPI_TABANI), (
        "taban `lab/reports/` altında — o dizin gitignore'lu, taban her temiz "
        "checkout'ta kaybolur ve kapı sessizce devre dışı kalır")


def test_DUSURULEN_TUR_KIRMIZI():
    """*"Sessiz kırpma yok"* kuralının doğrudan uygulanması: örneklem sınırı bir turu
    düşürdüyse ölçüm **eksiktir** ve kapı bunu yeşil sayamaz."""
    ozet = {"a": {"n": 1, "erisim": 1, "dogruluk": 1, "olculemedi": 0}}
    if not ks.KAPI_TABANI.exists():
        pytest.skip("taban henüz dondurulmamış")
    gecti, satirlar = ks.kapi_degerlendir(ozet, {"a": 3})
    assert not gecti, "DÜŞÜRÜLEN tur varken kapı yeşil verdi — sessiz kırpma yasağı ölü"
    assert any("DÜŞÜRÜLEN" in s for s in satirlar)


def test_OLCULEMEDI_GERILEME_SAYILMAZ_ama_GORUNUR():
    """`⊘` üçüncü durumdur: gerileme değildir (tabanla kıyaslanır) ama **ayrı raporlanır**
    — sessiz bir `⊘`, sahte bir ✅ kadar kötüdür."""
    if not ks.KAPI_TABANI.exists():
        pytest.skip("taban henüz dondurulmamış")
    import json

    taban = json.loads(ks.KAPI_TABANI.read_text(encoding="utf-8"))
    sinif = next(iter(taban["siniflar"]))
    b = taban["siniflar"][sinif]
    ozet = {sinif: {"n": b + 1, "erisim": b, "dogruluk": b, "olculemedi": 1}}
    gecti, satirlar = ks.kapi_degerlendir(ozet, {})
    assert gecti, "⊘ bir GERİLEME sayıldı — üçüncü durum yok sayılıyor"
    assert any("⊘" in s for s in satirlar), "⊘ raporda GÖRÜNMÜYOR (sessiz kırpma)"
