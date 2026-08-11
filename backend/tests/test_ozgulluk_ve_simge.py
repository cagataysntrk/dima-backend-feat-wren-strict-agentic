"""🔴🔴 `§UT` + `§SB` — **AYNI AİLE: bir terimin TAMAMI mı karşılandı?**

İki kusur da tek turda ölçüldü ve ikisi de *«kullanıcının yazdığı şeyin bir PARÇASI»*
üstünden çalışıyor:

| # | ölçülen soru | ne oldu | neden |
|---|---|---|---|
| `§UT` | *«en kötü **bakım maliyeti** hangi makinede»* | `maliyet.ort_birim_maliyet`, beyan **yok** | niteleyen düştü: `bakim maliyeti` (2 kelime) yerine `maliyet` (1 kelime) |
| `§SB` | *«ortalama **dE**»* | **R4** — hiçbir küp eşleşmedi | `dE` → `de` (Türkçe bağlaç); simge normalizasyonda **yok oldu** |

⊙ Ve ikisinin de çözümü bir **sözlük değil**: biri bir **kapsama ilişkisi** (kelime
kümesi), öteki bir **yazım imzası** (sözcük içi büyük harf). Kullanıcının kuralı burada
birebir geçerli: *«tek tek sinonim yazmak aptallık»* — özellikle `de` gibi bir bağlacı
sinonim yazmak (`§73`'ün tek-harf felaketinin kardeşi).
"""

from app import cube_router as cr
from app import simge
from app import uyum

# --- `§UT` · NİTELEYENİ DÜŞEN TAMLAMA ---------------------------------------------

_SEMA = {"cubes": [
    {"name": "maliyet", "display": "birim maliyet",
     "measure_synonyms": {"ort_birim_maliyet": ["maliyet", "birim maliyet"]},
     "measures": ["ort_birim_maliyet"], "dimensions": ["makine"]},
    {"name": "bakim_is_emri", "display": "bakım iş emri",
     "measure_synonyms": {"bakim_maliyeti": ["bakim maliyeti"]},
     "measures": ["bakim_maliyeti"], "dimensions": ["makine"]},
    {"name": "parti", "display": "parti",
     "measure_synonyms": {"toplam_ciro": ["ciro"]},
     "measures": ["toplam_ciro"], "dimensions": ["musteri"]},
]}
_MALIYET = _SEMA["cubes"][0]


def test_DAHA_OZGUL_SAHIP_BULUNUR():
    """🔴 **Kapının kalbi.** Kullanıcı iki kelimelik tamlamayı **yazmıştı**."""
    q = cr._norm("bu yıl en kötü bakım maliyeti hangi makinede")
    sonuc = uyum._daha_ozgul_sahip(q, _MALIYET, _SEMA)
    assert sonuc is not None
    assert sonuc[0] == "bakim maliyeti" and sonuc[1] == ["bakim_is_emri"]


def test_TAM_TERIM_SORULDUYSA_SESSIZ():
    """⚠ Cevabın küpü zaten en özgül olanıysa söylenecek bir şey yoktur."""
    q = cr._norm("bu yıl birim maliyet")
    assert uyum._daha_ozgul_sahip(q, _MALIYET, _SEMA) is None


