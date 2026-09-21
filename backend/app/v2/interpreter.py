"""P4 TurnInterpreter — the single natural-language owner in Dima V2.

The interpreter translates the current user turn into a typed surface-level contract.
It never chooses canonical semantic IDs, writes SQL, resolves ambiguity, or executes data.
"""

from __future__ import annotations

import json
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from pydantic import ValidationError

from app.v2.research import ResearchModePolicy

from app.v2.models import (
    BoundedSemanticContextV0,
    ConversationStateV2,
    PresentationKind,
    ResearchGoalKind,
    ResearchNonRelationshipGoalKind,
    SemanticMentionKind,
    TurnAct,
    TurnInterpretation,
    TurnInterpretationFailure,
)

_INTERPRETER_VERSION = "day6-v0.6"


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

    research = turn.research_request
    if research is not None:
        for goal in research.goals:
            spans.append(goal.text)
            spans.extend(m.text for m in goal.subject_mentions)
            spans.extend(m.text for m in goal.related_mentions)
        for relationship in research.relationships:
            spans.append(relationship.text)
            spans.extend(m.text for m in relationship.focus_mentions)
            spans.extend(m.text for m in relationship.counterpart_mentions)
        spans.extend(m.text for m in research.time_mentions)
        spans.extend(item.text for item in research.deliverables)

    if turn.user_repair is not None:
        spans.extend(turn.user_repair.correction_spans)
    return spans


def _source_tokens(question: str) -> list[tuple[int, int]]:
    """Return exact token character spans from the current message only."""
    return [(m.start(), m.end()) for m in re.finditer(r"[\wÇĞİÖŞÜçğıöşü-]+", question, flags=re.UNICODE)]


def _align_near_copy_surface(question: str, span: str) -> str:
    """Restore a model-normalized/typo-corrected span to the exact user surface.

    This is deliberately conservative: same token count, unique best contiguous window,
    high character similarity. It never chooses canonical semantics; it only repairs the
    TurnInterpreter source-copy contract.
    """
    normalized = _normalized_surface(span)
    if normalized and normalized in _normalized_surface(question):
        return span

    wanted_tokens = re.findall(r"[\wÇĞİÖŞÜçğıöşü-]+", span, flags=re.UNICODE)
    token_spans = _source_tokens(question)
    width = len(wanted_tokens)
    if width == 0 or width > len(token_spans):
        return span

    scored: list[tuple[float, str]] = []
    for i in range(0, len(token_spans) - width + 1):
        start = token_spans[i][0]
        end = token_spans[i + width - 1][1]
        candidate = question[start:end]
        ratio = SequenceMatcher(
            None,
            _normalized_surface(span),
            _normalized_surface(candidate),
        ).ratio()
        scored.append((ratio, candidate))

    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored or scored[0][0] < 0.78:
        return span
    if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.05:
        return span
    return scored[0][1]


def _align_turn_surfaces(question: str, turn: TurnInterpretation) -> TurnInterpretation:
    """Conservatively restore near-copy spans before strict grounding validation."""
    def aligned_model(item):
        fixed = _align_near_copy_surface(question, item.text)
        return item if fixed == item.text else item.model_copy(update={"text": fixed})

    request = turn.analytical_request
    if request is not None:
        updates = {
            "metric_mentions": tuple(aligned_model(x) for x in request.metric_mentions),
            "dimension_mentions": tuple(aligned_model(x) for x in request.dimension_mentions),
            "filter_mentions": tuple(aligned_model(x) for x in request.filter_mentions),
            "time_mentions": tuple(aligned_model(x) for x in request.time_mentions),
            "comparisons": tuple(aligned_model(x) for x in request.comparisons),
        }
        if request.ranking is not None:
            updates["ranking"] = aligned_model(request.ranking)
        request = request.model_copy(update=updates)

    research = turn.research_request
    if research is not None:
        research = research.model_copy(
            update={
                "goals": tuple(
                    goal.model_copy(
                        update={
                            "text": _align_near_copy_surface(question, goal.text),
                            "subject_mentions": tuple(
                                aligned_model(x) for x in goal.subject_mentions
                            ),
                            "related_mentions": tuple(
                                aligned_model(x) for x in goal.related_mentions
                            ),
                        }
                    )
                    for goal in research.goals
                ),
                "relationships": tuple(
                    relationship.model_copy(
                        update={
                            "text": _align_near_copy_surface(
                                question, relationship.text
                            ),
                            "focus_mentions": tuple(
                                aligned_model(x)
                                for x in relationship.focus_mentions
                            ),
                            "counterpart_mentions": tuple(
                                aligned_model(x)
                                for x in relationship.counterpart_mentions
                            ),
                        }
                    )
                    for relationship in research.relationships
                ),
                "time_mentions": tuple(
                    aligned_model(x) for x in research.time_mentions
                ),
                "deliverables": tuple(
                    item.model_copy(
                        update={
                            "text": _align_near_copy_surface(question, item.text)
                        }
                    )
                    for item in research.deliverables
                ),
            }
        )

    repair = turn.user_repair
    if repair is not None:
        repair = repair.model_copy(
            update={
                "correction_spans": tuple(
                    _align_near_copy_surface(question, span)
                    for span in repair.correction_spans
                )
            }
        )

    return turn.model_copy(
        update={
            "references": tuple(aligned_model(x) for x in turn.references),
            "unresolved_mentions": tuple(aligned_model(x) for x in turn.unresolved_mentions),
            "analytical_request": request,
            "research_request": research,
            "user_repair": repair,
        }
    )


