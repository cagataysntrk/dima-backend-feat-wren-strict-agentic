"""Pure Standard profile / lane integration for Day 6.5 D65-SI.

This module owns the Standard-domain finite cognition path only:

raw user message
→ exact-source bounded draft
→ governed semantic/temporal binding
→ CandidateObligation
→ StandardBuilder
→ StandardProjection
→ narrow CoverageVeto
→ AcceptedStandardAuthority
→ AcceptedAuthorityRegistry
→ Standard execution adapter

It deliberately does NOT import or create AcceptedTurnContract, UserObligationLedger,
ResearchManagerLoop, ManagerRuntime, raw SQL, or direct database authority.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable, Literal

from pydantic import Field, model_validator

from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    RepresentabilityDecision,
    SemanticBindingRef,
    StandardProjection,
)
from app.v2.manager_policy import ManagerCapabilityLane, ManagerCapabilityRegistry
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import BoundedSemanticContextV0, ConversationStateV2, FrozenModel
from app.v2.representability import RepresentabilityGate
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import SemanticCandidateDecisionProvider
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import (
    AcceptedAuthorityRegistry,
    AcceptedStandardAuthority,
    StandardAuthoritySealer,
)
from app.v2.standard_builder import (
    StandardBuilderSession,
    StandardBuilderState,
    StandardWorkMode,
)
from app.v2.standard_coverage import (
    StandardCoverageAudit,
    StandardCoverageIssueKind,
    StandardCoverageVeto,
)
from app.v2.standard_execution import (
    StandardExecutionResult,
    WrenStandardExecutionAdapter,
)
from app.v2.standard_projection import StandardProjectionCompiler
from app.v2.temporal_intent import TemporalNormalizationProvider


class StandardLaneStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"
    COGNITION_REJECTED = "COGNITION_REJECTED"
    FAILED = "FAILED"


class StandardDraftSemanticSurface(FrozenModel):
    surface: str = Field(min_length=1)
    kind_hint: Literal[
        "metric", "dimension", "filter", "time", "comparison", "unknown"
    ] = Field(
        description=(
            "filter means an explicit concrete governed category/entity value used to "
            "restrict rows. A descriptive qualifier or implied/computed predicate is not "
            "a standalone filter unless the user states a concrete governed value."
        )
    )


class StandardDraftObligation(FrozenModel):
    obligation_id: str = Field(min_length=1)
    capability_key: ManagerCapabilityKey
    origin: Literal["USER_MUST", "USER_OPTIONAL", "SYSTEM_REQUIRED"]
    priority: ObligationPriority
    polarity: ObligationPolarity
    source_surfaces: tuple[str, ...] = Field(min_length=1)
    semantic_surfaces: tuple[StandardDraftSemanticSurface, ...] = ()
    ranking_direction: Literal["asc", "desc"] | None = None
    ranking_limit: int | None = Field(default=None, ge=1, le=1000)

    @model_validator(mode="after")
    def _ranking_shape(self):
        if (self.ranking_direction is None) != (self.ranking_limit is None):
            raise ValueError("ranking direction + limit must be supplied together")
        if (
            self.capability_key == ManagerCapabilityKey.RANKING
            and self.polarity == ObligationPolarity.REQUIRED
        ):
            if self.ranking_direction is None or self.ranking_limit is None:
                raise ValueError("required ranking draft needs direction + limit")
        elif self.capability_key != ManagerCapabilityKey.RANKING and (
            self.ranking_direction is not None or self.ranking_limit is not None
        ):
            raise ValueError("ranking params are only valid for ranking obligation")
        return self


class StandardDraftControlRequest(FrozenModel):
    request_id: str = Field(min_length=1)
    category: Literal[
        "NON_AUTHORITATIVE_CONTROL_REQUEST",
        "CONVERSATION_REPAIR",
    ]
    source_surfaces: tuple[str, ...] = Field(min_length=1)


class StandardIntentDraft(FrozenModel):
    obligations: tuple[StandardDraftObligation, ...] = Field(min_length=1)
    control_requests: tuple[StandardDraftControlRequest, ...] = ()

    @model_validator(mode="after")
    def _unique_ids(self):
        obligation_ids = [item.obligation_id for item in self.obligations]
        if len(obligation_ids) != len(set(obligation_ids)):
            raise ValueError("standard draft obligation IDs must be unique")
        control_ids = [item.request_id for item in self.control_requests]
        if len(control_ids) != len(set(control_ids)):
            raise ValueError("standard draft control IDs must be unique")
        return self


@dataclass(frozen=True)
class StandardLaneOutcome:
    status: StandardLaneStatus
    reasons: tuple[str, ...] = ()
    obligations: tuple[CandidateObligation, ...] = ()
    projection: StandardProjection | None = None
    authority: AcceptedStandardAuthority | None = None
    execution: StandardExecutionResult | None = None
    work_mode: StandardWorkMode | None = None
    attempts: int = 0
    coverage_status: str | None = None

    @property
    def accepted(self) -> bool:
        return (
            self.status == StandardLaneStatus.ACCEPTED
            and self.projection is not None
            and self.authority is not None
            and self.execution is not None
        )


_STANDARD_DRAFT_SYSTEM = """You are Dima's bounded STANDARD profile intent drafter.

