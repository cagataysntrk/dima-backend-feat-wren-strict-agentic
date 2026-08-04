"""Çok-şirketli runtime v1 (ADR-0016 evrimi): istekteki tenant'a göre WrenService.

Süreç, varsayılan şirketi (settings.company) startup'ta yükler (app.state.wren);
DİĞER tenant'ların projesi bu registry'de TALEP ÜZERİNE derlenir ve önbelleklenir:
compose+build → demo/wren-projects/<slug>/ (gitignore'lu türetilmiş çıktı),
datasource şirketin wren_project.yml'inden, bağlantı bilgisi control-plane
DbConnection'ından (sır AES-256-GCM ile çözülür — KEK artık veri düzleminde de
gereklidir; sorgu icrası burada olur).

Materializer bir tenant'ın config'ini değiştirdiğinde ilgili giriş düşürülür
(sonraki istekte tazeden derlenir).
"""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import yaml


class CompanyRegistry:
    def __init__(self, settings):
        self.settings = settings
        self._services: dict[str, object] = {}
        self._vqrs: dict[str, object] = {}
        self._lock = threading.Lock()
        # NOT: build kilitleri artık BURADA DEĞİL — `app.compose.build_lock_for()` süreç
        # genelinde per-dizin tek kilit tutar. Registry'ye özel bir kayıt bırakmak, aynı
        # ağaca registry-dışından (compose_and_build) yazan yolları korumasız bırakıyordu.

    def _base(self) -> Path:
        return self.settings.resolved_project_dir().parent  # .../demo

    def has_company(self, slug: str) -> bool:
        return (self._base() / "companies" / slug / "company.yml").exists()

    def service_for(self, slug: str):
        with self._lock:
            svc = self._services.get(slug)
            if svc is not None:
                return svc
        from app.compose import build, build_lock_for, compose
        from app.wren_service import WrenService

        # Per-DİZİN BUILD kilidi: aynı çıktı ağacına AYNI ANDA birden çok thread compose
        # etmesin (canlı 2026-07-25: eş-zamanlı compose aynı wren-projects/<slug>'a yazıp
        # rmtree'yi "Directory not empty" ile bozuyor → kısmi/stale proje, türev view/KPI
        # eksik). 2 Ağustos 2026: kilit registry'ye ÖZEL olmaktan çıkıp `app.compose`'a
        # taşındı — `compose_and_build()` (main lifespan / materializer scheduler /
        # measures onayı) registry'den GEÇMİYOR ve kendi kilidi YOKTU, dolayısıyla
        # varsayılan şirket için koruma fiilen mevcut değildi.
        out = self._base() / "wren-projects" / slug
        build_lock = build_lock_for(out)

        with build_lock:  # yalnız bir thread compose+build eder; diğerleri bekleyip cache'i alır
            with self._lock:
                svc = self._services.get(slug)
                if svc is not None:
                    return svc
            compose(slug, self._base(), out)
            build(out)
        wp_path = out / "wren_project.yml"
        wp = yaml.safe_load(wp_path.read_text()) if wp_path.exists() else {}
        datasource = (wp or {}).get("data_source") or self.settings.datasource
        svc = WrenService(out, datasource=datasource,
                          connection_info=self._connection_info(slug, datasource),
                          company_slug=slug)
        with self._lock:
            self._services[slug] = svc
        return svc

    def _connection_info(self, slug: str, datasource: str) -> dict:
        if datasource in ("duckdb", "", None):
            # Demo/duckdb şirketleri süreç varsayılanının bağlantısını paylaşır
            # (gömülü dosya yolu settings'ten gelir).
            return self.settings.connection_dict()
        try:
            from sqlmodel import Session, select

            from control_plane.config import get_auth_settings
            from control_plane.crypto import decrypt_secret
            from control_plane.db import engine
            from control_plane.models import DbConnection, Tenant

            with Session(engine) as s:
                tenant = s.exec(select(Tenant).where(Tenant.slug == slug)).first()
                conns = (s.exec(select(DbConnection).where(
                    DbConnection.tenant_id == tenant.id)).all() if tenant else [])
                # İki bağlantı olabilir: canlı (cloud_direct, clone KAYNAĞI) + ayna
                # (api_sync, dima-api'nin sorguladığı klon). Ayna varsa ONU sorgula —
                # canlı yalnız clone/sync besler (ADR-0017 K9).
                conn = next((c for c in conns if c.topology == "api_sync"),
                            conns[0] if conns else None)
            if conn is None or not conn.conn_meta_json:
                return {}
            meta = json.loads(conn.conn_meta_json)
            info: dict = {"host": str(meta.get("host") or ""),
                          "port": str(meta.get("port") or 1433),
                          "database": str(meta.get("database") or ""),
                          "user": str(meta.get("user") or "")}
            if meta.get("trust_server_certificate", True):
                info["kwargs"] = {"TrustServerCertificate": "yes"}
            if conn.secret_ciphertext:
                info["password"] = decrypt_secret(
                    conn.secret_ciphertext, get_auth_settings().cred_kek)
            return info
        except Exception as exc:
            print(f"[registry] {slug} bağlantısı çözülemedi: {exc}", file=sys.stderr)
            return {}

    def invalidate(self, slug: str) -> None:
        with self._lock:
            self._services.pop(slug, None)
            self._vqrs.pop(slug, None)

    def vqr_for(self, slug: str):
        """Slug'a bağlı VQR (öğrenen sorgu deposu) — talep üzerine oluşturulur, önbelleklenir.
        WrenService ile aynı desen (ADR-0005/0008 çok-şirketli genişleme): önceden VQR
        yalnız ``settings.company`` için vardı ve diğer TÜM tenant'larda `/verify`
        tarafından bilerek None'a zorlanıyordu — öğrenme döngüsü tek şirket dışında
        hiç çalışmıyordu. Artık her tenant kendi çiftlerini biriktirir."""
        with self._lock:
            vqr = self._vqrs.get(slug)
            if vqr is not None:
                return vqr
        from app.vqr import VQR

        vqr = VQR(slug)
        with self._lock:
            vqr = self._vqrs.setdefault(slug, vqr)
        return vqr


