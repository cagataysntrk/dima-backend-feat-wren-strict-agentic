<!-- DIMA-V2-ACTIVE-OPERATION -->
# 🔴🔴 AKTİF OPERASYON — DIMA V2 DAY 6.5 ENGINEERING CLOSURE

> **Bu branch'te eski “aktif operasyon” bloklarının üstünde BU BLOK okunur.**
> Branch: `feat/ask-v2-mvp`.
>
> Her geliştirme oturumunun ilk sırası:
>
> 1. `belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md`
> 2. `belgeler/plan/DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md`
> 3. `belgeler/plan/DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md`
> 4. `belgeler/plan/DIMA_DAY6_5_MANAGER_ARCHITECTURE_VALIDATION.md`
> 5. `belgeler/plan/DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md`
> 6. `belgeler/plan/DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`
> 7. `belgeler/plan/ADR_DAY6_5_ONE_SHOT_COMPLEX_INTENT_REJECTED.md`
> 8. `eval/v2_day6_5_eval_manifest.yaml`
> 9. `belgeler/plan/DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md`
> 10. `belgeler/plan/DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md`
> 11. `AGENTS.md`
> 12. `MIMARI.md` ve yalnız aktif ticket'ın kodu
>
> Nihai rapor ve roadmap **mühürlü / salt-okunur**. İlerleme, karar sonucu, commit SHA,
> açık borç ve sonraki adım yalnız `DIMA_V2_GELISTIRME_DURUM.md` dosyasına yazılır.
>
> Koddan önce roadmap'teki aktif **P** bölümünü ve onun dayanak gösterdiği **R** bölümünü
> birlikte oku. Rapor gerekçenin, roadmap icra sırasının authority'sidir.
>
> **Day 6.5 amacı:** iki execution path'i (`STANDARD | RESEARCH`) trust-plane altında kapatmak. Standard'ın `DIRECT | BUILDER` outcome'ları aynı engine ve aynı `AcceptedStandardAuthority` ailesidir. D65-E3A-R'de yalnız process-control bilen minimal `BoundedAgentRuntimeKernel` kurulacak; Research Manager bu kernel'e şimdi migrate edilmeyecek. Production `/ask-v2` certification seal öncesi açılmaz.
>
> **FAILURE TRIAGE RECEIPT:** RED live/canary/DEV/Validation/Hidden run sonrası semantic/product code'a dokunmadan önce `belgeler/plan/DIMA_DAY6_5_FAILURE_TRIAGE_RECEIPTS.md` zorunlu schema'sı doldurulur.
> `failure_class + single_owner + root_cause` kapanmadan ve gerekli same-SHA A/B bitmeden product patch yasaktır. `ONE FAILURE ≠ ONE NEW RULE`.
>
> **Kısa operasyon protokolü:** geliştirme/mimari doğrulama önceliklidir; büyük test kampanyası
> yerine vertical slice. Normal loop `code → 3–15 sn focused/provider-free → devam`.
> Workers=1 önce. Fail sınıflandırmadan patch yok:
> `MODEL_COGNITION | CONTRACT/ARCHITECTURE | RESOLVER_TRUTH | EVAL_ORACLE | TRANSPORT/PROVIDER`.
> Regex/morphology/keyword/case-derived prompt/resolver heuristic yasak. Önemli müdahale
> öncesi checkpoint SHA; A/B exact same backend SHA. Hidden yalnız final seal blocker'ıdır.
>
> **Standard front-door:** retrieval/discovery authority değildir. DIRECT yalnız ilk-attempt seal outcome'udur; BUILDER aynı Standard engine'in bounded progress-driven repair outcome'udur. Standard loop generic kernel'i kullanır fakat kernel semantic/authority/research truth bilmez. `simple_standard_research_manager_loop = 0`.
>
> **D65-J1 pre-freeze:** reference canary 35697064833 GREEN; freeze/DEV80'dan önce isolated decision-model challenger çözülür.
> J1A product code'a dokunmaz. `typesafe/jev-1.13` yalnız OpenRouter Decisions API üzerinden frozen CandidateSet seçiminde Gemini Flash-Lite ve Sol ile kıyaslanır; Manager/TemporalNormalizer kapsam dışıdır.
> Jev promising çıkarsa ancak D65-J1B ile explicit DecisionProvider seam + SemanticLinker/TemporalNormalizer role split yapılabilir ve tüm focused/family/live/canary/sentinel gates yeniden geçilir.
> J1 cognition experiment ≠ D65-X substrate experiment.
>> **Substrate kararı:** Wren current incumbent'tır. Metabase şimdi dependency/production path değildir. Day 6.5 engineering closure + DEV80 sonrasında, Validation/Hidden certification öncesinde isolated `D65-X` substrate-only challenger yapılır. Production'da Wren + Metabase equal truth engines yasaktır.
> **METABASE SOURCE REFERENCE CONTRACT — ZORUNLU:**
> Canonical upstream: `metabase/metabase`.
> Current Day 6.5 reference SHA: `74216b30981d8310c4cf724d63ca282e2e63529d`.
> Canonical pinned paths:
> `src/metabase/metabot/agent/core.clj`,
> `src/metabase/metabot/agent/profiles.clj`,
> `src/metabase/agent_api/reference.md`,
> `src/metabase/agent_api/api.clj`,
> `src/metabase/agent_api/query_guards.clj`,
> `src/metabase/mcp/v2/tools/query.clj`.
>
> `public/metabase/master` varsa yalnız **read-only convenience checkout**; canonical authority değildir. SHA doğrulanmadan kullanılmaz.
> Source-copy / port / vendor / transliteration YASAK.
> D65-X gerçek integration yalnız **separate-service Metabase Agent API** üzerinden thin adapter ile yapılır.
>
> Metabase'e dayanan her önemli architecture/implementation kararından önce `DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md §17A.5` mandatory source-control / analysis / research protocolü uygulanır:
> source identity → exact pinned source reading → pattern/API/security/runtime classification → Dima trust-plane cross-check → current external verification where changeable → decision receipt.
> Required source files okunmadan, query guards/permissions doğrulanmadan veya source/runtime kimliği pinlenmeden Metabase işi yapılmaz.
>
> Her D65-X execution receipt `source_reference_sha + runtime_version + immutable runtime_image_digest + Dima tested SHA + adapter SHA + corpus/version + permission context` taşır.
> Bu protokol mevcut product development sequence'ini DEĞİŞTİRMEZ.

