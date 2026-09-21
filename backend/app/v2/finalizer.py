"""Day 5 Core MVP conversation finalizer.

This layer owns presentation only. It consumes typed V2 state/evidence and MUST NOT
re-interpret raw user language, repair semantic gaps, query data, or invent numbers.
"""

from __future__ import annotations

import json
from typing import Any

from app.v2.models import (
    AnalyticsIR,
    AskV2CoreResponse,
    AskV2Day4Response,
    ConversationResponseKind,
    ConversationResponseV0,
    ConversationTableV0,
    DialogueAction,
    EvidenceRefV0,
    ExecutionResultV0,
    ResultExecutionAnchorV0,
    ResearchBriefStatus,
    ScopeChipV0,
    SemanticHypothesis,
)


def _cell(value: Any) -> str:
    """Display an already-produced result value without deriving a new value."""
    if value is None:
        return "∅"
    if isinstance(value, (dict, list, tuple)):
        text = json.dumps(value, ensure_ascii=False, default=str)
    else:
        text = str(value)
    return text if len(text) <= 180 else text[:177] + "…"


def _row_text(row: dict[str, Any], *, max_fields: int = 6) -> str:
    items = list(row.items())
    shown = items[:max_fields]
    text = " · ".join(f"{key} = {_cell(value)}" for key, value in shown)
    if len(items) > max_fields:
        text += " · …"
    return text


def _execution_text(execution: ExecutionResultV0 | ResultExecutionAnchorV0) -> str:
    if execution.row_count <= 0 or not execution.rows:
        return "Bu kapsamda sonuç satırı dönmedi."
    first = _row_text(dict(execution.rows[0]))
    if execution.row_count == 1:
        return f"Sonuç: {first}."
    return f"{execution.row_count} doğrulanmış satır döndü. İlk satır: {first}."


def _candidate_labels(
    hypotheses: tuple[SemanticHypothesis, ...],
) -> dict[str, str]:
    labels: dict[str, str] = {}
    for hypothesis in hypotheses:
        for candidate in hypothesis.candidates:
            labels.setdefault(candidate.candidate_id, candidate.display_label)
    return labels


def _scope_chips(
    ir: AnalyticsIR | None,
    hypotheses: tuple[SemanticHypothesis, ...],
) -> tuple[ScopeChipV0, ...]:
    if ir is None:
        return ()

    labels = _candidate_labels(hypotheses)
    chips: list[ScopeChipV0] = []

    for ref in ir.metrics:
        chips.append(
            ScopeChipV0(
                kind="metric",
                label=labels.get(ref.candidate_id, ref.canonical_name),
                canonical_ref=ref.canonical_name,
            )
        )
    for ref in ir.dimensions:
        chips.append(
            ScopeChipV0(
                kind="dimension",
                label=labels.get(ref.candidate_id, ref.canonical_name),
                canonical_ref=ref.canonical_name,
            )
        )
    for ref in ir.filters:
        label = (
            "Filtre uygulandı"
            if ref.sensitive
            else labels.get(ref.candidate_id, f"{ref.dimension_name} = {ref.value}")
        )
        chips.append(
            ScopeChipV0(
                kind="filter",
                label=label,
                canonical_ref=ref.dimension_name,
            )
        )
    if ir.period is not None:
        chips.append(
            ScopeChipV0(
                kind="time",
                label=ir.period.source_text,
                canonical_ref=ir.period.time_dimension,
            )
        )
    if ir.ranking is not None:
        direction = "En yüksek" if ir.ranking.direction == "desc" else "En düşük"
        chips.append(
            ScopeChipV0(
                kind="ranking",
                label=f"{direction} {ir.ranking.limit}",
                canonical_ref=ir.ranking.measure,
            )
        )
    if ir.comparison is not None:
        chips.append(
            ScopeChipV0(
                kind="comparison",
                label=ir.comparison.source_text,
                canonical_ref=ir.comparison.mode,
            )
        )

    unique: list[ScopeChipV0] = []
    seen: set[tuple[str, str, str | None]] = set()
    for chip in chips:
        key = (chip.kind, chip.label, chip.canonical_ref)
        if key not in seen:
            seen.add(key)
            unique.append(chip)
    return tuple(unique)


