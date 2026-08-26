"""🔴🔴 `§AY` — **YORUMLANACAK ŞEY YOKKEN DISCOVERY ATEŞLİYORDU.**

## Ölçülen kusur (curl `O` turu, 2026-08-10 · beş turluk thread)

    t1  «bu yıl kalite sorunları»  → netleştirme (ortada RAPOR YOK)
    t2  «bunu yorumla»             → 🔴 Discovery: 18 satır vardiya×gün OEE — ALAKASIZ
    …
    t5  «en kötü üçünü grafikle göster» → «bu takip mesajını ilişkilendiremedim»

Kullanıcı **ekrandaki** cevabı yorumlamak istedi; ekranda cevap yoktu; sistem ham SQL
yazıp alakasız bir tablo üretti. Ve bedeli turla sınırlı kalmadı: `adhoc` cevap thread'in
**çapası** oldu ve sonraki turlar öldü.

⊙ Aynı üç yazım izole bir thread'de **çalışıyor** (ölçüldü) — yani `t5`'in reddi bir
ifade kusuru değil, `t2`'nin **alt sonucudur**. Kök tek: bağlamsız konuşma.

## `§X4` bu kuralı ZATEN yazmıştı — ama bir sınıfa

*Bir kural yalnız bir basamakta geçerliyse, o kural değil bir tesadüftür* — bugün
**altıncı** kez. Ve gerekçe burada daha da güçlü: **hiçbir SQL** *«ekranda ne var»*ı
cevaplayamaz, çünkü sorulan şey veride değil ekrandadır.
"""

from app import followup


def _bs(soru):
    return followup.sinifla(soru, baglam_var=False)


def test_YORUMLA_BAGLAMSIZ_MERDIVENE_INMEZ():
    """🔴 **Kapının kalbi** — ölçülen turun kendisi."""
    n = _bs("bunu yorumla")
    assert n.kural == "konusma-baglamsiz" and n.tur == followup.TUR_ANLAT


def test_NORMAL_MI_ZAMIRSIZ_DA_SAYILIR():
    """⚠ *«normal mi»* ve *«ne yapmalıyız»* — çıplak, KISA sorular — zamirsiz de
    konuşma sayılır (`_kisa_soru` şartından geçerler; `§AY/S` düzeltmesinden SONRA
    da böyle — bu ikisi zaten kısa, düzeltme yalnız UZUN cümlelerdeki muafiyeti
    kaldırdı, bkz. `test_UZUN_NE_YAPMALI_CUMLESI_CALINMAZ`)."""
    assert _bs("normal mi").kural == "konusma-baglamsiz"
    assert _bs("ne yapmalıyız").kural == "konusma-baglamsiz"


def test_UZUN_NE_YAPMALI_CUMLESI_CALINMAZ():
    """🔴🔴 `§AY/S` — **ASIL DÜZELTME.** Ölçülen kusur (canlı, 2026-08-26): uzun,
    zamirsiz, baştan sona geçerli bir YENİ veri isteği, içinde bir yerde
    `ne_yapmali`/`normal` kalıbı geçtiği için TAMAMEN reddediliyordu — `anlat`/
    `işaret` için zaten önlenen `test_KONU_DEGISIMI_CALINMAZ` hatasının ikiz
    kardeşi. Artık bu ikisi de `TUR_ANLAT`/`TUR_ISARET` ile AYNI muafiyete tabi.

    ⚠ Örnek cümle KASITLI OLARAK "bu yıl"/"bu ay" gibi bir baştan-temporal ifade
    TAŞIMIYOR — o ayrı, DAHA ÖNCE VAR OLAN bir bug (`_ISARET_ZAMIRI`'ndeki çıplak
    "bu", "bu yıl"/"bu ay" gibi TAMAMEN ilgisiz temporal ifadeleri de zamir sanıyor,
    ölçüldü: `test_CIPLAK_BU_TEMPORAL_IFADEYLE_KARISIYOR` — henüz düzeltilmedi,
    ayrı bir roadmap maddesi)."""
    uzun = ("her ay için ciro ve fire oranını göster, hangi ay en "
            "kötüsüydü açıkla, ve gelecek ay için ne yapmalıyız söyle")
    assert _bs(uzun).kural == "baglam-yok"
    uzun2 = ("vardiya bazında oee ve fire karşılaştır, en kötü vardiyayı bul, "
             "sebebini araştır, ve o vardiya için somut 3 aksiyon öner")
    assert _bs(uzun2).kural == "baglam-yok"


