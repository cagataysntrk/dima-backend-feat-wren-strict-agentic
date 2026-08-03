"""FAZ 4 — K3 ORKESTRATÖR: *"LLM garson olur, işi küpler yapar"* bir KAPI oldu.

## Zemin ve eksik olan tek şey

`planner.py`'nin **dört kapısı** (kayıt · yetki · deterministik-önce · bütçe) yazılmış ve
testliydi; eksik olan **plan SEÇİMİ**ydi. Modülün kendi docstring'i bunu *"bilinçli olarak
yok: o karar telemetriyle kalibre edilmeli"* diye kaydediyordu. Faz 0 telemetriyi kurdu,
Faz 2b onu triyaja bağladı — kapı açıldı.

## Bu fazın omurgası: SEÇİM ≠ ÇALIŞTIRMA

`sec()` yalnız **önerir**; her adım yine `calistir()`'e verilir ve **aynı dört kapıdan**
geçer. Sonuç: **seçicinin yanılması yeni bir risk açmaz.**

| seçici hatası | hangi kapı öldürür |
|---|---|
| uydurulmuş araç adı | **KAYIT** (ve `sec()` onu kayda geçirerek eler) |
| yetkisiz araç | **YETKİ** — ajan kullanıcıyı AŞAMAZ |
| `route` denenmeden LLM aracı | **DETERMİNİSTİK-ÖNCE** |
| sonsuz/pahalı plan | **BÜTÇE** |
| yazma yan etkili araç | zaten `llm_araclari` **dışında** (beyan edilerek) |

## Sessiz kırpma YOK

Geçersiz bir öneri **sessizce elenmez**: `Adim(hata="SEÇİM REDDİ…")` olarak kayda geçer.
Sessizce elemek, seçicinin ne kadar yanıldığını **ölçülemez** yapardı.
"""

from __future__ import annotations

import inspect

import pytest

from app import tools
from app.planner import AracReddi, Butce, Planlayici


class _LLM:
    def __init__(self, cikti):
        self.cikti, self.gorulen = cikti, []

    def plan_sec(self, soru, araclar_json, ipucu=""):
        self.gorulen.append(araclar_json)
        return self.cikti


def _p(principal=None, **kw):
    return Planlayici(principal=principal,
                      butce=kw.pop("butce", Butce(adim=6, saniye=20.0, sorgu=8)),
                      kaynaklar=kw.pop("kaynaklar", {}))


# --- SEÇİM ≠ ÇALIŞTIRMA ----------------------------------------------------------

def test_SEC_calistirmaz():
    """Öneri bir eylem DEĞİLDİR: `sec()` hiçbir araç çağırmamalı."""
    p = _p()
    once = len(p.kosum.adimlar)
    p.sec("bu yıl ciro", _LLM('[{"arac":"route","neden":"x"}]'))
    assert len(p.kosum.adimlar) == once, "sec() araç ÇALIŞTIRDI — seçim/çalıştırma ayrımı yok"


def test_ONERI_yine_DORT_KAPIDAN_gecer():
    """Seçicinin önerdiği bir LLM aracı, `route` denenmeden çalıştırılamaz."""
    p = _p()
    plan = p.sec("bu yıl ciro", _LLM('[{"arac":"llm.select_cube","neden":"x"}]'))
    assert any(a["arac"] == "llm.select_cube" for a in plan)
    with pytest.raises(AracReddi, match="DETERMİNİSTİK-ÖNCE"):
        p.calistir("llm.select_cube", "s", "k")


# --- SESSİZ KIRPMA YOK -----------------------------------------------------------

def test_UYDURMA_ARAC_kayda_GECEREK_elenir():
    p = _p()
    plan = p.sec("x", _LLM('[{"arac":"uydurma.arac","neden":"y"},{"arac":"route","neden":"z"}]'))
    assert not any(a["arac"] == "uydurma.arac" for a in plan)
    reddedilen = [a for a in p.kosum.adimlar if a.hata and "SEÇİM REDDİ" in a.hata]
    assert reddedilen and reddedilen[0].arac == "uydurma.arac", \
        "geçersiz öneri SESSİZCE elendi — seçicinin yanılma oranı ölçülemez olur"


def test_KAYIT_kapisi_ikinci_savunma():
    """`sec()` elese bile `calistir()` bağımsız olarak reddeder — tek savunma yeterli değil."""
    p = _p()
    with pytest.raises(KeyError):
        p.calistir("uydurma.arac")


