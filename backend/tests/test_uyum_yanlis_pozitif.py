"""🔴🔴 `§UY/K` — **ÖBEK EŞLEŞMEZ AMA KELİME KAPSANIR: doğru bir cevap «eksik» diye
etiketleniyordu.**

## Ölçülen kusur (curl turu, 2026-08-10)

    «en çok duruşa yol açan 3 nedeni bul»
      → makine_duruslari.toplam_sure_dk · «Malzeme/Parti Bekleme · 427.140 dk»  ✅ DOĞRU
      → not: «⚠ Sayı doğru ama EKSİK: «durus» bu küpte tanımlı değil.»          🔴 YANLIŞ

🔴 Oysa kelime **bol bol** kapsanıyordu: küp sinonimleri `durus nedeni` · `durus
sebebi`; ölçü sinonimleri `toplam durus` · `toplam durus dakikasi`. Sebep: hepsi **çok
kelimeli öbek** ve `_match_measure` **tam öbeği** arıyor — soruda öbek geçmiyor,
**kelime** geçiyor.

⊙ Doğru yüklem depoda **zaten vardı**: `partial_unknowns` kapsamayı `_syn_hit_words`
ile **kelime düzeyinde** hesaplıyor. İkinci bir kapsama kavramı yazmak `KAT-1` olurdu.

*Bir doğru cevaba «eksik» demek, tüm beyanların güvenini aşındırır* (`§101.1`): kusur
bazen olur, yanlış-pozitif **her seferinde** yanlıştır.
"""

from app.uyum import _kup_sozlugunde_kelime as kapsiyor

_DURUS = {
    "name": "makine_duruslari",
    "display": "duruş nedenleri",
    "synonyms": ["durus nedeni", "durus kaydi", "stoppage reason"],
    "measure_synonyms": {"toplam_sure_dk": ["toplam durus dakikasi", "toplam durus"],
                         "durus_sayisi": ["durus sayisi", "kac durus"]},
    "dimension_synonyms": {"neden": ["neden", "sebep"]},
    "measures": ["toplam_sure_dk", "durus_sayisi"],
    "dimensions": ["neden", "makine"],
}
_KALITE = {
    "name": "kalite",
    "display": "kalite",
    "synonyms": ["kalite", "tamir rework"],
    "measure_synonyms": {"rework_sayisi": ["rework", "tamir sayisi"]},
    "dimension_synonyms": {"musteri": ["musteri"]},
    "measures": ["rework_sayisi"],
    "dimensions": ["musteri"],
}


def test_COK_KELIMELI_SINONIMIN_ICINDEKI_KELIME_KAPSANIR():
    """🔴 **Kusurun kendisi.** `durus` hiçbir sinonime **tek başına** eşit değil ama
    dördünün de **içinde** — ve cevap o kavramı ölçüyor."""
    assert kapsiyor("durus", _DURUS) is True


def test_GERCEK_IKAME_HALA_BEYAN_EDILIR():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    `§Cİ`'nin ölçtüğü gerçek vaka — kullanıcı **fire** sordu, cevap **rework** verdi —
    bu düzeltmeden **etkilenmemeli**: `kalite`nin sözlüğünde `fire` diye bir kelime yok,
    beyan aynen yazılır. *Bir yanlış-pozitifi kapatırken gerçek pozitifi kapatmak,
    kapıyı dekora çevirir.*
    """
    assert kapsiyor("fire", _KALITE) is False


def test_KENDI_OLCUSU_KAPSANIR():
    """Cevabın kendi ölçüsünün adı elbette kapsanır — kapının tabanı."""
    assert kapsiyor("rework", _KALITE) is True


def test_ALAKASIZ_TERIM_KAPSANMAZ():
    """`ciro` duruş küpünün sözlüğünde geçmez — yüklem **gevşek değil**."""
    assert kapsiyor("ciro", _DURUS) is False


def test_COK_KELIMELI_TERIM_TAMAMI_ARANIR():
    """⚠ Terim kendisi çok kelimeliyse **hepsi** kapsanmalı: bir kelimesi geçiyor diye
    kapsanmış sayılmak, yüklemi gevşetip gerçek ikameyi gizlerdi."""
    assert kapsiyor("toplam durus", _DURUS) is True
    assert kapsiyor("toplam ciro", _DURUS) is False


def test_KISA_KELIMELER_SAYILMAZ():
    """⚠ İki harfli parçalar tesadüfen her yerde bulunur; `partial_unknowns`'ın aynı
    disiplini burada da geçerli."""
    assert kapsiyor("da", _DURUS) is False


def test_BOS_TERIM_KAPSANMIS_SAYILMAZ():
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir* — boş terim `True`
    dönseydi bütün beyanlar susardı."""
    assert kapsiyor("", _DURUS) is False


