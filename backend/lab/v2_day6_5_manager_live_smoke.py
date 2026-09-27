"""Day 6.5 live Manager architecture smoke over the manual HTTP boundary.

Real provider + bounded Manager; synthetic semantic/data engine. The oracle checks
authority/tool/terminal behavior, not exact model prose or generated SQL.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

os.environ.setdefault(
    "DIMA_DATABASE_URL",
    "sqlite:///" + str(Path(tempfile.gettempdir()) / "dima-v2-day65-live.db"),
)
os.environ.setdefault("DIMA_JWT_SECRET", "day65-live-public-secret-0123456789abcdef")
os.environ.setdefault("DIMA_JWT_REFRESH_SECRET", "day65-live-refresh-secret-0123456789abcdef")
os.environ.setdefault("DIMA_ADMIN_JWT_SECRET", "day65-live-admin-secret-0123456789abcdef")
os.environ.setdefault(
    "DIMA_ADMIN_JWT_REFRESH_SECRET",
    "day65-live-admin-refresh-secret-0123456789abcdef",
)
os.environ.setdefault("DIMA_SUPERADMIN_IP_ALLOWLIST", "testclient")
os.environ.setdefault("DIMA_V2_MANAGER_LAB_ENABLED", "true")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")
os.environ.setdefault("DIMA_V2_RESEARCH_MANAGER_PROVIDER", "openrouter")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.contracts import result_hash
from app.routers.manager_lab import router as manager_lab_router
import app.v2.runtime_boundary as runtime_boundary
from control_plane.authorize import Principal


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "lab" / "reports" / "v2_day6_5_manager_live_smoke.json"

CUBES = {
    "sales_omega": {
        "display": "Sales Omega",
        "metric": "net_value_x",
        "metric_display": "Net Gelir",
        "metric_synonyms": ["net gelir", "gelir"],
        "dimension": "region_axis_m",
        "dimension_display": "Bölge",
        "dimension_synonyms": ["bölge", "region"],
        "values": ["Kuzey", "Güney", "Batı"],
        "time": "booked_date_z",
    },
    "ops_delta": {
        "display": "Operations Delta",
        "metric": "yield_score_n",
        "metric_display": "Üretkenlik",
        "metric_synonyms": ["üretkenlik", "verimlilik"],
        "dimension": "line_axis_p",
        "dimension_display": "Hat",
        "dimension_synonyms": ["hat", "üretim hattı"],
        "values": ["CELL-Q9", "CELL-R8"],
        "time": "event_date_k",
    },
}


def semantic_schema() -> dict[str, Any]:
    cubes = []
    models = []
    for name, spec in CUBES.items():
        cubes.append(
            {
                "name": name,
                "display": spec["display"],
                "measures": [spec["metric"]],
                "measure_synonyms": {spec["metric"]: spec["metric_synonyms"]},
                "measure_synonyms_display": {spec["metric"]: spec["metric_display"]},
                "units": {spec["metric"]: "TRY" if name == "sales_omega" else "%"},
                "dimensions": [spec["dimension"]],
                "dimension_labels": {spec["dimension"]: spec["dimension_display"]},
                "dimension_synonyms": {spec["dimension"]: spec["dimension_synonyms"]},
                "dimension_values": {spec["dimension"]: spec["values"]},
                "time_dimensions": [spec["time"]],
            }
        )
        models.append(
            {
                "name": f"{name}_source",
                "columns": [
                    {"name": spec["dimension"], "type": "VARCHAR"},
                    {"name": spec["time"], "type": "DATE"},
                ],
            }
        )
    return {
        "catalog": "day65-live-synthetic",
        "schema_name": "main",
        "models": models,
        "cubes": cubes,
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


class LiveSyntheticService:
    mdl_version = "mdl-day65-live-v1"

    def __init__(self) -> None:
        self.query_calls = 0
        self.dry_calls = 0

    def schema(self):
        return semantic_schema()

    def cube_sql(self, cube_query: dict) -> str:
        return "DAY65_SYNTH:" + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        self.dry_calls += 1
        if not sql.startswith("DAY65_SYNTH:"):
            raise RuntimeError("unexpected synthetic plan")
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        cq = json.loads(sql.removeprefix("DAY65_SYNTH:"))
        spec = CUBES[cq["cube"]]
        dims = list(cq.get("dimensions") or ())
        measures = list(cq.get("measures") or ())
        rows = []
        values = list(spec["values"]) if dims else [None]
        for index, value in enumerate(values):
            row: dict[str, Any] = {}
            if dims:
                row[dims[0]] = value
            for metric in measures:
                row[metric] = float(120 - index * 25)
            rows.append(row)
        order = cq.get("order") or {}
        if order.get("measure"):
            rows.sort(
                key=lambda row: row.get(order["measure"], 0),
                reverse=order.get("direction") == "desc",
            )
        if cq.get("limit") is not None:
            rows = rows[: int(cq["limit"])]
        return {
            "columns": [*dims, *measures],
            "rows": rows,
            "row_count": len(rows),
            "column_types": ["VARCHAR" if c in dims else "DOUBLE" for c in [*dims, *measures]],
        }


class LiveContracts:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {
            "id": f"day65-live-contract-{self.n}",
            "result_hash": result_hash(kwargs["result"]),
            "durability": "db",
            "sealed": True,
        }


def _ledger_map(body: dict) -> dict[str, dict]:
    ledger = body.get("ledger") or {}
    return {str(item["obligation_id"]): item for item in ledger.get("items") or []}


def _observation_tools(body: dict) -> list[str]:
    return [
        str(item.get("tool"))
        for item in body.get("observations") or []
        if item.get("kind") == "tool"
    ]


def main() -> int:
    settings = get_settings()
    service = LiveSyntheticService()
    runtime_boundary.wren_for_request = lambda request: service

    app = FastAPI()
    app.include_router(manager_lab_router)
    principal = Principal(
        user_id="day65-live-user",
        tenant_id="day65-live-tenant",
        roles=["owner"],
        tenant_slug=settings.company,
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.state.contracts = LiveContracts()

    cases = [
        {
            "id": "standard-performance",
            "question": "net gelir ne durumda?",
            "expected_terminal": "VERIFIED_COMPLETE",
            "must_tools": {"resolve_semantics", "propose_acceptance", "run_analytics"},
        },
        {
            "id": "standard-ranking",
            "question": "bölgelerde en yüksek 2 net geliri göster",
            "expected_terminal": "VERIFIED_COMPLETE",
            "must_tools": {"resolve_semantics", "propose_acceptance", "run_analytics"},
        },
        {
            "id": "standard-comparison",
            "question": "son 12 ay net geliri geçen 12 ayla karşılaştır",
            "expected_terminal": "VERIFIED_COMPLETE",
            "must_tools": {"resolve_semantics", "propose_acceptance", "run_analytics"},
        },
        {
            "id": "relationship-unavailable",
            "question": "üretkenlik ile hat ilişkisini incele",
            "expected_terminal": "PARTIAL",
            "must_tools": {"resolve_semantics", "propose_acceptance", "run_relationship"},
        },
    ]

    records: list[dict[str, Any]] = []
    canonical_markers = {
        "net_value_x",
        "region_axis_m",
        "booked_date_z",
        "yield_score_n",
        "line_axis_p",
        "event_date_k",
    }

    with TestClient(app) as client:
        for index, case in enumerate(cases, start=1):
            payload = {
                "question": case["question"],
                "session_id": f"day65-live-session-{index}",
                "thread_id": f"day65-live-thread-{index}",
                "conversation": {},
            }
            started = time.perf_counter()
            response = client.post("/ask-v2-manager-lab", json=payload)
            elapsed = time.perf_counter() - started
            try:
                body = response.json()
            except Exception:
                body = {}

            tools = _observation_tools(body)
            terminal = body.get("terminal_status")
            observations_blob = json.dumps(
                body.get("observations") or [],
                ensure_ascii=False,
                sort_keys=True,
            )
            no_canonical_leak = not any(marker in observations_blob for marker in canonical_markers)
            ledger = _ledger_map(body)
            relationship_unsupported = True
            if case["id"] == "relationship-unavailable":
                relationship_unsupported = any(
                    item.get("status") == "UNSUPPORTED" for item in ledger.values()
                )

            checks = {
                "http_200": response.status_code == 200,
                "terminal": terminal == case["expected_terminal"],
                "run_finished": body.get("run_finished") is True,
                "tools_present": case["must_tools"].issubset(set(tools)),
                "accepted_contract": bool((body.get("snapshot") or {}).get("accepted_contract_id")),
                "canonical_not_leaked": no_canonical_leak,
                "turn_budget": int((body.get("snapshot") or {}).get("manager_turns") or 0) <= 8,
                "relationship_typed_unsupported": relationship_unsupported,
            }
            if case["expected_terminal"] == "VERIFIED_COMPLETE":
                checks["verified_complete"] = body.get("verified_complete") is True
            else:
                checks["verified_complete_false"] = body.get("verified_complete") is False

            records.append(
                {
                    "case_id": case["id"],
                    "question": case["question"],
                    "status_code": response.status_code,
                    "latency_s": round(elapsed, 4),
                    "terminal_status": terminal,
                    "tools": tools,
                    "manager_turns": (body.get("snapshot") or {}).get("manager_turns"),
                    "checks": checks,
                    "pass": all(checks.values()),
                    "observations": body.get("observations"),
                    "ledger": body.get("ledger"),
                }
            )

    gates = {
        "all_cases_pass": all(item["pass"] for item in records),
        "no_500": all(item["status_code"] < 500 for item in records),
        "canonical_leak_zero": all(item["checks"]["canonical_not_leaked"] for item in records),
    }
    payload = {
        "kind": "dima_v2_day6_5_manager_live_smoke",
        "provider": "openrouter",
        "model": getattr(settings, "v2_research_manager_model", None)
        or getattr(settings, "v2_reference_language_model", None)
        or getattr(settings, "openrouter_model", None),
        "source_policy": "real_provider_synthetic_semantic_engine_manual_only",
        "records": records,
        "gates": gates,
        "status": "pass" if all(gates.values()) else "fail",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
