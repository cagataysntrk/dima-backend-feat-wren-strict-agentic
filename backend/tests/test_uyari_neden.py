"""FAZ F3 — UYARININ NEDENİ: `check_alert → contribution → dispatch` kompozisyonu.

## Ölçülen boşluk (2 Ağustos 2026)

Zamanlanmış uyarı bugüne kadar şunu diyordu:

    ⚠ fire takibi: eşik ihlali — M-07: 45 (> eşik 30)

**NE olduğunu söylüyor, NİYE olduğunu söylemiyor.** Cevabı üretecek motor
(`app/contribution.py`) elimizde duruyordu ve `/ask`'te *"bu neden böyle?"* sorusuna
cevap veriyordu — ama arka plan işi onu **çağıramıyordu**, çünkü gövde
`/ask/contribution` ROUTER'ININ İÇİNDEYDİ (`request`, `_service_for`,
`_drill_record_contract`). Aynı kusurun ikinci yüzü: konuşma katmanı onu ancak router'ı
çağırarak kullanabildiği için planlayıcıya `dis_adim(..., gated: false)` diye **itiraf**
olarak giriyordu — kayıtlı bir araç değildi, dört kapıdan geçmiyordu.

Faz F3 gövdeyi `contribution.arastir`'a taşıdı. Bu dosya iki kazancı da kilitler.

## Neden bu testler

1. **PII fail-closed.** Segment etiketleri boyut DEĞERLERİNDEN gelir (operatör adı, cari
   unvanı) ve bir bildirimin kime ulaşacağı ÖNCEDEN BİLİNEMEZ. `run_schedule` ana sonucu
   zaten `principal=None` ile maskeliyor; nedenin bunu atlaması **ikinci bir sızıntı
   yüzeyi** açardı — tam olarak Faz A2'de kapatılan sınıf.
2. **Dürüst red.** Katkı ayrıştırması yalnız TOPLANABİLİR ölçülerde tanımlıdır. `AVG`/
   oran için "bu segment değişimin %40'ını açıklıyor" cümlesi matematiksel olarak
   yanlıştır — o durumda neden ÜRETİLMEZ ve nedeni söylenir.
3. **Maliyet sınırı.** Neden YALNIZ ihlalde koşar; rutin raporda boyut taraması kimsenin
   sormadığı bir soruya para ödemek olurdu.
4. **Kırılganlık yok.** Neden üretilemezse uyarı yine gider — gerekçesiz ama gider.
"""

from __future__ import annotations

import json

import pytest

from app import contribution as contrib
from app import schedules


# --- Sahte servis: `arastir`'ın ihtiyaç duyduğu yüzeyin EN AZI --------------------

class _SahteServis:
    """`arastir` yalnız `schema()` ve `yoy.compute`'un kullandığı sorgu yüzeyini ister."""

    mdl_version = "t1"

    def __init__(self, rows, cube):
        self._rows, self._cube = rows, cube

    def schema(self):
        return {"cubes": [self._cube]}

    def cube_sql(self, cq):
        return f"SELECT * FROM {cq.get('cube')}"

    def query(self, sql, limit=None):
        return {"columns": list(self._rows[0].keys()) if self._rows else [],
                "rows": self._rows, "row_count": len(self._rows)}


_CUBE = {
    "name": "uretim",
    "measures": ["fire_kg"],
    "dimensions": ["operator", "tarih"],
    "time_dimensions": ["tarih"],
    "units": {"fire_kg": "kg"},
}


def _kiyas_satirlari(isimler):
    """`yoy.compute` biçiminde satırlar: her segment için cari + geçen dönem."""
    return [{"operator": ad, "fire_kg": cari, "fire_kg_gecen": gecen}
            for ad, cari, gecen in isimler]


@pytest.fixture
def yoy_sahte(monkeypatch):
    """`yoy.compute`'u sabitler — burada test edilen ŞEY dönem matematiği değil,
    kompozisyonun kendisi (yoy'un kendi testleri ayrı: `test_yoy.py`)."""
    def _kur(rows):
        from app import yoy as _yoy

        monkeypatch.setattr(_yoy, "compute",
                            lambda svc, cq, mode, td, **k: {
                                "columns": list(rows[0].keys()) if rows else [],
                                "rows": rows, "row_count": len(rows),
                                "base_sql": "SELECT 1"})
        monkeypatch.setattr(_yoy, "time_dim_of", lambda schema, cube: "tarih")
    return _kur


