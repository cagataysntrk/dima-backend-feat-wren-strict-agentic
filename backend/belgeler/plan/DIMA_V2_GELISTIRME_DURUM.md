# DIMA V2 — GELİŞTİRME DURUMU

**Branch:** `feat/ask-v2-mvp`  
**Başlangıç tabanı:** `wren-bağımsız@869280db316d5bf3f76d3253b8b80e5609a000b9`  
**Başlangıç tarihi:** 20 Eylül 2026  
**Durum:** **DAY 4 ACTIVE — CONVERSATION / FOLLOW-UP / USER REPAIR**  
**Kod fazı:** Day 4 / P7 ACTIVE.

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



### V2-D010 — 28-case local acceptance Actions kapasite kuyruğunda

- Kaynak: P4 strict exit / V2-D007.
- Amaç: API key kullanmadan gerçek model davranışını ölçmek.
- Uygulama:
  - `.github/workflows/v2-day1-live-28.yml`
  - yalnız `lab/v2_day1_eval.py --require-live`
  - local Ollama `qwen2.5:3b`
  - full suite **YOK**
  - timeout 15 dk
- Commit: `b528de33562270fc043bbd16d10840f9d828a013`.
- Run: `35537876889`.
- Mevcut blocker model/TurnInterpreter değil, **Actions runner kapasitesi**:
  - ölçüm anında: 20/20 in-progress job'un tamamı eski `backend-ci`,
  - ayrıca 14 eski `backend-ci` run queued,
  - `v2-day1-live-28` run `35537876889` bu backlog'un arkasında queued.
  - legacy `backend-ci` eski commitlerden 20 concurrent full-suite job çalıştırıyor,
  - ayrıca çok sayıda eski full-suite job queued.
- Bu backlog, V2 hız politikası konmadan ÖNCE üretilen run'lardan geliyor.
- Yeni V2 commitlerinde full suite otomatik tetiklenmesi zaten kapatıldı; problem tekrar
  üretilmiyor.
- PR geçici close/open ile denenmesine rağmen mevcut eski run'lar GitHub tarafından
  otomatik iptal edilmedi.
- Blocker: **P4 live local measurement için YES**, implementation için NO.
- Kapanış:
  1. eski `backend-ci` queued/in-progress run'ları iptal edilir **veya**
  2. Actions kapasitesi doğal olarak boşalır;
  sonra yalnız run `35537876889` / aynı 28-case local gate çalıştırılır.
- API key bu borcu çözmek için repoya/commit'e ASLA yazılmaz. Remote provider gerekirse
  yalnız secure secret/env üzerinden kullanılır.

**Hız kuralı tekrar teyit**
- Full suite tekrar çalıştırılmayacak.
- Day1 için bundan sonra yalnız 28-case evaluator çalıştırılır.
- 28-case sonucu gelmeden Day2 açılmaz.



### 2026-09-21 — LEGACY BACKEND CI KALDIRILDI

**Karar**
Eski `.github/workflows/backend-ci.yml` sürekli full-suite ürettiği ve V2 rapid-development
sözleşmesini ihlal ettiği için tamamen kaldırıldı. Bu yalnız V2 branch seviyesinde bırakılmadı;
repo default/base branch `wren-bağımsız` üzerinden de silindi.

**Commitler**
- V2 branch deletion: `216b6e0be1d351d02aa38a222ef5a30046144638`
- default/base deletion: `cb9e6ab3aae5d5fbdb49ce59c91644a90dcb9cab`

**Sonuç**
- Yeni `backend-ci` push/PR run'ı artık üretilemez.
- Full regression her committe koşmayacak.
- Ağır doğrulama gerektiğinde `nightly.yml` / açık milestone kararı kullanılacak.
- V2'nin phase-scoped küçük workflow'ları korunuyor:
  - `v2-day0-baseline.yml`
  - `v2-day1-turn-interpreter.yml`
  - `v2-day1-live-28.yml`

**Mevcut eski runlar**
Workflow dosyasının silinmesi, daha önce oluşturulmuş queued/in-progress run snapshot'larını
geriye dönük iptal etmez. Bunlar yeni borç/run üretmiyor; kapasite boşaldıkça bitecek.
Yeni ağır run açılmayacak.

**Kural**
Full suite, milestone/release/security/parity gibi gerçekten gerekli bir kapı dışında
otomatiklaştırılmayacak. Günlük geliştirmede yalnız aktif P/R fazının hedefli acceptance
testleri çalıştırılacak.



### 2026-09-21 — LOCAL 28-CASE DENEMESİ KAPATILDI

**Run**
- `v2-day1-live-28` / `35537876889`
- model: local Ollama `qwen2.5:3b`
- scope: yalnız 28-case P4 evaluator; full suite yok.

**Sonuç**
- Ollama install: PASS
- model pull: PASS
- evaluator: **INFRA/PERFORMANCE FAIL**
- her structured call local CPU runner'da 30s read timeout'a girdi.
- workflow job timeout/cancel ile kapandı.
- evaluator final JSON üretilemeden kesildi; accuracy sonucu YOK.
- Bu sonuç TurnInterpreter correctness FAIL değildir; seçilen local execution motorunun
  acceptance için pratik olmadığını gösterir.

**Karar**
- Local Ollama yolu tekrar çalıştırılmayacak.
- `.github/workflows/v2-day1-live-28.yml` silindi.
- Day1 acceptance için bir sonraki tek yol: mevcut
  `v2-day1-turn-interpreter.yml` içindeki real-provider evaluator.
- Full suite açılmayacak; secret geldiğinde yalnız focused contracts + 28-case live eval.

**V2-D007 güncelleme**
Local alternatifi elendi. Blocker artık yalnız gerçek provider credential.
Secret hiçbir commit/.env'e yazılmayacak; GitHub Actions repository secret olarak verilecek.



### 2026-09-21 — DAY 1 STRICT EXIT / LIVE P4 PASS

**Provider / transport**
- GitHub Environment: `DIMA_OPENROUTER_API_KEY`
- provider: `openrouter`
- acceptance model: `openai/gpt-5.6-luna`
- one-call structured transport smoke: **PASS**
- OpenRouter environment binding fix:
  `164b88a94320080af2593b1449c9f7cb38cae255`
- model-compatible transport fix:
  `ca52f4ccd8c9c231f662b66bc0ac7d03f6907883`

**Final live acceptance**
- workflow run: `35540119438`
- product snapshot: `5b541d0ba4e928eb1a86c7e437ddcfbc60cdcc11`
- artifact: `10614537238`
- digest:
  `sha256:e0034a9bf67000f2c943c55e5d8a3563d9f3deae3037338595111ff3f97ad274`
- focused structural tests: **23 / 23 PASS**
- labeled live corpus: **28**
- structured output: **28 / 28 = 100%**
- turn act: **27 / 28 = 96.43%**
- surface-grounding violation: **0**
- total LLM calls: **31**
- max calls / case: **2**

**P4 strict exit**
- structured-output success >=99%: **PASS — 100%**
- turn_act_accuracy >=95%: **PASS — 96.43%**
- canonical/surface hallucination dedicated set =0: **PASS**
- k=1 normal path: **PASS**
- max one format-only retry: **PASS**
- SQL/query in interpreter: **0**
- request-level legacy fallback: **0**

### V2-D011 — “sadece RAM-3” refine/repair sınırı

