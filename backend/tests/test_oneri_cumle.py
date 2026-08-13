r"""🔴 **ÖNERİ ŞERİDİNİN CÜMLE KAPISI** (`app/oneri_cumle.py`).

Ölçülen kusur (bu turun başlangıç durumu): `/oneri` **ham alan parçaları** döndürüyordu —
`fire` · `su` · `set`. Planın `§18.7`'si bunu açıkça yasaklıyor (*«alan adını DEĞİL»*) ve
`§5.1` bir **cümle** şeridi istiyor. Bu dosya o şeridin **sözleşmesini** kilitler.

Her yüklem **tek bir kuralı** ölçer; kural planın hangi maddesinden geldiği docstring'de
yazılıdır. Morfoloji vakaları **gerçek katalog adlarıyla** yazıldı: `demo/packs`'teki
`dimension_labels` değerleri (*makine · vardiya · kumaş cinsi · iplik grubu · yaş grubu ·
haftanın günü · operatör · tedarikçi · ton derinliği · hat*) ve `test_next_steps.py`'nin
fikstüründeki *şehir* / *müşteri* · `oee` cube'unun *duruş nedeni* etiketi.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.oneri import Aday
from app.oneri_cumle import (
    _ONCEKI_DONEM,
    GRUP_RAPOR,
    GRUP_YENI,
    TUR_DONEM,
    TUR_KIRILIM,
    TUR_NEDEN,
    TUR_OLCU_EKLE,
    TUR_YENI,
    cumleler,
    iyelik_ekli_mi,
    kirilim_ifadesi,
    tamlayan,
    yonelme,
)

# ── Fikstür: GERÇEK katalogdan (demo/packs/modul/oee + sektor/boyahane/parti) ────────
#
# ⚠ `toplam_fire_kg`'ın görünen adı planın `§18.7` örneğiyle aynı ("toplam fire (kg)");
# `fire_orani_yuzde`'ninki cube YAML'ındaki ilk sinonim ("fire oranı"). İkisi de **etiket**,
# hiçbiri alan adı değil.
_SEMA = {
    "version": "kapi-1",
    "cubes": [
        {"name": "oee", "display": "OEE", "base_object": "oee_vardiya",
         "measures": ["ort_oee", "toplam_fire_kg", "fire_orani_yuzde", "toplam_durus_dakika"],
         "dimensions": ["makine", "vardiya", "hat", "neden"],
         "time_dimensions": ["tarih"],
         "measure_synonyms_display": {
             "ort_oee": "OEE", "toplam_fire_kg": "toplam fire (kg)",
             "fire_orani_yuzde": "fire oranı", "toplam_durus_dakika": "duruş"},
         "dimension_labels": {"makine": "makine", "vardiya": "vardiya", "hat": "hat",
                              "neden": "duruş nedeni"}},
        {"name": "parti", "display": "parti", "base_object": "partiler",
         "measures": ["toplam_ciro", "fire_orani_yuzde"],
         "dimensions": ["musteri", "kumas_cinsi", "operator"],
         "time_dimensions": ["tarih"],
         "measure_synonyms_display": {"toplam_ciro": "ciro",
                                      "fire_orani_yuzde": "fire oranı"},
         "dimension_labels": {"musteri": "müşteri", "kumas_cinsi": "kumaş cinsi",
                              "operator": "operatör"}},
    ],
}

_CAPA = {                       # 📌 RAM-3 · ort_oee · vardiya · bu ay   (`§5.1`)
    "cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"],
    "period_expr": "bu ay",
    "filters": [{"dimension": "makine", "operator": "eq", "value": "RAM-3"}],
}

_ADAYLAR = [
    Aday(kimlik="oee.toplam_fire_kg", etiket="toplam fire (kg)", cube="oee", kip="leksik"),
    Aday(kimlik="oee.fire_orani_yuzde", etiket="fire oranı", cube="oee", kip="leksik"),
]


class _Niyet:
    """`app/niyet.Niyet`'in bu modülün okuduğu **tek** alanı (`kirilimlar`)."""

    def __init__(self, kirilimlar):
        self.kirilimlar = list(kirilimlar)


