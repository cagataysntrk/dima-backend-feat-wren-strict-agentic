"""Accepted semantic authority contracts for Dima v3."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.v2.manager_models import AcceptedTurnContract as _ExistingAcceptedTurnContract
from app.v3.analytics_contract import (
    StandardProjection,
    projection_handles,
    projection_hash,
)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# There is deliberately no second Research authority body in v3.
AcceptedTurnContract: TypeAlias = _ExistingAcceptedTurnContract
AcceptedResearchAuthority: TypeAlias = _ExistingAcceptedTurnContract


class StandardWorkMode(StrEnum):
    STANDARD_DIRECT = "STANDARD_DIRECT"
    STANDARD_BUILDER = "STANDARD_BUILDER"


class AcceptedAuthorityFamily(StrEnum):
    STANDARD = "STANDARD"
    RESEARCH = "RESEARCH"


class SemanticSurfaceState(StrEnum):
    BOUND = "BOUND"
    UNRESOLVED = "UNRESOLVED"


class SemanticSurfaceRecord(FrozenModel):
    source_ref: str = Field(pattern=r"^src_[a-f0-9]{24}$")
    surface_text: str = Field(min_length=1)
    kind_hint: str = Field(min_length=1)
    state: SemanticSurfaceState
    handle_id: str | None = Field(default=None, pattern=r"^sem_[a-f0-9]{24}$")
    unresolved_reason: str | None = None

    @model_validator(mode="after")
    def _terminal_shape(self):
        if self.state == SemanticSurfaceState.BOUND:
            if self.handle_id is None or self.unresolved_reason is not None:
                raise ValueError("BOUND semantic surface requires handle only")
        else:
            if self.handle_id is not None or not self.unresolved_reason:
                raise ValueError("UNRESOLVED semantic surface requires explicit reason only")
        return self


class SemanticSurfaceCoverage(FrozenModel):
    turn_id: str = Field(min_length=1)
    attempt_id: str = Field(min_length=1)
    context_version: str = Field(min_length=1)
    surfaces: tuple[SemanticSurfaceRecord, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_material_surfaces(self):
        keys = [
            (item.source_ref, item.surface_text, item.kind_hint)
            for item in self.surfaces
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("material semantic surface must be accounted exactly once")
        return self

    @property
    def complete(self) -> bool:
        return all(item.state == SemanticSurfaceState.BOUND for item in self.surfaces)

    @property
    def bound_handle_refs(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                item.handle_id
                for item in self.surfaces
                if item.state == SemanticSurfaceState.BOUND and item.handle_id is not None
            )
        )


class AcceptedStandardAuthority(FrozenModel):
    authority_id: str = Field(pattern=r"^asa_[a-f0-9]{24}$")
    turn_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    context_version: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_handle_refs: tuple[str, ...] = Field(min_length=1)
    accepted_attempt_id: str = Field(min_length=1)
    model_role: str = Field(min_length=1)
    work_mode: StandardWorkMode
    created_at_iso: str


AcceptedAuthority: TypeAlias = AcceptedStandardAuthority | AcceptedResearchAuthority


class SemanticHandleValidator(Protocol):
    def validate(
        self,
        handle_id: str,
        *,
        tenant_binding: str,
        context_version: str,
    ):
        ...


class StandardAuthoritySealer:
    def __init__(self, *, semantic_handles: SemanticHandleValidator) -> None:
        self._handles = semantic_handles

    def seal(
        self,
        *,
        projection: StandardProjection,
        coverage: SemanticSurfaceCoverage,
        turn_id: str,
        request_ref: str,
        source_message_hash: str,
        context_version: str,
        tenant_binding: str,
        accepted_attempt_id: str,
        model_role: str,
        work_mode: StandardWorkMode,
    ) -> AcceptedStandardAuthority:
        if coverage.turn_id != turn_id:
            raise ValueError("semantic coverage turn does not match authority turn")
        if coverage.attempt_id != accepted_attempt_id:
            raise ValueError("semantic coverage attempt does not match accepted attempt")
        if coverage.context_version != context_version:
            raise ValueError("semantic coverage context does not match authority context")
        if not coverage.complete:
            raise ValueError("cannot seal Standard authority with unresolved material surface")

        handles = projection_handles(projection)
        if not handles:
            raise ValueError("standard authority requires semantic handles")
        if set(coverage.bound_handle_refs) != set(handles):
            raise ValueError(
                "semantic surface coverage handle set must equal projection handle set"
            )

        for handle_id in handles:
            self._handles.validate(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )

        p_hash = projection_hash(projection)
        identity = json.dumps(
            {
                "turn_id": turn_id,
                "request_ref": request_ref,
                "source_message_hash": source_message_hash,
                "context_version": context_version,
                "projection_hash": p_hash,
                "accepted_attempt_id": accepted_attempt_id,
                "model_role": model_role,
                "work_mode": work_mode.value,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        authority_id = "asa_" + hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:24]

        return AcceptedStandardAuthority(
            authority_id=authority_id,
            turn_id=turn_id,
            request_ref=request_ref,
            source_message_hash=source_message_hash,
            context_version=context_version,
            projection_hash=p_hash,
            semantic_handle_refs=handles,
            accepted_attempt_id=accepted_attempt_id,
            model_role=model_role,
            work_mode=work_mode,
            created_at_iso=datetime.now(timezone.utc).isoformat(),
        )


class AcceptedAuthorityConflict(RuntimeError):
    pass


class SharedAuthorityArbiter:
    """Exactly one accepted semantic authority across Standard and Research per turn."""

    def __init__(self) -> None:
        self._by_turn: dict[str, tuple[AcceptedAuthorityFamily, str]] = {}

    @staticmethod
    def _identity(
        authority: AcceptedAuthority,
    ) -> tuple[str, AcceptedAuthorityFamily, str]:
        if isinstance(authority, AcceptedStandardAuthority):
            return (
                authority.turn_id,
                AcceptedAuthorityFamily.STANDARD,
                authority.authority_id,
            )
        return (
            authority.turn_id,
            AcceptedAuthorityFamily.RESEARCH,
            authority.contract_id,
        )

    def validate(self, authority: AcceptedAuthority) -> None:
        turn_id, family, authority_id = self._identity(authority)
        candidate = (family, authority_id)
        existing = self._by_turn.get(turn_id)
        if existing is None or existing == candidate:
            return
        raise AcceptedAuthorityConflict(
            f"turn {turn_id} already has accepted {existing[0].value} authority "
            f"{existing[1]}"
        )

    def commit(self, authority: AcceptedAuthority) -> None:
        self.validate(authority)
        turn_id, family, authority_id = self._identity(authority)
        candidate = (family, authority_id)
        if self._by_turn.get(turn_id) == candidate:
            return
        self._by_turn[turn_id] = candidate

    def accepted(
        self,
        turn_id: str,
    ) -> tuple[AcceptedAuthorityFamily, str] | None:
        return self._by_turn.get(turn_id)
