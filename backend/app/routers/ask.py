"""Natural-language → SQL → result endpoint (the demo's headline flow)."""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from app import cube_router, pii, viz, yoy
from app.answer import (
    _attach_next_steps,
    _attach_recommendations,
    _build_explain,
    _log_interaction,
    _maybe_interpret,
    _persist_message,
    _source_kind,
    record_contract,
    seal,
)
from app.auth.dependencies import require, require_company
from app.config import get_settings
from app.llm import RuleBasedSqlGenerator
from app.logging_setup import get_logger
from app.schemas import (
    AskJobStatus,
    AskRequest,
    AskResponse,
    AskVerifyRequest,
    ContributionReport,
    ContributionRequest,
    ContributionResponse,
    CubeRequest,
    DrillRequest,
    DrillResponse,
    Explain,
    PvmReport,
    QueryResult,
    RawRow,
    ReportRequest,
    Suggestion,
    UploadRequest,
    UploadResponse,
)
from app.wren_service import UnsafeSqlError

router = APIRouter(tags=["ask"])
_log = get_logger("ask")  # system/app log (ADR-0020): best-effort bloklar sessizce yutmaz


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


def _capture_measure_candidate(question: str, sql: str, result: dict, principal=None) -> None:
    """Discovery→Promote yakalama (Faz 2d): başarılı bir Discovery (ham-SQL LLM) cevabını
    best-effort bir `MeasureCandidate` taslağı olarak DB'ye yazar (status='draft'). Yalnız
    YAKALAMA — inceleme/onay/MDL-yazımı tamamen AYRI (app/routers/measures.py), burada hiçbir
    doğrulama/dry_plan YAPILMAZ (onay anında yapılır). `SynonymOverride`'ın (ADR-0018) aday-
    kuyruğu deseniyle AYNI ruhta: pasif, sessiz, kullanıcı akışını YAVAŞLATMAZ — `_record_
    contract` ile AYNI best-effort try/except deseni. Ham SONUÇ SATIRLARI TUTULMAZ (yalnız
    ilk ~5 örnek — reviewer bağlamı için; KVKK/hassas-veri sınırı InteractionLog ile AYNI)."""
    try:
        import json as _json

        from sqlmodel import Session

        from control_plane.db import engine
        from control_plane.models import MeasureCandidate

        sample = {"columns": result.get("columns"), "rows": (result.get("rows") or [])[:5]}
        with Session(engine) as s:
            s.add(MeasureCandidate(
                tenant_id=_uuid_or_none(getattr(principal, "tenant_id", None)),
                company=getattr(principal, "tenant_slug", None) or get_settings().company,
                question=question, sql=sql,
                sample_rows_json=_json.dumps(sample, ensure_ascii=False, default=str),
                proposed_by=getattr(principal, "user_id", None),
            ))
            s.commit()
    except Exception:
        _log.warning("MeasureCandidate yakalaması başarısız (best-effort)", exc_info=True)


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
    if type(last).__name__ == "AnthropicSqlGenerator":
        return "llm:anthropic"
    # Son-çare: `_provider` yok VE bilinen bir tür değil. ÇIPLAK "llm" (":" YOK) döndürmek
    # frontend'in SourceBadge'inde (ChatPanel.tsx, `source.startsWith("llm:")`) yakalanmıyor
    # ve yanlışlıkla "⚙ KURAL" (LLM kullanılmadı) etiketine düşüyordu — bir LLM cevabı
    # deterministik gösteriliyordu. Tür adı her zaman ":" taşıyacak şekilde eklenir.
    return f"llm:{type(last).__name__}"


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
    _log.info("İSTEK /ask/upload: filename=%r session=%s boyut=%dB",
              body.filename, body.session_id, len(body.content_b64 or ""))
    try:
        raw = base64.b64decode(body.content_b64, validate=True)
    except Exception:
        _log.warning("/ask/upload: geçersiz base64 (filename=%r)", body.filename, exc_info=True)
        raise HTTPException(status_code=400, detail="Geçersiz base64 içerik")
    if len(raw) > _MAX_UPLOAD:
        _log.warning("/ask/upload: dosya çok büyük (%dB > %dB, filename=%r)",
                    len(raw), _MAX_UPLOAD, body.filename)
        raise HTTPException(status_code=413,
                            detail=f"Dosya çok büyük (>{_MAX_UPLOAD // 1024 // 1024} MB)")
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", body.session_id)[:80]
    label = Path(body.filename).stem[:40] or "veri"
    try:
        info = dataset.ingest_file(raw, body.filename, _UPLOAD_DIR / safe)
        mdl = dataset.build_mdl(info, cube_name="veri", label=label)
        svc = dataset.build_service(_UPLOAD_DIR / safe, mdl)
    except Exception as exc:  # noqa: BLE001 — kullanıcıya dürüst hata, sunucuyu düşürme
        # ÖNCEDEN bu blok hiç loglamıyordu — dosya işleme (DuckDB ingest/MDL/servis kurulumu)
        # patladığında kullanıcı yalnız "Dosya işlenemedi" görürdü, sunucu tarafında İZ YOKTU.
        _log.warning("/ask/upload: dosya işlenemedi (filename=%r): %s", body.filename, exc,
                    exc_info=True)
        raise HTTPException(status_code=400, detail=f"Dosya işlenemedi: {str(exc)[:200]}")
    _dataset_store(request)[body.session_id] = {
        "service": svc, "info": info, "filename": body.filename}
    # Yükleme olayını telemetriye yaz (ADR-0020) — sorgu değil ama viewer'da görünmeli.
    _log_upload(body.session_id, body.filename, label, info["row_count"],
                len(info["columns"]), int((time.monotonic() - t0) * 1000),
                principal=getattr(request.state, "principal", None))
    _log.info("CEVAP /ask/upload: filename=%r satır=%s sütun=%s süre=%dms",
              body.filename, info["row_count"], len(info["columns"]),
              int((time.monotonic() - t0) * 1000))
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
    _log.info("İSTEK /cube: label=%r session=%s thread=%s cube=%s",
              body.label, body.session_id, body.thread_id, (body.cube_query or {}).get("cube"))
    settings = get_settings()
    service = _service_for(request, body.session_id)  # yüklenen dataset varsa onu sorgular
    schema = service.schema()

    _, index = cube_router.build_catalog(schema)
    if body.cube_query and body.cube_query.get("cube"):
        # cube adı göçü (yeniden adlandırma sonrası eski adla gelen chip düzenlemesi)
        body.cube_query["cube"] = cube_router.resolve_cube_name(body.cube_query["cube"], schema)
    cq = cube_router.parse_cube_query(json.dumps(body.cube_query, ensure_ascii=False), index)
    if not cq:
        _log.warning("/cube: geçersiz cube sorgusu, body=%r", body.cube_query)
        raise HTTPException(status_code=400, detail="Geçersiz cube sorgusu (chip düzenlemesi).")

    limit = min(body.limit or settings.max_result_rows, settings.max_result_rows)
    # DÖNEMSEL KIYAS (YoY/MoM chip'i): cube_query.compare varsa period-shift ile iki seri
    # + %değişim (app.yoy). parse compare'ı düşürebilir → body'den okunur.
    _cmp = (body.cube_query or {}).get("compare")
    # Derleme/ÇALIŞTIRMA hataları (canlı bulgu, 31 Temmuz 2026 — bkz. /ask Discovery
    # yolundaki AYNI sınıf düzeltme): `parse_cube_query` yalnız YAPIYI doğrular, motorun
    # gerçek çalıştırması (compare/blend kombinasyonu, dry_plan'ın yakalamadığı bir
    # çalıştırma-zamanı hatası) yine de patlayabilir — çıplak 500 yerine dürüst 400.
    try:
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
    except Exception as exc:
        _log.warning("chip düzenleme derleme/çalıştırma başarısız", exc_info=True)
        raise HTTPException(status_code=400,
                            detail=f"Bu düzenleme çalıştırılamadı: {str(exc)[:200]}")
    resp = AskResponse(
        question=body.label or "(chip düzenleme)",
        sql=sql,
        planned_sql=planned,
        result=QueryResult(**result),
        source="cube",
        cube_query=cq,
        trace=[trace_msg],
        thread_id=body.thread_id,
    )
    # VİZ ÖNERİSİ (ADR-0024): chip düzenlemesi de grafik/tablo/pivot kararı taşır.
    try:
        cmeta = next(
            (c for c in (schema.get("cubes") or []) if c.get("name") == cq.get("cube")), None
        )
        resp.viz = viz.recommend(
            result,
            # NOT (31 Temmuz 2026): "measure_units" YANLIŞ anahtardı — schema() dict'i
            # ölçü birimlerini "units" adıyla taşıyor (bkz. app/wren_service.py:236);
            # "measure_units" hiçbir zaman var olmadığından `recommend()`'in birim-
            # farkındalığı (facet_measure/dual_axis/partition rengi) burada da HİÇ
            # devreye giremiyordu — `_attach_viz`'teki AYNI hata sınıfı (bkz. yukarıdaki
            # `_attach_viz` docstring'i).
            units=(cmeta or {}).get("units") or {},
            lower_set=(cmeta or {}).get("lower_is_better") or [],
            cube_query=cq,
        )
    except Exception:
        # Grafik kararı DEKORATİFTİR — patlaması cevabı düşürmez. Ama SESSİZ de kalmaz
        # (ADR-0020): 2 Ağustos 2026'ya kadar burada çıplak `pass` vardı ve `viz` sürekli
        # başarısız olsa kimse fark etmezdi.
        _log.warning("/cube görselleştirme kararı başarısız (best-effort)", exc_info=True)
    # KAPANIŞ — `app/answer.py` üzerinden (Faz A4). Burası eskiden `/ask`'in `_finish`'inin
    # ELLE KOPYALANMIŞ ikiziydi ve iki yerde ayrışmıştı: contract kaydını
    # `except Exception: pass` ile SESSİZCE yutuyordu (ADR-0020 ihlali) ve
    # `is_new_topic`/`thread_id`/`reply_to_label` alanlarını HİÇ set etmiyordu.
    from types import SimpleNamespace

    resp.contract_id = record_contract(
        request, service=service, session_id=body.session_id, question=resp.question,
        cube_query=cq, sql=sql, result=result, source="cube")
    return seal(resp, request=request,
                principal=getattr(request.state, "principal", None), t0=t0,
                session_id=body.session_id,
                log_body=SimpleNamespace(question=resp.question, cube_query=cq),
                thread_id=body.thread_id, endpoint="cube")



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
    rep = report_mod.compose_report(
        service, schema,
        {"title": body.title, "blocks": spec_blocks, "page_size": body.page_size},
    )
    # PII maskeleme (doğrulama turu düzeltmesi, 1 Ağustos 2026): rapor derleme daha önce HİÇ
    # maskelemiyordu — `/ask` üzerinden maskeli görülen bir sorgu rapora konunca maskesiz
    # görünüyordu (`compose_report` "saf" bir fonksiyon olarak kalsın diye maskeleme BİLEREK
    # burada, HTTP sınırında uygulanır — `_finish()`/`/query` ile AYNI ilke).
    from app.pii import mask_query_result

    principal = getattr(request.state, "principal", None)
    any_unmasked = False
    for page in rep.get("pages") or []:
        for block in page:
            if block.get("result"):
                block["result"], unmasked = mask_query_result(block["result"], principal)
                any_unmasked = any_unmasked or unmasked
    if any_unmasked:
        from control_plane import audit

        audit.record(principal, "pii_view", nl_question=f"rapor · {body.title or 'Rapor'}",
                    ip=request.client.host if request.client else None)
    return rep


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
    #
    # ÖNCEDEN burada `None if getattr(request.state, "wren", None) else app.state.vqr`
    # vardı — bu, VARSAYILAN ŞİRKET DIŞINDAKİ HER tenant için VQR'ı sessizce tamamen
    # kapatıyordu (request.state.wren yalnız non-default tenant'ta set edilir; "wren
    # strict mode" ile ilgisi yok). Sonuç: öğrenme döngüsü tek şirket dışında hiç
    # çalışmıyordu. vqr_for_request artık her tenant için kendi VQR'ını (registry'de
    # slug-bazlı önbelleklenmiş) döndürür — bkz. company_registry.vqr_for.
    from app.company_registry import vqr_for_request

    vqr = vqr_for_request(request)
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
                        cube_query=cq, trace=trace, interpretation=None),  # type: ignore[arg-type]
        0,
        principal,
    )
    from control_plane import audit

    audit.record(principal, "verify",
                 nl_question=f"[{verdict}] {body.label}" + (f" · {comment}" if comment else ""),
                 ip=request.client.host if request.client else None)
    return {"stored": stored, "removed": removed}



def _resolve_entity_limit(service, cq: dict, order, limit: int | None) -> str | None:
    """route()'un ürettiği ``entity_limit``'li CubeQuery için İKİ-ADIMLI SQL üretir
    (Faz 1 — eski 1800 satırlık kaldırılmış `/ask` işleyicisindeki mekanizmanın yeniden
    inşası; git tarihinde hayatta kalan bir sürümü yoktu).

    Neden iki adım: "ilk 3 müşterinin aylık cirosu" gibi bir soruda tek adımda LIMIT 3
    uygulamak zaman×varlık satırlarını keser (LIMIT ilk ayın 3 satırını alır, 3 MÜŞTERİ
    değil). Çözüm: (1) zaman kovası OLMADAN yalnız varlık×kıstas-ölçü ile top-N varlık
    bulunur, (2) TAM sorgu (zaman kovası dahil) o varlıklara `in` filtresiyle daraltılır.

    Herhangi bir adımda beklenmedik veri/hata olursa None döner — çağıran Discovery'ye
    düşer (asla yarım/yanlış SQL ile devam etmez)."""
    el = cq.get("entity_limit") or {}
    dim, crit, n = el.get("dimension"), el.get("measure"), el.get("n")
    direction = str(el.get("direction") or "desc").upper()
    if not (dim and crit and n):
        return None
    try:
        probe_cq: dict = {"cube": cq.get("cube"), "measures": [crit], "dimensions": [dim]}
        if cq.get("filters"):
            probe_cq["filters"] = list(cq["filters"])
        probe_sql = service.cube_sql(probe_cq, order=(crit, direction), limit=int(n))
        probe_result = service.query(probe_sql, limit=int(n))
        entities = [r.get(dim) for r in (probe_result.get("rows") or []) if r.get(dim) is not None]
        if not entities:
            return None
        full_cq = {k: v for k, v in cq.items() if k != "entity_limit"}
        kept_filters = [f for f in (full_cq.get("filters") or []) if f.get("dimension") != dim]
        kept_filters.append({"dimension": dim, "operator": "in", "value": entities})
        full_cq["filters"] = kept_filters
        sql = service.cube_sql(full_cq, order=order, limit=limit)
        # ÇAĞIRANIN cq'sini YERİNDE çözülmüş şekille günceller (entity_limit → gerçek
        # `in` filtresi): AskResponse.cube_query yalnız SQL'i değil GERÇEKTEN NEYİN
        # çalıştırıldığını yansıtsın — aksi halde bir takip mesajı bu raporu devam
        # ettirirken hâlâ çözülmemiş `entity_limit` şeklini görür (deterministic_refine
        # onu farklı yorumlayabilir), ve şeffaflık ilkesi (Query Contract) bozulur.
        cq.pop("entity_limit", None)
        cq["filters"] = kept_filters
        return sql
    except Exception:
        _log.warning("entity_limit iki-adımlı çözümleme başarısız (best-effort)", exc_info=True)
        return None