def _metinler(oneriler):
    return [o.metin for o in oneriler]


# ── ① `§5.1` — ŞERİDİN KENDİSİ ───────────────────────────────────────────────────


def test_S51_SERIDI_planin_ornegiyle_ayni_KALIPTA():
    """🔴 `§5.1` — planın şeridi birebir kuruluyor mu.

    Planın örneği her satırı **başka bir adaydan** çiziyor (bir illüstrasyon, bir kural
    değil); bu modülün kuralı aday başına deterministiktir. O yüzden iki satır **birebir**,
    ikisi **kalıbıyla** ölçülür — ve dördü de aynı koşumda çıkmak zorundadır.
    """
    out = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA)
    m = _metinler(out)
    # 🔴 `§40` — KULLANICI KARARI (2026-08-13): öngörü bir öbek değil **TAM CÜMLE**.
    # Planın `§5.1` örneği (`«… — bu ay»`) bir **öbekti**; kullanıcı ekranda görüp
    # reddetti: *«cümle bile değil … tam cümle öngörüsü»*. Kapı **kaldırılmadı**,
    # yeni kalıba taşındı: içerik aynı (varlık · ölçü · dönem), biçim cümle.
    assert any("RAM-3" in s and "fire oranı" in s for s in m), (
        f"🔴 çapalı ölçü cümlesi yok: {m}")
    assert any(s.startswith("bu ay makineye göre toplam fire (kg)") for s in m), (
        f"🔴 YENİ KONU cümlesi yok: {m}")
    assert any(s.endswith("ekle (aynı kırılım · aynı dönem)") for s in m), (
        f"🔴 *«… ekle (aynı kırılım · aynı dönem)»* satırı yok: {m}")
    assert any(s.endswith(" neden bu seviyede?") for s in m), f"🔴 makro satırı yok: {m}"


def test_CAPA_YOKSA_rapor_ustunde_bandi_BOS():
    """🔴 Görevin bağlayıcı kuralı: *«çapa yoksa BU RAPOR ÜZERİNDE boş — uydurma çapa yok»*.

    🅑 Mutasyon: `cumleler` içindeki `if c else []` kaldırılırsa bu yüklem kırılır.
    """
    out = cumleler(_ADAYLAR, capa=None, schema=_SEMA)
    assert out, "🔴 çapasızken hiç öneri dönmedi — şerit tamamen sustu."
    assert all(o.grup == GRUP_YENI for o in out), (
        f"🔴 çapa yokken çapalı bant doldu: {[(o.grup, o.metin) for o in out]}")


def test_IKI_BANT_DA_TEMSIL_EDILIR():
    """`§6/Thread 3`'ün asıl kazancı *«iki şerit gösteriliyor»*dur — üst bant tavanı
    yerse alt bant görünmez olur ve kopuş yine tahmine kalır."""
    out = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, limit=3)
    gruplar = {o.grup for o in out}
    assert len(out) == 3, f"🔴 tavan aşıldı/eksik kaldı: {len(out)}"
    assert gruplar == {GRUP_RAPOR, GRUP_YENI}, f"🔴 bir bant tamamen düştü: {gruplar}"


def test_LIMIT_TAVANI_ASILMAZ():
    """`FAZ 6.4` — şerit ≤7. Tavan `app/oneri.VARSAYILAN_LIMIT`'ten **ödünç alınır**."""
    from app.oneri import VARSAYILAN_LIMIT

    assert len(cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA)) <= VARSAYILAN_LIMIT
    assert cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, limit=0) == []


# ── ② `§18.7` — HAM ALAN ADI CÜMLEYE GİRMEZ ──────────────────────────────────────


