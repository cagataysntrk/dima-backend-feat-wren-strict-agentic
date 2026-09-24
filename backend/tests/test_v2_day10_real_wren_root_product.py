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
from app.v2.manager_core_adapter import ManagerCoreAnalyticsAdapter
from app.v2.manager_executor import GovernedManagerExecutionContext, GovernedManagerExecutor
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_runtime import ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_models import ObligationStatus
from app.v2.manager_tools import ManagerToolCall, ManagerToolName
from app.v2.model_policy import ModelProfile, ModelRole
from app.v2.models import ConversationStateV2, EpistemicLabel, TenantAnalyticsRuntimeV0
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
from app.v2.research_tasks import ResearchTaskRegistry
from app.v2.research_tools import ResearchToolRunner, ResearchTaskKind
from app.v2.root_cause_orchestration import (
    RootCauseBootstrapPolicy,
    RootCauseBootstrapStatus,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    SemanticDecompositionRepairBatchDecision,
    SemanticDecompositionRepairChoice,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
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


class _CautiousSemanticProvider:
    """Provider-free stand-in for baseline abstain -> narrowed contextual selection."""

    def __init__(self) -> None:
        self.calls = 0
        self._surface_attempts = {}

    def decide(self, requests):
        self.calls += 1
        choices = []
        for request in requests:
            attempt = self._surface_attempts.get(request.surface, 0) + 1
            self._surface_attempts[request.surface] = attempt
            if len(request.candidates) == 1:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=request.candidates[0].candidate_id,
                    )
                )
                continue

            contextual = next(
                (
                    item
                    for item in request.candidates
                    if attempt >= 2
                    and "arıza say" in item.label.casefold()
                    and "gözlenen bozulma" in request.source_context.casefold()
                ),
                None,
            )
            if contextual is not None:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=contextual.candidate_id,
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
    semantic_provider = _CautiousSemanticProvider()
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

    bakim_context = next(
        item for item in semantic_context.cubes
        if item.canonical_name == "bakim"
    )
    other_metric_label = next(
        (
            value
            for field in bakim_context.measures
            for value in (field.display, *field.synonyms)
            if value and "arıza say" not in value.casefold()
        ),
        None,
    )
    assert other_metric_label is not None
    question = (
        f"{other_metric_label} yalnız bağlam bilgisidir; "
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


class _AlwaysAbstainNonExactSemanticProvider:
    """Exact matches remain deterministic; every non-exact cognition call abstains."""

    def __init__(self) -> None:
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        return SemanticLinkBatchDecision(
            choices=tuple(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="ABSTAIN",
                    reason="NO_MATCH",
                )
                for request in requests
            )
        )


class _SelectCurrentMetricSourcesRepairProvider:
    def __init__(self, surfaces) -> None:
        self._surfaces = set(surfaces)
        self.calls = []

    def decide(self, requests, *, user_message):
        self.calls.append((requests, user_message))
        choices = []
        for request in requests:
            selected = tuple(
                item.source_token
                for item in request.available_user_source_concepts
                if item.surface in self._surfaces
            )
            choices.append(
                SemanticDecompositionRepairChoice(
                    gap_ref=request.gap_ref,
                    decision=("SELECT_SOURCES" if selected else "ABSTAIN"),
                    selected_source_tokens=selected,
                    reason=(
                        "SOURCE_SUPPORTS_SCOPE"
                        if selected
                        else "INSUFFICIENT_SOURCE_SUPPORT"
                    ),
                )
            )
        return SemanticDecompositionRepairBatchDecision(choices=tuple(choices))


