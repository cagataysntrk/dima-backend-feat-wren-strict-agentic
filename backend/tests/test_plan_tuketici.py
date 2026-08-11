"""FAZ O-4 tüketici — BOŞLUĞU DOLDURUYOR MU, ve DOLDURAMAYINCA NE SÖYLÜYOR.

Raporun `O-4` başarı ölçütü **iki dallı**: *«cevap üretiyor **ya da** neden üretemediğini
adım adım söylüyor»*. İkinci dal bir kaçış değil bir üründür — bugünkü karşılığı tek
cümlelik bir rettir ve kullanıcı ondan hiçbir şey öğrenemez.
"""

from __future__ import annotations

import json

import pytest

from app import plan_tuketici as pt
from app.plan_kosucu import PlanHatasi

ROWS = [{"makine": "RAM-1", "ort_oee": 0.58}, {"makine": "RAM-2", "ort_oee": 0.60},
        {"makine": "RAM-3", "ort_oee": 0.5245}, {"makine": "X", "ort_oee": 0.59}]
CQ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
PLAN = {"adimlar": [
    {"fiil": "SORGU", "cube_query": CQ},
    {"fiil": "BAGLA", "kaynak": "$1", "boyut": "makine", "olcu": "ort_oee"},
    {"fiil": "HESAPLA", "kaynak": "$1", "hedef": "$2", "boyut": "makine",
     "olcu": "ort_oee"}]}
SCHEMA = {"cubes": [{"name": "oee", "measures": ["ort_oee"],
                     "dimensions": ["makine"], "lower_is_better": []}]}


class _Motor:
    def cube_sql(self, cq): return "SELECT 1"
    def dry_plan(self, sql): return {}
    def query(self, sql, limit=None):
        return {"columns": ["makine", "ort_oee"], "rows": ROWS, "row_count": len(ROWS)}


class _Garson:
    """Sağlayıcı taklidi: `plan_kur` bir plan METNİ döndürür (gerçek sözleşme)."""

    sema_kullanir = False
    plan_kurabilir = True

    def __init__(self, plan): self._p = plan

    def plan_kur(self, question, catalog, sema=None):
        return json.dumps(self._p) if self._p else "{}"


@pytest.fixture(autouse=True)
def _bayrak_acik(monkeypatch):
    """⚠ Bayrak testte AÇIK tutulur — kapalı hâlin kendi kapısı ayrı (`test_BAYRAK…`)."""
    from app import plan_garson
    monkeypatch.setattr(plan_garson, "acik_mi", lambda *a, **k: True)


class _Istek:
    """`request.app.state.llm` — üretimdeki tek gerçek kaynak."""

    def __init__(self, llm):
        self.app = type("A", (), {"state": type("S", (), {"llm": llm})()})()


def _cevap(g, motor=None, soru="q"):
    return pt.cevap(_Istek(g), service=motor or _Motor(), schema=SCHEMA, soru=soru)


def test_BAYRAK_KAPALIYKEN_HIC_KONUSMAZ(monkeypatch):
    """🔴🔴 `KURAL B` — bayrak kapalıyken dal **hiç açılmaz**."""
    from app import plan_garson
    monkeypatch.setattr(plan_garson, "acik_mi", lambda *a, **k: False)
    assert _cevap(_Garson(PLAN)) is None


def test_PLAN_CIKMAZSA_MERDIVEN_BUGUNKU_GIBI():
    assert _cevap(_Garson(None)) is None


def test_SAGLAYICI_YOKSA_PATLAMAZ():
    """🔴 Ölçüldü (`EE19`, canlı): sağlayıcı çağıranın **yerelinden** okunuyordu ve
    deterministik yoldan gelindiğinde `UnboundLocalError` — bayrak KAPALIYKEN de.

    *Koşullu bağlanan bir ad, tanımsız bir addan daha sinsidir: statik olarak var,
    çalışırken yok.*
    """
    assert pt.cevap(_Istek(None), service=_Motor(), schema=SCHEMA, soru="q") is None
    assert pt.cevap(object(), service=_Motor(), schema=SCHEMA, soru="q") is None


