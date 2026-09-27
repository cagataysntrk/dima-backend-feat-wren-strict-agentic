from __future__ import annotations

import json

import pytest

from app.v2.manager_models import (
    CandidateObligation,
    ManagerCapabilityKey,
    ObligationOrigin,
    SemanticBindingRef,
)
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    SemanticLinkAuthorityError,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from app.v2.source_spans import SourceSpanRegistry
from app.v2.standard_coverage import StandardCoverageVeto


def _duplicate_context(*, reverse=False):
    cubes = [
        CompactCubeContextV0(
            canonical_name="orders",
            display="Orders",
            synonyms=("invoices",),
            measures=(
                CompactSemanticFieldV0(
                    canonical_name="orders.amount",
                    display="Invoice Total",
                    synonyms=("invoice total",),
                ),
            ),
            dimensions=(
                CompactSemanticFieldV0(
                    canonical_name="orders.account_code",
                    display="Account Code",
                    synonyms=("account code",),
                ),
            ),
        ),
        CompactCubeContextV0(
            canonical_name="ledger",
            display="Ledger",
            synonyms=("accounting ledger",),
            measures=(
                CompactSemanticFieldV0(
                    canonical_name="ledger.balance",
                    display="Balance",
                    synonyms=("balance",),
                ),
            ),
            dimensions=(
                CompactSemanticFieldV0(
                    canonical_name="ledger.account_code",
                    display="Account Code",
                    synonyms=("account code",),
                ),
            ),
        ),
    ]
    if reverse:
        cubes.reverse()
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-attack",
            mdl_version="mdl-attack",
            compact_catalog_builder_version="attack-test",
            business_rules_hash="a" * 64,
            prompt_context_policy_version="attack-test",
        ),
        cubes=tuple(cubes),
    )


class _ContextAwareProvider:
    def __init__(self, *, abstain=False, escape=False):
        self.calls = 0
        self.requests = ()
        self.abstain = abstain
        self.escape = escape

    def decide(self, requests):
        self.calls += 1
        self.requests = requests
        choices = []
        for request in requests:
            if self.abstain:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="AMBIGUOUS",
                    )
                )
                continue
            if self.escape:
                candidate_id = "cand_" + "f" * 24
            else:
                candidate_id = next(
                    card.candidate_id
                    for card in request.candidates
                    if "Orders" in card.cube_labels
                )
            choices.append(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=candidate_id,
                )
            )
        return SemanticLinkBatchDecision(choices=tuple(choices))


def _duplicate_linker(provider, *, reverse=False):
    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=SemanticCandidateGenerator(
            semantic_context=_duplicate_context(reverse=reverse),
            schema={"models": [], "cubes": [], "company_vocabulary": []},
        ),
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-attack",
        ),
        provider=provider,
    )
    return linker, handles


def test_duplicate_exact_without_context_remains_fail_closed():
    provider = _ContextAwareProvider()
    linker, _ = _duplicate_linker(provider)

    (selection,) = linker.resolve(
        (("dup-1", "account code", "dimension"),),
        provenance_type="USER_SOURCE",
    )

    assert selection.status == "AMBIGUOUS_EXACT"
    assert selection.binding is None
    assert provider.calls == 0


