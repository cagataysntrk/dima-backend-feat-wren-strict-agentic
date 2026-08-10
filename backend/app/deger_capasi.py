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


def denetle(cq: dict, schema: dict | None) -> list[Bulgu]:
    """Süzgeç değerlerini kataloğun **tam** enum'una karşı doğrula.

    Boş liste = *"itiraz yok"*. Bu bir iyimserlik değil bir **kapsam beyanıdır**: enum'u
    olmayan boyutta yargı **verilmez**.
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
                                 oneri=None, gecerliler=list(gecerliler)))
            continue
        if op not in KIMLIK_OPERATORLERI:
            continue
        bilinen = {_norm(g) for g in gecerliler}
        ham = f.get("value")
        degerler = ham if isinstance(ham, (list, tuple)) else [ham]
        for d in degerler:
            if d is None or not str(d).strip():
                continue
            if _norm(str(d)) in bilinen:
                continue
            out.append(Bulgu(boyut=boyut, deger=str(d),
                             oneri=_yakin(str(d), gecerliler),
                             gecerliler=list(gecerliler)))
    return out


def duzelt_yerinde(cq: dict, bulgular: list[Bulgu]) -> str | None:
    """Önerisi olan bulguları `cq` üzerinde **yerinde** düzelt ve beyan metnini döndür.

    ⚠ Önerisi **olmayan** bulgulara dokunmaz — onlar çağıranın netleştirme kararıdır.
    ⚠ `cq` yerinde değişir çünkü bu deponun süzgeç düzeltme deseni odur
    (`donem_capasi.tasi_yerinde`); ikinci bir dönüş türü her çağıranı değiştirirdi.
    """
    esleme = {(b.boyut, _norm(b.deger)): b.oneri for b in bulgular if b.oneri}
    if not esleme:
        return None
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
    yok = [b for b in bulgular if not b.oneri]
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
        if b.oneri:
            continue
        for g in b.gecerliler[:EN_FAZLA_SECENEK]:
            out.append({"label": str(g), "query": str(g), "kind": "deger"})
    return out[:EN_FAZLA_SECENEK]


def huni_karari(cq: dict, schema: dict | None) -> tuple[str | None, dict | None]:
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
    bulgular = denetle(cq, schema)
    if not bulgular:
        return None, None
    duzeltme = duzelt_yerinde(cq, bulgular)
    if any(not b.oneri for b in bulgular):
        return duzeltme, {"note": netlestirme_metni(bulgular),
                          "secenekler": secenekler(bulgular)}
    return duzeltme, None
