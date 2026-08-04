"""Cube YAML yazıcı (Faz 2d, Discovery→Promote): onaylanmış bir `MeasureCandidate`'ı
VAR OLAN bir cube'un `metadata.yml`'ına round-trip-güvenli EKLER.

`ruamel.yaml` kullanılır (pyyaml DEĞİL): pyyaml `safe_load`+`dump` tüm yorumları/orijinal
biçimlendirmeyi kaybeder — bu repodaki cube YAML'ları (bkz. demo/companies/*/cubes/*/
metadata.yml) kasıtlı, açıklayıcı yorumlarla dolu (ör. çakışma-koruması gerekçeleri);
onay akışının bunları silmesi kabul edilemez (`git diff` de dev-inceleme için asgari
kalmalı). `synonyms` listesi flow-style zorlanır — reponun mevcut YAML kuralıyla
(``synonyms: [a, b, c]``) birebir eşleşir.

Liste girintisi SABİT DEĞİL, düzenlenen dosyadan SEZİLİR (bkz. `_yaml`): sabit
`sequence=4, offset=2` ayarı, `- x` biçimindeki repo dosyalarını her yazımda BAŞTAN
biçimlendiriyordu ve 6 satırlık bir ekleme 500 satırlık bir diff üretiyordu — "git diff
asgari kalmalı" hedefinin tam tersi. Faz 4.2'nin diff önizlemesi bunu görünür kıldı.

Yalnız MEVCUT bir cube'a ölçü EKLER; yeni cube/model/ilişki icat ETMEZ — `base_object`
zaten var olmalı (Discovery bir soruyu cevapladıysa, dokunduğu tablo/model zaten MDL'de
demektir; yeni bir SEMANTİK ölçü ekliyoruz, yeni bir FİZİKSEL model değil)."""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class MeasureWriteError(Exception):
    """Ölçü YAML'a eklenemedi (ad çakışması, cube YAML'ı bulunamadı, vb.)."""


def _yaml(text: str | None = None) -> YAML:
    """ruamel round-trip yükleyici/yazıcı — liste girintisi DÜZENLENEN DOSYAYA UYDURULUR.

    Neden sabit değil (2 Ağustos 2026, Faz 4.2'nin diff önizlemesi ortaya çıkardı): girinti
    `sequence=4, offset=2` olarak sabitti ve liste öğelerini `  - x` diye yazıyordu. Oysa
    repodaki cube YAML'ları (ve `compose()`'un ürettiği derlenmiş kopyalar) `- x` kullanıyor.
    Sonuç: bir ölçü eklemek DOSYANIN TAMAMINI yeniden biçimlendiriyordu — 266 satırın 266'sı
    da değişmiş görünüyordu (içerik aynı, yalnız 2 boşluk kaymış).

    Kimse fark etmemişti çünkü kimse diff'e bakmıyordu. Planın istediği *"checkbox + diff
    onayı"* akışında ise bu ölümcüldür: 6 satırlık bir eklemeyi 500 satırlık bir gürültünün
    içinde incelemek, incelememekle aynı şeydir. Git geçmişinde de her onay dosyayı baştan
    yazmış gibi görünürdü.

    `text` verilirse girinti ondan SEZİLİR, böylece hangi yazıcı üretmiş olursa olsun
    round-trip byte-kararlı kalır; verilmezse repo geneli varsayılan (`- x`) kullanılır.
    """
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096  # uzun ifade/sinonim satırları sarılmasın (mevcut dosya biçimiyle tutarlı)
    seq, off = _sequence_indent(text or "")
    y.indent(mapping=2, sequence=seq, offset=off)
    return y


def _sequence_indent(text: str) -> tuple[int, int]:
    """Dosyanın liste girintisi → ruamel `(sequence, offset)`.

    `- x` (kapsayıcı anahtarla aynı sütun) → `(2, 0)`;  `  - x` → `(4, 2)`.
    Bulunamazsa `(2, 0)` — repo genelindeki biçim.
    """
    onceki_girinti = 0
    for satir in text.splitlines():
        if not satir.strip() or satir.lstrip().startswith("#"):
            continue
        girinti = len(satir) - len(satir.lstrip())
        if satir.lstrip().startswith("- "):
            return (4, 2) if girinti > onceki_girinti else (2, 0)
        onceki_girinti = girinti
    return (2, 0)


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
    metin = yaml_path.read_text(encoding="utf-8")
    y = _yaml(metin)  # girinti DÜZENLENEN dosyadan sezilir (bkz. _yaml)
    data = y.load(metin)
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


