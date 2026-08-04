"""FAZ 3.6 — **COLD-START METRİK ÖNERİSİ + GÖRÜNMEZ KOLON.** [bayrak: `coldstart_metrik`]

`db_introspect.draft_mdl()` **zaten** model çıkarıyordu; eksik olan **önem sıralamasıydı**:
yeni bir müşteri 200 tablo görüyor ve hangisinden başlayacağını **bilmiyor**.
*Bir liste, sıralanmadığı sürece bir yüktür.*

## 🔴 GÖRÜNMEZ KOLON — maddenin kapısı, birebir

*"Kapatılan kolon üretilen MDL'de **YOK**."* — çünkü *"gösterme"* ile *"yazma"* arasındaki
fark bu maddenin bütün değeridir: gizlenen **ama yazılan** bir kolon, bir prompt
sızıntısında ya da bir Discovery sorgusunda **geri gelir**.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

from app import coldstart as cs

KOK = pathlib.Path(__file__).resolve().parents[1]


# ── 1 · 🔴 GÖRÜNMEZ KOLON — MDL'DE YOK ─────────────────────────────────────

def test_GIZLI_KOLON_URETILMIYOR():
    kolonlar = [{"name": "id"}, {"name": "tc_kimlik"}, {"name": "tutar"}]
    out = cs.gorunur_kolonlar(kolonlar, ["tc_kimlik"])
    assert [k["name"] for k in out] == ["id", "tutar"]


def test_BUYUK_KUCUK_HARF_DUYARSIZ():
    """🔴 Kullanıcı `TCKN` yazıp kolon `tckn` olduğunda gizleme **sessizce çalışmazsa**,
    kullanıcı gizlediğini **sanır**. *Çalıştığı sanılan bir kapı, olmayan bir kapıdan
    tehlikelidir.*"""
    assert cs.gorunur_kolonlar([{"name": "tckn"}], ["TCKN"]) == []
    assert cs.gorunur_kolonlar(["TCKN"], ["  tckn "]) == []


def test_GIZLI_YOKSA_HICBIR_SEY_DEGISMIYOR():
    k = [{"name": "a"}, {"name": "b"}]
    assert cs.gorunur_kolonlar(k, None) == k and cs.gorunur_kolonlar(k, []) == k


def test_YAZICI_GIZLI_KOLONU_MDLYE_YAZMIYOR(tmp_path):
    """🔴 **MADDENİN KAPISI, BİREBİR:** *"kapatılan kolon üretilen MDL'de YOK"*."""
    from app.mdl_writer import write_introspected_schema

    from types import SimpleNamespace as _N

    class _T:
        def __init__(self):
            self.name = "musteri"
            # ⚠ Yazıcı `IntrospectedColumn` NESNESİ bekliyor (nitelik erişimi), sözlük
            # değil — ilk sürümde sözlük geçirdim ve kapı `AttributeError` ile yakaladı.
            self.columns = [_N(name="id", type="INTEGER", values=None, is_primary_key=False, nullable=True),
                            _N(name="tc_kimlik", type="VARCHAR", values=None, is_primary_key=False, nullable=True),
                            _N(name="ad", type="VARCHAR", values=None, is_primary_key=False, nullable=True)]

    draft = {"cubes": [{"name": "musteri", "include": True, "measures": [],
                        "dimensions": ["ad", "tc_kimlik"], "time_dimensions": [],
                        "gizli_kolonlar": ["tc_kimlik"]}], "relationships": []}
    yazilan, _ = write_introspected_schema(tmp_path, "sirket", [_T()], draft)
    assert yazilan == ["musteri"]
    model = yaml.safe_load(
        (tmp_path / "companies" / "sirket" / "models" / "musteri" / "metadata.yml")
        .read_text(encoding="utf-8"))
    adlar = {c.get("name") for c in (model.get("columns") or [])}
    assert "tc_kimlik" not in adlar, "GİZLİ KOLON MDL'YE YAZILMIŞ — LLM onu görebilir"
    assert {"id", "ad"} <= adlar, "gizli olmayan kolonlar da düşmüş"


def test_CUBE_TARAFI_DA_SUZULUYOR(tmp_path):
    """⚠ Gizli bir kolon ölçü/boyut listesinde kalırsa MDL **var olmayan** bir kolona
    bakar ve `validate_project()` **haklı olarak** patlar."""
    from app.mdl_writer import cube_yaml_path, write_introspected_schema

    from types import SimpleNamespace as _N

    class _T:
        name = "musteri"
        columns = [_N(name="id", type="INTEGER", values=None, is_primary_key=False, nullable=True),
                   _N(name="tc_kimlik", type="VARCHAR", values=None, is_primary_key=False, nullable=True)]

    draft = {"cubes": [{"name": "musteri", "include": True, "measures": [],
                        "dimensions": ["tc_kimlik"], "time_dimensions": [],
                        "gizli_kolonlar": ["tc_kimlik"]}], "relationships": []}
    write_introspected_schema(tmp_path, "sirket", [_T()], draft)
    cube = yaml.safe_load(cube_yaml_path(tmp_path, "sirket", "musteri")
                          .read_text(encoding="utf-8"))
    boyutlar = {d.get("name") if isinstance(d, dict) else d
                for d in (cube.get("dimensions") or [])}
    assert "tc_kimlik" not in boyutlar


def test_MASKELEME_ILE_AYNI_SEY_DEGIL():
    """⚠ `pii.py` **maskeler** (veri çıkışında); burası **hiç üretmez** (şema girişinde).
    İki farklı katman ve **biri ötekinin yerine geçmez** — maskelenen bir kolon hâlâ
    MDL'de durur ve LLM onu **görür**."""
    kaynak = (KOK / "app" / "coldstart.py").read_text(encoding="utf-8")
    assert "biri ötekinin yerine geçmez" in kaynak


