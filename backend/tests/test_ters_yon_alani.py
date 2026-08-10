"""🔴🔴 `C1`+`C3` — **TERS YÖN: sistem sözlüğünü KULLANIMDAN yazar, elle değil.**

Kullanıcı kararı: *"tek tek sinonim yazmak mesela aptallık."* Doğru kök, kullanıcının
kendi cümlesiyle: garson `zayiat → toplam_fire_kg` eşlemesini **zaten yapıyor**; ondan
istenen tek şey onu **söylemesi**. Ek LLM çağrısı **sıfır**.

Ve sorunun **biçimi** de bir karardır (`C1`, kullanıcı: *"katalogdaki kelimelerden
birinin eş anlamlısı var mı diye bakacak — nokta atışı"*):

| | ❌ açık üretim | ✅ **kapalı seçim** |
|---|---|---|
| çıktı | serbest **metin** | katalogdan **bir ad** ya da **hiçbiri** |
| doğrulanabilir mi | 🔴 hayır | ✅ evet — beyaz listede **deterministik** |

Bu dosya iki şeyi kilitler ve ikincisi birincisinden önemlidir:
1. eşleme **okunur ve sınanır**
2. eşleme bir **kimlik değil makbuzdur** → oyu **bölemez**
"""

import json

from app import cube_router as cr
from app.routers.ask import _canon_cq

_INDEX = {
    "parti": {"measures": ["toplam_fire_kg", "toplam_ciro"],
              "dimensions": ["hat", "musteri"]},
}


def _ham(**ek):
    return json.dumps({"cube": "parti", "measures": ["toplam_fire_kg"], **ek},
                      ensure_ascii=False)


def test_KAPALI_SECIM_OKUNUR():
    """Kullanıcının sözü + katalogdan **TAM** ad → eşleme geçerli."""
    t = cr.eslesen_terim_oku(
        _ham(eslesen_terim={"kullanicinin_sozu": "zayiat",
                            "katalog_adi": "toplam_fire_kg"}), _INDEX, "parti")
    assert t == {"soz": "zayiat", "ad": "toplam_fire_kg"}


def test_UYDURULMUS_AD_REDDEDILIR():
    """🔴 **Kapının kalbi.** Model bir ad **seçebilir, uyduramaz** — kapalı seçimin
    tamamı bu satırdır. Açık üretimde bu doğrulama **mümkün değildi**."""
    assert cr.eslesen_terim_oku(
        _ham(eslesen_terim={"kullanicinin_sozu": "zayiat",
                            "katalog_adi": "toplam_zayiat_kg"}), _INDEX, "parti") is None


def test_BOYUT_ADI_DA_GECERLIDIR():
    """Ters yön yalnız ölçüler için değil: *«müşteri»* de bir eşleme hedefidir."""
    t = cr.eslesen_terim_oku(
        _ham(eslesen_terim={"kullanicinin_sozu": "alici", "katalog_adi": "musteri"}),
        _INDEX, "parti")
    assert t and t["ad"] == "musteri"


def test_ALAN_YOKSA_SESSIZ():
    """*«Hiçbiri»* de bir cevaptır ve **alanı hiç yazmamak** onun biçimidir."""
    assert cr.eslesen_terim_oku(_ham(), _INDEX, "parti") is None


def test_BOZUK_GIRDI_TURU_DUSURMEZ():
    """Model bozuk JSON ya da yanlış tip üretirse tur **düşmez** — bu bir makbuz alanı;
    bir makbuzun okunamaması cevabı geçersiz kılmaz."""
    for kotu in ("{bozuk", "[]", json.dumps({"cube": "parti", "eslesen_terim": "metin"})):
        assert cr.eslesen_terim_oku(kotu, _INDEX, "parti") is None
    assert cr.eslesen_terim_oku(
        _ham(eslesen_terim={"kullanicinin_sozu": "ab",           # <3 harf
                            "katalog_adi": "toplam_fire_kg"}), _INDEX, "parti") is None


