# Dima Day 6.5 — Engineering Closure Protocol

**Status:** ACTIVE PHASE-LOCAL AUTHORITY  
**Branch:** `feat/ask-v2-mvp`  
**Prepared against:** `cb4df1601ac113b41bb3d54c308ab981246e11ed`  
**Latest semantic code at preparation:** `c9629d9029db360e86a8592e12da646a2afc0621`

> Bu belge mühürlü `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` ve
> `DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md` dosyalarını değiştirmez.
> Day 6.5'te bu iki belgenin bugünkü repo gerçekliğine nasıl uygulanacağını ve
> engineering closure sırasını tanımlar. Living progress yine yalnız
> `DIMA_V2_GELISTIRME_DURUM.md` dosyasına yazılır.

## 0. 2026-09-22 runtime-kernel/substrate override

Bu protokol artık `DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md` ile birlikte okunur.

Bağlayıcı delta:

- architecture execution path yalnız `STANDARD | RESEARCH`.
- `STANDARD_DIRECT` ayrı path/engine/router/authority değildir; Standard outcome/telemetry'dir.
- `STANDARD_BUILDER` aynı Standard engine'in bounded repair outcome'udur.
- `app/v2/agent_runtime.py` altında minimal generic bounded process-control kernel kurulacaktır.
- Kernel business/semantic/authority/research truth bilmeyecektir.
- Research Manager Day 6.5'te generic kernel'e migrate edilmeyecektir.
- Wren current incumbent analytics substrate olarak kalacaktır.
- Metabase production dependency değildir; engineering closure sonrası ve certification seal öncesi isolated challenger'dır.
- Kernel kararı gelmeden yazılmış StandardBuilder/E4/E5 focused-green kodu geri alınmaz; fakat kernel realignment bitene kadar architecture-sealed sayılmaz.

## 1. Mimari arama bitti

Day 6 one-shot complex semantic compiler'a geri dönülmez. Üçüncü bir genel cognition
mimarisi aranmaz.

Day 6.5'in korunacak ana ilkesi:

```text
LLM / language runtime  = cognition + bounded proposal / recovery
Semantic catalog        = what exists
SemanticBindingGate     = canonical semantic authority
Planner                 = analytical validity
Wren / DB               = numeric truth
QueryContract/Evidence  = proof
Ledger/CompletionGate   = research completion truth
```

Yeni işler mevcut sınırları tamamlar; yeni genel cognition stack açmaz.

## 2. İki execution path, iki accepted-authority ailesi

```text
execution_path:
  STANDARD
  RESEARCH

standard_outcome:
  DIRECT
  BUILDER
```

Transition eval telemetry'sinde `STANDARD_DIRECT` / `STANDARD_BUILDER` label'ları tutulabilir; fakat bunlar ayrı engine/router/authority değildir.

```text
AcceptedAuthority
├── AcceptedStandardAuthority
└── AcceptedResearchAuthority
```

- `STANDARD / DIRECT`: aynı Standard engine ilk turda lossless projection'ı seal eder.
- `STANDARD / BUILDER`: aynı Standard engine bounded discovery/repair ile seal eder.
- `RESEARCH`: multi-obligation / relationship / root-cause / adaptive evidence problemi.

DIRECT ve BUILDER aynı `AcceptedStandardAuthority` ailesini üretir.

`AcceptedResearchAuthority` yeni ikinci bir research semantic body DEĞİLDİR. Uygulamada mevcut `AcceptedTurnContract` research authority gövdesi olarak korunur; gerekiyorsa yalnız type alias / tagged-union etiketiyle `AcceptedResearchAuthority` adı verilir. Aynı research semantic gerçeği ikinci kez modellenmez.

## 2A. Generic bounded runtime kernel

Day 6.5 StandardBuilder ikinci bespoke loop olmayacaktır.

Yeni küçük process-control kernel: `app/v2/agent_runtime.py`.

Kernel yalnız model/tool counters, budget enforcement, observation append, generic dispatch lifecycle, action fingerprint, domain/profile-supplied state fingerprint, duplicate action/state detection, terminal detection, `NO_PROGRESS`, budget exhaustion ve telemetry bilir.

Kernel `AcceptedTurnContract`, `UserObligationLedger`, `ResearchDirective`, Evidence verification, semantic truth, `sem_*` minting, query/join/numeric truth veya completion truth bilmez.

`manager_progress.py` içindeki generic digest/action/result fingerprint primitive'leri reuse edilebilir; Research-specific `progress_fingerprint(runtime)` generic kernel'e taşınmaz.

