"""🔴🔴 **`§DK-2` — SÜZGEÇ DEĞERİ ÇAPASI: uydurulmuş bir değer, sessiz bir sıfır satırdır.**

## Ölçülen kusur (canlı curl turu, 2026-08-10)

Garson (`Intent-JSON`) bir süzgeç kurarken **değeri de kendisi yazıyor** ve o değerin
gerçekten var olup olmadığını **hiçbir şey sormuyordu**:

    «oee düşük olan makinelerin bakım maliyeti»
        → filters: [{dimension: "makine", operator: "eq", value: "Bakım"}]
        → `maliyet.makine` gerçek değerleri: RAM-1 · RAM-2 · KONTİNÜ KASAR …
        → sonuç: **0 satır**, beyan **yok**

⊙ Kullanıcı bunu *"bakım maliyeti sıfırmış"* diye okur. Bir uydurma sayı değil, bir
**uydurma yokluk** — ve yokluğun uydurması daha sinsidir, çünkü sıfır bir cevap gibi
görünür.

## Neden route bunu görmüyordu

`route()` değer eşleşmesini `value_index.FuzzyIndex` ile **zaten** yapıyor
(`cube_router:3714`). Ama garsonun ürettiği `cube_query` o yoldan **geçmiyor**: garson
kataloğu okur, süzgeci yazar, derleyici çalıştırır. Yani doğrulama **route'a özeldi** ve
merdivenin ikinci basamağında karşılığı **yoktu**.

*Bir kural yalnız bir basamakta geçerliyse, o kural değil bir tesadüftür.*

## 🔴 SIRA BİR TASARIM KARARIDIR — bu kapı `§DK`'dan ÖNCE yazılamazdı

`§DK` (`wren_service._enrich_cube_dim_values`) düzeltilmeden önce katalog enum'ları
**yalan söylüyordu**: `parti.musteri` → `M1001…` (oysa veri *TOROS ÖRME TİC. LTD. ŞTİ.*
tutuyor), `kalite.vardiya` → `1·2·3` (oysa veri `'1. Vardiya (08-16)'`). Bu kapı o gün
kurulsaydı **doğru** sorguları reddederdi ve kusuru düzeltmek yerine **kilitlerdi**.

*Bir doğrulayıcı, doğruladığı kaynaktan daha güvenilir olamaz.*

## Sözleşme

* **Yalnız TAM enum'lar.** `wren_service` bir boyutun değerlerini ancak **sayılabildiğinde**
  yazıyor (`0 < len ≤ _MAX_ENUM`); çok değerli boyutta **kayıt hiç yok**. Yani listede
  yoksa **gerçekten yok** — yokluk bir örneklem kırpması değil. Kaydı olmayan boyutta bu
  kapı **hiçbir şey söylemez** (`§101.1`: yanlış-pozitif yüklem, kusurdan pahalıdır).
* **Yalnız kimlik operatörleri**: `eq · neq · in · nin`. `contains` bir alt-dizedir,
  karşılaştırmalar (`gt · lt · gte · lte`) sıralıdır — ikisi de enum üyeliği sormaz.
* **Zaman boyutu dışarıda**: tarih bir enum değildir.
* **Üç sonuç, üçü de BEYANLI**:
  1. değer listede → dokunulmaz (`KURAL B`: bayrak kapalıyken zaten hiç koşmaz)
  2. listede yok ama **tek** bir yakın karşılığı var → düzeltilir **ve söylenir**
  3. listede yok, yakın karşılık da yok → sorgu **koşturulmaz**; gerçek değerler
     **chip** olarak sunulur

⚠ Üçüncüsü bir *"anlamadım"* değildir: kullanıcıya cevaplanabilir bir soru ve tıklanabilir
bir liste döner. *Dürüst bir red bir başarı değildir; dürüst bir SORU bir cevaptır.*
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app import yayilim as _yayilim

#: Enum üyeliği sorulabilen operatörler. ⚠ Liste **kapalı**: yeni bir operatör
#: eklendiğinde bu kapı ona sessizce uygulanmasın — sessiz genişleme, ölçülmemiş
#: davranış demektir.
KIMLIK_OPERATORLERI: frozenset[str] = frozenset({"eq", "neq", "in", "nin"})

#: 🔴🔴 `§TK` — **SIRALI OPERATÖR, KATEGORİK BOYUTTA BİR TÜR HATASIDIR.**
#:
#: ⊙ Canlı ölçüm (curl turu, 2026-08-10): *«bu yıl fire oranı %20 üstü olan hatlar»* →
#: garson `{"dimension":"hat","operator":"gt","value":"20"}` üretti — yani **hat adını
#: 20 ile karşılaştırdı**. Sekiz hattın hepsi döndü, süzgeç hiçbir şey yapmadı, beyan yok.
#:
#: ⚠ Kimlik kapısı (`§DK-2`) bunu **göremiyordu**: `gt` bir üyelik sormaz, o yüzden
#: `KIMLIK_OPERATORLERI` dışındaydı ve atlanıyordu. Ama hata **kanıtlanabilir**: boyutun
#: **tam enum'u** varsa ve o enum'da **hiçbir değer sayı değilse**, sıralı bir
#: karşılaştırma tanımsızdır — bir metin etiketi *«20'den büyük»* olamaz.
#:
#: ⊙ Ve bu, kullanıcının asıl istediğinin **ölçü eşiği** (`measure_having`) olduğunun da
#: işaretidir: *«%20 üstü»* bir satırın değil, **toplanmış ölçünün** eşiğidir.
#:
#: ⚠ Fail-closed: enum yoksa **yargı yok**; enum'da bir tek sayı bile varsa **yargı yok**
#: (kod-benzeri boyutlar `«1»·«2»` gerçekten sıralanabilir).
#:
#: *Bir süzgeç, karşılaştırdığı iki şeyin aynı türden olduğunu varsayar; bu varsayım
#: yanlışsa sonuç boş değil ANLAMSIZDIR — ve anlamsız bir sonuç sessizce doğru görünür.*
SIRALI_OPERATORLER: frozenset[str] = frozenset({"gt", "gte", "lt", "lte"})

#: Yakın-eşleşme eşiği. `value_index._ratio` ile aynı ölçek. 0.82 seçildi çünkü
#: `«Bakim» ↔ «Bakım»` (tek harf) geçmeli, `«Bakım» ↔ «RAM-1»` geçmemeli.
YAKINLIK_ESIGI: float = 0.82

#: Chip'te gösterilecek en fazla gerçek değer. Uzun bir liste bir menü değil bir
#: duvardır; kullanıcı 40 seçeneği okumaz.
EN_FAZLA_SECENEK: int = 8


@dataclass
class Bulgu:
    """Bir süzgeç değerinin kataloğa karşı yargısı."""

    boyut: str
    deger: str
    #: Tek bir yakın karşılık bulunduysa onun **gerçek** yazımı; yoksa `None`.
    oneri: str | None = None
    #: Boyutun tam enum'u (kırpılmamış) — çağıran chip üretirken kırpar.
    gecerliler: list[str] = field(default_factory=list)
    #: 🔴 `§TK` — sıralı operatör + metin enum. **Anlamsızlığı KANITLI** olduğu için
    #: netleştirme değil **düşürme** gerektirir (bkz. `duzelt_yerinde`).
    tur_hatasi: bool = False
    #: 🔴🔴 `§NT` — **DIŞLAMA OPERATÖRÜNDE «YOK» BİR BELİRSİZLİK DEĞİL, BİR YOK-İŞLEMDİR.**
    #:
    #: ⊙ Canlı ölçüm (curl `N` turu, 2026-08-10): *«bu yıl en kötü bakım maliyeti hangi
    #: makinede»* → garson `{"dimension":"makine","operator":"neq","value":"Bakım"}`
    #: üretti. `§DK-2` bunu *«listede yok»* diye yakaladı ve **kullanıcıya sordu** —
    #: oysa sorulacak bir şey yoktu.
    #:
    #: 🔴 Ayrım **kanıt sınıfıdır**, üslup değil:
    #:
    #: | operatör | değer listede yok | ne demektir |
    #: |---|---|---|
    #: | `eq` / `in` | ⊙ **belirsizlik** | kullanıcı gerçekten o değeri kastetmiş olabilir → **sor** |
    #: | `neq` / `nin` | ✅ **yok-işlem** | var olmayan bir değeri dışlamak **hiçbir satırı** dışlamaz → **düşür** |
    #:
    #: İkincisinde düşürmek davranışı **birebir korur** (kanıtlı), yani bir kapsam
    #: değişikliği değildir. `§TK-2`'nin sınıfı: *kanıtlı anlamsız bir süzgeç
    #: düşürülür ve söylenir.*
    #:
    #: *Aynı gözlem («bu değer listede yok») iki operatörde iki ayrı şey kanıtlar; ikisine
    #: aynı kararı vermek, kanıta değil kelimeye bakmaktır.*
    bos_islem: bool = False
    #: 🔴 `§YT` — değer bir **perdeleme yuvasıdır** (`{{ENT_1}}`), yani hiçbir zaman bir
    #: kullanıcı değeri değildi. `bos_islem` gibi düşürülür ama **adı yazılmaz**.
    yuva: bool = False
    #: 🔴 `§DB` — değer, süzdüğü **boyutun kendi adıdır** (*«operator = Operatör»*).
    #: `bos_islem` gibi düşürülür ama beyanı **kendi cümlesidir**: kullanıcı bir kırılım
    #: istemişti ve neden süzgeç görmediğini bilmelidir.
    boyut_adi: bool = False


def _norm(s: str) -> str:
    from app import cube_router as cr

    return cr._norm(str(s))


def _sayi_mi(x) -> bool:
    """Değer bir sayı olarak okunabiliyor mu? — `§TK`'nin fail-closed yüklemi."""
    try:
        float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return False
    return True