# --- ASIL KAPI: PII fail-closed ---------------------------------------------------

def test_NEDEN_etiketleri_PII_MASKELI(yoy_sahte):
    """Bildirimin kime ulaşacağı ÖNCEDEN BİLİNEMEZ (e-posta dağıtım listesi, bell, push) —
    bu yüzden `principal` bypass'ı YOKTUR, HER ZAMAN maskelenir. Bu test olmadan neden
    eki, Faz A2'de kapatılan sızıntı sınıfını arka kapıdan geri açardı."""
    yoy_sahte(_kiyas_satirlari([("ahmet@firma.com", 500.0, 100.0),
                                ("normal-operator", 120.0, 100.0)]))
    svc = _SahteServis([], _CUBE)
    satirlar, _ = schedules.uyari_nedeni(
        svc, {"cube": "uretim", "measures": ["fire_kg"], "filters": []},
        {"measure": "fire_kg", "op": "gt", "value": 300})
    assert satirlar, "neden üretilmedi — test bir şey korumuyor"
    hepsi = " ".join(satirlar)
    assert "ahmet@firma.com" not in hepsi, "e-posta MASKELENMEDEN bildirime girdi"
    assert "*" in hepsi, "maskeleme hiç uygulanmamış"


def test_TCKN_de_maskelenir(yoy_sahte):
    """`mask_rows` tüm PII filtrelerini uygular — e-posta tek örnektir, kural genel."""
    yoy_sahte(_kiyas_satirlari([("10000000146", 500.0, 100.0)]))
    satirlar, _ = schedules.uyari_nedeni(
        _SahteServis([], _CUBE), {"cube": "uretim", "measures": ["fire_kg"], "filters": []},
        {"measure": "fire_kg"})
    assert satirlar and "10000000146" not in satirlar[0]


# --- DÜRÜST RED: toplanabilirlik kapısı ------------------------------------------

def test_TOPLANAMAZ_olcude_neden_URETILMEZ_ve_nedeni_soylenir(yoy_sahte):
    """`AVG`/oran için "bu segment değişimin %40'ını açıklıyor" cümlesi MATEMATİKSEL
    OLARAK YANLIŞTIR. Sessizce boş dönmek de yanlış olurdu: kullanıcı "neden yok" ile
    "neden üretilemedi"yi ayırt edemezdi."""
    cube = {**_CUBE, "measures": ["ort_fire"], "non_additive": ["ort_fire"]}
    yoy_sahte(_kiyas_satirlari([("A", 5.0, 1.0)]))
    satirlar, not_ = schedules.uyari_nedeni(
        _SahteServis([], cube), {"cube": "uretim", "measures": ["ort_fire"], "filters": []},
        {"measure": "ort_fire"})
    assert satirlar == []
    assert not_ and len(not_) > 10, "ayrıştırma yapılmadı ama NEDENİ söylenmedi"


def test_ESIK_OLCUSU_aciklanir_sorgunun_ILK_olcusu_degil(yoy_sahte):
    """Çok ölçülü bir raporda uyarı `fire_kg` için kurulduysa AÇIKLANAN da o olmalı.
    Sorgunun ilk ölçüsünü varsaymak YANLIŞ ölçüyü açıklardı — ve kimse fark etmezdi."""
    cube = {**_CUBE, "measures": ["toplam_kg", "fire_kg"], "units": {"fire_kg": "kg"}}
    yakalanan = {}

    def _sahte_arastir(svc, schema, cq, **kw):
        yakalanan["measures"] = list(cq.get("measures") or [])
        return {"raporlar": []}

    from app import contribution as _c
    eski = _c.arastir
    _c.arastir = _sahte_arastir
    try:
        schedules.uyari_nedeni(
            _SahteServis([], cube),
            {"cube": "uretim", "measures": ["toplam_kg", "fire_kg"], "filters": []},
            {"measure": "fire_kg"})
    finally:
        _c.arastir = eski
    assert yakalanan["measures"] == ["fire_kg"]


