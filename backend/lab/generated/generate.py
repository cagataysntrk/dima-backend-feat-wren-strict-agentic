#!/usr/bin/env python3
"""
Deterministik Kombinatoryal Sorgu Korpus Üreteci — dima NL→SQL bankatı.

Çalıştır:
    python lab/generated/generate.py [--tur N]

Çıktı:
    lab/generated/queries.jsonl  — APPEND-ONLY, her satır bir JSON
    lab/generated/stats.md       — canlı toplam + eksen kırılımı
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from itertools import product
from collections import defaultdict, Counter

QUERIES_PATH = Path(__file__).parent / "queries.jsonl"
STATS_PATH = Path(__file__).parent / "stats.md"

# ──────────────────────────────────────────────────────────────────────────────
# VERİ TANIMI — Cube uzayı (metadata.yml'den türetildi)
# ──────────────────────────────────────────────────────────────────────────────

CUBE_SPACE = {
    # key = (erp, cube_name)
    ("mikro-v16", "ticaret"): {
        "label": "satış & alım",
        "measures": {
            "satis_tutari": ["satış", "ciro", "gelir", "hasılat", "satış tutarı", "ne sattık", "satışlarımız",
                             "satış gelirimiz", "ne kazandık satıştan", "gelirlerimiz"],
            "satis_miktari": ["satış miktarı", "satılan miktar", "kaç kilo satıldı", "ne kadar sevk ettik",
                              "sevk miktarı", "çıkış miktarı", "satılan mal"],
            "alim_tutari": ["alım tutarı", "ne kadar aldık", "alımlarımız", "satın almalar", "tedariğimiz",
                            "mal alımı", "hammadde alımı", "hurda alımı", "alış tutarı"],
            "alim_miktari": ["alım miktarı", "kaç kilo aldık", "alınan miktar", "topladığımız",
                             "giriş miktarı", "tedarik edilen"],
            "net_miktar": ["net miktar", "stok değişimi", "net stok", "kalan miktar"],
            "islem_sayisi": ["işlem sayısı", "kaç işlem oldu", "işlem adedi", "hareket sayısı"],
        },
        "dimensions": {
            "stok_kodu": ["stok", "ürün", "malzeme", "mal", "stok bazında", "ürün bazında"],
            "cari_kodu": ["cari", "firma", "müşteri", "tedarikçi", "müşteri bazında", "firmaya göre"],
            "evrak_tipi": ["evrak tipi", "evrak tipine göre"],
        },
        "time_dim": "tarih",
        "companies": ["boyahane", "atiksan"],
        "sectors": ["tekstil-boyahane", "geri-donusum"],
        "erp": "Mikro V16",
    },
    ("mikro-v16", "cari"): {
        "label": "cari hesap",
        "measures": {
            "toplam_borc": ["borç", "borç toplamı", "borçlar", "borç tutarı", "cari borç", "ne kadar borcu var"],
            "toplam_alacak": ["alacak", "tahsilatlar", "alacaklarımız", "ne kadar alacağımız var",
                              "alacak toplamı", "tahsil edilen"],
            "bakiye": ["bakiye", "net bakiye", "kalan borç", "hesap bakiyesi", "cari bakiye",
                       "hesap durumu", "kalan"],
            "hareket_sayisi": ["hareket sayısı", "kaç hareket var", "işlem adedi", "kaç işlem oldu"],
        },
        "dimensions": {
            "cari_kodu": ["cari", "firma", "müşteri", "tedarikçi", "müşteri bazında"],
            "evrak_tipi": ["evrak tipi", "evrak tipine göre"],
        },
        "time_dim": "tarih",
        "companies": ["boyahane", "atiksan"],
        "sectors": ["tekstil-boyahane", "geri-donusum"],
        "erp": "Mikro V16",
    },
    ("logo-3", "ticaret"): {
        "label": "satış & alım (fatura)",
        "measures": {
            "satis_tutari": ["satış", "ciro", "gelir", "net satış", "satış tutarı", "fatura tutarı"],
            "brut_satis": ["brüt satış", "brüt ciro", "brüt tutar", "kdvli satış"],
            "alim_tutari": ["alım", "alış", "mal alımı", "alım tutarı"],
            "satis_fatura_sayisi": ["fatura sayısı", "kaç fatura kesildi", "fatura adedi", "kesilen fatura"],
        },
        "dimensions": {
            "cari_ref": ["cari", "müşteri", "tedarikçi", "müşteriye göre"],
            "fatura_no": ["fatura no", "fiş no"],
        },
        "time_dim": "tarih",
        "companies": ["gulteks"],
        "sectors": ["kumas-ticareti"],
        "erp": "Logo Start 3",
    },
    ("logo-3", "cari"): {
        "label": "cari hesap",
        "measures": {
            "toplam_borc": ["borç", "borçlar", "borç toplamı"],
            "toplam_alacak": ["alacak", "tahsilat", "alacak toplamı"],
            "bakiye": ["bakiye", "kalan", "net bakiye", "cari bakiye"],
            "hareket_sayisi": ["hareket sayısı", "kaç hareket", "işlem adedi"],
        },
        "dimensions": {
            "cari_ref": ["cari", "müşteri", "firmaya göre"],
            "islem_turu": ["işlem türü", "evrak türü"],
        },
        "time_dim": "tarih",
        "companies": ["gulteks"],
        "sectors": ["kumas-ticareti"],
        "erp": "Logo Start 3",
    },
    ("logo-3", "mal"): {
        "label": "mal hareketi (miktar)",
        "measures": {
            "satis_miktari": ["satış miktarı", "satılan", "sevk edilen", "çıkış miktarı"],
            "alim_miktari": ["alım miktarı", "alınan", "giriş miktarı"],
            "satis_tutari": ["satış tutarı", "çıkış tutarı"],
            "alim_tutari": ["alım tutarı", "giriş tutarı"],
        },
        "dimensions": {
            "stok_ref": ["stok", "ürün", "kumaş", "malzeme", "kumaş bazında"],
            "cari_ref": ["cari", "müşteri", "müşteriye göre"],
        },
        "time_dim": "tarih",
        "companies": ["gulteks"],
        "sectors": ["kumas-ticareti"],
        "erp": "Logo Start 3",
    },
    ("netsis", "ticaret"): {
        "label": "satış & alım (fatura)",
        "measures": {
            "satis_tutari": ["satış", "ciro", "gelir", "satış tutarı", "hasılat"],
            "alim_tutari": ["alım", "alış", "alım tutarı", "hurda alımı"],
            "satis_kdv": ["kdv", "satış kdv", "kdv tutarı"],
            "satis_fatura_sayisi": ["fatura sayısı", "kaç fatura", "fatura adedi"],
        },
        "dimensions": {
            "cari_adi": ["müşteri", "firma", "cari", "kime", "kimden", "müşteriye göre"],
            "cari_kodu": ["cari kodu", "müşteri kodu"],
            "sube": ["şube", "şubeye göre", "şube bazında"],
            "hafta_gunu": ["haftanın günü", "günlere göre", "hangi gün"],
        },
        "time_dim": "tarih",
        "companies": ["gitas", "atiksan"],
        "sectors": ["tarim-ticareti", "geri-donusum"],
        "erp": "Netsis",
    },
    ("netsis", "cari"): {
        "label": "cari hesap",
        "measures": {
            "toplam_borc": ["borç", "borçlar", "borç toplamı"],
            "toplam_alacak": ["alacak", "tahsilat", "alacak toplamı"],
            "bakiye": ["bakiye", "kalan", "net bakiye"],
            "hareket_sayisi": ["hareket sayısı", "kaç hareket", "işlem adedi"],
        },
        "dimensions": {
            "cari_adi": ["müşteri", "firma", "cari", "müşteriye göre"],
            "sube": ["şube", "şubeye göre"],
            "hareket_turu": ["hareket türü", "işlem türü"],
            "hafta_gunu": ["haftanın günü", "günlere göre"],
        },
        "time_dim": "tarih",
        "companies": ["gitas"],
        "sectors": ["tarim-ticareti"],
        "erp": "Netsis",
    },
    ("netsis", "mal"): {
        "label": "mal hareketi (miktar)",
        "measures": {
            "satis_miktari": ["satış miktarı", "satılan", "sevk edilen", "ne kadar sevk ettik"],
            "alim_miktari": ["alım miktarı", "alınan", "toplanan", "ne kadar topladık"],
            "satis_tutari": ["satış tutarı", "çıkış tutarı"],
            "alim_tutari": ["alım tutarı", "giriş tutarı", "hurda değeri"],
            "net_miktar": ["net miktar", "stok değişimi"],
        },
        "dimensions": {
            "stok_adi": ["stok", "ürün", "malzeme", "ne sattık", "ne aldık", "ürün bazında"],
            "cari_adi": ["müşteri", "tedarikçi", "firma", "kimden", "kime"],
            "depo": ["depo", "depoya göre"],
            "hafta_gunu": ["haftanın günü", "güne göre"],
        },
        "time_dim": "tarih",
        "companies": ["gitas", "atiksan"],
        "sectors": ["tarim-ticareti", "geri-donusum"],
        "erp": "Netsis",
    },
    ("netsis", "yaslandirma"): {
        "label": "cari yaşlandırma",
        "measures": {
            "net_bakiye": ["bakiye", "açık bakiye", "net bakiye", "tutar"],
            "vadesi_gecen": ["vadesi geçen", "gecikmiş", "gecikme", "muaccel", "geciken alacak"],
        },
        "dimensions": {
            "yas_kovasi": ["yaş kovası", "vade aralığı", "gün aralığı", "yaşlandırma kovası"],
            "cari_kodu": ["cari kodu", "hesap kodu"],
            "cari_adi": ["müşteri", "firma", "cari"],
        },
        "time_dim": "tarih",
        "companies": ["gitas", "atiksan"],
        "sectors": ["tarim-ticareti", "geri-donusum"],
        "erp": "Netsis",
    },
    ("boyahane", "parti"): {
        "label": "parti",
        "measures": {
            "fire_orani_yuzde": ["fire oranı", "fire yüzdesi", "ne kadar fire verdik", "fire durumu", "zayiat oranı"],
            "toplam_fire_kg": ["fire", "toplam fire", "fire kg"],
            "toplam_agirlik_kg": ["ağırlık", "kilo", "tonaj", "işlenen miktar", "üretim miktarı"],
            "toplam_ciro": ["ciro", "gelir", "tutar", "satış"],
            "kar": ["kar", "kâr", "kazanç", "net kar", "kârımız"],
            "kar_marji_yuzde": ["kar marjı", "kâr marjı", "kar oranı", "karlılık", "marj", "karlılık oranı"],
            "ort_renk_sapmasi": ["renk sapması", "sapma", "delta", "renk delta"],
            "parti_sayisi": ["parti sayısı", "kaç parti", "adet"],
        },
        "dimensions": {
            "makine": ["makine", "makine bazında", "makinaya göre", "cihaz"],
            "kumas_cinsi": ["kumaş cinsi", "kumaş", "kumaş bazında"],
            "renk": ["renk", "renge göre", "renk bazında"],
            "asama": ["aşama", "boyama", "yıkama", "apre", "kurutma", "aşamaya göre"],
            "musteri": ["müşteri", "firma", "müşteriye göre"],
            "hafta_gunu": ["haftanın günü", "güne göre", "günlere göre"],
        },
        "time_dim": "tarih",
        "companies": ["boyahane"],
        "sectors": ["tekstil-boyahane"],
        "erp": "Mikro V16",
    },
    ("boyahane", "surdurulebilirlik"): {
        "label": "sürdürülebilirlik",
        "measures": {
            "su_yogunlugu_lt_kg": ["su yoğunluğu", "kg başına su", "spesifik su tüketimi"],
            "enerji_yogunlugu_kwh_kg": ["enerji yoğunluğu", "kg başına enerji", "spesifik enerji"],
            "toplam_su_lt": ["su tüketimi", "toplam su", "ne kadar su kullandık"],
            "toplam_enerji_kwh": ["enerji tüketimi", "elektrik tüketimi", "kwh", "ne kadar enerji"],
            "kimyasal_yogunlugu_tl_kg": ["kimyasal yoğunluğu", "kg başına kimyasal maliyet"],
        },
        "dimensions": {
            "makine": ["makine", "makine bazında"],
            "kumas_cinsi": ["kumaş", "kumaş bazında"],
            "asama": ["aşama", "boyama", "yıkama"],
            "musteri": ["müşteri", "müşteriye göre"],
        },
        "time_dim": "tarih",
        "companies": ["boyahane"],
        "sectors": ["tekstil-boyahane"],
        "erp": "Mikro V16",
    },
    ("boyahane", "oee"): {
        "label": "OEE / makine verimi",
        "measures": {
            "ort_oee": ["oee", "verim", "randıman", "makine verimi", "verimliliğimiz"],
            "ort_kullanilabilirlik": ["kullanılabilirlik", "availability", "makine kullanım oranı"],
            "ort_performans": ["performans", "makine performansı"],
            "ort_kalite": ["kalite oranı", "kalite"],
            "toplam_durus_dakika": ["duruş süresi", "arıza süresi", "downtime", "duruş dakikası"],
            "toplam_uretim_kg": ["üretim miktarı", "üretim", "ne kadar ürettik"],
            "toplam_fire_kg": ["fire", "oee fire", "fire kg"],
        },
        "dimensions": {
            "makine": ["makine", "makine bazında", "cihaz"],
            "vardiya": ["vardiya", "vardiyaya göre"],
            "personel_kodu": ["personel", "operatör", "çalışan bazında", "kişiye göre"],
            "cinsiyet": ["cinsiyet", "cinsiyete göre"],
            "hafta_gunu": ["haftanın günü", "güne göre"],
        },
        "time_dim": "tarih",
        "companies": ["boyahane"],
        "sectors": ["tekstil-boyahane"],
        "erp": "Mikro V16",
    },
}

# Kullanıcı tipleri ve kendi jargonları
USER_TYPES = {
    "patron": {
        "label": "Patron/CEO",
        "phrases": ["toplam", "genel", "tüm", "özetle", "kısaca", "rakam ver", "kaç para"],
    },
    "muhasebeci": {
        "label": "Muhasebeci",
        "phrases": ["bakiye", "borç/alacak", "ekstre", "hesap", "muhasebe"],
    },
    "satis_muduru": {
        "label": "Satış Müdürü",
        "phrases": ["satış", "müşteri", "ciro", "fatura", "sipariş"],
    },
    "uretim_muduru": {
        "label": "Üretim/Operasyon Müdürü",
        "phrases": ["üretim", "makine", "fire", "verim", "parti"],
    },
    "depo_sorumlusu": {
        "label": "Depo Sorumlusu",
        "phrases": ["stok", "miktar", "depo", "giriş", "çıkış"],
    },
    "finans_uzmani": {
        "label": "Finans Uzmanı",
        "phrases": ["nakit", "vade", "yaşlandırma", "vadesi geçen", "tahsilat"],
    },
    "veri_analisti": {
        "label": "Veri Analisti",
        "phrases": ["trend", "kırılım", "karşılaştırma", "yoy", "mom"],
    },
    "satin_alma": {
        "label": "Satın Alma",
        "phrases": ["alım", "tedarik", "tedarikçi", "hammadde", "satın alma"],
    },
    "saha_personeli": {
        "label": "Saha Personeli",
        "phrases": ["bugün", "dün", "bu hafta", "ne var", "durum"],
    },
}

# Dönem ifadeleri — basit → karmaşık
PERIODS_BY_LEVEL = {
    1: ["bu yıl", "geçen ay", "bu ay"],
    2: ["son 3 ay", "2. çeyrek", "geçen yıl", "temmuz", "son 30 gün"],
    3: ["ocak-mart", "yılın ilk yarısı", "son çeyrek", "2024", "2025"],
    4: ["bu yıl aynı dönem geçen yıl", "son 2 yıl", "yıllık büyüme"],
    5: ["2023 vs 2024 vs 2025", "son 5 yıl", "çeyrekler arası karşılaştırma"],
}

# Kırılım kalıpları
BREAKDOWN_PATTERNS = [
    "{dim} bazında",
    "{dim} göre",
    "{dim} kırılımında",
    "{dim} detayında",
    "her {dim} için",
    "{dim} itibarıyla",
]

# TopN kalıpları
TOPN_PATTERNS = [
    "en yüksek {n} {dim}",
    "ilk {n} {dim}",
    "top {n} {dim}",
    "en fazla {n} {dim}",
    "en düşük {n} {dim}",
    "en kötü {n} {dim}",
]

# Sıralama ekleri
SORT_PATTERNS = [
    "yüksekten düşüğe",
    "düşükten yükseğe",
    "en yüksekten sırala",
    "sıralı göster",
    "büyükten küçüğe",
]

# Granülarity
GRAN_PATTERNS = [
    "aylık",
    "haftalık",
    "günlük",
    "çeyreklere göre",
    "yıllık",
]

# Kırılım suffixleri (çok-boyut)
FILTER_PHRASES = {
    "parti": ["boyama aşamasında", "yıkama aşamasında", "apre aşamasında"],
    "oee": ["A vardiyasında", "B vardiyasında", "gece vardiyasında"],
    "ticaret": ["satış faturalarında", "alış faturalarında"],
    "cari": ["borç kalanı olan", "alacaklı olduğumuz"],
    "yaslandirma": ["vadesi geçmiş", "30 günden fazla gecikmiş"],
    "mal": ["çıkış hareketlerinde", "giriş hareketlerinde"],
    "surdurulebilirlik": ["boyama aşamasında", "kurutma aşamasında"],
}

# Jenerik şirketler (gelecek müşteriler için)
GENERIC_COMPANIES = [
    {"company": "generic-perakende", "sector": "perakende", "erp": "jenerik"},
    {"company": "generic-gida", "sector": "gida", "erp": "jenerik"},
    {"company": "generic-metal", "sector": "metal", "erp": "jenerik"},
    {"company": "generic-kimya", "sector": "kimya", "erp": "jenerik"},
    {"company": "generic-insaat", "sector": "insaat", "erp": "jenerik"},
    {"company": "generic-lojistik", "sector": "lojistik", "erp": "jenerik"},
    {"company": "generic-mobilya", "sector": "mobilya", "erp": "jenerik"},
    {"company": "generic-otomotiv", "sector": "otomotiv-yan-sanayi", "erp": "jenerik"},
]

# ──────────────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ──────────────────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Dedup için normalize: küçük harf, diakritik koru, noktalama/boşluk sadeleştir."""
    t = text.lower().strip()
    # Çoklu boşluk → tek boşluk
    t = re.sub(r"\s+", " ", t)
    # Noktalama kaldır (? ! . , ; :)
    t = re.sub(r"[?!.,;:]", "", t)
    return t