def _current_tables(core: AskV2Day4Response) -> tuple[ConversationTableV0, ...]:
    return tuple(
        ConversationTableV0(
            execution_id=result.execution_id,
            role=result.role,
            columns=result.columns,
            rows=result.rows,
            row_count=result.row_count,
            truncated=False,
        )
        for result in core.executions
    )


def _existing_tables(core: AskV2Day4Response) -> tuple[ConversationTableV0, ...]:
    anchor = core.existing_result
    if anchor is None:
        return ()
    return tuple(
        ConversationTableV0(
            execution_id=result.execution_id,
            role=result.role,
            columns=result.columns,
            rows=result.rows,
            row_count=result.row_count,
            truncated=result.truncated,
        )
        for result in anchor.executions
    )


def _evidence_refs(core: AskV2Day4Response) -> tuple[EvidenceRefV0, ...]:
    if core.query_contracts:
        return tuple(
            EvidenceRefV0(
                contract_id=contract.contract_id,
                execution_id=contract.execution_id,
                role=next(
                    (
                        execution.role
                        for execution in core.executions
                        if execution.execution_id == contract.execution_id
                    ),
                    "primary",
                ),
                sealed=contract.sealed,
            )
            for contract in core.query_contracts
        )

    anchor = core.existing_result
    if anchor is None:
        return ()

    refs: list[EvidenceRefV0] = []
    for index, contract_id in enumerate(anchor.contract_refs):
        execution = anchor.executions[index] if index < len(anchor.executions) else None
        refs.append(
            EvidenceRefV0(
                contract_id=contract_id,
                execution_id=execution.execution_id if execution else f"existing-{index}",
                role=execution.role if execution else "primary",
                sealed=anchor.verified,
            )
        )
    return tuple(refs)


