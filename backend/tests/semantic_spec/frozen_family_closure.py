"""Provider-free adjudication map for immutable Round-2 counterexample seeds.

The old benchmark is diagnostic evidence only.  These records do not drive runtime
routing and contain no prompt text.  They map a formerly invalid boundary to the
generic owner law that now governs the same semantic family.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FrozenFamilyReceipt:
    seeds: tuple[str, ...]
    old_first_invalid_boundary: str
    current_owner_path: str
    expected_terminal: str
    generic_law: str


RECEIPTS = (
    FrozenFamilyReceipt(
        seeds=("F02_H",),
        old_first_invalid_boundary="R1_NATIVE_RANKING_SCOPE_MISMATCH",
        current_owner_path=(
            "typed ranking basis -> Metabot native query -> dima.10 R5 observation "
            "-> exact semantic material admission"
        ),
        expected_terminal="FULFILLED_OR_GOVERNED_LIMIT",
        generic_law=(
            "CHANGE is first-class typed ranking authority; R5 may expose basis=change "
            "only from structurally proven period-over-period native material; ordinary "
            "ranking remains LEVEL and ambiguous derived ranking fails closed"
        ),
    ),
    FrozenFamilyReceipt(
        seeds=("F03_H", "F04_M"),
        old_first_invalid_boundary="P20_RESEARCH_SESSION_NOT_SEALED",
        current_owner_path="canonical USER_MUST terminal owner artifacts -> P20 claim gate",
        expected_terminal="FULFILLED_OR_GOVERNED_LIMIT",
        generic_law=(
            "completion derives from terminal mandatory owner artifacts; incidental "
            "process lifecycle flags are not a second completion authority"
        ),
    ),
    FrozenFamilyReceipt(
        seeds=("F06_M",),
        old_first_invalid_boundary="R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE",
        current_owner_path=(
            "typed comparison + result dependency -> bounded P14 material repair -> "
            "verified source execution anchor -> execution-local dependency filter"
        ),
        expected_terminal="FULFILLED_OR_LIMITED_OR_INCONCLUSIVE",
        generic_law=(
            "legal result-dependent comparison preserves accepted scope, never replays "
            "parent analytics, uses the exact durable source occurrence, and either "
            "produces governed material or an honest terminal limitation"
        ),
    ),
    FrozenFamilyReceipt(
        seeds=("F06_H",),
        old_first_invalid_boundary="BRAIN_V2_NEXT_TEST_DESIGN_INVALID",
        current_owner_path="P19 NextTestRequest -> P17 typed material delta -> P19 reassessment",
        expected_terminal="FULFILLED_OR_INCONCLUSIVE",
        generic_law=(
            "NextTest is executable only when it creates a legal materially-new governed "
            "surface; no legal information gain is a typed INCONCLUSIVE outcome, not an exception"
        ),
    ),
    FrozenFamilyReceipt(
        seeds=("F07_M",),
        old_first_invalid_boundary="INTAKE_CAUSAL_CHANGE_TEMPORAL_MATERIAL_REQUIRED",
        current_owner_path=(
            "typed causal/effect requirement -> temporal authority -> governed observation "
            "surface -> P19 epistemic judgment"
        ),
        expected_terminal="FULFILLED_OR_LIMITED_OR_INCONCLUSIVE",
        generic_law=(
            "temporal observation authority is distinct from explicit calendar comparison; "
            "one governed time axis may support observation, ambiguity clarifies/fails closed, "
            "and temporal evidence never manufactures causal authority"
        ),
    ),
    FrozenFamilyReceipt(
        seeds=("F10_S", "F10_M", "F10_H"),
        old_first_invalid_boundary="INTAKE_SCOPE_PATCH_INVALID_OR_NATIVE_FILTER_SCOPE_MISMATCH",
        current_owner_path=(
            "typed partial scope patch -> new ScopeVersion/currentness -> exact entity-filter "
            "semantic admission -> fresh Evidence only"
        ),
        expected_terminal="FULFILLED_OR_GOVERNED_LIMIT",
        generic_law=(
            "absent patch facets are unchanged, explicit mutation is local, stale Evidence "
            "does not become current, and exact governed entity value sets may be represented "
            "by one native membership predicate without relaxing scope authority"
        ),
    ),
    FrozenFamilyReceipt(
        seeds=("F01_H", "F04_H", "F05_M", "F05_H", "F08_M", "F08_H"),
        old_first_invalid_boundary="P20_SYNTHESIS_QUALITY_CEILING",
        current_owner_path=(
            "terminal P14/P18/P19 governed artifacts -> source-backed report projection -> P20"
        ),
        expected_terminal="FULFILLED_OR_LIMITED",
        generic_law=(
            "P20 preserves exact row context and numeric provenance, does no hidden analytics "
            "or invented arithmetic, exposes an observation-only ceiling when interpretation "
            "is absent, and synthesizes only governed upstream interpretation"
        ),
    ),
)

REQUIRED_ANSWER_BLOCKING = frozenset(
    {"F02_H", "F03_H", "F04_M", "F06_M", "F06_H", "F07_M", "F10_S", "F10_M", "F10_H"}
)
REQUIRED_SYNTHESIS = frozenset({"F01_H", "F04_H", "F05_M", "F05_H", "F08_M", "F08_H"})
ALLOWED_TERMINAL_CLASSES = frozenset(
    {
        "FULFILLED_OR_GOVERNED_LIMIT",
        "FULFILLED_OR_LIMITED_OR_INCONCLUSIVE",
        "FULFILLED_OR_INCONCLUSIVE",
        "FULFILLED_OR_LIMITED",
    }
)


def seed_set() -> frozenset[str]:
    return frozenset(seed for receipt in RECEIPTS for seed in receipt.seeds)


def payload() -> dict[str, object]:
    seeds = seed_set()
    return {
        "schema": "dima_brain_v2_1_frozen_family_closure_v1",
        "broad_benchmark_executed": False,
        "answer_blocking_complete": REQUIRED_ANSWER_BLOCKING.issubset(seeds),
        "synthesis_complete": REQUIRED_SYNTHESIS.issubset(seeds),
        "unexpected_seed_count": len(
            seeds - REQUIRED_ANSWER_BLOCKING - REQUIRED_SYNTHESIS
        ),
        "all_terminal_classes_governed": all(
            item.expected_terminal in ALLOWED_TERMINAL_CLASSES for item in RECEIPTS
        ),
        "receipts": [asdict(item) for item in RECEIPTS],
    }


def main() -> None:
    report = payload()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["answer_blocking_complete"]:
        raise SystemExit(1)
    if not report["synthesis_complete"]:
        raise SystemExit(1)
    if report["unexpected_seed_count"] != 0:
        raise SystemExit(1)
    if not report["all_terminal_classes_governed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
