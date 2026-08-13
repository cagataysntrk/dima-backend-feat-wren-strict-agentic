"""PLAN TÜKETİCİSİ — planı **motora bağlar** ve sonucunu ANLATIR (FAZ O-4, tüketici).

## Nereye giriyor: merdivenin **boşluğuna**

`E3` bu fazın en sert şartını koyuyor: *orkestratör merdivenin **yerine** geçmez,
**boşluğunu** doldurur.* Bu modül tam olarak orada çağrılır — route boş döndü, garsonun
tek-cube cevabı da yok, yani bugünkü sonuç **Discovery ya da dürüst ret**. Bir yerde
cevap varken bu modül hiç konuşmaz.

⊙ Ve `MIMARI`'nin kendi ölçüsüyle tutarlı: *"Discovery'nin her ateşlenmesi bir MUTFAK
EKSİKLİĞİ RAPORUDUR."* Bu modül o raporu **azaltmayı** hedefler, yenisini üretmeyi değil.

## İki çıktı, ve ikincisi de bir başarıdır

| durum | çıktı |
|---|---|
| plan sonuna kadar koştu | cevap **+ adım adım makbuz** |
| bir adım koşamadı | 🔴 **hangi adımda, ne eksikti** — adım adım |

İkincisi bir kaçış değil bir **ürün**: bugünkü karşılığı *"Bu soru için güvenilir bir
sorgu üretemedim."* — yani kullanıcı **neyin** eksik olduğunu öğrenemiyor. Bir eksikliği
adıyla söylemek, onu bir sonraki mutfak işine çevirir.

*Cevaplayamadığını söyleyebilen bir sistem, cevaplayamadığını gizleyenden daha çok şey
bilir.*

## ⚠ Beyaz liste burada da geçerli

Her `SORGU` adımı `parse_cube_query`'den geçer — planın içindeki bir cube sorgusu,
garsonun doğrudan ürettiği bir sorgudan **daha az** denetlenmez. Bir adımı beyaz listeden
muaf tutmak, planı Discovery'ye çevirirdi.
"""

from __future__ import annotations

import re

import json
import logging
import types
from typing import Any

from app import features as _features
from app import plan_kosucu

_log = logging.getLogger("dima.plan_tuketici")
from app.sayi_bicimi import ek as _sek, sayi as _ssayi, yuzde as _syuzde


def _govdeler(service: Any, schema: dict, cube_meta: dict | None) -> dict[str, Any]:
    """`FAZ 2` — dört fiilin gövdeleri. **Hiçbiri yeni kod değil**; hepsi zaten var olan,
    testli, deterministik fonksiyonlar. Bu sözlük onları plana **bağlar**, yazmaz.

    | fiil | gövde | not |
    |---|---|---|
    | `TREND` | `yoy.compute` | dönem kaydırıp kıyas kolonu ekler — çıktı yine **satırlar** |
    | `AYRISTIR` | `contribution.arastir` | kullanılmayan boyutları tarar (**pahalı**) |
    | `KIYASLA` | `contribution._akran_kiyasi` | `§AA1` — akran ortalamasından sapma |
    | `ANLAT` | `interpret` + `narration_guard` | 🔴 **LLM YOK** (aşağı bkz.) |

    🔴 **`ANLAT` neden LLM'siz.** Bir anlatı fiilini `llm.anlat`'a bağlamak, planın her
    turuna bir LLM çağrısı daha eklerdi — tam da `E6`'nın ve bu turun A/B'sinin cezalandırdığı
    şey. `interpret` zaten deterministik olgular üretiyor ve `narration_guard` cümleyi
    sayılara karşı doğruluyor. *Bir cümleyi model kurmadan da doğru kurabiliyorsan,
    modeli çağırmak bir yetenek değil bir masraftır.*

    ⚠ Gövdeler `PlanHatasi` fırlatmaz; yorumlayıcı zaten `TypeError`/`ValueError`'ı
    sarıyor. Buradaki tek iş **adı doğru parametreye bağlamak** — `FAZ 0`'ın ölçtüğü
    kusur tam olarak buydu.
    """
    # 🔴 `§X1` — küp → **kendi** zaman ekseni. Bir kez kurulur, gövdeler yalnız okur.
    _zaman_ekseni: dict[str, str] = {
        str(c.get("name")): (c.get("time_dimensions") or [None])[0]
        for c in (schema.get("cubes") or []) if (c.get("time_dimensions") or [])}
    _varsayilan_eksen = ((cube_meta or {}).get("time_dimensions") or ["tarih"])[0]

    def _trend(a: dict) -> list[dict]:
        # ⟳ `kaynak`tan `__cq` kazımaya çalışan hâl **kaldırıldı**: satırların içinde
        # sorgusunu taşıyan bir alan hiç yoktu, yani o dal her zaman `{}` veriyordu.
        # *Var olmayan bir alandan okumak, sessizce boş dönmenin en kibar yoludur.*
        #
        # 🔴🔴 `§X1` — **ÜÇÜNCÜ TEKRAR, ve bu kez sessizce yanlış kolona yazmadı,
        # tur ÖLDÜ.** Ölçüldü (canlı `V`, *«personel devir oranı bu yıl nasıl»*):
        #
        #     adım 2 (`TREND`) koşulamadı: Unknown filter dimension 'tarih' in cube 'ik'
        #
        # ⊙ `cube_meta` bu çağrıya `{"lower_is_better": [...]}` olarak geliyor —
        # `time_dimensions` anahtarı **hiç yok**. Yani yedek (`["tarih"]`) her zaman
        # kazanıyordu ve `ik` (`donem_tarih`) · `enerji_makine` (`donem_tarih`) gibi
        # küplerde `TREND` **yapısal olarak** koşamıyordu.
        #
        # ⚠ Doğru kaynak **sorgunun kendi küpü**dür, bir yan kanaldan gelen sözlük
        # değil: aynı planda iki farklı küpe `TREND` atılabilir ve tek bir eksen adı
        # ikisini birden doğru anlatamaz.
        #
        # *Var olmayan bir anahtarı `or` ile yedeklemek, yedeği varsayılan yapar — ve
        # varsayılan yanlışsa kusur asla görünmez, yalnız tekrarlar.*
        from app import yoy
        _cqt = a.get("cube_query") if isinstance(a.get("cube_query"), dict) else {}
        # ⚠ Eşleme **gövdenin dışında** kurulur (aşağıda `_zaman_ekseni`): kapı
        # (`test_GOVDE_SEMANIN_YASAKLADIGI_ALANI_OKUMUYOR`) gövdedeki her `.get("…")`
        # çağrısını **adımın alanı** sanıyor ve şemada olmayan bir ad görünce fiili ölü
        # ilan ediyor — haklı bir yüklem, çünkü bir gövdenin adımdan başka bir yerden
        # okuması tam da o kapının yasakladığı şey. Şemayı burada gezmek yerine
        # **önceden** çözmek hem kapıyı hem okuyucuyu doğru tutar.
        _td = _zaman_ekseni.get(_cqt.get("cube")) or _varsayilan_eksen
        return (yoy.compute(service, a.get("cube_query") or {},
                            a.get("mode") or "yoy", _td) or {}).get("rows") or []

    def _ayristir(a: dict) -> dict:
        from app import contribution
        return contribution.arastir(service, schema, a.get("cube_query") or {},
                                    mode=a.get("mode") or "yoy")

    def _kiyasla(a: dict) -> dict:
        from app import contribution
        _cq = a.get("cube_query") or {}
        _olcu = (_cq.get("measures") or [None])[0]
        out = contribution._akran_kiyasi(service, _cq, cube_meta or {}, _olcu)
        if out is None:
            raise ValueError("akran kıyası yapılamadı — ayrıştırılabilir bir ölçü yok")
        return out

    def _anlat(a: dict) -> str:
        from app import interpret as _yorum
        from app import narration_guard
        # ⚠ `FAZ 3` — `kaynaklar` bir **liste**dir; her öğe bir adımın çıktısı. Yalnız
        # **satır** üretenler anlatılır: bir `varlik`ı ya da `olcum`u tabloya çevirmek,
        # `interpret`e olmayan bir sonuç kümesi uydurmak olurdu.
        _satirlar: list[dict] = []
        for _c in (a.get("kaynaklar") or []):
            if isinstance(_c, list):
                _satirlar.extend(x for x in _c if isinstance(x, dict))
        _sonuc = ({"rows": _satirlar, "columns": list(_satirlar[0])}
                  if _satirlar else None)
        _ozet = ""
        try:
            # ⚠ `interpret` → `{facts:[...], summary:"Türkçe"} | None`. **Özet** alınıyor,
            # olgular değil: olgular yapısal kayıtlardır, `summary` zaten cümledir.
            _ozet = ((_yorum.interpret(_sonuc) or {}) or {}).get("summary") or ""
        except Exception:
            _log.info("interpret özet üretemedi — anlatı boş kalır", exc_info=True)
        if not _ozet:
            return ""
        # 🔴 `temiz_metin` — `Rapor`un yayımlanabilir alanı. Guard doğrulanamayan **cümleyi**
        # düşürür, metnin tamamını değil; yani en kötü durum *«süssüz ama doğru»*.
        return narration_guard.dogrula(_ozet, _sonuc).temiz_metin

    # ── `FAZ 7` · KÖK-NEDEN İNİŞİ ────────────────────────────────────────────────
    # Üçü de `drill.py`/`contribution.py`'de **zaten var**, testli ve deterministik.
    # `drill.py`'nin kendi belgesi bu anı öngörmüştü: *«İleride bir agent'ın AYNI
    # mekanizmayı otomatik gezebilmesi hedeflenir.»*
    def _kir(a: dict) -> dict:
        from app.drill import expand_cube_query
        return expand_cube_query(a.get("cube_query") or {}, a["boyut"])

    def _suz(a: dict) -> dict:
        from app.drill import select_cube_query
        _d = a.get("deger")
        # ⚠ `BAGLA`'nın çıktısı `(varlık, değer)`; bir plan *«en kötüyü bul, ona süz»*
        # derse `deger` oraya işaret eder. Aynı dönüşüm `HESAPLA`'da da var ve **tek
        # sahibi burası**: `ilkeller` birbirini tanımaz.
        if isinstance(_d, tuple):
            _d = _d[0]
        return select_cube_query(a.get("cube_query") or {}, a["boyut"], str(_d))

    def _boyutsec(a: dict) -> dict:
        from app.contribution import rank_dimensions
        _k = a.get("kaynak") or {}
        _rap = _k.get("raporlar") if isinstance(_k, dict) else None
        return {"siralama": rank_dimensions(list(_rap or []))}

    def _gorsel(a: dict) -> dict:
        """`GORSEL` — grafik kararı **deterministik** (ADR-0024), modele sorulmuyor.

        ⚠ `viz.recommend` semantik metadata'yı `cube_meta` olarak DEĞİL, açılmış hâliyle
        ister (`units`/`lower_set`/…). `FAZ 0`'ın ölçtüğü kusur tam buydu; `meta_args`
        o açmayı yapan tek yer."""
        from app import viz
        _k = a.get("kaynak")
        _satirlar = [r for r in (_k or []) if isinstance(r, dict)] if isinstance(_k, list) else []
        _sonuc = {"rows": _satirlar, "columns": list(_satirlar[0]) if _satirlar else []}
        return viz.recommend(_sonuc, cube_query=a.get("cube_query") or {},
                             **viz.meta_args(cube_meta or {})) or {}

    return {"TREND": _trend, "AYRISTIR": _ayristir, "KIYASLA": _kiyasla, "ANLAT": _anlat,
            "KIR": _kir, "SUZ": _suz, "BOYUTSEC": _boyutsec, "GORSEL": _gorsel}


def bolumlere_cevir(out: dict, plan: dict, *, schema: dict,
                    soru: str = "") -> tuple[list[dict], dict | None]:
    """`calistir` çıktısı → **(bölümler, son sonuç)**. Sunumun **tek sahibi** ㊲.

    ⊙ **Neden çıkarıldı (ölçüldü, insan testi 2026-08-13):** `§7②` makro ucu
    `calistir`'ı çağırıyor ve dönen şeyi olduğu gibi veriyordu — yani `ciktilar`,
    `katmanlar`, `makbuz`… Bir **koşucu iç sözleşmesi**, bir cevap değil. Arayüz onu
    normal kart yolundan geçirince kart **gövdesiz** çizildi 🆘.

    ⚠ Ve `cevap()` çağrılamazdı: o **boşluk doldurma** yoludur ve kendi ön koşulları
    vardır (bayrak · *«route zaten cevapladı → boşluk YOK»* · azınlık okuması). Makro bir
    boşluk değil bir **istektir**. Geriye tek doğru seçenek kaldı: bu bloğu **ikinci kez
    yazmak değil, çıkarmak**.

    ## İki kural burada yaşıyor — ikisi de ölçümle konmuştu

    **1 · Bölümler FİİLE göre değil ÇIKTI TİPİNE göre toplanır.** İlk hâl yalnız
    `SORGU`'yu topluyordu; tek `TREND` adımlı bir plan satır **üretip** boş cevap
    veriyordu. `CIKTI_TIPI` zaten hangi fiilin `satirlar` ürettiğini söylüyor.

    **2 · Fiş, ürettiği sayıyla aynı şeyi söylemeli.** `SORGU` dışı fiiller sorgularını
    kendileri koşar; adımın `period_expr`'i **çözülmeden** saklanırsa kart *«2026»* der,
    sayılar *«2025»* olur. `_fisi_coz` **çağrılır**, ikinci bir çözücü yazılmaz.
    """
    from app.plan_semasi import CIKTI_TIPI

    sorgular = out.get("sorgular") or []
    bolumler: list[dict] = []
    sorgu_sirasi = 0
    for adim, cikti in zip(plan.get("adimlar") or [], out.get("ciktilar") or []):
        if CIKTI_TIPI.get(adim.get("fiil")) != "satirlar":
            continue
        if adim.get("fiil") == "SORGU":
            cq = sorgular[sorgu_sirasi] if sorgu_sirasi < len(sorgular) else None
            sorgu_sirasi += 1
        else:
            cq = adim.get("cube_query") if isinstance(adim.get("cube_query"), dict) else None
            cq = _fisi_coz(cq, schema=schema, soru=soru)
        satirlar = ([r for r in (cikti or []) if isinstance(r, dict)]
                    if isinstance(cikti, list) else [])
        bolumler.append({"cube_query": cq,
                         "result": {"columns": list(satirlar[0]) if satirlar else [],
                                    "rows": satirlar, "row_count": len(satirlar)}})
    return bolumler, (bolumler[-1]["result"] if bolumler else None)


