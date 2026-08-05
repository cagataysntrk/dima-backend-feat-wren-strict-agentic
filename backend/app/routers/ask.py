"""Natural-language → SQL → result endpoint (the demo's headline flow)."""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

import time as _time

from app import context as app_context
from app import prescribe
from app import planner as _planner
from app import ask_jobs, cekirdek, followup, katman_b, typo_onerisi
from app import soz as _soz
from app import cube_router, eylem, pii, tercih, viz, yoy
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
    NextStep,
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


def _adhoc_store(request: Request) -> dict:
    """`adhoc_id` → {service, schema, maskeli_kolonlar, kirpilmis} (in-memory, ephemeral).

    `_dataset_store`'dan **AYRI** olmak zorunda. Oraya yazılsaydı iki şey birden kırılırdı:
    (a) yüklenmiş bir Excel ezilirdi, (b) `_service_for` o oturumdaki SONRAKİ NORMAL
    soruları da ad-hoc tabloya yönlendirirdi — yani bir Discovery cevabı, tenant'ın gerçek
    kataloğunu oturum boyunca **gölgelerdi**. Ad-hoc servis YALNIZ `cube_query.adhoc`
    işaretini taşıyan bir düzenleme geldiğinde okunur.
    """
    store = getattr(request.app.state, "adhoc_cubes", None)
    if store is None:
        store = {}
        request.app.state.adhoc_cubes = store
    return store


def _adhoc_service_for(request: Request, cq: dict | None):
    """`cube_query` ad-hoc ise onun servisini döner; değilse None (çağıran normal yola gider)."""
    if not isinstance(cq, dict) or not cq.get("adhoc"):
        return None
    kayit = _adhoc_store(request).get(str(cq.get("adhoc_id") or ""))
    return kayit["service"] if kayit else None


def _adhoc_kur(request: Request, body, result: dict | None, sql: str,
               limit: int | None) -> dict | None:
    """Discovery sonucundan ad-hoc cube (FAZ 1 / K1). Kurulamazsa **None** — bugünkü davranış.

    Planın dört risk maddesi burada uygulanır:

    * **KILL-SWITCH** — `adhoc_cube` bayrağı kapalıyken hiç çalışmaz (KURAL B).
    * **KIRPMA** — `row_count == limit` ise sonuç tavana DEĞMİŞ olabilir; o görünüm
      üzerinde `SUM`/`AVG`/`TOP-N` kendinden emin ama yanlış cevap verir. İşaretlenir
      (`kirpilmis`) ve toplama chip'leri `answer.py`'de SUNULMAZ.
    * **MASKELEME SIRASI** — cube MASKELİ satırlardan kurulur (aksi halde oturum `.duckdb`
      dosyası diskte maskesiz PII taşırdı). Bedeli, maskelenen kolonda filtre chip'inin
      BOŞ dönmesidir; o kolonlar işaretlenir ve chip üretilmez.
    * **DONDURULMUŞLUK** — `adhoc_cube.turet()` satırları materyalize eder; sonraki
      sorgular kaynak DB'ye geri gitmez (testle ölçülür, iddia edilmez).
    """
    if not result or not (result.get("rows") or []):
        return None
    from app.features import resolve_for

    settings = get_settings()
    principal = getattr(request.state, "principal", None)
    if "adhoc_cube" not in resolve_for(settings, principal):
        return None

    from app import adhoc_cube as _adhoc
    from app.answer import _UPLOAD_DIR
    from app.pii import mask_rows

    # MASKELEME ÖNCE: hangi kolonlar maskelendi? (`mask_rows` içerik-tabanlıdır — kolon
    # meta'sı değil hücre değeri taranır, o yüzden fark ALINARAK bulunur.)
    ham = list(result.get("rows") or [])
    maskeli, bulundu = mask_rows(ham)
    maskeli_kolonlar: set[str] = set()
    if bulundu:
        for h, m in zip(ham, maskeli):
            maskeli_kolonlar.update(k for k, v in h.items() if m.get(k) != v)

    sid = re.sub(r"[^A-Za-z0-9_-]", "_", str(body.session_id or "anon"))[:80]
    adhoc_id = f"{sid}-{abs(hash(sql)) % (10 ** 10)}"
    kirpilmis = bool(limit) and int(result.get("row_count") or 0) >= int(limit)
    try:
        kurulan = _adhoc.turet(
            {**result, "rows": maskeli if bulundu else ham},
            _UPLOAD_DIR / "adhoc" / adhoc_id,
            cube_adi="adhoc", etiket="geçici model",
            kirpilmis=kirpilmis, maskeli_kolonlar=frozenset(maskeli_kolonlar))
    except Exception:  # noqa: BLE001 — yapı VAAT ETMEMEK, 500 atmaktan iyidir
        _log.warning("ad-hoc cube kurulamadı (best-effort)", exc_info=True)
        return None
    if not kurulan:
        return None
    kurulan["cube_query"]["adhoc_id"] = adhoc_id
    _adhoc_store(request)[adhoc_id] = kurulan
    return kurulan


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


def _prompt_enhance_dene(request, ham_soru: str, q_norm: str, schema: dict, principal,
                         *, liste: bool) -> tuple[dict | None, str | None]:
    """`route()` boş dönünce soruyu katalog terimleriyle yeniden yazıp TEKRAR dener.

    Döner: `(route_hit | None, iz_metni | None)`. Hiçbir koşulda istisna sızdırmaz —
    enhancer bir **kurtarma** yoludur; kendisi patlarsa cevap bugünkü haliyle döner
    (gerileme YOK).

    **LLM YAPI SEÇMEZ.** Çıktı bir METİNDİR ve `route()` ona sıfırdan karar verir; model
    uydurma bir terim üretse bile `route()` onu yine reddeder. Hata yüzeyi bu yüzden
    yapısal olarak dardır — enhancer en kötü ihtimalle *işe yaramaz*, yanlış cevap
    üretemez.
    """
    llm = getattr(request.app.state, "llm", None)
    if llm is None or not hasattr(llm, "prompt_enhance"):
        return None, None                  # kural-tabanlı sağlayıcı: YOL KAPALI, hata değil
    try:
        from app import planner as _planner

        service = _service_for(request, None)
        catalog_text, _idx = cube_router.build_catalog(schema)
        plan = _planner.Planlayici(
            principal=principal,
            butce=_planner.Butce(adim=3, saniye=10.0, sorgu=0),
            kaynaklar={"servis:llm": llm, "servis:wren": service},
        )
        # DETERMİNİSTİK-ÖNCE kapısı: `route` PLANLAYICI ÜZERİNDEN denenmiş olmalı.
        # Yukarıda zaten çağrıldı ve None döndü; burada aynı çağrıyı planlayıcıya da
        # yaptırmak kapıyı GERÇEKTEN geçirmek içindir — "denendi" demek yetmez, kapı
        # kendi kaydını görmelidir (aksi halde kapı bir yorumdan ibaret kalırdı).
        if plan.calistir("route", ham_soru, schema) is not None:
            return None, None              # ikinci deneme çözdüyse enhancer gereksiz
        yeni_metin = plan.calistir("llm.prompt_enhance", ham_soru, catalog_text)
    except Exception as exc:  # noqa: BLE001 — bütçe/yetki reddi dahil: sessizce geç
        _log.info("prompt-enhancer atlandı: %s", exc)
        return None, None

    yeni_metin = (yeni_metin or "").strip().strip('"').splitlines()[0].strip()
    if not yeni_metin or cube_router._norm(yeni_metin) == q_norm:
        return None, None                  # değişmedi → yeni bilgi yok
    try:
        hit = cube_router.route(yeni_metin, schema, liste_kirilimi=liste)
    except Exception:
        _log.warning("enhancer sonrası route() hata verdi (best-effort)", exc_info=True)
        return None, None
    if not hit:
        return None, None                  # iyileştirilmiş metin de çözülemedi → bugünkü yol
    # MAKBUZ İZİ (planın 2. şartı): kanonik soru SESSİZCE kullanılır ama KAYIT DIŞI
    # kalmaz — denetçi hangi metnin çözüldüğünü görebilmeli.
    hit["cube_query"]["provenance_soru"] = {
        "question_original": ham_soru, "question_normalized": yeni_metin}
    return hit, f"soru yeniden yazıldı ({ham_soru!r} → {yeni_metin!r})"


def _capraz_alan_pilotu(request, body, q_norm: str, schema: dict, principal,
                        migration_trace: list[str]):
    """FAZ 4 — planlayıcı ÖNERİR, dört kapı DENETLER, makbuz KOŞUMU kaydeder.

    Döner: `AskResponse | None`. `None` = pilot bir şey üretemedi → **bugünkü davranış**
    (Discovery) aynen devam eder. Gerileme yok.

    ## Ne yapar

    1. `sec()` planı **önerir** (LLM yoksa deterministik yedek: `["route"]`).
    2. Her adım `calistir()`'den geçer — **kayıt · yetki · deterministik-önce · bütçe**.
    3. Bir adım cevap üretirse o cevap döner ve **`agent_run` makbuzu** ona iliştirilir:
       hangi araçlar, hangi sırayla, kaç ms, hangi adım hata verdi.

    ## Neden makbuz zorunlu

    Planlayıcı bir cevabı **nasıl** ürettiğini söyleyemezse, "LLM garson oldu" bir beyan
    olarak kalır. `Kosum.makbuza()` bunu **yapısal** kılar: `steps` · `step_count` ·
    `query_count` · `truncated`. Bütçe aşımı da **sessizce kesilmez** — kısmi cevap ve
    kısılma gerekçesi birlikte döner.
    """
    from app import planner as _planner

    llm = getattr(request.app.state, "llm", None)
    service = _service_for(request, body.session_id)
    plan = _planner.Planlayici(
        principal=principal,
        butce=_planner.Butce(adim=6, saniye=20.0, sorgu=8),   # planın verdiği tavan
        kaynaklar={"servis:wren": service, "servis:llm": llm},
    )
    try:
        adimlar = plan.sec(body.question, llm)
    except Exception:  # noqa: BLE001 — seçim bir kurtarma yolu; patlarsa Discovery devam
        _log.info("çapraz-alan pilotu: plan seçilemedi", exc_info=True)
        return None

    # ÇAPRAZ-ALAN ADIMI PLANA EKLENİR. `sec()` LLM yoksa yalnız `["route"]` döner ve o
    # hâlde pilot `route()`'un zaten yaptığını TEKRARLARDI — hiçbir kazanç üretmezdi.
    # `cross_cube_add` DETERMİNİSTİKTİR: LLM olsun olmasın denenmeli.
    if not any(a["arac"] == "cross_cube_add" for a in adimlar):
        adimlar = list(adimlar) + [{"arac": "cross_cube_add",
                                    "neden": "çapraz-alan kompozisyonu (deterministik)"}]

    sonuc = None
    for adim in adimlar:
        ad = adim.get("arac")
        try:
            if ad == "route":
                # BREAK YOK — bu, pilotun ASIL noktası. `route` bir TABAN üretir ve
                # kompozisyon adımı o tabanı genişletir. İlk sürüm burada `break`
                # ediyordu, dolayısıyla `cross_cube_add`'e HİÇ ULAŞILMIYORDU: pilot
                # `route()`'un zaten yaptığını tekrarlayıp duruyordu — Faz 4'ün kazancının
                # "yok" olmasının ikinci sebebi buydu (birincisi aracın hiç çağrılmaması).
                sonuc = plan.calistir("route", body.question, schema) or sonuc
            elif ad == "llm.select_cube" and not sonuc:
                catalog_text, index = cube_router.build_catalog(schema)
                ham = plan.calistir("llm.select_cube", body.question, catalog_text)
                cq = cube_router.parse_cube_query(ham, index)
                if cq:
                    sonuc = {"cube_query": cq, "order": None, "limit": None}
                    break
            elif ad == "cross_cube_add" and sonuc:
                # ÇAPRAZ-ALAN KOMPOZİSYONU — planın somut pilotu ve fazın ASIL kazancı.
                # MIMARI §9.2'nin yapısal sınırı: bir cube'un ölçüsü + BAŞKA cube'un
                # boyutu **tek** CubeQuery'de ifade edilemez. İki adımda edilebilir:
                # `route` bir taban üretir, bu araç öteki cube'un ölçüsünü `blend` olarak
                # katar. **Deterministik** — LLM gerekmiyor, yalnız SIRA gerekiyordu.
                #
                # ⚠️ DENETİMDE BULUNDU: pilotun ilk sürümü yalnız `route` ve
                # `llm.select_cube` deniyordu; `blend` HİÇ çağrılmıyordu. Yani Faz 4'ün
                # kabul ölçütü (*"Discovery yerine 2 adımlı kompozisyon"*) karşılanmamış,
                # pilot yalnız "planlayıcı çalışıyor"u kanıtlıyordu — `route()`'a EK bir
                # şey getirmiyordu. Kazanç belirsiz değildi, **YOKTU**.
                genis = plan.calistir("cross_cube_add", sonuc["cube_query"],
                                      q_norm, schema)
                if genis:
                    sonuc = {"cube_query": genis, "order": None, "limit": None}
                    break
            # Kalan araçlar bu pilotta ÇAĞRILMAZ: `sec()` onları önerebilir ve öneri
            # makbuzda görünür, ama cevabı ÜRETEN yalnız yukarıdaki basamaklardır.
        except (_planner.AracReddi, _planner.ButceAsimi, KeyError) as red:
            # Kapılar ÇALIŞTI. Bu bir hata değil, sistemin doğru davranışı — ve
            # `calistir()` adımı zaten kayda geçirdi (hata alanıyla birlikte).
            _log.info("çapraz-alan pilotu: adım reddedildi (%s): %s", ad, red)
            continue
        except Exception:  # noqa: BLE001
            _log.warning("çapraz-alan pilotu: adım patladı (%s)", ad, exc_info=True)
            continue

    if not sonuc:
        return None                      # pilot bir şey üretemedi → Discovery devam

    iz = migration_trace + [
        "Ajan: plan seçildi → " + " → ".join(a["arac"] for a in adimlar),
        "Ajan: her adım dört kapıdan geçti (kayıt · yetki · deterministik-önce · bütçe)",
    ]
    resp = _answer_from_cube_query(sonuc["cube_query"], source="cube", trace=iz)
    if resp is not None:
        # MAKBUZ: koşumun kendisi cevabın YANINDA taşınır — "hangi araçlar, hangi sırayla,
        # kaç ms, hangi adım reddedildi" sorusu cevaplanabilir olsun. Reddedilen adımlar
        # da kayıttadır: bütçe tüketildi ve denetçi neyin DENENDİĞİNİ görmeli.
        try:
            resp.agent_run = (plan.kosum.makbuza() or {}).get("agent_run")
        except Exception:  # noqa: BLE001 — makbuz cevabı düşürmez
            _log.warning("agent_run makbuzu iliştirilemedi", exc_info=True)
    return resp


def _vqr_olcu_tutarli(q_norm: str, cached: dict, schema: dict) -> bool:
    """Benzerlik eşleşmesinin ÖLÇÜSÜ, sorunun kendi ölçüsüyle tutarlı mı?

    **Canlı turda ölçülen vaka:** *"geçen ay toplam FİRE"* → kayıt *"geçen ay toplam
    CİRO"* → `SELECT SUM(ciro_tl)`, `confidence=0.95`. Beş token'ın dördü eşleştiği için
    kosinüs 0,92'yi aştı; farklı olan **tek** kelime ise **ölçünün kendisiydi**.

    Bu yüzden kapı **eşik değil SEMANTİK**: eşiği yükseltmek yanlış çözümdü — sorun
    benzerliğin ne kadar YÜKSEK olduğu değil, **hangi kelimede** olduğu.

    Kural: soru bir ölçüyü **açıkça adlandırıyorsa**, kaydın `cube_query`'si de **o
    ölçüyü** taşımalı. Soru ölçü adlandırmıyorsa (ör. *"geçen ayki durum"*) kapı
    **karışmaz** — orada tutarsızlık iddia edilemez ve fazla dar bir kapı, kapsamı
    gerekçesiz keserdi.
    """
    cq = (cached or {}).get("cube_query") or {}
    kayit_olculeri = {m for m in (cq.get("measures") or []) if isinstance(m, str)}
    if not kayit_olculeri:
        return True                       # ham SQL kaydı — ölçü iddiası yok, karışma
    cube_meta = next((c for c in (schema.get("cubes") or [])
                      if c.get("name") == cq.get("cube")), None)
    if cube_meta is None:
        return True                       # şema değişmiş; başka kapı (sürüm) ilgilenir
    sorunun_olcusu, _syn = cube_router._match_measure(q_norm, cube_meta)
    if sorunun_olcusu is None:
        return True                       # soru ölçü ADLANDIRMIYOR → tutarsızlık iddia edilemez
    return sorunun_olcusu in kayit_olculeri


