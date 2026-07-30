#!/usr/bin/env python3
"""
Ek Turlar — dima NL Sorgu Korpus Genişletici (Round 2+)

Boşlukları kapatır:
1. atiksan/geri-donusum az temsil edildi → tüm cube'larını genişlet
2. Zorluk 4-5 çok az → yeni şablon varyasyonları
3. Yazım hataları / diyalekt → gerçek kullanıcı yazımı
4. Kullanıcı tipi dengesi → muhasebeci/depo/satin_alma artır
5. Cross-cube multi-turn uzun zincirler
6. Granülarity + dönem kombinasyonları genişlet

Koşum:
    python3 lab/generated/generate_ext.py
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


# ──────────────────────────────────────────────────────────────────────────────
# GENIŞLETME 1: atiksan tam cube kapsamı
# ──────────────────────────────────────────────────────────────────────────────

ATIKSAN_MEASURES = {
    "hurda_alim": ["hurda alımı", "hurda aldık", "gelen hurda", "toplanan hurda", "hurda tutarı"],
    "satis_tutari": ["satış", "ciro", "hasılat", "satış tutarı", "gelir"],
    "alim_tutari": ["alım tutarı", "ne kadar aldık", "alımlarımız", "maliyet"],
    "alim_miktari": ["alınan miktar", "kaç ton topladık", "giriş miktarı"],
    "satis_miktari": ["satılan miktar", "kaç ton sattık", "sevk edilen"],
    "bakiye": ["bakiye", "cari bakiye", "kalan"],
    "toplam_borc": ["borç", "borçlar"],
    "toplam_alacak": ["alacak", "tahsilat"],
}

ATIKSAN_DIMS = ["müşteri", "tedarikçi", "malzeme tipi", "depo", "evrak tipi", "stok"]
ATIKSAN_PERIODS = ["bu yıl", "geçen ay", "bu ay", "son 3 ay", "2024", "2025",
                   "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
                   "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"]

GERI_DONUSUM_JARGON = [
    "ferro hurda", "demir hurda", "bakır hurdası", "alüminyum hurdası",
    "atık kağıt", "plastik hurdası", "akü hurdası", "cam hurda",
    "çelik hurdası", "geri dönüşüm malzemesi", "ikinci el malzeme",
]


def gen_atiksan_extended(seen_norms: set) -> list[dict]:
    records = []
    company, sector, erp = "atiksan", "geri-donusum", "Mikro V16"

    # Tek ölçü sorular
    for m_name, phrasings in ATIKSAN_MEASURES.items():
        for p in phrasings:
            for period in ATIKSAN_PERIODS:
                templates = [
                    f"{period} {p}",
                    f"{p} {period}",
                    f"{period} {p} ne kadar",
                    f"{p} ne kadar {period}",
                    f"{period} toplam {p}",
                ]
                for tmpl in templates:
                    for user in ["patron", "satin_alma", "depo_sorumlusu", "muhasebeci"]:
                        norm = normalize(f"{company}:{user}:{tmpl}")
                        if norm not in seen_norms and len(norm) > 5:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": user, "_diff": 1,
                                "_turns": [tmpl], "_tags": [m_name, "atiksan"],
                            })

    # Kırılım + dönem
    for m_name, phrasings in ATIKSAN_MEASURES.items():
        for p in phrasings[:3]:
            for dim in ATIKSAN_DIMS[:3]:
                for period in ATIKSAN_PERIODS[:6]:
                    templates = [
                        f"{period} {p} {dim} bazında",
                        f"{dim} bazında {period} {p}",
                        f"{p} {dim} kırılımında {period}",
                    ]
                    for tmpl in templates:
                        norm = normalize(f"{company}:kir:{tmpl}")
                        if norm not in seen_norms and len(norm) > 8:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": "veri_analisti", "_diff": 2,
                                "_turns": [tmpl], "_tags": [m_name, dim, "atiksan"],
                            })

    # Geri dönüşüm jargonu
    for jargon in GERI_DONUSUM_JARGON:
        for period in ["bu yıl", "geçen ay", "bu ay"]:
            templates = [
                f"{period} {jargon} alımı ne kadar",
                f"{period} {jargon} satışı",
                f"en çok {jargon} hangi tedarikçiden aldık {period}",
            ]
            for tmpl in templates:
                norm = normalize(f"{company}:jargon:{tmpl}")
                if norm not in seen_norms:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": "satin_alma", "_diff": 2,
                        "_turns": [tmpl], "_tags": ["geri-donusum-jargon", "atiksan"],
                    })

    # Çok-adımlı zincirler
    chains = [
        {
            "turns": [
                "bu yıl hurda alımlarımız ne kadar",
                "malzeme tipine göre kır",
                "en çok aldığımız 3 malzeme",
                "bu 3'ün aylık trendi nasıl",
                "geçen yılla karşılaştır",
            ],
            "user": "satin_alma", "diff": 5,
            "tags": ["atiksan", "multi-turn", "5-turn"],
        },
        {
            "turns": [
                "bu ay satışlarımız",
                "en büyük müşteri kimdi",
                "bu müşteriye ne kadar sattık geçen ay",
                "yıllık toplamda ne kadar",
            ],
            "user": "satis_muduru", "diff": 4,
            "tags": ["atiksan", "multi-turn", "4-turn"],
        },
        {
            "turns": [
                "vadesi geçen alacaklarım",
                "yaş kovalarına göre dağılım",
                "en riskli müşteri kim",
                "bu müşterinin satış geçmişi",
                "ne yapmalıyım",
            ],
            "user": "finans_uzmani", "diff": 5,
            "tags": ["atiksan", "yaslandirma", "multi-turn"],
        },
    ]
    for ch in chains:
        key = normalize(f"{company}:{ch['turns'][0]}:{len(ch['turns'])}")
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": company, "_sector": sector, "_erp": erp,
                "_user": ch["user"], "_diff": ch["diff"],
                "_turns": ch["turns"], "_tags": ch["tags"],
            })

    return records


# ──────────────────────────────────────────────────────────────────────────────
# GENIŞLETME 2: Yazım hataları ve diyalekt varyasyonlar
# ──────────────────────────────────────────────────────────────────────────────

TYPO_VARIANTS = [
    # (doğru, yanlış/alternatif)
    ("satış", "satiss"),
    ("satış", "satış "),
    ("ciro", "çiro"),
    ("alım", "alim"),
    ("bakiye", "bakıye"),
    ("fatura", "fatüra"),
    ("müşteri", "musteri"),
    ("toplam", "topplam"),
    ("karşılaştır", "karsılastır"),
    ("aylık", "aylik"),
    ("haftalık", "haftalik"),
    ("günlük", "gunluk"),
    ("kırılım", "kirilim"),
    ("özetle", "ozetle"),
    ("şube", "sube"),
]

# Türkçe diyalekt / bölge farklılıkları
DIALECT_VARIANTS = [
    ("ne kadar sattık", "ne kadar sattık be"),
    ("satışlar", "satışlarımız"),
    ("ciro", "çiro"),
    ("alım", "alış"),
    ("muhasebe", "muhasib"),
    ("tedarikçi", "satıcı"),
    ("müşteri", "alıcı"),
    ("borç", "veresiye"),
    ("alacak", "senet"),
    ("fatura", "irsaliye"),
    ("stok", "mal varlığı"),
    ("depo", "ambar"),
    ("hurda", "köhne mal"),
    ("fire", "israf"),
    ("verim", "randıman"),
]


def gen_typo_variants(seen_norms: set) -> list[dict]:
    records = []
    companies = [
        ("boyahane", "tekstil-boyahane", "Mikro V16"),
        ("gitas", "tarim-ticareti", "Netsis"),
        ("gulteks", "kumas-ticareti", "Logo Start 3"),
    ]
    periods = ["bu yıl", "geçen ay", "bu ay"]

    for correct, wrong in TYPO_VARIANTS + DIALECT_VARIANTS:
        for period in periods:
            q = f"{period} {wrong}"
            for company, sector, erp in companies:
                norm = normalize(f"{company}:typo:{q}")
                if norm not in seen_norms and len(norm) > 5:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": "saha_personeli", "_diff": 1,
                        "_turns": [q], "_tags": ["typo", "dialect"],
                    })

        # Cümle içinde yazım hatası
        q2 = f"en yüksek {wrong} yapan 5 müşteri bu yıl"
        for company, sector, erp in companies:
            norm = normalize(f"{company}:typo2:{q2}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "saha_personeli", "_diff": 2,
                    "_turns": [q2], "_tags": ["typo", "top-n"],
                })

    return records


# ──────────────────────────────────────────────────────────────────────────────
# GENIŞLETME 3: Kullanıcı tipi denge düzeltmesi
# ──────────────────────────────────────────────────────────────────────────────

MUHASEBECI_QUESTIONS = [
    "hesap ekstresi ver",
    "borç alacak dengesi nedir",
    "aylık cari hesap özeti",
    "hangi cari hesap en fazla işlem gördü",
    "vadesi bu ay dolan borçlar",
    "fatura mutabakatı nasıl",
    "kdv beyannamesine göre satışlar",
    "bilanço için alacak toplamı",
    "muhasebe kayıtları bu ay",
    "dönem sonu bakiyeler",
    "ödeme planı",
    "işlenmemiş faturalar var mı",
    "eksik ödeme var mı",
    "tahakkuk kaydı gerekli mi",
    "vergi matrahı ne kadar",
    "stopaj tutarları",
    "çek/senet vadeleri bu ay",
    "nakit akış tablosu",
    "geçen ay kapanış bakiyesi",
    "bu ay açılış bakiyesi",
]

DEPO_SORUMLUSU_QUESTIONS = [
    "bu gün depodan ne çıktı",
    "depo stok durumu",
    "hangi malzeme azaldı",
    "kritik stok seviyesi altında neler var",
    "bugün giren malzemeler",
    "haftalık depo özeti",
    "fire miktarı bu ay",
    "iade edilen mallar",
    "en çok kullanılan 10 stok",
    "stok sayım farklılıkları",
    "hangi depodan ne gitti",
    "depo doluluk oranı",
    "son hareket tarihi ne olan mallar",
    "hareketsiz stoklar",
    "geçen hafta giriş çıkış",
]

SATIN_ALMA_QUESTIONS = [
    "bu ay alım planımız",
    "tedarikçi değerlendirmesi",
    "en fazla alım yaptığımız 5 tedarikçi",
    "alım bütçesi gerçekleşme oranı",
    "fiyat artışı olan malzemeler",
    "alternatif tedarikçi var mı",
    "sipariş durumu",
    "bekleyen siparişler",
    "teslim süresi en uzun tedarikçi",
    "geçen aya göre alım maliyeti farkı",
    "en ucuz fiyata kim satıyor",
    "alım faturası onay bekleyenler",
    "iade edilen siparişler",
    "tedarikçi borcumuz ne kadar",
    "ödeme vadesi yaklaşan faturalar",
]


def gen_underrepresented_users(seen_norms: set) -> list[dict]:
    records = []
    companies_all = [
        ("boyahane", "tekstil-boyahane", "Mikro V16"),
        ("atiksan", "geri-donusum", "Mikro V16"),
        ("gulteks", "kumas-ticareti", "Logo Start 3"),
        ("gitas", "tarim-ticareti", "Netsis"),
    ]

    user_questions = {
        "muhasebeci": MUHASEBECI_QUESTIONS,
        "depo_sorumlusu": DEPO_SORUMLUSU_QUESTIONS,
        "satin_alma": SATIN_ALMA_QUESTIONS,
    }

    for user_type, questions in user_questions.items():
        for q in questions:
            for company, sector, erp in companies_all:
                norm = normalize(f"{company}:{user_type}:{q}")
                if norm not in seen_norms:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": user_type, "_diff": 2,
                        "_turns": [q], "_tags": [user_type, "user-balance"],
                    })

    # Multi-turn chains for underrepresented users
    muhasebe_chains = [
        ["bu ay alacaklarımız ne kadar", "vadesi geçenleri göster", "30 gün üstü ayrı listele",
         "bu müşterilere hatırlatma gönder", "toplam risk ne"],
        ["bu ay borçlarımız", "vadeye göre sırala", "bu hafta ödenecekler",
         "ödeme emri oluştur", "özet tablo"],
        ["aylık gelir gider özeti", "geçen aya göre kıyasla", "fark neden büyük",
         "detay ver", "raporu kaydet"],
    ]

    depo_chains = [
        ["bugün çıkış hareketleri", "hangi malzeme en çok çıktı", "stok kaldı mı",
         "minimum stok uyarısı var mı"],
        ["geçen hafta giriş miktarları", "bu hafta ile kıyasla", "trend nereye gidiyor"],
    ]

    satin_alma_chains = [
        ["bu ay alım bütçesi ne kadar", "ne kadarı harcandı", "kalan bütçe yeter mi",
         "en kritik alımlar neler", "öncelik sırası"],
        ["bekleyen sipariş var mı", "teslim tarihi geçen var mı", "tedarikçiye not gönder"],
    ]

    for chain_list, user_type in [
        (muhasebe_chains, "muhasebeci"),
        (depo_chains, "depo_sorumlusu"),
        (satin_alma_chains, "satin_alma"),
    ]:
        for chain in chain_list:
            for company, sector, erp in companies_all:
                key = normalize(f"{company}:{user_type}:{chain[0]}:{len(chain)}")
                if key not in seen_norms:
                    seen_norms.add(key)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": user_type, "_diff": 4,
                        "_turns": chain,
                        "_tags": [user_type, f"{len(chain)}-turn", "multi-turn"],
                    })

    return records


# ──────────────────────────────────────────────────────────────────────────────
# GENIŞLETME 4: Zorluk 4-5 yoğunlaştırma
# ──────────────────────────────────────────────────────────────────────────────

DIFF4_TEMPLATES = [
    # Oran soruları
    "{m1} / {m2} oranı {period}",
    "{period} her birim {m2} başına {m1}",
    "{period} {m1} ve {m2} birlikte",
    "{m1} artarken {m2} neden azalıyor {period}",
    "{period} {m1} {m2} ile korelasyonu",
    # YoY/MoM karmaşık
    "{m1} {period_cur} vs {period_prev} yüzde değişim",
    "{period_cur} {m1} büyüme hızı aylık kırılımda",
    "aylık {m1} büyüme trendi son 12 ay",
    # Çok boyut
    "{period} {m1} hem {dim1} hem {dim2} bazında",
    "{dim1} ve {dim2} kesişiminde {m1} {period}",
]

DIFF5_ADVANCED_CHAINS = [
    # Karmaşık diagnostic zincirler
    {
        "company": "boyahane", "sector": "tekstil-boyahane", "erp": "Mikro V16",
        "user": "patron", "diff": 5,
        "tags": ["diagnostic", "multi-cube", "15-turn"],
        "turns": [
            "bu yılki toplam ciromuz ve geçen yıla göre büyüme oranımız",
            "hangi müşteri segmentinde büyüme düştü",
            "bu segmentte aylık kırılım",
            "fire oranımız bu segmentle ilişkili mi",
            "fire en yüksek hangi makine",
            "bu makinenin OEE geçmişi son 6 ay",
            "kullanılabilirlik mi yoksa performans mı düşük",
            "vardiya bazında OEE kıyasla",
            "en iyi vardiyanın uygulaması ne",
            "su ve enerji tüketimi bu makinede",
            "yatırım geri dönüşü hesapla: yeni makine vs bakım",
            "geçen yılın aynı döneminde durum nasıldı",
            "karar önerisi nedir",
            "raporu CEO için özetle",
            "sunum hazırla",
        ],
    },
    {
        "company": "gitas", "sector": "tarim-ticareti", "erp": "Netsis",
        "user": "finans_uzmani", "diff": 5,
        "tags": ["cash-flow", "multi-cube", "12-turn"],
        "turns": [
            "bu ayki nakit girişim ne kadar",
            "alacak tahsilat ne kadar bu ay geldi",
            "tahsilat oranım ne",
            "vadesi geçen alacaklar hangi kovada",
            "90 gün+ gecikmiş müşteriler",
            "bu müşterilerin satış geçmişi",
            "kredi riski var mı",
            "şube bazında nakit dağılımı",
            "en sorunlu şube hangisi",
            "geçen 3 aydaki trend",
            "aksiyon planı öner",
            "bir sonraki ay tahmini nakit akışı",
        ],
    },
    {
        "company": "gulteks", "sector": "kumas-ticareti", "erp": "Logo Start 3",
        "user": "veri_analisti", "diff": 5,
        "tags": ["trend", "multi-cube", "10-turn"],
        "turns": [
            "son 2 yılda satış trendimiz",
            "kumaş cinsine göre büyüme oranları",
            "en hızlı büyüyen kumaş tipi",
            "bu kumaşın müşteri dağılımı",
            "brüt vs net satış farkı bu kumaşta",
            "alım maliyeti nasıl seyretmiş",
            "kar marjı tarihi trend",
            "aylık mevsimsel etki var mı",
            "gelecek çeyrek tahmini",
            "bu tahmine göre alım planı",
        ],
    },
    {
        "company": "atiksan", "sector": "geri-donusum", "erp": "Mikro V16",
        "user": "uretim_muduru", "diff": 5,
        "tags": ["operations", "8-turn"],
        "turns": [
            "bu ay kaç ton hurda aldık",
            "hangi malzeme en fazla",
            "alım fiyatları nasıl değişti aylık",
            "fiyat en az artan malzeme hangisi",
            "satış tarafında marj nasıl",
            "alım-satış farkı karlılığımız",
            "önümüzdeki ay ne almalıyız",
            "stok optimizasyon önerisi",
        ],
    },
]

MEASURES_FOR_DIFF4 = [
    ("satış", "alım"),
    ("ciro", "bakiye"),
    ("fire oranı", "verim"),
    ("satış miktarı", "alım miktarı"),
    ("borç", "alacak"),
    ("toplam fire", "toplam üretim"),
    ("su tüketimi", "enerji tüketimi"),
    ("vadesi geçen", "bakiye"),
]

PERIODS_PAIRS = [
    ("bu yıl", "geçen yıl"),
    ("bu ay", "geçen ay"),
    ("bu çeyrek", "geçen çeyrek"),
    ("2025", "2024"),
    ("ocak-mart", "nisan-haziran"),
]

DIMS_PAIRS = [
    ("müşteri", "şube"),
    ("ürün", "müşteri"),
    ("makine", "vardiya"),
    ("kumaş", "müşteri"),
    ("depo", "malzeme"),
]


def gen_difficulty_4_extended(seen_norms: set) -> list[dict]:
    records = []
    companies = [
        ("boyahane", "tekstil-boyahane", "Mikro V16"),
        ("atiksan", "geri-donusum", "Mikro V16"),
        ("gulteks", "kumas-ticareti", "Logo Start 3"),
        ("gitas", "tarim-ticareti", "Netsis"),
    ]
    periods_simple = ["bu yıl", "geçen ay", "son 3 ay", "yıllık"]

    for company, sector, erp in companies:
        for m1, m2 in MEASURES_FOR_DIFF4:
            for period in periods_simple:
                for tmpl in DIFF4_TEMPLATES[:5]:
                    try:
                        q = tmpl.format(m1=m1, m2=m2, period=period,
                                        period_cur="bu yıl", period_prev="geçen yıl",
                                        dim1="müşteri", dim2="şube")
                        norm = normalize(f"{company}:d4:{q}")
                        if norm not in seen_norms and len(norm) > 8:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": "finans_uzmani", "_diff": 4,
                                "_turns": [q], "_tags": ["multi-measure", "ratio"],
                            })
                    except KeyError:
                        pass

        # YoY cift donem
        for p_cur, p_prev in PERIODS_PAIRS:
            for m1, _ in MEASURES_FOR_DIFF4[:4]:
                templates = [
                    f"{m1} {p_cur} ile {p_prev} kıyasla",
                    f"{p_cur} ve {p_prev} {m1} karşılaştırması",
                    f"{m1} yıllık değişim {p_cur}",
                    f"{p_cur} {m1} büyüme yüzdesi ({p_prev} baz)",
                ]
                for q in templates:
                    norm = normalize(f"{company}:yoy:{q}")
                    if norm not in seen_norms:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 4,
                            "_turns": [q], "_tags": ["yoy", "comparison"],
                        })

        # Çok boyut
        for dim1, dim2 in DIMS_PAIRS:
            for m1, _ in MEASURES_FOR_DIFF4[:3]:
                for period in ["bu yıl", "geçen ay"]:
                    q = f"{period} {m1} {dim1} ve {dim2} bazında birlikte"
                    norm = normalize(f"{company}:multidim:{q}")
                    if norm not in seen_norms:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 4,
                            "_turns": [q], "_tags": ["multi-dim", "4d"],
                        })

    return records


def gen_difficulty_5_advanced(seen_norms: set) -> list[dict]:
    records = []
    for sc in DIFF5_ADVANCED_CHAINS:
        key = normalize(f"{sc['company']}:{sc['turns'][0]}:{len(sc['turns'])}")
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": sc["company"], "_sector": sc["sector"], "_erp": sc["erp"],
                "_user": sc["user"], "_diff": sc["diff"],
                "_turns": sc["turns"], "_tags": sc["tags"],
            })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# GENIŞLETME 5: Daha fazla dönem + granülarity kombinasyonları
# ──────────────────────────────────────────────────────────────────────────────

EXTENDED_PERIODS = [
    # Ay adları
    "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
    "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık",
    # Yıllar
    "2022", "2023", "2024", "2025", "2026",
    # Bileşik
    "ocak-mart", "nisan-haziran", "temmuz-eylül", "ekim-aralık",
    "ilk yarı", "ikinci yarı", "yılın ilk çeyreği", "son çeyrek",
    # Göreceli
    "dün", "bu hafta", "geçen hafta", "son 7 gün", "son 14 gün",
    "son 90 gün", "son 180 gün", "son 365 gün",
    # Özel
    "ramazan ayında", "yılbaşında", "sezon başında", "sezon sonunda",
]

CORE_MEASURES = [
    "satış", "ciro", "alım", "bakiye", "borç", "alacak",
    "fire oranı", "verim", "oee", "su tüketimi", "enerji tüketimi",
    "stok", "fatura sayısı", "hareket sayısı",
]


def gen_period_granularity_sweep(seen_norms: set) -> list[dict]:
    records = []
    companies = [
        ("boyahane", "tekstil-boyahane", "Mikro V16"),
        ("gitas", "tarim-ticareti", "Netsis"),
        ("gulteks", "kumas-ticareti", "Logo Start 3"),
        ("atiksan", "geri-donusum", "Mikro V16"),
    ]
    granularity = ["aylık", "haftalık", "günlük", "çeyreklere göre", "yıllık"]

    for company, sector, erp in companies:
        for m in CORE_MEASURES:
            for period in EXTENDED_PERIODS:
                q = f"{period} {m}"
                norm = normalize(f"{company}:period:{q}")
                if norm not in seen_norms and len(norm) > 5:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": "patron", "_diff": 1,
                        "_turns": [q], "_tags": ["period-sweep", m.replace(" ", "_")],
                    })

            # Dönem + granülarity çakıştırması
            for period in ["bu yıl", "geçen yıl", "son 2 yıl"]:
                for gran in granularity:
                    q = f"{period} {m} {gran}"
                    norm = normalize(f"{company}:gran:{q}")
                    if norm not in seen_norms and len(norm) > 8:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 2,
                            "_turns": [q], "_tags": ["granularity", m.replace(" ", "_")],
                        })

    return records


# ──────────────────────────────────────────────────────────────────────────────
# GENIŞLETME 6: Sektör-spesifik jargon
# ──────────────────────────────────────────────────────────────────────────────

SEKTOR_JARGON = {
    "tekstil-boyahane": {
        "company": "boyahane", "erp": "Mikro V16",
        "terms": [
            "boyama reçetesi", "flote oranı", "renk haslığı", "parti takip",
            "boyama süresi", "kimyasal maliyet/kg", "su m3/ton", "kWh/ton",
            "apre ağırlık", "yıkama kaybı", "kurutma süresi", "sanfor fire",
            "pelerin ağırlığı", "toplam işlenen ton", "iade parti",
        ],
    },
    "kumas-ticareti": {
        "company": "gulteks", "erp": "Logo Start 3",
        "terms": [
            "metre fiyatı", "kg fiyatı", "top", "bale", "rulo",
            "pamuk kumaş", "polyester", "viskon", "keten kumaş",
            "dokuma kumaş", "örme kumaş", "konsinye kumaş",
            "kumaş gramajı", "en (cm)", "eni boy özellikleri",
            "depo nitelik kontrolü", "kumaş hareketi",
        ],
    },
    "tarim-ticareti": {
        "company": "gitas", "erp": "Netsis",
        "terms": [
            "gübre", "tohum", "tarım ilacı", "zirai ilaç",
            "hasat dönemi", "sezon satışı", "kooperatif",
            "çiftçi cari", "tarla fiyatı", "mazot alımı",
            "tarım ekipmanı", "sulama malzemesi",
        ],
    },
    "geri-donusum": {
        "company": "atiksan", "erp": "Mikro V16",
        "terms": [
            "hurda alım fiyatı", "fire oranı hurda", "ton başına değer",
            "akü geri dönüşüm", "elektronik hurda", "metal cins",
            "ergitme kapasitesi", "presleme", "granülleme",
            "çevre izni maliyeti", "nakliye maliyeti hurda",
        ],
    },
}


def gen_sector_jargon(seen_norms: set) -> list[dict]:
    records = []
    for sector, info in SEKTOR_JARGON.items():
        company = info["company"]
        erp = info["erp"]
        for term in info["terms"]:
            for period in ["bu yıl", "geçen ay", "bu ay", ""]:
                prefix = f"{period} " if period else ""
                templates = [
                    f"{prefix}{term} ne kadar",
                    f"{prefix}{term} raporu",
                    f"{prefix}{term} trendi",
                    f"en yüksek {term} nerede",
                ]
                for tmpl in templates:
                    tmpl = tmpl.strip()
                    norm = normalize(f"{company}:sektör:{tmpl}")
                    if norm not in seen_norms and len(norm) > 5:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "uretim_muduru", "_diff": 2,
                            "_turns": [tmpl], "_tags": [sector, "sektor-jargon"],
                        })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# ANA FONKSİYON
# ──────────────────────────────────────────────────────────────────────────────

def run_extension():
    print(f"[generate_ext.py] Mevcut queries.jsonl yükleniyor: {QUERIES_PATH}")
    seen_norms = load_existing(QUERIES_PATH)
    next_id = get_next_id(QUERIES_PATH)
    start_total = next_id - 1
    print(f"  Mevcut: {start_total} sorgu | sonraki ID: {next_id}")

    all_new: list[dict] = []

    print("\n[EXT-1] atiksan genişletme")
    batch = gen_atiksan_extended(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    print("[EXT-2] Yazım hataları + diyalekt")
    batch = gen_typo_variants(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    print("[EXT-3] Kullanıcı tipi denge")
    batch = gen_underrepresented_users(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    print("[EXT-4] Zorluk 4 genişletme")
    batch = gen_difficulty_4_extended(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    print("[EXT-5] Zorluk 5 gelişmiş zincirler")
    batch = gen_difficulty_5_advanced(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    print("[EXT-6] Dönem + granülarity taraması")
    batch = gen_period_granularity_sweep(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    print("[EXT-7] Sektör jargonu")
    batch = gen_sector_jargon(seen_norms)
    print(f"  +{len(batch)}")
    all_new.extend(batch)

    # YAZIM
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

    diff_count: Counter = Counter()
    company_count: Counter = Counter()
    sector_count: Counter = Counter()
    user_count: Counter = Counter()
    tag_count: Counter = Counter()

    # Tüm dosyayı oku (stats için)
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

    print(f"\nTOPLAM ÜRETİLEN: {total_now} (bu ext +{len(all_new)}) | "
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
        f"- Yazım hataları: {tag_count.get('typo', 0)} sorgu",
        f"- Sektör jargonu: {tag_count.get('sektor-jargon', 0)} sorgu",
        f"- Türetilmiş metrikler: {tag_count.get('dso', 0) + tag_count.get('ccc', 0)} sorgu",
        f"",
        f"## Bir Sonraki Koşu",
        f"- Daha fazla zorluk 5 (cross-cube, what-if, forecast)",
        f"- Tam metin arama senaryoları",
        f"- Hata senaryoları (geçersiz filtre, var olmayan cube)",
        f"- İngilizce-Türkçe karma sorular",
        f"- Hedef: 300.000+ tekrarsız sorgu",
        f"",
        f"## Kaynaklar",
        f"- demo/packs/kaynak/*/cubes/*/metadata.yml",
        f"- demo/packs/sektor/boyahane/cubes/*/metadata.yml",
        f"- demo/packs/modul/oee/cubes/oee/metadata.yml",
        f"- lab/nl_corpus.py — REAL_PHRASINGS bankası",
        f"- app/archetypes.py — ölçü arketip sinonimleri",
        f"- Gerçek Türkçe ERP forum soruları (logo destek, mikro kullanıcı grupları)",
    ]

    STATS_PATH.write_text("\n".join(stats_lines), encoding="utf-8")
    print(f"[stats.md] Güncellendi.")


if __name__ == "__main__":
    run_extension()
