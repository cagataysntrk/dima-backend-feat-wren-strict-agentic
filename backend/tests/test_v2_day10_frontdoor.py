"""Provider-free D10-A ownership and two-lane routing contracts."""

from __future__ import annotations

import ast
import inspect
from types import SimpleNamespace

from app.v2.manager_models import ManagerRunSnapshot, ManagerState
from app.v2.models import (
    AskV2Request,
    ContextVersionV0,
    BoundedSemanticContextV0,
    EvidenceArtifact,
    TenantAnalyticsRuntimeV0,
)
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_models import (
    ProductLane,
    ProductRequestContext,
    ProductStatus,
)
from app.v2.standard_lane import StandardLaneOutcome, StandardLaneStatus


class _Standard:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return self.outcome


class _Research:
    def __init__(self, result=None):
        self.result = result
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def _context(principal=None):
    return ProductRequestContext(
        request_ref="r-day10-frontdoor",
        tenant_binding="id:tenant-a",
        principal=principal or object(),
        tenant_runtime=TenantAnalyticsRuntimeV0(
            tenant_id="tenant-a",
            tenant_slug="tenant-a",
            principal_user_id="user-a",
            roles=("owner",),
            mdl_version="mdl-day10",
            catalog="catalog",
            schema_name="main",
            db_online=True,
        ),
        service=object(),
        schema={"cubes": []},
        semantic_context=BoundedSemanticContextV0(
            context_version=ContextVersionV0(
                version="ctx-day10",
                mdl_version="mdl-day10",
                compact_catalog_builder_version="test",
                business_rules_hash="0" * 64,
                prompt_context_policy_version="test",
            ),
        ),
        contract_store=object(),
        session_id="session-a",
        thread_id="thread-a",
    )


def _body():
    return AskV2Request(
        question="performansı incele",
        session_id="session-a",
        thread_id="thread-a",
    )


def _accepted_standard():
    evidence = EvidenceArtifact(
        artifact_id="evi_standard",
        task_id="standard:authority",
        obligation_ids=("U1",),
        query_contract_refs=("QC_STANDARD",),
        evidence_kind="standard_analytics",
        verified=True,
        payload={},
    )
    execution = SimpleNamespace(evidence=evidence, query_count=1)
    return StandardLaneOutcome(
        status=StandardLaneStatus.ACCEPTED,
        execution=execution,
        projection=SimpleNamespace(),
        authority=SimpleNamespace(),
    )


def _research_result():
    snapshot = ManagerRunSnapshot(
        run_id="mgr-day10",
        state=ManagerState.COMPLETED,
        terminal_status="VERIFIED_COMPLETE",
        manager_turns=3,
        tool_calls=2,
        data_queries=1,
        evidence_refs=("evi_research",),
    )
    evidence = EvidenceArtifact(
        artifact_id="evi_research",
        task_id="seed:U1",
        obligation_ids=("U1",),
        query_contract_refs=("QC_RESEARCH",),
        evidence_kind="standard_analytics",
        verified=True,
        payload={},
    )
    outcome = SimpleNamespace(
        clarification_required=False,
        verified_complete=True,
        terminal_status=SimpleNamespace(value="VERIFIED_COMPLETE"),
    )
    runtime = SimpleNamespace(snapshot=snapshot)
    return SimpleNamespace(
        outcome=outcome,
        verified_complete=True,
        runtime=runtime,
        evidence=(evidence,),
    )


def _coordinator(monkeypatch, *, standard_outcome, research_result=None, principal=None):
    standard = _Standard(standard_outcome)
    research = _Research(research_result)
    coordinator = ProductCoordinator(
        standard_lane=standard,
        standard_model_role="FAST_LANGUAGE",
        research_lane=research,
    )
    context = _context(principal)
    monkeypatch.setattr(
        coordinator,
        "_bind_context",
        lambda **_kwargs: context,
    )
    return coordinator, standard, research, context