class _SahteNiyet:
    def __init__(self, **kw):
        self.olcu_adaylari = kw.get("olcu_adaylari", [])
        self.kirilimlar = kw.get("kirilimlar", [])
        self.donem_sayisi = kw.get("donem_sayisi", 0)
        self.filtreler = kw.get("filtreler", [])


def test_KA_HICBIR_EKSENE_DEGMEYEN_SORU_BEYAN_EDILIR():
    """🔴🔴 `§KA` — ölçüldü (curl `CC` turu, CC-15): *«asdfgh qwerty»* → `cube+llm`,
    **11 satırlık makine bazında OEE raporu**, not YOK. `route()`in kapsam kapısı var;
    garson devraldığında o kapı **hiç koşmuyor**.

    ⚠ Bir kapı değil bir **beyandır**: cevap gider, yanına varsayım olduğu yazılır —
    reddetmek `§0.0`'ı (*«anlamadım» bir son cevap olamaz*), susmak `E-2`'yi çiğnerdi."""
    from app import uyum

    assert uyum.tanimadan_cevap_notu(_SahteNiyet()) is not None


def test_KA_TANINAN_TEK_BIR_EKSEN_BILE_SUSTURUR():
    """`§101.1` kalibrasyonu — aynı turda ölçülen iki vaka **susmalı**, oysa ikisinin de
    `bilinmeyen` artığı doludur:

        «lütfen bana bu yılın cirosunu söyler misin» → bilinmeyen=soyler,misin  (ölçü+dönem VAR)
        «kaç makinemiz var»                          → bilinmeyen=kac,makinemiz (kırılım VAR)

    *Artığa bakan bir yüklem bu ikisini suçlardı; tanınana bakan yüklem susuyor.*"""
    from app import uyum

    for kw in ({"olcu_adaylari": [("parti", "toplam_ciro")]}, {"kirilimlar": ["makine"]},
               {"donem_sayisi": 1}, {"filtreler": [{"dimension": "makine"}]}):
        assert uyum.tanimadan_cevap_notu(_SahteNiyet(**kw)) is None, kw
    assert uyum.tanimadan_cevap_notu(None) is None


class _Yanit:
    def __init__(self):
        self.note = None
        self.trace = []


_SEMA_YS = {"cubes": [{
    "name": "parti", "dimensions": ["musteri"],
    "synonyms": ["parti", "uretim"],
    "measure_synonyms": {"toplam_ciro": ["ciro", "hasilat", "satis"]},
    "dimension_synonyms": {"musteri": ["musteri", "cari"]},
}]}
_CQ_YS = {"cube": "parti", "measures": ["toplam_ciro"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}],
          "period_expr": "bu yıl"}


def test_YS_ATILAN_TERIM_BEYAN_EDILIR():
    """🔴🔴 `§YS` — üç canlı ölçüm, tek sınıf: *«…ciroyu **euro** olarak göster»* →
    ₺74.022.836 · *«**mars gezegenindeki** satışlarımız»* → ₺137.588.350 · *«bütçe
    **gerçekleşme** oranı»* → `toplam_hedef`. Üçünde de garson soruyu okudu, bir kısmını
    temsil edemedi ve **sessizce attı**."""
    from app import uyum

    r = _Yanit()
    assert uyum.yok_sayilan_beyani(r, "bu yıl ciroyu euro olarak göster", _CQ_YS,
                                   _SEMA_YS["cubes"][0], _SEMA_YS, ["euro"]) is True
    assert "euro" in (r.note or "") and "yansımadı" in (r.note or ""), r.note


def test_YS_UYDURULAN_TERIM_DUSER():
    """**Süzgeç 1** — model bir sözcük uydurabilir; kullanıcının cümlesinde yoksa iddia
    düşer. *Bir hakemin sözünü tartmadan yayımlamak, hakemliği ona devretmektir.*"""
    from app import uyum

    r = _Yanit()
    assert uyum.yok_sayilan_beyani(r, "bu yıl toplam ciro", _CQ_YS,
                                   _SEMA_YS["cubes"][0], _SEMA_YS, ["euro"]) is False
    assert not r.note


