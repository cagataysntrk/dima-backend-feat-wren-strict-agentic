"""🔴🔴 KÖK-1 · **NİYET NESNESİ** — çözümleme ile eşleştirme ayrılsın. (FAZ 1)

## Raporun teşhisi

> *"KN-4 (uyum denetimi) **yazılamaz** çünkü karşılaştırılacak iki şey yok. KN-2 (çok
> sahip) **kaçınılmaz** çünkü «bu bir çekim mi?» sorusunun sahibi yok. KN-1 **kaçınılmaz**
> çünkü taşınacak durum bir nesne değil."*

⊡ Ölçüldü: `app/` içinde `Niyet` sınıfı **yoktu**. Sorunun anlamı `route()`'un içinde,
yerel değişkenlerde, dönüş anında **kaybolarak** yaşıyordu. Ve bu turda o boşluk **beş
ayrı yerde** ayrı ayrı doldurulmuştu:

| modül | ne okuyor | ne için |
|---|---|---|
| `app/uyum.py` | kıyas · çok-dönem · trend · kırılım · üstünlük · eşik · dışlama | beyanlı kısmi cevap |
| `app/yetenek.py` | forecast · olumsuzluk · iki-cube ölçüsü | *"yapamıyorum"* |
| `app/donem_capasi.py` | dönem filtresi | takip turunda çapa |
| `app/turetme.py` | bilinmeyen kelimeler | türetme chip'i |
| `app/belirsizlik_chipi.py` | eşleşen ölçü terimi | belirsizlik beyanı |

🔴 Beşi de **aynı soruyu** soruyor ve beşi de **kendi cevabını** üretiyor. Bu, deponun
adını koyduğu *"aynı kuralın iki sahibi"* sınıfının **beşe katlanmış** hâli.

## 🔴 FAZ 1 — GÖZLEMCİ, ve bu bilinçli

Raporun kapı ölçütü aynen: *"`Niyet` üretilir ve **loglanır**; `route()` davranışı
**BİREBİR aynı** kalır. Sıfır gerileme, tam görünürlük."*

Bu modül **hiçbir kararı değiştirmez**. `route()` onu görmez, `ask()` onu tüketmez.
Tek tüketicisi **iz** (`trace`) ve **kapı**dır (`test_kok1_niyet.py`), ve kapı onun
mevcut okuyucularla **aynı şeyi söylediğini** ölçer.

⚠ Neden bu adım *"ölü kod"* değil: deponun kuralı *ölü kod zararsız değildir* der ve
haklıdır. Buradaki fark, tüketicinin **ölçüm** olması: Faz 2'de tüketiciler tek tek
taşınacak ve her taşımada *"nesne ile eski okuyucu aynı mı"* sorusu **zaten yazılmış**
bir kapıyla cevaplanacak. *Bir göçün ilk adımı, iki tarafın aynı şeyi söylediğini
kanıtlamaktır.*

## ⚠ YENİ DİLBİLİM YAZILMIYOR

Raporun şartı: *"`_syn_hit` · `_covers` · `_ek_gecerli` · `_cekimli_token` ·
`compare_mode` · `_kiyas_spanlari` — **hepsi zaten var**, dağınık. Yeni dilbilim
**yazılmıyor**, var olan **tek çatı altına alınıyor**."*

Bu dosyada **tek bir regex yok**. Her alan mevcut bir fonksiyonun çağrısıdır; `test_
kok1_niyet.py::test_YENI_DILBILIM_YAZILMADI` bunu AST ile kilitler.

## Ne taşıyabiliyor — ve neden bu bir YETENEK maddesi

Raporun *"savunmacı değil **genişletici** tek maddesi"*: `Niyet` **çok dönem · çok ölçü ·
iki cube** taşıyabilir — bugün `CubeQuery`'nin **temsil edemediği** her şey. `donemler`
bir **liste**dir; `route()` tek aralığa çökmek zorundadır, `Niyet` çökmez.
*Bir şeyi temsil edemeyen sistem, onu göremez de.*
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from typing import Any

#: 🔴 İSTEK-KAPSAMLI BELLEK — ve Faz 2'nin **ön koşulu**.
#:
#: Ölçüldü (2026-08-06): reddedilen bir soruda `partial_unknowns` **DÖRT KEZ** koşuyordu
#: (`_niyet_izi` · `_turetme_adaylari` · `ask`in kendi netleştirme dalı · …). Niyet
#: nesnesi *"tek çatı"* olacaksa, çatıya girmek **ucuz** olmalı: aksi hâlde her yeni
#: tüketici tam bir yeniden-çözümleme ekler ve tek çatı, dağınık okuyuculardan **pahalı**
#: hâle gelir — yani KÖK-1'in kendisi bir maliyet kalemine dönüşür.
#:
#: ⚠ Kapsam **istek**tir, süreç değil: `ContextVar` her istekte kendi değerini taşır
#: (`cube_router._reddi_var` ile aynı desen). Süreç ömrü boyunca önbelleklemek, şema
#: değiştiğinde bayat bir niyet üretirdi — ve bu operasyon bayat okumanın bedelini
#: **ölçtü** (`tests/test_olcum_semasi_taze.py`).
#:
#: *Bir soyutlamanın benimsenmesi, ona girmenin maliyetiyle ters orantılıdır.*
_BELLEK: contextvars.ContextVar[dict] = contextvars.ContextVar("niyet_bellek")


def bellek_sifirla() -> None:
    """İstek sınırında çağrılır — yeni istek, yeni bellek."""
    _BELLEK.set({})


def _bellekten(anahtar: str, uret):
    try:
        d = _BELLEK.get()
    except LookupError:
        return uret()                    # istek dışı çağrı (lab/test) → önbelleksiz
    if anahtar not in d:
        d[anahtar] = uret()
    return d[anahtar]

#: Niyet türleri — **kapalı** küme. Yeni bir tür eklendiğinde uyum denetimi de eklenir
#: (KÖK-2'nin *"mekanizma kendini genişletir"* ilkesi).
TUR_TOPLAM = "toplam"        # tek sayı
TUR_KIRILIM = "kirilim"      # boyut bazında dağılım
TUR_TREND = "trend"          # zaman ekseni
TUR_KIYAS = "kiyas"          # iki dönem/değer karşılaştırması
TUR_LISTE = "liste"          # satır dökümü
TUR_USTUNLUK = "ustunluk"    # en yüksek/düşük N


@dataclass(frozen=True)
class Niyet:
    """Sorunun **anlamı** — bir `CubeQuery` değil, ondan ÖNCEKİ katman.

    ⚠ `frozen`: niyet bir **okuma**dır, bir çalışma alanı değil. Değiştirilebilir olsaydı
    tüketiciler onu yerinde düzeltmeye başlar ve *"kim değiştirdi"* sorusu doğardı —
    tam da bu nesnenin kapatmak için var olduğu belirsizlik.
    """

    soru: str

    # ── ÇÖZÜMLEME (şema GEREKMEZ) — kullanıcı NE İSTEDİ ────────────────────────
    #
    # 🔴 Raporun başlığı: *"çözümleme ile eşleştirme AYRILSIN."* Bu blok sorunun
    # **dilinden** okunur; katalog bilinmese de doğrudur. Faz 2'de `uyum`un okuduğu
    # yedi soru-sinyalinin **hepsi** burada olmalı — ölçüldü ve ilk yazımda ÜÇÜ
    # eksikti, İKİSİ farklı okunuyordu (`trend` · `kırılım` · `üstünlük`).
    #
    # ⚠ Ayrımın somut hâli: *"kullanıcı kırılım İSTEDİ mi"* çözümlemedir (`kirilim_istendi`),
    # *"hangi boyut EŞLEŞTİ"* eşleştirmedir (`kirilimlar`). İkisini tek alanda taşımak,
    # tam da bu nesnenin ayırmak için var olduğu iki şeyi karıştırmaktı.
    kirilim_istendi: bool = False
    trend_istendi: bool = False
    ustunluk_istendi: bool = False
    dislama_istendi: bool = False

    # ── EŞLEŞTİRME (şema GEREKİR) — katalogda NE BULUNDU ───────────────────────
    olcu_adaylari: list[tuple[str, str]] = field(default_factory=list)   # (cube, ölçü)
    #: **ÇÖZÜLEBİLEN** dönem filtreleri — `CubeQuery`ye girecek olanlar.
    donemler: list[dict] = field(default_factory=list)
    #: 🔴 Sorunun **ADIYLA SAYDIĞI** dönem sayısı — çözülebilse de çözülemese de.
    #: İkisinin farkı, raporun *"bilgi var, temsil yok"* cümlesinin **sayısal hâlidir**:
    #: `ocak ve haziran ciro` → `donem_sayisi=2` ama `donemler=[]`, çünkü `CubeQuery`
    #: ayrık iki ayı taşıyamaz ve `date_filters` bu yüzden **boş** döner.
    #: *Bir sistemin temsil edemediği şeyi SAYABİLMESİ, onu görebilmesinin ilk adımıdır.*
    donem_sayisi: int = 0
    kirilimlar: list[str] = field(default_factory=list)
    filtreler: list[dict] = field(default_factory=list)
    turler: set[str] = field(default_factory=set)
    ustunluk: int | None = None                                          # top-N (sayılı)
    granulerlik: str | None = None
    bilinmeyenler: list[str] = field(default_factory=list)

    @property
    def cok_donem(self) -> bool:
        """🔴 Soru birden çok dönem **adıyla** anıyor mu — çözülebilirlikten bağımsız."""
        return self.donem_sayisi > 1

    #: 🔴 `§B.4` — **ROUTE'UN ÇEKİLME SEBEBİ ADLANDIRILDI** (⟳ 2026-08-12).
    #: Kapalı küme; `KÖK-1`'in *«sistem temsil edemediği şeyi SAYABİLSİN»* ilkesi.
    SEBEP_COK_SAHIP = "cok_sahipli_terim"
    SEBEP_BILINMEYEN = "bilinmeyen_token"
    SEBEP_OLCU_YOK = "olcu_bulunamadi"

    @property
    def cekilme_sebebi(self) -> str | None:
        """🔴🔴 `§B.4` — **ROUTE ÇEKİLİYORSA, NEDEN?**

        ## Ölçülen boşluk

        `§B.1`'de doğrulandı: çok sahipli bir terimde `route()` **`None`** dönüyor ve
        kural **uygulanıyor**. Ama `None` **sebepsizdi**: *«`adet` altı küpe işaret
        ediyor»* ile *«bu kelimeyi hiç tanımıyorum»* aynı boşluğa düşüyordu.

        ⊙ Sonuç: garsonun yükünün **ne kadarının** belirsizlikten geldiği bilinemiyordu —
        ve `§A.2`'nin **73 çok-sahipli terimlik** borcunun **ürün maliyeti** ölçülemiyordu.

        ## Neden bir alan DEĞİL, bir türev

        `referans`'ın gerekçesinin aynısı (`KAT-1`): bir alan olsaydı *«kim doldurur»*
        sorusu doğardı — `_coz_soru` mu, `route()` mü, `ask.py` mi? Türev olduğunda
        **doldurulacak bir yer yoktur**: niyet neyse sebep odur.

        ⚠ **Bu bir tahmin değil bir SINIFLANDIRMADIR**: yalnız `Niyet`'in **zaten
        taşıdığı** alanlardan okunur (`olcu_adaylari` · `bilinmeyenler`). Yeni bir
        ölçüm, yeni bir liste, yeni bir eşik **yok**.

        Döner: kapalı kümeden bir sebep ya da `None` (*«çekilecek bir şey yok»*).
        """
        if len({c for c, _m in self.olcu_adaylari}) >= 2:
            # 🔴 Aynı terim **iki farklı küpe** işaret ediyor: `§A.2`'nin 73 teriminden
            # biri. Bu bir bilgisizlik değil, bir **çokluk** — ve ikisi ayrı şeydir.
            return self.SEBEP_COK_SAHIP
        if self.bilinmeyenler:
            return self.SEBEP_BILINMEYEN
        if not self.olcu_adaylari:
            return self.SEBEP_OLCU_YOK
        return None

    @property
    def referans(self) -> dict | None:
        """🔴 `G6.4` — KIYASIN İKİ UCU: `{eksen, kaynak, hedef}`. **TEK TEMSİL.**

        ## Neden bir alan DEĞİL, bir türev

        `referans` bir alan olsaydı, onu **kim doldurur** sorusu doğardı: `_coz_soru`
        mu, `route()` mü, `parse_cube_query` mi? Üçü de dolduracak konumda ve üçü de
        biraz farklı doldururdu — bu deponun bir numaralı kusur sınıfı (`KAT-1`,
        *aynı kuralın iki sahibi*). Türev olduğunda **doldurulacak bir yer yoktur**:
        soru neyse referans odur.

        *Bir değeri iki yerden yazılabilir yapmak, iki değeri garanti etmektir.*

        ## Sahibi neden `Niyet`

        Planın `G6.4`'ü: *"`referans` bilgisi `app/niyet.py`'de doğar; ikinci sahip
        yok."* Doğru yer burasıdır çünkü referans **sorunun** bir özelliğidir, sorgunun
        değil: *"mart'ı şubatla kıyasla"* cümlesi, hangi cube'a gittiğinden bağımsız
        olarak iki uç taşır. `CubeQuery`'deki `referans` bunun **izdüşümüdür**.

        ⚠ Kapsamı `donem` ekseniyle sınırlı — kapalı sözlüğün öteki dördünün sahibi
        başka modüller (`kiyas_cebiri.EKSENLER` tablosu). Burada bir eksen **icat
        edilmez**; yalnız cebrin indirgeyebildiği ilan edilir.
        """
        if TUR_KIYAS not in self.turler:
            return None
        from app import kiyas_cebiri

        return _guvenli(lambda: kiyas_cebiri.referans_uret(self.donemler), None)

    @property
    def temsil_edilemeyen(self) -> list[str]:
        """🔴 **Bu nesnenin var olma sebebi.** Sorunun taşıdığı ama `CubeQuery`ye
        giremeyen niyet işaretleri.

        `route()` bunları döndüremez çünkü dönüş tipi onları **taşıyamaz**; `Niyet`
        taşır ve `uyum` bugün bunu **cq üzerinden geriye doğru** çıkarmak zorunda
        kalıyor. Faz 2'de o hesap buraya taşınacak.
        """
        out = []
        # 🔴 `G6.4` — **KAYITLI BORÇ KAPANDI.** `test_r11_ifade_edilemez.py`'nin şerhi:
        # *"`route()` indirgeme yapsa bile iz hâlâ «temsil-yok» yazar… iz YANILTICI."*
        # Sebebi buydu: bu hesap **yalnız kaç dönem adlandığına** bakıyordu, o dönemlerin
        # temsil edilip edilemediğine değil. Artık `referans` cevabı biliyor — ve o cevap
        # cebrin kendi indirgeyicisinden geliyor, yani izle sorgu **aynı kaynağa** bakıyor.
        #
        # ⚠ İki uçlu kıyas indirgenebiliyorsa temsil edilebilir demektir: `compare`
        # kurulur, `yoy.compute` iki seriyi hesaplar. *Bir eksiği bildirmeye devam etmek,
        # o eksik kapandıktan sonra, kusurun kendisidir.*
        if self.cok_donem and len(self.donemler) <= 2 and not self.referans:
            out.append("cok_donem")      # ≥2 dönem adlandı, en fazla bir aralık çözüldü
        if TUR_KIYAS in self.turler and not self.cok_donem:
            out.append("kiyas")          # kıyas fiili var, kıyaslanacak ikinci uç yok
        return out

    def iz(self) -> str:
        """Tek satırlık **görünürlük** — Faz 1'in tek ürünü budur."""
        parca = [f"tür={'+'.join(sorted(self.turler)) or '?'}"]
        if self.temsil_edilemeyen:
            parca.append(f"🔴temsil-yok={','.join(self.temsil_edilemeyen)}")
        if self.olcu_adaylari:
            parca.append(f"ölçü={len(self.olcu_adaylari)}")
        if self.donem_sayisi:
            parca.append(f"dönem={self.donem_sayisi}"
                         + ("" if self.donemler else "(çözülemedi)"))
        if self.kirilimlar:
            parca.append(f"kırılım={','.join(self.kirilimlar[:3])}")
        if self.ustunluk:
            parca.append(f"üstünlük={self.ustunluk}")
        if self.granulerlik:
            parca.append(f"granülerlik={self.granulerlik}")
        if self.bilinmeyenler:
            parca.append(f"bilinmeyen={','.join(self.bilinmeyenler[:3])}")
        return "niyet: " + " · ".join(parca)