def load_existing(path: Path) -> set[str]:
    """Mevcut queries.jsonl'den normalize edilmiş sorgu setini yükle."""
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


def make_record(id_: int, company: str, sector: str, erp: str,
                user_type: str, difficulty: int, turns: list[str],
                tags: list[str] | None = None) -> dict:
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
# ÜRETİM FONKSİYONLARI
# ──────────────────────────────────────────────────────────────────────────────

def gen_difficulty_1(cube_key, cube_info, seen_norms: set) -> list[dict]:
    """Zorluk 1: tek ölçü + tek dönem."""
    records = []
    erp_key, cube_name = cube_key
    companies = cube_info["companies"]
    sectors = cube_info["sectors"]
    erp = cube_info["erp"]

    for company, sector in zip(companies, sectors + sectors):
        for measure, phrasings in cube_info["measures"].items():
            for phrasing in phrasings:
                for period in PERIODS_BY_LEVEL[1] + PERIODS_BY_LEVEL[2]:
                    for user_type in ["patron", "satis_muduru", "muhasebeci"]:
                        # Basit soru kalıpları
                        templates = [
                            f"{period} {phrasing}",
                            f"{phrasing} {period}",
                            f"{period} {phrasing} nedir",
                            f"{period} {phrasing} ne kadar",
                            f"{phrasing} ne kadar {period}",
                        ]
                        for tmpl in templates:
                            norm = normalize(tmpl)
                            if norm not in seen_norms and len(norm) > 5:
                                seen_norms.add(norm)
                                records.append({
                                    "_company": company, "_sector": sector, "_erp": erp,
                                    "_user": user_type, "_diff": 1,
                                    "_turns": [tmpl], "_tags": [cube_name, measure],
                                })
    return records


