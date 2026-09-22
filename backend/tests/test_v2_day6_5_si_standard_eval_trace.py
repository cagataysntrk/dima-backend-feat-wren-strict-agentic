from __future__ import annotations

from types import SimpleNamespace

from app.v2.manager_models import SemanticHandle
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
    SemanticBindingGate,
    SemanticCandidateGenerator,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
    StructuredSemanticCandidateDecisionProvider,
)
from lab.si_standard_eval import install_standard_eval_trace, new_case_trace


def _context():
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-trace",
            mdl_version="mdl-trace",
            compact_catalog_builder_version="trace-test",
            business_rules_hash="a" * 64,
            prompt_context_policy_version="trace-test",
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


class _Structured:
    def __init__(self):
        self.calls = []

    def __call__(self, system, user, *, schema, schema_name):
        import json

        payload = json.loads(user)
        self.calls.append(payload)
        request = payload["requests"][0]
        selected = next(
            candidate["candidate_id"]
            for candidate in request["candidates"]
            if "Orders" in candidate["cube_labels"]
        )
        return {
            "choices": [
                {
                    "request_id": request["request_id"],
                    "decision": "SELECT",
                    "candidate_id": selected,
                    "reason": None,
                }
            ]
        }


def _linker(structured):
    handles = SemanticHandleRegistry()
    generator = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="tenant-a",
            context_version="ctx-trace",
        ),
        provider=StructuredSemanticCandidateDecisionProvider(
            structured=structured
        ),
    )
    return linker, generator, handles


def _run(linker, generator):
    candidate_set = generator.generate(
        request_id="r1",
        surface="account code field",
        kind_hint="dimension",
        decision_context="show invoice total by account code",
    )
    (selection,) = linker.resolve(
        (("r1", "account code field", "dimension"),),
        provenance_type="USER_SOURCE",
        decision_context="show invoice total by account code",
    )
    return {
        "candidate_ids": tuple(
            item.card.candidate_id for item in candidate_set.bindings
        ),
        "backend": candidate_set.retrieval_backend,
        "exhaustive": candidate_set.retrieval_exhaustive,
        "truncated": candidate_set.retrieval_truncated,
        "selection_status": selection.status,
        "selection_id": (
            selection.binding.card.candidate_id
            if selection.binding is not None
            else None
        ),
    }


def test_eval_trace_is_semantically_transparent(monkeypatch):
    baseline_structured = _Structured()
    baseline_linker, baseline_generator, _ = _linker(baseline_structured)
    baseline = _run(baseline_linker, baseline_generator)

    traced_structured = _Structured()
    traced_linker, traced_generator, _ = _linker(traced_structured)

    harness = SimpleNamespace(
        _engine=SimpleNamespace(
            _draft=lambda *args, **kwargs: SimpleNamespace(
                obligations=(),
                control_requests=(),
            )
        )
    )
    trace = new_case_trace(
        {
            "id": "trace-parity",
            "family": "trace",
            "question": "show invoice total by account code",
        }
    )
    trace_ref = {"current": trace}
    install_standard_eval_trace(monkeypatch, harness, trace_ref)

    traced = _run(traced_linker, traced_generator)

    assert traced == baseline
    assert traced_structured.calls == baseline_structured.calls
    assert trace["candidate_retrieval"]
    observed = trace["candidate_retrieval"][0]
    assert tuple(observed["visible_candidate_ids"]) == baseline["candidate_ids"]
    assert observed["backend"] == baseline["backend"]
    assert observed["exhaustive"] == baseline["exhaustive"]
    assert observed["truncated"] == baseline["truncated"]
    assert observed["decision_context_present"] is True


def test_eval_generate_proxy_forwards_future_optional_kwargs(monkeypatch):
    observed = {}

    def future_generate(self, *args, **kwargs):
        from app.v2.semantic_linker import CandidateSet

        observed["args"] = args
        observed["kwargs"] = dict(kwargs)
        return CandidateSet(
            request_id=kwargs["request_id"],
            surface=kwargs["surface"],
            kind_hint=kwargs["kind_hint"],
            bindings=(),
            retrieval_exhaustive=False,
            retrieval_backend="future-test",
            retrieval_truncated=False,
        )

    monkeypatch.setattr(
        SemanticCandidateGenerator,
        "generate",
        future_generate,
    )

    generator = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
    )
    harness = SimpleNamespace(
        _engine=SimpleNamespace(
            _draft=lambda *args, **kwargs: SimpleNamespace(
                obligations=(),
                control_requests=(),
            )
        )
    )
    trace_ref = {
        "current": new_case_trace(
            {"id": "future", "family": "trace", "question": "q"}
        )
    }
    install_standard_eval_trace(monkeypatch, harness, trace_ref)

    result = generator.generate(
        request_id="future-r",
        surface="future surface",
        kind_hint="metric",
        decision_context="context",
        future_optional="kept",
    )

    assert result.retrieval_backend == "future-test"
    assert observed["kwargs"]["decision_context"] == "context"
    assert observed["kwargs"]["future_optional"] == "kept"


def test_nested_retriever_proxy_forwards_all_kwargs(monkeypatch):
    from app.v2.semantic_linker import CandidateSet
    from app.v2.semantic_retriever import SemanticRetrievalResult

    retriever_seen = {}

    class _FutureRetriever:
        def retrieve(self, *args, **kwargs):
            retriever_seen.update(kwargs)
            return SemanticRetrievalResult(
                candidates=(),
                exhaustive=False,
                backend="future-retriever",
                truncated=False,
            )

    def future_generate(self, *args, **kwargs):
        result = self._retriever.retrieve(
            surface=kwargs["surface"],
            kind_hint=kwargs["kind_hint"],
            limit=48,
            decision_context=kwargs.get("decision_context"),
            future_retriever_flag="preserved",
        )
        return CandidateSet(
            request_id=kwargs["request_id"],
            surface=kwargs["surface"],
            kind_hint=kwargs["kind_hint"],
            bindings=(),
            retrieval_exhaustive=result.exhaustive,
            retrieval_backend=result.backend,
            retrieval_truncated=result.truncated,
        )

    monkeypatch.setattr(
        SemanticCandidateGenerator,
        "generate",
        future_generate,
    )

    generator = SemanticCandidateGenerator(
        semantic_context=_context(),
        schema={"models": [], "cubes": [], "company_vocabulary": []},
        retriever=_FutureRetriever(),
    )
    harness = SimpleNamespace(
        _engine=SimpleNamespace(
            _draft=lambda *args, **kwargs: SimpleNamespace(
                obligations=(),
                control_requests=(),
            )
        )
    )
    trace_ref = {
        "current": new_case_trace(
            {"id": "nested-future", "family": "trace", "question": "q"}
        )
    }
    install_standard_eval_trace(monkeypatch, harness, trace_ref)

    generator.generate(
        request_id="future-r",
        surface="future surface",
        kind_hint="metric",
        decision_context="context",
    )

    assert retriever_seen["decision_context"] == "context"
    assert retriever_seen["future_retriever_flag"] == "preserved"
