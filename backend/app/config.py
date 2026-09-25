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
    # Uzak DB sorgu zaman aşımı, SANİYE (Faz B). 0 = kapalı (motorun kendi varsayılanı).
    # ÖLÇÜLDÜ: motor `statement_timeout`'u yalnız postgres/clickhouse/trino/bigquery için
    # enjekte ediyor (180 sn) — `mssql` dalı YOK ve üretim tenant'larımız mssql, yani
    # kilitlenmiş bir sorgu SÜRESİZ asılabiliyordu. 60 sn seçildi: etkileşimli bir BI
    # cevabı için 180 fazla, ama `/report` ve zamanlanmış koşumların ağır sorguları için
    # 15-20 az. duckdb'de UYGULANMAZ (gömülü — ağ yok, kilitlenecek uzak sunucu yok).
    db_statement_timeout: int = 60

    # --- Dima V2 rollout --------------------------------------------------
    # Day 0: new semantic/conversation core is dark by default. Rollback is an
    # explicit tenant-server setting, never a per-request silent legacy fallback.
    ask_v2_enabled: bool = False

    # --- P14 native Metabase gateway ------------------------------------
    # Authentication is request-scoped pass-through; no native credential is stored here.
    metabase_native_base_url: str = ""
    metabase_engine_sha: str = "cbe313af9ac2d5960f662068e433d328d896fb06"
    metabase_engine_upstream_sha: str = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
    metabase_engine_runtime_tag: str = "v0.63.18-dima.6"
    metabase_engine_image_digest: str = "sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353"
    metabase_engine_build_identity: str = "github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06"
    metabase_engine_image_identity: str = "sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353"

    # --- LLM sağlayıcı ---------------------------------------------------
    # auto: anthropic → xai → gemini → groq → ollama (ayakta ise) → kural-tabanlı.
    # Açık değerler: auto | anthropic | xai | gemini | groq | openrouter | ollama | rule
    llm_provider: str = "auto"
    # ⚠️ FAZ 0.16 — **AYRILMIŞ ÖLÇÜM ANAHTARI.** Ürün anahtarından **ayrıdır**: ölçüm
    # turları (`lab/*.py --live`) ile üretim trafiği aynı kotayı paylaşırsa, ölçüm
    # üretimi boğar ya da üretim ölçümü boğar — ikisi de sessizce olur. Ölçüldü
    # (`50402d3`): *"gemini-flash-lite 2×429 … nemotron-ultra ⊘ 54×429 — ücretsiz katman
    # doydu"* ve *"ölçümün gerçek gürültü kaynağı BENİMDİ: üç konteyner aynı anda API'yi
    # dövüyordu."* Bu belgenin **151 maddesinin her «önce ölç» kapısı** o kotaya bağlı.
    #
    # Tanımsızsa davranış **bugünküyle birebir aynıdır** (GERİ AL): ürün anahtarı kullanılır.
    # YALNIZ `lab/` araçları okur; üretim yolu bu alana **hiç bakmaz**.
    measure_api_key: str = ""
    measure_provider: str = ""
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
    # OpenRouter (tek anahtarla ONLARCA model — açık kaynak dâhil).
    #
    # Neden eklendi: Gemini ücretsiz katmanı ölçüm turlarında **HTTP 429**'a çarpıyor
    # (kullanıcının uyardığı günlük kota). OpenRouter'ın açık-kaynak modelleri daha yüksek
    # hacimli A/B ölçümüne izin veriyor. Sağlayıcı OpenAI-uyumlu olduğu için **yeni bir
    # istemci yazılmadı** — `OpenAICompatibleSqlGenerator` aynen kullanılıyor.
    #
    # ⚠️ Zincirdeki YERİ bilinçli: `gemini`/`groq`'tan SONRA. Ölçüm sağlayıcısı, üretimin
    # varsayılan sağlayıcısını **değiştirmemeli**; yalnız onlar tükendiğinde devreye girer.
    openrouter_api_key: str = ""
    # 🔴 **YEDEK ANAHTAR ZİNCİRİ (kullanıcı kararı, 2026-08-07).** OpenRouter'ın ücretsiz
    # katmanı kredi dolunca `402 Payment Required` verir ve **tüm LLM yolu susar** —
    # ölçüm turu ürünü değil **faturayı** ölçmeye başlar (ve bu bir kez oldu).
    #
    # ⚠ Zincir **döngüseldir**: anahtarlar sırayla denenir ve tur başa döndüğünde ilk
    # anahtarın kotası çoktan tazelenmiş olur. Yani bu bir yedek değil bir **rotasyon**.
    #
    # Virgülle ayrılmış liste. Boşsa `openrouter_api_key` tek başına kullanılır —
    # yani varsayılan davranış **birebir bugünkü**.
    #
    # *Bir ölçüm aracının durması, ölçtüğü şeyin bozulmasından daha sinsidir: biri
    # kırmızı verir, öteki sessizce sıfır ölçer.*
    openrouter_api_keys: str = ""

    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # V2 operational default (2026-09-21): tek source-of-truth model.
    # GitHub Environment variable DIMA_OPENROUTER_MODEL bunu override edebilir.
    # select_model boş bırakılırsa LLM adapter ana modeli aynen kullanır.
    # Cost-first hot path: structured turn interpretation/extraction/clarification/repair.
    # Harder reasoning is escalated explicitly; the fast default must stay cheap.
    openrouter_model: str = "google/gemini-2.5-flash-lite"
    openrouter_select_model: str = ""

    # --- Dima V2 model roles ---------------------------------------------
    # Concrete model names are configuration; V2 product code asks for a role.
    # Blank FAST model falls back to the configured provider default. REFERENCE is
    # intentionally blank by default so a production-certification run must name or
    # configure the stronger candidate explicitly instead of silently reusing FAST.
    v2_fast_language_provider: str = "openrouter"
    v2_fast_language_model: str = ""
    v2_reference_language_provider: str = "openrouter"
    v2_reference_language_model: str = ""
    v2_research_manager_provider: str = "openrouter"
    v2_research_manager_model: str = ""
    # Bounded semantic interpretation role. Blank values intentionally fall back to
    # FAST_LANGUAGE configuration; semantic truth/handle minting remains deterministic.
    v2_semantic_linker_provider: str = ""
    v2_semantic_linker_model: str = ""
    # Typed temporal cognition is a distinct contract from semantic candidate selection.
    # Blank values fall back to REFERENCE_LANGUAGE; deterministic TemporalBindingEngine
    # remains the calendar/date authority after the model emits a typed choice.
    v2_temporal_normalizer_provider: str = ""
    v2_temporal_normalizer_model: str = ""
    # Role-scoped structured inference policy. FAST keeps reasoning off for latency/cost;
    # REFERENCE may use reasoning because correctness certification is its purpose and
    # some capable endpoints require it. Concrete model names do not participate here.
    v2_fast_language_reasoning: bool = False
    v2_reference_language_reasoning: bool = True
    v2_research_manager_reasoning: bool = True
    v2_semantic_linker_reasoning: bool = False
    v2_temporal_normalizer_reasoning: bool = True
    # Native JSON-schema replies are compact. Bound only the provider output reservation;
    # semantic contracts/context are unchanged. Prevents OpenRouter reserving full 65k.
    v2_structured_max_tokens: int = 16384
    v2_manager_lab_enabled: bool = False
    # Internal scoped setting written by ModelRolePolicy before build_generator().
    # Legacy callers retain False, preserving the historical hot-path behavior.
    v2_structured_reasoning_enabled: bool = False
    # Ollama (tam yerel, anahtarsız: `brew install ollama` + `ollama pull ...`)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5-coder:7b"
    ollama_select_model: str = ""

    # A#5 (ADR-0008): kural-tabanlı serbest-SQL YEDEĞİ yalnız demo/geliştirme içindir.
    # Üretimde False: LLM yoksa ya da hata verirse TAHMİN yerine dürüst ret döner
    # (kural yedeği yalnız demo şemasını bilir; gerçek şemada sessiz-yanlış üretir).
    #
    # 2 Ağustos 2026: VARSAYILAN False YAPILDI. Yukarıdaki yorum zaten "üretimde False"
    # diyordu ama varsayılan True'ydu — yani niyet belgeliydi, kod tersini yapıyordu.
    # `RuleBasedSqlGenerator` demo-boyahane kolon adlarını (`fire_kg`, `agirlik_kg`,
    # `tutar`) ve tablo adlarını SABİT KODLAR; bu adlar başka bir tenant'ta da bulunabilir
    # ve o zaman MAKUL AMA YANLIŞ SQL üretir. Rozeti dürüst (`source="rule"`) olduğu için
    # silinmedi — demo/geliştirme için `DIMA_RULE_FALLBACK=true` ile açılır.
    rule_fallback: bool = False

    # Self-consistency (ADR-0008 + literatür önerisi #1): LLM cube-seçimi k kez
    # örneklenir, kanonik CubeQuery üzerinde oylanır; uyuşmazlık → chip. 1 = kapalı.
    consistency_k: int = 3
    # 🔴 **INTENT'İN BÜTÇESİ.** Ölçüldü (canlı, openrouter): tek bir Intent çağrısı
    # **98.176 ms**. Kullanıcı 1,5 dakika bekleyip *"anlayamadım"* aldı.
    # ⚠ Anlatıdan (8 sn) gevşek, çünkü Intent bir **süs değil cevabın kendisi**: erken
    # kesmek kapsamı düşürür. Ama sınırsız da olamaz.
    # ⚠ `requests`'in `timeout`'u **okuma başına**dır; toplam süreyi ancak çağıran sınırlar.
    intent_azami_saniye: float = 20.0

    #: 🔴 `§55` — **Discovery'nin duvar-saati bütçesi.** En güvenmediğimiz basamak
    #: (`§0.0`: *"yan dükkândan sipariş"*) en uzun bekleten basamaktı: ölçüldü 63.526 ms.
    #: ⚠ Aşımda cevap düşmez, **yol** düşer — dürüst ret zaten oradadır.
    discovery_azami_saniye: float = 25.0

    # 🔴 **ANLATININ ZAMAN BÜTÇESİ** — canlı ölçüm (2026-08-07): aynı sağlayıcı aynı iş
    # için **2.936 ms ↔ 22.564 ms ↔ 69.399 ms** yaptı, ve *flash* adlı bir modelde.
    #
    # ⚠ Anlatı bir **süslemedir**: altındaki `summary` zaten yazılı ve doğru. 22 saniyelik
    # bir üslup için kullanıcıyı bekletmek, cevabı geciktirmenin karşılığı olmayan biçimi.
    # Aşılırsa anlatı **düşer**, cevap **düşmez** — en kötü durum yine *"süssüz ama doğru"*.
    #
    # *Bir süsün bütçesi, süslediği şeyin süresini aşamaz.*
    anlati_azami_saniye: float = 8.0

    # 🔴 **VQR KAPALI (kullanıcı kararı, 2026-08-07): *"o bambaşka bir ar-ge konusu."***
    #
    # Doğrulanmış soru deposu merdivenin **İLK** basamağıdır — yani bir kayıt dondurulduğu
    # anda deterministik yolun sonraki iyileşmelerini **es geçtirir**. Canlı denetimde tam
    # bu görüldü: *"şubatta ciro ocağa göre nasıl değişti"* `source=vqr` ile 434 ms'de
    # dönüyordu ve cevabı **beyanlı kısmiydi** (`eksik_niyet=['kiyas','trend']`) — aynı
    # soruyu `Ö10` ile düzelttiğimiz halde kullanıcı **eski cevabı** görecekti.
    #
    # ⚠ Mekanizma **silinmedi, kapatıldı** (`MIMARI §10`: *kapananlar işaretlenir,
    # silinmez*). Depo, benzerlik kapısı, güven kapısı, şema-sürüm kapısı ve `/verify`
    # ucu yerinde duruyor; tek anahtar bu. `DIMA_VQR_ACIK=1` ile geri gelir.
    #
    # *Bir öğrenme deposu, öğrendiğini ne zaman unutacağını bilmiyorsa, öğrenmez —
    # ezberler; ve ezber, düzeltilen kusuru da korur.*
    vqr_acik: bool = False

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

    # FAZ 1.1 — MOTOR-SEVİYESİ RLS. `off|shadow|on`, varsayılan `shadow`:
    # `strict_sql_policy`'nin AYNI disiplini — bir güvenlik katmanı önce ÖLÇÜLÜR, sonra
    # açılır. Cube `always_filter`'ları motorun `rowLevelAccessControls`'una çevrilir ve
    # koşul HER model referansına iner.
    #
    # 🔴 NEDEN: `always_filter` bir UYGULAMA KATMANI yamasıdır ve iki yol onu ATLIYOR,
    # ikisi de ölçüldü: (1) JOIN — `compose.py:434` (G10) birebir yazıyor: "filtreli bir
    # modele join'lemek always_filter'ı BAYPAS EDER"; (2) Discovery HAM SQL —
    # `_inject_always_filter` yalnız `cube_sql()` yolundan çağrılır, ham SQL o fonksiyona
    # HİÇ uğramaz (MIMARI §6.3'ün ❌ maddesi).
    #
    # `off` → manifest'e HİÇ dokunulmaz, davranış birebir bugünkü (testle kilitli).
    motor_rls: str = "shadow"

    # FAZ 1.2 — KOLON DÜZEYİ ERİŞİM DENETİMİ. `off|shadow|on`, varsayılan **`off`**.
    #
    # 🔴 VARSAYILAN `motor_rls`'ten FARKLI ve nedeni ÖLÇÜLDÜ: CLS kolonu MASKELEMEZ,
    # PLANDAN DÜŞÜRÜR — seviye yetersizken `SELECT *` o kolonu HİÇ döndürmüyor. Düşme
    # SESSİZDİR: kullanıcı sorduğu kırılımın neden gelmediğini öğrenemez. Sessizce eksik
    # bir tablo, maskeli bir tablodan DAHA KÖTÜDÜR çünkü eksiklik fark edilmez.
    # `on` kademesi "hangi kolonlar esirgendi" yüzeyi kurulmadan AÇILAMAZ (kapı kilitli).
    motor_cls: str = "off"
    # FAZ 2.1 — ÇEKİRDEK KATMAN (`off|shadow|on`). Varsayılan `off` ve nedeni KURAL B:
    # bayrak kapalıyken compose çıktısı BİREBİR bugünküdür ve bu testle kilitlidir.
    # `shadow` hesaplar ama YAZMAZ (yazan bir gölge, gölge değildir — FAZ 1.1'de ölçüldü);
    # `on` yazar ve grain sözleşmesi ihlalinde compose'u REDDEDER (fail-closed).
    cekirdek_katman: str = "off"
    #: FAZ 5.9 — Slack webhook. ⚠ **SIR**: depoya değil ortama yazılır
    #: (`DIMA_SLACK_WEBHOOK`). Bir webhook URL'si, onu bilen herkese o kanala yazma
    #: yetkisi verir; bu yüzden tercih/`delivery` gövdesinde **taşınmaz**.
    slack_webhook: str = ""
    #: 🔴 FAZ 6.2 — YAZMA ARAÇLARI. `off` (varsayılan) → araçlar araç kaydına **HİÇ
    #: GİRMEZ**. Geri alma *"kapatmak"* değil **hiç açmamaktır**: bir aracı kayda alıp
    #: sonra engellemek, o engelin bir gün unutulabileceği anlamına gelir.
    #:
    #: ⚠ Feature-flag değil **Settings**: araç kaydı **import zamanında** kurulur ve o an
    #: bir tenant/principal bağlamı yoktur. Bir kurulum kararını istek bağlamına
    #: bağlamak, *"ajan neyi çağırabilir"* sorusunun tek bir cevabı olmaması demekti.
    yazma_araclari: str = "off"

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
