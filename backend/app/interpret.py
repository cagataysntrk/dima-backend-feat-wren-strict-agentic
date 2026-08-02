"""Evrensel çıktı yorumlama — her grafik/tablo/rapor/KPI için data-güdümlü yorum.

İLKE (min-LLM + veri egemenliği): analiz TAMAMEN DETERMİNİSTİK (Python) — en yüksek/düşük,
% değişim, trend yönü, pay, tepe/dip dönem. LLM aritmetik YAPMAZ; opsiyonel anlatım katmanı
yalnız buradaki küçük FACT sözlüğünü cümleye döker (ham satırlar LLM'e GİTMEZ → KVKK).

Çıktı tipini result'ın kolonlarından çıkarır (cube_query/kpi ipucu varsa kullanır); böylece
cube raporu, blend, serbest-SQL, KPI — hepsi aynı motordan geçer. Şablon-tabanlı Türkçe özet
LLM'siz üretilir; LLM sonradan "cilalama" olarak eklenebilir (interpret_llm hook)."""

from __future__ import annotations

import datetime as _dt
from typing import Any

_DATE_NAMES = {"tarih", "ay", "yil", "yıl", "hafta", "gun", "gün", "ceyrek", "çeyrek",
               "donem", "dönem", "date", "month", "year", "week", "day", "quarter", "period"}
_MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _is_num(v: Any) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v.replace(",", "."))
            return True
        except ValueError:
            return False
    return False


def _num(v: Any) -> float:
    return float(str(v).replace(",", ".")) if not isinstance(v, (int, float)) else float(v)


def _looks_date(v: Any) -> bool:
    if isinstance(v, (_dt.date, _dt.datetime)):
        return True
    if isinstance(v, str) and len(v) >= 7:
        return bool(v[:4].isdigit() and (v[4] in "-/" or v[:7].isdigit()))
    return False


def _fmt(v: Any, unit: str | None = None) -> str:
    """Türkçe biçimli sayı (binlik ayraç, gereksiz ondalık yok) + birim."""
    if v is None:
        return "—"
    try:
        n = _num(v)
    except (ValueError, TypeError):
        return str(v)
    s = (f"{n:,.0f}" if abs(n) >= 100 or n == int(n) else f"{n:,.2f}").replace(",", "§") \
        .replace(".", ",").replace("§", ".")
    if unit:
        return f"{s} {unit}" if unit not in ("₺", "$", "€") else f"{unit}{s}"
    return s


def _fmt_bucket(v: Any) -> str:
    """Zaman kovası etiketi — YYYY-MM → 'Şub 2024'."""
    s = str(v)
    if len(s) >= 7 and s[:4].isdigit() and s[5:7].isdigit():
        mi = int(s[5:7])
        if 1 <= mi <= 12:
            return f"{_MONTHS_TR[mi - 1]} {s[:4]}"
    return s[:10]


def _classify(columns: list[str], rows: list[dict],
              cube_query: dict | None = None) -> tuple[list[str], list[str], str | None]:
    """Kolon rolleri — gövdesi `app/result_shape.py`'de (Faz C1).

    ÖNEMLİ DEĞİŞİKLİK: artık `cube_query` OTORİTESİNİ kullanıyor. Eskiden saf değer-tabanlıydı
    ve `interpret()` `cube_query`'yi alıyor olmasına rağmen yalnız `measures` süzgeci için
    kullanıyordu; `dimensions`/`timeDimensions` bilgisini GÖRMEZDEN geliyordu. Sonuç:
    sayısal değerli bir boyut (ay numarası, vardiya no, yıl) ÖLÇÜ sanılıyor ve anlatım
    onun "ortalamasını" bir metrik gibi sunuyordu.
    """
    from app.result_shape import authority_from_cube_query, classify as _rol

    dim_cols, time_hint = authority_from_cube_query(cube_query)
    return _rol(columns, rows, dim_cols=dim_cols, time_col_hint=time_hint)


def _tone(pct: float, lib: bool) -> str:
    """Değer yargısı — YALNIZ yönü BİLİNEN (lower_is_better işaretli) ölçüde. Aksi halde
    boş (adet gibi nötr ölçüde 'yüksek=iyi' varsaymayız → yanıltmayız). lib=düşük iyi:
    artış olumsuz, azalış iyileşme."""
    if not lib or -1 <= pct <= 1:
        return ""
    return " — olumsuz (yükseldi)" if pct > 1 else " — iyileşti (düştü)"