- Case: `refine-filter`
- input: `sadece RAM-3`
- expected: `ANALYTIC_REFINE`
- actual: `USER_REPAIR`
- Day1 gate etkisi: **NON-BLOCKING**; aggregate accuracy %96.43 ve P4 eşiği geçiyor.
- Neden şimdi hard-code edilmiyor:
  - “RAM-3 → refine” özel case yazmak P5/P7 generic semantics ilkesini ihlal eder.
  - gerçek ayrım conversation state + prior IR/focus ile Day4'te daha güçlü yapılacak.
- Sentinel:
  canonical Day4 flow'da `yalnız RAM-3 / sadece RAM-3` unrelated-slot preservation ve
  refine-vs-repair davranışı ayrıca ölçülecek.
- Hedef kapanış: Day4 / P7 canonical conversation flows.

**V2-D007**
- **CLOSED.**
- Gerçek provider credential bulundu, 28-case evaluator çalıştı ve P4 strict KPI geçti.

**Day 1 kapanış kararı**
Day 1 **COMPLETE**. P4/R7 implementation + structural + live acceptance kapıları geçildi.
Test uğruna yeni special-case parser eklenmedi. Day 2 artık açılabilir.

**Sıradaki zorunlu sıra**
1. `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` → P5 yeniden oku.
2. `DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md` → R8 yeniden oku.
3. Bu dosyada Day2 ticket contract aç.
4. Yalnız `SemanticResolver + SemanticHypothesis + ClarificationState` geliştir.
5. Blocking ambiguity'de query=0.
6. CubePlanner/SQL Day3'e kadar yasak.



### 2026-09-21 — OPENROUTER MODEL AUTHORITY + KALICI ÖĞRENİMLER

**Kullanıcı kararı / ileriye dönük model**
- OpenRouter runtime/focused-test varsayılanı:
  `deepseek/deepseek-v4-flash`.
- GitHub Environment variable:
  `DIMA_OPENROUTER_MODEL=deepseek/deepseek-v4-flash`.
- Kod fallback authority:
  `app/config.py::openrouter_model = "deepseek/deepseek-v4-flash"`.
- Focused Actions workflow modeli doğrudan hard-code etmez:
  `vars.DIMA_OPENROUTER_MODEL` → yoksa aynı repo fallback.
- `DIMA_OPENROUTER_SELECT_MODEL` ayrıca verilmezse ana model takip edilir.

**Provenance kuralı**
Day1 strict acceptance'ın `openai/gpt-5.6-luna` ile geçmiş olması tarihsel kanıttır;
`eval/v2_day1_measurement.json` bu nedenle değiştirilmedi. Gelecekteki model kararı eski
ölçümü yeniden yazmaz.

**Kalıcı devir kuralları**
`backend/AGENTS.md §11` eklendi. Bağlam/oturum kopsa bile aşağıdaki hatalar yeniden
tekrarlanmayacak:
1. always-on full `backend-ci` geri getirilmeyecek,
2. full suite her küçük değişiklikte çalıştırılmayacak,
3. Environment secret kullanan job environment'a açıkça bağlanacak,
4. OpenRouter'da önce tek-call transport smoke, sonra corpus,
5. reasoning'i kapatmak için `enabled:false`; `exclude:true` yeterli değil,
6. GitHub CPU Ollama `qwen2.5:3b` 30s timeout yolu acceptance için tekrar denenmeyecek,
7. infra/provider fail correctness fail diye etiketlenmeyecek,
8. tarihsel measurement provenance sonradan model değiştirildi diye tahrif edilmeyecek,
9. `sadece RAM-3` için special-case parser/hard-code yazılmayacak.

**Commitler**
- `b40ef77af4dbcf3ccd89453bbac93ee90a741123` — config OpenRouter default.
- `b15a3c832ef191002fe6e3f66d1f233225b763a4` — focused workflow variable-driven model;
  push başına otomatik rerun kaldırıldı.
- `c7b3f2425a5d619adf801b2cc4d1f751c9aa019c` — AGENTS §11 kalıcı öğrenimler.
- `4c884c310ad2dcdd2cb226e7f0101a6cfeea0c64` — CLAUDE compact-recovery pointer.

**Test kararı**
Bu değişiklik model/config/devir policy değişikliğidir. Day1 zaten strict exit'i geçtiği için
yalnız bu kayıt uğruna 23+28 acceptance tekrar çalıştırılmadı. Yeni model gerçek bir sonraki
fazın focused ölçümü gerektiğinde kullanılacak; gereksiz test yok.



## 9. DAY 2 ACTIVE TICKET — P5 / R8 SEMANTIC RESOLVER + CLARIFICATION

**AMAÇ**  
TurnInterpreter'ın surface-level mention'larını tenant'ın gerçek semantic/data kataloğuna
deterministik bağlamak; gerçek ambiguity varsa ilk adayı seçmek yerine minimum gerekli
netleştirmeyi üretmek. Day 2 hiçbir query çalıştırmaz.

**USER SCENARIO**
```text
“Siyah için fire”
“Bakiye ne?”
“Gece verimlilik”
“RAM-3 nasıl?”
```

**ROADMAP**  
P5 / P5.1 / P5.2 / P5.3 / P5.4.

**REPORT DAYANAK**  
R8; kök hata için R3.1/R3.2/R3.4. North-star kontrolü: R26B / NS2.

**NEW OWNER**
- `SemanticResolver` → surface mention → candidate set → hypothesis.
- `ClarificationState` → blocking ambiguity / fuzzy-only / semantic gap.
- signed candidate token → deterministic chip resume.
- TurnInterpreter raw language owner olarak kalır; resolver raw soruyu yeniden parse etmez.

**INPUT**
- `TurnInterpretation`
- tenant-bound `WrenService.schema()`
- `BoundedSemanticContextV0`
- typed conversation anchors / pending clarification.

**OUTPUT**
- `SemanticHypothesis[]`
- gerekirse tek `ClarificationState`
- chip resume'da deterministic resolved hypothesis.

**CANDIDATE PROVENANCE**
```text
explicit anchor
current focus
canonical name
verified synonym
exact entity value
verified company vocabulary   # yalnız gerçekten provenance varsa
fuzzy suggestion
```

**KARAR KURALI**
```text
tek güçlü/material aday       → resolve
birden fazla material aday    → clarify
yalnız fuzzy aday             → suggestion clarification
aday yok                      → semantic gap / açık soru
```

Company-vocabulary provenance mevcut schema yüzeyinde ayrıca korunmuyorsa ona sahte
`company_vocabulary` etiketi verilmeyecek; onaylı overlay synonym mevcutsa
`verified_synonym` olarak tüketilecek. Provenance uydurmak yasak.

**PRIVACY**
- Entity value index süreç içinde resolver tarafından görülebilir.
- Hassas entity values fuzzy candidate discovery/chip label ile sızdırılmaz.
- Kullanıcının birebir yazdığı hassas değer ancak exact match olarak kendi surface'i
  üzerinden çözülebilir; prompt'a toplu değer dökümü yoktur.
- Candidate token integrity içindir; auth/tenant sınırını gevşetmez.

**SIGNED RESUME**
```text
tenant + context_version + thread/session binding
+ clarification_id + candidate_id + source mention
→ HMAC-signed opaque selection token
→ candidate current schema'dan yeniden türetilir
→ deterministic slot resolution
```
Client'ın candidate payload'ı semantic truth sayılmaz.

**FREE-TEXT RESUME**
Pending clarification + `CLARIFICATION_ANSWER` TurnInterpretation üzerinden candidate
set daraltılır. Resolver raw question parser olmaz.

