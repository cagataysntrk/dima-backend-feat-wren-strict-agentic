"""Day 5 live Core MVP attack table over the real /ask-v2 HTTP boundary.

This is intentionally not a demo-database benchmark. The Wren-facing service is a small
synthetic semantic engine with opaque canonical identifiers. Natural-language understanding
uses the configured real provider. Oracles are independent semantic requirements/state,
not generated SQL text.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any

# Isolated control-plane state must be selected before importing app/control-plane modules.
os.environ.setdefault(
    "DIMA_DATABASE_URL",
    "sqlite:///" + str(Path(tempfile.gettempdir()) / "dima-v2-day5-live.db"),
)
os.environ.setdefault("DIMA_JWT_SECRET", "day5-live-public-secret-0123456789abcdef")
os.environ.setdefault("DIMA_JWT_REFRESH_SECRET", "day5-live-refresh-secret-0123456789abcdef")
os.environ.setdefault("DIMA_ADMIN_JWT_SECRET", "day5-live-admin-secret-0123456789abcdef")
os.environ.setdefault(
    "DIMA_ADMIN_JWT_REFRESH_SECRET",
    "day5-live-admin-refresh-secret-0123456789abcdef",
)
os.environ.setdefault("DIMA_SUPERADMIN_IP_ALLOWLIST", "testclient")
os.environ.setdefault("DIMA_ASK_V2_ENABLED", "true")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_principal
from app.config import get_settings
from app.contracts import result_hash
from app.llm import build_generator
from app.routers.ask_v2 import router as ask_v2_router
import app.v2.orchestrator as orchestrator_module
from control_plane.authorize import Principal


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "lab" / "reports" / "v2_day5_live_attack.json"
CUBES = {
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
    "sales_omega": {
        "display": "Sales Omega",
        "metric": "net_value_x",
        "metric_display": "Net Gelir",
        "metric_synonyms": ["net gelir", "gelir"],
        "dimension": "region_axis_m",
        "dimension_display": "Bölge",
        "dimension_synonyms": ["bölge", "region"],
        "values": ["Kuzey", "Güney"],
        "time": "booked_date_z",
    },
    "risk_tau": {
        "display": "Risk Tau",
        "metric": "loss_score_v",
        "metric_display": "Kayıp",
        "metric_synonyms": ["kayıp", "loss"],
        "dimension": "segment_axis_s",
        "dimension_display": "Segment",
        "dimension_synonyms": ["segment"],
        "values": ["Prime"],
        "other_dimension": "account_axis_a",
        "other_dimension_display": "Hesap",
        "other_dimension_synonyms": ["hesap"],
        "other_values": ["Prime"],
        "time": "risk_date_j",
    },
}


def semantic_schema() -> dict[str, Any]:
    cubes = []
    models = []
    for name, spec in CUBES.items():
        dimensions = [spec["dimension"]]
        labels = {spec["dimension"]: spec["dimension_display"]}
        synonyms = {spec["dimension"]: spec["dimension_synonyms"]}
        values = {spec["dimension"]: spec["values"]}
        columns = [
            {"name": spec["dimension"], "type": "VARCHAR"},
            {"name": spec["time"], "type": "DATE"},
        ]
        if spec.get("other_dimension"):
            dimensions.append(spec["other_dimension"])
            labels[spec["other_dimension"]] = spec["other_dimension_display"]
            synonyms[spec["other_dimension"]] = spec["other_dimension_synonyms"]
            values[spec["other_dimension"]] = spec["other_values"]
            columns.append({"name": spec["other_dimension"], "type": "VARCHAR"})

        cubes.append({
            "name": name,
            "display": spec["display"],
            "measures": [spec["metric"]],
            "measure_synonyms": {spec["metric"]: spec["metric_synonyms"]},
            "measure_synonyms_display": {spec["metric"]: spec["metric_display"]},
            "units": {spec["metric"]: "%"},
            "dimensions": dimensions,
            "dimension_labels": labels,
            "dimension_synonyms": synonyms,
            "dimension_values": values,
            "time_dimensions": [spec["time"]],
        })
        models.append({"name": f"{name}_source", "columns": columns})

    return {
        "catalog": "day5-live-synthetic",
        "schema_name": "main",
        "models": models,
        "cubes": cubes,
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


class LiveSyntheticService:
    mdl_version = "mdl-day5-live-v1"

    def __init__(self) -> None:
        self.query_calls = 0
        self.dry_calls = 0
        self.principals: list[tuple[str, Any]] = []

    def schema(self):
        return semantic_schema()

    def cube_sql(self, cube_query: dict) -> str:
        return "LIVE_SYNTH:" + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        self.dry_calls += 1
        self.principals.append(("dry", principal))
        if not sql.startswith("LIVE_SYNTH:"):
            raise RuntimeError("unexpected synthetic plan")
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        self.principals.append(("query", principal))
        query = json.loads(sql.removeprefix("LIVE_SYNTH:"))
        cube_name = query["cube"]
        spec = CUBES[cube_name]
        dims = list(query.get("dimensions") or ())
        measures = list(query.get("measures") or ())
        columns = [*dims, *measures]

        values = list(spec["values"])
        for flt in query.get("filters") or ():
            if flt.get("operator") == "eq" and flt.get("dimension") in dims:
                values = [flt.get("value")]
            elif flt.get("operator") == "in" and flt.get("dimension") in dims:
                values = list(flt.get("value") or ())

        rows = []
        for index, value in enumerate(values or [None]):
            row: dict[str, Any] = {}
            if dims:
                row[dims[0]] = value
            for metric in measures:
                # Fixed fixture facts. The evaluator never recomputes these values.
                row[metric] = float(91 - index * 17)
            rows.append(row)

        order = query.get("order") or {}
        if order.get("measure"):
            rows.sort(
                key=lambda row: row.get(order["measure"], 0),
                reverse=order.get("direction") == "desc",
            )
        if query.get("limit") is not None:
            rows = rows[: int(query["limit"])]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_types": ["VARCHAR" if c in dims else "DOUBLE" for c in columns],
        }


class LiveContracts:
    def __init__(self) -> None:
        self.n = 0

    def record_v2_minimum(self, **kwargs):
        self.n += 1
        return {
            "id": f"day5-live-contract-{self.n}",
            "result_hash": result_hash(kwargs["result"]),
            "durability": "db",
            "sealed": True,
        }


def p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def main() -> int:
    settings = get_settings()
    service = LiveSyntheticService()
    orchestrator_module.wren_for_request = lambda request: service

    app = FastAPI()
    app.include_router(ask_v2_router)
    principal = Principal(
        user_id="day5-live-user",
        tenant_id="day5-live-tenant",
        roles=["owner"],
        tenant_slug=get_settings().company,
    )
    # Override only identity. Permission + company dependencies remain real and
    # consume the same Principal through FastAPI's nested dependency graph.
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.state.llm = build_generator(settings)
    app.state.contracts = LiveContracts()

    records: list[dict[str, Any]] = []
    standard_latencies: list[float] = []
    clarify_latencies: list[float] = []
    silent_wrong = 0
    unhandled_500 = 0

    def record(
        name: str,
        response,
        elapsed: float,
        checks: dict[str, bool],
        *,
        latency_class: str | None = None,
    ) -> dict[str, Any] | None:
        nonlocal silent_wrong, unhandled_500
        body: dict[str, Any] | None
        try:
            body = response.json()
        except Exception:
            body = None
        if response.status_code >= 500:
            unhandled_500 += 1
        wrong_official = bool(
            body
            and body.get("official_verified")
            and not all(checks.values())
        )
        silent_wrong += int(wrong_official)
        ok = response.status_code == 200 and all(checks.values())
        records.append({
            "attack": name,
            "status_code": response.status_code,
            "latency_s": round(elapsed, 4),
            "checks": checks,
            "official_verified": body.get("official_verified") if body else None,
            "response_kind": (body.get("response") or {}).get("kind") if body else None,
            "failure": body.get("failure") if body else None,
            "turn": body.get("turn") if body else None,
            "analytics_ir": body.get("analytics_ir") if body else None,
            "hypotheses": body.get("hypotheses") if body else None,
            "pass": ok,
        })
        if latency_class == "standard" and response.status_code == 200:
            standard_latencies.append(elapsed)
        if latency_class == "clarify" and response.status_code == 200:
            clarify_latencies.append(elapsed)
        return body

    def post(client: TestClient, question: str, *, conversation=None, token=None):
        payload = {
            "question": question,
            "session_id": "day5-live-session",
            "thread_id": "day5-live-thread",
            "conversation": conversation or {},
        }
        if token is not None:
            payload["clarification_token"] = token
        started = time.perf_counter()
        response = client.post("/ask-v2", json=payload)
        return response, time.perf_counter() - started

    with TestClient(app) as client:
        # 1 — paraphrase/morphology: canonical ids are not present in the question.
        response, elapsed = post(client, "bu ay hatlara göre üretkenlik nasıl gidiyor?")
        body = response.json() if response.status_code == 200 else {}
        ir = body.get("analytics_ir") or {}
        record("paraphrase", response, elapsed, {
            "answer": (body.get("response") or {}).get("kind") == "answer",
            "cube": ir.get("cube") == "ops_delta",
            "metric": [x.get("canonical_name") for x in ir.get("metrics") or []] == ["yield_score_n"],
            "dimension": [x.get("canonical_name") for x in ir.get("dimensions") or []] == ["line_axis_p"],
            "time": (ir.get("period") or {}).get("kind") == "this_month",
            "evidence": bool((body.get("response") or {}).get("evidence_refs")),
        }, latency_class="standard")

        # 2 — typo: two independent surface corruptions.
        response, elapsed = post(client, "bu ay bolge bazında net gelr ne durumda?")
        body = response.json() if response.status_code == 200 else {}
        ir = body.get("analytics_ir") or {}
        typo_kind = (body.get("response") or {}).get("kind")
        typo_safe_clarify = (
            typo_kind == "clarify"
            and body.get("query_execution_count") == 0
            and body.get("official_verified") is False
        )
        typo_safe_answer = (
            typo_kind == "answer"
            and ir.get("cube") == "sales_omega"
            and [x.get("canonical_name") for x in ir.get("metrics") or []] == ["net_value_x"]
            and [x.get("canonical_name") for x in ir.get("dimensions") or []] == ["region_axis_m"]
            and (ir.get("period") or {}).get("kind") == "this_month"
        )
        record("typo", response, elapsed, {
            "safe_resolve_or_clarify": typo_safe_answer or typo_safe_clarify,
            "no_silent_wrong": not (
                body.get("official_verified") is True and not typo_safe_answer
            ),
        }, latency_class="standard")

        # 3 — ranking + comparison: all material requirements must survive.
        response, elapsed = post(
            client,
            "bu ay bölgelerde en yüksek 2 net gelir, geçen ayla kıyasla",
        )
        body = response.json() if response.status_code == 200 else {}
        ir = body.get("analytics_ir") or {}
        ranking = ir.get("ranking") or {}
        comparison = ir.get("comparison") or {}
        record("ranking_comparison", response, elapsed, {
            "answer": (body.get("response") or {}).get("kind") == "answer",
            "cube": ir.get("cube") == "sales_omega",
            "ranking_direction": ranking.get("direction") == "desc",
            "ranking_limit": ranking.get("limit") == 2,
            "comparison": comparison.get("mode") == "previous_period",
            "two_queries": body.get("query_execution_count") == 2,
            "two_evidence": len((body.get("response") or {}).get("evidence_refs") or []) == 2,
        }, latency_class="standard")

        # 4 — blocking ambiguity must clarify, not guess.
        response, elapsed = post(client, "Prime için kayıp ne durumda?")
        body = response.json() if response.status_code == 200 else {}
        chips = (body.get("response") or {}).get("clarification_chips") or []
        record("ambiguity", response, elapsed, {
            "clarify": (body.get("response") or {}).get("kind") == "clarify",
            "query_zero": body.get("query_execution_count") == 0,
            "candidate_count": len(chips) >= 2,
            "not_official": body.get("official_verified") is False,
        }, latency_class="clarify")

        # 5 — signed resume patches only the pending slot.
        if chips:
            segment_chip = next(
                (chip for chip in chips if str(chip.get("label", "")).startswith("Segment")),
                chips[0],
            )
            response, elapsed = post(
                client,
                str(segment_chip["label"]),
                conversation=body.get("conversation") or {},
                token=str(segment_chip["token"]),
            )
            resumed = response.json() if response.status_code == 200 else {}
            resumed_ir = resumed.get("analytics_ir") or {}
            record("clarification_resume", response, elapsed, {
                "answer": (resumed.get("response") or {}).get("kind") == "answer",
                "query_once": resumed.get("query_execution_count") == 1,
                "metric_preserved": [x.get("canonical_name") for x in resumed_ir.get("metrics") or []] == ["loss_score_v"],
                "filter_bound": bool(resumed_ir.get("filters")),
            }, latency_class="standard")
        else:
            records.append({
                "attack": "clarification_resume",
                "status_code": None,
                "latency_s": None,
                "checks": {"blocking_ambiguity_did_not_produce_chips": False},
                "official_verified": None,
                "response_kind": None,
                "failure": None,
                "pass": False,
            })

        # 6 — natural multi-turn repair/follow-up/explain/social thread.
        conversation: dict[str, Any] = {}
        response, elapsed = post(client, "bu yıl hatlara göre üretkenlik nasıl?", conversation=conversation)
        body = response.json() if response.status_code == 200 else {}
        conversation = body.get("conversation") or {}
        base_ir = body.get("analytics_ir") or {}
        record("thread_base", response, elapsed, {
            "answer": (body.get("response") or {}).get("kind") == "answer",
            "cube": base_ir.get("cube") == "ops_delta",
        }, latency_class="standard")

        response, elapsed = post(client, "yalnız CELL-Q9 kalsın", conversation=conversation)
        body = response.json() if response.status_code == 200 else {}
        conversation = body.get("conversation") or conversation
        filtered_ir = body.get("analytics_ir") or {}
        record("followup_filter", response, elapsed, {
            "answer": (body.get("response") or {}).get("kind") == "answer",
            "metric_preserved": [x.get("canonical_name") for x in filtered_ir.get("metrics") or []] == ["yield_score_n"],
            "dimension_preserved": [x.get("canonical_name") for x in filtered_ir.get("dimensions") or []] == ["line_axis_p"],
            "filter": [x.get("value") for x in filtered_ir.get("filters") or []] == ["CELL-Q9"],
        }, latency_class="standard")

        response, elapsed = post(client, "yok, son üç ay olsun", conversation=conversation)
        body = response.json() if response.status_code == 200 else {}
        conversation = body.get("conversation") or conversation
        repaired_ir = body.get("analytics_ir") or {}
        record("repair", response, elapsed, {
            "answer": (body.get("response") or {}).get("kind") == "answer",
            "metric_preserved": [x.get("canonical_name") for x in repaired_ir.get("metrics") or []] == ["yield_score_n"],
            "dimension_preserved": [x.get("canonical_name") for x in repaired_ir.get("dimensions") or []] == ["line_axis_p"],
            "filter_preserved": [x.get("value") for x in repaired_ir.get("filters") or []] == ["CELL-Q9"],
            "time_changed": (repaired_ir.get("period") or {}).get("kind") == "last_n_months",
        }, latency_class="standard")

        before_no_query = service.query_calls
        response, elapsed = post(client, "bu sonucu yorumlar mısın?", conversation=conversation)
        body = response.json() if response.status_code == 200 else {}
        conversation = body.get("conversation") or conversation
        record("result_explain", response, elapsed, {
            "explain": (body.get("response") or {}).get("kind") == "explain",
            "query_zero": body.get("query_execution_count") == 0,
            "service_query_unchanged": service.query_calls == before_no_query,
            "evidence": bool((body.get("response") or {}).get("evidence_refs")),
        })

        before_no_query = service.query_calls
        response, elapsed = post(client, "eyvallah teşekkürler", conversation=conversation)
        body = response.json() if response.status_code == 200 else {}
        conversation = body.get("conversation") or conversation
        record("pure_social", response, elapsed, {
            "talk": (body.get("response") or {}).get("kind") == "talk",
            "query_zero": body.get("query_execution_count") == 0,
            "service_query_unchanged": service.query_calls == before_no_query,
        })

        # 7 — topic switch: prior filter/metric must not bleed into the new independent topic.
        response, elapsed = post(
            client,
            "peki bu ay bölgelerde net gelir nasıl?",
            conversation=conversation,
        )
        body = response.json() if response.status_code == 200 else {}
        switched_ir = body.get("analytics_ir") or {}
        record("topic_switch", response, elapsed, {
            "answer": (body.get("response") or {}).get("kind") == "answer",
            "new_cube": switched_ir.get("cube") == "sales_omega",
            "new_metric": [x.get("canonical_name") for x in switched_ir.get("metrics") or []] == ["net_value_x"],
            "old_filter_absent": not any(
                x.get("value") == "CELL-Q9" for x in switched_ir.get("filters") or []
            ),
        }, latency_class="standard")

    standard_p95 = p95(standard_latencies)
    clarify_p95 = p95(clarify_latencies)
    all_attack_pass = all(bool(item.get("pass")) for item in records)
    principal_aware = bool(service.principals) and all(
        principal is not None for _, principal in service.principals
    )
    gates = {
        "all_attack_records_pass": all_attack_pass,
        "silent_wrong_zero": silent_wrong == 0,
        "unhandled_500_zero": unhandled_500 == 0,
        "principal_aware_100pct": principal_aware,
        "standard_p95_le_10s": standard_p95 is not None and standard_p95 <= 10.0,
        "clarify_p95_le_6s": clarify_p95 is not None and clarify_p95 <= 6.0,
    }
    payload = {
        "kind": "dima_v2_day5_live_core_attack",
        "provider": settings.llm_provider,
        "model": getattr(settings, "openrouter_model", None),
        "source_policy": "real_http_real_provider_synthetic_semantic_engine_no_demo_db",
        "records": records,
        "silent_wrong": silent_wrong,
        "unhandled_500": unhandled_500,
        "standard_p95_s": round(standard_p95, 4) if standard_p95 is not None else None,
        "clarify_p95_s": round(clarify_p95, 4) if clarify_p95 is not None else None,
        "principal_events": len(service.principals),
        "gates": gates,
        "status": "pass" if all(gates.values()) else "fail",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
