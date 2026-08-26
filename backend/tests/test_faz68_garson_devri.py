"""🔴🔴 FAZ 6.8 — **GARSON DEVRİ, `sinifla()` kalıp bulamadığında.**

## Kullanıcının düzeltmesi (2026-08-26, aynı gün, FAZ 6.7'nin hemen ardından)

*"kral bi hata yaptık sohbet merkezli yapalım dedik ama 1 cümle yazmak için demedim...
adam mesela soru sordu cevap geldi üstüne sohbet etmek isteyince artık llm uzun uzun
anlatmalı."* Sonra ikinci, belirleyici düzeltme: *"mesele sadece anlamadımm sözcüğü
değil bu gibi convarsitional her şeyin tespit edilmesi lazım tek tek hard code
edilmeden bi şekilde."*

## İki ayrı sorunun İKİ ayrı çözümü

1. **TESPİT** — *"anlamadım"*, *"peki bu ne demek"* gibi ifadeler `followup._ANLAT`
   kelime listesinde YOK ve `_fiil_hit`'in fiil-çekim zincirine de girmiyor
   (olumsuzluk+geçmiş+kişi bir AYRI morfolojik sınıftır). `EN ÜST KURAL` bunun için
   zaten yazılmıştı: *"bir cümle anlaşılmıyorsa çözüm route'u genişletmek değil devri
   tetiklemektir."* `followup.niyet_garsondan` + `llm.takip_siniflandir` bu devri
   uygular — kelime listesi BÜYÜMEZ, ZATEN güvendiğimiz hakeme (garson) sorulur.

2. **DERİNLİK** — tespit doğru olsa bile `answer._anlati_ekle`'nin `basit_mi()`
   kısayolu basit olguları HER ZAMAN şablonla geçiştiriyordu — konuşma bağlamında bile.
   `resp._zorla_anlati` işareti bu kısayolu YALNIZ konuşma bağlamında geçersiz kılar;
   ANINDA cevaplanan plain sorgular (FAZ 6.7'nin geri alınan hatası) ETKİLENMEZ.

Her iki mekanizma da `KURAL B` altında doğar: `t8_sohbet` kapalıyken HİÇBİR davranış
değişmez (ne yeni bir LLM çağrısı, ne `basit_mi` kısayolunun geçersiz kılınması).
"""

from __future__ import annotations

import inspect

import pytest

from app import answer as answer_mod
from app import followup as fu
from app import llm as llm_mod


# ─────────────────────────────────────────────────────────────────────────────
# A · `followup.niyet_garsondan` — kararı `Niyet`e çeviren SAF fonksiyon
# ─────────────────────────────────────────────────────────────────────────────

def test_KONUSMA_TRUE_GECERLI_TUR_niyet_uretir():
    n = fu.niyet_garsondan({"konusma": True, "tur": "anlat"}, "anlamadım")
    assert n is not None
    assert n.sinif == fu.SINIF_KONUSMA
    assert n.tur == fu.TUR_ANLAT
    assert n.kural == "garson-devri"
    assert n.kanit == "anlamadım"
    assert n.konusma is True


@pytest.mark.parametrize("tur", ["neden", "ne_yapmali", "normal_mi", "anlat", "makbuz"])
def test_TUM_GECERLI_TURLER_KABUL_EDILIR(tur):
    n = fu.niyet_garsondan({"konusma": True, "tur": tur}, "x")
    assert n is not None and n.tur == tur


def test_KONUSMA_FALSE_NONE_DONER():
    assert fu.niyet_garsondan({"konusma": False, "tur": "anlat"}, "yeni bir soru") is None


def test_KONUSMA_ANAHTARI_YOKSA_NONE_DONER():
    """🔴 Fail-closed: `konusma` alanı eksikse (garson yarım bir JSON döndürdüyse)
    varsayılan `False` sayılır — konuşma UYDURULMAZ."""
    assert fu.niyet_garsondan({"tur": "anlat"}, "x") is None


def test_UYDURMA_TUR_REDDEDILIR():
    """🔴 Garson kapalı kümenin DIŞINDA bir tür üretirse (halüsinasyon) `None` döner —
    yeni bir tür İCAT EDİLMEZ."""
    assert fu.niyet_garsondan({"konusma": True, "tur": "boyle_bir_tur_yok"}, "x") is None


def test_TUR_YOKSA_REDDEDILIR():
    assert fu.niyet_garsondan({"konusma": True}, "x") is None


@pytest.mark.parametrize("bozuk", [None, [], "metin", 42, {}])
def test_BOZUK_KARAR_NONE_DONER(bozuk):
    assert fu.niyet_garsondan(bozuk, "x") is None


def test_KANIT_KIRPILIR():
    """Uzun bir mesaj `kanit` alanını şişirmemeli — makbuz okunabilir kalmalı."""
    uzun = "a" * 500
    n = fu.niyet_garsondan({"konusma": True, "tur": "anlat"}, uzun)
    assert n is not None and len(n.kanit) <= 120


