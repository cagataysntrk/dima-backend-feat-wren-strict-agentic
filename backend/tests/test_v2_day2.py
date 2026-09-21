"""Focused P5 tests for deterministic semantic grounding and clarification."""

from __future__ import annotations

import inspect

import pytest

from app.v2.models import (
    BoundedSemanticContextV0,
    CandidateSource,
    ClarificationReason,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
    ResolutionStatus,
    SemanticAnchor,
    SemanticMention,
    SemanticMentionKind,
    SemanticTargetKind,
    TurnAct,
    TurnInterpretation,
    AnalyticalRequest,
)
from app.v2.resolver import ClarificationTokenError, SemanticResolver, _morph_token_forms


CTX = ContextVersionV0(
    version="ctx-day2",
    mdl_version="mdl-day2",
    compact_catalog_builder_version="v0.1",
    business_rules_hash="rules",
    prompt_context_policy_version="v0.1",
)


def semantic_context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=CTX,
        cubes=(
            CompactCubeContextV0(
                canonical_name="finans",
                display="Finans",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="cari_bakiye",
                        display="Cari Bakiye",
                        synonyms=("bakiye", "müşteri bakiyesi"),
                        unit="TRY",
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="ciro",
                        display="Ciro",
                        synonyms=("satış", "hasılat"),
                        unit="TRY",
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="musteri",
                        display="Müşteri",
                        synonyms=("cari", "müşteri"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="renk",
                        display="Renk",
                        synonyms=("renk",),
                    ),
                ),
            ),
            CompactCubeContextV0(
                canonical_name="uretim",
                display="Üretim",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="oee",
                        display="OEE",
                        synonyms=("verimlilik",),
                        unit="%",
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="makine",
                        display="Makine",
                        synonyms=("tezgah",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="vardiya",
                        display="Vardiya",
                        synonyms=("vardiya",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="segment",
                        display="Segment",
                        synonyms=("ürün segmenti",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="personel_ad_soyad",
                        display="Personel",
                        synonyms=("personel",),
                    ),
                ),
            ),
        ),
        kpis=(
            CompactSemanticFieldV0(
                canonical_name="teslimat_performansi",
                display="Teslimat Performansı",
                synonyms=("zamanında teslimat",),
                unit="%",
            ),
        ),
    )


def schema() -> dict:
    return {
        "models": [
            {
                "name": "finans_src",
                "columns": [
                    {"name": "musteri", "type": "VARCHAR"},
                    {"name": "renk", "type": "VARCHAR"},
                ],
            },
            {
                "name": "uretim_src",
                "columns": [
                    {"name": "makine", "type": "VARCHAR"},
                    {"name": "vardiya", "type": "VARCHAR"},
                    {"name": "segment", "type": "VARCHAR"},
                    {
                        "name": "personel_ad_soyad",
                        "type": "VARCHAR",
                        "sensitivity": "person",
                    },
                ],
            },
        ],
        "cubes": [
            {
                "name": "finans",
                "dimension_values": {
                    "renk": ["Siyah", "Mavi"],
                    "musteri": ["Siyah Tekstil", "Acme"],
                },
            },
            {
                "name": "uretim",
                "dimension_values": {
                    "makine": ["RAM-3", "RAM-4"],
                    "vardiya": ["Gece", "Gündüz"],
                    "segment": ["Premium", "Standart"],
                    "personel_ad_soyad": ["Ali Veli", "Ayşe Yılmaz"],
                },
            },
        ],
        "company_vocabulary": [
            {
                "verified": True,
                "surface": "nakit pozisyonu",
                "target_kind": "metric",
                "canonical_name": "cari_bakiye",
                "display_label": "Cari Bakiye · şirket sözlüğü",
                "cube_names": ["finans"],
            }
        ],
    }


def resolver() -> SemanticResolver:
    return SemanticResolver(signing_key=b"day2-test-signing-key")


def turn(text: str, kind: SemanticMentionKind) -> TurnInterpretation:
    field = {
        SemanticMentionKind.METRIC: "metric_mentions",
        SemanticMentionKind.DIMENSION: "dimension_mentions",
        SemanticMentionKind.FILTER: "filter_mentions",
    }[kind]
    return TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            **{field: (SemanticMention(text=text, kind=kind),)}
        ),
    )


def resolve(text: str, kind: SemanticMentionKind, *, conversation=None):
    return resolver().resolve_turn(
        turn=turn(text, kind),
        schema=schema(),
        semantic_context=semantic_context(),
        conversation=conversation or ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )


def test_canonical_and_verified_synonym_resolve_without_clarification():
    canonical = resolve("ciro", SemanticMentionKind.METRIC)
    synonym = resolve("bakiye", SemanticMentionKind.METRIC)

    assert canonical.clarification is None
    assert synonym.clarification is None
    assert canonical.hypotheses[0].status == ResolutionStatus.RESOLVED
    assert synonym.hypotheses[0].status == ResolutionStatus.RESOLVED
    assert CandidateSource.CANONICAL_NAME in canonical.hypotheses[0].candidates[0].provenance
    assert CandidateSource.VERIFIED_SYNONYM in synonym.hypotheses[0].candidates[0].provenance


@pytest.mark.parametrize(
    ("surface", "expected_dimension"),
    [
        ("RAM-3", "makine"),
        ("gece", "vardiya"),
        ("premium", "segment"),
    ],
)
def test_exact_entity_families_use_same_generic_mechanism(surface, expected_dimension):
    bundle = resolve(surface, SemanticMentionKind.FILTER)
    assert bundle.clarification is None
    hyp = bundle.hypotheses[0]
    assert hyp.status == ResolutionStatus.RESOLVED
    chosen = next(c for c in hyp.candidates if c.candidate_id == hyp.resolved_candidate_id)
    assert chosen.target_kind == SemanticTargetKind.ENTITY_VALUE
    assert chosen.dimension_name == expected_dimension
    assert CandidateSource.EXACT_ENTITY_VALUE in chosen.provenance


def test_material_entity_ambiguity_clarifies_and_never_auto_picks():
    bundle = resolve("siyah", SemanticMentionKind.FILTER)

    assert bundle.clarification is not None
    assert bundle.clarification.reason == ClarificationReason.MATERIAL_AMBIGUITY
    assert bundle.hypotheses[0].status == ResolutionStatus.CLARIFY
    assert bundle.hypotheses[0].resolved_candidate_id is None

    labels = {c.display_label for c in bundle.clarification.candidates}
    assert "Renk = Siyah" in labels
    assert "Müşteri = Siyah Tekstil" in labels


def test_fuzzy_only_is_suggestion_not_auto_resolution():
    bundle = resolve("bakiy", SemanticMentionKind.METRIC)

    assert bundle.clarification is not None
    assert bundle.clarification.reason == ClarificationReason.FUZZY_ONLY
    assert bundle.hypotheses[0].resolved_candidate_id is None
    assert CandidateSource.FUZZY_SUGGESTION in bundle.clarification.candidates[0].provenance


@pytest.mark.parametrize(
    ("surface", "kind", "canonical"),
    [
        ("müşterilere", SemanticMentionKind.DIMENSION, "musteri"),
        ("müşterilere göre", SemanticMentionKind.DIMENSION, "musteri"),
        ("vardiyalarda", SemanticMentionKind.DIMENSION, "vardiya"),
        ("vardiyalarda bazında", SemanticMentionKind.DIMENSION, "vardiya"),
        ("satışların", SemanticMentionKind.METRIC, "ciro"),
    ],
)
def test_turkish_inflection_resolves_only_through_verified_semantic_aliases(
    surface,
    kind,
    canonical,
):
    bundle = resolve(surface, kind)

    assert bundle.clarification is None, {
        "surface": _morph_token_forms(surface),
        "customer": _morph_token_forms("müşteri"),
        "shift": _morph_token_forms("vardiya"),
        "sales": _morph_token_forms("satış"),
    }
    hyp = bundle.hypotheses[0]
    assert hyp.status == ResolutionStatus.RESOLVED
    chosen = next(c for c in hyp.candidates if c.candidate_id == hyp.resolved_candidate_id)
    assert chosen.canonical_name == canonical
    assert CandidateSource.MORPHOLOGICAL_MATCH in chosen.provenance


def test_unknown_surface_becomes_semantic_gap():
    bundle = resolve("xyzqwerty", SemanticMentionKind.METRIC)

    assert bundle.clarification is not None
    assert bundle.clarification.reason == ClarificationReason.SEMANTIC_GAP
    assert bundle.clarification.candidates == ()
    assert bundle.hypotheses[0].status == ResolutionStatus.SEMANTIC_GAP


def test_verified_company_vocabulary_is_used_only_with_explicit_provenance():
    bundle = resolve("nakit pozisyonu", SemanticMentionKind.METRIC)
    assert bundle.clarification is None
    candidate = bundle.hypotheses[0].candidates[0]
    assert CandidateSource.COMPANY_VOCABULARY in candidate.provenance


def test_explicit_anchor_can_win_as_typed_provenance_without_label_guessing():
    conversation = ConversationStateV2(
        selected_anchor=SemanticAnchor(
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="ciro",
            display_label="Net Satış",
            aliases=("net satış",),
        )
    )
    bundle = resolve("net satış", SemanticMentionKind.METRIC, conversation=conversation)

    assert bundle.clarification is None
    candidate = bundle.hypotheses[0].candidates[0]
    assert CandidateSource.EXPLICIT_ANCHOR in candidate.provenance


