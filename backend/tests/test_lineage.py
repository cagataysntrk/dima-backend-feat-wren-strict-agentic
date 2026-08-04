"""FAZ 1.6 — **KOLON KÖKENİ** kapısı.

`answer.koken()` **ilişki** düzeyinde çalışıyordu (*hangi kırılım hangi join'den*);
cevaplayamadığı soru **kolon** düzeyindeydi: *"bu sayı hangi tablonun hangi kolonundan ve
hangi dönüşümle üretildi?"* İkisi farklı sorulardır — biri ötekinin **yerine geçmez**.
"""

from __future__ import annotations

import pathlib

import pytest

from app import lineage

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"

_SEMA = {
    "cubes": [{
        "name": "bakim",
        "base_object": "ariza_kayitlari",
        "measures": [
            {"name": "ariza_sayisi", "expression": "COUNT(*)"},
            {"name": "toplam_durus", "expression": "SUM(durus_dakika)"},
            {"name": "ort_durus", "expression": "ROUND(AVG(durus_dakika),1)"},
            {"name": "acik_oran", "expression": "CASE WHEN durum='acik' THEN 1 ELSE 0 END"},
            {"name": "kod", "expression": "ariza_kodu"},
        ],
        "dimension_origin": {"makine_adi": {"model": "makineler", "via": "makine_id"}},
    }],
}


# ── 1 · DÖNÜŞÜM TİPİ MANİFESTTEN TÜRÜYOR ────────────────────────────────────

@pytest.mark.parametrize("ifade,beklenen", [
    ("COUNT(*)", "toplam"),
    ("SUM(durus_dakika)", "toplam"),
    ("ROUND(AVG(durus_dakika),1)", "oran"),
    ("bozuk / toplam", "oran"),
    ("oran * 100", "oran"),
    ("CASE WHEN durum='acik' THEN 1 ELSE 0 END", "filtre"),
    ("SUM(x) FILTER (WHERE y=1)", "filtre"),
    ("ariza_kodu", "dogrudan"),
    ("", "turetilmis"),
    (None, "turetilmis"),
])
def test_DONUSUM_TIPI_IFADEDEN_TURUYOR(ifade, beklenen):
    """🔴 **Yeni bir BEYAN yazılmadı.** Katalog cevabı zaten taşıyordu (`expression`),
    yalnız sorulmuyordu. Bir `lineage:` alanı beyan ettirmek, bu deponun defalarca
    ölçtüğü *"ikinci bir kaynak açmak"* hatasını tekrarlardı."""
    assert lineage.donusum_tipi(ifade) == beklenen


def test_FILTRE_TOPLAMDAN_ONCE_SORULUYOR():
    """Sıra **önemli ve ölçüldü**: `CASE WHEN SUM(...)` bir **filtreli toplamdır** ve
    kullanıcıya söylenmesi gereken şey **daraltma**dır — toplam olduğu zaten görünür."""
    assert lineage.donusum_tipi("CASE WHEN a THEN SUM(x) END") == "filtre"


def test_ILISKIDEN_GELEN_BOYUT_BIRLESTIRME():
    assert lineage.donusum_tipi("makine_adi", iliskiden=True) == "birlestirme"


def test_ALTI_TIP_TAM():
    assert set(lineage.DONUSUM_TIPLERI) == {
        "dogrudan", "toplam", "oran", "filtre", "birlestirme", "turetilmis"}


# ── 2 · KÖKEN KAYDI ─────────────────────────────────────────────────────────

def test_OLCU_VE_BOYUT_KOKENI_CIKIYOR():
    k = lineage.kolon_kokeni(_SEMA, {
        "cube": "bakim", "measures": ["toplam_durus"], "dimensions": ["makine_adi"],
        "filters": [{"dimension": "bolum", "value": "boya"}]})
    assert k["olculer"][0]["donusum_tipi"] == "toplam"
    assert k["olculer"][0]["kaynak"] == "ariza_kayitlari"
    assert k["boyutlar"][0]["donusum_tipi"] == "birlestirme"
    assert k["boyutlar"][0]["kaynak"] == "makineler"
    assert k["filtreler"] == [{"boyut": "bolum", "deger": "boya"}]


def test_MASKELENDI_TEK_SAHIPTEN():
    """🔴 `sensitivity.classify` — **tek sahip**. İkinci bir hassasiyet kuralı yazmak,
    `pii.py` · CLS (`1.2a`) · köken üçlüsünün **ayrışması** demekti: aynı kolon bir yerde
    maskeli, ötekinde *"maskelenmedi"* diye raporlanırdı."""
    kaynak = (KOK / "app" / "lineage.py").read_text(encoding="utf-8")
    assert "from app.sensitivity import classify" in kaynak
    sema = {"cubes": [{"name": "c", "base_object": "t",
                       "measures": [{"name": "tc_kimlik", "expression": "tc_kimlik"}]}]}
    k = lineage.kolon_kokeni(sema, {"cube": "c", "measures": ["tc_kimlik"]})
    assert k["olculer"][0]["maskelendi"] is True


def test_CUBE_QUERY_YOKSA_NONE():
    assert lineage.kolon_kokeni(_SEMA, None) is None


def test_BILINMEYEN_CUBE_NONE():
    assert lineage.kolon_kokeni(_SEMA, {"cube": "yok", "measures": ["x"]}) is None


# ── 3 · «BİLİNMİYOR» ≠ «HİÇ SORULMADI» ──────────────────────────────────────

