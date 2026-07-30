"""JENERİK incremental DB sync/clone (ERP-BAĞIMSIZ). Değişiklik-algılama HARDCODE edilmez,
KEŞFEDİLİR — her tablo için en iyi "watermark" kolonu otomatik bulunur:

  1. rowversion/timestamp TİPLİ kolon (SQL Server; her değişiklikte otomatik artar) — evrensel.
  2. datetime kolonlar arasında "değiştirilme/güncelleme" İSMİ (cross-ERP: modified/updated/
     changed/last_mod/güncelle/duzeltme/degistir/aedat…). Netsis DUZELTMETARIHI bunun ÖRNEĞİ.
  3. yoksa → full refresh (küçük tablo) ya da çağıran full alır.

Watermark'lı çekim: `WHERE <wm> > @son` → PK'ya MERGE (upsert; hem yeni hem DEĞİŞMİŞ eski satır).
Silme (timestamp'siz) → periyodik full ya da PK-set diff (çağıranın kararı). Datasource-özel
SQL parçaları tek yerde (şimdilik mssql; postgres/mysql aynı arayüzle eklenir).

Bu, snapshot_mssql.py'nin (full clone) incremental kardeşi; admin API bunu çağırır.
"""

from __future__ import annotations

# Datetime "değiştirilme" kolonu isim-sezgisi (cross-ERP, küçük harf; datasource-bağımsız).
_MOD_HINTS = ("duzeltmetarih", "kayittarih", "modified", "updated", "changed", "last_mod",
              "lastmod", "guncelle", "güncelle", "degistir", "değiştir", "aedat", "aetim",
              "edit_date", "editdate", "change_date", "modifydate", "capiblock_modified",
              "son_islem", "islem_tarih")
# rowversion benzeri tipler (mssql) — monotonik, her değişiklikte artar.
_ROWVER_TYPES = ("timestamp", "rowversion")


def discover_watermark(columns: list[tuple[str, str]]) -> tuple[str, str] | None:
    """columns: [(ad, tip)] → (watermark_kolonu, mod) | None. mod: 'rowversion' | 'datetime'.
    Öncelik: rowversion tipi > isim-sezgili datetime. JENERİK — hiçbir ERP/kolon hardcode."""
    for name, typ in columns:
        if typ.lower() in _ROWVER_TYPES:
            return name, "rowversion"
    dt = {"datetime", "datetime2", "smalldatetime", "date", "timestamp", "timestamptz"}
    best: str | None = None
    for name, typ in columns:
        if typ.lower() in dt and any(h in name.lower() for h in _MOD_HINTS):  # noqa: SIM102
            # "duzeltme/modified/updated" > "kayit/created" (değişikliği de yakalayan tercih)
            if best is None or any(h in name.lower() for h in ("duzeltme", "modified", "updated", "changed", "güncelle", "guncelle")):
                best = name
    return (best, "datetime") if best else None


# ---- mssql datasource adaptörü (keşif SQL'leri; postgres/mysql aynı arayüzle eklenir) ----

def mssql_columns(cur, table: str) -> list[tuple[str, str]]:
    cur.execute(
        "SELECT c.name, TYPE_NAME(c.system_type_id) FROM sys.columns c "
        "WHERE c.object_id = OBJECT_ID(?) ORDER BY c.column_id", table)
    return [(n, t or "") for n, t in cur.fetchall()]


def mssql_pk(cur, table: str) -> list[str]:
    """Birincil anahtar kolonları (upsert MERGE için). Yoksa [] → full refresh gerekir."""
    cur.execute(
        "SELECT c.name FROM sys.indexes i "
        "JOIN sys.index_columns ic ON ic.object_id=i.object_id AND ic.index_id=i.index_id "
        "JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id "
        "WHERE i.object_id=OBJECT_ID(?) AND i.is_primary_key=1 ORDER BY ic.key_ordinal", table)
    return [r[0] for r in cur.fetchall()]


def plan_table(cur, table: str) -> dict:
    """Bir tablonun sync PLANINI keşfeder (jenerik): watermark kolonu/modu + PK + strateji.
    strateji: 'incremental' (watermark+PK var) | 'full' (yoksa; küçük/silme-riskli tablo)."""
    cols = mssql_columns(cur, table)
    wm = discover_watermark(cols)
    pk = mssql_pk(cur, table)
    strategy = "incremental" if (wm and pk) else "full"
    return {"table": table, "columns": [c[0] for c in cols],
            "watermark": wm[0] if wm else None, "watermark_mode": wm[1] if wm else None,
            "pk": pk, "strategy": strategy}
