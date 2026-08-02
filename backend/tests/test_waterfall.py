"""FAZ I2 — ŞELALE (waterfall): PVM'nin görünen yarısı.

## Ölçülen boşluk

Faz 5.1'de PVM'nin (fiyat–miktar–birleşik) **matematiği yazıldı** ve artıksızlığı
`test_pvm_ARTIKSIZ` ile kilitlendi. Ama **görseli yoktu**: `grep -c waterfall app/viz.py`
→ **0**. Özelliğin görünen yarısı eksikti; kullanıcı üç sayıyı bir ızgarada görüyor,
"nasıl bu sonuca vardık" yolunu göremiyordu.

## Seçim kuralı — her yeni tür bir kuralla gelir (plan I2)

Şelalenin tüm anlamı şudur: *"bu çubukları üst üste koyarsan sondaki değere varırsın."*
Bileşenler toplamı bitişe varmıyorsa **grafik yalan söyler** — çubuklar bir yere çıkar,
eksen başka bir yeri gösterir ve okuyan farkı **göremez**.

Bu yüzden kural bir tercih değil bir **KAPIDIR**: toplam tutmuyorsa `None` döner ve
çağıran tabloya düşer. `viz.py`'nin varlık sebebi (ADR-0024) *"grafik kararı deterministik
ve doğrulanabilir olsun"*dur; toplamı denetlemeyen bir şelale o sebebi çürütürdü.
"""

from __future__ import annotations

import pytest

from app import viz


# --- ASIL KAPI: artıksızlık ------------------------------------------------------

def test_ARTIKSIZ_ayrisma_kabul_edilir():
    spec = viz.waterfall_spec(baslangic=0.0, bitis=100.0,
                              bilesenler=[("fiyat", 60.0), ("miktar", 30.0),
                                          ("birleşik", 10.0)])
    assert spec and spec["kind"] == "waterfall"
    assert [s["value"] for s in spec["steps"]] == [60.0, 30.0, 10.0]
    assert spec["net"] == 100.0


def test_ARTIK_VARSA_grafik_REDDEDILIR():
    """ASIL KAPI. Bileşenler 90, net 100 → 10 birim artık. Çubuklar 90'a çıkar, eksen
    100'ü gösterir ve okuyan farkı GÖREMEZ. Grafik susmalı, tablo konuşmalı."""
    assert viz.waterfall_spec(baslangic=0.0, bitis=100.0,
                              bilesenler=[("fiyat", 60.0), ("miktar", 30.0)]) is None


def test_kucuk_KAYAN_NOKTA_farki_kabul_edilir():
    """`0.1 + 0.2 != 0.3` — birebir eşitlik istemek meşru her ayrışmayı reddederdi."""
    assert viz.waterfall_spec(baslangic=0.0, bitis=0.3,
                              bilesenler=[("a", 0.1), ("b", 0.2)]) is not None


def test_tolerans_GORECELI():
    """Mutlak eşik ölçek değişince anlamını yitirir: ₺15.576.000 ile %2,3 aynı eşiği
    paylaşamaz. Büyük ölçekte 1 birimlik sapma gürültü, küçük ölçekte kusurdur."""
    # Büyük ölçek: 1 birimlik sapma → göreceli olarak ~6e-8, tolerans içinde.
    assert viz.waterfall_spec(baslangic=0.0, bitis=15_576_000.0,
                              bilesenler=[("a", 15_575_999.0), ("b", 1.0)]) is not None
    # Küçük ölçek: aynı MUTLAK sapma → göreceli olarak 1.0, tolerans dışında.
    assert viz.waterfall_spec(baslangic=0.0, bitis=1.0,
                              bilesenler=[("a", 0.5), ("b", 1.5)]) is None


def test_NEGATIF_bilesenler():
    """Şelalenin asıl işi budur: bir etki artırır, diğeri azaltır."""
    spec = viz.waterfall_spec(baslangic=0.0, bitis=-40.0,
                              bilesenler=[("fiyat", 20.0), ("miktar", -60.0)])
    assert spec and spec["net"] == -40.0


def test_SIFIRDAN_FARKLI_baslangic():
    spec = viz.waterfall_spec(baslangic=100.0, bitis=150.0, bilesenler=[("a", 50.0)])
    assert spec and spec["start"]["value"] == 100.0 and spec["end"]["value"] == 150.0


def test_BOS_bilesen_grafik_uretmez():
    assert viz.waterfall_spec(baslangic=0.0, bitis=0.0, bilesenler=[]) is None


def test_birim_TASINIR():
    spec = viz.waterfall_spec(baslangic=0.0, bitis=1.0, bilesenler=[("a", 1.0)], birim="₺")
    assert spec["unit"] == "₺"


def test_spec_JSON_serilesebilir():
    import json

    assert json.dumps(viz.waterfall_spec(baslangic=0.0, bitis=1.0, bilesenler=[("a", 1.0)]))


# --- PVM zinciri: karar BACKEND'de --------------------------------------------

def test_PVM_raporu_SELALE_tasir(client):
    """Zincirin tamamı: PVM artıksız → `waterfall_spec` kapıyı geçer → `PvmReport.viz`
    dolar. Karar backend'de alınır (ADR-0024: grafik kararı LLM'e VERİLMEZ, frontend'e
    de bırakılmaz)."""
    from tests.conftest import ask

    # PVM `parti`de toplam_ciro ⇄ toplam_agirlik_kg çifti üstünde BEYAN EDİLMİŞ; ölçü
    # uymayan bir sorgu (yalnız kg) ayrışma üretmez ve test sessizce atlanırdı.
    ilk = ask(client, "bu yıl makine bazında ciro")
    cq = ilk.get("cube_query")
    assert cq, f"ciro sorgusu kurulamadı: {ilk.get('note')!r}"
    r = client.post("/ask/contribution",
                    json={"cube_query": cq, "mode": "yoy", "kind": "pvm"})
    assert r.status_code == 200, r.text
    d = r.json()
    if not d.get("pvm_raporlar"):
        pytest.skip(f"bu cube'da PVM beyanı yok: {d.get('note')!r}")

    for rap in d["pvm_raporlar"]:
        spec = rap.get("viz")
        assert spec, "PVM artıksız ama şelale üretilmedi"
        assert spec["kind"] == "waterfall"
        # Grafiğin İDDİASI: adımların toplamı nete varır.
        assert sum(s["value"] for s in spec["steps"]) == pytest.approx(spec["net"], rel=1e-6)


def test_PVM_selalesi_UC_ETKIYI_tasir(client):
    """Fiyat · miktar · birleşik — üçü de görünmeli. Biri eksikse ayrışma artıksız
    OLMAZ ve kapı zaten reddederdi; bu test etiketlerin de doğru olduğunu kilitler."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında ciro")
    r = client.post("/ask/contribution",
                    json={"cube_query": ilk["cube_query"], "mode": "yoy", "kind": "pvm"})
    d = r.json()
    if not d.get("pvm_raporlar"):
        pytest.skip("PVM beyanı yok")
    etiketler = [s["label"] for s in d["pvm_raporlar"][0]["viz"]["steps"]]
    assert etiketler == ["fiyat", "miktar", "birleşik"]
