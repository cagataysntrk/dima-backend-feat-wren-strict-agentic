"""P4 ContextProvider V0.

Builds a bounded semantic prompt context from the tenant-bound WrenService schema.
It never resolves user mentions and deliberately excludes entity values.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactRelationshipV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    TenantAnalyticsRuntimeV0,
)

COMPACT_CATALOG_BUILDER_VERSION = "v0.1"
PROMPT_CONTEXT_POLICY_VERSION = "v0.1"

_MAX_RULE_CHARS = 8_000
_MAX_DESCRIPTION_CHARS = 320


def _text(value: Any, *, limit: int | None = None) -> str | None:
    if value is None:
        return None
    out = str(value).strip()
    if not out:
        return None
    if limit is not None:
        out = out[:limit]
    return out


def _strings(values: Any, *, limit: int | None = None) -> tuple[str, ...]:
    out: list[str] = []
    for value in values or ():
        text = _text(value)
        if text and text not in out:
            out.append(text)
        if limit is not None and len(out) >= limit:
            break
    return tuple(out)


def _rules_for_prompt(schema: dict[str, Any]) -> tuple[str, bool]:
    """Return only runtime-approved rules already exposed by WrenService.schema().

    The V2 provider does not read extra files or discover a second business-rule owner.
    """
    raw = schema.get("business_rules")
    if not isinstance(raw, str):
        return "", False
    canonical = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    return canonical[:_MAX_RULE_CHARS], len(canonical) > _MAX_RULE_CHARS


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ContextProviderV0:
    """Create prompt context + non-null provenance without semantic interpretation."""

    def build(
        self,
        service,
        runtime: TenantAnalyticsRuntimeV0,
    ) -> BoundedSemanticContextV0:
        schema = service.schema()
        rules, rules_truncated = _rules_for_prompt(schema)
        rules_hash = _sha256(rules)

        cubes: list[CompactCubeContextV0] = []
        for cube in (schema.get("cubes") or []):
            if not isinstance(cube, dict) or not cube.get("name"):
                continue

            measure_synonyms = cube.get("measure_synonyms") or {}
            measure_display = cube.get("measure_synonyms_display") or {}
            units = cube.get("units") or {}
            measures: list[CompactSemanticFieldV0] = []
            for name in (cube.get("measures") or []):
                name = str(name)
                measures.append(
                    CompactSemanticFieldV0(
                        canonical_name=name,
                        display=_text(measure_display.get(name)),
                        description=_text(
                            (cube.get("measure_descriptions") or {}).get(name),
                            limit=_MAX_DESCRIPTION_CHARS,
                        ),
                        synonyms=_strings(measure_synonyms.get(name), limit=None),
                        unit=_text(units.get(name)),
                    )
                )

            dimension_synonyms = cube.get("dimension_synonyms") or {}
            dimension_labels = cube.get("dimension_labels") or {}
            dimensions: list[CompactSemanticFieldV0] = []
            for name in (cube.get("dimensions") or []):
                name = str(name)
                dimensions.append(
                    CompactSemanticFieldV0(
                        canonical_name=name,
                        display=_text(dimension_labels.get(name)),
                        description=_text(
                            (cube.get("dimension_descriptions") or {}).get(name),
                            limit=_MAX_DESCRIPTION_CHARS,
                        ),
                        synonyms=_strings(dimension_synonyms.get(name), limit=None),
                    )
                )

            cubes.append(
                CompactCubeContextV0(
                    canonical_name=str(cube["name"]),
                    display=_text(cube.get("display")),
                    description=_text(cube.get("description"), limit=_MAX_DESCRIPTION_CHARS),
                    synonyms=_strings(cube.get("synonyms"), limit=None),
                    measures=tuple(measures),
                    dimensions=tuple(dimensions),
                    time_dimensions=_strings(
                        cube.get("time_dimensions"),
                        limit=max(1, len(cube.get("time_dimensions") or [])),
                    ),
                )
            )

        kpis: list[CompactSemanticFieldV0] = []
        for kpi in (schema.get("kpis") or []):
            if not isinstance(kpi, dict) or not kpi.get("name"):
                continue
            kpis.append(
                CompactSemanticFieldV0(
                    canonical_name=str(kpi["name"]),
                    display=_text(kpi.get("label")),
                    description=_text(kpi.get("description"), limit=_MAX_DESCRIPTION_CHARS),
                    synonyms=_strings(kpi.get("synonyms"), limit=None),
                    unit=_text(kpi.get("unit")),
                )
            )

        relationships: list[CompactRelationshipV0] = []
        for rel in (schema.get("relationships") or []):
            if not isinstance(rel, dict) or not rel.get("name"):
                continue
            # Physical join condition is intentionally omitted. The interpreter needs
            # relationship availability, not permission to design joins.
            relationships.append(
                CompactRelationshipV0(
                    name=str(rel["name"]),
                    models=_strings(rel.get("models"), limit=None),
                    join_type=_text(rel.get("join_type")),
                    certified=_text(rel.get("certified")),
                )
            )

        version_payload = {
            "mdl_version": runtime.mdl_version,
            "compact_catalog_builder_version": COMPACT_CATALOG_BUILDER_VERSION,
            "business_rules_hash": rules_hash,
            "prompt_context_policy_version": PROMPT_CONTEXT_POLICY_VERSION,
        }
        version = _sha256(
            json.dumps(version_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        )

        return BoundedSemanticContextV0(
            context_version=ContextVersionV0(
                version=version,
                mdl_version=runtime.mdl_version,
                compact_catalog_builder_version=COMPACT_CATALOG_BUILDER_VERSION,
                business_rules_hash=rules_hash,
                prompt_context_policy_version=PROMPT_CONTEXT_POLICY_VERSION,
            ),
            cubes=tuple(cubes),
            kpis=tuple(kpis),
            relationships=tuple(relationships),
            approved_business_rules=rules,
            business_rules_truncated=rules_truncated,
        )
