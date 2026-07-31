"""Cube YAML yazıcı (Faz 2d, Discovery→Promote): onaylanmış bir `MeasureCandidate`'ı
VAR OLAN bir cube'un `metadata.yml`'ına round-trip-güvenli EKLER.

`ruamel.yaml` kullanılır (pyyaml DEĞİL): pyyaml `safe_load`+`dump` tüm yorumları/orijinal
biçimlendirmeyi kaybeder — bu repodaki cube YAML'ları (bkz. demo/companies/*/cubes/*/
metadata.yml) kasıtlı, açıklayıcı yorumlarla dolu (ör. çakışma-koruması gerekçeleri);
onay akışının bunları silmesi kabul edilemez (`git diff` de dev-inceleme için asgari
kalmalı). `indent(mapping=2, sequence=4, offset=2)` + `synonyms` listesi flow-style
zorlanır — reponun mevcut YAML kuralıyla (``synonyms: [a, b, c]``) birebir eşleşir.

Yalnız MEVCUT bir cube'a ölçü EKLER; yeni cube/model/ilişki icat ETMEZ — `base_object`
zaten var olmalı (Discovery bir soruyu cevapladıysa, dokunduğu tablo/model zaten MDL'de
demektir; yeni bir SEMANTİK ölçü ekliyoruz, yeni bir FİZİKSEL model değil)."""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class MeasureWriteError(Exception):
    """Ölçü YAML'a eklenemedi (ad çakışması, cube YAML'ı bulunamadı, vb.)."""


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096  # uzun ifade/sinonim satırları sarılmasın (mevcut dosya biçimiyle tutarlı)
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def cube_yaml_path(base: Path, company: str, cube: str) -> Path:
    """companies/<company>/cubes/<cube>/metadata.yml — compose'un ŞİRKET katmanı
    (en az invaziv: yalnız o tenant'ı etkiler, sektör/kaynak pack'lerine dokunmaz)."""
    return base / "companies" / company / "cubes" / cube / "metadata.yml"


def add_measure_to_cube_yaml(
    yaml_path: Path,
    *,
    measure_name: str,
    expression: str,
    type_: str = "DOUBLE",
    synonyms: list[str] | None = None,
    lower_is_better: bool | None = None,
    label: str | None = None,
) -> None:
    """`yaml_path`'teki cube'un `measures:` listesine yeni bir ölçü ekler (dosyanın geri
    kalanını, yorumları ve biçimlendirmeyi korur). Ölçü adı zaten varsa `MeasureWriteError`."""
    if not yaml_path.exists():
        raise MeasureWriteError(f"Cube YAML bulunamadı: {yaml_path}")
    y = _yaml()
    data = y.load(yaml_path.read_text(encoding="utf-8"))
    if data is None or not isinstance(data, dict):
        raise MeasureWriteError(f"Cube YAML boş/bozuk: {yaml_path}")

    measures = data.get("measures")
    if measures is None:
        measures = CommentedSeq()
        data["measures"] = measures
    for m in measures:
        if isinstance(m, dict) and m.get("name") == measure_name:
            raise MeasureWriteError(f"Ölçü zaten var: {measure_name}")

    new_measure = CommentedMap()
    new_measure["name"] = measure_name
    new_measure["expression"] = expression
    new_measure["type"] = type_
    if label:
        new_measure["label"] = label
    if synonyms:
        syns = CommentedSeq(list(synonyms))
        syns.fa.set_flow_style()
        new_measure["synonyms"] = syns
    if lower_is_better is not None:
        new_measure["lower_is_better"] = bool(lower_is_better)

    measures.append(new_measure)
    with yaml_path.open("w", encoding="utf-8") as f:
        y.dump(data, f)


def resolve_cube_yaml_for_edit(base: Path, company: str, cube: str,
                               compiled_project_dir: Path) -> Path:
    """DÜZENLENECEK (tenant-scoped) kaynak YAML yolu. Şirket katmanında zaten kendi
    dosyası varsa onu döner. Yoksa (cube bir PACK'ten geliyor — sektör/kaynak/kesişim/
    modül, birden çok tenant PAYLAŞIYOR olabilir) `compose()`'un zaten katmanları çözdüğü
    DERLENMİŞ içeriği (`compiled_project_dir/cubes/<cube>/metadata.yml`) şirket katmanına
    byte-birebir KOPYALAR (yorumlar dahil) ve o kopyayı döner: `compose()`'da şirket katmanı
    HER ZAMAN SON kopyalanandır (bkz. app/compose.py `compose()` — `layers.append((company_dir,
    None))` en sonda), bu yüzden bu kopya bundan sonra bu tenant için KAZANIR — paylaşılan
    pack dosyasına HİÇ dokunulmaz, diğer tenant'lar etkilenmez."""
    import shutil

    company_path = cube_yaml_path(base, company, cube)
    if company_path.exists():
        return company_path
    compiled_path = compiled_project_dir / "cubes" / cube / "metadata.yml"
    if not compiled_path.exists():
        raise MeasureWriteError(f"Cube bulunamadı (derlenmiş projede de yok): {cube}")
    company_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(compiled_path, company_path)
    return company_path


def cube_base_object(yaml_path: Path) -> str | None:
    """Cube'un `base_object`'i (dry-plan doğrulaması için: `SELECT {expr} FROM {base}`)."""
    if not yaml_path.exists():
        return None
    y = _yaml()
    data = y.load(yaml_path.read_text(encoding="utf-8")) or {}
    return data.get("base_object")