def _complete_explicit_ranking_limit(question: str, turn: TurnInterpretation) -> TurnInterpretation:
    """Bind an explicit adjacent numeric top-N token without semantic guessing.

    The model has already anchored the ranking surface. Copying an immediately adjacent
    numeric token from the same source phrase is a language-contract repair owned by
    TurnInterpreter, not a planner or business-semantic decision.
    """
    request = turn.analytical_request
    if request is None or request.ranking is None:
        return turn

    ranking = request.ranking
    limit = ranking.limit
    text = ranking.text

    in_span = re.search(r"(?<!\d)([1-9]\d{0,3})(?!\d)", text)
    if limit is None and in_span is not None:
        value = int(in_span.group(1))
        if value <= 1000:
            limit = value

    exact_positions = [m for m in re.finditer(re.escape(text), question, flags=re.IGNORECASE)]
    if len(exact_positions) == 1:
        match = exact_positions[0]
        suffix = question[match.end():]
        adjacent = re.match(r"([\s:,-]*)([1-9]\d{0,3})(?=\b)", suffix)
        if adjacent is not None:
            value = int(adjacent.group(2))
            if value <= 1000:
                if limit is None:
                    limit = value
                if str(value) not in text:
                    text = question[match.start(): match.end() + adjacent.end()]

    if limit == ranking.limit and text == ranking.text:
        return turn
    updated_ranking = ranking.model_copy(update={"text": text, "limit": limit})
    return turn.model_copy(
        update={
            "analytical_request": request.model_copy(update={"ranking": updated_ranking})
        }
    )


def _normalize_interpretation(question: str, turn: TurnInterpretation) -> TurnInterpretation:
    turn = _align_turn_surfaces(question, turn)
    turn = _complete_explicit_ranking_limit(question, turn)
    return turn


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
- semantic/reference/unresolved/repair/research alanlarındaki her 'text' değeri
  CURRENT_MESSAGE içinden kopyalanmış surface span olmalı. Katalogdaki canonical adı
  output'a taşıma.
- Semantic context yalnız kullanıcının sözünün analitik mi/sosyal mi olduğunu ve hangi
  YÜZEY türlerinin geçtiğini anlamak içindir. Binding Day 2 SemanticResolver işidir.
- Bir ifade birden fazla gerçek kavrama bağlanabilecekse seçim yapma; surface ifadeyi
  unresolved_mentions içine yaz.
- Tarih aritmetiği yapma. 'son üç ay', 'bu ay', 'geçen yılla' gibi ifadeyi yalnız
  surface text olarak taşı.
- k=1: alternatif yorum listesi üretme.
- DIALOGUE ACT KARAR SIRASI (conversation precedence):
  1) Saf selam/teşekkür/onay ve yeni analitik talep yoksa SOCIAL.
  2) pending clarification'a cevap ise CLARIFICATION_ANSWER.
  3) aktif verified sonucu açıklatma ise RESULT_EXPLAIN.
  4) önceki analitik seçimi açıkça geri alma/değiştirme ise USER_REPAIR.
  5) önceki analitik talebi yanlışlamadan scope/filter/breakdown ekleme ise ANALYTIC_REFINE.
  6) bağımsız yeni analitik talep için ANALYTIC_NEW veya COMPLEX_ANALYSIS üret.
     Bu seçim yalnız analytical operation shape'i tarif eder; final STANDARD/RESEARCH
     routing authority ResearchModePolicy'dir.
  7) REPORT_REQUEST geriye dönük şema desteği için kabul edilir ama SUNUM kararı değildir.
     "rapor/chart/table" kelimesi tek başına bu act'i seçme sebebi OLAMAZ.
