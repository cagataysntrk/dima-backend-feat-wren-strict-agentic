"""FAZ 1 (K1) — AD-HOC CUBE: uçurumu kaldır, ama YAPI ≠ GÜVEN.

## Kapatılan uçurum

`answer.py::seal()` üç kapısını da **tek bir alana** bakarak açar: `resp.cube_query`.
Discovery cevabı onu hiç set etmiyordu → chip · kırılım · zaman granülerliği · aksiyon
önerisi · köken · drill · katkı · doğru grafik · rapor · pano · zamanlama · frontend
butonları **hepsi birden** kapanıyordu (plan §1: *"tasarlanmış bir uçurum"*).

## Bu dosyanın kilitlediği DÖRT RİSK (planın ⟳ eklemesi)

1. **DONDURULMUŞLUK** — ad-hoc cube kurulduktan sonra kaynak DB'ye **sıfır** sorgu.
   Tasarımın tamamı buna dayanıyordu ama hiçbir yerde **yazılı değildi**; artık ölçülüyor.
2. **KIRPILMIŞ GÖRÜNÜM** — `row_count == limit` iken toplama/kırılım chip'i **sunulmaz**.
   Kırpılmış 1000 satırı gruplamak kısmi toplam verir: *kendinden emin ama yanlış*.
3. **MASKELEME SIRASI** — cube **maskeli** satırlardan kurulur (yoksa oturum `.duckdb`
   diskte maskesiz PII taşır); maskelenen kolonda filtre/kırılım chip'i üretilmez.
4. **KILL-SWITCH** — `adhoc_cube` bayrağı kapalıyken davranış **bugünküyle birebir**.

## Ve rozet dürüstlüğü

`source` **`llm:*` kalır**, `explain.confidence` **`None` kalır** (MIMARI §5). Yapı
açılır, güven açılmaz.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app import adhoc_cube


def _sonuc(n=3, kolon_tip=(("bolge", "string"), ("ciro", "double"))):
    kolonlar = [k for k, _ in kolon_tip]
    tipler = [t for _, t in kolon_tip]
    rows = [{k: (f"v{i}" if t == "string" else float(i * 10))
             for k, t in kolon_tip} for i in range(n)]
    return {"columns": kolonlar, "rows": rows, "row_count": n, "column_types": tipler}


# --- MODÜL: türetme -------------------------------------------------------------

def test_ROL_atamasi_TIPTEN_gelir(tmp_path):
    """Tipsiz bir sonuçtan ölçü/boyut ayrımı yapılamaz — K1'in TEK eksiği buydu
    (`query()` Arrow şemasını atıyordu)."""
    k = adhoc_cube.turet(_sonuc(), tmp_path)
    assert k is not None
    roller = {c["name"]: c["role"] for c in k["info"]["columns"]}
    assert roller == {"bolge": "dimension", "ciro": "measure"}


def test_TIP_YOKSA_yapi_VAAT_EDILMEZ(tmp_path):
    """Tip gelmezse her kolon VARCHAR olur → ölçüsüz cube → yapı rozeti takılmış ama
    içi boş bir cevap. Tahmin etmektense yapı vaat etmemek doğrudur."""
    s = _sonuc()
    s.pop("column_types")
    assert adhoc_cube.turet(s, tmp_path) is None


def test_BOS_sonuctan_cube_KURULMAZ(tmp_path):
    assert adhoc_cube.turet({"columns": ["a"], "rows": [], "row_count": 0,
                             "column_types": ["string"]}, tmp_path) is None


def test_COK_BUYUK_sonuc_REDDEDILIR(tmp_path):
    """Materyalizasyon senkron ve diske yazıyor — bir Discovery cevabı için sınırsız
    disk/zaman harcanmaz."""
    s = _sonuc(n=adhoc_cube.MAKS_SATIR + 1)
    assert adhoc_cube.turet(s, tmp_path) is None


def test_ROZET_alanlari_cube_query_uzerinde(tmp_path):
    """YAPI ≠ GÜVEN: makbuz yapının nereden geldiğini SÖYLEMEK zorunda."""
    k = adhoc_cube.turet(_sonuc(), tmp_path, kirpilmis=True)
    cq = k["cube_query"]
    assert cq["adhoc"] is True
    assert cq["provenance"] == "llm_sql'den türetildi"
    assert cq["kirpilmis"] is True


def test_MASKELI_kolon_SLUGA_cevrilir(tmp_path):
    """Chip üreten taraf orijinal adı değil cube'daki boyut adını görür."""
    k = adhoc_cube.turet(_sonuc(kolon_tip=(("Müşteri Adı", "string"), ("ciro", "double"))),
                         tmp_path, maskeli_kolonlar=frozenset({"Müşteri Adı"}))
    assert k["maskeli_kolonlar"] == frozenset({"musteri_adi"})


# --- DONDURULMUŞLUK: planın 1. risk maddesi -------------------------------------

