"""Yapısal finansal tablolar (GL raporları) — Tekdüzen Hesap Planı'ndan DETERMİNİSTİK
gelir tablosu + bilanço. Girdi: mizan satırları [{hesap_kodu, bakiye}] (bakiye = borç −
alacak, ERP-bağımsız kanonik view'dan). Çıktı: sıralı rapor satırları + ara toplamlar.

İŞARET MANTIĞI: bakiye = borç − alacak. Gelir hesapları (60/64/67) ALACAK bakiyeli →
bakiye<0; gider hesapları (61/62/63/65/66/68) BORÇ bakiyeli → bakiye>0. Her satırın
GÖSTERİLEN tutarı = −Σbakiye → gelir POZİTİF, gider NEGATİF; dönem karı = −Σbakiye(6xx).
Ara toplamlar üstteki satırların kümülatif toplamı. Bilançoda aktif (1/2) = Σbakiye,
pasif (3/4/5) = −Σbakiye; aktif = pasif denetimi. LLM YOK — saf aritmetik.
"""

from __future__ import annotations


def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _by_prefix(rows: list[dict], width: int) -> dict[str, float]:
    """hesap_kodu'nun ilk `width` hanesine göre bakiye toplamı."""
    out: dict[str, float] = {}
    for r in rows:
        code = str(r.get("hesap_kodu") or "").strip()
        if len(code) < width or not code[:width].isdigit():
            continue
        out[code[:width]] = out.get(code[:width], 0.0) + _num(r.get("bakiye"))
    return out


# Gelir tablosu (Tekdüzen) — sıra + 2-hane hesap grubu → etiket. None grup = ara toplam
# (üstteki satırların kümülatif toplamı). Gösterilen tutar = −Σbakiye.
_GELIR_TEMPLATE: list[tuple[str | None, str]] = [
    ("60", "Brüt Satışlar"),
    ("61", "Satış İndirimleri (-)"),
    (None, "Net Satışlar"),
    ("62", "Satışların Maliyeti (-)"),
    (None, "BRÜT SATIŞ KARI/ZARARI"),
    ("63", "Faaliyet Giderleri (-)"),
    (None, "FAALİYET KARI/ZARARI"),
    ("64", "Diğer Faaliyetlerden Olağan Gelir/Kar"),
    ("65", "Diğer Faaliyetlerden Olağan Gider/Zarar (-)"),
    ("66", "Finansman Giderleri (-)"),
    (None, "OLAĞAN KAR/ZARAR"),
    ("67", "Olağandışı Gelir/Kar"),
    ("68", "Olağandışı Gider/Zarar (-)"),
    (None, "DÖNEM KARI/ZARARI"),
]


def _map_7a_costs(grp: dict[str, float]) -> dict[str, float]:
    """7/A maliyet hesabı yansıtması: bazı ERP/dönemler maliyeti 6xx'e YANSITMADAN 7/A
    (71-78) hesaplarında tutar (720 Direkt İşçilik, 730 GÜG…). 62x SMM ve 63x faaliyet
    gideri BOŞ ama 7x DOLUysa, 7/A'yı Tekdüzen gelir tablosu slotlarına eşle → maliyetler
    görünür (aksi halde dönem karı = tüm satış, hatalı). 6xx doluysa DOKUNMA (gitas yolu).
    Eşleme: 71-74→62 (SMM/üretim maliyeti), 76-77→63 (pazarlama+genel yönetim), 78→66
    (finansman). Not: stok değişimi ihmal (yaklaşık; tam SMM = 7x − mamul stok artışı)."""
    cost_6xx = sum(abs(grp.get(p, 0.0)) for p in ("62", "63"))
    cost_7xx = sum(abs(grp.get(p, 0.0)) for p in ("71", "72", "73", "74", "76", "77", "78"))
    if cost_6xx > 0.01 or cost_7xx < 0.01:
        return grp  # 6xx zaten var ya da 7x yok → olduğu gibi
    g = dict(grp)
    # 7/A giderleri BORÇ bakiyeli (bakiye>0); gelir tablosunda gider slotu −Σbakiye ile
    # negatife döner → işaret zaten tutarlı, sadece prefix'i 6xx slotuna taşırız.
    g["62"] = g.get("62", 0.0) + sum(grp.get(p, 0.0) for p in ("71", "72", "73", "74"))
    g["63"] = g.get("63", 0.0) + sum(grp.get(p, 0.0) for p in ("76", "77"))
    g["66"] = g.get("66", 0.0) + grp.get("78", 0.0)
    return g


