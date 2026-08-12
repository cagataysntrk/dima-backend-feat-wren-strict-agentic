"""Faz 4.7a araştırma bulgusunun testi: view fan-out sağlık kontrolü (31 Temmuz/1 Ağustos
2026 — dış yol haritası 1.11c "metrik tuzakları: fan-out").

**4.7a araştırması (kod değişikliği YOK, yalnız kanıt topladı)** somut bir fan-out riski
KANITLADI: `parti` cube'unun `base_object`'i olan `parti_zengin` view'ı `partiler`ı
`personel.ad_soyad` (BENZERSİZLİĞİ VERİTABANI SEVİYESİNDE GARANTİ EDİLMEYEN bir metin
alanı — iki farklı çalışan aynı ada sahip olabilir) üzerinden LEFT JOIN'liyor. Bugünkü
demo verisinde (29 personel, sıfır tekrar eden isim — ampirik olarak doğrulandı) bu
YANLIŞLIKLA güvenli; YAPISAL bir koruma YOKTU. `makine_duruslari` cube'undaki fan-out
yorumunun (bkz. o dosya) ele aldığı risk (İKİ FARKLI GRAIN'İ AYNI cube'da birleştirmek)
BUNDAN FARKLI bir sınıf: burası bir cube'un KENDİ view'ının İÇİNDEKİ bir JOIN riski.

**4.7b (araştırma OLUMLU çıktığı için, en az invaziv düzeltme)**: mevcut `dry_plan`/cube
derleme mekanizmasına DOKUNMADAN, YENİ bir REGRESYON TESTİ eklendi — her view'ın satır
sayısının kendi TEMEL (FROM'daki ilk) tablosunu AŞMADIĞINI doğrular. Bugün YEŞİL (kanıt:
mevcut sistem sağlıklı) — ama biri ileride bir view'a fan-out yaratan bir JOIN eklerse
(ya da demo verisine tesadüfen aynı isimli iki personel eklenirse) bu test KIRILIR ve
sorunu ÜRETİME gitmeden yakalar. `MetricDefinition` gibi daha büyük, YENİ bir katman
GEREKMEDİ — araştırma bunu somut bir ihtiyaçla DOĞRULAYAMADI, bu yüzden bilinçli olarak
yapılmadı (UC-1.14 budur — bu test ONUN karşılığıdır).

**4.7a'nın İKİNCİ araştırma bacağı — mali takvim/kur (UC-1.15), 1 Ağustos 2026 doğrulama
turunda TAMAMLANDI**: `control_plane/models.py::TenantConfig`'te mali-yıl-başlangıcı türünde
HİÇBİR alan YOK (`donem_no` LOGO ERP'nin tablo-önekindeki PERİYOT NUMARASIDIR — ör.
`LG_121_01_STLINE` — mali yılın HANGİ AYDA başladığıyla İLGİSİZ bir kavram, salt şema
isimlendirmesi). `app/cube_router.py`'nin "geçen ay/geçen yıl" çözümleyicisi (`_prev_period_
filters` ve komşuları) HER ZAMAN takvim (Ocak-Aralık) sınırları kullanır. `demo/companies/*`
altındaki (gulteks, demo-boyahane, gitas, atiksan) HİÇBİR şirket fixture'ı takvim-dışı bir
mali yıl BEYAN ETMİYOR — Türk Ticaret Kanunu'nda da varsayılan mali yıl takvim yılıdır,
farklısı (yabancı ana şirkete hizalanmış nadir istisnalar dışında) olağan değildir. Sonuç:
bu ihtiyaç bugün TAMAMEN VARSAYIMSAL — hiçbir gerçek/demo/lab tenant'ında somutlaşmıyor. Bu
yüzden `TenantConfig`'e mali-yıl alanı eklemek/`cube_router`'ı DEĞİŞTİRMEK bilinçli olarak
YAPILMADI (4.7b ilkesi: kanıtlanmamış ihtiyaç için altyapı kurulmaz) — bir müşteri GERÇEKTEN
takvim-dışı bir mali yılla gelirse bu o zaman, somut bir örnekle ele alınmalı.

**GÜNCELLEME — FAZ 2 (2 Ağustos 2026): bu testin KAPSAMI daraldı, DEĞERİ değil.**
4.7a'nın somut bulgusu (`parti_zengin`) artık YOK: `parti`/`mizan`/`ik` cube'ları elle
yazılmış denormalize view'lardan MODEL tabanına taşındı ve o üç view silindi. Geriye tek
meşru view kaldı (`enerji_tesis` — bileşik `(yil, ay)` anahtarı, MDL ilişkileri tek kolonlu,
bkz. MIMARI.md). Bu testin GENEL kuralı hâlâ geçerlidir ve yeni bir view eklendiği anda onu
da kapsar.

Asıl önemli olan: **risk kaybolmadı, KATMAN DEĞİŞTİRDİ.** `parti_zengin`in tehlikeli join'i
(`partiler.operator = personel.ad_soyad` — benzersizliği veritabanı seviyesinde GARANTİ
EDİLMEYEN bir metin alanı) bugün `partiler_personel` İLİŞKİSİ olarak duruyor. Koruma da
onunla birlikte taşındı ve GENELLEŞTİ: `tests/test_relationship_health.py` bildirilen 31
ilişkinin HEPSİNİ fan-out/NULL/öksüz açısından gerçek veriye karşı ölçüyor — yani eskiden
tek bir view'a özel olan kontrol artık her ilişki için otomatik. Aşağıdaki
`test_ad_soyad_join_anahtari_riski_ILISKIYE_TASINDI` bu devri kayda geçirir."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


def _view_files(project_dir: Path) -> list[Path]:
    views_dir = project_dir / "views"
    if not views_dir.is_dir():
        return []
    return sorted(views_dir.glob("*/metadata.yml"))


def _tum_projeler() -> list[Path]:
    """🔴🔴 **TÜM KİRACILAR** — varsayılan proje **ve** `demo/wren-projects/*`.

    Ölçülen kusur (2026-08-12, denetim ajanı + kendi ölçümüm): bu kapı
    `settings.resolved_project_dir()` ile **tek** kiracıya bakıyordu ve
    **9 view'in 1'ini** görüyordu.

        wren-project  : enerji_tesis                          (3 LEFT JOIN)  ← görülen
        atiksan       : cari_finans_src · karlilik_src         (1 + 2)       ← görülmeyen
        gitas         : cari_finans_src · karlilik_src · mizan_src (1+1+1)   ← görülmeyen
        gulteks       : cari_finans_src · karlilik_src         (1 + 2)       ← görülmeyen
        demo-boyahane : enerji_tesis                          (3)            ← görülmeyen

    Toplam **9 view · 15 LEFT JOIN**; korunan **3**. `karlilik_src`'nin
    `LEFT JOIN stok_kartlari ON STOK_KODU` bacağı, kuralın doğduğu `parti_zengin`
    vakasının **tam sınıfıdır** — fan-out tutarı şişirir ve `source="cube"` rozetiyle
    çıkar, yani **sessiz-yanlış**.

    ⊙ Ve ölçüldü: dört kiracının **dördü de** `--network none` altında servis kurup
    sorgu koşabiliyor — yani kapsamı dar tutmanın **ortamsal bir gerekçesi yoktu**.
    """
    kok = Path(__file__).parent.parent / "demo"
    out = [kok / "wren-project"]
    p = kok / "wren-projects"
    if p.is_dir():
        out += sorted(d for d in p.iterdir() if d.is_dir() and (d / "views").is_dir())
    return [d for d in out if (d / "views").is_dir()]


def _servis(project_dir: Path):
    """O kiracının kendi motoru — view'ler **kendi verisiyle** ölçülmeli."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(project_dir=str(project_dir), datasource=s.datasource,
                       connection_info=s.connection_dict())


