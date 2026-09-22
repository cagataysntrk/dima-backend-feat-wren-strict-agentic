"""Day 6.5 J1S/J1T isolated decision-model benchmark.

LAB/EVAL ONLY. Gemini/Sol use OpenRouter chat structured output. Jev uses the
native OpenRouter Decisions API directly and never Dima structured_json().
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
REPORTS = Path(__file__).resolve().parent / "reports"
J1S = EVAL / "v2_day6_5_j1s_frozen.json"
J1T = EVAL / "v2_day6_5_j1t_frozen.json"
FREEZE = EVAL / "v2_day6_5_j1_freeze_manifest.json"

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
MODELS = (
    "google/gemini-2.5-flash-lite",
    "typesafe/jev-1.13",
    "openai/gpt-5.6-sol",
)
JEV_MODEL = "typesafe/jev-1.13"


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
        "reasoning": {"enabled": model == "openai/gpt-5.6-sol"},
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
        "provider": {"allow_fallbacks": False},
        "session_id": f"dima-day65-{track.lower()}-{case['id']}",
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
    latencies = [float(r["latency_s"]) for r in records if r["status"] == "OK"]
    costs = [float(r["cost"]) for r in records if r.get("cost") is not None]

    result: dict[str, Any] = {
        "case_count": len(cases),
        "evaluable_case_count": len(evaluable),
        "provider_failure_count": len(failures),
        "accuracy": (
            sum(bool(r["correct"]) for r in evaluable) / len(evaluable)
            if evaluable else None
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
        "turkish_accuracy": (
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
    if case_ids:
        selected = set(case_ids)
        cases = [case for case in cases if case["id"] in selected]
    elif smoke:
        selected_id = next(c["id"] for c in cases if c["expected"] != "ABSTAIN")
        abstain_id = next(c["id"] for c in cases if c["expected"] == "ABSTAIN")
        cases = [c for c in cases if c["id"] in {selected_id, abstain_id}]
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
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = run(
        track=args.track,
        model=args.model,
        case_ids=args.case_id,
        smoke=args.smoke,
        timeout_s=args.timeout,
    )
    output = args.output or (
        REPORTS
        / f"v2_day6_5_{args.track.lower()}_{args.model.replace('/', '__').replace('.', '_')}.json"
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
