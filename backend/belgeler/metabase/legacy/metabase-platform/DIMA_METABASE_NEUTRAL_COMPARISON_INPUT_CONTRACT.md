# DIMA METABASE — Neutral Comparison Input Contract

Status: FROZEN FOR PLATFORM COMPARISON CANDIDATE
Contract owner: Dima Metabase Platform
Scope: neutral external comparison handoff only; this document does not score or evaluate Wren.

## 1. Canonical product contract

The comparison-facing product contract is the existing headless Python contract:

- `backend/app/v3/product/contracts.py`
- `backend/app/v3/product/service.py`
- `PRODUCT_CONTRACT_VERSION = core-b-product-v1`

No HTTP/UI surface is added for comparison. `HeadlessProductService` remains projection/orchestration over sealed owners.

Canonical entry points:

- `research_question(...)`
- `company_context(...)`
- `resume(...)`
- `page(...)`
- `timeline(...)`
- `trace(...)`
- `closed_loop(...)`

Owner-native create/transition methods remain owned by their sealed stores; the comparison harness must not bypass owner authorization.

## 2. Inputs

Every comparison invocation must provide an authenticated `Principal` with explicit tenant binding.

Supported headless inputs are:

1. Company context inputs: analytical-context availability, entity refs, optional sector-pack refs.
2. Ask/Research inputs: raw user question plus a governed `ResearchIntakeCatalog`; prior brief only when explicitly exercising follow-up.
3. Artifact navigation inputs: typed `ArtifactRef` values and optional durable scope IDs required by the artifact contract.
4. Closed-loop projection inputs: a set of existing governed artifact refs for the same authorized tenant.

The harness must not inject hidden authority IDs, expected answers, case-specific routing hints, prompt patches, or benchmark-only semantic metadata.

## 3. Outputs

Canonical outputs are immutable product DTOs from `contracts.py`, including:

`CompanyContext`, `CapabilityDiscovery`, `ResearchDTO`, `WatchDTO`, `SignalDTO`,
`InvestigationDTO`, `EvidenceDTO`, `EpistemicAssessmentDTO`, `ReportDTO`,
`DecisionDTO`, `AdoptionDTO`, `ActionWorkDTO`, `OutcomeDTO`, `MemoryDTO`,
`ArtifactPage`, `ArtifactTimeline`, `OperationTrace`, and `ClosedLoopProjection`.

Failure output uses the stable `ProductErrorCode` taxonomy. A governed limitation or inconclusive result is a legal result and must not be rewritten as success.

## 4. Environment

Canonical platform runtime for this candidate:

- Python: 3.12
- analytical engine: Metabase / Metabot
- engine SHA: `cbe313af9ac2d5960f662068e433d328d896fb06`
- engine release: `0.63.18-dima.6`
- immutable image digest: `sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353`
- cognition model: `openai/gpt-5.6-luna`
- no Sol
- no C1
- no model cascade
- default external Action capability registry: empty
- `action:execute`: absent

Provider-free comparison preparation uses:

`DIMA_VQR_EMBEDDER=off`
`DIMA_SCHEDULER_ENABLED=false`
`DIMA_INTERACTION_LOG=false`

A live neutral comparison may supply the same provider credentials required by the already-certified runtime, but may not change model topology.

## 5. Tenant and security setup

The comparison harness must create or use an explicit tenant and authenticated principal. Cross-tenant reads must remain non-oracle: a foreign artifact and a missing artifact must not disclose distinguishable existence information.

Current principal authorization is re-evaluated on resume. Restart/resume must use durable identities and must not reinterpret the original raw prompt as authority.

## 6. Fixture expectations

Neutral comparison fixtures must:

- be identical for every candidate under the external comparison authority;
- contain no encoded expected answer or case-specific routing hint;
- expose only data required by the declared test case;
- preserve the same tenant/security assumptions;
- keep specialized-engine cases distinguishable from shared-engine cases.

The Platform does not define the neutral comparison corpus or winner formula.

## 7. Measurement hooks

The harness may measure and record:

- wall-clock latency;
- provider/model calls;
- Metabase analytical calls;
- terminal state;
- product error/failure class;
- artifact IDs and lineage;
- currentness;
- `OperationTrace.owner_calls`;
- `OperationTrace.artifact_ids`;
- `OperationTrace.terminal_state`;
- exceptions;
- token/model usage when exposed by the provider trace.

Existing Core-B live receipts are valid historical platform evidence. This contract authorizes no new paid campaign by itself.

## 8. UX foundation status contract

The Wave-1 catalog is `backend/product_contracts/ux_foundations.json`, version
`wave-1-comparison-ready-v2`. Every one of the 50 descriptors has exactly one status from:

- `HEADLESS_READY`
- `FOUNDATION_ONLY`
- `DATA_DEPENDENT`
- `SPECIAL_ENGINE_DEFERRED`
- `PRODUCTIZATION_DEFERRED`

These are readiness facts, not comparison scores.

## 9. Explicit exclusions

This contract does not authorize UI, frontend routes, Metabase embedding UI, external action execution,
Resend live, Wren import/merge/tuning, DEV80, Validation50, Hidden50, or a winner decision.
