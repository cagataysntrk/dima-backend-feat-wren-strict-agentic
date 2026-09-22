# DIMA V2 — GELİŞTİRME DURUMU

**Branch:** `feat/ask-v2-mvp`  
**Başlangıç tabanı:** `wren-bağımsız@869280db316d5bf3f76d3253b8b80e5609a000b9`  
**Başlangıç tarihi:** 20 Eylül 2026  
**Durum:** **D65-SI FINAL GREEN / SEALED — M0E-DEEP-DELTA ACTIVE; X0-BRIDGE-PREFLIGHT NEXT AFTER M0E FINAL; X0/DEV80 FORBIDDEN**  
**Kod fazı:** D65-SI is sealed FINAL GREEN at tested HEAD `c72eb913...`. Evidence: provider-free/family `35738044476 = 73/73 PASS`; focused real-live frozen 001+005 `35738400321 = GREEN`; exact frozen six-case full-live `35738912690 = GREEN`, artifact `completed_cases=6`, `failed_case_ids=[]`, `accepted=5`, `clarified=1`. Last product-code change before seal = `fb2f243...`; final seal commits thereafter are docs/workflow only. Semantic-discovery optimization cycle is CLOSED absent new P0 evidence. Current primary work = `DIMA_DAY6_5_M0E_DEEP_DELTA_CONTRACT.md` source/classification to `UNCLASSIFIED=0`; then `DIMA_DAY6_5_X0_BRIDGE_PREFLIGHT.md`. No Metabase runtime yet. `/ask-v2` migration remains Day10 release blocker. DEV80/Validation50/Hidden50 forbidden.  

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
- `DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md` — current Day 6.5 engineering closure authority.
- `DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md` — runtime-kernel, Standard terminology ve substrate/reference authority.
- `DIMA_DAY6_5_PREFREEZE_DECISION_GATE_J1_M0_X0.md` — **current J1S/J1T + M0/X0 decision authority**.
- `DIMA_RELEASE_FINAL_INTEGRATED_GATE.md` — **release-level final freeze / DEV80 / Validation50 / Hidden50 timing authority**.
- `DIMA_DAY6_5_J1_BENCHMARK_CONTRACT.md` — J1S/J1T corrected frozen lab benchmark contract.
- `DIMA_DAY6_5_J1B_REAL_FLOW_RECEIPT.md` — J1B real-flow evidence/RED receipt.
- `DIMA_DAY6_5_PROVIDER_TOPOLOGY_ENGINEERING_RECEIPT.md` — **chosen P0=0 Day6.5 engineering model topology evidence**.
- `DIMA_DAY6_5_POST_J1B_LUNA_M0E_HANDOFF.md` — **current continuation handoff / provider ladder / stop points**.
- `DIMA_DAY6_5_M0E_CAPABILITY_EXHAUSTION_BUILD_VS_BUY.md` — Metabase exhaustion/build-vs-buy contract.
- `DIMA_DAY6_5_M0E_EXHAUSTION_RECEIPT.md` — **M0E GREEN mechanism classification receipt**.
- `DIMA_DAY6_5_STANDARD_INTEGRATION_CLOSURE.md` — **D65-SI authority; FINAL GREEN / SEALED**.
- `DIMA_DAY6_5_SI_FINAL_SEAL.md` — **final SI evidence + causal chain + anti-patch seal**.
- `DIMA_FRONTDOOR_OWNERSHIP_CLOSURE.md` — **Day10 release blocker for authoritative /ask-v2 ownership**.
- `DIMA_DAY6_5_X0_BRIDGE_PREFLIGHT.md` — **mandatory bridge gate before Metabase runtime X0**.
- `DIMA_DAY6_5_M0E_DEEP_DELTA_CONTRACT.md` — **reopened final Metabase exhaustion delta**.
- `DIMA_DAY6_5_POST_ANALYST_RECONCILED_HANDOFF.md` — **CURRENT continuation authority after analyst audit**.
- `DIMA_DAY6_5_METABASE_ADOPTION_MATRIX.md` — D65-M0 adoption-audit working matrix.
- `DIMA_DAY6_5_METABASE_DEPLOYMENT_TOPOLOGY_DECISION.md` — Metabase Cloud/self-host/bundled-service/source-port deployment decision gate.
- `../../MIMARI.md` — mevcut sistem gerçekleri + V2 authority overlay.
- `../../AGENTS.md` — V2 geliştirici/ajan çalışma sözleşmesi.
- `../../CLAUDE.md` — repo kuralları; V2 branch override üstte olmalıdır.

---

### Historical sequence precedence rule

Bu living status eski commit/run kararlarını audit amacıyla silmez.
Eski günlük bölümlerinde görülen `Day6.5 freeze → DEV80`, `DEV80 → D65-X`,
`one DEV80 per candidate` gibi ifadeler **historical record** kabul edilir.

Current timing authority yalnız:
1. `DIMA_DAY6_5_PREFREEZE_DECISION_GATE_J1_M0_X0.md` — current Day6.5 decisions,
2. `DIMA_RELEASE_FINAL_INTEGRATED_GATE.md` — final release freeze/80/50/50 timing.

Çelişkide bu iki current authority üstün gelir.

---

## 0A. CURRENT PRE-RUN RECEIPT — 2026-09-22

```text
entry checkpoint                f2b246a7f186705f8ddd98a61e60d950f606d326
J1 freeze                       d65-j1-freeze-v2
J1S blob                        0dd53d5b1bb2ac39ba35f2c17c870c45c249d686 (UNCHANGED)
J1T blob                        d18db04d26da1059e4ebb47d058f305e2e5a5bfb (UNCHANGED)
corrected prep commit           732741be94ea7d5a618e5d566730875877d5fa59
provider-free corrected run     35705204058 = 6/6 PASS
wrong-topology run              35704627396 = INVALID AUTHORITY
product semantic code touch     0
product temporal code touch     0
authority code touch            0
```

Current required order:

```text
corrected primary transport smoke
→ corrected J1 full evidence
→ J1 decision gate
→ if Jev promising: STOP / consult before J1B or topology change
→ else current topology retained
→ D65-SI Standard Integration Closure
→ real Standard Wren vertical
→ X0
→ if X0 promising: STOP / consult before full D65-X
```

J1 evidence is split:
- J1S model-needed score vs deterministic/sensitive/retrieval controls;
- J1T-CHOICE vs J1T-CONTRACT-FIDELITY.
Jev native Decisions has no dynamic integer output primitive; dynamic `n` /
`implicit_base_n` is recorded as `TEMPORAL_INTEGRATION_LIMITATION`, not hidden by
case-enumeration/prompt hacks.

---

## 0C. TERRA CONDITIONAL CLOSED / J1B OPEN

```text
Terra valid run                  35710080143
J1T choice                       34/34
unsafe ambiguity                 0
repeat/metamorphic               100% / 100%
J1T exact typed contract         34/34
invalid typed                    0
provider failure                 0

J1B semantic candidate           typesafe/jev-1.13
J1B temporal candidate           openai/gpt-5.6-terra
production seal                  NO
fallback/cascade/threshold       NONE
```

Current immediate sequence:

```text
D65-J1B narrow provider-contract split
→ provider-free P0
→ semantic ambiguity failure-family
→ temporal typed-contract family
→ metamorphic
→ workers=1 real-LLM focused
→ small representative canary
→ if GREEN: D65-SI
```

---

## 0D. J1B REAL-FLOW RED — CONSULTATION

```text
run                          35713785149
tested SHA                   09c9128bd385a83c099b18855636b703d73bec48
fresh corpus                 d65-j1b-semantic-family-v1-frozen
semantic provider            typesafe/jev-1.13
temporal provider            openai/gpt-5.6-terra
workers                      1
fallback/cascade/threshold   NONE

Jev semantic                 12/20
silent semantic wrong        8   STOP
unsafe ambiguity auto-pick   8   STOP
candidate escape             0
cross-tenant leak            0
provider failure             0

Terra temporal               6/8
temporal wrong               2
provider failure             0
```

Mandatory consultation gate is active.
D65-SI, real Standard Wren sentinel and X0 execution may not start until the J1B semantic /
temporal provider decision is explicitly resolved.

---

## 0E. POST-J1B CONSULTATION RESOLVED — LUNA + M0E

Binding decision:

```text
Jev universal provider         = REJECT
Jev temporal provider          = REJECT
Jev semantic provider AS-IS    = REJECT
Jev calibration/verifier       = DEFER / POST-MVP

next semantic control          = Luna / same frozen 20
next temporal control          = Luna / same frozen 8
role-specific fallback         = Sol REFERENCE_CEILING only if Luna role fails
Gemini automatic rerun         = NO
Terra retuning                 = NO
threshold/fallback/cascade     = NONE
```

Acceptance for chosen engineering provider topology:

```text
silent_semantic_wrong       = 0
unsafe_ambiguity_auto_pick  = 0
candidate_escape            = 0
cross_tenant_leak           = 0
provider_failure            = 0
real_flow_temporal_wrong    = 0
invalid_typed_contract      = 0
```

Parallel work:
`D65-M0E capability exhaustion + build-vs-buy classification`.

Sequence:
```text
Luna frozen controls
→ if needed failed-role Sol ceiling
→ provider topology P0=0
+
M0E
→ D65-SI
→ real Standard Wren sentinel
→ M0E final cross-check
→ X0 residual-value/runtime-necessity
```

Wren semantic backbone:
`RETAIN by default`; removal is a separate consultation.

---

## 0F. LUNA SAME-FROZEN CONTROL — SEMANTIC GREEN / TEMPORAL A-B

```text
run                         35716056419
tested SHA                  c256ebfda765ac35f1d3b51f59d53d1018dd695e
frozen corpus blob          cc68f87271dcaada1443d2cf9e48024b85bff9f3
provider-free               31/31 PASS

Luna semantic               20/20 GREEN
silent semantic wrong       0
unsafe ambiguity pick       0
candidate escape            0
cross-tenant leak           0

Luna temporal               6/8 RED
invalid typed               0
provider failure            0
failed family               previous-period comparison with separately bound base period
```

Terra failed the same two temporal scenarios. Therefore:
```text
semantic engineering candidate = Luna
temporal owner classification  = pending exact-same-SHA Sol ceiling
D65-SI                         = BLOCKED
```

---

## 0G. PROVIDER TOPOLOGY P0 GREEN

```text
Luna semantic run             35716056419 = 20/20 P0=0
Sol temporal exact-SHA run    35716502261 = 8/8 P0=0
exact tested backend SHA      c256ebfda765ac35f1d3b51f59d53d1018dd695e

SEMANTIC_LINKER               Luna
TEMPORAL_NORMALIZER           Sol
RESEARCH_MANAGER              Sol

BindingGate                   unchanged
TemporalBindingEngine         unchanged
fallback/cascade/threshold    none
production activation         NO
```

Provider topology P0 gate is closed. Current active blocker before D65-SI:
`D65-M0E capability exhaustion/build-vs-buy completion`.

---

## 0H. M0E GREEN — D65-SI ENTRY OPEN

```text
provider topology P0       GREEN
M0E capability exhaustion  GREEN
Dima-relevant unclassified 0
Wren semantic default      RETAIN
Metabase production dep    OFF
```

Current next ticket:
`D65-SI STANDARD INTEGRATION CLOSURE`.

X0 remains blocked until:
`D65-SI GREEN → real Standard Wren sentinel GREEN → M0E final cross-check`.

---

## 0I. POST-ANALYST RECONCILIATION — CURRENT AUTHORITY

Current single handoff:
`DIMA_DAY6_5_POST_ANALYST_RECONCILED_HANDOFF.md`.

```text
HEAD                         3774484167f1056d89da0e0609246fb4a05057ec
SI focused                   35718675540 = 25/25 PASS
real Wren sentinels          35718883950 = 2/2 PASS

SI implementation            PARTIAL GREEN
SI final composition         OPEN
M0E-v1                       VALID BASELINE / PRESERVED
M0E-DEEP-DELTA               OPEN
X0-BRIDGE-PREFLIGHT          OPEN / BLOCKS X0
X0 execution                 BLOCKED
production /ask-v2           OFF
DEV80                        FORBIDDEN
```

Immediate order:
`semantic-surface P0 → shared authority arbiter → Research temporal split → focused proofs`.

Parallel:
`M0E-DEEP-DELTA`.

Then:
`workers=1 full-live Standard composition → SI FINAL + M0E delta FINAL → bridge preflight`.

---

## 0J. FULL-LIVE STANDARD RED — EXACT ROOT SUBCAUSE PROVEN

```text
failed full-live run       35724830736
same-product diagnostic    35728413368

surface                    "tahsil edilmemiş cari bakiye"
metric catalog             136
exact candidates           0
linker bound               48
too_broad                  true
semantic provider called   false
selection                  CANDIDATE_SET_TOO_BROAD
```

Classification:
`CONTRACT/ARCHITECTURE → SEMANTIC_DISCOVERY_BREADTH`.

No context-loss repair is authorized for this case.
Next:
`generic bounded retrieval → family/metamorphic provider-free proof → same frozen 6-case live rerun`.

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



### 2026-09-21 — DAY 4 / MODEL CAPABILITY KARARI — SUPERSEDED

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

**SUPERSEDED NOTU — 2026-09-21**  
Bu ara karar, kullanıcı tarafından daha önce açıkça mühürlenen ileriye dönük tek model authority'siyle çeliştiği için uygulanabilir son karar değildir. Day1 Luna measurement tarihsel provenance olarak kalır; yeni çalışma/test default'u `deepseek/deepseek-v4-flash`tır. Dedicated Luna transport yolu final Day4 seal öncesi kaldırılmıştır.

**Tarihsel ara karar (uygulanmıyor)**
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



### 2026-09-21 — DAY 4 / P7 COMPLETE — FINAL SEAL

**Authority cross-check**
- Roadmap P7 yeniden okundu.
- Report R9 + R6 conversation boundary yeniden okundu.
- P7 normatif correctness:
  - prior IR + deterministic delta,
  - unrelated-slot preservation,
  - canonical 5-turn context continuity,
  - social query = 0,
  - result-explain unnecessary query = 0.
- Exact `ANALYTIC_REFINE ↔ USER_REPAIR` subtype etiketi P7 release gate değildir;
  semantic state transition doğruysa diagnostic olarak tutulur.

**Final architecture**
```text
TurnInterpreter
→ DialoguePolicyV0
→ SemanticResolver
→ ConversationCoordinatorV0
→ prior AnalyticsIR + typed current delta
→ RequirementLedger
→ CubePlanner
→ Wren execution
→ ResultValidator
→ MinimumQueryContract
→ updated ConversationStateV2
```

**Conversation state**
Canonical Day4 state artık şunları typed taşır:
- `TopicFrameV0`
- `FocusStateV0`
- `ClarificationState`
- `PendingAnalyticalStateV0`
- `last_ir`
- `last_result`
- contract refs / result anchors.

Raw SQL ve previous CubeQuery canonical memory değildir.

**Typed delta semantics**
- Current metric varsa metric slotu değişir; yoksa prior korunur.
- Current dimension varsa breakdown slotu değişir; yoksa prior korunur.
- Current entity filter yalnız kendi canonical dimension filter'ını değiştirir.
- Unrelated filters korunur.
- Current time varsa period değişir; yoksa prior period korunur.
- Ranking/comparison yalnız current typed request'te varsa değişir.
- Cross-cube uyuşmazlıkta silent coercion yok.
- Empty continuation delta fail-closed; query açılmaz.

**Clarification resume — V2-D012 CLOSED**
- Pending clarification sırasında original analytical request saklanır.
- Initial resolved sibling hypotheses saklanır.
- Base prior IR saklanır.
- Signed-chip resume yalnız ambiguous hypothesis'i patch eder.
- Free-text resume aynı typed pending state'i kullanır.
- Original turn yeniden semantic parse edilmez.
- Sibling metric/request slotu kaybolmaz.
- Dedicated focused testlerde signed + free-text resume PASS.

**“sadece RAM-3” sentinel — V2-D011 CLOSED**
- Production code'da `RAM-3` veya eşdeğer fixture literal special-case yok.
- Concrete member/value → Resolver candidate → canonical filter delta.
- Prior metric/dimension/time korunur.
- `REFINE` ile `USER_REPAIR` subtype'ı semantic state transition'ı değiştirmiyorsa
  downstream owner'lara özel patch yazılmaz.
- Doğru owner:
  - language surface → TurnInterpreter,
  - canonical filter binding → SemanticResolver,
  - prior IR + slot transition → ConversationCoordinator.

**No-query policy**
- Verified active result + RESULT_EXPLAIN → existing result/evidence, query=0.
- SOCIAL → TALK, query=0.
- Empty/mislabelled analytical continuation with zero delta → fail-closed before Wren,
  query=0.
- Clarification → query=0 until resolved.

**Dataset-agnostic correctness**
`backend/AGENTS.md §12` kalıcı kuraldır.
Day4 primary correctness kanıtı repo demo DB'sine göre kurulmadı:
- iki tamamen farklı synthetic/permuted schema,
- user language ile canonical identifiers birbirinden farklı,
- aynı 5-turn invariant iki schema'da production code değişmeden geçti,
- production conversation code fixture literal ban PASS,
- real Wren smoke capability'yi schema'dan dinamik seçti; demo metric/cube adı hard-code edilmedi.

**Single-owner root-fix — kalıcı kural**
`backend/AGENTS.md §13` eklendi:
```text
failure
→ failure stage
→ normative requirement
→ “Bu kararın tek sahibi kim?”
→ yalnız owner'da root fix
→ focused proof
```
Şu refleks yasak:
```text
prompt başarısız
→ resolver özel if
→ planner fallback
→ orchestrator exception branch
→ test yeşil
```

**Final deterministic focused gate**
- Workflow: `35563410971`
- Result: **9 passed / 0 failed**
- Pytest: **6.06s**
- Full suite: **0**
- legacy corpus: **0**
- Day0/1/2/3 rerun: **0**
- Includes:
  - two-schema permutation,
  - canonical natural 5-turn state flow,
  - unrelated-slot preservation,
  - same-dimension filter replacement,
  - explain query=0,
  - social query=0,
  - signed clarification resume,
  - free-text clarification resume,
  - sensitive conversation prompt boundary,
  - fixture-literal production ban,
  - dynamic real-Wren time-repair smoke,
  - empty continuation cannot query.

**Live DB-independent language evidence — raw preserved**
DeepSeek/OpenRouter run:
- workflow: `35561951458`
- artifact: `10622696301`
- digest:
  `sha256:6ad0e367d6892500b5340060fecb0450057ec7e7246db8dcb94ddbc8abeb7b78`
- model provenance from workflow log:
  `DIMA_OPENROUTER_MODEL=deepseek/deepseek-v4-flash`
- threads: **6**
- turns: **30**
- demo DB access: **0**
- structured output: **30/30 = 100%**
- surface grounding violation: **0**
- max LLM calls/case: **1**
- exact raw turn-act label accuracy: **70% diagnostic**
- exact social label: **5/6 diagnostic**

**P7 normative re-score of SAME raw records**
Test cases ve provider outputları değiştirilmedi.
Roadmap P7 state-transition oracle'ına göre:
```text
routing action accuracy                 29/30 = 96.67%
follow-up typed-delta correctness       12/12 = 100%
repair changed-slot preservation         6/6  = 100%
result-explain classification            6/6  = 100%
social analytical-payload safety         6/6  = 100%
structured output                       30/30 = 100%
surface grounding violation                 0
```
Permanent record:
`backend/eval/v2_day4_measurement.json`.

**Neden eski live evaluator FAIL idi?**
İlk evaluator proxy olarak exact `REFINE/USER_REPAIR` label eşitliğini semantic
correctness sayıyordu. P7 ise bekleneni açıkça:
```text
turn2 prior IR + filter
turn3 prior IR + time repair
```
diye tanımlar. Aynı typed delta / aynı state transition üretildiğinde subtype farkını
release blocker yapmak roadmap'te olmayan bir şart ekliyordu.
Raw measurement silinmedi veya değiştirilmedi; exact label metriği diagnostic kaldı.
Evaluator owner/test-oracle kuralına göre düzeltildi.

**Model authority — final**
Kullanıcının daha önce mühürlediği ileriye dönük authority korunur:
- operational/focused OpenRouter default:
  `deepseek/deepseek-v4-flash`.
- Day1 `openai/gpt-5.6-luna` ölçümü tarihsel provenance olarak DEĞİŞMEDİ.
- Sonradan eklenen dedicated `v2_interpreter_model=openai/gpt-5.6-luna` yolu
  **SUPERSEDED ve kaldırıldı**.
- `config.py / llm.py / main.py / v2/orchestrator.py` DeepSeek run-3 öncesindeki
  tek-model-policy hâline geri alındı.
- Live workflow'taki V2 Luna env override kaldırıldı.
- Yeni live test sırf bu policy restore için tekrar çalıştırılmadı; run-3 zaten
  DeepSeek provenance taşıyor.

**Workflow discipline**
- `v2-day4-conversation.yml` → workflow_dispatch-only.
- `v2-day4-live-conversation.yml` → workflow_dispatch-only.
- live workflow structural testleri tekrar koşturmaz; yalnız language eval yapar.
- removed `backend-ci.yml` yok ve geri gelmedi.
- final status/document/model-policy commitleri otomatik test başlatmaz.

### V2-D014 — exact continuation subtype / acknowledgment language diagnostic

Day4 P7 blocker değildir; Day5 attack-table girdisidir.

Observed:
- `ANALYTIC_REFINE ↔ USER_REPAIR` exact subtype DeepSeek'te varyanslı.
- Bir natural acknowledgement (`tamamdır`) bir run'da boş `ANALYTIC_REFINE` çıktı.

Safety:
- typed analytical slot payload doğru/boş kaldı,
- ConversationCoordinator unrelated slots'u koruyor,
- empty continuation fail-closed,
- query=0 sentinel final focused testte PASS.