def cube_yaml_source_for_preview(base: Path, company: str, cube: str,
                                 compiled_project_dir: Path) -> tuple[Path, bool]:
    """ÖNİZLEME için okunacak YAML yolu + şirket katmanında YENİ mi oluşacağı.

    `resolve_cube_yaml_for_edit`in **yan etkisiz** ikizi. O fonksiyon, cube bir pack'ten
    geliyorsa derlenmiş içeriği şirket katmanına KOPYALAR — bir önizleme bunu yapamaz:
    "onaylamadan önce ne değişecek" sorusunun cevabı, sorulmuş olmakla dosya sistemini
    değiştirmemelidir. İnceleyen kişi vazgeçtiğinde geride yeni bir dosya kalmamalı.

    İkinci dönen değer inceleyene gösterilir: `True` ise bu onay, cube'u bu tenant'ın
    şirket katmanına **taşıyacak** demektir (paylaşılan pack dosyasına dokunulmaz) — bu,
    diff'te görünmeyen ama bilinmesi gereken bir sonuçtur.
    """
    company_path = cube_yaml_path(base, company, cube)
    if company_path.exists():
        return company_path, False
    compiled_path = compiled_project_dir / "cubes" / cube / "metadata.yml"
    if not compiled_path.exists():
        raise MeasureWriteError(f"Cube bulunamadı (derlenmiş projede de yok): {cube}")
    return compiled_path, True


def cube_base_object(yaml_path: Path) -> str | None:
    """Cube'un `base_object`'i (dry-plan doğrulaması için: `SELECT {expr} FROM {base}`)."""
    if not yaml_path.exists():
        return None
    metin = yaml_path.read_text(encoding="utf-8")
    y = _yaml(metin)
    data = y.load(metin) or {}
    return data.get("base_object")


# ── Faz 4.5 (31 Temmuz 2026) — introspect edilmiş bir DB bağlantısından YENİ model+cube+
# ilişki yazımı. Yukarıdaki fonksiyonlardan FARKI: onlar MEVCUT bir cube'a ölçü EKLER,
# bunlar YENİ fiziksel model + YENİ semantik cube + YENİ ilişki YARATIR — DB bağlama
# sihirbazının (app/db_introspect.py) kullanıcı-onaylı taslağını gerçek dosyaya döker.
# Aynı ruamel.yaml round-trip-güvenli yazıcı; şirket klasöründe HENÜZ VAR OLMAYAN
# dosyalar için (var olan bir cube/modelin üstüne YAZILMAZ — çakışma varsa atlanır,
# ConnectionConfirmResult bunu `written_cubes`'ta göstermez).



def write_model_yaml(base: Path, company: str, table_name: str, columns: list,
                     primary_key: str | None, *, db_schema: str = "public") -> Path:
    """Wren MODEL (fiziksel tablo bağı) — `models/<table>/metadata.yml`. `columns`:
    `app/db_introspect.py::IntrospectedColumn` listesi. Dosya zaten varsa DOKUNULMAZ
    (var olan bir fiziksel modelin üstüne asla sessizce yazılmaz)."""
    path = base / "companies" / company / "models" / table_name / "metadata.yml"
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    y = _yaml()
    data = CommentedMap()
    data["name"] = table_name
    tref = CommentedMap()
    tref["schema"] = db_schema
    tref["table"] = table_name
    data["table_reference"] = tref
    cols = CommentedSeq()
    for c in columns:
        cm = CommentedMap()
        cm["name"] = c.name
        cm["type"] = c.type
        if c.is_primary_key:
            cm["is_primary_key"] = True
        if not c.nullable:
            cm["not_null"] = True
        cols.append(cm)
    data["columns"] = cols
    if primary_key:
        data["primary_key"] = primary_key
    with path.open("w", encoding="utf-8") as f:
        y.dump(data, f)
    return path


def write_cube_yaml(base: Path, company: str, cube: dict) -> Path:
    """Semantik CUBE — `cubes/<name>/metadata.yml`. `cube`: `app/db_introspect.py::
    draft_mdl`'in ürettiği (kullanıcı onayından geçmiş) sözlük {name, measures,
    dimensions, time_dimensions}. Sinonim ÜRETİLMEZ (yalnız tablo adının kendisi) —
    kullanıcı sonradan cube_synonyms.yml ile ZENGİNLEŞTİREBİLİR (mevcut mekanizma,
    app/compose.py::_merge_cube_synonyms); burada TAHMİNİ sinonim UYDURULMAZ. Dosya
    zaten varsa DOKUNULMAZ."""
    name = cube["name"]
    path = cube_yaml_path(base, company, name)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    y = _yaml()
    data = CommentedMap()
    data["name"] = name
    data["label"] = name.replace("_", " ")
    data["base_object"] = name
    syns = CommentedSeq([name])
    syns.fa.set_flow_style()
    data["synonyms"] = syns

    measures = CommentedSeq()
    for m in cube.get("measures") or []:
        mm = CommentedMap()
        mm["name"] = m
        mm["expression"] = f"SUM({m})"
        mm["type"] = "DOUBLE"
        measures.append(mm)
    if measures:
        data["measures"] = measures

    dimensions = CommentedSeq()
    for d in cube.get("dimensions") or []:
        dm = CommentedMap()
        dm["name"] = d
        dm["expression"] = d
        dm["type"] = "VARCHAR"
        dimensions.append(dm)
    if dimensions:
        data["dimensions"] = dimensions

    time_dims = CommentedSeq()
    for t in cube.get("time_dimensions") or []:
        tm = CommentedMap()
        tm["name"] = t
        tm["expression"] = t
        tm["type"] = "DATE"
        time_dims.append(tm)
    if time_dims:
        data["time_dimensions"] = time_dims

    with path.open("w", encoding="utf-8") as f:
        y.dump(data, f)
    return path


