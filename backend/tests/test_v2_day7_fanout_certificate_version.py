"""Day7 fanout certificate freshness/version binding."""

from __future__ import annotations

from app import fanout


def _certificate(*, mdl_version="mdl-current", healthy=True):
    return {
        "version": 1,
        "olculme_zamani": "2026-09-22T20:00:00+00:00",
        "mdl_version": mdl_version,
        "relationships": {
            "orders_customer": {
                "durum": "olculdu",
                "saglikli": healthy,
            }
        },
    }


def test_matching_mdl_certificate_preserves_measured_health():
    proof = fanout.kanit(
        _certificate(healthy=True),
        "orders_customer",
        current_mdl_version="mdl-current",
    )
    assert proof == {
        "relationship": "orders_customer",
        "status": "HEALTHY",
        "certified": "olculdu:saglikli",
        "certificate_mdl_version": "mdl-current",
        "current_mdl_version": "mdl-current",
        "measured_at": "2026-09-22T20:00:00+00:00",
    }


def test_matching_mdl_risky_certificate_stays_risky():
    proof = fanout.kanit(
        _certificate(healthy=False),
        "orders_customer",
        current_mdl_version="mdl-current",
    )
    assert proof["status"] == "RISKY"
    assert proof["certified"] == "olculdu:riskli"


def test_stale_certificate_can_never_stamp_current_relationship_healthy():
    proof = fanout.kanit(
        _certificate(mdl_version="mdl-old", healthy=True),
        "orders_customer",
        current_mdl_version="mdl-current",
    )
    assert proof["status"] == "MDL_MISMATCH"
    assert proof["certified"] == "olculmedi"
    assert proof["certificate_mdl_version"] == "mdl-old"
    assert proof["current_mdl_version"] == "mdl-current"


def test_missing_version_is_unverified_not_healthy():
    cert = _certificate()
    cert.pop("mdl_version")

    proof = fanout.kanit(
        cert,
        "orders_customer",
        current_mdl_version="mdl-current",
    )
    assert proof["status"] == "MDL_VERSION_MISSING"
    assert proof["certified"] == "olculmedi"


def test_missing_relationship_is_unverified_even_on_matching_mdl():
    proof = fanout.kanit(
        {
            "mdl_version": "mdl-current",
            "olculme_zamani": "2026-09-22T20:00:00+00:00",
            "relationships": {},
        },
        "orders_customer",
        current_mdl_version="mdl-current",
    )
    assert proof["status"] == "RELATIONSHIP_UNMEASURED"
    assert proof["certified"] == "olculmedi"


def test_legacy_badge_behavior_is_backward_compatible_without_current_mdl():
    assert (
        fanout.rozet(_certificate(healthy=True), "orders_customer")
        == "olculdu:saglikli"
    )
    assert fanout.rozet({}, "orders_customer") == "olculmedi"


def test_real_wren_schema_exposes_version_bound_fanout_receipts(wren):
    schema = wren.schema()
    relationships = tuple(schema.get("relationships") or ())
    assert relationships

    for relationship in relationships:
        proof = relationship.get("fanout_proof")
        assert isinstance(proof, dict)
        assert proof["relationship"] == relationship["name"]
        assert proof["current_mdl_version"] == wren.mdl_version
        assert relationship["certified"] == proof["certified"]
        if proof["status"] == "HEALTHY":
            assert proof["certificate_mdl_version"] == wren.mdl_version
            assert proof["measured_at"]
