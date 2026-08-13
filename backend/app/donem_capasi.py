"""🔴 KÖK-4 — **TAKİP TURUNDA DÖNEM ÇAPASI.** (denetim raporu KN-1)

## Ölçülen kusur — sondanın **en büyük tek kümesi**

| | |
|---|---|
| Toplam netleştirme | **43** |
| — *"Hangi dönem için?"* | **34** (%79) |
| — bunların ilk turda olanı | 8 → **doğru davranış** (ADR-0007-K3) |
| — 🔴 **takip turunda** olanı | **26** |
| Takipte, önceki turda dönem var mıydı | 🔴 **26/26 EVET** |

```
tur 1  bu yıl makine bazında oee        ✅ oee.ort_oee × makine
tur 2  en düşük hangisi                 ✅ aynı cube, dönem KORUNUYOR
tur 3  o makinenin duruşları ne kadar   🔵 «Hangi dönem için?»
tur 4  peki fire tarafı nasıl           🔵 «Hangi dönem için?»
```

Fark: 2. tur **aynı ölçüyü** sıralıyor; 3. tur **yeni bir ölçü** istiyor. Yani dönem,
**ölçü değişince** düşüyor.

## Kod yolu — raporun bulduğu tek satır

`cube_router.py:1112-1113`:

```python
if em and em not in prev.get("measures", []) and swap is None and topn is None:
    return None  # farklı metrik açıkça isteniyor → yeni sorgu, LLM sınıflandırsın
```

`deterministic_refine` **`None`** dönünce soru **taze soru** sayılıyor; `route()` çıplak
takip metnini görüyor (`o makinenin duruşları ne kadar`) → dönem yok → **netleştirme**.

⚠ Ve kanıtı kesinleştiren ayrıntı: dönemi taşıyacak mekanizma **iki satır aşağıda zaten
var** (`cq = copy.deepcopy(prev)`); ölçü-değişimi dalı ona **hiç ulaşmıyor**.
🔴 *Bilgi var, temsil yok — en saf hâli.*

## 🔴 Neden `return None` KALDIRILMIYOR

Raporun kendi anti-çözüm listesi (**A4**): *"o dal **bilinçli** — farklı metrik
gerçekten yeni bir sorudur. Kaldırmak **ölçü karışması** üretir."*

> Doğru olan **dönemi soruya değil, OTURUMA bağlamaktır**: ölçü değişse de dönem
> çapası yaşasın.

Bu modül tam olarak onu yapar ve **başka hiçbir şeye dokunmaz**: cube değişebilir,
ölçü değişebilir, kırılım değişebilir — **yalnız dönem** taşınır.

## Üç şart — üçü birden

Çapa YALNIZ şu üç şart aynı anda sağlanınca taşınır:

1. Yeni sorgu **hiç dönem filtresi taşımıyor** → kullanıcı bu turda dönem söylemedi.
2. Önceki sorgu **dönem filtresi taşıyor** → oturumda bir dönem *kurulmuş*.
3. Soru **"tüm zamanlar" demiyor** → filtre yokluğu **kasıtlı değil**.

⚠ Üçüncüsü olmadan `tüm zamanlar` isteği sessizce eski döneme geri dönerdi — yani
kullanıcının **açık** talimatı, hatırlanan bir bağlam tarafından ezilirdi. *Bir bağlam,
kendisini ezmek için verilmiş bir talimatı ezemez.*
"""

from __future__ import annotations

import re

from app.logging_setup import get_logger

_log = get_logger("donem_capasi")

#: Dönem filtresi sayılan operatörler. ⚠ `eq` DEĞİL: `tarih = '2026-01-01'` bir dönem
#: değil bir nokta seçimidir ve taşınması yanlış olurdu.
_DONEM_OP = ("gte", "lte", "gt", "lt", ">=", "<=", ">", "<")


