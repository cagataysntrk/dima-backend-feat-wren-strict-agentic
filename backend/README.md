# dima-backend

FastAPI köprüsü: **Wren (dima-wrenai) semantik SQL motorunu** HTTP üzerinden `dima-frontend-demo`'e açar.

`dima-wrenai` (WrenAI fork'u) bir CLI + Python SDK'dır; doğrudan konuşulabilen bir HTTP
servisi değildir. Bu servis o boşluğu doldurur:

```
Next.js 16 (dima-frontend-demo)
      │  HTTP / JSON
      ▼
FastAPI (dima-backend) ──import──► wren.engine.WrenEngine ──► müşteri DB
      │                              (MDL transpile · dry-plan · execute)
      └──► Anthropic Claude (NL→SQL, yalnızca /ask için)
```

## Akış (trust-first)
1. `/ask` — Claude, MDL şemasına dayanarak SQL **önerir**.
2. Motor `dry_plan` ile SQL'i semantik katmandan geçirip **doğrular**; guard yalnızca `SELECT/WITH`'e izin verir.
3. Doğrulanan SQL **çalıştırılır**, sonuç JSON döner. LLM önerir; motor ve guard'lar karar verir.

## Endpoint'ler
| Method | Path | Açıklama |
|--------|------|----------|
| GET | `/health`, `/health/ready` | Liveness / MDL hazır mı (auth'suz tek uçlar) |
| POST | `/auth/login` `/auth/refresh` `/auth/logout` | Oturum: Bearer access + HTTP-only refresh cookie (OTP/MFA destekli) |
| GET | `/auth/me` | Kimlik + roller + izin listesi (`permissions`) |
| GET | `/schema` | MDL modelleri + cube kataloğu (`lower_is_better` yön semantiği dahil) |
| GET | `/features` | Özellik bayrakları — **principal'a özel**; global YAML (`packs/features.yml`) < sektör < şirket + DB override (ADR-0009) |
| POST | `/query` | Ham SQL (SELECT-only) çalıştır |
| POST | `/dry-plan` | SQL'i transpile et (DB'ye dokunmadan) |
| POST | `/ask` | Doğal dil → SQL → sonuç (+ flag'liyse `interpretation` deterministik yorum, ADR-0022) |
| POST | `/ask/upload` | Chat-scoped Excel/CSV yükle → oturum DuckDB + oto-cube (ADR-0021) |
| GET/DELETE | `/conversations` `/conversations/{id}` | Sohbet geçmişi: liste/getir/soft-delete (ADR-0007/0019) |
| * | `/cube` `/verify` `/contracts*` `/schedules*` `/notifications` | Chip düzenleme · verify döngüsü · Query Contract/replay · zamanlanmış raporlar |
| GET | `/oneri` `/oneri/pill` | 🔴 **ÖNGÖRÜ KATMANI** — yazarken **cümle** önerir (leksik+vektör RRF, ⊘ LLM) · girilen metnin **pill** temsili |
| POST | `/oneri/makro` `/oneri/tik` | adlandırılmış **makro** (N deterministik adım, ⊘ LLM; onaysız çağrı **önizler**) · tıklama sinyali (hasat) |
| POST | `/plan/kos` | 🔴 **onaylanan planı koşar** — kullanıcı önizlemeyi onaylayınca, ⊘ LLM |
| * | `/ask/drill` `/ask/jobs/{id}` `/dashboards*` `/measures*` `/decisions` `/stats` | kök-neden inişi · async iş · pano · ölçü terfi · karar kaydı · telemetri |

`/health` ve `/auth/login|refresh` dışında **her uç geçerli Bearer access token ister**
(bkz. Kimlik doğrulama). Swagger UI: `http://localhost:8000/docs`

⚠ **Port:** uvicorn konteyner **içinde** `8000` dinler; dışarıya `-p 8002:8000` ile
yayımlanır — yani tarayıcıdan **`localhost:8002/docs`**. Reçete:
[`belgeler/kilavuz/SERVER_COMMANDS.md`](../belgeler/kilavuz/SERVER_COMMANDS.md).

Ayrı süreçte **admin-api** (`admin_app.main:app`, Wren'siz, ADR-0015): `/sadmin/tenants`
(+config +status; config'te sektör/modül + kaynak/firma-dönem kapsamı — ADR-0017),
`/sadmin/users` (bu fazda yalnız `owner` rolü), `/sadmin/features` (bayrak
override'ları), `/sadmin/packs` (sektör/modül/kaynak keşfi), `/sadmin/connections`
(müşteri DB bağlantıları: sır AES-256-GCM, KEK `DIMA_CRED_KEK`; test-connection +
ERP fingerprint + Logo firma/dönem keşfi), `/sadmin/connections/{id}/clone|sync` +
`/sadmin/clone/overview` + `/sadmin/clone-jobs/{id}` (canlı→yerel klon/sync, ADR-0017 §9),
`/sadmin/audit` (erişim kanıtı) + `/sadmin/interactions` (sorgu telemetrisi viewer, ADR-0020).

## Kurulum
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip

# Wren motoru — DAİMA yerel aynadan kur (test edilen kod budur):
pip install -e ../dima-wrenai/core/wren
# NOT: PyPI `wrenai>=0.13,<0.14` ile ayna AYNI DEĞİL (21 .py dosyası farklı; versiyon
# string'i 0.13.0 kalmış ama ayna HEAD'i ileride). Rust binding'i PyPI'dan gelir:
#   pip install "wren-core-py==0.7.2"

pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "anthropic>=0.40" "pydantic-settings>=2"

cp .env.example .env   # DIMA_ANTHROPIC_API_KEY doldur (/ask için)

# Control-plane (auth) DB — Postgres kullanıyorsan şemayı Alembic kurar:
#   DIMA_DATABASE_URL=postgresql+psycopg://...  →  .venv/bin/python -m alembic upgrade head
# (boş bırakılırsa lokal SQLite: tablolar startup'ta otomatik oluşur, migration gerekmez)

# İlk superadmin (admin paneline giriş için):
#   PYTHONPATH=. .venv/bin/python -m control_plane.cli create-superadmin --email you@x.co
#   PYTHONPATH=. .venv/bin/python -m control_plane.cli enroll-mfa --email you@x.co   # TOTP (ops.)
#   PYTHONPATH=. .venv/bin/python -m control_plane.cli seed-demo                     # 2 demo firma+owner

uvicorn app.main:app --reload --port 8000

# admin-api (ayrı süreç, superadmin control-plane — dima-admin-frontend buna bağlanır):
cd admin-dev && pnpm dev        # http://admin-api.dima.localtld (yoksa :8001)
```

Testler: `.venv/bin/python -m pytest tests/` — **5.962 test** (ölçüm: `--collect-only`,
2026-08-13; auth/eval/VQR depoları geçici yollara izole edilir, canlı log kirletilmez).
Eval: `.venv/bin/python eval/run.py`.

🔴 **Ama gündelik akış bu değildir.** Bu depoda kapı **toplu** koşulur ve üç seviyesi
vardır (`CLAUDE.md` › *TEST KAPISI*): hedefli `pytest tests/test_x.py` (3-15 sn) →
demet sonunda `python lab/kapi.py --hizli --degisen <dosyalar>` → `--tam` (korpus).
⚠ **Belge kapıları repo kökünü ister** (`test_belge_duzeni.py` ·
`test_belge_yollari_gercek.py`): standart kapta **atlarlar** — `skipped` bir onay
değildir. Kök mount: `-v "$PWD:/repo" -w /repo/backend`.

### localtld (yerel domain)
`pnpm dev`, [localtld](https://github.com/abdullahharunozturk) kuruluysa servisi
**http://backend.dima.localtld** altında çalıştırır (yoksa düz uvicorn'a düşer). uvicorn,
localtld'nin verdiği `$PORT`'a bağlanır; domain'i o porta proxy'ler.
`package.json` › `localtld: backend.dima`. Varsayılan CORS `frontend.dima.localtld`'ı
kapsar. İlk sefer: `localtld setup`.

## Demo verisi — boyahane (dye house)
Şema, **Egemen Yazılım boyahane otomasyonunun** kamuya açık kataloğundaki gerçek veri
modelinden türetilmiştir (parti reçetesi, sipariş/termin, makine üretim & OEE, personel
verimlilik, boya/kimyasal & su/enerji tüketimi). Tablo/kolon adları Egemen terminolojisiyle
hizalıdır — gerçek DB erişimi gelince `mssql`/`oracle` connector'ı ile birebir değiştirilir.

- `demo/data/boyahane.duckdb` — 10 tablo (DuckDB), referans bütünlüğüyle:
  - **`partiler`** — boya partileri (ana olgu): parti_no, sipariş, makine, reçete, personel,
    kumaş cinsi, renk, aşama; fire, su/enerji, kimyasal maliyet, renk sapması, ağırlık, ciro
  - **`vardiya_kayitlari`** — OEE: makine × vardiya × personel; kullanılabilirlik × performans × kalite
  - **`siparisler`** — müşteri siparişleri: termin, miktar, tip (boya/baskı), durum
  - **`sevkiyatlar`** — sevkiyat: brüt/net sevk, fire, durum (sipariş bazlı)
  - **`recete_kimyasal`** — reçete BOM: konsantrasyon (g/L), maliyet katkısı (kimyasal bazında)
  - **`makineler`** · **`musteriler`** · **`receteler`** · **`kimyasallar`** · **`personel`** — boyut tabloları
- `demo/build_data.py` — veriyi yeniden üretir (sabit tohum): `.venv/bin/python demo/build_data.py`
- `demo/wren-project/` — MDL projesi (10 model + 10 ilişki; `target/mdl.json` commit'li).
  İlişkiler yeniden derlemek için: `cd demo/wren-project && wren context build`

`.env` varsayılanları bu demoyu işaret eder; ek kurulum gerekmez. Kural-tabanlı üreteç
soruyu ilgili tabloya yönlendirir: OEE/verimlilik/vardiya/personel → `vardiya_kayitlari`;
fire/su/renk/ciro/müşteri/aşama → `partiler`; sevkiyat/termin/geciken → `sevkiyatlar`+`siparisler`;
reçete/kimyasal → `recete_kimyasal` (BOM); makine verim+fire → 3-tablo çapraz JOIN. Ayrıca
top-N (“ilk 3”) ve aylık/haftalık/günlük trend desteklenir; diğer sağlayıcılar ilişki
metadatasıyla serbest JOIN yazabilir.

## LLM sağlayıcı seçimi
`/ask` sağlayıcısı `DIMA_LLM_PROVIDER` ile seçilir (varsayılan `auto`):
`anthropic` (ücretli) → `groq` (ücretsiz key) → `ollama` (yerel, anahtarsız) → `rule` (kural-tabanlı, anahtarsız).
`auto`: hangisi yapılandırılmışsa onu kullanır; hiçbiri yoksa kural-tabanlıya düşer. Bkz. `.env.example`.

## Gerçek müşteri veritabanı (Postgres)
`.env`'de:
```
DIMA_DATASOURCE=postgres
DIMA_CONNECTION_INFO={"host":"...","port":5432,"database":"...","user":"...","password":"...","schema":"public"}
DIMA_PROJECT_DIR=/path/to/wren-project   # o DB için MDL derlenmiş olmalı
```

## Kimlik doğrulama ve çok-kiracılılık (ADR-0014/0015)
Auth **her zaman zorunludur** — kapatma bayrağı yoktur. Model:

- **Oturum:** Argon2id parola + kısa ömürlü Bearer access token (15 dk) + HTTP-only
  refresh cookie (rotation + reuse detection + paralel-sekme grace + 30 günlük mutlak
  family ömrü). `mfa_secret`'lı hesaplarda TOTP zorunlu; login'de e-posta/IP bazlı
  rate limit. **Admin plane ayrı JWT secret çiftiyle** imzalar (`DIMA_ADMIN_JWT_SECRET*`)
  — public süreç admin token'ı basamaz.
- **Roller:** matris altyapısı hazır (viewer<analyst<admin<owner, `control_plane/authorize.py`)
  ama bu fazda ürün **yalnız `owner`** kullanır; diğer rol anahtarları admin API'de reddedilir.
  İzin listesi `permissions` alanıyla login//auth/me yanıtında döner — UI buton
  görünürlüğünü oradan okur, rol semantiği frontend'e kopyalanmaz.
- **Tenant-RLS:** access token tenant slug (`tsl`) taşır; veri uçları yalnız yüklü
  şirketle eşleşen tenant'a çalışır. Contracts/schedules/bildirimler tenant-damgalıdır
  ve okumada filtrelenir. Askıya alınan tenant: login 403, açık oturumlar ≤60 sn'de düşer.
- **Audit (ADR-0014 K6):** her sorgu/verify/schedule/yönetim eylemi `audit_log`'a yazılır;
  superadmin `/sadmin/audit` ve paneldeki Denetim ekranından okur.
- **Özellik bayrakları (ADR-0009 DB fazı):** üç katman — metadata `FLAG_REGISTRY`
  (`app/features.py`: etiket/açıklama/kategori, tek kaynak); varsayılan aşama YAML
  (global `packs/features.yml` < sektör < şirket); hedefleme `feature_override` tablosu
  (global|sector|tenant|role|user × off|alpha|beta|prod) üstüne biner — **en spesifik
  kazanır**, spesifik `off` = kill switch. Ham özelliği flag'lemenin reçetesi: ADR-0009.
- **TenantConfig materializer (ADR-0016):** panelden seçilen sektör/modüller control-plane
  DB'ye yazılır; dima-api ≤60 sn'de `companies/<slug>/company.yml`'e türetir ve aktif
  şirketse yeniden derler — iki servis disk paylaşmaz.

## Konfigürasyon
Tüm ayarlar `DIMA_` önekli env değişkenleri (bkz. `.env.example` — JWT secret'ları,
control-plane DB, MFA bayrağı ve rate-limit ayarları dahil).

## Canlıya alma (Railway)
`Dockerfile` Wren'i yerel aynadan kurar (PyPI'dan değil — yukarıdaki not), Rust binding'i
`wren-core-py==0.7.2` olarak pinler ve DuckDB demosunu image'a gömer. **Build context
parent `dima` repo'su olmalı** (Wren kaynağı sibling submodule'de); Railway config'i parent
repo kökündeki `railway.json`'dadır (`dockerfilePath: dima-backend/Dockerfile`). Swagger
`/docs`'ta açıktır. Adımlar ve env: kurulum reçetesi [`belgeler/kilavuz/SERVER_COMMANDS.md`](../belgeler/kilavuz/SERVER_COMMANDS.md),
gerekçe [ADR-0012](../docs/adr/0012-canliya-alma-hosting-topolojisi.md).
