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

import pytest
import yaml

from app import fanout

# Öksüz oranı için üst sınır. 0'da tutuluyor: bugün ölçülen değer bu ve gevşetmek,
# testin yakalamak için var olduğu sınıfı (polimorfik/yanlış join) görünmez kılar.
MAX_ORPHAN_RATE = 0.0



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


# Ayrıştırma ve ÖLÇÜM `app/fanout.py`'de (Faz D2). Test kendi SQL'ini yazmaz — sertifikayı
# üreten kodun AYNISINI çağırır. Aksi halde aynı kural iki yerde yaşardı; bu depoda o desen
# defalarca ölçüldü ve her seferinde sapmayla sonuçlandı (drill↔schedules z-skoru,
# interpret↔schedules sayı biçimi).
_parse = fanout.ayristir


def test_her_iliski_ayristirilabiliyor(rels_and_conn):
    rels, _, _ = rels_and_conn
    assert rels, "relationships.yml boş"
    bozuk = [r["name"] for r in rels if _parse(r) is None]
    assert not bozuk, f"condition ayrıştırılamadı (bileşik/karmaşık join?): {bozuk}"


@pytest.fixture(scope="module")
def sertifika(rels_and_conn):
    """ÖLÇÜMÜN TEK KAYNAĞI (Faz D2) — build artefaktını üreten fonksiyonun aynısı."""
    rels, con, tables = rels_and_conn
    return fanout.certify(rels, fanout.duckdb_sorgu(con), tablolar=tables)


def test_hedef_anahtari_BENZERSIZ_ve_NULLSUZ(sertifika):
    """FAN-OUT KAPISI. Motor `join_type`'ı okumaz — tek gerçek koruma budur."""
    sorunlar = []
    for ad, k in sertifika["relationships"].items():
        if k.get("durum") != "olculdu":
            continue
        if not k["benzersiz"]:
            sorunlar.append(f"{ad}: {k['bir']}.{k['bir_kolon']} BENZERSİZ DEĞİL "
                            f"({k['bir_satir']} satır / {k['bir_farkli']} farklı) → join "
                            "satırları çoğaltır, SUM'lar şişer")
        if k["bir_null"]:
            sorunlar.append(f"{ad}: {k['bir']}.{k['bir_kolon']} {k['bir_null']} NULL içeriyor")
    assert not sorunlar, "FAN-OUT RİSKİ:\n  " + "\n  ".join(sorunlar)


def test_kaynak_satirlari_OKSUZ_KALMIYOR(sertifika):
    """ÖKSÜZ KAPISI — polimorfik/yanlış join'i yakalar.

    Öksüz satır kırılımda NULL kovasına düşer ve o kolona konan HER filtre onları
    sessizce eler. Kanıtlanmış vaka: `cari_kodu` hem müşteriyi hem tedarikçiyi gösterir;
    `cari_hareketler → musteriler` eklenirse satırların %53'ü öksüz kalır.
    """
    sorunlar = []
    for ad, k in sertifika["relationships"].items():
        if k.get("durum") != "olculdu" or not k["cok_satir"]:
            continue
        if k["oksuz_oran"] > MAX_ORPHAN_RATE:
            eksik = k["cok_satir"] - k["cok_eslesen"]
            sorunlar.append(
                f"{ad}: {k['cok']}.{k['cok_kolon']} satırlarının %{k['oksuz_oran']*100:.1f}'i "
                f"{k['bir']}.{k['bir_kolon']}'de karşılık BULAMIYOR ({eksik}/{k['cok_satir']}) "
                "→ join semantik olarak yanlış olabilir (polimorfik anahtar? yanlış master "
                "tablo?)")
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


def test_uretilen_boyutlar_AYIRT_EDICI_olmali(rels_and_conn):
    """İlişki-türevi bir boyut, veride EN AZ İKİ farklı değer taşımalı.

    Kardinalitesi 1 olan bir boyut hiçbir şeyi ayırt etmez: kırılım tek satır döner,
    kullanıcıya bilgi katmaz — ama sinonimleri router'ın arama uzayına GİRER ve başka
    boyutlarla çakışma yüzeyini büyütür. Yani net etkisi NEGATİFTİR.

    Ölçülmüş vaka (2 Ağustos 2026): `partiler → tedarikciler` üzerinden `sehir`/`tur`
    yayımlandı; bu veri setinde TÜM partiler Çorlu'daki tedarikçilere ait olduğu için
    her iki kırılım da TEK SATIR döndürdü. Üretilen SQL doğruydu (ham SQL ile birebir
    aynı) — sorun doğrulukta değil, YARARDAYDI. `expose:` geri çekildi.

    Cube'un kendi rehberi de aynı yöne bakar: *"Smaller, focused views are easier to
    navigate and lead to better AI results."* Boyut eklemek bedava değildir.
    """
    import yaml

    from app.config import get_settings

    proje = get_settings().resolved_project_dir()
    _, con, tables = rels_and_conn
    zayif = []
    for cd in sorted((proje / "cubes").iterdir()):
        f = cd / "metadata.yml"
        if not f.is_file():
            continue
        cm = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        base = cm.get("base_object")
        if base not in tables:
            continue  # view tabanlı cube'lar bu taramanın dışında
        for d in cm.get("dimensions") or []:
            origin = (d.get("properties") or {}).get("origin")
            if not origin:
                continue  # yalnız ÜRETİLEN boyutlar
            n = con.execute(
                f'select count(distinct o."{origin["column"]}") '
                f'from main.{base} s left join main.{origin["model"]} o '
                f'on s."{_join_col(rels_and_conn, origin["relationship"], base)}" '
                f'= o."{_hedef_col(rels_and_conn, origin["relationship"])}"').fetchone()[0]
            if n < 2:
                zayif.append(f"{cm.get('name')}.{d['name']}: veride {n} farklı değer "
                             f"({origin['model']}.{origin['column']}) — ayırt edici değil")
    assert not zayif, "AYIRT EDİCİ OLMAYAN ÜRETİLEN BOYUT:\n  " + "\n  ".join(zayif)


def _join_col(rels_and_conn, rel_adi: str, kaynak: str) -> str:
    rels, _, _ = rels_and_conn
    r = next(x for x in rels if x["name"] == rel_adi)
    many, src, _, _ = _parse(r)
    return src


def _hedef_col(rels_and_conn, rel_adi: str) -> str:
    rels, _, _ = rels_and_conn
    r = next(x for x in rels if x["name"] == rel_adi)
    _, _, _, dst = _parse(r)
    return dst