def test_DONDURULMUS_kaynak_DBye_SIFIR_sorgu(tmp_path):
    """Tasarımın TAMAMI buna dayanıyor ve hiçbir yerde yazılı değildi. Ad-hoc servis
    yalnız oturum `.duckdb`'sine bağlıdır; `always_filter` endişesi bu yüzden yok."""
    k = adhoc_cube.turet(_sonuc(), tmp_path)
    svc = k["service"]
    # bağlantı hedefi oturum dizini
    assert str(tmp_path) in str(getattr(svc, "connection_info", {}))
    # ve veri gerçekten materyalize: kaynak olmadan sorgulanabiliyor
    sql = svc.cube_sql({"cube": "adhoc", "measures": ["toplam_ciro"]})
    rows = svc.query(sql)["rows"]
    assert rows and rows[0]["toplam_ciro"] == pytest.approx(30.0)  # 0+10+20


def test_MATERYALIZE_edilen_dosya_OTURUM_dizininde(tmp_path):
    adhoc_cube.turet(_sonuc(), tmp_path)
    assert (tmp_path / "data.duckdb").exists()
    assert (tmp_path / "target" / "mdl.json").exists()


# --- UÇTAN UCA: /ask zinciri ----------------------------------------------------

def _discovery_cevabi(client, soru="zxqw plmk asdf listele"):
    return client.post("/ask", json={"question": soru, "session_id": "adhoc-t",
                                     "execute": True}).json()


def test_BAYRAK_KAPALIYKEN_davranis_BIREBIR_AYNI(client, monkeypatch):
    """KURAL B. Kapatma bayrağı yoksa geri dönüş yoktur; `ask_intent_first` aynı kalıpta
    yönetiliyor. Kapalıyken Discovery cevabı `cube_query` TAŞIMAMALI."""
    from app import features

    gercek = features.resolve_for
    monkeypatch.setattr(
        features, "resolve_for",
        lambda *a, **k: {x: v for x, v in gercek(*a, **k).items() if x != "adhoc_cube"})
    d = _discovery_cevabi(client)
    assert not (d.get("cube_query") or {}).get("adhoc"), \
        "bayrak KAPALIYKEN ad-hoc cube kuruldu — geri dönüş yolu yok demektir"


def test_ROZET_DURUST_kalir(client):
    """En sert kural (MIMARI §5): yapı açılsa bile `source` `llm:*` ve
    `explain.confidence` **None** kalmalı. `_build_explain` güveni `source`'tan okur —
    `cube_query`'nin varlığından DEĞİL; bu test o bağın kopmadığını kilitler."""
    d = _discovery_cevabi(client)
    if not d.get("cube_query") or not (d["cube_query"] or {}).get("adhoc"):
        pytest.skip("bu ortamda Discovery ad-hoc cube üretmedi (LLM yok / rule yolu)")
    assert (d.get("source") or "").startswith(("llm", "rule"))
    assert (d.get("explain") or {}).get("confidence") is None


# --- KIRPILMIŞ GÖRÜNÜM: planın 2. risk maddesi ----------------------------------

def test_KIRPILMISTA_chip_SUNULMAZ_ve_SEBEBI_yazilir(client, monkeypatch):
    """Kırpılmış 1000 satırı gruplamak KISMİ toplam verir — kendinden emin ama yanlış.
    Chip'in sessizce eksilmesi de yetmez: kullanıcı SEBEBİNİ görmeli."""
    from app.answer import _attach_next_steps
    from app.schemas import AskResponse, QueryResult

    resp = AskResponse(question="x", sql="SELECT 1", planned_sql=None,
                       result=QueryResult(columns=["a"], rows=[{"a": 1}], row_count=1),
                       source="llm:test")
    resp.cube_query = {"cube": "adhoc", "measures": ["toplam_ciro"],
                       "adhoc": True, "kirpilmis": True}

    class _R:
        class state:  # noqa: N801
            principal = None

        class app:  # noqa: N801
            class state:  # noqa: N801
                adhoc_cubes: dict = {}

    _attach_next_steps(_R, resp)
    assert not resp.next_steps, "kırpılmış görünümde toplama chip'i sunuldu"
    assert resp.note and "kırpılmış" in resp.note.lower()


