"""🔴 `§F2` — MOTORUN SQL'İ BİZİMKİYLE **AYNI**; FARK OLAN YER, MOTORUN SESSİZ DÜŞÜRDÜĞÜ.

## Raporun kaygısı ölçüldü ve ÇÜRÜDÜ

`§11.4` *«EN AĞIR BULGU»* diyordu: *«Wren'in artık kendi `CubeQuery`'si var… `cube_router`
`4.807` satırının bir kısmı motorun artık kendi yaptığı işi **ikinci kez** yapıyor
olabilir. Bu ölçülmeli — `wren cube query --sql-only` ile bizim `cube_sql` çıktımız yan
yana konabilir.»*

**Yan yana kondu (2026-08-11, motor `0.13.2`, canlı MDL). Beş vakanın DÖRDÜ bayt bayt
aynı** — çünkü `WrenService.cube_sql` zaten **motoru çağırıyor**:

    from wren_core import cube_query_to_sql
    base = cube_query_to_sql(json.dumps(cq), self._mdl_bytes().decode())

⊙ Yani *«ikinci kez yapıyor»* kaygısı **yersizdi**: SQL üretimi zaten motorun. Ve
`cube_router`'ın satırları SQL üretmiyor — **Türkçe NL → CubeQuery** çeviriyor, ki motor
onu **hiç yapmıyor**. İkisi farklı işlerdir; biri ötekini tekrarlamıyor.

## 🔴 VE ÖLÇÜM DAHA ÖNEMLİ BİR ŞEY BULDU: MOTOR SESSİZCE DÜŞÜRÜYOR

`cube_query_to_sql` desteklemediği alanı **reddetmiyor** — alıp atıyor ve SQL'i
üretiyor. Ölçülen dört alan:

| geçilen | motorun ürettiği | sonuç |
|---|---|---|
| `order` / `orderBy` | `ORDER BY` **yok** | *«en yüksek 5 müşteri»* → **rastgele** 5 müşteri |
| `having` | `HAVING` **yok** | *«10 milyon üzeri»* → eşik **hiç uygulanmaz** |
| `filters: tarih in ["2026-01","2026-03"]` | `WHERE tarih IN ('2026-01','2026-03')` | DATE ↔ ay-metni → **sıfır satır** |

> Üçü de **hatasız, uyarısız ve `source="cube"` rozetiyle** yanlış sayı üretirdi. Bu
> deponun `sessiz_yanlış` diye avladığı sınıfın ta kendisi — ve kaynağı **motor**.

Bu yüzden `cube_sql`'in sarmalayıcıları bir **fazlalık değil, bir korumadır**:
`order`/`limit`/`measure_having`/`ayrik_aylar` motordan **ayıklanır** ve dışarıdan
sarılır. Gerekçeleri bugüne kadar **yazılıydı**; bu dosyayla **ölçülü** hâle geldi.

*Bir bağımlılığın sınırını bilmek yetmez — o sınırın hâlâ orada olduğunu test etmek
gerekir. Yoksa bir gün sınır kalkar ve sarmalayıcı sessizce gereksizleşir; ya da sınır
büyür ve sarmalayıcı sessizce yetersizleşir.*
"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.usefixtures("schema")


def _motor_sql(svc, cq: dict) -> str:
    from wren_core import cube_query_to_sql
    return cube_query_to_sql(json.dumps(cq), svc._mdl_bytes().decode())


@pytest.fixture
def svc():
    from app.config import get_settings
    from app.wren_service import WrenService
    s = get_settings()
    return WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict())


# --- MOTORUN SQL'İ = BİZİMKİ (sarmalayıcı gerekmeyen vakalarda) ------------------

@pytest.mark.parametrize("cq", [
    {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["bolum"]},
    {"cube": "oee", "measures": ["ort_oee", "toplam_durus_dakika"], "dimensions": ["makine"]},
    {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
     "filters": [{"dimension": "musteri", "operator": "eq", "value": "AKKA TEKSTİL"}]},
    {"cube": "parti", "measures": ["toplam_ciro"],
     "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]},
])
def test_SADE_VAKADA_bizim_SQL_motorunkiyle_AYNI(svc, cq):
    """🔴 `§11.4`'ün cevabı: aynı — çünkü `cube_sql` **motoru çağırıyor**. Bir gün
    ayrışırsa, ikinci bir SQL üreticisi doğmuş demektir ve bu test onu yakalar."""
    assert svc.cube_sql(cq).strip() == _motor_sql(svc, cq).strip()


# --- MOTORUN SESSİZ SINIRLARI — SARMALAYICILARIN GEREKÇESİ ----------------------

def test_MOTOR_order_alanini_SESSIZCE_dusuruyor(svc):
    """*«en yüksek 5 müşteri»* motora ham geçilseydi **rastgele** 5 müşteri dönerdi."""
    sql = _motor_sql(svc, {"cube": "parti", "measures": ["toplam_ciro"],
                           "dimensions": ["musteri"],
                           "order": [{"id": "toplam_ciro", "desc": True}]})
    assert "ORDER BY" not in sql.upper(), (
        "motor artık ölçüye göre sıralıyor — `cube_sql`'in dış sarmalayıcısı "
        "GEREKSİZLEŞTİ, kaldırılabilir (bu iyi bir haber, ama sessizce olmamalı)")


def test_MOTOR_having_alanini_SESSIZCE_dusuruyor(svc):
    sql = _motor_sql(svc, {"cube": "parti", "measures": ["toplam_ciro"],
                           "dimensions": ["musteri"],
                           "having": [{"measure": "toplam_ciro", "operator": "gt",
                                       "value": 1000000}]})
    assert "HAVING" not in sql.upper(), (
        "motor artık HAVING üretiyor — `measure_having` sarmalayıcısı gözden geçirilmeli")


def test_MOTOR_ayrik_aylari_YANLIS_kuruyor(svc):
    """🔴 En sinsisi: motor **hata vermiyor**, DATE kolonunu ay-metniyle kıyaslayan bir
    `WHERE` kuruyor → **sıfır satır**, uyarısız. `ayrik_aylar` sarmalayıcısının sebebi."""
    sql = _motor_sql(svc, {"cube": "parti", "measures": ["toplam_ciro"],
                           "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
                           "filters": [{"dimension": "tarih", "operator": "in",
                                        "value": ["2026-01", "2026-03"]}]})
    assert "'2026-01'" in sql, "motorun kurduğu WHERE değişti — ayrik_aylar yeniden ölçülmeli"
    assert "DATE_TRUNC" in sql.upper()
    # Ay kovasına DEĞİL, ham tarihe uygulanıyor: kesilmiş kolon adı WHERE'de yok.
    where = sql.upper().split("WHERE", 1)[1].split("GROUP BY", 1)[0]
    assert "DATE_TRUNC" not in where, (
        "motor artık ay kovasına süzüyor — `ayrik_aylar` sarmalayıcısı kaldırılabilir")


# --- ÜRÜN DOĞRU: sarmalayıcı çalışıyor ------------------------------------------

def test_BIZIM_SQL_siralamayi_UYGULUYOR(svc):
    """Motor düşürüyor, biz sarıyoruz — ve *«en yüksek 5»* gerçekten en yüksek 5.
    ⚠ `order` şekli `{measure, direction}`'dır; `[{id, desc}]` **değil** (ölçüm turunda
    bu karıştırıldı ve sahte bir kusur gibi göründü)."""
    sql = svc.cube_sql({"cube": "parti", "measures": ["toplam_ciro"],
                        "dimensions": ["musteri"],
                        "order": {"measure": "toplam_ciro", "direction": "desc"},
                        "limit": 5})
    u = sql.upper()
    assert "ORDER BY" in u and "DESC" in u and "LIMIT 5" in u
