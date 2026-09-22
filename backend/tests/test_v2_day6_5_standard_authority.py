"""Provider-free invariants for Standard/Research accepted-authority split."""

from __future__ import annotations

import pytest

from app.v2.manager_models import AcceptedTurnContract, StandardProjection
from app.v2.models import ResolvedSemanticRef, SemanticTargetKind
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import (
    AcceptedAuthorityConflict,
    AcceptedAuthorityFamily,
    AcceptedAuthorityRegistry,
    AcceptedResearchAuthority,
    StandardAuthoritySealer,
)
from app.v2.standard_builder import StandardWorkMode


def _metric_handle():
    handles = SemanticHandleRegistry()
    metric = handles.mint_from_resolver(
        tenant_binding="tenant-a",
        context_version="ctx-1",
        resolver_provenance_id="metric-standard-authority",
        target_kind="metric",
        canonical_target=ResolvedSemanticRef(
            candidate_id="metric-standard-authority",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="Sales.net_revenue",
            cube_names=("Sales",),
        ),
    )
    return handles, metric


def _seal(*, turn_id="turn-1"):
    handles, metric = _metric_handle()
    projection = StandardProjection(
        obligation_ids=("U1",),
        metric_handles=(metric.handle_id,),
    )
    authority = StandardAuthoritySealer(
        semantic_handles=handles
    ).seal(
        projection=projection,
        turn_id=turn_id,
        request_ref="req-1",
        source_message_hash="a" * 64,
        context_version="ctx-1",
        tenant_binding="tenant-a",
        accepted_attempt_id="attempt-1",
        model_role="FAST_LANGUAGE",
        work_mode=StandardWorkMode.STANDARD_DIRECT,
    )
    return handles, metric, projection, authority


def _research_contract(*, turn_id="turn-1"):
    return AcceptedTurnContract(
        contract_id="atc_" + "b" * 24,
        lineage_id="atl-research",
        version=1,
        turn_id=turn_id,
        request_ref="req-research",
        source_message_hash="c" * 64,
        accepted_attempt_id="attempt-research",
        model_role="RESEARCH_MANAGER",
        obligation_ids=("U_REL",),
        context_version="ctx-1",
        accepted_at_iso="2026-09-22T00:00:00+00:00",
    )


def test_standard_authority_seals_projection_by_hash_without_copying_semantic_body():
    _, metric, projection, authority = _seal()

    assert authority.authority_id.startswith("asa_")
    assert authority.semantic_handle_refs == (metric.handle_id,)
    assert len(authority.projection_hash) == 64
    assert not hasattr(authority, "projection")
    assert authority.work_mode == StandardWorkMode.STANDARD_DIRECT

    same = StandardAuthoritySealer(
        semantic_handles=_seal()[0]
    )
    # Projection hash is a property of the semantic body, independent of authority metadata.
    assert len(authority.projection_hash) == 64
    assert projection.obligation_ids == ("U1",)


def test_standard_authority_rejects_foreign_tenant_handle():
    handles, metric = _metric_handle()
    projection = StandardProjection(
        obligation_ids=("U1",),
        metric_handles=(metric.handle_id,),
    )

    with pytest.raises(ValueError, match="foreign-tenant"):
        StandardAuthoritySealer(semantic_handles=handles).seal(
            projection=projection,
            turn_id="turn-1",
            request_ref="req-1",
            source_message_hash="a" * 64,
            context_version="ctx-1",
            tenant_binding="tenant-b",
            accepted_attempt_id="attempt-1",
            model_role="FAST_LANGUAGE",
            work_mode=StandardWorkMode.STANDARD_DIRECT,
        )


def test_research_authority_is_existing_accepted_turn_contract_alias():
    research = _research_contract()
    assert isinstance(research, AcceptedResearchAuthority)
    assert research.contract_id.startswith("atc_")


def test_cross_family_registry_forbids_second_authority_for_same_turn():
    _, _, _, standard = _seal(turn_id="turn-1")
    research = _research_contract(turn_id="turn-1")
    registry = AcceptedAuthorityRegistry()

    registry.commit(standard)
    registry.commit(standard)  # exact retry is idempotent

    assert registry.accepted("turn-1") == (
        AcceptedAuthorityFamily.STANDARD,
        standard.authority_id,
    )
    with pytest.raises(AcceptedAuthorityConflict):
        registry.commit(research)


def test_cross_family_registry_allows_different_turns():
    _, _, _, standard = _seal(turn_id="turn-standard")
    research = _research_contract(turn_id="turn-research")
    registry = AcceptedAuthorityRegistry()

    registry.commit(standard)
    registry.commit(research)

    assert registry.accepted("turn-standard")[0] == AcceptedAuthorityFamily.STANDARD
    assert registry.accepted("turn-research")[0] == AcceptedAuthorityFamily.RESEARCH