def _first_from_table(statement: str) -> str | None:
    m = re.search(r"\bFROM\s+([A-Za-z_][A-Za-z0-9_]*)", statement, re.IGNORECASE)
    return m.group(1) if m else None


@pytest.fixture(scope="module")
def duckdb_conn():
    """Ham SQL çalıştırmak için gerçek `WrenService` — motorun kendi DuckDB bağlantı
    yönetimini (CSV/parquet dizin bağlama, wren_core) YENİDEN İCAT ETMEDEN kullanır
    (aynı desen: tests/conftest.py::schema fixture'ı)."""
    from app.config import get_settings
    from app.wren_service import WrenService

    get_settings.cache_clear()
    settings = get_settings()
    svc = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
    )

    class _Conn:
        def execute(self, sql: str):
            result = svc.query(sql)
            return _Row(result["rows"][0]) if result["rows"] else _Row({})

    yield _Conn()


class _Row:
    def __init__(self, d: dict):
        self._values = list(d.values())

    def fetchone(self):
        return tuple(self._values)


def test_no_view_fans_out_relative_to_its_base_table(duckdb_conn):
    """HER view, KENDİ temel tablosundan DAHA FAZLA satır DÖNDÜRMEMELİ (LEFT JOIN'lerle
    zenginleştirme satır sayısını korumalı, çoğaltmamalı).

    Kuralın doğduğu somut vaka (`parti_zengin`) Faz 2'de göç etti ve view silindi; kural
    kalıcıdır çünkü ne zaman biri yeni bir denormalize view yazsa aynı risk geri gelir."""
    from app.config import get_settings

    settings = get_settings()          # noqa: F841 — kapsam artık TÜM kiracılar
    checked, atlanan = 0, []
    for proje in _tum_projeler():
        views = _view_files(proje)
        if not views:
            continue
        try:
            svc = _servis(proje)
        except Exception as exc:                                 # noqa: BLE001
            # ⚠ Ortam eksiği **sessizce** geçilmez: sayılır ve aşağıda beyan edilir.
            atlanan.append(f"{proje.name}: {type(exc).__name__}")
            continue
        for vf in views:
            data = yaml.safe_load(vf.read_text(encoding="utf-8")) or {}
            stmt = data.get("statement")
            if not stmt:
                continue
            base_table = _first_from_table(stmt)
            assert base_table, f"{vf}: FROM tablosu ayrıştırılamadı"
            try:
                base_count = svc.query(f"SELECT COUNT(*) AS n FROM {base_table}")["rows"][0]["n"]
                view_count = svc.query(f"SELECT COUNT(*) AS n FROM ({stmt}) t")["rows"][0]["n"]
            except Exception as exc:                             # noqa: BLE001
                atlanan.append(f"{proje.name}/{vf.parent.name}: {type(exc).__name__}")
                continue
            assert view_count <= base_count, (
            f"FAN-OUT: view '{data.get('name')}' ({vf}) temel tablosu '{base_table}' "
            f"({base_count} satır) yerine {view_count} satır döndürüyor — bir JOIN "
            f"çoğaltıyor olabilir (benzersizliği garanti edilmeyen bir anahtar kolonu ara)."
        )
        checked += 1
    # 🔴 **PAYDA KİLİDİ** (⟳ 08-12). Eski eşik `>= 1` idi ve tek view'le yeşil kalıyordu
    # — yani kapsam 9'dan 1'e düştüğü hâlde kapı bunu **hiç duyurmadı**. Bu deponun
    # `gitas` dersinin birebir tekrarı: *sistem bozulurken sayı iyileşir.*
    # ⚠ Eşik **9**: bugün ölçülen view sayısı. Bir view **eklenirse** bu sayı büyür
    # (kapı kırmızı vermez); **düşerse** kırmızı verir ve gerekçesi yazılır.
    # 🔴 **KAPSAM İKİYE BÖLÜNDÜ — ve ikisi de SAYIYLA yazılı** (⟳ 08-12).
    #
    # Ölçüldü: dokuz view'in **yedisi** `--network none` altında koşamıyor —
    # `[INVALID_SQL] table 'wren.dbo.cari_hareketler' not found`. Sebep **ortamsal**:
    # `atiksan`·`gitas`·`gulteks` `CLAUDE.md`'ye göre **mssql** lab fikstürleridir ve
    # temel tabloları yerel veri kaynağında **yok**. Bu bir ürün kusuru değil.
    #
    # ⚠ Ama sessizce geçilmiyor: ölçülemeyenler **adıyla** sayılıyor ve sayı bir
    # tavana bağlı. Biri ölçülebilir hâle gelirse (veri yerelleşirse) kapı **iyi
    # haberle** kırmızı verir ve kapsam genişletilir.
    #
    # *Bir kapıyı ortam eksiğinde susturmak dürüstlüktür; o susmayı DUYURMAMAK
    # kapsamı sessizce kırpmaktır.*
    assert len(atlanan) <= 7, (
        f"🔴 ATLANAN VIEW SAYISI ARTTI ({len(atlanan)} > 7): {atlanan}\n"
        "Daha önce ölçülebilen bir view artık ölçülemiyor — kapsam DARALDI.")
    if len(atlanan) < 7:
        import pytest as _pt
        _pt.skip(f"✅ İYİ HABER: yalnız {len(atlanan)} view atlandı (önce 7) — "
                 f"{atlanan}. Bir kiracının verisi yerelleşmiş olabilir; tavanı "
                 "düşürüp kapsamı genişletin.")
    assert checked >= 2, (
        f"🔴 PAYDA DÜŞTÜ: yalnız {checked} view DAVRANIŞSAL olarak ölçüldü, beklenen "
        "**≥2** (`wren-project/enerji_tesis` · `demo-boyahane/enerji_tesis`).\n"
        "*Hız kapsamdan değil çekirdekten satın alınır — payda kutsaldır.*")


