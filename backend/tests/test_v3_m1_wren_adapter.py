from __future__ import annotations

import ast
import inspect
import json

from app import contracts as contracts_module
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
)
from app.v2.models import (
    ResolvedSemanticRef as V2ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import (
    StandardAuthoritySealer as V2StandardAuthoritySealer,
)
from app.v2.standard_builder import StandardBuilderSession, StandardBuilderState
from app.v2.standard_execution import WrenStandardExecutionAdapter
from app.v2.standard_projection import StandardProjectionCompiler
from app.v3.analytics_contract import (
    ResolvedAnalyticsIntentBuilder,
    StandardProjection,
)
from app.v3.authority import (
    SemanticSurfaceCoverage,
    SemanticSurfaceRecord,
    SemanticSurfaceState,
    StandardAuthoritySealer,
    StandardWorkMode,
)
from app.v3.substrate.wren import WrenSubstrateAdapter
from control_plane.authorize import Principal


def test_wren_substrate_has_no_semantic_handle_or_raw_language_dependency():
    import app.v3.substrate.wren as module

    tree = ast.parse(inspect.getsource(module))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
    joined = "\n".join(imported)
    assert "semantic_handles" not in joined
    assert "semantic_linker" not in joined
    assert "resolver" not in joined.lower()

    source = inspect.getsource(module.WrenSubstrateAdapter.execute_execution_intent)
    assert "question" not in source
    assert "binding_for_execution" not in source


def test_v3_wren_adapter_matches_certified_v2_query_behavior(
    wren,
    schema,
    monkeypatch,
):
    cube = next(item for item in schema["cubes"] if item.get("name") == "bakim")
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())

    tenant_binding = "test-tenant"
    context_version = "ctx-m1-wren-parity"

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant_binding,
        context_version=context_version,
        resolver_provenance_id="m1-parity:bakim:ariza_sayisi",
        target_kind="metric",
        canonical_target=V2ResolvedSemanticRef(
            candidate_id="m1-parity-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )
    obligation = CandidateObligation(
        obligation_id="U_M1_WREN",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=(metric.handle_id,),
    )
    builder = StandardBuilderSession(
        compiler=StandardProjectionCompiler(semantic_handles=handles),
        tenant_binding=tenant_binding,
        context_version=context_version,
    )
    built = builder.submit((obligation,))
    assert built.state == StandardBuilderState.PROJECTION_READY
    assert built.projection is not None
    assert built.work_mode is not None

    v2_authority = V2StandardAuthoritySealer(
        semantic_handles=handles
    ).seal(
        projection=built.projection,
        turn_id="turn-m1-parity",
        request_ref="request-m1-parity",
        source_message_hash="1" * 64,
        context_version=context_version,
        tenant_binding=tenant_binding,
        accepted_attempt_id="attempt-m1-parity",
        model_role="STANDARD_PROFILE",
        work_mode=built.work_mode,
    )

    projection = StandardProjection.model_validate(
        built.projection.model_dump(mode="json")
    )
    coverage = SemanticSurfaceCoverage(
        turn_id="turn-m1-parity",
        attempt_id="attempt-m1-parity",
        context_version=context_version,
        surfaces=(
            SemanticSurfaceRecord(
                source_ref="src_" + "1" * 24,
                surface_text="arıza sayısı",
                kind_hint="metric",
                state=SemanticSurfaceState.BOUND,
                handle_id=metric.handle_id,
            ),
        ),
    )
    v3_authority = StandardAuthoritySealer(
        semantic_handles=handles
    ).seal(
        projection=projection,
        coverage=coverage,
        turn_id="turn-m1-parity",
        request_ref="request-m1-parity",
        source_message_hash="1" * 64,
        context_version=context_version,
        tenant_binding=tenant_binding,
        accepted_attempt_id="attempt-m1-parity",
        model_role="STANDARD_PROFILE",
        work_mode=StandardWorkMode(built.work_mode.value),
    )
    assert v3_authority.authority_id == v2_authority.authority_id
    assert v3_authority.projection_hash == v2_authority.projection_hash

    principal = Principal(
        user_id="test-user",
        tenant_id=tenant_binding,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant_binding,
        tenant_slug="demo-boyahane",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=wren.mdl_version,
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema") or "public"),
        db_online=True,
    )

    persisted = []
    monkeypatch.setattr(contracts_module, "_persist", lambda row: persisted.append(row))

    v2_result = WrenStandardExecutionAdapter(
        semantic_handles=handles
    ).execute(
        projection=built.projection,
        authority=v2_authority,
        tenant_binding=tenant_binding,
        principal=principal,
        service=wren,
        runtime=runtime,
        contract_store=contracts_module.ContractStore(),
        session_id="m1-parity-v2",
        question="m1 parity reference",
    )

    intent = ResolvedAnalyticsIntentBuilder(
        semantic_handles=handles
    ).build(
        projection=projection,
        authority=v3_authority,
        tenant_binding=tenant_binding,
        principal_subject=principal.user_id,
        principal_roles=tuple(principal.roles),
    )

    adapter = WrenSubstrateAdapter(
        service=wren,
        principal=principal,
        runtime=runtime,
        contract_store=contracts_module.ContractStore(),
        session_id="m1-parity-v3",
    )
    validation = adapter.validate_execution_intent(intent)
    assert validation.valid, validation.reasons
    v3_result = adapter.execute_execution_intent(intent)
    inspection = adapter.inspect_execution(v3_result)
    assert inspection.verified, inspection.reasons

    assert v3_result.query_count == v2_result.query_count == 1
    assert v3_result.analytics_ir_snapshot == v2_result.analytics_ir.model_dump(mode="json")
    assert v3_result.evidence.verified is True
    assert v3_result.evidence.evidence_kind == "standard_analytics"
    assert v3_result.evidence.obligation_ids == ("U_M1_WREN",)
    assert metric.handle_id in tuple(
        v3_result.evidence.payload["executions"][0]["columns"]
    )

    assert len(persisted) == 2
    old_row, new_row = persisted
    assert old_row.sql == new_row.sql
    assert old_row.cube_query_json == new_row.cube_query_json
    assert old_row.result_hash == new_row.result_hash
    assert old_row.row_count == new_row.row_count
    assert old_row.schema_version == new_row.schema_version
    assert old_row.source == new_row.source == "v2_standard"

    old_provenance = json.loads(old_row.provenance_json)["v2_standard"]
    new_provenance = json.loads(new_row.provenance_json)["v2_standard"]
    for key in (
        "adapter_id",
        "accepted_standard_authority_id",
        "projection_hash",
        "obligation_ids",
        "analytics_ir",
        "planner_id",
        "planner_version",
        "context_version",
        "principal_user_id",
        "principal_roles",
    ):
        assert old_provenance[key] == new_provenance[key]

    assert v3_result.query_receipts[0].legacy_query_contract_ref
    assert v3_result.query_receipts[0].resolved_intent_hash == intent.resolved_intent_hash