# ── 2 · SIRALAMA — sinyal, tahmin değil ────────────────────────────────────

def test_ONEM_IKI_SINYALDEN():
    buyuk = cs.onem_puani({"row_count": 200_000, "columns": ["tutar", "adet"]})
    kucuk = cs.onem_puani({"row_count": 10, "columns": ["aciklama", "not"]})
    assert buyuk == 1.0 and kucuk < 0.1


def test_AGIRLIK_UYDURULMADI():
    """🔴 Kalibre edilmemiş bir ağırlık (`0.7 × satır + 0.3 × sinyal`) yazmak, bu deponun
    *"kalibre edilmemiş bir sayı güven değil süstür"* kuralının **sıralama tarafındaki**
    hâli olurdu. **Eşit ağırlık, bilmediğimizi beyan eden ağırlıktır.**"""
    kaynak = (KOK / "app" / "coldstart.py").read_text(encoding="utf-8")
    assert "bilmediğimizi beyan eden" in kaynak
    # Yapısal: eşit ağırlık → iki sinyalin yeri değişince puan DEĞİŞMEZ.
    a = cs.onem_puani({"row_count": 100_000, "columns": ["aciklama"]})
    b = cs.onem_puani({"row_count": 0, "columns": ["tutar"]})
    assert a == b == 0.5


def test_SIRALAMA_ELEMIYOR():
    """⚠ *Sıralama bir öneridir; gizleme bir karardır ve kararı kullanıcı verir.* Düşük
    puanlı bir tabloyu listeden düşürmek, müşterinin **kendi verisini göremediği** bir
    onboarding üretirdi."""
    t = [{"name": "a", "row_count": 0, "columns": []},
         {"name": "b", "row_count": 999_999, "columns": ["tutar"]}]
    out = cs.sirala(t)
    assert len(out) == 2 and out[0]["name"] == "b"
    assert all("onem" in x for x in out)


def test_SIRALAMA_KARARLI():
    """Eşit puanlı tablolar **ada göre** sıralanır — rastgele sıra, aynı ekranı iki kez
    açan kullanıcıya farklı liste gösterirdi."""
    t = [{"name": "z", "row_count": 0, "columns": []},
         {"name": "a", "row_count": 0, "columns": []}]
    assert [x["name"] for x in cs.sirala(t)] == ["a", "z"]


# ── 3 · SÖZLEŞME ────────────────────────────────────────────────────────────

def test_SOZLESME_ALANLARI():
    from app.schemas import DraftCube

    d = DraftCube(name="x")
    assert d.gizli_kolonlar == [] and d.onem is None, "varsayılan gizleme YAPILMIYOR olmalı"


def test_ADR_0008_ILE_CELISMIYOR():
    """⚠ `_OLCU_SINYALI` bir **sözlük değil**: eşleşme bir **sıralama** üretir, bir cevap
    değil. Yanlış sıralama bir soruyu **cevapsız bırakmaz**, yalnız listede aşağı iter."""
    kaynak = (KOK / "app" / "coldstart.py").read_text(encoding="utf-8")
    assert "ADR-0008" in kaynak and "bir cevap değil" in kaynak