def test_HAM_ALAN_ADI_hicbir_cumlede_GECMEZ():
    """🔴 **Fazın kusuru buydu**: `/oneri` `fire` · `su` · `set` gibi ham parçalar
    döndürüyordu. Katalogdaki hiçbir **iç ad** bir cümlede görünemez.

    🅑 Mutasyon: `_olcu_etiketi`/`_boyut_etiketi` ham ada düşerse bu yüklem kırılır.
    """
    ic_adlar = {"ort_oee", "toplam_fire_kg", "fire_orani_yuzde", "toplam_durus_dakika",
                "kumas_cinsi", "musteri", "operator"}
    for capa in (None, _CAPA):
        for o in cumleler(_ADAYLAR, capa=capa, schema=_SEMA,
                          niyet=_Niyet(["makine", "neden"])):
            dusuk = o.metin.lower()
            assert not any(ad in dusuk for ad in ic_adlar), (
                f"🔴 ALAN ADI SIZDI: {o.metin!r}")
            assert "_" not in o.metin, f"🔴 alt çizgi = iç ad kalıbı: {o.metin!r}"


def test_ETIKETI_OLMAYAN_BOYUT_cumleye_GIRMEZ():
    """Şema verilmezse boyut etiketi bilinmez → *«… göre»* kuruluşu **kurulmaz**.
    Ham `makine` yazmaktansa cümleyi kısa bırakmak yeğdir (`§18.7`)."""
    out = cumleler(_ADAYLAR, capa=_CAPA, schema=None, niyet=_Niyet(["makine"]))
    assert out, "🔴 şemasız hiç cümle kurulmadı — etiket adaylardan da geliyordu."
    assert not any("göre" in o.metin or "bazında" in o.metin for o in out), (
        f"🔴 etiketsiz boyut cümleye girdi: {_metinler(out)}")


# ── ③ `§6/Thread 3` — TEMSİL EDİLEBİLİRLİK 🆈 ────────────────────────────────────


def test_CAPRAZ_KUP_ADAYI_rapor_ustunde_BANDINA_GIRMEZ():
    """🔴 `§6/Thread 3` kırılma 1: *«BU RAPOR ÜZERİNDE önerisi JOIN gerektiriyor ve JOIN
    planlayıcı yasağı var»* → başka küpün ölçüsü çapanın kapsamına **giremez**.

    ⚠ Ama **kaybolmaz** da: `YENİ KONU` bandında durur — kopuş tahmin edilmiyor,
    iki şerit gösteriliyor.
    """
    # `Thread 3` turu: kullanıcı *«ciro»* yazıyor, çapa hâlâ `fire · RAM-3 · bu ay` →
    # çapraz küp adayı listenin **başında** (sıralamanın sahibi `app/oneri.ara`).
    capraz = Aday(kimlik="parti.toplam_ciro", etiket="ciro", cube="parti", kip="leksik")
    out = cumleler([capraz, *_ADAYLAR], capa=_CAPA, schema=_SEMA)
    ust = [o for o in out if o.grup == GRUP_RAPOR]
    assert all(o.cube == "oee" for o in ust), (
        f"🔴 JOIN gerektiren öneri çapalı banda girdi: {[(o.cube, o.metin) for o in ust]}")
    assert any(o.cube == "parti" for o in out if o.grup == GRUP_YENI), (
        f"🔴 çapraz küp adayı tamamen kayboldu: {_metinler(out)}")


def test_CAPA_KUPUNDEN_HIC_ADAY_YOKSA_ust_bant_SUSAR():
    """🔴 `§6/Thread 3` — kullanıcı konuyu değiştirdiyse (yazdığının çapa küpüyle hiçbir
    kesişimi yoksa) üst bant **susar**.

    Alternatifi şeridi kullanıcının **sormadığı** şeyle doldurmaktı: açık rapor hakkında
    makro/dönem satırları. ⚠ Çapa düşmüyor — yalnız o turda sunacak bir şeyi olmadığını
    beyan ediyor.
    """
    capraz = [Aday(kimlik="parti.toplam_ciro", etiket="ciro", cube="parti", kip="leksik")]
    out = cumleler(capraz, capa=_CAPA, schema=_SEMA)
    assert out, "🔴 hiç öneri dönmedi."
    assert all(o.grup == GRUP_YENI for o in out), (
        f"🔴 ilgisiz üst bant doldu: {[(o.grup, o.metin) for o in out]}")


