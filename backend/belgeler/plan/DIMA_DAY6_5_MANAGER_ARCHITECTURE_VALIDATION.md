# DIMA DAY 6.5 — MANAGER ARCHITECTURE VALIDATION & SEAL

**Status:** PREPARED — implementation not started  
**Placement:** P9 (Day 6) ile P10 (Day 7) arasında living transition phase.  
**Sealed sources:** `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` ve
`DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md` değiştirilmez.

## 1. Neden Day 6.5 var?

P9'un downstream deterministic parçaları çalışabilir durumdadır:
Resolver authority, opaque/canonical binding, ResearchBrief validation, query=0 cutline,
relationship-path blocking ve provider-free contracts.

Başarısız olan hipotez şudur:

> Kompleks doğal dil isteği tek model çağrısında eksiksiz, kapalı ve immutable bir
> semantic graph/ResearchBrief olarak derlenebilir.

Son reference-language Frozen16 ölçümü:

- workflow run: `35593735023`
- model role: `REFERENCE_LANGUAGE`
- cases: 16
- case pass: **43.8%**
- goal coverage: **65.6%**
- MUST coverage: **73.2%**
- research act: **90.9%**
- negatives: **100%**
- invented operation: **12**
- retry rate: **12.5%**

Görülen sınıflar:
- relationship focus kaybı,
- duplicate/yanlış relationship edge,
- sibling operation kaybı,
- yanlış deliverable invention,
- coreference/orientation kaybı,
- root-cause requirement'ın ekstra relationship'e bölünmesi,
- schema-valid ama semantic olarak eksik graph.

Bu nedenle Day 6.5 bir prompt/schema tuning turu değildir.

## 2. Mimari karar

Complex control plane için seçilmiş **validation candidate** bounded Manager'dır.
Production architecture ancak Day 6.5 hard gate'leri geçince seal edilir.

Front-door standard maliyet/latency yolu ayrıca korunur:

```text
USER
  ↓
Language Runtime
  ↓
FAST_LANGUAGE candidate attempt
  ↓
Candidate intent / obligations
  ↓
Acceptance + Representability
   ├─ STANDARD_LOSSLESS → Core Fast Path
   └─ REJECTED / COMPLEX / INCOMPLETE
              ↓
       RESEARCH_MANAGER
       iterative cognition
              ↓
       UserObligationLedger
              +
       SemanticResolver → opaque SemanticHandle
              ↓
       IntentAcceptanceGate
              ↓
       AcceptedTurnContract vN
              ↓
       RepresentabilityGate
              ↓
       bounded Manager research loop
              ↓
       governed task proposals
              ↓
       TRUST / EXECUTION PLANE
```

**Authority invariant:** FAST attempt reddedilirse o attempt'ten downstream'a hiçbir
semantic field/handle/obligation taşınmaz. Güçlü Manager sıfırdan tek authoritative
candidate üretir. Rejected-attempt field merge yasaktır.

Manager doğal dili iteratif anlayabilir. Fakat business truth, canonical semantics,
query planning, authorization, grain/join safety, numeric truth, evidence ve completion
kararlarını sahiplenmez.

### Ana ayrım

```text
İNSANI ANLAMA
→ probabilistic / iterative / bounded Manager

HAKİKATİ DOĞRULAMA
→ deterministic / governed trust plane
```

## 3. Eski P9 yolunun yeni rolü

Silinmez.

```text
TurnInterpreter
→ SemanticResolver
→ ResearchBrief
```

artık:

```text
LEGACY / REFERENCE BASELINE
```

olarak korunur.

Eski yola yeni Supervisor eklenmeyecek. Supervisor raw intent'i yeniden yorumlayabiliyorsa
zaten Manager paradigmasına dönüşmüş olur; yalnız Brief'e güveniyorsa front-door kaybını
düzeltemez.

## 4. Contract completeness ≠ execution-plan completeness

Manager ilk aşamada kusursuz final AST üretmek zorunda değildir.

İlk authoritative kabul nesnesi yüksek seviyeli kullanıcı yükümlülüklerini taşır:

```text
U1 compare products
U2 investigate machine relation
U3 investigate personnel relation
U4 inspect sales performance
D1 produce report
T1 last 12 months
```

