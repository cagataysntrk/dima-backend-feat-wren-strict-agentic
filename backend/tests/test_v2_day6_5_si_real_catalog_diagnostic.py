"""Provider-free real-catalog diagnostic for remaining D65-SI live RED families."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from app.v2.context_provider import ContextProviderV0
from app.v2.semantic_linker import SemanticCandidateGenerator
from tests.test_v2_day6_5_si_full_live_standard import _runtime


pytestmark = pytest.mark.skipif(
    os.getenv("DIMA_D65_SI_REAL_CATALOG_DIAGNOSTIC") != "1",
    reason="manual-only provider-free real-catalog diagnostic",
)


def _safe(item):
    target = item.canonical_target
    return {
        "candidate_id": item.card.candidate_id,
        "target_kind": item.card.target_kind,
        "label": item.card.label,
        "cube_labels": list(item.card.cube_labels),
        "canonical_name": getattr(target, "canonical_name", None),
        "dimension_name": getattr(target, "dimension_name", None),
        "cube_refs": list(getattr(target, "cube_names", ()) or ()),
        "sensitive": bool(item.sensitive),
    }


def test_real_catalog_remaining_red_diagnostic(wren, schema):
    principal, runtime = _runtime(wren, schema)
    del principal
    context = ContextProviderV0().build(wren, runtime)
    generator = SemanticCandidateGenerator(
        semantic_context=context,
        schema=schema,
        max_candidates=48,
    )

    probes = [
        {
            "id": "001-metric-context",
            "surface": "tahsil edilmemiş cari bakiyeyi",
            "kind_hint": "metric",
        },
        {
            "id": "001-filter-surface",
            "surface": "tahsil edilmemiş",
            "kind_hint": "filter",
        },
        {
            "id": "005-dimension-surface",
            "surface": "cari kodunu",
            "kind_hint": "dimension",
        },
        {
            "id": "005-dimension-full-source-context",
            "surface": "en yüksek 5 cari kodunu fatura toplamına göre göster",
            "kind_hint": "dimension",
        },
        {
            "id": "005-metric-surface",
            "surface": "fatura toplamına",
            "kind_hint": "metric",
        },
    ]

    records = []
    for index, probe in enumerate(probes):
        result = generator.generate(
            request_id=f"probe-{index}",
            surface=probe["surface"],
            kind_hint=probe["kind_hint"],
        )
        records.append(
            {
                **probe,
                "backend": result.retrieval_backend,
                "exhaustive": result.retrieval_exhaustive,
                "truncated": result.retrieval_truncated,
                "too_broad": result.too_broad,
                "candidate_count": len(result.bindings),
                "candidates": [
                    _safe(item)
                    for item in result.bindings
                    if not item.sensitive
                ],
            }
        )

    report = {
        "kind": "d65_si_real_catalog_remaining_red_diagnostic",
        "context_version": context.context_version.version,
        "records": records,
    }
    out = (
        Path(__file__).resolve().parents[1]
        / "lab"
        / "reports"
        / "v2_day6_5_si_real_catalog_remaining_red.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    assert all(record["backend"] == "governed_token_index_v1" for record in records)
