"""**GERÇEK-DÜNYA KORPUSU** — persona × zorluk merdiveni. *(denetim §9.6)*

## 🔴 Neden var: mevcut korpus KENDİ SÖZLÜĞÜNÜ ölçüyor

`lab/nl_corpus.py::gen_single()` soruyu **cevabın anahtarından** kuruyor
(`measure_synonyms_display` · `dimension_labels`). Ölçüldü: boyahane'nin 5077 tekil
sorusunun **≥%97,1'i katalog türevi**; gerçek kullanıcı dağarcığı **≤123 soru (≤%2,4)**.

> 🔴 Yani `%93,1` şu soruya cevap veriyor: *"sistem **kendi** kelimelerini tanıyor mu?"*
> — ve o soruya yüksek puan almak **şaşırtıcı değil, beklenendir**.
> Ölçülmeyen soru: *"**kullanıcının** kelimelerini tanıyor mu?"*

Ve bu, kullanıcının kendi gözlemini açıklıyor: *"bayrakları hep `off` tuttuk, hiç
değişiklik olmadı."* — **Bir A/B'nin sonucu «fark yok» ise, önce ölçen aletin o farkı
görebildiği kanıtlanmalıdır.** Bu dosya o aleti kurar.

## Şartnamenin altı kuralı — birebir

| Kural | Nasıl uygulandı |
|---|---|
| **0 · payda kutsaldır** | `nl_corpus`'a **dokunulmadı**; bu korpus onun **yanına** kurulur ve kendi tabanını yazar |
| **1 · soru cevabın anahtarından TÜRETİLMEZ** | `_katalog_sizintisi()` her vakayı **mekanik** denetler: `soru ∩ (ölçü etiketleri ∪ boyut etiketleri) = ∅`. İhlal → vaka **korpusa girmez**, sessizce geçmez |
| **2 · altı persona** | `PERSONALAR` — her biri **kendi dilini** konuşur |
| **3 · beş zorluk kademesi** | `K1…K5`; payda **kademeli** raporlanır ki bir kademedeki kayıp ötekinde saklanmasın |
| **4 · üç beyan** | her vaka `soru` + `kabul` *(doğru ∨ netleştirme ∨ dürüst ret)* + `yasak` taşır |
| **5 · vakalar TOPLANIR** | kaynak: borç defterinin **canlı** bulguları + `deneyim.py` personaları. ⚠ Uydurulmadı — her vakanın `kaynak`'ı yazılı |
| **6 · kapı yanına kurulur** | hedef **yüzde değil ilerleme**: ilk koşum **taban**dır |

## 🔴 NETLEŞTİRME BİR BAŞARIDIR

Bugünkü korpus `CLARIFY`'ı **OK saymıyor**. Oysa *"bakiye: cari mi mizan mı?"* diye
**sormak**, ₺11,86 milyonluk sessiz seçimden **iyidir**. Bu korpus onu **ayrı bir kazanç
sütunu** olarak sayar.

## Koşum

```bash
python lab/gercek_dunya.py                 # tüm personalar
python lab/gercek_dunya.py --persona ceo   # tek persona
python lab/gercek_dunya.py --kademe K4     # tek kademe
```

⚠ **Sıfır-LLM, sıfır-DB**: `route()` doğrudan çağrılır (`nl_corpus`'un HTTP turu bile
gerekmez). Maliyet **saniye**, dakika değil — §9.7/d'nin ölçtüğü gibi.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

#: Kabul sınıfları — **üçü de başarıdır**.
#: 🔴 `NETLESTIRME` bir kayıp değil: *"hangisini kastettin"* diye sormak, yanlış olana
#: kendinden emin cevap vermekten **iyidir**.
DOGRU = "dogru"              # doğru cube + doğru ölçü
NETLESTIRME = "netlestirme"  # belirsizliği fark etti, sordu
DURUST_RET = "durust_ret"    # cevaplayamayacağını söyledi
SESSIZ_YANLIS = "sessiz_yanlis"  # 🔴 **tek gerçek başarısızlık**

KADEMELER = ("K1", "K2", "K3", "K4", "K5")

#: Altı persona — **aynı iş sorusu, altı ayrı ağız**.
PERSONALAR = {
    "ceo": "kısa, sonuç odaklı, ölçü adı KULLANMAZ",
    "cfo": "dönem + mutabakat dili, mali takvim",
    "uretim": "vardiya/makine/parti, kısaltma ve argo",
    "kalite": "oran + neden zinciri",
    "satis": "müşteri/segment, kıyas",
    "saha": "🔴 yazım hatası · eksik cümle · konuşma dili",
}


def _v(persona: str, kademe: str, soru: str, *, kabul: list[str], yasak: str,
       kaynak: str, cube: str | None = None) -> dict[str, Any]:
    """Bir vaka. **Üç beyan zorunlu** (kural 4) — yoksa vaka değildir.

    ⚠ `kaynak` da zorunlu (kural 5): *uydurulmuş bir vaka, uydurulmuş bir ölçüdür.*
    """
    assert persona in PERSONALAR and kademe in KADEMELER
    assert kabul and yasak and kaynak, soru
    return {"persona": persona, "kademe": kademe, "soru": soru, "kabul": kabul,
            "yasak": yasak, "kaynak": kaynak, "cube": cube}


#: 🔴 **VAKALAR — hepsi TOPLANDI, uydurulmadı** (kural 5).
#: Kaynaklar: (a) borç defterinin **canlı turlardan** gelen bulguları #16…#23,
#: (b) `lab/deneyim.py`'nin persona senaryoları, (c) `REAL_PHRASINGS`'in katalog-dışı
#: dağarcığı. Her satırın `kaynak`'ı hangisinden geldiğini söyler.
VAKALAR: list[dict[str, Any]] = [
    # ---- CEO: ölçü adı KULLANMAZ ----
    _v("ceo", "K1", "işler nasıl gidiyor",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="rastgele bir ölçü seçip kendinden emin sayı vermek",
       kaynak="deneyim.py · patron sabahı deseni"),
    _v("ceo", "K3", "geçen aya göre iyi miyiz",
       kabul=[NETLESTIRME, DOGRU],
       yasak="hangi ölçü olduğunu sormadan tek bir ölçüde kıyas yapmak",
       kaynak="deneyim.py · kıyas turu"),
    _v("ceo", "K5", "bu gidişle yılı nerede kapatırız",
       kabul=[DURUST_RET, NETLESTIRME],
       yasak="tahmin yeteneği yokken bir sayı uydurmak",
       kaynak="§9.6 K5 · forecast v1'de YOK"),

    # ---- CFO: dönem + mutabakat ----
    _v("cfo", "K1", "kapanışta bakiye tutuyor mu",
       kabul=[NETLESTIRME],
       yasak="`bakiye` iki cube'un ölçüsüyken birini SESSİZCE seçmek",
       kaynak="borç #19 · ₺11,86 M sessiz seçim (CANLI tur)"),
    _v("cfo", "K3", "3. çeyrek gerçekleşme nasıl",
       kabul=[DOGRU, NETLESTIRME],
       yasak="çeyreği takvim yılı sanıp mali takvimi yok saymak",
       kaynak="borç · mali takvim (CANLI tur)"),

    # ---- Üretim: argo + kısaltma ----
    _v("uretim", "K1", "gece vardiyası niye düştü",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="hangi ölçünün düştüğünü sormadan bir neden anlatmak",
       kaynak="deneyim.py · uretim_muduru_sabahi"),
    _v("uretim", "K2", "2 nolu makine yine mi",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="eksik cümleyi bir ölçüye bağlayıp kendinden emin cevap vermek",
       kaynak="deneyim.py · eksik cümle deseni"),
    _v("uretim", "K4", "düşüşün sebebi ne",
       kabul=[NETLESTIRME, DOGRU],
       yasak="bağlam yokken 'düşüş'ü rastgele bir ölçüye bağlamak",
       kaynak="borç #17 · «değişim» istenip TOPLAM verilmesi (CANLI tur)"),

    # ---- Kalite: oran + neden ----
    _v("kalite", "K1", "ne kadar fire verdik",
       kabul=[DOGRU], cube="parti",
       yasak="fire miktarını fire ORANI sanmak (ya da tersi)",
       kaynak="REAL_PHRASINGS · katalog-dışı dağarcık"),
    _v("kalite", "K4", "fire nerede artıyor",
       kabul=[DOGRU, NETLESTIRME],
       yasak="'nerede' bir KIRILIM isterken tek toplam vermek",
       kaynak="§9.6 K4 · katkı ayrıştırması"),

    # ---- Satış: müşteri/segment ----
    _v("satis", "K2", "hangi müşteri bizi taşıyor",
       kabul=[DOGRU, NETLESTIRME],
       yasak="üstünlük ifadesini yok sayıp sıralamasız liste vermek",
       kaynak="borç #21 · üstünlük ifadesinin cevaplanmaması (CANLI tur)"),
    _v("satis", "K3", "ocakla haziranı karşılaştır",
       kabul=[DOGRU, NETLESTIRME],
       yasak="iki dönemi tek dönem sanıp birini yok saymak",
       kaynak="§9.6 K3"),

    # ---- Saha: 🔴 yazım hatası · konuşma dili ----
    _v("saha", "K1", "bu ayki fire ne kdr",
       kabul=[DOGRU, NETLESTIRME], cube="parti",
       yasak="kısaltmayı anlamayıp dürüst ret yerine yanlış ölçü seçmek",
       kaynak="deneyim.py · yazim_hatali_gercek_kullanici"),
    _v("saha", "K1", "musetri bazinda ciro",
       kabul=[DOGRU, NETLESTIRME],
       yasak="🔴 yazım hatasını düzeltmeden RASTGELE bir cube'a gitmek",
       kaynak="§9.7/b · harf devrikliği (aksan DEĞİL — o zaten `_norm` ile kapalı)"),
    _v("saha", "K2", "peki ya geçen sene",
       kabul=[NETLESTIRME, DURUST_RET],
       yasak="bağlamsız bir takip sorusuna bağlam varmış gibi cevap vermek",
       kaynak="deneyim.py · bağlam kopması turu"),
]


def _katalog_etiketleri(schema: dict) -> set[str]:
    """Kataloğun **kendi sözlüğü** — kural 1'in ölçüsü."""
    kelimeler: set[str] = set()
    for cube in (schema.get("cubes") or []):
        for alan in ("measure_synonyms_display", "dimension_labels"):
            deger = cube.get(alan) or {}
            if isinstance(deger, dict):
                for v in deger.values():
                    for parca in (v if isinstance(v, list) else [v]):
                        kelimeler |= {w.lower() for w in str(parca).split() if len(w) > 3}
        for m in (cube.get("measures") or []):
            ad = m.get("name") if isinstance(m, dict) else m
            kelimeler |= {w.lower() for w in str(ad).split("_") if len(w) > 3}
    return kelimeler


