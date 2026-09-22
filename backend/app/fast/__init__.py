"""DIMA Fast Track isolated product namespace.

This package intentionally contains no runtime implementation at bootstrap.
Functional analytics begins only after F0A pinned Metabase capability preflight.

Forbidden hot-path dependencies:
- Wren runtime
- app.v2 semantic/manager owners
- app.v3 semantic/compiler owners
"""
