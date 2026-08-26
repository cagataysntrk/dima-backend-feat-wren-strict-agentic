"""FAZ 1 (Katman 7) — T7 GUARDED LLM MUHAKEME: `t2_anlatici`nin KARAR-DESTEĞİ kardeşi.

## Neden bu dosya `test_t2_anlatici.py`'yi BİREBİR taklit ediyor

`_tavsiye_ekle`, `_anlati_ekle`'nin AYNI iskeletidir (roadmap: "yeniden icat edilmez").
Bu dosyanın yapısı da öyle — aynı üç kilit test edilir:

**1. FAIL-CLOSED.** Uydurma bir sayı taşıyan cümle DÜŞER; hiçbir cümle sağ kalmazsa
`resp.prescription["muhakeme_metni"]` HİÇ YAZILMAZ — `rec.gerekce` (zaten
`resp.prescription["rationale"]`'da) yerinde kalır.

**2. ŞABLONU EZMEZ.** `options`/`rationale`/`concentration`/`diffuse` dokunulmaz;
yalnız yeni bir alt-alan (`muhakeme_metni`) eklenir.

**3. GİRDİ DAR + SEÇENEK KISITI.** Model yalnız `prescribe.recete()`'nin sıraladığı
`secenekler` üzerinde muhakeme kurar; segment adları PERDELENEREK gider (hava boşluğu).

⚠ **Bilinen sınır (dürüstçe kaydedilir, `_anlati_ekle` ile PAYLAŞILAN bir sınırdır,
YENİ değil):** guard zinciri SAYI halüsinasyonunu (`narration_guard`) ve ŞEMA-YETENEK
iddialarını (`iddia.py`) yakalar; modelin kendi ürettiği DÜZ METİN bir segment adı
(yer tutucu FORMATINDA değilse) hiçbir guard'dan geçmez — tıpkı `llm.anlat`ın metninde
`{{NUM_i}}` DIŞINDA bir sayı üretse bile yakalanabilmesi, ama tamamen ilgisiz bir CÜMLE
uydurabilmesinin (üslup düzeyinde) guard'ın kapsamı dışında kalması gibi. Hava boşluğu
(segment adları perdeleniyor) bu riski azaltır ama SIFIRLAMAZ — istem disiplini ikinci
savunma katmanıdır, birinci değil.
"""

from __future__ import annotations

import inspect

from app import answer as answer_mod
from app.prescribe import Oneri, Recete


class _SahteLLM:
    """Tavsiye sağlayıcı taklidi — üretilecek metni testin kendisi belirler."""

    def __init__(self, metin):
        self.metin, self.cagrildi = metin, []

    def tavsiye_et(self, soru, gercekler, secenekler):
        self.cagrildi.append((soru, list(gercekler), list(secenekler)))
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


_RAPOR = {"net_degisim": 1000.0, "brut_hareket": 3000.0,
          "bulgular": [{"label": "RAM-3", "delta": -1800.0, "net_pay": -0.6,
                        "cube_query": {"cube": "oee", "measures": ["ort_oee"]}},
                       {"label": "RAM-5", "delta": 900.0, "net_pay": 0.3,
                        "cube_query": {"cube": "oee", "measures": ["ort_oee"]}}]}


def _rec(*, tek=False):
    """İki (ya da tek) önerili bir `Recete` — `prescribe.recete()`'yi TEKRAR
    KOŞMADAN doğrudan kurulur (bu dosyanın sınadığı şey `_tavsiye_ekle`'nin KENDİ
    mantığıdır, `recete()`'nin aritmetiği `test_recete.py`'nin işidir)."""
    oneriler = [Oneri(segment="RAM-3", etki=-1800.0, pay=-0.6, yon="kotulesti",
                      cube_query={"cube": "oee", "measures": ["ort_oee"],
                                 "filters": [{"dimension": "makine", "operator": "eq",
                                             "value": "RAM-3"}]})]
    if not tek:
        oneriler.append(Oneri(segment="RAM-5", etki=900.0, pay=0.3, yon="iyilesti",
                              cube_query={"cube": "oee", "measures": ["ort_oee"],
                                         "filters": [{"dimension": "makine",
                                                     "operator": "eq",
                                                     "value": "RAM-5"}]}))
    return Recete(oneriler=oneriler, yogunlasma=0.6, dagitik=False,
                  gerekce="Değişim yoğunlaşmış (en büyük segment brüt hareketin %60'ı). "
                          "1 segment ters yönde hareket etmiş; önce onlara bakmak en "
                          "yüksek getirili adım.")


