"""Native Jev bounded semantic-decision provider for the Day 6.5 J1B experiment.

This module is cognition-only. It sees LLM-safe CandidateSet cards and returns SELECT/ABSTAIN.
It cannot mint semantic handles, see canonical targets, write SQL, or fall back to another model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from app.v2.semantic_linker import (
    SemanticCandidateDecisionProvider,
    SemanticDecisionProviderError,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
    SemanticLinkRequestCard,
)


@dataclass(frozen=True)
class JevDecisionTelemetry:
    request_id: str
    confidence: float | None
    probabilities: dict[str, float]


class JevDecisionProvider(SemanticCandidateDecisionProvider):
    MODEL = "typesafe/jev-1.13"
    ENDPOINT = "https://openrouter.ai/api/alpha/decisions"

    def __init__(
        self,
        *,
        api_key: str,
        model: str = MODEL,
        endpoint: str = ENDPOINT,
        timeout_s: float = 30.0,
    ) -> None:
        if not str(api_key or "").strip():
            raise ValueError("JevDecisionProvider requires an OpenRouter API key")
        self._api_key = str(api_key).strip()
        self._model = str(model)
        self._endpoint = str(endpoint)
        self._timeout_s = float(timeout_s)
        self._telemetry: list[JevDecisionTelemetry] = []

    @property
    def telemetry(self) -> tuple[JevDecisionTelemetry, ...]:
        return tuple(self._telemetry)

    @staticmethod
    def _criteria(request: SemanticLinkRequestCard) -> dict[str, str]:
        out: dict[str, str] = {}
        for card in request.candidates:
            aliases = ", ".join(card.verified_aliases) or "(none)"
            cubes = ", ".join(card.cube_labels) or "(none)"
            out[card.candidate_id] = (
                f'target_kind={card.target_kind}; label="{card.label}"; '
                f"verified_aliases=[{aliases}]; cube_labels=[{cubes}]"
            )
        out["ABSTAIN"] = (
            "No supplied candidate is clearly the intended business concept, multiple "
            "candidates remain plausible, or the surface is under-specified."
        )
        return out

    def _decide_one(
        self,
        *,
        client: httpx.Client,
        request: SemanticLinkRequestCard,
    ) -> SemanticLinkChoice:
        criteria = self._criteria(request)
        safe_record = {
            "request_id": request.request_id,
            "user_surface": request.surface,
            "kind_hint": request.kind_hint,
            "candidate_cards": [
                card.model_dump(mode="json") for card in request.candidates
            ],
        }
        payload = {
            "model": self._model,
            "state": {
                "description": (
                    "One Dima bounded semantic decision. Only supplied opaque candidate "
                    "cards are visible; no canonical target or database authority is present."
                ),
                "records": [
                    {
                        "id": request.request_id,
                        "record": json.dumps(
                            safe_record,
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    }
                ],
            },
            "questions": {
                "decision": {
                    "type": "choice",
                    "instructions": (
                        f'For record "{request.request_id}", select exactly one supplied '
                        "candidate_id only when it is clearly intended; otherwise ABSTAIN."
                    ),
                    "criteria": criteria,
                },
                "abstain_reason": {
                    "type": "choice",
                    "instructions": (
                        "Classify why ABSTAIN would be required. This field is diagnostic "
                        "unless decision=ABSTAIN."
                    ),
                    "criteria": {
                        "AMBIGUOUS": "Multiple supplied candidates remain plausibly intended.",
                        "NO_MATCH": "No supplied candidate matches the requested business concept.",
                        "INSUFFICIENT_CONTEXT": "The surface is under-specified for safe selection.",
                    },
                },
            },
        }
        try:
            response = client.post(
                self._endpoint,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        except Exception as exc:
            raise SemanticDecisionProviderError(
                f"Jev transport failed: {type(exc).__name__}: {exc}"
            ) from exc
        if response.status_code != 200:
            raise SemanticDecisionProviderError(
                f"Jev provider HTTP {response.status_code}: {response.text[:400]}"
            )

        try:
            raw = response.json()
            answer = (raw.get("answers") or {}).get("decision") or {}
            choice = str(answer["choice"])
        except Exception as exc:
            raise SemanticDecisionProviderError(
                f"Jev response contract invalid: {type(exc).__name__}: {exc}"
            ) from exc

        if choice not in criteria:
            raise SemanticDecisionProviderError(
                "Jev selected a choice outside the exact supplied candidate set"
            )

        probabilities = {
            str(key): float(value)
            for key, value in (answer.get("probabilities") or {}).items()
            if isinstance(value, (int, float))
        }
        confidence = answer.get("confidence")
        self._telemetry.append(
            JevDecisionTelemetry(
                request_id=request.request_id,
                confidence=(
                    float(confidence)
                    if isinstance(confidence, (int, float))
                    else None
                ),
                probabilities=probabilities,
            )
        )

        if choice != "ABSTAIN":
            return SemanticLinkChoice(
                request_id=request.request_id,
                decision="SELECT",
                candidate_id=choice,
            )

        reason_answer = (raw.get("answers") or {}).get("abstain_reason") or {}
        reason = str(reason_answer.get("choice") or "")
        if reason not in {"AMBIGUOUS", "NO_MATCH", "INSUFFICIENT_CONTEXT"}:
            raise SemanticDecisionProviderError(
                "Jev ABSTAIN response lacks a valid typed abstain reason"
            )
        return SemanticLinkChoice(
            request_id=request.request_id,
            decision="ABSTAIN",
            reason=reason,
        )

    def decide(
        self,
        requests: tuple[SemanticLinkRequestCard, ...],
    ) -> SemanticLinkBatchDecision:
        if not requests:
            raise ValueError("Jev semantic decision requires at least one request")
        self._telemetry = []
        with httpx.Client(timeout=self._timeout_s) as client:
            choices = tuple(
                self._decide_one(client=client, request=request)
                for request in requests
            )
        return SemanticLinkBatchDecision(choices=choices)
