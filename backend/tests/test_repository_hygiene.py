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

FORBIDDEN_WORKFLOW_REFERENCES = (
    "WrenAI-main/",
    "dima-frontend-demo-master/",
    "backend/admin-dev/",
    "backend/admin_app/",
    "backend/backend/lab/",
    "backend/demo/",
    "backend/docs/",
    "lab/curl/",
)


def test_forbidden_legacy_paths_are_absent():
    for relative in FORBIDDEN_PATHS:
        assert not (REPO_ROOT / relative).exists(), relative


def test_old_frontend_and_ui_roots_are_absent():
    for relative in ("frontend", "web", "ui", "dima-frontend-demo-master"):
        assert not (REPO_ROOT / relative).exists(), relative


def test_active_workflows_have_no_deleted_path_guards():
    workflow_root = REPO_ROOT / ".github" / "workflows"
    for path in workflow_root.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_WORKFLOW_REFERENCES:
            assert token not in text, (path.name, token)


def test_canonical_manifest_has_no_wren_runtime_dependency():
    text = (BACKEND / "pyproject.toml").read_text(encoding="utf-8").lower()
    assert '"wrenai' not in text
    assert '"wren-core-py' not in text
    assert "fastapi bridge exposing the wren" not in text


def test_canonical_main_has_no_legacy_runtime_imports():
    text = (BACKEND / "app" / "main.py").read_text(encoding="utf-8")
    for token in (
        "WrenService",
        "ask_v2",
        "manager_lab",
        "compose_and_build",
        "company_registry",
        "app.state.wren",
    ):
        assert token not in text


def test_ask_v2_source_namespace_is_absent():
    assert not (BACKEND / "app" / "v2").exists()
    assert not (BACKEND / "app" / "v3" / "legacy_contract.py").exists()


def test_wren_substrate_source_is_absent():
    assert not (BACKEND / "app" / "v3" / "substrate" / "wren.py").exists()
    assert not (BACKEND / "app" / "wren_service.py").exists()


def test_engine_gitlink_is_documented_exactly():
    gitmodules = (REPO_ROOT / ".gitmodules").read_text(encoding="utf-8")
    assert "engine/metabase" in gitmodules
    roadmap = (
        BACKEND
        / "belgeler"
        / "metabase"
        / "DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md"
    ).read_text(encoding="utf-8")
    assert "cbe313af9ac2d5960f662068e433d328d896fb06" in roadmap


def test_default_action_registry_and_execution_boundary_remain_closed():
    action = (BACKEND / "app" / "v3" / "action_authorization.py").read_text(
        encoding="utf-8"
    )
    authorize = (BACKEND / "control_plane" / "authorize.py").read_text(
        encoding="utf-8"
    )
    assert "DEFAULT_ACTION_CAPABILITY_REGISTRY = ActionCapabilityRegistry()" in action
    assert '"action:execute"' not in authorize
    assert not (BACKEND / "app" / "v3" / "action_execution.py").exists()


def test_readmes_describe_only_canonical_product():
    for path in (REPO_ROOT / "README.md", BACKEND / "README.md"):
        text = path.read_text(encoding="utf-8")
        for token in (
            "WrenAI-main/",
            "dima-frontend-demo-master/",
            "backend/demo/",
            "belgeler/00-INDEKS",
        ):
            assert token not in text, (path, token)
