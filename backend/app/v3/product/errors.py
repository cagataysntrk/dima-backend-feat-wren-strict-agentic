"""Stable product-facing error normalization."""
from __future__ import annotations

from .contracts import ProductErrorCode


class ProductError(RuntimeError):
    def __init__(self, code: ProductErrorCode, detail: str) -> None:
        super().__init__(f"{code.value}: {detail}")
        self.code = code
        self.detail = detail


def normalize_owner_error(exc: Exception) -> ProductError:
    raw_code = str(getattr(exc, "code", exc.__class__.__name__)).upper()
    detail = str(getattr(exc, "detail", "artifact unavailable"))

    # Non-oracle owner errors are deliberately collapsed.
    if any(token in raw_code for token in ("NOT_FOUND", "TENANT_MISMATCH", "SCOPE_MISMATCH", "UNAVAILABLE", "UNKNOWN")):
        return ProductError(ProductErrorCode.UNAVAILABLE, "artifact unavailable in caller scope")
    if "FORBIDDEN" in raw_code or "UNAUTHORIZED" in raw_code:
        return ProductError(ProductErrorCode.FORBIDDEN, "operation is not authorized")
    if "SUPERSEDED" in raw_code:
        return ProductError(ProductErrorCode.SUPERSEDED, detail)
    if "STALE" in raw_code or "CONTEXT_MISMATCH" in raw_code:
        return ProductError(ProductErrorCode.STALE, detail)
    if "TRANSITION" in raw_code:
        return ProductError(ProductErrorCode.INVALID_TRANSITION, detail)
    if "EVIDENCE" in raw_code and any(token in raw_code for token in ("MISSING", "REQUIRED", "INSUFFICIENT")):
        return ProductError(ProductErrorCode.INSUFFICIENT_EVIDENCE, detail)
    if "INCONCLUSIVE" in raw_code or "NO_DEFENSIBLE" in raw_code:
        return ProductError(ProductErrorCode.INCONCLUSIVE, detail)
    if "DEFERRED" in raw_code or "CAPABILITY" in raw_code:
        return ProductError(ProductErrorCode.DEFERRED_CAPABILITY, detail)
    return ProductError(ProductErrorCode.UNAVAILABLE, "artifact unavailable in caller scope")
