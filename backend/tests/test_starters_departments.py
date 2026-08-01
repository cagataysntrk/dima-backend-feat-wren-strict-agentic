"""Faz 4.8 (1 Ağustos 2026) — "Ne sorabilirim?" departman/grup etiketleri (dış yol
haritası 1.13). `demo/packs/starters.yml` (YENİ, global) her starter'a bir `grup`
(departman) etiketi ekler; bu testler (a) API'nin `grup` alanını gerçekten döndürdüğünü,
(b) HER starter sorusunun GERÇEKTEN deterministik bir cube cevabına ulaştığını (dürüst-
ret/netleştirmeye DÜŞMEDİĞİNİ) kanıtlar — küratörlü bir örneğin bozuk olması, hiç
küratör olmamasından (katalog otomatiğine düşme) DAHA KÖTÜdür, bu yüzden tek tek doğrulanır."""

from __future__ import annotations

from tests.conftest import ask


def test_starters_endpoint_returns_grouped_entries(client):
    r = client.get("/starters")
    assert r.status_code == 200, r.text
    starters = r.json()["starters"]
    # demo-boyahane sektör pack'i (rol-filtreli, TEST_USER "owner") en az 4 küratörlü
    # örnek döndürür — "enerji yoğunluğu" surdurulebilirlik/yonetici rolüne özel, owner'a
    # GÖRÜNMEMELİ (rol filtresi doğru çalıştığının da kanıtı).
    assert len(starters) >= 4
    assert all("label" in s and "query" in s for s in starters)
    groups = {s.get("grup") for s in starters if s.get("grup")}
    assert groups >= {"Üretim", "Kalite", "Satış/Ticaret"}
    assert not any(s["label"] == "Makine bazında enerji yoğunluğu" for s in starters)


def test_every_starter_query_routes_to_a_real_cube_answer(client):
    """Küratörlü bir örnek dürüst-ret/netleştirmeye düşerse KULLANICIYA YALAN söylemiş
    olur ("bunu sorabilirsin" dedik ama cevaplayamadık) — bu yüzden HER biri gerçekten
    çalıştırılıp doğrulanır (mock değil, gerçek /ask çağrısı).

    NOT: `source` "cube" DIŞINDA "vqr" da olabilir — tam test paketi koşumunda BAŞKA
    testlerin öğrettiği bir VQR çifti (near-match) bu soruyu yakalayabilir; bu da GERÇEK
    ve DOĞRU bir anlık cevaptır (bkz. tests/test_ask_golden.py VQR testleri) — bir
    starter'ın "anlık cevap ver" sözleşmesini BOZMAZ. Yalnız clarification/dürüst-ret
    (source=None) BAŞARISIZLIKTIR."""
    starters = client.get("/starters").json()["starters"]
    assert starters
    for s in starters:
        d = ask(client, s["query"])
        assert d["source"] is not None and d.get("result") is not None, (
            f"starter '{s['label']}' ({s['query']!r}) anlık cevap ÜRETMEDİ (netleştirmeye/"
            f"dürüst-rete düştü): source={d.get('source')!r} note={d.get('note')!r}"
        )
