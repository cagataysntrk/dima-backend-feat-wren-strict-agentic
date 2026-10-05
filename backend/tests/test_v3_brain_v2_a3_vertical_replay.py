from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.brain_v2.material_groups import (
    project_material_groups,
    result_dependency_execution_anchor,
    select_pending_material_group,
)
from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    RuntimeIdentity,
)
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_analytical_scope import (
    NativeMaterialBinding,
    analytical_scope_contract,
)
from app.v3.research_contracts import ResearchBrief
from app.v3.research_material_coverage import assert_material_result_coverage
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_result_dependency import resolve_first_ranked_entity
from app.v3.research_store import ResearchSessionStore
from control_plane.authorize import Principal


FIXTURE = Path(__file__).with_name("fixtures") / "a3_37237863865_vertical_replay.json"
ENGINE_SHA = "4c49b8da6b424b0fa4d8ef340ca1b238d12980c1"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
RUNTIME_TAG = "v0.63.18-dima.11.1.1"
DIGEST = "sha256:0ff1e378b532cc986d871ed3945e677a7a6d0bfb28686b344dfa4ec8d397327d"
BUILD = f"github-actions:37176179588:{ENGINE_SHA}"
STAMP = datetime(2026, 10, 4, 21, 56, tzinfo=timezone.utc)


def _fixture() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert value["source_run_id"] == 37237863865
    assert value["source_artifact_id"] == 11315439520
    assert value["current_replay_product_sha"] == (
        "957fea9876cfa4cdf8ee3a4f5701c0b6cfc2a40e"
    )
    assert value["engine_sha"] == ENGINE_SHA
    return value


def _engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _principal() -> Principal:
    return Principal(
        user_id="00000000-0000-4000-8000-000000000901",
        tenant_id="00000000-0000-4000-8000-000000000902",
        roles=["analyst"],
        tenant_slug="a3-vertical-replay",
    )


def _runtime() -> RuntimeIdentity:
    return RuntimeIdentity(
        substrate="metabase-native",
        runtime_version=RUNTIME_TAG,
        image_digest=DIGEST,
        database_id="metabase:1",
        repository="UpcyTech/dima-metabase-engine",
        revision_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=RUNTIME_TAG,
        build_identity=BUILD,
        image_identity=DIGEST,
        runtime_instance_id=UUID("00000000-0000-4000-8000-000000000911"),
    )


def _admit(
    *,
    session,
    obligation_id: str,
    occurrence: dict,
    result_payload: dict,
    coverage,
    conversation_suffix: int,
):
    result = ExecutionResultSnapshot(
        payload=result_payload,
        row_count=len(result_payload["data"]["rows"]),
    )
    contract = analytical_scope_contract(
        session=session,
        obligation_id=obligation_id,
    )
    receipt = DimaQueryReceiptSealer.seal_research_execution(
        authority_id=session.authority_id,
        research_session_id=session.session_id,
        obligation_ids=(obligation_id,),
        tenant_binding=session.tenant_binding,
        principal_subject=session.principal_subject,
        roles=("analyst",),
        native_subject_ref="metabase-user:7",
        native_conversation_id=UUID(
            f"00000000-0000-4000-8000-{conversation_suffix:012d}"
        ),
        native_query_id=occurrence["native_query_id"],
        native_query_provenance_ref=(
            f"artifact:{37237863865}:{occurrence['execution_link_id']}:query"
        ),
        native_result_provenance_ref=(
            f"artifact:{37237863865}:{occurrence['execution_link_id']}:result"
        ),
        query_fingerprint=occurrence["query_fingerprint"],
        semantic_context_version=session.context_version,
        scope_fingerprint=contract.scope_fingerprint,
        runtime=_runtime(),
        result=result,
        event=ExecutionEventIdentity(
            execution_id=f"artifact-replay:{occurrence['execution_link_id']}",
            executed_at=STAMP,
        ),
    )
    evidence = EvidenceArtifact(
        artifact_id=(
            "evi_"
            + hashlib.sha256(receipt.receipt_id.encode("utf-8")).hexdigest()[:24]
        ),
        authority_id=receipt.authority_id,
        obligation_ids=(obligation_id,),
        query_receipt_refs=(receipt.receipt_id,),
        evidence_kind="p14_native_research_material_replay",
        state=EvidenceState.VERIFIED,
        payload={
            "source_run_id": 37237863865,
            "source_artifact_id": 11315439520,
            "result_hash": result.result_hash,
            "result_coverage": coverage.model_dump(mode="json"),
        },
    )
    updated = ResearchManager.admit_receipted_evidence(
        session,
        obligation_id=obligation_id,
        receipt=receipt,
        evidence=evidence,
        satisfies_obligation=True,
    )
    return updated, receipt, evidence


