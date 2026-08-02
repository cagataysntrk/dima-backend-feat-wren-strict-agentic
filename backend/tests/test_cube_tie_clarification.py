"""FAZ 3.1 — cube-düzeyi BERABERLİK: tahmin etme, SOR.

ÖLÇÜM (5011 soruluk demo-boyahane korpusu, 2 Ağustos 2026). `route()` 1057 soruda None
dönüyor ve bunların **872'sinde zaten bir netleştirme chip'i vardı** (`cube_only_match` 502,
`measure_cube_candidates` 370). Yani "belirsizlik Discovery'ye düşüyor" tezi %82 oranında
çoktan çözülmüştü. Geriye kalan 185'in en büyük sınıfı (88 soru) hiçbir netleştiriciye
görünmüyordu: `_match_cube`'un `len(hits) > 1` dalında beraberliği kıramayıp None dönmesi.
Bu sınıfa `measure_cube_candidates` AÇIKÇA bakmıyor (*"cube-düzeyi eşleşme → route
halleder"* — ama route halledemedi), `cube_only_match` de `_match_cube`'u çağırdığı için
yine None alıyor.

Sınıf kanıta göre İKİYE ayrıldı ve yalnız birine dokunuldu:
  55 soru — `bakim` vs `oee`, cube-sinonim farkı **0** VE ölçü-sinonim farkı **0**:
            ikisi de `"arıza duruşu"`nu BİREBİR aynı kanıtla eşliyor. GERÇEK belirsizlik.
  33 soru — `parti` vs `surdurulebilirlik`, fark 1: kanıt EŞİT DEĞİL → zayıf sinyal, orta
            güven bandı → DOKUNULMADI, Intent-JSON devralır.

Uygulama sonrası aynı korpus: cevaplanan soru sayısı **3954 → 3954** (sıfır regresyon),
chip'siz kalan 185 → 130.
"""

from __future__ import annotations

import pytest

from app import cube_router
from tests.conftest import ask

# Ölçülen kanonik vaka. `bakim.toplam_durus_dakika` ve `oee.plansiz_durus_dakika` İKİSİ DE
# "arıza duruşu" sinonimini taşır ve ikisi de meşrudur (bakım perspektifinden arıza süresi,
# OEE perspektifinden plansız duruş). Metinde ayrım YOKTUR.
BERABERLIK = "makine bazında arıza duruşu"


def test_beraberlik_ADAYLARI_dondurur(schema):
    ties = cube_router.cube_tie_candidates(BERABERLIK, schema)
    assert {c["name"] for c, _, _ in ties} == {"bakim", "oee"}


def test_chip_metni_DOGRULANMIS_cube_query_uretir(schema):
    """Chip'in metni VARSAYILMAZ, `route()` ile GERÇEKTEN koşulur ve referansla BİREBİR
    aynı `cube_query`yi üretmek zorundadır.

    Referans = "bu cube tek aday olsaydı kullanıcı ne alırdı" (katalog o cube'a daraltılıp
    `route()` yeniden koşulur). Bu sıkılık teorik değil: ilk sürüm yalnız cube adına bakıyordu
    ve gerçek koşuda iki sessiz-yanlış üretti — `oee` chip'i ölçüyü `plansiz_durus_dakika`dan
    `ort_kullanilabilirlik`e kaydırıyordu (ayırt edici kelime AYNI ZAMANDA bir ölçü sinonimiydi
    ve eşleşenden uzundu), `bakim` chip'i ise kırılıma `ariza_tipi` boyutunu ekliyordu
    ("makine arızası" içindeki "arıza" boyutu tetikliyordu). İkisi de bu testin kapsamı."""
    for cube, netlestirici, hit in cube_router.cube_tie_candidates(BERABERLIK, schema):
        referans = cube_router.route(
            BERABERLIK, {"models": schema.get("models", []), "cubes": [cube]})
        assert referans, f"{cube['name']} tek aday olsa bile cevaplanamıyor"
        assert hit["cube_query"] == referans["cube_query"], (
            f"{cube['name']}: chip metni {netlestirici!r} referanstan FARKLI bir sorgu "
            f"üretiyor — kullanıcı chip'in vaat ettiğinden başka bir sayı görür.\n"
            f"  chip     : {hit['cube_query']}\n  referans : {referans['cube_query']}")


def test_chip_tiklaninca_CEVAP_gelir_dongu_olmaz(schema):
    """Netleştirici metin tekrar belirsiz olsaydı kullanıcı aynı chip'e sonsuza kadar
    tıklardı. `_longest_syn_hit` MAKSİMUM aldığı için naif "cube adını başa ekle"
    stratejisi tam olarak bunu yapardı: `"bakım"` eklemek `bakim`in skorunu 5'ten 5'e
    taşır, yani beraberliği HİÇ bozmaz."""
    for cube, netlestirici, _ in cube_router.cube_tie_candidates(BERABERLIK, schema):
        assert cube_router.route(netlestirici, schema) is not None, (
            f"{netlestirici!r} yine belirsiz — chip DÖNGÜ yaratır")
        assert not cube_router.cube_tie_candidates(netlestirici, schema), (
            f"{netlestirici!r} yine beraberlik üretiyor")


