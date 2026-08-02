"""Control-plane SQLModel entities (day-1 subset).

Tam model ve izolasyon değişmezleri: ``docs/auth/control-plane-sema.md``.
Her tenant-scoped satır ``tenant_id`` taşır; tenant DAİMA token'dan türetilir
(ADR-0014 Karar 1), request girdisinden asla.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _now() -> datetime:
    return datetime.utcnow()


class Tenant(SQLModel, table=True):
    __tablename__ = "tenant"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    slug: str = Field(index=True, unique=True)  # dima company/MDL derlemesine eşlenir
    name: str
    status: str = "active"  # active | suspended
    created_at: datetime = Field(default_factory=_now)


class Branch(SQLModel, table=True):
    __tablename__ = "branch"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    code: str  # veri tarafındaki branch_id ile eşleşir (RLS predicate kaynağı)
    name: str


class User(SQLModel, table=True):
    __tablename__ = "app_user"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    # superadmin (platform) tenant'sız olabilir → nullable; tenant kullanıcıları zorunlu.
    tenant_id: uuid.UUID | None = Field(default=None, foreign_key="tenant.id", index=True)
    email: str = Field(index=True)
    password_hash: str  # Argon2id
    is_superadmin: bool = False  # açık flag (saka-standards 08: sessiz bypass YOK)
    status: str = "active"
    mfa_secret: str | None = None  # TOTP; superadmin'de zorunlu (ADR-0015), tenant day-1 ops.
    created_at: datetime = Field(default_factory=_now)


class Role(SQLModel, table=True):
    __tablename__ = "role"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    key: str  # owner | admin | analyst | viewer | custom
    name: str


class Membership(SQLModel, table=True):
    """(user × branch × role) — kullanıcının şube başına rolü (saka-standards 08
    context-specific roles; upcyman UserFacilityRole muadili)."""

    __tablename__ = "membership"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(index=True)
    user_id: uuid.UUID = Field(foreign_key="app_user.id", index=True)
    branch_id: uuid.UUID | None = Field(default=None, foreign_key="branch.id")  # None = tüm şubeler
    role_id: uuid.UUID = Field(foreign_key="role.id")


class ModelPermission(SQLModel, table=True):
    """Katman B (kaba): rol hangi MDL model/kolonuna hangi aksiyonla erişir.
    Zorlama üretilen SQL üstünde, dry-plan'da yapılır (ADR-0014 Karar 5)."""

    __tablename__ = "model_permission"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(index=True)
    role_id: uuid.UUID = Field(foreign_key="role.id", index=True)
    model: str  # MDL model adı (tablo/view)
    # None = tüm kolonlar; aksi halde JSON allowlist (SQLModel JSON alanı migration'da).
    columns_json: str | None = None
    action: str = "read"  # dima read-only; ileride export/approve


class DbConnection(SQLModel, table=True):
    """Müşteri DB bağlantısı (ADR-0017 Faz 2 ile aktif): sır AES-256-GCM
    (control_plane/crypto.py, KEK yalnız admin ortamında), meta düz JSON."""

    __tablename__ = "db_connection"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    datasource: str  # postgres | sqlserver | duckdb | ...
    topology: str = "cloud_direct"  # cloud_direct | agent (ADR-0003) | api_sync (ADR-0017 K9)
    conn_meta_json: str | None = None  # host/port/db (sır DEĞİL)
    secret_ciphertext: bytes | None = None  # AES-256-GCM (control_plane/crypto.py)
    # Müşteri DB kullanıcısının salt-okunurluğu sunucudan doğrulandı mı
    # (fn_my_permissions + rol üyeliği — ADR-0017; control-plane-sema garanti listesi).
    read_only_verified: bool = False
    created_at: datetime = Field(default_factory=_now)


class CloneJob(SQLModel, table=True):
    """Bir DB clone/sync işinin durumu + ilerlemesi (ADR-0017 K9 api_sync ayna).

    Admin clone API başlatır (arka plan thread), buraya ilerleme yazar; panel poll'lar.
    In-memory DEĞİL (upcyman'dan sapma) — DB'de durur ki restart'ta kaybolmasın ve
    audit izi kalsın. kind: 'clone' (tam ayna) | 'sync' (incremental watermark)."""

    __tablename__ = "clone_job"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    source_conn_id: uuid.UUID = Field(foreign_key="db_connection.id", index=True)
    target_conn_id: uuid.UUID | None = Field(default=None, foreign_key="db_connection.id")
    kind: str = "clone"  # clone | sync
    status: str = Field(default="pending", index=True)  # pending|running|completed|failed
    target_db: str | None = None
    total_tables: int = 0
    done_tables: int = 0
    ok_tables: int = 0
    skip_tables: int = 0
    fail_tables: int = 0
    rows_total: int = 0
    current_table: str | None = None
    message: str | None = None
    error: str | None = None
    started_at: datetime = Field(default_factory=_now)
    finished_at: datetime | None = None


