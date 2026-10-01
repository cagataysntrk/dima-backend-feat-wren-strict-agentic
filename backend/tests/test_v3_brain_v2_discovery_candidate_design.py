from types import SimpleNamespace

from app.v3.brain_v2.discovery_candidate_design import (
    project_candidate_set,
    remaining_discovery_mechanism_refs,
)
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
    embed_root_cause_candidate_semantics,
)


def _claim(
    mechanism_ref: str,
    *,
    obligation_id: str = "g_root",
    lineage_id: str = "atl_current",
    scope_version_id: str = "scope_v1",
    typed: bool = True,
    evidence: bool = True,
):
    proposition = {"provider_note": "bounded"}
    if typed:
        proposition = embed_root_cause_candidate_semantics(
            proposition,
            RootCauseCandidateSemantics(
                explanatory_subject_ref=obligation_id,
                relation_kind=RootCauseCandidateRelation.EXPLANATORY_CANDIDATE,
                mechanism_ref=mechanism_ref,
                scope_lineage_id=lineage_id,
                scope_version_id=scope_version_id,
            ),
        )
    return SimpleNamespace(
        obligation_id=obligation_id,
        proposition=proposition,
        evidence_links=(SimpleNamespace(evidence_id="evi_1"),) if evidence else (),
    )


def _remaining(*claims):
    return remaining_discovery_mechanism_refs(
        snapshot=SimpleNamespace(claims=claims),
        obligation_id="g_root",
        scope_lineage_id="atl_current",
        scope_version_id="scope_v1",
        governed_mechanism_refs=(
            "metric.a",
            "metric.b",
            "metric.c",
            "metric.a",
        ),
    )


def test_current_evidence_linked_candidate_is_consumed_once():
    assert _remaining(_claim("metric.a")) == (
        "metric.b",
        "metric.c",
    )


def test_foreign_or_historical_claims_do_not_consume_current_vocabulary():
    assert _remaining(
        _claim("metric.a", obligation_id="g_other"),
        _claim("metric.b", lineage_id="atl_old"),
        _claim("metric.c", scope_version_id="scope_v2"),
    ) == (
        "metric.a",
        "metric.b",
        "metric.c",
    )


def test_untyped_or_ungrounded_claims_do_not_consume_current_vocabulary():
    assert _remaining(
        _claim("metric.a", typed=False),
        _claim("metric.b", evidence=False),
    ) == (
        "metric.a",
        "metric.b",
        "metric.c",
    )



def _project(
    *,
    allowed=("metric.effect", "metric.a", "metric.b", "metric.c"),
    current=("metric.effect", "metric.a", "metric.b", "metric.c"),
    observed=("metric.effect", "metric.a", "metric.b", "metric.c"),
    eligible=("metric.effect", "metric.a", "metric.b", "metric.c"),
    effect="metric.effect",
):
    return project_candidate_set(
        allowed_discovery_surface=allowed,
        current_scope_semantic_refs=current,
        observed_material_semantic_refs=observed,
        candidate_eligible_semantic_refs=eligible,
        effect_semantic_id=effect,
        scope_version_id="scope_v1",
        evidence_refs=("evi_" + "1" * 24,),
        material_requirement_ref="g_root",
    )


def test_candidate_projection_is_exact_typed_intersection_and_excludes_effect():
    projected = _project(
        current=("metric.effect", "metric.a", "metric.b"),
        observed=("metric.effect", "metric.a", "metric.c"),
        eligible=("metric.effect", "metric.a", "metric.b", "metric.c"),
    )

    assert tuple(item.semantic_id for item in projected.candidates) == ("metric.a",)
    candidate = projected.candidates[0]
    assert candidate.source == "OBSERVED_GOVERNED_MATERIAL"
    assert candidate.scope_version_id == "scope_v1"
    assert candidate.evidence_refs == ("evi_" + "1" * 24,)
    assert candidate.material_requirement_ref == "g_root"


def test_candidate_projection_preserves_all_legal_candidates_without_forcing_two():
    projected = _project()
    assert tuple(item.semantic_id for item in projected.candidates) == (
        "metric.a",
        "metric.b",
        "metric.c",
    )


def test_candidate_projection_allows_zero_or_one_without_fabricating_competitor():
    zero = _project(observed=("metric.effect",))
    one = _project(observed=("metric.effect", "metric.b"))
    assert zero.candidates == ()
    assert tuple(item.semantic_id for item in one.candidates) == ("metric.b",)


def test_candidate_projection_deduplicates_identity_without_text_matching():
    projected = _project(
        allowed=("metric.effect", "metric.a", "metric.a", "metric.b"),
        current=("metric.effect", "metric.a", "metric.b", "metric.a"),
        observed=("metric.effect", "metric.a", "metric.a", "metric.b"),
        eligible=("metric.effect", "metric.a", "metric.b"),
    )
    assert tuple(item.semantic_id for item in projected.candidates) == (
        "metric.a",
        "metric.b",
    )


def test_candidate_projection_rejects_observed_metric_outside_allowed_surface():
    projected = _project(
        allowed=("metric.effect", "metric.a"),
        observed=("metric.effect", "metric.a", "metric.b", "metric.c"),
    )
    assert tuple(item.semantic_id for item in projected.candidates) == ("metric.a",)


def test_candidate_projection_does_not_promote_unrelated_dimension():
    projected = project_candidate_set(
        allowed_discovery_surface=(
            "metric.effect",
            "metric.a",
            "dimension.department",
        ),
        current_scope_semantic_refs=(
            "metric.effect",
            "metric.a",
            "dimension.department",
        ),
        observed_material_semantic_refs=(
            "metric.effect",
            "metric.a",
            "dimension.department",
        ),
        candidate_eligible_semantic_refs=("metric.effect", "metric.a"),
        effect_semantic_id="metric.effect",
        scope_version_id="scope_v1",
        evidence_refs=("evi_" + "2" * 24,),
        material_requirement_ref="g_root",
    )
    assert tuple(item.semantic_id for item in projected.candidates) == ("metric.a",)


def test_candidate_projection_bounds_large_observed_surface_to_authority():
    observed = ("metric.effect",) + tuple(
        f"metric.observed_{index}" for index in range(30)
    )
    allowed = (
        "metric.effect",
        "metric.observed_3",
        "metric.observed_11",
        "metric.observed_27",
    )
    projected = project_candidate_set(
        allowed_discovery_surface=allowed,
        current_scope_semantic_refs=observed,
        observed_material_semantic_refs=observed,
        candidate_eligible_semantic_refs=observed,
        effect_semantic_id="metric.effect",
        scope_version_id="scope_v1",
        evidence_refs=("evi_" + "3" * 24,),
        material_requirement_ref="g_root",
    )
    assert tuple(item.semantic_id for item in projected.candidates) == (
        "metric.observed_3",
        "metric.observed_11",
        "metric.observed_27",
    )