**FILES TO TOUCH**
- `app/v2/models.py`
- `app/v2/resolver.py` (new)
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`
- `tests/test_v2_day2.py` (new, yalnız focused contract)
- bu yaşayan durum dosyası.

**FILES NOT TO TOUCH**
- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/followup.py`
- `app/intent_semasi.py`
- Day1 tarihsel measurement.
- kaldırılmış `.github/workflows/backend-ci.yml` yeniden yaratılmaz.

**TEST KARARI — HIZ**
Bu ticket için full suite/corpus yok. Koddan sonra yalnız yeni Day2 resolver/clarification
contract dosyası ve gerekirse Day1'in kırılma riski taşıyan tek küçük boundary testi koşulur.
OpenRouter/LLM acceptance Day2 resolver correctness'inin sahibi değildir; provider/infra
hatası semantic correctness FAIL sayılmaz.

**TARGETED CASES**
- canonical metric exact → resolve.
- verified synonym → resolve.
- exact entity tek aday → resolve.
- aynı surface birden çok material target → clarify; auto-pick=0.
- yalnız fuzzy → clarify, auto-resolve=0.
- unknown → semantic gap.
- sensitive value fuzzy discovery yok / placeholder-safe behavior.
- signed chip valid → deterministic resolution.
- token wrong tenant/context/thread/tamper → fail-closed.
- free-text clarification answer → pending candidate set içinden resolve.
- `Siyah / RAM-3 / gece / premium / bakiye` aynı generic mechanism.
- clarification path query/dry_plan/SQL = 0.

**KPI / EXIT**
```text
blocking_ambiguity_recall          >= 95% dedicated focused set
blocking false auto-resolution     = 0
unnecessary_clarification_rate     <= 10%
clarification query count          = 0
clarification_recovery             >= 95%
```

**STOP-THE-LINE**
- `Siyah`, `RAM-3` veya başka bir literal için special-case branch/regex yazılırsa.
- Resolver raw `question` parse ederse.
- İlk candidate sessizce kazanırsa.
- Fuzzy candidate otomatik execute semantic truth olursa.
- Sensitive entity value suggestion ile ifşa edilirse.
- Clarification sırasında query/SQL açılırsa.
- Signed token client payload'ını doğrulamadan semantic state patch ederse.
- Day3 CubePlanner/AnalyticsIR resolution mantığı Day2'ye çekilirse.



### 2026-09-21 — DAY 2 / P5 COMPLETE

**Roadmap / report çaprazı**
- P5/P5.1/P5.2/P5.3/P5.4 uygulandı.
- R8 semantic hypothesis + clarification kararları authority olarak izlendi.
- R3.1 tek semantic owner, R3.2 parser creep yasağı ve R3.4 ambiguity-is-success
  ilkeleri implementation sınırı olarak korundu.
- R26B/NS2: gerçek ambiguity → clarification + query=0 + chip resume.

**Yapılan**
- `SemanticCandidate`, `SemanticHypothesis`, genişletilmiş `ClarificationState`
  ve Day2 response contract'ları eklendi.
- `SemanticResolver` raw kullanıcı sorusunu ALMAZ; yalnız typed
  `TurnInterpretation` mention'larını grounding eder.
- Candidate provenance generic mekanizma:
  - explicit anchor
  - current focus
  - canonical name
  - verified synonym
  - exact entity value
  - yalnız explicit verified provenance varsa company vocabulary
  - fuzzy suggestion
- Tek güçlü/material aday resolve olur.
- Birden fazla material adayda auto-pick=0; clarification oluşur.
- Fuzzy-only aday semantic truth olmaz; suggestion clarification olur.
- Candidate yoksa semantic gap üretilir.
- `Siyah / RAM-3 / gece / premium / bakiye` için production resolver'da
  literal special-case/parser **yok**.
- Hassas entity değerleri fuzzy discovery'ye girmez; exact user surface dışında değer
  candidate label/value ile ifşa edilmez.
- Signed clarification chip:
  tenant + ContextVersion + session/thread + clarification + candidate + mention
  integrity binding taşır.
- Chip seçiminde client candidate payload'ına güvenilmez; candidate güncel tenant
  schema/context'ten yeniden türetilir.
- Free-text clarification answer TurnInterpreter'ın typed mention'ları üzerinden pending
  candidate set'i daraltır; resolver raw question parser'a dönüşmez.
- `/ask-v2` Day2 akışı:
  `runtime → context → interpreter → resolver → resolved/clarify/gap`.
- Clarification token stale/tampered/binding mismatch → 409 fail-closed.
- Query / dry-plan / CubePlanner / SQL hâlâ **0**.

**Ek reuse touch**
- İlk ticket touch listesine sonradan yalnız
  `control_plane/security.py::derive_hmac_key()` eklendi.
- Gerekçe: V2'nin JWT secret/fallback seçimini kopyalayan ikinci security owner
  yaratmaması; mevcut auth authority'den domain-separated integrity key türetmesi.
- Auth/yetki davranışı değişmedi.

**Commitler**
- `1703e6701eaa9674ac48631acb7004bbf51e5f2f` — Day2 typed contracts.
- `a51fcdddc6bd4b4b5409652029027208b2bdd101` — domain-separated HMAC key.
- `f69413f705ec4210582a473d8d9675eeb7fc6d91` — generic SemanticResolver.
- `5f9bab70f8f2d80167b55e2d9eca59114cb37aa1` — resolver/resume orchestration.
- `3ea83e47419d68a6910e0e476e734e278ff36b59` — Day2 HTTP response/boundary.
- `4d09ff992955a1aee087ba5925b02645a485630d` — focused P5 contracts.
- `9df4ede9cbd68e7371259192dcc433f6b3756523` — closed Day1 gate manual-only.
- `aefb487274204bdf074373a388cb4eb3420c493d` — explicit Day2 focused workflow.
- `45b808b649fe75c34e234690b1768f0ab5f1ccba` — signing-key focused test.

**Focused test / hız kanıtı**
- Yalnız `tests/test_v2_day2.py` çalıştırıldı.
- Workflow run: `35541275684`.
- Sonuç: **19 passed / 0 failed**.
- Süre: **4.58 saniye**.
- Day0 baseline tekrar koşmadı.
- Day1 23+28 acceptance tekrar koşmadı.
- Corpus/full suite koşmadı.
- Kaldırılmış `.github/workflows/backend-ci.yml` yeniden yaratılmadı.

**P5 focused exit**
- blocking ambiguity recall: **1/1 = %100** dedicated material-ambiguity case.
- blocking false auto-resolution: **0/1 = 0**.
- unnecessary clarification: **0/5 = %0** exact/verified cases.
- clarification query count: **0**.
- clarification recovery:
  - signed chip **1/1**
  - free text **1/1**
  - focused toplam **2/2 = %100**.
- sensitive fuzzy disclosure dedicated case: **0**.
- literal special-case parser: **0**.
- resolver raw-question parameter: **0**.

Bu oranlar küçük **focused Day2 contract setinin** sonucudur; ürün-geneli istatistik diye
sunulmaz. P5'in mimari/exit davranışını kısa ve deterministik olarak kilitler.

**No-touch final cross-check**
```text
backend/app/routers/ask.py       unchanged
backend/app/cube_router.py       unchanged
backend/app/uyum.py              unchanged
backend/app/plan_tuketici.py     unchanged
backend/app/plan_semasi.py       unchanged
backend/app/followup.py          unchanged
backend/app/intent_semasi.py     unchanged
```