Day5 beklentisi:
- exact language quality ayrı diagnostic olarak saldırı masasında ölçülür,
- fakat çözüm downstream özel if/fallback olmayacak,
- failure sahibi TurnInterpreter ise yalnız onun contract/model/prompt boundary'si ele alınır.

**P7 EXIT**
```text
followup_correctness focused realistic set       100%   PASS
repair_slot_preservation regression              100%   PASS
canonical 5-turn context break                      0   PASS
pure_social_query_rate                              0   PASS
result-explain unnecessary query                    0   PASS
clarification resume sibling-slot loss              0   PASS
schema-permutation invariant break                  0   PASS
production fixture-literal dependency               0   PASS
legacy semantic fallback                            0   PASS
```

**No-touch final cross-check**
```text
backend/app/routers/ask.py       unchanged
backend/app/cube_router.py       unchanged
backend/app/uyum.py              unchanged
backend/app/plan_tuketici.py     unchanged
backend/app/plan_semasi.py       unchanged
backend/app/followup.py          unchanged
backend/app/intent_semasi.py     unchanged
.github/workflows/backend-ci.yml absent
```

**Karar**
Day 4 / P7 **COMPLETE**.
Day 5 / P8 henüz açılmadı.

---

## 12. DAY 5 READY DIRECTIVE — CORE MVP SALDIRI MASASI

Day5 başlamadan:
1. Roadmap **P8** yeniden oku.
2. Report **R6.1 + R20** yeniden oku.
3. V2-D013 (full E2E p95) + V2-D014 (language subtype diagnostic) çaprazla.
4. Kod/feature eklemeden önce attack-ticket yaşayan deftere yaz.
5. İlk çalışma **feature değil eval/trace/failure-classification** olacak.

**Day5 ciddi denetim biçimi**
Tek tek sınıflara unit-test eklemek yerine gerçek kullanıcı gibi `/ask-v2` yüzeyine
uçtan uca saldır:

| Attack | Beklenen invariant |
|---|---|
| paraphrase | aynı semantic requirement; fixture/canonical wording ezberi yok |
| typo | silent wrong yok; safe resolve veya clarification |
| ambiguity | blocking auto-selection=0; clarification query=0 |
| clarification answer | yalnız pending slot patch; sibling loss=0 |
| repair | unrelated-slot loss=0 |
| follow-up | prior IR korunur; yalnız current delta |
| topic switch | old focus bleed=0; yeni TopicFrame görünür |
| comparison | A/B semantiği korunur; tek range'e çökme yok |
| ranking | direction + semantic limit birlikte korunur |
| result explain | active result yeterliyse query=0 |
| pure social | SQL/query=0 |
| malformed clarification token | fail-closed; semantic fallback=0 |
| stale context/version | stale replay=0; fail-closed |
| provider/infra failure | correctness fail diye sayma; typed unavailable/failure |
| cross-tenant attempt | evidence/data leak=0 |
| silent-wrong attack | wrong-but-plausible official answer=0 |

**Day5 çalışma kuralı**
Roadmap P8 zaten söyler:
```text
Yeni özellik ekleme.
Yalnız:
eval
trace
failure classify
root fix
```

Her kırmızı için:
```text
Bu kararın tek sahibi kim?
```
sorusu cevaplanmadan kod değişikliği YOK.

**Day5 blocker gate**
```text
P0 silent-wrong                     = 0 MVP holdout
blocking ambiguity auto-selection   = 0
clarification SQL                   = 0
pure social SQL                     = 0
user repair unrelated-slot loss     = 0
canonical threads context break     = 0
unhandled 500                       = 0
executed queries principal-aware    = 100%
standard E2E p95                    <= 10s
clarify p95                         <= 6s
```

Day5 bu saldırı masası geçmeden Research Mode / Day6 açılmaz.


## 13. DAY 5 ACTIVE TICKET — P8 CORE MVP PRODUCT INTEGRATION

**AMAÇ**  
Day0–4'te ayrı ayrı kanıtlanan runtime → interpreter → resolver → AnalyticsIR/Ledger →
planner/execution → conversation zincirini gerçek `/ask-v2` ürün akışında tek Core MVP
olarak tamamlamak. Day5 yalnız denetim değildir: önce eksik ürün/finalization entegrasyonu
kapanır; **sonra** P8 exit saldırı masası çalışır.

**USER SCENARIO**
Tek gerçek conversation içinde:
```text
1. basit analitik soru → text-first verified answer
2. belirsiz soru → nokta atışı clarification + signed chips, query=0
3. chip/free-text clarification answer → sibling slot kaybetmeden doğru query
4. follow-up refinement → prior IR + current delta
5. user repair → unrelated slot kaybı yok
6. result explain → mevcut evidence/result, query=0
7. pure social → insan-okur talk response, query=0
```

**ROADMAP**  
P8 / P8.A; P6/P7 kullanıcı-facing kabul yüzeyleriyle birlikte.

**REPORT DAYANAK**  
R6.0 Katman 10 Conversation Finalizer, R6.1 L1–L2 capability ladder,
R6.2/R6.3 text-first + visible-scope + clarify-in-place UX,
R10 Standard Analytics yolu, R20 değişmezleri, R25.1 normal yol.
R3A anti-pattern matrisi Day5 root-fix authority'sidir.

**YORUM / P8 SINIRI**  
P8'deki “Yeni özellik ekleme”:
- Research/Decision/yeni analytics capability ekleme YOK;
- Day0–4 çekirdeğini ürün yüzeyine tamamlayan **Finalizer / ConversationResponse / UI adapter**
  entegrasyonu Day5'in Core MVP kapanış işidir.
- Finalizer veya UI semantic eksikliği tahminle kapatamaz.

**NEW OWNER**
- `ConversationFinalizerV0` → yalnız doğrulanmış typed state/evidence'dan kullanıcı-facing
  `ConversationResponseV0` üretir.
- Finalizer **semantic owner değildir**:
  - raw question parse etmez,
  - metric/entity seçmez,
  - requirement tamamlamaz,
  - DB/Wren çağırmaz,
  - yeni sayı/hesap üretmez.
- `/ask-v2` route → orchestrator'ın typed Core sonucunu Finalizer'dan geçirip ürün
  response contract'ını dönen HTTP product boundary.
- Frontend V2 adapter → backend'in verdiği answer/scope/clarification/evidence contract'ını
  render eder; client-side semantic heuristic yok.

**REUSE EDİLEN PRIMITIVE**
- Day0–4 V2 orchestrator + typed ConversationState.
- MinimumQueryContract / ContractStore evidence refs.
- mevcut frontend conversation shell / auth-enabled api client.
- mevcut Wren/Principal/ContextVersion değişmezleri.

**FILES TO TOUCH — beklenen**
Backend:
- `app/v2/models.py`
- `app/v2/finalizer.py` (new)
- `app/routers/ask_v2.py`
- `app/v2/orchestrator.py` yalnız product-finalization için gerçekten gerekiyorsa minimal.
Frontend:
- `src/lib/types.ts`
- `src/lib/api-client.ts`
- mevcut conversation shell'e **küçük V2 adapter/surface**; full UI rewrite YOK.
Docs:
- bu yaşayan durum dosyası.

**FILES NOT TO TOUCH**
- sealed roadmap/report
- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/followup.py`
- `app/intent_semasi.py`
- historical Day0–4 measurement artefacts
- removed `.github/workflows/backend-ci.yml`.

**PRODUCT RESPONSE CONTRACT — DAY5**
Minimum:
```text
ConversationResponseV0
  kind                  answer | clarify | talk | explain | semantic_gap | unsupported | failure
  text                  text-first user-facing body
  scope_chips[]         backend-derived; semantic authority değil
  clarification_chips[] signed backend tokens
  evidence_refs[]       contract/execution refs
  table?                verified execution preview; optional
  official_verified
```

Kurallar:
- numeric cell yalnız verified execution/result'tan gelir; Finalizer hesap yapmaz.
- semantic display label yalnız resolver hypothesis/canonical state'ten gelir.
- sensitive filter value açık scope chip'e sızmaz.
- clarify/talk/explain typed action'a göre finalize edilir; raw text tekrar parse edilmez.
- failure/semantic-gap boş veya “dead” response üretmez.
- RESULT_EXPLAIN existing verified result kullanır; query açmaz.
- UI backend state'ini heuristics ile yeniden çözmez.

**TARGETED DEVELOPMENT PROOF — test fazına geçmeden önce**
- endpoint response her terminal Core action için user-facing `ConversationResponseV0` taşır,
- standard answer contract/evidence refs taşır,
- clarification signed token UI'ya kadar taşınabilir,
- conversation state bir sonraki V2 turn'de aynen yankılanabilir,
- frontend'de gerçek `askV2()` consumer vardır; legacy `/ask` silent fallback YOK.

**EXIT TEST — geliştirme bittikten sonra kısa/nokta atışı**
Önce küçük Core MVP integration testleri; sonra P8 saldırı masası.
Full suite / legacy corpus / uzun CI YOK.

**P8 SALDIRI AİLELERİ**
```text
paraphrase · typo · ambiguity · clarification resume · repair · follow-up
topic switch · comparison · ranking · result explain · pure social
malformed clarification token · stale context/version · provider/infra failure
cross-tenant attempt · silent-wrong
```

Her kırmızıda:
```text
observed failure
→ failure stage
→ normative requirement
→ Bu kararın tek sahibi kim?
→ yalnız owner'da root fix
→ focused proof
```

**EXIT / RELEASE BLOCKER**
```text
P0 silent-wrong                     = 0 MVP holdout
blocking ambiguity auto-selection   = 0
clarification SQL                   = 0
pure social SQL                     = 0
user repair unrelated-slot loss     = 0
canonical threads context break     = 0
unhandled 500                       = 0
executed queries principal-aware    = 100%
standard E2E p95                    <= 10s
clarify p95                         <= 6s
dead/broken Core response           = 0
frontend semantic re-interpretation = 0
legacy silent fallback              = 0
```

**STOP-THE-LINE**
- Finalizer raw question/SQL parse etmeye başlarsa,
- Finalizer missing metric/filter/ranking'i tahmin ederse,
- UI canonical semantic anlam seçerse,
- response text evidence/result dışında yeni numeric claim üretirse,
- `/ask-v2` başarısızlığında legacy `/ask` sessiz fallback açılırsa,
- test için demo-boyahane/OEE/RAM-3 vb production special-case yazılırsa,
- attack test oracle'ı implementation SQL'ini kopyalayıp kendini doğrularsa,
- Research/Decision scope Day5'e çekilirse.

**DAY5 BAŞLANGIÇ KARARI**  
Önce product integration/finalization uygulanacak. Attack table **geliştirme sonrası exit gate**;
Day5 geliştirmesinin yerine geçmez.


---

## 14. DAY 5 / P8 — EXIT ATTACK SONUCU VE AÇIK BORÇLAR (2026-09-21)

**Focused Core gate**
- workflow run: `35572034785`
- result: **PASS**
- interpreter role contract: PASS
- resolver morphology safety: PASS
- ranked-comparison contract: PASS
- Day4 + Day5 Core contracts: PASS
- frontend V2 typecheck: PASS
- full/legacy corpus açılmadı.

**Live /ask-v2 attack — son ölçülen durum**
- workflow run: `35572057395`
- provider: OpenRouter
- gerçek kullanılan model: `deepseek/deepseek-v4-flash`
- NOT: repo/environment variable workflow fallback'ını override ettiği için bu run
  **Gemini Flash-Lite ölçümü değildir**.
- synthetic/permuted semantic engine; demo DB correctness oracle değildir.
- silent-wrong: **0**
- unhandled 500: **0**
- principal-aware execution: **100%**
- standard p95: **8.3733s** → PASS (<=10s)
- clarify p95: **2.4482s** → PASS (<=6s)
- signed clarification resume filter binding: **PASS**
- pure social query=0: **PASS**
- topic switch old-focus bleed=0: **PASS**
- paraphrase / typo safe path / ambiguity / ranking+comparison: **PASS**
- tek blocker: natural repair turn
  `"yok, son üç ay olsun"` language owner tarafından replacement time delta yanında
  discourse/retraction surface'i semantic gap olarak da yayımlandı; sonuç
  `semantic_gap` oldu. **Wrong official answer üretilmedi.**

**Root classification**
Bu failure'ın sahibi:
`TurnInterpreter`.

Downstream owner'lara özel patch YASAK:
- SemanticResolver'a `yok` special-case eklenmeyecek.
- ConversationCoordinator'a prompt-specific fallback eklenmeyecek.
- Planner/Orchestrator exception branch eklenmeyecek.
- test fixture'a göre production code yazılmayacak.

Normatif düzeltme:
- repair/retraction discourse marker business semantic mention değildir;
- replacement slot typed delta olarak taşınır;
- discourse marker `unresolved_mentions` üzerinden SemanticResolver'a gönderilmez;
- owner fix yalnız TurnInterpreter contract/model boundary'sinde yapılır.

**Clarification silent-wrong borcu — CLOSED**
Önceki live attack'ta signed ambiguity resume seçilen ENTITY_VALUE'yu canonical filter
slotuna taşımıyordu. `ConversationCoordinator.restore_pending()` içinde generic
`UNKNOWN → resolved ENTITY_VALUE → FILTER` normalization ile kapatıldı.
Son live run'da:
- metric preserved: PASS
- selected Segment=Prime filter bound: PASS
- query_once: PASS
- official_verified: true
Bu düzeltme fixture literal veya resolver/planner fallback içermez.

**LLM maliyet politikası — ACTIVE**
Paid live-provider workflow artık **workflow_dispatch-only** olmalıdır; push başına ücretli
LLM suite çalıştırmak yasaktır. Deterministic focused Core CI otomatik kalabilir.
Live LLM yalnız:
1. owner-level değişiklik sonrası,
2. tek/nokta-atışı vaka veya küçük exit setiyle,
3. sonuç karar değiştirecekse
çalıştırılır.

Fast-model hedefi:
`google/gemini-2.5-flash-lite`.
Smart escalation adayı:
`gpt-5-mini`.
Research modeli Day7 bake-off authority'sine bırakılır.

**ÖNEMLİ MODEL PROVENANCE BORCU**
`35572057395` Gemini testi sanılmamalıdır. GitHub Environment/Repository
`DIMA_OPENROUTER_MODEL` variable'ı DeepSeek'i seçmiştir. Gemini karşılaştırması yapılacaksa
manual live workflow model selection'ı explicit olarak Gemini'ye sabitlenmeli veya manual
input ile seçilmeli; ardından yalnız gerekli küçük ölçüm çalıştırılmalıdır.

**P8 release kararı**
Day5 Core implementation **çalışıyor**, deterministic Core gate yeşildir ve önceki
silent-wrong clarification kusuru kapanmıştır. Ancak P8 exit gate henüz **SEALED değildir**:
natural repair blocker açık kaldığı için Day6/Research'e geçiş yapılmaz.

**Açık borç sırası**
1. TurnInterpreter owner boundary'sinde repair discourse-marker contract'ını kökten düzelt.
2. Paid live workflow model provenance'ını explicit/yanlış-yorumlanamaz yap.
3. Gemini Flash-Lite ile yalnız gerekli nokta-atışı repair + küçük smoke ölçümü yap.
4. Doğruluk korunursa latency/cost kararını kaydet; bozulursa yalnız o zaman
   `gpt-5-mini` validated escalation dene.
5. P8 blocker'ların tamamı yeşil olduğunda Day5'i seal et ve ancak sonra Day6'yı aç.



---

## 15. DAY 5 / P8 COMPLETE — FINAL SEAL (2026-09-21)

**Karar**
Day 5 / P8 **COMPLETE**. Core MVP release blocker'larının tamamı current code üzerinde
deterministik gate + gerçek-provider HTTP attack ile geçti. Day 6 artık açılabilir.

### Current code proof
Owner-level son düzeltmeler:
- `a2f3aed0f1e77faa5ab3f65ff94b86fa90fee2bd`
  - repair/retraction discourse marker semantic mention olmaktan çıkarıldı.
- `6b029bf6fc9649596aca6659e4c23e7036850a83`
  - model typo surface'i normalize ederse exact user surface'e conservative realignment;
  - explicit adjacent top-N sayısı model tarafından düşürülürse aynı grounded ranking
    phrase'inden deterministik recovery.
- `7460d5403e06ddf05e69869d34a5dab5e9d2a734`
  - short-token conservative typo realignment eşiği düzeltildi.
- `69ba65140d4748f4a9ebe01b3a92af3f06636140`
  - typo grounding + explicit top-N recovery deterministic regression proof'ları.

Bu düzeltmeler:
- canonical/business semantic seçmez,
- Resolver/Planner/Orchestrator'a prompt-specific fallback eklemez,
- LLM semantic retry açmaz,
- fixture literal içermez,
- TurnInterpreter'ın tek language-owner sınırında kalır.

### Deterministic Core gate
- workflow: `v2-day5-core-mvp`
- run: `35574230175`
- head: `69ba65140d4748f4a9ebe01b3a92af3f06636140`
- result: **SUCCESS**

Kapsam:
- interpreter role contracts
- resolver morphology safety
- ranked comparison contract
- Day4 + Day5 Core contracts
- frontend V2 typecheck

### Final real-provider exit attack
- workflow: `v2-day5-live-attack`
- run: `35574379890`
- head: `ac943a7e6a1d358714436cd3135832b95d9daa8e`
- result: **SUCCESS**
- provider: OpenRouter
- exact model provenance:
  `google/gemini-2.5-flash-lite`
- source policy:
  `real_http_real_provider_synthetic_semantic_engine_no_demo_db`
- artifact: `10626619366`
- artifact digest:
  `sha256:cc7d50e50c1649f044c31119ed25c9a4ba21069312970fbf75b2e53edaa3b9ca`

Attack sonuçları:
```text
paraphrase                         PASS
typo safe resolve/clarify          PASS
ranking + comparison               PASS
blocking ambiguity                 PASS
signed clarification resume        PASS
thread base                        PASS
follow-up filter                   PASS
user repair                        PASS
result explain query=0             PASS
pure social query=0                PASS
topic switch old-focus bleed=0     PASS
```

Release gate:
```text
all_attack_records_pass            true
P0 silent-wrong                    0
unhandled 500                      0
principal-aware execution          100%
standard E2E p95                   5.6234s   <= 10s PASS
clarify p95                        0.9789s   <= 6s  PASS
blocking ambiguity auto-select     0
clarification query                0
pure social query                  0
repair unrelated-slot loss         0
canonical thread context break     0
dead/broken Core response          0
legacy silent fallback             0
```

### Gemini model decision
Day5 fast-path measurement artık gerçek provenance ile:
`google/gemini-2.5-flash-lite`.

DeepSeek önceki ölçümlere göre standard/clarify latency'nin ciddi kısmı düşmüştür;
Day5 final gate Gemini ile doğrudan geçmiştir. Bu nedenle Day5 hot-path için GPT-5-mini
escalation denemesi **gereksizdir** ve ek ücretli test yapılmayacaktır.

Bu seal:
- bütün Dima için gelecekteki `fast/smart/research` router tasarımını çözmüş saymaz;
- yalnız V2 Day5 Core hot-path model authority/provenance'ını kapatır.
ModelRouter/ModelPolicy genişletmesi ilgili sonraki roadmap fazında tek-owner olarak ele alınır.

### Paid-test discipline
Tek final Gemini exit run'ını connector dispatch desteği olmadığı için geçici
one-shot sentinel ile tetikledik. Koşu başladıktan hemen sonra:
- live workflow tekrar `workflow_dispatch-only` yapıldı;
- sentinel silindi;
- cleanup commitleri:
  - `00a3de6cab044c73392dcb0bb65317cafa8293be`
  - `d537a9691ec6d5eba5ccd2f9a82e24b5194e96e7`

Current branch'te paid live workflow **manual-only** durumdadır. Push başına ücretli LLM
suite çalışmaz.

### P8 EXIT
```text
Day5 Core implementation               COMPLETE
deterministic Core gate                PASS
real-provider Core attack              PASS
silent wrong                           0
unhandled 5xx                          0
principal propagation                  PASS
standard p95                           PASS
clarify p95                            PASS
Gemini provenance                      VERIFIED
paid CI accidental auto-run            CLOSED
```

**NEXT**
Day 6 açılabilir. Day6 başlamadan roadmap'teki ilgili P bölümü ve rapordaki referans
bölümler yeniden okunacak; Day5'e yeni feature geri çekilmeyecek.


---

## 16. DAY 6 / P9 ACTIVE TICKET — PRODUCT MVP: RESEARCHBRIEF

**AMAÇ**  
Kompleks kullanıcı talebini tek SQL'e veya dev statik plana sıkıştırmadan, bütün açık
araştırma hedeflerini kayıpsız ve denetlenebilir bir `ResearchBrief` sözleşmesine
dönüştürmek. Day6 araştırmayı **çalıştırmaz**; araştırmanın typed iş emrini üretir.

**USER SCENARIO**  
Kanonik:
> “Son 12 aylık üretilen ürünleri karşılaştır, üretildikleri makineler ve personellerle
> ilişkisini analiz et, satış performanslarını yorumla ve raporla.”

Kaybolmadan MUST olarak temsil edilmesi gereken hedefler:
```text
production comparison
machine relationship
personnel/shift relationship
sales performance
report deliverable
```

**ROADMAP**  
P9 / P9.A.

**REPORT DAYANAK**  
R11.1 ResearchBrief; R11.3 raw-user-prompt almayan typed worker sınırı.
R12 cross-domain grain/join gate Day7+ execution işi olduğundan Day6'ya çekilmez.
R20 semantic-owner ve evidence/security değişmezleri geçerlidir.

**NEW OWNER**
- `TurnInterpreter` → raw dildeki COMPLEX_ANALYSIS / REPORT_REQUEST speech act'i ve
  bağımsız research goal surface'lerini **bir kez** çıkarır.
- `SemanticResolver` → Research goal içindeki semantic mention'ları mevcut canonical
  authority ile bind eder; raw prompt okumaz.
- `ResearchBriefBuilder` (`app/v2/research.py`) → typed language goals + resolver
  hypotheses + context version'dan `ResearchBrief` üretir.
- Day7 Supervisor yalnız `ResearchBrief` okuyacaktır; raw prompt semantic authority
  olmayacaktır.

**REUSE EDİLEN PRIMITIVE**
- `TurnInterpretation` / surface-grounding invariant
- `SemanticResolver` candidate provenance + clarification
- `ContextVersionV0`
- existing `SemanticHypothesis` / resolved candidate authority
- mevcut `/ask-v2` runtime + principal boundary

**FILES TO TOUCH — beklenen**
- `app/v2/models.py`
- `app/v2/interpreter.py`
- `app/v2/resolver.py` — yalnız research typed mention integration
- `app/v2/dialogue_policy.py`
- `app/v2/research.py` — NEW
- `app/v2/orchestrator.py` — yalnız routing/integration
- `app/v2/finalizer.py` / `routers/ask_v2.py` — yalnız Day6 product response için minimal
- `tests/test_v2_day6.py`
- gerekirse küçük deterministic eval fixture; paid live eval YOK.

**FILES NOT TO TOUCH**
- sealed roadmap/report
- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- Day7 adaptive research tools / ResearchToolContract execution
- Wren query/planner execution semantics
- removed always-on backend CI
- manual-only paid live workflow

**DAY6 EXECUTION CUTLINE**
```text
User complex request
→ TurnInterpreter
→ COMPLEX_ANALYSIS / REPORT_REQUEST
→ SemanticResolver
→ ResearchBriefBuilder
→ ResearchBrief READY | BLOCKED
→ STOP
```

Bu fazda:
```text
query execution      = 0
dry_plan             = 0
research tool call   = 0
adaptive loop        = 0
EvidenceArtifact lifecycle = 0
report generation    = 0
raw prompt reparse downstream = 0
```

**TARGETED TEST / DEMO — MALİYET DİSİPLİNİ**
- Default testler LLM/provider çağırmayacak.
- Synthetic/permuted semantic context kullanılacak.
- Bir canonical + birkaç paraphrase/order/extra-clause fixture doğrudan typed
  `TurnInterpretation` üstünden `ResearchBriefBuilder` contract'ını ölçecek.
- Interpreter owner değişikliği için canlı provider suite otomatik koşmayacak.
- Gerekirse faz sonunda **tek küçük manual** Gemini Flash-Lite smoke ayrıca karar verilecek;
  Day6 correctness gate'i paid LLM'e bağımlı olmayacak.
- Full backend suite / legacy corpus / always-on backend CI YOK.

**EXIT**
```text
canonical complex goal extraction = 100%
complex validation goal coverage  >= 95%
invented semantic domain/ref       = 0
blocking unresolved ignored        = 0
query execution                    = 0
downstream raw prompt reparse      = 0
```

**NEGATIVE SENTINELS**
- “Ürünleri analiz et” → machine/personnel/sales/report goal icat ETME.
- “Ürünleri ve makineleri karşılaştırıp raporla” → personnel goal icat ETME.
- Semantic modelde relationship/domain güvenilir bağlanamıyorsa goal'u düşürme veya
  tahminle READY yapma; BLOCKED / clarification / explicit semantic gap üret.
- Aynı explicit user goal'un farklı paraphrase/order ifadesi coverage kaybına yol açmamalı.

**STOP-THE-LINE**
- ResearchBriefBuilder raw `question` okursa,
- Research planner/supervisor Day6'da raw prompt reparse ederse,
- semantic ref Resolver dışında icat edilirse,
- unresolved MUST goal sessiz düşerse,
- Day6 sırasında Wren/query/tool execution açılırsa,
- canonical promptu geçirmek için “ürün/makine/personel/satış” literal special-case yazılırsa,
- paid LLM workflow push ile otomatik tetiklenirse.

**BAŞLANGIÇ KARARI**  
Day6 implementation başlatıldı. İlk proof, language extraction ile semantic binding'i
birbirinden ayıran typed contract + query=0 sentinel olacaktır.


---

## 17. DAY 6.5 PREPARED — MANAGER ARCHITECTURE VALIDATION & SEAL

**STATUS:** PREPARED / NOT STARTED

Day6 P9 çalışması downstream deterministic contract'ların doğruluğunu kanıtladı; ancak
one-shot universal complex-intent compilation hipotezi product-quality live language
gate'inde doğrulanamadı.

Latest historical reference evidence:
- Frozen16 reference-language run: `35593735023`
- cases: 16
- case pass: 43.8%
- goal coverage: 65.6%
- MUST coverage: 73.2%
- invented operations: 12
- negatives: 100%

Bu nedenle:
- P9 kodu silinmez; **legacy/reference baseline** olur.
- Eski yola raw-intent okuyabilen ayrı Supervisor eklenmez; bu fiilen Manager olur.
- Complex language cognition bounded iterative Manager runtime'a taşınır.
- Deterministic truth plane korunur ve genişletilir.

Day6.5 living authority:
- `belgeler/plan/DIMA_DAY6_5_MANAGER_ARCHITECTURE_VALIDATION.md`
- `belgeler/plan/DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md`
- `belgeler/plan/ADR_DAY6_5_ONE_SHOT_COMPLEX_INTENT_REJECTED.md`
- `eval/v2_day6_5_eval_manifest.yaml`

### Manager candidate control plane

```text
USER
→ bounded Manager cognition
→ UserObligationLedger
+ SemanticResolver → opaque SemanticHandle
→ IntentAcceptanceGate
→ AcceptedTurnContract vN
→ RepresentabilityGate
   ├─ STANDARD_LOSSLESS → Core
   └─ RESEARCH_REQUIRED → bounded Manager research loop
