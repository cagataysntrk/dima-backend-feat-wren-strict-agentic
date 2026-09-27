# DIMA V1 — NİHAİ 3 FAZLI YOL HARİTASI

## 0. Nihai mimari karar

V1 boyunca artık engine seçimi yeniden açılmayacak.

```text
DIMA PRODUCT
│
├── Company Brain
│   ├── company ontology
│   ├── terminology / aliases
│   ├── entity registry
│   ├── business relationships
│   └── Metabase resource mappings
│
├── Dima Brain
│   ├── Research
│   ├── Investigation
│   ├── Evidence
│   ├── Claims
│   ├── Hypotheses
│   ├── Root Cause
│   ├── Reporting
│   └── Decision
│
├── Operating Loop
│   ├── Watch
│   ├── Signal
│   ├── Today
│   ├── Action
│   ├── Outcome
│   ├── Memory
│   └── Brief
│
└── METABASE / METABOT
    ├── query semantics
    ├── aggregation
    ├── grouping
    ├── ranking
    ├── temporal analysis
    ├── native exploration
    ├── analytical execution
    └── permissions
```

Dosyadaki temel mimari de Company Brain + Dima Brain + Operating Loop’un Metabase/Metabot native analytics üzerinde durmasını öngörüyor.

Kalıcı kural:

```text
METABASE computes.
DIMA investigates, interprets, remembers and decides.
```

Dima hiçbir aşamada ikinci:

```text
query engine
semantic analytics truth
query planner
temporal engine
ranking engine
trend/outlier engine
```

oluşturmayacak.

Wren’den kod taşınmayacak. Taşınacak olanlar yalnızca işe yarayan araştırma ve epistemik pattern’lerdir; dosyada da AcceptedTurnContract, ManagerActionSet, Adaptive Branch, HypothesisLedger, counter-evidence, discriminating test ve CompletionGate gibi fikirler bu şekilde eşleştirilmiş.

---

# FAZ 1 — BRAIN CONVERGENCE & INTELLIGENCE CLOSURE

## Amaç

Round-2’de 70.8/100 alan mevcut Metabase tabanlı Dima Brain’i V1 açısından gerçekten güvenilir hale getirmek.

Bu faz:

```text
UI fazı değildir.
Onboarding fazı değildir.
Yeni sektör motoru fazı değildir.
```

Faz 1 sonunda elimizde frontend’e güvenle verilebilecek sealed Dima Brain V1 bulunmalı. Dosyadaki Phase 1 de aynı şekilde UI geliştirmeden Research + RCA + scope + evidence motorunu kapatmayı hedefliyor.

## 1.1 Wren Research Harvest

Önce bir:

```text
WREN_RESEARCH_HARVEST_MATRIX
```

oluşturulacak.

Taşınacak kavramlar:

```text
Wren                          Dima V1
────────────────────────────────────────────────────
AcceptedTurnContract       → TurnScopeContract
Research Goal / Task split → ResearchBrief + InvestigationRequirement
ManagerActionSet           → P17 LegalActionProfile
Adaptive Branch            → P17 Investigation Branch
HypothesisLedger           → P19 Hypothesis Ledger
Counter-evidence           → Evidence relation
Discriminating Test        → P19 → P17 NextTestRequest
CompletionGate             → Product Completion Contract
Research Trace             → InvestigationTrace
```

Taşınmayacak:

```text
Wren runtime
Wren SQL/query engine
Wren semantic authority
exact-surface gating
Wren model cascade
```

---

## 1.2 P17 provider-contract reliability — P0

Round-2 `F06_M` gerçek typed provider exception verdi.

Bu tamamen kapanmalı.

LLM bundan sonra sistem kimlikleri üretmeyecek.

Model yalnız:

```text
action
target concept
reason
analytical objective
expected evidence
inspected evidence
```

önerecek.

Dima deterministic katmanı üretecek:

```text
objective_id
step_id
branch_id
task_id
scope_version
hypothesis_id
```

Provider akışı:

```text
model output
→ schema normalization
→ state-derived closed choice validation
→ max 1 bounded repair
→ valid proposal
```

Olmazsa:

```text
governed INCONCLUSIVE
```

Generic exception/500 yok.

Dosya da özellikle provider’ın machine identity üretmemesini ve malformed proposal’ın bounded normalize/repair sonrasında governed terminale gitmesini öneriyor.

---

## 1.3 TurnScopeContract + ScopeVersion

F10’un ana problemi çözülmeli.

First-class:

```text
ScopeVersion
TurnScopeContract
ScopeMutation
```

Mutation vocabulary:

```text
ADD
REMOVE
REPLACE
NARROW_ENTITY
EXPAND_ENTITY
CHANGE_PERIOD
CHANGE_METRIC
CHANGE_BREAKDOWN
RESET
```

Her:

```text
Evidence
Claim
InvestigationStep
Hypothesis
Report
Decision
```

bir `scope_version` taşımalı.

Örneğin:

```text
scope_v1
All departments

↓ "yalnız Assembly"

scope_v2
Assembly only
```

`scope_v1` Evidence geçmişte kalır.

Şuna dönüşemez:

```text
current Evidence for scope_v2
```

Bu mekanizma dosyada Conversation Scope Engine’in temel görevi olarak tarif edilmiş.

---

## 1.4 AnalyticalRequestContract — ama ikinci query planner DEĞİL

Bu noktada dosyadaki öneriyi kabul ediyorum fakat sınırını sertleştiriyorum.

Contract:

```text
target metric refs
dimensions
time scope
filters
comparison intent
ranking basis
requested grain
requested output surfaces
scope version
```

taşıyabilir.

Ancak:

```text
aggregation implementation
SQL
MBQL
query plan
join plan
temporal computation
```

Dima’nın işi değildir.

Akış:

```text
User contract
→ AnalyticalRequestContract
→ Metabot native planning
→ native query candidate
→ request-invariant check
→ execute
```

Check yalnız şu seviyede:

```text
June requested → June preserved?
Assembly only → Assembly preserved?
rank by downtime delta → same target preserved?
```

olacak.

Dima:

> “Bu SQL doğru mu?”

diye ikinci query validator olmayacak.

Dima:

> “Kabul edilmiş kullanıcı isteğinin maddi scope’u kaybolmuş mu?”

diyecek.

Bu sınır CI’da architecture invariant olarak korunmalı.

Dima’nın request-invariant kontrolü yalnız:

```text
metric refs
dimensions
time scope
filters
comparison intent
ranking basis
requested grain
requested output surfaces
scope version
```

üzerinde çalışabilir.

Architecture test açıkça şunları yasaklamalı:

```text
SQL parsing / scoring / rewriting
MBQL parsing / scoring / rewriting
join-plan validation
aggregation-implementation validation
temporal-computation validation
query-optimality judgment
second analytical planner / second query validator
```

Yani accepted user contract ile native Metabase/Metabot candidate’ın maddi request invariants’ı karşılaştırılır; analitik implementasyonun nasıl yapıldığı Dima tarafından yeniden değerlendirilmez.

Mismatch durumunda:

```text
one native repair
→ still mismatch
→ bounded failure / limitation
```

Round-2’de contribution isteğinin changeover ranking’e kayması ve Haziran filtresinin ikinci query’de kaybolması tam olarak bu contract ihtiyacını gösteriyor. Dosyada da bu mekanizma query planner’ı tekrar yazmadan dry-plan disiplinini alma biçiminde öneriliyor.

---

## 1.5 User Requirement / Completion Ledger

Round-2’de birçok vaka core hesabı doğru yapıp isteğin ikinci yarısını unuttu.

Örnek:

```text
"toplamı söyle
+ bölüm bazında göster
+ farkı hesapla
+ yüzde değişimi ver
+ top contributors ver"
```

Tek obligation değildir.

ResearchBrief içinde:

```text
Requirement R1
Requirement R2
Requirement R3
...
```

olarak kalmalı.

Final terminalden önce:

```text
FULFILLED
LIMITED
UNSUPPORTED
INCONCLUSIVE
```

olmadan requirement kaybolamaz.

Bu özellikle:

```text
F01
F02
F03
F04
F08
```