def test_KIRPILMAMIS_gorunumde_chip_ACILIYOR(tmp_path):
    """UÇURUMUN KAPANDIĞININ ASIL KANITI. Bugüne kadar Discovery cevabında `next_steps`
    sayısı **0**'dı (plan §6 kabul ölçütü: *"0 → ≥3"*). Ad-hoc cube kurulunca kırılım
    chip'leri GERÇEK cube meta'sından üretilmeli.

    Kırpılmamış bir Discovery sonucu kural-üretecinden elde edilemiyor (`SELECT *` her
    zaman tavana değiyor), o yüzden zincir burada GERÇEK ad-hoc kaydıyla kurulur —
    sahte cube meta'sı değil, `dataset.build_mdl`'in ürettiği şema."""
    from app.answer import _attach_next_steps
    from app.schemas import AskResponse, QueryResult

    kurulan = adhoc_cube.turet(
        _sonuc(n=3, kolon_tip=(("bolge", "string"), ("urun", "string"),
                               ("ciro", "double"))), tmp_path)
    assert kurulan is not None
    kurulan["cube_query"]["adhoc_id"] = "t-1"

    resp = AskResponse(question="x", sql="SELECT 1", planned_sql=None,
                       result=QueryResult(columns=["bolge"], rows=[{"bolge": "a"}], row_count=1),
                       source="llm:test")
    resp.cube_query = kurulan["cube_query"]

    class _R:
        class state:  # noqa: N801
            principal = None

        class app:  # noqa: N801
            class state:  # noqa: N801
                adhoc_cubes = {"t-1": kurulan}

    _attach_next_steps(_R, resp)
    assert resp.next_steps, "ad-hoc cube kurulduğu hâlde chip üretilmedi — uçurum açık"
    kirilimlar = {d for s in resp.next_steps
                  for d in ((s.cube_query or {}).get("dimensions") or [])}
    assert kirilimlar & {"bolge", "urun"}, f"SQL'in seçtiği kolonlar kırılım olmadı: {kirilimlar}"


def test_MASKELI_kolonda_chip_URETILMEZ(tmp_path):
    """Planın 3. risk maddesi: cube MASKELİ satırlardan kuruldu, `Ahm** Y***` değerine
    kırılım kuran chip anlamsız/boş döner. Boş dönen chip, chipsizlikten KÖTÜDÜR."""
    from app.answer import _attach_next_steps
    from app.schemas import AskResponse, QueryResult

    kurulan = adhoc_cube.turet(
        _sonuc(n=3, kolon_tip=(("musteri", "string"), ("urun", "string"),
                               ("ciro", "double"))), tmp_path,
        maskeli_kolonlar=frozenset({"musteri"}))
    kurulan["cube_query"]["adhoc_id"] = "t-2"
    assert kurulan["maskeli_kolonlar"] == frozenset({"musteri"})

    resp = AskResponse(question="x", sql="SELECT 1", planned_sql=None,
                       result=QueryResult(columns=["a"], rows=[{"a": 1}], row_count=1),
                       source="llm:test")
    resp.cube_query = kurulan["cube_query"]

    class _R:
        class state:  # noqa: N801
            principal = None

        class app:  # noqa: N801
            class state:  # noqa: N801
                adhoc_cubes = {"t-2": kurulan}

    _attach_next_steps(_R, resp)
    kirilimlar = {d for s in (resp.next_steps or [])
                  for d in ((s.cube_query or {}).get("dimensions") or [])}
    assert "musteri" not in kirilimlar, "maskelenmiş kolonda kırılım chip'i sunuldu"
    assert "urun" in kirilimlar, "maskeleme kapısı fazla geniş — temiz kolonu da kesti"


# --- SÖZLEŞME: parse_cube_query işaretleri KORUR --------------------------------

def test_PARSE_adhoc_isaretlerini_KORUR():
    """İşaretler düşerse: `adhoc_id` kaybolur → İKİNCİ chip tıklaması servisi bulamaz,
    zincir TEK ADIMDA kopar; `kirpilmis` kaybolur → 2. risk maddesi sessizce açılır."""
    import json

    from app import cube_router as cr

    index = {"adhoc": {"measures": ["toplam_ciro"], "dimensions": ["bolge"],
                       "time_dimensions": []}}
    cq = cr.parse_cube_query(json.dumps({
        "cube": "adhoc", "measures": ["toplam_ciro"], "adhoc": True,
        "adhoc_id": "s-42", "kirpilmis": True, "provenance": "llm_sql'den türetildi"}), index)
    assert cq["adhoc"] is True and cq["adhoc_id"] == "s-42"
    assert cq["kirpilmis"] is True and cq["provenance"]


def test_PARSE_adhoc_ISARETI_YOKSA_uydurmaz():
    """Normal cube sorgusuna ad-hoc işareti EKLENMEZ — uydurma yüzeyi yok."""
    import json

    from app import cube_router as cr

    index = {"adhoc": {"measures": ["toplam_ciro"], "dimensions": [], "time_dimensions": []}}
    cq = cr.parse_cube_query(json.dumps({"cube": "adhoc", "measures": ["toplam_ciro"],
                                         "adhoc_id": "s-42"}), index)
    assert "adhoc" not in cq and "adhoc_id" not in cq


# --- column_types: K1'in tek eksiği ---------------------------------------------

def test_QUERY_arrow_TIPLERINI_tasiyor(wren):
    """`query()` eskiden yalnız kolon ADLARINI dönüyordu; Arrow şeması ATILIYORDU."""
    r = wren.query("SELECT 1 AS a, 'x' AS b")
    assert r["column_types"] and len(r["column_types"]) == len(r["columns"])
    assert any("int" in t for t in r["column_types"])
