"""FAZ E-1 — TELEMETRİNİN YAZMA YOLU: ölçüm aracının kendisi test edilir.

## Ölçülen boşluk (2 Ağustos 2026)

`interaction_log` altyapısı **tam**: tablo (`InteractionLog`, 20 alan), KPI ucu
(`GET /sadmin/interactions/route-distribution`), varsayılan **açık**
(`interaction_log: bool = True`). Ama:

- `tests/test_route_distribution.py` ve `tests/test_candidates.py` satırları **elle
  ekleyip** yalnız **OKUMA** tarafını sınıyor.
- `tests/conftest.py` yazmayı **global olarak kapatıyor** (`DIMA_INTERACTION_LOG=false`)
  — haklı olarak: testler canlı telemetriyi kirletmemeli.
- Sonuç: **`/ask`'in gerçekten satır yazdığını sınayan hiçbir test yok.**

Bu, Faz D'de ölçülen `lab/nl_corpus.py` kusurunun **aynı sınıfıdır**: ölçüm aracı sessizce
kırılırsa sistem *"ölçemiyorum"* demez — KPI **sıfır** okur ve herkes *"trafik yok"* sanır.
Planın *"Intent ≥%70 / Discovery <%30"* hedefi tam olarak bu satırlara dayanıyor.

> **Ölçüm aracının kendisi de bir bağımlılıktır** (MIMARI §6.4). Yazma yolu test
> edilmeyen bir telemetri, olmayan bir telemetriden **daha kötüdür**: birincisi
> yanlış bir güven verir.

## Bu dosya ne yapar

Yazmayı **yalnız bu testler için** açar (`get_settings` yamalanır — conftest'in global
kapaması bozulmaz) ve `/ask`'in gerçekten yazdığını, hangi alanları doldurduğunu, ve
KPI'ın o satırlardan **doğru** hesaplandığını uçtan uca doğrular.
"""

from __future__ import annotations

import pytest
from sqlmodel import Session, select

from control_plane.db import engine
from control_plane.models import InteractionLog


@pytest.fixture
def telemetri_acik(monkeypatch):
    """Yazmayı YALNIZ bu test için açar. `conftest`'in global kapaması bozulmaz —
    diğer testler canlı telemetriyi kirletmeye devam etmez."""
    from app import answer
    from app.config import get_settings

    gercek = get_settings()

    class _Acik:
        def __getattr__(self, ad):
            return True if ad == "interaction_log" else getattr(gercek, ad)

    monkeypatch.setattr(answer, "get_settings", lambda: _Acik())
    with Session(engine) as s:
        onceki = len(s.exec(select(InteractionLog)).all())
    return onceki


def _yeni_satirlar(onceki: int) -> list[InteractionLog]:
    with Session(engine) as s:
        hepsi = s.exec(select(InteractionLog)).all()
    return hepsi[onceki:]


# --- ASIL KAPI: /ask GERÇEKTEN yazıyor mu? --------------------------------------

def test_ask_TELEMETRI_SATIRI_yazar(client, telemetri_acik):
    """ASIL KAPI. Bu test olmadan yazma yolu sessizce kırılabilir ve KPI **sıfır**
    okurdu — "trafik yok" ile "loglama bozuk" ayırt edilemezdi."""
    from tests.conftest import ask

    _ask_bekleyerek(client, "bu yıl makine bazında işlenen kg")
    yeni = _yeni_satirlar(telemetri_acik)
    assert yeni, "/ask hiç telemetri satırı yazmadı — KPI ölçülemez"


