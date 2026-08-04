"""E-posta viz render (app.viz_email) — email-safe HTML/CSS grafik davranış kilidi (ADR-0024).

Karar backend viz motorundan gelir; email JS çalıştırmaz → yatay-bar/KPI HTML. Karmaşık tipler
(heatmap/scatter/pivot/facet*) tabloya bırakılır (None).
"""

from __future__ import annotations

from app import viz, viz_email


def _viz(columns, rows, units, cq):
    return viz.recommend({"columns": columns, "rows": rows}, units=units, cube_query=cq)


def test_bar_renders_horizontal_bars():
    # ⟳ FAZ 5.11 — örnek **4 kaleme** çıkarıldı. Testin amacı *"bar → yatay çubuk HTML'i"*
    # ve o amaç aynen duruyor; 3 kategoride backend artık grafik ÇİZMİYOR (§15.6 kural 2)
    # ve `render_chart_html` doğru davranıp `None` dönüyor. *Bir testin örneği
    # değişebilir; ölçtüğü şey değişmemeli.*
    rows = [{"musteri": "A", "ciro": 120}, {"musteri": "B", "ciro": 80},
            {"musteri": "C", "ciro": 45}, {"musteri": "D", "ciro": 30}]
    spec = _viz(["musteri", "ciro"], rows, {"ciro": "₺"},
                {"cube": "x", "measures": ["ciro"], "dimensions": ["musteri"]})
    html = viz_email.render_chart_html(spec, rows)
    assert html and "<table" in html
    assert html.count("<tr>") == 4          # dört bar satırı
    assert "background:" in html and "width:100%" in html
    assert "₺" in html                        # birimli değer


def test_bar_sorts_desc_and_caps():
    rows = [{"m": f"M{i}", "v": i} for i in range(20)]
    spec = _viz(["m", "v"], rows, {"v": ""},
                {"cube": "x", "measures": ["v"], "dimensions": ["m"]})
    html = viz_email.render_chart_html(spec, rows, max_bars=12)
    assert html.count("<tr>") == 12          # ilk 12
    assert "satır daha" in html               # +N notu
    # değere göre azalan → en büyük (M19) en üstte
    assert html.index("M19") < html.index("M8")


def test_time_series_preserves_order():
    rows = [{"ay": f"2026-0{i}", "uretim": i * 10} for i in range(1, 6)]
    spec = _viz(["ay", "uretim"], rows, {"uretim": "kg"},
                {"cube": "x", "measures": ["uretim"],
                 "timeDimensions": [{"dimension": "ay", "granularity": "month"}]})
    # zaman ekseni: line kararı, sıra KRONOLOJİK korunur (değere göre sıralamaz)
    html = viz_email.render_chart_html(spec, rows)
    assert html and html.index("2026-01") < html.index("2026-05")


def test_kpi_renders_cards():
    rows = [{"ciro": 1234567.0, "fire_kg": 5321.0}]
    spec = _viz(["ciro", "fire_kg"], rows, {"ciro": "₺", "fire_kg": "kg"},
                {"cube": "x", "measures": ["ciro", "fire_kg"], "dimensions": []})
    assert spec["kind"] == "kpi"
    html = viz_email.render_chart_html(spec, rows)
    assert html and "border-radius:8px" in html
    assert "ciro" in html and "fire_kg" in html


def test_complex_kinds_fall_back_to_table():
    # heatmap → email grafik değil (None) → template tabloya düşer
    rows = [{"vardiya": v, "gun": g, "oee": 70 + i}
            for i, (v, g) in enumerate(
                [(v, g) for v in ("A", "B", "C") for g in ("Pzt", "Sal", "Çar")])]
    spec = _viz(["vardiya", "gun", "oee"], rows, {"oee": "%"},
                {"cube": "x", "measures": ["oee"], "dimensions": ["vardiya", "gun"]})
    assert spec["kind"] == "heatmap"
    assert viz_email.render_chart_html(spec, rows) is None


def test_empty_none():
    assert viz_email.render_chart_html(None, []) is None
    assert viz_email.render_chart_html({"kind": "bar"}, []) is None


def test_label_html_escaped():
    # ⟳ FAZ 5.11 — aynı gerekçe: örnek 4 kaleme çıkarıldı. Testin amacı **enjeksiyon
    # koruması**dır ve o amaç kategori sayısından bağımsızdır.
    rows = [{"ad": "<script>x</script>", "v": 5}, {"ad": "B", "v": 3},
            {"ad": "C", "v": 2}, {"ad": "D", "v": 1}]
    spec = _viz(["ad", "v"], rows, {"v": ""},
                {"cube": "x", "measures": ["v"], "dimensions": ["ad"]})
    html = viz_email.render_chart_html(spec, rows)
    assert "<script>" not in html and "&lt;script&gt;" in html  # injection guard