def _enum(cq: dict, schema: dict | None) -> dict[str, list[str]]:
    """Hedef küpün **tam** enum haritası. Küp bulunamazsa boş — ve boş, *"bilmiyorum"*
    demektir, *"yok"* değil."""
    kup = (cq or {}).get("cube")
    if not kup:
        return {}
    for c in (schema or {}).get("cubes") or []:
        if c.get("name") == kup:
            return {k: list(v) for k, v in (c.get("dimension_values") or {}).items() if v}
    return {}


def _zaman_adlari(cq: dict, schema: dict | None) -> set[str]:
    kup = (cq or {}).get("cube")
    for c in (schema or {}).get("cubes") or []:
        if c.get("name") == kup:
            return {str(t) for t in (c.get("time_dimensions") or [])}
    return set()


def _yakin(deger: str, gecerliler: list[str]) -> str | None:
    """Tek bir yakın karşılık varsa onu döndür. **İki aday varsa `None`** — çünkü
    hangisi olduğunu bilmiyoruz ve tahmin etmek bu kapının kapatmaya çalıştığı kusurun
    ta kendisidir.

    İki yol, bu sırayla:

    1. **Yazım yakınlığı** (`value_index._ratio`) — *«DİJİTAL BASKII» → «DİJİTAL BASKI»*
    2. **TEKİL ÖNEK** — *«3» → «3. Vardiya (00-08)»*

    🔴 İkincisi canlı bir ölçümden doğdu: garson `vardiya eq "3"` yazdı, kapı *«listede
    yok»* dedi ve **haklıydı** — ama kullanıcının kastettiği besbelliydi. Bir netleştirme
    burada dürüsttü ama **gereksizdi**; *dürüst bir red bir başarı değil, çözülecek bir
    borçtur.* Önek yolu yalnız **tek aday** kalırsa çalışır: `«RAM»` hem `RAM-1` hem
    `RAM-2`'yi çağırır ve orada soru sormak doğru kalır.
    """
    from app.value_index import _ratio

    n = _norm(deger)
    adaylar = [(g, _ratio(n, _norm(g))) for g in gecerliler]
    iyi = sorted((a for a in adaylar if a[1] >= YAKINLIK_ESIGI), key=lambda x: -x[1])
    if iyi and not (len(iyi) > 1 and abs(iyi[0][1] - iyi[1][1]) < 1e-9):
        return iyi[0][0]
    onekler = [g for g in gecerliler if _norm(g).startswith(n)]
    return onekler[0] if len(onekler) == 1 else None