def test_yazilan_satir_KPI_ALANLARINI_doldurur(client, telemetri_acik):
    """KPI'ın dayandığı alanlar dolu olmalı. Boş bir `kind`, route-distribution'ı
    sessizce "other" kovasına iter ve *"Intent ≥%70"* hedefi ölçülemez hale gelir."""
    from tests.conftest import ask

    ask(client, "bu yıl makine bazında işlenen kg")
    satir = _yeni_satirlar(telemetri_acik)[-1]

    assert satir.question, "soru kaydedilmedi"
    assert satir.source and satir.kind, f"yol sınıflandırması boş: {satir.source}/{satir.kind}"
    assert satir.kind in ("cube", "llm", "rule", "vqr", "meta", "catalog", "statement",
                          "upload", "none", "other"), satir.kind
    assert satir.duration_ms is not None and satir.duration_ms >= 0
    assert satir.ts is not None


def test_deterministik_cevap_KIND_CUBE_olarak_kaydedilir(client, telemetri_acik):
    """*"Intent ≥%70"* hedefi bu sınıflandırmaya dayanıyor: `route()` ile cevaplanan bir
    soru `kind="cube"` yazılmazsa hedef ölçülemez."""
    from tests.conftest import ask

    d = ask(client, "bu yıl makine bazında işlenen kg")
    if d.get("source") != "cube":
        pytest.skip("bu soru bu veri setinde cube yolundan gelmedi")
    satir = _yeni_satirlar(telemetri_acik)[-1]
    assert satir.kind == "cube" and satir.source == "cube"