def test_BOSLUKTA_CEVAP_URETIYOR():
    """🔴 Üç adım koştu, tek sorgu, ve cevabın içinde **bulgu** var — makbuz değil sonuç."""
    c = _cevap(_Garson(PLAN))
    assert c["source"] == "cube+llm"
    assert "3 adımda üretildi" in c["note"]
    assert "RAM-3" in c["note"], "BAGLA'nın seçtiği varlık cevaba girmedi"
    assert "%11,1" in c["note"], "HESAPLA'nın farkı cevaba girmedi"
    assert c["result"]["row_count"] == 4
    assert c["cube_query"] == CQ, "makbuz TIKLANABİLİR olmalı (O-5: /cube ile 0 LLM)"


def test_HAM_FLOAT_SIZMAZ():
    """⚠ `§AA1`'in dersi: `0.5245118291704627` bir cevap değil, bir sızıntıdır."""
    c = _cevap(_Garson(PLAN))
    assert "0.5245118" not in c["note"]


def test_KOSAMAYINCA_ADIM_ADIM_SOYLUYOR():
    """🔴🔴 `O-4`'ün İKİNCİ başarı ölçütü — *«neden üretemediğini adım adım söylüyor»*.

    Bugünkü karşılığı: *«Bu soru için güvenilir bir sorgu üretemedim.»*
    """
    # ⟳ Eskiden burada `TREND` vardı — `FAZ 2`'de **bağlandı**, yani artık koşuyor ve
    # bu kapı başka bir şeyi ölçmeye başlamıştı. Koşamayan gerçek bir durum seçildi:
    # katalogda karşılığı olmayan bir cube. *Bir kapının varsayımı da bayatlar.*
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "uydurma_kup"}},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "makine",
                         "olcu": "ort_oee"}]}
    c = _cevap(_Garson(plan))
    assert c["source"] is None, "koşamayan bir plan CEVAP VERMİŞ gibi görünemez"
    assert "1." in c["note"] and "2." in c["note"], "adımlar sayılmamış"
    # ⟳ Red mesajı **kesinleşti**: artık *"katalogda karşılanmıyor"* değil, hangi
    # alanın tanımsız olduğunu söylüyor. *Bir kapının beklediği metin, kapının ölçtüğü
    # davranışın kendisi değildir — davranış iyileşince metin de değişir.*
    assert "tamamlayamadım" in c["note"] and "diye bir cube YOK" in c["note"]