def test_KESISMEYEN_TERIM_OZGULLUK_DEGILDIR():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    `ciro` ile `maliyet` bir özgüllük ilişkisi değil **iki ayrı kavramdır** — oraya
    `§Ci` (ölçü ikamesi) bakar. Bu kapı onu çalarsa iki kusur da yanlış adla anılır."""
    q = cr._norm("bu yıl maliyet ve ciro")
    sonuc = uyum._daha_ozgul_sahip(q, _MALIYET, _SEMA)
    assert sonuc is None or sonuc[1] != ["parti"]


def test_CEVABIN_KUPU_HIC_ESLESMIYORSA_SESSIZ():
    """Kendi terimi yoksa kıyaslanacak bir kapsam da yoktur — `KURAL B`."""
    q = cr._norm("bu yıl toplam üretim")
    assert uyum._daha_ozgul_sahip(q, _MALIYET, _SEMA) is None


def test_BEYAN_IKAMEDEN_AYRI_BIR_ISARET():
    """🔴 `olcu_ikamesi` cümlesi (*«bu cevap onu içermiyor»*) burada **yalan** olurdu:
    cevap bir maliyet içeriyor, yalnız **istenen** maliyeti değil.
    *Bir kusuru en yakın komşusunun adıyla anmak, iki kusuru da görünmez yapar.*"""
    q = cr._norm("bu yıl en kötü bakım maliyeti hangi makinede")
    ihlaller = uyum.denetle(q, {"cube_query": {"cube": "maliyet",
                                               "measures": ["ort_birim_maliyet"],
                                               "dimensions": ["makine"]}},
                            _MALIYET, _SEMA)
    isaretler = {i.isaret for i in ihlaller}
    assert "olcu_ozgullugu" in isaretler
    metin = next(i.aciklama for i in ihlaller if i.isaret == "olcu_ozgullugu")
    assert "parça" in metin and "içermiyor" not in metin


# --- `§SB` · TEKNİK SİMGE ----------------------------------------------------------

def test_SOZCUK_ICI_BUYUK_HARF_SIMGEDIR():
    """🔴 Türkçe sözcüklerde sözcük içi büyük harf **yoktur** — imza budur."""
    assert simge.simgeler("müşteri bazında ortalama dE bu yıl") == {"dE"}
    assert simge.simgeler("aylık kWh tüketimi") == {"kWh"}
    assert simge.simgeler("pH değeri") == {"pH"}


def test_NORMAL_TURKCE_SIMGE_URETMEZ():
    """🔴🔴 Yanlış-pozitif kapısı: gündelik bir cümle simge taşımamalı, yoksa her
    netleştirmeye alakasız chip'ler dolardı (`§101.1`)."""
    assert simge.simgeler("bu yıl toplam ciro makine bazında") == set()
    assert simge.simgeler("en çok duruşa yol açan 3 nedeni bul") == set()


def test_TUMU_BUYUK_KISALTMA_SIMGE_SAYILMAZ():
    """⚠ `OEE` küçültülünce **zaten** doğru eşleşir; onu bu yola sokmak gereksiz bir
    genişlemedir. *Bir kuralı, ihtiyaç bittiği yerde genişletmek onu bir tahmine
    çevirir.*"""
    assert simge.simgeler("makine bazında OEE") == set()


def test_SIMGE_SAHIBI_KIMLIKTEN_BULUNUR():
    """🔴 Ölçülen kusurun kendisi: `dE`'yi **kimliğinde** taşıyan ölçüler chip olur."""
    sema = {"cubes": [
        {"name": "kalite", "measures": ["ort_dE"],
         "measure_synonyms_display": {"ort_dE": "ortalama dE (kalite)"}},
        {"name": "sikayet", "measures": ["ort_sapma_dE"],
         "measure_synonyms_display": {"ort_sapma_dE": "şikâyet dE"}},
        {"name": "parti", "measures": ["ort_renk_sapmasi", "toplam_ciro"]},
    ]}
    etiketler = simge.sahipler("müşteri bazında ortalama dE bu yıl", sema,
                                   haric="parti")
    assert etiketler == ["ortalama dE (kalite)", "şikâyet dE"]


def test_HARIC_TUTULAN_KUP_ATLANIR():
    """Netleştirmeyi açan küp kendi ölçülerini zaten listeliyor — tekrar etmez."""
    sema = {"cubes": [{"name": "kalite", "measures": ["ort_dE"]}]}
    assert simge.sahipler("ortalama dE", sema, haric="kalite") == []


def test_SIMGESIZ_SORUDA_HIC_CHIP_URETILMEZ():
    """`KURAL B`: simge yoksa bu yol **hiç** konuşmaz."""
    sema = {"cubes": [{"name": "kalite", "measures": ["ort_dE"]}]}
    assert simge.sahipler("bu yıl toplam ciro", sema) == []


# --- `§YT` · YUVA BİR DEĞER DEĞİLDİR ------------------------------------------------