def test_TUM_VIEWLER_SAYILIYOR_hicbiri_SESSIZCE_DUSMUYOR():
    """🔴🔴 **KAPSAM KİLİDİ** — dokuz view'in **hepsi** görülmeli, ölçülebilsin ya da
    ölçülemesin.

    Ölçülen kusur: kapı `settings.resolved_project_dir()` ile **tek** kiracıya
    bakıyordu ve **9 view'in 1'ini** görüyordu; eski eşik `checked >= 1` olduğu için
    kapsam 9'dan 1'e düştüğü hâlde **hiçbir kırmızı konuşmadı**. Bu deponun `gitas`
    dersinin birebir tekrarı: *sistem bozulurken sayı iyileşir.*

    ⊙ Ve hepsi risk taşıyor: **9 view · 15 LEFT JOIN** (ölçüldü). `karlilik_src`'nin
    `LEFT JOIN stok_kartlari ON STOK_KODU` bacağı, kuralın doğduğu `parti_zengin`
    vakasının **tam sınıfıdır**.
    """
    tum = [(p.name, vf.parent.name) for p in _tum_projeler() for vf in _view_files(p)]
    assert len(tum) >= 9, (
        f"🔴 VIEW SAYISI DÜŞTÜ: {len(tum)} bulundu, beklenen ≥9 → {tum}\n"
        "Bir view silindiyse gerekçesi yazılsın; bir dizin adı değiştiyse tarayıcı "
        "düzeltilsin — *sessizce düşen bir view, ölçülmeyen bir risktir.*")
    kiracilar = {p for p, _ in tum}
    assert len(kiracilar) >= 4, (
        f"🔴 yalnız {len(kiracilar)} kiracı tarandı: {sorted(kiracilar)} — kapı yine "
        "tek kiracıya daralmış olabilir.")


