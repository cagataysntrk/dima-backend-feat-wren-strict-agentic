from __future__ import annotations

import json
from pathlib import Path

from app.v3.product.capabilities import capability_discovery
from app.v3.product.contracts import CapabilityStatus
from control_plane.authorize import Principal


ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "eval" / "v1" / "brain_v2_phase2_headless_manifest.json"


def _principal() -> Principal:
    return Principal(
        user_id="00000000-0000-4000-8000-000000009801",
        tenant_id="00000000-0000-4000-8000-000000009802",
        tenant_slug="phase2-headless",
        roles=["analyst"],
    )


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_phase2_manifest_is_exact_t1_t7_headless_panel():
    manifest=_manifest()
    assert manifest["schema_version"]=="dima_brain_v2_phase2_headless_v1"
    assert manifest["authority"]=="EVAL_ONLY"
    assert manifest["phase1_status"]=="ACCEPTED_CARRY_FORWARD"
    assert manifest["frontend"]=="NOT_IMPLEMENTED"
    assert manifest["thirty_case"]=="NOT_RUN"
    assert [item["id"] for item in manifest["capabilities"]]==[
        "T1","T2","T3","T4","T5","T6","T7"
    ]
    assert manifest["metamorphic_required"]==[
        "T1","T2","T3","T5","T6","T7"
    ]


def test_phase2_manifest_proof_references_exist_exactly():
    for capability in _manifest()["capabilities"]:
        assert capability["proofs"], capability["id"]
        for proof in capability["proofs"]:
            raw_path,test_name=proof.split("::",1)
            path=ROOT / raw_path.removeprefix("backend/")
            assert path.exists(), proof
            source=path.read_text(encoding="utf-8")
            assert f"def {test_name}(" in source, proof


def test_phase2_capability_catalog_matches_manifest():
    manifest=_manifest()
    hot=capability_discovery(
        principal=_principal(),
        analytical_context_available=True,
    )
    cold=capability_discovery(
        principal=_principal(),
        analytical_context_available=False,
    )
    hot_by_id={item.capability_id:item.status for item in hot.capabilities}
    cold_by_id={item.capability_id:item.status for item in cold.capabilities}

    expected={item["capability_id"] for item in manifest["capabilities"]}
    assert expected.issubset(hot_by_id)
    assert {hot_by_id[item] for item in expected}=={CapabilityStatus.SUPPORTED}

    always_supported={
        "brain.t1.scope_repair",
        "brain.t6.report_contextual",
    }
    assert {
        item
        for item in expected
        if cold_by_id[item]==CapabilityStatus.SUPPORTED
    }==always_supported
    assert {
        item
        for item in expected-always_supported
        if cold_by_id[item]==CapabilityStatus.DATA_DEPENDENT
    }==expected-always_supported


def test_t5_observational_relationship_does_not_require_policy_or_claim_causality():
    composition=(ROOT / "app" / "v3" / "product" / "composition.py").read_text(
        encoding="utf-8"
    )
    projection=(ROOT / "app" / "v3" / "business_relationship_v1.py").read_text(
        encoding="utf-8"
    )
    assert "goal.relationship_intent != RelationshipIntent.OBSERVATIONAL" in composition
    assert "RelationshipPolicyResolutionStatus.NOT_REQUIRED" in projection
    assert "causality_state=RelationshipLayerState.NOT_ESTABLISHED" not in projection
    assert (
        "causality_state: RelationshipLayerState = "
        "RelationshipLayerState.NOT_ESTABLISHED"
    ) in projection
    assert (
        "contribution_state: RelationshipLayerState = "
        "RelationshipLayerState.NOT_ESTABLISHED"
    ) in projection


def test_t6_contextual_report_is_projection_only_and_cannot_reopen_analytics():
    report=(ROOT / "app" / "v3" / "report_document.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "NativeEngineBridge",
        "MetabaseAgentClient",
        "execute_dataset",
        "explore_adhoc",
        "attest_native_query",
        "execute_native_query",
        "wren_service",
    ):
        assert forbidden not in report


def test_t7_multi_intent_remains_material_contract_composition_not_query_planning():
    composition=(ROOT / "app" / "v3" / "product" / "composition.py").read_text(
        encoding="utf-8"
    )
    assert "coorigin_material_requirements" in composition
    for forbidden in (
        "SELECT ",
        "GROUP BY",
        "JOIN ",
        "construct_notebook_query",
        "NativeEngineBridge",
        "MetabaseAgentClient",
    ):
        assert forbidden not in composition


def test_phase2_product_surface_contains_no_frontend_or_benchmark_routing():
    serialized=json.dumps(_manifest(),sort_keys=True).lower()
    assert "benchmark_case_ids" not in serialized
    product_root=ROOT / "app" / "v3" / "product"
    source="\n".join(
        path.read_text(encoding="utf-8")
        for path in product_root.glob("*.py")
    ).lower()
    for forbidden in (
        "next.js",
        "react",
        "30_case",
        "benchmark_case_id",
        "fuzzy",
        "levenshtein",
        "difflib.get_close_matches",
    ):
        assert forbidden not in source