def recover_stale_ask_jobs() -> int:
    """Faz 4.1 — süreç başlangıcında (app/main.py lifespan) çağrılır: önceki çalıştırmadan
    `pending`/`running` kalmış AskJob satırları (süreç Discovery ORTASINDAYKEN çökmüş
    demektir — thread'le birlikte sessizce yok oldu) dürüst bir `failed`e çevrilir.
    Kullanıcı soruyu yeniden sorar (bkz. control_plane/models.py::AskJob docstring'i —
    bu ilk sürümde TAM "kaldığı yerden devam" YOK, bilinçli kapsam sınırı). `replay_spool`/
    `replay_contract_spool` ile AYNI "başlangıçta yarım kalanı temizle" deseni. Döner:
    kaç iş kurtarıldı (log/gözlem için)."""
    try:
        from sqlmodel import Session, select

        from control_plane.db import engine
        from control_plane.models import AskJob

        with Session(engine) as s:
            stale = s.exec(select(AskJob).where(
                AskJob.status.in_(["pending", "running"]))).all()
            for j in stale:
                j.status = "failed"
                j.error = "Sunucu yeniden başlatıldı, iş yarıda kaldı. Soruyu tekrar sorar mısın?"
                j.finished_at = datetime.utcnow()
                s.add(j)
            if stale:
                s.commit()
            return len(stale)
    except Exception:
        _log.warning("AskJob kurtarma taraması başarısız (best-effort)", exc_info=True)
        return 0


def _with_extra_context(question: str, extra_context: list[str] | None) -> str:
    """§B düzeltmesi (1 Ağustos 2026) — çoklu-seçim birleşik bağlam: kullanıcının thread
    içinde seçtiği DİĞER kartların kısa özetlerini YALNIZ Discovery'ye giden LLM prompt
    metnine ekler (grounding). Çağıranlar (`resp.question`, `vqr.few_shot_block`,
    `vqr.store`) HİÇBİRİ bunu görmez — yalnız `llm.generate_sql`/`llm.generate_followup_sql`'e
    VERİLEN argüman değişir; ham `body.question` her yerde OLDUĞU GİBİ kalır. Deterministik
    cube-routing/Intent-JSON yoluna (route/deterministic_refine/select_cube/refine_cube)
    BİLEREK karışmaz (golden-eval hassasiyeti). Boşsa/None ise no-op."""
    if not extra_context:
        return question
    grounding = "\n".join(f"- {c}" for c in extra_context)
    return f"Ek bağlam (kullanıcının seçtiği ilgili önceki sorular/sonuçlar):\n{grounding}\n\nSoru: {question}"


def _queue_discovery_job(request: Request, body: AskRequest, principal, runner) -> AskResponse:
    """Faz 4.1 (dış yol haritası 0.1'in BullMQ/Redis'siz karşılığı) — Discovery'yi arka-plan
    işine kuyruklar (yalnız `ask_async_discovery` bayrağı açıkken çağrılır). `CloneJob` ile
    AYNI desen (control_plane/models.py::AskJob docstring'i): DB-tablosu tabanlı durum +
    thread — in-memory DEĞİL, süreç yeniden başlasa da iz bırakır.

    `runner` (ask()'in `_run_discovery` kapanışı) zaten `service`/`schema`/`vqr`/`llm`/
    `principal`/`body`'yi KAPANIŞ olarak taşıyor — CloneJob'un aksine bunları TEKRAR DB'den
    türetmeye GEREK YOK: iş aynı süreçte, aynı anda başlıyor (yalnız İSTEMCİYE hemen dönmek
    için arka plana alınıyor), request-bağımsız yeniden-kurulum gerektirmiyor. Süreç bu iş
    bitmeden ÇÖKERSE (`app/main.py` lifespan'daki kurtarma), iş "yarıda kaldı" diye dürüstçe
    `failed`e çevrilir — sessizce kaybolmaz, ama otomatik yeniden-deneme bu ilk sürümde
    kapsam dışı (bilinçli sınır, AskJob docstring'inde gerekçeli)."""
    import json as _json
    import threading
    import uuid as _uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import AskJob

    tenant_id_raw = getattr(principal, "tenant_id", None)
    try:
        tenant_uuid = _uuid.UUID(str(tenant_id_raw)) if tenant_id_raw else None
    except (ValueError, TypeError):
        tenant_uuid = None

    job = AskJob(
        tenant_id=tenant_uuid, session_id=body.session_id, question=body.question,
        request_json=_json.dumps({"question": body.question, "session_id": body.session_id},
                                 ensure_ascii=False),
    )
    with Session(engine) as s:
        s.add(job)
        s.commit()
        s.refresh(job)
    job_id = job.id

    def _on_step(trace: list[str]) -> None:
        """Faz 4.12 — HER Discovery adımından sonra çağrılır, job satırına ANINDA yazar
        (best-effort: bir yazım başarısız olursa Discovery'yi DURDURMAZ, yalnız o adımın
        canlı görünürlüğü kaybolur — sonuç yine de tamamlanınca result_json'da tam gelir)."""
        try:
            import json as _json
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                if j is not None:
                    j.trace_json = _json.dumps(trace, ensure_ascii=False)
                    s.add(j)
                    s.commit()
        except Exception:
            _log.warning("AskJob canlı adım yazımı başarısız (best-effort)", exc_info=True)

    def _bg() -> None:
        with Session(engine) as s:
            j = s.get(AskJob, job_id)
            j.status = "running"
            j.started_at = datetime.utcnow()
            s.add(j)
            s.commit()
        try:
            resp = runner(on_step=_on_step)
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                j.status = "completed"
                j.result_json = resp.model_dump_json()
                j.finished_at = datetime.utcnow()
                s.add(j)
                s.commit()
        except Exception as exc:  # noqa: BLE001 - arka-plan işi ASLA sessizce kaybolmaz
            _log.warning("AskJob arka-plan çalıştırması başarısız", exc_info=True)
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                j.status = "failed"
                j.error = str(exc)[:500]
                j.finished_at = datetime.utcnow()
                s.add(j)
                s.commit()

    threading.Thread(target=_bg, daemon=True).start()
    return AskResponse(
        question=body.question, source=None, job_id=str(job_id),
        note="Bu soru arka planda hazırlanıyor…",
        trace=["Discovery: arka-plan işine kuyruklandı (ask_async_discovery)"],
    )


