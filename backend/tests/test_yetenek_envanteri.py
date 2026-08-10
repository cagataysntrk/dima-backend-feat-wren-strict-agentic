"""🔴🔴 `B-10`/`B-6` — **MENÜDE OLMAYAN YEMEK İSTENEMEZ.**

Mutfağın (`wren_service` + `cube_router`) `cube_query`'de **okuduğu** her alan,
garsonun şemasında (`intent_semasi`) ya **var** olmalı ya **bilerek dışarıda** diye
beyan edilmeli. Sessiz fark kırmızı verir.

## Neden bu bir kapı olmak zorunda

Bu depo aynı dersi **üç kez** ödedi — `§M-6` (`pencere`/`turev`) · `§W-C` (yön) ·
`§AR/Ö` (örnek): *mutfak o yemeği yapabiliyorsa menüde de yazmalı; yoksa garson
isteyemez ve niteleme cevaptan **sessizce** düşer.*

`2026-08-07_CEVIRI-SOZLESMESI.md` farkı sayıyla yazmıştı: `route()` **12 anahtar**
üretebiliyordu, şema modele **7** alan sunuyordu. O fark bugün kapandı — ama
**bir belgede** kapandı, bir kapıda değil. *Belgeye yazılmış bir eşitlik, bir sonraki
alan eklendiğinde sessizce bozulur.*

## Liste elle tutulMAZ — koddan taranır

Mutfak tarafı `cq.get("…")` çağrılarından **üretilir**. Elle tutulan bir kopya, bu
kapının kapatmaya çalıştığı kusurun ta kendisini üretirdi: iki sahip, biri bayat.
"""

from __future__ import annotations

import json
import pathlib
import re

_APP = pathlib.Path(__file__).resolve().parents[1] / "app"

#: 🔴 **BİLEREK DIŞARIDA** — her satır bir **karar**, bir eksiklik değil.
#: Boş bırakmak üçüncü seçenek değildir: beyan edilmeyen bir fark, kapıyı kırmızı yapar.
BILEREK_DISARIDA: dict[str, str] = {
    "blend": "🔴 **AÇIK BORÇ, bilinçli dışarıda DEĞİL — `B-3`'e bağlı.** Çapraz-küp "
             "birleştirme `blend_sql` ile mutfakta VAR, ama eşleşme anahtarı ham boyut "
             "ADI olduğu için müşteri ekseninin üç ayrık ailesi arasında **kurulamıyor** "
             "(`cari_adi` · `musteri` · `musteri_kod`). Garsona bugün sunulsaydı, "
             "kuramayacağı bir yemeği sipariş etmesini istemiş olurduk. Kanonik varlık "
             "ekseni (`cekirdek/varlik_sozlugu.yml`) inince bu satır **silinir** ve alan "
             "şemaya girer.",
    # ── SİSTEM TAŞIYICILARI — bir yetenek değil, cevabın kendi damgası ──
    #
    # ⊙ Bu dört alan `cube_query` sözlüğünde **taşınır** ama kullanıcı onları
    # *isteyemez*: sistemin kendi kendine koyduğu işaretlerdir. Garsona sunmak,
    # ona *«cevabın ad-hoc mı olsun?»* diye sormak olurdu — anlamsız bir sipariş.
    #
    # ⚠ Ayrım bu kapının asıl kazancıdır: **yetenek** (kullanıcı isteyebilir) ile
    # **taşıyıcı** (sistem koyar) aynı sözlükte yaşıyor ve bugüne kadar hiçbir yerde
    # ayrılmamıştı. *Bir alanın menüde olmaması iki ayrı sebeple olabilir — biri borç,
    # öteki tasarım; ve ikisini ayırmayan bir liste, borcu gizler.*
    "adhoc": "SİSTEM TAŞIYICISI — yüklenen dosyadan üretilmiş geçici cube işareti "
             "(`dataset.py`). Kullanıcı bir cevabın ad-hoc olmasını isteyemez; sistem "
             "kaynağı işaretler. Menüye koymak anlamsız bir sipariş kalemi yaratırdı.",
    "kirpilmis": "SİSTEM TAŞIYICISI — sonuç satır tavanına takıldığında konan dürüstlük "
                 "işareti. Kullanıcının isteyeceği bir şey değil, cevabın kendisi "
                 "hakkında bir **beyan**; kırpıldığını söylemek sistemin görevidir.",
    "provenance_soru": "SİSTEM TAŞIYICISI — `question_original` + `question_normalized` "
                       "çifti; yeniden yazılan metnin izde görünmesini sağlar "
                       "(`B-8`'in iki sert sınırından biri). Sipariş değil **makbuz**.",
    "referans": "SİSTEM TAŞIYICISI — takip turunun çapası (önceki cevabın sorgusu). "
                "Kullanıcı onu yazmaz, konuşmanın kendisi üretir.",

    "ayrik_aylar": "⚠ Bitişik olmayan ay kümesi (*«ocak ve mart»*) — `timeDimensions` "
                   "aralık taşır, ayrık küme taşımaz. Mutfak destekliyor; garsona "
                   "sunmak için önce şemada bir **liste** biçimi gerekiyor ve bugünkü "
                   "`period_expr` metin alanı bunu **zaten** ifade edebiliyor. İkinci "
                   "bir yol açmak iki sahip yaratırdı (`§AR`'nin sınıfı).",
}