def test_YUVA_TANINIR():
    """🔴 `§UT` canlıda doğrulanırken **yeni bir kusur ifşa oldu**: not kullanıcıya
    *«⚠ Etkisiz bir dışlama düşürüldü («{{ENT_1}}» ∉ makine)»* yazdı — yani bir
    perdeleme yuvası geri konmadan süzgece, oradan da beyana sızmıştı."""
    from app import yayilim

    assert yayilim.yuva_mu("{{ENT_1}}") is True
    assert yayilim.yuva_mu("{{DIM_12}}") is True
    assert yayilim.yuva_mu("RAM-1") is False
    assert yayilim.yuva_mu("") is False


def test_YUVA_SESSIZCE_DUSER():
    """⚠ Yuva **adlandırılmaz**: bir yuva hiçbir katalogda bulunamaz çünkü hiçbir zaman
    bir değer değildi. Süzgeç yine düşer, ama kullanıcıya iç mekanizma gösterilmez.
    *Bir maskeyi değer sanan kod, maskenin var olma sebebini de kaybeder.*"""
    from app import deger_capasi as dc

    sema = {"cubes": [{"name": "m", "dimensions": ["makine"],
                       "dimension_values": {"makine": ["RAM-1", "RAM-2"]},
                       "time_dimensions": []}]}
    cq = {"cube": "m", "measures": ["x"],
          "filters": [{"dimension": "makine", "operator": "neq", "value": "{{ENT_1}}"}]}
    notu, netlestir = dc.huni_karari(cq, sema)
    assert netlestir is None
    assert cq["filters"] == []
    assert notu is None, f"🔴 yuva kullanıcıya sızdı: {notu!r}"


def test_GERCEK_DEGER_HALA_ADLANDIRILIR():
    """🔴🔴 **Fazla ileri gitmemek.** Gerçek bir değerde `§NT` beyanı aynen yazılır —
    yoksa bu düzeltme `§NT`'yi sessizce kaldırırdı."""
    from app import deger_capasi as dc

    sema = {"cubes": [{"name": "m", "dimensions": ["makine"],
                       "dimension_values": {"makine": ["RAM-1", "RAM-2"]},
                       "time_dimensions": []}]}
    cq = {"cube": "m", "measures": ["x"],
          "filters": [{"dimension": "makine", "operator": "neq", "value": "Bakım"}]}
    notu, _ = dc.huni_karari(cq, sema)
    assert notu and "Bakım" in notu


def test_OZGULLUK_BEYANI_CHIP_TASIR():
    """🔴 `§TZ` deseni — *«sorabilirsin»* demek yetmez, **sorulabilir** yapmak gerekir.

    ⊙ Ölçüldü: *«bakım maliyeti raporu hazırla»* **6/6** genel küpe gidiyor ve beyan her
    seferinde doğru sahibi **adıyla** söylüyordu — ama kullanıcı onu **yazmak**
    zorundaydı. Bugün eklenen her beyan (dönem · değer · özgüllük) aynı dersi taşıyor.
    """
    q = cr._norm("bu yıl en kötü bakım maliyeti hangi makinede")
    ihlaller = uyum.denetle(q, {"cube_query": {"cube": "maliyet",
                                               "measures": ["ort_birim_maliyet"],
                                               "dimensions": ["makine"]}},
                            _MALIYET, _SEMA)
    chipler = uyum.chipler(ihlaller)
    assert chipler, "🔴 özgüllük beyanı tık taşımıyor"
    assert chipler[0]["query"] == "bakim_is_emri bakim maliyeti"
    assert "bakim maliyeti" in chipler[0]["label"]


def test_CHIPSIZ_IHLAL_KANALA_GIRMEZ():
    """⚠ Her ihlal tıklanabilir değildir; olmayanı chip'e çevirmek kullanıcıya
    **çalışmayan** bir düğme verirdi. *Bir tıkın var olması, gideceği bir yer olmasına
    bağlıdır.*"""
    assert uyum.chipler([uyum.Ihlal("trend", "x", "y")]) == []
    assert uyum.chipler([]) == []