def test_HER_CUMLE_TIKLANABILIR():
    """Görevin kuralı: her cümle ya bir `cube_query` taşır ya `TUR_NEDEN` gibi bir makrodur.
    Tıklanamayan bir öneri, bir menü satırı bile değildir."""
    out = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, niyet=_Niyet(["neden"]))
    for o in out:
        assert o.tiklanabilir, f"🔴 ölü satır: {o.metin!r} (tur={o.tur})"


def test_MAKRO_sorgu_TASIMAZ():
    """`§6/Thread 2`: *«neden bu seviyede?»* dört adımlık bir **makro**dur, tek bir
    `cube_query` değil. Ona sorgu iliştirmek, dört adımın birini koşup ötekileri
    sessizce düşürmek olurdu."""
    out = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA)
    makro = [o for o in out if o.tur == TUR_NEDEN]
    assert makro, "🔴 makro hiç üretilmedi."
    assert all(o.cube_query is None for o in makro), (
        f"🔴 makroya sorgu iliştirilmiş: {[o.cube_query for o in makro]}")


def test_URETILEN_HER_SORGU_beyaz_listeden_GECER():
    """🔴 🆈 **Sunulan her öneri, sunulmadan önce temsil edilebilir olmalı.**

    Ölçüt tahmin değil: üretilen her `cube_query` `cube_router.parse_cube_query`'nin —
    bu deponun **tek doğrulama boğazının** — beyaz listesinden geçirilir. Geçmeyen bir
    öneri tıklandığında sessizce ölürdü.
    """
    from app.cube_router import build_catalog, parse_cube_query

    _, index = build_catalog(_SEMA)
    out = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, niyet=_Niyet(["neden"]), limit=20)
    sorgulu = [o for o in out if o.cube_query is not None]
    assert sorgulu, "🔴 hiç sorgu üretilmedi."
    for o in sorgulu:
        assert parse_cube_query(json.dumps(o.cube_query), index) is not None, (
            f"🔴 TEMSİL EDİLEMEYEN ÖNERİ: {o.metin!r} → {o.cube_query}")


def test_ONCEKI_DONEM_ifadeleri_route_tarafindan_COZULUYOR():
    """Kapalı dönem tablosunun her değeri `date_filters` tarafından **çözülebilir**
    olmalı; olmayan bir ifadeyi öneri olarak sunmak boş bir tık üretirdi."""
    from app.cube_router import _norm, date_filters

    for kaynak, hedef in _ONCEKI_DONEM.items():
        assert date_filters(_norm(hedef)), (
            f"🔴 «{kaynak}» → «{hedef}» route tarafından ÇÖZÜLEMİYOR — sunulamaz.")


def test_DONEM_ONERISI_capanin_donemini_KAYDIRIR():
    """`TUR_DONEM`: aynı rapor, önceki dönem. Çözülmüş tarih filtreleri **düşürülür** —
    kalsalardı sorgu `period_expr` ile çelişirdi."""
    capa = {**_CAPA, "filters": [*_CAPA["filters"],
                                 {"dimension": "tarih", "operator": "gte",
                                  "value": "2026-08-01"}]}
    out = cumleler(_ADAYLAR, capa=capa, schema=_SEMA, limit=20)
    donem = [o for o in out if o.tur == TUR_DONEM]
    assert donem, f"🔴 dönem önerisi üretilmedi: {_metinler(out)}"
    cq = donem[0].cube_query
    assert cq["period_expr"] == "geçen ay", f"🔴 dönem kaymadı: {cq}"
    assert all(f["dimension"] != "tarih" for f in cq.get("filters") or []), (
        f"🔴 çözülmüş tarih filtresi kaldı — sorgu kendiyle çelişiyor: {cq}")


