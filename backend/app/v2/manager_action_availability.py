"""Historical module path retained only as a non-authoritative import shim.

D10-U removed ManagerActionAvailability / ActionApplicabilitySnapshot as independent
control-plane representations. The only executable-action projection owner is
app.v2.manager_action_set.ManagerActionSet.
"""

from app.v2.manager_action_set import (  # noqa: F401
    ActionInstance,
    DirectiveActionState,
    HypothesisActionState,
    InspectableEvidenceState,
    ManagerActionSet,
    ManagerActionSetBuilder,
    ManagerActionSetContext,
    NextTestContractState,
    ParentEvidenceActionState,
    RootActionState,
    SemanticActionRef,
    TaskActionState,
)

__all__ = [
    "ActionInstance",
    "DirectiveActionState",
    "HypothesisActionState",
    "InspectableEvidenceState",
    "ManagerActionSet",
    "ManagerActionSetBuilder",
    "ManagerActionSetContext",
    "NextTestContractState",
    "ParentEvidenceActionState",
    "RootActionState",
    "SemanticActionRef",
    "TaskActionState",
]
