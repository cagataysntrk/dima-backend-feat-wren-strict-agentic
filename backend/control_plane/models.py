"""Control-plane SQLModel entities (day-1 subset).

Tam model ve izolasyon değişmezleri: ``docs/auth/control-plane-sema.md``.
Her tenant-scoped satır ``tenant_id`` taşır; tenant DAİMA token'dan türetilir
(ADR-0014 Karar 1), request girdisinden asla.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Text, UniqueConstraint

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


class EskalasyonKurali(SQLModel, table=True):
    """FAZ 1.10 — bir uyarı, GÖRÜLMEZSE yükselir.

    Bir eşik aşıldığında bildirim gider ve orada BİTER. Kimse bakmazsa sistem "haber
    verdim" der ve susar — ama bir uyarının İŞLEVİ haber vermek değil, BİR KARARA YOL
    AÇMAKTIR: on iki saat kimsenin bakmadığı bir alarm, hiç gönderilmemiş bir alarmla
    AYNI SONUCU üretir.

    ⚠ `otomatik_kilitle` bir ÖNERİ üretir, bir eylem DEĞİL: bir hesabı otomatik
    kilitlemek GERİ ALINAMAZ ve FAZ 6'nın "onaysız hiçbir yazma" değişmezine bağlıdır.
    """

    __tablename__ = "eskalasyon_kurali"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(index=True)
    ad: str
    tetikleyici_esik: str                    # hangi eşik/uyarı sınıfı
    sure_dakika: int = 60                    # bu süre YANITSIZ kalırsa yükselir
    hedef_rol: str = "analyst"               # şu an kimde; bir ÜSTÜNE yükselir
    otomatik_kilitle: bool = False           # ÖNERİ üretir — eylem FAZ 6.1'e bağlı
    enabled: bool = True
    created_at: datetime = Field(default_factory=_now)


class MetrikSertifikasi(SQLModel, table=True):
    """FAZ 1.5 — bir metriğin tanımını KİM onayladı, ve o onaydan beri ne değişti?

    `source=cube` rozeti *"deterministik bir yoldan geldi"* der; bu tablo *"tanımı kim
    onayladı"* der. Bir metrik DOĞRU hesaplanıp YANLIŞ tanımlanmış olabilir ve determinizm
    onu yakalamaz.

    🔴 **Çürüme kaydı SİLİNMEZ** — `app/certification.py::durum` seviyeyi korur ve üstüne
    bayrak düşürür: *"hiç sertifikalanmamış"* ile *"sertifikalanmış ama tanım değişmiş"*
    farklı şeylerdir ve ikincisi kullanıcı için daha bilgilendiricidir.
    """

    __tablename__ = "metrik_sertifikasi"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(index=True)
    metric_ref: str = Field(index=True)      # "<cube>.<olcu>"
    seviye: str = "onerilen"                 # onerilen | sertifikali | master_veri
    sertifikalayan_id: uuid.UUID | None = None
    sertifika_notu: str | None = None
    # Parmak izleri: tanımın KENDİSİ saklanmaz — aynı gerçeğin ikinci kopyası olurdu.
    definition_hash: str | None = None
    lineage_set_hash: str | None = None      # FAZ 1.6'nın kolon kökeninden
    son_gecerlilik: datetime | None = None   # TTL 90 gün (certification.GECERLILIK_GUN)
    otomatik_iptal_nedeni: str | None = None
    created_at: datetime = Field(default_factory=_now)


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
    #: 🔴 **SOFT DELETE** (proje kuralı: hard-delete YOK). Bu alan bir ihlal kapatıyor:
    #: `delete_connection` `s.delete(conn)` yapıyordu ve satır **şifreli kimlik bilgisi**
    #: taşıyor — silindiğinde geri getirilemez, ve `audit`'in `connection_delete` kaydı
    #: **konusu olmayan bir kimliğe** işaret ederdi.
    #: *Bir silme kaydı, sildiği şeye artık ulaşamıyorsa, bir kayıt değil bir dipnottur.*
    deleted_at: datetime | None = Field(default=None, index=True)


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
    # RED GEREKÇESİ (Faz 0): `route()` hangi dalda pes etti — R1…R10 (`cube_router.
    # RED_KODLARI`). AYRI kolon, `note`'a sıkıştırılmadı: `note` serbest METİNDİR ve
    # `admin_app/routers/synonyms.py::mine_candidates` onu zaten başarısızlık açıklaması
    # olarak okuyor. Sabit bir kod ayrı kolonda durursa GRUPLANABİLİR — planın Faz 0
    # çıktısı ("en sık 20 red gerekçesi") tam olarak bunu gerektiriyor.
    # `route()` pes etmediyse (cevap geldi) NULL kalır.
    reject_reason: str | None = Field(default=None, index=True)
    # 🔴 KÖK-8a — RED KAYITLARI KENDİ BOŞLUĞUNU BİLDİRSİN (denetim raporu).
    #
    # `reject_reason` *"hangi dalda pes ettim"* der (R1…R10) ama **hangi kelime yüzünden**
    # demez. Sözlük boşluğu bugün **tahminle** kapatılıyor: birileri bir kelime düşünüp
    # katalog'a ekliyor. Bu iki kolon onu **ölçüme** çevirir:
    #
    #     "bu ay 412 soru `sattık` yüzünden düştü"
    #
    # 🔴 Stratejik değeri en yüksek madde: girdi **gerçek kullanıcı cümleleridir**, yani
    # devralınan raporun teşhis ettiği *"sistemi kendi aynasında ölçme"* tuzağına
    # **yapısal olarak** düşemez. Ve elle vaka yazma ihtiyacını azaltır.
    #
    # ⚠ İkisi de JSON dizi (metin): SQLite/Postgres ortak paydası. Sorgu `LIKE` ile
    # yapılabilir; asıl tüketici toplu bir rapor, satır-içi filtre değil.
    #: `route()`in kapsayamadığı kelimeler — sözlük boşluğunun ADI.
    uncovered_words: str | None = None
    #: Ölçü sinyali veren ama seçilmeyen cube'lar — belirsizliğin ADI.
    aday_cubelar: str | None = None


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
    # KÖKEN KANITI (Faz D2). `{"dimensions": {<boyut>: {relationship, model, column, hops,
    # certified}}}`. "Bu sayı nasıl hesaplandı"ın yanına "bu KIRILIM nereden geldi ve o
    # join ÖLÇÜLDÜ mü" cevabını koyar. Yalnız ilişki-türevi boyut kullanan cevaplarda dolar.
    provenance_json: str | None = None


class DecisionRecord(SQLModel, table=True):
    """KARAR KAYDI (Faz E-4) — *"bu kararı şu kanıta dayanarak, şu tarihte aldık."*

    Query Contract *"bu sayı nasıl hesaplandı"* sorusunu cevaplar. Karar Kaydı bir üst
    soruyu cevaplar: **"bu sayıya bakarak NE KARAR VERDİK ve neden?"** BI ürünlerinde
    eksik olan halka budur — rapor kalır, kararın kendisi kaybolur ve altı ay sonra
    *"bunu neden yapmıştık"* sorusunun cevabı kimsede olmaz.

    **İmza = kanonik içeriğin SHA-256'sı.** Gizli anahtarlı bir imza DEĞİL (bu bir
    kimlik doğrulama değil **kurcalama tespiti**dir): kayıt sonradan değiştirilirse hash
    tutmaz ve `GET /decisions/{id}` bunu söyler. Append-only — karar silinmez, iptal
    edilirse yeni bir kayıt yazılır (`supersedes`).
    """

    __tablename__ = "decision_record"
    id: str = Field(primary_key=True)                        # "d-<hex>"
    ts: datetime = Field(default_factory=_now, index=True)
    tenant_id: str | None = Field(default=None, index=True)  # RLS
    user_id: str | None = Field(default=None, index=True)    # kararı ALAN kişi
    session_id: str | None = Field(default=None, index=True)
    question: str | None = None                              # kararın doğduğu soru
    # Seçilen seçenek + değerlendirilen TÜM seçenekler (reçetenin gövdesi). Yalnız
    # seçileni saklamak, kararın GEREKÇESİNİ yok ederdi: "neden bu?" sorusu ancak
    # "hangilerine karşı?" bilinirse cevaplanır.
    chosen_json: str | None = None
    options_json: str | None = None
    rationale: str | None = None                             # reçetenin gerekçesi
    note: str | None = None                                  # kullanıcının kendi notu
    # KANIT: bu kararın dayandığı Query Contract kimlikleri. Karar kaydı tek başına bir
    # cümledir; makbuzlara bağlı olduğunda YENİDEN ÇALIŞTIRILABİLİR bir iddiaya dönüşür.
    contract_ids_json: str | None = None
    content_hash: str | None = Field(default=None, index=True)
    supersedes: str | None = None                            # iptal/revizyon zinciri
    # 🔴 FAZ 5.8 — **ŞABLON**: kararın dayandığı analizi **yeniden koşulabilir** kılar.
    #
    # `contract_ids` *"o gün hangi sayıya baktık"* der (donmuş kanıt). Şablon bir üst
    # soruyu cevaplar: **"aynı analizi BUGÜN koşsak ne çıkar?"** İkisi farklı şeylerdir
    # ve biri ötekinin yerine geçmez — makbuz **geçmişi**, şablon **tekrarı** taşır.
    #
    # ⚠ `{"cube_query": {...}, "parametreler": ["period", ...]}`. `cube_query` taşınır
    # çünkü yeniden koşum **0 LLM**'dir (`POST /cube` yolu); `sql` taşınmaz — donmuş bir
    # SQL, şema değişince sessizce yanlış çalışır.
    sablon_json: str | None = None


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
    # NEDEN (Faz F3): uyarıyı sürükleyen segmentler + kırpma/tarama notu. Ayrı bir kolon,
    # `delivery_json`'ın içine sıkıştırılmadı: teslim TELEMETRİSİ ile cevabın İÇERİĞİ farklı
    # şeylerdir ve birini ötekinin içinde saklamak, ikisini de sorgulanamaz yapardı.
    # Etiketler PII-maskeli ve tıklanabilir sorgu TAŞIMAZ (bkz. `schedules.uyari_nedeni`).
    neden_json: str | None = None                           # {"satirlar": [...], "not": "..."}


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


class SunumTercihi(SQLModel, table=True):
    """Kullanıcının KALICI SUNUM tercihi (Faz E — "Memories"in daraltılmış hâli).

    ## Neden YALNIZ sunum

    Araştırma raporu genel bir *"Memories"* katmanı öneriyordu. Kapsam **bilerek**
    daraltıldı, çünkü iki yarısından biri **zaten vardı**: terminoloji tercihi
    (*"biz fire'yi kg konuşuruz"*) `SynonymOverride`'dır ve katalog katmanında yaşar.
    Eksik olan yalnız **sunum** yarısıydı (*"hep aylık göster"*) ve onun deposu yoktu.

    ## Değişmez: tercih ÖLÇÜ/CUBE SEÇİMİNE KARIŞMAZ

    Saklanan şey bir **görünüm** kararıdır (granülerlik, tablo/grafik). Bir tercihin
    *hangi ölçü* ya da *hangi cube* sorusuna karışması, kullanıcının sormadığı bir
    raporu ona kendi ayarı gibi göstermek olurdu — bu deponun kovaladığı sessiz-yanlışın
    en sinsi hâli, çünkü kaynağı kullanıcının kendi geçmiş cümlesidir.

    ## Değişmez: tercih SESSİZ uygulanmaz

    Uygulandığı her turda cevap bunu SÖYLER. Sessiz uygulanan bir tercih, aylar sonra
    *"bu rapor neden aylık?"* sorusunu cevapsız bırakır.

    `anahtar` kapalı bir kümedir (`granularity` | `view`); serbest metin DEĞİL —
    aksi hâlde depo, tanımsız bir *"model belleği"*ne dönüşürdü. (user_id, anahtar)
    mantıksal olarak benzersizdir. Soft-delete (ADR-0019)."""

    __tablename__ = "sunum_tercihi"
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    tenant_id: str | None = Field(default=None, index=True)   # RLS
    anahtar: str = Field(index=True)                          # granularity | view
    deger: str                                                # month | week | table | chart …
    #: Tercihi doğuran CÜMLE — kullanıcı *"bunu ne zaman söylemişim?"* diye sorabilmeli.
    kaynak_ifade: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)


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
    #: 🔴 FAZ 5.10 — **KPI PİN**. `app/kpi_pin.py` yazılmıştı ama kolonu yoktu ve modül
    #: üretim kodunda **hiç import edilmiyordu**. ⚠ Varsayılan `False`: mevcut widget'lar
    #: pin'siz doğar — *hiç kimse onları pin'lemedi.*
    pinned: bool = False
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


class ResearchSessionRecord(SQLModel, table=True):
    """Durable P14 Research aggregate checkpoint, scoped to one tenant/principal."""

    __tablename__ = "research_session"
    session_id: str = Field(primary_key=True)
    tenant_binding: str = Field(index=True)
    principal_subject: str = Field(index=True)
    authority_id: str = Field(index=True)
    context_version: str
    revision: int
    checkpoint_json: str = Field(sa_column=Column(Text, nullable=False))
    checkpoint_fingerprint: str = Field(index=True)
    delegatable_ids_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class NativeSubjectBinding(SQLModel, table=True):
    """Explicit Dima-user to native Metabase subject correlation; never a credential."""

    __tablename__ = "native_subject_binding"
    __table_args__ = (
        UniqueConstraint("tenant_id", "dima_user_id", name="uq_native_subject_binding_dima_user"),
        UniqueConstraint("tenant_id", "metabase_user_id", name="uq_native_subject_binding_metabase_user"),
    )
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    dima_user_id: uuid.UUID = Field(foreign_key="app_user.id", index=True)
    metabase_user_id: int = Field(index=True, ge=1)
    security_profile: str
    policy_version: str
    approved_by_user_id: uuid.UUID = Field(foreign_key="app_user.id")
    enabled: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class NativeResourceBinding(SQLModel, table=True):
    """Business-context to exact native resource locator/version mapping only."""

    __tablename__ = "native_resource_binding"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "semantic_context_version", "candidate_id", "candidate_kind",
            name="uq_native_resource_binding_candidate",
        ),
    )
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    semantic_context_version: str = Field(index=True)
    candidate_id: str = Field(index=True)
    candidate_kind: str
    semantic_id: str = Field(index=True)
    canonical_name: str
    locator_kind: str
    metabase_database_id: int = Field(ge=1)
    metabase_table_id: int | None = Field(default=None, ge=1)
    metabase_field_id: int | None = Field(default=None, ge=1)
    metabase_metric_id: int | None = Field(default=None, ge=1)
    metabase_entity_id: str | None = None
    resource_entity_id: str = Field(index=True)
    resource_fingerprint: str = Field(index=True)
    resource_version: str
    enabled: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ResearchExecutionLink(SQLModel, table=True):
    """Durable correlation from a Research obligation to one native occurrence."""

    __tablename__ = "research_execution_link"
    __table_args__ = (
        UniqueConstraint(
            "dima_request_id",
            name="uq_research_execution_link_request",
        ),
    )

    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    session_id: str = Field(foreign_key="research_session.session_id", index=True)
    obligation_id: str = Field(index=True)
    execution_kind: str = Field(default="P14_BASE", index=True)
    reasoning_step_id: str | None = Field(
        default=None,
        foreign_key="research_reasoning_step.step_id",
        index=True,
    )
    investigation_task_id: str | None = Field(
        default=None,
        foreign_key="research_investigation_task.task_id",
        index=True,
    )
    dima_request_id: str = Field(index=True)
    dima_trace_id: str
    native_conversation_id: uuid.UUID
    native_query_id: str | None = Field(default=None, index=True)
    native_query_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    native_query_fingerprint: str | None = Field(default=None, index=True)
    native_subject_ref: str | None = None
    runtime_identity_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    native_result_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    result_hash: str | None = Field(default=None, index=True)
    executed_at: datetime | None = None
    attestation_id: str | None = None
    status: str = Field(default="DELEGATED", index=True)
    receipt_id: str | None = Field(default=None, index=True)
    evidence_id: str | None = Field(default=None, index=True)
    limitation_code: str | None = None
    limitation_detail: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ResearchExplorationMaterial(SQLModel, table=True):
    """Durable P15 native exploration material bound to one sealed P14 occurrence.

    This record stores provenance/material only. It is not an analytics definition,
    interestingness score owner, query planner, or claim/finding.
    """

    __tablename__ = "research_exploration_material"
    __table_args__ = (
        UniqueConstraint(
            "execution_link_id",
            name="uq_research_exploration_material_execution_link",
        ),
    )

    lead_id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="research_session.session_id", index=True)
    obligation_id: str = Field(index=True)
    execution_link_id: uuid.UUID = Field(
        foreign_key="research_execution_link.id",
        index=True,
    )
    native_conversation_id: uuid.UUID
    native_query_id: str = Field(index=True)
    query_fingerprint: str = Field(index=True)
    source_evidence_refs_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    exploration_kind: str = Field(index=True)
    native_payload_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    payload_fingerprint: str = Field(index=True)
    epistemic_state: str = Field(default="RESEARCH_MATERIAL", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ResearchClaimRecord(SQLModel, table=True):
    """Durable P16 claim identity; no analytical truth computation lives here."""

    __tablename__ = "research_claim"

    claim_id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="research_session.session_id", index=True)
    obligation_id: str = Field(index=True)
    tenant_binding: str = Field(index=True)
    principal_subject: str = Field(index=True)
    semantic_context_version: str = Field(index=True)
    claim_text: str = Field(sa_column=Column(Text, nullable=False))
    proposition_json: str = Field(sa_column=Column(Text, nullable=False))
    scope_json: str = Field(sa_column=Column(Text, nullable=False))
    freshness_json: str = Field(sa_column=Column(Text, nullable=False))
    origin_material_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    epistemic_state: str = Field(default="PROPOSED", index=True)
    limitations_json: str = Field(sa_column=Column(Text, nullable=False))
    claim_fingerprint: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ClaimEvidenceLinkRecord(SQLModel, table=True):
    """Immutable P16 edge from one claim to one eligible P14 Evidence identity."""

    __tablename__ = "claim_evidence_link"
    __table_args__ = (
        UniqueConstraint(
            "claim_id",
            "evidence_id",
            name="uq_claim_evidence_link_claim_evidence",
        ),
    )

    link_id: str = Field(primary_key=True)
    claim_id: str = Field(foreign_key="research_claim.claim_id", index=True)
    evidence_id: str = Field(index=True)
    receipt_id: str = Field(index=True)
    execution_link_id: uuid.UUID = Field(
        foreign_key="research_execution_link.id",
        index=True,
    )
    relation: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class MetrikSahipligi(SQLModel, table=True):
    """FAZ 2.2b — bir **çakışan terimin** sahibi hangi cube'dur.

    ## 🔴 Neden bu tablo var — 0.18 KENDİ KENDİNE ATILDI

    `0.18` hakemi kurdu (`metrik_kaydi.hakem`) ama kaydı **katalogdan taslak** olarak
    üretiyor ve `sahiplenilen_terimler` **boş** başlıyor. Boşu dolduracak bir yol
    olmadığı için hakem **hiçbir zaman** karar veremezdi: mekanizma yapısal olarak
    **atıldı**. *Kurulmuş ama beslenemeyen bir hakem, kurulmamış bir hakemdir.*

    ## ⚠ Neden yalnız SAHİPLİK — yol haritasının alan listesi BİLEREK daraltıldı

    Yol haritası `display_name · unit · rounding · description · target_ref` da sayıyor.
    Bunların hepsi **cube YAML'ında zaten var** ve oradan şemaya akıyor; DB'ye kopyalamak
    *"aynı kuralın iki sahibi"* olurdu — biri güncellenir, öteki unutulur ve kullanıcı
    hangi birimin doğru olduğunu bilemez. **DB'nin eklediği tek yeni bilgi SAHİPLİKTİR:**
    çakışan bir terimi hangi cube'un sahiplendiği bir **karardır**, katalogdan türetilemez.

    🔴 Bir terimi **iki** cube sahiplenemez: `(tenant_id, terim)` tekildir. Çift sahiplik
    `metrik_kaydi.cift_sahiplik_denetle` ile de ayrıca denetlenir — veri tabanı kısıtı
    ile mantık kapısı **aynı kuralı iki yerden** korur ve bu bilinçlidir: kısıt yazma
    anını, kapı okuma anını kollar.
    """

    __tablename__ = "metrik_sahipligi"
    __table_args__ = (UniqueConstraint("tenant_id", "terim", name="uq_metrik_terim"),)
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    terim: str = Field(index=True)
    #: Sahiplenen cube. `None` → sahiplik **kaldırıldı** (kayıt silinmez: kararın
    #: geri alındığı da bir kayıttır — kim, ne zaman geri aldı görülebilsin).
    sahip_cube: str | None = None
    # ⚠ Tablo adı `app_user` — `user` PostgreSQL'de ayrılmış sözcüktür ve bu depo
    # onu bilerek yeniden adlandırmış. `foreign_key="user.id"` yazmak 222 testi
    # birden düşürdü: FK çözülemeyince TÜM metadata kurulumu patlıyor.
    karar_veren_user_id: uuid.UUID | None = Field(default=None,
                                                  foreign_key="app_user.id")
    guncellendi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    # FAZ 1.7 — TAZELİK. Yapılandırılan TEK sayı: beklenen senkron periyodu (saat).
    # Eşikler ondan TÜRER (uyarı 2× · hata 5×) ve ayrı ayrı ayarlanamaz — `warn=10g,
    # error=3g` gibi bir çelişki mümkün olsaydı kullanıcı `uyari`'yı hiç görmeden
    # `hata`'ya düşerdi. ÇELİŞEBİLEN İKİ AYAR, ÇELİŞECEK DEMEKTİR.
    tazelik_periyot_saat: int | None = None   # None → app/tazelik.VARSAYILAN_PERIYOT_SAAT
    # 🔴 FAZ 5.16 — **NETLEŞTİRME DÜZEYİ** ∈ `kapali | normal | yuksek`.
    # `None`/`normal` → **bugünkü davranış BİREBİR** (GERİ AL bedava).
    #
    # ⚠ **`kapali` bir sessiz-yanlış kapısı DEĞİLDİR** ve üç sertleştirmeyle bağlanır:
    #   1. Varsayım **cevabın GÖVDESİNDE** görünür (*"Dönem belirtilmedi — bu yıl
    #      varsayıldı."*), bir rozette/tooltip'te değil. MIMARI'nin avladığı sınıf tam
    #      olarak *"varsayımı kenara yazmak"*tır.
    #   2. Ayar **tenant-admin'e kilitli** ve her değişiklik `AuditLog`'a **ayrı satır**.
    #   3. `kapali` düzeyinde üretilen her cevap `kanit_sinifi="probabilistik"` taşır.
    netlestirme_duzeyi: str | None = None
    # FAZ 1.12 — AI Act Md.12/19: otomatik kayıt SAKLAMA süresi (gün). Yasal taban 6 ay
    # (180 gün) ve varsayılan ONUN ALTINA İNMEZ; `None` → 180.
    # ⚠ Bu alan SİLME YAPMAZ, POLİTİKAYI BEYAN EDER: bir saklama süresini uygulamak
    # (retention job) geri alınamaz bir SİLME eylemidir ve FAZ 6'nın onay değişmezine
    # bağlıdır. Beyan edilmiş ama uygulanmamış bir politika, beyan edilmemiş bir
    # politikadan iyidir: DENETLEYİCİ ne beklediğimizi okuyabilir.
    audit_saklama_gun: int | None = None
    # FAZ 2.6 — MALİ YIL BAŞLANGIÇ AYI (1–12). Varsayılan `1` = takvim yılı, yani
    # yapılandırılmamış her tenant BUGÜNKÜ davranışı görür.
    # 🔴 Bu alan bir SESSİZ-YANLIŞI kapatıyor: `"bu yıl"` takvim yılı varsayılıyordu ve
    # mali yılı Nisan'da başlayan bir müşteride cevap yanlış ama rozet YEŞİLDİ.
    mali_yil_baslangic_ay: int = 1
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
    # 🔴 FAZ 6.5 — **IDEMPOTENCY.** *Yeni kuyruk KURULMAZ*: `AskJob` genellenir.
    #
    # Benzersizlik `(client_idempotency_key, tenant_id)` üstündedir — **tek başına anahtar
    # DEĞİL**: iki kiracının aynı anahtarı seçmesi mümkündür ve o an biri ötekinin işini
    # görürdü. *Bir idempotency anahtarı, kiracı sınırının içinde benzersizdir.*
    #
    # ⚠ `None` bırakılabilir: anahtar **göndermeyen** bir çağrı, idempotency **istememiş**
    # demektir ve her seferinde yeni iş üretir. Boş dizeyi anahtar saymak, anahtarsız
    # bütün çağrıları **aynı işe** düşürürdü.
    client_idempotency_key: str | None = Field(default=None, index=True)


class EmbedToken(SQLModel, table=True):
    """FAZ 6.5 — **gömme token'ı**. [bayrak: `embed`]

    🔴 **Looker'ın imzalı-URL modeli DEĞİL**: kapsam bir **kayıttır**, bir URL parametresi
    değil. İmzalı URL'de kapsamı değiştirmek imzayı bozar ama **iptal etmek imkânsızdır**
    — dağıtılmış bir URL geri çağrılamaz. Kayıt `iptal_edildi` ile **anında** düşer.

    🔴 **P0 — `embed` BAYRAĞI BU TURDA AÇILAMAZ.** Yol haritasının şartı: *"Wren RLS'i
    gömülü pano grafiklerini kapsamıyorsa `embed` AÇILMAZ; `always_filter` tek başına
    yeterli sayılmaz."* Ölçüldü: **`motor_cls = "off"`** — motor-RLS **hiç açık değil**
    ve açılması 36 çağrı sitesinin kimlik geçirmesine bağlı (açık borç). Yani şart
    **karşılanmıyor** ve tablo **kurulur ama bayrak kapalı kalır**.
    """

    __tablename__ = "embed_token"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    tenant_id: uuid.UUID = Field(index=True)
    #: `ModelPermission` şeması — hangi cube/boyut/ölçü görünür.
    scope_json: str = "{}"
    #: Günlük çağrı kotası. ⚠ `None` **sınırsız DEĞİL**, *"kota belirtilmedi"* demektir
    #: ve uç onu **reddeder**: sınırsız bir gömme token'ı, faturayı bilinmez yapar.
    kota: int | None = None
    son_kullanim: datetime | None = None
    #: 🔴 **ANINDA DÜŞER.** Bir imzalı URL'nin yapamadığı tek şey budur.
    iptal_edildi: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=_now)


class KanalKimlikEslemesi(SQLModel, table=True):
    """FAZ 6.6 — **sohbet kimliği → DİMA kimliği**. [bayrak: `kanal_kimlik`]

    ## 🔴 ARAŞTIRMANIN EN NET UYARISI

    Hiçbir satıcı sağlam bir *"sohbet-kimliği → BI-kimliği → RLS"* eşlemesi yayımlamamış;
    **Microsoft'un kendi belgesi Slack e-postasının Teams hesabına güvenilir
    eşlenemeyeceğini** söylüyor `[DOĞRULANMADI — birincil kaynak okunmadı]`.

    ## 🔴 `onaylayan_admin_id` ZORUNLU — e-postadan ÇIKARILAMAZ

    En cazip kısayol şudur: *"Slack e-postası `ali@x.com`, DİMA'da da `ali@x.com` var,
    demek ki aynı kişi."* **Değildir.** Bir e-posta adresi bir **iddiadır**, bir kimlik
    kanıtı değil: kanal yöneticisi onu değiştirebilir, bir takma hesap aynı adresi
    gösterebilir, ve bir kez yanlış eşlenen kimlik **o kişinin göremeyeceği veriyi**
    ona açar.

    > *Bir kimliği çıkarımla kurmak, RLS'i çıkarımla kurmaktır.*

    Bu yüzden eşleme **bir insan tarafından onaylanır** ve onaylayanın kimliği **kayda
    girer**: bir gün *"bu kişi bu veriyi neden gördü"* sorulduğunda cevabı olan tek şey
    o satırdır.

    ⚠ Soft-delete (ADR-0019): eşleme kaldırılır, **silinmez** — kaldırılmış bir eşleme
    de bir kayıttır.
    """

    __tablename__ = "kanal_kimlik_eslemesi"
    id: uuid.UUID = Field(default_factory=_uuid, primary_key=True)
    #: `slack | teams | whatsapp`
    kanal: str = Field(index=True)
    kanal_kullanici_id: str = Field(index=True)
    dima_user_id: str = Field(index=True)
    tenant_id: uuid.UUID | None = Field(default=None, index=True)   # RLS
    #: 🔴 **ZORUNLU** — e-postadan çıkarılamaz. Bir insan onayladı ve **kim olduğu** yazılı.
    onaylayan_admin_id: str
    created_at: datetime = Field(default_factory=_now)
    deleted_at: datetime | None = Field(default=None, index=True)


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
    # FAZ 1.8 — AUDIT ZİNCİRİ. "Append-only" bir BEYANDIR, bir mekanizma değil: bir satır
    # DELETE edilirse geriye HİÇBİR İZ kalmaz. Her kayıt bir öncekinin hash'ini taşır;
    # ilki `genesis`. Silme ya da değiştirme zinciri KOPARIR ve `app/audit_zinciri.py::
    # zinciri_dogrula` onu ADIYLA gösterir.
    # ⚠ Zincir eşzamanlı yazımları SIRALAMAZ (çatal mümkün) — ama çatal da TESPİT EDİLİR;
    # sınır gizlenmiyor, raporlanıyor.
    onceki_kayit_hash: str | None = None
    kayit_hash: str | None = None
    contract_id: str | None = None  # ADR-0010 contract'a bağ

class ResearchReasoningStepRecord(SQLModel, table=True):
    """Durable P17 manager proposal/transition under accepted Research authority."""

    __tablename__ = "research_reasoning_step"

    step_id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="research_session.session_id", index=True)
    source_revision: int = Field(index=True)
    source_snapshot_fingerprint: str = Field(index=True)
    parent_obligation_id: str = Field(index=True)
    parent_step_id: str | None = Field(
        default=None,
        foreign_key="research_reasoning_step.step_id",
        index=True,
    )
    depth: int = Field(default=0, index=True)
    branch_id: str = Field(default="legacy-root", index=True)
    intent: str = Field(default="LEGACY", index=True)
    target_kind: str = Field(default="GAP", index=True)
    target_ref: str | None = Field(default=None, index=True)
    stop_scope: str | None = Field(default=None, index=True)
    proposal_id: str = Field(index=True)
    proposal_json: str = Field(sa_column=Column(Text, nullable=False))
    action: str = Field(index=True)
    objective_key: str = Field(index=True)
    bounded_objective: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    rationale: str = Field(sa_column=Column(Text, nullable=False))
    inspected_evidence_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    inspected_claim_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    inspected_material_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    proposal_fingerprint: str = Field(index=True)
    status: str = Field(index=True)
    stop_reason: str | None = Field(default=None, index=True)
    result_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None


class ResearchInvestigationTaskRecord(SQLModel, table=True):
    """Durable child task created by one P17 reasoning step.

    It is subordinate to a sealed P14 obligation and is never appended to
    ResearchSession.obligations.
    """

    __tablename__ = "research_investigation_task"
    __table_args__ = (
        UniqueConstraint(
            "reasoning_step_id",
            name="uq_research_investigation_task_reasoning_step",
        ),
    )

    task_id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="research_session.session_id", index=True)
    reasoning_step_id: str = Field(
        foreign_key="research_reasoning_step.step_id",
        index=True,
    )
    parent_obligation_id: str = Field(index=True)
    bounded_objective: str = Field(sa_column=Column(Text, nullable=False))
    counter_to_claim_id: str | None = Field(default=None, index=True)
    status: str = Field(index=True)
    native_execution_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    material_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    evidence_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None

class BusinessRelationshipPolicyRecord(SQLModel, table=True):
    """P18 governed business-interpretation policy; never native join metadata."""

    __tablename__ = "business_relationship_policy"
    __table_args__ = (
        UniqueConstraint(
            "policy_fingerprint",
            name="uq_business_relationship_policy_fingerprint",
        ),
    )

    policy_id: str = Field(primary_key=True)
    tenant_binding: str = Field(index=True)
    semantic_context_version: str = Field(index=True)
    policy_key: str = Field(index=True)
    source_business_ref: str = Field(index=True)
    target_business_ref: str = Field(index=True)
    business_relationship_statement: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    applicability_scope_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    applicability_scope_fingerprint: str = Field(index=True)
    policy_fingerprint: str = Field(index=True)
    provenance_ref: str = Field(index=True)
    approved_by_subject: str = Field(index=True)
    status: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    retired_at: datetime | None = None


class BusinessRelationshipPolicyUseRecord(SQLModel, table=True):
    """Immutable P18 lineage for one explicit policy requirement resolution."""

    __tablename__ = "business_relationship_policy_use"

    policy_use_id: str = Field(primary_key=True)
    research_session_id: str = Field(
        foreign_key="research_session.session_id",
        index=True,
    )
    obligation_id: str = Field(index=True)
    claim_id: str = Field(
        foreign_key="research_claim.claim_id",
        index=True,
    )
    reasoning_step_id: str = Field(
        foreign_key="research_reasoning_step.step_id",
        index=True,
    )
    requirement_fingerprint: str = Field(index=True)
    policy_id: str | None = Field(
        default=None,
        foreign_key="business_relationship_policy.policy_id",
        index=True,
    )
    policy_fingerprint: str | None = Field(default=None, index=True)
    resolution_status: str = Field(index=True)
    limitation_code: str | None = Field(default=None, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )




class HypothesisRecord(SQLModel, table=True):
    """P19 stable candidate explanation identity; never P16 claim/Evidence truth."""

    __tablename__ = "p19_hypothesis"
    __table_args__ = (
        UniqueConstraint(
            "identity_fingerprint",
            name="uq_p19_hypothesis_identity_fingerprint",
        ),
    )

    hypothesis_id: str = Field(primary_key=True)
    research_session_id: str = Field(
        foreign_key="research_session.session_id",
        index=True,
    )
    obligation_id: str = Field(index=True)
    tenant_binding: str = Field(index=True)
    semantic_context_version: str = Field(index=True)
    statement: str = Field(sa_column=Column(Text, nullable=False))
    identity_fingerprint: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class HypothesisGroundingLink(SQLModel, table=True):
    """Append-only P19 link from one hypothesis to one sealed source identity."""

    __tablename__ = "p19_hypothesis_grounding"
    __table_args__ = (
        UniqueConstraint(
            "link_fingerprint",
            name="uq_p19_hypothesis_grounding_fingerprint",
        ),
    )

    grounding_link_id: str = Field(primary_key=True)
    hypothesis_id: str = Field(
        foreign_key="p19_hypothesis.hypothesis_id",
        index=True,
    )
    source_kind: str = Field(index=True)
    source_ref: str = Field(index=True)
    source_receipt_id: str | None = Field(default=None, index=True)
    relation: str = Field(index=True)
    link_fingerprint: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class RootCauseAssessment(SQLModel, table=True):
    """Immutable P19 aggregate epistemic snapshot; never analytical execution."""

    __tablename__ = "p19_root_cause_assessment"
    __table_args__ = (
        UniqueConstraint(
            "assessment_fingerprint",
            name="uq_p19_root_cause_assessment_fingerprint",
        ),
    )

    assessment_id: str = Field(primary_key=True)
    research_session_id: str = Field(
        foreign_key="research_session.session_id",
        index=True,
    )
    obligation_id: str = Field(index=True)
    tenant_binding: str = Field(index=True)
    semantic_context_version: str = Field(index=True)
    candidate_assessments_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    root_cause_hypothesis_ids_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    aggregate_outcome: str = Field(index=True)
    limitations_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    numeric_provenance_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    mediation_annotations_json: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    assessment_fingerprint: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )



class ReportDocumentRecord(SQLModel, table=True):
    """Immutable P20 governed-report snapshot; references upstream truth without owning it."""

    __tablename__ = "p20_report_document"
    __table_args__ = (
        UniqueConstraint(
            "research_session_id",
            "report_key",
            "revision",
            name="uq_p20_report_document_revision",
        ),
        UniqueConstraint(
            "report_fingerprint",
            name="uq_p20_report_document_fingerprint",
        ),
    )

    report_id: str = Field(primary_key=True)
    research_session_id: str = Field(
        foreign_key="research_session.session_id",
        index=True,
    )
    tenant_binding: str = Field(index=True)
    semantic_context_version: str = Field(index=True)
    report_key: str = Field(index=True)
    revision: int = Field(ge=1, index=True)
    parent_report_id: str | None = Field(
        default=None,
        foreign_key="p20_report_document.report_id",
        index=True,
    )
    coverage_json: str = Field(sa_column=Column(Text, nullable=False))
    statements_json: str = Field(sa_column=Column(Text, nullable=False))
    source_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    limitations_json: str = Field(sa_column=Column(Text, nullable=False))
    source_set_fingerprint: str = Field(index=True)
    report_fingerprint: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )



class DecisionBriefRecord(SQLModel, table=True):
    """Immutable P21 advisory decision-intelligence snapshot."""

    __tablename__ = "p21_decision_brief"
    __table_args__ = (
        UniqueConstraint(
            "tenant_binding",
            "brief_key",
            "revision",
            name="uq_p21_decision_brief_revision",
        ),
        UniqueConstraint(
            "brief_fingerprint",
            name="uq_p21_decision_brief_fingerprint",
        ),
    )

    decision_brief_id: str = Field(primary_key=True)
    report_id: str = Field(
        foreign_key="p20_report_document.report_id",
        index=True,
    )
    tenant_binding: str = Field(index=True)
    semantic_context_version: str = Field(index=True)
    brief_key: str = Field(index=True)
    revision: int = Field(ge=1, index=True)
    parent_decision_brief_id: str | None = Field(
        default=None,
        foreign_key="p21_decision_brief.decision_brief_id",
        index=True,
    )
    objective_json: str = Field(sa_column=Column(Text, nullable=False))
    constraints_json: str = Field(sa_column=Column(Text, nullable=False))
    options_json: str = Field(sa_column=Column(Text, nullable=False))
    tradeoffs_json: str = Field(sa_column=Column(Text, nullable=False))
    recommendation_json: str = Field(sa_column=Column(Text, nullable=False))
    premise_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    assumptions_json: str = Field(sa_column=Column(Text, nullable=False))
    limitations_json: str = Field(sa_column=Column(Text, nullable=False))
    model_provenance_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    source_report_fingerprint: str = Field(index=True)
    decision_source_fingerprint: str = Field(index=True)
    brief_fingerprint: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )



class DecisionAdoptionRecord(SQLModel, table=True):
    """Immutable modern human-adoption truth for one exact P21 DecisionBrief."""

    __tablename__ = "decision_adoption"
    __table_args__ = (
        UniqueConstraint("adoption_fingerprint", name="uq_decision_adoption_fingerprint"),
    )

    adoption_id: str = Field(primary_key=True)
    decision_brief_id: str = Field(foreign_key="p21_decision_brief.decision_brief_id", index=True)
    source_brief_fingerprint: str = Field(index=True)
    tenant_binding: str = Field(index=True)
    actor_user_id: str = Field(index=True)
    actor_authorization_context_json: str = Field(sa_column=Column(Text, nullable=False))
    disposition: str = Field(index=True)
    selected_option_ids_json: str = Field(sa_column=Column(Text, nullable=False))
    human_rationale: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    human_conditions_json: str = Field(sa_column=Column(Text, nullable=False))
    supersedes_adoption_id: str | None = Field(default=None, foreign_key="decision_adoption.adoption_id", index=True)
    recorded_at: datetime = Field(index=True)
    adoption_fingerprint: str = Field(index=True)



class ActionAuthorizationRecord(SQLModel, table=True):
    """Immutable authorization over one exact canonical ActionPlan snapshot."""

    __tablename__ = "action_authorization"
    __table_args__ = (
        UniqueConstraint(
            "authorization_fingerprint",
            name="uq_action_authorization_fingerprint",
        ),
    )

    authorization_id: str = Field(primary_key=True)
    tenant_binding: str = Field(index=True)

    decision_brief_id: str = Field(
        foreign_key="p21_decision_brief.decision_brief_id",
        index=True,
    )
    decision_brief_fingerprint: str = Field(index=True)
    decision_adoption_id: str = Field(
        foreign_key="decision_adoption.adoption_id",
        index=True,
    )
    decision_adoption_fingerprint: str = Field(index=True)

    report_id: str = Field(
        foreign_key="p20_report_document.report_id",
        index=True,
    )
    report_fingerprint: str = Field(index=True)

    action_kind: str = Field(index=True)
    target_system: str = Field(index=True)
    target_resource: str = Field(index=True)

    canonical_plan_json: str = Field(sa_column=Column(Text, nullable=False))
    plan_fingerprint: str = Field(index=True)

    capability_key: str = Field(index=True)
    capability_version: str = Field(index=True)
    capability_fingerprint: str = Field(index=True)

    risk_class: str = Field(index=True)
    reversibility: str
    confirmation_requirement: str
    idempotency_strategy: str

    authorization_policy_id: str = Field(index=True)
    authorization_policy_version: str = Field(index=True)

    authorizer_user_id: str = Field(index=True)
    authorizer_context_json: str = Field(sa_column=Column(Text, nullable=False))

    issued_at: datetime = Field(index=True)
    expires_at: datetime = Field(index=True)

    supersedes_authorization_id: str | None = Field(
        default=None,
        foreign_key="action_authorization.authorization_id",
        index=True,
    )
    authorization_fingerprint: str = Field(index=True)



class ActionWorkRecord(SQLModel, table=True):
    """Immutable revision snapshot for internal organizational work tracking."""

    __tablename__ = "action_work"
    __table_args__ = (
        UniqueConstraint(
            "root_action_work_id",
            "revision",
            name="uq_action_work_root_revision",
        ),
        UniqueConstraint("work_fingerprint", name="uq_action_work_fingerprint"),
    )

    action_work_id: str = Field(primary_key=True)
    root_action_work_id: str = Field(index=True)
    revision: int = Field(ge=1, index=True)
    parent_action_work_id: str | None = Field(
        default=None,
        foreign_key="action_work.action_work_id",
        index=True,
    )
    tenant_binding: str = Field(index=True)

    decision_brief_id: str = Field(
        foreign_key="p21_decision_brief.decision_brief_id",
        index=True,
    )
    decision_brief_fingerprint: str = Field(index=True)
    decision_adoption_id: str = Field(
        foreign_key="decision_adoption.adoption_id",
        index=True,
    )
    decision_adoption_fingerprint: str = Field(index=True)
    action_authorization_id: str | None = Field(
        default=None,
        foreign_key="action_authorization.authorization_id",
        index=True,
    )
    action_authorization_fingerprint: str | None = Field(default=None, index=True)

    title: str = Field(sa_column=Column(Text, nullable=False))
    work_intent_json: str = Field(sa_column=Column(Text, nullable=False))
    owner_user_id: str = Field(index=True)
    owner_context_json: str = Field(sa_column=Column(Text, nullable=False))
    due_at: datetime | None = Field(default=None, index=True)

    status: str = Field(index=True)
    blocker_reason: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    completion_reference: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    transition_history_json: str = Field(sa_column=Column(Text, nullable=False))

    source_fingerprint: str = Field(index=True)
    work_fingerprint: str = Field(index=True)
    created_at: datetime = Field(index=True)



class OutcomeObservationRecord(SQLModel, table=True):
    """Immutable organizational Outcome over governed analytical provenance."""

    __tablename__ = "outcome_observation"
    __table_args__ = (
        UniqueConstraint(
            "outcome_fingerprint",
            name="uq_outcome_observation_fingerprint",
        ),
    )

    outcome_id: str = Field(primary_key=True)
    tenant_binding: str = Field(index=True)
    action_work_id: str = Field(
        foreign_key="action_work.action_work_id",
        index=True,
    )
    action_work_fingerprint: str = Field(index=True)
    decision_brief_id: str = Field(
        foreign_key="p21_decision_brief.decision_brief_id",
        index=True,
    )
    decision_adoption_id: str = Field(
        foreign_key="decision_adoption.adoption_id",
        index=True,
    )

    evidence_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    claim_ids_json: str = Field(sa_column=Column(Text, nullable=False))
    report_id: str | None = Field(
        default=None,
        foreign_key="p20_report_document.report_id",
        index=True,
    )
    report_fingerprint: str | None = Field(default=None, index=True)

    baseline_definition: str = Field(sa_column=Column(Text, nullable=False))
    baseline_window: str = Field(sa_column=Column(Text, nullable=False))
    observation_window: str = Field(sa_column=Column(Text, nullable=False))
    expected_target_ref: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    observed_result_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    limitations_json: str = Field(sa_column=Column(Text, nullable=False))
    classification: str = Field(index=True)

    source_fingerprint: str = Field(index=True)
    outcome_fingerprint: str = Field(index=True)
    observed_at: datetime = Field(index=True)
    recorder_user_id: str = Field(index=True)



class InstitutionalMemoryEntryRecord(SQLModel, table=True):
    """Immutable precedent/context index over exact sealed artifact identities."""

    __tablename__ = "institutional_memory_entry"
    __table_args__ = (
        UniqueConstraint(
            "memory_fingerprint",
            name="uq_institutional_memory_fingerprint",
        ),
    )

    memory_id: str = Field(primary_key=True)
    tenant_binding: str = Field(index=True)
    role: str = Field(index=True)
    problem_type: str = Field(index=True)
    domain: str = Field(index=True)
    entity_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    metric_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    source_refs_json: str = Field(sa_column=Column(Text, nullable=False))
    summary: str = Field(sa_column=Column(Text, nullable=False))
    limitations_json: str = Field(sa_column=Column(Text, nullable=False))
    precedent_of_memory_id: str | None = Field(
        default=None,
        foreign_key="institutional_memory_entry.memory_id",
        index=True,
    )
    source_set_fingerprint: str = Field(index=True)
    memory_fingerprint: str = Field(index=True)
    created_at: datetime = Field(index=True)
    indexed_by_user_id: str = Field(index=True)
