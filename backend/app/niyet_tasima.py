"""🔴 **NİYET PARÇALARI NETLEŞTİRMEDEN SAĞ ÇIKMALI.**

## Sınıf — ve neden ayrı bir modül

Bu depoda **iki kez** aynı kusur ölçüldü:

| tur | soru | netleştirmeden sonra |
|---|---|---|
| `§34.2` | `ciromun en büyük **3** kaynağı…` → *"hangi dönem?"* → `bu yıl` | **sırasız** 8 satır |
| `§40` | `fire oranı **yüzde 5 üzerindeki**…` → *"hangi dönem?"* → `bu yıl` | tek sayı: **19.79** |

İkisinde de ayrıştırıcı **kusursuz** çalışıyordu; kaybolan şey netleştirme turuydu:
uyum kapısı **o turun** sorusuna bakar ve o tur *"bu yıl"*dır — içinde ne üstünlük vardır
ne eşik. Kullanıcının niyeti bir önceki cümlede kalır ve `cq` onu taşımaz.

🔴 **`§34` bu sınıfı bir örneğinde kapatmıştı ve sınıf kapanmadı.**

> *Bir sınıfı bir örneğinde kapatmak, sınıfı kapatmaz — yalnız bir sonraki örneğini
> daha şaşırtıcı yapar.*

## ⚠ KAYITLI BORÇ — bu modül ile `app/siralama.py` AYNI SINIFTIR

`siralama.tamamla` ile buradaki `esik` aynı şeyi yapar: *"soruda tanınan ama `cq`'ya
girememiş bir niyet parçasını yerleştir"*. Bugün ikisi ayrı duruyor çünkü `siralama`
`§34`'te tek başına doğdu ve o gün sınıf henüz görünmemişti.

**Kural:** **üçüncü** parça geldiğinde ikisi tek bir `parcalar` kaydında birleşir
(`(ad, tanı, yerleştir)` üçlüsü) ve çağıran tek bir döngü koşar. Üç kopyaya izin yoktur.

*Bir borcu görünür bırakmak onu ödemek değildir; ama gizlemek onu ikiye katlamaktır.*
"""

from __future__ import annotations


def _cr():
    from app import cube_router
    return cube_router


def esik(cq: dict, q: str) -> bool:
    """🔴 **`§40` — TANINAN EŞİK, NETLEŞTİRME TURUNDAN SAĞ ÇIKMALI.** Döner: değişti mi.

    ## Ölçülen sessiz yanlış

    `fire oranı yüzde 5 üzerindeki partileri listele` → *"hangi dönem için?"* → kullanıcı
    *"bu yıl"* dedi → cevap **tek bir sayı: 19.79**. Ne eşik uygulandı, ne liste geldi,
    **ne de bir şey beyan edildi**. Kullanıcı 19.79'u cevap sanabilir.

    ⊙ Ayrıştırıcı **kusursuz** çalışıyordu: `_measure_threshold("… yuzde 5 uzerindeki …")`
    → `{'op': '>', 'value': 5.0}`. Ve `Niyet` de onu **sayıyordu**. Kaybolduğu yer
    netleştirme turuydu: uyum kapısı **o turun** sorusuna bakar ve o tur *"bu yıl"*dır —
    içinde hiçbir eşik yoktur.

    🔴 Bu, `§34.2`'nin (üstünlük niyeti netleştirmede düşüyordu) **birebir aynı sınıfı**.
    O zaman `order` için çözülmüştü; sınıf o gün kapanmadı çünkü çözüm **tek parçaya**
    uygulandı. *Bir sınıfı bir örneğinde kapatmak, sınıfı kapatmaz.*

    ## Sınır

    ⚠ Zaten bir `measure_having` varsa dokunulmaz; ölçü yoksa hiçbir şey yapılmaz —
    eşik neyin eşiği olduğu bilinmeden uygulanamaz.
    """
    if not isinstance(cq, dict) or cq.get("measure_having"):
        return False
    olculer = [m for m in (cq.get("measures") or []) if m]
    if not olculer:
        return False
    esik = _cr()._measure_threshold(_cr()._norm(q or ""))
    if not esik:
        return False
    cq["measure_having"] = {"measure": olculer[0], **esik}
    return True


def route_supheli(cq: dict | None, q: str) -> bool:
    """🔴 **`§51` — ROUTE'UN YARIM BAŞARISI GARSONU ENGELLİYOR.**

    ## Ölçülen kusur — üç kanıt, tek desen

    | soru | route ne yaptı | kullanıcı ne gördü |
    |---|---|---|
    | `top 5 customers by profit this quarter` *(İngilizce)* | ölçü+boyut buldu, `top 5` ve `this quarter` **düştü** | *"hangi dönem için?"* |
    | `en çok duruş yaşayan hattı bul ve nedenini **açıkla**` | **uydurma** değer filtresi: `neden = "Açık"` | *"hangi dönem için?"* |
    | `bu yıl kar marjı … 3 müşteri` *(dönem yok)* | yarım `cq` | *"hangi dönem için?"* |

    ⊙ Üçünde de **garsona hiç sorulmadı**: `_try_fresh_intent`'in garson dalı
    `route_hit is None` ile bağlı — yani route **herhangi bir şey** bulduysa, o şey ne
    kadar eksik olursa olsun, LLM devreye girmiyor.

    🔴 Ve `§0.0`'ın kuralı bunun tersini söylüyor: *"aşçı **kesinlikle** duyduysa hemen
    yapar; **en ufak anlamama varsa garson gider**."* Route'un yarım duyması bir duyma
    değildir.

    ## Yüklem — şüphenin YAPISAL işaretleri

    `route()` bugün bir **derece** üretmiyor (`§AJ4.6`: marj hesaplanıp atılıyor), o yüzden
    şüphe `cq`'nun **eksikliğinden** okunur:

    * dönem yok (ne `filters`'ta tarih, ne `timeDimensions`) **ve** soruda bir dönem
      ifadesi var gibi duruyor → route dönemi **kaçırdı**
    * soruda üstünlük/sayı var ama `cq`'da `order`/`limit`/`entity_limit` yok
    * soruda kıyas var ama `cq` tek dönemli

    ⚠ **Fail-open:** şüphe yoksa `False` döner ve davranış **birebir bugünkü** kalır
    (`KURAL B`). Şüphe varsa çağıran garsona sorar ve **yalnız daha iyisini** alır.

    *Yarım duymak, duymamaktan daha tehlikelidir: duymadığını bilen sorar, yarım duyan
    emin olur.*
    """
    return bool(eksiklik(cq, q))


