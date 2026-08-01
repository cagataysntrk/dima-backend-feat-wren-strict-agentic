"""`AskRequest.execute=False` sözleşmesi — "yalnız üret + doğrula, ÇALIŞTIRMA".

NEDEN VAR (canlı bulgu, 2 Ağustos 2026): `execute` alanı `app/schemas.py:54`'te
*"If false, only generate + validate SQL"* diye tanımlıydı ama `/ask` onu **HİÇ
OKUMUYORDU** — `body.execute` dosyada sıfır kez geçiyordu. Yani ölü bir API sözleşmesiydi.

Sonucu yalnız bir API kusuru değildi. Planın ANA ÖLÇÜM ARACI olan `lab/nl_corpus.py`
(~1000 soru × 4 şirket) kendi docstring'inde *"DB'ye BAĞLANMAZ — execute=False +
enrichment no-op → dört şirket de yerelde/hızlı"* diyor. Bayrak yok sayıldığı için
DuckDB olmayan her şirkette (atiksan/gulteks → mssql lab sunucusu) `service.query()`
gerçekten çağrılıyor, konnektör patlıyor, `_answer_from_cube_query` geniş `except`iyle
None dönüyor ve cevap Discovery'ye düşüyordu. Ölçülen yönlendirme başarısı: **%0** —
oysa `route()` o sorulara doğru CubeQuery üretiyordu. Yani ölçüm aracı, ölçtüğünü
sandığı şeyi ölçmüyordu ve üç şirket "tamamen bozuk" görünüyordu.
"""

from __future__ import annotations

import pytest

from tests.conftest import ask

Q = "makine bazında ortalama oee bu yıl"


def test_execute_false_sql_uretir_ama_calistirmaz(client, monkeypatch):
    """SQL + cube_query gelir, `result` GELMEZ — ve `query()` hiç çağrılmaz."""
    import app.wren_service as ws

    cagrildi: list[str] = []

    def _patlat(self, sql, limit=None):
        cagrildi.append(sql)
        raise AssertionError("execute=False iken query() ÇAĞRILMAMALIYDI")

    monkeypatch.setattr(ws.WrenService, "query", _patlat)

    d = ask(client, Q, execute=False)
    assert d["source"] == "cube", f"yapısal yol korunmadı: {d.get('source')} / {d.get('note')}"
    assert d["sql"], "SQL üretilmedi"
    assert d["cube_query"], "cube_query üretilmedi"
    assert d.get("result") is None, "execute=False iken sonuç döndü"
    assert not cagrildi, "query() çağrıldı"


def test_execute_varsayilan_true_sonuc_dondurur(client):
    """Varsayılan davranış değişmedi: sonuç gelir."""
    d = ask(client, Q)
    assert d["source"] == "cube"
    assert d["result"] and d["result"]["rows"], "varsayılan koşumda sonuç yok"


def test_execute_false_dry_plan_HALA_kosar(client, monkeypatch):
    """"Yalnız üret + DOĞRULA" — doğrulama adımı atlanmaz.

    dry_plan patlarsa cevap yapısal yoldan DÜŞMELİ (uydurma SQL yayımlanmamalı).
    """
    import app.wren_service as ws

    kosuldu: list[str] = []

    def _dry(self, sql):
        kosuldu.append(sql)
        raise RuntimeError("dry_plan reddetti")

    monkeypatch.setattr(ws.WrenService, "dry_plan", _dry)

    d = ask(client, Q, execute=False)
    assert kosuldu, "dry_plan çağrılmadı — doğrulama atlandı"
    assert d.get("source") != "cube", "dry_plan reddettiği halde cube cevabı döndü"


@pytest.mark.parametrize("execute", [True, False])
def test_query_contract_her_iki_durumda_da_yazilir(client, execute):
    """Sözleşme kanıtı (ADR-0010) çalıştırma yapılmasa da üretilmeli — SQL + MDL sürümü
    zaten belirlenmiştir."""
    d = ask(client, Q, execute=execute)
    assert d.get("contract_id"), f"execute={execute} için sözleşme kaydı yok"
