"""Provider-free certification projections for final/integrated Dima V2 gates.

This module is evaluation authority only. It must never participate in Product runtime
decisions. Certification is derived from accepted typed authority, final lifecycle
state and governed provenance; diagnostic observations/events may be carried in
receipts but do not own lifecycle truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


def _value(value: Any) -> Any:
    return getattr(value, "value", value)


@dataclass(frozen=True)
class AdaptiveLifecycleCertification:
    valid: bool
    lifecycle_outcome: str
    certification_coverage: str
    disposition_status: str | None
    evidence_ref: str | None
    branch_task_refs: tuple[str, ...]
    errors: tuple[str, ...]
    diagnostic_observation_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class Day8RootLiveDebtCertification:
    valid: bool
    root_obligation_id: str | None
    hypothesis_ref: str | None
    next_test_evidence_ref: str | None
    candidate_finding_ids: tuple[str, ...]
    confirmed_cause_count: int
    errors: tuple[str, ...]
    diagnostic_observation_kinds: tuple[str, ...]


def _evidence_index(evidence_items: Iterable[Any]) -> dict[str, Any]:
    return {
        str(item.artifact_id): item
        for item in evidence_items
        if getattr(item, "artifact_id", None)
    }


def _ledger_index(ledger: Any) -> dict[str, Any]:
    return {
        str(item.obligation_id): item
        for item in (getattr(ledger, "items", ()) or ())
        if getattr(item, "obligation_id", None)
    }


def evidence_belongs_to_parent_lineage(
    *,
    ledger: Any,
    evidence: Any,
    parent_obligation_id: str,
) -> bool:
    """Eval-only mirror of the already-ratified lineage invariant."""

    by_id = _ledger_index(ledger)
    for obligation_id in getattr(evidence, "obligation_ids", ()) or ():
        current = str(obligation_id)
        seen: set[str] = set()
        while current not in seen:
            if current == parent_obligation_id:
                return True
            seen.add(current)
            item = by_id.get(current)
            if item is None:
                break
            parent = getattr(item, "parent_obligation_id", None)
            if parent is None:
                break
            current = str(parent)
    return False


def certify_adaptive_lifecycle(
    *,
    directive: Any,
    disposition: Any | None,
    evidence_items: Iterable[Any],
    ledger: Any,
    inspected_evidence_refs: Iterable[str],
    product_verified_complete: bool,
    diagnostic_observations: Iterable[dict[str, Any]] = (),
) -> AdaptiveLifecycleCertification:
    """Certify ADAPT_ON_EVIDENCE from authoritative state, never event chronology."""

    errors: list[str] = []
    observation_kinds = tuple(
        str(item.get("kind"))
        for item in diagnostic_observations
        if isinstance(item, dict) and item.get("kind")
    )
    directive_type = _value(getattr(directive, "directive_type", None))
    directive_id = getattr(directive, "directive_id", None)
    parent_id = getattr(directive, "parent_obligation_id", None)

    if directive_type != "ADAPT_ON_EVIDENCE":
        errors.append("accepted directive is not ADAPT_ON_EVIDENCE")

    if disposition is None:
        errors.append("accepted ADAPT_ON_EVIDENCE has no final disposition")
        return AdaptiveLifecycleCertification(
            valid=False,
            lifecycle_outcome="INVALID",
            certification_coverage="INCOMPLETE",
            disposition_status=None,
            evidence_ref=None,
            branch_task_refs=(),
            errors=tuple(errors),
            diagnostic_observation_kinds=observation_kinds,
        )

    status = _value(getattr(disposition, "status", None))
    evidence_ref = getattr(disposition, "evidence_ref", None)
    branch_task_refs = tuple(getattr(disposition, "branch_task_refs", ()) or ())

    if getattr(disposition, "directive_id", None) != directive_id:
        errors.append("final disposition directive_id does not match accepted directive")
    if _value(getattr(disposition, "directive_type", None)) != directive_type:
        errors.append("final disposition directive_type does not match accepted directive")
    if getattr(disposition, "parent_obligation_id", None) != parent_id:
        errors.append("final disposition parent obligation does not match accepted directive")

    if status == "OPEN":
        if product_verified_complete:
            errors.append(
                "CompletionGate verified Product while completion-relevant ADAPT directive remained OPEN"
            )
        return AdaptiveLifecycleCertification(
            valid=not errors and not product_verified_complete,
            lifecycle_outcome="OPEN" if not errors else "INVALID",
            certification_coverage="INCOMPLETE",
            disposition_status=status,
            evidence_ref=evidence_ref,
            branch_task_refs=branch_task_refs,
            errors=tuple(errors),
            diagnostic_observation_kinds=observation_kinds,
        )

    evidence_by_ref = _evidence_index(evidence_items)
    evidence = evidence_by_ref.get(str(evidence_ref)) if evidence_ref else None
    if evidence_ref is None:
        errors.append("terminal ADAPT disposition lacks governed Evidence ref")
    elif evidence is None:
        errors.append("terminal ADAPT disposition references missing Evidence")
    else:
        if not bool(getattr(evidence, "verified", False)):
            errors.append("terminal ADAPT disposition Evidence is not VERIFIED")
        if not evidence_belongs_to_parent_lineage(
            ledger=ledger,
            evidence=evidence,
            parent_obligation_id=str(parent_id),
        ):
            errors.append("terminal ADAPT disposition Evidence is outside parent lineage")

    reason = getattr(disposition, "reason", None)
    if not isinstance(reason, str) or not reason.strip():
        errors.append("terminal ADAPT disposition lacks bounded reason")

    if status == "APPLIED":
        if not branch_task_refs:
            errors.append("APPLIED disposition lacks branch_task_refs")
        for task_ref in branch_task_refs:
            result_evidence = [
                item
                for item in evidence_by_ref.values()
                if str(getattr(item, "task_id", "")) == str(task_ref)
            ]
            if not result_evidence:
                errors.append(
                    f"APPLIED branch {task_ref} has no governed result Evidence"
                )
                continue
            if not any(bool(getattr(item, "verified", False)) for item in result_evidence):
                errors.append(
                    f"APPLIED branch {task_ref} has no VERIFIED result Evidence"
                )
            if not any(
                evidence_belongs_to_parent_lineage(
                    ledger=ledger,
                    evidence=item,
                    parent_obligation_id=str(parent_id),
                )
                for item in result_evidence
            ):
                errors.append(
                    f"APPLIED branch {task_ref} result Evidence is outside parent lineage"
                )
        return AdaptiveLifecycleCertification(
            valid=not errors,
            lifecycle_outcome="VALIDLY_ACCOUNTED" if not errors else "INVALID",
            certification_coverage="COMPLETE" if not errors else "INCOMPLETE",
            disposition_status=status,
            evidence_ref=evidence_ref,
            branch_task_refs=branch_task_refs,
            errors=tuple(errors),
            diagnostic_observation_kinds=observation_kinds,
        )

    if status == "NO_MATERIAL_DIRECTION":
        if branch_task_refs:
            errors.append("NO_MATERIAL_DIRECTION cannot carry branch_task_refs")
        if evidence_ref not in set(str(ref) for ref in inspected_evidence_refs):
            errors.append(
                "NO_MATERIAL_DIRECTION requires inspected current-run VERIFIED Evidence"
            )
        return AdaptiveLifecycleCertification(
            valid=not errors,
            lifecycle_outcome="VALIDLY_ACCOUNTED" if not errors else "INVALID",
            certification_coverage="COMPLETE" if not errors else "INCOMPLETE",
            disposition_status=status,
            evidence_ref=evidence_ref,
            branch_task_refs=branch_task_refs,
            errors=tuple(errors),
            diagnostic_observation_kinds=observation_kinds,
        )

    if status == "BLOCKED":
        return AdaptiveLifecycleCertification(
            valid=not errors,
            lifecycle_outcome="VALID_PRODUCT_TERMINAL" if not errors else "INVALID",
            certification_coverage=(
                "CERTIFICATION_COVERAGE_INCOMPLETE"
                if not errors
                else "INCOMPLETE"
            ),
            disposition_status=status,
            evidence_ref=evidence_ref,
            branch_task_refs=branch_task_refs,
            errors=tuple(errors),
            diagnostic_observation_kinds=observation_kinds,
        )

    errors.append(f"unknown ADAPT disposition status: {status}")
    return AdaptiveLifecycleCertification(
        valid=False,
        lifecycle_outcome="INVALID",
        certification_coverage="INCOMPLETE",
        disposition_status=status,
        evidence_ref=evidence_ref,
        branch_task_refs=branch_task_refs,
        errors=tuple(errors),
        diagnostic_observation_kinds=observation_kinds,
    )


def _find_observations(observations: Iterable[dict[str, Any]], kind: str) -> tuple[dict[str, Any], ...]:
    return tuple(
        item
        for item in observations
        if isinstance(item, dict) and item.get("kind") == kind
    )


def certify_day8_root_live_debt(
    *,
    accepted_contract: Any,
    ledger: Any,
    evidence_items: Iterable[Any],
    findings: Iterable[Any],
    observations: Iterable[dict[str, Any]],
) -> Day8RootLiveDebtCertification:
    """Certify the historical Day8 ROOT proof without requiring an ADAPT trajectory."""

    errors: list[str] = []
    observations = tuple(observations)
    observation_kinds = tuple(
        str(item.get("kind"))
        for item in observations
        if isinstance(item, dict) and item.get("kind")
    )
    evidence_by_ref = _evidence_index(evidence_items)

    root_items = [
        item
        for item in (getattr(ledger, "items", ()) or ())
        if _value(getattr(item, "capability_key", None)) == "root_cause"
        and _value(getattr(item, "origin", None)) == "USER_MUST"
        and _value(getattr(item, "polarity", None)) == "REQUIRED"
    ]
    if len(root_items) != 1:
        errors.append(f"expected exactly one ROOT_CAUSE USER_MUST; got {len(root_items)}")
        root = None
        root_id = None
    else:
        root = root_items[0]
        root_id = str(root.obligation_id)
        if _value(getattr(root, "status", None)) != "VERIFIED":
            errors.append("ROOT_CAUSE USER_MUST is not VERIFIED")
        if root_id not in set(getattr(accepted_contract, "obligation_ids", ()) or ()):
            errors.append("ROOT_CAUSE obligation is outside AcceptedTurnContract")

    registered = _find_observations(observations, "hypothesis_registered")
    registered = tuple(
        item
        for item in registered
        if root_id is not None
        and str((item.get("result") or {}).get("parent_obligation_id")) == root_id
    )
    hypothesis_ref = None
    if not registered:
        errors.append("no registered hypothesis proof for accepted ROOT obligation")
    else:
        hypothesis_ref = str((registered[-1].get("result") or {}).get("hypothesis_id") or "")
        if not hypothesis_ref:
            errors.append("registered hypothesis proof lacks server-owned hypothesis id")

    next_tests = _find_observations(observations, "hypothesis_next_test_executed")
    matching_next = []
    for item in next_tests:
        result = item.get("result") or {}
        if hypothesis_ref and str(result.get("hypothesis_id")) != hypothesis_ref:
            continue
        matching_next.append(item)
    next_test_evidence_ref = None
    if not matching_next:
        errors.append("no governed executed hypothesis next-test proof")
    else:
        result = matching_next[-1].get("result") or {}
        next_test_evidence_ref = str(result.get("evidence_ref") or "")
        task_id = str(result.get("task_id") or "")
        evidence = evidence_by_ref.get(next_test_evidence_ref)
        if evidence is None:
            errors.append("executed hypothesis next test has no captured result Evidence")
        else:
            if not bool(getattr(evidence, "verified", False)):
                errors.append("hypothesis next-test result Evidence is not VERIFIED")
            if task_id and str(getattr(evidence, "task_id", "")) != task_id:
                errors.append("hypothesis next-test task/result Evidence provenance mismatch")
            if root_id and not evidence_belongs_to_parent_lineage(
                ledger=ledger,
                evidence=evidence,
                parent_obligation_id=root_id,
            ):
                errors.append("hypothesis next-test result Evidence is outside ROOT lineage")

    relations = _find_observations(observations, "hypothesis_relation_admitted")
    admitted_relation = None
    for item in relations:
        result = item.get("result") or {}
        if hypothesis_ref and str(result.get("hypothesis_id")) != hypothesis_ref:
            continue
        links = tuple(result.get("evidence_links") or ())
        if next_test_evidence_ref and any(
            str(link.get("evidence_ref")) == next_test_evidence_ref
            and str(link.get("relation")) in {"SUPPORTS", "CONTRADICTS"}
            for link in links
            if isinstance(link, dict)
        ):
            admitted_relation = item
            break
    if admitted_relation is None:
        errors.append("no admitted hypothesis-Evidence relation for next-test Evidence")

    findings = tuple(findings)
    candidate_findings = [
        item
        for item in findings
        if _value(getattr(item, "epistemic_label", None)) == "CANDIDATE_CAUSE"
        and (root_id is None or str(getattr(item, "parent_obligation_id", "")) == root_id)
        and (
            hypothesis_ref is None
            or str(getattr(item, "hypothesis_ref", "")) == hypothesis_ref
        )
    ]
    if not candidate_findings:
        errors.append("no canonical CANDIDATE_CAUSE Finding for ROOT hypothesis")
    for finding in candidate_findings:
        for ref in getattr(finding, "evidence_refs", ()) or ():
            evidence = evidence_by_ref.get(str(ref))
            if evidence is None or not bool(getattr(evidence, "verified", False)):
                errors.append(
                    f"CANDIDATE_CAUSE Finding references missing/unverified Evidence: {ref}"
                )

    confirmed_count = sum(
        1
        for item in findings
        if _value(getattr(item, "epistemic_label", None)) == "CONFIRMED_CAUSE"
    )
    if confirmed_count:
        errors.append("CONFIRMED_CAUSE ceiling violated")

    return Day8RootLiveDebtCertification(
        valid=not errors,
        root_obligation_id=root_id,
        hypothesis_ref=hypothesis_ref,
        next_test_evidence_ref=next_test_evidence_ref,
        candidate_finding_ids=tuple(
            str(item.finding_id) for item in candidate_findings
        ),
        confirmed_cause_count=confirmed_count,
        errors=tuple(errors),
        diagnostic_observation_kinds=observation_kinds,
    )
