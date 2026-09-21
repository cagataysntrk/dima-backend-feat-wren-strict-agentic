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
    ResearchComparisonFrame,
    ResearchDeliverableSurface,
    ResearchFocusBinding,
    ResearchGoalSurface,
    ResearchNonRelationshipGoalKind,
    ResearchOperationPolarity,
    ResearchRelationshipSurface,
    ResearchRequestSurface,
    ResearchRootCauseFrame,
    SemanticMention,
    SemanticMentionKind,
    TurnAct,
    TurnInterpretation,
    TurnInterpretationFailure,
    TurnInterpreterTransport,
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
    return f"""Sen Dima V2 TurnInterpreter'sın. Kullanıcının BU TURDA ne yaptığını
tek seferde typed bir dil sözleşmesine çevirirsin. Sen semantic resolver, planner veya
SQL üreticisi değilsin.

SÜRÜM: {_INTERPRETER_VERSION}

MUTLAK SINIRLAR:
- Çıktı transport katmanında native JSON Schema ile zorlanır; markdown/açıklama ekleme.
- Şemayı prompt metninden yeniden yorumlama; yalnız alanların semantik anlamına uy.
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

RESEARCH_GRAPH — source inventory → typed operation graph:
- Final STANDARD/RESEARCH route ResearchModePolicy'nindir. Presentation bu karara girmez.
- surfaces[] BU MESAJDA geçen semantic yüzeylerin tek envanteridir. Her surface:
  * current-message exact text,
  * yalnız bu graph içinde kullanılan local surface_id,
  * language role kind taşır.
  Bu local ID canonical semantic ID DEĞİLDİR; Resolver binding yapacaktır.
- Aynı semantic source span'i farklı operation'larda tekrar tekrar text olarak yazma;
  operation'lar local surface ref'leri kullanır.
- operations[] relationship dışındaki analytical requirement'lardır ve polarity zorunludur:
  requested → requirement üretir; excluded → kullanıcı açıkça reddetmiştir, requirement üretmez.
- root_cause ayrı typed frame'dir:
  * outcome_ref = açıklanması/kök nedeni araştırılması istenen sonuç,
  * factor_refs = kullanıcının aynı root-cause requirement'ında ilişkilendirdiği explicit faktörler.
  Aynı factor edge'ini ayrıca relationship olarak üretme; kullanıcı ayrıca ayrı relationship
  analizi istemişse o zaman iki ayrı requirement vardır.
- relationships[] yalnız ilişki requirement'ıdır:
  * counterpart_refs = explicit ilişki tarafları,
  * focus_binding=explicit ise focus_ref relationship.text içinde açıkça geçer,
  * focus_binding=antecedent ise focus_ref aynı CURRENT_MESSAGE içinde daha önce kurulmuş
    bir source surface'e bağlanır,
  * focus_binding=unresolved ise focus_ref=null; downstream focus tahmin etmez.
  Bir ilişki cümlesinde birden fazla counterpart varsa hepsini aynı frame'de ref olarak taşı;
  compiler bunları atomik edge'lere açar.
- Negation/exclusion keyword ezberi değildir. Dil seviyesinde reddedilen analytical operation
  veya deliverable polarity=excluded olarak işaretlenir; deterministic compiler yalnız
  requested olanları requirement'a dönüştürür.
- time_refs yalnız surfaces[] içindeki TIME surface ID'lerine referans verir.
- deliverables[] analytical question değildir; output requirement'ıdır ve polarity taşır.
- STANDARD-capable operation typed Core payload'ını kaybetmez:
  * ranking frame ranking payload'ını,
  * period/reference comparison frame comparisons[] payload'ını taşır.
  Policy operation text'ini yeniden parse ederek eksik slot tamamlamaz.
- Semantic context'te tanınmayan ama kullanıcıda explicit geçen surface'i düşürme;
  kind=unknown ile inventory'de koru. Resolver binding/clarification/gap sahibidir.

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
    """Normalize transport spelling only; never repair analytical meaning."""
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

    graph = out.get("research_graph")
    if isinstance(graph, dict):
        graph = dict(graph)

        surfaces = []
        for raw_surface in graph.get("surfaces") or ():
            if not isinstance(raw_surface, dict):
                surfaces.append(raw_surface)
                continue
            item = dict(raw_surface)
            item["kind"] = _enum_value(item.get("kind"), SemanticMentionKind)
            surfaces.append(item)

        operations = []
        for raw_operation in graph.get("operations") or ():
            if not isinstance(raw_operation, dict):
                operations.append(raw_operation)
                continue
            item = dict(raw_operation)
            item["kind"] = _enum_value(
                item.get("kind"), ResearchNonRelationshipGoalKind
            )
            item["polarity"] = _enum_value(
                item.get("polarity"), ResearchOperationPolarity
            )
            ranking = item.get("ranking")
            if isinstance(ranking, dict):
                ranking = dict(ranking)
                direction = ranking.get("direction")
                if isinstance(direction, str):
                    folded = direction.strip().casefold()
                    if folded in {"asc", "desc", "unspecified"}:
                        ranking["direction"] = folded
                item["ranking"] = ranking
            item["comparisons"] = [
                dict(value) if isinstance(value, dict) else value
                for value in (item.get("comparisons") or ())
            ]
            operations.append(item)

        relationships = []
        for raw_relationship in graph.get("relationships") or ():
            if not isinstance(raw_relationship, dict):
                relationships.append(raw_relationship)
                continue
            item = dict(raw_relationship)
            item["focus_binding"] = _enum_value(
                item.get("focus_binding"), ResearchFocusBinding
            )
            item["polarity"] = _enum_value(
                item.get("polarity"), ResearchOperationPolarity
            )
            relationships.append(item)

        deliverables = []
        for raw_deliverable in graph.get("deliverables") or ():
            if not isinstance(raw_deliverable, dict):
                deliverables.append(raw_deliverable)
                continue
            item = dict(raw_deliverable)
            item["kind"] = _enum_value(item.get("kind"), PresentationKind)
            item["polarity"] = _enum_value(
                item.get("polarity"), ResearchOperationPolarity
            )
            deliverables.append(item)

        graph["surfaces"] = surfaces
        graph["operations"] = operations
        graph["relationships"] = relationships
        graph["deliverables"] = deliverables
        out["research_graph"] = graph

    return out


def _parse(raw: str) -> TurnInterpreterTransport:
    try:
        data = json.loads(_strip_json_fence(raw))
        data = _normalize_structured_payload(data)
        return TurnInterpreterTransport.model_validate(data)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        raise ValueError(str(exc)) from exc


def _transport_surface_spans(turn: TurnInterpreterTransport) -> list[str]:
    spans: list[str] = []
    spans.extend(item.text for item in turn.references)
    spans.extend(item.text for item in turn.unresolved_mentions)

    request = turn.analytical_request
    if request is not None:
        for group in (
            request.metric_mentions,
            request.dimension_mentions,
            request.filter_mentions,
            request.time_mentions,
        ):
            spans.extend(item.text for item in group)
        if request.ranking is not None:
            spans.append(request.ranking.text)
        spans.extend(item.text for item in request.comparisons)

    graph = turn.research_graph
    if graph is not None:
        spans.extend(item.text for item in graph.surfaces)
        for operation in graph.operations:
            spans.append(operation.text)
            ranking = getattr(operation, "ranking", None)
            if ranking is not None:
                spans.append(ranking.text)
            spans.extend(item.text for item in getattr(operation, "comparisons", ()))
        spans.extend(item.text for item in graph.relationships)
        spans.extend(item.text for item in graph.deliverables)

    if turn.user_repair is not None:
        spans.extend(turn.user_repair.correction_spans)
    return spans


def _align_transport_surfaces(
    question: str,
    turn: TurnInterpreterTransport,
) -> TurnInterpreterTransport:
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

    graph = turn.research_graph
    if graph is not None:
        operations = []
        for operation in graph.operations:
            updates = {
                "text": _align_near_copy_surface(question, operation.text),
            }
            ranking = getattr(operation, "ranking", None)
            if ranking is not None:
                updates["ranking"] = aligned_model(ranking)
            comparisons = getattr(operation, "comparisons", None)
            if comparisons is not None:
                updates["comparisons"] = tuple(
                    aligned_model(item) for item in comparisons
                )
            operations.append(operation.model_copy(update=updates))

        graph = graph.model_copy(
            update={
                "surfaces": tuple(aligned_model(item) for item in graph.surfaces),
                "operations": tuple(operations),
                "relationships": tuple(
                    item.model_copy(
                        update={
                            "text": _align_near_copy_surface(question, item.text)
                        }
                    )
                    for item in graph.relationships
                ),
                "deliverables": tuple(
                    item.model_copy(
                        update={
                            "text": _align_near_copy_surface(question, item.text)
                        }
                    )
                    for item in graph.deliverables
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
            "unresolved_mentions": tuple(
                aligned_model(x) for x in turn.unresolved_mentions
            ),
            "analytical_request": request,
            "research_graph": graph,
            "user_repair": repair,
        }
    )


def _validate_transport_grounding(
    question: str,
    turn: TurnInterpreterTransport,
) -> None:
    haystack = _normalized_surface(question)
    bad = [
        span
        for span in _transport_surface_spans(turn)
        if not _normalized_surface(span)
        or _normalized_surface(span) not in haystack
    ]
    if bad:
        raise TurnInterpreterError(
            TurnInterpretationFailure(
                code="surface_grounding_violation",
                message=(
                    "TurnInterpreter kullanıcı mesajında bulunmayan source span üretti: "
                    + ", ".join(repr(x) for x in bad[:5])
                ),
            )
        )


def _dedupe_mentions(
    mentions: list[SemanticMention],
) -> tuple[SemanticMention, ...]:
    seen: set[tuple[str, str]] = set()
    out: list[SemanticMention] = []
    for mention in mentions:
        key = (_normalized_surface(mention.text), mention.kind.value)
        if key in seen:
            continue
        seen.add(key)
        out.append(mention)
    return tuple(out)


def _compile_research_graph(
    question: str,
    graph,
) -> ResearchRequestSurface | None:
    surface_index = {
        item.surface_id: SemanticMention(text=item.text, kind=item.kind)
        for item in graph.surfaces
    }

    def mentions(refs) -> tuple[SemanticMention, ...]:
        return tuple(surface_index[ref] for ref in refs)

    goals: list[ResearchGoalSurface] = []
    relationships: list[ResearchRelationshipSurface] = []
    excluded: list[SemanticMention] = []

    for operation in graph.operations:
        if isinstance(operation, ResearchRootCauseFrame):
            refs = (operation.outcome_ref, *operation.factor_refs)
        else:
            refs = (*operation.subject_refs, *operation.related_refs)

        if operation.polarity == ResearchOperationPolarity.EXCLUDED:
            excluded.extend(mentions(refs))
            continue

        if isinstance(operation, ResearchRootCauseFrame):
            goals.append(
                ResearchGoalSurface(
                    kind=ResearchNonRelationshipGoalKind.ROOT_CAUSE,
                    text=operation.text,
                    subject_mentions=(surface_index[operation.outcome_ref],),
                    related_mentions=mentions(operation.factor_refs),
                )
            )
            continue

        goals.append(
            ResearchGoalSurface(
                kind=ResearchNonRelationshipGoalKind(operation.kind),
                text=operation.text,
                subject_mentions=mentions(operation.subject_refs),
                related_mentions=mentions(operation.related_refs),
                ranking=getattr(operation, "ranking", None),
                comparisons=tuple(getattr(operation, "comparisons", ())),
            )
        )

    normalized_question = _normalized_surface(question)
    for relationship in graph.relationships:
        referenced = (
            *((relationship.focus_ref,) if relationship.focus_ref is not None else ()),
            *relationship.counterpart_refs,
        )
        if relationship.polarity == ResearchOperationPolarity.EXCLUDED:
            excluded.extend(mentions(referenced))
            continue

        focus_mentions: tuple[SemanticMention, ...] = ()
        if relationship.focus_binding != ResearchFocusBinding.UNRESOLVED:
            if relationship.focus_ref is None:
                raise ValueError("resolved relationship focus requires local focus_ref")
            focus = surface_index[relationship.focus_ref]
            focus_mentions = (focus,)
            focus_text = _normalized_surface(focus.text)
            relationship_text = _normalized_surface(relationship.text)

            if relationship.focus_binding == ResearchFocusBinding.EXPLICIT:
                if focus_text not in relationship_text:
                    raise ValueError(
                        "explicit relationship focus must occur inside relationship source span"
                    )
            elif relationship.focus_binding == ResearchFocusBinding.ANTECEDENT:
                focus_pos = normalized_question.find(focus_text)
                relation_pos = normalized_question.find(relationship_text)
                if focus_pos < 0 or relation_pos < 0 or focus_pos >= relation_pos:
                    raise ValueError(
                        "antecedent relationship focus must occur earlier in current message"
                    )

        relationships.append(
            ResearchRelationshipSurface(
                text=relationship.text,
                focus_mentions=focus_mentions,
                counterpart_mentions=mentions(relationship.counterpart_refs),
            )
        )

    deliverables = tuple(
        ResearchDeliverableSurface(kind=item.kind, text=item.text)
        for item in graph.deliverables
        if item.polarity == ResearchOperationPolarity.REQUESTED
    )

    if not goals and not relationships:
        return None

    return ResearchRequestSurface(
        goals=tuple(goals),
        relationships=tuple(relationships),
        time_mentions=mentions(graph.time_refs),
        deliverables=deliverables,
        excluded_mentions=_dedupe_mentions(excluded),
    )


def _compile_transport(
    question: str,
    transport: TurnInterpreterTransport,
) -> TurnInterpretation:
    research_request = None
    if transport.research_graph is not None:
        research_request = _compile_research_graph(question, transport.research_graph)

    dialogue_act = transport.dialogue_act
    if (
        transport.research_graph is not None
        and research_request is None
        and transport.analytical_request is None
    ):
        dialogue_act = TurnAct.UNSUPPORTED

    return TurnInterpretation(
        dialogue_act=dialogue_act,
        references=transport.references,
        analytical_request=transport.analytical_request,
        research_request=research_request,
        presentation_request=transport.presentation_request,
        user_repair=transport.user_repair,
        unresolved_mentions=transport.unresolved_mentions,
    )


class TurnInterpreter:
    """One native-schema call; at most one format-only retry; no semantic retry."""

    def interpret(
        self,
        *,
        question: str,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        llm,
    ) -> TurnInterpretation:
        structured = getattr(llm, "structured_json", None)
        if not callable(structured):
            raise TurnInterpreterError(
                TurnInterpretationFailure(
                    code="llm_unavailable",
                    message=(
                        "Configured provider native JSON-schema language interpretation "
                        "desteklemiyor."
                    ),
                )
            )

        system = _system_prompt()
        user = _user_prompt(question, semantic_context, conversation)
        schema = TurnInterpretation.model_json_schema()
        transport_kwargs = {
            "schema": schema,
            "schema_name": "dima_turn_interpretation_v2",
        }

        try:
            raw = structured(system, user, **transport_kwargs)
        except Exception as exc:
            raise TurnInterpreterError(
                TurnInterpretationFailure(
                    code="llm_unavailable",
                    message=f"TurnInterpreter native schema çağrısı başarısız: {exc}",
                )
            ) from exc

        try:
            turn = _parse(raw)
        except ValueError as first_error:
            repair_system = (
                system
                + "\n\nFORMAT_REPAIR_ONLY: Native schema çıktısı uygulama doğrulamasını "
                  "geçmedi. Aynı semantic kararı DEĞİŞTİRMEDEN yalnız şema-geçerli biçimde "
                  "yeniden yaz. Yeni yorum, canonical ID veya yeni mention ekleme."
            )
            repair_user = (
                user
                + "\n\nPREVIOUS_INVALID_OUTPUT:\n"
                + raw
                + "\n\nFORMAT_ERROR:\n"
                + str(first_error)[:1200]
            )
            try:
                repaired = structured(
                    repair_system,
                    repair_user,
                    **transport_kwargs,
                )
                turn = _parse(repaired)
            except Exception as exc:
                raise TurnInterpreterError(
                    TurnInterpretationFailure(
                        code="invalid_structured_output",
                        message=(
                            "TurnInterpreter native schema + bir format retry sonrasında "
                            f"geçersiz çıktı: {exc}"
                        ),
                    )
                ) from exc

        turn = _normalize_interpretation(question, turn)
        _validate_surface_grounding(question, turn)

        # Final STANDARD/RESEARCH routing is deterministic and presentation-agnostic.
        # This happens only after every provider surface has passed source grounding,
        # so projection cannot hide hallucinated research/deliverable text.
        turn = ResearchModePolicy().decide(turn).canonical_turn
        return turn