def test_kirilan_beraberlikte_SESSIZ_kalir(schema):
    """EN ÖNEMLİ REGRESYON KİLİDİ. `route()` cevap üretebiliyorsa bu fonksiyon ASLA
    konuşmamalı — aksi halde bugün çalışan 3954 sorunun her biri gereksiz bir
    netleştirmeye dönüşürdü."""
    calisanlar = [
        "bu yıl fire oranı", "bölüm bazında oee bu yıl", "geçen ay toplam ciro",
        "makine bazında oee", "bu yıl su tüketimi", "aylık üretim trendi",
        "en çok ciro yapılan 5 müşteri", "bu yıl arıza duruşu",
    ]
    for soru in calisanlar:
        if cube_router.route(soru, schema) is None:
            continue  # bu soru zaten cevaplanmıyor — bu testin konusu değil
        assert not cube_router.cube_tie_candidates(soru, schema), (
            f"{soru!r} route() ile cevaplanıyor ama beraberlik chip'i de üretiliyor")


def test_kanit_ESIT_DEGILSE_dokunmaz(schema):
    """Zayıf sinyal beraberlik değildir. Ölçülen sınıf: `parti` (`"sapma"`, 5) vs
    `surdurulebilirlik` (`"enerji"`, 6) — 33 soru. Kanıt farklıysa karar bir soru sormaya
    değecek kadar dengeli değildir; orta güven bandı Intent-JSON'ındır. Bu ayrım olmadan
    fonksiyon "route çözemedi" ile "iki eşit yorum var"ı karıştırırdı."""
    soru = "enerji kaynağı bazında sapma yüzdesi"
    q = cube_router._norm(soru)
    hits = [c for c in schema.get("cubes", []) if cube_router._any_hit(q, c.get("synonyms"))]
    if len(hits) < 2 or cube_router._match_cube(q, schema) is not None:
        pytest.skip("bu şemada ölçülen eşitsiz-kanıt vakası yok")
    kanit = {(cube_router._longest_syn_hit(q, c),
              len(cube_router._match_measure(q, c)[1] or "")) for c in hits}
    assert len(kanit) > 1, "vaka artık eşitsiz-kanıt değil — testin gerekçesi kalktı"
    assert not cube_router.cube_tie_candidates(soru, schema)


def test_donem_ve_kirilim_chipte_KORUNUR(schema):
    """Netleştirme sorunun geri kalanını kaybetmemeli — kullanıcı dönemi ve kırılımı
    yeniden yazmak zorunda kalmasın."""
    ties = cube_router.cube_tie_candidates("bu yıl makine bazında arıza duruşu", schema)
    assert ties, "beraberlik vakası bulunamadı"
    for _, _, hit in ties:
        cq = hit["cube_query"]
        assert cq.get("dimensions") == ["makine"], cq
        assert any(f.get("operator") == "gte" for f in cq.get("filters") or []), cq


def test_ask_uctan_uca_NETLESTIRME_doner(client):
    """`/ask` merdiveninde chip Intent-JSON'dan ÖNCE gelir: iki aday birebir eşit kanıt
    taşırken LLM'e seçtirmek "belirsizlikte sor, tahmin etme" değişmezinin (MIMARI.md
    §4-6) ihlalidir — LLM'in tahmini `cube+llm` rozetiyle sunulur ve yanlışsa makul görünür."""
    d = ask(client, BERABERLIK)
    assert d.get("source") is None, f"beraberlikte cevap üretildi: {d.get('source')}"
    assert d.get("result") is None
    etiketler = [s["label"] for s in d.get("suggestions") or []]
    assert len(etiketler) == 2, etiketler
    assert any("plansız" in e.lower() for e in etiketler), etiketler
    assert any(t in " ".join(d.get("trace") or []) for t in ("beraberlik",)), d.get("trace")


def test_tum_adaylar_ifade_edilemezse_HIC_chip_yok(schema):
    """HEPSİ YA DA HİÇBİRİ. Eksik bir chip listesi bir yorumu sessizce eler — ADR-0008'in
    yasakladığı davranış. Burada adaylardan biri kasten ifade edilemez hale getirilir
    (ölçü ve cube sinonimleri boşaltılır) ve listenin TAMAMEN sustuğu doğrulanır."""
    import copy

    sakat = copy.deepcopy(schema)
    for c in sakat["cubes"]:
        if c["name"] == "oee":
            olcu, eslesen = cube_router._match_measure(cube_router._norm(BERABERLIK), c)
            c["measure_synonyms"][olcu] = [eslesen]  # ikame edecek başka sinonim yok
            rakip = {s.removesuffix("!") for o in sakat["cubes"] if o["name"] == "bakim"
                     for s in o.get("synonyms") or []}
            c["synonyms"] = [s for s in c["synonyms"] if s.removesuffix("!") in rakip]
    assert not cube_router.cube_tie_candidates(BERABERLIK, sakat)
