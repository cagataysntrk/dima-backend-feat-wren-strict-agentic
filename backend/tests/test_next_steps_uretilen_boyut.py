"""FAZ 3.4 — `suggest_next_steps` ilişki-türevi boyutları da göstersin.

ÖLÇÜLDÜ (2 Ağustos 2026): Faz 1 üreteci katalogda 7 boyut açtı (`bakim`/`kalite`/
`makine_duruslari`/`oee` → **bölüm**, `parti`/`surdurulebilirlik` → **kısım**, `kalite` →
**operatör**) ve `suggest_next_steps` bunların **sıfırını** öneriyordu. `parti`nin 15
boyutundan chip'e yalnız `makine` + `hat` çıkıyordu.

Sebep sıralama DEĞİL, **kesme**: `dims[:2]` manifest sırasını alıyor, üreteç ise boyutları
metadata'nın SONUNA ekliyor. Bu yüzden planın önerdiği "hop-derinliğine göre sırala" tek
başına ETKİSİZDİR — yerli boyutlar zaten manifest başındadır, sıralamak çıktıyı hiç
değiştirmez. Düzeltme kesmede: iki kırılım slotundan biri türev boyuta ayrılır.

Neden ikinci YERLİ chip feda ediliyor: yerli boyut kullanıcının zaten yazabileceği bir
kelimedir (*"hat bazında"* çalışır). Çapraz-model boyut ise VAR OLDUĞU BİLİNMEYEN bir
yetenektir. Chip bir keşif mekanizmasıdır; keşfedilmesi gerekeni göstermelidir.
"""

from __future__ import annotations

import pytest

from app import cube_router


@pytest.fixture(scope="module")
def index(schema):
    return {c["name"]: c for c in schema.get("cubes", [])}


def _kirilim_chipleri(index, cube_adi):
    spec = index[cube_adi]
    steps = cube_router.suggest_next_steps(
        {"cube": cube_adi, "measures": [spec["measures"][0]]}, index)
    return steps, [s for s in steps if s["kind"] == "dimension"]


def test_uretilen_boyutu_olan_HER_cube_onu_oneriyor(index):
    """Kapı: üretilen boyutu olan bir cube onu chip'lemiyorsa Faz 1'in açtığı yetenek
    kullanıcıya görünmez kalır."""
    kapsam = {ad: sorted((c.get("dimension_origin") or {}).keys())
              for ad, c in index.items() if c.get("dimension_origin")}
    assert kapsam, "katalogda hiç üretilen boyut yok — Faz 1 geri mi alındı?"
    eksik = []
    for ad, uretilenler in kapsam.items():
        _, dims = _kirilim_chipleri(index, ad)
        onerilen = {d["cube_query"]["dimensions"][-1] for d in dims}
        if not (onerilen & set(uretilenler)):
            eksik.append(f"{ad}: üretilen={uretilenler} önerilen={sorted(onerilen)}")
    assert not eksik, "ÜRETİLEN BOYUT CHIP'TE YOK:\n  " + "\n  ".join(eksik)


def test_yerli_boyut_HALA_ilk_sirada(index):
    """Türev boyut yerli boyutun YERİNE değil YANINA geçer — ilk chip hep yerli kalır.
    Aksi halde en olağan kırılım ("makine kırılımı") ikinci plana düşerdi."""
    for ad, c in index.items():
        if not c.get("dimension_origin"):
            continue
        _, dims = _kirilim_chipleri(index, ad)
        assert dims, ad
        ilk = dims[0]["cube_query"]["dimensions"][-1]
        assert ilk not in (c.get("dimension_origin") or {}), (
            f"{ad}: ilk kırılım chip'i türev boyut ({ilk}) — yerli olmalıydı")


def test_uretilen_boyutu_OLMAYAN_cube_degismedi(index):
    """SIFIR REGRESYON KAPISI. Üretilen boyutu olmayan cube'larda kesme kuralı eskisiyle
    birebir aynı çalışmalı (manifest sırasına göre ilk iki kullanılmayan boyut)."""
    for ad, c in index.items():
        if c.get("dimension_origin"):
            continue
        _, dims = _kirilim_chipleri(index, ad)
        beklenen = [d for d in (c.get("dimensions") or [])
                    if not (d.endswith("_kodu") and f"{d[:-5]}_adi" in (c.get("dimensions") or []))
                    ][:2]
        assert [d["cube_query"]["dimensions"][-1] for d in dims] == beklenen, ad


def test_ic_alan_disari_SIZMIYOR(index):
    """Seçim `_ad` yardımcı alanıyla yapılıyor; o alan `NextStep` şemasında YOK ve
    yanıta sızarsa pydantic'e kadar taşınır."""
    for ad in index:
        steps, _ = _kirilim_chipleri(index, ad)
        for s in steps:
            assert set(s) == {"label", "kind", "cube_query"}, (ad, s)


def test_birden_cok_turevde_SICRAMA_sirasi(index):
    """`kalite` iki türev boyut taşıyor (bölüm + operatör) → yakın olan önce. Bugün ikisi
    de hops=1 olduğu için kural manifest sırasına düşer; katalog derinleştiğinde (2
    sıçramalı yayımlanmış boyut belirdiğinde) anlam kazanır ve o güne kadar davranışı
    DEĞİŞTİRMEZ."""
    origin = index["kalite"].get("dimension_origin") or {}
    assert len(origin) >= 2, "kalite artık çok türevli değil — testin gerekçesi kalktı"
    _, dims = _kirilim_chipleri(index, "kalite")
    turev = [d["cube_query"]["dimensions"][-1] for d in dims
             if d["cube_query"]["dimensions"][-1] in origin]
    assert len(turev) == 1, f"iki slotun ikisi de türeve gitti: {turev}"
    en_yakin = min(origin, key=lambda d: origin[d].get("hops", 1))
    assert turev[0] == en_yakin, f"{turev[0]} seçildi ama {en_yakin} daha yakın"


def test_chip_cube_query_GERCEKTEN_calisir(index, schema):
    """Chip tıklanınca `/cube` ile LLM'siz koşar — türev boyut o yolda da derlenmeli.
    (Faz 1'in JOIN'i cube derleyicisinde değil MODEL katmanında oluşuyor; bu test o
    zincirin chip yolundan da geçtiğini doğrular.)"""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    denendi = 0
    for ad, c in index.items():
        origin = c.get("dimension_origin") or {}
        if not origin:
            continue
        _, dims = _kirilim_chipleri(index, ad)
        for d in dims:
            if d["cube_query"]["dimensions"][-1] not in origin:
                continue
            sql = svc.cube_sql(d["cube_query"])
            assert svc.dry_plan(sql).upper().count(" JOIN ") >= 1, (
                f"{ad}.{d['cube_query']['dimensions'][-1]}: türev boyut ama JOIN yok")
            # `query()` cube SQL'ini KENDİ planlar — planlanmışı vermek çift planlama olur.
            assert svc.query(sql)["rows"], f"{ad}: chip boş sonuç döndürdü"
            denendi += 1
    assert denendi >= 6, f"yalnız {denendi} türev chip sınandı"
