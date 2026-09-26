from __future__ import annotations

from collections import Counter
from pathlib import Path

from app.v3.core_a.ux_foundations import load_ux_foundations

EXPECTED_NAMES = {
    "general": (
        "Smart Onboarding + Data Connection + first Company Map",
        "Sector Intelligence + Company Overlay",
        "Dima Today / Focus Queue",
        "Radar + Watch Engine",
        "Evidence / Trust Drawer",
        "Contextual Ask / Quick Answer",
        "Investigation Workspace / See Why",
        "Domain Root Cause Room",
        "Live Dashboard / Saved Analysis",
        "Morning Briefing / Scheduled Intelligence",
    ),
    "finance": (
        "Smart Collections Desk",
        "Bank–ERP–POS Reconciliation",
        "Daily Cash Radar",
        "Smart Payment Planner",
        "e-Invoice / e-Archive / e-Ledger Compliance Radar",
        "Smart Invoice Auditor",
        "Duplicate / Suspicious Payment and Accounting Anomaly Radar",
        "13-Week Cash Forecast",
        "Customer Risk / Collection Behavior Engine",
        "Financial Cause-Effect / contribution investigation surface",
    ),
    "manufacturing": (
        "Plant Today",
        "Loss Tree / automatic root-cause investigation",
        "Plan vs Actual / Delivery Risk Radar",
        "Capacity / Bottleneck Desk",
        "Scrap / Rework Detector",
        "Downtime / Micro-downtime Intelligence",
        "Maintenance Prioritization / Asset Health",
        "Quality Drift / FPY Radar",
        "Energy / resource-per-unit optimization surface",
        "Money Loss Bridge",
    ),
    "textile": (
        "Right-First-Time Dyeing Radar",
        "Recipe Recommendation / Correction Desk",
        "Batch Preflight",
        "Off-Shade / Rework Root Cause Investigator",
        "Water / Steam / Energy per kg",
        "Dyeing Cycle-Time Optimizer surface",
        "Color Sequence / Machine Scheduling surface",
        "Lab → Bulk Scale-Up Reliability",
        "Stenter / Finishing Optimization surface",
        "Customer Delivery + Quality Risk linker",
    ),
    "plastics": (
        "Process Stability Radar",
        "Cycle Time / Throughput Optimizer surface",
        "Scrap / Reject Root Cause",
        "Drying / Moisture Readiness",
        "Dosing / Masterbatch / Regrind Audit",
        "Mold / Die / Extruder Health",
        "Energy per kg / per shot",
        "Material / Color / Mold Changeover surface",
        "Recycled / Regrind Blend Optimizer surface",
        "Unit Cost / Margin Leak Advisor",
    ),
}

EXPECTED_SPECIALIZED = {
    "finance-04": "constraint_optimizer",
    "finance-07": "advanced_anomaly_model",
    "finance-08": "forecast_service",
    "finance-09": "risk_model",
    "finance-10": "causal_contribution_model",
    "manufacturing-04": "constraint_optimizer",
    "manufacturing-07": "predictive_asset_model",
    "manufacturing-09": "resource_optimizer",
    "textile-02": "recipe_matching_optimizer",
    "textile-06": "cycle_time_optimizer",
    "textile-07": "scheduling_solver",
    "textile-09": "process_optimizer",
    "plastics-02": "throughput_optimizer",
    "plastics-08": "changeover_scheduler",
    "plastics-09": "blend_optimizer",
}


def test_wave_one_catalog_contains_exactly_fifty_ordered_descriptors():
    catalog = load_ux_foundations()
    assert len(catalog.descriptors) == 50
    counts = Counter(item.group for item in catalog.descriptors)
    assert counts == {
        "general": 10,
        "finance": 10,
        "manufacturing": 10,
        "textile": 10,
        "plastics": 10,
    }
    for group, names in EXPECTED_NAMES.items():
        rows = [item for item in catalog.descriptors if item.group == group]
        assert tuple(item.ordinal for item in rows) == tuple(range(1, 11))
        assert tuple(item.ux_name for item in rows) == names


def test_every_descriptor_has_complete_backend_dependency_contract():
    catalog = load_ux_foundations()
    for item in catalog.descriptors:
        assert item.business_objective.strip()
        assert item.required_entity_types
        assert item.required_metrics
        assert item.required_source_data
        assert item.headless_api_needs
        assert item.shared_motors
        assert "SemanticRefs" in item.shared_motors
        assert "stable_entity_refs" in item.headless_api_needs
        assert "tenant_non_oracle" in item.headless_api_needs


def test_sector_foundations_share_core_instead_of_product_forks():
    catalog = load_ux_foundations()
    for item in catalog.descriptors:
        if item.group == "manufacturing":
            assert "DIMA_MANUFACTURING_CORE" in item.sector_pack_requirements
            assert "SectorPack" in item.shared_motors
        if item.group in {"textile", "plastics"}:
            assert "DIMA_MANUFACTURING_CORE" in item.sector_pack_requirements
            assert f"sector-pack:{item.group}" in item.sector_pack_requirements
            assert "SectorPack" in item.shared_motors


def test_specialized_engines_are_explicitly_deferred():
    catalog = load_ux_foundations()
    by_id = {item.ux_id: item for item in catalog.descriptors}
    actual = {
        item.ux_id: item.specialized_engine_gap.split(":", 1)[1]
        for item in catalog.descriptors
        if item.specialized_engine_gap is not None
    }
    assert actual == EXPECTED_SPECIALIZED
    for ux_id, engine in EXPECTED_SPECIALIZED.items():
        item = by_id[ux_id]
        assert item.current_feasibility == "SPECIAL_ENGINE_DEFERRED"
        assert item.deferred_capabilities == (engine,)


def test_non_deferred_foundations_do_not_smuggle_heavy_engine_implementation():
    catalog = load_ux_foundations()
    heavy_terms = {
        "forecast_service",
        "constraint_optimizer",
        "scheduling_solver",
        "causal_contribution_model",
        "advanced_anomaly_model",
        "blend_optimizer",
        "throughput_optimizer",
        "process_optimizer",
    }
    for item in catalog.descriptors:
        if item.specialized_engine_gap is None:
            assert not heavy_terms.intersection(item.deferred_capabilities)


def test_catalog_is_shared_contract_not_fifty_services():
    catalog = load_ux_foundations()
    allowed_motors = {
        "CompanyMap",
        "EntityRegistry",
        "SemanticRefs",
        "Watch",
        "Signal",
        "Investigation",
        "Evidence",
        "Decision",
        "ActionWork",
        "Outcome",
        "Memory",
        "SectorPack",
    }
    all_motors = {motor for item in catalog.descriptors for motor in item.shared_motors}
    assert all_motors <= allowed_motors
    assert len(all_motors) <= len(allowed_motors)


def test_ux_foundations_are_backend_only_and_create_no_frontend_surface():
    module = Path("app/v3/core_a/ux_foundations.py").read_text(encoding="utf-8")
    catalog = Path("product_contracts/ux_foundations.json").read_text(encoding="utf-8")
    for token in (
        "React",
        "tsx",
        "Next.js",
        "CSS",
        "frontend route",
        "Metabase embedding",
        "chart component",
        "dashboard shell",
    ):
        assert token not in module
        assert token not in catalog


def test_catalog_load_is_deterministic():
    first = load_ux_foundations()
    second = load_ux_foundations()
    assert first == second
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
