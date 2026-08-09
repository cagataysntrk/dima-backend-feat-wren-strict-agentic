"""FAZ O-2 — PLAN ÇALIŞTIRICISININ KAPISI.

Bu kapı **zincirin kurulabildiğini** kanıtlar: `SORGU → BAGLA → HESAPLA` bir soruyu
üç adımda cevaplıyor ve her adım bir öncekinin çıktısını **girdi olarak** alıyor.

⊙ Raporun `B3` boşluğu tam buydu: mutfak her adımı yapabiliyordu ama bir adımın çıktısını
ötekinin girdisine çeviren bir şey yoktu. Bu kapı o halkanın **kurulduğunu** ölçer.
"""

from __future__ import annotations

import pytest

from app.plan_kosucu import PlanHatasi, kos

ROWS = [{"m": "RAM-1", "v": 0.58}, {"m": "RAM-2", "v": 0.60},
        {"m": "RAM-3", "v": 0.5245}, {"m": "X", "v": 0.59}]


def _kos(plan, **kw):
    return kos(plan, sorgu_kos=lambda cq: ROWS, **kw)


def test_ZINCIR_KURULUYOR():
    """🔴🔴 `B3`'ün kapısı — bir adımın **çıktısı** ötekinin **girdisi** oluyor."""
    r = _kos({"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "oee", "measures": ["v"]}},
        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"},
        {"fiil": "HESAPLA", "kaynak": "$1", "hedef": "$2", "boyut": "m", "olcu": "v"}]})
    assert r["ciktilar"][1] == ("RAM-3", 0.5245), "BAGLA hedefi seçemedi"
    h = r["ciktilar"][2]
    assert h["fark_yuzde"] == -11.1 and h["akran_sayisi"] == 3
    assert r["sorgu_sayisi"] == 1, "üç adımlık plan tek sorgu koşmalı"


def test_ILERI_REFERANS_TURU_DUSURUR():
    """⚠ `$3` üçüncü adımdayken **henüz yoktur**. Şema sıra bilmez; kapı burada."""
    with pytest.raises(PlanHatasi, match=r"\$3"):
        _kos({"adimlar": [{"fiil": "BAGLA", "kaynak": "$3", "boyut": "m", "olcu": "v"}]})


def test_BAGLANMAMIS_FIIL_SESSIZCE_ATLANMAZ():
    """🔴 Şemada olup çalıştırıcıda olmayan bir fiil **turu düşürür**.

    *Bir fiili şemaya koyup çalıştırıcıda unutmak, onu sessizce yalan yapmaktır.*
    """
    # ⟳ Plan **geçerli** olmalı ki test bağlanmamış fiili ölçebilsin: tek adımlık
    # `ANLAT($1)` artık `dogrula`da ileri referans olarak düşüyor (kendi kendine
    # referans) ve o zaman bu kapı **başka bir şeyi** ölçmüş olurdu.
    with pytest.raises(PlanHatasi, match="O-4"):
        _kos({"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "oee"}},
                          {"fiil": "TREND", "kaynak": "$1"}]})