def test_sensitive_values_are_not_fuzzy_discovered_and_exact_chip_does_not_reveal_value():
    fuzzy = resolve("Ali", SemanticMentionKind.FILTER)
    assert fuzzy.clarification is not None
    assert all(
        c.dimension_name != "personel_ad_soyad"
        for c in fuzzy.clarification.candidates
    )

    exact = resolve("Ali Veli", SemanticMentionKind.FILTER)
    hyp = exact.hypotheses[0]
    assert hyp.status == ResolutionStatus.RESOLVED
    chosen = next(c for c in hyp.candidates if c.candidate_id == hyp.resolved_candidate_id)
    assert chosen.sensitive is True
    assert chosen.value is None
    assert "Ali Veli" not in chosen.display_label
    assert hyp.resolved_surface_value == "Ali Veli"


def test_signed_chip_resume_rederives_candidate_and_resolves_deterministically():
    r = resolver()
    first = r.resolve_turn(
        turn=turn("siyah", SemanticMentionKind.FILTER),
        schema=schema(),
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    clarification = first.clarification
    assert clarification is not None

    renk_chip = next(chip for chip in clarification.chips if chip.label == "Renk = Siyah")
    resumed = r.resume_signed(
        token=renk_chip.token,
        schema=schema(),
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )

    assert resumed.clarification is None
    assert resumed.hypotheses[0].status == ResolutionStatus.RESOLVED
    chosen = resumed.hypotheses[0].candidates[0]
    assert chosen.dimension_name == "renk"
    assert chosen.value == "Siyah"


@pytest.mark.parametrize(
    "mutation",
    ["tamper", "tenant", "context", "thread"],
)
def test_signed_chip_fails_closed_on_tamper_or_binding_mismatch(mutation):
    r = resolver()
    first = r.resolve_turn(
        turn=turn("siyah", SemanticMentionKind.FILTER),
        schema=schema(),
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    token = first.clarification.chips[0].token

    kwargs = {
        "token": token,
        "schema": schema(),
        "semantic_context": semantic_context(),
        "conversation": ConversationStateV2(),
        "tenant_binding": "id:t1",
        "session_id": "s1",
        "thread_id": "th1",
    }
    if mutation == "tamper":
        kwargs["token"] = token[:-1] + ("A" if token[-1] != "A" else "B")
    elif mutation == "tenant":
        kwargs["tenant_binding"] = "id:t2"
    elif mutation == "context":
        changed = semantic_context().model_copy(
            update={"context_version": CTX.model_copy(update={"version": "ctx-changed"})}
        )
        kwargs["semantic_context"] = changed
    elif mutation == "thread":
        kwargs["thread_id"] = "other"

    with pytest.raises(ClarificationTokenError):
        r.resume_signed(**kwargs)


def test_free_text_resume_uses_interpreter_mentions_not_raw_question_parser():
    r = resolver()
    first = r.resolve_turn(
        turn=turn("siyah", SemanticMentionKind.FILTER),
        schema=schema(),
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    pending = first.clarification
    assert pending is not None

    answer_turn = TurnInterpretation(
        dialogue_act=TurnAct.CLARIFICATION_ANSWER,
        analytical_request=AnalyticalRequest(
            filter_mentions=(
                SemanticMention(text="renk", kind=SemanticMentionKind.FILTER),
                SemanticMention(text="siyah", kind=SemanticMentionKind.FILTER),
            )
        ),
    )
    resumed = r.resume_free_text(
        turn=answer_turn,
        pending=pending,
        schema=schema(),
        semantic_context=semantic_context(),
        conversation=ConversationStateV2(
            pending_clarification=True,
            clarification_state=pending,
        ),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )

    assert resumed.clarification is None
    chosen = resumed.hypotheses[0].candidates[0]
    assert chosen.dimension_name == "renk"


def test_dedicated_p5_rates_are_green_on_focused_deterministic_set():
    # Exact known surfaces should not clarify; genuine ambiguity must clarify.
    exact_cases = [
        ("ciro", SemanticMentionKind.METRIC),
        ("bakiye", SemanticMentionKind.METRIC),
        ("RAM-3", SemanticMentionKind.FILTER),
        ("gece", SemanticMentionKind.FILTER),
        ("premium", SemanticMentionKind.FILTER),
    ]
    ambiguity_cases = [("siyah", SemanticMentionKind.FILTER)]

    unnecessary = sum(resolve(q, k).clarification is not None for q, k in exact_cases)
    false_auto = sum(resolve(q, k).clarification is None for q, k in ambiguity_cases)

    assert unnecessary / len(exact_cases) <= 0.10
    assert false_auto == 0


def test_resolver_has_no_literal_special_cases_or_execution_boundary_calls():
    import app.v2.resolver as module

    source = inspect.getsource(module).casefold()

    # User-scenario literals belong to tests/corpus, never resolver implementation.
    for literal in ("siyah", "ram-3", "gece", "premium", "bakiye"):
        assert literal not in source

    # Day 2 must not cross into execution/planning.
    for token in (".query(", ".dry_plan(", ".cube_sql(", "generate_sql(", "select_cube("):
        assert token not in source

    signature = inspect.signature(SemanticResolver.resolve_turn)
    assert "question" not in signature.parameters


def test_clarification_hmac_key_is_stable_and_domain_separated():
    from control_plane.security import derive_hmac_key

    a1 = derive_hmac_key("v2-clarification-chip-v1")
    a2 = derive_hmac_key("v2-clarification-chip-v1")
    other = derive_hmac_key("another-purpose")

    assert a1 == a2
    assert a1 != other
    assert len(a1) == 32


def test_exact_verified_match_dominates_fuzzy_material_lookalike():
    context = BoundedSemanticContextV0(
        context_version=CTX,
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="gross_revenue",
                        display="Brüt Gelir",
                        synonyms=("gelir",),
                    ),
                ),
            ),
        ),
    )
    turn = TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            metric_mentions=(
                SemanticMention(text="net gelir", kind=SemanticMentionKind.METRIC),
            ),
        ),
    )
    result = SemanticResolver(signing_key=b"x" * 32).resolve_turn(
        turn=turn,
        schema={"models": [], "cubes": [{"name": "sales", "dimension_values": {}}]},
        semantic_context=context,
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    assert result.clarification is None
    assert result.hypotheses[0].status == ResolutionStatus.RESOLVED
    assert result.hypotheses[0].candidates[0].canonical_name == "net_revenue"


def test_multiple_exact_verified_matches_still_clarify():
    context = BoundedSemanticContextV0(
        context_version=CTX,
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="metric_a",
                        display="A",
                        synonyms=("performans",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="metric_b",
                        display="B",
                        synonyms=("performans",),
                    ),
                ),
            ),
        ),
    )
    turn = TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            metric_mentions=(
                SemanticMention(text="performans", kind=SemanticMentionKind.METRIC),
            ),
        ),
    )
    result = SemanticResolver(signing_key=b"x" * 32).resolve_turn(
        turn=turn,
        schema={"models": [], "cubes": [{"name": "sales", "dimension_values": {}}]},
        semantic_context=context,
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    assert result.clarification is not None
    assert result.clarification.reason == ClarificationReason.MATERIAL_AMBIGUITY


def test_full_span_inflectional_match_dominates_shorter_contained_alias():
    context = BoundedSemanticContextV0(
        context_version=CTX,
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="gross_revenue",
                        display="Brüt Gelir",
                        synonyms=("gelir",),
                    ),
                ),
            ),
        ),
    )
    turn = TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            metric_mentions=(
                SemanticMention(text="net geliri", kind=SemanticMentionKind.METRIC),
            ),
        ),
    )
    result = SemanticResolver(signing_key=b"x" * 32).resolve_turn(
        turn=turn,
        schema={"models": [], "cubes": [{"name": "sales", "dimension_values": {}}]},
        semantic_context=context,
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    assert result.clarification is None
    assert result.hypotheses[0].status == ResolutionStatus.RESOLVED
    assert result.hypotheses[0].candidates[0].canonical_name == "net_revenue"


def test_equal_full_span_inflectional_matches_still_clarify():
    context = BoundedSemanticContextV0(
        context_version=CTX,
        cubes=(
            CompactCubeContextV0(
                canonical_name="ops",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="perf_a",
                        display="Performans A",
                        synonyms=("performans",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="perf_b",
                        display="Performans B",
                        synonyms=("performans",),
                    ),
                ),
            ),
        ),
    )
    turn = TurnInterpretation(
        dialogue_act=TurnAct.ANALYTIC_NEW,
        analytical_request=AnalyticalRequest(
            metric_mentions=(
                SemanticMention(text="performansı", kind=SemanticMentionKind.METRIC),
            ),
        ),
    )
    result = SemanticResolver(signing_key=b"x" * 32).resolve_turn(
        turn=turn,
        schema={"models": [], "cubes": [{"name": "ops", "dimension_values": {}}]},
        semantic_context=context,
        conversation=ConversationStateV2(),
        tenant_binding="id:t1",
        session_id="s1",
        thread_id="th1",
    )
    assert result.clarification is not None
    assert result.clarification.reason == ClarificationReason.MATERIAL_AMBIGUITY