class SyncState(SQLModel, table=True):
    """Per-(kaynak-bağlantı × tablo) watermark durumu — incremental sync'in "nerede
    kaldık" defteri (JENERİK, db_sync.discover_watermark ile). watermark_value string
    saklanır (datetime → ISO; rowversion → hex); mode geri-dönüşümü belirler."""

    __tablename__ = "sync_state"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    connection_id: uuid.UUID = Field(foreign_key="db_connection.id", index=True)
    table_name: str = Field(index=True)
    watermark_column: str | None = None
    watermark_mode: str | None = None  # datetime | rowversion
    watermark_value: str | None = None
    row_count: int = 0
    last_synced_at: datetime = Field(default_factory=_now)


class InteractionLog(SQLModel, table=True):
    """Sorgu telemetrisi (ADR-0020 interaction yüzeyi) — Postgres'te, çünkü admin API AYRI
    servis (ADR-0015) ve Railway volume tek servise bağlı: viewer'ın data-API'nin yazdığını
    görebilmesi için ORTAK store (Postgres) şart. Audit'ten AYRI (compliance değil, kalite +
    madencilik). Dosya JSONL de yazılır (dev-grep + synonym madencisi), ama VIEWER burayı sorgular.

    Hassas veri sınırı: ham sonuç satırları TUTULMAZ; yalnız türetilmiş meta (soru, sql, satır
    sayısı, source, not, yorum-özeti)."""

    __tablename__ = "interaction_log"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    session_id: str | None = Field(default=None, index=True)
    # Aktör-ID'leri UUID (AuditLog ile TUTARLI → cross-table JOIN cast'siz çalışır).
    # Değer zaten str(uuid) tutuluyordu; tip artık UUID.
    user_id: uuid.UUID | None = Field(default=None, index=True)
    tenant_id: uuid.UUID | None = Field(default=None, index=True)
    question: str | None = None
    source: str | None = Field(default=None, index=True)  # cube | llm:<p> | rule | None
    kind: str | None = Field(default=None, index=True)     # normalize: cube|llm|rule|none|other
    follow_up: bool = False
    sql: str | None = None
    rows: int | None = None
    note: str | None = None
    duration_ms: int | None = None
    cube_query_json: str | None = None
    trace_json: str | None = None
    interpretation_json: str | None = None
    # LLM çağrı telemetrisi (yalnız LLM yoluna düşen istekte dolar; cube/rule yolunda NULL).
    # Maliyet/performans görünürlüğü: model bazında token toplamı + gecikme.
    llm_model: str | None = None
    llm_input_tokens: int | None = None
    llm_output_tokens: int | None = None
    llm_latency_ms: int | None = None