puanlarını yükseltecek.

---

## 1.6 Adaptive Investigation Engine — P17 gerçek işine kavuşmalı

Bugünkü F06 = 35/100.

P17 yalnız:

```text
query yaptım
→ stop
```

değil.

Şu hareketleri native şekilde yönetebilmeli:

```text
INVESTIGATE_GAP
EXPLORE_ALTERNATIVES
TEST_DISCRIMINATING_EVIDENCE
SEEK_COUNTER_EVIDENCE
DEEPEN_EXPLANATION
REPLAN
STOP_BRANCH
STOP_INVESTIGATION
```

Ama yine:

```text
P17 chooses WHAT to investigate.
Metabase determines HOW to analyze it.
```

Her ResearchReasoningStep:

```text
what was known
what gap existed
why this branch
what evidence arrived
what changed
what next
```

kaydını tutmalı.

---

## 1.7 P17 → P19 bridge — P0

Round-2’nin en ciddi brain bulgusu:

```text
P19 invocations = 0 / 30
```

Bu kapanmadan RCA tamamlanmış sayılamaz.

Canonical flow:

```text
Observed problem
↓
P17 investigation
↓
Candidate explanation A
Candidate explanation B
Candidate explanation C
↓
P16 governed claims
↓
eligible competing hypotheses
↓
P19
```

Product Composer:

```text
"iki hypothesis üret"
```

demeyecek.

Yalnız mevcut state’e bakacak.

P19 callability tek bir executable predicate ile belirlenmeli:

```text
eligible_candidates(snapshot) :=
    candidate explanations
    WHERE scope_version == current_scope_version
      AND governed P16 claim refs are present
      AND governed Evidence refs are present

P19_ELIGIBLE(snapshot) :=
    request.intent == ROOT_CAUSE
    AND materially_distinct(eligible_candidates(snapshot)) >= 2
```

`materially_distinct` lexical farklılık değildir.

Ayrım typed/durable candidate identity ve açıklayıcı mekanizma/ilişki farkından gelmeli; yalnız farklı kelimelerle aynı açıklamayı söyleyen iki kayıt iki candidate sayılamaz. Regex, fuzzy text similarity veya morphology bu predicate’in authority’si olamaz.

Predicate true ise:

```text
P19 callable
```

Predicate false fakat legal bir discriminating investigation ile eksik Evidence elde edilebiliyorsa:

```text
NEED_MORE_EVIDENCE
→ P17 legal next investigation
```

`NEED_MORE_EVIDENCE` burada P19 epistemic assessment status’u değildir; P19 callability oluşmadan önce Product/P17 routing disposition’ıdır.

Predicate false ve yeni ayırıcı Evidence için legal/available yol yoksa:

```text
INCONCLUSIVE
```

Product Composer candidate/hypothesis uyduramaz, sayıyı ikiye tamamlayamaz ve stale/başka scope’taki candidate’ı current eligibility için kullanamaz.

Fake hypothesis yok.

---

## 1.8 P19 — Multi-factor Recursive Root Cause

V1’in en önemli differentiation katmanı.

P19 tek winner seçmeyecek.

Bir observed effect için:

```text
Hypothesis A
Hypothesis B
Hypothesis C
...
```

ve her biri için:

```text
supporting evidence
challenging evidence
missing evidence
temporal consistency
alternative explanations
materiality
```

tutulacak.

Epistemic durumlar:

```text
SUPPORTED
CHALLENGED
CONTESTED
CONTRADICTED
INCONCLUSIVE
```

Contribution interpretation:

```text
DOMINANT
MATERIAL
SECONDARY
WEAK
UNKNOWN
```

olabilir.

Ancak gerçek probabilistic/statistical model yoksa:

```text
"bu neden %83 ihtimal"
```

yasak.

Dosyanın önerdiği competing hypotheses → supporting/challenging evidence → discriminating test → bounded recursive child investigation akışı doğru ve korunmalı.

Recursive depth:

```text
depth starts at 1
deepen only on positive expected information gain
V1 hard max_depth = 3
```

`positive expected information gain` numeric veya LLM tarafından uydurulmuş bir confidence score değildir.

