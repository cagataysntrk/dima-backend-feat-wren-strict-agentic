# ACTIONPLAN / ACTION AUTHORIZATION / EXECUTION AUTHORITY — PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-26  
**Status:** **PRE-DEVELOPMENT REVIEW COMPLETE / IMPLEMENTATION NOT AUTHORIZED**  
**Consumes:** sealed P21 DecisionBrief + sealed DMP-DEC-0058 Human Adoption authority  
**Production code:** 0  
**Tables/migrations:** 0  
**External side effects:** 0  
**Model calls:** Luna = 0 / Sol = 0 / C1 = 0  
**UI/UX:** NOT AUTHORIZED

## 1. Boundary

Permanent chain:

```text
DecisionBrief
→ DecisionAdoption
→ ActionPlan
→ ActionAuthorization
→ ActionExecutionAttempt / Receipt
→ later Outcome
```

Never collapse:

```text
ADOPTION != ACTION AUTHORIZATION
ACTION AUTHORIZATION != EXECUTION
EXECUTION SUCCESS != BUSINESS OUTCOME
```

## 2. Three distinct concepts

### ActionPlan

A typed canonical description of one proposed side effect.

It answers:

```text
what action kind?
which target system?
which exact typed parameters?
which DecisionBrief lineage?
which DecisionAdoption lineage?
which preconditions?
which governed risk class?
is it reversible?
what confirmation is required?
what idempotency strategy applies?
```

ActionPlan executes nothing.

### ActionAuthorization

A durable permission over one exact ActionPlan fingerprint.

It answers:

```text
who authorized?
under which policy/version?
which current DecisionAdoption?
which current DecisionBrief/P20 context?
which exact plan fingerprint?
which risk class?
which approvers?
until when is authorization valid?
```

### ActionExecutionAttempt / Receipt

A durable occurrence proving what exact authorized artifact was attempted and what the remote system
reported.

It is not analytical Evidence and must not reuse `DimaQueryReceipt`.

## 3. Recommended durable-state model

Do not create three tables by default.

Recommended first authority shape:

```text
ActionPlan = transient typed canonical artifact
             + deterministic plan fingerprint

ActionAuthorizationRecord = durable
  contains exact canonical ActionPlan snapshot/fingerprint
  + source DecisionBrief/DecisionAdoption lineage
  + authorizer/approval policy
  + risk/reversibility/expiry

ActionExecutionReceiptRecord = durable only when execution is later opened
  binds exact authorization + exact plan fingerprint
  + attempt identity + executor identity
  + target + timestamps + external reference + final/unknown status
```

No separate ActionPlan table is justified for the first slice.

Execution should not be implemented in the same first ActionAuthorization slice.

## 4. Required current governed context

At authorization time require all:

```text
P20 ReportDocument = CURRENT
P21 DecisionBrief = CURRENT
DecisionAdoption = CURRENT
```

If any becomes stale:

```text
BLOCK AUTHORIZATION
→ require refreshed governed upstream authority
```

Action code never recomputes analytics to repair staleness.

## 5. Facts changed after adoption

If the underlying report or DecisionBrief changes after Human Adoption:

```text
old adoption remains historical truth
old adoption becomes non-current for future Action authorization
new DecisionBrief requires a new human adoption
```

No silent carry-forward.

## 6. Authorization currentness before execution

Immediately before any external side effect, future executor must revalidate:

```text
tenant
exact ActionAuthorization identity
authorization not expired/revoked/superseded
exact ActionPlan fingerprint
CURRENT DecisionBrief
CURRENT DecisionAdoption
required approval policy/version
target identity
idempotency key
```

If governed context changed after authorization:

```text
BLOCK EXECUTION
→ require a new ActionAuthorization
```

## 7. Capability model

Do not implement generic `call arbitrary tool/API`.

Future Action capability must be registered as typed metadata:

```text
action_kind
target_connector/system
typed parameter schema
risk_class
reversibility
confirmation requirement
authorization policy
idempotency/reconciliation strategy
```

Unknown action kind = fail closed.

## 8. Risk classification

Risk comes from governed action-kind metadata, never:

```text
regex
fuzzy matching
LLM
free-text heuristics
```

Minimum classes:

```text
REVERSIBLE_LOW_RISK
REVERSIBLE_MATERIAL
IRREVERSIBLE_EXTERNAL_COMMIT
```

Read-only operations are not side-effect Action authority.

## 9. Who may authorize?

Do not reuse `decision:adopt`.

Future Action authority needs a distinct capability such as:

```text
action:authorize
```

Recommended baseline for future ratification:

```text
REVERSIBLE_LOW_RISK
→ admin+ / one authorized approver may suffice

REVERSIBLE_MATERIAL
→ admin+ with stronger policy; additional approval may be required

IRREVERSIBLE_EXTERNAL_COMMIT
→ explicit dual approval by default
→ at least one owner-level approver recommended
→ approvers must be distinct authenticated principals
```

Exact thresholds must be carried by a versioned policy, not hard-coded ad hoc in handlers.

## 10. Human Adoption requirement

