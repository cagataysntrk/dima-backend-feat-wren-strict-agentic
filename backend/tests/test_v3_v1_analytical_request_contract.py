from __future__ import annotations

import ast
import inspect

import pytest

from app.v3 import analytical_request_contract as request_module
from app.v3.analytical_request_contract import (
    AnalyticalRequestMismatch,
    AnalyticalScopeIdentity,
    analytical_request_contract_from_intent,
    assert_request_invariants,
    observation_from_contract,
)
from app.v3.analytics_contract import (
    PrincipalContextRef,
    ResolvedAnalyticsIntent,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedRanking,
    ResolvedSemanticRef,
)


def intent():
    return ResolvedAnalyticsIntent(
        authority_id="asa-v1-request",
        request_ref="req-v1-request",
        source_message_hash="a" * 64,
        projection_hash="b" * 64,
        semantic_context_version="ctx-v1-request",
        obligation_ids=("g1",),
        metrics=(
            ResolvedSemanticRef(
                semantic_ref="sem_metric_sales",
                source_candidate_id="metric.sales",
                kind="metric",
                canonical_name="Sales",
            ),
        ),
        dimensions=(
            ResolvedSemanticRef(
                semantic_ref="sem_dim_region",
                source_candidate_id="dimension.region",
                kind="dimension",
                canonical_name="Region",
            ),
        ),
        filters=(
            ResolvedFilterRef(
                semantic_ref="sem_filter_region_tr",
                source_candidate_id="entity.region.tr",
                dimension_name="Region",
                value="TR",
            ),
        ),
        period=ResolvedPeriod(
            kind="absolute",
            source_text="2026-Q3",
            time_dimension="orders.created_at",
            start="2026-07-01",
            end="2026-10-01",
        ),
        ranking=ResolvedRanking(
            measure="Sales",
            direction="desc",
            limit=5,
        ),
        grain_constraints=("region",),
        principal=PrincipalContextRef(
            tenant_binding="tenant-a",
            principal_subject="user-a",
            roles=("analyst",),
        ),
    )


def contract():
    return analytical_request_contract_from_intent(
        intent(),
        scope_lineage_id="atl_scope_a",
        scope_version_id="scope_v2",
        requested_output_surfaces=("table", "chart"),
    )


def test_matching_material_request_invariants_authorize_without_query_shape():
    item = contract()
    assert_request_invariants(item, observation_from_contract(item))


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("metric_refs", ("sem_metric_margin",), "ANALYTICAL_REQUEST_METRIC_MISMATCH"),
        ("dimension_refs", (), "ANALYTICAL_REQUEST_DIMENSION_MISMATCH"),
        ("grain_constraints", ("day",), "ANALYTICAL_REQUEST_GRAIN_MISMATCH"),
        ("requested_output_surfaces", ("table",), "ANALYTICAL_REQUEST_OUTPUT_SURFACE_MISMATCH"),
    ],
)
def test_material_request_drift_fails_closed(field, value, code):
    item = contract()
    observed = observation_from_contract(item).model_copy(update={field: value})
    with pytest.raises(AnalyticalRequestMismatch) as exc:
        assert_request_invariants(item, observed)
    assert exc.value.code == code


def test_period_filter_and_ranking_drift_fail_closed():
    item = contract()

    period_drift = observation_from_contract(item).model_copy(
        update={
            "period": item.period.model_copy(
                update={"start": "2026-08-01"}
            )
        }
    )
    with pytest.raises(AnalyticalRequestMismatch) as period_exc:
        assert_request_invariants(item, period_drift)
    assert period_exc.value.code == "ANALYTICAL_REQUEST_TIME_MISMATCH"

    filter_drift = observation_from_contract(item).model_copy(
        update={
            "filters": (
                item.filters[0].model_copy(update={"value": "DE"}),
            )
        }
    )
    with pytest.raises(AnalyticalRequestMismatch) as filter_exc:
        assert_request_invariants(item, filter_drift)
    assert filter_exc.value.code == "ANALYTICAL_REQUEST_FILTER_MISMATCH"

    ranking_drift = observation_from_contract(item).model_copy(
        update={
            "ranking": item.ranking.model_copy(update={"direction": "asc"})
        }
    )
    with pytest.raises(AnalyticalRequestMismatch) as ranking_exc:
        assert_request_invariants(item, ranking_drift)
    assert ranking_exc.value.code == "ANALYTICAL_REQUEST_RANKING_MISMATCH"


def test_scope_identity_is_lineage_plus_version_not_bare_ordinal():
    item = contract()
    observed = observation_from_contract(item).model_copy(
        update={
            "scope_identity": AnalyticalScopeIdentity(
                lineage_id="atl_other_conversation",
                version_id="scope_v2",
            )
        }
    )
    with pytest.raises(AnalyticalRequestMismatch) as exc:
        assert_request_invariants(item, observed)
    assert exc.value.code == "ANALYTICAL_REQUEST_SCOPE_MISMATCH"


def test_request_contract_module_has_no_query_planner_dependency_boundary():
    source = inspect.getsource(request_module)
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    forbidden_prefixes = (
        "sqlalchemy",
        "sqlmodel",
        "app.v3.native_standard",
        "app.v3.substrate",
    )
    assert not any(
        imported.startswith(forbidden_prefixes)
        for imported in imports
    ), imports
    fields = set(request_module.AnalyticalRequestContract.model_fields)
    assert fields == {
        "authority_id",
        "request_ref",
        "semantic_context_version",
        "scope_identity",
        "metric_refs",
        "dimension_refs",
        "filters",
        "period",
        "comparison",
        "temporal_observation",
        "ranking",
        "grain_constraints",
        "requested_output_surfaces",
    }


def test_v1_forward_authorize_does_not_delegate_to_historical_physical_certifier():
    from app.v3.native_standard.trust import NativeStandardTrustOrchestrator

    source = inspect.getsource(NativeStandardTrustOrchestrator.authorize_v1)
    forbidden = (
        "cls.authorize(",
        "cls._candidate(",
        "_assert_shape(",
        "_observed_metric(",
        "_observed_time(",
        "_observed_breakout(",
        "_observed_ranking(",
        "NativeCandidateAuthorizationGate",
    )
    for token in forbidden:
        assert token not in source, token


def test_forward_gateway_is_wired_into_canonical_native_runtime():
    import inspect as _inspect
    from app import main as main_module

    source = _inspect.getsource(main_module.lifespan)
    assert "NativeStandardExecutionGateway" in source
    assert "app.state.native_standard_gateway" in source
    assert "expected_engine=identity" in source