def gen_difficulty_2(cube_key, cube_info, seen_norms: set) -> list[dict]:
    """Zorluk 2: ölçü + dönem + kırılım."""
    records = []
    erp_key, cube_name = cube_key
    companies = cube_info["companies"]
    sectors = cube_info["sectors"]
    erp = cube_info["erp"]

    dims = cube_info.get("dimensions", {})

    for company, sector in zip(companies, sectors + sectors):
        for measure, m_phrasings in cube_info["measures"].items():
            for period in PERIODS_BY_LEVEL[1] + PERIODS_BY_LEVEL[2]:
                for dim_name, d_phrasings in dims.items():
                    for m_phr in m_phrasings[:3]:  # ilk 3 phrasing
                        for d_phr in d_phrasings[:2]:
                            for bp in BREAKDOWN_PATTERNS[:3]:
                                breakdown = bp.format(dim=d_phr)
                                templates = [
                                    f"{period} {m_phr} {breakdown}",
                                    f"{breakdown} {period} {m_phr}",
                                    f"{m_phr} {breakdown} {period}",
                                ]
                                for tmpl in templates:
                                    norm = normalize(tmpl)
                                    if norm not in seen_norms and len(norm) > 8:
                                        seen_norms.add(norm)
                                        records.append({
                                            "_company": company, "_sector": sector, "_erp": erp,
                                            "_user": "satis_muduru", "_diff": 2,
                                            "_turns": [tmpl], "_tags": [cube_name, measure, dim_name],
                                        })
    return records