def _prescription_payload(rec):
    return {"options": [{**o.makbuza(), "cube_query": o.cube_query} for o in rec.oneriler],
            "concentration": rec.yogunlasma, "diffuse": rec.dagitik,
            "rationale": rec.gerekce, "measure": "ort_oee"}


def _kos(monkeypatch, llm, rec, *, bayrak_acik=True, rapor=None):
    from app import features
    from app.schemas import AskResponse

    monkeypatch.setattr(
        features, "resolve_for",
        lambda *a, **k: {"t7_tavsiye": "beta"} if bayrak_acik else {})
    resp = AskResponse(question="ram 3 için hangisi en etkili", sql="SELECT 1",
                       planned_sql=None, result=None, source="cube")
    resp.prescription = _prescription_payload(rec)
    answer_mod._tavsiye_ekle(_Istek(llm), resp, rapor or _RAPOR, rec,
                             lower_is_better=False)
    return resp


# --- FAIL-CLOSED -----------------------------------------------------------------

def test_UYDURMA_SAYI_yayimlanmaz(monkeypatch):
    """Guard'ın varlık sebebi. Metindeki `%87` `gercekler`de YOK — düşer."""
    rec = _rec()
    llm = _SahteLLM("RAM-3'e odaklanmak en mantıklısı, çünkü etkisi %87 daha büyük.")
    r = _kos(monkeypatch, llm, rec)
    assert "muhakeme_metni" not in r.prescription, \
        f"uydurma sayı yayımlandı: {r.prescription.get('muhakeme_metni')!r}"
    assert r.prescription["rationale"] == rec.gerekce, "şablon (gerekçe) kayboldu"


def test_DOGRU_MUHAKEME_yayimlanir(monkeypatch):
    """Yalnız `gercekler`de geçen sayılarla kurulmuş bir cümle guard'dan geçmeli."""
    rec = _rec()
    llm = _SahteLLM("RAM-3'e öncelik vermek mantıklı — etkisi -1.800 ile en büyük "
                    "ve net değişime payı -%60.")
    r = _kos(monkeypatch, llm, rec)
    assert r.prescription.get("muhakeme_metni"), \
        f"doğru sayılı cümle guard'da düştü, hava_boslugu={r.hava_boslugu!r}"


def test_KISMI_dusus_TEMIZ_cumleleri_KORUR(monkeypatch):
    """Kapı cerrahi: bir uydurma cümle yüzünden doğru cümleyi de atmak bilgi kaybettirir."""
    rec = _rec()
    llm = _SahteLLM("RAM-3'ün etkisi -1.800 ile en büyük. Ayrıca %999 iyileşme beklenir.")
    r = _kos(monkeypatch, llm, rec)
    m = r.prescription.get("muhakeme_metni") or ""
    assert "1.800" in m or "1800" in m, f"doğru cümle de düştü: {m!r}"
    assert "999" not in m, f"uydurma sayı sızdı: {m!r}"


# --- ŞABLONU EZMEZ -----------------------------------------------------------------

def test_OPTIONS_ve_RATIONALE_dokunulmaz(monkeypatch):
    rec = _rec()
    llm = _SahteLLM("RAM-3'e öncelik vermek mantıklı — etkisi -1.800 ile en büyük.")
    onceki_options = _prescription_payload(rec)["options"]
    r = _kos(monkeypatch, llm, rec)
    assert r.prescription["options"] == onceki_options
    assert r.prescription["rationale"] == rec.gerekce


def test_KAYNAK_KODU_deterministik_alanlari_YAZMIYOR():
    govde = inspect.getsource(answer_mod._tavsiye_ekle)
    for alan in ('resp.prescription["options"] =', 'resp.prescription["rationale"] ='):
        assert alan not in govde, f"tavsiye deterministik alanı EZİYOR: {alan}"


# --- KURAL B: bayrak + sağlayıcı + öneri sayısı ------------------------------------

def test_BAYRAK_KAPALIYKEN_hic_calismaz(monkeypatch):
    rec = _rec()
    llm = _SahteLLM("RAM-3'e öncelik vermek mantıklı — etkisi -1.800.")
    r = _kos(monkeypatch, llm, rec, bayrak_acik=False)
    assert "muhakeme_metni" not in r.prescription
    assert not llm.cagrildi, "bayrak kapalıyken LLM ÇAĞRILDI — bütçe/gizlilik ihlali"