def _dogrulanmis_chipler(labels, schema, *, en_fazla: int) -> list[Suggestion]:
    """Etiketleri chip'e çevirir — ama **yalnız `route()`'un çözebildiklerini**.

    ## Neden (Faz 9.2, denetimde bulundu)

    `olcu_netlestirme` (2a-2) chip sorgusunu `route()` ile **doğruluyor** ve gerekçesi
    ölçülmüştü: `display` bir **insan etiketidir** (`mizan`'ınki *"mizan (hesap
    bakiyeleri)"*), sorgu kelimesi değil — o turda **39 chip kırıktı**.

    Ama **kardeş netleştirme dalları** (`cube_only_match` · `partial_unknowns` ·
    daraltma · katalog örnekleri · beraberlik) hâlâ `Suggestion(label=lb, query=lb)`
    üretiyordu: aynı kural bir dalda uygulanıyor, kardeşinde uygulanmıyor —
    deponun kendi *"kimlik asimetrisi"* sınıfı (MIMARI §6.1h), üçüncü kez.

    **Tıklanınca hiçbir yere varmayan bir chip, kullanıcıyı aynı duvara ikinci kez
    çarptırır ve chip olmamasından KÖTÜDÜR.** Bu yüzden kullanışsız etiket **düşürülür**;
    kaç tanesinin düştüğü **loglanır** (sessiz kırpma yok).

    ## ⚠️ ÖLÇÜT DÜZELTİLDİ — ilk sürüm çalışan chip'leri kesiyordu

    İlk hâl `route()`'u tek ölçüt aldı. Ölçüm bunu **çürüttü**: katalogdan türeyen 85
    etiketin **hepsi** bir yere varıyor (2 doğrudan cevap · 83 daraltan chip · **0 çıkmaz
    sokak**). `route()`=`None` olan *"sürdürülebilirlik"* bile *"hangi ölçüyü istiyorsun?"*
    + 6 çalışan chip döndürüyor — **duvar değil huni**. Üç golden test bu gerilemeyi yakaladı.

    Denetim raporunun 9.2 öncülü (*"bu beş dal kırık chip üretiyor"*) böylece **ölçülerek
    reddedildi** — 2a-1'in `elektrik` kararıyla aynı disiplin. Kapı yine de KALIYOR, çünkü
    ölçüt artık doğru şeyi ölçüyor: **sentezlenmiş** bir sorgu (2a-2'nin 39 kırık chip'i
    gibi) hâlâ elenebilir. Ayrıntı: `cube_router.chip_kullanisli_mi`.
    """
    tutulan: list[Suggestion] = []
    dusen: list[str] = []
    for lb in labels:
        etiket = str(lb).strip()
        if not etiket:
            continue
        # ⚠️ `route()` DOĞRUDAN çağrılmaz: her çağrı `reddi_sifirla()` yapar ve kullanıcının
        # gerçek red kodunu EZER (ölçüldü: R4 → R1; `answer.py:198` onu yazacaktı). Sonda
        # yalıtımı `chip_kullanisli_mi`'nin İÇİNDE — burada tekrarlanmaz ki unutulamasın.
        #
        # Ölçüt `route()` DEĞİL: bu daldaki etiketler KATALOGDAN gelir ve ölçüldü ki
        # route'suz olanlar bile bir yere varıyor (huni). Ayrıntı: `chip_kullanisli_mi`.
        if cube_router.chip_kullanisli_mi(etiket, schema):
            tutulan.append(Suggestion(label=etiket, query=etiket))
        else:
            dusen.append(etiket)
        if len(tutulan) >= en_fazla:
            break
    if dusen:
        _log.info("netleştirme: %d chip ÇÖZÜLMEDİĞİ için düşürüldü: %s",
                  len(dusen), dusen[:8])
    return tutulan


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
#
# ⟳ FAZ D1 — SELAMLAŞMA BU LİSTEDEN ÇIKARILDI. `merhaba`/`selam`/`naber`/`napiyorsun`
# burada **tesadüfen** duruyordu ve yalnız onlar çalışıyordu; `teşekkürler`·`sağol`·
# `günaydın`·`görüşürüz`·`tamam`·`ok`… **SQL üretiyordu** (ölçüldü: 16 ifadenin 12'si).
# Doğru yer `_SOSYAL` sınıfıdır — liste BÜYÜMEDİ, **küçüldü**.
_META_HINTS = (
    "dima ne", "dima nedir", "ne yapabil", "neler yapab", "ne ise yar", "ne ise yara",
    "nasil kullan", "nasil calis", "sen kim", "kimsin", "sen nesin", "yardim",
    "ornek soru", "ne sorabil",
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

# --- SOSYAL SINIF (FAZ D1) --------------------------------------------------------
#
# Sözlüğün SAHİBİ `cube_router`'dır (`_SOSYAL_SINIFLAR` · `sosyal_edim` ·
# `_sosyal_hit_words`) — çünkü İKİ tüketicisi var ve aynı sözlüğü okumak zorundalar:
# burası (sosyal cevap) ve `route()`'un kapsam kapısı (sosyal sözcük = dolgu).
# Burada yalnız **cevabın metni** durur; sınıflandırma orada.
_SOSYAL_METIN = {
    "selam": "Merhaba! Verinle ilgili ne bakalım?",
    "tesekkur": "Rica ederim. Başka neye bakmak istersin?",
    "kapanis": "Görüşürüz! İstediğin zaman buradayım.",
}


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
#: Görünüm kelimelerini SÖKEN desen. Bir takip mesajı yalnız görünüm istiyorsa
#: (`"pasta grafik"`) geriye anlamlı kelime kalmaz; `"pasta grafik olarak müşteri
#: bazında"` gibi bir istek ise YAPISAL bir düzenlemedir ve normal zincire gitmelidir.
#: `_VIZ_MAP`'ten TÜRETİLİR — iki liste ayrışamaz.
_VIZ_TEMIZ_RE = None  # aşağıda _VIZ_MAP'ten kurulur

_VIZ_LABELS = {"chart": "grafik", "table": "tablo", "line": "çizgi grafik",
               "bar": "sütun grafik", "pie": "pasta grafik", "heatmap": "ısı haritası",
               "facet": "panelli görünüm"}


_VIZ_TEMIZ_RE = re.compile(
    "|".join(sorted((re.escape(k) for k, _ in _VIZ_MAP), key=len, reverse=True))
    + r"|\b(grafik|gorunum|olarak|ver|yap|goster|cevir|istiyorum|lutfen)\b")


def _viz_hint(q_norm: str) -> str | None:
    for k, v in _VIZ_MAP:
        if k in q_norm:
            return v
    # FAZ 2a-5 — LİSTE NİYETİ BİR GÖRÜNÜM NİYETİDİR. *"listele"* / *"dökümü"* / *"detay"*
    # diyen kullanıcı SATIRLARI görmek istiyor; deterministik grafik kararı (ADR-0024) o
    # sonuca `bar` diyor ve teknik olarak haklı — ama kullanıcının AÇIKÇA söylediği şey
    # bu değil. `view_hint` zaten bu iş için var ("grafik ver"in tersi yönü); burada
    # simetriği kuruluyor. ADR-0024 ihlal EDİLMİYOR: `viz` kararı deterministik kalıyor,
    # `view_hint` yalnız kullanıcının açık isteğini taşıyor ve FE'de üstüne biniyor.
    # `_VIZ_MAP`'ten SONRA bakılır: "dökümü PASTA grafik yap" derse pasta kazanır.
    if cube_router.liste_niyeti(q_norm):
        return "table"
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


def _select_consistent(llm, question: str, catalog: str, index: dict, k: int,
                       sema: dict | None = None):
    """CubeQuery SELF-CONSISTENCY (literatür #1 / ClarifyGPT deseni): k örnekleme →
    kanonik oylama. Uyuşma = hem doğruluk hem KALİBRE güven sinyali; uyuşmazlık
    tek eksendeyse o eksen chip'e dönüşür.

    `sema` (FAZ 3a): şema-kısıtlı çıktı. `None` = bugünkü serbest-JSON yolu, birebir.

    Döner: (kazanan|None, uyum_orani, uyusmazlik_ekseni|None, farklı_adaylar)."""
    import concurrent.futures as cf

    def one(_i):
        try:
            ham = llm.select_cube(question, catalog, sema) if sema is not None \
                else llm.select_cube(question, catalog)
            cq = cube_router.parse_cube_query(ham, index)
            # PLANIN §6 KAPISI: "whitelist reddi oranı ÖLÇÜLÜP DÜŞÜŞÜ doğrulanır."
            # Bugün bu red SESSİZDİ — LLM bir cevap üretti, `parse_cube_query` onu
            # düşürdü ve geriye hiçbir iz kalmadı. Şema-kısıtlı çıktının kazancı tam
            # olarak bu sayının düşmesidir; ölçülemezse doğrulanamaz.
            if cq is None:
                _log.info("intent: whitelist REDDİ (sema=%s) — ham=%.200s",
                          "acik" if sema is not None else "kapali", ham)
            return cq
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


def _intent_uyusmazlik_chipi(question: str, eksen: str, adaylar: list[dict],
                             schema: dict, uyum: float, k: int) -> AskResponse:
    """Self-consistency uyuşmazlığı → NETLEŞTİRME (Faz D4). Tahmin etmez, SORAR.

    `_select_consistent` k örneğin kanonik CubeQuery'leri üzerinde oy verir. Uyum 2/3'ün
    altındaysa kazanan yoktur — ama uyuşmazlık **tek bir eksende** ise (hepsi aynı cube'da
    ama farklı ölçüde, ya da aynı ölçüde farklı kırılımda) bu, cevaplanabilir bir sorudur.
    Faz 3.1'in cube-beraberlik chip'iyle aynı felsefe: **belirsizlik bir cevap değil, bir
    sorudur** (ADR-0008).

    Chip'ler `next_steps` üzerinden taşınır — YENİ BİR ALAN/PANEL AÇILMAZ (mimari kural H3).
    `next_steps` zaten tam `cube_query` taşıyan ve tıklanınca `/cube` ile **LLM'siz** koşan
    tek taşıyıcıdır; kullanıcının seçimi ikinci bir LLM turu doğurmaz.
    """
    cubes = {c.get("name"): c for c in (schema.get("cubes") or [])}

    def _etiket(cq: dict) -> str:
        cm = cubes.get(cq.get("cube")) or {}
        cad = cm.get("display") or cq.get("cube") or "?"
        if eksen == "cube":
            return cad
        if eksen == "measures":
            disp = cm.get("measure_synonyms_display") or {}
            return " + ".join(disp.get(m) or m for m in (cq.get("measures") or [])) or cad
        etiketler = cm.get("dimension_labels") or {}
        dims = cq.get("dimensions") or []
        return (" × ".join(etiketler.get(d) or d for d in dims)
                if dims else "kırılımsız (toplam)")

    gorulen: set[str] = set()
    adimlar: list[NextStep] = []
    for cq in adaylar:
        lb = _etiket(cq)
        if lb in gorulen:
            continue
        gorulen.add(lb)
        adimlar.append(NextStep(
            label=lb,
            kind={"dimensions": "dimension", "measures": "measure"}.get(eksen, "measure"),
            cube_query=cq,
        ))
    soru = {"cube": "Hangi konuyu kastettin?", "measures": "Hangi ölçüyü istiyorsun?",
            "dimensions": "Hangi kırılımı istiyorsun?"}.get(eksen, "Hangisini istiyorsun?")
    return AskResponse(
        question=question, source=None, note=soru,
        next_steps=adimlar,
        trace=[f"Intent-path: self-consistency uyuşmazlığı (%{uyum*100:.0f} uyum / {k} "
               f"örnek, eksen={eksen}) → netleştirme, tahmin YOK"],
    )


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
    # FAZ 9.2 — yükleme chip'leri de DOĞRULANIR, ama **veri setinin KENDİ şemasıyla**:
    # bu chip'ler tıklandığında `/ask` aynı `session_id` ile gelir ve `_service_for` tenant
    # servisini değil YÜKLENEN dataset'i seçer (`:71-78`). Tenant şemasıyla doğrulamak
    # hepsini gerekçesiz düşürürdü — doğrulama, chip'in GERÇEKTEN gideceği şemaya karşı
    # yapılmazsa bir kapı değil bir gürültü kaynağıdır.
    ham = []
    if dims and meas:
        ham.append(f"{dims[0]['orig']} bazında {meas[0]['orig']}")
    if meas:
        ham.append(f"toplam {meas[0]['orig']}")
    try:
        veri_semasi = svc.schema()
    except Exception:  # noqa: BLE001 — şema alınamıyorsa doğrulama İMKÂNSIZ, chip kesilmez
        _log.warning("/ask/upload: chip doğrulaması için şema alınamadı", exc_info=True)
        veri_semasi = None
    sug: list[Suggestion] = _dogrulanmis_chipler(ham, veri_semasi, en_fazla=2)
    # META chip: `route()`'a değil `_is_catalog_query` (`:579`) katalog yoluna gider —
    # doğrulama kapısı ona UYGULANMAZ, çünkü kapı yanlış mekanizmayı ölçerdi.
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
    # FAZ 1 (K1) — AD-HOC CUBE. Chip'in `cube_query`'si `adhoc: true` taşıyorsa hedef,
    # tenant kataloğu değil o Discovery cevabından türetilmiş DONDURULMUŞ oturum
    # görünümüdür. Tenant servisiyle çözmeye çalışmak "cube bulunamadı" (400) verirdi —
    # yani chip görünür ama tıklanınca çalışmaz olurdu; bu, chip'i hiç sunmamaktan kötüdür
    # (aynı kural: `olcu_netlestirme` / `ay_netlestirme`).
    _adhoc_svc = _adhoc_service_for(request, body.cube_query)
    service = _adhoc_svc or _service_for(request, body.session_id)
    schema = service.schema()

    _, index = cube_router.build_catalog(schema)
    if body.cube_query and body.cube_query.get("cube") and _adhoc_svc is None:
        # cube adı göçü (yeniden adlandırma sonrası eski adla gelen chip düzenlemesi).
        # Ad-hoc cube oturumla doğar/ölür — göç edecek bir geçmişi YOKTUR.
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
    # ⚠️ ROZET DÜRÜSTLÜĞÜ İKİNCİ TURDA DA GEÇERLİ OLMALI (denetimde ölçüldü).
    # `source="cube"` SABİTİ, ad-hoc bir cube üzerinde yapılan chip düzenlemesini de
    # deterministik gösteriyordu: `confidence=1.0`, path *"LLM'siz, sıfır maliyet"*,
    # frontend `◆ CUBE` + 🥇. Oysa veri hâlâ **incelenmemiş LLM SQL'inden** türetilmiş
    # DONDURULMUŞ bir görünümdür — MIMARI §6.2z'nin *"kullanıcı `◆ CUBE` görmez"* beyanı
    # tam olarak burada çürüyordu. Yapı taşınabilir, GÜVEN taşınamaz.
    _kaynak = "llm:adhoc" if (cq or {}).get("adhoc") else "cube"
    resp = AskResponse(
        question=body.label or "(chip düzenleme)",
        sql=sql,
        planned_sql=planned,
        result=QueryResult(**result),
        source=_kaynak,
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
            cube_query=cq,
            # Metadata argümanları TEK KAYNAKTAN (Faz I1). Elle toplamak bu dosyada
            # zaten bir kez `measure_units` yazım hatasına yol açmıştı; ikinci örnek
            # `semi_additive`in hiçbir çağıran tarafından geçirilmemesi oldu.
            **viz.meta_args(cmeta),
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

    # 🔴 FAZ 5.13b — **HER BLOK BİR MAKBUZ YAZAR, KAYNAK LİSTESİ ONU TAŞIR.**
    #
    # Yol haritasının şartı: *"PDF'e döküldüğünde bile `contract_id` altta kalır."*
    # Makbuz **maskelemeden SONRA** yazılır: rapora giren sonuç maskeliyse, kanıt da
    # maskelenmiş sonucun hash'i olmalı — aksi hâlde `result_hash` kullanıcının hiç
    # görmediği bir tabloyu damgalardı.
    #
    # ⚠ Makbuz yazılamazsa rapor **düşmez** (`contract_id: None` kalır ve kaynak
    # listesinde **öyle görünür**): kanıtın yokluğunu gizlemek, kanıtsızlıktan kötüdür.
    try:
        from app.contracts import ContractStore

        _store = ContractStore()
        _sv = str(schema.get("version") or "")
        for _page in rep.get("pages") or []:
            for _blk in _page:
                if not _blk.get("result"):
                    continue
                try:
                    _blk["contract_id"] = _store.record(
                        session_id=None,
                        question=str(_blk.get("title") or body.title or "Rapor"),
                        cube_query=_blk.get("cube_query"), sql=None,
                        result=_blk.get("result"), source="report",
                        schema_version=_sv,
                        tenant_id=str(getattr(principal, "tenant_id", "") or "") or None,
                    )
                except Exception:                            # noqa: BLE001, PERF203
                    _log.warning("rapor bloğu makbuzsuz kaldı", exc_info=True)
        # Yapı bloklardan SONRA yeniden hesaplanır ki kaynak listesi makbuzları görsün.
        rep.update(report_mod.yapi(
            {"title": body.title}, [b for pg in (rep.get("pages") or []) for b in pg]))
    except Exception:                                        # noqa: BLE001
        _log.warning("rapor yapısı üretilemedi (best-effort)", exc_info=True)
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
                # FAZ 1.12 (AI Act Md.14) — kullanıcı DURDURDUYSA sonuç YAYIMLANMAZ.
                # İptal işi öldürmez, sonucunu yayımlatmaz (gerekçe: app/ask_jobs.py):
                # yarım bir sonucu yayımlamamak, hızlı öldürmekten daha güvenlidir.
                if ask_jobs.yayimlanabilir_mi(j.status):
                    j.status = "completed"
                    j.result_json = resp.model_dump_json()
                j.finished_at = datetime.utcnow()
                s.add(j)
                s.commit()
        except Exception as exc:  # noqa: BLE001 - arka-plan işi ASLA sessizce kaybolmaz
            _log.warning("AskJob arka-plan çalıştırması başarısız", exc_info=True)
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                if ask_jobs.yayimlanabilir_mi(j.status):   # durduruldu → `failed` DEMEZ
                    j.status = "failed"
                j.error = str(exc)[:500]                   # tanı yine de yazılır
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

    # BAĞLAM ÇÖZÜMÜ (Faz G5) — sunucunun ARTIK bir bağlam modeli var. Bugüne kadar
    # `thread_id`/`reply_to_label` salt ECHO'ydu ve `is_new_topic` yalnız `not is_followup`
    # idi; yani hangi soru hangi bağlama ait, sunucu BİLMİYOR, istemciye güveniyordu.
    # `app/context.py` saf bir fonksiyondur (izole test edilebilir) ve her zaman bir
    # KURAL döndürür — bağlam sessizce kopmaz, koparsa gerekçesi makbuza yazılır.
    #
    # ✅ FAZ 0.5 — ÇAPA ZİNCİRİ BAĞLANDI. *(Bu yorum eskiden "reply_to_cube_query HENÜZ
    # istemciden gelmiyor; thread paneli Faz H4'te yeniden kurulacak" diyordu. Panel
    # 2026-08-01'de kuruldu ve istemci çapayı ZATEN biliyordu — onu genel `cube_query`
    # yuvasına DÜZLEŞTİRİYORDU, bu yüzden hep `KURAL_YAPISAL` çalışıyor, `KURAL_CAPA`
    # hiç ateşlenmiyordu. Bayat bir gerekçe kodda kilitli kalmasın diye güncellendi.)*
    #
    # Çapa listesi: **kullanıcının AÇIK eylemi** (bir karta yanıt / kart seçimi) —
    # istemcinin taşıdığı örtük duruma (`cube_query`) **baskın** gelir. Çok kart →
    # kesişim; farklı cube'lar → **SOR** (`KURAL_CELISKI`, ADR-0008: belirsizlikte tahmin
    # etme). Bayrak kapalıyken liste boş kalır → davranış **birebir bugünkü** (GERİ AL).
    _capalar: list[dict] = []
    if "capa_zinciri" in resolve_for(settings, principal):
        if body.reply_to_cube_query:
            _capalar.append(body.reply_to_cube_query)
        _capalar.extend(c for c in (body.reply_to_extra_cube_queries or []) if c)

    baglam = app_context.coz(
        cube_query=body.cube_query,
        prev_sql=prev_sql,
        history=body.history,
        capalar=_capalar,
        capa_etiketi=body.reply_to_label,
        atif=cube_router.atif_var(body.question),
    )

    # ATIF ÇÖZÜMÜ (FAZ E) — bağlamın ham ifadeden GERİ KAZANILMASI.
    #
    # Ölçülen kusur: yapısal bağlam yokken *"az önce dediğin gibi makine bazında ayır"*
    # `source=rule` ile **ham SQL üretiyordu** — kullanıcının işaret ettiği rapor değil,
    # uydurulmuş bir sorgu. `history` sunucuya geliyordu ama yalnız BOOLEAN olarak
    # okunuyordu (`prev_sql and history`); içeriğine hiç bakılmıyordu.
    #
    # Çözüm LLM DEĞİL, muhasebe: önceki turun metnini **deterministik `route()`** ile
    # yeniden çöz, çıkan sorguyu yapısal çapa yerine koy. Bundan sonrası zaten var olan
    # takip yoludur — ikinci bir cevap hattı YAZILMAZ (bu deponun bir numaralı kusur
    # sınıfı). `route()` çözemezse hiçbir şey uydurulmaz: bağlam olduğu gibi kalır.
    # ✅ FAZ 0.5 — ÇÖZÜLEN ÇAPA **UYGULANIR**. Kapı bunu yakaladı: `coz()` doğru kuralı
    # (`capa:karta-yanit`) üretiyordu ama takip zinciri hâlâ `body.cube_query`'yi okuyordu
    # → çapa **çözülüp yok sayılıyordu**. Tam olarak *"beyan var, kod onu tanımıyor"*
    # sınıfı; ve kullanıcı için sonucu şuydu: işaret ettiği karta yanıt verirken cevap
    # **başka bir raporun** bağlamına kayıyor, üstelik **sessizce**.
    #
    # `KURAL_CELISKI`'de ÇAPA UYGULANMAZ: `cube_query` `None`'dır ve aşağıdaki zincir
    # dürüst reddine düşer — ADR-0008'in *"belirsizlikte tahmin etme"* kuralı. Sessizce
    # birini seçmek, kullanıcının görmediği bir karar vermek olurdu.
    if baglam.kural in (app_context.KURAL_CAPA, app_context.KURAL_COKLU) and baglam.cube_query:
        body.cube_query = baglam.cube_query
        structural_followup = True
        raw_followup = False
        is_followup = True

    if baglam.kural == app_context.KURAL_ATIF and not body.cube_query:
        _temel = None
        try:
            _temel = cube_router.route(baglam.ham_ifade[-1], schema)
        except Exception:
            _log.warning("atıf çözümü: önceki turun route()'u başarısız (best-effort)",
                         exc_info=True)
        _temel_cq = (_temel or {}).get("cube_query")
        if _temel_cq:
            body.cube_query = _temel_cq
            structural_followup = True
            raw_followup = False
            is_followup = True
            baglam = app_context.coz(
                cube_query=_temel_cq, prev_sql=prev_sql, history=body.history,
                capa_etiketi=body.reply_to_label)
            _log.info("ATIF /ask: önceki tur %r → cube=%s (deterministik geri kazanım)",
                      baglam.ham_ifade[-1] if baglam.ham_ifade else "",
                      _temel_cq.get("cube"))

    _log.info("BAĞLAM /ask: kural=%s cube=%s eksen=%s", baglam.kural,
              (baglam.cube_query or {}).get("cube"), baglam.kullanilmis_eksenler)

    # İSTEK GELDİ (1 Ağustos 2026, kullanıcı talebi: "her girdiyi net şekilde loglayalım").
    # Kapsamlı görünürlük için TEK giriş noktası — soru+bağlam sinyalleri (LLM'e mi düşecek,
    # yapısal takip mi, hangi thread) `_finish()`'teki "cevap gönderildi" logunun eşi.
    _log.info("İSTEK /ask: q=%r session=%s thread=%s followup=%s(yapısal=%s ham=%s)",
              body.question, body.session_id, body.thread_id, is_followup,
              structural_followup, raw_followup)

    # KALICI SUNUM TERCİHİ okuyucu (FAZ E) — istek başına TEK DB okuması; tercih bir
    # kolaylıktır, cevabın önkoşulu değil (depo düşerse rapor yine gelmeli → boş sözlük).
    _tercih_onbellek: dict[str, dict[str, str]] = {}

    def _tercihlerim() -> dict[str, str]:
        if "v" not in _tercih_onbellek:
            _tercih_onbellek["v"] = {}
            try:
                from sqlmodel import Session

                from app.routers.tercihler import oku
                from control_plane.db import engine

                with Session(engine) as _s:
                    _tercih_onbellek["v"] = oku(_s, principal) if principal else {}
            except Exception:
                _log.warning("sunum tercihi okunamadı (best-effort)", exc_info=True)
        return _tercih_onbellek["v"]

    def _TERCIH_NOTU_GORUNUM(deger: str) -> str:  # noqa: N802
        return (f"“{tercih.etiketle(tercih.ANAHTAR_GORUNUM, deger)} göster” tercihiniz "
                "uygulandı (kaldırmak için: ayarlar › tercihler)")

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
                _kayit = _adhoc_store(request).get(str(cq.get("adhoc_id") or ""))
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
            resp.viz = viz.recommend(result, cube_query=cq, **viz.meta_args(cube_meta_for_viz))
            # 🔴 FAZ 5.12 — İÇGÖRÜ PAKETİ. **`resp.viz` DEĞİŞMEZ**: paket AYRI bir alanda
            # (`viz_paketi`) taşınır ve bayrak kapalıyken `None` kalır → tekil kart bugünkü
            # hâliyle görünür (V-5/E-3: **birebir eski davranış**).
            #
            # ⚠ `recommend`i iki kez çağırmak yerine paketin İLK üyesini `resp.viz` yapmak
            # daha "temiz" görünürdü — ama o an tekil dönüşün bayt-bayt aynılığı **bir
            # varsayıma** dönerdi. *Geriye uyumluluk, ikinci bir çağrının maliyetinden
            # ucuzdur.*
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

    def _record_contract(cq: dict | None, sql: str | None, result: dict | None,
                         source: str) -> str | None:
        """Gövde `app/answer.py::record_contract`'ta — TEK uygulama (Faz A4)."""
        return record_contract(request, service=service, session_id=body.session_id,
                               question=body.question, cube_query=cq, sql=sql,
                               result=result, source=source, baglam=baglam)

    def _plan_izi(plan) -> str:
        """Ajan koşusunun tek satırlık özeti — iz'de görünür, makbuzda ayrıntısı durur.

        Kısılma **görünür olmalıdır**: kapsamı daraltan her sınır kullanıcıya söylenir
        (`contribution`'ın `kirpilan_segment`'iyle aynı ilke). Kısılmayan bir koşumda da
        adım/sorgu sayısı yazılır — maliyet gizli kalmaz.
        """
        k = plan.kosum
        temel = f"Ajan koşusu: {len(k.adimlar)} adım · {k.sorgu_sayisi} sorgu"
        return f"{temel} · KISILDI ({k.kisilma_nedeni})" if k.kisildi else temel

    def _cevap_ustunde_konus(prev_cq: dict, cube_meta: dict | None, niyet,
                             migration_trace: list[str], session_id: str | None):
        """"Cevap üstünde konuşma" (Faz G1) — VAR OLAN araçları KOMPOZE eder.

        Burada yeni bir analiz motoru İCAT EDİLMEZ; F1'in araç kaydındaki yetenekler
        çağrılır. MIMARI §11.6: *"özellik = kompozisyon, endpoint değil."* Bu yüzden
        `/ask/konusma` diye bir uç AÇILMADI — cevap, cevabın kendi turunda gelir.

        Sözgelimi *"bu neden böyle?"*:  `contribution` (katkı) → tıklanır bulgular.
        *"normal mi?"*:                 `yoy` (dönemsel kıyas) → sinyal.
        *"ne yapmalıyız?"*:             katkı + öneri chip'leri.

        `None` dönerse çağıran normal zincire devam eder — gerileme YOK: kullanıcı en
        kötü ihtimalle bugünkü davranışı alır.
        """
        import app.contribution as _contrib

        tur = niyet.tur
        iz = migration_trace + [f"Takip: üçüncü sınıf → cevap üstünde konuşma ({tur}, LLM'siz)"]

        # FAZ F3 — KOMPOZİSYON PLANLAYICIDAN GEÇER. F2'nin yönetişimi (bütçe · yetki ·
        # deterministik-önce · adım makbuzu) yazıldı ama hiçbir yola BAĞLI DEĞİLDİ; bu,
        # bu turda altı kez ölçtüğüm "beyan var, tüketici yok" sınıfının aynısı olurdu.
        # Kullanıcının yetkisi planlayıcıya verilir: ajan onu AŞAMAZ.
        plan = _planner.Planlayici(
            principal=principal,
            butce=_planner.Butce(adim=6, saniye=20.0, sorgu=8),
            kaynaklar={"servis:wren": service},
        )

        # NEDEN / NE YAPMALI → katkı ayrıştırması. `/ask/contribution`'ın gövdesi
        # ÇAĞRILIR, kopyalanmaz (aynı kural iki yerde yaşamasın — bu depoda ölçülmüş
        # desen: drill↔schedules, interpret↔schedules, _uncovered↔_syn_hit).
        if tur in (followup.TUR_NEDEN, followup.TUR_NE_YAPMALI, followup.TUR_ISARET):
            recete_payload: dict | None = None
            try:
                # FAZ F3 — artık KAYITLI bir araç: dört kapıdan (kayıt · yetki ·
                # deterministik-önce · bütçe) geçer ve kendi adım makbuzunu üretir.
                # Önceki tur burada `dis_adim(..., gated: false)` diye İTİRAF ediyordu,
                # çünkü gövde `/ask/contribution` router'ının içindeydi ve kayda tek
                # araçmış gibi yazmak yalan olurdu. Gövde `app/contribution.py::arastir`'a
                # taşındı; itiraf artık gereksiz.
                ham = plan.calistir(
                    "contribution.report", service, schema, prev_cq,
                    mode="yoy", kind="segment",
                    kaydet=lambda baslik, acq, sql, res: _drill_record_contract(
                        request, service, session_id, baslik, acq, sql, res))
            except _planner.ButceAsimi:
                _log.info("konuşma: bütçe tavanı — katkı ayrıştırması yapılmadı")
                return None
            except Exception:
                _log.warning("konuşma: katkı ayrıştırması başarısız (best-effort)",
                             exc_info=True)
                return None
            katki = ContributionResponse(
                measure=ham.get("measure"), mode=ham.get("mode") or "yoy",
                kind=ham.get("kind") or "segment", note=ham.get("note"),
                taranmayan_boyut=ham.get("taranmayan_boyut") or 0,
                taranmayan_adlar=ham.get("taranmayan_adlar") or [],
                contract_ids=ham.get("contract_ids") or [],
                raporlar=[ContributionReport(**r) for r in (ham.get("raporlar") or [])],
                pvm_raporlar=[PvmReport(**_pvm_seleli(r))
                              for r in (ham.get("pvm_raporlar") or [])])
            adimlar: list[NextStep] = []
            for rapor in katki.raporlar:
                for b in rapor.bulgular[:3]:
                    adimlar.append(NextStep(label=b.label, kind="dimension",
                                            cube_query=b.cube_query))
            if not adimlar and not katki.note:
                return None
            # DÜRÜST RED birinci sınıf: ayrıştırma yapılamadıysa NEDENİ söylenir
            # (toplanamayan ölçü, dönem yok) — boş bir "bilmiyorum" değil.
            not_metni = katki.note or (
                "Değişimi en çok sürükleyen segmentler aşağıda — her biri tıklanınca "
                "tek başına açılır ve kendi kanıtını üretir.")
            # REÇETE (Faz G3) — YALNIZ "ne yapmalıyız?" sorulduğunda. "Neden böyle?"
            # bir AÇIKLAMA ister, reçete değil; ikisini karıştırmak kullanıcının
            # sormadığı bir tavsiyeyi cevabın yerine koymak olurdu.
            if tur == followup.TUR_NE_YAPMALI and katki.raporlar:
                ilk = katki.raporlar[0]
                dusuk_iyi = (katki.measure or "") in (
                    (cube_meta or {}).get("lower_is_better") or [])
                rec = prescribe.recete(ilk.model_dump(), lower_is_better=dusuk_iyi)
                iz.append(f"Reçete: {'dağınık → öneri YOK' if rec.dagitik else f'{len(rec.oneriler)} öneri'}")
                # Gerekçe cevabın kendisidir: dağınık değişimde ÖNERİ ÜRETİLMEZ ve
                # NEDEN üretilmediği söylenir (dürüst red, `contribution`ın
                # toplanabilirlik kapısıyla aynı disiplin).
                not_metni = rec.gerekce
                recete_payload = {
                    **rec.makbuza()["prescription"],
                    # UI'ın render edebilmesi için sorgular da taşınır (bulgu tıklanır
                    # olmalı — ürünün tezi her önerinin doğrulanabilir bir sorgu olması).
                    "options": [{**o.makbuza(), "cube_query": o.cube_query}
                                for o in rec.oneriler],
                    "measure": katki.measure,
                }
                if rec.oneriler:
                    adimlar = [NextStep(label=o.segment, kind="dimension",
                                        cube_query=o.cube_query) for o in rec.oneriler]
            # Bulgular CEVABIN GÖVDESİDİR — `next_steps` DEĞİL. `next_steps`e konulduğunda
            # UI onları "sonraki adım" başlığıyla gösteriyordu (ölçüldü) ve Δ tutarları,
            # % paylar, kırpma uyarısı kayboluyordu. `contribution` alanı zengin gövdeyi
            # taşır; `next_steps` yalnız GEZİNME için kalır (kullanıcı bir bulguyu tek
            # başına açmak isterse) — ikisi farklı şeydir ve UI'da farklı görünmelidir.
            return AskResponse(question=body.question, source=None, note=not_metni,
                               cube_query=prev_cq, next_steps=adimlar[:8],
                               trace=iz + [_plan_izi(plan)],
                               contribution=katki.model_dump(),
                               prescription=recete_payload)

        # NORMAL Mİ → dönemsel kıyas. Yeni bir "normallik" tanımı UYDURULMAZ: elimizdeki
        # tek nesnel zemin geçen dönemle kıyastır ve cevap onu böyle sunar.
        if tur == followup.TUR_NORMAL:
            time_dim = yoy.time_dim_of(schema, prev_cq.get("cube"))
            kiyas_cq = {**prev_cq, "compare": "yoy"}
            try:
                # KAYITLI araç → dört kapıdan geçer (kayıt · yetki · deterministik-önce ·
                # bütçe) ve adım makbuzu üretir.
                sonuc = plan.calistir("yoy.compute", service, prev_cq, "yoy", time_dim,
                                      limit=settings.max_result_rows)
            except _planner.ButceAsimi:
                _log.info("konuşma: bütçe tavanı — kısmi cevap")
                return None
            except Exception:
                _log.warning("konuşma: dönemsel kıyas başarısız (best-effort)", exc_info=True)
                return None
            if not (sonuc or {}).get("rows"):
                return None
            r = QueryResult(columns=sonuc.get("columns") or [],
                            rows=sonuc.get("rows") or [],
                            row_count=len(sonuc.get("rows") or []))
            return _attach_viz(AskResponse(
                question=body.question, source="cube", result=r, cube_query=kiyas_cq,
                note="Geçen dönemle kıyas — \"normal mi\" sorusunun nesnel zemini budur.",
                trace=iz + ["Kıyas: app/yoy.py (yeni dönem matematiği YAZILMADI)",
                            _plan_izi(plan)],
            ), sonuc, kiyas_cq)

        # ANLAT / ANALİZ ET → **ELDEKİ raporu AÇ**. Faz D2.
        #
        # ## Ölçülen ölü uç (3 Ağustos 2026), bir `oee` raporu üstünde
        #
        #     "bunu analiz et"     → *"«bunu» yerine «gunu» mi demek istedin?"*
        #     "değerlendir"        → *"«degerlendir» yerine «degree» mi?"*
        #     "yorumlar mısın" · "özetle" · "bu grafiği açıkla"
        #                          → *"Bu takip mesajını önceki raporla ilişkilendiremedim"*
        #
        # Altı ifadenin BEŞİ duvara çarpıyordu — `followup.py`'nin kendi docstring'inde
        # tarif edilen ölü uç, **bir tür eksik olduğu için** yaşamaya devam ediyordu.
        #
        # ## Bu dal neden YENİ SORGU YAZMAZ
        #
        # Sınıfın tanımı: *"YENİ CEVAP ÜRETMEZ, VAR OLANI AÇAR"*. `prev_cq` **aynen**
        # yeniden çalıştırılır (dolayısıyla `cube_query` DEĞİŞMEZ — sözleşme #1) ve
        # `seal()` zinciri `interpret()` olgularını, `t2_anlatici` açıksa guard'lı
        # anlatıyı, `next_steps` chip'lerini kendisi ekler. Yani bu dalın işi **cevabı
        # yeniden üretmek değil, konuşmayı doğru rapora ÇAPALAMAK**.
        #
        # Devam chip'leri konuşmayı KENDİ KENDİNE besler: kullanıcı "analiz et" dedikten
        # sonra "neden böyle?" · "normal mi?" · "ne yapmalıyız?" bir tık uzakta ve üçü de
        # ZATEN çalışan türler.
        if tur == followup.TUR_ANLAT:
            # ⚠️ `_answer_from_cube_query` KULLANILMAZ — o `_finish`'i KENDİ İÇİNDE
            # çağırır ve bu fonksiyonun çağıranı da `_finish(resp)` yapar. Ölçüldü:
            # **tek tur İKİ telemetri satırı** yazıyordu (çift mühür → çift audit, çift
            # PII maskesi, çift yorum). Kardeş dallar (`TUR_NORMAL`) MÜHÜRSÜZ bir
            # `AskResponse` döndürür; bu dal da o sözleşmeye uyar.
            try:
                _sql = service.cube_sql(prev_cq)
                service.dry_plan(_sql)
                _sonuc = service.query(_sql, limit=settings.max_result_rows) \
                    if body.execute else None
            except Exception:
                _log.warning("anlat: rapor yeniden çalıştırılamadı (best-effort)",
                             exc_info=True)
                return None
            resp = _attach_viz(AskResponse(
                question=body.question, source="cube", sql=_sql,
                result=QueryResult(**_sonuc) if _sonuc else None,
                cube_query=prev_cq,
                trace=iz + ["Anlat: eldeki rapor YENİDEN YORUMLANDI (yeni sorgu YAZILMADI)",
                            _plan_izi(plan)],
            ), _sonuc, prev_cq)
            # Konuşmayı besleyen devam chip'leri — üçü de ZATEN çalışan konuşma türleri.
            _devam = [("Neden böyle?", "bu neden böyle?"),
                      ("Normal mi?", "normal mi?"),
                      ("Ne yapmalıyız?", "ne yapmalıyız?")]
            resp.suggestions = ([Suggestion(label=lb, query=q) for lb, q in _devam]
                                + list(resp.suggestions or []))[:8]
            return resp

        return None

    def _capayi_uygula(prev_cq: dict, capa, cube_meta: dict | None) -> tuple[dict, list[str]]:
        """Grafik çapasını (hücre koordinatı) GERÇEK bir alt-sorguya çevirir (Faz G2).

        `drill.select_cube_query` ÇAĞRILIR, yeniden yazılmaz: o boyutu kırılımdan çıkarıp
        yerine `eq` filtresi koyar — DrillDownPanel'in her adımının kullandığı aynı
        dönüşüm. İki yol aynı koordinat mantığını ayrı ayrı uygularsa zamanla ayrışır ve
        "grafikte tıkladığım hücre" ile "sohbette konuştuğum hücre" farklı olur.

        Geçersiz/eksik çapa **sessizce yok sayılır** ve konuşma tüm rapor üstünde yürür:
        uydurulmuş bir filtre, filtre olmamasından kötüdür.
        """
        if not isinstance(capa, dict):
            return prev_cq, []
        dim, val = capa.get("dimension"), capa.get("value")
        if not dim or val is None:
            return prev_cq, []
        if cube_meta and dim not in (cube_meta.get("dimensions") or []):
            _log.info("çapa yok sayıldı: %r bu cube'da boyut değil", dim)
            return prev_cq, []
        from app import drill as _drill

        return (_drill.select_cube_query(prev_cq, str(dim), str(val)),
                [f"Çapa: grafikte «{val}» hücresi → alt-sorgu ({dim})"])

    def _honest_refusal(note: str, trace: list[str],
                        suggestions: list[Suggestion] | None = None,
                        soz: str | None = None) -> AskResponse:
        """Dürüst ret — NoLlmGenerator'ın kendi docstring'inin vaat ettiği ama strict-agentic
        göçünde hiç uygulanmayan dönüşüm ("routers/ask.py bunu dürüst redde çevirir").
        ÖNCEDEN generate_sql/generate_followup_sql/refine_cube başarısızlığı 502 fırlatıyordu
        — kullanıcıya çökme gibi görünen bir hata. "Anlaşılmadı" bir SİSTEM HATASI değil,
        dürüstçe söylenecek bir sonuçtur (source=None, sql yok, çökme yok)."""
        # FAZ 5.17 — `soz` opsiyonel: verilmeyen yollarda frontend `soz ?? note` ile
        # bugünkü metni gösterir (GERİ AL bedava).
        return _finish(AskResponse(question=body.question, source=None, note=note,
                                   suggestions=suggestions or [], trace=trace, soz=soz))

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
        # FAZ -0.5a — ÇÖZÜLEMEYEN AY LİSTESİ kapıyı SUSTURAMAZ. `_period_hit_words` ay
        # adlarını `finditer` ile görüp "kullanıcı dönem belirtti" diyor, ama `date_filters`
        # AYRIK ayları ("ocak ve mart") tek bir aralığa çeviremiyor — sözleşme düz bir AND
        # zinciri. İkisi arasındaki bu asimetri §1.6'nın çarpıcı sonucunu üretiyordu:
        # "kullanıcı NE KADAR çok dönem detayı verirse, kapı O KADAR az soru soruyor."
        if cube_router.cozulemeyen_ay_listesi(q_norm) and not has_period_filter:
            # Seçenekler kullanıcının KENDİ saydığı aylardan üretilir — jenerik dönem
            # chip'leri ("Bugün · Bu hafta · Bu ay") burada işe YARAMAZ: iki belirli ay
            # isteyen birine "Bu ay" sunmak, soruyu cevaplamak değil konuyu değiştirmektir.
            # Belirsizlikte SORMAK (ADR-0008) cevaplanabilir bir soru sormak demektir.
            # YENİ YÜZEY AÇILMIYOR: aynı `suggestions` alanı, aynı chip bileşeni (§14.1).
            _ay_secenek = cube_router.ay_netlestirme(q_norm) or _PERIOD_SUGGESTIONS
            return _finish(AskResponse(
                question=body.question, source=None, cube_query=cq,
                note="Saydığın aylar tek bir tarih aralığına sığmıyor — hangisini "
                     "istiyorsun? (Kapsayan aralığı seçersen aradaki aylar da dahil olur.)",
                suggestions=[Suggestion(**s) for s in _ay_secenek],
                trace=[f"{trace_prefix}: ayrık ay listesi tek aralığa çevrilemiyor "
                       "→ netleştirme (LLM'siz)"],
            ))
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
        # KALICI GRANÜLERLİK TERCİHİ (FAZ E) — SQL derlenmeden ÖNCE uygulanır ki
        # cevaptaki sayı ile `cube_query` BİREBİR aynı şeyi anlatsın (sonradan
        # uygulansaydı makbuz ile rapor ayrışırdı).
        #
        # YALNIZ TAZE soruda: takipte kullanıcı var olan bir raporu YÖNLENDİRİYORDUR ve
        # aylar önce söylenmiş bir tercihin o canlı konuşmayla çekişmesi doğru olmaz.
        _t_sozluk = {} if is_followup else _tercihlerim()
        if _t_sozluk:
            _cq_yeni, _, _t_not = tercih.uygula(
                cq, q_norm, _t_sozluk, gorunum=None,
                zaman_boyutu=yoy.time_dim_of(schema, cq.get("cube")))
            if _t_not:
                cq = _cq_yeni or cq
                note = " · ".join(x for x in [note, _t_not] if x)
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
        # KALICI GÖRÜNÜM TERCİHİ (FAZ E) — ÜÇÜNCÜ yedek: facet ve açık grafik-tipi
        # isteği ÖNCE gelir. Tercihin, kullanıcının O TURDA yazdığı isteği ezmesi,
        # kendi geçmiş cümlesini bugünkü cümlesinin üstüne koymak olurdu.
        if not resp.view_hint and not is_followup:
            _g = _tercihlerim().get(tercih.ANAHTAR_GORUNUM)
            if _g:
                resp.view_hint = _g
                resp.note = " · ".join(x for x in [resp.note, _TERCIH_NOTU_GORUNUM(_g)] if x)
        # BOŞ SONUÇ DÜRÜSTÇE SÖYLENİR (Faz X'in gerçekçi senaryosunda ölçüldü).
        #
        # *"geçen haftada makine bazında oee"* → **satır=0, not=None, yorum=None**.
        # Kullanıcı boş bir tablo görüyor ve nedenini bilmiyor: soru mu yanlış anlaşıldı,
        # veri mi yok, filtre mi fazla dar? Bir "şirket beyni"nin verebileceği en kötü
        # cevap, sessiz bir boşluktur — çünkü okuyucu boşluğu KENDİ varsayımıyla doldurur.
        #
        # Not DETERMİNİSTİKTİR ve UYDURMAZ: yalnız sorgunun KENDİ dönem filtresini okur.
        # "Veri yok" demez — *"bu aralıkta kayıt bulunamadı"* der; ikisi farklı iddialardır.
        if (result or {}).get("row_count") == 0 and not resp.note:
            _dnm = [f for f in (cq.get("filters") or [])
                    if f.get("operator") in ("gte", "lte")]
            _aralik = ""
            if _dnm:
                _bas = next((f["value"] for f in _dnm if f["operator"] == "gte"), None)
                _son = next((f["value"] for f in _dnm if f["operator"] == "lte"), None)
                _aralik = (f" ({str(_bas)[:10]} – {str(_son)[:10]})" if _bas and _son
                           else (f" ({str(_bas)[:10]} sonrası)" if _bas else ""))
            resp.note = (f"Bu aralıkta{_aralik} kayıt bulunamadı. Rapor doğru kuruldu — "
                         "dönemi genişletmek ya da filtreyi gevşetmek ister misin?")
        if learn and vqr is not None:
            try:
                # `auto_cube` (Faz 4.1): saklanan SQL, LLM'in serbest metni DEĞİL —
                # katalogla doğrulanmış bir CubeQuery'den DERLENMİŞ SQL.
                # ⟳ FAZ 2b (§1.7 kararı): artık DOĞRUDAN TEKRAR-OYNATILMIYOR, yalnız
                # few-shot'ta kalıyor — gerekçe `app/vqr.py::_FEW_SHOT_ONLY_SOURCES`.
                # Kısaca: dondurulmuş kayıt İYİLEŞMEZ, router İYİLEŞİR; bu oturumda
                # dört sinonim cube DEĞİŞTİRDİ ve replay o düzeltmeleri gizlerdi.
                vqr.store(body.question,
                          {"wren_sql": sql, "mdl_version": service.mdl_version},
                          source="auto_cube")
            except Exception:
                _log.warning("VQR otomatik kayıt başarısız (best-effort)", exc_info=True)
        resp.contract_id = _record_contract(cq, sql, result, source)
        return _finish(_attach_viz(resp, result, cq))

    def _kiyas_cevabi(base_cq: dict, mode: str, iz: str) -> AskResponse | None:
        """Dönemsel kıyas (YoY/MoM) cevabı — TEK gövde, İKİ çağıran.

        FAZ X'te canlı ölçülen kusur bir **kimlik asimetrisiydi**: mekanizma TAZE dalda
        vardı, kardeşi olan TAKİP dalında YOKTU. Sonuç:

            "bu yıl makine bazında oee" → rapor ✅
            takip: "geçen yılla kıyasla" → *"Bu takip mesajını ilişkilendiremedim"* ❌

        …oysa bu bir analistin en doğal ikinci cümlesi. Düzeltirken gövde KOPYALANMADI:
        iki dal aynı fonksiyonu çağırır, aksi hâlde zamanla ayrışırlardı (bu deponun
        ölçülmüş bir numaralı kusur sınıfı).
        """
        try:
            from app import yoy as _yoy

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
                trace=[f"{iz} ({mode}, LLM'siz)"],
            )
            resp.contract_id = _record_contract(final_cq, out["base_sql"], result, "cube")
            return _finish(_attach_viz(resp, result, final_cq))
        except Exception:
            _log.warning("YoY/MoM hesaplama başarısız (best-effort) — sıradaki adıma "
                         "düşülüyor", exc_info=True)
            return None

    # 1) Deterministik ön-kapı — WrenAI'nin intent_classification'ının LLM'siz Dima
    # karşılığı: meta/ürün soruları ve katalog-keşfi SQL üretimine hiç girmez.
    if _is_meta(q_norm):
        return _finish(AskResponse(
            question=body.question, source="meta", note=_META_TEXT,
            suggestions=[Suggestion(**s) for s in _META_SUGGESTIONS],
            trace=["meta soru → deterministik yanıt (LLM'siz)"],
        ))
    # SOSYAL SINIF (FAZ D1) — META'DAN SONRA, çünkü *"merhaba, neler yapabilirsin?"*
    # daha bilgilendirici olan meta cevabını hak eder.
    #
    # İKİ KOŞUL BİRDEN: (a) hiçbir veri sinyali yok (YAPISAL kapı) ve (b) tanınan bir
    # sosyal edim var (SINIF). Yalnız (b) olsaydı *"teşekkürler, bu yıl ciro?"* sosyal
    # sayılırdı; yalnız (a) olsaydı anlamsız bir dize sosyal cevap alırdı — ikisi de
    # yanlış olurdu, o yüzden kapı iki kanatlı.
    # ⚠️ FAZ 0.13 — KILL-SWITCH BURADA, `cube_router`'DA DEĞİL.
    # MIMARI §6.13z/9.11: *"bir kill-switch yalnız KOD'da varsa YARIMDIR"* — sınıf kod
    # olarak vardı ama **geri alma yolu yoktu**; teslim borcunun asıl parçası buydu.
    # Kapı çağırandadır çünkü `cube_router` **hiçbir bayrak okumaz** ve okumamalı
    # (FAZ 0.18'in değişmezi, `test_CUBE_ROUTER_BAYRAK_OKUMUYOR` ile kilitli):
    # deterministik saflık, bayrak sızarsa çürür.
    # `off` → sınıf hiç sorulmaz → cevap bugünkü merdivenden iner (GERİ AL).
    _sosyal = (cube_router.sosyal_edim(q_norm)
               if "sosyal_sinif" in resolve_for(settings, principal) else None)
    if _sosyal:
        _tur, _tam_kaplama = _sosyal
        # Sosyal sınıf İKİ yoldan biriyle kazanır:
        #   (a) hiç veri sinyali yok        → "teşekkürler"
        #   (b) kalıp ifade TÜM mesajı kaplıyor → "iyi çalışmalar" (`çalışma` katalogda
        #       gerçek bir terim ama kalıp ifadenin parçası, katalog terimi değil)
        # Aksi hâlde sosyal sözcük İÇEREN bir veri sorusudur ve kapı AÇILMAZ.
        if _tam_kaplama or not cube_router.veri_niyeti_var(q_norm, schema):
            return _finish(AskResponse(
                question=body.question, source="meta", note=_SOSYAL_METIN[_tur],
                suggestions=[Suggestion(**s) for s in _META_SUGGESTIONS[:3]],
                trace=[f"sosyal sınıf ({_tur}) → deterministik yanıt "
                       "(LLM'siz, sıfır maliyet)"],
            ))
    # EYLEM SINIFI (FAZ H) — SOSYAL'DAN SONRA, KATALOG'DAN ÖNCE.
    #
    # Ölçülen kusur: *"her pazartesi bu raporu bana yolla"* → `source=rule`, **SQL
    # ÜRETTİ**. Ajan yazmıyordu ama UYDURUYORDU — sorulmayan bir soruyu cevaplıyordu.
    # Sınıf D1 (sosyal) ve D2 (*"analiz et"*) ile aynı ailedendir: veri sorusu OLMAYAN
    # bir ifade türünün tanımsızlığı.
    #
    # Argümanlar konuşmadaki DOĞRULANMIŞ `cube_query`den gelir — bir LLM'in uydurduğu
    # sorgu bir zamanlamaya yazılsaydı o uydurma HER HAFTA tekrar koşardı.
    # `view_hint` BİLEREK boş: istek gövdesinde yoktur ve uydurulmaz. Kullanıcının o
    # anki CANLI görünümünü (tip/pivot) yalnız frontend bilir — onay çağrısında ekler
    # (manuel "panoya ekle" düğmesi de tam olarak bunu yapıyor, ReportCard.tsx).
    # 🔴 **FAZ 5.0 — K3 DÜZELTMESİ (tek çağrı, hiçbir `if`in içinde değil).**
    # `followup.sinifla()`'nın TEK çağrısı `if structural_followup:` bloğunun İÇİNDEYDİ ve
    # `baglam_var=` sabit **`True`** geçiliyordu. İki ölçülmüş sonucu vardı:
    #   (1) İstemci `cube_query` göndermiyorsa (Discovery / ham thread) *"bu neden
    #       böyle?"* · *"normal mi?"* · *"analiz et"* — **hiçbiri sınıflanmıyordu**;
    #       beş konuşma türü de o thread sınıfında **erişilemezdi**.
    #   (2) Sabit `True` yüzünden `followup.py`'nin *"bağlam-yok"* kuralı **üretimde hiç
    #       ateşlenmiyordu** — yalnız birim testinde yaşıyordu.
    # ⚠ Çağrı yukarı taşındı ama **hiçbir yol kesilmedi** (KAT-2).
    niyet = followup.sinifla(body.question, baglam_var=bool(is_followup))

    _eylem_karar = eylem.degerlendir(q_norm, body.cube_query, schema=schema)
    # 🔴 FAZ 5.1 — **6. TÜR: *"bunu takip et"***. `degerlendir()` bunu tanımaz (teslim
    # fiili yok, yinelenme yok) → `SINIF_YENI` → kapsam kapısı **R10** → dürüst red.
    # Ölçüldü: panoya/zamanlamaya giden **hiçbir doğal-dil yolu yoktu**; kullanıcı 🔔 ve
    # *"+ panoya ekle"* düğmelerini **fareyle bulmak zorundaydı**.
    #
    # ⚠ **Yeni motor YAZILMADI:** periyot varsa `degerlendir()`'in KENDİ `ZAMANLA` dalı
    # çağrılır. Bu dal yalnız **erişimi** açar — ikinci bir zamanlama yolu değil.
    # ⚠ Bayrak `off` iken bu blok HİÇ çalışmaz → bugünkü davranış birebir (KURAL B).
    # ⚠ `niyet` YUKARIDA **bir kez** hesaplandı (FAZ 5.0). İkinci bir `sinifla()` çağrısı
    # açmak, aynı kuralın ikinci sahibini yaratırdı — ve `test_FAZ_5_0_sinifla_
    # STRUCTURAL_BLOGUN_DISINDA` bunu ilk denemede **yakaladı**.
    if (_eylem_karar is None and niyet.tur == followup.TUR_TAKIP
            and "tur_takip" in resolve_for(settings, principal)):
        _eylem_karar = eylem.takip_karari(q_norm, body.cube_query, schema=schema)
    if _eylem_karar is not None:
        return _finish(AskResponse(
            question=body.question, source="eylem", note=_eylem_karar.not_,
            cube_query=body.cube_query or None,
            # ⚠ `or None` DEĞİL: `AskResponse.suggestions` bir listedir ve `None`
            # kabul etmez — ilk yazımım 21 testi kırdı ve hızlı kapı bunu yakaladı.
            suggestions=list(_eylem_karar.chipler),
            eylem_onerisi=_eylem_karar.oneri, trace=_eylem_karar.iz,
        ))
    # KALICI SUNUM TERCİHİ (FAZ E) — *"bundan sonra hep aylık göster"*.
    #
    # Ölçüldü: bu cümle *"Bu takip mesajını ilişkilendiremedim"* ya da
    # *"«bundan» yerine «unvan» mi demek istedin?"* alıyordu. Kullanıcı tercihini
    # söylüyor, sistem anlamıyordu.
    #
    # Tercih YAZMAK bir yazmadır → Faz H'nin ONAY kademesinden geçer. Muafiyet açmak,
    # bir faz önce yazdığım değişmezi kodda tanımamak olurdu.
    _tercih_adayi = tercih.tespit(q_norm, gorunum=_viz_hint(q_norm))
    if _tercih_adayi is not None:
        _tb = eylem.beyan(eylem.TERCIH_KAYDET)
        return _finish(AskResponse(
            question=body.question, source="eylem", note=tercih.ozet(_tercih_adayi),
            cube_query=body.cube_query or None,
            eylem_onerisi={
                "eylem": _tb.ad, "ozet": tercih.ozet(_tercih_adayi), "izin": _tb.izin,
                "geri_alinabilir": _tb.geri_alinabilir,
                "argumanlar": {"anahtar": _tercih_adayi.anahtar,
                               "deger": _tercih_adayi.deger,
                               "kaynak_ifade": body.question},
            },
            trace=[f"kalıcı sunum tercihi ({_tercih_adayi.anahtar}="
                   f"{_tercih_adayi.deger}) → onay bekliyor (LLM'siz, SQL'siz)"],
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
        # ⚠️ BENZERLİK EŞLEŞMESİ `route()`'A YENİLİR — birebir tekrar YENİLMEZ.
        #
        # **CANLI TURDA ÖLÇÜLDÜ (2026-08-03), §1.7'nin riski gerçek çıktı ve plandakinden
        # DAHA KÖTÜ:** kullanıcı *"geçen ay toplam **FİRE**"* sordu; VQR embedding
        # benzerliğiyle *"geçen ay toplam **CİRO**"* kaydını eşleştirdi ve
        # `SELECT SUM(ciro_tl)` döndürdü — `source="vqr"`, `confidence=0.95`,
        # *"önceden doğrulanmış sorgu"* rozetiyle. **Sorulan ölçünün ZIDDI bir ölçü.**
        #
        # İki soru TEK KELİME farklıydı ve o kelime **ölçünün kendisiydi** — yani beş
        # token'ın dördü eşleşince kosinüs 0,92 eşiğini aşıyor. Embedding için "fire" ile
        # "ciro" bu bağlamda neredeyse aynı; **anlamca zıt** oldukları görülmüyor.
        #
        # Faz 2b'nin kararı (`auto_cube`'u replay'den çıkarmak) DOĞRUYDU ama **yetersizdi**:
        # bu kayıt `user_verified`'dı, yani insan onaylıydı. Risk kaynağın güveninde değil,
        # **benzerlik eşiğinin kendisinde**.
        #
        # Kural (ADR-0008'in "deterministik-önce"si merdivene uygulanmış hâli):
        #   * **BİREBİR** (normalize) eşleşme → replay KALIR. Aynı soruyu ikinci kez soran
        #     kullanıcı aynı cevabı hak eder; burada tahmin yok.
        #   * **BENZERLİK** eşleşmesi → `route()` bir cevap üretebiliyorsa **O KAZANIR**.
        #     Deterministik ve tam bir cevap, olasılıksal ve yaklaşık bir eşleşmeye
        #     tercih edilir. `route()` çözemezse benzerlik kaydı yine devreye girer —
        #     yani kapsam KAYBEDİLMEZ, yalnız sıra düzeltilir.
        if cached and cube_router._norm(cached.get("question") or "") != q_norm:
            try:
                _det = cube_router.route(
                    body.question, schema,
                    liste_kirilimi="liste_niyeti" in resolve_for(settings, principal))
            except Exception:  # noqa: BLE001
                _det = None
            if _det:
                _log.info("VQR benzerlik eşleşmesi ATLANDI — route() deterministik cevap "
                          "üretiyor (kayıt=%r, soru=%r)",
                          (cached.get("question") or "")[:60], body.question[:60])
                cached = None
            elif not _vqr_olcu_tutarli(q_norm, cached, schema):
                # ⚠️ İKİNCİ KAPI — `route()` çözemediğinde de gerekli.
                #
                # Yukarıdaki "deterministik-önce" kuralı bir HAFİFLETMEDİR: yalnız
                # `route()` bir cevap üretebildiğinde korur. Ölçülen boşluğun (~%31)
                # içinde `route()` çözemez ve benzerlik kaydı **yine** cevap olur —
                # canlı turda görülen *"fire → ciro"* vakasının tam olarak mümkün kaldığı
                # yer burasıdır.
                #
                # Kapı SEMANTİK, eşik değil: kullanıcının sorusu bir ölçüyü AÇIKÇA
                # adlandırıyorsa (`_match_measure`), kaydın ölçüsü de o olmalı. Eşiği
                # yükseltmek yanlış çözümdü — asıl sorun benzerliğin ne kadar YÜKSEK
                # olduğu değil, **hangi kelimede** olduğu: beş token'ın dördü eşleşiyor
                # ama farklı olan tek kelime ÖLÇÜNÜN KENDİSİ.
                _log.info("VQR benzerlik eşleşmesi ATLANDI — ölçü TUTARSIZ "
                          "(kayıt=%r, soru=%r)",
                          (cached.get("question") or "")[:60], body.question[:60])
                cached = None
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

    def _yol_izinli(basamak: str) -> bool:
        """Kullanıcının `yol_siniri` tercihi bu basamağa izin veriyor mu? (Faz F2)

        Üç ayrık seviye, **merdivenin kendisine** bağlı — uydurma bir kalibrasyon değil:

            "deterministik" → yalnız `route()`
            "llm"           → route + Intent-JSON
            None / "kesif"  → + Discovery  (**bugünkü varsayılan**)

        Tanınmayan bir değer **sınır saymaz** (varsayılana düşer): bir yazım hatasının
        kullanıcının cevabını sessizce kesmesi, sınırın kendisinden daha zararlıdır.
        """
        # 🔴 **FAZ 5.14 — `mod="hizli"` AYNI KAPIDAN GEÇER.** İkinci bir "LLM'i kapat"
        # yolu açmak, aynı kuralın iki sahibi olurdu ve ikisi ayrışırdı: biri Discovery'yi
        # keser, öteki kesmez ve hangisinin kazandığı çağrı sırasına bağlı kalırdı.
        #
        # ⚠ `hizli`, `yol_siniri="deterministik"` ile **birebir aynı** anlama gelir —
        # yalnız kullanıcıya **daha anlaşılır bir adla** sunulur. *Aynı davranışa iki ad
        # vermek meşrudur; iki UYGULAMA vermek değildir.*
        # ⚠ Bayrak kapalıysa alan **yok sayılır** (bugünkü davranış birebir).
        from app.features import resolve_for as _rf

        _mod = str(getattr(body, "mod", None) or "").strip().lower()
        if _mod == "hizli" and "hizli_derin" in _rf(settings, principal):
            return False if basamak in ("intent", "discovery") else True

        sinir = (getattr(body, "yol_siniri", None) or "").strip().lower()
        if sinir not in ("deterministik", "llm"):
            return True
        if basamak == "intent":
            return sinir == "llm"
        return False          # discovery: iki sınırda da kapalı

    def _yol_siniri_notu(basamak: str) -> str:
        """Sessizce boş dönmek YOK: kullanıcı kendi koyduğu sınırı görebilmeli."""
        sinir = (getattr(body, "yol_siniri", None) or "").lower()
        ad = {"deterministik": "yalnız deterministik küp",
              "llm": "küp + LLM alan seçimi"}.get(sinir, sinir)
        return (f"Bu soruyu {'katalogdan seçimle' if basamak == 'intent' else 'ham SQL ile'} "
                f"cevaplayabilirdim ama yol sınırın **{ad}** olarak ayarlı. "
                "Sınırı gevşetirsen deneyebilirim.")

    def _olcu_belirsizligi_netlestir(q_norm: str, schema: dict) -> AskResponse | None:
        """Katalog **≥2 SAHİP** biliyorsa netleştirme chip'i — yoksa `None`.

        ## FAZ 2a'nın etiket çakışması tuzağı (korunuyor)

        Chip'ler eskiden yalnız ölçünün GÖRÜNEN adıyla kuruluyordu; iki cube aynı adı
        taşıdığında (`cari.bakiye` ve `mizan.bakiye` → ikisi de *"bakiye"*) liste
        tekilleşip 1'e düşüyor, `>= 2` kapısı chip'i **sessizce** atlıyor ve soru
        Discovery'ye düşüyordu. Ölçüldü: 54 belirsiz sinonimin **33'ü (%61)** bu
        tuzaktaydı. `olcu_netlestirme` çakışan etiketi **cube ile** niteler.

        ## Neden ORTAK yardımcı oldu (Faz F)

        Aynı kural artık **iki** yerden çağrılıyor: (a) bayrak açıkken Intent-JSON'dan
        **ÖNCE**, (b) bayrak kapalıyken bugünkü yerinde (Intent'ten sonra). İki kopya
        yazmak, bu deponun defalarca ölçtüğü *"kimlik asimetrisi"*ni üretirdi.
        """
        try:
            cands = cube_router.measure_cube_candidates(q_norm, schema)
        except Exception:
            return None
        distinct_cubes = {c["name"]: (c, m) for c, m in cands}
        if len(distinct_cubes) < 2:
            return None
        etiketler = cube_router.olcu_netlestirme(list(distinct_cubes.values()), schema)
        if len(etiketler) < 2:
            return None
        return AskResponse(
            question=body.question, source=None,
            note="Birden fazla konu anlaşıldı, hangisini istiyorsun?",
            soz=_soz.soz("netlestirme.konu"),
            suggestions=[Suggestion(**s) for s in etiketler[:6]],
            trace=["Intent-path: çapraz konu → netleştirme (LLM'siz)"],
        )

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
        # FAZ 2a-5 (KURAL B) — liste/döküm niyetini kırılıma çevirme yetkisi. Bir kez
        # çözülür ve BU FONKSİYONDAKİ HER `route()` çağrısına geçirilir: biri atlanırsa
        # aynı soru geldiği yola göre farklı davranır (Faz -1'in "üç çağrı yeri" dersi).
        _liste = "liste_niyeti" in resolve_for(settings, principal)
        try:
            route_hit = cube_router.route(body.question, schema, liste_kirilimi=_liste)
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
                    retry_hit = cube_router.route(corrected_q, schema,
                                                  liste_kirilimi=_liste)
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
                # §G/AJ0 örnek #1 — **bir öneri, ancak CEVAP AÇIYORSA öneridir.** Karar
                # `app/typo_onerisi.py`'de (saf, test edilebilir): `0.21`'in modül büyüme
                # kapısı bu mantık `ask()` içindeyken tavanı aştı ve kendi talimatını
                # uygulattı — *"yeni davranışı MODÜLE ÇIKAR, tavanı yükseltme."*
                typo_suggestion = typo_onerisi.gecerli_oneri(typo_fixes, schema, liste_kirilimi=_liste)  # noqa: E501

        # Dönemsel kıyas (YoY/MoM) — route() _COMPARE_HINTS nedeniyle BİLEREK None döner;
        # ayrı, YİNE deterministik bir mekanizma var (/cube'un compare chip'iyle AYNI —
        # app/yoy.py). Kıyas ifadesi sökülüp temiz metinle route() tekrar denenir.
        if route_hit is None:
            mode = cube_router.compare_mode(q_norm)
            if mode:
                cleaned = cube_router.strip_compare(q_norm)
                try:
                    base_hit = cube_router.route(cleaned, schema,
                                                 liste_kirilimi=_liste)
                except Exception:
                    base_hit = None
                if base_hit:
                    _kiyas = _kiyas_cevabi(base_hit["cube_query"], mode,
                                           "Intent-path: dönemsel kıyas")
                    if _kiyas is not None:
                        return _kiyas

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

        # FAZ 3b — PROMPT-ENHANCER (§4.3). T1'in DÖRDÜNCÜ, AYRI LLM rolü: Intent-JSON
        # ALAN SEÇER, bu yalnız METNİ iyileştirir ve AYNI deterministik `route()`'a geri
        # verir — *"hangi ölçü/boyut"* kararı HÂLÂ KÜPTEDİR.
        #
        # Planın dört şartı:
        #   1. YALNIZ `route()` boş dönünce tetiklenir → %64'lük sıfır-maliyet çoğunluk
        #      dokunulmadan kalır (her soruda LLM çağrısı YOK).
        #   2. Başarı SESSİZDİR; iz makbuza `question_original`/`question_normalized`
        #      olarak yazılır — denetlenebilir ama sohbeti yavaşlatmaz.
        #   3. Belirsizlik MEVCUT chip mekanizmasına devreder; YENİ UI YÜZEYİ AÇILMAZ.
        #   4. Ucuz/seçici model (`*_select_model`).
        #
        # ⟳ PLANIN ZORUNLU EKLEMESİ: çağrı `Planlayici.calistir()` üzerinden yapılır.
        # Aksi halde bu, F2'nin tam olarak engellemek için var olduğu **kapısız LLM
        # çağrısı** olurdu: yetkiye bağlanmaz, bütçeye sayılmaz, makbuzda ADIM olarak
        # görünmez — yani *"LLM ne zaman devreye girdi"* sorusu cevaplanamaz hale gelirdi.
        # `sorgu-uretimi` etiketi DETERMİNİSTİK-ÖNCE kapısını da bağlar: `route` planlayıcı
        # üzerinden denenmeden bu araç seçilemez (kapı bunu KENDİSİ zorlar).
        if route_hit is None and "prompt_enhancer" in resolve_for(settings, principal):
            route_hit, _eh_iz = _prompt_enhance_dene(
                request, body.question, q_norm, schema, principal, liste=_liste)
            if route_hit:
                intent_source = "cube"
                typo_fix_trace = _eh_iz

        # ── FAZ F — KATALOG BELİRSİZLİĞİ INTENT-JSON'U ÖNCELER (bayraklı) ──────────
        #
        # ## Canlıda ölçülen vaka (3 Ağustos 2026)
        #
        #     "bu yıl bakiye" → source=cube+llm · cube=mizan · confidence=0.85 · chip YOK
        #
        # Oysa `bakiye` katalogda **iki** cube'un ölçüsü (`cari` · `mizan`) ve §6.1g'nin
        # netleştirme chip'i tam bunun için var. CI'da (LLM yok) chip ateşliyor;
        # **üretimde Intent-JSON onu gölgeliyor** — olasılıksal bir 2/3 oyu,
        # **deterministik olarak BİLİNEN** bir belirsizliği eziyor.
        #
        # Bu, §1.7'nin dersinin yeni bir kapıdan girişi: *"yapısal geçerlilik ≠ semantik
        # doğruluk"*. Gerçekten belirsiz bir kelimede **doğru cevap yoktur**; herhangi bir
        # seçim yazı-turadır ve 0.85 rozetiyle sunulması onu daha kötü yapar.
        #
        # ## Nüfusu ÖLÇÜLDÜ (LLM'siz, 384 ölçü sinonimi taranarak)
        #
        #     katalogda ≥2 SAHİP + route ÇÖZEMİYOR : 53   ← bu kapının nüfusu
        #     katalogda ≥2 SAHİP ama route ÇÖZÜYOR : 20   ← DOKUNULMAZ (spesiflik kuralı)
        #
        # İkinci satır kritik: `route()` çözebiliyorsa belirsizlik **zaten kırılmıştır**
        # (2a-3'ün "en spesifik ölçü kazanır" kuralı) ve kapı oraya karışmaz — koşul
        # `route_hit is None` ile bağlı.
        #
        # ## KURAL B — varsayılan KAPALI ve nedeni
        #
        # Kapsam kaybı gerçektir: bugün LLM'in cevapladığı sorular netleştirmeye düşer.
        # Kazanç (kapanan sessiz-yanlış) ile kaybın kıyası **gerçek sağlayıcıyla** ölçülmeli
        # ve o ölçüm bu turda kotaya takıldı. Ölçmeden açmak, 2a-1'in `elektrik` hatasını
        # (kimlik silindi, 388 cevap kayboldu) tekrarlamak olurdu.
        if (route_hit is None
                and "netlestirme_onceligi" in resolve_for(settings, principal)):
            _bel = _olcu_belirsizligi_netlestir(q_norm, schema)
            if _bel is not None:
                _bel.trace = ["Intent-path: katalog belirsizliği → netleştirme "
                              "Intent-JSON'u ÖNCELEDİ (LLM'siz)"]
                return _finish(_bel)

        if route_hit is None and not _yol_izinli("intent"):
            # FAZ F2 — kullanıcı "yalnız deterministik" dedi ve route çözemedi.
            return _finish(AskResponse(
                question=body.question, source=None, note=_yol_siniri_notu("intent"),
                suggestions=_dogrulanmis_chipler(
                    [str(c.get("display") or c.get("name") or "")
                     for c in cube_router.ilgili_cubelar(q_norm, schema)][:4],
                    schema, en_fazla=4),
                trace=["Yol sınırı: LLM basamakları kullanıcı tercihiyle KAPALI"],
            ))

        if route_hit is None and "ask_intent_first" in resolve_for(settings, principal):
            llm_probe = getattr(request.app.state, "llm", None)
            if llm_probe is not None and hasattr(llm_probe, "select_cube"):
                try:
                    catalog_text, cube_index = cube_router.build_catalog(schema)
                    # SELF-CONSISTENCY (Faz D4). `_select_consistent` ve `consistency_k=3`
                    # ayarı ikisi de YAZILMIŞ ama BAĞLANMAMIŞTI: burada tek bir örnek
                    # alınıyordu, yani ayar bir NİYET BEYANIYDI — `grep consistency_k` bugüne
                    # kadar TEK bir tüketici bulmuyordu. Belgelenmiş davranışla kodun
                    # ayrışması, bu depoda tekrar eden en pahalı hata sınıfıdır.
                    #
                    # k örnek → kanonik oylama. Uyuşma hem doğruluğu artırır hem de
                    # KALİBRE bir güven sinyali verir (Faz F planlayıcısının bütçe/eskalasyon
                    # kararının girdisi). Örnekler paralel koşar → gecikme ~tek çağrı.
                    k = max(1, int(getattr(settings, "consistency_k", 1) or 1))
                    # FAZ 3a (KURAL B) — ŞEMA-KISITLI ÇIKTI. Bayrak kapalıysa `sema`
                    # None kalır ve yol BİREBİR bugünküdür. Şema her istekte kataloğun
                    # O ANKİ hâlinden üretilir: cube yeniden adlandırılırsa/ölçü
                    # eklenirse enum kendiliğinden güncel kalır (bayat enum, olmayan
                    # enum'dan kötüdür — modele var olmayan bir adı DAYATIRDI).
                    _sema = None
                    if "llm_sema_kisitli" in resolve_for(settings, principal):
                        try:
                            _sema = cube_router.cube_query_json_schema(cube_index)
                        except Exception:
                            _log.warning("şema üretilemedi → serbest-JSON yolu",
                                         exc_info=True)
                    parsed, uyum, eksen, adaylar = _select_consistent(
                        llm_probe, body.question, catalog_text, cube_index, k, _sema)
                    if parsed:
                        route_hit = {"cube_query": parsed, "order": None, "limit": None}
                        intent_source = "cube+llm"
                        if k > 1:
                            # Uyum oranı TRACE'e yazılır: cevabın yanında "ne kadar emindim"
                            # görünür olmalı (Faz F'nin kalibrasyon girdisi de bu).
                            _uyum_notu = f"self-consistency %{uyum*100:.0f} ({k} örnek)"
                            typo_fix_trace = (f"{typo_fix_trace} · {_uyum_notu}"
                                              if typo_fix_trace else _uyum_notu)
                    elif adaylar and eksen:
                        # UYUŞMAZLIK TEK EKSENDE → tahmin etme, SOR. Faz 3.1'in cube
                        # beraberlik chip'iyle aynı felsefe: belirsizlik bir cevap değil,
                        # bir sorudur. Eksen birden çoksa chip anlaşılmaz olur → sessiz
                        # düşüş (aşağıdaki Discovery merdiveni devralır).
                        return _finish(_intent_uyusmazlik_chipi(
                            body.question, eksen, adaylar, schema, uyum, k))
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
            # FAZ -0.5d — DÖNEM ASİMETRİSİ. `llm.py`'nin prompt'u LLM'e tarih filtresi
            # yazmayı AÇIKÇA YASAKLIYOR ("TARİH filtresi ASLA yazma — sistem hesaplar").
            # Ama "sistem" o beyanı yalnız İKİ yolda uyguluyordu: `route()` kendi içinde
            # (`cube_router.py`: `filters.extend(date_filters(...))`) ve takip-düzenleme dalı
            # (`_resolve_period`). **Taze Intent-JSON yolunda hesaplayan kimse yoktu** — LLM
            # yazmıyor, sistem de hesaplamıyor, sonuç sessizce TÜM ZAMANLAR.
            #
            # Bu bir politika değil bir ASİMETRİDİR: beyan zaten verilmiş, bir yol onu
            # uyguluyor, öteki uygulamıyor. `date_filters` TEK kaynaktır ve üç yol da onu
            # çağırır — kural ikinci kez yazılmıyor.
            #
            # `_resolve_period` doğrudan çağrılMADI çünkü o "tarih" adını SABİT kodluyor;
            # zaman boyutu farklı adlı bir cube'da var olmayan bir kolona filtre yazardı.
            # Burada cube'un KENDİ beyan ettiği zaman boyutu kullanılır (route() ile aynı).
            if intent_source == "cube+llm":
                _tds = (cube_meta or {}).get("time_dimensions") or []
                if _tds and not any(f.get("dimension") == _tds[0]
                                    for f in (cq.get("filters") or [])):
                    _dfs = cube_router.date_filters(q_norm, _tds[0])
                    if _dfs:
                        cq = {**cq, "filters": [*(cq.get("filters") or []), *_dfs]}
                        typo_fix_trace = ((f"{typo_fix_trace} · dönem sistemce çözüldü")
                                          if typo_fix_trace else "dönem sistemce çözüldü")
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
                suggestions=_dogrulanmis_chipler(labels, schema, en_fazla=8),
                trace=["Intent-path: cube belirlendi, ölçü belirsiz → netleştirme (LLM'siz)"],
            ))

        _belirsiz = _olcu_belirsizligi_netlestir(q_norm, schema)
        if _belirsiz is not None:
            return _finish(_belirsiz)

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
            # FAZ -1: tarama `cube_router.ilgili_cubelar`'a TAŞINDI (kopyalanmadı) —
            # aynı sinyal artık "hiç konu yok" dalında da kullanılabiliyor.
            hit_cube_names = {c["name"] for c, _ in hits}
            other_topic = False
            for c in cube_router.ilgili_cubelar(q_norm, schema, haric=hit_cube_names):
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
            # ÇAPRAZ-ALAN PİLOTU BURADA DA DENENİR — canlı turda ölçüldü (3 Ağustos).
            #
            # `other_topic=True` demek: soruda **rakip bir cube kimliği** var — yani bu,
            # katalogdaki en güçlü ÇAPRAZ-ALAN sinyalidir (*"personel bazlı verimlilik"*:
            # `verimlilik`→oee, `personel`→parti/ik). Pilot ise adım 4b'de, yani bu
            # `return`'ün **çok sonrasında** duruyordu → bayrak AÇIKKEN bile hiç
            # ateşlemiyordu ve Faz 4'ün kabul ölçütü (*"çapraz-alan pilotu → 2 adımlı
            # kompozisyon"*) canlıda **karşılanmıyordu**.
            #
            # Bu, §1.5'in dersinin kardeş daldaki hâli: **truthy bir netleştirme, daha
            # yetenekli bir adımı sessizce öldürür.** Orada Discovery için düzeltilmişti;
            # kompozisyon için düzeltilmemişti (*"kimlik asimetrisi"*, MIMARI §6.1h).
            #
            # KAPSAM KAYBI YOK: pilot `None` dönerse netleştirme aynen döner. Bayrak
            # (`agent_plan_secimi`, varsayılan **off**) kapalıyken bu blok hiç koşmaz —
            # KURAL B.
            if other_topic and "agent_plan_secimi" in resolve_for(settings, principal):
                _pilot = _capraz_alan_pilotu(request, body, q_norm, schema, principal, [])
                if _pilot is not None:
                    return _pilot
            return _finish(AskResponse(
                question=body.question, source=None, note=note,
                suggestions=_dogrulanmis_chipler(labels, schema, en_fazla=6),
                trace=[trace_msg],
            ))

        # HİÇ KONU YOK ("bu yıl tüm aylarını karşılaştır" — NEYİ?): dönem/kıyas dili var
        # ama partial_unknowns HİÇBİR (cube, ölçü) çifti bulamadı (hits boş).
        #
        # FAZ -1 — ÖLÜ UÇ. Bu dal eskiden HİÇBİR DARALTMA DENEMEDEN 13 cube'un 1'er
        # örneğini döküyordu ve `_finish(...)` truthy döndüğü için Discovery'ye (adım 5)
        # HİÇ SIRA GELMİYORDU. Canlı örnek: *"son 6 ay personel bazlı çalışma süreleri
        # kıyasla"* → 13 seçenekli dump, ve kaç kez denenirse denensin hep aynı duvar.
        # Oysa "personel" `ik`/`parti` cube'larında ZATEN bir sinonim — sistemin elinde
        # daraltacak sinyal vardı, o sinyal yalnız BAŞKA bir dalın içinde kullanılıyordu.
        if not hits and (cube_router._period_hit_words(q_norm) or cube_router.compare_mode(q_norm)):
            # (1) UCUZ DETERMİNİSTİK DARALTMA — LLM gerekmez, yeni regex gerekmez;
            # var olan iki dal artık AYNI sinyali paylaşıyor (ADR-0008: kök neden düzelt).
            ilgili = cube_router.ilgili_cubelar(q_norm, schema)
            if ilgili:
                dar_labels: list[str] = []
                for c in ilgili[:4]:
                    for m in (c.get("measures") or [])[:3]:
                        mdisp = (c.get("measure_synonyms_display") or {}).get(m) or m
                        if mdisp not in dar_labels:
                            dar_labels.append(mdisp)
                konular = ", ".join(c.get("display") or c.get("name") or "" for c in ilgili[:3])
                return _finish(AskResponse(
                    question=body.question, source=None,
                    note=f"{konular} ile ilgili görünüyor ama hangi ölçüyü istediğini "
                         "anlayamadım. Şunlardan biri mi?",
                    suggestions=_dogrulanmis_chipler(dar_labels, schema, en_fazla=8),
                    trace=["Intent-path: konu daraltıldı (zayıf cube/boyut sinyali, LLM'siz)"],
                ))
            # (2) DISCOVERY BİR SEÇENEK OLSUN — ama GÜVENLE. Yapısal-takip zinciri bu
            # kapıyı zaten doğru kuruyor (`_match_cube is not None` ise Discovery'ye düş);
            # fresh zincirinde AYNI kapı yoktu, asimetri buydu. Gerçek bir katalog cube'u
            # tanınıyorsa `None` dönülür ve merdivenin 5. basamağı devralır.
            if cube_router._match_cube(q_norm, schema) is not None:
                return None
            # (3) HİÇBİR kelime tanınmadı → bugünkü dürüst red KORUNUR. Katalog dökümü
            # burada bir "bildiğini okuma" değil, sistemin NE YAPABİLDİĞİNİ göstermesidir —
            # ve bu, hiçbir şey anlaşılmadığında yapılabilecek en dürüst şeydir.
            example_labels = []
            for c in schema.get("cubes") or []:
                for m in (c.get("measures") or [])[:1]:
                    mdisp = (c.get("measure_synonyms_display") or {}).get(m) or m
                    if mdisp not in example_labels:
                        example_labels.append(mdisp)
            return _finish(AskResponse(
                question=body.question, source=None,
                note="Neyi karşılaştırmak/görmek istediğini anlayamadım — sorunda tanıdığım "
                     "bir konu geçmiyor. Şunlardan birini mi demek istedin?",
                suggestions=_dogrulanmis_chipler(example_labels, schema, en_fazla=14),
                trace=["Intent-path: hiçbir konu tanınmadı → katalog örnekleri (LLM'siz)"],
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
        # ⚠ TAMAMLAMA ile GENİŞLETME AYRI ŞEYLERDİR (Faz X'te canlı ölçüldü).
        #
        # Bu fonksiyonun adı ve docstring'i *"bir raporu TAMAMLADIĞINDA"* diyor; kod ise
        # yalnız *"önceki mesaj konu taşıyor mu"* diye bakıyordu. Ölçülen sonuç:
        #
        #   1) "bu yıl makine bazında oee"  → dim=['makine']            ✅ (zaten TAM)
        #   2) takip: "vardiya bazında"     → dim=['makine','vardiya']  ✅ (GENİŞLETME)
        #   3) AYNI taban soru tekrar       → source=vqr, dim=['makine','vardiya']  ❌
        #
        # Yani kullanıcının makine kırılımı isteyen sorusu, bir daha sorulduğunda
        # SORMADIĞI ikinci kırılımı getiriyor ve her hücredeki sayı değişiyor —
        # sessiz-yanlışın kalıcılaştırılmış hâli, üstelik `source=vqr` rozetiyle.
        #
        # Kök neden "beyan var, kod onu tanımıyor": *tamamlama* demek, önceki mesajın
        # TEK BAŞINA cevaplanamamış olması demektir.
        #
        # ⚠ ÖLÇÜT `route()` DEĞİL, **CEVAPLANABİLİRLİK** (ilk düzeltmem fazla genişti ve
        # iki altın testi düşürdü — kaydı burada duruyor). `route()` bir şekil döndürse
        # bile dönem eksikse ürün *"hangi dönem?"* diye SORAR; yani soru cevaplanmamıştır
        # ve kullanıcının onu tamamlaması GERÇEK bir tamamlamadır:
        #
        #     "renklerin ortalama sapması nedir" → şekil VAR, dönem YOK  → tamamlama ✅
        #     "bu yıl makine bazında oee"        → şekil VAR, dönem VAR  → GENİŞLETME ❌
        #
        # İkisini ayıran şey `needs_period`'dur ve o zaten tek kaynaktır (ADR-0007 K3).
        try:
            _onceki = cube_router.route(prev_q, schema)
        except Exception:
            _log.warning("öğrenme kapısı: önceki turun route()'u başarısız (best-effort)",
                         exc_info=True)
            return None            # fail-closed: emin değilsek ÖĞRENMEYİZ
        if _onceki and not cube_router.needs_period(
                _onceki.get("cube_query") or {}, prev_q_norm):
            return None            # önceki mesaj TEK BAŞINA cevaplanıyordu → tamamlama YOK
        try:
            if vqr.store(prev_q, cq, source="chip_approved"):
                return "chip-onaylı → VQR güncellendi (LLM'siz öğrenme)"
        except Exception:
            _log.warning("chip-onaylı VQR öğrenme başarısız (best-effort)", exc_info=True)
        return None

    # ⚠️ FAZ 0.22 — `migration_trace` BURADA tanımlanır, `if`in İÇİNDE değil.
    # Kök neden (satır satır doğrulandı): tanım `if structural_followup:` bloğunun İÇİNDEYDİ,
    # ama `agent_plan_secimi` dalı (aşağıda, 4b) blok DIŞINDA onu `_capraz_alan_pilotu`'ya
    # geçiriyor → **bayrak `on` VE `structural_followup=False` → `UnboundLocalError`**.
    # Bugün dormant çünkü bayrak `off`; yani *"kota serbest kalınca ölçeriz"* iyimserdi —
    # ölçüm denenseydi ilk taze soruda 500 alınırdı. Kapı:
    # `tests/test_orkestrator.py::test_agent_plan_secimi_yapisal_olmayan_turda_cokmez`.
    migration_trace: list[str] = []

    # 🔴 **FAZ 5.0 — K3 DÜZELTMESİ.** `followup.sinifla()`'nın TEK çağrısı
    # `if structural_followup:` bloğunun **İÇİNDEYDİ** ve `baglam_var=` sabit **`True`**
    # geçiliyordu. İki sonucu vardı ve ikisi de ölçüldü:
    #   (1) İstemci `cube_query` göndermiyorsa (Discovery / ham thread) *"bu neden
    #       böyle?"* · *"normal mi?"* · *"analiz et"* — **hiçbiri sınıflanmıyordu**.
    #       Beş konuşma türü de o thread sınıfında **erişilemezdi**.
    #   (2) `baglam_var` sabit `True` olduğu için `followup.py`'nin *"bağlam-yok"* kuralı
    #       **üretimde hiç ateşlenmiyordu** — yalnız birim testinde yaşıyordu.
    #
    # ⚠ **Çağrı yukarı taşındı, DAVRANIŞ KESİLMEDİ (KAT-2):** sınıflandırma artık her
    # thread sınıfında yapılıyor ama *"cevapsız bir dal, cevaplı bir yolu KESEMEZ"* —
    # ham thread'de konuşma sınıfı bir cevabı **engellemez**, yalnız zincir zaten
    # tükendiğinde daha **isabetli** bir not üretir (aşağıda).
    #
    # 🔴 `baglam_var` **gerçek bağlam durumundan**: yapısal takip **ya da** ham takip.
    # *Sabit bir `True`, bir bayrak değil bir yalandır.* (Çağrının kendisi daha yukarıda,
    # eylem kapısından ÖNCE — bkz. `niyet = followup.sinifla(...)`.)

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
        # DÖNEMSEL KIYAS TAKİPTE (FAZ X) — kimlik asimetrisi kapatılıyor. Mekanizma
        # taze dalda vardı, burada YOKTU; *"geçen yılla kıyasla"* dürüst rette kalıyordu.
        # `deterministic_refine`'dan ÖNCE: kıyas bir düzenleme değil AYRI bir eksendir
        # (refine onu ne tanır ne uygular, kapsam kapısına takılıp zinciri boşa harcar).
        _tk_mode = cube_router.compare_mode(q_norm)
        if _tk_mode and (body.cube_query or {}).get("cube"):
            _tk = _kiyas_cevabi(dict(body.cube_query), _tk_mode, "Takip: dönemsel kıyas")
            if _tk is not None:
                return _tk

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
                soz=_soz.soz("netlestirme.kirilim"),
                suggestions=_dogrulanmis_chipler(labels, schema, en_fazla=10),
                trace=migration_trace + ["Takip: yetenek sorusu → kırılım chip'leri (LLM'siz)"],
            ))

        # ÜÇÜNCÜ SINIF — "CEVAP ÜSTÜNDE KONUŞMA" (Faz G1). Ölçüldü (2 Ağustos 2026):
        # "bu neden böyle?" · "normal mi?" · "ne yapmalıyız?" · "şu düşüş ne?" ·
        # "bunu nasıl iyileştiririz?" · "sence iyi mi?" — ALTISI DA ölü uca çarpıyordu
        # ("Bu takip mesajını önceki raporla ilişkilendiremedim"), biri de anlamsız bir
        # yazım önerisi alıyordu ("bunu" → "gunu").
        #
        # Bu sınıf YENİ SORGU ÜRETMEZ, var olanı AÇAR: mevcut makbuza çapalanır ve
        # ARAÇ ÇAĞIRIR. `deterministic_refine`'dan ÖNCE yakalanmalıdır — aksi halde
        # "neden"/"düşüş" gibi kelimeler onun sözlük eşleşmesine karışır (Faz D3'te
        # "neden arttı" → `bakim.mudahale_eden` sahte eşleşmesi tam buydu).
        # ⚠ `niyet` YUKARIDA hesaplandı (FAZ 5.0) — burada yeniden çağırmak, aynı kuralın
        # ikinci bir sahibini yaratırdı ve iki sahip **ayrışır**.
        if niyet.konusma:
            # GRAFİĞE ÇAPA (Faz G2): kullanıcı bir hücreye işaret ettiyse konuşma O
            # hücrenin üstünde yürür. Çapa bir metin değil KOORDİNATTIR ve burada
            # gerçek bir alt-sorguya çevrilir — "nisandaki sıçrama ne?" sorusu
            # nisanı filtreleyen bir cube_query'ye bağlanır.
            konu_cq, capa_izi = _capayi_uygula(prev_cq, body.anchor, prev_cube_meta)
            resp = _cevap_ustunde_konus(konu_cq, prev_cube_meta, niyet,
                                        migration_trace + capa_izi, body.session_id)
            if resp is not None:
                return _finish(resp)
            # Araç bir şey üretemediyse SESSİZCE düşme: normal zincir devam eder ve
            # kullanıcı en azından bugünkü davranışı alır (gerileme YOK).

        # SAF GÖRÜNÜM DEĞİŞİKLİĞİ ("pasta grafik" · "tablo olarak" · "çizgi grafik").
        #
        # FAZ 0.5'İN ÖLÇTÜĞÜ BULGU (2026-08-03): plan §4.7-1(e)(i) bu vakayı
        # *"`_viz_hint`/`_VIZ_MAP` zaten var ama `deterministic_refine`'ın saf görünüm
        # değişikliğini 'değişti' sayıp saymadığı ÖLÇÜLMEDİ"* diye işaretlemişti.
        # Ölçüldü: **saymıyor.** `deterministic_refine` yapısal bir değişiklik göremediği
        # için `None` dönüyor, zincir tükeniyor ve kullanıcı *"Bu takip mesajını önceki
        # raporla ilişkilendiremedim"* alıyor — yani GRAFİK TİPİ İSTEĞİ TÜM RAPORU
        # SİLİYOR. `gorunum_donusumu` senaryo sınıfı **0/5** ölçüldü.
        #
        # Doğru davranış: rapor AYNEN yeniden verilir, yalnız `view_hint` değişir. Bu
        # `deterministic_refine`'ın kendi `already` (no-op) sözleşmesinin aynısıdır —
        # istek mevcut raporu ONAYLIYOR, değiştirmiyor. `cube_router`'a taşınmadı çünkü
        # `_VIZ_MAP` bir SUNUM sözlüğüdür (router yapı üretir, görünüm üretmez).
        _sadece_gorunum = _viz_hint(q_norm)
        if _sadece_gorunum and prev_cq:
            _kalan = _VIZ_TEMIZ_RE.sub(" ", q_norm).strip()
            if not cube_router._uncovered(_kalan, cube_router._misc_hit_words(_kalan)):
                resp = _answer_from_cube_query(
                    dict(prev_cq), source="cube",
                    trace=migration_trace + [
                        f"Takip: saf görünüm değişikliği → {_sadece_gorunum} "
                        f"(rapor korunur, LLM'siz)"])
                if resp is not None:
                    return resp

        try:
            # 🔴 FAZ 4.3 BORCU — bayrak **çağıranda** çözülür; `deterministic_refine`
            # saf kalır (test edilebilirlik + `lab/` A/B koşumu).
            #
            # Ölçüldü @bu commit (`lab/sharding.py`, `demo-boyahane`, 44 konuşmalık
            # sabit kohort): tur 1 %63,6 → tur 5 **%45,5 → %59,1**, düşüş
            # **−%18,2 → −%4,5**, karar **`kaldi` → `gecti`**.
            refined = cube_router.deterministic_refine(
                prev_cq, q_norm, schema,
                olcu_ekle="olcu_ekleme_takibi" in resolve_for(settings, principal))
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
                note=f"Konu değişti: {prev_label} → {new_label}"
                     f"{cekirdek.grain_uyarisi(prev_cq, switched, schema)}",
                trace=migration_trace + ["Takip: çapraz-cube konu geçişi (LLM'siz)"])
            if resp:
                return resp

        # KONU DEĞİŞİMİ (ÖLÇÜ DE farklı) — cross_cube_dim_switch yalnız AYNI ölçü(ler)i
        # YENİ boyutla taşıyan cube'a geçirir; mesaj hem YENİ boyut hem YENİ ölçü
        # taşıyorsa (ör. OEE raporundayken "kumaş cinsine göre fire oranı") o fonksiyon
        # bilerek None döner. Mesaj tek başına TAM bağımsız bir rapor tanımlıyorsa
        # route() onu zaten sıfır-LLM çözer — deterministik zincirin son, en genel adımı.
        try:
            fresh_route = cube_router.route(
                q_norm, schema,
                liste_kirilimi="liste_niyeti" in resolve_for(settings, principal))
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
            # 🔴 FAZ 5.0 — ZİNCİR ZATEN TÜKENDİ (Discovery'ye de düşülmedi: katalogda
            # kanıt yok). Burada bir yol **kesilmiyor**; yalnız verilecek not, artık
            # bilinen konuşma sınıfıyla **isabetli** hâle geliyor. Kullanıcı *"bu neden
            # böyle?"* diye sorduysa ona *"yeni bir soru olarak sorar mısın"* demek,
            # sorduğu şeyin ne olduğunu **anlamadığımızı** söylemektir — oysa anladık,
            # yalnız **çapalanacak bir rapor** yok.
            if niyet.konusma:
                return _honest_refusal(
                    note=_soz.soz("ret.konusma_capasiz"),
                    soz=_soz.soz("ret.konusma_capasiz"),
                    trace=migration_trace + [
                        f"Takip: konuşma sınıfı ({niyet.tur}) ama çapalanacak rapor YOK "
                        f"→ dürüst ret (FAZ 5.0)"],
                )
            return _honest_refusal(
                note=reason or "Bu takip mesajını önceki raporla ilişkilendiremedim. "
                              "Yeni bir soru olarak sorar mısın?",
                # 🔴 FAZ 5.17 — eski metin bir FORM HATASIYDI. `soz` katalogdan gelir ve
                # *"önce ne anladığını söyle, sonra sor"* şeklindedir; `note` geçmiş
                # kayıtlarla uyum için AYNEN korunur (frontend `soz ?? note` okur).
                soz=_soz.soz("ret.takip_baglanamadi"),
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

    # 4b) ÇAPRAZ-ALAN PİLOTU — FAZ 4 (K3). `Planlayici.sec()`'in TÜKETİCİSİ.
    #
    # ⚠️ **DENETİMDE BULUNDU (canlı tur, 2026-08-03):** `sec()` yazılmış ve 18 testle
    # kilitlenmişti ama **hiçbir yerden çağrılmıyordu** — yani bu oturumda on bir kez
    # eleştirdiğim *"beyan var, TÜKETİCİSİ yok"* sınıfına kendim düşmüştüm. Faz 4'ün
    # kabul ölçütü (*"çapraz-alan pilotu → 2 adımlı kompozisyon"*) karşılanmamıştı.
    #
    # Neden BURADA: bu nokta, deterministik zincirin (route · refine · Intent-JSON)
    # tükendiği ve Discovery'ye (ham SQL, cube sınırlarının ötesinde) düşülmek üzere
    # olduğu yer. MIMARI §9.2'nin yapısal sınırı da tam burada ısırır: bir cube'un ölçüsü
    # + başka cube'un boyutu **tek** CubeQuery'de ifade edilemez — ama **iki adımda**
    # edilebilir. Planlayıcı o iki adımı önerir; **dört kapı** onu denetler.
    if "agent_plan_secimi" in resolve_for(settings, principal):
        _agent = _capraz_alan_pilotu(request, body, q_norm, schema, principal,
                                     migration_trace)
        if _agent is not None:
            return _agent

    # 5) Discovery: sağlayıcı zinciri (failover + kural-tabanlı/dürüst-ret yedeği —
    # app/llm.py, app.state.llm). RAW takip (önceki tur yapısal cube_query ÜRETMEMİŞSE),
    # bağımsız-ama-Intent-path'in kapsamadığı sorular VE (1 Ağustos 2026'dan beri) kendi
    # deterministik+LLM zinciri TÜKENMİŞ bir YAPISAL takip buraya ulaşır (§3'ün son çaresi —
    # `raw_followup` bu durumda hâlâ False, `_run_discovery` bu yüzden taze `generate_sql`
    # üretir, stale prev_sql'e çapalamaz).
    # FAZ F2 — YOL SINIRI: Discovery ham SQL yazar; kullanıcı "yalnız küp" dediyse buraya
    # HİÇ gelinmez. Sessizce boş dönmek yerine SINIRIN KENDİSİ söylenir — aksi hâlde
    # kullanıcı kendi ayarını unutup ürünü yeteneksiz sanır.
    if not _yol_izinli("discovery"):
        return _finish(AskResponse(
            question=body.question, source=None, note=_yol_siniri_notu("discovery"),
            trace=["Yol sınırı: Discovery (ham SQL) kullanıcı tercihiyle KAPALI"],
        ))

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
        motor = katman_b.sarmala(service, request)
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
            planned = motor.dry_plan(wren_sql)
        except katman_b.ModelErisimReddi as red:
            return _honest_refusal(note=katman_b.RED_NOTU, trace=trace + [str(red)])
        except Exception as e:
            trace.append(f"dry_plan hatası → kendi kendini onarma: {e}")
            if on_step:
                on_step(list(trace))
            try:
                wren_sql = llm.repair(body.question, prompt_schema, wren_sql, str(e))
                planned = motor.dry_plan(wren_sql)
            except Exception as exc2:
                _log.warning("Discovery self-healing başarısız", exc_info=True)
                return _honest_refusal(
                    note="Bu soru için güvenilir bir sorgu üretemedim.",
                    soz=_soz.soz("ret.sorgu_uretilemedi"),
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
            result = motor.query(wren_sql, limit=limit)
        except Exception as e:
            trace.append(f"çalıştırma hatası → kendi kendini onarma: {e}")
            if on_step:
                on_step(list(trace))
            try:
                wren_sql = llm.repair(body.question, prompt_schema, wren_sql, str(e))
                planned = motor.dry_plan(wren_sql)
                result = motor.query(wren_sql, limit=limit)
            except Exception as exc2:
                _log.warning("Discovery çalıştırma + self-healing başarısız", exc_info=True)
                return _honest_refusal(
                    note="Bu soru için güvenilir bir sorgu üretemedim.",
                    soz=_soz.soz("ret.sorgu_uretilemedi"),
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
                          {"wren_sql": wren_sql, "mdl_version": motor.mdl_version},
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
        # FAZ 1 (K1) — UÇURUMU KALDIR. Buraya kadar cevap `cube_query=None` ile gidiyordu
        # ve `seal()`'in ÜÇ kapısı da (chip · aksiyon · köken) kapanıyordu. Sonuçtan
        # oturum-scoped bir ad-hoc cube türetilir; YAPI açılır, ROZET dürüst kalır
        # (`source` hâlâ `llm:*`, `explain.confidence` hâlâ None — `_build_explain` güveni
        # `source`'tan okur, `cube_query`'nin varlığından DEĞİL).
        adhoc = _adhoc_kur(request, body, result, wren_sql, limit)
        if adhoc:
            resp.cube_query = adhoc["cube_query"]
            trace.append(f"ad-hoc cube kuruldu ({adhoc['info']['row_count']} satır, "
                         f"dondurulmuş görünüm) — yapı açıldı, rozet llm:* kaldı")
            return _finish(_attach_viz(resp, result, adhoc["cube_query"]))
        return _finish(_attach_viz(resp, result))

    # Faz 4.1 (31 Temmuz 2026) — bayrak KAPALIYKEN (varsayılan, tüm mevcut testler/tenant'lar)
    # davranış BİREBİR eskisiyle aynı: Discovery senkron çalışır, /ask onun sonucunu döner.
    # Yalnız `ask_async_discovery` açık tenant'larda Discovery'nin bu kendi kendine en yavaş
    # (LLM+self-healing) adımı arka-plan işine kuyruklanır (dış yol haritası 0.1 karşılığı).
    if "ask_async_discovery" not in resolve_for(settings, principal):
        return _run_discovery()
    return _queue_discovery_job(request, body, principal, _run_discovery)


@router.delete("/ask/jobs/{job_id}",
               dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_job_iptal(job_id: str, request: Request) -> dict:
    """FAZ 1.12 — **İNSAN GÖZETİMİ / DURDURMA** (AI Act Md.14).

    🔴 **Md.14 bir DURDURMA DÜĞMESİ istiyor** ve `/ask/jobs` bugüne kadar yalnız
    **okunabiliyordu**: başlattığınız uzun bir Discovery sorgusunu **durduramıyordunuz**.
    *Durdurulamayan bir otomasyon, üzerinde insan denetimi olmayan bir otomasyondur.*

    ⚠ **İptal, işi ÖLDÜRMEZ — sonucu YAYIMLATMAZ** (gerekçe: `app/ask_jobs.py`). Karar ve
    yazma orada; burada kalan yalnız **uç kaydı** — durumu okuyan tek yer `_job_durum_oku`
    (tenant izolasyonunu **o** uygular), ikinci bir okuyucu izolasyonun ikinci sahibi olurdu.
    """
    return ask_jobs.iptal_et(job_id, _job_durum_oku(job_id, request)[0])


@router.get("/ask/jobs/{job_id}", response_model=AskJobStatus,
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_job_status(job_id: str, request: Request) -> AskJobStatus:
    """Faz 4.1 — arka-plan Discovery işinin durumu (istemci bunu poll eder). Tamamlanmışsa
    `response` tam bir AskResponse'tur — client bunu normal /ask cevabı gibi işler (job_id
    alanı boş kalır, tekrar poll edilmez)."""
    durum, trace, resp, hata, soru = _job_durum_oku(job_id, request)
    return AskJobStatus(id=job_id, status=durum, question=soru,
                        response=resp, error=hata, trace=trace)


#: FAZ S — akış sabitleri. Poll ucunun `ASK_JOB_POLL_MS=1500` / `MAX_POLLS=240`
#: sınırlarıyla AYNI disiplin: akış da sonsuz açık bağlantı bırakmaz.
_AKIS_ARALIK_SANIYE = 0.25      # adım doğduğu an ≈ anında iletilir (poll'da 1,5 sn)
_AKIS_AZAMI_SANIYE = 360.0      # 6 dk — poll ucunun üst sınırıyla aynı


def _job_durum_oku(job_id: str, request: Request) -> tuple[str, list[str], "AskResponse | None", str | None, str | None]:
    """Bir işin ANLIK durumu: (status, trace, response, error, question).

    `GET /ask/jobs/{id}` ile akış ucunun **ORTAK** okuyucusu — iki uç aynı satırı iki
    farklı biçimde okusaydı zamanla ayrışırlardı (tenant izolasyonu iki yerde yazılırdı,
    biri unutulurdu). Akış bir TAŞIMADIR, ikinci bir gerçeklik değil.
    """
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
        # `question` iş satırından gelir: iş HENÜZ bitmemişken de dolu olmalı
        # (poll ucunun eski davranışı — bekleyen işte soru gösteriliyordu).
        return job.status, trace, resp, job.error, job.question


@router.get("/ask/jobs/{job_id}/stream",
            dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_job_stream(job_id: str, request: Request):
    """FAZ S — AŞAMA AKIŞI (SSE biçimi). *"Ne yapıyor?"* sorusunun anlık cevabı.

    ## Neden bu uç var — ve neden İKİNCİ BİR GERÇEKLİK DEĞİL

    Ölçüldü (canlı): deterministik yol ~100–800 ms (akış gereksiz), **LLM yolu 2,8–5,5 sn**
    — sessizlik tam orada. Biriken `AskJob.trace` bu aşamaları ZATEN taşıyor; eksik olan
    onu **anında** iletmekti. Poll 1,5 sn'de bir bakıyor; akış adımı doğduğu an veriyor.

    Bu uç yeni bir olay hattı UYDURMAZ: `_job_durum_oku` ile poll ucunun **aynı** satırını
    okur. Aksi hâlde iki farklı "ne yapıyor" anlatısı doğar ve biri yalan söylemeye başlar.

    ## Neden `EventSource` DEĞİL — güvenlik değişmezi

    `EventSource` **Authorization başlığı gönderemez**; tek yolu token'ı URL'e koymaktır ve
    o token sunucu loglarına/tarayıcı geçmişine sızar. Bu deponun açık kuralı: *"access
    token memory'de, localStorage'a ASLA"* (frontend/CLAUDE.md). Bu yüzden **SSE BİÇİMİ**
    korunur ama taşıma `fetch` + `ReadableStream`'dir: Bearer başlığı aynen çalışır, hiçbir
    değişmez gevşetilmez. Format aynı olduğu için ileride gerçek bir `EventSource`
    tüketicisi de eklenebilir — karar geri alınabilir kalır.

    ## Sonlanma

    Akış `completed`/`failed` olayıyla KAPANIR. Üst sınır: iş bitmezse `_AKIS_AZAMI_SANIYE`
    sonunda `timeout` olayıyla kapanır — sonsuz açık bağlantı bırakmaz (poll ucunun
    `ASK_JOB_MAX_POLLS` sınırıyla aynı disiplin).
    """
    from fastapi.responses import StreamingResponse

    # ⚠ DOĞRULAMA AKIŞTAN ÖNCE. `StreamingResponse` yanıtı üretici çalışmadan BAŞLATIR;
    # `HTTPException`'ı üreticinin içinde atmak *"response already started"* üretir ve
    # istemci temiz bir 400/404 yerine **bozuk bir akış** alır (testle yakalandı).
    # Bu çağrı kimlik/varlık/tenant kontrolünün üçünü de yapar.
    _job_durum_oku(job_id, request)

    def _olay(ad: str, veri: dict) -> str:
        return f"event: {ad}\ndata: {json.dumps(veri, ensure_ascii=False)}\n\n"

    def _uret():
        gonderilen = 0
        gecen = 0.0
        while gecen < _AKIS_AZAMI_SANIYE:
            durum, trace, resp, hata, _ = _job_durum_oku(job_id, request)
            # YALNIZ YENİ adımlar gönderilir — istemci listeyi biriktirir, tam listeyi
            # her turda yeniden yollamak akışı bir poll'a çevirirdi.
            for adim in trace[gonderilen:]:
                yield _olay("adim", {"metin": adim})
            gonderilen = max(gonderilen, len(trace))
            if durum == "completed":
                yield _olay("tamam", {"response": json.loads(resp.model_dump_json())
                                      if resp else None})
                return
            if durum == "failed":
                yield _olay("hata", {"error": hata or "bilinmeyen hata"})
                return
            # FAZ 1.12 — DURDURMA `hata` DEĞİLDİR. Ayrı olay: aksi hâlde kullanıcı kendi
            # durdurduğu iş için "bir sorun oluştu" görürdü; ve dalı hiç eklememek akışı
            # 6 dk açık bırakırdı (durdurma düğmesi UI'yi DÖNER hâlde bırakırdı).
            if durum == ask_jobs.DURUM_IPTAL:
                yield _olay("iptal", {"job_id": job_id})
                return
            _time.sleep(_AKIS_ARALIK_SANIYE)
            gecen += _AKIS_ARALIK_SANIYE
        yield _olay("zaman_asimi", {"saniye": _AKIS_AZAMI_SANIYE})

    return StreamingResponse(_uret(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        # Ters vekil tamponlaması akışı ANLAMSIZ kılar (her şey sonda tek parça gelir).
        "X-Accel-Buffering": "no",
    })


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
    """FAZ 9.1 — GİZLİLİK MÜHRÜ. Gövde SARMALANIYOR, sekiz dönüş noktası tek tek
    yamanmıyor: yamamak, dokuzuncu dönüş noktasını ekleyen kişinin unutmasına açık
    kalırdı — tam olarak bu kusurun doğuş biçimi (`raw` dalı düzeltilmiş, kardeşleri
    unutulmuştu). Sarmal, **yeni dallar dahil** hepsini kapsar."""
    resp = _ask_drill_govde(request, body)
    try:
        from app.pii import muhurle

        muhurle(resp, request, getattr(request.state, "principal", None),
                ad=f"drill:{(body.cube_query or {}).get('cube') or '-'}")
    except Exception:  # noqa: BLE001 — mühür cevabı DÜŞÜRMEZ ama sessiz de kalmaz
        _log.warning("drill gizlilik mührü uygulanamadı", exc_info=True)
    return resp


def _ask_drill_govde(request: Request, body: DrillRequest) -> DrillResponse:
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

    # FAZ 1 (K1) — ad-hoc cube'da drill DONDURULMUŞ görünüm üzerinde çalışır: SQL'in
    # SEÇTİĞİ kolonlar boyut olur, seçmediği eklenemez (planın açıkça kaydettiği sınır —
    # "tam kırılım değil, dondurulmuş görünüm üzerinde tam etkileşim").
    service = _adhoc_service_for(request, body.cube_query) or \
        _service_for(request, body.session_id)
    settings = get_settings()
    schema = service.schema()
    cubes_by_name = {c.get("name"): c for c in (schema.get("cubes") or [])}
    cube_meta = cubes_by_name.get(body.cube_query.get("cube"))
    if cube_meta is None:
        raise HTTPException(status_code=400, detail="Cube bulunamadı (şema değişmiş olabilir).")
    if body.cube_query.get("kirpilmis"):
        # KIRPILMIŞ GÖRÜNÜMDE DRILL YOK (aynı gerekçe `answer._attach_next_steps`'te):
        # eksik veriden hesaplanmış bir kök-neden analizi, analizsizlikten kötüdür.
        return DrillResponse(
            formula_explanation="Bu sonuç satır tavanına ulaştı (kırpılmış görünüm) — "
                                "üzerinden kök-neden dallanması sunulmuyor, çünkü sayılar "
                                "eksik veriden hesaplanırdı. Soruyu daraltıp tekrar sor.",
        )

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
    """FAZ 9.1 — GİZLİLİK MÜHRÜ (bkz. `ask_drill`). `raporlar[].segment` bir BOYUT
    DEĞERİDİR: `musteri`/`operator` kırılımında doğrudan kişi adıdır."""
    resp = _ask_contribution_govde(request, body)
    try:
        from app.pii import muhurle

        muhurle(resp, request, getattr(request.state, "principal", None),
                ad=f"contribution:{(body.cube_query or {}).get('cube') or '-'}")
    except Exception:  # noqa: BLE001
        _log.warning("contribution gizlilik mührü uygulanamadı", exc_info=True)
    return resp


def _ask_contribution_govde(request: Request,
                            body: ContributionRequest) -> ContributionResponse:
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

    cq = dict(body.cube_query or {})
    if not cq.get("cube"):
        return ContributionResponse(note="Bu sonuç yapısal bir cube_query taşımıyor "
                                         "(Discovery/ham SQL) — katkı ayrıştırması yapılamaz.")
    service = _service_for(request, body.session_id)

    # FAZ F3 — GÖVDE `app/contribution.py::arastir`'DA. Bu router artık yalnız HTTP
    # kaygılarını çözer (servis çözümü · makbuz yazıcısı · hata kodu). Ayırmanın ölçülen
    # sebebi: gövde router'a yapışıkken (a) planlayıcıya `dis_adim(..., gated: false)`
    # diye İTİRAF olarak giriyordu — kayıtlı bir araç değildi, (b) `request` olmayan arka
    # plan işleri (zamanlanmış uyarılar) onu HİÇ çağıramıyordu.
    out = contrib.arastir(
        service, service.schema(), cq,
        mode=body.mode, kind=body.kind, max_dimensions=body.max_dimensions,
        kaydet=lambda baslik, acq, sql, res: _drill_record_contract(
            request, service, body.session_id, baslik, acq, sql, res))
    if out.get("hata") == "cube_yok":
        raise HTTPException(status_code=400, detail="Cube bulunamadı (şema değişmiş olabilir).")

    return ContributionResponse(
        measure=out.get("measure"), mode=out.get("mode") or body.mode,
        kind=out.get("kind") or body.kind, note=out.get("note"),
        taranmayan_boyut=out.get("taranmayan_boyut") or 0,
        taranmayan_adlar=out.get("taranmayan_adlar") or [],
        contract_ids=out.get("contract_ids") or [],
        raporlar=[ContributionReport(**r) for r in (out.get("raporlar") or [])],
        pvm_raporlar=[PvmReport(**_pvm_seleli(r)) for r in (out.get("pvm_raporlar") or [])])


def _pvm_seleli(r: dict) -> dict:
    """PVM raporuna ŞELALE grafiğini ekler (Faz I2) — matematiği var, görseli yoktu.

    Karar `viz.waterfall_spec`'te ve **kapılıdır**: bileşenler toplamı net değişime
    varmıyorsa `None` döner ve frontend tabloya düşer. PVM artıksız olduğu için normalde
    geçer; geçmediği gün bu bir **bozulma sinyalidir** ve grafiğin susması doğrudur.

    Başlangıç `0` seçildi: PVM bir DEĞİŞİMİN ayrışmasıdır (seviyenin değil). Şelale
    sıfırdan başlayıp net değişime varır — okuyan "önceki değer neydi" diye sormaz,
    "değişim neden bu kadar" diye sorar.
    """
    spec = viz.waterfall_spec(
        baslangic=0.0,
        bilesenler=[("fiyat", r.get("fiyat_etkisi") or 0.0),
                    ("miktar", r.get("miktar_etkisi") or 0.0),
                    ("birleşik", r.get("birlesik_etki") or 0.0)],
        bitis=r.get("net_degisim") or 0.0,
    )
    return {**r, "viz": spec}


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

