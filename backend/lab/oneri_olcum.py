#!/usr/bin/env python3
"""🔴🔴 `FAZ 0` — **ÖLÜM ŞARTI ÖLÇÜMÜ: Türkçe kısa alan adlarında gömme isabeti.**

## Neden bu koşucu var — ve neden ÖNCE o

`belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md §13.1`, öneri katmanının tamamını
**tek bir ölçüme** bağlıyor:

| `Recall@3` | karar |
|---|---|
| **≥ %85** | 🟢 devam — tıklama→etiket→sözlük döngüsü kapanır |
| %70–85 | ◐ sinonim desteğiyle devam, kapsam **dar** |
| **< %70** | 🔴 **DUR** — sinonim tredmill'i geri gelir, `§3`–`§14` uygulanmaz |

⚠ Ve literatür bunu **cevaplamıyor**: beş model kartının hiçbirinde **tek kelimelik /
`snake_case` alan adı** performansı hakkında ölçüm yok. Yani bu sayı **okunarak** değil
yalnız **koşularak** öğrenilebilir.

> *Bir planın ölüm şartı ölçülmeden yazılan her satır, bir varsayımın üstüne inşa edilir.*

## Ne ölçer — ve neyi ölçMEZ

**Ölçer:** *«kullanıcının iş dilindeki ifadesi, katalogdaki doğru ölçüyü ilk N adayda
getiriyor mu»* — `Recall@1/3/5` + `MRR`.

**Ölçmez:** kabul oranı (`§13.2`, kullanıcı gerektirir) · gecikme (ayrı ölçüm) ·
sessiz-yanlışın gerçekten azalması (korpus `@1`/`@3` gerektirir). Bu koşucu **tek bir
soruyu** cevaplar ve fazlasını iddia etmez 🆆.

## Üç yol birden ölçülür — çünkü marjinal katkı asıl karardır

```
LEKSİK   difflib oranı (bugün zaten var: cube_router `_TYPO_*` yolu)
VEKTÖR   multilingual-e5-large (fastembed/ONNX, önbellekten AĞSIZ)
BİRLEŞİK max(leksik, vektör) — basit füzyon
```

🔴 **Asıl karar sayısı `VEKTÖR − LEKSİK` farkıdır.** Vektör leksikten belirgin biçimde
iyi değilse öneri katmanı bir **gömme altyapısı** taşımayı hak etmez: aynı işi bugünkü
`difflib` yolu zaten yapıyordur. *Bir bileşeni eklemenin gerekçesi, onsuz ölçülen
sayıdır.*

## `E-8` KORUNUR

Çevrimdışı ölçüm: `/ask` yolundan tetiklenmez, sıcak yola hiçbir şey eklemez.

## Kullanım

    python lab/oneri_olcum.py                 # kuru: vaka sayısı + leksik taban, GÖMME YOK
    python lab/oneri_olcum.py --vektor        # gömmeyi de koş (önbellek gerekir)
    python lab/oneri_olcum.py --vektor --json lab/reports/oneri_olcum.json
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
import unicodedata
from pathlib import Path

#: 🔴 `§13.1` eşikleri — **karar burada yazılı**, koşanın yorumuna bırakılmaz.
ESIK_YESIL = 85.0
ESIK_SARI = 70.0

#: E5 **simetrik** görevde iki tarafa da `query:` ister (model kartı). Asimetrik
#: (`query:`/`passage:`) ayrımı bizim görevimiz için **yanlış** olurdu: kullanıcı ifadesi
#: ile ölçü adı iki *soru* değil, iki *isim*dir.
ONEK = "query: "

#: Aday havuzunda bir ölçünün kaç görünümü var — ad · etiket · sinonimler. En iyi
#: görünümün skoru ölçünün skoru sayılır (kullanıcı hangi görünümü yazdıysa o).
#: ⚠ Bu bir **tercih** değil ölçütün tanımı: bir ölçü, adıyla da etiketiyle de
#: sinonimiyle de bulunabilmelidir.


def _norm(s: str) -> str:
    """Küçült + aksan/şapka düşür — leksik yolun `cube_router` ile aynı zemini."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return (s.replace("ı", "i").replace("ş", "s").replace("ğ", "g")
             .replace("ü", "u").replace("ö", "o").replace("ç", "c").strip())


def gorunumler(schema: dict) -> dict[str, list[str]]:
    """`{"cube.olcu": [ad, etiket, sinonim…]}` — **ÇOK GÖRÜNÜMLÜ** aday havuzu (`0.1`)."""
    out: dict[str, list[str]] = {}
    for c in (schema or {}).get("cubes") or []:
        cad = str(c.get("name") or "")
        disp = c.get("measure_synonyms_display") or {}
        syn = c.get("measure_synonyms") or {}
        for m in c.get("measures") or []:
            ad = m if isinstance(m, str) else (m or {}).get("name")
            if not ad:
                continue
            g = [str(ad).replace("_", " ")]
            if disp.get(ad):
                g.append(str(disp[ad]))
            g += [str(x) for x in (syn.get(ad) or [])]
            out[f"{cad}.{ad}"] = list(dict.fromkeys(g))
    return out


