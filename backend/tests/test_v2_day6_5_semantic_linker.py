"""Provider-free invariants for the Day 6.5 bounded semantic linker."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    CatalogCandidateBinding,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    StructuredSemanticCandidateDecisionProvider,
    SemanticLinkAuthorityError,
    SemanticLinkCandidateCard,
)
from app.v2.semantic_retriever import SemanticRetrievalResult


def _context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-linker-v1",
            mdl_version="mdl-linker-v1",
            compact_catalog_builder_version="linker-test",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="linker-test",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                display="Satış",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="sales.net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir", "gelir"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="sales.gross_revenue",
                        display="Brüt Gelir",
                        synonyms=("brüt gelir", "gelir"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="sales.region",
                        display="Bölge",
                        synonyms=("bölge", "bölgeler"),
                    ),
                ),
            ),
        ),
    )


def _schema() -> dict:
    return {
        "models": [],
        "cubes": [
            {
                "name": "sales",
                "dimension_values": {
                    "sales.region": ["Kuzey", "Güney"],
                },
            }
        ],
        "company_vocabulary": [],
    }


class _Scripted:
    def __init__(self, response: dict):
        self.response = response
        self.calls = 0
        self.last_user = None

    def structured_json(self, system, user, *, schema, schema_name):
        del system, schema
        assert schema_name == "dima_bounded_semantic_link_v1"
        self.calls += 1
        self.last_user = json.loads(user)
        return self.response


def _linker(structured=None, *, max_candidates=48):
    handles = SemanticHandleRegistry()
    generator = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema=_schema(),
        max_candidates=max_candidates,
    )
    gate = SemanticBindingGate(
        semantic_handles=handles,
        tenant_binding="tenant-a",
        context_version="ctx-linker-v1",
    )
    return (
        BoundedSemanticLinker(
            generator=generator,
            binding_gate=gate,
            provider=(
                StructuredSemanticCandidateDecisionProvider(structured=structured)
                if structured is not None
                else None
            ),
        ),
        handles,
    )


def test_unique_exact_verified_alias_binds_without_model_call():
    scripted = _Scripted({"choices": []})
    linker, handles = _linker(scripted.structured_json)
    (selection,) = linker.resolve(
        (("r1", "net gelir", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "BOUND"
    assert selection.mode == "EXACT"
    assert scripted.calls == 0

    handle = linker.bind_selection(selection, provenance_type="USER_SOURCE")
    assert handle.handle_id.startswith("sem_")
    binding = handles.binding_for_execution(
        handle.handle_id,
        tenant_binding="tenant-a",
        context_version="ctx-linker-v1",
    )
    assert binding.canonical_target.canonical_name == "sales.net_revenue"


def test_true_exact_alias_ambiguity_abstains_without_model_guess():
    scripted = _Scripted({"choices": []})
    linker, _ = _linker(scripted.structured_json)
    (selection,) = linker.resolve(
        (("r1", "gelir", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "AMBIGUOUS_EXACT"
    assert selection.binding is None
    assert scripted.calls == 0


def test_non_exact_surface_is_interpreted_only_within_bounded_candidate_cards():
    # The test script selects the opaque candidate whose human label is Brüt Gelir.
    # Production code contains no phrase-specific rule.
    probe, _ = _linker(None)
    candidate_set = probe._generator.generate(
        request_id="r1",
        surface="brüt gelir toplamı",
        kind_hint="metric",
    )
    gross = next(
        item.card.candidate_id
        for item in candidate_set.bindings
        if item.card.label == "Brüt Gelir"
    )
    scripted = _Scripted(
        {
            "choices": [
                {
                    "request_id": "r1",
                    "decision": "SELECT",
                    "candidate_id": gross,
                    "reason": None,
                }
            ]
        }
    )
    linker, handles = _linker(scripted.structured_json)
    (selection,) = linker.resolve(
        (("r1", "brüt gelir toplamı", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "BOUND"
    assert selection.mode == "LINKER"
    assert scripted.calls == 1
    request = scripted.last_user["requests"][0]
    assert request["surface"] == "brüt gelir toplamı"
    assert all(item["candidate_id"].startswith("cand_") for item in request["candidates"])
    assert not any("sales.gross_revenue" in json.dumps(item) for item in request["candidates"])

    handle = linker.bind_selection(selection, provenance_type="USER_SOURCE")
    binding = handles.binding_for_execution(
        handle.handle_id,
        tenant_binding="tenant-a",
        context_version="ctx-linker-v1",
    )
    assert binding.canonical_target.canonical_name == "sales.gross_revenue"


def test_model_cannot_select_candidate_outside_bounded_request_set():
    scripted = _Scripted(
        {
            "choices": [
                {
                    "request_id": "r1",
                    "decision": "SELECT",
                    "candidate_id": "cand_" + "f" * 24,
                    "reason": None,
                }
            ]
        }
    )
    linker, _ = _linker(scripted.structured_json)
    with pytest.raises(SemanticLinkAuthorityError, match="outside"):
        linker.resolve(
            (("r1", "brüt gelir toplamı", "metric"),),
            provenance_type="USER_SOURCE",
        )


def test_binding_gate_remains_tenant_and_context_bound():
    linker, handles = _linker(None)
    (selection,) = linker.resolve(
        (("r1", "net gelir", "metric"),),
        provenance_type="USER_SOURCE",
    )
    handle = linker.bind_selection(selection, provenance_type="USER_SOURCE")
    with pytest.raises(ValueError, match="foreign-tenant"):
        handles.validate(
            handle.handle_id,
            tenant_binding="tenant-b",
            context_version="ctx-linker-v1",
        )
    with pytest.raises(ValueError, match="stale-context"):
        handles.validate(
            handle.handle_id,
            tenant_binding="tenant-a",
            context_version="ctx-linker-v2",
        )


def test_sensitive_filter_value_is_exact_only_and_not_exposed_to_linker_fallback():
    context = BoundedSemanticContextV0(
        context_version=_context().context_version,
        cubes=(
            CompactCubeContextV0(
                canonical_name="people",
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="email",
                        display="E-posta",
                    ),
                ),
            ),
        ),
    )
    generator = SemanticCandidateGenerator(
        semantic_context=context,
        schema={
            "models": [
                {
                    "name": "people",
                    "columns": [{"name": "email", "type": "VARCHAR"}],
                }
            ],
            "cubes": [
                {
                    "name": "people",
                    "dimension_values": {"email": ["alice@example.com"]},
                }
            ],
        },
    )
    exact = generator.generate(
        request_id="r1",
        surface="alice@example.com",
        kind_hint="filter",
    )
    assert len(exact.bindings) == 1
    non_exact = generator.generate(
        request_id="r2",
        surface="alice",
        kind_hint="filter",
    )
    assert non_exact.bindings == ()


def test_semantic_linker_production_module_has_no_language_matching_heuristics():
    source = (
        Path(__file__).resolve().parents[1] / "app" / "v2" / "semantic_linker.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "SequenceMatcher",
        "SnowballStemmer",
        "_FUZZY",
        "from difflib import",
        "py_rust_stemmers",
        "import re",
        "re.search",
        "re.match",
        "re.compile",
    )
    for marker in forbidden:
        assert marker not in source


class _StaticRetriever:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def retrieve(self, *, surface, kind_hint, limit):
        self.calls.append((surface, kind_hint, limit))
        return self.result


def _retrieved_metric_binding():
    candidate_id = "cand_" + "a" * 24
    return CatalogCandidateBinding(
        card=SemanticLinkCandidateCard(
            candidate_id=candidate_id,
            target_kind="metric",
            label="Net Gelir",
            verified_aliases=("net gelir",),
            cube_labels=("Satış",),
        ),
        canonical_target=ResolvedSemanticRef(
            candidate_id=candidate_id,
            target_kind=SemanticTargetKind.METRIC,
            canonical_name="sales.net_revenue",
            cube_names=("sales",),
        ),
        exact_keys=frozenset({"net gelir"}),
    )


def test_candidate_generator_uses_explicit_non_authoritative_retriever_seam():
    retriever = _StaticRetriever(
        SemanticRetrievalResult(
            candidates=(_retrieved_metric_binding(),),
            exhaustive=False,
            backend="test_ranked_retriever",
        )
    )
    generator = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema=_schema(),
        retriever=retriever,
    )

    candidate_set = generator.generate(
        request_id="r1",
        surface="net gelir",
        kind_hint="metric",
    )

    assert retriever.calls == [("net gelir", "metric", 48)]
    assert candidate_set.retrieval_exhaustive is False
    assert candidate_set.retrieval_backend == "test_ranked_retriever"
    assert candidate_set.bindings[0].card.candidate_id == "cand_" + "a" * 24


def test_non_exhaustive_retrieval_miss_is_not_semantic_nonexistence():
    retriever = _StaticRetriever(
        SemanticRetrievalResult(
            candidates=(),
            exhaustive=False,
            backend="test_ranked_retriever",
        )
    )
    generator = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema=_schema(),
        retriever=retriever,
    )
    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-linker-v1",
        ),
        provider=None,
    )

    (selection,) = linker.resolve(
        (("r1", "unknown surface", "metric"),),
        provenance_type="USER_SOURCE",
    )

    assert selection.status == "RETRIEVAL_MISS"
    assert "existence unknown" in (selection.reason or "")