def kosum_cube_meta(schema: dict) -> dict:
    """`calistir(cube_meta=…)`'nın gövdesi — **tek sahip** ㊲.

    ⊙ Bu birleşim (`lower_is_better`) iki yerden isteniyor: orkestratörün kendi yolundan
    (`cevap`) ve `§7②`'nin **LLM'siz** makro ucundan. İkisi ayrı ayrı yazsaydı bir gün
    biri yeni bir kaynağı okumaya başlar, öteki okumazdı — ve *«hangi ölçüde küçük iyidir»*
    sorusunun iki cevabı olurdu. Bir küpün yönü, cevabın **işaretini** belirler.
    """
    lower: set[str] = set()
    for c in (schema.get("cubes") or []):
        lower |= set(c.get("lower_is_better") or [])
    return {"lower_is_better": sorted(lower)}


def calistir(plan: dict, *, service: Any, index: dict, cube_meta: dict | None = None,
             schema: dict | None = None, limit: int | None = None,
             azami_sorgu: int | None = None, soru: str = "") -> dict:
    """Planı motora bağlayıp koşar.

    Döner: `plan_kosucu.kos`'un sözleşmesi **+ `sonuclar`** — her `SORGU` adımının TAM
    motor çıktısı (`columns`/`rows`). ⚠ Çalıştırıcı yalnız satırlarla ilgilenir (ilkeller
    satır bekler); sunum katmanı kolonları da ister. İkisini tek dönüşe sıkıştırmak,
    çalıştırıcıya sunumu öğretmek olurdu.

    ⚠ `soru` **dönem çözümü için** gerekir ve varsayılanı boştur: `period_expr` yoksa
    hiç okunmaz. Zorunlu yapmak, tek çağıranı olan bir alanı üç teste taşımak olurdu.
    """
    from app import plan_onarim
    from app.cube_router import parse_cube_query

    sonuclar: list[dict] = []
    #: 🔴 Onarım **beyanları** — sessiz düzeltme yoktur (gerekçe `plan_onarim`'in
    #: başlığında). Buradan ize (`trace`) çıkar; kullanıcı kendisinin yazmadığı bir
    #: varsayımla üretilmiş bir sayıyı, varsayımı görmeden okumaz.
    onarimlar: list[str] = []
    #: 🔴 **ÇÖZÜLMÜŞ** sorgular. Adımdaki `cube_query` bir **referans** olabilir (`"$4"` —
    #: `KIR`/`SUZ`'ün ürettiği sorguyu koşan adım tam olarak öyle yazılır) ve o referansı
    #: cevaba koymak, kartı `/cube` ile yeniden koşulamaz yapardı. Üstelik `AskResponse.
    #: cube_query` bir **sözlük** bekler: canlıda Pydantic `input_value='$4'` diye düştü.
    #: *Bir alanın tipi genişlediğinde, onu okuyan her yer de genişlemelidir.*
    sorgular: list[dict] = []

    def _neden_dustu(cq: dict) -> str:
        """🔴 **TEK SAHİP** — metin `plan_onarim.gerekce`'de.

        ⟳ `O-18` — bu fonksiyon bir zamanlar teşhisin **kendisiydi** ve `dogrula()`
        aynı reddi başka kelimelerle veriyordu. İki kopya, modele bir cümle kullanıcıya
        başka bir cümle söylemekti (`KAT-1`). *Aynı reddin iki metni varsa, biri er geç
        ötekinden farklı bir şey öğretir.*
        """
        _c = (cq or {}).get("cube")
        _spec = index.get(_c) if _c else None
        if not _spec:
            # ⚠ Son çare: teşhis edilemeyen bir sorgu **loglanır**. Bir kör nokta ancak
            # görülebiliyorsa kapatılır; *"geçmedi"* diye susmak onu saklamaktır.
            _log.info("plan: teşhis edilemeyen sorgu: %s",
                      json.dumps(cq, ensure_ascii=False)[:500])
        return plan_onarim.gerekce(cq, _spec, {"cubes": list(index.values())})

    def _sorgu_kos(cq: dict) -> list[dict]:
        # 🔴 `O-15/R` — ONARIM DOĞRULAMADAN ÖNCE. Tek anlamlı bir alan kayması bir
        # belirsizlik değildir; onu beyaz listeye çarptırmak, bilinen bir cevabı bir
        # düzeltme turuyla ikinci kez satın almaktır. Gerekçe `app/plan_onarim.py`'de.
        _spec = (index.get((cq or {}).get("cube")) or {}) if isinstance(cq, dict) else {}
        cq, _beyan = plan_onarim.onar(cq, _spec)
        onarimlar.extend(_beyan)
        temiz = parse_cube_query(json.dumps(cq, ensure_ascii=False), index)
        if temiz is None:
            raise plan_kosucu.PlanHatasi(_neden_dustu(cq))
        # 🔴🔴 `O-15/D` — **DÖNEM ARTIK DÜŞMÜYOR.** Ölçüldü (canlı `K1`/`K2`):
        # *«toplam fire»* ve *«**2023 yılındaki** toplam fire»* **aynı** sayıyı
        # veriyordu (`1703818.39…`) — yani plan yolu dönemi sessizce yutuyordu.
        #
        # Mekanizma: istem modele dönemi `period_expr`'e yazdırıyor (doğru), beyaz liste
        # alanı **koruyor** (doğru), ama `cube_sql` onu **tanımıyor** — o bir niyet
        # taşıyıcısı, bir sorgu alanı değil. `ask()`in garson dalı bunu çözüyordu; bu
        # dal için **hiç kimse** çözmüyordu.
        #
        # ⚠ İkinci bir çözücü YAZILMADI, aynısı ÇAĞRILDI: aynı ifadenin iki farklı
        # tarihe çözülmesi, bir kusurdan beter bir tutarsızlıktır. Ve `§X1` gereği
        # küpün **kendi** zaman boyutu geçilir — sabit `"tarih"` `enerji_makine` gibi
        # küplerde var olmayan bir kolona filtre yazardı.
        #
        # *Bir alanı taşımak, onu çözecek kişiyi de taşımaz — ve çözülmeyen bir niyet
        # taşıyıcısı, sessizce silinmiş bir kullanıcı isteğidir.*
        if temiz.get("period_expr"):
            from app.cube_router import _norm
            from app.routers.ask import _resolve_period
            _td = (_spec.get("time_dimensions") or ["tarih"])[0]
            temiz, _ = _resolve_period(None, temiz, temiz.pop("period_expr"),
                                       _norm(soru or ""), _td)
        sql = service.cube_sql(temiz)
        service.dry_plan(sql)
        res = service.query(sql, limit=limit)
        sonuclar.append(res)
        sorgular.append(temiz)
        return res.get("rows") or []

    # 🔴 `paralel=True` — ve bu bir tercih değil bir **ölçüm sonucudur**
    # (`lab/olcumler/motor_eszamanlilik.md`): aynı `WrenService` üzerinde 32 eş zamanlı
    # sorguda **0 hata · 0 sapma**, hızlanma 2,52×. ⚠ Yalnız aynı DAG katmanındaki
    # `SORGU`lar, tavan 4, çıktılar adım sırasına yazılır.
    out = plan_kosucu.kos(plan, sorgu_kos=_sorgu_kos,
                          govdeler=_govdeler(service, schema or {}, cube_meta),
                          cube_meta=cube_meta, paralel=True,
                          **({"azami_sorgu": azami_sorgu} if azami_sorgu else {}))
    out["sonuclar"] = sonuclar
    out["sorgular"] = sorgular
    out["onarimlar"] = onarimlar
    return out


