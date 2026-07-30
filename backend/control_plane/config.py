"""Control-plane settings (env, prefix ``DIMA_``).

Auth bounded-context'in kendi ayarları — ``app.config.Settings``'ten ayrı tutulur ki
ileride ayrı servise çıkarken taşıma olmasın (ADR-0014 Karar 3/7).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import BASE_DIR


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="DIMA_",
        extra="ignore",
    )

    # --- Control-plane DB ------------------------------------------------
    # Prod: Postgres (Railway private network). Demo/lokal: SQLite dosyası → Postgres
    # olmadan da auth ayakta (ADR-0012 "bu fazda platform-DB yok" ile uyumlu geçiş).
    database_url: str = f"sqlite:///{BASE_DIR / 'logs' / 'control_plane.db'}"

    # --- JWT (saka-standards 02-authentication) --------------------------
    # ZORUNLU: access ve refresh için FARKLI secret. Üretimde env'den gelir; boşsa
    # startup'ta üretilir (yalnız lokal/dev — restart'ta oturumları düşürür).
    jwt_secret: str = ""
    jwt_refresh_secret: str = ""
    # Admin plane'in AYRI secret çifti (ADR-0015 izolasyonu): public süreç ele geçse
    # bile env'indeki secret'larla admin-api'ye geçerli token BASILAMAZ.
    admin_jwt_secret: str = ""
    admin_jwt_refresh_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_ttl_seconds: int = 15 * 60          # 15 dk
    refresh_ttl_seconds: int = 7 * 24 * 60 * 60  # 7 gün
    # Rotation sertleştirmesi: paralel sekme yarışı için hoşgörü penceresi (reuse
    # bu pencere içindeyse hırsızlık sayılmaz) + family mutlak ömrü (kayan oturum
    # sonsuza uzayamaz).
    refresh_grace_seconds: int = 10
    refresh_family_max_seconds: int = 30 * 24 * 60 * 60  # 30 gün

    # --- Login brute-force sınırı (ADR-0015 Karar 5: "JWT auth + rate limit") ----
    login_max_attempts: int = 5        # pencere içindeki başarısız deneme sınırı
    login_window_seconds: int = 15 * 60

    # --- Superadmin public-plane erişimi (ADR-0015 K7, log-only + IP kapısı) ----
    # Superadmin ürün UI'ından (public plane) YALNIZ bu IP'lerden login olabilir
    # (virgülle ayrık; boş = fail-closed, superadmin public login tamamen kapalı).
    # Lokal dev: 127.0.0.1. Prod: core ekibin statik IP'leri (Railway/Cloudflare'de de
    # tanımlı). Tenant kullanıcıları bu listeden ETKİLENMEZ.
    superadmin_ip_allowlist: str = ""
    # Proxy arkasında gerçek istemci IP'si X-Forwarded-For'dadır; YALNIZ güvenilir bir
    # proxy (Cloudflare/Railway edge) önündeyken true yapılır — aksi halde spoof edilebilir.
    trust_forwarded_for: bool = False

    def superadmin_ip_list(self) -> list[str]:
        return [x.strip() for x in self.superadmin_ip_allowlist.split(",") if x.strip()]

    # --- MFA (TOTP) ------------------------------------------------------
    # ADR-0015: superadmin'de 2FA zorunlu. Dev'de enrollment akışı olmadan kilitlenmemek
    # için bayrak; PROD'da True — mfa_secret'sız superadmin admin plane'e giremez.
    require_superadmin_mfa: bool = False

    # --- Refresh cookie (HTTP-only) --------------------------------------
    cookie_domain: str = ""        # cross-subdomain için ".domain.com"; boş = host-only
    cookie_secure: bool = False    # prod'da True (HTTPS)
    cookie_name: str = "dima_refresh"
    # Admin cookie SameSite: LOKAL admin UI → CANLI admin-api topolojisi CROSS-ORIGIN'dir
    # (admin.dima.localtld → dima-sadmin-api.upcytech.com); tarayıcının cookie'yi XHR'da
    # göndermesi için prod'da "none" (+ cookie_secure=true) gerekir. Lokal-lokal: "lax".
    admin_cookie_samesite: str = "lax"     # lax | none | strict

    # --- Müşteri DB kimlik bilgisi şifrelemesi (ADR-0017, KEK admin-api'de) ----
    # base64 kodlu 32 bayt anahtar; DbConnection.secret_ciphertext AES-256-GCM ile
    # bununla şifrelenir. Boş = bağlantı sırrı yazılamaz (fail-closed).
    cred_kek: str = ""

    # --- Bootstrap -------------------------------------------------------
    # İlk superadmin (yalnız boş DB'de seed edilir; prod'da env ile verilir).
    bootstrap_superadmin_email: str = ""
    bootstrap_superadmin_password: str = ""

    # --- Admin plane (ADR-0015) -----------------------------------------
    # admin_app CORS: lokal superadmin UI (dima-admin-frontend) origin'leri.
    # localtld: admin.dima.localtld + localhost fallback.
    admin_cors_origins: str = (
        "http://admin.dima.localtld,"
        "http://localhost:3001,"
        "http://localhost:3000"
    )

    def admin_cors_list(self) -> list[str]:
        return [o.strip() for o in self.admin_cors_origins.split(",") if o.strip()]

    def effective_database_url(self) -> str:
        # .env'de "DIMA_DATABASE_URL=" (boş) → default SQLite. Böylece boş değer
        # create_engine("")'i patlatmaz; "unset" ile aynı davranır.
        return (
            self.database_url.strip()
            or f"sqlite:///{BASE_DIR / 'logs' / 'control_plane.db'}"
        )


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
