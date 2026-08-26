"""FAZ 2.1 — **YOKLUK SORGUSU "SİHİRİ"** (Tur 2 Senaryo 6, KÖK NEDEN C).

## Kök neden (canlı ölçüldü, `s57`, 2026-08-26)

*"bu ay hiç sipariş vermeyen müşteriler kim"* — `cube_query` sözleşmesinin
(`dimensions`/`measures`/`filters`/`order`) hiç temsil edemediği bir SQL örüntüsü
(NOT EXISTS/anti-join). Garson bu deseni tanımıyor: canlı curl `niyet:
bilinmeyen=hic,vermeyen,kim` gösterdi — "hiç"/"vermeyen" sessizce düşüyor, sistem
YANLIŞ bir cube'a (`cari`) ya da yanlış bir fiile (`KIYASLA`) kayıyor, **hiçbir
beyan yok**. Aynı canlı turda `plan_taslagi.adimlar[0].cube_query` şunu gösterdi:

    {"cube": "siparis", "measures": ["siparis_adedi"],
     "dimensions": ["musteri_kod"], "period_expr": "bu ay"}

Yani garson doğru cube/ölçü/kırılımı ZATEN buluyor — yalnız yanlış FİİLE düşüyor.
Bu ölçüm, roadmap'in "alternatif için FAZ 1'in guarded-LLM basamağı gerekir"
varsayımını (FAZ 2.2'dekiyle AYNI sınıf bir düzeltme) LLM'SİZ, deterministik bir
chip'e çevirdi: `uyum.yokluk_chip()` yalnız `ic.measures[0]`/`dimensions[0]`'ı
okuyup sırayı ASC'ye çeviren bir DOĞAL-DİL yeniden-soru kurar; hiçbir sayı üretmez.

## Üç ayrı kayıp noktası, tek üretici (`uyum.yokluk_ihlali`)

Tek bir `Ihlal` inşası üç FARKLI dala bağlanır (`KAT-1` — ikinci bir üretici YOK):
1. **Tek-adımlı yol** (`uyum.beyan_ekle` → `ask.py:3208`) — `denetle()`'e otomatik
   bağlı, ek kod GEREKMEDİ.
2. **Agentic plan — ÖNİZLEME** (`plan_tuketici.cevap()`'in `§66` erken dönüşü,
   `_ihlaller` hiç kurulmadan döner) — bu TAM OLARAK canlı testin düştüğü dal;
   ayrı bir çağrı eklendi (`_uyum.yokluk_ihlali` doğrudan).
3. **Agentic plan — KOŞULMUŞ** (`_ihlaller` listesi, `denetle()`'den otomatik).

Chip taşınması da AYNI körlüğü tekrarlıyordu: `uyum.chipler()` zaten vardı ama
`plan_tuketici.cevap()` onu hiç toplamıyordu (FAZ 2.2'nin `eksik_niyet_detay`
bulgusunun `suggestions` alanındaki İKİZİ) — `"suggestions"` anahtarı iki dönüş
sözlüğüne de eklendi, `ask.py`'nin `AskResponse(...)` inşası bunu `Suggestion`'a
çeviriyor.
"""

from __future__ import annotations

import ast
import pathlib

from app.uyum import Ihlal, denetle, yokluk_chip, yokluk_ihlali, yokluk_istendi

_KOK = pathlib.Path(__file__).resolve().parents[1]

# --- 1 · TEMEL DESEN — "hiç" + olumsuz-ortaç eki BİRLİKTE gerekir ------------------

_YOKLUK_ORNEKLERI = [
    "bu ay hic siparis vermeyen musteriler kim",
    "hicbir siparis vermeyen musteriler kim",
    "hic odeme yapmayan tedarikciler",
    "hic sikayet acmayan musteriler",
    "hic bakim gormeyen makineler hangileri",
]

_YOKLUK_DEGIL_ORNEKLERI = [
    "bu ay en cok siparis veren musteriler kim",       # üstünlük, yokluk değil
    "hic bu kadar cok satis gormedik",                  # "hic" var, ortaç YOK
    "gecen ay siparis vermeyen ama bu ay veren musteriler",  # ortaç var, "hic" YOK
    "bu yil toplam ciro ne kadar",
    "makine bazinda oee",
]


