"""Tek yetki arayüzü: ``authorize(principal, action, resource)`` (ADR-0014 Karar 3).

Query mantığı / guard / dry-plan hiçbir yerde user/role tablosuna doğrudan dokunmaz;
hep buradan geçer. Böylece auth ileride ayrı servise çıkarılabilir (in-process → remote).

Day-1: Katman A (tenant/superadmin scope) burada; Katman B (tablo/kolon/satır, dry-plan
üstünde) ``enforce_query`` kancasıyla bağlanacak (stub).
"""

from __future__ import annotations

from dataclasses import dataclass, field


class AuthzError(Exception):
    """Yetki reddi → çağıran katman 403'e çevirir."""


@dataclass(frozen=True)
class Principal:
    """Doğrulanmış istek kimliği. Tümü token'dan türetilir (ADR-0014 Karar 1)."""

    user_id: str
    tenant_id: str | None            # superadmin'de None olabilir
    is_superadmin: bool = False
    roles: list[str] = field(default_factory=list)
    branch_ids: list[str] = field(default_factory=list)  # boş = tüm şubeler (üyeliğe göre)
    tenant_slug: str | None = None   # dima company/veri-düzlemi bağı (RLS)


@dataclass(frozen=True)
class TenantScope:
    """Repository/sorgu katmanına verilen açık tenant kapsamı.

    saka-standards 08: superadmin için sessiz ``tenant_id=None`` bypass YOK —
    ``is_superadmin`` açık flag; çağıran bunu bilinçli kontrol eder.
    """

    tenant_id: str | None
    is_superadmin: bool


def tenant_scope(principal: Principal) -> TenantScope:
    if principal.is_superadmin:
        return TenantScope(tenant_id=None, is_superadmin=True)
    if not principal.tenant_id:
        raise AuthzError("Tenant context yok")
    return TenantScope(tenant_id=principal.tenant_id, is_superadmin=False)


# --- Rol matrisi (Katman A) ------------------------------------------------
# İlke: rol = YETENEK seviyesi (ne yapabilirsin); veri KAPSAMI (hangi cube/kolon)
# Katman B'nin işidir. viewer sorgu SORABİLİR ama sistemi DEĞİŞTİREMEZ
# (verify VQR öğrenmesini, schedule bildirim akışını değiştirir → analyst+).
ROLE_RANK = {"viewer": 0, "analyst": 1, "admin": 2, "owner": 3}

