from lab.v2_day7_capability_surface_receipt import build_receipt


def _rows():
    return {
        row["capability"]: row
        for row in build_receipt()["rows"]
    }


def test_day7_capability_surface_receipt_covers_every_registered_capability():
    rows = _rows()

    assert set(rows) == {
        "performance",
        "breakdown",
        "ranking",
        "comparison",
        "relationship",
        "root_cause",
        "trend",
        "report",
        "table",
        "chart",
        "explain",
    }


def test_current_direct_day7_execution_surface_is_explicit():
    rows = _rows()

    assert rows["performance"]["disposition"] == "DIRECT_DAY7_EXECUTION"
    assert rows["performance"]["task_kind"] == "QUERY"
    assert rows["performance"]["declared_tool_ids"] == ["wren.query"]

    assert rows["breakdown"]["disposition"] == "DIRECT_DAY7_EXECUTION"
    assert rows["breakdown"]["task_kind"] == "BREAKDOWN"
    assert rows["breakdown"]["declared_tool_ids"] == ["wren.breakdown"]

    assert rows["ranking"]["disposition"] == "DIRECT_DAY7_EXECUTION"
    assert rows["ranking"]["task_kind"] == "RANK"
    assert rows["ranking"]["declared_tool_ids"] == ["wren.rank"]

    assert rows["comparison"]["disposition"] == "DIRECT_DAY7_EXECUTION"
    assert rows["comparison"]["task_kind"] == "COMPARE"
    assert rows["comparison"]["declared_tool_ids"] == ["wren.compare"]

    assert rows["relationship"]["disposition"] == "DIRECT_DAY7_EXECUTION"
    assert rows["relationship"]["task_kind"] == "RELATIONSHIP"
    assert rows["relationship"]["declared_tool_ids"] == ["wren.relationship"]


def test_root_cause_and_trend_are_recognized_but_not_directly_executable_on_day7():
    rows = _rows()

    assert rows["root_cause"] == {
        "capability": "root_cause",
        "lane": "RESEARCH",
        "executable": False,
        "task_kind": None,
        "declared_tool_ids": [],
        "disposition": "NON_EXECUTABLE_DECLARED",
    }

    assert rows["trend"] == {
        "capability": "trend",
        "lane": "RESEARCH",
        "executable": False,
        "task_kind": "TREND",
        "declared_tool_ids": [],
        "disposition": "NON_EXECUTABLE_DECLARED",
    }


def test_day7_has_no_advertised_executable_dead_end():
    assert build_receipt()["unresolved_executable_surfaces"] == []


def test_presentation_capabilities_are_explicitly_non_executable():
    rows = _rows()

    for capability in ("report", "table", "chart", "explain"):
        assert rows[capability]["executable"] is False
        assert rows[capability]["disposition"] == "NON_EXECUTABLE_DECLARED"