def cevap(request: Any, *, service: Any, schema: dict, soru: str, settings: Any = None,
          principal: Any = None, limit: int | None = None,
          route_hit: dict | None = None, onceki_rapor: Any = None,
          koru: bool = True, onaylandi: bool = False) -> dict | None:
    """🔴 **BOŞLUĞUN TEK KAPISI** — `ask()` bundan başka bir şey bilmez.

    `None` döner ve **hiçbir şey yapmaz** eğer: bayrak kapalıysa, sağlayıcı plan
    kuramıyorsa, ya da kullanılabilir bir plan çıkmadıysa.

    🔴 **Buraya YALNIZ boşlukta gelinir** ve LLM çağrısı **burada** yapılır — yani
    cevaplanan hiçbir soruya bir çağrı eklenmez. Ölçüm bu yerleşimi zorunlu kıldı:
    `select_cube`'un yerine geçtiğinde arıza oranı %55 → %65'e **çıkmıştı**.

    ⚠ `index` ve `cube_meta` **burada** türetilir, çağırandan alınmaz: `ask()`in o
    noktasında ikisi de garantili değil ve *"belki tanımlıdır"* diye bir değişken okumak,
    bir `NameError`'ı bir üretim kusuruna çevirmenin en kısa yoludur.

    Döner: `{source, note, iz, result?, cube_query?}` — `ask()` bunu doğrudan bir
    `AskResponse`'a çevirir, karar vermez.
    """
    # `§RG`/`§RB` — belge isteği **tek kez** hesaplanır ve iki kararı birden besler:
    # (1) orkestratör susmasın, (2) plan belgeyle bitmezse belge yine de kurulsun.
    # ⚠ Kapsam bilinçli **fonksiyon düzeyi**: ilk yazımda `route_hit` dalının içindeydi ve
    # derleme noktasında **tanımsızdı** — yani `§RB` `route_hit` yokken hiç koşamazdı.
    # *Bir yüklemi kullanacağı yerden dar bir kapsamda hesaplamak, onu orada yok saymaktır.*
    from app.plan_semasi import belge_istegi as _belge_yuklemi
    _belge_istegi = _belge_yuklemi(soru or "")
    from app import plan_garson

    # ⚠ **SESSİZ DAL KALMASIN (`ADR-0020`).** Bu fonksiyon `None` döndüğünde neden
    # döndüğü hiçbir yerde yazmıyordu; canlıda *"tüketici hiç konuşmadı"* diye bir kör
    # nokta üretti. *Bir dalın sessizce kapanması, o dalın var olmadığı anlamına gelmez —
    # yalnız görünmediği anlamına gelir.*
    # 🔴 Sağlayıcı **uygulamanın durumundan** okunur, çağıranın yerelinden değil. Ölçüldü
    # (`EE19`, canlı): `llm_probe` yalnız garson dalında bağlanıyor; deterministik yoldan
    # gelindiğinde `UnboundLocalError` — ve bu bayrak KAPALIYKEN de patlıyordu, çünkü
    # argüman çağrıdan **önce** değerlendirilir. ⚠ `ruff F821` bunu göremez: ad bir yerde
    # atanmış, yalnız **o yoldan gelinince** atanmamış oluyor. *Koşullu bağlanan bir ad,
    # tanımsız bir addan daha sinsidir: statik olarak var, çalışırken yok.*
    # 🔴🔴 **`O-17` — BU MODÜL KENDİ ÖN KOŞULUNU ARTIK KENDİSİ UYGULUYOR.**
    #
    # Yukarıdaki docstring *"Buraya YALNIZ boşlukta gelinir"* diyor ve çağrı yerindeki
    # yorum da öyle diyordu — ama **hiçbiri bunu ZORLAMIYORDU**. Çağrı `if route_hit:`
    # dalının **üstünde** ve koşulsuzdu; yani route bir cevap bulduğunda bile bu modül
    # önce koşuyor, bir plan üretiyor ve **route'un cevabını hiç konuşturmadan** dönüyordu.
    #
    # ⊙ Ölçüldü (canlı `IV` turu, kullanıcının işaret ettiği dört soru):
    #
    #   | soru | `route()` tek başına | HTTP yolu |
    #   |---|---|---|
    #   | *«makine bazında ortalama oee»* | ✅ `oee/ort_oee/makine` | `cube+llm` — LLM çağrıldı |
    #   | *«bu yıl toplam ciro»* | ✅ `parti/toplam_ciro` | `cube+llm` |
    #   | *«en yüksek cirolu 5 müşteri»* | ✅ `order DESC · limit 5` | 🔴 **CEVAPSIZ** — garson `satis` küpü uydurdu |
    #   | *«aylara göre fire»* | ✅ `parti/toplam_fire_kg` | `cube+llm` |
    #
    # 🔴 Üçüncü satır kusurun bedelini tek başına ölçüyor: **route'un doğru bildiği bir
    # soru cevapsız kaldı.** Öteki üçü sessizce bir LLM çağrısı ve yanlış bir rozet
    # (`cube+llm` yerine `cube`) ödedi.
    #
    # ⚠ Ve çağrı yerindeki iki yorum **birbiriyle çelişiyordu**: biri *"buraya
    # `route_hit=None` ile gelinir"*, öteki *"bu kancaya YUKARIDAKİ HER yoldan gelinir"*.
    # İkincisi doğruydu; kod onu izliyordu, belge birincisini.
    #
    # 🔴 Ön koşul **sahibinin yanına** kondu, çağrı yerine değil: bir değişmezi her
    # çağıranın hatırlamasına bırakmak, onu bir gün unutulacak bir âdete çevirir.
    # *Bir modül kendi ön koşulunu uygulamıyorsa, o bir ön koşul değil bir dilektir.*
    if route_hit is not None:
        # 🔴🔴 `O-21` — **AMA «route cevapladı» İLE «garsonun azınlık okuması» AYNI ŞEY
        # DEĞİLDİR.** `O-17` ön koşulu doğruydu ve fazla genişti: `route_hit` iki farklı
        # yerden gelebiliyor ve ikisi aynı ağırlıkta değil.
        #
        # ⊙ Ölçüldü (canlı `VI`): bir örnek *«1 adım»*, ötekiler *«3 adım
        # (SORGU·SORGU·MATRIS)»* dedi. Çok adımlılar `"{}"` döndürüp **çekimser**
        # sayıldığı için tek adımlı okuma oy kazandı, `route_hit` oldu ve bu ön koşul
        # **geçerli bir planı susturdu**. Cevap: `iki_cube` reddi.
        #
        # 🔴 Ayrım: `route_hit` **garsonun kendi tek-fiş okumasıysa** ve garsonun
        # örneklerinin **çoğunluğu** *"orkestre gerekli"* dediyse, o okuma bir cevap
        # değil bir **azınlıktır** — plan konuşur. `route()`'un deterministik cevabı
        # (ya da garsonun çoğunlukla desteklenen tek-fişi) **her zaman** kazanır.
        #
        # ⚠ Karşılaştırma `plan_tek_cq` ile **birebir**: başka bir yoldan gelen bir
        # `route_hit`'e dokunmaz. *Bir ön koşulu gevşetirken, gevşemenin sınırını da
        # yazmak gerekir; yoksa gevşeme bir delik olur.*
        _st = getattr(request, "state", None)
        _sekil = getattr(_st, "plan_sekil", None) or {}
        _tek_cq = getattr(_st, "plan_tek_cq", None)
        _azinlik = (_sekil.get("cok", 0) > _sekil.get("tek", 0)
                    and _tek_cq is not None
                    and route_hit.get("cube_query") == _tek_cq)
        # 🔴🔴 `§RG` — **BİR BELGE, TEK FİŞLE KARŞILANAMAZ.**
        #
        # ⊙ Ölçüldü (5 koşum): *«son 2 yıl satış raporu hazırla»* → 4 koşumda belge, **1
        # koşumda hiç plan yok** — route/garson tek fişle cevapladı ve bu blok sustu.
        # Kullanıcı bir **belge** istedi, bir **tablo** aldı; hangisini alacağı modelin o
        # anki tercihine kalmıştı.
        #
        # 🔴 Oysa bir rapor **tanımı gereği** çok bölümlüdür: tek bir sorgu onu
        # karşılayamaz. Merdivenin kendi kuralı bunu zaten söylüyor — *«tek fişte
        # olmuyorsa orkestre eder»* (`§0.0`).
        #
        # ⚠ Yüklem bir sözlük değil **yetenek listesidir**: `plan_semasi.BELGE_FIILLERI`
        # bu dosyanın kendi fiilleridir (`FIILLER` kadar kapalı). `simge.sahipler`'in
        # katalog kimliklerine, `§KD`'nin boyut adlarına bakması gibi.
        # ⚠ Ve route'un cevabı **iptal edilmez**: plan koşamazsa aşağıdaki dallar yine
        # ona döner (`KURAL B`).
        if not _azinlik and _belge_istegi:
            _log.info("orkestratör: BELGE istendi (%s) → tek fiş yetmez (§RG)", _belge_istegi)
            _azinlik = True
        if not _azinlik:
            _log.info("orkestratör: route zaten cevapladı → boşluk YOK, hiç konuşmuyorum")
            return None
        _log.info("orkestratör: tek-fiş okuması AZINLIKTA (tek=%d · çok=%d) → plan "
                  "konuşuyor (`O-21`)", _sekil.get("tek", 0), _sekil.get("cok", 0))
    llm = getattr(getattr(getattr(request, "app", None), "state", None), "llm", None)
    _hazir = getattr(getattr(request, "state", None), "plan_taslagi", None)
    if not soru or llm is None:
        _log.info("orkestratör: soru/sağlayıcı yok (soru=%s llm=%s)",
                  bool(soru), llm is not None)
        return None
    if not plan_garson.acik_mi(settings, principal, llm):
        _log.info("orkestratör: bayrak kapalı ya da sağlayıcı plan kuramıyor")
        return None
    _log.info("orkestratör: DEVREDE (hazır plan=%s)", bool(_hazir))
    try:
        from app.katalog_metni import metin_ve_indeks
        catalog, index = metin_ve_indeks(schema, principal)
    except Exception:
        _log.warning("katalog kurulamadı → boşluk kapanmadı", exc_info=True)
        return None
    # 🔴 `O-14` — garson zaten bir plan ürettiyse **ikinci kez sorma**. `request.state`
    # okunuyor çünkü bu kancaya yukarıdaki HER yoldan gelinir ve çağıranın yereli
    # garantili değil (`EE19`'un `UnboundLocalError` dersi).
    # ⚠ `_hazir` fonksiyon başında da okundu (log satırı için) ama **karar burada
    # verilir**: arada `metin_ve_indeks` koşuyor ve o sırada geç bir oy planı saklamış
    # olabilir. Ölçüldü (`III7`): saklama tüketici başladıktan **2 sn sonra** oldu.
    # 🔴 `O-22` — bu yol da bağlamı görmeli. Ölçüldü: yalnız `PlanGarsonu` bağlandığında
    # canlıda **hiçbir şey değişmedi**, çünkü o turda planı **burası** üretiyordu.
    _onceki = getattr(getattr(request, "state", None), "plan_onceki", None)
    # 🔴 `§RD` — kullanıcı bir **belgeyi** düzenliyorsa bağlam tek fiş değil **bölüm
    # listesidir**. Kaynak: bir önceki turun `rapor`u (istemci `previous_rapor` ile geri
    # yollar) ya da istek durumunda saklanmış hâli. ⚠ Yalnız **kimlikler** gider —
    # satırlar değil (`G0b`).
    _onceki_bolumler = _belge_bolumleri(onceki_rapor)
    plan = (getattr(getattr(request, "state", None), "plan_taslagi", None)
            or plan_garson.plan_uret(llm, plan_garson.baglamli(soru, _onceki,
                                                               _onceki_bolumler),
                                     catalog, index))
    # 🔴 `O-15/Y` — **GEÇ GELEN PLAN ARTIK KAYBOLMUYOR.** Ölçüldü (canlı `II10`,
    # loglarla): garson `19:42:31`'de geçerli bir **4 adımlık** plan üretip sakladı
    # (`SORGU·BAGLA·SUZ·ANLAT`) — ama bu fonksiyon hazır planı `19:42:23`'te, yani
    # **sekiz saniye önce** yoklamıştı. Kendi üretimi düştü, saklanan plan hiç
    # okunmadı, ve soru **Discovery'ye** indi (iki `Binder Error` ile).
    #
    # Sebep bir yarıştır: oylama görevlerinin bütçesi (20 sn) aştı (`Intent oyu
    # BÜTÇEYİ AŞTI` × 3), `ask()` yoluna devam etti, ama görevler **koşmayı sürdürdü**
    # ve sonuçlarını geç yazdı. Bir zaman aşımı görevi **iptal etmez**.
    #
    # ⚠ Çözüm bütçeyi büyütmek değil (gecikme bir kullanıcı maliyetidir), **kullanım
    # anında yeniden okumaktır**: geç gelmiş bir plan hâlâ bir plandır ve onu atmak,
    # bedeli ödenmiş bir işi çöpe atmaktır.
    # *Bir değeri başlangıçta okuyup sonda kullanmak, aradaki her şeyi görmezden
    # gelmeye söz vermektir.*
    if not plan:
        plan = getattr(getattr(request, "state", None), "plan_taslagi", None)
        if plan:
            _log.info("orkestratör: plan GEÇ geldi (yarış) → kurtarıldı, %d adım",
                      len(plan.get("adimlar") or []))
    if not plan:
        # 🔴🔴 `§RD-4` — **BELGE DÜZENLENİRKEN DISCOVERY'YE DÜŞÜLMEZ.**
        #
        # ⊙ Ölçüldü (curl `T` turu, T28): ekranda **6 bloklu** bir pano varken
        # *«panodan kalite bölümünü çıkar»* → `source=llm:openrouter`, **ham SQL**,
        # ve pano **yok oldu** (`rapor=None`). Kullanıcı bir belgeyi düzenliyordu;
        # sistem yerine bir SQL yazdı.
        #
        # 🔴 Doktrinin kendi cümlesi: *Discovery'nin her ateşlenmesi bir mutfak
        # eksikliği raporudur* — ama burada mutfak zaten doluydu: belge **elimizdeydi**.
        # Bir düzenleme isteği karşılanamıyorsa doğru cevap belgeyi **korumak** ve
        # anlamadığımızı **söylemektir**; belgeyi yok edip yerine alakasız bir tablo
        # koymak değil.
        #
        # *Elindeki belgeyi kaybederek verilen bir cevap, cevap değil bir zarardır.*
        # 🔴 `§RD-5` — **KORUMA, MERDİVENİN SONUNDA BİR CEVAPTIR; ORTASINDA BİR SET.**
        #
        # `koru=False` ile çağrıldığında (takip dalının **erken** denemesi) bu dal
        # `None` döner ve zincir bugünkü gibi sürer. Sebep ölçüldü: erken denemede
        # `_belgeyi_koru` dönmek, ekranda belge varken sorulan **her** meşru fiş
        # sorusunu (*«en yükseği hangisi»*) *«belge korundu»* diye cevaplardı — yani
        # bir kusuru kapatırken sohbeti kilitlerdi.
        # *Bir korumanın doğru yeri, korunacak şeyden başka seçenek kalmadığı yerdir.*
        if _onceki_bolumler and koru:
            return _belgeyi_koru(_onceki_bolumler, schema, soru)
        _log.info("orkestratör: kullanılabilir plan yok → merdiven bugünkü gibi")
        return None
    _n = len(plan["adimlar"])
    # ══════════════════════════════════════════════════════════════════════════════
    # 🔴🔴 `§66` — **ÇOK ADIMLI PLAN, KOŞMADAN ÖNCE KULLANICIYA SORULUR** (`§28.3`).
    # ══════════════════════════════════════════════════════════════════════════════
    #
    # Belgenin **başlığı** işin kendisi: *«route ve garson, KARAR VERİCİ olmaktan çıkıp
    # TAHMİNCİ oluyor … **kullanıcı KARARI VERİR (bir tık)**»* (`§3.1`). `§63` bunu
    # **makro** yolunda kurmuştu; ama asıl merdiven buradan geçiyor ve burada plan hâlâ
    # **koşuyordu** — yani rol değişikliği yarım kalmıştı 🆘.
    #
    # `§28.3` karar tablosu (birebir): **tek adım + emin → 🟢 koşar** · **çok adım
    # (N ≥ 2) → 🔴 her zaman önizleme**. Gerekçesi ölçülmüş: *«7. adımda çökerse
    # kullanıcı SONDA öğreniyor — onarım tutma %25, payda 16»* + bütçe.
    #
    # ⚠ **`KURAL B`:** öngörü katmanı kapalı bir kiracıda bu dal **hiç** çalışmaz ve
    # merdiven bayt bayt bugünküdür. Bayrağın **tek sahibi** `features` ㊲.
    # ⚠ Plan **cevaba iliştirilir**: onay `POST /plan/kos`'a *aynı planı* geri yollar —
    # yani kullanıcı **onayladığı planı** koşar, yeniden üretilmiş bir benzerini değil.
    # İkinci bir garson turu hem `E-8`'i çiğner hem de onaydan **farklı** bir plan
    # üretebilirdi. *Onaylanan şey ile koşan şey aynı değilse, onay bir tören olur.*
    if _n >= 2 and not onaylandi and _features.oneri_katmani_acik(principal):
        try:
            plan_kosucu.dogrula(plan)
            _gecerli, _not = True, f"{_n} adım — koşmadan önce gözden geçir."
        except plan_kosucu.PlanHatasi as e:
            # ⊘ Dürüst ret: geçersiz plan da **gösterilir**, gerekçesiyle (`§7`).
            _gecerli, _not = False, str(e)
        _log.info("orkestratör: %d adımlık plan ÖNİZLENİYOR (onay bekliyor) — §28.3", _n)
        return {"source": "onizleme", "note": _not, "gecerli": _gecerli, "plan_taslagi": plan,
                "adimlar": [{"sira": i, "fiil": x.get("fiil"), "metin": onizleme_satiri(x)}
                            for i, x in enumerate(plan["adimlar"], 1)],
                "iz": [f"orkestratör: {_n} adımlık plan önizlendi (§28.3 — onay bekliyor)"]}
    try:
        out = calistir(plan, service=service, index=index, schema=schema,
                       cube_meta=kosum_cube_meta(schema), limit=limit,
                       soru=soru)
    except plan_kosucu.PlanHatasi as e:
        _log.info("plan KOŞAMADI (%d adım) → adım adım dürüst ret: %s", _n, e)
        return {"source": None, "note": neden_olmadi(plan, e),
                "iz": [f"orkestratör: {_n} adımlık plan koşulamadı → adım adım ret"]}
    except Exception:
        # ⚠ Beklenmeyen bir arıza bu dalı **sessizce** kapatır: merdiven bugünkü gibi
        # devam eder (Discovery / dürüst ret). Bir genişleme, genişlettiği şeyi bozamaz.
        _log.warning("plan tüketicisi düştü → bugünkü yol", exc_info=True)
        return None
    # 🔴 `FAZ 5` — **HESAPLANAN MALZEME ARTIK ATILMIYOR.** Bugüne kadar `sonuclar`'ın
    # hepsi hesaplanıp yalnız **sonuncusu** dönüyordu; çok bölümlü rapor/pano için gereken
    # ara sonuçlar üretilip çöpe gidiyordu. *Bir maliyeti ödeyip ürününü atmak, onu hiç
    # ödememekten pahalıdır: hem para gider hem cevap.*
    # 🔴🔴 **BÖLÜMLER FİİLE GÖRE DEĞİL, ÇIKTI TİPİNE GÖRE TOPLANIR.**
    #
    # İlk hâl yalnız `SORGU` adımlarını topluyordu. Ölçüldü (canlı `FF8` — *«geçen yılın
    # aynı dönemine göre ciro nasıl değişti»*): plan tek bir `TREND` adımından ibaretti,
    # `yoy.compute` satırları **üretti**, ama `sonuclar` boş kaldı → cevap `source=cube+llm`
    # rozetiyle **0 satır** döndü ve hiçbir şey söylemedi.
    #
    # ⊙ Düzeltme fiile özel değil **sınıfsal**: `CIKTI_TIPI` zaten hangi fiilin `satirlar`
    # ürettiğini söylüyor. Yarın sekizinci bir satır-üreten fiil eklenirse burası
    # kendiliğinden doğru çalışır. *Bir kusuru fiilin adıyla düzeltmek, aynı kusuru
    # sıradaki fiilde yeniden yazmaya söz vermektir.*
    # ⟳ Bu blok **`bolumlere_cevir`'e taşındı** ㊲ — aynı sunum `§7②` makro ucundan da
    # isteniyor ve ikinci kez yazılsaydı bir gün ikisi ayrışırdı. Aşağıdaki uzun
    # gerekçeler (çıktı tipi · fiş çözümü) o işlevin başlığında **korunuyor**; buraya
    # kopyalanmadı, çünkü bir gerekçenin de tek bir yeri olmalı.
    _bolumler, _son = bolumlere_cevir(out, plan, schema=schema, soru=soru)
    # `§RP` — belge fiili varsa bölümleri `Report` biçimine diz (tek sahip: `report.py`).
    _belge_fiili = next((str(a.get("fiil")) for a in (plan.get("adimlar") or [])
                         if str(a.get("fiil")) in ("RAPOR", "PANO")), None)
    # 🔴🔴 `§RB` — **PLANIN BELGEYLE BİTMESİ BİR UMUT OLAMAZ.**
    #
    # ⊙ Ölçüldü (curl, 2026-08-10): *«geçen yıla göre satış raporu hazırla»* iki varyant
    # üretti — `SORGU→TREND→RAPOR` (plan doğru, koşamadı) ve `SORGU→TREND→**ANLAT**`
    # (koştu ama belge fiili YOK → `rapor=None`). Kullanıcı bir **belge** istedi; garson
    # son adımda `ANLAT` seçti ve belge **kayboldu**.
    #
    # 🔴 `§RG` orkestratörün **koşmasını** zorluyor; planın **belgeyle bitmesini**
    # zorlayan bir şey yoktu. Ama fiş bunu zaten **kanıtlıyor**: belge istendi ve ortada
    # **≥2 bölüm** var — bu bir belgedir, fiilin adı ne olursa olsun. `§RP`'nin
    # derleyicisi hazır; yeniden planlamaya, ikinci bir LLM turuna gerek yok.
    #
    # ⚠ Eşik **2**: tek bölüm bir belge değil bir cevaptır ve ona kapak takmak
    # kullanıcıya olmayan bir şeyi vaat etmek olurdu.
    #
    # *LLM'in seçimine bırakılmış bir şey, fişin zaten kanıtladığı bir şeyse, orada bir
    # karar değil bir kumar vardır.*
    # `§RZ` — belge istendi ama plan tek bölüm ürettiyse, eksik bölümleri **katalogdan**
    # türet ve koş. Gerekçe `plan_semasi.belge_ek_bolumleri`'nde; burada yalnız **çağrı**
    # var. ⚠ Temel bölüm **yeniden koşulmaz** (`bolumlerden_kur`'un aynı ilkesi): bir
    # sonucu iki kez hesaplamak, onu bir kez yanlış hesaplamanın en kolay yoludur.
    if (_belge_istegi and len(_bolumler) == 1
            and isinstance(_bolumler[0].get("cube_query"), dict)):
        _bolumler.extend(_ek_bolumler_kos(_bolumler[0]["cube_query"], service=service,
                                          schema=schema, limit=limit))

    # 🔴🔴 `§RD-3` — **BİR BELGENİN BÜTÜN BÖLÜMLERİ AYNI DÖNEMİ KONUŞUR.**
    #
    # ⊙ Ölçüldü (curl `T` turu, T24): elde *«son 2 yıl»* dönemli 3 bloklu bir rapor
    # varken *«rapora aylık ciro trendi de ekle»* → eklenen blok
    # `{"cube":"parti","measures":["toplam_ciro"]}` — **ne aylık, ne dönemli**. Yani
    # iki yıllık blokların yanında **tüm zamanların** bir sayısı duruyordu.
    #
    # 🔴 Ve bu bir grafik kusuru değil bir **doğruluk** kusurudur: aynı belgede iki
    # farklı evreni aynı başlık altında okumak, kıyaslanamaz iki sayıyı kıyaslanır
    # sanmaktır — ve hiçbir yerde yazmıyordu.
    #
    # ⚠ Sahiplik: **kendi dönemi olan bölüme dokunulmaz.** Kullanıcı *«bir de geçen ayı
    # ekle»* derse o bölümün dönemi onundur. Devralma yalnız **hiç dönemi olmayan**
    # bölüme uygulanır — yani bir seçim ezilmez, bir **boşluk** doldurulur.
    #
    # *Bir belgede dönemini söylemeyen bir bölüm, dönemi olmayan bir bölüm değildir —
    # dönemi bilinmeyen bir bölümdür.*
    # ⚠ Ve devralan bölüm **YENİDEN KOŞULUR.** İlk yazımda süzgeci koşulmuş bir bölümün
    # fişine basıyordum — yani sayının taşımadığı bir dönemi **iddia ediyordum**. Bu
    # deponun en pahalı kusur sınıfı tam olarak budur: fiş ile sayının ayrışması.
    # *Bir fişi sayıyı değiştirmeden düzeltmek, yalanı belgelemektir.*
    _devir_izi: list[str] = []
    if _belge_istegi and len(_bolumler) > 1:
        _bolumler = _donemi_devret(_bolumler, service=service, schema=schema, limit=limit,
                                   onceki=_onceki_bolumler, iz=_devir_izi)

    _rapor = None
    _derle = bool(_belge_fiili) or (bool(_belge_istegi) and len(_bolumler) >= 2)
    if _derle and _bolumler:
        from app import report as _report
        _baslik = next((str(a.get("baslik")) for a in (plan.get("adimlar") or [])
                        if _belge_fiili and str(a.get("fiil")) == _belge_fiili
                        and a.get("baslik")), None)
        # 🔴🔴 `§RD-ad` — **BİR BELGEYİ DÜZENLEMEK, ONA YENİ BİR AD VERMEK DEĞİLDİR.**
        #
        # ⊙ Ölçüldü (curl `EE` turu, EE-6): *«Son 2 Yıl Üretim Raporu»* (6 bölüm) →
        # *«rapora enerji tüketimini de ekle»* → bölümler korundu (7 oldu) ama başlık
        # **«Makine Bazlı Performans Raporu»** oluverdi. Planlayıcı her turda yeni bir
        # ad uyduruyor; kullanıcı ise **aynı belgeyi** düzenlediğini sanıyor.
        #
        # ⚠ Kural `§RD-3`'ün (dönem devri) kardeşidir ve aynı gerekçeye dayanır: bir
        # düzenleme turunda **söylenmemiş olan devralınır**. Dönem devralınıyordu, ad
        # devralınmıyordu — ve ad, bir belgenin kullanıcı için **kimliğidir**.
        #
        # ⚠ Bilinen sınır, yazılı: bu turda belge **yeniden adlandırılamaz**. Ad
        # değiştirmek ayrı bir istektir ve onu bir kelime listesiyle sezmek bu deponun
        # yasakladığı şeydir; geldiğinde kendi fiiliyle gelir.
        #
        # *Bir belgeyi her dokunuşta yeniden adlandırmak, onu her seferinde yeni bir
        # belge yapar — ve kullanıcı hangisini düzenlediğini bilemez.*
        _onceki_ad = (onceki_rapor or {}).get("title") if isinstance(onceki_rapor, dict) else None
        if _onceki_bolumler and _onceki_ad:
            _baslik = str(_onceki_ad)
        try:
            _rapor = _report.bolumlerden_kur(
                _bolumler, baslik=_baslik or soru or "Rapor", schema=schema)
        except Exception:                     # noqa: BLE001 — belge kurulamazsa tur DÜŞMEZ
            _log.warning("rapor derlenemedi (best-effort)", exc_info=True)
    # 🔴🔴 `§RT` — **TEK BÖLÜMLÜ BELGE SESSİZCE DÜŞÜYORDU — ve bu bir red bile değildi.**
    #
    # ⊙ Ölçüldü (curl `Q` turu, 2026-08-10): *«bakım maliyeti raporu hazırla»* → plan
    # **1 bölüm** üretti, `§RB`'nin eşiği (≥2) yüzünden belge kurulmadı ve kullanıcı
    # **tablo** aldı. Neden rapor olmadığı **hiç söylenmedi**.
    #
    # 🔴 Eşiğin gerekçesi doğru (*«tek bölüm bir belge değil bir cevaptır»*) ama sonucu
    # yanlıştı: **sessiz bir indirgeme**. Kullanıcının kuralı — *dürüst red bir başarı
    # değildir* — burada bir red **bile** yoktu.
    #
    # ⚠ Ve doğru cevap bir belge uydurmak değil: kullanıcı bir **canvas** istiyor
    # (*«kullanıcı ile mükemmelce tamamlanacak»*), yani eksik olanı **sormak** doğru
    # olanıdır. `§TZ` deseni: beyan + tek tık.
    #
    # *Bir indirgemeyi söylemeden yapmak, kullanıcıya istediğini verdiğini sanmasına izin
    # vermektir.*
    _belge_notu = None
    # 🔴 `§RÇ` — **DEĞİŞMEYEN BİR BELGE, DEĞİŞTİĞİNİ SÖYLEMEDEN GERİ VERİLEMEZ.**
    #
    # ⊙ Ölçüldü (curl `T` turu, T27/T29): 6 bloklu bir pano varken *«panodan bakım
    # bölümünü çıkar»* → **6 blok, birebir aynı**, ve **tek kelime** açıklama yok.
    # (O panoda `bakim` bloğu zaten yoktu — yani istek karşılanamazdı.) Kullanıcı
    # bölümün çıkarıldığını sanır ve bir daha bakmaz.
    #
    # ⚠ Kıyas **kimlikler** üzerinden: satır sayısı veri tazelenince değişebilir, bir
    # belgenin **bölüm listesi** değişmez. *Bir değişikliği satır sayısından ölçmek, veri
    # değiştiğinde değişiklik olduğunu sanmaktır.*
    # 🔴🔴 `§RS` — **«EKLE» DEMEK, HİÇBİR ŞEYİN GİTMEMESİ DEMEKTİR.**
    #
    # ⊙ Ölçüldü (curl `X` turu): düzenleme **tüm belgeyi yeniden planlıyor** ve sonuç
    # **tutarsız** — X9'da kusursuz (4 blok birebir korundu, 5.'si eklendi), X6/X7'de
    # **kayıplı** (bölümler kaydı). Kullanıcı *«rapora kârlılık ekle»* dediğinde
    # müşteri kırılımının kaybolmasını beklemez; kaybolduğunu **fark bile etmez**.
    #
    # ⚠ Kural **dar**: yalnız **ekleme niyeti** varken ve **çıkarma niyeti yokken**
    # koşar. İkisi de kataloğun değil dilbilgisinin kapalı sınıfları ve tek sahipleri
    # `cube_router`'da (`_ADD_RE` · `_RM_VERB_RE`) — ikinci bir liste `KAT-1` olurdu.
    # *«Yeniden yap»* gibi bir istek ne ekleme ne çıkarmadır; orada plan neyi getirdiyse
    # o kalır (bir yeniden yazımı geri almak, kullanıcının isteğini ezmek olurdu).
    #
    # ⚠ Ve kayıp bölüm **yeniden koşulur**: kimliğiyle geri koymak, sonucu olmayan bir
    # kart üretirdi (`§RE`'nin dersi — fiş ile sayı aynı şeyi söylemeli).
    #
    # *Bir düzenlemeyi «yeniden planlama» olarak yapmak, kullanıcının yazmadığı bir
    # silmeyi de o düzenlemeye eklemektir.*
    if _onceki_bolumler and _rapor is not None:
        from app.cube_router import _ADD_RE, _RM_VERB_RE, _norm as _n2

        _qn = _n2(soru or "")
        if _ADD_RE.search(_qn) and not _RM_VERB_RE.search(_qn):
            _bolumler, _geri = _kayip_bolumleri_geri_koy(
                _bolumler, _onceki_bolumler, service=service, schema=schema, limit=limit)
            if _geri:
                _rapor = _belgeyi_derle(_bolumler, _baslik_metni(plan, soru), schema)
                _devir_izi.append(f"§RS: «ekle» isteğinde kaybolan {_geri} bölüm "
                                  f"geri kondu ve yeniden koştu")

        def _kimlik(bs: list[dict]) -> set[tuple]:
            return {(str((b.get("cube_query") or {}).get("cube") or ""),
                     tuple((b.get("cube_query") or {}).get("measures") or []),
                     tuple((b.get("cube_query") or {}).get("dimensions") or []))
                    for b in (bs or []) if isinstance(b.get("cube_query"), dict)}
        if _kimlik(_bolumler) == _kimlik(_onceki_bolumler):
            _belge_notu = BELGE_DEGISMEDI
            _log.info("§RÇ: düzenleme belgeyi DEĞİŞTİRMEDİ (%d bölüm) → beyan",
                      len(_bolumler))
    if _belge_notu is None and _belge_istegi and _rapor is None and len(_bolumler) == 1:
        _belge_notu = ("⚠ **Tek bölümlük** bir sonuç çıktı — bir belge en az iki bölüm "
                       "ister. Rapora dönüştürmek için ne eklemek istersin? (ör. "
                       "*«müşteri kırılımı da ekle»* · *«geçen yıla göre kıyasla»* · "
                       "*«aylık trend ekle»*)")
    # 🔴 **BOŞ SONUÇ SESSİZ KALMAZ.** Merdivenin geri kalanı bunu zaten yapıyor
    # (*«Bu aralıkta kayıt bulunamadı — rapor doğru kuruldu»*); plan yolu yapmıyordu ve
    # `source=cube+llm` rozetiyle **0 satır** dönüyordu. *Boş bir cevabı açıklamadan
    # vermek, kullanıcının onu bir hata sanmasına izin vermektir.*
    _bos = bool(_bolumler) and all(b["result"]["row_count"] == 0 for b in _bolumler)
    # 🔴🔴 **BOŞ OLMAYAN AMA TÜMÜ `null` BİR SATIR DA BİR SESSİZLİKTİR.**
    #
    # ⊙ Ölçüldü (canlı `D2'`): *«2023 yılındaki toplam fire»* → **1 satır**,
    # `{"toplam_fire_kg": null}`, hiçbir not. `row_count == 1` olduğu için yukarıdaki
    # boşluk yüklemi susuyordu; kullanıcı boş bir hücre görüyor ve onu bir **arıza**
    # sanıyor — oysa cevap doğru: o dönemde veri yok (demo verisi 2024'te başlıyor).
    #
    # ⚠ Ve bu kusuru **kendi düzeltmem görünür kıldı**: dönem çözülmeden önce sorgu
    # tüm zamanların toplamını veriyordu (sessiz **yanlış**); dönem çözülünce doğru
    # ama **açıklamasız** bir boşluğa dönüştü. *Bir yolu açmak, o yolun üstündeki
    # çukuru da devralmaktır.*
    #
    # ⚠ Yüklem dar: **her** satırın **her** ölçü değeri `null` olmalı. Tek bir dolu
    # hücre varsa cevap doludur ve not yazılmaz (`§101.1` — yanlış pozitif üreten bir
    # uyarı, sustuğu durumdan pahalıdır).
    def _hepsi_bos(r: dict) -> bool:
        _rows = r.get("rows") or []
        return bool(_rows) and all(v is None for row in _rows for v in row.values())

    _null = (not _bos) and bool(_bolumler) and all(
        b["result"]["row_count"] == 0 or _hepsi_bos(b["result"]) for b in _bolumler)
    # 🔴🔴 `O-20` — **DÜRÜSTLÜK KAPISI PLAN YOLUNU HİÇ GÖRMÜYORDU.**
    #
    # ⊙ Ölçüldü (canlı `V` turu): *«personel **devir oranı** bu yıl nasıl»* → cevap
    # **`personel_sayisi`** (baş sayısı) döndü. Soru bir **oran** istiyordu, cevap bir
    # **sayım** verdi ve **hiçbir beyan yoktu** — `sessiz_yanlis` sınıfı, ve onu üreten
    # şey bayrağı kapatılamayan bir yol.
    #
    # ⚠ Kusur yeni değil: `uyum.py` bu sınıfı **zaten tanıyor** (`o16`: *«iş kazası
    # ORANI»* → `kaza_adedi`, beyansız) ve kapısı yazılı. Ama o kapı `ask()`in
    # kapanışında duruyor ve plan yolu oradan **hiç geçmiyor** — yani bir gardiyan var,
    # yeni açılan kapıda değil.
    #
    # ⚠ Model **uydurmadı**: `personel_sayisi` katalogda **var**. Yaptığı şey bir
    # **ikame**dir — istenen kavram yoksa en yakınını koymak. Beyaz liste ikameyi
    # göremez (ad geçerli), ad denetimi de göremez (`O-18` adın varlığına bakar).
    # Görebilen tek yer, **soruyla cevabı karşılaştıran** yerdir.
    #
    # *Bir kapıyı yazmak onu her yola koymaz — ve yeni bir yol, eski kapıların
    # arkasından değil, YANINDAN geçer.*
    # ⚠ `Ihlal` **nesnesi** taşınır, `isaret` dizesi değil: kullanıcıya giden metin
    # `aciklama` alanındadır ve nesneyi yeniden kurmak onu **boşaltırdı**. Bir kapının
    # çıktısını parçalayıp yeniden birleştirmek, kapının cümlesini kaybetmenin yoludur.
    _ihlaller: list = []
    _gorulen: set[str] = set()
    # 🔴🔴 `O-20/Y` — **PLANIN BAŞKA YOLDAN KARŞILADIĞI İŞARET BEYAN EDİLMEZ.**
    #
    # ⊙ Ölçüldü (canlı `VI`, *«en çok fire veren makineyi bul ve o makinenin vardiya
    # dağılımını göster»*): plan **6 adım** koştu, `BAGLA` en çok fire vereni **seçti**
    # (`RAM-2`) — ve cevabın altına *«en yüksek/en çok dedin ama sıralama
    # uygulayamadım»* yazıldı. **Yanlış.** Uygulandı; yalnız `order` alanıyla değil
    # bir **adımla**.
    #
    # ⚠ `uyum.denetle` bir **`CubeQuery`** denetleyicisidir: üstünlüğü `order`/`limit`
    # alanlarında arar. Plan yolunda aynı niyet `BAGLA` (tekini seç) ve `SIRALA` (çok
    # ölçütle sırala) fiilleriyle taşınır — kapı onları **göremez**, çünkü bakmadığı
    # bir yerdeler.
    #
    # 🔴 `§101.1` birebir: yanlış bir *«eksik»* beyanı, sustuğu durumdan pahalıdır —
    # kullanıcıya doğru bir cevabı **yanlış** diye okutur. Kapıyı kaldırmıyoruz;
    # **planın karşıladığını** ondan düşüyoruz.
    #
    # *Bir denetçiyi yeni bir yola koyarken, o yolun kendi araçlarını da tanıtmak
    # gerekir; yoksa denetçi tanımadığı her çözümü bir eksiklik sanar.*
    _fiiller = {str(a.get("fiil")) for a in (plan.get("adimlar") or [])}
    _karsilanan: set[str] = set()
    if _fiiller & {"BAGLA", "SIRALA"}:
        _karsilanan |= {"ustunluk", "kesme"}
    if "TREND" in _fiiller:
        _karsilanan |= {"trend", "kiyas"}
    if "KIR" in _fiiller or any(
            (b.get("cube_query") or {}).get("dimensions") for b in _bolumler
            if isinstance(b.get("cube_query"), dict)):
        _karsilanan.add("kirilim")
    # 🔴🔴 `§Cİ-belge` — **BİR BELGENİN KAPSAMI, BLOKLARININ BİRLEŞİMİDİR.**
    #
    # ⊙ Ölçüldü (curl `V` turu, T7/V7): 4 bloklu bir panoda *«panoya su tüketimi de
    # ekle»* → beyan *«**su tuket** bu küpte tanımlı değil»* dedi. Oysa
    # `surdurulebilirlik` **panonun bir bloğuydu** ve terimi karşılıyordu.
    #
    # 🔴 Kök: `denetle` bölüm **bölüm** koşuyor ve bir işaret için **ilk ıskalayan blok
    # kazanıyordu**. Yani beyan, cevabın **bir parçasına** bakıp *«bu cevap onu
    # içermiyor»* diyordu — `§KB`'nin (harman ölçüleri bayat yüzeyde) birebir kardeşi,
    # bu turda **beşinci** kez aynı ders.
    #
    # ⚠ Kural **yalnız çapraz-küp işaretlerine** uygulanır (`olcu_ikamesi`,
    # `olcu_ozgullugu`): orada *«başka blokta var»* gerçekten *«belgede var»* demektir.
    # Öteki işaretler (dönem, eşik, kırılım) bir bloğun **kendi** kusurudur ve bir
    # başkası onu karşılamaz — onlarda ilk-bulan aynen kalır.
    #
    # *Bir cevabın neyi içerdiğini, cevabın bir parçasına sorarsanız, öbür parçadakini
    # eksik ilan edersiniz.*
    # ⟳ `§Cİ-küp` (curl `DD` turu) — küp ikamesi de bir **çapraz-küp** işaretidir:
    # belge başka bir bloğunda o konuyu karşılamış olabilir.
    _BIRLESIM = {"olcu_ikamesi", "olcu_ozgullugu", "kup_ikamesi"}
    try:
        from app import uyum as _uyum
        _blok_sayisi = sum(1 for _b in _bolumler if isinstance(_b.get("cube_query"), dict))
        _iskalayan: dict[str, int] = {}
        _bekleyen: dict = {}
        for _b in _bolumler:
            _bcq = _b.get("cube_query")
            if not isinstance(_bcq, dict):
                continue
            _bcm = next((c for c in (schema.get("cubes") or [])
                         if c.get("name") == _bcq.get("cube")), None)
            # ⚠ `§Cİ` — şema geçilir: çapraz-küp ikamesi ancak öteki küpler görülerek
            # anlaşılır (ölçüldü: `_match_measure("…fire…", kalite)` → `None`).
            for _ih in _uyum.denetle(soru, {"cube_query": _bcq}, _bcm, schema):
                if _ih.isaret in _karsilanan or _ih.isaret in _gorulen:
                    continue
                if _ih.isaret in _BIRLESIM:
                    # Bu blok ıskaladı — ama belge onu **başka** bir blokla karşılamış
                    # olabilir. Kararı bütün bloklar görülmeden verme.
                    _iskalayan[_ih.isaret] = _iskalayan.get(_ih.isaret, 0) + 1
                    _bekleyen.setdefault(_ih.isaret, _ih)
                    continue
                _gorulen.add(_ih.isaret)
                _ihlaller.append(_ih)
        # `§Cİ-belge` — yalnız **HİÇBİR** blok karşılamadıysa beyan edilir.
        for _isaret, _sayi in _iskalayan.items():
            if _sayi >= _blok_sayisi and _isaret not in _gorulen:
                _gorulen.add(_isaret)
                _ihlaller.append(_bekleyen[_isaret])
        _eksik_notu = ("\n\n" + _uyum.kismi_cevap_notu(_ihlaller)) if _ihlaller else ""
        # 🔴🔴 `§YS-plan` — **GARSONUN «TEMSİL EDEMEDİM» İDDİASI, PLAN YOLUNDA DA.**
        #
        # Ölçülen kusur (curl, 2026-08-12): *«müşteri kohort analizi yap»* → plan koştu,
        # **müşteri × dönem PİVOTU** teslim edildi ve *«kohort uygulanmadı»* beyanı
        # **yoktu**. `uyum.denetle` bunu göremez: o bir **CubeQuery** denetleyicisidir
        # (ölçü · boyut · sıralama), *«kohort»* ise bir **metodoloji** sözcüğü — hiçbir
        # küp eksenine karşılık gelmez.
        #
        # ⊙ Sahip **değişmiyor**: karar ve iki deterministik süzgeç yine
        # `uyum.yok_sayilan_beyani`'nda (küp yolunun kullandığı **aynı** gövde). Buraya
        # kalan yalnız çağrı ve **fişin birleşimi**: plan çok bloklu olduğu için bir
        # sözcük *«fişte geçmiyor»* sayılmadan önce **bütün** blokların taşıdıkları
        # birleştirilir — `§Cİ-belge`'nin aynı disiplini (*bir cevabın neyi içerdiğini
        # bir parçasına sorarsanız, öbür parçadakini eksik ilan edersiniz*).
        _ys = [str(w).strip() for w in ((plan or {}).get("yok_sayilan") or [])
               if str(w).strip()]
        if _ys:
            _bkup = {"cube": "", "measures": [], "dimensions": [], "filters": [],
                     "period_expr": ""}
            for _b in _bolumler:
                _bcq = _b.get("cube_query")
                if not isinstance(_bcq, dict):
                    continue
                _bkup["cube"] = _bkup["cube"] or str(_bcq.get("cube") or "")
                _bkup["period_expr"] += " " + str(_bcq.get("period_expr") or "")
                _bkup["measures"] += [str(m) for m in (_bcq.get("measures") or [])]
                _bkup["dimensions"] += [str(d) for d in (_bcq.get("dimensions") or [])]
                _bkup["filters"] += list(_bcq.get("filters") or [])
            _cm0 = next((c for c in (schema.get("cubes") or [])
                         if c.get("name") == _bkup["cube"]), None)
            _kabuk = types.SimpleNamespace(note="", trace=[])
            if _uyum.yok_sayilan_beyani(_kabuk, soru, _bkup, _cm0, schema, _ys):
                _eksik_notu += ("\n\n" if _eksik_notu else "\n\n") + _kabuk.note.strip()
                _log.info("§YS-plan: temsil edilemeyen sözcük beyan edildi (%s)",
                          ", ".join(_ys))
        # `§RT` — belge indirgemesi beyanı, uyum beyanının **yanına** eklenir: ikisi
        # farklı şeyler söyler (biri *«sorunun bir parçası taşınmadı»*, öteki *«belge
        # kurulamadı»*) ve biri ötekini ezmemeli.
        if _belge_notu:
            _eksik_notu = ("\n\n" + _belge_notu) + _eksik_notu
        if _ihlaller:
            _log.info("plan: beyanlı kısmi cevap (%s)", ", ".join(sorted(_gorulen)))
    except Exception:                          # noqa: BLE001 — beyan turu DÜŞÜRMEZ
        _log.info("uyum denetimi yapılamadı (beyan atlandı)", exc_info=True)
        _eksik_notu = ""
    _uyari = ("\n\n⚠ Plan doğru kuruldu ve koştu ama **hiçbir adım satır döndürmedi** — "
              "dönem ya da süzgeç veriyle örtüşmüyor olabilir." if _bos else
              "\n\n⚠ Plan doğru kuruldu ve koştu, satır da döndü — ama **tüm değerler "
              "boş**. Bu bir arıza değil bir **bulgudur**: istenen dönem ya da süzgeç "
              "için kayıt yok. Daha geniş bir dönem denemek sonucu değiştirebilir."
              if _null else "")
    return {
        "source": "cube+llm",
        "note": cevap_notu(plan, out) + _uyari + _eksik_notu,
        # 🔴 Onarım beyanları izin **başına değil sonuna** eklenir: birinci satır
        # *"kaç adım koştu"* sorusunun cevabıdır ve okuyucunun ilk aradığı odur.
        # Beyan yoksa liste bayt bayt bugünküdür (`KURAL B` disiplini).
        "iz": ([f"orkestratör: {_n} adımlık plan koştu ({out['sorgu_sayisi']} sorgu)"]
               + _devir_izi
               + [f"onarım: {b}" for b in (out.get("onarimlar") or [])]),
        "result": _son,
        "cube_query": (_bolumler[-1]["cube_query"] if _bolumler else None),
        # ⊙ Her `SORGU` adımının TAM sonucu + onu üreten sorgu. `FAZ 6` (frontend adım
        # bileşeni) ve `FAZ 7` (rapor/pano) tüketicisi budur; ikisi de bunsuz kurulamaz.
        # ⚠ `cube_query` her bölümle birlikte taşınıyor ki her adım `/cube` ile **sıfır
        # LLM** yeniden koşulabilsin (`O-5`).
        "bolumler": _bolumler,
        # 🔴🔴 `§RP` — **ÇOK BÖLÜMLÜ BELGE, FRONTEND'İN TANIDIĞI BİÇİMDE.**
        #
        # ⊙ Ölçüldü (2026-08-10): *«son 2 yıl satış raporu hazırla»* → plan `SORGU×4 +
        # RAPOR` koştu ve dört bölüm hesaplandı. Bölümler cevaba **ulaşıyordu**
        # (`plan.bolumler`) — ama **ham** hâlde: başlıksız, `viz`siz, sayfasız. Yani
        # `ReportView.tsx`'in çizebileceği bir **belge** yoktu; yalnız bir veri yığını.
        #
        # ⚠ İlk teşhisim *«bölümler atılıyor»* idi ve **ölçümle düzeldi** (bugün 7.
        # kez). Kusur taşımada değil **derlemede**: bir yığın, bir belge değildir.
        #
        # ⚠ Biçimin tek sahibi `report.py` (`ReportView.tsx`'in tanıdığı `Report`);
        # burada yalnız **çağrı** var. Ve `bolumlerden_kur` sonuçları **yeniden
        # koşmaz** — elde olanı dizer. *Bir sonucu iki kez hesaplamak, onu bir kez
        # yanlış hesaplamanın en kolay yoludur.*
        #
        # ⚠ Yalnız plan gerçekten bir **belge** fiili taşıyorsa kurulur: `RAPOR`/`PANO`
        # yoksa bu bir rapor değil sıradan bir çok-adımlı cevaptır ve ona belge muamelesi
        # yapmak kullanıcıya olmayan bir şeyi vaat etmek olurdu.
        "rapor": _rapor,
        # 🔴 `FAZ 6` — cevabın **yapısı** kullanıcıya taşınır. `agent_run`'dan farkı:
        # o bir denetim izidir (geriye dönük, sonuçsuz), bu **cevabın kendisidir**.
        "plan": {
            "adimlar": [{"sira": i, "fiil": a.get("fiil"), "ozet": _adim_metni(a)}
                        for i, a in enumerate(plan["adimlar"], 1)],
            "bolumler": _bolumler,
        },
    }


