#!/usr/bin/env python3
"""Deterministic source reachability/classification for canonical cleanup."""
from __future__ import annotations

import argparse
import ast
import json
from collections import deque
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

FINAL_CERT_ROOTS = (
    "app.v3.action_connectors.resend_email",
    "app.v3.core_a.ux_foundations",
    "app.v3.entity_value_gate",
    "app.v3.hypothesis_root_cause_provider",
    "app.v3.native_standard",
    "app.v3.research_followup",
    "app.v3.research_manager_provider",
    "app.v3.resource_provisioning",
    "app.v3.resource_transport",
    "app.v3.security_identity",
    "app.v3.semantic_equivalence",
    "app.v3.semantic_import",
    "app.v3.substrate.base",
    "app.v3.substrate.metabase.adapter",
    "app.v3.substrate.metabase.execution_adapter",
    "app.v3.substrate.metabase.p3a_fixture",
    "app.v3.substrate.metabase.p3a_models",
    "app.v3.substrate.metabase.p3a_preflight",
)

EXTRA_TEST_FILES = (
    "tests/test_repository_hygiene.py",
    "tests/test_v3_control_plane_security.py",
)


def module_for(path: Path) -> str | None:
    rel = path.relative_to(BACKEND)
    parts = list(rel.with_suffix("").parts)
    if not parts or parts[0] not in PACKAGE_ROOTS:
        return None
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def discover_modules() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for root in PACKAGE_ROOTS:
        for path in (BACKEND / root).rglob("*.py"):
            module = module_for(path)
            if module:
                out[module] = path
    return out


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
                pieces = alias.name.split(".")
                for cut in range(len(pieces), 0, -1):
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
                candidate = f"{base}.{alias.name}"
                if candidate in known:
                    deps.add(candidate)
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else None
            )
            if name in {"__import__", "import_module"}:
                value = None
                if node.args and isinstance(node.args[0], ast.Constant):
                    value = node.args[0].value
                dynamic.append(str(value) if value is not None else "<dynamic>")
    return deps, dynamic


def closure(roots: set[str], graph: dict[str, set[str]]) -> set[str]:
    reached: set[str] = set()
    queue = deque(sorted(roots))
    while queue:
        module = queue.popleft()
        if module in reached:
            continue
        reached.add(module)
        queue.extend(sorted(graph.get(module, ()) - reached))
    return reached


def retained_test_roots(known: set[str]) -> set[str]:
    paths = sorted((BACKEND / "tests").glob("test_v3_*.py"))
    paths.extend(BACKEND / item for item in EXTRA_TEST_FILES)
    roots: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pieces = alias.name.split(".")
                    for cut in range(len(pieces), 0, -1):
                        candidate = ".".join(pieces[:cut])
                        if candidate in known:
                            roots.add(candidate)
                            break
            elif isinstance(node, ast.ImportFrom):
                if not node.module:
                    continue
                if node.module in known:
                    roots.add(node.module)
                for alias in node.names:
                    candidate = f"{node.module}.{alias.name}"
                    if candidate in known:
                        roots.add(candidate)
    return roots


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    modules = discover_modules()
    known = set(modules)
    graph: dict[str, set[str]] = {}
    dynamic: dict[str, list[str]] = {}
    for module, path in modules.items():
        deps, dyn = imports_for(module, path, known)
        graph[module] = deps
        if dyn:
            dynamic[module] = dyn

    missing_canonical = sorted(root for root in CANONICAL_ROOTS if root not in known)
    missing_final = sorted(root for root in FINAL_CERT_ROOTS if root not in known)
    if missing_canonical or missing_final:
        raise SystemExit(
            f"missing roots: canonical={missing_canonical} final_cert={missing_final}"
        )

    canonical = closure(set(CANONICAL_ROOTS), graph)
    final_cert = closure(set(FINAL_CERT_ROOTS), graph) - canonical
    test_roots = retained_test_roots(known)
    test_only = closure(test_roots, graph) - canonical - final_cert
    classified = canonical | final_cert | test_only
    legacy = sorted(known - classified)

    unresolved_dynamic = {
        module: values
        for module, values in dynamic.items()
        if module in classified
    }

    result = {
        "canonical_roots": list(CANONICAL_ROOTS),
        "final_cert_roots": list(FINAL_CERT_ROOTS),
        "test_roots": sorted(test_roots),
        "canonical_reachable": sorted(canonical),
        "final_cert_required": sorted(final_cert),
        "test_only_required": sorted(test_only),
        "legacy_unreachable": legacy,
        "unresolved_dynamic_import": unresolved_dynamic,
        "counts": {
            "all_modules": len(known),
            "canonical_reachable": len(canonical),
            "final_cert_required": len(final_cert),
            "test_only_required": len(test_only),
            "legacy_unreachable": len(legacy),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    for key in (
        "canonical_reachable",
        "final_cert_required",
        "test_only_required",
        "legacy_unreachable",
    ):
        print(f"[{key}]")
        for item in result[key]:
            print(item)
    print("[unresolved_dynamic_import]")
    print(json.dumps(unresolved_dynamic, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
