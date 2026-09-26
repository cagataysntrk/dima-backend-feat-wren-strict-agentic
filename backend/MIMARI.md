# Dima Metabase Platform — Canonical Architecture

**Branch:** `feat/dima-metabase-platform`  
**Canonical analytical engine:** Metabase / Metabot  
**UI state:** not implemented / forbidden under current authority

## 1. Ownership model

~~~text
METABASE / METABOT
= analytical computation
= analytical execution
= governed native analytical material

DIMA CORE
= company/context meaning
= research orchestration
= evidence and claim governance
= investigation and epistemics
= report and decision authority
= human adoption
= internal work/outcome/memory/watch closed loop
= headless product projection/orchestration
~~~

Dima does not reproduce Metabase analytical primitives.

## 2. Sealed authority chain

~~~text
P14 Research
→ P15 native Exploration material
→ P16 Claim / Evidence lineage
→ P17 Investigation
→ P18 Relationship Policy
→ P19 Epistemics / Root-Cause Assessment
→ P20 Governed Report
→ P21 DecisionBrief
→ Human Adoption
→ optional ActionAuthorization
~~~

Key boundaries:

~~~text
P17 investigation graph != causal graph
P18 relationship direction != causality
P19 epistemics may conclude no defensible root cause
P20 report cannot strengthen source semantics
P21 recommendation != human decision
Decision != Human Adoption
Adoption != external execution
~~~

## 3. Core Closure A — sealed closed loop

~~~text
ActionWork
= internal organizational commitment lifecycle
= no connector execution

OutcomeObservation
= governed observation over analytical provenance
= Outcome != causality
= no local KPI calculation

InstitutionalMemoryEntry
= references to governed artifacts + context + precedent
= Memory != truth authority

Watch / Signal
= governed observation/context intake and business significance
= Watch != analytics engine
~~~

Core A durable families are limited to its sealed five-family model:
ActionWork, OutcomeObservation, InstitutionalMemoryEntry, Watch and Signal.

## 4. Core Closure B — active forward architecture

Core B is the stable headless product layer over sealed owners. Preferred package:
`app/v3/product/`.

It owns no new business truth. It owns:

~~~text
DTOs
company/context projection
capability discovery
navigation/deep links
correlation/request identity
typed product errors
deterministic pagination
resume
artifact timeline projection
closed-loop orchestration
observability/audit projection
~~~

Required headless product objects include Company Context, Capabilities, Ask/Research, Watch, Signal,
Investigation, Evidence, Report, Decision, Adoption, ActionWork, Outcome, Memory and Artifact
Timeline.

### Resume

~~~text
RESUME != RAW PROMPT REINTERPRETATION
~~~

Resume starts from durable IDs/artifacts and reauthorizes the current Principal.

### Timeline

~~~text
TIMELINE = PROJECTION
~~~

No timeline truth table unless a measured blocker proves it unavoidable.

## 5. Product error taxonomy

Core B normalizes product-facing errors into:

~~~text
UNAVAILABLE
FORBIDDEN
STALE
SUPERSEDED
INVALID_TRANSITION
INSUFFICIENT_EVIDENCE
INCONCLUSIVE
DEFERRED_CAPABILITY
UNKNOWN_OUTCOME
~~~

Cross-tenant existing and missing identities preserve non-oracle behavior.

## 6. Analytics and causality invariants

~~~text
analytics != organizational authority
observed improvement != action caused improvement
Outcome != causality
Memory != current truth
Watch/Signal != metric computation
Report/Decision projections != new Evidence
~~~

Any numerical/analytical fact must ultimately trace to governed Metabase/Metabot analytical
provenance and the sealed authority chain.

## 7. Security

Tenant, actor and roles come from authenticated `Principal`, never request payload. Historical
access does not imply current access. Every protected resume/read rechecks current authorization.

## 8. External execution

External production execution is deferred. `action:execute` is absent. The default
ActionCapability registry remains closed. Resend provider-free work is productization debt, not a
Core B blocker.

## 9. Engine identity

Pinned engine gitlink:

`cbe313af9ac2d5960f662068e433d328d896fb06` — release `0.63.18-dima.6`.

No Wren runtime, Wren source substrate, Wren bake-off or dual-engine product architecture exists in
the canonical forward design.

## 10. Certification sequence

~~~text
repository canonicalization
→ Core B headless product engine
→ persistence/resume/currentness/security
→ 24+ deterministic closed-loop rehearsal
→ hardest-case rehearsal
→ pre-DEV80 freeze candidate
→ STOP
~~~

DEV80 is not run under the current directive. UI implementation does not open automatically after
backend readiness.
