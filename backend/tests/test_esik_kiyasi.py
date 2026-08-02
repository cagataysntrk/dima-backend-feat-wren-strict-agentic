"""FAZ G3 — EŞİK KIYASI: hedef uydurulmaz, kullanıcının KENDİ sınırı okunur.

## Ölçülen durum (2 Ağustos 2026)

Planın G3 kompozisyonu bir *"hedef/eşik kıyası"* istiyor. Ölçüldü: cube metadata'sında
`target:`/`hedef:` diye bir beyan **hiçbir cube'da YOK**. Demo için hedef uydurmak,
`pvm:` eşleştirmesinde bilinçle reddedilen şeyin aynısı olurdu — GÜVENLE YANLIŞ bir sayı
(*"hedefin %12 altındasın"*) ve kullanıcı onu sorgulamaz.

Ama gerçek, **beyan edilmiş** bir eşik kaynağı zaten var: kullanıcının kendi kurduğu
alarmlar. `fire_kg > 30` alarmını kuran kişi *"benim için kritik sınır bu"* demiş olur.

## Neden bu testler

1. **Aynı matematik.** Ekrandaki uyarı ile e-postadaki alarm AYNI `check_threshold`'u
   kullanmalı; ayrı yazılsalardı "e-postada uyarı gelirken ekranda gelmeyen" bir gün
   gelirdi (I4'te ölçülen sadakat kusurunun aynısı, uyarı tarafında).
2. **Sessizlik bir karardır.** Eşiğin rahatça altında kalmak SUSAR — "eşiğin %40
   altındasın" her cevaba eklenirse asıl uyarılar okunmaz olur.
3. **Anomali alarmı eşik DEĞİLDİR.** `method=zscore` bir sınır değil baseline'dan öğrenen
   bir istatistiktir ve `interpret._signals` onu zaten koşuyor — ikisini karıştırmak aynı
   şeyi iki kez söylerdi.
4. **Tanımsız sayı üretilmez.** `value <= 0` eşikte "yüzde olarak yaklaşmak" tanımsızdır.
"""

from __future__ import annotations

import pytest

from app.interpret import interpret
from app.schedules import (
    YAKLASMA_ORANI,
    esik_sinyalleri,
    kullanicinin_esikleri,
)


class _SahteStore:
    def __init__(self, tanimlar):
        self._t = tanimlar

    def list(self):
        return self._t


def _sched(**kw):
    d = {"id": "s-1", "label": "fire takibi", "enabled": True,
         "cube_query": {"cube": "uretim", "measures": ["fire_kg"]},
         "threshold": {"measure": "fire_kg", "op": "gt", "value": 30.0}}
    d.update(kw)
    return d


# --- KAYNAK SEÇİMİ: hangi alarmlar eşik sayılır? ---------------------------------

def test_KULLANICININ_esigi_bulunur():
    e = kullanicinin_esikleri(_SahteStore([_sched()]), "uretim", ["fire_kg"])
    assert e == [{"measure": "fire_kg", "op": "gt", "value": 30.0, "label": "fire takibi"}]


def test_ANOMALI_alarmi_esik_SAYILMAZ():
    """`method=zscore` bir SINIR değil, baseline'dan öğrenen bir istatistiktir ve
    `interpret._signals`'ın anomali dalı zaten AYNI motoru koşuyor. Eşik saymak, aynı
    şeyi iki kez söylemek olurdu."""
    s = _sched(threshold={"measure": "fire_kg", "method": "zscore", "k": 2.0})
    assert kullanicinin_esikleri(_SahteStore([s]), "uretim", ["fire_kg"]) == []


def test_BASKA_CUBE_un_esigi_sizmaz():
    s = _sched(cube_query={"cube": "enerji", "measures": ["fire_kg"]})
    assert kullanicinin_esikleri(_SahteStore([s]), "uretim", ["fire_kg"]) == []


