"""Canlı bulgu (31 Temmuz 2026): Discovery yolunun SON adımı — `service.query(wren_sql, ...)`
— dosyadaki TEK sarmalanmamış çağrıydı. `dry_plan` (planlama) geçse bile GERÇEK ÇALIŞTIRMA
ayrı bir aşamadır ve karmaşık sorularda patlayabiliyordu → çıplak 500 (kullanıcı örneği:
"makine bazlı verimlilik trendi hesapla son 6 ay ve üretime etkisini göster"). Düzeltme:
`app/routers/ask.py`'de try/except + `dry_plan` hatasındaki AYNI self-healing (`llm.repair`)
turu ÇALIŞTIRMA hatasında da denenir; o da başarısız olursa dürüst ret (asla 500).

Bu test GERÇEK bir LLM'in üretebileceği "dry_plan geçer ama çalıştırma patlar" senaryosunu
`WrenService.query`'yi monkeypatch'leyerek simüle eder — "asdf zxcv listele" gibi `route()`'un
DOĞAL olarak None döndüğü (mock gerekmeden Discovery'ye düşen) bir soru kullanılır.
    ## ⟳ ARAÇ DEĞİŞTİ (2026-08-06) — ölçüt DEĞİL

    Bu test `"sevkiyat durumu"` kullanıyordu ve kural motoru ona
    `SELECT COUNT(*) FROM partiler` → **37 878** üretiyordu. O bir **uydurmaydı**: dört
    farklı anlamsız soru aynı sayıyı veriyordu (`tests/test_uydurma_sayi_yok.py`) ve dal
    `ce5177d`de kapatıldı → bu kapı kırmızıya döndü.

    Yeni araç `"asdf zxcv listele"`: kapsam kapısından düşer, Discovery'ye ulaşır ve
    kural motorunun **satır dökümü** dalından cevaplanır. Döküm bir sayı UYDURMAZ —
    veriyi olduğu gibi gösterir. *Bir kapının ölçtüğü şey doğruysa, o şeyi ölçme biçimi
    değişebilir.*
"""

from __future__ import annotations

from app.wren_service import WrenService


def test_discovery_execution_failure_never_500(client, monkeypatch):
    original_query = WrenService.query
    calls: list[str] = []

    def flaky_query(self, sql: str, *args, **kwargs):
        calls.append(sql)
        if len(calls) == 1:
            raise RuntimeError("Binder Error: simulated execution failure (dry_plan geçti)")
        return original_query(self, sql, *args, **kwargs)

    monkeypatch.setattr(WrenService, "query", flaky_query)

    r = client.post("/ask", json={"question": "asdf zxcv listele", "execute": True})
    assert r.status_code == 200, r.text  # ASLA 500 — dürüst ret ya da self-heal
    body = r.json()
    assert len(calls) >= 1  # gerçekten çalıştırma denendi (dry_plan'dan geçti)
    if body.get("result") is None:
        assert body.get("note")  # başarısızsa dürüst açıklama taşımalı (sessiz değil)


def test_cube_endpoint_execution_failure_never_500(client, monkeypatch):
    """`/cube` (chip düzenlemesi) için AYNI sınıf açık — `service.query` hiç sarmalanmamıştı."""
    original_query = WrenService.query

    def always_fails(self, sql: str, *args, **kwargs):
        raise RuntimeError("simulated execution failure")

    monkeypatch.setattr(WrenService, "query", always_fails)

    r = client.post("/cube", json={"cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}})
    assert r.status_code == 400, r.text  # dürüst 400 — asla çıplak 500
    assert "detail" in r.json()