def test_NIYET_KIRILIMI_cumleye_TASINIR_ve_boyut_ICAT_EDILMEZ():
    """`§5.2`/`KÖK-1`: kırılım **kullanıcının kendi sözcüğünden** doğar. `Niyet` bir boyut
    eşleştirmediyse kırılım önerisi de yoktur — ikinci bir eşleştirici yazılmaz."""
    with_niyet = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA,
                          niyet=_Niyet(["neden"]), limit=20)
    kirilim = [o for o in with_niyet if o.tur == TUR_KIRILIM]
    assert kirilim, f"🔴 niyet boyutu cümleye taşınmadı: {_metinler(with_niyet)}"
    assert kirilim[0].metin.startswith("duruş nedenine göre "), (
        f"🔴 kırılım cümlesi yanlış kuruldu: {kirilim[0].metin!r}")
    assert kirilim[0].cube_query["dimensions"] == ["vardiya", "neden"], (
        f"🔴 çapanın kırılımı korunmadı: {kirilim[0].cube_query}")

    yalin = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, limit=20)
    assert not [o for o in yalin if o.tur == TUR_KIRILIM], (
        f"🔴 niyet yokken boyut İCAT EDİLDİ: {_metinler(yalin)}")


def test_CAPANIN_MEVCUT_OLCUSU_tekrar_ONERILMEZ():
    """Raporda **zaten olan** ölçüyü *«ekle»* diye sunmak, olmayan bir seçenek sunmaktır."""
    out = cumleler(_ADAYLAR, capa={**_CAPA, "measures": ["toplam_fire_kg"]},
                   schema=_SEMA, limit=20)
    ust = [o for o in out if o.grup == GRUP_RAPOR and o.tur == TUR_OLCU_EKLE]
    for o in ust:
        assert o.cube_query["measures"] != ["toplam_fire_kg"], (
            f"🔴 açık rapor kendi kendine öneriliyor: {o.metin!r}")
        assert not o.metin.startswith("toplam fire (kg) ekle"), (
            f"🔴 zaten olan ölçü *«ekle»* diye sunuldu: {o.metin!r}")


def test_AYNI_ETIKETLI_IKI_ONERI_kup_adiyla_AYRILIR():
    """🔴 `§6/Thread 4` kırılma 1: *«aynı etiketli iki öneri — kullanıcı ayırt edemez»*.

    Katalog tutarsızlığı **çözülmez** (o bir katalog borcudur) ama tıklama bir **kumar**
    olmaktan çıkar: çakışan cümleler küpün **görünen adıyla** ayrılır.
    """
    ikiz = [Aday(kimlik="oee.fire_orani_yuzde", etiket="fire oranı", cube="oee",
                 kip="leksik"),
            Aday(kimlik="parti.fire_orani_yuzde", etiket="fire oranı", cube="parti",
                 kip="leksik")]
    out = cumleler(ikiz, capa=None, schema=_SEMA)
    m = _metinler(out)
    assert len(m) == len(set(m)), f"🔴 AYIRT EDİLEMEZ İKİ ÖNERİ: {m}"
    assert any("fire oranı" in s and "(OEE)" in s for s in m), f"🔴 ayırıcı yanlış: {m}"
    assert any("fire oranı" in s and "(parti)" in s for s in m), f"🔴 ayırıcı yanlış: {m}"


def test_AYNI_GIRDI_AYNI_CIKTI():
    """🔴 `E-8` — modül **saf**: sıcak yolda ikinci bir LLM turu, bir sorgu ya da bir
    IO yok. Aynı girdi iki koşumda **birebir** aynı çıktıyı vermeli."""
    a = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, niyet=_Niyet(["neden"]))
    b = cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, niyet=_Niyet(["neden"]))
    assert a == b, "🔴 aynı girdi iki farklı şerit üretti — modül saf değil."