def test_KAPALI_zamanlama_esik_saymaz():
    assert kullanicinin_esikleri(_SahteStore([_sched(enabled=False)]),
                                 "uretim", ["fire_kg"]) == []


def test_BASKA_TENANT_esigi_sizmaz():
    """Tenant-RLS eşik kıyasında da geçerli: başka kiracının koyduğu sınır bu kullanıcının
    cevabında görünemez."""
    s = _sched(tenant_id="t-DIGER")
    assert kullanicinin_esikleri(_SahteStore([s]), "uretim", ["fire_kg"],
                                 tenant_id="t-BEN") == []


def test_SAYIYA_cevrilemeyen_esik_ATLANIR():
    s = _sched(threshold={"measure": "fire_kg", "op": "gt", "value": "otuz"})
    assert kullanicinin_esikleri(_SahteStore([s]), "uretim", ["fire_kg"]) == []


def test_STORE_patlarsa_bos_doner():
    class _Patlak:
        def list(self):
            raise RuntimeError("db yok")

    assert kullanicinin_esikleri(_Patlak(), "uretim", ["fire_kg"]) == []


# --- SİNYAL: ihlal · yaklaşma · SESSİZLİK ----------------------------------------

_ESIK = [{"measure": "fire_kg", "op": "gt", "value": 30.0, "label": "fire takibi"}]


def test_IHLAL_critical():
    s = esik_sinyalleri([{"makine": "M-07", "fire_kg": 45.0}], _ESIK, {"fire_kg": "kg"})
    assert len(s) == 1
    assert s[0]["severity"] == "critical" and s[0]["kind"] == "threshold"
    assert "45" in s[0]["text"] and "fire takibi" in s[0]["text"]


def test_YAKLASMA_warning():
    """Eşiği aşmadan haber vermek, "reaktif değil proaktif" vaadinin (öz #6) en ucuz
    karşılığıdır."""
    s = esik_sinyalleri([{"makine": "M-07", "fire_kg": 29.0}], _ESIK)
    assert len(s) == 1 and s[0]["severity"] == "warning"
    assert "yaklaşıyor" in s[0]["text"]


def test_RAHAT_alanda_SUSAR():
    """"Eşiğin %40 altındasın" her cevaba eklenirse sinyal gürültüye döner ve ASIL
    uyarılar okunmaz olur. Sessizlik burada bir karardır."""
    assert esik_sinyalleri([{"fire_kg": 10.0}], _ESIK) == []


def test_YAKLASMA_BANDI_orana_bagli():
    """Bant `YAKLASMA_ORANI` ile tanımlıdır; sabit bir sayı gizlenmez."""
    sinir = 30.0 * YAKLASMA_ORANI
    assert esik_sinyalleri([{"fire_kg": sinir + 0.1}], _ESIK)
    assert esik_sinyalleri([{"fire_kg": sinir - 0.1}], _ESIK) == []


def test_LT_esiginde_yon_TERS():
    """`lt` eşiğinde tehlike AŞAĞIDADIR: 30'un altına düşmemesi istenen bir ölçüde 31
    yaklaşmadır, 10 ihlaldir."""
    esik = [{"measure": "oee", "op": "lt", "value": 30.0, "label": "oee tabanı"}]
    assert esik_sinyalleri([{"oee": 10.0}], esik)[0]["severity"] == "critical"
    assert esik_sinyalleri([{"oee": 31.0}], esik)[0]["severity"] == "warning"
    assert esik_sinyalleri([{"oee": 90.0}], esik) == []


def test_SIFIR_veya_NEGATIF_esikte_yaklasma_URETILMEZ():
    """0'a %90 yaklaşmak nedir? Tanımsız bir sayı üretmektense sinyal verilmez —
    `contribution`ın `net_pay = None` disiplininin aynısı. İhlal yine bildirilir."""
    esik = [{"measure": "kar", "op": "lt", "value": 0.0, "label": "zarar sınırı"}]
    assert esik_sinyalleri([{"kar": 5.0}], esik) == []       # yaklaşma HESAPLANMAZ
    assert esik_sinyalleri([{"kar": -3.0}], esik)[0]["severity"] == "critical"


