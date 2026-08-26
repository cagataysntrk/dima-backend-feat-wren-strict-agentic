"""FAZ 1.4 (Katman 7) — `kok_neden.py` (§KN) için `_tavsiye_ekle`'nin karar-desteği
kardeşi: `answer._kok_tavsiye_ekle`.

## Bu dosyanın `test_t7_tavsiye.py`'den FARKI (kasıtlı, dikkatle tasarlandı)

`secenekler` burada bir SEGMENT/müşteri adı listesi DEĞİL, ölçünün FORMÜL
BİLEŞENLERİdir (kullanılabilirlik/performans/kalite gibi katalog sözlüğü) — bu yüzden
PERDELENMEZ (ticari/kişisel veri değil). Yalnız İNCELENEN SEGMENT hava boşluğundan
geçer.

## `GG8` kilidi

`kok_neden.ayristir`'in kendisi `lower_is_better` beyan edilmemiş bir ölçüde bir
"kötü/iyi" yargısı ÜRETMEZ (modülün kendi ilkesi). `Prescription` sözleşmesi her
seçenek için ZORUNLU bir `direction` istediğinden, yön bilinmiyorken bu basamak HİÇ
açılmaz — uydurma bir yargı üretmek yerine sessizce (bugünkü davranışla) geçilir.
"""

from __future__ import annotations

import inspect

from app import answer as answer_mod
from app.kok_neden import CARPAN, Ayristirma, Bilesen, Katki


class _SahteLLM:
    def __init__(self, metin):
        self.metin, self.cagrildi = metin, []

    def tavsiye_et(self, soru, gercekler, secenekler):
        self.cagrildi.append((soru, list(gercekler), list(secenekler)))
        return self.metin


class _Istek:
    def __init__(self, llm=None):
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


def _katki(ad, display, *, hedef, akran, katki, pay_yuzde):
    b = Bilesen(ad=ad, rol=CARPAN, yon=1, display=display)
    return Katki(bilesen=b, hedef=hedef, akran=akran, katki=katki, pay_yuzde=pay_yuzde)


def _ayr():
    """RAM-3 (OEE düşük) — kullanılabilirlik en çok açıklıyor. `pay_yuzde` toplamı
    100'e yaklaşan, gerçekçi bir üç-bileşenli ayrıştırma."""
    katkilar = [
        _katki("kullanilabilirlik", "kullanılabilirlik", hedef=70.0, akran=85.0,
              katki=-0.18, pay_yuzde=62.0),
        _katki("kalite", "kalite", hedef=98.0, akran=99.0, katki=-0.02, pay_yuzde=18.0),
        _katki("performans", "performans", hedef=90.0, akran=95.0, katki=-0.05,
              pay_yuzde=20.0),
    ]
    return Ayristirma(olcu="ort_oee", hedef_deger=55.8, akran_deger=68.0,
                      katkilar=katkilar, sucllu=katkilar[0].bilesen)


def _kos(monkeypatch, llm, ayr, *, bayrak_acik=True, yon_beyanli=True):
    from app import features
    from app.schemas import AskResponse

    monkeypatch.setattr(
        features, "resolve_for",
        lambda *a, **k: {"t7_tavsiye": "beta"} if bayrak_acik else {})
    cube_meta = {"lower_is_better": ["ort_oee"]} if yon_beyanli else {}
    resp = AskResponse(question="ram 3 neden böyle, hangisi en etkili", sql="SELECT 1",
                       planned_sql=None, result=None, source="cube")
    answer_mod._kok_tavsiye_ekle(_Istek(llm), resp, ayr, cube_meta,
                                 segment="RAM-3", boyut="makine")
    return resp


# --- FAIL-CLOSED -----------------------------------------------------------------

def test_UYDURMA_SAYI_yayimlanmaz(monkeypatch):
    llm = _SahteLLM("Kullanılabilirlik en çok açıklıyor, farkın %999'unu oluşturuyor.")
    r = _kos(monkeypatch, llm, _ayr())
    assert not r.prescription or "muhakeme_metni" not in r.prescription, \
        f"uydurma sayı yayımlandı: {r.prescription!r}"


