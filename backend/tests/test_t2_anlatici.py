"""FAZ 5 — T2 GUARDED LLM ANLATICI: *"LLM ÜSLUBU yazar, SAYIYI sistem koyar."*

## Neden bu faz en sona konuldu (§4.4)

Önce cevapların **doğru** gelmesi, sonra **güzel** anlatılması. "Güzel ama yanlış" bir
anlatı, şablon bir doğrudan **kötüdür** — süs, hatayı görünmez yapar. Bu yüzden fazın
sırası plana **kesin** yazılmıştı: `-0.5 · -1 · 0 · 1 · 2a` tamamlanmadan başlamaz.

## Bu dosyanın kilitlediği üç şey

**1. FAIL-CLOSED.** `narration_guard` **zorunlu** çıkış kapısıdır: her cümledeki her sayı
sonuç kümesiyle eşlenir; eşleşmeyen cümle **düşer**. Hiçbir cümle sağ kalmazsa anlatı
**hiç eklenmez** — deterministik `summary` yerinde kalır. En kötü durum *"süssüz ama
doğru"*, asla *"akıcı ama uydurma"*.

**2. ŞABLONU EZMEZ.** Anlatı `interpretation["narration"]`'a yazılır; `summary`/`facts`
**aynen kalır**. Bu, kullanıcının açıkça istediği iki şartın karşılığı: *"her zaman grafik
değil, bazen mesele sadece konuşmaktır"* korunur ve *"o konuşmayı grafiğe çevir"* çalışır
— çünkü altındaki yapı **hiçbir zaman silinmez** (Faz 0.5 bu şartın bir yerde ihlal
edildiğini ölçüp düzeltmişti: `gorunum_donusumu` 0/5 → 4/5).

**3. GİRDİ DAR.** Model SQL yazmaz, sayı hesaplamaz, cube seçmez, **ham satır görmez** —
girdisi yalnız `interpret()`'in doğrulanmış olgularıdır.
"""

from __future__ import annotations

import inspect

import pytest

from app import answer as answer_mod
from app.narration_guard import guvenli_anlatim


class _SahteLLM:
    """Anlatıcı sağlayıcı taklidi — üretilecek metni testin kendisi belirler."""

    def __init__(self, metin):
        self.metin, self.cagrildi = metin, []

    def anlat(self, soru, gercekler):
        self.cagrildi.append((soru, list(gercekler)))
        return self.metin


class _Istek:
    def __init__(self, llm=None, bayraklar=("cikti_yorumlama", "t2_anlatici")):
        self._llm, self._bayraklar = llm, bayraklar

        class _S:
            principal = None
        self.state = _S()

        class _AppS:
            pass
        _as = _AppS()
        _as.llm = llm

        class _App:
            state = _as
        self.app = _App()


def _kos(monkeypatch, llm, yorum, result, bayraklar=("cikti_yorumlama", "t2_anlatici")):
    from app import features
    from app.schemas import AskResponse, QueryResult

    monkeypatch.setattr(features, "resolve_for",
                        lambda *a, **k: {b: "beta" for b in bayraklar})
    resp = AskResponse(question="bu yıl ciro", sql="SELECT 1", planned_sql=None,
                       result=QueryResult(**result) if result else None, source="cube")
    resp.interpretation = yorum
    answer_mod._anlati_ekle(_Istek(llm), resp)
    return resp


_SONUC = {"columns": ["ciro"], "rows": [{"ciro": 1500.0}], "row_count": 1}
_YORUM = {"facts": [{"text": "Toplam ciro 1500 TL."}], "summary": "Toplam ciro 1500 TL."}


# --- FAIL-CLOSED -----------------------------------------------------------------

def test_UYDURMA_SAYI_yayimlanmaz(monkeypatch):
    """Guard'ın varlık sebebi. 'Akıcı ama uydurma' bir cümle, şablon bir doğrudan kötüdür."""
    llm = _SahteLLM("Ciro 999999 TL'ye ulaştı. Bu geçen yıla göre %87 artış.")
    r = _kos(monkeypatch, llm, dict(_YORUM), _SONUC)
    assert "narration" not in r.interpretation, \
        f"uydurma sayı yayımlandı: {r.interpretation.get('narration')!r}"
    assert r.interpretation["summary"] == "Toplam ciro 1500 TL.", "şablon kayboldu"


def test_DOGRU_SAYI_yayimlanir(monkeypatch):
    llm = _SahteLLM("Bu yıl toplam ciro 1500 TL olarak gerçekleşti.")
    r = _kos(monkeypatch, llm, dict(_YORUM), _SONUC)
    assert r.interpretation.get("narration")