`manager_loop.py`, `manager_runtime.py`, `manager_tools.py`, `manager_preacceptance.py` Day 6.5'te kernel'e migrate edilmez.

## 3. Standard ile Research correctness problemi ayrıdır

### StandardBuilder

Tek soru:

> Bu kullanıcı isteğini tek governed analytical projection olarak güvenli ve kayıpsız
> nasıl kurarım?

Yapabilir:
- semantic candidate discovery,
- exact semantic resource inspection,
- bounded semantic selection,
- typed temporal normalization,
- standard projection proposal,
- deterministic validation feedback'ine göre bounded representation repair,
- genuine ambiguity'de clarification.

Yapamaz:
- hypothesis tree / root-cause investigation,
- evidence'dan yeni business question üretme,
- USER_MUST research ledger yönetme,
- adaptive research branch,
- numeric truth ilanı,
- raw SQL / direct DB / join authority,
- RLS/CLS bypass,
- research completion kararı.

İlk tool surface dar tutulur:

```text
retrieve_semantic_candidates
read_semantic_resource
resolve_semantics
normalize_temporal
propose_standard_projection
request_clarification
```

### Research Manager

Research lane mevcut Day 6.5 authority modelini korur:

```text
finite pre-acceptance
AcceptedTurnContract
exactly-one active authority
UserObligationLedger
ResearchDirective
SourceSpan provenance
bounded semantic linker
SemanticBindingGate
capability algebra
evidence lifecycle
adaptive research
CompletionGate
```

Manager araştırma kapsamını / hipotezi önerebilir. Query fan-out ve analytical validity
Planner authority'sidir.

## 4. Semantic discovery truth değildir

Kalıcı invariant:

```text
retrieval score != semantic truth
retrieval miss  != semantic does not exist
```

`SemanticCatalogRetriever` interface zorunludur. İlk backend mevcut deterministic
enumeration olabilir. Vector/BM25/RRF Day 6.5 işi değildir.

`SemanticLinkCandidateCard` LLM-safe discovery görünümüdür.
`CatalogCandidateBinding` / BindingGate internal canonical truth zinciridir.

Retriever candidate discovery yapar; authority üretmez.

## 5. Standard authority minimal olmalı

Standard path Research'in ağır UOL/Completion machinery'sini taşımaz.

Minimal artifact:

```text
AcceptedStandardAuthority
- authority_id
- turn_id / request_ref
- source_message_hash
- context_version
- projection_hash
- semantic_handle_refs
- temporal_handle_refs
- projection_kind
- created_at
```

Execution ancak sealed Standard authority üzerinden Core'a gider.

## 6. Coverage veto-only

Standard seal öncesi şimdilik tek dar intent-coverage veto korunur:

```text
material user request omitted?
explicit exclusion omitted?
research-only directive/capability omitted?
```

Coverage:
- canonical semantic seçemez,
- semantic handle isteyemez,
- query oluşturamaz,
- clarification truth sahibi olamaz,
- obligation ekleyemez.

Benchmarklar gerçek omission yakalamadığını ve yalnız false-veto ürettiğini kanıtlarsa
sonradan eval-only observer'a indirilebilir.

## 7. Standard → Research isolation

Başarısız Standard attempt'tan Research authority'ye şunlar taşınmaz:

```text
sem_*
StandardProjection
accepted metric selection
inferred operation
comparison choice
temporal semantic decision
```

Taşınabilir non-authoritative cache:

```text
raw SourceSpanRefs
retrieved CandidateRefs
LLM-safe catalog cards
immutable catalog lookup cache
```

Research finite pre-acceptance original message'i fresh işler. Accepted authority doğduktan
sonra raw prompt downstream semantic authority olarak yeniden yorumlanamaz.

## 8. Bounded progress kuralı

StandardBuilder serbest agent değildir.

State machine:

```text
INITIAL
→ DISCOVERING / INSPECTING
→ CONSTRUCTING
→ VALIDATING
→ REPAIRING (bounded)
→ SEALED | CLARIFY | ESCALATE_RESEARCH | UNSUPPORTED | FAILED
```

Her action için:

```text
ActionFingerprint + StateFingerprint
```

tutulur. Aynı state üzerinde aynı action tekrar gelirse `NO_PROGRESS`.
Initial config ölçüm başlangıcı:

```text
max_model_turns = 4
max_tool_calls = 8
max_executions_per_action_state_pair = 1
duplicate_reexecution_max = 0
```

Sayılar benchmarkla değişebilir; değişmezler:
- progress varsa devam,
- sealed projection terminal,
- no-progress stop,
- research-only need escalate,
- budget fail-closed.

