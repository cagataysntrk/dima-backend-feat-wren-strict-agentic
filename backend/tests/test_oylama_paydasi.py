"""🔴🔴 `D2`/`F2` — **ÇEKİMSERLER PAYDAYA GİRER**: kalibrasyon yalanının aritmetiği.

Rapor `F2`: *"1 cevap + 2 «bilmiyorum» → uyum **%100** görünüyor. Kendi kaydının
cümlesi: **şüphenin en yüksek olduğu durum EN EMİN görünür**."*

## Aritmetik — ve neden bu bir yalan

`ask.py`: `agreement = len(best) / (len(oylar) if _tam_payda else len(cands))`

* `oylar` — **bütün** oylar, `{"cube": null}` çekimserleri dâhil
* `cands` — yalnız **cevap veren** oylar

Üç çağrının biri cevap, ikisi *«bu soru tek cube ile yanıtlanamaz»* dediğinde:

| payda | uyum | ne söylüyor |
|---|---|---|
| `cands` (bugün) | `1/1` = **%100** | *«oy birliği»* 🔴 |
| `oylar` (bayrak) | `1/3` = **%33** | *«iki oy çekimser»* ✅ |

⊙ Çekimser bir **bilgidir**, gürültü değil: `{"cube": null}` *"bu soru tek bir cube ile
yanıtlanamaz"* demektir. Onu paydadan düşürmek, **hayır oylarını saymadan oy birliği
ilan etmektir**.

⚠ `MIMARI`'nin açık kararı bunu yasaklıyor: *"kalibre edilmediği sürece o sayı bir
güven değil bir **SÜSTÜR**."*

## Neden korpus bunu ölçemez — ve ölçebilecek şey ne

`nl_corpus` tanımı gereği `rule` sağlayıcıyla koşar: **hiç LLM yoktur**, dolayısıyla
oylama yolu orada **hiç çalışmaz**. Bu bayrağın kazancı/bedeli ancak **tam `/ask`
yolundan** ölçülebilir — yani `A2` kasetli garson korpusundan. *Bir mekanizmayı,
koşmadığı bir korpusla yargılamak, sessizliği bir cevap sanmaktır.*
"""

from __future__ import annotations


def _uyum(kazanan: int, cevap_veren: int, cekimser: int, tam_payda: bool) -> float:
    """`ask.py`'deki hesabın **birebir** aynası — ikinci bir formül DEĞİL, bir aynadır.

    ⚠ Buraya bir kopya yazmak iki sahip yaratırdı; bu fonksiyon yalnız **kapının
    okuyabildiği** biçimde aynı aritmetiği ifade eder ve `test_AYNA_KAYMADI` onu
    kaynağa karşı sınar.
    """
    return kazanan / ((cevap_veren + cekimser) if tam_payda else cevap_veren)


def test_KALIBRASYON_YALANI_VAR():
    """🔴 Bugünkü hesap: **1 cevap + 2 çekimser → %100**.

    *Şüphenin en yüksek olduğu durum, sistemin en emin göründüğü durumdur.*
    """
    assert _uyum(1, 1, 2, tam_payda=False) == 1.0


def test_BAYRAK_YALANI_KAPATIR():
    """✅ Çekimser paydaya girince aynı durum **%33** — ve `2/3` eşiğinin altında,
    yani netleştirmeye düşer."""
    assert abs(_uyum(1, 1, 2, tam_payda=True) - 1 / 3) < 1e-9
    assert _uyum(1, 1, 2, tam_payda=True) < 2 / 3


def test_CEKIMSER_YOKKEN_IKI_HESAP_AYNIDIR():
    """🔴 `KURAL B`'nin aritmetik karşılığı: çekimser yoksa bayrak **hiçbir şey
    değiştirmez**. Bir bayrağın bedeli, ancak dokunduğu vakada doğar."""
    for kazanan, cevap in ((3, 3), (2, 3), (1, 2)):
        assert _uyum(kazanan, cevap, 0, False) == _uyum(kazanan, cevap, 0, True)


def test_AYNA_KAYMADI():
    """⚠ Kaynak formül değişirse bu kapı **sessizce yanlış** ölçmeye başlardı.

    *Bir aynayı, yansıttığı şeyden bağımsız tutmak; onu bir gün yalancı yapar.*
    """
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1] /
              "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    assert "agreement = len(best) / (len(oylar) if _tam_payda else len(cands))" in kaynak, (
        "oylama payda formülü değişmiş — bu kapının aynası güncellenmeli, yoksa "
        "kalibrasyon yalanını ölçtüğünü SANARAK başka bir şey ölçer")
