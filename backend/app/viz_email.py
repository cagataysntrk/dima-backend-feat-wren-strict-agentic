"""E-posta viz render (ADR-0024 cross-surface) — viz spec → email-safe HTML/CSS grafik.

E-posta client'ları JS çalıştırmaz → echarts YOK. Deterministik, evrensel uyumlu YATAY BAR
(CSS genişlik + arka plan renk; Gmail/Outlook/Apple Mail güvenli). Grafik/tablo KARARI backend
viz motorundan gelir (chat/pano ile AYNI); burada yalnız o karara uygun email-safe çizim üretilir.
Karmaşık tipler (heatmap/scatter/pivot/facet*) e-postada tabloya bırakılır (dürüst — zorlamayız).

`height` gibi responsive ölçek YOK (kullanıcı notu): e-posta akışkan tablo, sabit stil yeterli.
"""

from __future__ import annotations

import html
from typing import Any

# Yatay-bar üretilecek tipler. Kalanlar (heatmap/scatter/pivot/facet/facet_measure/table) → tablo.
_BAR_KINDS = {"bar", "stacked", "line", "pie", "treemap"}
_FONT = "system-ui,-apple-system,'Segoe UI',Roboto,sans-serif"


def _num(v: Any) -> float | None:
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def render_chart_html(
    viz: dict | None, rows: list[dict], accent: str = "#0f766e", max_bars: int = 12
) -> str | None:
    """viz spec + satırlar → email-safe HTML grafik (ya da None → tablo yeter/uygun değil)."""
    if not viz or not rows:
        return None
    from app.schedules import _fmt_boyut, _fmt_deger, _ile_birim  # lazy: import döngüsü yok

    kind = viz.get("kind")
    measures = viz.get("measures") or []
    units = viz.get("units") or {}
    if kind == "kpi":
        return _render_kpi(rows[0], measures, units, accent, _fmt_deger, _ile_birim)
    if kind not in _BAR_KINDS:
        return None
    dim = viz.get("time_col") or viz.get("primary_dim")
    if not dim or not measures:
        return None

    m = measures[0]
    unit = units.get(m) or ""
    pairs: list[tuple[str, float]] = []
    for r in rows:
        v = _num(r.get(m))
        if v is None:
            continue
        pairs.append((_fmt_boyut(r.get(dim)), v))
    if not pairs:
        return None
    # Zaman DEĞİLSE değere göre sırala (büyük üstte); zaman ise kronolojik sırayı KORU.
    if not viz.get("time_col"):
        pairs.sort(key=lambda p: p[1], reverse=True)
    shown = pairs[:max_bars]
    more = len(pairs) - len(shown)
    vmax = max((abs(v) for _, v in shown), default=0.0) or 1.0

    title = html.escape(str(m)) + (f" ({html.escape(unit)})" if unit else "")
    parts = [
        f'<div style="font-family:{_FONT};margin:14px 0 4px;">',
        f'<div style="font-size:12px;color:#6b7280;font-weight:600;margin-bottom:6px;">'
        f'{title}</div>',
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="border-collapse:collapse;width:100%;">',
    ]
    for label, v in shown:
        pct = max(2, round(abs(v) / vmax * 100))
        val = _ile_birim(_fmt_deger(v), unit)
        parts.append(
            '<tr>'
            f'<td style="font-size:12px;color:#374151;padding:3px 8px 3px 0;'
            f'white-space:nowrap;vertical-align:middle;max-width:140px;overflow:hidden;'
            f'text-overflow:ellipsis;">{html.escape(label)}</td>'
            '<td style="width:100%;padding:3px 8px;vertical-align:middle;">'
            f'<div style="background:{accent};width:{pct}%;height:11px;border-radius:3px;'
            f'min-width:2px;line-height:11px;">&nbsp;</div></td>'
            f'<td style="font-size:12px;color:#111827;font-weight:600;padding:3px 0;'
            f'white-space:nowrap;text-align:right;vertical-align:middle;'
            f'font-variant-numeric:tabular-nums;">{html.escape(val)}</td>'
            '</tr>'
        )
    parts.append('</table>')
    if more > 0:
        parts.append(
            f'<div style="font-size:11px;color:#9ca3af;margin-top:4px;">+{more} satır daha</div>'
        )
    parts.append('</div>')
    return "".join(parts)


def _render_kpi(
    row: dict, measures: list[str], units: dict, accent: str, fmt_deger, ile_birim
) -> str | None:
    """Tek satır + ölçüler → KPI kart(lar)ı (her ölçü kendi birimiyle)."""
    cards = []
    for m in measures:
        v = _num(row.get(m))
        if v is None:
            continue
        val = ile_birim(fmt_deger(v), units.get(m) or "")
        cards.append(
            '<td style="padding:0 8px 0 0;vertical-align:top;">'
            '<div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px 14px;">'
            f'<div style="font-size:22px;font-weight:700;color:{accent};line-height:1.1;'
            f'font-variant-numeric:tabular-nums;">{html.escape(val)}</div>'
            f'<div style="font-size:11px;color:#6b7280;text-transform:uppercase;'
            f'letter-spacing:.4px;margin-top:6px;">{html.escape(str(m))}</div>'
            '</div></td>'
        )
    if not cards:
        return None
    return (
        f'<div style="font-family:{_FONT};margin:14px 0 4px;">'
        '<table role="presentation" cellpadding="0" cellspacing="0" '
        'style="border-collapse:separate;"><tr>' + "".join(cards) + '</tr></table></div>'
    )
