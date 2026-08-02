"""FAZ F2 — planlayıcı çekirdeği: dört kapı, bütçe ve dürüst kısmi cevap.

## Ölçülen boşluk (2 Ağustos 2026)

    $ grep -rn "budget|max_steps|token_limit" app/
    (boş)

**Sıfır bütçe tavanı, sıfır plan kaydı.** Şartname 4.16 bir bütçe istiyordu; hiç yoktu.

## Neden yönetişim planlayıcı zekâsından ÖNCE geliyor

Bu modül bir ReAct döngüsü **değildir** ve bilinçli değildir: *"hangi adımı seçeyim"*
kararı telemetriyle kalibre edilmeli (Faz E-1) ve telemetri bugün **boş**. Ölçülmemiş bir
kararı LLM'e devretmek, bu turda altı kez ölçülen *"beyan var, kanıt yok"* sınıfının en
pahalı örneği olurdu.

> Planlayıcı zekâsı olmadan yönetişim işe yarar. **Yönetişim olmadan planlayıcı zekâsı
> tehlikelidir** — sınırsız bir döngü, denetlenmeyen bir yetki, izlenmeyen bir maliyet.

## Dört kapı

kayıt (araç uydurulamaz) · yetki (kullanıcıyı aşamaz) · deterministik-önce (kural değil
KAPI) · bütçe (adım/süre/sorgu).
"""

from __future__ import annotations

import time

import pytest

from app import tools
from app.planner import AracReddi, Butce, ButceAsimi, Planlayici
from control_plane.authorize import Principal


def _p(*roller: str) -> Principal:
    return Principal(user_id="u", tenant_id="t", roles=list(roller), tenant_slug="demo")


# --- KAPI 1: KAYIT — planlayıcı araç UYDURAMAZ ----------------------------------

def test_kayitli_olmayan_arac_REDDEDILIR():
    p = Planlayici()
    with pytest.raises(KeyError, match="Kayıtlı olmayan"):
        p.calistir("veritabanini_sil")
    assert p.kosum.adimlar == [], "reddedilen çağrı adım olarak kaydedilmemeli"


# --- KAPI 2: YETKİ — ajan kullanıcının yetkisini AŞAMAZ -------------------------

def test_yetkisiz_kullanici_ARACI_CALISTIRAMAZ(monkeypatch):
    """Kayıttaki araçların hepsi bugün `query:run` (viewer+). Kapının GERÇEKTEN
    çalıştığını göstermek için geçici olarak yüksek izinli bir araç enjekte edilir —
    aksi halde test yalnız "bugün böyle bir araç yok"u kanıtlardı."""
    yuksek = tools.Arac(
        ad="_test_yuksek", ozet="yalnız test için yüksek izinli sahte araç",
        girdi={"x": "değer"}, cikti="yok", determinizm="deterministik",
        maliyet="sifir", yan_etki="yok", izin="measure:approve", makbuz=None,
        modul="app.tools", fonksiyon="hepsi", etiketler=("test",),
    )
    monkeypatch.setitem(tools._ARACLAR, "_test_yuksek", yuksek)
    monkeypatch.setattr(tools, "KAYIT", (*tools.KAYIT, yuksek))

    with pytest.raises(AracReddi, match="yetkisi yok"):
        Planlayici(principal=_p("viewer")).calistir("_test_yuksek")
    # admin+ geçebilmeli — kapı yetkiyi okuyor, herkesi reddetmiyor.
    assert Planlayici(principal=_p("owner")).calistir("_test_yuksek") is not None


def test_kimliksiz_cagri_yetki_kapisina_TABI_DEGIL():
    """Dahili/test çağrıları (principal=None) kapıdan muaf — aksi halde her birim
    testi sahte bir kimlik kurmak zorunda kalır ve kapı gürültüye dönerdi."""
    assert Planlayici().calistir("route", "merhaba", {"cubes": []}) is None


# --- KAPI 3: DETERMİNİSTİK-ÖNCE — kural değil KAPI ------------------------------

def test_LLM_araci_deterministik_kardes_DENENMEDEN_secilemez():
    """ASIL KAPI. `llm.select_cube`'un deterministik kardeşi `route`'tur (aynı
    "sorgu-uretimi" etiketi). Merdivenin felsefesi plan seviyesine böyle taşınır."""
    p = Planlayici(kaynaklar={"servis:llm": object()})
    with pytest.raises(AracReddi, match="DETERMİNİSTİK-ÖNCE"):
        p.calistir("llm.select_cube", "soru", "katalog")


def test_deterministik_DENENDIKTEN_sonra_LLM_serbest():
    """`route` çalıştıktan sonra (cevap üretmese bile) LLM aracı meşrudur — merdivenin
    bir sonraki basamağı budur."""
    class _SahteLLM:
        def select_cube(self, *_a):
            return '{"cube":"x"}'

    p = Planlayici(kaynaklar={"servis:llm": _SahteLLM()})
    p.calistir("route", "anlaşılmaz soru", {"cubes": []})
    assert p.calistir("llm.select_cube", "soru", "katalog") == '{"cube":"x"}'


