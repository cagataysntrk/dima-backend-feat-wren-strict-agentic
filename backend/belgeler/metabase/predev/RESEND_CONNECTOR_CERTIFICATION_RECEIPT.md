# RESEND CONNECTOR CERTIFICATION RECEIPT

**Date:** 2026-09-26  
**Authority:** connector certification addendum only  
**DMP:** **NO DMP-DEC-0060**  
**Status:** **IMPLEMENTATION AUTHORIZED / PROVIDER-FREE PENDING / LIVE CANARY PENDING**

This receipt does not introduce a new durable truth owner and does not authorize Action execution.

## Frozen upstream

```text
P14-P21 = SEALED
Human Adoption = SEALED / DMP-DEC-0058
ActionPlan / ActionAuthorization = SEALED / DMP-DEC-0059
ActionAuthorization behavior SHA = afd284f6bfa55337e174ea9c8150c6ef95b2275e
ActionAuthorization certified HEAD = 43bc6947b0e884a9d35b3531c1e12217cbf3de4e
```

## Certification target

```text
provider = Resend
fixed origin = https://api.resend.com
POST = /emails
retrieve = GET /emails/:email_id
test recipient = delivered@resend.dev
idempotency retention = 24 hours
```

Provider references verified 2026-09-26:

- https://resend.com/changelog/idempotency-keys
- https://resend.com/changelog/sending-test-emails
- https://resend.com/changelog/message-id-for-sent-emails

## Permanent limits

```text
DEFAULT_ACTION_CAPABILITY_REGISTRY = EMPTY
real email risk = IRREVERSIBLE_EXTERNAL_COMMIT
DMP-DEC-0059 supported risk = REVERSIBLE_LOW_RISK only
real-recipient execution = NOT AUTHORIZED
action:execute = ABSENT
execution tables = 0
background executor = 0
models = 0
analytics = 0
engine changes = 0
legacy channels.py integration = 0
```

Provider-free certification and one bounded test-mode live canary must complete before this receipt
may be marked TEST-MODE PROTOCOL CERTIFIED.


## Provider-free certification result

```text
connector behavior SHA                = 4cd9e7cb54bc1a0cbce26591060f23037dfb6b5a
provider-free                         = 36224592531 SUCCESS
governance final                      = 36224898224 SUCCESS

Resend focused                        = 31 PASS
ActionAuthorization regression        = 38 PASS
Human Adoption regression             = 29 PASS
P21 / P20 / P19 / P18                 = 25 / 19 / 42 / 24 PASS
P17 / P16 / P15 / P14                 = 95 / 6 / 5 / 17 PASS

fixed origin                          = GREEN
trusted credential boundary           = GREEN
typed request rejects extras          = GREEN
canonical payload/fingerprint         = GREEN
deterministic idempotency key         = GREEN
24h idempotency window model          = GREEN
2xx provider id capture               = GREEN
400 invalid-key classification        = GREEN
409 payload mismatch fail-closed      = GREEN
409 concurrent same-key retry state   = GREEN
timeout/connection loss UNKNOWN       = GREEN
same-key unknown-state recovery       = GREEN
retrieve exact-id reconciliation      = GREEN
retrieve mismatch fail-closed         = GREEN
arbitrary URL                         = IMPOSSIBLE BY CONTRACT
ActionAuthorization mutation          = 0
DecisionAdoption mutation             = 0
execution DB writes                   = 0
action:execute                        = 0
models                                = 0
analytics                             = 0
engine changes/builds                 = 0 / 0
legacy channels.py diff               = 0
```

The initial connector candidate passed provider-free certification without a product RED.

A legacy M2 lab workflow was triggered only because the canary script lives under
`backend/lab/metabase/action_execution/**`. Its first transition failed at the historical
M2 forbidden-file isolation gate, not at Resend behavior. The generic CI-economy fix excludes this
connector-certification lab subtree from M2 and governance permanently asserts that exclusion.
No product or provider semantics changed.

## Live-canary architecture STOP

```text
required trigger                         = workflow_dispatch only
repository default branch               = feat/ask-v2-mvp
live workflow on default branch          = NO
live workflow on feat/dima-metabase-platform = YES
connected GitHub workflow-dispatch action = UNAVAILABLE

external POST                            = 0
logical sends                            = 0
real recipients                          = 0
```

GitHub requires a `workflow_dispatch` workflow file to exist on the repository default branch.
The Platform live workflow is intentionally isolated on `feat/dima-metabase-platform`; copying it
into `feat/ask-v2-mvp` or changing the repository default branch would cross the authorized branch
boundary. A push-triggered real Resend call is explicitly forbidden and is not used as a workaround.

Therefore:

```text
RESEND CONNECTOR PROVIDER-FREE CERTIFICATION = GREEN
RESEND TEST-MODE LIVE CANARY                  = NOT RUN / ARCHITECTURE STOP
RESEND TEST-MODE PROTOCOL CERTIFIED           = NOT YET
REAL-RECIPIENT EXECUTION                      = NOT AUTHORIZED
PRODUCTION EXECUTION PREDEV                   = NOT STARTED
DMP-DEC-0060                                  = NOT CREATED
```

No external state was made ambiguous by this STOP.
