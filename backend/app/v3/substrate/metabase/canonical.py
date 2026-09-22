"""Pinned-runtime canonicalization proof for P4 Metabase projections."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.compiler import (
    MetabaseProjectionPlan,
    QueryStructuralManifest,
    SemanticSlotManifest,
    query_structural_manifest,
)
from app.v3.substrate.metabase.execution_binding import MetabaseCompilationBlocked
from app.v3.substrate.metabase.models import ConstructedQuery


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CanonicalProjectionStep(FrozenModel):
    role: str = Field(pattern=r"^(primary|base|reference)$")
    serialized_query: str = Field(min_length=1)
    decoded_query: dict[str, Any]
    canonical_query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    manifest: QueryStructuralManifest


class CanonicalProjection(FrozenModel):
    authority_id: str = Field(min_length=1)
    projection_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    resolved_intent_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    semantic_context_version: str = Field(min_length=1)
    steps: tuple[CanonicalProjectionStep, ...] = Field(min_length=1)
    manifest: SemanticSlotManifest
    current_catalog_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    canonical_query_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class MetabaseCanonicalizer:
    def __init__(self, *, client: MetabaseAgentClient) -> None:
        self._client = client

    @staticmethod
    def _decode(serialized: str) -> dict[str, Any]:
        try:
            raw = base64.b64decode(serialized, validate=True)
            decoded = json.loads(raw.decode("utf-8"))
        except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MetabaseCompilationBlocked(
                "CANONICAL_QUERY_DECODE_FAILED",
                "Metabase construct-query returned invalid base64 JSON",
            ) from exc
        if not isinstance(decoded, dict):
            raise MetabaseCompilationBlocked(
                "CANONICAL_QUERY_DECODE_FAILED",
                "decoded canonical query is not an object",
            )
        return decoded

    @staticmethod
    def _fingerprint(decoded: dict[str, Any]) -> str:
        raw = json.dumps(
            decoded,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _assert_structure_preserved(
        *,
        expected: QueryStructuralManifest,
        actual: QueryStructuralManifest,
    ) -> None:
        if actual.explicit_join_count or actual.implicit_join_reference_count:
            raise MetabaseCompilationBlocked(
                "SILENT_FIELD_DROP_OR_REWRITE",
                "canonicalization introduced explicit or implicit join behavior",
            )

        fields = (
            "source_count",
            "aggregation_operators",
            "breakout_count",
            "filter_leaf_count",
            "time_predicate_count",
            "order_by_count",
            "limit",
            "explicit_join_count",
            "implicit_join_reference_count",
        )
        differences = {
            field: (getattr(expected, field), getattr(actual, field))
            for field in fields
            if getattr(expected, field) != getattr(actual, field)
        }
        if differences:
            raise MetabaseCompilationBlocked(
                "SILENT_FIELD_DROP_OR_REWRITE",
                f"canonical structural manifest drift: {differences!r}",
            )

    def canonicalize(self, plan: MetabaseProjectionPlan) -> CanonicalProjection:
        canonical_steps: list[CanonicalProjectionStep] = []

        for step in plan.steps:
            first: ConstructedQuery = self._client.construct_query(step.portable_query)
            second: ConstructedQuery = self._client.construct_query(step.portable_query)
            if first.serialized_query != second.serialized_query:
                raise MetabaseCompilationBlocked(
                    "NON_DETERMINISTIC_CANONICAL_SERIALIZATION",
                    f"construct-query changed for {step.role} step",
                )

            decoded = self._decode(first.serialized_query)
            actual_manifest = query_structural_manifest(decoded)
            expected_manifest = query_structural_manifest(step.portable_query)
            self._assert_structure_preserved(
                expected=expected_manifest,
                actual=actual_manifest,
            )
            canonical_steps.append(
                CanonicalProjectionStep(
                    role=step.role,
                    serialized_query=first.serialized_query,
                    decoded_query=decoded,
                    canonical_query_fingerprint=self._fingerprint(decoded),
                    manifest=actual_manifest,
                )
            )

        if len(canonical_steps) != plan.manifest.query_count:
            raise MetabaseCompilationBlocked(
                "SILENT_FIELD_DROP_OR_REWRITE",
                "canonical query count differs from Dima projection plan",
            )

        canonical_manifest = SemanticSlotManifest(
            query_count=len(canonical_steps),
            comparison_query_count=plan.manifest.comparison_query_count,
            steps=tuple(item.manifest for item in canonical_steps),
            semantic_ids=plan.manifest.semantic_ids,
            resource_entity_ids=plan.manifest.resource_entity_ids,
            resource_fingerprints=plan.manifest.resource_fingerprints,
        )

        aggregate = json.dumps(
            [item.decoded_query for item in canonical_steps],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        overall_fingerprint = hashlib.sha256(
            aggregate.encode("utf-8")
        ).hexdigest()

        return CanonicalProjection(
            authority_id=plan.authority_id,
            projection_hash=plan.projection_hash,
            resolved_intent_hash=plan.resolved_intent_hash,
            semantic_context_version=plan.semantic_context_version,
            steps=tuple(canonical_steps),
            manifest=canonical_manifest,
            current_catalog_fingerprint=plan.current_catalog_fingerprint,
            canonical_query_fingerprint=overall_fingerprint,
        )
