"""🔴🔴 KÖK-2 + KÖK-3 — **UYUM KAPISI** ve **BEYANLI KISMİ CEVAP**.

## Ölçülen kusur (devralınan raporun KN-4 · bu raporun 42 sessiz-yanlışı)

`route()` bir `CubeQuery` üretiyor ve dönüyor. Ama sorudaki **her niyet işaretinin**
sorguda karşılığı olduğu **hiçbir yerde denetlenmiyor**. Ölçülen üç sınıf:

| soru | üretilen | kaybolan |
|---|---|---|
| `mart cirosunu şubat ile kıyasla` | tek toplam | **kıyas** |
| `ocak ve haziran ciro karşılaştır` | Ocak–Haziran **toplamı** | altı ay yutuluyor |
| `ciro değişimi son 6 ay` | toplam | **değişim** ≠ trend |

🔴 Ve hepsi `source=cube` rozetiyle dönüyor — yani **kanıtlanmış yol** damgasıyla.
*Yanlış cevap veren bir sistem, sustuğunu bilen bir sistemden tehlikelidir.*

## Neden bu bir "vaka listesi" değil, bir **değişmez listesi**

Kusuru tek tek düzeltmek (her ifade için bir yama) bu deponun on dört kez avladığı
desendir. Burada tersi yapılır: **niyet türü başına bir değişmez** yazılır. Yeni bir
niyet türü eklendiğinde denetimi de eklenir — mekanizma **kendini genişletir**.

## 🔴 Sıfırdan yazılmıyor — ZATEN VAR, dörtten yediye genişletiliyor

`cube_router.py:866` ve `:1191`'de bu koruma **iki yerde elle** duruyor ve kodun kendi
yorumu adını koymuş: *"SESSİZ-YANLIŞ koruması"*. Ama yalnız **kırılım** işaretine
bakıyor ve yalnız iki dalda çalışıyor. Bu modül aynı ilkeyi **yedi işarete** ve **tek
çıkışa** taşır. Dedektörlerin **hepsi** `cube_router`'ın kendi fonksiyonlarıdır —
`compare_mode` · `_kiyas_spanlari` · `_time_gran` · `_BREAKDOWN_HINTS` ·
`_TOPN_CUE` · `_measure_threshold` · `_EXCLUDE_MARKERS`. Yeni dilbilim **yazılmıyor**.

## KÖK-3 — ve neden ikisi BİRLİKTE inmeli

KÖK-2 tek başına inseydi **kapsam daralırdı**: bugün cevaplanan sorular netleştirmeye
düşerdi. Üçüncü seçenek bunu alır:

> Bugün iki seçenek var: **cevapla** ya da **reddet**. Üçüncüsü:
> *"şu kısmını verdim, şu kısmını **veremedim**, nedeni bu."*

⚠ **ADR-0008 uyumu:** kural *"yanlış cevaba güven rozeti takma"* der. Beyanlı kısmi
cevap **rozetsizdir** — yasağı çiğnemez, **karşılar**.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Bir niyet işaretinin sorguda karşılığı yoksa üretilen kayıt.
@dataclass(frozen=True)
class Ihlal:
    """`isaret` telemetri için SABİT; `aciklama` kullanıcıya gider."""

    isaret: str
    aciklama: str
    oneri: str
    #: 🔴 `§TZ` deseni — **beyanın yanında bir tık.** Bir ihlal, kullanıcının tek
    #: hamlede düzeltebileceği bir şeyse o hamleyi **taşır**; taşımıyorsa `None`.
    #: ⚠ Metin değil **veri**: `{label, query}`. Metni chip'ten türetmek, aynı cümlenin
    #: ikinci yazarını doğururdu (`KAT-1`).
    #: *Bir kullanıcıya ne yapabileceğini söyleyip yolu göstermemek, yarım bir cevaptır.*
    chip: dict | None = None


#: *"Değişim/trend"* — zaman EKSENİ ister, tek bir toplam değil.
#: ⚠ `_time_gran` granülerliği (`aylara göre`) yakalar; bu ise **niyeti** yakalar.
_TREND = re.compile(
    r"\b(trend|trendi|degisim|degisimi|degisti|seyri|seyir|gidisat|"
    r"nasil gidiyor|nasil gitti|artti|azaldi|dustu|yukseldi)\b")

#: Çok-dönem: iki AYRI dönem adı geçiyor ve ikisi de istenmiş.
_AY = ("ocak", "subat", "mart", "nisan", "mayis", "haziran",
       "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik")


def _norm(s: str) -> str:
    return s.translate(str.maketrans("çÇğĞıİöÖşŞüÜ", "cCgGiIoOsSuU")).lower()


#: 🔴 ARALIK İŞARETLERİ — iki dönem adı **tek bir aralığın iki UCU** olabilir.
#:
#: Ölçülen yanlış-pozitif: `1 ocak 31 mart arası toplam üretim` (eval `tarih-acik-aralik`)
#: iki ay adı taşıyor ve *"çok dönem"* sanılıyordu — oysa orada **tek bir aralık** var ve
#: `route()` onu zaten `gte`+`lte` ile doğru kurmuş.
#:
#: *İki tarih, aralarında bir "arası" varsa iki istek değil bir aralıktır.*
_ARALIK = (" arasi", " arasinda", " ila ", " kadar", "dan ", "den ",
           "tan ", "ten ", " itibaren")

#: 🔴 **AŞIRI-YÜKLÜ BAĞLAÇ** — `" ile "` iki ayrı işi görür ve `G6`'da ölçüldü:
#:
#: | okuma | örnek |
#: |---|---|
#: | **aralık** | *"ocak **ile** mart arası"* → tek dönem |
#: | **birliktelik** | *"mart cirosunu şubat **ile** kıyasla"* → **iki** dönem |
#:
#: Bağlaç `_ARALIK` içindeyken ikinci okuma birinciye yutuluyordu: `cok_donem` ihlali
#: bastırılıyor, `kiyas` ihlali de (o zaman) hiç doğmuyordu → soru **1 Şubat–31 Mart
#: toplamıyla** cevaplanıp **etiketsiz** gidiyordu.
#:
#: ⚠ Bu, bu deponun defterindeki **`göre`/`bazında` aşırı-yüklenmesinin** aynı sınıfı.
#: Çözüm bir kelime eklemek değil, iki sahip arasında bir **öncelik** kurmaktır:
#: kıyas fiili varsa `" ile "` **birliktelik** okunur. Gerçek aralık ifadesi zaten
#: `" arasi"`/`" ila "` taşır — yani bu kısıt meşru aralığı **daraltmaz**.
_ARALIK_BAGLAC = (" ile ",)

#: Göreli dönem aralığı — *"son 3 ay"*, *"son 6 ay"*. İkisi AYRI birer dönemdir.
_GORELI_DONEM = re.compile(
    r"son\s+(\d+)\s*(ay|gun|hafta|yil|ceyrek)")


def _cok_donem(q: str) -> int:
    """Soruda kaç **AYRI** dönem geçiyor.

    Dört biçim sayılır ve dördü de **ölçülerek** eklendi:
      · ay adı  — `ocak ve haziran`
      · yıl     — `2025 ve 2026`
      · göreli  — `son 3 ay ve son 6 ay`        ← 🔴 ilk yazımda EKSİKTİ
      · çeyrek  — `ilk çeyrek ve ikinci çeyrek` ← 🔴 KÖK-7c açınca EKSİK ÇIKTI

    ⚠ Üçüncüsü kapıyı ölçerken yakalandı: `son 3 ay ve son 6 ay ciro` hiçbir ihlal
    vermiyordu, oysa `route()` ikisini **tek bir filtreye** (`gte 2026-05-05`) çöküyor
    ve altı ayın üçü sessizce yutuluyordu. *Bir sayacın saymadığı biçim, o sayaç için
    var olmayan bir dünyadır.*

    🔴 **Dördüncüsü, KÖK-7c'nin kendi açtığı kapıydı.** `_period_hit_words` çok-geçişe
    geçince `ilk ceyrek ve ikinci ceyrek ciro` **R10'dan kurtuldu** — ama `route()` yine
    yalnız **ilk** çeyreği çözüyor (`_quarter_period_filters` tek `.search`). Sayaç
    çeyreği saymasaydı, bu soru **R10 reddinden SESSİZ-YANLIŞA terfi** ederdi.

    *Bir kapsamı açan değişiklik, açtığı kapsamın beyan sayacını da beslemek zorundadır;
    yoksa dürüst bir "anlamadım"ı sessiz bir yanlışa çevirir.*

    ⚠ Çeyrek sözlüğü **yazılmadı, ödünç alındı**: `cube_router._QUARTER_RE` çeyreğin tek
    sahibidir. Buraya ikinci bir sıra-sayı listesi yazmak, deponun ölçülmüş *"aynı kuralın
    iki sahibi"* sınıfını yeniden doğururdu.
    """
    from app.cube_router import _PREV_RE, _QUARTER_ORD, _QUARTER_RE

    qn = _norm(q)
    aylar = {a for a in _AY if re.search(rf"(?<![a-z0-9]){a}", qn)}
    yillar = set(re.findall(r"(?<!\d)(20\d{2})(?!\d)", qn))
    goreli = {f"{n}{b}" for n, b in _GORELI_DONEM.findall(qn)}
    # Çeyreğin KİMLİĞİ numarasıdır: `ilk çeyrek` ile `1. çeyrek` **aynı** dönemdir ve iki
    # kez sayılmamalıdır (*"1. çeyrek yani ilk çeyrek"* tek istektir).
    ceyrek = {str(m.group(1) or _QUARTER_ORD[m.group(2)])
              for m in _QUARTER_RE.finditer(qn)}
    # 🔴 Beşinci biçim, KAPININ KENDİSİ yakaladı: `gecen ay ve gecen yil ciro` →
    # `route()` yalnız **Temmuz 2026**'yı çözüyor, "geçen yıl" sessizce yutuluyor.
    # Kimlik BİRİMDİR (`ay` ≠ `yil`); *"geçen ay"* iki kez geçse tek dönemdir.
    onceki = {b for b, _ek in _PREV_RE.findall(qn)}
    return len(aylar) + len(yillar) + len(goreli) + len(ceyrek) + len(onceki)


def trend_istendi(qn: str) -> bool:
    """Soru bir **değişim/trend** istiyor mu — *"değişimi"* · *"artışı"* · *"seyri"*.

    ## 🔴 Neden bir FONKSİYON (KÖK-1 Faz 2'de doğdu)

    `_TREND` bu modülün **özel** kalıbıdır. `app/niyet.py` onu doğrudan çağırdı ve kendi
    kapısı (`test_YENI_DILBILIM_YAZILMADI`) haklı olarak kırmızı verdi: bir çatının başka
    modülün **kalıbına** uzanması, o kalıbı ikinci bir sahibe açar.

    ⚠ Ödünç alınacak şey bir kalıp değil bir **karardır**. Kalıp burada kalır, karar
    adıyla dışarı çıkar. *Bir kuralı paylaşmanın doğru biçimi, kuralı değil cevabını
    paylaşmaktır.*

    ⚠ `_time_gran` ile AYNI ŞEY DEĞİLDİR: o *"aylara göre"* der (eksen istendi), bu
    *"değişimi"* der (değişim istendi). İkisini bir alanda toplamak Faz 2'nin ilk
    ölçümünde yakalandı.
    """
    return bool(_TREND.search(qn))


def ustunluk_istendi(qn: str) -> bool:
    """Soru bir **üstünlük** istiyor mu — *"en yüksek"* · *"en çok"* (SAYI gerekmez).

    ⚠ `cube_router._top_n` ile aynı şey değildir: o **sayı** ister (`en yüksek 5`), bu
    istemez. `uyum`un beşinci değişmezi bunu sorar; `route`un sıralaması ötekini.
    """
    from app.cube_router import _TOPN_CUE

    return bool(_ustunluk_mu(qn, _TOPN_CUE, None, None))


#: 🔴 `§HB` — Türkçenin **belgisiz sıfatı** `her`. Kapalı sınıf, tek sözcük.
#: ⚠ Kelime listesi değil: `her` bir dilbilgisi işaretidir ve bir **boyut adının
#: önünde** aranır — *«her zaman»* · *«her ay»* bir boyut adı taşımadığı için giremez.
HER_ISARETI = "her"


def _grup_basina_istendi(qn: str, boyutlar) -> bool:
    """*«her <boyut>»* denmiş mi? (`§HB`)

    ⚠ Çekim toleransı `cube_router._ek_gecerli`'den — **tek sahip**. Türkçe ek
    kurallarını burada ikinci kez yazmak, ikisinin zamanla ayrışması demekti.
    """
    import re as _re

    from app.cube_router import _KELIME_BASI, _ek_gecerli
    from app.cube_router import _norm as _n

    for d in (boyutlar or []):
        m = _re.search(rf"{_KELIME_BASI}{HER_ISARETI}\s+{_re.escape(_n(str(d)))}([a-z]*)", qn)
        if m and _ek_gecerli(m.group(1)):
            return True
    return False


def _kup_sozlugunde_kelime(terim: str, cube_meta: dict) -> bool:
    """Terim, cevabın küpünün **sözlüğünde bir kelime** olarak geçiyor mu?

    ⊙ `_match_measure` **öbek** arar (`«toplam durus dakikasi»`); kullanıcı ise tek
    kelime söyler (`«duruşa»`). Bu yüklem araya giren farkı kapatır: küp adı · küp
    sinonimleri · ölçü ve boyut sinonimleri **kelimelerine ayrılır** ve terim orada
    aranır.

    ⚠ Kapsam bilerek **yalnız beyan** içindir; yönlendirmeye dokunmaz. Sinonimleri
    kelimelerine ayırıp eşleştirmede kullanmak katalogu **açgözlü** yapardı (`§99.1`) —
    ama *«bu cevap o kavramı içeriyor mu»* sorusunun doğru cevabı kelime düzeyindedir.
    """
    from app.cube_router import _norm

    kelimeler: set[str] = set()
    kaynaklar = [str(cube_meta.get("name") or ""), *(cube_meta.get("synonyms") or []),
                 str(cube_meta.get("display") or "")]
    for sozluk in ("measure_synonyms", "dimension_synonyms"):
        for syns in (cube_meta.get(sozluk) or {}).values():
            kaynaklar.extend(syns or [])
    kaynaklar.extend(str(x) for x in (cube_meta.get("measures") or []))
    kaynaklar.extend(str(x) for x in (cube_meta.get("dimensions") or []))
    for k in kaynaklar:
        kelimeler |= {w for w in re.findall(r"[a-z0-9]+", _norm(str(k))) if len(w) > 2}
    hedef = {w for w in re.findall(r"[a-z0-9]+", _norm(terim)) if len(w) > 2}
    return bool(hedef) and hedef <= kelimeler


def _daha_ozgul_sahip(qn: str, cube_meta: dict, sema: dict) -> tuple[str, list[str]] | None:
    """🔴🔴 `§UT` — **NİTELEYENİ DÜŞEN TAMLAMA: «bakım maliyeti» sorup «maliyet» almak.**

    ## Ölçülen kusur (curl `N+2` turu, 2026-08-10)

        «bu yıl en kötü bakım maliyeti hangi makinede»
          → orkestratör: maliyet.ort_birim_maliyet · «ROTASYON BASKI · 30,83»
          → beyan: **YOK**

    Katalogda **tam** karşılığı vardı — ölçüldü:

        bakim_is_emri  → bakim_maliyeti      terim='bakim maliyeti'   ← 2 kelime, TAM
        maliyet        → ort_birim_maliyet   terim='maliyet'          ← 1 kelime, PARÇA

    Kullanıcı iki kelimelik bir tamlama yazdı; sistem **niteleyeni düşürüp** bir kelimelik
    bir eşleşmeyle cevapladı ve bunu hiç söylemedi.

    ## Neden `§Ci` bunu göremiyordu

    `_capraz_kup_ikamesi`'nin ilk satırı: *«cevabın küpü terimi zaten karşılıyorsa ikame
    yoktur»*. `maliyet` küpü *«maliyet»*i gerçekten karşılıyor — yüklem **doğru**, ama
    sorduğu soru eksik: *«karşılıyor mu»* diye soruyor, *«TAM MI karşılıyor»* diye değil.

    ⚠ Ve bu bir **ikame değil** bir **özgüllük kaybıdır**; o yüzden `olcu_ikamesi`
    cümlesi (*«bu cevap onu içermiyor»*) burada **yalan** olurdu — cevap bir maliyet
    içeriyor, yalnız **istenen** maliyeti değil. Ayrı işaret, ayrı cümle.
    *Bir kusuru en yakın komşusunun adıyla anmak, iki kusuru da görünmez yapar.*

    ## Yüklem — kanıtlı, katalogdan, sözlüksüz

    Başka bir küp, cevabın küpünün eşleştiği terimin **her kelimesini içeren ve daha
    uzun** bir terimle eşleşiyorsa, o küp **kesin olarak daha özgüldür**. Kanıt tamdır:
    `_match_measure` terimin soruda **gerçekten geçtiğini** garanti eder — yani kullanıcı
    o uzun ifadeyi **yazmıştır**.

    ⚠ Eşit uzunlukta ya da kesişmeyen terimler **sayılmaz**: onlar bir özgüllük ilişkisi
    değil, iki ayrı kavramdır ve oraya `§Ci` bakar.
    ⚠ Ve bu bir **beyandır**, bir yönlendirme değil: cevap değişmez, yanına *«daha özgül
    bir karşılık var»* yazılır. Yönlendirmeyi değiştirmek korpus A/B'si ister.
    """
    from app.cube_router import _match_measure, _syn_hit

    _kendi_ad, _kendi_terim = _match_measure(qn, cube_meta)
    kendi = [w for w in re.findall(r"[a-z0-9]+", _norm(str(_kendi_terim or ""))) if w]
    if not kendi:
        return None

    # 🔴🔴 `§UT-YP` — **KENDİ EKLEDİĞİM BEYANIN YANLIŞ-POZİTİFİ** (curl `T` turu, T4).
    #
    #     «geçen yıl toplam duruş dakika»  → oee.toplam_durus_dakika · 890.161 dk  ✅ TAM DOĞRU
    #       beyan: «"toplam durus" … yalnız bir parçasıyla hesaplandı»             🔴 YALAN
    #
    # ⊙ Ölçüldü — yüklem yalnız **eşleşen terimlere** bakıyordu:
    #
    #       oee              → ölçü `toplam_durus_dakika`  terim=`durus`        (1 kelime)
    #       makine_duruslari → ölçü `toplam_sure_dk`       terim=`toplam durus` (2 kelime)
    #
    # Terim kıyası *«öteki daha uzun»* diyor — ama cevabın **seçtiği ölçünün ADI** o uzun
    # terimin her kelimesini zaten taşıyor: `toplam_durus_dakika`. Yani özgüllük **hiç
    # kaybolmamıştı**; kaybolan şey yüklemin görüş alanıydı.
    #
    # ⚠ `§101.1`: bir kusur bazen olur, **yanlış-pozitif her seferinde**. Ve bu beyan
    # kullanıcıyı **doğru cevaptan** başka bir küpe yönlendiriyordu.
    # 🔴 Asıl kök yine katalogda: iki küp aynı kavrama iki ad vermiş (`B8`) — bu kapı o
    # borcu kapatmaz, yalnız yanlış cümleyi susturur.
    #
    # *Bir cevabın neyi ölçtüğünü, cevabın eşleştiği kelimeye sorarsanız, seçtiği ölçüyü
    # hiç görmemiş olursunuz.*
    kimlik = [w for w in re.findall(r"[a-z0-9]+",
                                    _norm(f"{_kendi_terim or ''} {_kendi_ad or ''}")) if w]
    kimlik_metin = " ".join(kimlik)

    def _kimlikte(w: str) -> bool:
        """Kelime, cevabın **seçtiği ölçünün kimliğinde** var mı? İki çekim yönü de sayılır:
        `dakika`↔`dakikasi` (Türkçede tamlamanın başı iyelik eki alır — `§UT`'nin kendi
        dersi). Ek zinciri disiplini yine `_syn_hit`'in; ikinci bir kural `KAT-1` olurdu."""
        return _syn_hit(kimlik_metin, w) or any(_syn_hit(w, k) for k in kimlik)

    for c in (sema.get("cubes") or []):
        if c.get("name") == cube_meta.get("name"):
            continue
        _ad, _terim = _match_measure(qn, c)
        if not _ad:
            continue
        oteki_metin = _norm(str(_terim or _ad))
        oteki = [w for w in re.findall(r"[a-z0-9]+", oteki_metin) if w]
        # 🔴 **HAM KÜME KIYASI TAM DA BURADA KIRILIYOR — ve bunu kapı yakaladı.**
        #
        # İlk yazımda yüklem `kendi < oteki` (küme alt-kümesi) idi ve ölçüldüğünde
        # **çalışmadı**: katalogdaki terim `«bakim maliyeti»`, ötekinin terimi
        # `«maliyet»` — Türkçede tamlamanın **başı iyelik eki alır** (`maliyet` →
        # `maliyeti`) ve `{maliyet} ⊄ {bakim, maliyeti}`.
        #
        # ⊙ Yani kural **tam olarak geçerli olduğu yerde** sessizce yanlış çıkıyordu.
        # Doğru yüklem depoda **zaten var**: `_syn_hit` ek zincirini bilir ve bütün depo
        # onunla eşleşir. İkinci bir ek kuralı yazmak `KAT-1` olurdu.
        #
        # *Bir dilbilgisi kuralını atlayan yüklem, atladığı yerde en çok gerekendir.*
        # `§UT-YP` — cevabın seçtiği ölçü o uzun terimi ZATEN ifade ediyorsa özgüllük kaybı YOK.
        if all(_kimlikte(w) for w in oteki):
            continue
        if len(oteki) > len(kendi) and all(_syn_hit(oteki_metin, w) for w in kendi):
            return str(_terim or _ad), [str(c.get("name"))]
    return None


