"""FAZ 4.4 kapısı — **ROUND-TRIP: ihraç → geri ithal → BİREBİR AYNI SQL.**

🔴 Bu kapı `ossie_ihrac` bayrağından **BAĞIMSIZDIR**. Yol haritasının şartı: *"ihraç
edilen model geri ithal edildiğinde birebir aynı SQL'i vermelidir — vermiyorsa bayrak
AÇILMAZ."* Yani bayrağı açma kararı bir ürün kararı, bu kapı ise bir **doğruluk
kararıdır** ve ikincisi birincisini **kilitler**.

## Neden SQL, neden alan değil

Alanları tek tek kıyaslamak, *"hangi alan SQL'i belirliyor"* sorusunu **testin kendi
yorumuna** bağlardı — ve bu depo o hatayı daha önce ödedi (`mdl_diff` `additive`'i
"sözlük" kovasına atıp **beş gerçek davranış değişikliğini** maskelemişti). Burada
karşılaştırılan şey motorun **gerçekten ürettiği SQL**'dir.
"""

from __future__ import annotations

import re

import pytest
import yaml

from app.ossie import UZANTI, belge, cevir, disa_aktar


def _bosluksuz(s: str) -> str:
    """SQL'i normalize eder — **yalnız boşluk**, başka hiçbir şey değil.

    ⚠ Daha agresif bir normalize (tırnak/parantez/alias silme) kapıyı **yalancı-yeşil**
    yapardı: farkı normalize eden bir karşılaştırma, farkı ölçmez.
    """
    return re.sub(r"\s+", " ", (s or "").strip())


@pytest.fixture(scope="module")
def _cari_cube() -> dict:
    """Gerçek bir pack cube'u — uydurma bir fixture DEĞİL.

    `cari`, bu deponun en zor cube'u: `additive: semi` bir ölçüsü (`bakiye`) var ve o
    ölçü düz `SUM` edilirse **güvenle yanlış** sayı üretir. Round-trip'in taşıması
    gereken en pahalı alan tam olarak orada.
    """
    from pathlib import Path

    yol = (Path(__file__).resolve().parents[1]
           / "demo/wren-projects/demo-boyahane/cubes/cari/metadata.yml")
    if not yol.exists():
        pytest.skip("derlenmiş demo-boyahane ağacı yok")
    return yaml.safe_load(yol.read_text(encoding="utf-8"))


def test_ROUND_TRIP_cube_alanlari_KAYBOLMAZ(_cari_cube):
    """İhraç → ithal: SQL'i belirleyen her alan **geri gelmeli**."""
    geri = cevir({"version": "0.2", "datasets": [disa_aktar(_cari_cube)]})["cubes"][0]

    assert geri["name"] == _cari_cube["name"]
    assert geri["base_object"] == _cari_cube["base_object"]

    ilk_olcu = {m["name"]: m for m in _cari_cube["measures"]}
    son_olcu = {m["name"]: m for m in geri["measures"]}
    assert set(son_olcu) == set(ilk_olcu), "ölçü kümesi değişti"
    for ad, m in ilk_olcu.items():
        assert son_olcu[ad].get("expression") == m.get("expression"), (
            f"`{ad}`: ölçü İFADESİ round-trip'te değişti — SQL de değişir")
        assert son_olcu[ad].get("additive") == m.get("additive"), (
            f"🔴 `{ad}`: `additive` DÜŞTÜ. `semi` bir bakiyeyi düz SUM etmek GÜVENLE "
            f"YANLIŞ sayı üretir; standarda uyarken bu alanı kaybetmek ihracın bedeli "
            f"olamaz (bu yüzden `{UZANTI}` var).")
        assert son_olcu[ad].get("unit") == m.get("unit")

    ilk_boyut = {d["name"]: d for d in _cari_cube["dimensions"]}
    son_boyut = {d["name"]: d for d in geri["dimensions"]}
    assert set(son_boyut) == set(ilk_boyut), "boyut kümesi değişti"
    for ad, d in ilk_boyut.items():
        assert son_boyut[ad].get("expression") == d.get("expression"), (
            f"`{ad}`: boyut ifadesi round-trip'te değişti")
        assert son_boyut[ad].get("type") == d.get("type"), (
            f"`{ad}`: veri tipi kayboldu — Ossie'nin `type`ı 'dimension|metric' ayrımını "
            f"tutuyor, veri tipi `{UZANTI}.veri_tipi`'nde taşınmalı")