def test_duplicate_exact_with_immutable_context_is_decided_only_inside_exact_set():
    provider = _ContextAwareProvider()
    linker, handles = _duplicate_linker(provider)

    (selection,) = linker.resolve(
        (("dup-2", "account code", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="show invoice total by account code",
    )

    assert provider.calls == 1
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert request.source_context == "show invoice total by account code"
    assert len(request.candidates) == 2
    assert {
        tuple(card.cube_labels) for card in request.candidates
    } == {("Orders",), ("Ledger",)}

    assert selection.status == "BOUND"
    assert selection.mode == "LINKER"
    assert selection.binding is not None
    assert selection.binding.canonical_target.canonical_name == (
        "orders.account_code"
    )

    handle = linker.bind_selection(
        selection,
        provenance_type="USER_SOURCE",
    )
    binding = handles.binding_for_execution(
        handle.handle_id,
        tenant_binding="tenant-a",
        context_version="ctx-attack",
    )
    assert binding.canonical_target.canonical_name == "orders.account_code"


def test_duplicate_exact_with_still_ambiguous_context_can_abstain():
    provider = _ContextAwareProvider(abstain=True)
    linker, _ = _duplicate_linker(provider)

    (selection,) = linker.resolve(
        (("dup-3", "account code", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="account code report",
    )

    assert provider.calls == 1
    assert selection.status == "ABSTAIN"
    assert selection.binding is None


def test_duplicate_exact_context_outcome_is_catalog_order_invariant():
    selected = []
    for reverse in (False, True):
        provider = _ContextAwareProvider()
        linker, _ = _duplicate_linker(provider, reverse=reverse)
        (selection,) = linker.resolve(
            (("dup-order", "account code", "dimension"),),
            provenance_type="USER_SOURCE",
            decision_context="show invoice total by account code",
        )
        assert selection.status == "BOUND"
        selected.append(selection.binding.canonical_target.canonical_name)
    assert selected == ["orders.account_code", "orders.account_code"]


def _coverage_fixture(question: str, *, semantic_surfaces: tuple[str, ...]):
    spans = SourceSpanRegistry()
    digest = spans.register_message(message_id="m1", text=question)
    whole = spans.mint_exact(message_id="m1", surface=question)
    bindings = []
    handles = []
    for index, surface in enumerate(semantic_surfaces, start=1):
        span = spans.mint_exact(message_id="m1", surface=surface)
        handle_id = "sem_" + f"{index:024x}"
        handles.append(handle_id)
        bindings.append(
            SemanticBindingRef(
                source_ref=span.source_ref,
                handle_id=handle_id,
                target_kind="metric" if index == 1 else "filter",
            )
        )
    obligation = CandidateObligation(
        obligation_id="U1",
        capability_key=ManagerCapabilityKey.PERFORMANCE,
        origin=ObligationOrigin.USER_MUST,
        source_refs=(whole.source_ref,),
        semantic_handle_refs=tuple(handles),
        semantic_bindings=tuple(bindings),
    )
    return spans, digest, obligation


class _CaptureCoverage:
    def __init__(self, response):
        self.response = response
        self.payload = None

    def __call__(self, system, user, *, schema, schema_name):
        self.payload = json.loads(user)
        return self.response


def test_coverage_view_exposes_actual_bound_semantic_surfaces_for_conservation():
    question = "yüksek cari bakiyeyi göster"
    spans, digest, obligation = _coverage_fixture(
        question,
        semantic_surfaces=("cari bakiyeyi",),
    )
    capture = _CaptureCoverage({"status": "PASS", "issues": []})
    coverage = StandardCoverageVeto(
        structured=capture,
        source_spans=spans,
    )

    coverage.audit(
        question=question,
        obligations=(obligation,),
        source_message_hash=digest,
    )

    item = capture.payload["STANDARD_INTENT_VIEW"][0]
    assert item["source_surfaces"] == [question]
    assert item["semantic_source_surfaces"] == ["cari bakiyeyi"]


def test_coverage_view_can_distinguish_concrete_filter_from_lost_qualifier():
    question = "net gelir Kuzey"
    spans, digest, obligation = _coverage_fixture(
        question,
        semantic_surfaces=("net gelir", "Kuzey"),
    )
    capture = _CaptureCoverage({"status": "PASS", "issues": []})
    coverage = StandardCoverageVeto(
        structured=capture,
        source_spans=spans,
    )

    coverage.audit(
        question=question,
        obligations=(obligation,),
        source_message_hash=digest,
    )

    item = capture.payload["STANDARD_INTENT_VIEW"][0]
    assert item["semantic_source_surfaces"] == ["net gelir", "Kuzey"]


def test_coverage_contract_explicitly_guards_material_modifier_predicate_loss():
    import app.v2.standard_coverage as module

    prompt = module._STANDARD_COVERAGE_SYSTEM.casefold()
    assert "qualifier" in prompt or "modifier" in prompt
    assert "predicate" in prompt
    assert "silently" in prompt or "silent" in prompt



def test_duplicate_exact_context_candidate_escape_is_rejected():
    provider = _ContextAwareProvider(escape=True)
    linker, _ = _duplicate_linker(provider)

    with pytest.raises(SemanticLinkAuthorityError, match="outside"):
        linker.resolve(
            (("dup-escape", "account code", "dimension"),),
            provenance_type="USER_SOURCE",
            decision_context="show invoice total by account code",
        )

    assert provider.calls == 1


def _turkish_inflection_context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-tr-inflect",
            mdl_version="mdl-tr-inflect",
            compact_catalog_builder_version="tr-inflect-test",
            business_rules_hash="b" * 64,
            prompt_context_policy_version="tr-inflect-test",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="cari",
                display="Cari Hesap",
                synonyms=("cari",),
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="cari.bakiye",
                        display="Bakiye",
                        synonyms=("açık bakiye",),
                    ),
                ),
            ),
            CompactCubeContextV0(
                canonical_name="mizan",
                display="Mizan",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="mizan.bakiye",
                        display="Bakiye",
                        synonyms=("hesap bakiyesi",),
                    ),
                ),
            ),
        ),
    )


def test_turkish_inflected_surface_keeps_relevant_candidate_via_governed_context():
    generator = SemanticCandidateGenerator(
        semantic_context=_turkish_inflection_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )

    candidate_set = generator.generate(
        request_id="tr-inflect",
        surface="cari bakiyeyi",
        kind_hint="metric",
        decision_context="tahsil edilmemiş cari bakiyeyi göster",
    )

    canonical = {
        item.canonical_target.canonical_name
        for item in candidate_set.bindings
    }
    assert "cari.bakiye" in canonical
    assert candidate_set.retrieval_backend == "governed_token_index_v1"
    assert candidate_set.too_broad is False


def test_coverage_veto_can_quote_exact_lost_modifier_without_minting_semantics():
    question = "yüksek cari bakiyeyi göster"
    spans, digest, obligation = _coverage_fixture(
        question,
        semantic_surfaces=("cari bakiyeyi",),
    )
    capture = _CaptureCoverage(
        {
            "status": "VETO",
            "issues": [
                {
                    "kind": "MATERIAL_REQUEST_OMITTED",
                    "source_surfaces": ["yüksek"],
                    "note": "material threshold/qualifier is not represented",
                }
            ],
        }
    )
    coverage = StandardCoverageVeto(
        structured=capture,
        source_spans=spans,
    )

    audit = coverage.audit(
        question=question,
        obligations=(obligation,),
        source_message_hash=digest,
    )

    assert audit.status == "VETO"
    assert audit.issues[0].source_surfaces == ("yüksek",)