def test_SORGU_BUTCESI_ASILAMAZ():
    """⚠ Bütçe aşımında **kısmi cevap yok**: hangi adımın eksik olduğunu kullanıcı aramaz."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "oee"}}] * 3}
    with pytest.raises(PlanHatasi, match="bütçe"):
        _kos(plan, azami_sorgu=2)


def test_BOS_PLAN_REDDEDILIR():
    with pytest.raises(PlanHatasi, match="boş"):
        _kos({"adimlar": []})


def test_YON_BEYANDAN_OKUNUR():
    """🔴 `§W-C`: *az olan iyi* mi — sözlükten değil **`lower_is_better` beyanından**.

    Aynı satırlarda aynı plan, beyan değişince **başka bir hedef** seçmeli.
    """
    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "oee"}},
        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"}]}
    assert _kos(plan)["ciktilar"][1][0] == "RAM-3"          # yüksek iyi → en düşüğü seç
    assert _kos(plan, cube_meta={"lower_is_better": ["v"]}
                )["ciktilar"][1][0] == "RAM-2"              # az iyi → en yükseği seç


# ═══════════════════════════════════════════════════════════════════════════════
# FAZ 1 · `dogrula()` — KOŞMADAN ÖNCE, ve aynı geçişte DAG
# ═══════════════════════════════════════════════════════════════════════════════

from app.plan_kosucu import dogrula                                    # noqa: E402

CQ = {"cube": "oee", "measures": ["v"]}


def _sorgu(n=1):
    return [{"fiil": "SORGU", "cube_query": CQ} for _ in range(n)]


def test_DOGRULAMA_MOTORA_HIC_DOKUNMADAN_REDDEDER():
    """🔴🔴 Ölçülmüş çelişki kapandı.

    `plan_garson` şunu yazıyordu: *«Bir planı koşarken reddetmek, hiç kurmamaktan
    pahalıdır — ilk adım o ana kadar çoktan koşmuştur.»* Ama ileri referans denetimi
    `_coz` içindeydi, yani **tam da koşum anında**.

    Bu kapı, sahte koşucunun **hiç çağrılmadığını** iddia eder.
    """
    cagri = []
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "BAGLA", "kaynak": "$5", "boyut": "m", "olcu": "v"}]}
    with pytest.raises(PlanHatasi, match=r"\$5"):
        kos(plan, sorgu_kos=lambda cq: cagri.append(cq) or ROWS)
    assert cagri == [], "plan reddedildi ama motor ZATEN sorgulanmıştı"


def test_TIP_UYUSMAZLIGI_KOSUM_ONCESI_YAKALANIR():
    """🔴 `HESAPLA.hedef` bir **varlık** ister; `$1` bir `SORGU` ise **satırlar** gider.

    Şema bunu göremez: çıktı tipleri şemada değil, `plan_semasi.CIKTI_TIPI`'nde.
    Görmezse kusur `ilkeller.hesapla` içinde, koşum anında bulunurdu.
    """
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "HESAPLA", "kaynak": "$1", "hedef": "$1",
                         "boyut": "m", "olcu": "v"}]}
    with pytest.raises(PlanHatasi, match="varlik"):
        dogrula(plan)


def test_ANLAT_YALNIZ_SON_ADIM():
    """🔴 `oneOf` **konum** bilmez; bu kural bugüne kadar yalnız İSTEMDE yazılıydı —
    yani beyan ediliyor ama **denetlenmiyordu**."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "ANLAT", "kaynak": "$1"},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"}]}
    with pytest.raises(PlanHatasi, match="SON adım"):
        dogrula(plan)


def test_BUTCE_TOPLAM_OLARAK_ONCEDEN_DENETLENIR():
    """⚠ Eski hâl **artımlıydı**: ilk sorgular koşup sonra düşüyordu — aşımın bedeli
    zaten ödenmiş oluyordu."""
    cagri = []
    plan = {"adimlar": _sorgu(3)}
    with pytest.raises(PlanHatasi, match="bütçe"):
        kos(plan, sorgu_kos=lambda cq: cagri.append(cq) or ROWS, azami_sorgu=2)
    assert cagri == [], "bütçe aşıldı ama sorgular ZATEN koşmuştu"


def test_ULASILAMAZ_ADIM_REDDEDILIR():
    """⚠ `E9` — plan uzunluğu bir **ölçüdür**. Kimsenin kullanmadığı bir adım koşulur,
    ödenir ve **atılır**."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "BAGLA", "kaynak": "$2", "boyut": "m", "olcu": "v"}]}
    with pytest.raises(PlanHatasi, match="hiçbir adım"):
        dogrula(plan)


def test_DAG_KATMANLARI_BAGIMSIZLIGI_GOSTERIR():
    """🔴 `$n` **tek** veri kanalı olduğu için bağımlılık grafiği EKSİKSİZDİR — ve
    `depends_on` diye bir alan **eklenmeyecek**: bağımlılık çıkarılır, sorulmaz.

    ⊙ İki bağımsız `SORGU` **aynı katmanda**; onları kullanan adım bir sonrakinde.
    Bu, `FAZ 4`'ün paralel koşumunun zeminidir.
    """
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"},
                        {"fiil": "HESAPLA", "kaynak": "$2", "hedef": "$3",
                         "boyut": "m", "olcu": "v"}]}
    assert dogrula(plan) == [[1, 2], [3], [4]]


def test_ZINCIR_TEK_KATMANLI_DEGIL():
    """⚠ Bağımlı adımlar **ayrı** katmanlarda — yoksa paralelleştirme veriyi bozardı."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"},
                        {"fiil": "HESAPLA", "kaynak": "$1", "hedef": "$2",
                         "boyut": "m", "olcu": "v"}]}
    assert dogrula(plan) == [[1], [2], [3]]


# ═══════════════════════════════════════════════════════════════════════════════
# FAZ 3 · LİSTE DEĞERLİ REFERANS — referans dilinin TEK genişlemesi
# ═══════════════════════════════════════════════════════════════════════════════

def test_LISTE_REFERANSI_HER_OGESI_BIR_KENAR():
    """🔴 `kaynaklar: ["$1","$2"]` → **iki** kenar. Bağımlılık hâlâ ÇIKARILIYOR.

    ⊙ Aynı katmanda koşabilen iki `SORGU`, onları birlikte anlatan bir adımı bir sonraki
    katmana iter — yani liste genişlemesi DAG'ı bozmuyor, besliyor.
    """
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "ANLAT", "kaynaklar": ["$1", "$2"]}]}
    assert dogrula(plan) == [[1, 2], [3]]


