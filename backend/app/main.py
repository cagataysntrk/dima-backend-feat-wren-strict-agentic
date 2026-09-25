"""FastAPI application: HTTP bridge over the Wren semantic SQL engine."""

from __future__ import annotations

import threading
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth import router as auth_router
from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.llm import build_generator
from app.routers import ask, ask_v2, health, query
from app.routers import manager_lab as manager_lab_router
from app.routers import connections as connections_router
from app.routers import contracts as contracts_router
from app.routers import conversations as conversations_router
from app.routers import dashboards as dashboards_router
from app.routers import decisions as decisions_router
from app.routers import eylem as eylem_router
from app.routers import measures as measures_router
from app.routers import schedules as schedules_router
from app.routers import stats as stats_router
from app.routers import tercihler as tercihler_router
from app.vqr import VQR
from app.wren_service import WrenService


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.logging_setup import configure_logging, get_logger

    configure_logging()  # system/app log (ADR-0020) — sessiz-yutma yerine warning
    _log = get_logger("main")
    settings = get_settings()
    # Control-plane (auth) DB: lokal SQLite'ı hazırla; Postgres'te Alembic devralır (ADR-0015).
    from control_plane.audit import replay_spool
    from control_plane.bootstrap import ensure_bootstrap_superadmin
    from control_plane import models as _control_plane_models  # noqa: F401
    from control_plane.db import init_db

    # Control-plane şeması (SQLite'ta oluştur; Postgres'te Alembic sahibi) + superadmin seed.
    init_db()
    replay_spool()  # DB-down sırasında spool'lanan bekleyen audit'leri DB'ye boşalt
    from app.contracts import replay_spool as replay_contract_spool
    replay_contract_spool()  # bekleyen contract kanıtlarını DB'ye boşalt (audit deseni)
    from app.routers.ask import recover_stale_ask_jobs
    recover_stale_ask_jobs()  # Faz 4.1: önceki çalıştırmadan yarım kalan AskJob'ları temizle
    ensure_bootstrap_superadmin()
    # ADR-0005: şirket ⊕ sektör paketi ⊕ konu modülleri → wren-project (derlenmiş) + mdl.
    # Önce TenantConfig materializer'ı: admin panelden yazılan sektör/modül seçimi
    # company.yml'e iner (DB kazanır) — compose bu dosyayı okur.
    from app.compose import compose_and_build
    from app.materialize import materialize_tenant_configs

    materialize_tenant_configs(settings)
    compose_and_build(settings)
    app.state.wren = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
        company_slug=settings.company,
    )
    _log.info("Wren motoru hazır: datasource=%s şirket=%s proje=%s",
              settings.datasource, settings.company, settings.resolved_project_dir())
    # 🔴 `A1` — KASET. Ortam değişkeni yoksa **dokunmaz** (`KURAL B`: bayraksız
    # davranış birebir bugünkü). Raporun `§4i` kararı: kapının yeni merkezi kasetli
    # garson korpusudur ve o, `/ask`'in TAM yolundan koşar — yani route'u da koşturur.
    # Sağlayıcıyı burada sarmak, ölçümün ürünün kendi hattından geçmesini garanti eder;
    # ayrı bir "test hattı" kurmak, ölçtüğü şeyi ölçmeyen bir alet üretirdi.
    from app.kaset import belki_sar

    app.state.llm = belki_sar(build_generator(settings))
    # BAŞLANGIÇTA hangi LLM sağlayıcı(lar)ının GERÇEKTEN aktif olduğunu net biçimde logla
    # (1 Ağustos 2026, kullanıcı talebi: "llm mi patladı" sorusunun İLK adımı — hangi
    # sağlayıcı yapılandırılmış OLMALI ki sonraki llm.py loglarıyla karşılaştırılabilsin).
    _gens = getattr(app.state.llm, "_gens", None)
    if _gens is not None:
        _providers = [getattr(g, "_provider", type(g).__name__) for g in _gens]
        _log.info("LLM sağlayıcı zinciri (failover sırasıyla): %s", _providers or "(BOŞ)")
    else:
        _log.info("LLM sağlayıcı: %s", type(app.state.llm).__name__)
    # Çok-şirketli runtime v1: varsayılan-dışı tenant'ların projeleri talep üzerine
    # derlenir (require_company → registry). Materializer değişen tenant'ı düşürür.
    from app.company_registry import CompanyRegistry

    app.state.company_registry = CompanyRegistry(settings)
    # Verified Query Repository (A#4): onaylı soru→CubeQuery çiftleri. Postgres'te
    # (verified_query, şirket kapsamlı) — eski JSONL redeploy'da siliniyordu (ADR-0005/0008).
    app.state.vqr = VQR(settings.company)

    # Query Contract deposu (ADR-0010) — kanıt TEK-KAYNAK DB'de (contract_log).
    from app.contracts import ContractStore

    app.state.contracts = ContractStore()

    # P14 Research state is durable in the control-plane DB. When configured,
    # ordinary Research uses principal-scoped Metabot + direct Metabase execution.
    from app.v3.research_product import ResearchAskOrchestrator
    from app.v3.research_store import ResearchSessionStore

    research_store = ResearchSessionStore()
    app.state.research_product = ResearchAskOrchestrator(store=research_store)
    if settings.metabase_native_base_url.strip():
        from app.v3.research_native_gateway import (
            NativeResearchMaterialExecutor,
            NativeSubjectSessionProvider,
        )
        from app.v3.substrate.metabase.native_models import NativeEngineIdentity

        native_identity = NativeEngineIdentity(
            engine_sha=settings.metabase_engine_sha,
            upstream_base_sha=settings.metabase_engine_upstream_sha,
            runtime_tag=settings.metabase_engine_runtime_tag,
            runtime_image_digest=settings.metabase_engine_image_digest,
            build_identity=settings.metabase_engine_build_identity,
            runtime_image_identity=settings.metabase_engine_image_identity,
        )
        native_subjects = NativeSubjectSessionProvider(
            base_url=settings.metabase_native_base_url,
            expected_identity=native_identity,
        )
        app.state.research_product.configure_native_runtime(
            bridge_factory=native_subjects,
            material_executor=NativeResearchMaterialExecutor(
                subject_provider=native_subjects,
                store=research_store,
                expected_identity=native_identity,
            ),
        )

    # Zamanlanmış raporlar (ADR-0011): tanım + koşum durumu (last_run) + bildirim HEPSİ
    # tek-kaynak DB'de (schedule_definition + notification_log) — dosya-state yok (double-fire fix).
    from app.schedules import ScheduleStore, run_due

    app.state.schedules = ScheduleStore(settings.company)
    if settings.scheduler_enabled:
        from app.materialize import materialize_and_recompose

        def _scheduler_loop():
            import time

            while True:
                time.sleep(60)
                try:
                    run_due(app.state)
                except Exception:
                    # ÖNCEDEN `except Exception: pass` — TAMAMEN SESSİZ, ADR-0020'nin kendi
                    # "sessiz yutma yok" ilkesini ihlal ediyordu (1 Ağustos 2026 log-görünürlük
                    # denetiminde bulundu). Davranış AYNI (döngü devam eder, zamanlanmış görev
                    # bir sonraki turda tekrar denenir) — yalnız artık İZ bırakıyor.
                    _log.warning("scheduler: run_due döngü hatası", exc_info=True)
                try:
                    # FAZ 1.10 — ESKALASYON. 🔴 YENİ CRON YOK: değerlendirici MEVCUT
                    # 60 sn döngüsüne bindi. İkinci bir zamanlayıcı, iki ayrı "şimdi saat
                    # kaç" sahibi yaratırdı ve ikisi kaydığında hangi kuralın ne zaman
                    # koştuğu BİLİNEMEZDİ.
                    from app.eskalasyon import dongude_degerlendir

                    dongude_degerlendir(app.state)
                except Exception:
                    _log.warning("scheduler: eskalasyon döngü hatası", exc_info=True)
                try:
                    # Admin panelden gelen tenant sektör/modül değişikliği ≤60 sn'de
                    # diske iner; aktif şirketse yeniden derlenir (TenantConfig).
                    materialize_and_recompose(app.state, settings)
                except Exception:
                    # ÖNCEDEN çıplak `print(..., file=sys.stderr)` — yapılandırılmış
                    # `dima.*` log ağacının DIŞINDA kalıyordu (log seviyesi/format/timestamp
                    # yok). Aynı hata, artık aynı yapılandırılmış logger üzerinden.
                    _log.warning("scheduler: materialize_and_recompose döngü hatası", exc_info=True)

        threading.Thread(target=_scheduler_loop, daemon=True).start()

    # SOĞUK BAŞLANGIÇ ISITMA (arka plan): ilk soru 12sn beklemesin — şema zenginleştirme
    # (kategorik değer probu) ve e5 embedder yüklemesi startup'ta paralel başlar.
    def _warm(fn):
        threading.Thread(target=fn, daemon=True).start()

    _warm(app.state.wren.schema)
    from app.vqr import _embedder

    def _oneri_indeksi() -> None:
        """🔴 **ÖLÇÜLMÜŞ ÜRÜN KUSURU** (2026-08-13): `§18.7` çok görünümlü temsili
        erişimi `%68,4 → %89,5` çıkardı, ama **ilk isteği `1,5 sn → 24,8 sn`** yaptı
        (534 görünüm gömülüyor). Ilık yol tabanda kaldı (`p95 53,88 ms`, eşik 300) —
        yani **kapı yeşildi ve kusuru göremiyordu** 🅖: p95 ılık dağılımın ölçüsüdür,
        ilk isteği hiç saymaz. Ama o ilk istek **bir kullanıcının** ilk tuşudur.

        🔴 **SIRA ZORUNLU — VE İLK YAZIMIM BUNU YARIŞA BIRAKTI (ölçüldü, canlıda).**
        Gömücü ve indeks **ayrı** `_warm(...)` iş parçacıklarına verilmişti. Sonuç,
        tazelenen kabın ilk kütük satırında göründü:

            dima.main: öneri indeksi: gömücü yok → ısıtma atlandı (leksik yol)

        Oysa gömücü **yükleniyordu**. Sebep `vqr.py:39`'da yazılı ve bilinçli bir
        karardır: `_embedder()` yükleme kilidini **başka bir iş parçacığı tutuyorsa
        beklemeden `None` döner** (*«bir istek 20 sn asılmasın»*). Yani benim iş
        parçacığım **her zaman kaybediyordu** — ısıtma koşuyor, log basıyor ve
        **hiçbir şey ısıtmıyordu** 🅯.

        ⊙ Çözüm eşzamanlılık eklemek değil, **çıkarmak**: gömücü ve indeks artık
        **tek** zincirde. `_embedder()` burada kilidi kendisi alır ve yükler; `ara()`
        ondan sonra çağrılır. Toplam süre aynı, yarış **yapısal olarak** yok ㊴.

        ⚠ Ve kusuru gösteren şey ADR-0020'ydi: kütüğe *«atlandı»* yazdığı için
        görülebildi. Sessiz bir `return` olsaydı, ısıtma **var sanılırdı**.

        ⚠ **Isıtılan şey VARSAYILAN projenin indeksidir** ㊴🅖: şema istek başına
        (tenant'a göre) çözülür ve başka bir tenant'ın indeksi **hâlâ ilk istekte**
        kurulur. Bu bir eksik ve **gizlenmiyor**: çok kiracılı ısıtma, tenant listesini
        startup'ta okumayı gerektirir — bu uçların değil, kayıt katmanının işidir ve
        ölçülmeden yapılmaz. *Tek kiracıda kusur kapanır, çok kiracıda küçülür.*

        ⚠ `except`: ısıtma bir **kolaylık**tır, bir ön koşul değil. Düşerse uygulama
        yine açılır ve indeks ilk istekte kurulur — yani en kötü hâl **bugünkü hâldir**.
        """
        try:
            if _embedder() is None:
                _log.info("öneri indeksi: gömücü yok → ısıtma atlandı (leksik yol)")
                return
            from app import oneri

            t0 = time.perf_counter()
            # 🔴 `§46` — `ara()` DEĞİL `isit()`: inşa hakkı **yalnız** ısıtmanındır.
            # Ölçüldü (canlı): ısınma **48,7 sn** sürüyor ve o pencerede gelen ilk istek
            # indeksi kendisi kurmaya kalkıp kullanıcıyı **44 sn** bekletiyordu — aynı iş
            # iki kez. Artık istek yolu soğuk indekste **leksik** cevap verir.
            _durum = oneri.isit(app.state.wren.schema())
            _log.info("öneri indeksi ısındı: %.0f ms (durum=%s)",
                      (time.perf_counter() - t0) * 1000.0, _durum.get("durum"))
        except Exception:                                  # noqa: BLE001
            # ADR-0020: sessiz yutma yok — ısıtma düşerse **nedeni** görünür.
            _log.warning("öneri indeksi ısıtılamadı → ilk istek soğuk kalacak",
                         exc_info=True)

    _warm(_oneri_indeksi)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="dima-backend",
        version=__version__,
        description="Wren (dima) semantic SQL engine over HTTP — NL→SQL, validate, execute.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Public: health + auth (login/refresh/logout). Diğer her router korumalıdır —
    # geçerli Bearer access token olmadan hiçbir veri ucu çalışmaz ("dev bypass" YOK).
    app.include_router(health.router)
    app.include_router(auth_router.router)
    _protected = [Depends(get_current_principal)]
    from app.routers import metrics

    app.include_router(metrics.router, dependencies=_protected)
    app.include_router(query.router, dependencies=_protected)
    app.include_router(ask.router, dependencies=_protected)
    # Dima V2 greenfield island. Route owns its query permission + company binding;
    # the feature flag remains default-off until Day 0/1 gates are proven.
    app.include_router(ask_v2.router)
    app.include_router(manager_lab_router.router)
    app.include_router(contracts_router.router, dependencies=_protected)
    # FAZ 1.12 — AI Act Md.13: denetleyici-okunabilir kayıt ihracı.
    from app.routers import audit_export as _audit_export

    app.include_router(_audit_export.router, dependencies=_protected)
    app.include_router(schedules_router.router, dependencies=_protected)
    app.include_router(conversations_router.router, dependencies=_protected)
    app.include_router(dashboards_router.router, dependencies=_protected)
    app.include_router(measures_router.router, dependencies=_protected)
    app.include_router(connections_router.router, dependencies=_protected)
    app.include_router(stats_router.router, dependencies=_protected)
    app.include_router(decisions_router.router, dependencies=_protected)
    # FAZ H — onaylı yazma: /ask/eylem (öneri ONAY ucu). Yazma yetkisi burada
    # AÇILMAZ, yalnız var olan uçlara yetkisi yeniden doğrulanmış bir kapı olur.
    app.include_router(eylem_router.router, dependencies=_protected)
    # FAZ E — kalıcı sunum tercihi: OKUMA/SİLME ucu. Yazma burada YOK;
    # tercih yazmak /ask/eylem onay kademesinden geçer (Faz H değişmezi).
    app.include_router(tercihler_router.router, dependencies=_protected)
    # FAZ 5.9b — bildirim tercihleri. `NotificationPreference` YETİM bir tabloydu
    # (0 satır, router yok): kullanıcı bir kategoriyi kapatabileceğini sanıyordu ama
    # onu yazacağı hiçbir yüzey yoktu. *Beyan edilmiş ama yazılamayan bir tercih,
    # verilmemiş bir sözden kötüdür.*
    from app.routers import bildirim_tercihleri as _btercih

    app.include_router(_btercih.router, dependencies=_protected)
    # FAZ 5.2 — paylaşım (KURUM İÇİ). ⚠ İlk tasarımım `GET /share/{token}`'ı KİMLİKSİZ
    # yapıyordu; iki yerden yanlıştı: (1) *"Auth HER ZAMAN zorunlu"* değişmezini delerdi,
    # (2) A tenant'ının token'ını B tenant'ından biri açabilirdi — imza token'ın
    # GERÇEKLİĞİNİ kanıtlar, okuyanın HAKKINI değil. Uç artık korumalı ve token'daki
    # tenant okuyanınkiyle eşleşmek zorunda.
    from app.routers import paylasim as _paylasim

    app.include_router(_paylasim.router, dependencies=_protected)
    # FAZ 4.5 — MCP yüzeyi. 🔴 Ayrı bir YOL DEĞİL, bir ÇEVİRİ: çağrı
    # `Planlayici.calistir()`'in aynı dört kapısından geçer ve aynı makbuzu üretir.
    # Bayrak kapalıyken uçlar 404 döner; HTTP yolunda tek bayt değişmez (KURAL B).
    from app.routers import mcp as _mcp

    app.include_router(_mcp.router, dependencies=_protected)
    # 🔴 FAZ 6.1 — yazarken-ara ucu. Motor `app/oneri.py`; yetki süzmesi **motorda**
    # ve **sıralamadan önce** (Katman B allowlist'i) — bir öneri listesi envanterdir.
    from app.routers import oneri as _oneri

    app.include_router(_oneri.router, dependencies=_protected)
    return app


app = create_app()
