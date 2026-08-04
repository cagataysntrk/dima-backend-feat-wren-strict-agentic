# dima-backend — CLAUDE.md

> 🔴 **AKTİF OPERASYON: DİMA v1 yol haritası.** Bir geliştirme isteği geldiğinde **önce
> şunları oku** — bağlam sıfırlansa bile operasyon buradan devam eder:
> 1. **`OPERASYON.md`** (repo kökü) — kural seti, döngü adımları, test kapısı, öz-denetim
> 2. **`OPERASYON-DURUM.md`** (repo kökü) — **nerede kaldık**, açık borçlar, ölçüm tabanı
> 3. **`~/.claude/plans/DIMA-V1-YOL-HARITASI.md`** — ne yapılacak (**5256** satır @`e22b2b9`
>    · `wc -l`; §10'daki bağlayıcı sıra)
>
> *Bu üçü + `MIMARI.md` operasyonun tam durumunu taşır; sohbet geçmişine ihtiyaç yoktur.*
>
> ✅ **DENETİM AJANLARI KULLANILIR** — her faz commit'inden sonra **üç ajan paralel**
> (`OPERASYON.md §7`, görev metinleri `OPERASYON-DENETIM.md`): **A** plan · **B** bütünlük ·
> **C** canlı kullanıcı. *(Bir ara «ajanlar sohbeti sildi» diye yasaklanmıştı; teşhis
> **yanlış** çıktı — sebep başarısız bir **daemon yükseltmesiydi**, ajanlar değil.)*

> **Mimari otorite `backend/MIMARI.md`'dir.** Bu dosya kısa bir kural indeksidir. Mimari bir
> soruda (cevaplama merdiveni, semantik katman, JOIN'in nerede oluştuğu, ne YAPILMAYACAĞI,
> bilinen kusurlar, ADR listesi) **önce `MIMARI.md`'yi oku** — çelişkide o kazanır.
> `HANDOFF_DOCS/*` tarihsel kayıttır; `Dima-0-100-Gorev-Takip-Dosyasi (2).md` ürün şartnamesidir,
> mimari otorite değildir.

## Rol
`dima-frontend-demo` ile `dima-wrenai` (Wren semantik SQL motoru) arasındaki **ince HTTP köprüsü**.
İş mantığı minimum: SQL üretimi (LLM), doğrulama (motor), çalıştırma (motor), guard'lar.
Ağır semantik iş `dima-wrenai` motorunda; UI `dima-frontend-demo`'de kalır.

## Teknoloji
- Python 3.11+ · FastAPI · Uvicorn
- `wren.engine.WrenEngine` (in-process; subprocess YOK)
- NL→SQL sağlayıcıları (pluggable,
  `DIMA_LLM_PROVIDER=auto|anthropic|xai|gemini|groq|ollama|rule`):
  Anthropic · xAI/Gemini/Groq/Ollama (OpenAI-uyumlu tek istemci) · **kural-tabanlı (anahtarsız)**
  fallback. `auto` → `FailoverSqlGenerator`, sıra `anthropic → gemini → groq → xai → ollama`,
  hepsi başarısızsa `rule`. Intent-JSON için ayrı/ucuz model (`*_select_model`).
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
├── cube_router.py     # SIFIR-LLM deterministik NL→CubeQuery (~1763 satır; içerik YAML'da)
├── viz.py/report.py/viz_email.py  # deterministik grafik+rapor kararı (ADR-0024)
├── drill.py           # dallı kök-neden: saf yorum fonksiyonları + CubeQuery dönüşümleri
├── vqr.py             # doğrulanmış-soru deposu (embedder + leksik yedek)
├── kpi.py/statements.py/yoy.py    # çapraz-cube KPI · gelir tablosu/bilanço · dönemsel kıyas
├── contracts.py       # Query Contract (ADR-0010)  ·  pii.py  # maskeleme (tek çıkış noktası)
├── channels.py        # bildirim/teslim kanalları (ADR-0011)
├── db_introspect.py/mdl_writer.py # canlı şema keşfi → taslak MDL (ADR-0017)
├── value_index.py/archetypes.py/synonyms  # bulanık eşleşme + sinonim katmanları (ADR-0018)
└── routers/           # health(+features), query, ask(+cube/verify/upload/drill/jobs),
                       #   contracts, schedules, conversations (ADR-0007/0019),
                       #   connections (bağlantı sihirbazı), dashboards, measures (terfi), stats
control_plane/         # auth bounded-context: SQLModel entity'ler (Tenant/User/… + CloneJob,
                       # SyncState, Conversation(Message), InteractionLog), authorize() matrisi,
                       # JWT/TOTP/rate-limit, audit, crypto (AES-256-GCM cred, DIMA_CRED_KEK), Alembic
admin_app/             # dima-admin-api (AYRI süreç, Wren'siz): /sadmin/* + clone/ (datasource-bağımsız
                       #   clone/sync motoru — ADR-0017 §9); interactions viewer (ADR-0020)
admin-dev/             # admin-api localtld başlatıcısı (pnpm dev → admin-api.dima.localtld)
migrations/            # Alembic (control-plane şeması; Postgres'te sahibi admin-api)
demo/                  # kendi kendine yeten DuckDB boyahane (tekstil) + OEE demosu
│  ├── packs/kaynak/   # kaynak-sistem pack'leri (ADR-0017): mikro-v16 (modeller pack'te),
│  │                   #   logo-3 (şablonlu — modeller şirkete üretilir), netsis;
│  │                   #   sektor/ = kesişim katmanı
│  ├── packs/modul/    # ERP-BAĞIMSIZ dikeyler: oee, bakim, ik, enerji, kpi, turev
│  ├── packs/sektor/   # boyahane (cube'lu), geri-donusum/kumas-ticareti/tarim-ticareti (yalnız
│  │                   #   terminoloji: cube_synonyms.yml + knowledge/rules)
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

## 🔴 TEST KAPISI — **YENİ POLİTİKA (kullanıcı kararı, 2026-08-04)**

> *"Kapı testlerini iptal edelim, sadece korpus koşsun — o da sadece en gerekli
> zamanlarda, sıklığı düşük, demet sonu gibi. Çok daha hızlı geliştirmeliyiz;
> fazları hızlıca ama mükemmelce tamamlamalıyız."*

### Kural — üç seviye, başka seviye YOK

| # | Ne zaman | Komut | Ne koşar | Süre |
|---|---|---|---|---|
| **1** | **her düzenlemeden sonra** | `python lab/kapi.py --hizli --degisen <dosyalar>` | değişen modüle bağımlı testler + çekirdek duman | **~15-60 sn** |
| **2** | **DEMET SONUNDA, bir kez** | `python lab/kapi.py --tam` | 🔴 **YALNIZ KORPUS** | **1 dk 50 sn** *(ölçüldü)* |
| **3** | **gecelik CI** *(insan beklemez)* | `python lab/kapi.py --hepsi` | korpus + süit + `eval` + senaryo | **4 dk 06 sn** *(ölçüldü)* |

🔴 **Seviye 3 YEREL OLARAK KOŞULMAZ.** Ne demet sonunda, ne commit öncesi, ne
*"bir de şuna bakayım"* diye. Onun yeri gecelik CI'dır ve orada **bedava**dır —
kimsenin beklediği zamandan ödenmez.

### Neden bu üçü — ve neden korpus KALDI

Ölçüldü, tahmin değil:

| Adım | Bu operasyonda kaç kez **kırmızı** verdi | Madde başına maliyeti |
|---|---|---|
| `eval.run` | **0** *(her koşum `+0,0 / +0,0 / +0,0`)* | ~1,5 dk |
| konuşma senaryoları | **0** *(dokuz sınıf tabanda sabit)* | ~1,5 dk |
| tam süit | birkaç kez — **aynı kusurları `--hizli` de yakaladı** | ~8,5 dk |
| **korpus** | 🔴 **1 kez — ve BAŞKA HİÇBİR ŞEYİN göremeyeceği bir kusuru** | **1 dk 57 sn** |

Korpusun o tek yakalaması, neden onun kaldığının **tamamıdır**: `gitas` bir compose
yarışıyla korpustan **tamamen düştü**, payda **445 → 342** indi, doğruluk **%93,2 →
%94,3'e ÇIKTI**. Sistem bozulurken **sayı iyileşti** — süit, `eval` ve senaryolar
üçü de **yeşildi**, çünkü hiçbiri *"kaç soru cevaplanabiliyor"* sorusunu sormuyor.
*Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla da olur.*

Korpus ayrıca **LLM'siz ve kotasızdır** (~1000 soru × 4 şirket): günlük kota dolsa
bile koşar.

### ⚠ Korpusun BİLİNEN körlüğü — yazılı, gizli değil

Korpus soruları **katalogdan üretiliyor**, yani hepsi **doğru yazılmış**. Typo yolu
korpusta **hiç sorulmuyor**. Yani `%93,1` yeşilken gerçek kullanıcı deneyimi kırık
olabilir — sayı **yalan söylemiyor, o yolu GÖRMÜYOR**. Kullanıcı-deneyimi kusurları
korpustan değil, **canlı turlardan** (`lab/deneyim.py --live`) çıkar.

### ⚡ HIZ KURALI — *"12 dakika bekleme"* bitti (2026-08-04, ölçüldü)

> Kullanıcı kararı: *"5 dk'dan uzun teste ayıracak kesinlikle vaktimiz yok."*

Kapı **20 çekirdekli makinede tek çekirdeği %91'de** tutup 19'unu boş bırakıyordu
(167 MB / 38 GB). Darboğaz soru sayısı değildi, **paralellik yokluğuydu**:

| | önce | **sonra** | nasıl |
|---|---|---|---|
| korpus (`--tam`) | 13 dk 18 sn | **1 dk 50 sn** | şirket × dilim → 16 süreç (`spawn`) |
| süit | ~8 dk 30 sn | **2 dk 15 sn** | `pytest -n 8` |
| tam kapı (`--hepsi`) | ~15 dk | **4 dk 06 sn** | iki dalga |

🔴 **KAPSAM KIRPILMADI — payda BÖLÜNDÜ, azaltılmadı.** Paralel koşumun sayıları seri
koşumla **birebir aynı**: boyahane 5306 · atiksan 1462 · gulteks 1618 · gitas 2479 tur,
semantik vaka paydası **445**, doğru-cube **%93,1**. KURAL A geçerli.

🔴 **SEYRELTME YASAK.** *"Korpus uzunsa soru azaltalım"* ölçülüp **reddedildi**: payda
kırpılırsa korpusun tek gerçek yakalaması (`gitas` düştü, payda 445→342, doğruluk
**YÜKSELDİ**) görünmez olur — o sinyal payda **sabitliğine** dayanır. Hız kapsamdan
değil, **çekirdekten** satın alınır.

⚠ **Dört adımı aynı anda koşma** — denendi: korpus + süit eş zamanlı compose yapınca
derleme kilidi 60 sn'de zaman aşımına uğradı, süit **934 hata** verdi. `--hepsi` bu
yüzden **iki dalga**: önce korpus tek başına, sonra süit ‖ eval ‖ senaryo → 0 hata.

Geri alma tek env: `DIMA_KORPUS_PARALEL=1`.

### Değişmeyen üç kural

- 🔴 **Kapı koşarken repoya YAZILMAZ** — mount canlıdır, ölçüm karışır.
- ⟳ ~~**İki test konteyneri ASLA paralel koşmaz**~~ — **KAPANDI 2026-08-04.** Yasağın
  sebebi paylaşılan `demo/wren-project` üzerindeki compose yarışıydı. Artık her süreç
  kendi derlenmiş ağacına yazıyor (`lab/izolasyon.py`) → yarış **yapısal olarak** yok.
  Yasak, doğruluğu hız feda ederek satın alıyordu; izolasyon ikisini birden verdi.
  **Sınır korundu:** aynı ağaca iki süreç hâlâ giremez, kilit hâlâ dizin başına.
- 🔴 **KOŞUM HİJYENİ:** `--rm` değil **`-d`**, `--name` ver, `docker wait` + `docker logs`
  ile oku, sonda `docker rm -f`. (`--rm` konteyner çıkınca kütüğü siler; bu operasyonda
  **iki koşumun özeti böyle kayboldu**.)

### Silinen bir şey YOK

Süit · `eval` · senaryo **yerel kapıdan çıkarıldı, kaldırılmadı** (MIMARI §10:
*"kapananlar işaretlenir, silinmez"*). `--hepsi` her an koşar, gecelik CI zaten koşuyor.
Geri alma tek bayrak — bir kod değişikliği değil.

## Standartlar
Kök `saka-standards` submodule'ü bağlayıcıdır (TypeScript tarafı için; Python tarafında
strict typing + ruff). Commit mesajlarında Claude footer KULLANILMAZ (saka standardı).