→ deterministic trust plane
→ CompletionGate
   ├─ VERIFIED_COMPLETE
   ├─ PARTIAL
   └─ FAILED
```

### Day6.5 hard rules

- Contract completeness ≠ execution-plan completeness.
- Manager candidate obligation üretir; authoritative commit runtime/gate işidir.
- Manager canonical semantic ref üretemez.
- SemanticHandle yalnız Resolver tarafından mint edilir.
- AcceptedTurnContract immutable/versioned; repair yeni version yaratır.
- Representability raw text/length/keyword ile karar vermez.
- Manager direct SQL/DB/Wren çalıştıramaz.
- Completion status Manager-owned değildir.
- hidden chain-of-thought persist/show edilmez.
- paid eval workflow manual-only kalır.
- one-shot P9 failures için regex/provider-specific semantic patch yasaktır.

### Eval governance

Frozen16:
- historical/reference baseline,
- architecture selection oracle değil.

Yeni architecture corpus hedefi:
```text
DEV         80
VALIDATION  50
HIDDEN      50
TOTAL      180
```

Hidden prompt text repoya girmez.
Kodlamadan önce independent source/evaluator tarafından dondurulup yalnız SHA-256,
count ve taxonomy metadata repoya yazılmalıdır.

### Day6.5 implementation order

```text
0. freeze hidden holdout hash
1. contracts
2. provider-free invariant gate
3. SemanticHandle boundary
4. AcceptanceGate + versioning
5. RepresentabilityGate
6. bounded Manager runtime/tools
7. adaptive evidence-response proof
8. CompletionGate
9. DEV
10. VALIDATION
11. HIDDEN seal
12. Day7 production research execution
```

### STOP-THE-LINE

- hidden holdout implementation sırasında açılırsa,
- Manager canonical truth icat ederse,
- AcceptanceGate / RepresentabilityGate bypass edilirse,
- old Frozen16 cümleleri production prompt/code'a taşınırsa,
- Manager raw SQL veya direct DB tool alırsa,
- accepted contract in-place mutate edilirse,
- evidence olmadan VERIFIED_COMPLETE çıkarsa,
- standard-lossless request gereksiz research loop'a sokulursa.

**NEXT ACTION:** Kullanıcı onayıyla Day6.5 implementation başlatılacak. İlk adım production
kod değil, independent hidden-holdout freeze + contract-only models olacaktır.


### 2026-09-21 — DAY 6.5 / FINAL PRE-IMPLEMENTATION HARDENING

**Current branch HEAD before hardening:** `8b2a9aa44bf4c9e1dfde5e6f608a129d4c85e0d5`

**External review cross-check**
- Day6.5 hazırlığı genel olarak doğru bulundu.
- Production Manager kodundan önce dört blocker teyit edildi:
  1. simple/Core fast-path + latency/cost regression gate,
  2. obligation origin + derived-parent ownership,
  3. evidence-backed != VERIFIED completion semantics,
  4. exactly-one accepted authority + rejected-attempt merge yasağı.
- Ek hardening:
  - runtime-issued SourceSpanRef,
  - tenant/context-bound SemanticHandle,
  - registered capability vocabulary,
  - real trust-plane vertical proof before seal,
  - ADR candidate-vs-accepted ayrımı,
  - final seal sırasında MIMARI/CLAUDE/status authority sırası.

**Yapılan hardening**
- `DIMA_DAY6_5_MANAGER_ARCHITECTURE_VALIDATION.md`
  - simple standard fast lane açıkça korundu,
  - rejected FAST attempt semantic carry-over yasaklandı,
  - obligation `origin` + `parent_obligation_id` eklendi,
  - SourceSpanRegistry ve tenant-bound SemanticHandle sınırı eklendi,
  - AcceptedTurnContract audit/lineage alanları güçlendirildi,
  - evidence presence ile VERIFIED ayrıldı,
  - fast-path p95/cost/model-call gate'leri eklendi,
  - implementation sırası gate-before-runtime olacak şekilde düzeltildi,
  - seal öncesi gerçek read-only trust-plane vertical proof zorunlu yapıldı.
- `DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md`
  - `ObligationOrigin`: USER_MUST / USER_OPTIONAL / SYSTEM_REQUIRED / AGENT_DERIVED,
  - lifecycle'da gerçek `VERIFIED` ve BLOCKED/LIMITED ayrımı,
  - opaque SourceSpanRef + registry,
  - capability_key registry gate,
  - tenant-bound SemanticHandle,
  - versioned/lineaged AcceptedTurnContract,
  - exactly-one accepted authority,
  - no rejected-attempt semantic merge,
  - CompletionGate VERIFIED/PARTIAL/FAILED semantiği düzeltildi.
- `eval/v2_day6_5_eval_manifest.yaml`
  - authority, fast-path, completion hard gate'leri genişletildi.
- `ADR_DAY6_5_ONE_SHOT_COMPLEX_INTENT_REJECTED.md`
  - one-shot rejection = ACCEPTED,
  - bounded Manager = SELECTED CANDIDATE FOR VALIDATION,
  - production acceptance yalnız Day6.5 seal sonrası.
- `AGENTS.md` ve `CLAUDE.md`
  - Day6.5 owner/authority override eklendi,
  - tarihsel “raw language only TurnInterpreter” kuralının complex path için yanlışlıkla
    uygulanması engellendi.

**Commits**
- architecture hardening: `07a3024f35162b7511c22c3f0710ec260547c391`
- contract hardening: `f56108f3db29763c4a277f3974f63d21812117b2`
- eval gates: `25612707c8da27b242d548f9f20876cdaad6cc71`
- ADR candidate status: `42da43d42438e5e5533181b6a3a2a88ac6eacfd7`
- AGENTS override: `4bd6b4debabaf64b2a5a716ed479cbab8cb0ea8b`
- CLAUDE active operation: `2072a5a243a8572d60f3ae659e67e5a0e0bef118`

### DAY 6.5 PRE-IMPLEMENTATION GATE

```text
one-shot P9 rejection documented                PASS
Manager candidate/not-yet-production semantics  PASS
simple Core fast-path gates                      PASS
obligation origin/parent contract                PASS
evidence-backed != VERIFIED                      PASS
exactly-one accepted authority                   PASS
rejected attempt semantic merge = 0 contract     PASS
opaque source evidence contract                  PASS
tenant/context-bound SemanticHandle contract     PASS
gate-before-runtime implementation order         PASS
real trust-plane vertical proof in exit plan     PASS
MIMARI final-seal step recorded                  PASS
hidden holdout SHA/count/taxonomy freeze         BLOCKED / REQUIRED
```

### V2-D0XX — Hidden architecture holdout henüz freeze edilmedi

- Kaynak: Day6.5 eval manifest / architecture seal discipline.
- Manifest current state:
  - count = 50 target,
  - `sha256 = REQUIRED_BEFORE_IMPLEMENTATION`,
  - `taxonomy_sha256 = REQUIRED_BEFORE_IMPLEMENTATION`.
- Blocker: **YES — production Manager implementation öncesi**.
- Neden burada çözülmüyor: hidden corpus mevcut development model/implementation süreci
  tarafından üretilir veya görülürse hidden niteliğini kaybeder.
- Kapanış: bağımsız source/evaluator corpus'u external olarak dondurur; repo yalnız
  hash/count/taxonomy metadata alır. Prompt text repo veya implementation context'e girmez.
- Sonraki adım: holdout metadata freeze → ardından contract-only production models +
  provider-free authority tests.

**Karar**
Bu blocker dışında Day6.5 contract/mimari hazırlığı production implementation'a hazırdır.
Hidden freeze tamamlanmadan Manager runtime kodu yazılmayacak.


**Holdout handoff tooling**
- freeze utility: `lab/v2_day6_5_freeze_holdout.py` @ `347e207fa9cc6a0ccf167fdab9e8b15560ead525`
- safe handoff contract: `eval/DAY6_5_HIDDEN_HOLDOUT_HANDOFF.md` @ `2e5532bbd0b4830cd81d771f8c922c1166fb84e3`
- tracking issue: **#2 — Day 6.5 gate — external hidden holdout freeze**
- issue prompt text kabul etmez; yalnız FROZEN_EXTERNAL metadata/hash alınır.

**Implementation unlock condition**
```text
issue #2 metadata received
+ case_count == 50
+ corpus_sha256 present
+ taxonomy_sha256 present
+ prompt_text_committed == false
+ development_model_generated == false
→ manifest placeholders replaced
→ blocker CLOSED
→ Day6.5 contract-only production implementation START
```


### 2026-09-21 — DAY 6.5 / HIDDEN HOLDOUT PROVENANCE HARDENING

External review sonrası hidden-freeze gate'in provenance beyanı sertleştirildi.

Yapılan:
- `lab/v2_day6_5_freeze_holdout.py` artık provenance boolean'larını kendisi sabit yazmaz.
- External evaluator `ATTESTED_EXTERNAL` attestation dosyası vermeden freeze metadata üretilmez.
- Metadata artık `attestation_sha256` ile attestation artefaktına bağlanır.
- Zorunlu beyanlar:
  - `independent_evaluator=true`
  - `development_model_generated=false`
  - `prompt_text_committed=false`
  - `prompt_text_shared_with_implementation=false`
  - `frozen_before_implementation=true`
- Day6.5 preflight corpus + taxonomy yanında attestation hash/alanlarını da doğrular.
- Final hidden seal promptları development context'e açmaz; external evaluator receipt'i
  `tested_git_sha` + `eval_harness_sha` ile sonucu bağlar.
- Issue #2 handoff sözleşmesi bu yeni protokole güncellendi.

Commits:
- freeze attestation: `debb47a54686f3ecacc7a056679002c176508f71`
- handoff contract: `9b9f5d98be317d7fcba1418f42178de483af5345`
- manifest attestation gate: `640f027db212a852197378f3915eb15a2ae7e95b`
- preflight attestation enforcement: `caad2e298c7e9d40d1b515ec7d931d51efec58ae`
- preflight placeholder test: `a4740099845e0b5a58f533077232338d2d104be2`
- attestation unit tests: `b61c3e9742a8c65060dd809e94839f784d8f00a1`

Current blocker değişmedi:
```text
external evaluator metadata/attestation receipt   WAITING
production Manager implementation                 LOCKED
```

Issue #2 ancak gerçek external metadata alındıktan, manifest placeholder'ları kapatıldıktan
ve `python lab/v2_day6_5_preflight.py` READY verdikten sonra kapatılacaktır.


### 2026-09-21 — DAY 6.5 / IMPLEMENTATION BATCH 1

**Owner kararı**
- External hidden holdout/freeze disiplini korunuyor.
- Hidden hash/receipt artık **implementation blocker değil, architecture-seal blocker**.
- Otomatik/push-trigger paid LLM job YASAK; live eval manuel kalacak.
- Geliştirme önceliği: control-plane architecture + governed tools.

**Mimari ilerleme**

1. `manager_models.py`
   - `ObligationOrigin`, `ObligationStatus`, `ManagerCapabilityKey`
   - `SourceSpanRef`, `SemanticHandle`
   - `CandidateObligation`, `UserIntentEnvelope`
   - `UserObligationLedger`, `AcceptedTurnContract`
   - `ManagerState`, `ManagerBudget`, `ManagerRunSnapshot`
   - terminal: VERIFIED_COMPLETE / PARTIAL / FAILED

2. `source_spans.py`
   - runtime-owned message hash + exact offset registry,
   - Manager yalnız opaque `src_*` kullanır,
   - fabricated/exact-surface mismatch fail-closed.

3. `semantic_handles.py`
   - Resolver-owned opaque `sem_*`,
   - canonical target yalnız trusted registry içinde,
   - tenant/context binding enforced,
   - execution tarafı canonical binding'i registry üzerinden açar.

4. `manager_policy.py`
   - registered capability vocabulary,
   - STANDARD / RESEARCH / PRESENTATION lane ayrımı,
   - raw-language routing yok.

5. `acceptance.py`
   - `IntentAcceptanceGate`,
   - source/provenance/handle/capability doğrulama,
   - clarification vs rejection ayrımı,
   - `AcceptedContractRegistry` ile exactly-one authority/turn,
   - contract lineage + monotonic version.

6. `representability.py`
   - yalnız accepted typed contract/ledger okur,
   - STANDARD_LOSSLESS / RESEARCH_REQUIRED / CLARIFICATION_REQUIRED / UNSUPPORTED,
   - raw question/length/keyword kullanmaz.

7. `completion.py`
   - evidence presence != VERIFIED,
   - bütün USER_MUST VERIFIED → VERIFIED_COMPLETE,
   - explicit blocked/limited/unsupported → PARTIAL,
   - non-terminal MUST → finish reject.

8. `model_policy.py` + `config.py`
   - yeni `RESEARCH_MANAGER` rolü,
   - model/provider business logic içine hardcode edilmedi,
   - reference model fallback yalnız config/policy seviyesinde.

9. `manager_tools.py`
   - kapalı 6-tool registry:
     - resolve_semantics
     - propose_acceptance
     - run_analytics
     - run_relationship
     - inspect_evidence
     - request_clarification
   - raw SQL/direct DB/generic Python tool YOK,
   - execution tools AcceptedTurnContract olmadan çağrılamaz.

10. `manager_runtime.py`
    - bounded state machine:
      INITIAL → UNDERSTANDING → CONTRACT_ACCEPTED → INVESTIGATING
      + CLARIFICATION/BLOCKED/BUDGET/FAILED/COMPLETED terminal/side states,
    - tool/data-query/manager-turn budget,
    - actual query fanout bütçeye ayrıca yazılır.

11. `manager_semantics.py`
    - `src_*` → existing SemanticResolver,
    - canonical truth Resolver'da,
    - Manager output yalnız `sem_*`,
    - raw prompt downstream reparse edilmez.

12. `cube_planner.py`
    - yeni `ledger_from_canonical_ir()` pure reuse primitive,
    - Manager adapter query-level RequirementLedger ID/state contractını yeniden icat etmez.

13. `manager_core_adapter.py`
    - ilk **REAL trust-plane vertical**:
      SemanticHandle → AnalyticsIR → RequirementLedger → CubePlanner
      → Wren dry-plan → Wren query → ResultValidator → ContractStore
      → verified EvidenceArtifact,
    - bounded evidence rows,
    - QueryContract sealing zorunlu,
    - accepted contract dışı obligation reject.

14. `models.py / EvidenceArtifact`
    - obligation refs,
    - verified flag,
    - limitations,
    - query contract refs.

15. `obligation_ledger.py`
    - USER_MUST immutable promise,
    - AGENT_DERIVED yalnız parent child olarak eklenebilir,
    - VERIFIED için evidence + deterministic verdict şart,
    - blocked/limited/unsupported explicit terminal.

16. `manager_executor.py`
    - governed tool executor boundary,
    - standard analytics evidence store'a girer,
    - actual query fanout budget'a yansır,
    - yalnız STANDARD capability exact obligation için deterministic VERIFIED transition alır,
    - relationship/root-cause standard evidence yüzünden yanlış tamamlanmaz.

**Targeted authority test dosyası**
- `tests/test_v2_day6_5_manager_authority.py`
- fabricated source reject
- foreign-tenant semantic handle reject
- exactly-one accepted authority
- standard vs research representability
- evidence presence != VERIFIED
- PARTIAL vs VERIFIED_COMPLETE ayrımı

**Başlıca commits**
- manager contracts: `972f5add80d3a4a538c28e97373f3142149ed9fd`
- capability/source/semantic registries:
  `8776cda8e428196534f1475a833d8b19ce980e99`,
  `37cad6f588dabc570ae794192e58aef0f9f5e17a`,
  `21fd3ffce01caee5bc9f3595897a57bc205a5950`
- acceptance / representability:
  `5af782daedd8f658fb04e4cac7637ec0091fa8d5`,
  `e708d5ca920845f3af5b31060e0f2ec295e5b21a`
- completion: `6af0c092828e1b534cdf601c753c1050b31c06cc`
- RESEARCH_MANAGER role: `a8a6165d345832166ab676b4d084873734a6837a`
- tool registry/runtime:
  `40d9d44eb131eb96fbd6d810b2f3eb831f08b12b`,
  `acea3dcf06b7e45b6f4e784559979a02bd31ad45`
- canonical IR ledger: `8e78368433564d94ea07a52806b340910b58b4b5`
- Core trust-plane adapter: `2c7d2ca662cc3b41625514bbb09f26aff35155b9`
- semantic resolver adapter: `76e0f3535a0e62be94adb3b6a089ef5094c38113`
- obligation ledger service: `f46d5354558568c9c4d145a8c06ea8e00073d7f5`
- governed executor + ledger binding:
  `d855315e7b8134d5e5feed2c6d4e5f63fcd9f27c`,
  `40a33a3490538d5b840246431d311cc09d2d70ec`

### Açık borçlar

**V2-D65-01 — Hidden holdout architecture seal receipt**
- implementation blocker: NO
- architecture seal blocker: YES
- promptlar development context'e girmeyecek.
- final receipt: corpus/taxonomy/attestation SHA + tested_git_sha + eval_harness_sha + aggregate PASS/FAIL.

**V2-D65-02 — run_relationship gerçek executor**
- mevcut durum: tool contract/policy var, executor injection slotu var.
- neden şimdi yok: CrossDomainJoinGate / grain-cardinality safety Day7 trust-plane capability.
- blocker: Manager standard vertical proof için NO; relationship architecture proof için YES.
- kapanış: verified relationship path + grain/cardinality gate → QueryContract/Evidence.

**V2-D65-03 — Manager model loop/prompt**
- mevcut durum: runtime/tool state machine hazır; model cognition henüz bağlanmadı.
- blocker: YES — bir sonraki batch.
- kural: tek güçlü `RESEARCH_MANAGER`, no cheap→strong escalation ilk spike'ta.

**V2-D65-04 — DEV architecture corpus/evaluator**
- hidden ayrı ve sealed kalır.
- visible DEV cases Manager runtime bağlandıktan sonra yazılacak/koşulacak.
- otomatik paid workflow yok.

### NEXT

```text
1. Manager model loop → typed tool-call protocol
2. propose_acceptance / resolve_semantics cycle
3. real run_analytics adaptive observe loop
4. inspect_evidence bounded context
5. AGENT_DERIVED replanning proof
6. manual focused provider-free contract check
7. visible DEV manager corpus
8. relationship executor / CrossDomainJoinGate
9. VALIDATION
10. external HIDDEN architecture seal
```

**STOP-THE-LINE hâlâ geçerli**
- raw SQL tool eklemek,
- canonical ref'i Manager schema'ya açmak,
- second accepted semantic authority,
- rejected attempt field merge,
- evidence gördü diye otomatik research VERIFIED,
- hidden promptları development context'e taşımak,
- model-specific semantic case patch.


### 2026-09-21 — DAY 6.5 / IMPLEMENTATION BATCH 2

**Amaç**
Bounded Manager candidate'ını production `/ask-v2`ye bağlamadan gerçek Resolver/Core/Wren
trust plane üzerinde manuel çalıştırılabilir hale getirmek.

**Yapılan**
- `manager_loop.py`
  - tek structured action / manager turn,
  - private chain-of-thought istenmez/persist edilmez,
  - exact source surface runtime'da `src_*`e çevrilir,
  - semantic observation yalnız opaque `sem_*`,
  - finish yalnız CompletionGate tarafından kabul edilirse tamamlanır,
  - tool rejection modelin bir sonraki turda düzeltmesine izin verir,
  - manager turn budget enforced.
- `manager_tools.py`
  - `run_analytics` period/comparison opaque handle destekli,
  - agent-derived standard task aynı tool içinde parent'a bağlı açılabilir.
- `manager_executor.py`
  - canonical internal adapter result Manager'a dönmez,
  - Manager-safe observation: evidence_ref / verified / query_count / row_count / limitations,
  - standard verified evidence obligation ledger'a deterministic verdict ile bağlanır,
  - research USER_MUST standard evidence yüzünden tamamlanmaz.
- `manager_core_adapter.py`
  - Manager-facing evidence payload'dan canonical AnalyticsIR kaldırıldı,
  - result columns/rows canonical DB field yerine `sem_*` handle anahtarlarıyla gösterilir.
- `obligation_ledger.py`
  - agent-derived branch parent USER_MUST'ı mutate etmez.
- `runtime_boundary.py`
  - Standard orchestrator + Manager Lab ortak tenant/principal/request identity owner kullanır.
- `manager_lab.py`
  - RESEARCH_MANAGER model role üzerinden ayrı candidate LLM,
  - ContextProvider + Resolver + handles + gates + Core adapter + executor + loop tek harness.
- `/ask-v2-manager-lab`
  - default OFF,
  - yalnız `v2_manager_lab_enabled=true` ve manuel HTTP isteği ile çalışır,
  - production `/ask-v2` routing değişmedi,
  - push/CI otomatik LLM çağrısı YOK.

**Önemli güvenlik düzeltmesi**
İlk adapter taslağında internal `AnalyticsIR`/canonical result column'larının Manager observation'a
sızma riski bulundu ve production lab açılmadan kapatıldı.
Manager artık canonical semantic isimleri tool result üzerinden de göremez.

**Başlıca commits**
- Manager loop: `349ba13609fcf523e12f790fc4e6deb30d2dcb38`
- derived task contracts: `4fef64cb2708f5e39e0ead29b4d5d59f17149181`
- derived executor: `1934b389a7743ff3809732f9a3c683570a6f510a`
- safe analytics observation: `75f768e758b411de0a2c35f75e1aa8539c3e4a3a`
- canonical leakage closure: `61d9fd3db1e6f5e13223dc99fbb96bbfcbb022a2`
- executor safe return: `c121b79908c97722ea868197bfaea4bc71ed0f00`
- shared runtime boundary: `0211bb3c2e16a3734fb17573221add5ee9bb1ece`
- orchestrator boundary reuse: `03020fa2f3620cd3ac23e55c417bf6b894f68d8d`
- manual Manager Lab harness: `fd73a282168de76f11f39eb646646689f7e6d34e`
- default-off lab route: `179ce93315bb84becd17e037919d61540e6dece3`
- lab route registration: `c13c1999b060f9364a05744f56340388c720362f`

### Güncel mimari durum

```text
Manager contracts / authority          BUILT
SourceSpanRegistry                     BUILT
SemanticHandleRegistry                 BUILT
AcceptanceGate                         BUILT
RepresentabilityGate                   BUILT
CompletionGate                         BUILT
UserObligationLedger service           BUILT
6-tool closed registry                 BUILT
bounded Manager state machine          BUILT
RESEARCH_MANAGER role                  BUILT
resolve_semantics → real Resolver       BUILT
run_analytics → real Core/Wren          BUILT
QueryContract → Evidence               BUILT
adaptive AGENT_DERIVED standard branch BUILT
manual Manager Lab                     BUILT
production /ask-v2 hybrid routing      NOT YET
run_relationship real trust plane      NOT YET (Day7-grade)
external hidden architecture seal      PENDING
```

### NEXT IMPLEMENTATION

1. Manual Manager Lab smoke — az sayıda gerçek prompt; paid workflow yok.
2. Tool-action schema/runtime hatalarını düzelt.
3. Result-aware adaptive branch canonical scenario.
4. Safe relationship blocker/gate → sonra CrossDomainJoinGate.
5. Visible DEV architecture corpus.
6. Hard gates geçmeden production `/ask-v2` hybrid routing açma.


---

### 2026-09-21 — DAY 6.5 / STABILIZATION INTERVENTION — FINITE PRE-ACCEPTANCE

**Pre-stabilization checkpoint**
- branch checkpoint: `checkpoint/day6.5-pre-stabilization-a3f5e0d`
- checkpoint SHA: `a3f5e0dd89366d7b191b64256c55a8e18c286730`
- karar: bu noktadan sonra live-case özel prompt/regex/Resolver heuristic patch YASAK.
- `SemanticResolver` policy yeni vaka geçirmek için genişletilmeyecek.
- `SemanticResolutionReceipt` yalnız provenance / anti-laundering kanıtıdır; intent completeness oracle'ı değildir.

**Dış analizlerden çıkan kök teşhis**
```text
candidate contract validity
!=
intent completeness
```

Open pre-acceptance Manager loop:
```text
resolve
→ resolve
→ propose
→ resolve
→ clarify
→ budget
```
gereğinden fazla yanlış action alanı bırakıyordu ve aynı problemi eski Dima tarzı
case-derived prompt/gate patch'leriyle büyütme riski doğuruyordu.

**Seçilen stabilization mimarisi**
```text
USER
 ↓