class VerifiedQuery(SQLModel, table=True):
    """Doğrulanmış soru→CubeQuery çiftleri (VQR, ADR-0005/0008) — Postgres'te.

    Neden DB (eskiden companies/<şirket>/verified/queries.jsonl): Railway volume yalnız
    `logs/`'u kapsıyordu; VQR `companies/` altındaydı → her redeploy'da öğrenilen çiftler
    SİLİNİYORDU. Kalıcı + admin-küratörlük için Postgres. Yük ihmal edilebilir: başlangıçta
    1 SELECT ile belleğe yüklenir (hot-path RAM'de), yazma yalnız ✓/✗ verify/chip-onay
    (insan hızında). Dönem filtresi SAKLANMAZ — sorgu şekli öğrenilir (VQR sınıfı düşer).

    Silme = soft-delete (proje kuralı: HİÇBİR ZAMAN hard-delete): ✗/geri-al deleted_at
    damgalar; yükleme deleted_at IS NULL süzer, satır fiziksel kalır (audit/kurtarma)."""

    __tablename__ = "verified_query"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    company: str = Field(index=True)                          # scope (settings.company)
    tenant_id: str | None = Field(default=None, index=True)   # Principal.tenant_id (iz)
    question: str
    question_norm: str = Field(index=True)                    # _norm(question) — birebir/dedup
    cube_query_json: str                                      # dönem-filtresiz CubeQuery
    # GÜVEN KAYNAĞI (Faz 4.1) — yalnız GÜVENİLİR olanlar TEKRAR OYNATILIR (app/vqr.py
    # `_TRUSTED_SOURCES`): user_verified | chip_approved | auto_cube.
    # `auto_discovery` = incelenmemiş HAM LLM SQL'i → saklanır (terfi kuyruğu + few-shot)
    # ama replay'e girmez. `auto` = ayrım öncesi eski kayıt, kökeni bilinmiyor → güvenilmez.
    source: str = "user"
    verified_by: str | None = None                           # kim doğruladı (KVKK izi)
    verified_at: datetime | None = None                      # NE ZAMAN doğrulandı
    # Onboarding'de "şunu sorabilirsin" örneği olarak gösterilmeye UYGUN mu. Ayrı bir alan
    # çünkü "doğru" ile "yeni kullanıcıya gösterilecek kadar temsili" aynı şey değildir.
    use_as_onboarding_question: bool = Field(default=False)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)  # soft-delete (ADR-0019)


class ScheduleDefinition(SQLModel, table=True):
    """Zamanlanmış rapor TANIMLARI (ADR-0011) — Postgres'te.

    Eskiden companies/<şirket>/schedules.yaml'daydı → Railway volume dışı → redeploy'da
    SİLİNİYORDU (koşum STATE'i logs/'ta kalıcıydı ama tanım kaybolurdu — absürt). Koşum
    state'i (schedule-state.json) + bildirimler (notifications.jsonl) AYNI-servis dosyaları
    olarak volume'de kalır; yalnız TANIM DB'ye taşındı. Dönem GÖRELİ saklanır ("son 7 gün"),
    her koşumda çözülür. id string ("s-<hex>"). Silme = soft-delete (deleted_at, ADR-0019)."""

    __tablename__ = "schedule_definition"
    id: str = Field(primary_key=True)                        # "s-<hex>" (yaml'daki biçim)
    company: str = Field(index=True)                         # scope (settings.company)
    tenant_id: str | None = Field(default=None, index=True)  # RLS
    label: str = ""
    cube_query_json: str                                     # CubeQuery (dönem-göreli)
    period: str | None = None                                # "dün" | "son 7 gün" | …
    every: str = "day"                                       # hour | day | week
    at: str | None = "08:00"
    weekday: int | None = None                               # 1=Pzt..7=Paz (every=week)
    threshold_json: str | None = None                        # {measure, op, value} | {method:zscore,k}
    delivery_json: str | None = None                         # ek teslim kanalları {email:{to:[...]}}
    enabled: bool = True
    created_by: str | None = None
    # KOŞUM DURUMU (tek-kaynak DB): son koşum zamanı. schedule-state.json'ın yerini alır →
    # çok-instance'ta atomik CAS claim ile double-fire engellenir (dosya-only state her
    # instance'ın kendi volume'unu okuyup aynı raporu iki kez koşuyordu).
    last_run: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)  # soft-delete


class ContractLog(SQLModel, table=True):
    """Query Contract kanıtı (ADR-0010) — Postgres'te (tek-kaynak). contracts.jsonl'ın
    yerini alır: volume dosyası tek-servis → admin plane (AYRI servis) replay/denetim için
    okuyamaz + managed backup yok + partial-write riski. Append-only (soft-delete yok:
    kanıt silinmez). Her başarılı rapor soru+CubeQuery+SQL+sonuç-hash+şema-sürümü ile mühürlenir."""

    __tablename__ = "contract_log"
    id: str = Field(primary_key=True)                        # "c-<hex>"
    ts: datetime = Field(default_factory=_now, index=True)
    session_id: str | None = Field(default=None, index=True)
    tenant_id: str | None = Field(default=None, index=True)  # RLS
    question: str | None = None
    cube_query_json: str | None = None
    sql: str | None = None
    result_hash: str | None = None
    row_count: int | None = None
    schema_version: str | None = None
    source: str | None = None


