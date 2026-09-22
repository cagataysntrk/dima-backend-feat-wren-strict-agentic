"""Non-authoritative semantic catalog discovery seam for Day 6.5.

A retriever may narrow which verified catalog candidates are shown to cognition, but it
never creates canonical truth or SemanticHandle authority. Retrieval miss is not proof
that a semantic concept does not exist.
"""

from __future__ import annotations

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
    ) -> SemanticRetrievalResult[T]:
        ...


@dataclass(frozen=True)
class EnumeratingSemanticCatalogRetriever(Generic[T]):
    """Current Day 6.5 backend: enumerate the governed catalog exhaustively.

    surface and limit are accepted so future ranked/indexed implementations can share
    this interface. This backend intentionally ignores both and returns the full verified
    catalog slice. Bounded presentation remains the candidate generator responsibility.
    """

    enumerate_candidates: Callable[[str], Sequence[T]]
    backend: str = "deterministic_enumeration_v1"

    def retrieve(
        self,
        *,
        surface: str,
        kind_hint: str,
        limit: int,
    ) -> SemanticRetrievalResult[T]:
        del surface, limit
        return SemanticRetrievalResult(
            candidates=tuple(self.enumerate_candidates(kind_hint)),
            exhaustive=True,
            backend=self.backend,
            truncated=False,
        )
