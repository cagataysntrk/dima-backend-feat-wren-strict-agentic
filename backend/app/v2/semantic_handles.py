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

    def mint_from_resolver(
        self,
        *,
        tenant_binding: str,
        context_version: str,
        resolver_provenance_id: str,
        target_kind: str,
        canonical_target: Any,
        sensitive: bool = False,
    ) -> SemanticHandle:
        if not tenant_binding or not context_version or not resolver_provenance_id:
            raise ValueError("semantic handle binding alanları boş olamaz")
        payload = (
            f"{tenant_binding}\x1f{context_version}\x1f{resolver_provenance_id}"
            f"\x1f{target_kind}\x1f{repr(canonical_target)}"
        )
        handle_id = "sem_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        handle = SemanticHandle(
            handle_id=handle_id,
            tenant_binding=tenant_binding,
            context_version=context_version,
            resolver_provenance_id=resolver_provenance_id,
            target_kind=target_kind,
            sensitive=sensitive,
        )
        self._bindings[handle_id] = SemanticBinding(handle=handle, canonical_target=canonical_target)
        return handle

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