def test_CIPLAK_BU_TEMPORAL_IFADEYLE_ARTIK_KARISMIYOR():
    """✅ FAZ 3.4 — DÜZELTİLDİ (bu test eskiden BUGÜNKÜ KUSURLU davranışı sabitliyordu,
    adı da öyleydi — `KARISIYOR`; artık DÜZELTİLMİŞ davranışı kilitliyor, `ARTIK_
    KARISMIYOR`).

    Eski kusur: `_ISARET_ZAMIRI`'ndeki çıplak `"bu"`, "bu yıl"/"bu ay" gibi son
    derece yaygın TEMPORAL ifadeleri de (bağlamsal referansla hiç ilgisi olmayan)
    bir "rapora işaret eden zamir" sanıyordu — ölçüldü: `"bu yıl her ay için
    ciro..."` cümlesi `açıkla` (`TUR_ANLAT`) → çıplak "bu" zamir eşleşmesi
    yolundan yanlış `konusma-baglamsiz` sayılıyordu (`§AY/S`'in KAPSAMADIĞI,
    `KÖK NEDEN A` ailesinin üçüncü örneği).

    Kök çözüm: `followup._bu_su_zamir_mi()` — "bu"/"su" yalnız GERÇEK bir takvim/
    zaman-birimi isim (yıl/ay/hafta/gün/dönem/çeyrek — kapalı dilbilgisi sınıfı,
    `cube_router._ek_gecerli` ile ek-toleranslı) TAKİP ETMİYORSA zamir sayılır.
    "bu rapor"/"bu tablo"/"bu grafik"/"bu sonuc" gibi çok-kelimeli, rapora
    GERÇEKTEN işaret eden biçimler `_ISARET_ZAMIRI`'nde DEĞİŞMEDEN kaldı — bkz.
    `test_GERCEK_BU_ZAMIRI_HALA_TANINIR` (zıt-ölçüt)."""
    uzun = ("bu yıl her ay için ciro ve fire oranını göster, hangi ay en "
            "kötüsüydü açıkla, ve gelecek ay için ne yapmalıyız söyle")
    assert _bs(uzun).kural == "baglam-yok", (
        "🔴 'bu yıl' yine 'rapora işaret eden zamir' sayılıp cümle yanlışlıkla "
        "konusma-baglamsiz'e düşüyor — FAZ 3.4'ün düzeltmesi bozulmuş olabilir.")


def test_GERCEK_BU_ZAMIRI_HALA_TANINIR():
    """🔴 Zıt-ölçüt (FAZ 3.4) — `_bu_su_zamir_mi()` yalnız TEMPORAL kullanımı
    dışlamalı, GERÇEK zamir kullanımını BASTIRMAMALI. "bunu yorumla" (`bunu`,
    çekimli) ve çıplak "bu" (temporal olmayan, örn. "bu doğru mu") hâlâ doğru
    zamir sayılmalı — aksi hâlde düzeltme kusuru TERSİNE çevirmiş olurdu."""
    assert followup.sinifla("bunu yorumla", baglam_var=True).sinif == followup.SINIF_KONUSMA
    assert followup._bu_su_zamir_mi("bu dogru mu") == "bu"
    assert followup._bu_su_zamir_mi("bu rapor neyi anlatiyor") == "bu"
    assert followup._bu_su_zamir_mi("bu yil ciro ne kadar") is None
    assert followup._bu_su_zamir_mi("su ay fire orani") is None


def test_KONU_DEGISIMI_CALINMAZ():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    *«fire analizini yap»* bir **konu değişimidir** — zamir yok, kısa değil. Buraya
    girseydi kullanıcının yeni sorusu bir *«rapor yok»* cümlesine dönerdi; yani bir
    kusuru düzeltirken daha görünür bir tanesini açardık."""
    assert _bs("fire analizini yap").kural == "baglam-yok"


def test_NEDEN_DISARIDA_KALDI():
    """🔴 *«neden fire yüksek olur»* bağlamsız da olsa **gerçek bir veri sorusudur** ve
    merdivenin cevaplaması gerekir. `_NEDEN` bilerek kapsam dışı."""
    assert _bs("neden fire yüksek olur").kural == "baglam-yok"


def test_MAKBUZ_DALI_BOZULMADI():
    """`§X4` aynen yaşıyor — bu düzeltme onun **kardeşi**, yerine geçeni değil."""
    assert _bs("bu nasıl hesaplandı").kural == "makbuz-baglamsiz"


def test_BAGLAM_VARSA_HIC_KONUSMAZ():
    """`KURAL B`: ekranda rapor varsa yol birebir bugünküdür."""
    n = followup.sinifla("bunu yorumla", baglam_var=True)
    assert n.sinif == followup.SINIF_KONUSMA and n.tur == followup.TUR_ANLAT


def test_MAKBUZ_METNI_DE_AYNI_SAHIPTE():
    """⚠ `§X4`'ün cümlesi `ask.py`'den buraya **taşındı**: iki dal birleşince metnin de
    tek yazarı olmalı. *İki dalın aynı şeyi söylediği yerde, iki dal değil bir dal vardır.*"""
    metin = followup.baglamsiz_metni(None, "makbuz-baglamsiz")
    assert "nasıl hesaplandığını" in metin and "hangi formül" in metin


def test_METIN_TURUNE_GORE_DEGISIR():
    """⚠ Metnin **tek yazarı** `followup` (🗣 modül); `ask()` yalnız çağırır. İkinci bir
    yazar, bir gün ikinci bir cümle demektir."""
    assert "Yorumlayabileceğim" in followup.baglamsiz_metni(followup.TUR_ANLAT)
    assert "Öneri" in followup.baglamsiz_metni(followup.TUR_NE_YAPMALI)


def test_METIN_NE_YAPILACAGINI_SOYLER():
    """🔴 *Dürüst bir red bir başarı değildir; dürüst bir YÖNLENDİRME bir cevaptır.*"""
    for tur in (followup.TUR_ANLAT, followup.TUR_NORMAL, followup.TUR_ISARET):
        metin = followup.baglamsiz_metni(tur)
        assert "Önce bir soru sor" in metin and "oee" in metin


def test_BILINMEYEN_TURDE_DE_METIN_VAR():
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir* — tür çözülemezse de
    kullanıcı cevapsız kalmaz."""
    assert followup.baglamsiz_metni(None)
    assert followup.baglamsiz_metni("yok-boyle-tur")