def _capraz_kup_ikamesi(qn: str, cq: dict, cube_meta: dict,
                        sema: dict) -> tuple[str, list[str]] | None:
    """Soruda anılan bir ölçü terimi cevabın küpünde **yok**, başka küpte **var** mı?

    Döner: `(terim, sahip_küpler)` ya da `None`. ⚠ Terim, cevabın küpünde herhangi bir
    ölçüye eşleşiyorsa `None` döner — ikame değil, **karşılanmış** demektir.
    """
    from app.cube_router import _match_measure

    # Cevabın küpü terimi zaten karşılıyorsa ikame yoktur.
    # ⚠ `§UT` — ama *«karşılıyor mu»* ile *«TAM MI karşılıyor»* aynı soru değildir; ayrımı
    # `_daha_ozgul_sahip` yapar ve bulursa **ayrı bir işaretle** döner.
    if _match_measure(qn, cube_meta)[0]:
        return None
    # 🔴🔴 **AYNI KAVRAM, İKİ AD** — ve beyan bunu göremeyince YALAN SÖYLÜYORDU.
    #
    # ⊙ Canlıda ölçüldü: *«bu yıl toplam duruş dakika»* → `bakim.toplam_durus_dakika`
    # ile **doğru** cevaplandı, ama notta *«toplam durus bu küpte tanımlı değil»*
    # yazdı. Sebep: `toplam durus` aslında `makine_duruslari.toplam_sure_dk`'nın
    # sinonimi — **başka bir ad**, aynı kavram. Ad karşılaştırması onları iki ayrı şey
    # sanıyordu, oysa cevap zaten o kavramı ölçmüştü.
    #
    # Kural: terim, sorguda **zaten bulunan** bir ölçünün — herhangi bir küpteki —
    # sinonimlerine uyuyorsa **karşılanmıştır**. Ad değil **kapsam** kıyaslanır.
    #
    # ⚠ Buradaki birleştirme yalnız **beyan** içindir; eşleştirmeye (routing)
    # dokunmaz. Sinonimleri küplere yaymak onları açgözlü yapardı (`§99.1`) — oysa
    # düzeltilmesi gereken şey bir yönlendirme değil, bir **cümleydi**.
    #
    # 🔴 Asıl kök yine de kataloğun: iki küp aynı kavrama iki ad vermiş (`B8`).
    # Bu kapı o borcu **kapatmaz**, yalnız yanlış beyanı susturur.
    # *Bir yanlışı söylemeyi bırakmak, doğruyu söylemek değildir.*
    # 🔴🔴 `§KB` — **HARMAN BAŞARILI OLDU, BEYAN «İÇERMİYOR» DEDİ.**
    #
    # ⊙ Canlı ölçüm (curl `N` turu, 2026-08-10 · thread tur 2): *«bir de oee ekle»* →
    # çapraz-cube harman **çalıştı**, satırlar `{makine, toplam_fire_kg, ort_oee}` geldi.
    # Ve notun yazdığı cümle şuydu:
    #
    #     ⚠ Sayı doğru ama EKSİK: soruda «oee» geçiyor ama bu cevap onu İÇERMİYOR
    #
    # 🔴 İçeriyordu. Kök: bu yüklem **bayat bir yüzeye** bakıyordu — harmanın ölçüleri
    # `cq["measures"]`'da değil `cq["blend"][*]["measures"]`'dadır. Yani beyan, cevabın
    # **teslim ettiği** kolonları değil, cevabın bir **parçasını** okuyordu.
    #
    # ⊙ Bugün dördüncü kez aynı ders (`§UY/K` · `§ÜK` · `§ÖB` · bu): *önce ölçüm
    # yüzeyinden şüphelen.* Ve `§101.1`: kusur bazen olur, yanlış-pozitif her seferinde.
    #
    # *Bir cevabın neyi içerdiğini, cevabın kendisinden başka bir yere sorarsanız,
    # er ya da geç ona ait olmayan bir eksiklik yazarsınız.*
    _harman = [p for p in (cq.get("blend") or []) if isinstance(p, dict)]
    _harman_kupler = {str(p.get("cube")) for p in _harman if p.get("cube")}
    _mevcut = {str(m) for m in (cq.get("measures") or [])}
    _mevcut |= {str(m) for p in _harman for m in (p.get("measures") or [])}
    if _mevcut:
        for c in (sema.get("cubes") or []):
            _ad2, _ = _match_measure(qn, c)
            if _ad2 and _ad2 in _mevcut:
                return None
    for c in (sema.get("cubes") or []):
        # Harmana katılan bir cube, cevabın küpü kadar **cevabın içindedir**; onu
        # «başka küp» sayan bir döngü kendi teslimatını yabancı ilan eder.
        if c.get("name") == cube_meta.get("name") or c.get("name") in _harman_kupler:
            continue
        _ad, _terim = _match_measure(qn, c)
        if not _ad or _ad in _mevcut:      # `§KB`: harman ölçüleri de «mevcut»tur
            continue
        # 🔴🔴 **`§UY/K` — ÖBEK EŞLEŞMEZ AMA KELİME KAPSANIR: yüklem YANLIŞ-POZİTİF
        # veriyordu ve DOĞRU bir cevabı «eksik» diye etiketliyordu.**
        #
        # ⊙ Canlı ölçüm (curl, 2026-08-10): *«en çok duruşa yol açan 3 nedeni bul»* →
        # `makine_duruslari.toplam_sure_dk` ile **doğru** cevaplandı
        # (`Malzeme/Parti Bekleme · 427.140 dk`) — ama not şunu yazdı:
        #
        #     ⚠ Sayı doğru ama EKSİK: «durus» bu küpte tanımlı değil.
        #
        # 🔴 Oysa kelime **bol bol** kapsanıyor: küp sinonimleri `durus nedeni` ·
        # `durus nedenleri` · `durus sebebi`; ölçü sinonimleri `toplam durus` ·
        # `toplam durus dakikasi`. Sebep: hepsi **çok kelimeli öbek** ve
        # `_match_measure` **tam öbeği** arıyor; soruda öbek geçmiyor, **kelime** geçiyor.
        #
        # ⊙ Doğru yüklem depoda **zaten var**: `partial_unknowns` kapsamayı
        # `_syn_hit_words` ile **kelime düzeyinde** hesaplıyor. İkinci bir kapsama
        # kavramı yazmak `KAT-1` olurdu — o kavram çağrılır.
        #
        # ⚠ Kapı **dar**: yalnız *«bu terim cevabın küpünün sözlüğünde bir kelime mi»*
        # sorulur. Gerçek ikame (`fire` sorup `rework` almak) etkilenmez — `kalite`nin
        # sözlüğünde `fire` diye bir kelime yok, beyan aynen yazılır.
        #
        # *Bir doğru cevaba «eksik» demek, tüm beyanların güvenini aşındırır* (`§101.1`):
        # kusur bazen olur, yanlış-pozitif HER SEFERİNDE yanlıştır.
        if _kup_sozlugunde_kelime(str(_terim or _ad), cube_meta):
            continue
        # 🔴🔴 `§Cİ-boyut` — **BİR TERİMİN SAHİBİ BİR BOYUT DA OLABİLİR.**
        #
        # ⊙ Ölçüldü (curl `Z` turu): *«en yüksek 3 **arıza tipi**»* → cevap
        # `makine_duruslari`'ndan geldi ve beyan *«ariza şu küplerde var: **oee**»* dedi.
        # Oysa `ariza_tipi` **bir boyuttur** ve tek sahibi `bakim`'dir (ölçüldü) —
        # kullanıcı tam da onu arıyordu. Beyan yalnız **ölçü** sahiplerini tarıyordu,
        # yani doğru adresi bilmesine rağmen söylemiyordu.
        #
        # ⚠ Yönlendirme (routing) **değişmedi**: garsonun küp tercihi bir korpus A/B
        # ister ve bu turda ona dokunulmadı. Değişen tek şey, reddin **yanına konan
        # adresin** eksiksiz olması.
        #
        # ⚠ Boyut eşleşmesi `_match_dims` ile (tek sahip); ikinci bir eşleştirici
        # `KAT-1` olurdu.
        #
        # *Bir adresi bilip söylememek, bilmemekten daha az mazur görülür.*
        from app.cube_router import _match_dims

        _olcu_sahip = [str(k.get("name")) for k in (sema.get("cubes") or [])
                       if _match_measure(qn, k)[0]]
        _boyut_sahip = [str(k.get("name")) for k in (sema.get("cubes") or [])
                        if str(k.get("name")) not in _olcu_sahip
                        and str(k.get("name")) != cube_meta.get("name")
                        and _match_dims(qn, k)]
        return str(_terim or _ad), _olcu_sahip + _boyut_sahip
    return None