def test_BILINMEYEN_KUP_ICIN_YARGI_YOK():
    """Küp beyaz listede yoksa hedef ad da sınanamaz → eşleme **kabul edilmez**."""
    assert cr.eslesen_terim_oku(
        json.dumps({"cube": "yok", "eslesen_terim": {"kullanicinin_sozu": "zayiat",
                                                     "katalog_adi": "toplam_fire_kg"}}),
        _INDEX, "yok") is None


# ── 🔴🔴 İKİNCİ KİLİT: MAKBUZ, KİMLİK DEĞİLDİR ────────────────────────────────

def test_TASIYICI_OYU_BOLMEZ():
    """🔴🔴 **Bu kapının en önemli satırı.**

    Eşleme örnekten örneğe **değişir** (modelin hangi sözü rapor edeceği onun tercihi).
    Taşıyıcı kimlikten sayılsaydı üç örnek üç ayrı kovaya düşer, uyum oranı düşer ve
    **doğru bir cevap netleştirmeye çevrilirdi** — yani bir makbuz alanı, cevabı bozardı.

    *Bir kimliği tanımlarken neyin kimlik OLMADIĞINI da söylemek gerekir.*
    """
    taban = {"cube": "parti", "measures": ["toplam_fire_kg"]}
    a = {**taban, cr.TERIM_TASIYICI: {"soz": "zayiat", "ad": "toplam_fire_kg"}}
    b = {**taban, cr.TERIM_TASIYICI: {"soz": "kayip", "ad": "toplam_fire_kg"}}
    assert _canon_cq(a) == _canon_cq(b) == _canon_cq(taban)


def test_ALT_CIZGI_KURALI_GENELDIR():
    """⚠ Kural `_eslesen_terim`'e özel değil: **her** alt çizgili alan bir taşıyıcıdır.
    Depo bunu zaten yapıyordu (`donem_capasi._TASIYICI = "_capa_notu"`) ama kural yazılı
    değildi — *yazılı olmayan bir konvansiyon, ona uymayan satır yazılana kadar çalışır.*
    """
    taban = {"cube": "parti", "measures": ["toplam_fire_kg"]}
    assert _canon_cq({**taban, "_capa_notu": ("metin", "iz")}) == _canon_cq(taban)


def test_GERCEK_ALAN_HALA_KIMLIKTIR():
    """⚠ Kapı fazla ileri gitmemeli: alt çizgisiz **her** alan kimliğin parçası kalır."""
    taban = {"cube": "parti", "measures": ["toplam_fire_kg"]}
    assert _canon_cq({**taban, "dimensions": ["hat"]}) != _canon_cq(taban)


def test_IZ_ONEKI_SABITTIR():
    """`lab/sinonim_hasadi.py` bu dizeyi `interaction_log.trace_json` içinde arar.
    *Bir izi makine okuyacaksa o iz bir biçimdir; biçimi değiştirmek okuyucuyu kırar.*"""
    assert cr.TERIM_IZ_ONEKI == "ters-yön eşlemesi: "


# ── 🔴🔴 `C3-D`: EŞLEME MODELDEN İSTENMEZ, ÇIKARILIR ──────────────────────────
#
# `C3`'ün ilk yazımı eşlemeyi modelden istiyordu. Canlıda İKİ kez ölçüldü ve ikisi de
# başarısız: düzyazı talimat («isteğe bağlı») → alan hiç yazılmadı; `Biçim:` şablonunda
# **«ZORUNLUDUR»** → yine hiç yazılmadı. Üç turda üçünde de model DOĞRU çevirdi ama
# çevirisini SÖYLEMEDİ.
#
# *Bir modelden cevabı taşımayan bir alanı doldurmasını istemek, ona bir dipnot
# yazdırmaktır; cevabı verir, dipnotu atlar.*

_SEMA_C = {"cubes": [{
    "name": "parti",
    "synonyms": ["parti", "üretim"],
    "measures": ["toplam_fire_kg", "toplam_ciro"],
    "dimensions": ["musteri", "hat"],
    "measure_synonyms": {"toplam_fire_kg": ["fire", "toplam fire"],
                         "toplam_ciro": ["ciro", "toplam ciro"]},
    "dimension_synonyms": {"musteri": ["musteri", "müşteri"], "hat": ["hat"]},
}]}


