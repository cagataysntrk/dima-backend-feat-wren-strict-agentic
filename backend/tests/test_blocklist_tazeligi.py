"""FAZ 1.3c — **KONNEKTÖR BAŞINA BLOCKLIST TAZELİĞİ.**

## Neden bu kapı var — motorun kendi uyarısı

`wren/policy.py` iki ayrı rejim uyguluyor ve **ikisi aynı şey değil**:

* **Kaynak konumu (`FROM`/`JOIN`)** → gerçekten **fail-closed**: `_check_tables`
  bilinmeyen HER TVF'yi reddeder.
* **Kaynak-DIŞI konumlar** (projeksiyon · alt sorgu · iç argüman) → güvenlik sınırı
  **adlandırılmış bir listedir**. Motorun kendi yorumu, birebir:

  > *"you cannot allowlist every scalar function that may appear in a projection or WHERE
  > clause, so for non-source positions this named list is the security boundary: a reader
  > that is **not enumerated** here **will pass** in a projection / subquery / nested-arg
  > position. The list must therefore be **MAINTAINED PER-CONNECTOR**."*

Bir liste *"bakımlı tutulmalıdır"* diyorsa, bakımın **ölçülmesi** gerekir — yoksa cümle bir
niyet beyanı olarak kalır. Bu dosya o ölçümdür.

## 🔴 Kurulduğu gün ölçtüğü şey

**45 adın 0'ı SQL Server okuyucusu** — ve `wren_service.py:143`'ün kendi notu
*"üretimdeki tenant'larımız (gitas, atiksan) tam olarak **mssql**"* diyor. Motorun uyarısı
**ana konnektörümüzde hiç uygulanmamış**.

⚠ **ERİŞİLEBİLİRLİK ABARTILMIYOR.** Bu bir *"sömürülebiliriz"* iddiası **değildir** ve öyle
yazılmaz. SQL Server'ın en tehlikeli okuyucuları ya **kaynak konumundadır**
(`OPENROWSET`/`OPENQUERY`/`OPENDATASOURCE` → `FROM` → **zaten fail-closed**) ya da
`SELECT` bile değildir (`xp_cmdshell`/`sp_OACreate` → `EXEC` → `guard_sql` **zaten**
reddeder). Ölçülen şey **kapsama boşluğudur**, bir açık değil. Boşluğu *"açık"* diye yazmak
da, *"yok"* diye yazmak kadar yanlış olurdu.

## Neden `lab/kapi.py`'ye AYRI bir adım eklenmedi

Yol haritası kontrolü *"`lab/kapi.py`'ye"* diyor. Ama `kapi.py --tam`'ın **birinci adımı
zaten tam süittir** ve bu dosya süitin içinde. Beşinci bir kapı adımı açmak, aynı kuralın
**iki sahibi** olurdu — bu deponun 1 numaralı kusuru. Kontrol istenen yerde koşuyor,
istenen koşucudan.
"""

from __future__ import annotations

import pathlib
import re

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]

#: Ad → konnektör. Motorun listesi düz bir küme; sınıflandırma **burada** yapılır çünkü
#: soru *"bu ad hangi konnektöre ait"* değil, **"bizim kullandığımız konnektör kapsanmış mı"**.
KONNEKTOR_IZLERI: dict[str, tuple[str, ...]] = {
    "duckdb": ("read_csv", "read_parquet", "read_json", "read_ndjson", "read_blob",
               "read_text", "read_xlsx", "sniff_csv", "glob", "parquet_", "delta_scan",
               "iceberg_", "st_read", "url"),
    "postgres": ("pg_", "dblink", "lo_get", "lo_import", "postgres_"),
    "mysql": ("mysql_", "load_file"),
    "sqlite": ("sqlite_",),
    # 🔴 mssql: BİLE BİLE BOŞ. Aşağıdaki muafiyet bunun **kaydıdır**, unutulması değil.
    "mssql": (),
}

