"""FAZ 1.1 — **ÖN KOŞUL ÖLÇÜMÜ: motor RLS'i gerçekten uyguluyor mu?**

`1.1` motorun `rowLevelAccessControls` + `SessionProperty` yeteneği üstüne kurulacak.
Bir katmanı, **kanıtlanmamış** bir yeteneğin üstüne inşa etmek bu belgenin `KAT-3`
ihlalidir; o yüzden yetenek **önce ölçüldü** (2026-08-04) ve dört bulgusu burada
**donduruldu**. Motor sürümü değişip davranış kayarsa `1.1`'in tasarımı **sessizce**
çürümesin.

## Ölçülen dört gerçek

| # | Soru | Sonuç |
|---|---|---|
| **1** | Koşul SQL'e enjekte oluyor mu? | ✅ modelin alt sorgusuna `WHERE … = 'değer'` |
| **2** | **JOIN** ile baypas edilebiliyor mu? | ✅ **HAYIR** — filtre join'in **iki tarafına da** iniyor |
| **3** | Property verilmezse? | ✅ **fail-closed** — planlama hatası, filtresiz sorgu DEĞİL |
| **4** | Kötücül/kaçışsız değer? | ✅ reddediliyor — *"allow only literal value"* |

🔴 **(2) bu maddenin varlık sebebidir.** `always_filter` bir **uygulama katmanı** yamasıdır
ve `compose.py:434` (**G10**) onun **join altında baypas edildiğini** ölçmüştü: filtre
yalnız o cube'un kendi SQL'ine ekleniyor, join `__source` seviyesinde gerçekleşiyor.
Motor RLS'i o deliği **yapısal olarak** kapatıyor.

⚠ **(4) bir güvenlik yüzeyini KONUMLANDIRIYOR:** session property değerleri **SQL
literali** olarak veriliyor, yani tırnaklama/kaçış **bizim tarafımızda**. Motor tek bir
literal dışındaki her şeyi reddederek ikinci bir savunma koyuyor — ama ilk savunma
`1.1`'in `oturum_ozellikleri()` fonksiyonu olacak.

⚠ **Değerler `frozenset(dict.items())` olarak veriliyor** (`wren.engine._plan` onu böyle
kuruyor); düz `dict` geçmek `TypeError` verir. Bu, ölçüm sırasında düşülen ve burada
kilitlenen bir tuzak.
"""

from __future__ import annotations

import base64
import json

import pytest

Q = "'"

#: Bu sözlük hem testin girdisi hem de `1.1`'in **tasarım şablonudur**.
_RLAC = {
    "name": "rls_t",
    "requiredProperties": [{"name": "session_tenant", "required": True}],
    "condition": "tenant = @session_tenant",
}


def _mdl(*, rlac: bool = True) -> str:
    model: dict = {
        "name": "t",
        "tableReference": {"catalog": "memory", "schema": "main", "table": "t"},
        "columns": [{"name": "id", "type": "integer"},
                    {"name": "tenant", "type": "varchar"}],
    }
    if rlac:
        model["rowLevelAccessControls"] = [_RLAC]
    return base64.b64encode(json.dumps(
        {"catalog": "c", "schema": "s", "models": [model]}).encode()).decode()


def _ctx(props: dict | None):
    wc = pytest.importorskip("wren_core")
    return wc.SessionContext(_mdl(), None,
                             frozenset(props.items()) if props else None, "duckdb")


def _tenant(deger: str = "atiksan") -> dict:
    return {"session_tenant": f"{Q}{deger}{Q}"}


# ── 1 · ENJEKSİYON ───────────────────────────────────────────────────────────

def test_1_KOSUL_SQL_E_ENJEKTE_OLUYOR():
    """Yetenek **var mı** sorusunun cevabı. Yoksa `1.1` `⊘ ÖLÇÜLEMEDİ`'dir."""
    sql = _ctx(_tenant()).transform_sql("SELECT id FROM t")
    assert "tenant = 'atiksan'" in sql, sql


