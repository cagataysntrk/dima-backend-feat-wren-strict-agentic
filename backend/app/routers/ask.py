"""Natural-language → SQL → result endpoint (the demo's headline flow)."""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from app import cube_router, viz, yoy
from app.auth.dependencies import require, require_company
from app.config import get_settings
from app.llm import RuleBasedSqlGenerator
from app.logging_setup import get_logger
from app.schemas import (
    AskRequest,
    AskResponse,
    CubeRequest,
    QueryResult,
    ReportRequest,
    Suggestion,
    UploadRequest,
    UploadResponse,
)
from app.wren_service import UnsafeSqlError

router = APIRouter(tags=["ask"])
_log = get_logger("ask")  # system/app log (ADR-0020): best-effort bloklar sessizce yutmaz


def _source_kind(source: str | None) -> str:
    """Ham source → normalize tür (interaction_log facet/filtre): cube|llm|rule|upload|none|other."""
    s = (source or "").lower()
    if not s:
        return "none"
    if s.startswith("cube"):
        return "cube"
    if s.startswith("llm"):
        return "llm"
    if s.startswith(("rule", "kural")):
        return "rule"
    if s.startswith("upload"):
        return "upload"
    return "other"

_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
_UPLOAD_DIR = _LOG_DIR / "uploads"  # chat-scoped yüklenen veri (ephemeral, oturum DuckDB'si)
_MAX_UPLOAD = 25 * 1024 * 1024      # 25 MB — DuckDB bellek-içi ingest sınırı


def _dataset_store(request: Request) -> dict:
    """session_id → {service, info, filename} (in-memory, chat-scoped, ephemeral)."""
    store = getattr(request.app.state, "datasets", None)
    if store is None:
        store = {}
        request.app.state.datasets = store
    return store


def _service_for(request: Request, session_id: str | None):
    """Oturumda yüklenmiş dataset varsa ONU sorgula (base modu); yoksa tenant servisi."""
    if session_id:
        ds = _dataset_store(request).get(session_id)
        if ds:
            return ds["service"]
    from app.company_registry import wren_for_request
    return wren_for_request(request)


def _uuid_or_none(val):
    """str(uuid) → UUID (InteractionLog aktör kolonları AuditLog gibi UUID). Geçersiz/boş → None."""
    import uuid as _uuid

    try:
        return _uuid.UUID(val) if val else None
    except (ValueError, TypeError):
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


def _log_upload(session_id: str | None, filename: str, dataset_label: str,
                row_count: int, col_count: int, dur_ms: int, principal=None) -> None:
    """Chat-scoped dosya yükleme olayını `interaction_log`'a yazar (ADR-0020).

    Sorgu değil ama telemetri yüzeyinde görünür olmalı: hangi kullanıcı ne zaman hangi
    dosyayı yükledi (satır/sütun sayısı) — kalite izleme + KVKK erişim-izi. Ham dosya
    veya içerik TUTULMAZ (yalnız meta). source='upload' → viewer'da ⬆ YÜKLEME. Best-effort."""
    try:
        if not get_settings().interaction_log:
            return
        from sqlmodel import Session

        from control_plane.db import engine
        from control_plane.models import InteractionLog

        with Session(engine) as s:
            s.add(InteractionLog(
                session_id=session_id, user_id=_uuid_or_none(getattr(principal, "user_id", None)),
                tenant_id=_uuid_or_none(getattr(principal, "tenant_id", None)),
                question=f"[dosya yükleme] {filename}",
                source="upload", kind="upload", follow_up=False,
                rows=row_count, duration_ms=dur_ms,
                note=f"dataset: {dataset_label} · {row_count} satır · {col_count} sütun"))
            s.commit()
    except Exception:
        _log.warning("upload interaction log (DB) yazılamadı (best-effort)", exc_info=True)


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


def _parse_decision(raw: str) -> dict:
    """refine_cube çıktısını (JSON) ayrıştırır: {action, cube_query?, reason?}. Bozuksa {}."""
    import json
    import re

    if not raw:
        return {}
    s = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", raw.strip()).strip()
    try:
        d = json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, re.S)
        if not m:
            return {}
        try:
            d = json.loads(m.group(0))
        except Exception:
            return {}
    return d if isinstance(d, dict) else {}


