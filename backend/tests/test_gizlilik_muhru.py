"""FAZ 9.1 — `/ask` DIŞINDAKİ veri döndüren uçlarda PII maskesi ve audit YOKTU.

## Denetimde ölçülen kusur

`app/answer.py`'nin modül değişmezi *"**her** yanıt buradan geçer"* diyordu. İki uçta
**geçerli değildi**:

| uç | dönüş noktası | audit | PII maskesi |
|---|---|---|---|
| `POST /ask/drill` | **8** | yalnız `raw` dalında | **hiçbirinde** |
| `POST /ask/contribution` | 2 | yok | yok |

Taşıdıkları veri hassas: `DrillResponse.result` **satır**, `.anomalies` ve
`ContributionResponse.raporlar` **boyut değerleri** — bu katalogda `musteri` · `operator`
· `calisan` gerçek boyutlardır. Yani aynı kırılım `/ask`'ten maskeli, `/ask/drill`'den
**maskesiz** dönüyordu.

Kodun kendi yorumu `raw` dalı için bunun *"önceden hiç çalışmadığını"* kaydetmişti —
**kardeş dallar açık kalmıştı.** Deponun kendi *"kimlik asimetrisi"* sınıfı (MIMARI §6.1h):
kural bir dalda uygulanıyor, kardeşinde uygulanmıyor.

## Neden gövde SARMALANDI, sekiz dönüş noktası yamanmadı

Yamamak, **dokuzuncu** dönüş noktasını ekleyen kişinin unutmasına açık kalırdı — tam
olarak bu kusurun doğuş biçimi. Sarmal **yeni dallar dâhil** hepsini kapsar.
"""

from __future__ import annotations

import inspect

from app.pii import muhurle
from app.routers import ask as ask_mod
from app.schemas import ContributionResponse, DrillResponse, QueryResult

#: `mask_rows`'un tanıdığı gerçek bir PII deseni (TCKN checksum'lı) — uydurma bir dize
#: maskelenmez ve test yanlışlıkla yeşil kalırdı.
TCKN = "10000000146"


class _Istek:
    class state:  # noqa: N801
        principal = None

    class client:  # noqa: N801
        host = "127.0.0.1"


# --- SARMAL: yeni dallar da kapsanıyor -------------------------------------------

def test_GOVDE_SARMALANDI_dokuzuncu_dal_da_kapsanir():
    """Sekiz dönüş noktasını tek tek yamamak, dokuzuncuyu ekleyenin unutmasına açık
    kalırdı — bu kusurun doğuş biçimi tam olarak buydu."""
    for uc, govde in (("ask_drill", "_ask_drill_govde"),
                      ("ask_contribution", "_ask_contribution_govde")):
        dis = inspect.getsource(getattr(ask_mod, uc))
        assert f"{govde}(request, body)" in dis, f"{uc} gövdeyi sarmalamıyor"
        assert "muhurle(" in dis, f"{uc} gizlilik mührünü uygulamıyor"
        assert hasattr(ask_mod, govde), f"{govde} yok"


def test_MUHUR_cevabi_DUSURMEZ_ama_SESSIZ_de_kalmaz():
    for uc in ("ask_drill", "ask_contribution"):
        dis = inspect.getsource(getattr(ask_mod, uc))
        assert "except Exception" in dis and "_log.warning" in dis, \
            f"{uc}: mühür hatası ya cevabı düşürüyor ya sessizce yutuluyor"


# --- MASKELEME: gerçekten uyguluyor mu -------------------------------------------

def test_DRILL_SATIRLARI_maskeleniyor():
    r = DrillResponse(
        formula_explanation="x",
        result=QueryResult(columns=["musteri"], rows=[{"musteri": TCKN}], row_count=1))
    muhurle(r, _Istek, None, ad="t")
    assert r.result.rows[0]["musteri"] != TCKN, "TCKN maskelenmedi"


def test_RAW_ROWS_da_maskeleniyor():
    from app.schemas import RawRow

    r = DrillResponse(formula_explanation="x",
                      raw_rows=RawRow(columns=["a"], rows=[{"a": TCKN}], row_count=1))
    muhurle(r, _Istek, None, ad="t")
    assert r.raw_rows.rows[0]["a"] != TCKN


def test_KATKI_BULGU_ETIKETI_maskeleniyor():
    """Satır maskelenip etiket maskelenmeseydi kapı YARIM kalırdı ve tam da en GÖRÜNÜR
    yerden sızardı: `musteri` kırılımında bulgu etiketi **doğrudan kişi adıdır**.

    ⚠️ İlk sürümde `ContributionReport.segment` diye **var olmayan** bir alanı
    maskeliyordum; test onu yakaladı. Alan adları artık ŞEMADAN doğrulanmış."""
    from app.schemas import ContributionFinding, ContributionReport

    r = ContributionResponse(raporlar=[ContributionReport(
        dimension="musteri", dimension_label="Müşteri", net_degisim=0.0,
        brut_hareket=0.0,
        bulgular=[ContributionFinding(label=TCKN, deger=TCKN,
                                     cube_query={"cube": "parti"})])])
    muhurle(r, _Istek, None, ad="t")
    assert r.raporlar[0].bulgular[0].label != TCKN, "bulgu etiketi maskelenmedi"


def test_ANOMALI_DEGERI_maskeleniyor():
    from app.schemas import DrillAnomaly

    r = DrillResponse(formula_explanation="x", anomalies=[
        DrillAnomaly(dimension="musteri", value=TCKN, amount=1.0,
                     direction="above", z_score=3.0)])
    muhurle(r, _Istek, None, ad="t")
    assert r.anomalies[0].value != TCKN, "anomali değeri maskelenmedi"


def test_PII_OLMAYAN_veri_BOZULMUYOR():
    """Kapı fazla geniş olmamalı: normal boyut değerleri aynen kalmalı."""
    r = DrillResponse(
        formula_explanation="x",
        result=QueryResult(columns=["makine"], rows=[{"makine": "RAM-2"}], row_count=1))
    muhurle(r, _Istek, None, ad="t")
    assert r.result.rows[0]["makine"] == "RAM-2"


# --- AUDIT: "başarı audit'siz raporlanamaz" ---------------------------------------

def test_AUDIT_HER_ZAMAN_atiliyor(monkeypatch):
    from control_plane import audit

    kayitlar: list[str] = []
    monkeypatch.setattr(audit, "record",
                        lambda p, tur, **k: kayitlar.append(tur))
    muhurle(DrillResponse(formula_explanation="x"), _Istek, None, ad="t")
    assert "query" in kayitlar, "veri döndüren uç audit'siz kaldı"


def test_PII_GORULDUYSE_AYRI_audit(monkeypatch):
    """KVKK: hangi PII'yi kim gördü — `pii:view` yetkilisi maskesiz görür ve bu AYRI bir
    audit satırıdır."""
    from control_plane import audit

    kayitlar: list[str] = []
    monkeypatch.setattr(audit, "record", lambda p, tur, **k: kayitlar.append(tur))
    monkeypatch.setattr("control_plane.authorize.can", lambda p, izin: True)

    class _P:
        user_id = tenant_id = None

    r = DrillResponse(
        formula_explanation="x",
        result=QueryResult(columns=["a"], rows=[{"a": TCKN}], row_count=1))
    muhurle(r, _Istek, _P(), ad="t")
    assert r.result.rows[0]["a"] == TCKN, "yetkili maskesiz görmeliydi"
    assert "pii_view" in kayitlar, "maskesiz erişim audit'e yazılmadı"