def gen_difficulty_3(cube_key, cube_info, seen_norms: set) -> list[dict]:
    """Zorluk 3: ölçü + kırılım + filtre + sıralama + top-N."""
    records = []
    erp_key, cube_name = cube_key
    companies = cube_info["companies"]
    sectors = cube_info["sectors"]
    erp = cube_info["erp"]
    dims = cube_info.get("dimensions", {})
    cube_filters = FILTER_PHRASES.get(cube_name, [])

    for company, sector in zip(companies, sectors + sectors):
        for measure, m_phrasings in cube_info["measures"].items():
            for period in PERIODS_BY_LEVEL[2] + PERIODS_BY_LEVEL[3]:
                for dim_name, d_phrasings in list(dims.items())[:3]:
                    for n in [3, 5, 10]:
                        for m_phr in m_phrasings[:2]:
                            for d_phr in d_phrasings[:2]:
                                # TopN + sıralama
                                topn = TOPN_PATTERNS[0].format(n=n, dim=d_phr)
                                templates = [
                                    f"{period} {m_phr} — {topn}",
                                    f"{topn} {period} {m_phr}",
                                    f"{period} {m_phr} {SORT_PATTERNS[0]}",
                                ]
                                # Filtre ekle
                                if cube_filters:
                                    for filt in cube_filters[:2]:
                                        templates.append(
                                            f"{period} {filt} {m_phr} {topn}"
                                        )
                                for tmpl in templates:
                                    norm = normalize(tmpl)
                                    if norm not in seen_norms and len(norm) > 10:
                                        seen_norms.add(norm)
                                        records.append({
                                            "_company": company, "_sector": sector, "_erp": erp,
                                            "_user": "veri_analisti", "_diff": 3,
                                            "_turns": [tmpl], "_tags": [cube_name, measure, f"top{n}"],
                                        })
    return records


def gen_difficulty_4(cube_key, cube_info, seen_norms: set) -> list[dict]:
    """Zorluk 4: çok-ölçü / dönemsel karşılaştırma / oran."""
    records = []
    erp_key, cube_name = cube_key
    companies = cube_info["companies"]
    sectors = cube_info["sectors"]
    erp = cube_info["erp"]
    measures = list(cube_info["measures"].items())
    dims = list(cube_info.get("dimensions", {}).items())

    # Çift-ölçü kombinasyonları
    for i, (m1, p1) in enumerate(measures):
        for j, (m2, p2) in enumerate(measures):
            if i >= j:
                continue
            for period in PERIODS_BY_LEVEL[3] + PERIODS_BY_LEVEL[4]:
                mp1 = p1[0]
                mp2 = p2[0]
                templates = [
                    f"{period} {mp1} ve {mp2}",
                    f"{period} {mp1} ile {mp2} karşılaştır",
                    f"{mp1} ve {mp2} {period} kıyasla",
                ]
                for company, sector in zip(companies, sectors + sectors):
                    for tmpl in templates:
                        norm = normalize(tmpl)
                        if norm not in seen_norms and len(norm) > 10:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": "finans_uzmani", "_diff": 4,
                                "_turns": [tmpl], "_tags": [cube_name, m1, m2, "multi-measure"],
                            })

    # YoY / MoM karşılaştırma
    yoy_periods = [
        ("bu yıl", "geçen yıl"),
        ("bu ay", "geçen ay"),
        ("2025", "2024"),
        ("bu çeyrek", "geçen çeyrek"),
    ]
    for m, m_phrasings in measures[:4]:
        mp = m_phrasings[0]
        for p_cur, p_prev in yoy_periods:
            for company, sector in zip(companies, sectors + sectors):
                templates = [
                    f"{mp} {p_cur} vs {p_prev}",
                    f"{p_cur} ile {p_prev} {mp} karşılaştırması",
                    f"{mp} yıllık büyüme {p_cur}",
                    f"{p_cur} {mp} büyümesi (yoy)",
                ]
                for tmpl in templates:
                    norm = normalize(tmpl)
                    if norm not in seen_norms and len(norm) > 10:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "finans_uzmani", "_diff": 4,
                            "_turns": [tmpl], "_tags": [cube_name, m, "yoy", "comparison"],
                        })

    # Oran soruları
    if len(measures) >= 2:
        m1_name, m1_phrases = measures[0]
        m2_name, m2_phrases = measures[1]
        for period in PERIODS_BY_LEVEL[3]:
            for company, sector in zip(companies, sectors + sectors):
                templates = [
                    f"{period} {m1_phrases[0]} / {m2_phrases[0]} oranı",
                    f"{period} her {m2_phrases[0]}'na düşen {m1_phrases[0]}",
                ]
                for tmpl in templates:
                    norm = normalize(tmpl)
                    if norm not in seen_norms:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 4,
                            "_turns": [tmpl], "_tags": [cube_name, "ratio", "multi-measure"],
                        })

    return records