class NotificationLog(SQLModel, table=True):
    """Bildirim/teslim LOGU (ADR-0011/0020) — Postgres, TEK-KAYNAK (notifications.jsonl
    dual-write kaldırıldı).

    Zamanlanmış rapor/alarm koşumları bu tabloya yazılır (in-app bell); hem public bell
    (`GET /notifications`) hem admin plane (`/sadmin/notifications`) AYNI kaynaktan (Postgres)
    okur — admin AYRI servis olduğundan (ADR-0015) volume okunamaz, ortak store şart.
    delivery_json = kanal başına teslim sonucu (email ok/atlandı/başarısız + alıcı + Resend
    id). Append-only telemetri (interaction_log deseni; soft-delete YOK)."""

    __tablename__ = "notification_log"
    id: int | None = Field(default=None, primary_key=True)
    ts: datetime = Field(default_factory=_now, index=True)
    company: str = Field(index=True)                         # scope
    tenant_id: str | None = Field(default=None, index=True)  # RLS
    schedule_id: str | None = Field(default=None, index=True)
    kind: str = Field(index=True)                            # report | alert | anomaly
    message: str = ""
    row_count: int | None = None
    contract_id: str | None = None
    delivery_json: str | None = None                        # [{channel, ok, ...}] teslim sonucu


class NotificationPreference(SQLModel, table=True):
    """Kullanıcı bildirim tercihi (ADR-0011) — KATEGORİ × KANAL matrisi.

    Birleşik teslim mimarisinin tercih katmanı: kullanıcı her bildirim kategorisini
    (report/alert/anomaly/system) hangi kanaldan (inapp/email/push/…) alacağını seçer.
    (user_id, category, channel) benzersiz mantıksal anahtar. inapp varsayılan AÇIK;
    email/push opt-in. address: kanal-özel hedef (e-posta adresi / push token); boşsa
    kullanıcının varsayılanı (email → hesap e-postası). Bu tercih SELF-bildirim içindir;
    schedule.delivery (rapor dağıtım listesi) ayrı katmandır — dispatcher ikisini birler.
    Soft-delete (ADR-0019)."""

    __tablename__ = "notification_preference"
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    tenant_id: str | None = Field(default=None, index=True)  # RLS
    category: str = Field(index=True)                        # report | alert | anomaly | system
    channel: str                                            # inapp | email | push | …
    enabled: bool = True
    address: str | None = None                              # kanal-özel hedef (boş → varsayılan)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)  # soft-delete


class Dashboard(SQLModel, table=True):
    """Kullanıcı panosu (§9 canlı-izleme) — PER-USER, kullanıcı başı ≤10 (router guard).

    "Dinamik raporlama"nın PULL ayağı: chat'te üretilen grafik/tablo widget olarak eklenir,
    pano açılınca widget'lar CANLI (göreli dönem yeniden çözülür). visibility='tenant' →
    şirket içi paylaşım (sonraki faz). Soft-delete (ADR-0019)."""

    __tablename__ = "dashboard"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: str | None = Field(default=None, index=True)  # izolasyon
    user_id: str = Field(index=True)                         # sahiplik (per-user)
    title: str = ""
    visibility: str = "private"                              # private | tenant
    layout_json: str | None = None                          # grid düzeni (toplu)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now, index=True)
    deleted_at: datetime | None = Field(default=None, index=True)  # soft-delete


class DashboardWidget(SQLModel, table=True):
    """Pano widget'ı — kayıtlı `cube_query` + göreli dönem (schedule/VQR ile aynı ilke:
    dönem SAKLANMAZ, her görüntülemede çözülür). Chat sonucundan doğar (cube_query+view_hint
    zaten yanıtta). Zamanlanmış rapor ile AYNI "kayıtlı sorgu" soyutlaması (biri pull biri push)."""

    __tablename__ = "dashboard_widget"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    dashboard_id: uuid.UUID = Field(index=True)
    title: str = ""
    cube_query_json: str                                     # dönem-göreli CubeQuery
    view_hint: str | None = None                             # grafik türü (bar/line/pivot/…)
    period: str | None = None                                # "bu hafta" — her açılışta çözülür
    pos_json: str | None = None                              # {x,y,w,h} grid konumu
    refresh: str = "onview"                                  # onview | cache:<ttl> | live
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)  # soft-delete


