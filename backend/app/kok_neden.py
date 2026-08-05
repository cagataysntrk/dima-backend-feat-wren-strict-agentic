"""🌳 **KÖK-NEDEN HARİTASI** — düğüm şeması, sinyal puanı ve dört durum.

## Neden bu modül var — ve neden arayüzde DEĞİL

Kullanıcının ölçülmüş şikâyeti: *"çok karışık, kullanıcılar kolay kolay anlamıyor
çözemiyor."* Bugünkü `DrillDownPanel` bir **tablo yığını**: hangi yolun bakmaya değer
olduğunu **söylemiyor**, kullanıcı sayıların içinde kayboluyor.

Eksik olan veri değil, **önceliktir**. Bu modül her dallanma adayını bir **hipoteze**
çevirir ve ona iki şey iliştirir: `sinyal` (bakmaya ne kadar değer) ve `durum`
(neye dayanıyor). Arayüz bunları **hesaplamaz, gösterir**.

> 🔴 **Puanlama neden backend'de:** insanın tıklayarak verdiği karar (*"hangi boyutta
> dallanayım"*) ile bir ajanın vereceği karar **aynı karardır**. Frontend'e gömülü bir
> mantık **çağrılamaz** — o yüzden *"kök neden analizi yap"* denildiğinde ajan aynı
> ağacı üretemezdi. `tools.KAYIT`'a girebilmesinin şartı HTTP'den ayrık olmaktır
> (`contribution.arastir` bu dersi bir kez ödedi: router'a yapışıkken planlayıcıya
> `dis_adim(gated=false)` diye **itiraf** olarak giriyordu).

## Dört durum — ve neden ⊘ olanı da GÖSTERİLİR

| durum | anlamı |
|---|---|
| `kanitli` | veri **var**, sinyal eşiğin **üstünde** |
| `zayif` | veri var, sinyal **düşük** |
| `olculemedi` | boyut var ama veri **yok** / **taranmadı** |
| `kapsam_disi` | bu cube o boyutu **taşımıyor** (ilişkili bir cube taşıyor) |

🔴 **Silik düğümler bu tasarımın en dürüst parçasıdır.** *Yalnız bulduğunu gösteren bir
ağaç, bakmadığını gizler.* Bugün `contribution.arastir` bulgusuz boyutu **sessizce
düşürüyor** (`if not rapor["bulgular"]: continue`) ve `MAX_BOYUT` sınırının ötesini hiç
taramıyor — ikisi de doğru kararlar, ama sonucu kullanıcıya *"baktım, yok"* gibi
okunuyor. Oysa biri *"baktım, yok"*, öteki *"bakmadım"*. Bu modül ikisini **ayırır**.

Bu, deponun kendi **⊘ ÖLÇÜLEMEDİ** üçüncü hâlinin görsel karşılığıdır: ölçülemeyen
paydadan çıkar ama **sayılır ve görünür**.

⚠ **Silik ≠ kapalı.** Hiçbir düğüm devre dışı bırakılmaz, yalnız önceliksizleşir —
çünkü bazen **verinin yokluğu bulgunun kendisidir** (*"o vardiyada hiç kayıt yok"*).

## Yeni istatistik motoru YOK

Sinyal `contribution.rank_dimensions`'ın kullandığı **aynı** büyüklüktür (en büyük tek
segmentin brüt paydaki yüzdesi — Adtributor'ın *surprise* ölçüsünün okunabilir hâli).
Aday sırası `drill.available_dimensions`'tan (maliyet + fan-out güveni), kapsam dışı
düğümler `drill.related_cubes`'tan gelir. Bu modül **karar verir**, hesap icat etmez.
"""

from __future__ import annotations

from typing import Any

from app.logging_setup import get_logger

_log = get_logger("kok_neden")

#: Düğüm durumları — arayüzdeki dört görsel ağırlığın **tek sahibi**.
#: ⚠ Sıra anlamlıdır: `KANITLI` en güçlü, `KAPSAM_DISI` en silik.
KANITLI = "kanitli"
ZAYIF = "zayif"
OLCULEMEDI = "olculemedi"
KAPSAM_DISI = "kapsam_disi"