def test_CIKARIM_TEK_BILINMEYENI_TEK_HEDEFE_BAGLAR():
    """🔴 Canlı vaka: *«bu yıl zayiat ne kadar»* → route `zayiat`ı bilmiyor, garson
    `toplam_fire_kg` seçti. Eşleme bu ikisinin **kesişimidir** — modelden bir şey
    istemeye gerek yok."""
    t = cr.eslesen_terim_cikar(cr._norm("bu yil zayiat ne kadar"),
                               {"cube": "parti", "measures": ["toplam_fire_kg"]}, _SEMA_C)
    assert t == {"soz": "zayiat", "ad": "toplam_fire_kg"}


def test_CIKARIM_ROUTEUN_BILDIGI_ADI_ELER():
    """🔴🔴 **Kuralın kalbi.** *«alıcı bazında ciro»*: `ciro` route'un sözlüğünde **var**
    (elenir), `musteri` **yok** (kalır) → `alici → musteri`. Eleme olmasaydı iki hedef
    kalır ve kural susardı."""
    t = cr.eslesen_terim_cikar(
        cr._norm("bu yil alici bazinda ciro"),
        {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"]}, _SEMA_C)
    assert t == {"soz": "alici", "ad": "musteri"}


def test_IKI_BILINMEYENDE_SUSAR():
    """⚠ Hangi kelimenin hangi ada gittiği **bilinemez**. *Tekil aday yoksa sus* —
    bugün üçüncü kez uygulanan aynı disiplin."""
    assert cr.eslesen_terim_cikar(
        cr._norm("bu yil zayiat ve hasilat ne kadar"),
        {"cube": "parti", "measures": ["toplam_fire_kg", "toplam_ciro"]}, _SEMA_C) is None


def test_BILINMEYEN_YOKSA_CIKARIM_YOK():
    """Her kelimesi tanınan bir soruda öğrenilecek bir şey yoktur."""
    assert cr.eslesen_terim_cikar(cr._norm("bu yil toplam ciro"),
                                  {"cube": "parti", "measures": ["toplam_ciro"]},
                                  _SEMA_C) is None


def test_IKI_HEDEFTE_SUSAR():
    """Tek bilinmeyen ama iki ulaşılamayan ad → eşleme **belirsizdir**, üretilmez."""
    assert cr.eslesen_terim_cikar(
        cr._norm("bu yil zayiat"),
        {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["musteri"]},
        _SEMA_C) is None


# ── HASAT: kanıtlı adaylar ────────────────────────────────────────────────────

def test_HASAT_CELISKILI_ESLEMEYI_KUYRUGA_ALMAZ():
    """🔴🔴 `C5`'in sert kuralı **burada da** geçerli: aynı kelime farklı turlarda
    farklı adlara çözüldüyse bu bir sinonim değil bir **belirsizliktir**.

    Onu sözlüğe yazmak, `bakiye`'nin ₺11,86 milyonluk seçimini **kalıcı** yapmakla
    aynı hatadır — bugün `D6`'da ölçülen tam o vaka.
    """
    from lab import sinonim_hasadi as sh
    assert sh.eslesme_sinifi("bakiye", {"cari.bakiye": 5, "mizan.bakiye": 4},
                             _SEMA_C) == "celiskili"


def test_HASAT_TEK_GORULEN_ESLEME_SEYREKTIR():
    """*Tek görülen bir eşleme bir örüntü değil bir olaydır* — `ASGARI_SIKLIK` aynı
    eşikle burada da uygulanır; ikinci bir eşik ikinci bir sahip olurdu."""
    from lab import sinonim_hasadi as sh
    assert sh.eslesme_sinifi("zayiat", {"toplam_fire_kg": 1}, _SEMA_C) == "seyrek"


def test_HASAT_TUTARLI_VE_SIK_ESLEME_ADAYDIR():
    """✅ Onaya hazır: *«`zayiat` = `toplam_fire_kg` ve 14 kez böyle çözüldü»* bir
    sorudan farklıdır — bir insanın düşünmesini değil, yalnız **onayını** ister."""
    from lab import sinonim_hasadi as sh
    assert sh.eslesme_sinifi("zayiat", {"toplam_fire_kg": 14}, _SEMA_C) == "aday"
