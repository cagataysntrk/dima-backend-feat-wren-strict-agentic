"""D65-J1B provider-contract separation and P0 tests."""

from __future__ import annotations

import inspect
import json

import pytest

from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    SemanticDecisionProviderError,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
    StructuredSemanticCandidateDecisionProvider,
)
from app.v2.temporal_intent import (
    StructuredTemporalNormalizationProvider,
    TemporalNormalizationBatch,
    TemporalNormalizationChoice,
    TypedTemporalNormalizer,
)
from app.v2.jev_decision_provider import JevDecisionProvider

from test_v2_day6_5_semantic_linker import _context, _schema


class _SemanticProvider:
    def __init__(self, decision):
        self.decision = decision
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        return self.decision(requests)


def _linker(provider):
    from app.v2.semantic_handles import SemanticHandleRegistry

    handles = SemanticHandleRegistry()
    return BoundedSemanticLinker(
        generator=SemanticCandidateGenerator(
            semantic_context=_context(),
            schema=_schema(),
        ),
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-j1b",
            context_version="ctx-linker-v1",
        ),
        provider=provider,
    )


def test_manager_semantic_adapter_has_two_physical_cognition_contracts():
    params = inspect.signature(ManagerSemanticResolutionAdapter.__init__).parameters
    assert "semantic_linker_structured" not in params
    assert "semantic_decision_provider" in params
    assert "temporal_normalization_provider" in params


def test_semantic_provider_failure_is_visible_and_never_becomes_abstain():
    class Broken:
        def decide(self, requests):
            raise SemanticDecisionProviderError("synthetic provider failure")

    linker = _linker(Broken())
    with pytest.raises(SemanticDecisionProviderError, match="synthetic"):
        linker.resolve(
            (("r1", "brüt gelir toplamı", "metric"),),
            provenance_type="USER_SOURCE",
        )


def test_candidate_set_escape_still_fails_at_semantic_authority_boundary():
    provider = _SemanticProvider(
        lambda requests: SemanticLinkBatchDecision(
            choices=(
                SemanticLinkChoice(
                    request_id=requests[0].request_id,
                    decision="SELECT",
                    candidate_id="cand_" + "f" * 24,
                ),
            )
        )
    )
    linker = _linker(provider)
    with pytest.raises(Exception, match="outside"):
        linker.resolve(
            (("r1", "brüt gelir toplamı", "metric"),),
            provenance_type="USER_SOURCE",
        )


def test_structured_semantic_and_temporal_adapters_are_not_one_generic_contract():
    seen = []

    def structured(system, user, *, schema, schema_name):
        seen.append(schema_name)
        if schema_name == "dima_bounded_semantic_link_v1":
            request = json.loads(user)["requests"][0]
            return {
                "choices": [
                    {
                        "request_id": request["request_id"],
                        "decision": "ABSTAIN",
                        "candidate_id": None,
                        "reason": "AMBIGUOUS",
                    }
                ]
            }
        if schema_name == "dima_typed_temporal_intent_v1":
            request = json.loads(user)["requests"][0]
            return {
                "choices": [
                    {
                        "request_id": request["request_id"],
                        "target": request["target"],
                        "decision": "ABSTAIN",
                        "period_kind": None,
                        "comparison_kind": None,
                        "n": None,
                        "implicit_base_period_kind": None,
                        "implicit_base_n": None,
                        "reason": "AMBIGUOUS",
                    }
                ]
            }
        raise AssertionError(schema_name)

    semantic = StructuredSemanticCandidateDecisionProvider(structured=structured)
    temporal = StructuredTemporalNormalizationProvider(structured=structured)

    linker = _linker(semantic)
    (selection,) = linker.resolve(
        (("s1", "gelir toplamı", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "ABSTAIN"

    (choice,) = TypedTemporalNormalizer(provider=temporal).normalize(
        (("t1", "son dönem", "PERIOD"),)
    )
    assert choice.decision == "ABSTAIN"
    assert seen == [
        "dima_bounded_semantic_link_v1",
        "dima_typed_temporal_intent_v1",
    ]


def test_jev_payload_contains_only_llm_safe_candidate_cards(monkeypatch):
    captured = {}

    class Response:
        status_code = 200
        text = ""

        def json(self):
            request_id = captured["payload"]["state"]["records"][0]["id"]
            candidate = next(
                key
                for key in captured["payload"]["questions"]["decision"]["criteria"]
                if key != "ABSTAIN"
            )
            return {
                "answers": {
                    "decision": {
                        "choice": candidate,
                        "confidence": 0.8,
                        "probabilities": {candidate: 0.8, "ABSTAIN": 0.2},
                    },
                    "abstain_reason": {"choice": "INSUFFICIENT_CONTEXT"},
                }
            }

    class Client:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None
        def post(self, url, *, headers, json):
            del headers
            captured["url"] = url
            captured["payload"] = json
            return Response()

    import app.v2.jev_decision_provider as module
    monkeypatch.setattr(module.httpx, "Client", Client)

    probe = _linker(None)
    candidate_set = probe._generator.generate(
        request_id="r1",
        surface="brüt gelir toplamı",
        kind_hint="metric",
    )
    provider = JevDecisionProvider(api_key="fake")
    result = provider.decide((
        __import__("app.v2.semantic_linker", fromlist=["SemanticLinkRequestCard"]).SemanticLinkRequestCard(
            request_id="r1",
            surface="brüt gelir toplamı",
            kind_hint="metric",
            candidates=candidate_set.cards,
        ),
    ))
    assert result.choices[0].decision == "SELECT"
    record = captured["payload"]["state"]["records"][0]["record"]
    assert "canonical_name" not in record
    assert "sales.gross_revenue" not in record
    assert "sql" not in record.lower()
    assert captured["url"].endswith("/api/alpha/decisions")


def test_jev_provider_has_no_silent_fallback(monkeypatch):
    class Response:
        status_code = 503
        text = "unavailable"

    class Client:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None
        def post(self, *args, **kwargs):
            return Response()

    import app.v2.jev_decision_provider as module
    monkeypatch.setattr(module.httpx, "Client", Client)

    probe = _linker(None)
    candidate_set = probe._generator.generate(
        request_id="r1",
        surface="brüt gelir toplamı",
        kind_hint="metric",
    )
    request_cls = __import__(
        "app.v2.semantic_linker", fromlist=["SemanticLinkRequestCard"]
    ).SemanticLinkRequestCard
    provider = JevDecisionProvider(api_key="fake")
    with pytest.raises(SemanticDecisionProviderError, match="503"):
        provider.decide((
            request_cls(
                request_id="r1",
                surface="brüt gelir toplamı",
                kind_hint="metric",
                candidates=candidate_set.cards,
            ),
        ))
