"""🔴🔴 `§DK-3` — **ROUTE İLE GARSON AYNI MENÜYE BAKAR.**

`§DK` kataloğun enum'unu düzeltti. Ama route değerleri oradan **okumuyordu**: kendi
eşleşmesini `schema["models"][*]["columns"]`'dan, yani **ham model kolonlarından boyut
ADIYLA** yapıyordu. Yani aynı kusurun **ikinci kopyası** route'un içindeydi.

| boyut | route'un baktığı | küpün gerçeği (derleyicinin kullandığı) |
|---|---|---|
| `vardiya` | 🔴 kolon **hiç yok** → süzgeç yapısal olarak imkânsız | `1. Vardiya (08-16)` |
| `musteri` | `M1001…` (kullanıcının asla yazmadığı kod) | `AKDENİZ ÖRME TEKSTİL A.Ş.` |

⊙ Canlı bedeli: *«bu yıl **1. vardiyada** fire oranı»* → üç vardiya birden, ilk satır
*«3. Vardiya»*, süzgeç sessizce düştü, **beyan yok**.

*İki basamağın farklı menülere bakması bir tutarsızlık değil, iki ayrı üründür.*
"""

from app import cube_router as cr

#: Küpün gerçeği: görünen etiketler. Ham kolonda `vardiya` diye bir şey **yok** —
#: canlıdaki durumun birebir küçüğü.
_CUBE = {
    "name": "parti",
    "dimensions": ["vardiya", "musteri", "makine"],
    "dimension_values": {
        "vardiya": ["1. Vardiya (08-16)", "2. Vardiya (16-24)", "3. Vardiya (00-08)"],
        "musteri": ["AKDENİZ ÖRME TEKSTİL A.Ş.", "EGE KNIT DIŞ TİCARET LTD. ŞTİ."],
        "makine": ["RAM-1", "RAM 2"],
    },
}
#: Route'un ESKİDEN tek baktığı yer — ve yalanı buradan alıyordu.
_COLS = {"musteri": {"values": ["M1001", "M1002"]}}


def _deg(dname):
    return cr.boyut_degerleri(_CUBE, _COLS, dname)


def test_KUPUN_ENUMU_HAM_KOLONU_EZER():
    """🔴 Kapının kalbi: `musteri` için kod değil **ad** okunur."""
    assert _deg("musteri")[0].startswith("AKDENİZ")
    assert "M1001" not in _deg("musteri")


def test_KUPTE_KAYIT_YOKSA_HAM_KOLON_YEDEKTIR():
    """⚠ Düzeltme bir **kırpma** değil: küpün kaydı hiç yoksa bugünkü davranış korunur.
    *Bir kaynağı düzeltmek, öteki kaynağı silmek zorunda değildir.*"""
    bos = {"name": "x", "dimensions": ["musteri"], "dimension_values": {}}
    assert cr.boyut_degerleri(bos, _COLS, "musteri") == ["M1001", "M1002"]


def test_GORUNEN_ETIKETIN_CEKIRDEGI_ESLESIR():
    """🔴 Ölçülen sessiz yanlışın kendisi: kullanıcı `«1. vardiya»` yazar, katalog
    `«1. Vardiya (08-16)»` tutar."""
    q = cr._norm("bu yıl 1. vardiyada fire oranı")
    assert cr.deger_eslesmeleri(q, _deg("vardiya")) == ["1. Vardiya (08-16)"]


def test_CEKIRDEK_YOLU_BELIRSIZLIKTE_SUSAR():
    """🔴🔴 **Kapının kendi riski.** `«ram»` hem `RAM-1` hem `RAM 2`'yi çağırır; orada
    seçim yapmak yazı-turadır. *Belirsizlikte tahmin etmemek bu deponun tek kuralıdır
    ve çekirdek eşleşmesi onun istisnası olamaz.*"""
    q = cr._norm("ram makinesinin fire oranı")
    assert cr.deger_eslesmeleri(q, _deg("makine")) == []


def test_TAM_ESLESME_CEKIRDEGI_ONCELER():
    """Tam eşleşme varken çekirdeğe hiç bakılmaz — gevşek kural sıkı kuralı ezemez."""
    q = cr._norm("ram-1 makinesinin fire orani")
    assert cr.deger_eslesmeleri(q, _deg("makine")) == ["RAM-1"]


def test_SIRKET_ADI_KUYRUGU_KIRPILMAZ():
    """⚠ `LTD. ŞTİ.` bir **açıklama değil adın parçasıdır**; yalnız sondaki PARANTEZ
    atılır. Kuralı genişletmek onu belirsizleştirirdi."""
    assert cr._deger_cekirdegi(cr._norm("EGE KNIT DIŞ TİCARET LTD. ŞTİ.")) is None
    assert cr._deger_cekirdegi(cr._norm("1. Vardiya (08-16)")) == "1. vardiya"


def test_ALAKASIZ_SORU_DEGER_UYDURMAZ():
    """Değer geçmeyen bir soruda hiçbir süzgeç doğmaz — `§V5`'in kuralı korunuyor."""
    q = cr._norm("bu yil toplam ciro")
    for d in ("vardiya", "musteri", "makine"):
        assert cr.deger_eslesmeleri(q, _deg(d)) == [], d
