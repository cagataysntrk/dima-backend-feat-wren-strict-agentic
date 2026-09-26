"""D65-SI pure Standard REAL Wren trust-plane sentinel.

No LLM/raw language interpretation. This proves the exact post-cognition Standard authority
and execution chain against the repository's real in-process WrenService + demo DuckDB:

CandidateObligation
→ StandardBuilder / StandardProjection
→ AcceptedStandardAuthority
→ AcceptedAuthorityRegistry
→ WrenStandardExecutionAdapter
→ real Wren dry-plan/query
→ sealed QueryContract
→ verified EvidenceArtifact

No AcceptedTurnContract/UserObligationLedger/ResearchManagerLoop is used.
"""

from __future__ import annotations

import json

from app import contracts as contracts_module
from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
)
from app.v2.models import (
    ResolvedSemanticRef,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import (
    AcceptedAuthorityFamily,
    AcceptedAuthorityRegistry,
    StandardAuthoritySealer,
)
from app.v2.standard_builder import StandardBuilderSession, StandardBuilderState
from app.v2.standard_execution import WrenStandardExecutionAdapter
from app.v2.standard_projection import StandardProjectionCompiler
from control_plane.authorize import Principal


def test_pure_standard_crosses_real_wren_trust_plane(
    wren,
    schema,
    monkeypatch,
):
    cube = next(
        item for item in schema["cubes"]
        if item.get("name") == "bakim"
    )
    assert "ariza_sayisi" in tuple(cube.get("measures") or ())

    tenant_binding = "test-tenant"
    context_version = "ctx-day65-pure-standard-v1"

    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding=tenant_binding,
        context_version=context_version,
        resolver_provenance_id="day65-pure-standard:bakim:ariza_sayisi",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="day65-pure-standard-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )

    obligation = CandidateObligation(
        obligation_id="U_STANDARD_WREN",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=("src_" + "1" * 24,),
        semantic_handle_refs=(metric.handle_id,),
    )

    builder = StandardBuilderSession(
        compiler=StandardProjectionCompiler(
            semantic_handles=handles,
        ),
        tenant_binding=tenant_binding,
        context_version=context_version,
    )
    built = builder.submit((obligation,))
    assert built.state == StandardBuilderState.PROJECTION_READY
    assert built.projection is not None
    assert built.work_mode is not None

    authority = StandardAuthoritySealer(
        semantic_handles=handles,
    ).seal(
        projection=built.projection,
        turn_id="turn-pure-standard-wren",
        request_ref="request-pure-standard-wren",
        source_message_hash="1" * 64,
        context_version=context_version,
        tenant_binding=tenant_binding,
        accepted_attempt_id="standard-attempt-1",
        model_role="STANDARD_PROFILE",
        work_mode=built.work_mode,
    )
    registry = AcceptedAuthorityRegistry()
    registry.commit(authority)
    assert registry.accepted(authority.turn_id) == (
        AcceptedAuthorityFamily.STANDARD,
        authority.authority_id,
    )

    persisted_rows = []
    monkeypatch.setattr(
        contracts_module,
        "_persist",
        lambda row: persisted_rows.append(row),
    )
    contract_store = contracts_module.ContractStore()

    principal = Principal(
        user_id="test-user",
        tenant_id=tenant_binding,
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    tenant_runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant_binding,
        tenant_slug="demo-boyahane",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=wren.mdl_version,
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema") or "public"),
        db_online=True,
    )

    result = WrenStandardExecutionAdapter(
        semantic_handles=handles,
    ).execute(
        projection=built.projection,
        authority=authority,
        tenant_binding=tenant_binding,
        principal=principal,
        service=wren,
        runtime=tenant_runtime,
        contract_store=contract_store,
        session_id="day65-pure-standard-session",
        question="pure Standard Wren sentinel",
    )

    assert result.query_count == 1
    assert result.analytics_ir.metrics[0].canonical_name == "ariza_sayisi"
    assert result.evidence.verified is True
    assert result.evidence.evidence_kind == "standard_analytics"
    assert result.evidence.obligation_ids == ("U_STANDARD_WREN",)
    assert len(result.query_contract_refs) == 1
    assert result.evidence.query_contract_refs == result.query_contract_refs
    assert result.evidence.payload["accepted_standard_authority_id"] == authority.authority_id
    assert result.evidence.payload["projection_hash"] == authority.projection_hash
    assert result.evidence.payload["executions"]

    exposed = result.evidence.payload["executions"][0]
    assert metric.handle_id in tuple(exposed.get("columns") or ())
    assert "ariza_sayisi" not in tuple(exposed.get("columns") or ())

    assert len(persisted_rows) == 1
    persisted = persisted_rows[0]
    assert persisted.result_hash
    assert persisted.sql
    assert persisted.cube_query_json
    provenance = json.loads(persisted.provenance_json)
    standard = provenance["v2_standard"]
    assert standard["accepted_standard_authority_id"] == authority.authority_id
    assert standard["projection_hash"] == authority.projection_hash
    assert standard["adapter_id"] == "wren_standard_v1"