def gen_difficulty_5_multiturn(cube_key, cube_info, seen_norms: set) -> list[dict]:
    """Zorluk 5: çok-adımlı konuşma zincirleri (drill-down, refine, pivot, cube-cross)."""
    records = []
    erp_key, cube_name = cube_key
    companies = cube_info["companies"]
    sectors = cube_info["sectors"]
    erp = cube_info["erp"]
    measures = list(cube_info["measures"].items())
    dims = list(cube_info.get("dimensions", {}).items())

    if not measures:
        return records

    m0_name, m0_phrasings = measures[0]
    m0 = m0_phrasings[0]
    d0_name = dims[0][0] if dims else None
    d0 = dims[0][1][0] if dims else "kırılım"

    for company, sector in zip(companies, sectors + sectors):
        # Desen 1: Açılış → granülarity → kırılım → top-N → görünüm
        chain_3 = [
            f"bu yıl {m0}",
            "aylık kır",
            f"en yüksek 5 {d0}",
        ]
        chain_5 = [
            f"bu yıl {m0}",
            "aylık göster",
            f"{d0} bazında kır",
            "en yüksek 10 sırala",
            "grafik olarak göster",
        ]
        chain_7 = [
            f"bu yıl {m0}",
            "geçen yıl ile karşılaştır",
            f"{d0} bazında kır",
            "aylık trend",
            f"en kötü 5 {d0}",
            "neden düşük bunlar",
            "son 3 ayı göster",
        ]
        chain_10 = [
            f"bu yıl {m0}",
            "aylık kır",
            f"{d0} bazında göster",
            "geçen yılla karşılaştır",
            f"en düşük 3 {d0}",
            "bu 3 için aylık detay",
            "büyüme oranı ne",
            f"bu {d0} için diğer ölçüleri de göster",
            "çeyreklik özetle",
            "tablo olarak indir",
        ]

        for chain, n in [(chain_3, 3), (chain_5, 5), (chain_7, 7), (chain_10, 10)]:
            # Normalize ilk turna bak (tekillik için)
            key = normalize(chain[0] + " | " + str(n))
            if key not in seen_norms:
                seen_norms.add(key)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "veri_analisti", "_diff": 5,
                    "_turns": chain, "_tags": [cube_name, f"{n}-turn", "multi-turn"],
                })

        # Desen 2: Konu değiştirme zinciri (cross-cube implicit)
        if len(measures) >= 2:
            m1 = measures[1][1][0]
            cross_chain = [
                f"bu yıl {m0}",
                f"peki {m1} nasıl",
                "ikisini karşılaştır",
                "aylık trend göster",
                "geçen yılla kıyasla",
            ]
            key = normalize(cross_chain[0] + "|cross|" + m1)
            if key not in seen_norms:
                seen_norms.add(key)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "patron", "_diff": 5,
                    "_turns": cross_chain,
                    "_tags": [cube_name, "cross-measure", "multi-turn", "topic-change"],
                })

        # Desen 3: Patron kısa zincirleri
        patron_chain = [
            f"geçen ay ne sattık",
            "bu ay nasıl",
            "yıllık toplamda neredeyiz",
        ]
        key = normalize("patron:" + patron_chain[0])
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": company, "_sector": sector, "_erp": erp,
                "_user": "patron", "_diff": 5,
                "_turns": patron_chain,
                "_tags": [cube_name, "3-turn", "patron"],
            })

    return records


def gen_difficulty_5_derived_metrics(seen_norms: set) -> list[dict]:
    """Zorluk 5: Türetilmiş metrikler (DSO, DIO, DPO, CCC, brüt marj) — class-b."""
    records = []
    companies_sectors = [
        ("boyahane", "tekstil-boyahane", "Mikro V16"),
        ("atiksan", "geri-donusum", "Mikro V16"),
        ("gulteks", "kumas-ticareti", "Logo Start 3"),
        ("gitas", "tarim-ticareti", "Netsis"),
    ]

    derived_questions = [
        # DSO (Days Sales Outstanding)
        ("DSO'muz kaç gün bu yıl", ["dso", "multi-cube", "class-b"]),
        ("alacak tahsil süremiz kaç gün", ["dso", "multi-cube", "class-b"]),
        ("ortalama tahsilat günümüz", ["dso", "multi-cube", "class-b"]),
        # DPO (Days Payable Outstanding)
        ("tedarikçilere ortalama kaç günde ödüyoruz", ["dpo", "multi-cube", "class-b"]),
        ("ödeme günümüz kaç", ["dpo", "multi-cube", "class-b"]),
        # DIO (Days Inventory Outstanding)
        ("stok dönüş süremiz kaç gün", ["dio", "multi-cube", "class-b"]),
        ("ortalama stokta kaç gün bekliyoruz", ["dio", "multi-cube", "class-b"]),
        # CCC (Cash Conversion Cycle)
        ("nakit dönüşüm süremiz kaç gün", ["ccc", "multi-cube", "class-b"]),
        ("ccc hesabı bu yıl nasıl", ["ccc", "multi-cube", "class-b"]),
        # Brüt marj
        ("brüt marjımız bu yıl", ["gross-margin", "multi-cube", "class-b"]),
        ("satış karlılığımız nedir", ["gross-margin", "class-b"]),
        ("net karımız ne kadar bu çeyrekte", ["net-profit", "class-b"]),
        # Multi-cube birleşik
        ("satışlar artarken neden nakit azalıyor", ["multi-cube", "class-b", "diagnostic"]),
        ("en karlı müşterilerimiz hangileri", ["multi-cube", "class-b"]),
        ("hangi ürün grubu en yüksek karlılık", ["multi-cube", "class-b"]),
        # Sektöre özgü türetilmiş
        ("su tüketimimizi azaltırsak kar marjı ne olur", ["what-if", "class-b"]),
        ("fire oranı %1 düşseydi kar ne kadar artardı", ["what-if", "class-b"]),
        ("enerji verimliliği ile oee korelasyonu", ["correlation", "class-b", "multi-cube"]),
    ]

    for q, tags in derived_questions:
        for company, sector, erp in companies_sectors:
            norm = normalize(company + ":" + q)
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "finans_uzmani", "_diff": 5,
                    "_turns": [q], "_tags": tags,
                })
    return records


def gen_generic_sector_questions(seen_norms: set) -> list[dict]:
    """Jenerik sektörler için genel sorular (class-b — henüz cubeleri yok)."""
    records = []
    generic_templates = [
        "bu ay satışlarım ne kadar",
        "en çok satan ürünlerim hangileri",
        "stok seviyem ne durumda",
        "vadesi geçen alacaklarım",
        "geçen ay ile bu ay kıyasla",
        "nakit akışım nasıl",
        "tedarikçi borcum ne kadar",
        "müşteri başına ortalama gelir",
        "sezonluk satış trendi",
        "en iyi satış temsilcim kim",
    ]

    for gc in GENERIC_COMPANIES:
        for tmpl in generic_templates:
            norm = normalize(gc["company"] + ":" + tmpl)
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": gc["company"], "_sector": gc["sector"], "_erp": gc["erp"],
                    "_user": "patron", "_diff": 1,
                    "_turns": [tmpl], "_tags": ["generic", "class-b"],
                })
    return records


def gen_user_type_variations(cube_key, cube_info, seen_norms: set) -> list[dict]:
    """Her kullanıcı tipinin jargonuyla aynı ölçüyü soran varyasyonlar."""
    records = []
    erp_key, cube_name = cube_key
    companies = cube_info["companies"]
    sectors = cube_info["sectors"]
    erp = cube_info["erp"]

    user_question_map = {
        "patron": [
            "genel satış durumu nedir",
            "bu ay rakamlar nasıl",
            "kısaca özetle",
            "bu hafta ne durumdasın",
        ],
        "muhasebeci": [
            "cari hesap ekstresi",
            "borç/alacak bakiyesi",
            "hesap hareketleri",
            "ödeme vadesi gelen hesaplar",
        ],
        "satis_muduru": [
            "en iyi müşterilerim bu ay",
            "satış performansım geçen aya göre nasıl",
            "hangi bölgede satış düştü",
        ],
        "depo_sorumlusu": [
            "bugün çıkış var mı",
            "stok miktarları nerede",
            "hangi malzeme azaldı",
        ],
        "finans_uzmani": [
            "vadesi yaklaşan alacaklar",
            "30 günü geçmiş borçlar",
            "yaşlandırma raporu",
        ],
        "satin_alma": [
            "bu ay alımlarımız ne kadar",
            "hangi tedarikçiden ne aldık",
            "alım maliyeti geçen yıla göre",
        ],
        "uretim_muduru": [
            "makinelerin verimi nasıl",
            "fire oranı bu hafta",
            "hangi makinede en çok duruş var",
        ],
        "saha_personeli": [
            "bugün kaç hareket var",
            "bu vardiyada üretim ne",
            "son işlemim ne zaman",
        ],
        "veri_analisti": [
            "geçen yılın aynı haftasıyla karşılaştır",
            "aylık trend grafiği",
            "yıllık büyüme oranı",
        ],
    }

    for company, sector in zip(companies, sectors + sectors):
        for user_type, questions in user_question_map.items():
            for q in questions:
                # Her cube için user-tipi soruları etiketle
                norm = normalize(f"{company}:{cube_name}:{user_type}:{q}")
                if norm not in seen_norms:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": user_type, "_diff": 2,
                        "_turns": [q], "_tags": [cube_name, user_type, "user-type-var"],
                    })
    return records