def test_YOKLUK_ISTENDI_DESEN_YAKALAR():
    for q in _YOKLUK_ORNEKLERI:
        assert yokluk_istendi(q), f"🔴 «{q}» yokluk deseni sayılmalıydı"


def test_YOKLUK_ISTENDI_YANLIS_POZITIF_UretMEZ():
    for q in _YOKLUK_DEGIL_ORNEKLERI:
        assert not yokluk_istendi(q), f"🔴 «{q}» yanlışlıkla yokluk sayıldı"


# --- 2 · `yokluk_ihlali` — KOŞULSUZ (cq'ye bakmadan tetiklenir) --------------------

def test_YOKLUK_IHLALI_CQ_BOSKEN_DE_ATESLENIR():
    """Yanlış cube'a düşmüş (`cari`) ya da hiç cq üretilmemiş olsa BİLE beyan
    edilmeli — mimari sınır `cq`'nun içeriğinden bağımsızdır."""
    ih = yokluk_ihlali("bu ay hic siparis vermeyen musteriler kim", {}, None)
    assert isinstance(ih, Ihlal)
    assert ih.isaret == "yokluk"
    assert ih.etiket == "yokluk sorgusu"
    assert ih.chip is None  # `ic` boş → chip kurulamaz, ama beyan YİNE de var


def test_YOKLUK_IHLALI_YOKLUK_DEGILSE_HIC_URETMEZ():
    assert yokluk_ihlali("bu yil en cok ciro yapan musteri kim", {}, None) is None


# --- 3 · `yokluk_chip` — LLM'siz, AYNI ölçü/kırılımdan ASC alternatif --------------

def test_YOKLUK_CHIP_DOGRU_OLCU_KIRILIMLA_KURULUR():
    cq = {"cube": "siparis", "measures": ["siparis_adedi"],
          "dimensions": ["musteri_kod"], "period_expr": "bu ay"}
    cube_meta = {"measure_synonyms_display": {"siparis_adedi": "sipariş adedi"},
                 "dimension_labels": {"musteri_kod": "müşteri"}}
    chip = yokluk_chip(cq, cube_meta)
    assert chip is not None
    assert chip["kind"] == "yokluk"
    assert "sipariş adedi" in chip["query"]
    assert "müşteri" in chip["query"]
    assert "en az" in chip["query"]


def test_YOKLUK_CHIP_DISPLAY_YOKSA_HAM_ADA_DUSER():
    chip = yokluk_chip({"measures": ["siparis_adedi"], "dimensions": ["musteri_kod"]}, None)
    assert chip is not None
    assert "siparis_adedi" in chip["query"] or "siparis adedi" in chip["query"]


def test_YOKLUK_CHIP_OLCU_YA_DA_KIRILIM_YOKSA_NONE():
    assert yokluk_chip({"measures": [], "dimensions": ["musteri_kod"]}, None) is None
    assert yokluk_chip({"measures": ["siparis_adedi"], "dimensions": []}, None) is None
    assert yokluk_chip(None, None) is None
    assert yokluk_chip("not-a-dict", None) is None


# --- 4 · `denetle()` içinden uçtan uca — tek-adımlı yolun otomatik bağlandığı yer --

def test_DENETLE_YOKLUK_ISARETINI_URETIR():
    cq = {"cube_query": {"cube": "siparis", "measures": ["siparis_adedi"],
                          "dimensions": ["musteri_kod"]}}
    ihlaller = denetle("bu ay hic siparis vermeyen musteriler kim", cq,
                        {"measure_synonyms_display": {"siparis_adedi": "sipariş adedi"},
                         "dimension_labels": {"musteri_kod": "müşteri"}})
    yokluklar = [i for i in ihlaller if i.isaret == "yokluk"]
    assert len(yokluklar) == 1, "🔴 tam bir kez üretilmeli (cq içeriğinden bağımsız)"
    assert yokluklar[0].chip is not None


