# DIMA DAY 6.5 — D65-SI STANDARD INTEGRATION CLOSURE

**Status:** AUTHORIZED PLAN / BLOCKED UNTIL J1 DECISION  
**Order:** J1 decision → D65-SI → real Standard vertical sentinel → X0  
**Product code before J1 decision:** NO-TOUCH

## Purpose

Close the last integration gap between the already-built Standard components and the actual pure
Standard hot path before comparing execution substrates.

Required chain:

```text
Standard cognition/profile
→ BoundedAgentRuntimeKernel
→ governed semantic + temporal binding
→ bounded repair when needed
→ StandardProjection
→ CoverageVeto
→ AcceptedStandardAuthority
→ AcceptedAuthorityRegistry
→ official execution
→ QueryContract
→ Evidence
```

This is not a new architecture-selection day. It is integration closure of the accepted
Standard architecture.

## Hard invariants

For a pure Standard accepted turn:

```text
ResearchManagerLoop dependency              = 0
UserObligationLedger requirement            = 0
AcceptedTurnContract as Standard authority  = 0
```

Authority is an XOR:

```text
AcceptedStandardAuthority
xor
AcceptedResearchAuthority
```

The registry must prove exactly-one commit at runtime.

Rejected Standard semantic authority never transfers into Research. If Standard cannot be sealed
and transition to Research is required, Research cognition starts again from the original user
message / permitted non-authoritative context. Rejected Standard semantic choices are not merged.

## J1 dependency

Do not wire D65-SI before J1 chooses the semantic/temporal decision topology.

If J1 rejects Jev and current topology remains:
- proceed directly to D65-SI without another micro-consult.

If J1 is promising and product topology may change:
- STOP;
- consult on D65-J1B/topology;
- perform D65-SI once against the final approved topology.

## Real Standard sentinel

At least one real governed vertical must prove:

```text
Standard request
→ AcceptedStandardAuthority
→ StandardProjection
→ Wren
→ actual result
→ QueryContract
→ Evidence
```

No surrogate Research `AcceptedTurnContract` is accepted as proof.

## Testing discipline

Normal loop:
- focused provider-free;
- workers=1 focused real-LLM where required;
- failure-family classification;
- metamorphic/family proof;
- real Wren Standard sentinel.

No DEV80 / Validation50 / Hidden50 here.

## Exit

D65-SI closes only when:
- pure Standard contains no ResearchManagerLoop/UOL dependency;
- AcceptedStandardAuthority is the committed Standard authority;
- registry XOR is proven;
- Standard→Research rejected-authority carry-over is zero;
- real Wren Standard vertical yields QueryContract + Evidence;
- production `/ask-v2` remains OFF.

Only then may D65-X0 execute.