Create one complete non-authoritative typed draft from USER_MESSAGE using only the
registered CAPABILITY_CONTRACT.

Rules:
- Preserve every material requested business result and every explicit exclusion.
- Every source_surface and semantic surface MUST be an exact substring of USER_MESSAGE.
- semantic_surfaces contain only tenant semantic concepts that need governed binding:
  metric, dimension, filter, time, comparison.
- FILTER CONTRACT: emit kind=filter only for an explicit concrete category/entity VALUE
  stated by the user that can restrict rows through the governed value catalog. Do NOT split
  descriptive qualifiers, negation, qualitative modifiers, implied/computed predicates, or
  business adjectives into standalone filters. Keep such wording inside the exact metric/dimension
  surface it qualifies when that wording is part of the requested business concept.
- EVERY item placed in semantic_surfaces is MATERIAL and binding-required. A contextual/non-material
  phrase must not be placed there. A declared semantic surface may never be silently dropped merely
  because another surface of the same semantic kind resolved.
- Do not invent canonical IDs, database fields, aliases, semantic handles, SQL or joins.
- Ranking direction/limit are operation parameters, not semantic concepts.
- A root-cause, relationship, investigative or other Research capability MUST remain
  represented by its registered capability key; do not downgrade it to PERFORMANCE.
- Presentation-only capability may remain typed but must not become numeric/query authority.
- If the user text is a conversation repair/control request, expose it only as a
  non-authoritative control request; do not manufacture a business exclusion.
- REVISION_FEEDBACK can identify representation loss. Repair only from exact user-message
  evidence; never invent missing semantics.

