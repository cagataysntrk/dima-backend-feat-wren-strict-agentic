from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"

FORBIDDEN_PATHS = (
    "WrenAI-main",
    "belgeler",
    "dima-frontend-demo-master",
    "backend/admin-dev",
    "backend/admin_app",
    "backend/backend/lab",
    "backend/demo",
    "backend/docs",
    "lab/curl",
    "backend/app/v2",
)

FORBIDDEN_ROOT_DOCS = (
    "DIMA-METABASE-DENETIM.md",
    "DIMA-METABASE-HANDOFF.md",
    "DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md",
    "DIMA-METABASE-OPERASYON.md",
    "DIMA-METABASE-SUPERVISOR-HANDOFF.md",
    "OPERASYON-DENETIM.md",
    "OPERASYON-DURUM.md",
    "OPERASYON.md",
)

FORBIDDEN_ROOT_SCRIPTS = tuple(
    f"backend/{name}.py"
    for name in (
        "deney","dogrula","izole","kontrol","kova","olc","olc2","prune",
        "r1","r1d","rrf","rrf2","tara","tehis","z79",
    )
)

ACTIVE_AUTHORITY = (
    BACKEND / "CLAUDE.md",
    BACKEND / "AGENTS.md",
    BACKEND / "MIMARI.md",
    BACKEND / "belgeler" / "metabase" / "DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md",
    BACKEND / "belgeler" / "metabase" / "DIMA_METABASE_CURRENT_PRODUCT_PLAN.md",
    BACKEND / "belgeler" / "metabase" / "DIMA_METABASE_CURRENT_HANDOFF.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "DIMA-METABASE-DURUM.md",
)


def test_forbidden_legacy_paths_are_absent():
    for relative in FORBIDDEN_PATHS:
        assert not (REPO_ROOT / relative).exists(), relative


def test_root_is_one_story():
    for relative in FORBIDDEN_ROOT_DOCS:
        assert not (REPO_ROOT / relative).exists(), relative
    assert (REPO_ROOT / "DIMA-METABASE-DURUM.md").exists()


def test_old_frontend_and_ui_roots_are_absent():
    for relative in ("frontend", "web", "ui", "dima-frontend-demo-master"):
        assert not (REPO_ROOT / relative).exists(), relative


def test_old_v2_eval_corpus_is_absent():
    eval_root = BACKEND / "eval"
    if eval_root.exists():
        stale = [
            p for p in eval_root.rglob("*")
            if p.is_file() and (
                p.name.startswith("v2_day")
                or "day6_5" in p.name.lower()
                or "j1" in p.name.lower()
            )
        ]
        assert not stale, stale


def test_unclassified_root_utility_scripts_are_absent():
    for relative in FORBIDDEN_ROOT_SCRIPTS:
        assert not (REPO_ROOT / relative).exists(), relative


def test_active_developer_authority_is_canonical():
    claude=(BACKEND/"CLAUDE.md").read_text(encoding="utf-8")
    agents=(BACKEND/"AGENTS.md").read_text(encoding="utf-8")
    mimari=(BACKEND/"MIMARI.md").read_text(encoding="utf-8")
    for text in (claude,agents,mimari):
        assert "feat/dima-metabase-platform" in text
        assert "Metabase" in text
        assert "Core B" in text
    for token in (
        "belgeler/plan/",
        "feat/ask-v2-mvp",
        "Wren incumbent",
        "CURRENT CONTINUATION — POST-J1B",
        "Day6.5",
    ):
        assert token not in claude
        assert token not in agents
    assert "Wren remains incumbent" not in mimari
    assert "Wren-vs-Platform bake-off" not in mimari


def test_current_product_plan_has_no_forward_wren_bakeoff():
    text=(BACKEND/"belgeler"/"metabase"/"DIMA_METABASE_CURRENT_PRODUCT_PLAN.md").read_text(encoding="utf-8")
    current=text.split("## HISTORICAL / SUPERSEDED",1)[0]
    assert "Wren-vs-Platform bake-off" not in current
    normalized = " ".join(current.split())
    assert "DEV80 is not run" in normalized