def _kup_ikamesi(qn: str, cq: dict, sema: dict | None) -> tuple[str, str] | None:
    """🔴🔴 `§Cİ-küp` — **SORU BİR KÜPÜ ADIYLA ÇAĞIRDI, CEVAP BAŞKA BİR KÜPTEN GELDİ.**

    ## Ölçülen kusur (curl `DD` turu, DD-5)

        «bu yıl **bakım** raporu hazırla»
          → başlık *«**Bakım Departmanı** Yıllık Raporu»*, üç bölüm: `ik` (maaş) ·
            `egitim` · `isg` — hepsi `departman` kırılımında, ve **hiçbirinde**
            `departman = Bakım` süzgeci bile yok.

    Katalogda «bakım» `bakim_is_emri` küpünün **cube-düzeyi sinonimidir**. Kullanıcı bir
    **konu alanı** istedi; sistem onu bir **boyut değeri** sandı, sonra o değeri de
    uygulamadı. Sonuç: bakım raporu isteyip **İK raporu** almak.

    ⚠ `route()` bu ayrımı **doğru** yapıyor (ölçüldü, DD-17/DD-18: *«arıza sayısı»* →
    `bakim`, *«bakım maliyeti»* → `bakim_is_emri`). Kusur yalnız **plan/orkestratör**
    yolunda — yani garsonun okuması değil, planlayıcının seçimi.

    ## Yüklem — üç koşul, üçü de katalogdan

    1. Soruda bir **cube-düzeyi sinonim** eşleşiyor (`ilgili_cubelar` — yeniden yazılmaz).
    2. Cevabın küpü o küp **değil**.
    3. Terim bir **süzgeç değeri** olarak da taşınmıyor — *«bakım departmanındaki personel
       sayısı»* meşrudur ve orada `departman = Bakım` süzgeci vardır.

    Üçüncü koşul `§101.1`'in kendisidir: bir terimin cevapta **başka bir biçimde**
    karşılanmış olması, karşılanmamış sayılmaz.

    ⚠ Belge yolunda bu işaret `_BIRLESIM`e girer: bir belgenin kapsamı **bloklarının
    birleşimidir** ve tek bir blok ıskaladı diye belge ıskalamış sayılmaz.

    *Bir konuyu adıyla istemek, o konunun adının bir yerlerde geçmesini istemek değildir.*
    """
    from app import cube_router as _cr

    _kup = str((cq or {}).get("cube") or "")
    if not _kup or not sema:
        return None
    try:
        _ilgili = _cr.ilgili_cubelar(qn, sema)
    except Exception:                     # noqa: BLE001 — beyan susar, tur düşmez
        return None
    _adaylar = [str(c.get("name")) for c in (_ilgili or []) if c.get("name")]
    if not _adaylar or _kup in _adaylar:
        return None
    # Terim bir süzgeç değeri olarak taşınıyorsa karşılanmıştır (`§101.1`).
    _deger_metni = _cr._norm(" ".join(
        str(f.get("value")) for f in (cq.get("filters") or [])
        if not isinstance(f.get("value"), (list, dict))))
    for _ad in _adaylar:
        _c = next((c for c in (sema.get("cubes") or []) if c.get("name") == _ad), None)
        _syn = [str(x) for x in ((_c or {}).get("synonyms") or [])]
        _eslesen = next((x for x in _syn if _cr._syn_hit(qn, x.lower())), None)
        if not _eslesen:
            continue
        if _deger_metni and _cr._syn_hit(_deger_metni, _eslesen.lower()):
            continue                       # süzgeçte taşınıyor → karşılandı
        return _eslesen, _ad
    return None


def _kirilim_ikamesi(qn: str, cq: dict, cube_meta: dict | None,
                     sema: dict | None) -> tuple[str, list[str]] | None:
    """🔴🔴 `§KD-boyut` — **İSTENEN KIRILIM YERİNE BAŞKASI GELDİ, VE SÖYLENMEDİ.**

    ## Ölçülen kusur (curl `BB` turu, 2026-08-11)

        «bu yıl eğitim türüne göre katılım»
          → `egitim` küpü · kırılım **`sonuc`** (BAŞARILI/BAŞARISIZ) · beyan **YOK**

    `egitim`'de bir *tür* boyutu **yok** (ölçüldü: `departman`, `personel_kodu`, `sonuc`)
    ve garson en yakınını seçti. Sayı doğru — ama kullanıcı **tür** kırılımı istedi,
    **sonuç** kırılımı aldı ve bunu anlamasının hiçbir yolu yoktu.

    🔴 Mevcut `kirilim` beyanı bunu **göremez**: o yalnız *hiç boyut taşınamadı* hâlini
    sayar. Burada boyut **var** — yanlış olan. `olcu_ikamesi`'nin boyut eksenindeki
    kardeşi.

    ## Yüklem — katalogdan, sözlüksüz, ve **dar**

    Soruda anılan bir **boyut** (herhangi bir küpte tanımlı) cevabın kırılımında yoksa
    beyan edilir. `§101.1` gereği yanlış-pozitif riski **ölçülerek** sınırlandı: on
    vakalık bir sınamada (dokuzu bu oturumda doğru cevaplanmış gerçek sorular)
    **10/10** doğru — *«araç türüne göre»* bile doğru şekilde **susuyor**, çünkü
    `arac_turu` cevapta zaten var.

    ⚠ Boyutsuz cevaplarda **hiç konuşmaz**: orası `kirilim` beyanının işidir ve aynı
    şeyi iki kez söylemek iki ayrı kusur varmış gibi görünürdü.

    *Bir kırılımı sessizce başkasıyla değiştirmek, sorulmayan bir soruyu cevaplamaktır.*
    """
    from app import cube_router as _cr
    from app.cube_router import _match_dims

    boyutlar = [str(d) for d in (cq.get("dimensions") or [])]
    if not boyutlar or not sema:
        return None
    # 🔴🔴 **KIRILIM NİYETİ ARANMADAN BEYAN EDİLMEZ — iki canlı yanlış-pozitif öğretti.**
    #
    # ⊙ Ölçüldü (curl `CC` turu, CC-20/CC-21):
    #     «son 2 yıl **satış** raporu hazırla» → «satış» ⊂ «satış temsilcisi» → beyan konuştu
    #     «bir de fire oranı **bölüm**ü ekle»  → «bölüm» = *raporun bölümü* → beyan konuştu
    #
    # İkisinde de kullanıcı bir **kırılım istemedi**. İlk yazımın yüklemi *"soruda bir
    # boyut adı geçiyor"*du — ama bir boyut adının cümlede geçmesi, o kırılımın
    # **istendiği** anlamına gelmez: «satış» çok-sözcüklü bir etiketin parçası, «bölüm»
    # ise **belgenin kendi yapı adı**. `§101.1`: yanlış pozitif kusurun kendisinden pahalı.
    #
    # ⚠ Ayrım **yeniden yazılmadı, ÇAĞRILDI**: `kirilim_istendi` yüklemi `niyet.py:311`'de
    # zaten var ve *«son 3 ay'a göre»* tuzağına karşı `gore_donem_mi` ile korumalı. Bu
    # deponun defterinde `göre`/`bazında` aşırı-yüklenmesi **üç kez** ısırdı; dördüncüsü
    # için ikinci bir tanıyıcı yazmak `KAT-1`'i çiğnemek olurdu.
    #
    # ⚠ Bedeli **bilinerek** ödeniyor: işaretsiz bir gerçek vaka («eğitim türü katılım»)
    # artık **susar**. Ölçülen sayı bunu haklı çıkarıyor — iki yanlış-pozitife karşı bir
    # doğru-pozitif, ve o doğru-pozitif işareti **taşıyor** («türüne **göre**»).
    #
    # *Bir sözcüğün cümlede bulunması, onun istendiğine dair bir kanıt değildir.*
    try:
        _kirilim_istendi = (_cr._herhangi(qn, _cr._BREAKDOWN_HINTS)
                            and not _cr.gore_donem_mi(qn))
    except Exception:                     # noqa: BLE001 — beyan susar, tur düşmez
        _kirilim_istendi = False
    if not _kirilim_istendi:
        return None
    # 🔴🔴 **ÖNCE HEPSİNİ TOPLA, SONRA KARAR VER — ve bunu canlı ölçüm öğretti.**
    #
    # ⊙ İlk yazımda ilk eşleşen küpte **dönülüyordu** ve canlıda şu çıktı:
    # *«araç türüne göre nakliye maliyeti»* → cevap `arac_turu` kırılımında (**doğru**)
    # ama beyan *«tür bu küpte tanımlı değil»* dedi — çünkü döngü `sevkiyat`a gelmeden
    # `bakim_is_emri.tur`'u bulup dönmüştü.
    #
    # ⚠ Ve **çevrimdışı prob'um bunu kaçırmıştı**: orada küp sırası farklıydı ve erken
    # dönüş doğru cevabı veriyordu. *Sıraya bağlı bir yüklem, sırası değişen her yerde
    # başka bir şey söyler.*
    #
    # Kural: soruda anılan **bütün** boyut adayları toplanır; **herhangi biri** cevapta
    # varsa susulur (`§101.1`).
    _var = set(boyutlar)
    _adaylar: list[str] = []
    for c in (sema.get("cubes") or []):
        _adaylar.extend(_match_dims(qn, c))
    if any(d in _var for d in _adaylar):
        return None
    for d in _adaylar:
        if d not in _var:
            sahipler = [str(k.get("name")) for k in (sema.get("cubes") or [])
                        if d in (k.get("dimensions") or [])]
            # ⚠ Etiket **sahibin** kataloğundan okunur, cevabın küpünden değil: cevabın
            # küpünde o boyut zaten **yok** (kusurun kendisi bu) ve orada etiket aramak
            # her seferinde teknik ada düşerdi (`tur` ↔ `tür`).
            # *Bir şeyin adını, onu tanımayan yere sormak, adını kaybetmektir.*
            _lbl = next((((k.get("dimension_labels") or {}).get(d))
                         for k in (sema.get("cubes") or [])
                         if (k.get("dimension_labels") or {}).get(d)), d)
            return str(_lbl), sahipler
    return None