#: Şüphenin **adları**. Bir küme döndürmenin bir `bool` döndürmekten farkı: iki cevabı
#: **karşılaştırabilmek**. `§N2` bunu ölçtü — bkz. `eksiklik`.
EKSIK_DONEM = "donem"
EKSIK_SIRALAMA = "siralama"
EKSIK_TUMU = "yok"          # `cq` hiç yok → her şey eksik


def eksiklik(cq: dict | None, q: str) -> frozenset[str]:
    """🔴 **`§N2` — «YALNIZ DAHA İYİSİNİ AL» SÜZGECİ, ELDE HİÇBİR ŞEY YOKKEN DE ELİYORDU.**

    ## Ölçülen kusur — canlı log zinciri, tek istek

        route ŞÜPHELİ → garson çağrılıyor (§51)     ← route yarım duydu
        intent: 3 oy · 1 farklı aday · kazanan 2 oy ← garson OYBİRLİĞİYLE geçerli cevap
        CEVAP: not='Hangisini istiyorsun?'          ← ikisi de çöpe

    Soru: `bakım süresi en uzun makine`. **Soruda dönem YOK** — ne route ne garson tarih
    üretebilir. `route_supheli` dönemsizliği şüphe sayıyor, çağıran da garsonun cevabını
    *"hâlâ şüpheli"* diye eliyordu. Sonuç: hakem konuştu, kararı **duyulmadı**.

    ⊙ Ve bedeli yalnız sessizlik değil: aynı süzgeç, route'un **uydurduğu** filtreyi de
    hayatta bırakıyor. Ölçüldü — `en verimsiz hattı bul ve nedenini **açıkla**` →
    `filters:[{hat eq "Açık"}]`. Garsonun temiz cevabı elenince kullanıcıya giden şey
    uydurma filtreli rapor oluyor (`§51`'in kendi kanıt tablosundaki 2. satır, **hâlâ**).

    ## Kök — mutlak ölçüt, karşılaştırmalı sorunun yerine konmuş

    Süzgecin sorusu *"garsonun cevabı **daha iyi mi**"* olmalıydı; uygulaması *"garsonun
    cevabı **kusursuz mu**"* diye soruyordu. Route'un elinde hiçbir şey yokken bile aynı
    çıtayı tutuyordu — oysa **hiçbir şeyden kötü bir cevap yoktur**.

    ⚠ Bu yüzden yüklem `bool` değil **küme** döndürür: iki cevabı ancak adlandırılmış
    eksiklikler karşılaştırılabilir. `route_supheli` aynen korunur ve bu kümenin
    boşluğunu okur — **tek sahip** (`KAT-1`).

    ⚠ Ölçüt yine **dil-bağımsız**: hiçbir Türkçe sözcük aranmaz (`§51`'in kendi dersi).

    *Bir eleme ölçütü, elenenin yerine ne konacağını bilmiyorsa bir ölçüt değil bir
    kayıptır.*
    """
    if not isinstance(cq, dict):
        return frozenset({EKSIK_TUMU})
    cr = _cr()
    qn = cr._norm(q or "")
    eksik: set[str] = set()
    tarih_var = bool(cq.get("timeDimensions")) or any(
        f.get("operator") in ("gte", "lte") for f in (cq.get("filters") or []))
    # 🔴 **VE İLK YAZIMIM KENDİ KURALINI ÇİĞNEDİ.** Burada `\b(bu|gecen|son|ilk|…)\b`
    # diye bir **Türkçe** dönem sözcüğü aranıyordu — yani şüphe yüklemi, tam da yabancı
    # dilde çalışmayan bir şeye bağlıydı. Ölçüldü: `top 5 customers by profit this
    # quarter` → hiçbir Türkçe sözcük yok → şüphe **yok** sayıldı → garson yine
    # çağrılmadı. *Bir kuralın uygulaması, kuralın yasakladığı şeyi yapmamalıdır.*
    #
    # Dil-bağımsız işaret: **route dönemi hiç kuramadıysa şüphe vardır.** Kullanıcının
    # dönemden söz edip etmediğini anlamak garsonun işidir, bu yüklemin değil.
    # ⚠ Bedeli sınırlı: dönemsiz meşru sorularda garson da dönem üretmez, *"yalnız daha
    # iyisini al"* süzgeci route'un cevabını korur — maliyet bir LLM çağrısı, kazanç
    # kullanıcının cevapsız kalmaması.
    if not tarih_var:
        eksik.add(EKSIK_DONEM)
    if cr._direction(qn) and not (cq.get("order") or cq.get("entity_limit")):
        eksik.add(EKSIK_SIRALAMA)
    return frozenset(eksik)
