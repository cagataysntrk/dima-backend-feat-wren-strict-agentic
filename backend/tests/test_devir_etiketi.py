"""🔴🔴 `A3`/`A4`/`A5` — **DEVİR BİR GERİLEME DEĞİLDİR** ve kapı bunu kendi söyler.

## Ölçülen kusur — kullanıcının teşhisi, harfiyen

> *"Kapı sadece route'u koruyor; oysa asıl hakem garson. route sessiz yanlışlar
> yapıyor, bunlar garsona geçmesi lazımdı — bunlar geçse corpus tabii ki gerileyecek."*

`_ozet` beş sınıfın **üçünü** sayıyordu; `netlestirme` ve `durust_ret` yalnız toplu
`kabul` içinde görünüyordu. Sonuç: route bir sessiz-yanlışı bırakıp garsona çekildiğinde
kapının söyleyebildiği tek cümle *"düştü"* oluyordu — ve bir kez (rapor `G3`) sağlam bir
değişikliğin **geri alınmasına** yol açtı.

⊙ Yani gerilemenin kendisi bir **ölçüm artefaktıydı**: sayılmayan bir sınıf, olmayan bir
sınıf gibi davranır — ve onun yönüne yapılan her iyileştirme kırmızı verir.
"""

from __future__ import annotations

from lab.gercek_dunya import (
    DOGRU,
    SESSIZ_YANLIS,
    _degisim_listesi,
    _degisim_sinifi,
)

_TABAN = {"vaka": 100, "kabul": 90, "dogru": 80, "sessiz_yanlis": 10,
          "beyanli_kismi": 2, "netlestirme": 5, "devir": 5}


def _ile(**fark):
    return {**_TABAN, **fark}


def test_SESSIZ_YANLIS_DEVRE_DONUSTU_KAZANCTIR():
    """🔴 Kullanıcının istediği **tam** hareket: route çekilir, garson devralır."""
    sinif, gerekce = _degisim_sinifi(_TABAN, _ile(sessiz_yanlis=6, devir=9))
    assert sinif == "KAZANC", gerekce
    assert "garson" in gerekce


def test_DOGRU_DUSTU_AMA_DEVIR_KARSILADI_GERILEME_DEGIL():
    """⚠ `dogru → devir`: cevap hâlâ geliyor. Kapı geçirir **ama fiyatını yazar**."""
    sinif, gerekce = _degisim_sinifi(_TABAN, _ile(dogru=75, devir=10))
    assert sinif == "DEVIR", gerekce
    assert "LLM turu" in gerekce, "devir bedava sanılmamalı — fiyatı basılmalı"


def test_DOGRU_KARSILIKSIZ_KAYBOLDU_GERILEMEDIR():
    """🔴 Devir yoksa bu bir devir değil, **yetenek kaybıdır**."""
    sinif, gerekce = _degisim_sinifi(_TABAN, _ile(dogru=75))
    assert sinif == "GERILEME", gerekce
    assert "karşılıksız" in gerekce


def test_SESSIZ_YANLIS_ARTISI_HER_SEYI_EZER():
    """🔴 En ağır sınıf: devir de artmış olsa gerileme kararı değişmez."""
    sinif, _ = _degisim_sinifi(_TABAN, _ile(sessiz_yanlis=12, devir=20, dogru=85))
    assert sinif == "GERILEME"


def test_ESKI_TABAN_ETIKET_UYDURMAZ():
    """🔴 Eksik veriden etiket üretmek, ölçmediğini bilmemekten kötüdür."""
    sinif, gerekce = _degisim_sinifi({"dogru": 80, "sessiz_yanlis": 10}, _TABAN)
    assert sinif == "BILINMIYOR" and "KOŞULMADI" in gerekce


def test_A5_DEGISIM_LISTESI_IKI_YONU_DE_GOSTERIR():
    """🔴 *"Düştü"* bir şikâyettir; ölçüm **hangi soruların** düştüğünü söyler."""
    satir = _degisim_listesi({"a": SESSIZ_YANLIS, "b": "devir"},
                             {"b": "devir", "c": SESSIZ_YANLIS})
    metin = "\n".join(satir)
    assert f"`a` · {SESSIZ_YANLIS} → {DOGRU}" in metin, "kırmızı→yeşil görünmeli"
    assert f"`c` · {DOGRU} → {SESSIZ_YANLIS}" in metin, "yeşil→kırmızı görünmeli"
    assert "`b`" not in metin, "değişmeyen satır listeye girmemeli"


def test_A5_KIRPMA_SESSIZ_OLAMAZ():
    """🔴 Raporun kendi kuralı: sessiz kırpma, *«hepsini kapsadım»* diye okunur."""
    satir = _degisim_listesi({}, {f"s{i}": SESSIZ_YANLIS for i in range(40)}, tavan=5)
    assert len(satir) == 6 and "35 değişim daha" in satir[-1]
