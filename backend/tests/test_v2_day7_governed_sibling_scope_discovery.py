"""Provider-free attack family for GOVERNED_SIBLING_SCOPE_DISCOVERY LAB."""

from __future__ import annotations

from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    GovernedSiblingScopeCandidateGenerator,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from lab.v2_day7_governed_sibling_scope_discovery import (
    DEFAULT_MAX_CANDIDATES,
    _bind_exact_sibling,
    _canonical_name,
    _context,
    build_receipt,
)


class _SelectProvider:
    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        assert len(requests) == 1
        request = requests[0]
        assert self.candidate_id in {
            item.candidate_id for item in request.candidates
        }
        return SemanticLinkBatchDecision(
            choices=(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=self.candidate_id,
                ),
            )
        )


class _AbstainProvider:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        return SemanticLinkBatchDecision(
            choices=tuple(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="ABSTAIN",
                    reason="NO_MATCH",
                )
                for request in requests
            )
        )


class _ForbiddenProvider:
    def decide(self, requests):
        raise AssertionError("too-broad candidate set must never reach cognition")


def _base_and_scope(*, sibling_surface: str, sibling_kind: str, context_text: str):
    service, context = _context()
    handles = SemanticHandleRegistry()
    base = SemanticCandidateGenerator(
        semantic_context=context,
        schema=service.schema(),
        max_candidates=DEFAULT_MAX_CANDIDATES,
    )
    _, scope = _bind_exact_sibling(
        generator=base,
        handles=handles,
        context_version=context.context_version.version,
        surface=sibling_surface,
        kind_hint=sibling_kind,
        decision_context=context_text,
    )
    scoped = GovernedSiblingScopeCandidateGenerator(
        base=base,
        sibling_cube_names=scope,
        max_candidates=DEFAULT_MAX_CANDIDATES,
    )
    return service, context, handles, base, scoped


def test_positive_variations_recover_expected_candidate_without_language_rule():
    receipt = build_receipt()
    rows = {row["surface"]: row for row in receipt["rows"]}

    for surface in (
        "bölge",
        "bölgeler",
        "bölgelere",
        "Bölgelerde",
        "ürün",
        "ürünler",
        "ürünlere",
        "bölüm",
        "bölümler",
        "bölümlerle",
    ):
        assert rows[surface]["expected_candidate_visible"] is True
        assert rows[surface]["outside_scope_count"] == 0
        assert rows[surface]["authority_minted_by_discovery"] is False

    # Existing token retrieval remains primary where it already works.
    for surface in ("bölge", "bölgeler", "ürün", "ürünler", "bölüm", "bölümler"):
        assert rows[surface]["fallback_used"] is False

    # Only retrieval misses exercise the LAB sibling-scope fallback.
    for surface in ("bölgelere", "Bölgelerde", "ürünlere", "bölümlerle"):
        assert rows[surface]["baseline_candidate_count"] == 0
        assert rows[surface]["fallback_used"] is True
        assert rows[surface]["linker_required"] is True


