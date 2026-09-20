# DIMA V2 — GELİŞTİRME DURUMU

**Branch:** `feat/ask-v2-mvp`  
**Başlangıç tabanı:** `wren-bağımsız@869280db316d5bf3f76d3253b8b80e5609a000b9`  
**Başlangıç tarihi:** 20 Eylül 2026  
**Durum:** **DAY 1 IMPLEMENTATION COMPLETE — LIVE P4 ACCEPTANCE BLOCKED**  
**Kod fazı:** Day 1 / P4.

---

## 0. OTORİTE HARİTASI

### Aktif ve mühürlü — DEĞİŞTİRME

1. `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md`
   - uygulama sırası / P fazları / exit gate authority.
2. `DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md`
   - hedef mimari / kök neden / R bölümleri authority.

Bu iki belge branch'e kullanıcı tarafından verilen nihai sürümlerden **birebir** kopyalanmıştır.
Geliştirme ilerlemesi bu dosyalara işlenmez.

### Yaşayan belgeler

- `DIMA_V2_GELISTIRME_DURUM.md` — bu dosya; tek “nerede kaldık?” kaynağı.
- `../../MIMARI.md` — mevcut sistem gerçekleri + V2 authority overlay.
- `../../AGENTS.md` — V2 geliştirici/ajan çalışma sözleşmesi.
- `../../CLAUDE.md` — repo kuralları; V2 branch override üstte olmalıdır.

---

## 1. NORTH STAR — TEK CÜMLE

Eski `/ask` karar ağacını temizlemek değil; yanında izole, conversation-first,
single-semantic-owner bir V2 çekirdek kurmak ve çalışan auth/tenant/Wren/semantic/evidence
altyapısını typed adapter'larla reuse etmek.

---

## 2. PRE-DAY0 HAZIRLIK CHECKLIST

- [x] Yeni branch açıldı: `feat/ask-v2-mvp`.
- [x] Branch tam olarak denetlenen `869280d...` HEAD'inden oluşturuldu.
- [x] Nihai uygulama yol haritası aktif repo belgesi olarak eklendi.
- [x] Nihai mimari/denetim raporu aktif repo belgesi olarak eklendi.
- [x] Belgelerin canonical dosya adları kendi iç referanslarıyla uyumlu tutuldu.
- [x] `backend/AGENTS.md` V2 çalışma sözleşmesi eklendi.
- [x] `backend/CLAUDE.md` V2 aktif-operasyon override ile güncellendi.
- [x] `backend/MIMARI.md` V2 authority overlay ile güncellendi.
- [x] Branch diff yalnız hazırlık/authority belgelerini içeriyor; executable V2 kod değişikliği yok.
- [x] Mühürlü iki belgenin kaynakla içerik eşitliği doğrulandı (4744 / 6379 satır; içerik birebir).

### Erken başlanıp geri alınan iş

İlk branch açılışında `app/v2/__init__.py` ve `app/v2/models.py` iskeletleri erken
oluşturuldu. Kullanıcı kararıyla Day 0 başlamadan önce geri silindi.

**Neden:** branch/platform hazırlığı ile implementation başlangıcının git tarihinde ayrılması.

**Sonuç:** Day 0 temiz sınırdan başlayacak; bu iki dosyanın tasarımı authority sayılmaz.

---

## 3. ŞU ANKİ BORÇ DEFTERİ

### V2-D001 — Eski MIMARI/CLAUDE operasyon metni V2'yi henüz işaret etmiyor — **KAPANDI**

- Kaynak: P1 / R0.2
- Risk: yeni geliştirici eski “aktif operasyon”a gidebilir.
- Blocker: **CLOSED**
- Kapanış kanıtı: root `AGENTS.md` + `backend/AGENTS.md` + `CLAUDE.md` V2 override + `MIMARI.md` V2 authority overlay.
- Hedef: PRE-DAY0 — tamamlandı.

### V2-D002 — V2 executable code henüz yok

- Kaynak: P2
- Risk: yok; bilinçli başlangıç durumu.
- Blocker: NO
- Kapanış: Day 0 V2 island shell boot.
- Hedef: Day 0.

### V2-D003 — Önceki /ask denetim P0'ları legacy açık kaldığı sürece yaşamaya devam ediyor

Bilinen sınıflar:

- post-seal mutation / persisted-vs-HTTP divergence riski,
- parallel plan/request-state race,
- `None` ile failure/not-applicable semantiklerinin karışması,
- router ↔ plan reverse dependency,
- sync dependency → ContextVar principal propagation riski.

