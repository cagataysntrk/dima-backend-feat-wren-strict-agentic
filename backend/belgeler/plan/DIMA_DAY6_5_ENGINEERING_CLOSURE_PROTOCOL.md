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

## 2. Üç çalışma modu, iki accepted-authority ailesi

```text
STANDARD_DIRECT
STANDARD_BUILDER
RESEARCH
```

Bunlar üç semantic authority ailesi değildir.

```text
AcceptedAuthority
├── AcceptedStandardAuthority
└── AcceptedResearchAuthority
```

- `STANDARD_DIRECT`: standard builder'ın lossless projection'ı hemen kurabildiği kısa yol.
- `STANDARD_BUILDER`: tek analytical request için bounded discovery/repair micro-loop.
- `RESEARCH`: multi-obligation / relationship / root-cause / adaptive evidence problemi.

`STANDARD_DIRECT` ve `STANDARD_BUILDER` aynı Standard authority'yi üretir.

`AcceptedResearchAuthority` yeni ikinci bir research semantic body DEĞİLDİR. Uygulamada mevcut `AcceptedTurnContract` research authority gövdesi olarak korunur; gerekiyorsa yalnız type alias / tagged-union etiketiyle `AcceptedResearchAuthority` adı verilir. Aynı research semantic gerçeği ikinci kez modellenmez.

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
→ real Wren Standard + Research sentinels
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

## 12. Exact engineering closure sırası

Current semantic code `c9629d9029db...` henüz önceki 70/70 run ile certify edilmedi.

Sıra bağlayıcıdır:

1. **EXACT CURRENT SEMANTIC-SHA RECERTIFICATION**: `c9629d...` focused provider-free cognition/authority closure,
2. green → checkpoint SHA,
3. `SemanticCatalogRetriever` seam; ilk backend current deterministic enumeration olabilir,
4. safe candidate card/internal binding ayrımını koru,
5. `StandardBuilder` bounded state machine; Direct = onun kısa yolu,
6. minimal `AcceptedStandardAuthority`; Research tarafında mevcut `AcceptedTurnContract` body korunur,
7. Standard/Research accepted-authority tagged union / owner split,
8. narrow final Standard CoverageVeto,
9. provider-free failure-family tests,
10. workers=1 small focused live architecture set,
11. gerektiğinde exact-same-SHA fast/reference model-floor A/B,
12. 12–16 stratified canary,
13. real Wren Standard vertical + existing Research sentinel,
14. exact SHA = ENGINEERING FREEZE CANDIDATE,
15. DEV80 **exactly once for that freeze candidate**,
16. fail → family clustering; named-case patch yok; code change olursa yeni freeze candidate ve yeni DEV80 gerekir,
17. phase thresholds + P0 hard gates green → DAY 6.5 ENGINEERING CLOSED / ARCHITECTURE FROZEN,
18. Day 7 lab/flag altında frozen architecture üzerinde açılabilir,
19. tuning olmadan VALIDATION50,
20. Validation fail + code change → certification invalid, engineering reopen, fresh validation gerekir,
21. external **fresh** HIDDEN50,
22. Hidden fail + architecture/code change → new external sealed corpus gerekir,
23. green → DAY 6.5 CERTIFICATION SEALED,
24. ancak sonra production hybrid `/ask-v2` activation.

## 13. STOP-THE-LINE

Aşağıdakilerden biri olursa feature geliştirme durur ve abstraction düzeltilir:

- second semantic authority,
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
- silent fallback.

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
= abstraction + provider-free + focused/live + stratified canary + real Wren
  + DEV80 phase gate green for the exact freeze candidate

CERTIFICATION SEALED
= same frozen architecture + fresh unbiased VALIDATION50
  + external fresh HIDDEN50 green
```

Production hybrid route yalnız certification seal sonrasında açılır.