def _donem_filtreleri(cq: dict | None) -> list[dict]:
    """Bir `cube_query`'nin dönem filtreleri — **değere** bakarak, ada değil.

    ⚠ Zaman boyutunun adı cube'a göre değişir (`tarih` · `donem_tarih` ·
    `acilis_tarihi`); bir ada göre aramak yeni her cube'da sessizce boş döner.
    """
    out = []
    for f in ((cq or {}).get("filters") or []):
        v = f.get("value")
        if (str(f.get("operator")) in _DONEM_OP and isinstance(v, str)
                and len(v) >= 10 and v[:4].isdigit() and v[4] == "-"):
            out.append(f)
    return out


def tasi(yeni_cq: dict | None, onceki_cq: dict | None, soru: str,
         *, cube_meta: dict | None = None) -> tuple[dict | None, bool]:
    """Dönem çapasını taze sorguya taşı — `(cq, tasindi_mi)`.

    🔴 **Yalnız dönem taşınır.** Cube, ölçü, kırılım ve öteki filtreler **hiç
    dokunulmadan** kalır: bu modülün tek işi, ölçü değişiminde düşen tek şeyi
    yerine koymaktır.

    ⚠ Zaman boyutunun ADI cube'lar arasında farklı olabilir. Cube değiştiyse ve yeni
    cube'un zaman boyutu farklı adlanıyorsa filtre **yeniden adlandırılır** — yoksa
    var olmayan bir kolona filtre yazılır ve sorgu **çalışma anında** patlar.
    """
    from app.cube_router import _norm as _r_norm
    from app.cube_router import is_all_time

    if not yeni_cq or not onceki_cq:
        return yeni_cq, False
    if _donem_filtreleri(yeni_cq):
        return yeni_cq, False                    # kullanıcı bu turda dönem verdi
    onceki = _donem_filtreleri(onceki_cq)
    if not onceki:
        return yeni_cq, False                    # oturumda kurulmuş bir dönem yok
    # ⚠ `is_all_time` NORMALİZE metin bekler (`tüm` → `tum`). Ham metinle çağırınca
    # sessizce `False` döndü ve *"tüm zamanlar"* isteği eski döneme geri sarıldı —
    # yani kullanıcının AÇIK talimatı hatırlanan bir bağlamla ezildi.
    # *Bir yardımcıyı sözleşmesini okumadan çağırmak, onu çağırmamakla aynıdır.*
    if is_all_time(_r_norm(soru or "")):
        # 🔴 Açık talimat, hatırlanan bağlamı EZER — tersi değil.
        return yeni_cq, False

    hedef_zaman = _zaman_boyutu(yeni_cq, cube_meta)
    tasinan = []
    for f in onceki:
        g = dict(f)
        if hedef_zaman:
            g["dimension"] = hedef_zaman
        tasinan.append(g)

    cq = dict(yeni_cq)
    cq["filters"] = [*(cq.get("filters") or []), *tasinan]
    _log.info("KÖK-4 dönem çapası taşındı: %s → %s (%d filtre)",
              onceki_cq.get("cube"), cq.get("cube"), len(tasinan))
    return cq, True


def _zaman_boyutu(cq: dict, cube_meta: dict | None) -> str | None:
    """Hedef cube'un zaman boyutu adı — yoksa `None` (filtre adı korunur)."""
    tds = (cube_meta or {}).get("time_dimensions") or []
    if tds:
        return str(tds[0])
    # Cube meta yoksa mevcut filtrelerden çıkarım yapma; ad değiştirmeden bırak.
    return None


#: Kullanıcıya gösterilen iz — **sessiz bir taşıma, sessiz bir varsayımdır**.
IZ = "dönem çapası önceki turdan taşındı (KÖK-4)"

