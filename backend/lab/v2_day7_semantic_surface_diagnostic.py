"""Provider-free Day7 semantic surface pipeline diagnostic.

Diagnostic only. It does not add aliases, morphology, stemming, fuzzy matching,
prompt examples, thresholds, or semantic authority.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.v2.context_provider import ContextProviderV0
from app.v2.models import TenantAnalyticsRuntimeV0
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    _exact_key,
)
from lab.v2_day7_manager_live_sol import (
    Day7LiveSyntheticService,
    MDL_VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day7_semantic_surface_diagnostic.json"

SURFACES = (
    ("bölge", "dimension", "Bölge bazında net geliri incele.", "region_axis_m"),
    ("bölgeler", "dimension", "Bölgeler bazında net geliri incele.", "region_axis_m"),
    ("bölgelere", "dimension", "Net geliri bölgelere göre kır.", "region_axis_m"),
    ("Bölgelerde", "dimension", "Bölgelerde en yüksek 2 net geliri sırala.", "region_axis_m"),
    ("bölgelerde", "dimension", "bölgelerde en yüksek 2 net geliri değerlendir.", "region_axis_m"),
    ("ürün", "dimension", "Net geliri ürün bazında incele.", "product_axis_n"),
    ("ürünler", "dimension", "Ürünler bazında net geliri incele.", "product_axis_n"),
    ("ürünlere", "dimension", "Net geliri ürünlere göre incele.", "product_axis_n"),
)


def _context():
    service = Day7LiveSyntheticService()
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id="day7-semantic-diagnostic",
        tenant_slug="day7-semantic-diagnostic",
        principal_user_id="diagnostic",
        roles=("owner",),
        mdl_version=MDL_VERSION,
        catalog="day7-live-synthetic",
        schema_name="main",
        db_online=True,
    )
    return service, runtime, ContextProviderV0().build(service, runtime)


def _row(*, surface: str, kind_hint: str, decision_context: str, expected: str) -> dict:
    service, runtime, semantic_context = _context()
    handles = SemanticHandleRegistry()
    generator = SemanticCandidateGenerator(
        semantic_context=semantic_context,
        schema=service.schema(),
    )
    retrieval = generator._retriever.retrieve(
        surface=surface,
        kind_hint=kind_hint,
        limit=48,
        decision_context=decision_context,
    )
    candidate_set = generator.generate(
        request_id=f"diag:{surface}",
        surface=surface,
        kind_hint=kind_hint,
        decision_context=decision_context,
    )
    governed = generator._governed_candidates(kind_hint)
    expected_present_in_catalog = any(
        getattr(item.canonical_target, "canonical_name", None) == expected
        for item in governed
    )
    exact = [
        item.card.candidate_id
        for item in candidate_set.bindings
        if _exact_key(surface) in item.exact_keys
    ]

    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-semantic-diagnostic",
            context_version=semantic_context.context_version.version,
        ),
        provider=None,
    )
    selection = linker.resolve(
        ((f"diag:{surface}", surface, kind_hint),),
        provenance_type="USER_SOURCE",
        decision_context=decision_context,
    )[0]

    binding_gate_reached = selection.status == "BOUND"
    binding_gate_result = None
    if binding_gate_reached:
        bound = linker.bind_selection(selection, provenance_type="USER_SOURCE")
        binding_gate_result = {
            "handle_id": bound.handle_id,
            "target_kind": bound.target_kind,
        }

    if not expected_present_in_catalog:
        classification = "FIXTURE/CATALOG"
        owner = "expected canonical concept absent from governed catalog"
    elif not retrieval.candidates:
        classification = "RETRIEVAL_DISCOVERY"
        owner = "governed token-index discovery returned zero candidates before linker"
    elif selection.status == "LINKER_UNAVAILABLE":
        classification = "LINKER_COGNITION"
        owner = "candidate discovery succeeded; bounded linker cognition required"
    elif selection.status == "BOUND" and binding_gate_result is None:
        classification = "BINDING_GATE"
        owner = "candidate selected but authority binding failed"
    else:
        classification = "OTHER CONTRACT"
        owner = f"selection_status={selection.status}"

    return {
        "surface": surface,
        "kind_hint": kind_hint,
        "expected_canonical": expected,
        "expected_present_in_catalog": expected_present_in_catalog,
        "retrieval_backend": retrieval.backend,
        "candidate_count_before_bound": len(retrieval.candidates),
        "candidate_count_visible": len(candidate_set.bindings),
        "candidate_ids": [item.card.candidate_id for item in candidate_set.bindings],
        "candidate_labels": [item.card.label for item in candidate_set.bindings],
        "exact_candidates": exact,
        "decision_context": decision_context,
        "semantic_linker_called": selection.mode == "LINKER",
        "linker_decision": {
            "status": selection.status,
            "mode": selection.mode,
            "reason": selection.reason,
        },
        "binding_gate_reached": binding_gate_reached,
        "binding_gate_result": binding_gate_result,
        "clarification_gap_owner": owner,
        "classification": classification,
    }


def build_receipt() -> dict:
    rows = [
        _row(
            surface=surface,
            kind_hint=kind_hint,
            decision_context=decision_context,
            expected=expected,
        )
        for surface, kind_hint, decision_context, expected in SURFACES
    ]
    return {
        "kind": "dima_v2_day7_semantic_surface_diagnostic",
        "provider_free": True,
        "rows": rows,
        "temporal_surface": {
            "surface": "geçen dönemle",
            "kind_hint": "comparison",
            "pipeline": "typed_temporal_normalizer",
            "catalog_retrieval_applicable": False,
            "explicit_base_period_in_request": False,
            "contract_rule": (
                "COMPARISON may bind without an explicit base only when the exact "
                "surface determines an unambiguous natural base interval."
            ),
            "classification": "OTHER CONTRACT",
            "clarification_gap_owner": (
                "typed comparison has no governed explicit base period; whether the "
                "surface justifies an implicit base is temporal-normalizer cognition/"
                "eval-oracle territory, not catalog retrieval or BindingGate"
            ),
        },
    }


def main() -> int:
    payload = build_receipt()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