def test_GECERLI_TUR_KUMESI_KAPALI_KUME():
    """🔴 `TUR_ISARET`/`TUR_TAKIP`/`TUR_PAYLAS` BİLEREK dışarıda: bunlar ya bir
    KOORDİNAT (`isaret`) ya da bir HEDEF (`paylas`/`takip`) ister — garsonun tek
    cümlelik sınıflandırmasından üretilemez."""
    assert fu._GARSON_TUR_GECERLI == frozenset(
        {fu.TUR_NEDEN, fu.TUR_NE_YAPMALI, fu.TUR_NORMAL, fu.TUR_ANLAT, fu.TUR_MAKBUZ})


# ─────────────────────────────────────────────────────────────────────────────
# B · `app/llm.py` — yeni sağlayıcı yeteneği (`takip_siniflandir`) ve istemi
# ─────────────────────────────────────────────────────────────────────────────

def test_UC_SAGLAYICIDA_DA_TAKIP_SINIFLANDIR_VAR():
    for sinif in (llm_mod.AnthropicSqlGenerator, llm_mod.OpenAICompatibleSqlGenerator,
                 llm_mod.FailoverSqlGenerator):
        assert hasattr(sinif, "takip_siniflandir"), f"{sinif.__name__} yeteneği taşımıyor"


def test_KURAL_TABANLI_saglayicida_YOK():
    """`RuleBasedSqlGenerator`/`NoLlmGenerator` — devir hedefi bir LLM'dir; yol kapalı."""
    assert not hasattr(llm_mod.RuleBasedSqlGenerator, "takip_siniflandir")
    assert not hasattr(llm_mod.NoLlmGenerator, "takip_siniflandir")


def test_FAILOVER_DESENI_ANLAT_ILE_BIREBIR():
    govde = inspect.getsource(llm_mod.FailoverSqlGenerator.takip_siniflandir)
    assert 'hasattr(g, "takip_siniflandir")' in govde, "sağlayıcı yokluğu hata sayılıyor"
    assert "self._last = g" in govde


def test_ISTEM_JSON_SEMASI_VE_KAPALI_KUME():
    s = llm_mod._takip_sinif_system()
    assert "konusma" in s and "tur" in s and "JSON" in s
    for tur in ("neden", "ne_yapmali", "normal_mi", "anlat", "makbuz"):
        assert tur in s, f"istem kapalı kümenin bir üyesini ({tur!r}) hiç anmıyor"


def test_ISTEM_SQL_CUBE_SECMEZ():
    """🔴 Kapsam bilinçli DAR — `_cube_select_system`'in aksine bu istem SQL/ölçü/boyut
    seçmez, yalnız BEŞ bilinen konuşma türünden birine ya da `konusma=false`e karar
    verir."""
    s = llm_mod._takip_sinif_system().lower()
    for yasak in ("sql", "measures", "dimensions"):
        assert yasak not in s


def test_KULLANICI_ISTEMI_MESAJI_TASIR():
    u = llm_mod._takip_sinif_user("anlamadım")
    assert "anlamadım" in u


def test_SELECT_MODEL_KULLANILIR():
    """Ucuz/hızlı sınıflandırma — `select_cube`/`refine_cube` ile AYNI model sınıfı,
    anlatı/SQL üreten pahalı modelin AYNISI DEĞİL."""
    govde = inspect.getsource(llm_mod.AnthropicSqlGenerator.takip_siniflandir)
    assert "self._select_model" in govde
    govde2 = inspect.getsource(llm_mod.OpenAICompatibleSqlGenerator.takip_siniflandir)
    assert "self._select_model" in govde2


# ─────────────────────────────────────────────────────────────────────────────
# C · `answer._anlati_ekle` — `_zorla_anlati` konuşma-bağlamı istisnası
# ─────────────────────────────────────────────────────────────────────────────

class _SahteLLM:
    def __init__(self, metin):
        self.metin, self.cagrildi = metin, []

    def anlat(self, soru, gercekler):
        self.cagrildi.append((soru, list(gercekler)))
        return self.metin


class _Istek:
    def __init__(self, llm=None):
        self._llm = llm

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


def _kos(monkeypatch, llm, yorum, *, bayraklar, zorla):
    from app import features
    from app.schemas import AskResponse, QueryResult

    monkeypatch.setattr(features, "resolve_for",
                        lambda *a, **k: {b: "beta" for b in bayraklar})
    resp = AskResponse(question="anlamadım", sql="SELECT 1", planned_sql=None,
                       result=QueryResult(columns=["ciro"], rows=[{"ciro": 1500.0}],
                                          row_count=1),
                       source="cube")
    resp.interpretation = yorum
    if zorla:
        resp._zorla_anlati = True  # type: ignore[attr-defined]
    answer_mod._anlati_ekle(_Istek(llm), resp)
    return resp


#: Tek olgu, TANINAN bir tür, `summary` ile FARKLI metin (yankı kapısına takılmasın) —
#: yani `basit_mi()` KESİN `True` döner (bkz. `app/anlatici.py::basit_mi`).
_BASIT_YORUM = {"facts": [{"type": "single", "measure": "toplam_ciro",
                          "text": "Toplam ciro 1500 TL"}],
               "summary": "Farklı bir özet metni."}


