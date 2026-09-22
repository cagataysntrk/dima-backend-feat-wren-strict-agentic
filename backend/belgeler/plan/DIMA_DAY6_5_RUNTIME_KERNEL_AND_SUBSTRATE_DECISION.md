# DIMA DAY 6.5 — RUNTIME KERNEL, STANDARD PATH VE ANALYTICS SUBSTRATE KARAR ADDENDUMU

**Tarih:** 22 Eylül 2026  
**Branch:** `feat/ask-v2-mvp`  
**Statü:** **ACTIVE PHASE-LOCAL AUTHORITY**  
**Mühürlü roadmap/report:** DEĞİŞMEZ  
**Amaç:** Day 6.5 engineering closure'ın D65-E3 ve sonrasını, yeni runtime-kernel ve analytics-substrate kararlarıyla çelişkisiz yürütmek.

Bu belge yeni bir Day veya roadmap reset'i değildir. Mühürlü nihai roadmap ve denetim raporunun
Day 6.5 implementation addendum'udur. Çelişki halinde current Day 6.5 uygulama ayrıntısında bu belge
ve `DIMA_V2_GELISTIRME_DURUM.md`; üst seviye ürün hedefinde mühürlü roadmap/report authority'dir.

---

## 1. Karar özeti

```text
Day 6.5 RESET                              HAYIR
SemanticCatalogRetriever geri alınsın      HAYIR
StandardBuilder durdurulsun                HAYIR
ikinci bespoke Standard agent loop         HAYIR
minimal generic bounded runtime kernel     EVET
ResearchManager şimdi kernel'e migrate     HAYIR
Metabase source copy / port                HAYIR
Metabase production dependency şimdi       HAYIR
Wren current canonical incumbent           EVET
Metabase isolated substrate challenger     EVET
production'da iki equal truth engine       STOP-THE-LINE
```

Temel prensip:

> Generic runtime process-control sahibidir; business truth / semantic truth / authority sahibi değildir.

---

## 2. Nihai ürün zihinsel modeli

Ürün/mimari seviyesinde iki execution path vardır:

```text
execution_path:
  STANDARD
  RESEARCH
```

`STANDARD_DIRECT` üçüncü path, üçüncü engine veya üçüncü authority değildir.

```text
STANDARD outcome:
  DIRECT
  BUILDER
```

DIRECT:

```text
model_turns = 1
repair_count = 0
sealed = true
```

BUILDER:

```text
same STANDARD engine
+ bounded discovery / inspect / bind / propose / validate / repair
+ progress required
+ budget bounded
+ final seal
```

Transition eval corpus telemetry için `STANDARD_DIRECT` / `STANDARD_BUILDER` label'larını taşıyabilir.
Fakat architecture-level authority ailesi değildir.

Accepted authority:

```text
AcceptedAuthority
├── AcceptedStandardAuthority
└── AcceptedResearchAuthority
    = existing AcceptedTurnContract semantic body
    = alias / tagged view only
```

İkinci Research semantic contract oluşturmak yasaktır.

---

## 3. Nihai architecture target

```text
                         USER
                          │
                          ▼
                 DIMA CONVERSATION
                          │
                          ▼
                 cognition / intent
                          │
                          ▼
                   EXECUTION PATH
                    /           \
             STANDARD          RESEARCH
                │                 │
                ▼                 ▼
      Standard profile      existing bounded
                │            ResearchManager
                ▼                 │
      BoundedAgentRuntime          │
          Kernel                   │
                │                 │
                ▼                 ▼
      StandardProjection     AcceptedTurnContract
                │            + UOL / Directives
                ▼                 │
 AcceptedStandardAuthority        │
                └────────┬────────┘
                         ▼
                  DIMA TRUST PLANE
                         │
                SemanticBindingGate
                         │
                      Planner
                         │
                ANALYTICS SUBSTRATE
                         │
                  WREN — incumbent
                         │
                         DB
                         │
               QueryContract / Evidence
                         │
                  Findings / Research
                         │
              Recommendation / Decision
```

Metabase bu target'ın production hot path'inde bugün YOKTUR.

Şimdilik:

```text
METABASE
1. architecture reference
2. isolated analytics substrate challenger
3. future BI workspace candidate
```

---

## 4. D65-E3A — minimal generic bounded runtime kernel

Yeni modül:

