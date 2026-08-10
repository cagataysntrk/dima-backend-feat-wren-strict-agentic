"""🔴🔴 `§KS` — **HARMAN `order`/`limit`'İ YUTUYORDU: «en kötü üçü» → 11 SIRASIZ SATIR.**

## Ölçülen kusur (curl `N` turu, 2026-08-10 · üç turluk thread)

| tur | soru | sonuç |
|---|---|---|
| 1 | *«bu yıl makinelere göre fire kg»* | 11 satır ✅ |
| 2 | *«bir de oee ekle»* | harman kuruldu, `ort_oee` satırlara girdi ✅ |
| 3 | *«en kötü üçünü göster»* | `cq: order desc · limit 3` — sonuç **11 satır**, ilk satır **en büyük değil** 🔴 |

⊙ Fiş **doğru** yazılmıştı; `blend_sql` onun iki satırını (`order` · `limit`) **hiç
okumuyordu**. Yani kusur ne ayrıştırıcıda ne derleyicideydi — **taşımada**.

*Bir fişin doğru yazılması, okunduğu anlamına gelmez; ve okunmayan bir satır, hiç
yazılmamış bir satırdan daha tehlikelidir — çünkü makbuzda görünür.*
"""

import re

import pytest

from app.wren_service import WrenService


class _Sahte(WrenService):
    """Yalnız `blend_sql`'i sınamak için: MDL ve lehçe sabitlenir, motor kurulmaz.

    ⚠ Alt sınıf **davranışı değiştirmez**, yalnız iki dış bağımlılığı sabitler
    (`_mdl_bytes` · `_inject_always_filter`). Sınanan kod birebir üretimdekidir.
    """

    def __init__(self):                                   # noqa: D107 — fikstür
        self.datasource = "duckdb"

    def _mdl_bytes(self):
        return b"{}"

    def _inject_always_filter(self, sql, cube_name=None):
        return sql


@pytest.fixture()
def svc(monkeypatch):
    """`cube_query_to_sql` yerine, alanları görünür kılan bir taban SQL üreticisi."""
    def _sahte_sql(payload, mdl):
        import json
        p = json.loads(payload)
        kolonlar = [*(p.get("dimensions") or []), *(p.get("measures") or [])]
        return f"SELECT {', '.join(kolonlar)} FROM {p['cube']}_src"

    import wren_core
    monkeypatch.setattr(wren_core, "cube_query_to_sql", _sahte_sql, raising=False)
    return _Sahte()


_CQ = {
    "cube": "parti",
    "measures": ["toplam_fire_kg"],
    "dimensions": ["makine"],
    "blend": [{"cube": "oee", "measures": ["ort_oee"]}],
}


def test_SIRA_HARMANIN_DISINDA_KURULUR(svc):
    """🔴 **Kapının kalbi.** `order` artık dış SELECT'e iner — CTE'ye değil, çünkü
    sıralanacak ölçü **başka bir CTE'den** geliyor olabilir (harmanın var olma sebebi)."""
    sql = svc.blend_sql({**_CQ, "order": {"measure": "toplam_fire_kg", "direction": "desc"}})
    assert re.search(r"ORDER BY toplam_fire_kg DESC\s*$", sql), sql
    assert "ORDER BY 1" not in sql


def test_KESME_UYGULANIR(svc):
    """🔴 Ölçülen sessiz yanlışın kendisi: *«en kötü üçü»* üç satır olmalı."""
    sql = svc.blend_sql({**_CQ, "order": {"measure": "toplam_fire_kg", "direction": "desc"},
                         "limit": 3})
    assert sql.rstrip().endswith("ORDER BY toplam_fire_kg DESC LIMIT 3"), sql


def test_HARMANIN_IKINCI_KUPUNDEN_SIRALANABILIR(svc):
    """⚠ Sıra ölçüsü **eklenen** cube'a aitse de çalışmalı — yoksa düzeltme yarım olurdu
    ve *«oee'si en düşük üçü»* yine sırasız dönerdi."""
    sql = svc.blend_sql({**_CQ, "order": {"measure": "ort_oee", "direction": "asc"},
                         "limit": 2})
    assert sql.rstrip().endswith("ORDER BY ort_oee ASC LIMIT 2"), sql


def test_TANINMAYAN_OLCUDE_SIRA_KURULMAZ(svc):
    """🔴🔴 **FAIL-CLOSED — ve kapının en önemli satırı.**

    Sıralanmak istenen ölçü harmanın teslim ettiği kolonlar arasında değilse uydurma bir
    kolon adı SQL'i patlatırdı. Ve `limit` de **uygulanmaz**: *sırasız bir kesme rastgele
    bir örneklemdir* ve onu «en kötü üçü» diye sunmak, bu düzeltmenin kapattığı kusurun
    ta kendisidir.
    """
    sql = svc.blend_sql({**_CQ, "order": {"measure": "yok_boyle_bir_olcu", "direction": "desc"},
                         "limit": 3})
    assert "yok_boyle_bir_olcu" not in sql
    assert "LIMIT" not in sql.upper()
    assert sql.rstrip().endswith("ORDER BY 1"), "eski ordinal sıra korunmalı"


def test_SIRASIZ_HARMAN_BIREBIR_ESKI_DAVRANIS(svc):
    """`KURAL B`: `order` yoksa üretilen SQL değişmez — düzeltme bir **ek**tir, bir
    yeniden yazım değil."""
    sql = svc.blend_sql(dict(_CQ))
    assert sql.rstrip().endswith("ORDER BY 1")


def test_ANAHTARSIZ_HARMANDA_SIRA_YOK(svc):
    """⚠ Kırılımsız (tek satır × tek satır) harmanda sıralanacak bir liste yoktur;
    oraya `ORDER BY` yazmak anlamsız bir işlem olurdu."""
    sql = svc.blend_sql({"cube": "parti", "measures": ["toplam_fire_kg"],
                         "blend": [{"cube": "oee", "measures": ["ort_oee"]}],
                         "order": {"measure": "toplam_fire_kg", "direction": "desc"}})
    assert "ORDER BY" not in sql.upper()