#: `§RÇ` — bir düzenleme isteği belgeyi **değiştirmediyse** söylenecek cümle. Tek sahip:
#: iki dal (plan yok · plan değiştirmedi) aynı şeyi söylüyorsa orada iki dal değil bir
#: dal vardır (`§AY`'nin aynı dersi).
BELGE_DEGISMEDI = ("⚠ Belgede bir **değişiklik yapılmadı** — isteğini bir bölüme "
                   "bağlayamadım. Bölümü adıyla yazabilirsin (ör. *«müşteri kırılımını "
                   "çıkar»* · *«oee bölümünü çıkar»*), ya da ne eklemek istediğini söyle.")


def _belgeyi_koru(onceki_bolumler: list[dict], schema: dict, soru: str) -> dict:
    """`§RD-4`/`§RÇ` — elde tutulan belgeyi **aynen** geri ver + neden değişmediğini söyle.

    ⚠ Bölümlerin **sonuçları yoktur** (istemci yalnız kimlikleri geri yollar — `G0b`),
    o yüzden belge burada **yeniden koşulmaz**; kimlikleriyle dizilir. Frontend elindeki
    kartları zaten çiziyor; buradan giden şey belgenin **kaybolmadığının** kanıtıdır.
    """
    from app import report as _report

    try:
        _r = _report.bolumlerden_kur(onceki_bolumler, baslik=soru or "Rapor", schema=schema)
    except Exception:                     # noqa: BLE001 — koruma turu DÜŞÜREMEZ
        _log.warning("§RD-4: belge korunamadı (best-effort)", exc_info=True)
        _r = None
    _log.info("§RD-4: belge düzenlemesi çözülemedi → belge KORUNDU (%d bölüm)",
              len(onceki_bolumler))
    return {"source": "cube", "note": BELGE_DEGISMEDI, "rapor": _r,
            "iz": ["Belge düzenlemesi: istek bir bölüme bağlanamadı → belge KORUNDU "
                   "(Discovery'ye düşülmedi — §RD-4)"]}


