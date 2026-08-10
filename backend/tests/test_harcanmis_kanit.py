"""🔴🔴 `§SR` + `§KB` — **BİR KANIT İKİ KEZ SAYILAMAZ; VE BİR CEVAP KENDİ TESLİMATINDAN
SORULUR.**

İki kusur, tek ilke. `KAT-1` *«bir kuralın iki sahibi olmaz»* der; bu turda ölçülen şey
onun **çalışma-zamanı ikizidir**: aynı kanıtın iki tüketicisi.

| # | ölçülen soru | cevap | beyan |
|---|---|---|---|
| `§SR` | *«RAM-1 makinesinin bu yıl toplam duruş süresi»* | ✅ 41.104 dk | 🔴 *«**1** dedin ama listeyi o sayıya kesemedim»* |
| `§KB` | *«bir de oee ekle»* (harman) | ✅ satırlarda `ort_oee` **var** | 🔴 *«soruda «oee» geçiyor ama bu cevap onu **içermiyor**»* |

⊙ İkisinde de cevap **doğru**, beyan **yanlış**. `§101.1`: kusur bazen olur,
yanlış-pozitif **her seferinde** yanlıştır — ve doğru bir cevaba *«eksik»* demek tüm
beyanların güvenini aşındırır.
"""

from app import uyum
from app.uyum import _ustunluk_harcandi as harcandi

# --- `§SR` · HARCANMIŞ RAKAM -------------------------------------------------------

_IC = {"cube": "oee", "measures": ["toplam_durus_dakika"],
       "filters": [{"dimension": "makine", "operator": "eq", "value": "RAM-1"},
                   {"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}


def test_DEGER_SUZGECINE_GIREN_RAKAM_TUKENMISTIR():
    """🔴 **Kapının kalbi.** `RAM-1` içindeki **1**, bir makine adının parçasıdır."""
    qn = "ram-1 makinesinin bu yil toplam durus suresi"
    assert harcandi(qn, _IC, 1) is True


def test_SERBEST_GECEN_RAKAM_TUKENMEMISTIR():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    Sayı bir yerde bile süzgeç dışında geçiyorsa **gerçek** bir üstünlük sayısı olabilir.
    Tüketilmişliği *her* geçtiği yerde kanıtlamak gerekir; birini kanıtlayıp ötekini
    varsaymak, kapıyı bir tahmine çevirirdi."""
    qn = "ram-1 makinesinin en kotu 1 ayi"
    assert harcandi(qn, _IC, 1) is False


def test_SUZGECSIZ_SORUDA_ETKI_YOK():
    """`KURAL B`: süzgeç yoksa hiçbir şey tükenmez, beyan aynen yazılır."""
    assert harcandi("en yuksek 3 makine", {"cube": "oee", "filters": []}, 3) is False


def test_SAYI_ICERMEYEN_DEGER_ARALIK_URETMEZ():
    """⚠ Süzgeç değeri sayıyı **içermiyorsa** bir aralık değildir — yoksa alakasız bir
    süzgeç her sayıyı tüketirdi."""
    ic = {"filters": [{"dimension": "makine", "operator": "eq", "value": "SANTEX"}]}
    assert harcandi("en yuksek 3 makine", ic, 3) is False


def test_SIRALI_OPERATOR_KANIT_SAYILMAZ():
    """⚠ Yalnız **kimlik** operatörleri bir değeri adlandırır; `gte "2026-01-01"` bir
    tarih sınırıdır, bir varlık adı değil."""
    ic = {"filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    assert harcandi("2026 yilinin en kotu 1 ayi", ic, 1) is False


def test_LISTE_DEGERINDE_DE_TUKENIR():
    """`in [RAM-1, RAM-2]` de bir adlandırmadır — `§ÇE` birleştirmesinden sonra bu yol
    canlıda **normal** hâle geliyor."""
    ic = {"filters": [{"dimension": "makine", "operator": "in", "value": ["RAM-1", "RAM-2"]}]}
    assert harcandi("ram-1 ve ram-2 fire", ic, 1) is True


# --- `§KB` · HARMANIN TESLİMATI ----------------------------------------------------

_SEMA = {"cubes": [
    {"name": "parti", "display": "parti", "synonyms": ["parti"],
     "measure_synonyms": {"toplam_fire_kg": ["fire", "toplam fire"]},
     "dimension_synonyms": {"makine": ["makine"]},
     "measures": ["toplam_fire_kg"], "dimensions": ["makine"]},
    {"name": "oee", "display": "oee", "synonyms": ["oee"],
     "measure_synonyms": {"ort_oee": ["oee", "ortalama oee"]},
     "dimension_synonyms": {"makine": ["makine"]},
     "measures": ["ort_oee"], "dimensions": ["makine"]},
]}
_PARTI = _SEMA["cubes"][0]


def test_HARMAN_OLCUSU_ICERILMIS_SAYILIR():
    """🔴 Ölçülen yalan beyanın kendisi: `ort_oee` satırlarda **vardı**."""
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["makine"],
          "blend": [{"cube": "oee", "measures": ["ort_oee"]}]}
    assert uyum._capraz_kup_ikamesi("bir de oee ekle", cq, _PARTI, _SEMA) is None


def test_HARMANSIZ_IKAME_HALA_BEYAN_EDILIR():
    """🔴🔴 **Gerçek pozitif korunur.** Harman yoksa `oee` gerçekten cevapta değildir ve
    `§Cİ`'nin beyanı aynen yazılmalıdır — *bir yanlış-pozitifi kapatırken gerçek
    pozitifi kapatmak, kapıyı dekora çevirir.*"""
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["makine"]}
    sonuc = uyum._capraz_kup_ikamesi("bir de oee ekle", cq, _PARTI, _SEMA)
    assert sonuc is not None and sonuc[0] in ("oee", "ortalama oee")


def test_HARMAN_KUPU_YABANCI_SAYILMAZ():
    """⚠ Harmana katılan cube, cevabın küpü kadar **cevabın içindedir**; onu «başka küp»
    sayan bir döngü kendi teslimatını yabancı ilan eder."""
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"],
          "blend": [{"cube": "oee", "measures": []}]}
    assert uyum._capraz_kup_ikamesi("ortalama oee", cq, _PARTI, _SEMA) is None