```text
app/v2/agent_runtime.py
```

Tercih edilen minimal primitive'ler:

```text
BoundedLoopBudget
LoopCounters
LoopTerminalReason
ActionStateGuard
BoundedAgentRuntimeKernel
```

Kernel yalnız ortak process mechanics bilir:

```text
model turn counting
tool-call counting
budget enforcement
generic dispatch lifecycle
observation append
terminal detection
action fingerprint
state fingerprint
duplicate action/state detection
NO_PROGRESS
budget exhausted
generic telemetry
```

Kernel kesinlikle BİLMEZ:

```text
metric / dimension semantics
USER_MUST
root cause
AcceptedTurnContract
UserObligationLedger
ResearchDirective
Evidence VERIFIED semantics
sem_* minting
canonical semantic choice
join validity
query correctness
numeric truth
authority acceptance
research completion
RLS/CLS policy meaning
```

Kernel gate'leri tanımlamaz. Domain gate'leri profile/domain layer çağırır.

---

## 5. Profile / domain sınırı

Profile şunları seçebilir/tanımlayabilir:

```text
tool surface
action schema
allowed process states
budget defaults
terminal outcome types
prompt/instruction surface
state fingerprint projection
```

Profile şunları tanımlayamaz:

```text
authority policy
canonical semantic truth
security truth
numeric truth
completion truth
```

Authority domain-level/type-level kalır:

```text
StandardAuthorityGate / StandardAuthoritySealer
Research IntentAcceptanceGate
CompletionGate
SemanticBindingGate
Planner / Wren / DB
```

---

## 6. manager_progress.py reuse sınırı

Reuse edilebilir generic primitive'ler:

```text
_digest
action_fingerprint
result_fingerprint
```

Research-specific olarak kalır:

```text
progress_fingerprint(runtime)
DynamicActionFrontier.progress(runtime)
```

Çünkü bunlar şu Research state'ini okur:

```text
ledger
AcceptedTurnContract
evidence refs
semantic receipts
research runtime snapshot
```

Generic kernel contract:

```text
ActionFingerprint
+
StateFingerprint (domain/profile supplies it)
```

Runtime yalnız pair'ı izler:

```text
(action_fingerprint, state_fingerprint)
```

Invariant:

```text
max_executions_per_action_state_pair = 1
duplicate_reexecution_max = 0
```

Aynı action aynı authoritative state üzerinde ikinci kez execute edilmez → `NO_PROGRESS`.

---

## 7. D65-E3B — Standard profile / StandardBuilder

StandardBuilder tek governed analytical projection kurar.

Allowed:

```text
semantic candidate discovery
exact semantic resource inspection
bounded semantic selection
typed temporal normalization
standard projection proposal
deterministic validator feedback üzerinden representation repair
alternate verified candidate/source
genuine clarification
```

Forbidden:

```text
hypothesis tree
root-cause research
evidence-driven new business question
UserObligationLedger
ResearchDirective ownership
adaptive research branch
raw SQL
direct DB
join authority
numeric truth
RLS/CLS bypass
Research CompletionGate
```

Önerilen Standard tool surface:

```text
retrieve_semantic_candidates
read_semantic_resource
resolve_semantics
normalize_temporal
propose_standard_projection
request_clarification
```

State flow:

```text
INITIAL
→ DISCOVER / INSPECT
→ BIND
→ PROPOSE
→ VALIDATE

PASS
→ narrow CoverageVeto
→ SEAL

retryable representation error
→ REPAIR
→ PROPOSE

blocking ambiguity
→ CLARIFY

actual research-only capability
→ RESEARCH_REQUIRED

unsupported
→ UNSUPPORTED

same action + same state
→ NO_PROGRESS

budget exhausted
→ FAILED CLOSED
```

Standard failure otomatik Research DEĞİLDİR.

---

## 8. D65-E3C — StandardProjection compiler decoupling

Compiler core lightweight grounded Standard input alır:

```text
validated standard bindings
→ StandardProjection
```

Research compatibility wrapper korunabilir:

```text
compile(contract, ledger, ...)
→ wrapper
→ lightweight compiler core
```

Standard'ın `AcceptedTurnContract + UserObligationLedger` üretmesi gerekmez.

Aynı semantic body ikinci kez modellenmez.

---

## 9. STANDARD_DIRECT kararı

