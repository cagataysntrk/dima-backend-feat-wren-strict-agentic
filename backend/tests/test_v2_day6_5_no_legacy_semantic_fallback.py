"""Day 6.5 anti-regression guard for the authoritative semantic hot path.

This is intentionally scoped. It does NOT ban regular expressions repository-wide; it
prevents natural-language semantic authority modules from regaining the legacy
fuzzy/morphology/regex resolver seam.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.v2.manager_semantics import ManagerSemanticResolutionAdapter


ROOT = Path(__file__).resolve().parents[1]

AUTHORITATIVE_SEMANTIC_MODULES = (
    "app/v2/manager_semantics.py",
    "app/v2/manager_preacceptance.py",
    "app/v2/semantic_linker.py",
    "app/v2/semantic_retriever.py",
    "app/v2/temporal_intent.py",
)

FORBIDDEN_IMPORT_ROOTS = {
    "app.v2.resolver",
    "difflib",
    "rapidfuzz",
    "py_rust_stemmers",
    "re",
}

FORBIDDEN_SYMBOLS = {
    "SequenceMatcher",
    "SnowballStemmer",
    "_FUZZY",
}


def _tree(relative: str) -> ast.AST:
    return ast.parse((ROOT / relative).read_text(encoding="utf-8"))


def _imports(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_manager_hot_path_has_no_legacy_resolver_dependency():
    signature = inspect.signature(ManagerSemanticResolutionAdapter.__init__)
    assert "resolver" not in signature.parameters

    manager_semantics = (ROOT / "app/v2/manager_semantics.py").read_text(
        encoding="utf-8"
    )
    manager_lab = (ROOT / "app/v2/manager_lab.py").read_text(encoding="utf-8")

    assert "from app.v2.resolver import" not in manager_semantics
    assert "app.v2.resolver" not in _imports(_tree("app/v2/manager_semantics.py"))
    assert "_legacy_resolver" not in manager_semantics

    assert "from app.v2.resolver import" not in manager_lab
    assert "SemanticResolver(" not in manager_lab


def test_authoritative_semantic_modules_cannot_import_legacy_language_heuristics():
    violations: list[str] = []

    for relative in AUTHORITATIVE_SEMANTIC_MODULES:
        tree = _tree(relative)
        imports = _imports(tree)
        for module in sorted(imports):
            if any(
                module == forbidden or module.startswith(forbidden + ".")
                for forbidden in FORBIDDEN_IMPORT_ROOTS
            ):
                violations.append(f"{relative}: forbidden import {module}")

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_SYMBOLS:
                violations.append(
                    f"{relative}: forbidden semantic symbol {node.id}"
                )
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "re"
                and node.attr in {"search", "match", "fullmatch", "compile", "findall"}
            ):
                violations.append(
                    f"{relative}: forbidden semantic regex call re.{node.attr}"
                )

    assert violations == []


def test_legacy_resolver_may_exist_only_outside_manager_authority_boundary():
    legacy = ROOT / "app/v2/resolver.py"
    assert legacy.exists(), "compatibility resolver may remain for non-Manager paths"

    manager_modules = (
        ROOT / "app/v2/manager_semantics.py",
        ROOT / "app/v2/manager_lab.py",
    )
    for path in manager_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert "app.v2.resolver" not in _imports(tree)