def _fisi_coz(cq: dict | None, *, schema: dict, soru: str) -> dict | None:
    """`§RE` — bir bölümün fişindeki `period_expr` **çözülür**; gerekçe çağrı yerinde.

    ⚠ `period_expr` bir **niyet taşıyıcısıdır**, bir sorgu alanı değil (`O-15/D`). Fişte
    kalırsa iki zarar birden doğar: (1) yanındaki bayat `filters` fişi yalancı yapar,
    (2) `/cube` ile yeniden koşulduğunda **başka bir sayı** çıkar.

    ⚠ Çözülemezse fiş **olduğu gibi** döner: bir onarımın başarısızlığı bir bölümü
    düşürmez. *Bir kusuru düzeltememek, onu büyütmek için bir sebep değildir.*
    """
    if not isinstance(cq, dict) or not cq.get("period_expr"):
        return cq
    try:
        from app.cube_router import _norm
        from app.routers.ask import _resolve_period

        _spec = next((c for c in (schema.get("cubes") or [])
                      if c.get("name") == cq.get("cube")), {}) or {}
        _td = (_spec.get("time_dimensions") or ["tarih"])[0]
        _kopya = dict(cq)
        _ifade = _kopya.pop("period_expr")
        # ⚠ Bayat dönem süzgeci **atılır**: `period_expr` onu ezmek için yazılmıştır;
        # ikisini yan yana bırakmak tam da ölçülen çelişkiydi.
        _kopya["filters"] = [f for f in (_kopya.get("filters") or [])
                             if str((f or {}).get("dimension") or "") != _td]
        _cozulmus, _ = _resolve_period(None, _kopya, _ifade, _norm(soru or ""), _td)
        _log.info("§RE: bölüm fişi çözüldü (%s · %r)", cq.get("cube"), _ifade)
        return _cozulmus
    except Exception:                          # noqa: BLE001 — çözüm turu DÜŞÜRMEZ
        _log.warning("§RE: fiş çözülemedi (best-effort)", exc_info=True)
        return cq