## 9. Failure sınıflandırmadan patch yok

Her failure önce tam bir sınıfa girer:

```text
MODEL_COGNITION
CONTRACT/ARCHITECTURE
RESOLVER_TRUTH
EVAL_ORACLE
TRANSPORT/PROVIDER
```

Ek typed product outcomes gerektiğinde ayrı tutulur:
- genuine ambiguity,
- permission failure,
- provider failure,
- unsupported capability,
- metadata gap,
- budget/no-progress.

Infra/provider failure semantic denominator'a yanlış cevap olarak yazılmaz.

## 10. Yasaklar

- regex / morphology / keyword business branch,
- testcase-ID logic,
- case-derived prompt,
- Resolver'ı corpus'a göre eğip bükme,
- fuzzy score'u semantic truth yapmak,
- rejected attempt field/authority merge,
- second semantic owner,
- raw SQL Manager authority,
- post-acceptance raw prompt semantic reparse,
- unverified numeric claim,
- no-path cross-domain join,
- silent fallback,
- model-specific business logic.

Tek ilke:

> Vaka geçirerek sistem yapmıyoruz; doğru abstraction'ı kurup vakaların onun doğal sonucu
> olarak geçmesini istiyoruz.

## 11. Test operasyon protokolü

Normal loop:

```text
code
→ 3–15 sec focused/provider-free test
→ continue vertical slice
```

Büyük suite yalnız milestone/bundle/final gate.

- workers=1 semantic/mimari certification önce,
- paid LLM manual-only gerektiğinde,
- push başına otomatik paid test yok,
- fail → classify → then decide,
- model floor architecture ile karıştırılmaz,
- önemli müdahale öncesi checkpoint SHA,
- A/B exact same backend SHA.

Sequence:

```text
provider-free invariants
→ workers=1 focused stability
→ same-SHA strong reference / fast A/B when needed
→ 12–16 stratified canary
→ D65-J1A isolated decision-model bake-off
→ if promising: D65-J1B provider seam + role separation + focused/live/canary revalidation
→ real Wren Standard + Research sentinels/revalidation
→ ENGINEERING FREEZE CANDIDATE
→ DEV80 exactly once for that freeze candidate
→ engineering freeze
→ VALIDATION50 (no tuning)
→ external fresh HIDDEN50
→ certification seal
```

Hidden development blocker değildir; final certification blocker'dır.

### 11.1 Freeze-candidate / corpus invalidation

`DEV80 once` şu anlama gelir:

```text
one DEV80 per engineering-freeze candidate SHA
```

Aynı SHA'yı named-case tuning için tekrar tekrar DEV80'e sokmak yasaktır. DEV80 ortak bir
`CONTRACT/ARCHITECTURE` veya `RESOLVER_TRUTH` failure family gösterir ve kod değişirse yeni SHA
**yeni freeze candidate** olur; eski DEV80 yeni kodu certify etmez ve broad DEV80 proof yeniden
gerekir.

VALIDATION50 veya HIDDEN50 fail sonrası production/correctness code değişirse certification freeze
geçersiz olur:

```text
certification STOP
→ engineering REOPEN
→ root-cause classification
→ code/contract change if justified
→ new freeze candidate
→ provider-free / focused / canary / sentinels
→ DEV80 for new candidate
→ fresh certification sets
```

Görülmüş VALIDATION50 artık unbiased certification seti sayılmaz. HIDDEN50 fail sonrası
architecture/code değişirse aynı hidden corpusunu tekrar tekrar kullanmak yasaktır; external
evaluator yeni sealed hidden corpus üretir. Hidden prompt/per-case expected output development
context'e yine girmez.

### 11.2 Failure triage receipt gate

Live/canary/DEV/Validation/Hidden RED sonrasında:

```text
RED
→ NO PRODUCT/SEMANTIC CODE CHANGE
→ DIMA_DAY6_5_FAILURE_TRIAGE_RECEIPTS.md receipt
→ same-SHA A/B when owner/model-floor is not yet proven
→ failure_class + single_owner + root_cause
→ failure family statement
→ allowed_files_to_touch / files_not_to_touch
→ only then code
→ focused proof
→ family/metamorphic proof
```

Receipt tamamlanmadan semantic/product patch **STOP-THE-LINE**.

`ONE FAILURE ≠ ONE NEW RULE`: yalnız tek wording/testcase açıklanabiliyorsa yeni mechanism/prompt rule eklenmez.
Failure family aynı kök nedenin farklı wording/schema/tenant yüzeylerindeki genel temsilini açıklamalıdır.