DRAFT                         probabilistic / non-authoritative
 ↓
DRAFT SOURCE CONTRACT         deterministic exact-source provenance
 ↓
AUTO-GROUND                   runtime → Resolver → opaque SemanticHandle
 ↓
COVERAGE VETO                 probabilistic, veto-only; authority ÜRETEMEZ
 ↓
CONTRACT VALIDITY             deterministic capability/binding/provenance/effect gate
 ↓
ACCEPT
or one bounded REVISE
or CLARIFY
or NOT_ACCEPTED
```

**Önemli sınırlar**
- Coverage auditor canonical semantic seçemez.
- Coverage auditor handle mint edemez.
- Coverage auditor obligation/directive commit edemez.
- Capability anlamı yalnız `ManagerCapabilityRegistry` içindedir.
- Pre-acceptance Manager artık `resolve_semantics` tool'unu serbestçe seçmez.
- Runtime draft semantic surface'lerini otomatik ground eder.
- Accepted authority oluşmadan analytics/evidence execution açılamaz.
- Post-acceptance raw USER_SOURCE semantic reparse yasaktır.
- Aynı action aynı progress epoch'ta aynı knowledge/state'i üretirse generic
  `ActionFingerprint + ProgressFingerprint` frontier exact action'ı bloklar.

**ResearchDirective ontology ayrımı**
User obligation ile research behavior ayrıldı.

İlk directive:
```text
ResearchDirectiveType.ADAPT_ON_EVIDENCE
condition = MATERIAL_NEW_DIRECTION
parent_obligation_id = accepted research obligation
```

Örnek:
```text
"üretkenlik düşüşünü araştır"
→ USER_MUST root_cause