# --- DETERMİNİSTİK-ÖNCE, PLAN SEVİYESİNDE ----------------------------------------

def test_ROUTE_yoksa_BASA_eklenir():
    """Kapı ceza değil YÖNLENDİRME: `route` öneride yoksa plan ilk adımda ölürdü."""
    p = _p()
    plan = p.sec("x", _LLM('[{"arac":"llm.select_cube","neden":"y"}]'))
    assert plan[0]["arac"] == "route", f"route başa eklenmedi: {plan}"


def test_ROUTE_varsa_TEKRARLANMAZ():
    p = _p()
    plan = p.sec("x", _LLM('[{"arac":"route","neden":"a"},{"arac":"route","neden":"b"}]'))
    assert [a["arac"] for a in plan] == ["route"]


# --- YEDEK YOLLAR: gerileme YOK --------------------------------------------------

def test_LLM_YOKSA_deterministik_yedek():
    """Sağlayıcı yokluğu bir hata değil — merdivenin birinci basamağı zaten belliydi."""
    assert _p().sec("x") == [{"arac": "route",
                              "neden": "deterministik yedek (sağlayıcı yok)"}]


def test_PLAN_SEC_TASIMAYAN_saglayici_yedege_duser():
    class _Kuralli:
        pass

    plan = _p().sec("x", _Kuralli())
    assert plan[0]["arac"] == "route"


def test_BOZUK_JSON_yedege_duser():
    plan = _p().sec("x", _LLM("bu JSON değil {{"))
    assert plan == [{"arac": "route", "neden": "seçim başarısız → deterministik yedek"}]


def test_LLM_PATLARSA_yedege_duser():
    class _Patlak:
        def plan_sec(self, *a, **k):
            raise RuntimeError("sağlayıcı yok")

    assert _p().sec("x", _Patlak())[0]["arac"] == "route"


def test_BOS_LISTE_yedege_duser():
    assert _p().sec("x", _LLM("[]"))[0]["arac"] == "route"


def test_SARMALI_JSON_da_okunur():
    """Model ```json ile sarabilir ya da {"adimlar": [...]} döndürebilir."""
    p = _p()
    assert any(a["arac"] == "route"
               for a in p.sec("x", _LLM('```json\n[{"arac":"route"}]\n```')))
    assert any(a["arac"] == "route"
               for a in _p().sec("x", _LLM('{"adimlar":[{"arac":"route"}]}')))


# --- LLM NE GÖRÜR: yetki + yazma yan etkisi --------------------------------------

def test_LLM_YAZMA_yan_etkili_araclari_GORMEZ():
    """`tools.py:108-117` bunları **beyan ederek** dışarıda bırakıyor. Ajan kullanıcının
    kendi eliyle yapamayacağı bir işi onun adına YAPAMAZ."""
    adlar = {a["name"] for a in tools.llm_araclari(None)}
    for yasak in ("dashboards.create", "schedules.create", "measures.approve",
                  "drill.raw", "vqr.recall"):
        assert yasak not in adlar, f"{yasak} ajana açık — yazma/gizlilik sınırı delik"


def test_SECICI_YALNIZ_bu_listeyi_gorur():
    p = _p()
    llm = _LLM('[{"arac":"route"}]')
    p.sec("x", llm)
    gorulen = llm.gorulen[0]
    assert "dashboards.create" not in gorulen
    assert "route" in gorulen


def test_PROMPT_arac_UYDURMAYI_yasakliyor():
    from app import llm as llm_mod

    s = llm_mod._plan_sec_system("[]", "")
    assert "Araç UYDURMA" in s
    assert "route" in s and "ÖNCE" in s


# --- BÜTÇE -----------------------------------------------------------------------

def test_BUTCE_tavanı_planin_verdigi_deger():
    """Plan: `Butce(adim=6, saniye=20, sorgu=8)`."""
    b = Butce(adim=6, saniye=20.0, sorgu=8)
    assert (b.adim, b.saniye, b.sorgu) == (6, 20.0, 8)


# --- BEYAN GÜNCELLENDİ -----------------------------------------------------------

