"""FAZ 1.1/1.2 — ilişki-türevi boyut üreteci ve güvenlik kapıları.

Üreteç, `relationships.yml`'deki `expose:` bloklarından üç artefakt üretir:
handle kolonu → is_calculated kolon → base_object'i o model olan HER cube'a boyut.
Kaldıraç sonuncusundadır: tek bildirim, o modele oturan tüm cube'lara yayılır. Bu,
elle yazılmış denormalize view'ların (parti_zengin, ik_zengin) yerini alan mekanizmadır.

Kapılar bilinçli olarak SESSİZ ATLAMA değil, BUILD KIRAN hatalardır: yanlış bir join
hatasız ve uyarısız şişmiş bir sayı üretir ve `source="cube"` rozetiyle sunulur.
Derlemenin patlaması, üretimde yanlış sayı görmekten iyidir.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from app.compose import RelationshipExposeError, build, compose

DEMO = Path(__file__).resolve().parents[1] / "demo"
COMPANY = "demo-boyahane"


# --- (a) üretim gerçekten oluyor mu ------------------------------------------

def test_uretilen_boyut_TUM_cubelara_yayilir(schema):
    """Asıl kaldıraç: `makineler.bolum` tek yerde bildirildi, `oee`/`bakim`/`kalite`/
    `makine_duruslari` cube'larının HEPSİ boyutu kazandı."""
    dims = {c["name"]: c["dimensions"] for c in schema["cubes"]}
    for cube in ("oee", "bakim", "kalite", "makine_duruslari"):
        assert "bolum" in dims.get(cube, []), f"{cube} `bolum` boyutunu almadı"


def test_cube_kendi_boyutunu_tanimlamissa_ELLE_TANIM_KAZANIR(schema):
    """`enerji_makine` `bolum`'u zaten kendi tanımlıyor (kendi etiketi/sözlüğüyle) —
    üreteç onu EZMEMELİ."""
    em = next(c for c in schema["cubes"] if c["name"] == "enerji_makine")
    assert "bolum" in em["dimensions"]
    # elle tanımın zengin sözlüğü korunmalı ("ünite" yalnız pack YAML'ında var)
    assert any("unite" in s for s in em["dimension_synonyms"].get("bolum", []))


def test_provenance_manifeste_yaziliyor():
    """`properties.origin` — boyutun hangi join'den geldiğinin kaydı. Query Contract'ın
    "bu kolon nereden geldi" sorusuna cevap verebilmesinin ön koşulu."""
    from app.config import get_settings

    cube = yaml.safe_load(
        (get_settings().resolved_project_dir() / "cubes" / "oee" / "metadata.yml")
        .read_text(encoding="utf-8"))
    d = next(x for x in cube["dimensions"] if x["name"] == "bolum")
    origin = (d.get("properties") or {}).get("origin") or {}
    assert origin.get("model") == "makineler"
    assert origin.get("column") == "bolum"
    assert origin.get("relationship") == "oee_vardiya_makineler"
    assert origin.get("hops") == 1


# --- (b) güvenlik kapıları ----------------------------------------------------

@pytest.fixture()
def proje(tmp_path) -> Path:
    """`expose:` bloğu değiştirilebilir, izole bir kaynak ağacı."""
    kok = tmp_path / "demo"
    shutil.copytree(DEMO, kok, ignore=shutil.ignore_patterns(
        "wren-project", "wren-projects", "data", "*.duckdb"))
    return kok


def _rel_yaz(kok: Path, rel: dict) -> None:
    p = kok / "companies" / COMPANY / "relationships.yml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    data["relationships"] = [r for r in data["relationships"] if r["name"] != rel["name"]]
    data["relationships"].append(rel)
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _compose(kok: Path, out: Path):
    return compose(COMPANY, kok, out)


def test_G4_kendine_referansli_iliski_REDDEDILIR(proje, tmp_path):
    """Rust çekirdeği `lineage.rs`'te PANIC atıyor ve `PanicException` bir `Exception`
    DEĞİL (MRO: PanicException → BaseException) — `except Exception` onu yakalamaz, worker
    düşer. Hesap planı parent / BOM / org şeması ERP'lerde standarttır."""
    _rel_yaz(proje, {"name": "kendine", "join_type": "MANY_TO_ONE",
                     "models": ["partiler", "partiler"],
                     "condition": "partiler.parti_no = partiler.parti_no",
                     "expose": [{"column": "makine"}]})
    with pytest.raises(RelationshipExposeError, match="kendine-referans"):
        _compose(proje, tmp_path / "out")


def test_G6_bilesik_veya_ayristirilamayan_condition_REDDEDILIR(proje, tmp_path):
    """`db_introspect` bileşik FK'yi İLK KOLONA KIRPIYOR; öyle bir join semantik olarak
    yanlıştır ve tekil olmayan bir anahtar üretir. Sessizce üretmektense reddet."""
    _rel_yaz(proje, {"name": "bilesik", "join_type": "MANY_TO_ONE",
                     "models": ["partiler", "makineler"],
                     "condition": "partiler.makine = makineler.makine AND partiler.hat = makineler.hat",
                     "expose": [{"column": "bolum"}]})
    with pytest.raises(RelationshipExposeError, match="tek-kolonlu"):
        _compose(proje, tmp_path / "out")