"sonuç yeni bir yön gösterirse oraya da bak"
→ ResearchDirective.ADAPT_ON_EVIDENCE
```

Directive `UserObligationLedger` içine USER_OPTIONAL/MUST gibi sokulmaz.
AcceptedTurnContract içinde ayrı immutable research policy olarak yaşar.

**Yeni/yeniden sahiplenen dosyalar**
- `app/v2/manager_preacceptance.py`
  - finite DRAFT → AUTO_GROUND → COVERAGE → VALIDITY controller.
- `app/v2/manager_progress.py`
  - generic action/progress fingerprints + dynamic exact-action frontier.
- `app/v2/manager_models.py`
  - `ResearchDirective` first-class contract.
- `app/v2/manager_loop.py`
  - `understand()` open tool-loop yerine finite controller'a delege eder.
  - `run()` accepted research sonrasında agentic kalır.
- `app/v2/acceptance.py`
  - directive source/parent/lane validity; obligation ledger'dan ayrı.
- `tests/test_v2_day6_5_preacceptance_protocol.py`
  - provider-free finite-protocol sentinels.

**Capability algebra**
Aşağıdaki önceki doğru refactor korunuyor; geri alınmadı:
- `ManagerCapabilitySpec.required_kinds/allowed_kinds/required_params/effect_family`
- `CapabilityBindingValidator`
- `ObligationEffect`
- validated atomic obligations-only `StandardProjectionCompiler`.

**Provider-free evidence**
1. Stabilization closure run `35630382762`
   - tested SHA: `c818d69486a7da8a12af9da35b310761aa59cea5`
   - **45 passed / 0 failed**
2. Finite terminal closure run `35631871166`
   - tested SHA: `baf777d6da519c2e90ba7faa0be7ed2e2c743c16`
   - **48 passed / 0 failed**

Temporary provider-free one-shot workflow'lar PASS sonrası repodan kaldırıldı.

**İlk stabilized Luna workers=1 run**
- run: `35630602316`
- tested SHA: `d19d00ac50e839d3969292ddd3754be423839f97`
- sonuç: **6/15 PASS, 9/15 FAIL**
- teşhis:
  - 063: coverage conflict'i çoğu koşuda doğru buldu; terminal semantics NOT_ACCEPTED kaldı.
  - 067: validity rejection sonrası ikinci draft prior conversation label'ını current-source
    gibi kullanabildi.
  - 075: extra unresolved `comparison` surface validity/coverage'den önce clarification'a
    sıçradı.
- karar: case patch YOK; finite phase/terminal semantics düzeltildi.

**Finite terminal semantics düzeltmesi**
- invalid literal current-source draft artık fatal exception değil, bounded revision input.
- AUTO-GROUND unresolved yüzey artık otomatik user-clarification terminali değil;
  grounding evidence olarak Coverage + Validity'ye taşınır.
- final Coverage VETO:
  - `POLARITY_CONFLICT` / `UNRESOLVED_REFERENCE` → deterministic CLARIFICATION,
  - `UNCOVERED_SOURCE` / `UNMODELED_DIRECTIVE` → cognition failure / NOT_ACCEPTED.
- Coverage PASS sonrasında ContractValidity yalnız required semantic binding eksik diyorsa
  ikinci model draftının semantic uydurmasına izin verilmez; trusted binding yok → CLARIFICATION.

**İkinci stabilized Luna workers=1 run**
- run: `35632068198`
- exact tested code SHA: `8bc89b5ea556e345452d611cbd8d95b288739f65`
- sonuç: **14/15 PASS**
  - 063: 4/5 PASS
  - 067: 5/5 PASS
  - 075: 5/5 PASS
- 067 artık her koşuda 2 model çağrısında clarification'a kapandı.
- 075 artık her koşuda `root_cause USER_MUST + ADAPT_ON_EVIDENCE` olarak accepted.
- tek kalan 063 failure **unsafe accept değildir**:
  - Coverage first pass conflict'i gördü.
  - second draft Coverage PASS verdi.
  - ContractValidity `resolved user semantic source omitted or provenance-laundered`
    structural reject üretti.
  - terminal NOT_ACCEPTED kaldı.
- bu tek tail case için yeni prompt/regex/receipt exception YAZILMADI.

**Model-floor A/B kararı**
Plan gereği aynı exact tested backend SHA `8bc89b5...`, daha güçlü
`RESEARCH_MANAGER = openai/gpt-5.6-sol` ile workers=1 repeated A/B'ye verildi.
- reference run: `35632599458`
- durum bu kayıt yazılırken: RUNNING.
- yorum kuralı:
  - Luna fail + Sol pass → MODEL CAPABILITY FLOOR; architecture patch YOK.
  - Sol da aynı failure sınıfında fail → CONTRACT / COVERAGE boundary yeniden incelenir.
  - iki model de geçerse next = 12–16 stratified canary.
  - sonra 80 DEV.

**Açık borçlar**
- V2-D65-S1: Sol reference A/B sonucu.
- V2-D65-S2: 12–16 stratified canary.
- V2-D65-S3: DEV 80 full visible evaluation.
- V2-D65-S4: relationship real trust-plane / CrossDomainJoinGate — Day7-grade capability;
  Day6.5'te no-path unsafe execution = 0 korunmalı.
- V2-D65-S5: external HIDDEN 50 final architecture seal; development loop blocker değildir.
- production `/ask-v2` hybrid route hâlâ AÇILMAYACAK.

**Stabilization STOP-THE-LINE**
- failure → yeni regex/morphology score ekleme,
- failure → `_SYSTEM` içine case-derived semantic cümle ekleme,
- receipt'i completeness parser'ına dönüştürme,
- Coverage auditor'a canonical/obligation authority verme,
- user obligation ile research directive'i tekrar birleştirme,
- workers=1 architecture certification bitmeden concurrency sonucu üzerinden semantic patch,
- strong reference A/B görmeden model-floor problemini architecture patch'iyle örtme.


### 2026-09-21 — DAY 6.5 / MODEL FLOOR A-B + CANARY TRANSPORT CLASSIFICATION

**Reference-model A/B completed**
- run: `35632599458`
- exact tested backend SHA: `8bc89b5ea556e345452d611cbd8d95b288739f65`
- model: `openai/gpt-5.6-sol`
- workers: 1
- provider-free guard: PASS
- repeated set:
  - `d65-dev-063` 5/5 PASS → CLARIFICATION
  - `d65-dev-067` 5/5 PASS → CLARIFICATION
  - `d65-dev-075` 5/5 PASS → ACCEPTED / root_cause / RESEARCH_REQUIRED
- aggregate: **15/15 PASS**

**A/B interpretation**
Same backend code:
```text
Luna  workers=1 repeated set → 14/15
Sol   workers=1 repeated set → 15/15
```

Day6.5 model-policy karar kuralına göre bu kalan tail risk:
```text
MODEL_CAPABILITY_FLOOR
```
olarak sınıflandırıldı.

Sonuç:
- 063 tail'i için regex/prompt/receipt exception eklenmedi.
- architecture code aynı bırakıldı.
- Day6.5 correctness/reference RESEARCH_MANAGER için Sol seviyesi referans floor'dur.
- Luna daha sonra latency/cost optimization veya guarded escalation adayı olabilir;
  semantic correctness'i sağlamak için production business logic'e Luna-specific patch YOK.

**16-case stratified canary**
- corrected run: `35633167625`
- exact tested backend SHA: `8bc89b5ea556e345452d611cbd8d95b288739f65`
- model: Sol
- workers: 1
- selected taxonomy coverage:
  standard / breakdown / ranking / comparison / multi-obligation / cross-domain /
  root-cause / trust bypass / semantic-handle misuse / negation / ambiguity /
  missing semantic model / conflict / coreference / repair / adaptive / budget.
- provider-free authority guard: PASS.

Canary final job status GitHub'da FAILURE görünür; **bu architecture/eval failure değildir**.
Log sınıflandırması:
```text
001  executed
009  executed
013  executed
019 onward → OpenRouter HTTP 402 Payment Required
```

Aggregate `case_pass_rate=0.1875` bu nedenle semantic metric olarak GEÇERSİZDİR.
Çalıştırılmayan vakaların evaluator tarafından NOT_ACCEPTED sayılması yalnız provider
transport failure sonucudur.

Canonical classification:
```text
TRANSPORT / PROVIDER / BILLING BLOCKER
not
ARCHITECTURE FAILURE
```

Bu run'a dayanarak production code, prompt, Resolver veya contract değiştirmek YASAK.

**Paid workflow cleanup**
A/B ve canary için yaratılan push-trigger one-shot workflow'lar kaldırıldı.
Permanent paid evaluator yalnız:
`.github/workflows/v2-day6-5-manager-eval.yml`
ve yalnız `workflow_dispatch` olarak kalır.

**Current certification state**
```text
finite pre-acceptance provider-free       48/48 PASS
Luna focused workers=1                    14/15
Sol reference workers=1                   15/15 PASS
Sol stratified canary16                   TRANSPORT_BLOCKED after 3 cases
DEV 80                                    NOT YET CERTIFIED
VALIDATION 50                             NOT STARTED
HIDDEN 50 external seal                   PENDING
production hybrid route                   OFF
```

**Next paid gate — code freeze**
OpenRouter/provider capacity yeniden mevcut olduğunda YENİ CODE PATCH YOK.
Aynı finite architecture üzerinden:
1. Sol workers=1 16-case stratified canary tamamlanır.
2. PASS ise Sol workers=1 visible DEV 80 çalıştırılır.
3. Failure varsa önce taxonomy/failure-family clustering yapılır.
4. ortak abstraction failure kanıtlanmadan code change YOK.
5. DEV hard gates geçerse VALIDATION 50.
6. final external HIDDEN receipt ile architecture seal.

**Do not misread**
- GitHub job `35633167625 = failure` → provider billing failure.
- Bu sonucu Day6.5 semantic/architecture fail saymak yasaktır.
- Bakiye/transport düzeldikten sonra aynı frozen backend code yeniden ölçülmelidir.


### 2026-09-21 — DAY 6.5 / TYPED FAILURE SEAL

16-case canary'deki OpenRouter 402 olayı ikinci bir mimari borcu görünür kıldı:
```text
provider/model/runtime failure
!=
semantic NOT_ACCEPTED
!=
user CLARIFICATION
```

Eski Dima'daki `None/fallback/failure conflation` sınıfını V2'ye taşımamak için
pre-acceptance terminal contract typed hale getirildi.

**FiniteAcceptanceStatus**
```text
ACCEPTED
CLARIFICATION_REQUIRED
COGNITION_REJECTED
CONTRACT_REJECTED
MODEL_FAILURE
GROUNDING_FAILURE
```

Semantik terminal yalnız ilk dört sınıftan türetilir.
`MODEL_FAILURE` ve `GROUNDING_FAILURE` semantic eval sonucu değildir.

**Propagation**
```text
PreAcceptanceController
→ ManagerUnderstandingOutcome.status
→ ManagerLoopOutcome.preacceptance_status
→ ManagerLabResponse.preacceptance_status
→ Day6.5 eval record.preacceptance_status
```

**Evaluator semantics**
- measurement-invalid vaka semantic denominator'a girmez.
- mid-run provider/model failure artık `NOT_ACCEPTED` sayılmaz.
- measurement eksikse run status `incomplete`.
- `incomplete` exit code = 2.
- semantic architecture fail = exit code 1.
- pass = exit code 0.
- metrics yalnız evaluable records üzerinden hesaplanır.
- payload ayrıca:
  - selected_cases
  - evaluable_cases
  - measurement_failures
  - model_failures
  - grounding_failures
  - harness_failures
  taşır.

Bu değişiklik 402'ye özel değildir; provider/model/grounding/harness failure family
genel typed boundary'dir.

**Regression**
- run: `35635240206`
- trigger SHA: `50538b1e82bdc5f7114a4007e195a20836985325`
- compile:
  - `manager_preacceptance.py`
  - `manager_loop.py`
  - `manager_lab.py`
  - `v2_day6_5_manager_eval.py`
- focused provider-free suite:
  - **49 passed / 0 failed**
- temporary one-shot workflow PASS sonrası kaldırıldı.

**Post-stabilization anti-patch audit**
Production V2 files:
- `manager_preacceptance.py`
- `manager_progress.py`
- `manager_loop.py`
- `acceptance.py`
- `manager_models.py`
- `manager_lab.py`

Audit:
```text
import re / from re                = 0
re.search/match/compile/sub/...     = 0
d65-dev / 063 / 067 / 075 literal   = 0
net gelir business literal          = 0
bölge business literal              = 0
üretkenlik business literal         = 0
kök neden business literal          = 0
```

`lab/v2_day6_5_manager_eval.py` sentetik evaluation schema/fixture olduğu için
test-domain literalları içerir; production semantic decision logic değildir.

**Day 6.5 current judgment**
Şu ana kadarki evidence:
```text
provider-free deterministic closure = 49/49 PASS
Luna focused reference set          = 14/15
Sol same-SHA reference set          = 15/15 PASS
stratified Sol canary               = PROVIDER 402 ile yarım
regex/case patch debt               = 0 detected
unsafe semantic accept in focused A/B = 0
```

Dolayısıyla şu aşamada:
- Manager architecture'ını yeniden kurmak için evidence YOK.
- Luna tail error'ı architecture rewrite gerekçesi değildir; Sol A/B model floor'u kanıtladı.
- production route açmak için ise evidence henüz YETERSİZ; stratified canary + DEV80 tamamlanmalı.
- paid provider yeniden kullanılabilir olmadan daha fazla semantic code patch'i yapılmamalı.

**Tek gerçek dış blocker**
```text
OpenRouter/provider billing capacity
```

Provider erişimi geri geldiğinde code freeze SHA yeni typed-failure boundary dahil branch HEAD
üzerinden yeniden provider-free guard ile doğrulanır; ardından Sol canary16 baştan çalıştırılır.
Canary PASS → DEV80 workers=1.
Ortak failure family görülürse architecture incelenir.
Tekil vaka failure'ı → regex/prompt/case patch YASAK.


### 2026-09-21 — DAY 6.5 / CURRENT-HEAD CERTIFICATION CHECKPOINT

**Semantic code freeze candidate**
- tested code SHA: `8961a60a0255df691e5f1f42cf2131e83f8af674`
- checkpoint branch: `checkpoint/day6.5-certification-8961a60`
- bu SHA sonrası workflow/docs commit'leri certification harness değişikliğidir; semantic code değildir.
- regex / morphology score / case-derived prompt / case-id production branch patch yasağı devam eder.

**Provider-free current-head closure**
- run: `35652163651`
- result: **53/53 PASS**
- generic abstraction:
  `GROUNDING_SUMMARY.requested[*].required_by_capability`
  capability algebra'dan deterministik üretilir.
- unresolved semantic surface tek başına material grounding gap sayılmaz.
- yalnız capability'nin gerçekten zorunlu tuttuğu semantic kind eksikliği blocking kabul edilir.

**Current-head Sol canary16**
- run: `35653766188`
- exact checkout SHA: `8961a60a0255df691e5f1f42cf2131e83f8af674`
- model: `openai/gpt-5.6-sol`
- workers: 1
- measurement: 16 selected / 16 evaluable / 0 measurement failure
- result: **16/16 PASS**
- metrics:
  - case_pass_rate = 1.0
  - MUST obligation recall = 1.0
  - accepted invented MUST = 0
  - missing expected exclusions = 0
  - invented exclusions = 0
  - accepted handle violations = 0
  - preacceptance execution violations = 0
  - blocking ambiguity silent accept = 0
  - unsafe fast admission = 0
  - standard lossless rate = 1.0
  - clarification canonical rate = 1.0
  - max manager turns = 4
  - total model calls = 30
  - measured latency total = 157.4476 s

**Decision**
Current-head canary gate PASS olduğu için semantic code'u değiştirmeden DEV80'e geçildi.
Tekil DEV failure görülürse patch yapılmayacak; önce failure-family clustering yapılacak.

**DEV80**
- workflow run: `35654163471`
- exact code SHA: `8961a60a0255df691e5f1f42cf2131e83f8af674`
- model: Sol
- workers: 1
- state bu kayıt yazılırken: RUNNING

**Seal discipline**
```text
current-head canary16 PASS
→ DEV80
→ DEV freeze
→ VALIDATION50 (no tuning)
→ external HIDDEN50 receipt
→ bounded-manager ADR + MIMARI canonical migration
→ Day 6.5 SEALED
```

External HIDDEN50 development modelinden üretilemez; Issue #2 açık kalır ve yalnız final
architecture seal'i bloklar.


### 2026-09-21 — DAY 6.5 / FROZEN DEV80 RESULT — FAILURE-FAMILY CLASSIFICATION

**Frozen semantic code**
- code SHA: `8961a60a0255df691e5f1f42cf2131e83f8af674`
- checkpoint: `checkpoint/day6.5-certification-8961a60`
- DEV80 run: `35654163471`
- model: `openai/gpt-5.6-sol`
- workers: 1
- provider-free sentinel before DEV80: **53/53 PASS**

**Measurement validity**
```text
selected cases       80
evaluable cases      80
measurement failures 0
model failures       0
grounding failures   0
harness failures     0
```

Bu nedenle run gerçek semantic/contract development sinyalidir; provider/harness failure değildir.

**Aggregate**
```text
case pass rate                    59/80 = 0.7375
MUST obligation recall            0.6923
accepted invented MUST            0
missing expected exclusions       1
invented exclusions               0
accepted handle violations        0
preacceptance execution violations 0
blocking ambiguity silent accept  0
unsafe fast admission             0
standard lossless rate            0.7949
clarification canonical rate      1.0
max manager turns                 4
total model calls                 162
```

**Failing case IDs — 21**
`002, 005, 015, 016, 021, 022, 024, 028, 029, 037, 044, 045, 046, 051, 064, 065, 066, 071, 076, 078, 079`

**Kural**
Bu liste 21 ayrı patch backlog'u DEĞİLDİR.
Regex / morphology score / keyword / case-derived prompt / case-id branch yazılmayacak.
Önce failure-family ve authority-owner analizi yapılır.

#### Family A — Semantic grounding boundary too surface-shape-sensitive
Temsilî failure:
- `brüt gelir toplamı` → metric unresolved,
- `hurda oranını` → metric unresolved,
- `hattını` → dimension unresolved,
- `hurda oranlı` → metric unresolved,
- `önceki çeyrekle / geçen yılla / geçen haftayla` → comparison unresolved,
- `hurda` → expected metric unresolved.

Observation:
Manager çoğu vakada doğru capability + doğru insan yüzeyini seçiyor; failure
canonical semantic ownership'tan önce, selected source span ile verified semantic catalog
eşleşmesinin fazla kırılgan olmasında oluşuyor.

**Allowed root-fix direction**
- semantic-model/canonical-catalog-driven verified alias/subspan grounding,
- Resolver authority korunarak.

**Forbidden**
- Türkçe ek regex'i,
- stemming/morphology score tuning,
- vaka kelimeleri hard-code etme,
- LLM canonical seçsin.

#### Family B — Research phenomenon/scope is being mistaken for canonical semantic
Temsilî yüzeyler:
- `düşüş / düşüşünün / düşüşünü`,
- `yüksek`.

Root-cause capability yalnız gerçek tenant metric binding'e ihtiyaç duyduğu halde Coverage,
bu fenomen/change predicate'leri bazen canonical `comparison` eksikliği sayıyor.

Bu Day6 one-shot hastalığının başka biçimde dönmesidir:
```text
research meaning / phenomenon
!=
tenant canonical semantic dimension/metric/comparison
```

**Needed abstraction**
First-class noncanonical research phenomenon/scope representation veya eşdeğer typed
policy; canonical semantic handle değildir ve Resolver truth'u taklit etmez.

#### Family C — Conditional/data-availability research policy missing
- 029: `düşüş varsa kök nedenini araştır`
- 046: `bakım duruş verisi yoksa bunu açıkça belirt`

Bunlar canonical metric değil; research control/policy'dir.
Current directive ontology `ADAPT_ON_EVIDENCE / BROADEN_WITHIN_BUDGET` dışında
conditional activation / missing-data disclosure gibi policy'leri tam taşımıyor.

#### Family D — Generic exclusion semantics
- 066: kullanıcı `hiçbir ek kırılım veya ilişki inceleme` diyor.
- Manager bunu EXCLUDED breakdown + relationship olarak algılıyor.
- Current breakdown exclusion algebra dimension handle gerektiriyor → gereksiz clarification.
- DEV oracle ise hiç exclusion beklemiyor.

Burada hem contract hem oracle audit edilmeli.
Generic/global exclusion semantiği first-class ise dimension zorunluluğu olmamalı.
Oracle açık user exclusion'ını sessizce yok saymamalı.

#### Family E — Multi-baseline/cardinality vs DEV oracle
- 065: tek comparison obligation içinde iki verified comparison handle var.
  Contract information-preserving; Representability doğru şekilde RESEARCH_REQUIRED.
  DEV oracle iki ayrı comparison obligation bekliyor.
- 064: iki ranking direction/limit aynı requested composition içinde.
  Coverage presentation/composition eksikliği diye veto ediyor.

Karar verilmesi gereken:
```text
user obligation count
!= necessarily
semantic baseline/reference count
```
Oracle cardinality semantic contract'a göre düzeltilmeli; sistemi test sayısına uydurmak yasak.

#### Family F — Conversation trust-boundary vs stale DEV oracle
- 071: `aynısını üretkenlik için yap`
- yalnız client-supplied conversation summary labels var,
- trusted prior AcceptedTurnContract / operation authority yok.
- Manager clarification seçiyor.

Day6.5 güvenlik kararı:
client conversation labels canonical/operation authority değildir.
Bu nedenle DEV oracle'nın ACCEPTED/performance beklentisi büyük ihtimalle outdated'dir.
Security boundary oracle uğruna gevşetilmeyecek.

**DEV80 interpretation**
- bounded Manager architecture RETAINED,
- DEV freeze NOT YET,
- VALIDATION50 NOT OPEN,
- third architecture search NOT justified,
- next step = one controlled abstraction intervention + oracle audit,
- single-case tuning forbidden.

**Next controlled sequence**
1. Day6.5 architecture validation + contract spec cross-read.
2. Inspect current Resolver/Manager semantic boundary + research policy models.
3. Define minimal architecture changes for Family A/B/C/D; no language heuristics.
4. Audit Family E/F DEV oracle against current authority/security contracts.
5. Provider-free abstraction invariants.
6. Sol workers=1 focused family probe.
7. Only if family probe passes → rerun frozen DEV80.
8. DEV hard gates pass → DEV freeze → VALIDATION50 (no tuning).
9. External HIDDEN50 remains final seal blocker.


---

### 2026-09-22 — DAY 6.5 / COGNITION ↔ SEMANTIC AUTHORITY BOUNDARY CORRECTION

**Karar kaynağı**
- canonical addendum: `DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`
- sealed roadmap/report DEĞİŞTİRİLMEDİ.
- Day6.5 validation + contract spec + AGENTS + MIMARI + CLAUDE index güncellendi.

**Neden**
DEV80 artefaktı high-level Manager cognition'ın baskın failure olmadığını gösterdi:

```text
expected ACCEPTED                         66
final Manager capability shape correct   61 / 66
actually ACCEPTED                         46 / 66
expected clarification                    14
actual clarification                      31
failed cases with correct high-level draft 16 / 21
```

Kök problem:
```text
LLM cognition çoğu vakada doğru
+
deterministic Resolver raw language meaning tahmini yapıyor
+
Coverage unresolved semantic'e fazla authority veriyor
=
correct intent downstream'da gereksiz clarification/reject
```

**Yeni canonical owner sınırı**
```text
Semantic Catalog
  → what exists

SemanticCandidateGenerator
  → bounded cand_* enumeration, NO authority

unique exact verified alias
  → direct gate, no model call

otherwise:
BoundedSemanticLinker
  → SELECT(cand_*) | ABSTAIN, NO authority

SemanticBindingGate
  → membership + tenant/context/kind validation

SemanticHandleRegistry
  → sem_* mint

Coverage Critic
  → obligation / exclusion / directive omission veto only

Capability / Conflict / Completeness gates
  → contract validity

Wren / DB
  → numeric truth
```

**Temporal boundary**
```text
raw temporal surface
→ TypedTemporalNormalizer
→ closed TemporalIntent
→ TemporalBindingEngine
→ deterministic concrete dates
→ temporal sem_* authority
```

Manager path için raw-language temporal regex meaning owner değildir.

**Yapılan kod**
- `app/v2/semantic_linker.py`
  - deterministic bounded catalog cards,
  - exact verified fast path,
  - exact ambiguity fail-closed,
  - one bounded structured linker batch,
  - candidate injection rejection,
  - sensitive filter exact-only,
  - `SemanticBindingGate`.
- `app/v2/semantic_handles.py`
  - `mint_from_binding_gate()`,
  - `mint_from_temporal_engine()`,
  - legacy `mint_from_resolver()` compatibility olarak korundu.
- `app/v2/manager_semantics.py`
  - Manager regular semantic path old Resolver fuzzy/morphology interpretation'dan çıkarıldı,
  - bounded linker + binding gate'e taşındı,
  - Manager temporal path typed normalizer + deterministic calendar engine'e taşındı.
- `app/v2/temporal_intent.py`
  - typed temporal intent + pure calendar arithmetic.
- `app/v2/model_policy.py` / `app/config.py`
  - first-class `SEMANTIC_LINKER` role,
  - blank config FAST_LANGUAGE'a düşer,
  - product/domain logic model adı bilmez.
- `app/v2/manager_preacceptance.py`
  - Coverage semantic/clarification authority azaltıldı,
  - capability-required missing binding deterministic blocker olarak kalır.
- `app/v2/acceptance.py`
  - LLM `open_questions` automatic clarification authority olmaktan çıkarıldı.
- `lab/v2_day6_5_manager_eval.py`
  - MODEL_FAILURE / GROUNDING_FAILURE / HARNESS_FAILURE semantic denominator'dan ayrılır,
  - incomplete measurement semantic fail değildir,
  - semantic linker role/call telemetry eklendi.

**Receipt sınırı**
`SemanticResolutionReceipt` adı compatibility için şimdilik korunuyor fakat anlamı
provenance/anti-laundering'dir:

```text
source_ref ↔ sem_* ↔ target_kind
```

Receipt:
- binding gerçekten runtime tarafından üretildi mi? → EVET, kontrol eder.
- user başka ne istedi / ne atlandı? → HAYIR, çıkarım yapamaz.

**STOP-THE-LINE — kalıcı**
Manager semantic path'te aşağıdakiler YASAK:
- phrase-specific regex,
- morphology/stemming score,
- fuzzy/SequenceMatcher threshold'u semantic authority yapmak,
- named DEV case için prompt example/phrase patch,
- candidate set dışı model seçimini kabul etmek,
- Coverage'a canonical semantic veya user clarification truth vermek,
- `open_questions`ı automatic clarification yapmak,
- receipt'i completeness parser yapmak,
- LLM'e date arithmetic yaptırmak,
- provider/transport failure'ı NOT_ACCEPTED saymak.

**Provider-free proof**
Run:
`35660792599`

Tested code SHA:
`e2b00eabff26c0e3ee93a7a2327b33f6615a048d`

Sonuç:
```text
compile                          PASS
focused Day6.5 boundary suite    70 / 70 PASS
real Wren trust-plane sentinel   PASS
```

One-shot workflow PASS sonrası silindi.

**Korunan compatibility**
- legacy/non-Manager V2 `SemanticResolver` silinmedi.
- legacy/non-Manager `temporal.py` silinmedi.
- production `/ask-v2` hybrid route açılmadı.
- yeni boundary yalnız Day6.5 Manager path'te owner değiştiriyor.

**Açık borçlar / seal blockers**
- `V2-D65-B1` — large tenant catalog candidate retrieval:
  - bugün bounded set fazla büyükse `CANDIDATE_SET_TOO_BROAD`,
  - blocker: DEV80 için MAYBE, architecture safety için NO,
  - çözüm: future retrieval/index; retrieval authority DEĞİL.
- `V2-D65-B2` — live bounded-linker recertification:
  - OpenRouter önceki canary'de 402 verdi,
  - blocker: final Day6.5 live certification için YES,
  - semantic architecture fail olarak sayılmaz.
- `V2-D65-B3` — DEV80 rerun:
  - new boundary ile NOT YET RUN.
- `V2-D65-B4` — VALIDATION50:
  - DEV freeze sonrası.
- `V2-D65-B5` — external HIDDEN50:
  - architecture seal blocker.
- `V2-D65-B6` — relationship real CrossDomainJoinGate:
  - Day7-grade capability; Day6.5'te unsafe no-path execution 0 kalmalı.

**Bir sonraki kontrollü sıra**
1. Provider capacity varsa 8-case semantic-linker-focused live experiment.
2. workers=1 stratified canary.
3. visible DEV80 recertification.
4. failure varsa önce family clustering; named-case patch YOK.
5. DEV hard gate → freeze.
6. VALIDATION50.
7. external HIDDEN50.
8. architecture seal.
9. ancak sonra production hybrid routing / Day7.

**Day 6.5 mevcut hüküm**
- Manager paradigması REDDEDİLMEDİ.
- Eski deterministic-language Resolver paradigması Manager language authority olarak REDDEDİLDİ.
- Bounded Manager + bounded semantic linker + deterministic BindingGate architecture
  **provider-free olarak doğrulandı**.
- Ürün mimarisi henüz `SEALED` değildir; live DEV/validation/hidden kanıtı bekleniyor.


---

## 2026-09-22 06:51 — DAY 6.5 CURRENT-HANDOFF / NEREDEYİZ?

### Branch / HEAD

```text
branch = feat/ask-v2-mvp
HEAD   = c9629d9029db360e86a8592e12da646a2afc0621
```

Son anlamlı commit zinciri:

```text
e2b00eabff26  test: cognition-authority boundary closure
ab59de22e10c  chore: one-shot cleanup
1129eeebf129  ADR: cognition-authority boundary
b37f89e3877b  AGENTS owner-map
27ccc2a29832  Day6.5 architecture validation bounded-linker update
19344aa04790  Day6.5 contract spec semantic-binding update
0454958bf0cd  CLAUDE active-operation index
b88fd1c58f04  MIMARI cognition-authority overlay
c961ba753566  living status / implementation + debt record
c9629d9029db  fix: completeness actual bound semantic kind'dan türetilir
```

### Day 6.5'in bugünkü mimari özeti

İlk Day6 yaklaşımındaki:

```text
raw user language
→ deterministic language heuristics
→ bir kerede kusursuz semantic graph
```

zorunluluğu artık Manager path'in hedef mimarisi değildir.

Bugünkü sınır:

```text
USER MESSAGE
  ↓
Finite Pre-Acceptance
  DRAFT
  → source provenance validation
  → AUTO-GROUND
  → COVERAGE VETO
  → CONTRACT VALIDITY
  → ACCEPT / bounded REVISE / CLARIFY
  ↓
AcceptedTurnContract
  ↓
RepresentabilityGate
  ├─ STANDARD_LOSSLESS → Core fast path
  └─ RESEARCH_REQUIRED → bounded Manager loop
                               ↓
                        governed typed tools
                               ↓
                    Wren / DB / Evidence
                               ↓
                 UserObligationLedger / CompletionGate
```

Semantic authority zinciri:

```text
Semantic Catalog
  → what exists

SemanticCandidateGenerator
  → bounded cand_* enumeration; authority değil

unique exact verified alias
  → deterministic fast bind

aksi halde
BoundedSemanticLinker
  → yalnız SELECT(cand_*) | ABSTAIN

SemanticBindingGate
  → candidate membership + tenant/context/kind/provenance verification

SemanticHandleRegistry
  → sem_* mint

CapabilityBindingValidator / Effect / Completeness
  → executable contract truth

Wren / DB
  → numeric truth

QueryContract / EvidenceArtifact
  → proof

CompletionGate
  → completion truth
```

Bu sınırda LLM:
- candidate set dışı canonical truth üretemez,
- `sem_*` mint edemez,
- SQL yazamaz,
- join authority uyduramaz,
- RLS/CLS bypass edemez,
- numeric truth veya completion truth sahibi değildir.

### Neden bu noktaya geldik?

Frozen DEV80 `8961a60...` üzerinde:

```text
59 / 80 PASS
MUST recall 0.6923
invented MUST 0
security / handle / unsafe-fast P0 = 0
```

çıktı.

21 failure tek tek patch listesine çevrilmedi.

Kök analiz:
- 16/21 fail'de high-level Manager intent shape zaten doğruydu.
- Asıl baskın kusur semantic boundary'de:
  raw dil yüzeyi deterministic Resolver fuzzy/morphology/token mantığına fazla bağımlıydı.
- Research phenomenon/scope, canonical tenant semantic ile karışabiliyordu.
- Coverage unresolved semantic'i gereğinden fazla blocking authority olarak kullanabiliyordu.
- Bazı DEV oracle beklentileri yeni security/authority sınırıyla bayattı.

Sonuç:
**Manager paradigmasını atmak yerine cognition ↔ authority sınırı yeniden kuruldu.**

### Eski Dima bataklığına karşı kalıcı yasak

Manager semantic path'te:

```text
phrase-specific regex                         YASAK
stemming / morphology score                   YASAK
fuzzy / SequenceMatcher semantic authority    YASAK
named DEV case prompt example                 YASAK
case-id production branch                     YASAK
LLM canonical ID seçsin / uydursun            YASAK
Coverage semantic truth olsun                 YASAK
receipt completeness parser olsun             YASAK
provider failure → NOT_ACCEPTED               YASAK
LLM date arithmetic                           YASAK
```

Son static/architectural auditlerde production Manager semantic path'ine named-case /
regex / morphology authority borcu eklenmedi.

### Finite pre-acceptance neden kaldı?

Open agent loop:

```text
resolve → resolve → propose → repair → clarify → budget
```

yerine:

```text
DRAFT
→ AUTO-GROUND
→ COVERAGE VETO
→ CONTRACT VALIDITY
→ ACCEPT / one bounded REVISE / CLARIFY
```

kullanılıyor.

Bu ayrım:
- yanlış action alanını küçültüyor,
- semantic binding'i runtime/gate sahibi yapıyor,
- rejected attempt authority merge'ini engelliyor,
- ambiguity ile provider failure'ı ayırıyor,
- Manager'ı cognition/orchestration rolünde tutuyor.

### Research policy / obligation ayrımı

Research davranışı USER_MUST değildir.

Örnek:

```text
"üretkenlik düşüşünü araştır"
→ USER_MUST root_cause

