#!/usr/bin/env python3
"""
Round 4 — Çok-adımlı zincir fabrikası + 300k hedef

Odak:
1. Çok-adımlı zincirlerin sistematik kombinatoryal üretimi
2. Daha fazla zorluk 5 zinciri
3. Sesli/konuşma dili varyasyonları
4. Hızlı Patron Dashboard sorgu zincirleri
5. Muhasebe iş akışı zincirleri
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


def load_existing_first_turns(path: Path) -> set[str]:
    """Sadece ilk turları yükle (zincirlerin tekilliği için)."""
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
                turns = rec.get("turns", [])
                if turns:
                    # İlk tur + n_turns kombinasyonu ile tekilleştir
                    key = normalize(turns[0]) + f"::n{len(turns)}"
                    seen.add(key)
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
# 1. Sistematik 3-adım zincirleri (büyük batch)
# ──────────────────────────────────────────────────────────────────────────────

OPENING_QUESTIONS = {
    "boyahane": [
        "bu yıl satış ciromuzu göster",
        "fire oranımız ne kadar",
        "OEE verimiz nasıl",
        "su tüketimimiz bu yıl",
        "enerji tüketimimiz",
        "kar marjımız bu yıl",
        "müşteri bazında satışlar",
        "makine bazında fire",
        "parti sayımız bu ay",
        "geçen ay renk sapması",
    ],
    "atiksan": [
        "bu ay hurda alımımız kaç ton",
        "satışlarımız bu ay ne kadar",
        "bakiyemiz ne",
        "vadesi geçen alacaklar var mı",
        "en çok alınan malzeme",
        "tedarikçi borçlarımız",
        "depo durumu",
        "alım maliyeti bu ay",
        "bu ay kaç hareket oldu",
        "geçen ay alım miktarı",
    ],
    "gulteks": [
        "bu yıl satışlarım ne kadar",
        "kumaş bazında gelir",
        "fatura sayısı bu ay",
        "müşteri bakiyeleri",
        "en çok satan kumaş",
        "alım maliyeti bu yıl",
        "brüt ve net satış farkı",
        "cari hesap durumu",
        "bu ay kaç fatura kestik",
        "geçen yıla göre büyüme",
    ],
    "gitas": [
        "bu ay satış ciromuz",
        "müşteri bazında satışlar",
        "vadesi geçen alacaklar",
        "şube bazında gelir",
        "alım maliyeti bu yıl",
        "fatura adedi bu ay",
        "borç durumu",
        "tahsilat bu ay ne kadar",
        "şube karşılaştırması",
        "en büyük müşteri",
    ],
}

STEP2_OPTIONS = [
    "aylık kır",
    "müşteri bazında göster",
    "geçen yılla kıyasla",
    "haftalık göster",
    "şube bazında kır",
    "sırala yüksekten düşüğe",
    "en yüksek 5'ini göster",
    "en düşük 3'ünü göster",
    "grafik olarak göster",
    "trend analizi yap",
    "çeyreklik göster",
    "ürün bazında kır",
]

STEP3_OPTIONS = [
    "bunu da geçen yılla kıyasla",
    "ilk 5'e odaklan",
    "tablo olarak düzenle",
    "büyüme yüzdesi hesapla",
    "özet ver",
    "risk var mı",
    "aksiyon öner",
    "dikkat çekilmesi gereken nokta var mı",
    "en önemli bulgu ne",
    "bütçeyle kıyasla",
]


def gen_3step_chains(seen_first_turns: set) -> list[dict]:
    records = []
    for company, sector, erp in COMPANIES_ALL:
        c_name = company.split("-")[0] if "-" in company else company
        openings = OPENING_QUESTIONS.get(c_name, OPENING_QUESTIONS["boyahane"])

        for q1 in openings:
            for q2 in STEP2_OPTIONS:
                for q3 in STEP3_OPTIONS:
                    key = normalize(q1) + f"::n3::{normalize(q2)}"
                    if key not in seen_first_turns:
                        seen_first_turns.add(key)
                        records.append({
                            "_company": company, "_sector": sector, "_erp": erp,
                            "_user": "veri_analisti", "_diff": 4,
                            "_turns": [q1, q2, q3],
                            "_tags": ["3-turn", "systematic-chain"],
                        })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 2. Patron dashboard zincirleri (kısa, 2-4 adım)
# ──────────────────────────────────────────────────────────────────────────────

PATRON_2STEP = [
    ["bu ay satışlar ne kadar", "geçen aya göre nasıl"],
    ["ciro bu yıl", "hedef tuttu mu"],
    ["en büyük müşterimiz kim", "bu müşterinin bakiyesi ne"],
    ["fire oranımız bu ay", "makine bazında göster"],
    ["OEE bu hafta", "geçen hafta ile kıyasla"],
    ["tahsilat bu ay", "gecikmiş var mı"],
    ["alım maliyeti bu ay", "geçen aya göre artmış mı"],
    ["stok durumu", "kritik seviyede olan var mı"],
    ["borcumuz ne kadar", "ödeme planı"],
    ["genel performans özeti", "en önemli risk ne"],
]

PATRON_3STEP = [
    ["bu ay satışlar", "müşteri bazında kır", "en büyük 3'ü göster"],
    ["fire oranı", "aşama bazında göster", "en kötü aşama hangisi"],
    ["tahsilat", "vadesi geçen listele", "toplam tutar ne"],
    ["alım maliyeti", "aylık trend", "en pahalı ay hangisi"],
    ["OEE", "makine bazında", "en kötü makinede ne olmuş"],
    ["bakiye durumu", "borçlu olan müşteriler", "en büyük borçlu kim"],
    ["satış geçen ay", "aylık karşılaştırma son 6 ay", "trend ne yönde"],
    ["kar marjı bu yıl", "aşamaya göre kır", "en düşük margin nerede"],
    ["su tüketimi", "makine bazında", "hedefin üstünde olan var mı"],
    ["enerji yoğunluğu", "aylık trend", "geçen yıla göre iyileştik mi"],
]

PATRON_4STEP = [
    ["satışlar bu yıl", "müşteri bazında kır", "en büyük 5", "bakiyeleri göster"],
    ["OEE bu ay", "geçen aya göre", "en kötü makine", "sebep ne olabilir"],
    ["fire oranı", "aylık trend", "en yüksek ay", "o ayda ne oldu"],
    ["alacaklar", "vadesi geçenler", "yaş kovası", "risk tutarı toplam"],
    ["gelirimiz bu yıl", "giderimiz bu yıl", "kar hesabı", "hedefte miyiz"],
    ["satış miktarı", "ürün bazında", "en az satan 3", "neden az satılmış"],
    ["makine verimleri", "vardiya bazında", "en kötü vardiya", "aksiyon öner"],
    ["cari hesaplar", "borçlu olanlar", "en büyük borç", "ödeme tarihi ne"],
    ["alım bu ay", "tedarikçi bazında", "en fazla alınan 3", "fiyat kıyasla"],
    ["üretim miktarı", "haftalık trend", "en düşük hafta", "sebep araştır"],
]


def gen_patron_chains(seen_first_turns: set) -> list[dict]:
    records = []
    for company, sector, erp in COMPANIES_ALL:
        for chain_2, chain_3, chain_4 in zip(PATRON_2STEP, PATRON_3STEP, PATRON_4STEP):
            for chain, n_diff in [(chain_2, 3), (chain_3, 4), (chain_4, 5)]:
                key = normalize(chain[0]) + f"::patron::{company}::n{len(chain)}"
                if key not in seen_first_turns:
                    seen_first_turns.add(key)
                    records.append({
                        "_company": company, "_sector": sector, "_erp": erp,
                        "_user": "patron", "_diff": n_diff,
                        "_turns": chain,
                        "_tags": [f"{len(chain)}-turn", "patron-dashboard"],
                    })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 3. Muhasebe iş akışı zincirleri
# ──────────────────────────────────────────────────────────────────────────────

MUHASEBE_CHAINS = [
    {
        "turns": ["bu ay alacak toplamı ne", "vadesi geçen alacaklar", "vade aralıklarına göre dağılım",
                  "hangi müşteri en uzun süredir ödeme yapmadı", "bu müşterinin satış geçmişi"],
        "user": "muhasebeci", "diff": 4,
    },
    {
        "turns": ["bu ay borç toplamı", "tedarikçi bazında borç", "bu hafta ödenecekler",
                  "nakit planı yeterli mi", "hangi tedarikçiye önce ödeme yapılmalı"],
        "user": "muhasebeci", "diff": 4,
    },
    {
        "turns": ["aylık hareket sayısı", "geçen aya göre artmış mı", "en fazla hareket hangi hesapta",
                  "bu hesabın detayı", "anormal hareket var mı"],
        "user": "muhasebeci", "diff": 4,
    },
    {
        "turns": ["dönem sonu bakiyeler", "borç bakiyesi toplamı", "alacak bakiyesi toplamı",
                  "net pozisyon ne", "geçen döneme kıyasla"],
        "user": "muhasebeci", "diff": 3,
    },
    {
        "turns": ["fatura listesi bu ay", "iptal edilen fatura var mı", "kdv toplamı",
                  "brüt vs net fark", "vergi matrahı ne kadar"],
        "user": "muhasebeci", "diff": 4,
    },
    {
        "turns": ["tahsilat bu ay ne kadar", "hangi müşteri ödedi", "hangi müşteri ödemedi",
                  "gecikmiş ödeme tutarı", "hukuki takip gerektirecek var mı",
                  "aksiyon planı öner"],
        "user": "muhasebeci", "diff": 5,
    },
]


def gen_muhasebe_chains(seen_first_turns: set) -> list[dict]:
    records = []
    for company, sector, erp in COMPANIES_ALL:
        for ch in MUHASEBE_CHAINS:
            key = normalize(ch["turns"][0]) + f"::muhasebe::{company}::n{len(ch['turns'])}"
            if key not in seen_first_turns:
                seen_first_turns.add(key)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": ch["user"], "_diff": ch["diff"],
                    "_turns": ch["turns"],
                    "_tags": [f"{len(ch['turns'])}-turn", "muhasebe-workflow"],
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 4. Satış müdürü analiz zincirleri
# ──────────────────────────────────────────────────────────────────────────────

SATIS_CHAINS = [
    {
        "turns": ["bu ay satışlarım", "hedef neydi", "kaç yüzde gerçekleştirdim",
                  "en iyi müşterim kim", "bu müşterinin büyüme trendi"],
        "user": "satis_muduru", "diff": 4,
    },
    {
        "turns": ["en çok satan ürünlerim", "aylık trend", "geçen yıl ile kıyasla",
                  "bu ürünlerde müşteri dağılımı", "en karlı müşteri-ürün kombinasyonu"],
        "user": "satis_muduru", "diff": 4,
    },
    {
        "turns": ["şube bazında satışlar", "en iyi şube hangisi", "bu şubenin müşteri listesi",
                  "o müşterilerin bakiye durumu", "tahsilat gecikiyor mu"],
        "user": "satis_muduru", "diff": 4,
    },
    {
        "turns": ["yeni müşteri sayısı bu yıl", "kaybettiğimiz müşteri var mı",
                  "müşteri elde tutma oranı", "en büyük müşteri kaybı neden",
                  "geri kazanma planı öner"],
        "user": "satis_muduru", "diff": 5,
    },
    {
        "turns": ["satış faturası sayısı bu ay", "ortalama fatura tutarı", "en büyük fatura",
                  "bu fatura hangi müşteriye", "bu müşterinin diğer faturaları"],
        "user": "satis_muduru", "diff": 3,
    },
    {
        "turns": ["bu haftaki satışlar", "geçen haftayla kıyasla", "günlük dağılım",
                  "en iyi gün hangisi", "bu günün müşteri kırılımı",
                  "hedefi yakaladık mı", "önümüzdeki hafta için öneri"],
        "user": "satis_muduru", "diff": 5,
    },
]


def gen_satis_chains(seen_first_turns: set) -> list[dict]:
    records = []
    for company, sector, erp in COMPANIES_ALL:
        for ch in SATIS_CHAINS:
            key = normalize(ch["turns"][0]) + f"::satis::{company}::n{len(ch['turns'])}"
            if key not in seen_first_turns:
                seen_first_turns.add(key)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": ch["user"], "_diff": ch["diff"],
                    "_turns": ch["turns"],
                    "_tags": [f"{len(ch['turns'])}-turn", "satis-analysis"],
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 5. Üretim/operasyon zincirleri (boyahane odaklı)
# ──────────────────────────────────────────────────────────────────────────────

URETIM_CHAINS = [
    {
        "company": "boyahane",
        "turns": ["bugünkü vardiya üretimi", "hedef neydi", "fire oranı ne kadar",
                  "hangi makinede sorun var", "acil müdahale gerekiyor mu"],
        "user": "uretim_muduru", "diff": 4,
    },
    {
        "company": "boyahane",
        "turns": ["bu hafta OEE ortalaması", "makine bazında göster", "en düşük OEE hangisi",
                  "bu makinenin duruş nedenleri", "planlı bakım mı yoksa arıza mı",
                  "geçen ayla kıyasla", "iyileştirme aksiyonu öner"],
        "user": "uretim_muduru", "diff": 5,
    },
    {
        "company": "boyahane",
        "turns": ["renk sapması bu ay", "aşama bazında kır", "en yüksek sapma nerede",
                  "müşteri şikayeti var mı", "yeniden işleme maliyeti ne kadar"],
        "user": "uretim_muduru", "diff": 4,
    },
    {
        "company": "boyahane",
        "turns": ["su tüketimi bu ay", "hedef vs gerçek", "en fazla tüketen makine",
                  "geçen aya göre artmış mı", "ZDHC hedefine uyuyoruz mu",
                  "azaltma önlemi öner"],
        "user": "uretim_muduru", "diff": 5,
    },
    {
        "company": "boyahane",
        "turns": ["bu ay işlenen toplam kg", "makine kapasitesi doluluk oranı",
                  "darboğaz nerede", "vardiya planı optimize edilebilir mi",
                  "gelecek hafta kapasite tahmini"],
        "user": "uretim_muduru", "diff": 5,
    },
]


def gen_uretim_chains(seen_first_turns: set) -> list[dict]:
    records = []
    company_info = {"boyahane": ("tekstil-boyahane", "Mikro V16")}
    for ch in URETIM_CHAINS:
        company = ch["company"]
        sector, erp = company_info.get(company, ("tekstil-boyahane", "Mikro V16"))
        key = normalize(ch["turns"][0]) + f"::uretim::{company}::n{len(ch['turns'])}"
        if key not in seen_first_turns:
            seen_first_turns.add(key)
            records.append({
                "_company": company, "_sector": sector, "_erp": erp,
                "_user": ch["user"], "_diff": ch["diff"],
                "_turns": ch["turns"],
                "_tags": [f"{len(ch['turns'])}-turn", "uretim-ops", "boyahane"],
            })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# 6. Sesli/konuşma dili varyasyonları (bozuk cümleler, çekim hataları)
# ──────────────────────────────────────────────────────────────────────────────

CONVERSATIONAL_QUESTIONS = [
    # Konuşma dili — kısa ve belirsiz
    ("satış nerede", 1),
    ("ciro ne kadar ya", 1),
    ("patron ne diyecek sayılar için", 1),
    ("rakamlar nasıl abi", 1),
    ("geçen ay mı bu ay mı daha iyi", 2),
    ("fire çok mu bu hafta", 1),
    ("makine mi duruyor", 1),
    ("borç ne durumda hocam", 1),
    ("alacak topladık mı", 1),
    ("kasada ne var", 1),
    # Soru ekiyle biten
    ("satışlar iyiye gidiyor mu", 2),
    ("müşteri ödedi mi", 2),
    ("stok yeterli mi", 2),
    ("bütçe tuttu mu bu ay", 2),
    ("hedef yakalandı mı", 2),
    ("enerji fazla mı harcıyoruz", 2),
    ("vade sorunu var mı", 2),
    ("fire azaldı mı son haftalarda", 2),
    # Sohbet tarzı
    ("bi bak satışlara bu ay nasıl", 1),
    ("hızlıca ciroyu söyle", 1),
    ("geçen ay ile bu ayı karşılaştır bi de", 2),
    ("en çok kim aldı bizden", 2),
    ("en büyük borcumuz kime", 2),
    ("para topladık mı", 1),
    ("üretim gitti mi bu hafta", 1),
    # Bağlamlı (önceki konuşmayı varsayar)
    ("peki onu da göster", 2),
    ("onun da aylığını yap", 2),
    ("şimdi müşteri bazında kır bunu", 2),
    ("bir de grafiğini çiz", 2),
    ("geçen yılki hali neydi", 2),
    ("en büyük 5'ini listele", 2),
    ("kalanları da göster", 2),
    ("sıralasana büyükten küçüğe", 2),
]


def gen_conversational(seen_norms: set, path: Path) -> list[dict]:
    """seen_norms = normalize(turn) seti."""
    records = []
    for company, sector, erp in COMPANIES_ALL:
        for q, diff in CONVERSATIONAL_QUESTIONS:
            norm = normalize(f"{company}:conv:{q}")
            if norm not in seen_norms:
                seen_norms.add(norm)
                records.append({
                    "_company": company, "_sector": sector, "_erp": erp,
                    "_user": "saha_personeli", "_diff": diff,
                    "_turns": [q], "_tags": ["conversational", "spoken-lang"],
                })
    return records


# ──────────────────────────────────────────────────────────────────────────────
# ANA FONKSİYON
# ──────────────────────────────────────────────────────────────────────────────

def run_ext4():
    print(f"[generate_ext4.py] Başlıyor...")
    # Multi-turn için özel dedup (ilk tur + n_turns kombinasyonu)
    seen_first_turns = load_existing_first_turns(QUERIES_PATH)
    next_id = get_next_id(QUERIES_PATH)
    start_total = next_id - 1
    print(f"  Mevcut: {start_total} sorgu | sonraki ID: {next_id}")
    print(f"  Mevcut multi-turn anahtarlar: {len(seen_first_turns)}")

    # Tek-adım soruları için normal seen_norms da lazım
    seen_single = set()
    with open(QUERIES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                turns = rec.get("turns", [])
                if len(turns) == 1:
                    seen_single.add(normalize(turns[0]))
            except Exception:
                pass
    print(f"  Mevcut tekil sorgu hash: {len(seen_single)}")

    all_new: list[dict] = []

    steps = [
        ("EXT4-1: 3-adım sistematik zincirler", lambda: gen_3step_chains(seen_first_turns)),
        ("EXT4-2: Patron dashboard zincirleri", lambda: gen_patron_chains(seen_first_turns)),
        ("EXT4-3: Muhasebe iş akışı zincirleri", lambda: gen_muhasebe_chains(seen_first_turns)),
        ("EXT4-4: Satış analiz zincirleri", lambda: gen_satis_chains(seen_first_turns)),
        ("EXT4-5: Üretim/operasyon zincirleri", lambda: gen_uretim_chains(seen_first_turns)),
        ("EXT4-6: Konuşma dili sorular", lambda: gen_conversational(seen_single, QUERIES_PATH)),
    ]

    for label, fn in steps:
        print(f"[{label}]")
        batch = fn()
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
    n_turns_dist: Counter = Counter()
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
                n_turns_dist[rec["n_turns"]] += 1
                for t in rec.get("tags", []):
                    tag_count[t] += 1
            except Exception:
                pass

    print(f"\nTOPLAM ÜRETİLEN: {total_now} (bu ext4 +{len(all_new)})")
    print(f"zorluk kırılımı: {dict(sorted(diff_count.items()))}")
    print(f"n_turns dağılımı: {dict(sorted(n_turns_dist.items()))}")
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

    stats_lines += [f"", f"## n_turns Dağılımı"]
    for n in sorted(n_turns_dist.keys()):
        stats_lines.append(f"- {n} adım: {n_turns_dist[n]}")

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
        f"- Forecast/what-if: {tag_count.get('forecast', 0) + tag_count.get('what-if', 0)} sorgu",
        f"- Hata senaryoları: {tag_count.get('error-scenario', 0)} sorgu",
        f"- Konuşma dili: {tag_count.get('conversational', 0)} sorgu",
        f"- Çok-adımlı (3+ tur): {sum(v for k, v in n_turns_dist.items() if k >= 3)} kayıt",
        f"",
        f"## Bir Sonraki Koşu",
        f"- Daha fazla atiksan çok-adımlı (geri-dönüşüm operasyonu)",
        f"- Türkçe NLP forum ve muhasebe forum sorularından gerçek ifadeler",
        f"- Farklı yazım varyantları (q→ğ, ü→u vb. mobil klavye hataları)",
        f"- Hedef: 400.000+ tekrarsız sorgu",
        f"",
        f"## Kaynaklar",
        f"- demo/packs — cube metadata",
        f"- lab/nl_corpus.py — REAL_PHRASINGS",
        f"- app/archetypes.py — ölçü arketipleri",
    ]

    STATS_PATH.write_text("\n".join(stats_lines), encoding="utf-8")
    print(f"[stats.md] Güncellendi.")
    print(f"[queries.jsonl] Yol: {QUERIES_PATH}")
    sz = QUERIES_PATH.stat().st_size / 1024 / 1024
    print(f"Dosya boyutu: {sz:.1f} MB")


if __name__ == "__main__":
    run_ext4()
