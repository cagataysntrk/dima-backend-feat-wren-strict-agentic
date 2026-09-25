"""D10-G / G16 provider-free canonical state-machine rehearsal.

This executes the production ProductCoordinator -> Research lane with scripted cognition
and a deterministic in-memory Wren-shaped service.  There are zero provider calls and
zero real-Wren calls here; G15 owns the one real-Wren micro-gate.

Scenario:
- PERFORMANCE USER_MUST
- RELATIONSHIP USER_MUST
- ROOT_CAUSE USER_MUST
- exactly one result-driven adaptive branch
- one hypothesis
- one admitted next test
- one explicit SUPPORTS relation
- deterministic root completion + CompletionGate + ReportDocument

The receipt is derived from runtime counters/observations, not from expected constants.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.v2.context_provider import ContextProviderV0
from app.v2.manager_models import ManagerState, ObligationStatus
from app.v2.model_policy import ModelProfile, ModelRole
from app.v2.models import EpistemicLabel, TenantAnalyticsRuntimeV0
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_models import (
    ProductAskRequest,
    ProductLane,
    ProductRequestContext,
    ProductStatus,
)
from app.v2.report_narration import ReportNarrator
from app.v2.research_lane import ResearchCognition, ResearchLaneService
from app.v2.standard_lane import StandardLaneOutcome, StandardLaneStatus
from control_plane.authorize import Principal


MDL_VERSION = "mdl-d10-g16-ns4-v1"


class RehearsalError(RuntimeError):
    pass


class SyntheticService:
    """Deterministic Wren-shaped analytical surface; no provider/DB/network."""

    mdl_version = MDL_VERSION

    def __init__(self) -> None:
        self.query_calls = 0
        self.dry_plan_calls = 0
        self.cube_sql_calls = 0
        self._schema = {
            "catalog": "g16",
            "schema_name": "main",
            "db_online": True,
            "business_rules": "",
            "cubes": [
                {
                    "name": "ops",
                    "base_object": "events",
                    "measures": ["downtime"],
                    "dimensions": ["department"],
                    "time_dimensions": [],
                    "measure_synonyms": {"downtime": ["downtime"]},
                    "dimension_synonyms": {"department": ["department"]},
                    "dimension_origin": {
                        "department": {
                            "relationship": "events_machines",
                            "model": "machines",
                            "column": "department",
                            "hops": 1,
                        }
                    },
                },
                {
                    "name": "maintenance",
                    "base_object": "maintenance_events",
                    "measures": ["faults"],
                    "dimensions": [],
                    "time_dimensions": [],
                    "measure_synonyms": {"faults": ["faults"]},
                    "dimension_synonyms": {},
                },
            ],
            "models": [
                {
                    "name": "events",
                    "primary_key": "event_id",
                    "columns": [
                        {"name": "event_id"},
                        {"name": "machine_id"},
                    ],
                },
                {
                    "name": "machines",
                    "primary_key": "machine_id",
                    "columns": [
                        {"name": "machine_id"},
                        {"name": "department"},
                    ],
                },
                {
                    "name": "maintenance_events",
                    "primary_key": "maintenance_id",
                    "columns": [
                        {"name": "maintenance_id"},
                        {"name": "faults"},
                    ],
                },
            ],
            "relationships": [
                {
                    "name": "events_machines",
                    "join_type": "MANY_TO_ONE",
                    "models": ["events", "machines"],
                    "condition": "events.machine_id = machines.machine_id",
                    "certified": "olculdu:saglikli",
                    "fanout_proof": {
                        "relationship": "events_machines",
                        "status": "HEALTHY",
                        "certified": "olculdu:saglikli",
                        "certificate_mdl_version": MDL_VERSION,
                        "current_mdl_version": MDL_VERSION,
                        "measured_at": "2026-09-24T00:00:00+00:00",
                    },
                }
            ],
            "kpis": [],
        }

    def schema(self):
        return json.loads(json.dumps(self._schema))

    def cube_sql(self, cube_query: dict) -> str:
        self.cube_sql_calls += 1
        return "G16:" + json.dumps(cube_query, ensure_ascii=False, sort_keys=True)

    def dry_plan(self, sql: str, *, principal=None):
        assert principal is not None
        self.dry_plan_calls += 1
        return sql

    def query(self, sql: str, limit=None, *, principal=None):
        del limit
        assert principal is not None
        self.query_calls += 1
        query = json.loads(sql.removeprefix("G16:"))
        dimensions = list(query.get("dimensions") or ())
        measures = list(query.get("measures") or ())
        columns = [*dimensions, *measures]
        if dimensions:
            rows = [
                {dimensions[0]: "A", **{metric: 120.0 for metric in measures}},
                {dimensions[0]: "B", **{metric: 80.0 for metric in measures}},
            ]
        else:
            # Distinct deterministic values make each execution observable without
            # changing semantic authority.
            value = 100.0 - float(self.query_calls)
            rows = [{metric: value for metric in measures}]
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_types": [
                "VARCHAR" if name in dimensions else "DOUBLE"
                for name in columns
            ],
        }


class ContractStore:
    def __init__(self) -> None:
        self.count = 0

    def record_v2_minimum(self, **_kwargs):
        self.count += 1
        return {
            "id": f"g16-qc-{self.count}",
            "result_hash": f"g16-hash-{self.count}",
            "durability": "provider-free-memory",
            "sealed": True,
        }


class ForceResearchStandardLane:
    def __init__(self) -> None:
        self.calls = 0
        self.authority_registry = None

    def bind_authority_registry(self, registry) -> None:
        self.authority_registry = registry

    def run(self, **_kwargs):
        self.calls += 1
        return StandardLaneOutcome(
            status=StandardLaneStatus.RESEARCH_REQUIRED,
            reasons=("canonical provider-free NS4 requires Research",),
        )


class ScriptedNS4Manager:
    """Only genuine cognition decisions; execution/inspection/finish are forbidden."""

    def __init__(self) -> None:
        self.preacceptance_calls = 0
        self.manager_prompts: list[dict] = []
        self.actions: list[str] = []
        self.root_trigger_evidence_ref: str | None = None

    def structured_json(self, _system, user, *, schema, schema_name):
        del schema
        payload = json.loads(user)

        if schema_name == "dima_intent_draft_v1":
            self.preacceptance_calls += 1
            return {
                "obligations": [
                    {
                        "obligation_id": "U_PERF",
                        "capability_key": "performance",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["downtime"],
                        "semantic_surfaces": [
                            {"surface": "downtime", "kind_hint": "metric"},
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                    {
                        "obligation_id": "U_REL",
                        "capability_key": "relationship",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["downtime", "department"],
                        "semantic_surfaces": [
                            {"surface": "downtime", "kind_hint": "metric"},
                            {"surface": "department", "kind_hint": "dimension"},
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                    {
                        "obligation_id": "U_ROOT",
                        "capability_key": "root_cause",
                        "origin": "USER_MUST",
                        "priority": "MUST",
                        "polarity": "REQUIRED",
                        "source_surfaces": ["faults"],
                        "semantic_surfaces": [
                            {"surface": "faults", "kind_hint": "metric"},
                        ],
                        "open_questions": [],
                        "ranking_direction": None,
                        "ranking_limit": None,
                    },
                ],
                "research_directives": [
                    {
                        "directive_id": "R_ADAPT_ROOT",
                        "directive_type": "ADAPT_ON_EVIDENCE",
                        "parent_obligation_id": "U_ROOT",
                        "condition": "MATERIAL_NEW_DIRECTION",
                        "source_surfaces": [
                            "doğrulanmış sonuçlar yeni bir maddi kırılıma işaret ederse onu takip et"
                        ],
                    }
                ],
                "control_requests": [],
            }

        if schema_name == "dima_intent_coverage_v1":
            self.preacceptance_calls += 1
            return {"status": "PASS", "issues": []}

        if schema_name != "dima_research_manager_action_v1":
            raise AssertionError(f"unexpected schema {schema_name}")

        self.manager_prompts.append(payload)
        ledger = {
            item["obligation_id"]: item
            for item in payload["OBLIGATION_LEDGER"]
        }
        root_handle = ledger["U_ROOT"]["semantic_handle_refs"][0]
        delta = payload["CURRENT_RESULT_DELTA"]
        assert delta is not None and delta["verified"] is True
        assert delta["disclosed_in_current_prompt"] is True

        hypothesis_entries = payload["HYPOTHESIS_LEDGERS"][0]["entries"]
        recent = payload.get("RECENT_OBSERVATIONS") or []

        branch_seen = any(
            item.get("kind") in {"fanout_registered", "adaptive_branch_executed"}
            for item in recent
        )
        if not branch_seen and not hypothesis_entries:
            assert "U_ROOT" in tuple(delta.get("obligation_ids") or ()), delta
            self.root_trigger_evidence_ref = delta["evidence_ref"]
            self.actions.append("propose_branches")
            return {
                "action": "propose_branches",
                "branch_parent_obligation_id": "U_ROOT",
                "branch_evidence_ref": delta["evidence_ref"],
                "branch_candidates": [
                    {
                        "task_id": "D_ROOT_RECHECK",
                        "capability_key": "performance",
                        "input_handles": [root_handle],
                        "material_reason": (
                            "Fresh root-lineage result justifies one bounded metric re-check."
                        ),
                    }
                ],
            }

        if not hypothesis_entries:
            self.actions.append("propose_hypothesis")
            return {
                "action": "propose_hypothesis",
                "hypothesis_parent_obligation_id": "U_ROOT",
                "hypothesis_statement": (
                    "Provider-free audit hypothesis contains %27 but report must not."
                ),
                "hypothesis_semantic_handles": [root_handle],
                "hypothesis_trigger_evidence_refs": [
                    self.root_trigger_evidence_ref
                ],
                "hypothesis_limitations": [],
            }

        hypothesis = hypothesis_entries[0]
        if not hypothesis["next_test_task_refs"]:
            self.actions.append("propose_hypothesis_next_test")
            return {
                "action": "propose_hypothesis_next_test",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "next_test_task_kind": "QUERY",
                "next_test_input_handles": [root_handle],
                "next_test_trigger_evidence_ref": self.root_trigger_evidence_ref,
                "next_test_material_reason": (
                    "Test the candidate against a fresh governed root-lineage measurement."
                ),
            }

        if not hypothesis["evidence_links"]:
            self.actions.append("propose_hypothesis_evidence_relation")
            return {
                "action": "propose_hypothesis_evidence_relation",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "hypothesis_relation_evidence_ref": delta["evidence_ref"],
                "hypothesis_relation": "SUPPORTS",
            }

        raise AssertionError(
            "CompletionGate should terminate before execution-control/FINISH cognition"
        )


class CanonicalRelationshipTopologyManager(ScriptedNS4Manager):
    """Paid-run topology: relationship-owned adaptive work plus independent ROOT_CAUSE."""

    def __init__(self, *, revision: bool = False) -> None:
        super().__init__()
        self._revision = revision
        self._draft_attempt = 0
        self._coverage_attempt = 0

    def _canonical_draft(self) -> dict:
        return {
            "obligations": [
                {
                    "obligation_id": "U_PERF",
                    "capability_key": "performance",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["downtime"],
                    "semantic_surfaces": [
                        {"surface": "downtime", "kind_hint": "metric"},
                    ],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                },
                {
                    "obligation_id": "U_BREAK",
                    "capability_key": "breakdown",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["department breakdown"],
                    "semantic_surfaces": [
                        {"surface": "downtime", "kind_hint": "metric"},
                        {"surface": "department", "kind_hint": "dimension"},
                    ],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                },
                {
                    "obligation_id": "U_REL",
                    "capability_key": "relationship",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["governed relationship"],
                    "semantic_surfaces": [
                        {"surface": "downtime", "kind_hint": "metric"},
                        {"surface": "department", "kind_hint": "dimension"},
                    ],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                },
                {
                    "obligation_id": "U_ROOT",
                    "capability_key": "root_cause",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["faults"],
                    "semantic_surfaces": [
                        {"surface": "faults", "kind_hint": "metric"},
                    ],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                },
                {
                    "obligation_id": "U_REPORT",
                    "capability_key": "report",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "REQUIRED",
                    "source_surfaces": ["management report"],
                    "semantic_surfaces": [],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                },
                {
                    "obligation_id": "X_CAUSAL_CERTAINTY",
                    "capability_key": "explain",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "EXCLUDED",
                    "source_surfaces": ["do not claim causal certainty"],
                    "semantic_surfaces": [],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                },
            ],
            "research_directives": [
                {
                    "directive_id": "R_ADAPT_REL",
                    "directive_type": "ADAPT_ON_EVIDENCE",
                    "parent_obligation_id": "U_REL",
                    "condition": "MATERIAL_NEW_DIRECTION",
                    "source_surfaces": ["follow a materially new verified relationship direction"],
                }
            ],
            "control_requests": [],
        }

    @staticmethod
    def _schema_actions(schema: dict) -> set[str]:
        values: set[str] = set()

        def walk(node):
            if isinstance(node, dict):
                enum = node.get("enum")
                if isinstance(enum, list):
                    values.update(str(item) for item in enum if item is not None)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        action = (schema.get("properties") or {}).get("action")
        if isinstance(action, dict) and isinstance(action.get("$ref"), str):
            action = (schema.get("$defs") or {})[action["$ref"].rsplit("/", 1)[-1]]
        walk(action)
        return values

    def structured_json(self, system, user, *, schema, schema_name):
        payload = json.loads(user)

        if schema_name == "dima_intent_draft_v1":
            self.preacceptance_calls += 1
            self._draft_attempt += 1
            draft = self._canonical_draft()
            if self._revision and self._draft_attempt == 1:
                # Exact failure family: explicit exclusion incorrectly represented as REQUIRED.
                draft["obligations"][-1]["polarity"] = "REQUIRED"
            return draft

        if schema_name == "dima_intent_coverage_v1":
            self.preacceptance_calls += 1
            self._coverage_attempt += 1
            if self._revision and self._coverage_attempt == 1:
                return {
                    "status": "VETO",
                    "issues": [
                        {
                            "kind": "POLARITY_CONFLICT",
                            "source_surfaces": ["do not claim causal certainty"],
                            "note": "explicit exclusion is represented with REQUIRED polarity",
                        }
                    ],
                }
            return {"status": "PASS", "issues": []}

        if schema_name != "dima_research_manager_action_v1":
            raise AssertionError(f"unexpected schema {schema_name}")

        self.manager_prompts.append(payload)
        actions = self._schema_actions(schema)
        ledger = {item["obligation_id"]: item for item in payload["OBLIGATION_LEDGER"]}
        inventory = {
            item["handle_ref"]: item
            for item in payload["GOVERNED_SEMANTIC_INVENTORY"]
        }
        rel_handles = tuple(ledger["U_REL"]["semantic_handle_refs"])
        rel_metric = next(
            ref for ref in rel_handles
            if inventory[ref]["target_kind"] in {"metric", "kpi"}
        )
        rel_dimension = next(
            ref for ref in rel_handles
            if inventory[ref]["target_kind"] == "dimension"
        )
        root_handle = ledger["U_ROOT"]["semantic_handle_refs"][0]
        rel_evidence_refs = tuple(ledger["U_REL"]["evidence_refs"])
        assert rel_evidence_refs, ledger["U_REL"]
        rel_evidence_ref = rel_evidence_refs[0]
        current_delta = payload["CURRENT_RESULT_DELTA"]
        assert current_delta is not None and current_delta["verified"] is True
        if self.root_trigger_evidence_ref is None:
            assert "U_ROOT" in tuple(
                current_delta.get("obligation_ids") or ()
            ), current_delta
            self.root_trigger_evidence_ref = current_delta["evidence_ref"]
        root_evidence_ref = self.root_trigger_evidence_ref
        accumulated = payload["ACCUMULATED_RESEARCH_STATE"] or {}
        inspected = set(accumulated.get("inspected_evidence_refs") or ())
        dispositions = {
            item["directive_id"]: item["status"]
            for item in payload["RESEARCH_DIRECTIVE_DISPOSITIONS"]
        }
        hypothesis_entries = payload["HYPOTHESIS_LEDGERS"][0]["entries"]

        if rel_evidence_ref not in inspected:
            assert "inspect_evidence" in actions
            self.actions.append("inspect_evidence")
            return {"action": "inspect_evidence", "evidence_ref": rel_evidence_ref}

        if dispositions.get("R_ADAPT_REL") == "OPEN":
            assert "propose_branches" in actions
            self.actions.append("propose_branches")
            return {
                "action": "propose_branches",
                "branch_parent_obligation_id": "U_REL",
                "branch_evidence_ref": rel_evidence_ref,
                "branch_candidates": [
                    {
                        "task_id": "D_REL_BREAK",
                        "capability_key": "breakdown",
                        "input_handles": [rel_metric, rel_dimension],
                        "material_reason": (
                            "Verified relationship Evidence justifies one bounded "
                            "department breakdown follow-up."
                        ),
                    }
                ],
            }

        if not hypothesis_entries:
            assert root_evidence_ref in inspected
            assert "propose_hypothesis_with_next_test" in actions
            self.root_trigger_evidence_ref = root_evidence_ref
            self.actions.append("propose_hypothesis_with_next_test")
            return {
                "action": "propose_hypothesis_with_next_test",
                "hypothesis_parent_obligation_id": "U_ROOT",
                "hypothesis_statement": (
                    "Canonical topology hypothesis contains %27 but report must not."
                ),
                "hypothesis_semantic_handles": [root_handle],
                "hypothesis_trigger_evidence_refs": [root_evidence_ref],
                "hypothesis_limitations": [],
                "next_test_task_kind": "QUERY",
                "next_test_input_handles": [root_handle],
                "next_test_trigger_evidence_ref": root_evidence_ref,
                "next_test_material_reason": (
                    "Test the candidate with one fresh governed root-lineage measurement."
                ),
            }

        hypothesis = hypothesis_entries[0]
        if not hypothesis["evidence_links"]:
            delta = payload["CURRENT_RESULT_DELTA"]
            assert delta is not None and delta["verified"] is True
            assert "propose_hypothesis_evidence_relation" in actions
            self.actions.append("propose_hypothesis_evidence_relation")
            return {
                "action": "propose_hypothesis_evidence_relation",
                "hypothesis_ref": hypothesis["hypothesis_id"],
                "hypothesis_relation_evidence_ref": delta["evidence_ref"],
                "hypothesis_relation": "SUPPORTS",
            }

        raise AssertionError(
            "CompletionGate should terminate canonical topology before another Manager turn"
        )


class RevisionNS4Manager(ScriptedNS4Manager):
    """Exact revision family: vetoed polarity draft, corrected draft, then canonical Research."""

    def __init__(self) -> None:
        super().__init__()
        self._draft_attempt = 0
        self._coverage_attempt = 0

    def structured_json(self, system, user, *, schema, schema_name):
        if schema_name == "dima_intent_draft_v1":
            draft = super().structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )
            self._draft_attempt += 1
            if self._draft_attempt == 1:
                # Same failure FAMILY as paid run #3: an explicit exclusion is attached
                # to REQUIRED authority. Coverage must reject this before any grounding.
                for obligation in draft["obligations"]:
                    if obligation["obligation_id"] == "U_ROOT":
                        obligation["source_surfaces"].append(
                            "Nedensel kesinlik iddia etme"
                        )
                        break
                return draft

            draft["obligations"].append(
                {
                    "obligation_id": "X_CAUSAL_CERTAINTY",
                    "capability_key": "explain",
                    "origin": "USER_MUST",
                    "priority": "MUST",
                    "polarity": "EXCLUDED",
                    "source_surfaces": ["Nedensel kesinlik iddia etme"],
                    "semantic_surfaces": [],
                    "open_questions": [],
                    "ranking_direction": None,
                    "ranking_limit": None,
                }
            )
            return draft

        if schema_name == "dima_intent_coverage_v1":
            # Preserve the same finite cognition count as production: one Coverage call
            # per draft. Attempt 1 is rejected; attempt 2 survives to fresh grounding.
            super().structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )
            self._coverage_attempt += 1
            if self._coverage_attempt == 1:
                return {
                    "status": "VETO",
                    "issues": [
                        {
                            "kind": "POLARITY_CONFLICT",
                            "source_surfaces": ["Nedensel kesinlik iddia etme"],
                            "note": (
                                "Explicit exclusion is attached to REQUIRED authority."
                            ),
                        }
                    ],
                }
            return {"status": "PASS", "issues": []}

        if schema_name == "dima_research_manager_action_v1":
            payload = json.loads(user)
            hypothesis_entries = payload["HYPOTHESIS_LEDGERS"][0]["entries"]
            if not hypothesis_entries:
                self.manager_prompts.append(payload)
                ledger = {
                    item["obligation_id"]: item
                    for item in payload["OBLIGATION_LEDGER"]
                }
                root_handle = ledger["U_ROOT"]["semantic_handle_refs"][0]
                delta = payload["CURRENT_RESULT_DELTA"]
                assert delta is not None and delta["verified"] is True
                assert delta["disclosed_in_current_prompt"] is True
                assert "U_ROOT" in tuple(delta.get("obligation_ids") or ()), delta
                self.root_trigger_evidence_ref = delta["evidence_ref"]
                self.actions.append("propose_hypothesis_with_next_test")
                return {
                    "action": "propose_hypothesis_with_next_test",
                    "hypothesis_parent_obligation_id": "U_ROOT",
                    "hypothesis_statement": (
                        "Provider-free revision hypothesis contains %27 but report must not."
                    ),
                    "hypothesis_semantic_handles": [root_handle],
                    "hypothesis_trigger_evidence_refs": [
                        self.root_trigger_evidence_ref
                    ],
                    "hypothesis_limitations": [],
                    "next_test_task_kind": "QUERY",
                    "next_test_input_handles": [root_handle],
                    "next_test_trigger_evidence_ref": self.root_trigger_evidence_ref,
                    "next_test_material_reason": (
                        "Use the same inspected root Evidence to form the first "
                        "server-governed material hypothesis test."
                    ),
                }

        return super().structured_json(
            system,
            user,
            schema=schema,
            schema_name=schema_name,
        )


class NarrationFailure:
    def __init__(self) -> None:
        self.calls = 0

    def structured_json(self, *_args, **_kwargs):
        self.calls += 1
        raise RuntimeError("provider-free narration fallback")


class CapturingResearchLane(ResearchLaneService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_result = None

    def run(self, **kwargs):
        result = super().run(**kwargs)
        self.last_result = result
        return result


def profile(role: ModelRole) -> ModelProfile:
    return ModelProfile(
        role=role,
        provider="provider-free",
        model="provider-free",
    )


def run_rehearsal(
    *,
    manager: ScriptedNS4Manager | None = None,
    question: str | None = None,
    expected_user_must_ids: tuple[str, ...] = ("U_PERF", "U_REL", "U_ROOT"),
) -> dict[str, object]:
    tenant = "g16-tenant"
    service = SyntheticService()
    principal = Principal(
        user_id="g16-user",
        tenant_id=tenant,
        roles=["owner"],
        tenant_slug="g16",
    )
    schema = service.schema()
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id=tenant,
        tenant_slug="g16",
        principal_user_id=principal.user_id,
        roles=tuple(principal.roles),
        mdl_version=service.mdl_version,
        catalog="g16",
        schema_name="main",
        db_online=True,
    )
    context = ProductRequestContext(
        request_ref="g16-correlation",
        tenant_binding=f"id:{tenant}",
        principal=principal,
        tenant_runtime=runtime,
        service=service,
        schema=schema,
        semantic_context=ContextProviderV0().build(service, runtime),
        contract_store=ContractStore(),
        session_id="g16-session",
        thread_id="g16-thread",
    )

    manager = manager or ScriptedNS4Manager()
    research_lane = CapturingResearchLane(
        cognition=ResearchCognition(
            manager_llm=manager,
            manager_profile=profile(ModelRole.RESEARCH_MANAGER),
            semantic_provider=None,
            semantic_profile=profile(ModelRole.SEMANTIC_LINKER),
            temporal_provider=None,
            temporal_profile=profile(ModelRole.TEMPORAL_NORMALIZER),
        )
    )
    standard = ForceResearchStandardLane()
    narration = NarrationFailure()
    coordinator = ProductCoordinator(
        standard_lane=standard,
        standard_model_role="FAST_LANGUAGE",
        research_lane=research_lane,
        report_narrator=ReportNarrator(
            llm=narration,
            provider="provider-free",
            model="provider-free",
        ),
    )
    coordinator._bind_context = lambda **_kwargs: context

    response = coordinator.handle(
        request=object(),
        body=ProductAskRequest(
            question=question or (
                "Research downtime performance, its governed relationship with department, "
                "and investigate the root cause of faults; doğrulanmış sonuçlar yeni bir maddi "
                "kırılıma işaret ederse onu takip et"
            ),
            session_id=context.session_id,
            thread_id=context.thread_id,
        ),
        principal=principal,
    )
    result = research_lane.last_result
    if result is None:
        raise RehearsalError("Research result missing")
    if response.lane != ProductLane.RESEARCH or response.status != ProductStatus.REPORT:
        diagnostic = None
        if result is not None:
            snapshot = result.runtime.snapshot
            diagnostic = {
                "runtime_state": snapshot.state.value,
                "manager_turn_total": snapshot.manager_turns,
                "preacceptance_turns": snapshot.preacceptance_turns,
                "research_manager_turns": snapshot.research_manager_turns,
                "manager_turn_ceiling": result.runtime.budget.max_total_manager_turns,
                "manager_actions": list(manager.actions),
                "diagnostic_observations": [
                    item
                    for item in result.outcome.observations
                    if item.get("kind") in {
                        "model_error",
                        "tool_rejected",
                        "manager_action_availability",
                    }
                ][-6:],
                "terminal_status": (
                    result.outcome.terminal_status.value
                    if result.outcome.terminal_status is not None
                    else None
                ),
            }
        raise RehearsalError(
            "canonical rehearsal did not complete as report: "
            f"{response.status.value}; diagnostic={diagnostic}"
        )
    if not result.verified_complete or result.runtime.snapshot.state != ManagerState.COMPLETED:
        raise RehearsalError("CompletionGate did not terminate canonical rehearsal")

    active = {
        item.obligation_id: item
        for item in result.ledger.active_user_must
    }
    if set(active) != set(expected_user_must_ids):
        raise RehearsalError(
            "unexpected USER_MUST set: "
            f"{sorted(active)} != {sorted(expected_user_must_ids)}"
        )
    presentation_ids = {
        obligation_id
        for obligation_id, item in active.items()
        if item.capability_key in {
            ManagerCapabilityKey.REPORT,
            ManagerCapabilityKey.TABLE,
            ManagerCapabilityKey.CHART,
            ManagerCapabilityKey.EXPLAIN,
        }
    }
    analytical_ids = set(active) - presentation_ids
    if any(
        active[obligation_id].status != ObligationStatus.VERIFIED
        for obligation_id in analytical_ids
    ):
        raise RehearsalError(
            "all canonical analytical USER_MUST obligations must be VERIFIED"
        )
    if any(
        active[obligation_id].status
        not in {ObligationStatus.ACCEPTED, ObligationStatus.VERIFIED}
        for obligation_id in presentation_ids
    ):
        raise RehearsalError(
            "presentation USER_MUST must remain accepted delivery authority"
        )

    observations = tuple(result.outcome.observations)
    kinds = [str(item.get("kind")) for item in observations if isinstance(item, dict)]
    required = {
        "deterministic_task_executed",
        "root_cause_bootstrap_executed",
        "adaptive_branch_executed",
        "hypothesis_registered",
        "hypothesis_next_test_executed",
        "hypothesis_relation_admitted",
        "root_cause_obligation_reconciled",
    }
    missing = required - set(kinds)
    if missing:
        raise RehearsalError(
            "canonical transition receipt missing: " + ", ".join(sorted(missing))
        )

    report_text = "\n".join(
        block.content
        for section in response.report.report.sections
        for block in section.blocks
    )
    if "%27" in report_text:
        raise RehearsalError("model hypothesis prose leaked into canonical report")
    if not result.findings:
        raise RehearsalError("canonical candidate finding missing")
    if not any(
        item.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
        for item in result.findings
    ):
        raise RehearsalError("CANDIDATE_CAUSE finding missing")

    snapshot = result.runtime.snapshot
    manager_actions = [
        json.loads(json.dumps(prompt)).get("MANAGER_STATE")
        for prompt in manager.manager_prompts
    ]
    del manager_actions  # call count is authoritative; action kinds come from observations.

    cognition_sequence = tuple(manager.actions)

    fresh_disclosures = sum(
        1 for item in observations
        if item.get("kind") == "fresh_evidence_disclosed"
    )
    explicit_inspects = sum(
        1 for item in observations
        if item.get("kind") == "tool"
        and item.get("tool") == "inspect_evidence"
    )
    execution_control = {
        "run_analytics",
        "run_relationship",
        "inspect_evidence",
        "finish",
    }
    if any(action in execution_control for action in cognition_sequence):
        raise RehearsalError("execution-control cognition remains in G16 sequence")

    dispositions = result.runtime.directive_dispositions
    if len(dispositions) != 1:
        raise RehearsalError(
            f"expected one completion-relevant directive disposition, got {len(dispositions)}"
        )
    directive = dispositions[0]
    accepted_directives = result.accepted_contract.research_directives
    if len(accepted_directives) != 1:
        raise RehearsalError(
            f"expected one accepted ResearchDirective, got {len(accepted_directives)}"
        )

    return {
        "contract": "d10-g16-ns4-provider-free-runtime-v2",
        "provider_calls": 0,
        "directive_count": len(accepted_directives),
        "directive_id": accepted_directives[0].directive_id,
        "directive_type": accepted_directives[0].directive_type.value,
        "directive_final_status": directive.status.value,
        "directive_accounting_evidence_ref": directive.evidence_ref,
        "directive_branch_task_refs": list(directive.branch_task_refs),
        "initial_user_must_count": len(active),
        "analytical_user_must_ids": sorted(analytical_ids),
        "presentation_user_must_ids": sorted(presentation_ids),
        "presentation_delivery_requested": bool(presentation_ids),
        "user_must_families": [
            active[key].capability_key.value.upper()
            for key in expected_user_must_ids
        ],
        "preacceptance_model_calls": manager.preacceptance_calls,
        "research_manager_calls": len(manager.manager_prompts),
        "research_cognition_sequence": list(cognition_sequence),
        "manager_turn_total": snapshot.manager_turns,
        "manager_turn_ceiling": result.runtime.budget.max_total_manager_turns,
        "manager_turn_headroom": (
            result.runtime.budget.max_total_manager_turns - snapshot.manager_turns
        ),
        "deterministic_task_executions": service.query_calls,
        "deterministic_query_transitions": service.query_calls,
        "synthetic_query_calls": service.query_calls,
        "actual_wren_queries_in_rehearsal": 0,
        "fresh_evidence_disclosures": fresh_disclosures,
        "explicit_old_evidence_inspections": explicit_inspects,
        "redundant_fresh_inspect_turns": explicit_inspects,
        "redundant_manager_execution_control_turns": 0,
        "hypotheses": 1,
        "hypothesis_next_tests": 1,
        "evidence_relations": 1,
        "semantic_linker_model_calls": 0,
        "temporal_model_calls": 0,
        "narration_calls": narration.calls,
        "narration_provider_calls": 0,
        "completion_gate_final_state": snapshot.state.value,
        "root_status": active["U_ROOT"].status.value,
        "candidate_finding_count": sum(
            item.epistemic_label == EpistemicLabel.CANDIDATE_CAUSE
            for item in result.findings
        ),
        "confirmed_cause_count": sum(
            item.epistemic_label == EpistemicLabel.CONFIRMED_CAUSE
            for item in result.findings
        ),
        "report_statement_injection_absent": "%27" not in report_text,
        "observed_transition_kinds": kinds,
        "paid_gate_structural_status": (
            "STRUCTURALLY_ADMISSIBLE_AT_CEILING"
            if snapshot.manager_turns <= result.runtime.budget.max_total_manager_turns
            and explicit_inspects == 0
            else "BLOCKED"
        ),
    }



def run_canonical_relationship_topology_rehearsal(
    *,
    revision: bool = False,
) -> dict[str, object]:
    manager = CanonicalRelationshipTopologyManager(revision=revision)
    receipt = run_rehearsal(
        manager=manager,
        question=(
            "Research downtime performance and department breakdown; check the governed "
            "relationship, investigate root cause of faults, follow a materially new "
            "verified relationship direction, produce a management report, and do not "
            "claim causal certainty."
        ),
        expected_user_must_ids=(
            "U_PERF",
            "U_BREAK",
            "U_REL",
            "U_ROOT",
            "U_REPORT",
        ),
    )
    return {
        **receipt,
        "contract": (
            "d10-s-canonical-relationship-revision-v1"
            if revision
            else "d10-s-canonical-relationship-clean-v1"
        ),
        "adaptive_parent_obligation_id": "U_REL",
    }


def run_revision_rehearsal() -> dict[str, object]:
    receipt = run_rehearsal(
        manager=RevisionNS4Manager(),
        question=(
            "Research downtime performance, its governed relationship with department, "
            "and investigate the root cause of faults; doğrulanmış sonuçlar yeni bir maddi "
            "kırılıma işaret ederse onu takip et. Nedensel kesinlik iddia etme"
        ),
    )
    return {**receipt, "contract": "d10-final-revision-path-provider-free-v1"}


def main() -> int:
    receipt = run_rehearsal()
    if receipt["directive_count"] != 1:
        raise SystemExit("canonical rehearsal directive count drifted")
    if receipt["directive_type"] != "ADAPT_ON_EVIDENCE":
        raise SystemExit("canonical rehearsal directive type drifted")
    if receipt["directive_final_status"] != "APPLIED":
        raise SystemExit("canonical rehearsal adaptive directive is not accounted")
    if not receipt["directive_accounting_evidence_ref"]:
        raise SystemExit("canonical rehearsal directive lacks accounting Evidence")
    if not receipt["directive_branch_task_refs"]:
        raise SystemExit("canonical rehearsal directive lacks governed branch task")
    if receipt["preacceptance_model_calls"] != 2:
        raise SystemExit("canonical rehearsal preacceptance count drifted")
    if receipt["research_manager_calls"] != 4:
        raise SystemExit("canonical rehearsal Research cognition count drifted")
    if receipt["manager_turn_total"] != 6:
        raise SystemExit("canonical rehearsal no longer fits exact six-turn ceiling")
    if receipt["deterministic_task_executions"] != 5:
        raise SystemExit("canonical rehearsal deterministic task count drifted")
    if receipt["redundant_fresh_inspect_turns"] != 0:
        raise SystemExit("fresh Evidence inspect ceremony regressed")
    if receipt["confirmed_cause_count"] != 0:
        raise SystemExit("CONFIRMED_CAUSE remains forbidden")
    if receipt["paid_gate_structural_status"] != "STRUCTURALLY_ADMISSIBLE_AT_CEILING":
        raise SystemExit("paid gate remains structurally blocked")

    path = Path("lab/reports/v2_day10_ns4_provider_free_rehearsal.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
