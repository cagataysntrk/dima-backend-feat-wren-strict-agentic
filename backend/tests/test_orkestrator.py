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


def test_PILOT_CAPRAZ_ALAN_kompozisyonu_DENIYOR():
    """⚠️ **DENETİMDE BULUNDU:** pilotun ilk sürümü yalnız `route` ve `llm.select_cube`
    deniyordu; `blend` **hiç** çağrılmıyordu. Yani Faz 4'ün kabul ölçütü (*"Discovery
    yerine 2 adımlı kompozisyon"*) karşılanmamış, pilot yalnız *"planlayıcı çalışıyor"*u
    kanıtlıyordu — `route()`'a **ek bir şey getirmiyordu**. Kazanç belirsiz değildi, YOKTU.

    MIMARI §9.2'nin yapısal sınırı: bir cube'un ölçüsü + BAŞKA cube'un boyutu **tek**
    CubeQuery'de ifade edilemez; iki adımda edilebilir ve ikinci adım **deterministiktir**."""
    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod._capraz_alan_pilotu)
    assert 'plan.calistir("cross_cube_add"' in govde, "çapraz-alan adımı ÇAĞRILMIYOR"
    assert "cross_cube_add" in govde and "adimlar = list(adimlar)" in govde, \
        "LLM yokken plan `route`'ta biter ve kompozisyon HİÇ denenmez"


def test_CROSS_CUBE_ADD_kayitli_ve_DETERMINISTIK():
    a = next((x for x in tools.KAYIT if x.ad == "cross_cube_add"), None)
    assert a is not None, "kapısız çağrı — araç kaydında YOK (calistir KeyError verirdi)"
    assert a.determinizm == "deterministik" and a.maliyet == "sifir"
    # ETİKET AİLESİ AYRI ve bu BİLİNÇLİ. İlk sürümde `sorgu-uretimi` verdim; deterministik-
    # önce kapısı onu HER LLM aracından önce zorunlu kıldı ve `prompt_enhancer` testleri
    # KIRILDI — çünkü bu araç `prev` bir CubeQuery ister ve o yokken UYGULANAMAZ. Kapı,
    # uygulanamaz bir aracı şart koşup meşru yolları kapatıyordu.
    # (Kendi kapım kendi değişikliğimi yakaladı — kapının doğru çalıştığının kanıtı.)
    rt = next(x for x in tools.KAYIT if x.ad == "route")
    assert "sorgu-uretimi" not in a.etiketler, (
        "`cross_cube_add` sıfırdan sorgu ÜRETMEZ, var olanı GENİŞLETİR — `route` ile aynı "
        "iş için yarışmaz. `sorgu-uretimi` etiketi uygulanamaz bir şart doğurur.")
    assert "kompozisyon" in a.etiketler and "sorgu-uretimi" in rt.etiketler


# --- FAZ 0.2 · MAKBUZ KENDİNİ YIKAMAZ --------------------------------------------

def test_uydurma_arac_makbuzu_dusurmez():
    """🔴 **FAZ 0.2 KAPISI.** Uydurma bir araç adı, `agent_run` makbuzunun TAMAMINI
    düşürüyordu ve bütçe kapısını SESSİZCE atlatıyordu.

    Zincir (canlı doğrulandı): `sec()` reddi `kapisiz=False` ile kaydedilir →
    `Kosum.sorgu_sayisi` `tools.get(<uydurma ad>)` çağırır → **KeyError** → makbuz üretimi
    ve `_butce_kapisi` aynı yoldan patlar; `ask.py` `continue` ile yutar.

    Makbuzun **en çok gerektiği an** modelin yanıldığı andır. O anda kaybolan bir makbuz,
    bir makbuz değildir."""
    p = _p()
    plan = p.sec("x", _LLM('[{"arac":"uydurma.arac","neden":"y"},{"arac":"route","neden":"z"}]'))
    assert not any(a["arac"] == "uydurma.arac" for a in plan)

    # (1) makbuz ÜRETİLİYOR — eskiden burada KeyError vardı
    mk = p.kosum.makbuza()
    adimlar = mk["agent_run"]["steps"]
    red = next((s for s in adimlar if "SEÇİM REDDİ" in (s.get("error") or "")), None)
    assert red is not None, f"SEÇİM REDDİ adımı makbuzda YOK: {adimlar}"
    assert red["tool"] == "uydurma.arac"
    assert red["gated"] is False, "kayıtta olmayan ad `gated` işaretlenmemiş — denetçi yanılır"

    # (2) reddedilen adım veriye DOKUNMADI → sorgu saymaz (bütçe muhasebesi bozulmaz)
    assert p.kosum.sorgu_sayisi == 0, "hiç çalıştırılmamış bir red adımı sorgu sayıldı"
    assert mk["agent_run"]["query_count"] == 0

    # (3) BÜTÇE KAPISI hâlâ çalışıyor — eskiden bu çağrı KeyError ile patlıyor,
    #     `ask.py`'de `continue` ile yutuluyor ve kapı sessizce atlanıyordu.
    p._butce_kapisi(tools.get("route"))


