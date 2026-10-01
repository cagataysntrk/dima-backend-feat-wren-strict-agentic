"""Typed idempotency keys for Brain V2 external/cognition activities."""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _fingerprint(value: dict[str, Any]) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CognitionPurpose(StrEnum):
    INTERPRET_NEW_INTENT = "INTERPRET_NEW_INTENT"
    ASSESS_NEW_EVIDENCE = "ASSESS_NEW_EVIDENCE"
    DISCOVER_HYPOTHESES = "DISCOVER_HYPOTHESES"
    DESIGN_DISCRIMINATING_TEST = "DESIGN_DISCRIMINATING_TEST"
    REPAIR_SCOPE = "REPAIR_SCOPE"
    SYNTHESIZE_REPORT = "SYNTHESIZE_REPORT"


class CognitionRequestKey(Frozen):
    owner: str = Field(min_length=1)
    purpose: CognitionPurpose
    objective_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    evidence_revision: int = Field(ge=0)
    hypothesis_revision: int = Field(ge=0)
    legal_action_profile_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    model_profile: str = Field(min_length=1)

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.model_dump(mode="json"))


class NativeMaterialRequestKey(Frozen):
    tenant: str = Field(min_length=1)
    principal: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")
    scope_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    material_requirement_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    engine_identity: str = Field(min_length=1)

    @property
    def fingerprint(self) -> str:
        return _fingerprint(self.model_dump(mode="json"))
