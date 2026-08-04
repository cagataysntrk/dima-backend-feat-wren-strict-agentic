"""FAZ 2.1 — **GÖLGE DERLEME DIFF'İ.** Çekirdek katman MDL'i değiştirdi mi?

## Neden bu araç var

Göç reçetesinin ikinci adımı: *"`compose()` iki çıktı üretir, **MDL'ler diff'lenir**"*.
Bir semantik katman göçünün tek anlamlı kabul ölçütü, **hiçbir sayının değişmemesidir** —
ve bunu *"testler yeşil"* diye ölçmek yetmez: testler **bildikleri** vakaları doğrular,
MDL'de sessizce kayan bir ifadeyi değil.

## 🔴 KARŞILAŞTIRMA BİRİMİ: cube × ölçü × boyut × İFADE

Dosya diff'i **işe yaramaz**: `yaml.safe_dump` anahtar sırasını, girintiyi ve tırnak
biçimini değiştirir; iki anlamca özdeş dosya **binlerce satır fark** verir. Karşılaştırma
**anlam düzeyinde** olmak zorunda.

⚠ Ve tersi de doğru: *sıra değişikliğini fark saymamak*, gerçek bir ifade değişikliğini
gizleyebilir — o yüzden ifade **birebir** karşılaştırılır, yalnız **konumu** yok sayılır.

## Kullanım

    python lab/mdl_diff.py                 # off ↔ on: çekirdek katmanın MDL etkisi
    python lab/mdl_diff.py --sirket gitas
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SIRKETLER = ("demo-boyahane", "gitas", "atiksan", "gulteks")


def _imza(proje: Path) -> dict[str, str]:
    """MDL → `{"cube.ölçü": ifade}` · `{"cube.boyut": ifade}` — **anlam düzeyi imza**.

    Anahtar `cube.tür.ad`, değer ifadenin **kendisi**. Sıra ve biçim düşer, anlam kalır.
    """
    import yaml

    out: dict[str, str] = {}
    for meta_path in sorted((proje / "cubes").glob("*/metadata.yml")):
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        cube = str(meta.get("name") or meta_path.parent.name)
        out[f"{cube}.__base_object__"] = str(meta.get("base_object") or "")
        out[f"{cube}.__always_filter__"] = str(meta.get("always_filter") or "")
        for tur in ("measures", "dimensions"):
            for x in meta.get(tur) or []:
                ad = str(x.get("name") or "")
                # 🔴 İFADE + TİP birlikte: aynı ifadenin tipi değişirse sayı da değişir
                # (INTEGER ↔ DOUBLE bölmede sessizce farklı sonuç verir).
                # 🔴 `additive` DE SAYI KOVASINDA — ve bu bir DÜZELTME. İlk sürüm onu
                # "sözlük" saymıştı; oysa `additive: semi` motorun toplama semantiğini
                # değiştirir (dönem boyunca TOPLAMA, dönem SONU al). Yani sinonimle aynı
                # kovaya konmuş bir SAYI özelliğiydi ve bir gün bir cube `additive`
                # beyan etmeyi unutsaydı, çekirdek onu doldurur ve araç bunu ZARARSIZ
                # bir sözlük değişikliği diye raporlardı.
                # *Ölçüm aracının kendisi de bir bağımlılıktır* (MIMARI §6.4).
                out[f"{cube}.{tur[:-1]}.{ad}"] = (
                    f"{x.get('expression') or ''}|{x.get('type') or ''}"
                    f"|{x.get('additive') or ''}")
                # Sinonim/birim ANLAMI taşır ama SAYIYI değiştirmez → ayrı anahtar,
                # ayrı rapor: bir göçün "sayı değişmedi ama sözlük büyüdü" olması
                # BEKLENEN sonuçtur; ikisini aynı kovaya koymak onu gizlerdi.
                # ⚠ `unit` burada KALIYOR: birim GÖSTERİMİ değiştirir, sayıyı değil.
                out[f"~{cube}.{tur[:-1]}.{ad}.sozluk"] = json.dumps(
                    {"synonyms": sorted(x.get("synonyms") or []),
                     "unit": x.get("unit")},
                    ensure_ascii=False, sort_keys=True)
    return out


def _derle(sirket: str, kademe: str) -> dict[str, str]:
    """Bir şirketi verilen kademede derler ve imzasını döner. Çıktı **geçici dizine**."""
    os.environ["DIMA_CEKIRDEK_KATMAN"] = kademe
    from app.config import get_settings

    get_settings.cache_clear()               # type: ignore[attr-defined]
    from app.compose import compose

    base = Path(__file__).resolve().parents[1] / "demo"
    with tempfile.TemporaryDirectory(prefix=f"mdldiff-{sirket}-") as td:
        out = Path(td) / "proje"
        compose(sirket, base, out)
        return _imza(out)


def diff(sirket: str) -> tuple[dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    """`(sayi_farklari, sozluk_farklari)` — **ikisi ayrı**, çünkü anlamları ayrı.

    🔴 `sayi_farklari` **boş olmalı**: çekirdek katman ifadeye dokunmaz (adım a).
    `sozluk_farklari` **dolu olabilir** ve bu bir başarıdır — sinonimler birleşti demektir.
    """
    once, sonra = _derle(sirket, "off"), _derle(sirket, "on")
    sayi: dict[str, tuple[str, str]] = {}
    sozluk: dict[str, tuple[str, str]] = {}
    for k in sorted(set(once) | set(sonra)):
        a, b = once.get(k, "‹YOK›"), sonra.get(k, "‹YOK›")
        if a == b:
            continue
        (sozluk if k.startswith("~") else sayi)[k] = (a, b)
    return sayi, sozluk


def main() -> int:
    ap = argparse.ArgumentParser(description="Çekirdek katmanın MDL etkisi (off ↔ on)")
    ap.add_argument("--sirket", nargs="*", default=list(SIRKETLER))
    a = ap.parse_args()

    kirmizi = 0
    for s in a.sirket:
        try:
            sayi, sozluk = diff(s)
        except Exception as exc:             # noqa: BLE001
            # 🔴 GRAIN İHLALİ ≠ ÖLÇÜM HATASI. Sözleşmenin **ateşlemesi** beklenen bir
            # sonuçtur (ad göçü inene kadar `on` açılamaz) ve onu *"ölçülemedi"* diye
            # raporlamak, çalışan bir kapıyı bir arıza gibi göstermek olurdu.
            if type(exc).__name__ == "GrainIhlali":
                print(f"  {s}: ⛔ SÖZLEŞME ATEŞLEDİ (beklenen) — `on` açılamaz:")
                for satir in str(exc).splitlines()[1:4]:
                    print(f"      {satir.strip()}")
                continue
            print(f"  {s}: ⊘ ÖLÇÜLEMEDİ — {exc}")
            kirmizi += 1                     # ölçülemeyeni yeşil saymak YALAN üretir
            continue
        durum = "✅" if not sayi else "🔴"
        print(f"  {s}: {durum} sayı-etkisi {len(sayi)} fark · sözlük {len(sozluk)} fark")
        for k, (x, y) in list(sayi.items())[:10]:
            print(f"      🔴 {k}: {x!r} → {y!r}")
        kirmizi += 1 if sayi else 0
    print("\n" + ("🔴 SAYIYI ETKİLEYEN FARK VAR" if kirmizi else
                  "✅ GÖLGE DIFF TEMİZ — çekirdek katman hiçbir sayıyı değiştirmiyor"))
    return 1 if kirmizi else 0


if __name__ == "__main__":
    raise SystemExit(main())
