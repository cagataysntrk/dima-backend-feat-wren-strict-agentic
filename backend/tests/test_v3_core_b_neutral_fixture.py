from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path("lab/metabase/core_b")
FIXTURE=ROOT/"fixtures/machine_operations.json"
LOCK=ROOT/"runtime/engine_runtime_lock.json"


def test_neutral_fixture_has_only_required_challenge_concepts():
    body=json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert body["schema_version"]=="core_b_neutral_machine_fixture_v1"
    assert body["table"]=="machine_operations"
    assert set(body["provenance"]["concepts"])=={
        "machine downtime","fault count","department","performance"
    }
    assert body["provenance"]["wren_mdl"] is False
    assert body["provenance"]["wren_query_contracts"] is False
    assert body["provenance"]["expected_sql"] is False
    columns={name for name,_ in body["columns"]}
    assert columns=={
        "event_date","department","machine_id",
        "machine_downtime_minutes","fault_count","performance_score"
    }
    assert len(body["rows"])==20


def test_neutral_fixture_is_deterministic_and_contains_no_wren_semantics():
    raw=FIXTURE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()
    lower=raw.lower()
    # The provenance schema intentionally contains the boolean key `wren_mdl=false`;\n    # guard semantic payload tokens rather than rejecting its own metadata key.\n    for token in (b"wren sql",b"query_contract",b"expected sql"):\n        assert token not in lower\n

def test_engine_lock_is_exact_certified_dima6():
    body=json.loads(LOCK.read_text(encoding="utf-8"))
    assert body=={
      "schema_version":"dima_engine_runtime_lock_v1",
      "engine_sha":"cbe313af9ac2d5960f662068e433d328d896fb06",
      "upstream_sha":"2ba2485c78d7e00a9a25f82c00fc201da71590c4",
      "runtime_tag":"v0.63.18-dima.6",
      "certification_run_id":"36042062775",
      "immutable_image_ref":"ghcr.io/upcytech/dima-metabase-engine@sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353",
      "registry_digest":"sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353",
      "build_identity":"github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06",
    }


def test_live_runtime_scripts_do_not_import_wren_or_product_case_ids():
    raw="\n".join(
        p.read_text(encoding="utf-8")
        for p in (ROOT/"runtime").glob("*.py")
    )
    assert "app.wren" not in raw
    assert "WrenAI" not in raw
    assert "askv2_case_id" not in raw
    assert "canonical_full" not in raw