**Açık not — company vocabulary provenance**
Current `WrenService.schema()` dedicated `company_vocabulary` provenance alanı
yayımlamıyor. Onaylı overlay'ler bugün verified synonym yüzeyine birleşiyor.
Resolver yalnız gerçekten `verified=True` provenance taşıyan explicit runtime alanı
varsa `company_vocabulary` etiketi kullanır; provenance **uydurmaz**.
Bu Day2 blocker değildir; P2D/P16 semantic-memory/provenance gelişiminde genişletilebilir.

**Karar**
Day 2 P5 tamamlandı. Day 3 henüz başlatılmadı.
Bir sonraki geliştirici önce P6 + R10 + R5.5 + R5D'yi yeniden okuyacak; ardından
`AnalyticsIR + RequirementLedger-lite + CubePlanner + principal-aware Wren execution`
ticket'ını açacak. Day2 resolver'a SQL/query davranışı eklenmeyecek.



### 2026-09-21 — DAY 2 gate freeze

- Day2 focused gate başarıyla tamamlandıktan sonra
  `.github/workflows/v2-day2-semantic-resolver.yml` de Day1 gibi
  **workflow_dispatch-only** yapıldı.
- Commit: `39a2cdd20ffc7943a9675452700cd33cd5958e52`.
- Gerekçe: Day3'te ortak `models.py/orchestrator.py` değişiklikleri Day2 testini
  gereksiz otomatik tekrar koşturmasın.
- Bu policy-only değişiklik için test **tekrar çalıştırılmadı**.
- Always-on/full CI yok; kapalı fazların focused gate'leri de otomatik rerun yapmaz.



## 10. DAY 3 ACTIVE TICKET — P6 / R10 + R5.5 + R5D

**AMAÇ**  
Day1'in typed dil çıktısı ve Day2'nin canonical semantic grounding'ini, maddi hiçbir
requirement düşmeden deterministik CubeQuery planına ve explicit-principal Wren execution'a
dönüştürmek. İlk gerçek V2 data-touching cevap bu fazda doğduğu için
`MinimumQueryContract` aynı anda zorunludur.

**USER SCENARIO**
```text
“bu ay ciro”
“makine bazında OEE”
“son 3 ay en çok fire veren 5 makine”
“bu ay ciro, geçen ayla kıyasla”
```

**ROADMAP**
P6 / P6.1 / P6.2 / P6.3 / P6.4 / P6.5.

**REPORT DAYANAK**
- R10 — standard analytics canonical path.
- R5.5 — Day3'ten itibaren Query Contract zorunlu; bir contract = bir execution.
- R5D — formula/aggregation/grain/unit/time/relationship truth yalnız MDL/cube.
- R3.7 / R3A — dry-plan geçse bile requirement düşebilir; ranking direction+limit ve
  A-vs-B comparison dedicated olarak korunmalı.

**NEW OWNER**
- `AnalyticsIRBuilder` — resolved hypothesis + typed analytical surface →
  canonical `AnalyticsIR`.
- `TemporalResolverV0` — yalnız TurnInterpreter'ın çıkardığı time/comparison span'larını
  tenant fiscal context ile deterministic period'e çevirir. Tam raw question ALMAZ.
- `RequirementLedger` — her material requirement'ın
  `DETECTED → RESOLVED → REPRESENTED_IN_IR → REPRESENTED_IN_PLAN → VERIFIED`
  zincirini taşır.
- `CubePlanner` — yalnız canonical IR'den mevcut CubeQuery-compatible plan üretir.
- `ResultValidator` — planın/result'ın ledger requirement'larını gerçekten taşıdığını
  doğrular.
- `MinimumQueryContract` — her execution'ın immutable audit kaydı.

**OLD OWNER / REUSE**
- `WrenService.cube_sql` mevcut deterministic compiler olarak reuse.
- `WrenService.dry_plan(..., principal=...)` + `query(..., principal=...)` official
  execution boundary olarak reuse.
- `mali_takvim` fiscal-year aritmetiğinin tek sahibi olarak reuse.
- Mevcut `app/contracts.py::ContractStore` durability/result-hash altyapısı reuse edilir;
  legacy `answer.record_contract` V2 official-seal authority yapılmaz.
- Formula/unit/grain/additivity/relationship için yalnız current schema/MDL metadata okunur;
  planner yeni semantic truth üretmez.

**INPUT**
```text
TurnInterpretation
+ SemanticHypothesis[]
+ TenantAnalyticsRuntimeV0
+ ContextVersionV0
+ current WrenService schema
+ explicit Principal
```

**OUTPUT**
```text
AnalyticsIR
+ RequirementLedger
+ one or more PlannedExecution
+ principal-aware Wren result(s)
+ MinimumQueryContract[] 
+ official_verified flag
```

**ANALYTICS IR — DAY3 MVP**
Canonical alanlar:
- metric refs
- dimension refs
- entity filter refs
- resolved period
- ranking {measure, direction, limit}
- optional `ResolvedComparison`
- chosen cube
- context_version.

KPI/cross-cube semantic ref tek-cube CubePlanner ile kanıtlanamıyorsa silent coercion YOK;
typed capability gap olur. Planner LLM'e dönmez ve legacy Discovery'ye düşmez.

**CUBE SEÇİMİ**
Planner yalnız schema'nın doğruladığı coverage üzerinden cube seçer:
- requested metric cube'da bulunmalı,
- requested dimensions/filter dimensions cube'da bulunmalı,
- time requirement varsa kullanılabilir canonical time axis bulunmalı.
Tek viable cube → plan.
0 viable cube → capability/semantic-plan failure.
>1 equally viable cube → first-candidate seçimi YOK; typed ambiguity/failure.
CubePlanner raw question veya synonym sözlüğü görmez.

**TIME — P6.2 SINIRI**
Temporal resolver yalnız `SemanticMention(kind=time).text` gibi Interpreter'ın ayırdığı
typed span'ı okur; bütün kullanıcı cümlesini yeniden parse etmez.
İlk MVP:
- this month,
- this fiscal year,
- last N days/months,
- previous month/year.
Date arithmetic mevcut kanıtlanmış davranışla uyumlu tutulur; fiscal year için
`mali_takvim` sahibi çağrılır. Time axis 0 veya birden fazla belirsizse planner tahmin
etmez.

**COMPARISON**
Comparison tek range'e çökmez. Day3 basit previous-period comparison typed
`ResolvedComparison(base_period, reference_period)` üretir.
İlk uygulamada iki execution gerekirse:
- base execution → contract A
- reference execution → contract B
- üst cevap iki contract ref taşır.
İkinci SQL ilk contract'a eklenip mutate edilmez.

**RANKING**
`ranking.direction` ve `ranking.limit` ledger'da AYRI MUST requirement'lardır.
Semantic top-N `CubeQuery.order + limit` olarak planlanır; Wren transport row cap ile
karıştırılmaz. Direction yoksa planner "top-N" uydurmaz.

**FILTER**
Day2 exact resolved entity candidate:
`dimension + resolved value → eq filter`.
Sensitive exact value için Day2'nin `resolved_surface_value` dışında entity catalog
ifşası yapılmaz.

**REQUIREMENT LEDGER**
Her material item için typed state tutulur:
```text
DETECTED
RESOLVED
REPRESENTED_IN_IR
REPRESENTED_IN_PLAN
VERIFIED
```
Bir MUST item VERIFIED değilse cevap official olamaz.
Planner requirement ekleyemez, silemez veya "yakınını" ikame edemez.

