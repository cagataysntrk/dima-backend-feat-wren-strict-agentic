from __future__ import annotations

import json
from pathlib import Path

from app.v2.cube_planner import CubePlanner, ledger_from_canonical_ir
from app.v2.manager_models import CandidateObligation, ManagerCapabilityKey, ObligationOrigin
from app.v2.models import (
    PeriodKind,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_authority import StandardAuthoritySealer
from app.v2.standard_builder import StandardBuilderSession, StandardBuilderState
from app.v2.standard_execution import WrenStandardExecutionAdapter
from app.v2.standard_projection import StandardProjectionCompiler
from lab.x0_bridge_preflight import (
    FamilyArtifact,
    attach_family,
    load_cube_metadata,
    prototype_from_ir,
    seam_assessment,
    terminal,
    bridge_adapter_loc,
)

REPORT = Path(__file__).resolve().parents[1] / "lab" / "reports" / "v2_day6_5_x0_bridge_preflight.json"


def _source_ref(n):
    return "src_" + f"{n:024x}"


def _mint(handles, *, tenant, context, kind, target, n):
    return handles.mint_from_resolver(
        tenant_binding=tenant,
        context_version=context,
        resolver_provenance_id=f"bridge-preflight:{n}",
        target_kind=kind,
        canonical_target=target,
    )


def _family(
    *,
    wren,
    family_id,
    cube,
    metric,
    dimensions=(),
    filter_pair=None,
    period=False,
    comparison=False,
    ranking=None,
):
    schema = wren.schema()
    cube_meta = next(item for item in schema["cubes"] if item["name"] == cube)
    assert metric in tuple(cube_meta.get("measures") or ())
    for dim in dimensions:
        assert dim in tuple(cube_meta.get("dimensions") or ())
    if filter_pair is not None:
        assert filter_pair[0] in tuple(cube_meta.get("dimensions") or ())

    tenant = "bridge-preflight-tenant"
    context = "bridge-preflight-context-v1"
    handles = SemanticHandleRegistry()
    refs = []
    n = 1

    metric_handle = _mint(
        handles,
        tenant=tenant,
        context=context,
        kind="metric",
        target=ResolvedSemanticRef(
            candidate_id=f"{family_id}-metric",
            target_kind=SemanticTargetKind.METRIC,
            canonical_name=metric,
            cube_names=(cube,),
        ),
        n=n,
    )
    n += 1
    refs.append(metric_handle.handle_id)

    dim_handles = []
    for dim in dimensions:
        handle = _mint(
            handles,
            tenant=tenant,
            context=context,
            kind="dimension",
            target=ResolvedSemanticRef(
                candidate_id=f"{family_id}-{dim}",
                target_kind=SemanticTargetKind.DIMENSION,
                canonical_name=dim,
                cube_names=(cube,),
            ),
            n=n,
        )
        n += 1
        dim_handles.append(handle.handle_id)
        refs.append(handle.handle_id)

    filter_handle = None
    if filter_pair is not None:
        dim, value = filter_pair
        filter_handle = _mint(
            handles,
            tenant=tenant,
            context=context,
            kind="entity_value",
            target=ResolvedFilterRef(
                candidate_id=f"{family_id}-filter",
                dimension_name=dim,
                value=value,
                cube_names=(cube,),
            ),
            n=n,
        )
        n += 1
        refs.append(filter_handle.handle_id)

    period_value = None
    period_handle = None
    if period:
        time_dimension = tuple(cube_meta.get("time_dimensions") or ())[0]
        period_value = ResolvedPeriod(
            kind=PeriodKind.THIS_MONTH,
            source_text="bu ay",
            time_dimension=time_dimension,
            start="2026-09-01",
            end="2026-09-30",
        )
        period_handle = _mint(
            handles,
            tenant=tenant,
            context=context,
            kind="period",
            target=period_value,
            n=n,
        )
        n += 1
        refs.append(period_handle.handle_id)

    comparison_handle = None
    if comparison:
        assert period_value is not None
        reference = ResolvedPeriod(
            kind=PeriodKind.PREVIOUS_MONTH,
            source_text="önceki dönem",
            time_dimension=period_value.time_dimension,
            start="2026-08-01",
            end="2026-08-31",
        )
        comparison_value = ResolvedComparison(
            mode="previous_period",
            source_text="önceki dönemle karşılaştır",
            base_period=period_value,
            reference_period=reference,
        )
        comparison_handle = _mint(
            handles,
            tenant=tenant,
            context=context,
            kind="comparison",
            target=comparison_value,
            n=n,
        )
        n += 1
        refs.append(comparison_handle.handle_id)

    if ranking is not None:
        capability = ManagerCapabilityKey.RANKING
    elif comparison:
        capability = ManagerCapabilityKey.COMPARISON
    elif dimensions:
        capability = ManagerCapabilityKey.BREAKDOWN
    else:
        capability = ManagerCapabilityKey.PERFORMANCE

    obligation = CandidateObligation(
        obligation_id=f"U-{family_id}",
        capability_key=capability,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(_source_ref(100 + len(family_id)),),
        semantic_handle_refs=tuple(refs),
        ranking_direction=(ranking[0] if ranking else None),
        ranking_limit=(ranking[1] if ranking else None),
    )
    builder = StandardBuilderSession(
        compiler=StandardProjectionCompiler(semantic_handles=handles),
        tenant_binding=tenant,
        context_version=context,
    )
    built = builder.submit((obligation,))
    assert built.state == StandardBuilderState.PROJECTION_READY, built.reasons
    authority = StandardAuthoritySealer(semantic_handles=handles).seal(
        projection=built.projection,
        turn_id=f"turn-{family_id}",
        request_ref=f"request-{family_id}",
        source_message_hash="a" * 64,
        context_version=context,
        tenant_binding=tenant,
        accepted_attempt_id=f"attempt-{family_id}",
        model_role="STANDARD_PROFILE",
        work_mode=built.work_mode,
    )

    adapter = WrenStandardExecutionAdapter(semantic_handles=handles)
    ir = adapter.resolve_authorized_ir(
        projection=built.projection,
        authority=authority,
        tenant_binding=tenant,
    )
    plans, _ = CubePlanner().plan(
        ir=ir,
        ledger=ledger_from_canonical_ir(ir),
        service=wren,
    )
    return FamilyArtifact(
        family_id=family_id,
        authority=authority,
        projection=built.projection,
        ir=ir,
        plans=plans,
        metadata=load_cube_metadata(cube),
    )


def test_x0_bridge_preflight_real_sealed_families(wren):
    artifacts = (
        _family(wren=wren, family_id="01_metric_only_computed", cube="cari", metric="bakiye"),
        _family(wren=wren, family_id="02_metric_dimension", cube="ticaret", metric="toplam_tutar", dimensions=("tur",)),
        _family(wren=wren, family_id="03_metric_filter", cube="ticaret", metric="toplam_tutar", filter_pair=("tur", "satis")),
        _family(wren=wren, family_id="04_metric_period", cube="ticaret", metric="toplam_matrah", period=True),
        _family(wren=wren, family_id="05_metric_period_comparison", cube="ticaret", metric="toplam_matrah", period=True, comparison=True),
        _family(wren=wren, family_id="06_metric_dimension_ranking", cube="ticaret", metric="toplam_tutar", dimensions=("cari_kodu",), ranking=("desc", 5)),
        _family(wren=wren, family_id="07_metric_two_dimensions", cube="ticaret", metric="toplam_tutar", dimensions=("tur", "cari_kodu")),
        _family(wren=wren, family_id="08_metric_filter_period_dimension", cube="ticaret", metric="toplam_tutar", dimensions=("cari_kodu",), filter_pair=("tur", "satis"), period=True),
    )

    receipts = tuple(
        attach_family(prototype_from_ir(item.ir, item.metadata), item)
        for item in artifacts
    )
    seam_matrix = seam_assessment(artifacts[0])
    outcome = terminal(receipts)

    assert len(receipts) == 8
    assert bridge_adapter_loc() > 0
    assert all(item.adapter_loc == bridge_adapter_loc() for item in receipts)
    assert seam_matrix["A_STANDARD_PROJECTION_HANDLES"]["verdict"] == "COLLAPSES_TO_B_IF_RESOLVED_ONCE"
    assert seam_matrix["B_RESOLVED_ANALYTICS_IR"]["verdict"] == "THIN_CANDIDATE"
    assert seam_matrix["C_WREN_PLANNED_REPRESENTATION"]["verdict"] == "REJECT_AS_PRIMARY_BRIDGE_SEAM"

    computed = receipts[0]
    assert computed.metric_formula_duplication is True
    assert computed.grain_additivity_duplication is True
    assert "computed_metric_expression:bakiye" in computed.unsupported_wren_construct
    assert computed.portable_queries == ()

    for item in receipts[1:]:
        assert item.manual_metadata_mapping == 0
        assert item.relationship_duplication is False
        assert item.time_semantics_duplication is False
        assert item.implicit_join_required is False
        assert item.bridge_lossless is True, item
        assert item.portable_queries

    comparison = receipts[4]
    assert len(comparison.portable_queries) == 2
    ranking = receipts[5]
    assert ranking.ranking_fidelity is True
    multi = receipts[6]
    assert multi.multi_dimension_fidelity is True

    assert outcome == "HEAVY_SEMANTIC_DUPLICATION"

    payload = {
        "kind": "d65_x0_bridge_preflight",
        "runtime_started": False,
        "metabase_api_called": False,
        "real_wren_plans_compiled": True,
        "seams": seam_matrix,
        "families": [
            {
                **{
                    k: v
                    for k, v in item.__dict__.items()
                    if k != "identity_requirements"
                },
                "identity_requirements": [
                    req.__dict__ for req in item.identity_requirements
                ],
            }
            for item in receipts
        ],
        "summary": {
            "terminal": outcome,
            "total_bridge_loc": bridge_adapter_loc(),
            "total_identity_mapping_count": sum(item.mechanical_identity_mapping_count for item in receipts),
            "total_manual_semantic_mapping_count": sum(item.manual_metadata_mapping for item in receipts),
            "total_duplicated_semantic_definitions": sum(
                int(item.metric_formula_duplication)
                + int(item.relationship_duplication)
                + int(item.grain_additivity_duplication)
                + int(item.time_semantics_duplication)
                for item in receipts
            ),
            "total_unsupported_semantic_shapes": sum(bool(item.unsupported_wren_construct) for item in receipts),
            "raw_user_language_reinterpretation": 0,
            "manual_metric_redefinition": 0,
            "manual_relationship_redefinition": 0,
            "manual_grain_redefinition": 0,
            "manual_time_semantic_redefinition": 0,
            "metabase_label_name_guessing": 0,
            "unapproved_implicit_FK_join": 0,
            "second_semantic_authority": 0,
            "semantic_handle_remint": 0,
            "cross_tenant_mapping": 0,
            "stale_identity_reuse_as_authority": 0,
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