def denetle(q: str, cq: dict, cube_meta: dict | None = None,
            sema: dict | None = None) -> list[Ihlal]:
    """Sorudaki niyet işaretlerinin **sorguda karşılığı var mı?**

    🔴 Boş liste = uyumlu. Dolu liste = **sessiz-yanlış adayı**: cevap üretildi ama
    kullanıcının istediği bir şey sorguya **taşınmadı**.

    ⚠ Kapı **fail-closed değil, BEYAN-AÇIK**: cevabı öldürmez, **etiketler** (KÖK-3).
    Öldürmek kapsamı daraltırdı; etiketlemek daraltmaz ama sessizliği bitirir.
    """
    from app.cube_router import _PERIOD_RANGE_REF, _TOPN_CUE, _time_gran
    from app.niyet import TUR_KIYAS, coz_soru

    out: list[Ihlal] = []
    qn = _norm(q or "")

    # 🔴 KÖK-1 FAZ 2 — SORU TARAFI ARTIK **NİYET NESNESİNDEN** OKUNUYOR.
    #
    # Bu modül soruyu yedi kez ayrı ayrı tarıyordu (`compare_mode` · `_cok_donem` ·
    # `_TREND` · `_BREAKDOWN_HINTS` · `_ustunluk_mu` · `_measure_threshold` ·
    # `_EXCLUDE_MARKERS`). Raporun KÖK-1'i *"çözümleme ile eşleştirme ayrılsın"* der ve
    # bu modül **ilk müşteridir** (*"KÇ-1, KÇ-0'ın ilk müşterisidir"*).
    #
    # ⊙ Göç ÖLÇÜLDÜ, tahmin edilmedi: **2 270** korpus sorusunda yedi sinyalin
    # **YEDİSİ DE** birebir aynı çıktı (`test_kok1_niyet.py::test_FAZ2_ESDEGERLIK`).
    # *Bir göçün ilk adımı, iki tarafın aynı şeyi söylediğini kanıtlamaktır.*
    #
    # ⚠ ÜSTÜNLÜK **taşınMADI** ve bu bir eksik değil bir SINIR: `_ustunluk_mu` burada
    # `ic`+`cube_meta` ile çağrılır çünkü ipucu bir **ölçü adının içindeyse** ipucu
    # değildir (`kur` cube'unun ölçüsü literal olarak *"en yüksek kur"*; 525 meşru
    # soruda 10 yanlış-pozitif buradan geliyordu). O denetim **eşleştirme** tarafıdır ve
    # şemasız bir çözümlemede yapılamaz. *Ayrımın doğru yeri, ayrımın kendisi kadar
    # önemlidir: yanlış yerden bölünen bir sorumluluk iki yerde de eksik kalır.*
    niyet = coz_soru(q or "")

    # 🔴 `route()` bir SARMALAYICI döndürür: `{cube_query: {...}, measure, order, limit,
    # period_optional}`. İlk yazımda doğrudan `cq.get("dimensions")` okundu ve **her
    # kırılımlı soru** ihlal verdi (`bu yıl makine bazında oee` → «kırılım yok»).
    #
    # ⚠ Bu, bu deponun kendi defterindeki **"bir alan adını okumadan yazmak"** sınıfı —
    # ve bir kapı içinde en tehlikeli hâli: kapı, koruduğu şeyi bozuk ölçer ve kimse
    # fark etmez, çünkü kapı **kırmızı** verir ve kırmızı "çalışıyor" gibi görünür.
    # *Bir sözleşmeyi okumadan denetleyen kapı, denetlediğini sanır.*
    disi = cq or {}
    ic = disi.get("cube_query") if isinstance(disi.get("cube_query"), dict) else disi
    filtreler = ic.get("filters") or []
    boyutlar = ic.get("dimensions") or []
    siralama = (disi.get("order") or disi.get("limit") or ic.get("order")
                or ic.get("limit") or ic.get("entity_limit"))
    # 🔴🔴 **`§R1` — SIRALAMA İLE KESME AYNI YÜKLEMDE BİRLEŞTİRİLMİŞTİ (9 kanıt).**
    #
    # `siralama` yukarıda beş alanın **herhangi biri** doluysa doğrudur. Sonuç: `order`
    # kondu ama `limit` konmadıysa sistem *"bir şey yaptım"* sayıp **susuyor** — oysa
    # kullanıcı bir **SAYI** vermişti.
    #
    # Ölçüldü (R turu, `r11`): `bu yıl en çok rework yapılan **3** makineyi bul` →
    #
    #     "üstünlük: sıralama sistem tarafından tamamlandı"
    #     niyet: üstünlük=3        cq: order ✅  limit ✗       →  **11 SATIR**
    #
    # ve **hiçbir beyan yok**. Aynı desen `r16` [EN] (`5 customers`) · `r4` (*"üç
    # müşteri"* — sayı **yazıyla**) · `p18` [EN] (`top 3`). Dört kanıt yalnız bu sınıfta.
    #
    # 🔴 Ve `§34`'ün kendi öğüdü bir **söz**dür: *"«en yüksek 5 makine» gibi sayı verirsen
    # sıralayıp **KESERİM**."* Sistem sıralıyor, kesmiyor, ve sözünü tutmadığını
    # söylemiyor.
    #
    # ⚠ Yeni sözlük **yok**: kesme talebi `niyet.ustunluk`'tan okunur — sistemin **zaten
    # hesapladığı** sayı. İki alanı karşılaştırmak, üçüncü bir alan uydurmaktan farklıdır.
    #
    # *Bir sözü yarım tutmak, hiç tutmamaktan daha sessizdir.*
    # 🔴 **VE İLK YAZIMIM YALAN SÖYLEDİ — kendi ölçümüm yakaladı (üç koşum).**
    #
    # Yüklem yalnız `limit`/`entity_limit` alanlarına bakıyordu. Ama `entity_limit`
    # **çözülünce alan olmaktan çıkar**: `ask.py::_resolve_entity_limit` onu sıralanan
    # boyut üzerinde bir **değer filtresine** dönüştürür ve alan `cq`'dan düşer. Ölçüldü:
    #
    #     satır=3  limit=None  entity_limit=False  filtre_boyut=['makine']  → BEYAN ATEŞLEDİ
    #     satır=3  limit=3     entity_limit=False  filtre_boyut=[]          → susar (doğru)
    #
    # Yani **kesme yapılmışken** sistem *"kesemedim"* diyordu — bir beyan olarak
    # **beyansızlıktan kötü**, çünkü doğru bir cevabı eksik ilan ediyor.
    #
    # ⚠ Ölçüt kesmenin **izine** bakar, alanına değil: sıralanan boyut üzerinde bir değer
    # filtresi varsa kesme **gerçekleşmiştir**. Yanlış-negatif tarafı güvenlidir
    # (kullanıcının kendi koyduğu bir boyut filtresi de beyanı susturur — susmak,
    # uydurmaktan iyidir).
    #
    # *Bir kusuru ilan eden yüklem, kendi yanlış-pozitifini üretirse, ilan ettiği kusurdan
    # daha pahalıdır.*
    _kesme_izi = any(f.get("dimension") in boyutlar for f in filtreler)
    kesme = (disi.get("limit") or ic.get("limit") or ic.get("entity_limit")
             or _kesme_izi)

    # 0 · GRUP BAŞINA ÜSTÜNLÜK — *«HER makinede en kötü vardiya»*
    #
    # 🔴🔴 **`§HB` — «her <boyut>» SESSİZCE GLOBAL TEK SATIRA İNDİRGENİYOR.**
    #
    # ⊙ Ölçüldü (canlı `XII`, iki soru):
    #
    #   | soru | üretilen | dönen |
    #   |---|---|---|
    #   | *«**her makinede** en kötü vardiya»* | `dims:[makine,vardiya] · order · limit 1` | **1 satır** |
    #   | *«**her vardiyada** en kötü makine»* | aynı | **1 satır** |
    #
    # Kullanıcı **11 makine için 11 satır** bekliyor; **bir** satır alıyor — ve rozet
    # `source=cube`, **beyan yok**. Yani doğru gibi görünen bir cevap, sorulan sorunun
    # onda birini karşılıyor.
    #
    # ⚠ Bu bir **ifade edememe**dir, bir eşleşme hatası değil: grup başına sıralama bir
    # **pencere fonksiyonu** ister ve `CubeQuery` onu taşımıyor. Yani düzeltme bu turda
    # bir **beyandır** — cevabı öldürmez, **etiketler** (`KÖK-3`'ün disiplini).
    #
    # ⚠ Yüklem dar: `her` **bir boyut adının önünde** olmalı (kapalı sınıf: Türkçede
    # `her` bir belgisiz sıfattır) **ve** sorguda bir kesme (`limit`) bulunmalı. *«her
    # zaman»* · *«her ay»* gibi kullanımlar bir boyut adı taşımadığı için giremez.
    #
    # *Bir soruyu onda bir cevaplamak, cevaplamamaktan yalnızca daha ikna edicidir.*
    if _grup_basina_istendi(qn, boyutlar) and (disi.get("limit") or ic.get("limit")):
        out.append(Ihlal(
            isaret="grup_basina",
            aciklama=("**her** dedin — yani grup başına bir sonuç istedin; ama "
                      "üretebildiğim şey **tek** bir satır (genel en iyi/en kötü)."),
            oneri=("Grup başına sıralama (her makinenin kendi en kötü vardiyası) v1'de "
                   "yok. Tek bir grubu sorarsan tam cevap veririm: *«RAM-2'de vardiya "
                   "kırılımı»*.")))

    # 0b · ÇAPRAZ-KÜP ÖLÇÜ İKAMESİ — *«fire sordu, rework aldı»*
    #
    # 🔴🔴 `§Cİ` — **KAPSAMA DENETİMİ KÜP-YERELDİ; CEVAP KÜP DEĞİŞTİRİNCE TERİM
    # İZSİZ KAYBOLUYORDU.**
    #
    # ⊙ Ölçüldü (canlı, `A9` sayacının açtığı iz): *«bu yıl **fire** neden arttı sebep
    # kırılımında göster»* → cevap `kalite.rework_sayisi`. Kullanıcı **fire** sordu,
    # **rework** aldı ve **hiçbir beyan yoktu**.
    #
    # ⊙ Sebep ölçüldü: `_match_measure("…fire…", kalite)` → `(None, None)`. Yani
    # düşen-ölçü sayacı terimi **göremiyor**, çünkü yalnız **cevabın küpüne** bakıyor.
    # Terim başka bir küpün ölçüsü olduğunda sayaç onu hiç saymıyor.
    #
    # ⚠ Yüklem dar: terim cevabın küpünde **hiçbir ölçüye** eşleşmemeli **ve** başka
    # bir küpte bir ölçüye eşleşmeli. Cevap o terimi başka adla karşılıyorsa (`fire`
    # → `fire_orani_yuzde`) `_match_measure` onu bulur ve beyan **yazılmaz**.
    # `§101.1`: yanlış bir *«eksik»*, doğru bir cevabı kusurlu gösterir.
    #
    # *Bir terimi yalnız cevabın küpünde aramak, cevabın küp değiştirdiği anı görmemeyi
    # seçmektir.*
    if sema and cube_meta:
        # 🔴 `§UT` — **ÖNCE ÖZGÜLLÜK, SONRA İKAME.** Sıra bilinçli: bir tamlamanın
        # niteleyeni düşmüşse ortada bir *ikame* yoktur (cevap kavramı ölçüyor), bir
        # **özgüllük kaybı** vardır ve cümlesi başkadır. Ters sırada `_capraz_kup_ikamesi`
        # zaten `None` döneceği için bu dal hiç konuşamazdı.
        _ozgul = _daha_ozgul_sahip(qn, cube_meta, sema)
        if _ozgul:
            _terim2, _sahip2 = _ozgul
            out.append(Ihlal(
                isaret="olcu_ozgullugu",
                aciklama=(f"Soruda **«{_terim2}»** geçiyor ama bu cevap onun yalnız bir "
                          f"**parçasıyla** hesaplandı — daha özgül bir karşılık var."),
                oneri=(f"**«{_terim2}»** için {', '.join(_sahip2[:2])} küpünü "
                       f"sorabilirsin; oradaki ölçü tam olarak bunu ölçüyor."),
                # `§TZ` — *«sorabilirsin»* demek yetmez, **sorulabilir** yapmak gerekir.
                # ⊙ Ölçüldü: `«bakım maliyeti raporu hazırla»` 6/6 genel küpe gidiyor ve
                # beyan her seferinde doğru sahibi **adıyla** söylüyordu — ama kullanıcı
                # onu **yazmak** zorundaydı. `§TZ`'nin dersi burada da geçerli.
                chip={"label": f"{_terim2} ({_sahip2[0]})",
                      "query": f"{_sahip2[0]} {_terim2}", "kind": "olcu"}))
        _ikame = _capraz_kup_ikamesi(qn, ic, cube_meta, sema)
        if _ikame:
            _terim, _sahipler = _ikame
            out.append(Ihlal(
                isaret="olcu_ikamesi",
                aciklama=(f"Soruda **«{_terim}»** geçiyor ama bu cevap onu **içermiyor** — "
                          f"«{_terim}» bu küpte tanımlı değil."),
                oneri=(f"«{_terim}» şu küplerde var: {', '.join(_sahipler[:3])}. "
                       f"Onu ayrıca sorabilirsin; aynı kırılımda birleştirmek her zaman "
                       f"mümkün olmayabilir."),
                # 🔴 `§Cİ-chip` — **KARDEŞİNDE VAR, BURADA YOKTU.**
                #
                # ⊙ Ölçüldü (curl `U` turu, U7): *«enerji maliyeti en yüksek 5 makine»*
                # → beyan hem kusuru hem sahibini **adıyla** söylüyor (*«maliyet şu
                # küplerde var: maliyet, surdurulebilirlik»*) ve `suggestions` **boş**.
                # Kullanıcı doğru cevabın adresini görüyor ama oraya **yazarak** gitmek
                # zorunda.
                #
                # `§TZ`'nin dersi (*«sorabilirsin» demek yetmez, **sorulabilir** yapmak
                # gerekir*) kardeş beyanda (`olcu_ozgullugu`) uygulanmış, burada
                # uygulanmamıştı — yine *bir kural yalnız bir dalda geçerliyse o kural
                # değil bir tesadüftür*.
                #
                # ⚠ Chip metni **tek sahipten** üretilir (`sahipler[0]`), ki tıklama
                # gerçekten o küpe çıksın; doğrulama `chipler()`'in kendi işi.
                chip=({"label": f"{_terim} ({_sahipler[0]})",
                       "query": f"{_sahipler[0]} {_terim}", "kind": "olcu"}
                      if _sahipler else None)))

    # 1 · KIYAS — "şubata göre", "geçen yılla kıyasla"
    #
    # 🔴 **`§67` — «KIYASLA» HER ZAMAN İKİ DÖNEM DEMEK DEĞİLDİR (8 kanıt).**
    #
    # Ölçüldü: `ciro ile kar marjını makine bazında **kıyasla**` → *«iki dönemi
    # kıyaslamanı istedin ama tek bir toplam üretebildim»*. Kullanıcı **iki ölçüyü**
    # kıyaslamak istedi; ortada dönem yok. Aynı desen `i7`·`d9`·`f2`·`g10`… sekiz kez.
    #
    # 🔴 Ve `Ö10`'un kuralı burada da geçerli: **yanlış bir beyan sessizlikten kötüdür** —
    # sistem kullanıcıya **onun söylemediği bir şeyi söylediğini** söylüyor.
    #
    # ⊙ Ayrım **yapısal**: kıyasın **nesnesi** ne? Sorguda **iki ya da daha çok ölçü**
    # varsa ve soru birden çok dönem saymıyorsa (`cok_donem` yok), o kıyas **ölçüler
    # arasıdır** ve sorguda **zaten karşılanmıştır** — iki ölçü yan yana duruyor.
    #
    # ⚠ Dar tutuldu: yalnız `cok_donem` **yokken** ve `cq` **çok ölçülüyken** susar.
    # `geçen yıla göre kıyasla` (tek ölçü, iki dönem) aynen ihlal sayılır.
    #
    # *Bir kıyasın eksik olduğunu söylemeden önce, neyin kıyaslandığına bakmak gerekir.*
    # 🔴🔴 **`§Z2` — İKİ ÖLÇÜ İSTENDİ, BİRİ VERİLDİ, HİÇBİR ŞEY SÖYLENMEDİ.**
    #
    # Ölçüldü (`Z18`, canlı — *«bu yıl aylık toplam **elektrik ve su** tüketimi»*):
    #
    #     niyet: ölçü=2          cq.measures: ["toplam_su_lt"]        beyan: YOK
    #
    # ⊙ Kullanıcı iki şey istedi, birini aldı ve **bunu cevaptan anlayamaz**: eksik olan
    # sütun görünmez, çünkü orada olmayan bir şeyin izi yoktur. `§98.1` bu yüzden yazıldı
    # (*eksikliği ADIYLA say*) ama ölçü sayısı sayılmıyordu — dönem sayısı, kıyas, oran,
    # sıralama ve kesme sayılıyordu, **ölçünün kendisi** değil.
    #
    # 🔴 **Ve ham sayı sayılamaz** (`§101.1`): `olcu_adaylari` `(cube, ölçü)` çiftleridir;
    # tek bir kelime iki küpte eşleşince aday sayısı **2** olur ve *"iki ölçü istedin"*
    # demek her eş-adlılıkta bir yanlış-pozitif üretirdi. Bu yüzden sayım **cevaplayan
    # küple sınırlı**: aynı küp içinde adı geçen **farklı** ölçüler.
    #
    #     «elektrik ve su» → surdurulebilirlik içinde {enerji, su} = 2 ✅ beyan
    #     «fire»          → parti içinde {toplam_fire_kg}          = 1 ✅ sessiz
    #
    # ⚠ Cevap **öldürülmez** (`KÖK-3`): ihlal etiketler, susturmaz.
    #
    # *Bir cevabın eksik olduğunu ancak istenenle karşılaştırarak bilebilirsiniz; ve
    # istenen, sistemin kendi kataloğunda kaç ADI olduğuyla değil, kaç ŞEY olduğuyla ölçülür.*
    # ⚠ Kaynak `niyet.olcu_adaylari` **DEĞİL**: o alan şemayı bilen ayrı bir adımda
    # doldurulur ve `denetle`'nin çağırdığı `coz_soru(q)` onu **boş** bırakır — ilk yazımda
    # bunu varsaydım, sondaj (4 vaka) beyanın hiç ateşlemediğini gösterdi. Elde olan
    # `cube_meta`'dır ve cevabı **o** taşıyor. *Bir alanın var olması, dolu olması değildir.*
    # ⚠ Eşleşme **`_syn_hit`** ile: alt-dize taraması bu kararı veremez (`KÖK-7a`) —
    # bir beyanın yanlış-pozitifi, beyan ettiği kusurdan pahalıdır (`§101.1`). Çekimin
    # tek sahibi `cube_router`'dır ve buraya **ikinci bir kopya yazılmaz**; tembel import
    # `yetenek.py`'nin desenidir (döngüyü kırar, kuralı tekleştirir).
    from app.cube_router import _syn_hit as _sh

    # 🔴 **İÇ İÇE SİNONİM — ve bu modülün KENDİ notu bunu zaten söylüyordu:**
    # *"Bir ipucu, başka bir şeyin adının içindeyse, ipucu değildir."* (`_olcu_araliklari`)
    #
    # Sondaj (ilk yazımda) kusuru **sevk edilmeden** yakaladı: *«vardiya bazında **fire
    # oranı**»* → `fire_orani_yuzde` ✓ **ve** `toplam_fire_kg` (sinonimi `fire`) → sistem
    # *"soruda 2 ölçü geçiyor"* diye **yanlış** beyan üretti. Kullanıcı tek bir şey
    # istemişti. `§101.1` birebir: bir kusuru ilan eden yüklem, kendi yanlış-pozitifini
    # üretirse ilan ettiği kusurdan pahalıdır.
    #
    # ⊙ Çözüm `_match_cube`'un kuralının aynısı: **en uzun eşleşme kazanır.** Bir ölçünün
    # bütün eşleşmeleri, başka bir ölçünün **daha uzun** eşleşmesinin içinde kalıyorsa o
    # ölçü sayılmaz. Yeni bir kural değil, var olan kuralın bu karara **uygulanmasıdır**.
    _verilen_olculer = {m for m in (ic.get("measures") or []) if m}
    _esles: dict[str, list[tuple[int, int]]] = {}
    for _m, _syns in ((cube_meta or {}).get("measure_synonyms") or {}).items():
        for _s in (_syns or []):
            _t = _norm(str(_s).removesuffix("!"))
            if len(_t) >= 3 and _sh(qn, _t):
                for _mt in re.finditer(re.escape(_t), qn):
                    _esles.setdefault(_m, []).append(_mt.span())
    _istenen_olculer = {
        _m for _m, _sp in _esles.items()
        if any(not any(_o != _m and any(_b <= _s2 and _e2 <= _e and (_e - _b) > (_e2 - _s2)
                                        for _b, _e in _oth)
                       for _o, _oth in _esles.items())
               for _s2, _e2 in _sp)}
    # 🔴🔴 `§ÖB` — **BİRLEŞİM KUSURUN KENDİSİYDİ: sistemin SEÇTİĞİ ölçü, kullanıcının
    # İSTEDİĞİ sayılıyordu.**
    #
    # ⊙ Canlı ölçüm (curl turu, 2026-08-10): *«bu yıl en kötü fire»* →
    # `fire_orani_yuzde` ile **doğru** cevaplandı (RAM-2 · %22,12), ama not:
    #
    #     ⚠ Sayı doğru ama EKSİK: soruda **2 ölçü** geçiyor ama cevapta **1** var —
    #     `toplam_fire_kg` rapora girmedi.
    #
    # Kullanıcı **bir** şey söyledi: *«fire»*. Sinonimler ayrık:
    # `toplam_fire_kg → ['fire', …]` · `fire_orani_yuzde → ['fire orani', …]`, ve soruda
    # *«fire orani»* **geçmiyor**. Yani sinonim eşleşmesi tek bir ölçü buluyordu —
    # ikinciyi **birleşim** ekliyordu (`| _verilen_olculer`), yani **cevabın kendisi**.
    #
    # 🔴 Sonuç bir öz-referans: sistemin seçimi *«istenen»* kovasına giriyor, sonra o
    # kovayla kıyaslanıyor ve **her zaman** bir eksik çıkıyor.
    #
    # ⚠ Birleşim gereksizdi: kullanıcının **adıyla andığı** bir ölçü zaten `_esles`
    # tarafından yakalanır. Birleşimin eklediği tek şey, **kullanıcının hiç anmadığı**
    # ölçülerdi — ve onlar tanım gereği *«istenen»* değildir.
    #
    # ⊙ Kullanıcı *«fire»* deyip `fire_orani_yuzde` almışsa bu **bir ikame beyanıdır**
    # ve o eksenin kendi kapısı var (`§Cİ`/`olcu_ikamesi`) — burada değil.
    #
    # *Bir talebi, cevabın kendisinden türetmek; sınavı kendi cevap anahtarından
    # yazmaktır.*
    if len(_istenen_olculer) >= 2 and len(_verilen_olculer) < len(_istenen_olculer):
        _dusen = sorted(_istenen_olculer - _verilen_olculer)
        _ad = ", ".join(f"`{_m}`" for _m in _dusen)
        out.append(Ihlal(
            "olcu_dustu",
            f"soruda **{len(_istenen_olculer)} ölçü** geçiyor ama cevapta "
            f"**{len(_verilen_olculer)}** var — {_ad} rapora girmedi",
            "Düşen ölçüyü ayrıca sorabilirsin; ya da takip turunda "
            "*«… ölçüsünü de ekle»* diyerek aynı rapora ekletebilirsin."))

    _olcu_kiyasi = (len([m for m in (ic.get("measures") or []) if m]) >= 2
                    and not niyet.cok_donem)
    if (TUR_KIYAS in niyet.turler and not _olcu_kiyasi
            and not (ic.get("compare") or ic.get("compare_mode"))):
        out.append(Ihlal(
            "kiyas",
            "iki dönemi **kıyaslamanı** istedin ama tek bir toplam üretebildim",
            "İki dönemi ayrı ayrı sorabilirsin; ya da *«geçen yıla göre»* diyerek "
            "dönemsel kıyası açıkça isteyebilirsin."))

    # 2 · ÇOK-DÖNEM — "ocak ve haziran", "2025 ve 2026"
    #    ⚠ Kıyas ihlali zaten yazıldıysa tekrar etme: aynı kaybı iki kez anlatmak,
    #    kullanıcıya iki ayrı sorun varmış gibi görünür.
    # ⚠ Aralık işareti varsa iki dönem adı tek bir aralığın UÇLARIDIR — ihlal yok.
    #
    # 🔴 İlk yazımda buna bir de *"route zaten gte+lte kurduysa niyet taşınmıştır"*
    # şartı eklenmişti ve **hedefi kaçırdı**: `ocak ve haziran ciro karşılaştır`
    # sorusunda route iki dönemi TEK aralığa (1 Ocak – 30 Haziran) çöküyor ve o da
    # gte+lte üretiyor. Yani "iki uçlu filtre" hem doğru aralığın hem YANLIŞ çöküşün
    # imzası — ayırt edici değil.
    # *Bir imza, iki farklı olayda da görünüyorsa kanıt değildir.*
    _pad = f" {qn} "
    _aralik_ifadesi = any(w in _pad for w in _ARALIK) or (
        any(w in _pad for w in _ARALIK_BAGLAC) and TUR_KIYAS not in niyet.turler)
    # FAZ O-6 — SISTEM AYIRDI AMA BEYAN HALA "TOPLADIM" DIYORDU.
    #
    # Olculdu (canli, O-6 duzeltmesinden HEMEN SONRA): "bu yil ocak ve haziran ayinda
    # fire orani" -> 2 SATIR dondu (ocak %20,47 + haziran) ve yaninda su cumle vardi:
    #     "birden cok donem saydin ama tek bir ARALIK olarak topladim"
    #
    # Cevap DOGRUYDU, beyan YANLISTI. Ve bu, beyan katmaninin en pahali hatasi: dogru bir
    # cevabi kusurlu ilan etmek (§X3'un aynisi, bir kat yukarida). Kullanici sayilara
    # bakip "demek ki eksik" diye dusunur — oysa tam da istedigi sey elindedir.
    #
    # Kok: yuklem yalnizca NIYETI (cok_donem) okuyordu, CEVABIN NE YAPTIGINI okumuyordu.
    # `ayrik_aylar` isareti tam olarak "bu cevap donemleri AYIRDI" demektir.
    #
    # *Bir eksigi ilan etmeden once, cevabin onu zaten karsilayip karsilamadigina
    # bakmak gerekir.*
    _ayirdi = bool(ic.get("ayrik_aylar"))
    if (niyet.cok_donem and not _aralik_ifadesi and not _ayirdi
            and not any(i.isaret == "kiyas" for i in out)
            and not (ic.get("compare") or ic.get("compare_mode"))):
        out.append(Ihlal(
            "cok_donem",
            "birden çok dönem saydın ama tek bir **aralık** olarak topladım",
            "Dönemleri ayrı ayrı sorarsan her birini tek tek veririm."))

    # 3 · TREND — zaman ekseni ister
    if niyet.trend_istendi and not (_time_gran(qn) or _zaman_ekseni_var(ic, cube_meta)):
        out.append(Ihlal(
            "trend",
            "**değişimi/trendi** istedin ama tek bir toplam ürettim — zaman ekseni yok",
            "*«aylara göre»* ya da *«çeyreklere göre»* eklersen zaman ekseninde çizerim."))

    # `§Cİ-küp` — soru bir küpü **adıyla** çağırdıysa ve cevap başka küptense söylenir.
    _kupi = _kup_ikamesi(qn, ic, sema)
    if _kupi:
        _kterim, _ksahip = _kupi
        out.append(Ihlal(
            isaret="kup_ikamesi",
            aciklama=(f"Soruda **«{_kterim}»** geçiyor ve bu katalogda **{_ksahip}** "
                      f"konusudur — ama bu cevap **{ic.get('cube')}** küpünden geldi."),
            oneri=(f"«{_kterim}» konusunu **{_ksahip}** küpünde sorabilirsin."),
            chip={"label": f"{_kterim} ({_ksahip})", "query": f"{_ksahip} {_kterim}",
                  "kind": "olcu"}))

    # `§KD-boyut` — istenen kırılım yerine başkası geldiyse **söylenir** (gövde yukarıda).
    _ki = _kirilim_ikamesi(qn, ic, cube_meta, sema)
    if _ki:
        _kt, _ksah = _ki
        out.append(Ihlal(
            isaret="kirilim_ikamesi",
            aciklama=(f"Soruda **«{_kt}»** kırılımı geçiyor ama bu cevap "
                      f"**{', '.join(str(b) for b in (ic.get('dimensions') or []))}** "
                      f"kırılımında hesaplandı — «{_kt}» bu küpte tanımlı değil."),
            oneri=((f"«{_kt}» şu küplerde bir boyut: {', '.join(_ksah[:3])}. "
                    f"Orada sorabilirsin.") if _ksah else
                   f"«{_kt}» diye bir kırılım katalogda yok."),
            chip=({"label": f"{_kt} ({_ksah[0]})", "query": f"{_ksah[0]} {_kt}",
                   "kind": "olcu"} if _ksah else None)))

    # 4 · KIRILIM — mevcut korumanın genelleştirilmiş hâli
    if (niyet.kirilim_istendi and not boyutlar
            and _time_gran(qn) is None and not _PERIOD_RANGE_REF.search(qn)):
        out.append(Ihlal(
            "kirilim",
            "bir **kırılım** istedin ama sorguya bir boyut taşıyamadım",
            "Kırılım adını açıkça yazarsan (*«makine bazında»*) uygularım."))

    # 5 · ÜSTÜNLÜK — "en yüksek 5", "en çok"
    if _ustunluk_mu(qn, _TOPN_CUE, ic, cube_meta) and not siralama:
        out.append(Ihlal(
            "ustunluk",
            "**en yüksek/en çok** dedin ama sıralama uygulayamadım",
            "*«en yüksek 5 makine»* gibi sayı verirsen sıralayıp keserim."))
    # 🔴🔴 `§ÜK` — **SIRALAMA VAR AMA KIRILIM YOK: «hangisi» sorusuna «ne kadar» cevabı.**
    #
    # ⊙ Canlı ölçüm (curl turu, 2026-08-10):
    #
    #     «bu yıl en yüksek enerji tüketimi» → {elektrik_tuketimi_kwh: 5.500.126}
    #     cq: order desc · dimensions: YOK · beyan: YOK
    #
    # Kullanıcı **hangisi** diye sordu, sistem **ne kadar** diye cevapladı. `order desc`
    # tek satırlık bir toplamın üstünde çalıştı — yani bir **yok-işlem**, ama cevapta
    # sıralanmış bir sonuç gibi duruyor.
    #
    # 🔴 Yukarıdaki `ustunluk` beyanı bunu **göremiyor**: o yalnız *sıralama hiç
    # yapılamadı* durumunu sayıyor. Burada sıralama **yapıldı** — anlamsız bir yerde.
    #
    # ⚠ Ve sistem aynı soruyu bazen **doğru** ele alıyor: *«bu yıl en iyi kâr marjı»* →
    # *«Hangi kırılımı istiyorsun?»* (garson kırılımda uyuşamadı → netleştirme). Yani
    # davranış **tutarsızdı**: aynı şekildeki soru bir yolda soruluyor, ötekinde
    # sessizce toplamla cevaplanıyordu.
    #
    # ⚠ Yanlış-pozitif kapısı (`§101.1`): `timeDimensions` de bir **kırılımdır**
    # (*«en yüksek aylık ciro»* → ay ay sıralanır). İkisinden biri varsa beyan **yazılmaz**.
    #
    # *Bir üstünlük sorusu bir SEÇİM ister; seçilecek bir küme yoksa cevap bir sayı
    # değil, bir yanlış anlamadır.*
    if (niyet.ustunluk_istendi or niyet.ustunluk) and siralama \
            and not (ic.get("dimensions") or ic.get("timeDimensions")):
        out.append(Ihlal(
            "ustunluk_kirilimsiz",
            "**en yüksek/en kötü** dedin ama cevapta bir **kırılım yok** — bu tek bir "
            "**toplam**, sıralanacak bir liste değil",
            "Neye göre sıralayayım? *«makine bazında»* · *«müşteri bazında»* · "
            "*«aylık»* yazarsan hangisi olduğunu gösteririm."))
    # `§R1` — SAYI VERİLDİ, KESİLMEDİ. Yukarıdaki beyandan **ayrı** bir kusurdur:
    # orada sıralama hiç yapılamamıştır, burada yapılmış ama **sayı tutulmamıştır**.
    # `§SR` — sayı bir değer süzgecine girmişse burada **yok**tur; tükenmiş bir kanıtın
    # üstüne beyan yazmak, doğru bir cevabı kusurlu ilan etmektir (`§101.1`).
    elif niyet.ustunluk and not kesme and not _ustunluk_harcandi(qn, ic, niyet.ustunluk):
        out.append(Ihlal(
            "kesme",
            f"**{niyet.ustunluk}** dedin ama listeyi o sayıya **kesemedim** — "
            f"sıralı ama **tam** liste görüyorsun",
            "Kırılımı tek bir boyuta indirirsen (*«makine bazında»*) ilk "
            f"{niyet.ustunluk} kaydı keserim."))

    # 6 · EŞİK — "1.000 üstü"
    if any(f.get("operator") not in ("gte", "lte") for f in niyet.filtreler) \
            and not _esik_filtresi_var(filtreler) and not ic.get("measure_having"):
        out.append(Ihlal(
            "esik",
            "bir **eşik** verdin (ör. *«1.000 üstü»*) ama filtreye çeviremedim",
            "Eşiği ölçü adıyla birlikte yazarsan (*«cirosu 1.000 üstü»*) uygularım."))

    # 8 · 🔴 **ÖLÇÜ İKAMESİ — beş kez ölçüldü, hiç beyan edilmedi.**
    #
    # | soru | istenen | verilen |
    # |---|---|---|
    # | `bu yıl **bakım maliyetleri**ni makine bazında` | bakım maliyeti | **`ort_birim_maliyet`** |
    # | `bu yılki fire **maliyetimiz**` | ₺ | **`toplam_fire_kg`** (kg) |
    # | `kumaş türüne göre **ortalama** parti ağırlığı` | ortalama | **`toplam_agirlik_kg`** |
    # | `**kalite red oranı** nedir` | red oranı | `fire_orani_yuzde` |
    #
    # ⊙ Beşinde de cevap **sessizce** başka bir ölçüyle geldi. Bu, `KÖK-3`'ün tanımladığı
    # **sessiz-yanlış adayının** ta kendisidir: sayı doğru hesaplanmıştır ama **başka bir
    # şeyin** sayısıdır.
    #
    # ⚠ Yüklem **dar ve yapısal**: soruda bir **birim/toplulaştırma sözcüğü** geçiyor
    # (`maliyet`·`₺`·`tl`·`ortalama`·`oran`·`yüzde`) ama seçilen ölçünün **birimi ya da
    # toplulaştırması** onunla uyuşmuyorsa beyan edilir. Katalogdan okunur — ikinci bir
    # sözlük yazılmaz.
    #
    # ⚠ **Yalnız BEYAN eder, cevabı öldürmez** (`KÖK-3`'ün beyan-açık sözleşmesi):
    # kullanıcı sayıyı görür ve **neyin** sayısı olduğunu da görür.
    #
    # *Bir sayıyı doğru hesaplayıp yanlış şeyin adıyla sunmak, yanlış hesaplamaktan daha
    # zor fark edilir.*
    _birim_bekleniyor = None
    if re.search(r"\b(maliyet\w*|tl\b|₺|tutar\w*|para\w*)", qn):
        _birim_bekleniyor = "₺"
    _toplulastirma_bekleniyor = ("ort" if re.search(r"\b(ortalama|ort\b|vasati)", qn)
                                 else None)
    # 🔴🔴 **`§O2` — BU YÜKLEMİN DOCSTRING'İ DÖRT SINIF SAYIYOR, KODU İKİSİNİ YAZIYORDU.**
    #
    # Yukarıdaki açıklama aynen şöyle diyor: *"soruda bir birim/toplulaştırma sözcüğü
    # geçiyor (`maliyet`·`₺`·`tl`·`ortalama`·**`oran`**·**`yüzde`**)"*. `oran` ve `yüzde`
    # **hiç yazılmamıştı** — beyan sınıfı belgede vardı, kodda yoktu.
    #
    # Ölçüldü (O turu, `o16`): `iş kazası **oranı** yıllara göre nasıl değişti` →
    # `isg.kaza_adedi` (birim **boş**, bir **sayım**) döndü, 5 satır, **hiçbir beyan yok**.
    # Kullanıcı bir **oran** sordu, bir **adet** aldı ve bunu söyleyen olmadı.
    # `niyet` bile biliyordu: `bilinmeyen=orani`.
    #
    # ⊙ Bu, `§86`'nın kardeşidir ve deponun kendi cümlesiyle: *"belgelenmiş davranışla
    # kodun ayrışması, bu depoda tekrar eden en pahalı hata sınıfıdır."* Orada bir **geri
    # alma**, burada bir **beyan sınıfı** yazılmış ama yapılmamıştı.
    #
    # ⚠ Ölçüt yine **tek sahipten** okunur (`viz._unit_of`) ve tür testidir, eşitlik
    # değil — `§60`'ın kendi yanlış-pozitif dersi (`₺/kg` de bir tutardır).
    # ⚠ `oranla` **dışarıda**: o bir kıyas edatıdır (*"geçen yıla oranla"*), bir birim
    # talebi değil. Sınır dilbilgiseldir, sözlüksel değil.
    _oran_bekleniyor = bool(re.search(r"\b(oran(?!la\b)\w*|yuzde\w*|%)", qn))
    # ⚠ **BİRİM TEK SAHİPTEN OKUNUR.** İlk yazımda `cube_meta["measure_meta"][m]["unit"]`
    # diye bir yol uydurdum ve kapı sessizce hiç ateşlemedi — o anahtar **yok**. Birimin
    # sahibi `viz._unit_of`'tur (MDL `units` sözlüğü, yoksa regex yedeği) ve ikinci bir
    # çözücü yazmak `KAT-1` olurdu.
    # *Var olmayan bir alanı okuyan kod sessizce hiçbir şey yapar — ve testi geçer.*
    from app.viz import _unit_of as _vbirim
    _units = (cube_meta or {}).get("units") or {}

    # FAZ O-7 — MUKERRER YAZDIM, VE BU BIR OLCUMDU.
    #
    # DD15 ("firenin maliyeti" -> toplam_fire_kg, sessiz) icin buraya bir `para_birimi_yok`
    # yuklemi yazdim. Canlida ateslendi — VE YANINDA ZATEN VAR OLAN BIR BEYAN CIKTI:
    #     "bir ₺ tutari sordun ama elimdeki olcu kg cinsinden (toplam_fire_kg)"
    #
    # Kaynak okundu: `_birim_bekleniyor` (:471) `maliyet|tl|₺|tutar|para` desenini ZATEN
    # tasiyor ve `olcu_ikamesi` ihlali ZATEN uretiyor. Yani DD15'in kusuru bir BEYAN
    # EKSIKLIGI DEGILDI — beyan vardi, ben onu aramadan ikincisini yazdim.
    #
    # YAZMADAN ONCE ARA kuralinin bu turdaki faturasi: iki cumle, ayni sey, ust uste.
    # Kaldirildi.
    #
    # ⊙ Ve bu, DD15'in GERCEK teshisini degistiriyor: sistem sessiz DEGILDI, DURUSTCE
    # beyan ediyordu. G2 boslugunun kaniti DD15 degil, DD16 (Discovery) ile DD17
    # (netlestirme) arasindaki TUTARSIZLIKTIR — ayni sinif, iki ayri yol.
    #
    # *Bir eksigi kapatmadan once, onun gercekten acik olup olmadigina bakmak gerekir.*

    # 🔴🔴 **`§U1` — İSTEĞİ KARŞILAYAN KOLONU GÖRMEDEN «EKSİK» İLAN ETMEK.**
    #
    # Aşağıdaki döngü ölçüleri **tek tek** geziyor ve ilk uyuşmayanda beyan ediyordu.
    # İki şeyi hiç sormuyordu: *(a)* listedeki **başka bir ölçü** isteği zaten karşılıyor
    # mu, *(b)* `pencere`/`turev` alanı istenen kolonu zaten **üretiyor** mu.
    #
    # Ölçüldü (U turu, **dört** kanıt):
    #
    #   `u8`  cevapta `_p_pay_toplam_rework_kg = 24,7`   → yine *"oran sordun ama kg"*
    #   `u9`  cevapta `_t_oran_… = 302,3` (ortalama parti kg) → *"ortalama sordun ama toplam"*
    #   `u14` ölçüler `[toplam_ciro, **fire_orani_yuzde**]` → *"oran sordun ama ₺"*
    #   `u15` aynı, `limit 3` ile
    #
    # 🔴 Sonuç **doğru bir cevabı eksik ilan etmek**tir — ve bu, beyansızlıktan kötüdür:
    # kullanıcı elindeki sayının yanlış olduğunu sanır. `§89.3`'te kendi `kesme`
    # yüklemim aynı hatayı yapmıştı ve ders orada yazılı:
    # *"Bir kusuru ilan eden yüklem, kendi yanlış-pozitifini üretirse, ilan ettiği
    # kusurdan daha pahalıdır."*
    #
    # ⚠ Yeni sözlük yok: `pencere`/`turev` alanları `§91`'de zaten `cq`'da taşınıyor;
    # burada yalnız **okunuyorlar**.
    _pn_kip = str((ic.get("pencere") or {}).get("kip") or "")
    _tv_kip = str((ic.get("turev") or {}).get("kip") or "")
    #: Oran/yüzde isteği **karşılanmış** sayılır: bir ölçü zaten oran ise, ya da `pay`
    #: penceresi / `yuzde`·`oran` türevi kolonu üretiyorsa.
    # 🔴 **`§X3` — `degisim_yuzde` DE BİR YÜZDEDİR ve beyan onu saymıyordu.**
    #
    # Ölçüldü (`X18` — *«aylık üretim ve önceki aya göre yüzde değişim»*): sistem
    # `pencere:{kip:"degisim_yuzde"}` üretti, `_p_degisim_yuzde_…` kolonunu **döndürdü**,
    # ve sonra *«bir oran/yüzde sordun ama `toplam_agirlik_kg` bir kg»* diye **kendi
    # verdiği cevabı eksik ilan etti**.
    #
    # ⊙ Kusur `§U1`'in kendi listesindeydi: `pay`/`yuzde`/`oran` sayılmış, `degisim_yuzde`
    # **unutulmuştu** — oysa adı da çıktısı da bir yüzdedir. `§101.1`'in tersi bir zarar:
    # yanlış-pozitif bir **beyan**, doğru bir cevabı kusurlu gösterir ve kullanıcı ona
    # güvenmez. *Bir cevabı haksız yere eksik ilan etmek, eksik bir cevap kadar pahalıdır.*
    _oran_karsilandi = (
        _pn_kip in ("pay", "degisim_yuzde") or _tv_kip in ("yuzde", "oran")
        or any(re.search(r"(%|yuzde|oran)", (_vbirim(_x, _units) or "") + _x, re.I)
               for _x in (ic.get("measures") or [])))
    #: Ortalama isteği karşılanmış sayılır: `ort_` ile başlayan bir ölçü var, ya da
    #: `oran` türevi (pay/payda) bir ortalama üretiyor (`u9`: toplam kg ÷ parti sayısı).
    _ort_karsilandi = (_tv_kip == "oran"
                       or any(str(_x).startswith("ort_") for _x in (ic.get("measures") or [])))
    for _m in (ic.get("measures") or []):
        _birim = _vbirim(_m, _units) or ""
        # 🔴 **VE İLK YAZIMIM YANLIŞ-POZİTİF ÜRETTİ — kapı yakaladı.** Test
        # `_birim != "₺"` idi; `birim maliyet` ölçüsünün birimi **`₺/kg`** olduğu için
        # meşru bir soru *"ikame"* diye damgalandı (**beş** korpus vakası).
        # ⊙ Doğru test **eşitlik değil TÜR**: birim bir **para** işareti taşıyor mu?
        # `₺/kg` de bir tutardır. *Bir türü eşitlikle sınamak, o türün bütün
        # biçimlerini reddetmektir.*
        _para_mi = bool(re.search(r"(₺|tl|\$|€|lira)", _birim, re.I))
        if _birim_bekleniyor and _birim and not _para_mi:
            out.append(Ihlal(
                "olcu_ikamesi",
                f"bir **{_birim_bekleniyor} tutarı** sordun ama elimdeki ölçü "
                f"**{_birim}** cinsinden (`{_m}`)",
                "O birimde bir ölçü katalogda yoksa hesabı ben uyduramam — "
                "başka bir ölçü adıyla sorabilirsin."))
            break
        if _oran_bekleniyor and not _oran_karsilandi:
            out.append(Ihlal(
                "olcu_ikamesi",
                f"bir **oran/yüzde** sordun ama `{_m}` bir "
                f"**{_birim or 'sayım'}** — payda katalogda tanımlı değil",
                "Oranı katalogda varsa adıyla sorabilirsin (*«… oranı»* biçiminde "
                "tanımlı bir ölçü); yoksa payı ve paydayı ayrı ayrı isteyebilirsin."))
            break
        if _toplulastirma_bekleniyor and not _ort_karsilandi and _m.startswith("toplam_"):
            out.append(Ihlal(
                "olcu_ikamesi",
                f"**ortalama** sordun ama `{_m}` bir **toplam**",
                "Ortalaması katalogda varsa adıyla sorabilirsin "
                "(*«ortalama …»* biçiminde tanımlı bir ölçü)."))
            break

    # 9 · 🔴 **KISITLAMA — «sadece …» dedi, hiçbir şey kısıtlanmadı (2 kanıt).**
    #
    # Ölçüldü: `aylık üretim` → `**sadece** hafta içi günleri al` → **satırlar aynen**
    # döndü, filtre uygulanmadı ve **hiçbir şey beyan edilmedi** (`e16`T2 · `j4`T2).
    #
    # ⊙ Sebebi bir **mutfak** eksiği: `hafta içi` katalogda bir **değer değil** (boyut
    # `hafta_gunu`'nun değerleri tek tek günlerdir), yani garson da onu ifade edemiyor.
    # Ama bu, susmayı **haklı çıkarmaz**: kullanıcı bir kısıtlama istedi ve kısıtlanmamış
    # bir sayı gördü — sessiz-yanlışın tanımı.
    #
    # ⚠ Yüklem dar ve **kapalı bir dilbilgisi sınıfına** dayanır: kısıtlayıcı zarflar
    # (`sadece`·`yalnız`·`yalnızca`·`only`·`just`). Ölçüt yapısal: `cq`'da **tarih dışı**
    # hiçbir filtre yoksa kısıtlama gerçekleşmemiştir.
    #
    # ⚠ Yalnız **beyan eder**, cevabı öldürmez (`KÖK-3`).
    #
    # *Bir kısıtlamayı uygulayamamak bir sınırdır; uygulamadığını söylememek bir hatadır.*
    if re.search(r"\b(sadece|yalniz|yalnizca|only|just)\b", qn) and not any(
            f.get("dimension") and f.get("dimension") != "tarih"
            and f.get("operator") not in ("gte", "lte")
            for f in filtreler):
        out.append(Ihlal(
            "kisitlama",
            "**sadece …** dedin ama sorguya bir kısıtlama taşıyamadım — sayı **tüm**"
            " kayıtları kapsıyor",
            "Kısıtlamayı katalogdaki bir değerle yazarsan (*«sadece Siyah renk»*) "
            "uygularım."))

    # 7 · DIŞLAMA — "X hariç"
    if (niyet.dislama_istendi
            and not any(str(f.get("operator")) in ("neq", "not_in", "!=")
                        for f in filtreler)):
        out.append(Ihlal(
            "dislama",
            "bir şeyi **hariç tutmanı** istedin ama dışlama filtresi kuramadım",
            "Hariç tutulacak değeri açıkça yazarsan (*«RAM-2 hariç»*) uygularım."))

    return out


