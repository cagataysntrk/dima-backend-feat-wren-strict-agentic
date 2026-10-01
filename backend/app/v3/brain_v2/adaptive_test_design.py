"""Brain V2 adapter for one governed P19 -> P17 discriminating test design.

This module owns no analytical semantics. It only narrows the existing P17
proposal manager to the exact obligation, current governed Evidence, and the
single TEST_DISCRIMINATING_EVIDENCE intent authorized by a typed NextTestRequest.
"""
from __future__ import annotations

from typing import Any

from app.v3.analytical_request_contract import (
    AnalyticalRequestContract,
    AnalyticalRequestMismatch,
    assert_child_request_scope,
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


class AdaptiveTestDesignError(RuntimeError):
    """The P17 design result escaped the typed adaptive boundary."""


def typed_child_scope_for_next_test(
    *,
    parent: AnalyticalRequestContract,
    request: NextTestRequest,
) -> AnalyticalRequestContract:
    """Project only the typed material delta authorized by a P19 next-test surface.

    This is not a query plan. It can only reuse already accepted semantic refs
    and the child-scope mutation law enforced by assert_child_request_scope().
    """

    if request.required_evidence_surface != NextTestEvidenceSurface.TEMPORAL_ORDER:
        raise AdaptiveTestDesignError(
            "no deterministic child material delta exists for "
            + request.required_evidence_surface.value
        )

    temporal = parent.temporal_observation
    if temporal is None:
        raise AdaptiveTestDesignError(
            "TEMPORAL_ORDER requires accepted temporal-observation authority"
        )
    time_ref = temporal.time_dimension
    dimensions = tuple(dict.fromkeys((*parent.dimension_refs, time_ref)))
    grains = tuple(dict.fromkeys((*parent.grain_constraints, time_ref)))
    if (
        dimensions == parent.dimension_refs
        and grains == parent.grain_constraints
    ):
        raise AdaptiveTestDesignError(
            "TEMPORAL_ORDER child scope would repeat parent material"
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
            "typed next-test child scope is not legal: " + exc.code
        ) from exc
    return child


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
