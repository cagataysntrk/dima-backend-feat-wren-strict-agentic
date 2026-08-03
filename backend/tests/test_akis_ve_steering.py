"""FAZ S — AŞAMA AKIŞI + STEERING, dürüst fiyatıyla.

## Plan ne diyordu, ölçüm ne gösterdi

Plan: *"`/ask/jobs` bir POLLING job, akış DEĞİL; SSE/WebSocket kodda SIFIR. Bu faz bir
TAŞIMA KATMANI işidir."* Ölçüldü — SSE/WebSocket gerçekten **0 satır**dı. Ama *"canlı
düşünme adımları"* deneyimi **zaten vardı**: `AskJob.trace_json` biriken adımları
taşıyor, `pollAskJob(onProgress)` onları 1,5 sn'de bir çekiyor, `ChatPanel.liveTrace`
gösteriyor.

Yani eksik olan **ikinci bir gerçeklik değil**, o gerçekliğin **anında** iletilmesiydi.
Canlı süre ölçümü kararı verdi: deterministik yol ~100–800 ms (akış gereksiz), **LLM yolu
2,8–5,5 sn** — sessizlik tam orada.

## İki değişmez bu süitte kilitlenir

1. **Akış İKİNCİ BİR HAKİKAT ÜRETMEZ** — poll ucu ile aynı satırı, aynı okuyucudan okur.
   İki ayrı okuyucu olsaydı tenant izolasyonu iki yerde yazılır, biri unutulurdu.
2. **STEERING'DE CEVAP KAYBOLMAZ** — geç gelen cevap geçmişe yazılır ama aktif bağlamı
   ele geçirmez, ve kullanıcıya NEDEN öyle olduğu söylenir.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

FE = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"
ASK = pathlib.Path(__file__).resolve().parents[1] / "app" / "routers" / "ask.py"


# --- 1) AKIŞ İKİNCİ BİR GERÇEKLİK DEĞİL --------------------------------------------

def test_AKIS_ve_POLL_AYNI_OKUYUCUYU_kullanir():
    """Akış bir TAŞIMADIR. İki uç aynı satırı iki farklı biçimde okusaydı zamanla
    ayrışırlardı — ve "ne yapıyor" sorusunun iki anlatısı doğardı, biri yalan söylerdi."""
    agac = ast.parse(ASK.read_text(encoding="utf-8"))
    cagiranlar = {n.name for n in ast.walk(agac)
                  if isinstance(n, ast.FunctionDef)
                  and any(isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_job_durum_oku"
                          for c in ast.walk(n))}
    assert {"ask_job_status", "ask_job_stream"} <= cagiranlar, cagiranlar
    assert sum(1 for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)
               and n.name == "_job_durum_oku") == 1, "ikinci bir okuyucu doğmuş"


def test_AKIS_TENANT_IZOLASYONUNU_devralir(client):
    """Ortak okuyucu tenant kontrolünü içerir; akış ucu onu ATLAYAMAZ."""
    import inspect

    from app.routers.ask import _job_durum_oku

    govde = inspect.getsource(_job_durum_oku)
    assert "tenant" in govde and "404" in govde


def test_AKIS_UCU_BILINMEYEN_ISI_REDDEDER(client):
    r = client.get("/ask/jobs/bozuk-kimlik/stream")
    assert r.status_code == 400, r.text


def test_AKIS_SONSUZ_ACIK_BAGLANTI_BIRAKMAZ():
    """Poll ucunun `MAX_POLLS` sınırıyla AYNI disiplin — süresiz akan bir bağlantı,
    sunucu tarafında sessizce biriken bir sızıntıdır."""
    from app.routers import ask as m

    assert m._AKIS_AZAMI_SANIYE > 0 and m._AKIS_ARALIK_SANIYE > 0
    assert m._AKIS_ARALIK_SANIYE < 1.5, (
        "akış aralığı poll'dan (1,5 sn) hızlı olmalı — yoksa akışın varlık nedeni yok")


# --- 2) GÜVENLİK DEĞİŞMEZİ: EventSource KULLANILMADI -------------------------------

def test_EVENTSOURCE_KULLANILMIYOR():
    """`EventSource` Authorization başlığı GÖNDEREMEZ; tek yolu token'ı URL'e koymaktır
    ve o token sunucu loglarına/tarayıcı geçmişine sızar. Deponun açık kuralı: *"access
    token memory'de, localStorage'a ASLA"*. SSE BİÇİMİ korunur, taşıma `fetch`tir."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    metin = "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                      for f in FE.rglob("*.ts*"))
    assert "new EventSource" not in metin, \
        "EventSource kullanılmış — token URL'e taşınıyor olabilir (güvenlik gerilemesi)"
    assert "/stream" in metin, "akış ucu frontend'den HİÇ çağrılmıyor (yetim uç)"
    assert "Authorization" in metin


def test_AKIS_KURULAMAZSA_POLLA_DUSULUR():
    """Yetenek kaybı YOK: eski tarayıcı / ters vekil tamponlaması / ağ hatasında
    davranış eski hâline döner, cevap yine gelir."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    src = (FE / "lib" / "api-client.ts").read_text(encoding="utf-8")
    i, j = src.index("streamAskJob"), src.index("pollAskJob(data.job_id")
    assert i < j, "akış denenmeden poll'a düşülüyor"
    assert "if (akan) return akan;" in src


# --- 3) STEERING: CEVAP KAYBOLMAZ, BAĞLAM ELE GEÇİRİLMEZ ---------------------------

def test_STEERING_SIRA_NUMARASI_var():
    """Ölçülen kusur: komposer koşarken kilitli değil (bilerek), iki istek aynı anda
    uçabiliyor ve YAVAŞ olan SONRA çözülünce `onSuccess` bağlamı GERİ ALIYOR —
    kullanıcı yön veriyor, sistem sessizce eski cevaba dönüyor."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    src = (FE / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "istekSirasi" in src, "istek sıra numarası yok — steering kapısı kurulmamış"
    assert "steering_golgede" in src


def test_STEERING_GEC_GELEN_CEVAP_KAYBOLMAZ():
    """*"Sessiz iptal YOK"*: geç gelen cevap geçmişe YAZILIR, yalnız aktif bağlamı
    ele geçirmez."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    src = (FE / "app" / "page.tsx").read_text(encoding="utf-8")
    i = src.index("if (!guncel)")
    blok = src[i:i + 400]
    assert "addHistory(data)" in blok, "geç gelen cevap sessizce YUTULUYOR"
    assert "setContextCq" not in blok and "setActiveThreadId" not in blok, \
        "geç gelen cevap aktif bağlamı ele geçiriyor — steering çalışmıyor"


def test_STEERING_KULLANICIYA_SOYLENIYOR():
    """Sessizce göstermek *"neden eski rapor geri geldi?"* sorusunu doğururdu."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "steering_golgede" in kart and "yeni bir soru sorarken" in kart


def test_STEERING_ALANI_BACKENDDEN_GELMIYOR():
    """`steering_golgede` İSTEMCİ kararıdır. Backend'e sızarsa sunucu, istemcinin
    zamanlama bilgisine sahip olduğunu iddia etmiş olur — sahip olmadığı bir bilgi."""
    from app.schemas import AskResponse

    assert "steering_golgede" not in AskResponse.model_fields
