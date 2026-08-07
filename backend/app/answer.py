"""Cevap kapanış zinciri — **her** yanıtın geçtiği TEK yer (Faz A4).

## Neden ayrı bir modül

Denetimde (2 Ağustos 2026) beş ayrı ihlalin **tek ortak kök nedeni** bulundu:
`ask()` 1180 satırlık bir fonksiyondu ve kapanış zinciri onun içinde bir **closure**
olarak yaşıyordu (`_finish`). Closure `body`/`request`/`principal`/`t0`/`is_followup`'a
kapandığı için:

- **`/cube` kendi paralel zincirini yazmıştı** — `is_new_topic`/`thread_id`/`reply_to_label`
  set etmiyor, contract kaydını `except Exception: pass` ile **sessizce yutuyordu** (ADR-0020
  ihlali; 20 satır aşağıda audit *bilerek* sarılmamıştı — aynı dosyada iki fail politikası).
- **`_try_kpi` zinciri tamamen ATLIYORDU**: `AskResponse`'u doğrudan `return` ediyor →
  contract yok, audit yok, PII maskesi yok.
- **Üç ayrı contract kaydedici** vardı (closure, `/cube` inline, drill).
- Hiçbiri **izole test edilemiyordu**.

`_finish`'in kendi yorumu bu kök nedenin daha önce bir üretim hatası ürettiğini zaten
kaydetmişti (*"`/ask`'ten gelen hiçbir yanıt interpretation/next_steps taşımıyordu"*) —
ama düzeltme yine closure'ın içine yazılmış, dışarı çıkarılmamıştı.

## Sözleşme

**Bir cevap ancak buradan geçerse yayımlanabilir.** Zincir: yorum → sonraki adımlar →
öneriler → açıklama → PII maskesi (+ görüldüyse ayrı audit) → kalıcı sohbet → etkileşim
logu → erişim audit'i → çıkış logu.

Bu aynı zamanda **Faz F'nin (agentic araç kaydı) taşıyıcısıdır**: bir ajan aracının çıktısı,
kullanıcının bir sorusundan daha az denetlenebilir olamaz. Araç ne üretirse üretsin
`seal()`'den geçer — makbuz, iz ve maskeleme garantisi böyle **yapısal** olur, her araca
ayrı ayrı eklenen bir alışkanlık değil.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request

from app.config import get_settings
from app.logging_setup import get_logger
from app.schemas import AskResponse, Explain

_log = get_logger("ask")


def _source_kind(source: str | None) -> str:
    """Ham source → normalize tür (interaction_log facet/filtre):
    cube|llm|rule|upload|vqr|meta|catalog|statement|none|other.

    vqr/meta/catalog LLM'e HİÇ düşmeyen yolları ayırt eder — bu facet olmadan
    "her soru LLM'e mi düşüyor" sorusu loglardan ölçülemez (ADR: strict-agentic
    /ask gözlemlenebilirliği)."""
    s = (source or "").lower()
    if not s:
        return "none"
    if s.startswith("cube"):
        return "cube"
    if s.startswith("vqr"):
        return "vqr"
    if s.startswith("meta"):
        return "meta"
    if s.startswith("catalog"):
        return "catalog"
    if s.startswith("statement"):
        return "statement"
    if s.startswith("llm"):
        return "llm"
    if s.startswith(("rule", "kural")):
        return "rule"
    if s.startswith("upload"):
        return "upload"
    return "other"


# Faz 3 (31 Temmuz 2026) — `explain.path` insan-okur etiketleri, ham `source` ÖNEKİNE göre
# (cube/cube+llm AYRIMI KORUNUR — _source_kind() bunu "cube"da birleştirir, güvenleri farklı
# olduğundan burada AYRI tutulur). `confidence`: yalnız deterministik/yarı-deterministik
# yollarda dolu (LLM/rule'da UYDURMA bir sayı yerine None — "ölçülebilir güven yok" dürüstçe).
_EXPLAIN_PATH = {
    "cube": ("cube (route() — LLM'siz, sıfır maliyet)", 1.0),
    "cube+llm": ("cube + LLM-destekli alan seçimi (SQL değil Intent-JSON)", 0.85),
    "vqr": ("önceden doğrulanmış sorgu (VQR) — LLM'siz tekrar oynatma", 0.95),
    "statement": ("yapısal finansal tablo (gelir tablosu/bilanço) — LLM'siz", 1.0),
    "meta": ("meta/karşılama sorusu — LLM'siz", 1.0),
    "catalog": ("katalog/kapsam sorusu — LLM'siz", 1.0),
    "rule": ("kural-tabanlı NL→SQL (anahtarsız LLM yedeği)", None),
}


def _build_explain(resp: AskResponse) -> Explain | None:
    """`resp` üzerinde ZATEN oturan alanlardan (source/cube_query/trace) EKLEYİCİ bir
    `Explain` sentezler — yeni bir hesaplama/yan-etki YOK, salt post-hoc özetleme. `source`
    yoksa (netleştirme/chip/dürüst-ret gibi rapor ÜRETMEYEN yanıtlar) None döner — bu
    yanıtlarda zaten açıklanacak bir "yol" yok."""
    s = (resp.source or "").lower()
    if not s:
        return None
    if s.startswith("llm"):
        path, confidence = f"LLM (ham SQL, Discovery) — {s}", None
    else:
        # EN UZUN ÖNEK KAZANIR — `next(...)` İLK eşleşeni alıyordu ve sözlükteki sıra
        # `cube` → `cube+llm` olduğu için `"cube+llm".startswith("cube")` **True** dönüp
        # her Intent-JSON cevabı `cube` dalına düşüyordu.
        #
        # ⚠️ CANLI LLM İLE BULUNDU (2026-08-03). Sonucu iki KATLI bir yanlış beyandı:
        #   * `confidence` **1.0** (olması gereken 0.85) — Intent-JSON cevabı, saf
        #     deterministik `route()` cevabıyla AYNI güven rozetini alıyordu;
        #   * `path` **"cube (route() — LLM'siz, sıfır maliyet)"** — oysa LLM
        #     `consistency_k=3` ile ÜÇ KEZ çağrılmıştı. Yani kullanıcıya *"LLM
        #     kullanılmadı"* deniyordu.
        #
        # Bu tam olarak §6.1'in "beyan var, kod onu tanımıyor" sınıfı ve **yalnız gerçek
        # bir sağlayıcıyla görülebilirdi**: CI reçetesi `--network none` olduğu için
        # `cube+llm` test ortamında HİÇ üretilmiyor, dolayısıyla hiçbir test bu yolu
        # koşturmuyordu. Sözlüğün kendi yorumu ayrımı *"güvenleri farklı olduğundan
        # burada AYRI tutulur"* diye BEYAN ediyordu — kod onu uygulamıyordu.
        prefix = max((k for k in _EXPLAIN_PATH if s.startswith(k)), key=len, default=None)
        if prefix is None:
            return None
        path, confidence = _EXPLAIN_PATH[prefix]

    assumptions: list[str] = []
    cq = resp.cube_query or {}
    if cq.get("period_confirmed") and not any(
        f.get("dimension") in ("tarih", "donem", "dönem") for f in (cq.get("filters") or [])
    ):
        assumptions.append(
            "Dönem açıkça belirtilmedi — kullanıcı \"tüm zamanlar\"ı seçti/onayladı "
            "(filtresiz, tüm-zamanlar toplama)."
        )
    # Faz 4.13a (1 Ağustos 2026) — dış yol haritası 2.17 "güven rozeti": sessiz bir
    # varsayım yapıldıysa (yukarıdaki `assumptions`, ör. "tüm zamanlar" otomatik seçildi)
    # güven bir kademe DÜŞÜRÜLÜR — aynı `source`'tan gelen ama varsayımsız bir yanıttan
    # daha az kesin kabul edilir (frontend'in 🥇/🥈/🥉 rozetinin ayırt edebileceği somut
    # bir sinyal). `confidence=None` olan yollarda (LLM/rule — zaten "ölçülemez") dokunulmaz.
    if assumptions and confidence is not None:
        confidence = round(max(0.0, confidence - 0.15), 2)

    return Explain(path=path, confidence=confidence, assumptions=assumptions)


_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
_UPLOAD_DIR = _LOG_DIR / "uploads"  # chat-scoped yüklenen veri (ephemeral, oturum DuckDB'si)
_MAX_UPLOAD = 25 * 1024 * 1024      # 25 MB — DuckDB bellek-içi ingest sınırı


def _uuid_or_none(val):
    """`app/routers/ask.py`'den taşındı — `_log_interaction`'ın tek bağımlılığı."""
    import uuid as _uuid

    try:
        return _uuid.UUID(str(val)) if val else None
    except (ValueError, AttributeError, TypeError):
        return None


def _bosluk_kaydi(request, body, resp) -> dict:
    """🔴 KÖK-8a — cevap gelmediyse **NEDEN gelmediğini** kelime düzeyinde kaydet.

    Sözlük boşluğu bugün tahminle kapatılıyor; bu, onu **ölçüme** çevirir:
    *"bu ay 412 soru `sattık` yüzünden düştü"*.

    ⚠ Yalnız cevap YOKKEN yazılır (`resp.source is None`): dolu bir cevapta bu iki
    kolon gürültüdür ve her isteğe bir katalog taraması maliyeti bindirirdi.

    ⚠ Ve **best-effort**: telemetri bir cevabı asla düşürmez.
    """
    if resp.source is not None:
        return {}
    try:
        from app import cube_router
        from app.company_registry import wren_for_request

        schema = wren_for_request(request).schema()
        q = body.question or ""
        bilinmeyen, _ = cube_router.partial_unknowns(q, schema)
        adaylar = [c.get("name") for c, _m in cube_router.measure_cube_candidates(q, schema)]
        return {
            "uncovered_words": json.dumps(sorted(bilinmeyen), ensure_ascii=False) or None,
            "aday_cubelar": json.dumps(sorted(x for x in adaylar if x), ensure_ascii=False) or None,
        }
    except Exception:                       # noqa: BLE001 — telemetri cevabı DÜŞÜRMEZ
        _log.warning("boşluk kaydı üretilemedi (best-effort)", exc_info=True)
        return {}


def _log_interaction(session_id: str | None, body: AskRequest, resp: AskResponse,
                     dur_ms: int, principal=None, request=None) -> None:
    """Her etkileşimi `interaction_log` DB tablosuna yazar — TEK KAYNAK (ADR-0020).

    JSONL kaldırıldı (redundancy): admin viewer AYRI servis (ADR-0015) → Postgres ortak store'dan
    okur (volume çapraz-servis çalışmaz); synonym-madencisi de DB'den okur. Ürün geliştirme +
    KVKK erişim-izi + log→golden madenciliği tek yerden. Ham SONUÇ satırı TUTULMAZ (yalnız
    türetilmiş meta). Best-effort — hata yanıtı düşürmez, system-log'a yazar."""
    try:
        if not get_settings().interaction_log:
            return  # test/eval koşumu — canlı log kirletilmez
        from sqlmodel import Session

        from control_plane.db import engine
        from control_plane.models import InteractionLog

        def _j(v):
            return json.dumps(v, ensure_ascii=False) if v else None

        from app.cube_router import teshis as _teshis
        from app.llm import get_llm_usage

        _u = get_llm_usage() or {}  # yalnız LLM yoluna düşen istekte dolu; aksi halde boş
        with Session(engine) as s:
            s.add(InteractionLog(
                session_id=session_id, user_id=_uuid_or_none(getattr(principal, "user_id", None)),
                tenant_id=_uuid_or_none(getattr(principal, "tenant_id", None)), question=body.question,
                source=resp.source, kind=_source_kind(resp.source), follow_up=bool(body.cube_query),
                sql=resp.sql or None, rows=resp.result.row_count if resp.result else None,
                note=resp.note, duration_ms=dur_ms, cube_query_json=_j(resp.cube_query),
                trace_json=_j(resp.trace), interpretation_json=_j(resp.interpretation),
                llm_model=_u.get("model"), llm_input_tokens=_u.get("input_tokens"),
                llm_output_tokens=_u.get("output_tokens"), llm_latency_ms=_u.get("latency_ms"),
                # RED GEREKÇESİ (Faz 0): `route()` pes ettiyse HANGİ dalda. Deterministik
                # yol cevabı ürettiyse `None` kalır — yani bu kolonun doluluğu doğrudan
                # "deterministik yoldan çıkamayan sorular" kümesini verir.
                # 🔴 KÖK-9/KÇ-5 (2026-08-06): `red_gerekcesi()` DEĞİL `teshis()`. Ölçüldü:
                # 2 116 reddin **%43,2'sinde** ham kapı kodu (çoğu R1) ile gerçek sorun
                # (tanınmayan kelime) AYRIŞIYORDU — ve bu kolonu okuyan araçlar
                # (`lab/r1_envanteri.py` · `lab/risk_kapsam.py`) GELİŞTİRME ÖNCELİĞİNİ
                # ona göre çıkarıyordu. *Kusuru gizlemekten daha kötüsü, yanlış yeri
                # işaret etmektir* — burada yanlış yer gösterilen geliştiriciydi.
                reject_reason=_teshis(body.question, _sema(request)),
                **_bosluk_kaydi(request, body, resp)))
            s.commit()
    except Exception:
        _log.warning("interaction log (DB) yazılamadı (best-effort)", exc_info=True)