- Presentation orthogonal eksendir: presentation_request ve research deliverables,
  analytical complexity kararını değiştirmez.
- USER_REPAIR kararı kelime ezberi değildir; semantik olarak "önceki seçim yanlıştı,
  bunu onun yerine koy" anlamını gerektirir. Yalnız kapsam daraltmak veya ilk kez bir
  entity filter eklemek REPAIR DEĞİL REFINE'dır.
- ANALYTIC_REFINE ile USER_REPAIR ayrımının iki aşamalı testi:
  A) Kullanıcı önceki tercihin yanlış/geri alınmış olduğunu bildiriyor mu?
     Hayır → REFINE (yeni filtre ekleme/daraltma dahil).
     Evet → B'ye geç.
  B) Yeni surface önceki seçimin yerine mi geçiyor?
     Evet → USER_REPAIR.
     Hayır → REFINE.
- Soyut örnekler (fixture değildir):
  prior period=A; "A değil, B olsun" → USER_REPAIR + yalnız B time surface.
  prior filter yok; "yalnız <member> kalsın" → ANALYTIC_REFINE + yalnız filter surface.
  prior analytics var; "tamam/teşekkür" → SOCIAL, analytical_request yok.
- ANALYTIC_REFINE ve USER_REPAIR'de analytical_request yalnız BU MESAJDA eklenen/değişen
  slotların surface span'lerini taşımalı. Önceki metric/dimension/filter/time slotlarını
  kullanıcı bu mesajda tekrar etmediyse output'a yeniden yazma.
- USER_REPAIR'de user_repair.correction_spans düzeltme/retraction anlamını taşıyan
  CURRENT_MESSAGE parçalarını taşır; hangi canonical slotun değişeceğine sen karar vermezsin.
- Düzeltme/retraction işlevi gören söylem parçaları business semantic mention değildir.
  Bir parça yalnız "hayır/yok/değil/onu değil/vazgeçtim/yerine" gibi önceki seçimi reddetme
  veya değiştirme işlevi görüyorsa onu references, unresolved_mentions veya analytical_request
  semantic mention alanlarına ASLA koyma. Bu parçayı yalnız user_repair.correction_spans içinde
  taşı. Replacement metric/dimension/filter/time surface'i analytical_request'te kendi gerçek
  rolünde kalır. Correction marker'ın kendisi SemanticResolver'a gönderilecek bir business
  kavramı değildir.
- CLARIFICATION_ANSWER yalnız CONVERSATION_STATE_JSON.pending_clarification=true ise
  mümkündür. pending_clarification=false ise bu act'i ASLA seçme; mesaj düzeltmeyse
  USER_REPAIR, ekleme/daraltmaysa ANALYTIC_REFINE, bağımsız soruyorsa ANALYTIC_NEW'dur.
- Yeni analitik soru ANALYTIC_NEW.
- Saf selam/teşekkür/gündelik sosyal tur SOCIAL.
- Veri/ürün kapsamında olmayan ve analitik niyet taşımayan istek UNSUPPORTED.

RESEARCH_REQUEST — rich typed analytical surface:
- Final STANDARD/RESEARCH route ResearchModePolicy'nindir. Presentation bu karara girmez.
- goals[] yalnız NON-RELATIONSHIP analytical operation taşır:
  comparison, performance, trend, breakdown, ranking, root_cause, other.
- RELATIONSHIP goals[] içinde temsil EDİLMEZ; relationships[] kullanılır.
- relationships[] kaydı tek bir focus ve bir veya daha fazla counterpart taşır:
  * text = ilişki isteğini kanıtlayan exact CURRENT_MESSAGE span,
  * focus_mentions = ilişkisi incelenen focus; aynı CURRENT_MESSAGE içinde daha önce
    açıkça söylenmişse o exact source surface yeniden kullanılabilir,
  * counterpart_mentions = focus ile ilişkisi istenen explicit counterpart surface'leri.
  Focus dilde gerçekten kurulmamışsa boş bırak; downstream tahmin etmez.
- N counterpart tek relationship request içinde taşınabilir; typed compiler bunu N atomik
  ResearchQuestion'a açar. Aynı edge'i tekrar üretme.
- Kullanıcının açıkça reddettiği operation/counterpart'ı taşıma. Aynı operation'ın yalnız
  yeniden söylenmesi yeni requirement değildir.