#: Cevabın notuna eklenen açıklama. ⚠ Taşıma **görünür** olmalı: kullanıcı hangi dönemin
#: geçerli olduğunu tahmin etmek zorunda kalmamalı.
def not_metni(filtreler: list[dict]) -> str:
    ilk = next((f["value"][:10] for f in filtreler
                if str(f.get("operator")) in ("gte", ">=", ">")), None)
    son = next((f["value"][:10] for f in filtreler
                if str(f.get("operator")) in ("lte", "<=", "<")), None)
    if ilk and son:
        aralik = f"{_gun(ilk)} – {_gun(son)}"
    elif ilk:
        aralik = f"{_gun(ilk)} sonrası"
    else:
        return ""
    return f"⏱ Önceki turun dönemi korundu ({aralik}). Değiştirmek için dönemi yaz."


def _gun(iso: str) -> str:
    y, a, g = iso[:4], iso[5:7], iso[8:10]
    return f"{g}.{a}.{y}"


#: Notun `cube_query` üstünde taşındığı geçici anahtar. ⚠ **Taşıyıcıdır**: vardığı yerde
#: `notu_al` tarafından SİLİNİR. Sızarsa `cube_query` cevaba kirli gider ve daha kötüsü
#: SQL derleyicisine bilinmeyen bir alan olarak ulaşır.
_TASIYICI = "_capa_notu"


def tasi_yerinde(cq: dict, onceki_cq: dict | None, soru: str,
                 cube_meta: dict | None = None) -> bool:
    """`cq`yi **yerinde** çapalar; taşındıysa `True`.

    🔴 Neden yerinde: çağıran `_period_gate`in sözleşmesi *"`None` = devam et"*tir.
    Yeni bir dönüş türü eklemek DÖRT çağıranı birden değiştirirdi. Ve router'da kalan
    kod **iki satıra** iner — *taşınabilir olan her şey modüle gider* kuralının somut
    hâli (büyüme kapısı bunu iki kez ölçerek dayattı).
    """
    yeni, tasindi = tasi(cq, onceki_cq, soru, cube_meta=cube_meta)
    if not tasindi:
        return False
    cq["filters"] = yeni.get("filters") or []
    cq[_TASIYICI] = (not_metni(cq["filters"]), IZ)
    return True


IZ_VARSAYILAN = "dönem belirtilmedi → verinin son 12 ayı BEYANLA varsayıldı (M-4)"

#: `M-4` — varsayılan pencerenin uzunluğu. Bir **ürün kararıdır** ve bu yüzden tek bir
#: yerde, adıyla durur: on iki ay, mevsimsellik taşıyan her iş sorusunun en küçük
#: dürüst penceresidir (bir yıllık döngü tam kapanır).
VARSAYILAN_AY = 12


#: Yıl **işareti** taşımayan dört haneli sayı. ⚠ `cube_router._YEAR_RE`'nin **zıddı**:
#: o *"yıl işareti VAR mı"* diye sorar ve bir dönem üretir; bu yalnız *"ortada anılmamış
#: bir dört hane var mı"* diye sorar ve **hiçbir dönem üretmez**.
_CIPLAK_YIL_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def _yok_sayilan_yil(soru: str) -> str | None:
    """Beyanın **anacağı** yok sayılan dört haneli sayı — yalnız varsayım dalında.

    🔴 `§34` — **EKSİK BİR DOĞRU.** *"Dönemi çözemedim"* doğruydu ama **yarımdı**:
    kullanıcı `2019 cirosu` yazdı, sistem `2019`'u **düşürdü** ve cevabı verinin son 12
    ayından kurdu — bunu **söylemeden**. Beyanın işi varsayımı görünür kılmaksa,
    **neyi yok saydığını** da söylemelidir; yoksa kullanıcı yanlış dönemi doğru sanır.

    ⚠ `㊸`'nin sınırı **korunmaz değil, KORUNUR**: çıplak yıl hâlâ bir dönem **değildir**
    (ERP'de bir hesap/şube/TRCODE değeri olabilir — `test_B_CIPLAK_YIL_BILEREK_KAPSAM_DISI`).
    Burada yalnız **anılır**; hiçbir filtre üretmez.

    ⚠ Yalnız `varsayilan_yerinde` içinden çağrılır — oraya gelinmişse dönem **zaten
    çözülememiştir**, yani ikinci bir sınır denetimi ㊲ gerekmez. Ve iddiası ölçülebilir:
    *"soruda geçen şu dört hane"* — sistemin **bilebileceği** bir şey. Bu, bir üstteki
    docstring'in dersinin (*"beyan ölçebildiğinden fazlasını söylemesin"*) ihlali değil,
    **uygulanışıdır**: ölçebildiğini artık söylüyor.
    """
    if not soru:
        return None
    m = _CIPLAK_YIL_RE.search(soru)
    return m.group(0) if m else None