def gen_erp_jargon_variations(seen_norms: set) -> list[dict]:
    """ERP-spesifik jargon varyasyonları."""
    records = []

    erp_jargon = {
        "Mikro V16": [
            ("stok hareketi raporu", "ticaret"),
            ("cari kart dökümü", "cari"),
            ("sth_tutar toplamı bu ay", "ticaret"),
            ("cha_meblag bakiyesi", "cari"),
            ("mikro raporları aç", "ticaret"),
        ],
        "Logo Start 3": [
            ("logo fatura raporu", "ticaret"),
            ("logo cari ekstre", "cari"),
            ("nettotal bu ay", "ticaret"),
            ("grosstotal geçen yıl", "ticaret"),
            ("logo 3 stok çıkış", "mal"),
        ],
        "Netsis": [
            ("netsis fatura listesi", "ticaret"),
            ("netsis yaşlandırma raporu", "yaslandirma"),
            ("geneltoplam bu yıl", "ticaret"),
            ("tblcahar bakiye", "cari"),
            ("netsis şube raporu", "ticaret"),
        ],
    }

    company_erp_map = {
        "Mikro V16": [("boyahane", "tekstil-boyahane"), ("atiksan", "geri-donusum")],
        "Logo Start 3": [("gulteks", "kumas-ticareti")],
        "Netsis": [("gitas", "tarim-ticareti"), ("atiksan", "geri-donusum")],
    }

    for erp, questions in erp_jargon.items():
        for company, sector in company_erp_map.get(erp, []):
            for q, cube in questions:
                norm = normalize(f"{company}:{q}")
                if norm not in seen_norms:
                    seen_norms.add(norm)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": "muhasebeci", "_diff": 1,
                        "_turns": [q], "_tags": [cube, "erp-jargon"],
                    })
    return records


def gen_long_multiturn_chains(seen_norms: set) -> list[dict]:
    """Uzun (10-20 adım) çok-adımlı konuşma zincirleri — zorluk 5."""
    records = []

    scenarios = [
        {
            "company": "boyahane", "sector": "tekstil-boyahane", "erp": "Mikro V16",
            "user": "patron", "diff": 5,
            "tags": ["parti", "oee", "multi-cube", "15-turn"],
            "turns": [
                "bu yıl toplam ciromuz ne kadar",
                "geçen yıla göre büyüme oranımız",
                "hangi müşteri en çok ciro yaptı",
                "bu müşteri için aylık kırılım göster",
                "peki fire oranımız nasıl bu yıl",
                "en yüksek fire hangi makinede",
                "bu makine için OEE verisini göster",
                "OEE geçen yıla göre nasıl değişmiş",
                "en kötü 3 ay hangisi OEE açısından",
                "bu aylarda duruş nedeni ne olmuş",
                "su ve enerji tüketimimiz nasıl bu yıl",
                "enerji yoğunluğu kg başına kaç kwh",
                "en fazla enerji hangi aşamada kullanılıyor",
                "boyama aşamasında su tüketimi aylık trend",
                "özet olarak ne yapmalıyız",
            ],
        },
        {
            "company": "gitas", "sector": "tarim-ticareti", "erp": "Netsis",
            "user": "finans_uzmani", "diff": 5,
            "tags": ["yaslandirma", "cari", "ticaret", "multi-cube", "12-turn"],
            "turns": [
                "bu ay satışlarımız ne kadar",
                "müşteri bazında kır",
                "en yüksek 5 müşteri satışa göre",
                "bu 5 müşterinin vadesi geçen alacakları nedir",
                "yaşlandırma kovalarına göre dağılım",
                "90 günü aşmış alacaklar hangi müşteride",
                "toplam açık bakiyemiz ne",
                "bu müşterilerle geçen yıl nasıldı",
                "alacak/satış oranımız normal mi",
                "tahsilat süreci nerede sıkıştı",
                "şube bazında yaşlandırma farkı var mı",
                "aksiyon öner",
            ],
        },
        {
            "company": "gulteks", "sector": "kumas-ticareti", "erp": "Logo Start 3",
            "user": "satis_muduru", "diff": 5,
            "tags": ["ticaret", "mal", "cari", "multi-cube", "10-turn"],
            "turns": [
                "bu yıl satışlarım ne kadar",
                "kumaş tipine göre kır",
                "en çok satan kumaş cinsim hangisi",
                "bu kumaş için aylık satış trendi",
                "brüt satış ve net satış farkı neden",
                "alım maliyetim bu kumaş için",
                "kar marjım ne kadar bu kumaşta",
                "rakip fiyatlarla kıyasla",
                "satış miktarı bu ay geçen aya göre",
                "en karlı müşterime özel rapor",
            ],
        },
        {
            "company": "atiksan", "sector": "geri-donusum", "erp": "Mikro V16",
            "user": "uretim_muduru", "diff": 5,
            "tags": ["ticaret", "cari", "multi-cube", "8-turn"],
            "turns": [
                "bu ay hurda alımımız kaç ton",
                "malzeme tipine göre kır",
                "en çok aldığımız 3 malzeme",
                "bu malzemelerin alım fiyatı aylık nasıl değişti",
                "satış tarafında ne yapıldı",
                "alım vs satış farkımız",
                "tedarikçi bazında alım dağılımı",
                "gelecek ay alım planı ne olmalı",
            ],
        },
    ]

    for sc in scenarios:
        key = normalize(sc["company"] + ":" + sc["turns"][0] + ":" + str(len(sc["turns"])))
        if key not in seen_norms:
            seen_norms.add(key)
            records.append({
                "_company": sc["company"], "_sector": sc["sector"], "_erp": sc["erp"],
                "_user": sc["user"], "_diff": sc["diff"],
                "_turns": sc["turns"], "_tags": sc["tags"],
            })

    return records