- Kaynak: R2/R3/R3A + önceki repo denetimi.
- Risk: V2 pilot öncesinde legacy trafik sürerken yalnız legacy yolu etkileyebilir.
- Blocker: **Day 0 için NO**, pilot/cutover değerlendirmesinde YES olabilir.
- Kapanış: V2'nin bu sınıfları yapısal olarak taşımadığının gate'leri; gerekirse legacy'ye
  küçük güvenlik/P0 patch'i. Legacy refactor kampanyası YOK.

---

## 4. TEST / HIZ POLİTİKASI

Geliştirme sırasında büyük suite her adımda koşulmaz.

- Unit/contract testi: yalnız yeni boundary veya P0 invariant için.
- Daily demo: aktif günün canonical user scenario'su.
- Toplu gate: milestone/demet sonunda.
- Nightly ağır suite: CI.
- Refactor/polish, çalışan dikey dilimi geciktiremez.

Bu politika hem roadmap P0A'nın “en hızlı doğrulanabilir kullanıcı değeri” ilkesine hem
repo `CLAUDE.md` içindeki toplu test kararına uygundur.

---

## 5. DAY 0 — SIRADAKİ TICKET (HENÜZ BAŞLAMADI)

**Roadmap:** P1 + P1B + P2 + P2B  
**Rapor:** R0–R6; özellikle R2, R3, R3A, R4, R5, R6  
**Amaç:** V2 island'ın boot ettiğini, doğru tenant/principal/Wren runtime'a bağlandığını ve
legacy semantic hot path'e girmediğini kanıtlamak.

### Başlamadan önce okunacak

- Roadmap: P0–P2B
- Report: R0–R6
- `MIMARI.md` V2 overlay + auth/Wren/current-runtime ilgili bölümleri
- `app/main.py`
- `app/company_registry.py`
- `app/wren_service.py`
- `app/auth/dependencies.py`
- `app/schemas.py`

### Beklenen Day 0 touch

Yeni:

- `app/v2/__init__.py`
- minimal `app/v2/models.py` veya runtime contract
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`

Adapter:

- `app/main.py`
- `app/config.py` yalnız rollback/feature flag gerçekten gerekiyorsa

### Day 0 NO-TOUCH

- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`

### Day 0 canonical scenario

`/ask-v2` protected route boot eder → principal/tenant çözülür → tenant-bound Wren schema/runtime
alınır → V2 kendi typed shell cevabını verir → legacy `/ask` semantic decision graph çağrılmaz.

### Day 0 exit

- legacy semantic hot-path import = 0
- demo tenant Wren smoke = pass
- feature-flag rollback = pass
- legacy behavior değişikliği = 0 P0

---

## 5A. DAY 0 COMPLETE — P3 SOURCE LOCK + BASELINE

**ROADMAP:** P0, P0A, P1/P1A/P1B, P2/P2B, **P3**  
**REPORT DAYANAK:** R0–R6; özellikle R2, R3/R3A, R4, R5/R5.6 ve immutable runtime ilkesi  
**NEW OWNER:** V2 bootstrap/runtime boundary + Day0 baseline artifact  
**OLD OWNER:** legacy `/ask` yalnız baseline ölçümünün deneği; V2 authority değildir.

### AMAÇ

Yeni beynin başlangıç noktasını ölçülebilir hâle getir ve aynı repo içinde legacy semantic
karar ağacına girmeyen, rollback edilebilir `/ask-v2` adasını boot ettir.

### USER SCENARIO / ACCEPTANCE

1. Basit KPI, top-N, comparison, ambiguity, follow-up, repair, social, explain-existing ve
   kompleks multi-domain ailelerinden en az 30 legacy vaka source/correctness/failure-stage/
   latency ile dondurulabilir bir baseline koşumuna girer.
2. Feature flag açıkken kimlikli kullanıcı `/ask-v2` stub'ına gider; principal/tenant
   çözülür; doğru tenant-bound Wren schema + mdl_version snapshot alınır; legacy semantic
   router/planner çağrılmaz; query çalışmaz.
3. Feature flag kapalıyken V2 görünmez/404; legacy davranış değişmez.

### INPUT / OUTPUT

**Input:** authenticated HTTP request + explicit `Principal` + tenant-bound `WrenService`.  
**Output Day0:** typed `TenantAnalyticsRuntimeV0` + V2 bootstrap response; query yok.

### FILES TO TOUCH

Yeni:
- `app/v2/__init__.py`
- `app/v2/models.py`
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`
- `lab/v2_day0_baseline.py`
- `eval/v2_day0_cases.yaml`
- gerekli küçük V2 architecture/bootstrap testleri

Adapter:
- `app/main.py`
- `app/config.py`

### FILES NOT TO TOUCH

- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/wren_service.py` (Day0 için adapter ihtiyacı yoksa)

