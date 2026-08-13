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

import re

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


def _yazilan_varlik(q: str, schema: dict) -> str | None:
    """🔴 `§40` — **YAZILAN VARLIK**: *«ram 3»* → `makine:RAM-3`.

    ## Ölçülen kusur (kullanıcı ekran görüntüsü, 2026-08-13)

    Kullanıcı `ram 3 neden` yazdı; öneri listesinde **`RAM-3` hiç geçmedi**. Gelen
    satırlar katalog alan adlarıydı (*«duruş sayısı»*, *«arıza sayısı»*) ve içlerinden
    biri — *«kök nedene göre **ram**ak kala»* — yalnız **harf benzerliğiyle** girmişti.

    ⊙ Kök: `oneri.py`'nin evreninde **boyut DEĞERLERİ yok** (`grep dimension_values
    app/oneri.py` → **0**). Sistem `RAM-3`'ü öneremiyordu çünkü **görmüyordu** 🆘.

    ⊙ İkinci kök: cümle katmanı varlığı **yalnız çapadan** alıyordu (`capa_varlik`),
    kullanıcının **yazdığından** değil. Oysa `oneri_cumle._kapsam(varlik, etiket)`
    *«RAM-3'te duruş»* demeyi **zaten biliyor** ㊷ — eksik olan girdiydi, yetenek değil.

    ## Neden yeni bir eşleştirici YAZILMADI ㊲

    Eşleşmeyi `value_index.FuzzyIndex` yapıyor — `route()`'un değer eşleşmesinde
    kullandığı **aynı** indeks (`cube_router:3935`). Burada yalnız **boyut adı** geri
    aranıyor: `FuzzyIndex` girdilerini `dimension_values.values()` üzerinden kurduğu
    için değeri bilir, ait olduğu **boyutu** düşürür.

    ⚠ Sessiz kalma şartı: eşleşme **yoksa `None`** döner ve çapa eskisi gibi davranır —
    `KURAL B` anlamında davranış yalnız *«yazılan bir varlık tanındığında»* değişir.
    """
    from app import cube_router as cr
    from app.value_index import FuzzyIndex

    qn = cr._norm(q or "")
    kelimeler = [w for w in qn.split() if len(w) >= 2]
    if not kelimeler:
        return None
    try:
        adaylar = FuzzyIndex(schema).suggest(qn, kelimeler, top=1)
    except Exception:                                    # noqa: BLE001
        _log.warning("yazılan varlık aranamadı — öneri varlıksız sürüyor", exc_info=True)
        return None
    deger = next((a.label for a in adaylar if a.kind == "value"), None)
    if not deger:
        return None
    hedef = cr._norm(deger)
    for c in schema.get("cubes", []):
        for boyut, degerler in (c.get("dimension_values") or {}).items():
            for v in degerler or []:
                if cr._norm(str(v)) == hedef:
                    return f"{boyut}:{v}"
    return None


#: `5.9` — boş kutuda gösterilecek **çekirdek** öneri sayısı. Plan *«çekirdek 5»* diyor.
_CEKIRDEK = 5


