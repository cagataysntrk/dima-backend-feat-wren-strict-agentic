"""Doğrulama turu düzeltmesi (1 Ağustos 2026) — `app/kpi.py`'nin cross-cube KPI motoru
canlı akışa HİÇ bağlı DEĞİLDİ: `resolve_kpi`/`resolve_kpi_series` hiçbir router'dan
çağrılmıyordu, `AskResponse.kpi` hiçbir zaman set edilmiyordu. `tests/test_kpi.py` zaten
`cube_router.match_kpi`'nin VAR OLMASINI bekliyordu (`test_likidite_kpileri_mizan_uzerinde`,
`test_match_kpi_en_uzun_sinonim_kazanir`) ama `cube_router.py`'de HİÇ TANIMLI değildi — bu
turda hem fonksiyon eklendi hem `/ask`'e bağlandı (bkz. `FAZ4-SONRASI-ONERILER_2026-08-01.md`
P1-1). Bu dosya SAF `match_kpi` mantığını `test_kpi.py`'nin GERÇEK compose+resolver
testlerinden AYRI, basit bir sahte şemayla (compose gerekmeden) tamamlar VE `/ask`'in
GERÇEKTEN `match_kpi`→`resolve_kpi` zincirini çağırdığını uçtan uca kanıtlar — WIRING'in
kendisi test edilir, `kpi.py`'nin formül matematiği DEĞİL (o zaten test_kpi.py'de kanıtlı)."""

from __future__ import annotations

from app.cube_router import match_kpi
from app.llm import _norm

_SCHEMA = {
    "cubes": [],
    "kpis": [
        {"name": "cari_oran", "label": "Cari Oran (Current Ratio)",
         "synonyms": [_norm(s) for s in ["cari oran", "current ratio", "likidite oranı"]]},
        {"name": "ccc", "label": "Nakit Döngü Süresi (CCC)",
         "synonyms": [_norm(s) for s in
                     ["nakit döngü süresi", "ccc", "cash conversion cycle"]]},
    ],
}


def test_match_kpi_finds_synonym():
    assert match_kpi(_norm("cari oranımız kaç bu ay"), _SCHEMA) == "cari_oran"


def test_match_kpi_returns_none_when_no_kpis_compiled():
    """Çoğu tenant (demo-boyahane dahil) için schema()["kpis"] BOŞTUR — davranış DEĞİŞMEZ."""
    assert match_kpi(_norm("cari oranımız kaç"), {"cubes": [], "kpis": []}) is None
    assert match_kpi(_norm("cari oranımız kaç"), {"cubes": []}) is None


def test_match_kpi_returns_none_for_unrelated_question():
    assert match_kpi(_norm("makine bazında ortalama oee bu yıl"), _SCHEMA) is None


def test_match_kpi_prefers_longer_more_specific_synonym():
    """İki KPI'nın sinonimleri iç içe geçse bile (ör. biri diğerinin alt-dizisi), en UZUN
    (en spesifik) eşleşme kazanır — cube-eşleştirmedeki "ölçü kanıtı" ilkesiyle AYNI
    (`test_kpi.py::test_match_kpi_en_uzun_sinonim_kazanir` GERÇEK KPI adlarıyla AYNISINI
    zaten kanıtlıyor — burada yalnız senaryo BAŞKA bir sahte şemayla tekrarlanır)."""
    schema = {
        "cubes": [],
        "kpis": [
            {"name": "oran", "label": "Oran", "synonyms": [_norm("oran")]},
            {"name": "cari_oran", "label": "Cari Oran", "synonyms": [_norm("cari oran")]},
        ],
    }
    assert match_kpi(_norm("cari oran nedir"), schema) == "cari_oran"


def test_ask_wires_kpi_match_to_resolve_kpi(client, monkeypatch):
    """UÇTAN UCA: /ask GERÇEKTEN match_kpi→resolve_kpi zincirini çağırır ve AskResponse.kpi'yi
    doldurur. `WrenService.schema` (bu şirkette normalde BOŞ olan kpis listesini enjekte
    etmek için) ve `app.kpi.load_kpis`/`resolve_kpi` (gerçek bir gulteks/logo-3 kurulumu
    GEREKTİRMEDEN) monkeypatch'lenir — test edilen şey WIRING, kpi.py'nin kendi
    matematiği DEĞİL (o zaten tests/test_kpi.py'de kanıtlı)."""
    from app.wren_service import WrenService

    original_schema = WrenService.schema

    def fake_schema(self):
        s = original_schema(self)
        return {**s, "kpis": [{"name": "cari_oran", "label": "Cari Oran",
                               "synonyms": [_norm("cari oran")]}]}

    monkeypatch.setattr(WrenService, "schema", fake_schema)

    import app.kpi as kpi_mod

    monkeypatch.setattr(kpi_mod, "load_kpis", lambda project_dir: {
        "cari_oran": {"name": "cari_oran", "formula": "a", "components": {}},
    })
    monkeypatch.setattr(kpi_mod, "resolve_kpi", lambda svc, spec, where="": {
        "kpi": "cari_oran", "label": "Cari Oran", "unit": "x", "lower_is_better": False,
        "formula": "a", "explain": None, "value": 1.8, "components": [],
    })

    r = client.post("/ask", json={"question": "cari oranımız kaç"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kpi"] is not None
    assert body["kpi"]["kpi"] == "cari_oran"
    assert body["kpi"]["value"] == 1.8
    assert body["source"] == "cube"
    assert any("KPI" in t for t in body.get("trace") or [])


def test_ask_kpi_match_does_not_fire_when_schema_has_no_kpis(client):
    """Regresyon kilidi: bugünkü demo-boyahane şemasında `kpis` BOŞTUR — normal bir OEE
    sorusu KPI dalına hiç GİRMEMELİ, mevcut cube-yönlendirme davranışı DEĞİŞMEMELİ."""
    r = client.post("/ask", json={"question": "bu yıl makine bazında ortalama oee",
                                  "execute": True})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kpi"] is None
    assert body["source"] == "cube"
    assert body["result"] is not None