def test_KISMI_dusus_TEMIZ_cumleleri_KORUR(monkeypatch):
    """Kapı **cerrahi**: bir uydurma cümle yüzünden üç doğru cümleyi atmak bilgi
    kaybettirir. Kullanılamayan kapı kapatılır ve o zaman hiç yoktur."""
    llm = _SahteLLM("Bu yıl toplam ciro 1500 TL. Kâr marjı 77777 TL arttı.")
    r = _kos(monkeypatch, llm, dict(_YORUM), _SONUC)
    n = r.interpretation.get("narration") or ""
    assert "1500" in n and "77777" not in n, f"cerrahi düşüş çalışmadı: {n!r}"


def test_SAYISIZ_cumle_GECER():
    """Kapı sayı uydurmasını engeller, ÜSLUBU değil."""
    metin, _ = guvenli_anlatim("Sonuçlar genel olarak istikrarlı görünüyor.", _SONUC)
    assert metin


# --- ŞABLONU EZMEZ ---------------------------------------------------------------

def test_SUMMARY_ve_FACTS_dokunulmaz(monkeypatch):
    llm = _SahteLLM("Bu yıl toplam ciro 1500 TL olarak gerçekleşti.")
    yorum = dict(_YORUM)
    r = _kos(monkeypatch, llm, yorum, _SONUC)
    assert r.interpretation["summary"] == _YORUM["summary"]
    assert r.interpretation["facts"] == _YORUM["facts"]


def test_KAYNAK_KODU_deterministik_alanlari_YAZMIYOR():
    govde = inspect.getsource(answer_mod._anlati_ekle)
    for alan in ('yorum["summary"] =', 'yorum["facts"] ='):
        assert alan not in govde, f"anlatı deterministik alanı EZİYOR: {alan}"


# --- KURAL B: bayrak + sağlayıcı yokluğu -----------------------------------------

def test_BAYRAK_KAPALIYKEN_hic_calismaz(monkeypatch):
    llm = _SahteLLM("Bu yıl toplam ciro 1500 TL.")
    r = _kos(monkeypatch, llm, dict(_YORUM), _SONUC, bayraklar=("cikti_yorumlama",))
    assert "narration" not in r.interpretation
    assert not llm.cagrildi, "bayrak kapalıyken LLM ÇAĞRILDI — bütçe/gizlilik ihlali"


def test_SAGLAYICI_YOKSA_yol_KAPALI_hata_DEGIL(monkeypatch):
    """Kural-tabanlı sağlayıcı `anlat` taşımaz — yokluğu bir hata değil YOL KAPALI."""
    class _Kuralli:
        pass

    r = _kos(monkeypatch, _Kuralli(), dict(_YORUM), _SONUC)
    assert "narration" not in r.interpretation


def test_LLM_PATLARSA_cevap_DUSMEZ(monkeypatch):
    class _Patlak:
        def anlat(self, soru, gercekler):
            raise RuntimeError("sağlayıcı yok")

    r = _kos(monkeypatch, _Patlak(), dict(_YORUM), _SONUC)
    assert r.interpretation["summary"] == _YORUM["summary"]
    assert "narration" not in r.interpretation


def test_OLGU_YOKSA_LLM_CAGRILMAZ(monkeypatch):
    llm = _SahteLLM("herhangi")
    _kos(monkeypatch, llm, {"facts": [], "summary": ""}, _SONUC)
    assert not llm.cagrildi, "boş olgu kümesiyle LLM çağrıldı — bedava uydurma daveti"


# --- GİRDİ DAR: ham satır GİTMEZ --------------------------------------------------

def test_LLMe_YALNIZ_OLGULAR_gider(monkeypatch):
    """Model ham satır görmez, sayı hesaplamaz. Girdi `interpret()`'in olgularıdır."""
    llm = _SahteLLM("Bu yıl toplam ciro 1500 TL.")
    _kos(monkeypatch, llm, dict(_YORUM), _SONUC)
    (soru, gercekler), = llm.cagrildi
    assert gercekler == ["Toplam ciro 1500 TL."]
    assert soru == "bu yıl ciro"


def test_PROMPT_sayi_uretmeyi_YASAKLIYOR():
    from app import llm as llm_mod

    s = llm_mod._anlati_system()
    assert "HİÇBİR YENİ SAYI ÜRETME" in s
    for yasak in ("Hesap yapma", "uydurma"):
        assert yasak in s


# --- ARAÇ KAYDI: kapısız LLM çağrısı yok ------------------------------------------

def test_ARAC_KAYDINDA(monkeypatch):
    """F2'nin dört kapısı (kayıt · yetki · deterministik-önce · bütçe) tam olarak
    KAPISIZ LLM çağrısını engellemek için var. Enhancer için planın koştuğu şart
    (§4.3 ⟳) anlatıcı için de geçerli: makbuzda görünmeli."""
    from app import tools

    a = next((x for x in tools.KAYIT if x.ad == "llm.anlat"), None)
    assert a is not None, "`llm.anlat` araç kaydında YOK — kapısız LLM çağrısı"
    assert a.determinizm == "llm" and a.yan_etki == "yok"
    assert "narration_guard" in a.notlar


