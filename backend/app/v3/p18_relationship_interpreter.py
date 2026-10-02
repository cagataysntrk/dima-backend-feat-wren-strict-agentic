"""Bounded P18 interpretation over already VERIFIED relationship Evidence.

P18 is an epistemic relationship judge, not an analytics engine. This module
cannot execute Metabase, mutate Scope, invent semantic identities or request
new Evidence. It only classifies an already-governed Evidence packet.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select

from app.v3.business_relationship_v1 import RelationshipAnalyticalKind
from app.v3.claim_lineage import ClaimEvidenceRelation
from app.v3.research_contracts import RelationshipIntent
from app.v3.structured_transport import strict_json_schema
from control_plane.models import ResearchExecutionLink


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RelationshipMaterialMode(StrEnum):
    CROSS_SECTIONAL_ASSOCIATION = "CROSS_SECTIONAL_ASSOCIATION"
    TEMPORAL_CO_MOVEMENT = "TEMPORAL_CO_MOVEMENT"


class P18EvidenceDigest(Frozen):
    """Read-only digest of one exact VERIFIED native occurrence."""

    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    receipt_id: str = Field(pattern=r"^dqr_[a-f0-9]{24}$")
    execution_link_id: str = Field(min_length=1)
    result_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    executed_at: datetime
    row_count: int = Field(ge=0)
    columns: tuple[str, ...] = ()
    rows: tuple[tuple[Any, ...], ...] = ()
    truncated: bool = False


class P18RelationshipView(Frozen):
    requirement_id: str = Field(min_length=1)
    relationship_intent: RelationshipIntent
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    material_group_id: str = Field(pattern=r"^mg_[a-f0-9]{24}$")
    material_mode: RelationshipMaterialMode
    source_semantic_id: str = Field(min_length=1)
    target_semantic_id: str = Field(min_length=1)
    dimension_semantic_ids: tuple[str, ...] = ()
    evidence: tuple[P18EvidenceDigest, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def evidence_identity_unique(self):
        refs = [item.evidence_id for item in self.evidence]
        if len(refs) != len(set(refs)):
            raise ValueError("P18 Evidence digests must have unique identities")
        return self


class P18EvidenceAssessment(Frozen):
    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    relation: ClaimEvidenceRelation


class P18SalientCell(Frozen):
    """Exact existing Evidence cell selected for presentation, never a new fact."""

    evidence_id: str = Field(pattern=r"^evi_[a-f0-9]{24}$")
    row_index: int = Field(ge=0)
    column_index: int = Field(ge=0)


class P18RelationshipInterpretationDraft(Frozen):
    analytical_kind: RelationshipAnalyticalKind
    claim_text: str = Field(min_length=1)
    evidence_assessments: tuple[P18EvidenceAssessment, ...] = Field(min_length=1)
    salient_cells: tuple[P18SalientCell, ...] = Field(default=(), max_length=6)
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def evidence_identity_unique(self):
        refs = [item.evidence_id for item in self.evidence_assessments]
        if len(refs) != len(set(refs)):
            raise ValueError("P18 Evidence assessments must be unique by evidence_id")
        if any(not item.strip() for item in self.limitations):
            raise ValueError("P18 limitations must be non-empty strings")
        identities = [
            (item.evidence_id, item.row_index, item.column_index)
            for item in self.salient_cells
        ]
        if len(identities) != len(set(identities)):
            raise ValueError("P18 salient Evidence cells must be unique")
        return self


class StructuredJSONTransport(Protocol):
    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str: ...


_SYSTEM = """You are the bounded P18 relationship interpretation owner.
Use only the supplied VERIFIED Evidence values and exact semantic identities.
Do not execute or request analytics. Do not invent metrics, dimensions, scope,
Evidence, business policy, mechanisms, hypotheses, causal effects, statistics
or confidence values. Classify every supplied Evidence identity exactly once.
For CROSS_SECTIONAL_ASSOCIATION material, you may describe only cross-sectional
association across the observed grain; never claim temporal co-movement.
For TEMPORAL_CO_MOVEMENT material, co-movement may be assessed only from the
supplied paired temporal observations. Causality remains NOT ESTABLISHED.
BUSINESS_POLICY is outside this interpretation and is resolved separately.
When the Evidence supports or challenges a relationship and exact numeric cells
are available, select 2-6 salient_cells directly from the supplied rows. Prefer
cells spanning both relationship metrics and useful observed entities. A cell is
only an exact pointer (Evidence id, row index, column index); never calculate a
new statistic, delta, percentage, score or derived value. If the material cannot
support the requested interpretation, use INSUFFICIENT Evidence relations and
explicit limitations instead of filling the gap."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )


def _schema(view: P18RelationshipView) -> dict[str, Any]:
    schema = strict_json_schema(P18RelationshipInterpretationDraft)
    props = schema["properties"]
    allowed_kinds = (
        [RelationshipAnalyticalKind.ASSOCIATION.value]
        if view.material_mode == RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION
        else [
            RelationshipAnalyticalKind.ASSOCIATION.value,
            RelationshipAnalyticalKind.CO_MOVEMENT.value,
        ]
    )
    props["analytical_kind"] = {
        "type": "string",
        "enum": allowed_kinds,
    }
    defs = schema.get("$defs") or {}
    evidence_ids = [item.evidence_id for item in view.evidence]
    assessment = defs.get("P18EvidenceAssessment")
    if isinstance(assessment, dict):
        assessment_props = assessment.get("properties") or {}
        assessment_props["evidence_id"] = {
            "type": "string",
            "enum": evidence_ids,
        }
    salient = defs.get("P18SalientCell")
    if isinstance(salient, dict):
        salient_props = salient.get("properties") or {}
        salient_props["evidence_id"] = {
            "type": "string",
            "enum": evidence_ids,
        }
    return schema


class StructuredP18RelationshipInterpreter:
    """One bounded provider judgment over an immutable P18 view."""

    def __init__(
        self,
        *,
        transport: StructuredJSONTransport,
        schema_name: str = "dima_p18_relationship_interpretation_v1",
    ) -> None:
        self._transport = transport
        self._schema_name = schema_name
        self.call_count = 0

    def interpret(
        self,
        view: P18RelationshipView,
    ) -> P18RelationshipInterpretationDraft:
        packet = _canonical(view.model_dump(mode="json"))
        raw = self._transport.structured_json(
            _SYSTEM,
            (
                "Interpret this governed P18 relationship view. Preserve the exact "
                "Evidence identity set and remain within the material mode.\n\n"
                + packet
            ),
            schema=_schema(view),
            schema_name=self._schema_name,
        )
        self.call_count += 1
        draft = P18RelationshipInterpretationDraft.model_validate_json(raw)

        expected = {item.evidence_id for item in view.evidence}
        observed = {item.evidence_id for item in draft.evidence_assessments}
        if observed != expected:
            raise ValueError(
                "P18 interpretation must classify the complete Evidence identity set"
            )
        if (
            view.material_mode
            == RelationshipMaterialMode.CROSS_SECTIONAL_ASSOCIATION
            and draft.analytical_kind != RelationshipAnalyticalKind.ASSOCIATION
        ):
            raise ValueError(
                "cross-sectional material cannot establish temporal co-movement"
            )

        evidence_by_id = {item.evidence_id: item for item in view.evidence}
        assessment_by_id = {
            item.evidence_id: item.relation
            for item in draft.evidence_assessments
        }
        numeric_columns: set[tuple[str, int]] = set()
        for evidence in view.evidence:
            for row in evidence.rows:
                for column_index, value in enumerate(row):
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        numeric_columns.add((evidence.evidence_id, column_index))

        selected_columns: set[tuple[str, int]] = set()
        for cell in draft.salient_cells:
            evidence = evidence_by_id.get(cell.evidence_id)
            if evidence is None:
                raise ValueError("P18 salient cell used foreign Evidence")
            if cell.row_index >= len(evidence.rows):
                raise ValueError("P18 salient cell row is outside Evidence")
            row = evidence.rows[cell.row_index]
            if cell.column_index >= len(row):
                raise ValueError("P18 salient cell column is outside Evidence")
            value = row[cell.column_index]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("P18 salient cell must reference an exact numeric value")
            if assessment_by_id[cell.evidence_id] == ClaimEvidenceRelation.INSUFFICIENT:
                raise ValueError(
                    "P18 salient cell cannot be presented from insufficient Evidence"
                )
            selected_columns.add((cell.evidence_id, cell.column_index))

        material_relationship = any(
            relation in {
                ClaimEvidenceRelation.SUPPORTS,
                ClaimEvidenceRelation.CHALLENGES,
            }
            for relation in assessment_by_id.values()
        )
        if material_relationship and len(numeric_columns) >= 2:
            if len(draft.salient_cells) < 2 or len(selected_columns) < 2:
                raise ValueError(
                    "P18 material relationship requires salient values across "
                    "at least two observed numeric columns"
                )
        return draft


