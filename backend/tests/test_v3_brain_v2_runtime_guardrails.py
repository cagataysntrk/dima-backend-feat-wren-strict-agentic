from pathlib import Path
import json
import re
import subprocess
import sys

from lab.metabase.brain_v2.final_probes import (
    FINAL_CAPABILITY_RUNTIME,
    ForwardRuntime,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
LIVE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "dima-brain-v2-phase1-live.yml"
BRAIN_LIVE = BACKEND_ROOT / "lab" / "metabase" / "brain_v2" / "phase1_live.py"
LIVE_SUPPORT = BACKEND_ROOT / "lab" / "metabase" / "brain_v2" / "live_support.py"
SEMANTIC_AUTHORITY_REGISTRY = BACKEND_ROOT / "lab" / "metabase" / "brain_v2" / "semantic_authority_registry.json"
ROOT_RECOVERY_AUTHORIZATION = BACKEND_ROOT / "lab" / "metabase" / "brain_v2" / "root_recovery_panel_authorization.json"


def test_all_final_probes_use_brain_v2_runtime():
    assert set(FINAL_CAPABILITY_RUNTIME) == {f"T{i}" for i in range(1, 8)}
    assert set(FINAL_CAPABILITY_RUNTIME.values()) == {
        ForwardRuntime.BRAIN_V2_LANGGRAPH
    }


def test_no_final_probe_imports_or_calls_headless_composer():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    harness = BRAIN_LIVE.read_text(encoding="utf-8")
    support = LIVE_SUPPORT.read_text(encoding="utf-8")
    assert "core_b/phase1_pinpoint_live.py" not in workflow
    assert "phase1_pinpoint_live import" not in harness
    assert "HeadlessProductComposer" not in workflow
    assert "HeadlessProductComposer" not in harness
    assert "from lab.metabase.core_b import live_sentinel" not in harness
    assert "import lab.metabase.core_b.live_sentinel" not in harness
    assert "from lab.metabase.core_b import live_sentinel" not in support
    assert "import lab.metabase.core_b.live_sentinel" not in support
    # Documentation may name the retired class. Import/call-path checks above
    # plus the isolated sys.modules test below enforce the runtime prohibition.


def test_agent_api_disabled_in_final_live():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "MB_AGENT_API_ENABLED=false" in workflow
    assert "MB_AGENT_API_ENABLED=true" not in workflow


def test_live_probe_owner_map_is_single_runtime():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert workflow.count("lab/metabase/brain_v2/phase1_live.py") >= 1
    assert "lab/metabase/core_b/phase1_pinpoint_live.py" not in workflow


def test_final_harness_import_graph_contains_no_legacy_runtime_module():
    code = (
        "import sys; import lab.metabase.brain_v2.phase1_live; "
        "forbidden={'lab.metabase.core_b.live_sentinel',"
        "'lab.metabase.core_b.phase1_pinpoint_live',"
        "'app.v3.product.composition'}; "
        "loaded=sorted(forbidden.intersection(sys.modules)); "
        "assert not loaded, loaded"
    )
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_ROOT,
        check=True,
    )


def test_production_brain_v2_contains_no_benchmark_or_case_ids():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((BACKEND_ROOT / "app" / "v3" / "brain_v2").rglob("*.py"))
    )
    forbidden = (
        r"\bDEV80\b",
        r"\bValidation50\b",
        r"\bHidden50\b",
        r"\b30[-_ ]?case\b",
        r"\bF0[0-9]\b",
        r"\bF10\b",
        r"\bT[1-7]\b",
    )
    for pattern in forbidden:
        assert re.search(pattern, source, flags=re.IGNORECASE) is None, pattern


def test_normal_discovery_has_no_p17_provider_graph_route():
    graph = (
        BACKEND_ROOT / "app" / "v3" / "brain_v2" / "graph.py"
    ).read_text(encoding="utf-8")
    assert 'builder.add_node("p17_discover"' not in graph
    assert '"project_candidates": "project_candidates"' in graph


def test_normal_relationship_owner_never_routes_through_p17():
    import inspect

    from app.v3.brain_v2.owner_adapter import DimaBrainV2Activities

    source = inspect.getsource(DimaBrainV2Activities.adjudicate_relationship)
    for forbidden in (
        "_investigation.run_one",
        "_RelationshipInterpretationProposalManager",
        "_investigation_manager",
        "FORM_CLAIM",
    ):
        assert forbidden not in source
    assert "_relationship_interpreter.interpret" in source
    assert "load_verified_evidence_digests" in source



