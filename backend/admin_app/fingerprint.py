"""ERP/kaynak fingerprint eşleştirme (ADR-0017 Karar 3).

Girdi: müşteri DB'sinden introspect edilmiş tablo adları. Pack registry'sindeki
``fingerprint`` imzalarıyla (imza tabloları + SQL-LIKE tablo desenleri) eşlenir;
panel EN yüksek skorlu kaynağı önerir, superadmin onaylar. Logo tek-DB-çok-firma
düzeninde firma/dönem kapsamı da tablo adlarından çıkarılır (LG_FFF_PP_*).
"""

from __future__ import annotations

import re


def _like_to_regex(pattern: str) -> re.Pattern:
    """SQL LIKE desenini regex'e çevirir: ``%`` → ``.*``, ``[_]`` → literal ``_``."""
    out = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if pattern.startswith("[_]", i):
            out.append("_")
            i += 3
        elif ch == "%":
            out.append(".*")
            i += 1
        elif ch == "_":
            out.append(".")
            i += 1
        else:
            out.append(re.escape(ch))
            i += 1
    return re.compile("^" + "".join(out) + "$", re.IGNORECASE)


def match_packs(table_names: list[str], kaynak_packs: list[dict]) -> list[dict]:
    """Her kaynak pack'i için eşleşme skoru: [{key, skor, eslesen_tablolar}].

    Skor = imza tablolarının bulunma oranı; desenli imzalarda (Logo) desene uyan
    tablo varlığı da tam eşleşme sayılır. Skor 0 olan pack listeye girmez.
    """
    upper = {t.upper() for t in table_names}
    results = []
    for pack in kaynak_packs:
        fp = pack.get("fingerprint") or {}
        expected = [str(t) for t in fp.get("tablolar") or []]
        patterns = [str(p) for p in fp.get("tablo_desenleri") or []]
        if not expected and not patterns:
            continue
        hits = [t for t in expected if t.upper() in upper]
        pattern_hits = []
        for p in patterns:
            rx = _like_to_regex(p)
            if any(rx.match(t) for t in table_names):
                pattern_hits.append(p)
        total = len(expected) + len(patterns)
        score = (len(hits) + len(pattern_hits)) / total if total else 0.0
        if score > 0:
            results.append({
                "key": pack["key"],
                "skor": round(score, 2),
                "eslesen_tablolar": hits,
                "eslesen_desenler": pattern_hits,
            })
    return sorted(results, key=lambda r: -r["skor"])


_LOGO_PREFIX = re.compile(r"^LG_(\d{3})_(\d{2})_", re.IGNORECASE)


def logo_kapsamlari(table_names: list[str]) -> list[dict]:
    """Tablo adlarından Logo firma/dönem çiftlerini çıkarır: [{firma_no, donem_no, tablo}]."""
    counts: dict[tuple[int, int], int] = {}
    for t in table_names:
        m = _LOGO_PREFIX.match(t)
        if m:
            key = (int(m.group(1)), int(m.group(2)))
            counts[key] = counts.get(key, 0) + 1
    return [{"firma_no": f, "donem_no": d, "tablo": n}
            for (f, d), n in sorted(counts.items())]