def coz_soru(soru: str) -> Niyet:
    """İstek-kapsamlı belleğe alınmış `_coz_soru` — sözleşme aynı, maliyet bir kez."""
    return _bellekten(f"soru:{soru}", lambda: _coz_soru(soru))


def _coz_soru(soru: str) -> Niyet:
    """🔴 **ÇÖZÜMLEME — şemasız.** Sorunun dilinden okunan niyet.

    Raporun KÖK-1 başlığı *"çözümleme ile eşleştirme ayrılsın"* der ve bu fonksiyon o
    ayrımın somut hâlidir: katalog bilinmese de doğru olan her şey buradadır.

    ## Neden ayrı bir giriş noktası

    `uyum.denetle(q, cq, cube_meta)` **şema almıyor** — yalnız tek bir `cube_meta`.
    Faz 2'de onu `Niyet`e taşımak için niyetin şemasız üretilebilmesi **zorunluydu**.
    ⊙ Yani ayrımı zorlayan şey bir tasarım tercihi değil, **ilk müşterinin sözleşmesi**
    oldu. *Bir soyutlamanın doğru sınırını, onu ilk kullanan çizer.*

    ⚠ Yedi sinyalin **hepsi** kendi sahibinden gelir; burada tek bir kalıp yok.
    """
    from app import cube_router as cr
    from app import uyum as _uyum

    q = cr._norm(soru)
    turler: set[str] = set()

    donemler = _guvenli(lambda: cr.date_filters(q), [])
    filtreler = list(donemler)
    esik = _guvenli(lambda: cr._measure_threshold(q), None)
    if esik:
        filtreler.append(esik)

    donem_sayisi = max(_guvenli(lambda: _uyum._cok_donem(soru), 0), 1 if donemler else 0)
    # 🔴 `G6` — KIYAS İKİ BİÇİMDE GELİR ve eskiden yalnız biri sayılıyordu.
    #
    # `compare_mode` **göreli** kıyastır (*"geçen yıla göre"* → `yoy`/`mom`); tüketicileri
    # onunla göreli SQL kurar, bu yüzden **iki uçlu** kıyasa `None` demesi doğrudur.
    # Ama `TUR_KIYAS`'ın tek kaynağı o olunca *"mart cirosunu şubat ile kıyasla"* sorusu
    # niyet nesnesinde **kıyas SAYILMIYORDU** — ve `uyum` kapısı da oradan okuduğu için
    # sessiz kalıyordu. Ölçüldü: o soru **1 Şubat–31 Mart toplamını** döndürüyor ve
    # hiçbir kapı etiketlemiyordu.
    #
    # *Bir niyeti sökebilen sistem (`strip_compare`) onu sayabilmelidir de.*
    if (_guvenli(lambda: cr.compare_mode(q), None)
            or _guvenli(lambda: cr.kiyas_niyeti(q), False)):
        turler.add(TUR_KIYAS)
    if _guvenli(lambda: cr.liste_niyeti(q), False):
        turler.add(TUR_LISTE)

    gran = _guvenli(lambda: cr._time_gran(q), None)

    # 🔴 TREND — `uyum._TREND` ("değişim/artış/seyir") ile `_time_gran` ("aylara göre")
    # AYRI şeylerdir. İlk yazımda ikisi tek alanda toplandı ve `uyum`un okuması ile
    # ayrıştı. *Bir alanı iki kaynaktan doldurmak, iki alanı bir kaynaktan doldurmaktan
    # daha tehlikelidir: ikincisi eksik olur, birincisi YANLIŞ.*
    trend = bool(_guvenli(lambda: _uyum.trend_istendi(q), False))
    if trend or gran:
        turler.add(TUR_TREND)

    # 🔴 ÜSTÜNLÜK iki ayrı soruya cevap verir ve ikisi de gerekir:
    #   · `ustunluk_istendi` — *"en çok"* dendi mi (SAYI gerekmez) → `uyum`un sorusu
    #   · `ustunluk`         — kaç tane (`en yüksek 5`)            → `route`un sorusu
    ustunluk_var = bool(_guvenli(lambda: _uyum.ustunluk_istendi(q), False))
    ustunluk = _guvenli(lambda: cr._top_n(q), None)
    if ustunluk or ustunluk_var:
        turler.add(TUR_USTUNLUK)

    # 🔴 `Ö10` — *"…-e **göre**"* HER ZAMAN KIRILIM DEĞİL. Ölçülen kusur:
    # *"şubatta ciro **ocağa göre** nasıl değişti"* → `tür=kirilim+trend`, ve `uyum`
    # kullanıcıya *«bir kırılım istedin ama boyut taşıyamadım»* diyordu. Kullanıcı kırılım
    # **istemedi**; `gore` bir kıyas edatıydı.
    #
    # 🔴 Yanlış bir beyan, sessizlikten kötüdür: sistem kullanıcıya **onun söylemediği bir
    # şeyi söylediğini** söylüyor — ve bu, güvenin en hızlı tükendiği yerdir.
    #
    # ⚠ Ayrım `cube_router.gore_donem_mi`'de ve **yapısal**: `gore`'den önce çözülebilir
    # bir dönem ifadesi varsa o `gore` kırılım işareti değildir. Ölçüt `date_filters`'ın
    # kendisi — ikinci bir dönem tanıyıcısı yazılmaz.
    #
    # ⚠ Kapsam **bilinçli olarak dar**: yalnız NİYET tarafı (yani beyan). `route()`'un
    # kendi `_BREAKDOWN_HINTS` korumaları (`:994` · `:1328` · `:3578`) dokunulmadan
    # bırakıldı — onlar sessiz-yanlış kapılarıdır ve kapsamları korpusla ölçülür.
    # *Bir ayrımı önce beyanda düzeltmek, onu yönlendirmede düzeltmekten ucuzdur.*
    kirilim_istendi = bool(_guvenli(
        lambda: cr._herhangi(q, cr._BREAKDOWN_HINTS)
        and not cr.gore_donem_mi(q), False))
    dislama = bool(_guvenli(
        lambda: cr._herhangi(q, cr._EXCLUDE_MARKERS), False))
    if kirilim_istendi:
        turler.add(TUR_KIRILIM)
    if not turler:
        turler.add(TUR_TOPLAM)

    return Niyet(soru=soru, donemler=donemler, donem_sayisi=donem_sayisi,
                 filtreler=filtreler, turler=turler, ustunluk=ustunluk,
                 granulerlik=gran, kirilim_istendi=kirilim_istendi,
                 trend_istendi=trend, ustunluk_istendi=ustunluk_var,
                 dislama_istendi=dislama)