class ConversationFinalizerV0:
    """Single owner for Core MVP wording/presentation, never semantic meaning."""

    def finalize(self, core: AskV2Day4Response) -> AskV2CoreResponse:
        ir = core.analytics_ir
        if ir is None and core.dialogue_action == DialogueAction.EXPLAIN_EXISTING:
            ir = core.conversation.last_ir

        scope = _scope_chips(ir, core.hypotheses)
        evidence = _evidence_refs(core)
        tables: tuple[ConversationTableV0, ...] = ()

        if core.dialogue_action == DialogueAction.RESEARCH_BRIEF:
            brief = core.research_brief
            if brief is None:
                response = ConversationResponseV0(
                    kind=ConversationResponseKind.FAILURE,
                    text="Typed ResearchBrief üretilemedi.",
                    official_verified=False,
                )
            elif brief.status == ResearchBriefStatus.READY_FOR_RESEARCH:
                goals = "\n".join(
                    f"- {question.source_text}" for question in brief.questions
                )
                response = ConversationResponseV0(
                    kind=ConversationResponseKind.RESEARCH_BRIEF,
                    text=(
                        "Araştırma sözleşmesi hazır. İncelenecek MUST hedefler:\n"
                        + goals
                    ),
                    official_verified=False,
                )
            else:
                blocked = {
                    question.goal_id: question.source_text
                    for question in brief.questions
                    if question.goal_id in brief.blocking_goal_ids
                }
                lines = "\n".join(
                    f"- {source_text}" for source_text in blocked.values()
                )
                response = ConversationResponseV0(
                    kind=ConversationResponseKind.SEMANTIC_GAP,
                    text=(
                        "Araştırma hedefleri kaybolmadan korundu; ancak şu MUST hedefler "
                        "güvenilir semantic bağ kurulmadan araştırmaya açılamaz:\n"
                        + lines
                    ),
                    # Research clarification resume is intentionally not a Day 6 feature.
                    clarification_chips=(),
                    official_verified=False,
                )
        elif core.dialogue_action == DialogueAction.CLARIFY:
            clarification = core.clarification
            kind = (
                ConversationResponseKind.SEMANTIC_GAP
                if core.semantic_status == "semantic_gap"
                else ConversationResponseKind.CLARIFY
            )
            response = ConversationResponseV0(
                kind=kind,
                text=(
                    clarification.question
                    if clarification is not None and clarification.question
                    else "Bu isteği güvenilir biçimde çözmek için bir noktayı netleştirmem gerekiyor."
                ),
                scope_chips=scope,
                clarification_chips=clarification.chips if clarification is not None else (),
                official_verified=False,
            )
        elif core.dialogue_action == DialogueAction.TALK:
            response = ConversationResponseV0(
                kind=ConversationResponseKind.TALK,
                text="Tamam. Analitik bağlamı değiştirmeden devam edebiliriz.",
                official_verified=False,
            )
        elif core.dialogue_action == DialogueAction.EXPLAIN_EXISTING:
            tables = _existing_tables(core)
            if core.used_existing_result and core.existing_result is not None:
                if core.existing_result.executions:
                    body = " ".join(
                        _execution_text(execution)
                        for execution in core.existing_result.executions
                    )
                    text = f"Mevcut doğrulanmış sonuç üzerinden: {body}"
                else:
                    text = "Mevcut doğrulanmış sonucun kanıt kaydı korunuyor."
                response = ConversationResponseV0(
                    kind=ConversationResponseKind.EXPLAIN,
                    text=text,
                    scope_chips=scope,
                    evidence_refs=evidence,
                    tables=tables,
                    official_verified=core.existing_result.verified,
                )
            else:
                message = core.failure.message if core.failure else "Açıklanacak aktif doğrulanmış sonuç yok."
                response = ConversationResponseV0(
                    kind=ConversationResponseKind.FAILURE,
                    text=message,
                    scope_chips=scope,
                    official_verified=False,
                )
        elif (
            core.dialogue_action == DialogueAction.ANALYTIC_STANDARD
            and core.analytics_status == "verified"
            and core.official_verified
        ):
            tables = _current_tables(core)
            if len(core.executions) > 1:
                detail = " ".join(
                    (
                        "Ana: " if execution.role == "primary" else "Referans: "
                    )
                    + _execution_text(execution)
                    for execution in core.executions
                )
                text = f"Karşılaştırma doğrulandı. {detail}"
            elif core.executions:
                text = _execution_text(core.executions[0])
            else:
                text = "Sorgu doğrulandı; gösterilecek sonuç satırı dönmedi."
            response = ConversationResponseV0(
                kind=ConversationResponseKind.ANSWER,
                text=text,
                scope_chips=scope,
                evidence_refs=evidence,
                tables=tables,
                official_verified=True,
            )
        elif core.dialogue_action == DialogueAction.UNSUPPORTED:
            response = ConversationResponseV0(
                kind=ConversationResponseKind.UNSUPPORTED,
                text=(
                    core.failure.message
                    if core.failure is not None
                    else "Bu istek Core MVP'nin standard analitik kapsamı dışında."
                ),
                scope_chips=scope,
                official_verified=False,
            )
        else:
            response = ConversationResponseV0(
                kind=ConversationResponseKind.FAILURE,
                text=(
                    core.failure.message
                    if core.failure is not None
                    else "Bu tur güvenilir bir Core MVP sonucuna dönüştürülemedi."
                ),
                scope_chips=scope,
                evidence_refs=evidence,
                official_verified=False,
            )

        payload = core.model_dump(mode="python")
        is_research = core.dialogue_action == DialogueAction.RESEARCH_BRIEF
        payload.update(
            {
                "status": "research_brief" if is_research else "core_mvp",
                "stage": "day6_research_brief" if is_research else "day5_core_mvp",
                "response": response,
                "next_stage": core.next_stage if is_research else "core_mvp_gate",
            }
        )
        return AskV2CoreResponse.model_validate(payload)