DURUMLAR = (KANITLI, ZAYIF, OLCULEMEDI, KAPSAM_DISI)

#: 🔴 Sinyal tabanı. **Yüksek kardinaliteli boyutlar için** gerekli: 50 segmentli bir
#: boyutta *"adil pay"* %2'dir ve o eşik gürültüyü bulgu diye satar.
SINYAL_TABANI = 20.0

#: *"Adil payın kaç katı"* — `kanitli` olmanın göreli şartı.
#: ⚠ Mutlak bir eşik (*"%25'ten büyükse kanıtlı"*) **kardinaliteyi görmez**: 3 segmentli
#: bir boyutta %25 hiçbir şey söylemez (adil pay zaten %33), 40 segmentlide ise çok şey
#: söyler (adil pay %2,5). Bu yüzden eşik **boyutun kendi kardinalitesinden** türetilir.
ADIL_PAY_KATI = 2.0


def esik(segment_sayisi: int) -> float:
    """Bir boyutun `kanitli` sayılması için gereken en büyük-segment payı (%).

    *Bilgi taşımayan bir boyut değişimi eşit dağıtır.* n segmentli bir boyutta adil pay
    `100/n`; bir segment payın **iki katını** taşıyorsa o boyut açıklayıcıdır.

    ⚠ Taban (`SINYAL_TABANI`) olmadan yüksek kardinalite eşiği sıfıra yaklaştırırdı:
    50 segmentli bir boyutta %4'lük bir pay *"kanıt"* diye gösterilirdi. Ve tavan
    doğal olarak gelir: 2 segmentli bir boyutta eşik %100 olur — yani iki-değerli bir
    boyut neredeyse hiç `kanitli` olamaz, **doğrusu da budur** (orada açıklanacak bir
    dağılım yoktur).
    """
    if segment_sayisi <= 0:
        return 100.0
    return max(ADIL_PAY_KATI * (100.0 / segment_sayisi), SINYAL_TABANI)


def _sinyal(rapor: dict) -> tuple[float, int]:
    """(en büyük segment payı %, segment sayısı) — `rank_dimensions` ile **aynı** büyüklük.

    ⚠ İki rapor türü var: segment raporunda `brut_pay` hazır, PVM raporunda yok (orada
    bulgular fiyat/miktar ayrışması taşır). Tek bir kural iki türe de uygulanır ki
    *"hangi boyut daha açıklayıcı"* sorusunun cevabı **ayrışmasın** — bu, deponun
    "aynı kuralın iki sahibi" kusurunun tam da kaçınılan hâli.
    """
    bulgular = rapor.get("bulgular") or []
    if not bulgular:
        return 0.0, 0
    n = len(bulgular)
    if bulgular[0].get("brut_pay") is not None:
        return max(abs(b.get("brut_pay") or 0) for b in bulgular), n
    brut = sum(abs(b.get("delta") or 0) for b in bulgular)
    if not brut:
        return 0.0, n
    return max(abs(b.get("delta") or 0) for b in bulgular) / brut * 100.0, n


def durum_of(rapor: dict | None, *, tarandi: bool) -> tuple[str, float]:
    """(durum, sinyal) — **dört durumun tek karar noktası**.

    🔴 `tarandi=False` ile bulgusuz taranmış bir boyut **aynı şey değildir**:
    biri *"bakmadım"*, öteki *"baktım, yok"*. Bugün ikisi de görünmüyordu ve
    kullanıcıya ikisi de *"yok"* gibi okunuyordu.
    """
    if not tarandi:
        return OLCULEMEDI, 0.0
    if not rapor or not (rapor.get("bulgular") or []):
        # Taranmış ama hiçbir segment gürültü eşiğini geçmemiş → veri var, sinyal yok.
        return ZAYIF, 0.0
    sinyal, n = _sinyal(rapor)
    return (KANITLI if sinyal >= esik(n) else ZAYIF), round(sinyal, 1)


