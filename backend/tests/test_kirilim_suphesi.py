"""🔴🔴 `§KD` + `§NÇ` — **BİR LİSTEYİ SORAN CÜMLEYE TEK BİR SAYI VERMEK.**

İki kusur, tek desen: sorulan şey bir **boyut**, verilen şey bir **toplam** ya da
**başka bir sorunun** cevabı. İkisi de aynı beş turluk canlı thread'de ölçüldü.

| tur | soru | sistem ne yaptı | doğrusu |
|---|---|---|---|
| 1 | *«bu yıl duruş **nedenleri**»* | tek satır **235.129 dk**, beyan yok, rozet `source=cube` | kırılım — ya da hakem |
| 3 | *«en büyük **nedeni** hangi **makinede**»* | `TUR_NEDEN` → **katkı analizi** (*«X nedeni 46.524 dk azaldı»*) | yapısal: makine kırılımı |

⊙ İkisinin kökü de Türkçenin aynı yerinde: `neden` **iki** kelimedir (soru zarfı ∧
isim) ve `nedenleri` bir **nesnedir**. Ama çözüm iki kez de bir **dil kuralı değil**,
bir **kapsam karşılaştırmasıdır** — hangi boyutların var olduğunu ve hangilerinin
raporda bulunduğunu **küp** söyler.

*Route'a dil öğretmiyoruz; route'un ne zaman emin OLMADIĞINI öğreniyoruz* (`§0.0`).
"""

from app import context as app_context
from app import followup
from app.niyet_tasima import kirilim_suphesi as suphe