### TEST / DEMO — HIZ POLİTİKASI

Büyük suite yok. Yalnız:
- architecture import-ban testi,
- flag off/on bootstrap testi,
- explicit runtime identity/snapshot testi,
- baseline runner'ın case-selection/record schema testi.

Baseline koşumu ayrı artefakt üretir; ağır full gate Day0 demetinin sonuna bırakılır.

### KPI / EXIT

- representative baseline case >= 30
- known silent-wrong family coverage = 100% **envanterde tanımlanan set için**
- every baseline record failure_stage field = 100%
- `/ask-v2` stub boot = pass
- legacy semantic hot-path import = 0
- demo tenant Wren schema/mdl smoke = pass
- feature-flag rollback = pass
- legacy `/ask` code change = 0

### STOP-THE-LINE

- V2 bootstrap legacy semantic owner import ederse,
- principal/runtime identity implicit ContextVar'a bırakılırsa,
- Day0 stub query/LLM çalıştırmaya başlarsa,
- baseline vakaları mevcut corpus yerine uydurulursa,
- source lock sırasında legacy refactor açılırsa.

### DAY 0 NOTU

İlk PRE-DAY0 notundaki “Day0 sadece stub” kapsamı **P3 yeniden okununca düzeltildi**.
Roadmap açıkça Source Lock + Baseline ister. Bu düzeltme plan sapması değil, plan authority'sine
geri dönüştür.


## 6. İLERLEME GÜNLÜĞÜ

### 2026-09-20 — PRE-DAY0 / branch bootstrap

**Yapılan**
- `feat/ask-v2-mvp` açıldı.
- Nihai roadmap ve rapor branch'e aktif mühürlü belgeler olarak alındı.
- Her iki mühürlü belgenin kaynak içerikle birebir eşitliği doğrulandı.
- Root `AGENTS.md` ve `backend/AGENTS.md` kuruldu.
- `backend/CLAUDE.md` V2 aktif-operasyon override aldı.
- `backend/MIMARI.md` V2 authority overlay aldı; eski current-state gövdesi korunarak bırakıldı.
- Premature V2 kod iskeleti geri alındı; Day 0 sınırı temizlendi.
- Branch diff'i yalnız hazırlık/authority belgelerinden oluşuyor; executable V2 kodu henüz yok.

**Karar**
- Geliştirme rapor + roadmap çapraz okunarak yapılacak.
- İlerleme mühürlü belgelere değil yalnız bu durum dosyasına yazılacak.
- Büyük testler her küçük değişiklikte değil milestone/demet sonunda çalışacak.

**Sıradaki**
- **Day 0 ticket'ını aç.**
- P0–P2B ile R0–R6'yı tekrar aktif ticket bağlamında çapraz oku.
- V2 island boot/runtime boundary'yi en küçük dikey dilimle uygula.
- Day 0 bitene kadar TurnInterpreter/Resolver gibi Day 1+ capability'lere geçme.

---

## 7. DEĞİŞMEZ DEVİR FORMATI

Bir sonraki geliştirici yalnız şu sırayla devam eder:

1. Bu dosyada **Durum**, **Borç Defteri**, **Sıradaki Ticket** bölümlerini oku.
2. Aktif ticket'ın roadmap P bölümünü oku.
3. Roadmap'in atıf yaptığı report R bölümünü oku.
4. Touch/no-touch listesini yaz.
5. Kodla.
6. Hedefli test/daily demo gerekiyorsa çalıştır.
7. Bu dosyayı commit SHA, sonuç, borç ve sıradaki adımla güncelle.
8. Ancak exit yeşilse sonraki ticket'a geç.


### 2026-09-20 — DAY 0 / implementation batch 1

**Roadmap/Report çaprazı**
- P3 Source Lock + Baseline okundu.
- P2/P2B isolation/touch-no-touch ile R2–R5 reuse-first sınırı çaprazlandı.
- R3/R3A eski hata sınıfları için import-ban + explicit runtime + no-fallback/no-query Day0 sınırı seçildi.

**Yapılan**
- `app/v2/` greenfield package yeniden, bu kez Day0 kapsamıyla kuruldu.
- `TenantAnalyticsRuntimeV0` yalnız principal/tenant + MDL/schema snapshot taşır; semantic yorum yok.
- `POST /ask-v2` eklendi; `query:run` + `require_company` ile mevcut auth/tenant yatırımı reuse edildi.
- `ask_v2_enabled=False` default-off rollback flag eklendi.
- Stub yalnız Wren `schema()` + `mdl_version` okur; query/dry-plan/LLM/legacy semantic path yok.
- 32 mevcut eval case + 5 mevcut experience scenario = 37 unit Day0 baseline manifesti kilitlendi.
- Known silent-wrong envanteri ranking/period/comparison/typo/repair/follow-up/ambiguity aileleriyle manifestte coverage gate'e bağlandı.
- `lab/v2_day0_baseline.py` mevcut `/ask` üzerinden outcome/source/correctness/failure_stage/latency kaydı üretecek şekilde eklendi.
- `tests/test_v2_day0.py` yalnız hedefli Day0 gate'leri içeriyor.
- Bir kerelik `v2-day0-baseline` workflow'u draft PR açılışında baseline JSON artefaktı üretecek; sonraki pushlarda otomatik tekrar etmeyecek.

