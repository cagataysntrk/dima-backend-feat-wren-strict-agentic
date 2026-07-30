#!/usr/bin/env python3
"""
Ek Turlar — Round 3 (250k+ hedef)

Eklenecekler:
1. Cross-cube senaryolar (çok cube'dan sorgu)
2. İngilizce-Türkçe karma sorular
3. Hata/sınır senaryoları (geçersiz filtre, bilinmeyen ölçü)
4. 15-20 adım ultra uzun zincirler
5. Negatif/muhalif sorular (neden düştü, sorun ne, risk)
6. Tahmin/projeksiyon soruları (class-b)
7. Benchmark soruları (sektör ortalaması vs biz)
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

QUERIES_PATH = Path(__file__).parent / "queries.jsonl"
STATS_PATH = Path(__file__).parent / "stats.md"


def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[?!.,;:]", "", t)
    return t


def load_existing(path: Path) -> set[str]:
    if not path.exists():
        return set()
    seen = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                for turn in rec.get("turns", []):
                    seen.add(normalize(turn))
            except Exception:
                pass
    return seen


def get_next_id(path: Path) -> int:
    if not path.exists():
        return 1
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count + 1


def make_record(id_, company, sector, erp, user_type, difficulty, turns, tags=None):
    turns = [t.strip() for t in turns if t.strip()]
    return {
        "id": id_,
        "company": company,
        "sector": sector,
        "erp": erp,
        "user_type": user_type,
        "difficulty": difficulty,
        "turns": turns,
        "n_turns": len(turns),
        "char_len": sum(len(t) for t in turns),
        "tags": tags or [],
    }


COMPANIES_ALL = [
    ("boyahane", "tekstil-boyahane", "Mikro V16"),
    ("atiksan", "geri-donusum", "Mikro V16"),
    ("gulteks", "kumas-ticareti", "Logo Start 3"),
    ("gitas", "tarim-ticareti", "Netsis"),
]

# ──────────────────────────────────────────────────────────────────────────────
# 1. Cross-cube senaryolar
# ──────────────────────────────────────────────────────────────────────────────

CROSS_CUBE_QUESTIONS = [
    # satış+cari birleşimi
    ("en yüksek satış yapan müşterinin bakiyesi ne kadar", ["ticaret", "cari", "multi-cube"]),
    ("satış arttı ama alacak da arttı — net durum ne", ["ticaret", "cari", "multi-cube"]),
    ("en büyük 5 müşterim hem satış hem bakiye bazında", ["ticaret", "cari", "multi-cube"]),
    ("müşteri başına satış vs bakiye oranı", ["ticaret", "cari", "multi-cube", "ratio"]),
    # ticaret+mal miktar birleşimi
    ("satış tutarı ve satış miktarı birlikte göster", ["ticaret", "mal", "multi-cube"]),
    ("birim başına ortalama satış fiyatı nedir", ["ticaret", "mal", "multi-cube", "derived"]),
    # oee+parti birleşimi
    ("OEE düştüğünde fire arttı mı", ["oee", "parti", "multi-cube", "correlation"]),
    ("en verimli makinelerin fire oranı", ["oee", "parti", "multi-cube"]),
    ("makine bazında OEE ve kar marjı birlikte", ["oee", "parti", "multi-cube"]),
    # parti+surdurulebilirlik
    ("parti cirosu ile su tüketimi ilişkisi var mı", ["parti", "surdurulebilirlik", "multi-cube"]),
    ("en karlı parti aşamasında enerji ne kadar harcandı", ["parti", "surdurulebilirlik", "multi-cube"]),
    # yaslandirma+ticaret
    ("satış yüksek ama tahsilat kötü olan müşteriler", ["ticaret", "yaslandirma", "multi-cube"]),
    ("90 gün gecikmiş alacakların bu yılki alış geçmişi", ["yaslandirma", "cari", "multi-cube"]),
]

CROSS_CUBE_MULTITURN = [
    {
        "company": "boyahane", "sector": "tekstil-boyahane", "erp": "Mikro V16",
        "user": "patron", "diff": 5,
        "tags": ["parti", "oee", "surdurulebilirlik", "multi-cube", "cross-cube", "10-turn"],
        "turns": [
            "bu yıl toplam ciromuz",
            "en karlı müşterim kim",
            "bu müşteri için fire oranımız nasıl",
            "aynı dönemde OEE ne olmuş",
            "OEE ve fire korelasyonu var mı",
            "su tüketimi bu müşterinin işlerinde nasıl",
            "enerji yoğunluğu hedefimize göre neredeyiz",
            "geçen yıla göre iyileşme var mı",
            "en verimli makine hangisi",
            "bu makineyi daha çok kullansaydık kar ne olurdu",
        ],
    },
    {
        "company": "gitas", "sector": "tarim-ticareti", "erp": "Netsis",
        "user": "finans_uzmani", "diff": 5,
        "tags": ["ticaret", "cari", "yaslandirma", "multi-cube", "cross-cube", "12-turn"],
        "turns": [
            "bu ay satış gelirimiz",
            "en büyük müşteriler bazında",
            "bu müşterilerin cari bakiyesi ne",
            "vadesi geçen alacak var mı",
            "yaş kovalarına dağılım",
            "90 gün üzeri gecikmiş tutarlar",
            "bu müşterilerin geçen yıl ödeme sicili nasıldı",
            "kötü borçlulara bu yıl satış ne kadar",
            "risk skorumuz nedir",
            "tahsilat aksiyon planı öner",
            "şube bazında riskli müşteri dağılımı",
            "CFO için tek sayfa özet",
        ],
    },
    {
        "company": "gulteks", "sector": "kumas-ticareti", "erp": "Logo Start 3",
        "user": "satis_muduru", "diff": 5,
        "tags": ["ticaret", "mal", "cari", "multi-cube", "cross-cube", "8-turn"],
        "turns": [
            "en çok satan kumaş tipim bu yıl",
            "bu kumaşın brüt ve net satış farkı",
            "alım maliyeti nedir bu kumaş için",
            "kar marjı nasıl",
            "satılan miktar ile satış tutarı uyumlu mu",
            "birim fiyat değişimi aylık",
            "en karlı müşterim bu kumaşta",
            "bu müşteriye özel fiyat indirimi yapılmış mı",
        ],
    },
]


def gen_cross_cube(seen_norms: set) -> list[dict]:
    records = []
    for q, tags in CROSS_CUBE_QUESTIONS:
        for company, sector, erp in COMPANIES_ALL:
            norm = normalize(f"{company}:cross:{q}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "veri_analisti", "_diff": 5,
                    "_turns": [q], "_tags": tags,
                })

    for sc in CROSS_CUBE_MULTITURN:
        key = normalize(f"{sc['company']}:cross-mt:{sc['turns'][0]}:{len(sc['turns'])}")
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": sc["company"], "_sector": sc["sector"], "_erp": sc["erp"],
                "_user": sc["user"], "_diff": sc["diff"],
                "_turns": sc["turns"], "_tags": sc["tags"],
            })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 2. İngilizce-Türkçe karma sorular (code-switching)
# ──────────────────────────────────────────────────────────────────────────────

MIXED_LANG_QUESTIONS = [
    # ERP terimleri İngilizce, soru Türkçe
    "bu yıl total sales ne kadar",
    "revenue bu ay ne",
    "gross margin nedir",
    "net profit bu çeyrekte",
    "YTD ciro",
    "MoM büyüme",
    "YoY comparison göster",
    "top 5 customers satışa göre",
    "dashboard açabilir misin",
    "KPI'larım nedir",
    "inventory level ne",
    "outstanding balance göster",
    "overdue receivables ne kadar",
    "cash flow özeti",
    "OEE performance bu ay",
    "downtime analysis",
    "fire rate bu hafta",
    "benchmark comparison yap",
    # Tam İngilizce (sistem bunu anlamalı)
    "what is my sales this month",
    "show me top customers",
    "current inventory status",
    "overdue invoices",
    "machine efficiency last week",
]


def gen_mixed_language(seen_norms: set) -> list[dict]:
    records = []
    for q in MIXED_LANG_QUESTIONS:
        for company, sector, erp in COMPANIES_ALL:
            norm = normalize(f"{company}:mixed:{q}")
            if norm not in seen_norms and len(norm) > 4:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "veri_analisti", "_diff": 2,
                    "_turns": [q], "_tags": ["mixed-lang", "english"],
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 3. Hata / sınır senaryoları
# ──────────────────────────────────────────────────────────────────────────────

ERROR_SCENARIOS = [
    # Var olmayan ölçü
    ("bitcoin fiyatı ne kadar", ["unsupported", "error-scenario"]),
    ("döviz kuru bugün", ["unsupported", "error-scenario"]),
    ("hisse senedi fiyatı", ["unsupported", "error-scenario"]),
    ("enflasyon oranı", ["unsupported", "error-scenario"]),
    # Sistem dışı konu
    ("çalışan maaşları", ["hr-domain", "error-scenario"]),
    ("personel izin durumu", ["hr-domain", "error-scenario"]),
    ("ofis kira maliyeti", ["unsupported", "error-scenario"]),
    # Muğlak / yetersiz bilgi
    ("en iyi", ["ambiguous", "error-scenario"]),
    ("bana rapor ver", ["ambiguous", "error-scenario"]),
    ("analiz yap", ["ambiguous", "error-scenario"]),
    ("ne durumdayız", ["ambiguous", "error-scenario"]),
    # SQL injection girişimi
    ("'; DROP TABLE faturalar; --", ["injection", "security", "error-scenario"]),
    ("1=1 OR satış göster", ["injection", "security", "error-scenario"]),
    # Aşırı uzun sorgu
    ("bu yıl tüm müşterilerin tüm ürünler bazında tüm dönemler için hem satış hem alım hem de bakiye ve fire oranı ve OEE ve su tüketimi ve enerji ve kar marjı ve fatura sayısı ve hareket sayısı ve vadesi geçen alacaklar ve borç toplamı ve alacak toplamı hepsini şube ve depo ve makine ve vardiya ve personel ve haftanın günü bazında birden kır",
     ["too-complex", "error-scenario"]),
    # Çelişkili filtreler
    ("bu yıl ve 2019'da satışlar", ["conflicting-period", "error-scenario"]),
    ("hem satış hem alım hem de bakiye aynı anda göster", ["multi-measure-edge", "error-scenario"]),
]


def gen_error_scenarios(seen_norms: set) -> list[dict]:
    records = []
    companies = [("boyahane", "tekstil-boyahane", "Mikro V16"),
                 ("gitas", "tarim-ticareti", "Netsis")]
    for q, tags in ERROR_SCENARIOS:
        for company, sector, erp in companies:
            norm = normalize(f"{company}:err:{q[:50]}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "saha_personeli", "_diff": 1,
                    "_turns": [q], "_tags": tags,
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 4. Negatif/diagnostic sorular
# ──────────────────────────────────────────────────────────────────────────────

NEGATIVE_DIAGNOSTIC = [
    ("satışlar neden düştü bu ay", ["diagnostic", "negative"]),
    ("fire oranı neden arttı", ["diagnostic", "negative"]),
    ("OEE gerilemiş — sebep ne", ["diagnostic", "negative"]),
    ("tahsilat neden yavaşladı", ["diagnostic", "negative"]),
    ("alım maliyeti neden yükseldi", ["diagnostic", "negative"]),
    ("müşteri kaybı var mı", ["diagnostic", "negative", "churn"]),
    ("hangi üründe zarar ediyoruz", ["diagnostic", "negative", "loss"]),
    ("kötü giden iş kolu hangisi", ["diagnostic", "negative"]),
    ("risk altındaki müşteriler", ["diagnostic", "risk"]),
    ("hangi makine en sorunlu", ["diagnostic", "negative"]),
    ("neden bu ay bütçe tutmadı", ["diagnostic", "negative", "budget"]),
    ("en kötü performanslı şube", ["diagnostic", "negative"]),
    ("kar marjı düşüşünün sebebi", ["diagnostic", "negative"]),
    ("su tüketimi neden arttı boyama aşamasında", ["diagnostic", "negative"]),
    ("verim düşüşü analizi", ["diagnostic", "negative", "oee"]),
    ("hangi müşteriden para toplayamıyoruz", ["diagnostic", "collection", "negative"]),
    ("geç ödeme yapan müşteriler kimler", ["diagnostic", "negative", "overdue"]),
    ("alacak takibinde sorun nerede", ["diagnostic", "negative"]),
    ("stok neden azaldı ani olarak", ["diagnostic", "negative", "inventory"]),
    ("enerji maliyeti neden bu kadar yüksek", ["diagnostic", "negative", "energy"]),
]


def gen_negative_diagnostic(seen_norms: set) -> list[dict]:
    records = []
    for q, tags in NEGATIVE_DIAGNOSTIC:
        for company, sector, erp in COMPANIES_ALL:
            norm = normalize(f"{company}:neg:{q}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "patron", "_diff": 3,
                    "_turns": [q], "_tags": tags,
                })

    # Multi-turn diagnostic zincirler
    diag_chains = [
        {
            "company": "boyahane", "sector": "tekstil-boyahane", "erp": "Mikro V16",
            "user": "patron", "diff": 5, "tags": ["diagnostic", "multi-turn", "7-turn"],
            "turns": [
                "bu ay kar marjı neden düştü",
                "hangi aşamada maliyet arttı",
                "kimyasal maliyet mi arttı yoksa fire mi",
                "fire oranı aylık trend göster",
                "OEE de düştü mü",
                "makine bakımı gecikmiş mi",
                "acil önlem öner",
            ],
        },
        {
            "company": "gitas", "sector": "tarim-ticareti", "erp": "Netsis",
            "user": "finans_uzmani", "diff": 5, "tags": ["diagnostic", "multi-turn", "6-turn"],
            "turns": [
                "tahsilat neden yavaşladı bu ay",
                "hangi müşteri ödeme yapmıyor",
                "bu müşterilerle geçen yılı kıyasla",
                "yaşlandırma kovası analizi",
                "hukuki takibe girecek tutar ne kadar",
                "aksiyon planı öner",
            ],
        },
    ]
    for sc in diag_chains:
        key = normalize(f"{sc['company']}:diag:{sc['turns'][0]}")
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": sc["company"], "_sector": sc["sector"], "_erp": sc["erp"],
                "_user": sc["user"], "_diff": sc["diff"],
                "_turns": sc["turns"], "_tags": sc["tags"],
            })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 5. Tahmin/projeksiyon soruları (class-b)
# ──────────────────────────────────────────────────────────────────────────────

FORECAST_QUESTIONS = [
    ("önümüzdeki ay satış tahmini", ["forecast", "class-b"]),
    ("yıl sonu ciro hedefine ulaşabilir miyiz", ["forecast", "class-b"]),
    ("q4 için alacak tahmini", ["forecast", "class-b"]),
    ("gelecek ay nakit akışı projeksiyon", ["forecast", "class-b"]),
    ("sezon sonu stok tahmini", ["forecast", "class-b"]),
    ("makine kullanım oranı gelecek hafta tahmini", ["forecast", "class-b"]),
    ("yıllık büyüme trendine göre hedef nedir", ["forecast", "class-b", "growth"]),
    ("eğer alım maliyeti %10 artarsa kar marjı ne olur", ["what-if", "class-b"]),
    ("fire oranını %1 düşürsek yıllık tasarruf ne", ["what-if", "class-b"]),
    ("en iyi senaryo / en kötü senaryo ciro", ["scenario", "class-b"]),
    ("satış hedefine ulaşmak için kaç fatura gerekli", ["planning", "class-b"]),
    ("stok yatırımı ne zaman geri döner", ["roi", "class-b"]),
    ("enerji verimliliği yatırımı kaç ayda amorti edilir", ["roi", "class-b"]),
    ("önümüzdeki çeyrekte personel ihtiyacı", ["planning", "class-b", "hr"]),
    ("kapasite planlama: mevcut makine kapasitemiz yeter mi", ["capacity", "class-b"]),
]


def gen_forecast_questions(seen_norms: set) -> list[dict]:
    records = []
    for q, tags in FORECAST_QUESTIONS:
        for company, sector, erp in COMPANIES_ALL:
            norm = normalize(f"{company}:forecast:{q}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "finans_uzmani", "_diff": 5,
                    "_turns": [q], "_tags": tags,
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 6. Benchmark/kıyaslama soruları
# ──────────────────────────────────────────────────────────────────────────────

BENCHMARK_QUESTIONS = [
    ("sektör ortalamasına göre OEE'miz iyi mi", ["benchmark", "class-b"]),
    ("fire oranımız sektörle kıyasla", ["benchmark", "class-b"]),
    ("DSO sektör standardına göre nasıl", ["benchmark", "dso", "class-b"]),
    ("rakiplerimize göre kar marjımız", ["benchmark", "class-b"]),
    ("su yoğunluğumuz ZDHC standardını karşılıyor mu", ["benchmark", "sustainability", "class-b"]),
    ("enerji verimliliğimiz ISO 50001 standardında mı", ["benchmark", "energy", "class-b"]),
    ("tahsilat süremiz piyasa ortalamasının altında mı", ["benchmark", "class-b"]),
    ("büyüme hızımız sektör büyümesiyle uyumlu mu", ["benchmark", "class-b", "growth"]),
]


def gen_benchmark_questions(seen_norms: set) -> list[dict]:
    records = []
    for q, tags in BENCHMARK_QUESTIONS:
        for company, sector, erp in COMPANIES_ALL:
            norm = normalize(f"{company}:bench:{q}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "patron", "_diff": 5,
                    "_turns": [q], "_tags": tags,
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 7. 15-20 adım ultra uzun zincirler
# ──────────────────────────────────────────────────────────────────────────────

ULTRA_LONG_CHAINS = [
    {
        "company": "boyahane", "sector": "tekstil-boyahane", "erp": "Mikro V16",
        "user": "veri_analisti", "diff": 5,
        "tags": ["ultra-long", "20-turn", "multi-cube", "cross-cube"],
        "turns": [
            "bu yıl toplam satışlarımız ne kadar",
            "geçen yıla göre büyüme oranı",
            "aylık satış trendi göster",
            "en çok büyüme hangi çeyrekte oldu",
            "bu çeyrekte müşteri bazında kırılım",
            "en büyük 5 müşteri sıralı listesi",
            "bu 5 müşterinin bakiye durumu",
            "vadesi geçen alacak var mı",
            "yaş kovası analizi bu müşteriler için",
            "30+ gün gecikmiş toplam tutar",
            "şimdi fire oranımıza bakalım bu yıl",
            "hangi aşamada en yüksek fire",
            "yıkama aşamasında fire aylık trend",
            "OEE bu aşamada nasıl",
            "vardiya bazında OEE kıyasla",
            "en iyi vardiya hangisi ve neden",
            "su tüketimi bu çeyrekte geçen yıla göre",
            "enerji yoğunluğu hedefimize göre nerede",
            "genel özetle: riskler ve fırsatlar",
            "yönetim sunumu için öncelikli bulgular",
        ],
    },
    {
        "company": "gitas", "sector": "tarim-ticareti", "erp": "Netsis",
        "user": "patron", "diff": 5,
        "tags": ["ultra-long", "18-turn", "multi-cube"],
        "turns": [
            "bu yılki gelir durumumuz özetle",
            "satış miktarı ve tutarı birlikte",
            "şube bazında satış performansı",
            "en iyi şubem hangisi",
            "bu şubede müşteri kırılımı",
            "en büyük müşterimiz kim bu şubede",
            "bu müşterinin alacak durumu",
            "vadesi geçen var mı",
            "bu yıl kaç fatura kestik",
            "aylık fatura adedi trendi",
            "alım tarafında ne var",
            "tedarikçi bazında alım dağılımı",
            "en fazla alım yaptığımız 3 tedarikçi",
            "bu tedarikçilere borcumuz ne",
            "nakit çıkış takvimi bu ay",
            "nakit giriş tahmini (alacaktan)",
            "net nakit pozisyonumuz",
            "öneriniz nedir finansal sağlık için",
        ],
    },
    {
        "company": "gulteks", "sector": "kumas-ticareti", "erp": "Logo Start 3",
        "user": "satis_muduru", "diff": 5,
        "tags": ["ultra-long", "15-turn"],
        "turns": [
            "bu sezon satışlarım geçen sezona göre",
            "kumaş tipi bazında karşılaştırma",
            "en çok satan 3 kumaş tipi",
            "bu 3'ün aylık satış trendi",
            "brüt vs net satış farkı bu kumaşlarda",
            "alım maliyeti bu kumaşlar için",
            "kar marjı hesabı yapabilir misin",
            "müşteri bazında satış dağılımı",
            "en karlı müşterim kim",
            "bu müşterinin bakiyesi",
            "fatura sayısı aylık nasıl seyretti",
            "sipariş başına ortalama tutar",
            "sezon sonunda hedef tutacak mı",
            "hangi kumaşa odaklanmalıyım",
            "aksiyon planı öner",
        ],
    },
    {
        "company": "atiksan", "sector": "geri-donusum", "erp": "Mikro V16",
        "user": "uretim_muduru", "diff": 5,
        "tags": ["ultra-long", "15-turn", "operations"],
        "turns": [
            "bu ay kaç ton hurda topladık",
            "malzeme tipine göre dağılım",
            "en çok toplanan 5 malzeme",
            "bu malzemelerin aylık toplama trendi",
            "fiyat gelişimi aylık bu malzemelerde",
            "en karlı malzeme hangisi",
            "satış tarafında bu malzemelerin durumu",
            "stok miktarı şu an ne kadar",
            "stok değeri ne kadar",
            "en uzun süre stokta bekleyen malzeme",
            "tedarikçi sayımız bu ay",
            "yeni tedarikçi geldi mi",
            "en büyük tedarikçiye borcumuz",
            "bu yılki hedef neydi toplama açısından",
            "hedefe ulaşıyor muyuz",
        ],
    },
]


def gen_ultra_long_chains(seen_norms: set) -> list[dict]:
    records = []
    for sc in ULTRA_LONG_CHAINS:
        key = normalize(f"{sc['company']}:ultra:{sc['turns'][0]}:{len(sc['turns'])}")
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": sc["company"], "_sector": sc["sector"], "_erp": sc["erp"],
                "_user": sc["user"], "_diff": sc["diff"],
                "_turns": sc["turns"], "_tags": sc["tags"],
            })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 8. Granülarity zoom (kova sorgular) — daha detaylı dönem sweepleri
# ──────────────────────────────────────────────────────────────────────────────

GRAN_ZOOM_TEMPLATES = [
    # Haftalık zoom
    "hafta {w} satışlar",
    "haftanın {d}. günü satışları",
    "{d} günü aylık trend",
    # Saat bazlı (henüz desteklenmeyen)
    "saat bazında satış (class-b)",
    # Çeyrek zoom
    "{year} {q}. çeyrek satışları",
    "çeyrekler arası büyüme {year}",
]

WEEKDAYS_TR = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
MEASURES_SIMPLE = ["satış", "ciro", "alım", "fire oranı", "verim", "bakiye", "fatura sayısı"]


def gen_gran_zoom(seen_norms: set) -> list[dict]:
    records = []
    for company, sector, erp in COMPANIES_ALL:
        # Hafta günleri
        for day in WEEKDAYS_TR:
            for m in MEASURES_SIMPLE:
                for period in ["bu yıl", "geçen ay"]:
                    q = f"{period} {day} günleri {m}"
                    norm = normalize(f"{company}:gday:{q}")
                    if norm not in seen_norms:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 3,
                            "_turns": [q], "_tags": ["weekday", "granularity"],
                        })

        # Hafta numaraları
        for w in range(1, 53):
            for m in MEASURES_SIMPLE[:3]:
                q = f"bu yılın {w}. haftası {m}"
                norm = normalize(f"{company}:week{w}:{m}")
                if norm not in seen_norms:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": "veri_analisti", "_diff": 2,
                        "_turns": [q], "_tags": ["week-number", "granularity"],
                    })

        # Çeyrek × yıl
        for year in [2023, 2024, 2025]:
            for q_num in [1, 2, 3, 4]:
                for m in MEASURES_SIMPLE[:4]:
                    q = f"{year} yılı {q_num}. çeyrek {m}"
                    norm = normalize(f"{company}:{year}q{q_num}:{m}")
                    if norm not in seen_norms:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "patron", "_diff": 2,
                            "_turns": [q], "_tags": ["quarter", "year", "granularity"],
                        })

    return records


# ──────────────────────────────────────────────────────────────────────────────
# 9. Bağlamsal refine soruları (önceki cevaba atıf)
# ──────────────────────────────────────────────────────────────────────────────

CONTEXTUAL_REFINE_CHAINS = [
    {
        "company": "boyahane", "sector": "tekstil-boyahane", "erp": "Mikro V16",
        "user": "patron", "diff": 5,
        "tags": ["contextual-refine", "multi-turn", "6-turn"],
        "turns": [
            "bu yıl satışlar",
            "sadece boyama aşamasını göster",
            "müşteri bazında yeniden kır",
            "sadece ilk 3'ü",
            "bunları grafikte göster",
            "geçen yılla karşılaştır",
        ],
    },
    {
        "company": "gitas", "sector": "tarim-ticareti", "erp": "Netsis",
        "user": "satis_muduru", "diff": 5,
        "tags": ["contextual-refine", "multi-turn", "5-turn"],
        "turns": [
            "müşteri bazında satışlar",
            "sadece gübre satışlarını filtrele",
            "aylık kır",
            "en yüksek 5",
            "bu müşterilerin bakiyesi",
        ],
    },
    {
        "company": "gulteks", "sector": "kumas-ticareti", "erp": "Logo Start 3",
        "user": "veri_analisti", "diff": 5,
        "tags": ["contextual-refine", "multi-turn", "7-turn"],
        "turns": [
            "kumaş tipine göre satışlar bu yıl",
            "yalnızca pamuklu kumaşlar",
            "aylık trend",
            "en düşük ay hangisi",
            "o ayın müşteri dağılımı",
            "en büyük müşterinin diğer aylardaki durumu",
            "yıllık toplamda bu müşteri ne kadar aldı",
        ],
    },
    {
        "company": "atiksan", "sector": "geri-donusum", "erp": "Mikro V16",
        "user": "muhasebeci", "diff": 5,
        "tags": ["contextual-refine", "multi-turn", "5-turn"],
        "turns": [
            "tüm cari hesap bakiyeleri",
            "sadece borçlu olanları göster",
            "vadesi geçmişleri filtrele",
            "toplam risk tutarı",
            "şubeye göre dağılım",
        ],
    },
]


def gen_contextual_refine(seen_norms: set) -> list[dict]:
    records = []
    for sc in CONTEXTUAL_REFINE_CHAINS:
        key = normalize(f"{sc['company']}:refine:{sc['turns'][0]}:{len(sc['turns'])}")
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": sc["company"], "_sector": sc["sector"], "_erp": sc["erp"],
                "_user": sc["user"], "_diff": sc["diff"],
                "_turns": sc["turns"], "_tags": sc["tags"],
            })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# ANA FONKSİYON
# ──────────────────────────────────────────────────────────────────────────────

def run_ext2():
    print(f"[generate_ext2.py] Mevcut queries.jsonl yükleniyor: {QUERIES_PATH}")
    seen_norms = load_existing(QUERIES_PATH)
    next_id = get_next_id(QUERIES_PATH)
    start_total = next_id - 1
    print(f"  Mevcut: {start_total} sorgu | sonraki ID: {next_id}")

    all_new: list[dict] = []

    steps = [
        ("EXT2-1: Cross-cube sorular", gen_cross_cube),
        ("EXT2-2: İngilizce-Türkçe karma", gen_mixed_language),
        ("EXT2-3: Hata senaryoları", gen_error_scenarios),
        ("EXT2-4: Negatif/diagnostic", gen_negative_diagnostic),
        ("EXT2-5: Tahmin/projeksiyon (class-b)", gen_forecast_questions),
        ("EXT2-6: Benchmark soruları", gen_benchmark_questions),
        ("EXT2-7: Ultra uzun zincirler (15-20 adım)", gen_ultra_long_chains),
        ("EXT2-8: Granülarity zoom", gen_gran_zoom),
        ("EXT2-9: Bağlamsal refine zincirleri", gen_contextual_refine),
    ]

    for label, fn in steps:
        print(f"[{label}]")
        batch = fn(seen_norms)
        print(f"  +{len(batch)}")
        all_new.extend(batch)

    print(f"\n[YAZIM] {len(all_new)} yeni kayıt ekleniyor...")
    with open(QUERIES_PATH, "a", encoding="utf-8") as f:
        for raw in all_new:
            rec = make_record(
                id_=next_id,
                company=raw["_company"],
                sector=raw["_sector"],
                erp=raw["_erp"],
                user_type=raw["_user"],
                difficulty=raw["_diff"],
                turns=raw["_turns"],
                tags=raw["_tags"],
            )
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            next_id += 1

    total_now = start_total + len(all_new)

    # İstatistik
    diff_count: Counter = Counter()
    company_count: Counter = Counter()
    sector_count: Counter = Counter()
    user_count: Counter = Counter()
    tag_count: Counter = Counter()

    with open(QUERIES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                diff_count[rec["difficulty"]] += 1
                company_count[rec["company"]] += 1
                sector_count[rec["sector"]] += 1
                user_count[rec["user_type"]] += 1
                for t in rec.get("tags", []):
                    tag_count[t] += 1
            except Exception:
                pass

    print(f"\nTOPLAM ÜRETİLEN: {total_now} (bu ext2 +{len(all_new)}) | "
          f"zorluk kırılımı: {dict(sorted(diff_count.items()))}")
    print(f"şirket kırılımı: {dict(company_count.most_common())}")

    stats_lines = [
        f"# Sorgu Korpus İstatistikleri",
        f"",
        f"Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## Toplam",
        f"- **Toplam tekrarsız sorgu**: {total_now}",
        f"- **Son turda eklenen**: +{len(all_new)}",
        f"",
        f"## Zorluk Kırılımı",
    ]
    for d in sorted(diff_count.keys()):
        stats_lines.append(f"- Zorluk {d}: {diff_count[d]}")

    stats_lines += [f"", f"## Şirket Kırılımı"]
    for c, cnt in company_count.most_common():
        stats_lines.append(f"- {c}: {cnt}")

    stats_lines += [f"", f"## Sektör Kırılımı"]
    for s, cnt in sector_count.most_common():
        stats_lines.append(f"- {s}: {cnt}")

    stats_lines += [f"", f"## Kullanıcı Tipi Kırılımı"]
    for u, cnt in user_count.most_common():
        stats_lines.append(f"- {u}: {cnt}")

    stats_lines += [f"", f"## En Sık Etiketler (Top 30)"]
    for t, cnt in tag_count.most_common(30):
        stats_lines.append(f"- {t}: {cnt}")

    stats_lines += [
        f"",
        f"## Boşluk Analizi",
        f"- Jenerik sektörler (class-b): {tag_count.get('class-b', 0)} sorgu",
        f"- Multi-cube: {tag_count.get('multi-cube', 0)} sorgu",
        f"- Cross-cube: {tag_count.get('cross-cube', 0)} sorgu",
        f"- Yazım hataları: {tag_count.get('typo', 0)} sorgu",
        f"- Forecast/what-if: {tag_count.get('forecast', 0) + tag_count.get('what-if', 0)} sorgu",
        f"- Hata senaryoları: {tag_count.get('error-scenario', 0)} sorgu",
        f"- Ultra uzun zincirler: {tag_count.get('ultra-long', 0)} sorgu",
        f"",
        f"## Bir Sonraki Koşu",
        f"- Daha fazla atiksan/geri-donusum kırılımı",
        f"- Türkçe ERP forum sorularından gerçek ifadeler",
        f"- Sesli sorgu simülasyonu (konuşma dili)",
        f"- Hedef: 400.000+ tekrarsız sorgu",
        f"",
        f"## Kaynaklar",
        f"- demo/packs/kaynak/*/cubes/*/metadata.yml",
        f"- demo/packs/sektor/boyahane/cubes/*/metadata.yml",
        f"- demo/packs/modul/oee/cubes/oee/metadata.yml",
        f"- lab/nl_corpus.py — REAL_PHRASINGS bankası",
        f"- app/archetypes.py — ölçü arketip sinonimleri",
    ]

    STATS_PATH.write_text("\n".join(stats_lines), encoding="utf-8")
    print(f"[stats.md] Güncellendi.")
    print(f"[queries.jsonl] Yol: {QUERIES_PATH}")


if __name__ == "__main__":
    run_ext2()