def test_LISTE_ICINDEKI_ILERI_REFERANS_DA_YAKALANIR():
    """⚠ Genişleyen bir dil, genişlemeyen bir denetimle **sessiz bir delik** açar."""
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "ANLAT", "kaynaklar": ["$1", "$9"]}]}
    with pytest.raises(PlanHatasi, match=r"\$9"):
        dogrula(plan)


def test_LISTE_REFERANSI_COZULUYOR():
    """⊙ Yorumlayıcı listeyi **öğe öğe** çözer; gövde `$n` diye bir şey görmez."""
    gorulen = {}
    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "ANLAT", "kaynaklar": ["$1", "$2"]}]}
    kos(plan, sorgu_kos=lambda cq: ROWS,
        govdeler={"ANLAT": lambda a: gorulen.update(a) or "x"})
    assert gorulen["kaynaklar"] == [ROWS, ROWS], "liste çözülmedi"


def test_REFERANS_DILI_HALA_IFADE_DILI_DEGIL():
    """🔴 Genişleyen şey **çokluk**, ifade gücü DEĞİL.

    `plan_semasi`'nin kendi uyarısı: *«Bir referans dilini genişletmek, onu bir
    programlama diline çevirir — ve o dilin denetimi artık şemada değil,
    yorumlayıcıdadır.»* Bu kapı o sınırı kilitler.
    """
    from app.plan_semasi import ADIM_REFERANSI
    import re as _re
    _p = _re.compile(ADIM_REFERANSI)
    for yasak in ("$1.gelir", "$1 * 2", "$1+$2", "${1}", "$1[0]"):
        assert not _p.match(yasak), f"`{yasak}` referans sayıldı — ifade dili sızdı"


# ═══════════════════════════════════════════════════════════════════════════════
# FAZ 4 · PARALEL `SORGU` — ölçülmüş bir tavanla
# ═══════════════════════════════════════════════════════════════════════════════

def _iki_bagimsiz_sorgu():
    return {"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "SORGU", "cube_query": CQ},
                        {"fiil": "ANLAT", "kaynaklar": ["$1", "$2"]}]}


def test_CIKTI_ADIM_SIRASINA_YAZILIR_TAMAMLANMA_SIRASINA_DEGIL():
    """🔴🔴 Paralel koşumun **en sinsi** kusuru burada kapanıyor.

    `append` kullanılsaydı hızlı biten sorgu `$1`, yavaş olan `$2` olurdu — yani `$2`
    her koşumda **başka bir adımın** çıktısına bağlanabilirdi. Tekrar üretilebilirliğin
    sessizce kaybolduğu yer tam olarak orasıdır.

    ⊙ Kapı: birinci sorgu bilerek **yavaş**, ikincisi hızlı. Sıra yine `[1, 2]` olmalı.
    """
    import time as _t

    cagri = []

    def _yavas(cq):
        n = len(cagri)
        cagri.append(cq)
        _t.sleep(0.05 if n == 0 else 0.0)
        return [{"i": n}]

    r = kos(_iki_bagimsiz_sorgu(), sorgu_kos=_yavas, paralel=True,
            govdeler={"ANLAT": lambda a: "x"})
    assert r["ciktilar"][0] == [{"i": 0}] and r["ciktilar"][1] == [{"i": 1}], (
        f"çıktılar tamamlanma sırasına yazıldı: {r['ciktilar'][:2]}")


def test_PARALEL_VE_SERI_AYNI_SONUCU_VERIR():
    """⚠ Asıl ölçüt hız değil **denklik**: aynı plan, aynı sonuç."""
    seri = kos(_iki_bagimsiz_sorgu(), sorgu_kos=lambda cq: ROWS,
               govdeler={"ANLAT": lambda a: "x"})
    par = kos(_iki_bagimsiz_sorgu(), sorgu_kos=lambda cq: ROWS, paralel=True,
              govdeler={"ANLAT": lambda a: "x"})
    assert seri["ciktilar"] == par["ciktilar"]
    assert seri["sorgu_sayisi"] == par["sorgu_sayisi"] == 2


def test_PARALEL_KATMANDA_TUM_HATALAR_TOPLANIR():
    """🔴 Kardeşler **iptal edilmez, bitirilir** ve TÜM eksikler birlikte söylenir.

    Kullanıcıya bir eksiği söyleyip ötekini saklamak, ikinci turu boşa harcatır.
    ⚠ Kısmi sonuç yine de **yayımlanmaz** — fail-closed sürüyor.
    """
    def _hep_patlar(cq):
        raise ValueError("motor düştü")

    with pytest.raises(PlanHatasi) as e:
        kos(_iki_bagimsiz_sorgu(), sorgu_kos=_hep_patlar, paralel=True,
            govdeler={"ANLAT": lambda a: "x"})
    assert "adım 1" in str(e.value) and "adım 2" in str(e.value), (
        f"yalnız ilk hata söylendi: {e.value}")


