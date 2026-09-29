from __future__ import annotations

import ast
import base64
import inspect
import json

from app.v3.execution_identity import (
    ExecutionAccessSnapshot,
    RuntimeIdentity,
)
from app.v3.substrate.base import AnalyticsSubstrate
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.execution_adapter import MetabaseSubstrateAdapter
from app.v3.substrate.metabase.models import (
    ConstructedQuery,
    ExecutionStatus,
    MetabaseExecutionResponse,
    MetabaseRuntimePolicy,
)
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot


class FakeClient:
    def __init__(self):
        self.policy = MetabaseRuntimePolicy(
            runtime_version="v0.63.18",
            runtime_image_digest="sha256:" + "1" * 64,
            raw_sql_policy="disabled",
            observed_page_size=200,
            observed_total_row_cap=2000,
        )

    def construct_query(self, portable_query):
        raw = json.dumps(
            portable_query,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return ConstructedQuery(
            serialized_query=base64.b64encode(raw).decode("ascii")
        )

    def execute_serialized(self, query):
        assert isinstance(query, ConstructedQuery)
        return MetabaseExecutionResponse(
            status=ExecutionStatus.COMPLETED,
            data={
                "cols": [{"name": "value"}],
                "rows": [[100]],
            },
            row_count=1,
            running_time=1,
        )


def _fixture():
    _, intent = build_cases()[0]
    snapshot = build_snapshot()
    plan = MetabaseProjectionCompiler.compile(
        intent=intent,
        snapshot=snapshot,
    )
    access = ExecutionAccessSnapshot(
        tenant_binding=intent.principal.tenant_binding,
        principal_subject=intent.principal.principal_subject,
        roles=intent.principal.roles,
        attribute_policy_digest="a" * 64,
        policy_version="p6-fixture-policy-v1",
        rls_versions=("p6-rls-v1",),
        cls_versions=("p6-cls-v1",),
        database_route="p6-shared-postgres",
        database_destination="p6-shared-postgres",
        impersonation_role=None,
        semantic_context_version=intent.semantic_context_version,
        source_object_refs=plan.manifest.resource_entity_ids,
        security_parameter_digest="b" * 64,
        attestation_refs=("attestation:p6-fixture",),
    )
    runtime = RuntimeIdentity(
        substrate="metabase",
        runtime_version="v0.63.18",
        image_digest="sha256:" + "1" * 64,
        database_id="p6-shared-postgres",
    )
    return intent, snapshot, access, runtime


def test_metabase_execution_adapter_is_thin_and_protocol_compatible():
    import app.v3.substrate.metabase.execution_adapter as module

    tree = ast.parse(inspect.getsource(module))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(
        {"re", "regex", "difflib", "rapidfuzz", "fuzzywuzzy", "Levenshtein"}
    )

    source = inspect.getsource(module)
    for forbidden in (
        ".search(",
        ".read_resource(",
        "canonical_name",
        "source_scopes",
        "raw user",
        "fallback",
        "similar",
        "synonym",
        "llm",
    ):
        assert forbidden not in source.lower()

    intent, snapshot, access, runtime = _fixture()
    adapter = MetabaseSubstrateAdapter(
        client=FakeClient(),
        binding_snapshot=snapshot,
        access_snapshot=access,
        runtime=runtime,
    )
    assert isinstance(adapter, AnalyticsSubstrate)
    assert adapter.validate_execution_intent(intent).valid is True


def test_metabase_execution_adapter_executes_and_strictly_seals():
    intent, snapshot, access, runtime = _fixture()
    adapter = MetabaseSubstrateAdapter(
        client=FakeClient(),
        binding_snapshot=snapshot,
        access_snapshot=access,
        runtime=runtime,
    )
    result = adapter.execute_execution_intent(intent)
    inspection = adapter.inspect_execution(result)

    assert inspection.verified is True
    assert result.substrate == "metabase"
    assert result.query_count == 1
    assert result.evidence.verified is True
    assert result.evidence.payload["resolved_intent_hash"] == intent.resolved_intent_hash
    assert result.evidence.payload["executions"][0]["rows"] == ((100,),)
    assert len(result.query_receipts) == 1
    assert result.query_receipts[0].receipt_fingerprint is not None
    assert result.query_receipts[0].access_attestation_refs == (
        "attestation:p6-fixture",
    )
