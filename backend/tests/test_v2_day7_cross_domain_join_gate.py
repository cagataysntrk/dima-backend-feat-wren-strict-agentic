"""Provider-free Day 7 attacks for CrossDomainJoinGate."""

from __future__ import annotations

from app.v2.cross_domain_join import (
    CompatibilityState,
    CrossDomainJoinGate,
    CrossDomainJoinRequest,
    JoinAggregation,
    JoinGateCode,
)


def _rel(
    name: str,
    source: str,
    target: str,
    *,
    join_type: str = "MANY_TO_ONE",
    certified: str = "olculdu:saglikli",
) -> dict:
    return {
        "name": name,
        "models": [source, target],
        "join_type": join_type,
        "condition": f'{source}."target_id" = {target}."id"',
        "certified": certified,
    }


def _request(
    *,
    source="orders",
    target="customers",
    source_grain="order_id",
    target_grain="customer_id",
    output_grain="order_id",
    target_analysis_grain=None,
    path=(),
    aggregation=JoinAggregation.PRESERVE_SOURCE_GRAIN,
    time=CompatibilityState.COMPATIBLE,
    unit=CompatibilityState.COMPATIBLE,
):
    return CrossDomainJoinRequest(
        source_model=source,
        target_model=target,
        source_grain=source_grain,
        target_grain=target_grain,
        target_analysis_grain=target_analysis_grain,
        requested_output_grain=output_grain,
        relationship_path=tuple(path),
        aggregation=aggregation,
        time_alignment=time,
        unit_compatibility=unit,
    )


def test_approved_many_to_one_wren_path_is_allowed():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}

    decision = CrossDomainJoinGate().decide(schema=schema, request=_request())

    assert decision.allowed is True
    assert decision.code == JoinGateCode.ALLOW
    assert decision.relationship_path == ("orders_customer",)
    assert decision.model_path == ("orders", "customers")


def test_approved_bridge_path_requires_explicit_safe_aggregation():
    schema = {
        "relationships": [
            _rel("orders_bridge", "orders", "customer_bridge"),
            _rel("bridge_customer", "customer_bridge", "customers"),
        ]
    }
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(
            path=("orders_bridge", "bridge_customer"),
            output_grain="customer_id",
            aggregation=JoinAggregation.PRE_AGGREGATE_TO_TARGET,
        ),
    )

    assert decision.allowed is True
    assert decision.relationship_path == ("orders_bridge", "bridge_customer")
    assert decision.required_aggregation == JoinAggregation.PRE_AGGREGATE_TO_TARGET


def test_missing_wren_path_denies_even_if_request_has_models():
    decision = CrossDomainJoinGate().decide(
        schema={"relationships": []},
        request=_request(),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.NO_WREN_PATH


def test_ambiguous_wren_path_requires_explicit_relationship_binding():
    schema = {
        "relationships": [
            _rel("orders_customer_a", "orders", "customers"),
            _rel("orders_customer_b", "orders", "customers"),
        ]
    }
    decision = CrossDomainJoinGate().decide(schema=schema, request=_request())
    assert decision.allowed is False
    assert decision.code == JoinGateCode.AMBIGUOUS_WREN_PATH


def test_many_to_many_is_unsafe_even_when_named_and_certified():
    schema = {
        "relationships": [
            _rel(
                "orders_tags",
                "orders",
                "tags",
                join_type="MANY_TO_MANY",
            )
        ]
    }
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(target="tags", target_grain="tag_id"),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.UNSAFE_CARDINALITY


def test_requested_grain_outside_governed_source_or_target_denies():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(output_grain="household_id"),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.GRAIN_MISMATCH


def test_target_grain_without_required_preaggregation_denies():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(
            output_grain="customer_id",
            aggregation=JoinAggregation.PRESERVE_SOURCE_GRAIN,
        ),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.AGGREGATION_REQUIRED
    assert decision.required_aggregation == JoinAggregation.PRE_AGGREGATE_TO_TARGET


def test_time_mismatch_or_unknown_denies():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    for state in (CompatibilityState.MISMATCH, CompatibilityState.UNKNOWN):
        decision = CrossDomainJoinGate().decide(
            schema=schema,
            request=_request(time=state),
        )
        assert decision.allowed is False
        assert decision.code == JoinGateCode.TIME_MISMATCH


def test_unit_or_currency_mismatch_or_unknown_denies():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    for state in (CompatibilityState.MISMATCH, CompatibilityState.UNKNOWN):
        decision = CrossDomainJoinGate().decide(
            schema=schema,
            request=_request(unit=state),
        )
        assert decision.allowed is False
        assert decision.code == JoinGateCode.UNIT_MISMATCH


def test_physical_fk_without_wren_relationship_is_not_authority():
    schema = {
        "relationships": [],
        "physical_foreign_keys": [
            {"source": "orders.customer_id", "target": "customers.id"}
        ],
    }
    decision = CrossDomainJoinGate().decide(schema=schema, request=_request())
    assert decision.allowed is False
    assert decision.code == JoinGateCode.NO_WREN_PATH


def test_measured_fanout_risk_denies_execution():
    schema = {
        "relationships": [
            _rel(
                "orders_customer",
                "orders",
                "customers",
                certified="olculdu:riskli",
            )
        ]
    }
    decision = CrossDomainJoinGate().decide(schema=schema, request=_request())
    assert decision.allowed is False
    assert decision.code == JoinGateCode.FANOUT_UNSAFE


def test_unmeasured_relationship_denies_execution():
    schema = {
        "relationships": [
            _rel(
                "orders_customer",
                "orders",
                "customers",
                certified="olculmedi",
            )
        ]
    }
    decision = CrossDomainJoinGate().decide(schema=schema, request=_request())
    assert decision.allowed is False
    assert decision.code == JoinGateCode.FANOUT_UNVERIFIED


def test_reverse_one_to_many_direction_is_not_silently_inverted():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(
            source="customers",
            target="orders",
            source_grain="customer_id",
            target_grain="order_id",
            path=("orders_customer",),
        ),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.INVALID_WREN_PATH



def test_governed_target_attribute_grain_is_allowed_only_with_explicit_aggregation():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(
            output_grain="segment",
            target_analysis_grain="segment",
            aggregation=JoinAggregation.GROUP_BY_TARGET_ATTRIBUTE,
            time=CompatibilityState.NOT_APPLICABLE,
            unit=CompatibilityState.NOT_APPLICABLE,
        ),
    )
    assert decision.allowed is True
    assert decision.code == JoinGateCode.ALLOW
    assert decision.required_aggregation == JoinAggregation.GROUP_BY_TARGET_ATTRIBUTE


def test_arbitrary_target_attribute_without_governed_analysis_grain_is_denied():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(
            output_grain="segment",
            aggregation=JoinAggregation.GROUP_BY_TARGET_ATTRIBUTE,
        ),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.GRAIN_MISMATCH


def test_governed_target_attribute_requires_exact_grouping_aggregation():
    schema = {"relationships": [_rel("orders_customer", "orders", "customers")]}
    decision = CrossDomainJoinGate().decide(
        schema=schema,
        request=_request(
            output_grain="segment",
            target_analysis_grain="segment",
            aggregation=JoinAggregation.PRE_AGGREGATE_TO_TARGET,
        ),
    )
    assert decision.allowed is False
    assert decision.code == JoinGateCode.AGGREGATION_REQUIRED
    assert decision.required_aggregation == JoinAggregation.GROUP_BY_TARGET_ATTRIBUTE