@router.post("/ask", response_model=AskResponse,
             dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask(request: Request, body: AskRequest) -> AskResponse:
    """NL→cevap: Intent-first yönlendirme (Faz 1 + Faz 1.5 — ADR: vizyon-yol-haritası,
    Cube.dev/WrenAI'nin "text-to-semantic-query" ilkesi). LLM'in rolü varsayılan olarak SQL
    YAZARLIĞINDAN niyet SEÇİCİLİĞİNE çekilir; ham-SQL üretimi artık kapsam-dışı sorular için
    AÇIKÇA ETİKETLİ bir "Discovery" istisnasıdır.

    Faz 1.5 (31 Temmuz 2026): `cube_router.py`'nin TAMAMI okunup denetlendi — deterministik
    takip-düzenleme (`deterministic_refine`), çapraz-cube ekleme/geçiş, dönemsel kıyas
    (YoY/MoM), ve kısmi-anlama/çapraz-konu netleştirme mekanizmaları ZATEN vardı, test edilmiş
    ve olgun ama strict-agentic göçünden beri `/ask`'e hiç bağlanmamıştı. Bu fonksiyon artık
    hepsini birleştiriyor — YENİ mantık icat edilmedi, var olan mükemmel-ama-kopuk parçalar
    doğru sırayla bağlandı (bkz. tests/test_ask_golden.py — bu testler beklenen davranışın
    canlı kanıtı, gerçek demo projesine karşı doğrulandı).

    Sıra (her adım bir öncekinin başarısız/uygunsuz olmasıyla tetiklenir):
    1. Meta/katalog soruları → deterministik yanıt (LLM YOK).
    2. BAĞIMSIZ (takip olmayan) sorularda VQR birebir/yakın eşleşme → önceden doğrulanmış
       SQL tekrar oynatılır (LLM YOK).
    3. YAPISAL TAKİP (body.cube_query + history dolu — önceki tur gerçek bir CubeQuery
       ürettiyse): `deterministic_refine` (LLM'siz düzenleme: ölçü değişimi/çıkarma,
       kırılım, dönem, sıralama, top-N) → `cross_cube_add` (blend) → `cross_cube_dim_switch`
       (konu değişti notu) → LLM-destekli yapısal düzenleme (`llm.refine_cube`, hâlâ SQL
       DEĞİL) → hiçbiri olmazsa `_try_fresh_intent()` son kez denenir → HÂLÂ boşsa artık
       DÜRÜST RET DEĞİL, Discovery'ye (ham-SQL, taze — stale prev_sql'e çapalanmadan) düşülür
       (1 Ağustos 2026 düzeltmesi: canlı bulgu — aynı soru taze/yeni-thread'den sorulunca
       Discovery cube sınırlarının ÖTESİNDE serbest join ile gerçekten cevaplayabiliyordu,
       yapısal takip zinciri eskiden bu noktada köre dürüst ret veriyordu).
    3b. RAW TAKİP (yalnız body.prev_sql + history dolu, cube_query YOK — önceki tur Discovery
       ürettiyse): Discovery'nin ham-SQL "takip düzenlemesi"ne (§5, prev_sql bağlamlı) düşmeden
       ÖNCE `_try_fresh_intent()` bir kez denenir — "raw_followup tuzağı" düzeltmesi (1 Ağustos
       2026): eskiden bu satır HİÇ çalışmazdı, bir thread'in İLK turu Discovery'ye düşerse o
       thread SONSUZA KADAR route()/Intent-JSON'a dönemezdi, konu tamamen değişse bile.
    4. FRESH (bağımsız) soru — Intent-first:
       a. `cube_router.route()` — SIFIR-LLM deterministik CubeQuery eşleştirme.
       b. Dönemsel kıyas niyeti (`compare_mode`: "geçen yıla göre") → `strip_compare` +
          `route()` + `app.yoy.compute` — YİNE LLM'siz, deterministik period-shift.
       c. route() boş dönerse VE `ask_intent_first` bayrağı açıksa: LLM'e SQL DEĞİL,
          Intent-JSON doldurttur (`llm.select_cube`), `parse_cube_query` ile doğrula.
       d. Hâlâ boşsa: `measure_cube_candidates`/`partial_unknowns` ile NEDEN-özel
          netleştirme chip'i (çapraz-konu ya da kısmi-anlama) — Discovery'ye köre düşmeden.
    5. Discovery: yukarıdakiler kapsamadıysa — VQR few-shot + business_rules/golden_sql ile
       LLM ham Wren SQL üretimi → dry_plan doğrulama → self-healing (repair). Üretim
       başarısız olursa (rule/NoLlm sağlayıcı ya da tüm sağlayıcılar tükendi) 502 DEĞİL,
       dürüst ret notu döner.
    6. Başarılı BAĞIMSIZ yanıt VQR'a otomatik yazılır — Intent-path'te yalnız LLM
       kullanıldıysa (route() zaten ücretsiz, tekrar önbelleklemeye gerek yok).
    7. Her yanıt bir Query Contract + access-audit kaydı alır ve `viz.recommend` ile grafik
       önerisi eklenir (gerçek cube_query varsa daha isabetli karar).
    """
    import time

    from app.features import resolve_for
    from app.llm import reset_llm_usage

    t0 = time.monotonic()
    reset_llm_usage()
    settings = get_settings()
    service = _service_for(request, body.session_id)
    schema = service.schema()
    q_norm = cube_router._norm(body.question)
    principal = getattr(request.state, "principal", None)
    limit = min(body.limit or settings.max_result_rows, settings.max_result_rows)

    # Önceki tur bağlamı — İKİ ayrı mekanizma, `cube_query` YAPISAL (önceki tur Intent-path
    # ürettiyse) tercih edilir: deterministic_refine/cross_cube_* gibi zengin, LLM'siz
    # düzenleme mümkün kılar. `prev_sql` yalnız ham-SQL (Discovery) devamı içindir — önceki
    # tur Intent-path DEĞİLSE (structural veri yoksa) buna düşülür.
    prev_sql = body.prev_sql
    # `cube_query` TEK BAŞINA yeterli sinyal — çağıran (frontend/test) onu bilerek
    # gönderiyor demektir ("bu rapora devam"), `history` dolu olması ŞART değil (gerçek
    # eval koşumu bunu ortaya çıkardı: conftest.py'nin `ask()` yardımcısı history
    # göndermeden cube_query gönderiyor — history yalnızca ham-SQL takibi için ek sinyal).
    structural_followup = bool(body.cube_query)
    raw_followup = bool(prev_sql) and bool(body.history) and not structural_followup
    is_followup = structural_followup or raw_followup
    prev_question = body.history[-1] if body.history else ""

    # İSTEK GELDİ (1 Ağustos 2026, kullanıcı talebi: "her girdiyi net şekilde loglayalım").
    # Kapsamlı görünürlük için TEK giriş noktası — soru+bağlam sinyalleri (LLM'e mi düşecek,
    # yapısal takip mi, hangi thread) `_finish()`'teki "cevap gönderildi" logunun eşi.
    _log.info("İSTEK /ask: q=%r session=%s thread=%s followup=%s(yapısal=%s ham=%s)",
              body.question, body.session_id, body.thread_id, is_followup,
              structural_followup, raw_followup)

    def _finish(resp: AskResponse) -> AskResponse:
        """`/ask`'in kapanışı — gövdesi `app/answer.py::seal`'dedir (Faz A4).

        Eskiden 55 satırlık bir CLOSURE'dı ve tam da bu yüzden `/cube` kendi kopyasını
        yazmak, `_try_kpi` de onu atlamak zorunda kalmıştı. Artık tek gövde; buradaki
        iş yalnız `/ask`'e özgü bağlamı (takip sinyali, thread çapası) geçirmek."""
        return seal(resp, request=request, principal=principal, t0=t0,
                    session_id=body.session_id, log_body=body,
                    thread_id=body.thread_id, reply_to_label=body.reply_to_label,
                    is_new_topic=not is_followup, endpoint="ask")

    def _attach_viz(resp: AskResponse, result: dict | None, cq: dict | None = None) -> AskResponse:
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
        units: dict = {}
        lower_set: list = []
        if cq and cq.get("cube"):
            cube_meta = cube_router._cube_meta(schema, cq["cube"])
            if cube_meta:
                units = cube_meta.get("units") or {}
                lower_set = cube_meta.get("lower_is_better") or []
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
                try:
                    origin = cube_meta.get("dimension_origin") or {}
                    satir = [
                        f"“{cube_meta.get('dimension_labels', {}).get(d, d)}” boyutu "
                        f"{origin[d]['model']}.{origin[d]['column']} kolonundan, "
                        f"{origin[d]['relationship']} ilişkisi üzerinden geldi "
                        f"({origin[d].get('hops', 1)} sıçrama)."
                        for d in (cq.get("dimensions") or []) if d in origin
                    ]
                    if satir:
                        resp.calculation_explanation = " ".join(
                            filter(None, [resp.calculation_explanation, *satir]))
                except Exception:
                    _log.warning("join soyağacı üretilemedi (best-effort)", exc_info=True)
        try:
            resp.viz = viz.recommend(result, units=units, lower_set=lower_set, cube_query=cq)
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

    def _record_contract(cq: dict | None, sql: str | None, result: dict | None,
                         source: str) -> str | None:
        """Gövde `app/answer.py::record_contract`'ta — TEK uygulama (Faz A4)."""
        return record_contract(request, service=service, session_id=body.session_id,
                               question=body.question, cube_query=cq, sql=sql,
                               result=result, source=source)

    def _honest_refusal(note: str, trace: list[str],
                        suggestions: list[Suggestion] | None = None) -> AskResponse:
        """Dürüst ret — NoLlmGenerator'ın kendi docstring'inin vaat ettiği ama strict-agentic
        göçünde hiç uygulanmayan dönüşüm ("routers/ask.py bunu dürüst redde çevirir").
        ÖNCEDEN generate_sql/generate_followup_sql/refine_cube başarısızlığı 502 fırlatıyordu
        — kullanıcıya çökme gibi görünen bir hata. "Anlaşılmadı" bir SİSTEM HATASI değil,
        dürüstçe söylenecek bir sonuçtur (source=None, sql yok, çökme yok)."""
        return _finish(AskResponse(question=body.question, source=None, note=note,
                                   suggestions=suggestions or [], trace=trace))

    def _period_gate(cq: dict, cube_meta: dict | None, period_optional: bool | None,
                     trace_prefix: str) -> AskResponse | None:
        """DÖNEM BELİRSİZLİĞİ KAPISI — route()/YoY/LLM-select/takip-düzenleme HANGİ yoldan
        gelirse gelsin AYNI kural: zaman boyutu var, period_optional DEĞİL, hiç dönem
        filtresi/kırılımı yok VE kullanıcı hiçbir dönem ifadesi kullanmadıysa sessizce tüm-
        zamanlar varsayma — SOR. Zaman KIRILIMI (timeDimensions, "aylık trend") İSTİSNA:
        kendi başına anlamlı bir varsayılan taşır (mevcut tüm geçmiş üzerinden trend)."""
        if period_optional is None:
            period_optional = cube_router.is_period_optional(
                (cq.get("measures") or [None])[0], cube_meta)
        time_dims = (cube_meta or {}).get("time_dimensions") or []
        # `period_confirmed`: "Tümü" chip'i BİR KEZ tıklanır (needs_period docstring'i,
        # deterministic_refine is_all_time kolu) — deepcopy(prev) ile SONRAKİ her takip
        # düzenlemesine (yeni cq teknik olarak "farklı" olsa da) taşınır, tekrar sorulmaz.
        if cq.get("period_confirmed") or period_optional or not time_dims or cq.get("timeDimensions"):
            return None
        time_dim = time_dims[0]
        has_period_filter = any(f.get("dimension") == time_dim for f in (cq.get("filters") or []))
        if has_period_filter or cube_router._period_hit_words(q_norm):
            return None
        return _finish(AskResponse(
            question=body.question, source=None, note=_PERIOD_TEXT, cube_query=cq,
            suggestions=[Suggestion(**s) for s in _PERIOD_SUGGESTIONS],
            trace=[f"{trace_prefix}: dönem belirsiz → netleştirme (LLM'siz)"],
        ))

    def _answer_from_cube_query(cq: dict, *, order=None, limit_val: int | None = None,
                                source: str, trace: list[str], note: str | None = None,
                                learn: bool = False) -> AskResponse | None:
        """CubeQuery → derle+doğrula+çalıştır+yanıtla ORTAK son adım — route()/YoY/LLM-
        select/takip-düzenleme (deterministic_refine/cross_cube_*) hepsi buraya çıkar. TEK
        yerde durur ki entity_limit/blend özel çözümü, VQR öğrenme, Query Contract, viz her
        yeni Intent-path kaynağında yeniden yazılmasın (Faz 1'de zaten kopya kod riski
        vardı, Faz 1.5'te dört kaynak daha eklenince tek helper'a çıkarıldı).
        Derleme/doğrulama başarısız olursa None döner (çağıran sıradaki adıma düşer)."""
        try:
            if "entity_limit" in cq:
                sql = _resolve_entity_limit(service, cq, order, limit_val or limit)
            elif cq.get("blend"):
                sql = service.blend_sql(cq)
            else:
                sql = service.cube_sql(cq, order=order, limit=limit_val)
            if not sql:
                return None
            planned = service.dry_plan(sql)
            # `execute=False` → "yalnız üret + doğrula" (AskRequest.execute sözleşmesi).
            # 2 Ağustos 2026: bu bayrak ŞEMADA tanımlıydı ama /ask onu HİÇ OKUMUYORDU —
            # `body.execute` dosyada sıfır kez geçiyordu. Sonucu yalnız ölü bir API
            # sözleşmesi değildi: ölçüm harness'i `lab/nl_corpus.py` (ki kendi docstring'i
            # "DB'ye BAĞLANMAZ — execute=False" diyor) DuckDB olmayan HER şirkette
            # çalıştırma adımında patlıyor, cevap Discovery'ye düşüyor ve yönlendirme
            # başarısı %0 ölçülüyordu (atiksan/gulteks/gitas). Yani planın ana ölçüm
            # aracı, ölçtüğünü sandığı şeyi ölçmüyordu.
            result = service.query(sql, limit=limit) if body.execute else None
        except Exception:
            _log.warning(f"{source}: derleme/çalıştırma başarısız (best-effort)", exc_info=True)
            return None
        resp = AskResponse(
            question=body.question, sql=sql, planned_sql=planned,
            result=QueryResult(**result) if result else None,
            source=source, cube_query=cq, note=note, trace=trace,
        )
        # PANELLİ görünüm niyeti ("her X için ayrı ayrı grafik") — açık NL niyeti, hem
        # taze hem takip yolunda AYNI şekilde geçerli → tek ortak noktada çözülür.
        cq_meta = next((c for c in (schema.get("cubes") or [])
                        if c.get("name") == cq.get("cube")), None)
        if cq_meta:
            try:
                resp.view_hint = cube_router.detect_facet(q_norm, cq_meta)
            except Exception:
                _log.warning("facet görünüm tespiti başarısız (best-effort)", exc_info=True)
        # Faz 4.4 (31 Temmuz 2026) — GRAFİK TİPİ isteği ("pasta grafik olarak göster", "tablo
        # olarak"): `_viz_hint()`/`_VIZ_MAP` (yukarıda) TANIMLIYDI ama hiçbir yerden
        # ÇAĞRILMIYORDU (ölü kod). Panelli görünüm (facet, üstte) YAPISAL bir kırılım isteğidir
        # ve ÖNCELİKLİDİR; bu yalnız facet TESPİT EDİLMEDİYSE devreye girer — ikisi ÇAKIŞMAZ,
        # TAMAMLAYICI (biri panel-görünümü, diğeri grafik-TİPİ niyeti).
        if not resp.view_hint:
            resp.view_hint = _viz_hint(q_norm)
        if learn and vqr is not None:
            try:
                # `auto_cube` (Faz 4.1): saklanan SQL, LLM'in serbest metni DEĞİL —
                # katalogla doğrulanmış bir CubeQuery'den DERLENMİŞ SQL. Tekrar
                # oynatılabilir (bkz. app/vqr.py `_TRUSTED_SOURCES`).
                vqr.store(body.question,
                          {"wren_sql": sql, "mdl_version": service.mdl_version},
                          source="auto_cube")
            except Exception:
                _log.warning("VQR otomatik kayıt başarısız (best-effort)", exc_info=True)
        resp.contract_id = _record_contract(cq, sql, result, source)
        return _finish(_attach_viz(resp, result, cq))

    # 1) Deterministik ön-kapı — WrenAI'nin intent_classification'ının LLM'siz Dima
    # karşılığı: meta/ürün soruları ve katalog-keşfi SQL üretimine hiç girmez.
    if _is_meta(q_norm):
        return _finish(AskResponse(
            question=body.question, source="meta", note=_META_TEXT,
            suggestions=[Suggestion(**s) for s in _META_SUGGESTIONS],
            trace=["meta soru → deterministik yanıt (LLM'siz)"],
        ))
    if _is_catalog_query(q_norm):
        return _finish(AskResponse(
            question=body.question, source="catalog", note=_catalog_listing(schema),
            suggestions=[Suggestion(**s) for s in _catalog_all_suggestions(schema)],
            trace=["katalog keşfi → deterministik yanıt (LLM'siz)"],
        ))

    # 1b) GL YAPISAL RAPOR (gelir tablosu / bilanço, Faz 2a) — route()'tan/VQR'dan ÖNCE
    # denenir: "gelir tablosu" içindeki "gelir" kelimesi parti/ticaret cube'larının da
    # ölçü sinonimidir (toplam_ciro) — route() bunu YANLIŞ cube'a yönlendirip dönem
    # sorardı (gerçek eval bulgusu: ny-gelir-tablosu). GL raporu tamamen ayrı, zaten test
    # edilmiş deterministik bir mekanizma (app/statements.py) — cube-eşleştirmeyle hiç
    # karışmamalı, LLM'e hiç düşmemeli. Tenant'ta `mizan` cube'u yoksa (GL bağlı değil)
    # sessizce normal akışa düşer.
    stmt_kind = _statement_kind(q_norm)
    if stmt_kind:
        try:
            from app import statements

            stmt_cq = {"cube": "mizan", "measures": ["bakiye"], "dimensions": ["hesap_kodu"]}
            out = statements.resolve_statement(service, stmt_kind)
            planned = service.dry_plan(out["sql"])
            qr = _statement_result(out)
            result = {"columns": qr.columns, "rows": qr.rows, "row_count": qr.row_count}
            resp = AskResponse(
                question=body.question, sql=out["sql"], planned_sql=planned,
                result=qr, source="statement", cube_query=stmt_cq,
                trace=["GL yapısal rapor (gelir tablosu/bilanço) → deterministik (LLM'siz)"],
            )
            resp.contract_id = _record_contract(stmt_cq, out["sql"], result, "statement")
            # viz.recommend'e stmt_cq VERİLMEZ: sonuç tablosunun kolonları ("Kalem"/"Tutar
            # (₺)") mizan'ın ham kolonlarıyla (hesap_kodu/bakiye) eşleşmez — kolon-adı
            # sezgisiyle genel tablo analizine düşmesi daha DOĞRU (yanlış chip önerisi yok).
            return _finish(_attach_viz(resp, result))
        except Exception:
            _log.warning("GL yapısal rapor başarısız (best-effort) — normal akışa düşülüyor",
                        exc_info=True)

    from app.company_registry import vqr_for_request

    vqr = vqr_for_request(request)

    # 2) VQR: yalnız BAĞIMSIZ (takip olmayan) sorularda kontrol edilir — bir takip mesajı
    # ("aylara göre") bağlamsız haliyle BAŞKA bir konuşmadan gelen alakasız bir VQR kaydını
    # yanlışlıkla eşleştirip tekrar oynatabilirdi. İSTİSNA (Madde 9, 1 Ağustos 2026): kullanıcı
    # sohbet İÇİNDE bir ÖNCEKİ soruyu (normalize) BİREBİR tekrar ediyorsa bu "takip" DEĞİL,
    # "aynısını tekrar ver" isteğidir — `prev_sql`/`cube_query` varlığı yüzünden is_followup
    # True olsa bile VQR ÖNCE denenmeli. VQR'da kayıt YOKSA (miss) hiçbir early-return
    # OLMADAN mevcut takip mantığına sessizce düşülür — gerçek bir takip sorusu ("aylara
    # göre kır") ETKİLENMEZ (metin farklı olduğundan is_literal_repeat zaten False kalır).
    is_literal_repeat = bool(body.history) and q_norm == cube_router._norm(body.history[-1])
    if not is_followup or is_literal_repeat:
        cached = vqr.near_exact(body.question) if vqr else None
        cached_payload = cached.get("cube_query") if cached else None
        cached_sql = (cached_payload or {}).get("wren_sql") if cached_payload else None
        # ŞEMA-SÜRÜM KAPISI (Faz 0.6, 2 Ağustos 2026). Öğrenilmiş HAM SQL, öğrenildiği
        # andaki cube tanımlarına göre doğruydu; MDL o zamandan beri değiştiyse artık
        # doğru olmayabilir. En somut hâli: bir cube'a sonradan `always_filter`
        # (ör. `CANCELLED = 0`) eklenirse, yapısal yol onu HER sorguya enjekte eder ama
        # bu kayıt ham SQL olduğu için filtreden GEÇMEZ — aynı soru, iki farklı sayı, ve
        # yanlış olanı `source="vqr"` rozetiyle "doğrulanmış" diye sunulur.
        # `dry_plan` bunu YAKALAMAZ: SQL sözdizimsel olarak hâlâ geçerlidir.
        #
        # Damgası olmayan eski kayıtlar da BAYAT sayılır: geçerliliğini KANITLAYAMADIĞIMIZ
        # bir kaydı "doğrulanmış" diye sunmak, tam da bu kapının önlemek için var olduğu
        # şey. Kısayol atlanır, soru normal merdivenden doğru cevabı üretir ve bir sonraki
        # başarılı cevapta kayıt damgalı olarak yeniden öğrenilir (kendi kendini onarır).
        cached_mdl = (cached_payload or {}).get("mdl_version") if cached_payload else None
        if cached_sql and cached_mdl != service.mdl_version:
            _log.info("VQR ham-SQL kaydı bayat (mdl_version %s ≠ %s) — kısayol atlanıyor",
                      cached_mdl, service.mdl_version)
            cached_sql = None
        if cached_sql:
            try:
                planned = service.dry_plan(cached_sql)
                result = service.query(cached_sql, limit=limit) if body.execute else None
                resp = AskResponse(
                    question=body.question, sql=cached_sql, planned_sql=planned,
                    result=QueryResult(**result) if result else None, source="vqr",
                    trace=["VQR (verified repository) birebir eşleşme → doğrulanmış SQL "
                          "tekrar oynatıldı (LLM'siz)"],
                )
                resp.contract_id = _record_contract(None, cached_sql, result, "vqr")
                return _finish(_attach_viz(resp, result))
            except Exception:
                _log.warning("VQR'daki SQL artık geçersiz (şema değişmiş olabilir) — "
                            "sonraki adıma düşülüyor", exc_info=True)
        elif cached_payload and cached_payload.get("cube"):
            # `/verify` (CubeQuery-şekilli, eski) ile öğrenilmiş çift — wren_sql sarmalayıcı
            # DEĞİL, ham CubeQuery. Deterministik derleyiciden geçirilir (ham SQL replay
            # değil): whitelist-doğrulama + her zaman güncel `always_filter`/dialect. Dönem
            # depoda YOK (VQR.store dönem filtresini bilerek düşürür, ADR: şekil öğrenilir,
            # tarih değil) → period-kapısı AYNI politika ile yeniden sorar (gerekirse).
            try:
                _, vqr_index = cube_router.build_catalog(schema)
                vqr_cq = cube_router.parse_cube_query(
                    json.dumps(cached_payload, ensure_ascii=False), vqr_index)
            except Exception:
                vqr_cq = None
                _log.warning("VQR CubeQuery çifti ayrıştırılamadı (şema değişmiş olabilir) — "
                            "sonraki adıma düşülüyor", exc_info=True)
            if vqr_cq:
                vqr_cube_meta = next((c for c in (schema.get("cubes") or [])
                                      if c.get("name") == vqr_cq.get("cube")), None)
                gate = _period_gate(vqr_cq, vqr_cube_meta, None,
                                    "VQR (verified repository) eşleşme bulundu")
                if gate:
                    return gate
                resp = _answer_from_cube_query(
                    vqr_cq, source="vqr",
                    trace=["VQR (verified repository) birebir eşleşme → deterministik "
                          "derleyici (LLM'siz)"])
                if resp:
                    return resp

    def _try_kpi() -> AskResponse | None:
        """Doğrulama turu düzeltmesi (1 Ağustos 2026) — `app/kpi.py`'nin cross-cube KPI
        motoru (CCC/cari oran gibi TEK cube ölçüsü OLAMAYAN bileşke metrikler) daha önce
        canlı akışa HİÇ bağlı değildi: `resolve_kpi`/`resolve_kpi_series` hiçbir router'dan
        çağrılmıyordu, `AskResponse.kpi` hiçbir zaman set edilmiyordu — altyapı (formül
        motoru + 3 ERP paketinin turev.yml'i + 8 birim testi) HAZIRDI, yalnız son kilometre
        (soru→KPI eşleşmesi) eksikti. `cube_router.match_kpi` yalnız BU şirkette GERÇEKTEN
        derlenmiş KPI'lar (`schema()["kpis"]`) için eşleşir — boşsa (demo-boyahane dahil
        ÇOĞU tenant) HER ZAMAN None döner, mevcut davranış DEĞİŞMEZ. Kapsam (bilinçli, bu
        turda MİNİMAL): yalnız SKALER kart (`resolve_kpi`) — dönem-serisi (`resolve_kpi_
        series`, "aylara göre X" gibi) ayrı bir turda ele alınabilir (gran-tespiti route()'un
        kendi karmaşık mekanizmasına dokunmadan izole edilmeli)."""
        kpi_name = cube_router.match_kpi(q_norm, schema)
        if not kpi_name:
            return None
        try:
            from app.kpi import load_kpis, resolve_kpi

            spec = load_kpis(service.project_dir).get(kpi_name)
            if not spec:
                return None
            kpi_meta = next((k for k in (schema.get("kpis") or [])
                            if k.get("name") == kpi_name), {})
            op_sql = {"gte": ">=", "lte": "<=", "gt": ">", "lt": "<", "eq": "="}
            conds = [f"tarih {op_sql.get(f['operator'], '=')} '{f['value']}'"
                    for f in cube_router.date_filters(q_norm, "tarih")
                    if f.get("dimension") == "tarih" and f.get("value")]
            where = ("WHERE " + " AND ".join(conds)) if conds else ""
            card = resolve_kpi(service, spec, where)
            # KAPANIŞTAN GEÇ (Faz A4). Buradaki `return` eskiden `_finish`'i ATLIYORDU:
            # KPI cevabı contract_id'siz, audit'siz ve PII maskesiz dönüyordu. MIMARI §2
            # bunu "bilinen sapma" olarak kaydetmişti ama kaçağın kapsamı belgede
            # yazandan genişti (yalnız "yorum" değil, üç garanti birden).
            return _finish(AskResponse(
                question=body.question, source="cube", kpi=card,
                trace=[f"KPI eşleşmesi (LLM'siz, sıfır maliyet): {kpi_meta.get('label', kpi_name)}"],
            ))
        except Exception:
            _log.warning("KPI resolver hata verdi (best-effort) — Discovery'ye düşülüyor",
                        exc_info=True)
            return None

    def _try_fresh_intent() -> AskResponse | None:
        """route() → YoY/MoM → LLM-Intent-JSON → neden-özel netleştirme chip'i. Hiçbiri
        cevaplayamazsa None (çağıran Discovery'ye düşer). Yapısal takip zinciri
        action="new" (konu tamamen değişti) dediğinde de BU fonksiyon çağrılır."""
        kpi_resp = _try_kpi()
        if kpi_resp:
            return kpi_resp
        route_hit: dict | None = None
        intent_source: str | None = None
        typo_fix_trace: str | None = None
        typo_suggestion: dict | None = None
        try:
            route_hit = cube_router.route(body.question, schema)
            if route_hit:
                intent_source = "cube"
        except Exception:
            _log.warning("cube_router.route() hata verdi (best-effort)", exc_info=True)

        # TYPO/BULANIK-EŞLEŞTİRME (Faz 2c/Faz 3) — ilk deneme (ham metin) başarısızsa,
        # `partial_unknowns` kapsamındaki tanınmayan kelimeler katalog haznesine karşı
        # bulanık eşlenir. Yüksek-benzerlik + net aday → metin OTOMATİK düzeltilip route()
        # TEKRAR denenir (trace'te AÇIKÇA belirtilir — sessiz değil); orta-benzerlik → metin
        # değişmez, `typo_suggestion` aşağıdaki "neden-özel" chip zincirinde kullanılır.
        if route_hit is None:
            try:
                corrected_q, typo_fixes = cube_router.typo_correct(q_norm, schema)
            except Exception:
                corrected_q, typo_fixes = q_norm, []
                _log.warning("typo_correct hata verdi (best-effort)", exc_info=True)
            autos = [f for f in typo_fixes if f["kind"] == "auto"]
            if autos:
                try:
                    retry_hit = cube_router.route(corrected_q, schema)
                except Exception:
                    retry_hit = None
                    _log.warning("cube_router.route() (typo-düzeltmeli) hata verdi "
                                "(best-effort)", exc_info=True)
                if retry_hit:
                    route_hit = retry_hit
                    intent_source = "cube"
                    fixes_text = ", ".join(f'"{f["from"]}"→"{f["to"]}"' for f in autos)
                    typo_fix_trace = f"yazım düzeltme ({fixes_text})"
            if route_hit is None:
                typo_suggestion = next((f for f in typo_fixes if f["kind"] == "suggest"), None)

        # Dönemsel kıyas (YoY/MoM) — route() _COMPARE_HINTS nedeniyle BİLEREK None döner;
        # ayrı, YİNE deterministik bir mekanizma var (/cube'un compare chip'iyle AYNI —
        # app/yoy.py). Kıyas ifadesi sökülüp temiz metinle route() tekrar denenir.
        if route_hit is None:
            mode = cube_router.compare_mode(q_norm)
            if mode:
                cleaned = cube_router.strip_compare(q_norm)
                try:
                    base_hit = cube_router.route(cleaned, schema)
                except Exception:
                    base_hit = None
                if base_hit:
                    try:
                        from app import yoy as _yoy

                        base_cq = base_hit["cube_query"]
                        time_dim = _yoy.time_dim_of(schema, base_cq.get("cube"))
                        out = _yoy.compute(service, {**base_cq, "compare": mode}, mode,
                                           time_dim, limit=limit)
                        final_cq = {**out["base_cq"], "compare": mode}
                        result = {"columns": out["columns"], "rows": out["rows"],
                                 "row_count": out["row_count"]}
                        resp = AskResponse(
                            question=body.question, sql=out["base_sql"],
                            planned_sql=service.dry_plan(out["base_sql"]),
                            result=QueryResult(**result), source="cube", cube_query=final_cq,
                            trace=[f"Intent-path: dönemsel kıyas ({mode}, LLM'siz)"],
                        )
                        resp.contract_id = _record_contract(
                            final_cq, out["base_sql"], result, "cube")
                        return _finish(_attach_viz(resp, result, final_cq))
                    except Exception:
                        _log.warning("YoY/MoM hesaplama başarısız (best-effort) — "
                                    "sıradaki adıma düşülüyor", exc_info=True)

        # CUBE-DÜZEYİ BERABERLİK (Faz 3.1) — Intent-JSON'dan ÖNCE, bilerek.
        # İki cube aynı kelimeleri BİREBİR aynı güçle sahiplendiğinde (ölçülen vaka:
        # "arıza duruşu" → hem bakim.toplam_durus_dakika hem oee.plansiz_durus_dakika,
        # ikisi de meşru) metinde ayrım YOKTUR. LLM'e sorulursa TAHMİN eder ve tahminini
        # `cube+llm` rozetiyle sunar — makul görünen yanlış cevap, merdivenin en pahalı
        # hata sınıfı. Değişmez (MIMARI.md §4-6): belirsizlikte SOR, tahmin etme.
        # Chip'lerin metni `cube_router` tarafında route() ile GERÇEKTEN doğrulanır, yani
        # tıklama kesin bir cevaba çıkar; doğrulanamayan tek bir aday bile varsa liste HİÇ
        # yayımlanmaz ve akış olağan şekilde Intent-JSON'a düşer.
        if route_hit is None:
            try:
                ties = cube_router.cube_tie_candidates(body.question, schema)
            except Exception:
                _log.warning("cube_tie_candidates hata verdi (best-effort)", exc_info=True)
                ties = []
            if ties:
                chips = []
                for c, netlestirici, hit in ties:
                    m = (hit.get("cube_query") or {}).get("measures") or [None]
                    mdisp = (c.get("measure_synonyms_display") or {}).get(m[0]) or m[0] or ""
                    clabel = c.get("display") or c.get("name") or ""
                    chips.append(Suggestion(label=f"{clabel}: {mdisp}" if mdisp else clabel,
                                            query=netlestirici))
                return _finish(AskResponse(
                    question=body.question, source=None,
                    note="Bu ifade birden fazla konuda aynı anlama geliyor, hangisini "
                         "istiyorsun?",
                    suggestions=chips,
                    trace=["Intent-path: cube-düzeyi beraberlik → netleştirme (LLM'siz)"],
                ))

        if route_hit is None and "ask_intent_first" in resolve_for(settings, principal):
            llm_probe = getattr(request.app.state, "llm", None)
            if llm_probe is not None and hasattr(llm_probe, "select_cube"):
                try:
                    catalog_text, cube_index = cube_router.build_catalog(schema)
                    raw = llm_probe.select_cube(body.question, catalog_text)
                    parsed = cube_router.parse_cube_query(raw, cube_index)
                    if parsed:
                        route_hit = {"cube_query": parsed, "order": None, "limit": None}
                        intent_source = "cube+llm"
                except Exception:
                    _log.warning("LLM Intent-JSON seçimi başarısız (best-effort)", exc_info=True)

        if route_hit:
            cq = route_hit["cube_query"]
            # Gitaş logu 2026-07-24: order/limit route()'tan AYRI alanlar olarak
            # dönüyordu ("en çok ciro yapılan 5 müşteri" → order=(measure,DESC),
            # limit=5) — dönem-belirsizliği kapıya takılınca (clarification cube_query'yi
            # DÖNDÜRÜR ama _answer_from_cube_query'ye hiç uğramaz) bu ikisi kaybolup
            # takip mesajı (dönem chip'i) sıralamasız/limitsiz bir rapora dönüşüyordu.
            # cq'nin İÇİNE gömülü taşınır (cube_sql zaten gömülü order/limit okuyabilir)
            # → clarification cube_query'si dahil HER round-trip'te hayatta kalır.
            if route_hit.get("order"):
                om, odir = route_hit["order"]
                cq = {**cq, "order": {"measure": om, "direction": str(odir).lower()}}
            if route_hit.get("limit"):
                cq = {**cq, "limit": route_hit["limit"]}
            cube_meta = next((c for c in (schema.get("cubes") or [])
                              if c.get("name") == cq.get("cube")), None)
            gate = _period_gate(cq, cube_meta, route_hit.get("period_optional"), "Intent-path")
            if gate:
                return gate
            fresh_trace = (["Intent-path: cube_router.route() (LLM'siz, sıfır maliyet)"]
                          if intent_source == "cube" else
                          ["Intent-path: LLM Intent-JSON seçimi (SQL değil, ölçü/boyut/"
                           "filtre seçimi) → deterministik derleyici"])
            if typo_fix_trace:
                fresh_trace.append(f"Intent-path: {typo_fix_trace}")
            resp = _answer_from_cube_query(
                cq, source=intent_source, learn=(intent_source == "cube+llm"),
                trace=fresh_trace,
            )
            if resp:
                return resp

        # YAZIM BENZERLİĞİ (orta güven, Faz 2c/Faz 3) — yüksek-güvenli otomatik düzeltme
        # (yukarıda) mümkün olmadıysa ama en azından ORTA benzerlikte tek bir aday varsa,
        # TAHMİN ETMEDEN "şunu mu demek istedin?" chip'i sorulur — tıklayınca düzeltilmiş
        # tam soru metniyle gerçek bir cevap gelir (chip'in `query`'si zaten düzeltilmiş).
        if typo_suggestion:
            return _finish(AskResponse(
                question=body.question, source=None,
                note=f"\"{typo_suggestion['from']}\" yerine \"{typo_suggestion['to']}\" mi "
                    "demek istedin?",
                suggestions=[Suggestion(label=typo_suggestion["to"],
                                       query=typo_suggestion["corrected_q"])],
                trace=["Intent-path: yazım benzerliği → \"şunu mu demek istedin?\" (LLM'siz)"],
            ))

        # route()+YoY+LLM-select tükendi — Discovery'ye köre düşmeden NEDEN-özel
        # netleştirme: TEK cube (ölçü belirsiz) / çapraz-konu (iki rakip cube kimliği) /
        # kısmi-anlama (tanınan + tanınmayan kelime karışımı). cube_router.py'de zaten
        # vardı, hiç bağlanmamıştı.
        try:
            only_cube = cube_router.cube_only_match(q_norm, schema)
        except Exception:
            only_cube = None
        if only_cube:
            labels = []
            for m in only_cube.get("measures") or []:
                mdisp = (only_cube.get("measure_synonyms_display") or {}).get(m) or m
                if mdisp not in labels:
                    labels.append(mdisp)
            cube_label = only_cube.get("display") or only_cube.get("name") or ""
            return _finish(AskResponse(
                question=body.question, source=None,
                note=f"{cube_label} için hangi ölçüyü istiyorsun?",
                suggestions=[Suggestion(label=lb, query=lb) for lb in labels[:8]],
                trace=["Intent-path: cube belirlendi, ölçü belirsiz → netleştirme (LLM'siz)"],
            ))

        try:
            cands = cube_router.measure_cube_candidates(q_norm, schema)
        except Exception:
            cands = []
        distinct_cubes = {c["name"]: (c, m) for c, m in cands}
        if len(distinct_cubes) >= 2:
            m_disp_labels = []
            for c, m in distinct_cubes.values():
                mdisp = (c.get("measure_synonyms_display") or {}).get(m) or m
                if mdisp not in m_disp_labels:
                    m_disp_labels.append(mdisp)
            if len(m_disp_labels) >= 2:
                return _finish(AskResponse(
                    question=body.question, source=None,
                    note="Birden fazla konu anlaşıldı, hangisini istiyorsun?",
                    suggestions=[Suggestion(label=lb, query=lb) for lb in m_disp_labels[:6]],
                    trace=["Intent-path: çapraz konu → netleştirme (LLM'siz)"],
                ))

        try:
            unknown, hits = cube_router.partial_unknowns(q_norm, schema)
        except Exception:
            unknown, hits = [], []
        if unknown and hits:
            labels = []
            for c, m in hits:
                mdisp = (c.get("measure_synonyms_display") or {}).get(m) or m
                if mdisp not in labels:
                    labels.append(mdisp)
            # "Tanınmayan" kelime aslında BAŞKA bir cube'un kendi kimliği olabilir (ör.
            # "sürdürülebilirlik" — partial_unknowns onu `resolved` cube'a (parti) ait
            # SAYMAZ ama katalogda meşru bir konu). O konu da chip'lenir — kullanıcı iki
            # rakip yorumdan birini seçsin (ADR-0008: sessizce biri seçilip ötekisi
            # yutulmaz).
            hit_cube_names = {c["name"] for c, _ in hits}
            other_topic = False
            for c in schema.get("cubes") or []:
                if c.get("name") in hit_cube_names:
                    continue
                # Cube-düzeyi VEYA boyut-düzeyi sinonim — "tedarikçi" gibi bir kelime
                # ölçü değil, BAŞKA bir cube'un BOYUTU olabilir (cari/ticaret'in
                # "tedarikçi" boyutu). İkisi de "başka bir konu" sinyali sayılır.
                dim_hit = any(cube_router._syn_hit_words(q_norm, syns)
                             for syns in (c.get("dimension_synonyms") or {}).values())
                if cube_router._syn_hit_words(q_norm, c.get("synonyms")) or dim_hit:
                    clabel = c.get("display") or c.get("name") or ""
                    if clabel and clabel not in labels:
                        labels.append(clabel)
                        other_topic = True
            trace_msg = ("Intent-path: çapraz konu (rakip cube kimliği) → netleştirme "
                        "(LLM'siz)" if other_topic else
                        "Intent-path: kısmi anlama → rapor düşülmedi, netleştirme (LLM'siz)")
            note = (f"\"{' '.join(unknown)}\" başka bir konu gibi görünüyor. "
                   "Hangisini istiyorsun?" if other_topic else
                   f"\"{' '.join(unknown)}\" kısmını anlayamadım, bu yüzden rapor "
                   "düşülmedi. Ne demek istediğini biraz daha açar mısın?")
            return _finish(AskResponse(
                question=body.question, source=None, note=note,
                suggestions=[Suggestion(label=lb, query=lb) for lb in labels[:6]],
                trace=[trace_msg],
            ))

        # HİÇ KONU YOK ("bu yıl tüm aylarını karşılaştır" — NEYİ?): dönem/kıyas dili var
        # ama partial_unknowns HİÇBİR (cube, ölçü) çifti bulamadı (hits boş) — LLM'e
        # bırakılırsa alakasız bir raporu (ör. personel) uydurabilir (log regresyonu).
        # Katalogdan örnek ölçülerle "hangisini istiyorsun?" sorulur.
        if not hits and (cube_router._period_hit_words(q_norm) or cube_router.compare_mode(q_norm)):
            example_labels = []
            for c in schema.get("cubes") or []:
                for m in (c.get("measures") or [])[:1]:
                    mdisp = (c.get("measure_synonyms_display") or {}).get(m) or m
                    if mdisp not in example_labels:
                        example_labels.append(mdisp)
            return _finish(AskResponse(
                question=body.question, source=None,
                note="Neyi karşılaştırmak/görmek istediğini anlayamadım. Hangi ölçüyü istersin?",
                # 8 → 14: katalog büyüdükçe (Faz 2b'de `makine_duruslari` eklendi, artık 13
                # cube var) sabit bir küçük kesim en spesifik/tanıdık örnekleri (ör. OEE)
                # sessizce dışarıda bırakabiliyordu — kesim kataloğun BUGÜNKÜ boyutunu
                # rahatça kapsayacak şekilde büyütüldü.
                suggestions=[Suggestion(label=lb, query=lb) for lb in example_labels[:14]],
                trace=["Intent-path: konu belirtilmedi → netleştirme (LLM'siz)"],
            ))
        return None

    def _learn_chip_completion(cq: dict, cube_meta: dict | None) -> str | None:
        """Takip zinciri bir raporu TAMAMLADIĞINDA (deterministic_refine), önceki mesaj
        (`history[-1]`) GERÇEK bir konu taşıyorsa (cube/ölçü sinonimi) — o soru +
        TAMAMLANMIŞ şekil VQR'a öğrenilir (log regresyonu: "aylara göre" gibi konusuz
        şekil-parçaları geçmişte chip-onayıyla yanlışlıkla öğreniliyordu — bağlamsız
        yanlış replay riski, ADR-0008). Konu taşımayan mesaj → None (öğrenilmez)."""
        if vqr is None or not body.history or not cube_meta:
            return None
        prev_q = body.history[-1]
        prev_q_norm = cube_router._norm(prev_q)
        topical = bool(cube_router._syn_hit_words(prev_q_norm, cube_meta.get("synonyms"))) or \
            cube_router._match_measure(prev_q_norm, cube_meta)[0] is not None
        if not topical:
            return None
        try:
            if vqr.store(prev_q, cq, source="chip_approved"):
                return "chip-onaylı → VQR güncellendi (LLM'siz öğrenme)"
        except Exception:
            _log.warning("chip-onaylı VQR öğrenme başarısız (best-effort)", exc_info=True)
        return None

    # 3) YAPISAL TAKİP — önceki tur GERÇEK bir CubeQuery ürettiyse (route()/LLM-select/
    # YoY/bu zincirin kendisi), deterministik düzenleme zinciri denenir (bkz. docstring §3).
    # cube_router.py'de zaten tam, test edilmiş, LLM'siz bir zincirdi — strict-agentic
    # göçünden beri /ask'e hiç bağlanmamıştı.
    if structural_followup:
        prev_cq = dict(body.cube_query or {})
        # Cube-adı göçü (yeniden adlandırma sonrası istemcide eski adla kalan rapor,
        # "fire" → "parti" gibi): /cube ve /report bunu zaten çözüyordu (satır ~658/761),
        # /ask'in yapısal takip zinciri hiç çözmüyordu — eski adla gelen HER takip mesajı
        # sahte "bağlam kopması" (dürüst ret) üretiyordu, oysa ad değişmiş tek bir cube.
        migration_trace: list[str] = []
        _resolved = cube_router.resolve_cube_name(prev_cq.get("cube"), schema)
        if _resolved and _resolved != prev_cq.get("cube"):
            migration_trace = [f"cube adı göçü → {_resolved}"]
            prev_cq["cube"] = _resolved
        prev_cube_meta = next((c for c in (schema.get("cubes") or [])
                               if c.get("name") == prev_cq.get("cube")), None)

        # BAYAT cube_query (Gitaş 500'ü, 2026-07-24): istemcide önceki oturumdan/şirketten
        # kalan bir cube_query artık MEVCUT şemada çalıştırılamıyor olabilir (ölçü/boyut
        # kaldırılmış, MDL değişmiş). Zincirin geri kalanı bunu SESSİZCE "anlaşılmadı"
        # sanıp genel bir "ilişkilendiremedim" notuna düşerdi — oysa asıl sorun ŞEKLİN
        # KENDİSİ artık geçersiz. ÖNCEDEN yakalanır: 500 yerine dürüst, isabetli not.
        if prev_cube_meta is None or any(
            m not in (prev_cube_meta.get("measures") or []) for m in (prev_cq.get("measures") or [])
        ) or any(
            d not in (prev_cube_meta.get("dimensions") or []) for d in (prev_cq.get("dimensions") or [])
        ):
            return _honest_refusal(
                note="Önceki rapor artık çalıştırılamadı (şema değişmiş olabilir). "
                    "Yeni bir soru olarak sorar mısın?",
                trace=migration_trace + ["Takip: bayat cube_query (şema uyuşmazlığı) → dürüst ret"],
            )

        # YETENEK SORUSU ("hangi kırılımlara göre detaylandırabilirim?") — bir DÜZENLEME
        # DEĞİL, mevcut cube'un boyut LİSTESİNİ ister (log regresyonu: LLM bunu edit
        # sanıp TÜM boyutları ekleyip aşırı büyük rapor üretiyordu). deterministic_refine
        # DENENMEDEN önce yakalanır — aksi halde "hangi"/"kırılım" gibi kelimeler onun
        # dolgu/kapsam mantığına karışabilir.
        if prev_cube_meta and cube_router.is_capability_query(q_norm):
            existing_dims = set(prev_cq.get("dimensions") or [])
            labels = []
            for dname in prev_cube_meta.get("dimensions") or []:
                if dname in existing_dims:
                    continue
                dlabel = (prev_cube_meta.get("dimension_labels") or {}).get(dname) or dname
                if dlabel not in labels:
                    labels.append(dlabel)
            return _finish(AskResponse(
                question=body.question, source=None,
                note="Bu raporu hangi kırılıma göre detaylandırmak istersin?",
                suggestions=[Suggestion(label=lb, query=lb) for lb in labels[:10]],
                trace=migration_trace + ["Takip: yetenek sorusu → kırılım chip'leri (LLM'siz)"],
            ))

        try:
            refined = cube_router.deterministic_refine(prev_cq, q_norm, schema)
        except Exception:
            _log.warning("deterministic_refine hata verdi (best-effort)", exc_info=True)
            refined = None
        if refined:
            gate = _period_gate(refined, prev_cube_meta, None, "Takip")
            if gate:
                return gate
            _el = refined.get("entity_limit")
            if _el and _el.get("n"):
                trace_msg = f"refine → varlık top-{_el['n']} (LLM'siz)"
            elif cube_router.is_all_time(q_norm):
                trace_msg = "refine → tüm zamanlar (dönem filtresi kaldırıldı, LLM'siz)"
            else:
                trace_msg = "refine → deterministik düzenleme"
            trace_list = migration_trace + [trace_msg]
            learn_note = _learn_chip_completion(refined, prev_cube_meta)
            if learn_note:
                trace_list.append(learn_note)
            resp = _answer_from_cube_query(refined, source="cube", trace=trace_list)
            if resp:
                return resp

        try:
            added = cube_router.cross_cube_add(prev_cq, q_norm, schema)
        except Exception:
            _log.warning("cross_cube_add hata verdi (best-effort)", exc_info=True)
            added = None
        if added:
            resp = _answer_from_cube_query(
                added, source="cube",
                trace=migration_trace + ["Takip: çapraz-cube ekleme (blend, LLM'siz)"])
            if resp:
                return resp

        try:
            switched = cube_router.cross_cube_dim_switch(prev_cq, q_norm, schema)
        except Exception:
            _log.warning("cross_cube_dim_switch hata verdi (best-effort)", exc_info=True)
            switched = None
        if switched:
            new_meta = next((c for c in (schema.get("cubes") or [])
                             if c.get("name") == switched.get("cube")), None)
            gate = _period_gate(switched, new_meta, None, "Takip")
            if gate:
                return gate
            prev_label = (prev_cube_meta or {}).get("display") or prev_cq.get("cube") or ""
            new_label = (new_meta or {}).get("display") or switched.get("cube") or ""
            resp = _answer_from_cube_query(
                switched, source="cube",
                note=f"Konu değişti: {prev_label} → {new_label}",
                trace=migration_trace + ["Takip: çapraz-cube konu geçişi (LLM'siz)"])
            if resp:
                return resp

        # KONU DEĞİŞİMİ (ÖLÇÜ DE farklı) — cross_cube_dim_switch yalnız AYNI ölçü(ler)i
        # YENİ boyutla taşıyan cube'a geçirir; mesaj hem YENİ boyut hem YENİ ölçü
        # taşıyorsa (ör. OEE raporundayken "kumaş cinsine göre fire oranı") o fonksiyon
        # bilerek None döner. Mesaj tek başına TAM bağımsız bir rapor tanımlıyorsa
        # route() onu zaten sıfır-LLM çözer — deterministik zincirin son, en genel adımı.
        try:
            fresh_route = cube_router.route(q_norm, schema)
        except Exception:
            _log.warning("route() (konu değişimi denemesi) hata verdi (best-effort)",
                        exc_info=True)
            fresh_route = None
        if fresh_route:
            new_cq = fresh_route["cube_query"]
            new_meta = next((c for c in (schema.get("cubes") or [])
                             if c.get("name") == new_cq.get("cube")), None)
            topic_switched = new_cq.get("cube") != prev_cq.get("cube")
            # DÖNEM TAŞIMA (panel K2, canlı gitas log 2026-07-24): konu değişimi mesajın
            # kendisi yeni bir dönem belirtmiyorsa önceki raporun dönem filtresi SESSİZCE
            # tüm-zamana düşmemeli — hedef cube'da AYNI zaman boyutu varsa taşınır (ikisi
            # de "tarih" — cross_cube_dim_switch'in deepcopy(prev) ile yaptığının aynısı,
            # burada yalnız route() TAMAMEN yeni bir cq ürettiği için elle yapılır).
            if (topic_switched and not new_cq.get("filters") and new_meta
                    and (new_meta.get("time_dimensions") or [None])[0]
                    == ((prev_cube_meta or {}).get("time_dimensions") or [None])[0]):
                prev_period_f = [f for f in (prev_cq.get("filters") or [])
                                 if f.get("dimension") == new_meta["time_dimensions"][0]]
                if prev_period_f:
                    new_cq = {**new_cq, "filters": prev_period_f}
            gate = _period_gate(new_cq, new_meta, fresh_route.get("period_optional"), "Takip")
            if gate:
                return gate
            note = None
            if topic_switched:
                prev_label = (prev_cube_meta or {}).get("display") or prev_cq.get("cube") or ""
                new_label = (new_meta or {}).get("display") or new_cq.get("cube") or ""
                note = f"Konu değişti: {prev_label} → {new_label}"
            resp = _answer_from_cube_query(
                new_cq, order=fresh_route.get("order"), limit_val=fresh_route.get("limit"),
                source="cube", note=note,
                trace=migration_trace + (
                    ["Takip: çapraz-cube konu geçişi (route() ile yeniden eşleştirme, LLM'siz)"]
                    if topic_switched else
                    ["Takip: route() ile yeniden eşleştirme (LLM'siz)"]))
            if resp:
                return resp

        # Deterministik zincir tükendi — LLM-destekli YAPISAL düzenleme (hâlâ SQL DEĞİL,
        # bir karar JSON'u: edit|new|unavailable). Kural-tabanlı sağlayıcıda refine_cube
        # yok (hasattr) → doğrudan dürüst rete düşer.
        llm_probe = getattr(request.app.state, "llm", None)
        reason = None
        if llm_probe is not None and hasattr(llm_probe, "refine_cube"):
            try:
                catalog_text, cube_index = cube_router.build_catalog(schema)
                raw = llm_probe.refine_cube(
                    json.dumps(prev_cq, ensure_ascii=False), body.question, catalog_text)
                decision = _parse_decision(raw)
                action = decision.get("action")
                if action == "edit" and isinstance(decision.get("cube_query"), dict):
                    cq2 = cube_router.parse_cube_query(
                        json.dumps(decision["cube_query"], ensure_ascii=False), cube_index)
                    if cq2:
                        cq2 = _drop_invented(cq2, q_norm, prev_cq)
                        cq2, unresolved = _resolve_period(
                            prev_cq, cq2, decision.get("period_expr"), q_norm)
                        if not unresolved:
                            new_meta = next((c for c in (schema.get("cubes") or [])
                                             if c.get("name") == cq2.get("cube")), None)
                            gate = _period_gate(cq2, new_meta, None, "Takip")
                            if gate:
                                return gate
                            resp = _answer_from_cube_query(
                                cq2, source="cube+llm",
                                trace=["Takip: LLM-destekli yapısal düzenleme"])
                            if resp:
                                return resp
                elif action == "new":
                    fresh = _try_fresh_intent()
                    if fresh:
                        return fresh
                reason = decision.get("reason")
            except Exception:
                _log.warning("LLM yapısal takip düzenlemesi başarısız (best-effort)", exc_info=True)

        # YAPISAL ZİNCİR ÇIKMAZI (canlı bulgu, 1 Ağustos 2026 — "personel bazlı verimlilikleri
        # karşılaştır son 6 ay" bir OEE thread'i içinde): deterministik refine/cross_cube_*/
        # fresh-route() VE LLM'in edit/new kararı TÜKENİNCE eskiden BURADA doğrudan dürüst ret
        # dönerdi — ama AYNI soru taze/yeni-thread'den (is_followup=False) sorulunca Discovery
        # (ham-SQL, cube sınırlarının ÖTESİNDE serbest join) GERÇEKTEN cevaplayabiliyordu (canlı
        # kanıt: interaction_log'da aynı metin iki kez — biri dürüst ret, biri source=llm:gemini
        # başarılı sonuç). `_try_fresh_intent()` bir kez daha denenir (action="new" DIŞINDAki —
        # refine_cube hiç çağrılamadı/hata verdi/"edit"-ama-geçersiz gibi — durumları da kapsar).
        fresh = _try_fresh_intent()
        if fresh:
            return fresh

        # ANLAŞILDI-AMA-TEK-CUBE-YETMİYOR mu, yoksa GERÇEKTEN ANLAŞILAMADI mı ("asdlkj qwerty
        # zxcvb" gibi) — bu ayrım KRİTİK: `test_convo_anlasilmayan_takip_serbest_sqle_dusmez`
        # BİLEREK anlamsız metnin Discovery'nin (rule-tabanlı sağlayıcıda özellikle) alakasız
        # bir varsayılan rapora ("_partiler_sql" son çare şablonu) düşmesini YASAKLAR — "ASLA
        # alakasız rapor değil". `_match_cube` (katalogda GERÇEK bir sinonim/kelime kanıtı var
        # mı) bu ayrımı ucuza yapar: eşleşme YOKSA mesaj katalogda hiçbir iz bırakmamıştır →
        # dürüst ret KORUNUR (ilk taslak bu koruma OLMADAN gibi metni de Discovery'ye
        # düşürüyordu — tam pytest bunu `test_convo_anlasilmayan_takip_serbest_sqle_dusmez`
        # ile YAKALADI). Eşleşme VARSA (ör. "verim" → oee) mesaj GERÇEK domain kelimesi taşıyor,
        # yalnız TEK bir cube'a sığmıyor — bu durumda Discovery'ye (ham-SQL, taze — stale
        # prev_sql'e çapalanmadan, `raw_followup` BURADA hâlâ False) düşülür.
        if cube_router._match_cube(q_norm, schema) is not None:
            _log.info("Takip: yapısal zincir tükendi ama mesajda katalog kanıtı var → "
                      "Discovery'ye düşülüyor (dürüst ret DEĞİL, önceki reason=%r)", reason)
        else:
            return _honest_refusal(
                note=reason or "Bu takip mesajını önceki raporla ilişkilendiremedim. "
                              "Yeni bir soru olarak sorar mısın?",
                trace=migration_trace + ["Takip: deterministik/LLM düzenleme tükendi → dürüst ret"],
            )

    # 4) FRESH (bağımsız) soru VEYA RAW takip (canlı bulgu, 1 Ağustos 2026 — "raw_followup
    # tuzağı"): bir thread'in İLK turu Discovery'ye (ham-SQL) düşerse `raw_followup` o thread'in
    # SONRAKİ HER turunda True kalırdı ve bu satır hiç ÇALIŞMAZDI — o thread bir daha asla
    # route()/Intent-JSON'a dönemiyordu, konu tamamen değişse (yeni, kolayca çözülebilir bir
    # soru olsa) BİLE. Yapısal takibin KENDİ "action==new" kaçış kapısıyla AYNI ilke: Discovery'nin
    # ham-SQL "takip düzenlemesi"ne (önceki SQL'i bağlam alarak) düşmeden ÖNCE, konu GERÇEKTEN
    # değiştiyse route()/Intent-JSON'un onu deterministik/ucuz çözüp çözemeyeceğine bakılır.
    # GÜVENLİ: `_try_fresh_intent()` yalnız KENDİNDEN EMİN olduğunda (route() eşleşmesi ya da
    # doğrulanmış Intent-JSON parse'ı) bir şey döner — gerçek bir ham-SQL devamı (ör. "temmuzu
    # çıkar", prev_sql'in bir parçasına atıfta bulunan, cube/ölçü kelimesi taşımayan bir kırpıntı)
    # route()'ta hiçbir eşleşme bulamaz, None döner, mevcut generate_followup_sql akışı DEĞİŞMEDEN
    # çalışmaya devam eder.
    if not is_followup or raw_followup:
        fresh = _try_fresh_intent()
        if fresh:
            return fresh

    # 5) Discovery: sağlayıcı zinciri (failover + kural-tabanlı/dürüst-ret yedeği —
    # app/llm.py, app.state.llm). RAW takip (önceki tur yapısal cube_query ÜRETMEMİŞSE),
    # bağımsız-ama-Intent-path'in kapsamadığı sorular VE (1 Ağustos 2026'dan beri) kendi
    # deterministik+LLM zinciri TÜKENMİŞ bir YAPISAL takip buraya ulaşır (§3'ün son çaresi —
    # `raw_followup` bu durumda hâlâ False, `_run_discovery` bu yüzden taze `generate_sql`
    # üretir, stale prev_sql'e çapalamaz).
    llm = getattr(request.app.state, "llm", None)
    if llm is None:
        raise HTTPException(status_code=503, detail="LLM sağlayıcısı yapılandırılmamış.")

    def _run_discovery(on_step=None) -> AskResponse:
        """Discovery'nin TAM yürütmesi — SQL üretimi→dry_plan→self-healing→çalıştırma→
        öğrenme→_finish (Faz 4.1, 31 Temmuz 2026): önceden bu blok doğrudan ask() gövdesinde
        SIRALI çalışıyordu; SENKRON (varsayılan) ve arka-plan işi (bayrak `ask_async_
        discovery` açıkken, bkz. _queue_discovery_job) yollarının İKİSİNDEN de AYNI şekilde
        çağrılabilsin diye bir kapanışa çıkarıldı — davranış BİREBİR korunur (hiçbir satır
        değişmedi), yalnız çağrılma şekli dallanır.

        `on_step` (Faz 4.12, 1 Ağustos 2026 — dış yol haritası 2.9 "canlı düşünme adımları"):
        verilirse HER trace adımından SONRA `on_step(mevcut_trace_listesi)` çağrılır —
        `_queue_discovery_job` bunu AskJob.trace_json'a ANINDA yazmak için kullanır, iş
        HENÜZ tamamlanmadan istemci hangi aşamada olunduğunu poll'layarak görebilir.
        Senkron yolda (bayrak kapalı) `on_step=None` — sıfır davranış değişikliği."""
        prompt_schema = schema
        if raw_followup:
            try:
                wren_sql = llm.generate_followup_sql(
                    _with_extra_context(body.question, body.extra_context),
                    schema, prev_question, prev_sql, body.history)
            except Exception as exc:
                # Dürüst ret — NoLlmGenerator'ın vaat ettiği ("routers/ask.py bunu dürüst
                # redde çevirir") ama strict-agentic göçünde 502'ye dönüşen davranış düzeltildi.
                _log.warning("Discovery takip üretimi başarısız", exc_info=True)
                return _honest_refusal(
                    note="Bu takip mesajını anlayamadım. Farklı bir şekilde sorar mısın?",
                    trace=[f"Discovery: takip üretimi başarısız ({exc}) → dürüst ret"],
                )
            trace = ["Discovery: önceki SQL bağlamında takip üretimi (LLM önceki SQL'i düzenledi/yok saydı)"]
            if on_step:
                on_step(list(trace))
        else:
            few_shot = vqr.few_shot_block(body.question) if vqr else ""
            if few_shot:
                prompt_schema = {**schema, "golden_sql": "\n\n".join(
                    s for s in (schema.get("golden_sql"), few_shot) if s)}
            try:
                wren_sql = llm.generate_sql(
                    _with_extra_context(body.question, body.extra_context), prompt_schema)
            except Exception as exc:
                _log.warning("Discovery SQL üretimi başarısız", exc_info=True)
                return _honest_refusal(
                    note="Bu soruyu anlayamadım. Farklı bir şekilde sorar mısın?",
                    trace=[f"Discovery: SQL üretimi başarısız ({exc}) → dürüst ret"],
                )
            trace = ["Discovery: VQR few-shot ile ham-SQL üretimi" if few_shot else
                    "Discovery: ham-SQL üretimi (Intent-path kapsamadı)"]
            if on_step:
                on_step(list(trace))

        try:
            planned = service.dry_plan(wren_sql)
        except Exception as e:
            trace.append(f"dry_plan hatası → kendi kendini onarma: {e}")
            if on_step:
                on_step(list(trace))
            try:
                wren_sql = llm.repair(body.question, prompt_schema, wren_sql, str(e))
                planned = service.dry_plan(wren_sql)
            except Exception as exc2:
                _log.warning("Discovery self-healing başarısız", exc_info=True)
                return _honest_refusal(
                    note="Bu soru için güvenilir bir sorgu üretemedim.",
                    trace=trace + [f"self-healing başarısız ({exc2}) → dürüst ret"],
                )

        # ÇALIŞTIRMA (canlı bulgu, 31 Temmuz 2026 — gerçek kullanıcı testinde 500 olarak
        # patladı): `dry_plan` yalnız PLANLAMA/SEMANTİK doğrulamadır — motorun GERÇEK
        # ÇALIŞTIRMASI (DuckDB/hedef lehçe) ayrı bir aşamadır ve dry_plan'ın geçtiği bir SQL
        # yine de ÇALIŞTIRMA anında patlayabilir (karmaşık, çok-parçalı sorular — "trend +
        # son N ay + X'in Y'ye etkisi" gibi bileşik istekler LLM'i geçersiz/aşırı karmaşık bir
        # sorguya götürebiliyor). Bu satır TEK BAŞINA sarmalanmamıştı — dosyadaki HER DİĞER
        # adımın (SQL üretimi, dry_plan, self-healing) aksine — üretim/planlama başarısız
        # olduğunda "dürüst ret" (502/500 DEĞİL) ilkesini burada da uygula: ÇALIŞTIRMA hatası
        # da dry_plan hatasıyla AYNI self-healing (`llm.repair`) turuna girer; o da başarısız
        # olursa dürüst ret (asla çıplak 500).
        if not body.execute:
            # `execute=False`: SQL üretildi ve dry_plan'dan geçti — çalıştırma YOK.
            # (Aynı sözleşme yapısal yolda da uygulanır, bkz. `_answer_from_cube_query`.)
            trace.append("Discovery: dry_plan geçti — execute=False, çalıştırılmadı")
            if on_step:
                on_step(list(trace))
            resp = AskResponse(question=body.question, sql=wren_sql, planned_sql=planned,
                               result=None, source=_llm_source(
                                   llm, used_rule=isinstance(llm, RuleBasedSqlGenerator)),
                               trace=trace)
            resp.contract_id = _record_contract(None, wren_sql, None, resp.source)
            return _finish(_attach_viz(resp, None))
        trace.append("Discovery: dry_plan geçti, çalıştırılıyor…")
        if on_step:
            on_step(list(trace))
        try:
            result = service.query(wren_sql, limit=limit)
        except Exception as e:
            trace.append(f"çalıştırma hatası → kendi kendini onarma: {e}")
            if on_step:
                on_step(list(trace))
            try:
                wren_sql = llm.repair(body.question, prompt_schema, wren_sql, str(e))
                planned = service.dry_plan(wren_sql)
                result = service.query(wren_sql, limit=limit)
            except Exception as exc2:
                _log.warning("Discovery çalıştırma + self-healing başarısız", exc_info=True)
                return _honest_refusal(
                    note="Bu soru için güvenilir bir sorgu üretemedim.",
                    trace=trace + [f"self-healing (çalıştırma) başarısız ({exc2}) → dürüst ret"],
                )

        # 6) Öğrenme döngüsü: yalnız BAĞIMSIZ başarılı yanıtlar VQR'a otomatik yazılır.
        # Bir takip cevabını ("aylara göre" → SQL) standalone soru metniyle önbelleklemek,
        # sonraki alakasız bir konuşmada YANLIŞ tekrar oynatmaya yol açardı — bu yüzden yalnız
        # bağlamdan bağımsız (kendi başına anlamlı) sorular öğrenilir.
        if vqr is not None and not is_followup:
            try:
                # `auto_discovery` (Faz 4.1): bu HAM LLM SQL'idir ve HİÇ İNCELENMEDİ.
                # Saklanır (terfi kuyruğunun ham maddesi + few-shot değeri) ama TEKRAR
                # OYNATILMAZ — `near_exact` güven kapısından geçmez. Eskiden "auto"
                # etiketiyle yazılıyor ve insan onaylı bir kayıtla AYNI otoriteyle
                # benzer sorulara tekrar oynatılıyordu.
                vqr.store(body.question,
                          {"wren_sql": wren_sql, "mdl_version": service.mdl_version},
                          source="auto_discovery")
            except Exception:
                _log.warning("VQR otomatik kayıt başarısız (best-effort)", exc_info=True)

        # 6b) Discovery→Promote yakalama (Faz 2d): başarılı BAĞIMSIZ bir Discovery cevabı,
        # best-effort bir "taslak ölçü" adayı olarak yakalanır (yalnız yakalama — inceleme/onay
        # AYRI, bkz. app/routers/measures.py). VQR'la (madde 6) AYNI "yalnız bağımsız soru"
        # politikası: bir takibin SQL'i tek başına anlamlı bir ölçü önerisi değildir.
        if result is not None and not is_followup:
            _capture_measure_candidate(body.question, wren_sql, result, principal)

        resp = AskResponse(
            question=body.question, sql=wren_sql, planned_sql=planned,
            result=QueryResult(**result) if result else None,
            source=_llm_source(llm, used_rule=isinstance(llm, RuleBasedSqlGenerator)),
            trace=trace,
        )
        resp.contract_id = _record_contract(None, wren_sql, result, resp.source)
        return _finish(_attach_viz(resp, result))

    # Faz 4.1 (31 Temmuz 2026) — bayrak KAPALIYKEN (varsayılan, tüm mevcut testler/tenant'lar)
    # davranış BİREBİR eskisiyle aynı: Discovery senkron çalışır, /ask onun sonucunu döner.
    # Yalnız `ask_async_discovery` açık tenant'larda Discovery'nin bu kendi kendine en yavaş
    # (LLM+self-healing) adımı arka-plan işine kuyruklanır (dış yol haritası 0.1 karşılığı).
    if "ask_async_discovery" not in resolve_for(settings, principal):
        return _run_discovery()
    return _queue_discovery_job(request, body, principal, _run_discovery)


@router.get("/ask/jobs/{job_id}", response_model=AskJobStatus,
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_job_status(job_id: str, request: Request) -> AskJobStatus:
    """Faz 4.1 — arka-plan Discovery işinin durumu (istemci bunu poll eder). Tamamlanmışsa
    `response` tam bir AskResponse'tur — client bunu normal /ask cevabı gibi işler (job_id
    alanı boş kalır, tekrar poll edilmez)."""
    import uuid as _uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import AskJob

    try:
        jid = _uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz iş kimliği.")
    with Session(engine) as s:
        job = s.get(AskJob, jid)
        if job is None:
            raise HTTPException(status_code=404, detail="İş bulunamadı.")
        # Tenant izolasyonu (RLS ilkesi, backend/CLAUDE.md): başka tenant'ın işi görülemez.
        principal = getattr(request.state, "principal", None)
        principal_tenant = getattr(principal, "tenant_id", None)
        if job.tenant_id is not None and str(job.tenant_id) != str(principal_tenant):
            raise HTTPException(status_code=404, detail="İş bulunamadı.")
        resp = AskResponse.model_validate_json(job.result_json) if job.result_json else None
        # Faz 4.12 — trace HENÜZ tamamlanmamışken de (pending/running) job.trace_json'dan
        # gelir; tamamlanınca resp.trace (tam/nihai liste) önceliklidir.
        trace = json.loads(job.trace_json) if job.trace_json else []
        if resp is not None and resp.trace:
            trace = resp.trace
        return AskJobStatus(id=str(job.id), status=job.status, question=job.question,
                            response=resp, error=job.error, trace=trace)


def _drill_record_contract(request: Request, service, session_id: str | None,
                           question: str, cq: dict, sql: str, result: dict) -> str | None:
    """/cube'un contract-kaydıyla AYNI desen (app/contracts.py) — HER dallanma adımı
    (expand/select/related) KENDİ kanıt kaydını üretir (kullanıcı talimatı: "HER dallanma
    adımı ayrı ayrı loglanır, tüm kök neden yolu SONRADAN yeniden oynatılabilir")."""
    store = getattr(request.app.state, "contracts", None)
    if store is None:
        return None
    try:
        principal = getattr(request.state, "principal", None)
        return store.record(
            session_id=session_id, question=question, cube_query=cq, sql=sql,
            result=result, source="drill", schema_version=service.mdl_version,
            tenant_id=getattr(principal, "tenant_id", None),
        )
    except Exception:
        _log.warning("drill query contract kaydedilemedi (best-effort)", exc_info=True)
        return None


@router.post("/ask/drill", response_model=DrillResponse,
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_drill(request: Request, body: DrillRequest) -> DrillResponse:
    """Faz 4.10 (1 Ağustos 2026) — dış yol haritası 2.5+2.15 "dallı kök-neden analizi
    temeli", kullanıcı talebiyle GENİŞLETİLMİŞ: yalnız "açıkla" değil, `action`'a göre
    GERÇEK sorgu çalıştırır (expand/select/raw/related) — kullanıcının "tüm veri ağacına
    ulaşabilmeli" ve "hesapta olan tüm ilişkiyi inceleyip dallandırılabilmeli" talebi
    (ör. OEE düşükken makine_duruslari'na geçip GERÇEK duruş nedenini görebilmek).

    Her GERÇEK sorgu adımı (expand/select/related) KENDİ Query Contract kaydını üretir
    (app/contracts.py — /cube ile AYNI ilke) VE cube'un TÜM ölçülerini birlikte döner
    (yalnız tek bir ölçü değil — "OEE düşük" derken YANINDA Kullanılabilirlik/Performans/
    Kalite/duruş dakikası da görünsün, kullanıcının "hesabı OLUŞTURAN ilişkiyi görme"
    talebi budur). Anomali tespiti `app/schedules.py::detect_anomalies` İLE AYNI z-skoru
    yöntemini kullanır (app/drill.py::flag_outliers — yeni bir istatistik motoru YOK).

    KAPSAM SINIRI: yapısal (cube-kaynaklı) sonuçlarda tam çalışır. Discovery/ham-SQL
    kaynaklı bir sonuç için `cube_query` yoktur — bu durumda dallanma sunulmaz, yalnız
    dürüst bir genel açıklama verilir (asla sahte bir dallanma UYDURULMAZ)."""
    import time as _time

    from app.drill import (
        available_dimensions,
        expand_cube_query,
        flag_outliers,
        formula_explanation,
        jump_to_related_cube,
        kpi_components,
        related_cubes,
        select_cube_query,
    )

    # KPI (bileşke metrik) — bu sistemde şu an inert (bkz. app/drill.py::kpi_components
    # docstring'i) ama şema hazır: dallanma sunulmaz, yalnız formül + bileşenler.
    if body.kpi:
        label = body.kpi.get("label") or body.kpi.get("kpi") or "KPI"
        formula = body.kpi.get("formula")
        explanation = (f"{label} = {formula}" if formula
                      else f"{label} — bileşke bir metriktir (birden çok cube'dan türetilir).")
        return DrillResponse(formula_explanation=explanation, kpi_components=kpi_components(body.kpi))

    if not body.cube_query or not body.cube_query.get("cube"):
        return DrillResponse(
            formula_explanation="Bu sonuç Discovery (ham-SQL) yoluyla üretildi — yapısal "
                                "bir cube_query taşımıyor, bu yüzden dallanma sunulamıyor. "
                                "Üretilen SQL'i \"sql göster\" ile inceleyebilirsin.",
        )

    service = _service_for(request, body.session_id)
    settings = get_settings()
    schema = service.schema()
    cubes_by_name = {c.get("name"): c for c in (schema.get("cubes") or [])}
    cube_meta = cubes_by_name.get(body.cube_query.get("cube"))
    if cube_meta is None:
        raise HTTPException(status_code=400, detail="Cube bulunamadı (şema değişmiş olabilir).")

    def _run(cq: dict) -> tuple[dict, str, float]:
        """cube_query'yi GERÇEKTEN çalıştırır (dry_plan+query, /cube ile AYNI adımlar) —
        (result_dict, sql, duration_ms) döner. Hata → HTTPException(400), asla çıplak 500.
        `sql`+`duration_ms` DrillResponse'a taşınır (UC-2.18/2.19 kanıt paneli — kullanıcı
        SQL'i kopyalayıp DB'de çalıştırdığında AYNI sonucu görmeli)."""
        started = _time.perf_counter()
        try:
            sql = service.cube_sql(cq, limit=settings.max_result_rows)
            service.dry_plan(sql)
            result = service.query(sql, limit=settings.max_result_rows)
            return result, sql, round((_time.perf_counter() - started) * 1000, 1)
        except Exception as exc:
            _log.warning("drill sorgusu çalıştırılamadı", exc_info=True)
            raise HTTPException(status_code=400,
                                detail=f"Bu dallanma adımı çalıştırılamadı: {str(exc)[:200]}")

    def _with_all_measures(cq: dict, meta: dict) -> dict:
        """Kullanıcı talebi: "hesapta olan TÜM ilişkiyi görebilmeli" — bir ölçüye
        bakarken cube'un DİĞER ölçüleri de (ör. OEE'nin yanında Kullanılabilirlik/
        Performans/Kalite/duruş dakikası) AYNI dilimde birlikte döner, tek bir sayı
        yerine hesabı oluşturan TÜM bileşenler görünür kalır."""
        all_measures = list(meta.get("measures") or [])
        return {**cq, "measures": all_measures or cq.get("measures") or []}

    def _anomalies_for(cq: dict, result: dict) -> list[dict]:
        dims = cq.get("dimensions") or []
        measures = cq.get("measures") or []
        primary = (body.cube_query.get("measures") or measures or [None])[0]
        if not dims or not primary or not result.get("rows"):
            return []
        try:
            return flag_outliers(result["rows"], dims[-1], primary)
        except Exception:  # noqa: BLE001 - yorumlama best-effort, rapor yine de döner
            _log.warning("drill anomali tespiti başarısız (best-effort)", exc_info=True)
            return []

    action = body.action

    if action == "explain":
        anomalies = []
        if body.result and body.result.rows:
            anomalies = _anomalies_for(body.cube_query, body.result.model_dump())
        active_dims = set(body.cube_query.get("dimensions") or [])
        active_dims |= {f.get("dimension") for f in (body.cube_query.get("filters") or [])}
        # UC-2.18 kanıt paneli: "explain" YENİ bir sorgu ÇALIŞTIRMAZ (mevcut result yeniden
        # kullanılır) ama SQL METNİ yine de üretilebilir (derleme, ÇALIŞTIRMA değil) — kullanıcı
        # ilk tıklamada bile formülün YANINDA gerçek SQL'i görsün. Başarısız olursa sessizce None
        # (bu alan "iyi olsun" niteliğinde, drill'in kendisini engellemez).
        try:
            explain_sql = service.cube_sql(body.cube_query, limit=settings.max_result_rows)
        except Exception:  # noqa: BLE001
            explain_sql = None
        return DrillResponse(
            cube_query=body.cube_query,
            formula_explanation=formula_explanation(body.cube_query, cube_meta),
            available_dimensions=available_dimensions(cube_meta, body.cube_query),
            related_cubes=related_cubes(cube_meta["name"], active_dims, list(cubes_by_name.values())),
            anomalies=anomalies,
            sql=explain_sql,
        )

    if action == "expand":
        if not body.dimension:
            raise HTTPException(status_code=400, detail="'expand' için 'dimension' gerekli.")
        new_cq = _with_all_measures(expand_cube_query(body.cube_query, body.dimension), cube_meta)
        result, sql, duration_ms = _run(new_cq)
        contract_id = _drill_record_contract(
            request, service, body.session_id,
            f"drill: {cube_meta.get('display') or cube_meta['name']} → {body.dimension}",
            new_cq, sql, result)
        active_dims = set(new_cq.get("dimensions") or [])
        active_dims |= {f.get("dimension") for f in (new_cq.get("filters") or [])}
        return DrillResponse(
            cube_query=new_cq,
            formula_explanation=formula_explanation(new_cq, cube_meta),
            available_dimensions=available_dimensions(cube_meta, new_cq),
            related_cubes=related_cubes(cube_meta["name"], active_dims, list(cubes_by_name.values())),
            anomalies=_anomalies_for(new_cq, result),
            result=QueryResult(**result),
            contract_id=contract_id,
            sql=sql,
            duration_ms=duration_ms,
        )

    if action == "select":
        if not body.dimension or body.filter_value is None:
            raise HTTPException(status_code=400,
                                detail="'select' için 'dimension' ve 'filter_value' gerekli.")
        new_cq = _with_all_measures(
            select_cube_query(body.cube_query, body.dimension, body.filter_value), cube_meta)
        result, sql, duration_ms = _run(new_cq)
        contract_id = _drill_record_contract(
            request, service, body.session_id,
            f"drill: {cube_meta.get('display') or cube_meta['name']} → "
            f"{body.dimension}={body.filter_value}",
            new_cq, sql, result)
        active_dims = set(new_cq.get("dimensions") or [])
        active_dims |= {f.get("dimension") for f in (new_cq.get("filters") or [])}
        return DrillResponse(
            cube_query=new_cq,
            formula_explanation=formula_explanation(new_cq, cube_meta),
            available_dimensions=available_dimensions(cube_meta, new_cq),
            related_cubes=related_cubes(cube_meta["name"], active_dims, list(cubes_by_name.values())),
            anomalies=_anomalies_for(new_cq, result),
            result=QueryResult(**result),
            contract_id=contract_id,
            sql=sql,
            duration_ms=duration_ms,
        )

    if action == "related":
        if not body.target_cube:
            raise HTTPException(status_code=400, detail="'related' için 'target_cube' gerekli.")
        target_meta = cubes_by_name.get(body.target_cube)
        if target_meta is None:
            raise HTTPException(status_code=400, detail="Hedef cube bulunamadı.")
        new_cq = jump_to_related_cube(body.cube_query, body.target_cube, target_meta)
        result, sql, duration_ms = _run(new_cq)
        contract_id = _drill_record_contract(
            request, service, body.session_id,
            f"drill: {cube_meta.get('display') or cube_meta['name']} → "
            f"{target_meta.get('display') or body.target_cube} (ilişkili veri)",
            new_cq, sql, result)
        active_dims = set(new_cq.get("dimensions") or [])
        active_dims |= {f.get("dimension") for f in (new_cq.get("filters") or [])}
        return DrillResponse(
            cube_query=new_cq,
            formula_explanation=formula_explanation(new_cq, target_meta),
            available_dimensions=available_dimensions(target_meta, new_cq),
            related_cubes=related_cubes(body.target_cube, active_dims, list(cubes_by_name.values())),
            anomalies=_anomalies_for(new_cq, result),
            result=QueryResult(**result),
            contract_id=contract_id,
            note=f"İlişkili veri: {target_meta.get('display') or body.target_cube}",
            sql=sql,
            duration_ms=duration_ms,
        )

    if action == "raw":
        from app.drill import build_raw_row_sql, UnsafeDrillError

        base_object = cube_meta.get("base_object") or cube_meta["name"]
        filters = list(body.cube_query.get("filters") or [])
        for d in (body.cube_query.get("dimensions") or []):
            if body.filter_value is not None and d == body.dimension:
                filters.append({"dimension": d, "operator": "eq", "value": body.filter_value})

        # KOLON SEÇİMİ (Faz A2) — eskiden `SELECT *`. Ham satır, sistemin en riskli
        # yüzeyidir: cube'un yayımlamadığı HER kolon (ör. `personel_ozluk.tc_kimlik`) gelir.
        # Artık yalnız `sensitivity: normal` kolonlar seçilir; hassas olan sorguya HİÇ
        # girmez (maskelemeye kalmadan — maskeleme son savunma, ilk savunma seçmemektir).
        from app.sensitivity import is_sensitive

        model = next((m for m in (schema.get("models") or [])
                      if m.get("name") == base_object), None)
        # Yalnız FİZİKSEL ve hassas-olmayan kolonlar. Calc kolonu ve ilişki handle'ı
        # tabloda yoktur (`SELECT personel FROM partiler` → binder hatası); ham satır
        # sorgusu semantik katmandan değil TABLODAN okur.
        secilebilir = [c["name"] for c in (model or {}).get("columns", [])
                       if not is_sensitive(c)
                       and not c.get("is_calculated") and not c.get("relationship")]
        try:
            raw_sql = build_raw_row_sql(base_object, filters, limit=body.limit,
                                        columns=secilebilir)
        except UnsafeDrillError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        # ALWAYS_FILTER (Faz A2) — `_inject_always_filter` YALNIZ `cube_sql`/`blend_sql`
        # yolunda uygulanıyordu; ham yaprak onu tamamen atlıyordu. `always_filter`
        # fail-closed'dır (MIMARI §4-5) ve sessizce düşmesi bir P0'dır: `ticaret`
        # cube'unun `tur='satis'` filtresi olmadan ham satır çekmek `alis` verisini
        # sızdırır (ölçülen vakada 34M TL).
        raw_sql = service._inject_always_filter(raw_sql, cube_meta.get("name"))

        started = _time.perf_counter()
        try:
            service.dry_plan(raw_sql)
            raw_result = service.query(raw_sql, limit=body.limit)
        except Exception as exc:
            _log.warning("drill ham-satır sorgusu başarısız", exc_info=True)
            raise HTTPException(status_code=400,
                                detail=f"Ham satırlar getirilemedi: {str(exc)[:200]}")
        duration_ms = round((_time.perf_counter() - started) * 1000, 1)

        # PII MASKELEME (Faz A2) — ham satır yolunda hiç çalışmıyordu. Kolon seçimi
        # yapısal kolonları eler; bu, SERBEST METİN içine gömülü PII'yi (açıklama
        # alanındaki telefon/IBAN) yakalayan ikinci savunmadır. Rol-duyarlı: `pii:view`
        # yetkisi olan maskesiz görür ve bu erişim audit'e düşer.
        _principal_raw = getattr(request.state, "principal", None)
        raw_result, _pii_acildi = pii.mask_query_result(raw_result, _principal_raw)
        contract_id = _drill_record_contract(
            request, service, body.session_id,
            f"drill: {cube_meta.get('display') or cube_meta['name']} → ham satırlar",
            body.cube_query, raw_sql, raw_result)
        # AUDIT (Faz A2, ADR-0014 K6) — bu yol tenant verisinin HAM SATIRLARINI dışarı
        # veriyor ve hiçbir iz bırakmıyordu. Denetlenebilirlik iddiası olan bir sistemde
        # en çok iz gerektiren yüzey tam da budur. `_pii_acildi` ayrıca kaydedilir:
        # maskesiz PII görüldüyse KİM gördüğü bilinmelidir.
        try:
            from control_plane import audit

            audit.record(
                _principal_raw,
                "drill_raw_view" if not _pii_acildi else "drill_raw_view_pii_unmasked",
                nl_question=f"drill ham satır: {base_object}",
                generated_sql=raw_sql,
                rows_returned=raw_result.get("row_count"),
                contract_id=contract_id,
                ip=request.client.host if request.client else None,
            )
        except Exception:
            _log.warning("drill ham-satır audit kaydı başarısız (best-effort)", exc_info=True)

        return DrillResponse(
            cube_query=body.cube_query,
            formula_explanation=f"{base_object} tablosunun bu dilime ait ham satırları "
                                f"(en fazla {body.limit}).",
            raw_rows=RawRow(**raw_result),
            contract_id=contract_id,
            sql=raw_sql,
            duration_ms=duration_ms,
        )

    raise HTTPException(status_code=400, detail=f"Bilinmeyen action: {action!r}")


@router.post("/ask/contribution", response_model=ContributionResponse,
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_contribution(request: Request, body: ContributionRequest) -> ContributionResponse:
    """FAZ 5.2 — *"neden değişti?"* KATEGORİ BOŞLUĞU.

    Rakiplerin hepsinde bir karşılığı var (Snowflake `TOP_INSIGHTS`, Power BI Key
    Influencers, Tableau Pulse) ve hepsi semantic layer'ın DIŞINDA: ürettikleri şey bir
    metin ya da görsel — yeniden tarihlenemez, kırılamaz, sözleşme taşımaz. Buradaki fark
    şu: **her bulgu kendi başına bir CubeQuery'dir.** Tıklanır, `/cube` ile LLM'siz koşar,
    kendi Query Contract'ını üretir, üstüne yeni kırılım eklenebilir.

    Yöntem cebirsel ve deterministik (LLM yok, eğitim yok, rastgelelik yok): kullanılmayan
    her boyut için dönemsel kıyas (`app/yoy.py` — YENİ bir dönem matematiği YAZILMADI)
    alınır, değişim segmentlere dağıtılır, boyutlar açıklayıcılığa göre sıralanır.

    **Toplanabilirlik kapısı esastır** (`app/contribution.py::ayristirilabilir_mi`): katkı
    ayrıştırması yalnız toplanabilir ölçülerde TANIMLIDIR. `AVG`/oran/`COUNT(DISTINCT)`
    için parçaların toplamı bütünü vermez ve "bu segment değişimin %40'ını açıklıyor"
    cümlesi matematiksel olarak yanlış olur. Bu, bu araç sınıfının klasik sessiz hatasıdır
    — burada ayrıştırma yapılmaz ve NEDENİ söylenir (ADR-0008'in ölçü-matematiği karşılığı).
    """
    from app import contribution as contrib
    from app import yoy as _yoy
    from app.drill import available_dimensions

    cq = dict(body.cube_query or {})
    if not cq.get("cube"):
        return ContributionResponse(note="Bu sonuç yapısal bir cube_query taşımıyor "
                                         "(Discovery/ham SQL) — katkı ayrıştırması yapılamaz.")
    service = _service_for(request, body.session_id)
    schema = service.schema()
    cube_meta = next((c for c in (schema.get("cubes") or [])
                      if c.get("name") == cq.get("cube")), None)
    if cube_meta is None:
        raise HTTPException(status_code=400, detail="Cube bulunamadı (şema değişmiş olabilir).")

    kind = body.kind if body.kind in ("segment", "pvm") else "segment"
    measure = (cq.get("measures") or [None])[0]

    ciftler = contrib.pvm_pairs(cube_meta)
    if kind == "pvm":
        # Eşleştirme TAHMİN EDİLMEZ: cube'un `pvm:` beyanı yoksa PVM sunulmaz. Ad kalıbıyla
        # (ör. "tutar/adet fiyattır") tahmin etmek, yanlış eşleştirmede GÜVENLE YANLIŞ
        # ekonomi üretirdi — kullanıcı "birim fiyat %12 arttı" cümlesini sorgulamaz.
        cift = next((p for p in ciftler if p["value"] == measure), None)
        if cift is None:
            return ContributionResponse(
                measure=measure, mode=body.mode, kind=kind,
                note=(f"`{cq.get('cube')}` cube'u `{measure}` için bir fiyat×miktar "
                      "eşleştirmesi BEYAN ETMİYOR (cube metadata'sında `pvm:`). Fiyat "
                      "ayrıştırması ancak beyan edilmiş bir değer/miktar çifti üzerinde "
                      "anlamlıdır; tahmin edilmez."))
    else:
        ok, neden = contrib.ayristirilabilir_mi(measure, cube_meta)
        if not ok:
            return ContributionResponse(measure=measure, mode=body.mode, kind=kind, note=neden)
        cift = None

    mode = body.mode if body.mode in ("yoy", "mom") else "yoy"
    time_dim = _yoy.time_dim_of(schema, cq.get("cube"))
    unit = (cube_meta.get("units") or {}).get(measure)
    labels = cube_meta.get("dimension_labels") or {}

    adaylar = [d["name"] for d in available_dimensions(cube_meta, cq)]
    sinir = max(1, int(body.max_dimensions or contrib.MAX_BOYUT))
    taranan, taranmayan = adaylar[:sinir], max(0, len(adaylar) - sinir)
    if taranmayan:
        # Sessiz kesme YOK: kapsamı daraltan her sınır loglanır VE yanıtta görünür.
        _log.info("katkı araması: %d boyuttan %d tanesi taranmadı (sınır=%d, cube=%s)",
                  len(adaylar), taranmayan, sinir, cq.get("cube"))

    raporlar, pvm_raporlar, contract_ids = [], [], []
    for dim in taranan:
        # PVM iki ölçüyü BİRLİKTE ister (değer ve miktar aynı kıyas sorgusunda gelsin ki
        # segment hizalaması kesin olsun; ayrı iki sorgu satır kümesi ayrışabilirdi).
        olculer = [cift["value"], cift["volume"]] if cift else list(cq.get("measures") or [])
        alt = {**cq, "measures": olculer, "dimensions": [dim]}
        try:
            out = _yoy.compute(service, {**alt, "compare": mode}, mode, time_dim)
        except Exception:
            _log.warning("katkı araması: %s boyutu için kıyas başarısız (atlanıyor)",
                         dim, exc_info=True)
            continue
        if cift:
            rapor = contrib.pvm_report(out["rows"], dim, cift, alt,
                                       dim_label=labels.get(dim), unit=unit)
            if not rapor["bulgular"]:
                continue
            pvm_raporlar.append(rapor)
        else:
            rapor = contrib.decompose(out["rows"], dim, measure, alt,
                                      dim_label=labels.get(dim), unit=unit)
            if not rapor["bulgular"]:
                continue
            raporlar.append(rapor)
        # Her katkı sorgusu KENDİ kanıt kaydını üretir — "yeniden çalıştırılıp hash
        # eşlenebilen makbuz" değişmezi burada da geçerli (drill ile AYNI desen).
        cid = _drill_record_contract(
            request, service, body.session_id,
            f"katkı araması: {measure} × {dim} ({mode})", {**alt, "compare": mode},
            out["base_sql"], {"columns": out["columns"], "rows": out["rows"],
                              "row_count": out["row_count"]})
        if cid:
            contract_ids.append(cid)

    if not raporlar and not pvm_raporlar:
        return ContributionResponse(
            measure=measure, mode=mode, kind=kind, taranmayan_boyut=taranmayan,
            note="Bu sorguda değişimi açıklayan bir kırılım bulunamadı — kullanılmayan "
                 "boyut yok ya da hiçbir segment anlamlı bir hareket göstermiyor.")

    return ContributionResponse(
        measure=measure, mode=mode, kind=kind, taranmayan_boyut=taranmayan,
        contract_ids=contract_ids,
        raporlar=[ContributionReport(**r) for r in contrib.rank_dimensions(raporlar)],
        pvm_raporlar=[PvmReport(**r) for r in contrib.rank_dimensions(pvm_raporlar)])


@router.post("/ask/verify", dependencies=[Depends(require("vqr:write")), Depends(require_company)])
def ask_verify(request: Request, body: AskVerifyRequest) -> dict:
    """Strict-agentic /ask cevapları için geri bildirim (UI '✓ doğru' / '✗ yanlış' düğmeleri) —
    `/verify`'nin (CubeQuery) wren_sql karşılığı. Bu uç nokta olmadan VQR'a hiçbir wren_sql
    çifti yazılmaz: sistem aynı/benzer soruyu her seferinde yeniden LLM'e sorar, hiç
    "öğrenmez". Onaylanan SQL önce dry_plan'dan geçirilir — geçersiz bir onay VQR'ı kirletip
    gelecekteki tekrar-oynatmaları bozamaz.

    - verdict=right (varsayılan): soru→wren_sql çifti VQR'a yazılır (few-shot + gelecekte
      birebir eşleşirse LLM'siz tekrar oynatma).
    - undo=true: önceki onay geri alınır.
    - verdict=wrong: negatif sinyal — VQR'daki (varsa) çift silinir; her durumda loglanır.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Soru eksik.")
    from app.company_registry import vqr_for_request

    vqr = vqr_for_request(request)
    principal = getattr(request.state, "principal", None)
    verdict = "wrong" if body.verdict == "wrong" else ("undo" if body.undo else "right")
    stored = removed = False
    if vqr is not None:
        if body.undo or body.verdict == "wrong":
            removed = vqr.remove(body.question)
        elif body.sql and body.sql.strip():
            service = _service_for(request, body.session_id)
            try:
                service.dry_plan(body.sql)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"SQL doğrulanamadı: {exc}") from exc
            stored = vqr.store(body.question,
                               {"wren_sql": body.sql, "mdl_version": service.mdl_version},
                               source="user_verified",
                               extra={"verified_by": getattr(principal, "user_id", None),
                                      "tenant_id": getattr(principal, "tenant_id", None)})

    from types import SimpleNamespace

    comment = (body.comment or "").strip() or None
    trace = [f"kullanıcı geri bildirimi (/ask) → {verdict}"
             + (" · VQR'a yazıldı" if stored else " · VQR'dan silindi" if removed else "")
             + (f" · yorum: {comment}" if comment else "")]
    _log_interaction(
        body.session_id,
        SimpleNamespace(question=f"ask-verify[{verdict}]: {body.question}", cube_query=None),
        SimpleNamespace(source="verify", sql=body.sql, result=None,
                        note=(comment if verdict == "wrong" else None),
                        cube_query=None, trace=trace, interpretation=None),
        0,
        principal,
    )
    from control_plane import audit

    audit.record(principal, "verify",
                 nl_question=f"[{verdict}] {body.question}" + (f" · {comment}" if comment else ""),
                 ip=request.client.host if request.client else None)
    return {"stored": stored, "removed": removed}

