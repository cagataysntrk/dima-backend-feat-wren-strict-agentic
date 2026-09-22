"""Eval-only trace helpers for the Day6.5 Standard SI gate.

These helpers observe existing cognition/retrieval/linker calls without altering product
semantics. They never mint authority and never expose sensitive entity values.
"""

from __future__ import annotations

from typing import Any

from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    SemanticCandidateGenerator,
    StructuredSemanticCandidateDecisionProvider,
    _exact_key,
)


def _safe_candidate(item) -> dict[str, Any]:
    card = item.card
    out: dict[str, Any] = {
        "candidate_id": card.candidate_id,
        "target_kind": card.target_kind,
        "sensitive": bool(getattr(item, "sensitive", False)),
    }
    if out["sensitive"]:
        return out
    target = item.canonical_target
    out["canonical_name"] = getattr(target, "canonical_name", None)
    out["dimension_name"] = getattr(target, "dimension_name", None)
    out["cube_refs"] = list(getattr(target, "cube_names", ()) or ())
    return out


def draft_summary(draft) -> dict[str, Any]:
    return {
        "obligations": [
            {
                "obligation_id": item.obligation_id,
                "capability_key": item.capability_key.value,
                "origin": item.origin,
                "priority": item.priority.value,
                "polarity": item.polarity.value,
                "source_surfaces": list(item.source_surfaces),
                "semantic_surfaces": [
                    {
                        "surface": semantic.surface,
                        "kind_hint": semantic.kind_hint,
                    }
                    for semantic in item.semantic_surfaces
                ],
                "ranking_direction": item.ranking_direction,
                "ranking_limit": item.ranking_limit,
            }
            for item in draft.obligations
        ],
        "control_requests": [
            {
                "request_id": item.request_id,
                "source_surfaces": list(item.source_surfaces),
            }
            for item in draft.control_requests
        ],
    }


def install_standard_eval_trace(monkeypatch, harness, trace_ref: dict[str, Any]) -> None:
    """Observe one workers=1 harness with a mutable trace_ref['current'] target."""

    original_draft = harness._engine._draft

    def traced_draft(**kwargs):
        draft = original_draft(**kwargs)
        current = trace_ref.get("current")
        if current is not None:
            current.setdefault("draft_attempts", []).append(draft_summary(draft))
        return draft

    monkeypatch.setattr(harness._engine, "_draft", traced_draft)

    original_generate = SemanticCandidateGenerator.generate

    def traced_generate(self, *, request_id, surface, kind_hint):
        current = trace_ref.get("current")
        captured: dict[str, Any] = {}
        original_retriever = self._retriever

        class _CapturingRetriever:
            def retrieve(inner_self, *, surface, kind_hint, limit):
                result = original_retriever.retrieve(
                    surface=surface,
                    kind_hint=kind_hint,
                    limit=limit,
                )
                captured["retrieval"] = result
                return result

        self._retriever = _CapturingRetriever()
        try:
            candidate_set = original_generate(
                self,
                request_id=request_id,
                surface=surface,
                kind_hint=kind_hint,
            )
        finally:
            self._retriever = original_retriever

        if current is not None:
            retrieval = captured.get("retrieval")
            raw = tuple(getattr(retrieval, "candidates", ()) or ())
            exact = [
                item
                for item in raw
                if _exact_key(surface) in item.exact_keys
            ]
            current.setdefault("candidate_retrieval", []).append(
                {
                    "request_id": request_id,
                    "surface": surface,
                    "kind_hint": kind_hint,
                    "backend": (
                        retrieval.backend
                        if retrieval is not None
                        else candidate_set.retrieval_backend
                    ),
                    "exhaustive": (
                        bool(retrieval.exhaustive)
                        if retrieval is not None
                        else candidate_set.retrieval_exhaustive
                    ),
                    "truncated": (
                        bool(retrieval.truncated)
                        if retrieval is not None
                        else False
                    ),
                    "candidate_count_before_bound": len(raw),
                    "visible_candidate_count": len(candidate_set.bindings),
                    "exact_candidate_count": len(exact),
                    "exact_candidates": [
                        _safe_candidate(item) for item in exact
                    ],
                    "too_broad": candidate_set.too_broad,
                }
            )
        return candidate_set

    monkeypatch.setattr(SemanticCandidateGenerator, "generate", traced_generate)

    original_resolve = BoundedSemanticLinker.resolve

    def traced_resolve(self, requests, **kwargs):
        selections = original_resolve(self, requests, **kwargs)
        current = trace_ref.get("current")
        if current is not None:
            current.setdefault("semantic_selections", []).extend(
                {
                    "request_id": item.request_id,
                    "surface": item.surface,
                    "status": item.status,
                    "mode": item.mode,
                    "reason": item.reason,
                    "selected_candidate": (
                        _safe_candidate(item.binding)
                        if item.binding is not None
                        else None
                    ),
                }
                for item in selections
            )
        return selections

    monkeypatch.setattr(BoundedSemanticLinker, "resolve", traced_resolve)

    original_decide = StructuredSemanticCandidateDecisionProvider.decide

    def traced_decide(self, requests):
        current = trace_ref.get("current")
        if current is not None:
            current["semantic_provider_called"] = True
            current.setdefault("semantic_provider_requests", []).extend(
                {
                    "request_id": item.request_id,
                    "surface": item.surface,
                    "kind_hint": item.kind_hint,
                    "candidate_count": len(item.candidates),
                }
                for item in requests
            )
        try:
            decision = original_decide(self, requests)
        except Exception as exc:
            if current is not None:
                current["semantic_provider_error"] = (
                    f"{type(exc).__name__}: {exc}"
                )
            raise
        if current is not None:
            current.setdefault("semantic_provider_choices", []).extend(
                item.model_dump(mode="json") for item in decision.choices
            )
        return decision

    monkeypatch.setattr(
        StructuredSemanticCandidateDecisionProvider,
        "decide",
        traced_decide,
    )


def new_case_trace(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["id"],
        "family": case["family"],
        "question": case["question"],
        "draft_attempts": [],
        "candidate_retrieval": [],
        "semantic_selections": [],
        "semantic_provider_called": False,
        "semantic_provider_requests": [],
        "semantic_provider_choices": [],
    }
