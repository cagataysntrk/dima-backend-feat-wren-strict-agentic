"""FAZ 4.2 — **RİSK-KAPSAM EĞRİSİ.** [bayraksız: kanıt]

MIMARI §9.1: *"hiçbir sevk edilmiş BI ürünü … **risk-kapsam eğrisi** yayınlamıyor."*
Bu araç o iddiayı **sayıya** çevirir.

## 🔴 SKALER `confidence` UYDURULMAZ

Eğri, kara-kutu bir güven puanı üzerinde **değil**, bizim **ayrık kapılarımız** üzerinde
tanımlanır:

    route (deterministik)  →  tie-chip (netleştirme)  →  intent (cube+llm)  →  discovery

Her nokta *"bu kapıya kadar cevaplarsak kapsam ne, risk ne"* der. Literatürün kara-kutu
sinyalleri **0,61–0,68 AUROC**'ta platoluyor; **bizim eğrimiz bir tahmin değil, bir
mimari beyandır** — hangi yoldan geçtiği **ölçülür**, tahmin edilmez.

## ⚠ YAN KURAL — BAĞLAYICI

`consistency_k` uyumu bir **güven eşiğine DÖNÜŞTÜRÜLMEZ**. Araştırma bunu doğrudan
çürütüyor: *"bir model son derece self-consistent olup yine de **tutarlı biçimde YANLIŞ**
olabilir."* Bu araç `consistency` alanına **hiç bakmaz** ve kapı bunu doğrular.

## Yeniden üretilebilirlik

Aynı sha → **aynı eğri**. Girdi korpustur (LLM'siz, deterministik); rastgelelik yok.

## Kullanım

    python lab/risk_kapsam.py                 # dört şirket, rapor
    python lab/risk_kapsam.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SIRKETLER = ("demo-boyahane", "gitas", "atiksan", "gulteks")

#: 🔴 **AYRIK KAPILAR** — eğrinin x ekseni. Sıra **anlamlıdır**: her kapı bir öncekinin
#: cevaplayamadığını devralır, yani kapsam **monoton artar**.
KAPILAR = ("route", "tie_chip", "intent", "discovery")

#: Kapıların **determinizm** sınıfı — riskin kaynağı budur, bir puan değil.
DETERMINIZM = {
    "route": "deterministik",
    "tie_chip": "deterministik",      # netleştirme: cevap değil, SORU üretir
    "intent": "llm_secim",            # sayı küpten, SEÇİM olasılıksal
    "discovery": "llm_sql",           # SQL'in kendisi olasılıksal
}


def _sema(sirket: str):
    from app.compose import build, compose
    from app.wren_service import WrenService

    out = Path(tempfile.mkdtemp(prefix=f"rk-{sirket}-")) / "proje"
    compose(sirket, Path(__file__).resolve().parents[1] / "demo", out)
    build(out)
    return WrenService(out, datasource="duckdb", connection_info={}).schema()


def sinifla(sema: dict, sorular: list[str]) -> dict[str, int]:
    """Her soruyu **hangi kapıda** durduğuna göre sınıflar. LLM **çağrılmaz**.

    ⚠ `intent`/`discovery` bu koşumda **ölçülemez** (LLM yok) — o yüzden sayılmaz,
    `llm_gerekli` kovasına düşer. *Ölçülmeyeni bir kapıya yazmak, eğriyi olduğundan
    iyimser gösterirdi.*
    """
    from app import cube_router as cr

    sayim = {"route": 0, "tie_chip": 0, "llm_gerekli": 0}
    for q in sorular:
        qn = cr._norm(q)
        if cr.route(qn, sema) is not None:
            sayim["route"] += 1
            continue
        kod = cr.teshis(q, sema)   # KÖK-9/KÇ-5 — ham kapı kodu %43,2 ayrışıyordu
        # Netleştirme (`tie`/`CLARIFY`) bir **cevapsızlık değil**, bir sorudur: kullanıcı
        # bir tık sonra cevabı alır ve o cevap **deterministiktir**.
        sayim["tie_chip" if kod in ("R7", "R8", None) else "llm_gerekli"] += 1
    return sayim


def egri(sayim: dict[str, int]) -> list[dict]:
    """Kümülatif kapsam/risk noktaları. **Risk bir tahmin değil, determinizm sınıfıdır.**

    🔴 `hata_orani` **YAZILMAZ**: bir kapının hata oranını bu araç ölçemez (doğruluk
    korpusun işi). Yazsaydık **uydurma** olurdu. Onun yerine her nokta **determinizm
    sınıfını** taşır — *"bu kapsamda cevaplarsak sayının kaynağı nedir"*.
    """
    toplam = sum(sayim.values()) or 1
    kumulatif = 0
    out = []
    for kapi in ("route", "tie_chip", "llm_gerekli"):
        kumulatif += sayim.get(kapi, 0)
        out.append({
            "kapi": kapi,
            "kapsam": round(kumulatif / toplam, 4),
            "determinizm": DETERMINIZM.get(kapi, "llm_secim"),
            "bu_kapida": sayim.get(kapi, 0),
        })
    return out


def _sorular(sema: dict) -> list[str]:
    """Korpusun ürettiği aynı sonda kümesi — **yeniden üretilebilir**, rastgele değil."""
    out: list[str] = []
    for c in sema.get("cubes") or []:
        for _o, syns in (c.get("measure_synonyms") or {}).items():
            for s in (syns or [])[:3]:
                s = str(s).removesuffix("!").strip()
                if s:
                    out.append(s)
                    out.append(f"bu yil {s}")
    return sorted(set(out))


def rapor_metni(veri: dict[str, list[dict]]) -> str:
    s = ["# Risk-kapsam eğrisi",
         "",
         "> MIMARI §9.1: *\"hiçbir sevk edilmiş BI ürünü risk-kapsam eğrisi yayınlamıyor.\"*",
         "",
         "🔴 **Skaler `confidence` UYDURULMAZ.** Eğri kara-kutu bir puan üzerinde değil,",
         "**ayrık kapılarımız** üzerinde tanımlı: `route → tie-chip → intent → discovery`.",
         "Literatürün kara-kutu sinyalleri **0,61–0,68 AUROC**'ta platoluyor; bizimki bir",
         "tahmin değil bir **mimari beyandır** — hangi yoldan geçildiği **ölçülür**.",
         "",
         "⚠ **YAN KURAL (bağlayıcı):** `consistency_k` uyumu bir güven eşiğine",
         "**dönüştürülmez** — *\"bir model son derece self-consistent olup yine de tutarlı",
         "biçimde YANLIŞ olabilir.\"*",
         ""]
    for sirket, noktalar in veri.items():
        s.append(f"## {sirket}")
        s.append("")
        s.append("| kapı | kümülatif kapsam | determinizm | bu kapıda |")
        s.append("|---|---|---|---|")
        for n in noktalar:
            s.append(f"| `{n['kapi']}` | %{n['kapsam'] * 100:.1f} | {n['determinizm']} "
                     f"| {n['bu_kapida']} |")
        s.append("")
    s += ["⚠ **`hata_orani` bilerek YOK:** bir kapının hata oranını bu araç ölçemez "
          "(doğruluk korpusun işi). Yazsaydık **uydurma** olurdu.",
          "",
          "⚠ `intent`/`discovery` bu koşumda **ölçülemez** (LLM'siz) — `llm_gerekli` "
          "kovasında toplanır. *Ölçülmeyeni bir kapıya yazmak, eğriyi olduğundan iyimser "
          "gösterirdi.*"]
    return "\n".join(s) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Risk-kapsam eğrisi (ayrık kapılar üstünde)")
    ap.add_argument("--sirket", nargs="*", default=list(SIRKETLER))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    veri: dict[str, list[dict]] = {}
    for s in a.sirket:
        try:
            sema = _sema(s)
            veri[s] = egri(sinifla(sema, _sorular(sema)))
        except Exception as exc:                             # noqa: BLE001
            print(f"  {s}: ⊘ ÖLÇÜLEMEDİ — {exc}")
    if a.json:
        print(json.dumps(veri, ensure_ascii=False, indent=2))
        return 0
    metin = rapor_metni(veri)
    hedef = Path(__file__).resolve().parent / "reports" / "risk_kapsam.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(metin)
    print(f"→ {hedef}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