#: 🔴 `0.2` — **GERÇEK İŞ İFADELERİ.** Kural: her ifade katalogdan **türetilmiş** bir
#: hedefe bağlanır (`kimlik` gerçek bir `cube.olcu`'dur, uydurulmaz ㊱); ifadenin
#: kendisi ise **kullanıcının ağzından** yazılır — katalog kelimesi kopyalanmaz, yoksa
#: ölçüm kendi cevabını sınar.
#:
#: ⚠ Dört zorluk sınıfı **bilerek** karışık: düz · yazım hatalı · karışık dil · dolaylı.
#:
#: 🔴 **HEDEF BİR KÜMEDİR, tek ad değil** — ve bu bir kolaylık değil bir **doğruluk**
#: şartı. Ölçüldü: *«fire»* hem `parti.toplam_fire_kg` hem `oee.toplam_fire_kg` altında
#: tanımlı. Tek ad beklenirse ölçüm, **doğru** bir cevabı yanlış sayar ve gömmeyi
#: haksız yere cezalandırır. 🆗 *Cevabı belirsiz bir girdiyle bir ölçüt sınanmaz —
#: sınanacaksa belirsizlik ölçüte YAZILIR.*
VAKALAR: list[tuple[str, tuple[str, ...], str]] = [
    # (ifade, kabul edilen cube.olcu KÜMESİ, sınıf)
    ("hasılat", ("parti.toplam_ciro",), "duz"),
    ("ciro", ("parti.toplam_ciro",), "duz"),
    ("kaç kilo fire verdik", ("parti.toplam_fire_kg", "oee.toplam_fire_kg"), "dolayli"),
    ("fire", ("parti.toplam_fire_kg", "oee.toplam_fire_kg"), "duz"),
    ("fire oranı", ("parti.fire_orani_yuzde",), "duz"),
    ("arıza sayısı", ("bakim.ariza_sayisi",), "duz"),
    ("kaç arıza oldu", ("bakim.ariza_sayisi",), "dolayli"),
    ("arıza duruşu", ("bakim.toplam_durus_dakika", "oee.plansiz_durus_dakika"), "duz"),
    ("mttr", ("bakim.ort_durus_dakika",), "karisik"),
    ("ortalama duruş", ("bakim.ort_durus_dakika",), "duz"),
    ("yedek parça maliyeti", ("bakim.toplam_yedek_parca_maliyet",), "duz"),
    ("iş emri adedi", ("bakim_is_emri.is_emri_adedi",), "duz"),
    ("bakım süresi", ("bakim_is_emri.toplam_bakim_suresi",), "duz"),
    ("vardya", (), "yazim"),
    ("firee", ("parti.toplam_fire_kg", "oee.toplam_fire_kg"), "yazim"),
    ("hasıl", ("parti.toplam_ciro",), "yazim"),
    ("arıza sayisi", ("bakim.ariza_sayisi",), "yazim"),
    ("downtime", ("bakim.toplam_durus_dakika", "oee.toplam_durus_dakika"), "karisik"),
    ("oee", ("oee.ort_oee",), "duz"),
    ("makine verimliliği", ("oee.ort_oee",), "dolayli"),
]

#: ⚠ `vardya` bir **gürültü** vakasıdır: kataloğa karşılığı olmayan bir kelime. Doğru
#: davranış onu **bulmamak**; bu yüzden aşağıda `GURULTU` ile işaretlenir ve `Recall`
#: paydasından **çıkarılır** — ama *«yanlış eşleşti mi»* diye **ayrıca** raporlanır.
#: 🅜 Payda kutsaldır: bir gürültü vakasını başarı paydasına koymak oranı şişirir.
GURULTU = {"vardya"}


def _leksik(ifade: str, havuz: dict[str, list[str]]) -> list[tuple[float, str]]:
    n = _norm(ifade)
    out = []
    for kimlik, gs in havuz.items():
        en = max((difflib.SequenceMatcher(None, n, _norm(g)).ratio() for g in gs),
                 default=0.0)
        out.append((en, kimlik))
    return sorted(out, reverse=True)


