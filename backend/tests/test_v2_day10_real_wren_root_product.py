"""D10-G one deterministic real-Wren ROOT_CAUSE Product micro-gate.

No paid model participates.  Probabilistic seams are scripted only where cognition is
the variable; analytical/numeric truth crosses the production Wren/QueryContract/Evidence
path through ProductCoordinator.
"""

from __future__ import annotations

import copy
import json

import pytest

from app import contracts as contracts_module
from app.v2.acceptance import IntentAcceptanceGate
from app.v2.context_provider import ContextProviderV0
from app.v2.manager_executor import GovernedManagerExecutionContext, GovernedManagerExecutor
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_models import ObligationStatus
from app.v2.model_policy import ModelProfile, ModelRole
from app.v2.models import EpistemicLabel, TenantAnalyticsRuntimeV0
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_models import (
    ProductAskRequest,
    ProductEventKind,
    ProductLane,
    ProductRequestContext,
    ProductStatus,
)
from app.v2.report_narration import ReportNarrator
from app.v2.research_lane import ResearchCognition, ResearchLaneService
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import SemanticLinkBatchDecision, SemanticLinkChoice
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_authority import AcceptedAuthorityFamily
from app.v2.standard_lane import StandardLaneEngine
from control_plane.authorize import Principal


class _CountingWren:
    def __init__(self, wren, schema: dict) -> None:
        self._wren = wren
        self._schema = schema
        self.mdl_version = wren.mdl_version
        self.query_calls = 0

    def schema(self):
        return copy.deepcopy(self._schema)

    def cube_sql(self, cube_query: dict):
        return self._wren.cube_sql(cube_query)

    def dry_plan(self, sql: str, *, principal=None):
        return self._wren.dry_plan(sql, principal=principal)

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        return self._wren.query(sql, limit=limit, principal=principal)


class _OmittedResearchStandardLLM:
    """Misclassify as Standard; typed CoverageVeto must recover the omitted Research need."""

    def __init__(self) -> None:
        self.schemas: list[str] = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema
        self.schemas.append(schema_name)
        if schema_name == "dima_standard_intent_draft_v1":
            return {
                "obligations": [
                    {
                        "obligation_id": "S1",
                        "capability_key": "performance",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["arıza sayısı"],
                        "semantic_surfaces": [
                            {"surface": "arıza sayısı", "kind_hint": "metric"},
                        ],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    }
                ],
                "control_requests": [],
            }
        if schema_name == "dima_standard_coverage_v1":
            return {
                "status": "VETO",
                "issues": [
                    {
                        "kind": "RESEARCH_NEED_OMITTED",
                        "source_surfaces": ["nedenini araştır"],
                        "note": "material Research request omitted from Standard view",
                    }
                ],
            }
        raise AssertionError(f"unexpected Standard schema: {schema_name}")


class _TypedResearchStandardLLM:
    """Source-valid Research capability plus non-authoritative control (D10-K family)."""

    def __init__(self) -> None:
        self.schemas: list[str] = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema
        self.schemas.append(schema_name)
        if schema_name == "dima_standard_intent_draft_v1":
            return {
                "obligations": [
                    {
                        "obligation_id": "S_ROOT",
                        "capability_key": "root_cause",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["nedenini araştır"],
                        "semantic_surfaces": [
                            {"surface": "arıza sayısı", "kind_hint": "metric"},
                        ],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    }
                ],
                "control_requests": [
                    {
                        "request_id": "C1",
                        "category": "NON_AUTHORITATIVE_CONTROL_REQUEST",
                        "source_surfaces": ["Nedensel kesinlik iddia etme"],
                    }
                ],
            }
        raise AssertionError(
            f"typed-direct Research must stop Standard before schema: {schema_name}"
        )