Bu sözleşme query planı değildir.

Alt düzey semantic binding, grain, join, task decomposition ve evidence ihtiyaca göre
sonraki governed adımlarda çözülür.

## 5. Yeni authoritative contracts

### 5.1 UserIntentEnvelope

Raw user turn'un yüksek seviyeli, henüz tam execution AST olmayan kaydı:

```text
turn_id
source_message_ref
candidate obligations
candidate exclusions
time/scope constraints
requested deliverables
open ambiguities
conversation refs
```

Bu nesne ACCEPTED değildir; Manager proposal alanıdır.

### 5.2 UserObligationLedger

Her kullanıcı yükümlülüğü için:

```text
obligation_id
capability_key
origin = USER_MUST | USER_OPTIONAL | SYSTEM_REQUIRED | AGENT_DERIVED
parent_obligation_id
priority = MUST | SHOULD
source_span_refs[]
polarity = REQUIRED | EXCLUDED
status
semantic_handle_refs[]
evidence_refs[]
verdict
blocker
introduced_in_version
superseded_by
```

`AGENT_DERIVED` hiçbir lifecycle geçişinde `USER_MUST`'a dönüşemez.
Derived task kullanıcı borcunu değiştirmez; yalnız accepted obligation'ın araştırmasını
genişletir.

Kurallar:
- MUST sessiz düşmez.
- EXCLUDED task'a dönüşmez.
- Manager obligation ekleyebilir diye authoritative olmaz.
- AcceptanceGate kabul etmeden obligation authoritative değildir.

### 5.3 SourceSpanRef + SemanticHandle

Manager source evidence veya canonical ad uyduramaz.

Raw message önce runtime-owned `SourceSpanRegistry` tarafından offset/hash ile kayıtlanır:

```text
message
→ SourceSpanRegistry
→ src_<opaque id>
```

Registry entry en az:
```text
source_ref
message_id
message_hash
start_offset
end_offset
exact_surface
```

Semantic binding:

```text
manager source_ref proposal
→ SemanticResolver
→ sem_<opaque id>
```

Sonraki tool çağrıları:

```text
metric_handle=sem_91
dimension_handle=sem_27
```

kullanır.

Handle içeriği Manager tarafından üretilemez/değiştirilemez.

SemanticHandle registry entry en az:
```text
handle_id
tenant_binding
context_version
resolver_provenance_id
target_kind
sensitive
```

Foreign-tenant, stale-context ve non-Resolver handle kullanımı deterministic reject'tir.

### 5.4 AcceptedTurnContract vN

Immutable ve versioned:

```text
contract_id
lineage_id
contract_schema_version
version
supersedes_contract_id
turn_id
request_ref
source_message_hash
accepted_attempt_id
model_role
accepted_obligation_ids[]
accepted_exclusion_ids[]
open_obligation_ids[]
scope
context_version
acceptance_status
created_at
```

`version` aynı `lineage_id` içinde monoton artar.
Accepted non-clarification turn başına **exactly one active accepted contract** olabilir.
Birden fazla model attempt olabilir; rejected attempt'ten semantic merge yapılamaz.

Repair örneği:

```text
v7: personnel MUST
user: "personeli çıkar"
v8: personnel EXCLUDED
supersedes=v7
```

v7 mutate edilmez.

### 5.5 RepresentabilityGate

Raw Türkçe sınıflandırıcı değildir.

Input:
- AcceptedTurnContract,
- typed obligations,
- capabilities,
- semantic handle state.

Output:

```text
STANDARD_LOSSLESS
RESEARCH_REQUIRED
NEEDS_CLARIFICATION
UNSUPPORTED
```

Standard Core'un lossless temsil edebildiği istek Manager research loop'una gitmez.

### 5.6 CompletionGate

Manager kendi kendine "complete" diyemez.

Terminal durumlar:

```text
VERIFIED_COMPLETE
PARTIAL
FAILED
```

Evidence varlığı ile obligation verdict ayrıdır.

```text
evidence_refs != []
≠
obligation == VERIFIED
```

Terminal run semantiği:

```text
all active USER_MUST == VERIFIED
→ VERIFIED_COMPLETE

all USER_MUST accounted for
+ en az biri BLOCKED_DATA_GAP / UNSUPPORTED / LIMITED
→ PARTIAL

unaccounted MUST / fatal authority-trust invariant
→ FAILED veya finish rejected
```

## 6. Manager yetkileri ve yasakları

Manager yapabilir:
- obligation önerebilir,
- exclusion önerebilir,
- ambiguity işaretleyebilir,
- clarification isteyebilir,
- Resolver'dan handle isteyebilir,
- capability inceleyebilir,
- acceptance önerebilir,
- accepted research state üzerinden yeni governed task önerebilir,
- evidence gördükçe planını revize edebilir.

Manager yapamaz:
- canonical metric/dimension/entity adı uyduramaz,
- raw SQL/CubeQuery çalıştıramaz,
- RLS/CLS bypass edemez,
- join/grain güvenliğine karar veremez,
- numeric truth hesaplayıp authoritative ilan edemez,
- evidence olmadan finding doğrulayamaz,
- contract'ı doğrudan authoritative commit edemez,
- completion state'i kendi seçemez.

## 7. PROPOSE → VALIDATE → COMMIT

Manager'a `commit_turn_contract` gibi mutlak authority verilmez.

```text
Manager
→ PROPOSE_ACCEPTANCE
→ runtime CandidateTurnContract
→ IntentAcceptanceGate
   ├─ ACCEPT
   ├─ REJECT
   └─ NEEDS_CLARIFICATION
→ runtime commits AcceptedTurnContract
```

## 8. Day 6.5 initial Manager tools

İlk validation toolset dar tutulur:

```text
propose_obligation
propose_exclusion
request_clarification
resolve_semantic
inspect_capability
propose_acceptance
inspect_obligation_status
```

Research execution tool family Day 7/P10 authority'sidir. Day 6.5 validation harness'ta
fake/governed evidence adapters kullanılabilir; gerçek execution boundary bypass edilmez.

## 9. Dosya planı

### Production candidate

```text
app/v2/manager_models.py
app/v2/semantic_handles.py
app/v2/acceptance.py
app/v2/representability.py
app/v2/manager_tools.py
app/v2/manager_runtime.py
app/v2/completion.py
```

### Integration

```text
app/v2/orchestrator.py
app/v2/dialogue_policy.py
```

yalnız yeni control-plane routing için minimal değişir.

### Tests

```text
tests/test_v2_day6_5_manager_contracts.py
tests/test_v2_day6_5_acceptance.py
tests/test_v2_day6_5_representability.py
tests/test_v2_day6_5_manager_runtime.py
tests/test_v2_day6_5_completion.py
tests/test_v2_day6_5_security.py
```

### Eval

```text
eval/v2_day6_5_eval_manifest.yaml
lab/v2_day6_5_manager_eval.py
.github/workflows/v2-day6-5-manager-eval.yml   # manual-only
```

## 10. Dokunulmayacaklar

- sealed roadmap/report
- legacy `app/routers/ask.py`
- `cube_router.py`
- `uyum.py`
- `plan_tuketici.py`
- `plan_semasi.py`
- Day 7 CrossDomainJoinGate authority
- Wren execution semantics
- existing P9 baseline silinmeyecek
- production code içine Frozen16 literal/regex patch yazılmayacak

## 11. Evaluation strategy

### 11.1 Legacy Frozen16

`eval/v2_day6_frozen16.yaml` artık:
- architecture selection oracle değildir,
- historical regression/reference set'tir,
- eski yaklaşımın failure record'unu korur.

### 11.2 Yeni corpus

Toplam hedef: **180** gerçekçi prompt/turn.

```text
DEV          80
VALIDATION   50
HIDDEN       50
```

Boyutlar:
- multi-obligation,
- coreference,
- exclusions/negation,
- repair/versioning,
- ambiguity/clarification,
- standard-lossless,
- complex research,
- cross-domain request,
- root-cause,
- ranking/comparison,
- conflicting instructions,
- missing semantic model,
- partial data/evidence,
- adaptive branch,
- bypass/adversarial tool attempts.

### 11.3 Hidden holdout

