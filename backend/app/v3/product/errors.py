"""Stable product-facing error normalization."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import ProductErrorCode


@dataclass(frozen=True)
class ProductOwnerDiagnostic:
    """Internal-only owner telemetry; never part of the public error message."""

    owner: str
    owner_error_code: str
    artifact_kind: str | None = None
    artifact_id: str | None = None
    requested_lineage: str | None = None
    artifact_lineage: str | None = None
    requested_scope_version: str | None = None
    artifact_scope_version: str | None = None
    currentness: str | None = None


class ProductError(RuntimeError):
    def __init__(
        self,
        code: ProductErrorCode,
        detail: str,
        *,
        diagnostic: ProductOwnerDiagnostic | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {detail}")
        self.code = code
        self.detail = detail
        self.diagnostic = diagnostic


def normalize_owner_error(
    exc: Exception,
    *,
    owner: str = "UNKNOWN_OWNER",
    diagnostic: ProductOwnerDiagnostic | None = None,
) -> ProductError:
    raw_code = str(getattr(exc, "code", exc.__class__.__name__)).upper()
    detail = str(getattr(exc, "detail", "artifact unavailable"))
    base = diagnostic or ProductOwnerDiagnostic(
        owner=owner,
        owner_error_code=raw_code,
    )
    if base.owner_error_code != raw_code:
        base = replace(base, owner_error_code=raw_code)

    # Non-oracle owner errors are deliberately collapsed.
    if any(token in raw_code for token in ("NOT_FOUND", "TENANT_MISMATCH", "SCOPE_MISMATCH", "UNAVAILABLE", "UNKNOWN")):
        return ProductError(
            ProductErrorCode.UNAVAILABLE,
            "artifact unavailable in caller scope",
            diagnostic=base,
        )
    if "FORBIDDEN" in raw_code or "UNAUTHORIZED" in raw_code:
        return ProductError(
            ProductErrorCode.FORBIDDEN,
            "operation is not authorized",
            diagnostic=base,
        )
    if "SUPERSEDED" in raw_code:
        return ProductError(ProductErrorCode.SUPERSEDED, detail, diagnostic=base)
    if "STALE" in raw_code or "CONTEXT_MISMATCH" in raw_code:
        return ProductError(ProductErrorCode.STALE, detail, diagnostic=base)
    if "TRANSITION" in raw_code:
        return ProductError(
            ProductErrorCode.INVALID_TRANSITION,
            detail,
            diagnostic=base,
        )
    if "EVIDENCE" in raw_code and any(token in raw_code for token in ("MISSING", "REQUIRED", "INSUFFICIENT")):
        return ProductError(
            ProductErrorCode.INSUFFICIENT_EVIDENCE,
            detail,
            diagnostic=base,
        )
    if "INCONCLUSIVE" in raw_code or "NO_DEFENSIBLE" in raw_code:
        return ProductError(ProductErrorCode.INCONCLUSIVE, detail, diagnostic=base)
    if "DEFERRED" in raw_code or "CAPABILITY" in raw_code:
        return ProductError(
            ProductErrorCode.DEFERRED_CAPABILITY,
            detail,
            diagnostic=base,
        )
    return ProductError(
            ProductErrorCode.UNAVAILABLE,
            "artifact unavailable in caller scope",
            diagnostic=base,
        )
