# P11 — PRE-DEVELOPMENT REVIEW

**Milestone:** P11 — Entity values / filter resolution  
**Normative decision:** DMP-DEC-0026  
**P10B2 prerequisite:** capability classification only; global P5 production blocker remains separate.

Status: **SEALED / NECESSITY EVALUATION AUTHORIZED / DETERMINISTIC ENTITY RESOLVER NOT AUTHORIZED**

## 1. Question

Before building a Dima entity-value resolver, prove the material failure that requires one.

Default candidate architecture:

```text
LLM cognition
→ current-principal Metabase value/index retrieval
→ candidate evidence
→ LLM choose/clarify
→ minimum Dima truth/security gate
```

## 2. Model policy

```text
Luna = default / economic baseline
Sol  = ceiling / headroom measurement
```

The exact same frozen corpus, tools, prompt contract, semantic config, database snapshot, access lens
and truth oracle are used. No Sol-specific examples or Luna-specific patches.

## 3. No implementation authorization yet

This review does not authorize:
- fuzzy/stemming/morphology authority;
- synonym tables derived from test cases;
- an EntityResolver framework;
- automatic value adoption from names;
- cross-user candidate reuse;
- hidden admin fallback.

Only corpus/tool-contract/evaluation harness work is authorized until the necessity result is known.

## 4. Interpretation

- Luna PASS + Sol PASS -> reuse native/retrieval path; no deterministic resolver.
- Luna FAIL + Sol PASS -> MODEL_COGNITION_GAP; consider bounded context/tool description or certified
  Sol escalation before permanent code.
- Luna FAIL + Sol FAIL on material truth/security -> identify generic root cause and add minimum
  guardrail only.
- any permission-hidden value exposure -> deterministic security failure regardless of model.

## 5. First frozen corpus

See:
`backend/belgeler/metabase/tickets/P11_ENTITY_VALUE_NECESSITY_GATE.md`.

No provider/live model evaluation has been run by this predev seal.