def test_SAGLAYICI_YOKSA_yol_KAPALI_hata_DEGIL(monkeypatch):
    class _Kuralli:
        pass

    r = _kos(monkeypatch, _Kuralli(), _rec())
    assert "muhakeme_metni" not in r.prescription


def test_LLM_PATLARSA_cevap_DUSMEZ(monkeypatch):
    class _Patlak:
        def tavsiye_et(self, soru, gercekler, secenekler):
            raise RuntimeError("sağlayıcı yok")

    rec = _rec()
    r = _kos(monkeypatch, _Patlak(), rec)
    assert r.prescription["rationale"] == rec.gerekce
    assert "muhakeme_metni" not in r.prescription


def test_TEK_ONERIDE_LLM_CAGRILMAZ(monkeypatch):
    """ŞABLON-ÖNCE: tek adayda `rec.gerekce` zaten TEK cevaptır — LLM'e gitmek süstür."""
    llm = _SahteLLM("herhangi")
    r = _kos(monkeypatch, llm, _rec(tek=True))
    assert not llm.cagrildi, "tek adayda LLM çağrıldı — gereksiz gecikme/maliyet"
    assert "muhakeme_metni" not in r.prescription


def test_PRESCRIPTION_YOKSA_CAGRILMAZ(monkeypatch):
    from app import features
    from app.schemas import AskResponse

    monkeypatch.setattr(features, "resolve_for", lambda *a, **k: {"t7_tavsiye": "beta"})
    llm = _SahteLLM("herhangi")
    resp = AskResponse(question="x", result=None, source="cube")
    resp.prescription = None
    answer_mod._tavsiye_ekle(_Istek(llm), resp, _RAPOR, _rec(), lower_is_better=False)
    assert not llm.cagrildi


# --- GİRDİ DAR: segment adları PERDELENEREK gider ----------------------------------

def test_SECENEKLER_PERDELENEREK_gider(monkeypatch):
    """Model gerçek segment adını (`RAM-3`) DEĞİL, yer tutucuyu görür."""
    rec = _rec()
    llm = _SahteLLM("{{DIM_1}} önceliklidir — etkisi -1.800 ile en büyük.")
    _kos(monkeypatch, llm, rec)
    (soru, gercekler, secenekler), = llm.cagrildi
    assert soru == "ram 3 için hangisi en etkili"
    assert not any("RAM-3" in s for s in secenekler), \
        f"gerçek segment adı sağlayıcıya SIZDI: {secenekler}"
    assert any("{{DIM_" in s for s in secenekler)


def test_PROMPT_secenek_disina_cikmayi_YASAKLIYOR():
    from app import llm as llm_mod

    s = llm_mod._tavsiye_system()
    assert "YALNIZ verilen SEÇENEKLER listesindeki" in s
    assert "HİÇBİR YENİ SAYI ÜRETME" in s


# --- ARAÇ KAYDI: kapısız LLM çağrısı yok -------------------------------------------

def test_ARAC_KAYDINDA():
    from app import tools

    a = next((x for x in tools.KAYIT if x.ad == "llm.tavsiye_et"), None)
    assert a is not None, "`llm.tavsiye_et` araç kaydında YOK — kapısız LLM çağrısı"
    assert a.determinizm == "llm" and a.yan_etki == "yok"
    assert "karar-recete" in a.etiketler


def test_DETERMINISTIK_ONCE_KARDESI_KAYITLI():
    """`prescribe.recete` ('karar-recete' etiketi) `llm.tavsiye_et`'in DETERMİNİSTİK-ÖNCE
    kardeşidir — `_deterministik_once_kapisi`'nin bu ikisini eşleştirebilmesi için
    ikisi de aynı etikette olmalı."""
    from app import tools

    kardes = next((x for x in tools.KAYIT if x.ad == "prescribe.recete"), None)
    hedef = next((x for x in tools.KAYIT if x.ad == "llm.tavsiye_et"), None)
    assert kardes is not None and kardes.determinizm == "deterministik"
    assert set(kardes.etiketler) & set(hedef.etiketler), \
        "prescribe.recete ile llm.tavsiye_et ORTAK etiket taşımıyor — gate kör kalır"


