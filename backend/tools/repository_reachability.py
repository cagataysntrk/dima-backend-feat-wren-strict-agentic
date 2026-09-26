#!/usr/bin/env python3
"""Deterministic Python source reachability for canonical repository cleanup."""
from __future__ import annotations

import argparse
import ast
import json
from collections import defaultdict, deque
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
PACKAGE_ROOTS = ("app", "control_plane")

CANONICAL_ROOTS = (
    "app.main",
    "app.v3.research",
    "app.v3.research_product",
    "app.v3.claim_lineage",
    "app.v3.research_manager",
    "app.v3.business_relationship_policy",
    "app.v3.hypothesis_root_cause",
    "app.v3.report_document",
    "app.v3.decision_intelligence",
    "app.v3.decision_adoption",
    "app.v3.action_authorization",
    "app.v3.core_a.action_work",
    "app.v3.core_a.outcome_observation",
    "app.v3.core_a.institutional_memory",
    "app.v3.core_a.watch_signal",
    "control_plane.models",
    "control_plane.authorize",
    "control_plane.db",
)

FINAL_CERT_PATH_HINTS = (
    "tests/test_v3_",
    "tests/test_repository_hygiene.py",
    "eval/core_b/",
)


def module_for(path: Path) -> str | None:
    rel = path.relative_to(BACKEND)
    parts = list(rel.with_suffix("").parts)
    if not parts or parts[0] not in PACKAGE_ROOTS:
        return None
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def discover_modules() -> tuple[dict[str, Path], dict[Path, str]]:
    by_module: dict[str, Path] = {}
    by_path: dict[Path, str] = {}
    for root in PACKAGE_ROOTS:
        for path in (BACKEND / root).rglob("*.py"):
            module = module_for(path)
            if not module:
                continue
            by_module[module] = path
            by_path[path] = module
    return by_module, by_path


def resolve_from(current: str, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module
    package = current.split(".")[:-1]
    up = node.level - 1
    if up > len(package):
        return None
    prefix = package[: len(package) - up]
    if node.module:
        prefix.extend(node.module.split("."))
    return ".".join(prefix)


def imports_for(module: str, path: Path, known: set[str]) -> tuple[set[str], list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    deps: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in known:
                    deps.add(name)
                else:
                    pieces = name.split(".")
                    for cut in range(len(pieces) - 1, 0, -1):
                        candidate = ".".join(pieces[:cut])
                        if candidate in known:
                            deps.add(candidate)
                            break
        elif isinstance(node, ast.ImportFrom):
            base = resolve_from(module, node)
            if not base:
                continue
            if base in known:
                deps.add(base)
            for alias in node.names:
                candidate = f"{base}.{alias.name}" if base else alias.name
                if candidate in known:
                    deps.add(candidate)
        elif isinstance(node, ast.Call):
            target = node.func
            name = None
            if isinstance(target, ast.Name):
                name = target.id
            elif isinstance(target, ast.Attribute):
                name = target.attr
            if name in {"__import__", "import_module"}:
                value = None
                if node.args and isinstance(node.args[0], ast.Constant):
                    value = node.args[0].value
                dynamic.append(str(value) if value is not None else "<dynamic>")
    return deps, dynamic


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    modules, _ = discover_modules()
    known = set(modules)
    graph: dict[str, set[str]] = {}
    dynamic: dict[str, list[str]] = {}
    for module, path in modules.items():
        deps, dyn = imports_for(module, path, known)
        graph[module] = deps
        if dyn:
            dynamic[module] = dyn

    missing_roots = sorted(root for root in CANONICAL_ROOTS if root not in known)
    if missing_roots:
        raise SystemExit(f"missing canonical roots: {missing_roots}")

    reachable: set[str] = set()
    queue = deque(CANONICAL_ROOTS)
    while queue:
        module = queue.popleft()
        if module in reachable:
            continue
        reachable.add(module)
        queue.extend(sorted(graph.get(module, ()) - reachable))

    all_modules = set(modules)
    legacy = sorted(all_modules - reachable)
    unresolved_dynamic = {
        module: values
        for module, values in dynamic.items()
        if module in reachable
    }

    result = {
        "canonical_roots": list(CANONICAL_ROOTS),
        "canonical_reachable": sorted(reachable),
        "legacy_unreachable": legacy,
        "unresolved_dynamic_import": unresolved_dynamic,
        "counts": {
            "all_modules": len(all_modules),
            "canonical_reachable": len(reachable),
            "legacy_unreachable": len(legacy),
        },
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for key in ("canonical_reachable", "legacy_unreachable"):
            print(f"[{key}]")
            for item in result[key]:
                print(item)
        print("[unresolved_dynamic_import]")
        print(json.dumps(unresolved_dynamic, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