- goals[].text, subject_mentions, related_mentions ve relationship endpoint'leri yalnız
  CURRENT_MESSAGE source evidence'ıdır; canonical ID/binding yoktur.
- STANDARD-capable operation için Core'un ihtiyaç duyduğu typed payload'ı kaybetme:
  * ranking operation → ranking zorunlu; direction/limit yalnız explicit ise,
  * comparison operation → explicit Core period/reference comparison varsa comparisons[].
  Policy bu bilgiyi goal.text'ten geri çıkarmayacaktır.
- Açık output isteğini deliverables[] içinde source-grounded taşı. Deliverable analytical
  question değildir ve route sebebi değildir.
- time_mentions yalnız explicit dönem/süre surface'lerini taşır.
- Semantic context'te tanınmayan explicit mention'ı düşürme; kind=unknown ile exact
  surface'i koru. Resolver binding/clarification/gap sahibidir.

ANALYTICAL_REQUEST:
- metric_mentions, dimension_mentions, filter_mentions, time_mentions yalnız surface span.
- DIMENSION = "hangi eksene göre gruplayalım/kıralım?" sorusunun cevabı olan kategori türü.
- FILTER = "hangi somut üye/değer(ler) kalsın?" sorusunun cevabı olan seçili scope.
- Bir kullanıcının "yalnız/sadece/bir tek <somut üye>" anlamındaki seçimi grouping değildir;
  o surface FILTER'dır. Canonical modele bağlama yapma; yalnız dil rolünü ayır.
- Buna karşılık "<kategori> bazında", "<kategori>lere göre", "<kategori> kırılımında"
  gibi grouping niyeti DIMENSION'dır.
- Bir surface'in katalogdaki dimension adına benzemesi onu dimension yapmaz; cümlede somut
  member/value rolündeyse filter_mentions'a koy.
- Aynı exact surface'i, kullanıcı aynı mesajda açıkça hem grouping hem filtering istemiyorsa
  dimension_mentions ve filter_mentions içine birlikte koyma.
- ranking varsa ranking.text CURRENT_MESSAGE içindeki ranking ifadesinin TAM surface span'i olmalı.
  Açık top-N sayısı varsa (örn. "en yüksek 2") sayıyı ranking.text içinde KORU ve limit=2 yaz;
  sayıyı düşürme, yeniden yazma veya tahmin etme. limit yalnız açıkça yazıldıysa.
- Yazım hatalarını DÜZELTME: mention text alanları kullanıcının yazdığı biçimi birebir taşımalı.
  Örn. kullanıcı "bolge" veya "net gelr" yazdıysa output da aynı surface'i kullanır; "bölge"/"net gelir" diye normalleştirme yapma.
- time_mentions yalnız açık bir takvim/göreli dönem veya süre surface'idir; durum/aspect/soru kalıbı time değildir.
- comparison ifadelerini hesaplama; reference/comparison surface'ini comparisons içine taşı. Aynı reference period span'ini time_mentions içine ayrıca kopyalama; time_mentions varsa base/current period içindir.
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


def _normalize_surface_role_overlap(turn: TurnInterpretation) -> TurnInterpretation:
    """Remove exact surface-role duplication without changing semantic meaning.

    A comparison reference is sometimes emitted twice by the language model: once as a
    TIME mention and again as part of COMPARISON. The reference period belongs to the
    comparison role; leaving the duplicate in time_mentions makes the temporal owner see
    two base periods. This normalization only removes a time span when its own grounded
    text is wholly contained in a grounded comparison span. No date phrase is parsed and
    no replacement meaning is inferred here.
    """
    request = turn.analytical_request
    if request is None or not request.time_mentions or not request.comparisons:
        return turn

    comparisons = tuple(_normalized_surface(item.text) for item in request.comparisons)
    kept = tuple(
        mention
        for mention in request.time_mentions
        if not any(
            normalized
            and normalized in comparison
            for normalized in (_normalized_surface(mention.text),)
            for comparison in comparisons
        )
    )
    if kept == request.time_mentions:
        return turn
    return turn.model_copy(
        update={
            "analytical_request": request.model_copy(update={"time_mentions": kept})
        }
    )


def _enum_value(value: Any, enum_type) -> Any:
    """Case-insensitive enum spelling repair; never changes semantic category.

    Provider structured-text transports do not enforce JSON Schema enums. Gemini can
    emit an enum name (e.g. RELATIONSHIP) instead of the schema value (relationship).
    Mapping a case-insensitive exact enum name/value back to its declared value is a
    format normalization, not a semantic retry.
    """
    if not isinstance(value, str):
        return value
    folded = value.strip().casefold()
    for member in enum_type:
        if folded in {member.name.casefold(), str(member.value).casefold()}:
            return member.value
    return value