def _cekirdek_adaylar(schema: dict, izinliler: set[str] | None) -> list:
    """🔴 `§54` — **BOŞ KUTU DA KONUŞUR** (`5.9`), ama motoru uyandırmadan.

    ## Ölçülen durum

    `oneri.ara("")` → **0 aday**, ve bu **bilinçli**: kapı
    `test_bos_ve_ANLAMSIZ_girdi_PATLAMIYOR` şunu savunuyor — *«typeahead her tuşta
    çağrılır; boş dize en sık gelen girdidir»* 🅡. Motoru her boş girdide indeks/füzyon
    boyunca koşturmak, en sık gelen istek için en pahalı yolu seçmek olurdu.

    ⟹ Bu yüzden çekirdek liste **uçta** kurulur: şemadan okunur, **hiçbir arama
    koşulmaz**. Kapının niyeti (motor sussun) korunur, planın istediği (kutu boşken de
    öneri) verilir.

    ## Neden `terimler()` çağrılıyor ㊲

    Etiket üretimi (görünen ad · sinonim · birim · küp bağlamı) ve **yetki süzmesi**
    orada. İkinci bir etiketleyici yazmak, aynı ölçünün iki farklı adla görünmesiyle
    biterdi. Buradaki tek iş **seçmektir**: küpün `default_measure`'ı.

    ⚠ `default_measure`'ı olmayan küp **atlanır** — çekirdek bir liste, rastgele bir
    ölçüyle doldurulmaz ㊱. ⚠ Değer adayları (`#`) dışarıda: boş kutuda bir makine adı
    önermek, kullanıcının hiç sormadığı bir varlığı öne sürmek olurdu.
    """
    from app import oneri

    hedef = {(str(c.get("name") or ""), str(c.get("default_measure") or ""))
             for c in schema.get("cubes") or [] if c.get("default_measure")}
    out = []
    for a in oneri.terimler(schema, izinliler):
        if "#" in a.kimlik:
            continue
        kod = a.kimlik.split(".", 1)[1] if "." in a.kimlik else ""
        if (a.cube, kod) in hedef:
            out.append(a)
        if len(out) >= _CEKIRDEK:
            break
    return out


def _katman_acik(request, principal) -> bool:
    """🔴 `§52` — **`KURAL B` SUNUCUDA DA UYGULANIR.**

    ## Ölçülen boşluk

    `OneriSeridi.tsx:56` şunu yazıyordu: *«`oneri_katmani` **sunucu tarafıdır ve bir
    YETKİdir**»* — ama ölçüldü: `grep oneri_katmani app/routers/oneri.py` → **0**. Yani
    bayrak yalnız **ön yüzde** okunuyordu; kapalı bir kiracı ucu doğrudan çağırsa öneri
    **yine** üretiliyordu. Fazın kendi `KURAL B` kapısı da bu yüzden yazılamamıştı 🆆.

    *Bir yetkiyi istemcide uygulamak, onu uygulamamaktır.*

    ⚠ Kapalıyken **404 değil boş yanıt**: bu faz öncesinde bu uçlar yoktu, dolayısıyla
    *«bayrak kapalı ⇒ hiçbir öneri»* davranışı fazın öncesiyle **eşdeğerdir**. 404 ise
    istemcide bir hata yolu açardı — kapalı bir özellik bir arıza değildir.
    """
    # ⚠ `§66` — gövde `features.oneri_katmani_acik`'a **taşındı** ㊲: aynı yüklem artık
    # cevap merdiveninde de soruluyor (`plan_tuketici.cevap`). İki `resolve_for` çağrısı
    # bir gün iki farklı ölçüte ayrışırdı — bir kiracıda öneri açık, önizleme kapalı.
    from app.features import oneri_katmani_acik

    return oneri_katmani_acik(principal)