# Meta/ürün soruları — veri sorgusu DEĞİL. Bunları SQL'e zorlamak yerine yardım yanıtı ver
# (yoksa cube tutmaz → kural-tabanlı alakasız tablo döner). Normalize edilmiş metinde aranır.
_META_HINTS = (
    "dima ne", "dima nedir", "ne yapabil", "neler yapab", "ne ise yar", "ne ise yara",
    "nasil kullan", "nasil calis", "sen kim", "kimsin", "sen nesin", "yardim",
    "merhaba", "selam", "naber", "napiyorsun", "ornek soru", "ne sorabil",
)
_META_TEXT = (
    "dima — verinle doğal dille konuşman için bir analitik motoru "
    "(deterministic · intelligent · modeled · agentic). Bir soru yaz; güvenilir SQL üretir, "
    "doğrular, çalıştırır ve raporlar. Şunları deneyebilirsin:"
)
# Örnekler tıklanır chip olarak sunulur (label gösterilir, query gönderilir).
_META_SUGGESTIONS = [
    {"label": "Makine bazında OEE", "query": "makine bazında ortalama oee"},
    {"label": "Aşama bazında toplam fire", "query": "aşama bazında toplam fire"},
    {"label": "Bu ay toplam üretim", "query": "bu ay toplam üretim"},
    {"label": "Vardiya × haftanın günü verimliliği", "query": "vardiya × haftanın günü verimliliği (son 3 ay)"},
]

# Görünüm isteği ("grafik ver", "tablo olarak") — VERİ değil SUNUM düzenlemesi.
# "grafi" kökü grafik/grafiği/grafiğini çekimlerini yakalar. Sıra önemli: özel tür
# (çizgi/pasta/ısı) genel "grafik"ten önce.
_VIZ_MAP = (
    ("tablo", "table"), ("pasta", "pie"), ("cizgi", "line"), ("sutun", "bar"),
    ("isi harita", "heatmap"), ("isi graf", "heatmap"), ("heatmap", "heatmap"), ("panel", "facet"),
    # "her kumaş türü İÇİN AYRI (ayrı) grafik" = small multiples (panelli)
    ("ayri ayri", "facet"), ("icin ayri", "facet"), ("ayri grafik", "facet"),
    ("grafi", "chart"), ("chart", "chart"), ("gorsel", "chart"),
)
_VIZ_LABELS = {"chart": "grafik", "table": "tablo", "line": "çizgi grafik",
               "bar": "sütun grafik", "pie": "pasta grafik", "heatmap": "ısı haritası",
               "facet": "panelli görünüm"}


def _viz_hint(q_norm: str) -> str | None:
    for k, v in _VIZ_MAP:
        if k in q_norm:
            return v
    return None


# Faz C — dönem belirsizse (pür toplam, dönem yok) sorulur; chip'ler deterministik uygulanır.
_PERIOD_TEXT = "Hangi dönem için? Bir dönem seç ya da yaz (ör. “son 3 ay”, “geçen yıl”)."
_PERIOD_SUGGESTIONS = [
    {"label": "Bugün", "query": "bugün"},
    {"label": "Bu hafta", "query": "bu hafta"},
    {"label": "Bu ay", "query": "bu ay"},
    {"label": "Bu yıl", "query": "bu yıl"},
    {"label": "Tümü", "query": "tüm zamanlar"},
]


def _catalog_suggestions(schema: dict) -> list[dict]:
    """Aktif katalogdan örnek soru chip'leri üretir (ADR-0018 d): şirket/sektör/kaynak
    fark etmez, mevcut cube×ölçü×boyuttan gerçek örnekler — "neler yapabilirsin",
    "hangi ölçüler var", selamlama hepsi bunu görür. Sıfır pack/şirket işi."""
    sugg: list[dict] = []
    for cube in (schema.get("cubes") or [])[:4]:
        disp = cube.get("display") or cube.get("name")
        m_disp = cube.get("measure_synonyms_display") or {}
        d_labels = cube.get("dimension_labels") or {}
        measures = cube.get("measures") or []
        if not measures:
            continue
        mlabel = m_disp.get(measures[0]) or measures[0]
        # zaman-dışı ilk boyut varsa "X bazında" örneği, yoksa düz ölçü
        dim = next((d_labels.get(d) or d for d in (cube.get("dimensions") or [])), None)
        if dim:
            sugg.append({"label": f"{dim} bazında {mlabel}",
                         "query": f"{dim} bazında {mlabel}"})
        else:
            sugg.append({"label": f"bu yıl {mlabel}", "query": f"bu yıl {mlabel}"})
    return sugg[:5]