def merge_relationships_yaml(base: Path, company: str, relationships: list[dict]) -> int:
    """`relationships.yml`e (company kökü, `wren.context.load_relationships` şeması —
    bkz. demo/companies/demo-boyahane/relationships.yml canlı örneği) YENİ ilişkileri
    ADDITIVE ekler: aynı `name` zaten varsa ATLANIR (üstüne yazılmaz — elle düzenlenmiş
    bir ilişkiyi bozmaz). Döner: kaç YENİ ilişki eklendi."""
    path = base / "companies" / company / "relationships.yml"
    metin = path.read_text(encoding="utf-8") if path.exists() else ""
    y = _yaml(metin)
    if metin:
        data = y.load(metin) or CommentedMap()
    else:
        data = CommentedMap()
    existing = data.get("relationships")
    if existing is None:
        existing = CommentedSeq()
        data["relationships"] = existing
    existing_names = {r.get("name") for r in existing if isinstance(r, dict)}
    added = 0
    for rel in relationships:
        if rel["name"] in existing_names:
            continue
        rm = CommentedMap()
        rm["name"] = rel["name"]
        rm["join_type"] = rel.get("join_type", "MANY_TO_ONE")
        models_seq = CommentedSeq(list(rel["models"]))
        models_seq.fa.set_flow_style()
        rm["models"] = models_seq
        rm["condition"] = rel["condition"]
        existing.append(rm)
        existing_names.add(rel["name"])
        added += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        y.dump(data, f)
    return added


def write_introspected_schema(base: Path, company: str, tables: list, draft: dict, *,
                              db_schema: str = "public") -> tuple[list[str], int]:
    """Onaylanmış taslağın (`draft`, kullanıcı `include`/sınıflandırma düzenlemesi geçmiş)
    TAMAMINI yazar: her `include=True` cube için model+cube YAML (yalnız henüz VAR
    OLMAYANLAR — çakışan bir isim SESSİZCE atlanır, `written_cubes` bunu yansıtır) +
    yalnız HER İKİ ucu da yazılan cube'larda olan ilişkiler. Döner: (yazılan cube adları,
    eklenen ilişki sayısı)."""
    tables_by_name = {t.name: t for t in tables}
    included = {c["name"] for c in draft.get("cubes") or [] if c.get("include", True)}
    written: list[str] = []
    for cube in draft.get("cubes") or []:
        name = cube["name"]
        if name not in included:
            continue
        table = tables_by_name.get(name)
        if table is None:
            continue  # taslak, artık introspect edilmemiş bir tablo adı taşıyor — atla
        cube_path = cube_yaml_path(base, company, name)
        model_path = base / "companies" / company / "models" / name / "metadata.yml"
        if cube_path.exists() or model_path.exists():
            continue  # var olan bir isimle çakışıyor — üstüne YAZILMAZ
        # 🔴 FAZ 3.6 — GÖRÜNMEZ KOLON. Kapatılan kolon **MDL'ye HİÇ YAZILMAZ**:
        # "gösterme" ile "yazma" arasındaki fark bu satırın bütün değeridir — gizlenen
        # ama yazılan bir kolon, bir prompt sızıntısında ya da Discovery sorgusunda
        # GERİ GELİR. `pii.py` maskeler (veri çıkışında), burası hiç ÜRETMEZ (şema
        # girişinde); iki farklı katman, biri ötekinin yerine geçmez.
        from app.coldstart import gorunur_kolonlar

        kolonlar = gorunur_kolonlar(table.columns, cube.get("gizli_kolonlar"))
        write_model_yaml(base, company, name, kolonlar, cube.get("primary_key"),
                         db_schema=db_schema)
        # ⚠ Cube tarafı da süzülür: gizli bir kolon ölçü/boyut listesinde kalırsa MDL
        # var olmayan bir kolona bakar ve `validate_project()` haklı olarak patlar.
        gizli = {str(x).strip().lower() for x in (cube.get("gizli_kolonlar") or [])}
        if gizli:
            cube = {**cube,
                    "measures": [m for m in (cube.get("measures") or [])
                                 if str(m).strip().lower() not in gizli],
                    "dimensions": [d for d in (cube.get("dimensions") or [])
                                   if str(d).strip().lower() not in gizli],
                    "time_dimensions": [t for t in (cube.get("time_dimensions") or [])
                                        if str(t).strip().lower() not in gizli]}
        write_cube_yaml(base, company, cube)
        written.append(name)
    rels = [r for r in (draft.get("relationships") or [])
            if set(r["models"]) <= included]
    added = merge_relationships_yaml(base, company, rels) if rels else 0
    return written, added
