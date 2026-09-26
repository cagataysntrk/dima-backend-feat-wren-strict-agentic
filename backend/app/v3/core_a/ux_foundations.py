"""Core Closure A5 — Wave-1 UX foundation descriptors.

These are backend/domain dependency contracts only. They do not implement UI.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CATALOG_PATH = (
    Path(__file__).resolve().parents[3]
    / "product_contracts"
    / "ux_foundations.json"
)


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class UXFoundationDescriptor(Frozen):
    ux_id: str = Field(pattern=r"^(general|finance|manufacturing|textile|plastics)-[0-9]{2}$")
    group: Literal["general", "finance", "manufacturing", "textile", "plastics"]
    ordinal: int = Field(ge=1, le=10)
    ux_name: str = Field(min_length=1)
    business_objective: str = Field(min_length=1)

    required_entity_types: tuple[str, ...]
    required_metrics: tuple[str, ...]
    required_source_data: tuple[str, ...]

    watch_dependency: bool
    signal_dependency: bool
    investigation_dependency: bool
    evidence_dependency: bool
    decision_dependency: bool
    action_work_dependency: bool
    outcome_dependency: bool
    memory_dependency: bool

    sector_pack_requirements: tuple[str, ...]
    specialized_engine_gap: str | None = None
    headless_api_needs: tuple[str, ...]
    current_feasibility: Literal[
        "FOUNDATION_READY",
        "FOUNDATION_PARTIAL",
        "SPECIAL_ENGINE_DEFERRED",
        "PRODUCTIZATION_DEBT",
    ]
    deferred_capabilities: tuple[str, ...]
    shared_motors: tuple[str, ...]

    @model_validator(mode="after")
    def coherent(self):
        expected_prefix = f"{self.group}-"
        if not self.ux_id.startswith(expected_prefix):
            raise ValueError("ux_id/group mismatch")
        if int(self.ux_id.rsplit("-", 1)[1]) != self.ordinal:
            raise ValueError("ux_id/ordinal mismatch")
        if self.specialized_engine_gap is not None:
            if not self.specialized_engine_gap.startswith("SPECIAL_ENGINE_DEFERRED:"):
                raise ValueError("heavy engine gap must be explicitly deferred")
            if self.current_feasibility != "SPECIAL_ENGINE_DEFERRED":
                raise ValueError("specialized engine gap requires deferred feasibility")
        return self


class UXFoundationCatalog(Frozen):
    version: str
    architecture: str
    descriptors: tuple[UXFoundationDescriptor, ...]

    @model_validator(mode="after")
    def complete_wave_one(self):
        if len(self.descriptors) != 50:
            raise ValueError("Wave-1 catalog must contain exactly 50 descriptors")
        ids = [item.ux_id for item in self.descriptors]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate UX descriptor IDs")
        for group in ("general", "finance", "manufacturing", "textile", "plastics"):
            rows = [item for item in self.descriptors if item.group == group]
            if [item.ordinal for item in rows] != list(range(1, 11)):
                raise ValueError(f"{group} must contain ordered 1..10 descriptors")
        return self


def load_ux_foundations(path: Path = CATALOG_PATH) -> UXFoundationCatalog:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return UXFoundationCatalog.model_validate(raw)
