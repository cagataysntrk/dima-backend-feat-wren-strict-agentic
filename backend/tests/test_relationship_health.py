"""FAZ 1.2/G3 — bildirilen her ilişkinin VERİYLE doğrulanması (fan-out + öksüz sertifikası).

Sektörde standart pratik, ilişki kardinalitesini MODELCİYE BEYAN ETTİRMEKTİR: Cube, LookML,
MetricFlow ve Snowflake hepsi böyle çalışır; Databricks kendi dokümanında `at_most_one_match`
için açıkça *"runtime'da doğrulanmaz"* der. Beyan yanlışsa sonuç hatasız, uyarısız ve
`source="cube"` rozetiyle şişmiş bir sayıdır.

Dima bunu ÖLÇEBİLİR — ve ölçmelidir. Bu dosya, `relationships.yml`'deki her ilişkiyi gerçek
veriye karşı üç açıdan sınar:

  1. FAN-OUT   — hedef ("bir" tarafı) anahtarı BENZERSİZ mi? Değilse join satırları çoğaltır
                 ve SUM'lar şişer. `wren_core` `join_type`'ı OKUMAZ (ölçüldü: MANY_TO_ONE ile
                 MANY_TO_MANY aynı SQL'i üretir), dolayısıyla motorda hiçbir koruma YOKTUR.
  2. NULL      — hedef anahtarında NULL var mı? (benzersizlik testini sessizce delen durum)
  3. ÖKSÜZ     — kaynak ("çok" tarafı) satırlarının hepsi bir hedef buluyor mu? Öksüz oran
                 yüksekse join semantik olarak YANLIŞTIR: kırılımda satırlar NULL kovasına
                 düşer ve o kolona konan HER filtre onları sessizce eler.

(3) somut bir bulgunun ürünüdür (2 Ağustos 2026): `cari_hareketler.cari_kodu` ve
`faturalar.cari_kodu` POLİMORFİK anahtarlardır — `M1001` müşteriyi, `T-204` tedarikçiyi
gösterir. 875 cari hareketinin 412'si `musteriler`e, 463'ü `tedarikciler`e eşleşir. Tek bir
MDL ilişkisi bunu ifade EDEMEZ; `cari_hareketler → musteriler` eklemek satırların %53'ünü
öksüz bırakırdı. `relationships.yml`'in başlığındaki *"cari_kodu/irsaliye gibi master-tablosuz
FK'ler bilinçli ATLANDI"* notu bu yüzden DOĞRUDUR ve bu test onu koruma altına alır: biri
"eksik ilişkiyi tamamlamak" isterse burada durur.

Doğru modelleme (gerektiğinde): müşteri+tedarikçiyi UNION'layan bir `cari` master view'ı,
ya da ayrıştırıcı olarak `cari_tip` boyutu — ki `cari` cube'unda ZATEN var.
"""

from __future__ import annotations

import re

import pytest
import yaml

# Öksüz oranı için üst sınır. 0'da tutuluyor: bugün ölçülen değer bu ve gevşetmek,
# testin yakalamak için var olduğu sınıfı (polimorfik/yanlış join) görünmez kılar.
MAX_ORPHAN_RATE = 0.0

_COND_RE = re.compile(r"^\s*(\w+)\.\"?(\w+)\"?\s*=\s*(\w+)\.\"?(\w+)\"?\s*$")


def _relationships(project_dir):
    f = project_dir / "relationships.yml"
    if not f.exists():
        pytest.skip(f"{f} yok")
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("relationships") or []


def _tables(con) -> set[str]:
    return {r[0] for r in con.execute(
        "select table_name from information_schema.tables where table_schema='main'").fetchall()}


@pytest.fixture(scope="module")
def rels_and_conn():
    import duckdb

    from app.config import get_settings

    s = get_settings()
    project = s.resolved_project_dir()
    rels = _relationships(project)
    db = (s.connection_dict() or {}).get("path") or "demo/data/boyahane.duckdb"
    con = duckdb.connect(str(db), read_only=True)
    try:
        yield rels, con, _tables(con)
    finally:
        con.close()


def _parse(rel: dict):
    """(kaynak_tablo, kaynak_kolon, hedef_tablo, hedef_kolon) — 'çok' → 'bir' yönünde."""
    m = _COND_RE.match(rel.get("condition", ""))
    if not m:
        return None
    la, lc, ra, rc = m.groups()
    models = rel.get("models") or []
    if len(models) != 2:
        return None
    many, one = models[0], models[1]
    # condition'daki taraf sırası models sırasıyla ters olabilir.
    src_col, dst_col = (lc, rc) if la == many else (rc, lc)
    return many, src_col, one, dst_col