#: Zaman birimleri — `_TOPN_CUE`nun ("son") yanlış-pozitifini kapatır.
#: 🔴 **`§42` — SINIFIN EKSİK ÜYESİ BİR YANLIŞ BEYAN ÜRETTİ.**
#:
#: Ölçüldü: `2025 ile 2026 **ilk yarısını** kıyasla` → `eksik_niyet:['ustunluk']` ve
#: cevapta *«**en yüksek/en çok** dedin ama sıralama uygulayamadım»*. Kullanıcı öyle bir
#: şey **demedi**; `ilk` orada bir sıra sayısıdır ve `yarı` bir **zaman birimidir**.
#:
#: ⊙ `_ustunluk_mu`'nun kuralı zaten doğruydu (*"ipucundan sonra bir zaman birimi
#: geliyorsa üstünlük değildir"*) — eksik olan **sınıfın bir üyesiydi**: `yarı`/`yarıyıl`.
#:
#: 🔴 Ve `Ö10`'un kuralı burada da geçerli: *yanlış bir beyan sessizlikten kötüdür* —
#: sistem kullanıcıya **onun söylemediği bir şeyi söylediğini** söylüyor.
#:
#: *Bir kuralın yanlış çalışması her zaman kuralın yanlışlığından gelmez; bazen kuralın
#: baktığı kümenin eksikliğindendir.*
#:
#: ⚠ **KAYITLI BORÇ:** `ilk yarı`/`ikinci yarı` bir **dönem olarak da çözülmüyor**
#: (`date_filters("ilk yari")` → boş; oysa `ilk ceyrek` → dolu). Bu ayrı bir iştir; bu
#: madde yalnız **yanlış beyanı** kapatır, dönemi çözmez. İkisini karıştırmak, kapatılan
#: kusurun ölçüsünü kaybettirirdi.
#: ⚠ `§45` — **ÜNSÜZ YUMUŞAMASI da bir yüzey biçimidir.** Kapı `son çeyreğin karlılığı`
#: ile kırmızı verdi: `çeyrek` + ek → `çeyreğ`, ve `k` biten kök `\w{0,4}` ile
#: yakalanamaz çünkü **kökün kendisi değişmiştir**. Türkçede `k→ğ`·`p→b`·`t→d`·`ç→c`
#: kural gereğidir; kökü tanıyıp yumuşamışını tanımamak, aynı kelimenin yarısını bilmektir.
_ZAMAN_BIRIMI = (r"(ay|gun|gün|hafta|yil|yıl|ceyre[kg]|çeyre[kğ]|donem|dönem|saat|dakika"
                 r"|yari|yarı|yariyil|yarıyıl)")


