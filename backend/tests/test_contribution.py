"""FAZ 5.2 — katkı ayrıştırması: *"neden değişti?"* CubeQuery üzerinde.

Rakiplerin hepsinde bir karşılığı var (Snowflake `TOP_INSIGHTS`, Power BI Key Influencers,
Tableau Pulse) ve hepsi semantic layer'ın **dışında** duruyor: ürettikleri şey bir metin ya
da görsel — yeniden tarihlenemez, kırılamaz, sözleşme taşımaz. Buradaki fark şudur ve bu
dosyanın asıl kilitlediği şey odur: **her bulgu kendi başına bir CubeQuery'dir.**

Ve ondan da önemlisi: **ayrıştırma yalnız TOPLANABİLİR ölçülerde yapılır.** `AVG`/oran/
`COUNT(DISTINCT)` bir ölçüde segment katkısı matematiksel olarak TANIMSIZDIR — parçaların
toplamı bütünü vermez. "Bu segment değişimin %40'ını açıklıyor" cümlesi o durumda YANLIŞtır
ve bu, bu araç sınıfının klasik sessiz hatasıdır: sayı makul görünür, kimse toplamı kontrol
etmez. `test_toplanabilirlik_KANITLI` bunu veriye karşı ölçer, iddiaya karşı değil.
"""

from __future__ import annotations

import pytest

from app import contribution as contrib


@pytest.fixture(scope="module")
def cubes(schema):
    return {c["name"]: c for c in schema.get("cubes", [])}


# --- saf fonksiyonlar (veriye/servise ihtiyaç yok) --------------------------------

_SATIRLAR = [
    {"makine": "A", "toplam_ciro": 300.0, "toplam_ciro_gecen": 100.0},   # +200
    {"makine": "B", "toplam_ciro": 100.0, "toplam_ciro_gecen": 150.0},   # -50
    {"makine": "C", "toplam_ciro": 50.0, "toplam_ciro_gecen": 50.0},     # 0
]


def test_katki_delta_ve_siralama():
    k = contrib.contributions(_SATIRLAR, "makine", "toplam_ciro")
    assert [x["deger"] for x in k] == ["A", "B", "C"]  # |delta|'ya göre
    assert k[0]["delta"] == 200.0 and k[1]["delta"] == -50.0


def test_net_ve_BRUT_pay_ayri_hesaplanir():
    """Net değişim 150, brüt hareket 250. A net'in %133'ü (>%100! çünkü B ters yönde) ama
    brüt'ün %80'i. İki sayı da doğrudur ve FARKLI soruları cevaplar; tek bir "pay" gösteren
    araç bu ayrımı gizler."""
    k = contrib.contributions(_SATIRLAR, "makine", "toplam_ciro")
    assert k[0]["net_pay"] == pytest.approx(133.3, abs=0.2)
    assert k[0]["brut_pay"] == pytest.approx(80.0, abs=0.2)


def test_net_sifira_yakinsa_net_pay_UYDURULMAZ():
    """Segmentler birbirini götürebilir (+100 / −100): net 0 ama anlatılacak hikâye VAR.
    Net payı hesaplamak sıfıra bölmek ya da saçma yüzdeler üretmek olurdu; `None` döner ve
    brüt pay hikâyeyi yine anlatır."""
    satirlar = [
        {"makine": "A", "toplam_ciro": 200.0, "toplam_ciro_gecen": 100.0},
        {"makine": "B", "toplam_ciro": 0.0, "toplam_ciro_gecen": 100.0},
    ]
    k = contrib.contributions(satirlar, "makine", "toplam_ciro")
    assert all(x["net_pay"] is None for x in k)
    assert k[0]["brut_pay"] == pytest.approx(50.0)


def test_eksik_gecen_donem_SIFIR_sayilir():
    """Geçen dönemde HİÇ olmayan bir segment (yeni müşteri) tam katkı sayılmalı, satır
    düşürülmemeli — `yoy._merge` eşleşmeyen satırda `None` bırakıyor."""
    k = contrib.contributions([{"m": "yeni", "x": 50.0, "x_gecen": None}], "m", "x")
    assert k[0]["onceki"] == 0.0 and k[0]["delta"] == 50.0