**Legacy no-touch doğrulaması**
- `app/routers/ask.py`: değişmedi.
- `app/cube_router.py`: değişmedi.
- `app/uyum.py`: değişmedi.
- `app/plan_tuketici.py`: değişmedi.
- `app/plan_semasi.py`: değişmedi.
- `app/wren_service.py`: değişmedi.

**Açık borç**

### V2-D004 — Live-provider Day0 baseline yok
- Kaynak: P3 baseline + P0A hız politikası.
- Mevcut ölçüm: `rule_offline` reproducible before-picture.
- Risk: Intent-LLM/Discovery canlı sağlayıcı davranışı Day0 artefaktında temsil edilmeyecek.
- Blocker: **Day0/Core geliştirme için NO**; pilot/default-ready öncesi YES.
- Neden şimdi değil: API/kota/belirlenimsizlik Day0 hızlı mimari kanıtını bloke etmemeli; mevcut repo da live ölçümü faz-sonu sınıfında tutuyor.
- Kapanış: gerçek sağlayıcıyla aynı source-locked manifest üzerinde ayrı ölçüm + provenance.
- Hedef: pilot hardening.

**Bekleyen ölçüm**
- Draft PR aç → one-shot Day0 workflow.
- Hedefli test + 37-unit baseline artefaktını oku.
- Sonucu ve artefakt özeti bu dosyaya yaz.
- Exit yeşilse Day0 kapat; Day1 TurnInterpreter ticket'ını ancak ondan sonra aç.


### 2026-09-20 — DAY 0 / kapanış ölçümü

**CI / ölçüm kanıtı**
- Draft PR: **#1** — `feat/ask-v2-mvp → wren-bağımsız`.
- Corrected Day0 workflow run: `35535503304`.
- Focused Day0 gates: **PASS**.
- Legacy baseline step: **PASS**.
- Artifact upload: **PASS**.
- Workflow artifact digest: `sha256:87dc5dd87c1bca8dd989a9b5a619f204ed413809aa0bf530ce97004a73e37556`.
- Kalıcı repo baseline: `eval/v2_day0_baseline.json` @ `4b52cdb916016f13d3c59dcff703649c63ac6b30`.

**Baseline sonucu**
- selected units: **37**
- produced records: **44**
- correct records: **43**
- baseline-observed non-green record: **1**
- known silent-wrong inventory coverage: **100%**
- execution mode: `rule_offline`
- every record has `failure_stage`: **YES**

**Tek non-green legacy kayıt**
- unit: `experience:kiyas_turu`
- akış: `bu yıl makine bazında oee → geçen yılla kıyasla → bunu analiz et`
- sources: `cube → cube → cube`
- failure stage: `experience_contract`
- yeşil kontroller:
  - süreklilik = true
  - makbuz = true
  - anlatı = true
- non-green kontrol:
  - `1·çapa: konuşma turu yeni SQL yazmaz = on_kosul_yok`

Bu sonuç **V2 regresyonu değildir**; Day0 source-lock'un yakaladığı legacy before-picture'dır.
Day0 gate'in amacı legacy'nin %100 yeşil olması değil, başlangıç gerçeğinin kaybolmadan
dondurulmasıdır.

### V2-D005 — legacy kıyas turunda çapa kontrolü ölçülemiyor

- Kaynak: P3 baseline / `experience:kiyas_turu`.
- Gözlem: comparison → “bunu analiz et” akışında mevcut legacy cevaplar `cube` yolunda;
  experience suite'in “konuşma turu yeni SQL yazmaz” kontrolü `on_kosul_yok` üretiyor.
- Sınıf: **baseline observation / measurement-contract gap**; henüz “ürün bug'ı” diye
  yeniden sınıflandırılmadı.
- Risk: yeni V2'nin RESULT_EXPLAIN / mevcut sonucu yorumlama turunda gereksiz query
  çalıştırmasını engelleyen Day1–Day5 acceptance için güçlü sentinel.
- Blocker: **Day0 için NO**.
- Kapanış: V2 canonical thread'de “bunu analiz et/yorumla” için query=0 davranışı
  TurnInterpreter + DialoguePolicy aşamalarında ölçülür; eski legacy dosyası bu uğurda
  patch edilmez.
