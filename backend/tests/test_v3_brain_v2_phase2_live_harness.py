from lab.metabase.brain_v2.final_probes import (
    FINAL_CAPABILITY_RUNTIME,
    PROBES,
    ForwardRuntime,
)
from lab.metabase.brain_v2.final_mechanical import (
    MULTI_INTENT,
    RELATIONSHIP_REPORT,
)


def test_phase2_relationship_report_probe_is_exact_two_turn_contract():
    probe = PROBES[RELATIONSHIP_REPORT]
    assert len(probe["turns"]) == 2
    assert "association/co-movement" in probe["turns"][0]
    assert "Yeni analitik acquisition açma" in probe["turns"][1]


def test_phase2_multi_intent_probe_retains_ranking_relationship_and_report():
    probe = PROBES[MULTI_INTENT]
    assert len(probe["turns"]) == 1
    text = probe["turns"][0]
    assert "sıralayıp" in text
    assert "gözlemsel" in text
    assert "yönetim raporu" in text


def test_t1_t7_live_owner_map_is_one_forward_runtime():
    assert set(FINAL_CAPABILITY_RUNTIME) == {f"T{i}" for i in range(1, 8)}
    assert set(FINAL_CAPABILITY_RUNTIME.values()) == {
        ForwardRuntime.BRAIN_V2_LANGGRAPH
    }
