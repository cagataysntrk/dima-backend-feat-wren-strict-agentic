"""🔴 `G2` — **DİYALOG BELLEĞİ**: sistem sorduğunu HATIRLAR.

## Ölçülen kusur

JPMorgan (arXiv 2605.26394, Mayıs 2026): çok-turlu text-to-SQL'de **tur-3 durumsuz
koşulduğunda beş modelin beşi de %0** yürütme doğruluğu verdi; **iki turluk** bir
çalışma penceresiyle **%87,6–100**. Durum taşımak bir iyileştirme değil, **var olma
koşuludur**.

DİMA'da bugün netleştirme **durumsuz**: chip tam bir soru metni taşır
(`belirsizlik_chipi.py:106`), sunucu **hiçbir açık slot saklamaz**, tur **sıfırdan**
koşar. Çok adımlı daraltma (*"hangi küp? → hangi ölçü? → hangi dönem?"*) yapısal olarak
imkânsız: her adım öncekini unutuyor.

## ⚠ Planın «taşınıyor» varsayımı ÇÜRÜDÜ

Yol haritası bu maddeyi *"sıfırdan yazmıyoruz — `0.5b`'nin `netlestirme.birlestir` saf
fonksiyonu çekirdek"* diye tarif ediyordu. **O fonksiyon YOK**
(`grep bekleyen_netlestirme` → 0 isabet; `netlestirme.py` yalnız `duzey`/`sorar_mi`/
`govde_notu`/`kanit_sinifi` tanımlıyor). Bu modül **sıfırdan** yazıldı.

## 🔴 TEK TEMSİL — `Niyet`'in boş alanı

*Açık slot* ikinci bir veri yapısı **değildir**: `Niyet`'in **boş alanıdır**.
`app/niyet.py` zaten `olcu_adaylari` · `donemler` · `kirilimlar` · `granulerlik`
taşıyor; ikinci bir slot dataclass'ı yazmak `KAT-1` ihlali olurdu — ve tam olarak bu
deponun adını koyduğu kusur (*"aynı kuralın iki sahibi"*).

## Taşıma: oturum deposu YOK, YANKI var

Sunucu durumu **saklamaz**; `cube_query`'nin bugün taşındığı gibi taşır: cevapta döner,
istemci bir sonraki istekte **geri yollar**. `context.py`'nin felsefesi burada da geçerli
— *"bağlam çözümü bir anlama işi değil bir MUHASEBE işidir"*.

🔴 Bunun bedeli dürüstçe yazılı: istemci yankılamazsa bellek **yoktur**. Sessiz bir
sunucu-yanı oturum deposu, `thread`/UI gruplamasının semantik sınır taşımasına yol
açardı — bu depoda daha önce ölçülmüş bir kusur sınıfı.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.logging_setup import get_logger

_log = get_logger("diyalog")

#: Bir turun **cevaplanabilmesi için** dolu olması gereken yuvalar.
#: ⚠ Liste kısa ve **kapalı**: her yuva, bugün zaten bir netleştirme dalı tarafından
#: sorulan bir şeydir. Yeni yuva eklemek yeni bir soru sormak demektir ve o, ürün kararı.
SLOT_OLCU = "olcu"
SLOT_DONEM = "donem"
SLOT_CUBE = "cube"

TUM_SLOTLAR = (SLOT_CUBE, SLOT_OLCU, SLOT_DONEM)

_DONEM_ADLARI = ("tarih", "donem", "dönem", "ay", "yil", "yıl", "date", "period")


def acik_slotlar(cube_query: dict | None, *, donem_gerekli: bool = False) -> list[str]:
    """Hangi yuvalar **boş**? Sıra anlamlıdır: cube → ölçü → dönem.

    ⚠ `donem_gerekli` çağırandan gelir çünkü *"dönem şart mı"* kararı bu modülün değil,
    `_period_gate`'in bilgisidir (zaman boyutu var mı · `period_optional` mı). İki yerde
    ayrı ayrı hesaplamak, iki farklı cevap veren iki sahip doğururdu.
    """
    cq = cube_query if isinstance(cube_query, dict) else {}
    acik: list[str] = []
    if not cq.get("cube"):
        acik.append(SLOT_CUBE)
    if not cq.get("measures"):
        acik.append(SLOT_OLCU)
    if donem_gerekli and not _donem_var(cq):
        acik.append(SLOT_DONEM)
    return acik


def _donem_var(cq: dict) -> bool:
    for f in cq.get("filters") or []:
        if isinstance(f, dict) and any(p in str(f.get("dimension", "")).lower()
                                       for p in _DONEM_ADLARI):
            return True
    return bool(cq.get("timeDimensions"))


def odak_belirle(cube_query: dict | None, satirlar: list | None,
                 plan: dict | None = None) -> dict | None:
    """🔴🔴 `B9` — **ODAK VARLIK.** Bu tur tek bir varlığı işaret etti mi? → `{boyut, deger}`

    ## Ölçülen kusur — canlıda İKİ kez, aynı kök

    | thread | tur | soru | olan | olması gereken |
    |---|---|---|---|---|
    | A | 3 | *«peki neden düşük»* | 11 makinenin hepsi | tur 2'nin seçtiği **RAM-3** |
    | B | 5 | *«o ayda hangi makine sorumlu»* | yılın tamamı → Haziran | tur 4'ün seçtiği **ay** |

    ⊙ İkisinde de bir önceki tur **bir varlığı adıyla seçmişti** ve bir sonraki tur ona
    *"o"* / *"peki"* diye atıfta bulundu — ama diyalog durumunda taşınacak bir **odak**
    yoktu. Taze sorulduğunda (*«ram 3 neden düşük»*) sistem doğru çalışıyor; kaybolan
    şey soru değil, **referans**.

    ⚠ Bu, daha önce üç kez yanlış yerden denendi: takip adımlarını *atlayarak*. Üçü de
    ölçüldü ve geri alındı — çünkü eksik olan bir adım değil, bir **bilgiydi**.
    *Bir zinciri, eksik halkasını atlayarak onaramazsın.*

    ## Odak ne zaman KURULUR — ve neden bu üç işaret

    Odak, cevabın **bir tanesini ayırdığı** turlarda kurulur:

    | işaret | neden ayırıyor |
    |---|---|
    | `limit == 1` | cevap zaten tek satır — *«hangisi»* sorulmuş |
    | plan `BAGLA` adımı | orkestratör bir varlığı açıkça **seçti** |
    | `order` + **tek** boyut | sıralı bir kırılımda 0. satır ayrıcalıklıdır |

    ⚠ Sıralama yoksa odak **kurulmaz**: sırasız bir kırılımda 0. satırın hiçbir imtiyazı
    yoktur ve onu odak saymak, motorun satır sırasını bir anlam sanmaktır.

    🔴 Boyut yoksa **zaman ekseni** odak olur (`timeDimensions`) — *«o ayda»* tam olarak
    budur ve bir ay da bir varlıktır.
    """
    if not isinstance(cube_query, dict) or not satirlar:
        return None
    ilk = satirlar[0]
    if not isinstance(ilk, dict):
        return None
    bagla = any(str(a.get("fiil")) == "BAGLA"
                for a in ((plan or {}).get("adimlar") or []) if isinstance(a, dict))
    boyutlar = [b for b in (cube_query.get("dimensions") or []) if isinstance(b, str)]
    # ⚠ EKSEN, `dimensions` DEĞİLDİR: bir ay da bir varlıktır ve o eksende yaşar.
    # İlk yazımda yalnız `dimensions` sayıldı ve *«o ayda»* vakası — odağı en çok
    # gereken vaka — sessizce dışarıda kaldı. İki eksen birdense odak kurulMAZ:
    # hangi varlığın kastedildiği belirsizdir ve *belirsizi seçmek, seçmemekten kötüdür.*
    eksen = len(boyutlar) + len(cube_query.get("timeDimensions") or [])
    ayirdi = cube_query.get("limit") == 1 or bagla or (
        cube_query.get("order") and eksen == 1)
    if not ayirdi:
        return None
    if boyutlar:
        boyut = boyutlar[0]
        deger = ilk.get(boyut)
    else:
        # ⚠ Zaman ekseni sütun adı `<boyut>__<granülerlik>` biçimindedir; satırdan
        # **okunur**, kurallardan türetilmez (`§X1`: zaman ekseni küpten gelir).
        td = (cube_query.get("timeDimensions") or [{}])[0]
        boyut = td.get("dimension") if isinstance(td, dict) else None
        deger = next((v for k, v in ilk.items()
                      if boyut and k.startswith(f"{boyut}__")), None)
        if boyut and deger is not None:
            # 🔴 Zaman odağı bir DEĞER değil bir **KOVA**dır; granülerliği olmadan
            # süzgece çevrilemez. Bkz. `odak_suzgeci` — `eq` ile süzmek, ayın
            # yalnız ilk anını seçmek olurdu.
            return {"boyut": str(boyut), "deger": deger,
                    "granulerlik": str(td.get("granularity") or "month")}
    if not boyut or deger is None:
        return None
    return {"boyut": str(boyut), "deger": deger}


def durum(cube_query: dict | None, *, sorulan: str | None = None,
          onceki: dict | None = None, donem_gerekli: bool = False,
          kismi_cq: dict | None = None, odak: dict | None = None) -> dict | None:
    """Bir turun diyalog durumu — cevapta döner, istemci **yankılar**.

    `sorulan` — bu turda kullanıcıya sorulan yuva (netleştirme dalı bunu bildirir).
    `onceki` — istemcinin yankıladığı bir önceki durum.

    Döner: `{acik_slotlar, sorulan, dolu, tur_no}` — ya da `None` (taşınacak bir şey yok).
    """
    acik = acik_slotlar(cube_query, donem_gerekli=donem_gerekli)
    tur_no = int((onceki or {}).get("tur_no") or 0) + 1
    onceki_acik = list((onceki or {}).get("acik_slotlar") or [])
    dolu = [s for s in onceki_acik if s not in acik]

    # 🔴 `B9` — odak **devralınır**: bu tur bir varlık ayırmadıysa öncekinin odağı
    # yaşamaya devam eder. *Bir konuşmada odak, her cümlede yeniden kurulmaz;
    # değiştirilene kadar sürer.* Aksi hâlde araya giren tek bir nötr tur referansı
    # siler ve kullanıcı neden silindiğini asla göremez.
    odak = odak or (onceki or {}).get("odak")
    if not (acik or sorulan or dolu or odak):
        return None
    out: dict[str, Any] = {"acik_slotlar": acik, "tur_no": tur_no}
    if odak:
        out["odak"] = odak
    if sorulan:
        out["sorulan"] = sorulan
    if dolu:
        out["dolu"] = dolu
    # 🔴 KISMİ SORGU — `devam`ın hammaddesi. Netleştirme dalları `cube_query=None`
    # döndürüyor; o turda ANLAŞILMIŞ olan parça (cube · ölçü) burada taşınmazsa bir
    # sonraki tur onu **yeniden bulmak** zorunda kalır ve `KURAL_TAZE` ateşlenir.
    # *Sorduğunu hatırlamak, sorarken bildiğini de hatırlamaktır.*
    kismi = kismi_cq if isinstance(kismi_cq, dict) else (
        cube_query if isinstance(cube_query, dict) else None)
    if kismi and (kismi.get("cube") or kismi.get("measures")):
        out["kismi_cq"] = {k: v for k, v in kismi.items()
                           if k in ("cube", "measures", "dimensions")}
    return out


def bekleyen_yanit_mi(onceki: dict | None) -> str | None:
    """Bir önceki tur bir yuva **sordu** ve cevabı bekliyor mu? → sorulan yuva adı.

    🔴 Bu, `devam` davranışının **tetikleyicisidir**: bekleyen bir soru varken gelen
    kısa bir ifade (*"geçen ay"*) **yeni bir soru değildir**, bir **cevaptır** —
    `KURAL_TAZE` orada ateşlenmemelidir.
    """
    if not isinstance(onceki, dict):
        return None
    sorulan = onceki.get("sorulan")
    return str(sorulan) if sorulan and sorulan in TUM_SLOTLAR else None


def devam_edilebilir(onceki: dict | None) -> dict | None:
    """Bekleyen bir soru VE onun kısmi sorgusu var mı? → kısmi `CubeQuery`.

    🔴 `context.coz`'un `KURAL_DEVAM` dalının tetikleyicisi. İkisi birden gerekir:
    bir soru sorulmuş **olmalı** (`sorulan`) ve o soruyu sorarken ne anlaşıldığı
    **taşınmış olmalı** (`kismi_cq`). Yalnız biri varsa devam edilemez — ve bu
    dürüstçe `None`'dır, tahmin değil.
    """
    if not bekleyen_yanit_mi(onceki):
        return None
    kismi = (onceki or {}).get("kismi_cq")
    return kismi if isinstance(kismi, dict) and kismi else None


def onarim_hedefi(onceki: dict | None, yeni_cq: dict | None,
                  eski_cq: dict | None) -> str | None:
    """*"Yok ya mart demiştim"* — **hangi tek yuva** değişti?

    Döner: değişen yuva adı; birden çok yuva değiştiyse `None` (bu bir onarım değil,
    yeni bir sorudur).

    ⚠ Ölçüm burada **geriye doğru** yapılır çünkü onarımı *"anlamak"* bir dil işidir ve
    `followup.sinifla`'nın sahasıdır. Bu modül yalnız *"sonuç bir onarıma benziyor mu"*
    sorusunu yanıtlar — ikinci bir dil sınıflandırıcısı yazmaz (`ADR-0008`).
    """
    if not isinstance(yeni_cq, dict) or not isinstance(eski_cq, dict):
        return None
    degisen: list[str] = []
    if eski_cq.get("cube") != yeni_cq.get("cube"):
        degisen.append(SLOT_CUBE)
    if (eski_cq.get("measures") or []) != (yeni_cq.get("measures") or []):
        degisen.append(SLOT_OLCU)
    if _donem_imzasi(eski_cq) != _donem_imzasi(yeni_cq):
        degisen.append(SLOT_DONEM)
    return degisen[0] if len(degisen) == 1 else None


def _donem_imzasi(cq: dict) -> str:
    parca = [f"{f.get('dimension')}={f.get('value')}"
             for f in (cq.get("filters") or [])
             if isinstance(f, dict)
             and any(p in str(f.get("dimension", "")).lower() for p in _DONEM_ADLARI)]
    parca += [str(td.get("granularity")) for td in (cq.get("timeDimensions") or [])
              if isinstance(td, dict)]
    return "|".join(sorted(parca))


#: 🔴 `B9` — işaret sıfatları. **KAPALI bir dilbilgisi sınıfıdır** (ADR-0008 sözcük
#: listesi yasaklar, kapalı sınıfa izin verir): Türkçede üç tanedir ve yenisi eklenmez.
#: ⚠ `!` = **TAM KELİME** (deponun mevcut işareti). Bu bir titizlik değil bir
#: ZORUNLULUK: kapı, çekim ekiyle aranan tek harflik `o`'nun **`oee`** kelimesinin
#: içinde eşleştiğini yakaladı — yani *«bu hafta **oee**»* taze sorusu bir önceki
#: turun makinesine daraltılıyordu.
#:
#: ⊙ Dilbilgisi de tam olarak bunu söylüyor: işaret **sıfatı** çekimsizdir
#: (*o makine*, *bu ay*); ek aldığında sıfat olmaktan çıkıp **zamir** olur
#: (*onu*, *ona*) ve artık bir ismi işaret etmez. Yani tam-kelime araması bir
#: kısıtlama değil, sınıfın **doğru tarifidir**.
#: 🔴 **`bu` BİLEREK DIŞARIDA** — ve bu bir eksik değil, ölçülmüş bir karardır.
#:
#: `bu`, Türkçede baskın olarak bir **zaman ismine** bağlanır: *bu yıl · bu ay · bu
#: hafta · bu çeyrek · bu gün · bu dönem*. `_period_hit_words` bunların bir kısmını
#: tüketiyor (`bu yıl`, `bu ay`, `bu hafta`) ama hepsini değil — *«bu çeyrek ciro»*
#: canlıda `granülerlik=quarter` olarak çözülüyor ve `bu` **açıkta kalıyor**. Yani
#: `bu`'yu bir geri-atıf saymak, taze bir soruyu bir önceki turun varlığına sessizce
#: daraltırdı.
#:
#: ⚠ Bedeli asimetrik ve `§101.1` bunu tarif ediyor: kaçırılan bir *«bu makinede»*
#: yalnız bir çekilmedir (garson devralır); yanlış uygulanan bir daraltma ise
#: **doğru görünen yanlış cevaptır**. *İki hatadan biri sorulur, öteki inanılır.*
ISARET_SIFATLARI: tuple[str, ...] = ("o!", "su!", "soz konusu!", "ayni!")

#: 🔴 Kök-neden takibi: bir üstünlük cevabının ardından gelen *«neden …»* sorusu,
#: **o cevabın seçtiği varlık** hakkındadır. Bu da kapalı bir sınıftır (soru sözcüğü).
_KOK_NEDEN: tuple[str, ...] = ("neden", "nicin", "nedeni")

#: `!` işareti karşılaştırma için soyulur — dönem sözlüğü çıplak kelime tutar.
_CIPLAK = str.maketrans("", "", "!")


def _kova_basi(deger: Any) -> datetime | None:
    """Satırdan okunan zaman kovası etiketi → `datetime`. Çözemezse `None` (uydurmaz)."""
    if isinstance(deger, datetime):
        return deger
    try:
        return datetime.fromisoformat(str(deger).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _kova_sonu(bas: datetime | None, gran: str) -> datetime | None:
    """Kovanın **dışlayıcı** bitişi. ⚠ Bilinmeyen granülerlikte `None` — *bir aralığı
    tahmin etmek, onu hiç koymamaktan tehlikelidir.*"""
    if bas is None:
        return None
    if gran in ("day", "gun"):
        return bas + timedelta(days=1)
    if gran in ("week", "hafta"):
        return bas + timedelta(days=7)
    ay = {"month": 1, "ay": 1, "quarter": 3, "ceyrek": 3, "year": 12, "yil": 12}.get(gran)
    if ay is None:
        return None
    toplam = bas.month - 1 + ay
    return bas.replace(year=bas.year + toplam // 12, month=toplam % 12 + 1, day=1)


def odak_suzgeci(soru: str, cq: dict | None, onceki: dict | None,
                 sema: dict | None = None) -> dict | None:
    """🔴🔴 `B9` okuma tarafı — çözülmemiş bir atıf, odaktan **süzgeçe** dönüşür.

    Döner: eklenecek süzgeç (`{dimension, operator, value}`) ya da `None`.

    ## Dört şart — ve dördü de gerekli

    | # | şart | neden |
    |---|---|---|
    | 1 | durumda **odak** var | yoksa uydurulacak bir referans yok |
    | 2 | soruda **çözülmemiş atıf** var (*«o …»* / *«neden …»*) | her takip turu odağa daralmaz |
    | 3 | sorguda o boyutta **süzgeç YOK** | kullanıcı açıkça yazdıysa onunki kazanır |
    | 4 | küp o boyutu **taşıyor** | başka bir konuya geçilmişse odak geçersizdir |

    ⚠ 3 ve 4 birer **çekilme** şartıdır: koşul sağlanmıyorsa hiçbir şey yapılmaz.
    *Bir referansı çözememek, onu yanlış çözmekten iyidir* — ve bu modül yanlış
    çözmektense hiç dokunmamayı seçer.

    ## Neden bu bir «dil kuralı ekleme» DEĞİL

    En üst kural route'a Türkçe öğretmeyi yasaklar. Burada öğretilen bir dil değil,
    **bir belleğin okunmasıdır**: işaret sıfatları ve soru sözcükleri Türkçenin
    **kapalı** sınıflarıdır (üyeleri sayılıdır, büyümez) ve `ADR-0008` bunu açıkça
    ayırır. *Bir sözlüğü büyütmek bir kuraldan kaçmaktır; kapalı bir sınıfı adıyla
    anmak ise onu tanımaktır.*
    """
    odak = (onceki or {}).get("odak") if isinstance(onceki, dict) else None
    if not (isinstance(odak, dict) and odak.get("boyut") and odak.get("deger") is not None):
        return None
    if not isinstance(cq, dict):
        return None
    # ⚠ Yerel import: `cube_router` bu modülü dolaylı çeker; modül düzeyinde döngü olur.
    from app.cube_router import _herhangi, _norm, _period_hit_words

    qn = _norm(soru or "")
    # 🔴🔴 **`bu` HER ZAMAN BİR İŞARET SIFATI DEĞİLDİR.**
    #
    # İlk yazımda öyle sayıldı ve kendi denemem yanlış-pozitif verdi: *«**bu** yıl
    # toplam ciro»* — hiçbir atfı olmayan **taze** bir soru — odak süzgecini aldı ve
    # bir önceki turun ayına sessizce daraltılacaktı. Bu, deponun üç kez ısırıldığı
    # sınıfın aynısıdır (`göre`/`bazında` üç yönlü aşırı yüklü) ve `§101.1`'in tarifi:
    # *yanlış-pozitif bir yüklem, kapatmaya çalıştığı kusurdan pahalıdır.*
    #
    # ⊙ Ayrım için yeni bir liste YAZILMAZ — dönem ifadelerinin sahibi zaten var:
    # `_period_hit_words` bir dönem kalıbının **tükettiği** kelimeleri döndürür.
    # `bu` orada görünüyorsa o bir zaman ifadesidir, bir geri-atıf değil.
    #
    # *Bir kelimenin sınıfını, onu zaten tüketen kurala sormak; ikinci bir sözlük
    # yazmaktan hem ucuz hem de tek sahiplidir.*
    donem_kelimeleri = _period_hit_words(qn)
    isaret = [k for k in ISARET_SIFATLARI
              if k.translate(_CIPLAK) not in donem_kelimeleri]
    if not (_herhangi(qn, isaret) or _herhangi(qn, _KOK_NEDEN)):
        return None
    boyut = str(odak["boyut"])
    # 🔴 **AÇIK BİR PİN İLE BİR KAPSAM AYNI ŞEY DEĞİLDİR.**
    #
    # İlk yazımda o boyutta *herhangi* bir süzgeç varsa çekiliyordum. Canlı ölçüm
    # (thread B/5) bunun kusurunu gösterdi: sorguda zaten `tarih >= 2026-01-01`
    # (yılın kapsamı) vardı ve *«o ayda»* atfı **hiç uygulanmadı**. Oysa bir ay,
    # yılın **içindedir** — atıf o kapsamı çiğnemez, **daraltır**.
    #
    # Ayrım operatörde: `eq` kullanıcının koyduğu bir **pin**dir ve ona dokunulmaz;
    # `gte`/`lte`/`lt`/`gt` bir **kapsamdır** ve daraltılabilir.
    # *Bir kapsamı bir pin sanmak, hatırlamayı imkânsız kılar.*
    if any(str(f.get("dimension")) == boyut and str(f.get("operator")) == "eq"
           for f in (cq.get("filters") or []) if isinstance(f, dict)):
        return None
    kup = next((c for c in ((sema or {}).get("cubes") or [])
                if c.get("name") == cq.get("cube")), None)
    if kup is not None and boyut not in (kup.get("dimensions") or []) \
            and boyut not in (kup.get("time_dimensions") or []):
        return None
    gran = odak.get("granulerlik")
    if not gran:
        return [{"dimension": boyut, "operator": "eq", "value": odak["deger"]}]
    # 🔴 Zaman kovası → **YARI AÇIK ARALIK** `[başlangıç, bitiş)`. Kapalı üst sınır
    # (`lte`) ayın son gününün 00:00'ından sonraki kayıtları düşürürdü — bir gün
    # eksik bir ay, sessizce yanlış bir sayıdır.
    bas = _kova_basi(odak["deger"])
    son = _kova_sonu(bas, gran)
    if bas is None or son is None:
        return None
    return [{"dimension": boyut, "operator": "gte", "value": bas.isoformat()},
            {"dimension": boyut, "operator": "lt", "value": son.isoformat()}]


def odak_uygula(soru: str, cq: dict, onceki: dict | None, sema: dict | None,
                note: str | None, trace: list | None) -> tuple[dict, str | None, list]:
    """🔴 `B9` — odağı sorguya **uygular** ve uyguladığını **söyler**. Tek çağrı.

    ⊙ Bu fonksiyon `ask()` içindeydi ve büyüme kapısı onu geri çevirdi:
    *"yeni davranışı modüle çıkar, tavanı yükseltme — tavanı yükseltmek kapıyı kapının
    kendisiyle çürütür."* Kapı haklıydı: karar zaten burada (`odak_suzgeci`), yalnız
    **uygulaması** orada duruyordu. *Bir kararın ve onun uygulamasının ayrı evlerde
    oturması, iki sahip demektir.*

    ⚠ Süzgeç **listedir**: bir zaman kovası `[başlangıç, bitiş)` iki satırdır.
    🔴 Sessiz daraltma YASAK — *görünmeyen bir süzgeç, cevabı değil SORUYU değiştirir.*
    """
    # ⚠ En iyi çaba **burada**: sözleşme *"cevabı asla bozma"*dır ve o sözleşmenin
    # yeri, çağıranın gövdesi değil kuralın kendi evidir. (Çağıranda durursa her yeni
    # tüketici onu yeniden yazmak zorunda kalır — ve biri unutur.)
    try:
        suzgecler = odak_suzgeci(soru, cq, onceki, sema)
    except Exception:                                      # noqa: BLE001
        _log.warning("odak süzgeci çözülemedi (cevap etkilenmez)", exc_info=True)
        return cq, note, list(trace or [])
    if not suzgecler:
        return cq, note, list(trace or [])
    boyut = suzgecler[0]["dimension"]
    deger = ((onceki or {}).get("odak") or {}).get("deger", suzgecler[0]["value"])
    cq = {**cq, "filters": [*(cq.get("filters") or []), *suzgecler]}
    beyan = f"«{deger}» üzerinden yanıtlandı — bir önceki turun seçtiği {boyut}."
    return (cq, " ".join(x for x in [note, beyan] if x),
            [*(trace or []), f"odak: {boyut}={deger}"])
