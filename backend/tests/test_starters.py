"""K1 starter_questions birim testleri — rol filtresi + küratör çözümü. Deterministik,
DB yok; _curated monkeypatch'lenir (pack zinciri okuma ayrı)."""

from types import SimpleNamespace

from app import starters
from app.starters import starter_questions


def _patch(monkeypatch, curated):
    monkeypatch.setattr(starters, "_curated", lambda settings: curated)


def test_no_roles_shows_untagged_only(monkeypatch):
    _patch(monkeypatch, [
        {"label": "A", "query": "a"},
        {"label": "B", "query": "b", "roles": ["finans"]},
    ])
    out = starter_questions(SimpleNamespace(), None)
    assert [s["label"] for s in out] == ["A"]  # rol-etiketli B gizli


def test_matching_role_shown(monkeypatch):
    _patch(monkeypatch, [
        {"label": "A", "query": "a"},
        {"label": "B", "query": "b", "roles": ["finans"]},
    ])
    out = starter_questions(SimpleNamespace(), SimpleNamespace(roles=["finans"]))
    assert [s["label"] for s in out] == ["A", "B"]


def test_label_defaults_to_query(monkeypatch):
    _patch(monkeypatch, [{"query": "makine bazında oee"}])
    out = starter_questions(SimpleNamespace(), None)
    assert out == [{"label": "makine bazında oee", "query": "makine bazında oee"}]


def test_invalid_entries_skipped(monkeypatch):
    _patch(monkeypatch, ["bozuk", {"label": "yok query"}, {"query": "ok"}])
    out = starter_questions(SimpleNamespace(), None)
    assert out == [{"label": "ok", "query": "ok"}]


def test_empty_curated_returns_empty(monkeypatch):
    _patch(monkeypatch, [])
    assert starter_questions(SimpleNamespace(), None) == []
