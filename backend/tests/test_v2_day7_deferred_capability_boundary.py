"""Provider-free Day7 proof for recognized-but-deferred analytical capabilities."""

from __future__ import annotations

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_models import (
    AcceptanceStatus,
    CandidateObligation,
    ManagerCapabilityKey,
    ManagerState,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    UserIntentEnvelope,
)
from app.v2.manager_preacceptance import (
    FiniteAcceptanceStatus,
    PreAcceptanceController,
)
from app.v2.manager_runtime import ManagerRuntime
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


class _ForbiddenExecutor:
    def execute(self, *args, **kwargs):
        raise AssertionError("deferred capability must stop before governed tool execution")


def _draft_payload(capability: str, source_surface: str, semantic_surface: str):
    return {
        "obligations": [
            {
                "obligation_id": "obligation_1",
                "capability_key": capability,
                "origin": "USER_MUST",
                "priority": "MUST",
                "polarity": "REQUIRED",
                "source_surfaces": [source_surface],
                "semantic_surfaces": [
                    {
                        "surface": semantic_surface,
                        "kind_hint": "metric",
                    }
                ],
                "open_questions": [],
                "ranking_direction": None,
                "ranking_limit": None,
            }
        ],
        "research_directives": [],
        "control_requests": [],
    }


@pytest.mark.parametrize(
    ("capability", "question", "source_surface"),
    [
        ("trend", "Net gelir trendini incele.", "Net gelir trendini incele"),
    ],
)
def test_deferred_analytical_capability_stops_before_grounding_and_acceptance(
    capability,
    question,
    source_surface,
):
    spans = SourceSpanRegistry()
    message_id = f"turn-{capability}"
    source_hash = spans.register_message(message_id=message_id, text=question)
    calls = []

    def structured(_system, _user, *, schema, schema_name):
        del schema
        calls.append(schema_name)
        if schema_name != "dima_intent_draft_v1":
            raise AssertionError(
                "deferred capability must stop before coverage or other cognition"
            )
        return _draft_payload(capability, source_surface, "Net gelir")

    runtime = ManagerRuntime(request_ref=f"req-{capability}")
    outcome = PreAcceptanceController(
        structured=structured,
        source_spans=spans,
    ).run(
        question=question,
        message_id=message_id,
        request_ref=f"req-{capability}",
        source_hash=source_hash,
        runtime=runtime,
        executor=_ForbiddenExecutor(),
        conversation=None,
    )

    assert outcome.status == FiniteAcceptanceStatus.UNSUPPORTED_CAPABILITY
    assert runtime.snapshot.state == ManagerState.BLOCKED
    assert runtime.accepted_contract is None
    assert runtime.ledger is None
    assert runtime.snapshot.data_queries == 0
    assert runtime.semantic_resolution_receipts == ()
    assert calls == ["dima_intent_draft_v1"]
    assert any(
        item.get("kind") == "unsupported_capability"
        and item.get("status") == "DEFERRED"
        for item in outcome.observations
    )


@pytest.mark.parametrize(
    "capability",
    [ManagerCapabilityKey.TREND],
)
def test_direct_acceptance_bypass_rejects_deferred_analytical_capability(capability):
    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    message_id = f"direct-{capability.value}"
    question = "Net gelir"
    source_hash = spans.register_message(message_id=message_id, text=question)
    source_ref = spans.mint_exact(
        message_id=message_id,
        surface="Net gelir",
    ).source_ref

    envelope = UserIntentEnvelope(
        attempt_id="attempt-1",
        turn_id=message_id,
        request_ref=f"req-direct-{capability.value}",
        source_message_hash=source_hash,
        model_role="RESEARCH_MANAGER",
        obligations=(
            CandidateObligation(
                obligation_id="obligation_1",
                capability_key=capability,
                origin=ObligationOrigin.USER_MUST,
                priority=ObligationPriority.MUST,
                polarity=ObligationPolarity.REQUIRED,
                source_refs=(source_ref,),
            ),
        ),
    )

    result = IntentAcceptanceGate(
        source_spans=spans,
        semantic_handles=handles,
    ).evaluate(
        envelope=envelope,
        tenant_binding="id:day7-deferred",
        context_version="ctx-day7-deferred",
    )

    assert result.status == AcceptanceStatus.REJECTED
    assert result.contract is None
    assert result.ledger is None
    assert any(
        "direct execution is unavailable" in reason
        for reason in result.reasons
    )
