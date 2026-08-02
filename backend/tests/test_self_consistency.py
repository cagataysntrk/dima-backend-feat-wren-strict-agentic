"""FAZ D4 — `_select_consistent` BAĞLANDI: yazılmış ama hiç çağrılmayan güven kapısı.

## Ölçülen durum (2 Ağustos 2026)

    $ grep -rn "consistency_k" app/ tests/
    app/config.py:85:    consistency_k: int = 3

**Tek satır. Sıfır tüketici.** `app/config.py` şunu beyan ediyordu:

> *"Self-consistency (ADR-0008 + literatür önerisi #1): LLM cube-seçimi k kez örneklenir,
> kanonik CubeQuery üzerinde oylanır; uyuşmazlık → chip. 1 = kapalı."*

…ve varsayılanı `3` idi. Gerçekte `ask.py` **tek bir** `select_cube` çağrısı yapıyordu:
oylama yok, uyuşma ölçümü yok, uyuşmazlık chip'i yok. `_select_consistent`'in kendisi de
yazılmış ve **üç testi** olmasına rağmen üretimde hiç çağrılmıyordu.

Yani ayar bir **niyet beyanıydı**. Bu depoda tekrar eden en pahalı hata sınıfı budur ve
MIMARI §5'te kayıtlıdır: *yorum doğru olanı söyler, kod onu tanımaz.* Aynı sınıf bu turda
üç kez daha görüldü (`drill.flag_outliers`'ın "yeni istatistik motoru icat edilmez"i,
`interpret`'in yok saydığı `cube_query` otoritesi, `config.py`'nin "üretimde False"u).

## Neden agentic katmanın ön koşulu

Uyuşma oranı yalnız doğruluğu artırmaz — **kalibre bir güven sinyalidir**. Faz F'nin
planlayıcısı *"bu adımda emin miyim, yoksa eskalasyon/soru mu gerekir"* kararını bu tür bir
sinyale bağlar. Sinyal üretilmiyorsa planlayıcı ya hep emin davranır ya hep temkinli.

## Sözleşme

| Durum | Sonuç |
|---|---|
| k örneğin **hepsi** aynı | kazanan + `uyum=1.0` |
| uyum **≥ 2/3** | çoğunluk kazanır (tek aykırı örnek yutulmaz, oylanır) |
| uyum **< 2/3**, uyuşmazlık **tek eksende** | kazanan YOK → netleştirme chip'i (tahmin YOK) |
| uyum < 2/3, uyuşmazlık **çok eksende** | kazanan YOK, eksen YOK → sessiz düşüş (merdiven devam) |

Chip'ler `next_steps` üzerinden taşınır: yeni alan/panel açılmaz (mimari kural H3) ve
tıklama `/cube` ile **LLM'siz** koşar — kullanıcının seçimi ikinci bir LLM turu doğurmaz.
"""

from __future__ import annotations

import json

import pytest

from app.routers.ask import _intent_uyusmazlik_chipi, _select_consistent


class _SahteLLM:
    """`select_cube` çağrıldıkça sıradaki cevabı döndürür (tükenirse sonuncuyu tekrarlar)."""

    def __init__(self, cevaplar):
        self._cevaplar = list(cevaplar)
        self.cagri = 0

    def select_cube(self, _q, _catalog):
        i = min(self.cagri, len(self._cevaplar) - 1)
        self.cagri += 1
        return self._cevaplar[i]


def _cq(cube="parti", measures=("toplam_ciro",), dimensions=()):
    return json.dumps({"cube": cube, "measures": list(measures),
                       "dimensions": list(dimensions), "filters": []}, ensure_ascii=False)


@pytest.fixture
def index(schema):
    from app import cube_router

    return cube_router.build_catalog(schema)[1]


# --- ayarın GERÇEKTEN bağlı olduğu ------------------------------------------------

def test_consistency_k_ayarinin_TUKETICISI_var():
    """ASIL KAPI. `consistency_k` bugüne kadar `config.py`'de TEK BAŞINA duruyordu:
    beyan edilen davranışın kodda karşılığı yoktu."""
    import inspect

    from app.routers import ask as ask_mod

    kaynak = inspect.getsource(ask_mod.ask)
    assert "consistency_k" in kaynak, "ayar hâlâ bağlanmamış (niyet beyanı)"
    assert "_select_consistent" in kaynak, "self-consistency üretim yolunda çağrılmıyor"


def test_varsayilan_k_UCTUR():
    """`config.py` `3` diyor; kod artık onu okuyor. İkisi ayrışırsa test kırılır."""
    from app.config import Settings

    assert Settings().consistency_k == 3