def test_ROUND_TRIP_gercek_SQL_BIREBIR_ayni(tmp_path):
    """🔴 **ASIL KAPI:** derlenmiş projede cube round-trip edilir, **motor SQL'i** kıyaslanır.

    Alan kıyası bir **vekildir**; bu test vekili değil, **şeyin kendisini** ölçer.
    """
    import shutil
    from pathlib import Path

    from app.compose import build, compose
    from app.config import get_settings
    from app.wren_service import WrenService

    # ⚠ `connection_info={}` DEĞİL: motor sözlük değil bir nesne bekliyor ve `{}`
    # geçmek `AttributeError: 'dict' object has no attribute 'format'` veriyor —
    # yani test "SQL üretilemedi" diye ATLANIRDI. *Atlanan bir kapı, olmayan bir kapıdır.*
    st = get_settings()
    kok = Path(__file__).resolve().parents[1]
    a_dir = tmp_path / "a"
    compose("demo-boyahane", kok / "demo", a_dir)
    build(a_dir)
    a = WrenService(a_dir, datasource=st.datasource,
                    connection_info=st.connection_dict())
    sema = a.schema()
    cube = next((c for c in sema.get("cubes") or [] if c.get("name") == "cari"), None)
    if cube is None:
        pytest.skip("`cari` cube derlenmiş ağaçta yok")

    # ⚠ Sorgu **şemadan türetilir**, elle yazılmaz: elle yazılan bir zaman boyutu
    # (`tarih`) motorda yoksa test `⊘ ATLANIR` ve kapı sessizce kaybolur — bu deponun
    # *"çalıştığı sanılan bir kapı, olmayan bir kapıdan tehlikelidir"* kuralı.
    olculer = [m for m in (cube.get("measures") or [])][:2]
    boyutlar = [d for d in (cube.get("dimensions") or [])][:1]
    zaman = (cube.get("time_dimensions") or cube.get("timeDimensions")
             or [d for d in (cube.get("dimensions") or [])
                 if "tarih" in str(d) or "date" in str(d).lower()])
    assert olculer and boyutlar, "`cari` cube'unda ölçü/boyut yok — fixture bozuk"
    cq = {"cube": "cari", "measures": olculer, "dimensions": boyutlar}
    if zaman:
        cq["timeDimensions"] = [{"dimension": str(zaman[0]), "granularity": "month"}]
    try:
        sql_a = a.cube_sql(cq)
    except Exception as exc:                              # noqa: BLE001
        pytest.skip(f"⊘ ÖLÇÜLEMEDİ — taban SQL üretilemedi: {exc}")

    # İhraç → geri ithal → **derlenmiş ağaçtaki cube'u DEĞİŞTİR** → yeniden kur.
    b_dir = tmp_path / "b"
    shutil.copytree(a_dir, b_dir)
    ham = yaml.safe_load((b_dir / "cubes/cari/metadata.yml").read_text(encoding="utf-8"))
    geri = cevir(belge([ham]))["cubes"][0]
    # `ithal_kaynak` bir DAMGADIR, SQL'i belirlemez — ama düşürülmez, yazılır.
    assert geri.pop("ithal_kaynak") == "ossie"
    (b_dir / "cubes/cari/metadata.yml").write_text(
        yaml.safe_dump(geri, allow_unicode=True, sort_keys=False), encoding="utf-8")
    build(b_dir)
    sql_b = WrenService(b_dir, datasource=st.datasource,
                        connection_info=st.connection_dict()).cube_sql(cq)

    assert _bosluksuz(sql_a) == _bosluksuz(sql_b), (
        "🔴 ROUND-TRIP KIRIK — `ossie_ihrac` AÇILAMAZ.\n"
        f"--- ihraç öncesi ---\n{sql_a}\n--- geri ithal sonrası ---\n{sql_b}")


def test_iliski_sertifikasi_IHRACTA_da_tasinir():
    """*Bir beyanı dışarı verirken düşürmek, karşı tarafa "ölçüldü" demektir.*"""
    b = belge([{"name": "c", "measures": [{"name": "m"}], "dimensions": []}],
              iliskiler=[{"name": "r", "models": ["a", "b"]}])
    assert b["relationships"][0][UZANTI]["certified"] == "olculmedi"
    # Ve geri okunur:
    geri = cevir(b)["relationships"][0]
    assert geri["certified"] == "olculmedi"


def test_beyan_edilmis_sertifika_KORUNUR():
    """Ölçülmüş bir sertifika round-trip'te `olculmedi`ye **düşürülmez** de."""
    b = belge([{"name": "c", "measures": [], "dimensions": []}],
              iliskiler=[{"name": "r", "models": ["a", "b"], "certified": "olculdu"}])
    assert cevir(b)["relationships"][0]["certified"] == "olculdu"


def test_always_filter_IHRACTA_kaybolmaz():
    """🔴 `always_filter` düşerse iptal kayıtları sızar ve **sayı sessizce şişer**."""
    c = {"name": "x", "base_object": "t", "always_filter": "CANCELLED = 0",
         "measures": [{"name": "m", "expression": "SUM(a)"}], "dimensions": []}
    assert disa_aktar(c)[UZANTI]["always_filter"] == "CANCELLED = 0"
    assert cevir(belge([c]))["cubes"][0]["always_filter"] == "CANCELLED = 0"


def test_adsiz_cube_IHRAC_EDILEMEZ():
    """Fail-closed **ihraçta da** geçerli: adsız bir dataset geri ithalde reddedilirdi."""
    from app.ossie import OssieIthalHatasi

    with pytest.raises(OssieIthalHatasi):
        disa_aktar({"name": "", "measures": []})


def test_baska_saticinin_belgesi_UZANTISIZ_da_ithal_edilir():
    """⚠ `x-dima` yokluğu bir hata **değildir**.

    *Standardın tamamını isteyen bir ithal kapısı, standardı olan hiç kimseyi içeri
    almaz.* Uzantısız belge girer; taşımadığı alanlar yalnız **yok** olur, ithal
    reddedilmez.
    """
    r = cevir({"version": "0.2",
               "datasets": [{"name": "d", "table": "t",
                             "metrics": [{"name": "m", "expression": "SUM(x)"}],
                             "fields": [{"name": "f", "type": "dimension"}]}]})
    c = r["cubes"][0]
    assert c["measures"][0]["expression"] == "SUM(x)"
    assert "additive" not in c["measures"][0]
    assert c["dimensions"][0]["name"] == "f"
