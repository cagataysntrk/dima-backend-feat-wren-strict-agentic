from __future__ import annotations

import ast
import inspect

import pytest

from app.v2.manager_models import AcceptedTurnContract as V2AcceptedTurnContract
from app.v2.models import ResolvedSemanticRef as V2ResolvedSemanticRef
from app.v2.models import SemanticTargetKind
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v3.analytics_contract import (
    ResolvedAnalyticsIntentBuilder,
    StandardProjection,
)
from app.v3.authority import (
    AcceptedAuthorityConflict,
    AcceptedAuthorityFamily,
    AcceptedResearchAuthority,
    SemanticSurfaceCoverage,
    SemanticSurfaceRecord,
    SemanticSurfaceState,
    SharedAuthorityArbiter,
    StandardAuthoritySealer,
    StandardWorkMode,
)


def _metric_setup():
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-m1",
        resolver_provenance_id="m1:metric",
        target_kind="metric",
        canonical_target=V2ResolvedSemanticRef(
            candidate_id="metric-m1",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ariza_sayisi",
            cube_names=("bakim",),
        ),
    )
    projection = StandardProjection(
        obligation_ids=("U1",),
        metric_handles=(metric.handle_id,),
    )
    coverage = SemanticSurfaceCoverage(
        turn_id="turn-m1",
        attempt_id="attempt-m1",
        context_version="ctx-m1",
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
    authority = StandardAuthoritySealer(
        semantic_handles=handles
    ).seal(
        projection=projection,
        coverage=coverage,
        turn_id="turn-m1",
        request_ref="request-m1",
        source_message_hash="a" * 64,
        context_version="ctx-m1",
        tenant_binding="tenant-a",
        accepted_attempt_id="attempt-m1",
        model_role="STANDARD_PROFILE",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
    )
    return handles, metric, projection, coverage, authority


def test_v3_core_modules_do_not_import_wren_or_metabase_or_legacy_resolver():
    import app.v3.analytics_contract as analytics_contract
    import app.v3.authority as authority
    import app.v3.evidence as evidence
    import app.v3.semantic_spec as semantic_spec

    for module in (analytics_contract, authority, evidence, semantic_spec):
        tree = ast.parse(inspect.getsource(module))
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported_modules.append(node.module or "")
            elif isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
        joined = "\n".join(imported_modules).lower()
        assert "metabase" not in joined
        assert "wren" not in joined
        assert "app.v2.resolver" not in joined


def test_research_authority_reuses_existing_contract_type():
    assert AcceptedResearchAuthority is V2AcceptedTurnContract


def test_material_semantic_surface_must_be_terminally_accounted():
    with pytest.raises(ValueError):
        SemanticSurfaceRecord(
            source_ref="src_" + "1" * 24,
            surface_text="belirsiz marj",
            kind_hint="metric",
            state=SemanticSurfaceState.UNRESOLVED,
        )

    unresolved = SemanticSurfaceRecord(
        source_ref="src_" + "1" * 24,
        surface_text="belirsiz marj",
        kind_hint="metric",
        state=SemanticSurfaceState.UNRESOLVED,
        unresolved_reason="AMBIGUOUS",
    )
    assert unresolved.state == SemanticSurfaceState.UNRESOLVED


def test_standard_authority_cannot_seal_partial_semantic_surface():
    handles, metric, projection, _, _ = _metric_setup()
    coverage = SemanticSurfaceCoverage(
        turn_id="turn-m1",
        attempt_id="attempt-m1",
        context_version="ctx-m1",
        surfaces=(
            SemanticSurfaceRecord(
                source_ref="src_" + "1" * 24,
                surface_text="arıza sayısı",
                kind_hint="metric",
                state=SemanticSurfaceState.BOUND,
                handle_id=metric.handle_id,
            ),
            SemanticSurfaceRecord(
                source_ref="src_" + "2" * 24,
                surface_text="belirsiz marj",
                kind_hint="metric",
                state=SemanticSurfaceState.UNRESOLVED,
                unresolved_reason="AMBIGUOUS",
            ),
        ),
    )
    with pytest.raises(ValueError, match="unresolved material surface"):
        StandardAuthoritySealer(semantic_handles=handles).seal(
            projection=projection,
            coverage=coverage,
            turn_id="turn-m1",
            request_ref="request-m1",
            source_message_hash="a" * 64,
            context_version="ctx-m1",
            tenant_binding="tenant-a",
            accepted_attempt_id="attempt-m1",
            model_role="STANDARD_PROFILE",
            work_mode=StandardWorkMode.STANDARD_DIRECT,
        )


def _research_contract(turn_id: str):
    return V2AcceptedTurnContract(
        contract_id="atc_" + "b" * 24,
        lineage_id="atl-m1",
        version=1,
        turn_id=turn_id,
        request_ref="request-research",
        source_message_hash="c" * 64,
        accepted_attempt_id="attempt-research",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U_REL",),
        context_version="ctx-m1",
        accepted_at_iso="2026-09-22T00:00:00+00:00",
    )


def test_shared_authority_arbiter_validate_is_non_mutating_and_xor_is_fail_closed():
    _, _, _, _, standard = _metric_setup()
    research = _research_contract(standard.turn_id)
    arbiter = SharedAuthorityArbiter()

    arbiter.validate(standard)
    assert arbiter.accepted(standard.turn_id) is None

    arbiter.commit(standard)
    arbiter.commit(standard)
    assert arbiter.accepted(standard.turn_id) == (
        AcceptedAuthorityFamily.STANDARD,
        standard.authority_id,
    )
    with pytest.raises(AcceptedAuthorityConflict):
        arbiter.validate(research)
    assert arbiter.accepted(standard.turn_id) == (
        AcceptedAuthorityFamily.STANDARD,
        standard.authority_id,
    )


def test_resolved_intent_resolves_each_handle_once_before_substrate():
    handles, metric, projection, _, authority = _metric_setup()

    class CountingRegistry:
        def __init__(self, inner):
            self.inner = inner
            self.calls = []

        def binding_for_execution(self, handle_id, *, tenant_binding, context_version):
            self.calls.append(handle_id)
            return self.inner.binding_for_execution(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )

    counting = CountingRegistry(handles)
    intent = ResolvedAnalyticsIntentBuilder(
        semantic_handles=counting
    ).build(
        projection=projection,
        authority=authority,
        tenant_binding="tenant-a",
        principal_subject="user-a",
        principal_roles=("owner",),
    )

    assert counting.calls == [metric.handle_id]
    assert intent.metrics[0].semantic_ref == metric.handle_id
    assert intent.metrics[0].canonical_name == "ariza_sayisi"
    assert intent.metrics[0].source_scopes == ("bakim",)
    assert len(intent.resolved_intent_hash) == 64
