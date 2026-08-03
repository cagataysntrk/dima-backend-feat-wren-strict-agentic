"""FAZ D2 — BEŞİNCİ KONUŞMA TÜRÜ: *"bunu analiz et / yorumla / özetle"*.

## Ölçülen ölü uç (3 Ağustos 2026), bir `oee` raporu üstünde

`followup.py` konuşma sınıfını **dört** türle tanımlıyordu (`NEDEN` · `NORMAL` ·
`NE_YAPMALI` · `ISARET`). Kullanıcının **en doğal** cümlesi hiçbirine girmiyordu —
altı ifadenin **beşi** duvara çarpıyordu:

    "bunu analiz et"     → *"«bunu» yerine «gunu» mi demek istedin?"*      (saçma)
    "değerlendir"        → *"«degerlendir» yerine «degree» mi?"*           (saçma)
    "yorumlar mısın"     → *"Bu takip mesajını önceki raporla ilişkilendiremedim"*
    "özetle"             → aynı ölü uç
    "bu grafiği açıkla"  → aynı ölü uç
    "bu neden böyle?"    → ✅ (TUR_NEDEN zaten vardı)

Yani `followup.py`'nin **kendi docstring'inde tarif ettiği** ölü uç, bir tür eksik
olduğu için yaşamaya devam ediyordu.

## Sınıfın tanımı DEĞİŞMEDİ

*"YENİ CEVAP ÜRETMEZ, VAR OLANI AÇAR."* Bu dal `prev_cq`'yu **aynen** yeniden çalıştırır
(`cube_query` DEĞİŞMEZ) ve `seal()` zinciri yorumu, `t2_anlatici` açıksa guard'lı
anlatıyı, chip'leri kendisi ekler.

## Üç kusur ölçülerek bulundu ve düzeltildi

1. **Konu değişimi çalınıyordu.** `analizini` kalıbı *"fire analizini yap"*ı da yakalıyordu
   — eldeki raporu açmak DEĞİL, yeni konu istemek. Dosyanın kendi zamir/kısalık disiplini
   (`TUR_NEDEN`/`TUR_ISARET`) bu türe de uygulandı.
2. **ÇİFT MÜHÜR.** İlk sürüm `_answer_from_cube_query` çağırıyordu; o `_finish`'i kendi
   içinde uygular ve çağıran da uygular → ölçüldü: **tek tur İKİ telemetri satırı**
   (çift audit · çift PII maskesi). Kardeş dal (`TUR_NORMAL`) mühürsüz döner; bu da öyle.
3. **YETİM ALAN (frontend).** `suggestions` yalnız `ReportPanel`'in NOT dalında render
   ediliyordu; RAPOR kartında hiç okunmuyordu → üç devam chip'i **ekranda görünmüyordu**.
   `test_cevap_alani_yetim_degil` bunu göremedi: alan adı frontend'de bir yerde geçiyordu,
   kapının kör noktası *"hangi RENDER YOLUNDA"* sorusuydu.
"""

from __future__ import annotations

import json
import pathlib

import pytest
from sqlmodel import Session, select

from app import followup
from control_plane.db import engine
from control_plane.models import InteractionLog

FE = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"

ANLAT_IFADELERI = ["bunu analiz et", "yorumlar mısın", "özetle",
                   "bu grafiği açıkla", "değerlendir", "bunu yorumla"]


# --- SINIFLANDIRMA ------------------------------------------------------------------

@pytest.mark.parametrize("soru", ANLAT_IFADELERI)
def test_ANLAT_turu_TANINIYOR(soru):
    from app.cube_router import _norm

    n = followup.sinifla(_norm(soru), baglam_var=True)
    assert n.sinif == followup.SINIF_KONUSMA and n.tur == followup.TUR_ANLAT, \
        f"{soru!r} → sınıf={n.sinif} tür={n.tur} (beklenen konusma/anlat)"


def test_KONU_DEGISIMI_calinmiyor():
    """`analizini` kalıbı *"fire analizini yap"*ı yakalamamalı — o eldeki raporu açmak
    değil YENİ konu istemektir. Yanlış-pozitif kullanıcının sorusunu YUTARDI."""
    n = followup.sinifla("fire analizini yap", baglam_var=True)
    assert n.sinif == followup.SINIF_YENI, f"konu değişimi çalındı: {n.sinif}/{n.tur}"


def test_YAPISAL_onceligi_KORUNUYOR():
    """*"makine bazında"* yeni sayı ister; konuşma bir sonraki turda hâlâ mümkündür ama
    yanlış sayı geri alınamaz."""
    assert followup.sinifla("makine bazinda", baglam_var=True).sinif == followup.SINIF_YAPISAL


def test_BAGLAM_YOKKEN_konusma_OLMAZ():
    assert followup.sinifla("bunu analiz et", baglam_var=False).sinif == followup.SINIF_YENI


# --- DAVRANIŞ: eldeki rapor AÇILIYOR -----------------------------------------------

@pytest.mark.parametrize("soru", ANLAT_IFADELERI)
def test_ANLAT_ELDEKI_raporu_ACIYOR(client, soru):
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında oee")
    cq = ilk.get("cube_query")
    assert cq, "ön koşul: ilk soru bir rapor üretmeli"
    d = ask(client, soru, cube_query=cq, history=["bu yıl makine bazında oee"])
    assert d.get("source") == "cube", f"{soru!r} → source={d.get('source')} (duvara çarptı)"
    assert json.dumps(d.get("cube_query"), sort_keys=True) == json.dumps(cq, sort_keys=True), \
        "cube_query DEĞİŞTİ — bu sınıf YENİ CEVAP ÜRETMEZ, var olanı açar"


