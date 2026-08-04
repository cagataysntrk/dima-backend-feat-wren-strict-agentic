"""FAZ 4.3 — **ÇOK-TURLU TÜRKÇE BENCHMARK (sharding).** [bayraksız: kanıt]

## Neden

ICLR 2026 En İyi Makale (*LLMs Get Lost In Multi-Turn Conversation*): 200.000+ simüle
konuşma, 15 model → ortalama **−%39 doğruluk**, **%112 güvenilirlik çöküşü**. Kök neden:
*"erken turlarda varsayım yapıp erken bir nihai cevaba yapışma"*; orta turlara atıf
**%20'nin altında**. Azaltma olarak **recap** (+16 puan) öneriliyor.

🔴 **Bizim mimarimiz recap'in DETERMİNİSTİK hâlini yapısal olarak uyguluyor:** her turda
`cube_query` **geri gönderiliyor** ve `deterministic_refine` onu **düzenliyor** — yani
"özet" bir metin değil, **yapının kendisi** taşınıyor.

**Ve bu fark dünyada ölçülmemiş:** makale *text-to-SQL*'de ölçtü; **semantik katmanın aynı
testteki farkı hiç ölçülmedi**.

## 🔴 İLK ÖLÇÜM — VE KÖTÜ HABERİ

`demo-boyahane`, **44 konuşmalık sabit kohort** (tek istatistiksel olarak geçerli kohort):
**tur 1 %63,6 → tur 5 %45,5 = −%18,2**. Hedef **−%10** idi → **KALDI**. Yayımlanıyor.

*Ama düşüş, makalenin teşhisi değil.* Kayıp turları tek tek okundu: derinlikte kaybedilen
konuşmaların **tamamı** aynı şekle sahip — takip mesajı **çıplak bir ikinci ölçü adı**
(*"fire orani yuzde"*, *"ort brut maas"*). `deterministic_refine` ölçü **eklemeyi**
*"bir de … ekle"* ipucuyla tanıyor (FAZ B1'de canlıda doğrulandı); ipuçsuz çıplak ölçü adı
bir **yenileme** sayılmıyor ve tur `route()`'a düşüyor — orada da tek başına bir ölçü adı
taban üretmiyor (R1/R10).

Yani sayı *"model kayboluyor"* demiyor; **`deterministic_refine`'ın ölçü-ekleme kapısı
dar**  diyor. ⚠ Bu tur **genişletilmedi**: FAZ 4.3'ün `GERİ AL` şartı *"ölçüm harness'i —
davranış değiştirmez"*. Ölçtüğü kusuru aynı turda düzelten bir alet, bir dahaki sefere
neyi ölçtüğünü bilemez. Borç `OPERASYON-DURUM.md`'ye yazıldı.

⚠ Diğer üç şirketin kohortu **7–10** — hedef o çözünürlükte **ayırt edilemez** (`⊘`).

## Algoritma — yeni ayrıştırıcı YAZILMAZ

Tek-turluk soru `{ölçü, dönem, boyut}` **atomlarına** ayrılır ve atomlar **`route()`'un
kendi çözdüğü `cube_query` alanlarından** türetilir. İkinci bir ayrıştırıcı yazmak, testin
ölçtüğü şeyi **testin kendi yorumuna** bağlardı.

⚠ Tohum **sabit**: aynı sha → aynı dağılım. *Rastgele bir benchmark, karşılaştırılamaz
bir benchmarktır.*

## Kullanım

    python lab/sharding.py                       # dört şirket
    python lab/sharding.py --tur 5 --json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SIRKETLER = ("demo-boyahane", "gitas", "atiksan", "gulteks")

#: 🔴 SABİT TOHUM — aynı sha → aynı dağılım. Rastgele bir benchmark karşılaştırılamaz.
TOHUM = 20260804

#: Makalenin ölçtüğü düşüş **−%39**. Bizim hedefimiz: 5 turda **−%10'dan az**.
HEDEF_DUSUS = 0.10

#: 🔴 **HEDEFİ DEĞERLENDİRMEK İÇİN ASGARİ KOHORT.** `n=8`'de bir tek konuşma **%12,5
#: puan** demektir — yani hedefin (%10) altındaki her fark, tek bir örneğin gürültüsüdür.
#: *Bu boyutta "geçti" demek de "kaldı" demek kadar uydurmadır.* Altında karar **`⊘`**.
YETER_KOHORT = 20


def hedef_karari(kohort: dict[int, dict]) -> dict[str, Any]:
    """Kohort → **üç hâlli** karar: `gecti` · `kaldi` · `olculemedi`.

    ⚠ İkili bir karar (geçti/kaldı) burada **yanlış** olurdu: küçük kohortta hedefin
    altında kalmak bir başarı değil, bir **örneklem kazasıdır**. Üçüncü hâl, bu deponun
    `⊘ ÖLÇÜLEMEDİ` kuralının bu araçtaki karşılığıdır.
    """
    if len(kohort) < 2:
        return {"karar": "olculemedi", "neden": "iki derinlik ölçülemedi"}
    ilk, son = kohort[min(kohort)], kohort[max(kohort)]
    n = int(ilk.get("konusma") or 0)
    dusus = round(ilk["tam_cevaplanan"] - son["tam_cevaplanan"], 4)
    if n < YETER_KOHORT:
        return {"karar": "olculemedi", "dusus": dusus, "n": n,
                "neden": f"kohort {n} < {YETER_KOHORT}: tek konuşma "
                         f"%{100 / n:.1f} puan oynatıyor — hedef (%{HEDEF_DUSUS * 100:.0f}) "
                         f"bu çözünürlükte AYIRT EDİLEMEZ"}
    return {"karar": "gecti" if dusus < HEDEF_DUSUS else "kaldi",
            "dusus": dusus, "n": n}


def cube_query_ac(r: dict | None) -> dict:
    """`route()` bir **sarmalayıcı** döner (`{"cube_query": {...}, "measure": …}`).

    ⚠ **Kapı bunu yakaladı:** ilk sürüm üst düzey sözlüğü `cube_query` sanıyordu ve
    `atomlar()` **boş liste** döndürüyordu — eğri **tamamen boş** çıktı. *Boş bir eğri,
    kötü bir eğriden daha tehlikelidir: hiçbir şey söylemez ama tablo dolu görünür.*
    """
    r = r or {}
    return dict(r.get("cube_query") or r)


def atomlar(cq: dict) -> list[str]:
    """`cube_query` → doğal dil **atomları**. Yeni ayrıştırıcı **yok** — alanlar okunur.

    ⚠ Atomlar **tek başlarına anlamlı** olmalı: *"aylara göre"* bir turdur, *"aylara"*
    değil. Anlamsız bir parça, testi konuşmanın değil **parçalamanın** testi yapardı.
    """
    out: list[str] = []
    for m in (cq.get("measures") or [])[:2]:
        out.append(str(m).replace("_", " "))
    for d in (cq.get("dimensions") or [])[:2]:
        out.append(f"{str(d).replace('_', ' ')} bazinda")
    for t in cq.get("timeDimensions") or []:
        g = str((t or {}).get("granularity") or "").lower()
        if g:
            out.append({"month": "aylara gore", "year": "yillara gore",
                        "week": "haftalara gore", "day": "gunlere gore"}.get(g, ""))
    for f in (cq.get("filters") or [])[:1]:
        v = (f or {}).get("value")
        if isinstance(v, str) and v and not v[:4].isdigit():
            out.append(f"{v} icin")
    return [a for a in out if a]


def birlestir(a: dict, b: dict) -> dict:
    """Aynı cube'un **iki `route()` çıktısını** birleştirir → daha derin konuşma.

    🔴 **Kapı bunu yakaladı (ikinci kez).** Tek bir soru tipik olarak **3 atom** üretiyordu
    (`ölçü` · `boyut bazında` · `aylara göre`); yani `4` ve `5` tur satırları **gerçekte 3
    turdu** ve tablo, ölçmediği bir derinliği ölçmüş gibi görünüyordu. *Etiketi doğru
    olmayan bir satır, boş bir satırdan tehlikelidir.*

    ⚠ İkinci bir ayrıştırıcı **yazılmadı**: birleşen iki taraf da `route()`'un kendi
    çözdüğü `cube_query`. Birleştirme yalnız **küme birleşimidir**.
    """
    if a.get("cube") != b.get("cube"):
        return dict(a)
    out = dict(a)
    for alan in ("measures", "dimensions"):
        gorulen, birlesim = set(), []
        for x in list(a.get(alan) or []) + list(b.get(alan) or []):
            if str(x) not in gorulen:
                gorulen.add(str(x))
                birlesim.append(x)
        out[alan] = birlesim[:2]
    return out


def turlara_dagit(atom: list[str], tur: int, rnd: random.Random) -> list[str]:
    """Atomları **rastgele sırayla** turlara dağıtır (tohum sabit).

    🔴 **TOHUM KONUŞMA BAŞINA, DERİNLİK BAŞINA DEĞİL.** İlk sürüm `Random(TOHUM + tur)`
    kullanıyordu: her derinlikte **sıralama da değişiyordu**, yani eğri *"derinlik"* ile
    *"sıra"*yı **karıştırıyordu** ve düşüş, derinliğin değil karıştırmanın eseri olabilirdi.
    Derinlik-*N*, derinlik-*N+1*'in **öneki olmak zorundadır** — makalenin shard tasarımı
    da budur: shard kümesi sabit, **açığa çıkma** kademeli.

    🔴 İlk tur **her zaman bir ölçü** taşır: makalenin senaryosu *"eksik bilgiyle başla"*,
    *"anlamsız başla"* değil. Ölçüsüz bir ilk tur `route()`'u zaten `R1`'e düşürürdü ve
    test **konuşmayı değil boş girdiyi** ölçerdi.
    """
    if not atom:
        return []
    ilk, kalan = atom[0], atom[1:]
    rnd.shuffle(kalan)
    turlar = [ilk] + kalan
    return turlar[:tur]


def konusma_kos(sema: dict, turlar: list[str], *, olcu_ekle: bool = False) -> dict:
    """Turları **sırayla** koşar; her turda `cube_query` taşınır (deterministik recap).

    Döner: `{cevaplanan, yapi_kaybi, cq_surekliligi, son_cube}`
    """
    from app import cube_router as cr

    cq: dict | None = None
    cevaplanan = 0
    dolu_tur = 0
    yapi_kaybi = 0
    for i, t in enumerate(turlar):
        qn = cr._norm(t)
        if cq is None:
            yeni = cube_query_ac(cr.route(qn, sema)) or None
        else:
            # 🔴 DETERMİNİSTİK RECAP: yapının kendisi taşınıyor, bir metin özeti değil.
            duz = cr.deterministic_refine(cq, qn, sema, olcu_ekle=olcu_ekle)
            yeni = duz or (cube_query_ac(cr.route(qn, sema)) or None)
            if yeni is None:
                # Makalenin "kayboldu" hâli: takip mesajı bağlama BAĞLANAMADI.
                yapi_kaybi += 1
        if yeni is not None:
            cq = yeni
            cevaplanan += 1
        if cq is not None:
            dolu_tur += 1
        del i
    return {
        "tur": len(turlar),
        "cevaplanan": cevaplanan,
        "yapi_kaybi": yapi_kaybi,
        "cq_surekliligi": round(dolu_tur / len(turlar), 4) if turlar else 0.0,
        "son_cube": (cq or {}).get("cube"),
    }


def kos(sema: dict, *, azami_tur: int = 5, ornek: int = 200,
        olcu_ekle: bool = False) -> dict:
    """Korpusun sorularını shard'layıp **tur derinliği ↔ doğruluk** eğrisini ölçer."""
    from app import cube_router as cr

    rnd = random.Random(TOHUM)
    tohumluk: list[dict] = []
    for c in sema.get("cubes") or []:
        for olcu, syns in (c.get("measure_synonyms") or {}).items():
            s = str((syns or [olcu])[0]).removesuffix("!")
            for boyut in (c.get("dimensions") or [])[:2]:
                q = f"bu yil {s} {str(boyut).replace('_', ' ')} bazinda aylara gore"
                r = cube_query_ac(cr.route(cr._norm(q), sema))
                if r.get("measures"):
                    tohumluk.append(r)
    # Aynı cube'un ardışık tohumlarını birleştir → 3 atom yerine 5 atom.
    zengin: list[dict] = []
    for i, cq in enumerate(tohumluk):
        zengin.append(birlestir(cq, tohumluk[(i + 1) % len(tohumluk)]) if tohumluk else cq)
    tohumluk = zengin
    rnd.shuffle(tohumluk)
    tohumluk = tohumluk[:ornek]

    egri: dict[int, dict] = {}
    for tur in range(1, azami_tur + 1):
        toplam = kayip = surek = tam = 0
        for i, cq in enumerate(tohumluk):
            t = turlara_dagit(atomlar(cq), tur, random.Random(TOHUM + i))
            # 🔴 **GERÇEK DERİNLİK ŞARTI.** `turlar[:tur]` istenen turdan KISA bir konuşma
            # döndürebilir; onu `tur` satırında saymak, ölçülmemiş bir derinliği ölçülmüş
            # gibi gösterirdi. Kısa konuşma bu satıra **girmez**.
            if len(t) != tur:
                continue
            r = konusma_kos(sema, t, olcu_ekle=olcu_ekle)
            toplam += 1
            kayip += r["yapi_kaybi"]
            surek += r["cq_surekliligi"]
            tam += 1 if r["cevaplanan"] == r["tur"] else 0
        # ⚠ `toplam == 0` → satır **yazılmaz**: `⊘ ÖLÇÜLEMEDİ`. Sıfırı `%0` diye yazmak
        # ölçülmemişi başarısız gibi gösterirdi.
        if toplam:
            egri[tur] = {
                "konusma": toplam,
                "tam_cevaplanan": round(tam / toplam, 4),
                "yapi_kaybi": kayip,
                "cq_surekliligi": round(surek / toplam, 4),
            }
    # 🔴 **SABİT KOHORT — asıl sayı budur.** `egri` her derinlikte FARKLI bir popülasyon
    # ölçer (tur 5'e yalnız 5+ atomlu konuşmalar girer), dolayısıyla "tur 1 → tur 5 düşüşü"
    # oradan okunursa **elma-armut** kıyası olur. Kohort, `azami_tur`'a ULAŞABİLEN
    # konuşmaların **aynısını** 1…5 arası her derinlikte koşar. *Popülasyonu değişen bir
    # eğrinin eğimi, ölçtüğü şeyin değil örnekleminin eğimidir.*
    kohort_cq = [c for c in tohumluk if len(atomlar(c)) >= azami_tur]
    kohort: dict[int, dict] = {}
    for tur in range(1, azami_tur + 1):
        toplam = kayip = tam = 0
        for i, cq in enumerate(kohort_cq):
            t = turlara_dagit(atomlar(cq), tur, random.Random(TOHUM + i))
            if len(t) != tur:
                continue
            r = konusma_kos(sema, t, olcu_ekle=olcu_ekle)
            toplam += 1
            kayip += r["yapi_kaybi"]
            tam += 1 if r["cevaplanan"] == r["tur"] else 0
        if toplam:
            kohort[tur] = {"konusma": toplam, "yapi_kaybi": kayip,
                           "tam_cevaplanan": round(tam / toplam, 4)}
    return {"ornek": len(tohumluk), "egri": egri, "kohort": kohort,
            "azami_atom": max((len(atomlar(c)) for c in tohumluk), default=0),
            "hedef": hedef_karari(kohort)}


