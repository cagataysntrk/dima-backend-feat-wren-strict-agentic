"""D10-F deterministic ProductCoordinator -> real Wren -> report vertical.

Cognition is provider-free and scripted only at the probabilistic decision seams.
Analytical/numeric truth is real Wren/DuckDB and the production QueryContract/Evidence
path. The test enters through ProductCoordinator's authoritative two-lane boundary.
"""

from __future__ import annotations

import copy
import json

from app import contracts as contracts_module
from app import fanout
from app.wren_service import WrenService
from app.v2.context_provider import ContextProviderV0
from app.v2.model_policy import ModelProfile, ModelRole
from app.v2.models import TenantAnalyticsRuntimeV0
from app.v2.semantic_linker import (
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_models import (
    ProductAskRequest,
    ProductEventKind,
    ProductLane,
    ProductStatus,
)
from app.v2.report_narration import ReportNarrator
from app.v2.research_lane import ResearchCognition, ResearchLaneService
from app.v2.standard_lane import StandardLaneOutcome, StandardLaneStatus
from app.v2.product_models import ProductRequestContext
from control_plane.authorize import Principal


class _CertifiedService:
    """Proxy real Wren while exposing an exact-current fanout certificate."""

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


def _certified_schema(wren) -> dict:
    schema = copy.deepcopy(wren.schema())
    relationship = next(
        item
        for item in schema["relationships"]
        if item.get("name") == "makine_duruslari_makineler"
    )
    raw_mdl = json.loads(wren._mdl_bytes())
    physical = {
        model.get("name"): WrenService._physical_name(model)
        for model in raw_mdl.get("models", [])
        if model.get("name")
    }
    cert = fanout.certify(
        [relationship],
        fanout.konnektor_sorgu(wren),
        tablolar=set(physical),
        nitelikli=lambda name: physical.get(name, f"main.{name}"),
        mdl_version=wren.mdl_version,
    )
    proof = fanout.kanit(
        cert,
        relationship["name"],
        current_mdl_version=wren.mdl_version,
    )
    assert proof["status"] == "HEALTHY", proof
    relationship["certified"] = proof["certified"]
    relationship["fanout_proof"] = proof
    return schema


class _ForceResearchStandardLane:
    """Typed upstream disposition only; no Research semantic state crosses the seam."""

    def __init__(self) -> None:
        self.calls = 0
        self.authority_registry = None

    def bind_authority_registry(self, registry) -> None:
        self.authority_registry = registry

    def run(self, **_kwargs):
        self.calls += 1
        return StandardLaneOutcome(
            status=StandardLaneStatus.RESEARCH_REQUIRED,
            reasons=("relationship capability requires Research",),
        )


class _RelationshipResearchLLM:
    """Provider-free cognition reacting only to typed runtime state."""

    def __init__(self) -> None:
        self.manager_prompts: list[dict] = []

    def structured_json(self, system, user, *, schema, schema_name):
        del system, schema
        payload = json.loads(user)

        if schema_name == "dima_intent_draft_v1":
            return {
                "obligations": [
                    {
                        "obligation_id": "U_REL",
                        "capability_key": "relationship",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["toplam duruş", "bölüm"],
                        "semantic_surfaces": [
                            {"surface": "toplam duruş", "kind_hint": "metric"},
                            {"surface": "bölüm", "kind_hint": "dimension"},
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
            return {"status": "PASS", "issues": []}

        if schema_name != "dima_research_manager_action_v1":
            raise AssertionError(f"unexpected Research schema: {schema_name}")

        self.manager_prompts.append(payload)
        ledger = payload["OBLIGATION_LEDGER"]
        assert len(ledger) == 1
        handles = ledger[0]["semantic_handle_refs"]
        assert len(handles) == 2

        if not payload["EVIDENCE_REFS"]:
            return {
                "action": "run_relationship",
                "relationship_obligation_id": "U_REL",
                "focus_handles": [handles[0]],
                "counterpart_handles": [handles[1]],
            }

        delta = payload.get("CURRENT_RESULT_DELTA")
        if delta and not delta["inspected"]:
            return {
                "action": "inspect_evidence",
                "evidence_ref": delta["evidence_ref"],
            }

        return {"action": "finish"}


class _SharedCubeSemanticProvider:
    """Provider-free bounded cognition pinned to the fixture's governed target cube.

    The preferred cube label is derived from the real semantic context, not from user
    phrase matching. This test provider can only copy candidate IDs that the production
    bounded linker supplied.
    """

    def __init__(self, *, preferred_cube_label: str) -> None:
        self._preferred_cube_label = preferred_cube_label

    def decide(self, requests):
        choices = []
        for request in requests:
            matches = [
                candidate
                for candidate in request.candidates
                if self._preferred_cube_label in candidate.cube_labels
            ]
            assert len(matches) == 1, {
                "surface": request.surface,
                "preferred_cube_label": self._preferred_cube_label,
                "matches": [
                    {
                        "candidate_id": item.candidate_id,
                        "label": item.label,
                        "cube_labels": item.cube_labels,
                    }
                    for item in matches
                ],
                "candidates": [
                    {
                        "candidate_id": item.candidate_id,
                        "label": item.label,
                        "cube_labels": item.cube_labels,
                    }
                    for item in request.candidates
                ],
            }
            choices.append(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=matches[0].candidate_id,
                )
            )
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _NarrationProviderFailure:
    def structured_json(self, *_args, **_kwargs):
        raise RuntimeError("provider-free test uses deterministic narration fallback")


def test_product_research_relationship_crosses_real_wren_and_builds_report(
    wren,
    monkeypatch,
):
    schema = _certified_schema(wren)
    service = _CertifiedService(wren, schema)
    tenant_id = "day10-product-real"
    tenant_binding = f"id:{tenant_id}"
    principal = Principal(
        user_id="day10-real-user",
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
        schema_name=str(schema.get("schema_name") or "public"),
        db_online=True,
    )
    semantic_context = ContextProviderV0().build(service, runtime)
    relationship_cube = next(
        cube
        for cube in semantic_context.cubes
        if cube.canonical_name == "makine_duruslari"
    )
    relationship_cube_label = relationship_cube.display or relationship_cube.canonical_name

    persisted = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted.append(row),
    )
    contract_store = contracts_module.ContractStore()

    context = ProductRequestContext(
        request_ref="r-day10-real-product",
        tenant_binding=tenant_binding,
        principal=principal,
        tenant_runtime=runtime,
        service=service,
        schema=schema,
        semantic_context=semantic_context,
        contract_store=contract_store,
        session_id="day10-real-session",
        thread_id="day10-real-thread",
    )

    manager = _RelationshipResearchLLM()
    profile = ModelProfile(
        role=ModelRole.RESEARCH_MANAGER,
        provider="provider-free",
        model="provider-free",
    )
    cognition = ResearchCognition(
        manager_llm=manager,
        manager_profile=profile,
        semantic_provider=_SharedCubeSemanticProvider(
            preferred_cube_label=relationship_cube_label
        ),
        semantic_profile=ModelProfile(
            role=ModelRole.SEMANTIC_LINKER,
            provider="provider-free",
            model="provider-free",
        ),
        temporal_provider=None,
        temporal_profile=ModelProfile(
            role=ModelRole.TEMPORAL_NORMALIZER,
            provider="provider-free",
            model="provider-free",
        ),
    )
    research_lane = ResearchLaneService(cognition=cognition)
    standard_lane = _ForceResearchStandardLane()
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
            question="toplam duruş ile bölüm ilişkisini incele",
            session_id=context.session_id,
            thread_id=context.thread_id,
        ),
        principal=principal,
    )

    assert standard_lane.calls == 1
    assert response.lane == ProductLane.RESEARCH
    assert response.status == ProductStatus.REPORT, response.model_dump(mode="json")
    assert response.terminal_receipt.verified_complete is True
    assert response.report is not None
    assert response.report.version == 1
    assert response.report.report.sections
    assert response.evidence_refs
    assert all(item.verified for item in response.evidence_refs)
    assert response.artifact_refs
    assert response.section_continuations

    kinds = [event.kind for event in response.events]
    assert ProductEventKind.RESEARCH_STARTED in kinds
    assert ProductEventKind.EVIDENCE_VERIFIED in kinds
    assert ProductEventKind.RELATIONSHIP_CHECKED in kinds
    assert ProductEventKind.ARTIFACT_READY in kinds
    assert ProductEventKind.REPORT_READY in kinds
    assert kinds[-1] == ProductEventKind.TERMINAL

    assert service.query_calls == 1
    assert len(persisted) == 1
    assert persisted[0].sql
    assert persisted[0].result_hash
    assert persisted[0].provenance_json

    evidence = response.evidence_refs[0]
    assert evidence.evidence_kind == "relationship_analytics"
    assert evidence.query_contract_refs
    report = response.report.report
    assert any(
        "ilişki analizi" in block.content.lower()
        for section in report.sections
        for block in section.blocks
    )
    assert not any(
        "kesin neden" in block.content.lower()
        for section in report.sections
        for block in section.blocks
    )

    # Fully-bound DIRECT USER_MUST execution is deterministic scheduling work.
    # No Manager cognition turn is spent saying run/inspect/finish for this simple case.
    assert len(manager.manager_prompts) == 0