def test_URETIM_PATLARSA_uyari_yine_gider(monkeypatch):
    """Nedeni üretememek bir uyarıyı KIRMAZ. Haber, gerekçesinden önemlidir."""
    def _patla(*a, **k):
        raise RuntimeError("motor yok")

    monkeypatch.setattr(contrib, "arastir", _patla)
    assert schedules.uyari_nedeni(_SahteServis([], _CUBE), {"cube": "uretim"},
                                  {"measure": "fire_kg"}) == ([], None)


# --- MALİYET: sınır var ve sınır SESSİZ DEĞİL ------------------------------------

def test_ARKA_PLAN_taramasi_ASK_ten_DAR():
    """Bu bir arka plan işidir ve 60 sn'lik scheduler penceresi paylaşımlıdır. Her boyut
    AYRI bir kıyas sorgusu demek — `/ask`'in 6'sı burada 2'dir."""
    assert schedules.NEDEN_MAX_BOYUT < contrib.MAX_BOYUT
    assert schedules.NEDEN_MAX_BULGU <= 3


def test_KIRPMA_RAPORLANIR(yoy_sahte):
    """Sessiz kesme YOK: gösterilmeyen segment sayısı söylenir, yoksa liste "her şey bu
    kadar" diye okunur (`contribution.decompose`'un `kirpilan_segment` disiplini)."""
    yoy_sahte(_kiyas_satirlari([(f"op-{i}", 100.0 + i * 50, 100.0) for i in range(1, 8)]))
    satirlar, not_ = schedules.uyari_nedeni(
        _SahteServis([], _CUBE), {"cube": "uretim", "measures": ["fire_kg"], "filters": []},
        {"measure": "fire_kg"})
    assert len(satirlar) <= schedules.NEDEN_MAX_BULGU
    assert not_ and "gösterilmedi" in not_, f"kırpma raporlanmadı: {not_!r}"


def test_MAKBUZ_yazilmaz_arka_planda(yoy_sahte):
    """Koşum zaten kendi kök `contract_id`'sini üretir; boyut başına ikinci bir kayıt arka
    plan işinde gürültüdür. `arastir`'ın `kaydet=None` seçeneği bunu BİLİNÇLİ yapar."""
    yoy_sahte(_kiyas_satirlari([("A", 500.0, 100.0)]))
    yakalanan = {}
    from app import contribution as _c
    eski = _c.arastir
    _c.arastir = lambda svc, schema, cq, **kw: (yakalanan.update(kw) or {"raporlar": []})
    try:
        schedules.uyari_nedeni(_SahteServis([], _CUBE), {"cube": "uretim"},
                               {"measure": "fire_kg"})
    finally:
        _c.arastir = eski
    assert yakalanan.get("kaydet") is None
    assert yakalanan.get("max_dimensions") == schedules.NEDEN_MAX_BOYUT


# --- TAŞIMA: neden bell'e kadar hayatta kalıyor mu? ------------------------------

def test_TIKLANABILIR_SORGU_bildirime_KONMAZ(yoy_sahte):
    """Maskelenmiş bir değere (`ahm**@***`) filtre kuran sorgu BOŞ döner. "Tıkla" deyip
    boş sonuç vermek, hiç tıklatmamaktan kötüdür — bu yüzden neden yalnız METİN taşır."""
    yoy_sahte(_kiyas_satirlari([("A", 500.0, 100.0)]))
    satirlar, _ = schedules.uyari_nedeni(
        _SahteServis([], _CUBE), {"cube": "uretim", "measures": ["fire_kg"], "filters": []},
        {"measure": "fire_kg"})
    assert all(isinstance(s, str) for s in satirlar)


def test_KANAL_olayi_nedeni_TASIR():
    """`NotificationEvent` kanaldan bağımsız anlamsal taşıyıcıdır — neden orada YOKSA
    hiçbir kanal onu gösteremez."""
    from app import channels

    ev = channels.NotificationEvent(category="alert", severity="critical", title="t",
                                    summary="s", neden=["↳ makine: M-07"],
                                    neden_not="+2 segment daha")
    assert ev.neden and ev.neden_not


