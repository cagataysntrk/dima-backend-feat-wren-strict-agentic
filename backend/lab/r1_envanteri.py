"""FAZ 3.2 — **R1 ENVANTERİ.** *"Katalogda VAR OLAN bir ölçü sinonimi, düz sorulduğunda
cube'unu bile tanıtmıyor."*

## Neden bu araç var

470 sinonimlik sondada **`R1: 99`** ölçüldü ve §6.1h *"R1'in TAMAMI gerçek ölçü-düzeyi
belirsizliğidir"* dedi. Bu, bu depodaki **ölçülmüş tek en büyük kaldıraç** — ve hiç
çalışılmamıştı. Ama bir sayı, **hangi terimler** olduğu bilinmeden kapatılamaz.

## 🔴 BU ARAÇ KARAR VERMEZ, RAPOR ÜRETİR

FAZ 3.1'in dersi taze: kararları **araç** verirse, bir tenant'ın alan bilgisi bütün
tenant'lara dayatılır ve korpus geriler (%93,2 → %92,6, ölçüldü). Burada üretilen şey bir
**iş listesidir**: terim · cube adayları · kanıt. Kararı **insan** verir ve o karar
`sahiplenilen_terimler`'e **tenant kapsamlı** girer (FAZ 3.1b).

*Bir envanter aracının kendi kararını vermesi, envanteri bir dayatmaya çevirir.*

## Kullanım

    python lab/r1_envanteri.py                    # dört şirket
    python lab/r1_envanteri.py --sirket gitas
    python lab/r1_envanteri.py --kapi             # R1 ≤ HEDEF mi? (çıkış kodu)
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SIRKETLER = ("demo-boyahane", "gitas", "atiksan", "gulteks")

#: 🔴 Yol haritasının hedefi: **99 → ≤30**. Kalanlar *gerçek* belirsizliktir ve **chip'e**
#: gider — sıfır hedefi koymak, gerçek belirsizliği tahminle kapatmayı zorlardı.
HEDEF = 30


def _sema(sirket: str):
    from app.compose import build, compose
    from app.wren_service import WrenService

    td = tempfile.mkdtemp(prefix=f"r1-{sirket}-")
    out = Path(td) / "proje"
    compose(sirket, Path(__file__).resolve().parents[1] / "demo", out)
    build(out)
    return WrenService(out, datasource="duckdb", connection_info={}).schema()


def sondalar(sema: dict) -> list[tuple[str, str, str]]:
    """`(sinonim, cube, ölçü)` — katalogdaki **her** ölçü sinonimi bir sondadır.

    ⚠ Cube-düzeyi sinonimler **dahil edilmez**: onlar bir ölçü **iddia etmez**, yalnız
    konu belirtir. R1 tanımı gereği *"ölçü sinonimi cube'unu tanıtmıyor"* der.
    """
    out: list[tuple[str, str, str]] = []
    for c in sema.get("cubes") or []:
        for olcu, syns in (c.get("measure_synonyms") or {}).items():
            for s in syns or []:
                s = str(s).removesuffix("!").strip()
                if s:
                    out.append((s, str(c.get("name")), str(olcu)))
    return out


def envanter(sema: dict) -> dict:
    """Her sinonimi `route()`'a sok, `R1` dönenleri **kanıtıyla** topla."""
    from app import cube_router as cr

    r1: list[dict] = []
    kodlar: Counter[str] = Counter()
    for sinonim, cube, olcu in sondalar(sema):
        q = cr._norm(sinonim)
        sonuc = cr.route(q, sema)
        # 🔴 `red_gerekcesi()` DEĞİL `teshis()` (KÖK-9/KÇ-5, 2026-08-06). Ölçüldü:
        # 2 116 reddin %43,2'sinde ham kapı kodu ile gerçek sorun ayrışıyordu ve
        # ayrışanların **646'sı R1'di** — yani bu aracın envanteri, tam da saymak için
        # var olduğu kümeyi şişiriyordu. *Bir envanter, saydığı şeyin tanımını başka bir
        # yerden alıyorsa, saydığı şey o değildir.*
        kod = cr.teshis(sinonim, sema)
        if sonuc is not None:
            kodlar["cozuldu"] += 1
            continue
        kodlar[kod or "kodsuz"] += 1
        if kod != "R1":
            continue
        # 🔴 KANIT: hangi cube'lar bu terimi iddia ediyor? Karar bunsuz verilemez.
        adaylar = sorted({
            str(c.get("name")) for c in (sema.get("cubes") or [])
            for _o, ss in (c.get("measure_synonyms") or {}).items()
            if any(str(x).removesuffix("!").strip() == sinonim for x in ss or [])
        })
        r1.append({
            "terim": sinonim,
            "kaynak_cube": cube,
            "kaynak_olcu": olcu,
            "adaylar": adaylar,
            # Kanıt uzunluğu: tek kelimelik terimler en kırılgan olanlardır.
            "kelime": len(sinonim.split()),
            "kutu": "tek_sahip" if len(adaylar) == 1 else "belirsiz",
        })
    return {"toplam_sonda": len(sondalar(sema)), "r1": r1, "kodlar": dict(kodlar)}


def main() -> int:
    ap = argparse.ArgumentParser(description="R1 envanteri — RAPOR, karar değil")
    ap.add_argument("--sirket", nargs="*", default=list(SIRKETLER))
    ap.add_argument("--kapi", action="store_true", help=f"R1 ≤ {HEDEF} mi?")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    hepsi: dict[str, dict] = {}
    for s in a.sirket:
        try:
            hepsi[s] = envanter(_sema(s))
        except Exception as exc:                             # noqa: BLE001
            # ⊘ ÖLÇÜLEMEDİ — yeşile yuvarlamak "risk yok" YALANI üretirdi.
            print(f"  {s}: ⊘ ÖLÇÜLEMEDİ — {exc}")
            hepsi[s] = {"hata": str(exc), "r1": [], "toplam_sonda": 0}

    if a.json:
        print(json.dumps(hepsi, ensure_ascii=False, indent=2))
        return 0

    toplam_r1 = 0
    for s, d in hepsi.items():
        r1 = d.get("r1") or []
        toplam_r1 += len(r1)
        tek = [x for x in r1 if x["kutu"] == "tek_sahip"]
        print(f"\n══ {s}: {d.get('toplam_sonda', 0)} sonda · R1 = {len(r1)} "
              f"({len(tek)} TEK SAHİP — kapatılabilir · {len(r1) - len(tek)} belirsiz → chip)")
        for x in r1[:12]:
            isaret = "→" if x["kutu"] == "tek_sahip" else "?"
            print(f"   {isaret} {x['terim']:<28} {x['adaylar']}")
        if len(r1) > 12:
            print(f"   … +{len(r1) - 12} tane daha (`--json` ile tamamı)")

    print(f"\nTOPLAM R1: {toplam_r1}  (hedef ≤ {HEDEF} · yol haritası tabanı 99)")
    print("🔴 Bu bir RAPORDUR: kararı insan verir ve karar TENANT kapsamlı girer (3.1b).")
    if a.kapi:
        if toplam_r1 > HEDEF:
            print(f"✗ KAPI: R1 {toplam_r1} > {HEDEF}")
            return 1
        print(f"✓ KAPI: R1 {toplam_r1} ≤ {HEDEF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
