"""Provider-free/live harness support for Brain V2 certification.

This module deliberately contains no Product orchestrator and imports no legacy
HeadlessProductComposer. It only owns bounded provider accounting, governed
fixture catalog construction and exact native binding seeding.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlmodel import Session

from app.v3.research_contracts import (
    ResearchNativeVerificationBinding,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_intake import AllowedRelationship, ResearchIntakeCatalog
from control_plane.models import NativeResourceBinding
from lab.metabase.core_b import live_sentinel as sealed

MODEL = "openai/gpt-5.6-luna"
METABOT_MODEL = "openrouter/openai/gpt-5.6-luna"
CONTEXT = "phase1-final-pinpoint-v1"
MAX_ORCHESTRATION_BOUNDARY_UNITS = 12

class PinpointBudgetExceeded(RuntimeError):
    code = "PINPOINT_ORCHESTRATION_BOUNDARY_BUDGET_EXHAUSTED"

    def __init__(self, owner: str, limit: int) -> None:
        super().__init__(
            f"{self.code}: {owner} would exceed the {limit}-unit live ceiling"
        )
        self.owner = owner
        self.limit = limit


class OrchestrationBudget:
    def __init__(self, limit: int) -> None:
        if limit < 1 or limit > MAX_ORCHESTRATION_BOUNDARY_UNITS:
            raise ValueError("pinpoint model budget must be between 1 and 12")
        self.limit = limit
        self.used = 0
        self.by_owner: dict[str, int] = {}

    def consume(self, owner: str) -> None:
        if self.used >= self.limit:
            raise PinpointBudgetExceeded(owner, self.limit)
        self.used += 1
        self.by_owner[owner] = self.by_owner.get(owner, 0) + 1


class BoundedStructuredTransport:
    def __init__(self, inner, *, budget: OrchestrationBudget, owner: str) -> None:
        self._inner = inner
        self._budget = budget
        self._owner = owner

    @property
    def call_count(self) -> int:
        return int(self._inner.call_count)

    @property
    def trace_log(self):
        return self._inner.trace_log

    def structured_json(self, system, user, *, schema, schema_name):
        self._budget.consume(self._owner)
        return self._inner.structured_json(
            system,
            user,
            schema=schema,
            schema_name=schema_name,
        )

    def close(self) -> None:
        self._inner.close()


class BoundedMaterialExecutor:
    def __init__(self, inner, *, budget: OrchestrationBudget) -> None:
        self._inner = inner
        self._budget = budget

    def execute(self, *args, **kwargs):
        self._budget.consume("metabot")
        return self._inner.execute(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _metric(cid: str, name: str, mention: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=mention,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def _dim(cid: str, name: str, mention: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=mention,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def load_binding_manifest(path: Path) -> dict[str, Any]:
    body = json.loads(path.read_text(encoding="utf-8"))
    if body.get("schema_version") != "phase1_pinpoint_native_bindings_v1":
        raise RuntimeError("unexpected pinpoint native binding manifest")
    if body.get("table_name") != "machine_operations":
        raise RuntimeError("unexpected pinpoint native table")
    metrics = body.get("metrics")
    if not isinstance(metrics, list):
        raise RuntimeError("pinpoint metric bindings missing")
    entity_values = body.get("entity_values")
    if not isinstance(entity_values, list):
        raise RuntimeError("pinpoint governed entity-value bindings missing")
    return body

def _native_resource_fingerprint(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _native_resource_binding_rows(
    binding_manifest: dict[str, Any],
) -> list[NativeResourceBinding]:
    """Build exact governed runtime bindings from the sealed live manifest."""
    database_id = int(binding_manifest["database_id"])
    table_id = int(binding_manifest["table_id"])
    rows: list[NativeResourceBinding] = []

    for item in binding_manifest["metrics"]:
        candidate_id = str(item["candidate_id"])
        entity_id = str(item["native_metric_entity_id"])
        field_id = int(item["fixture_definition"]["field_id"])
        locator = {
            "database_id": database_id,
            "table_id": table_id,
            "field_id": field_id,
            "metric_id": int(item["metabase_metric_id"]),
            "entity_id": entity_id,
        }
        rows.append(
            NativeResourceBinding(
                tenant_id=sealed.TENANT_ID,
                semantic_context_version=CONTEXT,
                candidate_id=candidate_id,
                candidate_kind=SemanticTargetKind.METRIC.value,
                semantic_id=candidate_id,
                canonical_name=str(item["canonical_name"]),
                locator_kind="metric",
                metabase_database_id=database_id,
                metabase_table_id=table_id,
                metabase_field_id=field_id,
                metabase_metric_id=int(item["metabase_metric_id"]),
                metabase_entity_id=entity_id,
                resource_entity_id=f"metabase:metric:{entity_id}",
                resource_fingerprint=_native_resource_fingerprint(locator),
                resource_version=str(binding_manifest["schema_version"]),
            )
        )

    dimensions = binding_manifest.get("dimensions")
    if not isinstance(dimensions, list):
        raise RuntimeError("pinpoint dimension bindings missing")
    for item in dimensions:
        candidate_id = str(item["candidate_id"])
        field_id = int(item["field_id"])
        locator = {
            "database_id": database_id,
            "table_id": table_id,
            "field_id": field_id,
        }
        rows.append(
            NativeResourceBinding(
                tenant_id=sealed.TENANT_ID,
                semantic_context_version=CONTEXT,
                candidate_id=candidate_id,
                candidate_kind=SemanticTargetKind.DIMENSION.value,
                semantic_id=candidate_id,
                canonical_name=str(item["canonical_name"]),
                locator_kind="field",
                metabase_database_id=database_id,
                metabase_table_id=table_id,
                metabase_field_id=field_id,
                resource_entity_id=f"metabase:field:{field_id}",
                resource_fingerprint=_native_resource_fingerprint(locator),
                resource_version=str(binding_manifest["schema_version"]),
            )
        )

    entity_values = binding_manifest.get("entity_values")
    if not isinstance(entity_values, list):
        raise RuntimeError("pinpoint entity-value bindings missing")
    for item in entity_values:
        candidate_id = str(item["candidate_id"])
        field_id = int(item["field_id"])
        locator = {
            "database_id": database_id,
            "table_id": table_id,
            "field_id": field_id,
        }
        rows.append(
            NativeResourceBinding(
                tenant_id=sealed.TENANT_ID,
                semantic_context_version=CONTEXT,
                candidate_id=candidate_id,
                candidate_kind=SemanticTargetKind.ENTITY_VALUE.value,
                semantic_id=candidate_id,
                canonical_name=str(item["canonical_name"]),
                locator_kind="field",
                metabase_database_id=database_id,
                metabase_table_id=table_id,
                metabase_field_id=field_id,
                resource_entity_id=f"metabase:field:{field_id}",
                resource_fingerprint=_native_resource_fingerprint(locator),
                resource_version=str(binding_manifest["schema_version"]),
            )
        )
    return rows


def seed_native_resource_bindings(
    db_engine,
    binding_manifest: dict[str, Any],
) -> None:
    """Persist exact runtime locators; never derive business semantics here."""
    rows = _native_resource_binding_rows(binding_manifest)
    with Session(db_engine) as db:
        for row in rows:
            db.add(row)
        db.commit()



def build_catalog(binding_manifest: dict[str, Any]) -> ResearchIntakeCatalog:
    base_refs = (
        _metric(
            "metric.machine_downtime_minutes",
            "Machine Downtime Minutes",
            "makine duruşları / duruş süresi / machine downtime",
        ),
        _metric("metric.fault_count", "Fault Count", "arıza sayısı / fault count"),
        _metric("metric.performance_score", "Performance Score", "performans / performance"),
        _metric(
            "metric.maintenance_delay_hours",
            "Maintenance Delay Hours",
            "bakım gecikmesi / maintenance delay",
        ),
        _metric(
            "metric.spare_part_delay_hours",
            "Spare Part Delay Hours",
            "yedek parça gecikmesi / spare part delay",
        ),
        _metric(
            "metric.pm_compliance_pct",
            "Preventive Maintenance Compliance",
            "önleyici bakım uyumu / preventive maintenance compliance",
        ),
        _metric(
            "metric.changeover_count",
            "Changeover Count",
            "changeover / değişim sayısı",
        ),
        _metric(
            "metric.operator_absence_hours",
            "Operator Absence Hours",
            "operatör devamsızlığı / operator absence",
        ),
        _dim("dimension.department", "Department", "bölüm / departman / department"),
        _dim("dimension.event_date", "Event Date", "tarih / date / Mayıs / Haziran"),
        _dim("dimension.machine_id", "Machine", "makine / machine"),
    )
    entity_refs = tuple(
        ResearchSemanticRef(
            source_mention=str(item["source_mention"]),
            candidate_id=str(item["candidate_id"]),
            target_kind=SemanticTargetKind.ENTITY_VALUE,
            canonical_name=str(item["canonical_name"]),
            dimension_name=str(item["dimension_name"]),
            value=str(item["value"]),
            cube_names=("machine_operations",),
        )
        for item in binding_manifest["entity_values"]
    )
    refs = (*base_refs, *entity_refs)
    relationships = (
        AllowedRelationship(
            relationship_id="rel.downtime_fault.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.fault_count",
            dimension_semantic_id="dimension.department",
        ),
        AllowedRelationship(
            relationship_id="rel.downtime_performance.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.performance_score",
            dimension_semantic_id="dimension.department",
        ),
        AllowedRelationship(
            relationship_id="rel.downtime_maintenance.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.maintenance_delay_hours",
            dimension_semantic_id="dimension.department",
        ),
        AllowedRelationship(
            relationship_id="rel.downtime_spare.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.spare_part_delay_hours",
            dimension_semantic_id="dimension.department",
        ),
    )
    metric_bindings = {
        str(item["candidate_id"]): item
        for item in binding_manifest["metrics"]
        if isinstance(item, dict)
    }
    bindings: list[ResearchNativeVerificationBinding] = []
    metric_ids = {
        item.candidate_id
        for item in refs
        if item.target_kind == SemanticTargetKind.METRIC
    }
    missing = sorted(metric_ids - metric_bindings.keys())
    if missing:
        raise RuntimeError(
            "governed native metric bindings missing: " + ",".join(missing)
        )
    for candidate_id in sorted(metric_ids):
        item = metric_bindings[candidate_id]
        native_id = str(item.get("native_metric_entity_id") or "").strip()
        column = str(item.get("column_name") or "").strip()
        if not native_id or not column:
            raise RuntimeError(f"invalid native metric binding: {candidate_id}")
        bindings.append(
            ResearchNativeVerificationBinding(
                candidate_id=candidate_id,
                table_name="machine_operations",
                column_name=column,
                native_metric_entity_id=native_id,
            )
        )
    for candidate_id, column in (
        ("dimension.department", "department"),
        ("dimension.event_date", "event_date"),
        ("dimension.machine_id", "machine_id"),
    ):
        bindings.append(
            ResearchNativeVerificationBinding(
                candidate_id=candidate_id,
                table_name="machine_operations",
                column_name=column,
            )
        )
    for item in binding_manifest["entity_values"]:
        candidate_id = str(item.get("candidate_id") or "").strip()
        column = str(item.get("column_name") or "").strip()
        value = item.get("value")
        dimension_name = str(item.get("dimension_name") or "").strip()
        if not candidate_id or not column or not dimension_name or not isinstance(value, str):
            raise RuntimeError("invalid governed entity-value binding")
        bindings.append(
            ResearchNativeVerificationBinding(
                candidate_id=candidate_id,
                table_name="machine_operations",
                column_name=column,
            )
        )
    return ResearchIntakeCatalog(
        context_version=CONTEXT,
        semantic_refs=refs,
        allowed_relationships=relationships,
        supported_domains=("machine_operations",),
        temporal_dimension_ids=("dimension.event_date",),
        native_verification_bindings=tuple(bindings),
    )


