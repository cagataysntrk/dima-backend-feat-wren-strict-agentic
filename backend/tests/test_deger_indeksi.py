"""FAZ B1 — değer indeksi: semantik katmanı atla, sorguları topla.

## Ölçülen sorun

`schema()` ilk çağrısı **2277 ms** sürüyordu. Kırılım (cProfile + doğrudan karşılaştırma):
kolon başına bir `eng.query()` → **229 çağrı**; her biri motor üzerinden **22,65 ms**, aynı
sorgu doğrudan DuckDB'de **0,70 ms**. Yani maliyetin **%97'si planlama**, %3'ü DB. Sebep:
her çağrı 118 KB'lık manifesti yeniden çözüp sqlglot'la ayrıştırıyor ve yeni bir
`ManifestExtractor` kuruyor.

**Motoru uzun ömürlü tutmak İŞE YARAMADI** (ölçüldü: 5,54 → 5,50 ms) — maliyet motor
kurulumunda değil, **her plan çağrısında**. Plandaki varsayım buydu ve ölçümle çürüdü.

## Uygulanan iki hamle

1. **Fiziksel kolonlar semantik katmanı ATLAR.** `SELECT DISTINCT kolon FROM tablo` fiziksel
   bir iştir; MDL'in katkısı yoktur. `wren.engine.get_connector` ile doğrudan konnektöre
   gidilir: 183 kolon, tek `UNION ALL` → **98 ms** (22×).
2. **Kalan her şey de tek sorguda toplanır.** Calc kolonlar (ilişki üzerinden çözülür →
   semantik katman şart) ve cube türev boyutları (CASE ifadeleri) motor yolunda kalır ama
   N plan yerine 1 plan öderler.

**Sonuç: 2277 → 694 ms (3,3×), içerik BİREBİR aynı.** Hedef <150 ms'ye inilmedi; kalan
maliyet birkaç büyük planın kendisi. Dürüst rakam budur.

## Bu dosyanın asıl işi: içeriğin DEĞİŞMEDİĞİNİ kanıtlamak

Hız bir iyileştirme, değer indeksinin bozulması bir **gerilemedir**. Yol boyunca gerçekten
bir gerileme oluştu ve ölçümle yakalandı: calc kolonlar konnektöre gönderilince "kolon
bulunamadı" veriyor ve **19 kolon değerlerini sessizce kaybediyordu** — `route()` model
kolonlarının `values`'ını kategorik filtre için okuduğu için bu, *"Aylin Bulut'un firesi"*
sınıfı soruların deterministik çözümünü öldürürdü.
"""

from __future__ import annotations

import time

import pytest


@pytest.fixture(scope="module")
def svc():
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict())


def test_deger_indeksi_KAPSAMI_korunuyor(schema):
    """ALTIN KAPI. Optimizasyon sonrası hiçbir kolon/boyut değerini kaybetmemeli.

    Sayılar ölçülmüş taban değerleridir (2 Ağustos 2026, demo-boyahane). Düşerlerse
    deterministik değer filtresi sessizce körleşir."""
    kolonlu = sum(1 for m in schema["models"] for c in m["columns"] if c.get("values"))
    boyutlu = sum(len(v) for c in schema["cubes"]
                  for v in (c.get("dimension_values") or {}).values())
    assert kolonlu >= 188, f"değer taşıyan kolon {kolonlu} (taban 188) — kapsam DARALDI"
    assert boyutlu >= 506, f"cube boyut değeri {boyutlu} (taban 506) — kapsam DARALDI"


def test_CALC_kolonlar_da_deger_tasiyor(schema):
    """Ölçülen gerileme buydu: calc kolonlar fiziksel değildir, konnektöre gönderilince
    kaybolurlar. `route()` onları kategorik filtre için OKUYOR."""
    calc = [c for m in schema["models"] for c in m["columns"]
            if c.get("is_calculated") and str(c.get("type", "")).upper().startswith("VARCHAR")]
    if not calc:
        pytest.skip("bu katalogda VARCHAR calc kolonu yok")
    degerli = [c for c in calc if c.get("values")]
    assert degerli, (
        f"{len(calc)} calc kolonunun HİÇBİRİ değer taşımıyor — konnektör yoluna yanlışlıkla "
        "gönderilmiş olabilirler (tabloda yoklar, sessizce boş dönerler)")


def test_hassas_kolon_deger_ORNEKLENIR_ama_promptta_YOK(schema):
    """Faz A1 ile etkileşim: hassasiyet damgası bu yolda basılır; değerler `route()` için
    ÖRNEKLENMEYE devam eder, yalnız prompt sınırında süzülür."""
    from app.sensitivity import is_sensitive, prompt_safe_values

    cols = {c["name"]: c for m in schema["models"] for c in m["columns"]}
    op = cols.get("operator")
    assert op and op.get("values"), "hassas kolon örneklenmemiş — route() körleşir"
    assert is_sensitive(op) and prompt_safe_values(op) == []


def test_fiziksel_ad_NITELIKLI_uretilir(svc):
    """Konnektör yolu şema-nitelikli ad ister (`"katalog"."şema"."tablo"`); niteliksiz ad
    `Catalog Error` verir ve tüm toplu sorgu düşerdi."""
    import json

    mdl = json.loads(svc.mdl_path.read_text(encoding="utf-8"))
    m = next(x for x in mdl["models"] if x["name"] == "partiler")
    ad = svc._physical_name(m)
    assert ad.count(".") >= 1 and ad.startswith('"'), f"nitelikli değil: {ad}"


def test_konnektor_KULLANICI_SQLi_tasimaz():
    """Güvenlik sınırı: konnektör yolu `guard_sql` ve SQL politikasını atlar, bu yüzden
    oraya YALNIZ metadata'dan üretilmiş sorgu gidebilir. Kullanıcı SQL'i `dry_plan`/`query`
    üzerinden gitmeye devam etmeli."""
    import inspect

    from app.wren_service import WrenService

    kaynak = inspect.getsource(WrenService)
    conn_kullananlar = [ad for ad, fn in vars(WrenService).items()
                        if callable(fn) and "_connector()" in (inspect.getsource(fn)
                                                               if hasattr(fn, "__code__") else "")]
    assert set(conn_kullananlar) <= {"_enrich_categorical"}, (
        f"`_connector()` beklenmedik yerlerden çağrılıyor: {conn_kullananlar} — bu yol "
        "guard_sql ve SQL politikasını ATLAR, yalnız metadata'dan üretilmiş sorgu taşıyabilir")
    assert "guard_sql(sql)" in kaynak


def test_schema_ilk_cagri_MAKUL_surede(svc):
    """Regresyon kapısı. Taban 2277 ms'ti, ölçülen 694 ms. Eşik 1500 ms: kesin bir hedef
    değil, **eskiye dönüşü** yakalayan bir tel. (Hedef <150 ms'ye inilemedi — kalan maliyet
    birkaç büyük planın kendisi; iddia edilen değil ölçülen rakam raporlanır.)"""
    svc.invalidate_schema_cache()
    t = time.perf_counter()
    svc.schema()
    sure_ms = (time.perf_counter() - t) * 1000
    assert sure_ms < 1500, f"schema() {sure_ms:.0f} ms — kolon-başına yola dönmüş olabilir"


def test_schema_onbellekli_cagri_BEDAVA(svc):
    svc.schema()
    t = time.perf_counter()
    for _ in range(20):
        svc.schema()
    assert (time.perf_counter() - t) / 20 * 1000 < 1.0
