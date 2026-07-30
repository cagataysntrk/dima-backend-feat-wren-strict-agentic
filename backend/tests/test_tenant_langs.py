"""§7b tenant aktif-dil seti — TenantConfig.diller → materialize company.yml → wren_service
synonyms_for(langs). Deterministik; DB/mdl gerekmez (materialize _render + _active_langs saf)."""

import pytest
from fastapi import HTTPException

from admin_app.routers.tenants import _validate_langs
from app.archetypes import DEFAULT_LANGS
from app.materialize import _render
from app.wren_service import WrenService


def test_render_writes_diller():
    out = _render("acme", ["boyahane"], None, diller=["tr", "en"])
    assert "diller:" in out and "- en" in out


def test_render_omits_diller_when_empty():
    assert "diller:" not in _render("acme", ["boyahane"], None)


def test_validate_langs_supported_ok():
    _validate_langs(None)
    _validate_langs(["tr", "en"])  # desteklenen → hata yok


def test_validate_langs_rejects_unsupported():
    with pytest.raises(HTTPException):
        _validate_langs(["fr"])  # cube-based desteklenen dil ileride; şimdi tr/en


def test_active_langs_reads_company_yml(tmp_path):
    (tmp_path / "companies" / "acme").mkdir(parents=True)
    (tmp_path / "companies" / "acme" / "company.yml").write_text(
        "name: acme\ndiller: [tr, en, de]\n")
    svc = WrenService(tmp_path / "wren-project", "duckdb", {}, company_slug="acme")
    assert svc._active_langs() == ("tr", "en", "de")  # sıra korunur (öncelik)


def test_active_langs_defaults_when_unset(tmp_path):
    svc = WrenService(tmp_path / "wren-project", "duckdb", {}, company_slug="nope")
    assert svc._active_langs() == DEFAULT_LANGS