- Hedef: Day1 classification contract + Day5 Core MVP.

**Day 0 EXIT**
- representative baseline >=30: **PASS (37)**
- known silent-wrong inventory coverage: **PASS**
- failure-stage kayıt disiplini: **PASS**
- `/ask-v2` stub boot: **PASS**
- explicit principal/tenant runtime: **PASS**
- immutable request runtime snapshot: **PASS**
- real demo Wren schema + MDL smoke: **PASS**
- feature flag off rollback: **PASS**
- V2 query/LLM invocation: **0**
- legacy semantic hot-path import: **0**
- legacy semantic owner dosyalarında değişiklik: **0**
- request-level legacy fallback: **0**

**Day 0 kapanış kararı**
Day 0 tamamlandı. V2'nin Katman 0 / L0 sınırı kanıtlandı ve source-lock kalıcı olarak
repoya alındı. Baseline workflow tekrar eden pushlarda çalışmayacak şekilde tekrar
`opened + workflow_dispatch` moduna donduruldu.

**Sıradaki**
- Day1 başlamadan **roadmap P4 + rapor R7** okunacak.
- Önce Day1 ticket contract'ı bu dosyaya yazılacak.
- Day1 yalnız `ContextProviderV0 + TurnInterpreter + typed TurnInterpretation` kapsamına
  girecek.
- SemanticResolver/clarification Day2'ye, CubePlanner/query Day3'e bırakılacak.


## 8. DAY 1 ACTIVE TICKET — P4 CONTEXTPROVIDER V0 + TURNINTERPRETER

**AMAÇ**  
Dima'nın ilk kez “hangi query?” yerine “kullanıcı bu turda ne yapıyor?” sorusunu tek
language-owner üzerinden typed cevaplaması. Day 1 hiçbir analitik query çalıştırmaz.

**USER SCENARIO**
```text
“bu ay ciro”
“makine bazında OEE”
“teşekkürler”
“bunu yorumla”
“hayır son üç ay”
“siyah fire”
```

**ROADMAP**  
P4 / P4.1 / P4.2 / P4.3.

**REPORT DAYANAK**  
R7; sınır için ayrıca R3/R3A + R6 Katman 1–2. Raw kullanıcı dili yalnız
`TurnInterpreter` tarafından yorumlanır; canonical data model seçimi Resolver'a aittir.

**NEW OWNER**
- `ContextProviderV0` → prompt'a girecek bounded semantic context + `ContextVersionV0`.
- `TurnInterpreter` → raw user message'in tek language owner'ı.
- `TurnInterpretation` → Day1 typed output.

**REUSE EDİLEN PRIMITIVE**
- tenant-bound `WrenService.schema()` / `mdl_version`.
- Day0 `TenantAnalyticsRuntimeV0`.
- mevcut `app.state.llm` provider/failover/telemetry/kaset **transport yatırımı**.
- auth/principal/company runtime.

**LLM ADAPTER KARARI**
Legacy `select_cube/refine_cube/takip_siniflandir` V2'ye çağrılmayacak. Bunlar eski
semantic owner davranışı taşır. Mevcut provider sınıflarına yalnız semantik-agnostic
`structured_text(system,user)` taşıma yüzeyi eklenecek; prompt, Pydantic schema,
validation ve retry policy tamamen `v2/interpreter.py` sahibi olacak.

**FILES TO TOUCH**
- `app/v2/models.py`
- `app/v2/context_provider.py` (new)
- `app/v2/interpreter.py` (new)
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`
- `app/llm.py` — yalnız generic structured transport adapter
- `tests/test_v2_day1.py` (new)
- bu durum dosyası.

**FILES NOT TO TOUCH**
- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/followup.py`
- `app/intent_semasi.py`
- semantic pack/MDL authoring dosyaları.

**CONTEXT V0 CONTRACT**
```text
WrenService.schema()
→ compact cube/metric/dimension/time/relationship metadata
→ entity values EXCLUDED
→ approved in-context business rules bounded + canonical hash
→ ContextVersionV0 = sha256(
     mdl_version
     + compact_catalog_builder_version
     + business_rules_hash
     + prompt_context_policy_version
   )
```

Canonical isimler prompt context'te görülebilir; **çıktıda canonical ref alanı yoktur**.
Interpreter yalnız kullanıcı mesajından exact surface span'ler çıkarır. Canonical binding
Day2 Resolver işidir.

**TURN ACTS**
```text
ANALYTIC_NEW
ANALYTIC_REFINE
CLARIFICATION_ANSWER
USER_REPAIR
RESULT_EXPLAIN
SOCIAL
UNSUPPORTED
```