def test_MAKBUZ_bilinmeyen_arac_adinda_da_AYAKTA_kalir():
    """Kök neden ikinci katman: `sorgu_sayisi` bir DENETİM aracıdır; denetlediği şeyin
    kusuru yüzünden **susmamalıdır**. Kayıtta olmayan bir ad `kapisiz=False` ile
    kaydedilirse (gelecekte başka bir yer aynı hatayı yaparsa) makbuz yine üretilmeli —
    ad temkinli sayılır, `WARNING` yazılır, ama makbuz yok olmaz."""
    from app.planner import Adim

    p = _p()
    p.kosum.adimlar.append(Adim(arac="hic.olmayan", determinizm="llm", sure_ms=1))
    assert p.kosum.sorgu_sayisi == 1, "bilinmeyen ad temkinli sayılmadı"
    assert p.kosum.makbuza()["agent_run"]["step_count"] == 1


# --- FAZ 0.22 · `migration_trace` UnboundLocalError -------------------------------

def test_agent_plan_secimi_yapisal_olmayan_turda_cokmez(client, monkeypatch):
    """🔴 **FAZ 0.22 KAPISI.** `migration_trace` YALNIZ `if structural_followup:`
    bloğunun içinde tanımlıydı; **adım 4b**'nin `agent_plan_secimi` dalı blok DIŞINDA onu
    okuyordu → **bayrak `on` + `structural_followup=False` → `UnboundLocalError`** (HTTP 500).

    Bugün dormant çünkü bayrak `off` — yani *"kota serbest kalınca ölçeriz"* iyimserdi:
    ölçüm denenseydi bu soruda **500** alınırdı. Faz C'nin iki bayrağının
    (`agent_plan_secimi`, `t2_anlatici`) ölçülebilmesi buna bağlı.

    ⚠️ **BU TEST İKİ KEZ YANLIŞ YAZILDI — ikisi de ÖLÇÜLEREK yakalandı:**
    (1) İlk soru (*"…işten ayrıldı ve neden"*) `route()` ile cevaplanıyordu; pilot hiç
        çağrılmıyordu → test BOŞA koşuyordu.
    (2) İkinci soru (*"personel bazında verimlilik"*) pilotu çağırıyordu ama **YANLIŞ
        ÇAĞRI YERİNDEN**: netleştirme dalındaki ikinci çağrı yeri (`other_topic`) `[]`
        LİTERALİNİ geçiyor, yani hatalı kodda bile çökmüyor. Hata geri konularak ölçüldü:
        test **YEŞİL** kaldı. Bir kapı, ölçmediği bir şeyi *"geçti"* diye raporlayamaz.
    Bu yüzden aşağıda **çağrı YERİ de** iddia edilir — pilotun çağrılmış olması yetmez."""
    import inspect as _inspect
    import pathlib

    from lab.nl_accuracy import _BayrakZorla

    from app.routers import ask as ask_mod

    cagri_satirlari: list[str] = []
    gercek = ask_mod._capraz_alan_pilotu

    def _casus(request, body, q_norm, schema, principal, migration_trace):
        # Çağrının KENDİSİ kanıttır: argüman değerlendirilebildi → isim BAĞLI.
        # ⚠ `code_context` TEK satır verir; 4b'deki çağrı İKİ satıra yayılıdır ve
        # `lineno` ilk satırı gösterir → `migration_trace` o tek satırda GÖRÜNMEZ.
        # (Bu testin ÜÇÜNCÜ kusuru; yine ölçülerek yakalandı.) Bu yüzden kaynaktan
        # küçük bir PENCERE okunur.
        ust = _inspect.stack()[1]
        kaynak = pathlib.Path(ust.filename).read_text(encoding="utf-8").splitlines()
        cagri_satirlari.append("\n".join(kaynak[max(0, ust.lineno - 1):ust.lineno + 2]))
        return gercek(request, body, q_norm, schema, principal, migration_trace)

    monkeypatch.setattr(ask_mod, "_capraz_alan_pilotu", _casus)

    # ⚠ Soru ÖLÇÜLEREK seçildi (27 aday tarandı): 4b dalına ULAŞAN soru azdır — merdivenin
    # daha erken bir basamağı cevaplarsa ya da netleştirme dalı yakalarsa test boşa koşar.
    with _BayrakZorla("agent_plan_secimi", acik=True):
        r = client.post("/ask", json={"question": "stok devir hızımız nedir",
                                      "execute": False})
    assert r.status_code == 200, f"taze soruda çöktü: {r.status_code} {r.text[:300]}"
    assert cagri_satirlari, ("pilot HİÇ çağrılmadı — test boşa koştu. "
                             "Kapı bir şey ölçmüyorsa kapı değildir.")
    assert any("migration_trace" in s for s in cagri_satirlari), (
        "pilot çağrıldı ama YALNIZ `[]` literalini geçen çağrı yerinden — 0.22'nin hatalı "
        f"dalı (4b) hiç denenmedi: {cagri_satirlari}")