def _belgeyi_derle(bolumler: list[dict], baslik: str, schema: dict):
    """`§RS` — bölümleri `Report`'a dizer. Tek sahip yine `report.bolumlerden_kur`."""
    from app import report as _report

    try:
        return _report.bolumlerden_kur(bolumler, baslik=baslik, schema=schema)
    except Exception:                          # noqa: BLE001 — derleme turu DÜŞÜREMEZ
        _log.warning("§RS: belge yeniden derlenemedi (best-effort)", exc_info=True)
        return None


def _baslik_metni(plan: dict, soru: str) -> str:
    """Belge başlığı — planın belge fiilindeki başlık, yoksa kullanıcının cümlesi."""
    return next((str(a.get("baslik")) for a in (plan.get("adimlar") or [])
                 if str(a.get("fiil")) in ("RAPOR", "PANO") and a.get("baslik")),
                soru or "Rapor")


def _kayip_bolumleri_geri_koy(bolumler: list[dict], onceki: list[dict], *, service,
                              schema: dict, limit: int | None = None
                              ) -> tuple[list[dict], int]:
    """`§RS` — önceki belgede olup yenisinde **olmayan** bölümleri geri koyar ve koşar.

    Gerekçe çağrı yerinde. Burada tek incelik: kimlik kıyası `§RÇ` ile **aynı** üçlüdür
    (küp · ölçüler · boyutlar) — iki farklı kimlik tanımı, bir gün iki farklı belge
    demekti (`KAT-1`).
    """
    from app import report as _report

    def _k(b: dict) -> tuple:
        cq = b.get("cube_query") or {}
        return (str(cq.get("cube") or ""), tuple(cq.get("measures") or []),
                tuple(cq.get("dimensions") or []))

    _var = {_k(b) for b in bolumler if isinstance(b.get("cube_query"), dict)}
    _kayip = [b for b in (onceki or [])
              if isinstance(b.get("cube_query"), dict) and _k(b) not in _var]
    if not _kayip:
        return bolumler, 0
    try:
        _r = _report.compose_report(
            service, schema,
            {"blocks": [{"cube_query": b["cube_query"]} for b in _kayip]},
            limit=limit or 1000)
    except Exception:                          # noqa: BLE001 — geri koyma turu DÜŞÜREMEZ
        _log.warning("§RS: kayıp bölümler koşulamadı (best-effort)", exc_info=True)
        return bolumler, 0
    _geri = [{"cube_query": b.get("cube_query"), "result": b["result"]}
             for sayfa in (_r.get("pages") or []) for b in (sayfa or [])
             if b.get("result") and not b.get("error")]
    if not _geri:
        return bolumler, 0
    _log.info("§RS: «ekle» isteğinde kaybolan %d bölüm geri kondu", len(_geri))
    return bolumler + _geri, len(_geri)


def _tarih_suzgeci(cq: Any) -> list[dict]:
    """Bir fişin **dönem** süzgeçleri. Tek sahip: üç yerde tekrar eden okuma."""
    if not isinstance(cq, dict):
        return []
    return [f for f in (cq.get("filters") or [])
            if str((f or {}).get("dimension") or "") == "tarih"]