def _yok_sayilan_ek(soru: str) -> str:
    """Yok sayılan dört hane varsa beyana eklenen **tek cümle**; yoksa **boş dize**.

    Cümle iki iş yapar: (1) düşürüleni **adıyla** anar, (2) düzeltmeyi **öğretir**
    (*«2019 yılı»*) — *bir sınırı söylemek, onu aşmanın yolunu göstermekle tamamlanır.*
    """
    yil = _yok_sayilan_yil(soru)
    if not yil:
        return ""
    return (f" ⚠ «{yil}» bir yıl **işareti** taşımadığı için dönem sayılmadı "
            f"(bir hesap/şube kodu da olabilir) — **«{yil} yılı»** dersen onu uygularım.")


def varsayilan_yerinde(cq: dict, service, cube_meta: dict | None,
                       *, soru: str = "") -> bool:
    """🔴🔴 **`M-4` — SORMAK VARSAYILAN DAVRANIŞTI; ARTIK BEYANLI VARSAYIM DA VAR.**

    ## Ölçülen kusur

    Korpusun **%13,7'si** `CLARIFY:dönem`. P/R turlarında **on** senaryoda görüldü ve
    hepsinde aynı desen: ölçü **çözülmüş**, kırılım **çözülmüş**, sıralama **çözülmüş** —
    tek eksik dönem, ve sistem cevabı **tutup soruyor**:

        toplam duruş dakikasını hat bazında sırala → «toplam sure dk çıkarabilirim —
                                                      hangi dönem için?»

    Politika (`ADR-0007`) savunulabilir; raporun tespiti şuydu: **bedeli ölçülmedi.**

    ## 🔴 Raporun formu ÜÇÜNCÜ KEZ düzeltildi — ve sebebi yine yapısal

    Rapor küp düzeyinde `varsayilan_donem:` beyanı öneriyordu. `M-2` (`rol`) ve `M-9`
    (`pencere`) ile **aynı duvar**: MDL'de küp alanları da sabittir
    (`name·label·baseObject·synonyms·defaultMeasure·measures·dimensions·timeDimensions`);
    yeni bir anahtar ya derlemede düşer ya motorun `serde`'si projeyi reddeder.

    ⊙ Ama raporun **kendi cümlesi** çıkışı gösteriyordu: *"`veri_araligi` verinin gerçek
    aralığını **zaten biliyor**."* Varsayılanın kataloğa yazılmasına gerek yok — **veriden
    türetilir**. Bu, katalog beyanından **daha iyi**dir: bayat bir beyan yanlış bir
    pencere üretir, veri kendini günceller.

    ## Sözleşme

    * **Bayraklı** (`varsayilan_donem`, varsayılan **kapalı**) → `KURAL B`: bayrak
      kapalıyken davranış **birebir** bugünküdür.
    * **Beyanlı**: pencere `_TASIYICI` ile cevaba yazılır — *sessiz varsayım yasak,
      beyanlı varsayım deponun kendi deseni* (`ADR-0027`'nin ihlali değil, uygulaması).
    * **Veriden**: aralık `veri_araligi.aralik` ile ölçülür; **ölçülemezse hiçbir şey
      yapılmaz** ve kapı bugünkü gibi sorar (fail-closed).
    * Netleştirme **kalkmaz**; ikinci seçenek olur.

    *Bir varsayımı yapmak değil, yaptığını söylememek yasaktır.*
    """
    if not isinstance(cq, dict) or cq.get("filters") and _donem_filtreleri(cq):
        return False
    zaman = _zaman_boyutu(cq, cube_meta)
    if not zaman or service is None or not cube_meta:
        return False
    try:
        from app import veri_araligi as _va
        sinir = _va.aralik(service, cube_meta)
    except Exception:                                   # noqa: BLE001 — tur düşmez
        sinir = None
    if not sinir:
        return False                                    # ⚠ ölçemediysek varsayma
    _min, _max = sinir[0][:10], sinir[1][:10]
    try:
        from datetime import date as _d
        y, a, g = (int(x) for x in (_max[:4], _max[5:7], _max[8:10]))
        _ay = a - VARSAYILAN_AY
        _bas = _d(y + (_ay - 1) // 12, (_ay - 1) % 12 + 1, 1).isoformat()
    except Exception:                                   # noqa: BLE001
        return False
    bas = max(_bas, _min)
    cq["filters"] = [*(cq.get("filters") or []),
                     {"dimension": zaman, "operator": "gte", "value": bas},
                     {"dimension": zaman, "operator": "lte", "value": _max}]
    cq[_TASIYICI] = (
        # 🔴🔴 `§BD` — **BEYAN, KULLANICI HAKKINDA DEĞİL KENDİ YAPTIĞI HAKKINDA KONUŞUR.**
        #
        # ⊙ Canlı ölçüm (çok-dilli curl turu, 2026-08-10):
        #
        #     «لهذا العام إجمالي الإيرادات»  (= «bu yıl toplam ciro»)
        #       → 137.588.350 (son 12 ay)   · doğrusu 74.022.836 (bu yıl)
        #       → not: «⏱ Dönem BELİRTMEDİN …»
        #
        # 🔴 Kullanıcı dönemi **belirtti** — başka bir dilde. Garson ölçüyü çevirdi
        # (`إجمالي الإيرادات → toplam_ciro`) ama dönemi çeviremedi (istem `هذا العام`
        # örneğini taşıyor, kullanıcı ön ekli `لهذا العام` yazdı). Sonuç yalnız yanlış
        # bir sayı değil, **yanlış bir BEYAN**: sistem kullanıcıya *«sen söylemedin»*
        # dedi, oysa söylemişti.
        #
        # ⊙ Kök çözüm bir çeviri yaması değil — o modelin oynaklığıdır ve istem zaten
        # doğru talimatı taşıyor. Kök, **beyanın kendisinin fazla iddialı olmasıdır**:
        # sistem kullanıcının ne söylediğini **bilmez**, yalnız kendi **çözemediğini**
        # bilir. Yeni metin yalnız ikincisini söyler ve **her dilde doğrudur**.
        #
        # ⚠ Kullanıcıya sunulan seçenek aynen duruyor: *«başka bir dönem yazarsan onu
        # uygularım»* — sınır daralmadı, yalnız iddia dürüstleşti.
        #
        # *Bir beyan, ölçebildiğinden fazlasını söylediği anda bir varsayıma dönüşür —
        # ve beyanın işi tam olarak varsayımı görünür kılmaktı.*
        (f"⏱ Dönemi çözemedim — **verinin son {VARSAYILAN_AY} ayı** alındı "
         f"({_gun(bas)} – {_gun(_max)}). Başka bir dönem yazarsan onu uygularım."
         + _yok_sayilan_ek(soru)),
        IZ_VARSAYILAN)
    return True


#: 🔴🔴 `§TZ` — **BEYANIN YANINDA BİR TIK OLMALI.**
#:
#: ## Ölçülen kusur (curl `N+1` turu, 2026-08-10)
#:
#:     «makine bazında ortalama oee»
#:       note: ⏱ Dönemi çözemedim — verinin son 12 ayı alındı … **başka bir dönem
#:             YAZARSAN** onu uygularım
#:       suggestions: **[]**
#:
#: `D3` (`varsayilan_donem` → `beta`) doğru bir karardı ve ölçülmüştü: sormak yerine
#: **beyanla varsaymak** kullanıcıyı cevapsız bırakmıyor. Ama kararın **yan etkisi**
#: ölçülmemişti: netleştirme dalı ölünce onun **chip'leri de** öldü. Yani düzeltme
#: yolu bir **tıktan** bir **yazma** eylemine düştü.
#:
#: ⊙ Ve bu, beş bayat kapının aslında neyi koruduğunu gösteriyor: `test_ask_golden`
#: *«Tümü chip'i olmalı»* diyordu ve **haklıydı** — yanlış olan tek şey, o chip'in
#: bir **netleştirme** turunda gelmesi gerektiği varsayımıydı. Yetenek doğruydu, akış
#: değil. *Bayat bir kapı bazen yanlış cevabı değil, doğru cevabın eski adresini tutar.*
#:
#: ⚠ Liste **yeniden yazılmadı**: `ask.py`'nin netleştirme dalında zaten duran aynı
#: seçenekler buraya taşındı ve iki çağıran da buradan okuyor (`KAT-1`). Böylece
#: *«hangi dönemleri tek tıkla seçebilirim»* sorusunun **tek** cevabı var.
DONEM_SECENEKLERI: tuple[dict[str, str], ...] = (
    {"label": "Bugün", "query": "bugün"},
    {"label": "Bu hafta", "query": "bu hafta"},
    {"label": "Bu ay", "query": "bu ay"},
    {"label": "Bu yıl", "query": "bu yıl"},
    {"label": "Tümü", "query": "tüm zamanlar"},
)


def notu_al(cq: dict, note: str | None,
            trace: list[str]) -> tuple[str | None, list[str], list[dict[str, str]]]:
    """Taşıyıcıyı **boşalt** ve notu/izi/seçenekleri cevaba kat. *Bir taşıyıcı alan,
    taşıdığı yere varınca boşaltılmalıdır.*

    Üçüncü dönüş (`§TZ`): beyanlı bir varsayım yapıldıysa **düzeltme chip'leri**. Boş
    liste = *"düzeltilecek bir varsayım yok"*.
    """
    tasinan = cq.pop(_TASIYICI, None) if isinstance(cq, dict) else None
    if not tasinan:
        return note, trace, []
    # 🔴 İZ ARTIK TAŞIYICIDAN GELİR — canlıda ölçüldü: `M-4`'ün beyanlı varsayımı
    # cevaba **doğru** notu yazıyordu ama ize *"önceki turdan taşındı (KÖK-4)"* diye
    # **yanlış gerekçe** basıyordu, çünkü `IZ` bu satıra sabit gömülüydü. İki farklı
    # sebep aynı kanalı paylaşınca, kanalın kendisi sebebi de taşımalıdır.
    # *Doğru bir notun yanında yanlış bir iz, notu da şüpheli yapar.*
    metin, iz = tasinan if isinstance(tasinan, tuple) else (tasinan, IZ)
    if not metin:
        return note, trace, []
    # ⚠ Chip yalnız **varsayım** izinde: taşıyıcının öteki kullanıcısı (`KÖK-4`, önceki
    # turdan taşınan dönem) bir varsayım değil bir **süreklilik**tir — orada düzeltme
    # önerisi, kullanıcının kendi seçtiği dönemi geri almasını önerirdi.
    secenekler = [dict(x) for x in DONEM_SECENEKLERI] if iz == IZ_VARSAYILAN else []
    return " ".join(x for x in [note, metin] if x), [*trace, iz], secenekler

#: `§68` — `YYYY-AA-GG` **şekli**.
_ISO_GUN_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def tarih_sinirimi(deger: object) -> bool:
    """Bir süzgeç değeri bir **dönem sınırı** mı (şekline göre) ⑤.

    🔴 **Buranın sahibi olması bir yerleşim tercihi değil bir kapı kararı** ㊸:
    `test_YENI_DILBILIM_YAZILMADI` `niyet.py`'de bir `re.compile` gördüğü an kırmızı
    verir ve **haklıdır** — o nesne bir **çatıdır**, bir kalıp sahibi değil. Dönemle
    ilgili her okuma bu modülde toplanır (`_CIPLAK_YIL_RE`'nin komşusu).

    ⚠ Bu bir **son çare**dir: birincil ölçüt küpün `time_dimensions` kaydıdır. Şekil
    ölçüsü yalnız meta yokken konuşur — ve bir tahmin değildir: bir hesap kodu `2019`
    olabilir, ama `2019-07-01` bir tarihtir.
    """
    return bool(_ISO_GUN_RE.match(str(deger or "")))

#: 🔴 `§74` — **YAZIYLA YAZILMIŞ SAYI: kapalı, sonlu, tek sahipli** ㊱.
#:
#: ⊙ Canlı ölçüldü (`s35`): `«son 3 ayda fire»` → `source=cube`, dönem doğru;
#: `«son üç ayda fire»` → route **düştü** (`source=cube+llm`) ve garson dönemi
#: **13 aya** açtı (`2025-06-01 → 2026-06-30`). İki zarar: gereksiz bir LLM turu **ve**
#: kullanıcının doğru sandığı **yanlış bir sayı**.
#:
#: ⚠ Bu bir *«route'a dil kuralı eklemek»* **değildir**: `_REL_DATE` zaten bir Türkçe
#: birim listesi taşıyor (`ay|gun|hafta|yil`). Sayı sözcükleri de aynı cinsten — **kapalı
#: ve sonlu** bir küme. Açık uçlu bir sözcük listesi yazılsaydı doktrin ihlali olurdu.
#:
#: ⚠ Anahtarlar **normalize** biçimdedir (`_norm`: `üç → uc`), çünkü eşleşme normalize
#: metinde olur. `on bir`/`on iki` **iki sözcüktür** ve kalıpta **önce** denenmeli.
#: ⊘ `yarım` yok: *«son yarım ay»* bir dönem değil bir yuvarlamadır.
SAYI_SOZCUKLERI: dict[str, int] = {
    "bir": 1, "iki": 2, "uc": 3, "dort": 4, "bes": 5, "alti": 6,
    "yedi": 7, "sekiz": 8, "dokuz": 9, "on": 10, "on bir": 11, "on iki": 12,
}

#: Regex alternasyonu — **uzun olan önce** (`on iki` `on`dan önce denenmeli, yoksa
#: `«son on iki ay»` → `on` + artık `iki ay` kalır ve kalıp tutmaz).
SAYI_KALIBI: str = "|".join(
    sorted((k.replace(" ", r"\s+") for k in SAYI_SOZCUKLERI), key=len, reverse=True))


def sayi_coz(soz: str | None) -> int | None:
    """`«uc»` → `3`. Rakamsa `int`, sözcükse tablodan; ikisi de değilse `None`.

    ⚠ **Tek okuma noktası** ㊲: hem `_REL_DATE` hem gelecekteki her dönem kalıbı buradan
    okur — iki yerde çözülen bir sayı, bir gün iki farklı tarihe dönüşür.
    """
    if not soz:
        return None
    t = " ".join(str(soz).split())
    if t.isdigit():
        return int(t)
    return SAYI_SOZCUKLERI.get(t)