def test_DENETLE_YOKLUK_DEGILSE_ISARET_URETMEZ():
    cq = {"cube_query": {"cube": "siparis", "measures": ["siparis_adedi"],
                          "dimensions": ["musteri_kod"]}}
    ihlaller = denetle("bu ay en cok siparis veren musteri kim", cq, None)
    assert not any(i.isaret == "yokluk" for i in ihlaller)


# --- 5 · KAYNAK-KİLİTLİ testler — agentic plan yolunun İKİ dönüşü de bağlı mı ------
# (Live Playwright/curl reproduction FAZ 2.2'de aynı garson-gecikmesi riskiyle
# güvenilmez çıkmıştı — o oturumun kararı: kaynak-kilitli test yeterli kanıttır.)

def _plan_tuketici_kaynagi() -> str:
    return (_KOK / "app" / "plan_tuketici.py").read_text(encoding="utf-8")


def test_ONIZLEME_DALI_YOKLUK_IHLALINA_BAGLI():
    """`§66` erken dönüşü (`source: "onizleme"`) `uyum.yokluk_ihlali`'yi ÇAĞIRIYOR mu —
    kaynak okunarak kilitlenir (canlı repro FAZ 2.2'de güvenilmez çıktığı için)."""
    kaynak = _plan_tuketici_kaynagi()
    onizleme_blok = kaynak.split('"source": "onizleme"')[1][:2500]
    assert "_uyum.yokluk_ihlali" in kaynak.split('"source": "onizleme"')[0][-3000:] + onizleme_blok, (
        "🔴 önizleme dalı yokluk denetimini çağırmıyor")
    assert '"eksik_niyet"' in onizleme_blok
    assert '"suggestions"' in onizleme_blok


def test_KOSULMUS_DAL_SUGGESTIONS_TASIR():
    """Agentic planın KOŞULMUŞ dönüşü (`"source": "cube+llm"`) `chipler()`'i
    `suggestions` anahtarına bağlıyor mu — FAZ 2.2'nin `eksik_niyet_detay`
    testiyle AYNI desen (`test_ASKRESPONSE_INSASI_EKSIK_NIYETI_TASIR`)."""
    kaynak = _plan_tuketici_kaynagi()
    assert '"suggestions": _uyum.chipler(_ihlaller)' in kaynak


def test_ASKPY_SUGGESTIONS_PC_DEN_CEKER():
    """`ask.py`'nin agentic-plan `AskResponse(...)` inşası `_pc["suggestions"]`'ı
    gerçekten `Suggestion`'a çeviriyor mu — FAZ 2.2'nin ders aldığı ikinci-yol
    körlüğünün (chip versiyonu) bir daha sessizce geri gelmemesi için."""
    kaynak = (_KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    bolum = kaynak.split('if _pc is not None:')[1][:1200]
    assert "_pc.get(\"suggestions\")" in bolum or '_pc["suggestions"]' in bolum
    assert "Suggestion(**s)" in bolum


# --- 6 · AST TAM-TARAMA — `Ihlal(isaret="yokluk"...)` yalnız TEK yerde kuruluyor --

def test_YOKLUK_IHLALI_TEK_URETICI():
    """`Ihlal(isaret="yokluk"` yalnız `uyum.yokluk_ihlali` İÇİNDE kurulmalı — ikinci
    bir üretici `KAT-1`'i ihlal eder (bu turun kendi dersinin AST-doğrulanmış hâli,
    `test_HER_IHLAL_INSASI_ETIKET_TASIR` ile aynı teknik)."""
    kaynak = (_KOK / "app" / "uyum.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    uretici_fonksiyonlar = []
    for node in ast.walk(agac):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Ihlal":
            for kw in node.keywords:
                if kw.arg == "isaret" and isinstance(kw.value, ast.Constant) and kw.value.value == "yokluk":
                    parents = [n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)
                               and node in ast.walk(n)]
                    uretici_fonksiyonlar.extend(p.name for p in parents
                                                if p.name not in {"denetle"})
    assert uretici_fonksiyonlar == ["yokluk_ihlali"] or set(uretici_fonksiyonlar) == {"yokluk_ihlali"}