_ACTION_MIN_RANK = {
    "query:run": 0,          # NL sorgu + chip düzenleme + şema (ürünün kalbi)
    "contract:read": 0,      # kanıt görüntüleme/replay (rapor görmekle eşdeğer)
    "notification:read": 0,
    "schedule:read": 0,
    "vqr:write": 1,          # verify — gelecekteki cevapları değiştirir
    "schedule:create": 1,
    "schedule:run": 1,
    "sql:run": 1,            # ham SQL / dry-plan (guard SELECT-only olsa da güç yüzeyi)
    "schedule:delete": 2,    # admin+; analyst KENDİ oluşturduğunu silebilir (handler'da)
    # Discovery→Promote (Faz 2d): bir Discovery adayını kalıcı MDL ölçüsüne yükseltmek
    # yanlış eşanlamlıdan KATEGORİK olarak daha riskli (yeni SQL/join/agregasyon — çift-
    # sayım/grain riski), admin+ seviyesi gerektirir (analyst yalnız görüntüler/önerir).
    "measure:read": 1,       # aday listesi/detayı — analyst+ (viewer'a SQL/örnek gösterilmez)
    "measure:approve": 2,    # onay/ret/deprecate — admin+
    # Faz 4.5 (31 Temmuz 2026): tenant-kendi-hizmeti DB bağlama sihirbazı. Bir üçüncü-
    # taraf veritabanı KİMLİK BİLGİSİ eklemek/silmek en az measure:approve kadar riskli
    # (yanlış/kötü niyetli bağlantı → veri sızıntısı/yanlış kaynak) — admin+ gerektirir.
    # Salt listeleme/görüntüleme (sır İÇERMEZ, has_secret bool'u) analyst+ yeterli.
    "connection:read": 1,
    "connection:write": 2,
    # Faz 4.14 (1 Ağustos 2026) — PII maskeleme (dış yol haritası 2.19): sonuç
    # hücrelerindeki TCKN/e-posta/telefon/IBAN varsayılan MASKELİ döner; bu aksiyona
    # sahip rol (admin+) maskesiz görür — bu erişim audit'e düşer (app/pii.py).
    "pii:view": 2,
    # KARAR KAYDI (Faz E-4). Okuma `contract:read` ile aynı seviyede (viewer): bir kararı
    # GÖRMEK, dayandığı raporu görmekle eşdeğerdir. YAZMA analyst+ — bir karar kaydı
    # kurumsal bir beyandır ve append-only'dir (silinemez), dolayısıyla rapor okumaktan
    # kategorik olarak daha ağırdır.
    "decision:read": 0,
    "decision:write": 1,
    # DMP-DEC-0058 — Human Adoption truth; no side-effect authority.
    "decision:adopt": 1,
    # DMP-DEC-0059 — external side-effect authorization is stricter than
    # human adoption. This grants permission to authorize an exact ActionPlan;
    # it does not grant execution capability.
    "action:authorize": 2,
    # DMP-DEC-0060 / Core Closure A1 — internal work lifecycle only.
    # No external execution capability is implied.
    "work:manage": 1,
    # DMP-DEC-0060 / Core Closure A2 — records organizational Outcome over
    # governed provenance; does not calculate analytics.
    "outcome:record": 1,
    # DMP-DEC-0060 / Core Closure A3 — institutional precedent index.
    "memory:read": 0,
    "memory:write": 1,
    # DMP-DEC-0060 / Core Closure A4 — governed Watch/Signal state only.
    "watch:manage": 1,
    # ── FAZ 1.3 · AJAN ARAÇ AKSİYONLARI (2026-08-04) ────────────────────────────
    # Ölçüldü: 15 aracın **15'i** `query:run` taşıyordu → `izinli_araclar()` ya 15'ini
    # döndürüyor ya hiçbirini. §11.2'nin *"ajan kullanıcının yetkisini AŞAMAZ"* değişmezi
    # aşılmıyordu ama **sınırlanamıyordu** da: tek bir izin, granülerlik değil bir anahtardır.
    #
    # 🔴 **RÜTBELER BİLİNÇLE SEÇİLDİ — TEK BİR DAVRANIŞ DEĞİŞİKLİĞİ.** İkisi `0`, yani
    # bugün `query:run`'ı olan herkes onlara da sahip → **birebir aynı davranış** (KURAL B).
    # Yalnız `contribution:scan` `1`'e çıkar ve bu, yol haritasının KAPI'sının **adıyla
    # istediği** düzeltmedir: *"viewer rolü `contribution.report` (maliyet `pahali`)
    # çağıramıyor."*
    "drill:run": 0,          # drill.expand/select — maliyet `sifir`, çekirdek okuma
    "contribution:run": 0,   # decompose/pvm — maliyet `ucuz`, deterministik
    "contribution:scan": 1,  # 🔴 contribution.report — maliyet **`pahali`** (6 boyut tarama)
    # ⚠ `llm:invoke` **0** ve bu bir KARAR: LLM araçlarını analyst+ yapmak bir GÜVENLİK
    # değil bir ÜRÜN kararıdır (viewer'ın cevabı küple sınırlanır) ve bu madde onu vermek
    # için kurulmadı. Aksiyonun **var olması** yeter: ajan araç listesi artık dürüst ve
    # sıkılaştırma tek satırlık bir karara indi. Rütbe, LLM maliyeti ölçüldüğünde
    # (FAZ 0.17'nin gecikme bütçesi + kota telemetrisi) yeniden ele alınır.
    "llm:invoke": 0,
    # FAZ 1.5 — metrik sertifikalama. `measure:approve` ile AYNI rütbe (admin+): bir
    # metriği "sertifikalı" ilan etmek, bir Discovery adayını kalıcı ölçüye yükseltmekle
    # aynı ağırlıkta bir KURUMSAL BEYANDIR ve geri alınması aynı ölçüde pahalıdır.
    "metric:certify": 2,
}