def test_closed_v1_grammar_is_conformance_only_not_runtime_veto():
    """Closed grammar may describe/test compositions; it must not veto production flow."""

    production = BACKEND_ROOT / "app" / "v3"
    forbidden = (
        "assert_v1_analytical_composition",
        "validate_v1_research_brief",
    )
    offenders = []
    for path in sorted(production.rglob("*.py")):
        if path.name == "analytical_boundary.py":
            continue
        source = path.read_text(encoding="utf-8")
        for symbol in forbidden:
            if symbol in source:
                offenders.append(f"{path.relative_to(BACKEND_ROOT)}:{symbol}")
    assert not offenders, offenders


def test_fulfillment_verifier_has_one_runtime_admission_owner():
    """Intent <-> ExecutionManifest semantic admission has exactly one runtime owner."""

    production = BACKEND_ROOT / "app" / "v3"
    owners = {
        path.relative_to(BACKEND_ROOT).as_posix()
        for path in sorted(production.rglob("*.py"))
        if "verify_analytical_fulfillment_v1" in path.read_text(encoding="utf-8")
    }
    assert owners == {
        "app/v3/analytical_boundary.py",
        "app/v3/research_native_gateway.py",
    }


def test_material_group_is_execution_projection_not_semantic_judge():
    source = (
        BACKEND_ROOT / "app" / "v3" / "brain_v2" / "material_groups.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "verify_analytical_fulfillment_v1",
        "AnalyticalExecutionManifestV1",
        "EvidenceArtifact",
        "execute_native_query(",
    ):
        assert forbidden not in source


def test_epistemic_and_synthesis_owners_do_not_execute_native_analytics():
    paths = (
        BACKEND_ROOT / "app" / "v3" / "p18_relationship_interpreter.py",
        BACKEND_ROOT / "app" / "v3" / "hypothesis_root_cause.py",
        BACKEND_ROOT / "app" / "v3" / "brain_v2" / "report_synthesis.py",
    )
    forbidden = (
        "execute_native_query(",
        "NativeEngineBridge",
        "analytical_scope_contract(",
        ".run_next(",
    )
    offenders = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        for symbol in forbidden:
            if symbol in source:
                offenders.append(f"{path.relative_to(BACKEND_ROOT)}:{symbol}")
    assert not offenders, offenders


def test_semantic_authority_registry_matches_constitution():
    registry = json.loads(
        SEMANTIC_AUTHORITY_REGISTRY.read_text(encoding="utf-8")
    )
    assert registry["schema_version"] == "dima_semantic_authority_law_v1"
    assert registry["sole_fulfillment_judge"] == "verify_analytical_fulfillment_v1"
    assert registry["laws"]["closed_grammar_runtime_veto_forbidden"] is True
    assert registry["laws"]["new_duplicate_semantic_owner_forbidden"] is True
    assert registry["laws"]["acquisition_identity_not_requirement_identity"] is True
    assert registry["laws"]["p18_turn_bundle_atomic_reset"] is True


