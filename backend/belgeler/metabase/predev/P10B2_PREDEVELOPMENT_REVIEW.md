# P10B2 — PRE-DEVELOPMENT CAPABILITY CLASSIFICATION

**Milestone:** P10B2 — advanced security/data-lens capability matrix  
**Branch:** `feat/dima-metabase-platform`  
**Current audited HEAD:** `e422df46cefa9ef7207030e48fcc28cd0b78bb51`  
**P10A:** `35783766213 = SUCCESS`  
**P10B1:** `35784824929 = SUCCESS`

Status: **SEALED / CLASSIFICATION ONLY / NO ADVANCED SECURITY IMPLEMENTATION AUTHORIZED**

## 1. Purpose

P10B2 does not manufacture premium/enterprise security capabilities in the OSS lab. It classifies the
advanced security surface honestly so later profiles can distinguish:
`PROVEN`, `NOT_CONFIGURED`, `CAPABILITY_GAP`,
`REQUIRES_EXTERNAL_OWNER`, and `BLOCKING_FOR_PROFILE`.

Configured absence is not proof of a feature. If a tenant requires a capability and its owner is
unproven, the profile blocks.

## 2. Capability matrix

| Capability | Current owner | Current proof | Required governance level | OSS lab available? | Production prerequisite? | Disposition |
|---|---|---|---:|---|---|---|
| tenant identity | Dima Principal + accepted intent + P10A issuer | P10A exact tenant coherence/fail-closed mismatch | 0 | yes | yes | PROVEN |
| principal identity | Dima Principal + authenticated Metabase subject attestation | P10A + P10B1 same restricted user/session | 0 | yes | yes | PROVEN |
| basic DB query permission | Metabase permission graph/runtime | P10B1 allow execution | 0 | yes | yes | PROVEN |
| same-session revocation | Metabase permission graph/runtime | P10B1 same session changes from allow to HTTP 403 and restores | 0 | yes | yes | PROVEN |
| collection permission | Metabase collection permission owner | P9B lifecycle used isolated lab, but P10B1 did not certify tenant-user collection write/read revocation | 0 for persisted resources | yes | yes for resource persistence | CAPABILITY_GAP |
| RLS / row restriction | external real lens owner: premium Metabase sandbox or DB-native governed route | no real row-restricted P10B2 lens in current lab | 2 when tenant policy requires rows | no current proof | conditional | NOT_CONFIGURED |
| CLS / column restriction | external real lens owner | no real column-restricted P10B2 lens in current lab | 2 when tenant policy requires columns | no current proof | conditional | NOT_CONFIGURED |
| impersonation | external governed identity/routing owner | P10A can bind an attested role value but does not prove real impersonation | 2 when configured | no current proof | conditional | REQUIRES_EXTERNAL_OWNER |
| database routing | deployment/data-access control plane | P10B1 proves exact current database id only; no alternate governed route decision | 0 exact destination; 2 advanced routing | single route only | yes when multi-route profile exists | REQUIRES_EXTERNAL_OWNER |
| cache/result reauthorization | evidence/read path + substrate access owner | no cached-result cross-lens/revocation canary yet | 2 when shared/cache path used | capability exists but unproven here | yes before shared cached evidence | CAPABILITY_GAP |
| service/admin fallback prohibition | Dima P10 issuer + execution orchestration | P10A requires explicit principal; P10B1 execution uses restricted user; admin only mutates test permission graph | 0 | yes | yes | PROVEN |

## 3. Profile rule

```text
feature genuinely absent by tenant policy
→ explicit attested absence may be valid

feature required by tenant/profile
+ owner/proof absent
→ BLOCKING_FOR_PROFILE
```

Never:
```text
unknown RLS/CLS/impersonation
→ empty tuple / null
→ GREEN
```

## 4. P5 blocker

`DMP-P5-BLOCK-001` remains **OPEN** for global production official issuance.

P10A + P10B1 prove a basic authenticated subject / basic permission-revocation slice. They do not
certify advanced row/column/impersonation/database-route/cache-isolation capability globally.

A future profile-scoped production readiness policy requires a separate explicit decision and proof.

## 5. Exit of this classification milestone

P10B2 classification closes when this matrix is recorded and no fake runtime implementation is added.
P11 development may proceed independently under DMP-DEC-0026; production official receipt issuance
remains governed by the open P5 blocker.