def role_rank(principal: Principal) -> int:
    """En yüksek rol kazanır; bilinmeyen/custom rol = viewer seviyesi (fail-low).
    Üyeliksiz kullanıcı da viewer sayılır — veri kapsamını Katman B daraltacak."""
    return max((ROLE_RANK.get(r, 0) for r in principal.roles), default=0)


def permissions_for(principal: Principal) -> list[str]:
    """Principal'ın izinli aksiyon listesi — login//auth/me yanıtında frontend'e gider.

    TEK KAYNAK bu matristir: UI buton görünürlüğünü buradan okur (rol semantiği
    frontend'e kopyalanmaz; rol açmak yalnız backend değişikliğidir).
    Superadmin: tüm aksiyonlar (log-only doktrini — ADR-0015 K7 güncellemesi)."""
    if principal.is_superadmin:
        return sorted(_ACTION_MIN_RANK)
    rank = role_rank(principal)
    return sorted(a for a, r in _ACTION_MIN_RANK.items() if rank >= r)


def can(principal: Principal, action: str) -> bool:
    """Yetki sorusu (fırlatmaz) — istisna mantığı kuran handler'lar için."""
    try:
        authorize(principal, action, f"data:{action.split(':', 1)[0]}")
        return True
    except AuthzError:
        return False


def authorize(principal: Principal, action: str, resource: str) -> None:
    """Katman A kaba yetki. Reddederse ``AuthzError`` fırlatır (allow = sessiz döner).

    Kurallar:
    - superadmin: her aksiyona izinli — veri erişimi dahil. Doktrin (ADR-0015 K7
      güncellemesi 2026-07-23): ENGEL değil GÖRÜNÜRLÜK — her erişim audit'e
      actor_kind="superadmin" olarak düşer; veri-mahremiyeti kaygısı yüksek müşteri
      zaten on-prem senaryosuna gider (ADR-0003).
    - tenant kullanıcısı: kendi tenant'ı zorunlu (tenant_scope doğrular) + rol matrisi.
    - Tanımsız aksiyon = red (fail-closed).
    """
    if principal.is_superadmin:
        return
    tenant_scope(principal)  # tenant context'i doğrula (yoksa AuthzError)
    min_rank = _ACTION_MIN_RANK.get(action)
    if min_rank is None:
        raise AuthzError(f"Tanımsız aksiyon: {action}")
    if role_rank(principal) < min_rank:
        raise AuthzError("Bu işlem için yetkiniz yok")


def enforce_query(principal: Principal, referenced_models: list[str],
                  izinliler: set[str] | None = None) -> None:
    """Katman B: SQL'in dokunduğu MDL modelleri `ModelPermission` allowlist'ine karşı
    doğrulanır. Zorlama **dry-plan yolunda**, LLM prompt'unda DEĞİL (ADR-0014 Karar 5).

    ⟳ **FAZ 1.3b (2026-08-04) — STUB DOLDURULDU.** Eski gövde tek satırdı (`return`) ve
    üstünde `# TODO(faz-2)` vardı; yani **ADR-0014 Karar 5'in beyan ettiği katman hiçbir
    şey yapmıyordu**. Ölçüldü ki **çağıranı da yoktu** — katman boş değil, **bağlı bile
    değildi**.

    🔴 **«Yapılandırılmamış» ile «boş allowlist» AYNI ŞEY DEĞİL** — ve bu ayrım, yol
    haritasının *"fail-open → fail-closed"* şartını **kesinti üretmeden** sağlar:

    * `izinliler is None` → tenant'ta hiç `ModelPermission` satırı yok → Katman B
      **kurulmamış** → Katman A yönetir.
    * `izinliler` bir küme → allowlist **aktif**; içinde olmayan model **REDDEDİLİR**,
      küme boş olsa bile. *Bir kez yapılandırıldığında eksik allowlist artık geçmez.*

    Karar `app/katman_b.py::karar`'da (saf fonksiyon, DB'siz test edilebilir); burası
    yalnız onu **fırlatan** kabuktur — `context.py` felsefesi.
    """
    from control_plane.model_access import ModelErisimReddi, karar

    gecer, gerekce = karar(set(referenced_models or []), izinliler)
    if not gecer:
        raise ModelErisimReddi(f"Katman B: {gerekce}")
