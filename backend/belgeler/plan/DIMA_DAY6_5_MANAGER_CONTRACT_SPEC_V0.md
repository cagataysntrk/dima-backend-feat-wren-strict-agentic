# DIMA DAY 6.5 — MANAGER CONTRACT SPEC V0

**Status:** PREPARED / NON-EXECUTABLE SPEC  
**Purpose:** Day 6.5 implementation boyunca owner sınırlarını sabitlemek.

Bu dosya production code değildir. Manager implementasyonu başlamadan önce veri
sözleşmelerini, authority sınırlarını ve lifecycle'ı dondurur.

---

## 1. Owner map

| Decision | Single owner |
|---|---|
| raw user intent cognition | ManagerRuntime |
| proposed obligation/exclusion | ManagerRuntime |
| obligation acceptance | IntentAcceptanceGate |
| canonical semantic binding | SemanticResolver |
| opaque handle issuance | SemanticHandleRegistry |
| standard vs research representability | RepresentabilityGate |
| task/tool compatibility | ResearchToolContract gate |
| query planning | Planner |
| relationship/grain safety | CrossDomainJoinGate |
| authorization | OfficialExecutionBoundary |
| numeric truth | Wren / DB / approved engine |
| evidence validity | Evidence contract / validator |
| completion state | CompletionGate |
| final wording | Finalizer |

No owner repeats another owner's semantic decision.

---

## 2. Core enums

### ObligationPriority

```text
MUST
SHOULD
```

### ObligationPolarity

```text
REQUIRED
EXCLUDED
```

### ObligationStatus

```text
PROPOSED
ACCEPTED
NEEDS_CLARIFICATION
SEMANTIC_BLOCKED
READY
IN_PROGRESS
EVIDENCE_BACKED
DATA_GAP
UNSUPPORTED
SUPERSEDED
```

### AcceptanceDecision

```text
ACCEPT
REJECT
NEEDS_CLARIFICATION
```

### RepresentabilityDecision

```text
STANDARD_LOSSLESS
RESEARCH_REQUIRED
NEEDS_CLARIFICATION
UNSUPPORTED
```

### CompletionStatus

```text
VERIFIED_COMPLETE
PARTIAL
FAILED
```

---

## 3. SourceEvidenceRef

Manager'ın proposal'ı kaynaksız authoritative olamaz.

Minimum:

```python
class SourceEvidenceRef:
    source_message_id: str
    source_span_id: str
    quoted_surface: str
```

Rules:
- source span current/prior authorized conversation source'a ait olmalı,
- exact source surface audit için saklanabilir,
- source evidence canonical semantic truth değildir,
- downstream worker raw prompt'u reparse etmez.

---

## 4. CandidateObligation

```python
class CandidateObligation:
    obligation_id: str
    kind: str
    priority: MUST | SHOULD
    polarity: REQUIRED | EXCLUDED
    source_refs: list[SourceEvidenceRef]
    scope_refs: list[str]
    semantic_handle_refs: list[str]
    open_questions: list[str]
```

Manager yalnız candidate üretir.

Invariant:
- source_refs boşsa ACCEPTED olamaz,
- EXCLUDED obligation executable task'a dönüşemez,
- semantic_handle_refs yalnız registry-issued olabilir.

---

## 5. UserIntentEnvelope

Bir turn için cognition workspace.

```python
class UserIntentEnvelope:
    turn_id: str
    source_message_id: str
    candidate_obligations: list[CandidateObligation]
    candidate_exclusions: list[CandidateObligation]
    requested_deliverables: list[CandidateObligation]
    scope_constraints: list[CandidateObligation]
    ambiguities: list[AmbiguityRecord]
    conversation_refs: list[str]
```

Bu nesne authoritative değildir.

Amaç:
- perfect execution AST değil,
- kullanıcıya borçlu olduğumuz yüksek seviye işleri kaybetmemek.

---

## 6. UserObligationLedger