def _mutfak_alanlari() -> set[str]:
    """`cq.get("…")` çağrılarından **üretilen** mutfak yüzeyi — elle tutulan liste YOK."""
    desen = re.compile(r'\b(?:cq|q|query|cube_query)\.get\(\s*"([a-zA-Z_]+)"')
    alanlar: set[str] = set()
    for dosya in ("wren_service.py", "cube_router.py", "plan_kosucu.py"):
        yol = _APP / dosya
        if yol.is_file():
            alanlar |= set(desen.findall(yol.read_text(encoding="utf-8")))
    return alanlar


def _garson_alanlari(index: dict) -> set[str]:
    from app.intent_semasi import cube_query_json_schema

    def gez(n, acc):
        if isinstance(n, dict):
            acc |= set((n.get("properties") or {}).keys())
            for k, v in n.items():
                if k != "properties":
                    gez(v, acc)
        elif isinstance(n, list):
            for v in n:
                gez(v, acc)
        return acc

    return gez(cube_query_json_schema(index), set())


#: Mutfakta okunan ama `cube_query`'nin **alanı olmayan** anahtarlar (satır/iç yapı).
_ALAN_DEGIL = {"name", "measures", "dimensions", "time_dimensions", "type", "label",
               "synonyms", "cubes", "rows", "sql", "value", "operator", "dimension",
               "measure", "direction", "granularity", "lower_is_better"}


def test_MUTFAGIN_HER_ALANI_MENUDE_YA_DA_BEYANLI(schema):
    """🔴 *Mutfak o yemeği yapabiliyorsa menüde de yazmalı.*"""
    index = {c["name"]: c for c in schema["cubes"]}
    mutfak = _mutfak_alanlari() - _ALAN_DEGIL
    garson = _garson_alanlari(index)
    sessiz = sorted(mutfak - garson - set(BILEREK_DISARIDA))
    assert not sessiz, (
        f"🔴 SESSİZ FARK — mutfak {len(sessiz)} alanı okuyor, garson isteyemiyor: "
        f"{sessiz}\n"
        "  İki seçenek var: (1) `intent_semasi`'ye ekle, (2) `BILEREK_DISARIDA`'ya "
        "**gerekçesiyle** yaz.\n"
        "  ⚠ Boş bırakmak üçüncü bir seçenek değildir — niteleme cevaptan SESSİZCE "
        "düşer ve bu depo aynı dersi üç kez ödedi (`§M-6` · `§W-C` · `§AR/Ö`).")


def test_BEYAN_BAYATLAMAZ(schema):
    """⚠ Menüye giren bir alan `BILEREK_DISARIDA`'da kalmamalı — beyan **yalan** olur."""
    index = {c["name"]: c for c in schema["cubes"]}
    garson = _garson_alanlari(index)
    hayalet = sorted(set(BILEREK_DISARIDA) & garson)
    assert not hayalet, (
        f"bu alan(lar) artık garson şemasında VAR, beyandan çıkarılmalı: {hayalet}")


def test_HER_BEYAN_GEREKCE_TASIR():
    """*Gerekçesiz bir beyan, beyan değil bir istisnadır.*"""
    for alan, gerekce in BILEREK_DISARIDA.items():
        assert len(gerekce.strip()) >= 60, f"{alan}: gerekçe çok kısa"


def test_MUTFAK_YUZEYI_BOS_DEGIL():
    """🔴 Tarama bozulursa kapı **sessizce yeşil** olurdu — dekor tuzağı."""
    assert len(_mutfak_alanlari()) >= 5, (
        "mutfak alan taraması boş/az döndü — `cq.get(...)` deseni değişmiş olabilir. "
        "Kırmızı veremeyen bir kapı, kapı değildir.")