#: Kapsamı OLMAYAN ama kullandığımız konnektörler — **gerekçesiyle**.
#: Bir konnektörü buraya yazmak onu *"güvenli"* ilan etmez; **bilinen ve gerekçelendirilmiş**
#: kılar. Gerekçesiz bir boşluk, sessiz bir boşluktur.
MUAFIYETLER: dict[str, str] = {
    "mssql": (
        "SQL Server'ın dosya/uzak okuyucuları ya KAYNAK konumundadır "
        "(`OPENROWSET`/`OPENQUERY`/`OPENDATASOURCE` → `FROM` → `_check_tables` ZATEN "
        "fail-closed) ya da `SELECT` değildir (`xp_cmdshell`/`sp_OACreate` → `EXEC` → "
        "`guard_sql` ZATEN reddeder). Yani kaynak-dışı blocklist'e mssql adı eklemek bugün "
        "ölçülebilir bir şey kapatmıyor. Gerçek sınır 1.1 (`motor_rls`) + 1.3b "
        "(`enforce_query`); bu muafiyet o ikisi indiğinde YENİDEN DEĞERLENDİRİLİR."
    ),
}


def _okuyucu_adlari() -> frozenset[str]:
    try:
        from wren import policy
    except ImportError:                                     # pragma: no cover
        pytest.skip("motor (`wren`) kurulu değil")
    adlar = getattr(policy, "_DATA_READER_NAMES", None)
    assert adlar, (
        "`wren.policy._DATA_READER_NAMES` YOK — motorun iç adı değişmiş olabilir. "
        "Kapı GÜNCELLENMELİ, silinmemeli: bu liste kaynak-dışı konumlarda GÜVENLİK "
        "SINIRIDIR ve ölçülmezse bakımı da ölçülmez.")
    return frozenset(str(a).lower() for a in adlar)


def _kullandigimiz_konnektorler() -> set[str]:
    """Kodun **gerçekten** dallandığı datasource'lar — beyan değil, `if` sayısı.

    ⚠ Liste elle yazılmaz: elle yazılan bir liste, yeni bir konnektör eklendiğinde
    **sessizce** bayatlar ve kapı *"hepsi kapsandı"* der. Kaynak `wren_service.py`'nin
    kendi dallarıdır.
    """
    kaynak = (KOK / "app" / "wren_service.py").read_text(encoding="utf-8")
    bulunan = set(re.findall(r'self\.datasource\s*==\s*["\']([a-z_]+)["\']', kaynak))
    bulunan.add(_varsayilan_datasource())
    return bulunan


def _varsayilan_datasource() -> str:
    kaynak = (KOK / "app" / "config.py").read_text(encoding="utf-8")
    m = re.search(r'datasource:\s*str\s*=\s*["\']([a-z_]+)["\']', kaynak)
    assert m, "`config.py`'de varsayılan datasource okunamadı"
    return m.group(1)


# ── KAPILAR ──────────────────────────────────────────────────────────────────

def test_HER_KULLANDIGIMIZ_KONNEKTOR_KAPSANMIS_ya_da_GEREKCELI_MUAF():
    """🔴 **Motorun *«konnektör başına bakımlı tutulmalı»* uyarısının ÖLÇÜMÜ.**

    Kullandığımız her datasource için ya listede **en az bir** okuyucu adı olmalı, ya da
    `MUAFIYETLER`'de **gerekçesi yazılı** bir kayıt. Üçüncü bir seçenek — *"sessizce
    kapsanmamış"* — bu kapının varlık sebebidir.
    """
    adlar = _okuyucu_adlari()
    eksik: list[str] = []
    for ds in sorted(_kullandigimiz_konnektorler()):
        izler = KONNEKTOR_IZLERI.get(ds)
        if izler is None:
            eksik.append(f"{ds}: KONNEKTOR_IZLERI'nde HİÇ TANIMLI DEĞİL — yeni bir "
                         f"datasource eklendi ve blocklist kapsamı KARARA BAĞLANMADI")
            continue
        kapsanan = sum(1 for a in adlar if any(a.startswith(i) or a == i for i in izler))
        if kapsanan == 0 and ds not in MUAFIYETLER:
            eksik.append(f"{ds}: listede 0 okuyucu ve GEREKÇELİ MUAFİYETİ YOK")
    assert not eksik, (
        "🔴 KONNEKTÖR BAŞINA BLOCKLIST BAKIMI EKSİK:\n  " + "\n  ".join(eksik)
        + "\nMotorun kendi uyarısı: *'The list must be MAINTAINED PER-CONNECTOR.'* "
          "Bir konnektör kapsanmıyorsa bu YAZILIR — sessiz bir boşluk, bilinen bir "
          "boşluktan her zaman kötüdür.")