def _sema(request: Request) -> dict:
    """İstek şeması — okunamazsa **boş sözlük**.

    ⚠ Teşhis hesabı bir kayıt yazarken koşuyor: şema okunamıyorsa telemetriyi kaybetmek
    yerine ham koda düşmek doğrudur (`teshis()` boş şemada `partial_unknowns` üzerinden
    ham koda döner). *Bir kayıt satırı, kaydettiği şeyden daha kırılgan olmamalıdır.*
    """
    # ⚠ İçeride import: `wren_for_request` bu modülde HER YERDE yerel olarak alınıyor
    # (bkz. `:177`, `:309`) — modül düzeyine çekmek bir import döngüsü riskidir.
    # 🔴 İlk yazımda unutuldu ve `NameError` **sessizce yutuldu**: çağıran blok
    # `except Exception` ile sarılı bir "best-effort" kayıttır, yani ETKİLEŞİM KAYDI
    # TAMAMEN YAZILMADI ve hiçbir yerde iz kalmadı. `test_kok8a_bosluk_kaydi` yakaladı.
    # *En tehlikeli hata, bir hata yolunun içinde doğan hatadır.*
    from app.company_registry import wren_for_request

    try:
        return wren_for_request(request).schema() or {}
    except Exception:                        # ADR-0020: sessiz yutma yok
        _log.warning("teşhis için şema okunamadı", exc_info=True)
        return {}