def test_her_iliski_ayristirilabiliyor(rels_and_conn):
    rels, _, _ = rels_and_conn
    assert rels, "relationships.yml boş"
    bozuk = [r["name"] for r in rels if _parse(r) is None]
    assert not bozuk, f"condition ayrıştırılamadı (bileşik/karmaşık join?): {bozuk}"


def test_hedef_anahtari_BENZERSIZ_ve_NULLSUZ(rels_and_conn):
    """FAN-OUT KAPISI. Motor `join_type`'ı okumaz — tek gerçek koruma budur."""
    rels, con, tables = rels_and_conn
    sorunlar = []
    for r in rels:
        p = _parse(r)
        if not p:
            continue
        many, _, one, dst = p
        if one not in tables:
            continue
        n, d, nulls = con.execute(
            f'select count(*), count(distinct "{dst}"), count(*) filter (where "{dst}" is null) '
            f"from main.{one}").fetchone()
        if n != d:
            sorunlar.append(f"{r['name']}: {one}.{dst} BENZERSİZ DEĞİL ({n} satır / {d} farklı) "
                            "→ join satırları çoğaltır, SUM'lar şişer")
        if nulls:
            sorunlar.append(f"{r['name']}: {one}.{dst} {nulls} NULL içeriyor")
    assert not sorunlar, "FAN-OUT RİSKİ:\n  " + "\n  ".join(sorunlar)


def test_kaynak_satirlari_OKSUZ_KALMIYOR(rels_and_conn):
    """ÖKSÜZ KAPISI — polimorfik/yanlış join'i yakalar.

    Öksüz satır kırılımda NULL kovasına düşer ve o kolona konan HER filtre onları
    sessizce eler. Kanıtlanmış vaka: `cari_kodu` hem müşteriyi hem tedarikçiyi gösterir;
    `cari_hareketler → musteriler` eklenirse satırların %53'ü öksüz kalır.
    """
    rels, con, tables = rels_and_conn
    sorunlar = []
    for r in rels:
        p = _parse(r)
        if not p:
            continue
        many, src, one, dst = p
        if many not in tables or one not in tables:
            continue
        toplam, eslesen = con.execute(
            f'select count(*), count(*) filter (where o."{dst}" is not null) '
            f'from main.{many} s left join main.{one} o on s."{src}" = o."{dst}"').fetchone()
        if not toplam:
            continue
        oran = (toplam - eslesen) / toplam
        if oran > MAX_ORPHAN_RATE:
            sorunlar.append(
                f"{r['name']}: {many}.{src} satırlarının %{oran*100:.1f}'i {one}.{dst}'de "
                f"karşılık BULAMIYOR ({toplam - eslesen}/{toplam}) → join semantik olarak "
                "yanlış olabilir (polimorfik anahtar? yanlış master tablo?)")
    assert not sorunlar, "ÖKSÜZ SATIR:\n  " + "\n  ".join(sorunlar)


def test_polimorfik_cari_kodu_iliskisi_EKLENMEMIS(rels_and_conn):
    """Bilinçli atlamanın kaydı — biri 'eksik ilişkiyi tamamlamak' isterse burada durur.

    `cari_kodu` polimorfiktir (M#### müşteri, T-### tedarikçi). Tek bir MDL ilişkisi bunu
    ifade edemez. Doğru modelleme: müşteri+tedarikçiyi UNION'layan bir `cari` master view'ı,
    ya da ayrıştırıcı olarak `cari_tip` boyutu (`cari` cube'unda ZATEN var).
    """
    rels, _, _ = rels_and_conn
    yasak = {("cari_hareketler", "musteriler"), ("cari_hareketler", "tedarikciler"),
             ("faturalar", "musteriler"), ("faturalar", "tedarikciler")}
    for r in rels:
        cift = tuple(r.get("models") or [])
        assert cift not in yasak, (
            f"{r['name']}: polimorfik `cari_kodu` üzerinden tek-hedefli ilişki eklenmiş. "
            "Satırların yarısı öksüz kalır; `test_kaynak_satirlari_OKSUZ_KALMIYOR` bunu "
            "zaten yakalar. Doğru çözüm UNION'lı bir cari master view'ı ya da cari_tip."
        )
