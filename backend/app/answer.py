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
        prefix = next((k for k in _EXPLAIN_PATH if s.startswith(k)), None)
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


def _log_interaction(session_id: str | None, body: AskRequest, resp: AskResponse,
                     dur_ms: int, principal=None) -> None:
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
                llm_output_tokens=_u.get("output_tokens"), llm_latency_ms=_u.get("latency_ms")))
            s.commit()
    except Exception:
        _log.warning("interaction log (DB) yazılamadı (best-effort)", exc_info=True)


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
        try:
            from app.company_registry import wren_for_request
            for c in wren_for_request(request).schema().get("cubes") or []:
                units.update(c.get("units") or {})
                lower_is_better.update(c.get("lower_is_better") or [])  # DSO/CCC/fire… yönü
        except Exception:
            pass
        if resp.kpi and resp.kpi.get("lower_is_better"):
            lower_is_better.add(resp.kpi.get("kpi"))  # KPI ölçüsü (CCC gibi) düşük=iyi
        resp.interpretation = interpret(
            resp.result.model_dump() if resp.result else None,
            resp.cube_query, resp.kpi, units, lower_is_better)
    except Exception:  # noqa: BLE001 - yorum best-effort (yanıtı düşürmez)
        _log.warning("çıktı yorumu üretilemedi (best-effort)", exc_info=True)


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
        cubes = wren_for_request(request).schema().get("cubes") or []
        index = {c.get("name"): c for c in cubes}
        resp.next_steps = [NextStep(**s)
                           for s in cube_router.suggest_next_steps(resp.cube_query, index)]
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


def record_contract(request: Request, *, service, session_id: str | None, question: str,
                    cube_query: dict | None, sql: str | None, result: dict | None,
                    source: str) -> str | None:
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
            provenance=koken(service, cube_query),
        )
    except Exception:
        _log.warning("Query Contract kaydedilemedi (best-effort) — source=%s", source,
                     exc_info=True)
        return None


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
    _attach_next_steps(request, resp)
    _attach_recommendations(request, resp)
    resp.explain = _build_explain(resp)

    # PII maskesi kalıcı yazımlardan ÖNCE — ham TCKN/e-posta/telefon/IBAN sohbet
    # geçmişine de düşmesin. `pii:view` yetkisi olan maskesiz görür; o erişim AYRI bir
    # audit satırıdır (KVKK: hangi PII'yi kim gördü).
    if apply_to_ask_response(resp, principal):
        audit.record(principal, "pii_view", nl_question=resp.question,
                     ip=request.client.host if request.client else None)

    _persist_message(request, resp, session_id)
    sure_ms = int((time.monotonic() - t0) * 1000)
    if log_body is not None:
        _log_interaction(session_id, log_body, resp, sure_ms, principal)

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