def test_decompose_her_bulguya_CUBE_QUERY_koyar():
    """Modülün varlık sebebi: skor bir metin değil, TIKLANABİLİR bir sorgunun etiketi."""
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"]}
    r = contrib.decompose(_SATIRLAR, "makine", "toplam_ciro", cq, dim_label="makine")
    assert r["bulgular"], r
    for b in r["bulgular"]:
        f = b["cube_query"].get("filters") or []
        assert any(x["dimension"] == "makine" and x["value"] == b["deger"] for x in f), b
        assert "makine" not in (b["cube_query"].get("dimensions") or [])


def test_kirpma_SESSIZ_degil():
    """Gürültü eşiği altındaki segmentler listeden düşer ama KAÇ tanesinin düştüğü
    raporlanır — sessiz kesme "her şey kapsandı" gibi okunur (MIMARI.md)."""
    satirlar = _SATIRLAR + [{"makine": f"kucuk{i}", "toplam_ciro": 0.1,
                             "toplam_ciro_gecen": 0.0} for i in range(20)]
    r = contrib.decompose(satirlar, "makine", "toplam_ciro",
                          {"cube": "parti", "measures": ["toplam_ciro"]})
    # 21: 20 küçük segment + hiç kıpırdamayan "C" (delta 0 → payı da 0 → eşik altı).
    assert r["kirpilan_segment"] == 21
    assert r["kirpilan_esik_yuzde"] == contrib._GURULTU_PAYI


def test_boyut_siralamasi_ACIKLAYICILIGA_gore():
    """Değişimin %80'i tek bir makineden geliyorsa `makine`, değişimi eşit bölen bir
    boyuttan daha açıklayıcıdır."""
    yogun = contrib.decompose(_SATIRLAR, "makine", "toplam_ciro",
                              {"cube": "parti", "measures": ["toplam_ciro"]})
    dagitik = contrib.decompose(
        [{"gun": g, "toplam_ciro": 100.0, "toplam_ciro_gecen": 50.0} for g in "abcde"],
        "gun", "toplam_ciro", {"cube": "parti", "measures": ["toplam_ciro"]})
    assert contrib.rank_dimensions([dagitik, yogun])[0]["dimension"] == "makine"


# --- toplanabilirlik kapısı ------------------------------------------------------

def test_toplanabilir_olcu_GECER(cubes):
    ok, neden = contrib.ayristirilabilir_mi("toplam_ciro", cubes["parti"])
    assert ok and neden is None


@pytest.mark.parametrize("cube,measure", [
    ("parti", "fire_orani_yuzde"), ("oee", "ort_oee"), ("parti", "kar_marji_yuzde"),
])
def test_oran_ve_ortalama_REDDEDILIR(cubes, cube, measure):
    ok, neden = contrib.ayristirilabilir_mi(measure, cubes[cube])
    assert not ok and neden and measure in neden


def test_toplanabilirlik_KANITLI(cubes, schema):
    """Kapının İDDİASI veriyle sınanır: toplanabilir dediği ölçüde segment toplamı bütüne
    EŞİT, reddettiğinde DEĞİL. Bu test olmadan kapı bir inanç olurdu."""
    import duckdb

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)

    def _topla(cq):
        plan = svc.dry_plan(svc.cube_sql(cq))
        return [r for r in con.execute(plan.replace('boyahane."main".', "main.")).fetchall()]

    try:
        for measure, toplanabilir_beklenen in (("toplam_ciro", True),
                                               ("fire_orani_yuzde", False)):
            ok, _ = contrib.ayristirilabilir_mi(measure, cubes["parti"])
            assert ok is toplanabilir_beklenen, f"{measure} kapısı beklenenden farklı"
            butun = _topla({"cube": "parti", "measures": [measure]})[0][0]
            parcalar = sum(r[-1] for r in _topla(
                {"cube": "parti", "measures": [measure], "dimensions": ["makine"]})
                if r[-1] is not None)
            esit = abs(parcalar - butun) < max(1e-6, abs(butun) * 1e-6)
            assert esit is toplanabilir_beklenen, (
                f"{measure}: parçalar={parcalar} bütün={butun} — kapının kararı veriyle "
                "çelişiyor")
    finally:
        con.close()


# --- uç nokta --------------------------------------------------------------------