**RETRY / FAILURE POLICY**
- normal: 1 structured LLM call, k=1.
- yalnız JSON/schema format-invalid ise: en fazla 1 format-only retry.
- semantic ambiguity retry: 0.
- output'ta kullanıcı mesajında bulunmayan semantic/reference span: fail-closed,
  semantic retry yok.
- SQL/canonical id/physical table alanı model sözleşmesinde bulunmaz.
- LLM unavailable: legacy fallback yok; explicit typed interpretation failure.

**TARGETED TEST / DEMO**
- ContextVersion determinism + business-rule hash.
- compact context entity values içermez.
- valid JSON = exactly 1 LLM call.
- malformed JSON = exactly 1 format retry, sonra success/fail.
- canonical-id hallucination/span invention = reject.
- seven act family + six canonical Day1 phrases.
- interpreter source içinde SQL/query/dry-plan/legacy semantic imports = 0.
- `/ask-v2` Day1 response query_executed=false.

**EXIT**
- structured-output success after ≤1 format retry >=99% validation corpus.
- turn_act_accuracy >=95% Day1 labeled corpus.
- canonical-id/surface hallucination = 0 dedicated set.
- SQL generation/execution in interpreter = 0.
- raw question parser owner count = 1.
- ContextVersionV0 non-null, deterministic and runtime-bound.

**STOP-THE-LINE**
- regex/keyword parser TurnInterpreter'ın ikinci sahibi olursa,
- Resolver işi Day1'e çekilirse,
- model canonical metric/dimension/entity ID seçerse,
- `select_cube/refine_cube/followup` V2 hot path'e girerse,
- query/SQL üretilirse,
- entity values prompt'a topluca dökülürse,
- malformed output legacy semantic path'e fallback ederse.



### 2026-09-20 — DAY 1 / implementation batch 1

**Roadmap/Report çaprazı**
- P4/P4.1/P4.2/P4.3 yeniden okundu.
- R7 tek structured language owner sözleşmesi aktif implementation authority olarak kullanıldı.
- R3/R3A'daki “aynı raw soru birden fazla parser tarafından tekrar yorumlanıyor” kök
  hata sınıfı için V2 hot path tek-owner tutuldu.
- R6 Katman 1–2 sınırı korundu: Interpreter doğal dili anlar, canonical data model seçmez.

**Yapılan**
- `app.llm` üzerine semantic-agnostic `structured_text(system,user)` taşıma kabiliyeti
  eklendi; mevcut provider/failover/telemetry/kaset korunuyor.
- RuleBased/NoLlm provider'larda structured language fallback açıkça RED: regex/kural motoru
  ikinci language owner olmayacak.
- Day1 typed domain modelleri eklendi; canonical semantic ID alanı
  `TurnInterpretation` sözleşmesinde bilinçli olarak YOK.
- `ContextProviderV0` eklendi:
  - tüm canonical cube/metric/dimension isimlerini korur,
  - synonym/rule payload'ını bounded tutar,
  - entity values'ı prompt context'e almaz,
  - physical relationship condition'ı taşımaz,
  - business-rule truncation olursa bunu açıkça işaretler,
  - gerçek `ContextVersionV0` üretir.
- `TurnInterpreter` eklendi:
  - k=1,
  - maksimum 1 format-only retry,
  - semantic retry=0,
  - span-grounding fail-closed,
  - SQL/query/canonical binding=0.
- `/ask-v2` Day1 path'i:
  `runtime → context → interpreter`.
  Resolver/planner/query/legacy fallback yok.
- Day0 runtime/rollback testinin beklentisi Day1 route'a uyarlanırken Day0 değişmezleri korundu.
- 28-case `eval/v2_day1_cases.yaml` labeled P4 corpus eklendi.
- `lab/v2_day1_eval.py` gerçek configured provider ile:
  structured success, act accuracy, surface-grounding violations ve call count ölçer.
- `v2-day1-turn-interpreter.yml` yalnız Day0+Day1 focused tests + varsa live P4 eval için eklendi.

