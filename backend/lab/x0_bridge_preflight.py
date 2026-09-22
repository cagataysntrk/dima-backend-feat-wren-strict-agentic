"""Provider-free D65-X0 bridge preflight.

No Metabase runtime is started. This lab proves whether current sealed Dima/Wren
Standard semantics can be mechanically represented for Metabase Agent API portable MBQL
without inventing a second semantic truth.

Exactly three seams are evaluated:
A = StandardProjection + sem_* handles
B = resolved canonical Dima AnalyticsIR
C = Wren PlannedExecution / CubeQuery
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from app.v2.cube_planner import CubePlanner, ledger_from_canonical_ir
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
)
from app.v2.models import (
    AnalyticsIR,
    PeriodKind,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import AcceptedStandardAuthority, StandardAuthoritySealer
from app.v2.standard_builder import StandardBuilderSession, StandardBuilderState
from app.v2.standard_execution import WrenStandardExecutionAdapter
from app.v2.standard_projection import StandardProjectionCompiler

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEMO_COMPANY = "demo-boyahane"


@dataclass(frozen=True)
class IdentityRequirement:
    kind: str
    cube: str
    table: str
    field: str | None
    classification: str = "IDENTITY_ONLY"


@dataclass(frozen=True)
class FamilyArtifact:
    family_id: str
    authority: AcceptedStandardAuthority
    projection: Any
    ir: AnalyticsIR
    plans: tuple[Any, ...]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class BridgeFamilyReceipt:
    family_id: str
    authority_id: str
    projection_hash: str
    analytics_ir_hash: str
    chosen_seam: str
    bridge_lossless: bool
    metric_fidelity: bool
    dimension_fidelity: bool
    filter_fidelity: bool
    period_fidelity: bool
    comparison_fidelity: bool
    ranking_fidelity: bool
    multi_dimension_fidelity: bool
    metric_formula_duplication: bool
    relationship_duplication: bool
    grain_additivity_duplication: bool
    time_semantics_duplication: bool
    manual_metadata_mapping: int
    mechanical_identity_mapping_count: int
    implicit_join_required: bool
    unsupported_wren_construct: tuple[str, ...]
    adapter_conceptual_complexity: str
    sync_surface: str
    portable_queries: tuple[dict[str, Any], ...]
    identity_requirements: tuple[IdentityRequirement, ...]


def _hash_model(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_cube_metadata(cube: str) -> dict[str, Any]:
    path = (
        BACKEND_ROOT
        / "demo"
        / "companies"
        / DEMO_COMPANY
        / "cubes"
        / cube
        / "metadata.yml"
    )
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _index(items: list[dict] | None) -> dict[str, dict]:
    return {str(item["name"]): item for item in (items or [])}


def _simple_field(expression: Any) -> str | None:
    text = str(expression or "").strip()
    return text if text.isidentifier() else None


def _simple_measure(expression: Any) -> tuple[str, str | None] | None:
    text = str(expression or "").strip()
    upper = text.upper()
    if upper == "COUNT(*)":
        return ("count", None)
    for fn in ("SUM", "AVG", "MIN", "MAX"):
        prefix = fn + "("
        if upper.startswith(prefix) and text.endswith(")"):
            inner = text[len(prefix):-1].strip()
            if inner.isidentifier():
                return (fn.lower(), inner)
            return None
    return None


def _field_ref(identity: IdentityRequirement) -> list[Any]:
    # Database/schema names are runtime identities resolved later from the same DB route.
    return [
        "field",
        {},
        ["__CURRENT_DB__", "__CURRENT_SCHEMA__", identity.table, identity.field],
    ]


def _base_query(table: str) -> dict[str, Any]:
    return {
        "lib/type": "mbql/query",
        "stages": [
            {
                "lib/type": "mbql.stage/mbql",
                "source-table": ["__CURRENT_DB__", "__CURRENT_SCHEMA__", table],
            }
        ],
    }


def _period_filters(field: IdentityRequirement, period: ResolvedPeriod) -> list[list[Any]]:
    ref = _field_ref(field)
    filters: list[list[Any]] = [[">=", {}, ref, period.start]]
    if period.end is not None:
        filters.append(["<=", {}, ref, period.end])
    return filters


def _combine_filters(items: list[list[Any]]) -> list[list[Any]]:
    if len(items) <= 1:
        return items
    return [["and", {}, *items]]


def prototype_from_ir(ir: AnalyticsIR, metadata: dict[str, Any]) -> BridgeFamilyReceipt:
    measures = _index(metadata.get("measures"))
    dimensions = _index(metadata.get("dimensions"))
    times = _index(metadata.get("time_dimensions"))
    table = str(metadata["base_object"])

    identities: list[IdentityRequirement] = [
        IdentityRequirement(kind="table", cube=ir.cube, table=table, field=None)
    ]
    unsupported: list[str] = []
    metric_duplication = False
    grain_duplication = False

    metric_clauses: list[list[Any]] = []
    for metric in ir.metrics:
        spec = measures.get(metric.canonical_name)
        if spec is None:
            unsupported.append(f"missing_wren_measure:{metric.canonical_name}")
            continue
        simple = _simple_measure(spec.get("expression"))
        if simple is None:
            metric_duplication = True
            if spec.get("additive") is not None:
                grain_duplication = True
            unsupported.append(f"computed_metric_expression:{metric.canonical_name}")
            continue
        op, field = simple
        if field is None:
            metric_clauses.append([op, {}])
        else:
            identity = IdentityRequirement(
                kind="metric_field",
                cube=ir.cube,
                table=table,
                field=field,
            )
            identities.append(identity)
            metric_clauses.append([op, {}, _field_ref(identity)])

    breakout: list[list[Any]] = []
    for dim in ir.dimensions:
        spec = dimensions.get(dim.canonical_name)
        if spec is None:
            unsupported.append(f"missing_wren_dimension:{dim.canonical_name}")
            continue
        field = _simple_field(spec.get("expression"))
        if field is None:
            unsupported.append(f"computed_dimension_expression:{dim.canonical_name}")
            continue
        identity = IdentityRequirement(
            kind="dimension_field",
            cube=ir.cube,
            table=table,
            field=field,
        )
        identities.append(identity)
        breakout.append(_field_ref(identity))

    filters: list[list[Any]] = []
    for item in ir.filters:
        spec = dimensions.get(item.dimension_name)
        if spec is None:
            unsupported.append(f"missing_filter_dimension:{item.dimension_name}")
            continue
        field = _simple_field(spec.get("expression"))
        if field is None:
            unsupported.append(f"computed_filter_dimension:{item.dimension_name}")
            continue
        identity = IdentityRequirement(
            kind="filter_field",
            cube=ir.cube,
            table=table,
            field=field,
        )
        identities.append(identity)
        filters.append(["=", {}, _field_ref(identity), item.value])

    time_identity: IdentityRequirement | None = None
    period_for_primary = ir.period
    if ir.period is not None:
        spec = times.get(ir.period.time_dimension)
        field = _simple_field(spec.get("expression")) if spec else None
        if field is None:
            unsupported.append(f"computed_time_dimension:{ir.period.time_dimension}")
        else:
            time_identity = IdentityRequirement(
                kind="time_field",
                cube=ir.cube,
                table=table,
                field=field,
            )
            identities.append(time_identity)

    def make_query(period: ResolvedPeriod | None, *, include_rank: bool) -> dict[str, Any]:
        query = _base_query(table)
        stage = query["stages"][0]
        if metric_clauses:
            stage["aggregation"] = metric_clauses
        if breakout:
            stage["breakout"] = breakout
        local_filters = list(filters)
        if period is not None and time_identity is not None:
            local_filters.extend(_period_filters(time_identity, period))
        if local_filters:
            stage["filters"] = _combine_filters(local_filters)
        if include_rank and ir.ranking is not None:
            stage["order-by"] = [
                ["desc" if ir.ranking.direction == "desc" else "asc", ["aggregation", {}, 0]]
            ]
            stage["limit"] = ir.ranking.limit
        return query

    queries: list[dict[str, Any]] = []
    if not unsupported:
        queries.append(make_query(period_for_primary, include_rank=True))
        if ir.comparison is not None:
            queries.append(
                make_query(ir.comparison.reference_period, include_rank=False)
            )

    deduped_identities = tuple(
        dict.fromkeys(
            (item.kind, item.cube, item.table, item.field)
            for item in identities
        )
    )
    identity_rows = tuple(
        IdentityRequirement(kind=k, cube=c, table=t, field=f)
        for k, c, t, f in deduped_identities
    )
    bridge_lossless = not unsupported and not metric_duplication and not grain_duplication

    return BridgeFamilyReceipt(
        family_id="",
        authority_id="",
        projection_hash="",
        analytics_ir_hash=_hash_model(ir),
        chosen_seam="B_RESOLVED_ANALYTICS_IR",
        bridge_lossless=bridge_lossless,
        metric_fidelity=not any(x.startswith(("missing_wren_measure", "computed_metric_expression")) for x in unsupported),
        dimension_fidelity=not any(x.startswith(("missing_wren_dimension", "computed_dimension_expression")) for x in unsupported),
        filter_fidelity=not any(x.startswith(("missing_filter_dimension", "computed_filter_dimension")) for x in unsupported),
        period_fidelity=not any(x.startswith("computed_time_dimension") for x in unsupported),
        comparison_fidelity=(ir.comparison is None or (not unsupported and len(queries) == 2)),
        ranking_fidelity=(ir.ranking is None or not unsupported),
        multi_dimension_fidelity=(len(ir.dimensions) < 2 or not unsupported),
        metric_formula_duplication=metric_duplication,
        relationship_duplication=False,
        grain_additivity_duplication=grain_duplication,
        time_semantics_duplication=False,
        manual_metadata_mapping=0,
        mechanical_identity_mapping_count=len(identity_rows),
        implicit_join_required=False,
        unsupported_wren_construct=tuple(unsupported),
        adapter_conceptual_complexity="LOW" if bridge_lossless else "SEMANTIC_TRANSLATION_REQUIRED",
        sync_surface="runtime identity resolution only" if bridge_lossless else "semantic expression translation required",
        portable_queries=tuple(queries),
        identity_requirements=identity_rows,
    )


def seam_assessment(artifact: FamilyArtifact) -> dict[str, dict[str, Any]]:
    return {
        "A_STANDARD_PROJECTION_HANDLES": {
            "additional_resolution_needed": True,
            "handle_resolution_duplicated": True,
            "semantic_meaning_duplicated": False,
            "wren_internals_leak": False,
            "metabase_ids_leak_upstream": False,
            "verdict": "COLLAPSES_TO_B_IF_RESOLVED_ONCE",
        },
        "B_RESOLVED_ANALYTICS_IR": {
            "additional_resolution_needed": False,
            "handle_resolution_duplicated": False,
            "semantic_meaning_duplicated": False,
            "wren_internals_leak": False,
            "metabase_ids_leak_upstream": False,
            "verdict": "THIN_CANDIDATE",
        },
        "C_WREN_PLANNED_REPRESENTATION": {
            "additional_resolution_needed": False,
            "handle_resolution_duplicated": False,
            "semantic_meaning_duplicated": True,
            "wren_internals_leak": True,
            "metabase_ids_leak_upstream": False,
            "raw_sql_option_forbidden": True,
            "cube_query_metric_formula_absent": True,
            "verdict": "REJECT_AS_PRIMARY_BRIDGE_SEAM",
        },
    }


def attach_family(receipt: BridgeFamilyReceipt, artifact: FamilyArtifact) -> BridgeFamilyReceipt:
    return BridgeFamilyReceipt(
        **{
            **asdict(receipt),
            "family_id": artifact.family_id,
            "authority_id": artifact.authority.authority_id,
            "projection_hash": artifact.authority.projection_hash,
            "analytics_ir_hash": _hash_model(artifact.ir),
            "identity_requirements": receipt.identity_requirements,
        }
    )


def terminal(receipts: tuple[BridgeFamilyReceipt, ...]) -> str:
    if any(
        item.metric_formula_duplication
        or item.relationship_duplication
        or item.grain_additivity_duplication
        or item.time_semantics_duplication
        for item in receipts
    ):
        return "HEAVY_SEMANTIC_DUPLICATION"
    if all(item.bridge_lossless for item in receipts):
        return "THIN_LOSSLESS"
    return "ARCHITECTURE_CHANGE_REQUIRED"
