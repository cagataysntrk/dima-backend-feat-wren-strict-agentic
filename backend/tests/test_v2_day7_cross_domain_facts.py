"""Provider-free Day7 attacks for governed CrossDomainJoinFacts construction."""

from __future__ import annotations

from app.v2.cross_domain_facts import (
    CrossDomainJoinFactBuilder,
    JoinFactCode,
)
from app.v2.cross_domain_join import (
    CompatibilityState,
    JoinAggregation,
    JoinGateCode,
)
from app.v2.manager_models import (
    ManagerCapabilityKey,
    ObligationLedgerItem,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    ObligationStatus,
)
from app.v2.manager_tools import RunRelationshipArgs
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.semantic_handles import SemanticHandleRegistry


class _Service:
    def __init__(self, schema: dict, *, mdl_version: str = "mdl-current") -> None:
        self._schema = schema
        self.mdl_version = mdl_version

    def schema(self):
        return self._schema


def _proof(name: str, *, current="mdl-current", certificate="mdl-current", status="HEALTHY"):
    certified = {
        "HEALTHY": "olculdu:saglikli",
        "RISKY": "olculdu:riskli",
    }.get(status, "olculmedi")
    return {
        "relationship": name,
        "status": status,
        "certified": certified,
        "certificate_mdl_version": certificate,
        "current_mdl_version": current,
        "measured_at": "2026-09-22T20:00:00+00:00",
    }


def _schema(*, source_pk="order_id", target_pk="customer_id", relationships=None):
    rels = relationships
    if rels is None:
        rels = [
            {
                "name": "orders_customer",
                "models": ["orders", "customers"],
                "join_type": "MANY_TO_ONE",
                "condition": 'orders."customer_id" = customers."customer_id"',
                "certified": "olculdu:saglikli",
                "fanout_proof": _proof("orders_customer"),
            }
        ]
    return {
        "models": [
            {
                "name": "orders",
                **({} if source_pk is None else {"primary_key": source_pk}),
                "columns": [],
            },
            {
                "name": "customers",
                **({} if target_pk is None else {"primary_key": target_pk}),
                "columns": [],
            },
        ],
        "cubes": [
            {"name": "sales", "base_object": "orders"},
            {"name": "customer", "base_object": "customers"},
        ],
        "relationships": rels,
    }


def _context(*, target_dimension="customer_id", target_tenant="tenant-a"):
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-revenue",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-revenue",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="revenue",
            cube_names=("sales",),
        ),
    )
    target = handles.mint_from_resolver(
        tenant_binding=target_tenant,
        context_version="ctx-1",
        resolver_provenance_id="dim-customer",
        target_kind="dimension",
        canonical_target=ResolvedSemanticRef(
            candidate_id="dim-customer",
            target_kind=SemanticTargetKind.DIMENSION,
            canonical_name=target_dimension,
            cube_names=("customer",),
        ),
    )
    obligation = ObligationLedgerItem(
        obligation_id="U_REL",
        capability_key=ManagerCapabilityKey.RELATIONSHIP,
        origin=ObligationOrigin.USER_MUST,
        priority=ObligationPriority.MUST,
        polarity=ObligationPolarity.REQUIRED,
        status=ObligationStatus.ACCEPTED,
        source_refs=("src-rel",),
        semantic_handle_refs=(metric.handle_id, target.handle_id),
        introduced_in_version=1,
    )
    args = RunRelationshipArgs(
        obligation_id="U_REL",
        focus_handles=(metric.handle_id,),
        counterpart_handles=(target.handle_id,),
    )
    builder = CrossDomainJoinFactBuilder(
        semantic_handles=handles,
        tenant_binding="tenant-a",
        context_version="ctx-1",
    )
    return builder, obligation, args, metric.handle_id, target.handle_id