def test_TAVAN_OLCULDU_SECILMEDI():
    """⚠ `AZAMI_ESZAMANLI` bir tercih değil bir **ölçüm sonucudur**
    (`lab/olcumler/motor_eszamanlilik.md`: 4 işçi 2,52× · 8 işçi 1,86×).

    *Bir tavanı yükseltmek bir kazanç değildir; ölçülmeden yükseltmek bir borçtur.*
    """
    from app.plan_kosucu import AZAMI_ESZAMANLI
    assert AZAMI_ESZAMANLI == 4


def test_TEK_SORGULU_KATMANDA_HAVUZ_KURULMAZ():
    """⚠ Bir iş için iş parçacığı havuzu kurmak net **negatif** getiridir."""
    import app.plan_kosucu as pk

    kuruldu = []
    _asil = __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]).ThreadPoolExecutor

    class _Casus(_asil):
        def __init__(self, *a, **k):
            kuruldu.append(True)
            super().__init__(*a, **k)

    import concurrent.futures as _cf
    _eski, _cf.ThreadPoolExecutor = _cf.ThreadPoolExecutor, _Casus
    try:
        kos({"adimlar": [{"fiil": "SORGU", "cube_query": CQ},
                         {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"}]},
            sorgu_kos=lambda cq: ROWS, paralel=True)
    finally:
        _cf.ThreadPoolExecutor = _eski
    assert not kuruldu, "tek sorgulu katmanda havuz kuruldu"
    assert pk.AZAMI_ESZAMANLI >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# FAZ 7 · KÖK-NEDEN İNİŞİ — döngü EKLEMEDEN derinleşme
# ═══════════════════════════════════════════════════════════════════════════════

def test_KOK_NEDEN_INISI_ZINCIR_OLARAK_KURULUYOR():
    """🔴🔴 `drill.py`'nin kendi belgesi bu anı öngörmüştü: *«İleride bir agent'ın AYNI
    mekanizmayı otomatik gezebilmesi hedeflenir.»*

    Bugüne kadar her `drill` adımı **kullanıcının tıklamasıyla** ve ayrı bir HTTP
    çağrısıyla tetikleniyordu. Şimdi aynı gezinti bir **zincir**:

        SORGU(taban) → BAGLA(en kötü) → SUZ(taban, makine=en kötü) → SORGU($3)

    ⊙ Derinlik **plan uzunluğuyla** sınırlı — yani döngü eklemeden derinleşme.
    *Bir döngü eklemeden derinleşmenin yolu, derinliği plana yazdırmaktır.*
    """
    TABAN = {"cube": "oee", "measures": ["v"], "dimensions": ["m"]}
    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": TABAN},
        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"},
        {"fiil": "SUZ", "cube_query": TABAN, "boyut": "m", "deger": "$2"},
        {"fiil": "SORGU", "cube_query": "$3"}]}
    kosulan: list[dict] = []

    def _kos_sorgu(cq):
        kosulan.append(cq)
        return ROWS

    from app.drill import select_cube_query
    r = kos(plan, sorgu_kos=_kos_sorgu,
            govdeler={"SUZ": lambda a: select_cube_query(
                a["cube_query"], a["boyut"],
                str(a["deger"][0] if isinstance(a["deger"], tuple) else a["deger"]))})
    assert len(kosulan) == 2, "ikinci sorgu koşmadı — iniş kurulmadı"
    _ikinci = kosulan[1]
    assert {"dimension": "m", "operator": "eq", "value": "RAM-3"} in _ikinci["filters"], (
        f"süzgeç `BAGLA`'nın seçtiği varlığa bağlanmadı: {_ikinci}")
    assert "m" not in (_ikinci.get("dimensions") or []), "süzülen boyut kırılımda kaldı"
    assert r["katmanlar"] == [[1], [2], [3], [4]]


def test_KIR_SATIR_DEGIL_SORGU_URETIR():
    """🔴 Tip sistemi olmasaydı `BAGLA($kir)` bir `cube_query` sözlüğünü **satır** sanardı.

    Kök-neden inişinin bütün mekanizması bu ayrımda: bir adım bir sorgu üretir, sonraki
    adım onu **koşar**.
    """
    from app.plan_semasi import CIKTI_TIPI
    assert CIKTI_TIPI["KIR"] == "sorgu" and CIKTI_TIPI["SUZ"] == "sorgu"
    plan = {"adimlar": [{"fiil": "KIR", "cube_query": {"cube": "oee"}, "boyut": "m"},
                        {"fiil": "BAGLA", "kaynak": "$1", "boyut": "m", "olcu": "v"}]}
    with pytest.raises(PlanHatasi, match="satirlar"):
        dogrula(plan)