def coz(soru: str, schema: dict[str, Any]) -> Niyet:
    """İstek-kapsamlı belleğe alınmış `_coz` — sözleşme aynı, maliyet bir kez.

    ⚠ Anahtar **yalnız soruyu** taşır: bir istek içinde şema değişmez (tek tenant, tek
    derleme). Şemayı anahtara katmak onu hash'lemeyi gerektirirdi ve bu, önbelleğin
    kazandırdığından pahalı olurdu.
    """
    return _bellekten(f"tam:{soru}", lambda: _coz(soru, schema))


def _coz(soru: str, schema: dict[str, Any]) -> Niyet:
    """🔴 **ÇÖZÜMLEME + EŞLEŞTİRME.** Şemasız niyeti alır, katalog bulgularıyla zenginleştirir.

    ⚠ Gövde `coz_soru`yu **çağırır, kopyalamaz**. Kopyalasaydı bu nesne — ayırmak için var
    olduğu kusuru — kendi içinde üretirdi. *Bir çatının ilk sınavı, kendi kendini
    tekrarlamamasıdır.*

    ⚠ `dataclasses.replace`: `Niyet` `frozen`dır ve öyle kalmalı; zenginleştirme bir
    **yeni nesne** üretir, bir yerinde-düzeltme değil.
    """
    import dataclasses

    from app import cube_router as cr

    temel = coz_soru(soru)
    q = cr._norm(soru)

    adaylar = [(c.get("name", ""), m)
               for c, m in _guvenli(lambda: cr.measure_cube_candidates(q, schema), [])]
    bilinmeyen = _guvenli(lambda: cr.partial_unknowns(q, schema)[0], [])
    kirilimlar = _kirilimlar(cr, q, schema, adaylar)

    turler = set(temel.turler)
    if kirilimlar:
        turler.add(TUR_KIRILIM)
    if turler != {TUR_TOPLAM}:
        turler.discard(TUR_TOPLAM)

    return dataclasses.replace(temel, olcu_adaylari=adaylar, kirilimlar=kirilimlar,
                               turler=turler, bilinmeyenler=list(bilinmeyen),
                               filtreler=[*temel.filtreler, *_varlik_filtreleri(soru, schema)])