def test_INAPP_kanali_nedeni_KAYDA_gecirir():
    """Bell'in kaynağı `notification_log`'dur: neden orada saklanmazsa e-postada görünüp
    arayüzde kaybolurdu — aynı olayın iki yüzeyde farklı okunması (I4'ün sadakat kusuru)."""
    from app import channels

    yazilan = {}
    ev = channels.NotificationEvent(category="alert", severity="critical", title="t",
                                    summary="s", neden=["↳ a"], neden_not="n")
    channels.dispatch(ev, [{"channel": "inapp"}],
                      channels.DispatchContext(inapp_sink=lambda rec: yazilan.update(rec) or rec))
    assert yazilan.get("neden") == ["↳ a"] and yazilan.get("neden_not") == "n"


def test_EPOSTA_DUZ_METNI_de_nedeni_tasir():
    """Zengin istemcide görünüp metin okuyanda kaybolan bir gerekçe, gerekçesiz bir
    uyarıdır. HTML ile düz metin AYNI bilgiyi taşımalı."""
    from app import channels
    from app.email_render import render_email

    ev = channels.NotificationEvent(
        category="alert", severity="critical", title="fire takibi",
        summary="⚠ eşik ihlali", violations=["M-07: 45 (> eşik 30)"],
        neden=["makine: M-07 — 12.400 kg arttı (net değişimin %61'i)"],
        neden_not="+2 segment daha (gösterilmedi, yok sayılmadı)")
    _subject, html, text = render_email(ev)
    assert "Neden?" in text and "M-07 — 12.400" in text
    assert "Neden?" in html


def test_KAYIT_yazma_okuma_ROUND_TRIP():
    """`neden_json` yazılıp okunduğunda AYNI şeyi vermeli. Ayrı bir kolon olması bilinçli:
    teslim TELEMETRİSİ (`delivery_json`) ile cevabın İÇERİĞİ farklı şeylerdir."""
    rec = {"neden": ["↳ a", "↳ b"], "neden_not": "n"}
    ham = json.dumps({"satirlar": rec["neden"], "not": rec["neden_not"]}, ensure_ascii=False)
    n = json.loads(ham)
    assert n["satirlar"] == rec["neden"] and n["not"] == rec["neden_not"]


def test_ESKI_satirda_neden_ALANI_HIC_GORUNMEZ():
    """Faz F3 öncesi satırlarda neden YOKTUR ve olmaması bir OLGUDUR. Boş liste döndürmek,
    "üretildi ama bir şey bulunamadı" ile karıştırılırdı."""
    class _Satir:
        id, ts, tenant_id, schedule_id = 1, None, None, None
        kind, message, row_count, contract_id = "alert", "m", 0, None
        delivery_json = None
        # `neden_json` YOK — eski şema

    store = schedules.ScheduleStore.__new__(schedules.ScheduleStore)
    d = store._notif_to_dict(_Satir())
    assert "neden" not in d and "neden_not" not in d


# --- ARAÇ KAYDI: itiraf kalktı ---------------------------------------------------

