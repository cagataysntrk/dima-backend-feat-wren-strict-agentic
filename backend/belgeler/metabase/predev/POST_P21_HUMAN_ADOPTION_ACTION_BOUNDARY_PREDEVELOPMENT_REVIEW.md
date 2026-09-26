# POST-P21 — HUMAN ADOPTION / ACTION BOUNDARY PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-26  
**Status:** **PRE-DEVELOPMENT REVIEW COMPLETE / IMPLEMENTATION NOT AUTHORIZED**  
**Consumes:** sealed P21 DecisionBrief authority + historical legacy DecisionRecord audit  
**Production code:** 0  
**Tables/migrations:** 0  
**Model calls:** Luna = 0 / Sol = 0 / C1 = 0  
**Action execution / external side effects:** 0  
**UI/UX:** NOT AUTHORIZED

## 1. Boundary and core fact

The sealed authority chain now ends at advisory decision intelligence:

```text
P20 ReportDocument
→ P21 DecisionBrief
→ human/authorized-actor adoption truth
→ separately authorized Action
→ later Outcome
→ later Memory
```

Permanent:

```text
P21 RECOMMENDATION != HUMAN-ADOPTED DECISION
HUMAN-ADOPTED DECISION != ACTION EXECUTION
```

The exact durable fact future product work needs is:

```text
one authorized actor,
under one tenant/policy context,
responded to one exact immutable DecisionBrief/fingerprint,
with one explicit disposition,
at one recorded time.
```

Recommended typed dispositions:

```text
ACCEPTED
REJECTED
MODIFIED
DEFERRED
```

A recommendation being generated, viewed, clicked or sent is not adoption. Absence of rejection is
not adoption. An Action execution is not retroactive proof that adoption occurred.

No new phase number is assigned by this review.

## 2. Legacy DecisionRecord re-audit

Existing historical surfaces:

```text
backend/control_plane/models.py :: DecisionRecord
backend/app/decision.py
backend/app/routers/decisions.py
```

Useful historical semantics include tenant/user identity, timestamp, chosen/options, rationale/note,
append-only supersession and content-hash integrity.

However the same record is materially coupled to the old analytical/replay model:

```text
contract_ids_json → legacy Query Contract evidence
sablon_json       → cube_query replay template
POST /decisions/{did}/kos → legacy analytical replay behavior
```

Therefore:

```text
legacy DecisionRecord
= HISTORICAL COMPATIBILITY

legacy DecisionRecord
!= modern DecisionBrief adoption source of truth
```

Do not repurpose, rename, silently migrate or add DecisionBrief authority semantics to it.

A future narrow compatibility adapter may expose/import historical decisions, but it must keep modern
adoption truth separate from Query Contract / Cube replay semantics.

## 3. Recommended future adoption authority

If implementation is later authorized, prefer one narrow immutable adoption fact family,
conceptually:

```text
DecisionAdoptionRecord
```

This is a conceptual recommendation only. No table or production code is authorized by this review.

Minimum identity/state should include:

```text
adoption_id
decision_brief_id
source_brief_fingerprint
tenant_binding

actor_user_id
actor_authorization_context
approval_policy_id / version when applicable
delegation_ref nullable

disposition:
  ACCEPTED | REJECTED | MODIFIED | DEFERRED

selected_option_ids
human_rationale
modification_json nullable

supersedes_adoption_id nullable
recorded_at
adoption_fingerprint
```

The record must be immutable. Revocation or change is a new record that supersedes prior adoption
truth; never update the old adoption event in place.

## 4. DecisionBrief identity and staleness

Adoption binds one exact DecisionBrief id + fingerprint.

If the DecisionBrief is stale or superseded before adoption, a new adoption must fail closed and
require a current DecisionBrief.

If an already-adopted brief later becomes stale, the historical adoption remains true as history but
must not silently authorize new Action execution. A future Action gate should require explicit
revalidation/re-adoption under current governed truth.

## 5. Disposition semantics

```text
ACCEPTED
= actor explicitly accepts the referenced DecisionBrief recommendation/selected option set

REJECTED
= actor explicitly rejects it
= no Action authority

DEFERRED
= actor intentionally postpones a decision
= no Action authority

MODIFIED
= actor adopts a structured variation inside the governed DecisionBrief option surface
```

MODIFIED must not become a free-text escape from governed decision context.

A safe first boundary is that the actor may select a different subset of options already present in
the DecisionBrief and/or add explicit human conditions/rationale. If the desired option is absent,
require a new DecisionBrief revision before adoption rather than smuggling an unreviewed factual or
action premise into the adoption record.

Human rationale remains human rationale. It does not become analytical Evidence, P20 fact or P21
factual premise.