def _post(client, cq, **kw):
    return client.post("/ask/contribution", json={"cube_query": cq, **kw})


_CQ = {"cube": "parti", "measures": ["toplam_ciro"],
       "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}


def test_uc_nokta_rapor_uretir(client):
    r = _post(client, _CQ)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["measure"] == "toplam_ciro"
    assert d["raporlar"], d.get("note")
    ilk = d["raporlar"][0]
    assert ilk["bulgular"] and ilk["bulgular"][0]["cube_query"]["cube"] == "parti"


def test_uc_nokta_bulgu_cube_query_si_GERCEKTEN_kosar(client):
    """Bir bulgu tıklanabilir olmalı — `/cube` ile LLM'siz koşup sonuç döndürmeli.
    Aksi halde "her bulgu bir CubeQuery'dir" iddiası kâğıt üstünde kalır."""
    d = _post(client, _CQ).json()
    b = d["raporlar"][0]["bulgular"][0]
    r = client.post("/cube", json={"cube_query": b["cube_query"]})
    assert r.status_code == 200, r.text
    assert r.json().get("result", {}).get("rows")


def test_oran_olcusunde_uc_nokta_DURUSTCE_reddeder(client):
    d = _post(client, {**_CQ, "measures": ["fire_orani_yuzde"]}).json()
    assert not d["raporlar"]
    assert d["note"] and "fire_orani_yuzde" in d["note"]


def test_yapisal_olmayan_sorgu_REDDEDILIR(client):
    d = _post(client, {}).json()
    assert not d["raporlar"] and "Discovery" in (d["note"] or "")


def test_boyut_SINIRI_raporlanir(client):
    """Kombinatorik patlamayı önleyen sınır gerçek, ama sessiz değil: bakılmayan boyut
    sayısı yanıtta görünür."""
    d = _post(client, _CQ, max_dimensions=1).json()
    assert d["taranmayan_boyut"] >= 1
    assert len(d["raporlar"]) <= 1


def test_her_taranan_boyut_SOZLESME_uretir(client):
    """Her katkı sorgusu bir Query Contract kaydı bırakmalı — "yeniden çalıştırılıp hash
    eşlenebilen makbuz" değişmezi burada da geçerli."""
    d = _post(client, _CQ).json()
    assert len(d["contract_ids"]) >= len(d["raporlar"])


# --- FAZ 5.1: PVM (fiyat / miktar / birleşik) -------------------------------------

_PVM_SATIR = [
    # A: fiyat 10→12 (+2), miktar 100→100 → SAF FİYAT etkisi
    {"m": "A", "v": 1200.0, "v_gecen": 1000.0, "q": 100.0, "q_gecen": 100.0},
    # B: fiyat 5→5, miktar 100→140 → SAF MİKTAR etkisi
    {"m": "B", "v": 700.0, "v_gecen": 500.0, "q": 140.0, "q_gecen": 100.0},
    # C: ikisi de değişti → birleşik terim SIFIR DEĞİL
    {"m": "C", "v": 660.0, "v_gecen": 400.0, "q": 110.0, "q_gecen": 100.0},
]


def test_pvm_SAF_fiyat_ve_SAF_miktar_ayrisir():
    k = {x["deger"]: x for x in contrib.pvm(_PVM_SATIR, "m", "v", "q")}
    assert k["A"]["fiyat_etkisi"] == pytest.approx(200.0)
    assert k["A"]["miktar_etkisi"] == pytest.approx(0.0)
    assert k["B"]["miktar_etkisi"] == pytest.approx(200.0)
    assert k["B"]["fiyat_etkisi"] == pytest.approx(0.0)
    assert k["C"]["birlesik_etki"] != pytest.approx(0.0)


def test_pvm_ARTIKSIZ():
    """Yöntemin cebirsel olmasının ve bir TAHMİN taşımamasının kanıtı: üç etkinin toplamı
    her segmentte ve toplamda BİREBİR ΔV'dir. Artık çıkarsa ayrıştırma yanlıştır ve
    "fiyat %X etkiledi" cümlesi dayanaksız kalır."""
    kalemler = contrib.pvm(_PVM_SATIR, "m", "v", "q")
    for k in kalemler:
        toplam = k["fiyat_etkisi"] + k["miktar_etkisi"] + k["birlesik_etki"]
        assert toplam == pytest.approx(k["delta"], abs=1e-9), k
    assert (sum(k["fiyat_etkisi"] for k in kalemler)
            + sum(k["miktar_etkisi"] for k in kalemler)
            + sum(k["birlesik_etki"] for k in kalemler)) == pytest.approx(
        sum(k["delta"] for k in kalemler), abs=1e-9)


def test_pvm_SIFIR_MIKTAR_fiyat_uydurmaz():
    """Miktarı sıfır olan bir segmentte fiyat TANIMSIZDIR. Segment atlanmaz (gerçek bir
    hacim hareketi var — yeni giren / tamamen duran), ama değişim MİKTAR etkisi sayılır;
    "fiyat" diye adlandırmak 0'a bölmenin kılık değiştirmiş hali olurdu."""
    k = contrib.pvm([{"m": "yeni", "v": 500.0, "v_gecen": 0.0,
                      "q": 50.0, "q_gecen": 0.0}], "m", "v", "q")[0]
    assert k["fiyat_etkisi"] == 0.0 and k["birlesik_etki"] == 0.0
    assert k["miktar_etkisi"] == pytest.approx(500.0)
    assert k["fiyat_onceki"] is None and k["delta"] == pytest.approx(500.0)


def test_pvm_esleştirme_BEYAN_edilir_tahmin_EDILMEZ(cubes):
    """`toplam_ciro / toplam_agirlik_kg` gerçek bir TL/kg fiyatıdır; `toplam_tutar /
    fatura_sayisi` ise ortalama fatura büyüklüğüdür — fiyat DEĞİL. Ayrım bir İÇERİK
    bilgisidir ve ad kalıbından çıkarılamaz."""
    assert contrib.pvm_pairs(cubes["parti"]), "parti PVM beyanı kayboldu"
    assert contrib.pvm_pairs(cubes["parti"])[0]["value"] == "toplam_ciro"
    assert "TL/kg" in contrib.pvm_pairs(cubes["parti"])[0]["price_label"], (
        "price_label varsayılana düştü — build camelCase'e çeviriyor (priceLabel), "
        "pvm_pairs iki yazımı da okumalı")
    assert not contrib.pvm_pairs(cubes["ticaret"]), (
        "ticaret'e PVM beyanı eklenmiş — tutar/fatura_sayisi bir FİYAT değildir")


def test_pvm_uc_noktasi_calisir(client):
    r = _post(client, {**_CQ, "measures": ["toplam_ciro"]}, kind="pvm")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["kind"] == "pvm" and d["pvm_raporlar"], d.get("note")
    rp = d["pvm_raporlar"][0]
    assert rp["value_measure"] == "toplam_ciro" and rp["volume_measure"] == "toplam_agirlik_kg"
    assert rp["bulgular"][0]["baskin_etken"] in ("fiyat", "miktar")


def test_pvm_uc_noktasi_GERCEK_veride_artiksiz(client):
    """Gerçek veri üzerinde de artıksız olmalı — sentetik satırlarda tutması yetmez."""
    d = _post(client, {**_CQ, "measures": ["toplam_ciro"]}, kind="pvm").json()
    for rp in d["pvm_raporlar"]:
        toplam = rp["fiyat_etkisi"] + rp["miktar_etkisi"] + rp["birlesik_etki"]
        assert toplam == pytest.approx(rp["net_degisim"], rel=1e-9, abs=1e-6), rp["dimension"]


def test_pvm_beyansiz_olcude_DURUSTCE_reddeder(client):
    """`toplam_fire_kg` için bir fiyat×miktar çifti BEYAN EDİLMEMİŞ — tahmin edilmez."""
    d = _post(client, {**_CQ, "measures": ["toplam_fire_kg"]}, kind="pvm").json()
    assert not d["pvm_raporlar"]
    assert d["note"] and "pvm" in d["note"].lower()


def test_pvm_bulgusu_TIKLANABILIR(client):
    d = _post(client, {**_CQ, "measures": ["toplam_ciro"]}, kind="pvm").json()
    b = d["pvm_raporlar"][0]["bulgular"][0]
    r = client.post("/cube", json={"cube_query": b["cube_query"]})
    assert r.status_code == 200 and r.json().get("result", {}).get("rows")
