"""Typed failures for the Fast Track Metabase boundary.

Transport/provider failures remain infrastructure failures. They are never silently
relabelled as semantic "no match" outcomes.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class FastMetabaseErrorCode(StrEnum):
    METABASE_UNAVAILABLE = "METABASE_UNAVAILABLE"
    AGENT_API_DISABLED = "AGENT_API_DISABLED"
    AUTH_FAILED = "AUTH_FAILED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    QUERY_CONSTRUCT_FAILED = "QUERY_CONSTRUCT_FAILED"
    QUERY_EXECUTION_FAILED = "QUERY_EXECUTION_FAILED"
    DB_TIMEOUT = "DB_TIMEOUT"
    ROW_BUDGET_EXCEEDED = "ROW_BUDGET_EXCEEDED"
    PAGINATION_INVALID = "PAGINATION_INVALID"
    RATE_LIMITED = "RATE_LIMITED"
    UPSTREAM_CONTRACT_CHANGED = "UPSTREAM_CONTRACT_CHANGED"


class FastMetabaseError(RuntimeError):
    def __init__(
        self,
        *,
        code: FastMetabaseErrorCode,
        operation: str,
        message: str,
        status_code: int | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(f"{code.value} [{operation}]: {message}")
        self.code = code
        self.operation = operation
        self.status_code = status_code
        self.body = body

    @classmethod
    def from_http(
        cls,
        *,
        operation: str,
        status_code: int,
        body: Any,
    ) -> "FastMetabaseError":
        body_text = str(body or "").lower()

        if status_code == 401:
            code = FastMetabaseErrorCode.AUTH_FAILED
        elif status_code == 403 and "agent api" in body_text and (
            "not enabled" in body_text or "disabled" in body_text
        ):
            code = FastMetabaseErrorCode.AGENT_API_DISABLED
        elif status_code == 403:
            code = FastMetabaseErrorCode.PERMISSION_DENIED
        elif status_code == 404:
            code = FastMetabaseErrorCode.RESOURCE_NOT_FOUND
        elif status_code == 429:
            code = FastMetabaseErrorCode.RATE_LIMITED
        elif status_code >= 500:
            code = FastMetabaseErrorCode.METABASE_UNAVAILABLE
        elif operation == "construct_query":
            code = FastMetabaseErrorCode.QUERY_CONSTRUCT_FAILED
        elif operation in {"execute", "combined_query", "continue_query"}:
            code = FastMetabaseErrorCode.QUERY_EXECUTION_FAILED
        else:
            code = FastMetabaseErrorCode.UPSTREAM_CONTRACT_CHANGED

        return cls(
            code=code,
            operation=operation,
            message=f"HTTP {status_code}",
            status_code=status_code,
            body=body,
        )