def dugum(*, boyut: str, etiket: str, olcu: str | None, durum: str, sinyal: float,
          deger: Any = None, makbuz: str | None = None, cube_query: dict | None = None,
          gerekce: str | None = None, cocuklar: list[dict] | None = None) -> dict:
    """Tek düğüm — **sözleşmenin tek üreticisi**.

    Alanları elle sözlük yazarak üretmek, ajanın ve arayüzün **farklı şekilli** düğümler
    görmesine yol açardı; bu depoda *"bir alan adını okumadan yazmak"* dört kez kusur
    üretti. Tek bir yapıcı, o sınıfı kapatır.
    """
    if durum not in DURUMLAR:
        raise ValueError(f"bilinmeyen düğüm durumu: {durum!r}")
    return {
        "boyut": boyut,
        "etiket": etiket,
        "deger": deger,
        "olcu": olcu,
        "sinyal": round(float(sinyal), 1),
        "durum": durum,
        "gerekce": gerekce,
        "makbuz": makbuz,
        "cube_query": cube_query,
        "cocuklar": list(cocuklar or []),
    }


def _gerekce(durum: str, sinyal: float, n: int, etiket: str) -> str:
    """Düğümün **neden** o ağırlıkta olduğunun bir cümlelik hâli.

    ⚠ Kullanıcıya `z=2.4` göstermek bir gerekçe değildir. *Bir ağırlık, sebebi
    okunmadıkça bir süstür* — bu deponun güven rozeti hakkındaki kararının aynısı.
    """
    if durum == KANITLI:
        return (f"{etiket}: en büyük tek segment değişimin %{sinyal:.0f}'ini taşıyor "
                f"({n} segment arasında — eşit dağılsa %{100 / n:.0f} olurdu).")
    if durum == ZAYIF:
        if not n:
            return f"{etiket}: tarandı, hiçbir segment gürültü eşiğini geçmedi."
        return (f"{etiket}: değişim {n} segmente dağılmış, en büyüğü %{sinyal:.0f} — "
                "tek bir sorumlu görünmüyor.")
    if durum == OLCULEMEDI:
        return f"{etiket}: ⊘ taranmadı — sinyali bilinmiyor, yok DEĞİL."
    return f"{etiket}: bu cube o boyutu taşımıyor; ilişkili bir cube taşıyor."


