"""FastAPI application: HTTP bridge over the Wren semantic SQL engine."""

from __future__ import annotations

import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth import router as auth_router
from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.llm import build_generator
from app.routers import ask, health, query
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

    _warm(_embedder)
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
