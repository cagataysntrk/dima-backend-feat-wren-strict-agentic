"""Resolver-owned opaque semantic handles for Day 6.5.

Canonical semantic values remain inside this trusted registry. Manager-facing contracts
carry only sem_* IDs plus non-secret provenance metadata.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from app.v2.manager_models import SemanticHandle


@dataclass(frozen=True)
class SemanticBinding:
    handle: SemanticHandle
    canonical_target: Any


class SemanticHandleRegistry:
    def __init__(self) -> None:
        self._bindings: dict[str, SemanticBinding] = {}

    def _mint(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        provenance_id: str,
        target_kind: str,
        canonical_target: Any,
        sensitive: bool = False,
        provenance_type: str = "USER_SOURCE",
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
    ) -> SemanticHandle:
        if not tenant_binding or not context_version or not provenance_id:
            raise ValueError("semantic handle binding alanları boş olamaz")
        payload = (
            f"{tenant_binding}\x1f{context_version}\x1f{provenance_id}"
            f"\x1f{target_kind}\x1f{provenance_type}\x1f{parent_obligation_id or ''}"
            f"\x1f{trigger_evidence_ref or ''}\x1f{repr(canonical_target)}"
        )
        handle_id = "sem_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        handle = SemanticHandle(
            handle_id=handle_id,
            tenant_binding=tenant_binding,
            context_version=context_version,
            resolver_provenance_id=provenance_id,
            target_kind=target_kind,
            provenance_type=provenance_type,
            parent_obligation_id=parent_obligation_id,
            trigger_evidence_ref=trigger_evidence_ref,
            sensitive=sensitive,
        )
        self._bindings[handle_id] = SemanticBinding(
            handle=handle,
            canonical_target=canonical_target,
        )
        return handle

    def mint_from_resolver(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        resolver_provenance_id: str,
        target_kind: str,
        canonical_target: Any,
        sensitive: bool = False,
        provenance_type: str = "USER_SOURCE",
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
    ) -> SemanticHandle:
        """Legacy/Day1-6 resolver authority path; preserved for non-Manager callers."""
        return self._mint(
            tenant_binding=tenant_binding,
            context_version=context_version,
            provenance_id=resolver_provenance_id,
            target_kind=target_kind,
            canonical_target=canonical_target,
            sensitive=sensitive,
            provenance_type=provenance_type,
            parent_obligation_id=parent_obligation_id,
            trigger_evidence_ref=trigger_evidence_ref,
        )

    def mint_from_binding_gate(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        candidate_id: str,
        target_kind: str,
        canonical_target: Any,
        sensitive: bool = False,
        provenance_type: str = "USER_SOURCE",
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
    ) -> SemanticHandle:
        """Day6.5 Manager authority path after bounded candidate selection + gate."""
        if not str(candidate_id).startswith("cand_"):
            raise ValueError("binding gate candidate_id must be runtime-issued cand_*")
        return self._mint(
            tenant_binding=tenant_binding,
            context_version=context_version,
            provenance_id=candidate_id,
            target_kind=target_kind,
            canonical_target=canonical_target,
            sensitive=sensitive,
            provenance_type=provenance_type,
            parent_obligation_id=parent_obligation_id,
            trigger_evidence_ref=trigger_evidence_ref,
        )

    def mint_from_temporal_engine(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        temporal_provenance_id: str,
        target_kind: str,
        canonical_target: Any,
        provenance_type: str = "USER_SOURCE",
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
    ) -> SemanticHandle:
        """Manager temporal authority after typed normalization + calendar arithmetic."""
        if target_kind not in {"period", "comparison"}:
            raise ValueError("temporal engine may mint only period/comparison handles")
        return self._mint(
            tenant_binding=tenant_binding,
            context_version=context_version,
            provenance_id=temporal_provenance_id,
            target_kind=target_kind,
            canonical_target=canonical_target,
            sensitive=False,
            provenance_type=provenance_type,
            parent_obligation_id=parent_obligation_id,
            trigger_evidence_ref=trigger_evidence_ref,
        )

    def validate(
        self,
        handle_id: str,
        *,
        tenant_binding: str,
        context_version: str,
    ) -> SemanticHandle:
        binding = self._bindings.get(handle_id)
        if binding is None:
            raise KeyError("unknown/non-Resolver semantic handle")
        handle = binding.handle
        if handle.tenant_binding != tenant_binding:
            raise ValueError("foreign-tenant semantic handle")
        if handle.context_version != context_version:
            raise ValueError("stale-context semantic handle")
        return handle

    def handles_for_parent(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        parent_obligation_id: str,
        trigger_evidence_ref: str | None = None,
        provenance_type: str = "AGENT_DERIVED",
    ) -> tuple[SemanticHandle, ...]:
        """Project existing opaque handle metadata for one exact authority lineage.

        This is a read-only registry query. It never mints semantics and never exposes
        canonical targets. Tenant/context, parent obligation, provenance and optional
        trigger Evidence are exact-match filters so sibling/foreign derived handles
        cannot enter the same executable action surface.
        """

        rows: list[SemanticHandle] = []
        for binding in self._bindings.values():
            handle = binding.handle
            if handle.tenant_binding != tenant_binding:
                continue
            if handle.context_version != context_version:
                continue
            if handle.parent_obligation_id != parent_obligation_id:
                continue
            if handle.provenance_type != provenance_type:
                continue
            if (
                trigger_evidence_ref is not None
                and handle.trigger_evidence_ref != trigger_evidence_ref
            ):
                continue
            rows.append(handle)
        return tuple(sorted(rows, key=lambda item: item.handle_id))

    def binding_for_execution(
        self,
        handle_id: str,
        *,
        tenant_binding: str,
        context_version: str,
    ) -> SemanticBinding:
        self.validate(
            handle_id,
            tenant_binding=tenant_binding,
            context_version=context_version,
        )
        return self._bindings[handle_id]
