"""Emit deterministic semantic-dimension coverage for CI artifacts."""
from __future__ import annotations

import json

from tests.semantic_spec.model import pair_coverage, semantic_matrix
from tests.semantic_spec.saturation import (
    expected_pair_value_counts,
    saturation_dimension_values,
    saturation_pair_coverage,
    saturation_pairwise_matrix,
)


def main() -> None:
    cases = semantic_matrix()
    coverage = pair_coverage(cases)
    saturation_cases = saturation_pairwise_matrix()
    saturation_coverage = saturation_pair_coverage(saturation_cases)
    payload = {
        "schema": "dima_brain_v2_1_semantic_conformance_coverage_v2",
        "legacy": {
            "semantic_cases": len(cases),
            "dimension_pairs": len(coverage),
            "pair_value_counts": {
                key: len(values)
                for key, values in coverage.items()
            },
        },
        "saturation": {
            "dimensions": {
                key: [item.value for item in values]
                for key, values in saturation_dimension_values().items()
            },
            "dimension_count": len(saturation_dimension_values()),
            "pairwise_cases": len(saturation_cases),
            "dimension_pairs": len(saturation_coverage),
            "pair_value_counts": {
                key: len(values)
                for key, values in saturation_coverage.items()
            },
            "expected_pair_value_counts": expected_pair_value_counts(),
            "pair_complete": {
                key: len(saturation_coverage[key]) == expected
                for key, expected in expected_pair_value_counts().items()
            },
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
