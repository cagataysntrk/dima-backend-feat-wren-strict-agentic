from __future__ import annotations

import ast
import base64
import inspect
import json

import pytest

from app.v3.analytics_contract import (
    ApprovedRelationshipPath,
    ResolvedFilterRef,
    ResolvedRanking,
)
from app.v3.semantic_spec import DimensionSpec, MetricSpec, SourceLineage
from app.v3.substrate.metabase import canonical as canonical_module
from app.v3.substrate.metabase import compiler as compiler_module
from app.v3.substrate.metabase import execution_binding as execution_binding_module
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.execution_binding import (
    CandidateSemanticBinding,
    CurrentCatalogObject,
    CurrentCatalogSnapshot,
    DimaExecutionBindingSnapshot,
    MetabaseCompilationBlocked,
)
from app.v3.substrate.metabase.models import ConstructedQuery
from app.v3.substrate.metabase.p3a_fixture import (
    CTX,
    build_cases,
    build_intent,
    build_period,
    build_snapshot,
)


def _case(index: int):
    return build_cases()[index][1]


def _encode(query):
    return base64.b64encode(
        json.dumps(query, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")


class DeterministicClient:
    def construct_query(self, portable_query):
        return ConstructedQuery(serialized_query=_encode(portable_query))


class MutatingClient:
    def __init__(self, mutate):
        self._mutate = mutate

    def construct_query(self, portable_query):
        copied = json.loads(json.dumps(portable_query))
        self._mutate(copied)
        return ConstructedQuery(serialized_query=_encode(copied))


def _inject_runtime_uuids(value, token):
    if isinstance(value, dict):
        for item in value.values():
            _inject_runtime_uuids(item, token)
        return
    if isinstance(value, list):
        if (
            len(value) >= 2
            and isinstance(value[0], str)
            and isinstance(value[1], dict)
        ):
            value[1]["lib/uuid"] = f"runtime-{token}-{value[0]}"
        for item in value:
            _inject_runtime_uuids(item, token)


class UuidVolatileClient:
    def __init__(self):
        self.calls = 0

    def construct_query(self, portable_query):
        self.calls += 1
        copied = json.loads(json.dumps(portable_query))
        _inject_runtime_uuids(copied, self.calls)
        return ConstructedQuery(serialized_query=_encode(copied))


class NonDeterministicClient:
    def __init__(self):
        self.calls = 0

    def construct_query(self, portable_query):
        self.calls += 1
        copied = json.loads(json.dumps(portable_query))
        _inject_runtime_uuids(copied, self.calls)
        copied["stages"][0]["source-table"][-1] = (
            "orders" if self.calls % 2 else "orders_v2"
        )
        return ConstructedQuery(serialized_query=_encode(copied))


class SimilarUuidKeyDriftClient:
    def __init__(self):
        self.calls = 0

    def construct_query(self, portable_query):
        self.calls += 1
        copied = json.loads(json.dumps(portable_query))
        _inject_runtime_uuids(copied, self.calls)
        copied["stages"][0]["aggregation"][0][1]["lib/uuid2"] = (
            "A" if self.calls % 2 else "B"
        )
        copied["stages"][0]["aggregation"][0][1]["my_uuid"] = (
            "same" if self.calls % 2 else "different"
        )
        return ConstructedQuery(serialized_query=_encode(copied))


class InvalidBase64Client:
    def construct_query(self, portable_query):
        del portable_query
        return ConstructedQuery(serialized_query="not@@base64")


def test_compiler_source_has_no_semantic_retrieval_or_name_locator_dependencies():
    source = inspect.getsource(MetabaseProjectionCompiler)
    assert ".canonical_name" not in source
    assert ".source_scopes" not in source
    assert "MetabaseAgentClient" not in source
    assert ".search(" not in source
    assert ".read_resource(" not in source
    assert "request_ref" not in source
    assert "source_message_hash" not in source
    assert "semantic_handle" not in source.lower()




def test_p4_production_boundary_has_no_regex_or_fuzzy_matching_dependencies():
    forbidden = {
        "re",
        "regex",
        "difflib",
        "rapidfuzz",
        "fuzzywuzzy",
        "Levenshtein",
    }
    for module in (
        compiler_module,
        canonical_module,
        execution_binding_module,
    ):
        tree = ast.parse(inspect.getsource(module))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert imported.isdisjoint(forbidden), (module.__name__, imported & forbidden)


def test_eight_representative_families_compile_with_exact_manifest():
    expected = (
        (1, 0, 0, 0, None),
        (1, 1, 0, 0, None),
        (1, 0, 1, 0, None),
        (1, 0, 2, 2, None),
        (2, 0, 4, 4, None),
        (1, 1, 0, 0, 3),
        (1, 2, 0, 0, None),
        (1, 1, 3, 2, None),
    )

    for index, (_, intent) in enumerate(build_cases()):
        plan = MetabaseProjectionCompiler.compile(
            intent=intent,
            snapshot=build_snapshot(),
        )
        query_count, breakouts, filter_leaves, time_predicates, limit = expected[index]
        assert plan.manifest.query_count == query_count
        assert sum(x.breakout_count for x in plan.manifest.steps) == breakouts
        assert sum(x.filter_leaf_count for x in plan.manifest.steps) == filter_leaves
        assert sum(x.time_predicate_count for x in plan.manifest.steps) == time_predicates
        assert all(x.explicit_join_count == 0 for x in plan.manifest.steps)
        assert all(x.implicit_join_reference_count == 0 for x in plan.manifest.steps)
        if limit is not None:
            assert plan.manifest.steps[0].limit == limit


def test_comparison_is_two_explicit_query_steps():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(4),
        snapshot=build_snapshot(),
    )
    assert [step.role for step in plan.steps] == ["base", "reference"]
    assert plan.manifest.query_count == 2
    assert plan.manifest.comparison_query_count == 2


def test_multiple_textual_filters_are_preserved():
    base = _case(2)
    north = base.filters[0]
    second = north.model_copy(
        update={
            "semantic_ref": "handle_filter_2",
            "source_candidate_id": "cand_filter_channel",
            "dimension_name": "DO NOT USE AS PHYSICAL FIELD",
            "value": "Web",
        }
    )
    snapshot = build_snapshot()
    snapshot = snapshot.model_copy(
        update={
            "candidate_bindings": (
                *snapshot.candidate_bindings,
                CandidateSemanticBinding(
                    candidate_id="cand_filter_channel",
                    semantic_id="dimension.channel",
                    kind="filter",
                ),
            )
        }
    )
    intent = base.model_copy(update={"filters": (north, second)})
    plan = MetabaseProjectionCompiler.compile(intent=intent, snapshot=snapshot)
    assert plan.manifest.steps[0].filter_leaf_count == 2
    rendered = repr(plan.steps[0].portable_query)
    assert "North" in rendered
    assert "Web" in rendered


def test_nullable_schema_is_preserved_as_json_null_locator():
    base = build_snapshot()

    metrics = tuple(
        item.model_copy(
            update={
                "source_lineage": tuple(
                    lineage.model_copy(update={"schema_name": None})
                    for lineage in item.source_lineage
                )
            }
        )
        for item in base.semantic_spec.metrics
    )
    dimensions = tuple(
        item.model_copy(
            update={
                "source_lineage": tuple(
                    lineage.model_copy(update={"schema_name": None})
                    for lineage in item.source_lineage
                )
            }
        )
        for item in base.semantic_spec.dimensions
    )
    spec = base.semantic_spec.model_copy(
        update={"metrics": metrics, "dimensions": dimensions}
    )
    catalog = CurrentCatalogSnapshot(
        catalog_version=base.current_catalog.catalog_version,
        objects=tuple(
            item.model_copy(update={"schema_name": None})
            for item in base.current_catalog.objects
        ),
    )
    snapshot = base.model_copy(
        update={"semantic_spec": spec, "current_catalog": catalog}
    )

    plan = MetabaseProjectionCompiler.compile(
        intent=_case(1),
        snapshot=snapshot,
    )
    stage = plan.steps[0].portable_query["stages"][0]
    assert stage["source-table"][1] is None
    assert stage["aggregation"][0][2][2][1] is None
    assert stage["breakout"][0][2][1] is None


def test_numeric_metric_lineage_is_used_without_name_guessing():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(0),
        snapshot=build_snapshot(),
    )
    aggregation = plan.steps[0].portable_query["stages"][0]["aggregation"][0]
    assert aggregation[0] == "sum"
    assert aggregation[2][2][-1] == "amount"
    assert "DO NOT USE THIS" not in repr(plan.steps[0].portable_query)