def test_FAILOVER_anlat_TASIYOR():
    from app import llm as llm_mod

    assert hasattr(llm_mod.FailoverSqlGenerator, "anlat")
    govde = inspect.getsource(llm_mod.FailoverSqlGenerator.anlat)
    assert 'hasattr(g, "anlat")' in govde, "sağlayıcı yokluğu hata sayılıyor"


def test_KURAL_TABANLI_saglayicida_anlat_YOK():
    from app import llm as llm_mod

    assert not hasattr(llm_mod.RuleBasedSqlGenerator, "anlat")


# --- UÇTAN UCA: bayrak varsayılan KAPALI -----------------------------------------

def test_VARSAYILAN_KAPALI_ask_zincirinde_narration_YOK(client):
    """Sıcak yola bir LLM çağrısı ekliyor; açılması BİLİNÇLİ bir karar olmalı."""
    d = client.post("/ask", json={"question": "bu yıl toplam ciro",
                                  "session_id": "t2", "execute": True}).json()
    assert not (d.get("interpretation") or {}).get("narration")


# --- FAZ 9.8: kapısız LLM çağrısı YOK, makbuzda ADIM olarak görünüyor -------------
#
# ## Ölçülen uyuşmazlık (denetim, Faz 9)
#
# MIMARI §12.6b: *"`llm.anlat` `tools.KAYIT`'ta — prompt-enhancer için koştuğu şart
# (**kapısız LLM çağrısı olmasın; makbuzda ADIM olarak görünsün**) anlatıcı için de
# uygulandı."* Kaydın ilk yarısı doğruydu; **ikinci yarısı karşılıksızdı**: `answer.py`
# `llm.anlat(...)`'ı DOĞRUDAN çağırıyordu. Karşılaştır: enhancer gerçekten geçiyordu.
#
# Bu, bu oturumun on dört kez avladığı *"beyan var, kod onu tanımıyor"* sınıfının
# MIMARI'nin kendi metnindeki hâliydi.

def test_ANLATICI_PLANLAYICIDAN_geciyor():
    import inspect

    from app import answer

    govde = inspect.getsource(answer._anlati_ekle)
    assert 'calistir("llm.anlat"' in govde, "kapısız LLM çağrısı"
    assert 'calistir("interpret"' in govde, (
        "DETERMİNİSTİK-ÖNCE kapısı kendi kaydını görmüyor — `interpret` (aynı `anlatim` "
        "etiketinin LLM'siz kardeşi) planlayıcı üzerinden denenmeli")


def test_ANLATI_MAKBUZU_ajan_kosumunu_EZMIYOR():
    """Makbuz *"LLM ne zaman devreye girdi"* sorusunu cevaplamak için var; ajan
    koşumunun adımlarını silip yerine tek bir anlatı adımı yazmak, o soruyu cevaplamak
    yerine YANILTIRDI."""
    from app.answer import _anlati_makbuzu
    from app.schemas import AskResponse

    class _Kosum:
        def makbuza(self):
            return {"agent_run": {"steps": [{"arac": "llm.anlat"}], "step_count": 1}}

    class _Plan:
        kosum = _Kosum()

    resp = AskResponse(question="x")
    resp.agent_run = {"steps": [{"arac": "route"}], "step_count": 1, "truncated": False}
    _anlati_makbuzu(resp, _Plan())
    araclar = [s["arac"] for s in resp.agent_run["steps"]]
    assert araclar == ["route", "llm.anlat"], f"ajan adımı EZİLDİ: {araclar}"
    assert resp.agent_run["step_count"] == 2, "step_count birleşimden sonra düzeltilmedi"
    assert resp.agent_run["truncated"] is False, "mevcut makbuzun alanları kayboldu"


def test_ANLATI_MAKBUZU_yoksa_KURAR():
    from app.answer import _anlati_makbuzu
    from app.schemas import AskResponse

    class _Kosum:
        def makbuza(self):
            return {"agent_run": {"steps": [{"arac": "llm.anlat"}], "step_count": 1}}

    class _Plan:
        kosum = _Kosum()

    resp = AskResponse(question="x")
    _anlati_makbuzu(resp, _Plan())
    assert resp.agent_run and resp.agent_run["step_count"] == 1


def test_MAKBUZ_HATASI_cevabi_DUSURMEZ():
    """Makbuz bir denetim kolaylığıdır; kullanıcının cevabını rehin alamaz."""
    from app.answer import _anlati_makbuzu
    from app.schemas import AskResponse

    class _Patlak:
        @property
        def kosum(self):
            raise RuntimeError("patladı")

    resp = AskResponse(question="x")
    _anlati_makbuzu(resp, _Patlak())      # patlamamalı
    assert resp.agent_run is None