## 6. Actor identity, tenant and authorization

Adoption requires explicit authenticated actor authorization.

Future authority must bind:

```text
authenticated actor identity
tenant
role / capability
approval policy/version
delegation, if any
DecisionBrief identity/fingerprint
```

Never trust actor/user/tenant identifiers supplied only by request payload.

Cross-tenant adoption must fail without revealing the foreign DecisionBrief or adoption record.

## 7. Approval policy, dual approval and delegation

Do not hard-code dual approval globally.

Approval should be an explicit governed organizational policy that may depend on action risk, amount,
target system, reversibility or organizational role. The adoption record should capture the exact
policy/version under which adoption was accepted.

If policy requires multiple approvers, one actor event is not sufficient to become
execution-eligible. The aggregate approval result must be deterministically derived from immutable
actor events or a separately reviewed approval authority.

Delegation must be explicit and auditable:

```text
delegator
delegate
scope
tenant
valid-from / valid-until
policy/version
revocation
```

A delegated actor may adopt only inside that exact scope. Do not infer delegation from role
similarity, manager hierarchy prose or UI possession.

No approval/delegation implementation is authorized here.

## 8. Revocation and supersession

Adoption history is append-only:

```text
old adoption
→ remains historical

revocation / changed adoption
→ new immutable record
→ supersedes prior adoption
```

Revocation is not deletion.

A future Action gate must resolve the latest valid adoption authority before permitting a new side
effect.

## 9. Does adoption itself create Action authority?

Recommended boundary:

```text
NO.
```

Adoption is a necessary business-decision fact, not sufficient permission to execute an external side
effect.

Reasons include:
- an accepted decision may intentionally remain unexecuted;
- the executor may require a narrower capability than the adopter;
- irreversible/high-risk operations may require confirmation close to execution;
- credentials, target-system scope and idempotency are execution concerns;
- a DecisionBrief may become stale after adoption but before execution.

Therefore:

```text
valid adoption
= prerequisite for future Action authorization

valid adoption
!= automatic execution authorization
```

## 10. ActionPlan versus executed Action

Future design should distinguish:

```text
ActionPlan
= side-effect-free specification of what would be done

Action execution / attempt
= an actual side effect against an external or internal operational system
```

Creating or reviewing an ActionPlan must not itself execute anything.

The plan should bind the exact adoption authority and DecisionBrief lineage that justifies it.

## 11. Future Action authorization gate

Before any external side effect, future Action authority should validate:

```text
current valid adoption exists
adoption references exact DecisionBrief/fingerprint
DecisionBrief/P20 staleness policy is satisfied
actor/executor is authorized for the action class
required approval policy is satisfied
required confirmation is present
target system/resource is allowed
payload is bounded and typed
idempotency key is established
reversibility / rollback policy is known
```

No Action should execute because a model emitted prose suggesting it.

## 12. Reversibility and confirmation

Action types require an explicit risk/reversibility classification, conceptually:

```text
READ_ONLY
REVERSIBLE_WRITE
IRREVERSIBLE_OR_HIGH_RISK_WRITE
```

The class determines whether additional confirmation, dual approval, dry-run/preview or rollback
capability is required.

Risk class is policy. It must not be guessed from action text by regex/fuzzy/model heuristics.

## 13. External-system boundary

Future Action authority must use an explicit allowlist/capability model for external systems and
action kinds. No generic "call any tool/API" authority.

Credentials remain outside decision/adoption artifacts. Tenant and actor authorization must survive
all the way to the external execution boundary.

## 14. Retry and idempotency

External side effects need an execution identity distinct from DecisionBrief/adoption identity.

Future execution must use an idempotency key scoped at least to:

```text
adoption / action-plan identity
target system
action kind
bounded payload fingerprint
```

A retry must not accidentally execute the same irreversible effect twice.

"Request timed out" is not proof that the remote side effect did not happen.

## 15. Side-effect receipt

Do not reuse analytical `DimaQueryReceipt`.

A future Action execution needs a separately reviewed side-effect receipt concept recording, at
minimum:

```text
action / attempt identity
adoption authority identity
executor actor/service identity
target system/resource
bounded request fingerprint
idempotency key
started / completed timestamps
external correlation id when available
outcome status
response/result fingerprint
failure classification
rollback/refund/reversal reference when applicable
```

This is not implemented or declared as a durable table by this review.

## 16. Failure recording and rollback

Execution failure is an immutable event, not a reason to rewrite history.

Future design must distinguish:

```text
NOT_STARTED
ATTEMPTED
SUCCEEDED
FAILED
UNKNOWN_REMOTE_STATE
ROLLED_BACK / REVERSED
```