def _persist_message(request: Request, resp: AskResponse, session_id: str | None) -> None:
    """Yanıtı kalıcı sohbete yazar (per-user, tenant-izole). find-or-create Conversation
    (user_id × session_id) → ConversationMessage(tam AskResponse payload). Best-effort —
    asla yanıtı düşürmez. Resume: kayıtlı payload'ları yeniden render (yeniden çalıştırma yok)."""
    principal = getattr(request.state, "principal", None)
    if principal is None or not session_id or not getattr(principal, "user_id", None):
        return
    try:
        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import Conversation, ConversationMessage

        with Session(engine) as s:
            conv = s.exec(select(Conversation).where(
                Conversation.user_id == principal.user_id,
                Conversation.session_id == session_id)).first()
            if conv is None:
                conv = Conversation(tenant_id=getattr(principal, "tenant_id", None),
                                    user_id=principal.user_id, session_id=session_id)
                s.add(conv); s.flush()
            q = resp.question or ""
            if not conv.title and q and not q.startswith(("chip:", "📎")):
                conv.title = q[:80]
            s.add(ConversationMessage(conversation_id=conv.id, seq=conv.message_count,
                                      question=q, payload_json=resp.model_dump_json()))
            conv.message_count += 1
            conv.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            s.add(conv); s.commit()
    except Exception:  # noqa: BLE001 - persistence best-effort (yanıtı düşürmez)
        _log.warning("konuşma kaydı yazılamadı (best-effort)", exc_info=True)


def _maybe_interpret(request: Request, resp: AskResponse) -> None:
    """EVRENSEL ÇIKTI YORUMU — feature flag 'cikti_yorumlama' açıksa resp.interpretation'a
    DETERMİNİSTİK data-güdümlü yorum ekler (her tablo/grafik/rapor/KPI). Bayrak kapalı →
    dokunmaz (admin panelden kim görür kararlaştırılır). Ham veri LLM'e GİTMEZ (yerel analiz)."""
    if resp.interpretation is not None or (resp.result is None and resp.kpi is None):
        return
    principal = getattr(request.state, "principal", None)
    try:
        from app.features import resolve_for
        if "cikti_yorumlama" not in resolve_for(get_settings(), principal):
            return
        from app.interpret import interpret
        units: dict[str, str] = {}
        lower_is_better: set[str] = set()
        # Cevabın KENDİ cube'unun metadata'sı: `interpret` toplanabilirliği buradan
        # okur (`non_additive`/`semi_additive`/`measure_expressions`). AYNI döngüden
        # alınır — ikinci bir şema arama mekanizması AÇILMAZ (KAT-1).
        cube_meta: dict | None = None
        etiketler: dict[str, str] = {}
        aranan = (resp.cube_query or {}).get("cube")
        try:
            from app.company_registry import wren_for_request
            for c in wren_for_request(request).schema().get("cubes") or []:
                units.update(c.get("units") or {})
                lower_is_better.update(c.get("lower_is_better") or [])  # DSO/CCC/fire… yönü
                if aranan and c.get("name") == aranan:
                    cube_meta = c
        except Exception:
            pass

        # ⚠️ FAZ 0.10b — ETİKETLER **TEK KAYNAKTAN**: `build_catalog` →
        # `measure_synonyms_display` / `dimension_labels`. `eylem._rapor_adi` ve
        # `cube_router.next_step_chips` ile **aynı** kaynak. `eylem.py`'nin kendi
        # uyarısı: *"bu depoda «ikinci bir etiket kaynağı» deseni **beş kez**
        # ayrışmayla sonuçlandı"* — burada da açılmaz. Yeni I/O yok: döngü zaten
        # `units`/`lower_is_better` için dönüyordu.
        if aranan:
            try:
                from app.cube_router import build_catalog

                _, _idx = build_catalog(wren_for_request(request).schema())
                _spec = _idx.get(aranan) or {}
                etiketler = {**(_spec.get("measure_synonyms_display") or {}),
                             **(_spec.get("dimension_labels") or {})}
            except Exception:                              # noqa: BLE001
                _log.warning("etiket sözlüğü kurulamadı (best-effort)", exc_info=True)
        # 🔴 G1 — TEMELLENDİRME aynı etiket sözlüğünü kullanır. İkinci bir `build_catalog`
        # çağrısı YAPILMAZ: bu bloğun kendi yorumu *"ETİKETLER TEK KAYNAKTAN"* diyor ve
        # ikinci bir kaynak, zamanla ayrışan iki ad kümesi doğururdu.
        resp._etiketler = etiketler          # type: ignore[attr-defined]
        if resp.kpi and resp.kpi.get("lower_is_better"):
            lower_is_better.add(resp.kpi.get("kpi"))  # KPI ölçüsü (CCC gibi) düşük=iyi
        # EŞİK KIYASI (Faz G3). Kaynak KULLANICININ KENDİ kurduğu alarmlardır — cube
        # metadata'sında `target:` beyanı hiçbir cube'da yok (ölçüldü) ve demo için hedef
        # uydurmak GÜVENLE YANLIŞ bir sayı üretirdi. Burada olmasının sebebi: `_maybe_interpret`
        # TEK kapanış zincirinin parçası, yani /ask · /cube · /report · drill · katkı —
        # HEPSİ bu kıyası bedava alır ve UI'da YENİ BİR YÜZEY AÇILMAZ (sinyal zaten
        # InterpretationBar'da render ediliyor).
        esikler: list[dict] = []
        try:
            from app.schedules import kullanicinin_esikleri
            store = getattr(request.app.state, "schedules", None)
            if store is not None and resp.cube_query:
                esikler = kullanicinin_esikleri(
                    store, (resp.cube_query or {}).get("cube"),
                    (resp.cube_query or {}).get("measures"),
                    tenant_id=getattr(principal, "tenant_id", None))
        except Exception:
            _log.warning("eşik kıyası okunamadı (best-effort)", exc_info=True)
        resp.interpretation = interpret(
            resp.result.model_dump() if resp.result else None,
            resp.cube_query, resp.kpi, units, lower_is_better, esikler=esikler,
            cube_meta=cube_meta, etiketler=etiketler)
    except Exception:  # noqa: BLE001 - yorum best-effort (yanıtı düşürmez)
        _log.warning("çıktı yorumu üretilemedi (best-effort)", exc_info=True)
    _anlati_ekle(request, resp)


def _anlati_makbuzu(resp: AskResponse, plan) -> None:
    """T2 anlatıcının adımını `agent_run` makbuzuna **ekler** — varsa EZMEZ.

    FAZ 9.8. Makbuzun tek amacı *"LLM ne zaman devreye girdi"* sorusunu cevaplamaktır;
    ajan koşumunun adımlarını silip yerine tek bir anlatı adımı yazmak, o soruyu
    cevaplamak yerine **yanıltırdı**. Bu yüzden birleştirme yapılır ve `step_count`
    yeniden hesaplanır.
    """
    try:
        yeni = (plan.kosum.makbuza() or {}).get("agent_run") or {}
        mevcut = resp.agent_run
        if not mevcut:
            resp.agent_run = yeni
            return
        adimlar = [*(mevcut.get("steps") or []), *(yeni.get("steps") or [])]
        resp.agent_run = {**mevcut, "steps": adimlar, "step_count": len(adimlar)}
    except Exception:  # noqa: BLE001 — makbuz cevabı DÜŞÜRMEZ
        _log.warning("T2 anlatı makbuzu iliştirilemedi", exc_info=True)


