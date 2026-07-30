"""Pack keşfi (ADR-0005): demo/packs altındaki sektör/modül paketlerini listeler.

Sektör↔cube eşleşmesinin KAYNAĞI pack dosyalarıdır; admin panel bu listeden
SEÇİM yapar ve önizleme gösterir ("bu sektörü seçersen şu cube'lar gelir") —
eşleşmeyi tanımlamaz. Yeni sektör = yeni pack dizini, kod/panel değişikliği yok.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def _load_yaml(p: Path) -> dict:
    try:
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _cubes_of(pack_dir: Path) -> list[dict]:
    out = []
    cubes_dir = pack_dir / "cubes"
    if not cubes_dir.is_dir():
        return out
    for d in sorted(cubes_dir.iterdir()):
        meta = _load_yaml(d / "metadata.yml")
        if meta.get("name"):
            out.append({
                "name": meta["name"],
                "label": str(meta.get("label") or meta["name"]),
                "measures": len(meta.get("measures") or []),
            })
    return out


def list_packs(base: Path) -> dict:
    """{"sektorler": [...], "moduller": [...]} — her giriş: key + cube önizlemesi."""
    base = Path(base)
    sektorler = []
    for d in sorted((base / "packs" / "sektor").iterdir()) if (base / "packs" / "sektor").is_dir() else []:
        if not d.is_dir():
            continue
        pack = _load_yaml(d / "pack.yml")
        sektorler.append({
            "key": d.name,
            "moduller": pack.get("moduller") or [],   # varsayılan konu modülleri
            "features": pack.get("features") or {},
            "cubes": _cubes_of(d),
        })
    moduller = []
    for d in sorted((base / "packs" / "modul").iterdir()) if (base / "packs" / "modul").is_dir() else []:
        if d.is_dir():
            moduller.append({"key": d.name, "cubes": _cubes_of(d)})
    # Kaynak pack'leri (ADR-0017): fiziksel şema katmanı. "onekli" = gereksinim
    # şablonu {firma}/{donem} yer tutucusu taşıyor (Logo) — panel kapsam sorar.
    kaynaklar = []
    kaynak_base = base / "packs" / "kaynak"
    for d in sorted(kaynak_base.iterdir()) if kaynak_base.is_dir() else []:
        if not d.is_dir():
            continue
        pack = _load_yaml(d / "pack.yml")
        try:
            gereksinim = (d / "gereksinim.yml").read_text()
        except OSError:
            gereksinim = ""
        kaynaklar.append({
            "key": d.name,
            "datasource": pack.get("datasource") or "",
            "onekli": "{firma}" in gereksinim,
            "fingerprint": pack.get("fingerprint") or {},
            "cubes": _cubes_of(d),
        })
    return {"sektorler": sektorler, "moduller": moduller, "kaynaklar": kaynaklar}