def gen_real_phrasing_variations(seen_norms: set) -> list[dict]:
    """REAL_PHRASINGS (nl_corpus.py) genişletilmiş varyasyonları."""
    records = []

    REAL_PHRASINGS_EXTENDED = {
        "satis_tutari": [
            "hasılat", "ne kadar sattık", "satışlarımız", "gelirimiz", "cirosu",
            "ne sattım bu ay", "ay sonu ciromuz", "toplam gelirimiz", "satış rakamları",
            "ne kadar para girdi", "gelir tarafı", "satış bütçesi tuttu mu",
        ],
        "alim_tutari": [
            "ne kadar aldık", "alımlarımız", "satın almalar", "tedariğimiz",
            "tedarik maliyetimiz", "hammadde gideri", "malzeme masrafı",
            "satın alma bütçesi", "ne harcadık alımlara",
        ],
        "bakiye": [
            "kalan borcu", "hesap durumu", "ne kadar borçlu",
            "carinin durumu", "hesabın güncel hali", "bakiyesi ne",
            "kalan tutar", "net pozisyon",
        ],
        "toplam_borc": [
            "borçları", "borç durumu", "ne kadar borcu var",
            "toplam yükümlülük", "borç yükü", "ödenmesi gereken",
        ],
        "toplam_alacak": [
            "tahsilatlar", "alacaklarımız", "ne kadar alacağımız var",
            "toplayacağımız para", "bize borçlu olanlar",
        ],
        "satis_miktari": [
            "kaç kilo satıldı", "satılan miktar", "ne kadar sevk ettik",
            "çıkan miktar", "satış adedi", "kaç ton sattık", "kaç metre sattık",
        ],
        "alim_miktari": [
            "kaç kilo aldık", "alınan miktar", "topladığımız",
            "gelen miktar", "tedarik miktarı", "kaç ton aldık",
        ],
        "hareket_sayisi": [
            "kaç işlem oldu", "kaç hareket var", "işlem adedi",
            "kayıt sayısı", "hareket adedi",
        ],
        "satis_fatura_sayisi": [
            "kaç fatura kesildi", "fatura adedi", "kesilen fatura",
            "fatura sayımız", "kaç belge düzenlendi",
        ],
        "kar": [
            "kazancımız", "ne kadar kar ettik", "kârımız",
            "bıraktığı para", "net gelir", "kazanç ne kadar",
        ],
        "fire_orani_yuzde": [
            "ne kadar fire verdik", "fire durumu", "zayiat oranı",
            "kayıp oranımız", "israf yüzdesi", "fire % kaç",
        ],
        "ort_oee": [
            "verimliliğimiz", "makine verimi", "randıman",
            "ekipman etkinliği", "makineler ne kadar verimli",
        ],
        "vadesi_gecen": [
            "vadesi geçen alacaklar", "gecikmiş tahsilatlar",
            "muaccel alacak", "vadesi geçmiş", "geciken borçlar",
        ],
    }

    company_measure_map = {
        "satis_tutari": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                          ("gulteks", "kumas-ticareti", "Logo Start 3"),
                          ("gitas", "tarim-ticareti", "Netsis")],
        "alim_tutari": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                         ("atiksan", "geri-donusum", "Mikro V16"),
                         ("gitas", "tarim-ticareti", "Netsis")],
        "bakiye": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                    ("gitas", "tarim-ticareti", "Netsis")],
        "toplam_borc": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                          ("gulteks", "kumas-ticareti", "Logo Start 3")],
        "toplam_alacak": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                           ("gitas", "tarim-ticareti", "Netsis")],
        "satis_miktari": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                           ("gitas", "tarim-ticareti", "Netsis")],
        "alim_miktari": [("atiksan", "geri-donusum", "Mikro V16"),
                          ("gitas", "tarim-ticareti", "Netsis")],
        "hareket_sayisi": [("boyahane", "tekstil-boyahane", "Mikro V16"),
                            ("gulteks", "kumas-ticareti", "Logo Start 3")],
        "satis_fatura_sayisi": [("gulteks", "kumas-ticareti", "Logo Start 3"),
                                  ("gitas", "tarim-ticareti", "Netsis")],
        "kar": [("boyahane", "tekstil-boyahane", "Mikro V16")],
        "fire_orani_yuzde": [("boyahane", "tekstil-boyahane", "Mikro V16")],
        "ort_oee": [("boyahane", "tekstil-boyahane", "Mikro V16")],
        "vadesi_gecen": [("gitas", "tarim-ticareti", "Netsis"),
                          ("atiksan", "geri-donusum", "Mikro V16")],
    }

    periods = ["bu yıl", "geçen ay", "bu ay", "son 3 ay", ""]

    for measure, phrasings in REAL_PHRASINGS_EXTENDED.items():
        companies = company_measure_map.get(measure, [])
        for phr in phrasings:
            for p in periods:
                q = f"{p} {phr}".strip()
                for company, sector, erp in companies:
                    norm = normalize(f"{company}:{q}")
                    if norm not in seen_norms and len(norm) > 4:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "patron", "_diff": 1,
                            "_turns": [q], "_tags": [measure, "real-phrasing"],
                        })
    return records


def gen_capability_questions(seen_norms: set) -> list[dict]:
    """Yetenek/meta soruları."""
    records = []
    cap_questions = [
        "hangi kırılımlar var",
        "hangi kırılımlara göre detaylandırabilirim",
        "kırılımları ver",
        "kırılımları göster",
        "başka ne sorabilirim",
        "neler yapabilirsin",
        "hangi ölçüler var",
        "bu raporu nasıl detaylandırırım",
        "hangi raporları çekebilirsin",
        "ne tür analizler yapabilirsin",
        "desteklediğin cube'lar neler",
        "sana ne sorabilirim",
        "mevcut metrikler neler",
        "hangi boyutlara göre filtreleyebilirim",
    ]
    companies = [("boyahane", "tekstil-boyahane", "Mikro V16"),
                 ("gitas", "tarim-ticareti", "Netsis"),
                 ("gulteks", "kumas-ticareti", "Logo Start 3")]

    for q in cap_questions:
        for company, sector, erp in companies:
            norm = normalize(f"{company}:cap:{q}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "veri_analisti", "_diff": 1,
                    "_turns": [q], "_tags": ["capability", "meta"],
                })
    return records


def gen_noise_questions(seen_norms: set) -> list[dict]:
    """Gürültü/alakasız sorular — sistem bunlara duvar ya da meta ile cevap vermeli."""
    records = []
    noise = [
        "merhaba", "dima nedir", "teşekkürler", "asdf qwerty zxcv",
        "bana bir fıkra anlat", "hava nasıl", "@#$%^&*",
        "select * from users", "drop table faturalar", "python kodu yaz",
        "en iyi film hangisi", "kaç yaşındasın", "seni seviyorum",
        "1234567890", "abc123", "test", "deneme",
        "ne yapıyorsun", "kim yarattı seni", "merhaba dünya",
        "lorem ipsum dolor sit amet",
    ]
    companies = [("boyahane", "tekstil-boyahane", "Mikro V16")]
    for q in noise:
        for company, sector, erp in companies:
            norm = normalize(f"noise:{q}")
            if norm not in seen_norms and q.strip():
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "saha_personeli", "_diff": 1,
                    "_turns": [q], "_tags": ["noise", "negative"],
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# ANA DÖNGÜ
# ──────────────────────────────────────────────────────────────────────────────