def test_arbitrary_formula_fails_closed():
    base = build_snapshot()
    metric = base.semantic_spec.metrics[0].model_copy(
        update={"formula": "amount * 1.2"}
    )
    spec = base.semantic_spec.model_copy(update={"metrics": (metric,)})
    snapshot = base.model_copy(update={"semantic_spec": spec})
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseProjectionCompiler.compile(intent=_case(0), snapshot=snapshot)
    assert exc.value.code == "UNPROVEN_METRIC_FORMULA_EXPRESSIVITY"


def test_metric_cardinality_fails_closed():
    intent = _case(0)
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseProjectionCompiler.compile(
            intent=intent.model_copy(update={"metrics": (intent.metrics[0], intent.metrics[0])}),
            snapshot=build_snapshot(),
        )
    assert exc.value.code == "P4_METRIC_CARDINALITY"


def test_text_null_token_remains_literal_string_equality():
    intent = _case(2)
    literal = intent.filters[0].model_copy(update={"value": "NULL"})
    plan = MetabaseProjectionCompiler.compile(
        intent=intent.model_copy(update={"filters": (literal,)}),
        snapshot=build_snapshot(),
    )
    filters = plan.steps[0].portable_query["stages"][0]["filters"]
    assert filters == [[
        "=",
        {},
        ["field", {}, ["Dima Analytics Lab", "public", "orders", "region"]],
        "NULL",
    ]]


