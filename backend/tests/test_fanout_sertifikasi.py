"""FAZ D2 — fan-out sertifikası: ölçümden ARTEFAKTA ve MAKBUZA.

## Neden

`tests/test_relationship_health.py` beyan edilen her join'in fan-out / NULL / öksüz
sağlığını gerçek veriye karşı ölçüyordu — ama ölçüm **koşum anında doğup koşum bitince
ölüyordu**. MIMARI §9.1 bunu *"dünyada ilk"* sayan bir iddia taşıyor; **artefakt olmadan
iddia karşılıksızdır**: kullanıcı bir kırılıma bakıp *"bu join ölçüldü mü"* diye soramaz,
cevabın makbuzu da bunu taşıyamaz.

## Kurulan zincir

    relationships.yml → app/fanout.certify() → target/fanout_certificate.json (BUILD)
                                             ↘ WrenService.schema() → dimension_origin.certified
                                             ↘ contract_log.provenance_json (MAKBUZ)

## Korunan ayrım

`"olculmedi"` ≠ `"olculdu:saglikli"`. Sertifikanın **tüm değeri** bu ayrımdadır: ölçülmemiş
bir join'i temiz göstermek, olmayan bir garantiyi rozetlemektir. Bu yüzden `oku()` artefakt
yokken boş döner ve damga `"olculmedi"` olur — sessiz "sağlıklı" değil.
"""

from __future__ import annotations

import json

import pytest

from app import fanout

_RELS = [
    {"name": "temiz", "models": ["fact", "dim"], "condition": "fact.k = dim.k"},
    {"name": "ters_yazim", "models": ["fact", "dim"], "condition": "dim.k = fact.k"},
    {"name": "bilesik", "models": ["a", "b"], "condition": "a.x = b.x AND a.y = b.y"},
    {"name": "yok_tablo", "models": ["fact", "olmayan"], "condition": "fact.k = olmayan.k"},
]


def _sahte_sorgu(bir=(10, 10, 0), cok=(100, 100)):
    def _q(sql):
        return [bir] if "count(distinct" in sql else [cok]
    return _q


# --- ayrıştırma -------------------------------------------------------------------

def test_yon_MODELS_sirasindan_okunur():
    """`condition`'ın yazım sırası TERS olabilir; "çok"/"bir" yönü `models`'ten gelir.
    Ters okunursa fan-out YANLIŞ TARAFTA ölçülür ve test hiçbir şey korumaz."""
    assert fanout.ayristir(_RELS[0]) == ("fact", "k", "dim", "k")
    assert fanout.ayristir(_RELS[1]) == ("fact", "k", "dim", "k")


def test_bilesik_kosul_ayristirilamaz():
    assert fanout.ayristir(_RELS[2]) is None


# --- ölçüm ------------------------------------------------------------------------

def test_saglikli_iliski():
    s = fanout.certify([_RELS[0]], _sahte_sorgu())["relationships"]["temiz"]
    assert s["durum"] == "olculdu" and s["saglikli"] and s["oksuz_oran"] == 0.0


def test_FANOUT_yakalanir():
    """Hedef anahtar benzersiz değil → join satırları çoğaltır, SUM'lar şişer."""
    s = fanout.certify([_RELS[0]], _sahte_sorgu(bir=(10, 7, 0)))["relationships"]["temiz"]
    assert s["benzersiz"] is False and s["saglikli"] is False


def test_NULL_anahtar_yakalanir():
    """NULL, benzersizlik testini sessizce deler → ayrı ölçülür."""
    s = fanout.certify([_RELS[0]], _sahte_sorgu(bir=(10, 10, 3)))["relationships"]["temiz"]
    assert s["bir_null"] == 3 and s["saglikli"] is False


def test_OKSUZ_oran_yakalanir():
    """Polimorfik anahtar imzası: satırların bir kısmı hedefte karşılık bulamaz."""
    s = fanout.certify([_RELS[0]], _sahte_sorgu(cok=(100, 47)))["relationships"]["temiz"]
    assert s["oksuz_oran"] == pytest.approx(0.53) and s["saglikli"] is False


def test_OLCULMEDI_ile_TEMIZ_karistirilmaz():
    """Ölçülemeyen ilişki kayda `atlandi`/`ayristirilamadi` diye girer — SESSİZCE
    DÜŞÜRÜLMEZ ve asla `saglikli` sayılmaz."""
    kayit = fanout.certify(_RELS, _sahte_sorgu(), tablolar={"fact", "dim", "a", "b"})
    r = kayit["relationships"]
    assert r["bilesik"]["durum"] == "ayristirilamadi"
    assert r["yok_tablo"]["durum"] == "atlandi" and "olmayan" in r["yok_tablo"]["not"]
    assert "saglikli" not in r["yok_tablo"]


def test_sorgu_HATASI_yutulmaz():
    def _patlar(_sql):
        raise RuntimeError("bağlantı koptu")

    s = fanout.certify([_RELS[0]], _patlar)["relationships"]["temiz"]
    assert s["durum"] == "hata" and "koptu" in s["not"]


