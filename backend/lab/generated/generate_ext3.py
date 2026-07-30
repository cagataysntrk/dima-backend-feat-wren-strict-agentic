#!/usr/bin/env python3
"""
Round 4 — Büyük ölçekli phrasing genişletme (200k+ hedef)

Stratejisi:
- Mevcut cube ölçülerinin tüm kullanıcı tiplerine uyarlanmış tam phrasing matrisi
- Bağlaç + soru eki varyasyonları (ne kadar, nasıl, nedir, hangi, kaç, ne zaman)
- Çok-cümle soru formatları (şartlı, karşılaştırmalı, sıralı)
- Tüm şirket × tüm dönem × tüm kullanıcı tipi sweep (atlanmış kombinasyonlar)
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter
from itertools import product

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
# BÜYÜK PHRASING MATRİSİ
# ──────────────────────────────────────────────────────────────────────────────

COMPANIES_ALL = [
    ("boyahane", "tekstil-boyahane", "Mikro V16"),
    ("atiksan", "geri-donusum", "Mikro V16"),
    ("gulteks", "kumas-ticareti", "Logo Start 3"),
    ("gitas", "tarim-ticareti", "Netsis"),
]

# Soru çerçeveleri (tüm ölçüler bu çerçevelere sokulabilir)
QUESTION_FRAMES = [
    "{period} {measure} ne kadar",
    "{period} {measure} nedir",
    "{period} {measure} nasıl",
    "{period} {measure} kaç",
    "{measure} {period} ne kadar oldu",
    "{measure} {period} nedir",
    "{period} toplam {measure}",
    "{period} {measure} tutarı",
    "{period} {measure} miktarı",
    "bu {period_unit} {measure} ne kadar",
    "{measure} hakkında {period} rapor",
    "{period} {measure} özeti",
    "{period} {measure} rakamı",
    "{period} için {measure} bilgisi",
    "{measure} göster {period}",
    "{period} {measure} ver",
    "{period} {measure} listele",
    "{measure} ne durumda {period}",
    "{period} {measure} durumu",
    "{measure} {period} itibarıyla",
]

# Büyük ölçü kelime seti (tüm cube'lardan, arketip dahil)
MEASURE_WORDS_FULL = [
    # Satış ailesi
    ("satış", "satis_tutari"),
    ("ciro", "satis_tutari"),
    ("gelir", "satis_tutari"),
    ("hasılat", "satis_tutari"),
    ("net satış", "satis_tutari"),
    ("satışlarımız", "satis_tutari"),
    ("satış tutarı", "satis_tutari"),
    ("satış gelirimiz", "satis_tutari"),
    ("satış rakamlarımız", "satis_tutari"),
    ("satıştan gelen para", "satis_tutari"),
    # Alım ailesi
    ("alım", "alim_tutari"),
    ("alış", "alim_tutari"),
    ("satın alma", "alim_tutari"),
    ("tedarik", "alim_tutari"),
    ("alımlarımız", "alim_tutari"),
    ("alım maliyeti", "alim_tutari"),
    ("mal alımı", "alim_tutari"),
    ("hammadde alımı", "alim_tutari"),
    ("hurda alımı", "alim_tutari"),
    # Miktar ailesi
    ("satış miktarı", "satis_miktari"),
    ("satılan miktar", "satis_miktari"),
    ("sevk edilen", "satis_miktari"),
    ("kaç kilo satıldı", "satis_miktari"),
    ("kaç ton sattık", "satis_miktari"),
    ("alım miktarı", "alim_miktari"),
    ("alınan miktar", "alim_miktari"),
    ("kaç kilo aldık", "alim_miktari"),
    ("toplanan miktar", "alim_miktari"),
    # Cari ailesi
    ("bakiye", "bakiye"),
    ("net bakiye", "bakiye"),
    ("cari bakiye", "bakiye"),
    ("hesap bakiyesi", "bakiye"),
    ("borç", "toplam_borc"),
    ("borçlar", "toplam_borc"),
    ("borç toplamı", "toplam_borc"),
    ("alacak", "toplam_alacak"),
    ("tahsilat", "toplam_alacak"),
    ("alacak toplamı", "toplam_alacak"),
    ("hareket sayısı", "hareket_sayisi"),
    ("kaç hareket", "hareket_sayisi"),
    # Fatura
    ("fatura sayısı", "satis_fatura_sayisi"),
    ("kaç fatura", "satis_fatura_sayisi"),
    ("fatura adedi", "satis_fatura_sayisi"),
    # Boyahane
    ("fire oranı", "fire_orani_yuzde"),
    ("fire yüzdesi", "fire_orani_yuzde"),
    ("fire durumu", "fire_orani_yuzde"),
    ("zayiat oranı", "fire_orani_yuzde"),
    ("toplam fire", "toplam_fire_kg"),
    ("fire miktarı", "toplam_fire_kg"),
    ("ağırlık", "toplam_agirlik_kg"),
    ("işlenen miktar", "toplam_agirlik_kg"),
    ("kar", "kar"),
    ("kâr", "kar"),
    ("kazanç", "kar"),
    ("kar marjı", "kar_marji_yuzde"),
    ("karlılık", "kar_marji_yuzde"),
    ("marj", "kar_marji_yuzde"),
    ("renk sapması", "ort_renk_sapmasi"),
    ("parti sayısı", "parti_sayisi"),
    # OEE
    ("OEE", "ort_oee"),
    ("makine verimi", "ort_oee"),
    ("verim", "ort_oee"),
    ("randıman", "ort_oee"),
    ("kullanılabilirlik", "ort_kullanilabilirlik"),
    ("performans", "ort_performans"),
    ("duruş süresi", "toplam_durus_dakika"),
    ("arıza süresi", "toplam_durus_dakika"),
    ("üretim miktarı", "toplam_uretim_kg"),
    # Sürdürülebilirlik
    ("su tüketimi", "toplam_su_lt"),
    ("su yoğunluğu", "su_yogunlugu_lt_kg"),
    ("enerji tüketimi", "toplam_enerji_kwh"),
    ("enerji yoğunluğu", "enerji_yogunlugu_kwh_kg"),
    ("kimyasal maliyeti", "kimyasal_yogunlugu_tl_kg"),
    # Yaşlandırma
    ("vadesi geçen alacaklar", "vadesi_gecen"),
    ("gecikmiş alacaklar", "vadesi_gecen"),
    ("açık bakiye", "net_bakiye"),
    # KDV
    ("kdv tutarı", "satis_kdv"),
    ("satış kdv", "satis_kdv"),
]

PERIODS_FULL = [
    # Basit
    "bu yıl", "geçen yıl", "bu ay", "geçen ay", "bu hafta", "geçen hafta",
    "bugün", "dün", "son 7 gün", "son 30 gün", "son 90 gün", "son 365 gün",
    "son 3 ay", "son 6 ay", "son 12 ay",
    # Ay adları
    "ocak ayında", "şubat ayında", "mart ayında", "nisan ayında", "mayıs ayında",
    "haziran ayında", "temmuz ayında", "ağustos ayında", "eylül ayında",
    "ekim ayında", "kasım ayında", "aralık ayında",
    # Yıllar
    "2022 yılında", "2023 yılında", "2024 yılında", "2025 yılında",
    # Çeyrekler
    "1. çeyrekte", "2. çeyrekte", "3. çeyrekte", "4. çeyrekte",
    "ilk çeyrekte", "son çeyrekte",
    # Bileşik
    "yılın ilk yarısında", "yılın ikinci yarısında",
    "ocak-mart döneminde", "nisan-haziran döneminde",
    "temmuz-eylül döneminde", "ekim-aralık döneminde",
]

PERIOD_UNITS = ["ay", "hafta", "yıl", "çeyrek"]

USER_TYPES_FULL = [
    "patron", "muhasebeci", "satis_muduru", "uretim_muduru",
    "depo_sorumlusu", "finans_uzmani", "veri_analisti",
    "satin_alma", "saha_personeli",
]

# Boyut eşleme (kırılım için)
DIMS_BY_CUBE = {
    "ticaret_mikro": ["stok bazında", "cari bazında", "evrak tipine göre"],
    "ticaret_netsis": ["müşteriye göre", "şubeye göre", "haftanın günlerine göre"],
    "ticaret_logo": ["müşteriye göre", "fatura numarasına göre"],
    "cari_all": ["cari koduna göre", "müşteriye göre", "evrak tipine göre", "şubeye göre"],
    "parti": ["makineye göre", "kumaş cinsine göre", "renge göre", "aşamaya göre", "müşteriye göre"],
    "oee": ["makineye göre", "vardiyaya göre", "personele göre", "cinsiyete göre"],
    "surdurulebilirlik": ["makineye göre", "kumaş cinsine göre", "aşamaya göre"],
    "mal_netsis": ["ürün bazında", "müşteriye göre", "depoya göre"],
}


def gen_phrasing_matrix(seen_norms: set) -> list[dict]:
    """En büyük batch: ölçü × dönem × soru çerçevesi × şirket."""
    records = []
    # Belirli şirket-ölçü eşleşmeleri (gerçek cube kapsamı)
    company_measure_sets = {
        "boyahane": [w for w, m in MEASURE_WORDS_FULL],
        "atiksan": [w for w, m in MEASURE_WORDS_FULL
                    if m in ("satis_tutari", "alim_tutari", "satis_miktari", "alim_miktari",
                              "bakiye", "toplam_borc", "toplam_alacak", "hareket_sayisi",
                              "satis_fatura_sayisi", "vadesi_gecen", "net_bakiye")],
        "gulteks": [w for w, m in MEASURE_WORDS_FULL
                    if m in ("satis_tutari", "brut_satis", "alim_tutari", "satis_fatura_sayisi",
                              "satis_miktari", "alim_miktari", "bakiye", "toplam_borc",
                              "toplam_alacak", "hareket_sayisi")],
        "gitas": [w for w, m in MEASURE_WORDS_FULL
                  if m in ("satis_tutari", "alim_tutari", "satis_kdv", "satis_fatura_sayisi",
                            "satis_miktari", "alim_miktari", "bakiye", "toplam_borc",
                            "toplam_alacak", "hareket_sayisi", "vadesi_gecen", "net_bakiye")],
    }
    company_info = {
        "boyahane": ("tekstil-boyahane", "Mikro V16"),
        "atiksan": ("geri-donusum", "Mikro V16"),
        "gulteks": ("kumas-ticareti", "Logo Start 3"),
        "gitas": ("tarim-ticareti", "Netsis"),
    }

    for company, measures in company_measure_sets.items():
        sector, erp = company_info[company]
        for measure_word in measures:
            for period in PERIODS_FULL[:20]:  # ilk 20 dönem (kombinasyon patlamasını önle)
                for frame in QUESTION_FRAMES[:8]:  # ilk 8 çerçeve
                    for period_unit in PERIOD_UNITS[:2]:
                        try:
                            q = frame.format(
                                measure=measure_word,
                                period=period,
                                period_unit=period_unit,
                            )
                        except KeyError:
                            q = frame.replace("{period}", period).replace(
                                "{measure}", measure_word).replace(
                                "{period_unit}", period_unit)

                        norm = normalize(f"{company}:{q}")
                        if norm not in seen_norms and len(norm) > 6:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": "patron", "_diff": 1,
                                "_turns": [q], "_tags": ["phrasing-matrix"],
                            })
    return records


def gen_kiririm_matrix(seen_norms: set) -> list[dict]:
    """Kırılım matrisi: ölçü × dönem × boyut × şirket × zorluk 2."""
    records = []
    MEASURES_CORE = [
        "satış", "ciro", "alım", "bakiye", "fire oranı", "verim", "hareket sayısı",
    ]
    DIMS_CORE = [
        "müşteri bazında", "ürün bazında", "şube bazında", "makine bazında",
        "vardiya bazında", "aşama bazında", "kumaş cinsine göre",
    ]
    PERIODS_CORE = ["bu yıl", "geçen ay", "bu ay", "son 3 ay", "2024", "2025"]
    BREAKDOWN_TMPL = [
        "{period} {measure} {dim}",
        "{dim} {period} {measure}",
        "{measure} {period} {dim} kırılımında",
        "{dim} itibarıyla {period} {measure}",
    ]

    for company, sector, erp in COMPANIES_ALL:
        for m in MEASURES_CORE:
            for dim in DIMS_CORE:
                for period in PERIODS_CORE:
                    for tmpl in BREAKDOWN_TMPL:
                        q = tmpl.format(measure=m, dim=dim, period=period)
                        norm = normalize(f"{company}:kiririm:{q}")
                        if norm not in seen_norms and len(norm) > 8:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": "veri_analisti", "_diff": 2,
                                "_turns": [q], "_tags": ["kiririm-matrix"],
                            })
    return records


def gen_user_x_measure_x_period(seen_norms: set) -> list[dict]:
    """Kullanıcı × ölçü × dönem tam süpürme."""
    records = []
    # Her kullanıcı tipinin 5 temel ölçüsü
    user_measure_map = {
        "patron": ["satış", "ciro", "kar", "fire oranı", "bakiye"],
        "muhasebeci": ["bakiye", "borç", "alacak", "hareket sayısı", "fatura sayısı"],
        "satis_muduru": ["satış", "ciro", "fatura sayısı", "satış miktarı", "müşteri bakiyesi"],
        "uretim_muduru": ["fire oranı", "verim", "OEE", "duruş süresi", "üretim miktarı"],
        "depo_sorumlusu": ["stok miktarı", "giriş miktarı", "çıkış miktarı", "fire miktarı", "hareket sayısı"],
        "finans_uzmani": ["bakiye", "vadesi geçen", "borç", "alacak", "nakit akışı"],
        "veri_analisti": ["satış", "alım", "bakiye", "fire oranı", "verim"],
        "satin_alma": ["alım", "tedarik", "alım miktarı", "alım maliyeti", "tedarikçi borcu"],
        "saha_personeli": ["bugünkü satış", "bugünkü üretim", "bu vardiya", "bugün hareket", "stok durumu"],
    }

    # Kullanıcıya özgü soru kalıpları
    user_frames = {
        "patron": ["{period} {measure}", "genel {measure} {period}", "özetle {period} {measure}"],
        "muhasebeci": ["{period} {measure} ne durumda", "{period} {measure} raporu", "{measure} listesi {period}"],
        "satis_muduru": ["{period} {measure} hedef tuttu mu", "satış {period} {measure}", "{measure} {period} sırala"],
        "uretim_muduru": ["{period} {measure} nasıl", "üretimde {period} {measure}", "{measure} {period} makine bazında"],
        "depo_sorumlusu": ["{period} depo {measure}", "ambarda {period} {measure}", "{measure} durumu {period}"],
        "finans_uzmani": ["{period} {measure} analizi", "finansal {period} {measure}", "{measure} riski {period}"],
        "veri_analisti": ["{period} {measure} trend", "{measure} {period} kırılım", "{period} {measure} yoy"],
        "satin_alma": ["{period} {measure} bütçe", "tedarik {period} {measure}", "{measure} en uygun {period}"],
        "saha_personeli": ["{period} {measure}", "{measure} nerde", "{measure} var mı {period}"],
    }

    PERIODS_SHORT = ["bu yıl", "geçen ay", "bu ay", "son 3 ay", "bu hafta"]

    for company, sector, erp in COMPANIES_ALL:
        for user_type, measures in user_measure_map.items():
            frames = user_frames.get(user_type, ["{period} {measure}"])
            for m in measures:
                for period in PERIODS_SHORT:
                    for frame in frames:
                        try:
                            q = frame.format(measure=m, period=period)
                        except KeyError:
                            q = f"{period} {m}"
                        norm = normalize(f"{company}:{user_type}:{q}")
                        if norm not in seen_norms and len(norm) > 5:
                            seen_norms.add(norm)
                            records.append({
                                "_company": company, "_sector": sector, "_erp": erp,
                                "_user": user_type, "_diff": 1,
                                "_turns": [q], "_tags": ["user-measure-period"],
                            })
    return records


def gen_comparison_templates(seen_norms: set) -> list[dict]:
    """Karşılaştırma sorguları — dönem × şirket × ölçü."""
    records = []
    COMPARISON_FRAMES = [
        "{m} {p1} ile {p2} kıyasla",
        "{p1} ve {p2} {m} farkı ne",
        "{m} {p1}'de {p2}'ye göre değişim",
        "{p1} vs {p2} {m} büyümesi",
        "{m} {p2}'ye göre {p1}'de kaç yüzde arttı",
        "{p1} {m} hedefini {p2}'ye kıyasla göster",
        "{m}: {p1} neydi, {p2} ne",
    ]
    PERIOD_PAIRS = [
        ("bu yıl", "geçen yıl"),
        ("bu ay", "geçen ay"),
        ("bu çeyrek", "geçen çeyrek"),
        ("2025", "2024"),
        ("2024", "2023"),
        ("ocak", "şubat"),
        ("mayıs", "haziran"),
        ("bu hafta", "geçen hafta"),
    ]
    MEASURES_COMP = [
        "satış", "ciro", "alım", "bakiye", "fire oranı", "verim",
        "kar marjı", "fatura sayısı", "tahsilat", "su tüketimi", "enerji",
    ]

    for company, sector, erp in COMPANIES_ALL:
        for m in MEASURES_COMP:
            for p1, p2 in PERIOD_PAIRS:
                for frame in COMPARISON_FRAMES:
                    q = frame.format(m=m, p1=p1, p2=p2)
                    norm = normalize(f"{company}:comp:{q}")
                    if norm not in seen_norms and len(norm) > 8:
                        seen_norms.add(norm)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 4,
                            "_turns": [q], "_tags": ["comparison", "period-pair"],
                        })
    return records


def gen_topn_extended(seen_norms: set) -> list[dict]:
    """Genişletilmiş Top-N sorguları."""
    records = []
    TOPN_FRAMES = [
        "en yüksek {n} {dim} {m} bazında {period}",
        "en düşük {n} {dim} {m} bazında {period}",
        "{period} {m} itibarıyla ilk {n} {dim}",
        "{period} en fazla {m} yapan {n} {dim}",
        "{period} en az {m} yapan {n} {dim}",
        "{period} {m} rankinginde ilk {n}",
        "top {n} {dim} {m} açısından {period}",
        "{period} {m} en kötü {n} {dim}",
        "en çok büyüyen {n} {dim} {m}'da {period}",
        "en hızlı düşen {n} {dim} {m}'de {period}",
    ]
    NS = [3, 5, 10, 20]
    DIMS_TOPN = ["müşteri", "ürün", "şube", "makine", "tedarikçi", "stok", "kumaş"]
    MEASURES_TOPN = ["satış", "ciro", "alım", "fire oranı", "verim", "fatura sayısı"]
    PERIODS_TOPN = ["bu yıl", "geçen ay", "son 3 ay", "2024"]

    for company, sector, erp in COMPANIES_ALL:
        for n in NS:
            for dim in DIMS_TOPN[:4]:
                for m in MEASURES_TOPN[:4]:
                    for period in PERIODS_TOPN[:3]:
                        for frame in TOPN_FRAMES[:5]:
                            q = frame.format(n=n, dim=dim, m=m, period=period)
                            norm = normalize(f"{company}:topn:{q}")
                            if norm not in seen_norms and len(norm) > 10:
                                seen_norms.add(norm)
                                records.append({
                                    "_company": company, "_sector": sector, "_erp": erp,
                                    "_user": "satis_muduru", "_diff": 3,
                                    "_turns": [q], "_tags": [f"top{n}", "topn-extended"],
                                })
    return records


def run_ext3():
    print(f"[generate_ext3.py] Mevcut queries.jsonl yükleniyor: {QUERIES_PATH}")
    seen_norms = load_existing(QUERIES_PATH)
    next_id = get_next_id(QUERIES_PATH)
    start_total = next_id - 1
    print(f"  Mevcut: {start_total} sorgu | sonraki ID: {next_id}")

    all_new: list[dict] = []

    steps = [
        ("EXT3-1: Büyük phrasing matrisi", gen_phrasing_matrix),
        ("EXT3-2: Kırılım matrisi", gen_kiririm_matrix),
        ("EXT3-3: Kullanıcı × ölçü × dönem sweep", gen_user_x_measure_x_period),
        ("EXT3-4: Karşılaştırma şablonları", gen_comparison_templates),
        ("EXT3-5: Top-N genişletme", gen_topn_extended),
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

    print(f"\nTOPLAM ÜRETİLEN: {total_now} (bu ext3 +{len(all_new)}) | "
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
        f"- Forecast: {tag_count.get('forecast', 0)} sorgu",
        f"- Hata senaryoları: {tag_count.get('error-scenario', 0)} sorgu",
        f"",
        f"## Bir Sonraki Koşu",
        f"- Sesli sorgu simülasyonu (konuşma dili bozuk cümleler)",
        f"- Gerçek forum soruları adaptasyonu",
        f"- Daha kapsamlı atiksan kırılım matrisi",
        f"- Hedef: 500.000+ tekrarsız sorgu",
        f"",
        f"## Kaynaklar",
        f"- demo/packs — cube metadata",
        f"- lab/nl_corpus.py — REAL_PHRASINGS",
        f"- app/archetypes.py — ölçü arketipleri",
    ]
    STATS_PATH.write_text("\n".join(stats_lines), encoding="utf-8")
    print(f"[stats.md] Güncellendi.")
    print(f"[queries.jsonl] Yol: {QUERIES_PATH}")


if __name__ == "__main__":
    run_ext3()
