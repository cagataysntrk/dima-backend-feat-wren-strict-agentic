"""FAZ 3b — PROMPT-ENHANCER (§4.3): T1'in DÖRDÜNCÜ, AYRI LLM rolü.

## Ayrım fazın varlık sebebi

`llm.select_cube` **ALAN SEÇER** (hangi cube/ölçü/boyut). Enhancer **yapı seçmez**, yalnız
**METNİ** iyileştirir ve aynı deterministik `route()`'a geri verir — *"hangi ölçü/boyut"*
kararı **hâlâ küptedir**. LLM'in gücü burada "ifadeyi düzeltmek"le sınırlı kalır.

**Hata yüzeyi yapısal olarak dardır:** çıktı bir metindir ve `route()` ona sıfırdan karar
verir. Model uydurma bir terim üretse bile `route()` onu yine reddeder — yani enhancer
en kötü ihtimalle **işe yaramaz**, yanlış cevap **üretemez**.

## Planın ZORUNLU ⟳ eklemesi

Çağrı `Planlayici.calistir()` üzerinden yapılır. Aksi halde bu, F2'nin tam olarak
engellemek için var olduğu **kapısız LLM çağrısı** olurdu: yetkiye bağlanmaz, bütçeye
sayılmaz, makbuzda adım olarak görünmez — *"LLM ne zaman devreye girdi"* sorusu
cevaplanamaz hale gelirdi.

`sorgu-uretimi` etiketi **deterministik-önce** kapısını da bağlar: `route` planlayıcı
üzerinden denenmeden enhancer **seçilemez**, ve bunu kapı **kendisi** zorlar — bir kural
olarak yazılmadı. (*"Kural denetlenemezse kural değildir."*)
"""

from __future__ import annotations

import inspect

import pytest

from app import planner as _planner
from app import tools
from app.routers import ask as ask_mod


# --- ARAÇ KAYDI + DÖRT KAPI ------------------------------------------------------

def test_ARAC_KAYITLI():
    a = next((x for x in tools.KAYIT if x.ad == "llm.prompt_enhance"), None)
    assert a is not None, "kapısız LLM çağrısı — araç kaydında YOK"
    assert a.determinizm == "llm" and a.yan_etki == "yok" and a.maliyet == "ucuz"


def test_DETERMINISTIK_ONCE_kapisi_ROUTEu_ZORUNLU_kiliyor():
    """Etiket paylaşımı kapının mekanizmasıdır: `route` ile aynı `sorgu-uretimi`
    etiketini taşımasaydı kapı hiç ateşlemezdi ve "önce route" bir YORUM olurdu."""
    eh = next(x for x in tools.KAYIT if x.ad == "llm.prompt_enhance")
    rt = next(x for x in tools.KAYIT if x.ad == "route")
    assert set(eh.etiketler) & set(rt.etiketler), "kapı bağlanmamış — etiket paylaşımı yok"

    plan = _planner.Planlayici(principal=None, butce=_planner.Butce(adim=3, saniye=5, sorgu=0),
                               kaynaklar={})
    with pytest.raises(_planner.AracReddi, match="DETERMİNİSTİK-ÖNCE"):
        plan.calistir("llm.prompt_enhance", "soru", "katalog")


def test_PLANLAYICIDAN_gecer_makbuzda_ADIM_uretir():
    govde = inspect.getsource(ask_mod._prompt_enhance_dene)
    assert 'plan.calistir("llm.prompt_enhance"' in govde, "kapısız çağrı"
    assert 'plan.calistir("route"' in govde, \
        "route planlayıcıya kaydedilmiyor — kapı kendi kaydını göremez"


# --- DAVRANIŞ: kurtarma yolu, gerileme YOK ---------------------------------------

class _Sahte:
    def __init__(self, cikti):
        self.cikti, self.cagrildi = cikti, []

    def prompt_enhance(self, soru, catalog):
        self.cagrildi.append(soru)
        return self.cikti


class _Istek:
    def __init__(self, llm, app_state=None):
        class _S:
            principal = None
        self.state = _S()

        class _AS:
            pass
        _as = _AS()
        _as.llm = llm
        _as.datasets = {}

        class _App:
            state = _as
        self.app = _App()