def _sorudan_kurtar(soru: str, gecerliler: list[str]) -> str | None:
    """🔴🔴 `§DK-5` — **KULLANICI DEĞERİ ZATEN YAZMIŞSA SORMAK BİR KUSURDUR.**

    ⊙ Canlı ölçüm (curl `N` turu, 2026-08-10):

        «AKDENİZ ÖRME için bu yıl ciro»
          → garson: musteri eq "M1001"        ← UYDURMA kod
          → §DK-2 : «M1001 listede yok» + 8 gerçek ad chip

    Davranış dürüsttü ama **gereksizdi**: kullanıcı gerçek adın (`AKDENİZ ÖRME TEKSTİL
    A.Ş.`) tam önekini **kendi eliyle yazmıştı**. Sistem elindeki cevabı sordu.

    ## Neden `_yakin` bunu bulamıyor — ve kök bu

    `_yakin` **garsonun ürettiği değere** bakar (`M1001`). O değer hiçbir şeye yakın
    değildir; olması da gerekmez — çünkü kanıt orada değil, **kullanıcının cümlesinde**.
    Yani kusur bir eşik ayarı değil, **yanlış yüzeye bakmak**.

    ⊙ Doğru yüklem depoda **zaten var**: `deger_eslesme.deger_eslesmeleri` route'un aynı
    işi için yazıldı (tam eşleşme, yoksa **tekil** çekirdek eşleşmesi) ve `§DK-3`'te
    kapılandı. İkinci bir eşleştirici yazmak `KAT-1` olurdu — o kavram **çağrılır**.

    ⚠ Sınır **tekillik**: soruda iki geçerli değer birden anılıyorsa `None` döner ve
    netleştirme aynen çalışır. *Belirsizlikte tahmin etmemek bu deponun tek kuralıdır
    ve bir kurtarma yolu onun istisnası olamaz.*

    *Bir soruyu sormadan önce, cevabın soruyu soranın cümlesinde yazılı olup olmadığına
    bakmak gerekir.*
    """
    if not soru:
        return None
    import re as _re

    from app import deger_eslesme as _de

    qn = _norm(soru)
    eslesme = _de.deger_eslesmeleri(qn, list(gecerliler))
    if len(eslesme) == 1:
        return eslesme[0]
    if eslesme:
        return None                      # ⚠ iki tam eşleşme → belirsizlik, tahmin YOK
    # 🔴 **ÖNEK YOLU — ve neden ayrı bir kural.**
    #
    # `deger_eslesmeleri` değerin **tamamını** (ya da çekirdeğini) arar ve bu bilinçli:
    # `§DK-3`'ün ölçümü `«EGE KNIT DIŞ TİCARET LTD. ŞTİ.»`nin kuyruğunun bir açıklama
    # değil **adın parçası** olduğunu kaydetti. Ama hiçbir kullanıcı şirketin tam
    # ticari unvanını yazmaz — *«AKDENİZ ÖRME»* yazar.
    #
    # ⚠ Bu yüzden önek **kelime** sayar, harf değil: tek kelimelik bir önek
    # (*«akdeniz»*, *«ege»*) cümlenin ortasında tesadüfen bulunabilir; **iki** kelimelik
    # bitişik bir dizi bir tesadüf değil bir **atıftır**.
    # ⚠ Ve **tekillik** yine şart: iki değerin aynı iki-kelimelik öneki varsa `None`.
    en_iyi: tuple[int, str] | None = None
    esit = False
    for g in gecerliler:
        kelimeler = [w for w in _norm(g).split() if w]
        k = 0
        for n in range(len(kelimeler), 1, -1):
            onek = " ".join(kelimeler[:n])
            if _re.search(rf"(?:^|\W){_re.escape(onek)}(?:\W|$)", qn):
                k = n
                break
        if not k:
            continue
        if en_iyi is None or k > en_iyi[0]:
            en_iyi, esit = (k, g), False
        elif k == en_iyi[0]:
            esit = True
    return None if (en_iyi is None or esit) else en_iyi[1]