V1’de deepen gate ancak şu typed koşullar birlikte varsa açılır:

```text
material unresolved hypothesis ambiguity exists
AND a legal NextTestRequest can discriminate it
AND the requested Evidence surface is available
AND the Evidence/test is not a duplicate of already-inspected material
```

Bu koşullar yoksa recursive child investigation açılmaz.

Sırf depth=3 olsun diye derine inilmez.

Stop reasons:

```text
NO_INFORMATION_GAIN
NO_AVAILABLE_DATA
BUDGET_EXHAUSTED
HYPOTHESES_SEPARATED
CONTRIBUTION_IMMATERIAL
CAUSAL_IDENTIFICATION_INSUFFICIENT
```

---

## 1.9 P19 → P17 discriminating-test loop

P19 terminal-only evaluator olmayacak.

Örneğin:

```text
H1 ve H2 hâlâ ayrıştırılamadı.
```

P19:

```text
NextTestRequest
```

üretecek.

Sonra:

```text
P19
→ typed analytical need
→ P17 legal investigation step
→ Metabase
→ Evidence
→ P19
```

Bu loop dosyada da Dima’yı gerçek investigator yapan ana mekanizma olarak tanımlanmış.

---

## 1.10 P18 Relationship Closure

F05 bugün 75/100.

Hedef:

```text
association
co-movement
relationship
contribution
causality
```

ayrımını net tutmak.

P18:

```text
join engine
correlation calculator
query engine
```

olmayacak.

Metabase native analytics sonuçlarını business relationship semantics’e oturtacak.

Her önemli ilişki:

```text
supporting Evidence
challenging Evidence
limitation
scope
```

taşımalı.

---

## 1.11 Evidence-backed P20 Reporting

F08 = 55.

Şu terminal yasak:

```text
trusted REPORT
+
material analytical claim
+
Evidence = 0
```

Report sections:

```text
Observation
Finding
Hypothesis
Counter-evidence
Limitation
Decision implication
```

ve her material section:

```text
Claim
→ Evidence
→ Receipt
→ Scope
→ Freshness
```

zincirine sahip olmalı.

Evidence yoksa:

```text
LIMITED REPORT
```

olabilir.

Ama güçlü sonuç gibi sunulamaz.

---

## 1.12 Internal execution paths

Kullanıcı bunları görmeyecek.

```text
FAST ANSWER
GUIDED ANALYSIS
INVESTIGATION
```

### Fast Answer

```text
simple metric
breakdown
ranking
period comparison
```

P17/P19 yok.

Minimum model hop.

### Guided Analysis

```text
multi-metric
relationship
complex comparison
```

### Investigation

```text
adaptive
hypothesis
RCA
multi-step evidence
```

Dosya da aynı üç iç çalışma yolunu öneriyor.

---

## FAZ 1 — Benchmark hedefi

Round-2 aynı 30 promptla fix geliştirmek için kullanılır ama prompt-specific patch yasaktır.

Phase 1 final:

```text
overall common benchmark >= 90
```

tercihen:

```text
F01 >= 95
F02 >= 95
F03 >= 95
F04 >= 90
F05 >= 90
F06 >= 85
F07 >= 85
F08 >= 90
F09 = 100
F10 >= 90
```

Ama release gate salt score değildir.

Zorunlu invariant:

```text
provider contract exception       = 0
silent semantic drift             = 0
cross-tenant leak                 = 0
invented numeric fact             = 0
unsupported causal promotion      = 0

eligible RCA → P19                = yes
scope replacement                 = correct
Evidence-free trusted report      = 0
restart/resume                    = stable
```

Round-2’den sonra ayrıca yeni metamorphic/hidden-like validation corpus oluşturulmalı.

**Phase 1 kapanmadan Phase 2 intelligence productization başlamaz.**

---

# FAZ 2 — PRODUCT PLATFORM & COMPANY INTELLIGENCE

## Amaç

Phase 1’de çalışan beynin gerçek şirkete bağlanması.

Dosyanın Phase 2 tanımı da bunu “beyni gerçek bir şirkete nasıl bağlarız ve kullanıcı daha soru sormadan nasıl değer üretir?” şeklinde koyuyor.

