"""JENERİK clone/sync orkestrasyonu (datasource-BAĞIMSIZ). SourceAdapter'dan okur,
TargetAdapter'a yazar (admin_app/clone/adapters.py). CLI (snapshot_mssql) + admin API
bunu ORTAK kullanır.

İki mod:
  - full_clone: her tablo DROP+yeniden yükle (tam ayna).
  - incremental_sync: watermark keşfiyle (discovery) yalnız yeni/DEĞİŞMİŞ satır → PK upsert.

GÜVENLİK — assert_not_self_clone: kaynak (datasource+sunucu+DB) == hedef (datasource+sunucu)+
hedef-DB ise REDDEDER. "Clone'u kendi içine kopyalayıp veriyi silme" faciasını kapatır.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from admin_app.clone.adapters import SelfCloneError

# progress_cb(done, total, table, rows, status): status "ok"|"skip"|"full"|"incremental"|"fail:.."
ProgressCb = Callable[[int, int, str, int, str], None]


def target_db_name(slug: str) -> str:
    return f"{slug.upper()}_SNAP"


def assert_not_self_clone(source, target, target_db: str) -> None:
    """Kaynak == hedef (aynı datasource+sunucu, kaynak DB == hedef DB) ise raise."""
    s_ds, s_srv, s_db = source.server_identity()
    t_ds, t_srv, _ = target.server_identity()
    if s_ds == t_ds and s_srv == t_srv and s_db == target_db.lower():
        raise SelfCloneError(
            f"Kaynak == hedef ({s_ds}:{s_srv}/{s_db}): bağlantı klonun KENDİSİNE bakıyor. "
            f"Clone iptal (aksi halde hedef tablolar boşalırdı). Kaynağı canlı/upstream "
            f"DB'ye yönlendirin (ayrı 'source' bağlantısı).")


def _copy_full(source, target, db: str, table: str) -> int:
    """Bir tabloyu tam kopyala (DROP+CREATE+INSERT). Dönüş: satır (kolon yoksa -1=skip)."""
    cols = source.columns(table)
    if not cols:
        return -1
    target.create_table(db, table, cols)
    colnames = [n for n, _ in cols]
    total = 0
    for batch in source.read_all(table, colnames):
        target.insert(db, table, colnames, [tuple(source.fix(v) for v in r) for r in batch])
        total += len(batch)
    return total


def full_clone(source, target, db: str, tables: Iterable[str],
               progress: ProgressCb | None = None) -> dict:
    """Tam ayna: her tablo DROP+yeniden yükle. HER TABLO İZOLE (biri patlarsa devam)."""
    assert_not_self_clone(source, target, db)
    target.ensure_db(db)
    tables = list(tables)
    ok = skip = fail = rows_tot = 0
    for i, tab in enumerate(tables, 1):
        try:
            rows = _copy_full(source, target, db, tab)
            if rows < 0:
                skip += 1
                if progress:
                    progress(i, len(tables), tab, 0, "skip")
            else:
                ok += 1; rows_tot += rows
                if progress:
                    progress(i, len(tables), tab, rows, "ok")
        except Exception as exc:  # noqa: BLE001 — tablo-izole dayanıklılık
            fail += 1
            source.rollback(); target.rollback()
            if progress:
                progress(i, len(tables), tab, 0, f"fail:{str(exc)[:80]}")
    return {"ok": ok, "skip": skip, "fail": fail, "rows": rows_tot, "total": len(tables)}


def _sync_one(source, target, db: str, table: str, last_wm,
              state_set: Callable[[str, object, int], None]) -> tuple[int, str]:
    """Bir tablonun incremental sync'i. Dönüş: (değişen_satır, mod)."""
    wm = source.discover_watermark(table)          # (kolon, mod) | None
    pk = source.primary_key(table)
    wm_col = wm[0] if wm else None
    # İlk sefer / watermark yok / PK yok / hedefte tablo yok → tam ayna.
    if not wm_col or not pk or last_wm is None or not target.table_exists(db, table):
        rows = _copy_full(source, target, db, table)
        rows = max(rows, 0)
        new_wm = source.max_watermark(table, wm_col) if wm_col else None
        state_set(table, new_wm, rows)
        return rows, "full"

    cols = source.columns(table)
    colnames = [n for n, _ in cols]
    pk_idx = [colnames.index(k) for k in pk if k in colnames]
    wm_idx = colnames.index(wm_col) if wm_col in colnames else None
    changed = 0
    new_wm = last_wm
    for batch in source.read_since(table, colnames, wm_col, last_wm):
        if pk_idx:  # upsert: değişen PK'ları sil, sonra ekle (yeni + değişmiş eski)
            for r in batch:
                target.delete_pk(db, table, pk, [r[i] for i in pk_idx])
        target.insert(db, table, colnames,
                      [tuple(source.fix(v) for v in r) for r in batch])
        changed += len(batch)
        if wm_idx is not None and batch:
            bmax = max(r[wm_idx] for r in batch)
            if new_wm is None or bmax > new_wm:
                new_wm = bmax
    state_set(table, new_wm, changed)
    return changed, "incremental"


def incremental_sync(source, target, db: str, tables: Iterable[str],
                     state_get: Callable[[str], object],
                     state_set: Callable[[str, object, int], None],
                     progress: ProgressCb | None = None) -> dict:
    """Incremental: her tablo için watermark keşfi → yeni/değişmiş satır → PK upsert.
    state_get(table)→last_wm; state_set(table, new_wm, rows). Watermark'sız → full."""
    assert_not_self_clone(source, target, db)
    target.ensure_db(db)
    tables = list(tables)
    ok = fail = rows_tot = 0
    for i, tab in enumerate(tables, 1):
        try:
            changed, mode = _sync_one(source, target, db, tab, state_get(tab), state_set)
            ok += 1; rows_tot += changed
            if progress:
                progress(i, len(tables), tab, changed, mode)
        except Exception as exc:  # noqa: BLE001
            fail += 1
            source.rollback(); target.rollback()
            if progress:
                progress(i, len(tables), tab, 0, f"fail:{str(exc)[:80]}")
    return {"ok": ok, "fail": fail, "rows": rows_tot, "total": len(tables)}