def harita(service, schema: dict, cube_query: dict, *, mode: str = "yoy",
           max_dimensions: int | None = None, kaydet=None, satir_donustur=None) -> dict:
    """🌳 Bir `cube_query` için **kök-neden düğüm ağacının ilk katı**.

    Saf orkestrasyon — HTTP bilmez, FastAPI bilmez (`contribution.arastir` ile aynı
    biçim, aynı sebep: `tools.KAYIT`'a girebilsin ve arka plan işleri de çağırabilsin).

    ## Neden `arastir`'ı SARAR, yeniden yazmaz

    Tarama, dönemsel kıyas ve ayrıştırma zaten `contribution.arastir`'da ve **doğru**.
    Eksik olan tek şey **bakılmayanın görünmemesiydi**. Bu fonksiyon o boşluğu kapatır:
    `taranmayan_adlar` (sınır dışı kalanlar) `⊘ olculemedi` düğümüne, taranıp bulgusuz
    kalanlar `zayif`e, ilişkili cube'ların bizde olmayan boyutları `kapsam_disi`ne çevrilir.

    ⚠ **Bir kat döner, ağacın tamamını değil.** *Bir ağaç, tüm dallarını aynı anda
    gösterdiğinde ağaç olmaktan çıkar, yığın olur* — ve yığın, kullanıcının şikâyet
    ettiği şeyin ta kendisi. Sonraki kat, düğüme tıklanınca `/ask/drill` ile açılır.
    """
    from app import contribution as _katki
    from app.drill import available_dimensions, related_cubes

    cq = dict(cube_query or {})
    if not cq.get("cube"):
        from app import soz as _soz
        return {"dugumler": [], "note": _soz.soz("bilgi.yapisal_sorgu_yok")}

    cube_meta = next((c for c in (schema.get("cubes") or [])
                      if c.get("name") == cq.get("cube")), None)
    if cube_meta is None:
        return {"dugumler": [],
                "note": f"`{cq.get('cube')}` cube'u şemada yok (şema değişmiş olabilir)."}

    olcu = (cq.get("measures") or [None])[0]
    etiketler = cube_meta.get("dimension_labels") or {}
    # Aday SIRASI `available_dimensions`tan gelir: maliyet (JOIN sıçraması) + fan-out
    # güveni. Açıklayıcılık ÖNCEDEN bilinemez — onu aşağıdaki tarama ölçer.
    adaylar = [d["name"] for d in available_dimensions(cube_meta, cq)]

    cikti = _katki.arastir(service, schema, cq, mode=mode, kind="segment",
                           max_dimensions=max_dimensions, kaydet=kaydet,
                           satir_donustur=satir_donustur)
    raporlar = {r.get("dimension"): r for r in (cikti.get("raporlar") or [])}
    # 🔴 `taranmayan_adlar` sınırın ÖTESİNDE kalanlardır. Onları taranmış saymak,
    # "bakmadım"ı "yok" diye satmak olurdu.
    taranmayan = set(cikti.get("taranmayan_adlar") or [])

    dugumler: list[dict] = []
    for d in adaylar:
        rapor = raporlar.get(d)
        st, sinyal = durum_of(rapor, tarandi=d not in taranmayan)
        etiket = etiketler.get(d) or d
        _, n = _sinyal(rapor) if rapor else (0.0, 0)
        dugumler.append(dugum(
            boyut=d, etiket=etiket, olcu=olcu, durum=st, sinyal=sinyal,
            gerekce=_gerekce(st, sinyal, n, etiket),
            cube_query={**cq, "dimensions": [*(cq.get("dimensions") or []), d]},
            makbuz=(cikti.get("contract_ids") or [None])[0] if rapor else None,
        ))

    # KAPSAM DIŞI — bu cube'da olmayan ama İLİŞKİLİ bir cube'un taşıdığı boyutlar.
    # ⚠ Hayalet düğüm bir **yok** değil, bir **yol**dur: tıklanınca cube atlanır
    # (`drill.jump_to_related_cube`). Kullanıcının somut senaryosu: OEE düşük →
    # `oee` cube'unun boyutları tükendi → `makine_duruslari`na geç, duruş NEDENİNİ gör.
    aktif = set(cq.get("dimensions") or []) | {
        f.get("dimension") for f in (cq.get("filters") or [])}
    bizdeki = set(cube_meta.get("dimensions") or [])
    gorulen: set[str] = set()
    for ic in related_cubes(cq.get("cube"), aktif, schema.get("cubes") or []):
        ilgili = next((c for c in (schema.get("cubes") or [])
                       if c.get("name") == ic["cube"]), None)
        if ilgili is None:
            continue
        o_etiketler = ilgili.get("dimension_labels") or {}
        for d in (ilgili.get("dimensions") or []):
            if d in bizdeki or d in gorulen:
                continue
            gorulen.add(d)
            etiket = o_etiketler.get(d) or d
            dugumler.append(dugum(
                boyut=d, etiket=etiket, olcu=olcu, durum=KAPSAM_DISI, sinyal=0.0,
                gerekce=(f"{etiket}: `{cq.get('cube')}` bu boyutu taşımıyor — "
                         f"`{ic['label']}` cube'u taşıyor ({', '.join(ic['shared_dimensions'])} "
                         "üzerinden bağlı)."),
                cube_query=None,
            ))

    if taranmayan:
        _log.info("kök-neden haritası: %d boyut taranmadı (⊘ düğüm olarak gösteriliyor): %s",
                  len(taranmayan), ", ".join(sorted(taranmayan)))

    return {
        "cube": cq.get("cube"),
        "olcu": olcu,
        "mode": mode,
        # 🔴 SIRA: kanıtlı → zayıf → ⊘ → hayalet; eşitlikte sinyal büyükten küçüğe.
        # ⚠ `sorted` kararlıdır: eşit ağırlıkta `available_dimensions`ın maliyet sırası
        # KORUNUR — yoksa aynı soru iki kez sorulduğunda farklı bir ağaç görünürdü.
        "dugumler": sorted(dugumler,
                           key=lambda x: (DURUMLAR.index(x["durum"]), -x["sinyal"])),
        "taranmayan_adlar": sorted(taranmayan),
        "note": cikti.get("note"),
    }
