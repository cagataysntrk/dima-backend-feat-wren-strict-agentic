"""Day7 LAB ONLY: governed sibling-scope semantic discovery bake-off.

This module is deliberately outside the product semantic path.  It tests one hypothesis:

    already-bound sibling authority
      -> bounded governed cube scope
      -> candidate DISCOVERY only
      -> bounded semantic cognition
      -> existing SemanticBindingGate authority

It never strips suffixes, stems words, fuzzily matches text, creates aliases, invents
relationships, or mints authority from cube membership.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.v2.context_provider import ContextProviderV0
from app.v2.manager_models import SemanticHandle
from app.v2.models import TenantAnalyticsRuntimeV0
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    CandidateSet,
    CatalogCandidateBinding,
    SemanticBindingGate,
    SemanticCandidateGenerator,
)
from lab.v2_day7_manager_live_sol import Day7LiveSyntheticService, MDL_VERSION


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT / "lab" / "reports" / "v2_day7_governed_sibling_scope_discovery.json"
)
DEFAULT_MAX_CANDIDATES = 48


@dataclass(frozen=True)
class ScopedDiscoveryReceipt:
    surface: str
    kind_hint: str
    sibling_surface: str | None
    sibling_cube_names: tuple[str, ...]
    baseline_backend: str
    baseline_candidate_count: int
    fallback_used: bool
    scoped_candidate_count_before_bound: int
    scoped_candidate_count_visible: int
    candidate_ids: tuple[str, ...]
    candidate_canonical_names: tuple[str, ...]
    outside_scope_count: int
    too_broad: bool
    retrieval_truncated: bool


def _target_cube_names(binding: CatalogCandidateBinding) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            str(value)
            for value in tuple(getattr(binding.canonical_target, "cube_names", ()) or ())
            if str(value)
        )
    )


def _canonical_name(binding: CatalogCandidateBinding) -> str:
    target = binding.canonical_target
    value = getattr(target, "canonical_name", None)
    if value is None:
        value = getattr(target, "dimension_name", None)
    return str(value or "")


class GovernedSiblingScopeCandidateGenerator:
    """LAB wrapper that widens only discovery after a real retrieval miss.

    The wrapped product generator remains the source of current governed candidate
    bindings.  This wrapper never interprets the unresolved surface.  It only filters
    current candidate truth by an already-resolved sibling's governed cube scope.
    """

    def __init__(
        self,
        *,
        base: SemanticCandidateGenerator,
        sibling_cube_names: Iterable[str],
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> None:
        self._base = base
        self._scope = frozenset(str(value) for value in sibling_cube_names if str(value))
        self._max_candidates = max(1, int(max_candidates))

    @property
    def scope(self) -> tuple[str, ...]:
        return tuple(sorted(self._scope))

    def _scoped_bindings(self, kind_hint: str) -> tuple[CatalogCandidateBinding, ...]:
        if not self._scope:
            return ()
        out = []
        for item in self._base._governed_candidates(kind_hint):
            if item.sensitive or not item.card.verified_aliases:
                continue
            if self._scope.intersection(_target_cube_names(item)):
                out.append(item)
        # Candidate ids are stable governed ids; sort only for reproducible lab output.
        out.sort(key=lambda item: item.card.candidate_id)
        return tuple(out)

    def generate(
        self,
        *,
        request_id: str,
        surface: str,
        kind_hint: str,
        decision_context: str | None = None,
    ) -> CandidateSet:
        baseline = self._base.generate(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            decision_context=decision_context,
        )
        # Fallback is strictly retrieval-miss only.  Exact, ambiguous, broad or any
        # already-visible product candidate set keeps the product discovery result.
        if baseline.bindings or baseline.too_broad or baseline.retrieval_exhaustive:
            return baseline
        if not self._scope:
            return baseline

        scoped = self._scoped_bindings(kind_hint)
        too_broad = len(scoped) > self._max_candidates
        visible = scoped[: self._max_candidates]
        return CandidateSet(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            bindings=visible,
            too_broad=too_broad,
            # Exhaustive only inside the sibling hint, never globally.
            retrieval_exhaustive=False,
            retrieval_backend="lab_governed_sibling_scope_v1",
            retrieval_truncated=too_broad,
        )

    def receipt(
        self,
        *,
        request_id: str,
        surface: str,
        kind_hint: str,
        decision_context: str | None = None,
        sibling_surface: str | None = None,
    ) -> ScopedDiscoveryReceipt:
        baseline = self._base.generate(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            decision_context=decision_context,
        )
        scoped_all = self._scoped_bindings(kind_hint) if not baseline.bindings else ()
        result = self.generate(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            decision_context=decision_context,
        )
        outside = [
            item
            for item in result.bindings
            if not self._scope.intersection(_target_cube_names(item))
        ]
        return ScopedDiscoveryReceipt(
            surface=surface,
            kind_hint=kind_hint,
            sibling_surface=sibling_surface,
            sibling_cube_names=self.scope,
            baseline_backend=baseline.retrieval_backend,
            baseline_candidate_count=len(baseline.bindings),
            fallback_used=(
                result.retrieval_backend == "lab_governed_sibling_scope_v1"
            ),
            scoped_candidate_count_before_bound=len(scoped_all),
            scoped_candidate_count_visible=len(result.bindings),
            candidate_ids=tuple(item.card.candidate_id for item in result.bindings),
            candidate_canonical_names=tuple(
                _canonical_name(item) for item in result.bindings
            ),
            outside_scope_count=len(outside),
            too_broad=result.too_broad,
            retrieval_truncated=result.retrieval_truncated,
        )


def _context():
    service = Day7LiveSyntheticService()
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id="day7-sibling-scope-lab",
        tenant_slug="day7-sibling-scope-lab",
        principal_user_id="diagnostic",
        roles=("owner",),
        mdl_version=MDL_VERSION,
        catalog="day7-live-synthetic",
        schema_name="main",
        db_online=True,
    )
    context = ContextProviderV0().build(service, runtime)
    return service, context


def _bind_exact_sibling(
    *,
    generator: SemanticCandidateGenerator,
    handles: SemanticHandleRegistry,
    context_version: str,
    surface: str,
    kind_hint: str,
    decision_context: str,
) -> tuple[SemanticHandle, tuple[str, ...]]:
    linker = BoundedSemanticLinker(
        generator=generator,
        binding_gate=SemanticBindingGate(
            semantic_handles=handles,
            tenant_binding="id:day7-sibling-scope-lab",
            context_version=context_version,
        ),
        provider=None,
    )
    selection = linker.resolve(
        (("sibling", surface, kind_hint),),
        provenance_type="USER_SOURCE",
        decision_context=decision_context,
    )[0]
    if selection.status != "BOUND" or selection.mode != "EXACT":
        raise RuntimeError(
            f"sibling must already be governed exact authority: {surface!r} -> "
            f"{selection.status}/{selection.mode}"
        )
    handle = linker.bind_selection(selection, provenance_type="USER_SOURCE")
    binding = handles.binding_for_execution(
        handle.handle_id,
        tenant_binding="id:day7-sibling-scope-lab",
        context_version=context_version,
    )
    cubes = tuple(getattr(binding.canonical_target, "cube_names", ()) or ())
    if not cubes:
        raise RuntimeError("resolved sibling authority has no governed cube scope")
    return handle, cubes


LAB_CASES = (
    # surface, kind, sibling surface, sibling kind, full immutable source context,
    # expected canonical candidate inside sibling scope
    ("bölge", "dimension", "net gelir", "metric", "Net geliri bölge bazında incele.", "region_axis_m"),
    ("bölgeler", "dimension", "net gelir", "metric", "Net geliri bölgeler bazında incele.", "region_axis_m"),
    ("bölgelere", "dimension", "net gelir", "metric", "Net geliri bölgelere göre kır.", "region_axis_m"),
    ("Bölgelerde", "dimension", "net gelir", "metric", "Bölgelerde net geliri incele.", "region_axis_m"),
    ("ürün", "dimension", "net gelir", "metric", "Net geliri ürün bazında incele.", "product_axis_n"),
    ("ürünler", "dimension", "net gelir", "metric", "Net geliri ürünler bazında incele.", "product_axis_n"),
    ("ürünlere", "dimension", "net gelir", "metric", "Net geliri ürünlere göre incele.", "product_axis_n"),
    ("bölüm", "dimension", "duruş süresi", "metric", "Duruş süresini bölüm bazında incele.", "department_axis_d"),
    ("bölümler", "dimension", "duruş süresi", "metric", "Duruş süresini bölümler bazında incele.", "department_axis_d"),
    ("bölümlerle", "dimension", "duruş süresi", "metric", "Duruş süresinin bölümlerle ilişkisini incele.", "department_axis_d"),
)


def build_receipt() -> dict:
    service, context = _context()
    rows = []
    for index, (
        surface,
        kind_hint,
        sibling_surface,
        sibling_kind,
        decision_context,
        expected,
    ) in enumerate(LAB_CASES, start=1):
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
            decision_context=decision_context,
        )
        scoped = GovernedSiblingScopeCandidateGenerator(
            base=base,
            sibling_cube_names=scope,
            max_candidates=DEFAULT_MAX_CANDIDATES,
        )
        receipt = scoped.receipt(
            request_id=f"lab:{index}",
            surface=surface,
            kind_hint=kind_hint,
            decision_context=decision_context,
            sibling_surface=sibling_surface,
        )
        rows.append(
            {
                **receipt.__dict__,
                "expected_canonical": expected,
                "expected_candidate_visible": (
                    expected in receipt.candidate_canonical_names
                ),
                "linker_required": (
                    receipt.fallback_used
                    and bool(receipt.candidate_ids)
                    and not receipt.too_broad
                ),
                "authority_minted_by_discovery": False,
            }
        )

    return {
        "kind": "dima_v2_day7_governed_sibling_scope_discovery_lab",
        "provider_free": True,
        "product_behavior_changed": False,
        "hypothesis": "GOVERNED_SIBLING_SCOPE_DISCOVERY",
        "rules": {
            "surface_interpretation_in_discovery": False,
            "stemming": False,
            "fuzzy_matching": False,
            "alias_creation": False,
            "global_catalog_enumeration": False,
            "binding_from_scope_membership": False,
            "max_candidates": DEFAULT_MAX_CANDIDATES,
        },
        "rows": rows,
    }


def main() -> int:
    payload = build_receipt()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