def _olcu_sinonim_araliklari(qn: str, ic: dict, cube_meta: dict | None) -> list[tuple[int, int]]:
    """Sorudaki **ölçü adının** kapladığı aralıklar.

    🔴 Ölçülen yanlış-pozitif (525 meşru soruda 10 tanesi): `kur` cube'unun ölçüsü
    **`en yuksek kur`** diye adlandırılmış. Yani *"bu yıl en yüksek kur"* sorusunda
    `en yüksek` bir **sıralama isteği değil, ölçünün ADIDIR**.

    *Bir ipucu, başka bir şeyin adının içindeyse, ipucu değildir.*
    """
    if not cube_meta:
        return []
    araliklar: list[tuple[int, int]] = []
    secili = set(ic.get("measures") or [])
    for m, syns in (cube_meta.get("measure_synonyms") or {}).items():
        if secili and m not in secili:
            continue
        for syn in (syns or []):
            t = _norm(str(syn).removesuffix("!"))
            if len(t) < 3:
                continue
            for mt in re.finditer(re.escape(t), qn):
                araliklar.append(mt.span())
    return araliklar


def _ustunluk_harcandi(qn: str, ic: dict | None, sayi: int | None) -> bool:
    """🔴🔴 `§SR` — **BİR RAKAM İKİ KEZ OKUNAMAZ: değer süzgecine giren sayı TÜKENMİŞTİR.**

    ## Ölçülen kusur (curl `N` turu, 2026-08-10)

        «RAM-1 makinesinin bu yıl toplam duruş süresi»
          → cq: makine eq "RAM-1" · 41.104 dk        ✅ CEVAP DOĞRU
          → not: «**1** dedin ama listeyi o sayıya kesemedim»   🔴 YALAN BEYAN

    `RAM-1` içindeki **1** hem bir makine adının parçası olarak süzgece girdi, hem de
    *«en iyi 1»* sayısı olarak `niyet.ustunluk`'a. Aynı karakter iki ayrı niyeti besledi
    ve ikincisi **doğru bir cevabın üstüne bir eksiklik yazdı**.

    ## Neden bu, `KAT-1`'in çalışma-zamanı ikizi

    `KAT-1` *«bir kuralın iki sahibi olmaz»* der; buradaki kusur bir **kanıtın** iki
    tüketicisi olmasıdır. Depo bu ayrımı zaten bir kez yapmıştı — `_ustunluk_mu`'ya
    `cube_meta` verilmesinin gerekçesi birebir aynıdır: *«ipucu bir ölçü adının
    içindeyse ipucu değildir»* (`kur` cube'unun ölçüsü literal olarak *«en yüksek
    kur»*). Aynı disiplin **değer** tarafında kurulmamıştı.

    ## Yüklem — konumsal, sözlüksüz

    Sayının soruda geçtiği **her** yer, kimlik süzgeçlerinden birinin değerinin
    içindeyse sayı tükenmiştir. Bir yerde bile serbest geçiyorsa **tüketilmemiştir** —
    o zaman gerçek bir üstünlük sayısı olabilir (*«RAM-1 ve RAM-2'nin en kötü 1 ayı»*).

    ⚠ Yeni dil kuralı **yok**: yalnız iki dizgenin konumu kıyaslanıyor. ADR-0008 kapsamı
    dışında — bu bir morfoloji değil, bir **muhasebe**.

    *Bir kanıt harcandığında biter; iki kez sayılan bir kanıt, kanıt değil bir
    yankıdır.*
    """
    if not isinstance(ic, dict) or not sayi:
        return False
    from app.cube_router import _norm as _n

    metin = str(sayi)
    araliklar: list[tuple[int, int]] = []
    for f in (ic.get("filters") or []):
        if not isinstance(f, dict):
            continue
        if str(f.get("operator") or "") not in ("eq", "neq", "in", "nin"):
            continue
        ham = f.get("value")
        for d in (ham if isinstance(ham, (list, tuple)) else [ham]):
            nd = _n(str(d))
            if not nd or metin not in nd:
                continue
            i = qn.find(nd)
            while i >= 0:
                araliklar.append((i, i + len(nd)))
                i = qn.find(nd, i + 1)
    if not araliklar:
        return False
    yerler = [m.span() for m in re.finditer(rf"\b{re.escape(metin)}\b", qn)]
    if not yerler:
        return False
    return all(any(a <= s and e <= b for a, b in araliklar) for s, e in yerler)


