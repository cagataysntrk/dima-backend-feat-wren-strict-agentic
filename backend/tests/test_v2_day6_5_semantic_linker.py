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
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    StructuredSemanticCandidateDecisionProvider,
    SemanticLinkAuthorityError,
    SemanticLinkCandidateCard,
)
from app.v2.semantic_retriever import (
    SemanticRetrievalContractError,
    SemanticRetrievalResult,
)


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

    def retrieve(
        self,
        *,
        surface,
        kind_hint,
        limit,
        decision_context=None,
    ):
        self.calls.append((surface, kind_hint, limit, decision_context))
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
    baseline = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema=_schema(),
    )
    governed = next(
        item
        for item in baseline._governed_candidates("metric")
        if item.card.label == "Net Gelir"
    )
    retriever = _StaticRetriever(
        SemanticRetrievalResult(
            candidates=(governed,),
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

    assert retriever.calls == [("net gelir", "metric", 48, None)]
    assert candidate_set.retrieval_exhaustive is False
    assert candidate_set.retrieval_backend == "test_ranked_retriever"
    assert candidate_set.bindings[0].card.candidate_id == governed.card.candidate_id


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



def _large_context(*, noise_count=100, reverse=False):
    noise = [
        CompactSemanticFieldV0(
            canonical_name=f"receivables.noise_{index:03d}",
            display=f"Noise Metric {index:03d}",
            synonyms=(f"noise metric {index:03d}",),
        )
        for index in range(noise_count)
    ]
    target = CompactSemanticFieldV0(
        canonical_name="receivables.target_balance",
        display="Target Balance",
        synonyms=("target balance",),
    )
    metrics = [*noise, target]
    if reverse:
        metrics = list(reversed(metrics))
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-large",
            mdl_version="mdl-large",
            compact_catalog_builder_version="large-test",
            business_rules_hash="2" * 64,
            prompt_context_policy_version="large-test",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="receivables",
                display="Receivables",
                synonyms=("receivable accounts",),
                measures=tuple(metrics),
            ),
            CompactCubeContextV0(
                canonical_name="ledger",
                display="General Ledger",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="ledger.target_balance",
                        display="Target Balance",
                        synonyms=("target balance",),
                    ),
                ),
            ),
        ),
    )


def _large_generator(*, noise_count=100, reverse=False):
    return SemanticCandidateGenerator(
        semantic_context=_large_context(
            noise_count=noise_count,
            reverse=reverse,
        ),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
        max_candidates=48,
    )


def test_large_catalog_non_exact_discovery_is_bounded_before_linker():
    generator = _large_generator(noise_count=130)
    candidate_set = generator.generate(
        request_id="large-1",
        surface="show overdue receivables target balance",
        kind_hint="metric",
    )
    canonical = {
        item.canonical_target.canonical_name
        for item in candidate_set.bindings
    }

    assert candidate_set.retrieval_backend == "governed_token_index_v1"
    assert candidate_set.retrieval_exhaustive is False
    assert candidate_set.too_broad is False
    assert len(candidate_set.bindings) <= 48
    assert "receivables.target_balance" in canonical


def test_relevant_candidate_after_enumeration_position_48_is_retrieved():
    generator = _large_generator(noise_count=100)
    governed = generator._governed_candidates("metric")
    target_position = next(
        index
        for index, item in enumerate(governed)
        if item.canonical_target.canonical_name == "receivables.target_balance"
    )
    assert target_position > 48

    candidate_set = generator.generate(
        request_id="large-2",
        surface="receivables target balance overview",
        kind_hint="metric",
    )
    assert any(
        item.canonical_target.canonical_name == "receivables.target_balance"
        for item in candidate_set.bindings
    )