def _anlati_ekle(request: Request, resp: AskResponse) -> None:
    """FAZ 5 — T2 GUARDED LLM ANLATICI (§4.4): *"LLM ÜSLUBU yazar, SAYIYI sistem koyar."*

    ## Neden bu faz en sona konuldu

    Önce cevapların DOĞRU gelmesi, sonra GÜZEL anlatılması. "Güzel ama yanlış" bir anlatı,
    şablon bir doğrudan **kötüdür** — süs, hatayı görünmez yapar.

    ## Ne YAPMAZ

    Girdi olarak **yalnız** `interpret()`'in ZATEN HESAPLADIĞI, deterministik olgular
    verilir. Model SQL yazmaz, sayı hesaplamaz, cube seçmez, ham satır görmez. İşi salt
    **üslup**tur.

    ## FAIL-CLOSED — bu fonksiyonun varlık sebebi

    Çıktı `narration_guard.guvenli_anlatim`'dan **zorunlu** geçer: her cümledeki her sayı
    sonuç kümesiyle eşlenir (±%2, kapalı türetme listesi), eşleşmeyen cümle **düşer**.
    Hiçbir cümle sağ kalmazsa **anlatı hiç eklenmez** — deterministik `summary` yerinde
    kalır. Yani en kötü durum "süssüz ama doğru", asla "akıcı ama uydurma" değildir.

    ## ŞABLONU EZMEZ — üstüne biner

    Anlatı `interpretation["narration"]` alanına yazılır; `summary`/`facts` **aynen
    kalır**. Bu, §4.4'ün kullanıcı tarafından açıkça istenen iki şartının doğrudan
    karşılığıdır: *"her zaman grafik değil, bazen mesele sadece konuşmaktır"* korunur ve
    *"o konuşmayı grafiğe çevir"* çalışır, çünkü altındaki yapı (`cube_query`/`result`/
    `summary`) **hiçbir zaman silinmez**. Faz 0.5 bu şartın bir yerde İHLAL edildiğini
    ölçüp düzeltmişti (`gorunum_donusumu` 0/5 → 4/5).
    """
    yorum = resp.interpretation
    if not yorum or yorum.get("narration"):
        return
    principal = getattr(request.state, "principal", None)
    try:
        from app.features import resolve_for
        if "t2_anlatici" not in resolve_for(get_settings(), principal):
            return                      # KURAL B — kapalıyken davranış BİREBİR bugünkü
        llm = getattr(request.app.state, "llm", None)
        if llm is None or not hasattr(llm, "anlat"):
            return                      # kural-tabanlı sağlayıcı: YOL KAPALI, hata DEĞİL
        gercekler = [f["text"] for f in (yorum.get("facts") or [])
                     if isinstance(f, dict) and f.get("text")]
        if not gercekler:
            return
        from app.narration_guard import guvenli_anlatim

        # FAZ 9.8 — ÇAĞRI PLANLAYICIDAN GEÇER. MIMARI §12.6b *"prompt-enhancer için
        # koşulan şart (kapısız LLM çağrısı olmasın; makbuzda ADIM olarak görünsün)
        # anlatıcı için de uygulandı"* diyordu; kayıt (`tools.KAYIT`) doğruydu ama
        # ÇAĞRI doğrudandı — yani beyanın ikinci yarısı **karşılıksızdı**. Denetimde
        # bulundu; bu deponun on dört kez avladığı *"beyan var, kod onu tanımıyor"* sınıfı.
        #
        # Kapıların burada gerçek karşılığı: **bütçe** (sıcak yola giren LLM çağrısı
        # sayılır) ve **makbuz** (*"LLM ne zaman devreye girdi"* cevaplanabilir olur).
        from app import planner as _planner

        plan = _planner.Planlayici(
            principal=principal,
            butce=_planner.Butce(adim=2, saniye=15.0, sorgu=0),
            kaynaklar={"servis:llm": llm},
        )
        # DETERMİNİSTİK-ÖNCE kapısı: `interpret` (aynı `anlatim` etiketinin LLM'siz
        # kardeşi) planlayıcı ÜZERİNDEN denenmiş olmalı. Zaten çalıştı — çıktısı bu
        # fonksiyonun GİRDİSİ — ama kapı **kendi kaydını** görmelidir; "denendi" demek
        # yetmez, yoksa kapı bir yorumdan ibaret kalır (enhancer'da verilen aynı karar).
        # Maliyeti sıfır: `interpret` veriye dokunmaz, eldeki sonucu okur.
        plan.calistir("interpret", resp.result.model_dump() if resp.result else None,
                      resp.cube_query)

        # 🔴 G0b — HAVA BOŞLUĞU. Fact-Sheet'te GERÇEK boyut değerleri ve GERÇEK sayılar
        # var (`interpret.py:248` → *"En yüksek Makine: RAM 3 (12.430 kg)"*); ikisi de
        # PII kalıbı DEĞİL, yani `llm_guard` onları görmez ve dış sağlayıcıya olduğu gibi
        # giderlerdi. Perdeleme onları yer tutucuya çevirir: model gerçek değeri **hiç
        # görmez** ve bir rakam **üretemez** — yalnız verdiğimiz yuvayı taşıyabilir.
        from app.yayilim import geri_koy, perdele

        gercekler, _harita = perdele(gercekler, degerler=_boyut_degerleri(resp))
        ham = plan.calistir("llm.anlat", resp.question, gercekler)
        _anlati_makbuzu(resp, plan)
        ham, _yayilim_sorunlari = geri_koy(ham or "", _harita)
        if _yayilim_sorunlari:
            # Model yuvayı bozduysa ya da UYDURDUYSA cümle güvenilmezdir. Sessizce
            # geri koymak, bozulmuş bir cümleyi doğru göstermek olurdu.
            _log.info("T2 anlatı YAYILIM BOZULDU (%d): %s",
                      len(_yayilim_sorunlari), ", ".join(_yayilim_sorunlari[:5]))
        resp.hava_boslugu = {"yer_tutucu": len(_harita),
                             "bozulan": len(_yayilim_sorunlari)}

        metin, rapor = guvenli_anlatim(
            ham, resp.result.model_dump() if resp.result else None, yedek=None)
        if not metin:
            # Tüm cümleler düştü — sessizce geç. Deterministik `summary` zaten orada.
            _log.info("T2 anlatı GUARD'DA DÜŞTÜ (yayımlanmadı): reddedilen=%d",
                      len(getattr(rapor, "reddedilen", []) or []))
            return
        yorum["narration"] = metin
        if getattr(rapor, "reddedilen", None):
            # Kısmi düşüş de GÖRÜNÜR olmalı — sessiz kırpma yok (bu deponun disiplini).
            _log.info("T2 anlatı: %d cümle guard'da düştü",
                      len(rapor.reddedilen))
    except Exception:  # noqa: BLE001 — anlatı SÜStür, cevabı asla düşürmez
        _log.warning("T2 anlatı üretilemedi (best-effort)", exc_info=True)


def _boyut_degerleri(resp) -> list[str]:
    """Sonuç satırlarındaki **gerçek boyut değerleri** — perdelemenin girdisi (`G0b`).

    Yalnız `cube_query.dimensions`'ta ilan edilmiş kolonlar okunur: ölçü kolonları
    zaten sayıdır ve sayı taraması onları **zaten** perdeler. Boyut değerleri ise
    (`"RAM 3"` · `"Ahmet Tekstil A.Ş."`) hiçbir kalıba uymaz — bu liste olmadan
    perdeleme onları göremez.
    """
    try:
        r = resp.result.model_dump() if resp.result else None
        satirlar = (r or {}).get("rows") or []
        boyutlar = [str(d) for d in ((resp.cube_query or {}).get("dimensions") or [])]
        if not satirlar or not boyutlar:
            return []
        kisa = {b.split(".")[-1] for b in boyutlar} | set(boyutlar)
        out: list[str] = []
        for s in satirlar[:200]:                      # üst sınır: perdeleme O(n·m)
            if not isinstance(s, dict):
                continue
            for k, v in s.items():
                if k in kisa and isinstance(v, str) and v.strip():
                    out.append(v)
        return out
    except Exception:                                  # noqa: BLE001 — best-effort
        _log.warning("boyut değerleri okunamadı; perdeleme yalnız SAYI yapacak",
                     exc_info=True)
        return []


