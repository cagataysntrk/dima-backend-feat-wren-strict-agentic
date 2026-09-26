"""Day14 durable canonical V2 checkpointing and restart projection.

The checkpoint contains typed authoritative state only. Provider reasoning, ActionSet
trajectory, observations, ProductEvent diagnostics, raw prompts, and scratch cognition
are deliberately excluded.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import Field

from app.v2.manager_models import (
    AcceptedTurnContract,
    ManagerRunSnapshot,
    ResearchDirectiveDisposition,
    ResearchRunTerminal,
    UserObligationLedger,
)
from app.v2.models import (
    ConversationStateV2,
    EvidenceArtifact,
    EvidenceLinkedFinding,
    FrozenModel,
    HypothesisLedgerState,
    ResearchTask,
)
from app.v2.product_models import VersionedReport
from app.v2.semantic_handles import (
    SemanticBindingRecord,
    SemanticHandleRegistry,
)


class DurableCheckpointError(RuntimeError):
    pass


class StaleCheckpointWrite(DurableCheckpointError):
    pass


class CheckpointScope(FrozenModel):
    tenant_binding: str = Field(min_length=1)
    principal_subject: str = Field(min_length=1)
    session_id: str | None = None
    thread_id: str | None = None
    context_version: str = Field(min_length=1)
    lineage_id: str = Field(min_length=1)


class CanonicalResumeState(FrozenModel):
    manager_snapshot: ManagerRunSnapshot | None = None
    accepted_contract: AcceptedTurnContract | None = None
    ledger: UserObligationLedger | None = None
    research_tasks: tuple[ResearchTask, ...] = ()
    evidence: tuple[EvidenceArtifact, ...] = ()
    findings: tuple[EvidenceLinkedFinding, ...] = ()
    hypothesis_states: tuple[HypothesisLedgerState, ...] = ()
    directive_dispositions: tuple[ResearchDirectiveDisposition, ...] = ()
    reports: tuple[VersionedReport, ...] = ()
    completion_status: ResearchRunTerminal | None = None
    conversation: ConversationStateV2 | None = None
    semantic_bindings: tuple[SemanticBindingRecord, ...] = ()


class DurableCheckpoint(FrozenModel):
    checkpoint_id: str = Field(pattern=r"^v2cp_[a-f0-9]{24}$")
    scope: CheckpointScope
    revision: int = Field(ge=1)
    state_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    state: CanonicalResumeState


def _canonical_json(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _state_hash(state: CanonicalResumeState) -> str:
    return hashlib.sha256(_canonical_json(state).encode("utf-8")).hexdigest()


def _scope_key(scope: CheckpointScope) -> str:
    return hashlib.sha256(_canonical_json(scope).encode("utf-8")).hexdigest()[:32]


class DurableCheckpointStore:
    """Filesystem-backed atomic checkpoint repository with cross-process CAS.

    A deployment may later replace the storage adapter, but the CAS/idempotency
    contract is authoritative: no silent last-write-wins is allowed.
    """

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _paths(self, scope: CheckpointScope) -> tuple[Path, Path]:
        key = _scope_key(scope)
        return (
            self._root / f"{key}.json",
            self._root / f"{key}.lock",
        )

    @staticmethod
    def _read(path: Path) -> DurableCheckpoint | None:
        if not path.exists():
            return None
        try:
            return DurableCheckpoint.model_validate_json(
                path.read_text(encoding="utf-8")
            )
        except Exception as exc:
            raise DurableCheckpointError(
                f"durable checkpoint is unreadable: {path.name}"
            ) from exc

    def load(self, scope: CheckpointScope) -> DurableCheckpoint | None:
        path, lock_path = self._paths(scope)
        with lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
            try:
                checkpoint = self._read(path)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        if checkpoint is not None and checkpoint.scope != scope:
            raise DurableCheckpointError("durable checkpoint scope mismatch")
        return checkpoint

    def commit(
        self,
        *,
        scope: CheckpointScope,
        state: CanonicalResumeState,
        expected_revision: int,
    ) -> DurableCheckpoint:
        path, lock_path = self._paths(scope)
        if expected_revision < 0:
            raise ValueError("expected_revision must be >= 0")

        state_hash = _state_hash(state)
        with lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                prior = self._read(path)
                if prior is not None:
                    if prior.scope != scope:
                        raise DurableCheckpointError(
                            "durable checkpoint scope mismatch"
                        )
                    # Exact retry is idempotent even when caller still carries the
                    # previous expected revision.
                    if prior.state_hash == state_hash and prior.state == state:
                        return prior
                    current_revision = prior.revision
                else:
                    current_revision = 0

                if current_revision != expected_revision:
                    raise StaleCheckpointWrite(
                        "stale checkpoint writer: "
                        f"expected={expected_revision} current={current_revision}"
                    )

                revision = current_revision + 1
                identity = (
                    f"{_scope_key(scope)}\x1f{revision}\x1f{state_hash}"
                )
                checkpoint = DurableCheckpoint(
                    checkpoint_id=(
                        "v2cp_"
                        + hashlib.sha256(
                            identity.encode("utf-8")
                        ).hexdigest()[:24]
                    ),
                    scope=scope,
                    revision=revision,
                    state_hash=state_hash,
                    state=state,
                )
                tmp = path.with_suffix(
                    f".{os.getpid()}.{revision}.tmp"
                )
                payload = checkpoint.model_dump_json()
                with tmp.open("w", encoding="utf-8") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(tmp, path)
                # fsync directory so rename is durable across crash.
                directory_fd = os.open(self._root, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
                return checkpoint
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def delete_for_test(self, scope: CheckpointScope) -> None:
        path, lock_path = self._paths(scope)
        with lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                path.unlink(missing_ok=True)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def state_from_research_result(
    *,
    result,
    scope: CheckpointScope,
    reports: tuple[VersionedReport, ...] = (),
    conversation: ConversationStateV2 | None = None,
) -> CanonicalResumeState:
    accepted = result.accepted_contract
    if accepted is not None and accepted.lineage_id != scope.lineage_id:
        raise DurableCheckpointError("research result lineage does not match scope")
    ledger = result.ledger
    if ledger is not None and ledger.lineage_id != scope.lineage_id:
        raise DurableCheckpointError("research ledger lineage does not match scope")

    semantic_records = result.semantic_handles.export_records(
        tenant_binding=scope.tenant_binding,
        context_version=scope.context_version,
    )
    outcome = result.outcome
    return CanonicalResumeState(
        manager_snapshot=outcome.snapshot,
        accepted_contract=accepted,
        ledger=ledger,
        research_tasks=tuple(outcome.research_tasks),
        evidence=tuple(result.evidence),
        findings=tuple(result.findings),
        hypothesis_states=tuple(outcome.hypothesis_states),
        directive_dispositions=tuple(outcome.directive_dispositions),
        reports=reports,
        completion_status=outcome.terminal_status,
        conversation=conversation,
        semantic_bindings=semantic_records,
    )


def restore_evidence_store(checkpoint: DurableCheckpoint):
    # Lazy import avoids making the canonical Evidence model depend on its store.
    from app.v2.manager_executor import EvidenceStore

    store = EvidenceStore(
        tenant_binding=checkpoint.scope.tenant_binding,
        principal_subject=checkpoint.scope.principal_subject,
        context_version=checkpoint.scope.context_version,
    )
    for evidence in checkpoint.state.evidence:
        store.put(evidence)
    return store


def restore_semantic_handles(
    checkpoint: DurableCheckpoint,
) -> SemanticHandleRegistry:
    return SemanticHandleRegistry.restore_records(
        checkpoint.state.semantic_bindings
    )


def restore_task_registry(checkpoint: DurableCheckpoint):
    from app.v2.research_tasks import ResearchTaskRegistry

    registry = ResearchTaskRegistry(
        max_fanout=max(4, len(checkpoint.state.research_tasks) or 1)
    )
    for task in checkpoint.state.research_tasks:
        registry.register(task)
    return registry


@dataclass(frozen=True)
class RestoredResearchContext:
    runtime: Any
    evidence_store: Any
    semantic_handles: SemanticHandleRegistry
    accepted_contract: AcceptedTurnContract
    ledger: UserObligationLedger
    evidence: tuple[EvidenceArtifact, ...]
    findings: tuple[EvidenceLinkedFinding, ...]


def restore_research_context(
    checkpoint: DurableCheckpoint,
) -> RestoredResearchContext:
    from app.v2.manager_runtime import ManagerRuntime

    state = checkpoint.state
    if (
        state.manager_snapshot is None
        or state.accepted_contract is None
        or state.ledger is None
    ):
        raise DurableCheckpointError(
            "research resume requires snapshot + accepted contract + ledger"
        )
    runtime = ManagerRuntime.restore_canonical(
        snapshot=state.manager_snapshot,
        accepted_contract=state.accepted_contract,
        ledger=state.ledger,
        directive_dispositions=state.directive_dispositions,
    )
    return RestoredResearchContext(
        runtime=runtime,
        evidence_store=restore_evidence_store(checkpoint),
        semantic_handles=restore_semantic_handles(checkpoint),
        accepted_contract=state.accepted_contract,
        ledger=state.ledger,
        evidence=state.evidence,
        findings=state.findings,
    )
