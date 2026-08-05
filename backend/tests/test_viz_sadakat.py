"""FAZ I4/I5 — YÜZEYLER ARASI SADAKAT: tek VizSpec, N oluşturucu.

## Sözleşme

> Aynı `cube_query` için ekran · e-posta · rapor · pano · resume **AYNI VizSpec
> kararlarını** üretmelidir. `viz.recommend()` **tek** bir karar verir; yüzeyler onu
> **render eder**, yeniden karar VERMEZ.

## Neden bu test var

Bu sözleşme kodda zaten iddia ediliyordu ama **hiçbir şey onu tutmuyordu** ve iki kez
kırılmıştı — ikisi de kodda kayıtlı:

1. Bir çağıran birim sözlüğünü **`measure_units`** diye yanlış anahtarla geçiyordu;
   `recommend()`'in birim farkındalığı o yolda **hiç** devreye girmemişti.
2. `semi_additive`/`non_additive` `schema()`'da üretiliyor ama **hiçbir çağıran**
   geçirmiyordu (Faz I1'de ölçüldü) — yani `bakiye` bazı yüzeylerde yığılabilirdi.

Faz I1 `viz.meta_args()` ile argüman toplamayı **tek kaynağa** indirdi. Bu dosya o
kazancın **davranış** düzeyinde tutulduğunu kilitler: argümanlar aynı yerden gelse bile
bir çağıran `cube_query` geçirmeyi unutursa karar yine ayrışır.

**Sapma sessizdir ve bu yüzden tehlikelidir:** kullanıcı ekranda çizgi grafiği görür,
e-postada aynı sorunun bar grafiğini alır ve hangisinin doğru olduğunu bilemez.
"""

from __future__ import annotations

import pytest

import ast as ast_mod

from app import viz

# Karar üreten alanlar — sadakat bunların üstünde tanımlıdır. `alternatives` de dahil:
# kullanıcıya sunulan toggle seçenekleri de bir karardır ve yüzeyler arasında değişmemeli.
KARAR_ALANLARI = ("kind", "measures", "dims", "time_col", "primary_dim", "series_dim",
                  "stackable", "partition", "dual_axis", "unit_count", "alternatives")


def _karar(spec: dict | None) -> dict:
    return {k: (spec or {}).get(k) for k in KARAR_ALANLARI}


@pytest.fixture
def ornek(schema):
    """Gerçek bir cube + gerçek metadata — sentetik bir sözlük sadakat sorusunu
    cevaplamaz, çünkü asıl risk metadata'nın YOLDA KAYBOLMASIDIR."""
    cube = next((c for c in schema["cubes"] if c["name"] == "parti"), None)
    assert cube, "parti cube'u yok"
    result = {
        "columns": ["makine", "toplam_ciro"],
        "rows": [{"makine": f"M-{i:02d}", "toplam_ciro": 1000.0 * (10 - i)} for i in range(1, 7)],
        "row_count": 6,
    }
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"],
          "filters": []}
    return cube, result, cq


# --- ASIL KAPI: aynı girdi → aynı karar ------------------------------------------

def _recommend_cagrilari() -> list[tuple[str, ast_mod.Call]]:
    """`viz.recommend(...)` **gerçek çağrıları** — AST ile.

    ⚠ **Belirteç AST'ye çevrildi (FAZ 5.12).** Regex taraması `features.py`'nin bayrak
    **açıklama metnini** yakalayıp yanlış-kırmızı verdi: o metin `viz.recommend()`
    ifadesini *anlatmak* için içeriyordu. Bu deponun **on ikinci kez** ödediği ders —
    *beyan ile beyanın anlatımı farklı şeylerdir.*
    """
    import pathlib

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    out: list[tuple[str, ast_mod.Call]] = []
    for f in kok.rglob("*.py"):
        if f.name == "viz.py":
            continue
        agac = ast_mod.parse(f.read_text(encoding="utf-8"))
        for n in ast_mod.walk(agac):
            if (isinstance(n, ast_mod.Call)
                    and getattr(n.func, "attr", "") == "recommend"
                    and getattr(getattr(n.func, "value", None), "id", "")
                    in ("viz", "_viz")):
                out.append((str(f.relative_to(kok)), n))
    return out