def _series_facts(rows: list[dict], time_col: str, measure: str, unit: str | None,
                  lib: bool = False) -> list[dict]:
    """Zaman serisi: ilk→son % değişim, yön (+lower_is_better ise iyi/kötü çerçeve), tepe/dip."""
    pts = [(str(r[time_col]), _num(r[measure])) for r in rows
           if r.get(time_col) is not None and r.get(measure) is not None]
    pts.sort(key=lambda p: p[0])
    if len(pts) < 2:
        return []
    first, last = pts[0], pts[-1]
    hi = max(pts, key=lambda p: p[1])
    lo = min(pts, key=lambda p: p[1])
    facts = []
    if first[1]:
        pct = (last[1] - first[1]) / abs(first[1]) * 100
        yon = "arttı" if pct > 1 else "azaldı" if pct < -1 else "yatay seyretti"
        facts.append({"type": "trend", "measure": measure, "pct": round(pct, 1),
                      "favorable": (None if not lib or -1 <= pct <= 1 else pct < -1),
                      "text": f"{measure}: {_fmt_bucket(first[0])}→{_fmt_bucket(last[0])} "
                              f"%{abs(round(pct, 1))} {yon} "
                              f"({_fmt(first[1], unit)} → {_fmt(last[1], unit)}){_tone(pct, lib)}"})
    facts.append({"type": "peak", "measure": measure,
                  "text": f"En yüksek {_fmt_bucket(hi[0])} ({_fmt(hi[1], unit)}), "
                          f"en düşük {_fmt_bucket(lo[0])} ({_fmt(lo[1], unit)})"})
    return facts


def _rank_facts(rows: list[dict], dim: str, measure: str, unit: str | None) -> list[dict]:
    """Kategorik top-N: en yüksek varlık + toplam içindeki payı, en düşük, kalem sayısı."""
    agg: dict[str, float] = {}
    for r in rows:
        if r.get(dim) is not None and r.get(measure) is not None:
            agg[str(r[dim])] = agg.get(str(r[dim]), 0.0) + _num(r[measure])
    if not agg:
        return []
    total = sum(agg.values())
    ranked = sorted(agg.items(), key=lambda kv: kv[1], reverse=True)
    top, bot = ranked[0], ranked[-1]
    share = (top[1] / total * 100) if total else 0
    facts = [{"type": "top", "dim": dim, "measure": measure, "entity": top[0],
              "text": f"En yüksek {dim}: {top[0]} ({_fmt(top[1], unit)}"
                      + (f", toplamın %{round(share, 1)}'i)" if total else ")")}]
    if len(ranked) > 1:
        facts.append({"type": "bottom", "dim": dim,
                      "text": f"En düşük: {bot[0]} ({_fmt(bot[1], unit)}); {len(ranked)} kalem"})
    return facts


def _kpi_facts(kpi: dict) -> list[dict]:
    """KPI kartı: değer + iyi/kötü yönü + bileşen dökümü."""
    val, unit = kpi.get("value"), kpi.get("unit")
    label = kpi.get("label") or kpi.get("kpi")
    facts = [{"type": "kpi_value", "text": f"{label}: {_fmt(val, unit)}"}]
    comps = [c for c in (kpi.get("components") or []) if c.get("value") is not None]
    if comps:
        facts.append({"type": "kpi_components",
                      "text": "Bileşenler: "
                              + ", ".join(f"{c.get('label', c['key'])} {_fmt(c['value'], c.get('unit'))}"
                                          for c in comps)})
    return facts


