"""FAZ 0.4 — **NETLEŞTİRME ÖNCELİĞİ: ÖLÇÜM KARARI.**

`netlestirme_onceligi` mekanizması `ff987eb`'de indi; karar **ölçülmedi**. Bu araç o
ölçümü yapar ve bayrağın `off` mu kalacağını, `beta`'ya mı açılacağını **sayıyla** söyler.

## 🔴 İLAN EDİLEN KAPI ÇALIŞMIYOR — ve nedeni ilkesel

Yol haritası kapıyı şöyle yazmıştı: *"`lab/nl_corpus.py --kapi` öncesi/sonrası: kapanan
sessiz-yanlış (yanlış-cube azalması) vs kapsam kaybı (`CLARIFY:konu` artışı)."* İki ayrı
sebeple **koşulamaz**:

1. **Alette karşılığı yok.** `nl_corpus.py`'nin bayrak zorlama seçeneği **yoktur**
   (`--bayrak` yalnız `deneyim.py`'de var, `--ab` yalnız `nl_accuracy.py`'de). Beyan
   edilen komut bugün **hiçbir şeyi** A/B koşturmaz — bu, bu deponun avladığı *"beyan
   var, kod onu tanımıyor"* sınıfının ölçüm aletindeki hâli.

2. 🔴 **Daha ağırı: korpus bu nüfusa HAKEMLİK EDEMEZ.** Korpusun *"beklenen cube"*u,
   soruyu **hangi cube'un sözlüğünden ürettiğiyse** odur (`nl_corpus.py::kaynak`). Bu
   bayrağın nüfusu ise tam olarak **aynı terimi ≥2 cube'un sahiplendiği** kümedir. Yani
   korpusun yer gerçeği, bu 50 küsur soruda **kendisi bir yazı-turadır**: LLM'in şanslı
   tahmini *"doğru"*, netleştirme sorusu *"kayıp"* sayılırdı — **ürün niyetinin tam
   tersi**. `ask.py`'nin kendi yorumu bunu zaten söylüyor: *"Gerçekten belirsiz bir
   kelimede **doğru cevap yoktur**; herhangi bir seçim yazı-turadır."*

**Sonuç: doğruluk bu kararı veremez.** Yer gerçeği olmayan bir nüfusta ölçülebilecek şey
**kararlılıktır** — ve kararlılık, yer gerçeği istemez.

## Ne ölçülüyor — üç adım

| # | Ölçüm | LLM | Ne söyler |
|---|---|---|---|
| **1** | **NÜFUS** — bayrak AÇIKKEN gerçekten netleştirmeye düşen soru kümesi | **0** | Kapının nüfusu; `ask.py`'nin *"53"* beyanı doğru mu |
| **2** | **NEGATİF KONTROL** — etiketli vaka setinde bozulan | **0** | Bayrak **nüfusunun dışına taşıyor mu** (KURAL B) |
| **3** | **CANLI KARAR** — bayrak KAPALIYKEN LLM ne yapıyor | var | Yazı-tura mı, bağlamdan mı çözüyor, yoksa hep aynı cube'a mı yığıyor |

**1 ve 2 neden LLM'siz:** bayrak kapısı `route_hit is None` koşuluna bağlı ve
`_olcu_belirsizligi_netlestir` Intent-JSON'dan **ÖNCE** döner — yani bayrak AÇIKKEN bu
nüfus için **hiç LLM çağrılmaz**. A/B'nin *"sonra"* yakası bedavadır; ücret yalnız
*"önce"* yakasındadır. (Bu, kotayı yarıya indiren yapısal bir olgudur, bir kısaltma değil.)

## Karar kuralı — ÜÇ YOL, önceden yazılı

Bayrak KAPALIYKEN, nüfustaki her soru `tur` kez sorulur:

* **A · KARARSIZ** — aynı soru turlar arası **farklı cube** veriyor ya da
  `self-consistency` düşük → seçim **yazı-tura**. Netleştirme bir kaybı değil, bir
  **kurayı** değiştirir → bayrak **AÇILIR**.
* **B · BAĞLAMDAN ÇÖZÜYOR** — her soru kendi içinde kararlı **ve** sorular arası cube
  **değişiyor** → LLM sorudaki ayırt edici bilgiyi gerçekten kullanıyor. Netleştirme
  **gerçek kapsam kaybı** → bayrak **KAPALI kalır**, gerekçe `MIMARI.md`'ye yazılır.
* **C · SİSTEMATİK YANLILIK** — kararlı ama **hep aynı cube** → ayırt etme değil,
  sabit bir tercih. Öteki cube'un kullanıcısı **her seferinde sessizce yanlış** cevap
  alır → bayrak **AÇILIR**.

⚠ **Dördüncü sonuç mümkün ve raporlanır:** bayrak KAPALIYKEN cevabın kendisi zaten bir
**netleştirme** olabilir — `_select_consistent` tek eksende uyuşmazsa `ask.py` zaten
`_intent_uyusmazlik_chipi` döndürür. O soruda 0.4'ün **kazancı yoktur**, çünkü sistem
zaten soruyor. Bu pay ayrı sayılır; yoksa kazanç **abartılır**.

## Örneklem — sessiz kırpma YOK

Canlı yaka örneklenir (kota bilinmiyor: **10 istek / 10 saniye**, günlük kota belirsiz).
Rapor **her zaman** nüfusu, örneklemi ve dışarıda kalanı yazar. Örneklem kararı taşıyamaz
hâle gelirse sonuç `⊘ ÖLÇÜLEMEDİ`'dir — *"karar veremedim"* bir sonuçtur, sessizlik değil.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 🔴 **İÇE AKTARMA SIRASI BİR SÖZLEŞMEDİR — ve bu alet ona ilk denemede uydu SANDI.**
#
# `konusma_senaryolari` gerçek ortamı (`DIMA_LLM_PROVIDER` …) **modül düzeyinde**, yani
# `tests.conftest` onu `rule`'a sabitlemeden **ÖNCE** yakalar. Bu dosya ilk sürümünde
# `tests.conftest`'i başa koymuştu ve `--live` **fail-closed** ile durdu:
#     "--live GERÇEK bir sağlayıcı ister. `DIMA_LLM_PROVIDER` boş ya da 'rule'"
# Kapan **çalıştı** — sessizce `rule` ile koşan sahte bir "canlı" tur üretilmedi. Ama
# kuralın kendisi yalnız `nl_accuracy.py`'nin bir **yorumunda** yazılıydı; yorum, sırayı
# **zorlayamaz**. Artık `tests/test_faz0_4_netlestirme.py::test_ICE_AKTARMA_SIRASI_*`
# bunu canlı koşabilen her lab aletinde **kapıya** çeviriyor.
#
# TEK SAHİP: bayrak zorlayıcı, istemci kurucu, hesaplar ve canlı ortam geri yükleyici
# **yeniden yazılmaz**, çağrılır. Bu deponun 1 numaralı kusuru "aynı kuralın iki sahibi".
from lab.konusma_senaryolari import _canli_ortami_geri_yukle  # noqa: E402
from lab.nl_accuracy import (  # noqa: E402
    ACCOUNTS,
    _BayrakZorla,
    _client,
    ab_kos,
)

import tests.conftest as _conf  # noqa: E402,F401  (env kurulumu — SIRA: canlı yakalamadan SONRA)

BAYRAK = "netlestirme_onceligi"
RAPOR = Path(__file__).resolve().parent / "reports" / "faz0_4_netlestirme.md"

#: Turlar arası bekleme. Ölçülen sınır 10 istek/10 sn; bir Intent turu `consistency_k=3`
#: ile ÜÇ çağrı yapar → 5 sn ara, tepe yükte bile sınırın yarısında kalır.
BEKLE = 5.0


def _sorular(sch: dict) -> list[tuple[str, str, list[str]]]:
    """`(soru, terim, sahip cube'lar)` — katalogda **≥2 cube'un sahiplendiği** ölçü
    sinonimleri.

    ⚠ Soru **`"bu yıl …"`** ile kurulur ve bu bir süs değil: dönem verilmezse
    `CLARIFY:dönem` kapısı **önce** ateşlenir ve ölçü belirsizliğini **maskeler** —
    ölçülmek istenen şeyin yerine başka bir şey ölçülürdü.
    """
    sahip: dict[str, set[str]] = {}
    for c in sch.get("cubes") or []:
        for _olcu, sinonimler in (c.get("measure_synonyms") or {}).items():
            for s in sinonimler or []:
                if s:
                    sahip.setdefault(str(s), set()).add(str(c.get("name")))
    return [(f"bu yıl {t}", t, sorted(v)) for t, v in sorted(sahip.items()) if len(v) > 1]


def _sinif(d: dict) -> tuple[str, str | None]:
    """Cevabı sınıflandır → `(sınıf, seçilen cube)`.

    `netlestirme` · `sql` · `bos`. Netleştirmenin **iki kaynağı** ayrılmaz burada;
    ayrımı çağıran yapar (bayrak açıkken → 0.4'ün kendisi; kapalıyken → Intent
    uyuşmazlık chip'i, yani *zaten soruyordu*).
    """
    if d.get("_http"):
        return f"HTTP{d['_http']}", None
    cq = d.get("cube_query") or {}
    if d.get("sql") or cq.get("cube"):
        return "sql", cq.get("cube")
    if (d.get("suggestions") or []) and len(d["suggestions"]) >= 2:
        return "netlestirme", None
    return "bos", None


def _uyum(d: dict) -> float | None:
    """`self-consistency %NN (k örnek)` — `ask.py` bunu **trace'e yazıyor**; ikinci bir
    alan açmak yerine yazdığı yerden okunur.

    ⚠ Etiketten SONRASI okunur, ilk `%`'den değil: aynı trace satırına typo notu
    ekleniyor (`typo_fix_trace · self-consistency …`) ve o not da yüzde taşıyabilir —
    ilk `%`'yi almak **benzerlik oranını uyum sanmak** olurdu.
    """
    for t in d.get("trace") or []:
        s = str(t)
        i = s.find("self-consistency %")
        if i < 0:
            continue
        try:
            return int(s[i + len("self-consistency %"):].split()[0]) / 100.0
        except (IndexError, ValueError):
            return None
    return None


def _sor(c, q: str) -> dict:
    d = c.post("/ask", json={"question": q, "execute": False})
    try:
        return d.json()
    except Exception:
        return {"_http": d.status_code}


# ══ 1 · NÜFUS — bayrak AÇIKKEN netleştirmeye düşen küme (LLM'siz) ═════════════
def nufus_olc(c, adaylar: list[tuple[str, str, list[str]]]) -> list[tuple[str, str, list[str]]]:
    """Kapının **gerçek** nüfusu. Proxy değil: bayrak açılır ve cevaba **bakılır**.

    `route()`'un çözdüğü (*"en spesifik ölçü kazanır"*) ve VQR'ın tekrarladığı sorular
    kendiliğinden elenir — ayrı bir eleme kuralı yazmak, kapının kuralını **ikinci kez**
    yazmak olurdu.
    """
    icinde = []
    with _BayrakZorla(BAYRAK, acik=True):
        for q, terim, cubes in adaylar:
            s, _ = _sinif(_sor(c, q))
            if s == "netlestirme":
                icinde.append((q, terim, cubes))
    return icinde


def llmsiz_fark_olc(c, nufus: list[tuple[str, str, list[str]]]) -> int:
    """🔴 **İLAN EDİLEN KAPININ BOŞ OLDUĞUNUN KANITI** — kaç soruda A/B farkı var.

    Bayrak KAPALIYKEN de aynı netleştirici çağrılıyor (`ask.py:2757`), yalnız
    Intent-JSON'dan **SONRA**. LLM yoksa Intent dalı hiç koşmaz → iki yol **aynı yere**
    çıkar. Yani `nl_corpus.py` gibi LLM'siz bir korpusta bu bayrağın A/B farkı
    **yapısal olarak sıfırdır** ve *"gerileme yok"* diye okunurdu.

    Bu sayı **0 çıkmalıdır**; 0 çıkması kapının değil, **eski kapının** kırmızısıdır.
    """
    fark = 0
    for q, _t, _c in nufus:
        with _BayrakZorla(BAYRAK, acik=True):
            a, _ = _sinif(_sor(c, q))
        with _BayrakZorla(BAYRAK, acik=False):
            b, _ = _sinif(_sor(c, q))
        if a != b:
            fark += 1
    return fark


# ══ 3 · CANLI KARAR — bayrak KAPALIYKEN LLM ne yapıyor ═══════════════════════
def canli_olc(c, nufus: list[tuple[str, str, list[str]]], n: int, tur: int) -> dict:
    """Örneklem üstünde, bayrak KAPALI, `tur` kez. Döner: soru → tur sonuçları."""
    ornek = nufus[:n]
    out: dict[str, list[tuple[str, str | None, float | None]]] = {}
    with _BayrakZorla(BAYRAK, acik=False):
        for t in range(tur):
            for q, _terim, _cubes in ornek:
                d = _sor(c, q)
                s, cube = _sinif(d)
                out.setdefault(q, []).append((s, cube, _uyum(d)))
                time.sleep(BEKLE)
            print(f"  tur {t + 1}/{tur} bitti ({len(ornek)} soru)", flush=True)
    return out


def karar_ver(sonuc: dict, nufus_n: int) -> tuple[str, list[str]]:
    """Üç yolun hangisi — ve **neden**. Karar kuralı ölçümden ÖNCE yazıldı."""
    gerekce: list[str] = []
    if not sonuc:
        return "⊘ ÖLÇÜLEMEDİ", ["Örneklem boş — canlı yaka hiç koşmadı."]

    # 🔴 **SON KOŞUL: LLM GERÇEKTEN KATILDI MI?** Ön uçuş bir ÖN koşuldur ve kota koşumun
    # **ortasında** tükenebilir. Ölçüldü (2026-08-04): ön uçuş geçti, sonra her tur
    # *"TÜM sağlayıcılar başarısız"* (`429`/`503`) verdi ve bu fonksiyon **"B · bağlamdan
    # çözüyor"** bastı — oysa ölçtüğü kararlılık, LLM'in değil **BAŞARISIZLIĞIN**
    # kararlılığıydı. Deterministik bir düşüş her turda aynı cevabı verir; "kararlı"
    # görünür ve **yanlış-yeşildir**.
    #
    # Katılım kanıtı: `_select_consistent` uyum oranını **trace'e yazar** (`k>1` iken).
    # Hiçbir turda uyum notu yoksa Intent dalı hiç çalışmamış demektir.
    katildi = any(u is not None for turlar in sonuc.values() for _s, _c, u in turlar)
    if not katildi:
        return "⊘ ÖLÇÜLEMEDİ", [
            f"**LLM hiçbir turda cevap vermedi** ({len(sonuc)} soru): tek bir turda bile "
            "`self-consistency` izi yok. Sağlayıcı kotası tükenmiş ya da erişilemez "
            "olabilir. Bu koşumda ölçülen kararlılık, LLM'in değil **başarısızlığın** "
            "kararlılığıdır — karar basılmadı (fail-closed)."]

    kararsiz, zaten_soruyor, secilen_cubeler, dusuk_uyum = [], [], [], []
    for q, turlar in sonuc.items():
        siniflar = {s for s, _c, _u in turlar}
        cubeler = {c for _s, c, _u in turlar if c}
        uyumlar = [u for _s, _c, u in turlar if u is not None]
        if siniflar == {"netlestirme"}:
            zaten_soruyor.append(q)
            continue
        if len(cubeler) > 1:
            kararsiz.append(q)
        elif cubeler:
            secilen_cubeler.append(next(iter(cubeler)))
        if uyumlar and min(uyumlar) < 0.67:      # 2/3 altı = tek eksende bile uzlaşmıyor
            dusuk_uyum.append(q)

    olculebilir = [q for q in sonuc if q not in zaten_soruyor]
    if not olculebilir:
        return "⊘ ÖLÇÜLEMEDİ", [
            f"Örneklemin **tamamı** ({len(zaten_soruyor)}) bayrak KAPALIYKEN de zaten "
            "netleştirme döndürdü (Intent uyuşmazlık chip'i). 0.4'ün bu örneklemde "
            "**kazancı da kaybı da yok**; karar daha geniş bir örneklem ister."]

    gerekce.append(f"Ölçülebilir soru: **{len(olculebilir)}**/{len(sonuc)} "
                   f"(nüfus {nufus_n}) · zaten netleştiren: {len(zaten_soruyor)}")
    if kararsiz or dusuk_uyum:
        gerekce.append(f"**KARARSIZ {len(kararsiz)}** (turlar arası cube değişti) · "
                       f"düşük self-consistency {len(dusuk_uyum)}")
        return "A · KARARSIZ → bayrak AÇILIR", gerekce
    if secilen_cubeler and len(set(secilen_cubeler)) == 1:
        gerekce.append(f"Tüm ölçülebilir sorular **tek cube**'a yığıldı: "
                       f"`{secilen_cubeler[0]}` — ayırt etme değil, sabit tercih.")
        return "C · SİSTEMATİK YANLILIK → bayrak AÇILIR", gerekce
    gerekce.append(f"Her soru kendi içinde kararlı **ve** sorular arası cube değişiyor "
                   f"({len(set(secilen_cubeler))} farklı cube) — LLM bağlamdan çözüyor.")
    return "B · BAĞLAMDAN ÇÖZÜYOR → bayrak KAPALI kalır", gerekce


def main() -> int:
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 8
    tur = int(sys.argv[sys.argv.index("--tur") + 1]) if "--tur" in sys.argv else 2
    canli = "--live" in sys.argv

    if canli:
        sag = _canli_ortami_geri_yukle()
        print(f"CANLI MOD — sağlayıcı: {sag} · örneklem {n} × {tur} tur "
              f"(≈{n * tur * 3} LLM çağrısı) · tur arası {BEKLE}s", flush=True)

    login, pw, slug = ACCOUNTS["boyahane"]
    c = _client(login, pw, slug)
    try:
        sch = c.get("/schema").json()
        adaylar = _sorular(sch)
        print(f"\n1 · NÜFUS — katalogda ≥2 sahibi olan terim: {len(adaylar)}", flush=True)
        nufus = nufus_olc(c, adaylar)
        print(f"    bayrak AÇIKKEN netleştirmeye düşen: **{len(nufus)}** "
              f"(`ask.py` beyanı: 53)", flush=True)

        # ⚠ Bu ölçüm **yalnız LLM YOKKEN** anlamlıdır: iddiası *"LLM'siz bir korpusta A/B
        # farkı sıfırdır"*. Canlı modda koşturulursa aynı sayı bambaşka bir şeyi ölçer
        # (Intent dalı devrededir) ve **aynı adla** raporlanırdı. Ölçüldü: canlı koşumda
        # `28/41` çıktı ve satır hâlâ *"LLM'SİZ"* diyordu — bir ölçümün adı, ölçtüğü şeyle
        # ayrışırsa okuyan kişi doğru sayıdan **yanlış sonuç** çıkarır.
        llmsiz_fark = None
        if not canli:
            llmsiz_fark = llmsiz_fark_olc(c, nufus)
            print(f"\n1b · LLM'SİZ A/B FARKI: **{llmsiz_fark}**/{len(nufus)} — "
                  + ("🔴 ilan edilen `nl_corpus --kapi` kapısı BOŞ: LLM'siz koşumda iki "
                     "yol aynı yere çıkıyor (`ask.py:2757` aynı netleştiriciyi çağırıyor)."
                     if llmsiz_fark == 0 else
                     "LLM'siz yolda da fark ölçüldü — beklenmiyordu, incelenmeli."),
                  flush=True)
        else:
            print("\n1b · LLM'SİZ A/B FARKI — ⊘ ATLANDI: bu ölçüm yalnız LLM YOKKEN "
                  "anlamlıdır (iddiası *'LLM'siz korpusta fark sıfırdır'*).", flush=True)

        print("\n2 · NEGATİF KONTROL — etiketli vaka setinde bozulan", flush=True)
        neg = ab_kos(BAYRAK)

        sonuc: dict = {}
        if canli and nufus:
            print(f"\n3 · CANLI KARAR — bayrak KAPALI, örneklem {min(n, len(nufus))}",
                  flush=True)
            sonuc = canli_olc(c, nufus, n, tur)
        elif not canli:
            print("\n3 · CANLI KARAR — ⊘ ATLANDI (`--live` verilmedi). "
                  "LLM'siz koşum bu kararı VEREMEZ: kapatılan sessiz-yanlış ancak "
                  "gerçek sağlayıcıyla görülür.", flush=True)
    finally:
        c.__exit__(None, None, None)

    karar, gerekce = karar_ver(sonuc, len(nufus)) if canli else (
        "⊘ ÖLÇÜLEMEDİ", ["`--live` olmadan koşuldu — karar üretilmedi."])
    print(f"\n=== 0.4 KARARI: {karar} ===")
    for g in gerekce:
        print(f"  · {g}")

    RAPOR.parent.mkdir(parents=True, exist_ok=True)
    RAPOR.write_text(
        _rapor_yaz(adaylar, nufus, llmsiz_fark, neg, sonuc, karar, gerekce, n, tur),
        encoding="utf-8")
    print(f"\nrapor → {RAPOR}")
    return 0


def _rapor_yaz(adaylar, nufus, llmsiz_fark, neg, sonuc, karar, gerekce, n, tur) -> str:
    s = ["# FAZ 0.4 — netleştirme önceliği: ÖLÇÜM KARARI", "",
         f"**KARAR: {karar}**", ""]
    s += [f"- {g}" for g in gerekce]
    s += ["", "## 1 · Nüfus (LLM'siz)", "",
          f"- katalogda ≥2 sahibi olan terim: **{len(adaylar)}**",
          f"- bayrak AÇIKKEN gerçekten netleştirmeye düşen: **{len(nufus)}**",
          "", "## 1b · İlan edilen kapının ölçümü", ""]
    if llmsiz_fark is None:
        s.append("⊘ **ATLANDI** — bu ölçüm yalnız LLM YOKKEN anlamlıdır: iddiası "
                 "*«LLM'siz bir korpusta A/B farkı sıfırdır»*. Canlı modda aynı sayı "
                 "başka bir şeyi ölçerdi ve **aynı adla** raporlanırdı.")
    elif llmsiz_fark == 0:
        s += [f"- LLM'siz A/B farkı: **0**/{len(nufus)}",
              "- 🔴 `nl_corpus.py --kapi` bu kararı **veremez**: LLM olmayan bir koşumda "
              "bayrak AÇIK ve KAPALI **aynı cevabı** üretir (`ask.py:2601` ile `:2757` "
              "aynı netleştiriciyi çağırır; ikincisi Intent-JSON'dan sonradır ve LLM "
              "yoksa Intent dalı hiç koşmaz). Fark **yapısal olarak sıfırdır** ve "
              "*«gerileme yok»* diye okunurdu."]
    else:
        s += [f"- LLM'siz A/B farkı: **{llmsiz_fark}**/{len(nufus)}",
              "- ⚠ LLM'siz yolda fark ölçüldü — beklenmiyordu, incelenmeli."]
    s += ["", "## 2 · Negatif kontrol (LLM'siz)", "",
          f"- `ab_kos({BAYRAK!r})` çıkış kodu: **{neg}** "
          f"({'bozulan YOK — bayrak nüfusunun dışına taşmıyor' if neg == 0 else '🔴 BOZULAN VAR'})",
          "", "## 3 · Canlı ölçüm", ""]
    if not sonuc:
        s.append("⊘ **ÖLÇÜLEMEDİ** — canlı yaka koşmadı.")
    else:
        s.append(f"Örneklem **{len(sonuc)}**/{len(nufus)} · **{tur}** tur "
                 f"· kapsam dışı **{max(0, len(nufus) - len(sonuc))}** soru "
                 "*(sessiz kırpma yok: kota bilinmediği için örneklem küçük tutuldu)*")
        s += ["", "| soru | turlar (sınıf/cube/uyum) |", "|---|---|"]
        for q, turlar in sonuc.items():
            hucre = " · ".join(f"{a}/{b or '—'}/{f'%{u*100:.0f}' if u else '—'}"
                               for a, b, u in turlar)
            s.append(f"| `{q}` | {hucre} |")
    return "\n".join(s) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