class Conversation(SQLModel, table=True):
    """Kullanıcı sohbeti (first-class entity) — session_id → soru+yanıt zinciri, PER-USER,
    tenant-izole. Şu ana kadar yalnız interaction-LOG (JSONL) + FE memory store vardı; bu,
    liste/getir/resume + geçmiş kenar çubuğu için kalıcı kayıt. Öğrenme (VQR) + audit değeri.

    Kimlik token'dan (Principal): user_id/tenant_id STRING (JWT sub/tid). Konuşma
    (user_id × session_id) ile tekilleşir; session_id client üretir (konuşma başına)."""

    __tablename__ = "conversation"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: str | None = Field(default=None, index=True)   # Principal.tenant_id (izolasyon)
    user_id: str = Field(index=True)                          # Principal.user_id (sahiplik)
    session_id: str = Field(index=True)                       # client üretir (konuşma başına)
    title: str = ""                                           # ilk gerçek sorudan türer
    message_count: int = 0
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now, index=True)
    # SOFT DELETE (proje kuralı: HİÇBİR ZAMAN hard-delete): silme = deleted_at damgası;
    # liste/getir deleted_at IS NULL süzer. Kayıt fiziksel silinmez (audit/kurtarma).
    deleted_at: datetime | None = Field(default=None, index=True)


class ConversationMessage(SQLModel, table=True):
    """Bir sohbetteki tek yanıt — resume için TAM AskResponse (payload_json): soru + sql +
    result + source + cube_query + note + kpi + interpretation. Resume = kayıtlı yanıtları
    yeniden render (yeniden çalıştırma yok → veri değişse de geçmiş sabit kalır)."""

    __tablename__ = "conversation_message"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", index=True)
    seq: int = 0
    question: str = ""
    payload_json: str = "{}"                                  # tam AskResponse (JSON)
    created_at: datetime = Field(default_factory=_now)


class TenantConfig(SQLModel, table=True):
    """Tenant'ın veri-düzlemi yapılandırması (sektör pack'leri + modüller).

    KAYNAK burasıdır (admin panel yazar); dima-api bunu companies/<slug>/company.yml
    dosyasına MATERIALIZE eder (türetilmiş çıktı) ve compose eder — iki servis disk
    paylaşmaz, paylaşılan tek şey bu DB'dir. Config satırı OLMAYAN tenant için
    repo'daki elle yazılmış company.yml (varsa) geçerli kalır; satır varsa DB kazanır.
    """

    __tablename__ = "tenant_config"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True, unique=True)
    sektorler_json: str = "[]"        # JSON listesi; sırada önce gelen kazanır
    moduller_json: str | None = None  # None = sektör paketlerinin varsayılanları
    # ADR-0017 kaynak faseti: kaynak pack anahtarları (None = kaynak seçilmemiş,
    # demo DuckDB akışı) + önekli şemalarda (Logo LG_FFF_PP_*) firma/dönem kapsamı.
    kaynaklar_json: str | None = None
    firma_no: int | None = None
    donem_no: int | None = None
    # AKTİF DİL SETİ (§7b) — sıralı JSON listesi (öncelik: önce gelen = soft-prior). None →
    # varsayılan (tr+en). company.yml `diller:` olarak materialize edilir → routing union'lar.
    diller_json: str | None = None
    updated_by: uuid.UUID | None = None
    updated_at: datetime = Field(default_factory=_now)


class FeatureOverride(SQLModel, table=True):
    """Özellik bayrağı override'ı (ADR-0009 DB fazı) — admin panelden yönetilir.

    Çözüm kuralı: EN SPESİFİK tanım kazanır (user > role > tenant > sector >
    global); tanımsız kapsam bir üstünü MİRAS alır. Pack/company YAML değerleri
    fabrika ayarıdır, buradaki satırlar üstüne biner. Spesifik kapsamda "off"
    yazmak = kill switch (global prod'u o kapsam için kapatır)."""

    __tablename__ = "feature_override"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    feature_key: str = Field(index=True)
    scope_type: str = Field(index=True)  # global | sector | tenant | role | user
    scope_id: str | None = Field(default=None, index=True)  # global'de None
    stage: str  # off | alpha | beta | prod
    updated_by: uuid.UUID | None = None
    updated_at: datetime = Field(default_factory=_now)


