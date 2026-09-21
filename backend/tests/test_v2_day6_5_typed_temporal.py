"""Provider-free tests for typed temporal normalization/calendar authority."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.v2.temporal_intent import (
    ComparisonIntentKind,
    TemporalBindingEngine,
    TemporalIntentKind,
    TemporalNormalizationChoice,
    TypedTemporalNormalizer,
)


class _Scripted:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0
        self.last_user = None

    def structured_json(self, system, user, *, schema, schema_name):
        del system, schema
        assert schema_name == "dima_typed_temporal_intent_v1"
        self.calls += 1
        self.last_user = json.loads(user)
        return self.payload


def test_model_normalizes_language_but_calendar_engine_computes_quarter_dates():
    scripted = _Scripted(
        {
            "choices": [
                {
                    "request_id": "t1",
                    "target": "PERIOD",
                    "decision": "NORMALIZED",
                    "period_kind": "THIS_QUARTER",
                    "comparison_kind": None,
                    "n": None,
                    "reason": None,
                }
            ]
        }
    )
    normalizer = TypedTemporalNormalizer(structured=scripted.structured_json)
    (choice,) = normalizer.normalize((("t1", "bu çeyrek", "PERIOD"),))
    assert choice.period_kind == TemporalIntentKind.THIS_QUARTER
    assert scripted.last_user["requests"][0]["surface"] == "bu çeyrek"

    period = TemporalBindingEngine().period(
        choice=choice,
        source_text="bu çeyrek",
        time_dimension="Sales.date",
        today=date(2026, 9, 22),
    )
    assert period.start == "2026-07-01"
    assert period.end == "2026-09-22"


def test_previous_period_comparison_is_pure_arithmetic_over_governed_base():
    engine = TemporalBindingEngine()
    base = engine.period(
        choice=TemporalNormalizationChoice(
            request_id="base",
            target="PERIOD",
            decision="NORMALIZED",
            period_kind=TemporalIntentKind.LAST_N_DAYS,
            n=30,
        ),
        source_text="period",
        time_dimension="Sales.date",
        today=date(2026, 9, 22),
    )
    comparison = engine.comparison(
        choice=TemporalNormalizationChoice(
            request_id="cmp",
            target="COMPARISON",
            decision="NORMALIZED",
            comparison_kind=ComparisonIntentKind.PREVIOUS_PERIOD,
        ),
        source_text="reference",
        time_dimension="Sales.date",
        base_period=base,
    )
    assert comparison.reference_period.end < comparison.base_period.start
    base_days = (
        date.fromisoformat(base.end) - date.fromisoformat(base.start)
    ).days
    ref_days = (
        date.fromisoformat(comparison.reference_period.end)
        - date.fromisoformat(comparison.reference_period.start)
    ).days
    assert ref_days == base_days


def test_temporal_normalizer_can_abstain_without_date_guess():
    scripted = _Scripted(
        {
            "choices": [
                {
                    "request_id": "t1",
                    "target": "PERIOD",
                    "decision": "ABSTAIN",
                    "period_kind": None,
                    "comparison_kind": None,
                    "n": None,
                    "reason": "AMBIGUOUS",
                }
            ]
        }
    )
    (choice,) = TypedTemporalNormalizer(
        structured=scripted.structured_json
    ).normalize((("t1", "yakın zamanda", "PERIOD"),))
    assert choice.decision == "ABSTAIN"


def test_manager_typed_temporal_module_contains_no_language_regex_parser():
    source = (
        Path(__file__).resolve().parents[1] / "app" / "v2" / "temporal_intent.py"
    ).read_text(encoding="utf-8")
    for marker in (
        "import re",
        "re.search",
        "re.match",
        "re.compile",
        "SequenceMatcher",
        "SnowballStemmer",
        "SAYI_KALIBI",
        "sayi_coz",
    ):
        assert marker not in source