def _normalize_structured_payload(data: Any) -> Any:
    """Normalize transport-level JSON spelling only; never repair business meaning.

    This boundary may normalize enum casing and structurally split an already-explicit
    relationship endpoint list. It does not migrate old semantic schemas, invent goals,
    infer standard/research mode, or recover missing ranking/comparison semantics.
    """
    if not isinstance(data, dict):
        return data

    out = dict(data)
    if "dialogue_act" in out:
        out["dialogue_act"] = _enum_value(out.get("dialogue_act"), TurnAct)
    if out.get("presentation_request") is None:
        out.pop("presentation_request", None)
    else:
        out["presentation_request"] = _enum_value(
            out.get("presentation_request"), PresentationKind
        )

    research = out.get("research_request")
    if isinstance(research, dict):
        research = dict(research)

        def normalize_mention(raw_mention):
            if not isinstance(raw_mention, dict):
                return raw_mention
            mention = dict(raw_mention)
            mention["kind"] = _enum_value(
                mention.get("kind"), SemanticMentionKind
            )
            return mention

        deliverables = []
        for raw_deliverable in research.get("deliverables") or ():
            if not isinstance(raw_deliverable, dict):
                deliverables.append(raw_deliverable)
                continue
            item = dict(raw_deliverable)
            item["kind"] = _enum_value(item.get("kind"), PresentationKind)
            deliverables.append(item)

        relationships = []
        for raw_relationship in research.get("relationships") or ():
            if not isinstance(raw_relationship, dict):
                relationships.append(raw_relationship)
                continue
            relationship = dict(raw_relationship)
            relationship["focus_mentions"] = [
                normalize_mention(item)
                for item in (relationship.get("focus_mentions") or ())
            ]
            relationship["counterpart_mentions"] = [
                normalize_mention(item)
                for item in (relationship.get("counterpart_mentions") or ())
            ]
            relationships.append(relationship)

        goals = []
        for raw_goal in research.get("goals") or ():
            if not isinstance(raw_goal, dict):
                goals.append(raw_goal)
                continue

            goal = dict(raw_goal)
            goal["kind"] = _enum_value(
                goal.get("kind"), ResearchNonRelationshipGoalKind
            )
            goal["subject_mentions"] = [
                normalize_mention(item)
                for item in (goal.get("subject_mentions") or ())
            ]
            goal["related_mentions"] = [
                normalize_mention(item)
                for item in (goal.get("related_mentions") or ())
            ]

            ranking = goal.get("ranking")
            if isinstance(ranking, dict):
                ranking = dict(ranking)
                direction = ranking.get("direction")
                if isinstance(direction, str):
                    folded = direction.strip().casefold()
                    if folded in {"asc", "desc", "unspecified"}:
                        ranking["direction"] = folded
                goal["ranking"] = ranking

            goal["comparisons"] = [
                dict(item) if isinstance(item, dict) else item
                for item in (goal.get("comparisons") or ())
            ]
            goals.append(goal)

        # Exact duplicate deliverables are a transport duplicate, not a new MUST.
        deduped_deliverables = []
        seen_deliverables = set()
        for item in deliverables:
            if not isinstance(item, dict):
                deduped_deliverables.append(item)
                continue
            key = (
                str(item.get("kind") or "").casefold(),
                _normalized_surface(str(item.get("text") or "")),
            )
            if key in seen_deliverables:
                continue
            seen_deliverables.add(key)
            deduped_deliverables.append(item)

        research["goals"] = goals
        research["relationships"] = relationships
        research["time_mentions"] = [
            normalize_mention(item)
            for item in (research.get("time_mentions") or ())
        ]
        research["deliverables"] = deduped_deliverables
        out["research_request"] = research

    return out


def _parse(raw: str) -> TurnInterpretation:
    try:
        data = json.loads(_strip_json_fence(raw))
        data = _normalize_structured_payload(data)
        turn = TurnInterpretation.model_validate(data)
        return _normalize_surface_role_overlap(turn)
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

        turn = _normalize_interpretation(question, turn)
        _validate_surface_grounding(question, turn)

        # Final STANDARD/RESEARCH routing is deterministic and presentation-agnostic.
        # This happens only after every provider surface has passed source grounding,
        # so projection cannot hide hallucinated research/deliverable text.
        turn = ResearchModePolicy().decide(turn).canonical_turn
        return turn