def test_BASIT_OLGUDA_ZORLA_YOKSA_LLM_CAGRILMAZ(monkeypatch):
    """FAZ 6.7'nin geri alınan hatasının TERSİ regresyona karşı kilit: `zorla` işareti
    YOKSA (plain/anlık sorgu) `basit_mi()` kısayolu AYNEN çalışmalı — LLM çağrılmamalı."""
    llm = _SahteLLM("herhangi bir anlatı")
    r = _kos(monkeypatch, llm, dict(_BASIT_YORUM),
            bayraklar=("t2_sablon", "t2_anlatici"), zorla=False)
    assert not llm.cagrildi, "zorla=False iken basit olguda LLM ÇAĞRILDI"
    assert r.interpretation["narration_kaynak"] == "sablon"


def test_BASIT_OLGUDA_ZORLA_VARSA_LLM_CAGRILIR(monkeypatch):
    """🔴🔴 FAZ 6.8'in asıl kazancı: konuşma bağlamında (`_zorla_anlati=True`) basit
    olgu bile LLM'e gider — kullanıcının kendi düzeltmesi budur."""
    llm = _SahteLLM("Bu yıl toplam ciro 1500 TL olarak gerçekleşti.")
    r = _kos(monkeypatch, llm, dict(_BASIT_YORUM),
            bayraklar=("t2_sablon", "t2_anlatici"), zorla=True)
    assert llm.cagrildi, "zorla=True iken basit olguda LLM ÇAĞRILMADI"
    assert r.interpretation.get("narration")


def test_ZORLA_VARSA_ama_T2_ANLATICI_KAPALIYSA_YINE_CAGRILMAZ(monkeypatch):
    """`zorla` yalnız `basit_mi` KISAYOLUNU atlar — `t2_anlatici` bayrağının KENDİSİNİ
     atlamaz. İki bayrak birbirinden BAĞIMSIZ kapı (`KURAL B` iki kez korunur).

    ⚠ `zorla=True` şablon dalını (ve onun `narration_kaynak="sablon"` makbuzunu)
    BİLEREK atlar — o dal `t2_sablon`'un KENDİ makbuzudur, `t2_anlatici` kapalıyken
    hiçbir dal `narration_kaynak` YAZMAZ (davranış "hiç dokunulmadı" ile aynı)."""
    llm = _SahteLLM("herhangi")
    r = _kos(monkeypatch, llm, dict(_BASIT_YORUM),
            bayraklar=("t2_sablon",), zorla=True)
    assert not llm.cagrildi
    assert "narration_kaynak" not in r.interpretation
    assert "narration" not in r.interpretation


def test_ZORLA_ISARETI_YOKSA_VARSAYILAN_FALSE():
    """`getattr(resp, "_zorla_anlati", False)` — alan hiç kurulmamışsa `False` sayılır;
    `AskResponse` bu alanı TANIMLI olarak TAŞIMAZ (dinamik işaret, `resp._etiketler`
    ile AYNI desen)."""
    from app.schemas import AskResponse

    resp = AskResponse(question="x")
    assert getattr(resp, "_zorla_anlati", False) is False


# ─────────────────────────────────────────────────────────────────────────────
# D · `routers/ask.py` — kablolama (yapısal denetim, closure doğrudan import EDİLEMEZ)
# ─────────────────────────────────────────────────────────────────────────────

def test_ASK_KAYNAGINDA_GARSON_KONUSMA_DENE_TANIMLI():
    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    assert "_garson_konusma_dene" in src
    assert "niyet_garsondan" in src
    assert "takip_siniflandir" in src


def test_KALIP_YOK_SARTI_ONCE_GELIR():
    """🔴 Devir yalnız `kural=="kalip-yok"` iken denenmeli — deterministik zincirin
    ZATEN tanıdığı bir türü (`konusma:neden` gibi) EZMEMELİ."""
    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    i = src.index("_garson_konusma_dene(body.question)")
    pencere = src[max(0, i - 400):i]
    assert 'niyet.kural == "kalip-yok"' in pencere
    assert "not niyet.konusma" in pencere


def test_T8_SOHBET_KURAL_B_IKI_YERDE_DE_KONTROL_EDILIR():
    """FAZ 6.8'in İKİ etkisi (tespit + derinlik) AYRI kapılardan geçer — ikisi de
    `t8_sohbet` bayrağını kendi başına sınar (tek bir kontrol paylaşılmaz, çünkü
    biri `_garson_konusma_dene` İÇİNDE, öteki `ask()` gövdesinde çağrılır)."""
    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    assert src.count('"t8_sohbet" in resolve_for') >= 1
    assert src.count('"t8_sohbet" not in resolve_for') >= 1


def test_ZORLA_ANLATI_ISARETI_KURULUR():
    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    assert "resp._zorla_anlati = True" in src


def test_FAZ68_ROADMAP_KAYDI_TUTARLI():
    """Bu modülün kendi kaydı — `niyet_garsondan`'ın docstring'i `KAT-1`'e uygun."""
    assert "GARSON DEVRİ" in (fu.niyet_garsondan.__doc__ or "")
