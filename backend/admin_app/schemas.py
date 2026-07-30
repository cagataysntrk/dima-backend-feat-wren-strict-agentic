"""Admin request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)
    otp: str | None = None  # TOTP kodu (mfa_secret'lı hesaplarda zorunlu)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TenantCreate(BaseModel):
    slug: str = Field(min_length=2)
    name: str = Field(min_length=1)
    # Veri-düzlemi yapılandırması: sektör pack'leri (listede önce gelen kazanır) +
    # modüller (None = sektör varsayılanları). Boş sektorler = config satırı yazılmaz
    # (repo'daki elle yazılmış company.yml, varsa, geçerli kalır).
    sektorler: list[str] = []
    moduller: list[str] | None = None
    # ADR-0017 kaynak faseti: kaynak pack'leri + önekli şemalarda firma/dönem kapsamı.
    kaynaklar: list[str] | None = None
    firma_no: int | None = Field(default=None, ge=1, le=999)
    donem_no: int | None = Field(default=None, ge=1, le=99)
    # AKTİF DİL SETİ (§7b) — firmanın kullandığı diller; sıra = öncelik. None = varsayılan
    # (tr+en). Desteklenen diller router'da doğrulanır (şu an tr, en).
    diller: list[str] | None = None


class TenantConfigUpdate(BaseModel):
    sektorler: list[str] = Field(min_length=1)
    moduller: list[str] | None = None
    kaynaklar: list[str] | None = None
    firma_no: int | None = Field(default=None, ge=1, le=999)
    donem_no: int | None = Field(default=None, ge=1, le=99)
    diller: list[str] | None = None  # §7b aktif dil seti (None = varsayılan tr+en)


class TenantOut(BaseModel):
    id: str
    slug: str
    name: str
    status: str
    sektorler: list[str] | None = None  # None = DB config yok (repo dosyası geçerli)
    moduller: list[str] | None = None
    kaynaklar: list[str] | None = None
    firma_no: int | None = None
    donem_no: int | None = None
    diller: list[str] | None = None  # §7b aktif dil seti


class TenantStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|suspended)$")


class SAUserCreate(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    tenant_id: str | None = None       # superadmin oluşturuluyorsa None
    role_key: str = "owner"            # tenant kullanıcısının başlangıç rolü
    is_superadmin: bool = False


class SAUserOut(BaseModel):
    id: str
    email: str
    tenant_id: str | None
    is_superadmin: bool


class ConnectionCreate(BaseModel):
    """Müşteri DB bağlantısı (ADR-0017): parola yalnız istekte yaşar, DB'ye
    AES-256-GCM şifreli yazılır; yanıtlarda asla dönmez."""

    tenant_id: str
    datasource: str = "mssql"
    host: str = Field(min_length=1)
    port: int = Field(default=1433, ge=1, le=65535)
    database: str = Field(min_length=1)
    user: str = Field(min_length=1)
    password: str = Field(min_length=1)
    trust_server_certificate: bool = True


class ConnectionOut(BaseModel):
    id: str
    tenant: str
    datasource: str
    topology: str
    host: str
    port: int
    database: str
    user: str
    has_secret: bool


class ConnectionTestOut(BaseModel):
    ok: bool
    database: str
    server_version: str


class FingerprintOut(BaseModel):
    tablo_sayisi: int
    oneriler: list[dict]        # [{key, skor, eslesen_tablolar, eslesen_desenler}]
    logo_kapsamlari: list[dict]  # [{firma_no, donem_no, tablo}]


class CloneStart(BaseModel):
    """Clone/sync başlatma (ADR-0017 K9). scope: hangi tablolar. kind endpoint'ten gelir."""

    scope: str = "all"                  # all (tüm base tablo) | core (pack gereksinimi) | list
    tables: list[str] | None = None     # scope='list' ise açık tablo adları
    target_conn_id: str | None = None   # hedef (mirror) bağlantı; None = tenant api_sync / lab


class CloneJobOut(BaseModel):
    id: str
    tenant: str
    kind: str                           # clone | sync
    status: str                         # pending | running | completed | failed
    target_db: str | None
    total_tables: int
    done_tables: int
    ok_tables: int
    skip_tables: int
    fail_tables: int
    rows_total: int
    current_table: str | None
    message: str | None
    error: str | None
    started_at: str
    finished_at: str | None


class CloneEndpoint(BaseModel):
    """Bir tenant'ın tek DB ucu (canlı ya da klon) — card içi satır."""

    id: str
    host: str
    port: int
    database: str
    user: str
    datasource: str
    topology: str


class CloneCard(BaseModel):
    """Tenant başına clone kartı: canlı (cloud_direct) + klon (api_sync) YAN YANA +
    son clone bilgisi (kullanıcı isteği: tek card içinde original + clone + tarih)."""

    tenant: str
    tenant_id: str
    live: CloneEndpoint | None = None       # cloud_direct — clone KAYNAĞI
    clone: CloneEndpoint | None = None       # api_sync — dima-api'nin sorguladığı ayna
    last_clone_at: str | None = None
    last_clone_status: str | None = None
    last_clone_kind: str | None = None
    last_clone_rows: int | None = None
    active_job_id: str | None = None         # koşan/bekleyen iş varsa


class SynonymCreate(BaseModel):
    """Canlı sinonim overlay'i (ADR-0018 katman 3): pack+arketip üstüne additive biner."""

    scope_type: str = "global"          # global | tenant
    scope_id: str | None = None         # tenant slug (tenant kapsamında zorunlu)
    cube: str
    field_kind: str = "measure"         # cube | measure | dimension
    field_name: str | None = None       # measure/dimension adı (cube-düzeyinde None)
    synonyms: list[str] = Field(min_length=1)
    lang: str | None = None            # dil kodu (tr/en/…); None = yerel/belirsiz (§7b)
    approved: bool = False              # False = aday kuyruğu (canlıya inmez)
    source: str = "manual"             # manual | mined


class SynonymOut(BaseModel):
    id: str
    scope_type: str
    scope_id: str | None
    cube: str
    field_kind: str
    field_name: str | None
    synonyms: list[str]
    lang: str | None = None
    approved: bool
    source: str