def test_untyped_non_text_filter_fails_closed():
    base = build_snapshot()
    snapshot = base.model_copy(
        update={
            "candidate_bindings": (
                *base.candidate_bindings,
                CandidateSemanticBinding(
                    candidate_id="cand_filter_date",
                    semantic_id="dimension.order_date",
                    kind="filter",
                ),
            )
        }
    )
    ref = _case(2).filters[0].model_copy(
        update={
            "source_candidate_id": "cand_filter_date",
            "dimension_name": "not-a-locator",
            "value": "42",
        }
    )
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseProjectionCompiler.compile(
            intent=build_intent(filters=(ref,)),
            snapshot=snapshot,
        )
    assert exc.value.code == "UNTYPED_NON_TEXT_FILTER_UNSUPPORTED"


def test_relationship_and_grain_are_not_silently_accepted():
    base_intent = _case(0)
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseProjectionCompiler.compile(
            intent=base_intent.model_copy(
                update={
                    "approved_relationship_paths": (
                        ApprovedRelationshipPath(relationship_refs=("rel.orders.customer",)),
                    )
                }
            ),
            snapshot=build_snapshot(),
        )
    assert exc.value.code == "APPROVED_RELATIONSHIP_PATH_UNSUPPORTED"

    with pytest.raises(MetabaseCompilationBlocked) as exc2:
        MetabaseProjectionCompiler.compile(
            intent=base_intent.model_copy(update={"grain_constraints": ("day",)}),
            snapshot=build_snapshot(),
        )
    assert exc2.value.code == "GRAIN_CONSTRAINT_UNSUPPORTED"


def test_cross_table_dimension_fails_closed_even_when_current_catalog_is_explicit():
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
    snapshot = DimaExecutionBindingSnapshot(
        semantic_context_version=base.semantic_context_version,
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
        current_catalog=CurrentCatalogSnapshot(
            catalog_version=base.current_catalog.catalog_version,
            objects=(
                *base.current_catalog.objects,
                CurrentCatalogObject(
                    source_id="customers.name",
                    database_ref="Dima Analytics Lab",
                    schema_name="public",
                    table_name="customers",
                    column_name="name",
                    resource_entity_id="lab:customers.name",
                    resource_fingerprint="c" * 64,
                ),
            ),
        ),
    )
    ref = _case(1).dimensions[0].model_copy(
        update={"source_candidate_id": "cand_customer"}
    )
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseProjectionCompiler.compile(
            intent=build_intent(dimensions=(ref,)),
            snapshot=snapshot,
        )
    assert exc.value.code == "APPROVED_RELATIONSHIP_PATH_REQUIRED"


