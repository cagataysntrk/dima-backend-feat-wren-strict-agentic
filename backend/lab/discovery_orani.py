"""FAZ O-9 — **DISCOVERY ORANI** ve A/B. *"Her Discovery ateşlemesi bir arıza raporudur."*

## Neden bir oran, neden bir sayaç değil

`MIMARI`'nin en üst kuralı Discovery'yi bir **yol** değil bir **ölçü** yapıyor: hangi
yemeği yapamadığımızı söyler. Ama bir sayaç *"kaç kez ateşlendi"* der ve **paydayı**
saklar — 3/10 ile 3/100 aynı sayıyı verir. Oran paydayı görünür tutar.

🔴 Ve payda **kutsaldır**: iki koşum farklı soru kümesiyle karşılaştırılamaz. Bu alet
A/B'de paydaları eşitleyemezse **karşılaştırmayı reddeder** — çünkü *"sistem bozulurken
sayı iyileşir"* deseni tam olarak paydanın sessizce değişmesiyle doğar (ölçüldü: `gitas`
korpustan düştü, payda 445→342, doğruluk **YÜKSELDİ**).

## Ne sayıyor

`/ask` yanıtının `source` alanı merdivenin **hangi basamağının** cevapladığını söyler:

| `source` | basamak | okuma |
|---|---|---|
| `cube` | 🍳 route — sıfır LLM | ✅ en ucuz, en güvenilir |
| `cube+llm` | 🗣 garson çevirdi, sayıyı küp koydu | ✅ hedeflenen yol |
| `llm:*` | 🥡 **Discovery** — ham SQL | 🔴 **arıza raporu** |
| `None` | cevap yok | 🔴 arıza raporu (sessiz olanı) |

⚠ `cube=adhoc` da bir arıza raporudur (`source` `cube` görünse bile veri incelenmemiş
LLM SQL'inden türemiştir) — ayrı sayılır, çünkü rozeti dürüst değildir.

## Kullanım

    # curl turu her cevabı bir JSONL satırına yazar (bir soru = bir satır)
    python lab/discovery_orani.py tur-ee.jsonl
    python lab/discovery_orani.py --ab kapali.jsonl acik.jsonl

⚠ Bu alet **istek atmaz**. Senaryolar `curl` ile tek tek koşulur (döngü kuralı); alet
yalnız o koşumun çıktısını okur. *Ölçen ile ölçülenin aynı süreç olması, ikisinin de
aynı arızaya düşmesi demektir.*
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SINIF_CUBE = "cube"
SINIF_GARSON = "cube+llm"
SINIF_DISCOVERY = "discovery"
SINIF_ADHOC = "adhoc"
SINIF_CEVAPSIZ = "cevapsiz"

SIRA = (SINIF_CUBE, SINIF_GARSON, SINIF_DISCOVERY, SINIF_ADHOC, SINIF_CEVAPSIZ)

ETIKET = {
    SINIF_CUBE: "🍳 cube (0 LLM)",
    SINIF_GARSON: "🗣 cube+llm (garson)",
    SINIF_DISCOVERY: "🥡 DISCOVERY",
    SINIF_ADHOC: "🥡 adhoc cube",
    SINIF_CEVAPSIZ: "🔴 cevapsız",
}

#: 🔴 Arıza raporu sayılan sınıflar. `adhoc` buradadır: rozeti `cube` görünse de veri
#: **incelenmemiş** LLM SQL'inden türemiştir — `MIMARI §6.2z`'nin dürüstlük kuralı.
ARIZA = (SINIF_DISCOVERY, SINIF_ADHOC, SINIF_CEVAPSIZ)


def sinifla(cevap: dict) -> str:
    """Bir `/ask` yanıtını merdiven basamağına eşler.

    ⚠ Sıra önemli: `adhoc` kontrolü `cube` kontrolünden **önce** gelir, yoksa ad-hoc bir
    cevap `cube` sayılır ve arıza raporu görünmez olur.
    """
    src = cevap.get("source")
    cube = ((cevap.get("cube_query") or {}).get("cube") or "")
    if cube == "adhoc":
        return SINIF_ADHOC
    if not src:
        return SINIF_CEVAPSIZ
    if str(src).startswith("llm"):
        return SINIF_DISCOVERY
    if src == SINIF_GARSON:
        return SINIF_GARSON
    return SINIF_CUBE


def oku(yol: Path) -> list[dict]:
    """JSONL — her satır bir `/ask` yanıtı. ⚠ Bozuk satır **atlanmaz, sayılır**:
    sessizce düşen bir satır paydayı gizlice küçültür (`ADR-0020`)."""
    out: list[dict] = []
    for i, s in enumerate(yol.read_text(encoding="utf-8").splitlines(), 1):
        s = s.strip()
        if not s:
            continue
        try:
            out.append(json.loads(s))
        except Exception:
            out.append({"source": None, "_bozuk": i})
    return out


def dagilim(cevaplar: list[dict]) -> dict[str, int]:
    d = {k: 0 for k in SIRA}
    for c in cevaplar:
        d[sinifla(c)] += 1
    return d


def oran(d: dict[str, int]) -> float:
    n = sum(d.values())
    return (sum(d[k] for k in ARIZA) / n * 100.0) if n else 0.0


def _yazdir(ad: str, d: dict[str, int]) -> None:
    n = sum(d.values())
    print(f"\n{ad}  (payda {n})")
    for k in SIRA:
        if d[k]:
            print(f"  {ETIKET[k]:<24} {d[k]:>3}  ({d[k] / n * 100:5.1f}%)")
    print(f"  {'ARIZA ORANI':<24} {sum(d[k] for k in ARIZA):>3}  ({oran(d):5.1f}%)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Discovery oranı ve A/B (FAZ O-9 / G6)")
    ap.add_argument("dosya", type=Path)
    ap.add_argument("--ab", type=Path, help="ikinci koşum (A/B)")
    a = ap.parse_args()

    A = dagilim(oku(a.dosya))
    _yazdir(f"A · {a.dosya.name}", A)
    if not a.ab:
        return 0

    B = dagilim(oku(a.ab))
    _yazdir(f"B · {a.ab.name}", B)
    if sum(A.values()) != sum(B.values()):
        print(f"\n🔴 PAYDA EŞİT DEĞİL ({sum(A.values())} ≠ {sum(B.values())}) — "
              "karşılaştırma REDDEDİLDİ.\n"
              "   Farklı soru kümeleriyle ölçülen iki oran karşılaştırılamaz: sistem "
              "bozulurken de sayı iyileşebilir.")
        return 2
    fark = oran(B) - oran(A)
    print(f"\nARIZA ORANI: {oran(A):.1f}% → {oran(B):.1f}%  ({fark:+.1f} puan)")
    # ⚠ Yargı **yazılmaz, ölçüt hatırlatılır**: raporun kendi kuralı *«oran düşmezse faz
    # GELİŞTİRİLİR, iptal edilmez»* — bir aletin faz iptal etme yetkisi yoktur.
    print("⊙ Ölçüt (`O-9`): oran DÜŞMELİ. Düşmezse faz **geliştirilir, iptal edilmez**.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