class SynonymOverride(SQLModel, table=True):
    """Canlı öğrenilen sinonim overlay'i (ADR-0018 katman 3): pack YAML (kod) +
    arketip kütüphanesi (platform) üstüne DEPLOY'SUZ biner. Additive — base sözlüğü
    SİLMEZ, ekler. Kaynak: route-edilemeyen soru madenciliği → admin onayı.

    Hedef: cube (+opsiyonel measure/dimension). Kapsam: global (tüm tenantlar) |
    tenant (yalnız o slug). dima-api schema() derlerken okur ve birleştirir; ~1 dk
    materializer döngüsüyle cache tazelenir (deploy yok). approved=False → aday
    kuyruğunda bekler, canlıya İNMEZ (determinizm koruması, ADR-0018 1e)."""

    __tablename__ = "synonym_override"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    scope_type: str = Field(index=True)          # global | tenant
    scope_id: str | None = Field(default=None, index=True)  # tenant slug; global'de None
    cube: str = Field(index=True)                # hedef cube adı
    field_kind: str                              # measure | dimension | cube
    field_name: str | None = None               # measure/dimension adı; cube-düzeyinde None
    synonyms_json: str                           # JSON listesi (additive)
    lang: str | None = None                     # dil kodu (tr/en/…); None = yerel/belirsiz (§7b)
    approved: bool = Field(default=False, index=True)  # onaysız aday canlıya inmez
    source: str = "manual"                       # manual | mined (log madenciliği)
    updated_by: uuid.UUID | None = None
    updated_at: datetime = Field(default_factory=_now)


class RefreshToken(SQLModel, table=True):
    """Refresh rotation + reuse detection (saka-standards 02). Day-1 Redis yerine
    Postgres (bilinçli sapma; rotation/family/reuse korunur)."""

    __tablename__ = "refresh_token"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="app_user.id", index=True)
    family_id: uuid.UUID = Field(index=True)  # rotation family; reuse → tüm family revoke
    token_hash: str = Field(index=True)       # ham token asla saklanmaz
    fingerprint: str | None = None            # hash(UA + Accept-Language)
    is_used: bool = False
    issued_at: datetime = Field(default_factory=_now)
    expires_at: datetime
    revoked_at: datetime | None = None


class MeasureCandidate(SQLModel, table=True):
    """Discovery→Promote adayı (Faz 2d, 31 Temmuz 2026): Discovery (ham-SQL LLM) yolunun
    ürettiği bir cevap best-effort bir "taslak ölçü" adayı olarak buraya yakalanır
    (`app/routers/ask.py` Discovery bloğu). `SynonymOverride`'ın (ADR-0018 katman 3)
    aday→onay→additive-overlay deseninin ÖLÇÜ-seviyesi genişlemesi — ama blast-radius
    kategorik olarak farklı (yanlış bir ölçü = yeni SQL/join/agregasyon riski, yanlış bir
    eşanlamlıdan çok daha tehlikeli): onay AYRICA `expression`'ı `dry_plan`'dan geçirir +
    eşleşen bir altın-vaka (`golden_case_id`) ister + blast-radius (best-effort) taraması
    yapar. Onay MDL YAML'ına (`app/mdl_writer.py`, ruamel round-trip) kalıcı bir ölçü
    EKLER — var olan bir cube'a; yeni cube/model/ilişki icat ETMEZ (base_object zaten
    var olmalı). Geri-alma YAML'dan SİLME değil `MeasureOverride` (suppress) overlay'idir
    (kanıt silinmez ilkesi — eski VQR/dashboard/Contract kullanımları kırılmaz)."""

    __tablename__ = "measure_candidate"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID | None = Field(default=None, foreign_key="tenant.id", index=True)
    company: str = Field(index=True)  # settings.company kapsamı (VerifiedQuery ile tutarlı)
    status: str = Field(default="draft", index=True)  # draft|pending_review|approved|rejected|deprecated
    question: str
    sql: str
    sample_rows_json: str | None = None  # ilk ~5 satır (reviewer'a bağlam)
    schema_version: str | None = None
    # Onay formunda doldurulur (approve öncesi None):
    cube: str | None = None
    measure_name: str | None = None
    expression: str | None = None
    measure_type: str = "DOUBLE"
    label: str | None = None
    synonyms_json: str | None = None
    lower_is_better: bool | None = None
    golden_case_id: str | None = None  # eval/cases.yaml'a eklenen vakanın id'si
    proposed_by: str | None = None  # user_id (varsa) — Discovery yakalaması genelde sistem
    reviewed_by: uuid.UUID | None = None
    review_note: str | None = None
    superseded_by_id: uuid.UUID | None = Field(default=None, foreign_key="measure_candidate.id")
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)  # soft-delete (ADR-0019)