def _boyutun_kendi_adi(deger: str, boyut: str, cq: dict, schema: dict | None) -> bool:
    """`§DB` — değer, süzdüğü **boyutun kendi adı** mı? (ad · etiket · sinonim)

    ⚠ Kaynak **katalog**: `dimension_labels` ve `dimension_synonyms`. Bir kelime listesi
    yazmak, her yeni katalogda elle bakım isterdi (ADR-0008).
    """
    _d = _norm(deger)
    if not _d:
        return False
    kup = next((c for c in ((schema or {}).get("cubes") or [])
                if c.get("name") == cq.get("cube")), {}) or {}
    # 🔴🔴 **SİNONİMLER BU SORUYA CEVAP VEREMEZ — ve bunu kapı ölçerek gösterdi.**
    #
    # ⊙ İlk yazımda `dimension_synonyms` de ad sayılıyordu ve tam kapı **iki kırmızı**
    # verdi (`test_kirilimli_soru_da_donem_sorar` + `eval` precision `1.0 → 0.9741`):
    # katalog `cinsiyet`in **DEĞERLERİNİ** sinonim yazmış — `[cinsiyet, kadın, erkek,
    # cinsiyete göre]` — çünkü kullanıcı *«kadın çalışanlar»* deyince boyut bulunsun.
    # Yani sinonim kümesi bilerek **değer** taşır; onu *«boyutun adı»* diye okumak
    # meşru bir süzgeci (`cinsiyet = Kadın`) **silmek** demekti.
    #
    # ⚠ Kaynak yalnız **ad** ve **etiket**: ikisi de tanım gereği boyutun kendisidir.
    # *Bir kümeyi ne için kurulduğunu sormadan kullanmak, onun taşıdığı şeyi değil
    # adını ödünç almaktır.*
    adlar = {_norm(boyut)}
    _et = (kup.get("dimension_labels") or {}).get(boyut)
    if _et:
        adlar.add(_norm(str(_et)))
    return _d in adlar