def test_SAF_MODUL_llm_sorgu_io_ICERMEZ():
    """🅑 **Yapısal kapı** (`test_YENI_DILBILIM_YAZILMADI` deseni): saflık bir niyet
    beyanı değil, import grafiğinin **ölçülebilir** bir özelliğidir.

    İzinli import kümesi dar: dil çekimi `app.ek`'in, tavan sayısı `app.oneri`'nindir.
    Buraya bir `llm` · `wren_service` · `requests` importu girerse şerit sıcak yolda
    ikinci bir tur açmış olur (`E-8`).
    """
    from app import oneri_cumle

    izinli = {"__future__", "re", "dataclasses", "typing", "collections.abc",
              "app.ek", "app.oneri"}
    agac = ast.parse(Path(oneri_cumle.__file__).read_text(encoding="utf-8"))
    bulunan: set[str] = set()
    for d in ast.walk(agac):
        if isinstance(d, ast.Import):
            bulunan |= {a.name for a in d.names}
        elif isinstance(d, ast.ImportFrom) and d.module:
            bulunan.add(d.module)
    assert bulunan <= izinli, f"🔴 SAFLIK İHLALİ — beklenmeyen import: {bulunan - izinli}"
    assert "open(" not in Path(oneri_cumle.__file__).read_text(encoding="utf-8"), (
        "🔴 modülde dosya IO var — öneri şeridi bir okuyucu değildir.")


# ── ④ MORFOLOJİ — gerçek katalog adlarıyla, kural başına ayrı yüklem ─────────────


def test_MORFOLOJI_duz_yonelme_gercek_boyut_adlari():
    """Ünlü uyumu + kaynaştırma `y`: `app/ek.py`'nin işi, burada **çağrılıyor**."""
    beklenen = {"makine": "makineye", "vardiya": "vardiyaya", "müşteri": "müşteriye",
                "operatör": "operatöre", "eğitim": "eğitime", "tedarikçi": "tedarikçiye",
                "departman": "departmana", "aşama": "aşamaya"}
    for etiket, dogru in beklenen.items():
        assert yonelme(etiket) == dogru, f"🔴 «{etiket}» → {yonelme(etiket)!r} ≠ {dogru!r}"


def test_MORFOLOJI_iyelik_tamlamasi_kaynastirma_N_alir():
    """🔴 Bu modülün `ek.py` üstüne koyduğu **birinci** kural: belirtisiz isim
    tamlamasında hâl eki `-n-` kaynaştırmasıyla gelir.

    ⚠ Kaynaştırma olmasaydı *«kumaş cinsiye»* · *«iplik grubuya»* gibi **hiçbir Türkçe
    konuşurun yazmayacağı** biçimler doğardı; ve bunlar tam olarak gerçek katalog
    etiketleridir (`demo/packs/sektor/boyahane/cubes/parti`).
    """
    beklenen = {"kumaş cinsi": "kumaş cinsine", "iplik grubu": "iplik grubuna",
                "yaş grubu": "yaş grubuna", "haftanın günü": "haftanın gününe",
                "ton derinliği": "ton derinliğine", "duruş nedeni": "duruş nedenine"}
    for etiket, dogru in beklenen.items():
        assert iyelik_ekli_mi(etiket), f"🔴 «{etiket}» iyelik zinciri sayılmadı."
        assert yonelme(etiket) == dogru, f"🔴 «{etiket}» → {yonelme(etiket)!r} ≠ {dogru!r}"


def test_MORFOLOJI_tek_sozcukte_kaynastirma_UYGULANMAZ():
    """Ters yön: *«müşteri»* bir tamlama değildir. Kural genişletilseydi *«müşterine»*
    gibi yanlış bir çekim doğardı — bir kuralı fazla uygulamak, hiç uygulamamak kadar
    görünür bir kusurdur."""
    assert not iyelik_ekli_mi("müşteri") and yonelme("müşteri") == "müşteriye"
    assert not iyelik_ekli_mi("tedarikçi") and yonelme("tedarikçi") == "tedarikçiye"


def test_MORFOLOJI_unlu_dusmesi_kapali_listeden():
    """🔴 İkinci kural: *«şehir» → «şehre»* (`ek.py`'nin `_YUMUSAMAZ` deseni: kural değil
    **liste**). `test_next_steps.py` fikstüründeki gerçek etiket."""
    assert yonelme("şehir") == "şehre", f"🔴 {yonelme('şehir')!r}"
    assert yonelme("isim") == "isme" and yonelme("akıl") == "akla"


