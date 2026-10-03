"""Mutation canaries for the independent semantic-conformance oracle."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from .model import (
    AdaptiveSpec,
    AdmissionSpec,
    CompletionSpec,
    RankingBasis,
    ReferencePatch,
    ReferenceScope,
    apply_reference_patch,
    completion_allows_presentation,
    legal_next_test,
    ranking_basis_admission_allowed,
    semantic_admission_allowed,
)


@dataclass(frozen=True)
class MutationCanary:
    name: str
    killed: bool
    witness: str


def mutation_canaries() -> tuple[MutationCanary, ...]:
    ranking_oracle = ranking_basis_admission_allowed(
        required=RankingBasis.CHANGE,
        observed=RankingBasis.LEVEL,
    )
    ranking_mutant = True

    stale = AdmissionSpec(
        required=frozenset({"metric.m1"}),
        observed=frozenset({"metric.m1"}),
        permitted=frozenset({"metric.m1"}),
        current=False,
    )
    stale_oracle = semantic_admission_allowed(stale)
    stale_mutant = (
        stale.required.issubset(stale.observed)
        and stale.observed.issubset(stale.permitted)
        and stale.tenant_matches
        and stale.principal_matches
        and stale.scope_version_matches
    )

    next_test = AdaptiveSpec(
        unresolved_discrimination=True,
        preserves_scope=True,
        material_fingerprint_changes=False,
        executable_by_existing_metabot_path=True,
        produces_newer_evidence_on_success=True,
        duplicate_material=False,
    )
    next_test_oracle = legal_next_test(next_test)
    next_test_mutant = (
        next_test.unresolved_discrimination
        and next_test.preserves_scope
        and next_test.executable_by_existing_metabot_path
        and next_test.produces_newer_evidence_on_success
        and not next_test.duplicate_material
    )

    completion = CompletionSpec(
        required_owner_ids=frozenset({"goal.g1"}),
        terminal_owner_ids=frozenset(),
        presentation_requested=True,
    )
    completion_oracle = completion_allows_presentation(completion)
    completion_mutant = completion.presentation_requested

    scope = ReferenceScope(
        entities=frozenset({"entity.e1"}),
        metrics=frozenset({"metric.m1"}),
        breakdowns=frozenset({"dimension.d1"}),
        periods=frozenset({"period.p1"}),
        version=1,
    )
    patch = ReferencePatch(metrics=frozenset({"metric.m2"}))
    scope_oracle = apply_reference_patch(scope, patch)
    scope_mutant = ReferenceScope(
        metrics=frozenset({"metric.m2"}),
        version=scope.version + 1,
    )

    return (
        MutationCanary(
            "ranking_basis_wrong_acceptance",
            ranking_oracle != ranking_mutant,
            "CHANGE required but LEVEL observed",
        ),
        MutationCanary(
            "stale_evidence_promoted_current",
            stale_oracle != stale_mutant,
            "current=False must block semantic admission",
        ),
        MutationCanary(
            "next_test_noop_accepted",
            next_test_oracle != next_test_mutant,
            "material fingerprint must change",
        ),
        MutationCanary(
            "completion_nonterminal_accepted",
            completion_oracle != completion_mutant,
            "USER_MUST owner is not terminal",
        ),
        MutationCanary(
            "scope_patch_wipes_unrelated_facet",
            scope_oracle != scope_mutant,
            "metric patch must preserve entity/breakdown/period",
        ),
    )


def mutation_report_payload() -> dict[str, object]:
    results = mutation_canaries()
    killed = sum(item.killed for item in results)
    return {
        "schema": "dima_brain_v2_1_mutation_canary_v1",
        "total": len(results),
        "killed": killed,
        "detection_rate": killed / len(results),
        "all_detected": killed == len(results),
        "canaries": [asdict(item) for item in results],
    }


def main() -> None:
    payload = mutation_report_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["all_detected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
