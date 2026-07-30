"""Pack mimari değişmez testleri (ADR-0017 faset disiplini — MEKANİK kapı).

"kaynak cube'u sektörden bağımsız olmalı" kuralını insan/AI dikkatine değil teste
bağlar (kumas cube'unun kaynak katmanına sızması bu kapı olmadığı için yakalanmadı).
Yeni kaynak pack'i eklendiğinde bu testler ihlali derleme-zamanı yakalar.
"""

from __future__ import annotations

from pathlib import Path

import yaml

PACKS = Path(__file__).resolve().parents[1] / "demo" / "packs"

# Sektör-özgü terimler: kaynak katmanı (ERP-fiziksel, sektörden BAĞIMSIZ) bunları
# cube adında/sinonimde İÇEREMEZ. Bu terimler sektör pack'lerine aittir.
_SEKTOR_TERIMLERI = {
    "kumas", "kumaş", "boya", "boyahane", "parti", "recete", "reçete", "fire",
    "oee", "vardiya", "hurda", "atik", "atık", "geri donusum", "geri dönüşüm",
    "soya", "misir", "mısır", "bugday", "buğday", "emtia", "yem", "kuspe", "küspe",
    "metre", "top",  # tekstil birimleri
}


def _cube_files(layer: str):
    root = PACKS / layer
    if not root.is_dir():
        return
    for pack in sorted(root.iterdir()):
        for meta in sorted((pack / "cubes").glob("*/metadata.yml")) if (pack / "cubes").is_dir() else []:
            yield pack.name, meta


def test_kaynak_cubelari_sektorden_bagimsiz():
    """Kaynak cube adı ve cube-düzeyi sinonimleri sektör terimi İÇEREMEZ."""
    ihlaller = []
    for pack, meta in _cube_files("kaynak"):
        doc = yaml.safe_load(meta.read_text()) or {}
        name = str(doc.get("name") or "")
        syns = [str(s).lower().rstrip("!") for s in (doc.get("synonyms") or [])]
        tokens = {name.lower()} | set(syns)
        # çok-kelimeli sinonimlerin kelimelerini de kontrol et
        for s in syns:
            tokens.update(s.split())
        hit = tokens & _SEKTOR_TERIMLERI
        if hit:
            ihlaller.append(f"{pack}/{meta.parent.name}: sektör terimi {sorted(hit)}")
    assert not ihlaller, (
        "Kaynak cube'una sektör terimi sızmış (ADR-0017: kaynak=fiziksel, "
        "sektör=terminoloji). Terimi sektör pack'ine taşı:\n" + "\n".join(ihlaller))


def test_cube_metadata_yapisal_gecerli():
    """Her cube: name + base_object + en az 1 measure; measure expression'ı boş değil."""
    hatalar = []
    for layer in ("kaynak", "modul", "sektor"):
        for pack, meta in _cube_files(layer):
            doc = yaml.safe_load(meta.read_text()) or {}
            loc = f"{layer}/{pack}/{meta.parent.name}"
            if not doc.get("name"):
                hatalar.append(f"{loc}: name yok")
            if not doc.get("base_object"):
                hatalar.append(f"{loc}: base_object yok")
            ms = doc.get("measures") or []
            if not ms:
                hatalar.append(f"{loc}: measure yok")
            for m in ms:
                if not m.get("name") or not str(m.get("expression") or "").strip():
                    hatalar.append(f"{loc}: measure name/expression eksik ({m.get('name')})")
                # additive yalnız bilinen değerler
                if m.get("additive") and str(m["additive"]).lower() not in ("full", "semi", "non"):
                    hatalar.append(f"{loc}.{m.get('name')}: geçersiz additive '{m['additive']}'")
    assert not hatalar, "Cube metadata yapısal hatası:\n" + "\n".join(hatalar)
