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
    import pathlib
    import re

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    cagrilar: list[str] = []
    for f in kok.rglob("*.py"):
        if f.name == "viz.py":
            continue
        metin = f.read_text(encoding="utf-8")
        for m in re.finditer(r"(?:_?viz)\.recommend\(", metin):
            # Eşleşen kapanış parantezine kadar (sabit pencere uzun yorumlarda yanılır).
            derinlik, i = 0, m.end() - 1
            while i < len(metin):
                if metin[i] == "(":
                    derinlik += 1
                elif metin[i] == ")":
                    derinlik -= 1
                    if derinlik == 0:
                        break
                i += 1
            cagrilar.append(f"{f.relative_to(kok)}::{metin[m.end() - 1:i]}")
    assert cagrilar, "hiç çağrı bulunamadı — test bir şey korumuyor"
    eksik = [c for c in cagrilar if "meta_args" not in c]
    assert not eksik, ("`viz.recommend` argümanları elle toplanmış:\n  "
                       + "\n  ".join(x.split("::")[0] for x in eksik))


def test_CUBE_QUERY_her_yuzeyde_geciriliyor():
    """`cube_query` boyut OTORİTESİDİR (Faz C1): onsuz `recommend()` kolon rollerini
    veriden TAHMİN eder ve zaman/kategori ayrımı yanlış çıkabilir. Bir yüzey onu
    geçirmezse aynı sorunun grafiği o yüzeyde farklı olur."""
    import pathlib
    import re

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    eksik: list[str] = []
    for f in kok.rglob("*.py"):
        if f.name == "viz.py":
            continue
        metin = f.read_text(encoding="utf-8")
        for m in re.finditer(r"(?:_?viz)\.recommend\(", metin):
            derinlik, i = 0, m.end() - 1
            while i < len(metin):
                if metin[i] == "(":
                    derinlik += 1
                elif metin[i] == ")":
                    derinlik -= 1
                    if derinlik == 0:
                        break
                i += 1
            if "cube_query" not in metin[m.end() - 1:i]:
                eksik.append(str(f.relative_to(kok)))
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