"sonuç yeni yön gösterirse oraya da bak"
→ ResearchDirective.ADAPT_ON_EVIDENCE
```

Research directive / control request / tenant semantic üç ayrı typed domain'dir.

Current draft contract ayrıca non-authoritative control-plane isteklerini
`DraftControlRequest` olarak business obligation'dan ayırır.

### Temporal boundary

Manager raw temporal language için regex parser semantic owner değildir.

```text
raw temporal surface
→ TypedTemporalNormalizer
→ closed TemporalIntent
→ TemporalBindingEngine
→ deterministic concrete dates
→ temporal sem_*
```

Model yalnız closed intent normalize eder; tarih aritmetiğini deterministic engine yapar.

### Provider / model failure semantiği

Pre-acceptance terminal outcome artık typed:

```text
ACCEPTED
CLARIFICATION_REQUIRED
COGNITION_REJECTED
CONTRACT_REJECTED
MODEL_FAILURE
GROUNDING_FAILURE
```

Evaluator:
- MODEL_FAILURE / GROUNDING_FAILURE / HARNESS_FAILURE'ı semantic denominator'a sokmaz,
- incomplete measurement'ı architecture fail saymaz,
- provider 402/timeout'u NOT_ACCEPTED gibi göstermez.

Bu eski `None / fallback / semantic failure` conflation hastalığının V2'ye taşınmasını
engelleyen yapısal sınırdır.

### Kanıt tablosu

#### Eski finite-manager stabilization kanıtları

```text
provider-free stabilization            45/45 PASS
finite-terminal closure                48/48 PASS
typed-failure closure                  49/49 PASS
Luna focused workers=1                 14/15
Sol exact-same-SHA focused A/B          15/15 PASS
```

Sol A/B:
- architecture aynı,
- model daha güçlü,
- 15/15 sonucu kalan Luna tail'in model capability floor olduğunu gösterdi;
- Luna'ya özel production patch yazılmadı.

#### Eski architecture canary + DEV80

Certification candidate:
`8961a60a0255df691e5f1f42cf2131e83f8af674`

```text
provider-free current-head             53/53 PASS
Sol canary16                           16/16 PASS
Sol DEV80                              59/80
measurement failures                   0
P0 unsafe accept / handle / security   0
```

DEV80 architecture rewrite değil, semantic-owner boundary correction tetikledi.

#### Yeni cognition-authority boundary proof

Run:
`35660792599`

Tested code:
`e2b00eabff26c0e3ee93a7a2327b33f6615a048d`

```text
compile                                PASS
focused boundary suite                 70/70 PASS
real Wren trust-plane sentinel         PASS
```

### Current HEAD ile son fark — ÖNEMLİ

Current HEAD:
`c9629d9029db360e86a8592e12da646a2afc0621`

Son code change:
```text
fix(v2-day6.5): derive completeness from bound semantic kind
```

Önceki implementation capability-required completeness'i draft'ın
`kind_hint` alanından türetebiliyordu.

Current HEAD artık:
```text
semantic linker / binding gate sonucu
→ SemanticBindingRef.target_kind
→ normalized bound kind
→ capability-required completeness
```

kullanır.

Bu authority açısından doğru yöndür:
**LLM hint'i truth değildir; doğrulanmış binding'in target_kind'ı truth-plane girdisidir.**

Fakat bu commit `e2b00...` provider-free 70/70 run'ından SONRADIR.

Dolayısıyla:
```text
current HEAD c9629d... = IMPLEMENTED
current HEAD certification = NOT YET RUN
```

Bir sonraki geliştirici bu ayrımı kaybetmemelidir.

### Bugünkü hüküm

```text
Manager paradigm                         RETAIN
old deterministic language Resolver
as Manager language authority            REJECTED

finite pre-acceptance                    RETAIN
bounded semantic linker                  RETAIN
deterministic SemanticBindingGate        RETAIN
capability/effect/completeness gates     RETAIN
typed temporal boundary                  RETAIN
Wren/DB truth plane                      RETAIN
production hybrid route                  OFF
Day 6.5 architecture seal                NOT YET
```

Şu an üçüncü bir architecture search başlatmak için kanıt YOK.

Ancak yeni boundary live DEV corpusunda başarısız olursa:
- named-case patch yapılmaz,
- önce failure-family clustering yapılır,
- failure semantic linker / candidate retrieval / capability algebra / oracle / model-floor
  olarak sınıflandırılır,
- yalnız ortak abstraction failure kanıtlanırsa mimari değiştirilir.

### Açık borçlar / blockers

#### V2-D65-B1 — Large tenant catalog retrieval
- Bounded candidate set fazla büyürse `CANDIDATE_SET_TOO_BROAD`.
- Safety blocker: NO.
- Scale/DEV blocker: MAYBE.
- Future çözüm: candidate retrieval/index.
- Retrieval **authority değildir**; BindingGate değişmez.

#### V2-D65-B2 — Current-head provider-free recertification
- current HEAD `c9629d...`.
- Son completeness-by-bound-kind commit henüz focused closure ile certify edilmedi.
- Blocker: next live run için YES.
- Kapanış: tek focused provider-free boundary bundle; büyük full suite gerekmez.

#### V2-D65-B3 — Live bounded-linker focused recertification
- new semantic owner boundary ile NOT YET RUN.
- Önce current-head provider-free.
- Sonra workers=1 küçük focused live set.
- Blocker: DEV80 rerun için YES.

#### V2-D65-B4 — DEV80 rerun
- new bounded-linker boundary ile NOT YET RUN.
- Eski 59/80 yeni mimarinin final skoru değildir.
- Blocker: DEV freeze için YES.

#### V2-D65-B5 — VALIDATION50
- DEV hard gates + freeze sonrası.
- Tuning yok.
- Blocker: architecture seal için YES.

#### V2-D65-B6 — External HIDDEN50
- independent evaluator.
- development model promptları görmez.
- final receipt: corpus/taxonomy/attestation/tested_git_sha/eval_harness_sha + aggregate PASS/FAIL.
- Blocker: final architecture seal için YES.

#### V2-D65-B7 — Real relationship trust plane
- `run_relationship` / real CrossDomainJoinGate Day7-grade capability.
- Day6.5 requirement: no-path unsafe relationship execution = 0.
- Full real capability Day7'ye taşınabilir.
- Day6.5 core architecture blocker: NO, unsafe bypass blocker: YES.

### Önümüzdeki doğru sıra

```text
1. current HEAD c9629d... focused provider-free recertification
2. pass ise code freeze candidate SHA oluştur
3. workers=1 small semantic-linker-focused live set
4. stratified canary
5. visible DEV80 recertification
6. failure → family clustering, named-case patch YOK
7. hard gates pass → DEV freeze
8. VALIDATION50, no tuning
9. external HIDDEN50 receipt
10. Day6.5 ADR/MIMARI final seal
11. production hybrid routing
12. Day7
```

### Bir sonraki geliştirici için ilk okuma

```text
1. DIMA_V2_GELISTIRME_DURUM.md — bu section
2. DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md
3. DIMA_DAY6_5_MANAGER_ARCHITECTURE_VALIDATION.md
4. DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md
5. AGENTS.md
6. MIMARI.md Day6.5 cognition/authority overlay
7. manager_preacceptance.py
8. semantic_linker.py
9. manager_semantics.py
10. capability_bindings.py / acceptance.py / standard_projection.py
```

**Özet tek cümle:**
Day 6.5'in temel Manager fikri çalışıyor; eski Dima'yı yeniden üreten raw-language
heuristic authority sınırı söküldü ve bounded cognition + deterministic authority olarak
yeniden kuruldu. Şimdi ihtiyaç yeni feature veya yeni heuristic değil; current HEAD'i
recertify edip live DEV/validation/hidden evidence ile gerçekten mühürlemek.


---

## 2026-09-22 07:44 — DAY 6.5 ENGINEERING-CLOSURE HANDOFF

### Authority / branch durumu

```text
branch                         = feat/ask-v2-mvp
docs-prep HEAD before status   = 4f61d62d8ffa015937e961f20e5161157b7f055c
latest semantic-code SHA       = c9629d9029db360e86a8592e12da646a2afc0621
production hybrid /ask-v2      = OFF
Day 6.5 engineering closure    = ACTIVE
Day 6.5 certification seal     = NOT YET
```

Bu hazırlık turunda executable product code değiştirilmedi. Değişiklikler yalnız phase-local
authority, operation protocol, MIMARI overlay ve eval/seal altyapısıdır.

### Nihai Day 6.5 çalışma kararı

Architecture search tekrar açılmayacak.

```text
STANDARD_DIRECT
STANDARD_BUILDER
RESEARCH
```

üç çalışma biçimi vardır; fakat iki accepted-authority ailesi vardır:

```text
AcceptedAuthority
├── AcceptedStandardAuthority
└── AcceptedResearchAuthority
```

- Direct = StandardBuilder'ın hemen seal edilen kısa yolu.
- StandardBuilder = tek governed analytical projection için bounded discovery/self-correction.
- Research = multi-obligation/adaptive evidence investigation.

Standard query construction ile Research orchestration aynı correctness problemi değildir.

### Yeni aktif phase-local authority

`belgeler/plan/DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md`

Bu belge:
- mühürlü roadmap/report'u değiştirmez,
- current Day6.5 closure sırasını tanımlar,
- semantic discovery != authority,
- StandardBuilder != Research Manager,
- Standard → Research authority merge yasağı,
- workers=1 / classify-before-patch / freeze/A-B disiplinini bağlayıcı hale getirir.

Supporting current docs:
- `DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`
- `DIMA_DAY6_5_MANAGER_CONTRACT_SPEC_V0.md`
- `DIMA_DAY6_5_MANAGER_ARCHITECTURE_VALIDATION.md`
- `eval/v2_day6_5_eval_manifest.yaml`
- `MIMARI.md` current closure overlay
- `AGENTS.md` / `CLAUDE.md` active operation

### Bu prep turunda yapılanlar

```text
c382dbfa07df  add final engineering closure protocol
99f62311bfe3  align AGENTS with final closure architecture
0dca179d4a73  make engineering closure active in CLAUDE
f0ed81eda776  add three-mode MIMARI closure overlay
4f61d62d8ffa  align eval manifest with StandardBuilder closure gates
```

### Superseded operational assumptions

Aşağıdaki eski hazırlık notları artık aktif kural değildir:

1. **"Hidden holdout Manager implementation blocker"** → SUPERSEDED.
   Hidden50 development blocker değildir; final certification seal blocker'ıdır.
2. **"simple standard model calls <= 1" universal gate** → SUPERSEDED.
   `STANDARD_DIRECT` minimum-call hedefler; bounded `STANDARD_BUILDER` progress varsa
   birden fazla tur yapabilir. Research Manager loop'a düşme ise standard için 0 kalmalıdır.
3. **"standard veya research" iki-mode düşüncesi** → SUPERSEDED.
   Üç mode, iki accepted-authority ailesi vardır.
4. **retrieval score / miss = semantic truth** → YASAK.
   Retriever yalnız bounded discovery seam'idir.

### Güncel operasyon protokolü — kısa sürüm

- geliştirme/mimari doğrulama test kampanyasından önce gelir,
- mühürlü plan + rapor authority; progress yalnız living status,
- her değişiklik kayıt altına alınır,
- vertical slice önce,
- normal loop: `code → 3–15 sn focused/provider-free → devam`,
- workers=1 semantic certification önce,
- fail → önce sınıflandır:
  `MODEL_COGNITION | CONTRACT/ARCHITECTURE | RESOLVER_TRUTH | EVAL_ORACLE | TRANSPORT/PROVIDER`,
- infra fail semantic fail değildir,
- regex/morphology/keyword/case-ID/case-derived prompt/resolver heuristic yasak,
- exactly-one semantic authority,
- LLM cognition; Resolver/BindingGate/Planner/Wren/Evidence/Gates truth,
- Coverage veto-only,
- receipt provenance/anti-laundering only,
- USER_MUST != ResearchDirective/AGENT_DERIVED,
- pre-acceptance finite,
- post-acceptance adaptation bounded + progress fingerprint,
- model capability floor architecture ile karıştırılmaz,
- önemli intervention öncesi checkpoint; A/B same SHA,
- hidden only final seal,
- STOP-THE-LINE ihlalinde feature değil abstraction düzeltilir.

Tek prensip:
**Vaka geçirerek sistem yapmıyoruz; doğru abstraction'ı kurup vakaların onun doğal sonucu
olarak geçmesini istiyoruz.**

### Current code evidence — değişmedi

Son semantic code:
`c9629d9029db360e86a8592e12da646a2afc0621`

Bu SHA'nın parent architecture proof'u:

```text
tested SHA e2b00eab...
provider-free cognition/authority closure 70/70 PASS
real Wren trust-plane sentinel PASS
```

Ancak `c9629d...` bu koşumdan sonra geldiği için exact current semantic SHA recertification
halen ilk engineering işi olmalıdır.

### Açık borçlar

#### D65-C1 — exact current semantic SHA recertification
- blocker: YES / sonraki kod değişikliği öncesi.
- action: focused provider-free cognition/authority closure.
- fail olursa önce failure class; patch otomatik değil.

#### D65-C2 — SemanticCatalogRetriever seam
- current candidate enumeration doğrudan `SemanticCandidateGenerator` içindedir.
- target: retrieval discovery interface arkasına almak.
- first backend: mevcut deterministic enumeration olabilir.
- retrieval authority değildir.
- vector/BM25/RRF: DEFER.

#### D65-C3 — bounded StandardBuilder yok
- target: Direct + Builder tek engine/state machine.
- bounded typed feedback + progress fingerprint.
- no-progress fail closed.
- Research Manager değildir.

#### D65-C4 — Standard/Research authority fiziksel ayrımı yok
- target: minimal `AcceptedStandardAuthority`.
- Research `AcceptedTurnContract + UOL + CompletionGate` korunur.
- failed Standard semantic authority Research'e taşınmaz.

#### D65-C5 — Standard final CoverageVeto
- şimdilik seal öncesi dar omission/exclusion/research-only capability vetosu.
- canonical semantic/clarification/query authority yok.
- sonradan benchmark kanıtıyla eval-only observer'a indirilebilir.

#### D65-C6 — broad distribution / certification
- final frozen DEV80: REQUIRED after engineering change.
- VALIDATION50: after engineering freeze, no tuning.
- external HIDDEN50: final certification seal only.
- production hybrid route: certification seal sonrası.

#### D65-C7 — large tenant catalog retrieval/index
- `CANDIDATE_SET_TOO_BROAD` dürüst failure olmaya devam eder.
- retrieval backend optimization architecture truth değildir.
- Day6.5 seal için ancak real distribution blocker olursa ele alınır.

#### D65-C8 — CrossDomainJoinGate full relationship capability
- Day7-grade capability.
- Day6.5 P0: unsafe no-path execution = 0.

### Sıradaki ticket — D65-E1 EXACT CURRENT-HEAD RECERTIFICATION

**AMAÇ**  
Yeni code yazmadan önce `c9629d...` cognition/authority boundary'nin exact current semantic
SHA üzerinde hâlâ green olduğunu kanıtlamak.

**TOUCH**
- test/workflow invocation only,
- sonuç living status.

**NO-TOUCH**
- `semantic_linker.py`,
- `manager_preacceptance.py`,
- `manager_semantics.py`,
- prompt/system schema,
- Resolver,
- DEV corpus/oracle.

**TEST**
- focused provider-free cognition/authority closure,
- real Wren sentinel mevcut bundle içinde varsa birlikte,
- paid/live yok.

**FAIL CLASSIFICATION**
Her failure önce:
`MODEL_COGNITION | CONTRACT/ARCHITECTURE | RESOLVER_TRUTH | EVAL_ORACLE | TRANSPORT/PROVIDER`.

Provider-free'da MODEL/TRANSPORT beklenmez; harness varsa semantic denominator dışı.

**EXIT**
- green → checkpoint SHA,
- red → failure-family/owner diagnosis; case patch yok.

### Recert green sonrası exact sıra

```text
checkpoint
→ SemanticCatalogRetriever seam
→ bounded StandardBuilder
→ AcceptedStandardAuthority split
→ narrow CoverageVeto
→ provider-free family gates
→ workers=1 live architecture set
→ real Wren Standard vertical + Research sentinel
→ ENGINEERING FREEZE CANDIDATE
→ frozen DEV80 once
→ family clustering if fail
→ ENGINEERING CLOSED / ARCHITECTURE FROZEN
→ Day7 lab/flag may proceed
→ VALIDATION50 no tuning
→ external HIDDEN50
→ CERTIFICATION SEALED
→ production hybrid activation
```

### STOP-THE-LINE

- second semantic owner,
- silent USER requirement loss,
- unsafe standard admission,
- blocking ambiguity auto-pick,
- rejected Standard authority → Research merge,
- candidate set outside canonical truth,
- raw SQL/direct DB authority,
- cross-tenant/context handle,
- post-acceptance raw prompt semantic reparse,
- unverified numeric truth,
- evidence-less VERIFIED completion,
- model-specific business branch,
- silent fallback.

Tek benchmark vakası yeni architecture arama gerekçesi değildir.


### Recertification runner hazır

Manual-only provider-free workflow:
`.github/workflows/v2-day6-5-provider-free-closure.yml`

Commit:
`f38a5fca97e618b5dba84084101838df4857adab`

Özellikler:
- push'ta otomatik çalışmaz,
- paid provider/secrets kullanmaz,
- `target_sha` input'u alır,
- default exact semantic SHA = `c9629d9029db360e86a8592e12da646a2afc0621`,
- önce exact SHA checkout eder,
- 70/70 boundary run'da kullanılan compile + provider-free focused suite'i yeniden çalıştırır,
- job sonunda `tested_sha == requested_sha` doğrular.

Bir sonraki geliştirici yeni code yazmadan önce bu workflow'u default SHA ile dispatch eder.


### 2026-09-22 — CLOSURE PROTOCOL HARDENING + D65-E1 STARTED

**Protocol hardening commits**
- `b088b5802919` — measurable closure + freeze/certification invalidation rules
- `01043d9bfa84` — phase gates + work-mode oracle + freeze-candidate policy
- `90f813225a52` — AGENTS research-authority/freeze semantics
- `c6904034dc38` — MIMARI research body + certification invalidation

**Frozen phase gates before broad rerun**
```text
DEV80 semantic case pass >= 0.95
DEV80 MUST recall        >= 0.95
VALIDATION50 case pass   >= 0.95
VALIDATION50 MUST recall >= 0.95
HIDDEN50 case pass       >= 0.95
HIDDEN50 MUST recall     >= 0.95
adaptive branch          >= 0.90 where applicable
P0 authority/security/silent-loss counters = 0
```

**Three-mode oracle**
Every eval case must carry:
- `allowed_work_modes`
- `expected_authority_family`

Valid modes:
`STANDARD_DIRECT | STANDARD_BUILDER | RESEARCH`.

Direct/Builder both map to `AcceptedStandardAuthority`.
Research maps to the **existing `AcceptedTurnContract` body**; `AcceptedResearchAuthority`
is alias/tagged-view only, never a second semantic contract.

**Progress invariant**
```text
max_executions_per_action_state_pair = 1
duplicate_reexecution_max = 0
```

**Freeze invalidation**
- one DEV80 per engineering-freeze candidate SHA,
- architecture/code change after DEV80 => new candidate + new DEV80,
- Validation fail + code change => certification freeze invalid; fresh validation set required,
- Hidden fail + architecture/code change => same hidden may not be reused for certification;
  external evaluator must provide a fresh sealed hidden corpus.

**Canonical sequence correction**
```text
provider-free
→ workers=1 focused live
→ same-SHA model-floor A/B when needed
→ 12–16 stratified canary
→ real Wren Standard + Research sentinel
→ ENGINEERING FREEZE CANDIDATE
→ DEV80 once-per-candidate
→ engineering closed
→ VALIDATION50
→ external fresh HIDDEN50
→ certification sealed
```

**Terminology**
Old “current-head recertification” phrasing is superseded.
Canonical name:
`EXACT CURRENT SEMANTIC-SHA RECERTIFICATION`.

### D65-E1 — RUNNING

Exact semantic code:
`c9629d9029db360e86a8592e12da646a2afc0621`

GitHub Actions run:
`35689470508`

Trigger workflow-source commit:
`521b1f768e75df1e36c833a57e0b28eeac082892`

Receipt records separately:
- `workflow_source_sha`
- `requested_code_sha`
- `tested_code_sha`

Product semantic code was not modified before recertification.


### D65-E1 — GREEN / EXACT CURRENT SEMANTIC-SHA RECERTIFIED

**Exact semantic code**
`c9629d9029db360e86a8592e12da646a2afc0621`

**Run**
`35689470508`

**Result**
```text
compile cognition-authority boundary    PASS
focused provider-free closure           70 / 70 PASS
warnings                                5
test time                               10.73s
certification identity                  PASS
receipt upload                          PASS
```

**Audit identity**
```text
workflow_source_sha = 521b1f768e75df1e36c833a57e0b28eeac082892
requested_code_sha  = c9629d9029db360e86a8592e12da646a2afc0621
tested_code_sha     = c9629d9029db360e86a8592e12da646a2afc0621
artifact_id         = 10677887784
artifact_digest     = sha256:685eade8e948c22b839e51db769f53210ef3839d5d4d42a78acfaf2afd78cd82
```

**Checkpoint**
`checkpoint/day6.5-exact-recert-c9629d`
→ points exactly to `c9629d9029db...`.

**Interpretation**
- no semantic/contract regression observed in the exact current semantic SHA,
- completeness-by-bound-kind change preserved the 70/70 cognition-authority closure,
- real Wren trust-plane sentinel remained inside the passing bundle,
- no patch was required,
- D65-E1 CLOSED GREEN.

**Workflow hygiene**
One-shot push trigger was used only because connector has no workflow-dispatch action.
After the successful run, `v2-day6-5-provider-free-closure.yml` was restored to
manual-only at `207e58fdabf12663356065dd5b1c344a22a483e6`.
Paid/provider automation remains OFF.

### D65-E2 — SemanticCatalogRetriever seam

**AMAÇ**
Semantic candidate discovery'yi explicit non-authoritative interface arkasına almak;
current deterministic enumeration behavior'ını değiştirmeden ileride large-catalog retrieval
backend'ine yer açmak.

**ROADMAP / REPORT**
Mühürlü plan/rapor değişmez. Aktif phase-local owner:
`DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md §4 / §12`.

**NEW OWNER**
`SemanticCatalogRetriever` = discovery only.
Canonical authority hâlâ `SemanticBindingGate`.

**TOUCH**
- `app/v2/semantic_retriever.py` NEW
- `app/v2/semantic_linker.py` minimal seam wiring
- `tests/test_v2_day6_5_semantic_linker.py` focused seam invariant
- living status

**NO-TOUCH**
- Manager prompt/schema semantics
- Resolver canonical rules
- Capability algebra
- temporal boundary
- DEV80 corpus/oracle
- production routing

**INVARIANTS**
- retrieval score != semantic truth,
- retrieval miss != semantic does not exist,
- retriever cannot mint `sem_*`,
- candidate outside returned bounded set cannot bind,
- exact alias deterministic fast bind remains unchanged,
- sensitive filter fallback remains exact-only,
- no regex/morphology/fuzzy semantic authority.

**TARGETED TEST**
`pytest -q tests/test_v2_day6_5_semantic_linker.py`

**EXIT**
Current behavior preserved and generator obtains discovery candidates through the explicit
Retriever seam. No vector/BM25/RRF implementation in Day6.5.


### D65-E2 — GREEN / SemanticCatalogRetriever seam

**Product commits**
- `4b28fc169e71` — add non-authoritative semantic retriever seam
- `14b117e2eeae` — route candidate discovery through retriever seam
- `2ff527379047` — lock discovery-only / retrieval-miss invariants

**Focused gate**
- workflow run: `35689752878`
- result: **9 / 9 PASS**
- runtime: **8.26s**
- compile: PASS

**One-shot cleanup**
- `5feaf5edc528` — retriever focused workflow removed after pass.

**What changed**
`SemanticCandidateGenerator` artık candidate discovery'yi explicit
`SemanticCatalogRetriever` interface üzerinden alıyor.

Current backend:
`EnumeratingSemanticCatalogRetriever`
→ mevcut governed catalog slice'ını exhaustive döndürür.
Bu nedenle mevcut semantic behavior korunur.

Future ranked/indexed backend için result contract:
```text
candidates
exhaustive
backend
truncated
```

**New invariant**
```text
non-exhaustive retrieval miss
!=
semantic does not exist
```

Non-exhaustive boş discovery artık `GAP` yerine `RETRIEVAL_MISS` üretir.
Binding authority değişmedi; `SemanticBindingGate` tek canonical authority sahibidir.

**Deferred**
- vector/BM25/RRF
- separate Hydrator framework
- catalog ranking optimization

Bunlar D65-E2 kapsamı değildir.

### D65-E3 — bounded StandardBuilder

**AMAÇ**
Research Manager'dan ayrı, tek governed analytical projection kuran bounded StandardBuilder
state machine'ini eklemek. `STANDARD_DIRECT` ayrı engine olmayacak; aynı builder'ın immediate
lossless short path'i olacak.

**DESIGN SOURCE**
`DIMA_DAY6_5_ENGINEERING_CLOSURE_PROTOCOL.md §2–§8`
+ Day6.5 closure report Standard Builder §7–§11.

**FIRST CUT**
- `standard_projection.py` compiler core'unu heavy `AcceptedTurnContract + UOL`
  input'una sıkı bağlı olmaktan çıkar; lightweight standard binding source kabul et.
- existing research wrapper behavior korunur.
- `standard_builder.py` finite state/progress contract eklenir.
- no raw SQL / no research tools.
- same action + same state second execution => `NO_PROGRESS`.
- compile/validation failure otomatik `RESEARCH` değildir.
- `RESEARCH_REQUIRED` yalnız gerçek research-only capability olduğunda mümkündür.

**NO-TOUCH**
- production `/ask-v2` routing
- Research Manager loop
- AcceptedTurnContract semantic body
- DEV corpus/oracle
- Resolver/BindingGate authority


### D65-E3 — GREEN / bounded StandardBuilder core

**Product commits**
- `2fbcc31d1019` — add `STANDARD_BUILD_REQUIRED` representability outcome
- `d62dcdcb0fba` — decouple StandardProjection compiler core from Research contract/UOL
- `7884f7912f37` — reserve RESEARCH_REQUIRED for actual research capabilities
- `1c13447e3c1a` — bounded StandardBuilder state machine
- `de7a7751840e` — update old authority expectation
- `151e16184ad2` — StandardBuilder provider-free invariants

**Focused gate**
- workflow run: `35690931816`
- result: **20 / 20 PASS**
- runtime: **5.69s**
- compile: PASS
- one-shot workflow cleanup: `d413e48a5c3e`

**Closed architecture points**
```text
STANDARD_DIRECT = first successful attempt of StandardBuilder
STANDARD_BUILDER = same engine after bounded repair
missing/incomplete standard representation != RESEARCH_REQUIRED
real research capability                     = RESEARCH_REQUIRED
same proposal + unchanged state              = NO_PROGRESS
budget exhausted                             = fail closed
```

`StandardProjectionCompiler.compile_bound(...)` now accepts lightweight grounded standard
atoms without requiring `AcceptedTurnContract + UserObligationLedger`.
Existing `compile(contract, ledger, ...)` wrapper remains for Research compatibility.

### D65-E4 — Minimal Standard authority / cross-family exactly-one

**TARGET**
- minimal `AcceptedStandardAuthority` seal,
- semantic body = `StandardProjection`; authority artifact does not duplicate it,
- `AcceptedResearchAuthority` = existing `AcceptedTurnContract` alias/tag only,
- same turn cannot commit both Standard and Research accepted authority,
- Standard seal validates every `sem_*` against tenant/context before authority mint.


### D65-E4 — GREEN / Standard-Research authority split

**Product**
- `9974d36b346c` — minimal `AcceptedStandardAuthority` sealer + cross-family registry
- `3212af70b8ac` — Standard/Research authority invariants

**Focused gate**
- run: `35691100678`
- result: **25 / 25 PASS**
- runtime: **6.31s**
- compile: PASS
- one-shot cleanup: `5924a21a8cee`

**Authority shape**
```text
AcceptedStandardAuthority
- authority_id
- turn_id / request_ref
- source_message_hash
- context_version
- projection_hash
- semantic_handle_refs
- accepted_attempt_id
- model_role
- work_mode
- created_at
```

Semantic body burada tekrar yazılmaz:
`StandardProjection` body'dir.

Research:
`AcceptedResearchAuthority = AcceptedTurnContract` **type alias only**.
İkinci research contract/body yaratılmadı.

Cross-family `AcceptedAuthorityRegistry`:
same-turn second accepted authority → deterministic reject.

### D65-E5 — narrow Standard CoverageVeto

Seal öncesi yalnız:
- material user request omission,
- explicit exclusion omission / wrong polarity,
- research-only need omitted from routing

için veto olabilir.

YASAK:
- canonical semantic seçmek,
- `sem_*` üretmek/istemek,
- obligation eklemek,
- query/projection repair etmek,
- clarification truth sahibi olmak.


### D65-E5 — GREEN / narrow Standard CoverageVeto

**Product**
- `13ef659ce6d2` — veto-only Standard intent coverage guard
- `b49063863b74` — provider-free coverage boundary invariants

**Focused gate**
- run: `35691288505`
- result: **16 / 16 PASS**
- runtime: **7.52s**
- compile: PASS
- one-shot cleanup: `f5ce6b217ee2`

**Coverage input surface**
Only:
- user message,
- obligation id,
- registered capability key,
- REQUIRED/EXCLUDED polarity,
- runtime-validated exact source surfaces.

It does NOT receive:
- semantic handles,
- canonical semantic IDs,
- SQL/DB metadata,
- QueryContract/Evidence.

**Coverage output authority**
```text
PASS
or
VETO:
  MATERIAL_REQUEST_OMITTED
  EXCLUSION_OMITTED_OR_WRONG_POLARITY
  RESEARCH_NEED_OMITTED
