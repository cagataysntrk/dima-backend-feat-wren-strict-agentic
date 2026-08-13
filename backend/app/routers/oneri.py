r"""🔴 `FAZ 6.1` — **`GET /oneri`**: yazarken-ara ucu.

`app/oneri.py` motorunu HTTP'ye açar. **İnce bir çevirici**: karar da, yetki süzmesi de
motorun içindedir; burası yalnız isteği çözer ve cevabı biçimler.

## Neden bu uç motorla AYNI DEMETTE geliyor

`FAZ 3`'ün bulgusu: bu depoda *«yazılmış ama bağlanmamış»* **beş kez** ölçüldü, ve
`test_g_yetim_modul_kapisi` bunu bir **borç tavanı** ile tutuyor — doktrini açık:
*«kapı yalnız artışı yasaklar.»* Motor bir tur önce doğdu (ön koşulu bir **ölçüme**
bağlıydı 🅕); kapı *«bağla»* dedi ve **haklıydı**. Bu dosya o bağlamadır.

⚠ Ve uç **tek başına** da yetmez: `test_g_yetim_uc_kapisi` bir ucun **FE'de geçmesini**
şart koşar (tavan **8**). O yüzden `6.2` (FE tüketicisi) bu commit'in **içinde**.

## ⊘ Ne YAPMIYOR

* Sorgu **koşmuyor** — dönen aday bir **ad**dır, bir sayı değil. Sayıyı küp koyar (`§38.4`).
* LLM **çağırmıyor** (`E-8`: sıcak yolda seri ikinci tur yok).
* `/ask` yoluna **dokunmuyor**.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.auth.dependencies import require_company

router = APIRouter(tags=["oneri"])

#: ADR-0020 — sessiz yutma yok. Bir telemetri hatası cevabı bozmaz (`§101.1`) ama
#: **duyurulur**: duyurulmayan bir hata, olmamış bir hatadan ayırt edilemez.
_log = logging.getLogger("dima.oneri")


def _liste(ham: str) -> list[str]:
    """`"a,b"` → `["a", "b"]`. Biçimin **tek sahibi** burasıdır ㊲.

    ⚠ Boş parçalar düşer: `"a,,b"` → `["a","b"]`. Bir arayüzün ürettiği fazladan virgül
    bir hata değil bir **gürültü**dür 🅡; onu uçta temizlemek, her tüketiciye aynı
    temizliği öğretmekten ucuzdur.
    """
    return [p.strip() for p in ham.split(",") if p.strip()]


def _capa_kur(cube: str, olcu: str, kirilim: str, donem: str, varlik: str) -> dict | None:
    """Parçalı query paramlarından **`cube_query` biçiminde** çapa.

    ⚠ Çapa yeni bir model **değildir**: `oneri_cumle._capa_oku` doğrudan bir `cube_query`
    bekler, yani buradaki iş bir **çeviri değil, bir toplama**dır. Yeni bir çapa şeması
    icat etseydik `§5.1`'in *«bağlam gizli durum olmaktan çıkar»* vaadi, iki temsili olan
    bir bağlama dönerdi (`KAT-1`).

    ⚠ `varlik` biçimi **`boyut:deger`** (`makine:RAM-3`) — ve bu bilinçli: değerin hangi
    boyuta ait olduğunu **tahmin etmek** (*«ilk kırılımdır herhâlde»*) bu deponun defalarca
    ısırılmış olduğu türden bir varsayımdır ㊱. Boyut yoksa varlık **taşınmaz**; eksik
    bir çapa, yanlış bir çapadan iyidir.
    """
    if not cube.strip():
        return None
    cq: dict = {"cube": cube.strip()}
    if (m := _liste(olcu)):
        cq["measures"] = m
    if (d := _liste(kirilim)):
        cq["dimensions"] = d
    if donem.strip():
        cq["period_expr"] = donem.strip()
    if ":" in varlik:
        boyut, _, deger = varlik.partition(":")
        if boyut.strip() and deger.strip():
            cq["filters"] = [{"dimension": boyut.strip(), "operator": "eq",
                              "value": deger.strip()}]
    return cq


@router.get("/oneri", dependencies=[Depends(require_company)])
def oneri_ara(request: Request, q: str = Query("", max_length=120),
              capa_cube: str = Query("", max_length=64),
              capa_olcu: str = Query("", max_length=240),
              capa_kirilim: str = Query("", max_length=240),
              capa_donem: str = Query("", max_length=64),
              capa_varlik: str = Query("", max_length=120)) -> dict:
    """Katalogdan yazarken-ara **cümleleri** (`§5.1`) — ve ham adaylar.

    🔴 **Yetki motorda süzülür, burada değil** (`KAT-1`): `app/oneri.terimler()`
    `katman_b.karar`'ı çağırır ve **sıralamadan önce** süzer. Buradaki tek iş
    allowlist'i **almak**tır (`katman_b.allowlist`), yorumlamak değil.

    ## 🔴 ÇAPA NEDEN **PARÇALI QUERY PARAMI** — ve neden gövde değil

    Ölçülen kısıt: bu uç `GET`'tir ve **typeahead**'in sıcak yoludur (ılık `p95`
    **49,23 ms**, eşik 300 ms). Üç seçenek vardı:

    | seçenek | bedeli |
    |---|---|
    | `POST` + gövde | `GET` sözleşmesi kırılır, tarayıcı önbelleği/iptali kaybolur |
    | `capa=<url-encoded JSON>` | uçta **JSON ayrıştırıcı** doğar 🅪 — ikinci bir sözleşme |
    | **parçalı param** ✅ | ayrıştırma yok, alanlar **adıyla** görünür, kısa |

    ⚠ Çoklu alanlar **virgülle**: `capa_olcu=ort_oee,toplam_fire_kg`. Bu bir biçim
    kararıdır ve **tek yerde** yaşar (aşağıdaki `_liste`), iki tarafta değil ㊲.

    ⚠ Çapa **doğrulanmaz, taşınır**: geçersiz bir çapa cümle üretmez (aday eşleşmez) ve
    bir sorgu **koşulmaz** — bu uç sorgu koşmuyor. Doğrulamanın yeri `parse_cube_query`
    beyaz listesidir; burada ikinci bir doğrulayıcı kurmak ㊲ olurdu.
    """
    from app import katman_b, oneri, oneri_cumle
    from app.company_registry import wren_for_request

    principal = getattr(request.state, "principal", None)
    izinliler = katman_b.allowlist(request, principal)
    schema = wren_for_request(request).schema()
    adaylar = oneri.ara(q, schema, izinliler=izinliler)

    capa = _capa_kur(capa_cube, capa_olcu, capa_kirilim, capa_donem, capa_varlik)
    # ⚠ Cümle kurmak **sorgu koşmaz ve LLM çağırmaz** (`E-8`): `oneri_cumle` saf bir
    # modüldür. Sıcak yola eklenen tek maliyet dize birleştirmedir.
    oneriler = oneri_cumle.cumleler(adaylar, capa=capa, schema=schema)

    return {
        # 🔴 `§5.1`'in ASIL çıktısı: kullanıcı **cümle** görür, alan adı değil.
        # ⚠ `adaylar` **kaldırılmadı** — `KURAL B`: bayrak kapalıyken ve eski tüketici
        # varken davranış bugünküyle birebir kalmalı. Yeni alan **ekler**, eskisini
        # götürmez 🅐; götürseydi bu uç, henüz göç etmemiş bir tüketiciyi bozardı.
        "oneriler": [
            {"kimlik": o.kimlik, "metin": o.metin, "grup": o.grup, "tur": o.tur,
             "cube_query": o.cube_query, "cube": o.cube}
            for o in oneriler
        ],
        "capa": capa,
        "adaylar": [
            {"kimlik": a.kimlik, "etiket": a.etiket, "cube": a.cube, "kip": a.kip}
            for a in adaylar
        ],
        # 🅖 Kip **beyan edilir**: gömücü soğuksa liste leksik'tir ve kullanıcı arayüzü
        # bunu (isterse) söyleyebilir. Sessizce kalitesi düşen bir liste, düşmediğini
        # sandıran bir listedir.
        "kip": adaylar[0].kip if adaylar else "yok",
        # `5.7/④` — indeksin durumu **beyan edilir**: `taze` · `yok` (ilk istek, henüz
        # kurulmadı) · `kapali` (gömücü yok → liste leksiktir). Bayat bir hâl **yoktur**:
        # önbellek şema sürümüyle anahtarlıdır, eski sürüm okunamaz 🅐.
        "indeks": oneri.indeks_durumu(schema),
    }


@router.get("/oneri/pill", dependencies=[Depends(require_company)])
def oneri_pill(request: Request, q: str = Query("", max_length=400)) -> dict:
    """🔴 `§5.2` + `§5.3` — **`Niyet`in GÖRÜNÜR HÂLİ**: pill satırı + canlı doğrulama.

    ```
       olcu_adaylari      donemler        kirilimlar       turler
            │                │                │               │
       [toplam_fire_kg] [bu ay]    [makineye göre]    [+ ölçü ▾]
    ```

    🔴 **Yeni model kurulmuyor, mevcut model çiziliyor.** Pill'ler `app/niyet.py::Niyet`
    alanlarından **türetilir**; ikinci bir temsil doğsaydı bir gün biri ötekinden ayrılır
    ve kullanıcı *«anladığım şu»* diye yanlış bir şey okurdu (`KAT-1`).

    ⚠ **`+` TİPLİDİR** (`artilar`): `[+ ölçü] [+ kırılım] [+ dönem] [+ adım]`. Tek bir `+`
    üç ayrı anlama gelir (aynı sorguya ölçü ekle · adım ekle · ayrı rapor) ve bu deponun
    bir numaralı tuzağıdır — *«göre/bazında»* üç anlamlıydı ve **üç kez** ısırdı.

    ⚠ `dogrula` **koşmadan** çalışır: geçersiz bir kombinasyon kırmızıya döner ve nedenini
    söyler. *«Sayıyı küp koyar»* ilkesinin arayüz karşılığı budur — **imkânsız soru
    sorulamaz hâle gelir.**

    ⊘ Bu uç **sorgu koşmaz ve LLM çağırmaz**: `Niyet` çözümlemesi deterministiktir.
    """
    from app import niyet as _niyet
    from app import pill
    from app.company_registry import wren_for_request

    if not q.strip():
        # ⚠ Boş soruda **boş pill satırı** — uydurma bir niyet çizmek, kullanıcının
        # yazmadığı bir şeyi ona *«anladığım şu»* diye göstermek olurdu 🅡.
        return {"piller": [], "artilar": [], "hatalar": []}

    schema = wren_for_request(request).schema()
    n = _niyet.coz(q, schema)
    return {
        "piller": [{"alan": p.alan, "metin": p.metin, "deger": p.deger,
                    "silinebilir": p.silinebilir} for p in pill.pillerden(n, schema)],
        # ⚠ `tip` **taşınır** ve `alan` `None` olabilir: `+ adım` bir `Niyet` alanına
        # değil **plana** karşılık gelir (`sonuc="plan"`). İkisini tek anahtara sıkıştırmak,
        # `+`'ın tipini kaybetmek — yani kapatmaya çalıştığımız tuzağı geri açmak olurdu.
        "artilar": [{"tip": a.tip, "alan": a.alan, "metin": a.metin, "sonuc": a.sonuc,
                     "secenekler": [{"deger": s.deger, "metin": s.metin}
                                    for s in a.secenekler]}
                    for a in pill.artilar(n, schema)],
        "hatalar": [{"alan": h.alan, "deger": h.deger, "neden": h.neden}
                    for h in pill.dogrula(n, schema)],
    }


@router.post("/oneri/makro", dependencies=[Depends(require_company)])
def oneri_makro(request: Request, govde: dict | None = None) -> dict:
    """🔴 `§7 ②` — **adlandırılmış makro KOŞULUR**: tek tıklama, N deterministik adım.

    Şeritteki *«… neden bu seviyede?»* satırı bir `cube_query` **taşımaz** (`TUR_NEDEN`,
    `cube_query=None`); taşıdığı şey bir **reçete adıdır**. Bu uç o adı bir **plana**
    çevirir (`makro.plan_uret`) ve planı **LLM'siz** koşar (`plan_tuketici.calistir`).

    ## 🔴 Neden `plan_tuketici.cevap` DEĞİL

    Ölçüldü (`plan_tuketici.py:405-411`): `cevap()` *«boşluğun tek kapısı»*dır ve **LLM
    çağrısını kendi içinde** yapar — bayrak kapalıysa `None` döner, açıksa garsona plan
    kurdurur. Yani `cevap`'tan geçen bir makro `②` kademesi olmaktan çıkar, `③` (özgün
    besteleme) olurdu. `§7`'nin tablosu `②` için LLM'i **⊘** işaretliyor ve kademelerin
    *«karışmamalı»* olması o tablonun başlığıdır.

    ⚠ Bu yüzden burada **plan hazır gelir** (bir reçeteden), garsondan **istenmez**.

    ## Dürüst ret 🅤

    Plan koşulamazsa `neden_olmadi` ile **adım adım** gerekçe döner — sessiz bir boş
    cevap, tıklandığında hiçbir şey yapmayan bir düğmedir ve hiçbir yerde iz bırakmaz.
    """
    from app import makro, plan_kosucu, plan_tuketici
    from app.company_registry import wren_for_request

    d = govde if isinstance(govde, dict) else {}
    ad = str(d.get("ad") or "").strip()
    cq = d.get("capa") if isinstance(d.get("capa"), dict) else None
    boyut = str(d.get("boyut") or "").strip()
    # 🔴 **ÖLÇÜLMÜŞ KUSUR (arayüz bağlanırken, 2026-08-13).** İlk yazımda `calistir`'a
    # `soru=ad` geçiyordum — yani *«neden»*. İki ayrı zarar:
    #
    # * `soru` `calistir`'ın **dönem çözümü** için okunuyor (`period_expr` varsa);
    #   bir **makro adı** dönem taşımaz, kullanıcının cümlesi taşır.
    # * Cevapta `question` **hiç yoktu**; `AskResponse` onu zorunlu tutuyor ve istemci
    #   `question.startsWith(...)` çağırıyor → dürüst ret yolunda `undefined` üstünde
    #   çökme. Arayüz bunu **yamamak** zorunda kalmıştı 🆘 — bir sözleşme eksiğini
    #   tüketiciye ödetmek, onu iki yerde bilmek demektir ㊲.
    #
    # ⊙ `metin` **tıklanan cümledir** (*«toplam fire (kg) neden bu seviyede?»*): hem
    # dönem çözümüne doğru girdi, hem kullanıcının kartta göreceği soru. Yoksa `ad`'a
    # düşer — eski davranış korunur 🅐.
    metin = str(d.get("metin") or "").strip() or ad
    if not ad or not cq:
        raise HTTPException(status_code=400,
                            detail="`ad` ve `capa` zorunlu — makro bir çapanın üstünde koşar.")

    try:
        plan = makro.plan_uret(ad, cq, boyut=boyut)
    except ValueError as e:                                # bilinmeyen ad / eksik boyut
        raise HTTPException(status_code=400, detail=str(e)) from e

    service = wren_for_request(request)
    schema = service.schema()
    principal = getattr(request.state, "principal", None)
    from app.katalog_metni import metin_ve_indeks

    _, index = metin_ve_indeks(schema, principal)
    try:
        # ⚠ **Koşmadan denetle**: `dogrula` tip uyuşmazlıklarını (bir `SORGU` adımı bir
        # `olcum` adımına atıf yapıyorsa) motora hiç gitmeden yakalar. Reçeteler kapıda
        # zaten bundan geçiyor; burada ikinci kez çağrılması bir yinelenme değil, **canlı
        # çapayla** kurulan planın ilk kez denetlenmesidir.
        plan_kosucu.dogrula(plan)
        out = plan_tuketici.calistir(
            plan, service=service, index=index, schema=schema,
            cube_meta=plan_tuketici.kosum_cube_meta(schema), soru=metin)
    except plan_kosucu.PlanHatasi as e:
        _log.info("makro %r koşamadı: %s", ad, e)
        # ⚠ Dürüst ret de `question` taşır: kullanıcı **hangi** soruya ret aldığını
        # görmeden bir reddi okuyamaz.
        return {"source": None, "makro": ad, "question": metin,
                "note": plan_tuketici.neden_olmadi(plan, e)}
    out["makro"] = ad
    out["question"] = metin
    out["adim_sayisi"] = len(plan["adimlar"])
    return out


@router.post("/oneri/tik", dependencies=[Depends(require_company)])
def oneri_tik(request: Request, govde: dict | None = None) -> dict:
    """🔴 `FAZ 8.1` — **tıklama kaydı**: `(ham ifade → seçilen alan → konum)`.

    ⊘ **Yeni bir tablo AÇILMADI** 🆝: kayıt `InteractionLog`'a `kind="oneri_tik"` ile
    düşer — denetim kanalı **zaten** bu; ikinci bir depo kurmak, aynı olayın iki
    sahibi demekti (`KAT-1`).

    ⚠ `§101.1` — öneri katmanı **cevabı bozmaz**: kayıt başarısız olursa istek yine
    `{"kaydedildi": false}` ile döner. Bir telemetri hatası bir ürün hatası **değildir**.

    ⚠ Sinyalin **sınıfı burada hesaplanır ama karar burada verilmez**: `hasat.sinyal`
    saf bir fonksiyondur ve **tek sahibidir**; bu uç yalnız onu **çağırır**.
    """
    from app import hasat

    # ⚠ Ayrıştırma **modülde** (`KAT-1`) ve **asla fırlatmaz** 🅡: bozuk gövde bir
    # hâldir, bir çökme değil. Uç burada yalnız **çağırır**.
    t = hasat.govdeden(govde)
    sinif = hasat.sinyal(t)
    kaydedildi = False
    try:                                                   # pragma: no cover - IO
        # 🔴 **ÖLÇÜLMÜŞ KUSUR (curl turu, 2026-08-13).** Uç `principal`in alanlarını
        # **ham** geçiyordu ve kayıt **her çağrıda** düşüyordu:
        #
        #     Principal.tenant_id : `str | None`      ← garson/JWT'den gelen SLUG
        #     InteractionLog.tenant_id : `UUID | None`
        #
        # Yani tür uyuşmazlığı; ve `except` sessiz olduğu için **kimse görmedi**
        # (`kaydedildi:false` üç koşumda da yeniden üretildi 🅢). Sonuç ağırdı:
        # `FAZ 8`'in hasat zinciri bu kaydı okur — yazma düşükse zincir
        # **tüketicisiz bir yetenektir** 🆘.
        #
        # ⚠ Dönüştürücü **yazılmadı, ÇAĞRILDI** ㊲: `answer.py` ve `ask.py` aynı
        # `principal → InteractionLog` yazımını zaten `_uuid_or_none` ile yapıyor.
        # Altıncı bir kopya, bir gün ötekilerden ayrışacak altıncı bir kuraldı.
        from app.answer import _uuid_or_none
        from control_plane.db import get_session
        from control_plane.models import InteractionLog

        principal = getattr(request.state, "principal", None)
        with next(get_session()) as oturum:
            oturum.add(InteractionLog(
                tenant_id=_uuid_or_none(getattr(principal, "tenant_id", None)),
                user_id=_uuid_or_none(getattr(principal, "user_id", None)),
                question=t.ham_ifade,
                kind="oneri_tik",
                source="oneri",
                note=hasat.not_yaz(t),   # ㊲ biçimin tek sahibi `hasat`
            ))
            oturum.commit()
        kaydedildi = True
    except Exception:                                      # noqa: BLE001 — §101.1
        # ADR-0020: cevabı bozma, ama **sus da deme**. Bu satır olmasaydı yukarıdaki
        # tür uyuşmazlığı bir daha ancak bir curl turunda görülürdü 🅖.
        _log.exception("oneri_tik: tıklama kaydı yazılamadı")
        kaydedildi = False
    # 🅖 Sinıf **her hâlde** dönülür: kayıt tutulamasa bile istemci ne olduğunu bilir.
    return {"sinyal": sinif, "kaydedildi": kaydedildi}
