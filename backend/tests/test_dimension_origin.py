"""FAZ 1.3 — `dimension_origin`: bir boyut cube'un KENDİ tablosundan mı, join'den mi geldi?

Bugüne kadar `WrenService.schema()` boyutun `expression`'ını bile atıyordu — router
açısından `parti.cinsiyet` ile `parti.makine` AYIRT EDİLEMEZDİ. İlişki-türevi boyutlar
yayıldıkça bu körlük pahalıya patlar:

  * Query Contract "bu kolon hangi join'den geldi" diyemez (ADR-0010, ürünün tezi
    "her sayının kaynağını kanıtlayabilmek").
  * `_match_cube` tie-break'i, boyutu YERELİNDE taşıyan cube ile 2 sıçrama ötesinden
    ulaşanı ayırt edemez (Faz 3.2) — enrichment yayıldıkça belirsizlik ARTAR.
  * Fan-out riski anote edilemez (hangi ilişki, kaç sıçrama).
  * Drill `base_object` ötesine inemez.

`base_object` alanı da tam bu gerekçeyle sonradan eklenmişti (wren_service.py:209-214):
drill'in ihtiyacı vardı, yoktu, tek çare YAML'ı doğrudan okumaktı.
"""

from __future__ import annotations

import pytest

from tests.conftest import ask


def _cube(schema, ad):
    return next(c for c in schema["cubes"] if c["name"] == ad)


def test_iliski_turevi_boyut_origin_TASIR(schema):
    o = _cube(schema, "oee").get("dimension_origin") or {}
    assert "bolum" in o, "üretilen boyut provenance taşımıyor"
    assert o["bolum"] == {"model": "makineler", "column": "bolum",
                          "relationship": "oee_vardiya_makineler", "hops": 1}


def test_YEREL_boyut_origin_TASIMAZ(schema):
    """Sözlük yalnız ilişki-türevi boyutları içerir — yerel olanlar sessizdir.
    (Aksi halde "join'den mi geldi" sorusu her boyut için evet olurdu.)"""
    o = _cube(schema, "oee").get("dimension_origin") or {}
    for yerel in ("makine", "hat", "vardiya"):
        assert yerel not in o, f"{yerel} yerel bir boyut, origin taşımamalı"


def test_origin_TUM_uretilen_cubelarda_var(schema):
    """Tek `expose` bildirimi → çok cube; provenance hepsinde olmalı."""
    for cube, dim, rel in (("bakim", "bolum", "ariza_kayitlari_makineler"),
                           ("kalite", "bolum", "tamir_rework_makineler"),
                           ("parti", "kisim", "partiler_makineler")):
        o = _cube(schema, cube).get("dimension_origin") or {}
        assert o.get(dim, {}).get("relationship") == rel, f"{cube}.{dim} provenance eksik"


def test_join_soyagaci_CEVAPTA_gorunur(client):
    """Uçtan uca: ilişki üzerinden gelen bir boyutla sorulan soru, cevabında bunu SÖYLER."""
    d = ask(client, "bu yıl bölüm bazında ortalama oee")
    assert d.get("cube_query", {}).get("dimensions") == ["bolum"], d.get("note")
    aciklama = d.get("calculation_explanation") or ""
    assert "makineler.bolum" in aciklama, f"join soyağacı yok: {aciklama!r}"
    assert "oee_vardiya_makineler" in aciklama


def test_yerel_boyutta_soyagaci_EKLENMEZ(client):
    """Gürültü yapma: cube'un kendi kolonunda ilişki cümlesi olmamalı."""
    d = ask(client, "bu yıl makine bazında ortalama oee")
    assert d.get("cube_query", {}).get("dimensions") == ["makine"], d.get("note")
    assert "ilişkisi üzerinden" not in (d.get("calculation_explanation") or "")


@pytest.mark.parametrize("cube_adi", ["oee", "bakim", "kalite", "parti", "surdurulebilirlik"])
def test_origin_kayitli_iliski_gercekten_VAR(schema, cube_adi):
    """Provenance uydurma olmamalı: adı geçen ilişki `relationships.yml`'de bulunmalı."""
    import yaml

    from app.config import get_settings

    rels = {r["name"] for r in (yaml.safe_load(
        (get_settings().resolved_project_dir() / "relationships.yml").read_text(
            encoding="utf-8")) or {}).get("relationships", [])}
    for d, o in (_cube(schema, cube_adi).get("dimension_origin") or {}).items():
        assert o["relationship"] in rels, f"{cube_adi}.{d} olmayan bir ilişkiye atıf yapıyor"