def _bos_yanit() -> dict:
    """Kapalı katmanın yanıtı — **şekli aynı**, içeriği boş (istemci dallanmasın)."""
    return {"oneriler": [], "adaylar": [], "capa": None, "kip": "kapali",
            "indeks": {"durum": "kapali", "surum": ""}}


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
    from app import katman_b, niyet as _niyet, oneri, oneri_cumle
    from app.company_registry import wren_for_request

    principal = getattr(request.state, "principal", None)
    if not _katman_acik(request, principal):
        return _bos_yanit()
    izinliler = katman_b.allowlist(request, principal)
    schema = wren_for_request(request).schema()
    adaylar = (oneri.ara(q, schema, izinliler=izinliler) if q.strip()
               else _cekirdek_adaylar(schema, izinliler))

    capa = _capa_kur(capa_cube, capa_olcu, capa_kirilim, capa_donem,
                     capa_varlik or _yazilan_varlik(q, schema) or "")
    # ⚠ Cümle kurmak **sorgu koşmaz ve LLM çağırmaz** (`E-8`): `oneri_cumle` saf bir
    # modüldür. Sıcak yola eklenen tek maliyet dize birleştirmedir.
    # ⚠ `niyet.coz` **ölçüldü**: ılık hâlde ~4,4 ms (ilk çağrılar ısınmadır ⑨) — `p95`
    # 53,82 ms'nin ~%8'i. Kullanıcının **yazdığı** kırılımı ve dönemi cümleye taşımanın
    # bedeli budur; taşımamanın bedeli ise `fire (parti)` gibi bir **etiketti** 🆡.
    # ⚠ `q` boşsa çağrılmaz: boş metinden çıkarılacak bir niyet yoktur ve sıcak yola
    # ödenmemiş bir maliyet eklenmez.
    n = _niyet.coz(q, schema) if q.strip() else None
    oneriler = oneri_cumle.cumleler(adaylar, capa=capa, schema=schema, niyet=n, soru=q)

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
    # `§28.3` — **onay bayrağı**: çok adımlı plan önce **önizlenir**, koşum ancak
    # kullanıcı onayıyla gelir (`kos=true`). Tek adımlı planda anlamı yoktur.
    kos = bool(d.get("kos", False))
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
    # 🔴🔴 `§63` — **ÇOK ADIM (N ≥ 2) → HER ZAMAN ÖNİZLEME** (`§28.3`, bir KURAL).
    #
    # Belgenin karar tablosu bir bayrak değil bir kural veriyor:
    #
    #     tek adım · garson emin      → 🟢 koşar, pill'ler makbuz olur
    #     tek adım · garson kararsız  → 🔵 pill önerilir, kullanıcı onaylar
    #     çok adım (N ≥ 2)            → 🔴 HER ZAMAN önizleme
    #     yazma fiili                 → 🔴 senkron onay
    #
    # Gerekçesi ölçülmüş: *«plan yazılıp KOŞUYOR; 7. adımda çökerse kullanıcı SONDA
    # öğreniyor — onarım tutma %25, payda 16»*. Ve belgenin başlığı işin kendisi:
    # *«route ve garson KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor … kullanıcı KARARI
    # VERİR (bir tık)»* (`§3.1`).
    #
    # ⚠ Doğrulama **aynı** kapıdan geçer ㊲: önizleme *«daha gevşek»* bir yol değil,
    # **koşumsuz** yoldur. Bütçe de zaten `dogrula`'nın içinde (`azami_sorgu` ·
    # `plan_semasi.AZAMI_ADIM`) — ikinci bir bütçe sayacı bir gün iki farklı sınır olurdu.
    if len(plan.get("adimlar") or []) >= 2 and not kos:
        try:
            plan_kosucu.dogrula(plan)
            gecerli = True
            not_ = plan_tuketici.onizleme_notu(plan)
        except plan_kosucu.PlanHatasi as e:
            # ⊘ Geçersiz plan da **gösterilir**: kullanıcı neyin tutmadığını görmeden
            # düzeltemez. Ürünün kendi Türkçe gerekçesi taşınır, yeniden yazılmaz.
            gecerli, not_ = False, str(e)
        return {"source": "onizleme", "makro": ad, "question": metin, "gecerli": gecerli,
                "adimlar": [{"sira": i, "fiil": x.get("fiil"),
                             "metin": plan_tuketici.onizleme_satiri(x)}
                            for i, x in enumerate(plan["adimlar"], 1)],
                "note": not_}

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
    # 🔴 **ÖLÇÜLMÜŞ KUSUR (insan testi).** Burası `out`'u **olduğu gibi** döndürüyordu —
    # yani `ciktilar`·`katmanlar`·`makbuz`, bir **koşucu iç sözleşmesi**. Plan koşuyordu
    # (5 adım) ama cevapta `result` **yoktu**; arayüz onu normal kart yolundan geçirince
    # kart **gövdesiz** çizildi 🆘. *Bir yeteneğin çalışması, cevabının okunabilir olması
    # demek değildir.*
    #
    # ⚠ Sunum **yazılmadı, ÇAĞRILDI** ㊲: `plan_tuketici.bolumlere_cevir` orkestratörün
    # de kullandığı işlevdir. İkinci kez yazılsaydı bir gün biri `CIKTI_TIPI`'ni okur,
    # öteki hâlâ `SORGU`'ya bakardı — ve o gün `TREND` makrosu boş cevap verirdi.
    # ⚠ Sunum **yazılmadı, ÇAĞRILDI** ㊲: biçimin tek sahibi `plan_tuketici.kosum_yaniti`
    # ve onu `POST /plan/kos` de kullanıyor. İki yerde yazılsaydı bir gün birinde `result`
    # olur ötekinde olmazdı — bu depoda tam o kusur ölçüldü (kart gövdesiz çizildi 🆘).
    return plan_tuketici.kosum_yaniti(out, plan, schema=schema, soru=metin, makro=ad)


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