def test_MORFOLOJI_sert_unsuz_sonunda_EK_ISTENMEZ():
    """🔴 Üçüncü kaçış kapısı — ve bu **ölçülmüş** bir kusur.

    `p·ç·t·k` sonrası yumuşama bir kurala değil bir **listeye** bağlıdır
    (`ek.py::_YUMUSAMAZ`) ve o liste anlatıcının sözcükleriyle kalibre edilmiştir. Bu
    deponun bu sınıftaki **üç** boyut etiketinin **üçü de** yanlış çekimleniyor:

        hat → «hada» ⊘ · renk → «renğe» ⊘ · cinsiyet → «cinsiyede» ⊘

    Üçü de gerçek katalog etiketidir (`oee` · `parti`). Onarım motora kural eklemek değil,
    **ek istemeyen** bir kuruluş kurmaktır.
    """
    for etiket in ("hat", "renk", "cinsiyet"):
        assert kirilim_ifadesi(etiket) == f"{etiket} bazında", (
            f"🔴 güvensiz ek takıldı: {kirilim_ifadesi(etiket)!r}")
    assert kirilim_ifadesi("makine") == "makineye göre", "🔴 güvenli dal da söndü."
    assert kirilim_ifadesi("kumaş cinsi") == "kumaş cinsine göre"


def test_MORFOLOJI_tamlayan_RAKAMLA_biten_varlik_adi():
    """🔴 `§5.1`'in gösterge cümlesi: *«RAM-3'ün …»*. Ek **rakamın okunuşuna** göre seçilir
    (*üç* → `'ün`), son harfe göre değil — TDK kuralı ve `ek.py`'nin `sayi=True` dalı.
    Son harfe bakan bir motor *«RAM-3'ın»* yazardı."""
    assert tamlayan("RAM-3") == "RAM-3'ün", f"🔴 {tamlayan('RAM-3')!r}"
    assert tamlayan("HAT-40") == "HAT-40'ın", f"🔴 {tamlayan('HAT-40')!r}"
    assert tamlayan("Merkez") == "Merkez'in"
    assert tamlayan("İstanbul") == "İstanbul'un"


def test_MORFOLOJI_okunusu_bilinmeyen_varlikta_EK_UYDURULMAZ():
    """🔴 *«uydurma ek ekleme»*: bir kısaltmanın eki **okunuşuna** bağlıdır (*ABC* →
    *be-ce* → `'nin`) ve okunuşu bilmiyoruz; noktalamayla biten bir değere ise ek
    hiç takılamaz. İkisinde de `None` = *«güvenle ek takamam»*."""
    assert tamlayan("ABC") is None
    assert tamlayan("1. Vardiya (08-16)") is None
    assert tamlayan("") is None


def test_IYELIK_ZINCIRI_kurulamazsa_ICIN_edatina_DUSULUR():
    """🔴 *«RAM-3'ün toplam fire (kg)»* eksik bir tamlamadır (doğrusu *«…firesi»*) ve o eki
    parantezli/birimli bir etikette üretmek uydurma olurdu. `için` edatı ek istemez ve her
    sözcükle çalışır; *«fire oranı»* ise iyelik ekini **zaten taşıdığı** için tamlamaya girer.
    """
    m = _metinler(cumleler(_ADAYLAR, capa=_CAPA, schema=_SEMA, limit=20))
    assert "RAM-3'ün fire oranı — bu ay" in m, f"🔴 {m}"
    assert "RAM-3 için toplam fire (kg) — bu ay" in m, f"🔴 {m}"