def _ustunluk_mu(qn: str, topn_cue, ic: dict | None = None,
                 cube_meta: dict | None = None) -> bool:
    """Gerçekten bir **üstünlük** isteği mi, yoksa bir dönem mi?

    🔴 Ölçülen yanlış-pozitif: `_TOPN_CUE` kalıbı `son`u da içeriyor (çünkü *"son 5
    makine"* meşrudur) ve bu yüzden **`son 3 ay ve son 6 ay ciro`** sorusu *"sıralama
    uygulayamadım"* ihlali veriyordu — oysa orada `son` bir **dönem edatıdır**.

    ⚠ `route()` bu ayrımı zaten yapıyor ama **bağlamla** (`_TOPN_CUE.search(before)`),
    yani ipucunun neyin ÖNÜNDE olduğuna bakarak. Burada aynı ayrım tersten kurulur:
    ipucundan sonra bir **zaman birimi** geliyorsa üstünlük değildir.

    *Bir kalıbı ödünç almak, onun bağlamını da ödünç almayı gerektirir.*
    """
    olcu_araliklari = _olcu_sinonim_araliklari(qn, ic or {}, cube_meta)
    for m in re.finditer(topn_cue.pattern, qn):
        kuyruk = qn[m.end():m.end() + 24]
        # 🔴 **`§45` — `\b` TÜRKÇE EKİ GÖREMİYOR ve kural yarısında ölüydü.**
        #
        # Ölçüldü: `son 3 **ay** ciro` ✅ geçiyor ama `son 3 **ayın** ortalama günlük
        # üretimi` 🔴 geçmiyordu → *«en yüksek/en çok dedin ama sıralama uygulayamadım»*.
        # Kullanıcı öyle bir şey **demedi**.
        #
        # ⊙ Sebep tek karakter: `ay\b` deseni `ayin`de **`y` ile `i` arasında** bir sözcük
        # sınırı arar ve orada sınır **yoktur**. Yani kural, zaman biriminin **çekimsiz**
        # hâlinde çalışıyor, çekimli hâlinde susuyordu — ve Türkçede dönem ifadeleri
        # neredeyse **her zaman** çekimlidir (`ayın`·`ayda`·`aylık`·`yılın`·`çeyreğin`).
        #
        # ⚠ `\w{0,4}` bilerek **sınırlı**: eksiz de olabilir (`ay`), en fazla dört harflik
        # bir ek alabilir (`aylık`). Sınırsız bırakmak `ay` ile başlayan her kelimeyi
        # (`ayrıntı`) zaman birimi sayardı — `§32`'nin dersi: *kısa bir dizge her yere
        # sığar*, o yüzden sağı **açık değil dar** bırakılır.
        #
        # *Bir sınır kontrolü, sınırladığı dilin biçimbilgisini tanımıyorsa yalnız o dilin
        # en yalın hâlinde çalışır — ve gerçek cümleler yalın değildir.*
        if re.match(rf"\s*\d*\s*{_ZAMAN_BIRIMI}\w{{0,4}}\b", kuyruk):
            continue                       # "son 3 ay" / "son 3 ayın" → dönem
        if any(a <= m.start() and m.end() <= b for a, b in olcu_araliklari):
            continue                       # "en yüksek kur" → ölçünün ADI
        return True
    return False


def _zaman_ekseni_var(cq: dict, cube_meta: dict | None) -> bool:
    """Kırılımda bir ZAMAN boyutu var mı — trend gerçekten çizilebiliyor mu?"""
    zaman = set((cube_meta or {}).get("time_dimensions") or ["tarih"])
    return any(d in zaman or str(d).startswith("tarih") for d in (cq.get("dimensions") or []))


#: 🔴 **EŞİK İKİ YERDE YAŞAR — ve kapı yalnız birine bakıyordu.** Curl'de ölçüldü
#: (`§AJ4` sonrası): *"bu yıl 5 milyon üzeri ciro yapan müşteriler"* → `cq` artık
#: `measure_having={"measure":"toplam_ciro","op":">","value":5000000}` **taşıyor**, ama
#: `uyum` yine *"eşiği filtreye çeviremedim"* diyordu.
#:
#: ⊙ Sebep yapısal: **boyut** eşiği `filters`'a (WHERE), **ölçü** eşiği
#: `measure_having`'e (HAVING) gider — ikisi farklı SQL kademesidir ve farklı alanlarda
#: yaşar. Kapı yalnız `filters`'ı sayıyordu.
#:
#: ⚠ Ve bu, kapının en pahalı hata biçimiydi: sistem **doğru olanı yapmıştı** ve
#: kullanıcıya *"yapamadım"* diyordu — yanlış bir özür, yanlış bir cevaptan daha çok
#: güven tüketir çünkü kullanıcı çalışan bir yolu terk eder.
#:
#: *Bir niyetin karşılandığını sormak, onun nereye yazıldığını bilmeyi gerektirir.*


def _esik_filtresi_var(filtreler: list[dict]) -> bool:
    return any(str(f.get("operator")) in ("gt", "lt", "gte", "lte", ">", "<", ">=", "<=")
               and not _tarih_gibi(f.get("value")) for f in filtreler)


def _tarih_gibi(v) -> bool:
    """Dönem filtresini eşik sanma. ⚠ Bu ayrım olmadan **her dönemli soru** eşik
    ihlali verirdi — kapının en olası yanlış-pozitifi."""
    return isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}", v) is not None


# ═══════════════════════════════════════════════════════════════════════════════
# KÖK-3 · BEYANLI KISMİ CEVAP
# ═══════════════════════════════════════════════════════════════════════════════

def chipler(ihlaller: list[Ihlal]) -> list[dict]:
    """`§TZ` — ihlallerin **tıklanabilir** olanları. Boş liste = tık yok.

    ⚠ Tek sahip: chip'i **ihlali üreten yer** kurar (terimi ve sahibini orada biliyoruz);
    burası yalnız toplar. Metinden chip türetmek, aynı cümleyi ikinci kez ayrıştırmaktı.
    """
    out, gorulen = [], set()
    for i in (ihlaller or []):
        c = getattr(i, "chip", None)
        if isinstance(c, dict) and c.get("label") and c["label"] not in gorulen:
            gorulen.add(c["label"])
            out.append(dict(c))
    return out


def kismi_cevap_notu(ihlaller: list[Ihlal]) -> str:
    """*"Şu kısmını verdim, şu kısmını veremedim, nedeni bu."*

    ⚠ **Rozetsizdir**: ADR-0008 *"yanlış cevaba güven rozeti takma"* der; beyanlı kısmi
    cevap o yasağı **çiğnemez, karşılar**. Sayı doğrudur (küpten gelir) — eksik olan
    **sorunun bir parçasıdır** ve bu **yazılır**.
    """
    if not ihlaller:
        return ""
    if len(ihlaller) == 1:
        i = ihlaller[0]
        # ⚠ `§UT-M` — nokta **koşullu**: açıklamalar zaten cümledir ve çoğu noktayla
        # biter. Koşulsuz eklemek canlıda *«…bir karşılık var..»* üretiyordu (ölçüldü,
        # curl `U` turu). Küçük bir kusur ama kullanıcının okuduğu **tek** cümlede.
        _a = str(i.aciklama or "").rstrip()
        return f"⚠ Sayı doğru ama **eksik**: {_a}{'' if _a.endswith(('.', '!', '?', '…')) else '.'}\n\n{i.oneri}"
    satirlar = "\n".join(f"· {i.aciklama}" for i in ihlaller)
    return ("⚠ Sayı doğru ama **eksik** — sorunun şu kısımlarını yerine getiremedim:\n"
            f"{satirlar}\n\n{ihlaller[0].oneri}")


def cokluk_mu(eksen: str | None, adaylar: list) -> bool:
    """🔴🔴 `O-19` — **AYRIK ÖLÇÜ KÜMELERİ BİR BELİRSİZLİK DEĞİL, BİR ÇOKLUKTUR.**

    ⊙ Ölçüldü (canlı `IV` turu, iki soru): *«iade oranı en yüksek 3 müşteriyi **ve**
    ciro paylarını göster»* ve *«hangi vardiyada kalite sorunları yoğunlaşıyor bu yıl»*
    → ikisi de *«Hangi ölçüyü istiyorsun?»* ile **cevapsız** kaldı:

        Intent-path: self-consistency uyuşmazlığı (%50 uyum / 3 örnek, eksen=measures)

    Oyların hikâyesi şudur: biri **çekimser** kalıyor (*«bu soru tek bir cube ile
    yanıtlanamaz»* — ve **haklı**), ikisi **farklı** küplerden **farklı** ölçüler
    seçiyor. Yani üç oy da doğru: soru gerçekten **iki parçalı**.

    🔴 Ayrım keskin ve deterministiktir:

    | oylar | ne demek | doğru cevap |
    |---|---|---|
    | aynı ölçü adı, **farklı küp** (`eksen=cube`) | 🔴 **belirsizlik** | sor |
    | **ayrık** ölçü kümeleri (`eksen=measures`) | ⊙ **çokluk** | **planla** |

    Birincisinde kullanıcı bir şey istedi, iki sahip çıktı. İkincisinde kullanıcı **iki
    şey** istedi ve her oy **birini** yakaladı. İkisine aynı soruyu sormak, ikinci
    kullanıcıya kendi cümlesini tekrar ettirmektir.

    ⚠ Kesişen kümeler **çokluk sayılmaz**: `{ciro}` ↔ `{ciro, fire}` bir oyun ötekinden
    **daha zengin** okumasıdır (`§V2`'nin konusu), iki ayrı istek değil. `§101.1` gereği
    şüphede **susulur** ve netleştirme aynen konuşur.

    *Bir soruyu sormak için önce iki farklı cevabın olması gerekir — iki EKSİK cevabın
    değil.*
    """
    if eksen != "measures" or len(adaylar or []) < 2:
        return False
    kumeler = [frozenset(str(m) for m in ((a or {}).get("measures") or []))
               for a in adaylar]
    if any(not k for k in kumeler):
        return False
    for i, a in enumerate(kumeler):
        for b in kumeler[i + 1:]:
            if a & b:                 # kesişiyorsa zenginlik farkı — çokluk DEĞİL
                return False
    return True


def tanimadan_cevap_notu(niyet) -> str | None:
    """🔴🔴 `§KA` — **HİÇBİR ŞEYİ TANIMADAN VERİLEN GÜVENLİ BİR CEVAP, BİR UYDURMADIR.**

    ## Ölçülen kusur (curl `CC` turu, CC-15)

        «asdfgh qwerty»
          → `source=cube+llm` · `oee` küpü · **11 satırlık makine bazında OEE raporu**
          → not YOK · beyan YOK · uyarı YOK

    Sorunun tek bir harfi bile kataloğa değmiyor. `route()` bu soruyu **cevaplamazdı**:
    onun bir **kapsam kapısı** var (`partial_unknowns` → `_uncovered`) ve açıklanamayan
    bir içerik sözcüğü kalırsa çekilir. Garson devraldığında o kapı **hiç koşmuyor** —
    ve garson *ne attığını* söylemiyor.

    🔴 Bu bir **kapı değil, bir beyandır** ve olması gereken de budur: doktrin
    *«"anlamadım" bir son cevap olamaz»* diyor. Cevap **gider**; yanına *bunun bir
    varsayım olduğu* yazılır. Reddetmek `§0.0`'ı, susmak `E-2`'yi çiğnerdi.

    ## Yüklem — sözlüksüz, ve `§101.1` gereği DAR

    Dördü **birden** boşsa konuşur: ölçü adayı · kırılım · adı geçen dönem · süzgeç.
    Yani soru kataloğun **hiçbir** eksenine değmemiştir. Meşru bir iş sorusu bu dördün
    en az birini taşır — taşımıyorsa cevap zaten bir tahmindir.

    ⚠ Ölçülen kalibrasyon (aynı tur): *«lütfen bana bu yılın cirosunu söyler misin»*
    (ölçü+dönem var) ve *«kaç makinemiz var»* (`makine` kırılımı var) **susar** — oysa
    ikisinin de `bilinmeyen` artığı doludur (`soyler,misin` · `kac,makinemiz,var`).
    *Artığa bakan bir yüklem bu ikisini suçlardı; tanınana bakan yüklem susuyor.*

    ## 🔴 Ve bu, kusurun YALNIZ BİR PARÇASI — kalanı ölçüldü ve BORÇ yazıldı

    Aynı turda iki vaka daha çıktı ve bu yüklem onları **görmez**, çünkü ikisinde de
    katalog eksenlerine değen bir şey **var**:

        «mars gezegenindeki satışlarımız»   → `satış` tanındı → ₺137.588.350
        «…ciroyu **euro** olarak göster»    → ölçü+dönem tanındı → ₺74.022.836 (TL)

    Onları ayırt edecek şey artık sözcüğün **ne olduğudur** (`euro` bir nesne, `misin`
    bir soru eki) ve bunu bilen tek merci **garsonun kendisidir**. Doğru çözüm bir
    kelime listesi değil, Intent-JSON'a bir `yok_sayilan` alanı ve iddianın iki
    deterministik süzgeci (sözcük soruda **geçmeli**, teslim edilen fişte
    **geçmemeli**). Ayrı bir demet, ayrı bir ölçüm — `OPERASYON-DURUM.md`'de.

    *Bir kusurun yarısını kapatmak, tamamını kapatmış gibi yazılmadıkça bir ilerlemedir.*
    """
    if niyet is None:
        return None
    if (getattr(niyet, "olcu_adaylari", None) or getattr(niyet, "kirilimlar", None)
            or getattr(niyet, "donem_sayisi", 0) or getattr(niyet, "filtreler", None)):
        return None
    return ("⚠ Bu soruyu kataloğumdaki hiçbir **ölçü**, **boyut** ya da **döneme** "
            "bağlayamadım — aşağıdaki rapor bir **varsayımdır**. Kastettiğin bu "
            "değilse sorunu biraz açar mısın?")


def beyan_ekle(resp, *, soru: str, cq: dict, sema: dict, cube_meta: dict | None = None,
               chip: bool = True) -> None:
    """`§UY-yoy` — ihlal beyanını cevaba **iliştirir**: tek gövde, iki çağıran.

    ⊙ Ölçüldü (curl `CC` turu, CC-18/CC-19) — aynı kayıp, iki yol, **tek** beyan:

        «bu yıl toplam ciro **ve** fire oranı»          → ✅ *«soruda 2 ölçü, cevapta 1»*
        «geçen yıla göre ciro **ve** fire oranı değişimi» → 🔴 aynı kayıp, **NOT YOK**

    Dönemsel kıyas (`yoy`) kendi `AskResponse`'unu kurup doğrudan mühre gidiyor, yani
    `_answer_from_cube_query`'deki beyan bloğunu **hiç görmüyordu**. `ask.py`'nin kendi
    uyarısının birebir tekrarı: *bir kuralı yazmak, onu her çağrı yerinde kurmak
    değildir — ve eksik kurulan yer, kuralın hiç olmadığı yerden daha tehlikelidir,
    çünkü kural yazılı olduğu için orada da işlediği sanılır.*

    ⚠ `cq` **kıyas alanıyla** geçilmelidir (`compare`): `denetle` onu okur (`:846`) ve
    okumazsa bu dal, kıyası **yapan** yolun kendisini *«kıyas istendi ama yok»* diye
    suçlardı — düzeltmenin kendisi bir yanlış-pozitif üretirdi.
    """
    ihlaller = denetle(soru, {"cube_query": cq}, cube_meta, sema)
    if not ihlaller:
        return
    resp.eksik_niyet = [i.isaret for i in ihlaller]
    resp.note = " ".join(x for x in [resp.note, kismi_cevap_notu(ihlaller)] if x)
    if chip:
        resp.suggestions = (resp.suggestions or []) + chipler(ihlaller)


