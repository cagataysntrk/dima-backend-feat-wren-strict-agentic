"""Provider-free constitution for the pre-comparison development rehearsal."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
MANIFEST = BACKEND / "eval" / "v2_precomparison_rehearsal_cases.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_rehearsal_is_exactly_development_scope_and_20_to_25_cases():
    manifest = _manifest()
    assert manifest["status"] == "DEVELOPMENT_REHEARSAL"
    assert 20 <= manifest["case_count"] <= 25
    assert manifest["case_count"] == len(manifest["cases"])
    assert manifest["real_llm_required"] is True
    assert manifest["real_wren_required"] is True
    assert manifest["large_certification_corpus"] is False
    assert {"DEV80", "Validation50", "Hidden50"} <= set(manifest["forbidden"])


def test_rehearsal_covers_required_product_categories():
    categories = {item["category"] for item in _manifest()["cases"]}
    required = {
        "standard_analytical_question",
        "breakdown",
        "ranking",
        "relationship",
        "multi_intent",
        "research",
        "root_cause",
        "adaptive_branch",
        "unsupported_request",
        "clarification",
        "conversation_repair",
        "persistence_resume",
        "security_isolation",
    }
    assert required <= categories
    kinds = {item["kind"] for item in _manifest()["cases"]}
    assert "signed_continuation" in kinds
    assert "restart_continuation" in kinds
    assert "foreign_principal_replay" in kinds


def test_rehearsal_import_performs_no_provider_or_wren_execution():
    module = importlib.import_module("lab.v2_precomparison_rehearsal_live")
    assert module.CASES == MANIFEST
    assert callable(module.run)


def test_rehearsal_manifest_has_no_wren_internal_or_certification_case_ids():
    raw = MANIFEST.read_text(encoding="utf-8").lower()
    assert "dev80-" not in raw
    assert "validation50" in raw  # forbidden marker only
    assert "hidden50" in raw  # forbidden marker only
    for forbidden in ("cube_sql_expected", "action_ref", "wren_internal_event"):
        assert forbidden not in raw


def test_every_rehearsal_case_has_explicit_behavioral_contract_class():
    manifest = _manifest()
    allowed = {
        "MUST_EXECUTE",
        "MAY_CLARIFY",
        "MUST_CLARIFY",
        "MUST_REJECT",
        "SECURITY_ATTACK",
        "CONTINUATION",
        "PERSISTENCE",
    }
    assert set(manifest["contract_classes"]) == allowed
    assert all(item["contract_class"] in allowed for item in manifest["cases"])


def test_canonical_metamorphic_family_shares_one_execution_contract_class():
    cases = {item["id"]: item for item in _manifest()["cases"]}
    assert {
        cases["canonical_full"]["contract_class"],
        cases["canonical_reordered"]["contract_class"],
        cases["canonical_no_diacritics"]["contract_class"],
    } == {"MUST_EXECUTE"}


def test_orthogonal_cases_are_not_scored_as_generic_analytical_execution_contracts():
    cases = {item["id"]: item for item in _manifest()["cases"]}
    assert cases["foreign_principal_replay"]["contract_class"] == "SECURITY_ATTACK"
    assert cases["broaden_policy"]["contract_class"] == "CONTINUATION"
    assert cases["report_control"]["contract_class"] == "CONTINUATION"
    assert cases["restart_signed_continuation"]["contract_class"] == "PERSISTENCE"
