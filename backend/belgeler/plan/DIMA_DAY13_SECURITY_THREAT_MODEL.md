# DIMA DAY13 — TENANT / PRINCIPAL / PII SECURITY THREAT MODEL

## Authority map

Day13 adds no security truth engine.

```text
authentication / permission       control_plane Principal + authorize
tenant execution identity         TenantAnalyticsRuntimeV0 + tenant_binding
semantic authority                SemanticBindingGate
QueryContract                     ContractStore
Evidence                          EvidenceStore
report continuation integrity     ReportSectionContinuationSigner
continuation admission            ReportContextRegistry
PII masking                       app.pii
Product events                    diagnostic only
```

## Protected boundaries

Every V2 execution/replay path must preserve:

```text
tenant
principal
session
thread
context version
accepted authority
Evidence lineage
Finding lineage
ResearchTask identity
directive parent
signed section identity
semantic authority
```

Cross-boundary references fail closed at their existing owner. No lookup-by-label,
fallback-by-similarity, or foreign-tenant recovery is permitted.

## Provider exposure policy

Providers receive minimum bounded cognition context only.

Forbidden accidental egress:

```text
raw SQL
raw QueryContract persistence row
unbounded DB rows
JWT/HMAC secrets
foreign-tenant data
raw signed-token key material
raw PII from analytical result rows
raw PII from narration presentation packet
```

Current explicit egress protections:

- Research result disclosure is bounded and string PII-masked through `app.pii`.
- Numeric/bool analytical values remain unchanged by PII masking.
- Narration receives a presentation-safe Report projection whose human text is PII-masked.
- Signed continuation token contains locator + integrity fields only; no semantic handle,
  Evidence payload, formula, SQL, or canonical analytical payload.
- ProductEvent is diagnostic and carries IDs/refs, never raw provider/tool payloads.
- QueryContract audit receipt is secret-minimized; SQL remains in the canonical ContractStore,
  not in provider cognition receipts.

## Threat matrix

```text
same tenant / wrong principal              DENY
wrong tenant / same-looking principal      DENY
wrong session                              DENY
wrong thread                               DENY
wrong context version                      DENY
tampered signed token                      DENY
stale/missing continuation context         REBIND / DENY
foreign Evidence                           DENY
foreign ResearchTask                       DENY
stale/invented ActionInstance              DENY
foreign Finding / hypothesis Evidence      DENY
principal substitution at Research runner  DENY
missing principal                          DENY
```

## PII principle

PII masking is an egress/privacy function only. It never becomes semantic truth and
never changes canonical Evidence, QueryContract, ReportDocument, or database truth.
Canonical objects remain immutable; provider-facing projections are sanitized copies.

## Stop-the-line

Day13 is RED if any test demonstrates cross-boundary admission, provider exposure of
raw governed rows/SQL/secrets, or a PII fix that mutates analytical authority.