Return strict schema only.
"""


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["required"] = list(properties.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


class StandardLaneEngine:
    """One finite Standard attempt family with deterministic seal/execution boundaries."""

    def __init__(
        self,
        *,
        intent_structured: Callable[..., Any],
        coverage_structured: Callable[..., Any],
        semantic_provider: SemanticCandidateDecisionProvider | None,
        temporal_provider: TemporalNormalizationProvider | None,
        capabilities: ManagerCapabilityRegistry | None = None,
        authority_registry: AcceptedAuthorityRegistry | None = None,
        max_draft_attempts: int = 2,
    ) -> None:
        if not callable(intent_structured):
            raise ValueError("intent structured_json callable required")
        if not callable(coverage_structured):
            raise ValueError("coverage structured_json callable required")
        self._intent_structured = intent_structured
        self._coverage_structured = coverage_structured
        self._semantic_provider = semantic_provider
        self._temporal_provider = temporal_provider
        self._capabilities = capabilities or ManagerCapabilityRegistry()
        self._authorities = authority_registry or AcceptedAuthorityRegistry()
        self._max_draft_attempts = max(1, int(max_draft_attempts))

    @property
    def authority_registry(self) -> AcceptedAuthorityRegistry:
        return self._authorities

    @staticmethod
    def _coverage_requires_research(audit: StandardCoverageAudit) -> bool:
        return any(
            issue.kind == StandardCoverageIssueKind.RESEARCH_NEED_OMITTED
            for issue in audit.issues
        )

    @staticmethod
    def _coverage_reasons(audit: StandardCoverageAudit) -> tuple[str, ...]:
        return tuple(
            f"{issue.kind.value}: {issue.note}"
            for issue in audit.issues
        )

    def bind_authority_registry(
        self,
        registry: AcceptedAuthorityRegistry,
    ) -> None:
        if self._authorities is registry:
            return
        if self._authorities.has_any:
            raise RuntimeError(
                "cannot rebind Standard authority registry after authority commit"
            )
        self._authorities = registry

    def _draft(
        self,
        *,
        question: str,
        conversation: ConversationStateV2 | None,
        revision_feedback: dict[str, Any] | None,
    ) -> StandardIntentDraft:
        payload = {
            "USER_MESSAGE": question,
            "CONVERSATION_SURFACE": {
                "has_prior_analytical_request": bool(
                    conversation
                    and conversation.has_prior_analytical_request
                ),
                "has_active_result": bool(
                    conversation and conversation.has_active_result
                ),
                "pending_clarification": bool(
                    conversation and conversation.pending_clarification
                ),
                "topic_labels": list(
                    conversation.topic_labels if conversation else ()
                ),
                "focus_labels": list(
                    conversation.focus_labels if conversation else ()
                ),
            },
            "CAPABILITY_CONTRACT": self._capabilities.manager_contract(),
            "REVISION_FEEDBACK": revision_feedback,
        }
        schema = _strict_schema(StandardIntentDraft.model_json_schema())
        raw = self._intent_structured(
            _STANDARD_DRAFT_SYSTEM,
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            schema=schema,
            schema_name="dima_standard_intent_draft_v1",
        )
        data = json.loads(raw) if isinstance(raw, str) else raw
        return StandardIntentDraft.model_validate(data)

    @staticmethod
    def _validate_exact_surfaces(
        *,
        draft: StandardIntentDraft,
        source_spans: SourceSpanRegistry,
        message_id: str,
    ) -> tuple[str, ...]:
        errors: list[str] = []

        def check(owner: str, surface: str) -> None:
            try:
                source_spans.mint_exact(
                    message_id=message_id,
                    surface=surface,
                )
            except (KeyError, ValueError):
                errors.append(
                    f"{owner}: source surface is not exact current-message evidence: "
                    f"{surface!r}"
                )

        for obligation in draft.obligations:
            for surface in obligation.source_surfaces:
                check(obligation.obligation_id, surface)
            for semantic in obligation.semantic_surfaces:
                check(obligation.obligation_id, semantic.surface)
        for control in draft.control_requests:
            for surface in control.source_surfaces:
                check(control.request_id, surface)
        return tuple(errors)

    @staticmethod
    def _normalized_kind(kind: str) -> str:
        return "period" if kind == "time" else kind

    def _ground(
        self,
        *,
        draft: StandardIntentDraft,
        message_id: str,
        source_spans: SourceSpanRegistry,
        adapter: ManagerSemanticResolutionAdapter,
    ) -> tuple[tuple[CandidateObligation, ...], tuple[str, ...]]:
        unique: list[tuple[str, str]] = []
        for obligation in draft.obligations:
            for item in obligation.semantic_surfaces:
                pair = (item.surface, item.kind_hint)
                if pair not in unique:
                    unique.append(pair)

        resolved_by_pair: dict[tuple[str, str], SemanticBindingRef] = {}
        unresolved_pairs: set[tuple[str, str]] = set()

        if unique:
            refs = tuple(
                source_spans.mint_exact(
                    message_id=message_id,
                    surface=surface,
                ).source_ref
                for surface, _ in unique
            )
            hints = tuple(kind for _, kind in unique)
            result = adapter.resolve(
                ResolveSemanticsArgs(
                    provenance="USER_SOURCE",
                    source_refs=refs,
                    target_kind_hints=hints,
                )
            )
            by_ref = {
                item.source_ref: item
                for item in result.resolved
                if item.source_ref is not None
            }
            unresolved_refs = set(result.unresolved_source_refs)
            for pair, source_ref in zip(unique, refs, strict=True):
                resolved = by_ref.get(source_ref)
                if resolved is None or source_ref in unresolved_refs:
                    unresolved_pairs.add(pair)
                    continue
                resolved_by_pair[pair] = SemanticBindingRef(
                    source_ref=source_ref,
                    handle_id=resolved.handle.handle_id,
                    target_kind=resolved.handle.target_kind,
                )

        obligations: list[CandidateObligation] = []
        material_gaps: list[str] = []

        for item in draft.obligations:
            bindings = tuple(
                dict.fromkeys(
                    resolved_by_pair[(surface.surface, surface.kind_hint)]
                    for surface in item.semantic_surfaces
                    if (surface.surface, surface.kind_hint) in resolved_by_pair
                )
            )
            declared_pairs = tuple(
                (surface.surface, surface.kind_hint)
                for surface in item.semantic_surfaces
            )
            unresolved_declared = tuple(
                pair
                for pair in declared_pairs
                if pair in unresolved_pairs or pair not in resolved_by_pair
            )
            if unresolved_declared:
                material_gaps.append(
                    f"{item.obligation_id}: unresolved governed semantic surfaces: "
                    + ", ".join(
                        f"{surface!r}/{kind}"
                        for surface, kind in unresolved_declared
                    )
                )

            # Accounting invariant: every declared semantic surface is either bound
            # or explicitly unresolved. This prevents same-kind partial binding from
            # being hidden by the older kind-level completeness check.
            accounted_pairs = set(resolved_by_pair).union(unresolved_pairs)
            unaccounted = tuple(
                pair for pair in declared_pairs if pair not in accounted_pairs
            )
            if unaccounted:
                raise RuntimeError(
                    "standard semantic accounting invariant violated: "
                    + ", ".join(
                        f"{surface!r}/{kind}" for surface, kind in unaccounted
                    )
                )

            resolved_kinds = {
                self._normalized_kind(binding.target_kind)
                for binding in bindings
            }
            spec = self._capabilities.get(item.capability_key)
            required = (
                spec.required_kinds
                if item.polarity == ObligationPolarity.REQUIRED
                else spec.exclusion_required_kinds
            )
            missing = sorted(required - resolved_kinds)
            if missing:
                material_gaps.append(
                    f"{item.obligation_id}: missing required governed semantic kinds: "
                    + ", ".join(missing)
                )

            source_refs = tuple(
                source_spans.mint_exact(
                    message_id=message_id,
                    surface=surface,
                ).source_ref
                for surface in item.source_surfaces
            )
            obligations.append(
                CandidateObligation(
                    obligation_id=item.obligation_id,
                    capability_key=item.capability_key,
                    origin=ObligationOrigin(item.origin),
                    priority=item.priority,
                    polarity=item.polarity,
                    source_refs=source_refs,
                    semantic_handle_refs=tuple(
                        dict.fromkeys(binding.handle_id for binding in bindings)
                    ),
                    semantic_bindings=bindings,
                    ranking_direction=item.ranking_direction,
                    ranking_limit=item.ranking_limit,
                )
            )

        return tuple(obligations), tuple(material_gaps)

    def run(
        self,
        *,
        question: str,
        turn_id: str,
        request_ref: str,
        semantic_context: BoundedSemanticContextV0,
        schema: dict,
        conversation: ConversationStateV2,
        tenant_binding: str,
        cognition_model_role: str,
        principal,
        service,
        tenant_runtime,
        contract_store,
        session_id: str | None,
    ) -> StandardLaneOutcome:
        source_spans = SourceSpanRegistry()
        source_hash = source_spans.register_message(
            message_id=turn_id,
            text=question,
        )
        handles = SemanticHandleRegistry()
        semantic_adapter = ManagerSemanticResolutionAdapter(
            source_spans=source_spans,
            semantic_handles=handles,
            semantic_context=semantic_context,
            conversation=conversation,
            schema=schema,
            tenant_binding=tenant_binding,
            session_id=session_id,
            thread_id=None,
            semantic_decision_provider=self._semantic_provider,
            temporal_normalization_provider=self._temporal_provider,
        )
        compiler = StandardProjectionCompiler(
            semantic_handles=handles,
            capabilities=self._capabilities,
        )
        builder = StandardBuilderSession(
            compiler=compiler,
            tenant_binding=tenant_binding,
            context_version=semantic_context.context_version.version,
        )
        representability = RepresentabilityGate(self._capabilities)
        coverage = StandardCoverageVeto(
            structured=self._coverage_structured,
            source_spans=source_spans,
        )
        sealer = StandardAuthoritySealer(semantic_handles=handles)
        executor = WrenStandardExecutionAdapter(semantic_handles=handles)

        revision_feedback: dict[str, Any] | None = None

        for attempt in range(1, self._max_draft_attempts + 1):
            try:
                draft = self._draft(
                    question=question,
                    conversation=conversation,
                    revision_feedback=revision_feedback,
                )
            except Exception as exc:
                if attempt < self._max_draft_attempts:
                    revision_feedback = {
                        "kind": "DRAFT_CONTRACT_REJECTED",
                        "reasons": [
                            "typed response did not satisfy StandardIntentDraft",
                        ],
                    }
                    continue
                return StandardLaneOutcome(
                    status=StandardLaneStatus.FAILED,
                    reasons=(f"standard intent draft failed: {type(exc).__name__}: {exc}",),
                    attempts=attempt,
                )

            exact_errors = self._validate_exact_surfaces(
                draft=draft,
                source_spans=source_spans,
                message_id=turn_id,
            )
            if exact_errors:
                if attempt < self._max_draft_attempts:
                    revision_feedback = {
                        "kind": "SOURCE_CONTRACT_REJECTED",
                        "reasons": list(exact_errors),
                    }
                    continue
                return StandardLaneOutcome(
                    status=StandardLaneStatus.COGNITION_REJECTED,
                    reasons=exact_errors,
                    attempts=attempt,
                )

            try:
                obligations, material_gaps = self._ground(
                    draft=draft,
                    message_id=turn_id,
                    source_spans=source_spans,
                    adapter=semantic_adapter,
                )
            except Exception as exc:
                return StandardLaneOutcome(
                    status=StandardLaneStatus.FAILED,
                    reasons=(f"standard governed grounding failed: {type(exc).__name__}: {exc}",),
                    attempts=attempt,
                )

            def coverage_guard() -> StandardCoverageAudit | StandardLaneOutcome:
                try:
                    return coverage.audit(
                        question=question,
                        obligations=obligations,
                        source_message_hash=source_hash,
                    )
                except Exception as exc:
                    return StandardLaneOutcome(
                        status=StandardLaneStatus.FAILED,
                        reasons=(
                            f"standard coverage failed: {type(exc).__name__}: {exc}",
                        ),
                        obligations=obligations,
                        attempts=attempt,
                    )

            # Conversation/control semantics remain non-Research by default.  The only
            # allowed bridge is the existing typed omission veto over the raw message.
            if draft.control_requests:
                audit = coverage_guard()
                if isinstance(audit, StandardLaneOutcome):
                    return audit
                if self._coverage_requires_research(audit):
                    return StandardLaneOutcome(
                        status=StandardLaneStatus.RESEARCH_REQUIRED,
                        reasons=self._coverage_reasons(audit),
                        attempts=attempt,
                        coverage_status=audit.status,
                    )
                return StandardLaneOutcome(
                    status=StandardLaneStatus.CLARIFICATION_REQUIRED,
                    reasons=(
                        "standard fresh-turn SI path does not convert conversation control "
                        "requests into business authority",
                    ),
                    obligations=obligations,
                    attempts=attempt,
                    coverage_status=audit.status,
                )

            # A genuine semantic gap remains a clarification unless the independent
            # omission guard proves that the Standard view dropped material Research work.
            if material_gaps:
                audit = coverage_guard()
                if isinstance(audit, StandardLaneOutcome):
                    return audit
                if self._coverage_requires_research(audit):
                    return StandardLaneOutcome(
                        status=StandardLaneStatus.RESEARCH_REQUIRED,
                        reasons=self._coverage_reasons(audit),
                        attempts=attempt,
                        coverage_status=audit.status,
                    )
                return StandardLaneOutcome(
                    status=StandardLaneStatus.CLARIFICATION_REQUIRED,
                    reasons=material_gaps,
                    obligations=obligations,
                    attempts=attempt,
                    coverage_status=audit.status,
                )

            # Reuse the existing deterministic representability owner before asking the
            # omission guard to spend another cognition call. Correctly typed Research
            # authority never needs a coverage call merely to discover its lane.
            preliminary = representability.decide_bound(
                obligations=obligations,
                projection=None,
            )
            if preliminary.decision == RepresentabilityDecision.RESEARCH_REQUIRED:
                return StandardLaneOutcome(
                    status=StandardLaneStatus.RESEARCH_REQUIRED,
                    reasons=preliminary.reasons,
                    attempts=attempt,
                )

            # Presentation-only / otherwise non-executable Standard candidates must still
            # allow the omission guard to detect independently omitted Research intent.
            if preliminary.decision in {
                RepresentabilityDecision.CLARIFICATION_REQUIRED,
                RepresentabilityDecision.UNSUPPORTED,
            }:
                audit = coverage_guard()
                if isinstance(audit, StandardLaneOutcome):
                    return audit
                if self._coverage_requires_research(audit):
                    return StandardLaneOutcome(
                        status=StandardLaneStatus.RESEARCH_REQUIRED,
                        reasons=self._coverage_reasons(audit),
                        attempts=attempt,
                        coverage_status=audit.status,
                    )
                terminal_status = (
                    StandardLaneStatus.CLARIFICATION_REQUIRED
                    if preliminary.decision
                    == RepresentabilityDecision.CLARIFICATION_REQUIRED
                    else StandardLaneStatus.UNSUPPORTED
                )
                return StandardLaneOutcome(
                    status=terminal_status,
                    reasons=preliminary.reasons,
                    obligations=obligations,
                    attempts=attempt,
                    coverage_status=audit.status,
                )

            builder_outcome = builder.submit(obligations)
            if builder_outcome.state == StandardBuilderState.RESEARCH_REQUIRED:
                # No Standard authority is committed and no semantic/projection artifact is
                # exported into Research. Research must start again from the raw message.
                return StandardLaneOutcome(
                    status=StandardLaneStatus.RESEARCH_REQUIRED,
                    reasons=builder_outcome.reasons,
                    attempts=attempt,
                )
            if builder_outcome.state in {
                StandardBuilderState.CLARIFICATION_REQUIRED,
                StandardBuilderState.UNSUPPORTED,
            }:
                audit = coverage_guard()
                if isinstance(audit, StandardLaneOutcome):
                    return audit
                if self._coverage_requires_research(audit):
                    return StandardLaneOutcome(
                        status=StandardLaneStatus.RESEARCH_REQUIRED,
                        reasons=self._coverage_reasons(audit),
                        attempts=attempt,
                        coverage_status=audit.status,
                    )
                terminal_status = (
                    StandardLaneStatus.CLARIFICATION_REQUIRED
                    if builder_outcome.state
                    == StandardBuilderState.CLARIFICATION_REQUIRED
                    else StandardLaneStatus.UNSUPPORTED
                )
                return StandardLaneOutcome(
                    status=terminal_status,
                    reasons=builder_outcome.reasons,
                    obligations=obligations,
                    attempts=attempt,
                    coverage_status=audit.status,
                )
            if builder_outcome.state == StandardBuilderState.NEEDS_REPAIR:
                if attempt < self._max_draft_attempts:
                    revision_feedback = {
                        "kind": "STANDARD_REPRESENTATION_REPAIR",
                        "reasons": list(builder_outcome.reasons),
                    }
                    continue
                return StandardLaneOutcome(
                    status=StandardLaneStatus.COGNITION_REJECTED,
                    reasons=builder_outcome.reasons,
                    obligations=obligations,
                    attempts=attempt,
                )
            if not builder_outcome.projection_ready:
                return StandardLaneOutcome(
                    status=StandardLaneStatus.FAILED,
                    reasons=builder_outcome.reasons
                    or (f"standard builder terminal={builder_outcome.state.value}",),
                    obligations=obligations,
                    attempts=attempt,
                )

            assert builder_outcome.projection is not None
            assert builder_outcome.work_mode is not None

            audit = coverage_guard()
            if isinstance(audit, StandardLaneOutcome):
                return audit

            if self._coverage_requires_research(audit):
                # Coverage is veto-only: it creates no Research authority and exports no
                # Standard semantic/projection state. ProductCoordinator owns the raw
                # Standard -> Research transition.
                return StandardLaneOutcome(
                    status=StandardLaneStatus.RESEARCH_REQUIRED,
                    reasons=self._coverage_reasons(audit),
                    attempts=attempt,
                    coverage_status=audit.status,
                )

            if audit.status != "PASS":
                return StandardLaneOutcome(
                    status=StandardLaneStatus.COGNITION_REJECTED,
                    reasons=self._coverage_reasons(audit),
                    obligations=obligations,
                    projection=builder_outcome.projection,
                    work_mode=builder_outcome.work_mode,
                    attempts=attempt,
                    coverage_status=audit.status,
                )

            authority = sealer.seal(
                projection=builder_outcome.projection,
                turn_id=turn_id,
                request_ref=request_ref,
                source_message_hash=source_hash,
                context_version=semantic_context.context_version.version,
                tenant_binding=tenant_binding,
                accepted_attempt_id=f"standard:{attempt}",
                model_role=cognition_model_role,
                work_mode=builder_outcome.work_mode,
            )
            self._authorities.commit(authority)

            try:
                execution = executor.execute(
                    projection=builder_outcome.projection,
                    authority=authority,
                    tenant_binding=tenant_binding,
                    principal=principal,
                    service=service,
                    runtime=tenant_runtime,
                    contract_store=contract_store,
                    session_id=session_id,
                    question=question,
                )
            except Exception as exc:
                return StandardLaneOutcome(
                    status=StandardLaneStatus.FAILED,
                    reasons=(f"standard execution failed: {type(exc).__name__}: {exc}",),
                    obligations=obligations,
                    projection=builder_outcome.projection,
                    authority=authority,
                    work_mode=builder_outcome.work_mode,
                    attempts=attempt,
                    coverage_status=audit.status,
                )

            return StandardLaneOutcome(
                status=StandardLaneStatus.ACCEPTED,
                obligations=obligations,
                projection=builder_outcome.projection,
                authority=authority,
                execution=execution,
                work_mode=builder_outcome.work_mode,
                attempts=attempt,
                coverage_status=audit.status,
            )

        return StandardLaneOutcome(
            status=StandardLaneStatus.FAILED,
            reasons=("standard finite attempt loop exhausted",),
            attempts=self._max_draft_attempts,
        )