@router.post("/plan/kos", dependencies=[Depends(require_company)])
def plan_kos(request: Request, govde: dict | None = None) -> dict:
    """🔴🔴 `§66` — **ONAYLANAN PLANI KOŞAR** — ve *onaylananı*, benzerini değil.

    `§3.1`'in cümlesi: *«route ve garson, KARAR VERİCİ olmaktan çıkıp TAHMİNCİ oluyor …
    **kullanıcı KARARI VERİR (bir tık)**»*. `/ask` çok adımlı bir planı artık koşmadan
    önizliyor (`source="onizleme"` + `plan_taslagi`); bu uç o tıkın karşılığıdır.

    ## Neden planı istemci geri yolluyor — ve neden bu bir açık değil

    Onayda planı **yeniden üretmek** iki şeyi birden bozardı: `E-8` (sıcak yolda ikinci
    seri LLM turu) ve — daha ağırı — **onayın anlamını**. Model aynı soruya iki farklı
    plan üretebilir; kullanıcı A'yı onaylayıp B koşulsaydı onay bir **tören** olurdu.

    ⚠ Güven sınırı **genişlemiyor**: bu depo `POST /cube`'da zaten istemciden gelen bir
    `cube_query`'yi koşuyor. Plan da aynı iki kapıdan geçer — `plan_kosucu.dogrula`
    (**kapalı fiil kümesi** + adım/atıf tipleri) ve her adımın `parse_cube_query` beyaz
    listesi. *Bir gövdeye güvenmek ile onu doğrulayıp koşmak aynı şey değildir.*

    ⊘ **LLM YOK.** Bu uç bir plan **almaz**, bir plan **koşar**.
    """
    from app import plan_kosucu, plan_tuketici
    from app.company_registry import wren_for_request

    d = govde if isinstance(govde, dict) else {}
    plan = d.get("plan") if isinstance(d.get("plan"), dict) else None
    metin = str(d.get("soru") or "").strip()
    if not plan or not isinstance(plan.get("adimlar"), list) or not plan["adimlar"]:
        # ⚠ Dürüst ret: boş bir 200 tıklandığında hiçbir şey yapmayan bir düğmedir 🅯.
        raise HTTPException(status_code=400, detail="Koşulacak bir plan gelmedi.")

    principal = getattr(request.state, "principal", None)
    if not _katman_acik(request, principal):
        # ⚠ `KURAL B`: katman kapalıyken bu uç **hiç yokmuş gibi** davranır — önizleme de
        # üretilmiyordu, dolayısıyla onay da olamaz.
        raise HTTPException(status_code=400, detail="Öngörü katmanı kapalı.")

    service = wren_for_request(request)
    schema = service.schema()
    from app.katalog_metni import metin_ve_indeks

    _, _index = metin_ve_indeks(schema, principal)
    try:
        plan_kosucu.dogrula(plan)
        out = plan_tuketici.calistir(
            plan, service=service, index=_index,
            schema=schema, cube_meta=plan_tuketici.kosum_cube_meta(schema), soru=metin)
    except plan_kosucu.PlanHatasi as e:
        _log.info("§66: onaylanan plan koşamadı: %s", e)
        return {"source": None, "question": metin,
                "note": plan_tuketici.neden_olmadi(plan, e)}
    # ⚠ Cevap **makro yolunun biçiminde** döner: istemci ikinci bir gösterim öğrenmesin
    # (`KAT-1`). `question` zorunlu — `AskResponse` onu şart koşuyor ve kart başlığı odur.
    return plan_tuketici.kosum_yaniti(out, plan, schema=schema, soru=metin)