def test_DOGRU_MUHAKEME_yayimlanir_ve_PRESCRIPTION_TAM_KURULUR(monkeypatch):
    """🔴 Yapısal doğruluk: `PrescriptionLayer.tsx` `recete.options.map(...)` yapar —
    `options`/`concentration`/`diffuse`/`rationale` EKSİK gelirse UI çöker. Bu test
    tam kuruluşu kilitler."""
    llm = _SahteLLM("Kullanılabilirlik en çok açıklıyor — 70,0 ↔ akran 85,0, "
                    "farkın %62'sini oluşturuyor.")
    r = _kos(monkeypatch, llm, _ayr())
    assert r.prescription, "prescription hiç kurulmadı"
    assert r.prescription.get("muhakeme_metni")
    assert r.prescription.get("muhakeme_kaynak") == "llm"
    assert isinstance(r.prescription.get("options"), list) and r.prescription["options"]
    for o in r.prescription["options"]:
        assert set(o) >= {"segment", "impact", "share", "direction"}
        assert o["direction"] in ("kotulesti", "iyilesti")
        assert 0.0 <= o["share"] <= 1.0 or o["share"] is None
    assert isinstance(r.prescription.get("concentration"), float)
    assert r.prescription.get("diffuse") is False
    assert r.prescription.get("rationale")
    assert r.prescription.get("measure") == "ort_oee"


def test_KISMI_dusus_TEMIZ_cumleleri_KORUR(monkeypatch):
    llm = _SahteLLM("Kullanılabilirlik 70,0 ↔ akran 85,0 ile en büyük fark. "
                    "Ayrıca %999 iyileşme beklenir.")
    r = _kos(monkeypatch, llm, _ayr())
    m = (r.prescription or {}).get("muhakeme_metni") or ""
    assert "70" in m or "85" in m, f"doğru cümle de düştü: {m!r}"
    assert "999" not in m, f"uydurma sayı sızdı: {m!r}"


# --- GG8: yön bilinmiyorsa HİÇ ÇALIŞMAZ --------------------------------------------

def test_YON_BEYANSIZSA_hic_calismaz(monkeypatch):
    """`lower_is_better` beyan edilmemiş bir ölçüde `direction` UYDURULAMAZ — bu
    basamak `kok_neden.ayristir`'in kendi ilkesini (`GG8`) miras alır."""
    llm = _SahteLLM("herhangi")
    r = _kos(monkeypatch, llm, _ayr(), yon_beyanli=False)
    assert not r.prescription
    assert not llm.cagrildi, "yön bilinmezken LLM ÇAĞRILDI — GG8 ihlali riski"


# --- KURAL B / sağlayıcı / şablon-önce ---------------------------------------------

def test_BAYRAK_KAPALIYKEN_hic_calismaz(monkeypatch):
    llm = _SahteLLM("herhangi")
    r = _kos(monkeypatch, llm, _ayr(), bayrak_acik=False)
    assert not r.prescription
    assert not llm.cagrildi


def test_SAGLAYICI_YOKSA_yol_KAPALI_hata_DEGIL(monkeypatch):
    class _Kuralli:
        pass

    r = _kos(monkeypatch, _Kuralli(), _ayr())
    assert not r.prescription


def test_LLM_PATLARSA_cevap_DUSMEZ(monkeypatch):
    class _Patlak:
        def tavsiye_et(self, soru, gercekler, secenekler):
            raise RuntimeError("sağlayıcı yok")

    r = _kos(monkeypatch, _Patlak(), _ayr())
    assert not r.prescription


def test_AZ_BILESENDE_LLM_CAGRILMAZ(monkeypatch):
    llm = _SahteLLM("herhangi")
    tek = Ayristirma(olcu="ort_oee", hedef_deger=55.8, akran_deger=68.0,
                     katkilar=[_katki("kullanilabilirlik", "kullanılabilirlik",
                                      hedef=70.0, akran=85.0, katki=-0.18,
                                      pay_yuzde=100.0)],
                     sucllu=None)
    r = _kos(monkeypatch, llm, tek)
    assert not llm.cagrildi
    assert not r.prescription


