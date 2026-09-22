"""Result normalization, evidence hashing, and deterministic answer synthesis."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Any

from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    AggregationKind,
    FastEvidence,
    FastQueryResult,
    FieldAuthority,
    TableAuthority,
    TemporalWindow,
)
from app.fast.metabase_models import ExecutionResponse


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def _column_names(data: dict[str, Any], rows: list[Any]) -> list[str]:
    cols = data.get("cols") or data.get("columns") or []
    names: list[str] = []
    for index, col in enumerate(cols):
        if isinstance(col, dict):
            raw = (
                col.get("name")
                or col.get("display_name")
                or col.get("display-name")
                or col.get("field_ref")
            )
            name = str(raw or f"col_{index}")
        else:
            name = str(col)
        if name in names:
            suffix = 2
            candidate = f"{name}_{suffix}"
            while candidate in names:
                suffix += 1
                candidate = f"{name}_{suffix}"
            name = candidate
        names.append(name)

    if not names and rows:
        first = rows[0]
        if isinstance(first, dict):
            names = [str(key) for key in first.keys()]
        elif isinstance(first, (list, tuple)):
            names = [f"col_{index}" for index in range(len(first))]
    return names


def normalize_execution(response: ExecutionResponse) -> FastQueryResult:
    raw_rows = response.data.get("rows") or []
    if not isinstance(raw_rows, list):
        raise FastAskError(
            FastAskErrorCode.RESULT_CONTRACT_INVALID,
            "Metabase execution data.rows is not a list",
        )
    names = _column_names(response.data, raw_rows)
    normalized: list[dict[str, Any]] = []

    for raw in raw_rows:
        if isinstance(raw, dict):
            row = {str(key): value for key, value in raw.items()}
            if not names:
                names = list(row)
        elif isinstance(raw, (list, tuple)):
            if len(raw) != len(names):
                raise FastAskError(
                    FastAskErrorCode.RESULT_CONTRACT_INVALID,
                    "Metabase row width does not match result columns",
                )
            row = dict(zip(names, raw))
        else:
            raise FastAskError(
                FastAskErrorCode.RESULT_CONTRACT_INVALID,
                "Metabase result row is neither object nor array",
            )
        normalized.append(row)

    return FastQueryResult(
        columns=tuple(names),
        rows=tuple(normalized),
        row_count=len(normalized),
    )


def build_evidence(
    *,
    question: str,
    table: TableAuthority,
    fields: dict[str, FieldAuthority],
    temporal_window: TemporalWindow | None,
    portable_query: dict[str, Any],
    access_fingerprint: str,
    metabase_runtime_version: str,
    result: FastQueryResult,
) -> FastEvidence:
    query_fingerprint = hashlib.sha256(
        _canonical({
            "query": portable_query,
            "access_fingerprint": access_fingerprint,
        })
    ).hexdigest()
    result_digest = hashlib.sha256(_canonical(result.model_dump(mode="json"))).hexdigest()
    evidence_id = "ev_" + hashlib.sha256(
        _canonical({
            "question": question,
            "resource": table.resource_uri,
            "query_fingerprint": query_fingerprint,
            "result_digest": result_digest,
        })
    ).hexdigest()[:20]

    return FastEvidence(
        evidence_id=evidence_id,
        question=question,
        resource_handle=table.resource_handle,
        resource_ref=table.resource_uri,
        field_refs={purpose: field.field_name for purpose, field in fields.items()},
        exact_time_bounds=(
            {
                "start": temporal_window.start.isoformat(),
                "end_exclusive": temporal_window.end_exclusive.isoformat(),
                "kind": temporal_window.kind.value,
            }
            if temporal_window is not None
            else None
        ),
        portable_query=portable_query,
        query_fingerprint=query_fingerprint,
        access_fingerprint=access_fingerprint,
        metabase_runtime_version=metabase_runtime_version,
        result=result,
        result_digest=result_digest,
    )


def _number(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise FastAskError(
            FastAskErrorCode.RESULT_CONTRACT_INVALID,
            "expected scalar aggregation value is not numeric",
        ) from exc


def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral():
        return str(value.quantize(Decimal("1")))
    rendered = format(value.normalize(), "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def deterministic_answer(
    *,
    aggregation: AggregationKind,
    breakdown: FieldAuthority | None,
    result: FastQueryResult,
) -> str:
    if breakdown is not None:
        return f"{result.row_count} kırılım döndü."

    if result.row_count != 1 or len(result.rows) != 1:
        raise FastAskError(
            FastAskErrorCode.RESULT_CONTRACT_INVALID,
            "scalar aggregation must return exactly one row",
        )
    row = result.rows[0]
    preferred = aggregation.value.lower()
    value = row.get(preferred)
    if value is None:
        if len(row) != 1:
            raise FastAskError(
                FastAskErrorCode.RESULT_CONTRACT_INVALID,
                f"scalar result did not expose expected {preferred!r} column",
            )
        value = next(iter(row.values()))

    number = _number(value)
    if aggregation == AggregationKind.COUNT:
        if number != number.to_integral():
            raise FastAskError(
                FastAskErrorCode.RESULT_CONTRACT_INVALID,
                "COUNT result is not integral",
            )
        return f"Sonuç: {_format_decimal(number)} kayıt."
    return f"Sonuç: {_format_decimal(number)}."
