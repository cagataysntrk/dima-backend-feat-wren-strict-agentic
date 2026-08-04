"""FAZ 5.3 — **KONUŞMA TÜRLERİNİN GERÇEK İFADE KORPUSU.** [bayraksız: kök neden]

## Kök neden — 5.2'nin bulduğu şey

*"Müdüre 3 cümle yaz"* çalışan bir yeteneğe **bir kelime yüzünden** ulaşamıyordu. Ama
kök neden *"kelime eksik"* **değildi**:

> 🔴 **Kalıp sözlüğü TASARIMCININ kelimelerinden kuruldu** (*analiz et · yorumla ·
> özetle*), **kullanıcının ifadelerinden değil.**

Ve kelime eklemek **ADR-0008'in yasakladığı yamadır** — *"kök nedeni düzelt, örneği
değil"*. Bu dosya kökü düzeltir: kalıp sözlüğünün karşısına bir **ölçüm korpusu** koyar.

## Bu bir SÖZLÜK DEĞİL, bir ÖLÇÜ

`followup.py`'nin kalıpları **ürün kodudur**; buradaki ifadeler **testin girdisidir**.
Ayrım kritiktir:

| | kalıp sözlüğü (`followup.py`) | ifade korpusu (bu dosya) |
|---|---|---|
| ne yapar | eşleştirir | **eşleşmeyi ölçer** |
| büyürse | kapsam artar **ve yanlış-pozitif riski** artar | yalnız **ölçüm** keskinleşir |
| bir kelime eklemek | ADR-0008 ihlali olabilir | **her zaman meşru** |

*Bir yamayı bir ölçümden ayıran şey, hangisinin cevabı değiştirdiğidir.*

## ⚠ Bağımlılık — ve v1'in kapısı

Varyantların **kalıcı** kaynağı **FAZ 8.1**'dir (gerçek kullanım penceresi). v1 kapısı
**≥10 elle küratörlenmiş varyantla** kapanır; 8.1'den sonra bu liste **otomatik beslenir**.
Bugünkü liste bir **başlangıç**tır, bir bitiş değil — ve bunu yazmak, listeyi bir gün
*"tamamlanmış"* sanmayı önler.

## GERİ AL — ve neden "eski sözlüğe dönmek" DEĞİL

Bir varyant **yanlış-pozitif** üretirse korpustan **çıkarılır ve çıkarma gerekçesi
kayda geçer** (`CIKARILAN`). ⚠ Geri alma *"eski dar sözlüğe dönmek"* **değildir** — o,
ölçülmüş kusuru geri getirirdi.

## Kullanım

    python lab/konusma_ifadeleri.py            # kapsama raporu
    python lab/konusma_ifadeleri.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

#: 🔴 §C/9'un kapısı: **her tür için ≥10 gerçek varyant**.
ASGARI_VARYANT = 10

#: **GERÇEK KULLANICI İFADELERİ** — tür başına. ⚠ Etiket kelimesi (türün kendi adı)
#: bilerek **dışlanmadı** ama *tek başına* bir varyant sayılmaz: liste, kullanıcının
#: gerçekten yazdığı **cümleleri** taşır, sözlüğün kendi kelimelerini değil.
IFADELER: dict[str, tuple[str, ...]] = {
    "neden": (
        "bu neden böyle?",
        "bunun sebebi ne?",
        "niye bu kadar düşük?",
        "neden düşmüş?",
        "bu nereden geliyor?",
        "bunu ne etkiledi?",
        "bu artışın sebebi nedir",
        "niçin böyle çıktı",
        "bunda ne oldu?",
        "buradaki sapma neden",
        "bu sonucu ne yol açtı",
    ),
    "normal_mi": (
        "normal mi?",
        "bu normal mi",
        "olağan mı",
        "beklenen bir şey mi",
        "iyi mi kötü mü",
        "bu iyi mi?",
        "endişelenmeli miyim",
        "sorun var mı",
        "makul mü",
        "alarm vermeli miyiz",
        "bu değer beklenen aralıkta mı",
    ),
    "ne_yapmali": (
        "ne yapmalıyız?",
        "ne yapabiliriz",
        "ne önerirsin",
        "bunu nasıl iyileştiririz",
        "nasıl düzeltiriz",
        "nasıl azaltırız",
        "ne tavsiye edersin",
        "hangi aksiyonu almalıyız",
        "önlem olarak ne yapılır",
        "nasıl yol alırız",
        "buradan sonra ne yapmalı",
    ),
    "isaret": (
        "şu düşüş ne?",
        "bu sıçrama nedir",
        "buradaki kırılma ne",
        "şu artış neyin nesi",
        "bu anomali ne",
        "aykırı değer var mı",
        "şu tepe noktası ne",
        "bu düşüş kalıcı mı",
        "grafikteki o çukur ne",
        "bu kırılmayı açıkla",
        "şuradaki sıçramayı anlat",
        "bu sıçrama ne",
        "bu düşüş ne",
        "şu artış ne",
        "buradaki anomali ne",
        "bu kırılma ne",
    ),
    "anlat": (
        "bunu analiz et",
        "yorumlar mısın",
        "özetle",
        "değerlendir",
        "bu grafiği açıkla",
        "ne diyor bu",
        "bunu okur musun",
        "kısaca anlat",
        "bu tabloyu yorumla",
        "ne anlama geliyor",
        "bunu incele",
        "bunu yorumla",
        "bu ne demek",
        "bunu açıkla",
        "bu sonucu değerlendir",
        "bu raporu özetle",
    ),
    # FAZ 5.1
    "takip": (
        "bunu takip et",
        "bunu takibe al",
        "bunu izle",
        "bunu izlemeye al",
        "bu raporu takip et",
        "bu raporu izle",
        "bundan haberim olsun",
        "bunu bildir",
        "bunu gündemde tut",
        "bunu takipte kal",
        "bunu düzenli gönder",
    ),
    # FAZ 5.2
    "paylas": (
        "müdüre 3 cümle yaz",
        "müdüre yaz",
        "yöneticiye yaz",
        "patrona yaz",
        "bunu paylaş",
        "paylaşabilir link ver",
        "link oluştur",
        "maille",
        "mail at",
        "üç cümle ile özetle",
        "iki cümle yaz",
        "sunuma koy",
    ),
}

#: 🔴 **ÇIKARILAN VARYANTLAR — gerekçesiyle.** Bir varyant yanlış-pozitif ürettiğinde
#: sessizce silinmez: neden çıkarıldığı burada durur ki aynı ifade bir daha **aynı
#: gerekçeyle** eklenmesin. *Sessizce silinen bir vaka, bir gün geri gelir.*
CIKARILAN: dict[str, str] = {
    "fire takibi nasıl yapılır":
        "FAZ 5.1 — `TUR_TAKIP` sanılıyordu ama bu YENİ BİR KONUDUR (zamir yok, kısa "
        "değil). Korpusta tutulsaydı `konu_degisimi` sınıfını çalan bir kalıbı meşru "
        "göstermiş olurdu.",
    "analizi kim yaptı":
        "`TUR_ANLAT` sanılabilir ama bir **meta** sorudur (veri sorusu değil) ve "
        "`_META_HINTS` yolunun işidir — konuşma türü değil.",
}


def _kacma_sebebi(ifade: str, beklenen: str, n) -> str:
    """🔴 **Kaçma sebebi SINIFLANDIRILIR — körlemesine kelime EKLENMEZ.**

    *"Kök nedeni düzelt, örneği değil"* (ADR-0008). Bir varyantın tanınmaması dört farklı
    şey olabilir ve **yalnız birine** sözlükle cevap verilir:

    | sebep | doğru cevap |
    |---|---|
    | `sozlukte-yok` | ölçüm gösterdi → **sözlüğe veri olarak** girer (5.3'ün işi) |
    | `zamir-sarti` | ⚠ **DOKUNULMAZ** — şart `konu_degisimi`'ni koruyor |
    | `baska-tur-kazandi` | tanındı, yalnız başka tür — **kusur değil**, öncelik |
    | `yapisal-oncelik` | ⚠ **DOKUNULMAZ** — kullanıcı yeni sayı bekliyor |
    """
    from app import followup

    if n.sinif == followup.SINIF_YAPISAL:
        return "yapisal-oncelik"
    if n.sinif == followup.SINIF_KONUSMA:
        return "baska-tur-kazandi"
    q = followup._norm(ifade)
    kaliplar = {"neden": followup._NEDEN, "normal_mi": followup._NORMAL,
                "ne_yapmali": followup._NE_YAPMALI, "isaret": followup._ISARET,
                "anlat": followup._ANLAT, "takip": followup._TAKIP,
                "paylas": followup._PAYLAS}.get(beklenen, ())
    if followup._hit(q, kaliplar):
        return "zamir-sarti"
    return "sozlukte-yok"


def olc() -> dict[str, dict]:
    """Her varyant için **tanındı mı** ve **tanınmadıysa NEDEN** — ürün koduyla ölçülür.

    🔴 İki ayrı sayı raporlanır ve **karıştırılmaz**:
      · `konusma`  — *konuşma sınıfına girdi mi* (§C/9'un asıl sorusu: *"bir kelime
        yüzünden kapalı yetenek"* var mı)
      · `tur_dogru` — *beklenen türe* girdi mi (daha zayıf bir sinyal: bazı ifadeler
        gerçekten iki türe birden yakındır)

    *İkisini tek sayıya katlamak, bir öncelik kararını bir kusur gibi gösterirdi.*
    """
    from app import followup

    out: dict[str, dict] = {}
    for tur, ifadeler in IFADELER.items():
        konusma, tur_dogru, kacan = 0, 0, []
        for x in ifadeler:
            n = followup.sinifla(x, baglam_var=True)
            if n.sinif == followup.SINIF_KONUSMA:
                konusma += 1
                if n.tur == tur:
                    tur_dogru += 1
                    continue
            kacan.append({"ifade": x, "sebep": _kacma_sebebi(x, tur, n),
                          "dustugu": f"{n.sinif}/{n.tur or '-'}"})
        out[tur] = {
            "toplam": len(ifadeler),
            "konusma": konusma,
            "tur_dogru": tur_dogru,
            "oran": round(konusma / len(ifadeler), 4) if ifadeler else None,
            "kacan": kacan,
            # 🔴 KAPI **konuşma sınıfı** üstünde: §C/9 *"bir kelime yüzünden kapalı
            # yetenek"* sorusunu sorar, *"tür seçimi mükemmel mi"* sorusunu değil.
            "yeterli": konusma >= ASGARI_VARYANT,
        }
    return out


def rapor_metni(veri: dict[str, dict]) -> str:
    s = ["# Konuşma türleri — gerçek ifade korpusu (FAZ 5.3)",
         "",
         "> 🔴 Kök neden: kalıp sözlüğü **tasarımcının** kelimelerinden kuruldu, ",
         "> **kullanıcının ifadelerinden** değil. Kelime eklemek ADR-0008'in yasakladığı",
         "> yamadır; **ölçüm korpusu** eklemek değildir.",
         "",
         f"🔴 §C/9 kapısı: her tür için **≥{ASGARI_VARYANT}** gerçek varyant tanınmalı.",
         "",
         "⚠ **İki sayı ayrı tutulur:** `konuşma` = konuşma sınıfına girdi mi (§C/9'un",
         "asıl sorusu); `tür doğru` = beklenen türe girdi mi. *İkisini tek sayıya",
         "katlamak, bir öncelik kararını bir kusur gibi gösterirdi.*",
         "",
         "| tür | varyant | **konuşma** | tür doğru | oran | kapı |",
         "|---|---|---|---|---|---|"]
    for tur, d in sorted(veri.items()):
        rozet = "✅" if d["yeterli"] else "🔴 KALDI"
        s.append(f"| `{tur}` | {d['toplam']} | **{d['konusma']}** | {d['tur_dogru']} | "
                 f"%{(d['oran'] or 0) * 100:.0f} | {rozet} |")
    s += ["",
          "### Kaçma sebepleri — **körlemesine kelime EKLENMEZ**",
          "",
          "| sebep | doğru cevap |",
          "|---|---|",
          "| `sozlukte-yok` | ölçüm gösterdi → sözlüğe **veri olarak** girer (5.3'ün işi) |",
          "| `zamir-sarti` | ⚠ **DOKUNULMAZ** — şart `konu_degisimi`'ni koruyor |",
          "| `baska-tur-kazandi` | tanındı, yalnız başka tür — **kusur değil**, öncelik |",
          "| `yapisal-oncelik` | ⚠ **DOKUNULMAZ** — kullanıcı yeni sayı bekliyor |",
          ""]
    for tur, d in sorted(veri.items()):
        if d["kacan"]:
            s += [f"### `{tur}` — beklenen türe girmeyenler", "",
                  "| ifade | sebep | düştüğü |", "|---|---|---|"]
            s += [f"| `{k['ifade']}` | `{k['sebep']}` | `{k['dustugu']}` |"
                  for k in d["kacan"]]
            s.append("")
    s += ["---", "",
          "## ⚠ Bu korpus bir BAŞLANGIÇ, bir bitiş değil",
          "",
          "Varyantların **kalıcı** kaynağı **FAZ 8.1**'dir (gerçek kullanım penceresi).",
          "v1 kapısı elle küratörlenmiş listeyle kapanır; 8.1'den sonra **otomatik**",
          "beslenir. *Bunu yazmak, listeyi bir gün 'tamamlanmış' sanmayı önler.*",
          ""]
    if CIKARILAN:
        s += ["## 🔴 Çıkarılan varyantlar — **gerekçesiyle**", ""]
        s += [f"- `{k}` — {v}" for k, v in CIKARILAN.items()]
        s += ["", "*Sessizce silinen bir vaka, bir gün geri gelir.*"]
    return "\n".join(s) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Konuşma türü ifade korpusu")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    veri = olc()
    if a.json:
        print(json.dumps(veri, ensure_ascii=False, indent=2))
        return 0
    metin = rapor_metni(veri)
    hedef = Path(__file__).resolve().parent / "reports" / "konusma_ifadeleri.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(metin)
    print(f"→ {hedef}")
    return 0 if all(d["yeterli"] for d in veri.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
