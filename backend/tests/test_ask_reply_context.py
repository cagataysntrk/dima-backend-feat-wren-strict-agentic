"""§B düzeltmesi (1 Ağustos 2026) — "bu karta yanıt ver" + çoklu-seçim birleşik bağlam.
Önceki thread modeli kullanıcı tarafından reddedildi (is_new_topic yanlışlıkla thread
sınırı kararına karışıyordu) — bu turda backend'e yalnız iki KATKISAL, salt pass-through/
grounding alanı eklendi: `reply_to_label` (thread_id ile AYNI echo deseni) ve
`extra_context` (yalnız Discovery LLM promptuna grounding, resp.question'a/deterministik
yola HİÇ dokunmaz). Bu testler ikisini de doğrudan doğrular."""

from __future__ import annotations

from tests.conftest import ask

# "sevkiyat durumu" — route()'un DOĞAL olarak None döndüğü, Discovery'ye düşen bir soru
# (bkz. test_discovery_execution_failure.py'nin kendi docstring'i). CANLI BULGU (1 Ağustos
# 2026): tam pytest koşumunda BAŞKA test dosyaları (test_discovery_execution_failure.py,
# test_ask_async_discovery.py) da AYNI soruyu başarıyla üretip VQR'a ("auto") yazıyor —
# session-ömürlü VQR store PAYLAŞILDIĞI için sonraki bir test bu soruyu sorunca "vqr"
# kaynağından (near_exact GÖMME-benzerliği) dönebiliyor, Discovery'ye HİÇ düşmeyebiliyor.
# Rastgele bir sonek eklemek YETMEDİ (gömme-benzerlik küçük metin farklarını da yakın
# sayıyor); nonsense kelimelerle değiştirmek de BAŞKA bir deterministik kapıyı (kısmi
# anlama/çapraz-konu netleştirmesi) tetikledi. Sağlam çözüm: bu üç Discovery testi için
# `vqr.near_exact`'ı doğrudan `None` döndürecek şekilde monkeypatch'lemek — hangi sırada
# koşulursa koşulsun VQR replay'i KESİN olarak devre dışı bırakır.
_DISCOVERY_Q = "sevkiyat durumu"


def _force_discovery(client, monkeypatch) -> None:
    monkeypatch.setattr(client.app.state.vqr, "near_exact", lambda question: None)


def test_reply_to_label_echoed(client):
    d = ask(client, "makine bazında ortalama oee", reply_to_label="ilk rapor")
    assert d["reply_to_label"] == "ilk rapor"


def test_reply_to_label_defaults_none(client):
    d = ask(client, "makine bazında ortalama oee")
    assert d.get("reply_to_label") is None


def test_extra_context_reaches_llm_prompt_not_question(client, monkeypatch):
    """`generate_sql`'i casus bir fonksiyonla değiştirip ARGÜMANI yakalıyoruz, sonra
    dürüst-ret yoluna düşmesi için fırlatıyoruz."""
    _force_discovery(client, monkeypatch)
    captured: list[str] = []

    def spy_generate_sql(question: str, schema: dict) -> str:
        captured.append(question)
        raise RuntimeError("simulated — yalnız argümanı yakalamak için")

    monkeypatch.setattr(client.app.state.llm, "generate_sql", spy_generate_sql)

    d = ask(client, _DISCOVERY_Q, extra_context=["toplam ciro → 12 satır"])

    assert len(captured) == 1
    assert "toplam ciro → 12 satır" in captured[0]
    assert _DISCOVERY_Q in captured[0]  # ham soru grounding metninin İÇİNDE de var
    # UI'daki soru (resp.question) HİÇ değişmemiş olmalı — yalnız LLM'e giden argüman zenginleşti.
    assert d["question"] == _DISCOVERY_Q
    assert d["source"] is None  # generate_sql patladı → dürüst ret
    assert d["note"]


def test_extra_context_ignored_when_no_extra_context(client, monkeypatch):
    """Geriye-uyum kilidi: extra_context verilmezse LLM'e giden metin OLDUĞU GİBİ kalır."""
    _force_discovery(client, monkeypatch)
    captured: list[str] = []

    def spy_generate_sql(question: str, schema: dict) -> str:
        captured.append(question)
        raise RuntimeError("simulated")

    monkeypatch.setattr(client.app.state.llm, "generate_sql", spy_generate_sql)
    ask(client, _DISCOVERY_Q)
    assert captured == [_DISCOVERY_Q]


def test_extra_context_not_used_for_structural_followup(client, monkeypatch):
    """Kapsam sınırı: `cube_query` doluyken (yapısal takip) `extra_context` gönderilse
    bile Discovery LLM çağrıları (generate_sql/generate_followup_sql) HİÇ tetiklenmez —
    deterministik cube-routing yoluna bilinçli olarak karışılmıyor (golden-eval koruması)."""
    calls: list[str] = []
    monkeypatch.setattr(
        client.app.state.llm, "generate_sql",
        lambda question, schema: calls.append("generate_sql") or (_ for _ in ()).throw(RuntimeError()),
    )
    monkeypatch.setattr(
        client.app.state.llm, "generate_followup_sql",
        lambda *a, **k: calls.append("generate_followup_sql") or (_ for _ in ()).throw(RuntimeError()),
    )

    d1 = ask(client, "makine bazında ortalama oee")
    d2 = ask(client, "temmuz ayı", cube_query=d1["cube_query"], extra_context=["ek not → 3 satır"])

    assert d2["source"] == "cube"  # yapısal düzenleme deterministik çalıştı
    assert calls == []  # LLM'e HİÇ düşülmedi