def _starter_suggestions(request: Request, schema: dict) -> list[dict]:
    """K1 (rehberli analitik) — rol/sektör bazlı KÜRATÖRLÜ başlangıç soruları; küratör
    yoksa katalog-türevi otomatiğe düşer. "neler yapabilirsin"/selamlama chip'leri."""
    try:
        from app.starters import starter_questions
        principal = getattr(request.state, "principal", None)
        curated = starter_questions(get_settings(), principal)
        if curated:
            return curated[:6]
    except Exception:  # noqa: BLE001 - best-effort (katalog yedeğine düş)
        _log.warning("başlangıç soruları çözülemedi (best-effort)", exc_info=True)
    return _catalog_suggestions(schema)


def _is_catalog_query(q: str) -> bool:
    """Katalog KEŞFİ: "hangi kpi/rapor/metrik var", "neler sorabilirim", "ölçüler neler".
    Sistem kendi cube/ölçü/KPI kataloğunu bilir → deterministik listeler (LLM'siz)."""
    import re

    return bool(re.search(
        r"\b(hangi|neler|ne\s+tur|listele|liste|mevcut)\b.*"
        r"(kpi|rapor|metrik|olcu|olcum|analiz|gosterge|cube|veri|oran|hesap)"
        r"|neler\s+sorabil|ne\s+sorabil|neler\s+yapabil|neler\s+var", q))


def _catalog_listing(schema: dict) -> str:
    """Aktif katalogu okunur metne döker: KPI'lar + her cube'un ölçüleri (jenerik, DB-bağımsız)."""
    parts: list[str] = []
    kpis = schema.get("kpis") or []
    if kpis:
        parts.append("KPI'lar (bileşke): "
                     + " · ".join(str(k.get("label") or k.get("name")) for k in kpis))
    lines: list[str] = []
    for c in schema.get("cubes") or []:
        disp = c.get("display") or c.get("name")
        m_disp = c.get("measure_synonyms_display") or {}
        ms = [str(m_disp.get(m) or m) for m in (c.get("measures") or [])[:7]]
        if ms:
            lines.append(f"• {disp}: " + ", ".join(ms))
    if lines:
        parts.append("Raporlar (cube × ölçü):\n" + "\n".join(lines))
    return ("Sorabileceklerin:\n\n" + "\n\n".join(parts)) if parts else "Katalog boş görünüyor."


def _catalog_all_suggestions(schema: dict) -> list[dict]:
    """KPI'lar (tıklanır) + cube örnekleri — katalog keşfi yanıtının chip'leri."""
    sugg: list[dict] = []
    for k in (schema.get("kpis") or [])[:3]:
        q = (k.get("synonyms") or [k.get("name")])[0]
        sugg.append({"label": str(k.get("label") or k.get("name")).split("(")[0].strip(),
                     "query": str(q)})
    sugg += _catalog_suggestions(schema)
    return sugg[:6]


def _is_meta(q_norm: str) -> bool:
    # Soruda "dima" KELİMESİ geçiyorsa ürün/meta sorusudur (veri sorusu ürünün adını
    # içermez). TAM-KELİME şart: "randıman" içinde "dima" altdizisi var! Ayrıca genel
    # meta ipuçları (nasıl kullanılır, merhaba...).
    import re

    return bool(re.search(r"\bdima\b", q_norm)) or any(h in q_norm for h in _META_HINTS)


_VIZ_KINDS = {"chart", "table", "line", "bar", "pie", "heatmap", "facet"}


def _drop_invented(cq: dict, q_norm: str, prev: dict | None = None) -> dict:
    """LLM çıktısı doğrulayıcısı (ADR-0008): mesajda GEÇMEYEN değer filtreleri ve
    istenmemiş zaman kovası ATILIR — katalogdaki enum listesi seçenek dökümüdür,
    varsayılan filtre değildir. Önceki rapordan taşınan filtreler meşrudur."""
    from app import cube_router as cr

    prev_f = {(f.get("dimension"), f.get("value")) for f in (prev or {}).get("filters", [])}
    keep = []
    for f in cq.get("filters", []):
        if f.get("dimension") == "tarih":
            keep.append(f)
            continue
        nv = cr._norm(str(f.get("value", "")))
        if (f.get("dimension"), f.get("value")) in prev_f or (nv and nv in q_norm):
            keep.append(f)
    out = dict(cq)
    if keep:
        out["filters"] = keep
    else:
        out.pop("filters", None)
    if out.get("timeDimensions") and not (
        cr._time_gran(q_norm) or cr._period_hit_words(q_norm) or (prev or {}).get("timeDimensions")
    ):
        out.pop("timeDimensions")  # kimse zaman kovası istemedi
    if out.get("limit") and out.get("timeDimensions") and out.get("dimensions"):
        # SATIR limiti zaman serili kırılımı ortadan keser ("ilk 3" = Ocak'ın 3 satırı
        # olurdu) — varlık top-N'i deterministik yol kurar; LLM'inki atılır.
        out.pop("limit")
    return out