class _StandardSemanticProvider:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        choices = []
        for request in requests:
            assert request.candidates
            candidate = next(
                (
                    item
                    for item in request.candidates
                    if item.label.casefold() == request.surface.casefold()
                ),
                request.candidates[0],
            )
            choices.append(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=candidate.candidate_id,
                )
            )
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _CurrentTurnRecoveryResearchLLM:
    """Preacceptance-only fixture for D10-N current-turn applicability."""

    def __init__(self) -> None:
        self.schemas: list[str] = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema
        self.schemas.append(schema_name)
        if schema_name == "dima_intent_draft_v1":
            return {
                "obligations": [
                    {
                        "obligation_id": "U_PERF",
                        "capability_key": "performance",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["arıza sayısı"],
                        "semantic_surfaces": [
                            {"surface": "arıza sayısı", "kind_hint": "metric"},
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                    {
                        "obligation_id": "U_ROOT",
                        "capability_key": "root_cause",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["gözlenen bozulma"],
                        "semantic_surfaces": [
                            {"surface": "gözlenen bozulma", "kind_hint": "metric"},
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                ],
                "research_directives": [],
                "control_requests": [],
            }
        if schema_name == "dima_intent_coverage_v1":
            return {"status": "PASS", "issues": []}
        raise AssertionError(f"preacceptance sentinel reached unexpected schema: {schema_name}")


class _RootResearchLLM:
    """Script only genuine bounded cognition decisions; never execution control."""

    def __init__(self) -> None:
        self.preacceptance_calls = 0
        self.manager_prompts: list[dict] = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, schema
        payload = json.loads(user)

        if schema_name == "dima_intent_draft_v1":
            self.preacceptance_calls += 1
            return {
                "obligations": [
                    {
                        "obligation_id": "U_ROOT",
                        "capability_key": "root_cause",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["arıza sayısı"],
                        "semantic_surfaces": [
                            {"surface": "arıza sayısı", "kind_hint": "metric"},
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    }
                ],
                "research_directives": [],
                "control_requests": [],
            }

        if schema_name == "dima_intent_coverage_v1":
            self.preacceptance_calls += 1
            return {"status": "PASS", "issues": []}

        if schema_name != "dima_research_manager_action_v1":
            raise AssertionError(f"unexpected Research schema: {schema_name}")

        self.manager_prompts.append(payload)
        evidence_refs = payload["EVIDENCE_REFS"]
        assert evidence_refs
        delta = payload["CURRENT_RESULT_DELTA"]
        assert delta is not None
        assert delta["verified"] is True
        assert delta["disclosed_in_current_prompt"] is True

        ledgers = payload["HYPOTHESIS_LEDGERS"]
        assert len(ledgers) == 1
        entries = ledgers[0]["entries"]

        if not entries:
            return {
                "action": "propose_hypothesis",
                "hypothesis_parent_obligation_id": "U_ROOT",
                # Deliberately contains an invented number. It may remain cognition/audit
                # material but must never surface in canonical Finding/Report prose.
                "hypothesis_statement": "Arıza sayısını bakım disiplini %27 artırdı.",
                "hypothesis_semantic_handles": ["h1"],
                "hypothesis_trigger_evidence_refs": [delta["evidence_ref"]],
                "hypothesis_limitations": [],
            }

        hypothesis = entries[0]
        if not hypothesis["next_test_task_refs"]:
            return {
                "action": "propose_hypothesis_next_test",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "next_test_task_kind": "QUERY",
                "next_test_input_handles": ["h1"],
                "next_test_trigger_evidence_ref": evidence_refs[0],
                "next_test_material_reason": (
                    "Aday açıklamayı ikinci governed metric ölçümüyle sınırla."
                ),
            }

        if not hypothesis["evidence_links"]:
            return {
                "action": "propose_hypothesis_evidence_relation",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "hypothesis_relation_evidence_ref": delta["evidence_ref"],
                "hypothesis_relation": "SUPPORTS",
            }

        raise AssertionError("deterministic completion should end before another Manager turn")


class _NarrationProviderFailure:
    def structured_json(self, *_args, **_kwargs):
        raise RuntimeError("provider-free deterministic narration fallback")


class _CapturingResearchLane(ResearchLaneService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_result = None

    def run(self, **kwargs):
        result = super().run(**kwargs)
        self.last_result = result
        return result


def _profile(role: ModelRole) -> ModelProfile:
    return ModelProfile(role=role, provider="provider-free", model="provider-free")


@pytest.mark.parametrize("standard_mode", ("omission_veto", "typed_direct"))
def test_product_root_cause_crosses_real_wren_and_finishes_bounded_investigation(
    wren,
    schema,
    monkeypatch,
    standard_mode,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())

    tenant_id = "day10-root-product"
    tenant_binding = f"id:{tenant_id}"
    principal = Principal(
        user_id="day10-root-user",
        tenant_id=tenant_id,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant_id,
        tenant_slug="demo-boyahane",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=wren.mdl_version,
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema_name") or schema.get("schema") or "public"),
        db_online=True,
    )
    service = _CountingWren(wren, schema)
    semantic_context = ContextProviderV0().build(service, runtime)

    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    context = ProductRequestContext(
        request_ref="r-day10-root-product",
        tenant_binding=tenant_binding,
        principal=principal,
        tenant_runtime=runtime,
        service=service,
        schema=schema,
        semantic_context=semantic_context,
        contract_store=contract_store,
        session_id="day10-root-session",
        thread_id="day10-root-thread",
    )

    manager = _RootResearchLLM()
    research_lane = _CapturingResearchLane(
        cognition=ResearchCognition(
            manager_llm=manager,
            manager_profile=_profile(ModelRole.RESEARCH_MANAGER),
            semantic_provider=None,
            semantic_profile=_profile(ModelRole.SEMANTIC_LINKER),
            temporal_provider=None,
            temporal_profile=_profile(ModelRole.TEMPORAL_NORMALIZER),
        )
    )
    standard_llm = (
        _OmittedResearchStandardLLM()
        if standard_mode == "omission_veto"
        else _TypedResearchStandardLLM()
    )
    standard_semantic = _StandardSemanticProvider()
    standard_lane = StandardLaneEngine(
        intent_structured=standard_llm.structured_json,
        coverage_structured=standard_llm.structured_json,
        semantic_provider=standard_semantic,
        temporal_provider=None,
    )
    coordinator = ProductCoordinator(
        standard_lane=standard_lane,
        standard_model_role="FAST_LANGUAGE",
        research_lane=research_lane,
        report_narrator=ReportNarrator(
            llm=_NarrationProviderFailure(),
            provider="provider-free",
            model="provider-free",
        ),
    )
    monkeypatch.setattr(
        coordinator,
        "_bind_context",
        lambda **_kwargs: context,
    )

    response = coordinator.handle(
        request=object(),
        body=ProductAskRequest(
            question=(
                "arıza sayısının nedenini araştır. Nedensel kesinlik iddia etme"
            ),
            session_id=context.session_id,
            thread_id=context.thread_id,
        ),
        principal=principal,
    )

    if standard_mode == "omission_veto":
        assert standard_llm.schemas == [
            "dima_standard_intent_draft_v1",
            "dima_standard_coverage_v1",
        ]
    else:
        assert standard_llm.schemas == ["dima_standard_intent_draft_v1"]
        assert standard_semantic.calls == 0
    accepted_family, _accepted_ref = standard_lane.authority_registry.accepted(
        context.turn_ref
    )
    assert accepted_family == AcceptedAuthorityFamily.RESEARCH
    assert response.lane == ProductLane.RESEARCH
    assert response.status == ProductStatus.REPORT, response.model_dump(mode="json")
    assert response.terminal_receipt.verified_complete is True
    assert response.report is not None
    assert response.report.report.sections

    result = research_lane.last_result
    assert result is not None
    root = next(
        item for item in result.ledger.items
        if item.obligation_id == "U_ROOT"
    )
    assert root.status == ObligationStatus.VERIFIED
    assert "nedensel doğruluk" in (root.verdict or "")

    assert len(result.evidence) == 2
    assert all(item.verified for item in result.evidence)
    assert service.query_calls == 2
    assert len(persisted) == 2
    assert all(row.sql and row.result_hash and row.provenance_json for row in persisted)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
    assert "%27" not in finding.statement
    assert finding.semantic_handle_refs
    assert any("nedenselliği doğrulamaz" in item for item in finding.limitations)

    report = response.report.report
    report_text = "\n".join(
        block.content
        for section in report.sections
        for block in section.blocks
    )
    assert "%27" not in report_text
    assert any(
        block.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
        for section in report.sections
        for block in section.blocks
    )
    assert not any(
        block.epistemic_label == EpistemicLabel.CONFIRMED_CAUSE
        for section in report.sections
        for block in section.blocks
    )

    kinds = [event.kind for event in response.events]
    assert ProductEventKind.RESEARCH_STARTED in kinds
    assert ProductEventKind.EVIDENCE_VERIFIED in kinds
    assert ProductEventKind.ROOT_CAUSE_CANDIDATE in kinds
    assert ProductEventKind.REPORT_READY in kinds
    assert kinds[-1] == ProductEventKind.TERMINAL

    # Two pre-acceptance cognition calls + three genuinely adaptive Manager decisions.
    assert manager.preacceptance_calls == 2
    assert len(manager.manager_prompts) == 3
    assert result.runtime.snapshot.preacceptance_turns == 2
    assert result.runtime.snapshot.research_manager_turns == 3
    assert result.runtime.snapshot.manager_turns == 5
    assert response.terminal_receipt.manager_turns == 5


def test_d10_n_real_wren_preacceptance_accepts_current_turn_metric_recovery(
    wren,
    schema,
):
    """Real catalog/Wren context; scripted cognition; no Product report or paid model."""
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    runtime_ctx = TenantAnalyticsRuntimeV0(
        tenant_id="day10-n-semantic",
        tenant_slug="day10-n-semantic",
        principal_user_id="day10-n",
        roles=("owner",),
        mdl_version=str(wren.mdl_version),
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema_name") or "public"),
        db_online=bool(schema.get("db_online", True)),
    )
    service = _CountingWren(wren, schema)
    semantic_context = ContextProviderV0().build(service, runtime_ctx)
    source_spans = SourceSpanRegistry()
    semantic_handles = SemanticHandleRegistry()
    semantic_provider = _StandardSemanticProvider()
    diagnostics = []

    semantic = ManagerSemanticResolutionAdapter(
        source_spans=source_spans,
        semantic_handles=semantic_handles,
        semantic_context=semantic_context,
        conversation=ConversationStateV2(),
        schema=schema,
        tenant_binding=f"id:{runtime_ctx.tenant_id}",
        session_id="d10-n-semantic",
        thread_id="d10-n-semantic",
        semantic_decision_provider=semantic_provider,
        semantic_diagnostic_sink=diagnostics.append,
    )
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
        ),
        core_analytics=object(),
        context=GovernedManagerExecutionContext(
            tenant_binding=f"id:{runtime_ctx.tenant_id}",
            context_version=semantic_context.context_version.version,
            principal=Principal(
                user_id="day10-n",
                tenant_id="day10-n-semantic",
                roles=["owner"],
                tenant_slug="day10-n-semantic",
            ),
            service=service,
            tenant_runtime=runtime_ctx,
            contract_store=contracts_module.ContractStore(),
            session_id="d10-n-semantic",
        ),
        semantic_resolution=semantic,
    )
    cognition = _CurrentTurnRecoveryResearchLLM()
    loop = ResearchManagerLoop(llm=cognition, source_spans=source_spans)
    manager_runtime = ManagerRuntime(
        request_ref="req-d10-n-semantic",
        turn_ref="turn-d10-n-semantic",
    )

    question = (
        "arıza sayısı ve gözlenen bozulma için kök neden araştırması yap"
    )
    outcome = loop.understand(
        question=question,
        message_id="turn-d10-n-semantic",
        request_ref="req-d10-n-semantic",
        runtime=manager_runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    assert outcome.clarification_required is False
    assert manager_runtime.accepted_contract is not None
    assert manager_runtime.ledger is not None
    assert {
        item.capability_key.value
        for item in manager_runtime.ledger.active_user_must
    } == {"performance", "root_cause"}
    assert cognition.schemas == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    assert service.query_calls == 0

    root_recovery = [
        item
        for item in diagnostics
        if item.get("owner_obligation_id") == "U_ROOT"
        and item.get("discovery_pass") == "current_turn_applicability"
    ]
    assert len(root_recovery) == 1
    assert root_recovery[0]["selection"]["status"] == "BOUND"
    assert root_recovery[0]["candidate_count"] >= 1
