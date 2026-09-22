"""Day7 governed construction of CrossDomainJoinGate facts.

The LLM/Manager may propose *which accepted semantic handles* to relate. It never
certifies model grain, Wren path, relationship cardinality, fanout health, time
compatibility or unit compatibility. Those facts are reconstructed here from accepted
opaque handles + current Wren schema.

Initial executable shape is intentionally narrow:
    source metric -> target model's governed row-key dimension

That shape uses exactly one metric and one target primary-key dimension. Time/unit
compatibility are NOT_APPLICABLE by construction because the primitive does not compare
two measures or combine units/time series. Broader analytical grains remain unsupported
until a governed primitive can prove them.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from app.v2.cross_domain_join import (
    CompatibilityState,
    CrossDomainJoinDecision,
    CrossDomainJoinGate,
    CrossDomainJoinRequest,
    JoinAggregation,
    JoinGateCode,
)
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationStatus,
)
from app.v2.manager_tools import RunRelationshipArgs
from app.v2.models import FrozenModel, ResolvedSemanticRef, SemanticTargetKind
from app.v2.semantic_handles import SemanticHandleRegistry


class JoinFactCode(StrEnum):
    READY = "READY"
    INVALID_OBLIGATION = "INVALID_OBLIGATION"
    HANDLE_OUTSIDE_AUTHORITY = "HANDLE_OUTSIDE_AUTHORITY"
    INVALID_HANDLE = "INVALID_HANDLE"
    UNSUPPORTED_HANDLE_SHAPE = "UNSUPPORTED_HANDLE_SHAPE"
    CUBE_SCOPE_AMBIGUOUS = "CUBE_SCOPE_AMBIGUOUS"
    MODEL_MAPPING_MISSING = "MODEL_MAPPING_MISSING"
    ROW_GRAIN_UNKNOWN = "ROW_GRAIN_UNKNOWN"
    TARGET_GRAIN_NOT_GOVERNED = "TARGET_GRAIN_NOT_GOVERNED"
    FANOUT_UNVERIFIED = "FANOUT_UNVERIFIED"
    FANOUT_UNSAFE = "FANOUT_UNSAFE"
    NO_WREN_PATH = "NO_WREN_PATH"
    AMBIGUOUS_WREN_PATH = "AMBIGUOUS_WREN_PATH"
    GATE_DENIED = "GATE_DENIED"


class FanoutFact(FrozenModel):
    relationship: str
    status: str
    certified: str
    certificate_mdl_version: str | None = None
    current_mdl_version: str | None = None
    measured_at: str | None = None


class CrossDomainJoinFacts(FrozenModel):
    obligation_id: str
    source_metric_handle: str
    target_dimension_handle: str

    source_cube: str
    target_cube: str
    source_model: str
    target_model: str

    source_row_grain: str
    target_row_grain: str
    requested_output_grain: str

    relationship_path: tuple[str, ...] = Field(min_length=1)
    cardinality_path: tuple[str, ...] = Field(min_length=1)
    fanout_proofs: tuple[FanoutFact, ...] = Field(min_length=1)

    aggregation: JoinAggregation
    time_alignment: CompatibilityState
    unit_compatibility: CompatibilityState
    mdl_version: str

    def to_gate_request(self) -> CrossDomainJoinRequest:
        return CrossDomainJoinRequest(
            source_model=self.source_model,
            target_model=self.target_model,
            source_grain=self.source_row_grain,
            target_grain=self.target_row_grain,
            requested_output_grain=self.requested_output_grain,
            relationship_path=self.relationship_path,
            aggregation=self.aggregation,
            time_alignment=self.time_alignment,
            unit_compatibility=self.unit_compatibility,
        )


class CrossDomainJoinFactResult(FrozenModel):
    ready: bool
    code: JoinFactCode
    facts: CrossDomainJoinFacts | None = None
    fanout_proofs: tuple[FanoutFact, ...] = ()
    gate_decision: CrossDomainJoinDecision | None = None
    reason: str


class CrossDomainJoinFactBuilder:
    """Deterministic bridge from accepted semantic authority to join-gate facts."""

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        tenant_binding: str,
        context_version: str,
    ) -> None:
        self._handles = semantic_handles
        self._tenant = tenant_binding
        self._context_version = context_version
        self._gate = CrossDomainJoinGate()

    @staticmethod
    def _fail(
        code: JoinFactCode,
        reason: str,
        *,
        fanout_proofs: tuple[FanoutFact, ...] = (),
    ) -> CrossDomainJoinFactResult:
        return CrossDomainJoinFactResult(
            ready=False,
            code=code,
            fanout_proofs=fanout_proofs,
            reason=reason,
        )

    def _binding(self, handle_id: str):
        try:
            return self._handles.binding_for_execution(
                handle_id,
                tenant_binding=self._tenant,
                context_version=self._context_version,
            )
        except (KeyError, ValueError) as exc:
            raise ValueError(f"invalid accepted semantic handle {handle_id}: {exc}") from exc

    @staticmethod
    def _one_cube(ref: ResolvedSemanticRef) -> str:
        cubes = tuple(dict.fromkeys(ref.cube_names))
        if len(cubes) != 1:
            raise LookupError(
                f"semantic ref requires exactly one governed cube; got {cubes}"
            )
        return cubes[0]

    @staticmethod
    def _cube_model(schema: dict, cube_name: str) -> str | None:
        cube = next(
            (
                item
                for item in tuple(schema.get("cubes") or ())
                if item.get("name") == cube_name
            ),
            None,
        )
        if not isinstance(cube, dict):
            return None
        base = cube.get("base_object")
        return str(base) if base else None

    @staticmethod
    def _model(schema: dict, model_name: str) -> dict | None:
        return next(
            (
                item
                for item in tuple(schema.get("models") or ())
                if item.get("name") == model_name
            ),
            None,
        )

    @staticmethod
    def _directed_paths(
        schema: dict,
        *,
        source_model: str,
        target_model: str,
        max_hops: int = 2,
    ) -> tuple[tuple[dict, ...], ...]:
        relationships = tuple(
            item
            for item in tuple(schema.get("relationships") or ())
            if isinstance(item, dict)
            and item.get("name")
            and len(tuple(item.get("models") or ())) == 2
        )
        paths: list[tuple[dict, ...]] = []

        def walk(current: str, path: tuple[dict, ...], visited: frozenset[str]):
            if len(path) >= max_hops:
                return
            for relation in relationships:
                models = tuple(str(x) for x in relation.get("models") or ())
                if models[0] != current:
                    continue
                nxt = models[1]
                if nxt in visited:
                    continue
                next_path = (*path, relation)
                if nxt == target_model:
                    paths.append(next_path)
                else:
                    walk(nxt, next_path, visited | {nxt})

        walk(source_model, (), frozenset({source_model}))
        return tuple(paths)

    def build(
        self,
        *,
        args: RunRelationshipArgs,
        obligation: ObligationLedgerItem,
        service,
    ) -> CrossDomainJoinFactResult:
        if (
            obligation.obligation_id != args.obligation_id
            or obligation.capability_key != ManagerCapabilityKey.RELATIONSHIP
            or obligation.status == ObligationStatus.SUPERSEDED
        ):
            return self._fail(
                JoinFactCode.INVALID_OBLIGATION,
                "relationship facts require active accepted RELATIONSHIP obligation",
            )

        requested_handles = {
            *args.focus_handles,
            *args.counterpart_handles,
        }
        if not requested_handles.issubset(set(obligation.semantic_handle_refs)):
            return self._fail(
                JoinFactCode.HANDLE_OUTSIDE_AUTHORITY,
                "relationship handle is outside accepted obligation semantic authority",
            )
        if len(args.focus_handles) != 1 or len(args.counterpart_handles) != 1:
            return self._fail(
                JoinFactCode.UNSUPPORTED_HANDLE_SHAPE,
                "initial governed relationship primitive requires one focus metric and one counterpart dimension",
            )

        try:
            source_binding = self._binding(args.focus_handles[0])
            target_binding = self._binding(args.counterpart_handles[0])
        except ValueError as exc:
            return self._fail(JoinFactCode.INVALID_HANDLE, str(exc))

        source_ref = source_binding.canonical_target
        target_ref = target_binding.canonical_target
        if (
            not isinstance(source_ref, ResolvedSemanticRef)
            or source_ref.target_kind != SemanticTargetKind.METRIC
            or not isinstance(target_ref, ResolvedSemanticRef)
            or target_ref.target_kind != SemanticTargetKind.DIMENSION
        ):
            return self._fail(
                JoinFactCode.UNSUPPORTED_HANDLE_SHAPE,
                "initial relationship primitive requires metric -> dimension semantic refs",
            )

        try:
            source_cube = self._one_cube(source_ref)
            target_cube = self._one_cube(target_ref)
        except LookupError as exc:
            return self._fail(JoinFactCode.CUBE_SCOPE_AMBIGUOUS, str(exc))

        schema = service.schema()
        current_mdl = str(service.mdl_version)
        source_model = self._cube_model(schema, source_cube)
        target_model = self._cube_model(schema, target_cube)
        if not source_model or not target_model:
            return self._fail(
                JoinFactCode.MODEL_MAPPING_MISSING,
                "accepted cube does not expose a governed Wren base_object",
            )
        if source_model == target_model:
            return self._fail(
                JoinFactCode.UNSUPPORTED_HANDLE_SHAPE,
                "relationship primitive requires distinct governed Wren models",
            )

        source_meta = self._model(schema, source_model)
        target_meta = self._model(schema, target_model)
        source_pk = (
            str(source_meta.get("primary_key"))
            if isinstance(source_meta, dict) and source_meta.get("primary_key")
            else None
        )
        target_pk = (
            str(target_meta.get("primary_key"))
            if isinstance(target_meta, dict) and target_meta.get("primary_key")
            else None
        )
        if not source_pk or not target_pk:
            return self._fail(
                JoinFactCode.ROW_GRAIN_UNKNOWN,
                "material model row grain is UNKNOWN; primary_key is not declared",
            )

        # This is NOT a universal analytical-grain inference. The initial primitive is
        # explicitly target-row breakdown, so the accepted counterpart must itself be
        # the governed target primary-key dimension.
        if target_ref.canonical_name != target_pk:
            return self._fail(
                JoinFactCode.TARGET_GRAIN_NOT_GOVERNED,
                "counterpart dimension is not the governed target row-key; broader analytical grain unsupported",
            )

        paths = self._directed_paths(
            schema,
            source_model=source_model,
            target_model=target_model,
        )
        if not paths:
            return self._fail(
                JoinFactCode.NO_WREN_PATH,
                "no directed Wren relationship path connects accepted source/target models",
            )
        if len(paths) != 1:
            return self._fail(
                JoinFactCode.AMBIGUOUS_WREN_PATH,
                "multiple Wren relationship paths exist; fact construction refuses auto-pick",
            )

        path = paths[0]
        proofs: list[FanoutFact] = []
        cardinalities: list[str] = []
        for relation in path:
            raw_proof = relation.get("fanout_proof")
            if not isinstance(raw_proof, dict):
                return self._fail(
                    JoinFactCode.FANOUT_UNVERIFIED,
                    f"relationship {relation.get('name')} lacks version-bound fanout proof",
                )
            proof = FanoutFact.model_validate(raw_proof)
            proofs.append(proof)
            current_proofs = tuple(proofs)

            if (
                proof.current_mdl_version != current_mdl
                or proof.certificate_mdl_version != current_mdl
                or not proof.measured_at
            ):
                return self._fail(
                    JoinFactCode.FANOUT_UNVERIFIED,
                    (
                        f"relationship {relation.get('name')} fanout proof is not bound "
                        f"to current MDL {current_mdl}"
                    ),
                    fanout_proofs=current_proofs,
                )
            if proof.status == "RISKY" or proof.certified == "olculdu:riskli":
                return self._fail(
                    JoinFactCode.FANOUT_UNSAFE,
                    f"relationship {relation.get('name')} measured fanout is unsafe",
                    fanout_proofs=current_proofs,
                )
            if proof.status != "HEALTHY" or proof.certified != "olculdu:saglikli":
                return self._fail(
                    JoinFactCode.FANOUT_UNVERIFIED,
                    f"relationship {relation.get('name')} fanout proof is not healthy",
                    fanout_proofs=current_proofs,
                )
            cardinalities.append(str(relation.get("join_type") or ""))

        facts = CrossDomainJoinFacts(
            obligation_id=args.obligation_id,
            source_metric_handle=args.focus_handles[0],
            target_dimension_handle=args.counterpart_handles[0],
            source_cube=source_cube,
            target_cube=target_cube,
            source_model=source_model,
            target_model=target_model,
            source_row_grain=source_pk,
            target_row_grain=target_pk,
            requested_output_grain=target_pk,
            relationship_path=tuple(str(item["name"]) for item in path),
            cardinality_path=tuple(cardinalities),
            fanout_proofs=tuple(proofs),
            aggregation=JoinAggregation.PRE_AGGREGATE_TO_TARGET,
            # For this exact primitive only: one source metric grouped by target row key.
            # No two-measure arithmetic and no cross-domain temporal comparison occurs.
            time_alignment=CompatibilityState.NOT_APPLICABLE,
            unit_compatibility=CompatibilityState.NOT_APPLICABLE,
            mdl_version=current_mdl,
        )
        decision = self._gate.decide(
            schema=schema,
            request=facts.to_gate_request(),
        )
        if not decision.allowed:
            return CrossDomainJoinFactResult(
                ready=False,
                code=JoinFactCode.GATE_DENIED,
                facts=facts,
                gate_decision=decision,
                reason=f"CrossDomainJoinGate denied: {decision.code.value}: {decision.reason}",
            )

        return CrossDomainJoinFactResult(
            ready=True,
            code=JoinFactCode.READY,
            facts=facts,
            fanout_proofs=tuple(proofs),
            gate_decision=decision,
            reason="governed handles + Wren row grain/path + version-bound fanout proof verified",
        )