def test_ANLAT_devam_chipleri_URETIYOR(client):
    """Konuşma kendi kendini beslemeli: üç chip de ZATEN çalışan konuşma türleri."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında oee")
    d = ask(client, "bunu analiz et", cube_query=ilk.get("cube_query"),
            history=["bu yıl makine bazında oee"])
    etiketler = [s["label"] for s in (d.get("suggestions") or [])]
    assert len(etiketler) >= 2, f"devam chip'i yok: {etiketler}"
    for beklenen in ("Neden böyle?", "Normal mi?", "Ne yapmalıyız?"):
        assert beklenen in etiketler, f"{beklenen!r} chip'i yok"


def test_ANLAT_yorum_ve_ozet_TASIYOR(client):
    """Sözleşme #2'nin deterministik tabanı. ⚠️ Sayı ÖLÇÜLEREK konuldu: `interpret()`
    tek satırlık toplamda **1**, kırılımlı raporda **2** olgu üretiyor. İlk yazdığım
    *"≥3"* ölçütü ölçülmeden konmuştu — bu oturumda dördüncü kez ölçütün kendisi kusurlu
    çıktı."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında oee")
    d = ask(client, "bunu analiz et", cube_query=ilk.get("cube_query"),
            history=["bu yıl makine bazında oee"])
    y = d.get("interpretation") or {}
    assert y.get("summary"), "deterministik özet yok"
    assert len(y.get("facts") or []) >= 2, f"kırılımlı raporda olgu sayısı: {y.get('facts')}"
    assert (d.get("result") or {}).get("row_count"), "sonuç tablosu kayboldu"


def test_ANLAT_Discoverye_DUSMUYOR(client):
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında oee")
    d = ask(client, "özetle", cube_query=ilk.get("cube_query"),
            history=["bu yıl makine bazında oee"])
    assert not str(d.get("source") or "").startswith(("llm", "rule")), \
        "konuşma turu Discovery'ye düştü — bağlamsız ham SQL, ölü tablo"


# --- ÇİFT MÜHÜR: tek tur, tek telemetri satırı --------------------------------------

@pytest.fixture
def telemetri_acik(monkeypatch):
    from app import answer
    from app.config import get_settings

    gercek = get_settings()

    class _Acik:
        def __getattr__(self, ad):
            return True if ad == "interaction_log" else getattr(gercek, ad)

    monkeypatch.setattr(answer, "get_settings", lambda: _Acik())


def test_TEK_TUR_TEK_telemetri_satiri(client, telemetri_acik):
    """`_answer_from_cube_query` `_finish`'i KENDİ İÇİNDE uygular; çağıran da uygular.
    Ölçüldü: tek tur **iki** satır yazıyordu — çift audit, çift PII maskesi, çift yorum."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında oee")
    with Session(engine) as s:
        n1 = len(s.exec(select(InteractionLog)).all())
    ask(client, "bunu analiz et", cube_query=ilk.get("cube_query"),
        history=["bu yıl makine bazında oee"])
    with Session(engine) as s:
        n2 = len(s.exec(select(InteractionLog)).all())
    assert n2 - n1 == 1, f"ÇİFT MÜHÜR: tek tur {n2 - n1} telemetri satırı yazdı"


def test_ANLAT_dali_ANSWER_FROM_CUBE_QUERY_kullanmiyor():
    """Kapının yapısal hâli: o yardımcı mühürlü döner ve bu dal mühürsüz dönmek zorunda."""
    import inspect

    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod.ask)
    i = govde.index("if tur == followup.TUR_ANLAT:")
    # ⚠️ YORUM SATIRLARI ELENİR: ilk sürüm KENDİ açıklama yorumumu ("bu yardımcı
    # KULLANILMAZ, çünkü…") yakalayıp testi kırdı — bu oturumda beşinci kez bir testim
    # METNİ davranış sandı. Ölçülen şey ÇAĞRININ kendisi olmalı.
    pencere = "\n".join(s for s in govde[i:i + 2400].splitlines()
                        if not s.strip().startswith("#"))
    assert "_answer_from_cube_query(" not in pencere, \
        "ANLAT dalı mühürlü yardımcıyı ÇAĞIRIYOR — çift mühür geri geldi"


# --- FRONTEND: devam chip'i GERÇEKTEN render ediliyor -------------------------------

def test_DEVAM_CHIPI_rapor_kartinda_RENDER_ediliyor():
    """⚠️ Ölçülen yetim alan: `suggestions` yalnız `ReportPanel`'in NOT dalında
    render ediliyordu; rapor kartında hiç okunmuyordu → chip'ler EKRANDA YOKTU.
    `test_cevap_alani_yetim_degil` bunu göremez (alan adı bir yerde geçiyor); kapının
    kör noktası *"hangi render yolunda"* sorusudur."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "item.suggestions" in kart, \
        "ReportCard `suggestions` OKUMUYOR — devam chip'leri görünmez"
    assert "devam sorusu" in kart, "devam chip'leri başlıksız/ayırt edilemez"
    assert "onReply(threadId, index, s.query)" in kart, \
        "chip tıklaması takip sorusu olarak gönderilmiyor"


def test_DEVAM_CHIPI_next_steps_ile_KARISMIYOR():
    """İkisi FARKLI eylemdir: `next_steps` sorguyu DÜZENLER (`cube_query` taşır),
    `suggestions` bir SORU sorar. Aynı kutuya konursa kullanıcı hangisinin yeni sayı
    getireceğini bilemez."""
    if not FE.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert kart.index("devam sorusu") < kart.index("sonraki adım"), \
        "iki blok ayrı başlıklarla ve ayrı sırada durmalı"