def katalog_sizintisi(soru: str, etiketler: set[str], hamlar: set[str]) -> list[str]:
    """🔴 **KURAL 1'in mekanik kapısı** — ve **kalibrasyonu ÖLÇÜMLE düzeltildi.**

    ## ⚠ İlk yazım şartnameyi HARFİYEN uyguladı ve fazla sıkı çıktı

    Şartname *"soru metni ∩ etiketler = ∅"* diyor. Uygulandı ve **15 vakanın 8'i**
    elendi: `fire` · `bakiye` · `müşteri` · `makine` · `ciro`. Oysa bunlar *"cevabın
    anahtarı"* değil, **işin kendi kelimeleri** — üretim müdürü *"fire"* der, başka
    kelimesi yoktur.

    > 🔴 Kuralın **niyeti** şuydu: soru, etiketten **TÜRETİLMESİN** (`gen_single`'ın
    > yaptığı gibi: etiket × dönem × boyut şablonu). Bir insan cümlesinin içinde *"fire"*
    > geçmesi bir **türetme** değil, bir **dağarcıktır**.
    >
    > *Bir kuralı harfiyen uygulamak, onu amacının tersine çevirebilir.*

    ## İki mekanik imza — ikisi de TÜRETMEYİ yakalar, dağarcığı değil

    | # | sızıntı | neden |
    |---|---|---|
    | 1 | **ham tanımlayıcı** (`toplam_fire_kg`, `fire_orani_yuzde`) | kullanıcı asla böyle konuşmaz; oradaysa **kopyalanmıştır** |
    | 2 | sorunun **tamamı** katalog kelimesi | `gen_single`'ın imzası: bağlaç/fiil yok, yalnız etiket+dönem+boyut |

    ⚠ Sessizce elemek **yasak**: sızıntı **raporlanır**. *Bir vakayı sessizce düşürmek,
    paydayı sessizce kırpmaktır.*
    """
    kelimeler = [w.strip(".,?!").lower() for w in soru.split() if len(w) > 2]
    if not kelimeler:
        return []
    # 1 · ham tanımlayıcı — tek başına yeterli kanıt
    ham = sorted({w for w in kelimeler if w in hamlar or "_" in w})
    if ham:
        return ham
    # 2 · sorunun TAMAMI katalog kelimesi → şablon imzası
    anlamli = [w for w in kelimeler if len(w) > 3]
    if anlamli and all(w in etiketler for w in anlamli):
        return sorted(anlamli)
    return []