def test_discovery_recovery_still_requires_cognition_before_authority():
    _, context, handles, _, scoped = _base_and_scope(
        sibling_surface="net gelir",
        sibling_kind="metric",
        context_text="Net geliri bölgelere göre kır.",
    )
    before = set(handles._bindings)

    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context.context_version.version,
        ),
        provider=None,
    )
    selection = linker.resolve(
        (("target", "bölgelere", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="Net geliri bölgelere göre kır.",
    )[0]

    assert selection.status == "LINKER_UNAVAILABLE"
    assert selection.binding is None
    assert set(handles._bindings) == before


def test_bounded_cognition_select_then_existing_binding_gate_mints_authority():
    _, context, handles, _, scoped = _base_and_scope(
        sibling_surface="net gelir",
        sibling_kind="metric",
        context_text="Net geliri bölgelere göre kır.",
    )
    candidate_set = scoped.generate(
        request_id="target",
        surface="bölgelere",
        kind_hint="dimension",
        decision_context="Net geliri bölgelere göre kır.",
    )
    expected = next(
        item for item in candidate_set.bindings
        if _canonical_name(item) == "region_axis_m"
    )
    provider = _SelectProvider(expected.card.candidate_id)
    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context.context_version.version,
        ),
        provider=provider,
    )

    selection = linker.resolve(
        (("target", "bölgelere", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="Net geliri bölgelere göre kır.",
    )[0]
    assert selection.status == "BOUND"
    assert selection.mode == "LINKER"
    assert provider.calls == 1

    handle = linker.bind_selection(selection, provenance_type="USER_SOURCE")
    binding = handles.binding_for_execution(
        handle.handle_id,
        tenant_binding="id:day7-sibling-scope-lab",
        context_version=context.context_version.version,
    )
    assert binding.canonical_target.canonical_name == "region_axis_m"


def test_unknown_surface_can_abstain_without_forced_binding():
    _, context, handles, _, scoped = _base_and_scope(
        sibling_surface="net gelir",
        sibling_kind="metric",
        context_text="Net gelir için tamamen bilinmeyen ekseni incele.",
    )
    provider = _AbstainProvider()
    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context.context_version.version,
        ),
        provider=provider,
    )
    before = set(handles._bindings)

    selection = linker.resolve(
        (("unknown", "tamamen bilinmeyen eksen", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="Net gelir için tamamen bilinmeyen ekseni incele.",
    )[0]

    assert selection.status == "ABSTAIN"
    assert provider.calls == 1
    assert set(handles._bindings) == before


def test_same_cube_scope_does_not_invent_cross_domain_candidate():
    _, _, _, _, scoped = _base_and_scope(
        sibling_surface="net gelir",
        sibling_kind="metric",
        context_text="Net gelirin bölümlerle ilişkisini incele.",
    )
    candidate_set = scoped.generate(
        request_id="cross-domain",
        surface="bölümlerle",
        kind_hint="dimension",
        decision_context="Net gelirin bölümlerle ilişkisini incele.",
    )

    assert candidate_set.retrieval_backend == "governed_sibling_scope_v1"
    assert "department_axis_d" not in {
        _canonical_name(item) for item in candidate_set.bindings
    }
    assert {
        _canonical_name(item) for item in candidate_set.bindings
    } == {"region_axis_m", "product_axis_n", "channel_axis_c"}


def test_missing_resolved_sibling_does_not_widen_discovery():
    service, context = _context()
    handles = SemanticHandleRegistry()
    base = SemanticCandidateGenerator(
        semantic_context=context,
        schema=service.schema(),
    )
    scoped = GovernedSiblingScopeCandidateGenerator(
        base=base,
        sibling_cube_names=(),
    )
    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context.context_version.version,
        ),
        provider=None,
    )

    selection = linker.resolve(
        (("missing-sibling", "bölgelere", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="Bölgelere göre incele.",
    )[0]

    assert selection.status == "RETRIEVAL_MISS"


def _wide_context(*, unrelated_dimensions: int = 0):
    wide_dimensions = tuple(
        CompactSemanticFieldV0(
            canonical_name=f"axis_{i:02d}",
            display=f"Axis {i:02d}",
            synonyms=(f"axis {i:02d}",),
        )
        for i in range(60)
    )
    cubes = [
        CompactCubeContextV0(
            canonical_name="wide_cube",
            measures=(
                CompactSemanticFieldV0(
                    canonical_name="revenue",
                    display="Revenue",
                    synonyms=("revenue",),
                ),
            ),
            dimensions=wide_dimensions,
        )
    ]
    if unrelated_dimensions:
        cubes.append(
            CompactCubeContextV0(
                canonical_name="unrelated_cube",
                measures=(),
                dimensions=tuple(
                    CompactSemanticFieldV0(
                        canonical_name=f"unrelated_{i:02d}",
                        display=f"Unrelated {i:02d}",
                        synonyms=(f"unrelated {i:02d}",),
                    )
                    for i in range(unrelated_dimensions)
                ),
            )
        )
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-wide",
            mdl_version="mdl-wide",
            compact_catalog_builder_version="lab",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="lab",
        ),
        cubes=tuple(cubes),
    )
    schema = {
        "cubes": [
            {
                "name": cube.canonical_name,
                "measures": [
                    field.canonical_name for field in cube.measures
                ],
                "dimensions": [
                    field.canonical_name for field in cube.dimensions
                ],
                "dimension_values": {},
            }
            for cube in cubes
        ],
        "models": [],
        "company_vocabulary": [],
    }
    return context, schema


def test_scope_above_bound_stops_before_linker():
    context, schema = _wide_context()
    handles = SemanticHandleRegistry()
    base = SemanticCandidateGenerator(
        semantic_context=context,
        schema=schema,
        max_candidates=DEFAULT_MAX_CANDIDATES,
    )
    scoped = GovernedSiblingScopeCandidateGenerator(
        base=base,
        sibling_cube_names=("wide_cube",),
        max_candidates=DEFAULT_MAX_CANDIDATES,
    )
    candidate_set = scoped.generate(
        request_id="broad",
        surface="unmatched surface",
        kind_hint="dimension",
        decision_context="revenue unmatched surface",
    )
    assert candidate_set.too_broad is True
    assert candidate_set.retrieval_truncated is True
    assert len(candidate_set.bindings) == DEFAULT_MAX_CANDIDATES

    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:wide",
            context_version=context.context_version.version,
        ),
        provider=_ForbiddenProvider(),
    )
    selection = linker.resolve(
        (("broad", "unmatched surface", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="revenue unmatched surface",
    )[0]
    assert selection.status == "CANDIDATE_SET_TOO_BROAD"


def test_unrelated_catalog_growth_does_not_expand_scoped_candidate_set():
    base_context, base_schema = _wide_context(unrelated_dimensions=0)
    grown_context, grown_schema = _wide_context(unrelated_dimensions=80)

    base_generator = SemanticCandidateGenerator(
        semantic_context=base_context,
        schema=base_schema,
        max_candidates=100,
    )
    grown_generator = SemanticCandidateGenerator(
        semantic_context=grown_context,
        schema=grown_schema,
        max_candidates=100,
    )
    base_scoped = GovernedSiblingScopeCandidateGenerator(
        base=base_generator,
        sibling_cube_names=("wide_cube",),
        max_candidates=100,
    )
    grown_scoped = GovernedSiblingScopeCandidateGenerator(
        base=grown_generator,
        sibling_cube_names=("wide_cube",),
        max_candidates=100,
    )

    base_set = base_scoped.generate(
        request_id="base",
        surface="unmatched",
        kind_hint="dimension",
        decision_context="revenue unmatched",
    )
    grown_set = grown_scoped.generate(
        request_id="grown",
        surface="unmatched",
        kind_hint="dimension",
        decision_context="revenue unmatched",
    )

    assert len(base_set.bindings) == 60
    assert len(grown_set.bindings) == 60
    assert {
        _canonical_name(item) for item in base_set.bindings
    } == {
        _canonical_name(item) for item in grown_set.bindings
    }
