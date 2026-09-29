"""Shared typed P17 -> Product/P19 root-candidate semantic contract.

This is a transport contract over existing P16 claim persistence. It does not
own claim truth, Evidence truth, hypothesis identity, or causal qualification.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


ROOT_CAUSE_CANDIDATE_SEMANTICS_KEY = "__dima_root_cause_candidate_v1"


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RootCauseCandidateRelation(StrEnum):
    EXPLANATORY_CANDIDATE = "EXPLANATORY_CANDIDATE"


class RootCauseCandidateSemantics(Frozen):
    explanatory_subject_ref: str = Field(min_length=1)
    relation_kind: RootCauseCandidateRelation
    mechanism_ref: str = Field(min_length=1)
    scope_lineage_id: str = Field(min_length=1)
    scope_version_id: str = Field(pattern=r"^scope_v[1-9][0-9]*$")

    @property
    def mechanism_identity(self) -> tuple[str, str]:
        return (self.relation_kind.value, self.mechanism_ref)


def embed_root_cause_candidate_semantics(
    proposition: dict[str, Any],
    semantics: RootCauseCandidateSemantics,
) -> dict[str, Any]:
    """Bind Dima-owned candidate semantics without rewriting provider cognition."""

    if ROOT_CAUSE_CANDIDATE_SEMANTICS_KEY in proposition:
        raise ValueError(
            "root-cause candidate semantic slot is Dima-owned"
        )
    return {
        **proposition,
        ROOT_CAUSE_CANDIDATE_SEMANTICS_KEY: semantics.model_dump(mode="json"),
    }


def decode_root_cause_candidate_semantics(
    proposition: dict[str, Any],
) -> RootCauseCandidateSemantics | None:
    raw = proposition.get(ROOT_CAUSE_CANDIDATE_SEMANTICS_KEY)
    if raw is None:
        return None
    return RootCauseCandidateSemantics.model_validate(raw)