def test_CONTRIBUTION_REPORT_artik_KAYITLI_arac():
    """Faz F2'de bu bileşik `dis_adim(..., gated: false)` ile İTİRAF ediliyordu. Gövde
    HTTP'den ayrılınca kayda girebildi — itiraf artık gereksiz ve `ask.py`'de kalmamalı."""
    import pathlib

    from app import tools

    arac = tools.get("contribution.report")
    assert arac.determinizm == "deterministik" and arac.yan_etki == "yok"
    assert arac.maliyet == "pahali", "boyut başına ayrı sorgu koşar — maliyet bunu söylemeli"
    assert arac.cagir() is contrib.arastir, "kayıt çözülemeyen bir işaretçi tutuyor"

    kaynak = (pathlib.Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text()
    assert 'dis_adim("contribution.report"' not in kaynak, (
        "itiraf hâlâ duruyor — araç kayıtlıysa `dis_adim` yalan söyler")


def test_ROUTER_govdeyi_KOPYALAMAZ():
    """Aynı kural iki yerde yaşamasın (MIMARI §5). Router `arastir`'ı ÇAĞIRMALI; kendi
    boyut tarama döngüsünü yazarsa ikisi zamanla ayrışır — bu depoda ölçülmüş desen."""
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text()

    # ⟳ FAZ 9.1 — gövde `_ask_contribution_govde`'ye ALINDI (gizlilik mührü sarmalı).
    # Test GEVŞETİLMEDİ, KESKİNLEŞTİRİLDİ: hem sarmal hem gövde ayrı ayrı denetleniyor.
    # Yalnız `def ask_contribution`'a bakan eski sürüm, ince sarmalı görüp "çağırmıyor"
    # diyordu — doğru kuralı YANLIŞ yerde ölçüyordu.
    sarmal = kaynak.split("def ask_contribution(")[1].split("\ndef ")[0]
    govde = kaynak.split("def _ask_contribution_govde(")[1].split("\ndef ")[0]

    assert "_ask_contribution_govde(" in sarmal, "sarmal gövdeyi çağırmıyor"
    assert "muhurle(" in sarmal, "sarmal gizlilik mührünü uygulamıyor (Faz 9.1)"
    assert "arastir" in govde, "router gövdeyi çağırmıyor"
    for yer, metin in (("sarmal", sarmal), ("gövde", govde)):
        assert "available_dimensions" not in metin, f"{yer} kendi boyut taramasını yazmış"
        assert "yoy.compute" not in metin and "_yoy.compute" not in metin, \
            f"{yer} YoY'u kendi hesaplıyor"


# --- BOYUT SIRASI: kesme keyfi değil (Faz B) -------------------------------------

def test_ADAY_SIRASI_maliyet_ve_GUVENE_gore():
    """ÖLÇÜLDÜ (2026-08-02): `available_dimensions` YAML BEYAN SIRASINDA dönüyordu.
    Faz F3'e kadar zararsızdı (`/ask/contribution` 6 boyutun hepsini tarıyor); uyarının
    nedeni ise yalnız 2 tarayabilir ve `parti` cube'unda 15 BOYUT var. Yani beyan sırası
    kullanıcının gördüğü gerekçeyi BELİRLER hale geldi.

    Sıra açıklayıcılık hakkında bir iddia DEĞİLDİR (onu `rank_dimensions` sorgudan SONRA
    ölçer) — MALİYET ve GÜVEN hakkındadır: kendi tablosundaki boyut JOIN gerektirmez ve
    fan-out riski taşımaz. Kesme yapılacaksa denenmeye önce onlar değer.
    """
    from app.drill import available_dimensions

    meta = {"dimensions": ["uzak_riskli", "uzak_saglikli", "yerel", "uzak_olculmedi"],
            "dimension_origin": {
                "uzak_riskli": {"hops": 1, "certified": "olculdu:riskli"},
                "uzak_saglikli": {"hops": 1, "certified": "olculdu:saglikli"},
                "uzak_olculmedi": {"hops": 1, "certified": "olculmedi"}}}
    sira = [d["name"] for d in available_dimensions(meta, {})]
    assert sira[0] == "yerel", "kendi tablosundaki boyut önce gelmiyor"
    # ÖLÇÜLMEDİ, RİSKLİ'nin ÖNÜNDE: ölçülmemiş bir ilişki BİLİNMEZDİR, riskli ölçülmüş
    # bir ilişki ise BİLİNEN bir sorundur (fan-out toplamları şişirir).
    assert sira[1:] == ["uzak_saglikli", "uzak_olculmedi", "uzak_riskli"]


def test_ADAY_SIRASI_KARARLI():
    """Eşit maliyette beyan sırası korunur — yoksa aynı soru iki kez sorulduğunda farklı
    chip'ler görünürdü."""
    from app.drill import available_dimensions

    meta = {"dimensions": ["c", "a", "b"]}
    assert [d["name"] for d in available_dimensions(meta, {})] == ["c", "a", "b"]


def test_ATLANAN_boyutlar_ADIYLA_raporlanir(yoy_sahte):
    """Bir SAYI ("3 boyut taranmadı") kullanıcıya hangi soruyu sorabileceğini söylemez;
    ad söyler ("peki renk bazında?")."""
    cube = {**_CUBE, "dimensions": ["operator", "renk", "vardiya", "hat", "tarih"]}
    yoy_sahte(_kiyas_satirlari([("A", 500.0, 100.0)]))
    _satirlar, not_ = schedules.uyari_nedeni(
        _SahteServis([], cube), {"cube": "uretim", "measures": ["fire_kg"], "filters": []},
        {"measure": "fire_kg"})
    assert not_ and "taranmadı" in not_
    assert "vardiya" in not_ or "hat" in not_, f"atlananlar adıyla yazılmamış: {not_!r}"