_SEMA = {"cubes": [{
    "name": "makine_duruslari",
    "measures": ["toplam_sure_dk"],
    "dimensions": ["neden", "makine", "vardiya"],
    "dimension_synonyms": {"neden": ["sebep"], "makine": ["hat"]},
    "dimension_values": {"makine": ["RAM-1", "RAM-2"]},
}]}
_TOPLAM = {"cube": "makine_duruslari", "measures": ["toplam_sure_dk"],
           "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}


# --- `§KD` · ROUTE'UN KIRILIM ŞÜPHESİ ---------------------------------------------

def test_BOYUT_ADIYLA_BITEN_SORU_SUPHELIDIR():
    """🔴 **Kapının kalbi.** *«duruş nedenleri»* bir liste ister; toplam bir cevap değil."""
    assert suphe(_TOPLAM, "bu yıl duruş nedenleri", _SEMA) is True


def test_SINONIM_DE_SAYILIR():
    """Boyutun sinonimi de boyuttur — katalog neyi biliyorsa yüklem de onu bilir."""
    assert suphe(_TOPLAM, "bu yıl duruş sebepleri", _SEMA) is True


def test_ORTADA_GECEN_BOYUT_ADI_SUPHE_URETMEZ():
    """🔴🔴 **Kapının en önemli satırı (`§101.1`).**

    `musteri`/`makine` gibi adlar cümlenin **ortasında** çok geçer (*«makinesinin fire
    oranı»*) ve orada bir kırılım istenmez. Türkçede tamlamanın **başı sondadır**:
    sorulan şey en sonda durur. Konum bir dil kuralı değil, bir **yer** bilgisidir.
    """
    assert suphe(_TOPLAM, "makine duruş süresi toplamı", _SEMA) is False


def test_KIRILIM_ZATEN_VARSA_SUPHE_YOK():
    """Fişte kırılım varsa sorulan şey **zaten** verilmiştir."""
    cq = {**_TOPLAM, "dimensions": ["neden"]}
    assert suphe(cq, "bu yıl duruş nedenleri", _SEMA) is False


def test_ZAMAN_KIRILIMI_DA_BIR_KIRILIMDIR():
    """⚠ `timeDimensions` de bir kırılımdır — *«aylık duruş nedenleri»* zaten bir liste
    döndürür ve orada ikinci bir şüphe üretmek yanlış-pozitif olurdu."""
    cq = {**_TOPLAM, "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    assert suphe(cq, "aylık duruş nedenleri", _SEMA) is False


def test_SUZGECTE_TUKENEN_BOYUT_SAYILMAZ():
    """🔴 `§SR`'nin *harcanmış kanıt* ilkesi, ikinci kez: boyuta süzgeç kurulmuşsa o
    boyut **tüketilmiştir** ve bir kırılım isteği sayılamaz."""
    cq = {**_TOPLAM, "filters": [{"dimension": "makine", "operator": "eq", "value": "RAM-1"}]}
    assert suphe(cq, "duruş süresi RAM-1 makine", _SEMA) is False


def test_OLCU_ADIYLA_BITEN_SORU_SUPHELI_DEGIL():
    """`ciro`/`süresi` bir ölçüdür, boyut değil — kapı **katalogdan** okur, tahminden değil."""
    assert suphe(_TOPLAM, "bu yıl toplam duruş süresi", _SEMA) is False


def test_SEMASIZ_CAGRIDA_SUSAR():
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir* — şema yoksa şüphe yok."""
    assert suphe(_TOPLAM, "bu yıl duruş nedenleri", None) is False


# --- `§NÇ` · «NEDEN» İKİ KELİMEDİR -------------------------------------------------

def test_EKRANDA_OLMAYAN_BOYUT_YAPISALA_GIDER():
    """🔴 Ölçülen kusurun kendisi: *«hangi makinede»* yeni satırlar ister, açıklama değil."""
    niyet = followup.sinifla("en büyük nedeni hangi makinede", baglam_var=True,
                             acik_boyutlar=frozenset({"makine", "vardiya"}))
    assert niyet.sinif == followup.SINIF_YAPISAL
    assert niyet.kural == "§NÇ:ekranda-olmayan-boyut"


def test_GERCEK_NEDEN_TAKIBI_BOZULMAZ():
    """🔴🔴 **Gerçek pozitif korunur.** *«bu neden düştü»* bir boyut anmaz ve eldeki
    cevabı açıklar — bu tur `TUR_NEDEN` kalmalıdır, yoksa katkı analizi ölürdü."""
    niyet = followup.sinifla("bu neden düştü", baglam_var=True,
                             acik_boyutlar=frozenset({"makine", "vardiya"}))
    assert niyet.sinif == followup.SINIF_KONUSMA
    assert niyet.tur == followup.TUR_NEDEN


def test_ACIK_BOYUT_YOKSA_DAVRANIS_BIREBIR_AYNI():
    """`KURAL B`: yeni argüman verilmezse yol birebir bugünküdür."""
    niyet = followup.sinifla("bu neden düştü", baglam_var=True)
    assert niyet.sinif == followup.SINIF_KONUSMA and niyet.tur == followup.TUR_NEDEN


def test_ACIK_BOYUTLAR_FISTEKILERI_ELER():
    """`context.acik_boyutlar` yalnız **eksik** olanları verir — raporda bulunan bir
    boyutun anılması gerçek bir açıklama isteğidir ve bozulmamalıdır."""
    cq = {"cube": "makine_duruslari", "dimensions": ["makine"]}
    acik = app_context.acik_boyutlar(cq, _SEMA)
    assert acik is not None
    assert "makine" not in acik and "neden" in acik


def test_ACIK_BOYUTLAR_KUPSUZ_CAGRIDA_SUSAR():
    """Rapor yoksa *«ekranda ne yok»* sorusu tanımsızdır — `capa_degerleri` ile aynı sınır."""
    assert app_context.acik_boyutlar(None, _SEMA) is None
    assert app_context.acik_boyutlar({"cube": "yok"}, _SEMA) is None


# --- `§NÇ` DARALTILDI · işaret zarfı belirsizliği kaldırır ---------------------------

def test_NEDEN_BOYLE_YAPISALA_SURUKLENMEZ():
    """🔴🔴 **Canlıda ölçülen kusur (2026-08-11).** *«bu yıl makine bazında duruş
    dakika»* → *«**neden böyle**»* → **66 satırlık tablo**, not YOK.

    `§NÇ` doğru çalışıyordu: `makine_duruslari`'nda `neden` **raporda bulunmayan** bir
    boyuttur, dolayısıyla tur *yapısal* sayıldı ve *«nedene göre kır»* diye okundu.

    🔴 Ama *«neden **böyle**»*'deki `böyle` bir **işaret zarfıdır** ve ekrandaki cevaba
    işaret eder — orada belirsizlik **yoktur**. Kuralın kendi cümlesi de bunu söylüyor:
    *«bir cevabın üstünde konuşmak, o cevabın içinde olan şeyler hakkında konuşmaktır»*.

    *Bir belirsizlik kuralını, belirsizliğin ortadan kalktığı yerde de uygulamak, kuralı
    değil alışkanlığı sürdürmektir.*"""
    from app import followup

    n = followup.sinifla("neden böyle", baglam_var=True,
                         acik_boyutlar=frozenset({"makine", "neden"}))
    assert n.sinif == followup.SINIF_KONUSMA and n.tur == followup.TUR_NEDEN


def test_ISARETSIZ_NEDEN_HALA_YAPISAL():
    """🔴 **Daraltma fazla ileri gitmemeli.** `§NÇ`'nin var olma sebebi duruyor:
    *«en büyük nedeni hangi makinede»* bir **isim** kullanımıdır, işaret zarfı yoktur ve
    ekranda olmayan bir boyutu anar → yapısal kalır."""
    from app import followup

    n = followup.sinifla("en büyük nedeni hangi makinede", baglam_var=True,
                         acik_boyutlar=frozenset({"neden"}))
    assert n.sinif == followup.SINIF_YAPISAL and n.kural == "§NÇ:ekranda-olmayan-boyut"


def test_ISARET_ZARFI_KAPALI_SINIF():
    """🔴 `ADR-0008` — işaret zarfları dilbilgisinin **kapalı** bir sınıfıdır, bir alan
    sözlüğü değil. *Bir yüklem alan kelimesi taşımaya başladığında, o bir yüklem değil
    bir sözlüktür.*"""
    from app import followup

    kalip = followup._ISARET_ZARFI.pattern
    for alan in ("fire", "duruş", "makine", "ciro", "oee"):
        assert alan not in kalip


# --- `§KD-boyut` · İSTENEN KIRILIM YERİNE BAŞKASI GELDİYSE SÖYLENİR ------------------

_SEMA_KD = {"cubes": [
    {"name": "egitim", "dimensions": ["departman", "personel_kodu", "sonuc"],
     "dimension_synonyms": {"sonuc": ["sonuç", "sonuc"], "departman": ["departman"]},
     "dimension_labels": {"sonuc": "sonuç"}},
    {"name": "bakim_is_emri", "dimensions": ["tur", "makine"],
     "dimension_synonyms": {"tur": ["tür", "tur"], "makine": ["makine"]},
     "dimension_labels": {"tur": "tür"}},
]}


def test_KD_BOYUT_IKAMESI_BEYAN_EDILIR():
    """🔴🔴 **Ölçülen kusur (curl `BB` turu).** *«bu yıl eğitim türüne göre katılım»* →
    `egitim` küpü, kırılım **`sonuc`** (BAŞARILI/BAŞARISIZ), beyan **YOK**. `egitim`'de
    bir *tür* boyutu yok ve garson en yakınını seçti: sayı doğru ama kullanıcı **tür**
    kırılımı istedi, **sonuç** kırılımı aldı.

    Mevcut `kirilim` beyanı bunu göremez — o yalnız *hiç boyut taşınamadı* hâlini sayar.

    *Bir kırılımı sessizce başkasıyla değiştirmek, sorulmayan bir soruyu cevaplamaktır.*"""
    from app import uyum

    out = uyum._kirilim_ikamesi("bu yil egitim turune gore katilim",
                                {"cube": "egitim", "dimensions": ["sonuc"]},
                                _SEMA_KD["cubes"][0], _SEMA_KD)
    assert out is not None
    terim, sahipler = out
    assert "tür" in terim and "bakim_is_emri" in sahipler


def test_KD_ISTENEN_KIRILIM_VARSA_SUSAR():
    """🔴🔴 **Yanlış-pozitif kapısı** (`§101.1`). Ölçüldü: on vakalık sınamada **10/10**
    doğru — *«araç türüne göre»* bile susuyor çünkü `arac_turu` cevapta **zaten var**."""
    from app import uyum

    assert uyum._kirilim_ikamesi("bu yil makine bazinda is emri",
                                 {"cube": "bakim_is_emri", "dimensions": ["makine"]},
                                 _SEMA_KD["cubes"][1], _SEMA_KD) is None


def test_KD_BOYUTSUZ_CEVAPTA_KONUSMAZ():
    """⚠ Boyutsuz cevaplarda **hiç konuşmaz**: orası `kirilim` beyanının işidir ve aynı
    şeyi iki kez söylemek iki ayrı kusur varmış gibi görünürdü."""
    from app import uyum

    assert uyum._kirilim_ikamesi("bu yil egitim turune gore katilim",
                                 {"cube": "egitim", "dimensions": []},
                                 _SEMA_KD["cubes"][0], _SEMA_KD) is None


def test_KD_ONCE_HEPSINI_TOPLAR():
    """🔴🔴 **Canlı ölçüm, çevrimdışı prob'un kaçırdığını yakaladı.** İlk yazımda ilk
    eşleşen küpte **dönülüyordu**: *«araç türüne göre nakliye maliyeti»* → cevap
    `arac_turu` kırılımında (**doğru**) ama beyan *«tür bu küpte tanımlı değil»* dedi —
    döngü `sevkiyat`a gelmeden `bakim_is_emri.tur`'u bulup dönmüştü.

    ⚠ Çevrimdışı prob bunu **kaçırmıştı**: orada küp sırası farklıydı.
    *Sıraya bağlı bir yüklem, sırası değişen her yerde başka bir şey söyler.*"""
    from app import uyum

    sema = {"cubes": [
        {"name": "bakim_is_emri", "dimensions": ["tur"],
         "dimension_synonyms": {"tur": ["tür", "tur"]},
         "dimension_labels": {"tur": "tür"}},
        {"name": "sevkiyat", "dimensions": ["arac_turu"],
         "dimension_synonyms": {"arac_turu": ["arac turu", "araç türü"]},
         "dimension_labels": {"arac_turu": "araç türü"}},
    ]}
    out = uyum._kirilim_ikamesi("bu yil arac turune gore nakliye maliyeti",
                                {"cube": "sevkiyat", "dimensions": ["arac_turu"]},
                                sema["cubes"][1], sema)
    assert out is None, f"🔴 doğru kırılımda yanlış-pozitif: {out}"


def test_KD_KIRILIM_ISTENMEDIYSE_SUSAR():
    """🔴🔴 **`§KD-boyut`'un İKİ CANLI YANLIŞ-POZİTİFİ** (curl `CC` turu, CC-20/CC-21):

        «son 2 yıl **satış** raporu hazırla» → «satış» ⊂ «satış temsilcisi» → beyan konuştu
        «bir de fire oranı **bölüm**ü ekle»  → «bölüm» = *raporun bölümü* → beyan konuştu

    İkisinde de kullanıcı bir **kırılım istemedi**. İlk yüklem *«soruda bir boyut adı
    geçiyor»*du — ama bir boyut adının cümlede bulunması, o kırılımın **istendiğine**
    dair bir kanıt değildir: biri çok-sözcüklü bir etiketin parçası, öteki **belgenin
    kendi yapı adı**. `§101.1`: yanlış pozitif kusurun kendisinden pahalıdır.

    ⚠ Ayrım **yeniden yazılmadı, çağrıldı** (`kirilim_istendi`, `niyet.py:311`) — bu
    depoda `göre`/`bazında` aşırı-yüklenmesi üç kez ısırdı."""
    from app import uyum

    sema = {"cubes": [
        {"name": "parti", "dimensions": ["musteri", "satis_temsilcisi"],
         "dimension_synonyms": {"satis_temsilcisi": ["satis temsilcisi", "satis"],
                                "musteri": ["musteri"]},
         "dimension_labels": {"satis_temsilcisi": "satış temsilcisi"}},
        {"name": "bakim", "dimensions": ["bolum"],
         "dimension_synonyms": {"bolum": ["bolum", "bölüm"]},
         "dimension_labels": {"bolum": "bölüm"}},
    ]}
    for soru in ("son 2 yil satis raporu hazirla",
                 "bir de fire orani bolumu ekle"):
        out = uyum._kirilim_ikamesi(soru, {"cube": "parti", "dimensions": ["musteri"]},
                                    sema["cubes"][0], sema)
        assert out is None, f"🔴 kırılım istenmemişken beyan konuştu ({soru}): {out}"


def test_KD_ISARET_VARSA_HALA_KONUSUR():
    """Daraltma **doğru-pozitifi öldürmemeli**: `BB` turunun ölçülen vakası işaret
    (*«türüne **göre**»*) taşır ve beyan aynen konuşur.

    *Bir yüklemi daraltmak, onu susturmak değildir — sınırını çizmektir.*"""
    from app import uyum

    sema = {"cubes": [
        {"name": "egitim", "dimensions": ["sonuc", "departman"],
         "dimension_synonyms": {"sonuc": ["sonuc"]}, "dimension_labels": {}},
        {"name": "bakim_is_emri", "dimensions": ["tur"],
         "dimension_synonyms": {"tur": ["tur", "tür"]},
         "dimension_labels": {"tur": "tür"}},
    ]}
    out = uyum._kirilim_ikamesi("bu yil egitim turune gore katilim",
                                {"cube": "egitim", "dimensions": ["sonuc"]},
                                sema["cubes"][0], sema)
    assert out is not None and out[0] == "tür", f"🔴 doğru-pozitif kayboldu: {out}"
