"""Non-authoritative semantic catalog discovery seam for Day 6.5.

A retriever may narrow which verified catalog candidates are shown to cognition, but it
never creates canonical truth or SemanticHandle authority. Retrieval miss is not proof
that a semantic concept does not exist.

The default indexed backend uses only exact normalized tokens/phrases from governed
catalog metadata. It performs no stemming, fuzzy ratio, morphology, regex language rule,
or semantic auto-selection.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Callable, Generic, Protocol, Sequence, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SemanticRetrievalResult(Generic[T]):
    """Candidate discovery result with explicit completeness semantics."""

    candidates: tuple[T, ...]
    exhaustive: bool
    backend: str
    truncated: bool = False


class SemanticCatalogRetriever(Protocol[T]):
    """Discovery-only interface; canonical authority remains outside this boundary."""

    def retrieve(
        self,
        *,
        surface: str,
        kind_hint: str,
        limit: int,
        decision_context: str | None = None,
    ) -> SemanticRetrievalResult[T]:
        ...


class SemanticRetrievalContractError(RuntimeError):
    """Retriever output violated the governed-catalog discovery contract."""


@dataclass(frozen=True)
class SemanticDiscoveryDocument:
    """Governed metadata used only for candidate discovery.

    exact_terms preserve identity/alias ambiguity.
    primary_terms describe the candidate itself.
    context_terms provide verified surrounding catalog context.
    discoverable=False removes an item from non-exact ranked discovery while exact
    user-supplied identity may still match through exact_terms.
    """

    stable_id: str
    exact_terms: tuple[str, ...] = ()
    primary_terms: tuple[str, ...] = ()
    context_terms: tuple[str, ...] = ()
    discoverable: bool = True


def _normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "").strip().casefold())
    chars: list[str] = []
    for ch in value:
        if unicodedata.combining(ch):
            continue
        chars.append(ch if ch.isalnum() else " ")
    return " ".join("".join(chars).split())


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(_normalized_text(value).split()))


@dataclass(frozen=True)
class _IndexedCandidate(Generic[T]):
    item: T
    document: SemanticDiscoveryDocument
    primary_norm: tuple[str, ...]
    context_norm: tuple[str, ...]
    primary_tokens: frozenset[str]
    context_tokens: frozenset[str]


@dataclass(frozen=True)
class _KindIndex(Generic[T]):
    entries: tuple[_IndexedCandidate[T], ...]
    exact: dict[str, tuple[int, ...]]
    postings: dict[str, tuple[int, ...]]


class IndexedTokenSemanticCatalogRetriever(Generic[T]):
    """Lazy governed token index with bounded ranked output.

    The index scans governed metadata when built, then candidate discovery is driven by
    exact token postings. Ranking is discovery-only; no score can mint authority.
    """

    def __init__(
        self,
        *,
        enumerate_candidates: Callable[[str], Sequence[T]],
        document_for: Callable[[T], SemanticDiscoveryDocument],
        backend: str = "governed_token_index_v1",
    ) -> None:
        self._enumerate_candidates = enumerate_candidates
        self._document_for = document_for
        self._backend = backend
        self._by_kind: dict[str, _KindIndex[T]] = {}

    def _build(self, kind_hint: str) -> _KindIndex[T]:
        cached = self._by_kind.get(kind_hint)
        if cached is not None:
            return cached

        entries: list[_IndexedCandidate[T]] = []
        exact: dict[str, list[int]] = {}
        postings: dict[str, list[int]] = {}

        for item in self._enumerate_candidates(kind_hint):
            doc = self._document_for(item)
            primary_norm = tuple(
                value
                for value in (
                    _normalized_text(term) for term in doc.primary_terms
                )
                if value
            )
            context_norm = tuple(
                value
                for value in (
                    _normalized_text(term) for term in doc.context_terms
                )
                if value
            )
            entry = _IndexedCandidate(
                item=item,
                document=doc,
                primary_norm=primary_norm,
                context_norm=context_norm,
                primary_tokens=frozenset(
                    token
                    for term in primary_norm
                    for token in term.split()
                ),
                context_tokens=frozenset(
                    token
                    for term in context_norm
                    for token in term.split()
                ),
            )
            idx = len(entries)
            entries.append(entry)

            for term in doc.exact_terms:
                key = _normalized_text(term)
                if key:
                    exact.setdefault(key, []).append(idx)

            if doc.discoverable:
                for token in entry.primary_tokens | entry.context_tokens:
                    postings.setdefault(token, []).append(idx)

        built = _KindIndex(
            entries=tuple(entries),
            exact={key: tuple(value) for key, value in exact.items()},
            postings={key: tuple(value) for key, value in postings.items()},
        )
        self._by_kind[kind_hint] = built
        return built

    @staticmethod
    def _term_score(
        *,
        surface_norm: str,
        query_tokens: frozenset[str],
        terms: tuple[str, ...],
        tokens: frozenset[str],
    ) -> tuple[int, int, int]:
        phrase = max(
            (
                len(term.split())
                for term in terms
                if term and term in surface_norm
            ),
            default=0,
        )
        overlap = query_tokens & tokens
        return (
            phrase,
            len(overlap),
            sum(len(token) for token in overlap),
        )

    def retrieve(
        self,
        *,
        surface: str,
        kind_hint: str,
        limit: int,
        decision_context: str | None = None,
    ) -> SemanticRetrievalResult[T]:
        index = self._build(kind_hint)
        surface_norm = _normalized_text(surface)
        if not surface_norm:
            return SemanticRetrievalResult(
                candidates=(),
                exhaustive=False,
                backend=self._backend,
                truncated=False,
            )

        exact_ids = index.exact.get(surface_norm, ())
        if exact_ids:
            # All exact aliases are preserved even when there are multiple matches.
            # They terminate as exact ambiguity before any model call.
            return SemanticRetrievalResult(
                candidates=tuple(index.entries[idx].item for idx in exact_ids),
                exhaustive=True,
                backend=self._backend,
                truncated=False,
            )

        query_tokens = frozenset(_tokens(surface_norm))
        decision_norm = _normalized_text(decision_context or "")
        decision_tokens = frozenset(_tokens(decision_norm))

        candidate_ids: set[int] = set()
        for token in query_tokens | decision_tokens:
            candidate_ids.update(index.postings.get(token, ()))

        scored: list[tuple[tuple[int, ...], str, T]] = []
        for idx in candidate_ids:
            entry = index.entries[idx]
            local_primary = self._term_score(
                surface_norm=surface_norm,
                query_tokens=query_tokens,
                terms=entry.primary_norm,
                tokens=entry.primary_tokens,
            )
            decision_primary = self._term_score(
                surface_norm=decision_norm,
                query_tokens=decision_tokens,
                terms=entry.primary_norm,
                tokens=entry.primary_tokens,
            )
            decision_catalog_context = self._term_score(
                surface_norm=decision_norm,
                query_tokens=decision_tokens,
                terms=entry.context_norm,
                tokens=entry.context_tokens,
            )
            local_catalog_context = self._term_score(
                surface_norm=surface_norm,
                query_tokens=query_tokens,
                terms=entry.context_norm,
                tokens=entry.context_tokens,
            )
            # Local semantic surface is always primary evidence. Full source context
            # breaks ties and improves discovery only; it cannot create or bind candidates.
            score = (
                *local_primary,
                *decision_primary,
                *decision_catalog_context,
                *local_catalog_context,
            )
            if not any(score):
                continue
            scored.append((score, entry.document.stable_id, entry.item))

        # Numeric score descending; stable governed id ascending breaks ties so
        # catalog enumeration order/growth does not become semantic behavior.
        scored.sort(key=lambda row: row[1])
        scored.sort(key=lambda row: row[0], reverse=True)

        bounded = scored[: max(1, int(limit))]
        return SemanticRetrievalResult(
            candidates=tuple(row[2] for row in bounded),
            exhaustive=False,
            backend=self._backend,
            truncated=len(scored) > len(bounded),
        )


@dataclass(frozen=True)
class EnumeratingSemanticCatalogRetriever(Generic[T]):
    """Historical exhaustive backend retained for explicit tests/diagnostics only."""

    enumerate_candidates: Callable[[str], Sequence[T]]
    backend: str = "deterministic_enumeration_v1"

    def retrieve(
        self,
        *,
        surface: str,
        kind_hint: str,
        limit: int,
    ) -> SemanticRetrievalResult[T]:
        del surface, limit, decision_context
        return SemanticRetrievalResult(
            candidates=tuple(self.enumerate_candidates(kind_hint)),
            exhaustive=True,
            backend=self.backend,
            truncated=False,
        )
