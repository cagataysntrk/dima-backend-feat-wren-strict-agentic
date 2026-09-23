"""Manual-only Day7 focused LIVE SOL evaluation.

Real RESEARCH_MANAGER cognition runs through the current ManagerLabHarness and Day7
trust plane. The semantic/data engine is deterministic synthetic Wren-compatible
infrastructure so the run measures Manager orchestration rather than external DB drift.

This file is never push-triggered. Use the workflow_dispatch Day7 live workflow.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "eval" / "v2_day7_live_sol_cases.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day7_live_sol.json"

LIVE_MANAGER_MODEL = os.getenv("DIMA_DAY7_LIVE_MANAGER_MODEL", "openai/gpt-5.6-sol")
LIVE_LINKER_MODEL = os.getenv("DIMA_DAY7_LIVE_LINKER_MODEL", "openai/gpt-5.6-luna")
LIVE_TEMPORAL_MODEL = os.getenv("DIMA_DAY7_LIVE_TEMPORAL_MODEL", "openai/gpt-5.6-luna")

os.environ.setdefault(
    "DIMA_DATABASE_URL",
    "sqlite:///" + str(Path(tempfile.gettempdir()) / "dima-v2-day7-live.db"),
)
os.environ.setdefault("DIMA_JWT_SECRET", "day7-live-public-secret-0123456789abcdef")
os.environ.setdefault("DIMA_JWT_REFRESH_SECRET", "day7-live-refresh-secret-0123456789abcdef")
os.environ.setdefault("DIMA_ADMIN_JWT_SECRET", "day7-live-admin-secret-0123456789abcdef")
os.environ.setdefault(
    "DIMA_ADMIN_JWT_REFRESH_SECRET",
    "day7-live-admin-refresh-secret-0123456789abcdef",
)
os.environ.setdefault("DIMA_SUPERADMIN_IP_ALLOWLIST", "testclient")
os.environ.setdefault("DIMA_V2_MANAGER_LAB_ENABLED", "true")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")
os.environ.setdefault("DIMA_LLM_PROVIDER", "openrouter")
os.environ.setdefault("DIMA_V2_RESEARCH_MANAGER_PROVIDER", "openrouter")
os.environ["DIMA_V2_RESEARCH_MANAGER_MODEL"] = LIVE_MANAGER_MODEL
os.environ.setdefault("DIMA_V2_SEMANTIC_LINKER_PROVIDER", "openrouter")
os.environ["DIMA_V2_SEMANTIC_LINKER_MODEL"] = LIVE_LINKER_MODEL
os.environ.setdefault("DIMA_V2_TEMPORAL_NORMALIZER_PROVIDER", "openrouter")
os.environ["DIMA_V2_TEMPORAL_NORMALIZER_MODEL"] = LIVE_TEMPORAL_MODEL

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.contracts import result_hash
from app.routers.manager_lab import router as manager_lab_router
import app.v2.runtime_boundary as runtime_boundary
from control_plane.authorize import Principal


MDL_VERSION = "mdl-day7-live-v1"

SALES_METRICS = {
    "net_value_x": {
        "display": "Net Gelir",
        "synonyms": ["net gelir", "gelir"],
        "unit": "TRY",
    },
    "gross_value_y": {
        "display": "Brüt Gelir",
        "synonyms": ["brüt gelir", "brut gelir"],
        "unit": "TRY",
    },
    "order_count_k": {
        "display": "Sipariş Sayısı",
        "synonyms": ["sipariş sayısı", "sipariş adedi"],
        "unit": "adet",
    },
    "stable_margin_s": {
        "display": "İstikrarlı Marj",
        "synonyms": ["istikrarlı marj", "stabil marj"],
        "unit": "%",
    },
    "sparse_signal_q": {
        "display": "Seyrek Sinyal",
        "synonyms": ["seyrek sinyal"],
        "unit": "puan",
    },
}

SALES_DIMS = {
    "region_axis_m": {
        "display": "Bölge",
        "synonyms": ["bölge", "bölgeler", "region"],
        "values": ["Kuzey", "Güney", "Batı"],
    },
    "product_axis_n": {
        "display": "Ürün",
        "synonyms": ["ürün", "ürünler", "product"],
        "values": [f"ÜRÜN-{i:02d}" for i in range(1, 13)],
    },
    "channel_axis_c": {
        "display": "Kanal",
        "synonyms": ["kanal", "kanallar", "channel"],
        "values": ["Online", "Bayi", "Kurumsal"],
    },
}

OPS_METRICS = {
    "downtime_min_d": {
        "display": "Duruş Süresi",
        "synonyms": ["duruş süresi", "durus suresi"],
        "unit": "dakika",
    },
    "yield_score_n": {
        "display": "Üretkenlik",
        "synonyms": ["üretkenlik", "verimlilik"],
        "unit": "%",
    },
}

OPS_DIMS = {
    "line_axis_p": {
        "display": "Hat",
        "synonyms": ["hat", "üretim hattı"],
        "values": ["LINE-1", "LINE-2", "LINE-3"],
    },
    "department_axis_d": {
        "display": "Bölüm",
        "synonyms": ["bölüm", "bölümler", "departman"],
        "values": ["Kesim", "Montaj", "Paketleme"],
    },
}


def _fanout_proof(name: str) -> dict[str, Any]:
    return {
        "relationship": name,
        "status": "HEALTHY",
        "certified": "olculdu:saglikli",
        "certificate_mdl_version": MDL_VERSION,
        "current_mdl_version": MDL_VERSION,
        "measured_at": "2026-09-23T00:00:00+00:00",
    }


def semantic_schema() -> dict[str, Any]:
    relationship_name = "ops_events_line_master"
    return {
        "catalog": "day7-live-synthetic",
        "schema_name": "main",
        "models": [
            {
                "name": "sales_events",
                "primary_key": "sale_id",
                "columns": [
                    {"name": "sale_id", "type": "VARCHAR", "is_primary_key": True},
                    *[
                        {"name": name, "type": "VARCHAR"}
                        for name in SALES_DIMS
                    ],
                    {"name": "booked_date_z", "type": "DATE"},
                ],
            },
            {
                "name": "ops_events",
                "primary_key": "event_id",
                "columns": [
                    {"name": "event_id", "type": "VARCHAR", "is_primary_key": True},
                    {"name": "line_id", "type": "VARCHAR"},
                    {"name": "event_date_k", "type": "DATE"},
                ],
            },
            {
                "name": "line_master",
                "primary_key": "line_id",
                "columns": [
                    {"name": "line_id", "type": "VARCHAR", "is_primary_key": True},
                    {"name": "department", "type": "VARCHAR"},
                ],
            },
        ],
        "cubes": [
            {
                "name": "sales_omega",
                "display": "Sales Omega",
                "base_object": "sales_events",
                "measures": list(SALES_METRICS),
                "measure_synonyms": {
                    name: spec["synonyms"] for name, spec in SALES_METRICS.items()
                },
                "measure_synonyms_display": {
                    name: spec["display"] for name, spec in SALES_METRICS.items()
                },
                "units": {
                    name: spec["unit"] for name, spec in SALES_METRICS.items()
                },
                "dimensions": list(SALES_DIMS),
                "dimension_labels": {
                    name: spec["display"] for name, spec in SALES_DIMS.items()
                },
                "dimension_synonyms": {
                    name: spec["synonyms"] for name, spec in SALES_DIMS.items()
                },
                "dimension_values": {
                    name: spec["values"] for name, spec in SALES_DIMS.items()
                },
                "time_dimensions": ["booked_date_z"],
            },
            {
                "name": "ops_delta",
                "display": "Operations Delta",
                "base_object": "ops_events",
                "measures": list(OPS_METRICS),
                "measure_synonyms": {
                    name: spec["synonyms"] for name, spec in OPS_METRICS.items()
                },
                "measure_synonyms_display": {
                    name: spec["display"] for name, spec in OPS_METRICS.items()
                },
                "units": {
                    name: spec["unit"] for name, spec in OPS_METRICS.items()
                },
                "dimensions": list(OPS_DIMS),
                "dimension_labels": {
                    name: spec["display"] for name, spec in OPS_DIMS.items()
                },
                "dimension_synonyms": {
                    name: spec["synonyms"] for name, spec in OPS_DIMS.items()
                },
                "dimension_values": {
                    name: spec["values"] for name, spec in OPS_DIMS.items()
                },
                "time_dimensions": ["event_date_k"],
                "dimension_origin": {
                    "department_axis_d": {
                        "model": "line_master",
                        "column": "department",
                        "relationship": relationship_name,
                        "hops": 1,
                    }
                },
            },
        ],
        "kpis": [],
        "relationships": [
            {
                "name": relationship_name,
                "models": ["ops_events", "line_master"],
                "join_type": "MANY_TO_ONE",
                "condition": 'ops_events."line_id" = line_master."line_id"',
                "certified": "olculdu:saglikli",
                "fanout_proof": _fanout_proof(relationship_name),
            }
        ],
        "business_rules": "",
        "db_online": True,
    }


class Day7LiveSyntheticService:
    mdl_version = MDL_VERSION

    def __init__(self) -> None:
        self.query_calls = 0
        self.dry_calls = 0

    def schema(self):
        return semantic_schema()

    def cube_sql(self, cube_query: dict) -> str:
        return "DAY7_LIVE:" + json.dumps(
            cube_query,
            ensure_ascii=False,
            sort_keys=True,
        )

    def dry_plan(self, sql: str, *, principal=None):
        if principal is None:
            raise RuntimeError("principal required")
        self.dry_calls += 1
        if not sql.startswith("DAY7_LIVE:"):
            raise RuntimeError("unexpected synthetic plan")
        return sql

    @staticmethod
    def _dimension_values(cube: str, dimension: str) -> list[str]:
        if cube == "sales_omega":
            return list(SALES_DIMS.get(dimension, {}).get("values") or ["ALL"])
        if cube == "ops_delta":
            return list(OPS_DIMS.get(dimension, {}).get("values") or ["ALL"])
        return ["ALL"]

    @staticmethod
    def _metric_value(metric: str, index: int, dimension: str | None) -> float:
        if metric == "stable_margin_s":
            values = [100.0, 101.0, 99.0, 100.5]
            return values[index % len(values)]
        if metric == "order_count_k":
            return float(max(1, 60 - index * 4))
        if metric == "gross_value_y":
            return float(max(10, 220 - index * 13))
        if metric == "downtime_min_d":
            return float(max(5, 180 - index * 55))
        if metric == "yield_score_n":
            return float(min(99, 72 + index * 8))
        # net_value_x is intentionally materially uneven for adaptive cases.
        if dimension == "region_axis_m":
            values = [180.0, 58.0, 42.0]
            return values[index % len(values)]
        if dimension == "product_axis_n":
            return float(max(8, 210 - index * 16))
        return float(max(10, 150 - index * 12))

    def query(self, sql: str, limit=None, *, principal=None):
        if principal is None:
            raise RuntimeError("principal required")
        self.query_calls += 1
        query = json.loads(sql.removeprefix("DAY7_LIVE:"))
        cube = str(query["cube"])
        measures = list(query.get("measures") or ())
        dimensions = list(query.get("dimensions") or ())

        if "sparse_signal_q" in measures:
            return {
                "columns": [*dimensions, *measures],
                "rows": [],
                "row_count": 0,
                "column_types": [
                    *["VARCHAR" for _ in dimensions],
                    *["DOUBLE" for _ in measures],
                ],
            }

        driver = dimensions[0] if dimensions else None
        dim_values = self._dimension_values(cube, driver) if driver else [None]
        rows: list[dict[str, Any]] = []
        for index, value in enumerate(dim_values):
            row: dict[str, Any] = {}
            for dimension in dimensions:
                row[dimension] = (
                    value
                    if dimension == driver
                    else self._dimension_values(cube, dimension)[
                        index % len(self._dimension_values(cube, dimension))
                    ]
                )
            for metric in measures:
                row[metric] = self._metric_value(metric, index, driver)
            rows.append(row)

        order = query.get("order") or {}
        measure = order.get("measure")
        if measure:
            rows.sort(
                key=lambda row: row.get(measure, 0),
                reverse=str(order.get("direction") or "desc") == "desc",
            )
        effective_limit = query.get("limit")
        if effective_limit is not None:
            rows = rows[: int(effective_limit)]

        return {
            "columns": [*dimensions, *measures],
            "rows": rows,
            "row_count": len(rows),
            "column_types": [
                *["VARCHAR" for _ in dimensions],
                *["DOUBLE" for _ in measures],
            ],
        }


class LiveContracts:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {
            "id": f"day7-live-qc-{self.n}",
            "result_hash": result_hash(kwargs["result"]),
            "durability": "lab",
            "sealed": True,
        }


def _ledger_items(body: dict[str, Any]) -> list[dict[str, Any]]:
    return list((body.get("ledger") or {}).get("items") or [])


def _tool_observations(body: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in body.get("observations") or []
        if item.get("kind") == "tool"
    ]


def _fanout_observations(body: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in body.get("observations") or []
        if item.get("kind") == "fanout_registered"
    ]


def _case_checks(
    case: dict[str, Any],
    *,
    response,
    body: dict[str, Any],
    query_delta: int,
) -> dict[str, bool]:
    snapshot = body.get("snapshot") or {}
    tools = _tool_observations(body)
    tool_names = [str(item.get("tool")) for item in tools]
    ledger = _ledger_items(body)
    user_must = [
        item
        for item in ledger
        if item.get("origin") == "USER_MUST"
        and item.get("polarity") == "REQUIRED"
    ]
    executed_task_ids = [
        str(item.get("research_task_id"))
        for item in tools
        if item.get("research_task_id")
    ]
    derived_executions = [
        task_id
        for task_id in executed_task_ids
        if not task_id.startswith("seed:")
    ]
    fanouts = _fanout_observations(body)
    max_selected = max(
        [
            len((item.get("result") or {}).get("selected_task_ids") or [])
            for item in fanouts
        ]
        or [0]
    )
    zero_row_seen = any(
        int((item.get("result") or {}).get("row_count") or -1) == 0
        for item in tools
        if item.get("tool") == "run_analytics"
    )
    typed_block_seen = any(
        item.get("status") in {
            "BLOCKED_DATA_GAP",
            "LIMITED",
            "UNSUPPORTED",
        }
        for item in ledger
    )
    budget_exhausted = snapshot.get("state") == "BUDGET_EXHAUSTED"

    checks: dict[str, bool] = {
        "http_200": response.status_code == 200,
        "accepted_contract": bool(snapshot.get("accepted_contract_id")),
        "manager_turn_cap": int(snapshot.get("manager_turns") or 0) <= 6,
        "tool_call_cap": int(snapshot.get("tool_calls") or 0) <= 12,
        "data_query_cap": int(snapshot.get("data_queries") or 0) <= 8,
        "service_query_cap": query_delta <= int(case.get("max_queries", 8)),
        "must_tools": set(case.get("must_tools") or ()).issubset(set(tool_names)),
        "min_user_must": len(user_must) >= int(case.get("min_user_must", 1)),
        "no_failed_runtime": snapshot.get("state") != "FAILED",
    }

    expected_terminal = case.get("expected_terminal")
    if expected_terminal:
        checks["expected_terminal"] = body.get("terminal_status") == expected_terminal
        checks["expected_finished"] = body.get("run_finished") is True

    if case.get("require_typed_block"):
        checks["typed_block"] = typed_block_seen
        checks["unsafe_relationship_not_verified"] = not any(
            item.get("capability_key") == "relationship"
            and item.get("status") == "VERIFIED"
            for item in ledger
        )

    if case.get("expect_evidence_inspection"):
        checks["evidence_inspected"] = bool(snapshot.get("inspected_evidence_refs"))

    if "max_derived_executions" in case:
        checks["derived_execution_bound"] = (
            len(derived_executions) <= int(case["max_derived_executions"])
        )

    if "max_fanout_selected" in case:
        checks["fanout_bound"] = max_selected <= int(case["max_fanout_selected"])

    if case.get("require_unique_task_side_effects"):
        # This case uses only one-query Standard tasks; duplicate delivery may be
        # observed but must not create a second DB side effect.
        checks["unique_task_side_effects"] = query_delta <= len(set(executed_task_ids))

    if case.get("require_zero_row_observation"):
        checks["zero_row_observed"] = zero_row_seen

    if case.get("allow_budget_exhausted"):
        checks["budget_disclosed_if_exhausted"] = (
            not budget_exhausted
            or (
                body.get("run_finished") is False
                and body.get("terminal_status") != "VERIFIED_COMPLETE"
            )
        )
    else:
        checks["not_budget_exhausted"] = not budget_exhausted

    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case-id", action="append", default=[])
    args = parser.parse_args()

    document = yaml.safe_load(args.cases.read_text(encoding="utf-8"))
    cases = list(document.get("cases") or [])
    selected = set(args.case_id)
    if selected:
        cases = [case for case in cases if str(case["id"]) in selected]
    if not cases:
        raise SystemExit("No Day7 live cases selected")

    settings = get_settings()
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

    records: list[dict[str, Any]] = []
    with TestClient(app) as client:
        for index, case in enumerate(cases, start=1):
            before = service.query_calls
            started = time.perf_counter()
            response = client.post(
                "/ask-v2-manager-lab",
                json={
                    "question": case["question"],
                    "session_id": f"day7-live-session-{index}",
                    "thread_id": f"day7-live-thread-{index}",
                    "conversation": {},
                },
            )
            latency = time.perf_counter() - started
            try:
                body = response.json()
            except Exception:
                body = {}
            query_delta = service.query_calls - before
            checks = _case_checks(
                case,
                response=response,
                body=body,
                query_delta=query_delta,
            )
            observations = list(body.get("observations") or [])
            model_errors = [
                item for item in observations
                if item.get("kind") == "model_error"
            ]
            records.append(
                {
                    "case_id": case["id"],
                    "kind": case["kind"],
                    "question": case["question"],
                    "latency_s": round(latency, 4),
                    "status_code": response.status_code,
                    "terminal_status": body.get("terminal_status"),
                    "snapshot": body.get("snapshot"),
                    "query_delta": query_delta,
                    "checks": checks,
                    "behavior_pass": all(checks.values()),
                    "model_errors": model_errors,
                    "observations": observations,
                    "ledger": body.get("ledger"),
                }
            )

    hard_keys = {
        "http_200",
        "accepted_contract",
        "manager_turn_cap",
        "tool_call_cap",
        "data_query_cap",
        "service_query_cap",
        "no_failed_runtime",
        "typed_block",
        "unsafe_relationship_not_verified",
        "unique_task_side_effects",
        "budget_disclosed_if_exhausted",
    }
    hard_failures = [
        {
            "case_id": record["case_id"],
            "failed": [
                key
                for key, passed in record["checks"].items()
                if key in hard_keys and not passed
            ],
        }
        for record in records
        if any(
            key in hard_keys and not passed
            for key, passed in record["checks"].items()
        )
    ]
    model_failure_cases = [
        record["case_id"] for record in records if record["model_errors"]
    ]
    behavior_passes = sum(int(record["behavior_pass"]) for record in records)
    payload = {
        "kind": "dima_v2_day7_live_sol",
        "corpus_version": document.get("version"),
        "source_policy": (
            "real_provider_current_day7_manager_trust_plane_"
            "deterministic_synthetic_semantic_data_engine"
        ),
        "workers": 1,
        "profiles": {
            "research_manager": LIVE_MANAGER_MODEL,
            "semantic_linker": LIVE_LINKER_MODEL,
            "temporal_normalizer": LIVE_TEMPORAL_MODEL,
        },
        "case_count": len(records),
        "behavior_pass_count": behavior_passes,
        "behavior_pass_rate": round(behavior_passes / len(records), 4),
        "hard_safety_failures": hard_failures,
        "model_failure_cases": model_failure_cases,
        "total_service_queries": service.query_calls,
        "total_latency_s": round(
            sum(float(record["latency_s"]) for record in records),
            4,
        ),
        "records": records,
        "status": (
            "pass"
            if behavior_passes == len(records)
            and not hard_failures
            and not model_failure_cases
            else "fail"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