def rapor_metni(veri: dict[str, dict]) -> str:
    s = ["# Çok-turlu Türkçe benchmark (sharding)",
         "",
         "> ICLR 2026 En İyi Makale: 15 model, 200.000+ konuşma → **−%39 doğruluk**,",
         "> **%112 güvenilirlik çöküşü**. Kök neden: *erken turda varsayım yapıp nihai",
         "> cevaba yapışma*. Azaltma önerisi: **recap** (+16 puan).",
         "",
         "🔴 **Bizim mimarimiz recap'in DETERMİNİSTİK hâlini yapısal olarak uyguluyor:**",
         "her turda `cube_query` geri gönderiliyor ve `deterministic_refine` onu",
         "**düzenliyor** — yani taşınan şey bir metin özeti değil, **yapının kendisi**.",
         "",
         "⚠ **Bu fark dünyada ölçülmemiş:** makale *text-to-SQL*'de ölçtü; semantik",
         "katmanın aynı testteki farkı **hiç ölçülmedi**.",
         ""]
    for sirket, d in veri.items():
        s += [f"## {sirket} · örnek {d.get('ornek', 0)} konuşma", "",
              "⚠ Aşağıdaki tabloda **her satır farklı bir popülasyondur** (tur *N*'e yalnız "
              "*N* atomlu konuşmalar girer) — **eğim buradan okunmaz**, kohort tablosundan "
              "okunur.", "",
              "| tur | konuşma | tam cevaplanan | yapı kaybı | `cube_query` sürekliliği |",
              "|---|---|---|---|---|"]
        egri = d.get("egri") or {}
        for tur, x in sorted(egri.items()):
            s.append(f"| {tur} | {x['konusma']} | %{x['tam_cevaplanan'] * 100:.1f} "
                     f"| {x['yapi_kaybi']} | %{x['cq_surekliligi'] * 100:.1f} |")
        eksik = [t for t in range(1, 6) if t not in egri]
        if eksik:
            s.append("")
            s.append(f"⊘ **ÖLÇÜLEMEDİ:** tur {', '.join(map(str, eksik))} — bu derinlikte "
                     f"hiç konuşma yok (azami atom: {d.get('azami_atom', 0)}). *Ölçülmemiş "
                     "bir derinliği tabloya yazmak, ölçülmüş gibi gösterirdi.*")
        s.append("")
        k = d.get("kohort") or {}
        if len(k) >= 2:
            ilk, son = k[min(k)], k[max(k)]
            dusus = ilk["tam_cevaplanan"] - son["tam_cevaplanan"]
            s += [f"**Sabit kohort ({ilk['konusma']} konuşma, her derinlikte AYNI'sı):**",
                  "",
                  "| tur | tam cevaplanan | yapı kaybı |", "|---|---|---|"]
            s += [f"| {t} | %{x['tam_cevaplanan'] * 100:.1f} | {x['yapi_kaybi']} |"
                  for t, x in sorted(k.items())]
            h = d.get("hedef") or {}
            rozet = {"gecti": "✅ GEÇTİ", "kaldi": "🔴 KALDI",
                     "olculemedi": "⊘ ÖLÇÜLEMEDİ"}.get(h.get("karar"), "⊘")
            s += ["",
                  f"**Düşüş (tur {min(k)} → {max(k)}): %{dusus * 100:.1f}** — makalenin "
                  f"ölçtüğü **−%39**'a karşı. Hedef: **−%{HEDEF_DUSUS * 100:.0f}'dan az**.",
                  "",
                  f"**Karar: {rozet}**"
                  + (f" — {h['neden']}." if h.get("neden") else ""),
                  ""]
        elif d.get("egri"):
            s += ["⊘ **Sabit kohort ÖLÇÜLEMEDİ** — bu şirkette `azami_tur` derinliğine "
                  "ulaşan konuşma yok. *Üstteki tablodan eğim OKUNMAZ: her satır farklı "
                  "bir popülasyondur.*", ""]
    s += ["⚠ **`⊘ ÖLÇÜLEMEDİ` bir başarısızlık DEĞİL, bir dürüstlüktür:** kohort "
          f"**{YETER_KOHORT}**'nin altındayken tek bir konuşma hedefin tamamı kadar puan "
          "oynatır. O çözünürlükte *\"geçti\"* demek, *\"kaldı\"* demek kadar uydurmadır.",
          "",
          "⚠ **Kötü sonuç saklanmaz.** §C/16'nın *ilan edilmiş puanlama kuralı* şartı,",
          "sonucun yönünden bağımsızdır: eğri düşerse **düşmüş hâliyle** yayımlanır."]
    return "\n".join(s) + "\n"