**Commitler**
- `3e720fa6f72125b4b465c902c827cfe0663ae003` — generic structured transport
- `5d784fcacb1af665cef94a59f7de6af038cc5ec4` — typed Day1 contracts
- `fe5ccae2f4f7a3fd62436254d06f5bfedfbc6735` — bounded-context loss visibility
- `a6bf721e2295f26f94edf6c18d8aa6163cbf27da` / `efb1544110f166f8c782234a9d046a87de2f1075` — ContextProviderV0
- `eb8d0cee10ba72392af749087fd0294b1e44988d` — TurnInterpreter
- `79ef1c4f5769dfb4ef0e44f01ab27e31646f3c8b` / `446b39a71a5d2e7dda30a5a878aa98690f707762` — Day1 orchestration/router
- `a013af3f6c77fe1437135aecbc0aea3d5a602bb1` — focused Day1 contracts
- `eb257bbec7dd72d4f05cc8a6dd8f88e21c3f0e11` — Day0 invariant adaptation
- `a97f59ed68e329fe72f018be0b87e23cfec47f24` — labeled Day1 corpus
- `0aa8c71b035cde8c5bc7f8264c934e62e0ebfa8d` — real-provider evaluator
- `586fe6807803958869ffab1c6ba95446612594bb` — focused Day1 CI

**Şu anki gate durumu**
- Structural/contract code: implementation complete, CI ölçümü bekleniyor.
- P4 live KPI: **ölçülmeden PASS sayılmayacak**.
- Live provider secret Actions ortamında yoksa bu açık bir measurement debt/blocker olarak
  kaydedilecek; fake-output unit testleri `turn_act_accuracy` yerine sayılmayacak.



### 2026-09-20 — DAY 1 / acceptance ara sonucu + CI borç temizliği

**Focused contract evidence**
- Run `35536670734`: **23/23 PASS** (20.20s).
- Day0 runtime/rollback invariants + Day1 typed/context/interpreter contracts birlikte yeşil.
- Bu koşu fake-output contract testidir; **turn_act_accuracy KPI'sı yerine sayılmıyor**.

**Live P4 evidence**
- Aynı run'da Actions ortamı kontrol edildi.
- `DIMA_ANTHROPIC_API_KEY`: boş
- `DIMA_GEMINI_API_KEY`: boş
- `DIMA_GROQ_API_KEY`: boş
- `DIMA_OPENROUTER_API_KEY`: boş
- `DIMA_XAI_API_KEY`: boş
- Sonuç: `live_provider_unavailable`.
- Artifact digest: `sha256:df451c9b50f8e875f72782e8f1f4bf5b652eae40aa679330642bdbf9a25b4530`.

### V2-D006 — /ask-v2 dark endpoint geçici API-only borcu

- Kaynak: P2/P4 feature-flag dark development + iki mevcut orphan-endpoint gate.
- Mevcut durum: `/ask-v2` Core MVP öncesi kullanıcı UI'ına bağlanmıyor.
- Karar: endpoint silinmedi ve sahte frontend tüketicisi yazılmadı; iki gate'te çağıranı
  “developer acceptance” olarak gerekçeli API-only/meşru yetim ilan edildi.
- Borç tavanı geçici `8 → 9`; bu artış gizlenmedi.
- Blocker: Day1 için **NO**.
- Kapanış: frontend gerçek `askV2()` tüketicisi bağlandığında iki muafiyet kaldırılacak
  ve tavan tekrar 8'e inecek.
- Hedef: Core MVP frontend integration (en geç Day5).

### V2-D007 — P4 live TurnInterpreter KPI ölçülemiyor

- Kaynak: P4 exit.
- Gerekli kanıt:
  - structured-output success >=99%
  - turn_act_accuracy >=95%
  - canonical/surface hallucination = 0 dedicated set
- Hazır ölçüm aracı: `lab/v2_day1_eval.py`.
- Hazır corpus: `eval/v2_day1_cases.yaml` (**28 labeled case**).
- Mevcut blocker: GitHub Actions'ta gerçek LLM provider secret yok.
- Fake-output testler bu KPI yerine **sayılmayacak**.
- Blocker: **Day1 strict exit / Day2 transition için YES**.
- Kapanış: herhangi bir desteklenen provider credential ile evaluator'ı çalıştır;
  result artifact `status=pass` olmadan Day2 ticket açma.

### V2-D008 — source-lock full legacy suite kırmızı

- Eski Day0 full-CI run `35535435497`:
  - 5995 passed
  - 94 skipped
  - 28 failed
  - süre 22:55
- Bu sonuç Day1 focused gate değildir; source-lock çevresindeki legacy/test-infra borcunun
  görünür fotoğrafıdır.
- V2'nin doğrudan ürettiği kökler ayrı teşhis edildi:
  1. repo-root `AGENTS.md` belge düzeni ihlali → **FIXED** `fdb01fb903a4a4fac5e436d3050225b95e84a958`.
  2. `/ask-v2` yetim uç → **EXPLICIT DEBT** V2-D006; gate beyanları
     `313e1760e67ee11cf0fb3d494a91c65529208b32` +
     `4f04b5080fe9cddb3a2542fc2b1c2e5305df321f`.
  3. V2 authority overlay'i `MIMARI.md` satır indeksini bayatlattı →
     duplicate authority kaldırıldı, base current-state MIMARI'ya geri dönüldü
     `2fea97730c072abdf48bffc41261b28a3bde19c9`.
