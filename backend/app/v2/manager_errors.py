"""Typed Manager tool error taxonomy."""

from __future__ import annotations


class ManagerToolExecutionError(RuntimeError):
    fatal: bool = False
    code: str = "tool_error"

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        if code is not None:
            self.code = code


class ManagerRecoverableToolError(ManagerToolExecutionError):
    fatal = False


class ManagerFatalToolError(ManagerToolExecutionError):
    fatal = True


class ManagerAuthorityViolation(ManagerFatalToolError):
    code = "authority_violation"


class ManagerSecurityViolation(ManagerFatalToolError):
    code = "security_violation"


class ManagerInvariantBreach(ManagerFatalToolError):
    code = "invariant_breach"


class ManagerSemanticGap(ManagerRecoverableToolError):
    code = "semantic_gap"


class ManagerDataGap(ManagerRecoverableToolError):
    code = "data_gap"


class ManagerUnsupportedCapability(ManagerRecoverableToolError):
    code = "unsupported_capability"


class ManagerProjectionIncomplete(ManagerRecoverableToolError):
    code = "projection_incomplete"
