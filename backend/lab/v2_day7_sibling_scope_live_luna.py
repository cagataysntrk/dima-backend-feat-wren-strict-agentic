"""Manual-only LIVE Luna bake-off for GOVERNED_SIBLING_SCOPE_DISCOVERY.

Product semantics are not modified.  This script evaluates only bounded cognition:
current governed candidate set -> Luna SELECT/ABSTAIN -> existing BindingGate.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.v2.manager_lab import _build_role_scoped_manager_models
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    StructuredSemanticCandidateDecisionProvider,
)
from lab.v2_day7_governed_sibling_scope_discovery import (
    DEFAULT_MAX_CANDIDATES,
    GovernedSiblingScopeCandidateGenerator,
    _bind_exact_sibling,
    _canonical_name,
    _context,
)
from lab.v2_day7_manager_live_sol import (
    LIVE_LINKER_MODEL,
    MeasurementValidity,
    _classify_provider_failure,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT / "lab" / "reports" / "v2_day7_sibling_scope_live_luna.json"
)

# Keep the sealed role topology even though this lab invokes only the semantic-linker role.
os.environ.setdefault("DIMA_LLM_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_SEMANTIC_LINKER_PROVIDER", "openrouter")
os.environ["DIMA_V2_SEMANTIC_LINKER_MODEL"] = LIVE_LINKER_MODEL


LIVE_CASES = (
    {
        "id": "region-dative",
        "surface": "bölgelere",
        "kind_hint": "dimension",
        "sibling_surface": "net gelir",
        "sibling_kind": "metric",
        "context": "Net geliri bölgelere göre kır.",
        "expected": "region_axis_m",
        "decision": "SELECT",
    },
    {
        "id": "region-locative",
        "surface": "Bölgelerde",
        "kind_hint": "dimension",
        "sibling_surface": "net gelir",
        "sibling_kind": "metric",
        "context": "Bölgelerde net geliri incele.",
        "expected": "region_axis_m",
        "decision": "SELECT",
    },
    {
        "id": "product-dative",
        "surface": "ürünlere",
        "kind_hint": "dimension",
        "sibling_surface": "net gelir",
        "sibling_kind": "metric",
        "context": "Net geliri ürünlere göre incele.",
        "expected": "product_axis_n",
        "decision": "SELECT",
    },
    {
        "id": "department-instrumental",
        "surface": "bölümlerle",
        "kind_hint": "dimension",
        "sibling_surface": "duruş süresi",
        "sibling_kind": "metric",
        "context": "Duruş süresinin bölümlerle ilişkisini incele.",
        "expected": "department_axis_d",
        "decision": "SELECT",
    },
    {
        "id": "unknown-abstain",
        "surface": "tamamen bilinmeyen eksen",
        "kind_hint": "dimension",
        "sibling_surface": "net gelir",
        "sibling_kind": "metric",
        "context": "Net gelir için tamamen bilinmeyen ekseni incele.",
        "expected": None,
        "decision": "ABSTAIN",
    },
    {
        "id": "wrong-scope-abstain",
        "surface": "bölümlerle",
        "kind_hint": "dimension",
        "sibling_surface": "net gelir",
        "sibling_kind": "metric",
        "context": "Net gelirin bölümlerle ilişkisini incele.",
        "expected": None,
        "decision": "ABSTAIN",
    },
)


def _preflight(structured, profile) -> dict[str, Any]:
    started = time.perf_counter()
    schema = {
        "type": "object",
        "properties": {"status": {"type": "string", "enum": ["ok"]}},
        "required": ["status"],
        "additionalProperties": False,
    }
    try:
        raw = structured(
            "Dima Day7 semantic-linker LAB preflight. Return only the required schema.",
            '{"probe":"semantic_linker_structured_transport"}',
            schema=schema,
            schema_name="dima_day7_semantic_linker_lab_preflight_v1",
        )
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict) or data.get("status") != "ok":
            return {
                "ok": False,
                "measurement_validity": MeasurementValidity.PROVIDER_UNAVAILABLE.value,
                "provider": profile.provider,
                "model": profile.model,
                "message": "semantic linker did not return required preflight schema",
                "latency_s": round(time.perf_counter() - started, 4),
            }
        return {
            "ok": True,
            "measurement_validity": MeasurementValidity.VALID.value,
            "provider": profile.provider,
            "model": profile.model,
            "message": None,
            "latency_s": round(time.perf_counter() - started, 4),
        }
    except Exception as exc:
        diagnostic = str(exc)
        try:
            response = getattr(exc, "response", None)
            body = str(getattr(response, "text", "") or "")
            if body:
                diagnostic += f" | body={body[:800]}"
        except Exception:
            pass
        return {
            "ok": False,
            "measurement_validity": (
                _classify_provider_failure(diagnostic)
                or MeasurementValidity.PROVIDER_UNAVAILABLE
            ).value,
            "provider": getattr(profile, "provider", "unknown"),
            "model": getattr(profile, "model", LIVE_LINKER_MODEL),
            "message": diagnostic[:1200],
            "latency_s": round(time.perf_counter() - started, 4),
        }


def _run_case(case: dict[str, Any], *, provider) -> dict[str, Any]:
    service, context = _context()
    handles = SemanticHandleRegistry()
    base = SemanticCandidateGenerator(
        semantic_context=context,
        schema=service.schema(),
        max_candidates=DEFAULT_MAX_CANDIDATES,
    )
    sibling_handle, scope = _bind_exact_sibling(
        generator=base,
        handles=handles,
        context_version=context.context_version.version,
        surface=case["sibling_surface"],
        kind_hint=case["sibling_kind"],
        decision_context=case["context"],
    )
    scoped = GovernedSiblingScopeCandidateGenerator(
        base=base,
        sibling_cube_names=scope,
        max_candidates=DEFAULT_MAX_CANDIDATES,
    )
    candidate_set = scoped.generate(
        request_id=case["id"],
        surface=case["surface"],
        kind_hint=case["kind_hint"],
        decision_context=case["context"],
    )
    candidate_names = tuple(_canonical_name(item) for item in candidate_set.bindings)

    before_handles = set(handles._bindings)
    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context.context_version.version,
        ),
        provider=provider,
    )
    started = time.perf_counter()
    selection = linker.resolve(
        ((case["id"], case["surface"], case["kind_hint"]),),
        provenance_type="USER_SOURCE",
        decision_context=case["context"],
    )[0]
    latency = time.perf_counter() - started

    selected_canonical = None
    target_handle_id = None
    if selection.status == "BOUND":
        target_handle = linker.bind_selection(
            selection,
            provenance_type="USER_SOURCE",
        )
        target_handle_id = target_handle.handle_id
        binding = handles.binding_for_execution(
            target_handle.handle_id,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context.context_version.version,
        )
        selected_canonical = getattr(binding.canonical_target, "canonical_name", None)

    new_handles = set(handles._bindings) - before_handles
    expected_decision = case["decision"]
    if expected_decision == "SELECT":
        passed = (
            selection.status == "BOUND"
            and selection.mode == "LINKER"
            and selected_canonical == case["expected"]
            and target_handle_id in new_handles
        )
    else:
        passed = (
            selection.status == "ABSTAIN"
            and target_handle_id is None
            and not new_handles
        )

    return {
        "case_id": case["id"],
        "surface": case["surface"],
        "sibling_surface": case["sibling_surface"],
        "sibling_handle": sibling_handle.handle_id,
        "sibling_cube_names": list(scope),
        "candidate_count": len(candidate_set.bindings),
        "candidate_canonical_names": list(candidate_names),
        "too_broad": candidate_set.too_broad,
        "retrieval_backend": candidate_set.retrieval_backend,
        "expected_decision": expected_decision,
        "expected_canonical": case["expected"],
        "linker_status": selection.status,
        "linker_mode": selection.mode,
        "selected_canonical": selected_canonical,
        "target_handle_id": target_handle_id,
        "authority_minted_only_after_bound": (
            bool(target_handle_id) if expected_decision == "SELECT" else not new_handles
        ),
        "pass": passed,
        "latency_s": round(latency, 4),
    }


def main() -> int:
    settings = get_settings()
    (
        _manager_llm,
        _manager_profile,
        linker_llm,
        linker_profile,
        _temporal_llm,
        _temporal_profile,
    ) = _build_role_scoped_manager_models(settings)
    structured = getattr(linker_llm, "structured_json", None)
    if not callable(structured):
        payload = {
            "kind": "dima_v2_day7_sibling_scope_live_luna",
            "measurement_valid": False,
            "measurement_validity": MeasurementValidity.HARNESS_FAILURE.value,
            "selected_cases": len(LIVE_CASES),
            "evaluable_cases": 0,
            "records": [],
            "status": "invalid_measurement",
            "message": "semantic linker structured_json unavailable",
        }
        DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2

    preflight = _preflight(structured, linker_profile)
    if not preflight["ok"]:
        payload = {
            "kind": "dima_v2_day7_sibling_scope_live_luna",
            "provider_preflight": preflight,
            "measurement_valid": False,
            "measurement_validity": preflight["measurement_validity"],
            "selected_cases": len(LIVE_CASES),
            "evaluable_cases": 0,
            "records": [],
            "status": "invalid_measurement",
        }
        DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2

    provider = StructuredSemanticCandidateDecisionProvider(structured=structured)
    records = []
    for case in LIVE_CASES:
        try:
            records.append(_run_case(case, provider=provider))
        except Exception as exc:
            diagnostic = str(exc)
            provider_failure = _classify_provider_failure(diagnostic)
            if provider_failure is not None:
                payload = {
                    "kind": "dima_v2_day7_sibling_scope_live_luna",
                    "provider_preflight": preflight,
                    "measurement_valid": False,
                    "measurement_validity": provider_failure.value,
                    "selected_cases": len(LIVE_CASES),
                    "evaluable_cases": len(records),
                    "records": records,
                    "status": "invalid_measurement",
                    "message": diagnostic[:1200],
                }
                DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
                DEFAULT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                print(json.dumps(payload, ensure_ascii=False))
                return 2
            records.append(
                {
                    "case_id": case["id"],
                    "surface": case["surface"],
                    "pass": False,
                    "error": diagnostic[:1200],
                }
            )

    passes = sum(int(bool(item.get("pass"))) for item in records)
    payload = {
        "kind": "dima_v2_day7_sibling_scope_live_luna",
        "provider_preflight": preflight,
        "measurement_valid": True,
        "measurement_validity": MeasurementValidity.VALID.value,
        "product_behavior_changed": False,
        "model": linker_profile.model,
        "selected_cases": len(LIVE_CASES),
        "evaluable_cases": len(records),
        "pass_count": passes,
        "pass_rate": round(passes / len(records), 4),
        "records": records,
        "status": "pass" if passes == len(records) else "fail",
    }
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
