"""Domain failures for Fast Ask."""

from __future__ import annotations

from enum import StrEnum


class FastAskErrorCode(StrEnum):
    COGNITION_UNAVAILABLE = "COGNITION_UNAVAILABLE"
    COGNITION_INVALID = "COGNITION_INVALID"
    UNSUPPORTED = "UNSUPPORTED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    NO_RESOURCE = "NO_RESOURCE"
    AMBIGUOUS_RESOURCE = "AMBIGUOUS_RESOURCE"
    UNKNOWN_HANDLE = "UNKNOWN_HANDLE"
    NO_MEASURE_FIELD = "NO_MEASURE_FIELD"
    NO_TEMPORAL_FIELD = "NO_TEMPORAL_FIELD"
    NO_BREAKDOWN_FIELD = "NO_BREAKDOWN_FIELD"
    TEMPORAL_ANCHOR_REQUIRED = "TEMPORAL_ANCHOR_REQUIRED"
    TEMPORAL_INVALID = "TEMPORAL_INVALID"
    RESULT_CONTRACT_INVALID = "RESULT_CONTRACT_INVALID"


class FastAskError(RuntimeError):
    def __init__(self, code: FastAskErrorCode, message: str) -> None:
        super().__init__(f"{code.value}: {message}")
        self.code = code
        self.message = message