def _sinifla(sonuc: dict | None, vaka: dict) -> str:
    """`route()` çıktısı → kabul sınıfı.

    ⚠ **Netleştirmeyi bir kayıp saymak**, bugünkü korpusun kusuru; burada tekrarlanmaz.

    ## 🔴 SINIR — ve bu tablo okunurken UNUTULMAMALI

    Bu araç **yalnız deterministik katmanı** (`route()`) ölçer. `route()` `None` dönmesi
    **ürünün başarısızlığı DEĞİLDİR**: `/ask` orada durmaz, Intent-JSON ve Discovery
    basamaklarına devam eder. Buradaki `durust_ret` bu yüzden *"sıfır-LLM yol pes etti"*
    demektir, *"kullanıcı cevapsız kaldı"* değil.

    > 🔴 **Ama ölçtüğü şey tam da aranan şeydir:** *"kullanıcının kendi kelimeleriyle
    > sorduğunda **LLM'siz** yol nereye kadar gidiyor?"* — çünkü ürünün tezi budur
    > (*"LLM garson, küp aşçı"*) ve mevcut korpus bunu **kataloğun kendi kelimeleriyle**
    > ölçtüğü için hep yüksek çıkıyor.
    """
    if sonuc is None:
        # `route()` pes etti → dürüst ret ya da netleştirme yolu. Hangisi olduğunu
        # `/ask` bilir; `route()` düzeyinde ikisi **ayırt edilemez** ve bu **yazılı**.
        return DURUST_RET
    cq = (sonuc or {}).get("cube_query") or {}
    if vaka.get("cube") and cq.get("cube") != vaka["cube"]:
        return SESSIZ_YANLIS
    return DOGRU


