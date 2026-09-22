"""Minimal Standard accepted-authority seal for Day 6.5.

The StandardProjection is the semantic body. AcceptedStandardAuthority only proves that
one exact projection, bound to one turn/context/attempt, is the accepted Standard
execution authority. Research keeps its existing AcceptedTurnContract body.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import TypeAlias

from pydantic import Field

from app.v2.manager_models import AcceptedTurnContract, StandardProjection
from app.v2.models import FrozenModel
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.standard_builder import StandardWorkMode


class AcceptedAuthorityFamily(StrEnum):
    STANDARD = "STANDARD"
    RESEARCH = "RESEARCH"


class AcceptedStandardAuthority(FrozenModel):
    authority_id: str = Field(pattern=r"^asa_[a-f0-9]{24}$")
    turn_id: str = Field(min_length=1)
    request_ref: str = Field(min_length=1)
    source_message_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    context_version: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_handle_refs: tuple[str, ...]
    accepted_attempt_id: str = Field(min_length=1)
    model_role: str = Field(min_length=1)
    work_mode: StandardWorkMode
    created_at_iso: str


# Deliberately an alias, not a second research semantic body.
AcceptedResearchAuthority: TypeAlias = AcceptedTurnContract
AcceptedAuthority: TypeAlias = AcceptedStandardAuthority | AcceptedResearchAuthority


class AcceptedAuthorityConflict(RuntimeError):
    pass


class StandardAuthoritySealer:
    def __init__(self, *, semantic_handles: SemanticHandleRegistry) -> None:
        self._handles = semantic_handles

    @staticmethod
    def _projection_hash(projection: StandardProjection) -> str:
        payload = json.dumps(
            projection.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _projection_handles(projection: StandardProjection) -> tuple[str, ...]:
        values = [
            *projection.metric_handles,
            *projection.dimension_handles,
            *projection.filter_handles,
        ]
        if projection.period_handle is not None:
            values.append(projection.period_handle)
        if projection.comparison_handle is not None:
            values.append(projection.comparison_handle)
        return tuple(dict.fromkeys(values))

    def seal(
        self,
        *,
        projection: StandardProjection,
        turn_id: str,
        request_ref: str,
        source_message_hash: str,
        context_version: str,
        tenant_binding: str,
        accepted_attempt_id: str,
        model_role: str,
        work_mode: StandardWorkMode,
    ) -> AcceptedStandardAuthority:
        semantic_handle_refs = self._projection_handles(projection)
        if not semantic_handle_refs:
            raise ValueError("standard authority requires semantic handles")

        for handle_id in semantic_handle_refs:
            self._handles.validate(
                handle_id,
                tenant_binding=tenant_binding,
                context_version=context_version,
            )

        projection_hash = self._projection_hash(projection)
        identity = json.dumps(
            {
                "turn_id": turn_id,
                "request_ref": request_ref,
                "source_message_hash": source_message_hash,
                "context_version": context_version,
                "projection_hash": projection_hash,
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
            projection_hash=projection_hash,
            semantic_handle_refs=semantic_handle_refs,
            accepted_attempt_id=accepted_attempt_id,
            model_role=model_role,
            work_mode=work_mode,
            created_at_iso=datetime.now(timezone.utc).isoformat(),
        )


class AcceptedAuthorityRegistry:
    """Exactly-one accepted semantic authority across Standard and Research per turn."""

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
        """Validate cross-family XOR without mutating shared authority state."""
        turn_id, family, authority_id = self._identity(authority)
        existing = self._by_turn.get(turn_id)
        candidate = (family, authority_id)
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
