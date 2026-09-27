from lab.v2_day7_semantic_surface_diagnostic import build_receipt


def _rows():
    return {
        row["surface"]: row
        for row in build_receipt()["rows"]
    }


def test_base_and_catalog_forms_bind_without_language_specific_repair():
    rows = _rows()

    for surface in ("bölge", "bölgeler", "ürün", "ürünler"):
        row = rows[surface]
        assert row["expected_present_in_catalog"] is True
        assert row["candidate_count_before_bound"] >= 1
        assert row["candidate_count_visible"] >= 1
        assert row["exact_candidates"]
        assert row["linker_decision"]["status"] == "BOUND"
        assert row["linker_decision"]["mode"] == "EXACT"
        assert row["binding_gate_reached"] is True
        assert row["binding_gate_result"] is not None


def test_inflected_dimension_failures_are_retrieval_discovery_not_linker_or_binding():
    rows = _rows()

    for surface in ("bölgelere", "Bölgelerde", "bölgelerde", "ürünlere"):
        row = rows[surface]
        assert row["expected_present_in_catalog"] is True
        assert row["retrieval_backend"] == "governed_token_index_v1"
        assert row["candidate_count_before_bound"] == 0
        assert row["candidate_count_visible"] == 0
        assert row["semantic_linker_called"] is False
        assert row["linker_decision"]["status"] == "RETRIEVAL_MISS"
        assert row["binding_gate_reached"] is False
        assert row["binding_gate_result"] is None
        assert row["classification"] == "RETRIEVAL_DISCOVERY"


def test_previous_period_surface_is_not_catalog_retrieval_failure():
    receipt = build_receipt()
    temporal = receipt["temporal_surface"]

    assert temporal["surface"] == "geçen dönemle"
    assert temporal["pipeline"] == "typed_temporal_normalizer"
    assert temporal["catalog_retrieval_applicable"] is False
    assert temporal["explicit_base_period_in_request"] is False
    assert temporal["classification"] == "OTHER CONTRACT"