ActionAuthorization requires an exact CURRENT `DecisionAdoption`.

An `ACCEPTED` adoption does not automatically authorize execution.

A `MODIFIED` adoption may authorize only actions derived from the selected existing option(s), after
the separate ActionPlan legality review.

`REJECTED` and `DEFERRED` cannot authorize Action.

## 11. ActionPlan canonical identity

Plan fingerprint must cover at least:

```text
tenant
action kind
target system/account/resource
typed parameters
DecisionBrief id/fingerprint
DecisionAdoption id/fingerprint
preconditions
risk class
reversibility
confirmation requirement
idempotency strategy metadata
```

Post-authorization reconstruction is forbidden.

LLM rewriting of the authorized payload is forbidden.

## 12. Execution identity invariant

Permanent:

```text
authorized artifact
==
executed artifact
==
receipted artifact
```

The executor receives the exact authorized canonical plan; it does not regenerate intent.

## 13. Retry and idempotency

Every material side effect requires explicit idempotency/reconciliation semantics before execution is
authorized.

Future execution state must distinguish:

```text
NOT_ATTEMPTED
ATTEMPTED
CONFIRMED
FAILED
UNKNOWN_EXTERNAL_STATE
```

Rules:

```text
timeout != failure
timeout != safe-to-retry
UNKNOWN_EXTERNAL_STATE → reconcile before retry
duplicate material execution = forbidden
partial success = explicit
compensation/rollback = new explicit authorized Action
```

If the connector cannot provide a stable idempotency key, external operation identity or reliable
reconciliation path, automated material execution is a STOP.

## 14. Attempt identity and receipt

Before an external call, future execution must allocate a stable attempt identity/idempotency key.

A future side-effect receipt must bind:

```text
ActionAuthorization id/fingerprint
ActionPlan fingerprint
attempt identity
executor identity
target system
exact canonical payload fingerprint
started_at / completed_at
external reference
execution status
failure / unknown-state detail
```

Do not reuse analytical `DimaQueryReceipt`.

## 15. Approval and execution separation

```text
adopter != automatically authorizer
plan creator != automatically authorizer
authorizer != automatically executor
executor credentials != authorization authority
```

Material/irreversible policy may enforce separation of duties.

No service account may self-authorize merely because it can call the target API.

## 16. Tenant and non-oracle

All ActionPlan/Authorization/Execution lookups must remain tenant scoped.

Foreign existing and missing identities must expose the same unavailable error family.

Tenant/actor/role authority comes from authenticated `Principal`, never request payload.

## 17. Authorization lifecycle

Recommended immutable authority semantics:

```text
new plan or changed parameters
→ new plan fingerprint
→ new ActionAuthorization

changed governed context
→ old authorization remains history
→ old authorization becomes non-current

revocation
→ explicit superseding/revocation authority event
```

Do not mutate history to pretend a different artifact had been authorized.

## 18. Outcome boundary

```text
ActionExecutionReceipt
= what side effect occurred / was attempted

Outcome
= what happened in the business afterward
```

Business Outcome observation remains governed analytics via Metabase/Metabot.

No Outcome analytics inside executor.

## 19. Model role

No model is required for permission correctness.

A future model may propose a typed ActionPlan only if separately authorized, but:

```text
model != risk classifier
model != permission authority
model != approver
model != payload rewriter after authorization
```

Deterministic policy owns legality.

## 20. Recommended first future implementation slice

If separately authorized, first implement:

```text
CURRENT P20
+ CURRENT P21
+ CURRENT DecisionAdoption
+ typed ActionPlan
→ deterministic ActionPlanLegalityGate
→ explicit action:authorize policy
→ one immutable ActionAuthorizationRecord
```

Still keep:

```text
external execution = 0
ActionExecutionReceipt table = 0
UI/UX = 0
models = 0
```

Seal authorization authority first.

Only then perform connector-specific execution implementation/certification.

## 21. Genuine STOP conditions

STOP future work if it requires:

```text
generic arbitrary tool/API execution
risk derived from text/regex/fuzzy/LLM
ActionAuthorization from stale P20/P21/adoption
REJECTED or DEFERRED adoption authorizing Action
plan mutation after authorization
executor reconstructing parameters
blind retry after timeout
material action without idempotency/reconciliation
reuse of DimaQueryReceipt
tenant/actor/role trusted from payload
service account self-authorization
Outcome analytics inside executor
legacy DecisionRecord / cube_query replay as Action authority
P14-P21 mutation
engine or Metabase-core changes
UI as security authority
```

## 22. Exit state

```text
HUMAN ADOPTION AUTHORITY = SEALED

ACTIONPLAN / ACTION AUTHORIZATION /
EXECUTION PRE-DEVELOPMENT REVIEW = COMPLETE

Action production code = 0
Action tables/migrations = 0
Action execution = 0
external side effects = 0
model calls = 0
UI/UX = NOT AUTHORIZED
```

Recommended next bounded objective requires new supervisor authority:

```text
provider-free ActionPlan + ActionAuthorization authority only
→ no external execution
```

STOP before implementation.