def test_active_docs_do_not_reference_deleted_current_paths():
    forbidden=(
        "belgeler/plan/",
        "WrenAI-main/",
        "dima-frontend-demo-master/",
        "DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md",
        "DIMA-METABASE-SUPERVISOR-HANDOFF.md",
        "DIMA-METABASE-OPERASYON.md",
        "OPERASYON.md",
    )
    for path in ACTIVE_AUTHORITY:
        text=path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (path,token)


def test_active_workflows_have_no_deleted_path_guards():
    workflow_root = REPO_ROOT / ".github" / "workflows"
    forbidden=(
        "WrenAI-main/",
        "dima-frontend-demo-master/",
        "backend/admin-dev/",
        "backend/admin_app/",
        "backend/backend/lab/",
        "backend/demo/",
        "backend/docs/",
        "lab/curl/",
        "DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md",
    )
    for path in workflow_root.glob("*.yml"):
        text=path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (path.name, token)


def test_canonical_manifest_has_no_wren_runtime_dependency():
    text = (BACKEND / "pyproject.toml").read_text(encoding="utf-8").lower()
    assert '"wrenai' not in text
    assert '"wren-core-py' not in text
    assert "fastapi bridge exposing the wren" not in text


def test_canonical_main_has_no_legacy_runtime_imports():
    text = (BACKEND / "app" / "main.py").read_text(encoding="utf-8")
    for token in (
        "WrenService","ask_v2","manager_lab","compose_and_build",
        "company_registry","app.state.wren",
    ):
        assert token not in text


def test_ask_v2_source_namespace_is_absent():
    assert not (BACKEND / "app" / "v2").exists()
    assert not (BACKEND / "app" / "v3" / "legacy_contract.py").exists()


def test_wren_substrate_source_is_absent():
    assert not (BACKEND / "app" / "v3" / "substrate" / "wren.py").exists()
    assert not (BACKEND / "app" / "wren_service.py").exists()


def test_legacy_top_level_runtime_is_absent():
    allowed={
        "__init__.py","config.py","istek_kimligi.py","logging_setup.py","main.py"
    }
    extras=sorted(
        p.name for p in (BACKEND/"app").glob("*.py")
        if p.name not in allowed
    )
    assert extras == [], extras
    router_extras=sorted(
        p.name for p in (BACKEND/"app"/"routers").glob("*.py")
        if p.name not in {"__init__.py","health.py"}
    )
    assert router_extras == [], router_extras
    assert not (BACKEND/"app"/"email").exists()


def test_engine_gitlink_is_documented_exactly():
    gitmodules = (REPO_ROOT / ".gitmodules").read_text(encoding="utf-8")
    assert "engine/metabase" in gitmodules
    roadmap = (
        BACKEND / "belgeler" / "metabase" / "DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md"
    ).read_text(encoding="utf-8")
    assert "cbe313af9ac2d5960f662068e433d328d896fb06" in roadmap


def test_default_action_registry_and_execution_boundary_remain_closed():
    action = (BACKEND / "app" / "v3" / "action_authorization.py").read_text(encoding="utf-8")
    authorize = (BACKEND / "control_plane" / "authorize.py").read_text(encoding="utf-8")
    assert "DEFAULT_ACTION_CAPABILITY_REGISTRY = ActionCapabilityRegistry()" in action
    assert '"action:execute"' not in authorize
    assert not (BACKEND / "app" / "v3" / "action_execution.py").exists()


def test_readmes_describe_only_canonical_product():
    for path in (REPO_ROOT / "README.md", BACKEND / "README.md"):
        text = path.read_text(encoding="utf-8")
        for token in (
            "WrenAI-main/","dima-frontend-demo-master/","backend/demo/","belgeler/00-INDEKS",
        ):
            assert token not in text, (path, token)