def _resolve_period(prev: dict | None, cq: dict, period_expr, q_norm: str) -> tuple[dict, bool]:
    """ADR-0008 K3: LLM tarih YAZMAZ; dönem sırasıyla period_expr → mesaj metni →
    önceki raporun dönemi'nden PYTHON'la çözülür. Açık ifade çözülemezse (True):
    sistem tahmin etmez, sorar."""
    from app import cube_router as cr

    base = [f for f in cq.get("filters", []) if f.get("dimension") != "tarih"]
    prev_dates = [f for f in (prev or {}).get("filters", []) if f.get("dimension") == "tarih"]
    expr_n = cr._norm(period_expr.strip()) if isinstance(period_expr, str) and period_expr.strip() else ""
    unresolved = False
    if expr_n:
        if cr.is_all_time(expr_n):
            dates: list = []
        else:
            dates = cr.date_filters(expr_n, "tarih") or cr.date_filters(q_norm, "tarih")
            if not dates:
                dates, unresolved = prev_dates, True
    else:
        dates = cr.date_filters(q_norm, "tarih") or prev_dates
    out = dict(cq)
    allf = base + dates
    if allf:
        out["filters"] = allf
    else:
        out.pop("filters", None)
    return out, unresolved


def _canon_cq(cq: dict) -> str:
    """Oylama için kanonik CubeQuery formu (liste sıraları normalize)."""
    c = json.loads(json.dumps(cq, sort_keys=True))
    for key in ("measures", "dimensions"):
        if key in c:
            c[key] = sorted(c[key])
    if "filters" in c:
        c["filters"] = sorted(
            c["filters"],
            key=lambda f: (f.get("dimension", ""), f.get("operator", ""), str(f.get("value"))),
        )
    return json.dumps(c, sort_keys=True, ensure_ascii=False)


def _select_consistent(llm, question: str, catalog: str, index: dict, k: int):
    """CubeQuery SELF-CONSISTENCY (literatür #1 / ClarifyGPT deseni): k örnekleme →
    kanonik oylama. Uyuşma = hem doğruluk hem KALİBRE güven sinyali; uyuşmazlık
    tek eksendeyse o eksen chip'e dönüşür.

    Döner: (kazanan|None, uyum_orani, uyusmazlik_ekseni|None, farklı_adaylar)."""
    import concurrent.futures as cf

    def one(_i):
        try:
            return cube_router.parse_cube_query(llm.select_cube(question, catalog), index)
        except Exception:
            return None

    if k <= 1:
        c = one(0)
        return c, (1.0 if c else 0.0), None, ([c] if c else [])
    with cf.ThreadPoolExecutor(max_workers=k) as ex:
        cands = [c for c in ex.map(one, range(k)) if c]
    if not cands:
        return None, 0.0, None, []
    votes: dict[str, list[dict]] = {}
    for c in cands:
        votes.setdefault(_canon_cq(c), []).append(c)
    best = max(votes.values(), key=len)
    agreement = len(best) / len(cands)
    if len(votes) == 1 or agreement >= 2 / 3:
        return best[0], agreement, None, [v[0] for v in votes.values()]
    distinct_cqs = [v[0] for v in votes.values()]
    axes = [
        f for f in ("cube", "measures", "dimensions")
        if len({json.dumps(c.get(f), sort_keys=True, ensure_ascii=False) for c in distinct_cqs}) > 1
    ]
    axis = axes[0] if len(axes) == 1 else None
    return None, agreement, axis, distinct_cqs


def _llm_source(llm, used_rule: bool) -> str:
    """Yanıt provenance'ı: hangi sağlayıcı SQL üretti."""
    if used_rule:
        return "rule"
    last = getattr(llm, "_last", None) or llm  # FailoverSqlGenerator → son başarılı
    prov = getattr(last, "_provider", None)
    if prov:
        return f"llm:{prov}"
    return "llm:anthropic" if type(last).__name__ == "AnthropicSqlGenerator" else "llm"


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