`STANDARD_DIRECT` ayrı:

```text
engine        HAYIR
router        HAYIR
authority     HAYIR
runtime       HAYIR
```

Yalnız StandardBuilder telemetry/outcome'udur:

```text
execution_path  = STANDARD
standard_outcome = DIRECT
```

İlk attempt lossless seal değilse:

```text
execution_path   = STANDARD
standard_outcome = BUILDER
```

---

## 10. AcceptedStandardAuthority

Minimal seal:

```text
authority_id
turn_id
request_ref
source_message_hash
context_version
projection_hash
semantic_handle_refs
temporal_handle_refs where applicable
projection_kind
accepted_attempt_id
model_role
standard_outcome
created_at
```

`StandardProjection` semantic body olmaya devam eder.

Authority object projection'ı duplicate AST olarak tekrar taşımaz.

Execution yalnız sealed Standard authority ile Core'a ilerler.

---

## 11. Semantic authority değişmez

```text
Semantic Catalog
→ SemanticCatalogRetriever        discovery only
→ bounded linker SELECT/ABSTAIN   cognition only
→ SemanticBindingGate             canonical truth + sem_*
```

Kalıcı invariant:

```text
retrieval score != semantic truth
retrieval miss  != semantic does not exist
```

LLM:

```text
canonical ID uyduramaz
candidate set dışına çıkamaz
sem_* mint edemez
SQL yazamaz
numeric truth veremez
```

---

## 12. Standard → Research izolasyonu

Rejected/failed Standard attempt'tan Research'e taşınmaz:

```text
sem_*
StandardProjection
accepted metric selection
accepted dimension selection
inferred operation
comparison choice
temporal semantic decision
Standard accepted authority
```

Taşınabilir yalnız non-authoritative cache:

```text
raw SourceSpanRefs
retrieved CandidateRefs
LLM-safe candidate cards
immutable catalog lookup cache
```

Research original user message üzerinden fresh bind eder.

```text
rejected Standard authority merge = 0
```

---

## 13. Narrow Standard CoverageVeto

Standard path ağır UOL/Completion taşımaz.

Final seal öncesi Coverage yalnız şu sorulara veto koyabilir:

```text
material user request omitted?
explicit exclusion omitted / wrong polarity?
research-only request/capability silently omitted?
```

Coverage:

```text
semantic seçemez
handle mint edemez
canonical ID öneremez
query/projection repair edemez
clarification truth sahibi değildir
obligation ekleyemez
authority commit edemez
```

---

## 14. Standard başlangıç bütçesi

```text
max_model_turns = 4
max_tool_calls = 8
max_executions_per_action_state_pair = 1
duplicate_reexecution_max = 0
```

Sayısal değerler benchmark-tunable config'dir.

Architecture invariant:

```text
progress varsa bounded devam
sealed projection terminal
duplicate/no-progress stop
real research-only request typed escalation
budget fail-closed
```

---

## 15. Research Manager — NO-TOUCH

Day 6.5 boyunca şu dosyalar generic runtime uğruna wholesale refactor edilmez:

```text
manager_loop.py
manager_runtime.py
manager_tools.py
manager_preacceptance.py
```

Current Research path:

```text
AcceptedTurnContract
UserObligationLedger
ResearchDirective
CompletionGate
ResearchRunTerminal
Evidence
semantic receipts
```

ile test edilmiş ve bounded kalır.

`ManagerRuntime` Standard için reuse edilmez.

Research generic-kernel migration:

```text
Day 6.5 prerequisite DEĞİL
Day 7–10 prerequisite DEĞİL
Day 10 Product MVP sonrası duplication ölçümüne bağlı
optional
```

Migration hiç yapılmayabilir; bu kabul edilebilir.

---

## 16. Wren current incumbent

Day 6.5 boyunca canonical analytics substrate:

```text
WREN
```

Current role:

```text
company/customer MDL
models
relationships
measures
dimensions
cubes
governed planning/query execution boundary
```

Bu sunk-cost kararı değildir; bugün kanıtlı incumbent budur.

Şimdi yapılmayacak:

```text
Wren'i çıkarma
production'a ikinci query truth engine koyma
büyük AnalyticsExecutionPort framework yazma
```

---

## 17. Metabase kararı

Metabase:

```text
source-copy / port              NO
Dima fork of Metabase           NO
production engine today         NO
runtime architecture reference  YES
substrate challenger            YES
future BI workspace candidate   YES
```

Metabase OSS/agent subsystem kaynak kodunu Dima proprietary backend'e kopyalama/port etme yapılmaz.
Lisans/compliance ayrı değerlendirme gerektirir.

Metabase pattern'den alınan fikir:

```text
GENERIC LOOP MECHANICS
+
DOMAIN-SPECIFIC PROFILE
```

Dima-native uygulanır.

---


---

## 17A. Metabase Source Reference Contract

**Canonical upstream authority**

```text
repository = metabase/metabase
reference_sha = 74216b30981d8310c4cf724d63ca282e2e63529d
authority = canonical upstream Git source at the pinned SHA
```

Bu SHA Day 6.5 runtime/substrate kararı için current source-reference snapshot'ıdır.
Yeni bir Metabase mimari kararı verilecekse önce upstream güncelliği ayrıca araştırılır;
fakat geçmiş kararın neye dayanarak verildiği bu SHA ile audit edilir.

**Canonical source paths — pinned SHA üzerinde doğrulandı**

```text
src/metabase/metabot/agent/core.clj
src/metabase/metabot/agent/profiles.clj
src/metabase/agent_api/reference.md
src/metabase/agent_api/api.clj
src/metabase/agent_api/query_guards.clj
src/metabase/mcp/v2/tools/query.clj
```

Kısa referans adları:

```text
metabot/agent/core.clj
metabot/agent/profiles.clj
agent_api/reference.md
agent_api/api.clj
agent_api/query_guards.clj
mcp/v2/tools/query.clj
```

### 17A.1 Local checkout contract

Repo veya çalışma ortamında ileride `public/metabase/master` bulunursa:

```text
role = read-only convenience checkout
authority = NONE
write / vendor / patch / import into Dima = FORBIDDEN
canonical comparison target = metabase/metabase @ pinned/declared SHA
```

Şu an Dima Git tree'sinde `public/metabase/master` yoktur. Varlığı hiçbir zaman upstream
authority'nin yerine geçmez; stale olabileceği varsayılır ve SHA doğrulanmadan karar verilmez.

### 17A.2 Source-copy / port / vendor yasağı

Kesin yasak:

```text
Metabase Clojure source copy into Dima backend
Metabase agent loop port into Python by transliteration
vendor directory / subtree import
copy-paste query guards as Dima implementation
forked embedded Metabase runtime hidden inside Dima
local checkout'u canonical source gibi kabul etmek
```

İzin verilen:

```text
architecture pattern study
behavioral contract study
API contract study
permission/query-guard study
independent Dima-native implementation
separate-service integration through supported Agent API
```

### 17A.3 D65-X integration boundary

D65-X gerçek Metabase challenger entegrasyonu **separate-service Agent API** üzerinden yapılır.

```text
Dima
  StandardProjection / AcceptedStandardAuthority
        ↓ thin challenger adapter
Metabase separate service
  /api/agent ...
        ↓ Metabase permission/query guards
database
```

Metabase process/library Dima backend içine linklenmez veya vendored edilmez.
Dima adapter Metabase'in public/supported Agent API contract'ına konuşur.

D65-X'te Metabase native agent/NLQ experience ayrıca ölçülecekse bu **secondary experiment**
olarak tutulur; substrate-only primary bake-off ile karıştırılmaz.

### 17A.4 Required bake-off receipt

Her Metabase D65-X measurement receipt en az şunları pinler:

```text
canonical_source_repo = metabase/metabase
source_reference_sha
runtime_version
runtime_image_digest
service/API base identity
Agent API contract/version evidence
Dima tested SHA
adapter SHA
benchmark/corpus version
tenant/user permission context
timestamp
```

`runtime_image_digest` mümkünse immutable container digest (`sha256:...`) olmalıdır;
yalnız mutable image tag receipt için yeterli değildir.

Source SHA ile çalışan runtime image aynı artifact olmak zorunda değildir; ikisi ayrı ayrı
kaydedilir. Uyuşmazlık varsa receipt bunu açıkça belirtir ve benchmark yorumu buna göre yapılır.

### 17A.5 Mandatory Metabase source-control / analysis / research protocol

