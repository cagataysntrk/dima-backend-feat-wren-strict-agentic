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
    volatile_lib_uuid_count: int = Field(ge=0)
    stabilized_aggregation_ref_count: int = Field(ge=0)
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

    @classmethod
    def _rewrite_aggregation_refs(
        cls,
        value: Any,
        *,
        uuid_to_index: dict[str, int],
    ) -> tuple[Any, int]:
        if isinstance(value, dict):
            rewritten: dict[str, Any] = {}
            count = 0
            for key, item in value.items():
                rewritten_item, item_count = cls._rewrite_aggregation_refs(
                    item,
                    uuid_to_index=uuid_to_index,
                )
                rewritten[key] = rewritten_item
                count += item_count
            return rewritten, count

        if isinstance(value, list):
            rewritten_items: list[Any] = []
            count = 0
            for item in value:
                rewritten_item, item_count = cls._rewrite_aggregation_refs(
                    item,
                    uuid_to_index=uuid_to_index,
                )
                rewritten_items.append(rewritten_item)
                count += item_count

            if (
                len(rewritten_items) >= 3
                and rewritten_items[0] == "aggregation"
                and isinstance(rewritten_items[1], dict)
                and isinstance(rewritten_items[2], str)
                and rewritten_items[2] in uuid_to_index
            ):
                rewritten_items[2] = uuid_to_index[rewritten_items[2]]
                count += 1
            return rewritten_items, count

        return value, 0

    @classmethod
    def _stabilize_aggregation_references(
        cls,
        query: dict[str, Any],
    ) -> tuple[dict[str, Any], int]:
        stages = query.get("stages")
        if not isinstance(stages, list):
            rewritten, count = cls._rewrite_aggregation_refs(
                query,
                uuid_to_index={},
            )
            if not isinstance(rewritten, dict):
                raise AssertionError("canonical query lost object shape")
            return rewritten, count

        stable_query: dict[str, Any] = {}
        total = 0
        for key, value in query.items():
            if key != "stages":
                rewritten, count = cls._rewrite_aggregation_refs(
                    value,
                    uuid_to_index={},
                )
                stable_query[key] = rewritten
                total += count
                continue

            stable_stages: list[Any] = []
            for stage in value:
                if not isinstance(stage, dict):
                    rewritten, count = cls._rewrite_aggregation_refs(
                        stage,
                        uuid_to_index={},
                    )
                    stable_stages.append(rewritten)
                    total += count
                    continue

                uuid_to_index: dict[str, int] = {}
                aggregations = stage.get("aggregation")
                if isinstance(aggregations, list):
                    for index, clause in enumerate(aggregations):
                        if (
                            isinstance(clause, list)
                            and len(clause) >= 2
                            and isinstance(clause[1], dict)
                            and isinstance(clause[1].get("lib/uuid"), str)
                        ):
                            runtime_uuid = clause[1]["lib/uuid"]
                            if runtime_uuid in uuid_to_index:
                                raise MetabaseCompilationBlocked(
                                    "AMBIGUOUS_RUNTIME_AGGREGATION_IDENTITY",
                                    "duplicate same-stage aggregation lib/uuid",
                                )
                            uuid_to_index[runtime_uuid] = index

                rewritten, count = cls._rewrite_aggregation_refs(
                    stage,
                    uuid_to_index=uuid_to_index,
                )
                stable_stages.append(rewritten)
                total += count

            stable_query[key] = stable_stages

        return stable_query, total

    @classmethod
    def _strip_runtime_volatility(cls, value: Any) -> tuple[Any, int]:
        """Remove only Metabase's documented runtime-volatile JSON map key: lib/uuid."""

        if isinstance(value, dict):
            stable: dict[str, Any] = {}
            removed = 0
            for key, item in value.items():
                if key == "lib/uuid":
                    removed += 1
                    continue
                stable_item, item_removed = cls._strip_runtime_volatility(item)
                stable[key] = stable_item
                removed += item_removed
            return stable, removed

        if isinstance(value, list):
            stable_items: list[Any] = []
            removed = 0
            for item in value:
                stable_item, item_removed = cls._strip_runtime_volatility(item)
                stable_items.append(stable_item)
                removed += item_removed
            return stable_items, removed

        return value, 0

    @classmethod
    def _first_difference(
        cls,
        left: Any,
        right: Any,
        *,
        path: str = "$",
    ) -> tuple[str, Any, Any] | None:
        """Return the first exact structural/value difference without normalizing either side."""

        if type(left) is not type(right):
            return path, left, right

        if isinstance(left, dict):
            left_keys = set(left)
            right_keys = set(right)
            if left_keys != right_keys:
                missing_left = sorted(right_keys - left_keys, key=str)
                missing_right = sorted(left_keys - right_keys, key=str)
                return (
                    path,
                    {"missing_keys": missing_left},
                    {"missing_keys": missing_right},
                )
            for key in sorted(left_keys, key=str):
                found = cls._first_difference(
                    left[key],
                    right[key],
                    path=f"{path}.{key}",
                )
                if found is not None:
                    return found
            return None

        if isinstance(left, list):
            if len(left) != len(right):
                return f"{path}.length", len(left), len(right)
            for index, (left_item, right_item) in enumerate(zip(left, right)):
                found = cls._first_difference(
                    left_item,
                    right_item,
                    path=f"{path}[{index}]",
                )
                if found is not None:
                    return found
            return None

        if left != right:
            return path, left, right
        return None

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

            first_decoded = self._decode(first.serialized_query)
            second_decoded = self._decode(second.serialized_query)

            first_identity_stable, first_ref_count = (
                self._stabilize_aggregation_references(first_decoded)
            )
            second_identity_stable, second_ref_count = (
                self._stabilize_aggregation_references(second_decoded)
            )
            first_stable, first_uuid_count = self._strip_runtime_volatility(
                first_identity_stable
            )
            second_stable, second_uuid_count = self._strip_runtime_volatility(
                second_identity_stable
            )
            if not isinstance(first_stable, dict) or not isinstance(second_stable, dict):
                raise AssertionError("stable canonical query lost object shape")

            if first_stable != second_stable:
                difference = self._first_difference(first_stable, second_stable)
                if difference is None:
                    raise AssertionError("canonical inequality had no observable difference")
                diff_path, first_value, second_value = difference
                raise MetabaseCompilationBlocked(
                    "NON_DETERMINISTIC_CANONICAL_SEMANTICS",
                    (
                        f"non-volatile construct-query output changed for {step.role} step "
                        f"at {diff_path}: first={first_value!r}, second={second_value!r}"
                    )[:1200],
                )

            actual_manifest = query_structural_manifest(first_stable)
            expected_manifest = query_structural_manifest(step.portable_query)
            self._assert_structure_preserved(
                expected=expected_manifest,
                actual=actual_manifest,
            )
            canonical_steps.append(
                CanonicalProjectionStep(
                    role=step.role,
                    serialized_query=first.serialized_query,
                    decoded_query=first_stable,
                    canonical_query_fingerprint=self._fingerprint(first_stable),
                    volatile_lib_uuid_count=max(
                        first_uuid_count,
                        second_uuid_count,
                    ),
                    stabilized_aggregation_ref_count=max(
                        first_ref_count,
                        second_ref_count,
                    ),
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
