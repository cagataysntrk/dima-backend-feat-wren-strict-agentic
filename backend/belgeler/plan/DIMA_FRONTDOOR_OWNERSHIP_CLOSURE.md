# DIMA — FRONTDOOR_OWNERSHIP_CLOSURE

**Status:** OPEN  
**Owner timing:** Day10 Product MVP integration  
**Release blocker:** YES  
**Production /ask-v2:** OFF

## Current fact

```text
/api/ask-v2
→ V2Orchestrator
→ TurnInterpreter
→ SemanticResolver
→ legacy Day4 AnalyticsIR/CubePlanner route
```

This path still imports/executes historical heuristic semantic code
(regex/fuzzy/morphology machinery in legacy resolver/interpreter).

The new Day6.5 `StandardLaneEngine` is not yet the HTTP front-door owner.

## Target before FINAL FREEZE

```text
/api/ask-v2
→ STANDARD | RESEARCH dispatcher

STANDARD → StandardLaneEngine
RESEARCH → governed ResearchManager path
```

Required:
```text
authoritative request path imports/executes legacy SemanticResolver = 0
request-level fallback to legacy Day4 authority path                = 0
```

Old code may remain migration/history-only if non-authoritative.

Do not perform this migration prematurely during current SI structural closure.

A future architecture test must prevent silent reintroduction of legacy fuzzy/regex authority.