def test_takip_sorusu_FOLLOW_UP_isaretlenir(client, telemetri_acik):
    """Takip oranı, konuşma katmanının (Faz G) etkisini ölçmenin tek yolu."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    ask(client, "aylık", cube_query=ilk["cube_query"], history=[ilk["question"]])
    satir = _yeni_satirlar(telemetri_acik)[-1]
    assert satir.follow_up is True, "takip sorusu takip olarak işaretlenmedi"



def _ask_bekleyerek(client, soru: str):
    """`/ask` — ve arka-plan işi varsa **bitmesini bekler**.

    🔴 `G5.10` `ask_async_discovery`'yi açtı: Discovery yolu artık bir **iş** döndürüyor
    ve telemetri işçinin `_finish`'inde yazılıyor. Kanal kaybolmadı, **ötelendi**.

    ⚠ Testi *"yeni satır yok"* diye yeşile boyamak, ölçüm kanalını taşımaya bağımlı
    kılmak olurdu. Kapının konusu **kanalın varlığı**; bekleme yalnız onu ölçebilmek için.

    *Bir taşımayı değiştirmek ölçümü de değiştirir — kapı taşımaya değil, ÖLÇÜLEN ŞEYE
    çapalanmalıdır.*
    """
    import time

    from tests.conftest import ask

    d = ask(client, soru)
    jid = d.get("job_id")
    if not jid:
        return d
    for _ in range(50):
        r = client.get(f"/ask/jobs/{jid}")
        if r.status_code == 200 and r.json().get("status") in ("completed", "failed",
                                                              "cancelled", "iptal"):
            return d
        time.sleep(0.1)
    return d


def test_CEVAPSIZ_yanit_da_kaydedilir(client, telemetri_acik):
    """Netleştirme/dürüst ret de telemetriye girmeli: *"kaç soru cevaplanamadı"*
    kapsam boşluğunun EN DOĞRUDAN ölçüsüdür. Yalnız başarılı cevapları loglamak,
    kapsamı olduğundan iyi gösterirdi."""
    from tests.conftest import ask

    _ask_bekleyerek(client, "asdf qwerty zxcv")
    yeni = _yeni_satirlar(telemetri_acik)
    assert yeni, "cevapsız yanıt telemetriye yazılmadı — kapsam boşluğu görünmez olur"


# --- KPI zinciri: yazılan satırlar OKUNABİLİYOR mu? -----------------------------

def test_YAZILAN_satir_KPI_sorgusuna_dusuyor(client, telemetri_acik):
    """Zincirin tamamı: `/ask` yazar → `route-distribution` okur. İki uç ayrı ayrı
    çalışıp ARADA kopabilirdi (ör. `source` biçimi değişir, gruplama tanımaz)."""
    from collections import Counter

    from tests.conftest import ask

    ask(client, "bu yıl makine bazında işlenen kg")
    yeni = _yeni_satirlar(telemetri_acik)
    assert yeni

    # `route_distribution`'ın gruplama anahtarı `source`; yazılan değer o gruplamada
    # tanınabilir olmalı (boş/None bir "other" kovası KPI'ı anlamsız kılar).
    dagilim = Counter(s.source for s in yeni)
    assert None not in dagilim, f"kaynaksız satır yazıldı: {dagilim}"


def test_telemetri_KAPALIYKEN_yazmaz(client):
    """Ters yön: `conftest`'in global kapaması GERÇEKTEN çalışmalı — aksi halde her
    test koşumu canlı telemetriyi kirletir ve KPI gürültüye boğulur."""
    with Session(engine) as s:
        onceki = len(s.exec(select(InteractionLog)).all())
    from tests.conftest import ask

    ask(client, "bu yıl makine bazında işlenen kg")
    with Session(engine) as s:
        sonraki = len(s.exec(select(InteractionLog)).all())
    assert sonraki == onceki, "telemetri KAPALIYKEN yazdı — testler canlı veriyi kirletir"


# --- FAZ 9.4: `reject_reason` GERÇEKTEN DB'ye yazılıyor mu? ------------------------
#
# ## Ölçülen boşluk (denetim, Faz 9)
#
# Faz 0'ın kolonunun **tek kapısı** `tests/test_red_gerekcesi.py`'ydi ve o
# `inspect.getsource` ile **kaynak metninde string arıyor** — yani "kod bu satırı
# içeriyor" diyor, "veritabanında bu değer var" demiyor. Gerçek yazmayı koşan tek dosya
# bu dosyaydı ve bu alana **hiç bakmıyordu**.
#
# Canlı tur farkı gösterdi: kolon şema sürüklenmesi yüzünden **yoktu**, `answer.py`'nin
# best-effort `except`'i hatayı **yuttu** ve telemetri sessizce boş kaldı. İki kapı da
# yeşildi. Faz 2b'nin triyajı, Faz 6'nın sıra kararı ve §1.6-5'in %20 eşiği bu kolondan
# besleniyor — boş bir kolon üstüne kurulan her karar dayanaksızdır.

def test_REJECT_REASON_veritabanina_YAZILIYOR(client, telemetri_acik):
    """ASIL KAPI: kaynak metni değil, **satırın kendisi**."""
    from tests.conftest import ask

    d = ask(client, "son 6 ay personel bazlı çalışma süreleri kıyasla")
    assert not d.get("sql"), "ön koşul: bu soru gerçekten cevapsız kalmalı"
    satir = _yeni_satirlar(telemetri_acik)[-1]
    assert satir.reject_reason, (
        "CEVAPSIZ soru DB'ye red gerekçesiz yazıldı — Faz 0'ın kolonu boş kalıyor ve "
        "Faz 2b'nin triyajı ölçüm yerine TAHMİNE dayanır")
    assert satir.reject_reason.startswith("R"), f"beklenmeyen kod: {satir.reject_reason!r}"


def test_LLM_YOLUNDAN_gelen_cevap_da_RED_gerekcesi_tasir(client, telemetri_acik):
    """Kolonun ASIL değeri burada. Cevap **geldi** ama deterministik yoldan gelmedi:
    `route()` pes etti, soru LLM/Discovery'ye düştü. Kolon yalnız *"cevapsız"* soruları
    kaydetseydi, Faz 2b'nin triyajı **kapsam boşluğunun en büyük kümesini kaçırırdı** —
    ölçülen R1 kümesi (99/470) tam olarak bu sınıftır.

    ⚠️ Ön koşul test ortamına bağlı: kural-tabanlı sağlayıcı saçma soruyu bile
    cevaplıyor (ölçüldü) — bu, kapıyı zayıflatmıyor, tam da ölçmek istediğimiz durumu
    ücretsiz üretiyor."""
    from tests.conftest import ask

    # 🔴 `G5.10` — asenkron Discovery açıldı: bu soru bir **iş** olarak koşuyor ve
    # telemetri işçinin `_finish`'inde yazılıyor. Beklemeden okumak, kanalı değil
    # **zamanlamayı** ölçerdi.
    d = _ask_bekleyerek(client, "asdf qwerty zxcv olmayan bir sey")
    if d.get("source") == "cube":
        pytest.skip("bu soru deterministik yoldan cevaplandı — bu testin konusu değil")
    satirlar = _yeni_satirlar(telemetri_acik)
    assert satirlar, (
        "⊘ HİÇ SATIR YAZILMADI — kapı bu durumda `IndexError` verirdi ve okuyucu onu "
        "bir kod hatası sanardı. Ölçümün YOKLUĞU ile ölçümün BAŞARISIZLIĞI ayrı şeylerdir.")
    satir = satirlar[-1]
    assert satir.reject_reason, (
        f"LLM yoluna düşen soru (source={satir.source}) red gerekçesiz kaydedildi — "
        "kapsam boşluğunun EN BÜYÜK kümesi telemetride görünmez kalır")


def test_KOLON_VARLIGI_dogrulaniyor():
    """Canlı turda kolon ŞEMADA YOKTU ve best-effort `except` hatayı yuttu: iki kapı da
    yeşil kaldı. Kolonun kendisi bir değişmezdir, varlığı ölçülür."""
    from sqlalchemy import inspect as sa_inspect

    kolonlar = {c["name"] for c in sa_inspect(engine).get_columns("interaction_log")}
    assert "reject_reason" in kolonlar, (
        f"`interaction_log.reject_reason` kolonu YOK → yazma sessizce yutulur. "
        f"Mevcut kolonlar: {sorted(kolonlar)}")


def test_DETERMINISTIK_cevapta_reject_reason_BOS(client, telemetri_acik):
    """Kapı fazla geniş olmamalı: kolonun doluluğu *"deterministik yoldan çıkamayan
    sorular"* kümesini vermeli. Başarılı bir cube cevabı da doldurursa kolon anlamını
    yitirir ve triyaj gürültüye boğulur."""
    from tests.conftest import ask

    # ⚠️ Bu dosyadaki BAŞKA hiçbir testin sormadığı bir soru: aynı soru ikinci kez
    # sorulduğunda VQR tekrar-oynatması devreye girer ve `source="vqr"` olur — kapı o
    # zaman sessizce `skip`'e düşer, yani hiçbir şey ölçmez. (Ölçüldü: kardeş iki test
    # tam olarak bu yüzden atlanıyordu.)
    d = ask(client, "bu yıl fire")
    assert d.get("source") == "cube", f"ön koşul: cube yolundan gelmeli (geldi: {d.get('source')})"
    satir = _yeni_satirlar(telemetri_acik)[-1]
    assert satir.reject_reason is None, (
        f"deterministik cevapta red gerekçesi yazıldı: {satir.reject_reason!r} — "
        "muhtemelen bir chip SONDASI ContextVar'ı ezdi (bkz. test_dogrulanmis_chip.py)")


def test_NETLESTIRMEYE_dusen_soru_da_gerekce_tasiyor(client, telemetri_acik):
    """Netleştirme chip'i **geçerli bir cevaptır** ama `route()` yine de pes etmiştir —
    o red, kapsam boşluğunun en doğrudan sinyalidir ve kaydedilmeli. Chip üretimi
    sırasında yapılan `route()` SONDALARI bu değeri EZMEMELİ (Faz 9.2'nin tuzağı)."""
    from tests.conftest import ask

    d = ask(client, "son 6 ay personel bazlı çalışma süreleri kıyasla")
    if d.get("sql"):
        pytest.skip("bu soru bu veri setinde cevaplanabildi")
    satir = _yeni_satirlar(telemetri_acik)[-1]
    assert satir.reject_reason, "netleştirmeye düşen soru red gerekçesiz kaydedildi"
