# Dima Brain V2.1 Permanent Forward Runtime Laws

Status: permanent architecture guardrail. These laws do not override newer RED
evidence; executable CI is the enforcement authority.

1. One Product has one forward orchestrator: `BrainV2Service / LangGraph`.
   `HeadlessProductComposer` is legacy fallback/reference only and is forbidden
   from final certification.
2. User Requirement, Scope, Material Need, Evidence, Epistemic Outcome and
   Presentation are distinct authorities. In particular: requirement != query,
   goal != material plan, ordering != ranking, association != business policy !=
   causality, process completion != requirement fulfillment, report != analytics.
3. Requirement owner routing is typed and deterministic. Direct/ranking consumes
   Evidence; relationship terminates through P18; RCA terminates through P19;
   report/presentation terminates through P20 after analytical completion.
4. MaterialGroup is an execution projection only. Compatible requirements may
   share one exact typed material package. Evidence has explicit consumers and
   never silently fulfills every requirement.
5. Scope mutations use the canonical typed reducer. Omitted facets inherit;
   explicit clear is explicit. Presentation-only continuation cannot mutate
   Research/Scope or open native analytics.
6. Normal discovery is Metabot -> VERIFIED Evidence -> deterministic
   CandidateSetProjector -> P19. P17 is only an information-gain re-entry
   controller after a typed P19 NextTest request (plus bounded audit surfaces).
7. P20 consumes terminal governed outcomes. It does not reopen analytics or
   decide whether upstream requirements were fulfilled.
8. Semantic truth is independent from physical SQL/MBQL shape. Native
   observations satisfy required-subset/allowed-superset contracts and hard-fail
   tenant/entity/metric/time drift.
9. Evidence is bound to tenant, principal, ScopeVersion, material fingerprint,
   receipt and result hash. Scope change makes prior Evidence historical.
10. Same semantic activity and revisions/fingerprint are idempotent. Resume must
    not repeat completed provider/native work.
11. Final V2.1 live runs use `MB_AGENT_API_ENABLED=false`; Agent API request
    count must be zero.
12. Production Brain V2 contains no benchmark/case-specific semantic branching.

Executable mapping:
- `test_v3_brain_v2_runtime_guardrails.py`: one runtime, legacy ban, Agent API,
  benchmark/case-id ban, and no normal-discovery P17 graph route.
- material/requirement stateful tests: material sharing, report material +0,
  ordering/metamorphic invariance.
- graph/owner integration: P17 discovery ban, completion-before-P20,
  resume/idempotency and current Evidence.
- `test_v3_p18_relationship_result.py`: immutable tenant-scoped P18 terminal
  artifact; Completion/P20 consume its ref rather than owner internals.
- security tests: tenant/principal isolation.
- live receipt gates: duplicate native, Agent API, legacy calls, causal overclaim.

Every new RED follows: first wrong boundary -> exact PF reproducer -> generic
invariant -> metamorphic sibling -> owner-level root fix -> affected regressions
-> full PF -> frozen candidate -> one fresh surgical live. Same-SHA retry,
fuzzy/regex/prompt hacks, benchmark phrase patches and ceiling increases are
forbidden as fixes.