def wren_for_request(request):
    """İsteğin şirketine bağlı WrenService.

    ``require_company`` varsayılan-dışı tenant için servisi ``request.state.wren``'e
    bağlar; yoksa süreç varsayılanı (settings.company) kullanılır.

    🔴 **FAZ 2.6 — mali yıl BURADA kurulur.** Bu fonksiyon, veriye giden **her** yolun
    geçtiği tek nokta: dönem çözümünü besleyen ayarı başka bir yere koymak, bazı yolların
    onu **görmemesi** demekti — ve görmeyen yol sessizce **takvim yılına** düşerdi, yani
    tam olarak bu maddenin kapattığı sessiz-yanlışa.
    """
    from app import mali_takvim

    mali_takvim.kur(_mali_yil_ayi(request))
    return getattr(request.state, "wren", None) or request.app.state.wren


#: Tenant → mali yıl başlangıç ayı. ⚠ Önbellek **bilinçli**: bu değer bir yapılandırmadır,
#: istek başına DB'ye gitmek dönem çözümüne bir sorgu maliyeti eklerdi. Değişince
#: `mali_yil_onbellegini_temizle()` çağrılır (materializer'ın `invalidate` deseni).
_MALI_AY_ONBELLEK: dict[str, int] = {}


def mali_yil_onbellegini_temizle(tenant_id: str | None = None) -> None:
    _MALI_AY_ONBELLEK.pop(str(tenant_id), None) if tenant_id else _MALI_AY_ONBELLEK.clear()


def _mali_yil_ayi(request) -> int:
    """Tenant'ın mali yıl başlangıç ayı — okunamıyorsa **takvim yılı** (bugünkü davranış).

    ⚠ DB'ye ulaşamamak bir *"mali yıl yok"* kararı değildir; ama burada takvim yılına
    düşmek **doğru** olandır: alternatif, bir altyapı arızasını *"bu yıl"* sorusunun
    cevapsız kalmasına çevirmekti (`katman_b`'nin tersi durum — orada yokluk bir GÜVENLİK
    kararıydı, burada yalnız bir dönem tercihi).
    """
    from app import mali_takvim

    try:
        p = getattr(getattr(request, "state", None), "principal", None)
        tenant = str(getattr(p, "tenant_id", "") or "")
        if not tenant:
            return mali_takvim.VARSAYILAN_BASLANGIC_AY
        if tenant in _MALI_AY_ONBELLEK:
            return _MALI_AY_ONBELLEK[tenant]
        from sqlmodel import select

        from control_plane.db import get_session
        from control_plane.models import TenantConfig

        with next(get_session()) as oturum:
            cfg = oturum.exec(select(TenantConfig).where(
                TenantConfig.tenant_id == p.tenant_id)).first()
        ay = int(getattr(cfg, "mali_yil_baslangic_ay", 0) or 0) or \
            mali_takvim.VARSAYILAN_BASLANGIC_AY
        _MALI_AY_ONBELLEK[tenant] = ay
        return ay
    except Exception:                                        # noqa: BLE001
        return mali_takvim.VARSAYILAN_BASLANGIC_AY


def vqr_for_request(request):
    """İsteğin şirketine bağlı VQR — wren_for_request ile AYNI tenant çözünürlüğünü izler.

    Varsayılan şirket ``app.state.vqr``'ı (startup'ta kurulan) kullanır; diğer her
    tenant için ``company_registry`` üzerinden slug-bazlı VQR talep üzerine derlenir.
    Önceden `/verify` bu durumda VQR'ı tamamen None'a zorluyordu (bkz. CompanyRegistry.vqr_for)."""
    service = wren_for_request(request)
    slug = getattr(service, "company_slug", None)
    default_vqr = getattr(request.app.state, "vqr", None)
    if not slug or (default_vqr is not None and slug == default_vqr.company):
        return default_vqr
    registry = getattr(request.app.state, "company_registry", None)
    if registry is None:
        return default_vqr
    return registry.vqr_for(slug)
