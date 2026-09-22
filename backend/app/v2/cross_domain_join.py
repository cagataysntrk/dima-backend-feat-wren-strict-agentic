"""Day 7 fail-closed CrossDomainJoinGate.

The gate is NOT a join planner and never treats a physical FK/name match as authority.
It consumes only explicit Wren relationships already exported in schema plus the
existing fanout certificate stamp.  Grain/time/unit/aggregation compatibility must be
provided as typed governed facts; unknown material facts deny execution.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from app.v2.models import FrozenModel


class JoinGateCode(StrEnum):
    ALLOW = "ALLOW"
    NO_WREN_PATH = "NO_WREN_PATH"
    AMBIGUOUS_WREN_PATH = "AMBIGUOUS_WREN_PATH"
    INVALID_WREN_PATH = "INVALID_WREN_PATH"
    UNSAFE_CARDINALITY = "UNSAFE_CARDINALITY"
    FANOUT_UNVERIFIED = "FANOUT_UNVERIFIED"
    FANOUT_UNSAFE = "FANOUT_UNSAFE"
    GRAIN_MISMATCH = "GRAIN_MISMATCH"
    AGGREGATION_REQUIRED = "AGGREGATION_REQUIRED"
    TIME_MISMATCH = "TIME_MISMATCH"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    PATH_TOO_DEEP = "PATH_TOO_DEEP"


class JoinAggregation(StrEnum):
    PRESERVE_SOURCE_GRAIN = "PRESERVE_SOURCE_GRAIN"
    PRE_AGGREGATE_TO_TARGET = "PRE_AGGREGATE_TO_TARGET"


class CompatibilityState(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


class CrossDomainJoinRequest(FrozenModel):
    source_model: str = Field(min_length=1)
    target_model: str = Field(min_length=1)
    source_grain: str = Field(min_length=1)
    target_grain: str = Field(min_length=1)
    requested_output_grain: str = Field(min_length=1)
    relationship_path: tuple[str, ...] = ()
    aggregation: JoinAggregation
    time_alignment: CompatibilityState
    unit_compatibility: CompatibilityState
    max_relationship_hops: int = Field(default=2, ge=1, le=4)

    @model_validator(mode="after")
    def _different_domains(self):
        if self.source_model == self.target_model:
            raise ValueError("CrossDomainJoinGate requires distinct source/target models")
        return self


class CrossDomainJoinDecision(FrozenModel):
    allowed: bool
    code: JoinGateCode
    relationship_path: tuple[str, ...] = ()
    model_path: tuple[str, ...] = ()
    cardinality_path: tuple[str, ...] = ()
    required_aggregation: JoinAggregation | None = None
    reason: str


class CrossDomainJoinGate:
    """Prove a Wren-approved many-to-one path without inventing relationship truth."""

    _SAFE_JOIN_TYPES = {
        "MANY_TO_ONE",
        "MANY-TO-ONE",
        "MANY2ONE",
    }

    @staticmethod
    def _norm_join_type(value: object) -> str:
        return str(value or "").strip().upper().replace(" ", "_")

    @staticmethod
    def _relationships(schema: dict) -> tuple[dict, ...]:
        return tuple(
            item
            for item in tuple(schema.get("relationships") or ())
            if isinstance(item, dict) and item.get("name")
        )

    def _select_path(
        self,
        *,
        schema: dict,
        request: CrossDomainJoinRequest,
    ) -> tuple[dict, ...] | CrossDomainJoinDecision:
        relationships = self._relationships(schema)
        by_name = {str(item["name"]): item for item in relationships}

        if request.relationship_path:
            if len(request.relationship_path) > request.max_relationship_hops:
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.PATH_TOO_DEEP,
                    relationship_path=request.relationship_path,
                    reason="declared Wren relationship path exceeds bounded hop limit",
                )
            missing = [name for name in request.relationship_path if name not in by_name]
            if missing:
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.NO_WREN_PATH,
                    relationship_path=request.relationship_path,
                    reason="relationship is not present in Wren schema: " + ", ".join(missing),
                )
            return tuple(by_name[name] for name in request.relationship_path)

        direct = [
            item
            for item in relationships
            if tuple(item.get("models") or ()) == (
                request.source_model,
                request.target_model,
            )
        ]
        if not direct:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.NO_WREN_PATH,
                reason="no explicit Wren relationship connects source to target",
            )
        if len(direct) > 1:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.AMBIGUOUS_WREN_PATH,
                relationship_path=tuple(str(item["name"]) for item in direct),
                reason="multiple Wren relationships exist; caller must bind one explicit path",
            )
        return (direct[0],)

    def decide(
        self,
        *,
        schema: dict,
        request: CrossDomainJoinRequest,
    ) -> CrossDomainJoinDecision:
        selected = self._select_path(schema=schema, request=request)
        if isinstance(selected, CrossDomainJoinDecision):
            return selected

        current = request.source_model
        model_path = [current]
        relationship_names: list[str] = []
        cardinalities: list[str] = []

        for relation in selected:
            name = str(relation.get("name"))
            models = tuple(str(x) for x in (relation.get("models") or ()))
            if len(models) != 2 or current != models[0]:
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.INVALID_WREN_PATH,
                    relationship_path=tuple(relationship_names + [name]),
                    model_path=tuple(model_path),
                    reason=(
                        "Wren path is not a contiguous source→target path in declared "
                        "many-side to one-side order"
                    ),
                )

            join_type = self._norm_join_type(relation.get("join_type"))
            if join_type not in self._SAFE_JOIN_TYPES:
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.UNSAFE_CARDINALITY,
                    relationship_path=tuple(relationship_names + [name]),
                    model_path=tuple(model_path + [models[1]]),
                    cardinality_path=tuple(cardinalities + [join_type or "UNKNOWN"]),
                    reason="relationship cardinality is not governed MANY_TO_ONE",
                )

            certified = str(relation.get("certified") or "")
            if certified == "olculdu:riskli":
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.FANOUT_UNSAFE,
                    relationship_path=tuple(relationship_names + [name]),
                    model_path=tuple(model_path + [models[1]]),
                    cardinality_path=tuple(cardinalities + [join_type]),
                    reason="existing fanout certificate marks Wren relationship unsafe",
                )
            if certified != "olculdu:saglikli":
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.FANOUT_UNVERIFIED,
                    relationship_path=tuple(relationship_names + [name]),
                    model_path=tuple(model_path + [models[1]]),
                    cardinality_path=tuple(cardinalities + [join_type]),
                    reason="Wren relationship lacks a healthy measured fanout certificate",
                )
            if not str(relation.get("condition") or "").strip():
                return CrossDomainJoinDecision(
                    allowed=False,
                    code=JoinGateCode.INVALID_WREN_PATH,
                    relationship_path=tuple(relationship_names + [name]),
                    reason="Wren relationship has no explicit join condition",
                )

            relationship_names.append(name)
            cardinalities.append(join_type)
            current = models[1]
            model_path.append(current)

        if current != request.target_model:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.INVALID_WREN_PATH,
                relationship_path=tuple(relationship_names),
                model_path=tuple(model_path),
                cardinality_path=tuple(cardinalities),
                reason="declared Wren path does not terminate at requested target model",
            )

        if request.time_alignment not in {
            CompatibilityState.COMPATIBLE,
            CompatibilityState.NOT_APPLICABLE,
        }:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.TIME_MISMATCH,
                relationship_path=tuple(relationship_names),
                model_path=tuple(model_path),
                cardinality_path=tuple(cardinalities),
                reason=f"time alignment is {request.time_alignment.value}; execution denied",
            )

        if request.unit_compatibility not in {
            CompatibilityState.COMPATIBLE,
            CompatibilityState.NOT_APPLICABLE,
        }:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.UNIT_MISMATCH,
                relationship_path=tuple(relationship_names),
                model_path=tuple(model_path),
                cardinality_path=tuple(cardinalities),
                reason=f"unit/currency compatibility is {request.unit_compatibility.value}",
            )

        if request.requested_output_grain == request.source_grain:
            required = JoinAggregation.PRESERVE_SOURCE_GRAIN
        elif request.requested_output_grain == request.target_grain:
            required = JoinAggregation.PRE_AGGREGATE_TO_TARGET
        else:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.GRAIN_MISMATCH,
                relationship_path=tuple(relationship_names),
                model_path=tuple(model_path),
                cardinality_path=tuple(cardinalities),
                reason="requested analytical grain is neither governed source nor target grain",
            )

        if request.aggregation != required:
            return CrossDomainJoinDecision(
                allowed=False,
                code=JoinGateCode.AGGREGATION_REQUIRED,
                relationship_path=tuple(relationship_names),
                model_path=tuple(model_path),
                cardinality_path=tuple(cardinalities),
                required_aggregation=required,
                reason=(
                    f"requested grain requires {required.value}; "
                    f"received {request.aggregation.value}"
                ),
            )

        return CrossDomainJoinDecision(
            allowed=True,
            code=JoinGateCode.ALLOW,
            relationship_path=tuple(relationship_names),
            model_path=tuple(model_path),
            cardinality_path=tuple(cardinalities),
            required_aggregation=required,
            reason=(
                "explicit Wren path + measured healthy fanout + grain/aggregation/"
                "time/unit compatibility proven"
            ),
        )
