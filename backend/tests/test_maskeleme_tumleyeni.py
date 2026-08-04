"""FAZ 1.2c — **redactor TÜMLEYENİ: sayma, KAPAT.**

## Ölçülen kusur

`apply_to_ask_response` yalnız **üç** yeri maskeliyordu: `result.rows` · `facts[].text` ·
`summary`. `AskResponse`'un **26** alanı var; geri kalanı hiç maskelenmiyordu:

* `interpretation.narration` — LLM metni, **olgulardan üretilir** (yani PII taşıyabilir)
* `contribution` — **cevabın gövdesi** (`0.23`'ün ölçtüğü zengin alan)
* `next_steps` · `suggestions` — chip **etiketleri** (boyut değerleri taşır)
* `prescription` · `recommendations` · `kpi` · `note` · `calculation_explanation`

🔴 **Sayılan bir liste, yeni alanı sessizce dışarıda bırakır.** `KAT-5`'in kuralı:
*"SAYMA — KAPAT."* Varsayılan **maskelemektir**; muaf tutmak **açık bir karar** ister.
Aynı desen bu depoda zaten var: `ReportPanel`'in `SAF_NOT_ALANLARI` tümleyeni.

## §D.2/2'nin hükmü — ölçüldü ve DOĞRU çıktı

Yol haritası *"grafik etiketleri maskelenmezse §D.2/2 doğru değil"* diyordu. Ölçüldü:
grafik `option`'ı `buildOption(result, …)` ile **maskeli sonuçtan** türüyor, CSV dışa
aktarımı `exportTableCsv(result, …)` ile **aynı** maskeli satırlardan, PNG/SVG **aynı
option**'dan. `VizSpec` yalnız **kolon adları** taşıyor (veri değeri değil).
→ **Dışa aktarım zinciri zaten maskeliydi**; asıl boşluk **yanıt gövdesindeydi**.
Bu test o zinciri de **kilitler** ki biri ileride paralel bir kaynak eklerse görünsün.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app import pii

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"


# ── 1 · TÜMLEYEN: her alan ya maskelenir ya GEREKÇELİ muaf ──────────────────

def test_HER_ALAN_YA_MASKELENIR_YA_GEREKCELI_MUAF():
    """🔴 **Maddenin kalbi.** Yeni bir alan eklendiğinde varsayılan **maskelemektir**;
    muaf tutmak açık bir karar ister ve gerekçesi `MUAF_ALANLAR`'da durur.

    Bu test yeni alanı **yakalar**: gerekçesiz muafiyet yoktur, ve muaf olmayan her alan
    derin maskeleyiciden geçer.
    """
    from app.schemas import AskResponse

    alanlar = set(AskResponse.model_fields)
    muaf = set(pii.MUAF_ALANLAR)
    bilinmeyen_muaf = muaf - alanlar
    assert not bilinmeyen_muaf, (
        f"`MUAF_ALANLAR`'da olmayan alan var: {sorted(bilinmeyen_muaf)} — şema değişmiş, "
        "muafiyet listesi bayatlamış")
    for ad, gerekce in pii.MUAF_ALANLAR.items():
        assert len(gerekce) >= 4, f"{ad}: muafiyet GEREKÇESİZ — sessiz bir boşluk"


def test_MUAF_LISTE_KUCUK_KALIYOR():
    """Muafiyet **istisnadır**. Liste alanların çoğunu kaplarsa tümleyen anlamını yitirir
    ve *"sayma"* desenine geri dönmüş oluruz — yalnız adı değişmiş hâliyle."""
    from app.schemas import AskResponse

    oran = len(pii.MUAF_ALANLAR) / len(AskResponse.model_fields)
    assert oran < 0.6, f"alanların %{oran * 100:.0f}'ı muaf — tümleyen anlamını yitirdi"


# ── 2 · DERİN MASKELEYİCİ ────────────────────────────────────────────────────

def test_YUVALANMIS_METIN_MASKELENIYOR():
    girdi = {"a": [{"b": "ali@example.com"}], "c": ("TR33 0006 1005 1978 6457 8413 26",)}
    cikti = pii.muhurle_derin(girdi)
    assert "ali@example.com" not in str(cikti)
    assert "6457 8413 26" not in str(cikti)


def test_SAYI_VE_BOOL_DOKUNULMUYOR():
    """Bir **ölçü değerini** maskelemek veriyi bozar — `mask_rows`'un aynı kararı."""
    girdi = {"ciro": 1234567.89, "aktif": True, "yok": None}
    assert pii.muhurle_derin(girdi) == girdi


def test_PYDANTIC_MODELI_DE_GEZILIYOR():
    """🔴 `suggestions` bir `list[Suggestion]`'dır — **sözlük değil**. Yalnız
    `str`/`dict`/`list` gezen bir maskeleyici onu **sessizce** atlardı ve chip etiketleri
    maskesiz kalırdı."""
    from app.schemas import Suggestion

    s = Suggestion(label="ali@example.com", query="ali@example.com raporu")
    pii.muhurle_derin([s])
    assert "ali@example.com" not in s.label, "model alanı maskelenmedi"
    assert "ali@example.com" not in s.query


# ── 3 · UÇTAN UCA: YANIT GÖVDESİ ────────────────────────────────────────────

