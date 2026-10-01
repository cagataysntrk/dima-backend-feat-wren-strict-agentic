"""Brain V2 adapter for one governed P19 -> P17 discriminating test design.

This module owns no analytical semantics. It only narrows the existing P17
proposal manager to the exact obligation, current governed Evidence, and the
single TEST_DISCRIMINATING_EVIDENCE intent authorized by a typed NextTestRequest.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v3.analytical_request_contract import (
    AnalyticalRequestContract,
    AnalyticalRequestMismatch,
    assert_child_request_scope,
    material_coverage_contract,
)
from app.v3.hypothesis_root_cause_v1 import (
    NextTestEvidenceSurface,
    NextTestRequest,
)
from app.v3.research_manager import (
    InvestigationIntent,
    ManagerAction,
    ManagerProposal,
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ChildMaterialDelta(Frozen):
    """One deterministic analytical deepening inside unchanged user scope."""

    scope_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    parent_material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    child_material_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    added_required_breakout_refs: tuple[str, ...] = ()
    added_allowed_breakout_refs: tuple[str, ...] = ()
    child_contract: AnalyticalRequestContract

    @model_validator(mode="after")
    def material_changes_without_scope_mutation(self):
        if self.child_contract.scope_fingerprint != self.scope_fingerprint:
            raise ValueError("child material changed user scope fingerprint")
        if (
            self.child_material_fingerprint
            != self.child_contract.material_fingerprint
        ):
            raise ValueError("child material fingerprint does not match contract")
        if self.parent_material_fingerprint == self.child_material_fingerprint:
            raise ValueError("child material delta must add new analytical material")
        return self


class AdaptiveTestDesignError(RuntimeError):
    """The P17 design result escaped the typed adaptive boundary."""


def _parent_governed_refs(
    parent: AnalyticalRequestContract,
) -> tuple[str, ...]:
    values = [
        *parent.metric_refs,
        *parent.dimension_refs,
        *(item.source_candidate_id for item in parent.filters),
    ]
    if parent.period is not None:
        values.append(parent.period.time_dimension)
    if parent.comparison is not None:
        values.extend(
            (
                parent.comparison.reference_period.time_dimension,
                parent.comparison.base_period.time_dimension,
            )
        )
    if parent.temporal_observation is not None:
        values.append(parent.temporal_observation.time_dimension)
    if getattr(parent.ranking, "measure", None):
        values.append(parent.ranking.measure)
    return tuple(dict.fromkeys(values))


def typed_child_material_delta_for_next_test(
    *,
    parent: AnalyticalRequestContract,
    request: NextTestRequest,
    governed_semantic_refs: tuple[str, ...],
) -> ChildMaterialDelta:
    """Project one typed information-gain delta without mutating user scope."""

    if (
        request.scope_lineage_id != parent.scope_identity.lineage_id
        or request.scope_version_id != parent.scope_identity.version_id
    ):
        raise AdaptiveTestDesignError(
            "typed child material must remain on the current accepted scope"
        )

    if request.required_evidence_surface != NextTestEvidenceSurface.TEMPORAL_ORDER:
        raise AdaptiveTestDesignError(
            "no deterministic child material delta exists for "
            + request.required_evidence_surface.value
        )

    if parent.comparison is not None or parent.temporal_observation is not None:
        raise AdaptiveTestDesignError(
            "TEMPORAL_ORDER is already observable in parent material; "
            "no materially new child material exists"
        )
    if parent.period is None:
        raise AdaptiveTestDesignError(
            "TEMPORAL_ORDER requires accepted bounded time authority"
        )

    time_ref = parent.period.time_dimension
    if time_ref not in set(governed_semantic_refs):
        raise AdaptiveTestDesignError(
            "typed child material may use only governed semantic refs"
        )

    dimensions = tuple(dict.fromkeys((*parent.dimension_refs, time_ref)))
    grains = tuple(dict.fromkeys((*parent.grain_constraints, time_ref)))
    if (
        dimensions == parent.dimension_refs
        and grains == parent.grain_constraints
    ):
        raise AdaptiveTestDesignError(
            "TEMPORAL_ORDER child material would repeat parent material"
        )

    child = parent.model_copy(
        update={
            "dimension_refs": dimensions,
            "grain_constraints": grains,
        }
    )
    try:
        assert_child_request_scope(parent, child)
    except AnalyticalRequestMismatch as exc:
        raise AdaptiveTestDesignError(
            "typed next-test child material is not legal: " + exc.code
        ) from exc

    parent_coverage = material_coverage_contract(parent)
    child_coverage = material_coverage_contract(child)
    parent_required = set(parent_coverage.required_breakout_refs)
    child_required = set(child_coverage.required_breakout_refs)
    parent_allowed = set(parent_coverage.allowed_breakout_refs)
    child_allowed = set(child_coverage.allowed_breakout_refs)

    return ChildMaterialDelta(
        scope_fingerprint=parent.scope_fingerprint,
        parent_material_fingerprint=parent.material_fingerprint,
        child_material_fingerprint=child.material_fingerprint,
        added_required_breakout_refs=tuple(
            item
            for item in child_coverage.required_breakout_refs
            if item not in parent_required
        ),
        added_allowed_breakout_refs=tuple(
            item
            for item in child_coverage.allowed_breakout_refs
            if item not in parent_allowed
        ),
        child_contract=child,
    )


def typed_child_scope_for_next_test(
    *,
    parent: AnalyticalRequestContract,
    request: NextTestRequest,
) -> AnalyticalRequestContract:
    """Backward-compatible wrapper returning only the child material contract."""

    return typed_child_material_delta_for_next_test(
        parent=parent,
        request=request,
        governed_semantic_refs=_parent_governed_refs(parent),
    ).child_contract


class TypedNextTestProposalManager:
    """Compose existing P17 cognition without creating a second planner."""

    def __init__(
        self,
        *,
        inner: Any,
        request: NextTestRequest,
        obligation_id: str,
        evidence_refs: tuple[str, ...],
    ) -> None:
        self._inner = inner
        self._request = request
        self._obligation_id = obligation_id
        self._evidence_refs = tuple(dict.fromkeys(evidence_refs))

    def propose(self, snapshot) -> ManagerProposal:
        propose = getattr(
            self._inner,
            "propose_for_obligation_with_constraints",
            None,
        )
        if not callable(propose):
            raise AdaptiveTestDesignError(
                "P17 manager does not expose constrained obligation design"
            )
        proposal = propose(
            snapshot,
            target_parent_obligation=self._obligation_id,
            allowed_evidence_refs=self._evidence_refs,
            allowed_intents=(
                InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE,
            ),
        )
        if proposal.target_parent_obligation != self._obligation_id:
            raise AdaptiveTestDesignError(
                "P17 discriminating design escaped the authorized obligation"
            )
        if (
            proposal.action != ManagerAction.EXPLORE_NATIVE
            or proposal.intent
            != InvestigationIntent.TEST_DISCRIMINATING_EVIDENCE
        ):
            raise AdaptiveTestDesignError(
                "P17 discriminating design escaped the authorized intent"
            )
        if not proposal.bounded_objective:
            raise AdaptiveTestDesignError(
                "P17 discriminating design requires one bounded objective"
            )

        # P19 owns the durable NextTestRequest identity. P17 owns the bounded
        # analytical question, while Dima binds the machine identity here.
        return proposal.model_copy(
            update={
                "target_ref": self._request.request_id,
                "objective_key": "next_test." + self._request.request_id[4:],
            }
        )