- Kalan legacy kırmızılar Day1 semantic implementation kapsamına çekilmeyecek.
- Blocker: rapid Day1 için **NO**; milestone full regression için **YES, ayrı baseline/debt**.

### V2-D009 — semantic description provenance henüz schema yüzeyinde yok

- P4 bounded context modeli description alanını destekliyor.
- Mevcut `WrenService.schema()` cube/metric/dimension descriptions yayımlamıyor;
  ContextProvider bu yüzden açıklama **uydurmuyor**, alanı null bırakıyor.
- Label/synonym/unit/relationship/business rules korunuyor.
- Blocker: Day1 act classification için **NO**.
- Kapanış: P2D Semantic Preservation Audit sırasında canonical description kaynağı
  gerçekten varsa schema adapter ile expose et; yoksa yeni truth uydurma.

**CI hız düzeltmesi**
- Eski `backend-ci` her V2 commitinde ~23 dakikalık full suite açarak runner kuyruğu
  oluşturdu.
- `17cb232c6a8e52fb6dfb44dbb03a7bb7ba54e8d8`:
  `feat/ask-v2-*` push/PR'larında full suite otomatik çalışmaz; `workflow_dispatch`
  milestone kapısı olarak korunur.
- Day1 workflow da artık push başına değil `ready_for_review + manual` milestone'da çalışır.

**Day1 strict durum**
- Kod/sınır/contract implementasyonu: **COMPLETE**.
- Focused structural gate: **GREEN**.
- P4 gerçek-model accuracy gate: **BLOCKED BY MISSING PROVIDER CREDENTIAL**.
- Bu nedenle Day2 ticket'ı henüz açılmaz.



### 2026-09-21 — DAY 1 / final structural seal

**Final product-code snapshot**
- `b57c7c49dba49a40f8c3789ab4cc53dbb00a110a`
- Bu snapshot şunları içerir:
  - KPI semantic surface preservation,
  - synonym silent-truncation removal,
  - P4 minimum domain,
  - ContextVersionV0,
  - single-owner TurnInterpreter,
  - no-query/no-SQL/no-legacy-fallback contracts.

**Final focused acceptance**
- Workflow: `35536961771`
- Result: **PASS**
- Focused tests: **23 passed / 0 failed**
- Duration: **20.48s**
- Measurement artifact: `10613258675`
- Artifact digest:
  `sha256:75c7eaf5d37002383617f18db6d8d3a870d0600ad92614d6bc52cb1c0db27f8d`
- Permanent record: `eval/v2_day1_measurement.json`
  @ `a69bd514ba28257c18c1383ea3a6784833b6b097`.

**Legacy owner no-touch final cross-check**
```text
backend/app/routers/ask.py       unchanged
backend/app/cube_router.py       unchanged
backend/app/uyum.py              unchanged
backend/app/plan_tuketici.py     unchanged
backend/app/plan_semasi.py       unchanged
backend/app/followup.py          unchanged
backend/app/intent_semasi.py     unchanged
```

**Strict P4 exit tablosu**
- ContextProviderV0 implemented: **PASS**
- ContextVersionV0 non-null/deterministic: **PASS**
- all canonical cube/metric/dimension + KPI semantic surface preserved: **PASS**
- verified synonym silent truncation: **0**
- entity values in prompt context: **0 by contract**
- physical join condition in prompt context: **0 by contract**
- one language owner: **PASS**
- k=1: **PASS**
- max one format-only retry: **PASS**
- semantic retry: **0**
- canonical-ID output field: **0**
- invented surface span: **fail-closed**
- SQL generation/execution: **0**
- request-level legacy fallback: **0**
- focused structural tests: **23/23 PASS**
- live structured-output >=99%: **NOT MEASURED — V2-D007**
- live turn_act_accuracy >=95%: **NOT MEASURED — V2-D007**
- live hallucination dedicated set =0: **NOT MEASURED — V2-D007**

**Karar**
Day 1'in **implementation ve structural acceptance** kısmı tamamlandı.
Roadmap'in gerçek-model KPI'sı credentials yokluğu yüzünden ölçülmeden “PASS” ilan edilmedi.
Bu nedenle mimari disiplin gereği **Day 2 henüz açılmayacak**.

Bir sonraki geliştirici:
1. önce V2-D007'yi kapatır,
2. `python lab/v2_day1_eval.py --require-live` gerçek provider ile çalıştırır,
3. `status=pass` artefaktını bu dosyaya işler,
4. ancak sonra P5 + R8 okuyup Day2 ticket'ını açar.