Unknown remote state must fail closed for automatic retry when duplicate side effects are possible.

Rollback/reversal is a separate side effect and must have its own authorization and receipt.

## 17. Approval versus execution separation

An adopter/approver may or may not be an executor.

A future Action authority must preserve:

```text
who adopted/approved
who authorized execution
who/what executed
when
under which policy
against which exact action payload
```

Never collapse those identities into one generic user field.

## 18. Outcome boundary

An Action execution receipt proves that an action was attempted/completed. It does not prove business
impact.

Future Outcome authority must separately observe governed post-action facts and relate them to the
Action identity.

Permanent:

```text
ACTION SUCCEEDED != DESIRED BUSINESS OUTCOME OCCURRED
```

Do not write Outcome or Memory logic inside an Action executor.

## 19. Model role

No model is required to establish human adoption truth or side-effect authorization.

A model may later propose ActionPlans only under separate authority, but deterministic policy must own
legality, permissions, adoption linkage, confirmation, idempotency and execution boundaries.

Model output alone never authorizes adoption or execution.

## 20. UI boundary

UI/UX remains unauthorized by this review.

Future UI may display DecisionBrief, request human adoption, show approval state or preview an
ActionPlan, but UI interaction must call explicit backend authorities. Button possession/click
presence is not authorization truth.

No UI work is opened here.

## 21. STOP conditions for future implementation

Stop if a future implementation would require:

```text
repurposing legacy DecisionRecord as modern source of truth
making cube_query replay adoption authority
treating P21 recommendation as implicit adoption
automatic action on DecisionBrief seal
action execution without explicit current adoption
generic external-tool execution
tenant/actor identifiers trusted from payload
model-generated permission or risk classification
reuse of analytical DimaQueryReceipt for side effects
mutable adoption/action history
silent retry after unknown remote state
Outcome/Memory ownership inside Action executor
UI as security authority
```

## 22. Recommended bounded next objective

No production work is authorized by this review.

If a supervisor later opens the next slice, the smallest coherent objective should be:

```text
one CURRENT sealed DecisionBrief
+ one authenticated/authorized actor
+ explicit typed adoption disposition
+ exact policy / tenant binding
→ deterministic adoption-legality gate
→ one immutable human-adoption fact
```

Still exclude Action execution from that first adoption slice.

After adoption authority is separately sealed, perform a fresh pre-development review for the first
ActionPlan / execution authority slice before any external side effect is enabled.

## 23. Review exit

```text
P21 = SEALED

POST-P21 HUMAN ADOPTION / ACTION BOUNDARY
PRE-DEVELOPMENT REVIEW = COMPLETE

human-adoption production code = 0
Action production code          = 0
tables/migrations               = 0
model calls                     = 0
external side effects           = 0
UI/UX                           = NOT AUTHORIZED
```

Return to supervisor before implementing adoption or Action.


## 24. DMP-DEC-0058 lifecycle — Human Adoption implementation authorization

The historical review status above remains the state at the time this review completed. Supervisor
authority on 2026-09-26 ratifies:

```text
DMP-DEC-0058
MINIMAL HUMAN ADOPTION AUTHORITY

RATIFIED /
MINIMAL PROVIDER-FREE IMPLEMENTATION AUTHORIZED
```

Implementation contract:

```text
CURRENT DecisionBrief
+ authenticated Principal
+ decision:adopt = analyst+
+ exact brief fingerprint
+ typed adoption disposition
+ exact existing option ids
→ AdoptionLegalityGate
→ one immutable DecisionAdoptionRecord
```

No Action implementation is authorized by DMP-DEC-0058.


## 25. DMP-DEC-0058 final closure — Human Adoption Authority SEALED

```text
behavior SHA                    = cbfc0fe792b6a6121d0a04c8ab819c289950af97
certified integration HEAD      = cbfc0fe792b6a6121d0a04c8ab819c289950af97
provider-free                   = 36222145155 SUCCESS
governance                      = 36222145158 SUCCESS
focused                         = 29 PASS
P21/P20/P19/P18                 = 25/19/42/24 PASS
P17/P16/P15/P14                 = 95/6/5/17 PASS
Alembic head                    = f9e6c4fa1052
DecisionAdoptionRecord families = 1
decision:adopt                  = analyst+
Action writes                   = 0
external side effects           = 0
model calls                     = 0
engine changes/builds           = 0/0
```

Status from this point:

```text
HUMAN ADOPTION AUTHORITY = SEALED
ACTION AUTHORITY = PRE-DEVELOPMENT NEXT
ACTION EXECUTION = NOT AUTHORIZED
UI/UX = NOT AUTHORIZED
```