Prompt değişikliği yalnız generic typed contract değişikliğini tarif etmek için yapılabilir. Failed phrase/example, case-ID instruction, keyword/regex teaching veya model micro-patch yasaktır.


### 11.3 D65-J1 decision-model challenger gate

D65-J1 is a pre-freeze **cognition decision-model** gate. It does not renumber the canonical roadmap, change Day7–10, or alter D65-X.

Entry preconditions:
```text
D65-G CLOSED GREEN
provider-free family 102/102 GREEN
reference-floor canary 35697064833 = 16/16 GREEN
P0 counters = 0
```

J1A is LAB/EVAL ONLY. Product semantic/authority/temporal files are NO-TOUCH.

Pinned Jev challenger:
```text
typesafe/jev-1.13
```

Forbidden during J1A:
```text
~typesafe/jev-latest
chat/completions wrapper for Jev
current structured_json adapter reuse for Jev
v2_semantic_linker_model=typesafe/jev-1.13
semantic_linker.py product change
BindingGate product change
Manager semantics product change
TypedTemporalNormalizer Jev routing
case019-specific tuning
hidden fallback/cascade
```

Native Jev surface is OpenRouter Decisions API (`POST /api/alpha/decisions`) using state + typed choice questions.

Benchmark contract:
```text
same frozen candidate sets
same user surfaces
A = google/gemini-2.5-flash-lite structured decision
B = typesafe/jev-1.13 native Decisions API
C = openai/gpt-5.6-sol structured decision
output = supplied candidate_id | ABSTAIN
TemporalNormalizer = excluded
Manager = excluded
```

Required metrics:
- selection accuracy, ABSTAIN precision/recall, ambiguity unsafe-pick, candidate escape, Turkish paraphrase accuracy, metamorphic consistency, repeated-run agreement, p50/p95, cost, provider failure;
- Jev raw probabilities + calibration metric (Brier/ECE or equivalent) + high-confidence-wrong count.

J1A P0:
```text
candidate outside supplied set = 0
silent ambiguity auto-pick = 0
cross-tenant semantic leak = 0
high-confidence wrong accepted = 0
semantic authority minted by model = 0
```

No production confidence threshold is created in J1A. Threshold calibration/tuning requires a later explicit ticket and a separate set.

Decision:
```text
Jev poor / Turkish weak
  → REJECT
  → product code unchanged
  → resume freeze sequence

Jev promising
  → D65-J1B
  → SemanticLinkDecisionProvider seam
  → SEMANTIC_LINKER and TEMPORAL_NORMALIZER physically separate
  → focused/family/workers1/canary/sentinel revalidation
  → only then freeze candidate
```

D65-J1 and D65-X are orthogonal:
```text
D65-J1 = cognition / bounded decision model
D65-X  = analytics execution substrate
```

## 12. Exact engineering closure sırası

Current repo sequencing, yeni runtime-kernel kararıyla birlikte bağlayıcıdır.

1. D65-E1 exact semantic-SHA recertification — **DONE GREEN 70/70**.
2. D65-E2 `SemanticCatalogRetriever` seam — **DONE GREEN 9/9**.
3. D65-E3A minimal `BoundedAgentRuntimeKernel`.
4. Current `standard_builder.py` loop mechanics'i kernel consumer olacak şekilde re-home et; semantic behavior değiştirme.
5. D65-E3B Standard profile/tool surface; DIRECT yalnız outcome/telemetry.
6. D65-E3C lightweight StandardProjection compiler — mevcut implementation korunur/uyarlanır.
7. D65-E4 minimal `AcceptedStandardAuthority`; Research body mevcut `AcceptedTurnContract`.
8. D65-E5 narrow final Standard CoverageVeto.
9. Provider-free failure-family closure.
10. Workers=1 small focused live architecture set.
11. Gerektiğinde exact-same-SHA fast/reference model-floor A/B.
12. 12–16 stratified canary.
13. D65-J1A isolated Jev/Gemini/Sol candidate-selection bake-off — lab/eval only.
14. Jev promising only: D65-J1B DecisionProvider seam + semantic/temporal role separation + focused/family/live/canary revalidation.
15. Real Wren Standard vertical + existing Research sentinel/revalidation.
16. Exact SHA = ENGINEERING FREEZE CANDIDATE.
17. DEV80 exactly once for that freeze candidate.
18. Fail → family clustering; named-case patch yok; code change = yeni candidate + yeni DEV80.
19. Phase thresholds + P0 gates green → **DAY 6.5 ENGINEERING CLOSED / ARCHITECTURE FROZEN**.
20. Day 7 lab/flag frozen architecture üzerinde ilerleyebilir.
21. **D65-X analytics substrate challenger:** same Dima/authority/projection ile Wren incumbent vs thin Metabase Agent API adapter.
22. Wren wins/tie → Wren stays; Metabase clearly wins → certification STOP, new engineering candidate + affected gates/new DEV proof.
23. Tuning olmadan VALIDATION50.
24. Validation fail + code change → certification invalid, engineering reopen, fresh validation.
25. External fresh HIDDEN50.
26. Hidden fail + architecture/code change → new external sealed corpus.
27. Green → DAY 6.5 CERTIFICATION SEALED.
28. Ancak sonra production hybrid `/ask-v2` activation.