def _dene(monkeypatch, llm, ham, schema, wren):
    monkeypatch.setattr(ask_mod, "_service_for", lambda *a, **k: wren)
    return ask_mod._prompt_enhance_dene(
        _Istek(llm), ham, __import__("app.cube_router", fromlist=["x"])._norm(ham),
        schema, None, liste=False)


def test_SAGLAYICI_YOKSA_yol_KAPALI(schema, wren, monkeypatch):
    class _Kuralli:
        pass

    hit, iz = _dene(monkeypatch, _Kuralli(), "hasılatımız ne kadar", schema, wren)
    assert hit is None and iz is None


def test_LLM_PATLARSA_bugunku_yol(schema, wren, monkeypatch):
    class _Patlak:
        def prompt_enhance(self, soru, catalog):
            raise RuntimeError("sağlayıcı yok")

    hit, _ = _dene(monkeypatch, _Patlak(), "hasılatımız ne kadar", schema, wren)
    assert hit is None, "enhancer patladığında cevap bozulmamalı"


def test_DEGISMEYEN_metin_yeni_bilgi_DEGIL(schema, wren, monkeypatch):
    soru = "zxqw plmk asdf"
    hit, _ = _dene(monkeypatch, _Sahte(soru), soru, schema, wren)
    assert hit is None


def test_COZULEMEYEN_iyilestirme_bugunku_yola_DUSER(schema, wren, monkeypatch):
    hit, _ = _dene(monkeypatch, _Sahte("qwerty zxcvbn asdfgh"), "zxqw plmk", schema, wren)
    assert hit is None, "çözülemeyen metin yine de kabul edildi"


def test_BASARILI_yeniden_yazim_COZULUYOR(schema, wren, monkeypatch):
    """Asıl kazanç: kataloğun tanımadığı bir ifade, tanıdığı karşılığına çevrilince
    `route()` LLM'siz çözüyor."""
    hit, iz = _dene(monkeypatch, _Sahte("bu yıl ciro"), "bu yıl hasılatımız", schema, wren)
    assert hit is not None, "yeniden yazılmış soru çözülemedi"
    assert hit["cube_query"]["cube"]
    assert iz and "yeniden yazıldı" in iz


def test_MAKBUZ_izi_HER_IKI_metni_tasiyor(schema, wren, monkeypatch):
    """Kanonik soru SESSİZCE kullanılır ama KAYIT DIŞI kalmaz — denetçi hangi metnin
    çözüldüğünü görebilmeli (planın 2. şartı)."""
    hit, _ = _dene(monkeypatch, _Sahte("bu yıl ciro"), "bu yıl hasılatımız", schema, wren)
    prov = hit["cube_query"]["provenance_soru"]
    assert prov["question_original"] == "bu yıl hasılatımız"
    assert prov["question_normalized"] == "bu yıl ciro"


def test_COK_SATIRLI_cikti_TEK_satira_indirilir(schema, wren, monkeypatch):
    """Model açıklama eklerse ilk satır alınır — serbest metin sorguya sızmasın."""
    hit, _ = _dene(monkeypatch, _Sahte('"bu yıl ciro"\nAçıklama: hasılat = ciro'),
                   "bu yıl hasılatımız", schema, wren)
    assert hit is not None and hit["cube_query"]["cube"]


# --- PROMPT: yapı seçtirmiyor ----------------------------------------------------

def test_PROMPT_yapi_SECTIRMIYOR():
    from app import llm as llm_mod

    s = llm_mod._enhance_system("kat")
    assert "SQL, JSON" in s or "JSON" in s, "yapısal çıktı yasağı yok"
    assert "ANLAMI DEĞİŞTİRME" in s
    assert "uydurma bir terime çevirmek" in s, "uydurma yasağı yok"


def test_KURAL_TABANLI_saglayicida_YOK():
    from app import llm as llm_mod

    assert not hasattr(llm_mod.RuleBasedSqlGenerator, "prompt_enhance")


def test_FAILOVER_tasiyor():
    from app import llm as llm_mod

    assert hasattr(llm_mod.FailoverSqlGenerator, "prompt_enhance")
    govde = inspect.getsource(llm_mod.FailoverSqlGenerator.prompt_enhance)
    assert 'hasattr(g, "prompt_enhance")' in govde


# --- ÖN KOŞUL: Faz -1 gerçekten daraltıyor mu (planın açık şartı) -----------------