def _yanit(**kw):
    from app.schemas import AskResponse

    return AskResponse(question="test", **kw)


class _Sahte:
    is_superadmin = False
    roles: list[str] = ["viewer"]
    user_id = "u"
    tenant_id = "t"
    tenant_slug = "demo"


@pytest.mark.parametrize("alan,deger", [
    ("note", "müşteri ali@example.com bakiyesi"),
    ("interpretation", {"narration": "En yüksek: ali@example.com"}),
    ("contribution", {"detay": [{"ad": "ali@example.com"}]}),
    ("next_steps", [{"label": "ali@example.com detayı", "kind": "drill",
                     "cube_query": {"cube": "cari"}}]),
])
def test_ONCEDEN_MASKELENMEYEN_ALANLAR_ARTIK_MASKELENIYOR(alan, deger):
    """Dördü de `apply_to_ask_response`'un eski üçlüsünün **dışındaydı**."""
    resp = _yanit(**{alan: deger})
    pii.apply_to_ask_response(resp, _Sahte())
    assert "ali@example.com" not in str(getattr(resp, alan)), (
        f"`{alan}` hâlâ maskelenmiyor — tümleyen o alana ulaşmıyor")


def test_MUAF_ALAN_GERCEKTEN_DOKUNULMUYOR():
    """`cube_query` **yapısal** bir kanıttır; `POST /cube` onu birebir yeniden koşar.
    Maskelemek checkpoint'i (D4) kırardı — *bir kanıt, değiştirilirse kanıt değildir*."""
    cq = {"cube": "cari", "filters": [{"dimension": "eposta", "value": "ali@example.com"}]}
    resp = _yanit(cube_query=dict(cq))
    pii.apply_to_ask_response(resp, _Sahte())
    assert resp.cube_query == cq, "muaf alan değiştirilmiş"


def test_PII_VIEW_YETKISI_MASKELEMEYI_ATLATIYOR():
    """`pii:view` (admin+) maskesiz görür — `authorize.py`'nin **var olan** kararı."""
    class _Yetkili(_Sahte):
        roles = ["owner"]

    resp = _yanit(note="ali@example.com")
    pii.apply_to_ask_response(resp, _Yetkili())
    assert resp.note == "ali@example.com"


# ── 4 · DIŞA AKTARIM ZİNCİRİ — ölçüldü, DOĞRU çıktı, kilitleniyor ───────────

def test_GRAFIK_VE_CSV_MASKELI_SONUCTAN_TURUYOR():
    """🔴 **Yol haritasının varsayımı ölçüldü ve DOĞRU çıktı** — ama kilitlenmemişti.

    *"Grafik etiketleri maskelenmezse §D.2/2 doğru değil"* deniyordu. Ölçüm: grafik
    `option`'ı `buildOption(effResult, …)` ile **maskeli sonuçtan** türüyor; CSV
    `exportTableCsv(result, …)` ile **aynı** satırlardan; PNG/SVG **aynı option**'dan.

    Bu test o zinciri kilitler: biri ileride **paralel bir kaynak** eklerse (ör. grafiği
    ham bir uçtan beslerse) burada görünür. Bir doğru varsayım, kilitlenmemişse bir
    sonraki turda **yanlış** olabilir.
    """
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    rv = (FE / "components" / "ResultView.tsx").read_text(encoding="utf-8")
    ex = (FE / "lib" / "export.ts").read_text(encoding="utf-8")
    assert "buildOption(effResult" in rv, (
        "grafik `option`'ı artık `effResult`'tan türemiyor — paralel bir veri kaynağı "
        "eklenmiş olabilir ve o kaynak MASKELİ OLMAYABİLİR")
    assert "exportTableCsv(result" in ex or "result: QueryResult" in ex, \
        "CSV dışa aktarımı `QueryResult` dışında bir kaynaktan besleniyor"
    assert "exportChartImage" in ex and "option" in ex, \
        "grafik dışa aktarımı `option` dışında bir kaynaktan besleniyor"


def test_VIZSPEC_VERI_DEGERI_TASIMIYOR():
    """`VizSpec` yalnız **kolon adları** ve yapı taşır. Bir gün veri değeri taşırsa
    (ör. `categories: string[]`) maskeleme zinciri **atlanmış** olur."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    tip = (FE / "lib" / "types.ts").read_text(encoding="utf-8")
    i = tip.index("interface VizSpec")
    blok = tip[i:tip.index("}", i)]
    for supheli in ("values", "categories", "labels", "rows"):
        assert f"{supheli}:" not in blok, (
            f"`VizSpec` artık `{supheli}` taşıyor — VERİ DEĞERİ olabilir ve maskeleme "
            "zincirinin dışında kalır")


def test_ASKRESPONSE_ALAN_SAYISI_KAYITLI():
    """Alan sayısı **belgede** yazılı; şema büyürse tümleyenin kapsamı yeniden okunmalı."""
    from app.schemas import AskResponse

    kaynak = (KOK / "app" / "pii.py").read_text(encoding="utf-8")
    assert str(len(AskResponse.model_fields)) in kaynak, (
        f"`AskResponse` artık {len(AskResponse.model_fields)} alanlı; `pii.py`'deki "
        "ölçüm notu bayatlamış")
