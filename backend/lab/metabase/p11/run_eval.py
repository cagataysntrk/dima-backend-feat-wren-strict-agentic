#!/usr/bin/env python3
"""P11 V1 Semantic Necessity Gate.

Exactly four runnable cases are evaluated with Luna, then the exact same four with Sol.
No product resolver is imported or implemented here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

from app.v3.entity_value_gate import (
    CurrentLensValueEvidence,
    EntityValueAdoptionGate,
    EntityValueProposal,
)


HERE = Path(__file__).resolve().parent
CORPUS_PATH = HERE / "corpus_v1.json"
REPORT_PATH = HERE / "p11_eval_report.json"


def canonical_hash(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def login(base_url: str, email: str, password: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Metabase session token missing")
    return token


def list_payload(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [item for item in body if isinstance(item, dict)]
    if isinstance(body, dict):
        for key in ("data", "items"):
            value = body.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def locate_fields(
    client: httpx.Client,
    corpus: dict[str, Any],
    *,
    timeout_s: float = 150.0,
) -> dict[str, int]:
    db_name = corpus["dataset"]["database_name"]
    deadline = time.monotonic() + timeout_s
    last_detail = "not started"
    while time.monotonic() < deadline:
        db_response = client.get("/api/database")
        db_response.raise_for_status()
        dbs = [item for item in list_payload(db_response.json()) if item.get("name") == db_name]
        if len(dbs) != 1:
            last_detail = f"database count={len(dbs)}"
            time.sleep(3)
            continue
        database_id = int(dbs[0]["id"])
        metadata = client.get(
            f"/api/database/{database_id}/metadata",
            params={"include_hidden": "true"},
        )
        metadata.raise_for_status()
        body = metadata.json()
        tables = body.get("tables") if isinstance(body, dict) else None
        if not isinstance(tables, list):
            last_detail = "metadata tables missing"
            time.sleep(3)
            continue

        found: dict[str, int] = {}
        for semantic_ref, spec in corpus["semantic_context"]["scopes"].items():
            locator = spec["locator"]
            table_matches = [
                table for table in tables
                if isinstance(table, dict)
                and table.get("name") == locator["table"]
                and (table.get("schema") or "public") == locator["schema"]
            ]
            if len(table_matches) != 1:
                last_detail = f"{semantic_ref} table count={len(table_matches)}"
                break
            fields = table_matches[0].get("fields") or []
            field_matches = [
                field for field in fields
                if isinstance(field, dict)
                and field.get("name") == locator["field"]
            ]
            if len(field_matches) != 1:
                last_detail = f"{semantic_ref} field count={len(field_matches)}"
                break
            found[semantic_ref] = int(field_matches[0]["id"])
        if len(found) == len(corpus["semantic_context"]["scopes"]):
            return found
        time.sleep(3)
    raise RuntimeError(f"P11 exact field locator timeout: {last_detail}")


def current_user_values(
    client: httpx.Client,
    *,
    semantic_ref: str,
    field_id: int,
    limit: int,
    access_lens_ref: str,
) -> dict[str, Any]:
    response = client.get(f"/api/field/{field_id}/values")
    response.raise_for_status()
    body = response.json()
    if not isinstance(body, dict):
        raise RuntimeError(f"{semantic_ref} values payload is not an object")
    rows = body.get("values")
    if not isinstance(rows, list):
        raise RuntimeError(f"{semantic_ref} values payload has no list values")
    values = []
    for row in rows[:limit]:
        if not isinstance(row, list) or not row:
            continue
        values.append({
            "value": row[0],
            "display": row[1] if len(row) > 1 else row[0],
        })
    return {
        "semantic_ref": semantic_ref,
        "values": values,
        "has_more_values": bool(body.get("has_more_values")),
        "retrieval_source": "metabase_current_user_field_values",
        "freshness": "CURRENT_USER_RETRIEVAL",
        "access_lens_ref": access_lens_ref,
    }


def response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "decision": {"type": "string", "enum": ["BIND", "CLARIFY", "NO_MATCH"]},
            "semantic_ref": {"type": ["string", "null"]},
            "value": {"type": ["string", "null"]},
            "explanation": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["decision", "semantic_ref", "value", "explanation", "confidence"],
    }


def call_model(
    *,
    api_key: str,
    model: str,
    system: str,
    user_payload: dict[str, Any],
    max_tokens: int,
) -> dict[str, Any]:
    request = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(
                    user_payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "dima_p11_entity_decision_v1",
                "strict": True,
                "schema": response_schema(),
            },
        },
        "max_tokens": max_tokens,
    }
    started = time.perf_counter()
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "Dima P11 Semantic Necessity Gate",
        },
        json=request,
        timeout=120,
    )
    latency_ms = int((time.perf_counter() - started) * 1000)
    response.raise_for_status()
    body = response.json()
    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError(f"model {model} returned no choices")
    message = (choices[0] or {}).get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"model {model} returned empty structured content")
    decision = json.loads(content)
    usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
    return {
        "decision": decision,
        "latency_ms": latency_ms,
        "usage": usage,
        "requested_model": model,
        "runtime_model": body.get("model"),
        "provider": body.get("provider"),
        "response_id": body.get("id"),
    }


def normalized_decision(value: dict[str, Any]) -> dict[str, Any]:
    decision = value["decision"]
    if decision in {"CLARIFY", "NO_MATCH", "BLOCKED"}:
        return {"decision": decision, "semantic_ref": None, "value": None}
    return {
        "decision": decision,
        "semantic_ref": value.get("semantic_ref"),
        "value": value.get("value"),
    }


def accepted(case: dict[str, Any], decision: dict[str, Any]) -> bool:
    normalized = normalized_decision(decision)
    expected = case["oracle"]["accepted"]
    return any(normalized == item for item in expected)


def silent_wrong(case: dict[str, Any], decision: dict[str, Any]) -> bool:
    return decision.get("decision") == "BIND" and not accepted(case, decision)


def guarded_decision(
    *,
    raw: dict[str, Any],
    allowed_scopes: list[str],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    lens_refs = {str(item["access_lens_ref"]) for item in evidence}
    if len(lens_refs) != 1:
        raise RuntimeError("P11 evidence must carry one coherent access lens")
    expected_lens = next(iter(lens_refs))
    proposal = EntityValueProposal(
        decision=raw["decision"],
        semantic_ref=(
            raw.get("semantic_ref") if raw["decision"] == "BIND" else None
        ),
        value=raw.get("value") if raw["decision"] == "BIND" else None,
    )
    typed_evidence = tuple(
        CurrentLensValueEvidence(
            semantic_ref=item["semantic_ref"],
            values=tuple(candidate["value"] for candidate in item["values"]),
            access_lens_ref=item["access_lens_ref"],
            freshness=item["freshness"],
        )
        for item in evidence
    )
    result = EntityValueAdoptionGate.adjudicate(
        proposal=proposal,
        allowed_semantic_scopes=tuple(allowed_scopes),
        evidence=typed_evidence,
        expected_access_lens_ref=expected_lens,
    )
    return {
        "decision": result.decision.value,
        "semantic_ref": result.semantic_ref,
        "value": result.value,
        "reason_code": result.reason_code,
    }


def run_case(
    *,
    corpus_hash: str,
    corpus: dict[str, Any],
    case: dict[str, Any],
    model: str,
    api_key: str,
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    system = "\n".join(corpus["prompt_contract"]["system"])
    payload = {
        "corpus_fingerprint": corpus_hash,
        "case_id": case["id"],
        "user_surface": case["user_surface"],
        "allowed_semantic_scopes": case["allowed_scopes"],
        "current_user_value_evidence": evidence,
        "instruction": (
            "Choose the safe semantic value-binding outcome. "
            "Do not mention or invent physical identifiers."
        ),
    }

    def measured_attempt() -> dict[str, Any]:
        raw = call_model(
            api_key=api_key,
            model=model,
            system=system,
            user_payload=payload,
            max_tokens=int(corpus["model_policy"]["max_tokens"]),
        )
        official = guarded_decision(
            raw=raw["decision"],
            allowed_scopes=case["allowed_scopes"],
            evidence=evidence,
        )
        return {
            **raw,
            "raw_decision": raw["decision"],
            "guarded_decision": official,
        }

    attempts = [measured_attempt()]
    raw_first_pass = accepted(case, attempts[0]["raw_decision"])
    official_first_pass = accepted(case, attempts[0]["guarded_decision"])
    raw_first_silent_wrong = silent_wrong(case, attempts[0]["raw_decision"])
    official_first_silent_wrong = silent_wrong(
        case,
        attempts[0]["guarded_decision"],
    )

    # Preserve the frozen variance rule against raw cognition. A guardrail intercept
    # does not erase evidence that the model itself produced a suspicious first answer.
    if not raw_first_pass:
        attempts.extend(measured_attempt() for _ in range(2))

    raw_silent_wrong = any(
        silent_wrong(case, item["raw_decision"]) for item in attempts
    )
    official_silent_wrong = any(
        silent_wrong(case, item["guarded_decision"]) for item in attempts
    )
    official_all_pass = all(
        accepted(case, item["guarded_decision"]) for item in attempts
    )

    if official_first_pass and not raw_first_pass:
        classification = "PASS_WITH_MINIMUM_GUARDRAIL"
    elif official_first_pass:
        classification = "PASS_INITIAL_SIGNAL"
    elif official_silent_wrong:
        classification = "MATERIAL_SILENT_WRONG_AFTER_GUARDRAIL"
    elif official_all_pass:
        classification = "PASS_AFTER_VARIANCE"
    else:
        classification = "PERSISTENT_FAILURE_AFTER_GUARDRAIL"

    return {
        "case_id": case["id"],
        "requested_model": model,
        "raw_first_pass": raw_first_pass,
        "first_pass": official_first_pass,
        "raw_first_silent_wrong": raw_first_silent_wrong,
        "first_silent_wrong": official_first_silent_wrong,
        "raw_any_silent_wrong": raw_silent_wrong,
        "any_silent_wrong": official_silent_wrong,
        "classification": classification,
        "attempts": attempts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    corpus_hash = canonical_hash(corpus)
    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OpenRouter eval key is required")

    base_url = os.environ.get(
        "METABASE_URL",
        f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}",
    ).rstrip("/")
    token = login(
        base_url,
        os.environ["MB_RESTRICTED_EMAIL"],
        os.environ["MB_RESTRICTED_PASSWORD"],
    )
    access_lens_ref = (
        f"metabase-subject:{os.environ['MB_RESTRICTED_EMAIL']}:"
        f"{corpus['access_fixture']['lens']}"
    )

    headers = {
        "Accept": "application/json",
        "X-Metabase-Session": token,
    }
    with httpx.Client(base_url=base_url, headers=headers, timeout=30) as mb:
        field_ids = locate_fields(mb, corpus)
        evidence_by_scope = {
            semantic_ref: current_user_values(
                mb,
                semantic_ref=semantic_ref,
                field_id=field_id,
                limit=int(corpus["retrieval_contract"]["max_values_per_scope"]),
                access_lens_ref=access_lens_ref,
            )
            for semantic_ref, field_id in field_ids.items()
        }

    runnable = [case for case in corpus["cases"] if case["state"] == "RUNNABLE"]
    blocked = [case for case in corpus["cases"] if case["state"] == "BLOCKED"]
    results = []
    for profile_name in ("luna", "sol"):
        model = corpus["model_policy"][profile_name]["requested_model"]
        for case in runnable:
            evidence = [evidence_by_scope[scope] for scope in case["allowed_scopes"]]
            results.append(
                run_case(
                    corpus_hash=corpus_hash,
                    corpus=corpus,
                    case=case,
                    model=model,
                    api_key=api_key,
                    evidence=evidence,
                )
            )

    by_model: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_model.setdefault(result["requested_model"], []).append(result)

    luna_model = corpus["model_policy"]["luna"]["requested_model"]
    sol_model = corpus["model_policy"]["sol"]["requested_model"]
    luna = by_model[luna_model]
    sol = by_model[sol_model]

    luna_all_initial = all(item["first_pass"] for item in luna)
    sol_all_initial = all(item["first_pass"] for item in sol)
    any_silent = any(item["any_silent_wrong"] for item in results)
    raw_any_silent = any(item["raw_any_silent_wrong"] for item in results)

    if any_silent:
        resolver_decision = "MINIMUM_GUARDRAIL_REQUIRED"
        guardrail_status = "INSUFFICIENT"
    elif luna_all_initial and sol_all_initial:
        resolver_decision = "NOT_NEEDED"
        guardrail_status = (
            "SUFFICIENT" if raw_any_silent else "NOT_NEEDED_BY_RAW_MODEL"
        )
    elif (not luna_all_initial) and sol_all_initial:
        resolver_decision = "MODEL_COGNITION_GAP"
        guardrail_status = "INSUFFICIENT"
    else:
        resolver_decision = "MINIMUM_GUARDRAIL_REQUIRED"
        guardrail_status = "INSUFFICIENT"

    total_attempts = sum(len(item["attempts"]) for item in results)
    payload = {
        "kind": "dima_p11_entity_value_necessity_v1",
        "corpus_fingerprint": corpus_hash,
        "dataset": corpus["dataset"],
        "access_fixture": corpus["access_fixture"],
        "tool_contract": corpus["retrieval_contract"],
        "model_policy": corpus["model_policy"],
        "primary_evaluations": len(results),
        "total_model_calls_with_repeats": total_attempts,
        "blocked_cases": [
            {"id": item["id"], "blocker": item["blocker"]}
            for item in blocked
        ],
        "results": results,
        "summary": {
            "luna_initial_passes": sum(item["first_pass"] for item in luna),
            "sol_initial_passes": sum(item["first_pass"] for item in sol),
            "raw_luna_initial_passes": sum(
                item["raw_first_pass"] for item in luna
            ),
            "raw_sol_initial_passes": sum(
                item["raw_first_pass"] for item in sol
            ),
            "raw_silent_wrong_count": sum(
                1
                for item in results
                for attempt in item["attempts"]
                if silent_wrong(
                    next(c for c in runnable if c["id"] == item["case_id"]),
                    attempt["raw_decision"],
                )
            ),
            "silent_wrong_count": sum(
                1
                for item in results
                for attempt in item["attempts"]
                if silent_wrong(
                    next(c for c in runnable if c["id"] == item["case_id"]),
                    attempt["guarded_decision"],
                )
            ),
            "guardrail_status": guardrail_status,
            "resolver_decision": resolver_decision,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        "corpus_fingerprint": corpus_hash,
        "primary_evaluations": len(results),
        "total_model_calls_with_repeats": total_attempts,
        "summary": payload["summary"],
        "runtime_models": sorted({
            str(attempt.get("runtime_model"))
            for item in results
            for attempt in item["attempts"]
        }),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
