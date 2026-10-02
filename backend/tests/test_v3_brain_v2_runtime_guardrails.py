from pathlib import Path
import re
import subprocess
import sys

from lab.metabase.brain_v2.final_probes import (
    FINAL_CAPABILITY_RUNTIME,
    ForwardRuntime,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
LIVE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "dima-brain-v2-phase1-live.yml"
BRAIN_LIVE = BACKEND_ROOT / "lab" / "metabase" / "brain_v2" / "phase1_live.py"
LIVE_SUPPORT = BACKEND_ROOT / "lab" / "metabase" / "brain_v2" / "live_support.py"


def test_all_final_probes_use_brain_v2_runtime():
    assert set(FINAL_CAPABILITY_RUNTIME) == {f"T{i}" for i in range(1, 8)}
    assert set(FINAL_CAPABILITY_RUNTIME.values()) == {
        ForwardRuntime.BRAIN_V2_LANGGRAPH
    }


def test_no_final_probe_imports_or_calls_headless_composer():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    harness = BRAIN_LIVE.read_text(encoding="utf-8")
    support = LIVE_SUPPORT.read_text(encoding="utf-8")
    assert "core_b/phase1_pinpoint_live.py" not in workflow
    assert "phase1_pinpoint_live import" not in harness
    assert "HeadlessProductComposer" not in workflow
    assert "HeadlessProductComposer" not in harness
    assert "from lab.metabase.core_b import live_sentinel" not in harness
    assert "import lab.metabase.core_b.live_sentinel" not in harness
    assert "from lab.metabase.core_b import live_sentinel" not in support
    assert "import lab.metabase.core_b.live_sentinel" not in support
    # Documentation may name the retired class. Import/call-path checks above
    # plus the isolated sys.modules test below enforce the runtime prohibition.


def test_agent_api_disabled_in_final_live():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "MB_AGENT_API_ENABLED=false" in workflow
    assert "MB_AGENT_API_ENABLED=true" not in workflow


def test_live_probe_owner_map_is_single_runtime():
    workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert workflow.count("lab/metabase/brain_v2/phase1_live.py") >= 1
    assert "lab/metabase/core_b/phase1_pinpoint_live.py" not in workflow


def test_final_harness_import_graph_contains_no_legacy_runtime_module():
    code = (
        "import sys; import lab.metabase.brain_v2.phase1_live; "
        "forbidden={'lab.metabase.core_b.live_sentinel',"
        "'lab.metabase.core_b.phase1_pinpoint_live',"
        "'app.v3.product.composition'}; "
        "loaded=sorted(forbidden.intersection(sys.modules)); "
        "assert not loaded, loaded"
    )
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_ROOT,
        check=True,
    )


def test_production_brain_v2_contains_no_benchmark_or_case_ids():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((BACKEND_ROOT / "app" / "v3" / "brain_v2").rglob("*.py"))
    )
    forbidden = (
        r"\bDEV80\b",
        r"\bValidation50\b",
        r"\bHidden50\b",
        r"\b30[-_ ]?case\b",
        r"\bF0[0-9]\b",
        r"\bF10\b",
        r"\bT[1-7]\b",
    )
    for pattern in forbidden:
        assert re.search(pattern, source, flags=re.IGNORECASE) is None, pattern


def test_normal_discovery_has_no_p17_provider_graph_route():
    graph = (
        BACKEND_ROOT / "app" / "v3" / "brain_v2" / "graph.py"
    ).read_text(encoding="utf-8")
    assert 'builder.add_node("p17_discover"' not in graph
    assert '"project_candidates": "project_candidates"' in graph
