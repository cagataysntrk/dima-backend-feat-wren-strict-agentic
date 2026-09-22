# FT-005 — MODEL DEPENDENCY MATRIX RECEIPT

Status: BLOCKED_NO_CREDENTIAL
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`

## Purpose

Classify FT-005 model dependence on one frozen follow-up corpus while holding constant:

- questions;
- accepted context;
- schemas;
- system prompt;
- typed output contract;
- authority rules;
- temporal rules;
- retrieval oracle;
- evidence policy.

Only the model/provider role is allowed to vary.

## Model roles

### THIRD_MODEL_DIAGNOSTIC

Provider:
`openrouter`

Exact model:
`google/gemini-2.5-flash-lite`

Latest frozen diagnostic run:
`35789186261`

Result:
`RED`

Artifact:
`sha256:cd68d419c8262a123e9a99166afa8b2160bfee5102bba264974f2505473059d3`

Observed failure families remain:
- SYSTEMATIC_SCHEMA_CONTRACT_MISMATCH;
- EXECUTABLE_REASON_SCHEMA_MISMATCH;
- UNSUPPORTED_OPERATION_REINTERPRETATION candidate;
- RETRIEVAL_CONTRACT_DRIFT;
- exact inherited-slot labeling is diagnostic only.

### LUNA_BASELINE

Provider:
`openai`

Exact model:
`gpt-5.6-luna`

Role:
`LUNA_BASELINE / ECONOMIC DEFAULT CANDIDATE`

Measurement:
`MODEL_COMPARABLE`

Configured reasoning:
`disabled`

Workflow:
`35789207838`

Execution:
`NOT RUN`

Status:
`BLOCKED_NO_CREDENTIAL`

Artifact:
`sha256:0ebe4d78b8671f9886d4ce189ee3e3c9fbbc3fe17db0c86369e621c81f1a9321`

### SOL_CEILING

Provider:
`openai`

Exact model:
`gpt-5.6-sol`

Role:
`SOL_CEILING / CAPABILITY REFERENCE`

Measurement:
`MODEL_COMPARABLE`

Configured reasoning:
`disabled`

Workflow:
`35789207838`

Execution:
`NOT RUN`

Status:
`BLOCKED_NO_CREDENTIAL`

Artifact:
`sha256:3a5aa74c90a47b959c80822ca4a5bce0145b04d8453d23a849665d81fbecd578`

## Credential evidence

The workflow environment observed:

```text
DIMA_OPENAI_API_KEY =
```

empty for both matrix jobs.

The corpus execution step was therefore intentionally skipped and a blocker receipt was emitted.

Required canonical secret:
`DIMA_OPENAI_API_KEY`

Workflow also accepts:
`OPENAI_API_KEY`

No API key is written to repository content.

## Interpretation

No Luna/Sol quality comparison can currently be made.

Forbidden conclusions:
- Luna GREEN;
- Luna RED;
- Sol GREEN;
- Sol RED;
- model capability dependency;
- architecture ceiling reached;
- Gemini-specific weakness proven.

Those require actual model execution.

## Current authorized conclusion

```text
PROVIDER_FREE_FT005_CORE = GREEN

GEMINI_THIRD_MODEL_DIAGNOSTIC = RED

LUNA_BASELINE = BLOCKED_NO_CREDENTIAL

SOL_CEILING = BLOCKED_NO_CREDENTIAL

FT005_FINAL = OPEN
```

## Product patch authorization

`NOT AUTHORIZED YET`

Do not patch:
- production follow-up prompt;
- conversation schema;
- deterministic slot inheritance;
- retrieval dictionary;
- special topic classifier;
- analytical algorithm.

Reason:
the required model differential is not yet measured.

## Unblock action

Configure one GitHub Actions secret:

`DIMA_OPENAI_API_KEY`

Then rerun:

`dima-fast-ft005-openai-matrix`

After real matrix execution:
1. classify every frozen case;
2. produce model-dependency findings;
3. authorize only the smallest evidence-backed contract fix, if any;
4. rerun Luna focused corpus;
5. run Luna real-Metabase Q1→Q2→Q3 E2E;
6. run Sol ceiling confirmation;
7. regress FT-003/FT-004;
8. decide FT-005 seal honestly.


## Fail-closed workflow confirmation

Corrective workflow SHA:
`f677493c2722cc2117e1795cd0aa94e283cc81d4`

Canonical rerun:
`35789534149`

Both matrix jobs:
- emitted the explicit BLOCKED_NO_CREDENTIAL receipt;
- skipped the model corpus;
- then failed the job intentionally.

This prevents GitHub Actions green status from being confused with model-quality GREEN.

No product code changed.