def denetle(cq: dict, schema: dict | None, soru: str = "") -> list[Bulgu]:
    """Süzgeç değerlerini kataloğun **tam** enum'una karşı doğrula.

    Boş liste = *"itiraz yok"*. Bu bir iyimserlik değil bir **kapsam beyanıdır**: enum'u
    olmayan boyutta yargı **verilmez**.

    `soru` verilirse (`§DK-5`) karşılıksız bir değer için önce **kullanıcının kendi
    cümlesi** yoklanır — orada tekil bir karşılık varsa netleştirmeye hiç gerek kalmaz.
    """
    if not isinstance(cq, dict):
        return []
    enumlar = _enum(cq, schema)
    if not enumlar:
        return []
    zamanlar = _zaman_adlari(cq, schema)
    out: list[Bulgu] = []
    for f in cq.get("filters") or []:
        if not isinstance(f, dict):
            continue
        boyut = str(f.get("dimension") or "")
        op = str(f.get("operator") or "")
        if boyut in zamanlar:
            continue
        gecerliler = enumlar.get(boyut)
        if not gecerliler:
            continue                                 # ⚠ enum yok → yargı yok
        # 🔴 `§TK` — sıralı operatör + tamamen metin enum = **tür hatası**.
        if op in SIRALI_OPERATORLER:
            if not any(_sayi_mi(g) for g in gecerliler):
                out.append(Bulgu(boyut=boyut, deger=str(f.get("value")),
                                 oneri=None, gecerliler=list(gecerliler),
                                 tur_hatasi=True))
            continue
        if op not in KIMLIK_OPERATORLERI:
            continue
        bilinen = {_norm(g) for g in gecerliler}
        ham = f.get("value")
        degerler = ham if isinstance(ham, (list, tuple)) else [ham]
        for d in degerler:
            if d is None or not str(d).strip():
                continue
            # 🔴 `§YT` — **BİR YUVA, BİR DEĞER DEĞİLDİR.** Perdeleme yuvası (`{{ENT_1}}`)
            # geri konmadan süzgece girmişse bu bir kullanıcı belirsizliği değil bir
            # **taşıma kusurudur**; onu adıyla anmak kullanıcıya iç mekanizmayı gösterir.
            # ⊙ Canlıda ölçüldü: *«⚠ Etkisiz bir dışlama düşürüldü («{{ENT_1}}» ∉ makine)»*.
            # Desen `yayilim`'ın (üreticinin) yanında durur — ikinci bir tanıyıcı `KAT-1`
            # olurdu. Süzgeç yine düşer (yuva hiçbir kaydı seçemez), yalnız **sessizce**.
            if _yayilim.yuva_mu(d):
                out.append(Bulgu(boyut=boyut, deger=str(d), oneri=None,
                                 gecerliler=list(gecerliler), bos_islem=True,
                                 yuva=True))
                continue
            if _norm(str(d)) in bilinen:
                continue
            # 🔴🔴 `§DB` — **BİR BOYUTUN ADI, O BOYUTUN DEĞERİ OLAMAZ.**
            #
            # ⊙ Ölçüldü (curl `X` turu, X18): *«bu yıl **operatör bazında** ilk seferde
            # doğru oranı»* → garson (self-consistency **%100**) şu süzgeci yazdı:
            #
            #     {"dimension": "operator", "operator": "eq", "value": "Operatör"}
            #
            # `§DK-2` bunu dürüstçe yakaladı ve *«hangisini istersin»* diye **dokuz
            # operatör adı** listeledi. Cümle doğruydu ama kullanıcı bir **kırılım**
            # istemişti — yani dürüst bir red, **çıkmaz** bir reddi oldu.
            #
            # 🔴 Kök garsonun tercihinde: *«X bazında»* kalıbındaki `X`'i bir **değer**
            # sandı. Ve bu bir dil sorunu değil bir **tür** sorunudur: hiç kimse
            # `operator = "Operatör"` diye süzmez. Kanıt katalogdadır — değer, süzdüğü
            # boyutun **kendi adı/etiketi**dir.
            #
            # ⚠ Yüklem bilerek **dar**: yalnız değer, boyutun kendi ad/etiket/sinonim
            # kümesine eşitse düşer. Bir kelime listesi değil, **kimlik karşılaştırması**.
            # ⚠ Ve sessiz değil: süzgeç düşer, kullanıcı ne olduğunu **okur** (`bos_islem`
            # beyanı) — cevabın kendisi de artık gerçek kırılımı verir.
            #
            # *Bir boyutu adıyla süzmek, bir listeyi kendi başlığıyla filtrelemektir.*
            if _boyutun_kendi_adi(str(d), boyut, cq, schema):
                out.append(Bulgu(boyut=boyut, deger=str(d), oneri=None,
                                 gecerliler=list(gecerliler), bos_islem=True,
                                 boyut_adi=True))
                continue
            # 🔴 `§NT` — DIŞLAMADA «yok» = **yok-işlem**, kapsayışta «yok» = belirsizlik.
            # Var olmayan bir değeri dışlamak hiçbir satırı dışlamaz; kanıt tamdır ve
            # düşürmek davranışı birebir korur. Bkz. `Bulgu.bos_islem`.
            if op in ("neq", "nin"):
                out.append(Bulgu(boyut=boyut, deger=str(d), oneri=None,
                                 gecerliler=list(gecerliler), bos_islem=True))
                continue
            out.append(Bulgu(boyut=boyut, deger=str(d),
                             # `§DK-5`: önce garsonun değerine (yazım yakınlığı), sonra
                             # **kullanıcının cümlesine** bak. Sıra bilinçli: yakın yazım
                             # bir düzeltmedir, sorudan kurtarma bir **kanıttır** — ama
                             # yakın yazım zaten doğruysa ikincisini koşmak israftır.
                             oneri=(_yakin(str(d), gecerliler)
                                    or _sorudan_kurtar(soru, gecerliler)),
                             gecerliler=list(gecerliler)))
    return out