def _statement_kind(q: str) -> str | None:
    """GL YAPISAL RAPOR niyeti (§55): gelir tablosu / bilanço. q normalize edilmiş."""
    if re.search(r"gelir tablosu|kar zarar|kar/zarar|k?ar zarar|income statement", q):
        return "gelir"
    if re.search(r"\bbilanco\b|balance sheet", q):
        return "bilanco"
    return None


def _statement_result(out: dict) -> QueryResult:
    """Statement dict → tablo sonucu (kalem/tutar) — mevcut ResultView ile render."""
    if out["kind"] == "gelir":
        rows = [{"Kalem": s["label"], "Tutar (₺)": s["amount"]} for s in out["statement"]]
    else:
        b = out["balance"]
        rows = ([{"Bölüm": "AKTİF", "Kalem": x["label"], "Tutar (₺)": x["amount"]}
                 for x in b["aktif"]]
                + [{"Bölüm": "AKTİF", "Kalem": "AKTİF TOPLAM", "Tutar (₺)": b["aktif_toplam"]}]
                + [{"Bölüm": "PASİF", "Kalem": x["label"], "Tutar (₺)": x["amount"]}
                   for x in b["pasif"]]
                + [{"Bölüm": "PASİF", "Kalem": "PASİF TOPLAM", "Tutar (₺)": b["pasif_toplam"]}])
    cols = list(rows[0].keys()) if rows else []
    return QueryResult(columns=cols, rows=rows, row_count=len(rows))


@router.get("/starters", dependencies=[Depends(require("query:run"))])
def starters(request: Request) -> dict:
    """K1 (rehberli analitik) — rol/sektör bazlı başlangıç soruları. Küratörlü (pack
    zinciri, rol-filtreli); yoksa katalog otomatiğine düşer. FE boş-durum/yardım
    panelinde tıklanır chip olarak gösterir. Deterministik (LLM yok)."""
    principal = getattr(request.state, "principal", None)
    from app.starters import starter_questions
    curated = starter_questions(get_settings(), principal)
    if curated:
        return {"starters": curated}
    try:
        from app.company_registry import wren_for_request
        return {"starters": _catalog_suggestions(wren_for_request(request).schema())}
    except Exception:  # noqa: BLE001 - katalog erişilemezse boş liste
        return {"starters": []}


@router.post("/ask/upload", response_model=UploadResponse,
             dependencies=[Depends(require("query:run")), Depends(require_company)])