def test_AYNI_girdi_AYNI_karar(ornek):
    """`recommend()` saf olmalı: aynı girdi her çağrıda aynı kararı vermeli. Aksi halde
    "tek VizSpec" iddiası zaten çöker."""
    cube, result, cq = ornek
    a = viz.recommend(result, cube_query=cq, **viz.meta_args(cube))
    b = viz.recommend(result, cube_query=cq, **viz.meta_args(cube))
    assert _karar(a) == _karar(b)


def test_META_ARGS_atlanirsa_karar_DEGISIR(ornek):
    """Bu testin varlık sebebi: metadata yolda kaybolursa karar SESSİZCE değişir.
    Sadakatin neden argüman toplamaya değil TEK KAYNAĞA bağlandığının kanıtı."""
    cube, result, cq = ornek
    tam = viz.recommend(result, cube_query=cq, **viz.meta_args(cube))
    ciplak = viz.recommend(result, cube_query=cq)          # metadata YOK
    assert tam is not None and ciplak is not None
    # En az bir karar alanı ayrışmalı — ayrışmıyorsa bu cube/metadata birleşimi
    # sadakat riskini göstermiyor demektir ve test bir şey korumaz.
    assert _karar(tam) != _karar(ciplak) or (cube.get("units") or {}) == {}, (
        "metadata'sız çağrı aynı kararı verdi — bu örnek sadakat riskini göstermiyor")


# --- YÜZEYLER: hepsi meta_args'tan besleniyor mu? -------------------------------

def test_TUM_YUZEYLER_ayni_yardimciyi_kullanir():
    """Yapısal kilit (Faz I1'in tamamlayıcısı). Argümanları elle toplayan bir yüzey
    geri gelirse sadakat davranış testleriyle YAKALANMAYABİLİR — o yüzey belki hiç
    test edilmiyordur. Kaynak taraması bu boşluğu kapatır."""
    cagrilar = _recommend_cagrilari()
    assert cagrilar, "hiç çağrı bulunamadı — test bir şey korumuyor"
    eksik = [
        dosya for dosya, c in cagrilar
        if not any(k.arg is None                      # `**viz.meta_args(...)`
                   and getattr(getattr(k.value, "func", None), "attr", "") == "meta_args"
                   for k in c.keywords)
    ]
    assert not eksik, ("`viz.recommend` argümanları elle toplanmış:\n  "
                       + "\n  ".join(sorted(set(eksik))))


def test_CUBE_QUERY_her_yuzeyde_geciriliyor():
    """`cube_query` boyut OTORİTESİDİR (Faz C1): onsuz `recommend()` kolon rollerini
    veriden TAHMİN eder ve zaman/kategori ayrımı yanlış çıkabilir. Bir yüzey onu
    geçirmezse aynı sorunun grafiği o yüzeyde farklı olur."""
    eksik = [
        dosya for dosya, c in _recommend_cagrilari()
        if not any(k.arg == "cube_query" for k in c.keywords)
    ]
    assert not eksik, f"`cube_query` geçirmeyen yüzey(ler): {sorted(set(eksik))}"


# --- E-POSTA yüzeyi: aynı spec'i mi render ediyor? ------------------------------

def test_EPOSTA_kendi_karar_VERMEZ():
    """`viz_email.py` bir RENDER edicidir. Kendi `analyze()`/`recommend()` mantığını
    yazarsa ekran ile e-posta zamanla ayrışır — ve sapma sessiz olur."""
    import inspect

    from app import viz_email

    kaynak = inspect.getsource(viz_email)
    # Kendi karar mantığını kurmamalı: recommend'i YENİDEN uygulamamalı.
    assert "def recommend" not in kaynak, "e-posta kendi viz kararını veriyor"
    assert "def analyze" not in kaynak, "e-posta kendi kolon rolü analizini yapıyor"


def test_RAPOR_kendi_karar_VERMEZ():
    import inspect

    from app import report

    kaynak = inspect.getsource(report)
    assert "def recommend" not in kaynak and "def analyze" not in kaynak


# --- Faz I1'in kazancı davranışta tutuluyor mu? --------------------------------

