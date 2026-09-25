"""P9 ResearchBrief builder — typed research intent, no execution.

Day 6 answers only "what must be researched?". It consumes the language owner's
ResearchRequestSurface plus SemanticResolver hypotheses. It never receives/re-reads the
raw user question, never plans SQL/tools, and never executes Wren.

Day 7+ owns task planning, ResearchToolContract validation, cross-domain join gates,
EvidenceArtifact lifecycle, adaptive branching, and report generation.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata

from app.v2.capabilities import AnalyticsCapabilityLane, AnalyticsCapabilityRegistry
from app.v2.models import (
    AnalyticalRequest,
    BoundedSemanticContextV0,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchMode,
    ResearchModeDecision,
    ResearchModeReason,
    ResearchNonRelationshipGoalKind,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchUnresolvedRef,
    ResolutionStatus,
    SemanticHypothesis,
    SemanticMention,
    SemanticMentionKind,
    SemanticTargetKind,
    TurnAct,
    TurnInterpretation,
)


def _norm_surface(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.casefold().replace("\u0307", "").split())


def _hypothesis_index(
    hypotheses: tuple[SemanticHypothesis, ...],
) -> dict[tuple[str, str], tuple[SemanticHypothesis, ...]]:
    out: dict[tuple[str, str], list[SemanticHypothesis]] = {}
    for hypothesis in hypotheses:
        key = (_norm_surface(hypothesis.source_mention), hypothesis.mention_kind.value)
        out.setdefault(key, []).append(hypothesis)
    return {key: tuple(values) for key, values in out.items()}


def _resolved_ref(
    mention: SemanticMention,
    index: dict[tuple[str, str], tuple[SemanticHypothesis, ...]],
) -> tuple[ResearchSemanticRef | None, str | None]:
    key = (_norm_surface(mention.text), mention.kind.value)
    matching = index.get(key, ())
    if not matching:
        return None, "resolver hypothesis missing"

    resolved = [
        hypothesis
        for hypothesis in matching
        if hypothesis.status == ResolutionStatus.RESOLVED
        and hypothesis.resolved_candidate_id is not None
    ]
    if len(resolved) != 1:
        return None, "semantic mention is not uniquely resolved"

    hypothesis = resolved[0]
    candidate = next(
        (
            item
            for item in hypothesis.candidates
            if item.candidate_id == hypothesis.resolved_candidate_id
        ),
        None,
    )
    if candidate is None:
        return None, "resolved candidate is absent from resolver provenance"

    return (
        ResearchSemanticRef(
            source_mention=mention.text,
            candidate_id=candidate.candidate_id,
            target_kind=candidate.target_kind,
            canonical_name=candidate.canonical_name,
            dimension_name=candidate.dimension_name,
            value=None if candidate.sensitive else candidate.value,
            cube_names=candidate.cube_names,
            sensitive=candidate.sensitive,
        ),
        None,
    )


def _unique_refs(refs: list[ResearchSemanticRef]) -> tuple[ResearchSemanticRef, ...]:
    seen: set[str] = set()
    out: list[ResearchSemanticRef] = []
    for ref in refs:
        if ref.candidate_id in seen:
            continue
        seen.add(ref.candidate_id)
        out.append(ref)
    return tuple(out)


def _relationship_path_exists(
    *,
    subject_refs: list[ResearchSemanticRef],
    related_refs: list[ResearchSemanticRef],
    semantic_context: BoundedSemanticContextV0,
) -> bool:
    """Check semantic relationship availability only; never design/validate a join.

    Sharing a cube is sufficient availability evidence. Otherwise we use the compact
    cube-level relationship graph already certified by ContextProvider. Cardinality,
    grain, time alignment and executable join safety remain Day 7 responsibilities.
    """

    subject_cubes = {
        cube
        for ref in subject_refs
        for cube in ref.cube_names
        if cube
    }
    related_cubes = {
        cube
        for ref in related_refs
        for cube in ref.cube_names
        if cube
    }
    if not subject_cubes or not related_cubes:
        return False
    if subject_cubes.intersection(related_cubes):
        return True

    graph: dict[str, set[str]] = {}
    for relationship in semantic_context.relationships:
        names = tuple(dict.fromkeys(relationship.cube_names))
        for left in names:
            graph.setdefault(left, set())
            for right in names:
                if left != right:
                    graph[left].add(right)

    frontier = list(subject_cubes)
    seen = set(subject_cubes)
    while frontier:
        current = frontier.pop()
        for neighbor in graph.get(current, ()):
            if neighbor in related_cubes:
                return True
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    return False


def _dedupe_mentions(mentions: list[SemanticMention]) -> tuple[SemanticMention, ...]:
    seen: set[tuple[str, str]] = set()
    out: list[SemanticMention] = []
    for mention in mentions:
        key = (_norm_surface(mention.text), mention.kind.value)
        if key in seen:
            continue
        seen.add(key)
        out.append(mention)
    return tuple(out)


class ResearchModePolicy:
    """Own STANDARD vs RESEARCH routing from typed capability shape only.

    Presentation/deliverables and raw operation text are deliberately ignored. Every
    declared operation is capability-validated before any route is admitted; therefore
    an unclassified operation can never hide behind a valid relationship/research goal.
    """

    def __init__(self, registry: AnalyticsCapabilityRegistry | None = None):
        self._registry = registry or AnalyticsCapabilityRegistry()

    def decide(self, turn: TurnInterpretation) -> ResearchModeDecision:
        request = turn.research_request
        if request is None:
            return ResearchModeDecision(
                mode=ResearchMode.STANDARD,
                reason=ResearchModeReason.EXISTING_STANDARD_SURFACE,
                canonical_turn=turn,
            )

        kinds = tuple(goal.kind for goal in request.goals)
        assessment = self._registry.assess(kinds)

        # Validate the full declared operation set before routing. This is deliberately
        # before the relationship fast decision so OTHER/unknown semantics cannot be
        # masked by an otherwise valid relationship edge.
        if assessment.has_blocked:
            return self._blocked(
                turn,
                reason=ResearchModeReason.UNCLASSIFIED_OPERATION,
                detail="unclassified analytical operation; routing refused",
            )

        # Relationship is a declared Research capability. Cardinality/join execution
        # remains Day 7 territory; presentation never participates in this decision.
        if request.relationships:
            return ResearchModeDecision(
                mode=ResearchMode.RESEARCH,
                reason=ResearchModeReason.COMPLEX_ONLY_OPERATION,
                canonical_turn=turn.model_copy(
                    update={"dialogue_act": TurnAct.COMPLEX_ANALYSIS}
                ),
            )

        if assessment.has_research:
            return ResearchModeDecision(
                mode=ResearchMode.RESEARCH,
                reason=ResearchModeReason.COMPLEX_ONLY_OPERATION,
                canonical_turn=turn.model_copy(
                    update={"dialogue_act": TurnAct.COMPLEX_ANALYSIS}
                ),
            )

        projected = self._project_standard(request)
        if projected is not None:
            return ResearchModeDecision(
                mode=ResearchMode.STANDARD,
                reason=ResearchModeReason.STANDARD_PROJECTABLE_OPERATIONS,
                canonical_turn=turn.model_copy(
                    update={
                        "dialogue_act": TurnAct.ANALYTIC_NEW,
                        "analytical_request": projected,
                        "research_request": None,
                    }
                ),
            )

        # Several individually Core-capable operations may still require coordinated
        # research if they cannot be represented as one lossless AnalyticalRequest.
        if len(request.goals) > 1:
            return ResearchModeDecision(
                mode=ResearchMode.RESEARCH,
                reason=ResearchModeReason.MULTI_INDEPENDENT_GOALS,
                canonical_turn=turn.model_copy(
                    update={"dialogue_act": TurnAct.COMPLEX_ANALYSIS}
                ),
            )

        return self._blocked(
            turn,
            reason=ResearchModeReason.INCOMPLETE_STANDARD_OPERATION,
            detail="standard-capable operation lacks typed slots required for Core projection",
        )

    def _blocked(
        self,
        turn: TurnInterpretation,
        *,
        reason: ResearchModeReason,
        detail: str,
    ) -> ResearchModeDecision:
        canonical = turn.model_copy(
            update={
                "dialogue_act": TurnAct.UNSUPPORTED,
                "analytical_request": None,
                "research_request": None,
            }
        )
        return ResearchModeDecision(
            mode=ResearchMode.BLOCKED,
            reason=reason,
            canonical_turn=canonical,
        )

    def _project_standard(self, request) -> AnalyticalRequest | None:
        """Project exactly the typed slots already owned by Core AnalyticsIR."""

        if request.relationships or not request.goals:
            return None
        if any(
            self._registry.lane_for(goal.kind)
            != AnalyticsCapabilityLane.CORE_STANDARD
            for goal in request.goals
        ):
            return None

        if sum(
            goal.kind == ResearchNonRelationshipGoalKind.PERFORMANCE
            for goal in request.goals
        ) > 1:
            return None

        ranking_goals = [
            goal
            for goal in request.goals
            if goal.kind == ResearchNonRelationshipGoalKind.RANKING
        ]
        comparison_goals = [
            goal
            for goal in request.goals
            if goal.kind == ResearchNonRelationshipGoalKind.COMPARISON
        ]
        if len(ranking_goals) > 1 or len(comparison_goals) > 1:
            return None

        metrics: list[SemanticMention] = []
        dimensions: list[SemanticMention] = []
        filters: list[SemanticMention] = []

        for goal in request.goals:
            mentions = (*goal.subject_mentions, *goal.related_mentions)
            metrics.extend(
                mention for mention in mentions
                if mention.kind == SemanticMentionKind.METRIC
            )
            dimensions.extend(
                mention for mention in mentions
                if mention.kind == SemanticMentionKind.DIMENSION
            )
            filters.extend(
                mention for mention in mentions
                if mention.kind == SemanticMentionKind.FILTER
            )

        metric_mentions = _dedupe_mentions(metrics)
        dimension_mentions = _dedupe_mentions(dimensions)
        filter_mentions = _dedupe_mentions(filters)
        if not metric_mentions:
            return None

        ranking = ranking_goals[0].ranking if ranking_goals else None
        if ranking_goals and ranking is None:
            return None

        comparisons = comparison_goals[0].comparisons if comparison_goals else ()
        if comparison_goals and not comparisons:
            return None

        return AnalyticalRequest(
            metric_mentions=metric_mentions,
            dimension_mentions=dimension_mentions,
            filter_mentions=filter_mentions,
            time_mentions=request.time_mentions,
            ranking=ranking,
            comparisons=comparisons,
        )

class ResearchBriefBuilder:
    """Single Day 6 owner for the canonical typed research work order.

    Important: there is intentionally no `question` / `raw_prompt` argument.
    """

    def build(
        self,
        *,
        turn: TurnInterpretation,
        hypotheses: tuple[SemanticHypothesis, ...],
        semantic_context: BoundedSemanticContextV0,
        context_version: str,
    ) -> ResearchBrief:
        if turn.dialogue_act != TurnAct.COMPLEX_ANALYSIS:
            raise ValueError(
                "ResearchBriefBuilder requires canonical COMPLEX_ANALYSIS from ResearchModePolicy"
            )
        if turn.research_request is None:
            raise ValueError("research_request is required")

        request = turn.research_request
        hypothesis_index = _hypothesis_index(hypotheses)

        questions: list[ResearchQuestion] = []
        all_refs: list[ResearchSemanticRef] = []
        blocked_ids: list[str] = []

        next_goal_number = 1

        def append_question(
            *,
            kind: ResearchGoalKind,
            source_text: str,
            subject_mentions: tuple[SemanticMention, ...],
            related_mentions: tuple[SemanticMention, ...],
            ranking=None,
            comparisons=(),
            require_relationship_sides: bool = False,
        ) -> None:
            nonlocal next_goal_number
            goal_id = f"g{next_goal_number}"
            next_goal_number += 1

            subject_refs: list[ResearchSemanticRef] = []
            related_refs: list[ResearchSemanticRef] = []
            unresolved: list[ResearchUnresolvedRef] = []

            for mention in subject_mentions:
                ref, reason = _resolved_ref(mention, hypothesis_index)
                if ref is None:
                    unresolved.append(
                        ResearchUnresolvedRef(
                            source_mention=mention.text,
                            role="subject",
                            reason=reason or "semantic subject unresolved",
                        )
                    )
                else:
                    subject_refs.append(ref)
                    all_refs.append(ref)

            for mention in related_mentions:
                ref, reason = _resolved_ref(mention, hypothesis_index)
                if ref is None:
                    unresolved.append(
                        ResearchUnresolvedRef(
                            source_mention=mention.text,
                            role="related",
                            reason=reason or "semantic related ref unresolved",
                        )
                    )
                else:
                    related_refs.append(ref)
                    all_refs.append(ref)

            if not subject_mentions and not related_mentions:
                unresolved.append(
                    ResearchUnresolvedRef(
                        source_mention=source_text,
                        role="goal",
                        reason="research goal has no explicit semantic anchor",
                    )
                )

            if require_relationship_sides:
                if not subject_mentions:
                    unresolved.append(
                        ResearchUnresolvedRef(
                            source_mention=source_text,
                            role="subject",
                            reason="relationship goal has no explicit focus side",
                        )
                    )
                if not related_mentions:
                    unresolved.append(
                        ResearchUnresolvedRef(
                            source_mention=source_text,
                            role="related",
                            reason="relationship goal has no explicit counterpart side",
                        )
                    )
                if (
                    subject_refs
                    and related_refs
                    and not _relationship_path_exists(
                        subject_refs=subject_refs,
                        related_refs=related_refs,
                        semantic_context=semantic_context,
                    )
                ):
                    unresolved.append(
                        ResearchUnresolvedRef(
                            source_mention=source_text,
                            role="goal",
                            reason=(
                                "no verified semantic relationship path between "
                                "resolved research domains"
                            ),
                        )
                    )

            status = (
                ResearchGoalStatus.BLOCKED
                if unresolved
                else ResearchGoalStatus.RESOLVED
            )
            if status == ResearchGoalStatus.BLOCKED:
                blocked_ids.append(goal_id)

            questions.append(
                ResearchQuestion(
                    goal_id=goal_id,
                    kind=kind,
                    source_text=source_text,
                    subject_refs=_unique_refs(subject_refs),
                    related_refs=_unique_refs(related_refs),
                    ranking=ranking,
                    comparisons=tuple(comparisons),
                    unresolved=tuple(unresolved),
                    status=status,
                )
            )

        for goal in request.goals:
            append_question(
                kind=ResearchGoalKind(goal.kind.value),
                source_text=goal.text,
                subject_mentions=goal.subject_mentions,
                related_mentions=goal.related_mentions,
                ranking=goal.ranking,
                comparisons=goal.comparisons,
            )

        for relationship in request.relationships:
            # One typed relationship request may name several counterparts, but each
            # resulting ResearchQuestion is an atomic edge by construction.
            for counterpart in relationship.counterpart_mentions:
                append_question(
                    kind=ResearchGoalKind.RELATIONSHIP,
                    source_text=relationship.text,
                    subject_mentions=relationship.focus_mentions,
                    related_mentions=(counterpart,),
                    require_relationship_sides=True,
                )

        scope_refs = _unique_refs(all_refs)
        required_domain_candidates: list[str] = []
        for ref in scope_refs:
            if ref.target_kind == SemanticTargetKind.CUBE:
                required_domain_candidates.append(ref.canonical_name)
            elif len(ref.cube_names) == 1:
                # Resolver provenance, not ResearchBrief inference. Ambiguous multi-cube
                # ownership is intentionally not collapsed into a domain choice here.
                required_domain_candidates.append(ref.cube_names[0])
        required_domains = tuple(dict.fromkeys(required_domain_candidates))
        time_surfaces = tuple(
            dict.fromkeys(mention.text for mention in request.time_mentions)
        )
        deliverables = tuple(
            ResearchDeliverableRequirement(
                requirement_id=f"d{position}",
                kind=item.kind,
                source_text=item.text,
            )
            for position, item in enumerate(request.deliverables, start=1)
        )

        objective_parts = [question.source_text for question in questions]
        objective_parts.extend(item.source_text for item in deliverables)
        objective = " | ".join(objective_parts)
        digest_payload = {
            "context_version": context_version,
            "goals": [
                {
                    "id": question.goal_id,
                    "kind": question.kind.value,
                    "source_text": question.source_text,
                    "status": question.status.value,
                    "subject_ids": [ref.candidate_id for ref in question.subject_refs],
                    "related_ids": [ref.candidate_id for ref in question.related_refs],
                    "ranking": (
                        question.ranking.model_dump(mode="json")
                        if question.ranking is not None
                        else None
                    ),
                    "comparisons": [
                        item.model_dump(mode="json")
                        for item in question.comparisons
                    ],
                    "unresolved": [
                        {
                            "surface": item.source_mention,
                            "role": item.role,
                            "reason": item.reason,
                        }
                        for item in question.unresolved
                    ],
                }
                for question in questions
            ],
            "time_surfaces": time_surfaces,
            "deliverables": [
                {
                    "id": item.requirement_id,
                    "kind": item.kind.value,
                    "source_text": item.source_text,
                }
                for item in deliverables
            ],
        }
        brief_id = "rb-" + hashlib.sha256(
            json.dumps(
                digest_payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:20]

        return ResearchBrief(
            brief_id=brief_id,
            objective=objective,
            scope=ResearchScope(
                semantic_refs=scope_refs,
                time_surfaces=time_surfaces,
            ),
            required_domains=required_domains,
            questions=tuple(questions),
            deliverables=deliverables,
            must_requirement_ids=(
                tuple(question.goal_id for question in questions)
                + tuple(item.requirement_id for item in deliverables)
            ),
            blocking_goal_ids=tuple(blocked_ids),
            context_version=context_version,
            status=(
                ResearchBriefStatus.BLOCKED
                if blocked_ids
                else ResearchBriefStatus.READY_FOR_RESEARCH
            ),
        )