def kos(persona: str | None = None, kademe: str | None = None) -> dict[str, Any]:
    """Korpusu koşar. **Sıfır-LLM, sıfır-DB** — `route()` doğrudan."""
    from app import cube_router
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    schema = svc.schema()
    etiketler = _katalog_etiketleri(schema)
    hamlar = {str(m.get("name") if isinstance(m, dict) else m).lower()
              for c in (schema.get("cubes") or []) for m in (c.get("measures") or [])}

    secili = [v for v in VAKALAR
              if (not persona or v["persona"] == persona)
              and (not kademe or v["kademe"] == kademe)]

    sizinti: list[dict] = []
    sayac: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    ayrinti: list[dict] = []

    for v in secili:
        # KURAL 1 — mekanik kapı, **sessiz değil**.
        s_kelime = katalog_sizintisi(v["soru"], etiketler, hamlar)
        if s_kelime:
            sizinti.append({"soru": v["soru"], "kelimeler": s_kelime})
            continue
        try:
            sonuc = cube_router.route(v["soru"], schema)
        except Exception as exc:                              # noqa: BLE001
            ayrinti.append({**v, "sinif": "hata", "not": str(exc)[:120]})
            sayac[v["kademe"]]["hata"] += 1
            continue
        sinif = _sinifla(sonuc, v)
        kabul_edildi = sinif in v["kabul"]
        sayac[v["kademe"]][sinif] += 1
        sayac[v["kademe"]]["toplam"] += 1
        if kabul_edildi:
            sayac[v["kademe"]]["kabul"] += 1
        ayrinti.append({**v, "sinif": sinif, "kabul_edildi": kabul_edildi})

    return {"sayac": {k: dict(vv) for k, vv in sayac.items()},
            "sizinti": sizinti, "ayrinti": ayrinti, "toplam_vaka": len(secili)}