def uydurma_beyani(resp, niyet) -> bool:
    """`§KA`'nın **iliştirme** yarısı — yüklem `tanimadan_cevap_notu`'nda.

    Ayrı durur çünkü yüklem saf ve testlenebilir olmalı; bu ise bir cevabı değiştirir.
    Döner: beyan edildi mi (çağıran ize bunu yazar).
    """
    not_ = tanimadan_cevap_notu(niyet)
    if not not_:
        return False
    resp.note = " ".join(x for x in [resp.note, not_] if x)
    resp.trace = [*(resp.trace or []),
                  "§KA: katalogda hiçbir eksene değmeyen soru → cevap VARSAYIM "
                  "olarak beyan edildi"]
    return True


def yok_sayilan_beyani(resp, q: str, cq: dict, cube_meta: dict | None,
                       sema: dict | None, iddia: list[str]) -> bool:
    """🔴🔴 `§YS` — **GARSONUN «TEMSİL EDEMEDİM» İDDİASI, ÖLÇÜLEREK YAYIMLANIR.**

    ## Üç canlı ölçüm, tek sınıf

        «…ciroyu **euro** olarak göster»      → ₺74.022.836, beyan YOK   (curl `CC`, CC-16)
        «**mars gezegenindeki** satışlarımız» → ₺137.588.350, beyan YOK  (curl `CC`, CC-14)
        «bütçe **gerçekleşme** oranı»          → `toplam_hedef`, beyan YOK (curl `GG`, GG-a)

    Üçünde de garson soruyu okudu, bir kısmını temsil edemedi ve **sessizce attı**.
    `§KA` bunları göremez: soru kataloğun eksenlerine **değiyor** (ölçü var, dönem var).
    Ayırt edecek şey artık sözcüğün **ne olduğudur** (`euro` bir nesne, `misin` bir soru
    eki) — ve bunu bilen tek merci **garsonun kendisidir**.

    ## Ama bir iddia, bir ölçüm değildir — iki süzgeç

    1. **Sözcük soruda GERÇEKTEN geçmeli.** Model bir sözcük uydurabilir; uydurduğu şey
       kullanıcının cümlesinde yoksa iddia düşer.
    2. **Teslim edilen fişte GEÇMEMELİ.** Küp/ölçü/boyut adları, sinonimleri, süzgeç
       değerleri ve dönem ifadesi taranır; sözcük oralardan birinde karşılanmışsa
       **atılmamıştır** (`§101.1`: başka biçimde karşılanan bir terim eksik sayılmaz).

    ⚠ Sayı **hiç etkilenmez**: bu alan sorguya girmez, yalnız bir cümle üretir. Yani
    doktrinin sınırı korunur — garson **okur**, mutfak **sayar**.

    ⚠ Ve reddetmez: cevap gider, yanına *«şu kısım yansımadı»* yazılır (`§0.0`).

    *Bir hakeme niyetini sormak başka, ne attığını sormamak başkadır — ama hakemin
    sözünü de tartmadan yayımlamak, hakemliği ona devretmektir.*

    Döner: beyan edildi mi.
    """
    from app import cube_router as _cr

    if not iddia:
        return False
    qn = _cr._norm(q or "")
    # Fişin **taşıdığı** her metin: adlar, sinonimler, süzgeç değerleri, dönem ifadesi.
    _tasinan: list[str] = [str(cq.get("cube") or ""), str(cq.get("period_expr") or "")]
    _tasinan += [str(m) for m in (cq.get("measures") or [])]
    _tasinan += [str(d) for d in (cq.get("dimensions") or [])]
    _tasinan += [str(f.get("value")) for f in (cq.get("filters") or [])
                 if not isinstance(f.get("value"), (list, dict))]
    _tasinan += [str(f.get("dimension")) for f in (cq.get("filters") or [])]
    _cm = cube_meta or next((c for c in ((sema or {}).get("cubes") or [])
                             if c.get("name") == cq.get("cube")), None) or {}
    for _k in ("measure_synonyms", "dimension_synonyms"):
        for _ad, _syn in (_cm.get(_k) or {}).items():
            if _ad in _tasinan:
                _tasinan += [str(x) for x in (_syn or [])]
    _tasinan += [str(x) for x in (_cm.get("synonyms") or [])]
    _fis = _cr._norm(" ".join(t for t in _tasinan if t))
    _kalan = []
    for _w in iddia:
        _wn = _cr._norm(str(_w))
        if not _wn or len(_wn) < 3:
            continue
        if not _cr._syn_hit(qn, _wn):        # (1) soruda geçmiyor → uydurma
            continue
        if _fis and _cr._syn_hit(_fis, _wn):  # (2) fişte karşılanmış → atılmamış
            continue
        _kalan.append(str(_w))
    if not _kalan:
        return False
    _metin = ", ".join(f"«{w}»" for w in _kalan[:3])
    resp.note = " ".join(x for x in [getattr(resp, "note", None), (
        f"⚠ Soruda geçen {_metin} bu cevaba **yansımadı** — sayı bu kısmı "
        f"hesaba katmıyor.")] if x)
    resp.trace = [*(getattr(resp, "trace", None) or []),
                  f"§YS: garson {len(_kalan)} sözcüğü temsil edemediğini bildirdi "
                  f"(soruda geçtiği ve fişte geçmediği doğrulandı)"]
    return True


def kapida_kalanlar(ham: str, index: dict | None) -> list[tuple[str, str]]:
    """🔴🔴 `§YS-2` — **KAPIDA GERİ ÇEVRİLENİ OKUMAK.**

    ⊙ Ölçüldü (curl `GG` turu): *«bu yıl toplam ciroyu **euro** olarak göster»* →

        ham={"cube":"parti","measures":["toplam_ciro"],
             "filters":[{"dimension":"para_birimi","operator":"eq","value":"EUR"}]}
        → intent: whitelist REDDİ

    🔴 Model «euro»yu **atmıyor** — kataloğumuzda olmayan bir boyutla **temsil etmeye
    çalışıyor**. Beyaz liste o adayı reddediyor, oy euro'dan habersiz başka bir örneğe
    düşüyor ve kullanıcı ₺ cinsinden bir sayıyı **güvenle** alıyor.

    ⊙ Bu, `§YS`'nin (garsona *«ne attın»* diye sormak) **ölçülmüş sınırını** açıkladı:
    garsonun cevabı boştu, çünkü kendi zihninde **atmadı**. Ama bilgi kayıp değil —
    **kapıda** duruyor: `para_birimi` / `EUR` tam olarak *«temsil edemediğimiz şey»*dir.

    ⚠ Deterministik: bir LLM iddiası değil, **beyaz listenin kendi kararı**. Katalogda
    olmayan her boyut/ölçü adı ve onun değeri toplanır.

    *Bir hakemin ne attığını sormadan önce, kapıda kimi geri çevirdiğine bakmak
    gerekir.*

    Döner: `[(alan_adı, denenen_değer)]` — boş liste, geri çevrilen bir şey yok demek.
    """
    import json

    try:
        cq = json.loads(ham or "")
    except Exception:                     # noqa: BLE001 — hasat susar
        return []
    if not isinstance(cq, dict):
        return []
    # ⚠ Kaynak `index` — yani `parse_cube_query`'nin **kendi** beyaz listesi. İkinci bir
    # katalog okuması yazmak, kapının kararıyla beyanın kararını ayrıştırırdı (`KAT-1`).
    _spec = (index or {}).get(str(cq.get("cube") or ""))
    if not isinstance(_spec, dict):
        return []
    _boyut = {str(d) for d in (_spec.get("dimensions") or [])}
    _olcu = {str(m) for m in (_spec.get("measures") or [])}
    out: list[tuple[str, str]] = []
    for f in (cq.get("filters") or []):
        if not isinstance(f, dict):
            continue
        _d = str(f.get("dimension") or "")
        _v = f.get("value")
        if _d and _d not in _boyut and not isinstance(_v, (list, dict)):
            out.append((_d, str(_v)))
    for m in (cq.get("measures") or []):
        if str(m) not in _olcu:
            out.append((str(m), ""))
    for d in (cq.get("dimensions") or []):
        if str(d) not in _boyut:
            out.append((str(d), ""))
    # 🔴🔴 **REDDEDİLEN ÖRNEĞİN «yok_sayilan»'ı DA ÇÖPE GİDİYORDU.**
    #
    # ⊙ Ölçüldü (curl `GG` turu): *«mars gezegenindeki satışlarımız»* →
    # `ham={"cube":null,"yok_sayilan":["mars gezegeni","satışlar"]}` → whitelist REDDİ.
    # Yani garson **tam da istediğimiz cevabı verdi** — ve `parse_cube_query` `None`
    # dönünce onunla birlikte o cevap da düştü. `§YS` kanalı yalnız **kabul edilen**
    # örneklerde okunuyordu; oysa bir sözcüğü temsil edemediğini söyleyen örnek, tam
    # olarak **reddedilen** örnektir.
    #
    # ⚠ Alan adı boş bırakılır (`("", sözcük)`): beyan onu bir katalog alanı gibi değil,
    # kullanıcının **kendi sözcüğü** gibi yazar. Topraklama süzgeci ikisinde de aynı.
    #
    # *Bir kapıda geri çevrilen kâğıdın üstünde, neden geri çevrildiği de yazılıdır.*
    for w in (cq.get("yok_sayilan") or []):
        if isinstance(w, str) and len(w.strip()) >= 3:
            out.append(("", w.strip()))
    return out[:3]


def _kapsanmayan(q: str, cq: dict, sema: dict | None) -> list[str]:
    """Sorunun, teslim edilen fişin **hiçbir parçasıyla** açıklanmayan içerik sözcükleri.

    ⚠ Gövde `cube_router`'ın kendi kapsam kapısıdır (`partial_unknowns` → `_uncovered`,
    dolgu kökleri ve kısa sözcükler zaten elenir) — ikinci bir kapsam tanımı yazmak
    `KAT-1` olurdu.
    """
    from app import cube_router as _cr

    try:
        _bilinmeyen = _cr.partial_unknowns(_cr._norm(q or ""), sema or {})[0]
    except Exception:                     # noqa: BLE001 — beyan susar
        return []
    # ⚠ **SİNONİMLER DE FİŞİN PARÇASIDIR.** Kapı bunu yakaladı: yalnız adlar taranınca
    # *«ciroyu»* kapsanmamış sayılıyordu, oysa `ciro` `toplam_ciro`'nun sinonimi ve
    # cevap onu **taşıyor**. Bir terimi adıyla aramak, ona verdiğimiz adları unutmaktır.
    _c = next((c for c in ((sema or {}).get("cubes") or [])
               if c.get("name") == cq.get("cube")), None) or {}
    _parca = [str(cq.get("cube") or ""), str(cq.get("period_expr") or "")]
    for _k, _alanlar in (("measure_synonyms", cq.get("measures") or []),
                         ("dimension_synonyms", cq.get("dimensions") or [])):
        for _ad in _alanlar:
            _parca.append(str(_ad))
            _parca += [str(x) for x in ((_c.get(_k) or {}).get(str(_ad)) or [])]
    _fis = _cr._norm(" ".join(_parca))
    return [w for w in _bilinmeyen if len(w) >= 4 and not _cr._syn_hit(_fis, w)][:2]


def _hicbir_kupte_yok(alan: str, sema: dict | None) -> bool:
    """Bu alan adı **katalogda hiç** yok mu? (Uydurulmuş bir kavram mı, yoksa başka bir
    küpte duran gerçek bir boyut mu.)"""
    _a = str(alan or "").split(".")[-1]
    return bool(_a) and not any(
        _a in (c.get("dimensions") or []) or _a in ((c.get("measure_expressions") or {}))
        for c in ((sema or {}).get("cubes") or []))


def kapi_beyani(resp, q: str, cq: dict, kalanlar: list[tuple[str, str]],
                sema: dict | None = None) -> bool:
    """`§YS-2`'nin **iliştirme** yarısı — `§YS`'nin kardeşi, aynı disiplinle.

    ⚠ **Topraklama süzgeci** (`§101.1`): denenen alan ya da değeri sorunun bir sözcüğüyle
    en az **üç harflik bir ön ek** paylaşmalı (`EUR` ↔ *«euro»*). Model kataloğa
    dokunmayan bir alan uydurmuşsa (soruda hiçbir izi yoksa) beyan **susar** — yoksa
    kullanıcıya kendi sormadığı bir şeyi *«yansımadı»* diye anlatırdık.

    ⚠ Ve teslim edilen fişte o alan **varsa** susulur: karşılanmış bir şey atılmamıştır.
    """
    from app import cube_router as _cr

    if not kalanlar:
        return False
    _kelime = {w for w in re.findall(r"[a-z]+", _cr._norm(q or "")) if len(w) >= 3}
    _fis = {str(d) for d in (cq.get("dimensions") or [])} | {
        str(f.get("dimension")) for f in (cq.get("filters") or [])}
    _gecti: list[str] = []
    for _alan, _deger in kalanlar:
        if _alan and _alan in _fis:
            continue                       # cevapta zaten var → atılmamış
        # 🔴🔴 **TOPRAKLAMA, UYDURULMUŞ BİR KAVRAMDA ARANMAZ — ölçüm öğretti.**
        #
        # ⊙ Ölçüldü (curl `II` turu): *«bu yıl **dolar** bazında toplam ciro»* → model
        # `kur.para_birimi = "TL"` denedi ve beyaz liste reddetti. Süzgeç sustu, çünkü
        # denenen **değer** (`TL`) kullanıcının sözcüğüne (*«dolar»*) bağlanmıyordu.
        # Ama beyan yine de **doğru** olurdu: kataloğumda para birimi diye bir şey yok.
        #
        # ⚠ Ayrım şu: alan **başka bir küpte** duran gerçek bir boyutsa, onu istemediği
        # hâlde kullanıcıya söylemek gürültüdür — orada topraklama şart. Alan
        # **hiçbir küpte** yoksa, model bir kavram **uydurmuştur** ve o kavram ancak
        # sorudan gelebilir; orada topraklama aramak, doğru beyanı susturmaktır.
        #
        # *Bir sözcüğün izini ararken, izin bıraktığı şeyin var olup olmadığına da
        # bakmak gerekir.*
        _aday = [_cr._norm(x) for x in (_deger, _alan) if x]
        _uydurma = bool(_alan) and _hicbir_kupte_yok(_alan, sema)
        if _uydurma:
            # 🔴 **UYDURULMUŞ ALAN «BİR ŞEY DÜŞTÜ» DER; ARTIK «KULLANICI ONA NE DEDİ»Yİ.**
            # Alanın kendi adı (`kur.para_birimi`) kullanıcının sözcüğüne (*«dolar»*)
            # bağlanmaz — ve bağlanmadığı için ilk sürüm **sustu**. Ama iki sinyal
            # birlikte tamdır: uydurulmuş alan **düşme olayının** kanıtı, kapsanmayan
            # artık ise **adın** kendisi. ⚠ Artık tek başına kullanılmaz — bu deponun
            # ölçtüğü yanlış-pozitif tam olarak oydu (*«söyler misin»*).
            _art = _kapsanmayan(q, cq, sema)
            if _art:
                _s = f"«{_art[0]}»"
                if _s not in _gecti:
                    _gecti.append(_s)
            continue
        if not any(w.startswith(a[:3]) or a.startswith(w[:3])
                   for a in _aday if len(a) >= 3 for w in _kelime):
            continue                       # soruda izi yok → gürültü, susulur
        # ⚠ Tekilleştirme: `k=3` örneklemede **aynı** alanı iki örnek denemiş olabilir
        # ve canlıda tam bu oldu (*«`para_birimi` = «EUR» · `para_birimi` = «EUR»»*).
        # Bir şeyi iki kez söylemek, iki ayrı kusur varmış gibi okunur.
        _s = (f"«{_deger}»" if not _alan
              else f"`{_alan}`" + (f" = «{_deger}»" if _deger else ""))
        if _s not in _gecti:
            _gecti.append(_s)
    if not _gecti:
        return False
    resp.note = " ".join(x for x in [getattr(resp, "note", None), (
        f"⚠ Soruda geçen {' · '.join(_gecti[:2])} bu cevaba **yansımadı** — "
        f"kataloğumda karşılığı yok.")] if x)
    resp.trace = [*(getattr(resp, "trace", None) or []),
                  f"§YS-2: beyaz liste {len(_gecti)} alanı geri çevirdi, beyan edildi"]
    return True