def test_MUAFIYETLER_GEREKCESIZ_OLAMAZ():
    """Muafiyet bir **karardır**, bir susma değil. Gerekçesiz bir satır, kapıyı kapının
    kendisiyle çürütür — tam olarak 0.21'in muafiyet listesinde kilitlenen disiplin."""
    for ds, gerekce in MUAFIYETLER.items():
        assert len(gerekce) > 120, f"{ds}: muafiyet gerekçesi çok kısa/yok"
        assert "fail-closed" in gerekce or "guard_sql" in gerekce, (
            f"{ds}: gerekçe, riskin NEDEN kapalı olduğunu göstermiyor — "
            "'şimdilik atlıyoruz' bir gerekçe değildir")
        assert "YENİDEN DEĞERLENDİRİLİR" in gerekce or "yeniden değerlendir" in gerekce, (
            f"{ds}: muafiyetin BİTİŞ KOŞULU yok — süresiz bir muafiyet, kalıcı bir boşluktur")


def test_MSSQL_BOSLUGU_OLCULDU_ve_YAZILI():
    """🔴 Kurulduğu gün ölçtüğü somut boşluk **donduruluyor**: 45 adın **0'ı** mssql.

    Bu sayı değişirse (biri mssql okuyucusu eklerse) kapı **kırılır** ve muafiyetin
    gerekçesi güncellenmek zorunda kalır — muafiyetler böyle çürümez.
    """
    adlar = _okuyucu_adlari()
    mssql_izleri = ("openrowset", "opendatasource", "openquery", "xp_", "sp_oa", "bulk")
    kapsanan = sorted(a for a in adlar if any(i in a for i in mssql_izleri))
    assert kapsanan == [], (
        f"mssql okuyucusu artık listede: {kapsanan}. Bu İYİ bir haber — "
        "`KONNEKTOR_IZLERI['mssql']` doldurulmalı ve `MUAFIYETLER['mssql']` SİLİNMELİ.")
    assert "mssql" in MUAFIYETLER, "mssql boşluğu ölçüldü ama gerekçesi yazılı değil"


def test_MIMARI_STRICT_SQL_POLICY_YI_SINIR_DIYE_SATMIYOR():
    """🔴 **1.3c'nin asıl işi bu satır.**

    `strict_sql_policy=on`'u bir güvenlik sınırı gibi yazmak, olmayan bir garantiye
    dayanarak karar aldırır. MIMARI iki yerde *"45 TVF'yi **her AST konumunda** bloklar"*
    diyordu; motorun kendi kaynağı *"kaynak-dışı konumlarda bu bir **blocklist**tir…
    enumerate edilmemiş bir okuyucu **GEÇER**"* diyor. İkisi aynı cümle değil.
    """
    m = (KOK / "MIMARI.md").read_text(encoding="utf-8")
    assert "her AST konumunda" not in m, (
        "MIMARI hâlâ *'her AST konumunda bloklar'* diyor — bu, kaynak-dışı konumlardaki "
        "**blocklist** rejimini **allowlist** gibi gösterir ve olmayan bir garanti satar.")
    assert "MAINTAINED PER-CONNECTOR" in m, \
        "motorun kendi uyarısı MIMARI'ye alıntılanmamış"
    assert "Güvenlik SINIRI olarak yazılmaz/satılmaz" in m or \
           "GÜVENLİK SINIRI sanma" in m, \
        "sınır cümlesi MIMARI'de yok — 1.3c'nin `NE`'si tam olarak bu cümledir"


def test_SINIRIN_UC_BILESENI_ADIYLA_YAZILI():
    """Sınırın **ne olduğu** da yazılmalı, yalnız ne OLMADIĞI değil: `motor_rls` (1.1) +
    `enforce_query` (1.3b) + `denied_functions`. Bir yasağı gerekçesiz bırakmak,
    okuyucuyu *"o hâlde hiçbir şey korumuyor"* sonucuna iter."""
    m = (KOK / "MIMARI.md").read_text(encoding="utf-8")
    for bilesen in ("motor_rls", "enforce_query", "denied_functions"):
        assert bilesen in m, f"sınırın bileşeni MIMARI'de anılmıyor: {bilesen}"