Metabase ile ilgili hiçbir önemli implementation veya architecture adımı körlemesine yapılmaz.
Aşağıdaki protokol **D65-X başlamadan önce ve Metabase davranışına dayanan her önemli karar öncesinde** zorunludur.

**A — Source identity**

1. Canonical repo `metabase/metabase` olduğunu doğrula.
2. Kararın dayandığı exact source SHA'yı yaz.
3. Local checkout varsa `git rev-parse HEAD` ile SHA'sını doğrula; uyuşmazsa local source'a güvenme.
4. Gerekirse current upstream'i ayrıca araştır; pinned historical snapshot ile current upstream'i karıştırma.

**B — Required source reading**

En az şu dosyaları exact source SHA üzerinde tekrar oku:

```text
src/metabase/metabot/agent/core.clj
src/metabase/metabot/agent/profiles.clj
src/metabase/agent_api/reference.md
src/metabase/agent_api/api.clj
src/metabase/agent_api/query_guards.clj
src/metabase/mcp/v2/tools/query.clj
```

İncelenecek başlıklar:

```text
agent-loop continuation/termination semantics
profile-specific tool surfaces and iteration budgets
terminal-tool behavior
Agent API request/response and authentication surface
permission/scope enforcement
query guards / native SQL separation
query validation-repair-resolution pipeline
query execution/result envelope
handle/cursor/replay behavior
current runtime/version/deployment contract
```

**C — Distinguish pattern from authority**

Her bulgu şu sınıflardan biriyle not edilir:

```text
PATTERN_REFERENCE
API_CONTRACT
SECURITY_GUARD
RUNTIME_BEHAVIOR
DIMA_INFERENCE
NOT_APPLICABLE_TO_DIMA
```

Metabase implementation detail'i otomatik Dima requirement'ı sayılmaz.

**D — Dima cross-check**

Metabase bulgusu her zaman Dima'nın şu authority'leriyle çaprazlanır:

```text
AcceptedStandardAuthority
StandardProjection
SemanticBindingGate
planner validity
RLS/CLS / tenant identity
QueryContract
EvidenceArtifact
replay permission re-check
exactly-one primary substrate rule
```

Metabase bir davranışı desteklemiyorsa Dima invariant'ı sessizce gevşetilmez.

**E — Security and truth-plane review**

Agent API veya query path kullanmadan önce:

```text
auth identity mapping
tenant/user permission propagation
raw SQL/native-query boundary
query guard fail-closed behavior
result provenance
executed-query identity
permission re-check on replay/handle
cross-tenant leakage risk
```

ayrı ayrı doğrulanır.

**F — External/current verification**

Metabase sürümü, Agent API, lisans/edition, deployment veya API behavior'u değişebilecek
bir konuysa current upstream docs/source/release state ayrıca araştırılır. Eski pinned SHA'dan
current behavior varsayılmaz.

**G — Decision receipt**

Her önemli Metabase kararı living status'a şu formatta girer:

```text
question
canonical repo
source SHA
files inspected
runtime version/image digest if executed
observed fact
Dima inference
risk / limitation
decision
next verification
```

**H — STOP-THE-LINE**

Aşağıdakilerde Metabase integration/decision work durur:

```text
source SHA unknown
local checkout SHA unverified
required source files not inspected
API contract inferred only from memory
permission/query guard behavior unverified
runtime image/version unpinned
copy/port/vendor proposal
Metabase behavior used to weaken Dima trust-plane invariant
second equal production truth engine introduced
```

Bu protokol product development sequence'ini değiştirmez; yalnız Metabase'e temas edilen
relevant gate/decision'larda zorunlu preflight ve receipt discipline ekler.
## 18. D65-X — analytics substrate challenger gate

Bu gate Day 6.5 engineering closure'dan SONRA, final certification seal'den ÖNCE gelir.

```text
DAY 6.5 ENGINEERING CLOSED
ARCHITECTURE FROZEN
        ↓
D65-X ANALYTICS SUBSTRATE CHALLENGER
        ↓
VALIDATION50
        ↓
external fresh HIDDEN50
        ↓
CERTIFICATION SEALED
```

### 18.1 Primary experiment — substrate-only bake-off

Aynı:

```text
Dima cognition
accepted semantics
AcceptedStandardAuthority
StandardProjection
benchmark
```

Yalnız execution substrate değişir:

```text
StandardProjection
       │
  ┌────┴─────┐
  │          │
Wren      Metabase
Adapter    Adapter
  │          │
 DB         DB
```

Bu deney şu soruyu cevaplar:

> Hangi governed execution substrate Dima'nın trust/receipt contract'ını daha doğru, ekonomik ve sürdürülebilir sağlıyor?

### 18.2 Secondary experiment — full agent experience

Ayrı, daha sonra:

```text
Dima STANDARD profile
vs
Metabase native NLQ/Metabot
```

Bu substrate-only karar deneyiyle karıştırılmaz.

---

## 19. D65-X ölçütleri

P0:

```text
silent wrong                        = 0
cross-tenant leakage                = 0
permission bypass                   = 0
unsafe ambiguity auto-pick          = 0
unverified semantic substitution    = 0
provenance break                    = 0
```

Standard correctness:

```text
semantic correctness
query correctness
result correctness
repair success
unsupported handling
ambiguity handling
```

Operational:

```text
p50 / p95 latency
LLM calls
token cost
query count
integration LOC
maintenance surface
schema onboarding effort
```

Dima-specific:

```text
exact execution QueryContract'a bağlanabiliyor mu?
gerçekte çalışan query kanıtlanabiliyor mu?
AcceptedStandardAuthority execution identity referanslayabiliyor mu?
replay current permissions'ı tekrar doğrulayabiliyor mu?
result EvidenceArtifact'a semantic laundering olmadan dönüşebiliyor mu?
tenant/context identity end-to-end korunuyor mu?
```

Commercial:

```text
license
embedding
SSO
multi-tenancy
per-user cost
operations
upgrade cost
```

Karar:

```text
Wren wins / tie
→ Wren incumbent stays
→ certification continues

Metabase clearly wins
→ certification STOP
→ isolated Metabase adapter becomes new engineering candidate
→ affected Standard gates rerun
→ new DEV broad proof
→ new freeze candidate
→ fresh Validation/Hidden certification
```

Production'da Wren + Metabase equal truth engines YASAK.

---

## 20. UI / BI workspace sınırı

Metabase gelecekte:

```text
dashboards
collections
chart editor
exploration UI
saved questions
```

için değerlendirilebilir.

Temiz entegrasyon:

```text
Dima sealed artifacts
→ Metabase
```

veya:

```text
Dima governed analytical views/materialized surface
→ Metabase
```

Aynı production DB'ye serbest Query Builder vermek “UI only” değildir; ikinci query semantics/execution
yolu yaratır ve ayrıca karar gerektirir.

---

## 21. Engine-independent Dima kimliği

```text
DIMA
= cognition
+ accepted authority
+ research
+ evidence
+ decision intelligence
```

Analytics substrate replaceable olabilir; cognition/authority/evidence contract sabit kalmalıdır.

Fakat Day 6.5'te premature büyük abstraction framework açılmaz.

Bake-off zamanı en dar seam:

```text
StandardProjection
→ execute
→ governed execution receipt/result
```

Önce current Wren path ince adapter ile sarılır; challenger lab adapter aynı seam'i uygular.

---

## 22. Exact Day 6.5 engineering sequence

Canonical sequence:

```text
D65-E1 exact semantic-SHA recert
→ D65-E2 SemanticCatalogRetriever
→ D65-E3A minimal generic bounded runtime kernel
→ focused kernel tests
→ D65-E3B StandardBuilder/Profile uses kernel
→ D65-E3C lightweight StandardProjection compiler
→ D65-E4 AcceptedStandardAuthority / Research alias split
→ D65-E5 narrow CoverageVeto
→ provider-free failure-family closure
→ workers=1 focused live
→ same-SHA model-floor A/B only if needed
→ 12–16 stratified canary
→ real Wren Standard vertical + Research sentinel
→ ENGINEERING FREEZE CANDIDATE
→ DEV80 once-per-candidate
→ frozen hard gates
→ DAY 6.5 ENGINEERING CLOSED / ARCHITECTURE FROZEN
→ D65-X Wren vs Metabase substrate challenger
→ VALIDATION50 no tuning
→ external fresh HIDDEN50
→ CERTIFICATION SEALED
→ production hybrid activation
```

### 22.1 Current-repo sequencing exception — NO ROLLBACK