def test_MIGRATION_TRACE_blok_disinda_TANIMLI():
    """Davranış kapısının yanına YAPI kapısı: tanım `if structural_followup:` satırından
    ÖNCE gelmeli. (Bir gün pilot dalı erken `return` ile korunsa bile isim bağlı kalmalı —
    bu sınıf bu depoda *"beyan var, kod onu tanımıyor"* olarak üç kez tekrarladı.)"""
    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod.ask)
    tanim = govde.index("migration_trace: list[str] = []")
    blok = govde.index("    if structural_followup:\n")
    assert tanim < blok, "`migration_trace` hâlâ `if structural_followup` bloğunun İÇİNDE"


# ─────────────────────────────────────────────────────────────────────────────
# FAZ 6.4 — PLANLAYICI SERTLEŞTİRMESİ (§8.1, §8.6-8.10)
# ─────────────────────────────────────────────────────────────────────────────

def test_6_4_PLAN_DONDURULDUKTAN_sonra_arac_ciktisi_DEGISTIREMEZ():
    """🔴 **Kontrol-akışı bütünlüğü** (§8.1).

    Plan, **güvenilmeyen araç çıktısı bağlama girmeden** donar. Bir araç çıktısı planı
    değiştirebilseydi, dış veri (bir cube satırı, bir LLM metni) koşumun **akışını
    yönlendirebilirdi** — ve o an sistem bir **ReAct döngüsüne** dönerdi (MIMARI §11.5:
    *bu modül bir ReAct döngüsü DEĞİLDİR*).
    """
    import dataclasses

    from app.planner import PlanTaslagi, dondur

    taslak = dondur([{"arac": "route", "neden": "x"}, {"arac": "interpret"}])
    assert isinstance(taslak, PlanTaslagi) and taslak.donduruldu
    with pytest.raises(dataclasses.FrozenInstanceError):
        taslak.adimlar = ()                       # type: ignore[misc]


def test_6_4_DONDURMA_cagiranin_referansiyla_DELINEMEZ():
    """⚠ İç sözlükler de kopyalanır: bir çağıranın elindeki referansla adımı sonradan
    değiştirmek, dondurmayı **görünmez biçimde** delerdi."""
    from app.planner import dondur

    ham = [{"arac": "route"}]
    taslak = dondur(ham)
    ham[0]["arac"] = "llm.select_cube"
    assert taslak.adimlar[0]["arac"] == "route", (
        "🔴 Dondurulmuş plan dışarıdan değiştirildi — dondurma bir temenniye dönmüş.")


# --- DÖRT KATMANLI DOĞRULAMA · SINIR DEĞERLERİ --------------------------------------