def test_duplicate_exact_aliases_remain_ambiguity_after_indexing():
    generator = _large_generator(noise_count=100)
    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-large",
        ),
        provider=None,
    )
    (selection,) = linker.resolve(
        (("large-3", "target balance", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "AMBIGUOUS_EXACT"
    assert selection.binding is None


def test_ranked_discovery_winner_never_auto_mints_authority():
    generator = _large_generator(noise_count=100)
    candidate_set = generator.generate(
        request_id="large-4",
        surface="receivables target balance overview",
        kind_hint="metric",
    )
    assert candidate_set.bindings
    assert candidate_set.bindings[0].canonical_target.canonical_name == (
        "receivables.target_balance"
    )

    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-large",
        ),
        provider=None,
    )
    (selection,) = linker.resolve(
        (("large-4", "receivables target balance overview", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "LINKER_UNAVAILABLE"
    assert selection.binding is None


def test_ranked_non_exhaustive_no_hit_is_retrieval_miss():
    generator = _large_generator(noise_count=100)
    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-large",
        ),
        provider=None,
    )
    (selection,) = linker.resolve(
        (("large-5", "quasar nebula unrelated phrase", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "RETRIEVAL_MISS"


def test_retriever_cannot_inject_foreign_or_stale_candidate_body():
    foreign_context = _large_context(noise_count=0).model_copy(
        update={
            "context_version": ContextVersionV0(
                version="ctx-foreign",
                mdl_version="mdl-foreign",
                compact_catalog_builder_version="foreign-test",
                business_rules_hash="3" * 64,
                prompt_context_policy_version="foreign-test",
            )
        }
    )
    foreign_generator = SemanticCandidateGenerator(
        semantic_context=foreign_context,
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    foreign = foreign_generator._governed_candidates("metric")[0]
    retriever = _StaticRetriever(
        SemanticRetrievalResult(
            candidates=(foreign,),
            exhaustive=False,
            backend="foreign-index",
        )
    )
    local = SemanticCandidateGenerator(
        semantic_context=_large_context(noise_count=0),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
        retriever=retriever,
    )
    with pytest.raises(SemanticRetrievalContractError, match="governed catalog"):
        local.generate(
            request_id="large-6",
            surface="target",
            kind_hint="metric",
        )


class _SelectReceivables:
    def decide(self, requests):
        choices = []
        for request in requests:
            selected = next(
                card.candidate_id
                for card in request.candidates
                if "Receivables" in card.cube_labels
            )
            choices.append(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=selected,
                )
            )
        return SemanticLinkBatchDecision(choices=tuple(choices))


def _resolve_large(*, noise_count, reverse=False):
    generator = _large_generator(
        noise_count=noise_count,
        reverse=reverse,
    )
    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-large",
        ),
        provider=_SelectReceivables(),
    )
    (selection,) = linker.resolve(
        (("meta-1", "receivables target balance overview", "metric"),),
        provenance_type="USER_SOURCE",
    )
    assert selection.status == "BOUND"
    return selection.binding.canonical_target.canonical_name


def test_catalog_growth_and_order_do_not_change_bounded_semantic_outcome():
    small = _resolve_large(noise_count=5, reverse=False)
    grown = _resolve_large(noise_count=105, reverse=True)
    assert small == grown == "receivables.target_balance"


def test_sensitive_values_stay_out_of_ranked_token_index():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-sensitive-index",
            mdl_version="mdl-sensitive-index",
            compact_catalog_builder_version="sensitive-index-test",
            business_rules_hash="4" * 64,
            prompt_context_policy_version="sensitive-index-test",
        ),
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
                    "dimension_values": {"email": ["secret.person@example.com"]},
                }
            ],
        },
    )
    non_exact = generator.generate(
        request_id="sensitive-ranked",
        surface="secret person",
        kind_hint="filter",
    )
    assert non_exact.bindings == ()


def test_ranked_retriever_module_has_no_fuzzy_morphology_or_regex_authority():
    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "v2"
        / "semantic_retriever.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "SequenceMatcher",
        "SnowballStemmer",
        "py_rust_stemmers",
        "import re",
        "re.search",
        "re.match",
        "re.compile",
    )
    for marker in forbidden:
        assert marker not in source



def _two_cube_same_dimension_context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-contextual",
            mdl_version="mdl-contextual",
            compact_catalog_builder_version="contextual-test",
            business_rules_hash="5" * 64,
            prompt_context_policy_version="contextual-test",
        ),
        cubes=(
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
        ),
    )


class _SelectOrdersFromContext:
    def __init__(self):
        self.requests = ()

    def decide(self, requests):
        self.requests = requests
        choices = []
        for request in requests:
            assert request.source_context is not None
            target = next(
                card.candidate_id
                for card in request.candidates
                if "Orders" in card.cube_labels
            )
            choices.append(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=target,
                )
            )
        return SemanticLinkBatchDecision(choices=tuple(choices))


def test_source_context_disambiguates_only_inside_bounded_candidate_set():
    provider = _SelectOrdersFromContext()
    handles = SemanticHandleRegistry()
    generator = SemanticCandidateGenerator(
        semantic_context=_two_cube_same_dimension_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-contextual",
        ),
        provider=provider,
    )

    (selection,) = linker.resolve(
        (("ctx-1", "account code field", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="show top accounts by invoice total and account code",
    )

    assert selection.status == "BOUND"
    assert selection.binding is not None
    assert selection.binding.canonical_target.canonical_name == (
        "orders.account_code"
    )
    assert provider.requests[0].source_context == (
        "show top accounts by invoice total and account code"
    )
    supplied = {
        card.candidate_id for card in provider.requests[0].candidates
    }
    assert selection.binding.card.candidate_id in supplied


def test_source_context_does_not_auto_bind_without_linker_authority():
    generator = SemanticCandidateGenerator(
        semantic_context=_two_cube_same_dimension_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    handles = SemanticHandleRegistry()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-contextual",
        ),
        provider=None,
    )

    (selection,) = linker.resolve(
        (("ctx-2", "account code field", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="invoice total account code",
    )
    assert selection.status == "LINKER_UNAVAILABLE"
    assert selection.binding is None


def test_exact_duplicate_alias_stays_ambiguous_even_with_source_context():
    generator = SemanticCandidateGenerator(
        semantic_context=_two_cube_same_dimension_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    handles = SemanticHandleRegistry()
    provider = _SelectOrdersFromContext()
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-contextual",
        ),
        provider=provider,
    )

    (selection,) = linker.resolve(
        (("ctx-3", "account code", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="invoice total account code",
    )
    assert selection.status == "AMBIGUOUS_EXACT"
    assert selection.binding is None
    assert provider.requests == ()


def test_decision_context_cannot_retrieve_candidate_outside_governed_catalog():
    generator = SemanticCandidateGenerator(
        semantic_context=_two_cube_same_dimension_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    candidate_set = generator.generate(
        request_id="ctx-4",
        surface="account code field",
        kind_hint="dimension",
        decision_context="invented nonexistent warehouse concept",
    )
    governed = {
        item.card.candidate_id
        for item in generator._governed_candidates("dimension")
    }
    assert {
        item.card.candidate_id for item in candidate_set.bindings
    } <= governed