def test_BILINMIYOR_NONE_DEN_FARKLI():
    """🔴 Discovery ham SQL'inde `cube_query` **yoktur**; köken türetilemez.
    `"bilinmiyor"` bir eksiklik değil bir **beyandır** — `None` *"hiç sorulmadı"*,
    `"bilinmiyor"` *"soruldu, cevap yok"*. `⊘ ÖLÇÜLEMEDİ` üçüncü hâliyle aynı disiplin."""
    assert lineage.BILINMIYOR == "bilinmiyor"
    cumle = lineage.cumleler(lineage.BILINMIYOR)
    assert len(cumle) == 1 and "bilinmiyor" in cumle[0]
    assert lineage.cumleler(None) == []


# ── 4 · ŞABLON CÜMLELER — LLM'siz, teknik graf YOK (KD-13) ──────────────────

def test_CUMLELER_LLM_SIZ():
    kaynak = (KOK / "app" / "lineage.py").read_text(encoding="utf-8")
    assert "llm" not in kaynak.lower().replace("llm'siz", "").replace("llm’siz", ""), \
        "köken cümleleri LLM'e gidiyor — deterministik bir kanıt uydurmaya açılmış olur"


def test_BIRINCI_VE_IKINCI_CUMLE_VAR():
    k = lineage.kolon_kokeni(_SEMA, {
        "cube": "bakim", "measures": ["toplam_durus"],
        "filters": [{"dimension": "bolum", "value": "boya"}]})
    c = lineage.cumleler(k)
    assert any("ariza_kayitlari.toplam_durus" in x for x in c), c
    assert any("`bolum` = `boya` filtresiyle daraltıldı" in x for x in c), c


def test_UCUNCU_CUMLE_BILINCLE_YOK():
    """⚠ *"Bir üst-akış tablo N gün önce değişti"* **FAZ 1.7**'de gelir: tazelik verisi
    bugün `/ask`'e **hiç ulaşmıyor** (`grep -rl freshness backend/app/` → 0). Uydurma bir
    gün sayısı yazmak, `pvm:`/`target:` eşleştirmesinde **reddedilen** şeyin aynısı
    olurdu: **güvenle yanlış** bir sayı, ve kimse onu sorgulamaz."""
    kaynak = (KOK / "app" / "lineage.py").read_text(encoding="utf-8")
    assert "gün önce değişti" not in kaynak.split('"""')[2] if kaynak.count('"""') > 2 \
        else True
    assert "FAZ 1.7" in kaynak, "üçüncü cümlenin SAHİBİ yazılı değil — eksiklik sanılır"


def test_MASKELI_KOLON_CUMLEDE_BELIRTILIYOR():
    sema = {"cubes": [{"name": "c", "base_object": "t",
                       "measures": [{"name": "iban", "expression": "iban"}]}]}
    c = lineage.cumleler(lineage.kolon_kokeni(sema, {"cube": "c", "measures": ["iban"]}))
    assert any("maskeli" in x.lower() for x in c), c


# ── 5 · KURAL B + K2 (frontend tüketicisi) ──────────────────────────────────

def test_BAYRAK_KAPALIYKEN_MAKBUZ_BIREBIR():
    """`lineage=off` → `_provenance` bloğu bugünküyle **birebir**. Yapısal ölçüm:
    çağrı bayrak kapısının **içinde** mi?"""
    import ast

    kaynak = (KOK / "app" / "answer.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_provenance")
    kosullu = [n for n in ast.walk(fn) if isinstance(n, ast.If)]
    assert any("lineage" in ast.dump(n.test) for n in kosullu), \
        "kolon kökeni bayrak kapısı OLMADAN yazılıyor — KURAL B kırık"


def test_FRONTEND_KOKEN_CUMLELERINI_TUKETIYOR():
    """🔴 **K2:** yeni bir makbuz alanı **frontend tüketicisi olmadan** eklenemez."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    panel = (FE / "components" / "ContractDetailPanel.tsx").read_text(encoding="utf-8")
    assert "koken_cumleleri" in panel, "köken cümleleri hiçbir yerde GÖSTERİLMİYOR"
    assert "bu sayı nereden geldi" in panel


def test_FRONTEND_SABLONU_KOPYALAMIYOR():
    """🔴 Şablonlar **backend'de**. Frontend'de ikinci bir şablon kümesi, *"aynı kuralın
    iki sahibi"* olurdu ve ikisi ayrışıp kullanıcıya **aynı kanıtı farklı cümlelerle**
    gösterirdi."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    panel = (FE / "components" / "ContractDetailPanel.tsx").read_text(encoding="utf-8")
    for sablon in ("'dan geldi", "filtresiyle daraltıldı"):
        assert sablon not in panel, (
            f"şablon cümle frontend'e KOPYALANMIŞ ({sablon!r}) — iki sahip")


def test_TEKNIK_GRAF_GOSTERILMIYOR():
    """**KD-13:** bir köken **grafiği** geliştirici artefaktıdır; kullanıcının sorusu
    *"bu sayı nereden geldi"*dir ve cevabı **bir cümledir**. Grafiği basmak,
    `ReportCard`'ın `D3`'te düzeltilen *"geliştirici katmanı son kullanıcıda"* kusurunu
    tekrarlardı."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    panel = (FE / "components" / "ContractDetailPanel.tsx").read_text(encoding="utf-8")
    assert "kolon_kokeni" not in panel, (
        "ham köken YAPISI (graf) frontend'e basılıyor — KD-13 ihlali; kullanıcıya "
        "CÜMLE gösterilir, veri yapısı değil")