def _r(degerler, kolon="v"):
    return {"columns": [kolon], "rows": [{kolon: x} for x in degerler]}


def test_6_4_KATMAN_satir_bos_sonuc():
    """*Boş bir sonuç bir cevap değil, bir sessizliktir.*"""
    from app.planner import adim_dogrula

    r = adim_dogrula({"columns": ["v"], "rows": []})
    assert r["gecti"] is False and r["katman"] == "satir"


def test_6_4_KATMAN_null_sinir_degerinde():
    """Sınır: **%90 geçer, %91 geçmez.**"""
    from app.planner import adim_dogrula

    # 10 değerin 9'u boş → %90 → eşiği AŞMAZ (kural `>` )
    assert adim_dogrula(_r([1] + [None] * 9))["gecti"] is True
    # 11 değerin 10'u boş → %90,9 → aşar
    assert adim_dogrula(_r([1] + [None] * 10))["katman"] == "null"


def test_6_4_KATMAN_mertebe_sinir_degerinde():
    """Sınır: **99× geçer, 100× geçmez** — birim/ölçek hatasının tek işareti."""
    from app.planner import adim_dogrula

    assert adim_dogrula(_r([1, 1, 99]))["gecti"] is True
    assert adim_dogrula(_r([1, 1, 100]))["katman"] == "mertebe"


def test_6_4_MERTEBE_en_az_UC_gozlem_ister():
    """⚠ *İki noktada "medyan" bir merkez değil, noktalardan biridir.*"""
    from app.planner import adim_dogrula

    assert adim_dogrula(_r([1, 100000]))["gecti"] is True


def test_6_4_KATMAN_sema_uyusmazligi():
    """*Cevap başka bir soruya ait.*"""
    from app.planner import adim_dogrula

    r = adim_dogrula(_r([1, 2, 3]), beklenen_kolonlar=["fire_orani"])
    assert r["gecti"] is False and r["katman"] == "sema"


def test_6_4_DOGRULAMA_adimi_DUSURMEZ():
    """🔴 Bir `gecti=False`, *"bu sonuç yanlış"* demez; *"bu noktadan yeniden planla"*
    der.

    *Şüpheli bir sayı, yokluğundan daha bilgilendiricidir — yeter ki şüphe SÖYLENSİN.*
    """
    from app.planner import adim_dogrula

    r = adim_dogrula(_r([1, 1, 100]))
    assert r["neden"], "gerekçesiz bir doğrulama reddi, kullanıcıya hiçbir şey söylemez"
    assert "yanlış" not in r["neden"].lower()


# --- HATA SINIFLANDIRMA (§8.8) ------------------------------------------------------

def test_6_4_HATA_IMZASI_degisken_parcalari_ELER():
    """⚠ Mesajın tamamını imza saymak, içindeki id/sayı gibi **değişken parçalar**
    yüzünden aynı hatayı her seferinde **yeni** gösterir ve strateji hiç değişmezdi."""
    from app.planner import hata_imzasi

    a = hata_imzasi("route", "ValueError: cube 'x-123' bulunamadı")
    b = hata_imzasi("route", "ValueError: cube 'y-999' bulunamadı")
    assert a == b == "route|ValueError"


def test_6_4_AYNI_IMZA_IKINCI_KEZ_strateji_degistirir():
    """*Aynı yoldan ikinci kez geçmek bir ısrar değil, bir döngüdür.*"""
    from app.planner import strateji_degistir_mi

    assert strateji_degistir_mi([], "route|ValueError") is False
    assert strateji_degistir_mi(["route|ValueError"], "route|ValueError") is True


# --- PLAN KONTROL LİSTESİ (§8.7) ----------------------------------------------------

def test_6_4_KOSUM_adim_sayaci():
    """⚠ Hatalı adım **kaydedilir** ama *tamamlandı* sayılmaz — ikisini karıştırmak,
    yarım bir koşumu **tam** gösterirdi."""
    from app.planner import Adim, Kosum

    k = Kosum(adimlar_toplam=3)
    k.adimlar.append(Adim(arac="route", determinizm="deterministik", sure_ms=1))
    k.adimlar.append(Adim(arac="interpret", determinizm="deterministik", sure_ms=1,
                          hata="ValueError: x"))
    assert k.adimlar_toplam == 3 and k.adimlar_tamam == 1