Phase 2 sonunda eksiksiz headless V1 platform olacak.

---

## 2.1 Tek Product Façade

Frontend hiçbir zaman:

```text
P14
P17
P18
P19
P20
P21
```

bilmeyecek.

Canonical façade:

```text
/v1/company/context
/v1/company/map
/v1/capabilities

/v1/ask

/v1/investigations
/v1/investigations/{id}
v1/evidence/{id}
v1/artifacts/{id}
v1/timeline

/v1/watches
/v1/signals
/v1/today

/v1/saved-analyses
/v1/workspaces
/v1/briefs

/v1/decisions
/v1/actions
/v1/outcomes
/v1/memory
```

`HeadlessProductService` tek application façade.

Dosyanın önerdiği API yüzeyi de aynı biçimde frontend’in iç domain store’larını bilmemesini hedefliyor.

---

## 2.2 Authentication + Onboarding

V1:

```text
Google OAuth
email/password
```

İlk seçim:

```text
Use my data
Try demo
```

Data connect hedef havuzu:

```text
PostgreSQL
SQL Server
MySQL
CSV
Excel
```

Fakat Faz 2 ilk V1 acceptance scope’u bilinçli olarak daha dardır:

```text
Demo
+
CSV
+
one primary relational connector:
PostgreSQL OR SQL Server
```

Hangi relational connector’ın ilk olduğu gerçek pilot/müşteri ihtiyacına göre seçilir.

İlk connector acceptance gate connector sayısı değildir. Şu tam loop kanıtlanmalıdır:

```text
connect
→ schema discovery
→ Company Map
→ Company Brain
→ Ask
→ Watch
→ Signal
→ Investigation
```

Diğer relational connector, MySQL ve Excel Faz 2 içinde ikinci connector wave’i olabilir; ilk tam loop’un kapanmasını bloke etmez.

Yeni ingestion/query engine yok.

Metabase datasource substrate kullanılacak.

---

## 2.3 Semantic Bootstrap

Data connect sonrası:

```text
schema discovery
→ native metadata
→ entity candidates
→ metric/dimension candidates
→ relationship candidates
→ sector overlay
→ Company Map
→ human confirmation
```

Bu tamamen deterministic olmak zorunda değil.

Ancak mapping:

```text
versioned
auditable
editable
restart-safe
```

olmalı.

---

## 2.4 Company Brain

Company Brain analytical truth sahibi değildir.

Taşıdığı şey:

```text
Entity Registry
business Metric Registry
terminology
aliases
relationships
CompanyContext
sector overlay
Metabase resource refs
memory refs
```

Önemli sınır:

```text
Dima Metric Registry
≠ duplicate Metabase formula definition store
```

Dima:

```text
"fire" = revenue concept
```

bilir.

Revenue’nun analitik implementasyonu Metabase tarafındadır.

---

## 2.5 Watch → Signal

Canonical loop:

```text
scheduled/native observation
→ Watch
→ Signal
→ deduplication
→ cooldown
→ materiality
→ currentness
→ Today
```

Mümkün olduğunda Metabase native scheduled/alert capability kullanılmalı.

Dima scheduler’ı analytics engine’e dönüşmemeli.

Dima’nın sahibi:

```text
watch lifecycle
business meaning
Signal lifecycle
materiality state
responsibility
decision linkage
```

---

## 2.6 Today / Focus Queue

Today generic alerts listesi değildir.

Ama dosyadaki örnek:

```text
materiality × urgency × confidence × ...
```

formülünü canonical score olarak dondurmazdım.

V1’de:

```text
governed priority features
+
deterministic policy
```

kullanılır.

Inputs:

```text
materiality
urgency
freshness
persistence
responsibility
open decision relevance
blocked work
```

olabilir.

Ama ranking heuristiği ölçülmeden karmaşık formüle dönüşmez.

Feedback:

```text
important
not important
dismiss
snooze
watch
assign
investigate
```

saklanır.

---

## 2.7 Product objects

V1’e first-class:

```text
SavedAnalysis
Workspace
Brief
TodayItem
ScopeVersion
InvestigationTrace
HypothesisAssessment
```

eklenmeli.

Workspace:

```text
Signal
Chart
SavedAnalysis
Investigation
Evidence
Decision
Action
Outcome
Comment
```

toplayabilir.

Brief:

```text
period
audience
signals
decisions
outcomes
evidence refs
delivery state
```

taşır.

---

## 2.8 Finance Lite

Yalnız generic core ile üretilebilen yetenekler:

```text
cash position
receivables
payables
overdue invoices
collections breakdown
period variance
revenue/cost/gross-margin comparison
top debtor ranking
cash / overdue Watches
```

Advanced finance V1 dışı.

---

## 2.9 Manufacturing Lite

Generic core + Metabase:

```text
downtime
faults
throughput
performance
OEE if genuinely mapped
scrap / rework
FPY / quality
plan vs actual
department/machine breakdown
period comparison
Loss Radar
basic governed RCA
```

Predictive maintenance/optimizer yok.

---

## FAZ 2 çıkış kapısı

Yeni kullanıcı:

```text
login
→ data/demo
→ schema sync
→ Company Map
→ Company Brain
→ Ask
→ Watch
→ Signal
→ Today
→ Investigation
→ Evidence
→ SavedAnalysis
→ Workspace
→ Brief
```

akışını tamamlamalı.

Ve:

```text
browser refresh
backend restart
worker restart
```

sonrasında durable state kaybolmamalı.

---

# FAZ 3 — V1 EXPERIENCE, CLOSED LOOP & RELEASE

## Amaç

İlk iki fazdaki headless ürünün gerçek Dima deneyimine dönüşmesi.

Dosyada Phase 3 açıkça backend’i kullanıcıya gösterilen ürüne dönüştürme ve tüm ekranların Phase 1+2 product objects üzerinde çalışması olarak tanımlanıyor.

Ekrana özel backend yok.

---

## 3.1 Ana UX yüzeyleri

### Onboarding / Data Setup
Connection, schema scan, mapping review.

### Company Map
“Dima şirketimi nasıl anladı?”

### Dima Today
“Bugün dikkat etmeniz gerekenler.”

### Radar
Watch / Signal scanning surface.

### Contextual Ask
Her yerden açılabilen Ask.

### Evidence Drawer
Her sayı/finding/hypothesis/recommendation için:

```text
source
scope
filters
time
freshness
limitations
lineage
```

### Investigation Workspace

```text
Question
→ Branch
→ Evidence
→ Finding
→ Counter-evidence
→ Next Test
```

### Root Cause Room

```text
Hypothesis A
support
challenge
status

Hypothesis B
...

Go deeper
Test next
Stop here
```

### Saved Analysis / Live Dashboard

Native chart + Dima context.

### Brief

In-app first.

Controlled email later in the same V1 release if stable.

### Decision → Action → Outcome

Investigation ve Today üzerinden lightweight fakat durable.

V1 closed-loop scope burada mühürlüdür:

```text
contextual Decision
→ existing governed DecisionBrief / human adoption

manual / controlled ActionWork
→ owner
→ due state
→ progress / blocked / completed
→ no generic autonomous execution

Outcome observation
→ expected vs observed
→ governed Evidence / metric refs
→ no automatic causal attribution

Memory receipt
→ decision / action / outcome / limitation lineage
→ reference-first institutional memory
→ not a second truth owner
```

V1 içinde bunlar ayrı büyük ürünlere dönüşmeyecek.

Şunlar sonraya kalır:

```text
full Decision Desk
generic automation orchestration
agentic external execution
generic tool executor
autonomous ERP write-back
LLM/vector memory as truth authority
```

### Memory

Outcome’dan institutional memory’ye.

Dosyada bu deneyim yüzeyleri Company Map, Today, Radar, Contextual Ask, Evidence Drawer, Investigation Workspace ve Root Cause Room dahil ayrıntılı biçimde tanımlanıyor.

---

## 3.2 Üç canonical V1 demo loop

V1’i onlarca disconnected feature ile değil üç tam loop ile satacağız.

### A. Universal Intelligence