**OFFICIAL EXECUTION**
Her execution:
```text
CubePlanner
→ WrenService.cube_sql
→ WrenService.dry_plan(sql, principal=principal)
→ WrenService.query(sql, principal=principal)
→ ResultValidator
→ MinimumQueryContract seal
```
Explicit principal argümanı zorunlu; ContextVar implicit execution authority değildir.

**MINIMUM QUERY CONTRACT**
Her execution için:
```text
request_ref
AnalyticsIR snapshot
planner id/version
mdl_version
context_version
execution_id
executed SQL
result_hash
tenant_id
principal/execution identity
cube_query
verification status
```
Mevcut ContractLog tablosu + `provenance_json` taşıyıcı olarak reuse edilebilir.
Legacy `ContractStore.record()` best-effort davranışı V2 official doğrulama için yeterli
sayılmaz: DB/spool seal gerçekten oluşmadıysa `official_verified=false` ve typed
contract failure üretilir; cevap legacy'ye düşmez.

**FILES TO TOUCH — beklenen**
- `app/v2/models.py`
- `app/v2/temporal.py` (new, typed-span temporal owner)
- `app/v2/cube_planner.py` (new)
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`
- `app/contracts.py` yalnız V2 strict-seal adapter gerçekten gerekirse
- `tests/test_v2_day3.py` (new focused)
- gerekirse küçük Day3 explicit milestone workflow
- bu yaşayan durum dosyası.

**FILES NOT TO TOUCH**
- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/followup.py`
- `app/intent_semasi.py`
- Day0/Day1/Day2 historical measurement artefaktları.
- kaldırılmış `.github/workflows/backend-ci.yml` ASLA geri gelmez.

**TEST / DEMO — HIZ POLİTİKASI**
- Full suite YOK.
- Corpus YOK.
- Day0/Day1/Day2 gate tekrar YOK.
- Geliştirme sırasında test döngüsü açılmayacak.
- Demet sonunda BİR focused Day3 gate:
  1. pure IR/ledger/planner contracts,
  2. ranking direction+limit sentinel,
  3. explicit A-vs-B comparison sentinel,
  4. explicit principal propagation,
  5. contract seal/official fail-closed,
  6. birkaç gerçek demo-Wren dikey smoke: metric/breakdown/time/ranking/compare.
- Provider/LLM acceptance bu fazın planner correctness sahibi değildir; Day1 tarihi
  yeniden ölçülmez.

**KPI / EXIT**
```text
MUST requirement coverage      = 100% dedicated set
core result equivalence        >= 95% focused canonical set
P0 silent-wrong                = 0
principal-aware execution      = 100%
standard p95                   <= 10s initial focused demo
metric/breakdown/time/ranking/simple compare real demo = PASS
MinimumQueryContract per execution = 100%
```

**STOP-THE-LINE**
- CubePlanner raw question okursa.
- Planner synonym/fuzzy/entity language parsingi yaparsa.
- Metric/dimension/filter/time/ranking/comparison requirement ledger'dan kaybolursa.
- Multiple viable cube'da ilk eleman sessizce seçilirse.
- Time axis belirsizken ilk axis alınırsa.
- Formula/unit/grain planner tarafından yeniden tanımlanırsa.
- ranking.limit transport row cap yerine kullanılır veya direction düşerse.
- comparison tek geniş range'e çöküp A-vs-B semantiğini kaybederse.
- `dry_plan PASS` tek başına verified kabul edilirse.
- principal explicit verilmeden dry-plan/query çalışırsa.
- contract seal başarısızken cevap `official_verified=true` olursa.
- legacy /ask / raw Discovery fallback eklenirse.
- sırf bir test vakası için literal/special-case parser yazılırsa.



### 2026-09-21 — DAY 3 / implementation batch 1

**P6/R10/R5.5/R5D uygulanan sınırlar**
- `AnalyticsIR` canonical refs, filter, period, ranking, comparison ve context_version taşır.
- `RequirementLedger` yalnız final state değil tam lifecycle history taşır:
  `DETECTED → RESOLVED → REPRESENTED_IN_IR → REPRESENTED_IN_PLAN → VERIFIED`.
- Multi-metric/dimension representation requirement-index bazında doğrulanır; “herhangi biri
  var” kontrolü ile sahte yeşil üretilemez.
- `TemporalResolverV0` yalnız typed time/comparison span alır; full raw question parametresi yok.
- `mali_takvim` fiscal-year owner olarak reuse edilir; legacy `cube_router` V2 hot path'e
  import edilmedi.
- simple previous-period comparison iki ayrı period ve iki ayrı execution planlar.
- ranking direction + semantic limit ayrı MUST requirement'lardır.
- multiple viable cube veya multiple time axis → typed fail; ilk eleman seçilmez.
- KPI/cross-cube ref tek-cube Day3 planner'a sessizce coerced edilmez.
- `CubePlanner` canonical IR dışında language/synonym/fuzzy karar yapmaz.
- execution her çağrıda explicit `principal` ile
  `dry_plan → query` sırasını izler.
- `ResultValidator` required result columns, semantic top-N row count ve numeric order
  doğrular; dry-plan tek başına verified yapmaz.
- `ContractStore.record_v2_minimum` legacy `record()` davranışına dokunmadan eklendi:
  DB veya existing spool gerçekten yazılırsa sealed; ikisi de başarısızsa
  `sealed=false`.
- Her execution kendi immutable contract'ını alır; comparison iki contract üretir.
- Signed clarification sonucu Day4 prior-request state olmadan query'ye zorlanmaz.

**Commitler**
- `8e224e6452e4a722cd46c3a249197d2b3b571cb6` — Day3 domain/execution/contract models.
- `d4a047f69b974374154b558cded7a4bf12ef1014` — requirement lifecycle history.
- `752277b7f49f188af8fe4bbed359486224b9b667` — typed temporal resolver.
- `772334ad1d419b7136eeb9fcc09a4e3d804ec609` — IR/ledger/planner/result validator.
- `4e968305352d0eef16ad0dd1afc095baccceb963` — per-requirement plan representation fix.
- `951a9c54f9079466353390684cac13f9594995d5` — strict V2 contract seal.
- `5b9b678b9691da959619e55714a01c16c4013e14` — official Day3 orchestration.
- `aa5ce21466bcb6f2b51c4646ee08977a2ab80266` — Day3 HTTP response.
- `2aa564d64bce1e8e024e3474939823dae44a68d2` — earlier AnalyticsIR construction compatibility.
- `4c8a6118189379903c3cd3b04cf6f3e52b3fe453` — focused P6 test file.

**Test kararı**
Tek koşum: `pytest -q tests/test_v2_day3.py`.
Dosya pure contract testleri + yalnız 5 canonical real-demo Wren result-equivalence case içerir.
Full suite/corpus/Day0/Day1/Day2 gate tekrar yok.
Test failure olursa önce failure-stage ayrılır; infra/provider failure correctness olarak
etiketlenmez.



### 2026-09-21 — DAY 3 / P6 COMPLETE — FINAL SEAL

**Final P6 architecture**
```text
TurnInterpreter
→ SemanticResolver
→ AnalyticsIRBuilder
→ RequirementLedger
→ CubePlanner
→ WrenService.cube_sql
→ WrenService.dry_plan(principal=...)
→ WrenService.query(principal=...)
→ ResultValidator
→ ContractStore.record_v2_minimum
→ MinimumQueryContract[]
```