class MeasureOverride(SQLModel, table=True):
    """Ölçü GİZLEME overlay'i (Faz 2d) — `SynonymOverride`'ın additive-EKLEME deseninin
    TERSİ: bir MDL ölçüsünü NL-routing'ten (`cube_router.route()`/`cube_only_match()`,
    `_match_measure` yalnız `measure_synonyms`'a bakar) sessizce gizler ama YAML'dan
    SİLMEZ (dosya değişikliği/deploy yok) — dashboard/VQR/Contract'taki ESKİ kullanımlar
    (ölçüye adıyla, sinonim aramadan referans verir) kırılmaz (ADR ilkesi: kanıt silinmez).
    Kaynak: bir `MeasureCandidate.status='deprecated'` kararı (kötü/yanlış onaylanmış ölçü)."""

    __tablename__ = "measure_override"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    scope_type: str = Field(index=True)          # global | tenant
    scope_id: str | None = Field(default=None, index=True)  # tenant slug; global'de None
    cube: str = Field(index=True)
    measure_name: str = Field(index=True)
    reason: str | None = None
    candidate_id: uuid.UUID | None = Field(default=None, foreign_key="measure_candidate.id")
    superseded_by_measure: str | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=_now)


class AskJob(SQLModel, table=True):
    """Discovery (ham-SQL LLM) yolunun arka-plan iş kuyruğu karşılığı (Faz 4.1 — dış yol
    haritası 0.1'in BullMQ/Redis'siz, ölçeğimize uygun karşılığı). `CloneJob` (yukarıda)
    ile AYNI desen: DB-tablosu tabanlı durum + thread, in-memory DEĞİL (restart'ta iz kalır).

    Yalnız `ask_async_discovery` bayrağı açıkken devreye girer (varsayılan KAPALI —
    demo/packs/features.yml'e BİLEREK eklenmedi, mevcut senkron davranış hiçbir tenant'ta
    değişmez). `request_json`, işi tekrar bağlamlandırmak için gereken girdiyi taşır (soru,
    prev_sql, history, session_id) — ama bu ilk sürümde CloneJob'un aksine tam "kaldığı
    yerden devam" YOK: süreç çökmüşken pending/running kalan işler, yeniden başlatmada
    dürüst bir hata notuyla `failed`e çevrilir (bkz. app/main.py lifespan) — kullanıcı
    soruyu tekrar sorar. Sessizce kaybolma YOK, ama ORTASINDAN devam da YOK (bilinçli
    kapsam sınırı — tam resume, `_run_discovery`'nin request-bağımlı kapanışlarını tümüyle
    request-bağımsız hale getirmeyi gerektirir, bu ilk iterasyonda orantısız risk).
    `result_json`, tamamlanan işin TAM AskResponse'udur (frontend'in poll'da aldığı payload)."""

    __tablename__ = "ask_job"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID | None = Field(default=None, index=True)
    session_id: str | None = Field(default=None, index=True)
    question: str
    status: str = Field(default="pending", index=True)  # pending|running|completed|failed
    request_json: str = "{}"
    result_json: str | None = None
    # Faz 4.12 (1 Ağustos 2026 — dış yol haritası 2.9 "canlı düşünme adımları"): `trace[]`
    # artık iş TAMAMLANMADAN da (pending/running iken) BİRİKEREK yazılır — `_run_discovery`
    # her adımı ekledikçe (`on_step` callback) buraya da anında düşer; istemci poll
    # ederken TÜM iş bitmesini beklemeden hangi aşamada olduğunu görebilir.
    trace_json: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)
    started_at: datetime | None = None
    finished_at: datetime | None = None


class AuditLog(SQLModel, table=True):
    """Append-only erişim kanıtı — contracts.py genişletmesi + KVKK (ADR-0014 Karar 6).
    Başarı, audit yazılmadan raporlanmaz (mamut invariant #4)."""

    __tablename__ = "audit_log"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID | None = Field(default=None, index=True)
    ts: datetime = Field(default_factory=_now, index=True)
    actor_user_id: uuid.UUID | None = None
    actor_kind: str = "user"  # user | agent | superadmin | system
    branch_id: uuid.UUID | None = None
    role_key: str | None = None
    action: str = "query"  # query | login | logout | grant | break_glass
    nl_question: str | None = None
    generated_sql: str | None = None
    touched_models_json: str | None = None
    rows_returned: int | None = None
    masked_columns_json: str | None = None
    ip: str | None = None
    contract_id: str | None = None  # ADR-0010 contract'a bağ
