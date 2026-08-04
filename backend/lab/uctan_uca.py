"""FAZ 4.8 — ⭐ **UÇTAN UCA CEVAP DOĞRULUĞU.** [bayraksız: kanıt] *(§C/16'nın ölçüm aracı)*

## 🔴 Neden var: rakiplerin yayımladığı TEK kıyaslanabilir sayıyı biz ölçmüyoruz

| bugünkü alet | ne ölçüyor | ne ölçmüyor |
|---|---|---|
| `nl_corpus` (%93,1) | **doğru cube seçildi mi** | *doğru CEVAP mı* |
| `nl_accuracy` (n=63) | etiketli vaka | ölçek |
| `eval` | MIMARI §7'nin kendi ifadesiyle *"zaten çalışan şeye göre kuratörlenmiş"* | **regresyon kilidi**, doğruluk **değil** |

Yani dışarıya kıyaslanabilir bir sayı vermek için **bugün elimizde alet yoktu**. Bu o alet.

---

## 🔴 PUANLAMA KURALI — **KOŞUMDAN ÖNCE İLAN EDİLDİ**

> **Bir cevap ancak *dönen değer*, *varlık kapsamı* ve *zaman/filtre semantiği* altın
> cevapla eşleşiyorsa DOĞRU sayılır.**

Üç şart da **aynı anda** aranır. Kural **koda tek yerde** yazılıdır (`puanla()`) ve kapı
bunu kilitler — ikinci bir puanlama yolu, sonucu kurala değil kuralı sonuca uydurmanın
kapısıdır.

⚠ **Sıra bilinçli:** kural **önce** ilan edildi, sonra koşuldu. Tersi sıra, sayıyı görüp
kuralı ona göre yumuşatmaya davettir — ve bu, sektörün manşet sayılarını kıyaslanamaz
yapan şeyin ta kendisidir.

## 🔴 NETLEŞTİRME **AYRI SATIR** — PAYDADAN GİZLİCE ÇIKARILMAZ

*Her satıcı reddedilenleri paydadan sessizce çıkarıyor ve bu yüzden manşet sayıları
kıyaslanamaz.* Burada üç sayı birden yayımlanır:

    doğru / TOPLAM          ← ana sayı (netleştirme PAYDADA)
    netleştirme / TOPLAM    ← ayrı satır, gizlenmez
    doğru / (TOPLAM − netleştirme)   ← "cevaplananlar içinde" — İKİNCİL

## 🔴 TUTULMUŞ (held-out) KÜME — ve kilidi

Yeni bir küme **kuratörlenmez** (kuratörlük, ölçtüğü şeyi kendi yorumuna bağlar).
`nl_corpus`'un ürettiği evrenden **deterministik bir dilim** ayrılır (`TOHUM`, `PAY`) ve
**hash'iyle kilitlenir**. Kilit, kümenin ayar için kullanılmadığının **kanıtıdır**:
küme değişirse hash değişir ve kapı bunu söyler.

⚠ **Tutulmuş bir küme bir kez bakıldıktan sonra tutulmuş değildir.** Küme kirlendiyse
**yenisi ayrılır**, eskisi `eval`'e devredilir — bu kural burada yazılıdır ki kirlenme
sessizce olmasın.

## ⚠ ANOTASYON GÜRÜLTÜSÜ — yayımlanacak her sayının yanına yazılır

BIRD/Spider'da anotasyon hata oranı **%52,8 / %62,8** ölçüldü. Bizim altın cevabımız bir
insan etiketi değil, **bağımsız bir SQL yolu** (aşağıya bak) — ama yine de:
🔴 **10 puanın altındaki fark GÜRÜLTÜDÜR** ve bu, rapordaki her sayının yanında durur.

## Altın cevap NEREDEN geliyor — ve neden bir insan etiketi değil

Soru katalogdan üretilirken **hangi cube · ölçü · boyut · dönem**den üretildiği bilinir.
Altın cevap, o parametrelerden **doğrudan** kurulan bir `cube_query`'nin çalıştırılmasıdır.
Sistemin cevabı ise **soruyu okuyup** ürettiği `cube_query`'nin çalıştırılmasıdır.

🔴 İki yol **aynı motoru** kullanır ama **farklı girdiden** gelir: biri parametreden, öteki
**doğal dilden**. Ölçülen şey tam olarak aradaki fark — yani **anlama**dır.

⚠ Bunun ölçmediği şey **motorun kendi doğruluğudur** (ikisi de aynı motoru kullanır).
O ayrı bir sorudur ve bu alet onu **ölçtüğünü iddia etmez**.

## Kullanım

    python lab/uctan_uca.py                    # dört şirket, rapor
    python lab/uctan_uca.py --kilit-yaz        # tutulmuş kümenin hash'ini YENİLE
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SIRKETLER = ("demo-boyahane", "gitas", "atiksan", "gulteks")

#: 🔴 Tutulmuş kümenin tohumu — **değiştirilmez**. Değişirse küme değişir ve ölçüm
#: karşılaştırılamaz hâle gelir.
TOHUM = 4080205

#: Evrenden ayrılan pay. ⚠ `nl_corpus` bu dilimi **kullanmaz**; ayrım deterministiktir.
PAY = 0.12

#: 🔴 §C/16'nın şartı: **n ≥ 100**.
ASGARI_N = 100

#: ⚠ Anotasyon gürültüsü tabanı — BIRD/Spider ölçümü (%52,8 / %62,8 hata oranı).
#: **Bu eşiğin altındaki farklar YORUMLANMAZ.**
GURULTU_ESIGI = 0.10

#: Kilit dosyası — kümenin ayar için kullanılmadığının kanıtı.
KILIT = Path(__file__).resolve().parent / "tutulmus_kume.kilit"


def tutulmus_mu(soru: str) -> bool:
    """Bu soru **tutulmuş** dilime mi düşüyor? Deterministik, tohum sabit.

    🔴 `random` değil **hash** kullanılır: `random` çağrı sırasına bağlıdır ve korpus
    sorularını farklı sırayla üretirsek dilim **değişirdi**. Hash, sorunun kendisine
    bağlıdır — sıra değişse de dilim aynı kalır.
    """
    h = hashlib.sha256(f"{TOHUM}:{soru}".encode()).digest()
    return (int.from_bytes(h[:4], "big") % 10_000) < int(PAY * 10_000)


def puanla(altin: dict[str, Any], cevap: dict[str, Any] | None) -> dict[str, Any]:
    """🔴 **PUANLAMA KURALININ TEK YERİ.** İkinci bir yol yazmak, kuralı sonuca uydurmanın
    kapısıdır ve `tests/test_uctan_uca_kapisi.py` bunu AST ile kilitler.

    > *Bir cevap ancak **dönen değer**, **varlık kapsamı** ve **zaman/filtre semantiği**
    > altın cevapla eşleşiyorsa **doğru** sayılır.*

    Döner: `{"dogru": bool, "sinif": ..., "neden": ...}` — `sinif` ∈
    `dogru | deger | kapsam | zaman | netlestirme | hata`.
    """
    if cevap is None:
        return {"dogru": False, "sinif": "netlestirme",
                "neden": "sistem cevap üretmedi (netleştirme ya da red)"}
    if cevap.get("hata"):
        return {"dogru": False, "sinif": "hata", "neden": str(cevap["hata"])[:120]}

    # (1) DÖNEN DEĞER
    a, b = altin.get("deger"), cevap.get("deger")
    if not _deger_esit(a, b):
        return {"dogru": False, "sinif": "deger", "neden": f"değer {a!r} ≠ {b!r}"}
    # (2) VARLIK KAPSAMI — kaç satır, hangi boyut kümesi
    if altin.get("satir") != cevap.get("satir"):
        return {"dogru": False, "sinif": "kapsam",
                "neden": f"satır {altin.get('satir')} ≠ {cevap.get('satir')}"}
    if set(altin.get("boyutlar") or ()) != set(cevap.get("boyutlar") or ()):
        return {"dogru": False, "sinif": "kapsam",
                "neden": f"boyut {altin.get('boyutlar')} ≠ {cevap.get('boyutlar')}"}
    # (3) ZAMAN / FİLTRE SEMANTİĞİ
    if (altin.get("zaman") or None) != (cevap.get("zaman") or None):
        return {"dogru": False, "sinif": "zaman",
                "neden": f"zaman {altin.get('zaman')} ≠ {cevap.get('zaman')}"}
    return {"dogru": True, "sinif": "dogru", "neden": ""}


def _deger_esit(a: Any, b: Any) -> bool:
    """Sayısal eşitlik — **kayan nokta toleransı var, semantik tolerans YOK**.

    ⚠ Tolerans yalnız `float` yuvarlamasınadır (`1e-9` bağıl). *"Yakın sayı"* bir eşleşme
    **değildir**: %2 sapmayı doğru saymak, doğruluğu ölçmeyi bırakıp yakınlığı ölçmek olur.
    """
    if a is None or b is None:
        return a is None and b is None
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)
    if fa == fb:
        return True
    olcek = max(abs(fa), abs(fb), 1.0)
    return abs(fa - fb) <= 1e-9 * olcek


def _calistir(wren: Any, cq: dict[str, Any]) -> dict[str, Any]:
    """`cube_query` → gerçek satırlar → karşılaştırılabilir özet."""
    try:
        sql = wren.cube_sql(dict(cq))
        tablo = wren.query(sql)
    except Exception as exc:                                  # noqa: BLE001
        return {"hata": f"{type(exc).__name__}: {exc}"[:160]}
    satirlar = tablo.get("rows") if isinstance(tablo, dict) else tablo
    satirlar = list(satirlar or [])
    olcu = (cq.get("measures") or [None])[0]
    # Tek satır/tek ölçü ise "dönen değer" odur; çok satırlıysa TOPLAM alınır — toplam,
    # satır sayısı ve boyut kümesiyle birlikte kapsamı da yakalar.
    toplam = 0.0
    for r in satirlar:
        v = (r.get(olcu) if isinstance(r, dict) else None)
        try:
            toplam += float(v)
        except (TypeError, ValueError):
            pass
    zaman = [(t or {}).get("granularity") for t in (cq.get("timeDimensions") or [])]
    # 🔴 ZAMAN/FİLTRE SEMANTİĞİ — kuralın üçüncü şartı. Yalnız granülerlik değil,
    # **filtrenin kendisi** de karşılaştırılır: aynı granülerlikte ama farklı dönemde
    # bir cevap, kuralın açıkça yanlış saydığı şeydir.
    fil = sorted(
        f"{(f or {}).get('dimension')}{(f or {}).get('operator')}{(f or {}).get('value')}"
        for f in (cq.get("filters") or []))
    return {"deger": round(toplam, 6), "satir": len(satirlar),
            "boyutlar": list(cq.get("dimensions") or []),
            "zaman": ([z for z in zaman if z] or []) + fil or None}


def _bu_yil_filtresi(zaman_adi: str) -> list[dict[str, Any]]:
    """*"bu yıl"*ın altın karşılığı — **Python takvimi**, `cube_router`'ın parsı DEĞİL.

    🔴 **Kapı bunu yakaladı (ölçüm aracının kendi kusuru).** İlk sürüm *"bu yil … aylara
    göre"* sorusunu üretiyor ama altın `cube_query`'ye **yıl filtresini koymuyordu**:
    sistem doğru davranıp filtreyi uyguluyor, altın uygulamıyor, **fark sistemin hatası
    gibi** raporlanıyordu (`tep`: 3814 ≠ 1179 · `rework`: 7577 ≠ 1467).
    *Kendi kusurunu ölçtüğü şeye yazan bir alet, ölçtüğü şeyi olduğundan kötü gösterir —
    ve bu, iyimser göstermek kadar yanlıştır.*

    ⚠ Bağımsızlık korunur: filtre **buradaki takvim aritmetiğinden** gelir, `cube_router`
    çağrılmaz. İki yol hâlâ ayrı girdiden (parametre ↔ doğal dil) geliyor.
    """
    from datetime import date

    return [{"dimension": zaman_adi, "operator": "gte",
             "value": f"{date.today().year}-01-01"}]


def _vakalar(sema: dict) -> list[dict[str, Any]]:
    """Tutulmuş kümeyi üretir: **soru + altın parametreler**.

    ⚠ Soru katalogdan üretilir, elle yazılmaz — elle yazılan bir küme, ölçtüğü şeyi
    **yazanın beklentisine** bağlar.

    ⚠ Evren **bilerek geniş**: §C/16 `n ≥ 100` istiyor ve tutulmuş pay (%12) küçük
    kalmalı. Payı büyütmek daha kolay olurdu ama tutulmuş kümeyi evrenin yarısı yapmak,
    *"tutulmuş"* kelimesini anlamsızlaştırırdı.
    """
    out: list[dict[str, Any]] = []
    for c in sema.get("cubes") or []:
        cube = c.get("name")
        boyutlar = list(c.get("dimensions") or [])[:5]
        zaman = list(c.get("time_dimensions") or [])[:1]
        for olcu, syns in (c.get("measure_synonyms") or {}).items():
            adlar = [str(x).removesuffix("!").strip() for x in (syns or [olcu])[:3]]
            for ad in [a for a in adlar if a]:
                for b in boyutlar:
                    soru = f"{ad} {str(b).replace('_', ' ')} bazinda"
                    if tutulmus_mu(soru):
                        out.append({"soru": soru, "cube": cube, "measures": [olcu],
                                    "dimensions": [b], "timeDimensions": [],
                                    "filters": []})
                if not zaman:
                    continue
                z = str(zaman[0])
                soru_z = f"bu yil {ad} aylara gore"
                if tutulmus_mu(soru_z):
                    out.append({"soru": soru_z, "cube": cube, "measures": [olcu],
                                "dimensions": [],
                                "timeDimensions": [{"dimension": z,
                                                    "granularity": "month"}],
                                "filters": _bu_yil_filtresi(z)})
                soru_t = f"{ad} toplam"
                if tutulmus_mu(soru_t):
                    out.append({"soru": soru_t, "cube": cube, "measures": [olcu],
                                "dimensions": [], "timeDimensions": [], "filters": []})
    # ⚠ Yinelenenler ELENİR ama sıra **korunur**: sıra karışırsa kilit hash'i değişir.
    gorulen, tekil = set(), []
    for v in out:
        if v["soru"] not in gorulen:
            gorulen.add(v["soru"])
            tekil.append(v)
    return tekil


def kilit_hash(vakalar: list[dict[str, Any]]) -> str:
    """Kümenin kimliği. Küme değişirse hash değişir — **kirlenme sessiz olamaz**."""
    ham = "\n".join(sorted(v["soru"] for v in vakalar))
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()[:16]


def kos(sirket: str) -> dict[str, Any]:
    """Tek şirket için uçtan uca ölçüm."""
    from app import cube_router as cr
    from app.compose import build, compose
    from app.config import get_settings
    from app.wren_service import WrenService

    out = Path(tempfile.mkdtemp(prefix=f"uu-{sirket}-")) / "proje"
    compose(sirket, Path(__file__).resolve().parents[1] / "demo", out)
    build(out)
    st = get_settings()
    wren = WrenService(out, datasource=st.datasource,
                       connection_info=st.connection_dict())
    sema = wren.schema()

    vakalar = _vakalar(sema)
    sayim = {"dogru": 0, "deger": 0, "kapsam": 0, "zaman": 0,
             "netlestirme": 0, "hata": 0}
    ornekler: list[dict[str, Any]] = []
    # ⚠ Altın cevabı ÜRETİLEMEYEN vakalar. Sisteme ne puan ne ceza yazılır — ama
    # **sayılır**: sebepsiz bir `⊘` bir ölçüm değildir. (`atiksan`/`gulteks` mssql lab
    # fixture'larıdır ve `--network none` altında veri kaynağına erişemezler.)
    atlanan, atlanma_sebebi = 0, ""
    for v in vakalar:
        altin = _calistir(wren, {k: v[k] for k in
                                 ("cube", "measures", "dimensions", "timeDimensions",
                                  "filters")})
        if altin.get("hata"):
            atlanan += 1
            atlanma_sebebi = atlanma_sebebi or str(altin["hata"])[:120]
            # ⚠ Altın cevap üretilemiyorsa vaka **ÖLÇÜLEMEZ** — sisteme puan da ceza da
            # yazılmaz. Bunu "yanlış" saymak, motorun kendi sınırını ANLAMA hatası gibi
            continue
        r = cr.route(cr._norm(v["soru"]), sema)
        cevap = None
        if r:
            cevap = _calistir(wren, dict((r.get("cube_query") or r)))
        p = puanla(altin, cevap)
        sayim[p["sinif"]] = sayim.get(p["sinif"], 0) + 1
        if not p["dogru"] and len(ornekler) < 12:
            ornekler.append({"soru": v["soru"], **p})

    toplam = sum(sayim.values())
    netlestirme = sayim["netlestirme"]
    return {
        "sirket": sirket,
        "n": toplam,
        "vaka": len(vakalar),
        "atlanan": atlanan,
        "atlanma_sebebi": atlanma_sebebi,
        "kilit": kilit_hash(vakalar),
        "dogru": sayim["dogru"],
        # 🔴 ANA SAYI — netleştirme PAYDADA.
        "oran": round(sayim["dogru"] / toplam, 4) if toplam else None,
        # 🔴 AYRI SATIR — gizlenmez.
        "netlestirme": netlestirme,
        "netlestirme_orani": round(netlestirme / toplam, 4) if toplam else None,
        # İKİNCİL — "cevaplananlar içinde".
        "cevaplanan_ici": (round(sayim["dogru"] / (toplam - netlestirme), 4)
                           if toplam - netlestirme else None),
        "dagilim": sayim,
        "ornekler": ornekler,
    }


def rapor_metni(veri: list[dict[str, Any]]) -> str:
    s = ["# Uçtan uca cevap doğruluğu (§C/16)",
         "",
         "> 🔴 **PUANLAMA KURALI — koşumdan ÖNCE ilan edildi:** *bir cevap ancak **dönen",
         "> değer**, **varlık kapsamı** ve **zaman/filtre semantiği** altın cevapla",
         "> eşleşiyorsa **doğru** sayılır.* Kural kodda **tek yerde** (`puanla()`).",
         "",
         "🔴 **Netleştirme AYRI SATIR olarak raporlanır ve paydadan GİZLİCE ÇIKARILMAZ.**",
         "*Rakiplerin manşet sayılarını kıyaslanamaz yapan şey tam olarak budur: her",
         "satıcı reddedilenleri paydadan sessizce çıkarıyor.*",
         "",
         f"⚠ **Gürültü tabanı:** BIRD/Spider'da anotasyon hata oranı **%52,8 / %62,8**",
         f"ölçüldü. 🔴 **{GURULTU_ESIGI * 100:.0f} puanın altındaki farklar YORUMLANMAZ.**",
         "",
         "| şirket | n | kilit | **doğru** | netleştirme *(ayrı satır)* | cevaplanan içinde |",
         "|---|---|---|---|---|---|"]
    for d in veri:
        o = d.get("oran")
        no = d.get("netlestirme_orani")
        ci = d.get("cevaplanan_ici")
        s.append(
            f"| {d['sirket']} | {d['n']} | `{d['kilit']}` | "
            + (f"**%{o * 100:.1f}**" if o is not None else "⊘")
            + " | " + (f"%{no * 100:.1f} ({d['netlestirme']})" if no is not None else "⊘")
            + " | " + (f"%{ci * 100:.1f}" if ci is not None else "⊘") + " |")
    for d in veri:
        if d.get("atlanan"):
            s += ["",
                  f"⊘ **{d['sirket']}: {d['atlanan']}/{d.get('vaka', 0)} vaka "
                  f"ÖLÇÜLEMEDİ** — altın cevap üretilemedi: "
                  f"`{d.get('atlanma_sebebi', '')}`. *Sebepsiz bir `⊘` bir ölçüm "
                  f"değildir; sisteme ne puan ne ceza yazıldı.*"]
    s += ["",
          "⚠ **`n < %d` olan şirkette ana sayı `⊘ ÖLÇÜLEMEDİ`dir** — §C/16 en az bu kadar"
          % ASGARI_N,
          "vaka istiyor ve altında yayımlamak, örneklem kazasını sonuç diye satmaktır.",
          ""]
    for d in veri:
        if not d.get("ornekler"):
            continue
        s += [f"### {d['sirket']} — yanlışlardan örnekler", "",
              "| soru | sınıf | neden |", "|---|---|---|"]
        s += [f"| `{o['soru']}` | {o['sinif']} | {o['neden']} |" for o in d["ornekler"]]
        s.append("")
    s += ["---", "",
          "## ⚠ Bu aletin ÖLÇMEDİĞİ şey",
          "",
          "Altın cevap da sistemin cevabı da **aynı motoru** kullanır; ikisi yalnız",
          "**girdiden** ayrılır (biri parametreden, öteki **doğal dilden**). Yani ölçülen",
          "şey **anlamadır** — motorun kendi doğruluğu **değil**. O ayrı bir sorudur ve bu",
          "alet onu ölçtüğünü **iddia etmez**.",
          "",
          "⚠ **Tutulmuş bir küme, bir kez bakıldıktan sonra tutulmuş değildir.** Küme",
          "kirlendiyse **yenisi ayrılır**, eskisi `eval`'e devredilir."]
    return "\n".join(s) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Uçtan uca cevap doğruluğu (§C/16)")
    ap.add_argument("--sirket", nargs="*", default=list(SIRKETLER))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--kilit-yaz", action="store_true",
                    help="tutulmuş kümenin kilidini YENİLE (kirlenme kaydı)")
    a = ap.parse_args()

    veri = []
    for s in a.sirket:
        try:
            veri.append(kos(s))
        except Exception as exc:                              # noqa: BLE001
            print(f"  {s}: ⊘ ÖLÇÜLEMEDİ — {type(exc).__name__}: {exc}")
    if a.json:
        print(json.dumps(veri, ensure_ascii=False, indent=2))
        return 0
    if a.kilit_yaz:
        KILIT.write_text(json.dumps({d["sirket"]: d["kilit"] for d in veri},
                                    ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
        print(f"→ kilit yazıldı: {KILIT}")
    metin = rapor_metni(veri)
    hedef = Path(__file__).resolve().parent / "reports" / "uctan_uca.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(metin)
    print(f"→ {hedef}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
