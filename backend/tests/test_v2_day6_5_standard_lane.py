from __future__ import annotations

import inspect
import json

from app.v2.manager_models import ManagerCapabilityKey
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
)
from app.v2.semantic_linker import (
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from app.v2.standard_lane import (
    StandardIntentDraft,
    StandardLaneEngine,
    StandardLaneStatus,
)


class _SemanticProvider:
    def decide(self, requests):
        choices = []
        for request in requests:
            if request.surface == "net geliri":
                target = next(
                    card.candidate_id
                    for card in request.candidates
                    if card.label == "Net Gelir"
                )
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=target,
                    )
                )
            else:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="AMBIGUOUS",
                    )
                )
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _Execution:
    pass


def _context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-si",
            mdl_version="mdl-si",
            compact_catalog_builder_version="si-test",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="si-test",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="Sales",
                display="Satış",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="Sales.net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir",),
                    ),
                ),
                dimensions=(),
                time_dimensions=("event_date",),
            ),
        ),
    )


def _schema():
    return {"models": [], "cubes": [{"name": "Sales", "dimension_values": {}}]}


def _draft_response(capability="PERFORMANCE"):
    return {
        "obligations": [
            {
                "obligation_id": "U1",
                "capability_key": capability,
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": ["net geliri"],
                "semantic_surfaces": (
                    [{"surface": "net geliri", "kind_hint": "metric"}]
                    if capability != "RELATIONSHIP"
                    else []
                ),
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "control_requests": [],
    }


def _coverage_pass(system, user, *, schema, schema_name):
    assert schema_name == "dima_standard_coverage_v1"
    return {"status": "PASS", "issues": []}


def test_standard_lane_module_has_no_research_authority_dependencies():
    import app.v2.standard_lane as module

    source = inspect.getsource(module)
    assert "AcceptedTurnContract" not in source
    assert "UserObligationLedger" not in source
    assert "ResearchManagerLoop" not in source
    assert "ManagerRuntime" not in source


def test_standard_intent_draft_is_closed_and_typed():
    draft = StandardIntentDraft.model_validate(_draft_response())
    assert draft.obligations[0].capability_key == ManagerCapabilityKey.PERFORMANCE


def test_research_capability_stops_without_standard_authority(monkeypatch):
    def intent(system, user, *, schema, schema_name):
        assert schema_name == "dima_standard_intent_draft_v1"
        return _draft_response("RELATIONSHIP")

    engine = StandardLaneEngine(
        intent_structured=intent,
        coverage_structured=_coverage_pass,
        semantic_provider=_SemanticProvider(),
        temporal_provider=None,
    )

    outcome = engine.run(
        question="net geliri",
        turn_id="turn-research",
        request_ref="request-research",
        semantic_context=_context(),
        schema=_schema(),
        conversation=ConversationStateV2(),
        tenant_binding="tenant-a",
        cognition_model_role="RESEARCH_MANAGER",
        principal=object(),
        service=object(),
        tenant_runtime=object(),
        contract_store=object(),
        session_id=None,
    )
    assert outcome.status == StandardLaneStatus.RESEARCH_REQUIRED
    assert outcome.authority is None
    assert outcome.projection is None
    assert engine.authority_registry.accepted("turn-research") is None