def test_BAYAT_BEYAN_temizlendi():
    """`planner.py` iki yerde *"plan seçimi YOK"* diyordu; Faz 4 onu değiştirdi.
    Beyan güncellenmeseydi bu deponun en sık kusuru (*"beyan var, kod onu tanımıyor"*)
    tam tersi yönde tekrarlanırdı: kod var, beyan yokluğunu iddia ediyor."""
    import app.planner as pl

    # Eski ifade tarihsel kayıt olarak ⟳ bloğunda ALINTILANABİLİR; yasak olan onu HÂLÂ
    # İDDİA ETMEKTİR. Ayrım: ⟳ işaretinden ÖNCEKİ kısım bugünkü beyandır.
    ds = Planlayici.__doc__ or ""
    bugunku = ds.split("⟳")[0]
    assert "Plan seçmez" not in bugunku, "bayat beyan: sınıf hâlâ 'plan seçmez' İDDİA ediyor"
    assert "⟳" in ds and "sec()" in ds, "beyan güncellenmemiş"

    mod_bugunku = (pl.__doc__ or "").split("⟳")[0]
    assert "kısmı henüz yok" not in mod_bugunku, "modül docstring'i hâlâ yokluğu iddia ediyor"
    assert "⟳" in (pl.__doc__ or ""), "modül beyanı güncellenmemiş"


def test_FAILOVER_plan_sec_TASIYOR():
    from app import llm as llm_mod

    assert hasattr(llm_mod.FailoverSqlGenerator, "plan_sec")
    assert not hasattr(llm_mod.RuleBasedSqlGenerator, "plan_sec")


# --- TÜKETİCİ: sec() artık gerçekten çağrılıyor -----------------------------------

def test_SEC_TUKETICISI_VAR():
    """⚠️ **DENETİMDE BULUNDU (canlı tur, 2026-08-03).** `sec()` yazılmış ve 18 testle
    kilitlenmişti ama **hiçbir yerden çağrılmıyordu** — yani bu oturumda on bir kez
    eleştirdiğim *"beyan var, TÜKETİCİSİ yok"* sınıfına **kendim düşmüştüm**. Faz 4'ün
    kabul ölçütü (*"çapraz-alan pilotu → 2 adımlı kompozisyon"*) karşılanmamıştı.

    Bir mekanizmanın testi, o mekanizmanın **kullanıldığını** kanıtlamaz."""
    from app.routers import ask as ask_mod

    assert hasattr(ask_mod, "_capraz_alan_pilotu")
    govde = inspect.getsource(ask_mod._capraz_alan_pilotu)
    assert "plan.sec(" in govde, "pilot planlayıcıdan plan İSTEMİYOR"
    assert "plan.calistir(" in govde, "adımlar kapılardan GEÇMİYOR"

    zincir = inspect.getsource(ask_mod)
    assert "_capraz_alan_pilotu(" in zincir.replace(
        inspect.getsource(ask_mod._capraz_alan_pilotu), ""), \
        "pilot TANIMLI ama /ask zincirinden ÇAĞRILMIYOR"


def test_PILOT_makbuz_URETIYOR():
    """Planlayıcı bir cevabı NASIL ürettiğini söyleyemezse "LLM garson oldu" bir BEYAN
    olarak kalır. `agent_run` bunu YAPISAL kılar."""
    from app.schemas import AskResponse

    assert "agent_run" in AskResponse.model_fields
    from app.routers import ask as ask_mod

    assert "resp.agent_run" in inspect.getsource(ask_mod._capraz_alan_pilotu)


def test_PILOT_URETEMEZSE_bugunku_davranis():
    """`None` = Discovery aynen devam eder. Gerileme YOK."""
    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod._capraz_alan_pilotu)
    assert govde.count("return None") >= 2, "pilot başarısızlıkta bugünkü yola düşmüyor"
    assert "Discovery" in govde


def test_PILOT_BAYRAKLI():
    """KURAL B — sıcak yola LLM çağrısı ekliyor."""
    from app.routers import ask as ask_mod

    assert '"agent_plan_secimi" in resolve_for' in inspect.getsource(ask_mod)


def test_PILOT_KAPI_REDDINI_yutmuyor():
    """Kapılar çalıştığında bu bir HATA değil sistemin doğru davranışıdır — ama adım
    yine de KAYDA GEÇMELİ (calistir() zaten geçirir)."""
    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod._capraz_alan_pilotu)
    assert "AracReddi" in govde and "ButceAsimi" in govde
    assert "Kapılar ÇALIŞTI" in govde
