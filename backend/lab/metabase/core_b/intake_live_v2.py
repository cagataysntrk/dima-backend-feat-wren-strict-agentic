#!/usr/bin/env python3
"""One-call live proof for the Core-B v2 Research Intake relationship boundary."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from app.v3.research_contracts import ResearchGoalKind
from app.v3.research_intake import ResearchIntakeCompiler, ResearchIntakeTerminal
from app.v3.structured_transport import OpenRouterStructuredJSONTransport
from lab.metabase.core_b.live_sentinel import MODEL, _catalog, _load_cases


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--platform-sha", required=True)
    args = ap.parse_args()

    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is required")

    case = _load_cases(
        args.manifest,
        ("relationship_explicit_tr",),
    )["relationship_explicit_tr"]
    catalog = _catalog()
    transport = OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
    )
    compiler = ResearchIntakeCompiler(transport=transport)
    try:
        result = compiler.compile(
            question=str(case["platform_question"]),
            catalog=catalog,
        )
    finally:
        transport.close()

    passed = False
    selected_relationship_id = None
    expanded = None
    failure = None
    if result.terminal != ResearchIntakeTerminal.READY or result.brief is None:
        failure = "INTAKE_NOT_READY"
    else:
        goals = tuple(
            item for item in result.brief.questions
            if item.kind == ResearchGoalKind.RELATIONSHIP
        )
        if len(goals) != 1:
            failure = "RELATIONSHIP_GOAL_CARDINALITY_INVALID"
        else:
            goal = goals[0]
            subject_ids = tuple(
                item.candidate_id for item in goal.subject_refs
            )
            related_ids = tuple(
                item.candidate_id for item in goal.related_refs
            )
            matches = tuple(
                rel for rel in catalog.allowed_relationships
                if subject_ids == (
                    rel.left_semantic_id,
                    rel.right_semantic_id,
                )
                and related_ids == (
                    (rel.dimension_semantic_id,)
                    if rel.dimension_semantic_id is not None
                    else ()
                )
            )
            if len(matches) != 1:
                failure = "COMPILER_EXPANSION_NOT_ONE_LEGAL_RELATIONSHIP"
            else:
                selected_relationship_id = matches[0].relationship_id
                expanded = {
                    "subject_semantic_ids": list(subject_ids),
                    "related_semantic_ids": list(related_ids),
                }
                passed = compiler.call_count == 1
                if not passed:
                    failure = "INTAKE_MODEL_CALL_BOUND_EXCEEDED"

    report = {
        "schema_version": "core_b_intake_live_v2",
        "status": "GREEN" if passed else "RED",
        "platform_sha": args.platform_sha,
        "case_id": "relationship_explicit_tr",
        "terminal": result.terminal.value,
        "selected_relationship_id": selected_relationship_id,
        "compiler_expanded_refs": expanded,
        "catalog_relationship_ids": sorted(
            item.relationship_id for item in catalog.allowed_relationships
        ),
        "model_calls": compiler.call_count,
        "p17_calls": 0,
        "p18_calls": 0,
        "p19_calls": 0,
        "failure_class": failure,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
