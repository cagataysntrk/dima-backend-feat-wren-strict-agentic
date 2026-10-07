# Dima Brain V2.1 Permanent Forward Runtime Laws

Status: permanent architecture guardrail. These laws do not override newer RED
evidence; executable CI is the enforcement authority.

0. **Semantic Authority Law:** every business-semantic fact has exactly one
   canonical owner. A downstream component may project, transport, structurally
   observe, verify fulfillment, or consume that fact; it may not reinterpret the
   same fact and become a second veto authority.
0a. The canonical analytical authority chain is
   `ResearchBrief/ResearchScope -> AnalyticalIntentV1 -> ExecutionManifest ->
   verify_analytical_fulfillment_v1 -> Evidence`.
   `AnalyticalRequestContract` is a deterministic projection/transport form,
   not an independent business-semantic owner.
0b. `verify_analytical_fulfillment_v1` is the only runtime
   Intent <-> Execution semantic judge. Native attestation/observation is
   structural provenance only.
0c. Closed V1 grammar is conformance/test authority only. It must not become a
   production runtime capability veto over a legal typed intent.
0d. New-turn P18 graph refs are one atomic turn-owned projection bundle:
   requirement/result/claim/policy-use refs clear together. Durable historical
   P18 artifacts are not deleted by that projection reset.

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
4. MaterialGroup is an execution projection only. Acquisition identity is not
   requirement-fulfillment identity. Compatible comparison/ranking/top-k
   consumers may share one governed acquisition; the resulting manifest must
   pass each consumer's independent fulfillment verifier before shared Evidence
   admission. Result-dependent children remain later occurrences.
5. Scope mutations use the canonical typed reducer. Omitted facets inherit;
   explicit clear is explicit. Presentation-only continuation cannot mutate
   Research/Scope or open native analytics.
6. Normal discovery is Metabot -> VERIFIED Evidence -> deterministic
   CandidateSetProjector -> P19. P17 is only an information-gain re-entry
   controller after a typed P19 NextTest request (plus bounded audit surfaces).
6a. Normal observational relationship is VERIFIED Evidence -> bounded P18
    interpretation -> immutable RelationshipResult. P17 provider calls are zero.
    P18 may classify only the exact existing Evidence identity set and cannot
    execute analytics, mutate scope, invent semantic identities, promote
    causality, or require BUSINESS_POLICY for OBSERVATIONAL intent.
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
  benchmark/case-id ban, no normal-discovery P17 graph route, no normal
  observational-relationship P17 owner route, closed-grammar runtime-veto ban,
  one fulfillment-verifier runtime owner, MaterialGroup non-judge law, and
  P18/P19/P20 native-analytics ban.
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
