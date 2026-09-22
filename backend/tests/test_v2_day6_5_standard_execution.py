from __future__ import annotations

import inspect

import pytest

from app.v2.manager_models import StandardProjection
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import StandardAuthoritySealer
from app.v2.standard_builder import StandardWorkMode
from app.v2.standard_execution import (
    StandardExecutionError,
    WrenStandardExecutionAdapter,
)


def _sealed():
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-a",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-a",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.net_revenue",
            cube_names=("Sales",),
        ),
    )
    projection = StandardProjection(
        obligation_ids=("U1",),
        metric_handles=(metric.handle_id,),
    )
    authority = StandardAuthoritySealer(
        semantic_handles=handles
    ).seal(
        projection=projection,
        turn_id="turn-1",
        request_ref="request-1",
        source_message_hash="1" * 64,
        context_version="ctx-1",
        tenant_binding="tenant-a",
        accepted_attempt_id="attempt-1",
        model_role="STANDARD_PROFILE",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
    )
    return handles, projection, authority


def test_standard_execution_module_has_no_research_authority_dependency():
    import app.v2.standard_execution as module

    source = inspect.getsource(module)
    assert "AcceptedTurnContract" not in source
    assert "UserObligationLedger" not in source
    assert "ResearchManagerLoop" not in source
    assert "manager_core_adapter" not in source


def test_standard_execution_rejects_projection_not_matching_sealed_authority():
    handles, projection, authority = _sealed()
    adapter = WrenStandardExecutionAdapter(semantic_handles=handles)
    changed = projection.model_copy(update={"obligation_ids": ("U2",)})

    with pytest.raises(StandardExecutionError, match="does not match"):
        adapter._verify_authority(
            projection=changed,
            authority=authority,
            tenant_binding="tenant-a",
        )


def test_standard_execution_rejects_foreign_tenant_before_wren():
    handles, projection, authority = _sealed()
    adapter = WrenStandardExecutionAdapter(semantic_handles=handles)

    with pytest.raises(ValueError, match="foreign-tenant"):
        adapter._verify_authority(
            projection=projection,
            authority=authority,
            tenant_binding="tenant-b",
        )
