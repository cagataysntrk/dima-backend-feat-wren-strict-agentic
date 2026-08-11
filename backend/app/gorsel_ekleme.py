"""**GÖRSEL EKLEME** — cevaba `viz` / `viz_paketi` iliştirme.

## Neden `ask()`'ten ÇIKTI

`ask()` modül tavanını **55 satır** aşmıştı (1206 / 1151). Kapının kuralı:
*"yeni davranışı **modüle çıkar**, tavanı yükseltme. Tavanı yükseltmek kapıyı kapının
kendisiyle çürütür."*

⚠ **Blok büyüklüğüne göre seçilmedi, BAĞIMLILIĞINA göre seçildi.** `_try_fresh_intent`
427 satırdır ama `ask()`'in yerellerine derin bağlıdır; onu taşımak on parametrelik bir
imza üretir ve *"taşındı"* değil **"dağıtıldı"** olurdu.
*Büyüklük bir taşıma ölçütü değildir; bağımlılık öyledir.*

## 🔴 Bağımlılık ölçümü — ve bir önceki denemenin kusuru

İlk deneme **geri alındı** (119 test kırmızı): ölçüm aracım `ast.Name`'leri yalnız
modül-düzeyi *fonksiyon/atama* adlarıyla kıyaslıyordu ve **import edilen adları**
(`cube_router` · `viz` · `AskResponse`) ile kapsayan fonksiyonun **closure**'larını
kaçırıyordu. Modül eksik adlarla doğdu.

> ⚠ *Bir taşımanın güvenliği, taşınacak bloğun bağımlılık ölçümü kadardır — ve o ölçümün
> kendisi de bir bağımlılıktır.*

Yeniden ölçüldü (kapsam zinciri: kendi yerelleri → `ask()` → modül → builtins):

| kaynak | adlar | çözüm |
|---|---|---|
| `ask()` yereli | `schema` · `settings` · `request` · `principal` | **parametre** |
| `ask.py` modülü | `AskResponse` · `cube_router` · `viz` · `_log` | **import** |
| `ask.py` modülü | `_adhoc_store` | **parametre** (`adhoc_coz`) |
| `app.features` | `resolve_for` | **import** — zaten oradan geliyordu |

🔴 `_adhoc_store` **import EDİLMEDİ, parametreye çevrildi**: `ask.py`'de tanımlı ve onu
import etmek **döngüsel bağımlılık** doğururdu. *Bir taşımanın en sık kaçırılan bedeli
döngüsel import'tur; ve o bedel, taşımanın kendisini geri aldırır.*

⚠ Gövde **birebir** taşındı: yalnız `_adhoc_store(` → `adhoc_coz(`. *Bir taşıma, aynı
zamanda bir iyileştirme olmamalıdır — yoksa hangisinin kırdığı ölçülemez.*
"""

from __future__ import annotations

from app import cube_router, viz
from app.features import resolve_for
from app.logging_setup import get_logger
from app.schemas import AskResponse

_log = get_logger("ask")  # ⚠ AYNI ağaç: taşınan kodun log satırları yer değiştirmemeli

