"""Rapor kompozisyonu (ADR-0024, forward) — çok-blok / çok-SAYFA rapor üretimi.

Bir rapor tek grafik değil bir KOMPOZİSYONDUR: bir dizi blok (her biri cube_query → sonuç + viz
kararı), sayfalara bölünmüş. "Sayfalarca rapor üret" (yönetici özeti → trendler → detay) buradan
çıkar. Karar deterministik (LLM yok); her blok viz motorundan (app/viz.py) kendi grafik/tablo/pivot
kararını alır → web/e-posta/PDF AYNI kompozisyonu render eder (cross-surface).

Report := {title, pages: [[Block, ...], ...], block_count}
Block  := {title, cube_query, period, result, viz, error}
"""

from __future__ import annotations

from typing import Any

_DEFAULT_PAGE_SIZE = 3  # sayfa başına blok (yazdırma/PDF dostu)
_MAX_BLOCKS = 24

#: `§RK` — bir rapor bloğunun **özet** sayılabileceği üst sınırlar. Aşılırsa blok
#: **işaretlenir** (kırpılmaz): *bir dökümü rapor diye sunmak, okunmayacağını bilerek
#: yazmaktır.*
_OZET_ESIGI = 50
_EN_FAZLA_BOYUT = 3


#: `§RÜ` — zaman kovasının Türkçe adı. **Kapalı bir sınıf**: granülerlik değerleri
#: `cube_query` sözleşmesinde sayılıdır (ADR-0008'in izin verdiği kapalı küme).
_GRAN_ADI = {"day": "günlük", "week": "haftalık", "month": "aylık",
             "quarter": "çeyreklik", "year": "yıllık"}


def bolum_basligi(cq: dict | None, cube_meta: dict | None) -> str | None:
    """🔴 `§RÜ` — **BİR CANVAS BELGESİNİN BÖLÜMLERİ ADSIZ OLAMAZ.**

    ⊙ Ölçüldü (curl `T` turu, T20): üretilen her bloğun `title`'ı **`None`**. `Block.title`
    yalnız spec'ten okunuyordu (`b.get("title")`) ve orkestratörün ürettiği bölümlerde öyle
    bir alan **hiç yok**. Yani belge yolu ne zaman planlayıcıdan gelse, kullanıcı başlıksız
    kutular görüyordu.

    ⚠ Başlık **uydurulmaz, kimlikten türetilir**: ölçü ve boyut adları kataloğun kendi
    etiketlerinden (`measure_synonyms_display` · `dimension_labels`) okunur. Etiket yoksa
    teknik ad yazılır — *bir bölümün adı, o bölümün fişinden başka bir yerden gelemez.*

    ⚠ LLM **çağrılmaz**: bir başlık için bir model turu satın almak, deterministik bir
    bilgiyi olasılıklı hâle getirmektir.
    """
    if not isinstance(cq, dict):
        return None
    meta = cube_meta or {}
    _od = meta.get("measure_synonyms_display") or {}
    _bd = meta.get("dimension_labels") or {}
    olculer = [str(m) for m in (cq.get("measures") or [])]
    for parca in (cq.get("blend") or []):
        olculer.extend(str(m) for m in ((parca or {}).get("measures") or []))
    if not olculer:
        return None
    _ad = [str(_od.get(m) or m).replace("_", " ") for m in olculer[:3]]
    baslik = ", ".join(_ad) + (" …" if len(olculer) > 3 else "")
    boyutlar = [str(_bd.get(d) or d).replace("_", " ") for d in (cq.get("dimensions") or [])]
    if boyutlar:
        baslik += " — " + " × ".join(boyutlar[:3]) + " kırılımı"
    _td = (cq.get("timeDimensions") or [{}])[0]
    _gran = _GRAN_ADI.get(str(_td.get("granularity") or ""))
    if _gran:
        baslik += f" — {_gran} seyir"
    elif not boyutlar:
        baslik += " — toplam"
    return baslik[:120]