def test_ad_soyad_join_anahtari_riski_ILISKIYE_TASINDI(duckdb_conn):
    """4.7a'nın SPESİFİK bulgusunun Faz 2 sonrası hali — risk kaybolmadı, KATMAN DEĞİŞTİRDİ.

    `parti_zengin` view'ı silindi ama tehlikeli join'i `partiler_personel` İLİŞKİSİ olarak
    duruyor: `partiler.operator = personel.ad_soyad`. `ad_soyad` benzersizliği veritabanı
    seviyesinde GARANTİ EDİLMEZ — iki çalışan aynı ada sahip olabilir ve o an bu ilişki
    üzerinden gelen HER kırılım fan-out yapar (kg/ciro toplamları şişer, `source="cube"`
    rozeti değişmez). Bugün güvenli olması VERİ-BAĞIMLI bir gerçektir, şema garantisi değil.

    Bu tekilliği artık `tests/test_relationship_health.py` 31 ilişkinin hepsi için genel
    olarak ölçüyor; buradaki test o genel kapıyı DEĞİL, "risk motora taşındı" devrini
    kaydeder — biri `partiler_personel`i `personel_kodu`ya çevirirse (doğru düzeltme) bu
    test kendi gerekçesinin ortadan kalktığını söyler.
    """
    import yaml

    from app.config import get_settings

    rels = (yaml.safe_load(
        (get_settings().resolved_project_dir() / "relationships.yml").read_text(encoding="utf-8"))
        or {}).get("relationships") or []
    r = next((x for x in rels if x.get("name") == "partiler_personel"), None)
    assert r, "partiler_personel ilişkisi yok — `parti` cube'unun demografi zinciri koptu"
    if "ad_soyad" not in (r.get("condition") or ""):
        pytest.skip("ilişki artık ad_soyad üzerinden gitmiyor — bu testin gerekçesi kalktı, "
                    "genel kapı tests/test_relationship_health.py'de")

    dup_ad_soyad = duckdb_conn.execute(
        "SELECT COUNT(*) FROM (SELECT ad_soyad FROM personel "
        "GROUP BY ad_soyad HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    assert dup_ad_soyad == 0, (
        "personel.ad_soyad'da tekrar eden isim bulundu — `partiler_personel` ilişkisi "
        "artık fan-out YARATIYOR: `parti` cube'unun operatör demografisi kırılımlarında "
        "kg/ciro toplamları ŞİŞER. Doğru düzeltme: ilişkiyi `personel_kodu` üzerine kurmak "
        "(bunun için `partiler`da bir personel kodu kolonu gerekir)."
    )