def test_plan_carries_stable_semantic_and_resource_identity():
    snapshot = build_snapshot()
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(7),
        snapshot=snapshot,
    )
    assert plan.manifest.semantic_ids == (
        "metric.revenue",
        "dimension.channel",
        "dimension.region",
        "dimension.order_date",
    )
    assert len(plan.manifest.resource_fingerprints) == 4
    assert plan.current_catalog_fingerprint == snapshot.current_catalog.fingerprint


def test_provider_free_canonicalizer_accepts_deterministic_structure():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(7),
        snapshot=build_snapshot(),
    )
    canonical = MetabaseCanonicalizer(
        client=DeterministicClient()
    ).canonicalize(plan)
    assert canonical.projection_hash == plan.projection_hash
    assert canonical.manifest == plan.manifest
    assert len(canonical.canonical_query_fingerprint) == 64


def test_canonicalizer_tolerates_only_exact_lib_uuid_runtime_volatility():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(7),
        snapshot=build_snapshot(),
    )
    client = UuidVolatileClient()
    first = MetabaseCanonicalizer(client=client).canonicalize(plan)
    second = MetabaseCanonicalizer(client=client).canonicalize(plan)

    assert first.canonical_query_fingerprint == second.canonical_query_fingerprint
    assert first.steps[0].canonical_query_fingerprint == second.steps[0].canonical_query_fingerprint
    assert first.steps[0].volatile_lib_uuid_count > 1
    rendered = repr(first.steps[0].decoded_query)
    assert "'lib/uuid'" not in rendered


def test_canonicalizer_rejects_non_uuid_canonical_drift():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(0),
        snapshot=build_snapshot(),
    )
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseCanonicalizer(
            client=NonDeterministicClient()
        ).canonicalize(plan)
    assert exc.value.code == "NON_DETERMINISTIC_CANONICAL_SEMANTICS"


def test_canonicalizer_does_not_strip_similar_looking_uuid_keys():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(0),
        snapshot=build_snapshot(),
    )
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseCanonicalizer(
            client=SimilarUuidKeyDriftClient()
        ).canonicalize(plan)
    assert exc.value.code == "NON_DETERMINISTIC_CANONICAL_SEMANTICS"


def test_canonicalizer_rejects_silent_filter_drop():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(2),
        snapshot=build_snapshot(),
    )

    def mutate(query):
        query["stages"][0].pop("filters", None)

    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseCanonicalizer(
            client=MutatingClient(mutate)
        ).canonicalize(plan)
    assert exc.value.code == "SILENT_FIELD_DROP_OR_REWRITE"


@pytest.mark.parametrize("implicit_key", ["source-field", "source-field-name", "source-field-join-alias"])
def test_canonicalizer_rejects_implicit_join_metadata(implicit_key):
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(1),
        snapshot=build_snapshot(),
    )

    def mutate(query):
        query["stages"][0]["breakout"][0][1][implicit_key] = "unexpected"

    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseCanonicalizer(
            client=MutatingClient(mutate)
        ).canonicalize(plan)
    assert exc.value.code == "SILENT_FIELD_DROP_OR_REWRITE"


def test_canonicalizer_rejects_explicit_join_insertion():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(0),
        snapshot=build_snapshot(),
    )

    def mutate(query):
        query["stages"][0]["joins"] = [{
            "lib/type": "mbql/join",
            "alias": "bad",
            "stages": [],
            "conditions": [],
        }]

    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseCanonicalizer(
            client=MutatingClient(mutate)
        ).canonicalize(plan)
    assert exc.value.code == "SILENT_FIELD_DROP_OR_REWRITE"


def test_canonicalizer_rejects_invalid_base64_json():
    plan = MetabaseProjectionCompiler.compile(
        intent=_case(0),
        snapshot=build_snapshot(),
    )
    with pytest.raises(MetabaseCompilationBlocked) as exc:
        MetabaseCanonicalizer(
            client=InvalidBase64Client()
        ).canonicalize(plan)
    assert exc.value.code == "CANONICAL_QUERY_DECODE_FAILED"