# --- oylama sözleşmesi ------------------------------------------------------------

def test_hepsi_ayni_UYUM_TAM(index):
    llm = _SahteLLM([_cq()] * 3)
    cq, uyum, eksen, _ = _select_consistent(llm, "ciro", "kat", index, 3)
    assert cq and uyum == 1.0 and eksen is None
    assert llm.cagri == 3, "k örnek alınmadı"


def test_cogunluk_KAZANIR_aykiri_yutulmaz(index):
    """2/3 uyum: tek aykırı örnek cevabı bozmamalı — self-consistency'nin asıl kazancı."""
    llm = _SahteLLM([_cq(), _cq(), _cq(measures=["toplam_fire_kg"])])
    cq, uyum, eksen, _ = _select_consistent(llm, "ciro", "kat", index, 3)
    assert cq is not None and uyum == pytest.approx(2 / 3) and eksen is None
    assert cq["measures"] == ["toplam_ciro"]


def test_tek_eksende_UYUSMAZLIK_kazanan_yok(index):
    """Yarı yarıya bölünme → tahmin YOK. Eksen bildirilir ki chip kurulabilsin."""
    llm = _SahteLLM([_cq(), _cq(measures=["toplam_fire_kg"])])
    cq, uyum, eksen, adaylar = _select_consistent(llm, "ciro", "kat", index, 2)
    assert cq is None and eksen == "measures" and len(adaylar) == 2


def test_COK_eksende_uyusmazlik_eksen_bildirmez(index):
    """Cube DE ölçü DE farklıysa tek bir chip sorusu kurulamaz → sessiz düşüş (merdiven
    devam eder). Anlaşılmaz bir chip, chip olmamasından kötüdür."""
    llm = _SahteLLM([_cq(), _cq(cube="oee", measures=["ort_oee"])])
    cq, _uyum, eksen, adaylar = _select_consistent(llm, "x", "kat", index, 2)
    assert cq is None and eksen is None and len(adaylar) == 2


def test_k_1_ESKI_davranis(index):
    """`1 = kapalı` sözleşmesi: tek örnek, oylama yok, ek maliyet yok."""
    llm = _SahteLLM([_cq()])
    cq, uyum, eksen, _ = _select_consistent(llm, "ciro", "kat", index, 1)
    assert cq is not None and uyum == 1.0 and eksen is None and llm.cagri == 1


def test_hepsi_bozuksa_KAZANAN_YOK(index):
    llm = _SahteLLM(["bu json degil"] * 3)
    cq, uyum, eksen, adaylar = _select_consistent(llm, "x", "kat", index, 3)
    assert cq is None and uyum == 0.0 and eksen is None and adaylar == []


# --- netleştirme chip'i -----------------------------------------------------------

def test_uyusmazlik_chipi_NEXT_STEPS_tasir(schema):
    """H3: yeni yetenek yeni alan/panel doğurmaz. `next_steps` zaten tam `cube_query`
    taşıyan ve `/cube` ile LLM'siz koşan tek taşıyıcıdır."""
    a = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": [], "filters": []}
    b = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": [], "filters": []}
    r = _intent_uyusmazlik_chipi("ciro", "measures", [a, b], schema, 0.5, 2)
    assert r.source is None, "belirsizlik bir CEVAP değil"
    assert len(r.next_steps) == 2
    assert [s.cube_query for s in r.next_steps] == [a, b], "chip tam cube_query taşımalı"
    assert all(s.kind == "measure" for s in r.next_steps)
    assert "ölçü" in (r.note or "").lower()
    assert any("self-consistency" in t for t in r.trace), "gerekçe makbuza yazılmadı"


def test_uyusmazlik_chipi_AYNI_etiketi_tekrarlamaz(schema):
    a = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": [], "filters": []}
    r = _intent_uyusmazlik_chipi("x", "measures", [a, dict(a)], schema, 0.5, 2)
    assert len(r.next_steps) == 1


def test_uyusmazlik_chipi_BOYUT_ekseni(schema):
    a = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"], "filters": []}
    b = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": [], "filters": []}
    r = _intent_uyusmazlik_chipi("x", "dimensions", [a, b], schema, 0.5, 2)
    assert all(s.kind == "dimension" for s in r.next_steps)
    etiketler = [s.label for s in r.next_steps]
    assert "kırılımsız (toplam)" in etiketler, (
        "boş kırılım da bir SEÇENEKTİR — etiketsiz bırakılırsa chip anlamsız görünür")