def _varlik_filtreleri(soru: str, schema: dict[str, Any]) -> list[dict]:
    """🔴 `§51` — SORUDA GEÇEN **KATALOG DEĞERİ** bir filtredir.

    ## Ölçülen kusur (kullanıcı ekranı, 2026-08-13)

    `q=«ram 3»` için pill satırı yalnız `['toplam']` gösteriyordu. Ölçüldü:
    `niyet.coz("ram 3")` → `filtreler=[]` **ve** `bilinmeyenler=[]` — yani `RAM 3`
    ne tanınıyor ne de *«bilmiyorum»* diye bildiriliyordu; **sessizce düşüyordu**.
    Oysa `route()` aynı değeri buluyor ve `varlik.perdele` onu **doğru** çıkarıyor
    (`«ram 3»` → `RAM 3`, `«RAM-3 fire»` → `RAM-3`).

    ⟹ Eksik olan bir yetenek değil bir **çağrıydı** 🆘.

    ⚠ Yeni eşleştirici **yazılmadı**: değeri `varlik.perdele`, boyutunu
    `varlik.boyutu` söylüyor ㊲. Boyut bulunamazsa filtre **üretilmez** — bir
    değeri boyutsuz filtrelemek, sorguyu sessizce yanlış yapardı ㊱.
    """
    from app import varlik

    out: list[dict] = []
    try:
        _, harita, _ = varlik.perdele(soru, schema)
    except Exception:                                   # noqa: BLE001
        return out
    for deger in harita.values():
        boyut = varlik.boyutu(deger, schema)
        if boyut:
            out.append({"dimension": boyut, "operator": "eq", "value": deger})
    return out