def _sema(sirket: str):
    from app.compose import build, compose
    from app.wren_service import WrenService

    out = Path(tempfile.mkdtemp(prefix=f"sh-{sirket}-")) / "proje"
    compose(sirket, Path(__file__).resolve().parents[1] / "demo", out)
    build(out)
    return WrenService(out, datasource="duckdb", connection_info={}).schema()


def main() -> int:
    ap = argparse.ArgumentParser(description="Çok-turlu sharding benchmark")
    ap.add_argument("--sirket", nargs="*", default=list(SIRKETLER))
    ap.add_argument("--tur", type=int, default=5)
    ap.add_argument("--ornek", type=int, default=120)
    ap.add_argument("--json", action="store_true")
    #: 🔴 A/B — FAZ 4.3 borcunun kapanışı **ölçülerek** kanıtlanır, iddia edilerek değil.
    ap.add_argument("--olcu-ekle", action="store_true",
                    help="çıplak ikinci ölçü adını EKLEME olarak tanı (bayrak açık hâli)")
    a = ap.parse_args()

    veri: dict[str, dict] = {}
    for s in a.sirket:
        try:
            veri[s] = kos(_sema(s), azami_tur=a.tur, ornek=a.ornek,
                          olcu_ekle=a.olcu_ekle)
        except Exception as exc:                             # noqa: BLE001
            print(f"  {s}: ⊘ ÖLÇÜLEMEDİ — {exc}")
    if a.json:
        print(json.dumps(veri, ensure_ascii=False, indent=2))
        return 0
    metin = rapor_metni(veri)
    hedef = Path(__file__).resolve().parent / "reports" / "sharding.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(metin)
    print(f"→ {hedef}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