def test_KOK_NEDEN_YOLU_FARKLI_KARDESE_BAGLI():
    """🔴 `llm.tavsiye_et`'in İKİ çağrı yeri (prescribe.py/kok_neden.py) FARKLI
    deterministik kardeşe bağlı olmalı — TEK bir Arac'ın hem 'karar-recete' hem
    'karar-kok' taşıması, gate'i HER İKİ çağrı yerini HER İKİ kardeşe bağımlı kılardı
    (ölçüldü: `AracReddi`, bu dosyanın ilk yazımında). Bu yüzden AYNI Python metoduna
    (`app.llm.tavsiye_et`) bağlı İKİNCİ bir `Arac` (`llm.tavsiye_et_kok_neden`) var."""
    from app import tools

    recete_yolu = next((x for x in tools.KAYIT if x.ad == "llm.tavsiye_et"), None)
    kok_yolu = next((x for x in tools.KAYIT if x.ad == "llm.tavsiye_et_kok_neden"), None)
    assert recete_yolu is not None and kok_yolu is not None
    assert recete_yolu.modul == kok_yolu.modul == "app.llm"
    assert recete_yolu.fonksiyon == kok_yolu.fonksiyon == "tavsiye_et"
    assert not (set(recete_yolu.etiketler) & set(kok_yolu.etiketler) - {"t7", "guardli"}), \
        "iki çağrı yeri hâlâ ORTAK bir 'karar-*' etiketi paylaşıyor — çapraz bulaşma geri geldi"
    prescribe_kardes = next((x for x in tools.KAYIT if x.ad == "prescribe.recete"), None)
    kok_kardes = next((x for x in tools.KAYIT if x.ad == "kok_neden.ayristir"), None)
    assert set(prescribe_kardes.etiketler) & set(recete_yolu.etiketler)
    assert set(kok_kardes.etiketler) & set(kok_yolu.etiketler)
    assert not (set(prescribe_kardes.etiketler) & set(kok_yolu.etiketler)), \
        "prescribe.recete kok_neden yoluna da kardeş oluyor — kok_yolu artık YANLIŞLIKLA prescribe.recete'yi de ister"
    assert not (set(kok_kardes.etiketler) & set(recete_yolu.etiketler)), \
        "kok_neden.ayristir prescribe yoluna da kardeş oluyor — recete_yolu artık YANLIŞLIKLA kok_neden.ayristir'i de ister"


def test_FAILOVER_tavsiye_et_TASIYOR():
    from app import llm as llm_mod

    assert hasattr(llm_mod.FailoverSqlGenerator, "tavsiye_et")
    govde = inspect.getsource(llm_mod.FailoverSqlGenerator.tavsiye_et)
    assert 'hasattr(g, "tavsiye_et")' in govde, "sağlayıcı yokluğu hata sayılıyor"


def test_KURAL_TABANLI_saglayicida_tavsiye_et_YOK():
    from app import llm as llm_mod

    assert not hasattr(llm_mod.RuleBasedSqlGenerator, "tavsiye_et")
    assert not hasattr(llm_mod.NoLlmGenerator, "tavsiye_et")


# --- DETERMİNİSTİK-ÖNCE KAPISI KENDİ KAYDINI GÖRMELİ -------------------------------

def test_TAVSIYE_PLANLAYICIDAN_geciyor():
    govde = inspect.getsource(answer_mod._tavsiye_ekle)
    assert 'calistir("llm.tavsiye_et"' in govde, "kapısız LLM çağrısı"
    assert 'calistir("prescribe.recete"' in govde, (
        "DETERMİNİSTİK-ÖNCE kapısı kendi kaydını görmüyor — `prescribe.recete` "
        "(aynı `karar` etiketinin LLM'siz kardeşi) planlayıcı üzerinden denenmeli")


def test_G5_1_IDDIA_KAPISI_ON_KOSUL():
    govde = inspect.getsource(answer_mod._tavsiye_ekle)
    assert "G5.1" in govde
    assert "import app.iddia" in govde, "tavsiye iddia kapısını KONTROL ETMİYOR"


def test_ZINCIR_SIRASI_TAM():
    """perdele (G0b) → LLM → geri koy (G0b) → iddia (G4) → guard (rakam)."""
    govde = inspect.getsource(answer_mod._tavsiye_ekle)
    sira = [govde.index(x) for x in
            ("from app.yayilim import geri_koy, perdele",
             'plan.calistir("llm.tavsiye_et"',
             "_iddia.dogrula(ham",
             "guvenli_anlatim(")]
    assert sira == sorted(sira), f"tavsiye zincirinin sırası bozulmuş: {sira}"