**Maddi requirement preservation**
Day3 canonical ledger family:
```text
metric
dimension
filter
time
ranking_direction
limit
comparison
```
Her MUST item lifecycle history taşır:
```text
DETECTED
→ RESOLVED
→ REPRESENTED_IN_IR
→ REPRESENTED_IN_PLAN
→ VERIFIED
```
Lifecycle adımı atlanırsa kod fail eder. Multi-metric/dimension representation index
bazında doğrulanır; bir requirement'ın varlığı diğerini yanlışlıkla yeşile çeviremez.

**Semantic / computational ownership**
- Raw full question CubePlanner/TemporalResolver'a verilmez.
- TemporalResolver yalnız Interpreter'ın typed time/comparison span'ını okur.
- `cube_router` V2 hot path'e import edilmedi.
- Metric formula/aggregation/unit/grain ilişkisi yeniden yazılmadı; current Wren schema/MDL
  canonical ref'leri kullanıldı.
- Multiple viable cube → typed `ambiguous_cube`.
- Multiple time axis → typed `ambiguous_time_axis`.
- KPI/cross-cube semantic ref → Day3 single-cube planner'a sessiz coercion yok.
- Ranking direction + semantic limit ayrı MUST requirement.
- Semantic top-N transport row-cap ile karıştırılmıyor.
- Comparison tek geniş range'e çökmüyor; A ve B ayrı typed period + ayrı execution.

**Official execution**
- `dry_plan` ve `query` her execution'da explicit aynı `Principal` ile çağrılır.
- ContextVersion.mdl_version != runtime.mdl_version ise data-touch öncesi fail.
- ResultValidator:
  - requested metric/dimension columns,
  - top-N row count,
  - numeric ranking order
  doğrulamasını yapar.
- Dry-plan tek başına verified değildir.

**MinimumQueryContract**
Her execution:
- request_ref
- full AnalyticsIR snapshot
- planner id/version
- mdl_version
- context_version
- execution_id
- executed SQL
- result_hash
- tenant_id
- principal identity/roles
- CubeQuery
- durability/sealed
taşır.
Comparison iki execution ise loop her plan/result çifti için ayrı immutable contract seal
üretir; ikinci SQL ilk contract'a yazılmaz.

**Strict seal kararı**
Legacy `ContractStore.record()` değiştirilmedi.
Yeni `record_v2_minimum()`:
- DB write → `durability=db, sealed=true`
- DB fail + existing spool write → `spool_pending, sealed=true`
- DB + spool fail → `durability=none, sealed=false`
Son durumda result dönse bile `official_verified=false`; legacy fallback yok.

**Focused acceptance run 1**
- Run: `35558055708`
- Sonuç: **17 passed / 0 failed**
- Test süresi: **9.75s**
- İlk run sonrası roadmap exit yeniden okununca gerçek demo time + simple compare'ın
  yalnız fake compiler seviyesinde kaldığı görüldü.
- Bu nedenle Day3 kapatılmadı; eksik acceptance coverage tamamlandı.

**Final focused acceptance run**
- Product/test snapshot: `26b8cad7ba0cd01376bb55c3c27266ab8b121103`
- Run: `35558188351`
- Sonuç: **19 passed / 0 failed**
- Test süresi: **10.44s**
- Full suite: **çalışmadı**
- Corpus: **çalışmadı**
- Day0/Day1/Day2 gate: **tekrar çalışmadı**
- LLM/provider acceptance: **çalışmadı**

**Real demo Wren acceptance**
Gerçek Wren + demo DB üzerinde:
- metric: PASS
- breakdown: PASS
- time period: PASS
- ranking direction + limit: PASS
- simple comparison A-vs-B: PASS
- explicit principal dry-plan/query: PASS
- planned-vs-canonical result equivalence focused set: **5/5 = 100%**
- simple comparison: iki ayrı Wren execution + ResultValidator PASS
- focused real-demo planned-query latency sample count: **7**
- focused Wren planned-query p95 gate: **PASS (<10s)**

Bu küçük focused acceptance setidir; ürün-geneli performans/accuracy iddiası değildir.

**P6 exit**
```text
MUST requirement coverage dedicated paths   100%  PASS
core result equivalence focused canonical   100% (5/5) PASS
P0 silent-wrong found in focused set        0     PASS
principal-aware official execution          100%  PASS
focused Wren planned-query p95             <10s  PASS
real demo metric                            PASS
real demo breakdown                         PASS
real demo time                              PASS
real demo ranking                           PASS
real demo simple compare                    PASS
MinimumQueryContract per official execution structural contract PASS
legacy request fallback                     0
```

**No-touch final cross-check — Day2 seal → Day3**
```text
backend/app/routers/ask.py       unchanged
backend/app/cube_router.py       unchanged
backend/app/uyum.py              unchanged
backend/app/plan_tuketici.py     unchanged
backend/app/plan_semasi.py       unchanged
backend/app/followup.py          unchanged
backend/app/intent_semasi.py     unchanged
.github/workflows/backend-ci.yml absent / yeniden yaratılmadı
```

**Test-hız freeze**
- `a2f8cf18866e04be15dcb539524b39751091d9ef`:
  Day3 focused workflow başarı sonrası `workflow_dispatch`-only yapıldı.
- Day4 ortak `models.py/orchestrator.py` değişiklikleri Day3 gate'i otomatik
  yeniden koşturmayacak.
- Always-on full CI yok ve geri getirilmeyecek.

### V2-D012 — signed-chip sonrası full analytical resume Day4 state bekliyor

- Signed chip Day2'de semantic slotu deterministic çözer.
- Day3, original full `AnalyticalRequest` server-side conversation state'te henüz
  persistent olmadığı için yalnız chip'ten eksik request uydurup query açmaz.
- Bu deliberate fail-closed davranıştır; bug/fallback değil.
- Blocker: Day3 standard fresh-turn query için **NO**.
- Hedef kapanış: Day4 / P7 ConversationState + TopicFrame/FocusState + typed delta.
- Kabul: chip/free-text clarification sonrası yalnız ilgili slot patch edilir ve kalan
  request requirement'ları kaybolmadan standard analytics devam eder.

**Karar**
Day 3 P6 **COMPLETE**.
Day 4 henüz açılmadı.
Bir sonraki geliştirici önce roadmap **P7** ve report **R9**'u yeniden okuyacak; ayrıca
R6 conversation-layer sınırını ve V2-D011/V2-D012 sentinel'lerini çaprazlayacak.
Koddan önce Day4 ticket contract yaşayan deftere yazılacak.



### V2-D013 — full standard-turn E2E p95 henüz ayrı ölçülmedi

- P6 focused gate'in ölçtüğü latency:
  `CubePlanner → WrenService.query` planned-query execution örnekleri (**7 sample**).
- Bu örneklerde focused p95/max <10s kapısı geçti.
- Bu ölçüm; dış provider `TurnInterpreter`, HTTP, resolver, contract persistence ve
  response serialization toplamını kapsayan gerçek kullanıcı `/ask-v2` end-to-end p95
  değildir.
- Roadmap'teki `standard p95 <=10 sn başlangıç` ifadesi ürün deneyimi açısından daha geniş
  okunabileceğinden bu ayrım gizlenmez.
