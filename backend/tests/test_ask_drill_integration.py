"""Faz 4.10 (1 Ağustos 2026) — /ask/drill UÇTAN UCA entegrasyon testi: kullanıcının somut
senaryosunu BİREBİR canlandırır — "makine bazında OEE düşük çıktı, kök nedenine giden yol
sistem tarafından sağlanmalı, ilgili TÜM veriye ulaşılabilmeli". Her adım GERÇEK bir sorgu
çalıştırır (mock yok) — dry_plan+execute+Query Contract, tıpkı /cube gibi. Zincir: makine
kırılımı → en düşük makineyi SEÇ → vardiya kırılımı → bir vardiyayı SEÇ → İLİŞKİLİ
makine_duruslari cube'una GEÇ (kök neden) → neden kırılımı → YAPRAK: ham satırlar."""

from __future__ import annotations

from tests.conftest import ask


def _drill(client, **body) -> dict:
    r = client.post("/ask/drill", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_full_drill_chain_reaches_root_cause_and_raw_rows(client):
    # 1) Taze rapor: makine bazında ortalama OEE, bu yıl.
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    assert d["source"] == "cube"
    base_cq = d["cube_query"]
    assert base_cq["dimensions"] == ["makine"]

    # 2) action=explain — ZATEN elde olan sonucu yorumla (yeni sorgu YOK).
    explained = _drill(client, cube_query=base_cq, result=d["result"], action="explain")
    assert "makine bazında" in explained["formula_explanation"]
    assert any(dd["name"] == "vardiya" for dd in explained["available_dimensions"])
    assert any(dd["name"] == "hat" for dd in explained["available_dimensions"])
    # İlişkili cube keşfi: "makine" boyutunu paylaşan makine_duruslari bulunmalı.
    related_names = {r["cube"] for r in explained["related_cubes"]}
    assert "makine_duruslari" in related_names

    # En düşük OEE'li makineyi bul (gerçek veriden — hardcode YOK).
    worst_row = min(d["result"]["rows"], key=lambda r: r["ort_oee"])
    worst_makine = worst_row["makine"]

    # 3) action=select: o makineye FİLTRELE — GERÇEK sorgu, TÜM oee ölçüleriyle döner.
    selected = _drill(client, cube_query=base_cq, action="select",
                      dimension="makine", filter_value=worst_makine)
    assert selected["contract_id"]
    assert selected["result"] is not None
    cols = set(selected["result"]["columns"])
    # Kullanıcı talebi: "hesapta olan TÜM ilişkiyi görebilmeli" — yalnız ort_oee değil,
    # bileşenleri (kullanılabilirlik/performans/kalite) VE duruş dakikası da AYNI yanıtta.
    assert {"ort_oee", "ort_kullanilabilirlik", "ort_performans", "ort_kalite",
           "toplam_durus_dakika"} <= cols
    assert selected["cube_query"]["filters"][-1] == {
        "dimension": "makine", "operator": "eq", "value": worst_makine}
    assert selected["cube_query"]["dimensions"] == []

    # 4) action=expand: bu makinede VARDİYA'ya göre kır (hangi vardiya düşürüyor?).
    by_vardiya = _drill(client, cube_query=selected["cube_query"], action="expand",
                        dimension="vardiya")
    assert by_vardiya["contract_id"]
    assert by_vardiya["result"]["row_count"] >= 1
    assert "vardiya" in by_vardiya["cube_query"]["dimensions"]
    assert all(dd["name"] != "vardiya" for dd in by_vardiya["available_dimensions"])
    assert any(dd["name"] == "hat" for dd in by_vardiya["available_dimensions"])

    vardiya_value = by_vardiya["result"]["rows"][0]["vardiya"]

    # 5) action=select: bir vardiyaya daha FİLTRELE (breadcrumb'ın bir sonraki adımı).
    by_shift = _drill(client, cube_query=by_vardiya["cube_query"], action="select",
                      dimension="vardiya", filter_value=vardiya_value)
    assert by_shift["contract_id"]
    assert {"dimension": "vardiya", "operator": "eq", "value": vardiya_value} in (
        by_shift["cube_query"]["filters"])

    # 6) action=related: KÖK NEDEN için ilişkili cube'a geç (makine_duruslari — duruş
    # nedenleri). Yalnız PAYLAŞILAN filtreler (makine + tarih) taşınır; vardiya CASE-
    # dönüştürülmüş bir etiket olduğundan ham veri değeriyle eşleşmeyebilir — bu yüzden
    # yalnız makine+tarih paylaşımını doğruluyoruz (ayrı, gerçekçi bir sınır).
    related = _drill(client, cube_query=by_shift["cube_query"], action="related",
                     target_cube="makine_duruslari")
    assert related["cube_query"]["cube"] == "makine_duruslari"
    assert related["contract_id"]
    assert any(f["dimension"] == "makine" for f in related["cube_query"]["filters"])
    assert any(dd["name"] == "neden" for dd in related["available_dimensions"])

    # 7) action=expand: makine_duruslari'nda NEDEN'e göre kır — GERÇEK kök neden burada.
    by_reason = _drill(client, cube_query=related["cube_query"], action="expand",
                       dimension="neden")
    assert by_reason["contract_id"]
    assert by_reason["result"]["row_count"] >= 1
    assert "neden" in by_reason["result"]["columns"]

    # 8) action=raw — YAPRAK seviyesi: HAM satırlar (kullanıcı talebi: "tüm veri ağacına
    # ulaşabilmeli"). Gerçek base_object'ten (oee_vardiya) satır döner.
    raw = _drill(client, cube_query=selected["cube_query"], action="raw", limit=10)
    assert raw["raw_rows"] is not None
    assert raw["raw_rows"]["row_count"] >= 1
    assert raw["contract_id"]


def test_drill_explain_on_discovery_result_is_honest_no_fake_branching(client):
    """cube_query'si OLMAYAN (Discovery/ham-SQL kaynaklı) bir sonuç için dallanma
    SUNULMAZ — asla sahte bir dallanma uydurulmaz (dürüst geri düşüş)."""
    body = _drill(client, cube_query=None, action="explain")
    assert body["available_dimensions"] == []
    assert body["related_cubes"] == []
    assert "Discovery" in body["formula_explanation"]


def test_drill_expand_requires_dimension_param(client):
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    r = client.post("/ask/drill", json={"cube_query": d["cube_query"], "action": "expand"})
    assert r.status_code == 400


def test_drill_select_requires_dimension_and_value(client):
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    r = client.post("/ask/drill", json={"cube_query": d["cube_query"], "action": "select",
                                        "dimension": "makine"})
    assert r.status_code == 400


def test_drill_related_requires_target_cube(client):
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    r = client.post("/ask/drill", json={"cube_query": d["cube_query"], "action": "related"})
    assert r.status_code == 400


def test_drill_related_rejects_unknown_target_cube(client):
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    r = client.post("/ask/drill", json={"cube_query": d["cube_query"], "action": "related",
                                        "target_cube": "hic-boyle-bir-cube-yok"})
    assert r.status_code == 400


def test_drill_unknown_action_rejected(client):
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    r = client.post("/ask/drill", json={"cube_query": d["cube_query"], "action": "ucur"})
    assert r.status_code == 400


def test_drill_steps_expose_running_sql_and_duration_for_evidence_panel(client):
    """Doğrulama turu düzeltmesi (1 Ağustos 2026) — dış yol haritası UC-2.18 ("kanıt paneli:
    formül, kaynak tablolar, ÇALIŞAN SQL, süre") ve UC-2.19 ("kanıt panelindeki SQL kopyalanıp
    DB'de çalıştırılır → ekrandaki sonucun AYNISI çıkar"). Her adımın `sql` alanı dolu olmalı
    VE o SQL /query'ye AYNEN gönderildiğinde drill'in kendi `result`'ıyla BİREBİR aynı satırları
    üretmeli — SQL'in gösterimlik bir süs değil, GERÇEKTEN çalışan/tekrar-oynatılabilir bir
    kanıt olduğunu ispatlar."""
    d = ask(client, "bu yıl makine bazında ortalama oee", execute=True)
    base_cq = d["cube_query"]

    # explain: yeni sorgu ÇALIŞTIRMAZ ama SQL METNİ yine de üretilmeli (formülün kanıtı).
    explained = _drill(client, cube_query=base_cq, result=d["result"], action="explain")
    assert explained["sql"], "explain adımı da SQL üretmeli (kanıt paneli UC-2.18)"
    assert explained["duration_ms"] is None  # hiçbir sorgu ÇALIŞTIRILMADI, süre yok — dürüst

    worst_row = min(d["result"]["rows"], key=lambda r: r["ort_oee"])
    worst_makine = worst_row["makine"]

    for resp in (
        _drill(client, cube_query=base_cq, action="select",
              dimension="makine", filter_value=worst_makine),
        _drill(client, cube_query=base_cq, action="expand", dimension="vardiya"),
    ):
        assert resp["sql"], "sorgu ÇALIŞTIRAN her adım kendi SQL'ini döndürmeli"
        assert resp["duration_ms"] is not None and resp["duration_ms"] >= 0

        # UC-2.19: SQL'i KOPYALA, /query'ye DOĞRUDAN gönder — AYNI VERİ çıkmalı. Satır SIRASI
        # (ORDER BY yoksa) motor tarafından garanti edilmez — bu yüzden MULTISET olarak
        # karşılaştırılır (sıralanmış JSON temsili), tek tek satır SIRASI değil.
        import json as _json

        def _as_multiset(rows: list[dict]) -> list[str]:
            return sorted(_json.dumps(r, sort_keys=True, default=str) for r in rows)

        replay = client.post("/query", json={"sql": resp["sql"]})
        assert replay.status_code == 200, replay.text
        replayed = replay.json()
        assert replayed["columns"] == resp["result"]["columns"]
        assert _as_multiset(replayed["rows"]) == _as_multiset(resp["result"]["rows"])

    # raw (yaprak seviyesi) — kendi ham-satır SQL'i de aynı şekilde tekrar-oynatılabilir.
    raw = _drill(client, cube_query=base_cq, action="select",
                dimension="makine", filter_value=worst_makine)
    raw = _drill(client, cube_query=raw["cube_query"], action="raw", limit=5)
    assert raw["sql"]
    assert raw["duration_ms"] is not None
    replay = client.post("/query", json={"sql": raw["sql"]})
    assert replay.status_code == 200, replay.text
    assert replay.json()["row_count"] == raw["raw_rows"]["row_count"]


def test_drill_stale_cube_query_never_500(client):
    """Şema değişmiş/bozuk bir cube_query (var olmayan cube) 500 DEĞİL, dürüst 400 döner."""
    r = client.post("/ask/drill", json={
        "cube_query": {"cube": "hic-boyle-bir-cube-yok", "measures": ["x"]},
        "action": "explain"})
    assert r.status_code == 400