>
> **Runtime-kernel closure:** D65-E3A-R GREEN. Focused `35693039369` = **22/22 PASS**; runtime-aligned full provider-free family closure `35693146320` = **94/94 PASS**. Research remained NO-TOUCH. Next gate: workers=1 focused live architecture set.
>
> **Day 6.5 cognition/authority kuralı:** doğal dil yorumunu regex/morphology/fuzzy-score ile
> deterministic semantic truth'a çevirmek yasaktır. Manager yolu:
> `catalog candidates → bounded Semantic Linker → deterministic BindingGate`.
> Coverage omission-only veto'dur; semantic/clarification authority değildir. Temporal
> dil typed intent'e normalize edilir; tarih hesabı deterministic engine'dedir.
>
> **Test:** her küçük değişiklikte büyük kapı yok. Yalnız gerekli hedefli testler;
> full/corpus gate milestone/demet sonunda; ağır suite nightly CI'da. Daily dikey demo
> ve P0 invariant testleri önceliklidir.
>
> **Kalıcı operasyon notu:** ayrıntılı tekrar-etme kuralları `AGENTS.md §11`'dedir.
> OpenRouter varsayılan modeli `deepseek/deepseek-v4-flash`; model override'ı
> `DIMA_OPENROUTER_MODEL` ile yapılır. Eski always-on `backend-ci.yml` yeniden kurulmaz.
>
> **İlk 10 gün wholesale refactor yasağı:** `routers/ask.py`, `cube_router.py`,
> `uyum.py`, `plan_tuketici.py`, `plan_semasi.py`.
>
> Eski öngörü/v1 operasyon kayıtları bu branch için “nerede kaldık?” authority'si değildir;
> tarihsel/current-system bağlam olarak korunurlar, silinmezler.

---

# dima-backend — CLAUDE.md