def interpretation_ref(
    *,
    view: P18RelationshipView,
    draft: P18RelationshipInterpretationDraft,
) -> str:
    body = {
        "view": view.model_dump(mode="json"),
        "draft": draft.model_dump(mode="json"),
    }
    return "p18i_" + hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()[:24]


def load_verified_evidence_digests(
    db_engine,
    *,
    session_id: str,
    obligation_id: str,
    evidence_ids: tuple[str, ...],
    max_rows: int = 100,
) -> tuple[P18EvidenceDigest, ...]:
    """Load a closed current Evidence set directly from durable execution truth."""

    if not evidence_ids or len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("P18 requires one non-empty unique Evidence identity set")

    with Session(db_engine) as db:
        rows = tuple(
            db.exec(
                select(ResearchExecutionLink)
                .where(ResearchExecutionLink.session_id == session_id)
                .where(ResearchExecutionLink.obligation_id == obligation_id)
                .where(ResearchExecutionLink.evidence_id.in_(evidence_ids))
                .where(ResearchExecutionLink.status == "VERIFIED")
            ).all()
        )
    by_evidence: dict[str, ResearchExecutionLink] = {}
    for row in rows:
        if not row.evidence_id:
            continue
        if row.evidence_id in by_evidence:
            raise ValueError("P18 Evidence execution identity is not unique")
        by_evidence[row.evidence_id] = row
    if set(by_evidence) != set(evidence_ids):
        raise ValueError("P18 Evidence set is not fully VERIFIED/current")

    output: list[P18EvidenceDigest] = []
    for evidence_id in evidence_ids:
        row = by_evidence[evidence_id]
        if (
            not row.receipt_id
            or not row.native_result_json
            or not row.result_hash
            or row.executed_at is None
        ):
            raise ValueError("P18 Evidence execution provenance is incomplete")
        try:
            payload = json.loads(row.native_result_json)
        except json.JSONDecodeError as exc:
            raise ValueError("P18 Evidence result is invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("P18 Evidence result must be a JSON object")
        canonical = _canonical(payload)
        if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != row.result_hash:
            raise ValueError("P18 Evidence result hash mismatch")

        data = payload.get("data")
        raw_rows = data.get("rows") if isinstance(data, dict) else None
        raw_cols = data.get("cols") if isinstance(data, dict) else None
        projected_rows: list[tuple[Any, ...]] = []
        if isinstance(raw_rows, list):
            for item in raw_rows[:max_rows]:
                if isinstance(item, (list, tuple)):
                    projected_rows.append(tuple(item))
        columns: list[str] = []
        if isinstance(raw_cols, list):
            for item in raw_cols:
                if not isinstance(item, dict):
                    continue
                label = item.get("display_name")
                if not isinstance(label, str):
                    label = item.get("name")
                if isinstance(label, str) and label.strip():
                    columns.append(label.strip())
        raw_count = payload.get("row_count")
        row_count = (
            raw_count
            if isinstance(raw_count, int) and raw_count >= 0
            else len(raw_rows)
            if isinstance(raw_rows, list)
            else len(projected_rows)
        )
        output.append(
            P18EvidenceDigest(
                evidence_id=evidence_id,
                receipt_id=row.receipt_id,
                execution_link_id=str(row.id),
                result_hash=row.result_hash,
                executed_at=row.executed_at,
                row_count=row_count,
                columns=tuple(columns),
                rows=tuple(projected_rows),
                truncated=(
                    isinstance(raw_rows, list)
                    and len(raw_rows) > len(projected_rows)
                ),
            )
        )
    return tuple(output)
