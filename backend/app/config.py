"""Runtime configuration, loaded from environment / .env (prefix ``DIMA_``)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root of dima-backend (the parent of the ``app`` package).
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Environment-driven settings.

    Paths in ``project_dir`` and the connection ``url`` may be relative; they are
    resolved against the backend repo root so the demo runs from any cwd.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="DIMA_",
        extra="ignore",
    )

    # --- Wren project / data source -------------------------------------
    # ADR-0005 kompozisyon: packs/ + companies/<company> → project_dir (DERLENMİŞ çıktı).
    # Başlangıçta otomatik compose+build edilir; yeni dikey = yeni YAML.
    company: str = "demo-boyahane"
    project_dir: str = "demo/wren-project"
    datasource: str = "duckdb"
    # JSON object of connection parameters WITHOUT the ``datasource`` key.
    connection_info: str = '{"url": "demo/data", "format": "duckdb"}'

    # --- LLM sağlayıcı ---------------------------------------------------
    # auto: anthropic → xai → gemini → groq → ollama (ayakta ise) → kural-tabanlı.
    # Açık değerler: auto | anthropic | xai | gemini | groq | ollama | rule
    llm_provider: str = "auto"
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    # Faz 4.2 (dış yol haritası 2.11 "model sınıfı seçimi" karşılığı, 31 Temmuz 2026):
    # select_cube/refine_cube (Intent-JSON — katalogdan ölçü/boyut/filtre SEÇİMİ, basit
    # yapılandırılmış çıktı) generate_sql/repair'dan (Discovery — ham SQL üretimi, çok
    # daha zor bir görev) DAHA UCUZ/HIZLI bir modelle yanıtlanabilir. Boş (varsayılan) =
    # `llm_model` ile AYNI (davranış/geriye-uyum değişmez) — yalnız Anthropic'e somut,
    # gerçek bir ucuz-model varsayılanı verildi (diğer sağlayıcıların varsayılan modelleri
    # zaten hafif katman, ayrıca ucuzlatmaya gerek yok).
    anthropic_select_model: str = "claude-haiku-4-5-20251001"
    # xAI Grok (OpenAI-uyumlu: https://console.x.ai — hesapta kredi gerekir)
    xai_api_key: str = ""
    xai_base_url: str = "https://api.x.ai/v1"
    xai_model: str = "grok-4.5"
    xai_select_model: str = ""
    # Google Gemini (ücretsiz katman; OpenAI-uyumlu endpoint)
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    gemini_model: str = "gemini-flash-lite-latest"
    gemini_select_model: str = ""
    # Groq (ücretsiz key: https://console.groq.com)
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-120b"
    groq_select_model: str = ""
    # Ollama (tam yerel, anahtarsız: `brew install ollama` + `ollama pull ...`)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5-coder:7b"
    ollama_select_model: str = ""

    # A#5 (ADR-0008): kural-tabanlı serbest-SQL YEDEĞİ yalnız demo/geliştirme içindir.
    # Üretimde False: LLM yoksa ya da hata verirse TAHMİN yerine dürüst ret döner
    # (kural yedeği yalnız demo şemasını bilir; gerçek şemada sessiz-yanlış üretir).
    rule_fallback: bool = True

    # Self-consistency (ADR-0008 + literatür önerisi #1): LLM cube-seçimi k kez
    # örneklenir, kanonik CubeQuery üzerinde oylanır; uyuşmazlık → chip. 1 = kapalı.
    consistency_k: int = 3
    # Verified Query Repository dosyası (boş = <proje>/knowledge/verified/queries.jsonl).
    # Testler izolasyon için geçici yola yönlendirir.
    vqr_path: str = ""

    # VQR embedder anahtarı: auto | off. "off" → fastembed HİÇ denenmez, doğrudan
    # F5-token sözlüksel fallback kullanılır (`_lex_score`, eşik `_LEX_EXACT_THRESHOLD`).
    #
    # NEDEN VAR (canlı bulgu, 2 Ağustos 2026): `TextEmbedding("intfloat/multilingual-e5-large")`
    # ilk kullanımda HF Hub'dan ~2.2 GB ONNX indirir. Kimliksiz (HF_TOKEN'sız) indirme
    # ORANLANIYOR ve pratikte DURUYOR — ölçüldü: 20 saniyede 0 bayt ilerleme, `.incomplete`
    # dosyası 67 MB'da takılı. `fastembed`/`requests` katmanında üst-sınır (timeout) YOK.
    # Sonuç: taze bir konteynerde pytest paketi SAATLERCE asılı kalıyordu (kullanıcı
    # bildirimi: ~10 saat, hiç bitmedi). `_embedder()`'ın non-blocking kilidi ikinci bir
    # thread'i korur ama İNDİREN thread'in kendisini korumaz.
    #
    # Testler bunu "off" yapar (tests/conftest.py) → hermetik, ağsız, deterministik koşum.
    # Üretimde "auto" kalır; hava-boşluklu (air-gapped) kurulumda "off" meşru bir seçenektir.
    # Model önbelleğinin KALICI olması ayrı ve zorunlu bir iş: docker-compose'da
    # /tmp/fastembed_cache bir named volume olmalı, yoksa her yeniden-build 2.2 GB'ı
    # sıfırdan indirir (HANDOFF #4'ün uygulanmamış duran önerisi).
    vqr_embedder: str = "auto"

    # MOTOR-SEVİYESİ SQL POLİTİKASI (Faz A3) — `off` | `shadow` | `on`.
    #
    # `wren.policy.validate_sql_policy` strict modda iki şey yapar: (1) **45 veri-okuyucu
    # tablo fonksiyonunu** (`read_csv`, `read_parquet`, `pg_read_file`, `dblink`,
    # `postgres_scan`, …) SQL'in HER konumunda bloklar — upstream bunu bir güvenlik
    # açığı olarak kapattı (issue #2409); (2) MDL'de TANIMLI OLMAYAN tabloya referansı
    # reddeder. Dima'nın `guard_sql`'i (iki regex: `^(with|select)` + yasak kelime)
    # bunların **hiçbirini** yakalamaz — `SELECT * FROM read_csv('/etc/passwd')` ondan
    # GEÇER (ölçüldü). Bugün DataFusion o fonksiyonu tanımadığı için planlamada patlıyor;
    # yani savunma var ama **tesadüfi**, tasarlanmış değil.
    #
    # Neden varsayılan `shadow`: ölçüldü ki demo katalogunda strict hiçbir meşru yolu
    # kırmıyor (cube SQL, `always_filter` sarmalayıcısı, üretilen-boyut join'i — üçü de
    # aynen geçti; demo'daki 47 tablonun 47'si de MDL'de). Ama MSSQL kiracılarında
    # Discovery'nin ham SQL'i MDL-dışı bir tabloya dokunuyor olabilir. Bu **istenen**
    # reddir (semantic-first) ama **ölçülmeden** açılmamalı: `shadow` reddetmez, yalnız
    # "strict olsaydı reddedilirdi" diye loglar. Telemetri birikince `on`a alınır.
    strict_sql_policy: str = "shadow"

    # Strict moddan BAĞIMSIZ çalışan fonksiyon kara listesi (`engine._plan` koşulu `or`).
    # Boş bırakılırsa devre dışı; buraya yazılan her ad `off` modunda bile bloklanır.
    denied_sql_functions: str = ""

    # Zamanlanmış raporlar (ADR-0011): tanım + koşum durumu (last_run) + bildirim HEPSİ
    # tek-kaynak DB'de (schedule_definition + notification_log). Query Contract kanıtı da
    # DB'de (contract_log, ADR-0010). Dosya-yolu config'leri Faz 3'te kaldırıldı.
    scheduler_enabled: bool = True

    # Teslim kanalları (ADR-0011): zamanlanmış rapor/alarm bildirimi in-app bell'e
    # HER ZAMAN düşer; ek kanallar (e-posta) opsiyonel. Resend ilk e-posta sağlayıcısı;
    # key boşsa e-posta kanalı sessizce atlanır (in-app teslim etkilenmez). Ürün maili
    # BACKEND'de yönetilir — frontend'deki Resend yalnız pazarlama iletişim formu içindir.
    resend_api_key: str = ""
    resend_from: str = "dima <bildirim@dima.upcytech.com>"

    # Etkileşim logu (interaction_log tablosu, Postgres). Test/eval koşumları KAPATIR — canlı
    # log gerçek kullanıcı oturumlarını temsil etmeli (log→golden döngüsü kirlenmesin).
    interaction_log: bool = True

    # --- Guards / server -------------------------------------------------
    max_result_rows: int = 1000
    # localtld domaini `.localtld` (localtld servisi). localhost fallback da eklidir.
    cors_origins: str = (
        "http://frontend.dima.localtld,"
        "http://localhost:3000"
    )

    # --- Derived helpers -------------------------------------------------
    def resolved_project_dir(self) -> Path:
        p = Path(self.project_dir)
        return p if p.is_absolute() else (BASE_DIR / p)

    def connection_dict(self) -> dict:
        conn = json.loads(self.connection_info)
        # Resolve a relative DuckDB/file ``url`` against the backend root.
        url = conn.get("url")
        if url and not Path(url).is_absolute():
            conn["url"] = str((BASE_DIR / url).resolve())
        return conn

    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
