"""Typed Metabase transport errors.

Infrastructure/provider failures are never promoted into semantic failures here.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class MetabaseErrorCode(StrEnum):
    TRANSPORT = "METABASE_TRANSPORT"
    AUTH = "METABASE_AUTH"
    PERMISSION = "METABASE_PERMISSION"
    QUERY_INVALID = "METABASE_QUERY_INVALID"
    RESOURCE_NOT_FOUND = "METABASE_RESOURCE_NOT_FOUND"
    TIMEOUT = "METABASE_TIMEOUT"
    INTERNAL = "METABASE_INTERNAL"


class MetabaseClientError(RuntimeError):
    def __init__(
        self,
        *,
        code: MetabaseErrorCode,
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
    ) -> "MetabaseClientError":
        if status_code == 401:
            code = MetabaseErrorCode.AUTH
        elif status_code == 403:
            code = MetabaseErrorCode.PERMISSION
        elif status_code in (400, 409, 422):
            code = MetabaseErrorCode.QUERY_INVALID
        elif status_code == 404:
            code = MetabaseErrorCode.RESOURCE_NOT_FOUND
        else:
            code = MetabaseErrorCode.INTERNAL
        return cls(
            code=code,
            operation=operation,
            message=f"HTTP {status_code}",
            status_code=status_code,
            body=body,
        )