def test_langgraph_remains_orchestration_not_semantic_owner():
    source = (
        BACKEND_ROOT / "app" / "v3" / "brain_v2" / "graph.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "analytical_scope_contract(",
        "verify_analytical_fulfillment_v1",
        "assert_material_native_scope",
        "assert_material_result_coverage",
        "NativeEngineBridge",
    ):
        assert forbidden not in source


def test_completion_remains_ledger_not_analytics():
    for relative in (
        "app/v3/brain_v2/completion_policy.py",
        "app/v3/product/completion.py",
    ):
        source = (BACKEND_ROOT / relative).read_text(encoding="utf-8")
        for forbidden in (
            "analytical_scope_contract(",
            "verify_analytical_fulfillment_v1",
            "assert_material_native_scope",
            "assert_material_result_coverage",
            "NativeEngineBridge",
            "execute_native_query(",
        ):
            assert forbidden not in source


def test_open_semantic_authority_blocker_disarms_paid_recovery():
    registry = json.loads(
        SEMANTIC_AUTHORITY_REGISTRY.read_text(encoding="utf-8")
    )
    compliance = registry.get("runtime_compliance") or {}
    blockers = compliance.get("blockers") or []
    if blockers:
        authorization = json.loads(
            ROOT_RECOVERY_AUTHORIZATION.read_text(encoding="utf-8")
        )
        assert authorization["enabled"] is False
        assert authorization["broad_paid_allowed"] is False
        assert authorization["thirty_case_allowed"] is False
        assert authorization["frontend_allowed"] is False

def test_native_gateway_projects_execution_facts_without_transitional_semantic_vetoes():
    """P14 may correlate/project facts; business fulfillment belongs only to final verifier."""

    source = (
        BACKEND_ROOT / "app" / "v3" / "research_native_gateway.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "assert_material_native_scope",
        "assert_material_result_coverage",
    ):
        assert forbidden not in source
    assert "project_execution_manifest_v1" in source
    assert "verify_analytical_fulfillment_v1" in source
    execute_source = source[source.index("    def execute("):]
    assert execute_source.index("bridge.execute_native_query(") < execute_source.index(
        "execution_facts=observed.execution_facts"
    )
    assert execute_source.index("execution_facts=observed.execution_facts") < execute_source.rindex(
        "_execution_fact_observation("
    )
    assert "execution_facts=persisted_execution_facts" in execute_source
    assert "observe_native_query_material" not in source
    assert "_observe_executed_occurrence" not in source

def test_execution_manifest_separates_period_scope_from_result_time_axis():
    """Temporal filters/change periods cannot masquerade as result temporal grain."""

    source = (
        BACKEND_ROOT / "app" / "v3" / "research_native_gateway.py"
    ).read_text(encoding="utf-8")
    assert "temporal_observation_candidates" in source
    assert "temporal_candidates" not in source
    # Only the result-bucket branch may add the result time axis.
    assert source.count("temporal_observation_candidates.append(") == 1
    assert 'source="native_filter"' in source
    assert '"change_baseline"' in source
    assert '"change_comparison"' in source

def test_planner_material_envelope_has_no_duplicate_change_semantic_surfaces():
    source = (
        BACKEND_ROOT / "app" / "v3" / "research_analytical_scope.py"
    ).read_text(encoding="utf-8")
    start = source.index("def native_material_requirement(")
    end = source.index("def native_request_context(", start)
    body = source[start:end]
    for forbidden in (
        '"change_semantics"',
        '"temporal_change_frame"',
        '"material_coverage_period"',
        '"required_metric_refs"',
        '"required_breakout_refs"',
    ):
        assert forbidden not in body
    assert '"temporal_periods"' in body
    assert '"metrics"' in body
    assert '"dimensions"' in body


def test_p17_exact_query_reuse_is_structural_and_pre_execution():
    product = (
        BACKEND_ROOT / "app" / "v3" / "research_product.py"
    ).read_text(encoding="utf-8")
    store = (
        BACKEND_ROOT / "app" / "v3" / "research_store.py"
    ).read_text(encoding="utf-8")
    assert "verified_link_for_query_fingerprint" in store
    assert "P17_NATIVE_QUERY_ALREADY_VERIFIED" in product
    capture = product.index("produced = bridge.capture_produced_query(")
    material = product.index("outcome = self._materials.execute(")
    reuse = product.index("verified_link_for_query_fingerprint", capture)
    assert capture < reuse < material



def test_base_p14_planner_and_verifier_use_canonical_intent_not_request_contract():
    boundary = (
        BACKEND_ROOT / "app" / "v3" / "analytical_boundary.py"
    ).read_text(encoding="utf-8")
    research = (
        BACKEND_ROOT / "app" / "v3" / "research.py"
    ).read_text(encoding="utf-8")
    gateway = (
        BACKEND_ROOT / "app" / "v3" / "research_native_gateway.py"
    ).read_text(encoding="utf-8")

    start = boundary.index("def project_analytical_intent_v1(")
    end = boundary.index("def planner_analytical_intent_payload(", start)
    direct = boundary[start:end]
    for forbidden in (
        "contract.metric_refs",
        "contract.dimension_refs",
        "contract.filters",
        "contract.ranking",
        "contract.temporal_observation",
    ):
        assert forbidden not in direct

    direct_message = research[
        research.index("if analytical_intent is not None:"):
        research.index(
            "requirement = native_material_requirement(",
            research.index("if analytical_intent is not None:"),
        )
    ]
    assert '"dima_analytical_intent": payload' in direct_message
    assert "[USER OBLIGATION]" not in direct_message

    verify_start = gateway.index("consumer_intents = tuple(")
    verify_end = gateway.index(
        "for consumer_intent in consumer_intents:",
        verify_start,
    )
    verify_block = gateway[verify_start:verify_end]
    assert "project_analytical_intent_v1(" in verify_block
    assert "analytical_scope_contract(" not in verify_block

def test_material_group_sharing_is_not_rejudged_by_owner_adapter():
    source = (
        BACKEND_ROOT / "app" / "v3" / "brain_v2" / "owner_adapter.py"
    ).read_text(encoding="utf-8")
    start = source.index("    def acquire_material_group(")
    end = source.index("    def acquire_material(", start)
    body = source[start:end]
    assert "RequirementOwner.DIRECT_EVIDENCE" in body
    assert "dispatch_requirements(brief)" in body
    assert "ResearchGoalKind.COMPARISON" not in body
    assert "ResearchGoalKind.RANKING" not in body
    assert "ResearchGoalKind.BREAKDOWN" not in body

