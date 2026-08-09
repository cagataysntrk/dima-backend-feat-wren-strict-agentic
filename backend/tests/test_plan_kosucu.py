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
