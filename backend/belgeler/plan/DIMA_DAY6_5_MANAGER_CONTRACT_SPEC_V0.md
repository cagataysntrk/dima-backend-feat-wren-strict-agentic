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

### ObligationOrigin

```text
USER_MUST
USER_OPTIONAL
SYSTEM_REQUIRED
AGENT_DERIVED
```

### ObligationStatus

```text
PROPOSED
ACCEPTED
NEEDS_CLARIFICATION
READY
IN_PROGRESS
VERIFIED
BLOCKED_DATA_GAP
LIMITED
UNSUPPORTED
SUPERSEDED
```

Evidence varlığı status değildir; `evidence_refs` ayrı alandır.

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

## 3. SourceSpanRegistry / SourceSpanRef

Manager'ın proposal'ı kaynaksız authoritative olamaz ve Manager source evidence
uyduramaz.

Runtime current/prior authorized message üzerinde span registry üretir:

```python
class SourceSpanRef:
    source_ref: str          # src_<opaque>
    message_id: str
    message_hash: str
    start_offset: int
    end_offset: int
    exact_surface: str
```

Rules:
- source ref yalnız runtime registry tarafından mint edilir,
- offsets/hash/exact_surface gerçekten kaynak mesajla doğrulanır,
- Manager yalnız `src_<opaque>` ref kullanır,
- source evidence canonical semantic truth değildir,
- downstream worker raw prompt'u reparse etmez.

---

## 4. CandidateObligation

```python
class CandidateObligation:
    obligation_id: str
    capability_key: str
    origin: ObligationOrigin
    parent_obligation_id: str | None
    priority: MUST | SHOULD
    polarity: REQUIRED | EXCLUDED
    source_refs: list[SourceSpanRef]
    scope_refs: list[str]
    semantic_handle_refs: list[str]
    open_questions: list[str]
```

Manager yalnız candidate üretir.

Invariant:
- source_refs boşsa ACCEPTED olamaz,
- `capability_key` CapabilityRegistry'de kayıtlı değilse REJECT,
- EXCLUDED obligation executable task'a dönüşemez,
- semantic_handle_refs yalnız registry-issued olabilir,
- `AGENT_DERIVED` obligation `USER_MUST`'a promote edilemez,
- `AGENT_DERIVED.parent_obligation_id` accepted parent'a bağlanır.

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
    capability_key: str
    origin: ObligationOrigin
    parent_obligation_id: str | None
    priority: MUST | SHOULD
    polarity: REQUIRED | EXCLUDED
    status: ObligationStatus
    source_refs: list[SourceSpanRef]
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
    tenant_binding: str
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
    lineage_id: str
    contract_schema_version: str
    version: int
    supersedes_contract_id: str | None
    turn_id: str
    request_ref: str
    source_message_hash: str
    accepted_attempt_id: str
    model_role: str
    obligation_ids: tuple[str, ...]
    exclusion_ids: tuple[str, ...]
    scope_ids: tuple[str, ...]
    deliverable_ids: tuple[str, ...]
    unresolved_ids: tuple[str, ...]
    context_version: str
    accepted_at: datetime
```

Versioning / authority:
- update/mutation yok,
- `version` aynı `lineage_id` içinde monoton artar,
- repair → new version,
- old contract immutable,
- active pointer conversation state'te tutulur,
- accepted non-clarification turn başına exactly one active accepted contract,
- rejected model attempt hiçbir semantic field'i accepted attempt ile merge edemez.

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
- obligation verdict/status
- blockers
- failure records

Rules:

```text
all active USER_MUST == VERIFIED
→ VERIFIED_COMPLETE

all active USER_MUST accounted for
+ at least one BLOCKED_DATA_GAP / UNSUPPORTED / LIMITED
→ PARTIAL

unaccounted USER_MUST
→ finish rejected

no valid route / fatal trust-plane or authority failure
→ FAILED
```

`evidence_refs != []` tek başına `VERIFIED` değildir. Evidence bir hipotezi reddedebilir,
inconclusive olabilir veya yalnız limitation kanıtı olabilir.

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

### Representability / fast path
- simple metric/breakdown → STANDARD_LOSSLESS,
- ranking/comparison Core-capable → STANDARD_LOSSLESS,
- relationship/root-cause complex → RESEARCH_REQUIRED,
- unresolved ambiguity → NEEDS_CLARIFICATION,
- unsafe_fast_admission = 0,
- simple standard Manager loop = 0,
- simple standard model calls <= 1,
- simple standard p95/cost <= Day5 baseline * 1.10,
- rejected attempt semantic merge = 0.

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


---

## 21. Semantic interpretation and binding contract — 2026-09-22 addendum

Canonical ADR:
`DIMA_DAY6_5_COGNITION_AUTHORITY_BOUNDARY_ADR.md`

### 21.1 Authority split

```text
Semantic Catalog                → what exists
SemanticCandidateGenerator      → bounded candidate cards, no authority
BoundedSemanticLinker           → SELECT(cand_*) | ABSTAIN
SemanticBindingGate             → validates candidate membership + tenant/context/kind
SemanticHandleRegistry          → mints sem_* after gate
```

A model selection is never executable authority by itself.

### 21.2 Candidate contract

Candidate cards are runtime-issued and bounded. A linker may only choose an opaque
`cand_*` present in the request-specific set.

Required properties:
- candidate belongs to current tenant/context catalog,
- target kind is compatible with requested kind,
- candidate set is bounded,
- sensitive entity values are not probabilistically exposed,
- candidate outside set is deterministic reject.

Unique exact verified alias may bypass model inference.
Multiple exact verified aliases → ambiguity; never score/rank to a winner.

Current scale safety:
`CANDIDATE_SET_TOO_BROAD` is fail-closed. Future candidate retrieval may improve recall,
but retrieval does not become semantic authority.

### 21.3 Temporal contract

Language owner emits only a closed temporal intent.
Calendar engine owns concrete dates.

```text
TypedTemporalNormalizer
→ TemporalIntent
→ TemporalBindingEngine
→ ResolvedPeriod / ResolvedComparison
→ mint_from_temporal_engine()
```

The model never calculates date boundaries.

### 21.4 Coverage contract

Coverage is omission-only veto:
- omitted requested obligation,
- omitted / incorrect explicit exclusion,
- omitted supported research directive.

Coverage cannot:
- select candidates,
- decide canonical semantics,
- decide semantic ambiguity,
- mint authority,
- directly establish user clarification truth.

### 21.5 open_questions

`open_questions` is advisory diagnostic metadata.
It is not a sufficient condition for `NEEDS_CLARIFICATION`.

Clarification requires a deterministic blocker such as missing required binding,
required parameter gap, deterministic effect conflict, unavailable trusted previous
authority, unsupported capability, or required bounded-linker abstention/ambiguity.

### 21.6 Semantic receipts

`SemanticResolutionReceipt` is an anti-laundering provenance receipt:
`source_ref ↔ handle_id ↔ target_kind`.

It MUST NOT be used as a completeness oracle.

### 21.7 Failure typing

Pre-acceptance model/grounding/harness failures remain distinct from semantic outcomes.
Evaluation with such failures is `incomplete`, not semantic `fail`.

### 21.8 Compatibility

Legacy `SemanticResolver` / `temporal.py` remain compatibility primitives for non-Manager
V2 paths. They are not the Day 6.5 Manager language-authority target.