Yeni karar geldiğinde repo D65-E3B/C, E4 ve E5'in bazı parçalarını zaten yazmıştı.

Bunları geri alma:

```text
standard_builder.py core        focused GREEN
lightweight compiler            focused GREEN
AcceptedStandardAuthority       focused GREEN
narrow CoverageVeto             focused GREEN
```

Ancak bunlar generic kernel kararı öncesinde yazıldığı için:

```text
PROVISIONAL GREEN
!=
ARCHITECTURE SEALED
```

Sıradaki iş:

```text
D65-E3A generic kernel
→ existing StandardBuilder mechanics kernel consumer olacak şekilde re-home
→ semantic behavior değiştirme
→ E4/E5'i koru
→ family closure tekrar
```

Bu bir reset değildir; internal-structure correction'dır.

---

## 23. Eval terminology / oracle

Architecture-level:

```text
execution_path:
  STANDARD | RESEARCH

standard_outcome:
  DIRECT | BUILDER
```

Transition eval metadata:

```text
allowed_work_modes:
  STANDARD_DIRECT
  STANDARD_BUILDER
  RESEARCH

expected_authority_family:
  AcceptedStandardAuthority
  AcceptedResearchAuthority
  NONE
```

Interpretation:

- standard representable case: DIRECT veya BUILDER geçerli olabilir,
- research-only case: RESEARCH zorunlu,
- clarification/unsupported before acceptance: authority family NONE olabilir.

Work mode authority family değildir.

---

## 24. Phase thresholds

Run başlamadan dondurulur:

```text
DEV80 case pass        >= .95
DEV80 MUST recall      >= .95
VALIDATION50 case pass >= .95
VALIDATION50 MUST      >= .95
HIDDEN50 case pass     >= .95
HIDDEN50 MUST          >= .95
adaptive branch        >= .90 where applicable

P0 authority/security/silent-loss = 0
```

Moving goalpost yok.

---

## 25. Freeze / corpus invalidation

```text
one DEV80 per engineering-freeze candidate SHA
```

Named-case tuning için aynı candidate DEV80 tekrar tekrar koşturulmaz.

Systemic family bug fix → yeni SHA → yeni freeze candidate → yeni DEV80 broad proof.

Validation fail + code change:

```text
certification invalid
→ engineering reopen
→ new freeze
→ fresh validation set
```

Hidden fail + code/architecture change:

```text
same hidden certification için reuse edilmez
→ external evaluator fresh sealed hidden üretir
```

---

## 26. Day 7–10 değişmiyor

```text
Day 7 / P10  RESULT-AWARE RESEARCH LOOP
Day 8 / P11  ROOT-CAUSE BRANCH
Day 9 / P12  REPORTDOCUMENT
Day10 / P13  PRODUCT MVP GATE
```

Yeni:

```text
Day 6.6 Agent Runtime  YOK
Day 7 Metabase         YOK
```

Day 7 gate:

```text
valid tool selection        >= 95%
adaptive branch             >= 90%
undeclared tool execution   = 0
budget overrun undisclosed  = 0
```

Research generic-runtime migration bu günlerin prerequisite'i değildir.

---

## 27. Parallelism / sequencing of challenger

Ayrı developer hattı varsa:

```text
Day 7–10 canonical development
+
isolated D65-X lab bake-off
```

paralel olabilir.

Tek hattı varsa iki kabul edilebilir seçenek:

```text
A)
Day6.5 engineering closed
→ D65-X
→ Day7

B)
Day6.5 engineering closed
→ Day7–10 Product MVP
→ D65-X
→ certification
```

Değişmez:

> Metabase challenger kararı gelmeden production hot-path'e ikinci query engine eklenmez.

---

## 28. STOP-THE-LINE

Aşağıdakilerde feature work durur, abstraction düzeltilir:

```text
second semantic authority
Standard kernel learns Research semantics
silent user requirement loss
blocking ambiguity auto-pick
retrieval score becomes truth
rejected Standard authority leaks into Research
raw SQL/direct DB authority
cross-tenant/context handle
post-acceptance raw-prompt semantic reparse
unverified numeric truth
evidence-less VERIFIED completion
model-specific/case-specific semantic branch
silent fallback
Wren + Metabase equal production truth engines
```

---

## 29. Failure taxonomy

Patch'ten önce:

```text
MODEL_COGNITION
CONTRACT/ARCHITECTURE
RESOLVER_TRUTH
EVAL_ORACLE
TRANSPORT/PROVIDER
```

Infra/provider fail semantic fail değildir.

Corpus schema / manifest / evaluator expectation uyuşmazlığı `EVAL_ORACLE` sınıfıdır; product semantic
patch gerekçesi değildir.

---

## 30. Geliştirme protokolü

- Plan + report + bu addendum çapraz okunur.
- Mühürlü nihai roadmap/report değiştirilmez.
- Living status her commit/test/debt/next-ticket bilgisini taşır.
- Vertical slice önceliklidir.
- Normal loop: code → 3–15 sn focused provider-free → devam.
- Büyük suite milestone/family/freeze gate'te.
- Workers=1 semantic certification önce.
- Paid live test manuel/ölçülü.
- Failure owner sınıflandırılmadan patch yok.
- Regex/morphology/keyword/testcase-ID/case-derived prompt yok.
- Resolver corpus'a göre eğilip bükülmez.
- Exactly-one semantic authority.
- Coverage veto-only.
- Receipt provenance-only.
- USER_MUST != ResearchDirective/AGENT_DERIVED.
- Freeze öncesi checkpoint; A/B exact same SHA.
- Hidden final certification blocker.
- Vaka geçirerek sistem yapılmaz; doğru abstraction kurulur.

---

## 31. Current handoff — 22 Eylül 2026

Bu addendum yazılırken gerçek repo durumu living status'ta authoritative olarak tutulur.

Bilinen completed focused proofs:

```text
D65-E1 exact semantic-SHA recert       70/70 GREEN
D65-E2 Retriever seam                  9/9 GREEN
D65-E3 provisional StandardBuilder     20/20 GREEN
D65-E4 Standard authority split        25/25 GREEN
D65-E5 narrow CoverageVeto             16/16 GREEN
D65-E3A-R runtime kernel focused       22/22 GREEN
runtime-aligned provider-free family   94/94 GREEN
```

Front-door family closure history:
```text
run 35691397377
87 PASS / 1 FAIL
failure class = EVAL_ORACLE

run 35691982389
88 / 88 PASS
5 warnings
12.46s
```

İlk fail'in sebebi manifest ile DEV corpus schema-integrity oracle arasındaki metadata uyumsuzluğuydu (`allowed_work_modes`, `expected_authority_family`). Corpus/oracle hizalandı; semantic/product patch yapılmadı. Bu nedenle family closure şu anda GREEN kabul edilir.

---

## 32. Sıradaki exact çalışma

D65-E3A-R tamamlandı.

Implementation:

```text
app/v2/agent_runtime.py
  BoundedLoopBudget
  LoopCounters
  LoopTerminalReason
  ActionStateGuard
  BoundedAgentRuntimeKernel

app/v2/standard_builder.py
  now consumes BoundedAgentRuntimeKernel
```

Research NO-TOUCH doğrulandı.

Focused run `35693039369`: **22/22 PASS**.

Runtime-aligned full provider-free family run `35693146320`: **94/94 PASS**, 5 warnings, 12.39s.

Current next gate:

```text
workers=1 focused live architecture set
→ exact-same-SHA fast/reference model-floor A/B only if needed
→ 12–16 stratified canary
→ real Wren Standard vertical + Research sentinel
→ ENGINEERING FREEZE CANDIDATE
→ DEV80 once-per-candidate
```

Bu noktada yeni preparation/refactor açılmaz. Live gate current green checkpoint üzerinden yürür.

## 33. Kaynak karar provenance

Yeni karar iki ayrı rapordan birleştirilmiştir:

1. **Nihai Mimari Karar ve Güncellenmiş Yol Haritası** — genel architecture/roadmap kararı.
2. **Current Implementation Handoff** — D65-E3'ün repo üzerinde bugün nasıl uygulanacağı.

Raporların kritik dış referans snapshot'ı:

```text
Metabase pinned master in report: 74216b30981d8310c4cf724d63ca282e2e63529d
pattern taken: generic loop mechanics + domain-specific profiles
source-copy/port: forbidden

Wren: current incumbent governed semantic/query substrate
replacement decision: only through isolated D65-X bake-off
```

Metabase reference'i Dima'ya source import yetkisi vermez. Mimari desen alınır; kod kopyalanmaz.
