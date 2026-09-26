# FIRST ACTION EXECUTION / CONNECTOR — PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-26  
**Status:** **PRE-DEVELOPMENT REVIEW COMPLETE / EXECUTION NOT AUTHORIZED**  
**Consumes:** sealed DMP-DEC-0059 ActionAuthorization authority  
**Production code:** 0  
**Tables/migrations:** 0  
**External calls:** 0  
**Model calls:** Luna = 0 / Sol = 0 / C1 = 0  
**UI/UX:** NOT AUTHORIZED

## 1. Required execution boundary

~~~text
CURRENT P20 ReportDocument
+ CURRENT P21 DecisionBrief
+ CURRENT ACCEPTED DecisionAdoption
+ CURRENT ActionAuthorization
+ exact canonical ActionPlan snapshot/fingerprint
+ registered connector-specific execution capability
→ exact external side effect
→ immutable execution receipt
~~~

Permanent:

~~~text
AUTHORIZED ARTIFACT
==
EXECUTED ARTIFACT
==
RECEIPTED ARTIFACT
~~~

The executor never reconstructs or semantically rewrites the authorized payload.

## 2. Repository execution-surface inventory

The current repository was audited for real side-effect surfaces rather than inventing a fake
connector.

### 2.1 In-app notification

Current surface:

~~~text
backend/app/channels.py
@register("inapp")
→ injected notification_log DB sink
~~~

Assessment:

~~~text
external connector = NO
external side effect = NO
stable internal record identity = YES
~~~

This is internal product state, not the first external connector execution candidate requested by
this review.

### 2.2 Resend email

Current surface:

~~~text
backend/app/channels.py
_send_email(...)
→ httpx.post("https://api.resend.com/emails", ...)
→ provider response id
~~~

Existing positive properties:

~~~text
real supported external provider
server-side credential
provider returns an external id after successful send
~~~

Current blockers:

~~~text
no stable caller-supplied external idempotency key in the existing request
no repository read-after-write reconciliation path by provider id
no pre-send remote existence check
no safe retry contract after timeout / unknown remote state
no rollback / recall semantic
email delivery is externally visible and effectively irreversible after send
current dispatch path is best-effort delivery, not governed execution authority
~~~

Verdict:

~~~text
NOT SAFE AS FIRST AUTOMATED GOVERNED EXECUTION YET
~~~

### 2.3 Slack incoming webhook

Current surface:

~~~text
backend/app/channels.py
@register("slack")
→ urllib.request.urlopen(webhook, POST)
→ HTTP success/failure only
~~~

Existing positive properties:

~~~text
server-side secret
PII masking before send
bounded webhook target from settings
~~~

Current blockers:

~~~text
no returned stable message identity
no idempotency key
no read-after-write reconciliation
no duplicate-send detection at remote system
no delete/rollback reference
timeout can leave unknown remote state
incoming webhook is write-only for this implementation
~~~

Verdict:

~~~text
NOT SAFE AS FIRST AUTOMATED GOVERNED EXECUTION
~~~

### 2.4 Schedule create/delete

Current surface:

~~~text
backend/app/routers/schedules.py
backend/app/schedules.py
→ Postgres schedule_definition state
~~~

Assessment:

~~~text
real product mutation = YES
external connector = NO
external side effect = NO
soft-delete / internal read-after-write = available
~~~

It does not satisfy the requested first external connector execution review.

### 2.5 Wren / database connectors

Database/Wren connectors are analytical data-access infrastructure and are not repurposed into an
Action executor.

~~~text
ANALYTICAL CONNECTOR != SIDE-EFFECT CONNECTOR
~~~

## 3. Selected first execution candidate

~~~text
NO SAFE EXECUTION CANDIDATE YET
~~~

This is an explicit review result, not a missing decision.

The only concrete external write surfaces currently present are Resend email and Slack webhook.
Neither current implementation simultaneously provides:

~~~text
stable external idempotency
+ unknown-state reconciliation
+ read-after-write confirmation
+ safe retry semantics
+ rollback/compensation identity
~~~

Opening execution anyway would violate the exact-artifact and no-blind-retry trust model.

## 4. Closest future candidate

Resend email is the closest existing surface because the provider response already returns a
provider-side id. That alone is insufficient for execution authority.

Before it can become a candidate, a future connector-specific review must establish and implement:

~~~text
exact typed action_kind
typed input schema
server-side credential boundary
stable idempotency contract
attempt identity allocated before the external call
unknown-state reconciliation after timeout
retry only after reconciliation proves no prior success
provider acceptance success definition
confirmed pre-acceptance failure definition
explicit partial-success semantics
external receipt/reference
tenant isolation
separate execution permission
~~~

Provider capabilities are not assumed by this review. They must be verified before implementation.

## 5. Slack candidate conclusion

Slack incoming webhook is farther from readiness because the current implementation has no stable
remote message identity and no read-after-write/reconciliation path.

Do not select it as the first governed executor unless the integration changes from write-only
webhook semantics to a connector contract with stable remote identity and reconciliation.

## 6. Future executor credential boundary

Credentials may come only from trusted server-side configuration or a dedicated secret owner.

Forbidden:

~~~text
credential in ActionPlan payload
credential in DecisionBrief
credential in DecisionAdoption
credential supplied by model/user text
webhook URL supplied as arbitrary target_resource
~~~

## 7. Attempt identity and idempotency

Before any external request, future execution must durably bind:

~~~text
attempt_id
idempotency_key
authorization_id
plan_fingerprint
target identity
~~~

A timeout becomes:

~~~text
UNKNOWN_EXTERNAL_STATE
~~~

not FAILED. No retry occurs until connector-specific reconciliation resolves the state.

## 8. Authorization-to-payload binding

The future executor consumes the exact canonical plan snapshot stored with
ActionAuthorizationRecord.

It must prove:

~~~text
stored plan fingerprint
==
recomputed canonical snapshot fingerprint
==
authorization plan fingerprint
~~~

A connector-specific deterministic compiler may map that typed snapshot to one exact provider
request. No LLM, fuzzy matching or free-text interpretation participates after authorization.

## 9. Execution receipt boundary

A future execution receipt is separate from analytical DimaQueryReceipt and must bind:

~~~text
execution_receipt_id
authorization id/fingerprint
plan_fingerprint
attempt_id
idempotency_key
executor identity
connector/capability version
target identity
exact provider-request fingerprint
started_at / completed_at
external_reference
status
failure / unknown-state detail
~~~

## 10. Success, failure and partial success

~~~text
HTTP 2xx alone != business outcome
timeout != confirmed failure
provider acceptance != downstream business outcome
partial provider acceptance != full success
unknown external state != retry permission
~~~

## 11. Rollback and compensation

If a connector cannot truly roll back an external side effect, compensation is a new governed
action:

~~~text
new ActionPlan
→ new ActionAuthorization
→ new execution
→ new receipt
~~~

For current email/Slack surfaces, no true rollback is assumed.

## 12. Automation decision

~~~text
AUTOMATED EXTERNAL EXECUTION = NOT SAFE / NOT AUTHORIZED
~~~

No scheduled/background executor should consume ActionAuthorization records yet.

## 13. Execution STOP conditions

STOP future execution implementation if any remain unresolved:

~~~text
no stable remote identity
no idempotency semantics
no unknown-state reconciliation
blind retry after timeout
arbitrary URL/tool/API target
payload reconstructed after authorization
connector capability not versioned
credential supplied in action payload
stale P20/P21/adoption/authorization
missing exact authorization-to-payload binding
execution receipt reuses analytical receipt
Outcome analytics embedded in executor
~~~

## 14. Next bounded objective

No executor is opened by this review.

Recommended next supervisor decision:

~~~text
either

A) authorize connector-specific hardening / proof for ONE real provider
   (Resend is the nearest existing surface, but not yet safe)

or

B) introduce a new real low-risk connector only after its API provides
   stable identity + idempotency + reconciliation
~~~

Only after that proof should a separate directive authorize one connector-specific
ActionExecutionAttempt / Receipt vertical.

## 15. Exit state

~~~text
ACTIONPLAN / ACTIONAUTHORIZATION AUTHORITY = SEALED

FIRST ACTION EXECUTION / CONNECTOR
PRE-DEVELOPMENT REVIEW = COMPLETE

selected candidate = NO SAFE EXECUTION CANDIDATE YET

Action execution production code = 0
execution tables/migrations = 0
external calls = 0
model calls = 0
UI/UX = NOT AUTHORIZED
~~~

STOP before execution implementation.