```python
class ObligationLedgerItem:
    obligation_id: str
    version_introduced: int
    priority: MUST | SHOULD
    polarity: REQUIRED | EXCLUDED
    status: ObligationStatus
    source_refs: list[SourceEvidenceRef]
    semantic_handle_refs: list[str]
    evidence_refs: list[str]
    blocker: str | None
    superseded_by: str | None
```

Invariants:
- accepted MUST hiçbir lifecycle geçişinde sessiz silinmez,
- repair yeni contract version yaratır,
- superseded item historical audit'te kalır,
- completion bütün active MUST item'lara göre hesaplanır.

---

## 7. SemanticHandle

Opaque handle:

```python
class SemanticHandle:
    handle_id: str          # sem_<opaque>
    target_kind: str
    resolver_provenance_id: str
    context_version: str
    sensitive: bool
```

Manager'a canonical_name zorunlu olarak gösterilmez.

Registry:
- handle yalnız SemanticResolver sonucu ile mint edilir,
- unknown/expired context handle kullanılamaz,
- tenant/context crossing yasak,
- handle'dan canonical target çözümü trust plane içinde yapılır.

---

## 8. CandidateTurnContract

Runtime tarafından Manager proposal'larından assemble edilir.

```python
class CandidateTurnContract:
    turn_id: str
    candidate_obligation_ids: list[str]
    exclusion_ids: list[str]
    scope_ids: list[str]
    deliverable_ids: list[str]
    unresolved_ids: list[str]
    context_version: str
```

Manager doğrudan AcceptedTurnContract yazamaz.

---

## 9. IntentAcceptanceGate

Inputs:
- CandidateTurnContract
- source evidence
- obligation ledger
- semantic handle registry
- conversation state
- context version

Checks:
1. source evidence exists,
2. excluded/required contradiction,
3. duplicate obligation identity,
4. unresolved blocking ambiguity,
5. semantic handle provenance,
6. tenant/context compatibility,
7. missing MUST source,
8. supersession consistency.

Outputs:

```text
ACCEPT
REJECT
NEEDS_CLARIFICATION
```

No LLM-owned bypass.

---

## 10. AcceptedTurnContract

Immutable.

```python
class AcceptedTurnContract:
    contract_id: str
    version: int
    supersedes: str | None
    turn_id: str
    obligation_ids: tuple[str, ...]
    exclusion_ids: tuple[str, ...]
    scope_ids: tuple[str, ...]
    deliverable_ids: tuple[str, ...]
    unresolved_ids: tuple[str, ...]
    context_version: str
    accepted_at: datetime
```

Versioning:
- update/mutation yok,
- repair → new version,
- old contract immutable,
- active pointer conversation state'te tutulur.

---

## 11. RepresentabilityGate

Manager cognition ile product route ayrımı.

Input:
- AcceptedTurnContract
- obligation ledger
- semantic handle registry
- Core capability declaration

Decision:
- STANDARD_LOSSLESS
- RESEARCH_REQUIRED
- NEEDS_CLARIFICATION
- UNSUPPORTED

Rules:
- raw message length yok,
- keyword/regex yok,
- presentation type tek başına research sebebi değil,
- Core bütün MUST obligations'ı lossless taşıyabiliyorsa Standard,
- Core bir MUST operation'ı temsil edemiyorsa Research veya Unsupported,
- unresolved blocker varsa clarification/unsupported.

---

## 12. Manager action contract

Manager runtime yalnız declarative action önerir:

```text
PROPOSE_OBLIGATION
PROPOSE_EXCLUSION
REQUEST_CLARIFICATION
RESOLVE_SEMANTIC
INSPECT_CAPABILITY
PROPOSE_ACCEPTANCE
PROPOSE_TASK
STOP
```

Her action:
- action_id,
- turn_id,
- source/obligation refs,
- bounded args,
- declared cost,
- result state

taşır.

Raw SQL action YOK.

---

## 13. Day 6.5 validation tool contracts