def test_YS_FISTE_KARSILANAN_TERIM_DUSER():
    """**Süzgeç 2** — `§101.1`: başka biçimde karşılanan bir terim eksik sayılmaz.
    *«hasılat»* `toplam_ciro`'nun sinonimidir ve fiş onu **taşır**."""
    from app import uyum

    r = _Yanit()
    assert uyum.yok_sayilan_beyani(r, "bu yıl hasılat ne kadar", _CQ_YS,
                                   _SEMA_YS["cubes"][0], _SEMA_YS, ["hasılat"]) is False
    assert not r.note


_IDX_YS2 = {"parti": {"dimensions": ["musteri", "renk"],
                      "measures": ["toplam_ciro", "toplam_fire_kg"]}}


def test_YS2_KAPIDA_KALAN_ALAN_TOPLANIR():
    """🔴🔴 `§YS-2` — ölçüldü (curl `GG` turu): *«…ciroyu **euro** olarak göster»* →
    `ham={…"dimension":"para_birimi","value":"EUR"}` → **whitelist REDDİ**. Model
    «euro»yu **atmıyor**, kataloğumuzda olmayan bir boyutla **temsil etmeye çalışıyor**;
    beyaz liste adayı reddediyor ve oy euro'dan habersiz başka bir örneğe düşüyor."""
    from app import uyum

    ham = ('{"cube":"parti","measures":["toplam_ciro"],'
           '"filters":[{"dimension":"para_birimi","operator":"eq","value":"EUR"}]}')
    assert uyum.kapida_kalanlar(ham, _IDX_YS2) == [("para_birimi", "EUR")]


def test_YS2_REDDEDILEN_ORNEGIN_YOK_SAYILANI_DA_TOPLANIR():
    """🔴 **Reddedilen örneğin `yok_sayilan`'ı da çöpe gidiyordu.** Ölçüldü:
    *«mars gezegenindeki satışlarımız»* → `ham={"cube":null,"yok_sayilan":["mars
    gezegeni","satışlar"]}` → REDDİ. Garson **tam da istediğimiz cevabı verdi** ve
    `parse_cube_query` `None` dönünce onunla birlikte o cevap da düştü.

    *Bir kapıda geri çevrilen kâğıdın üstünde, neden geri çevrildiği de yazılıdır.*"""
    from app import uyum

    ham = '{"cube":"parti","measures":["toplam_ciro"],"yok_sayilan":["mars gezegeni"]}'
    assert ("", "mars gezegeni") in uyum.kapida_kalanlar(ham, _IDX_YS2)


def test_YS2_TOPRAKLAMA_SUZGECI_UYDURMAYI_ELER():
    """`§101.1` — denenen alan/değer sorunun bir sözcüğüyle **≥3 harflik ön ek**
    paylaşmalı. Model kataloğa dokunmayan bir şey uydurmuşsa beyan **susar**."""
    from app import uyum

    r = _Yanit()
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": []}
    # ⚠ `sema` geçilir: uydurulmuş alan yolunun kendi kapısı odur ve **artık** olmadan
    # konuşmaz — *«bu yıl toplam ciro»*da kapsanmayan bir içerik sözcüğü yoktur.
    assert uyum.kapi_beyani(r, "bu yıl toplam ciro", cq,
                            [("para_birimi", "EUR")], _SEMA_YS) is False
    assert uyum.kapi_beyani(r, "bu yıl ciroyu euro olarak göster", cq,
                            [("para_birimi", "EUR")], _SEMA_YS) is True
    # ⚠ Beyan **kullanıcının kendi sözcüğünü** yazar (*«euro»*), teknik alan adını
    # değil: uydurulmuş alan *bir şeyin düştüğünü* söyler, kapsanmayan artık *adını*.
    assert "euro" in (r.note or "") and "yansımadı" in (r.note or ""), r.note


def test_YS2_AYNI_SEY_IKI_KEZ_YAZILMAZ():
    """`k=3` örneklemede aynı alanı iki örnek denemiş olabilir — canlıda tam bu oldu
    (*«`para_birimi` = «EUR» · `para_birimi` = «EUR»»*). Bir şeyi iki kez söylemek, iki
    ayrı kusur varmış gibi okunur."""
    from app import uyum

    r = _Yanit()
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": []}
    uyum.kapi_beyani(r, "bu yıl ciroyu euro olarak göster", cq,
                     [("para_birimi", "EUR"), ("para_birimi", "EUR")], _SEMA_YS)
    assert (r.note or "").count("euro") == 1, r.note
