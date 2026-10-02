from pathlib import Path

from lab.metabase.brain_v2.final_probes import (
    FINAL_CAPABILITY_RUNTIME,
    ForwardRuntime,
)


ROOT = Path(__file__).resolve().parents[2]
LIVE_WORKFLOW = ROOT.parent / ".github" / "workflows" / "dima-brain-v2-phase1-live.yml"
BRAIN_LIVE = ROOT / "lab" / "metabase" / "brain_v2" / "phase1_live.py"


def test_all_final_probes_use_brain_v2_runtime():
    assert set(FINAL_CAPABILITY_RUNTIME) == {f"T{i}" for i in range(1, 8)}
    assert set(FINAL_CAPABILITY_RUNTIME.values()) == {
        ForwardRuntime.BRAIN_V2_LANGGRAPH
    }


def test_no_final_probe_imports_or_calls_headless_composer():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    harness = BRAIN_LIVE.read_text(encoding="utf-8")
    assert "core_b/phase1_pinpoint_live.py" not in workflow
    assert "phase1_pinpoint_live import" not in harness
    assert "HeadlessProductComposer" not in workflow
    assert "HeadlessProductComposer" not in harness


def test_agent_api_disabled_in_final_live():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "MB_AGENT_API_ENABLED=false" in workflow
    assert "MB_AGENT_API_ENABLED=true" not in workflow


def test_live_probe_owner_map_is_single_runtime():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert workflow.count("lab/metabase/brain_v2/phase1_live.py") >= 1
    assert "lab/metabase/core_b/phase1_pinpoint_live.py" not in workflow