def _coklu_esitlik_birlestir(cq: dict) -> str | None:
    """🔴🔴 `§ÇE` — **AYNI BOYUTA ÜST ÜSTE `eq` YAZMAK BİR SÜZGEÇ DEĞİL, BİR ÇELİŞKİDİR.**

    ⊙ Canlı ölçüm (curl `N` turu, 2026-08-10): *«ram makinesinin bu yıl fire oranı»* →
    garson üç ayrı süzgeç yazdı:

        makine eq "RAM-1"  AND  makine eq "RAM-2"  AND  makine eq "RAM-3"

    Süzgeçler `AND`'lenir; bir satırın `makine` alanı aynı anda üç değer **olamaz** →
    sonuç **yapısal olarak** boş. Ve cevabın notu şunu yazdı:

        «Bu aralıkta kayıt bulunamadı — dönemi genişletmek ister misin?»

    🔴 Boşluğun sebebi dönem **değildi**; beyan suçu yanlış yere attı. *Bir boşluğu
    yanlış sebebe bağlamak, boşluğun kendisinden pahalıdır: kullanıcı doğru olan
    dönemi değiştirmeye çalışır.*

    ## Neden `in` — ve neden bu bir tahmin değil

    `A eq X AND A eq Y` (X≠Y) **her zaman** boş döner: bilgi taşımayan bir sorgudur.
    Geriye iki okuma kalır — birini **düşürmek** (kullanıcının andığı bir değeri
    sessizce atmak) ya da **birleştirmek** (`in [X, Y]`). İkincisi anılan **her**
    değeri korur, yani kanıta daha sadıktır; ve **beyan edilir**.

    ⚠ Kapsam dar: yalnız `eq`, yalnız **farklı** değerler, yalnız aynı boyut. Aynı değer
    tekrarlanmışsa (`A eq X AND A eq X`) anlam değişmez → sessizce tekilleştirilir.
    ⚠ `denetle`'den **bağımsızdır**: çelişki sorgunun kendisinden kanıtlanır, enum
    gerektirmez. Bu yüzden enum'suz boyutlarda da çalışır.
    """
    filtreler = [f for f in (cq.get("filters") or []) if isinstance(f, dict)]
    sayac: dict[str, list[dict]] = {}
    for f in filtreler:
        if str(f.get("operator") or "") == "eq":
            sayac.setdefault(str(f.get("dimension") or ""), []).append(f)
    hedefler = {b: fs for b, fs in sayac.items() if len(fs) > 1}
    if not hedefler:
        return None
    soylenen: list[str] = []
    yeni: list[dict] = []
    goruldu: set[str] = set()
    for f in filtreler:
        boyut = str(f.get("dimension") or "")
        if boyut not in hedefler or str(f.get("operator") or "") != "eq":
            yeni.append(f)
            continue
        if boyut in goruldu:
            continue
        goruldu.add(boyut)
        degerler: list = []
        for g in hedefler[boyut]:
            v = g.get("value")
            if v not in degerler:
                degerler.append(v)
        if len(degerler) == 1:
            yeni.append({"dimension": boyut, "operator": "eq", "value": degerler[0]})
            continue                     # aynı değer tekrarı → anlam değişmedi, susulur
        yeni.append({"dimension": boyut, "operator": "in", "value": degerler})
        soylenen.append(f"**{boyut}**: " + " · ".join(f"«{d}»" for d in degerler))
    cq["filters"] = yeni
    if not soylenen:
        return None
    return ("🔎 Aynı boyuta birden çok eşitlik yazılmıştı (hiçbir satır iki değeri birden "
            "taşıyamaz) — hepsi tek bir **çoklu seçim** olarak uygulandı: "
            + " · ".join(soylenen) + ".")


