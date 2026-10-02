"""Emit deterministic semantic-dimension coverage for CI artifacts."""
from __future__ import annotations

import json

from tests.semantic_spec.model import pair_coverage, semantic_matrix


def main() -> None:
    cases = semantic_matrix()
    coverage = pair_coverage(cases)
    payload = {
        "schema": "dima_brain_v2_1_semantic_conformance_coverage_v1",
        "semantic_cases": len(cases),
        "dimension_pairs": len(coverage),
        "pair_value_counts": {
            key: len(values)
            for key, values in coverage.items()
        },
        "pair_values": {
            key: [list(value) for value in values]
            for key, values in coverage.items()
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
