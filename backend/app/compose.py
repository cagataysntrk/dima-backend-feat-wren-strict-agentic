"""Paket kompozisyonu (ADR-0005 + ADR-0017): faset katmanları → wren-project.

Katman sırası (son yazan kazanır — en spesifik en son):
    packs/kaynak/<k>/  →  packs/modul/<m>/  →  packs/sektor/<s>/
      →  packs/kaynak/<k>/sektor/<s>/ (kesişim)  →  companies/<şirket>/

Kaynak pack'i (ADR-0017) fiziksel şema katmanıdır (modeller + jenerik cube'lar);
`sektor/` alt-dizini kesişim içeriğidir ve kaynak katmanı kopyalanırken atlanır —
yalnız şirketin seçtiği sektörlerle eşleşenler ayrı kesişim katmanı olarak biner.

Kaynaklar git'te yaşar; `wren-project/` DERLENMİŞ çıktıdır (gitignore). Başlangıçta
otomatik compose + `wren` build çalışır — yeni dikey = yeni YAML, kod değişikliği yok.

Kullanım: uygulama başlangıcı (main.lifespan) ya da elle:
    .venv/bin/python -m app.compose            # settings.company için
    .venv/bin/python -m app.compose <şirket>
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml


def compose(company: str, base: Path, out: Path) -> dict:
    """Katmanları out'a kopyalar. Döner: {layers: [...], files: N}.

    Sektör alanı iki biçimde gelebilir: ``sektor: x`` (tekil, geriye-uyum) ya da
    ``sektorler: [x, y]`` (çoklu — LİSTEDE ÖNCE gelen kazanır; aynı adlı cube
    çakışmasında ilk sıradaki sektörün içeriği geçerli olur)."""
    base = Path(base)
    out = Path(out)
    company_dir = base / "companies" / company
    cfg = yaml.safe_load((company_dir / "company.yml").read_text()) or {}
    sektorler = cfg.get("sektorler") or ([cfg["sektor"]] if cfg.get("sektor") else [])
    sektor_dirs = [base / "packs" / "sektor" / str(s) for s in sektorler]

    moduller = cfg.get("moduller")
    if moduller is None:
        # Varsayılan modüller: tüm seçili sektör paketlerinin birleşimi (sıra korunur).
        seen: list[str] = []
        for d in sektor_dirs:
            pack_cfg = yaml.safe_load((d / "pack.yml").read_text()) or {}
            for m in pack_cfg.get("moduller") or []:
                if m not in seen:
                    seen.append(m)
        moduller = seen
    moduller = moduller or []

    kaynaklar = [str(k) for k in cfg.get("kaynaklar") or []]
    kaynak_dirs = [base / "packs" / "kaynak" / k for k in kaynaklar]

    # Kopyalama sırası = öncelik sırası (SON yazan kazanır): kaynak → modüller →
    # sektörler → kesişim → şirket. Listelerde önce gelen EN SON kopyalanır ki kazansın.
    # (layer, exclude) çifti: kaynak katmanının sektor/ alt-dizini kesişim içeriğidir,
    # ana kopyada atlanır.
    layers: list[tuple[Path, str | None]] = [(d, "sektor") for d in reversed(kaynak_dirs)]
    layers.extend((base / "packs" / "modul" / m, None) for m in moduller)
    layers.extend((d, None) for d in reversed(sektor_dirs))
    for layer, _ in layers + [(company_dir, None)]:
        if not layer.is_dir():
            raise FileNotFoundError(f"Kompozisyon katmanı yok: {layer}")
    # Kesişim katmanları (ADR-0017): yalnız var olan kaynak×sektör çiftleri biner —
    # matris seyrektir, eksik kesişim hata değildir.
    for k in reversed(kaynak_dirs):
        for s in [d.name for d in reversed(sektor_dirs)]:
            kesisim = k / "sektor" / s
            if kesisim.is_dir():
                layers.append((kesisim, None))
    layers.append((company_dir, None))

    # Çıktıyı sıfırla (derlenmiş artefakt — kaynak değil). rmtree macOS'ta geçici olarak
    # "Directory not empty" verebiliyor (FS gecikmesi/izleyici) — birkaç kez dene, sonra
    # son çare ignore_errors (registry per-slug kilidi eş-zamanlı yazımı zaten engeller).
    if out.exists():
        import time as _t

        for _ in range(3):
            try:
                shutil.rmtree(out)
                break
            except OSError:
                _t.sleep(0.1)
        shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)

    skip = {"company.yml", "pack.yml", "schedules.yaml", "gereksinim.yml",
            "cube_synonyms.yml", "turev.yml"}
    count = 0
    for layer, exclude in layers:
        for f in sorted(layer.rglob("*")):
            if not f.is_file() or f.name in skip:
                continue
            rel = f.relative_to(layer)
            if rel.parts[0] == "verified":
                continue  # öğrenilen VQR verisi şirkette KALIR (çalışma verisi, içerik değil)
            if exclude is not None and rel.parts[0] == exclude:
                continue
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            count += 1
    # SEKTÖR-SİNONİM ENJEKSİYONU (ADR-0017 faset disiplini): sektör/kesişim pack'i
    # generic KAYNAK cube'una terminoloji EKLER (kumaş→mal, hurda→ticaret) — kaynak
    # cube sektörden bağımsız kalır (pack-lint zorlar), sektör kelimesi burada birleşir.
    # additive: base sinonimi silmez. Katman sırasıyla uygulanır (şirket en son).
    _merge_cube_synonyms(layers, out)
    # JENERİK TÜREV METRİKLER: DB-bağımsız kâr/marj/SMM/... tanımlarını (packs/modul/turev/)
    # her ERP'nin turev.yml binding'lerinden view+cube olarak ÜRETİR (logo/mikro/netsis
    # bedavaya; yeni ERP sadece binding verir).
    _compose_derived_metrics(base, out, kaynaklar)
    # KPI-KOMPOZİSYON: cross-cube türev KPI'lar (packs/modul/kpi/*.yml). Bileşenleri
    # birden çok türev-view'dan çeker (CCC = cari_finans_src ⊕ karlilik_src). Yalnız
    # gerekli view'ların TAMAMI üretildiyse derlenir (dürüst gate — eksikse KPI yok).
    _compose_kpis(base, out)
    return {"layers": [str(l.relative_to(base)) for l, _ in layers], "files": count}


def _compose_kpis(base: Path, out: Path) -> None:
    """Cross-cube KPI tanımlarını (packs/modul/kpi/*.yml) out/kpis/ altına yalnız tüm
    requires_views üretilmişse kopyalar. KPI DB-bağımsızdır (kanonik view kolonları);
    bileşen SQL'i ERP-özel değildir → hiçbir binding gerekmez, view varsa çalışır."""
    kpi_dir = base / "packs" / "modul" / "kpi"
    if not kpi_dir.is_dir():
        return
    for kfile in sorted(kpi_dir.glob("*.yml")):
        spec = yaml.safe_load(kfile.read_text()) or {}
        need = spec.get("requires_views") or []
        if not all((out / "views" / v / "metadata.yml").is_file() for v in need):
            continue  # bu şirkette gerekli türev-view(lar) yok → KPI atlanır (dürüst)
        dst = out / "kpis" / f"{spec['name']}.yml"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False))


def _compose_derived_metrics(base: Path, out: Path, kaynaklar: list[str]) -> None:
    """Jenerik türev-metrikleri (packs/modul/turev/*.yml) her ERP'nin turev.yml
    binding'lerinden view+cube üretir. Metrik DB-bağımsız (kanonik kolonlar); binding
    ERP-özel (fiziksel kolon/kod eşlemesi). İlk sağlayan kaynak kazanır (tekil ERP varsayımı)."""
    metric_dir = base / "packs" / "modul" / "turev"
    if not metric_dir.is_dir():
        return
    bindings_by_kaynak: dict[str, dict] = {}
    for k in kaynaklar:
        bpath = base / "packs" / "kaynak" / k / "turev.yml"
        if bpath.is_file():
            bindings_by_kaynak[k] = yaml.safe_load(bpath.read_text()) or {}
    for mfile in sorted(metric_dir.glob("*.yml")):
        spec = yaml.safe_load(mfile.read_text()) or {}
        name, req = spec.get("name"), (spec.get("requires") or [])
        binding = None
        for k in kaynaklar:  # metriği TAM bağlayan ilk kaynak
            b = (bindings_by_kaynak.get(k) or {}).get(name)
            if b and all(r in b for r in req):
                binding = b
                break
        if binding is None:
            continue  # bu şirketin ERP'si metriği bağlamıyor → metrik atlanır (dürüst)
        # Opsiyonel placeholder default'ları (binding'de yoksa): row_filter = iptal/geçerlilik
        # yüklemi (netsis/mikro: yok → "1=1"; logo: "CANCELLED = 0").
        render = {"row_filter": "1=1", **binding}
        vname = spec["view_name"]
        vdir = out / "views" / vname
        vdir.mkdir(parents=True, exist_ok=True)
        (vdir / "metadata.yml").write_text(yaml.safe_dump(
            {"name": vname, "statement": spec["view_statement"].format(**render),
             "columns": spec["view_columns"]}, allow_unicode=True, sort_keys=False))
        cube = spec["cube"]
        cdir = out / "cubes" / cube["name"]
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "metadata.yml").write_text(
            yaml.safe_dump(cube, allow_unicode=True, sort_keys=False))


def _merge_cube_synonyms(layers: list[tuple[Path, str | None]], out: Path) -> None:
    """Her katmandaki cube_synonyms.yml'i derlenmiş cube metadata'sına additive işler.

    Biçim (cube adı → ekler):
        mal:
          synonyms: [kumaş, metre, top]       # cube-düzeyi
          measures: {satis_miktari: [kaç metre]}
          dimensions: {stok_kodu: [hangi kumaş]}
    """
    def _add(dst_list_owner: dict, key: str, extra: list) -> None:
        cur = dst_list_owner.get(key) or []
        for s in extra:
            if s not in cur:
                cur.append(s)
        dst_list_owner[key] = cur

    for layer, _ in layers:
        spec_path = layer / "cube_synonyms.yml"
        if not spec_path.is_file():
            continue
        spec = yaml.safe_load(spec_path.read_text()) or {}
        for cube_name, adds in spec.items():
            meta_path = out / "cubes" / cube_name / "metadata.yml"
            if not meta_path.is_file():
                continue  # bu şirkette o cube yok → atla (seyrek matris)
            meta = yaml.safe_load(meta_path.read_text()) or {}
            if adds.get("synonyms"):
                _add(meta, "synonyms", adds["synonyms"])
            for mname, syns in (adds.get("measures") or {}).items():
                for m in meta.get("measures", []):
                    if m.get("name") == mname:
                        _add(m, "synonyms", syns)
            for dname, syns in (adds.get("dimensions") or {}).items():
                for d in meta.get("dimensions", []):
                    if d.get("name") == dname:
                        _add(d, "synonyms", syns)
            meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False))


def build(project_dir: Path) -> Path:
    """Derlenmiş projeden target/mdl.json üretir (wren build, in-process)."""
    from wren.context import build_json, save_target

    manifest = build_json(Path(project_dir))
    return save_target(manifest, Path(project_dir))


def compose_and_build(settings) -> dict:
    base = Path(settings.demo_root) if getattr(settings, "demo_root", "") else None
    if base is None or not str(base):
        base = settings.resolved_project_dir().parent  # .../demo
    info = compose(settings.company, base, settings.resolved_project_dir())
    build(settings.resolved_project_dir())
    return info


if __name__ == "__main__":
    import sys

    from app.config import get_settings

    s = get_settings()
    if len(sys.argv) > 1:
        object.__setattr__(s, "company", sys.argv[1])
    info = compose_and_build(s)
    print(f"compose: {' ⊕ '.join(info['layers'])} → {s.resolved_project_dir()} ({info['files']} dosya) + mdl.json")