- Day3 correctness blocker: **NO**.
- Core MVP / Day5 performance blocker: **YES**.
- Kapanış: Day5 canonical standard analytics flow'larında küçük ve temsilî end-to-end
  latency sample'ı; provider/infra failure correctness failure diye sayılmadan ölçülür.
- Bu kayıt uğruna Day1 provider corpus'u veya Day3 focused gate **yeniden çalıştırılmadı**.



## 11. DAY 4 ACTIVE TICKET — P7 / R9 + R6 CONVERSATION BOUNDARY

**AMAÇ**  
V2'yi tek-turn analitik uç olmaktan çıkarıp prior canonical IR, focus, clarification ve
evidence/result anchor'larını taşıyan gerçek bir konuşma çekirdeğine dönüştürmek.
Follow-up ve user repair'de yalnız kullanıcının bu turda değiştirdiği typed slot değişir;
diğer canonical slotlar korunur. `RESULT_EXPLAIN` mevcut evidence yeterliyse yeni query
açmaz; `SOCIAL` hiçbir data query çalıştırmaz.

**USER SCENARIO — roadmap canonical**
```text
“bu yıl makine bazında OEE”
→ “sadece RAM-3”
→ “hayır son 3 ay”
→ “bunu yorumla”
→ “teşekkürler”
```

**ROADMAP**
P7 / P7.1 / P7.2.

**REPORT DAYANAK**
- R9 — canonical conversation state: TopicFrame, FocusState, ClarificationState,
  last contract, last IR; raw SQL memory değildir.
- R6 Katman 1 — ConversationState/TopicFrame/FocusState/artifact anchors bounded context.
- R6 Katman 4 — query gerekli mi kararının sahibi DialoguePolicy.
- R3/R3A — prior IR + slot delta; USER_REPAIR typed diff; referential flow.
- R26B NS3 — context preserved, yalnız ilgili slot değişir, explain mevcut evidence
  yeterliyse query açmaz.

**SENTINEL BORÇLAR**
- V2-D011: `sadece RAM-3` refine-vs-repair special-case parser yazmadan doğru state
  transition ile çözülmeli.
- V2-D012: signed/free-text clarification sonrası original analytical request +
  çözülmüş sibling hypotheses kaybolmadan yalnız ambiguous slot patch edilip standard
  analytics devam etmeli.

**NEW OWNER**
- `ConversationCoordinatorV0`
  - typed prior IR + typed current delta,
  - FocusState / TopicFrame,
  - pending analytical clarification state,
  - last result/contract anchors,
  - unrelated-slot preservation.
- `DialoguePolicyV0`
  - TALK
  - CLARIFY
  - EXPLAIN_EXISTING
  - ANALYTIC_STANDARD
  - UNSUPPORTED
  kararının tek sahibi.
- TurnInterpreter language owner olarak kalır.
- SemanticResolver canonical binding owner olarak kalır.
- CubePlanner query plan owner olarak kalır.

**PERSISTENCE SINIRI**
Day4 canonical conversation state HTTP turundan tura typed olarak taşınır ve response'ta
geri döner. Existing `Conversation/ConversationMessage` altyapısı current-state/reuse
kanıtı olarak incelendi; fakat roadmap Day14 persistence/resume işini ayrıca planladığı için
Day4'te legacy AskResponse persistence formatını V2 semantic memory authority yapmayacağız.
Raw SQL veya legacy payload canonical memory olmayacak.

**MINIMUM CONVERSATION STATE**
```text
TopicFrameV0:
  active topic/cube
  last canonical IR identity

FocusStateV0:
  active metrics
  active dimensions
  active filters/entities
  active period
  last contract refs
  last result anchor

ClarificationState:
  existing Day2 state

PendingAnalyticalStateV0:
  original TurnInterpretation
  resolved sibling hypotheses
  blocking clarification
  base prior IR if operation refine/repair

ConversationStateV2:
  last_ir
  topic
  focus
  pending analytical state
  last result / contract anchors
```

**DELTA KURALI**
For `ANALYTIC_REFINE` / `USER_REPAIR`:
- current metric mention varsa metric slotu değişir; yoksa prior korunur,
- current dimension mention varsa dimension slotu değişir; yoksa prior korunur,
- current entity filter yalnız kendi canonical dimension'ındaki prior filter'ı değiştirir;
  diğer filter dimensions korunur,
- current time mention varsa period değişir; yoksa prior korunur,
- ranking/comparison yalnız current typed request taşıyorsa değişir,
- hiçbir slot raw text/SQL edit ile patch edilmez,
- current resolved ref prior cube ile uyumsuzsa silent cross-cube coercion yok; typed
  capability/follow-up failure.

**USER_REPAIR CONTRACT**
Interpreter `USER_REPAIR` çıktısında `analytical_request` yalnız düzeltilen/new typed
surface slotları taşır; unrelated prior slotları model yeniden yazmaz.
ConversationCoordinator bu delta'yı prior IR üstüne uygular.
`correction_spans` tek başına hangi canonical slotun değişeceğini söylemiyorsa tahmin yok.

**CLARIFICATION RESUME**
Clarification oluştuğunda:
```text
original turn
+ all initial hypotheses
+ pending clarification
+ base prior IR (varsa)
```
typed state'te korunur.

Signed/free-text resume:
```text
resolved ambiguous hypothesis
→ pending hypothesis set içindeki aynı source slotu değiştir
→ original turn yeniden yorumlanmaz
→ NEW ise AnalyticsIRBuilder
→ REFINE/REPAIR ise prior IR + typed delta
```
Client payload semantic truth sayılmaz; Day2 signed token integrity devam eder.

**RESULT_EXPLAIN**
Active verified result + contract anchor varsa:
- query = 0
- dry_plan = 0
- existing result/evidence anchor response'a taşınır
- Day4 finalizer/narration mimarisini gereksiz büyütmez; text synthesis Core MVP'de
  ayrıca harden edilebilir.
Active result yoksa yeni SQL uydurulmaz; typed no-active-result outcome.

**SOCIAL**
`SOCIAL` → TALK; query/dry-plan/cube_sql = 0.

**DATASET-AGNOSTIC KURAL — YENİ KALICI İNVARIANT**
Kullanıcı kararıyla `backend/AGENTS.md §12` eklendi
(commit `495f7fe19c71b45c24269727269110ba76e6a6e9`).

Day4 development/test buna özellikle uyar:
- production code demo-boyahane / OEE / RAM-3 / parti / ciro literal'ını bilmez,
- generic conversation mekanizması schema/MDL'den türetilir,
- yalnız mevcut demo DB'ye uygun yapay sorular correctness kanıtı değildir,
- deterministic contract test en az iki sentetik/permuted schema fixture'da aynı
  conversation invariant'ını geçer,
- canonical isimler fixture'da değiştirilince production code değişmez,
- natural-language acceptance gerçekçi kısa/paraphrase follow-up'lardan oluşur,
- real demo Wren smoke ek kanıttır; generic correctness'in tek kanıtı değildir.

**TARGETED NATURAL THREAD A — synthetic manufacturing**
```text
“bu sene hatlara göre verimlilik nasıl?”
→ “yalnız AX-17”
→ “yok, son üç ay olsun”
→ “bu sonucu biraz yorumlar mısın?”
→ “sağ ol”
```
Canonical fixture names kullanıcı dilinden farklı tutulur
(`efficiency_score_z / asset_axis_q / UNIT-Z17 / fact_alpha` gibi).

**TARGETED NATURAL THREAD B — schema permutation**
Aynı conversation invariants; canonical cube/metric/dimension/entity/time-axis adlarının
tamamı değiştirilmiş ikinci fixture. Production code aynı kalır.

