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
from app.schemas import AskRequest, AskResponse, Explain

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
    # 🔴🔴 `§MV` — **NOT SÖYLÜYORDU, MAKBUZ SUSUYORDU.**
    #
    # ⊙ Ölçüldü (curl `N+1` turu, 2026-08-10 · kapı testinin yakaladığı hâliyle):
    #
    #     «makine bazında ortalama oee»
    #       note    : ⏱ Dönemi çözemedim — verinin son 12 ayı alındı …
    #       explain : {confidence: 1.0, assumptions: **[]**}
    #
    # Yani `varsayilan_donem` (`D3`) bir varsayım yapıyor, cevabın **metni** onu dürüstçe
    # itiraf ediyor, ama **makbuz** hiç haberdar değil: rozet açıkça tarih verilmiş bir
    # cevapla **aynı** kesinliği gösteriyordu (`1.0`).
    #
    # 🔴 Ve makbuz denetlenebilir yüzeydir: `interaction_log`'a yazılan, frontend'in
    # rozetlediği, *"bu sayıya ne kadar güvenebilirim"* sorusunun cevabı odur. Bir metin
    # cümlesi okunmayabilir; makbuz **her zaman** okunur.
    #
    # ⚠ Kaynak **izdir**, `note` metni değil: metin bir gün değişebilir (bugün üç kez
    # değişti — `§BD`), iz bir **sabittir** ve taşıyıcının kendi yazdığı şeydir.
    # İkinci bir yüklem yazmak `KAT-1` olurdu.
    #
    # ⊙ Ve hemen aşağıdaki kural bunu **zaten** bekliyordu: *"sessiz bir varsayım
    # yapıldıysa güven bir kademe DÜŞÜRÜLÜR"*. Kural yazılıydı, girdisi eksikti.
    #
    # *Bir varsayımı cevabın metninde itiraf edip makbuzunda gizlemek, itirafın kendisini
    # bir üsluba çevirir.*
    else:
        from app.donem_capasi import IZ_VARSAYILAN

        if IZ_VARSAYILAN in (resp.trace or []):
            assumptions.append(
                "Dönem çözülemedi — verinin son 12 ayı BEYANLA varsayıldı "
                "(kullanıcı onaylamadı; tek tıkla değiştirilebilir)."
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
    """⟳ `KAT-1` — tek sahip `control_plane.audit.uuid_or_none`; burası **çağırır**.

    Beş kopyanın beşi de aynı işi yapıyordu (ölçüldü); ayrı ayrı yaşamaları bir gün
    beşinin **farklı** davranmasıyla biterdi. İçe alma tembeldir: modül yükünü
    artırmamak için ㊲.
    """
    from control_plane.audit import uuid_or_none
    return uuid_or_none(val)


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
                     dur_ms: int, principal=None, request=None,
                     red_gerekcesi: str | None = None) -> None:
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
                # 🔴 `red_gerekcesi` — çağıran gerekçeyi **biliyorsa** o kazanır.
                # Arka-plan işi patladığında `_teshis` bir şey üretemez: kimlik
                # thread'e kopyalanmaz (`discovery_kuyrugu`'nun kendi sınırı), şema
                # okunamaz ve hesap `None` döner. Gerekçesiz bir cevapsızlık kaydı,
                # *kaç soru cevaplanamadı* sayacını doldurur ama **neden**ini boş
                # bırakır — ve o kolonun tek varlık sebebi o sorudur.
                reject_reason=red_gerekcesi or _teshis(body.question, _sema(request)),
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
    # 🔴 `§YV` — yön varsayımı beyanı **yorumun doğduğu yerde**. `uyum.denetle`'ye
    # konsaydı hiç ateşlemezdi: orada `interpretation` henüz yok (canlıda ölçüldü) ve
    # `denetle`'nin ÜÇ çağıranı var — kök-neden soruları planlayıcı yolundan geçiyor.
    try:
        from app.uyum import yon_beyani
        yon_beyani(resp)
    except Exception:  # noqa: BLE001
        _log.warning("yön varsayımı beyanı üretilemedi (best-effort)", exc_info=True)
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

        # 🔴 **T2'NİN İLK BASAMAĞI — ve LLM'DEN ÖNCE.** Merdiven ilkesi (`MIMARI §4`):
        # her basamak bir öncekinin yapamadığını yapar. Anlatının ilk basamağı
        # yazılmamıştı: `t2_anlatici` açıksa LLM, kapalıysa **hiç**.
        #
        # ⊙ Oysa `interpret()` yapılandırılmış olgular üretiyor (`trend`/`delta`/`peak`…)
        # ve *"ne yüksek ne düşük"* demek için bir modele ihtiyaç yok.
        #
        # ⚠ Şablon **sayıya dokunmaz**: cümleyi `interpret()`'in kendi metinlerinden
        # kurar. `narration_guard`'dan geçmesi tesadüf değil **yapısal**.
        #
        # 🔴 Ve devir koşulu **tanınmayanın varlığıdır**: bilmediği bir olgu türünü
        # görmezden gelip kalanı anlatmak, kullanıcıya *eksik ama tam görünen* bir özet
        # vermek olurdu. *Bir merdivenin basamağı, ne yapamadığını bilmiyorsa basamak
        # değil bir tahmindir.*
        if "t2_sablon" in resolve_for(get_settings(), principal):
            from app import anlatici as _anlatici

            if _anlatici.basit_mi(yorum):
                # 🔴 **ASIL KAZANÇ METİN DEĞİL, YAPILMAYAN ÇAĞRI.** Canlı ölçüldü:
                #
                # | tur | toplam | anlatı LLM | pay |
                # |---|---|---|---|
                # | *"makine bazında oee son 3 ay"* | 5.420 ms | **2.936 ms** | %54 |
                # | *"aylara göre"* (takip) | 24.285 ms | 🔴 **22.564 ms** | **%93** |
                #
                # İki turda da **intent 0 LLM** aldı (`route()` / `deterministic_refine`);
                # bekleyişin tamamı **süslemeydi**. Ve süslenen şey `summary`'nin taşıdığı
                # **aynı üç olguydu** — LLM'in kattığı bilgi değil, üsluptu.
                #
                # 🔴 Bu yüzden şablon basamağı **metin üretmese bile** durur: `summary`
                # zaten yazılı ve kullanıcı onu görüyor. Bir cümleyi ikinci kez, 22 saniye
                # bekleterek yazdırmak bir kazanç değil bir **fatura**dır.
                #
                # ⚠ İlk yazımda yankı kapısı buraya **yanlış** yerleştirilmişti: metin
                # `summary` ile aynıysa `None` dönüyordu ve tur **LLM'e düşüyordu** — yani
                # kapı, önlemek için var olduğu çağrıyı **davet ediyordu**.
                # *Bir eniyileştirmenin ölçütü ürettiği çıktı değil, engellediği iştir.*
                yorum["narration_kaynak"] = "sablon"       # makbuz: LLM devreye GİRMEDİ
                if (_sablon := _anlatici.anlat(yorum)):
                    yorum["narration"] = _sablon           # yalnız EK BİLGİ varsa
                _log.info("T2 ŞABLON: LLM çağrısı YAPILMADI (0 token, 0 ms)")
                return
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

        # 🔴 G5.1 — ÖN KOŞUL KİLİDİ. Anlatıcı, `iddia.py` OLMADAN açılamaz.
        #
        # `narration_guard` yalnız **rakamı** korur; `iddia.py` **cümleyi**. İkincisi
        # yoksa anlatı, korunmayan bir yüzeye açılır: *"tedarikçi kırılımı da
        # ekleyebilirim"* hiçbir kapıya takılmadan kullanıcıya ulaşırdı.
        # Fail-closed: modül yoksa anlatı **hiç üretilmez**, cevap deterministik kalır.
        try:
            import app.iddia as _iddia_kontrol  # noqa: F401
        except ImportError:
            _log.error("T2 anlatı ENGELLENDİ: `app/iddia.py` YOK — §4'ün ikinci "
                       "değişmezi kurulmadan anlatıcı açılamaz (G5.1).")
            return

        # FAZ 9.8 — ÇAĞRI PLANLAYICIDAN GEÇER. MIMARI §12.6b *"prompt-enhancer için
        # koşulan şart (kapısız LLM çağrısı olmasın; makbuzda ADIM olarak görünsün)
        # anlatıcı için de uygulandı"* diyordu; kayıt (`tools.KAYIT`) doğruydu ama
        # ÇAĞRI doğrudandı — yani beyanın ikinci yarısı **karşılıksızdı**. Denetimde
        # bulundu; bu deponun on dört kez avladığı *"beyan var, kod onu tanımıyor"* sınıfı.
        #
        # Kapıların burada gerçek karşılığı: **bütçe** (sıcak yola giren LLM çağrısı
        # sayılır) ve **makbuz** (*"LLM ne zaman devreye girdi"* cevaplanabilir olur).
        # 🔴 **SÜSÜN BÜTÇESİ — canlı ölçüm (2.936 / 22.564 / 69.399 ms).**
        #
        # Anlatı bir **süslemedir**: altındaki `summary` zaten yazılı ve doğru. Aşılırsa
        # anlatı **düşer**, cevap **düşmez** — en kötü durum yine *"süssüz ama doğru"*,
        # yani `narration_guard`'ın kendi sözleşmesiyle **aynı** en-kötü-durum.
        #
        # ⚠ Bütçe **çağırandadır**, sağlayıcıda değil: *"süs ne kadar bekletebilir"* bir
        # ürün kararıdır. Sağlayıcıya koymak, üç sağlayıcıda üç ayrı karar demekti.
        #
        # *Bir süsün bütçesi, süslediği şeyin süresini aşamaz.*
        from app import planner as _planner

        plan = _planner.Planlayici(
            principal=principal,
            # 🔴 `sorgu=0` = o eksende **sınırsız** (`Butce` sözleşmesi). Burada
            # meşru ve gerekçesi YAPISAL: bu planlayıcıya `servis:wren` **hiç
            # verilmiyor** (aşağıdaki `kaynaklar`), yani sorgu **koşamaz**. Eksen
            # sınırsız değil, **uygulanamaz**. ⚠ `servis:wren` bir gün eklenirse bu
            # satır bir tavan almalı — `test_c2_butce_stall` bunu ölçüyor.
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
        # 🔴 Bütçe **burada** uygulanır: `plan.calistir` bir duvar-saati sınırı taşımıyor
        # (bütçesi adım/sorgu sayar). Aşılırsa anlatı düşer, cevap yaşar.
        _azami = float(getattr(get_settings(), "anlati_azami_saniye", 8.0) or 8.0)
        # ⚠ **Çağrı biçimi bilerek korunuyor**: `plan.calistir("llm.anlat", …)` bir
        # kapının çapasıdır (`test_ANLATICI_PLANLAYICIDAN_geciyor` bu metni arar) ve
        # `submit(plan.calistir, …)` biçimine çevirmek onu **kırdı**. Lambda hem bütçeyi
        # uygular hem çapayı yerinde bırakır.
        # *Bir kapının ölçtüğü şey metinse, metni de o kapıya göre yazarsın.*
        #
        # 🔴 **VE BU BÜTÇE ÇALIŞMIYORDU — aşağıdaki yorum kodun YAPMADIĞI şeyi anlatıyordu.**
        # *"İş arka planda bitmeye devam eder — ama cevabı bekletmez"* yazıyordu; oysa
        # `with _cf.ThreadPoolExecutor(...)` çıkışta `shutdown(wait=True)` çağırıyor ve
        # cevabı tam olarak **bekletiyordu**. Ölçüldü (`§33`): bütçe 8 sn, anlatı çağrısı
        # **66.202 ms**, tur **81.656 ms** — ve `BÜTÇEYİ AŞTI` satırı 66. saniyede
        # yazıldı, 8.'de değil. Uygulama tek sahibe taşındı: `app/butce.py`.
        # *Bir yorumun anlattığı davranış ölçülmemişse, o bir belge değil bir dilektir.*
        from app import butce as _butce
        _sonuc = _butce.kos(
            [lambda: plan.calistir("llm.anlat", resp.question, gercekler)],
            saniye=_azami, ad="T2 anlatı", log=_log)[0]
        if _sonuc is _butce.ASIM:
            # İş arka planda biter (thread öldürülemez) ama cevabı **artık** bekletmez.
            # *Bir süs, süslediği şeyi geciktiriyorsa süs değil engeldir.*
            return
        ham = _sonuc
        _anlati_makbuzu(resp, plan)
        ham, _yayilim_sorunlari = geri_koy(ham or "", _harita)
        if _yayilim_sorunlari:
            # Model yuvayı bozduysa ya da UYDURDUYSA cümle güvenilmezdir. Sessizce
            # geri koymak, bozulmuş bir cümleyi doğru göstermek olurdu.
            _log.info("T2 anlatı YAYILIM BOZULDU (%d): %s",
                      len(_yayilim_sorunlari), ", ".join(_yayilim_sorunlari[:5]))
        resp.hava_boslugu = {"yer_tutucu": len(_harita),
                             "bozulan": len(_yayilim_sorunlari)}

        # 🔴 G4 — İDDİA KAPISI, guard'ın YANINDA. İkisi de `seal()`'in önünde durur ve
        # farklı şeyleri korur: guard **rakamı**, iddia **cümleyi**. §4'ün değişmezi
        # burada ikiye bölünür — gevşemez, BÖLÜNÜR.
        from app import iddia as _iddia

        # 🔴 **YEREL İMPORT ZORUNLU — ve eksikliği CANLI KAPI buldu.**
        #
        # `:248`'in notu açık: *"`wren_for_request` bu modülde HER YERDE yerel olarak
        # alınıyor."* `G4` bu satırı yazmayı atladı ve sonuç `NameError` oldu — ama
        # aşağıdaki `except Exception` onu **yuttu**: kapı her turda sessizce şemasız
        # koştu, yani her yetenek vaadi *"katalog yok → doğrulanamaz"* diye düştü.
        #
        # ⊙ Hiçbir birim testi göremedi (hepsi `dogrula()`'yı **doğrudan** şemayla
        # çağırıyor); süit de göremedi (`t2_anlatici` kapalıyken bu dal hiç koşmuyor).
        # Onu bulan `lab/garson.py --live` oldu — **kapının varlık sebebi tam budur**.
        #
        # *Bir `except Exception`, kapsadığı kodun yazılmamış olmasını da başarıyla
        # gizler.*
        from app.company_registry import wren_for_request

        try:
            _sema = wren_for_request(request).schema()
        except Exception:                                  # noqa: BLE001
            _sema = None                                   # fail-closed: katalog yoksa
            _log.warning("iddia kapısı için şema okunamadı", exc_info=True)
        _ir = _iddia.dogrula(ham, _sema)
        resp.hava_boslugu = {**(resp.hava_boslugu or {}),
                             "iddia_dusen": len(_ir.reddedilen)}
        if _ir.reddedilen:
            _log.info("İDDİA KAPISI: %d cümle düştü — %s",
                      len(_ir.reddedilen), "; ".join(_ir.gerekceler[:3]))
        ham = _ir.temiz_metin

        metin, rapor = guvenli_anlatim(
            ham, resp.result.model_dump() if resp.result else None, yedek=None)
        if not metin:
            # Tüm cümleler düştü — sessizce geç. Deterministik `summary` zaten orada.
            _log.info("T2 anlatı GUARD'DA DÜŞTÜ (yayımlanmadı): reddedilen=%d",
                      len(getattr(rapor, "reddedilen", []) or []))
            return
        yorum["narration"] = metin
        yorum["narration_kaynak"] = "llm"                 # makbuz: hangi basamak yazdı
        # 🔴 `DA-4` — GUARD'IN MAKBUZU KULLANICIYA ULAŞIYOR.
        #
        # `narration_guard.Rapor.makbuza()` yazılmıştı ve **hiçbir yerden
        # çağrılmıyordu**: `G5.4`'ün *"muafiyetler GÖRÜNÜR olur"* kazancı yalnız log'a
        # gidiyordu. Oysa maddenin kendi gerekçesi *"kullanıcı «her sayı doğrulanır»
        # sanıyordu; bir muafiyeti gizlemek, onu bir garanti gibi göstermenin en kısa
        # yoludur"* diyor — yani makbuza yazılmadıkça madde **kendi teşhisini** tekrar
        # üretir.
        #
        # ⚠ Yeni alan/panel YOK: iddia kapısının izi nerede duruyorsa oraya, aynı
        # `hava_boslugu` bloğuna girer. *İki kapıyı iki ayrı yere yazmak, onları iki ayrı
        # şeymiş gibi gösterir.*
        try:
            _mk = rapor.makbuza()
            resp.hava_boslugu = {
                **(resp.hava_boslugu or {}),
                "anlati_dogrulandi": bool(_mk.get("narration_verified")),
                "anlati_dusen": int(_mk.get("rejected_sentences") or 0),
                "guard_muaf": _mk.get("muaf"),
            }
            # 🔴 `Ö5` — DÜŞME ORANI KAYAN PENCEREYE. `iddia.py`'nin kendi sözü:
            # *"düşme oranı ÖLÇÜLÜR — kapı agresifse gevşetilir, ama ÖLÇÜYLE."*
            # Söz yazılmıştı, ölçüm kurulmamıştı. Model/prompt değişince kapılar TÜM
            # anlatıyı düşürmeye başlayabilir: kullanıcı yanlış sayı görmez (güvenli)
            # ama sistem sürekli "soğuk" cevap verir ve **hiçbir alarm çalmaz**.
            # *Bir kapının sessizce her şeyi düşürmesi, hiç olmamasından farksızdır —
            # tek fark, sistemin kendini güvende sanmasıdır.*
            from app import guard_alarmi as _alarm

            _alarm.kaydet(int(_mk.get("rejected_sentences") or 0),
                          int(_mk.get("total_sentences") or 0))
        except Exception:                                  # noqa: BLE001 — makbuz süstür
            _log.warning("guard makbuzu yazılamadı", exc_info=True)
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


def _temellendir(request: Any, resp: AskResponse) -> None:
    """🔴 `G1` — cevap **ne anladığını söyler**. 0 LLM · 0 token.

    ⚠ **Beyan kanalı PAYLAŞILIR:** `uyum.kismi_cevap_notu` bir ihlal bulduğunda zaten
    konuşuyor (`beyanli_kismi`). Bu, o kanalın **eksik yarısıdır** — sistem yanıldığını
    söylüyordu, anladığını söylemiyordu. İkinci bir beyan üreteci YAZILMAZ.

    🔴 **0 token olması bir tasarım özelliğidir:** LLM tamamen düşse bile (kota · ağ ·
    429) bu satır **yine basılır** — bozulma merdiveninin 3. basamağı.
    """
    # 🔴 **NETLEŞTİRME TURU DA TEMELLENDİRİLİR — ve bunu CANLI KAPI buldu.**
    #
    # İlk kapı `resp.source is None` ise dönüyordu, gerekçesi *"netleştirme cevabında
    # temellendirilecek bir sorgu YOK"*. **Ölçüldü ve yanlış çıktı:** `fire kg` →
    # `source=None` (dönem soruluyor) ama `cube_query` **dolu**:
    # `{'cube': 'parti', 'measures': ['toplam_fire_kg']}`.
    #
    # Yani kapı, temellendirmenin **en değerli** olduğu anda susuyordu: sistem *"hangi
    # dönem?"* diye sorarken *"fire kg'yi anladım"* demiyordu. Kullanıcı açısından bu,
    # sorunun **neyin üstüne** sorulduğunu bilmemek demektir — `G1`'in kapatmak için
    # yazıldığı boşluğun ta kendisi.
    #
    # ⚠ Gürültü riski yok: düz retlerde `cube_query` **boştur** (ölçüldü: `{}`), ve
    # `kur()` söyleyecek bir şey yoksa zaten `None` döner (*"boş sözlük dönmez"*).
    #
    # *Bir kapının gerekçesi, kapının kendisinden daha hızlı bayatlar.*
    if not resp.cube_query:
        return
    try:
        from app.temellendirme import kur

        # 🔴 `G6.3` — kıyas satırı **bayrağa bağlı** (`KURAL B`): kapalıyken makbuz
        # bayt bayt bugünkü. `hedef_kiyasi`'nın hemen altındaki desenin aynısı — bir
        # bayrağı okumanın ikinci bir biçimini icat etmek, iki bayrak yönetimi demektir.
        from app.config import get_settings as _gs2
        from app.features import resolve_for as _rf2

        _kiyas = False
        try:
            _kiyas = "referans_dili" in _rf2(
                _gs2(), getattr(getattr(request, "state", None), "principal", None))
        except Exception:                                  # noqa: BLE001 — makbuz düşmez
            _log.warning("referans_dili çözülemedi → kıyas satırı YOK", exc_info=True)
        resp.temellendirme = kur(
            resp.cube_query,
            katalog=getattr(resp, "_etiketler", None),
            cube_etiketi=(resp.cube_query or {}).get("cube"),
            kiyas=_kiyas)
    except Exception:                                      # noqa: BLE001 — best-effort
        _log.warning("temellendirme kurulamadı (cevap etkilenmez)", exc_info=True)


def _diyalog_durumu(resp: AskResponse, log_body: Any) -> None:
    """🔴 `G2` — sistem NE SORDUĞUNU hatırlar. Durumsuz taşıma: cevapta döner,
    istemci yankılar.

    ⚠ **Bu adım DAVRANIŞI DEĞİŞTİRMEZ** — yalnız KAYDEDER. Devam/onarım davranışı
    `G2.7`/`G2.8`'de gelir. Ara commit'in anlamı budur: bir belleği önce **görünür**
    kılarsın, sonra **kullanırsın**; tersi, göremediğin bir şeye güvenmek olurdu.
    """
    try:
        from app.diyalog import durum

        # ⚠ İstek gövdesi `seal`'in ZATEN aldığı `log_body`'dir — ikinci bir taşıyıcı
        # icat edilmedi. `/cube` gibi farklı şemalı uçlar `SimpleNamespace` verir ve
        # `getattr` orada da doğru çalışır (alan yoksa `None`).
        onceki = getattr(log_body, "diyalog_durumu", None)
        # `sorulan`: bu tur bir netleştirme ürettiyse hangi yuvayı sorduğu.
        # ⚠ Kaynağı `suggestions[].kind` DEĞİL, cevabın kendi eksiğidir — chip'in
        # görünüşü değişebilir, eksik yuva değişmez.
        sorulan = None
        if resp.source is None and resp.suggestions:
            from app.diyalog import SLOT_DONEM, SLOT_OLCU
            metin = " ".join(str(s.query or "") + str(s.label or "")
                             for s in resp.suggestions).lower()
            sorulan = SLOT_DONEM if any(k in metin for k in ("ay", "yıl", "dönem")) \
                else SLOT_OLCU
        # 🔴 KISMİ SORGU: netleştirme dalları `cube_query=None` döndürüyor ama o turda
        # bir şey ANLAŞILMIŞ olabilir (cube bulundu, ölçü belirsiz). `next_steps`/
        # `suggestions` chip'leri o kısmı zaten taşıyor — oradan okunur, YENİDEN
        # hesaplanmaz. *Sorduğunu hatırlamak, sorarken bildiğini de hatırlamaktır.*
        kismi = resp.cube_query
        if kismi is None:
            for ns in (resp.next_steps or []):
                aday = getattr(ns, "cube_query", None)
                if isinstance(aday, dict) and (aday.get("cube") or aday.get("measures")):
                    kismi = aday
                    break
        # 🔴 `B9` — odak varlık. Kararı `diyalog.odak_belirle` verir (tek sahip);
        # burada yalnız **hammadde** toplanır: cevabın sorgusu, satırları ve planı.
        from app.diyalog import odak_belirle

        _satirlar = ((resp.result or {}).get("rows")
                     if isinstance(resp.result, dict) else None)
        if _satirlar is None:
            _satirlar = getattr(getattr(resp, "result", None), "rows", None)
        _plan = resp.plan if isinstance(getattr(resp, "plan", None), dict) else None
        resp.diyalog_durumu = durum(resp.cube_query, sorulan=sorulan, onceki=onceki,
                                    kismi_cq=kismi,
                                    odak=odak_belirle(resp.cube_query, _satirlar, _plan))
    except Exception:                                      # noqa: BLE001 — best-effort
        _log.warning("diyalog durumu kurulamadı (cevap etkilenmez)", exc_info=True)


def _adhoc_kayit(request: Request, cq: dict | None) -> dict | None:
    """Ad-hoc cube kaydı (FAZ 1 / K1) — yoksa None. `ask.py::_adhoc_store` ile AYNI depo;
    burada import döngüsü olmasın diye `app.state`'ten doğrudan okunur."""
    if not isinstance(cq, dict) or not cq.get("adhoc"):
        return None
    return (getattr(request.app.state, "adhoc_cubes", None) or {}).get(
        str(cq.get("adhoc_id") or ""))


def _bicim_kotasi(soru: str | None, sema: dict | None) -> tuple[dict[str, int], str] | None:
    """`§D3` — sorudan **öneri kovası kotası**. Çözülemezse `None` (bugünkü davranış).

    🔴 **ŞEMALI okuma zorunludur — ve bunu makbuz yakaladı.** İlk yazımda şemasız
    `coz_soru()` çağırdım; curl'de `niyet:` izi *«tür=kirilim»* derken `§D3` makbuzu
    *«toplam»* dedi. Sebep: `kirilim`/`ustunluk` gibi türler **katalog eşleşmesiyle**
    doğar (`coz`), sorunun salt dilinden değil (`coz_soru`). Sonuç: *«hangi müşteri
    riskli»* — 8 satırlık bir **kırılım** — tek-sayı kotası alıyordu.
    ⊙ İki okuma yan yana basılmasaydı bu ayrışma **görünmezdi**; makbuz burada bir
    süs değil bir **kapı** oldu.

    ⚠ `niyet.coz` istek kapsamında **belleklidir** (anahtar `tam:{soru}`) — aynı turda
    `route()`/`uyum` zaten çözmüştür, yani ikinci bir çözümleme maliyeti yoktur.
    *Bir kararı ikinci kez hesaplamak, iki karar riski demektir.*
    """
    if not soru or not sema:
        return None
    try:
        from app.bicim import oneri_kotasi
        from app.niyet import coz

        return oneri_kotasi(coz(soru, sema).turler)
    except Exception:  # noqa: BLE001 - best-effort (şerit düşmez, eskiye döner)
        _log.warning("§D3: biçim kotası çözülemedi (best-effort)", exc_info=True)
        return None


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
            _sema = adhoc["schema"]
        else:
            _sema = wren_for_request(request).schema()
        cubes = _sema.get("cubes") or []
        index = {c.get("name"): c for c in cubes}
        # 🔴 `§D3` — ÖNERİ ŞERİDİ ARTIK SORU TÜRÜNE BAĞLI. Ölçüldü (§18'in sekiz
        # sorusu, 2026-08-11): chip dizisi `6,6,6,6,5,6,6,5` — soru ne olursa olsun
        # aynı boyda şerit, §18.1'in *"katalog hissinin birinci kaynağı"* dediği şey.
        # Karar tablosu ve gerekçeleri `app/bicim.py`'de; burada yalnız **tüketilir**.
        _kota = _gerekce = None
        if "bicim_karari" in resolve_for(get_settings(), principal):
            if (_karar := _bicim_kotasi(resp.question, _sema)):
                _kota, _gerekce = _karar
        adimlar = cube_router.suggest_next_steps(cq, index, _kota)
        if _gerekce:
            # Makbuz: kararı **gerekçesiyle** görünür kıl (`§98.1` disiplini — elenen
            # bir şey sessizce elenmez).
            resp.trace = [*(resp.trace or []), f"§D3 biçim: {_gerekce}"]
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
    from app.result_shape import belirlenimli_sirala as _belirlenimli_sirala

    if is_new_topic is not None:
        resp.is_new_topic = is_new_topic
    if thread_id is not None:
        resp.thread_id = thread_id
    if reply_to_label is not None:
        resp.reply_to_label = reply_to_label

    # 🔴 `§SB` — belirlenimli sıra. Karar ve yüklem `result_shape.belirlenimli_sirala`'da
    # (tek sahip); burada yalnız çağrı. ⚠ **Yorumdan ÖNCE**: `interpret()` *«en yüksek»*
    # gibi olguları satır sırasından okuyor ve sonradan sıralamak, yorumun okuduğu
    # tabloyu altından çekerdi. *Bir sırayı, ona bakan gözden sonra düzeltmek, düzeltmek
    # değildir.*
    if _belirlenimli_sirala(resp):
        resp.trace = [*(resp.trace or []), "§SB: sırasız kırılım belirlenimli sıraya "
                                           "kondu (ölçüye göre azalan)"]
    # Sıra ÖNEMLİ: öneriler yorumun signal'larına bağımlı; explain ikisini de okur.
    _maybe_interpret(request, resp)
    _temellendir(request, resp)
    _diyalog_durumu(resp, log_body)
    _attach_next_steps(request, resp)
    _attach_recommendations(request, resp)
    resp.explain = _build_explain(resp)
    # 🔴 `G6.11` — **ŞEMA GARANTİSİ SAĞLAYICIYA BAĞLI ve bu MAKBUZA YAZILIR.**
    #
    # `llm_sema_kisitli` yalnız Anthropic'te gerçektir (`llm.py`'nin kendi beyanı:
    # `sema_kullanir`). Failover ikinci sağlayıcıya düştüğünde Intent-JSON **serbest
    # JSON** olarak üretilir — `parse_cube_query` hâlâ reddeder, yani cevap yanlış olmaz,
    # ama *"model geçersiz bir ad ÜRETEMEZ"* garantisi **yoktur**.
    #
    # ⚠ Kanal bilerek `assumptions`: o liste zaten *"sessiz bir varsayım yapıldı"*
    # demektir ve dolduğunda güveni **bir kademe düşürür**. İkinci bir alan açmak,
    # kullanıcıya iki farklı güven anlatısı vermek olurdu.
    #
    # *Bir garantinin koşullu olduğunu bilip söylememek, garantiyi vermekten kötüdür:
    # ilki bir sınır, ikincisi bir yanlış beyandır.*
    try:
        if resp.source == "cube+llm" and resp.explain is not None:
            from app.config import get_settings as _gs3
            from app.features import resolve_for as _rf3

            _llm = getattr(getattr(request, "app", None), "state", None)
            _llm = getattr(_llm, "llm", None)
            if (_llm is not None and not getattr(_llm, "sema_kullanir", True)
                    and "llm_sema_kisitli" in _rf3(
                        _gs3(), getattr(getattr(request, "state", None), "principal", None))):
                resp.explain.assumptions.append(
                    "Şema-kısıtlı çıktı istendi ama etkin sağlayıcı onu desteklemiyor "
                    "(failover) — ad doğrulaması yine yapıldı, ama model geçersiz bir ad "
                    "ÜRETEMEZ garantisi bu yanıtta yok.")
    except Exception:                                  # noqa: BLE001 — makbuz cevabı düşürmez
        _log.warning("şema garantisi makbuza yazılamadı", exc_info=True)

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
    # 🔴 **AI ACT Md.50 — İŞARET, METNİN VARLIĞINA DEĞİL KAYNAĞINA BAKAR.**
    #
    # Eski hesap yalnız `narration`'ın **var olup olmadığına** bakıyordu. T2'nin şablon
    # basamağı inince bu **yanlış beyana** dönüştü: `interpret()`'in kendi olgu
    # metinlerinden kurulmuş, tek bir sağlayıcı çağrısı görmemiş bir cümle *"yapay zekâ
    # tarafından yazılmıştır"* diye işaretlenirdi.
    #
    # ⚠ Fazla işaretlemek de bir yanlış beyandır: kullanıcı deterministik bir cümleye
    # LLM'e duyduğu şüpheyle bakar, ve işaretin **ayırt edici gücü** kaybolur — her şey
    # işaretliyse hiçbir şey işaretli değildir.
    #
    # *Bir uyarıyı hak etmeyen yere koymak, hak ettiği yerde okunmamasına yol açar.*
    # 🔴 **KONTROL KARAKTERİ — canlı bulgu (§16.3).** İstemci tarafında:
    #     JSONDecodeError: Invalid control character at: line 1 column 415
    # Kullanıcıya görünen bir metin alanına ham bir C0 karakteri (ör. `\x0b`, `\x1f`)
    # sızdığında **katı** bir JSON çözücü (curl | jq, ön yüz) yanıtın **tamamını** düşürür
    # ve kullanıcı bunu *"sunucu hatası"* diye görür — oysa cevap doğruydu.
    #
    # ⚠ Kaynağı aramak yerine **çıkışta** temizleniyor ve bu bilinçli: metin üç ayrı
    # üreticiden gelebiliyor (katalog · LLM · şablon) ve üçünde ayrı ayrı temizlemek,
    # bir gün ikisinde temizlemek demekti. *Bir çıkışı korumanın yeri, çıkıştır.*
    #
    # 🔴 `\n` ve `\t` **korunur**: onlar biçimdir, gürültü değil — ve JSON onları zaten
    # kaçırır. Silinen yalnız çözücüyü kıran, hiçbir anlam taşımayan C0 artıklarıdır.
    for _alan in ("note", "soz"):
        _deger = getattr(resp, _alan, None)
        if isinstance(_deger, str) and any(ch < " " and ch not in "\n\t" for ch in _deger):
            setattr(resp, _alan, "".join(
                ch for ch in _deger if ch >= " " or ch in "\n\t"))
            _log.warning("çıkışta kontrol karakteri temizlendi (alan=%s)", _alan)

    _yorum = resp.interpretation or {}
    resp.ai_generated_prose = bool(_yorum.get("narration")) and \
        _yorum.get("narration_kaynak") != "sablon"
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