def _temellendir(resp: AskResponse) -> None:
    """🔴 `G1` — cevap **ne anladığını söyler**. 0 LLM · 0 token.

    ⚠ **Beyan kanalı PAYLAŞILIR:** `uyum.kismi_cevap_notu` bir ihlal bulduğunda zaten
    konuşuyor (`beyanli_kismi`). Bu, o kanalın **eksik yarısıdır** — sistem yanıldığını
    söylüyordu, anladığını söylemiyordu. İkinci bir beyan üreteci YAZILMAZ.

    🔴 **0 token olması bir tasarım özelliğidir:** LLM tamamen düşse bile (kota · ağ ·
    429) bu satır **yine basılır** — bozulma merdiveninin 3. basamağı.
    """
    if resp.source is None or not resp.cube_query:
        return          # ret/netleştirme cevabında temellendirilecek bir sorgu YOK
    try:
        from app.temellendirme import kur

        resp.temellendirme = kur(
            resp.cube_query,
            katalog=getattr(resp, "_etiketler", None),
            cube_etiketi=(resp.cube_query or {}).get("cube"))
    except Exception:                                      # noqa: BLE001 — best-effort
        _log.warning("temellendirme kurulamadı (cevap etkilenmez)", exc_info=True)


def _adhoc_kayit(request: Request, cq: dict | None) -> dict | None:
    """Ad-hoc cube kaydı (FAZ 1 / K1) — yoksa None. `ask.py::_adhoc_store` ile AYNI depo;
    burada import döngüsü olmasın diye `app.state`'ten doğrudan okunur."""
    if not isinstance(cq, dict) or not cq.get("adhoc"):
        return None
    return (getattr(request.app.state, "adhoc_cubes", None) or {}).get(
        str(cq.get("adhoc_id") or ""))


def _attach_next_steps(request: Request, resp: AskResponse) -> None:
    """K2 (rehberli analitik) — başarılı rapora DETERMİNİSTİK 'sonraki adım' chip'leri ekler
    (feature flag 'next_steps'): kullanılmayan boyut (kırılım) / ölçü (ölçek) / zaman
    granülerliği. Katalogdan türetilir (LLM yok); her chip TAM cube_query taşır → FE /cube
    ile LLM'siz koşar. Bayrak kapalı → dokunmaz."""
    if not resp.cube_query or resp.result is None:
        return
    principal = getattr(request.state, "principal", None)
    try:
        from app.features import resolve_for
        if "next_steps" not in resolve_for(get_settings(), principal):
            return
        from app import cube_router
        from app.company_registry import wren_for_request
        from app.schemas import NextStep

        cq = resp.cube_query
        # FAZ 1 (K1) — KIRPILMIŞ GÖRÜNÜMDE TOPLAMA CHIP'İ YOK.
        # Ad-hoc cube `max_result_rows` tavanına DEĞMİŞ bir sonuçtan kurulduysa, o görünüm
        # üzerindeki HER toplama (ölçü değiştir, kırılım ekle, zaman kovala) eksik veriden
        # hesaplanır ve **kendinden emin ama yanlış** çıkar — planın kendi *"en tehlikeli
        # sınıf"* tanımı, yeni bir kapıdan. Kırılım da güvenli DEĞİLDİR: 1000 kırpılmış
        # satırı gruplamak kısmi toplam verir. Bu yüzden chip'lerin TAMAMI kapatılır ve
        # kullanıcı sebebini görür (sessizce eksik chip, chipsizlikten kötüdür).
        if cq.get("kirpilmis"):
            resp.note = ((resp.note + " ") if resp.note else "") + (
                "Kırpılmış görünüm (satır tavanına ulaşıldı) — bu sonuç üzerinden "
                "toplama/kırılım önerilmiyor, sayılar eksik veriden hesaplanırdı.")
            return

        adhoc = _adhoc_kayit(request, cq)
        if adhoc is not None:
            # Ad-hoc cube TENANT KATALOĞUNDA YOK; şemasını kendi servisinden okumak
            # zorunludur, yoksa index'te bulunamaz ve chip'ler sessizce üretilmez.
            cubes = adhoc["schema"].get("cubes") or []
        else:
            cubes = wren_for_request(request).schema().get("cubes") or []
        index = {c.get("name"): c for c in cubes}
        adimlar = cube_router.suggest_next_steps(cq, index)
        if adhoc is not None and adhoc.get("maskeli_kolonlar"):
            # MASKELEME SIRASI (planın 3. risk maddesi): cube MASKELİ satırlardan kuruldu,
            # yani `Ahm** Y***` değerine filtre/kırılım kuran bir chip BOŞ ya da anlamsız
            # döner. `schedules.uyari_nedeni`'nde verilen aynı karar: boş dönen bir chip
            # sunmak, hiç sunmamaktan KÖTÜDÜR.
            gizli = adhoc["maskeli_kolonlar"]
            adimlar = [s for s in adimlar
                       if not (set((s.get("cube_query") or {}).get("dimensions") or []) & gizli)]
        resp.next_steps = [NextStep(**s) for s in adimlar]
    except Exception:  # noqa: BLE001 - best-effort (yanıtı düşürmez)
        _log.warning("sonraki adım önerileri üretilemedi (best-effort)", exc_info=True)


def _attach_recommendations(request: Request, resp: AskResponse) -> None:
    """K4 (karar motoru) — K3 sinyallerinden AKSİYON önerileri türetir: her sinyal 'neye
    bakmalısın'a çevrilir; trend/anomali için 'sürükleyeni bul' drill'i eklenir (K2 reuse).
    Sinyal yoksa dokunmaz (dolayısıyla cikti_yorumlama flag'ine bağlı). Deterministik."""
    signals = (resp.interpretation or {}).get("signals") if resp.interpretation else None
    if not signals or not resp.cube_query:
        return
    try:
        from app import cube_router
        from app.company_registry import wren_for_request
        from app.schemas import NextStep, Recommendation

        # FAZ 9.9 — AD-HOC CUBE TENANT KATALOĞUNDA YOK. Eskiden `spec` her Discovery
        # cevabında **None** kalıyordu; §6.2z'nin *"aksiyon önerisi açıldı"* iddiası
        # karşılıksızdı. `_attach_next_steps` bunu zaten doğru yapıyordu — aynı kural,
        # kardeş dalda uygulanmamıştı.
        adhoc = _adhoc_kayit(request, resp.cube_query)
        if adhoc is not None:
            cubes = adhoc["schema"].get("cubes") or []
        else:
            cubes = wren_for_request(request).schema().get("cubes") or []
        spec = next((c for c in cubes if c.get("name") == resp.cube_query.get("cube")), None)
        resp.recommendations = [
            Recommendation(text=r["text"],
                           action=NextStep(**r["action"]) if r.get("action") else None)
            for r in cube_router.recommend_actions(signals, resp.cube_query, spec)
        ]
    except Exception:  # noqa: BLE001 - best-effort (yanıtı düşürmez)
        _log.warning("öneriler üretilemedi (best-effort)", exc_info=True)



def koken(service, cube_query: dict | None) -> dict | None:
    """Cevabın KÖKEN kanıtı (Faz D2): hangi kırılım hangi join'den geldi, o join ölçüldü mü?

    Query Contract bugüne kadar *"hangi sayı, hangi SQL, hangi şema sürümü"* diyordu.
    Cevaplayamadığı soru **"bu kırılıma neden güveneyim"**dı — oysa fan-out riski tam
    orada yaşar: beyan yanlışsa sonuç hatasız, uyarısız ve `source="cube"` rozetiyle
    şişmiş gelir (`wren_core` `join_type`'ı OKUMAZ — ölçüldü).

    `None` döner (ve makbuza kolon yazılmaz) eğer cevap **hiç** ilişki-türevi boyut
    kullanmıyorsa: köken sorusu o zaman anlamsızdır ve boş bir sözlük yazmak *"köken
    bakıldı ve yoktu"* ile *"köken hiç sorulmadı"*yı karıştırırdı.
    """
    dims = (cube_query or {}).get("dimensions") or []
    cube_adi = (cube_query or {}).get("cube")
    if not dims or not cube_adi:
        return None
    try:
        cube = next((c for c in (service.schema().get("cubes") or [])
                     if c.get("name") == cube_adi), None)
    except Exception:                       # ADR-0020: sessiz yutma yok
        _log.warning("köken çözümlenemedi (best-effort) — cube=%s", cube_adi, exc_info=True)
        return None
    origins = (cube or {}).get("dimension_origin") or {}
    kayit = {d: origins[d] for d in dims if d in origins}
    return {"dimensions": kayit} if kayit else None