def test_governed_sources_build_exact_gate_facts_without_caller_supplied_grain():
    builder, obligation, args, metric_handle, target_handle = _context()
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema()),
    )

    assert result.ready is True
    assert result.code == JoinFactCode.READY
    assert result.facts is not None
    assert result.gate_decision is not None
    assert result.gate_decision.allowed is True
    assert result.gate_decision.code == JoinGateCode.ALLOW

    facts = result.facts
    assert facts.source_metric_handle == metric_handle
    assert facts.target_dimension_handle == target_handle
    assert facts.source_model == "orders"
    assert facts.target_model == "customers"
    assert facts.source_row_grain == "order_id"
    assert facts.target_row_grain == "customer_id"
    assert facts.requested_output_grain == "customer_id"
    assert facts.relationship_path == ("orders_customer",)
    assert facts.aggregation == JoinAggregation.PRE_AGGREGATE_TO_TARGET
    assert facts.time_alignment == CompatibilityState.NOT_APPLICABLE
    assert facts.unit_compatibility == CompatibilityState.NOT_APPLICABLE
    assert facts.fanout_proofs[0].certificate_mdl_version == "mdl-current"
    assert facts.fanout_proofs[0].current_mdl_version == "mdl-current"


def test_relationship_handle_outside_accepted_obligation_is_denied():
    builder, obligation, args, _, target_handle = _context()
    obligation = obligation.model_copy(
        update={"semantic_handle_refs": (target_handle,)}
    )
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema()),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.HANDLE_OUTSIDE_AUTHORITY


def test_foreign_tenant_handle_is_invalid_even_if_declared_in_obligation():
    builder, obligation, args, _, _ = _context(target_tenant="tenant-b")
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema()),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.INVALID_HANDLE


def test_missing_declared_row_grain_denies_instead_of_inferring_from_names():
    builder, obligation, args, _, _ = _context()
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema(source_pk=None)),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.ROW_GRAIN_UNKNOWN


def test_target_dimension_not_equal_governed_target_row_key_is_not_promoted_to_grain():
    builder, obligation, args, _, _ = _context(target_dimension="segment")
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema()),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.TARGET_GRAIN_NOT_GOVERNED


def test_stale_fanout_proof_denies_even_when_relationship_label_says_healthy():
    relationship = {
        "name": "orders_customer",
        "models": ["orders", "customers"],
        "join_type": "MANY_TO_ONE",
        "condition": 'orders."customer_id" = customers."customer_id"',
        # Attacker/stale surface cannot override the version-bound proof.
        "certified": "olculdu:saglikli",
        "fanout_proof": _proof(
            "orders_customer",
            current="mdl-current",
            certificate="mdl-old",
            status="MDL_MISMATCH",
        ),
    }
    builder, obligation, args, _, _ = _context()
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema(relationships=[relationship])),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.FANOUT_UNVERIFIED
    assert result.gate_decision is None
    # Stale display badge cannot launder a stale proof into gate authority.
    assert result.fanout_proofs[0].status == "MDL_MISMATCH"


def test_physical_fk_without_wren_business_relationship_is_never_authority():
    schema = _schema(relationships=[])
    schema["physical_foreign_keys"] = [
        {"source": "orders.customer_id", "target": "customers.customer_id"}
    ]
    builder, obligation, args, _, _ = _context()
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(schema),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.NO_WREN_PATH


def test_multiple_wren_paths_are_not_auto_picked():
    rels = [
        {
            "name": "orders_customer_a",
            "models": ["orders", "customers"],
            "join_type": "MANY_TO_ONE",
            "condition": 'orders."customer_id" = customers."customer_id"',
            "certified": "olculdu:saglikli",
            "fanout_proof": _proof("orders_customer_a"),
        },
        {
            "name": "orders_customer_b",
            "models": ["orders", "customers"],
            "join_type": "MANY_TO_ONE",
            "condition": 'orders."billing_customer_id" = customers."customer_id"',
            "certified": "olculdu:saglikli",
            "fanout_proof": _proof("orders_customer_b"),
        },
    ]
    builder, obligation, args, _, _ = _context()
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema(relationships=rels)),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.AMBIGUOUS_WREN_PATH


def test_risky_current_certificate_is_denied_by_existing_join_gate():
    relationship = {
        "name": "orders_customer",
        "models": ["orders", "customers"],
        "join_type": "MANY_TO_ONE",
        "condition": 'orders."customer_id" = customers."customer_id"',
        "certified": "olculdu:riskli",
        "fanout_proof": _proof("orders_customer", status="RISKY"),
    }
    builder, obligation, args, _, _ = _context()
    result = builder.build(
        args=args,
        obligation=obligation,
        service=_Service(_schema(relationships=[relationship])),
    )
    assert result.ready is False
    assert result.code == JoinFactCode.FANOUT_UNSAFE
    assert result.gate_decision is None
    assert result.fanout_proofs[0].status == "RISKY"