def test_NITELIKLI_ad_cozucu():
    """Şema adı SABİT KODLANMAZ: konnektör üzerinden `boyahane.musteriler` gelir
    (ölçüldü), doğrudan DuckDB'de `main.musteriler`."""
    gorulen = []

    def _q(sql):
        gorulen.append(sql)
        return [(1, 1, 0)] if "count(distinct" in sql else [(1, 1)]

    fanout.certify([_RELS[0]], _q, nitelikli=lambda t: f'"kat"."{t}"')
    assert any('"kat"."dim"' in s for s in gorulen)
    assert not any("main." in s for s in gorulen)


# --- artefakt ---------------------------------------------------------------------

def test_sertifika_OLCUM_ZAMANINI_ve_SEMA_SURUMUNU_tasir():
    """Sertifika bir GEÇMİŞ ölçümdür: *"bu join güvenli"* ancak *"ne zaman ve hangi şemaya
    karşı ölçüldü"* ile birlikte anlamlıdır. `partiler.operator = personel.ad_soyad` bugün
    benzersiz — aynı adı taşıyan ikinci personel eklendiği gün değil."""
    sert = fanout.certify([_RELS[0]], _sahte_sorgu(), mdl_version="sha256:abc")
    assert sert["mdl_version"] == "sha256:abc"
    assert sert["olculme_zamani"].startswith("20") and "T" in sert["olculme_zamani"]


def test_yaz_oku_gidis_donus(tmp_path):
    sert = fanout.certify([_RELS[0]], _sahte_sorgu())
    yol = fanout.yaz(tmp_path, sert)
    assert yol.name == "fanout_certificate.json" and yol.parent.name == "target"
    assert fanout.oku(tmp_path) == sert


def test_artefakt_YOKSA_bos_doner(tmp_path):
    """Sertifika bir KOLAYLIKTIR, kapı değil: üretilmemiş kurulumda sistem cevap vermeyi
    bırakmamalı, yalnız "bu join ölçüldü" diyememeli."""
    assert fanout.oku(tmp_path) == {}


def test_BOZUK_artefakt_patlatmaz(tmp_path):
    (tmp_path / "target").mkdir()
    (tmp_path / "target" / "fanout_certificate.json").write_text("{bozuk", encoding="utf-8")
    assert fanout.oku(tmp_path) == {}


@pytest.mark.parametrize("kayit,beklenen", [
    ({"durum": "olculdu", "saglikli": True}, "olculdu:saglikli"),
    ({"durum": "olculdu", "saglikli": False}, "olculdu:riskli"),
    ({"durum": "atlandi"}, "olculmedi"),
])
def test_rozet(kayit, beklenen):
    assert fanout.rozet({"relationships": {"r": kayit}}, "r") == beklenen


def test_rozet_BILINMEYEN_iliski_olculmedi():
    assert fanout.rozet({"relationships": {}}, "r") == "olculmedi"
    assert fanout.rozet({}, None) is None, "yerel boyutta köken sorusu anlamsız"


# --- zincirin uçları --------------------------------------------------------------

def test_schema_boyut_kokenine_DAMGA_basar(schema):
    """`dimension_origin` artık `certified` taşır — UI rozeti (Faz H5) ve makbuz bundan
    beslenir. Demo'da sertifika build edilmiş olmayabilir; o zaman `olculmedi` olmalı,
    ama alan HER ZAMAN bulunmalı."""
    damgali = 0
    for c in schema.get("cubes") or []:
        for origin in (c.get("dimension_origin") or {}).values():
            assert "certified" in origin, "köken damgasız kaldı"
            assert origin["certified"] in ("olculdu:saglikli", "olculdu:riskli", "olculmedi")
            damgali += 1
    assert damgali > 0, "hiç ilişki-türevi boyut yok — test bir şey korumuyor"


def test_makbuz_KOKENI_tasir(schema):
    """`answer.koken` cevabın kullandığı ilişki-türevi boyutları makbuza yazar."""
    from app.answer import koken

    class _Svc:
        def schema(self):
            return schema

    kaynakli = None
    for c in schema.get("cubes") or []:
        for d in (c.get("dimension_origin") or {}):
            kaynakli = (c["name"], d)
            break
        if kaynakli:
            break
    cube, dim = kaynakli
    out = koken(_Svc(), {"cube": cube, "dimensions": [dim], "measures": []})
    assert out and dim in out["dimensions"]
    assert "certified" in out["dimensions"][dim]
    assert json.dumps(out)  # makbuza JSON olarak yazılabilir olmalı


def test_makbuz_kokeni_ILISKISIZ_cevapta_None(schema):
    """Yerel boyutlu (ya da kırılımsız) cevapta köken sorusu ANLAMSIZDIR → `None`.
    Boş sözlük yazmak "bakıldı, yoktu" ile "hiç sorulmadı"yı karıştırırdı."""
    from app.answer import koken

    class _Svc:
        def schema(self):
            return schema

    assert koken(_Svc(), {"cube": "parti", "dimensions": [], "measures": ["toplam_ciro"]}) is None
    assert koken(_Svc(), None) is None
    assert koken(_Svc(), {"cube": "parti", "dimensions": ["makine"]}) is None, \
        "yerel boyut köken taşımaz"


def test_contract_log_KOLONU_var():
    """Makbuz şeması köken kolonunu taşımalı (migration b9e4c1d70a25)."""
    from control_plane.models import ContractLog

    assert "provenance_json" in ContractLog.model_fields