def _provenance(service, cube_query: dict | None, baglam) -> dict | None:
    """Makbuzun KÖKEN bloğu: *"bu cevap nereden geldi?"* — iki yüzü birlikte.

    **Köken** (Faz D2) hangi kırılımın hangi join'den geldiğini ve o join'in ölçülüp
    ölçülmediğini söyler. **Bağlam** (Faz G5) cevabın hangi çapaya, hangi KURALA göre
    bağlandığını söyler. İkisi aynı sorunun yüzleri olduğu için tek blokta durur —
    ayrı kolonlara bölmek, iki yarısı ayrı yerlerde duran bir kanıt üretirdi.

    İkisi de yoksa `None`: boş bir sözlük yazmak *"bakıldı ve yoktu"* ile *"hiç
    sorulmadı"*yı karıştırırdı.
    """
    blok: dict = {}
    k = koken(service, cube_query)
    if k:
        blok.update(k)
    # ⚠️ FAZ 1.6 — KOLON düzeyi köken, **ilişki düzeyinin YANINA** (yerine değil).
    # İkisi farklı sorulardır: `koken()` *"hangi kırılım hangi join'den"*, `kolon_kokeni`
    # *"bu sayı hangi kolondan, hangi dönüşümle"*. Birini ötekinin adıyla sunmak, bir
    # kanıtı başka bir kanıt gibi göstermek olurdu.
    #
    # 🔴 CÜMLELERİ **BACKEND** ÜRETİR. Şablonları frontend'e kopyalamak, bu deponun
    # defalarca ölçtüğü *"aynı kuralın iki sahibi"* deseni olurdu — ve iki şablon kümesi
    # zamanla ayrışır, kullanıcı aynı kanıtı iki farklı cümleyle görürdü.
    try:
        from app.features import resolve_for

        from app.config import get_settings as _gs

        if "lineage" in resolve_for(_gs(), getattr(baglam, "principal", None)):
            from app import lineage as _lin

            kk = _lin.kolon_kokeni(service.schema(), cube_query) if cube_query else None
            blok["kolon_kokeni"] = kk or _lin.BILINMIYOR
            blok["koken_cumleleri"] = _lin.cumleler(kk or _lin.BILINMIYOR)
    except Exception:  # noqa: BLE001 — makbuz zenginleştirmesi cevabı DÜŞÜRMEZ
        _log.warning("kolon kökeni üretilemedi (best-effort)", exc_info=True)
    if baglam is not None:
        blok.update(baglam.makbuza())
    return blok or None


def record_contract(request: Request, *, service, session_id: str | None, question: str,
                    cube_query: dict | None, sql: str | None, result: dict | None,
                    source: str, baglam=None) -> str | None:
    """Query Contract kaydı — **tek uygulama** (ADR-0010).

    Öncesinde ÜÇ tane vardı: `ask()` içinde bir closure, `/cube` içinde satır-içi
    (`except Exception: pass` ile **sessizce yutan**) ve `_drill_record_contract`.
    Sessiz yutma ADR-0020'nin ihlaliydi ve aynı dosyada 20 satır aşağıda audit *bilerek*
    sarmalanmamıştı — yani tek dosyada iki farklı hata politikası vardı.

    Burada hata **loglanır**, akış düşmez: makbuzun yazılamaması cevabı iptal etmez ama
    **görünmez de kalmaz**.
    """
    store = getattr(request.app.state, "contracts", None)
    if store is None:
        return None
    try:
        principal = getattr(request.state, "principal", None)
        return store.record(
            session_id=session_id, question=question, cube_query=cube_query, sql=sql,
            result=result, source=source, schema_version=service.mdl_version,
            tenant_id=getattr(principal, "tenant_id", None),
            provenance=_provenance(service, cube_query, baglam),
        )
    except Exception:
        _log.warning("Query Contract kaydedilemedi (best-effort) — source=%s", source,
                     exc_info=True)
        return None


def _sertifika_blogu(request, resp: AskResponse, principal) -> dict | None:
    """`cube_query` → metrik referansı → kayıt → bugünkü durum.

    ⚠ Her adım **sessizce** `None` dönebilir ve bu doğru: bir sertifika **yokluğu** bir
    hata değildir. Ama yokluk `otomatik_iptal_nedeni` ile **karıştırılmaz** —
    `certification.durum()` ikisini ayrı döndürür.

    🔴 **Tanım/köken parmak izleri BUGÜNKÜ şemadan hesaplanır**, kayıttakiyle kıyaslanmak
    için. Kayıttakini yeniden kullanmak, kıyası **kendisiyle** yapmak olurdu ve hiçbir
    çürüme asla görünmezdi.
    """
    from app import certification, sertifika_okuma
    from control_plane.db import get_session

    ref = sertifika_okuma.metrik_ref(resp.cube_query)
    if not ref:
        return None
    tenant_id = getattr(principal, "tenant_id", None)
    if not tenant_id:
        return None

    with next(get_session()) as oturum:                  # type: ignore[call-overload]
        kayit = sertifika_okuma.kayittan_oku(oturum, tenant_id, ref)
    if kayit is None:
        return None

    # Bugünkü parmak izleri — kıyas için.
    try:
        from app.company_registry import wren_for_request
        sema = wren_for_request(request).schema()
        cube_adi, _, olcu_adi = ref.partition(".")
        olcu = None
        for c in (sema.get("cubes") or []):
            if c.get("name") == cube_adi:
                for m in (c.get("measures") or []):
                    if (m.get("name") if isinstance(m, dict) else m) == olcu_adi:
                        olcu = m if isinstance(m, dict) else {"name": m}
                        break
        tanim = certification.tanim_hash(olcu)
        koken = certification.koken_hash(resp.cube_query)
    except Exception:                       # noqa: BLE001
        tanim = koken = None

    return sertifika_okuma.blok(kayit, tanim=tanim, koken=koken)


