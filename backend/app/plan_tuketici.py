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

import json
import logging
from typing import Any

from app import plan_kosucu

_log = logging.getLogger("dima.plan_tuketici")


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
        return plan_onarim.gerekce(cq, _spec)

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
          route_hit: dict | None = None) -> dict | None:
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
    plan = (getattr(getattr(request, "state", None), "plan_taslagi", None)
            or plan_garson.plan_uret(llm, soru, catalog, index))
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
        _log.info("orkestratör: kullanılabilir plan yok → merdiven bugünkü gibi")
        return None
    _n = len(plan["adimlar"])
    try:
        _lower: set[str] = set()
        for c in (schema.get("cubes") or []):
            _lower |= set(c.get("lower_is_better") or [])
        out = calistir(plan, service=service, index=index, schema=schema,
                       cube_meta={"lower_is_better": sorted(_lower)}, limit=limit,
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
    from app.plan_semasi import CIKTI_TIPI

    _sorgular = out.get("sorgular") or []
    _bolumler: list[dict] = []
    _sorgu_sirasi = 0
    for adim, cikti in zip(plan["adimlar"], out.get("ciktilar") or []):
        if CIKTI_TIPI.get(adim.get("fiil")) != "satirlar":
            continue
        if adim.get("fiil") == "SORGU":
            _cq = _sorgular[_sorgu_sirasi] if _sorgu_sirasi < len(_sorgular) else None
            _sorgu_sirasi += 1
        else:
            # ⚠ `TREND` gibi fiiller sorgularını **kendileri** koşar; adımın kendi
            # `cube_query`'si o bölümün kimliğidir (referanssa çözülmüş hâli yok —
            # o zaman `None` kalır ve kart yeniden koşulamaz, bu **dürüstçe** böyledir).
            _cq = adim.get("cube_query") if isinstance(adim.get("cube_query"), dict) else None
        _satirlar = [r for r in (cikti or []) if isinstance(r, dict)] \
            if isinstance(cikti, list) else []
        _bolumler.append({"cube_query": _cq,
                          "result": {"columns": list(_satirlar[0]) if _satirlar else [],
                                     "rows": _satirlar, "row_count": len(_satirlar)}})
    _son = _bolumler[-1]["result"] if _bolumler else None
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
    try:
        from app import uyum as _uyum
        for _b in _bolumler:
            _bcq = _b.get("cube_query")
            if not isinstance(_bcq, dict):
                continue
            _bcm = next((c for c in (schema.get("cubes") or [])
                         if c.get("name") == _bcq.get("cube")), None)
            for _ih in _uyum.denetle(soru, {"cube_query": _bcq}, _bcm):
                if _ih.isaret in _karsilanan or _ih.isaret in _gorulen:
                    continue
                _gorulen.add(_ih.isaret)
                _ihlaller.append(_ih)
        _eksik_notu = ("\n\n" + _uyum.kismi_cevap_notu(_ihlaller)) if _ihlaller else ""
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
        "note": makbuz(plan) + "\n\n" + _bulgu_metni(plan, out) + _uyari + _eksik_notu,
        # 🔴 Onarım beyanları izin **başına değil sonuna** eklenir: birinci satır
        # *"kaç adım koştu"* sorusunun cevabıdır ve okuyucunun ilk aradığı odur.
        # Beyan yoksa liste bayt bayt bugünküdür (`KURAL B` disiplini).
        "iz": ([f"orkestratör: {_n} adımlık plan koştu ({out['sorgu_sayisi']} sorgu)"]
               + [f"onarım: {b}" for b in (out.get("onarimlar") or [])]),
        "result": _son,
        "cube_query": (_bolumler[-1]["cube_query"] if _bolumler else None),
        # ⊙ Her `SORGU` adımının TAM sonucu + onu üreten sorgu. `FAZ 6` (frontend adım
        # bileşeni) ve `FAZ 7` (rapor/pano) tüketicisi budur; ikisi de bunsuz kurulamaz.
        # ⚠ `cube_query` her bölümle birlikte taşınıyor ki her adım `/cube` ile **sıfır
        # LLM** yeniden koşulabilsin (`O-5`).
        "bolumler": _bolumler,
        # 🔴 `FAZ 6` — cevabın **yapısı** kullanıcıya taşınır. `agent_run`'dan farkı:
        # o bir denetim izidir (geriye dönük, sonuçsuz), bu **cevabın kendisidir**.
        "plan": {
            "adimlar": [{"sira": i, "fiil": a.get("fiil"), "ozet": _adim_metni(a)}
                        for i, a in enumerate(plan["adimlar"], 1)],
            "bolumler": _bolumler,
        },
    }


def _bulgu_metni(plan: dict, out: dict) -> str:
    """Sorgu-dışı adımların **çıktısını** cümleye çevirir.

    ⚠ Yalnız çalıştırıcının **gerçekten döndürdüğü** sayılar yazılır — `narration_guard`'ın
    kuralının aynısı: eşleşmeyen sayı taşıyan cümle yayımlanmaz. Burada eşleşme
    yapısaldır, çünkü sayı zaten çıktının kendisidir.
    """
    sat: list[str] = []
    for a, c in zip(plan.get("adimlar") or [], out.get("ciktilar") or []):
        if a.get("fiil") == "BAGLA" and isinstance(c, tuple):
            sat.append(f"**{c[0]}** seçildi (`{a.get('olcu')}` = {_b(c[1])}).")
        elif a.get("fiil") == "HESAPLA" and isinstance(c, dict):
            _y = "düşük" if (c.get("fark") or 0) < 0 else "yüksek"
            sat.append(f"Akran ortalaması {_b(c.get('akran_ortalamasi'))} "
                       f"({c.get('akran_sayisi')} akran) — aradaki fark "
                       f"**%{abs(c.get('fark_yuzde') or 0):.1f} {_y}**.")
    return "\n".join(sat)


def _b(x: Any) -> str:
    """Okunabilir sayı. ⚠ `§AA1`'in dersi: ham `float` (`0.5245118291704627`) bir cevap
    değil, bir sızıntıdır."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return str(x)
    if abs(f) >= 1000:
        return f"{f:,.0f}".replace(",", ".")
    return (f"{f:.4g}".rstrip("0").rstrip(".") if f else "0")


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