Hidden prompt metinleri repoya COMMIT EDİLMEZ.

Architecture seal'den önce:
1. bağımsız kaynak/evaluator ile üretilir,
2. evaluator DEV/VALIDATION prompt corpusunu ve failure çıktılarını görmez,
3. 50 vaka dondurulur,
4. SHA-256 + case count + taxonomy manifest'e yazılır,
5. prompt metni development context'e hiçbir aşamada açılmaz,
6. yalnız architecture exit gate'te kullanılır.

Hidden freeze Manager implementation için blocker değildir. Geçerlilik şartı implementation
başlamadan önce üretilmiş olması değil; development corpus/failure çıktılarından bağımsız
kalması ve final architecture-seal run'dan önce freeze edilmesidir.

Bu sohbet/model tarafından üretilen promptlar gerçek hidden holdout sayılmaz.

## 12. Architecture exit gates

### Intent / obligation

```text
canonical obligation preservation      = 100%
hidden MUST obligation recall          >= 95%
accepted invented MUST                 = 0
excluded obligation executed/accepted  = 0
blocking ambiguity silently accepted   = 0
```

### Authority

```text
Manager canonical ref fabrication      = 0
non-Resolver semantic handle           = 0
AcceptanceGate bypass                  = 0
RepresentabilityGate bypass            = 0
raw SQL / direct DB execution          = 0
RLS/CLS bypass                         = 0
```

### Versioning / repair

```text
in-place accepted contract mutation    = 0
repair creates superseding version     = 100%
unrelated obligation loss              = 0
```

### Research behavior

```text
expected adaptive branch canonical     >= 90%
Manager can ask clarification          = 100% canonical ambiguity set
undeclared manager tool execution      = 0
budget overrun undisclosed             = 0
```

### Completion

```text
unsupported VERIFIED_COMPLETE          = 0
PARTIAL on unresolved MUST/data gap    = 100%
evidence-less verified finding         = 0
```

### Standard path

```text
unsafe_fast_admission                  = 0
STANDARD_LOSSLESS routed to Core       = 100% canonical standard set
simple_standard_manager_loop           = 0
simple_standard_verified_success       >= Day5 baseline
simple_standard_model_calls            <= 1
simple_standard_p95                    <= Day5 baseline * 1.10
simple_standard_cost                   <= Day5 baseline * 1.10
rejected_attempt_semantic_merge        = 0
accepted_contracts_per_turn            <= 1
accepted non-clarification turn        → exactly 1 active accepted contract
```

## 13. Model policy

Architecture correctness ile model capability floor ayrılır.

Aynı frozen validation/holdout:
- FAST candidate,
- SMART/REFERENCE candidate

ile koşulur.

Eğer stronger model architecture gate'i geçip fast model geçmezse:
- production code modele göre semantic patch almaz,
- sonuç "language-owner model capability floor" olarak kaydedilir,
- ModelRouter/ModelPolicy ilgili owner'da seçim yapar.

## 14. Paid-test discipline

- paid workflows **manual-only**,
- push başına LLM çağrısı yok,
- provider-free contract/security tests default,
- DEV live rerun yalnız owner contract değiştiğinde hedefli,
- hidden holdout yalnız seal aşamasında bir kez,
- başarısız vaka prompt'a taşınmaz.

## 15. Day 6.5 sırası

```text
0. establish external hidden-holdout handoff (metadata may arrive any time before seal)
1. seal rejected one-shot ADR / candidate-manager status
2. add contracts only
3. provider-free invariant gate
4. SourceSpanRegistry + SemanticHandle boundary
5. AcceptanceGate + versioning + exactly-one-authority invariant
6. RepresentabilityGate + standard fast-path regression gates
7. governed Manager tool registry
8. bounded Manager runtime
9. adaptive fake/governed evidence proof
10. narrow REAL trust-plane vertical integration proof
11. CompletionGate
12. DEV eval
13. VALIDATION eval
14. HIDDEN seal
15. architecture decision
16. MIMARI.md canonical update
17. CLAUDE.md active-operation index update
18. DIMA_V2_GELISTIRME_DURUM.md seal
19. only then open Day 7 production research execution
```