def test_KATALOG_DISI_SORGU_MOTORA_GITMEZ():
    """🔴 Beyaz liste planın İÇİNDE de geçerli — bir adım Discovery'ye dönüşemez."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "uydurma"}}]}
    # ⟳ Mesaj kesinleşti (bkz. `test_RED_HANGI_ALANIN_TANIMSIZ_OLDUGUNU_SOYLER`).
    with pytest.raises(PlanHatasi, match="diye bir cube YOK"):
        pt.calistir(plan, service=_Motor(), index={"oee": {"measures": ["ort_oee"]}})


def test_BEKLENMEYEN_ARIZA_MERDIVENI_BOZMAZ():
    """⚠ Fail-open: tüketici düşerse `None` döner ve bugünkü yol aynen sürer."""
    class _Patlak(_Motor):
        def query(self, sql, limit=None): raise RuntimeError("motor düştü")
    assert _cevap(_Garson(PLAN), _Patlak()) is None


def test_YEDI_FIILIN_YEDISI_DE_BAGLI():
    """🔴🔴 `FAZ 2`'nin ASIL İDDİASI — kapalı fiil kümesinin **tamamı** koşuyor.

    Ölçüldü (`FAZ O` sonu): 7 fiilin **3'ü** koşuyordu; `TREND`·`AYRISTIR`·`KIYASLA`·
    `ANLAT` `PlanHatasi` veriyordu ve bayrağın kazancının sıfır olmasının **tek** sebebi
    buydu — gövdeleri hazırdı, yalnız bağlı değildi.

    ⚠ Bu kapı gövdelerin **doğru** çalıştığını değil, **bağlı** olduğunu ölçer. Doğruluk
    her gövdenin kendi testinde (`yoy` · `contribution` · `narration_guard`).
    """
    from app.plan_kosucu import ICSEL_FIILLER
    from app.plan_semasi import FIILLER
    from app.plan_tuketici import _govdeler

    # ⚠ İçsel fiil listesi **elle yazılmıyor**, `plan_kosucu`'dan okunuyor. İlk hâli bir
    # kopyaydı ve `FAZ 7b`'de `MATRIS`/`SIRALA` eklenince **bayatladı**: kapı onları
    # *«bağlanmamış»* sandı. *Bir kümeyi tarif eden liste, kümeden üretilmiyorsa er ya
    # da geç onu yanlış tarif eder.*
    g = _govdeler(_Motor(), SCHEMA, {"lower_is_better": []})
    eksik = set(FIILLER) - set(ICSEL_FIILLER) - set(g)
    assert not eksik, f"🔴 gövdesi bağlanmamış fiil(ler): {sorted(eksik)}"
    # 🔴 Ve ters yön: içsel ilan edilen bir fiil gerçekten koşabiliyor mu?
    assert set(ICSEL_FIILLER) <= set(FIILLER), (
        "içsel ilan edilen bir fiil kapalı kümede YOK — şema onu hiç üretemez")


def test_ANLAT_LLM_CAGIRMAZ():
    """🔴 Bir anlatı fiilini LLM'e bağlamak, planın her turuna bir çağrı daha eklerdi —
    tam da `E6`'nın ve bu turun A/B'sinin cezalandırdığı şey.

    *Bir cümleyi model kurmadan da doğru kurabiliyorsan, modeli çağırmak bir yetenek
    değil bir masraftır.*
    """
    import inspect

    from app import plan_tuketici
    kaynak = inspect.getsource(plan_tuketici._govdeler)
    # ⚠ Dilim **yalnız `_anlat`ın gövdesi** olmalı. İlk hâl `split("def _anlat")[1]`
    # diyordu ve `FAZ 7` üç fonksiyon daha ekleyince `select_cube_query` (`SUZ`'ün
    # gövdesi) `select_cube` diye okundu — kapı **kendi yanlış-pozitifini** üretti.
    # *Bir kaynak dilimini fonksiyon sınırına değil metne göre kesmek, sonraki
    # fonksiyonu da ölçmektir.*
    _sonra = kaynak.split("def _anlat", 1)[1]
    _govde = _sonra.split("\n    def ", 1)[0].split("\n    return ", 1)[0]
    for yasak in ("llm.", "generate", "select_cube(", "_ask("):
        assert yasak not in _govde, f"ANLAT gövdesinde `{yasak}` geçiyor"
    assert "narration_guard" in _govde, "ANLAT guard'sız — sayı doğrulanmıyor"


def test_HER_ADIMIN_SONUCU_DONUYOR():
    """🔴 `FAZ 5` — hesaplanan malzeme **atılmıyor**.

    Bugüne kadar `plan_tuketici` her `SORGU`'nun sonucunu biriktiriyor ama yalnız
    **sonuncusunu** döndürüyordu. Çok bölümlü rapor/pano için gereken ara sonuçlar
    üretilip çöpe gidiyordu.

    *Bir maliyeti ödeyip ürününü atmak, onu hiç ödememekten pahalıdır: hem para gider
    hem cevap.*
    """
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "ANLAT", "kaynaklar": ["$1", "$2"]}]}
    c = _cevap(_Garson(plan))
    assert len(c["bolumler"]) == 2, "iki sorgunun sonucu da dönmeliydi"
    assert all(b["cube_query"] == CQ for b in c["bolumler"]), (
        "her bölüm kendi sorgusunu taşımalı — yoksa `/cube` ile yeniden koşulamaz (O-5)")
    assert all(b["result"]["row_count"] == 4 for b in c["bolumler"])


def test_GOVDE_SEMANIN_YASAKLADIGI_ALANI_OKUMUYOR():
    """🔴🔴 **ÜÇ FİİL YAPISAL OLARAK ÖLÜYDÜ — ve hiçbir kapı görmüyordu.**

    Ölçüldü (2026-08-09, canlı plan üretimi): `KIYASLA`·`AYRISTIR`·`TREND` **hiç**
    kullanılmadı. Sebep:

    | fiil | şemanın verdiği | gövdenin okuduğu |
    |---|---|---|
    | `KIYASLA` | `kaynak` | `cube_query` |
    | `AYRISTIR` | `kaynak` | `cube_query`, `mode` |
    | `TREND` | `kaynak` | `cube_query`, `mode` |

    `additionalProperties: False` + `_plani_oku`'nun fazla-alan reddi birleşince,
    **şema-geçerli** bir adım gövdeye `cube_query = {}` olarak varıyordu. Fiil
    bağlıydı, çağrılıyordu, ve **her zaman boş** dönüyordu.

    ⊙ Bu, istem kusurunun **ayna görüntüsüydü**: orada model sözleşmeyi hiç görmüyordu,
    burada **gövde** başka bir sözleşmeye göre yazılmıştı. Aynı `KAT-1`, iki uçta —
    ve ikisi de *çelişki* değil **eksiklik** olarak göründü.

    ⚠ Bu kapı bir daha olmasın diye var: gövde ne okuyorsa şema onu **verebilmeli**.
    """
    import inspect
    import re

    from app.plan_semasi import ISTEGE_BAGLI_ALANLAR, ZORUNLU_ALANLAR
    from app import plan_tuketici

    kaynak = inspect.getsource(plan_tuketici._govdeler)
    # `_govdeler` her fiili bir iç fonksiyonda tutar; adı fiilden türemez, bu yüzden
    # dönüş sözlüğünden eşleştiriyoruz — tek sahip orası.
    esleme = dict(re.findall(r'"([A-Z]+)":\s*(_[a-z_]+)', kaynak.split("return {", 1)[1]))
    assert len(esleme) >= 8, f"gövde eşlemesi okunamadı: {esleme}"

    ihlal: dict[str, list[str]] = {}
    for fiil, ad in esleme.items():
        govde = kaynak.split(f"def {ad}", 1)[1].split("\n    def ", 1)[0]
        okunan = set(re.findall(r"""a(?:\.get\(|\[)["']([a-z_]+)["']""", govde))
        izin = set(ZORUNLU_ALANLAR.get(fiil, ())) | set(ISTEGE_BAGLI_ALANLAR.get(fiil, ()))
        fark = sorted(okunan - izin)
        if fark:
            ihlal[fiil] = fark
    assert not ihlal, (
        f"🔴 Gövde şemanın VERMEDİĞİ alanı okuyor → fiil yapısal olarak ÖLÜ: {ihlal}\n"
        "Ya şemaya ekle (`ZORUNLU_ALANLAR`/`ISTEGE_BAGLI_ALANLAR`) ya gövdeyi düzelt. "
        "⚠ Bir fiili bağlamak, onu ulaşılabilir yapmaz.")


def test_ISTEGE_BAGLI_ALAN_DUSURULMEZ():
    """⚠ Şemanın izin verdiği bir planı **doğrulayıcının** reddetmesi, iki sahibin
    ayrışmasıdır. İkisi de aynı sözlükten okuyor."""
    from app.plan_garson import _plani_oku
    plan = {"adimlar": [{"fiil": "TREND", "cube_query": CQ, "mode": "mom"}]}
    assert _plani_oku(json.dumps(plan)) is not None, "isteğe bağlı `mode` düşürüldü"


def test_BOLUMLER_FIILE_GORE_DEGIL_TIPE_GORE():
    """🔴🔴 Ölçüldü (canlı `FF8`): tek `TREND` adımlı bir plan `yoy.compute` ile satır
    **üretti** ama `sonuclar` yalnız `SORGU` topladığı için cevap `source=cube+llm`
    rozetiyle **0 satır** döndü ve hiçbir şey söylemedi.

    *Bir kusuru fiilin adıyla düzeltmek, aynı kusuru sıradaki fiilde yeniden yazmaya
    söz vermektir.* — Toplama artık `CIKTI_TIPI`'ne bakıyor.
    """
    plan = {"adimlar": [{"fiil": "TREND", "cube_query": CQ}]}
    c = _cevap(_Garson(plan))
    assert c is not None and len(c["bolumler"]) == 1, c
    assert c["result"]["row_count"] == 4, "TREND'in satırları cevaba girmedi"


def test_BOS_SONUC_SESSIZ_KALMAZ():
    """🔴 Boş bir cevabı açıklamadan vermek, kullanıcının onu bir **hata** sanmasına
    izin vermektir. Merdivenin geri kalanı bunu zaten söylüyor."""
    class _Bos(_Motor):
        def query(self, sql, limit=None):
            return {"columns": [], "rows": [], "row_count": 0}

    c = _cevap(_Garson({"adimlar": [{"fiil": "SORGU", "cube_query": CQ}]}), _Bos())
    assert "hiçbir adım satır döndürmedi" in c["note"], c["note"]


def test_RED_HANGI_ALANIN_TANIMSIZ_OLDUGUNU_SOYLER():
    """🔴 *«tanımsız cube/ölçü/boyut»* bir teşhis değildir.

    Ölçüldü (canlı `HH1`): *«adım 3: `oee` sorgusu katalogda karşılanmıyor»* — hangi
    ölçü? hangi boyut? Ne kullanıcı bilebilirdi ne de **onarım turu**, çünkü model de
    aynı mesajı okuyor.

    ⚠ `parse_cube_query` **değişmedi**: o bir kapıdır, bir tanıcı değil. Teşhis onun
    **yanında** üretiliyor — aynı indeksten. *Bir reddi gerekçesiz vermek, onu iki kez
    öğrenmeye razı olmaktır.*
    """
    from app.plan_kosucu import PlanHatasi
    import pytest as _pt

    IDX = {"oee": {"measures": ["ort_oee"], "dimensions": ["makine"]}}
    with _pt.raises(PlanHatasi, match="diye bir cube YOK"):
        pt.calistir({"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "yok"}}]},
                    service=_Motor(), index=IDX)
    with _pt.raises(PlanHatasi, match="boyut"):
        pt.calistir({"adimlar": [{"fiil": "SORGU", "cube_query": {
            "cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya"]}}]},
            service=_Motor(), index=IDX)
    with _pt.raises(PlanHatasi, match="ölçü"):
        pt.calistir({"adimlar": [{"fiil": "SORGU", "cube_query": {
            "cube": "oee", "measures": ["uydurma"]}}]}, service=_Motor(), index=IDX)


def test_BG_SECILMEYEN_NONE_DIYE_YAZILMAZ():
    """🔴🔴 `§BG` — ölçüldü (curl `Y` turu): *«bu yıl hangi operatör en çok rework
    yaptı»* → kaynak sorgu **0 satır** döndü, `BAGLA` seçecek bir şey bulamadı ve cümle
    şu oldu:

        «**None** seçildi (`rework_sayisi` = …)»

    Kullanıcıya bir Python değeri sızdı ve üstelik **bir seçim yapılmış gibi** sunuldu.

    *Bir seçimin yapılmadığını söylemek, yapılmış gibi bir ad yazmaktan her zaman iyidir
    — çünkü ikincisi bir cevap gibi okunur.*"""
    from app import plan_tuketici

    plan = {"adimlar": [{"fiil": "BAGLA", "olcu": "rework_sayisi", "boyut": "operator"}]}
    metin = plan_tuketici._bulgu_metni(plan, {"ciktilar": [(None, None)]})
    assert "None" not in metin
    assert "seçilecek bir satır çıkmadı" in metin


def test_BG_GERCEK_SECIM_BOZULMADI():
    """`KURAL B` — gerçek bir seçim varken cümle bayt bayt bugünküdür."""
    from app import plan_tuketici

    plan = {"adimlar": [{"fiil": "BAGLA", "olcu": "rework_sayisi", "boyut": "operator"}]}
    metin = plan_tuketici._bulgu_metni(plan, {"ciktilar": [("MURAT DEMİR", 42)]})
    assert "MURAT DEMİR" in metin and "seçildi" in metin