def test_2_JOIN_BAYPAS_EDEMIYOR():
    """🔴 **Maddenin varlık sebebi.** `always_filter` burada baypas ediliyordu (G10):
    filtre yalnız cube'un kendi SQL'ine ekleniyor, join `__source` seviyesinde oluyor.

    Motor RLS'te filtre **her model referansına** iniyor — join'in **iki tarafına da**.
    """
    sql = _ctx(_tenant()).transform_sql("SELECT a.id FROM t a JOIN t b ON a.id=b.id")
    assert sql.count("tenant = 'atiksan'") == 2, (
        f"filtre join'in her iki tarafına inmedi ({sql.count(chr(39))}): {sql}")


def test_3_PROPERTY_YOKSA_FAIL_CLOSED():
    """🔴 **Filtresiz sorgu DEĞİL, hata.** Ters davranış (sessizce filtresiz plan) bu
    maddeyi bir güvenlik yamasından bir **süse** çevirirdi: kimlik enjekte edilmeyi
    unutulduğu gün sistem **sessizce** tüm satırları döndürürdü."""
    wc = pytest.importorskip("wren_core")
    with pytest.raises(Exception) as ex:
        wc.SessionContext(_mdl(), None, None, "duckdb").transform_sql("SELECT id FROM t")
    assert "required" in str(ex.value), str(ex.value)


def test_4_KOTUCUL_DEGER_REDDEDILIYOR():
    """Session property değerleri **SQL literali** olarak veriliyor → tırnaklama/kaçış
    BİZİM tarafımızda. Motor tek literal dışındaki her şeyi reddederek **ikinci** bir
    savunma koyuyor; `1.1`'in `oturum_ozellikleri()`'si **birinci** savunma olacak."""
    wc = pytest.importorskip("wren_core")
    with pytest.raises(Exception) as ex:
        _ctx({"session_tenant": f"{Q}x{Q} OR {Q}1{Q}={Q}1{Q}"}).transform_sql(
            "SELECT id FROM t")
    assert "literal" in str(ex.value).lower(), str(ex.value)


def test_5_PROPERTIES_FROZENSET_ISTIYOR():
    """⚠ Ölçüm sırasında düşülen tuzak: düz `dict` `TypeError` verir. `wren.engine._plan`
    onu `frozenset(properties.items())` diye kuruyor; `1.1` aynı biçimi kullanmak
    zorunda — yoksa hata **çalışma anında** ve **kimlik yolunda** patlar."""
    wc = pytest.importorskip("wren_core")
    with pytest.raises(TypeError):
        wc.SessionContext(_mdl(), None, _tenant(), "duckdb")


def test_6_RLAC_MANIFEST_ROUND_TRIP_TE_KAYBOLMUYOR():
    """`ManifestExtractor.extract_by()` `dry_plan` yolunda manifesti **daraltıyor**.
    RLAC o daraltmada düşerse motor filtreyi hiç görmez ve `1.1` **sessizce** devre dışı
    kalır — yeşil testlerle birlikte."""
    wc = pytest.importorskip("wren_core")
    b64 = _mdl()
    geri = json.loads(base64.b64decode(
        wc.to_json_base64(wc.ManifestExtractor(b64).extract_by(["t"]))))
    kurallar = geri["models"][0].get("rowLevelAccessControls")
    assert kurallar and kurallar[0]["condition"] == _RLAC["condition"], geri["models"][0]


def test_7_MOTOR_YUZEYI_UC_YOLDA_DA_PROPERTIES_ALIYOR():
    """`dry_plan` · `query` · `dry_run` — üçü de `properties` almalı. Biri almazsa o yol
    **RLS'siz** koşar ve tam olarak bugün `always_filter`'da ölçülen asimetri doğar
    (*"istek yolu güvenli, öteki yol açık"*)."""
    import inspect

    engine = pytest.importorskip("wren.engine")
    for ad in ("dry_plan", "query", "dry_run"):
        imza = inspect.signature(getattr(engine.WrenEngine, ad))
        assert "properties" in imza.parameters, f"{ad} `properties` almıyor: {imza}"