class _D10PRepairResearchLLM:
    def __init__(self, *, metric_a: str, metric_b: str, dimension: str) -> None:
        self.metric_a = metric_a
        self.metric_b = metric_b
        self.dimension = dimension
        self.schemas = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema
        self.schemas.append(schema_name)
        if schema_name == "dima_intent_draft_v1":
            return {
                "obligations": [
                    {
                        "obligation_id": "U_METRIC_A",
                        "capability_key": "performance",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": [self.metric_a],
                        "semantic_surfaces": [
                            {"surface": self.metric_a, "kind_hint": "metric"}
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                    {
                        "obligation_id": "U_METRIC_B",
                        "capability_key": "performance",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": [self.metric_b],
                        "semantic_surfaces": [
                            {"surface": self.metric_b, "kind_hint": "metric"}
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                    {
                        "obligation_id": "U_BREAKDOWN",
                        "capability_key": "breakdown",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": [
                            f"{self.dimension} bazındaki performansı"
                        ],
                        "semantic_surfaces": [
                            {"surface": self.dimension, "kind_hint": "dimension"},
                            {"surface": "performansı", "kind_hint": "metric"},
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
        raise AssertionError(f"unexpected D10-P preacceptance schema: {schema_name}")


def _field_surface(field):
    return next(
        value
        for value in (field.display, *field.synonyms)
        if value
    )


def test_d10_p_real_wren_preacceptance_repairs_decomposition_with_fresh_owner_handles(
    wren,
    schema,
):
    """Real governed catalog; scripted cognition; zero paid/provider calls."""
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert len(tuple(cube.get("measures") or ())) >= 2

    runtime_ctx = TenantAnalyticsRuntimeV0(
        tenant_id="day10-p-semantic",
        tenant_slug="day10-p-semantic",
        principal_user_id="day10-p",
        roles=("owner",),
        mdl_version=str(wren.mdl_version),
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema_name") or "public"),
        db_online=bool(schema.get("db_online", True)),
    )
    service = _CountingWren(wren, schema)
    semantic_context = ContextProviderV0().build(service, runtime_ctx)
    bakim_context = next(
        item for item in semantic_context.cubes
        if item.canonical_name == "bakim"
    )
    assert len(bakim_context.measures) >= 2
    assert bakim_context.dimensions

    metric_a = _field_surface(bakim_context.measures[0])
    metric_b = _field_surface(bakim_context.measures[1])
    dimension = _field_surface(bakim_context.dimensions[0])
    assert metric_a != metric_b

    question = (
        f"{metric_a}, {metric_b} ve {dimension} bazındaki performansı araştır"
    )
    source_spans = SourceSpanRegistry()
    semantic_handles = SemanticHandleRegistry()
    semantic_provider = _AlwaysAbstainNonExactSemanticProvider()
    repair_provider = _SelectCurrentMetricSourcesRepairProvider(
        (metric_a, metric_b)
    )
    diagnostics = []

    semantic = ManagerSemanticResolutionAdapter(
        source_spans=source_spans,
        semantic_handles=semantic_handles,
        semantic_context=semantic_context,
        conversation=ConversationStateV2(),
        schema=schema,
        tenant_binding=f"id:{runtime_ctx.tenant_id}",
        session_id="d10-p-semantic",
        thread_id="d10-p-semantic",
        semantic_decision_provider=semantic_provider,
        semantic_decomposition_repair_provider=repair_provider,
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
                user_id="day10-p",
                tenant_id="day10-p-semantic",
                roles=["owner"],
                tenant_slug="day10-p-semantic",
            ),
            service=service,
            tenant_runtime=runtime_ctx,
            contract_store=contracts_module.ContractStore(),
            session_id="d10-p-semantic",
        ),
        semantic_resolution=semantic,
    )
    cognition = _D10PRepairResearchLLM(
        metric_a=metric_a,
        metric_b=metric_b,
        dimension=dimension,
    )
    loop = ResearchManagerLoop(llm=cognition, source_spans=source_spans)
    manager_runtime = ManagerRuntime(
        request_ref="req-d10-p-semantic",
        turn_ref="turn-d10-p-semantic",
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-semantic",
        request_ref="req-d10-p-semantic",
        runtime=manager_runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    assert outcome.clarification_required is False
    assert manager_runtime.accepted_contract is not None
    assert manager_runtime.ledger is not None
    assert manager_runtime.snapshot.preacceptance_turns == 2
    assert manager_runtime.snapshot.manager_turns == 2
    assert cognition.schemas == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    assert len(repair_provider.calls) == 1
    assert service.query_calls == 0

    repair_requests, repair_message = repair_provider.calls[0]
    assert repair_message == question
    assert len(repair_requests) == 1
    request = repair_requests[0]
    assert request.obligation_id == "U_BREAKDOWN"
    assert request.missing_kind == "metric"
    assert {
        item.surface
        for item in request.available_user_source_concepts
    } == {metric_a, metric_b}

    items = {
        item.obligation_id: item
        for item in manager_runtime.ledger.items
    }
    a_handle_id = next(
        ref
        for ref in items["U_METRIC_A"].semantic_handle_refs
        if semantic_handles.validate(
            ref,
            tenant_binding=f"id:{runtime_ctx.tenant_id}",
            context_version=semantic_context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    )
    b_handle_id = next(
        ref
        for ref in items["U_METRIC_B"].semantic_handle_refs
        if semantic_handles.validate(
            ref,
            tenant_binding=f"id:{runtime_ctx.tenant_id}",
            context_version=semantic_context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    )
    breakdown_metrics = [
        ref
        for ref in items["U_BREAKDOWN"].semantic_handle_refs
        if semantic_handles.validate(
            ref,
            tenant_binding=f"id:{runtime_ctx.tenant_id}",
            context_version=semantic_context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    ]
    assert len(breakdown_metrics) == 2
    assert set(breakdown_metrics).isdisjoint({a_handle_id, b_handle_id})

    original = [
        semantic_handles.validate(
            ref,
            tenant_binding=f"id:{runtime_ctx.tenant_id}",
            context_version=semantic_context.context_version.version,
        )
        for ref in (a_handle_id, b_handle_id)
    ]
    repaired = [
        semantic_handles.validate(
            ref,
            tenant_binding=f"id:{runtime_ctx.tenant_id}",
            context_version=semantic_context.context_version.version,
        )
        for ref in breakdown_metrics
    ]
    assert {item.parent_obligation_id for item in original} == {
        "U_METRIC_A",
        "U_METRIC_B",
    }
    assert {item.parent_obligation_id for item in repaired} == {"U_BREAKDOWN"}
    assert {item.resolver_provenance_id for item in repaired} == {
        item.resolver_provenance_id for item in original
    }
    assert any(
        item.get("kind") == "semantic_decomposition_repair"
        for item in diagnostics
    )


class _SelectFirstScopeGroupRepairProvider:
    def __init__(self) -> None:
        self.calls = []

    def decide(self, requests, *, user_message):
        self.calls.append((requests, user_message))
        choices = []
        for request in requests:
            groups = tuple(request.available_scope_groups)
            choices.append(
                SemanticDecompositionRepairChoice(
                    gap_ref=request.gap_ref,
                    decision=("SELECT_SCOPE_GROUP" if groups else "ABSTAIN"),
                    selected_source_tokens=(),
                    selected_group_token=(
                        groups[0].group_token if groups else None
                    ),
                    reason=(
                        "SOURCE_SUPPORTS_SCOPE"
                        if groups
                        else "INSUFFICIENT_SOURCE_SUPPORT"
                    ),
                )
            )
        return SemanticDecompositionRepairBatchDecision(choices=tuple(choices))


class _D10QMultiMetricRootLLM:
    def __init__(self, *, metric_a: str, metric_b: str) -> None:
        self.metric_a = metric_a
        self.metric_b = metric_b
        self.schemas = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, user, schema
        self.schemas.append(schema_name)
        if schema_name == "dima_intent_draft_v1":
            return {
                "obligations": [
                    {
                        "obligation_id": "U_SCOPE",
                        "capability_key": "performance",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": [
                            f"{self.metric_a} ve {self.metric_b} birlikte"
                        ],
                        "semantic_surfaces": [
                            {"surface": self.metric_a, "kind_hint": "metric"},
                            {"surface": self.metric_b, "kind_hint": "metric"},
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
                        "source_surfaces": [
                            "gözlenen bozulmanın kök nedenlerini sınırla"
                        ],
                        "semantic_surfaces": [
                            {"surface": "gözlenen bozulma", "kind_hint": "metric"}
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
        raise AssertionError(f"unexpected D10-Q schema: {schema_name}")


def test_d10_q_real_wren_joint_root_scope_executes_both_metrics_into_verified_evidence(
    wren,
    schema,
    monkeypatch,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert len(tuple(cube.get("measures") or ())) >= 2

    tenant = "day10-q-multi-root"
    runtime_ctx = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="demo-boyahane",
        principal_user_id="day10-q",
        roles=("owner",),
        mdl_version=str(wren.mdl_version),
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema_name") or "public"),
        db_online=bool(schema.get("db_online", True)),
    )
    service = _CountingWren(wren, schema)
    semantic_context = ContextProviderV0().build(service, runtime_ctx)
    bakim_context = next(
        item for item in semantic_context.cubes
        if item.canonical_name == "bakim"
    )
    metric_a = _field_surface(bakim_context.measures[0])
    metric_b = _field_surface(bakim_context.measures[1])
    assert metric_a != metric_b

    question = (
        f"{metric_a} ve {metric_b} birlikte değerlendirilsin; "
        "gözlenen bozulmanın kök nedenlerini sınırla"
    )
    source_spans = SourceSpanRegistry()
    semantic_handles = SemanticHandleRegistry()
    repair = _SelectFirstScopeGroupRepairProvider()
    diagnostics = []
    principal = Principal(
        user_id="day10-q",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    semantic = ManagerSemanticResolutionAdapter(
        source_spans=source_spans,
        semantic_handles=semantic_handles,
        semantic_context=semantic_context,
        conversation=ConversationStateV2(),
        schema=schema,
        tenant_binding=f"id:{tenant}",
        session_id="d10-q-multi-root",
        thread_id="d10-q-multi-root",
        semantic_decision_provider=_AlwaysAbstainNonExactSemanticProvider(),
        semantic_decomposition_repair_provider=repair,
        semantic_diagnostic_sink=diagnostics.append,
    )
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=source_spans,
            semantic_handles=semantic_handles,
        ),
        core_analytics=ManagerCoreAnalyticsAdapter(
            semantic_handles=semantic_handles,
        ),
        context=GovernedManagerExecutionContext(
            tenant_binding=f"id:{tenant}",
            context_version=semantic_context.context_version.version,
            principal=principal,
            service=service,
            tenant_runtime=runtime_ctx,
            contract_store=contract_store,
            session_id="d10-q-multi-root",
        ),
        semantic_resolution=semantic,
    )
    cognition = _D10QMultiMetricRootLLM(
        metric_a=metric_a,
        metric_b=metric_b,
    )
    loop = ResearchManagerLoop(llm=cognition, source_spans=source_spans)
    runtime = ManagerRuntime(
        request_ref="req-d10-q-multi-root",
        turn_ref="turn-d10-q-multi-root",
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-q-multi-root",
        request_ref="req-d10-q-multi-root",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )
    assert outcome.accepted is True
    assert runtime.accepted_contract is not None
    assert runtime.ledger is not None
    assert runtime.snapshot.preacceptance_turns == 2
    assert cognition.schemas == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    assert len(repair.calls) == 1
    request = repair.calls[0][0][0]
    assert request.obligation_id == "U_ROOT"
    assert len(request.available_scope_groups) == 1
    assert len(request.available_scope_groups[0].member_source_tokens) == 2

    items = {item.obligation_id: item for item in runtime.ledger.items}
    scope_metric_handles = tuple(
        ref
        for ref in items["U_SCOPE"].semantic_handle_refs
        if semantic_handles.validate(
            ref,
            tenant_binding=f"id:{tenant}",
            context_version=semantic_context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    )
    root_metric_handles = tuple(
        ref
        for ref in items["U_ROOT"].semantic_handle_refs
        if semantic_handles.validate(
            ref,
            tenant_binding=f"id:{tenant}",
            context_version=semantic_context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    )
    assert len(scope_metric_handles) == 2
    assert len(root_metric_handles) == 2
    assert set(root_metric_handles).isdisjoint(scope_metric_handles)
    assert {
        semantic_handles.validate(
            ref,
            tenant_binding=f"id:{tenant}",
            context_version=semantic_context.context_version.version,
        ).resolver_provenance_id
        for ref in root_metric_handles
    } == {
        semantic_handles.validate(
            ref,
            tenant_binding=f"id:{tenant}",
            context_version=semantic_context.context_version.version,
        ).resolver_provenance_id
        for ref in scope_metric_handles
    }

    registry = ResearchTaskRegistry()
    bootstrap = RootCauseBootstrapPolicy(
        semantic_handles=semantic_handles,
    ).prepare(
        runtime=runtime,
        evidence_store=executor.evidence_store,
        task_registry=registry,
        root_obligation_id="U_ROOT",
        tenant_binding=f"id:{tenant}",
        context_version=semantic_context.context_version.version,
    )
    assert bootstrap.status == RootCauseBootstrapStatus.TASK_READY
    assert bootstrap.selected_capability.value == "performance"
    assert bootstrap.task is not None
    assert bootstrap.task.task_kind == ResearchTaskKind.QUERY.value
    assert bootstrap.task.input_refs == root_metric_handles

    before = service.query_calls
    result = ResearchToolRunner().execute(
        task=bootstrap.task,
        tool_id=ResearchToolRunner().tool_id_for_task(bootstrap.task),
        call=ManagerToolCall(
            name=ManagerToolName.RUN_ANALYTICS,
            args={
                "obligation_ids": ("U_ROOT",),
                "metric_handles": root_metric_handles,
            },
        ),
        runtime=runtime,
        executor=executor,
        principal=principal,
        task_registry=registry,
    )
    assert service.query_calls > before
    assert result.evidence.verified is True
    assert result.evidence.query_contract_refs
    assert persisted
    expected_metric_names = {
        semantic_handles.binding_for_execution(
            ref,
            tenant_binding=f"id:{tenant}",
            context_version=semantic_context.context_version.version,
        ).canonical_target.canonical_name
        for ref in root_metric_handles
    }
    contract_ir = [
        json.loads(row.provenance_json)["v2_manager"]["analytics_ir"]
        for row in persisted
        if row.provenance_json
    ]
    assert contract_ir
    assert all(
        {item["canonical_name"] for item in snapshot["metrics"]}
        == expected_metric_names
        for snapshot in contract_ir
    )
    assert all(len(snapshot["metrics"]) == 2 for snapshot in contract_ir)
    assert any(
        item.get("kind") == "semantic_decomposition_repair"
        for item in diagnostics
    )
