# Dima Brain V2 Phase-1 Provider-Free Candidate

This receipt exists only to freeze and certify the current Brain V2 implementation
against the deterministic Phase-1 provider-free closure.

Candidate parent:

`9e95ba4870a99facafb0fc692c7fbbdb7ff51036`

Scope:

- Brain V2 architecture invariants
- reference-only LangGraph state
- Postgres checkpoint/resume
- ONE_PASS / ADAPTIVE / DISCOVERY owner paths
- scope repair and currentness
- cognition/native dedup
- P14/P17/P19/P20 authority regressions
- legacy-v2 semantic shadow replay
- tenant/principal security
- repository hygiene

Engine remains frozen at:

`0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c / 0.63.18-dima.8`

This receipt authorizes no paid/live or 30-case execution.

## Closure retry receipt

P17 compatibility classification from run `36746951507`:
the new direct-P19 exact-obligation projection was incorrectly made mandatory
for historical P17 typed re-entry callers. The implementation now applies that
projection only when an exact downstream obligation is supplied; existing P17
terminal/action-profile legality remains unchanged otherwise.

Candidate parent for this closure retry:

`1c819861f14d8a6f90427c14df88c6264879e498`