def test_G1_hedef_kolon_PRIMARY_KEY_degilse_REDDEDILIR(proje, tmp_path):
    """Motor `join_type`'ı OKUMAZ (ölçüldü: MANY_TO_ONE ile MANY_TO_MANY aynı SQL'i
    üretir), yani o alan bir YORUMDUR. Tek yapısal benzersizlik sinyali hedef modelin
    `primary_key`'idir — Snowflake'in `REFERENCES <PK/UNIQUE>` kuralıyla aynı.

    `partiler.operator = personel.ad_soyad` bunun canlı örneğidir: `ad_soyad` PK DEĞİL.
    Bugün benzersiz ama bu bir VERİ özelliğidir, şema garantisi değil — üreteç onu
    otomatik üretmeyi REDDEDER; `models_enrich.yml` ile ELLE, bilinçli bir istisna olarak
    tanımlanmıştır (veri düzeyi doğrulama: tests/test_relationship_health.py).
    """
    _rel_yaz(proje, {"name": "partiler_personel", "join_type": "MANY_TO_ONE",
                     "models": ["partiler", "personel"],
                     "condition": "partiler.operator = personel.ad_soyad",
                     "expose": [{"column": "cinsiyet"}]})
    with pytest.raises(RelationshipExposeError, match="primary_key"):
        _compose(proje, tmp_path / "out")


def test_G5_hedef_kolonu_yoksa_REDDEDILIR(proje, tmp_path):
    _rel_yaz(proje, {"name": "oee_vardiya_makineler", "join_type": "MANY_TO_ONE",
                     "models": ["oee_vardiya", "makineler"],
                     "condition": "oee_vardiya.makine = makineler.makine",
                     "expose": [{"column": "olmayan_kolon"}]})
    with pytest.raises(RelationshipExposeError, match="olmayan_kolon"):
        _compose(proje, tmp_path / "out")


def test_G5b_etiket_mevcut_boyutun_sozlugunu_CALAMAZ(proje, tmp_path):
    """`_with_label` (ADR-0018 "LABEL ⊆ SYNONYM") etiketi KELİMELERİNE AYIRIP sinonim yapar.
    `label: makine bölümü` sessizce `makine` sinonimini doğurur ve o cube'da zaten bir
    `makine` boyutu varsa aynı soru İKİ boyut eşleştirir → GROUP BY bölünür, sayılar değişir.

    Bu gerçekten yaşandı: ilk `expose` denemesinde `test_surdurulebilirlik_cube` anında
    düştü (`['makine']` yerine `['makine','makine_bolum']`). Faz 0.5'in tahkimi bunu
    kurtaramaz — iki eşleşme de tam kelime `makine`'dir, öz alt-dizi ilişkisi YOKTUR.
    """
    _rel_yaz(proje, {"name": "partiler_makineler", "join_type": "MANY_TO_ONE",
                     "models": ["partiler", "makineler"],
                     "condition": "partiler.makine = makineler.makine",
                     "expose": [{"column": "bolum", "as": "mk_bolum",
                                 "label": "makine bölümü"}]})
    with pytest.raises(RelationshipExposeError, match="LABEL"):
        _compose(proje, tmp_path / "out")


def test_gecerli_expose_SORUNSUZ_derlenir(proje, tmp_path):
    """Kapılar fazla agresif olmamalı: geçerli bir bildirim compose+build'den geçmeli
    ve üç artefaktı da üretmeli."""
    out = tmp_path / "out"
    _compose(proje, out)
    build(out)

    model = yaml.safe_load((out / "models" / "oee_vardiya" / "metadata.yml")
                           .read_text(encoding="utf-8"))
    adlar = {c["name"] for c in model["columns"]}
    assert "makineler" in adlar, "handle kolonu üretilmedi"
    assert "makineler_bolum" in adlar, "calc kolonu üretilmedi"
    calc = next(c for c in model["columns"] if c["name"] == "makineler_bolum")
    assert calc["is_calculated"] and calc["expression"] == "makineler.bolum"

    cube = yaml.safe_load((out / "cubes" / "oee" / "metadata.yml").read_text(encoding="utf-8"))
    assert any(d["name"] == "bolum" for d in cube["dimensions"]), "cube boyutu üretilmedi"


def test_G10_always_filter_tasiyan_modele_join_REDDEDILIR(proje, tmp_path):
    """`always_filter` bir CUBE özelliğidir ve yalnız o cube'un kendi SQL'ine enjekte
    edilir. Bir başka cube o modele JOIN'lediğinde filtre UYGULANMAZ — join, model
    katmanının ALTINDA gerçekleşir.

    Ölçüldü (2 Ağustos 2026): `ticaret.always_filter = "tur='satis'"` iken
    `fatura_satirlari` üzerinden `faturalar`'a join edilince **34 milyon TL'lik `alis`
    verisi filtreyi geçti**. Bu, Discovery'de bilinen bir baypastı; otomatik join onu
    "handle üretilen HER cube"a yayardı. Sessizce yaymaktansa üretimi reddediyoruz.
    """
    # `makineler`'i filtreli bir cube'un tabanı yap → ona giden expose reddedilmeli.
    cube_yolu = proje / "packs" / "modul" / "oee" / "cubes" / "makine_filtreli"
    cube_yolu.mkdir(parents=True, exist_ok=True)
    (cube_yolu / "metadata.yml").write_text(yaml.safe_dump({
        "name": "makine_filtreli", "base_object": "makineler",
        "always_filter": "bolum <> 'Arşiv'",
        "measures": [{"name": "adet", "expression": "COUNT(*)", "type": "DOUBLE"}],
        "dimensions": [{"name": "mk", "expression": "makine", "type": "VARCHAR"}],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")

    with pytest.raises(RelationshipExposeError, match="always_filter"):
        _compose(proje, tmp_path / "out")