def test_TOPLANAMAZ_olcu_her_yuzeyde_yigilmaz(schema):
    """`bakiye` `additive: semi` beyanlı. Bir yüzey `meta_args`'ı atlarsa O YÜZEYDE
    yığılabilir — kullanıcı ekranda doğru, e-postada yanlış grafiği görür."""
    cube = next((c for c in schema["cubes"] if c["name"] == "cari"), None)
    if not cube or "bakiye" not in (cube.get("semi_additive") or []):
        pytest.skip("bu katalogda semi-additive beyanı yok")
    result = {"columns": ["ay", "cari_tip", "bakiye"],
              "rows": [{"ay": f"2026-0{i}", "cari_tip": t, "bakiye": 100.0 * i}
                       for i in range(1, 7) for t in ("A", "B", "C", "D", "E", "F")],
              "row_count": 36}
    cq = {"cube": "cari", "measures": ["bakiye"], "dimensions": ["cari_tip"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}], "filters": []}
    spec = viz.recommend(result, cube_query=cq, **viz.meta_args(cube))
    assert spec["stackable"] is False and spec["kind"] != "stacked"


# --- YÖN KAYNAĞI: cube kapsamlı, şema birleşimi DEĞİL --------------------------

def test_lower_set_VizSpecte_tasinir(schema):
    """ÖLÇÜLEN KUSUR (2026-08-02). Frontend `lower_is_better`'ı TÜM CUBE'LARIN
    BİRLEŞİMİ olarak okuyordu ve VizSpec'in cube-kapsamlı `lower_set`'ini YOK SAYIYORDU.

    Demo'da gerçek bir çakışma var: `toplam_dogalgaz_sm3` `surdurulebilirlik`'te
    düşük-iyi, `enerji_makine`'de DEĞİL. Birleşim ikisinde de ısı paletini ters
    çevirirdi — aynı sayı, yanlış cube'da YANLIŞ RENKLE okunurdu.
    """
    from app import viz

    cube = next((c for c in schema["cubes"] if c.get("lower_is_better")), None)
    if not cube:
        pytest.skip("bu katalogda lower_is_better beyanı yok")
    olcu = (cube.get("lower_is_better") or [])[0]
    r = {"columns": ["d", olcu],
         "rows": [{"d": f"K{i}", olcu: float(i)} for i in range(1, 5)], "row_count": 4}
    spec = viz.recommend(r, cube_query={"cube": cube["name"], "measures": [olcu],
                                        "dimensions": ["d"], "filters": []},
                         **viz.meta_args(cube))
    assert spec and olcu in (spec.get("lower_set") or []), (
        "VizSpec yön bilgisini taşımıyor — FE şema birleşimine düşer ve cube "
        "kapsamı kaybolur")


def test_CAKISAN_olcu_cube_kapsaminda_ayrisir(schema):
    """Aynı ölçü adı bir cube'da düşük-iyi, başkasında değilse VizSpec'ler AYRIŞMALI."""
    from collections import defaultdict

    from app import viz

    nerede = defaultdict(lambda: [set(), set()])
    for c in schema["cubes"]:
        lis = set(c.get("lower_is_better") or [])
        for m in (c.get("measures") or []):
            nerede[m][0 if m in lis else 1].add(c["name"])
    catisan = {m: v for m, v in nerede.items() if v[0] and v[1]}
    if not catisan:
        pytest.skip("bu katalogda çakışan ölçü yok")

    olcu, (dusuk_cubes, normal_cubes) = next(iter(catisan.items()))
    r = {"columns": ["d", olcu], "rows": [{"d": "A", olcu: 1.0}], "row_count": 1}
    def _spec(cube_adi):
        cm = next(c for c in schema["cubes"] if c["name"] == cube_adi)
        return viz.recommend(r, cube_query={"cube": cube_adi, "measures": [olcu],
                                            "dimensions": ["d"], "filters": []},
                             **viz.meta_args(cm))
    assert olcu in (_spec(sorted(dusuk_cubes)[0]).get("lower_set") or [])
    assert olcu not in (_spec(sorted(normal_cubes)[0]).get("lower_set") or []), (
        f"{olcu}: yön cube kapsamında ayrışmıyor — birleşim davranışı sürüyor")