> 🔴🔴 **AKTİF OPERASYON (2026-08-13'ten): ÖNGÖRÜ KATMANI.** Bir geliştirme isteği
> geldiğinde **önce şunları oku** — bağlam sıfırlansa (compact) bile operasyon buradan
> devam eder:
> 1. **`belgeler/plan/ONGORU-DURUM.md`** — 🔴 **ÖNCE BU**: nerede kaldık · bağlayıcı
>    kurallar · taban sayılar · açık borçlar · koşum kalıpları (`§0` compact kurtarma)
> 2. **`belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md`** — **plan** (`§0`'da üretilmiş
>    dizin · `§42` fazlar · `§44` bağımlılık haritası)
> 3. bu dosya + **`MIMARI.md §0` dizini**
>
> 🔴 **Döngü compact'te KIRILMAZ:** her turun son eylemi `ScheduleWakeup`
> (`delaySeconds: 60` — araç `[60,3600]`'e kırpar, **30 verilemez**). Yalnız kullanıcı
> *«dur»* derse durur.
>
> ⟳ **`OPERASYON.md` · `OPERASYON-DURUM.md` · `DIMA-V1-YOL-HARITASI.md` — v1 operasyonu,
> ARŞİV değil ama AKTİF de değil.** Kayıt olarak duruyorlar (`§10`: kapananlar
> işaretlenir, silinmez); bu operasyonun durumu **`ONGORU-DURUM.md`**'dedir. İkisini
> karıştırmak, iki farklı *«nerede kaldık»* okumak demektir (`KAT-1`).

---

> ⟳ **ÖNCEKİ OPERASYON — DİMA v1 yol haritası.** Bir geliştirme isteği geldiğinde **önce
> şunları oku** — bağlam sıfırlansa bile operasyon buradan devam eder:
> 1. **`OPERASYON.md`** (repo kökü) — kural seti, döngü adımları, test kapısı, öz-denetim
> 2. **`OPERASYON-DURUM.md`** (repo kökü) — **nerede kaldık**, açık borçlar, ölçüm tabanı
> 3. **`belgeler/plan/DIMA-V1-YOL-HARITASI.md`** — ne yapılacak (**5256** satır @`e22b2b9`
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
> `belgeler/devir/*` tarihsel kayıttır; `belgeler/urun/Dima-0-100-Gorev-Takip.md` ürün şartnamesidir,
> mimari otorite değildir.

## 🔴🔴 EN ÜST KURAL — GARSON DEVRİ *(kullanıcı kararı 2026-08-08)*

> *"Route'a — yani NLP'ye — Türkçe öğretmemiz gerekir ki bu gereksiz. NLP güvenilir bir
> araç değil; **anlama yok zaten**, kelimeleri kurallamaktan ibaret. İntent algılamada
> asıl **LLM'e** güveniyoruz: kullanıcı **ne'ce** yazarsa yazsın gerçekten anlıyor.
> Siparişte **en ufak %5'lik şüphe** bile varsa hemen garson gitsin, siparişi düzgün alsın."*

| rol | kim | tutum |
|---|---|---|
| 🗣 **GARSON** | Intent LLM (`select_cube` → Intent-JSON) — sözü **sistem diline çevirir** | ✅ **asıl hakem** |
| 🍳 **AŞÇI** | küpler + `route()` — sayıyı **her zaman** o koyar | ✅ mutfakta LLM'e güven yok |
| 🥡 **YAN DÜKKÂN** | Discovery LLM (ham SQL) | ⚠ istemediğimiz son çare |

🔴 **Garson ile Discovery ASLA karıştırılmaz.** Odak garsondur.

**Kural:** aşçı **kesinlikle** duyduysa hemen yapar; **en ufak anlamama varsa garson gider.**
Tetikleyiciler: kısmi kapsam · bilinmeyen token · belirsiz eşleşme · yazım şüphesi ·
morfolojik ıskalama · çapraz-konu şüphesi · *"anlayamadım"* üretecek **her** dal.

🔴 **route'a dil kuralı EKLEME** (morfoloji · ek · yumuşama · eşanlam · sözcük sınıfı)
zaruri olmadıkça. Bir cümle anlaşılmıyorsa çözüm route'u genişletmek değil **devri
tetiklemektir**. 🔴 **Kullanıcı asla cevapsız kalmaz:** *"anlayamadım"* bir son cevap
olamaz.

### 🔴 İKİ EKSEN — ve aralarındaki TEŞHİS KURALI

Geliştirme **iki** eksende yürür ve **karıştırılmaz**:

| # | eksen | hedef | araç |
|---|---|---|---|
| **1** | 🗣 **SİPARİŞ ALMA** | Kullanıcı **ne'ce** yazarsa yazsın niyet doğru alınsın. **«Anlamadım» YOK** — Arapça bile yazılsa. | **Garson LLM** *(hakem, güvendiğimiz)* |
| **2** | 🍳 **MUTFAK** | Küpler **her yemeği** sunabilsin; Discovery'ye hiç düşülmesin. | Küp / semantik katman geliştirme |

> **Teşhis kuralı:** *"Garson devreye girdi ve sisteme sorunsuz, doğru bir girdi sağladı —
> ama yine çalışmadıysa, sorun küplerde, **mutfaktadır**. O zaman mutfağı geliştiririz."*

| gözlem | eksen | doğru iş |
|---|---|---|
| niyet yanlış/eksik alındı · *"anlayamadım"* · yabancı dil | **1 · sipariş** | garsona **devret** — route'a dil öğretme |
| niyet **doğru** ama küp o soruyu karşılayamıyor | **2 · mutfak** | küpü / ölçüyü / boyutu **geliştir** |
| `source=llm:*` ya da `cube=adhoc` görüldü | **2 · mutfak eksiği** | 🔴 bir çözüm değil, bir **arıza raporu** |

🔴 **Discovery'nin her ateşlenmesi bir MUTFAK EKSİKLİĞİ RAPORUDUR.** Onu bir yol değil bir
**ölçü** olarak okuyun: hangi yemeği yapamadığımızı söyler. Hedef, oranını **sıfıra**
yaklaştırmaktır.

⚠ **İki LLM'in güven derecesi ZITTIR ve bu bilinçlidir:** birincisi (**garson**) *asıl
güvendiğimiz hakem*; ikincisi (**Discovery**) *hiç güvenmediğimiz*. Aynı teknolojinin iki
role konması bir çelişki değil bir **iş bölümüdür**: biri **anlar**, öteki **uydurabilir**.

> *Bir siparişi yanlış almakla, doğru alıp yapamamak aynı kusur değildir — ve aynı yerde
> düzeltilmezler.*

⚠ Garson yalnız **çevirir** — guard'lar, beyanlar, doğruluk vetosu aynen yürürlükte.
⚠ Ön koşul: `route()`'un **derece** kavramı yok (marj hesaplanıp atılıyor); devir bunu ister.
⚠ `KURAL B`: bayrak kapalıyken davranış bugünküyle birebir.

*Bir dili kurallarla yakalamaya çalışmak, ufka doğru yürümektir; dili bilen birine
sormak ise bir adımdır.*

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
- 🔴🔴 **ARŞİVLENMİŞ MOTOR DİRİLMEZ — motor IN-PROCESS'tir** *(kullanıcı kararı 2026-08-12)*.
  Bu depoda **iki ayrı şey** benzer ad taşıyor ve karıştırılmaları ürünü sessizce bozar:

  | | **YENİ — yaşayan** | **ESKİ — arşivlenmiş** |
  |---|---|---|
  | ne | `wren.engine.WrenEngine` — **Python kütüphanesi** | `ghcr.io/canner/wren-engine` — **Docker servisi** |
  | nasıl | `from wren.engine import WrenEngine` (`wren_service.py:18`), subprocess YOK | HTTP `:8080`, `WREN_ENGINE_URL` |
  | durum | ✅ her cevabın SQL'ini bu derliyor | ⊘ **kapatıldı** (`§F1`), imajı **silindi** (679 MB) |

  ⚠ `demo/wren-project` **YENİ** motorundur (semantik model dizini, `DIMA_PROJECT_DIR`) —
  adı benziyor diye temizlik turunda silinirse **her cevap düşer**.
  🔴 **Kural:** `app/`+`lab/` altında `WREN_ENGINE_URL`·`wren-engine`·`WREN_ENGINE_PORT`
  **geçemez**; `docker-compose.yml`'deki blok **yorumda kalır** (silinmez —
  `MIMARI §10`). Kapı: `tests/test_arsivlenmis_motor_dirilmiyor.py` (4).
  ⊙ **Ölçülen kalıntı (2026-08-12):** karar 08-11'de verilip compose doğru yazıldığı
  hâlde, **koşan konteyner** hâlâ `WREN_ENGINE_URL=http://wren-engine:8080` taşıyordu —
  çünkü satır yoruma alınmadan **önceki** compose'dan yaratılmıştı. Değişken ölüydü
  (okuyan kod: **0**), ama ölü bir işaretçi bir gün okunduğunda ölü kalmaz.
  *Bir bağımlılığı yapılandırmadan çıkarmak onu ortamdan çıkarmaz; çalışan süreç,
  yazıldığı günün yapılandırmasını taşır.*
  ⚠ **Ve `docker-compose` (v1) bu makinede backend'i YENİDEN YARATAMIYOR**: yeni imaj
  biçiminde `KeyError: 'ContainerConfig'` ile düşüyor **ve düşerken eski konteyneri
  durduruyor** (ölçüldü — backend 40 sn kapalı kaldı). Backend `docker run` ile
  kaldırılır; `docker-compose up` denenmez.
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

### 🔴🔴 SIFIRINCI KURAL — **KAPI TOPLU KOŞULUR** *(kullanıcı kararı 2026-08-08)*

> *"Sen tek tek düzeltip tek tek uzun testlere sebep oluyorsun. Sakın bir daha böyle
> yapma. **En az 20 senaryo ve toplu düzeltme sonrası** test yapabilirsin. Teste bu kadar
> vakit harcayamayız — tam kapı, demet kapısı vs. **toplu** yapılmalı, tek tek değil."*

**Bağlayıcı sıra — kapı ancak SON adımda koşar:**

1. ≥20 özgün senaryo curl ile koş · logla · raporla
2. **TÜM** kök teşhisleri
3. **TÜM** düzeltmeler — 🔴 aralarında **kapı yok** (yalnız hedefli `pytest tests/test_x.py`)
4. **BİR** kez docker tazele → **BİR** kez curl doğrulama → **BİR** kez kapı

🔴 **YASAK:** her kök için ayrı `--hepsi` / `--tam` / `--hizli`. Ve `--degisen`'e demetin
**tüm** dosyaları birlikte verilir — dosya başına ayrı koşum aynı yasağın içindedir.

**Ölçülen israf (2026-08-08):** beş kök için beş ayrı tam kapı ≈ **35 dk**; aynı beş kök
tek koşumla **7 dk**. Beş kat maliyet, **sıfır ek bilgi** — hiçbir koşum öncekinin
görmediği bir şey görmedi.

⚠ **Hedefli test bir kapı değildir** (`pytest tests/test_x.py`, 3–15 sn) ve serbesttir.
Kapı olan üç şey `--hizli` · `--tam` · `--hepsi`'dir.

*Bir kapıyı her düzeltmeden sonra koşmak onu beş kat güvenli yapmaz — beş kat pahalı
yapar. Ve pahalı bir kapı, atlanan bir kapıya dönüşür.*

### Kural — üç seviye, başka seviye YOK

| # | Ne zaman | Komut | Ne koşar | Süre |
|---|---|---|---|---|
| **1** | ⟳ ~~her düzenlemeden sonra~~ → **TÜM düzeltmeler bitince, BİR kez** (SIFIRINCI KURAL) | `python lab/kapi.py --hizli --degisen <demetin TÜM dosyaları>` | değişen modüllere bağımlı testler + çekirdek duman | **~15-60 sn** |
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

> ⚠ **YUKARIDAKİ TUR SAYILARI 2026-08-04 FOTOĞRAFIDIR — bugün atiksan `1447`, payda `444`.**
> Fark FAZ 3.x kataloğundan geliyor, paralelleştirmeden **değil**: A/B koşuldu (aynı kod,
> **eski** `features.yml`) ve atiksan yine **1447** çıktı. *Bir belgeye yazılmış sayı,
> yazıldığı anın fotoğrafıdır; taban diye okunursa yanlış bir gerileme alarmı üretir.*
> Güncel taban her zaman **`lab/reports/nl_corpus.md`**'dedir.

🔴 **SEYRELTME YASAK.** *"Korpus uzunsa soru azaltalım"* ölçülüp **reddedildi**: payda
kırpılırsa korpusun tek gerçek yakalaması (`gitas` düştü, payda 445→342, doğruluk
**YÜKSELDİ**) görünmez olur — o sinyal payda **sabitliğine** dayanır. Hız kapsamdan
değil, **çekirdekten** satın alınır.

⚠ **Dört adımı aynı anda koşma** — denendi: korpus + süit eş zamanlı compose yapınca
derleme kilidi 60 sn'de zaman aşımına uğradı, süit **934 hata** verdi. `--hepsi` bu
yüzden **iki dalga**: önce korpus tek başına, sonra süit ‖ eval ‖ senaryo → 0 hata.

Geri alma tek env: `DIMA_KORPUS_PARALEL=1`.

### 🔴 DÖRDÜNCÜ KURAL — *bir tasarım gerçeği KOŞULARAK değil, OKUNARAK bulunur*

**Ölçülen israf (2026-08-05):** `motor_cls=on` sorusu için **üç ayrı tam süit** koşuldu
(~7 dk) — `--hepsi`'yi bir buçuk kez koşmaya bedel. Çıkan cevap tek satırdı:
`rls.cls_manifeste_yaz` `shadow` kademesinde manifesti **dokunmadan** döndürüyor, yani
`shadow ≡ off`. Bu, **okunacak** bir gerçekti; koşulacak değil.

> Süit *"kod ne yapıyor?"* sorusunun cevabı **değildir**; *"değişiklik bir şeyi bozdu
> mu?"* sorusunun cevabıdır. İkincinin aletini birincinin sorusuna tutmak, hem yavaş hem
> güvenilmezdir — çünkü bir davranışın **neden** öyle olduğunu süit söylemez.

**Pratik sonuç:** demet başına **bir** `--tam` (1:50), gerekirse gecelik `--hepsi` (4:06).
Ara koşum yok, *"bir de şuna bakayım"* yok. Bir soru *"bu kod ne yapıyor / neden böyle"*
biçimindeyse **önce kaynağı oku**.

🔴 **VE `--hizli` DE BİR ARA KOŞUMDUR — kural yazıldığı turda ihlal edildi.**
Kullanıcı iki kez uyardı (*"yine yarım saattir test yapılıyor"*). Ölçüm: tek bir turda
`--hizli` **dört kez** koşuldu (her biri 1-2 dk) + `--tam`. Doğru ritim:

| ne zaman | ne koşulur |
|---|---|
| bir dosya düzenledikten sonra | **yalnız o dosyanın hedefli testi** (`pytest tests/test_x.py`, ~3-15 sn) |
| demet sonunda, **bir kez** | `lab/kapi.py --hizli --degisen <tüm değişenler>` → sonra `--tam` |

*Bir kapıyı beş kez koşmak, onu bir kez koşmaktan daha güvenli değildir; yalnız beş kat
pahalıdır.* Ve pahalı bir kapı, atlanan bir kapıya dönüşür.

#### Ölçülen tur (2026-08-05) — yarım saatin dökümü

| ne | kaç kez | not |
|---|---|---|
| hızlı kapı | **7** (517·741·755·812·930·1026·1390 test) | asıl maliyet |
| tam süit (`motor_cls` sorusu için) | **3** (~7 dk) | 🔴 **hiç gerekmiyordu** |
| korpus | **2** | ikincisi yeni bilgi vermedi (%93,1 sabit) |

🔴 **Altyapı masum:** konteyner + toplama **1 sn**; korpus 1:50, süit 2:15, `--hepsi`
4:06. Bu depoda hiçbir şey 4 dakikadan uzun sürmüyor. **Alet doğru, kullanım sıklığı
yanlıştı** — ve en pahalı koşum, **hiç gerekmeyen** koşumdu.

#### Üç kural daha

**K2 · Düzelt-koş döngüsünde YALNIZ hedef dosya koşulur.**
`pytest tests/test_x.py` ≈ **3-15 sn**. Geniş seçim **commit'ten önce bir kez**.
*Beş kez 1000 test yerine, beş kez 20 test + bir kez 1000.*

**K3 · Merkezî dosyalarda hızlı sinyal, kapının kendisinden pahalıdır → doğrudan `--tam`.**
Ölçüldü: `ask.py` **30/238** · `cube_router.py` **54/238** · `ReportCard.tsx` **45/238**
dosya seçiyor ≈ 1-1,5 dk. Korpus **1:50** ve **daha çok şey görüyor**.
⚠ Bu seçimler bilerek genişletildi (iki kapı-seçim kör noktası kapatıldı; bir gerileme
dört demet gizlenmişti). Genişletme doğruydu — **koşum sıklığı** yanlıştı.

**K4 · Demet başına BİR korpus.**

⚠ Ve `--hizli` merkezî dosyalarda (`ask.py` · `wren_service.py` · `cube_router.py`)
29-53 dosya seçer; paralelken bile 1-2 dakika. **Beş kez koşulursa kapının kendisinden
pahalı olur.**

### Değişmeyen üç kural

- 🔴 **Kapı koşarken repoya YAZILMAZ** — mount canlıdır, ölçüm karışır.
- ⟳ ~~**İki test konteyneri ASLA paralel koşmaz**~~ — **KAPANDI 2026-08-04.** Yasağın
  sebebi paylaşılan `demo/wren-project` üzerindeki compose yarışıydı. Artık her süreç
  kendi derlenmiş ağacına yazıyor (`lab/izolasyon.py`) → yarış **yapısal olarak** yok.
  Yasak, doğruluğu hız feda ederek satın alıyordu; izolasyon ikisini birden verdi.
  **Sınır korundu:** aynı ağaca iki süreç hâlâ giremez, kilit hâlâ dizin başına.
- 🔴🔴 **`belgeler/` MOUNT'U ZORUNLU — yoksa iki YAYIN KAPISI sessizce düşer.**
  Ölçüldü (2026-08-12, denetim ajanı buldu): mount yokken `test_f8_dogruluk_yayini.py`
  ve `test_karne_kendini_sayar.py` **11 test birden atlanıyor** (`11 skipped in 0.12s`)
  ve `pytest` bunu `skipped` diye, yani **iyi haber gibi** raporluyor. Bu iki kapı
  *«yayınlanmış bir sayı çürümesin»* diye kurulmuştu; hiç koşmuyorlardı.
  ⊙ `lab/kapi.py` artık kaybı **adıyla bildiriyor** (iki çıkışında da), ama en doğrusu
  mount'u vermektir:
  `-v "$PWD/belgeler:/belgeler:ro"` · frontend kapıları için ayrıca
  `-v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro"`.
  *Bir kapıyı ortam eksiğinde susturmak dürüstlüktür; o susmayı DUYURMAMAK ise kapsamı
  sessizce kırpmaktır.*
- 🔴 **KOŞUM HİJYENİ:** `--rm` değil **`-d`**, `--name` ver, `docker wait` + `docker logs`
  ile oku, sonda `docker rm -f`. (`--rm` konteyner çıkınca kütüğü siler; bu operasyonda
  **iki koşumun özeti böyle kayboldu**.)
- 🔴 **`--user "$(id -u):$(id -g)"` ZORUNLU — repoya yazan HER konteynerde.**
  Ölçüldü (2026-08-06): bayrak unutulan **tek** bir derleme koşumu `demo/` altında
  **229 dosyayı root sahipliğine** geçirdi; sonraki `--user`'lı koşumlarda **üç şirket**
  `Permission denied` ile düştü ve korpus onları **%0 erişim** diye raporladı.
  ⚠ Ve toplam yine **✅ %94,8** görünüyordu — çünkü **ayakta kalanlardan** hesaplanıyordu.
  Bu, yukarıdaki *"gitas düştü, doğruluk YÜKSELDİ"* desenin birebir tekrarıdır:
  **sistem bozulurken sayı iyileşir.** Onarım: `chown -R $(id -u):$(id -g) /app/demo`.
- 🔴 **ÖLÇÜM ARACI ŞEMASINI KENDİ DERLEMESİNDEN ALIR.** `demo/wren-project`
  **gitignore'lu bir derleme artefaktıdır**; pack değişince yenilenmez ve `git checkout`
  onu **geri almaz**. Bir ölçüm aracı oradan okursa **bayat** bir katalogla koşar ve
  aynı kaynak durumda farklı sayılar üretir (ölçüldü: `sessiz_yanlis` **8 ve 17**).
  Kapı: `tests/test_olcum_semasi_taze.py`. *Bayat bir okuma, yanlış bir sonuçtan
  kötüdür: yanlış sonuç sorgulanır, bayat okuma güvenilir.*

### 🔴 BU POLİTİKANIN ÖLÇÜLEN BEDELİ (2026-08-06) — karar değil, FATURA

Politika 2026-08-04'te kondu (*"kapı testlerini iptal edelim, sadece korpus koşsun"*) ve
hız kazancı gerçek. Ama 2026-08-06'da **bir kez** tam süit koşuldu ve şu çıktı:

> ⊙ **15 test kırmızıydı.** Hiçbiri o gün kırılmamıştı; hepsi **görünmüyordu**.

| ne | kaç | sınıf |
|---|---|---|
| `MeasurePreview.unit` eksik → önizleme ucu **409** | 1 | 🔴 **gerçek ürün kusuru** |
| uydurma-sayı düzeltmesi meşru **döküm** yolunu da kesmiş | 2 | 🔴 **gerçek gerileme** |
| uydurmayı bir ÖZELLİK sanan kapılar | 3 | bayat kanıt |
| `eval` beyanlı cevabı chip sanıyor (`coverage −23,4%`) | 1 | bayat sınıflandırıcı |
| bayat taban (küp beyanı 16↔26 · sentetik fikstür 0.932 sabit) | 4 | bayat taban |
| sadakat listesinde eksik alan (`lower_set`) | 1 | eksik sözleşme |
| birim kapısına uymayan fikstür | 3 | bayat fikstür |

🔴 **En pahalısı ikisi:** bir HTTP ucu bir demet boyunca kırıktı ve kimse görmedi;
bir düzeltmem meşru bir yolu kesti ve korpus onu göremedi (korpus `route()`u ölçer,
Discovery'yi değil).

**Sonuç — politika DEĞİŞMEDİ, iki şart eklendi:**
1. 🔴 **Gecelik CI `--hepsi` GERÇEKTEN koşuyor mu, doğrula.** Bu politikanın tamamı
   *"süit silinmedi, CI'ya taşındı"* varsayımına dayanıyor. Koşmuyorsa politika
   *"süit iptal"*e dönüşür ve yukarıdaki 15 kırmızı onun ilk faturasıdır.
2. ⚠ **Merkezî dosya + davranış değiştiren demet → demet sonunda `--hepsi`** (4-6 dk).
   `--tam` (korpus) `route()`u ölçer; `llm.py`/`ask.py`/`measures.py` gibi dosyalarda
   kusur **Discovery ve HTTP uçlarında** doğar ve korpus onları **hiç görmez**.

*Bir kapıyı ucuzlaştırmak, onu görünmez yapmanın da yoludur — ve görünmeyen bir kapı,
kaldırılmış bir kapıdan yalnızca daha pahalıdır, daha güvenli değil.*

### Silinen bir şey YOK

Süit · `eval` · senaryo **yerel kapıdan çıkarıldı, kaldırılmadı** (MIMARI §10:
*"kapananlar işaretlenir, silinmez"*). `--hepsi` her an koşar, gecelik CI zaten koşuyor.
Geri alma tek bayrak — bir kod değişikliği değil.

## Standartlar
Kök `saka-standards` submodule'ü bağlayıcıdır (TypeScript tarafı için; Python tarafında
strict typing + ruff). Commit mesajlarında Claude footer KULLANILMAZ (saka standardı).