def test_authoritative_frontdoor_import_graph_has_no_legacy_owner():
    import app.routers.ask_v2 as route
    import app.v2.product_coordinator as coordinator_module
    import app.v2.research_lane as research_module

    forbidden_modules = {
        "app.v2.orchestrator",
        "app.v2.resolver",
        "app.routers.ask",
        "app.cube_router",
    }
    for module in (route, coordinator_module, research_module):
        tree = ast.parse(inspect.getsource(module))
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        assert imported.isdisjoint(forbidden_modules)

    assert "ManagerLabHarness" not in inspect.getsource(research_module)
    assert "app.v2.manager_lab" not in inspect.getsource(research_module)


def test_standard_accepted_never_calls_research(monkeypatch):
    coordinator, standard, research, _ = _coordinator(
        monkeypatch,
        standard_outcome=_accepted_standard(),
    )

    response = coordinator.handle(
        request=object(),
        body=_body(),
        principal=object(),
    )

    assert response.lane == ProductLane.STANDARD
    assert response.status == ProductStatus.ANSWER
    assert response.evidence_refs[0].evidence_ref == "evi_standard"
    assert response.evidence_refs[0].verified is True
    assert len(standard.calls) == 1
    assert research.calls == []


def test_only_research_required_enters_research_with_raw_request_and_context(monkeypatch):
    poisoned_standard = StandardLaneOutcome(
        status=StandardLaneStatus.RESEARCH_REQUIRED,
        reasons=("research capability",),
    )
    coordinator, standard, research, context = _coordinator(
        monkeypatch,
        standard_outcome=poisoned_standard,
        research_result=_research_result(),
    )
    body = _body()

    response = coordinator.handle(
        request=object(),
        body=body,
        principal=context.principal,
    )

    assert response.lane == ProductLane.RESEARCH
    assert response.status == ProductStatus.PARTIAL
    assert len(research.calls) == 1
    call = research.calls[0]
    assert set(call) == {"context", "body"}
    assert call["context"] is context
    assert call["body"] is body
    assert response.evidence_refs[0].evidence_ref == "evi_research"
    # No Standard outcome/projection/obligations are accepted by the Research call seam.
    assert "standard" not in call
    assert "projection" not in call
    assert "obligations" not in call


def test_standard_nonresearch_terminals_never_silently_fallback(monkeypatch):
    cases = (
        (StandardLaneStatus.CLARIFICATION_REQUIRED, ProductStatus.CLARIFY),
        (StandardLaneStatus.UNSUPPORTED, ProductStatus.UNSUPPORTED),
        (StandardLaneStatus.COGNITION_REJECTED, ProductStatus.FAILED),
        (StandardLaneStatus.FAILED, ProductStatus.FAILED),
    )
    for lane_status, expected in cases:
        coordinator, _, research, _ = _coordinator(
            monkeypatch,
            standard_outcome=StandardLaneOutcome(
                status=lane_status,
                reasons=("typed terminal",),
            ),
        )
        response = coordinator.handle(
            request=object(),
            body=_body(),
            principal=object(),
        )
        assert response.status == expected
        assert response.lane == ProductLane.STANDARD
        assert research.calls == []


def test_research_preserves_frontdoor_principal_and_tenant_binding(monkeypatch):
    principal = object()
    coordinator, _, research, context = _coordinator(
        monkeypatch,
        standard_outcome=StandardLaneOutcome(
            status=StandardLaneStatus.RESEARCH_REQUIRED,
        ),
        research_result=_research_result(),
        principal=principal,
    )

    coordinator.handle(
        request=object(),
        body=_body(),
        principal=principal,
    )

    assert research.calls[0]["context"].principal is principal
    assert research.calls[0]["context"].tenant_binding == "id:tenant-a"
    assert research.calls[0]["context"].tenant_runtime.tenant_id == "tenant-a"