def upload_dataset(request: Request, body: UploadRequest) -> UploadResponse:
    """Chat-scoped Excel/CSV yükle → oturum DuckDB'sine ingest → oto-cube → NL pipeline hazır.

    EPHEMERAL (base modu): veri oturuma bağlı, kalıcılık yok. Sonraki /ask'ler bu session_id ile
    gelirse yüklenen veriyi sorgular. Ham dosya bulut LLM'e gitmez (yerel DuckDB)."""
    import time

    from app import dataset

    t0 = time.monotonic()
    try:
        raw = base64.b64decode(body.content_b64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Geçersiz base64 içerik")
    if len(raw) > _MAX_UPLOAD:
        raise HTTPException(status_code=413,
                            detail=f"Dosya çok büyük (>{_MAX_UPLOAD // 1024 // 1024} MB)")
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", body.session_id)[:80]
    label = Path(body.filename).stem[:40] or "veri"
    try:
        info = dataset.ingest_file(raw, body.filename, _UPLOAD_DIR / safe)
        mdl = dataset.build_mdl(info, cube_name="veri", label=label)
        svc = dataset.build_service(_UPLOAD_DIR / safe, mdl)
    except Exception as exc:  # noqa: BLE001 — kullanıcıya dürüst hata, sunucuyu düşürme
        raise HTTPException(status_code=400, detail=f"Dosya işlenemedi: {str(exc)[:200]}")
    _dataset_store(request)[body.session_id] = {
        "service": svc, "info": info, "filename": body.filename}
    # Yükleme olayını telemetriye yaz (ADR-0020) — sorgu değil ama viewer'da görünmeli.
    _log_upload(body.session_id, body.filename, label, info["row_count"],
                len(info["columns"]), int((time.monotonic() - t0) * 1000),
                principal=getattr(request.state, "principal", None))
    dims = [c for c in info["columns"] if c["role"] == "dimension"]
    meas = [c for c in info["columns"] if c["role"] == "measure"]
    sug: list[Suggestion] = []
    if dims and meas:
        q = f"{dims[0]['orig']} bazında {meas[0]['orig']}"
        sug.append(Suggestion(label=q, query=q))
    if meas:
        sug.append(Suggestion(label=f"toplam {meas[0]['orig']}", query=f"toplam {meas[0]['orig']}"))
    sug.append(Suggestion(label="neler sorabilirim", query="neler sorabilirim"))
    return UploadResponse(dataset=label, row_count=info["row_count"],
                          columns=info["columns"], suggestions=sug)


@router.post("/cube", response_model=AskResponse,
             dependencies=[Depends(require("query:run")), Depends(require_company)])
def cube(request: Request, body: CubeRequest) -> AskResponse:
    """Yorum çubuğu (chip) düzenlemesi — CubeQuery doğrulanır ve DETERMİNİSTİK çalışır.

    Kullanıcının yorumu (ölçü/kırılım/filtre/dönem) chip olarak görünür ve buradan
    oynanabilir (UpcyBrain IntentRouter deseninin CubeQuery-natif hali)."""
    import time

    t0 = time.monotonic()
    settings = get_settings()
    service = _service_for(request, body.session_id)  # yüklenen dataset varsa onu sorgular
    schema = service.schema()

    _, index = cube_router.build_catalog(schema)
    if body.cube_query and body.cube_query.get("cube"):
        # cube adı göçü (yeniden adlandırma sonrası eski adla gelen chip düzenlemesi)
        body.cube_query["cube"] = cube_router.resolve_cube_name(body.cube_query["cube"], schema)
    cq = cube_router.parse_cube_query(json.dumps(body.cube_query, ensure_ascii=False), index)
    if not cq:
        raise HTTPException(status_code=400, detail="Geçersiz cube sorgusu (chip düzenlemesi).")

    limit = min(body.limit or settings.max_result_rows, settings.max_result_rows)
    # DÖNEMSEL KIYAS (YoY/MoM chip'i): cube_query.compare varsa period-shift ile iki seri
    # + %değişim (app.yoy). parse compare'ı düşürebilir → body'den okunur.
    _cmp = (body.cube_query or {}).get("compare")
    if _cmp in ("yoy", "mom"):
        tdn = yoy.time_dim_of(schema, cq.get("cube"))
        out = yoy.compute(service, {**cq, "compare": _cmp}, _cmp, tdn, limit=limit)
        sql = out["base_sql"]
        planned = service.dry_plan(sql)
        result = {"columns": out["columns"], "rows": out["rows"], "row_count": out["row_count"]}
        cq = {**out["base_cq"], "compare": _cmp}
        trace_msg = f"chip düzenleme → dönemsel kıyas ({_cmp}, LLM'siz)"
    # CROSS-CUBE BLEND: chip düzenlemesi blend içeriyorsa (ölçü ekle/çıkar) blend_sql ile
    # birleştir (agregat → limit'siz, WITH+FOJ limit sarmalayıcısını bozuyor).
    elif cq.get("blend"):
        sql = service.blend_sql(cq)
        planned = service.dry_plan(sql)
        result = service.query(sql)
        trace_msg = "chip düzenleme → cross-cube blend"
    else:
        sql = service.cube_sql(cq)
        planned = service.dry_plan(sql)
        result = service.query(sql, limit=limit)
        trace_msg = "chip düzenleme → deterministik cube"
    resp = AskResponse(
        question=body.label or "(chip düzenleme)",
        sql=sql,
        planned_sql=planned,
        result=QueryResult(**result),
        source="cube",
        cube_query=cq,
        trace=[trace_msg],
    )
    # VİZ ÖNERİSİ (ADR-0024): chip düzenlemesi de grafik/tablo/pivot kararı taşır.
    try:
        cmeta = next(
            (c for c in (schema.get("cubes") or []) if c.get("name") == cq.get("cube")), None
        )
        resp.viz = viz.recommend(
            result,
            units=(cmeta or {}).get("measure_units") or {},
            lower_set=(cmeta or {}).get("lower_is_better") or [],
            cube_query=cq,
        )
    except Exception:
        pass
    # Query Contract (ADR-0010): chip düzenlemesi de rapor üretir → kanıt kaydı.
    if True:
        try:
            store = getattr(request.app.state, "contracts", None)
            if store is not None:
                _p = getattr(request.state, "principal", None)
                resp.contract_id = store.record(
                    session_id=body.session_id, question=resp.question, cube_query=cq,
                    sql=sql, result=result, source="cube", schema_version=service.mdl_version,
                    tenant_id=getattr(_p, "tenant_id", None),
                )
        except Exception:
            pass
    _maybe_interpret(request, resp)  # evrensel çıktı yorumu (feature flag'li)
    _attach_next_steps(request, resp)  # K2 sonraki-adım chip'leri (feature flag'li)
    _attach_recommendations(request, resp)  # K4 sinyal→aksiyon önerileri
    _persist_message(request, resp, body.session_id)  # kalıcı sohbete yaz
    from types import SimpleNamespace

    principal = getattr(request.state, "principal", None)
    _log_interaction(
        body.session_id,
        SimpleNamespace(question=resp.question, cube_query=cq),  # type: ignore[arg-type]
        resp,
        int((time.monotonic() - t0) * 1000),
        principal,
    )
    # AUDIT (ADR-0014 Karar 6): her veri erişimi kanıtlanabilir iz bırakır.
    from control_plane import audit

    audit.record(principal, "query", nl_question=resp.question, generated_sql=sql,
                 rows_returned=result.get("row_count"), contract_id=resp.contract_id,
                 ip=request.client.host if request.client else None)
    return resp


@router.post("/report", dependencies=[Depends(require("query:run")),
                                      Depends(require_company)])
def report(request: Request, body: ReportRequest) -> dict:
    """Çok-blok / çok-SAYFA rapor derleme (ADR-0024, forward): her blok deterministik koşar +
    kendi grafik/tablo/pivot kararını (viz) alır → sayfalara bölünmüş Report. Panodan "raporu
    dışa aktar" (widget'lar → bloklar) ya da seçili sorgulardan; LLM yok. Blok cube_query'leri
    katalogla doğrulanır (bozuk blok atlanır)."""
    from app import report as report_mod

    service = _service_for(request, body.session_id)  # yüklenen dataset varsa onu sorgular
    schema = service.schema()
    _, index = cube_router.build_catalog(schema)
    spec_blocks: list[dict] = []
    for b in body.blocks:
        cqb = dict(b.cube_query or {})
        if cqb.get("cube"):
            cqb["cube"] = cube_router.resolve_cube_name(cqb["cube"], schema)
        cq = cube_router.parse_cube_query(json.dumps(cqb, ensure_ascii=False), index)
        if not cq:
            continue  # bozuk/eski widget cube_query'si raporu düşürmez
        # parse compare'ı düşürebilir → geri ekle (YoY widget rapora aktarılınca kıyas korunur).
        if cqb.get("compare") in ("yoy", "mom"):
            cq["compare"] = cqb["compare"]
        spec_blocks.append({"cube_query": cq, "title": b.title, "period": b.period,
                            "view_hint": b.view_hint})
    return report_mod.compose_report(
        service, schema,
        {"title": body.title, "blocks": spec_blocks, "page_size": body.page_size},
    )


@router.post("/verify", dependencies=[Depends(require("vqr:write")),
                                      Depends(require_company)])
def verify(request: Request, body: CubeRequest) -> dict:
    """Kullanıcı geri bildirimi (UI '✓ doğru' / '✗ yanlış' düğmeleri, beta bayrağı):

    - verdict=right (varsayılan): soru→CubeQuery çifti DOĞRULANMIŞ yazılır (VQR).
    - undo=true: daha önce doğrulanan çift GERİ ALINIR.
    - verdict=wrong: negatif sinyal — soruya yakın öğrenilmiş çift varsa SİLİNİR
      (yanlış replay kaynağı kurumasın); her durumda LOGLANIR (eval/log madenciliği).
    """
    if not body.label:
        raise HTTPException(status_code=400, detail="Soru (label) eksik.")
    service = _service_for(request, body.session_id)  # yüklenen dataset varsa onu sorgular
    _, index = cube_router.build_catalog(service.schema())
    cq = cube_router.parse_cube_query(json.dumps(body.cube_query, ensure_ascii=False), index)
    if not cq:
        raise HTTPException(status_code=400, detail="Geçersiz cube sorgusu.")

    # VQR (replay cache) KAPALI olsa bile geri bildirim KAYBOLMAZ: store/remove atlanır
    # ama sinyal her durumda loglanır (ADR-0008 log-madenciliği). Canlı 2026-07-25: VQR
    # None iken "yanlış" verdict'i 400'le düşüyor, negatif sinyal yutuyordu — asıl amaç bu.
    vqr = None if getattr(request.state, "wren", None) else getattr(request.app.state, "vqr", None)
    principal = getattr(request.state, "principal", None)
    stored = removed = False
    if vqr is not None:
        if body.undo or body.verdict == "wrong":
            removed = vqr.remove(body.label)
        else:
            stored = vqr.store(body.label, cq, source="user_verified",
                               extra={"verified_by": getattr(principal, "user_id", None),
                                      "tenant_id": getattr(principal, "tenant_id", None)})

    from types import SimpleNamespace

    verdict = "wrong" if body.verdict == "wrong" else ("undo" if body.undo else "right")
    comment = (body.comment or "").strip() or None  # ✗ yanlış'ta opsiyonel "neden" (#57 madenci)
    trace = [f"kullanıcı geri bildirimi → {verdict}"
             + (" · VQR çifti silindi" if removed else " · VQR'a yazıldı" if stored else "")
             + (f" · yorum: {comment}" if comment else "")]
    _log_interaction(
        body.session_id,
        SimpleNamespace(question=f"verify[{verdict}]: {body.label}", cube_query=cq),  # type: ignore[arg-type]
        SimpleNamespace(source="verify", sql=None, result=None,
                        note=(comment if verdict == "wrong" else None),
                        cube_query=cq, trace=trace),  # type: ignore[arg-type]
        0,
        principal,
    )
    from control_plane import audit

    audit.record(principal, "verify",
                 nl_question=f"[{verdict}] {body.label}" + (f" · {comment}" if comment else ""),
                 ip=request.client.host if request.client else None)
    return {"stored": stored, "removed": removed}



import json
import os
import hashlib
import json
import os
import hashlib
from openai import OpenAI

LLM_MODEL = os.getenv("DIMA_OPENROUTER_MODEL", "gpt-4o")

def call_llm_for_wren_sql(system_prompt: str, user_question: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key.startswith("${"):
        api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "")
        
    base_url = "https://openrouter.ai/api/v1" if api_key and api_key.startswith("sk-or") else None
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.0
    )
    raw = completion.choices[0].message.content or ""
    if "```sql" in raw:
        raw = raw.split("```sql")[1].split("```")[0]
    return raw.strip()