def _tazelik_blogu(request, principal) -> tuple[str | None, str | None, str | None]:
    """`SyncState` → *(kademe, son_veri_ts, açıklama)*. *(FAZ 1.7 / §C ölçüt 12)*

    ## 🔴 Zincirin yalnız ORTASI eksikti

    | halka | vardı | bağlıydı |
    |---|---|---|
    | `SyncState.last_synced_at` (veri) | ✅ | — |
    | `app/tazelik.py` (`kademe`, `sayi_gosterilir_mi`) | ✅ | 🔴 **hiçbir çağıran yok** |
    | `AskResponse.freshness` + `son_veri_ts` + `tazelik_aciklama` | ✅ | 🔴 **hiçbir dolduran yok** |
    | `ReportCard` üç görsel hâli | ✅ **4 atıf** | 🔴 **hiç veri gelmiyor** |

    Denetimin adlandırdığı kör nokta buydu: *bir şema alanı üretici değildir* —
    `freshness` şemada vardı, ekran onu tüketiyordu, **dolduran kod yoktu**.

    ## ⚠ En yeni değil, EN ESKİ senkron

    Bir cevap birden çok tabloya dokunabilir ve tazelik **en zayıf halkadır**: bir tablo
    dün, biri sekiz gün önce senkronlandıysa cevap **sekiz gün eskidir**. En yeniyi
    almak, bayat bir sayıyı taze göstermenin en kolay yoludur.

    ## 🔴 Bulunamazsa `"bilinmiyor"` — `"taze"` DEĞİL

    B4: *ölçemediğimiz bir şeyi iyi varsaymak*, `⊘ ÖLÇÜLEMEDİ` üçüncü hâlinin tam
    tersidir. Ve `sayi_gosterilir_mi("bilinmiyor")` **False** → ekran sayıyı gizler.
    """
    from datetime import timezone

    from sqlmodel import select

    from app import tazelik
    from control_plane.db import get_session
    from control_plane.models import DbConnection, SyncState

    tenant_id = getattr(principal, "tenant_id", None)
    if not tenant_id:
        return None, None, None

    with next(get_session()) as oturum:                      # type: ignore[call-overload]
        # ⚠ Bağlantı üzerinden tenant'a bağlanır: `SyncState`in kendi `tenant_id`'si yok
        # ve onu varsaymak, **başka bir şirketin** tazeliğini göstermek olurdu.
        satirlar = oturum.exec(
            select(SyncState.last_synced_at)
            .join(DbConnection, DbConnection.id == SyncState.connection_id)  # type: ignore[arg-type]
            .where(DbConnection.tenant_id == tenant_id)
            .where(DbConnection.deleted_at.is_(None))        # type: ignore[union-attr]
        ).all()

    if not satirlar:
        return "bilinmiyor", None, ("Veri kaynağının en son ne zaman senkronlandığı "
                                    "bilinmiyor — bu yüzden sayı gösterilmiyor.")

    en_eski = min(satirlar)
    kademe = tazelik.kademe(en_eski)
    ts = (en_eski.replace(tzinfo=timezone.utc) if en_eski.tzinfo is None
          else en_eski).isoformat()
    if kademe == "taze":
        return kademe, ts, None
    if kademe == "uyari":
        return kademe, ts, ("Veri beklenenden eski — sayı gösteriliyor ama tazeliği "
                            "kontrol edin.")
    return kademe, ts, ("Veri bayat: en son senkron beklenen aralığın çok dışında. "
                        "Sayı gösterilmiyor — bayat bir sayıya dayanan karar geri "
                        "alınamaz.")


def _kural_baglami(request, principal, cube_query) -> str | None:
    """Yapısal iş kuralları → **anlatı notu**. *(FAZ 5.13b, bayrak `ui_knowledge_center`)*

    🔴 `app/rules.py` — 124 satır, 14 test — üretim kodunda **hiç import edilmiyordu** ve
    `AskResponse.kural_baglami` alanının **hiçbir dolduranı** yoktu. Denetimin *"12 yetim
    modül"* bulgusunun altıncı kalemi.

    ⚠ **Veri kaynağı da eksikti** ve bu ayrı bir kusurdu: `knowledge/rules/*.md` düz
    metindir (LLM prompt'una gider); `rules.py` yapısal `{id, metin, kapsam}` bekler.
    Kaynak (`knowledge/kurallar.yml`) mevcut metnin **kendi başlıklarından**
    yapılandırıldı — *yeni bir alan iddiası yok.*

    🔴 **Kural SQL'e DOKUNMAZ**: `rules.YASAK_ALANLAR` bunu şemada yasaklıyor ve
    `dogrula()` fail-closed reddediyor. *Bir kural SQL'i değiştirebilseydi, kullanıcının
    görmediği bir yerde sayıyı değiştirirdi.*
    """
    from app import rules
    from app.company_registry import wren_for_request

    ham = (wren_for_request(request).schema() or {}).get("kurallar")
    kurallar = rules.yukle(ham)
    if not kurallar:
        return None
    return rules.ek_baglam(kurallar, cube_query)