def test_a3_frozen_artifact_replays_through_evidence_dependency_and_child_readiness():
    frozen = _fixture()
    brief = ResearchBrief.model_validate(frozen["accepted_brief"])
    ranking_id = frozen["ranking_occurrence"]["obligation_id"]
    child_id = frozen["expected"]["child_obligation_id"]
    comparison_id = frozen["comparison_occurrence"]["obligation_id"]

    store = ResearchSessionStore(_engine())
    product = ResearchAskOrchestrator(store=store)
    session = product.start_from_brief(
        brief=brief,
        request_ref="a3-37237863865-vertical-replay",
        source_message_hash=hashlib.sha256(
            b"a3 frozen artifact 37237863865"
        ).hexdigest(),
        principal=_principal(),
    )

    time_binding = {
        "dimension.event_date": NativeMaterialBinding(
            candidate_id="dimension.event_date",
            candidate_kind="dimension",
            database_id=1,
            table_id=1,
            field_id=1,
        )
    }

    comparison_result = {
        "data": {
            "cols": [
                {
                    "id": 1,
                    "table_id": 1,
                    "display_name": "Event Date: Month",
                    "field_ref": ["field", 1, {"temporal-unit": "month"}],
                },
                {
                    "display_name": "Machine Downtime Minutes",
                    "field_ref": ["aggregation", 0],
                },
            ],
            "rows": frozen["comparison_occurrence"]["rows"],
        },
        "database_id": 1,
        "row_count": 2,
        "status": "completed",
    }
    comparison_contract = analytical_scope_contract(
        session=session,
        obligation_id=comparison_id,
    )
    comparison_coverage = assert_material_result_coverage(
        contract=comparison_contract,
        result_payload=comparison_result,
        bindings=time_binding,
        attested_native_material=True,
    )
    session, comparison_receipt, comparison_evidence = _admit(
        session=session,
        obligation_id=comparison_id,
        occurrence=frozen["comparison_occurrence"],
        result_payload=comparison_result,
        coverage=comparison_coverage,
        conversation_suffix=912,
    )
    assert frozen["comparison_occurrence"]["status"] == "VERIFIED"
    assert comparison_receipt.receipt_id
    assert comparison_evidence.artifact_id
    assert (
        ResearchManager.obligation(session, comparison_id).state
        == ObligationState.VERIFIED
    )

    ranking_result = frozen["ranking_occurrence"]["result_payload"]
    assert ranking_result["data"]["rows"] == [
        ["Assembly", 267.0],
        ["Packaging", 74.0],
        ["Utilities", 34.0],
        ["Maintenance", 18.0],
        ["Quality", 8.0],
    ]
    ranking_contract = analytical_scope_contract(
        session=session,
        obligation_id=ranking_id,
    )
    ranking_coverage = assert_material_result_coverage(
        contract=ranking_contract,
        result_payload=ranking_result,
        bindings=time_binding,
        attested_native_material=True,
    )
    assert ranking_coverage.status == "FULL"
    assert ranking_coverage.time_field_id is None

    session, ranking_receipt, ranking_evidence = _admit(
        session=session,
        obligation_id=ranking_id,
        occurrence=frozen["ranking_occurrence"],
        result_payload=ranking_result,
        coverage=ranking_coverage,
        conversation_suffix=913,
    )

    assert ranking_receipt.receipt_id is not None
    assert ranking_evidence.artifact_id is not None
    assert (
        ResearchManager.obligation(session, ranking_id).state
        == ObligationState.VERIFIED
    )

    child_contract = analytical_scope_contract(
        session=session,
        obligation_id=child_id,
    )
    resolution = resolve_first_ranked_entity(
        base_contract=child_contract,
        source_goal_id=ranking_id,
        source_execution_obligation_id=ranking_id,
        source_evidence_id=ranking_evidence.artifact_id,
        source_receipt_id=ranking_receipt.receipt_id,
        source_result_hash=ranking_receipt.result_hash,
        dimension_semantic_id=(
            frozen["expected"]["dependency_dimension_semantic_id"]
        ),
        native_field_id=2,
        parent_result=ranking_result,
        dimension_name="Department",
    )
    assert resolution.selected_value == frozen["expected"]["selected_entity"]
    assert resolution.selected_value == "Assembly"
    assert resolution.contract.scope_identity == child_contract.scope_identity
    assert resolution.contract.scope_fingerprint == child_contract.scope_fingerprint
    assert resolution.contract.filters[-1].source_candidate_id == (
        "dimension.department"
    )
    assert resolution.contract.filters[-1].value == "Assembly"

    groups = project_material_groups(session)
    by_requirement = {
        requirement_id: group
        for group in groups
        for requirement_id in group.consumer_requirement_ids
    }
    comparison_group = by_requirement[comparison_id]
    ranking_group = by_requirement[ranking_id]
    child_group = by_requirement[child_id]

    assert child_group.dependency_requirement_ids == (ranking_id,)
    assert (
        result_dependency_execution_anchor(
            session=session,
            groups=groups,
            requirement_id=child_id,
        )
        == ranking_group.anchor_requirement_id
    )

    next_group = select_pending_material_group(
        groups,
        completed_material_group_ids=(
            comparison_group.material_group_id,
            ranking_group.material_group_id,
        ),
    )
    assert next_group is not None
    assert next_group.material_group_id == child_group.material_group_id
    assert child_id in next_group.consumer_requirement_ids