def _donemi_devret(bolumler: list[dict], *, service: Any, schema: dict,
                   limit: int | None = None, onceki: list[dict] | None = None,
                   iz: list[str] | None = None) -> list[dict]:
    """`§RD-3` — dönemi olmayan bölümler belgenin dönemini devralır **ve yeniden koşar**.

    Gerekçe çağrı yerinde. Burada tek karar: **hangi dönem belgenindir?**

    1. Yeni planın dönemi olan **ilk** bölümü — kullanıcı bu turda bir dönem yazdıysa o
       kazanır (*«bir de geçen ayı ekle»* onun seçimidir, ezilmez).
    2. Yoksa **önceki belgenin** dönemi.

    🔴 İkinci basamak canlıda ölçülerek eklendi (curl `D7`): elde *«son 2 yıl»* dönemli
    6 bloklu bir rapor varken *«rapora aylık ciro trendi de ekle»* → yeni planın
    **hiçbir** bölümünde dönem yoktu. Yani belge, bir **düzenleme** turunda dönemini
    tümden kaybediyordu ve kullanıcı bunu ancak sayılar tuhaflaşınca fark ederdi.

    ⚠ İlk yazımda devir yalnız *«bölümlerden biri dönemi biliyorsa»* koşuyordu — yani
    tam da en çok gerektiği yerde, **hepsi unuttuğunda**, hiç koşmuyordu.
    *Bir boşluğu doldurmayı elde kalan bir örneğe bağlarsanız, hiçbir örnek kalmadığında
    boşluk en büyük hâline gelir.*
    """
    from app import report as _report

    _belge = next((_tarih_suzgeci(b.get("cube_query")) for b in bolumler
                   if _tarih_suzgeci(b.get("cube_query"))), [])
    _kaynak_adi = "planın kendi dönemi"
    if not _belge:
        _belge = next((_tarih_suzgeci(b.get("cube_query")) for b in (onceki or [])
                       if _tarih_suzgeci(b.get("cube_query"))), [])
        _kaynak_adi = "önceki belgenin dönemi"
    if not _belge:
        return bolumler
    _hedef = [i for i, b in enumerate(bolumler)
              if isinstance(b.get("cube_query"), dict)
              and not _tarih_suzgeci(b.get("cube_query"))]
    if not _hedef:
        return bolumler
    _yeni = [{**bolumler[i]["cube_query"],
              "filters": list(bolumler[i]["cube_query"].get("filters") or []) + list(_belge)}
             for i in _hedef]
    try:
        _r = _report.compose_report(service, schema,
                                    {"blocks": [{"cube_query": cq} for cq in _yeni]},
                                    limit=limit or 1000)
    except Exception:                     # noqa: BLE001 — devir turu DÜŞÜREMEZ
        _log.warning("§RD-3: dönem devri koşulamadı (best-effort)", exc_info=True)
        return bolumler
    _bloklar = [b for sayfa in (_r.get("pages") or []) for b in (sayfa or [])]
    _devredi = False
    for _i, _blok in zip(_hedef, _bloklar):
        if _blok.get("error") or not _blok.get("result"):
            continue      # ⚠ koşamayan bölüm ESKİ hâliyle kalır — fişi hâlâ doğrudur
        bolumler[_i] = {"cube_query": _blok.get("cube_query"), "result": _blok["result"]}
        _log.info("§RD-3: bölüm belgenin dönemini devraldı ve yeniden koştu (%s · %s)",
                  (_blok.get("cube_query") or {}).get("cube"), _kaynak_adi)
        _devredi = True
    # 🔴 **SESSİZ DEVİR YOK.** Kullanıcının yazmadığı bir dönemle hesaplanmış bir sayı,
    # varsayımı görülmeden okunmamalı (`§MV`'nin aynı kuralı).
    if _devredi and iz is not None:
        iz.append(f"belge dönemi: {len(_hedef)} bölüm {_kaynak_adi}ni devraldı "
                  f"ve yeniden koştu (§RD-3)")
    return bolumler


def _ek_bolumler_kos(temel: dict, *, service: Any, schema: dict,
                     limit: int | None = None) -> list[dict]:
    """`§RZ`'nin türettiği ek bölümleri **koşar** ve `_bolumler` biçiminde döner.

    ⚠ Koşucu **yeniden yazılmadı**: `report.compose_report` bir bloğu koşan tek sahiptir
    (dönem çözümü · `cube_sql` · hata izolasyonu hepsi orada). İkinci bir koşucu, bir gün
    ikisinden yalnız birinin düzeltileceği anlamına gelirdi (`KAT-1`).

    ⚠ **Boş bölüm eklenmez:** bir belgeye sıfır satırlık bir kırılım koymak, sayfayı
    doldurup okuyucuya hiçbir şey söylememektir.
    """
    from app import report as _report
    from app.plan_semasi import belge_bolum_sirala, belge_ek_bolumleri

    _kup = str((temel or {}).get("cube") or "")
    _meta = next((c for c in (schema.get("cubes") or []) if c.get("name") == _kup), None)
    if not _meta:
        return []
    _ekler = belge_ek_bolumleri(temel, _meta)
    if not _ekler:
        return []
    try:
        _r = _report.compose_report(service, schema,
                                    {"blocks": [{"cube_query": cq} for cq in _ekler]},
                                    limit=limit or 1000)
    except Exception:                     # noqa: BLE001 — zenginleştirme turu DÜŞÜREMEZ
        _log.warning("§RZ: ek bölümler koşulamadı (best-effort)", exc_info=True)
        return []
    _kosan: list[dict] = []
    for _blok in (b for sayfa in (_r.get("pages") or []) for b in (sayfa or [])):
        _sonuc = _blok.get("result")
        if _sonuc and (_sonuc.get("row_count") or 0) > 0:
            _kosan.append({"cube_query": _blok.get("cube_query"), "result": _sonuc})
    # `§RZ-2` — seçim **koşulmuş satırların üstünde** yapılır: hangi kırılımın bilgi
    # taşıdığı koşmadan bilinemez. Gerekçe `belge_bolum_sirala`'da.
    _out = belge_bolum_sirala(_kosan)
    _log.info("§RZ: belge tek bölümlüktü → %d aday türetildi · %d koştu · %d seçildi",
              len(_ekler), len(_kosan), len(_out))
    return _out


def _belge_bolumleri(kaynak: Any) -> list[dict] | None:
    """`§RD` — istekle gelen **önceki belgenin** bölüm kimlikleri (yoksa `None`).

    ⚠ Kaynak **istemcidir**: bir belge sunucuda saklanmaz (`PANO` fiilinin kendi kuralı:
    *«hiçbir şey kaydetmez»*). İstemci son cevabın `rapor`unu geri yollar — `cube_query`
    checkpoint'inin (`D4`) birebir aynı deseni.

    ⚠ Yalnız **kimlikler** okunur; `result` alanına hiç dokunulmaz. Planlayıcıya satır
    gitmez (`G0b`). *Bir planı kurmak için sonuçları bilmek gerekmez.*

    ⚠ Fail-open: alan yoksa ya da biçimi bozuksa `None` döner ve bağlam bugünkü hâline
    düşer (`KURAL B`).
    """
    if not isinstance(kaynak, dict):
        return None
    out: list[dict] = []
    for sayfa in (kaynak.get("pages") or []):
        for blok in (sayfa or []):
            if isinstance(blok, dict) and isinstance(blok.get("cube_query"), dict):
                out.append({"cube_query": blok["cube_query"]})
    return out or None


def _bulgu_metni(plan: dict, out: dict) -> str:
    """Sorgu-dışı adımların **çıktısını** cümleye çevirir.

    ⚠ Yalnız çalıştırıcının **gerçekten döndürdüğü** sayılar yazılır — `narration_guard`'ın
    kuralının aynısı: eşleşmeyen sayı taşıyan cümle yayımlanmaz. Burada eşleşme
    yapısaldır, çünkü sayı zaten çıktının kendisidir.
    """
    sat: list[str] = []
    for a, c in zip(plan.get("adimlar") or [], out.get("ciktilar") or []):
        if a.get("fiil") == "BAGLA" and isinstance(c, tuple):
            # 🔴🔴 `§BG` — **SEÇİLMEYEN BİR ŞEY «None» DİYE SEÇİLMİŞ GİBİ YAZILAMAZ.**
            #
            # ⊙ Ölçüldü (curl `Y` turu): *«bu yıl hangi operatör en çok rework yaptı»* →
            # kaynak sorgu **0 satır** döndü, `BAGLA` seçecek bir şey bulamadı ve cümle
            # şu oldu: *«**None** seçildi (`rework_sayisi` = …)»*. Kullanıcıya bir Python
            # değeri sızdı ve üstelik **bir seçim yapılmış gibi** sunuldu.
            #
            # ⚠ Doğru cevap sessizlik de değil: adımın **neden** boş döndüğü zaten
            # yanındaki boşluk beyanında yazılı (`§35`/`yokluk_notu`); burada tek iş, o
            # boşluğu bir **seçim** gibi anlatmamaktır.
            #
            # *Bir seçimin yapılmadığını söylemek, yapılmış gibi bir ad yazmaktan her
            # zaman iyidir — çünkü ikincisi bir cevap gibi okunur.*
            if c and c[0] is not None and str(c[0]).strip():
                sat.append(f"**{c[0]}** seçildi (`{a.get('olcu')}` = {_b(c[1])}).")
            else:
                sat.append(f"⚠ `{a.get('olcu')}` için **seçilecek bir satır çıkmadı** — "
                           f"bu adım bir varlık seçemedi.")
        elif a.get("fiil") == "HESAPLA" and isinstance(c, dict):
            _y = "düşük" if (c.get("fark") or 0) < 0 else "yüksek"
            sat.append(f"Akran ortalaması {_b(c.get('akran_ortalamasi'))} "
                       f"({c.get('akran_sayisi')} akran) — aradaki fark "
                       f"**{_syuzde(abs(c.get('fark_yuzde') or 0))} {_y}**.")
    return "\n".join(sat)


def _b(x: Any) -> str:
    """Okunabilir sayı. ⚠ `§AA1`'in dersi: ham `float` (`0.5245118291704627`) bir cevap
    değil, bir sızıntıdır.

    🔴 `§SB-metin` — bu, aynı sayının **BEŞİNCİ** biçimlendiricisiydi ve ötekiler gibi
    ondalık ayırıcıyı İngilizce basıyordu (*«= 0.5245 … akran 0.59»*). Gövde
    `app/sayi_bicimi.py`'de; burada yalnız takma ad.
    *Bir sayının Türkçesi tek bir yerde yazılır.*
    """
    return _ssayi(x)


def _adim_metni(adim: dict) -> str:
    """Bir adımı **kullanıcının** okuyabileceği tek satıra çevirir.

    ⚠ Fiil adı ham geçirilmez (`BAGLA` kimseye bir şey söylemez); anlamı `plan_semasi`'nin
    **kendi sözlüğünden** okunur. Burada ikinci bir anlam tablosu yazmak, fiil kümesine
    üçüncü bir sahip eklemek olurdu (`KAT-1`).
    """
    from app.plan_semasi import FIIL_ANLAMI

    fiil = adim.get("fiil", "?")
    anlam = FIIL_ANLAMI.get(fiil, "")
    if fiil == "SORGU":
        # ⚠ `cube_query` bir **referans dizesi** de olabilir (`"$3"`) — `KIR`/`SUZ`'ün
        # ürettiği sorguyu koşan adım tam olarak öyle yazılır. Sözlük varsayan hâl
        # canlıda patladı (`AttributeError`). *Bir alanın tipi genişlediğinde, onu
        # okuyan her yer de genişlemelidir — biri kalırsa orası kırılır.*
        cq = adim.get("cube_query")
        if isinstance(cq, str):
            return f"**{fiil}** — `{cq}` adımının ürettiği sorguyu koşar"
        cq = cq or {}
        # 🔴 `§CC-D` MAKBUZ DÜZEYİNDE TEKRARLANDI. Ölçüldü (canlı `D2'`): makbuzda
        # **`toplam_fire_kg↓`** yazıyordu — katalogun *«az olan iyidir»* işareti,
        # kullanıcının okuduğu satıra sızmış. `parse_cube_query` onu **kimlikten**
        # ayıklıyor (orada ölçülmüş bir kusurdu); makbuz aynı ayıklamayı yapmıyordu.
        # *Bir süsü bir yerde temizlemek, onu üreten kaynağı temizlemez — ve o kaynak
        # her yeni okuyucuya aynı süsü yeniden verir.*
        from app.katalog_metni import _AZ_IYI as _AZ
        _o = ", ".join(str(m).rstrip(_AZ).strip()
                       for m in (cq.get("measures") or [])) or "?"
        _b = ", ".join(cq.get("dimensions") or [])
        return f"**{fiil}** — `{_o}`" + (f" · `{_b}` kırılımında" if _b else "")
    # ⚠ Değer bir sözlük (satır içi `cube_query`) olabilir; ham `dict` basmak makbuzu
    # okunmaz yapar. Kısaltılır — makbuz bir **özet**tir, bir döküm değil.
    def _kisa(v: Any) -> str:
        if isinstance(v, dict):
            return str(v.get("cube") or "sorgu")
        if isinstance(v, (list, tuple)):
            return ", ".join(str(x) for x in v)
        return str(v)

    _ek = " · ".join(f"`{k}`=`{_kisa(v)}`" for k, v in adim.items() if k != "fiil")
    return f"**{fiil}** — {anlam}" + (f" ({_ek})" if _ek else "")


def makbuz(plan: dict) -> str:
    """Koşan planın **adım adım** makbuzu.

    🔴 `O-5`'in zeminidir: kullanıcı cevabın kaç adımda ve **hangi** adımlarla üretildiğini
    görür. Bir orkestratörün en büyük riski, birleşik sonucun hangi adımdan geldiğinin
    görünmemesiydi — makbuz o riskin panzehiridir, süsü değil.
    """
    adimlar = (plan or {}).get("adimlar") or []
    sat = [f"**Bu cevap {len(adimlar)} adımda üretildi:**"]
    sat += [f"{i}. {_adim_metni(a)}" for i, a in enumerate(adimlar, 1)]
    return "\n".join(sat)


def neden_olmadi(plan: dict, hata: Exception) -> str:
    """🔴 **Adım adım DÜRÜST RET** — `O-4`'ün ikinci başarı ölçütü.

    Bugünkü karşılığı tek cümle: *"Bu soru için güvenilir bir sorgu üretemedim."* Kullanıcı
    ondan hiçbir şey öğrenemez; bu metinden **neyin** eksik olduğunu öğrenir.

    ⚠ Uydurma yok: yalnız planın kendi adımları ve çalıştırıcının kendi hata metni yazılır.
    """
    adimlar = (plan or {}).get("adimlar") or []
    sat = ["Bu soruyu cevaplamak için şu adımları planladım:"]
    sat += [f"{i}. {_adim_metni(a)}" for i, a in enumerate(adimlar, 1)]
    sat += ["", f"🔴 **Ama tamamlayamadım:** {hata}"]
    return "\n".join(sat)


