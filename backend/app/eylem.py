"""EYLEM ÖNERİSİ — ajanın yazma yolunun **onay kademesi** (FAZ H).

## Ölçülen kusur (3 Ağustos 2026)

`app/tools.py` yazma araçlarını bilerek kayda ALMADI (*"Ajan YAZAMAZ"*). Bu doğru bir
karardı ama **yarım** kaldı: kullanıcı yazma isteğini yine de söylüyor ve sistemde
*"eylem ifadesi"* diye bir sınıf olmadığı için istek bir **veri sorusu** sanılıyordu:

    "her pazartesi bu raporu bana yolla"  → source=rule, **SQL ÜRETTİ**, 1 satır
    "bu raporu her sabah 8'de e-postala"  → source=rule, **SQL ÜRETTİ**, 1 satır
    "bunu panoya ekle"                    → *"«bunu» yerine «gunu» mi demek istedin?"*
    "şunu panoya kaydet"                  → *"«kaydet» yerine «adet» mi demek istedin?"*

Yani ajan yazmıyordu ama **uyduruyordu** — sorulmayan bir soruya cevap üretiyordu. Kök
neden D1 (sosyal) ve D2 (*"analiz et"*) ile **aynı ailedendir**: veri sorusu olmayan bir
ifade sınıfının tanımsız olması. Bu modül o sınıfı tanımlar.

## Yasak kaldırılmaz, KADEMELENDİRİLİR

Merdiven değişmiyor: **ajan hâlâ yazamaz**. Değişen şey, isteğin artık bir **öneriye**
dönüşmesi:

    kullanıcı söyler → sistem DETERMİNİSTİK olarak öneriyi kurar → kullanıcı ONAYLAR
                     → onay ucu yetkiyi YENİDEN doğrular → var olan uç çalışır

## Üç değişmez

1. **Argümanlar LLM'den GELMEZ.** Önerinin `cube_query`'si, konuşmada **zaten
   doğrulanmış** olan sorgudur. Bir LLM'in uydurduğu `cube_query` bir zamanlamaya
   yazılsaydı, o uydurma **her hafta** tekrar koşardı — bu deponun kovaladığı
   *"sessiz yanlış"*ın kalıcılaştırılmış hâli olurdu.
2. **Öneri yeni YETKİ yaratmaz.** Onay ucu, kullanıcının kendi eliyle çağırabileceği
   ucun **ta kendisini** çağırır; aynı `authorize()` aksiyonu, aynı doğrulama, aynı
   audit. Öneriye güvenilmez — çünkü ona güvenmeye **gerek yoktur**.
3. **Çapa yoksa öneri de yok.** Ortada bir rapor yokken *"panoya ekle"* çalıştırılamaz;
   o durumda sistem **dürüstçe sınırını söyler** — uydurmaz (Faz D4'ün proaktif sınır
   beyanı).

## Sözlük disiplini

`followup.py`'nin beş türü ve `cube_router`'ın sosyal sözlüğüyle **aynı**: kapalı,
belgeli kalıp demetleri + `_syn_hit` kelime sınırı. Alt-dize eşleşmesi YOK (bu depoda
`ay ⊂ detay`, `yas ⊂ kıyasla` sahte eşleşmeleri ölçüldü).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.cube_router import _syn_hit

# --- EYLEM ADLARI (tek kaynak; ask.py ve routers/eylem.py bunları kullanır) ---------

PANO_EKLE = "pano.ekle"
ZAMANLA = "zamanla.olustur"
#: FAZ E — kalıcı sunum tercihi. Yazma olduğu için ONAY kademesinden geçer: bir faz
#: önce *"onaysız hiçbir yazma"* deyip burada muafiyet açmak, bu deponun tekrar tekrar
#: ölçtüğü kusur sınıfı olurdu (**beyan var, kod onu tanımıyor**). Tespiti `app/tercih.py`
#: yapar; burası yalnız BEYANI tutar — kayıt ile tespit ayrı sahiplerdir.
TERCIH_KAYDET = "tercih.kaydet"


@dataclass(frozen=True)
class EylemBeyani:
    """Bir yazma eyleminin beyanı — `tools.Arac` ile aynı felsefe: gövde YOK.

    `uc` alanı bir *işaretçidir*: onay ucu bu adı kullanarak **var olan** handler'ı
    çağırır. Buraya bir gövde kopyalansaydı, doğrulama kuralları ikinci kez yazılmış
    olurdu — bu deponun ölçülmüş bir numaralı kusur sınıfı (`tools.py` girişi).
    """

    ad: str
    ozet_kalibi: str          # insan-okur özet; `{rapor}` ve `{ne_zaman}` doldurulur
    izin: str                 # authorize() aksiyonu — matriste VAR OLMALI (test kilitler)
    geri_alinabilir: bool     # False → senkron onay ŞART (plan: "geri alınamaz iş")
    uc: str                   # onay ucunun çağıracağı var olan handler'ın adı


EYLEM_KAYIT: tuple[EylemBeyani, ...] = (
    EylemBeyani(
        ad=PANO_EKLE,
        ozet_kalibi="“{rapor}” raporunu panona ekleyeyim mi?",
        # Pano widget'ı PER-USER'dır ve kullanıcının kendi sorabildiği bir raporu
        # kaydeder — yetki eşiği sorgunun kendisiyle aynı (`query:run`). Yeni bir veri
        # yüzeyi açmaz; yalnız var olan cevabı sabitler.
        izin="query:run",
        geri_alinabilir=True,     # widget silinebilir (soft-delete, ADR-0019)
        uc="dashboards.add_widget",
    ),
    EylemBeyani(
        ad=ZAMANLA,
        ozet_kalibi="“{rapor}” raporunu {ne_zaman} göndereyim mi?",
        izin="schedule:create",
        # Zamanlama bir kez kurulunca KENDİ BAŞINA koşar ve dışarıya (e-posta) çıkar;
        # kaydı silmek geçmişte gönderilmiş bildirimi geri almaz.
        geri_alinabilir=False,
        uc="schedules.create_schedule",
    ),
    EylemBeyani(
        ad=TERCIH_KAYDET,
        # Özet `app/tercih.py::ozet` tarafından üretilir (hedef etiketi oradan gelir);
        # kalıp yine de burada durur ki KAYIT tek başına okunabilir olsun.
        ozet_kalibi="Bundan sonra raporları {rapor} göstereyim mi?",
        # Sunum tercihi yeni bir veri yüzeyi açmaz — yalnız kullanıcının KENDİ
        # raporlarının görünümünü değiştirir; eşik sorgunun kendisiyle aynı.
        izin="query:run",
        geri_alinabilir=True,       # tek uçla silinir (DELETE /tercihler/{anahtar})
        uc="tercihler.tercih_yaz",
    ),
)

_BEYANLAR: dict[str, EylemBeyani] = {e.ad: e for e in EYLEM_KAYIT}


def beyan(ad: str) -> EylemBeyani:
    """Adıyla eylem beyanı. Bilinmeyen ad = hata (fail-closed): onay ucu, kayıtta
    OLMAYAN bir eylemi çalıştıramaz — istemci eylem UYDURAMAZ."""
    try:
        return _BEYANLAR[ad]
    except KeyError:
        raise KeyError(
            f"Kayıtlı olmayan eylem: {ad!r}. Kayıtta olmayan bir yazma AÇIK DEĞİLDİR "
            f"(bkz. app/eylem.py). Mevcut: {sorted(_BEYANLAR)}") from None


# --- SÖZLÜK (kapalı, belgeli — liste büyütmek ÇÖZÜM DEĞİLDİR, ADR-0008) ------------

#: Panoya kaydetme kalıpları. Hepsi **iki sözcüklü**: yalnız `ekle`/`kaydet` fiili
#: kapıyı açsaydı *"bir de fire ekle"* (meşru kompozisyon isteği, MIMARI §9.2) eylem
#: sanılırdı — hedef sözcüğü (`pano`) ZORUNLU.
_PANO_KALIP = ("panoya ekle", "panoya kaydet", "panoya at", "panoya koy",
               "panoma ekle", "panoma kaydet", "panele ekle", "panoya sabitle",
               "dashboarda ekle", "dashboard'a ekle")

#: Yinelenme ifadeleri → (`every`, `weekday`). `her ay` BİLEREK YOK: `ScheduleRequest`
#: yalnız hour|day|week destekler ve desteklenmeyen bir şeyi sessizce haftalığa
#: çevirmek kullanıcının istemediği bir şeyi kurmak olurdu (bkz. `_ZAMAN_DISI`).
_GUNLER = ("pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar")
_YINELENME: tuple[tuple[str, str, int | None], ...] = (
    *((f"her {g}", "week", i + 1) for i, g in enumerate(_GUNLER)),
    ("her hafta", "week", 1),
    ("haftada bir", "week", 1),
    ("her gun", "day", None),
    ("hergun", "day", None),
    ("her sabah", "day", None),
    ("her aksam", "day", None),
    ("her gece", "day", None),
    ("gunde bir", "day", None),
    ("her saat", "hour", None),
    ("saatte bir", "hour", None),
)

#: Tanınan ama DESTEKLENMEYEN yinelenmeler — sessizce düşmesinler diye AYRI liste.
#: Bunlar da eylem sayılır; öneri yerine **dürüst sınır beyanı** üretirler.
_ZAMAN_DISI = ("her ay", "ayda bir", "her yil", "yilda bir", "her ceyrek", "her donem")

#: Teslim fiilleri. Yinelenme TEK BAŞINA yetmez — *"her ay ciro"* bir GRANÜLERLİK
#: sorusudur, zamanlama değil. Kapı iki kanatlı: yinelenme **ve** teslim fiili.
#:
#: `raporla` BİLEREK YOK: `_syn_hit` çekim ekine toleranslıdır ve *"raporları"* onu
#: eşleştirirdi — *"her hafta raporları karşılaştır"* bir veri sorusudur. Çıplak `at`
#: da yok (Türkçede bağımsız bir sözcük); yalnız `mail at` gibi bağlı biçimler alınır.
_TESLIM_FIIL = ("yolla", "gonder", "epostala", "e-postala", "postala",
                "mail at", "mail gonder", "bildir", "ilet", "haber ver", "hatirlat")

#: Günün saati varsayılanları — ifadenin kendisinden gelir, uydurulmaz.
_SAAT_IMASI = (("her sabah", "08:00"), ("her aksam", "18:00"), ("her gece", "22:00"))

#: "saat 9'da", "8'de", "09:00", "17.30" — hepsi aynı çapa: bir sayı + saat eki/ayracı.
#:
#: ⚠ `_norm` KESME İŞARETİNİ SİLER: `09:00'da` → `09:00da`. İlk sürüm dakikadan sonra
#: `\b` istiyordu; kesme gidince ardından harf geldiği için o çapa TUTMUYOR ve desen
#: `00da`ya kayıp saati **00:00** okuyordu (ölçüldü). Dakika sonrası çapa artık
#: "rakam DEĞİL" (`(?!\d)`) — ekten bağımsız.
_SAAT_RE = re.compile(r"\b(?:saat\s*)?([01]?\d|2[0-3])[:.]([0-5]\d)(?!\d)|"
                      r"\b(?:saat\s*)?([01]?\d|2[0-3])\s*(?:de|da|te|ta)\b")


@dataclass
class Karar:
    """Eylem kapısının çıktısı.

    `oneri is None` **başarısızlık değildir**: eylem tanındı ama uygulanamıyor
    (çapa yok ya da yetenek yok). O durumda `not_` kullanıcıya NEDENİNİ söyler —
    sessiz düşme YOK.
    """

    eylem: str
    not_: str
    oneri: dict[str, Any] | None = None
    iz: list[str] = field(default_factory=list)
    #: FAZ 5.1 — netleştirme chip'leri. *"Bunu takip et"* bir **sıklık söylemez** ve
    #: sessizce haftalığa çevirmek, kullanıcının **istemediği** bir zamanlama kurmak
    #: olurdu (zamanlama `geri_alinabilir=False`). Periyot yoksa **sorulur**.
    chipler: list[str] = field(default_factory=list)


def _saat_bul(q: str) -> str | None:
    m = _SAAT_RE.search(q)
    if not m:
        return None
    if m.group(1) is not None:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    return f"{int(m.group(3)):02d}:00"


def _yinelenme_bul(q: str) -> tuple[str, int | None, str] | None:
    """(every, weekday, insan-okur) — en UZUN kalıp kazanır.

    Uzunluk sırası şart: *"her pazartesi"* ile *"her hafta"* çakışmaz ama *"her gun"*
    ile *"her gunaydin"* gibi bir gelecekteki eklemede kısa kalıp önce eşleşirse yanlış
    `every` seçilirdi. Sırayı veriye bağlamak, sırayı hatırlamaya bağlamaktan güvenli.
    """
    for kalip, every, weekday in sorted(_YINELENME, key=lambda t: -len(t[0])):
        if _syn_hit(q, kalip):
            return every, weekday, kalip
    return None


def tespit(q_norm: str) -> str | None:
    """Bu ifade bir YAZMA eylemi mi? — deterministik, sıfır LLM, sıfır SQL.

    `None` = eylem değil (akış merdivene devam eder). Kapı **dar** tutulur: şüphede
    kalınca eylem DEĞİL denir, çünkü yanlış pozitif meşru bir veri sorusunu cevapsız
    bırakır — yanlış negatif ise yalnız bugünkü davranışı sürdürür.
    """
    if any(_syn_hit(q_norm, k) for k in _PANO_KALIP):
        return PANO_EKLE
    if not any(_syn_hit(q_norm, f) for f in _TESLIM_FIIL):
        return None
    if _yinelenme_bul(q_norm) or any(_syn_hit(q_norm, z) for z in _ZAMAN_DISI):
        return ZAMANLA
    return None


def _rapor_adi(cq: dict, schema: dict | None) -> str:
    """Önerinin insan-okur etiketi.

    Etiketler DERLENMİŞ KATALOGDAN gelir (`build_catalog` → `dimension_labels` ·
    `measure_synonyms_display`) — `cube_router.next_step_chips`'in kullandığı **aynı
    kaynak**. Ham şemadaki `measures` bir **dize listesidir** (`["ort_oee", …]`);
    oradan etiket türetmeye çalışmak `ort_oee` gibi bir iç ad basardı ve kullanıcı
    onaylayacağı şeyi okuyamazdı. Bu depoda "ikinci bir etiket kaynağı" deseni beş kez
    ayrışmayla sonuçlandı — burada da açılmaz.
    """
    cube = cq.get("cube") or ""
    if not cube:
        return "rapor"
    spec: dict[str, Any] = {}
    display = cube
    if schema:
        from app.cube_router import build_catalog

        try:
            _, index = build_catalog(schema)
            spec = index.get(cube) or {}
        except Exception:                        # pragma: no cover — etiket best-effort
            spec = {}
        meta = next((c for c in (schema.get("cubes") or [])
                     if c.get("name") == cube), None) or {}
        display = meta.get("display") or cube
    m_lbl = spec.get("measure_synonyms_display") or {}
    d_lbl = spec.get("dimension_labels") or {}
    _ad = lambda tbl, k: tbl.get(k) or k.replace("_", " ")   # noqa: E731
    etiket = display
    olculer = cq.get("measures") or []
    if olculer:
        olcu = ", ".join(_ad(m_lbl, m) for m in olculer[:2])
        # Katalogda ölçü etiketi cube etiketiyle AYNI olabilir (`ort_oee` → "oee",
        # cube display "OEE") — *"oee (OEE)"* yazmak kullanıcıya hiçbir şey söylemez.
        etiket = olcu if olcu.casefold() == display.casefold() else f"{olcu} ({display})"
    boyutlar = cq.get("dimensions") or []
    if boyutlar:
        etiket += " · " + " × ".join(_ad(d_lbl, d) for d in boyutlar[:2])
    return etiket


_NE_ZAMAN = {"hour": "her saat", "day": "her gün", "week": "her hafta"}


def degerlendir(q_norm: str, cube_query: dict | None, *,
                schema: dict | None = None,
                view_hint: str | None = None,
                period: str | None = None) -> Karar | None:
    """Eylem kapısı. `None` → eylem değil; `Karar` → merdivene HİÇ girilmez.

    Çağıran (`routers/ask.py`) bu kararı bir `AskResponse`'a çevirir; ne SQL üretilir
    ne LLM çağrılır — eylem ifadesi bir veri sorusu DEĞİLDİR.
    """
    ad = tespit(q_norm)
    if ad is None:
        return None
    iz = [f"eylem sınıfı ({ad}) → deterministik yanıt (LLM'siz, SQL'siz)"]

    # ÇAPA KAPISI — argümanlar konuşmadaki DOĞRULANMIŞ sorgudan gelir, uydurulmaz.
    if not (cube_query or {}).get("cube"):
        # 🔴 FAZ 5.17 — **HİTAP ÖLÇÜLEN KUSURDU.** Bu metin *"siz"* kipindeydi
        # (*"kastettiğinizi"*, *"sorunuzu"*, *"tekrarlayın"*) ama `ask.py` 15 isabetle
        # *"sen"* kipindeydi: ikisi aynı oturumda karşılaşınca ürün **iki kişi gibi**
        # konuşuyordu. Metin artık katalogdan geliyor ve kip **tek yerde** kararlı.
        from app import soz as _soz

        return Karar(eylem=ad, iz=[*iz, "çapa yok → dürüst sınır beyanı"],
                     not_=_soz.soz("ret.capa_yok"))

    rapor = _rapor_adi(cube_query or {}, schema)
    b = beyan(ad)

    if ad == PANO_EKLE:
        args: dict[str, Any] = {"title": rapor, "cube_query": cube_query}
        if view_hint:
            args["view_hint"] = view_hint
        if period:
            args["period"] = period
        return Karar(eylem=ad, iz=iz, not_=b.ozet_kalibi.format(rapor=rapor, ne_zaman=""),
                     oneri={"eylem": ad, "ozet": b.ozet_kalibi.format(rapor=rapor,
                                                                     ne_zaman=""),
                            "izin": b.izin, "geri_alinabilir": b.geri_alinabilir,
                            "argumanlar": args})

    # --- ZAMANLA ---------------------------------------------------------------
    y = _yinelenme_bul(q_norm)
    if y is None:
        # Tanındı ama YETENEK YOK. Sessizce haftalığa çevirmek, kullanıcının
        # istemediği bir zamanlama kurmak olurdu → dürüstçe ne YAPABİLDİĞİMİZİ söyle.
        from app import soz as _soz

        # ⚠ Aynı kusur: *"söylerseniz"* → *"söylersen"* (katalog kipi).
        return Karar(eylem=ad, iz=[*iz, "desteklenmeyen periyot → dürüst sınır beyanı"],
                     not_=_soz.soz("bilgi.periyot_desteklenmiyor"))
    every, weekday, _kalip = y
    saat = _saat_bul(q_norm) or next(
        (s for k, s in _SAAT_IMASI if _syn_hit(q_norm, k)), "08:00")
    args = {"label": rapor, "cube_query": cube_query, "every": every,
            "at": None if every == "hour" else saat}
    if weekday:
        args["weekday"] = weekday
    if period:
        args["period"] = period
    ne_zaman = _NE_ZAMAN[every]
    if every == "week" and weekday:
        ne_zaman = f"her {_GUNLER[weekday - 1]}"
    if every != "hour":
        ne_zaman += f" saat {saat}'de"
    ozet = b.ozet_kalibi.format(rapor=rapor, ne_zaman=ne_zaman)
    return Karar(eylem=ad, iz=iz, not_=ozet,
                 oneri={"eylem": ad, "ozet": ozet, "izin": b.izin,
                        "geri_alinabilir": b.geri_alinabilir, "argumanlar": args})


def takip_karari(q_norm: str, cube_query: dict | None, *,
                 schema: dict | None = None,
                 period: str | None = None) -> Karar | None:
    """FAZ 5.1 — **6. tür (`TUR_TAKIP`) → `zamanla.olustur` ÖNERİSİ.**

    🔴 **Yeni motor YAZILMADI.** `degerlendir()`'in `ZAMANLA` dalı, `EYLEM_KAYIT`, onay
    ucu ve `schedules.create_schedule` **zaten vardı**; eksik olan tek şey **erişimdi**:
    *"bunu takip et"* hiçbir kalıba uymadığı için `SINIF_YENI` → **R10** → dürüst red
    alıyordu. Bu fonksiyon o boşluğu kapatır, ikinci bir zamanlama yolu **açmaz**.

    ## 🔴 PERİYOT UYDURULMAZ

    *"Bunu takip et"* bir **sıklık söylemez**. Sessizce haftalığa çevirmek, kullanıcının
    **istemediği** bir zamanlama kurmak olurdu — ve zamanlama `geri_alinabilir=False`'tır
    (kurulmuş bir gönderim geçmişe dönük silinemez). Periyot yoksa **sorulur**.

    ⚠ Bu, `ADR-0007-K3`'ün (*dönem eksikse SOR*) yazma tarafındaki karşılığıdır.
    """
    if not (cube_query or {}).get("cube"):
        return Karar(eylem=ZAMANLA,
                     iz=["takip niyeti (TUR_TAKIP) → çapa yok → dürüst sınır beyanı"],
                     not_=("Neyi takip edeyim? Önce sorunuzu sorun (örn. *“bu yıl makine "
                           "bazında OEE”*), sonra cevabın altından *“bunu takip et”* "
                           "deyin — raporu birebir o hâliyle zamanlarım."))
    if _yinelenme_bul(q_norm) is None and not any(
            _syn_hit(q_norm, z) for z in _ZAMAN_DISI):
        rapor = _rapor_adi(cube_query or {}, schema)
        return Karar(
            eylem=ZAMANLA,
            iz=["takip niyeti (TUR_TAKIP) → periyot YOK → netleştirme (periyot "
                "UYDURULMAZ; zamanlama geri alınamaz)"],
            not_=(f"“{rapor}” raporunu ne sıklıkta göndereyim? Şu an **saatlik, günlük "
                  f"ve haftalık** gönderim yapabiliyorum."),
            chipler=["her gün gönder", "her hafta gönder", "her saat gönder"])
    # Periyot VAR → var olan `ZAMANLA` dalını AYNEN kullan (ikinci bir yol yok).
    return degerlendir(q_norm, cube_query, schema=schema, period=period)