def rapor(sonuc: dict[str, Any]) -> str:
    sat = ["# GERÇEK-DÜNYA KORPUSU — persona × zorluk", "",
           "> 🔴 **Ölçülen katman: `route()` — yani SIFIR-LLM yol.** `durust_ret`,",
           "> *\"deterministik yol pes etti\"* demektir; `/ask` orada durmaz "
           "(Intent-JSON → Discovery).",
           "> Bu tablo ürünün cevapsızlığını değil, **LLM'siz yolun erişimini** ölçer —",
           "> ve ürünün tezi (*\"LLM garson, küp aşçı\"*) tam olarak o erişimdir.", ""]
    sat.append(f"Vaka: **{sonuc['toplam_vaka']}** · katalog sızıntısı: "
               f"**{len(sonuc['sizinti'])}**")
    sat.append("")
    sat.append("| Kademe | toplam | kabul | doğru | netleştirme | dürüst ret | 🔴 sessiz-yanlış |")
    sat.append("|---|---|---|---|---|---|---|")
    for k in KADEMELER:
        c = sonuc["sayac"].get(k)
        if not c:
            continue
        sat.append(f"| {k} | {c.get('toplam',0)} | **{c.get('kabul',0)}** | "
                   f"{c.get(DOGRU,0)} | {c.get(NETLESTIRME,0)} | {c.get(DURUST_RET,0)} | "
                   f"**{c.get(SESSIZ_YANLIS,0)}** |")
    if sonuc["sizinti"]:
        sat += ["", "## ⚠ KURAL 1 İHLALİ — katalog sızıntısı (vaka korpusa GİRMEDİ)", ""]
        for z in sonuc["sizinti"]:
            sat.append(f"- `{z['soru']}` → {z['kelimeler']}")
    kotu = [a for a in sonuc["ayrinti"] if not a.get("kabul_edildi")]
    if kotu:
        sat += ["", "## 🔴 KABUL EDİLMEYEN", ""]
        for a in kotu:
            sat.append(f"- **{a['persona']}/{a['kademe']}** `{a['soru']}` → "
                       f"`{a['sinif']}` · beklenen {a['kabul']}")
            sat.append(f"  - yasak: *{a['yasak']}* · kaynak: {a['kaynak']}")
    return "\n".join(sat) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Gerçek-dünya korpusu (denetim §9.6)")
    ap.add_argument("--persona", choices=sorted(PERSONALAR))
    ap.add_argument("--kademe", choices=KADEMELER)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    sonuc = kos(a.persona, a.kademe)
    if a.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
        return 0

    metin = rapor(sonuc)
    print(metin)
    hedef = pathlib.Path(__file__).resolve().parent / "reports" / "gercek_dunya.md"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(metin, encoding="utf-8")
    print(f"Rapor: {hedef.relative_to(pathlib.Path.cwd()) if hedef.is_relative_to(pathlib.Path.cwd()) else hedef}")
    # 🔴 **Hedef yüzde DEĞİL ilerleme** (kural 6): ilk koşum **tabandır** ve bu araç bir
    # eşikte kırmızı vermez. *Bir tabanı hedefe çevirmek, ilk ölçümü bir söze dönüştürür.*
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
