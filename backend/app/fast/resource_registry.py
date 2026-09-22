"""Request-local opaque resource and field authority registries."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    FieldAuthority,
    FieldCandidate,
    ResourceCandidate,
    TableAuthority,
)


_NUMERIC_MARKERS = (
    "integer",
    "bigint",
    "float",
    "double",
    "decimal",
    "number",
    "numeric",
)
_TEMPORAL_MARKERS = ("date", "time", "timestamp")


def _type_hint(field: dict[str, Any]) -> str | None:
    for key in (
        "effective_type",
        "effective-type",
        "base_type",
        "base-type",
        "semantic_type",
        "semantic-type",
        "type",
    ):
        value = field.get(key)
        if value is not None:
            return str(value)
    return None


def _is_numeric(field: dict[str, Any]) -> bool:
    values = " ".join(
        str(field.get(key) or "")
        for key in (
            "effective_type",
            "effective-type",
            "base_type",
            "base-type",
            "semantic_type",
            "semantic-type",
            "type",
        )
    ).lower()
    return any(marker in values for marker in _NUMERIC_MARKERS)


def _is_temporal(field: dict[str, Any]) -> bool:
    values = " ".join(
        str(field.get(key) or "")
        for key in (
            "effective_type",
            "effective-type",
            "base_type",
            "base-type",
            "semantic_type",
            "semantic-type",
            "type",
        )
    ).lower()
    return any(marker in values for marker in _TEMPORAL_MARKERS)


class ResourceRegistry:
    """Opaque public handles mapped to hidden Metabase resource authority."""

    def __init__(self, search_rows: Iterable[dict[str, Any]], *, max_candidates: int = 8) -> None:
        if max_candidates < 1:
            raise ValueError("max_candidates must be positive")

        public: list[ResourceCandidate] = []
        authority: dict[str, dict[str, Any]] = {}

        for row in search_rows:
            if str(row.get("type") or "").lower() != "table":
                continue
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            raw_id = row.get("id")
            uri = str(row.get("uri") or "").strip()
            if not uri:
                try:
                    uri = f"metabase://table/{int(raw_id)}"
                except (TypeError, ValueError):
                    continue
            if not uri.startswith("metabase://table/"):
                continue

            handle = f"fast_res_{len(public) + 1:03d}"
            candidate = ResourceCandidate(
                handle=handle,
                name=name,
                display_name=(
                    str(row.get("display_name") or row.get("display-name") or "").strip()
                    or None
                ),
                description=str(row.get("description") or "").strip() or None,
                resource_type="table",
            )
            public.append(candidate)
            authority[handle] = {"uri": uri, "search_row": dict(row)}
            if len(public) >= max_candidates:
                break

        self._public = tuple(public)
        self._authority = authority

    @property
    def candidates(self) -> tuple[ResourceCandidate, ...]:
        return self._public

    def resource_uri(self, handle: str) -> str:
        try:
            return str(self._authority[handle]["uri"])
        except KeyError as exc:
            raise FastAskError(
                FastAskErrorCode.UNKNOWN_HANDLE,
                "resource selection did not reference a provided opaque handle",
            ) from exc

    def bind_table_details(self, handle: str, details: dict[str, Any]) -> "FieldRegistry":
        uri = self.resource_uri(handle)
        portable = details.get("portable_fk") or details.get("portable-fk")
        if not isinstance(portable, (list, tuple)) or len(portable) < 3:
            raise FastAskError(
                FastAskErrorCode.RESULT_CONTRACT_INVALID,
                "Metabase table details did not contain portable_fk",
            )

        database_name = str(details.get("database_name") or details.get("database-name") or "").strip()
        table_name = str(details.get("name") or "").strip()
        if not database_name or not table_name:
            raise FastAskError(
                FastAskErrorCode.RESULT_CONTRACT_INVALID,
                "Metabase table details are missing authoritative database/table names",
            )

        schema_value = details.get("database_schema")
        if schema_value is None:
            schema_value = details.get("database-schema")
        schema_name = None if schema_value is None else str(schema_value)

        table = TableAuthority(
            resource_handle=handle,
            resource_uri=uri,
            table_name=table_name,
            database_name=database_name,
            schema_name=schema_name,
            portable_fk=tuple(portable),
        )
        raw_fields = details.get("fields")
        if not isinstance(raw_fields, list):
            raise FastAskError(
                FastAskErrorCode.RESULT_CONTRACT_INVALID,
                "Metabase table details did not contain a fields list",
            )
        return FieldRegistry(table=table, raw_fields=raw_fields)


class FieldRegistry:
    def __init__(self, *, table: TableAuthority, raw_fields: Iterable[dict[str, Any]]) -> None:
        self.table = table
        public: list[FieldCandidate] = []
        authority: dict[str, FieldAuthority] = {}

        for raw in raw_fields:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name") or "").strip()
            if not name:
                continue
            handle = f"fast_field_{len(public) + 1:03d}"
            numeric = _is_numeric(raw)
            temporal = _is_temporal(raw)

            portable = raw.get("portable_fk") or raw.get("portable-fk")
            if not isinstance(portable, (list, tuple)) or len(portable) < 4:
                portable = [*table.portable_fk, name]

            type_hint = _type_hint(raw)
            public_candidate = FieldCandidate(
                handle=handle,
                name=name,
                display_name=(
                    str(raw.get("display_name") or raw.get("display-name") or "").strip()
                    or None
                ),
                type_hint=type_hint,
                numeric=numeric,
                temporal=temporal,
            )
            public.append(public_candidate)
            authority[handle] = FieldAuthority(
                field_handle=handle,
                field_name=name,
                display_name=public_candidate.display_name,
                portable_fk=tuple(portable),
                type_hint=type_hint,
                numeric=numeric,
                temporal=temporal,
            )

        self._public = tuple(public)
        self._authority = authority

    @property
    def candidates(self) -> tuple[FieldCandidate, ...]:
        return self._public

    def public_for_measure(self) -> tuple[FieldCandidate, ...]:
        return tuple(item for item in self._public if item.numeric)

    def public_for_temporal(self) -> tuple[FieldCandidate, ...]:
        return tuple(item for item in self._public if item.temporal)

    def public_for_breakdown(self) -> tuple[FieldCandidate, ...]:
        return self._public

    def resolve(self, handle: str) -> FieldAuthority:
        try:
            return self._authority[handle]
        except KeyError as exc:
            raise FastAskError(
                FastAskErrorCode.UNKNOWN_HANDLE,
                "field selection did not reference a provided opaque handle",
            ) from exc