def seal(resp: AskResponse, *, request: Request, principal, t0: float,
         session_id: str | None, log_body: Any = None, thread_id: str | None = None,
         reply_to_label: str | None = None, is_new_topic: bool | None = None,
         endpoint: str = "ask") -> AskResponse:
    """Kapanış zinciri. **Her yanıt buradan geçer** — bkz. modül docstring'i.

    `log_body` etkileşim logunun ihtiyaç duyduğu istek nesnesidir; `/cube` gibi farklı
    şema kullanan uçlar hafif bir `SimpleNamespace` verebilir. `is_new_topic` verilmezse
    dokunulmaz (uç bilmiyorsa uydurmaz).
    """
    from control_plane import audit

    from app.pii import apply_to_ask_response

    if is_new_topic is not None:
        resp.is_new_topic = is_new_topic
    if thread_id is not None:
        resp.thread_id = thread_id
    if reply_to_label is not None:
        resp.reply_to_label = reply_to_label

    # Sıra ÖNEMLİ: öneriler yorumun signal'larına bağımlı; explain ikisini de okur.
    _maybe_interpret(request, resp)
    _temellendir(resp)
    _attach_next_steps(request, resp)
    _attach_recommendations(request, resp)
    resp.explain = _build_explain(resp)

    # ⚠️ FAZ 1.12 — AI ACT İŞARETLEMESİ. `_maybe_interpret` ANLATIYI ürettikten SONRA
    # okunur: `narration` varsa bu yanıtta LLM üretimi düz metin VAR demektir.
    # 🔴 SAYI DEĞİL, ÜSLUP işaretlenir — sayıyı her zaman sistem koyar ve
    # `narration_guard` eşleşmeyeni düşürür. Md.50'nin istediği tam olarak budur.
    # FAZ 2.5 — HEDEF KIYASI. Beyan yoksa `None` kalır ve grafikteki çizgi bugünkü
    # anlamını (ortalama) korur — *hedef UYDURULMAZ*.
    # 🔴 **BAYRAĞA BAĞLI (KURAL B).** Yol haritası 2.5'i `[bayrak: hedef_kiyasi]` diye
    # ilan ediyordu ama kod bayrağı TANIMIYORDU — bu deponun tekrar eden kusur sınıfı:
    # *"beyan var, kod onu tanımıyor"*. Bayraksız bir özellik GERİ ALINAMAZ; geri
    # alınamayan bir özelliğin `GERİ AL` satırı bir temenniden ibarettir.
    # Kapalıyken `resp.hedef` HİÇ üretilmez → yanıt bayt bayt bugünküyle aynıdır.
    try:
        from app import hedef as _hedef
        from app.company_registry import wren_for_request
        from app.config import get_settings
        from app.features import resolve_for

        if "hedef_kiyasi" in resolve_for(get_settings(),
                                         getattr(request.state, "principal", None)):
            resp.hedef = _hedef.blok(wren_for_request(request).schema(), resp.cube_query,
                                     resp.result.model_dump() if resp.result else None)
        else:
            resp.hedef = None
    except Exception:                       # noqa: BLE001 — hedef cevabı DÜŞÜRMEZ
        resp.hedef = None

    # 🔴 **FAZ 5.13b — KURAL MOTORU BAĞLANDI.** Modül 124 satır + 14 testti ve
    # `kural_baglami` alanının **hiçbir dolduranı yoktu**; üstelik yapısal veri kaynağı
    # da eksikti (düz metin ≠ `{id, metin, kapsam}`).
    # ⚠ Bayrak kapalıyken alan **hiç üretilmez** → yanıt bugünküyle birebir (KURAL B).
    try:
        from app.config import get_settings as _gs2
        from app.features import resolve_for as _rf2

        _p2 = getattr(request.state, "principal", None)
        if "ui_knowledge_center" in _rf2(_gs2(), _p2):
            resp.kural_baglami = _kural_baglami(request, _p2, resp.cube_query)
    except Exception:                       # noqa: BLE001 — kural cevabı DÜŞÜRMEZ
        resp.kural_baglami = None

    # 🔴 **FAZ 1.7 / §C ÖLÇÜT 12 — TAZELİK ZİNCİRİ BAĞLANDI.**
    #
    # Ölçüldü: `app/tazelik.py`'nin **hiçbir çağıranı**, `AskResponse.freshness`'in
    # **hiçbir dolduranı** yoktu — oysa `ReportCard` onu **dört yerde** okuyor ve üç
    # görsel hâli (`taze`/`uyari`/`hata`+`bilinmiyor`) çizili duruyordu.
    # *Bir şema alanı üretici değildir:* alan vardı, ekran tüketiyordu, **üreten yoktu**.
    #
    # ⚠ Yeri `seal()` — sertifikayla aynı sahip: tazelik de bir **mühürleme** kararıdır
    # ve `ask()` tavanı 1150/1151.
    # ⚠ Bayrak kapalıyken alanlar **HİÇ üretilmez** → yanıt bugünküyle birebir (KURAL B).
    try:
        from app.config import get_settings as _gs
        from app.features import resolve_for as _rf

        _p = getattr(request.state, "principal", None)
        if "tazelik" in _rf(_gs(), _p):
            resp.freshness, resp.son_veri_ts, resp.tazelik_aciklama = \
                _tazelik_blogu(request, _p)
    except Exception:                       # noqa: BLE001 — tazelik cevabı DÜŞÜRMEZ
        resp.freshness = None

    # 🔴 **ONAY BİLETİ — §C ölçüt 6'nın "süre aşımı 30 dk" şartı, TEK SAHİPTEN.**
    #
    # Ölçüldü (okunarak): canlı onay yolunda **hiçbir süre kontrolü yoktu**; üç saat
    # önceki bir öneri onaylanıp koşabiliyordu. `VARSAYILAN_OMUR_SN` yalnız
    # `onay_akisi.py`'de duruyordu — o modülün **hiçbir üretim tüketicisi olmadan**.
    #
    # ⚠ **Neden `seal()` — ve neden öneriyi KURAN yerler değil.** Öneri üç ayrı yerde
    # kuruluyor (`eylem.py` ×2 + `ask.py`'nin tercih dalı). Üçüne ayrı ayrı bilet eklemek
    # **üç sahip** demekti ve dördüncüsü bir gün unuturdu — bu deponun en sık kusuru.
    # Burada bir kez iliştirilir ve **her** öneri, nerede kurulursa kurulsun taşır.
    # ⚠ Ayrıca `ask()` tavanı 1150/1151: oraya bir satır eklemek tavanı doldururdu.
    if isinstance(resp.eylem_onerisi, dict) and resp.eylem_onerisi.get("eylem"):
        try:
            from app import onay_akisi
            resp.eylem_onerisi = {**resp.eylem_onerisi,
                                  "bilet": onay_akisi.bilet(resp.eylem_onerisi["eylem"])}
        except Exception:                   # noqa: BLE001 — anahtar yoksa BİLETSİZ döner
            # 🔴 Sessizce süresiz bir öneri üretmek yerine **biletsiz** dönülür ve
            # `eylem_onayla` onu reddeder. *Bir süre kapısı, atlanabildiği anda bir
            # törene dönüşür.*
            _log.warning("onay bileti üretilemedi — öneri BİLETSİZ (fail-closed)",
                         exc_info=True)

    # 🔴 **FAZ 7.3(k) / B8 — SERTİFİKA ZİNCİRİ BAĞLANDI.**
    #
    # Ölçüldü: `MetrikSertifikasi` tablosunun **hiçbir okuyucusu**, `certification.py`'nin
    # **hiçbir çağıranı**, `AskResponse.sertifika`'nın **hiçbir dolduranı** ve
    # `sertifikaRozeti()`'nin **hiçbir verisi** yoktu. Dört parça da ayrı ayrı doğru,
    # hiçbiri diğerine dokunmuyor.
    # *Bir zincirin her halkasını ayrı ayrı test etmek, zinciri test etmek değildir.*
    #
    # ⚠ Yeri `seal()`: sertifika bir **mühürleme** kararıdır (cevap tamamlandıktan sonra
    # okunur) ve `ask()` tavanı 1150/1151 — oraya bir çağrı eklemek tavanı aşardı.
    # ⚠ Bayrak kapalıyken `resp.sertifika` **HİÇ üretilmez** → yanıt bayt bayt bugünküyle
    # aynı (KURAL B).
    try:
        from app.config import get_settings
        from app.features import resolve_for

        # 🔴 `sertifika` **`Explain`'in alanıdır**, `AskResponse`'un değil — ve ilk
        # yazımda `resp.sertifika` yazdım, süit `ValueError: "AskResponse" object has no
        # field "sertifika"` ile yakaladı. ⚠ Pydantic bunu **çalışma zamanında** söyledi;
        # bir alanın hangi modele ait olduğunu *"yakınında duruyor"* diye varsaymak, bu
        # zincirin BEŞİNCİ kopukluğuydu.
        _principal = getattr(request.state, "principal", None)
        if resp.explain is not None and "metrik_sertifikasi" in resolve_for(
                get_settings(), _principal):
            resp.explain.sertifika = _sertifika_blogu(request, resp, _principal)
    except Exception:                       # noqa: BLE001 — sertifika cevabı DÜŞÜRMEZ
        if resp.explain is not None:
            resp.explain.sertifika = None
    # FAZ 2.6 — mali yıl penceresi. `seal()` HER yanıtın geçtiği kapanıştır; başka bir
    # yere koymak onu BAZI yanıtlarda eksik bırakırdı (1.12'nin aynı gerekçesi).
    try:
        from datetime import date as _date

        from app import mali_takvim

        resp.mali_donem = mali_takvim.etiket(_date.today()) or None
    except Exception:                       # noqa: BLE001 — etiket cevabı DÜŞÜRMEZ
        resp.mali_donem = None
    resp.ai_generated_prose = bool((resp.interpretation or {}).get("narration"))
    # `probabilistik` YALNIZ LLM yolunda: `cube` deterministiktir, `cube+llm`'de ALAN
    # SEÇİMİ olasılıksaldır ama SAYI yine küpten gelir → yine `olculmus` DEĞİL.
    # ⚠ Skaler bir güven puanı UYDURULMAZ; bu bir KATEGORİDİR.
    _src = str(resp.source or "")
    resp.kanit_sinifi = "probabilistik" if (_src.startswith("llm") or "+llm" in _src) \
        else "olculmus"

    # PII maskesi kalıcı yazımlardan ÖNCE — ham TCKN/e-posta/telefon/IBAN sohbet
    # geçmişine de düşmesin. `pii:view` yetkisi olan maskesiz görür; o erişim AYRI bir
    # audit satırıdır (KVKK: hangi PII'yi kim gördü).
    if apply_to_ask_response(resp, principal):
        audit.record(principal, "pii_view", nl_question=resp.question,
                     ip=request.client.host if request.client else None)

    _persist_message(request, resp, session_id)
    sure_ms = int((time.monotonic() - t0) * 1000)
    if log_body is not None:
        _log_interaction(session_id, log_body, resp, sure_ms, principal, request)

    # BİLEREK try/except'siz: `audit.record` kendi içinde DB→spool'a düşer ve YALNIZ ikisi
    # birlikte başarısız olursa fırlatır. "Başarı audit'siz raporlanamaz" — fail-closed.
    audit.record(principal, "query", nl_question=resp.question, generated_sql=resp.sql or None,
                 rows_returned=resp.result.row_count if resp.result else None,
                 contract_id=resp.contract_id,
                 ip=request.client.host if request.client else None)

    _log.info("CEVAP /%s: q=%r source=%s thread=%s yeni_konu=%s satır=%s süre=%dms%s",
              endpoint, resp.question, resp.source, resp.thread_id, resp.is_new_topic,
              resp.result.row_count if resp.result else None, sure_ms,
              f" not={resp.note!r}" if resp.note else "")
    return resp