def test_PRESCRIPTION_ZATEN_DOLUYSA_TEKRAR_CALISMAZ(monkeypatch):
    from app import features
    from app.schemas import AskResponse

    monkeypatch.setattr(features, "resolve_for", lambda *a, **k: {"t7_tavsiye": "beta"})
    llm = _SahteLLM("herhangi")
    resp = AskResponse(question="x", result=None, source="cube")
    resp.prescription = {"muhakeme_metni": "önceden yazılmış"}
    answer_mod._kok_tavsiye_ekle(_Istek(llm), resp, _ayr(),
                                 {"lower_is_better": ["ort_oee"]},
                                 segment="RAM-3", boyut="makine")
    assert not llm.cagrildi
    assert resp.prescription["muhakeme_metni"] == "önceden yazılmış"


# --- GİRDİ: yalnız SEGMENT perdelenir, BİLEŞEN ADLARI perdelenmez -----------------

def test_SEGMENT_PERDELENIR_BILESEN_ADLARI_PERDELENMEZ(monkeypatch):
    llm = _SahteLLM("{{DIM_1}} için kullanılabilirlik en çok açıklıyor.")
    _kos(monkeypatch, llm, _ayr())
    (soru, gercekler, secenekler), = llm.cagrildi
    assert not any("RAM-3" in g for g in gercekler), \
        f"gerçek segment adı sağlayıcıya SIZDI: {gercekler}"
    assert any("{{DIM_" in g for g in gercekler)
    assert "kullanılabilirlik" in secenekler and "performans" in secenekler, \
        "bileşen adları (katalog sözlüğü) gereksiz yere perdelendi"


def test_PROMPT_secenek_disina_cikmayi_YASAKLIYOR():
    from app import llm as llm_mod

    s = llm_mod._tavsiye_system()
    assert "YALNIZ verilen SEÇENEKLER listesindeki" in s


# --- DETERMİNİSTİK-ÖNCE KAPISI KENDİ KAYDINI GÖRMELİ -------------------------------

def test_KOK_TAVSIYE_PLANLAYICIDAN_geciyor():
    govde = inspect.getsource(answer_mod._kok_tavsiye_ekle)
    assert 'calistir("llm.tavsiye_et_kok_neden"' in govde, "kapısız LLM çağrısı"
    assert 'calistir("kok_neden.ayristir"' in govde, (
        "DETERMİNİSTİK-ÖNCE kapısı kendi kaydını görmüyor — `kok_neden.ayristir` "
        "(aynı `karar-kok` etiketinin LLM'siz kardeşi) planlayıcı üzerinden denenmeli")


def test_G5_1_IDDIA_KAPISI_ON_KOSUL():
    govde = inspect.getsource(answer_mod._kok_tavsiye_ekle)
    assert "G5.1" in govde
    assert "import app.iddia" in govde


def test_ZINCIR_SIRASI_TAM():
    """perdele (G0b) → LLM → geri koy (G0b) → iddia (G4) → guard (rakam)."""
    govde = inspect.getsource(answer_mod._kok_tavsiye_ekle)
    sira = [govde.index(x) for x in
            ("from app.yayilim import geri_koy, perdele",
             'plan.calistir("llm.tavsiye_et_kok_neden"',
             "_iddia.dogrula(ham",
             "guvenli_anlatim(")]
    assert sira == sorted(sira), f"tavsiye zincirinin sırası bozulmuş: {sira}"


def test_KAYNAK_KODU_deterministik_alanlari_YAZMIYOR():
    govde = inspect.getsource(answer_mod._kok_tavsiye_ekle)
    # `resp.prescription = {...}` TÜMÜNÜ kurar (options/rationale dâhil) — bu satır
    # `_tavsiye_ekle`'deki "var olanı ezme" testinin karşılığı DEĞİL: burada
    # `resp.prescription` bugün BOŞ geliyordu (yeni kuruluyor), o yüzden `options`/
    # `rationale`'ı da BİRLİKTE kurmak EZMEK değil YARATMAKTIR (docstring'te gerekçeli).
    assert 'resp.prescription = {' in govde
