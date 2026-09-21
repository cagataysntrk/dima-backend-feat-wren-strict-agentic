"""P4 TurnInterpreter — the single natural-language owner in Dima V2.

The interpreter translates the current user turn into a typed surface-level contract.
It never chooses canonical semantic IDs, writes SQL, resolves ambiguity, or executes data.
"""

from __future__ import annotations

import json
import unicodedata
from typing import Any

from pydantic import ValidationError

from app.v2.models import (
    BoundedSemanticContextV0,
    ConversationStateV2,
    TurnInterpretation,
    TurnInterpretationFailure,
)

_INTERPRETER_VERSION = "day4-v0.2"


class TurnInterpreterError(RuntimeError):
    def __init__(self, failure: TurnInterpretationFailure):
        super().__init__(failure.message)
        self.failure = failure


def _compact_json(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json", exclude_none=True)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalized_surface(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(text))
    normalized = normalized.casefold().replace("\u0307", "")
    return " ".join(normalized.split())


def _safe_anchor(anchor) -> dict | None:
    if anchor is None:
        return None
    return {
        "target_kind": anchor.target_kind.value,
        "canonical_name": anchor.canonical_name,
        "dimension_name": anchor.dimension_name,
        "display_label": anchor.display_label,
        "value": None if anchor.sensitive else anchor.value,
        "sensitive": anchor.sensitive,
    }


def _conversation_prompt_view(conversation: ConversationStateV2) -> dict:
    """Expose only bounded conversation cues; never dump prior result rows or full IR."""
    focus = conversation.focus
    clarification = conversation.clarification_state
    return {
        "has_prior_analytical_request": conversation.has_prior_analytical_request,
        "has_active_result": conversation.has_active_result,
        "pending_clarification": conversation.pending_clarification,
        "topic_labels": list(conversation.topic_labels),
        "focus_labels": list(conversation.focus_labels),
        "selected_anchor_label": conversation.selected_anchor_label,
        "selected_anchor": _safe_anchor(conversation.selected_anchor),
        "focus_anchors": [
            _safe_anchor(anchor) for anchor in conversation.focus_anchors
        ],
        "topic": (
            {
                "topic_id": conversation.topic.topic_id,
                "cube": conversation.topic.cube,
                "context_version": conversation.topic.context_version,
            }
            if conversation.topic is not None
            else None
        ),
        "focus": (
            {
                "metrics": [item.canonical_name for item in focus.metrics],
                "dimensions": [item.canonical_name for item in focus.dimensions],
                "filter_dimensions": [item.dimension_name for item in focus.filters],
                "period_kind": focus.period.kind.value if focus.period is not None else None,
                "last_contract_refs": list(focus.last_contract_refs),
            }
            if focus is not None
            else None
        ),
        "clarification": (
            {
                "pending": clarification.pending,
                "source_kind": (
                    clarification.source_kind.value
                    if clarification.source_kind is not None
                    else None
                ),
                "question": clarification.question,
            }
            if clarification is not None
            else None
        ),
        "pending_operation": (
            conversation.pending_analytical.dialogue_act.value
            if conversation.pending_analytical is not None
            else None
        ),
    }


def _strip_json_fence(raw: str) -> str:
    text = (raw or "").strip()
    if text.startswith("~~~json"):
        text = text[7:]
        if text.rstrip().endswith("~~~"):
            text = text.rstrip()[:-3]
    return text.strip()


def _surface_spans(turn: TurnInterpretation) -> list[str]:
    spans: list[str] = []
    spans.extend(m.text for m in turn.references)
    spans.extend(m.text for m in turn.unresolved_mentions)

    req = turn.analytical_request
    if req is not None:
        for group in (
            req.metric_mentions,
            req.dimension_mentions,
            req.filter_mentions,
            req.time_mentions,
        ):
            spans.extend(m.text for m in group)
        if req.ranking is not None:
            spans.append(req.ranking.text)
        spans.extend(c.text for c in req.comparisons)

    if turn.user_repair is not None:
        spans.extend(turn.user_repair.correction_spans)
    return spans


def _validate_surface_grounding(question: str, turn: TurnInterpretation) -> None:
    """Reject invented/canonicalized mentions before they can become semantic authority."""
    haystack = _normalized_surface(question)
    bad = [
        span
        for span in _surface_spans(turn)
        if not _normalized_surface(span)
        or _normalized_surface(span) not in haystack
    ]
    if bad:
        raise TurnInterpreterError(
            TurnInterpretationFailure(
                code="surface_grounding_violation",
                message=(
                    "TurnInterpreter kullanıcı mesajında bulunmayan surface span üretti: "
                    + ", ".join(repr(x) for x in bad[:5])
                ),
            )
        )


def _system_prompt() -> str:
    schema = TurnInterpretation.model_json_schema()
    return f"""Sen Dima V2 TurnInterpreter'sın. Kullanıcının BU TURDA ne yaptığını
tek seferde typed bir dil sözleşmesine çevirirsin. Sen semantic resolver, planner veya
SQL üreticisi değilsin.

SÜRÜM: {_INTERPRETER_VERSION}

MUTLAK SINIRLAR:
- SADECE JSON döndür; markdown/açıklama ekleme.
- Çıktı aşağıdaki JSON Schema'ya uymalı.
- SQL, tablo adı, fiziksel kolon, CubeQuery veya sorgu planı üretme.
- Canonical metric/dimension/entity ID SEÇME ve UYDURMA.
- semantic/reference/unresolved/repair alanlarındaki her 'text' değeri CURRENT_MESSAGE
  içinden kopyalanmış surface span olmalı. Katalogdaki canonical adı output'a taşıma.
- Semantic context yalnız kullanıcının sözünün analitik mi/sosyal mi olduğunu ve hangi
  YÜZEY türlerinin geçtiğini anlamak içindir. Binding Day 2 SemanticResolver işidir.
- Bir ifade birden fazla gerçek kavrama bağlanabilecekse seçim yapma; surface ifadeyi
  unresolved_mentions içine yaz.
- Tarih aritmetiği yapma. 'son üç ay', 'bu ay', 'geçen yılla' gibi ifadeyi yalnız
  surface text olarak taşı.
- k=1: alternatif yorum listesi üretme.
- Kullanıcı mevcut sonucu açıklatıyorsa ve active result varsa RESULT_EXPLAIN.
- Kullanıcı önceki analitik isteği geliştiriyorsa ANALYTIC_REFINE.
- 'hayır / değil / demek istediğim' gibi önceki isteği düzeltiyorsa USER_REPAIR.
- ANALYTIC_REFINE ve USER_REPAIR'de analytical_request yalnız BU MESAJDA eklenen/değişen
  slotların surface span'lerini taşımalı. Önceki metric/dimension/filter/time slotlarını
  kullanıcı bu mesajda tekrar etmediyse output'a yeniden yazma.
- USER_REPAIR'de user_repair.correction_spans düzeltmeyi işaret eden CURRENT_MESSAGE
  parçalarını taşır; hangi canonical slotun değişeceğine sen karar vermezsin.
- pending_clarification=true ve kullanıcı o soruya cevap veriyorsa CLARIFICATION_ANSWER.
- Yeni analitik soru ANALYTIC_NEW.
- Saf selam/teşekkür/gündelik sosyal tur SOCIAL.
- Veri/ürün kapsamında olmayan ve analitik niyet taşımayan istek UNSUPPORTED.

ANALYTICAL_REQUEST:
- metric_mentions, dimension_mentions, filter_mentions, time_mentions yalnız surface span.
- ranking varsa ranking.text de CURRENT_MESSAGE span'i olmalı; limit yalnız açıkça yazıldıysa.
- comparison ifadelerini hesaplama; surface span olarak taşı.
- canonical ref alanı YOKTUR ve ek alan üretmek yasaktır.

JSON_SCHEMA:
{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}
"""


def _user_prompt(
    question: str,
    semantic_context: BoundedSemanticContextV0,
    conversation: ConversationStateV2,
) -> str:
    return (
        "CURRENT_MESSAGE:\n"
        + question
        + "\n\nCONVERSATION_STATE_JSON:\n"
        + _compact_json(_conversation_prompt_view(conversation))
        + "\n\nBOUNDED_SEMANTIC_CONTEXT_JSON:\n"
        + _compact_json(semantic_context)
    )


def _parse(raw: str) -> TurnInterpretation:
    try:
        data = json.loads(_strip_json_fence(raw))
        return TurnInterpretation.model_validate(data)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc


class TurnInterpreter:
    """One structured call; at most one format-only retry; no semantic retry."""

    def interpret(
        self,
        *,
        question: str,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        llm,
    ) -> TurnInterpretation:
        structured = getattr(llm, "structured_text", None)
        if not callable(structured):
            raise TurnInterpreterError(
                TurnInterpretationFailure(
                    code="llm_unavailable",
                    message="Configured provider structured language interpretation desteklemiyor.",
                )
            )

        system = _system_prompt()
        user = _user_prompt(question, semantic_context, conversation)

        try:
            raw = structured(system, user)
        except Exception as exc:
            raise TurnInterpreterError(
                TurnInterpretationFailure(
                    code="llm_unavailable",
                    message=f"TurnInterpreter LLM çağrısı başarısız: {exc}",
                )
            ) from exc

        try:
            turn = _parse(raw)
        except ValueError as first_error:
            repair_system = (
                system
                + "\n\nFORMAT_REPAIR_ONLY: Önceki cevabın JSON/schema biçimi geçersizdi. "
                  "Aynı semantic kararı DEĞİŞTİRMEDEN yalnız geçerli JSON olarak yeniden yaz. "
                  "Yeni yorum, canonical ID veya yeni mention ekleme."
            )
            repair_user = (
                user
                + "\n\nPREVIOUS_INVALID_OUTPUT:\n"
                + raw
                + "\n\nFORMAT_ERROR:\n"
                + str(first_error)[:1200]
            )
            try:
                repaired = structured(repair_system, repair_user)
                turn = _parse(repaired)
            except Exception as exc:
                raise TurnInterpreterError(
                    TurnInterpretationFailure(
                        code="invalid_structured_output",
                        message=f"TurnInterpreter bir format retry sonrasında da geçersiz çıktı: {exc}",
                    )
                ) from exc

        _validate_surface_grounding(question, turn)
        return turn
