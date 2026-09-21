"""Runtime-owned source-span registry for Day 6.5.

The Manager may reference src_* IDs but cannot mint or modify them.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.v2.manager_models import SourceSpanRef


@dataclass(frozen=True)
class _Message:
    message_id: str
    text: str
    sha256: str


class SourceSpanRegistry:
    def __init__(self) -> None:
        self._messages: dict[str, _Message] = {}
        self._spans: dict[str, SourceSpanRef] = {}

    @staticmethod
    def message_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def register_message(self, *, message_id: str, text: str) -> str:
        if not message_id or not text:
            raise ValueError("message_id ve text boş olamaz")
        digest = self.message_hash(text)
        existing = self._messages.get(message_id)
        if existing is not None and existing.sha256 != digest:
            raise ValueError("aynı message_id farklı içerikle yeniden kaydedilemez")
        self._messages[message_id] = _Message(message_id, text, digest)
        return digest

    def mint_span(self, *, message_id: str, start_offset: int, end_offset: int) -> SourceSpanRef:
        message = self._messages.get(message_id)
        if message is None:
            raise KeyError("source message registry'de yok")
        if start_offset < 0 or end_offset <= start_offset or end_offset > len(message.text):
            raise ValueError("source span offset geçersiz")
        exact = message.text[start_offset:end_offset]
        payload = f"{message.message_id}\x1f{message.sha256}\x1f{start_offset}\x1f{end_offset}"
        ref = "src_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        span = SourceSpanRef(
            source_ref=ref,
            message_id=message.message_id,
            message_hash=message.sha256,
            start_offset=start_offset,
            end_offset=end_offset,
            exact_surface=exact,
        )
        self._spans[ref] = span
        return span

    def mint_exact(self, *, message_id: str, surface: str, occurrence: int = 0) -> SourceSpanRef:
        message = self._messages.get(message_id)
        if message is None:
            raise KeyError("source message registry'de yok")
        if not surface:
            raise ValueError("surface boş olamaz")
        start = -1
        cursor = 0
        for _ in range(occurrence + 1):
            start = message.text.find(surface, cursor)
            if start < 0:
                raise ValueError("surface source message içinde bulunamadı")
            cursor = start + len(surface)
        return self.mint_span(
            message_id=message_id,
            start_offset=start,
            end_offset=start + len(surface),
        )

    def get(self, source_ref: str) -> SourceSpanRef:
        try:
            return self._spans[source_ref]
        except KeyError as exc:
            raise KeyError("unknown/fabricated source span ref") from exc

    def validate(self, source_ref: str, *, expected_message_hash: str | None = None) -> SourceSpanRef:
        span = self.get(source_ref)
        message = self._messages.get(span.message_id)
        if message is None or message.sha256 != span.message_hash:
            raise ValueError("source span message binding geçersiz")
        if message.text[span.start_offset:span.end_offset] != span.exact_surface:
            raise ValueError("source span exact surface doğrulanamadı")
        if expected_message_hash is not None and span.message_hash != expected_message_hash:
            raise ValueError("source span farklı message hash'e bağlı")
        return span