```text
Watch
→ Signal
→ Today
→ Investigation
→ Evidence
→ Hypothesis
→ Report
→ Decision
→ Action
→ Outcome
→ Memory
→ Brief
```

### B. Finance Lite

```text
Overdue receivables ↑
→ Signal
→ Today
→ customer/invoice breakdown
→ Evidence
→ Investigation
→ Decision
→ collection Action
→ Outcome
```

### C. Manufacturing Lite

```text
Downtime ↑
→ Radar
→ department
→ machine
→ candidate explanations
→ Evidence / Counter-evidence
→ RCA
→ Decision
→ Action
→ later Outcome
```

Dosyanın önerdiği üç satış senaryosu da aynı closed-loop mantığı taşıyor.

---

# 3.3 Performance architecture

Quick Answer:

```text
request
→ minimum cognition
→ native Metabase
→ Evidence
→ answer
```

Research:

```text
request
→ durable investigation job
→ progress events
→ Evidence appears incrementally
→ report
```

Kullanıcı uzun investigation’da boş spinner görmez.

Görebilir:

```text
Investigating…
1/4 evidence gathered
Testing another explanation…
Counter-evidence found…
Going one level deeper…
```

Dosya da quick-answer thin path ile long investigation’ın progressive work olarak ayrılmasını öneriyor.

---

# 3.4 Production hardening

Release gate:

```text
tenant isolation
permissions
OAuth
credential security
audit
restart/retry
idempotency
currentness/staleness
partial-result handling
rate limiting
model/token telemetry
query latency telemetry
job durability
progress events
responsive
accessibility
locale/date/number
backup/migrations
```

Ayrıca Metabase deployment/licensing modeli ticari release öncesinde ayrı hukuk/dağıtım incelemesinden geçmeli; dosya da bunu release checklist maddesi olarak koyuyor.

---

# V1 DIŞI — KESİN SINIR

V1 içinde yok:

```text
Wren production runtime
second analytics engine
second query planner

advanced cash forecasting
generic forecasting engine
financial risk scoring
payment optimizer
tax automation
autonomous accounting

production optimizer
scheduler
predictive maintenance
energy optimizer
process optimizer
recipe optimizer

generic ERP write-back
autonomous financial actions
machine control

true causal inference engine
high-frequency industrial ML
```

Bu sınır dosyada da açıkça V1 dışı olarak mühürlenmiş.

Capability Registry bunları:

```text
SPECIAL_ENGINE_DEFERRED
PRODUCTIZATION_DEFERRED
DATA_DEPENDENT
```

olarak tanıyabilir.

---

# 70.8 → 100 GELİŞTİRME HARİTASI

Round-2 puan kaybını doğrudan roadmap’e bağlarsak:

```text
F06 Adaptive Investigation      35 → 90+
F07 Root Cause                  57.5 → 90+
F08 Evidence Reporting          55 → 90+
F10 Conversation Repair         50 → 90+
F05 Relationship               75 → 90+
F01/F02/F03/F04                 80–87.5 → 95+
F09 Safety                     100 → preserve
```

Bunun anlamı:

```text
70 → 80
scope correctness + completion + provider reliability

80 → 90
adaptive investigation + P19 + RCA + P18

90 → 95+
report synthesis + conversation continuity

95 → 100-class
performance + hidden/metamorphic robustness + production hardening
```

Gerçek “100” aynı Round-2 promptlarını ezberleyerek alınmış 100 değildir.

V1 için kabul edeceğimiz 100-class kalite:

```text
known benchmark GREEN
+
new hidden-like benchmark GREEN
+
no P0 correctness violation
+
no silent wrong
+
closed-loop E2E GREEN
+
restart/security GREEN
```

olmalıdır.

---

# FAZLAR ARASI IMMUTABLE ACCEPTANCE GOVERNANCE

Her faz tek bir canonical candidate SHA ve immutable acceptance receipt ile kapanır.

Bir fazın kapanışı yalnız “testler yeşil” anlamına gelmez; o fazın authority/contract yüzeyinin dondurulduğu anlamına gelir.

## Faz 1 seal

Faz 1 sonunda:

```text
one canonical Phase-1 candidate SHA
+
immutable Phase-1 acceptance receipt
+
Sealed Dima Brain V1
```

üretilir.

Receipt en az:

```text
candidate SHA
engine SHA / release / digest
migration head
Brain contract / schema versions
benchmark + metamorphic validation receipts
P0 invariant results
known governed limitations
open technical debt
```

taşımalı.

Faz 1 seal sonrasında intelligence semantics docs-only değişiklik dışında oynanmaz.

Eğer Faz 2 veya Faz 3 sırasında Faz 1 semantics’ini değiştirmeyi gerektiren gerçek bir defect bulunursa:

```text
REOPEN PHASE 1
→ fix at owning contract
→ focused proof
→ affected regression
→ new Phase-1 candidate SHA
→ new immutable acceptance receipt
→ dependent later phase gates revalidated
```

olmadan değişiklik yapılamaz.

## Faz 2 seal

Faz 2 sonunda:

```text
one canonical Phase-2 candidate SHA
+
immutable Phase-2 acceptance receipt
+
headless product contract freeze
```

üretilir.

Freeze kapsamı:

```text
Product façade contracts
Company Brain contracts
connector acceptance scope
Watch / Signal / Today contracts
Workspace / Brief product objects
durability / resume / currentness
tenant / permission boundaries
```

Faz 3 sırasında bu headless contract’lar yalnız UX/productization ihtiyacı bahanesiyle sessizce değiştirilemez.

Headless contract değişikliği gerekiyorsa Faz 2 resmen reopen edilir ve yeniden mühürlenir.

## Faz 3 seal

Faz 3 sonunda:

```text
one canonical V1 release candidate SHA
+
immutable V1 release acceptance receipt
```

üretilir.

Faz 3’te normal olarak yalnız:

```text
UX implementation
productization fixes
performance
accessibility
locale
release hardening
```

değişiklikleri kabul edilir.

Core intelligence semantics veya headless product authority’sini değiştiren bir sorun bulunursa ilgili önceki gate resmen reopen edilmeden “release fix” adı altında patch yapılamaz.

Kalıcı kural:

```text
SEALED PHASE
!=
NEVER CHANGE

SEALED PHASE
=
CHANGE ONLY THROUGH EXPLICIT REOPEN
+ NEW CANONICAL SHA
+ NEW IMMUTABLE RECEIPT
```

Bu governance daha önce yaşanan “bir şeyi düzeltirken başka seal’i sessizce bozma” döngüsünü engellemelidir.

---

# ÜÇ FAZIN NİHAİ ÖZETİ

| Faz | Ne çözüyoruz? | Faz sonunda |
|---|---|---|
| **Faz 1 — Brain Convergence** | Scope, completion, adaptive research, P18/P19, recursive RCA, Evidence, reporting, fast path | **Sealed Dima Brain V1** |
| **Faz 2 — Product Platform** | Company Brain, data connect, Product API, Watch/Signal/Today, Workspace/Brief, Lite Packs | **Eksiksiz headless Dima V1** |
| **Faz 3 — Experience & Release** | UX, Radar, RCA Workspace, closed loop, performance, security, release | **Satılabilir production Dima V1** |

Son durum:

```text
FAZ 1
Company Context
→ Question
→ Investigation
→ Evidence
→ Hypothesis
→ Explanation

FAZ 2
Company
→ Watch
→ Signal
→ Today
→ Brain

FAZ 3
Today
→ Investigation
→ Decision
→ Action
→ Outcome
→ Memory
→ Brief
```

V1 sonunda Dima'nın gerçek çekirdeği:

> **Company Context → Watch → Signal → Today → Investigation → Evidence → Hypothesis → Decision → Action → Outcome → Memory → Brief**

olmalıdır.

Bu üç faz tamamlandıktan sonra ileri finans, muhasebe, forecasting, optimization veya manufacturing modelleri yeni bir Dima mimarisi gerektirmez; aynı çekirdeğe yeni `Solution Pack + Specialized Capability` olarak eklenir. Dosyanın nihai vizyonu da tam olarak bunu hedefliyor.