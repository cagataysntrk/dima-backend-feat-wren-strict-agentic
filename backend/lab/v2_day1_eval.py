"""P4 Day 1 live evaluator for the production TurnInterpreter.

This measures the real configured LLM transport. It does not substitute fake outputs
for the roadmap's turn_act_accuracy / structured-output exit criteria.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from app.compose import compose_and_build
from app.config import get_settings
from app.llm import NoLlmGenerator, RuleBasedSqlGenerator, build_generator
from app.v2.context_provider import ContextProviderV0
from app.v2.interpreter import TurnInterpreter, TurnInterpreterError
from app.v2.models import ConversationStateV2, TenantAnalyticsRuntimeV0
from app.wren_service import WrenService

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "v2_day1_cases.yaml"
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day1_eval.json"


class CountingLlm:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def structured_text(self, system: str, user: str) -> str:
        self.calls += 1
        return self.inner.structured_text(system, user)


def _provider_names(llm) -> list[str]:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return [
        str(getattr(g, "_provider", type(g).__name__))
        for g in gens
    ]


def _is_real_llm(llm) -> bool:
    gens = list(getattr(llm, "_gens", None) or [llm])
    return any(not isinstance(g, (RuleBasedSqlGenerator, NoLlmGenerator)) for g in gens)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    compose_and_build(settings)

    service = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
        company_slug=settings.company,
    )
    schema = service.schema()
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id="day1-eval",
        tenant_slug=settings.company,
        principal_user_id="day1-eval",
        roles=("owner",),
        mdl_version=service.mdl_version,
        catalog=schema.get("catalog"),
        schema_name=schema.get("schema_name"),
        db_online=bool(schema.get("db_online", True)),
    )
    context = ContextProviderV0().build(service, runtime)

    llm = build_generator(settings)
    providers = _provider_names(llm)
    if not _is_real_llm(llm):
        payload = {
            "kind": "dima_v2_day1_eval",
            "status": "live_provider_unavailable",
            "providers": providers,
            "context_version": context.context_version.version,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False))
        return 2 if args.require_live else 0

    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))["cases"]
    interpreter = TurnInterpreter()

    records = []
    total_calls = 0
    max_calls = 0
    structured_ok = 0
    act_ok = 0
    surface_grounding_violations = 0

    for case in cases:
        counting = CountingLlm(llm)
        conversation = ConversationStateV2.model_validate(case.get("conversation") or {})
        try:
            turn = interpreter.interpret(
                question=case["q"],
                semantic_context=context,
                conversation=conversation,
                llm=counting,
            )
            structured_ok += 1
            correct = turn.dialogue_act.value == case["expected_act"]
            act_ok += int(correct)
            record = {
                "id": case["id"],
                "question": case["q"],
                "expected_act": case["expected_act"],
                "actual_act": turn.dialogue_act.value,
                "structured_success": True,
                "act_correct": correct,
                "calls": counting.calls,
                "failure": None,
            }
        except TurnInterpreterError as exc:
            if exc.failure.code == "surface_grounding_violation":
                surface_grounding_violations += 1
            record = {
                "id": case["id"],
                "question": case["q"],
                "expected_act": case["expected_act"],
                "actual_act": None,
                "structured_success": False,
                "act_correct": False,
                "calls": counting.calls,
                "failure": exc.failure.model_dump(mode="json"),
            }

        total_calls += counting.calls
        max_calls = max(max_calls, counting.calls)
        records.append(record)

    n = len(cases)
    structured_rate = structured_ok / n if n else 0.0
    act_accuracy = act_ok / n if n else 0.0
    passed = (
        structured_rate >= 0.99
        and act_accuracy >= 0.95
        and surface_grounding_violations == 0
        and max_calls <= 2
    )
    payload = {
        "kind": "dima_v2_day1_eval",
        "status": "pass" if passed else "fail",
        "providers": providers,
        "context_version": context.context_version.version,
        "n": n,
        "structured_success": structured_ok,
        "structured_success_rate": round(structured_rate, 4),
        "turn_act_correct": act_ok,
        "turn_act_accuracy": round(act_accuracy, 4),
        "surface_grounding_violations": surface_grounding_violations,
        "total_llm_calls": total_calls,
        "max_calls_per_case": max_calls,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Day1 eval: n={n} structured={structured_rate:.1%} "
        f"act={act_accuracy:.1%} surface_violations={surface_grounding_violations} "
        f"max_calls={max_calls} status={payload['status']}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