def test_SOZLESME_grup_ve_tur_KAPALI_KUME():
    """Şeridin tüketicisi (ön uç) bu iki kümeye göre çiziyor; üçüncü bir değer sessizce
    çizilmeyen bir satır demektir."""
    out = cumleler([*_ADAYLAR,
                    Aday(kimlik="parti.toplam_ciro", etiket="ciro", cube="parti",
                         kip="leksik")],
                   capa=_CAPA, schema=_SEMA, niyet=_Niyet(["neden"]), limit=20)
    turler = {TUR_OLCU_EKLE, TUR_KIRILIM, TUR_DONEM, TUR_NEDEN, TUR_YENI}
    assert {o.grup for o in out} <= {GRUP_RAPOR, GRUP_YENI}
    assert {o.tur for o in out} <= turler, f"🔴 kapalı küme dışı tür: {[o.tur for o in out]}"
    assert len({o.kimlik for o in out}) == len(out), "🔴 kimlik çakışması var."


# ── 🔴 İK1 — KULLANICININ YAZDIĞI DÖNEM CÜMLEYE GİRER (insan testi bulgusu) ──

def test_YAZILAN_DONEM_CUMLEYE_GIRER():
    """🔴 **İnsan testinde ölçüldü:** `bu ay fire` yazan kullanıcı `fire (parti)` görüyordu
    — yazdığı dönem **yok sayılıyordu**. Yarım bir cümle bir **etikettir** 🆡.

    ⚠ Kaynak `_ONCEKI_DONEM`'in anahtarlarıdır ve bu bir tercih değil bir **güvence**:
    o tablonun her değeri `route()` tarafından çözülebiliyor (bu dosyanın kendi kapısı
    bunu ölçer). Yani sunulan dönem, **koşulabilir** bir dönemdir.

    🅑 Mutasyon: `_yeni_konu`'daki `_yazilan_donem(soru)` çağrısı `""` yapılırsa kırılır.
    """
    from app.oneri_cumle import _yazilan_donem

    assert _yazilan_donem("bu ay fire") == "bu ay"
    assert _yazilan_donem("BU AY fire") == "bu ay", "büyük harf de tanınmalı ⑧"
    assert _yazilan_donem("bu yıl ciro") == "bu yıl"


def test_YAZILMAYAN_DONEM_UYDURULMAZ():
    """🔴 Kullanıcı dönem yazmadıysa cümle **dönemsiz** kalır.

    *Dönemsiz bir öneri hâlâ doğrudur; yanlış dönemli bir öneri değildir* 🅫. Ve bu
    modülün kendi kuralı zaten süzgeçten geri çözmeyi yasaklıyor (`_capa_oku`).
    """
    from app.oneri_cumle import _yazilan_donem

    assert _yazilan_donem("fire") == ""
    assert _yazilan_donem("") == ""
    # ⚠ 🅖 **Bilinen sınır, gizlenmiyor:** tablo *«şimdiki»* dönemleri anahtarlar
    # (`bu ay` → `geçen ay`), yani kullanıcı doğrudan *«geçen ay»* yazarsa eşleşme
    # **olmaz**. Tabloyu genişletmek bir ölçüm ister, bir sezgi değil 🆞.
    assert _yazilan_donem("geçen ay fire") == ""


def test_SAFLIK_KAPISI_DONEM_KAYNAGINI_SECTI():
    """⊙ **Kapı bir kaynak seçimini düzeltti ③🅑.** İlk yazımım `donem_capasi.
    DONEM_SECENEKLERI`'ni import etti; saflık kapısı reddetti ve **haklıydı** —
    `donem_capasi` yaprak değil (`cube_router`·`veri_araligi` çeker) ve bu modülün
    *«LLM yok, sorgu yok, IO yok»* ilanını kırardı.

    Bu yüklem o kararı **kilitler**: dönem kaynağı bu modülün **kendi** tablosudur.
    """
    import pathlib

    from tests._kod_ayikla import kodu_ayikla

    src = kodu_ayikla((pathlib.Path(__file__).resolve().parents[1] / "app"
                       / "oneri_cumle.py").read_text(encoding="utf-8"))
    assert "donem_capasi" not in src, (
        "🔴 saf modül `donem_capasi`'yı import ediyor — o modül `cube_router` ve "
        "`veri_araligi` çeker; saflık ilanı kırılır.")