def belge_takibi(request: Any, *, service: Any, schema: dict, soru: str,
                 settings: Any = None, principal: Any = None,
                 limit: int | None = None, onceki_rapor: Any = None) -> dict | None:
    """🔴🔴 `§RD-takip` — **BELGE DÜZENLEME, FİŞ DÜZENLEMEDEN ÖNCE GELİR.**

    ⊙ Ölçüldü (curl `CC` turu, CC-21/CC-22): ekranda **4 bölümlü** bir belge varken
    *«rapora fire oranını da ekle»* → `refine → deterministik düzenleme` →
    **`rapor=None`**. Belge yok oldu, yerine tek bloklu bir saçılım grafiği geldi.

    ⊙ Kök bir **öncelik ters çevrilmesidir**, eksik bir yetenek değil: `§RD`/`§RD-4`
    (*belgeyi düzenle · düzenleyemezsen **koru***) yalnız `ask()`in taze dalında
    yaşıyor, o da yapısal takip zincirinden **sonra** deneniyor. Bir belge düzenleme
    isteği aynı anda geçerli bir **fiş** düzenlemesidir de — `deterministic_refine`
    onu kapar, başarılı olur, ve dört bölüm sessizce silinir. Korumanın kendisi
    **erişilemezdi**.

    ⚠ İki hipotez **çürütüldü**, ikisi de ölçümle: (1) *«bölüm» sözcüğü `bolum`
    boyutuna eşleşiyor* — o sözcüğü taşımayan cümle de belgeyi yok etti; (2) *ölçüm
    artefaktı, istemci `previous_rapor` göndermiyor* — `page.tsx:265` `cube_query`
    **ve** `previous_rapor`'u birlikte gönderiyor.

    🔴 `KURAL B` **üç katmanla** korunur: bayrak kapalıysa `cevap()` zaten `None`
    döner · belge yoksa hiç koşulmaz · plan çıkmazsa (`koru=False`) `None` döner ve
    zincir bugünkü davranışını **bayt bayt** sürdürür.

    ⚠ Yalnız **belge üreten** bir cevap kabul edilir: plan tüketicisi belge kurmadan
    tek bir sorgu döndürdüyse o zaten takip zincirinin işidir ve orada **LLM'siz**
    yapılır. *Bir yolu açmak, ona ait olmayan işi de vermek değildir.*

    *Elindeki belgeyi kaybederek verilen bir cevap, cevap değil bir zarardır — ve bu
    cümle `§RD-4`'te zaten yazılıydı; eksik olan cümle değil, ona giden yoldu.*
    """
    if not onceki_rapor:
        return None
    try:
        out = cevap(request, service=service, schema=schema, soru=soru,
                    settings=settings, principal=principal, limit=limit,
                    route_hit=None, onceki_rapor=onceki_rapor, koru=False)
    except Exception:                    # noqa: BLE001 — tur düşmez (ADR-0020)
        _log.warning("§RD-takip: belge yolu hata verdi (best-effort)", exc_info=True)
        return None
    if out is None or not out.get("rapor"):
        return None
    out["iz"] = [*(out.get("iz") or []),
                 "§RD-takip: ekrandaki belge düzenlendi (fiş zincirinden ÖNCE)"]
    return out


def cevap_notu(plan: dict, out: dict) -> str:
    """🔴 `§67` — koşmuş bir planın **insan notu** — ve bunun **tek sahibi** ㊲.

    ## Ölçülen kusur (canlı `s30`, curl)

    `/oneri/makro` ve `/plan/kos` `note` alanında **koşucunun iç listesini** basıyordu:

        note = [{'sira': 1, 'fiil': 'SORGU', 'satir': 1}, {'sira': 2, ...}]

    Çünkü `kosum_yaniti` `out.get("makbuz")` okuyordu — ama `plan_kosucu.kos()`'un
    `makbuz` **anahtarı** adım başına makbuz **kayıtlarının listesidir** (`{"sira",
    "fiil", "satir"}`), bir cümle değil. Cümleyi üreten şey aynı adı taşıyan
    **fonksiyondur** (`makbuz(plan)`) ve merdiven yolu onu **doğru** çağırıyordu.

    ⊙ Bu, bu dosyanın kendi şerhinin (`bolumlere_cevir`) tekrarıdır: *«`ciktilar`,
    `katmanlar`, `makbuz`… bir **koşucu iç sözleşmesi**, bir cevap değil»* 🆘. Sunum
    oradan çıkarılmıştı; **not** çıkarılmamıştı — ve yarım çıkarılan bir sunum,
    çıkarılmamış gibi davranır.

    ⚠ *Aynı adı taşıyan iki şeyden biri veri, öteki cümle ise, `get` ile okunan her zaman
    yanlış olanıdır* 🅬 — çünkü sözlük erişimi tip sormaz.
    """
    return makbuz(plan) + "\n\n" + _bulgu_metni(plan, out)


def kosum_yaniti(out: dict, plan: dict, *, schema: dict, soru: str,
                 makro: str | None = None) -> dict:
    """🔴 `§66` — koşmuş bir planın **HTTP cevabı** — ve bunun **tek sahibi** ㊲.

    İki uç aynı şeyi döndürüyor: `POST /oneri/makro` (reçete) ve `POST /plan/kos`
    (onaylanan plan). Biçimi iki yerde yazmak, bir gün birinde `result` olup ötekinde
    olmaması demekti — ve bu depoda tam o kusur **ölçüldü**: makro cevabı bir demet
    boyunca `result` taşımadı, kart **gövdesiz** çizildi 🆘.

    ⚠ `source` **`cube`**: bu yolda LLM **yok** ve rozet bunu söylemeli 🅖.
    ⚠ `question` zorunlu: `AskResponse` onu şart koşuyor ve kart başlığı odur.
    """
    bolumler, son = bolumlere_cevir(out, plan, schema=schema, soru=soru)
    yanit = {
        "source": "cube",
        "question": soru,
        "adim_sayisi": len(plan.get("adimlar") or []),
        "result": son,
        # ⚠ Son bölümün fişi karta **yeniden koşulabilirlik** verir (`/cube`, 0 LLM).
        "cube_query": (bolumler[-1]["cube_query"] if bolumler else None),
        "bolumler": bolumler,
        # ⚠ `out["makbuz"]` **liste**dir (koşucu iç sözleşmesi); cümleyi `cevap_notu`
        # üretir. Ölçüldü (canlı `s30`): bu satır bir listeyi `note` diye basıyordu ve
        # arayüz onu **düz metin** olarak çiziyordu.
        "note": cevap_notu(plan, out),
    }
    if makro:
        yanit["makro"] = makro
    return yanit


def onizleme_satiri(adim: dict) -> str:
    """Önizlemede bir adımın **yazısı** — makbuzun cümlesi, ekranın biçiminde.

    ⚠ `§66` — gövde `routers/oneri.py`'den **buraya taşındı**: aynı satırı iki
    önizleme üretiyor (makro ucu ve cevap merdiveni) ve ikisi ayrı yazılsaydı
    kullanıcı **aynı adımı iki farklı cümleyle** okurdu ㊲.

    ⚠ Metnin **tek sahibi** `_adim_metni`'dir (`KAT-1`): ikinci bir cümle
    kurmak, aynı adımın makbuzda ve önizlemede **farklı** okunması demekti — ve kullanıcı
    onayladığı şeyle koşan şeyi karşılaştıramazdı. Burada yapılan **yalnız biçimdir**.

    İki ölçülmüş biçim kusuru (canlı `s24`):

    | görülen | neden |
    |---|---|
    | `SORGU` rozeti + *«**SORGU** — …»* | fiil **ayrı alan** olarak gidiyor; metin onu **yineliyordu** ㊲ |
    | ekranda düz `**` ve `` ` `` | makbuz **markdown**'a yazılır, önizleme **düz metne** |

    ⊘ Ve işaretler istemcide temizlenmedi: bir markdown çözücü üç simge için fazla, ama
    asıl sebep sahiplik — biçimi **üreten** yer bilir, tüketen yer tahmin eder 🅬.
    """

    from app.plan_semasi import FIIL_ONIZLEME

    fiil = str(adim.get("fiil") or "")
    metin = _adim_metni(adim)
    onek = f"**{fiil}** — "
    if metin.startswith(onek):
        metin = metin[len(onek):]
    metin = metin.replace("**", "").replace("`", "")
    # 🔴 `SORGU` **kendi gövdesini** yazar (*«ort_oee · makine kırılımında»*) — orada
    # kullanıcıya söylenecek şey zaten onun kendi ölçüsüdür. Ötekiler tanım basıyordu;
    # onlar için sözlüğün **önizleme kipi** okunur ve adımın kendi alanları (boyut ·
    # kaynaklar) o cümlenin **arkasına** iliştirilir.
    kisa = FIIL_ONIZLEME.get(fiil)
    if kisa and fiil != "SORGU":
        _b = str(adim.get("boyut") or adim.get("dimension") or "")
        # ⚠ Yuva **cümlenin içinde**: Türkçe eki oraya yazılı (*«makine kırılımı ekler»*).
        # Boyut yoksa yuva düşer — *«{boyut} kırılımı»* gibi bir kalıntı, bir cümleyi
        # bozuk Türkçeye çevirir ve kullanıcı onu bir hata sanır.
        metin = kisa.replace("{boyut} ", f"{_b} " if _b else "")
    # 🅡 `$3` bir **iç referanstır**; kullanıcı adımları **1'den** numaralı görüyor ve
    # aynı sayıyı iki yazımda okumak (`$3` ↔ `3`) bir tutarsızlıktır.
    # ⚠ Ek **birlikte** değişir ㊵: makbuz `$3` sözcüğünü bir ad gibi çekiyor (*«`$3`
    # adımının»*); ham değiştirme *«3. adımının»* üretti — ölçüldü, canlı `s27`. Sayıya
    # dönünce tamlama da düzelir: *«3. adımın»*. Bu bir dil kuralı değil **bir kalıbın
    # karşılığıdır**: kalıp `_adim_metni`'nde tek bir yerde yazılı.
    metin = re.sub(r"\$(\d+) adımının", r"\1. adımın", metin)
    return re.sub(r"\$(\d+)", r"\1.", metin)

def kararsiz_onizleme(cq: dict | None, soru: str, uyum: float, k: int,
                      principal: Any = None) -> Any:
    """🔴🔴 `§28.3` satır 2 + `§28.4` — **GARSON KARARSIZSA, KOŞMADAN ONAYA DÜŞER.**

    ## Planın kendi tablosu (birebir)

    ```
    3/3 aynı cevap   → marj YÜKSEK  → koş
    2/3              → marj DÜŞÜK   → pill'leri onaya düşür
    1/1/1 (dağıldı)  → marj YOK     → adayları göster, cevaplama
    ```

    Ve planın teşhisi: *«garsonun güven sinyali de **HESAPLANIYOR, ama bir KAPIYA
    bağlanmıyor**. Üç oy alınıp çoğunluk seçiliyor; **dağılım atılıyor**.»* Ölçüldü —
    `_select_consistent` `uyum_orani` **döndürüyor**, ama üç yere gidiyordu: uyuşmazlık
    chip'i (1/1/1 hâli · **zaten vardı**), iz notu (*«%67 uyum»* — bir **yazı**, bir kapı
    değil) ve `oylama_cogunluk` bayrağı (**doğrudan koşum**). Yani `2/3` sessizce koşuyordu.

    ## Neden yeni bir gösterim YOK 🆘

    Onay yüzü `§66`'da kuruldu: `source="onizleme"` + `adimlar` + `plan_taslagi`, ve
    `[koş]` `POST /plan/kos`'a **aynı planı** yollar (0 LLM). Tek adımlı bir plan da bir
    plandır (`MIMARI §2.0`) — o yüzden burada üretilen şey ikinci bir kip değil, **aynı
    kipin tek adımlı hâlidir**.

    ⚠ **`KURAL B`:** öngörü katmanı kapalıyken `None` döner ve merdiven bayt bayt bugünkü.
    ⚠ `k <= 1`'de oy **yok**, dolayısıyla kararsızlık da yok: sinyal ölçülmemişse
    ondan bir karar üretmek, ölçmediğini bilmek gibi davranmaktır 🆕.

    ⊘ **Sınır (açık borç 🅖):** plan `§28.1`'de *«pill'ler önerilir»* diyor; bugün
    önizleme adımı **cümle** olarak çiziliyor (*«ort_oee · makine kırılımında»*), pill
    satırı değil. Karar (koşma, sor) doğru; **gösterim** yarım — ve bunu yazmak, tam
    yapılmışmış gibi göstermekten yeğdir.
    """
    from app import plan_semasi
    from app.schemas import AskResponse

    if k <= 1 or uyum >= 1.0 or not cq:
        return None
    if not _features.oneri_katmani_acik(principal):
        return None
    plan = plan_semasi.tek_adim_plani(cq)
    if not plan:
        return None
    _log.info("§28.3: garson kararsız (uyum %.0f%%, %d örnek) → ONAYA düşüyor",
              uyum * 100, k)
    return AskResponse(
        question=soru, source="onizleme", cube_query=cq, plan_taslagi=plan, gecerli=True,
        adimlar=[{"sira": 1, "fiil": x.get("fiil"), "metin": onizleme_satiri(x)}
                 for x in plan["adimlar"]],
        # ⚠ Sayı **beyan edilir**: kullanıcı neden sorulduğunu bilmeden onaylayamaz.
        # ⚠ Ve *«emin değilim»* bir özür değil bir **ölçüdür** — payda da yazılır 🅜.
        note=(f"Bunu anladım ama **emin değilim** (garsonun {k} denemesinden "
              f"%{uyum * 100:.0f}'i aynı sonuca vardı). Koşmadan önce onayla."),
        trace=[f"§28.3: garson kararsız (self-consistency %{uyum * 100:.0f} / {k} örnek) "
               "→ onaya düştü"])