def duzelt_yerinde(cq: dict, bulgular: list[Bulgu]) -> str | None:
    """Önerisi olan bulguları `cq` üzerinde **yerinde** düzelt ve beyan metnini döndür.

    ⚠ Önerisi **olmayan** bulgulara dokunmaz — onlar çağıranın netleştirme kararıdır.
    ⚠ `cq` yerinde değişir çünkü bu deponun süzgeç düzeltme deseni odur
    (`donem_capasi.tasi_yerinde`); ikinci bir dönüş türü her çağıranı değiştirirdi.
    """
    # 🔴🔴 `§TK-2` — **ANLAMSIZ BİR SÜZGEÇ DÜŞÜRÜLÜR, TURU DÜŞÜRMEZ.**
    #
    # ⊙ Canlı ölçüm (curl turu, 2026-08-10): *«%20 üstü olan hatlar»* → garson
    # `{"dimension":"hat","operator":"gt","value":"20"}` üretti. `§TK` bunu yakaladı ve
    # **sorguyu bloke etti** — ama aynı turda deterministik eşik zaten uygulanmıştı
    # (`niyet_tasima.esik`, huni sırası: eşik 2735 → değer çapası 2832 → derleme 2849).
    # Yani doğru cevap **hazırdı** ve kapı onu tutuyordu.
    #
    # ⊙ Ayrım şu: *«bu değer listede yok»* bir **belirsizliktir** — kullanıcı gerçekten
    # o değeri kastetmiş olabilir, sormak gerekir. Ama *«hat adı > 20»* bir **tür
    # hatasıdır** ve anlamsızlığı **kanıtlıdır**: bir metin etiketi bir sayıdan büyük
    # olamaz. Kanıtlı anlamsız bir süzgeç, kullanıcının kastettiği şey **olamaz**.
    #
    # ⚠ Bu yüzden düşürülür **ve söylenir** — sessizce değil. *Bir sınırı aşmıyoruz;
    # anlamsız bir şeyi anlamlıymış gibi davranmayı bırakıyoruz.*
    dusen = [b for b in bulgular if b.tur_hatasi]
    if dusen:
        _at = {(b.boyut, _norm(b.deger)) for b in dusen}
        cq["filters"] = [f for f in (cq.get("filters") or [])
                         if not (isinstance(f, dict)
                                 and (str(f.get("dimension") or ""),
                                      _norm(str(f.get("value")))) in _at)]
    # 🔴 `§NT` — YOK-İŞLEM DIŞLAMALARI DÜŞÜRÜLÜR. `tur_hatasi`'ndan **ayrı** tutulur
    # çünkü beyanı da ayrıdır: orada bir **anlamsızlık** vardı, burada bir **etkisizlik**.
    # ⚠ Liste operatöründe (`nin`) yalnız karşılıksız üyeler atılır; kalanlar gerçek
    # birer dışlamadır ve düşürülmeleri kapsamı değiştirirdi.
    bos = [b for b in bulgular if b.bos_islem]
    if bos:
        _atB: dict[str, set[str]] = {}
        for b in bos:
            _atB.setdefault(b.boyut, set()).add(_norm(b.deger))
        kalan: list = []
        for f in (cq.get("filters") or []):
            if not isinstance(f, dict) or str(f.get("dimension") or "") not in _atB:
                kalan.append(f)
                continue
            _hedef = _atB[str(f.get("dimension") or "")]
            ham = f.get("value")
            if isinstance(ham, (list, tuple)):
                kalanlar = [d for d in ham if _norm(str(d)) not in _hedef]
                if kalanlar:
                    f["value"] = kalanlar
                    kalan.append(f)
                continue
            if _norm(str(ham)) not in _hedef:
                kalan.append(f)
        cq["filters"] = kalan
    esleme = {(b.boyut, _norm(b.deger)): b.oneri for b in bulgular if b.oneri}
    if not esleme and not dusen and not bos:
        return None
    # 🔴 `§DB` — **kendi cümlesi.** *«Etkisiz bir dışlama»* burada yalan olurdu: ortada
    # bir dışlama yok, bir **tür karışıklığı** var — kullanıcı kırılım istedi, süzgeç
    # yazıldı. Ve cümle ne yapıldığını söyler ki kullanıcı sayının kapsamını bilsin.
    _ba = [b for b in bulgular if b.boyut_adi]
    if _ba and not esleme and not dusen:
        adlar = " · ".join(f"«{b.deger}» = **{b.boyut}** boyutunun kendi adı"
                           for b in _ba)
        return (f"⚠ Bir süzgeç düşürüldü ({adlar}): bir boyutu **kendi adıyla** süzmek "
                f"hiçbir kaydı seçmez — soru bir **kırılım** olarak okundu ve tüm "
                f"kayıtlar üzerinden hesaplandı.")
    if bos and not esleme and not dusen:
        # `§YT` — yuvalar **adlandırılmaz**: kullanıcıya iç mekanizma gösterilmez.
        # Hepsi yuvaysa beyan da yazılmaz; söylenecek bir kullanıcı bilgisi yoktur.
        adlandirilabilir = [b for b in bos if not b.yuva and not b.boyut_adi]
        if not adlandirilabilir:
            return None
        adlar = " · ".join(f"«{b.deger}» ∉ **{b.boyut}**" for b in adlandirilabilir)
        return (f"⚠ Etkisiz bir dışlama düşürüldü ({adlar}): listede olmayan bir değeri "
                f"dışlamak hiçbir kaydı elemez.")
    if dusen and not esleme:
        adlar = " · ".join(f"«{b.deger}» → **{b.boyut}**" for b in dusen)
        # ⚠ **YAPTIĞIMDAN FAZLASINI SÖYLEME.** İlk yazım *«Eşik ölçünün kendisine
        # uygulandı»* diyordu — ama bu fonksiyon eşiği **uygulamaz**, yalnız anlamsız
        # süzgeci düşürür. Canlıda ölçüldü ve cümle o an **yalandı**. Bugün üçüncü kez
        # aynı ders (`§BD` · `§UY/K` · bu): *bir beyan, ölçebildiğinden fazlasını
        # söylediği anda bir varsayıma dönüşür.*
        return (f"⚠ Anlamsız bir süzgeç düşürüldü ({adlar}): bir metin etiketi bir "
                f"sayıyla karşılaştırılamaz.")
    soylenen: list[str] = []
    for f in cq.get("filters") or []:
        if not isinstance(f, dict):
            continue
        boyut = str(f.get("dimension") or "")
        ham = f.get("value")
        if isinstance(ham, (list, tuple)):
            yeni = []
            for d in ham:
                hedef = esleme.get((boyut, _norm(str(d))))
                if hedef:
                    soylenen.append(f"«{d}» → «{hedef}»")
                    yeni.append(hedef)
                else:
                    yeni.append(d)
            f["value"] = yeni
        else:
            hedef = esleme.get((boyut, _norm(str(ham))))
            if hedef:
                soylenen.append(f"«{ham}» → «{hedef}»")
                f["value"] = hedef
    if not soylenen:
        return None
    return ("🔎 Süzgeç değeri katalogla eşleştirildi: " + " · ".join(soylenen)
            + ". Farklı bir değer istersen yaz.")


