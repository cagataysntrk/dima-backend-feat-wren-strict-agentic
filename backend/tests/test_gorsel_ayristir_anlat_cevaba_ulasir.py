"""🔴 `§88` — **`GORSEL`/`AYRISTIR`/`ANLAT` HESAPLANIP CEVABA ULAŞIR.**

## Ölçülen kusur (canlı, `belgeler/arastirma/2026-08-25_MIMARI-CIKMAZ-ARASTIRMASI.md` §11)

Kullanıcının kendi cümlesi (*"son 2 yıl satış verileri … grafiğe dök"*) `/plan/kos`'a
koşturuldu: plan `SORGU→AYRISTIR→GORSEL→ANLAT` doğru kuruldu ve **koştu** (`HTTP 200`),
ama HTTP cevabında `viz`/`contribution`/`interpretation` **hiç yoktu** — yalnız ham
`result` tablosu ve "4 adımda üretildi" diyen statik bir şablon `note`.

Kod okununca sebep netti: `_gorsel()`/`_ayristir()`/`_anlat()` (`plan_tuketici.py`)
çıktıyı fiilen hesaplıyor, ama `bolumlere_cevir` bölümleri `CIKTI_TIPI`'ye göre süzüyor
ve yalnız `"satirlar"` tipini topluyor — `GORSEL`/`AYRISTIR` (`"bulgular"`) ve `ANLAT`
(`"metin"`) bu süzgeçten hiç geçmiyor, dolayısıyla `kosum_yaniti`'nin ürettiği HTTP
cevabına hiç ulaşmıyor. `AskResponse.viz`/`.contribution`/`.interpretation` zaten var
(ADR-0024, Faz G1/H) — eksik olan alan değil, **doldurma**.
"""

from __future__ import annotations

from app.plan_tuketici import _bulgu_ve_metin_cikar, kosum_yaniti

_SORGU_CQ = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"]}

#: Kullanıcının canlı örneğinin birebir küçültülmüş hâli: SORGU → AYRISTIR → GORSEL → ANLAT.
_PLAN = {"adimlar": [
    {"fiil": "SORGU", "cube_query": _SORGU_CQ},
    {"fiil": "AYRISTIR", "cube_query": _SORGU_CQ},
    {"fiil": "GORSEL", "kaynak": "$1", "cube_query": _SORGU_CQ},
    {"fiil": "ANLAT", "kaynaklar": ["$2", "$3"]},
]}

_VIZ_CIKTISI = {"kind": "bar", "measures": ["toplam_ciro"], "dims": ["musteri"]}
_AYRISTIR_CIKTISI = {"bilesenler": [{"ad": "musteri-1", "pay": 0.4}]}
_ANLAT_CIKTISI = "En büyük katkı EGE KNIT'ten geldi."

#: `out["ciktilar"]` — `plan_kosucu.kos()`'un çıktısı, `adimlar` ile **index-hizalı**.
_OUT_TAM = {
    "ciktilar": [
        [{"musteri": "EGE KNIT", "toplam_ciro": 41034758.4}],  # SORGU → satırlar
        _AYRISTIR_CIKTISI,                                      # AYRISTIR → bulgular
        _VIZ_CIKTISI,                                           # GORSEL → bulgular
        _ANLAT_CIKTISI,                                         # ANLAT → metin
    ],
    "sorgular": [_SORGU_CQ],
    "makbuz": [], "sorgu_sayisi": 1, "onarimlar": [],
}


def test_GORSEL_CIKTISI_VIZ_ALANINA_ULASIR():
    """🔴 **ASIL DEĞİŞMEZ.** `_gorsel()`'in hesapladığı grafik kaybolmaz."""
    viz, _, _ = _bulgu_ve_metin_cikar(_OUT_TAM, _PLAN)
    assert viz == _VIZ_CIKTISI, f"🔴 GORSEL çıktısı taşınmadı: {viz!r}"


def test_AYRISTIR_CIKTISI_CONTRIBUTION_ALANINA_ULASIR():
    contribution, _sirasi_onemsiz = (
        _bulgu_ve_metin_cikar(_OUT_TAM, _PLAN)[1], None)
    assert contribution == _AYRISTIR_CIKTISI, f"🔴 AYRISTIR çıktısı taşınmadı: {contribution!r}"


def test_ANLAT_CIKTISI_INTERPRETATION_ALANINA_ULASIR():
    _, _, interpretation = _bulgu_ve_metin_cikar(_OUT_TAM, _PLAN)
    assert interpretation is not None, "🔴 ANLAT çıktısı taşınmadı"
    assert interpretation["summary"] == _ANLAT_CIKTISI


def test_KOSUM_YANITI_UC_ALANI_BIRDEN_TASIR():
    """Uçtan uca: `kosum_yaniti` gerçek HTTP cevabını kurar."""
    yanit = kosum_yaniti(_OUT_TAM, _PLAN, schema={}, soru="test")
    assert yanit.get("viz") == _VIZ_CIKTISI, "🔴 HTTP cevabında viz yok"
    assert yanit.get("contribution") == _AYRISTIR_CIKTISI, "🔴 HTTP cevabında contribution yok"
    assert yanit.get("interpretation", {}).get("summary") == _ANLAT_CIKTISI, (
        "🔴 HTTP cevabında interpretation yok")
    # `bolumler`/`result` davranışı bu düzeltmeden ETKİLENMEMELİ — yalnız SORGU'nun
    # ürettiği satırlar orada kalır (§29'un kendi ölçütü).
    assert yanit["result"]["rows"] == _OUT_TAM["ciktilar"][0]


def test_ZIT_OLCUT_BOS_CIKTI_ALAN_EKLEMEZ():
    """🆃 Kapının kurbanı: `{}`/boş metin de "gerçek bir bulgu" sayılabilirdi. `GORSEL`
    hiçbir öneri üretemediğinde (`viz.recommend` → `{}`) alan hiç EKLENMEMELİ —
    "hesapladım ama boş" ile "hiç hesaplamadım" karışmasın."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": _SORGU_CQ},
                        {"fiil": "GORSEL", "kaynak": "$1", "cube_query": _SORGU_CQ}]}
    out = {"ciktilar": [[{"musteri": "X", "toplam_ciro": 1}], {}],
           "sorgular": [_SORGU_CQ], "makbuz": [], "sorgu_sayisi": 1, "onarimlar": []}
    viz, contribution, interpretation = _bulgu_ve_metin_cikar(out, plan)
    assert viz is None, f"🔴 boş `{{}}` gerçek bulgu sayıldı: {viz!r}"
    assert contribution is None
    assert interpretation is None
    yanit = kosum_yaniti(out, plan, schema={}, soru="test")
    assert "viz" not in yanit, "🔴 boşken bile `viz` anahtarı eklenmiş"


def test_ZIT_OLCUT_SORGU_TEK_BASINA_HALA_CALISIR():
    """🆃 Tek adımlı, eski davranışın (`GORSEL`/`AYRISTIR`/`ANLAT` yok) bozulmadığını
    doğrular — bu düzeltme yalnız EKLİYOR, var olanı değiştirmiyor."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": _SORGU_CQ}]}
    out = {"ciktilar": [[{"musteri": "X", "toplam_ciro": 1}]],
           "sorgular": [_SORGU_CQ], "makbuz": [], "sorgu_sayisi": 1, "onarimlar": []}
    yanit = kosum_yaniti(out, plan, schema={}, soru="test")
    assert "viz" not in yanit and "contribution" not in yanit and "interpretation" not in yanit
    assert yanit["result"]["row_count"] == 1