def build_income_statement(rows: list[dict]) -> list[dict]:
    """Mizan satırlarından Tekdüzen gelir tablosu: sıralı {label, amount, kind}. kind =
    'line' (hesap grubu) | 'subtotal' (ara toplam, kümülatif). Deterministik.
    7/A maliyet hesabı fallback: 62x boş + 7x doluysa maliyetler 7/A'dan eşlenir."""
    grp = _map_7a_costs(_by_prefix(rows, 2))
    out: list[dict] = []
    running = 0.0
    for prefix, label in _GELIR_TEMPLATE:
        if prefix is None:
            out.append({"label": label, "amount": round(running, 2), "kind": "subtotal"})
        else:
            amount = -grp.get(prefix, 0.0)  # gelir + / gider −
            running += amount
            out.append({"label": label, "amount": round(amount, 2), "kind": "line"})
    return out


# Bilanço (Tekdüzen) — 1-hane hesap sınıfı. AKTİF (1/2) = Σbakiye (borç bakiyeli varlık);
# PASİF (3/4/5) = −Σbakiye (alacak bakiyeli kaynak). Aktif = Pasif olmalı (denge).
_BILANCO_AKTIF: list[tuple[str, str]] = [
    ("1", "I. DÖNEN VARLIKLAR"),
    ("2", "II. DURAN VARLIKLAR"),
]
_BILANCO_PASIF: list[tuple[str, str]] = [
    ("3", "I. KISA VADELİ YABANCI KAYNAKLAR"),
    ("4", "II. UZUN VADELİ YABANCI KAYNAKLAR"),
    ("5", "III. ÖZKAYNAKLAR"),
]


def _period_result(rows: list[dict]) -> float:
    """Dönem net kâr/zararı = −Σbakiye(6xx), 7/A fallback ile (gelir tablosu son satırı).
    Gelir (60/64/67) alacak bakiyeli → −bakiye pozitif; gider/SMM (61-63/65/66/68) negatif."""
    grp = _map_7a_costs(_by_prefix(rows, 2))
    return round(sum(-grp.get(p, 0.0) for p, _ in _GELIR_TEMPLATE if p is not None), 2)


def build_balance_sheet(rows: list[dict]) -> dict:
    """Mizan satırlarından Tekdüzen bilanço: {aktif:[...], pasif:[...], aktif_toplam,
    pasif_toplam, dengede}. Aktif = Σbakiye(1/2); pasif = −Σbakiye(3/4/5). Deterministik.

    AÇIK DÖNEM: 6xx/7xx sonuç hesapları henüz 590/591'e KAPATILMADIĞI için dönem net
    sonucu özkaynakta görünmez → bilanço ham hâlde dengesizdir. Tekdüzen SUNUMU bu sonucu
    özkaynağa 'Dönem Net Kârı (590) / Zararı (591)' satırı olarak EKLER → denge sağlanır."""
    grp = _by_prefix(rows, 1)
    aktif = [{"label": lbl, "amount": round(grp.get(p, 0.0), 2)} for p, lbl in _BILANCO_AKTIF]
    pasif = [{"label": lbl, "amount": round(-grp.get(p, 0.0), 2)} for p, lbl in _BILANCO_PASIF]
    sonuc = _period_result(rows)  # + kâr / − zarar
    pasif.append({"label": "Dönem Net Kârı (590)" if sonuc >= 0 else "Dönem Net Zararı (591) (-)",
                  "amount": round(sonuc, 2)})
    at = round(sum(x["amount"] for x in aktif), 2)
    pt = round(sum(x["amount"] for x in pasif), 2)
    return {"aktif": aktif, "pasif": pasif, "aktif_toplam": at, "pasif_toplam": pt,
            "dengede": abs(at - pt) < 0.01}


def resolve_statement(svc, kind: str, extra_filters: list | None = None) -> dict:
    """Mizan cube'undan hesap bakiyelerini çeker → gelir tablosu / bilanço üretir.
    kind = 'gelir' | 'bilanco'. svc = WrenService (cube_sql + query). extra_filters =
    dönem filtreleri (ör. yıl). GL = ERP-bağımsız mizan view (gitas Netsis binding'inde).
    Döner: {kind, statement|balance, period?}. Deterministik."""
    cq: dict = {"cube": "mizan", "measures": ["bakiye"], "dimensions": ["hesap_kodu"]}
    if extra_filters:
        cq["filters"] = extra_filters
    sql = svc.cube_sql(cq)
    rows = (svc.query(sql, limit=10000) or {}).get("rows") or []
    if kind == "bilanco":
        return {"kind": "bilanco", "balance": build_balance_sheet(rows), "sql": sql}
    return {"kind": "gelir", "statement": build_income_statement(rows), "sql": sql}