def run_generation(max_tur: int = 10):
    print(f"[generate.py] Mevcut queries.jsonl yükleniyor: {QUERIES_PATH}")
    seen_norms = load_existing(QUERIES_PATH)
    next_id = get_next_id(QUERIES_PATH)
    start_total = next_id - 1
    print(f"  Mevcut: {start_total} sorgu | sonraki ID: {next_id}")

    all_new: list[dict] = []

    # ── TUR 1: Difficulty 1 — tüm cube'lar × dönem × phrasing
    print("\n[TUR 1] Difficulty 1 — tek ölçü + tek dönem")
    batch = []
    for cube_key, cube_info in CUBE_SPACE.items():
        batch.extend(gen_difficulty_1(cube_key, cube_info, seen_norms))
    print(f"  TUR 1: {len(batch)} yeni sorgu üretildi")
    all_new.extend(batch)

    # ── TUR 2: Difficulty 2 — kırılım eklendi
    print("[TUR 2] Difficulty 2 — ölçü + dönem + kırılım")
    batch = []
    for cube_key, cube_info in CUBE_SPACE.items():
        batch.extend(gen_difficulty_2(cube_key, cube_info, seen_norms))
    print(f"  TUR 2: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 3: Difficulty 3 — filtre + sıralama + top-N
    print("[TUR 3] Difficulty 3 — filtre + sıralama + top-N")
    batch = []
    for cube_key, cube_info in CUBE_SPACE.items():
        batch.extend(gen_difficulty_3(cube_key, cube_info, seen_norms))
    print(f"  TUR 3: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 4: Difficulty 4 — çok-ölçü, YoY, oran
    print("[TUR 4] Difficulty 4 — çok-ölçü / YoY / oran")
    batch = []
    for cube_key, cube_info in CUBE_SPACE.items():
        batch.extend(gen_difficulty_4(cube_key, cube_info, seen_norms))
    print(f"  TUR 4: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 5: Difficulty 5 — çok-adımlı zincirler
    print("[TUR 5] Difficulty 5 — çok-adımlı zincirler")
    batch = []
    for cube_key, cube_info in CUBE_SPACE.items():
        batch.extend(gen_difficulty_5_multiturn(cube_key, cube_info, seen_norms))
    batch.extend(gen_difficulty_5_derived_metrics(seen_norms))
    batch.extend(gen_long_multiturn_chains(seen_norms))
    print(f"  TUR 5: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 6: Real phrasing varyasyonları
    print("[TUR 6] Real phrasing varyasyonları")
    batch = gen_real_phrasing_variations(seen_norms)
    print(f"  TUR 6: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 7: Kullanıcı tipi varyasyonları
    print("[TUR 7] Kullanıcı tipi varyasyonları")
    batch = []
    for cube_key, cube_info in CUBE_SPACE.items():
        batch.extend(gen_user_type_variations(cube_key, cube_info, seen_norms))
    print(f"  TUR 7: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 8: ERP jargon
    print("[TUR 8] ERP jargon varyasyonları")
    batch = gen_erp_jargon_variations(seen_norms)
    print(f"  TUR 8: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 9: Jenerik sektörler (class-b)
    print("[TUR 9] Jenerik sektör soruları (class-b)")
    batch = gen_generic_sector_questions(seen_norms)
    print(f"  TUR 9: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ── TUR 10: Yetenek + gürültü
    print("[TUR 10] Yetenek soruları + gürültü")
    batch = gen_capability_questions(seen_norms)
    batch.extend(gen_noise_questions(seen_norms))
    print(f"  TUR 10: {len(batch)} yeni sorgu")
    all_new.extend(batch)

    # ────── YAZIM ──────
    print(f"\n[YAZIM] Toplam {len(all_new)} yeni kayıt queries.jsonl'e ekleniyor...")
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

    # ────── İSTATİSTİKLER ──────
    diff_count: Counter = Counter()
    company_count: Counter = Counter()
    sector_count: Counter = Counter()
    user_count: Counter = Counter()
    tag_count: Counter = Counter()

    for raw in all_new:
        diff_count[raw["_diff"]] += 1
        company_count[raw["_company"]] += 1
        sector_count[raw["_sector"]] += 1
        user_count[raw["_user"]] += 1
        for t in raw["_tags"]:
            tag_count[t] += 1

    print(f"\nTOPLAM ÜRETİLEN: {total_now} (bu tur +{len(all_new)}) | "
          f"zorluk kırılımı: {dict(sorted(diff_count.items()))}")

    stats_lines = [
        f"# Sorgu Korpus İstatistikleri",
        f"",
        f"Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## Toplam",
        f"- **Toplam tekrarsız sorgu**: {total_now}",
        f"- **Bu turda eklenen**: +{len(all_new)}",
        f"",
        f"## Zorluk Kırılımı",
    ]
    for d in sorted(diff_count.keys()):
        stats_lines.append(f"- Zorluk {d}: {diff_count[d]}")

    stats_lines += [
        f"",
        f"## Şirket Kırılımı",
    ]
    for c, cnt in company_count.most_common():
        stats_lines.append(f"- {c}: {cnt}")

    stats_lines += [
        f"",
        f"## Sektör Kırılımı",
    ]
    for s, cnt in sector_count.most_common():
        stats_lines.append(f"- {s}: {cnt}")

    stats_lines += [
        f"",
        f"## Kullanıcı Tipi Kırılımı",
    ]
    for u, cnt in user_count.most_common():
        stats_lines.append(f"- {u}: {cnt}")

    stats_lines += [
        f"",
        f"## En Sık Etiketler (Top 20)",
    ]
    for t, cnt in tag_count.most_common(20):
        stats_lines.append(f"- {t}: {cnt}")

    stats_lines += [
        f"",
        f"## Boşluk Analizi",
        f"- Jenerik sektörler (class-b): {tag_count.get('class-b', 0)} sorgu (henüz cube yok)",
        f"- Multi-cube: {tag_count.get('multi-cube', 0)} sorgu (birleşik cube desteği bekleniyor)",
        f"- Türetilmiş metrikler (DSO/CCC/DIO): sınırlı (class-b olarak işaretlendi)",
        f"",
        f"## Bir Sonraki Koşu",
        f"- queries.jsonl mevcut sorgu setini okuyup dedup ederek kaldığı yerden devam eder",
        f"- Eklenecek: daha uzun (15-20 adım) zincirler, diyalekt/yazım hataları, cross-cube senaryolar",
        f"- Hedef: 20.000+ tekrarsız sorgu",
        f"",
        f"## Kaynaklar",
        f"- demo/packs/kaynak/*/cubes/*/metadata.yml — gerçek cube tanımları",
        f"- demo/packs/sektor/boyahane/cubes/*/metadata.yml — boyahane sektör cube'ları",
        f"- demo/packs/modul/oee/cubes/oee/metadata.yml — OEE modülü",
        f"- lab/nl_corpus.py — REAL_PHRASINGS bankası",
        f"- app/archetypes.py — ölçü arketip sinonimleri",
    ]

    STATS_PATH.write_text("\n".join(stats_lines), encoding="utf-8")
    print(f"[stats.md] Güncellendi: {STATS_PATH}")
    print(f"[queries.jsonl] Yol: {QUERIES_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dima NL sorgu korpus üreteci")
    parser.add_argument("--tur", type=int, default=10, help="Maksimum tur sayısı")
    args = parser.parse_args()
    run_generation(max_tur=args.tur)
