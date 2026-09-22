from __future__ import annotations

import inspect

import pytest

from app.v3.semantic_spec import DimensionSpec, SourceLineage
from app.v3.substrate.metabase.p3a_fixture import (
    CTX,
    TIME_KEY,
    build_cases,
    build_intent,
    build_period,
    build_snapshot,
)
from app.v3.substrate.metabase.p3a_models import (
    BridgeFamily,
    CandidateSemanticBinding,
    DimaExecutionBindingSnapshot,
    P3ABridgeBlocked,
    P3AResult,
)
from app.v3.substrate.metabase.p3a_preflight import MetabaseBridgePreflightCompiler


def test_all_eight_representative_families_pass_candidate_b_seam():
    report = MetabaseBridgePreflightCompiler.audit(
        cases=build_cases(),
        snapshot=build_snapshot(),
    )
    assert report.result == P3AResult.PASS_B_SEAM
    assert len(report.findings) == 8
    assert all(item.compiled for item in report.findings)
    assert report.counters.clean is True
    assert report.counters.model_dump() == {
        "raw_user_language_reinterpretation": 0,
        "manual_metric_redefinition": 0,
        "manual_relationship_redefinition": 0,
        "metabase_label_name_guessing": 0,
        "unapproved_implicit_fk_join": 0,
        "second_semantic_authority": 0,
    }


def test_compiler_uses_dima_lineage_not_names_scopes_or_metabase_retrieval():
    source = inspect.getsource(MetabaseBridgePreflightCompiler)
    assert ".canonical_name" not in source
    assert ".source_scopes" not in source
    assert "MetabaseAgentClient" not in source
    assert ".search(" not in source
    assert ".read_resource(" not in source
    assert "request_ref" not in source
    assert "source_message_hash" not in source

    family, intent = build_cases()[1]
    plan = MetabaseBridgePreflightCompiler.compile(
        family=family,
        intent=intent,
        snapshot=build_snapshot(),
    )
    stage = plan.query_steps[0].query["stages"][0]
    assert stage["source-table"] == ["Dima Analytics Lab", "public", "orders"]
    assert stage["aggregation"][0][2][2][-1] == "amount"
    assert stage["breakout"][0][2][-1] == "region"
    rendered = repr(plan.query_steps[0].query)
    assert "legacy_wren_cube_name" not in rendered
    assert "DO NOT USE THIS" not in rendered
    assert "DISPLAY NAME" not in rendered


def test_missing_time_binding_blocks_period_without_name_guessing():
    base = build_snapshot()
    broken = DimaExecutionBindingSnapshot(
        semantic_context_version=base.semantic_context_version,
        semantic_spec=base.semantic_spec,
        candidate_bindings=base.candidate_bindings,
        temporal_bindings=(),
    )
    with pytest.raises(P3ABridgeBlocked) as exc:
        MetabaseBridgePreflightCompiler.compile(
            family=BridgeFamily.METRIC_PERIOD,
            intent=build_intent(period_value=build_period()),
            snapshot=broken,
        )
    assert exc.value.code == "MISSING_STABLE_TIME_BINDING"


def test_missing_candidate_binding_blocks_metric_without_name_fallback():
    base = build_snapshot()
    broken = DimaExecutionBindingSnapshot(
        semantic_context_version=base.semantic_context_version,
        semantic_spec=base.semantic_spec,
        candidate_bindings=tuple(
            item for item in base.candidate_bindings if item.kind != "metric"
        ),
        temporal_bindings=base.temporal_bindings,
    )
    with pytest.raises(P3ABridgeBlocked) as exc:
        MetabaseBridgePreflightCompiler.compile(
            family=BridgeFamily.METRIC,
            intent=build_intent(),
            snapshot=broken,
        )
    assert exc.value.code == "MISSING_STABLE_CANDIDATE_BINDING"


def test_cross_table_dimension_is_blocked_without_approved_relationship_path():
    base = build_snapshot()
    foreign = DimensionSpec(
        dimension_id="dimension.customer",
        name="Customer",
        data_type="text",
        semantic_version="1",
        source_lineage=(
            SourceLineage(
                source_id="customers.name",
                database_ref="Dima Analytics Lab",
                schema_name="public",
                table_name="customers",
                column_name="name",
            ),
        ),
    )
    spec = base.semantic_spec.model_copy(
        update={"dimensions": (*base.semantic_spec.dimensions, foreign)}
    )
    expanded = DimaExecutionBindingSnapshot(
        semantic_context_version=CTX,
        semantic_spec=spec,
        candidate_bindings=(
            *base.candidate_bindings,
            CandidateSemanticBinding(
                candidate_id="cand_customer",
                semantic_id="dimension.customer",
                kind="dimension",
            ),
        ),
        temporal_bindings=base.temporal_bindings,
    )

    metric_case = build_cases()[1][1]
    customer_ref = metric_case.dimensions[0].model_copy(
        update={"source_candidate_id": "cand_customer"}
    )
    with pytest.raises(P3ABridgeBlocked) as exc:
        MetabaseBridgePreflightCompiler.compile(
            family=BridgeFamily.METRIC_DIMENSION,
            intent=build_intent(dimensions=(customer_ref,)),
            snapshot=expanded,
        )
    assert exc.value.code == "APPROVED_RELATIONSHIP_PATH_REQUIRED"


def test_snapshot_context_mismatch_blocks_replay():
    other = build_snapshot().model_copy(
        update={"semantic_context_version": "other-context"}
    )
    with pytest.raises(P3ABridgeBlocked) as exc:
        MetabaseBridgePreflightCompiler.compile(
            family=BridgeFamily.METRIC,
            intent=build_intent(),
            snapshot=other,
        )
    assert exc.value.code == "SEMANTIC_CONTEXT_MISMATCH"


def test_time_compatibility_key_is_not_used_as_physical_field_name():
    family = BridgeFamily.METRIC_PERIOD
    plan = MetabaseBridgePreflightCompiler.compile(
        family=family,
        intent=build_intent(period_value=build_period()),
        snapshot=build_snapshot(),
    )
    rendered = repr(plan.query_steps[0].query)
    assert TIME_KEY not in rendered
    assert "order_date" in rendered