def _signals(rows: list[dict], dims: list[str], time_col: str | None,
             m0: str, unit: str | None, lower_is_better: bool) -> list[dict]:
    """K3 (rehberli analitik) — PROAKTİF sinyaller: nötr FACTS'ten farklı olarak DİKKAT
    çekici durumları işaretler. (a) zaman serisinde ANOMALİ (z-score, detect_anomalies
    reuse), (b) YÖN endişesi (lower_is_better ölçü artıyor / normal ölçü düşüyor —
    "izlenmeli"), (c) YOĞUNLAŞMA (tek kalem payı ≥%50). Deterministik; ham veri LLM'e
    gitmez. severity: info | warning | critical."""
    out: list[dict] = []

    # (a) Zaman serisi anomalisi — schedules.detect_anomalies (aynı z-score motoru).
    if time_col and len(rows) >= 4:
        try:
            from app.schedules import detect_anomalies
            anoms = detect_anomalies({"rows": rows}, m0, k=2.0, unit=unit)
        except Exception:  # noqa: BLE001 - sinyal best-effort
            anoms = []
        if anoms:
            out.append({"severity": "warning", "kind": "anomaly",
                        "text": "Olağandışı değer — " + "; ".join(anoms[:2])})

    # (b) Trend yönü endişesi — ilk→son anlamlı (%10+) değişim, ölçü semantiğine göre kötüyse.
    if time_col and len(rows) > 1:
        try:
            first, last = _num(rows[0].get(m0)), _num(rows[-1].get(m0))
        except (ValueError, TypeError):
            first = last = None
        if first not in (None, 0) and last is not None:
            change = (last - first) / abs(first)
            rising = change > 0
            bad = (rising and lower_is_better) or (not rising and not lower_is_better)
            if abs(change) >= 0.10 and bad:
                yon = "arttı" if rising else "azaldı"
                out.append({"severity": "warning", "kind": "trend",
                            "text": f"{m0} dönem içinde %{abs(change) * 100:.0f} {yon} — izlenmeli"})

    # (c) Yoğunlaşma — kategorik dağılımda tek kalem toplamın ≥%50'si (risk/bağımlılık).
    if dims and not time_col and len(rows) > 2:
        vals = [(_num(r.get(m0)) if _is_num(r.get(m0)) else 0.0) for r in rows]
        tot = sum(vals)
        if tot > 0 and max(vals) / tot >= 0.50:
            out.append({"severity": "info", "kind": "concentration",
                        "text": f"Yoğunlaşma — en yüksek kalem toplamın "
                                f"%{max(vals) / tot * 100:.0f}'i"})
    return out


def interpret(result: dict | None, cube_query: dict | None = None,
              kpi: dict | None = None, units: dict[str, str] | None = None,
              lower_is_better: set[str] | None = None) -> dict | None:
    """Evrensel yorum: {facts:[...], summary:"Türkçe"} | None. TAMAMEN deterministik.

    result: {columns, rows, row_count}. cube_query/kpi ipucu (opsiyonel). units: ölçü→birim.
    lower_is_better: yönü DÜŞÜK=İYİ olan ölçü adları (DSO/CCC/fire…) — trend iyi/kötü çerçevesi."""
    units = units or {}
    lib_set = lower_is_better or set()
    if kpi:
        facts = _kpi_facts(kpi)
        return {"facts": facts, "summary": " · ".join(f["text"] for f in facts)}
    if not result or not result.get("rows"):
        return None
    rows, cols = result["rows"], result.get("columns") or list(result["rows"][0].keys())
    # OTORİTE GEÇİRİLİYOR (Faz C1): `cube_query` zaten elimizdeydi ama yalnız `measures`
    # süzgeci için kullanılıyordu; `dimensions`/`timeDimensions` görmezden geliniyordu.
    measures, dims, time_col = _classify(cols, rows, cube_query)
    if cube_query and cube_query.get("measures"):  # cube ipucu ölçü seçimini netleştirir
        measures = [m for m in cube_query["measures"] if m in measures] or measures
    if not measures:
        return {"facts": [{"type": "count", "text": f"{result.get('row_count', len(rows))} satır"}],
                "summary": f"{result.get('row_count', len(rows))} satırlık sonuç."}

    m0 = measures[0]
    unit = units.get(m0)
    facts: list[dict] = []
    # Tek satır tek ölçü → tek değer.
    if len(rows) == 1 and not dims:
        facts.append({"type": "single", "measure": m0,
                      "text": f"{m0}: {_fmt(rows[0].get(m0), unit)}"})
    elif time_col and len(rows) > 1:              # zaman serisi → trend
        facts += _series_facts(rows, time_col, m0, unit, m0 in lib_set)
        entity = next((d for d in dims if d != time_col), None)
        if entity:  # varlık × zaman (pivot şekli) → kısa not
            n = len({str(r.get(entity)) for r in rows})
            facts.append({"type": "shape", "text": f"{n} {entity} × dönem kırılımı"})
    elif dims:                                     # kategorik → sıralama/pay
        facts += _rank_facts(rows, dims[0], m0, unit)
    if len(measures) > 1:
        facts.append({"type": "measures", "text": f"{len(measures)} ölçü: " + ", ".join(measures)})
    if not facts:
        facts.append({"type": "count", "text": f"{len(rows)} satır"})
    out = {"facts": facts, "summary": " ".join(f["text"].rstrip(".") + "." for f in facts)}
    signals = _signals(rows, dims, time_col, m0, unit, m0 in lib_set)  # K3 proaktif sinyaller
    if signals:
        out["signals"] = signals
    return out
