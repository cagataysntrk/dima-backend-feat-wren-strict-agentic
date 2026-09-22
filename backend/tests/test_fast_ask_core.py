from __future__ import annotations

from datetime import date
import json

import pytest

from app.fast.ask_cognition import StructuredJsonFastCognition
from app.fast.ask_errors import FastAskError, FastAskErrorCode
from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    DraftStatus,
    DraftTemporalIntent,
    FieldAuthority,
    TemporalKind,
)
from app.fast.evidence import deterministic_answer
from app.fast.query_builder import build_portable_query
from app.fast.resource_registry import ResourceRegistry
from app.fast.temporal import bind_temporal


def draft(
    *,
    aggregation=AggregationKind.COUNT,
    measure=None,
    breakdown=None,
    temporal=None,
):
    return AskDraft(
        status=DraftStatus.SUPPORTED,
        unsupported_reason=None,
        search_terms=("orders",),
        aggregation=aggregation,
        measure_hint=measure,
        breakdown_hint=breakdown,
        temporal=temporal or DraftTemporalIntent(
            kind=TemporalKind.NONE,
            days=None,
            start_date=None,
            end_date=None,
        ),
    )


def test_temporal_last_n_days_exact_bounds():
    window = bind_temporal(
        DraftTemporalIntent(
            kind=TemporalKind.LAST_N_DAYS,
            days=30,
            start_date=None,
            end_date=None,
        ),
        as_of_date=date(2026, 9, 7),
    )
    assert window is not None
    assert window.start.isoformat() == "2026-08-09"
    assert window.end_exclusive.isoformat() == "2026-09-08"


def test_temporal_previous_month_crosses_year_boundary():
    window = bind_temporal(
        DraftTemporalIntent(
            kind=TemporalKind.PREVIOUS_MONTH,
            days=None,
            start_date=None,
            end_date=None,
        ),
        as_of_date=date(2026, 1, 12),
    )
    assert window is not None
    assert window.start.isoformat() == "2025-12-01"
    assert window.end_exclusive.isoformat() == "2026-01-01"


def test_relative_temporal_without_anchor_fails_closed():
    with pytest.raises(FastAskError) as exc:
        bind_temporal(
            DraftTemporalIntent(
                kind=TemporalKind.CURRENT_MONTH,
                days=None,
                start_date=None,
                end_date=None,
            ),
            as_of_date=None,
        )
    assert exc.value.code == FastAskErrorCode.TEMPORAL_ANCHOR_REQUIRED


def test_absolute_range_is_inclusive_input_exclusive_query_end():
    window = bind_temporal(
        DraftTemporalIntent(
            kind=TemporalKind.ABSOLUTE_DATE_RANGE,
            days=None,
            start_date="2026-09-01",
            end_date="2026-09-30",
        ),
        as_of_date=None,
    )
    assert window is not None
    assert window.start.isoformat() == "2026-09-01"
    assert window.end_exclusive.isoformat() == "2026-10-01"


def test_resource_registry_exposes_no_raw_id_to_cognition():
    registry = ResourceRegistry([
        {
            "type": "table",
            "id": 77,
            "uri": "metabase://table/77",
            "name": "orders",
            "database_id": 4,
        }
    ])
    public = registry.candidates[0].model_dump()
    assert public["handle"] == "fast_res_001"
    assert "id" not in public
    assert "database_id" not in public
    assert registry.resource_uri("fast_res_001") == "metabase://table/77"


def test_unknown_resource_handle_is_rejected():
    registry = ResourceRegistry([
        {"type": "table", "id": 77, "uri": "metabase://table/77", "name": "orders"}
    ])
    with pytest.raises(FastAskError) as exc:
        registry.resource_uri("77")
    assert exc.value.code == FastAskErrorCode.UNKNOWN_HANDLE


def field(name, *, numeric=False, temporal=False):
    return {
        "name": name,
        "base_type": (
            "type/Float" if numeric else "type/Date" if temporal else "type/Text"
        ),
    }


def test_field_registry_derives_same_table_portable_authority():
    registry = ResourceRegistry([
        {"type": "table", "id": 77, "uri": "metabase://table/77", "name": "orders"}
    ])
    fields = registry.bind_table_details(
        "fast_res_001",
        {
            "database_name": "Dima Lab Analytics",
            "database_schema": "public",
            "name": "orders",
            "portable_fk": ["Dima Lab Analytics", "public", "orders"],
            "fields": [
                field("amount", numeric=True),
                field("order_date", temporal=True),
                field("region"),
            ],
        },
    )
    assert [item.name for item in fields.public_for_measure()] == ["amount"]
    assert [item.name for item in fields.public_for_temporal()] == ["order_date"]
    amount = fields.resolve(fields.public_for_measure()[0].handle)
    assert amount.portable_fk == (
        "Dima Lab Analytics",
        "public",
        "orders",
        "amount",
    )


def _authority(name, *, numeric=False, temporal=False):
    return FieldAuthority(
        field_handle="fast_field_001",
        field_name=name,
        display_name=None,
        portable_fk=("Dima Lab Analytics", "public", "orders", name),
        type_hint=None,
        numeric=numeric,
        temporal=temporal,
    )


