"""Day 6.5 J1S/J1T isolated decision-model benchmark.

LAB/EVAL ONLY. Primary peers are Gemini Flash-Lite, Jev 1.13 and GPT-5.6 Luna.
Jev uses OpenRouter Decisions directly; chat models use strict structured output.
Sol is reference-ceiling only; Terra is a conditional second stage.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import statistics
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from app.v2.temporal_intent import TemporalNormalizationChoice

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
REPORTS = Path(__file__).resolve().parent / "reports"
J1S = EVAL / "v2_day6_5_j1s_frozen.json"
J1T = EVAL / "v2_day6_5_j1t_frozen.json"
FREEZE = EVAL / "v2_day6_5_j1_freeze_manifest.json"

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
CHAT_MAX_TOKENS = 512
PRIMARY_MODELS = (
    "google/gemini-2.5-flash-lite",
    "typesafe/jev-1.13",
    "openai/gpt-5.6-luna",
)
JEV_MODEL = "typesafe/jev-1.13"
REFERENCE_MODEL = "openai/gpt-5.6-sol"
CONDITIONAL_MODEL = "openai/gpt-5.6-terra"
MODELS = (*PRIMARY_MODELS, REFERENCE_MODEL, CONDITIONAL_MODEL)

PERIOD_ONTOLOGY = (
    "THIS_WEEK", "THIS_MONTH", "THIS_QUARTER", "THIS_YEAR",
    "PREVIOUS_WEEK", "PREVIOUS_MONTH", "PREVIOUS_QUARTER", "PREVIOUS_YEAR",
    "LAST_N_DAYS", "LAST_N_WEEKS", "LAST_N_MONTHS",
)
COMPARISON_ONTOLOGY = ("PREVIOUS_PERIOD", "PREVIOUS_YEAR_ALIGNED")


@dataclass(frozen=True)
class DecisionResult:
    choice: str | None
    probabilities: dict[str, float]
    confidence: float | None
    latency_s: float
    cost: float | None
    input_tokens: int | None
    output_tokens: int | None
    response_model: str | None
    response_id: str | None
    status: str
    failure_class: str | None = None
    error: str | None = None


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _api_key() -> str:
    key = (
        os.getenv("DIMA_OPENROUTER_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or os.getenv("DIMA_MEASURE_API_KEY")
        or ""
    ).strip()
    if not key:
        raise RuntimeError("OpenRouter API key is not configured")
    return key


def _reasoning_policy(model: str) -> str:
    if model == JEV_MODEL:
        return "NATIVE_DECISIONS_NO_CHAT_REASONING"
    if model == REFERENCE_MODEL:
        return "REFERENCE_CEILING_REASONING_ENABLED"
    return "BOUNDED_DECISION_REASONING_DISABLED"


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                props = node.get("properties") or {}
                node["required"] = list(props.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


def _exact_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or "").strip().casefold())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(normalized.split())


def _usage(payload: dict[str, Any]) -> tuple[float | None, int | None, int | None]:
    usage = payload.get("usage") or {}
    cost = usage.get("cost")
    inp = usage.get("input_tokens", usage.get("prompt_tokens"))
    out = usage.get("output_tokens", usage.get("completion_tokens"))
    return (
        float(cost) if isinstance(cost, (int, float)) else None,
        int(inp) if isinstance(inp, (int, float)) else None,
        int(out) if isinstance(out, (int, float)) else None,
    )


def _j1s_options(case: dict[str, Any]) -> dict[str, str]:
    options: dict[str, str] = {}
    for card in case["candidates"]:
        aliases = ", ".join(card.get("verified_aliases") or []) or "(none)"
        cubes = ", ".join(card.get("cube_labels") or []) or "(none)"
        options[card["candidate_id"]] = (
            f'target_kind={card["target_kind"]}; label="{card["label"]}"; '
            f"verified_aliases=[{aliases}]; cube_labels=[{cubes}]"
        )
    options["ABSTAIN"] = (
        "No supplied candidate is clearly the intended concept, the surface is ambiguous, "
        "or safe selection is not possible from the supplied cards."
    )
    return options


def _temporal_description(option: dict[str, Any]) -> str:
    if option["option_id"] == "ABSTAIN":
        return (
            "The exact temporal surface is ambiguous, unsupported by the supplied closed "
            "ontology, or lacks enough context to normalize safely."
        )
    fields = []
    for key in (
        "target",
        "period_kind",
        "comparison_kind",
        "n",
        "implicit_base_period_kind",
        "implicit_base_n",
    ):
        value = option.get(key)
        if value is not None:
            fields.append(f"{key}={value}")
    return "; ".join(fields)


def _j1t_options(case: dict[str, Any]) -> dict[str, str]:
    return {item["option_id"]: _temporal_description(item) for item in case["options"]}


def _state(track: str, case: dict[str, Any]) -> dict[str, Any]:
    if track == "J1S":
        return {
            "task": "bounded_semantic_candidate_decision",
            "user_surface": case["surface"],
            "candidate_cards": case["candidates"],
            "safety_rule": (
                "entity_value candidates require an exact label or verified_alias match; "
                "otherwise abstain"
            ),
        }
    return {
        "task": "typed_temporal_intent_decision",
        "target": case["target"],
        "exact_temporal_surface": case["surface"],
        "closed_options": case["options"],
        "rule": "choose intent only; never calculate calendar dates",
    }


def _options(track: str, case: dict[str, Any]) -> dict[str, str]:
    return _j1s_options(case) if track == "J1S" else _j1t_options(case)


def _chat_decide(
    *, model: str, track: str, case: dict[str, Any], timeout_s: float
) -> DecisionResult:
    options = _options(track, case)
    keys = list(options)
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a bounded decision component. Select exactly one supplied "
                    "option label. You cannot invent labels, canonical identifiers, SQL, "
                    "handles, dates, or extra rules. If no supplied choice is safely "
                    "justified, choose ABSTAIN. Return only the strict response schema."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {"state": _state(track, case), "options": options},
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "dima_j1_decision",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"choice": {"type": "string", "enum": keys}},
                    "required": ["choice"],
                    "additionalProperties": False,
                },
            },
        },
        "provider": {"allow_fallbacks": False},
        "reasoning": {"enabled": model == REFERENCE_MODEL},
        "max_tokens": CHAT_MAX_TOKENS,
    }
    started = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout_s) as client:
            response = client.post(
                CHAT_URL,
                headers={
                    "Authorization": f"Bearer {_api_key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        latency = time.perf_counter() - started
        if response.status_code != 200:
            return DecisionResult(
                None, {}, None, latency, None, None, None, None, None,
                "PROVIDER_FAILURE", "TRANSPORT/PROVIDER",
                f"HTTP {response.status_code}: {response.text[:500]}",
            )
        raw = response.json()
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("structured response must be an object")
        cost, inp, out = _usage(raw)
        return DecisionResult(
            str(parsed["choice"]), {}, None, latency, cost, inp, out,
            raw.get("model"), raw.get("id"), "OK"
        )
    except Exception as exc:
        return DecisionResult(
            None, {}, None, time.perf_counter() - started, None, None, None,
            None, None, "HARNESS_OR_TRANSPORT_FAILURE", "TRANSPORT/PROVIDER",
            f"{type(exc).__name__}: {exc}",
        )


def _jev_decide(*, track: str, case: dict[str, Any], timeout_s: float) -> DecisionResult:
    options = _options(track, case)
    record = json.dumps(_state(track, case), ensure_ascii=False, sort_keys=True)
    payload = {
        "model": JEV_MODEL,
        "state": {
            "description": (
                "One frozen Dima decision benchmark record. The record contains only "
                "the bounded user surface/context and supplied decision options."
            ),
            "records": [{"id": case["id"], "record": record}],
        },
        "questions": {
            "decision": {
                "type": "choice",
                "instructions": (
                    f'For the record with id "{case["id"]}", choose exactly one supplied '
                    "option. Use ABSTAIN when no supplied option is safely justified."
                ),
                "criteria": options,
            }
        },
    }
    started = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout_s) as client:
            response = client.post(
                DECISIONS_URL,
                headers={
                    "Authorization": f"Bearer {_api_key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        latency = time.perf_counter() - started
        if response.status_code != 200:
            return DecisionResult(
                None, {}, None, latency, None, None, None, None, None,
                "PROVIDER_FAILURE", "TRANSPORT/PROVIDER",
                f"HTTP {response.status_code}: {response.text[:500]}",
            )
        raw = response.json()
        answer = (raw.get("answers") or {}).get("decision") or {}
        probabilities = {
            str(k): float(v)
            for k, v in (answer.get("probabilities") or {}).items()
            if isinstance(v, (int, float))
        }
        confidence = answer.get("confidence")
        cost, inp, out = _usage(raw)
        return DecisionResult(
            str(answer["choice"]) if answer.get("choice") is not None else None,
            probabilities,
            float(confidence) if isinstance(confidence, (int, float)) else None,
            latency, cost, inp, out, raw.get("model"), raw.get("id"), "OK",
        )
    except Exception as exc:
        return DecisionResult(
            None, {}, None, time.perf_counter() - started, None, None, None,
            None, None, "HARNESS_OR_TRANSPORT_FAILURE", "TRANSPORT/PROVIDER",
            f"{type(exc).__name__}: {exc}",
        )


def decide(*, model: str, track: str, case: dict[str, Any], timeout_s: float) -> DecisionResult:
    if model == JEV_MODEL:
        return _jev_decide(track=track, case=case, timeout_s=timeout_s)
    return _chat_decide(model=model, track=track, case=case, timeout_s=timeout_s)


def _j1s_route_bucket(case: dict[str, Any]) -> str:
    taxonomy = set(case.get("taxonomy") or [])
    if "sensitive_exact" in taxonomy:
        return "SENSITIVE_EXACT_ONLY"
    if "retrieval_miss" in taxonomy:
        return "RETRIEVAL_MISS"
    surface = _exact_key(case["surface"])
    exact_ids = [
        card["candidate_id"]
        for card in case["candidates"]
        if surface and surface in {_exact_key(v) for v in card.get("verified_aliases") or []}
    ]
    if len(exact_ids) == 1:
        return "DETERMINISTIC_BYPASS"
    if len(exact_ids) > 1:
        return "DETERMINISTIC_AMBIGUOUS_EXACT"
    return "MODEL_NEEDED"


def _expected_temporal_contract(case: dict[str, Any]) -> dict[str, Any]:
    if case["expected"] == "ABSTAIN":
        return {
            "request_id": case["id"],
            "target": case["target"],
            "decision": "ABSTAIN",
            "period_kind": None,
            "comparison_kind": None,
            "n": None,
            "implicit_base_period_kind": None,
            "implicit_base_n": None,
            "reason": case["abstain_reason"] or "INSUFFICIENT_CONTEXT",
        }
    option = next(
        item for item in case["options"] if item["option_id"] == case["expected"]
    )
    return {
        "request_id": case["id"],
        "target": option["target"],
        "decision": "NORMALIZED",
        "period_kind": option.get("period_kind"),
        "comparison_kind": option.get("comparison_kind"),
        "n": option.get("n"),
        "implicit_base_period_kind": option.get("implicit_base_period_kind"),
        "implicit_base_n": option.get("implicit_base_n"),
        "reason": None,
    }


def _chat_temporal_contract(
    *, model: str, case: dict[str, Any], timeout_s: float
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Normalize one exact temporal surface into Dima's supplied strict typed "
                    "contract. Use only the closed ontology. Infer dynamic N from the surface "
                    "when LAST_N applies. Do not calculate calendar dates. If ambiguous or "
                    "unsupported, ABSTAIN with the matching reason. Return only strict schema."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "request_id": case["id"],
                        "target": case["target"],
                        "exact_temporal_surface": case["surface"],
                        "period_ontology": PERIOD_ONTOLOGY,
                        "comparison_ontology": COMPARISON_ONTOLOGY,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "dima_temporal_normalization_choice",
                "strict": True,
                "schema": _strict_schema(
                    TemporalNormalizationChoice.model_json_schema()
                ),
            },
        },
        "provider": {"allow_fallbacks": False},
        "reasoning": {"enabled": model == REFERENCE_MODEL},
        "max_tokens": CHAT_MAX_TOKENS,
    }
    started = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout_s) as client:
            response = client.post(
                CHAT_URL,
                headers={
                    "Authorization": f"Bearer {_api_key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        return {
            "status": "TRANSPORT_PROVIDER_FAILURE",
            "failure_class": "TRANSPORT/PROVIDER",
            "error": f"{type(exc).__name__}: {exc}",
            "latency_s": time.perf_counter() - started,
        }

    latency = time.perf_counter() - started
    if response.status_code != 200:
        return {
            "status": "TRANSPORT_PROVIDER_FAILURE",
            "failure_class": "TRANSPORT/PROVIDER",
            "error": f"HTTP {response.status_code}: {response.text[:500]}",
            "latency_s": latency,
        }

    try:
        raw = response.json()
        content = raw["choices"][0]["message"]["content"]
    except Exception as exc:
        return {
            "status": "TRANSPORT_PROVIDER_FAILURE",
            "failure_class": "TRANSPORT/PROVIDER",
            "error": f"invalid provider response: {type(exc).__name__}: {exc}",
            "latency_s": latency,
        }

    cost, inp, out = _usage(raw)
    try:
        parsed = content if isinstance(content, dict) else json.loads(content)
        choice = TemporalNormalizationChoice.model_validate(parsed)
    except (json.JSONDecodeError, TypeError, ValidationError) as exc:
        return {
            "status": "INVALID_TYPED_CONTRACT",
            "failure_class": "MODEL_COGNITION/INVALID_TYPED_CONTRACT",
            "error": f"{type(exc).__name__}: {exc}",
            "invalid_payload": content if isinstance(content, dict) else str(content),
            "latency_s": latency,
            "cost": cost,
            "input_tokens": inp,
            "output_tokens": out,
            "response_model": raw.get("model"),
            "response_id": raw.get("id"),
        }

    return {
        "status": "OK",
        "choice": choice.model_dump(mode="json"),
        "latency_s": latency,
        "cost": cost,
        "input_tokens": inp,
        "output_tokens": out,
        "response_model": raw.get("model"),
        "response_id": raw.get("id"),
    }

def _jev_temporal_contract_capability() -> dict[str, Any]:
    return {
        "status": "TEMPORAL_INTEGRATION_LIMITATION",
        "transport": "openrouter_decisions",
        "native_primitives": ["choice", "noul", "score"],
        "field_support": {
            "decision": "REPRESENTABLE_AS_CHOICE_OR_NOUL",
            "period_kind": "REPRESENTABLE_AS_CHOICE",
            "comparison_kind": "REPRESENTABLE_AS_CHOICE",
            "n": "NOT_DYNAMICALLY_REPRESENTABLE",
            "implicit_base_period_kind": "REPRESENTABLE_AS_CHOICE",
            "implicit_base_n": "NOT_DYNAMICALLY_REPRESENTABLE",
            "reason": "REPRESENTABLE_AS_CHOICE",
        },
        "dynamic_integer_supported": False,
        "case_answer_pre_enumeration_required_for_n": True,
        "temporal_production_candidate": False,
        "reason": (
            "Jev native Decisions exposes choice/noul/score decisions; a dynamic positive "
            "integer N cannot be emitted faithfully without pre-enumerating candidate values."
        ),
    }


def run_temporal_contract_fidelity(
    *, model: str, cases: list[dict[str, Any]], timeout_s: float
) -> dict[str, Any]:
    if model == JEV_MODEL:
        return {
            "kind": "dima_v2_day6_5_j1t_contract_fidelity",
            "track": "J1T",
            "mode": "contract-fidelity",
            "model": model,
            "model_role": "PRIMARY_PEER",
            "reasoning_policy": _reasoning_policy(model),
            "capability": _jev_temporal_contract_capability(),
            "metrics": {
                "provider_failure_count": 0,
                "contract_valid_rate": None,
                "exact_contract_accuracy": None,
                "temporal_production_candidate": False,
            },
            "records": [],
        }

    records: list[dict[str, Any]] = []
    for case in cases:
        expected = _expected_temporal_contract(case)
        result = _chat_temporal_contract(model=model, case=case, timeout_s=timeout_s)
        actual = result.get("choice")
        records.append(
            {
                "case_id": case["id"],
                "surface": case["surface"],
                "expected": expected,
                "actual": actual,
                "status": result["status"],
                "failure_class": result.get("failure_class"),
                "error": result.get("error"),
                "invalid_payload": result.get("invalid_payload"),
                "contract_exact": result["status"] == "OK" and actual == expected,
                "latency_s": round(float(result.get("latency_s") or 0.0), 6),
                "cost": result.get("cost"),
                "input_tokens": result.get("input_tokens"),
                "output_tokens": result.get("output_tokens"),
                "response_model": result.get("response_model"),
                "response_id": result.get("response_id"),
            }
        )

    ok = [r for r in records if r["status"] == "OK"]
    invalid_typed = [r for r in records if r["status"] == "INVALID_TYPED_CONTRACT"]
    semantic_evaluable = [*ok, *invalid_typed]
    provider_failures = [
        r for r in records if r["status"] == "TRANSPORT_PROVIDER_FAILURE"
    ]
    exact = sum(bool(r["contract_exact"]) for r in semantic_evaluable)
    dynamic = [r for r in ok if r["expected"].get("n") is not None]
    implicit_n = [r for r in ok if r["expected"].get("implicit_base_n") is not None]
    comparisons = [r for r in ok if r["expected"].get("comparison_kind") is not None]
    abstains = [r for r in ok if r["expected"]["decision"] == "ABSTAIN"]

    def field_rate(rows: list[dict[str, Any]], field: str) -> float | None:
        if not rows:
            return None
        return sum(
            r["actual"] is not None
            and r["actual"].get(field) == r["expected"].get(field)
            for r in rows
        ) / len(rows)

    return {
        "kind": "dima_v2_day6_5_j1t_contract_fidelity",
        "track": "J1T",
        "mode": "contract-fidelity",
        "model": model,
        "model_role": (
            "REFERENCE_CEILING" if model == REFERENCE_MODEL
            else "CONDITIONAL_SECOND_STAGE" if model == CONDITIONAL_MODEL
            else "PRIMARY_PEER"
        ),
        "reasoning_policy": _reasoning_policy(model),
        "metrics": {
            "case_count": len(cases),
            "evaluable_case_count": len(semantic_evaluable),
            "valid_typed_count": len(ok),
            "invalid_typed_output_count": len(invalid_typed),
            "provider_failure_count": len(provider_failures),
            "contract_valid_rate": (
                len(ok) / len(semantic_evaluable) if semantic_evaluable else None
            ),
            "exact_contract_accuracy": (
                exact / len(semantic_evaluable) if semantic_evaluable else None
            ),
            "dynamic_n_accuracy": field_rate(dynamic, "n"),
            "comparison_kind_accuracy": field_rate(comparisons, "comparison_kind"),
            "implicit_base_kind_accuracy": field_rate(
                [r for r in ok if r["expected"].get("implicit_base_period_kind") is not None],
                "implicit_base_period_kind",
            ),
            "implicit_base_n_accuracy": field_rate(implicit_n, "implicit_base_n"),
            "abstain_reason_accuracy": field_rate(abstains, "reason"),
            "temporal_production_candidate": (
                len(provider_failures) == 0
                and len(invalid_typed) == 0
                and len(semantic_evaluable) == len(cases)
                and exact == len(semantic_evaluable)
            ),
        },
        "records": records,
    }


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def _brier(records: list[dict[str, Any]]) -> float | None:
    values = []
    for record in records:
        probs = record.get("probabilities") or {}
        if not probs:
            continue
        values.append(
            sum(
                (
                    float(probs.get(label, 0.0))
                    - (1.0 if label == record["expected"] else 0.0)
                ) ** 2
                for label in record["allowed_choices"]
            )
        )
    return statistics.fmean(values) if values else None


def _ece(records: list[dict[str, Any]], bins: int = 5) -> float | None:
    points = []
    for record in records:
        probs = record.get("probabilities") or {}
        if not probs:
            continue
        confidence = record.get("confidence")
        if confidence is None:
            confidence = max((float(v) for v in probs.values()), default=0.0)
        points.append((float(confidence), bool(record["correct"])))
    if not points:
        return None
    out = 0.0
    for idx in range(bins):
        low, high = idx / bins, (idx + 1) / bins
        if idx == bins - 1:
            bucket = [(conf, ok) for conf, ok in points if low <= conf <= high]
        else:
            bucket = [(conf, ok) for conf, ok in points if low <= conf < high]
        if bucket:
            mean_conf = statistics.fmean(conf for conf, _ in bucket)
            mean_acc = statistics.fmean(1.0 if ok else 0.0 for _, ok in bucket)
            out += (len(bucket) / len(points)) * abs(mean_acc - mean_conf)
    return out


def _metrics(
    *, track: str, model: str, cases: list[dict[str, Any]],
    records: list[dict[str, Any]], freeze: dict[str, Any],
) -> dict[str, Any]:
    first: dict[str, dict[str, Any]] = {}
    for record in records:
        first.setdefault(record["case_id"], record)
    evaluable = [r for r in first.values() if r["status"] == "OK"]
    failures = [r for r in records if r["status"] != "OK"]
    case_by_id = {case["id"]: case for case in cases}

    expected_abstain = [r for r in evaluable if r["expected"] == "ABSTAIN"]
    predicted_abstain = [r for r in evaluable if r["choice"] == "ABSTAIN"]
    abstain_tp = sum(
        r["expected"] == "ABSTAIN" and r["choice"] == "ABSTAIN" for r in evaluable
    )

    groups = freeze["metamorphic_groups"][track.lower()]
    group_ok = []
    for ids in groups.values():
        preds = [first[i]["choice"] for i in ids if i in first and first[i]["status"] == "OK"]
        if len(preds) == len(ids):
            group_ok.append(len(set(preds)) == 1)

    repeat_ids = set(freeze["repeated_run"][f"{track.lower()}_ids"])
    repeat_ok = []
    for case_id in repeat_ids:
        preds = [
            r["choice"] for r in records
            if r["case_id"] == case_id and r["status"] == "OK"
        ]
        if len(preds) >= 2:
            repeat_ok.append(len(set(preds)) == 1)

    tr = [r for r in evaluable if "tr" in case_by_id[r["case_id"]].get("taxonomy", [])]
    model_needed = [
        r for r in evaluable
        if track != "J1S" or _j1s_route_bucket(case_by_id[r["case_id"]]) == "MODEL_NEEDED"
    ]
    model_needed_tr = [
        r for r in model_needed
        if "tr" in case_by_id[r["case_id"]].get("taxonomy", [])
    ]
    deterministic_controls = [
        r for r in evaluable
        if track == "J1S" and _j1s_route_bucket(case_by_id[r["case_id"]]) == "DETERMINISTIC_BYPASS"
    ]
    sensitive_controls = [
        r for r in evaluable
        if track == "J1S" and _j1s_route_bucket(case_by_id[r["case_id"]]) == "SENSITIVE_EXACT_ONLY"
    ]
    retrieval_miss = [
        r for r in evaluable
        if track == "J1S" and _j1s_route_bucket(case_by_id[r["case_id"]]) == "RETRIEVAL_MISS"
    ]
    ambiguity_cases = [
        r for r in model_needed
        if {"true_ambiguity", "multiple_plausible"}.intersection(
            set(case_by_id[r["case_id"]].get("taxonomy", []))
        )
    ]
    no_match_cases = [
        r for r in model_needed
        if "no_match" in case_by_id[r["case_id"]].get("taxonomy", [])
    ]
    high_cardinality = [
        r for r in model_needed
        if "high_cardinality" in case_by_id[r["case_id"]].get("taxonomy", [])
    ]
    latencies = [float(r["latency_s"]) for r in records if r["status"] == "OK"]
    costs = [float(r["cost"]) for r in records if r.get("cost") is not None]

    result: dict[str, Any] = {
        "case_count": len(cases),
        "evaluable_case_count": len(evaluable),
        "provider_failure_count": len(failures),
        "all_cases_accuracy": (
            sum(bool(r["correct"]) for r in evaluable) / len(evaluable)
            if evaluable else None
        ),
        "model_needed_accuracy": (
            sum(bool(r["correct"]) for r in model_needed) / len(model_needed)
            if model_needed else None
        ),
        "model_needed_turkish_accuracy": (
            sum(bool(r["correct"]) for r in model_needed_tr) / len(model_needed_tr)
            if model_needed_tr else None
        ),
        "deterministic_bypass_controls": {
            "count": len(deterministic_controls),
            "accuracy": (
                sum(bool(r["correct"]) for r in deterministic_controls) / len(deterministic_controls)
                if deterministic_controls else None
            ),
        },
        "sensitive_exact_only_controls": {
            "count": len(sensitive_controls),
            "accuracy": (
                sum(bool(r["correct"]) for r in sensitive_controls) / len(sensitive_controls)
                if sensitive_controls else None
            ),
        },
        "retrieval_miss_behavior": {
            "count": len(retrieval_miss),
            "abstain_rate": (
                sum(r["choice"] == "ABSTAIN" for r in retrieval_miss) / len(retrieval_miss)
                if retrieval_miss else None
            ),
        },
        "ambiguity_abstain_accuracy": (
            sum(r["choice"] == "ABSTAIN" for r in ambiguity_cases) / len(ambiguity_cases)
            if ambiguity_cases else None
        ),
        "no_match_abstain_accuracy": (
            sum(r["choice"] == "ABSTAIN" for r in no_match_cases) / len(no_match_cases)
            if no_match_cases else None
        ),
        "high_cardinality_accuracy": (
            sum(bool(r["correct"]) for r in high_cardinality) / len(high_cardinality)
            if high_cardinality else None
        ),
        "abstain_precision": (
            abstain_tp / len(predicted_abstain) if predicted_abstain else 1.0
        ),
        "abstain_recall": (
            abstain_tp / len(expected_abstain) if expected_abstain else 1.0
        ),
        "unsafe_ambiguity_pick": sum(
            "ambiguity" in case_by_id[r["case_id"]].get("taxonomy", [])
            and r["expected"] == "ABSTAIN"
            and r["choice"] != "ABSTAIN"
            for r in evaluable
        ),
        "choice_escape": sum(bool(r.get("choice_escape")) for r in records),
        "turkish_accuracy_all_cases_diagnostic": (
            sum(bool(r["correct"]) for r in tr) / len(tr) if tr else 1.0
        ),
        "metamorphic_consistency": (
            sum(group_ok) / len(group_ok) if group_ok else 1.0
        ),
        "same_input_repeated_run_agreement": (
            sum(repeat_ok) / len(repeat_ok) if repeat_ok else None
        ),
        "p50_latency_s": _percentile(latencies, 0.50),
        "p95_latency_s": _percentile(latencies, 0.95),
        "total_cost": sum(costs) if costs else None,
    }
    if model == JEV_MODEL:
        ok_records = [r for r in records if r["status"] == "OK"]
        cutoff = float(freeze["diagnostic_only"]["jev_high_confidence_wrong_cutoff"])
        result.update(
            {
                "brier_multiclass": _brier(ok_records),
                "ece_5bin": _ece(ok_records),
                "high_confidence_wrong_cutoff": cutoff,
                "high_confidence_wrong_count": sum(
                    (not r["correct"])
                    and r.get("confidence") is not None
                    and float(r["confidence"]) >= cutoff
                    for r in ok_records
                ),
            }
        )
    return result


def run(
    *, track: str, model: str, case_ids: list[str], smoke: bool, timeout_s: float
) -> dict[str, Any]:
    freeze = _load(FREEZE)
    document = _load(J1S if track == "J1S" else J1T)
    cases = list(document["cases"])
    if model == CONDITIONAL_MODEL and os.getenv("DIMA_J1_ALLOW_CONDITIONAL_TERRA") != "1":
        raise SystemExit(
            "Conditional Terra stage is closed; explicit consultation/authorization is required"
        )
    if case_ids:
        selected = set(case_ids)
        cases = [case for case in cases if case["id"] in selected]
    elif smoke:
        selected_id = next(c["id"] for c in cases if c["expected"] != "ABSTAIN")
        abstain_id = next(c["id"] for c in cases if c["expected"] == "ABSTAIN")
        cases = [c for c in cases if c["id"] in {selected_id, abstain_id}]
    elif model == REFERENCE_MODEL:
        subset = set(freeze["reference_ceiling_subset"][f"{track.lower()}_ids"])
        cases = [c for c in cases if c["id"] in subset]
    if not cases:
        raise SystemExit("No J1 cases selected")

    repeat_ids = set(freeze["repeated_run"][f"{track.lower()}_ids"])
    repeat_count = int(freeze["repeated_run"]["runs_per_case"])
    records: list[dict[str, Any]] = []

    for case in cases:
        runs = 1 if smoke or case["id"] not in repeat_ids else repeat_count
        for repeat_index in range(runs):
            result = decide(model=model, track=track, case=case, timeout_s=timeout_s)
            allowed = list(_options(track, case))
            escape = result.choice is not None and result.choice not in allowed
            correct = (
                result.status == "OK"
                and not escape
                and result.choice == case["expected"]
            )
            records.append(
                {
                    "case_id": case["id"],
                    "repeat_index": repeat_index,
                    "track": track,
                    "model": model,
                    "expected": case["expected"],
                    "choice": result.choice,
                    "correct": correct,
                    "allowed_choices": allowed,
                    "choice_escape": escape,
                    "status": result.status,
                    "failure_class": result.failure_class,
                    "error": result.error,
                    "probabilities": result.probabilities,
                    "confidence": result.confidence,
                    "latency_s": round(result.latency_s, 6),
                    "cost": result.cost,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "response_model": result.response_model,
                    "response_id": result.response_id,
                    "taxonomy": case.get("taxonomy") or [],
                    "metamorphic_group": case.get("metamorphic_group"),
                }
            )

    return {
        "kind": "dima_v2_day6_5_j1_benchmark",
        "track": track,
        "model": model,
        "model_role": (
            "REFERENCE_CEILING" if model == REFERENCE_MODEL
            else "CONDITIONAL_SECOND_STAGE" if model == CONDITIONAL_MODEL
            else "PRIMARY_PEER"
        ),
        "reasoning_policy": _reasoning_policy(model),
        "corpus_version": document["version"],
        "freeze_version": freeze["version"],
        "frozen_before_any_benchmark_result": freeze["frozen_before_any_benchmark_result"],
        "transport": (
            "openrouter_decisions"
            if model == JEV_MODEL
            else "openrouter_chat_json_schema"
        ),
        "provider_fallbacks": False,
        "smoke": smoke,
        "metrics": _metrics(
            track=track, model=model, cases=cases, records=records, freeze=freeze
        ),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", choices=["J1S", "J1T"], required=True)
    parser.add_argument("--mode", choices=["choice", "contract-fidelity"], default="choice")
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.mode == "contract-fidelity":
        if args.track != "J1T":
            raise SystemExit("contract-fidelity mode is J1T-only")
        freeze = _load(FREEZE)
        document = _load(J1T)
        cases = list(document["cases"])
        if args.case_id:
            selected = set(args.case_id)
            cases = [case for case in cases if case["id"] in selected]
        elif args.smoke:
            cases = [
                next(c for c in cases if c["expected"] != "ABSTAIN"),
                next(c for c in cases if c["expected"] == "ABSTAIN"),
            ]
        elif args.model == REFERENCE_MODEL:
            subset = set(freeze["reference_ceiling_subset"]["j1t_ids"])
            cases = [case for case in cases if case["id"] in subset]
        if args.model == CONDITIONAL_MODEL and os.getenv("DIMA_J1_ALLOW_CONDITIONAL_TERRA") != "1":
            raise SystemExit(
                "Conditional Terra stage is closed; explicit consultation/authorization is required"
            )
        payload = run_temporal_contract_fidelity(
            model=args.model, cases=cases, timeout_s=args.timeout
        )
    else:
        payload = run(
            track=args.track,
            model=args.model,
            case_ids=args.case_id,
            smoke=args.smoke,
            timeout_s=args.timeout,
        )
    output = args.output or (
        REPORTS
        / (
            f"v2_day6_5_{args.track.lower()}_{args.mode.replace('-', '_')}_"
            f"{args.model.replace('/', '__').replace('.', '_')}.json"
        )
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({k: v for k, v in payload.items() if k != "records"}, ensure_ascii=False))
    return 2 if payload["metrics"]["provider_failure_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