def _vektor(ifadeler: list[str], havuz: dict[str, list[str]]):
    """→ `{ifade: [(skor, kimlik)…]}`; model yoksa `None` (kuru mod)."""
    try:
        from fastembed import TextEmbedding
    except Exception:                                  # noqa: BLE001
        return None
    try:
        model = TextEmbedding("intfloat/multilingual-e5-large",
                              cache_dir="/tmp/fastembed_cache")
    except Exception as exc:                           # noqa: BLE001
        print(f"⊘ gömme modeli yüklenemedi: {exc}", file=sys.stderr)
        return None

    duz, sahip = [], []
    for kimlik, gs in havuz.items():
        for g in gs:
            duz.append(ONEK + g)
            sahip.append(kimlik)
    dv = list(model.embed(duz))
    qv = list(model.embed([ONEK + i for i in ifadeler]))

    def kos(a, b):
        s = sum(x * y for x, y in zip(a, b, strict=True))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        return s / (na * nb) if na and nb else 0.0

    out = {}
    for ifade, q in zip(ifadeler, qv, strict=True):
        en: dict[str, float] = {}
        for v, kimlik in zip(dv, sahip, strict=True):
            sk = kos(q, v)
            if sk > en.get(kimlik, -1.0):
                en[kimlik] = sk
        out[ifade] = sorted(((s, k) for k, s in en.items()), reverse=True)
    return out


def _metrik(siralar: list[int | None]) -> dict:
    """`Recall@1/3/5` + `MRR`. `None` = hedef listede hiç yok."""
    n = len(siralar) or 1
    r = {f"recall@{k}": round(100.0 * sum(1 for s in siralar if s is not None and s <= k) / n, 1)
         for k in (1, 3, 5)}
    r["mrr"] = round(sum(1.0 / s for s in siralar if s) / n, 3)
    r["payda"] = len(siralar)
    return r


def kos(*, vektor: bool = False) -> dict:
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    w = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                    connection_info=s.connection_dict())
    havuz = gorunumler(w.schema())

    olculur = [(i, h) for i, h, _s in VAKALAR if i not in GURULTU]
    gurultu = [i for i, _h, _s in VAKALAR if i in GURULTU]
    rapor: dict = {"olcu": len(havuz), "gorunum": sum(len(v) for v in havuz.values()),
                   "vaka": len(olculur), "gurultu": len(gurultu), "kuru": not vektor}

    def siralar(sirali_fn) -> list[int | None]:
        out = []
        for ifade, hedef in olculur:
            sirali = sirali_fn(ifade)
            yer = next((i + 1 for i, (_s, k) in enumerate(sirali) if k in hedef), None)
            out.append(yer)
        return out

    rapor["leksik"] = _metrik(siralar(lambda i: _leksik(i, havuz)))

    if vektor:
        vek = _vektor([i for i, _h in olculur] + gurultu, havuz)
        if vek is None:
            rapor["vektor"] = {"hata": "model yüklenemedi"}
        else:
            rapor["vektor"] = _metrik(siralar(lambda i: vek[i]))
            rapor["birlesik"] = _metrik(siralar(
                lambda i: sorted(_birlestir(_leksik(i, havuz), vek[i]), reverse=True)))
            # 🔴 Gürültü vakası: doğru davranış **bulmamak**. En iyi skoru raporla ki
            # bir eşik konabilsin — ama Recall paydasına **girmesin** 🅜.
            rapor["gurultu_en_iyi"] = {g: round(vek[g][0][0], 3) for g in gurultu if g in vek}
    return rapor


def _birlestir(a: list[tuple[float, str]], b: list[tuple[float, str]]):
    """`max(leksik, vektör)` — en basit füzyon. ⚠ RRF gibi bir şey **denenmedi**;
    amaç en iyi füzyonu bulmak değil, **vektörün marjinal katkısını** görmek."""
    d = {k: s for s, k in a}
    for s, k in b:
        if s > d.get(k, -1.0):
            d[k] = s
    return [(s, k) for k, s in d.items()]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="FAZ 0 — Türkçe gömme isabeti (§13.1)")
    p.add_argument("--vektor", action="store_true", help="gömmeyi de koş (varsayılan: kuru)")
    p.add_argument("--json", default=None, help="raporu bu dosyaya yaz")
    a = p.parse_args(argv)
    r = kos(vektor=a.vektor)
    print(json.dumps(r, ensure_ascii=False, indent=2))

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")

    if r["kuru"]:
        print(f"\n⊙ KURU MOD — gömme çağrılmadı. Ölçülebilir vaka: {r['vaka']} "
              f"(+{r['gurultu']} gürültü). Gerçek ölçüm için `--vektor`.", file=sys.stderr)
        return 0

    v = (r.get("vektor") or {}).get("recall@3")
    if v is None:
        return 1
    karar = ("🟢 DEVAM" if v >= ESIK_YESIL else
             "◐ DAR KAPSAM" if v >= ESIK_SARI else "🔴 DUR — plan §3–§14 UYGULANMAZ")
    print(f"\n§13.1 KARARI: Recall@3 = %{v} → {karar}", file=sys.stderr)
    return 0


if __name__ == "__main__":                             # pragma: no cover
    raise SystemExit(main())
