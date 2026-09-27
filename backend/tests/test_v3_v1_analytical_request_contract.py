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
        "ranking",
        "grain_constraints",
        "requested_output_surfaces",
    }


def test_v1_native_entry_blocks_request_drift_before_historical_trust(monkeypatch):
    from app.v3.native_execution import NativeCandidateOutcome
    from app.v3.native_standard.trust import NativeStandardTrustOrchestrator

    item = contract()
    drifted = observation_from_contract(item).model_copy(
        update={"metric_refs": ("sem_metric_wrong",)}
    )
    called = {"value": False}

    def should_not_run(cls, **kwargs):
        called["value"] = True
        raise AssertionError("retained trust must not run after request mismatch")

    monkeypatch.setattr(
        NativeStandardTrustOrchestrator,
        "authorize",
        classmethod(should_not_run),
    )
    result = NativeStandardTrustOrchestrator.authorize_v1(
        request_contract=item,
        request_observation=drifted,
    )
    assert result.authorization.outcome == NativeCandidateOutcome.BLOCK
    assert result.authorization.code == "ANALYTICAL_REQUEST_METRIC_MISMATCH"
    assert called["value"] is False


def test_v1_native_entry_composes_existing_trust_after_request_match(monkeypatch):
    from app.v3.native_execution import (
        NativeCandidateAuthorization,
        NativeCandidateOutcome,
    )
    from app.v3.native_standard.trust import (
        NativeStandardAuthorizationResult,
        NativeStandardTrustOrchestrator,
    )

    item = contract()
    expected = NativeStandardAuthorizationResult(
        authorization=NativeCandidateAuthorization(
            outcome=NativeCandidateOutcome.BLOCK,
            code="RETAINED_TRUST_SENTINEL",
            detail="existing trust path was reached",
        )
    )

    def retained(cls, **kwargs):
        assert kwargs == {"sentinel": "existing-trust"}
        return expected

    monkeypatch.setattr(
        NativeStandardTrustOrchestrator,
        "authorize",
        classmethod(retained),
    )
    result = NativeStandardTrustOrchestrator.authorize_v1(
        request_contract=item,
        request_observation=observation_from_contract(item),
        sentinel="existing-trust",
    )
    assert result == expected
