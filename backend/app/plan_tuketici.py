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
    def _trend(a: dict) -> list[dict]:
        # ⟳ `kaynak`tan `__cq` kazımaya çalışan hâl **kaldırıldı**: satırların içinde
        # sorgusunu taşıyan bir alan hiç yoktu, yani o dal her zaman `{}` veriyordu.
        # *Var olmayan bir alandan okumak, sessizce boş dönmenin en kibar yoludur.*
        from app import yoy
        _td = ((cube_meta or {}).get("time_dimensions") or ["tarih"])[0]
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
             azami_sorgu: int | None = None) -> dict:
    """Planı motora bağlayıp koşar.

    Döner: `plan_kosucu.kos`'un sözleşmesi **+ `sonuclar`** — her `SORGU` adımının TAM
    motor çıktısı (`columns`/`rows`). ⚠ Çalıştırıcı yalnız satırlarla ilgilenir (ilkeller
    satır bekler); sunum katmanı kolonları da ister. İkisini tek dönüşe sıkıştırmak,
    çalıştırıcıya sunumu öğretmek olurdu.
    """
    from app.cube_router import parse_cube_query

    sonuclar: list[dict] = []
    #: 🔴 **ÇÖZÜLMÜŞ** sorgular. Adımdaki `cube_query` bir **referans** olabilir (`"$4"` —
    #: `KIR`/`SUZ`'ün ürettiği sorguyu koşan adım tam olarak öyle yazılır) ve o referansı
    #: cevaba koymak, kartı `/cube` ile yeniden koşulamaz yapardı. Üstelik `AskResponse.
    #: cube_query` bir **sözlük** bekler: canlıda Pydantic `input_value='$4'` diye düştü.
    #: *Bir alanın tipi genişlediğinde, onu okuyan her yer de genişlemelidir.*
    sorgular: list[dict] = []

    def _sorgu_kos(cq: dict) -> list[dict]:
        temiz = parse_cube_query(json.dumps(cq, ensure_ascii=False), index)
        if temiz is None:
            raise plan_kosucu.PlanHatasi(
                f"`{(cq or {}).get('cube') or '?'}` sorgusu katalogda karşılanmıyor "
                "(tanımsız cube/ölçü/boyut)")
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
    return out


def cevap(request: Any, *, service: Any, schema: dict, soru: str, settings: Any = None,
          principal: Any = None, limit: int | None = None) -> dict | None:
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
    plan = _hazir or plan_garson.plan_uret(llm, soru, catalog, index)
    if not plan:
        _log.info("orkestratör: kullanılabilir plan yok → merdiven bugünkü gibi")
        return None
    _n = len(plan["adimlar"])
    try:
        _lower: set[str] = set()
        for c in (schema.get("cubes") or []):
            _lower |= set(c.get("lower_is_better") or [])
        out = calistir(plan, service=service, index=index, schema=schema,
                       cube_meta={"lower_is_better": sorted(_lower)}, limit=limit)
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
    _uyari = ("\n\n⚠ Plan doğru kuruldu ve koştu ama **hiçbir adım satır döndürmedi** — "
              "dönem ya da süzgeç veriyle örtüşmüyor olabilir." if _bos else "")
    return {
        "source": "cube+llm",
        "note": makbuz(plan) + "\n\n" + _bulgu_metni(plan, out) + _uyari,
        "iz": [f"orkestratör: {_n} adımlık plan koştu ({out['sorgu_sayisi']} sorgu)"],
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
        _o = ", ".join(cq.get("measures") or []) or "?"
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
