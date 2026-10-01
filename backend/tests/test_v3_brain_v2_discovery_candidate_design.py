from types import SimpleNamespace

from app.v3.brain_v2.discovery_candidate_design import (
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