def _table():
    registry = ResourceRegistry([
        {"type": "table", "id": 77, "uri": "metabase://table/77", "name": "orders"}
    ])
    return registry.bind_table_details(
        "fast_res_001",
        {
            "database_name": "Dima Lab Analytics",
            "database_schema": "public",
            "name": "orders",
            "portable_fk": ["Dima Lab Analytics", "public", "orders"],
            "fields": [],
        },
    ).table


def test_count_query_is_exact_and_has_no_native_sql():
    q = build_portable_query(
        draft=draft(),
        table=_table(),
        measure=None,
        temporal_field=None,
        breakdown=None,
        temporal_window=None,
    )
    assert q == {
        "lib/type": "mbql/query",
        "stages": [{
            "lib/type": "mbql.stage/mbql",
            "source-table": ["Dima Lab Analytics", "public", "orders"],
            "aggregation": [["count", {}]],
        }],
    }
    assert "native" not in str(q).lower()
    assert "join" not in str(q).lower()


def test_sum_temporal_breakdown_query_is_exact():
    temporal_intent = DraftTemporalIntent(
        kind=TemporalKind.LAST_N_DAYS,
        days=30,
        start_date=None,
        end_date=None,
    )
    d = draft(
        aggregation=AggregationKind.SUM,
        measure="amount",
        breakdown="region",
        temporal=temporal_intent,
    )
    amount = _authority("amount", numeric=True)
    order_date = FieldAuthority(
        field_handle="fast_field_002",
        field_name="order_date",
        display_name=None,
        portable_fk=("Dima Lab Analytics", "public", "orders", "order_date"),
        type_hint=None,
        numeric=False,
        temporal=True,
    )
    region = FieldAuthority(
        field_handle="fast_field_003",
        field_name="region",
        display_name=None,
        portable_fk=("Dima Lab Analytics", "public", "orders", "region"),
        type_hint=None,
        numeric=False,
        temporal=False,
    )
    window = bind_temporal(temporal_intent, as_of_date=date(2026, 9, 7))
    q = build_portable_query(
        draft=d,
        table=_table(),
        measure=amount,
        temporal_field=order_date,
        breakdown=region,
        temporal_window=window,
    )
    stage = q["stages"][0]
    assert stage["aggregation"] == [[
        "sum",
        {},
        ["field", {}, ["Dima Lab Analytics", "public", "orders", "amount"]],
    ]]
    assert stage["filters"] == [[
        "and",
        {},
        [
            ">=",
            {},
            ["field", {}, ["Dima Lab Analytics", "public", "orders", "order_date"]],
            "2026-08-09",
        ],
        [
            "<",
            {},
            ["field", {}, ["Dima Lab Analytics", "public", "orders", "order_date"]],
            "2026-09-08",
        ],
    ]]
    assert stage["breakout"] == [[
        "field",
        {},
        ["Dima Lab Analytics", "public", "orders", "region"],
    ]]
    assert stage["order-by"] == [["desc", {}, ["aggregation", {}, 0]]]
    assert stage["limit"] == 100


def test_count_answer_must_come_from_result():
    from app.fast.ask_models import FastQueryResult

    result = FastQueryResult(
        columns=("count",),
        rows=({"count": 29},),
        row_count=1,
    )
    assert deterministic_answer(
        aggregation=AggregationKind.COUNT,
        breakdown=None,
        result=result,
    ) == "Sonuç: 29 kayıt."


def test_breakdown_answer_reports_observed_result_rows_only():
    from app.fast.ask_models import FastQueryResult

    result = FastQueryResult(
        columns=("region", "sum"),
        rows=({"region": "East", "sum": 300}, {"region": "West", "sum": 200}),
        row_count=2,
    )
    assert deterministic_answer(
        aggregation=AggregationKind.SUM,
        breakdown=_authority("region"),
        result=result,
    ) == "2 kırılım döndü."



class _CaptureStructuredGenerator:
    def __init__(self) -> None:
        self.system = ""
        self.user = ""

    def structured_json(self, system, user, *, schema, schema_name):
        self.system = system
        self.user = user
        assert schema_name == "dima_fast_ask_draft"
        return json.dumps(
            {
                "status": "SUPPORTED",
                "unsupported_reason": None,
                "search_terms": ["entity"],
                "aggregation": "COUNT",
                "measure_hint": None,
                "breakdown_hint": None,
                "temporal": {
                    "kind": "NONE",
                    "days": None,
                    "start_date": None,
                    "end_date": None,
                },
            }
        )


def test_fast_cognition_prompt_defines_generic_metadata_retrieval_contract():
    generator = _CaptureStructuredGenerator()
    cognition = StructuredJsonFastCognition(generator)

    observed = cognition.draft(question="Herhangi bir iş varlığını say.")

    assert observed.status == DraftStatus.SUPPORTED
    system = generator.system.lower()
    assert "primary business/data entity" in system
    assert "every search term must independently help retrieve" in system
    assert "at least one likely english entity/table lookup term" in system
    assert "aggregation or operation words" in system
    assert "measure names, breakdown dimensions" in system
    assert "prefer standalone entity/table nouns" in system
    assert "at most four search terms" in system
    assert "orders" not in system
    assert "sipariş" not in system