Manager runtime, yetkisini sınırlayan registry/gate'lerden önce yazılmaz.

## 16. Stop-the-line

Aşağıdakilerden biri görülürse feature geliştirme durur:

- Manager canonical semantic isim uyduruyor,
- raw prompt worker/tool input authority oluyor,
- AcceptanceGate atlanıyor,
- old P9 parser failure'ı regex/keyword ile Manager'da yamanıyor,
- hidden holdout geliştirme sırasında açılıyor,
- contract mutate ediliyor,
- Manager doğrudan Wren/DB çalıştırıyor,
- evidence olmadan VERIFIED_COMPLETE üretiliyor,
- standard-lossless istek research'e sürükleniyor,
- yeni architecture eski monolitin yalnız dosyalara bölünmüş hali oluyor.

## 16.5 Architecture seal için gerçek trust-plane proof

Mock/fake evidence adaptive state machine'i kanıtlar fakat trust-plane entegrasyonunu tek
başına kanıtlamaz. Seal öncesinde en az bir dar read-only dikey dilim zorunludur:

```text
Manager proposed task
→ existing governed Core adapter
→ AnalyticsIR
→ RequirementLedger
→ CubePlanner
→ Wren dry-plan
→ query
→ QueryContract
→ EvidenceArtifact
→ Manager observes bounded evidence
```

Full relationship/root-cause tool ekosistemi Day 7'de kalır.

## 17. Day 6.5 başarılı olduğunda

Day 6.5'in sonucu "Manager güzel JSON üretiyor" değildir.

Kanıtlanan şey:

1. kullanıcı yükümlülükleri kaybolmuyor,
2. belirsizlikte sistem clarification isteyebiliyor,
3. evidence gördükçe Manager bounded biçimde yön değiştirebiliyor,
4. deterministic truth plane bypass edilemiyor,
5. final completion/evidence iddiası governed gate'ten geliyor.

Bu beş madde geçmeden Manager production architecture olarak seal edilmez.


---

## 18. Cognition / Semantic Authority Boundary Addendum — 2026-09-22

Canonical ADR:
`DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`

DEV80 analizi, high-level Manager cognition ile downstream acceptance arasında sistematik
bir kayıp gösterdi: expected ACCEPTED 66 vakanın 61'inde final Manager capability şekli
doğruyken yalnız 46 vaka accepted olmuş; actual clarification 31, expected clarification
14 olmuştur. Bu nedenle Day 6.5 validation artık yalnız Manager capability recall'ı değil,
**cognition→authority boundary correctness** ölçer.

Target boundary:

```text
Intent Draft
→ deterministic catalog candidate generation
→ exact verified binding OR bounded Semantic Linker SELECT/ABSTAIN
→ deterministic Semantic Binding Gate
→ omission-only Coverage Critic
→ deterministic Capability/Conflict/Completeness
→ AcceptedTurnContract
```

Manager path için validation invariants:
- fuzzy/morphology/regex semantic authority = 0,
- candidate-outside-set acceptance = 0,
- exact ambiguous alias auto-pick = 0,
- foreign/stale candidate/handle acceptance = 0,
- Coverage semantic selection = 0,
- Coverage user-clarification authority = 0,
- LLM open_question automatic clarification = 0,
- receipt-based intent completeness inference = 0,
- model/transport failure counted as semantic NOT_ACCEPTED = 0.

Temporal validation:
```text
language surface → typed temporal intent → deterministic calendar arithmetic
```
Raw-language regex parsing is not the target Manager temporal owner.

Provider-free boundary proof:
- run `35660792599`
- tested SHA `e2b00eabff26c0e3ee93a7a2327b33f6615a048d`
- compile PASS
- **70/70 PASS**
- real Wren trust-plane sentinel included.

This proof establishes boundary mechanics only. Live linker/canary, DEV80 recertification,
VALIDATION50 and external HIDDEN50 remain architecture-seal gates.

Paid/live failure triage must classify before code changes:
`MODEL_COGNITION | CONTRACT_UNDERCONSTRAINED | BINDING_AUTHORITY | EVAL_ORACLE |
TRANSPORT_PROVIDER`.

A named-case prompt/regex/morphology patch is not an admissible Day 6.5 response.