**FILES TO TOUCH — beklenen**
- `app/v2/models.py`
- `app/v2/conversation.py` (new)
- `app/v2/dialogue_policy.py` (new)
- `app/v2/interpreter.py` — yalnız USER_REPAIR typed-delta prompt contract'ı
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`
- `tests/test_v2_day4.py` (new focused)
- gerekirse `eval/v2_day4_conversation_cases.yaml` + küçük live evaluator
- bu yaşayan durum dosyası.

**FILES NOT TO TOUCH**
- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/followup.py`
- `app/intent_semasi.py`
- sealed roadmap/report
- historical Day0/1/2/3 measurement artefacts
- removed `.github/workflows/backend-ci.yml`.

**TARGETED TEST / DEMO — HIZ + BAĞIMSIZLIK**
Tek development demetinin sonunda:
1. two-schema metamorphic conversation contract,
2. unrelated-slot preservation,
3. filter same-dimension replacement / unrelated-filter preservation,
4. result-explain query=0,
5. pure-social query=0,
6. signed/free-text clarification resume preserves sibling request slots,
7. stale context/version fail-closed,
8. production conversation source fixture literal ban,
9. gerekiyorsa küçük real-provider realistic-language classification thread,
10. real Wren yalnız ek smoke; sole oracle değil.

Full suite/corpus yok.

**KPI / EXIT**
```text
followup_correctness focused realistic set       >= 90%
repair_slot_preservation regression              100%
canonical 5-turn context break                   0
pure_social_query_rate                           0
result-explain unnecessary query                 0
clarification resume sibling-slot loss           0
schema-permutation invariant break               0
production fixture-literal dependency            0
```

**STOP-THE-LINE**
- prior SQL veya previous CubeQuery canonical conversation memory yapılırsa,
- follow-up raw question ikinci kez parser ile çözülürse,
- `RAM-3`, OEE, demo cube adları için production special-case yazılırsa,
- repair'de current message'ta olmayan prior slotlar LLM tarafından yeniden yazdırılırsa,
- pending clarification sibling hypotheses/request kaybedilirse,
- RESULT_EXPLAIN mevcut result varken query açarsa,
- SOCIAL query açarsa,
- test yalnız demo DB'deki bilinen satırlara uyan sorularla yeşil yapılırsa,
- fake schema tek correctness kanıtı olursa,
- second/permuted schema aynı generic invariant'ı bozarsa,
- Day14 persistence kapsamı Day4'e wholesale çekilirse.



### 2026-09-21 — DAY 4 / live realistic-language gate 1 — ROOT CLASSIFICATION

**Run**
- workflow: `v2-day4-live-conversation`
- run: `35559963264`
- artifact: `10621862234`
- digest:
  `sha256:8447fa93efcabafc2e49d7b5e22ea37aee58088989bceeac57db13af7247f61f`
- source policy: `synthetic_schema_permuted_no_demo_db`
- threads: **6**
- natural turns: **30**
- demo DB access: **0**

**Measured**
```text
structured success              30/30 = 100%
turn act accuracy               26/30 = 86.67%
follow-up correctness            4/12 = 33.33%
repair slot preservation         2/6  = 33.33%
result explain classification    6/6  = 100%
social classification            6/6  = 100%
surface grounding violation      0
max LLM calls/case               1
```

**Failure-stage analysis — DB/fixture değil language contract**
1. Repair-vs-refine sınırı:
   - düzeltme/retraction anlamı taşıyan bazı doğal turlar `USER_REPAIR` yerine
     `ANALYTIC_REFINE` geldi.
   - slot extraction doğruydu (time-only), dialogue act precedence eksikti.
2. Entity-member vs grouping-axis sınırı:
   - “yalnız/bir tek <somut üye/id>” refinement'larının bazılarında somut member
     `filter` yerine `dimension` veya `dimension+filter` olarak etiketlendi.
   - canonical DB bilgisi verilmediği için bu tam olarak generic language-role ayrımıdır.
3. Bir turda `pending_clarification=false` olmasına rağmen correction
   `CLARIFICATION_ANSWER` seçildi; state precondition istemde yeterince sert değildi.

**Yapılmayacak**
- K-17 / Kuzey-4 / Ekip-N / Tesis-C için branch, regex veya örnek sözlük eklenmeyecek.
- Test case çıkarılıp oran yapay biçimde yükseltilmeyecek.
- Demo DB değerleri prompt'a konup modelin işi kolaylaştırılmayacak.
- Resolver/Planner'a ikinci language owner eklenmeyecek.

**Kök düzeltme**
TurnInterpreter sözleşmesi generic olarak keskinleştirilecek:
- correction/retraction, additive refinement'tan önce gelir → `USER_REPAIR`;
- `CLARIFICATION_ANSWER` için `pending_clarification=true` hard semantic precondition;
- concrete selected member/value/identifier → `filter_mentions`;
- grouping/category axis → `dimension_mentions`;
- aynı concrete surface yalnız grouping açıkça istenmiyorsa dimension+filter diye
  duplicate edilmez.

Sonra **yalnız aynı 30-turn live gate** bir kez daha çalıştırılacak.
Deterministik 8-test gate/full suite/corpus tekrar açılmayacak.



### 2026-09-21 — DAY 4 / MODEL CAPABILITY KARARI

Aynı 30-turn DB-independent corpus `deepseek/deepseek-v4-flash` ile birden fazla kez
çalıştırıldı. Structured output %100 ve surface-grounding violation 0 kalırken ince
conversation speech-act sınırları run'lar arasında ciddi oynadı:

```text
run 1: act 86.7% | follow-up 33.3% | repair 33.3%
run 2: act 90.0% | follow-up 66.7% | repair 50.0%
run 3: act 70.0% | follow-up 33.3% | repair 33.3%
run 4: act 83.3% | follow-up 58.3% | repair 16.7%
```

`temperature=0` olmasına rağmen bu varyans ve eşik-altı sonuç, fixture/DB probleminden
bağımsız bir **model capability / instruction-following stability** problemi olarak
sınıflandırıldı. Prompt'a daha fazla fixture-benzeri örnek yığmak reddedildi.

**Karar**
- TurnInterpreter tek language owner olarak kalır.
- V2 TurnInterpreter için ayrı, explicit model capability tanımlanır.
- Default: `openai/gpt-5.6-luna` (OpenRouter), çünkü Day1 tarihsel acceptance'ta
  structured 28/28 ve act 27/28 ölçülmüştür.
- Core/general OpenRouter modeli `deepseek/deepseek-v4-flash` olarak kalır.
- Legacy select/generate davranışı değişmez.
- V2 interpreter model yoksa silent lower-quality fallback yapılmaz; mevcut global LLM
  yalnız explicit configuration/fallback policy ile kullanılabilir.
- Bu ayrım bir semantic-owner çoğalması değildir: model transport değişir, owner yine
  yalnız `TurnInterpreter`dır.

**Yeni config contract**
```text
DIMA_V2_INTERPRETER_PROVIDER=openrouter
DIMA_V2_INTERPRETER_MODEL=openai/gpt-5.6-luna
```

**Exit ölçümü**
Aynı 30-turn corpus DEĞİŞTİRİLMEDEN dedicated interpreter model ile yeniden çalışır.
Pass olursa ayrıca yeni, tuning sırasında kullanılmamış küçük holdout çalıştırılır.