def _kirilimlar(cr, q: str, schema: dict, adaylar: list[tuple[str, str]]) -> list[str]:
    """Sorunun istediği kırılımlar — **aday cube'ların boyutlarından**, sırayla.

    ⚠ Cube seçimi burada YAPILMAZ: `Niyet` bir eşleştirme değil bir okumadır. Aday
    cube'ların hepsinin boyutları taranır ve eşleşenler **tekilleştirilerek** döner.
    Hangisinin kazanacağı eşleştiricinin (`route()`) işidir.
    """
    out: list[str] = []
    adlar = {a for a, _ in adaylar} or {c.get("name") for c in (schema.get("cubes") or [])}
    for c in schema.get("cubes") or []:
        if c.get("name") not in adlar:
            continue
        for d in _guvenli(lambda c=c: cr._match_dims(q, c), []) or []:
            ad = d if isinstance(d, str) else str(d)
            if ad not in out:
                out.append(ad)
    return out


def _guvenli(f, varsayilan):
    """Bir çözümleyici patlarsa **niyet düşmez**, o alan boş kalır.

    ⚠ ADR-0020 *"sessiz yutma yok"* der ve haklıdır — ama burada yutulan bir **cevap**
    değil bir **gözlem**dir ve alternatifi, gözlemin cevabı düşürmesidir. Log yazılır.
    """
    from app.logging_setup import get_logger

    try:
        return f()
    except Exception:
        get_logger("niyet").warning("niyet alanı çözülemedi", exc_info=True)
        return varsayilan
