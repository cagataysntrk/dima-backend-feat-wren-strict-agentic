"""LIVE relationship structured-action diagnostic for Day7.

Diagnostic only:
- no product Manager/prompt/tool/relationship behavior is modified;
- no CrossDomainJoinGate/fact-builder/Wren relationship code is patched;
- a recording wrapper captures strict-schema model outputs while delegating to the
  existing RESEARCH_MANAGER provider;
- execution still uses the current governed ManagerLabHarness and synthetic live service.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.routers.manager_lab import router as manager_lab_router
import app.v2.manager_lab as manager_lab_module
import app.v2.runtime_boundary as runtime_boundary
from control_plane.authorize import Principal
from lab.v2_day7_manager_live_sol import (
    Day7LiveSyntheticService,
    LiveContracts,
    MeasurementValidity,
    _provider_preflight,
)

PRODUCT_BEHAVIOR_BASE_SHA = "b70f0aab209b2353b854463ace582c40bcc2bd98"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "reports" / "v2_day7_relationship_action_diagnostic.json"

CASES = (
    {
        "case_id": "relationship-safe",
        "question": "Duruş süresinin bölümlerle ilişkisini incele.",
    },
    {
        "case_id": "relationship-unsafe",
        "question": "Net gelir ile üretim bölümü arasındaki ilişkiyi incele.",
    },
)

_CURRENT_CASE = {"case_id": None}
_RAW_CALLS: list[dict[str, Any]] = []


def _jsonish(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


class _RecordingManagerLLM:
    def __init__(self, inner) -> None:
        self._inner = inner

    def __getattr__(self, name: str):
        return getattr(self._inner, name)

    def structured_json(self, system, user, **kwargs):
        record = {
            "case_id": _CURRENT_CASE["case_id"],
            "schema_name": kwargs.get("schema_name"),
            "system_first_line": str(system).splitlines()[0] if system else "",
        }
        try:
            raw = self._inner.structured_json(system, user, **kwargs)
        except Exception as exc:
            record["provider_error"] = f"{type(exc).__name__}: {exc}"
            _RAW_CALLS.append(record)
            raise
        record["raw_output"] = _jsonish(raw)
        _RAW_CALLS.append(record)
        return raw


def _install_recording_builder():
    original = manager_lab_module._build_role_scoped_manager_models

    def builder(settings):
        values = list(original(settings))
        values[0] = _RecordingManagerLLM(values[0])
        return tuple(values)

    manager_lab_module._build_role_scoped_manager_models = builder
    return original


def _first(observations: list[dict[str, Any]], kind: str) -> dict[str, Any] | None:
    return next((item for item in observations if item.get("kind") == kind), None)


def _raw_relationship_actions(case_id: str) -> list[dict[str, Any]]:
    out = []
    for call in _RAW_CALLS:
        if call.get("case_id") != case_id:
            continue
        if call.get("schema_name") != "dima_research_manager_action_v1":
            continue
        raw = call.get("raw_output")
        if isinstance(raw, dict) and raw.get("action") == "run_relationship":
            out.append(raw)
    return out


def _derived_fields(raw: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "derived_task_id",
        "derived_parent_obligation_id",
        "derived_capability_key",
        "derived_evidence_ref",
        "derived_reason",
    )
    return {
        key: raw.get(key)
        for key in keys
        if raw.get(key) is not None
    }


def _case_receipt(case: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
    observations = list(body.get("observations") or ())
    intent = _first(observations, "intent_draft") or {}
    grounding = _first(observations, "grounding") or {}
    seed = _first(observations, "seed_tasks_registered")
    ledger = body.get("ledger") or {}
    items = list(ledger.get("items") or ())
    accepted = items[0] if items else None
    requested = list((grounding.get("summary") or {}).get("requested") or ())
    raw_post = [
        call
        for call in _RAW_CALLS
        if call.get("case_id") == case["case_id"]
        and call.get("schema_name") == "dima_research_manager_action_v1"
    ]
    relationship_raw = _raw_relationship_actions(case["case_id"])
    user_source_reparse = any(
        item.get("kind") == "tool_rejected"
        and item.get("action") == "resolve_semantics"
        and "post-acceptance USER_SOURCE" in str(item.get("message") or "")
        for item in observations
    )

    unresolved = [
        item for item in requested
        if item.get("resolved") is False
    ]
    accepted_with_unresolved_relationship_surface = bool(
        body.get("snapshot", {}).get("accepted_contract_id")
        and accepted
        and accepted.get("capability_key") == "relationship"
        and unresolved
    )

    first_owner = (
        "PREACCEPTANCE_COMPLETENESS"
        if accepted_with_unresolved_relationship_surface
        else "UNCLASSIFIED"
    )
    secondary = []
    if user_source_reparse:
        secondary.append(
            "POST_ACCEPTANCE_USER_SOURCE_REPARSE_ATTEMPT_BLOCKED"
        )
    if any(_derived_fields(raw) for raw in relationship_raw):
        secondary.append(
            "MODEL_COGNITION_INVALID_DERIVED_FIELDS_ON_RUN_RELATIONSHIP"
        )

    return {
        "case_id": case["case_id"],
        "question": case["question"],
        "accepted_contract_id": (body.get("snapshot") or {}).get("accepted_contract_id"),
        "accepted_obligation": accepted,
        "accepted_semantic_handles": (
            list(accepted.get("semantic_handle_refs") or ())
            if accepted else []
        ),
        "intent_draft": intent.get("draft"),
        "grounding_requested": requested,
        "grounding_unresolved_source_refs": list(
            (grounding.get("summary") or {}).get("unresolved_source_refs") or ()
        ),
        "seed_task_observation": seed,
        "manager_postacceptance_raw_calls": raw_post,
        "run_relationship_raw_outputs": relationship_raw,
        "derived_fields_on_run_relationship": [
            _derived_fields(raw) for raw in relationship_raw
        ],
        "attempted_postacceptance_user_source_reparse": user_source_reparse,
        "model_errors": [
            item for item in observations if item.get("kind") == "model_error"
        ],
        "data_queries": int((body.get("snapshot") or {}).get("data_queries") or 0),
        "evidence_refs": list((body.get("snapshot") or {}).get("evidence_refs") or ()),
        "first_owner": first_owner,
        "secondary_observations": secondary,
        "first_owner_reason": (
            "RELATIONSHIP contract was accepted while a user-requested semantic "
            "relationship counterpart remained unresolved; post-acceptance repair is "
            "correctly forbidden, so completeness failed before relationship execution."
            if first_owner == "PREACCEPTANCE_COMPLETENESS"
            else "relationship first owner could not be proven from this receipt"
        ),
    }


def main() -> int:
    settings = get_settings()
    preflight = _provider_preflight(settings)
    if preflight.get("measurement_validity") != MeasurementValidity.VALID.value:
        print(json.dumps({
            "kind": "dima_v2_day7_relationship_action_diagnostic",
            "measurement_valid": False,
            "provider_preflight": preflight,
            "status": "invalid_measurement",
        }, ensure_ascii=False))
        return 2

    _RAW_CALLS.clear()
    original_builder = _install_recording_builder()
    service = Day7LiveSyntheticService()
    runtime_boundary.wren_for_request = lambda request: service

    app = FastAPI()
    app.include_router(manager_lab_router)
    principal = Principal(
        user_id="day7-live-user",
        tenant_id="day7-live-tenant",
        roles=["owner"],
        tenant_slug=settings.company,
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.state.contracts = LiveContracts()

    records = []
    try:
        with TestClient(app) as client:
            for index, case in enumerate(CASES, start=1):
                _CURRENT_CASE["case_id"] = case["case_id"]
                response = client.post(
                    "/ask-v2-manager-lab",
                    json={
                        "question": case["question"],
                        "session_id": f"day7-relationship-diagnostic-{index}",
                        "thread_id": f"day7-relationship-diagnostic-{index}",
                        "conversation": {},
                    },
                )
                body = response.json()
                receipt = _case_receipt(case, body)
                receipt["status_code"] = response.status_code
                records.append(receipt)
    finally:
        manager_lab_module._build_role_scoped_manager_models = original_builder
        _CURRENT_CASE["case_id"] = None

    payload = {
        "kind": "dima_v2_day7_relationship_action_diagnostic",
        "measurement_valid": True,
        "provider_preflight": preflight,
        "product_behavior_base_sha": PRODUCT_BEHAVIOR_BASE_SHA,
        "product_behavior_changed_by_diagnostic": False,
        "profiles": {
            "research_manager": "openai/gpt-5.6-sol",
            "semantic_linker": "openai/gpt-5.6-luna",
            "temporal_normalizer": "openai/gpt-5.6-sol",
        },
        "workers": 1,
        "service_queries": service.query_calls,
        "records": records,
        "status": "diagnostic_complete",
    }
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