def test_SAYISAL_OLMAYAN_deger_patlatmaz():
    assert esik_sinyalleri([{"fire_kg": None}, {"fire_kg": "x"}], _ESIK) == []


def test_ALARM_KOSUMUYLA_ayni_matematik():
    """Ekrandaki uyarı ile e-postadaki alarm AYNI `check_threshold`'u kullanmalı. Ayrı
    yazılsalardı, e-postada uyarı gelirken ekranda gelmeyen bir gün gelirdi."""
    import inspect

    from app import schedules

    govde = inspect.getsource(schedules.esik_sinyalleri)
    assert "check_threshold" in govde, "eşik matematiği İKİNCİ kez yazılmış"


# --- ENTEGRASYON: `interpret` sinyali taşıyor mu? --------------------------------

def test_INTERPRET_esik_sinyalini_ONE_koyar():
    """Kullanıcının kendi sınırı, sistemin çıkardığı sinyallerden ÖNCE gelir: en somut
    ve en az yorum gerektiren bilgidir."""
    r = {"columns": ["makine", "fire_kg"],
         "rows": [{"makine": f"M-{i}", "fire_kg": 10.0} for i in range(1, 5)]
                 + [{"makine": "M-9", "fire_kg": 90.0}],
         "row_count": 5}
    out = interpret(r, {"cube": "uretim", "measures": ["fire_kg"], "dimensions": ["makine"]},
                    units={"fire_kg": "kg"}, esikler=_ESIK)
    kinds = [s["kind"] for s in (out.get("signals") or [])]
    assert kinds and kinds[0] == "threshold"


def test_INTERPRET_esiksiz_DAVRANIS_degismez():
    """Geriye uyum: eşik verilmezse yorum bugünküyle birebir aynı olmalı."""
    r = {"columns": ["makine", "fire_kg"],
         "rows": [{"makine": "A", "fire_kg": 10.0}, {"makine": "B", "fire_kg": 90.0}],
         "row_count": 2}
    cq = {"cube": "uretim", "measures": ["fire_kg"], "dimensions": ["makine"]}
    assert interpret(r, cq) == interpret(r, cq, esikler=[])


@pytest.mark.parametrize("bozuk", [[{"measure": "fire_kg"}], [{}]])
def test_INTERPRET_bozuk_esikte_YORUMU_dusurmez(bozuk):
    """Sinyal best-effort'tur: eksik alanlı bir eşik yüzünden TÜM yorumu kaybetmek,
    yardımcı bir katman için orantısız olurdu."""
    r = {"columns": ["m", "fire_kg"], "rows": [{"m": "A", "fire_kg": 1.0}], "row_count": 1}
    out = interpret(r, {"cube": "uretim", "measures": ["fire_kg"]}, esikler=bozuk)
    assert out and out.get("summary")


# --- TEK KAPANIŞ ZİNCİRİ: her yol bu kıyası alıyor mu? ---------------------------

def test_ANSWER_ZINCIRI_esikleri_besliyor():
    """`_maybe_interpret` TEK kapanış zincirinin parçasıdır: /ask · /cube · /report ·
    drill · katkı HEPSİ bu kıyası bedava alır. Ayrı ayrı bağlansaydı biri unutulurdu —
    bu depoda altı kez ölçülmüş desen."""
    import inspect

    from app import answer

    govde = inspect.getsource(answer._maybe_interpret)
    assert "kullanicinin_esikleri" in govde
    assert "esikler=esikler" in govde, "eşikler `interpret`e geçirilmiyor"
    assert "tenant_id" in govde, "tenant-RLS eşik kıyasında uygulanmıyor"