### 12.1 Current sequencing exception — NO ROLLBACK

Runtime-kernel kararı geldiğinde E3/E4/E5'in bazı vertical'ları zaten yazılmış ve focused green idi:

- StandardBuilder core: 20/20 focused GREEN.
- Standard authority split: 25/25 focused GREEN.
- narrow CoverageVeto: 16/16 focused GREEN.

Bunlar geri alınmaz. Ancak kernel öncesi loop mechanics architecture-sealed sayılmaz. Sıradaki product ticket: `D65-E3A-R — runtime-kernel realignment`.


### 12.2 D65-X mandatory Metabase source preflight

Bu madde sequence'e yeni faz eklemez; mevcut **D65-X** adımının giriş kapısıdır.

D65-X veya Metabase'e dayanan herhangi bir önemli karar başlamadan önce
`DIMA_DAY6_5_RUNTIME_KERNEL_AND_SUBSTRATE_DECISION.md §17A` eksiksiz uygulanır.

Minimum preflight:

```text
canonical repo = metabase/metabase
declared source SHA verified
required six canonical source files inspected
local checkout (if any) SHA verified and treated read-only/non-authoritative
Agent API contract inspected
permission/query guards inspected
current version/runtime/deployment behavior externally re-verified where changeable
Dima trust-plane cross-check recorded
source-copy/port/vendor = 0
```

Execution measurement yapılacaksa receipt başlamadan önce şunların nasıl pinleneceği belli olmalıdır:

```text
source_reference_sha
runtime_version
runtime_image_digest
Dima tested SHA
adapter SHA
benchmark/corpus version
tenant/user permission context
```

Bu preflight PASS olmadan Metabase adapter/bake-off implementation'ı veya sonucu authority sayılmaz.

## 13. STOP-THE-LINE

Aşağıdakilerden biri olursa feature geliştirme durur ve abstraction düzeltilir:

- second semantic authority,
- Standard kernel'in Research semantics öğrenmesi,
- silent USER requirement loss,
- unsafe standard admission,
- blocking ambiguity auto-pick,
- rejected Standard authority Research'e taşınması,
- candidate-set dışı canonical truth,
- raw SQL/direct DB authority,
- cross-tenant/context handle,
- post-acceptance raw prompt semantic reparse,
- unverified numeric truth,
- evidence'siz VERIFIED completion,
- model-specific production branch,
- silent fallback,
- Wren + Metabase equal production truth engines.

Tek benchmark failure yeni architecture icat etme gerekçesi değildir.

## 14. Kapanış tanımı

Engineering closure ile certification seal ayrıdır. Phase quality gate'leri eval manifestte
**run başlamadan önce dondurulur**; sonuç görüldükten sonra eşik değiştirilemez.

Başlangıç architecture/reference-model phase gate:

```text
DEV80 semantic case pass >= 0.95
DEV80 MUST recall        >= 0.95
VALIDATION50 case pass   >= 0.95
VALIDATION50 MUST recall >= 0.95
HIDDEN50 case pass       >= 0.95
HIDDEN50 MUST recall     >= 0.95
adaptive cases           >= 0.90 where applicable
all P0 authority/security/silent-wrong counters = 0
```

```text
ENGINEERING CLOSED
= runtime-kernel + Standard/Research boundary + provider-free + focused/live
  + stratified canary + real Wren + DEV80 phase gate green for exact freeze candidate

SUBSTRATE DECISION COMPLETE
= D65-X isolated Wren-vs-Metabase substrate experiment resolved to one primary engine

CERTIFICATION SEALED
= same frozen architecture/substrate + fresh unbiased VALIDATION50
  + external fresh HIDDEN50 green
```

Production hybrid route yalnız certification seal sonrasında açılır.
