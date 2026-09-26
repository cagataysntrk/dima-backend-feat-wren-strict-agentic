"""Capability-specific semantic binding validation and deterministic obligation effects.

This module is the canonical boundary between probabilistic Manager proposals and
accepted semantic authority. It validates each obligation atomically before obligations
may conflict, merge, or compile into a Core projection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.v2.manager_models import (
    CandidateObligation,
    ObligationLedgerItem,
    ObligationPolarity,
)
from app.v2.manager_policy import (
    ManagerCapabilityExecutionMode,
    ManagerCapabilityLane,
    ManagerCapabilityRegistry,
    ManagerCapabilitySpec,
)
from app.v2.semantic_handles import SemanticHandleRegistry


BoundObligation = CandidateObligation | ObligationLedgerItem


@dataclass(frozen=True)
class ObligationEffect:
    """Deterministic semantic effect; never produced by the LLM."""

    family: str
    scope_kind: str
    scope_ref: str

    def conflicts_with(self, other: "ObligationEffect") -> bool:
        if self.family != other.family:
            return False
        if self.scope_kind == "global" or other.scope_kind == "global":
            return True
        return (
            self.scope_kind == other.scope_kind
            and self.scope_ref == other.scope_ref
        )


@dataclass(frozen=True)
class CapabilityBinding:
    obligation_id: str
    spec: ManagerCapabilitySpec
    handles_by_kind: tuple[tuple[str, tuple[str, ...]], ...]
    params: tuple[tuple[str, str], ...]
    effects: tuple[ObligationEffect, ...]

    def refs(self, kind: str) -> tuple[str, ...]:
        return dict(self.handles_by_kind).get(kind, ())


@dataclass(frozen=True)
class CapabilityBindingResult:
    binding: CapabilityBinding | None
    reasons: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        return self.binding is not None and not self.reasons


class CapabilityBindingValidator:
    """Validate one obligation against its registered semantic algebra."""

    _KIND_MAP = {
        "metric": "metric",
        "kpi": "metric",
        "dimension": "dimension",
        "entity_value": "filter",
        "filter": "filter",
        "period": "period",
        "time": "period",
        "comparison": "comparison",
    }

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        capabilities: ManagerCapabilityRegistry | None = None,
    ) -> None:
        self._handles = semantic_handles
        self._capabilities = capabilities or ManagerCapabilityRegistry()

    @staticmethod
    def _provided_params(item: BoundObligation) -> dict[str, str]:
        params: dict[str, str] = {}
        ranking_direction = getattr(item, "ranking_direction", None)
        ranking_limit = getattr(item, "ranking_limit", None)
        if ranking_direction is not None:
            params["ranking_direction"] = str(ranking_direction)
        if ranking_limit is not None:
            params["ranking_limit"] = str(int(ranking_limit))
        return params

    @staticmethod
    def _effects(
        *,
        item: BoundObligation,
        spec: ManagerCapabilitySpec,
        handles_by_kind: dict[str, tuple[str, ...]],
        effect_refs_by_kind: dict[str, tuple[str, ...]],
    ) -> tuple[ObligationEffect, ...]:
        family = spec.effect_family
        if not family:
            return ()

        def effects_for(kind: str, refs: tuple[str, ...]) -> tuple[ObligationEffect, ...]:
            return tuple(
                ObligationEffect(
                    family=family,
                    scope_kind=kind,
                    scope_ref=ref,
                )
                for ref in refs
            )

        if family == "measure":
            effects = effects_for("metric", effect_refs_by_kind.get("metric", ()))
        elif family == "group_by":
            effects = effects_for("dimension", effect_refs_by_kind.get("dimension", ()))
        elif family == "rank":
            refs = effect_refs_by_kind.get("dimension", ())
            kind = "dimension"
            if not refs:
                refs = effect_refs_by_kind.get("metric", ())
                kind = "metric"
            effects = effects_for(kind, refs)
        elif family == "compare":
            refs = effect_refs_by_kind.get("comparison", ())
            kind = "comparison"
            if not refs:
                refs = effect_refs_by_kind.get("metric", ())
                kind = "metric"
            effects = effects_for(kind, refs)
        else:
            all_refs = tuple(
                dict.fromkeys(
                    ref
                    for _, refs in sorted(effect_refs_by_kind.items())
                    for ref in refs
                )
            )
            effects = effects_for("semantic", all_refs)

        if effects:
            return effects
        return (
            ObligationEffect(
                family=family,
                scope_kind="global",
                scope_ref="*",
            ),
        )

    def validate(
        self,
        item: BoundObligation,
        *,
        tenant_binding: str,
        context_version: str,
        research_goal_authority: bool = False,
    ) -> CapabilityBindingResult:
        reasons: list[str] = []

        try:
            spec = self._capabilities.get(item.capability_key)
        except KeyError as exc:
            return CapabilityBindingResult(binding=None, reasons=(str(exc),))

        if spec.execution_mode == ManagerCapabilityExecutionMode.DEFERRED:
            return CapabilityBindingResult(
                binding=None,
                reasons=(
                    f"{item.obligation_id}: {item.capability_key.value} is recognized "
                    "but deferred in the current capability surface",
                ),
            )
        # PRESENTATION obligations are accepted as non-executable deliverables.
        # They carry no analytical semantic authority: required/allowed kinds and params
        # remain empty in the registry, so any attempted analytical binding is rejected
        # by the ordinary forbidden-kind/parameter checks below.
        by_kind: dict[str, list[str]] = {}
        effect_by_kind: dict[str, list[str]] = {}
        standard_cube_sets: list[frozenset[str]] = []
        for handle_id in item.semantic_handle_refs:
            try:
                handle = self._handles.validate(
                    handle_id,
                    tenant_binding=tenant_binding,
                    context_version=context_version,
                )
            except (KeyError, ValueError) as exc:
                reasons.append(f"invalid semantic handle {handle_id}: {exc}")
                continue

            normalized = self._KIND_MAP.get(handle.target_kind)
            if normalized is None:
                reasons.append(
                    f"{item.obligation_id}: unsupported semantic handle kind "
                    f"{handle.target_kind}"
                )
                continue
            by_kind.setdefault(normalized, []).append(handle_id)
            # Authority ownership lives in sem_* handle identity, while effect conflict
            # semantics must compare the governed semantic identity underneath it.
            # Fresh owner-bound handles for the same current candidate therefore still
            # conflict deterministically when their business effects oppose each other.
            effect_by_kind.setdefault(normalized, []).append(
                str(handle.resolver_provenance_id)
            )

            if (
                spec.lane == ManagerCapabilityLane.STANDARD
                and item.polarity == ObligationPolarity.REQUIRED
                and normalized in {"metric", "dimension", "filter"}
            ):
                binding = self._handles.binding_for_execution(
                    handle_id,
                    tenant_binding=tenant_binding,
                    context_version=context_version,
                )
                cubes = frozenset(
                    str(value)
                    for value in tuple(
                        getattr(binding.canonical_target, "cube_names", ()) or ()
                    )
                    if str(value)
                )
                if cubes:
                    standard_cube_sets.append(cubes)

        normalized_by_kind = {
            kind: tuple(dict.fromkeys(refs))
            for kind, refs in by_kind.items()
        }
        normalized_effect_by_kind = {
            kind: tuple(dict.fromkeys(refs))
            for kind, refs in effect_by_kind.items()
        }

        present_kinds = set(normalized_by_kind)

        if research_goal_authority:
            if (
                spec.lane != ManagerCapabilityLane.RESEARCH
                or item.polarity != ObligationPolarity.REQUIRED
            ):
                reasons.append(
                    f"{item.obligation_id}: research_goal_authority is valid only for "
                    "REQUIRED Research-lane obligations"
                )
            required_kinds = frozenset()
        else:
            required_kinds = (
                spec.required_kinds
                if item.polarity == ObligationPolarity.REQUIRED
                else spec.exclusion_required_kinds
            )
        missing_kinds = required_kinds - present_kinds
        if missing_kinds:
            reasons.append(
                f"{item.obligation_id}: {item.capability_key.value} missing required semantic kinds: "
                + ", ".join(sorted(missing_kinds))
            )

        forbidden_kinds = present_kinds - spec.allowed_kinds
        if forbidden_kinds:
            reasons.append(
                f"{item.obligation_id}: {item.capability_key.value} contains forbidden semantic kinds: "
                + ", ".join(sorted(forbidden_kinds))
            )

        if standard_cube_sets:
            common_cubes = set(standard_cube_sets[0])
            for cubes in standard_cube_sets[1:]:
                common_cubes.intersection_update(cubes)
            if len(common_cubes) != 1:
                reasons.append(
                    f"{item.obligation_id}: {item.capability_key.value} required STANDARD "
                    "semantic handles must resolve to exactly one common governed cube; "
                    f"candidates={sorted(common_cubes)}"
                )

        params = self._provided_params(item)
        present_params = set(params)
        required_params = (
            frozenset()
            if research_goal_authority
            else (
                spec.required_params
                if item.polarity == ObligationPolarity.REQUIRED
                else frozenset()
            )
        )
        missing_params = required_params - present_params
        if missing_params:
            reasons.append(
                f"{item.obligation_id}: {item.capability_key.value} missing required operation params: "
                + ", ".join(sorted(missing_params))
            )

        forbidden_params = present_params - spec.allowed_params
        if forbidden_params:
            reasons.append(
                f"{item.obligation_id}: {item.capability_key.value} contains forbidden operation params: "
                + ", ".join(sorted(forbidden_params))
            )

        if reasons:
            return CapabilityBindingResult(
                binding=None,
                reasons=tuple(dict.fromkeys(reasons)),
            )

        frozen_handles = tuple(
            (kind, normalized_by_kind[kind])
            for kind in sorted(normalized_by_kind)
        )
        binding = CapabilityBinding(
            obligation_id=item.obligation_id,
            spec=spec,
            handles_by_kind=frozen_handles,
            params=tuple(sorted(params.items())),
            effects=self._effects(
                item=item,
                spec=spec,
                handles_by_kind=normalized_by_kind,
                effect_refs_by_kind=normalized_effect_by_kind,
            ),
        )
        return CapabilityBindingResult(binding=binding)
