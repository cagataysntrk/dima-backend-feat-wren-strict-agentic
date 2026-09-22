# DIMA DAY 6.5 — M0E-DEEP-DELTA CONTRACT

**Status:** ACTIVE SOURCE / CLASSIFICATION GATE  
**Date:** 2026-09-22  
**M0E-v1:** PRESERVED VALID BASELINE  
**Final exhaustion:** REOPENED  
**Implementation mandate:** NONE BY DEFAULT  
**Source copy / port / vendor / transliteration:** FORBIDDEN  
**Production Metabase dependency:** OFF

## 1. Purpose

M0E-v1 successfully classified a large set of Metabase capabilities, but deeper upstream audit
found additional Dima-relevant mechanisms absent from the v1 map.

This delta does NOT invalidate v1 rows.
It only supersedes the claim that final exhaustion had already been reached.

Exit remains capability-level, not "read every file".

## 2. Required delta mechanisms

Classify at least:

1. effective data-access lens fingerprint
2. derived Evidence/Report/result viewer reauthorization
3. permission-sensitive cache keying
4. retrieval index → current-principal hydration
5. retrieval UNAVAILABLE != semantic NO_MATCH
6. indexed high-cardinality entity candidate → live current-user re-read
7. AI-context source-of-truth → derived index lifecycle
8. agent accumulated state vs per-turn state delta
9. non-serializable security-bound query → persistence forbidden
10. REST serialized query/continuation vs MCP server-side query_handle
11. client-declared capability != authorization
12. Dima-owned Agent API telemetry/provenance
13. async exploration idempotency/cancel/race
14. missing creator/principal → fail closed
15. cardinality-bounded Research fanout
16. interestingness = non-authoritative prioritization only
17. content verification / official-content metadata
18. glossary lifecycle vs Wren knowledge
19. Wren→Metabase semantic bridge
20. Agent API global AI-feature dependency
21. raw SQL kill-switch operational dependency
22. Metabase lib_metric multi-source semantics
23. OSI/Ossie interoperability watchlist
24. implicit-FK join repair
25. representation-repair idempotency

## 3. Mandatory row fields

Every mechanism records:

```text
mechanism
exact upstream source
observed behavior
problem solved
Dima owner/equivalent
Wren owner/equivalent
disposition
timing
security/authority impact
required behavioral proof
runtime dependency
```

Allowed dispositions:
`DIMA_CORE_NATIVE | WREN_OWNS | METABASE_RUNTIME_CANDIDATE | PATTERN_ONLY |
DEFER_PRODUCT | NOT_APPLICABLE | REJECT`.

## 4. Permanent patterns to preserve

### ExecutionAccessFingerprint

Pattern owner: Dima trust plane, Day12–14.

Design fields:
```text
tenant_binding
principal_subject
role_set_digest
attribute_policy_digest
policy_version
RLS/CLS rule-version digests
database_route / destination / impersonation role
semantic_context_version
source_object_refs
security_parameter_digest
```

No raw PII/sensitive attributes in persisted fingerprint.

### Security-bound persistence refusal

```text
runtime-only security binding
cannot be faithfully serialized
→ replay persistence FORBIDDEN
```

### Retrieval

```text
index → candidate IDs
→ current tenant hydration
→ current principal/access check
→ current context/catalog membership
→ CandidateSet
→ SemanticBindingGate
```

`INDEX HIT != CURRENT AUTHORITY`.

`INDEX UNAVAILABLE != NO MATCH != SEMANTIC GAP`.

Sensitive/live high-cardinality value requires current-principal authoritative re-read.

### Research

```text
metadata cardinality → deterministic fanout budget
high cardinality     → bounded Top-K + Other
interestingness      → priority hint only
async tasks          → idempotent + cancel-safe + race-safe
missing principal    → fail closed
```

## 5. New X0/full-X P0 — implicit FK join authority

Metabase representation repair may infer joins from physical FK metadata.

Dima invariant:

```text
UNAPPROVED_METABASE_IMPLICIT_JOIN = 0
```

No inferred physical FK join may execute unless compatible with retained Wren-approved semantic
relationship/cube truth.

Use upstream behavior as oracle; do not copy implementation.

## 6. Source protocol

For each important Metabase conclusion:
- pin source SHA;
- identify exact file/function/behavior;
- distinguish source-observed behavior from Dima design choice;
- never infer production viability from source alone;
- no source copy/port/vendor.

Current baseline pin remains `74216b30981d8310c4cf724d63ca282e2e63529d` until explicitly repinned.

## 7. Exit gate

```text
v1 rows lost                                           = 0
required delta mechanisms unclassified                 = 0
security/authority mechanisms without owner            = 0
runtime candidates without behavioral proof question   = 0
WREN_OWNS duplicated as Metabase semantic truth        = 0
implicit-FK authority unanswered                       = 0
bridge mechanism without explicit preflight question   = 0
```

Only then:
`M0E-DEEP-DELTA FINAL GREEN`.

M0E-DEEP-DELTA completion authorizes bridge preflight, not Metabase runtime X0.