def fix_llm_sql(system_prompt: str, user_question: str, bad_sql: str, error_msg: str) -> str:
    prompt = f"""
    Sen DİMA Semantik SQL Ajanısın.
    Kullanıcının Sorusu: {user_question}
    Yazdığın Hatalı SQL: {bad_sql}
    Wren Engine Hata Mesajı: {error_msg}
    
    Lütfen hatayı düzelt ve sadece doğru Wren SQL kodunu dön.
    """
    return call_llm_for_wren_sql(system_prompt, prompt)

@router.post("/ask", response_model=AskResponse, dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask(request: Request, body: AskRequest) -> AskResponse:
    import time
    settings = get_settings()
    service = _service_for(request, body.session_id)
    schema = service.schema()
    
    t0 = time.monotonic()
    
    system_prompt = f"""
    Sen DİMA Semantik SQL Ajanısın.
    Aşağıdaki MDL Şemasını incele ve kullanıcının Türkçe sorusuna karşılık gelen geçerli bir Wren SQL yaz.
    KURALLAR:
    - SADECE MDL içindeki tanımlı model, metrik ve kolon isimlerini kullan.
    - Veritabanında olmayan tablo veya kolon uydurma.
    - Yanıt olarak SADECE saf Wren SQL kodu döndür, açıklama veya yorum ekleme.
    MDL ŞEMASI:
    {json.dumps(schema)}
    """
    
    wren_sql = call_llm_for_wren_sql(system_prompt, body.question)
    
    try:
        service.dry_plan(wren_sql)
    except Exception as e:
        wren_sql = fix_llm_sql(system_prompt, body.question, wren_sql, str(e))
        service.dry_plan(wren_sql)
        
    result = service.query(wren_sql)
    
    resp = AskResponse(
        question=body.question,
        sql=wren_sql,
        source="llm:cortex",
        result=QueryResult(**result) if result else None
    )
    
    _persist_message(request, resp, body.session_id)
    
    principal = getattr(request.state, "principal", None)
    _log_interaction(body.session_id, body, resp, int((time.monotonic() - t0) * 1000), principal)
    
    return resp