def test_deterministik_arac_KAPIYA_takilmaz():
    p = Planlayici()
    assert p.calistir("route", "merhaba", {"cubes": []}) is None
    assert len(p.kosum.adimlar) == 1


# --- KAPI 4: BÜTÇE ---------------------------------------------------------------

def test_ADIM_tavani():
    p = Planlayici(butce=Butce(adim=2))
    p.calistir("route", "a", {"cubes": []})
    p.calistir("route", "b", {"cubes": []})
    with pytest.raises(ButceAsimi, match="adım tavanı"):
        p.calistir("route", "c", {"cubes": []})
    assert p.kosum.kisildi and "adım" in p.kosum.kisilma_nedeni
    assert len(p.kosum.adimlar) == 2, "kısılan adım kaydedilmemeli"


def test_SURE_tavani():
    p = Planlayici(butce=Butce(saniye=0.001))
    time.sleep(0.01)
    with pytest.raises(ButceAsimi, match="süre tavanı"):
        p.calistir("route", "a", {"cubes": []})
    assert p.kosum.kisildi


def test_SORGU_tavani_yalniz_VERIYE_dokunani_sayar():
    """`route` maliyet=sıfır → sorgu tavanını TÜKETMEZ. Sorgu bütçesi veriye dokunan
    adımlar içindir; sıfır maliyetli adımları saymak tavanı anlamsız kılardı."""
    p = Planlayici(butce=Butce(sorgu=0))
    for i in range(5):
        p.calistir("route", str(i), {"cubes": []})
    assert p.kosum.sorgu_sayisi == 0 and not p.kosum.kisildi


def test_SINIRSIZ_bütce():
    p = Planlayici(butce=Butce(adim=0, saniye=0, sorgu=0))
    for i in range(30):
        p.calistir("route", str(i), {"cubes": []})
    assert len(p.kosum.adimlar) == 30 and not p.kosum.kisildi


def test_kalan_butce_sorulabilir():
    p = Planlayici(butce=Butce(adim=3))
    p.calistir("route", "a", {"cubes": []})
    k = p.kalan()
    assert k["adim"] == 2 and k["saniye"] > 0


# --- DÜRÜST KISMİ CEVAP ---------------------------------------------------------

def test_butce_asiminda_ONCEKI_adimlar_GECERLI():
    """Sessiz kesme YOK: tavan aşıldığında o ana kadarki iş çöpe atılmaz. Çağıran
    kısmi ama DÜRÜST bir cevap verebilir — `contribution`'ın `kirpilan_segment`'iyle
    aynı desen."""
    p = Planlayici(butce=Butce(adim=1))
    p.calistir("route", "a", {"cubes": []})
    with pytest.raises(ButceAsimi):
        p.calistir("route", "b", {"cubes": []})
    m = p.kosum.makbuza()["agent_run"]
    assert m["step_count"] == 1 and m["truncated"] is True
    assert m["truncation_reason"], "kısılma GEREKÇESİZ kaydedilemez"


def test_kisilmadi_da_KAYDEDILIR():
    """"Kısılmadı" ile "kısılma sorulmadı" FARKLI şeylerdir; alan her zaman yazılır."""
    p = Planlayici()
    p.calistir("route", "a", {"cubes": []})
    m = p.kosum.makbuza()["agent_run"]
    assert m["truncated"] is False and m["truncation_reason"] is None


# --- MAKBUZ AĞACI ---------------------------------------------------------------

def test_her_adim_MAKBUZA_yazilir():
    p = Planlayici()
    p.calistir("route", "a", {"cubes": []}, makbuz="c-abc")
    adim = p.kosum.makbuza()["agent_run"]["steps"][0]
    assert adim["tool"] == "route" and adim["receipt"] == "c-abc"
    assert adim["determinism"] == "deterministik" and adim["ms"] >= 0


def test_BASARISIZ_adim_da_kaydedilir():
    """Sessizce kaybolan bir adım, yapılmamış bir adım gibi okunur ve koşumun maliyeti
    anlaşılmaz olur. Bütçe tüketildi; denetçi neyin denendiğini görmeli."""
    p = Planlayici()
    with pytest.raises(Exception):
        p.calistir("route", None, None)      # route None şemayla patlar
    adimlar = p.kosum.makbuza()["agent_run"]["steps"]
    assert len(adimlar) == 1 and adimlar[0].get("error")


def test_makbuz_JSON_serilesebilir():
    import json

    p = Planlayici()
    p.calistir("route", "a", {"cubes": []})
    assert json.dumps(p.kosum.makbuza())


# --- SERVİSE BAĞLI araçlar ------------------------------------------------------

def test_servis_araci_KAYNAKTAN_cozulur():
    """`servis:wren` bağlı araçlar istek-kapsamlı nesneden çözülür — planlayıcı hangi
    tenant'ın motoruna gittiğini bilir."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    p = Planlayici(kaynaklar={"servis:wren": svc})
    sql = p.calistir("cube_sql", {"cube": "parti", "measures": ["toplam_ciro"],
                                  "dimensions": [], "filters": []})
    assert "SELECT" in sql.upper()
    assert p.kosum.adimlar[-1].arac == "cube_sql"
