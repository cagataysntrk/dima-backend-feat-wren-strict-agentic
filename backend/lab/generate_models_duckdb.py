"""DuckDB introspection→model üretici (generate_models.py'nin duckdb kardeşi).

boyahane.duckdb'nin tüm tablolarını introspect eder ve WrenAI model YAML'larını
(demo/companies/demo-boyahane/models/<t>/metadata.yml) üretir. Cube'lar + sinonimler
ELLE kalır — üretici yalnız FİZİKSEL katmanı (table_reference + columns + PK) türetir.

Kullanım:
    .venv/bin/python lab/generate_models_duckdb.py
    .venv/bin/python lab/generate_models_duckdb.py --db demo/data/boyahane.duckdb \
        --catalog boyahane --out demo/companies/demo-boyahane/models
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import yaml

# DuckDB tipi → MDL tipi (wren build'in beklediği sözlük)
TYPE_MAP = {
    "TINYINT": "INTEGER", "SMALLINT": "INTEGER", "INTEGER": "INTEGER",
    "BIGINT": "BIGINT", "HUGEINT": "BIGINT",
    "BOOLEAN": "BOOLEAN",
    "FLOAT": "DOUBLE", "DOUBLE": "DOUBLE", "REAL": "DOUBLE",
    "DATE": "DATE", "TIMESTAMP": "TIMESTAMP", "TIMESTAMP_NS": "TIMESTAMP",
    "VARCHAR": "VARCHAR", "TEXT": "VARCHAR",
}

# Join-hedefi tablolar için birincil anahtar (WrenAI MANY_TO_ONE'ın "one" tarafı PK ister).
# Bileşik-anahtarlı aylık özet tabloları (makine_enerji_aylik=makine+ay vb.) join-hedefi
# DEĞİL → PK'sız kalır (aggregate cube base'i; sorun değil).
PK_MAP = {
    "makineler": "makine", "musteriler": "musteri_kodu", "tedarikciler": "tedarikci_kodu",
    "personel": "personel_kodu", "personel_ozluk": "personel_kodu",
    "ham_kartlari": "ham_kodu", "kimyasallar": "kimyasal_kodu",
    "stok_kartlari": "stok_kodu", "depolar": "depo_kodu", "hesap_plani": "hesap_kodu",
    "banka_hesaplari": "banka_kodu", "partiler": "parti_no", "faturalar": "fatura_no",
    "irsaliyeler": "irsaliye_no", "yevmiye_fisleri": "fis_no", "iplik_lotlari": "lot_no",
    "top_stok": "top_no", "teklifler": "teklif_no", "satinalma_siparisleri": "sas_no",
    "sertifikalar": "sertifika_kodu", "ariza_kayitlari": "ariza_no",
    "fiyat_listesi": "id",
}


# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 KİŞİ BEYANI — tek sahip (Faz A1 · ADR gizlilik)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Bu kolonların DEĞERLERİ bir insanı tanımlar → LLM prompt'una **girmez**.
# Deterministik `route()` onları görmeye devam eder (süreç içi), yetenek kaybı yok.
#
# ⚠ NEDEN AD-TABANLI EMNİYET AĞI YETMEZ: `operator` başka bir şemada makine tipi
# olabilir, `ekip` bir bölüm adıdır. *Bir kolonun kişi taşıyıp taşımadığı adından
# çıkarılamaz — beyan edilmesi gerekir.*
#
# 🔴 VE NEDEN BURADA, DOSYALARDA DEĞİL: beyanlar üretilmiş dosyalarda yaşarsa
# üretecin her koşumunda kaybolma riski taşırlar (bir kez **kayboldular** da).
# Burada tek sahip var; aşağıdaki taşıma mekanizması yalnız **emniyet ağıdır**.
KISI_KOLONLARI: dict[str, tuple[str, ...]] = {
    "partiler": ("operator",),
    "personel": ("ad_soyad",),
    "personel_ozluk": ("tc_kimlik", "sgk_no"),
    "ariza_kayitlari": ("mudahale_eden",),
    "bakim_planlari": ("sorumlu",),
    # --- ERP genişletmesi (2026-08-05) ---
    "is_emirleri": ("operator",),
    "uygunsuzluklar": ("operator",),
    "musteri_sikayetleri": ("operator",),
    "duzeltici_faaliyetler": ("sorumlu",),
    "satis_siparisleri": ("satis_temsilcisi",),
    "firsatlar": ("satis_temsilcisi",),
    "musteri_temaslari": ("personel",),
    "egitim_katilim": ("ad_soyad",),
    "performans_degerlendirme": ("ad_soyad",),
    "is_kazalari": ("ad_soyad",),
    "personel_hareketleri": ("ad_soyad",),
    "donem_kapanis": ("kapatan",),
    # ⚠ `bordro` · `puantaj` · `izinler` BEYAN EDİLMEZ — ve bu bir eksiklik değil,
    # bir konvansiyon: onlar `personel_kodu` taşır, **ad taşımaz**. Beyan **adın**
    # üzerindedir (`personel.ad_soyad`), çünkü prompt'a sızması anlamlı olan şey addır.
    # Bir kodu maskelemek gizlilik üretmez, yalnız `route()`in join'ini kırardı.
    #
    # 🔴 Bu üçünü ilk turda ben `ad_soyad` sanıp beyan ettim; yukarıdaki denetim
    # kapısı **ilk koşumunda kendi yazarını yakaladı**. Kapının değeri tam da budur.
}


def introspect(con, table: str) -> list[tuple[str, str]]:
    """(kolon, mdl_tipi) — fiziksel sıra korunur."""
    rows = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = ? AND table_schema = 'main' ORDER BY ordinal_position",
        [table],
    ).fetchall()
    out = []
    for name, dtype in rows:
        base = dtype.split("(")[0].upper()  # DECIMAL(18,2) → DECIMAL
        mdl = TYPE_MAP.get(base, "VARCHAR")
        out.append((name, mdl))
    return out


def pk_for(table: str, cols: list[str]) -> str | None:
    if table in PK_MAP:
        return PK_MAP[table]
    if "id" in cols:
        return "id"
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="demo/data/boyahane.duckdb")
    ap.add_argument("--catalog", default="boyahane")
    ap.add_argument("--out", type=Path, default=Path("demo/companies/demo-boyahane/models"))
    ap.add_argument("--enrich", type=Path,
                    default=Path("demo/companies/demo-boyahane/models_enrich.yml"),
                    help="cross-model calculated/relationship kolonları (yeniden üretimde korunur)")
    args = ap.parse_args()

    enrich: dict = {}
    if args.enrich and args.enrich.exists():
        enrich = yaml.safe_load(args.enrich.read_text()) or {}

    con = duckdb.connect(args.db, read_only=True)
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_name").fetchall()]

    # 🔴 ÖLÇÜLEN GERİLEME (2026-08-05) — bu üreteç **PII beyanlarını siliyordu**.
    #
    # `partiler.operator` · `personel.*` · `ariza_kayitlari.mudahale_eden` ve
    # `bakim_planlari` üzerindeki **`sensitivity: person`** beyanları (Faz A1) elle
    # eklenmişti. Üreteç dosyanın tamamını yeniden yazdığı için **dördü de düştü** —
    # yani operatör ve personel ADLARI yeniden LLM prompt'una akacaktı.
    #
    # > ⚠ Başlıktaki *"elle düzenleme yeniden üretimde ezilir"* uyarısı bunu
    # > **meşrulaştırmıyor**: bir gizlilik beyanı bir biçim tercihi değildir, ve
    # > sessizce kaybolan bir beyan **hiç yazılmamış** beyandan daha tehlikelidir —
    # > çünkü kimse onu bir daha aramaz.
    #
    # *Bir üretecin "kaynak dosyayı ezerim" hakkı, ezdiği şeyin ne olduğunu bilmesini
    # gerektirir.* Artık kolon-başı **koruma listesi** var: fiziksel katman türetilir,
    # BEYANLAR taşınır.
    KORUNAN_KOLON_ANAHTARLARI = ("sensitivity", "label", "description", "not_null")

    onceki: dict[str, dict[str, dict]] = {}
    if args.out.is_dir():
        for d in sorted(args.out.iterdir()):
            f = d / "metadata.yml"
            if not (d.is_dir() and f.exists()):
                continue
            eski = yaml.safe_load(f.read_text()) or {}
            onceki[d.name] = {
                str(c.get("name")): {k: c[k] for k in KORUNAN_KOLON_ANAHTARLARI if k in c}
                for c in (eski.get("columns") or []) if isinstance(c, dict)
            }
            f.unlink()
            d.rmdir()

    # 🔴 BEYAN DENETİMİ — *karşılığı olmayan bir beyan, sessizce hiçbir şey yapmaz.*
    # Bu deponun defterindeki **"beyan var, kod onu tanımıyor"** sınıfı: harita bir
    # kolonu korunmuş sanır, o kolon aslında yoktur (adı değişmiş, tablo yeniden
    # adlandırılmış) ve kimse fark etmez — gizlilik beyanı **var görünüp yok** olur.
    _mevcut = {t: {c for c, _ in introspect(con, t)} for t in tables}
    _hayalet = [f"{t}.{c}" for t, cols in KISI_KOLONLARI.items()
                for c in cols if c not in _mevcut.get(t, set())]
    if _hayalet:
        raise SystemExit(
            "🔴 KİŞİ BEYANI karşılıksız — bu kolonlar veritabanında YOK:\n  "
            + "\n  ".join(_hayalet)
            + "\n\nHaritayı düzelt ya da satırı kaldır; sessiz bir beyan beyan değildir."
        )

    tasinan = beyan = 0
    for table in tables:
        live = introspect(con, table)
        colnames = [c for c, _ in live]
        pk = pk_for(table, colnames)
        columns = []
        for c, t in live:
            col: dict = {"name": c, "type": t}
            if c == pk:
                col["is_primary_key"] = True
                col["not_null"] = True
            # 1) BEYAN (tek sahip) — kişi kolonları yukarıdaki haritadan.
            if c in KISI_KOLONLARI.get(table, ()):
                col["sensitivity"] = "person"
                beyan += 1
            # 2) Emniyet ağı: önceki dosyadaki elle beyanları taşı. ⚠ `not_null`
            # PK'dan geliyorsa üzerine yazılmaz — türetilmiş olan günceldir.
            for k, v in (onceki.get(table, {}).get(c) or {}).items():
                if k not in col:
                    col[k] = v
                    tasinan += 1
            columns.append(col)
        # Cross-model calculated/relationship kolonları (models_enrich.yml) — ADR-0017 §5:
        # `handle` → ilişki kolonu (type = hedef MODEL adı); diğerleri is_calculated ifade.
        for extra in enrich.get(table) or []:
            if "handle" in extra:
                # handle = hedef MODEL adı (type = ad; netsis konvansiyonu). JOIN'i motor üretir.
                columns.append({"name": extra["handle"], "type": extra["handle"],
                                "relationship": extra["relationship"]})
            else:
                columns.append({"name": extra["name"], "type": extra["type"],
                                "is_calculated": True, "expression": extra["expression"]})
        doc = {
            "name": table,
            "table_reference": {"catalog": args.catalog, "schema": "main", "table": table},
            "columns": columns,
        }
        if pk:
            doc["primary_key"] = pk
        out = args.out / table / "metadata.yml"
        out.parent.mkdir(parents=True, exist_ok=True)
        header = (
            f"# ÜRETİLMİŞTİR: lab/generate_models_duckdb.py ← {args.catalog}.{table}\n"
            "# (elle düzenleme yeniden üretimde ezilir; cube'lar/sinonimler packs'te yaşar.)\n"
        )
        out.write_text(header + yaml.dump(doc, allow_unicode=True, sort_keys=False))
        print(f"{out}: {len(columns)} kolon" + (f" (pk={pk})" if pk else ""))

    con.close()
    print(f"\n{len(tables)} model üretildi → {args.out}"
          f"  ·  {beyan} kişi-beyanı UYGULANDI  ·  {tasinan} elle-beyan taşındı")


if __name__ == "__main__":
    main()