def netlestirme_metni(bulgular: list[Bulgu]) -> str:
    """Karşılığı **hiç** olmayan değerler için kullanıcıya dönen cümle.

    🔴 *"Anlamadım"* demez: neyin bulunmadığını **adıyla** söyler ve neyin bulunduğunu
    gösterir. Bir sınırı söylemek, onu gizlemekten her zaman daha kullanışlıdır.
    """
    yok = [b for b in bulgular if not b.oneri and not b.tur_hatasi and not b.bos_islem]
    if not yok:
        return ""
    # 🔴 **BOYUTA GÖRE GRUPLANIR — ve bunu canlı bir ölçüm istedi.**
    #
    # `D8` turunda garson bir süzgece **beş** geçersiz değer koydu (`T-101`·`T-204`…)
    # ve kapı geçerli listeyi **beş kez** bastı. Doğru olan bir cevaptı ama okunmuyordu.
    #
    # ⊙ *Bir sınırı söylemek ile onu beş kez söylemek aynı şey değildir: ikincisi
    # kullanıcıya cümleyi atlatır ve sınır yine görülmemiş olur.*
    gruplar: dict[str, tuple[list[str], list[str]]] = {}
    for b in yok:
        degerler, gecerliler = gruplar.setdefault(b.boyut, ([], b.gecerliler))
        degerler.append(b.deger)
    parcalar = []
    for boyut, (degerler, gecerliler) in gruplar.items():
        ornek = " · ".join(gecerliler[:EN_FAZLA_SECENEK])
        artan = len(gecerliler) - EN_FAZLA_SECENEK
        if artan > 0:
            ornek += f" … (+{artan})"
        adlar = " · ".join(f"«{d}»" for d in degerler[:EN_FAZLA_SECENEK])
        if len(degerler) > EN_FAZLA_SECENEK:
            adlar += f" … (+{len(degerler) - EN_FAZLA_SECENEK})"
        # ⚠ Cümle **iki ayrı biçimdir**, tek şablonun içine sıkıştırılamaz: ilk yazımda
        # *««20» — bu değeri hat listesinde yok»* çıktı (canlı, `§TK` turu) — dilbilgisi
        # bozuk. *Bir doğru bilgiyi bozuk bir cümleyle vermek, onu yarı yarıya vermektir.*
        parcalar.append(
            (f"{adlar} değerleri **{boyut}** listesinde yok. Var olanlar: {ornek}")
            if len(degerler) > 1 else
            (f"{adlar} **{boyut}** listesinde yok. Var olanlar: {ornek}"))
    return " ".join(parcalar) + " Hangisini istersin?"


def secenekler(bulgular: list[Bulgu]) -> list[dict]:
    """Netleştirme chip'leri — **gerçek** değerlerden üretilir, uydurulmaz."""
    out: list[dict] = []
    for b in bulgular:
        if b.oneri or b.tur_hatasi or b.bos_islem:
            continue
        for g in b.gecerliler[:EN_FAZLA_SECENEK]:
            out.append({"label": str(g), "query": str(g), "kind": "deger"})
    return out[:EN_FAZLA_SECENEK]


def huni_karari(cq: dict, schema: dict | None,
                soru: str = "") -> tuple[str | None, dict | None]:
    """🔴 Huninin **tek çağrısı**: `(beyan_notu, netleştirme_alanları)`.

    ⊙ Bu fonksiyon `ask()`'ten **çıkarıldı** ve bunu bir kapı istedi: modül büyüme
    tavanı kırmızı verdi ve kendi mesajını yazdı — *«yeni davranışı modüle çıkar,
    tavanı yükseltme. Tavanı yükseltmek kapıyı kapının kendisiyle çürütür.»*

    ⚠ Ayrım yapısal olarak da doğru: `ask()` **sırayı** yönetir, bu dosya **kararı**
    verir. Karar üç satırda değil bir kavramda yaşamalı.

    Döner:
      * `(not, None)`   → değer düzeltildi, beyan cevaba eklenecek
      * `(not, alanlar)` → karşılıksız değer var, sorgu **koşturulmayacak**
      * `(None, None)`  → itiraz yok (`KURAL B`: bayrak kapalıyken zaten çağrılmaz)
    """
    # `§ÇE` — çelişki **enum gerektirmez**, sorgunun kendisinden kanıtlanır; bu yüzden
    # `denetle`'den ÖNCE koşar. Sırası da anlamlı: birleştirilen `in` listesi sonra
    # `denetle`'nin kimlik kapısından geçer, yani iki kural birbirini görmüş olur.
    birlestirme = _coklu_esitlik_birlestir(cq)
    bulgular = denetle(cq, schema, soru)
    if not bulgular:
        return birlestirme, None
    duzeltme = duzelt_yerinde(cq, bulgular)
    duzeltme = " ".join(x for x in (birlestirme, duzeltme) if x) or None
    # 🔴 `§TK-2` — **tür hatası netleştirme SEBEBİ DEĞİLDİR:** anlamsızlığı kanıtlı bir
    # süzgeç `duzelt_yerinde` tarafından **düşürüldü** ve beyan edildi; geriye sorulacak
    # bir şey kalmaz. ⚠ Bu satır ilk yazımda atlanmıştı ve canlıda ölçüldü: süzgeç
    # düşüyordu ama tur yine **boş** dönüyordu — *bir kararı değiştirmek, o kararı veren
    # her satırı değiştirmektir.*
    # ⚠ `§NT` aynı satırın ikinci sahibidir ve **atlanması** aynı kusuru üretirdi:
    # yok-işlem `duzelt_yerinde` tarafından düşürüldü, geriye sorulacak bir şey kalmaz.
    # *Bir kararı değiştirmek, o kararı veren her satırı değiştirmektir* — bu ders bu
    # dosyada bugün **ikinci** kez uygulanıyor (`§TK-2`'nin şerhine bak).
    if any(not b.oneri and not b.tur_hatasi and not b.bos_islem for b in bulgular):
        return duzeltme, {"note": netlestirme_metni(bulgular),
                          "secenekler": secenekler(bulgular)}
    return duzeltme, None
