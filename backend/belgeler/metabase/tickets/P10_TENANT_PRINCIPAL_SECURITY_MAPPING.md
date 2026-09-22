# P10-001 — Production ExecutionAccessSnapshot issuer and tenant/security mapping

**Milestone:** P10  
**Review:** `backend/belgeler/metabase/predev/P10_PREDEVELOPMENT_REVIEW.md`  
**Status:** P10A PROVIDER-FREE CONTRACT AUTHORIZED / LIVE SECURITY PROOF NOT AUTHORIZED YET

## Goal

Build the fail-closed production issuance boundary for the existing P5
`ExecutionAccessSnapshot`.

No second durable access fingerprint or snapshot model.

## P10A

Pure/provider-free:
- bind current Dima Principal to accepted ResolvedAnalyticsIntent principal;
- bind canonical projection semantic/source identity;
- accept only explicitly verified policy/RLS/CLS/database/security facts;
- require an explicit attested Metabase authenticated subject;
- produce the existing P5 snapshot;
- hard-fail every identity/lens mismatch.

## P10B

After P10A GREEN:
- tenant A/B topology;
- A1/A2/admin/restricted/row-restricted;
- real permission/lens mapping;
- revocation reread denial;
- cache isolation;
- no service/admin fallback;
- faithful serialization requirement.

## Blocking rule

DMP-P5-BLOCK-001 remains OPEN until P10B. Production official receipts and production P9B resource
writes remain blocked.


## P10A result

`1abf43657453a771954a939de834e6b48f55620e` is provider-free GREEN:
20 focused PASS, 59 inherited P5/P9B PASS, M1/Wren GREEN.

## P10B split

DMP-DEC-0025:
- P10B1 = one OSS authenticated-subject + basic permission revocation canary;
- P10B2 = advanced row/column/impersonation/database-route security lens.

Current OSS lab cannot certify P10B2. DMP-P5-BLOCK-001 remains open.


## P10B1 live result

`e422df46cefa9ef7207030e48fcc28cd0b78bb51` / workflow `35784824929`:
same authenticated restricted session executes before revocation, receives permission denial after
the exact permission-graph change, and executes again after restore. Admin is used only to mutate the
isolated test permission graph; tenant-bound analytical execution never falls back to admin.

P10B2 is classification-only. See
`backend/belgeler/metabase/predev/P10B2_PREDEVELOPMENT_REVIEW.md`.
