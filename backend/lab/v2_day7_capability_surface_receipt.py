"""Provider-free Day7 capability/task/tool surface consistency receipt.

Diagnostic only. This module does not alter Manager capability policy, task
materialization, tool registration, or execution behavior.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.v2.manager_models import ManagerCapabilityKey
from app.v2.manager_policy import ManagerCapabilityRegistry
from app.v2.research_tasks import ResearchTaskService
from app.v2.research_tools import ResearchToolRegistry

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "lab" / "reports" / "v2_day7_capability_surface_receipt.json"


def build_receipt() -> dict:
    capabilities = ManagerCapabilityRegistry()
    task_map = dict(ResearchTaskService._TASK_KIND_BY_CAPABILITY)
    tool_specs = dict(ResearchToolRegistry._SPECS)

    rows = []
    for capability in ManagerCapabilityKey:
        spec = capabilities.get(capability)
        task_kind = task_map.get(capability)
        tool_ids = []
        if task_kind is not None:
            tool_ids = sorted(
                tool_id
                for tool_id, tool_spec in tool_specs.items()
                if task_kind in tool_spec.contract.accepted_task_kinds
            )

        if not spec.executable:
            disposition = "NON_EXECUTABLE_DECLARED"
        elif task_kind is None:
            disposition = "EXECUTABLE_NO_TASK_MAPPING"
        elif len(tool_ids) == 0:
            disposition = "TASK_MAPPING_NO_DECLARED_TOOL"
        elif len(tool_ids) == 1:
            disposition = "DIRECT_DAY7_EXECUTION"
        else:
            disposition = "AMBIGUOUS_MULTI_TOOL_MAPPING"

        rows.append(
            {
                "capability": capability.value,
                "lane": spec.lane.value,
                "executable": bool(spec.executable),
                "task_kind": task_kind.value if task_kind is not None else None,
                "declared_tool_ids": tool_ids,
                "disposition": disposition,
            }
        )

    unresolved = [
        row
        for row in rows
        if row["executable"]
        and row["disposition"] != "DIRECT_DAY7_EXECUTION"
    ]
    return {
        "kind": "dima_v2_day7_capability_surface_receipt",
        "provider_free": True,
        "rows": rows,
        "unresolved_executable_surfaces": unresolved,
    }


def main() -> int:
    payload = build_receipt()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