def test_ON_KOSUL_belirsizlikte_chip_DARALTILMIS(client):
    """Plan: *"enhancer belirsizlikte MEVCUT chip mekanizmasına devrediyor; o mekanizma
    Faz -1'de daraltılmadan enhancer 13-cube dump'ına devretmiş olur."*
    Bu, VARSAYILMAMASI gereken bir ön koşul — ölçülüyor."""
    d = client.post("/ask", json={"question": "son 6 ay personel bazlı çalışma süreleri kıyasla",
                                  "session_id": "3b", "execute": False}).json()
    chips = d.get("suggestions") or []
    assert len(chips) < 13, f"hâlâ 13-cube dump'ı: {len(chips)} chip"


# --- KURAL B ---------------------------------------------------------------------

def test_VARSAYILAN_KAPALI(client, monkeypatch):
    """Sıcak yola LLM çağrısı ekliyor; açılması bilinçli karar olmalı."""
    from app import features
    from app.config import get_settings

    assert "prompt_enhancer" not in features.resolve_for(get_settings(), None)


def test_YAML_off_TUZAGI_kapali():
    """⚠️ **BU TUZAK BU FAZDA GERÇEKTEN ISIRDI.**

    `features.yml`'e `prompt_enhancer: off` yazdım. YAML 1.1 `off`/`on`/`yes`/`no`
    değerlerini **boolean** olarak okur — yani değer `"off"` STRING'i değil `False`
    oldu. `resolve_for`'un filtresi (`if v != "off"`) onu **elemedi** ve bayrak
    `resolve_for(...)` sonucunda **var** kaldı: `"prompt_enhancer" in ...` → **True**.
    İki bayrak (bu ve `t2_anlatici`) **sessizce AÇIKTI**.

    Tam olarak bu oturumda on kez avladığım sınıf — *"beyan var, kod onu tanımıyor"* —
    bu kez **kendi kodumda**. Ve Faz 5'in kendi testi bunu YAKALAYAMAMIŞTI, çünkü
    kural-tabanlı sağlayıcıda `anlat` olmadığı için yol zaten kapalıydı: bayrak açık
    olduğu hâlde davranış doğru görünüyordu.

    Kapı: `features.yml`'deki HİÇBİR bayrak boolean OLAMAZ. Aşama adları
    (`off|alpha|beta|prod`) STRING'dir ve tırnaklanmalıdır.
    """
    import pathlib

    import yaml

    from app.features import STAGES

    def _tara(d, yol_=""):
        for k, v in (d or {}).items():
            if isinstance(v, dict):
                _tara(v, f"{yol_}{k}.")
            else:
                assert not isinstance(v, bool), (
                    f"{yol_}{k} = {v!r} — YAML `off/on/yes/no`'yu BOOLEAN okur ve "
                    f"`resolve_for` onu ELEMEZ: bayrak sessizce AÇIK kalır. Tırnakla: "
                    f'`{k}: "off"`')
                assert v in STAGES, f"{yol_}{k} = {v!r} — geçerli aşama değil {STAGES}"

    # ⟳ FAZ 9.12 — KAPI YARIM KAPALIYDI. Yalnız `demo/packs/features.yml` taranıyordu;
    # ama `features.py` AYNI dönüşümü sektör pack'lerine ve şirket dosyalarına da
    # uyguluyor (`resolve_for` katman katman birleştirir). Bugün oralar boş → tuzak
    # ısırmıyor; yarın `oee_ozel: off` yazan **aynı sessiz-AÇIK** kapanına düşer ve CI
    # yeşil kalır. Bir kapının "bugün ısırmıyor" olması, kapsamının doğru olduğunu
    # göstermez — bu oturumda ölçülen `-0.5c` kusuruyla aynı sınıf.
    kok = pathlib.Path(__file__).resolve().parents[1]
    adaylar = [kok / "demo" / "packs" / "features.yml",
               *sorted((kok / "demo" / "packs" / "sektor").glob("*/pack.yml")),
               *sorted((kok / "demo" / "companies").glob("*/company.yml"))]
    tarandi = 0
    for yol in adaylar:
        if not yol.exists():
            continue
        veri = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        blok = veri.get("features") if isinstance(veri, dict) else None
        if blok is None and yol.name == "features.yml":
            blok = veri
        if not blok:
            continue
        tarandi += 1
        _tara(blok, f"{yol.name}:")
    assert tarandi >= 1, "hiçbir features bloğu taranmadı — kapı BOŞA koşuyor"