### resolve_semantic

Input:
- source evidence ref
- semantic mention kind hint (optional)

Output:
- RESOLVED SemanticHandle
- AMBIGUOUS candidates
- GAP

Canonical ref'i Manager seçmez.

### inspect_capability

Input:
- obligation kind
- semantic handles

Output:
- supported capability descriptors
- required missing data/semantic model
- no execution

### request_clarification

Input:
- ambiguity id
- typed reason
- user-facing concise question

Output:
- clarification state

### propose_acceptance

Input:
- candidate obligation ids

Output:
- proposal only

### inspect_obligation_status

Input:
- obligation ids

Output:
- lifecycle snapshot

---

## 14. Day 7+ execution tool boundary

Day 6.5 Manager runtime gerçek query yapmak zorunda değildir.

Day 7'de:

```text
PROPOSE_TASK
→ ResearchToolContract
→ permission / budget
→ OfficialExecutionBoundary
→ EvidenceArtifact
```

Manager tool output ile execution output farklı contract'lardır.

---

## 15. Adaptive cognition proof

Day 6.5'te gerçek DB şart olmadan şu davranış kanıtlanmalı:

```text
obligation accepted
→ task A proposed
→ governed evidence says hypothesis weak
→ Manager observes typed evidence summary
→ proposes task B
→ obligation coverage improves
```

Pozitif architecture proof:
Manager aynı başlangıç planını kör çalıştırmaz.

Negatif proof:
Manager evidence'i kullanarak trust-plane'in doğrulamadığı canonical/numeric iddia üretemez.

---

## 16. CompletionGate

Inputs:
- active AcceptedTurnContract
- obligation ledger
- evidence refs
- blockers
- failure records

Rules:

```text
all active MUST evidence-backed
→ VERIFIED_COMPLETE

some MUST evidence-backed
+ at least one explicit data/semantic/tool gap
→ PARTIAL

no valid route / fatal trust-plane failure
→ FAILED
```

Manager'ın "bitti" demesi yalnız STOP proposal'dır; terminal status değildir.

---

## 17. Security and isolation

Mandatory:
- tenant scoped handles,
- principal explicit through execution boundary,
- context-version match,
- no handle reuse cross tenant,
- no raw SQL manager tool,
- no arbitrary tool id,
- no hidden direct DB connector,
- bounded call/query budgets,
- audit of action/tool/result IDs.

---

## 18. Persistence / audit

Persist:
- AcceptedTurnContract versions,
- obligation lifecycle transitions,
- semantic handle provenance refs,
- Manager action summaries,
- tool calls/results,
- evidence refs,
- completion state.

Do NOT persist/show:
- hidden chain-of-thought,
- unrestricted model scratchpad,
- provider-private reasoning tokens.

---

## 19. Test matrix

### Contract unit
- immutable versioning,
- supersession,
- excluded not executable,
- source-less accept rejected,
- foreign handle rejected,
- expired context handle rejected,
- completion partial correctness.

### Metamorphic
- opaque semantic names permutation,
- tenant A/B handle isolation,
- obligation ids permutation,
- same invariant under different domain nouns.

### Manager runtime
- clarify ambiguity,
- preserve 4/4 obligations,
- exclusion repair,
- evidence-triggered replan,
- budget stop,
- unsupported capability,
- no tool bypass.

### Representability
- simple metric/breakdown → STANDARD_LOSSLESS,
- ranking/comparison Core-capable → STANDARD_LOSSLESS,
- relationship/root-cause complex → RESEARCH_REQUIRED,
- unresolved ambiguity → NEEDS_CLARIFICATION.

---

## 20. Non-goals for Day 6.5

- full ReportDocument,
- causal engine,
- unrestricted autonomous agent,
- arbitrary web search,
- optimizer,
- raw SQL agent,
- final Day 7 ResearchTool ecosystem,
- migration/deletion of old P9 code.

Day 6.5 validates and seals the Manager control plane architecture.