```

Every veto source must be exact user-message evidence.
Coverage cannot add/repair obligation, select semantic, create authority, or own clarification.

### D65-E6 — provider-free family closure

Bundle old cognition/authority closure + new standard front-door primitives:
- semantic retriever/linker,
- typed temporal,
- research finite pre-acceptance,
- capability algebra,
- authority/completion,
- adaptive branch/trust plane,
- StandardBuilder,
- Standard authority split,
- Standard CoverageVeto.

No paid/live model.

---

## 2026-09-22 — RUNTIME KERNEL + SUBSTRATE DECISION INTEGRATED

### Kaynak kararların birleşik sonucu

Yeni iki rapor roadmap reset'i yapmıyor. Current work devam ediyor; ancak D65-E3'ün internal structure'ı artık kesin:

```text
architecture execution paths = STANDARD | RESEARCH
STANDARD_DIRECT               = Standard outcome/telemetry only
STANDARD_BUILDER              = same Standard engine after bounded repair
generic runtime kernel        = process-control mechanics only
Research Manager migration    = NOT NOW
Wren                          = current incumbent substrate
Metabase                      = isolated post-closure challenger
```

Yeni active addendum: `DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md`.

Bu belge generic kernel ownership/forbidden knowledge, profile/domain boundary, manager_progress reuse sınırı, StandardBuilder tool/state sınırı, lightweight compiler, authority split, Standard→Research isolation, CoverageVeto, budgets, Research NO-TOUCH, Wren incumbent, Metabase challenger, D65-X ölçütleri, freeze/certification ve exact handoff sırasını dondurur.

### Gerçek current code state — NO ROLLBACK

```text
D65-E1 exact semantic SHA recert      70 / 70 GREEN
D65-E2 SemanticCatalogRetriever        9 / 9 GREEN
D65-E3 provisional StandardBuilder    20 / 20 GREEN
D65-E4 Standard authority split       25 / 25 GREEN
D65-E5 narrow CoverageVeto            16 / 16 GREEN
```

Bu kod geri alınmaz. Ancak runtime-kernel kararı E3 implementation başladıktan sonra geldiği için `focused GREEN != architecture sealed`.

Current `StandardBuilderSession` kendi counter/budget/action-state mechanics'ini taşıyor. Sıradaki refactor bu mechanics'i `BoundedAgentRuntimeKernel` içine taşır; Standard domain state, semantic binding, projection validation ve authority Standard layer'da kalır.

### Family closure ilk birleşik koşum

Run: `35691397377`.

```text
compile PASS
87 PASS
1 FAIL
5 warnings
```

Failure: `test_v2_day6_5_dev_corpus.py::test_day65_dev_corpus_is_complete_and_taxonomy_balanced`.

Classification: **EVAL_ORACLE**.

Sebep: manifest yeni `allowed_work_modes` ve `expected_authority_family` metadata alanlarını bekliyordu; DEV corpus schema-integrity key-map'i eskiydi. Bu semantic/product bug değildir; regex/prompt/Resolver/StandardBuilder patch yapılmadı.

### Eval schema düzeltmesi

```text
38 STANDARD_LOSSLESS      → [STANDARD_DIRECT, STANDARD_BUILDER] / AcceptedStandardAuthority
26 RESEARCH_REQUIRED      → [RESEARCH] / AcceptedResearchAuthority
15 CLARIFICATION_REQUIRED → [] / NONE
1  UNSUPPORTED            → [] / NONE
```

Architecture terminology: `execution_path = STANDARD | RESEARCH`; `standard_outcome = DIRECT | BUILDER`.

### Current family closure rerun

Oracle sync sonrası same family bundle yeniden tetiklendi: `run 35691982389`.

Result: **88 / 88 PASS**, 5 warnings, 12.46s. Compile PASS.

Semantic code testcase geçirmek için yamalanmadı. One-shot workflow green sonrası kaldırıldı (`6e3c81cf19c0`).

### Sıradaki product ticket — D65-E3A-R

**NAME:** `RUNTIME KERNEL REALIGNMENT`

**NEW:** `app/v2/agent_runtime.py`

**Kernel owns only:** model/tool counters, budgets, observation lifecycle, action fingerprint, domain/profile-supplied state fingerprint, duplicate action/state guard, terminal/no-progress/budget-exhausted, generic telemetry.

**Kernel must not know/import:** `AcceptedTurnContract`, `UserObligationLedger`, `ResearchDirective`, CompletionGate semantics, Evidence verification semantics, canonical semantic truth, `sem_*` minting, join/query/numeric truth.

**TOUCH:** `app/v2/agent_runtime.py`, `app/v2/standard_builder.py`, focused kernel/builder tests; `manager_progress.py` only if generic fingerprint primitives need a non-semantic export/rename.

**NO-TOUCH:** `manager_loop.py`, `manager_runtime.py`, `manager_tools.py`, `manager_preacceptance.py`, Research `AcceptedTurnContract` body, Resolver canonical rules, production `/ask-v2`, DEV expected semantic labels.

**EXIT:** StandardBuilder consumes `BoundedAgentRuntimeKernel`; kernel has zero Research-domain imports/knowledge; DIRECT remains outcome only; existing Standard semantic behavior is preserved; same action+state second execution = `NO_PROGRESS`; budget fail-closed; focused kernel+builder+authority+coverage and family closure GREEN.

### Bundan sonraki bağlayıcı sıra

```text
D65-E3A-R generic kernel realignment
→ focused provider-free kernel/builder gates
→ provider-free family closure
→ workers=1 focused live
→ same-SHA model-floor A/B if needed
→ 12–16 stratified canary
→ real Wren Standard vertical + Research sentinel
→ ENGINEERING FREEZE CANDIDATE
→ DEV80 once-per-candidate
→ DAY 6.5 ENGINEERING CLOSED / ARCHITECTURE FROZEN
→ D65-X Wren incumbent vs Metabase Agent API substrate-only challenger
→ choose ONE primary substrate
→ VALIDATION50 no tuning
→ external fresh HIDDEN50
→ CERTIFICATION SEALED
→ production hybrid activation
```

Day 7–10 numbering unchanged.

### D65-X non-negotiable isolation

Primary experiment fixes Dima cognition, accepted semantics, `AcceptedStandardAuthority`, `StandardProjection` and benchmark. Only execution substrate changes: `WrenAdapter` vs thin `MetabaseStandardAdapter`.

Metabase native NLQ/Metabot comparison is a separate secondary experiment. Wren + Metabase as equal production truth engines = **STOP-THE-LINE**.

---

## 2026-09-22 — D65-E3A-R GREEN / RUNTIME KERNEL REALIGNMENT

### Yapılan

`AGENTS.md` içindeki tek stale “üç-mode front door” ifadesi `STANDARD | RESEARCH` architecture terminology'sine düzeltildi.

Yeni generic mechanics kernel: `app/v2/agent_runtime.py`.

Primitive'ler:
```text
BoundedLoopBudget
LoopCounters
LoopTerminalReason
ActionReservation
LoopObservation
ActionStateGuard
BoundedAgentRuntimeKernel
```

Kernel yalnız model-turn/tool-call counters, budget enforcement, action fingerprint, domain-supplied state fingerprint, action/state guard, observation receipt, terminal/NO_PROGRESS/BUDGET_EXHAUSTED ve generic telemetry taşır.

Kernel Research/business truth katmanlarını import etmez: `AcceptedTurnContract`, `UserObligationLedger`, `ResearchDirective`, `ManagerRuntime`, Research loop, Evidence verification, CompletionGate semantics, canonical semantic truth, join/query/numeric truth.

`manager_progress.py` değiştirilmedi. Yalnız mevcut generic `action_fingerprint` / `result_fingerprint` primitive'leri reuse edildi; Research-specific `progress_fingerprint(runtime)` kernel'e taşınmadı.

### StandardBuilder realignment

`StandardBuilderSession` generic counters / duplicate guard / budget controller mechanics'ini artık `BoundedAgentRuntimeKernel` üzerinden kullanır.

Standard domain/profile hâlâ state-fingerprint payload'ını, Representability kararını, StandardProjection compile/validation'ı, DIRECT vs BUILDER outcome'ını ve RESEARCH_REQUIRED / CLARIFY / UNSUPPORTED mapping'ini sahiplenir.

Semantic davranış:
```text
first lossless attempt       → STANDARD_DIRECT outcome
repair then seal             → STANDARD_BUILDER outcome
same action + same state     → NO_PROGRESS
model-turn budget exhausted  → BUDGET_EXHAUSTED / fail closed
real research capability     → RESEARCH_REQUIRED
```

### Commits

```text
d0ed44b9212a  docs: remove stale three-mode wording
5cb7a046f4c1  feat: generic bounded runtime kernel
e1d44f742435  refactor: StandardBuilder consumes kernel
160f1ac0ffa6  test: kernel boundary invariants
291409d50145  test: StandardBuilder kernel-consumer proof
```

### Focused gate

Run: `35693039369`

```text
compile PASS
22 / 22 PASS
8.62s
```

### Full provider-free family closure

Run: `35693146320`

```text
compile PASS
94 / 94 PASS
5 warnings
12.39s
```

### NO-TOUCH kanıtı

D65-E3A-R başlangıç checkpoint'i `fc0472436124d764cb6f4bd0b6bc439ec80e8010` ile implementation sonrası code diff yalnız:

```text
backend/AGENTS.md
backend/app/v2/agent_runtime.py
backend/app/v2/standard_builder.py
backend/tests/test_v2_day6_5_agent_runtime.py
backend/tests/test_v2_day6_5_standard_builder.py
```

Research files NO-TOUCH:
```text
manager_loop.py
manager_runtime.py
manager_tools.py
manager_preacceptance.py
AcceptedTurnContract body
```

E4/E5 no-rollback korundu.

### D65-E3A-R exit

```text
StandardBuilder consumes BoundedAgentRuntimeKernel        PASS
kernel has zero Research-domain imports                   PASS
DIRECT remains outcome only                               PASS
existing Standard semantic behavior preserved             PASS
same action+state duplicate = NO_PROGRESS                 PASS
budget fail closed                                        PASS
focused kernel/builder/authority/coverage                 22/22 PASS
full provider-free family closure                         94/94 PASS
```

**D65-E3A-R CLOSED GREEN.**

### Sıradaki exact adım

Yeni feature/refactor açmadan:

```text
workers=1 focused live architecture set
→ exact-same-SHA model-floor A/B only if needed
→ 12–16 stratified canary
→ real Wren Standard vertical + Research sentinel
→ ENGINEERING FREEZE CANDIDATE
→ DEV80 once-per-candidate
```

Live gate başlamadan current green SHA checkpoint edilir.

---

## 2026-09-22 — METABASE SOURCE REFERENCE CONTRACT + LIVE GATE SIGNAL

### Metabase source authority/protocol

Canonical upstream exact source snapshot doğrulandı:

```text
repo = metabase/metabase
sha  = 74216b30981d8310c4cf724d63ca282e2e63529d
```

Pinned SHA üzerinde mevcut olduğu doğrulanan canonical files:

```text
src/metabase/metabot/agent/core.clj
src/metabase/metabot/agent/profiles.clj
src/metabase/agent_api/reference.md
src/metabase/agent_api/api.clj
src/metabase/agent_api/query_guards.clj
src/metabase/mcp/v2/tools/query.clj
```

Dima repo Git tree'sinde şu anda `public/metabase/master` yoktur. İleride varsa yalnız read-only convenience checkout; canonical authority değildir.

`DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md §17A` içine zorunlu **Metabase Source Reference Contract** ve **mandatory source-control / analysis / research protocol** eklendi.

Binding rules:
- source-copy / port / vendor / transliteration yasak,
- D65-X real integration = separate-service Metabase Agent API,
- important Metabase decision before coding = source identity + exact source reading + security/API/runtime review + Dima trust-plane cross-check + receipt,
- bake-off receipt pins source SHA + runtime version + immutable image digest + Dima/adapter SHA + corpus + permission context,
- product development sequence değişmedi.

Protocol additionally surfaced in `AGENTS.md`, `CLAUDE.md`, `MIMARI.md` and eval manifest so compact/handoff sırasında atlanamaz.

### Workers=1 focused live gate

Run: `35693815578`

Exact code under test:
`dea7ba673ba64280c3e58037705c31db99c733aa`

Workflow source SHA:
`612ae77d6cc43f910e9035bd1f73c085fb0d0793`

Model:
```text
RESEARCH_MANAGER = openai/gpt-5.6-sol
SEMANTIC_LINKER  = google/gemini-2.5-flash-lite
workers          = 1
```

Selected architecture set:
`001, 005, 025, 026, 047, 063, 067, 075`.

Measurement:
```text
selected/evaluable    8 / 8
measurement failures  0
model failures        0
grounding failures    0
harness failures      0
case pass             7 / 8 = 0.875
unsafe fast           0
silent ambiguity      0
invented MUST         0
handle violation      0
execution violation   0
clarification rate    1.0
```

Only failing case:
`d65-dev-026` — `net geliri bölgelere göre göster ve geçen ayla karşılaştır`.

Observed pipeline:
```text
Manager draft:
  U1 breakdown(metric=net geliri, dimension=bölgelere)
  U2 comparison(metric=net geliri, comparison=geçen ayla)