def compose_report(
    service,
    schema: dict,
    spec: dict,
    *,
    execute: bool = True,
    limit: int = 1000,
) -> dict[str, Any]:
    """spec {title?, blocks:[{cube_query, title?, period?}], page_size?} → Report.

    Her blok: göreli dönem çözülür → cube_sql → sonuç → viz kararı (birim-farkında). Tek blok
    hatası raporu düşürmez (error alanına yazılır). Bloklar `page_size`'lık SAYFALARA bölünür.
    """
    from app import cube_router, viz

    cubes = {c.get("name"): c for c in (schema.get("cubes") or [])}
    blocks: list[dict] = []
    for b in (spec.get("blocks") or [])[:_MAX_BLOCKS]:
        cq = dict(b.get("cube_query") or {})
        period = str(b.get("period") or "").strip()
        if period:
            dfs = cube_router.date_filters(cube_router._norm(period), "tarih")
            cq["filters"] = [
                f for f in cq.get("filters", []) if f.get("dimension") != "tarih"
            ] + dfs
        block: dict[str, Any] = {
            # `§RÜ` — spec başlık verdiyse o kazanır; vermediyse fişten türetilir.
            "title": b.get("title") or bolum_basligi(cq, cubes.get(cq.get("cube"))),
            "cube_query": cq,
            "period": period or None,
            "view_hint": b.get("view_hint"),  # widget'ın kayıtlı görünümü (FE onurlandırır)
            "result": None,
            "viz": None,
            "error": None,
        }
        try:
            # DÖNEMSEL KIYAS (YoY/MoM): blok cube_query'sinde compare varsa çöz (chip yolu ile aynı).
            _cmp = cq.get("compare")
            if _cmp in ("yoy", "mom"):
                from app import yoy
                tdn = yoy.time_dim_of(schema, cq.get("cube"))
                o = yoy.compute(service, cq, _cmp, tdn, limit=limit) if execute else None
                result = ({"columns": o["columns"], "rows": o["rows"], "row_count": o["row_count"]}
                          if o else None)
                viz_cq = {**(o["base_cq"] if o else cq), "compare": _cmp}
            else:
                sql = service.cube_sql(cq)
                result = service.query(sql, limit=limit) if execute else None
                viz_cq = cq
            block["result"] = result
            if result:
                cmeta = cubes.get(cq.get("cube")) or {}
                # NOT (31 Temmuz 2026): "measure_units" YANLIŞ anahtardı — schema() dict'i ölçü
                # birimlerini "units" adıyla taşıyor (bkz. app/wren_service.py:236); bu yüzden
                # `recommend()`'in birim-farkındalığı burada da HİÇ devreye giremiyordu (`/ask`,
                # `/cube`, dashboards.py'deki AYNI hata sınıfı, bkz. app/routers/ask.py `_attach_viz`).
                block["viz"] = viz.recommend(result, cube_query=viz_cq,
                                             **viz.meta_args(cmeta))
        except Exception as exc:  # noqa: BLE001 — tek blok hatası raporu düşürmesin
            block["error"] = str(exc)[:200]
        blocks.append(block)

    try:
        page_size = max(1, int(spec.get("page_size") or _DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        page_size = _DEFAULT_PAGE_SIZE
    pages = [blocks[i:i + page_size] for i in range(0, len(blocks), page_size)] or [[]]
    return {
        "title": spec.get("title") or "Rapor",
        "pages": pages,
        "block_count": len(blocks),
        # 🔴 FAZ 5.13b — **SABİT YAPI**. Aşağıdaki üç bölüm `pages`'in YANINDA durur,
        # içinde değil: bir dışa aktarıcı sayfaları atlasa bile kapak ve **kaynak
        # listesi** elinde kalır.
        **yapi(spec, blocks),
    }


def yapi(spec: dict, blocks: list[dict]) -> dict[str, Any]:
    """FAZ 5.13b — raporun **sabit yapısı**: kapak → yönetici özeti → kaynaklar.

    ## 🔴 `contract_id` ALTTA KALIR — her formatta

    Yol haritasının şartı: *"PDF'e döküldüğünde bile `contract_id` altta kalır."* Bunun
    tek güvenilir yolu onu **bir sunum katmanına değil, yapının kendisine** koymaktır:
    `kaynaklar` listesi `pages`'ten **bağımsızdır** ve bir dışa aktarıcı sayfaları
    atlasa, kırpsa ya da yeniden düzenlese bile **onu düşürmez**.

    ⚠ *Bir kanıt, taşındığı kabın şekline bağlıysa kanıt değildir.*

    ## ⊘ ÖLÇÜLEMEYEN: Word · Excel  — ama **PDF ÖLÇÜLÜR**

    Yol haritası *"dört formatta da `contract_id` var"* diyor. Ölçüldü ve **ilk beyanım
    yanlıştı**: `docx`/`openpyxl` gerçekten yok, ama **PDF VAR** — `ReportView`'in
    `window.print()` yolu. Tarayıcı baskısı bir dışa aktarımdır ve kaynak listesi o
    baskıda **görünmek zorundadır** (`print:hidden` OLMAMALI).

    *Var olan bir yolu "ölçülemez" ilan etmek, ölçmemenin en kolay yoludur.*

    ## Yönetici özeti neden buradan üretiliyor

    İçgörü kartlarının **birleşimi**dir ve `interpret()`'in zaten hesapladığı olgulardan
    gelir — **yeni bir anlatı motoru yazılmaz**. LLM çağrılmaz; özet bir **derleme**dir,
    bir yorum değil.
    """
    from datetime import date

    kaynaklar = [
        {"blok": b.get("title") or f"#{i + 1}", "contract_id": b.get("contract_id"),
         "cube": (b.get("cube_query") or {}).get("cube")}
        for i, b in enumerate(blocks)
    ]
    olgular: list[str] = []
    for b in blocks:
        for f in ((b.get("interpretation") or {}).get("facts") or [])[:2]:
            metin = str(f.get("text") or "").strip()
            if metin and metin not in olgular:
                olgular.append(metin)
    return {
        "kapak": {
            "baslik": spec.get("title") or "Rapor",
            "tarih": str(spec.get("tarih") or date.today().isoformat()),
            # ⚠ Yazar **uydurulmaz**: verilmediyse `None` kalır. Bir raporun altına
            # olmayan bir ad yazmak, o raporu kimsenin savunmadığı bir belge yapar.
            "yazar": spec.get("yazar") or None,
        },
        "yonetici_ozeti": olgular[:8],
        # 🔴 KAYNAK LİSTESİ — `pages`'ten BAĞIMSIZ ve her formatta altta kalır.
        "kaynaklar": kaynaklar,
        # ⊘ Kapının ölçemediği şey **yazılı**: bu üç dışa aktarıcı depoda YOK.
        # ⚠ **PDF listede DEĞİL**: `window.print()` yolu var ve kaynak listesi o baskıda
        # görünüyor (`ReportView`, `print:hidden` taşımıyor). *Var olan bir yolu
        # "ölçülemez" ilan etmek, ölçmemenin en kolay yoludur.*
        "olculemeyen_formatlar": ["word", "excel"],
    }


def bolumlerden_kur(bolumler: list[dict], *, baslik: str, schema: dict,
                    page_size: int | None = None) -> dict[str, Any]:
    """🔴🔴 `§RP` — **KOŞMUŞ BÖLÜMLERİ, YENİDEN KOŞMADAN, `Report` BİÇİMİNE DİZ.**

    ## Ölçülen kusur (araştırma turu, 2026-08-10)

        «son 2 yıl satış raporu hazırla»
          plan   : SORGU×4 + RAPOR      ← DÖRT bölüm hesaplandı
          cevap  : tek tablo            ← 🔴 üçü ATILDI

    Orkestratör bölümleri **zaten** üretiyor (`plan_tuketici._bolumler`: her biri
    `{cube_query, result}`), sonra `_son = _bolumler[-1]` ile yalnız sonuncusu dönüyordu.
    *Mutfak dört yemek pişirdi, birini servis etti.*

    ## Neden `compose_report` DEĞİL de bu

    `compose_report` bir **spec**ten yola çıkar ve her bloğu **koşar** (`cube_sql` →
    `query`). Burada sonuçlar **elde**: yeniden koşmak hem israf, hem de aynı soruya iki
    farklı sayı üretme riski (arada veri değişebilir). *Bir sonucu iki kez hesaplamak,
    onu bir kez yanlış hesaplamanın en kolay yoludur.*

    ⚠ Ama **biçimin tek sahibi yine bu dosya**: sayfalara bölme, `viz` kararı ve
    `yapi()` (kapak · yönetici özeti · kaynak listesi) aynı fonksiyonlardan geçer.
    İkinci bir `Report` üreticisi `KAT-1` olurdu — ve frontend'in (`ReportView.tsx`)
    tanıdığı **tek** biçim budur.

    ⚠ `viz` kararı burada da **birim-farkındadır** (`viz.meta_args(cmeta)`): aynı
    anahtar hatası (`measure_units` ↔ `units`) bu yolda tekrarlanmasın diye üstteki
    çağrıyla birebir aynı yazıldı.
    """
    from app import viz

    cubes = {c.get("name"): c for c in (schema.get("cubes") or [])}
    blocks: list[dict] = []
    for b in (bolumler or [])[:_MAX_BLOCKS]:
        cq = b.get("cube_query") if isinstance(b.get("cube_query"), dict) else None
        sonuc = b.get("result")
        block: dict[str, Any] = {
            # `§RÜ` — orkestratörün bölümleri başlık taşımaz; kimliğinden türetilir.
            "title": (b.get("baslik") or b.get("title")
                      or bolum_basligi(cq, cubes.get((cq or {}).get("cube")))),
            "cube_query": cq,
            "period": None,
            "view_hint": None,
            "result": sonuc,
            "viz": None,
            "error": None,
        }
        # ⚠ `viz` yalnız **satır varsa** kurulur; boş bir bölümü grafiğe çevirmek
        # kullanıcıya boş bir eksen göstermektir. Ve hata bölümü DÜŞÜRMEZ (üstteki
        # `compose_report`'un aynı kararı): bir bloğun çizilememesi raporu öldürmez.
        try:
            if sonuc and (sonuc.get("rows") or sonuc.get("row_count")):
                cmeta = cubes.get((cq or {}).get("cube")) or {}
                block["viz"] = viz.recommend(sonuc, cube_query=cq or {},
                                             **viz.meta_args(cmeta))
        except Exception as exc:                      # noqa: BLE001 — blok hatası izole
            block["error"] = str(exc)[:200]
        blocks.append(block)

    # 🔴🔴 `§RK` — **BİR RAPOR BLOĞU BİR ÖZETTİR; 1000 SATIR BİR DÖKÜMDÜR.**
    #
    # ⊙ Ölçüldü (curl `Q` turu, 2026-08-10): *«kalite raporu hazırla»* → iki blok, her
    # biri **6 boyut** (`makine,hat,musteri,kumas_cinsi,renk,renk_derinlik`) ve **1000
    # satır**. Kartezyen patlama: yazdırılabilir bir belgeye sığmaz, okunamaz.
    #
    # ⚠ Satırlar **kırpılmaz** — kırpmak sessiz bir kapsam değişikliği olurdu ve bu
    # deponun en pahalı kusur sınıfıdır. Yapılan tek şey: bloğu **işaretlemek**, ki
    # sunum katmanı (ve kullanıcı) bunun bir özet **olmadığını** bilsin.
    #
    # ⚠ Eşik `_OZET_ESIGI`: bir rapor sayfasında gözle taranabilecek satır sayısının
    # üstü. Bir sabit değil bir **karar**; değişirse burada değişir.
    #
    # *Bir dökümü rapor diye sunmak, okunmayacağını bilerek yazmaktır.*
    for _b in blocks:
        _rs = (_b.get("result") or {}).get("row_count") or 0
        _bo = len((_b.get("cube_query") or {}).get("dimensions") or [])
        if _rs > _OZET_ESIGI or _bo > _EN_FAZLA_BOYUT:
            _b["ozet_degil"] = {"satir": _rs, "boyut": _bo}

    boy = max(1, int(page_size or _DEFAULT_PAGE_SIZE))
    pages = [blocks[i:i + boy] for i in range(0, len(blocks), boy)] or [[]]
    spec = {"title": baslik or "Rapor"}
    return {
        "title": spec["title"],
        "pages": pages,
        "block_count": len(blocks),
        **yapi(spec, blocks),
    }