def gorsel_ekle(resp: AskResponse, result: dict | None, cq: dict | None = None, *,
                schema: dict, settings, request, principal, adhoc_coz) -> AskResponse:
    """Faz 2d+3 (viz.py↔chart.ts birleştirme, 31 Temmuz 2026): ÖNCEDEN `units={}`/
    `lower_set=[]` SABİT geçiliyordu — `recommend()`'in birim-farkındalığı (facet_measure/
    dual_axis/partition rengi) cube metadata'sında GERÇEK birimler olsa bile HİÇBİR ZAMAN
    devreye giremiyordu (schema zaten `units`/`lower_is_better`'ı taşıyor, ask.py bunu
    yalnız yanlışlıkla kullanmıyordu). Ayrıca `recommend()` istisna fırlatırsa `resp.viz`
    sessizce None kalıyordu ve `result` yine de döndürülüyordu — frontend bu durumda
    `chart.ts`'in KENDİ (daha az yetenekli, `recommend()` katmanı olmayan — bkz. viz.py
    modül docstring'i) yerel `analyze()`'ine düşüyordu: "tek backend-hesaplı spec" hedefinin
    TAM TERSİ bir sessiz-geriye-düşüş. İki düzeltme: (1) gerçek units/lower_set schema'dan
    okunur, (2) recommend() başarısız olursa ÇIPLAK analyze()'e (birim/karşılaştırma
    farkındalığı yok ama HER ZAMAN bir karar) düşülür — resp.viz sonuç doluyken asla None
    kalmaz."""
    # Metadata argümanları `viz.meta_args`'tan gelir (Faz I1) — burada elle
    # toplanmaz. Elle toplama bu dosyada zaten bir `measure_units` yazım hatası
    # üretmişti ve `semi_additive` hiçbir zaman geçirilmemişti.
    cube_meta_for_viz: dict | None = None
    if cq and cq.get("cube"):
        # FAZ 9.9 — AD-HOC CUBE TENANT KATALOĞUNDA YOKTUR. Eskiden yalnız `schema`'ya
        # bakılıyordu → Discovery cevabında `cube_meta` **her zaman None** kalıyordu ve
        # MIMARI §6.2z'nin *"doğru grafik · köken hepsi açıldı"* iddiası **karşılıksız**
        # oluyordu: kapı yeşil, hiçbir şey açılmıyor. `_attach_next_steps` bunu zaten
        # doğru yapıyordu — kural bir tüketiciye öğretilmiş, kardeşine öğretilmemişti
        # (*"kimlik asimetrisi"*, MIMARI §6.1h).
        _sema = schema
        if cq.get("adhoc"):
            _kayit = adhoc_coz(request).get(str(cq.get("adhoc_id") or ""))
            if _kayit and _kayit.get("schema"):
                _sema = _kayit["schema"]
        cube_meta = cube_router._cube_meta(_sema, cq["cube"])
        if cube_meta:
            cube_meta_for_viz = cube_meta
            # Madde 12 (1 Ağustos 2026): KPI-olmayan cube raporları için de düz-dil
            # hesaplama açıklaması — drill.py'nin ZATEN VAR OLAN saf fonksiyonu
            # (önceden yalnız /ask/drill'e bağlıydı) normal /ask cevabına taşınır.
            try:
                from app.drill import formula_explanation

                resp.calculation_explanation = formula_explanation(cq, cube_meta)
            except Exception:
                _log.warning("hesaplama açıklaması üretilemedi (best-effort)",
                            exc_info=True)
            # JOIN SOYAĞACI (Faz 1.3): kullanılan boyutlardan hangileri cube'un KENDİ
            # tablosundan DEĞİL, bir ilişki üzerinden geldi? Ürünün tezi "her sayının
            # kaynağını kanıtlayabilmek"; bir kolon iki tablo öteden geliyorsa bunu
            # kullanıcı GÖRMELİ. `dimension_origin` yalnız ilişki-türevi boyutlarda
            # dolu olduğundan (yerel boyutlarda yok) burası doğal olarak sessiz kalır.
            #
            # 🔴 `§F3` — VE SOYAĞACI ARTIK SERTİFİKAYI DA SÖYLÜYOR. Ölçüldü (2026-08-11):
            # cümle *"…ilişkisi üzerinden geldi (1 sıçrama)"* diyordu ve **orada
            # bitiyordu**; `fanout` sertifikası 31/31 ilişkiyi ölçmüştü ama o ölçüm
            # cevabın **hiçbir yerine** ulaşmıyordu (`"certified" in yanıt` → **False**).
            # Yani kullanıcı bir kolonun iki tablo öteden geldiğini görüyor, o join'in
            # toplamları şişirip şişirmediğini **bilemiyordu**. Beyan kültürünün tam da
            # kapatmak için var olduğu boşluk.
            try:
                from app import fanout as _fanout

                origin = cube_meta.get("dimension_origin") or {}

                def _soyagaci(d: str) -> str:
                    o = origin[d]
                    ad = cube_meta.get("dimension_labels", {}).get(d, d)
                    c = (f"“{ad}” boyutu {o['model']}.{o['column']} kolonundan, "
                         f"{o['relationship']} ilişkisi üzerinden geldi "
                         f"({o.get('hops', 1)} sıçrama)")
                    # ⚠ `certified` damgası `WrenService.schema()`'dan gelir; ad-hoc/eski
                    # şemalarda YOK olabilir → `beyan()` `None` döner ve cümle bugünkü
                    # hâliyle biter. *Eksik bir damga, uydurulmuş bir güvenceden iyidir.*
                    b = _fanout.beyan(o.get("certified"))
                    return f"{c} — {b}." if b else f"{c}."

                satir = [_soyagaci(d) for d in (cq.get("dimensions") or []) if d in origin]
                if satir:
                    resp.calculation_explanation = " ".join(
                        filter(None, [resp.calculation_explanation, *satir]))
            except Exception:
                _log.warning("join soyağacı üretilemedi (best-effort)", exc_info=True)
    try:
        resp.viz = viz.recommend(result, cube_query=cq, **viz.meta_args(cube_meta_for_viz))
        # 🔴 FAZ 5.12 — İÇGÖRÜ PAKETİ. **`resp.viz` DEĞİŞMEZ**: paket AYRI bir alanda
        # (`viz_paketi`) taşınır ve bayrak kapalıyken `None` kalır → tekil kart bugünkü
        # hâliyle görünür (V-5/E-3: **birebir eski davranış**).
        #
        # ⚠ `recommend`i iki kez çağırmak yerine paketin İLK üyesini `resp.viz` yapmak
        # daha "temiz" görünürdü — ama o an tekil dönüşün bayt-bayt aynılığı **bir
        # varsayıma** dönerdi. *Geriye uyumluluk, ikinci bir çağrının maliyetinden
        # ucuzdur.*
        # 🔴 FAZ 5.13a — HAYALET SERİ. Aynı sorgunun bir önceki koşumu.
        # ⚠ Bulunamaması cevabı DÜŞÜRMEZ: hayalet seri bir **ek**tir, bir cevap değil.
        if "ui_knowledge_center" in resolve_for(settings, principal):
            try:
                from app.contracts import ContractStore

                resp.previous_result = ContractStore().find_previous(
                    cq,
                    tenant_id=str(getattr(principal, "tenant_id", "") or "") or None,
                    mdl_version=str(schema.get("version") or ""))
            except Exception:                            # noqa: BLE001
                _log.warning("hayalet seri okunamadı (best-effort)", exc_info=True)
        if "ui_icgoru_paketi" in resolve_for(settings, principal):
            try:
                _pk = viz.recommend(result, cube_query=cq, paket=True,
                                    **viz.meta_args(cube_meta_for_viz))
                resp.viz_paketi = _pk if isinstance(_pk, list) and len(_pk) > 1 else None
            except Exception:                            # noqa: BLE001
                _log.warning("içgörü paketi üretilemedi (best-effort)", exc_info=True)
    except Exception:
        _log.warning("viz önerisi üretilemedi (recommend) — taban analyze()'e düşülüyor",
                    exc_info=True)
        try:
            cols = (result or {}).get("columns") or []
            rows = (result or {}).get("rows") or []
            resp.viz = viz.analyze(cols, rows) if (cols and rows) else None
        except Exception:
            _log.warning("viz taban kararı (analyze) da üretilemedi (best-effort)",
                        exc_info=True)
    return resp