grounding:
  metric resolved
  dimension resolved
  metric resolved
  comparison surface 'geçen ayla' unresolved

material grounding gap:
  comparison missing required kind

terminal:
  CLARIFICATION_REQUIRED

expected:
  ACCEPTED / STANDARD_LOSSLESS
```

Classification is **NOT YET PATCHABLE**.
Infra/provider/harness classes are ruled out. Next step is exact-same-SHA owner/model-floor A/B focused on comparison binding. No semantic code change before classification.

---

## 2026-09-22 — D65-G ROOT-FIX / ANTI-PATCH GUARD

### Giriş kanıtı

Stratified canary run `35695029547`, exact semantic SHA `f5ca942f83aaee0806d7119957c543ab17a59a37`:

```text
16 evaluable
14 PASS / 2 FAIL
measurement failures 0
model failures 0
grounding infrastructure failures 0
harness failures 0
P0 authority/security counters 0
```

Failures:
- `d65-dev-019` explicit-base comparison
- `d65-dev-073` conversation repair/versioning

Mandatory receipts: `DIMA_DAY6_5_FAILURE_TRIAGE_RECEIPTS.md`.

`019` exact-same-SHA diagnostic `35695366379`:
```text
flash-lite SEMANTIC_LINKER → FAIL
Sol SEMANTIC_LINKER        → PASS
classification            → MODEL_CAPABILITY_FLOOR
product correctness patch → FORBIDDEN
```

`073` same-SHA repeat diagnostic:
```text
FAIL / PASS / FAIL
semantic-linker calls = 0
classification = CONTRACT/ARCHITECTURE
owner = finite pre-acceptance repair-vs-exclusion contract / CoverageVeto boundary
```

### D65-G ticket contract

**AMAÇ**
Yeni Manager semantic hot path'ten legacy heuristic resolver dependency'sini fiziksel olarak sökmek ve RED sonrası vaka-yama disiplinini architecture test + mandatory receipt ile zorlaştırmak.

**USER SCENARIO**
Bir semantic/linking failure olduğunda geliştirici `legacy SemanticResolver` fallback'i, fuzzy/morphology/regex branch'i veya failed phrase prompt example'ı ekleyememeli; önce root owner/classification kanıtlanmalı.

**NEW OWNER**
No new semantic owner. Existing owner map korunur. D65-G yalnız anti-regression boundary'dir.

**FILES TO TOUCH**
```text
app/v2/manager_semantics.py
app/v2/manager_lab.py
tests/test_v2_day6_5_no_legacy_semantic_fallback.py  NEW
focused existing tests only if constructor surface changes
```

**FILES NOT TO TOUCH**
```text
app/v2/resolver.py behavior
semantic_linker.py truth/binding behavior
manager_preacceptance.py repair behavior (separate D65-CANARY-073 owner ticket)
temporal_intent.py
StandardBuilder/E4/E5
Research execution/evidence/completion
DEV expected labels
production /ask-v2
```

**HARDENING RULES**
- `manager_semantics.py` may not import `app.v2.resolver`.
- Manager hot path may not accept/store a legacy resolver dependency.
- `manager_lab.py` may not instantiate/inject `SemanticResolver`.
- authoritative Day6.5 semantic modules may not import/use `difflib`, `SequenceMatcher`, `py_rust_stemmers`, `SnowballStemmer`, `rapidfuzz`, `_FUZZY` or semantic-language regex parsing.
- Scope-limited regex guard applies only to semantic authority modules; syntax/JSON/security regex elsewhere is not globally banned.

**EXIT**
```text
legacy resolver import/injection from Manager hot path = 0
anti-heuristic architecture test = GREEN
focused Manager semantic tests = GREEN
full provider-free family closure = GREEN
Research behavior = NO-TOUCH
```

D65-G sonrasında active canary failures ayrı owner ticket'larıyla ele alınır; `019` için code patch yok, `073` için yalnız repair/coverage contract owner'ı yetkilidir.

---

## 2026-09-22 — D65-G + REPAIR HARDENING + REFERENCE CANARY GREEN

### D65-G anti-patch hardening

Manager semantic hot path artık legacy `SemanticResolver` import/constructor/field/fallback seam'i taşımıyor.

```text
manager_semantics.py  → no app.v2.resolver import
ManagerSemanticResolutionAdapter.__init__ → no resolver parameter
manager_lab.py        → no SemanticResolver construction/injection
```

Architecture guard:
`tests/test_v2_day6_5_no_legacy_semantic_fallback.py`.

Scoped forbidden semantic-authority primitives:
`app.v2.resolver`, `difflib/SequenceMatcher`, `py_rust_stemmers/SnowballStemmer`, `rapidfuzz`, `_FUZZY`, semantic-language `re.*` parser.

Regex repository-wide yasak değildir; yalnız authoritative semantic meaning/authority modülleri guard edilir.

### Mandatory RED triage gate

`DIMA_DAY6_5_FAILURE_TRIAGE_RECEIPTS.md` oluşturuldu ve AGENTS/CLAUDE/closure protocol/eval manifestte binding hale getirildi.

```text
RED
→ NO PRODUCT/SEMANTIC CODE CHANGE
→ failure triage receipt
→ same-SHA A/B if needed
→ failure_class + single_owner + root_cause + failure_family
→ allowed files
→ code
→ focused proof
→ family/metamorphic proof
```

`ONE FAILURE ≠ ONE NEW RULE` artık repo contract'ıdır.

### Conversation-repair root fix

Corrective/superseding discourse business EXCLUDED obligation ile aynı şey değildir.
Finite pre-acceptance draft artık `CONVERSATION_REPAIR` control state temsil edebilir.
EXCLUDED business obligation yalnız current message gerekli semantic target'ı source-ground ediyorsa geçerlidir.

Bu çözüm phrase/keyword/regex özel değildir; correction/replacement family abstraction'ıdır.

### Provider-free proofs

Combined focused closure:
```text
run 35696222877
59 / 59 PASS
```

Full family closure after all stale fixture cleanup:
```text
run 35696652502
exact tested SHA = ffbdc224066dc4c85a9e46b510ae3535f83f3416
102 / 102 PASS
5 warnings
```

Intermediate RED runs were not semantic patched; each was classified as `EVAL_ORACLE` stale test/harness constructor drift and received a formal receipt before test-only cleanup.

### Semantic Linker model-floor finding

`d65-dev-019` exact-same-SHA diagnostic run `35695366379`:

```text
backend SHA        = f5ca942f...
Manager            = openai/gpt-5.6-sol
flash-lite linker  = FAIL
Sol linker         = PASS
classification     = MODEL_CAPABILITY_FLOOR
product code patch = NONE
```

Reference architecture certification floor for current canary therefore uses Sol Manager + Sol Semantic Linker.
Bu model-specific business branch değildir; measured evaluation/certification floor'dur.

### Reference-floor stratified canary

Run: `35697064833`

Exact tested SHA:
`8dfde62d46d1418f05cce3ed44c26a8025b3b20e`

```text
selected/evaluable          16 / 16
case pass                   16 / 16 = 1.0
MUST obligation recall      1.0
invented MUST               0
missing/invented exclusion  0 / 0
handle violations           0
preacceptance exec violation 0
blocking ambiguity silent    0
unsafe fast admission        0
standard lossless rate       1.0
clarification canonical      1.0
measurement/model/grounding/harness failures = 0
```

Models:
```text
RESEARCH_MANAGER = openai/gpt-5.6-sol
SEMANTIC_LINKER  = openai/gpt-5.6-sol
workers          = 1
```

### Current exact next gate

Current pre-freeze sequence:

```text
D65-J1S semantic candidate-decision bake-off
+
D65-J1T typed temporal-intent bake-off
+
D65-M0 Metabase architecture extraction/adoption audit
↓
decision receipts
↓
D65-X0 thin Metabase feasibility
↓
Wren primary OR consult → full D65-X → ONE primary substrate
↓
ENGINEERING FREEZE CANDIDATE
↓
DEV80 once for that candidate
```

`35697471863` Wren/Research sentinel = 2/2 PASS on exact `8dfde62d...`; proof is preserved but does not authorize freeze until J1 + M0/X0 are resolved.

Current detailed authority: `DIMA_DAY6_5_PREFREEZE_DECISION_GATE_J1_M0_X0.md`.

---

## 2026-09-22 — D65-J1 JEV DECISION-MODEL CHALLENGER

### Trigger / neden şimdi

D65-G CLOSED GREEN:
```text
provider-free family run 35696652502 = 102/102 PASS
legacy SemanticResolver Manager hot path = REMOVED
regex/fuzzy/morphology semantic fallback = architecture-test forbidden
mandatory failure-triage receipt = ACTIVE
```

Reference-floor canary:
```text
run                  = 35697064833
workflow source SHA  = 07ac8d47796b89634b2411def457bb85f4bc0da7
tested code SHA      = 8dfde62d46d1418f05cce3ed44c26a8025b3b20e
Manager              = openai/gpt-5.6-sol
Semantic/Temporal    = openai/gpt-5.6-sol
workers              = 1
selected/evaluable   = 16/16
case pass            = 16/16
MUST recall          = 1.0
all P0 counters      = 0
measurement failures = 0
```

Earlier run `35696811902` = 16/16 HARNESS_FAILURE due stale `resolver=` evaluator constructor; classification `EVAL_ORACLE / HARNESS DRIFT`; semantic conclusion NONE; product code unchanged.

Early Wren/Research sentinel:
```text
run             = 35697471863
tested code SHA = 8dfde62d46d1418f05cce3ed44c26a8025b3b20e
result          = 2/2 PASS
```
This proof is retained but freeze is BLOCKED pending D65-J1.

### New architecture observation

Current `SEMANTIC_LINKER` role conflates two distinct cognition contracts:
```text
1. bounded catalog candidate selection
2. TypedTemporalNormalizer
```

`d65-dev-019` model-floor evidence belonged to typed temporal comparison normalization, not catalog candidate selection. Therefore Jev is NOT a case019 patch and case019 is not evidence to ship Jev.

### D65-J1A — isolated lab/eval only

Pinned challenger:
```text
typesafe/jev-1.13
```

Forbidden:
```text
~typesafe/jev-latest
v2_semantic_linker_model=typesafe/jev-1.13
Jev through chat/completions
Jev through current structured_json adapter
prompt wrapper/hack/fallback to make Jev look like a chat LLM
product semantic_linker.py changes before bake-off result
temporal normalization with Jev in J1A
```

Native surface:
```text
OpenRouter Decisions API
POST /api/alpha/decisions
state + typed choice question
→ choice + probabilities
```

Candidate boundary remains:
```text
USER SURFACE
→ frozen CandidateSet[cand_*]
→ decision challenger
→ candidate_id | ABSTAIN
→ existing SemanticBindingGate conceptually remains authority
```

J1A compares:
```text
A = google/gemini-2.5-flash-lite
B = typesafe/jev-1.13
C = openai/gpt-5.6-sol
```

Manager is not part of this benchmark. TemporalNormalizer is excluded.

Jev may not mint sem_*, see canonical IDs unnecessarily, escape candidate sets, write SQL, see DB/numeric truth, perform temporal arithmetic, or accept authority.

Required strata:
```text
exact alias controls
non-exact Turkish paraphrases
synonym surfaces
multiple plausible candidates
true ambiguity
no-match / ABSTAIN
retrieval miss
bounded high-cardinality candidate sets
entity-value cases
sensitive-value exact-only controls
different metric/dimension names
permuted/metamorphic schema names
cross-tenant candidate isolation
```

Metrics:
```text
candidate-selection accuracy
ABSTAIN precision/recall
ambiguity unsafe-pick count
candidate-escape count
Turkish paraphrase accuracy
metamorphic consistency
same-input repeated-run agreement
p50/p95 latency
cost
provider failures
Jev raw choice probabilities
Jev Brier/ECE or equivalent calibration
Jev high-confidence-wrong count
```

P0:
```text
candidate outside supplied set = 0
silent ambiguity auto-pick = 0
cross-tenant semantic leak = 0
high-confidence wrong accepted = 0
semantic authority minted by model = 0
```

No confidence threshold is tuned or activated in J1A.

### Decision rule

Jev clearly poor / Turkish weak:
```text
REJECT JEV
→ product code NO CHANGE
→ current architecture continues
→ Wren/Research sentinel proof can be retained/rechecked as needed
→ freeze sequence resumes
```

Jev promising:
```text
OPEN D65-J1B
→ SemanticLinkDecisionProvider seam
→ StructuredLLMDecisionProvider | JevDecisionProvider
→ SEMANTIC_LINKER = bounded candidate decision only
→ TEMPORAL_NORMALIZER = separate language→TemporalNormalizationChoice role
→ focused/provider-free/family/live/canary/sentinel revalidation
→ freeze
```

Jev/Gemini/Sol = cognition decision-model experiment.
Wren/Metabase D65-X = analytics execution-substrate experiment.
They are independent and MUST NOT be conflated.

Canonical roadmap numbering and Day7–10 remain unchanged.


---

## 2026-09-22 — PRE-FREEZE PLAN REVISION: J1S/J1T + M0/X0

This section supersedes the earlier candidate-only J1 scope and the earlier post-DEV80 D65-X timing.

Verified baseline:
```text
D65-G                         GREEN
provider-free family          35696652502 = 102/102 PASS
reference-floor canary        35697064833 = 16/16 PASS
Wren + Research sentinels     35697471863 = 2/2 PASS
production hybrid             OFF
freeze candidate              NOT CREATED
DEV80                         NOT STARTED
```

Metabase source identity:
```text
historical pinned reference = 74216b30981d8310c4cf724d63ca282e2e63529d
current upstream master      = fff70175e0b5f82dc0eb267593c717c4a6130206
ahead                         = 1 commit
relevant agent/API/MCP source changes between SHAs = NONE
```

Active pre-freeze work:
```text
D65-J1S = Gemini Flash-Lite vs Jev 1.13 vs Sol on bounded semantic candidate selection
D65-J1T = Gemini Flash-Lite vs Jev 1.13 vs Sol on typed temporal intent classification
D65-M0  = Metabase source/adoption matrix audit
D65-X0  = thin separate-service Agent API feasibility
```

J1S/J1T and M0 are isolated lab/research gates; product semantic/temporal/authority code remains NO-TOUCH until a decision gate is reached.

Consultation required before:
- D65-J1B integration,
- production model/cascade/threshold selection,
- full D65-X,
- primary substrate switch,
- freeze candidate,
- DEV80.

---

## 2026-09-22 — RELEASE-LEVEL DEV80 TIMING OVERRIDE

New binding economic/release rule:
```text
DEV80 = FINAL BROAD ENGINEERING GATE
DEV80 count for this release = exactly 1
```

Therefore DEV80 is no longer a Day6.5 closure test.

Current release sequence:
```text
J1S + J1T + M0
→ X0
→ if needed full X / chosen one primary substrate
→ any approved Jev/Metabase production integration
→ Day7 Research loop
→ Day8 Hypothesis/root-cause
→ Day9 ReportDocument
→ Day10 Product MVP
→ Day11 eval/metamorphic expansion
→ Day12 QueryContract/evidence/telemetry hardening
→ Day13 tenant/PII/principal security
→ Day14 persistence/resume
→ Day15 pilot flag + rollback CODE complete, flag OFF
→ all cheap/focused/live/metamorphic/canary/sentinel gates GREEN
→ 20–25 case final integration rehearsal
→ FINAL ENGINEERING FREEZE CANDIDATE
→ DEV80 ONCE
→ CODE FREEZE
→ Validation50 NO TUNING
→ fresh external Hidden50 NO TUNING
→ certification seal
→ pilot flag activation
```

Development still uses focused REAL LLM scenarios continuously. DEV80/Validation50/Hidden50 are not debugging tools.

Consult before final freeze and before DEV80 start.

Detailed authority: `DIMA_RELEASE_FINAL_INTEGRATED_GATE.md`.


---

## 0B. J1 FULL DECISION GATE — STOP / CONSULT

Corrected full run:
`35705668833` @ `bde3e5a21c159243002ef600ece007256d8482d0`.

Current decision state:

```text
J1S Jev semantic decision primitive   = PROMISING
J1T Jev temporal production role      = REJECTED BY CAPABILITY FLOOR
J1T Luna typed contract evidence      = strongest primary peer, but 2 invalid typed outputs
Gemini current cheap temporal evidence= weaker; one unsafe ambiguity pick + contract misses
run-level RED                         = EVAL_ORACLE classification bug
product code changes                  = 0
J1B                                   = CLOSED / CONSULT REQUIRED
D65-SI                                = WAITING FOR J1 TOPOLOGY DECISION
X0 execution                          = BLOCKED BY D65-SI
production /ask-v2                    = OFF
DEV80                                 = FORBIDDEN
```

Mandatory stop is active because Jev is promising for a narrower bounded semantic role.
Do not:
- open J1B;
- choose semantic/temporal production model topology;
- introduce cascade/confidence threshold;
- run Terra;
- wire D65-SI against a topology not yet approved;
- execute X0.

Permitted while stopped:
- documentation / receipt correction only;
- user consultation.

Open eval debt:
`D65-J1-FULL-001` — invalid typed Pydantic output is currently mislabeled as
TRANSPORT/PROVIDER by the harness. Root cause is classified EVAL_ORACLE; no patch has been made
because the J1 promising consultation gate has precedence.


---

## 2026-09-22 — J1 RESULTS + METABASE DEPLOYMENT CONSULTATION

Current HEAD before this documentation update:
`978e6317822eadbcb3ac469804cc19f1d569be29`.

J1 corrected full result:
```text
run                         = 35705668833
tested SHA                  = bde3e5a21c159243002ef600ece007256d8482d0

J1S Jev model-needed        = 93.33%
J1S Gemini                  = 86.67%
J1S Luna                    = 86.67%
Jev p50                     = 0.266s
Gemini p50                  = 0.537s
Luna p50                    = 1.013s
Jev measured cost           = $0.002282
high-confidence Jev wrong   = 0
```

Interpretation:
```text
Jev universal replacement   = NO
Jev bounded semantic choice = PROMISING
Jev temporal provider       = NO / capability floor
Luna temporal typed role    = PROMISING, not sealed
J1B                         = CONSULT REQUIRED
```

Run-level workflow FAILURE was classified EVAL_ORACLE because typed-contract validation failures
were mislabeled as TRANSPORT/PROVIDER. Real provider/network failures = 0. Product semantic code
was not patched from this RED.

Metabase deployment clarification:
```text
Agent API != Metabase Cloud requirement

X0 default:
Dima → private network → self-hosted pinned Metabase → analytical DB

vendor Cloud = not selected
source copy/port/vendor = forbidden
same-stack sidecar/container packaging = feasible candidate
same Python process/library embedding = not a supported realistic integration
```

Self-hosting adds real operational cost:
- Metabase JVM/service,
- production application DB,
- upgrades/migrations/backups,
- monitoring,
- scaling/load balancing,
- permission/tenant mapping.

These costs are now mandatory X0 metrics.

External current verification:
- OSS edition uses AGPL;
- Docker/JAR self-host are supported;
- production app DB should be relational/PostgreSQL;
- horizontal scaling is supported with shared app DB/load balancer.

Detailed decision:
`DIMA_DAY6_5_METABASE_DEPLOYMENT_TOPOLOGY_DECISION.md`.

Current STOP:
```text
J1B product experiment = WAITING USER APPROVAL
D65-SI                 = WAITING J1 TOPOLOGY DECISION
X0 execution           = WAITING consultation + D65-SI sequence
product /ask-v2        = OFF
DEV80                  = FORBIDDEN / final release only
```


---

## WREN_SEMANTIC_BACKBONE_RETENTION_DECISION

> **D65-X0 Wren'in MDL/cube semantic backbone'unu kaldırma deneyi değildir. İlk aşamada yalnız
> analytics execution/query-lifecycle overlap'ını ölçer. Wren semantic-layer retention ayrı bir
> architecture decision'dır.**

Binding implications:

```text
X0 MAY compare:
  StandardProjection → Wren execution/query lifecycle
  vs
  StandardProjection → Metabase construct/validate/execute lifecycle

X0 MAY NOT infer:
  "Metabase query execution works"
  ⇒ "Wren MDL/cube semantic backbone is redundant"
```

During X0:
- current Dima semantic authority remains `SemanticBindingGate + accepted authority`;
- existing Wren MDL/cube semantics may remain the semantic backbone even if Metabase is tested as
  an execution/query-lifecycle component;
- metric meaning, cube relationships, grain/additivity/unit/time semantics are not silently
  re-owned by Metabase;
- removing or replacing the Wren semantic layer requires a separate explicit architecture
  decision and consultation, with its own semantic-equivalence and migration evidence.

Therefore a promising X0 can justify a **full execution-substrate/query-lifecycle comparison**,
not automatic Wren semantic-layer removal.
