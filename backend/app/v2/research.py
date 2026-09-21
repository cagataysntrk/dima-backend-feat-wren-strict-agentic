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

from app.v2.models import (
    BoundedSemanticContextV0,
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ResearchUnresolvedRef,
    ResolutionStatus,
    SemanticHypothesis,
    SemanticMention,
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
        if turn.dialogue_act not in {
            TurnAct.COMPLEX_ANALYSIS,
            TurnAct.REPORT_REQUEST,
        }:
            raise ValueError("ResearchBriefBuilder requires a research dialogue act")
        if turn.research_request is None:
            raise ValueError("research_request is required")

        request = turn.research_request
        hypothesis_index = _hypothesis_index(hypotheses)

        questions: list[ResearchQuestion] = []
        all_refs: list[ResearchSemanticRef] = []
        deliverables: list[PresentationKind] = []
        blocked_ids: list[str] = []

        for position, goal in enumerate(request.goals, start=1):
            goal_id = f"g{position}"
            subject_refs: list[ResearchSemanticRef] = []
            related_refs: list[ResearchSemanticRef] = []
            unresolved: list[ResearchUnresolvedRef] = []

            if goal.kind == ResearchGoalKind.DELIVERABLE:
                if goal.deliverable is not None and goal.deliverable not in deliverables:
                    deliverables.append(goal.deliverable)
            else:
                for mention in goal.subject_mentions:
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

                for mention in goal.related_mentions:
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

                if not goal.subject_mentions and not goal.related_mentions:
                    unresolved.append(
                        ResearchUnresolvedRef(
                            source_mention=goal.text,
                            role="goal",
                            reason="research goal has no explicit semantic anchor",
                        )
                    )

                if goal.kind == ResearchGoalKind.RELATIONSHIP:
                    if not goal.subject_mentions:
                        unresolved.append(
                            ResearchUnresolvedRef(
                                source_mention=goal.text,
                                role="subject",
                                reason="relationship goal has no explicit subject",
                            )
                        )
                    if not goal.related_mentions:
                        unresolved.append(
                            ResearchUnresolvedRef(
                                source_mention=goal.text,
                                role="related",
                                reason="relationship goal has no explicit related side",
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
                                source_mention=goal.text,
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
                    kind=goal.kind,
                    source_text=goal.text,
                    subject_refs=_unique_refs(subject_refs),
                    related_refs=_unique_refs(related_refs),
                    unresolved=tuple(unresolved),
                    status=status,
                )
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

        objective = " | ".join(question.source_text for question in questions)
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
            "deliverables": [item.value for item in deliverables],
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
            deliverables=tuple(deliverables),
            must_requirement_ids=tuple(question.goal_id for question in questions),
            blocking_goal_ids=tuple(blocked_ids),
            context_version=context_version,
            status=(
                ResearchBriefStatus.BLOCKED
                if blocked_ids
                else ResearchBriefStatus.READY_FOR_RESEARCH
            ),
        )
