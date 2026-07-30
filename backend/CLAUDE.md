# dima-backend — CLAUDE.md

## Rol
`dima-frontend-demo` ile `dima-wrenai` (Wren semantik SQL motoru) arasındaki **ince HTTP köprüsü**.
İş mantığı minimum: SQL üretimi (LLM), doğrulama (motor), çalıştırma (motor), guard'lar.
Ağır semantik iş `dima-wrenai` motorunda; UI `dima-frontend-demo`'de kalır.

## Teknoloji
- Python 3.11+ · FastAPI · Uvicorn
- `wren.engine.WrenEngine` (in-process; subprocess YOK)
- NL→SQL sağlayıcıları (pluggable, `DIMA_LLM_PROVIDER=auto|anthropic|groq|ollama|rule`):
  Anthropic · Groq/Ollama (OpenAI-uyumlu tek istemci) · **kural-tabanlı (anahtarsız)** fallback
- pydantic-settings (env, `DIMA_` öneki)

## Yapı
```
app/
├── main.py            # FastAPI app + lifespan (WrenService/LLM app.state'e; 60sn scheduler+materializer döngüsü)
├── config.py          # Settings (DIMA_ env), path çözümleme
├── schemas.py         # request/response modelleri
├── wren_service.py    # WrenEngine sarmalayıcı + SQL guard (SELECT-only)
├── llm.py             # NL→SQL sağlayıcıları (Anthropic/Groq/Ollama/kural-tabanlı), MDL grounding
├── auth/              # public plane auth: login/refresh/logout/me + require()/require_company
├── features.py        # bayrak çözümü: global YAML (packs/features.yml) ⊕ sektör ⊕ şirket ⊕ DB override
├── materialize.py     # TenantConfig → company.yml materializer (ADR-0016)
├── interpret.py       # evrensel çıktı yorumu (deterministik, flag'li — ADR-0022)
├── dataset.py         # chat-scoped Excel/CSV → oturum DuckDB + oto-cube (ADR-0021)
├── logging_setup.py   # system/app logger (ADR-0020 — sessiz yutma yok)
└── routers/           # health(+features), query, ask(+cube/verify/upload), contracts,
                       #   schedules, conversations (sohbet geçmişi — ADR-0007/0019)
control_plane/         # auth bounded-context: SQLModel entity'ler (Tenant/User/… + CloneJob,
                       # SyncState, Conversation(Message), InteractionLog), authorize() matrisi,
                       # JWT/TOTP/rate-limit, audit, crypto (AES-256-GCM cred, DIMA_CRED_KEK), Alembic
admin_app/             # dima-admin-api (AYRI süreç, Wren'siz): /sadmin/* + clone/ (datasource-bağımsız
                       #   clone/sync motoru — ADR-0017 §9); interactions viewer (ADR-0020)
admin-dev/             # admin-api localtld başlatıcısı (pnpm dev → admin-api.dima.localtld)
migrations/            # Alembic (control-plane şeması; Postgres'te sahibi admin-api)
demo/                  # kendi kendine yeten DuckDB boyahane (tekstil) + OEE demosu
│  ├── packs/kaynak/   # kaynak-sistem pack'leri (ADR-0017): mikro-v16 (modeller pack'te),
│  │                   #   logo-3 (şablonlu — modeller şirkete üretilir); sektor/ = kesişim
│  └── companies/atiksan, gulteks  # lab fixture'ları: mssql, lab/ SQL Server'ına bağlanır
lab/                   # müşteri DB laboratuvarı: Docker mssql + restore/import/envanter
```

Compose katman sırası (en spesifik kazanır, ADR-0005+0017):
`kaynak → modül → sektör → kesişim(kaynak∧sektör) → şirket`. Cube ifadeleri
DuckDB/ANSI yazılır; DuckDB-dışı datasource'ta `WrenService._dialect_sql` hedef
lehçeye çevirir (DATETRUNC, ordinal genişletme — testleri `test_kaynak_compose.py`).

## Komutlar
```bash
uvicorn app.main:app --reload --port 8000   # dev
```

## Değişmezler (kurallar)
- **Yalnızca read-only**: guard `SELECT/WITH` dışını reddeder; asla DDL/DML çalıştırma.
- **LLM önerir, motor doğrular**: her üretilen SQL çalıştırılmadan önce `dry_plan`'dan geçer.
- **Sırlar env'de**: DB kimlik bilgileri ve API key asla commit edilmez (`.env` gitignore'da).
- **MDL kaynağı `dima-wrenai` projesidir**: şema `target/mdl.json`'dan okunur; elle uydurma yok.
- **Auth HER ZAMAN zorunlu** — kapatma bayrağı YOKTUR (dev bypass yok): korunan her uç
  geçerli Bearer access token ister; refresh HTTP-only cookie'de (rotation + reuse).
  Ortak kod `control_plane/` (ADR-0015 K1); public `app/auth/`, admin `admin_app/` —
  admin plane AYRI JWT secret çiftiyle imzalar. saka-standards `02`/`08` + ADR-0014/0015.
- **Rol matrisi uykuda**: authorize() viewer<analyst<admin<owner tanımlar ve testlidir,
  ama üründe bu fazda yalnız `owner` kullanılır (diğer role_key'ler admin API'de 400).
  UI izinleri login//auth/me `permissions` listesinden okur — matrisi frontend'e KOPYALAMA.
- **Tenant-RLS**: token'daki tenant slug (`tsl`) yüklü şirketle eşleşmeli; contracts/
  schedules/bildirimler tenant-damgalı yazılır ve okumada filtrelenir.
- **Bayraklar ≠ yetki**: feature flag rollout/görünürlük içindir (DB override, en spesifik
  kazanır); güvenlik sınırı her zaman authorize()'dır — bayrak onu gevşetemez.
- **DB→dosya tek yönlü** (ADR-0016): TenantConfig satırı olan tenant'ın company.yml'i
  TÜRETİLMİŞTİR; elle düzenleme materializer'da ezilir. Kaynak = control-plane DB.

## Standartlar
Kök `saka-standards` submodule'ü bağlayıcıdır (TypeScript tarafı için; Python tarafında
strict typing + ruff). Commit mesajlarında Claude footer KULLANILMAZ (saka standardı).
