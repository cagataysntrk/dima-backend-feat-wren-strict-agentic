"""P21 advisory Decision Intelligence authority.

P21 consumes exactly one sealed, CURRENT P20 ReportDocument and produces an
immutable advisory DecisionBrief. It performs no analytics, lower-authority
discovery, human-adoption write, or action execution.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, model_validator
from sqlmodel import Session, select

from app.v3.report_document import (
    P20ReportError,
    ReportCurrentness,
    ReportDocument,
    ReportDocumentStore,
    ReportStatement,
    ReportStatementKind,
)
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import DecisionBriefRecord


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class P21DecisionError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ConstraintSource(StrEnum):
    USER_DECLARED = "USER_DECLARED"
    P20_PREMISE = "P20_PREMISE"


class TradeoffSource(StrEnum):
    USER_JUDGMENT = "USER_JUDGMENT"
    P20_PREMISE = "P20_PREMISE"


class RecommendationKind(StrEnum):
    ADVISORY_CONSIDERATION = "ADVISORY_CONSIDERATION"


class DecisionBriefCurrentness(StrEnum):
    CURRENT = "CURRENT"
    STALE_SOURCE_REPORT = "STALE_SOURCE_REPORT"
    SUPERSEDED = "SUPERSEDED"


class DecisionObjective(Frozen):
    objective_id: str = Field(pattern=r"^p21o_[a-f0-9]{24}$")
    objective_text: str = Field(min_length=1)
    source_kind: Literal["USER_DECLARED"] = "USER_DECLARED"


class DecisionPremiseRef(Frozen):
    premise_id: str = Field(pattern=r"^p21p_[a-f0-9]{24}$")
    statement_id: str = Field(pattern=r"^p20s_[a-f0-9]{24}$")
    statement_kind: ReportStatementKind
    upstream_epistemic_ceiling: str = Field(min_length=1)
    numeric_value: StrictInt | StrictFloat | None = None
    numeric_unit: str | None = None

    @model_validator(mode="after")
    def typed_numeric_boundary(self):
        if self.statement_kind == ReportStatementKind.NUMERIC:
            if self.numeric_value is None:
                raise ValueError("NUMERIC premise requires exact copied numeric value")
        elif self.numeric_value is not None or self.numeric_unit is not None:
            raise ValueError("non-NUMERIC premise cannot carry numeric authority")
        if self.numeric_unit is not None and not self.numeric_unit:
            raise ValueError("numeric unit cannot be blank")
        return self


class DecisionConstraint(Frozen):
    constraint_id: str = Field(pattern=r"^p21c_[a-f0-9]{24}$")
    source_kind: ConstraintSource
    text: str = Field(min_length=1)
    premise_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def source_boundary(self):
        if self.source_kind == ConstraintSource.USER_DECLARED and self.premise_refs:
            raise ValueError("USER_DECLARED constraint cannot inherit factual authority")
        if self.source_kind == ConstraintSource.P20_PREMISE and not self.premise_refs:
            raise ValueError("P20_PREMISE constraint requires exact premise refs")
        if len(self.premise_refs) != len(set(self.premise_refs)):
            raise ValueError("constraint premise refs must be unique")
        return self


class DecisionOption(Frozen):
    option_id: str = Field(pattern=r"^p21x_[a-f0-9]{24}$")
    proposal_text: str = Field(min_length=1)
    source_kind: Literal["USER_DECLARED"] = "USER_DECLARED"


class DecisionAssumption(Frozen):
    assumption_id: str = Field(pattern=r"^p21a_[a-f0-9]{24}$")
    assumption_text: str = Field(min_length=1)
    source_kind: Literal["USER_ASSUMPTION"] = "USER_ASSUMPTION"


class DecisionLimitation(Frozen):
    limitation_id: str = Field(pattern=r"^p21l_[a-f0-9]{24}$")
    detail: str = Field(min_length=1)
    premise_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def unique_refs(self):
        if len(self.premise_refs) != len(set(self.premise_refs)):
            raise ValueError("limitation premise refs must be unique")
        return self


class DecisionTradeoff(Frozen):
    tradeoff_id: str = Field(pattern=r"^p21t_[a-f0-9]{24}$")
    option_id: str = Field(pattern=r"^p21x_[a-f0-9]{24}$")
    source_kind: TradeoffSource
    text: str = Field(min_length=1)
    premise_refs: tuple[str, ...] = ()
    assumption_refs: tuple[str, ...] = ()
    limitation_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def source_boundary(self):
        if self.source_kind == TradeoffSource.USER_JUDGMENT and self.premise_refs:
            raise ValueError("USER_JUDGMENT tradeoff cannot inherit factual authority")
        if self.source_kind == TradeoffSource.P20_PREMISE and not self.premise_refs:
            raise ValueError("P20_PREMISE tradeoff requires exact premise refs")
        for values in (self.premise_refs, self.assumption_refs, self.limitation_refs):
            if len(values) != len(set(values)):
                raise ValueError("tradeoff refs must be unique")
        return self


class DecisionRecommendation(Frozen):
    recommendation_kind: Literal["ADVISORY_CONSIDERATION"] = "ADVISORY_CONSIDERATION"
    recommended_option_ids: tuple[str, ...] = Field(min_length=1)
    premise_refs: tuple[str, ...] = Field(min_length=1)
    assumption_refs: tuple[str, ...] = ()
    limitation_refs: tuple[str, ...] = ()
    rationale: str | None = None

    @model_validator(mode="after")
    def unique_refs(self):
        for values in (
            self.recommended_option_ids,
            self.premise_refs,
            self.assumption_refs,
            self.limitation_refs,
        ):
            if len(values) != len(set(values)):
                raise ValueError("recommendation refs must be unique")
        return self


class DecisionBriefDraft(Frozen):
    report_id: str = Field(pattern=r"^p20r_[a-f0-9]{24}$")
    brief_key: str = Field(min_length=1, max_length=160)
    objective: DecisionObjective
    constraints: tuple[DecisionConstraint, ...]
    premises: tuple[DecisionPremiseRef, ...] = Field(min_length=1)
    options: tuple[DecisionOption, ...] = Field(min_length=2)
    tradeoffs: tuple[DecisionTradeoff, ...]
    assumptions: tuple[DecisionAssumption, ...]
    limitations: tuple[DecisionLimitation, ...]
    recommendation: DecisionRecommendation
    model_provenance: None = None


class DecisionBrief(Frozen):
    decision_brief_id: str = Field(pattern=r"^p21b_[a-f0-9]{24}$")
    report_id: str = Field(pattern=r"^p20r_[a-f0-9]{24}$")
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    brief_key: str = Field(min_length=1)
    revision: int = Field(ge=1)
    parent_decision_brief_id: str | None = Field(
        default=None,
        pattern=r"^p21b_[a-f0-9]{24}$",
    )
    objective: DecisionObjective
    constraints: tuple[DecisionConstraint, ...]
    premises: tuple[DecisionPremiseRef, ...]
    options: tuple[DecisionOption, ...]
    tradeoffs: tuple[DecisionTradeoff, ...]
    assumptions: tuple[DecisionAssumption, ...]
    limitations: tuple[DecisionLimitation, ...]
    recommendation: DecisionRecommendation
    model_provenance: None = None
    source_report_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    decision_source_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    brief_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    created_at: datetime


def _canonical_json(value: Any, *, code: str) -> tuple[str, str]:
    try:
        raw = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
    except (TypeError, ValueError) as exc:
        raise P21DecisionError(code, "value is not deterministic JSON") from exc
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise P21DecisionError(
            "P21_TIMEZONE_REQUIRED",
            "timestamps must be timezone-aware",
        )
    return stamp


def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise P21DecisionError(
        "P21_TENANT_REQUIRED",
        "P21 requires explicit tenant binding",
    )


def stable_decision_id(prefix: str, value: Any) -> str:
    if prefix not in {"p21o_", "p21p_", "p21c_", "p21x_", "p21a_", "p21l_", "p21t_"}:
        raise P21DecisionError("P21_ID_PREFIX_INVALID", prefix)
    return prefix + _canonical_json(value, code="P21_IDENTITY_NOT_CANONICAL")[1][:24]


class DecisionLegalityGate:
    """Deterministic legality/provenance gate over one CURRENT P20 report."""

    def __init__(self, *, report_store: ReportDocumentStore) -> None:
        self._reports = report_store

    def _report(
        self,
        *,
        report_id: str,
        principal: Principal,
    ) -> ReportDocument:
        try:
            report = self._reports.load(
                report_id=report_id,
                principal=principal,
            )
            currentness = self._reports.currentness(
                report_id=report_id,
                principal=principal,
            )
        except P20ReportError as exc:
            raise P21DecisionError(
                "P21_SOURCE_REPORT_UNAVAILABLE",
                "source report unavailable in caller scope",
            ) from exc
        if report.tenant_binding != _tenant(principal):
            raise P21DecisionError(
                "P21_SOURCE_REPORT_UNAVAILABLE",
                "source report unavailable in caller scope",
            )
        if currentness != ReportCurrentness.CURRENT:
            raise P21DecisionError(
                "P21_SOURCE_REPORT_STALE",
                report_id,
            )
        return report

    @staticmethod
    def _statement_map(report: ReportDocument) -> dict[str, ReportStatement]:
        values = {item.statement_id: item for item in report.statements}
        if len(values) != len(report.statements):
            raise P21DecisionError(
                "P21_SOURCE_REPORT_INVALID",
                "duplicate P20 statement identity",
            )
        return values

    @staticmethod
    def _require_known_refs(
        refs: tuple[str, ...],
        known: set[str],
        *,
        code: str,
        owner: str,
    ) -> None:
        unknown = tuple(ref for ref in refs if ref not in known)
        if unknown:
            raise P21DecisionError(code, f"{owner}:{','.join(unknown)}")

    @staticmethod
    def _canonical_p20_text(kind: str, refs: tuple[str, ...]) -> str:
        return f"{kind}: " + ", ".join(refs)

    def _validate_premises(
        self,
        *,
        report: ReportDocument,
        premises: tuple[DecisionPremiseRef, ...],
    ) -> dict[str, DecisionPremiseRef]:
        premise_map = {item.premise_id: item for item in premises}
        if len(premise_map) != len(premises):
            raise P21DecisionError(
                "P21_PREMISE_ID_DUPLICATE",
                report.report_id,
            )
        statement_ids = tuple(item.statement_id for item in premises)
        if len(statement_ids) != len(set(statement_ids)):
            raise P21DecisionError(
                "P21_PREMISE_STATEMENT_DUPLICATE",
                report.report_id,
            )
        statements = self._statement_map(report)
        for premise in premises:
            source = statements.get(premise.statement_id)
            if source is None:
                raise P21DecisionError(
                    "P21_PREMISE_NOT_IN_REPORT",
                    premise.statement_id,
                )
            if source.statement_kind != premise.statement_kind:
                raise P21DecisionError(
                    "P21_PREMISE_KIND_MISMATCH",
                    premise.statement_id,
                )
            if source.upstream_epistemic_ceiling != premise.upstream_epistemic_ceiling:
                raise P21DecisionError(
                    "P21_EPISTEMIC_CEILING_MISMATCH",
                    premise.statement_id,
                )
            if source.statement_kind == ReportStatementKind.NUMERIC:
                if "value" not in source.payload:
                    raise P21DecisionError(
                        "P21_SOURCE_NUMERIC_INVALID",
                        premise.statement_id,
                    )
                _, source_value = _canonical_json(
                    source.payload["value"],
                    code="P21_SOURCE_NUMERIC_NOT_CANONICAL",
                )
                _, copied_value = _canonical_json(
                    premise.numeric_value,
                    code="P21_NUMERIC_PREMISE_NOT_CANONICAL",
                )
                if source_value != copied_value:
                    raise P21DecisionError(
                        "P21_NUMERIC_PREMISE_MISMATCH",
                        premise.statement_id,
                    )
                source_unit = source.payload.get("unit")
                if premise.numeric_unit != source_unit:
                    raise P21DecisionError(
                        "P21_NUMERIC_UNIT_MISMATCH",
                        premise.statement_id,
                    )
        return premise_map

    def validate(
        self,
        *,
        draft: DecisionBriefDraft,
        principal: Principal,
    ) -> tuple[
        ReportDocument,
        tuple[DecisionConstraint, ...],
        tuple[DecisionTradeoff, ...],
        DecisionRecommendation,
        str,
    ]:
        report = self._report(
            report_id=draft.report_id,
            principal=principal,
        )
        premise_map = self._validate_premises(
            report=report,
            premises=draft.premises,
        )
        premise_ids = set(premise_map)

        option_map = {item.option_id: item for item in draft.options}
        if len(option_map) != len(draft.options):
            raise P21DecisionError(
                "P21_OPTION_ID_DUPLICATE",
                draft.brief_key,
            )
        assumption_map = {item.assumption_id: item for item in draft.assumptions}
        if len(assumption_map) != len(draft.assumptions):
            raise P21DecisionError(
                "P21_ASSUMPTION_ID_DUPLICATE",
                draft.brief_key,
            )
        limitation_map = {item.limitation_id: item for item in draft.limitations}
        if len(limitation_map) != len(draft.limitations):
            raise P21DecisionError(
                "P21_LIMITATION_ID_DUPLICATE",
                draft.brief_key,
            )

        normalized_constraints: list[DecisionConstraint] = []
        constraint_ids: set[str] = set()
        for constraint in draft.constraints:
            if constraint.constraint_id in constraint_ids:
                raise P21DecisionError(
                    "P21_CONSTRAINT_ID_DUPLICATE",
                    constraint.constraint_id,
                )
            constraint_ids.add(constraint.constraint_id)
            self._require_known_refs(
                constraint.premise_refs,
                premise_ids,
                code="P21_CONSTRAINT_PREMISE_UNKNOWN",
                owner=constraint.constraint_id,
            )
            if constraint.source_kind == ConstraintSource.P20_PREMISE:
                expected = self._canonical_p20_text(
                    "Governed constraint premises",
                    constraint.premise_refs,
                )
                if constraint.text != expected:
                    raise P21DecisionError(
                        "P21_CONSTRAINT_TEXT_NOT_CANONICAL",
                        constraint.constraint_id,
                    )
            normalized_constraints.append(constraint)

        for limitation in draft.limitations:
            self._require_known_refs(
                limitation.premise_refs,
                premise_ids,
                code="P21_LIMITATION_PREMISE_UNKNOWN",
                owner=limitation.limitation_id,
            )

        normalized_tradeoffs: list[DecisionTradeoff] = []
        tradeoff_ids: set[str] = set()
        for tradeoff in draft.tradeoffs:
            if tradeoff.tradeoff_id in tradeoff_ids:
                raise P21DecisionError(
                    "P21_TRADEOFF_ID_DUPLICATE",
                    tradeoff.tradeoff_id,
                )
            tradeoff_ids.add(tradeoff.tradeoff_id)
            if tradeoff.option_id not in option_map:
                raise P21DecisionError(
                    "P21_TRADEOFF_OPTION_UNKNOWN",
                    tradeoff.option_id,
                )
            self._require_known_refs(
                tradeoff.premise_refs,
                premise_ids,
                code="P21_TRADEOFF_PREMISE_UNKNOWN",
                owner=tradeoff.tradeoff_id,
            )
            self._require_known_refs(
                tradeoff.assumption_refs,
                set(assumption_map),
                code="P21_TRADEOFF_ASSUMPTION_UNKNOWN",
                owner=tradeoff.tradeoff_id,
            )
            self._require_known_refs(
                tradeoff.limitation_refs,
                set(limitation_map),
                code="P21_TRADEOFF_LIMITATION_UNKNOWN",
                owner=tradeoff.tradeoff_id,
            )
            if tradeoff.source_kind == TradeoffSource.P20_PREMISE:
                expected = self._canonical_p20_text(
                    "Governed tradeoff premises",
                    tradeoff.premise_refs,
                )
                if tradeoff.text != expected:
                    raise P21DecisionError(
                        "P21_TRADEOFF_TEXT_NOT_CANONICAL",
                        tradeoff.tradeoff_id,
                    )
            normalized_tradeoffs.append(tradeoff)

        recommendation = draft.recommendation
        self._require_known_refs(
            recommendation.recommended_option_ids,
            set(option_map),
            code="P21_RECOMMENDATION_OPTION_UNKNOWN",
            owner=draft.brief_key,
        )
        self._require_known_refs(
            recommendation.premise_refs,
            premise_ids,
            code="P21_RECOMMENDATION_PREMISE_UNKNOWN",
            owner=draft.brief_key,
        )
        self._require_known_refs(
            recommendation.assumption_refs,
            set(assumption_map),
            code="P21_RECOMMENDATION_ASSUMPTION_UNKNOWN",
            owner=draft.brief_key,
        )
        self._require_known_refs(
            recommendation.limitation_refs,
            set(limitation_map),
            code="P21_RECOMMENDATION_LIMITATION_UNKNOWN",
            owner=draft.brief_key,
        )
        rationale = (
            "Advisory consideration only. "
            f"Options: {', '.join(recommendation.recommended_option_ids)}. "
            f"Governed premises: {', '.join(recommendation.premise_refs)}. "
            f"Assumptions: {', '.join(recommendation.assumption_refs) or 'none'}. "
            f"Limitations: {', '.join(recommendation.limitation_refs) or 'none'}."
        )
        if recommendation.rationale is not None and recommendation.rationale != rationale:
            raise P21DecisionError(
                "P21_RECOMMENDATION_RATIONALE_NOT_CANONICAL",
                draft.brief_key,
            )
        normalized_recommendation = recommendation.model_copy(
            update={"rationale": rationale},
        )

        source_identity = {
            "report_id": report.report_id,
            "source_report_fingerprint": report.report_fingerprint,
            "objective": draft.objective.model_dump(mode="json"),
            "constraints": [
                item.model_dump(mode="json")
                for item in normalized_constraints
            ],
            "premises": [
                item.model_dump(mode="json")
                for item in draft.premises
            ],
            "options": [
                item.model_dump(mode="json")
                for item in draft.options
            ],
            "tradeoffs": [
                item.model_dump(mode="json")
                for item in normalized_tradeoffs
            ],
            "assumptions": [
                item.model_dump(mode="json")
                for item in draft.assumptions
            ],
            "limitations": [
                item.model_dump(mode="json")
                for item in draft.limitations
            ],
            "recommendation": normalized_recommendation.model_dump(mode="json"),
            "model_provenance": None,
        }
        decision_source_fingerprint = _canonical_json(
            source_identity,
            code="P21_DECISION_SOURCE_NOT_CANONICAL",
        )[1]
        return (
            report,
            tuple(normalized_constraints),
            tuple(normalized_tradeoffs),
            normalized_recommendation,
            decision_source_fingerprint,
        )


class DecisionBriefStore:
    """Single durable P21 owner for immutable advisory DecisionBrief snapshots."""

    def __init__(
        self,
        *,
        report_store: ReportDocumentStore,
        db_engine=None,
    ) -> None:
        self._reports = report_store
        self._engine = db_engine or control_plane_engine
        self._gate = DecisionLegalityGate(report_store=report_store)

    @staticmethod
    def _hydrate(row: DecisionBriefRecord) -> DecisionBrief:
        try:
            objective = json.loads(row.objective_json)
            constraints = json.loads(row.constraints_json)
            options = json.loads(row.options_json)
            tradeoffs = json.loads(row.tradeoffs_json)
            recommendation = json.loads(row.recommendation_json)
            premises = json.loads(row.premise_refs_json)
            assumptions = json.loads(row.assumptions_json)
            limitations = json.loads(row.limitations_json)
        except json.JSONDecodeError as exc:
            raise P21DecisionError(
                "P21_BRIEF_PERSISTENCE_INVALID",
                row.decision_brief_id,
            ) from exc
        values = (constraints, options, tradeoffs, premises, assumptions, limitations)
        if not all(isinstance(item, list) for item in values):
            raise P21DecisionError(
                "P21_BRIEF_PERSISTENCE_INVALID",
                row.decision_brief_id,
            )
        if not isinstance(objective, dict) or not isinstance(recommendation, dict):
            raise P21DecisionError(
                "P21_BRIEF_PERSISTENCE_INVALID",
                row.decision_brief_id,
            )
        if row.model_provenance_json is not None:
            raise P21DecisionError(
                "P21_MODEL_PROVENANCE_FORBIDDEN",
                row.decision_brief_id,
            )
        return DecisionBrief(
            decision_brief_id=row.decision_brief_id,
            report_id=row.report_id,
            tenant_binding=row.tenant_binding,
            semantic_context_version=row.semantic_context_version,
            brief_key=row.brief_key,
            revision=row.revision,
            parent_decision_brief_id=row.parent_decision_brief_id,
            objective=DecisionObjective.model_validate(objective),
            constraints=tuple(
                DecisionConstraint.model_validate(item)
                for item in constraints
            ),
            premises=tuple(
                DecisionPremiseRef.model_validate(item)
                for item in premises
            ),
            options=tuple(
                DecisionOption.model_validate(item)
                for item in options
            ),
            tradeoffs=tuple(
                DecisionTradeoff.model_validate(item)
                for item in tradeoffs
            ),
            assumptions=tuple(
                DecisionAssumption.model_validate(item)
                for item in assumptions
            ),
            limitations=tuple(
                DecisionLimitation.model_validate(item)
                for item in limitations
            ),
            recommendation=DecisionRecommendation.model_validate(
                recommendation
            ),
            model_provenance=None,
            source_report_fingerprint=row.source_report_fingerprint,
            decision_source_fingerprint=row.decision_source_fingerprint,
            brief_fingerprint=row.brief_fingerprint,
            created_at=row.created_at,
        )

    def seal(
        self,
        *,
        draft: DecisionBriefDraft,
        principal: Principal,
        now: datetime | None = None,
    ) -> DecisionBrief:
        (
            report,
            constraints,
            tradeoffs,
            recommendation,
            decision_source_fingerprint,
        ) = self._gate.validate(
            draft=draft,
            principal=principal,
        )
        identity = {
            "report_id": report.report_id,
            "tenant_binding": report.tenant_binding,
            "semantic_context_version": report.semantic_context_version,
            "brief_key": draft.brief_key,
            "objective": draft.objective.model_dump(mode="json"),
            "constraints": [
                item.model_dump(mode="json")
                for item in constraints
            ],
            "premises": [
                item.model_dump(mode="json")
                for item in draft.premises
            ],
            "options": [
                item.model_dump(mode="json")
                for item in draft.options
            ],
            "tradeoffs": [
                item.model_dump(mode="json")
                for item in tradeoffs
            ],
            "assumptions": [
                item.model_dump(mode="json")
                for item in draft.assumptions
            ],
            "limitations": [
                item.model_dump(mode="json")
                for item in draft.limitations
            ],
            "recommendation": recommendation.model_dump(mode="json"),
            "model_provenance": None,
            "source_report_fingerprint": report.report_fingerprint,
            "decision_source_fingerprint": decision_source_fingerprint,
        }
        _, brief_fingerprint = _canonical_json(
            identity,
            code="P21_BRIEF_NOT_CANONICAL",
        )
        decision_brief_id = "p21b_" + brief_fingerprint[:24]

        objective_json = _canonical_json(
            draft.objective.model_dump(mode="json"),
            code="P21_OBJECTIVE_NOT_CANONICAL",
        )[0]
        constraints_json = _canonical_json(
            [item.model_dump(mode="json") for item in constraints],
            code="P21_CONSTRAINTS_NOT_CANONICAL",
        )[0]
        options_json = _canonical_json(
            [item.model_dump(mode="json") for item in draft.options],
            code="P21_OPTIONS_NOT_CANONICAL",
        )[0]
        tradeoffs_json = _canonical_json(
            [item.model_dump(mode="json") for item in tradeoffs],
            code="P21_TRADEOFFS_NOT_CANONICAL",
        )[0]
        recommendation_json = _canonical_json(
            recommendation.model_dump(mode="json"),
            code="P21_RECOMMENDATION_NOT_CANONICAL",
        )[0]
        premise_refs_json = _canonical_json(
            [item.model_dump(mode="json") for item in draft.premises],
            code="P21_PREMISES_NOT_CANONICAL",
        )[0]
        assumptions_json = _canonical_json(
            [item.model_dump(mode="json") for item in draft.assumptions],
            code="P21_ASSUMPTIONS_NOT_CANONICAL",
        )[0]
        limitations_json = _canonical_json(
            [item.model_dump(mode="json") for item in draft.limitations],
            code="P21_LIMITATIONS_NOT_CANONICAL",
        )[0]

        with Session(self._engine) as db:
            existing = db.get(DecisionBriefRecord, decision_brief_id)
            if existing is not None:
                if existing.brief_fingerprint != brief_fingerprint:
                    raise P21DecisionError(
                        "P21_BRIEF_IDENTITY_CONFLICT",
                        decision_brief_id,
                    )
                return self._hydrate(existing)

            previous = db.exec(
                select(DecisionBriefRecord)
                .where(
                    DecisionBriefRecord.tenant_binding
                    == report.tenant_binding
                )
                .where(DecisionBriefRecord.brief_key == draft.brief_key)
                .order_by(DecisionBriefRecord.revision.desc())
            ).first()
            revision = 1 if previous is None else previous.revision + 1
            parent = (
                None
                if previous is None
                else previous.decision_brief_id
            )
            row = DecisionBriefRecord(
                decision_brief_id=decision_brief_id,
                report_id=report.report_id,
                tenant_binding=report.tenant_binding,
                semantic_context_version=report.semantic_context_version,
                brief_key=draft.brief_key,
                revision=revision,
                parent_decision_brief_id=parent,
                objective_json=objective_json,
                constraints_json=constraints_json,
                options_json=options_json,
                tradeoffs_json=tradeoffs_json,
                recommendation_json=recommendation_json,
                premise_refs_json=premise_refs_json,
                assumptions_json=assumptions_json,
                limitations_json=limitations_json,
                model_provenance_json=None,
                source_report_fingerprint=report.report_fingerprint,
                decision_source_fingerprint=decision_source_fingerprint,
                brief_fingerprint=brief_fingerprint,
                created_at=_aware(now),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(
        self,
        *,
        decision_brief_id: str,
        principal: Principal,
    ) -> DecisionBrief:
        with Session(self._engine) as db:
            row = db.get(DecisionBriefRecord, decision_brief_id)
            if row is None or row.tenant_binding != _tenant(principal):
                raise P21DecisionError(
                    "P21_DECISION_BRIEF_UNAVAILABLE",
                    "decision brief unavailable in caller scope",
                )
            return self._hydrate(row)

    def currentness(
        self,
        *,
        decision_brief_id: str,
        principal: Principal,
    ) -> DecisionBriefCurrentness:
        brief = self.load(
            decision_brief_id=decision_brief_id,
            principal=principal,
        )
        try:
            report = self._reports.load(
                report_id=brief.report_id,
                principal=principal,
            )
            report_currentness = self._reports.currentness(
                report_id=brief.report_id,
                principal=principal,
            )
        except P20ReportError:
            return DecisionBriefCurrentness.STALE_SOURCE_REPORT
        if (
            report_currentness != ReportCurrentness.CURRENT
            or report.report_fingerprint
            != brief.source_report_fingerprint
        ):
            return DecisionBriefCurrentness.STALE_SOURCE_REPORT
        with Session(self._engine) as db:
            latest = db.exec(
                select(DecisionBriefRecord)
                .where(
                    DecisionBriefRecord.tenant_binding
                    == brief.tenant_binding
                )
                .where(DecisionBriefRecord.brief_key == brief.brief_key)
                .order_by(DecisionBriefRecord.revision.desc())
            ).first()
        if latest is None or latest.decision_brief_id != brief.decision_brief_id:
            return DecisionBriefCurrentness.SUPERSEDED
        return DecisionBriefCurrentness.CURRENT
