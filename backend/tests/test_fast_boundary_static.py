from __future__ import annotations

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode


FAST_DIR = Path(__file__).resolve().parents[1] / "app" / "fast"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_fast_runtime_has_no_v2_v3_or_wren_imports():
    forbidden_prefixes = (
        "app.v2",
        "app.v3",
        "app.wren",
        "wren",
        "wrenai",
        "wren_core",
    )
    violations: list[str] = []

    for path in sorted(FAST_DIR.glob("*.py")):
        for imported in _imports(path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{path.name}: {imported}")

    assert violations == []


def test_auth_context_rejects_missing_identity_instead_of_admin_fallback():
    with pytest.raises(ValidationError):
        FastMetabaseAuthContext(
            tenant_id="",
            dima_user_id="",
            principal_id="",
            mode=FastMetabaseAuthMode.SESSION,
            secret="secret",
        )


def test_fast_namespace_contains_no_browser_or_service_secret_defaults():
    for path in sorted(FAST_DIR.glob("*.py")):
        source = path.read_text(encoding="utf-8").lower()
        assert "mb_admin_password" not in source
        assert "dimametabaselabadmin" not in source
        assert "service_secret" not in source
