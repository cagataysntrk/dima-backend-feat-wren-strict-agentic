"""Boyahane ERP + üretim + enerji-muhasebe veritabanı aynasını (DuckDB) üretir.

SEKTÖR-BAĞIMSIZ ORKESTRATÖR mimarisi:
  1. `models.boyahane.uret()` çağrılır → üretim/OEE/duruş/tamir/lab + enerji tabloları
     (SENTETİK, sabit tohumlu, iç-tutarlı) dict-listeleri olarak döner.
  2. Bu çıktı DuckDB'ye yazılır (partiler, makine_duruslari, tamir_rework, lab_olcumleri,
     oee_vardiya, uretim_aylik_ozet, tesis_enerji_aylik).
  3. Modül-düzeyi sabitlerden (MUSTERILER/TEDARIKCILER/MAKINELER/ELEKTRIK/DOGALGAZ/TESIS...)
     YENİ enerji-muhasebe tabloları (ISO 50001 / YGG grafikleri) türetilir:
     tep_ozet, yakit_karmasi, makine_enerji_aylik, oek_pareto, cusum, sevkiyat_aylik, su_bolum.
  4. ERP/İK/stok/muhasebe/finans/bakım katmanı (LOGIC korunur) modelin entitelerine
     yeniden bağlanır → cari/fatura/yevmiye/bordro/stok üretim ve enerjiyle TUTARLI olur.

TÜM adlar/sayılar KURGUSALDIR — hiçbir müşterinin gerçek verisi kullanılmaz.
Ölçek: 2026 H1 (6 ay). Yeniden üretilebilir (sabit tohum).

Çalıştırma:
    .venv/bin/python demo/build_data.py
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from models import boyahane as B  # noqa: E402  (sektör-çekirdeği kütüphanesi)

DB = Path(__file__).resolve().parent / "data" / "boyahane.duckdb"
# Model 2026 H1 (Ocak..Haziran) üretir → ERP penceresi de bu aralık.
BASE = date(2024, 1, 1)   # çok-yıl: 2024 tam + 2025 tam + 2026 H1
END = date(2026, 6, 30)
SPAN = (END - BASE).days
r2 = random.Random(20260728)   # ERP katmanı — sabit tohum (determinizm)


def d(offset: int) -> date:
    return BASE + timedelta(days=offset)


def m2(x) -> float:
    return round(float(x), 2)


def _parse_tarih(s: str) -> date:
    return date.fromisoformat(s)


def _donem(dt: date) -> str:
    return f"{dt.year}-{dt.month:02d}"


def build() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))
    # Tüm CREATE + INSERT tek transaction → satır-başı checkpoint yükünü kaldırır.
    con.execute("BEGIN TRANSACTION")

    # ════════════════════════════════════════════════════════════════════ #
    # A) SEKTÖR-ÇEKİRDEĞİ MODELİNİ ÇAĞIR + ÜRETİM/ENERJİ TABLOLARINI YAZ     #
    # ════════════════════════════════════════════════════════════════════ #
    M = B.uret()
    partiler = M["partiler"]      # ~7961
    durus = M["durus"]
    tamir = M["tamir"]
    lab = M["lab"]
    oee = M["oee"]
    aylik = M["aylik"]
    tesis = M["tesis"]

    # -- partiler (ana olgu tablosu) — modelin ürettiği tam şema ----------- #
    parti_kolonlar = [
        "parti_no", "siparis_no", "tarih", "ay", "makine", "hat", "vardiya", "vardiya_ad",
        "operator", "musteri_kod", "musteri_ad", "musteri_tolerans_dE", "birim_fiyat",
        "tedarikci_kod", "tedarikci_ad", "ham_ad", "ham_grup", "gramaj", "renk_ad",
        "renk_derinlik", "asama", "recete_kod", "kg", "metre", "en_cm", "giris_tarihi",
        "cikis_tarihi", "imalat_suresi_dk", "hiz_m_dk", "teorik_hiz_m_dk", "ilk_seferde_tamam",
        "uretim_dE", "lab_dE", "su_lt", "enerji_carpan", "elektrik_kwh", "dogalgaz_sm3",
        "elektrik_tl", "dogalgaz_tl", "su_m3", "su_tl", "atiksu_tl", "enerji_toplam_tl",
        "kwh_kg", "sm3_kg", "lt_kg", "tep", "ciro_tl", "kimyasal_tl",
    ]
    con.execute(
        "CREATE TABLE partiler ("
        "parti_no VARCHAR, siparis_no VARCHAR, tarih DATE, ay INTEGER, makine VARCHAR, "
        "hat VARCHAR, vardiya INTEGER, vardiya_ad VARCHAR, operator VARCHAR, musteri_kod VARCHAR, "
        "musteri_ad VARCHAR, musteri_tolerans_dE DOUBLE, birim_fiyat DOUBLE, tedarikci_kod VARCHAR, "
        "tedarikci_ad VARCHAR, ham_ad VARCHAR, ham_grup VARCHAR, gramaj INTEGER, renk_ad VARCHAR, "
        "renk_derinlik VARCHAR, asama VARCHAR, recete_kod VARCHAR, kg DOUBLE, metre DOUBLE, "
        "en_cm INTEGER, giris_tarihi VARCHAR, cikis_tarihi VARCHAR, imalat_suresi_dk DOUBLE, "
        "hiz_m_dk DOUBLE, teorik_hiz_m_dk DOUBLE, ilk_seferde_tamam INTEGER, uretim_dE DOUBLE, "
        "lab_dE DOUBLE, su_lt DOUBLE, enerji_carpan DOUBLE, elektrik_kwh DOUBLE, dogalgaz_sm3 DOUBLE, "
        "elektrik_tl DOUBLE, dogalgaz_tl DOUBLE, su_m3 DOUBLE, su_tl DOUBLE, atiksu_tl DOUBLE, "
        "enerji_toplam_tl DOUBLE, kwh_kg DOUBLE, sm3_kg DOUBLE, lt_kg DOUBLE, tep DOUBLE, ciro_tl DOUBLE, "
        "kimyasal_tl DOUBLE)"
    )
    con.executemany(
        "INSERT INTO partiler VALUES (" + ",".join(["?"] * len(parti_kolonlar)) + ")",
        [tuple(p.get(k) for k in parti_kolonlar) for p in partiler],
    )

    # -- makine_duruslari (modelin durus çıktısı) ------------------------- #
    con.execute(
        "CREATE TABLE makine_duruslari (id INTEGER, tarih DATE, makine VARCHAR, hat VARCHAR, "
        "vardiya INTEGER, baslangic VARCHAR, sure_dk DOUBLE, neden VARCHAR, aciklama VARCHAR)"
    )
    con.executemany(
        "INSERT INTO makine_duruslari VALUES (?,?,?,?,?,?,?,?,?)",
        [(i + 1, _parse_tarih(x["tarih"]), x["makine"], x["hat"], x["vardiya"],
          x["baslangic"], x["sure_dk"], x["neden"], x["aciklama"]) for i, x in enumerate(durus)],
    )

    # -- tamir_rework (modelin tamir çıktısı) ----------------------------- #
    con.execute(
        "CREATE TABLE tamir_rework (id INTEGER, parti VARCHAR, tarih DATE, makine VARCHAR, "
        "hat VARCHAR, vardiya INTEGER, musteri VARCHAR, musteri_ad VARCHAR, tedarikci VARCHAR, "
        "tedarikci_ad VARCHAR, renk VARCHAR, renk_derinlik VARCHAR, ham VARCHAR, sebep VARCHAR, "
        "ek_sure_dk DOUBLE, kg DOUBLE, dE DOUBLE, tolerans DOUBLE)"
    )
    con.executemany(
        "INSERT INTO tamir_rework VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(i + 1, x["parti"], _parse_tarih(x["tarih"]), x["makine"], x["hat"], x["vardiya"],
          x["musteri"], x["musteri_ad"], x["tedarikci"], x["tedarikci_ad"], x["renk"],
          x["renk_derinlik"], x["ham"], x["sebep"], x["ek_sure_dk"], x["kg"], x["dE"],
          x["tolerans"]) for i, x in enumerate(tamir)],
    )

    # -- lab_olcumleri (modelin lab çıktısı) ------------------------------ #
    con.execute(
        "CREATE TABLE lab_olcumleri (id INTEGER, parti VARCHAR, tarih DATE, makine VARCHAR, "
        "musteri VARCHAR, renk VARCHAR, ham VARCHAR, lab_dE DOUBLE, uretim_dE DOUBLE, "
        "sapma DOUBLE, tolerans DOUBLE)"
    )
    con.executemany(
        "INSERT INTO lab_olcumleri VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [(i + 1, x["parti"], _parse_tarih(x["tarih"]), x["makine"], x["musteri"], x["renk"],
          x["ham"], x["lab_dE"], x["uretim_dE"], x["sapma"], x["tolerans"])
         for i, x in enumerate(lab)],
    )

    # -- oee_vardiya (modelin oee çıktısı) -------------------------------- #
    con.execute(
        "CREATE TABLE oee_vardiya (id INTEGER, tarih DATE, makine VARCHAR, hat VARCHAR, "
        "vardiya INTEGER, vardiya_suresi_dk INTEGER, planli_durus_dk INTEGER, "
        "planli_uretim_suresi_dk INTEGER, plansiz_durus_dk DOUBLE, calisma_suresi_dk DOUBLE, "
        "uretim_kg DOUBLE, hatali_kg DOUBLE, parti_sayisi INTEGER, ilk_seferde_tamam INTEGER, "
        "rft_yuzde DOUBLE, kullanilabilirlik_EV DOUBLE, performans_PV DOUBLE, kalite_KS DOUBLE, OEE DOUBLE)"
    )
    con.executemany(
        "INSERT INTO oee_vardiya VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(i + 1, _parse_tarih(x["tarih"]), x["makine"], x["hat"], x["vardiya"],
          x["vardiya_suresi_dk"], x["planli_durus_dk"], x["planli_uretim_suresi_dk"],
          x["plansiz_durus_dk"], x["calisma_suresi_dk"], x["uretim_kg"], x["hatali_kg"],
          x["parti_sayisi"], x["ilk_seferde_tamam"], x["rft_yuzde"], x["kullanilabilirlik_EV"],
          x["performans_PV"], x["kalite_KS"], x["OEE"]) for i, x in enumerate(oee)],
    )

    # -- uretim_aylik_ozet (modelin aylik çıktısı) ------------------------ #
    con.execute(
        "CREATE TABLE uretim_aylik_ozet (yil INTEGER, ay INTEGER, uretim_kg DOUBLE, sevkiyat_kg DOUBLE, "
        "elektrik_kwh DOUBLE, dogalgaz_sm3 DOUBLE, su_m3 DOUBLE, kwh_kg DOUBLE, sm3_kg DOUBLE, "
        "lt_kg DOUBLE, rework_parti INTEGER, ciro_tl DOUBLE, tep_proses DOUBLE)"
    )
    con.executemany(
        "INSERT INTO uretim_aylik_ozet VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(x["yil"], x["ay"], x["uretim_kg"], x["sevkiyat_kg"], x["elektrik_kwh"], x["dogalgaz_sm3"],
          x["su_m3"], x["kwh_kg"], x["sm3_kg"], x["lt_kg"], x["rework_parti"], x["ciro_tl"],
          x["tep_proses"]) for x in aylik],
    )

    # -- tesis_enerji_aylik (modelin tesis çıktısı) ----------------------- #
    con.execute(
        "CREATE TABLE tesis_enerji_aylik (yil INTEGER, ay INTEGER, uretim_kg DOUBLE, sevkiyat_kg DOUBLE, "
        "sebeke_kwh DOUBLE, ges_kwh DOUBLE, toplam_elektrik_kwh DOUBLE, fatura_tl DOUBLE, "
        "birim_tl_kwh DOUBLE, elektrik_kg DOUBLE, ges_payi_yuzde DOUBLE, kuyu_su_m3 DOUBLE, "
        "atiksu_m3 DOUBLE, su_lt_kg DOUBLE)"
    )
    con.executemany(
        "INSERT INTO tesis_enerji_aylik VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(x["yil"], x["ay"], x["uretim_kg"], x["sevkiyat_kg"], x["sebeke_kwh"], x["ges_kwh"],
          x["toplam_elektrik_kwh"], x["fatura_tl"], x["birim_tl_kwh"], x["elektrik_kg"],
          x["ges_payi_yuzde"], x["kuyu_su_m3"], x["atiksu_m3"], x["su_lt_kg"]) for x in tesis],
    )

    # ════════════════════════════════════════════════════════════════════ #
    # B) YENİ ENERJİ-MUHASEBE TABLOLARI (ISO 50001 / YGG grafikleri)        #
    # ════════════════════════════════════════════════════════════════════ #
    # Çok-yıl: aylık anahtar (yil, ay) — 2024 tam + 2025 tam + 2026 H1.
    AY_ANAHTAR = [(y, a) for y, aa in B.YIL_AYLAR.items() for a in aa]
    tesis_by_ay = {(t["yil"], t["ay"]): t for t in tesis}
    uretim_by_ay = {(a["yil"], a["ay"]): a for a in aylik}
    # o (yıl,ay)'da üretim (dolayısıyla tesis satırı) var mı — boş dönemleri atla
    AY_ANAHTAR = [k for k in AY_ANAHTAR if k in tesis_by_ay]

    def proses_dogalgaz(yil, ay):
        return sum(B.DOGALGAZ.get(m, {}).get((yil, ay), 0) for m in B.DOGALGAZ)

    # -- 1) tep_ozet ------------------------------------------------------ #
    con.execute(
        "CREATE TABLE tep_ozet (yil INTEGER, ay INTEGER, uretim_kg DOUBLE, sevkiyat_kg DOUBLE, "
        "elektrik_tep DOUBLE, dogalgaz_tep DOUBLE, kati_yakit_tep DOUBLE, motorin_tep DOUBLE, "
        "benzin_tep DOUBLE, toplam_tep DOUBLE, set_uretim_tep_ton DOUBLE, set_sevkiyat_tep_ton DOUBLE)"
    )
    tep_rows = []
    for yil, ay in AY_ANAHTAR:
        u_kg = B.URETIM_KG[(yil, ay)]
        s_kg = B.SEVKIYAT_KG[(yil, ay)]
        el_tep = B.tep_elektrik(tesis_by_ay[(yil, ay)]["toplam_elektrik_kwh"])
        dg_sm3 = proses_dogalgaz(yil, ay) + B.KAZAN_DOGALGAZ[(yil, ay)]
        dg_tep = B.tep_dogalgaz(dg_sm3)
        ky_tep = B.KATI_YAKIT[(yil, ay)][0] * B.TEP_KATI_KG
        mo_tep = B.MOTORIN_LT[(yil, ay)] * B.TEP_MOTORIN_LT
        bz_tep = B.BENZIN_LT[(yil, ay)] * B.TEP_BENZIN_LT
        toplam = el_tep + dg_tep + ky_tep + mo_tep + bz_tep
        tep_rows.append((yil, ay, m2(u_kg), m2(s_kg), round(el_tep, 4), round(dg_tep, 4),
                         round(ky_tep, 4), round(mo_tep, 4), round(bz_tep, 4), round(toplam, 4),
                         round(toplam / (u_kg / 1000), 5), round(toplam / (s_kg / 1000), 5)))
    con.executemany("INSERT INTO tep_ozet VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tep_rows)

    # -- 2) yakit_karmasi (yakıt dönüşümü: Nisan'da katı yakıt devreye girer) #
    con.execute(
        "CREATE TABLE yakit_karmasi (yil INTEGER, ay INTEGER, kazan_dogalgaz_sm3 DOUBLE, kati_yakit_kg DOUBLE, "
        "kati_yakit_tl DOUBLE, buhar_ton DOUBLE, dogalgaz_kazan_tep DOUBLE, kati_yakit_tep DOUBLE)"
    )
    yk_rows = []
    for yil, ay in AY_ANAHTAR:
        kazan_sm3 = B.KAZAN_DOGALGAZ[(yil, ay)]
        ky_kg, ky_tl = B.KATI_YAKIT[(yil, ay)]
        yk_rows.append((yil, ay, m2(kazan_sm3), m2(ky_kg), m2(ky_tl), B.BUHAR_TON[(yil, ay)],
                        round(B.tep_dogalgaz(kazan_sm3), 4), round(ky_kg * B.TEP_KATI_KG, 4)))
    con.executemany("INSERT INTO yakit_karmasi VALUES (?,?,?,?,?,?,?,?)", yk_rows)

    # -- 3) makine_enerji_aylik (makine × yıl × ay) ----------------------- #
    con.execute(
        "CREATE TABLE makine_enerji_aylik (makine VARCHAR, hat VARCHAR, bolum VARCHAR, yil INTEGER, ay INTEGER, "
        "elektrik_kwh DOUBLE, dogalgaz_sm3 DOUBLE, tep DOUBLE)"
    )
    me_rows = []
    for m in B.ELEKTRIK:
        hat = B.MAKINELER[m]["hat"]
        bolum = B.MAKINE_BOLUM.get(m, "Diğer")
        for yil, ay in AY_ANAHTAR:
            el = B.ELEKTRIK[m][(yil, ay)]
            dg = B.DOGALGAZ.get(m, {}).get((yil, ay), 0)
            tep = B.tep_elektrik(el) + B.tep_dogalgaz(dg)
            me_rows.append((m, hat, bolum, yil, ay, m2(el), m2(dg), round(tep, 4)))
    con.executemany("INSERT INTO makine_enerji_aylik VALUES (?,?,?,?,?,?,?,?)", me_rows)

    # -- 4) oek_pareto (bölüm bazlı, Pareto sıralı — H1 toplamı) ---------- #
    con.execute(
        "CREATE TABLE oek_pareto (yil INTEGER, bolum VARCHAR, kaynak VARCHAR, toplam_tep DOUBLE, "
        "pay_yuzde DOUBLE, kumulatif_yuzde DOUBLE, oek BOOLEAN)"
    )
    pareto_rows = []
    for yil in B.YIL_AYLAR:  # HER YIL kendi ÖEK/SEU Pareto sıralaması (ISO 50001 §6.3)
        yil_aylar = [a for (y, a) in AY_ANAHTAR if y == yil]
        if not yil_aylar:
            continue
        bolum_tep = defaultdict(float)
        for m in B.ELEKTRIK:
            bolum = B.MAKINE_BOLUM.get(m, "Diğer")
            for ay in yil_aylar:
                el = B.ELEKTRIK[m][(yil, ay)]
                dg = B.DOGALGAZ.get(m, {}).get((yil, ay), 0)
                bolum_tep[bolum] += B.tep_elektrik(el) + B.tep_dogalgaz(dg)
        kaynaklar = [(b, b, bolum_tep[b]) for b in bolum_tep]
        kati_tep = sum(B.KATI_YAKIT[(yil, ay)][0] * B.TEP_KATI_KG for ay in yil_aylar)
        arac_tep = sum(B.MOTORIN_LT[(yil, ay)] * B.TEP_MOTORIN_LT + B.BENZIN_LT[(yil, ay)] * B.TEP_BENZIN_LT
                       for ay in yil_aylar)
        kaynaklar.append(("Katı Yakıt Kazanı", "Katı Yakıt Kazanı", kati_tep))
        kaynaklar.append(("Araç/Forklift", "Araç/Forklift", arac_tep))
        tesis_el_tep = sum(B.tep_elektrik(tesis_by_ay[(yil, ay)]["toplam_elektrik_kwh"]) for ay in yil_aylar)
        tesis_gaz_tep = sum(B.tep_dogalgaz(proses_dogalgaz(yil, ay) + B.KAZAN_DOGALGAZ[(yil, ay)]) for ay in yil_aylar)
        dagitilmamis = (tesis_el_tep + tesis_gaz_tep) - sum(bolum_tep.values()) - kati_tep
        if dagitilmamis > 0:
            kaynaklar.append(("Dağıtılmamış/Ortak", "Dağıtılmamış/Ortak", dagitilmamis))
        kaynaklar.sort(key=lambda x: x[2], reverse=True)
        genel_toplam = sum(k[2] for k in kaynaklar)
        kum = 0.0
        for bolum, kaynak, tep in kaynaklar:
            pay = tep / genel_toplam * 100 if genel_toplam else 0
            kum += pay
            pareto_rows.append((yil, bolum, kaynak, round(tep, 3), round(pay, 2), round(kum, 2),
                                kum <= 80.0 + 1e-9))
    con.executemany("INSERT INTO oek_pareto VALUES (?,?,?,?,?,?,?)", pareto_rows)

    # -- 5) cusum (ay × kaynak: üretim→tüketim regresyonu; ENPG + kümülatif) #
    con.execute(
        "CREATE TABLE cusum (yil INTEGER, ay INTEGER, kaynak VARCHAR, uretim_kg DOUBLE, gerceklesen DOUBLE, "
        "beklenen DOUBLE, enpg DOUBLE, cusum DOUBLE)"
    )
    cusum_rows = []
    for yil in B.YIL_AYLAR:  # regresyon (EnB) + CUSUM HER YIL kendi içinde (ISO 50006 baseline)
        yil_aylar = [a for (y, a) in AY_ANAHTAR if y == yil]
        if len(yil_aylar) < 2:
            continue  # regresyon için en az 2 nokta
        uretim_arr = np.array([B.URETIM_KG[(yil, ay)] for ay in yil_aylar], dtype=float)
        kaynak_gercek = {
            "elektrik": [tesis_by_ay[(yil, ay)]["toplam_elektrik_kwh"] for ay in yil_aylar],
            "dogalgaz": [proses_dogalgaz(yil, ay) + B.KAZAN_DOGALGAZ[(yil, ay)] for ay in yil_aylar],
            "su": [tesis_by_ay[(yil, ay)]["kuyu_su_m3"] for ay in yil_aylar],
        }
        for kaynak, gercekler in kaynak_gercek.items():
            g_arr = np.array(gercekler, dtype=float)
            egim, kesme = np.polyfit(uretim_arr, g_arr, 1)  # doğrusal regresyon (yıl bazında EnB)
            kum = 0.0
            for i, ay in enumerate(yil_aylar):
                beklenen = egim * uretim_arr[i] + kesme
                enpg = g_arr[i] - beklenen
                kum += enpg
                cusum_rows.append((yil, ay, kaynak, m2(uretim_arr[i]), m2(g_arr[i]), round(beklenen, 1),
                                   round(enpg, 1), round(kum, 1)))
    con.executemany("INSERT INTO cusum VALUES (?,?,?,?,?,?,?,?)", cusum_rows)

    # -- 6) sevkiyat_aylik ------------------------------------------------ #
    con.execute(
        "CREATE TABLE sevkiyat_aylik (yil INTEGER, ay INTEGER, uretim_kg DOUBLE, sevkiyat_kg DOUBLE, "
        "stok_degisim DOUBLE)"
    )
    con.executemany(
        "INSERT INTO sevkiyat_aylik VALUES (?,?,?,?,?)",
        [(yil, ay, m2(B.URETIM_KG[(yil, ay)]), m2(B.SEVKIYAT_KG[(yil, ay)]),
          m2(B.URETIM_KG[(yil, ay)] - B.SEVKIYAT_KG[(yil, ay)])) for yil, ay in AY_ANAHTAR],
    )

    # -- 7) su_bolum (bölüm × yıl × ay — kuyu suyunu üretim payına göre dağıt) --- #
    con.execute(
        "CREATE TABLE su_bolum (bolum VARCHAR, yil INTEGER, ay INTEGER, su_m3 DOUBLE, su_lt_kg DOUBLE)"
    )
    su_rows = []
    for yil, ay in AY_ANAHTAR:
        el_top = sum(B.ELEKTRIK[m][(yil, ay)] for m in B.ELEKTRIK)
        bolum_el = defaultdict(float)
        for m in B.ELEKTRIK:
            bolum_el[B.MAKINE_BOLUM.get(m, "Diğer")] += B.ELEKTRIK[m][(yil, ay)]
        kuyu = tesis_by_ay[(yil, ay)]["kuyu_su_m3"]
        u_kg = B.URETIM_KG[(yil, ay)]
        for bolum, el in bolum_el.items():
            pay = el / el_top if el_top else 0
            su_m3 = kuyu * pay
            bolum_kg = u_kg * pay
            su_rows.append((bolum, yil, ay, m2(su_m3), round(su_m3 * 1000 / bolum_kg, 1) if bolum_kg else 0))
    con.executemany("INSERT INTO su_bolum VALUES (?,?,?,?,?)", su_rows)

    # ════════════════════════════════════════════════════════════════════ #
    # C) ERP / İK / STOK / MUHASEBE / FİNANS / BAKIM (LOGIC KORUNUR)        #
    #    Entite kaynakları modelin entitelerine yeniden bağlanır (TUTARLI). #
    # ════════════════════════════════════════════════════════════════════ #

    def ettn() -> str:
        h = "0123456789abcdef"
        seg = lambda n: "".join(r2.choice(h) for _ in range(n))
        return f"{seg(8)}-{seg(4)}-{seg(4)}-{seg(4)}-{seg(12)}"

    # ------------------------------------------------------------------ #
    # C1) REFERANS: müşteri / makine / reçete / personel / kimyasal       #
    #     → modelin entitelerinden kurulur                                #
    # ------------------------------------------------------------------ #
    # müşteriler (modelin MUSTERILER'i — alıcılar)
    con.execute(
        "CREATE TABLE musteriler (musteri_kodu VARCHAR PRIMARY KEY, musteri_adi VARCHAR, "
        "tolerans_dE DOUBLE, birim_fiyat DOUBLE, pay DOUBLE)"
    )
    con.executemany("INSERT INTO musteriler VALUES (?,?,?,?,?)",
                    [(m["kod"], m["ad"], m["tolerans"], m["fiyat"], m["pay"]) for m in B.MUSTERILER])
    musteri_kodlari = [m["kod"] for m in B.MUSTERILER]
    musteri_ad = {m["kod"]: m["ad"] for m in B.MUSTERILER}

    # makineler (modelin MAKINELER'i)
    con.execute(
        "CREATE TABLE makineler (makine VARCHAR PRIMARY KEY, hat VARCHAR, bolum VARCHAR, "
        "teorik_hiz DOUBLE, kapasite_kg INTEGER, en_cm INTEGER)"
    )
    con.executemany("INSERT INTO makineler VALUES (?,?,?,?,?,?)",
                    [(m, mk["hat"], B.MAKINE_BOLUM.get(m, "Diğer"), mk["teorik_hiz"],
                      mk["kapasite_kg"], mk["en_cm"]) for m, mk in B.MAKINELER.items()])
    makine_kodlari = list(B.MAKINELER.keys())

    # ham/iplik kartları (modelin HAMLAR'ı — stok/BOM kaynağı)
    con.execute(
        "CREATE TABLE ham_kartlari (ham_kodu VARCHAR PRIMARY KEY, ham_adi VARCHAR, grup VARCHAR, "
        "gramaj INTEGER, zorluk DOUBLE)"
    )
    ham_kodlu = [(f"HAM-{i+1:02d}", h["ad"], h["grup"], h["gramaj"], h["zorluk"])
                 for i, h in enumerate(B.HAMLAR)]
    con.executemany("INSERT INTO ham_kartlari VALUES (?,?,?,?,?)", ham_kodlu)
    ham_kod_by_ad = {h["ad"]: f"HAM-{i+1:02d}" for i, h in enumerate(B.HAMLAR)}

    # kimyasallar (boya/yardımcı — ERP stok/BOM için, kurgusal)
    KIMYASALLAR = [
        ("K01", "Kostik Soda", "alkali", 12.5), ("K02", "Hidrojen Peroksit", "yardimci", 18.0),
        ("K03", "Tuz (Glauber)", "tuz", 4.2), ("K04", "Soda (Kalsine)", "alkali", 9.0),
        ("K05", "Sülfürik Asit", "asit", 7.5), ("K06", "Dispergatör", "yardimci", 22.0),
        ("K07", "Yumuşatıcı", "yardimci", 28.0), ("K08", "Sekestran", "yardimci", 19.5),
        ("K09", "Reaktif Boyarmadde", "boyarmadde", 145.0),
        ("K10", "Dispers Boyarmadde", "boyarmadde", 120.0),
    ]
    con.execute(
        "CREATE TABLE kimyasallar (kimyasal_kodu VARCHAR PRIMARY KEY, kimyasal_adi VARCHAR, "
        "tur VARCHAR, birim_fiyat DOUBLE)"
    )
    con.executemany("INSERT INTO kimyasallar VALUES (?,?,?,?)", KIMYASALLAR)

    # ------------------------------------------------------------------ #
    # C2) TEDARİKÇİLER — modelin TEDARIKCILER'i (iplik) + hizmet/kimyasal #
    # ------------------------------------------------------------------ #
    TEDARIKCILER = []
    for t in B.TEDARIKCILER:  # modelin iplik tedarikçileri (T-101..T-538)
        TEDARIKCILER.append((t["kod"], t["ad"], "Çorlu", f"12345{r2.randint(10000, 99999)}", "iplik"))
    # ek hizmet/kimyasal tedarikçileri (enerji/nakliye/ambalaj — kurgusal)
    EK_TEDARIKCI = [
        ("TK-01", "DyStar Kimya Tic.", "İstanbul", "boyarmadde"),
        ("TK-02", "Archroma Kimya", "Gebze", "kimyasal"),
        ("TK-03", "Rudolf Kimya", "İstanbul", "kimyasal"),
        ("TK-04", "Ege Enerji Doğalgaz", "İzmir", "hizmet"),
        ("TK-05", "Trakya Elektrik Dağıtım", "Tekirdağ", "hizmet"),
        ("TK-06", "Marmara Nakliyat Ltd.", "İstanbul", "hizmet"),
        ("TK-07", "Öz Ambalaj San.", "Çorlu", "yardimci"),
    ]
    for kod, ad, sehir, tur in EK_TEDARIKCI:
        TEDARIKCILER.append((kod, ad, sehir, f"12345{r2.randint(10000, 99999)}", tur))
    con.execute(
        "CREATE TABLE tedarikciler (tedarikci_kodu VARCHAR PRIMARY KEY, unvan VARCHAR, "
        "sehir VARCHAR, vergi_no VARCHAR, tur VARCHAR)"
    )
    con.executemany("INSERT INTO tedarikciler VALUES (?,?,?,?,?)", TEDARIKCILER)
    ted_kodlari = [t[0] for t in TEDARIKCILER]
    ted_ad = {t[0]: t[1] for t in TEDARIKCILER}
    ted_by_tur = defaultdict(list)
    for t in TEDARIKCILER:
        ted_by_tur[t[4]].append(t[0])
    iplik_ted = [t["kod"] for t in B.TEDARIKCILER]

    # ------------------------------------------------------------------ #
    # C3) HESAP PLANI + BANKA + DEPO + SERTİFİKA (LOGIC korunur)          #
    # ------------------------------------------------------------------ #
    HESAP_PLANI = [
        ("100", "Kasa", "aktif", "Dönen Varlıklar"),
        ("101", "Alınan Çekler", "aktif", "Dönen Varlıklar"),
        ("102", "Bankalar", "aktif", "Dönen Varlıklar"),
        ("103", "Verilen Çekler ve Ödeme Emirleri (-)", "aktif", "Dönen Varlıklar"),
        ("120", "Alıcılar", "aktif", "Dönen Varlıklar"),
        ("121", "Alacak Senetleri", "aktif", "Dönen Varlıklar"),
        ("150", "İlk Madde ve Malzeme", "aktif", "Dönen Varlıklar"),
        ("151", "Yarı Mamuller", "aktif", "Dönen Varlıklar"),
        ("152", "Mamuller", "aktif", "Dönen Varlıklar"),
        ("153", "Ticari Mallar", "aktif", "Dönen Varlıklar"),
        ("191", "İndirilecek KDV", "aktif", "Dönen Varlıklar"),
        ("253", "Tesis Makine ve Cihazlar", "aktif", "Duran Varlıklar"),
        ("320", "Satıcılar", "pasif", "Kısa Vadeli Yab. Kaynak"),
        ("321", "Borç Senetleri", "pasif", "Kısa Vadeli Yab. Kaynak"),
        ("335", "Personele Borçlar", "pasif", "Kısa Vadeli Yab. Kaynak"),
        ("360", "Ödenecek Vergi ve Fonlar", "pasif", "Kısa Vadeli Yab. Kaynak"),
        ("361", "Ödenecek Sosyal Güvenlik Kesintileri", "pasif", "Kısa Vadeli Yab. Kaynak"),
        ("391", "Hesaplanan KDV", "pasif", "Kısa Vadeli Yab. Kaynak"),
        ("600", "Yurtiçi Satışlar", "gelir", "Gelir Tablosu"),
        ("601", "Yurtdışı Satışlar", "gelir", "Gelir Tablosu"),
        ("610", "Satıştan İadeler (-)", "gelir", "Gelir Tablosu"),
        ("620", "Satılan Mamul Maliyeti (-)", "gider", "Gelir Tablosu"),
        ("710", "Direkt İlk Madde ve Malzeme Gideri", "gider", "Maliyet"),
        ("720", "Direkt İşçilik Gideri", "gider", "Maliyet"),
        ("730", "Genel Üretim Giderleri", "gider", "Maliyet"),
        ("740", "Hizmet Üretim Maliyeti", "gider", "Maliyet"),
        ("770", "Genel Yönetim Giderleri", "gider", "Gelir Tablosu"),
    ]
    con.execute(
        "CREATE TABLE hesap_plani (hesap_kodu VARCHAR PRIMARY KEY, hesap_adi VARCHAR, "
        "hesap_tipi VARCHAR, ana_grup VARCHAR)"
    )
    con.executemany("INSERT INTO hesap_plani VALUES (?,?,?,?)", HESAP_PLANI)

    BANKALAR = [
        ("B01", "Ziraat Bankası", "Çorlu Şubesi", "TR12 0001 0001 2345 6789 01", "TL"),
        ("B02", "İş Bankası", "Velimeşe Şubesi", "TR34 0006 4000 0012 3456 78", "TL"),
        ("B03", "Garanti BBVA", "Çorlu Şubesi", "TR56 0006 2000 0345 6789 01", "USD"),
        ("B04", "Yapı Kredi", "Merkez Şubesi", "TR78 0006 7010 0000 1234 56", "EUR"),
    ]
    con.execute(
        "CREATE TABLE banka_hesaplari (banka_kodu VARCHAR PRIMARY KEY, banka_adi VARCHAR, "
        "sube VARCHAR, iban VARCHAR, para_birimi VARCHAR)"
    )
    con.executemany("INSERT INTO banka_hesaplari VALUES (?,?,?,?,?)", BANKALAR)

    DEPOLAR = [
        ("D01", "Ham Kumaş Deposu", "hammadde"), ("D02", "İplik Deposu", "hammadde"),
        ("D03", "Boya-Kimyasal Deposu", "kimyasal"), ("D04", "Mamul Depo", "mamul"),
        ("D05", "Yardımcı Malzeme Deposu", "yardimci"),
    ]
    con.execute("CREATE TABLE depolar (depo_kodu VARCHAR PRIMARY KEY, depo_adi VARCHAR, tur VARCHAR)")
    con.executemany("INSERT INTO depolar VALUES (?,?,?)", DEPOLAR)

    SERTIFIKALAR = [
        ("SRT-01", "OEKO-TEX Standard 100", date(2025, 3, 1), date(2027, 2, 28), "Tüm mamul kumaşlar", "aktif"),
        ("SRT-02", "GOTS", date(2025, 6, 1), date(2026, 5, 31), "Organik pamuk hattı", "aktif"),
        ("SRT-03", "OE 100 / OE Blended", date(2025, 1, 15), date(2026, 12, 31), "Organik izlenebilirlik", "aktif"),
        ("SRT-04", "GRS", date(2025, 4, 1), date(2027, 3, 31), "Geri dönüşüm PES", "aktif"),
        ("SRT-05", "ISO 9001:2015", date(2024, 9, 1), date(2027, 8, 31), "Kalite yönetim sistemi", "aktif"),
        ("SRT-06", "ISO 50001:2018", date(2025, 1, 1), date(2028, 12, 31), "Enerji yönetim sistemi", "aktif"),
    ]
    con.execute(
        "CREATE TABLE sertifikalar (sertifika_kodu VARCHAR PRIMARY KEY, tur VARCHAR, "
        "gecerlilik_baslangic DATE, gecerlilik_bitis DATE, kapsam VARCHAR, durum VARCHAR)"
    )
    con.executemany("INSERT INTO sertifikalar VALUES (?,?,?,?,?,?)", SERTIFIKALAR)

    # ------------------------------------------------------------------ #
    # C4) İNSAN KAYNAKLARI — modelin PERSONEL'i (üretim) + idari kadro    #
    # ------------------------------------------------------------------ #
    con.execute(
        "CREATE TABLE personel (personel_kodu VARCHAR PRIMARY KEY, ad_soyad VARCHAR, "
        "vardiya VARCHAR, departman VARCHAR, cinsiyet VARCHAR)"
    )
    # üretim personeli: modelin PERSONEL[vardiya] listesi (9 kişi, vardiya-bazlı)
    _KADIN = {"SEDA YILDIZ", "AYLİN BULUT"}  # kurgusal cinsiyet ataması
    uretim_personel = []
    pcode = 1
    op_ad_to_kod = {}
    for vard, adlar in B.PERSONEL.items():
        vard_ad = B.VARDIYALAR[vard]["ad"].split(" ")[0] + ". Vardiya"
        for ad in adlar:
            kod = f"P{pcode:02d}"
            cins = "Kadın" if ad in _KADIN else "Erkek"
            uretim_personel.append((kod, ad, str(vard), "Boyahane", cins))
            op_ad_to_kod[ad] = kod
            pcode += 1
    # idari/destek kadro (kurgusal)
    _ADLAR = ["Ahmet Yılmaz", "Mehmet Kaya", "Elif Demir", "Zeynep Şahin", "Mustafa Çelik",
              "Fatma Yıldız", "Ali Aydın", "Ayşe Öztürk", "Hasan Doğan", "Emine Kılıç",
              "Osman Arslan", "Merve Kara", "Serkan Koç", "Gamze Polat", "Burak Şimşek",
              "Deniz Çakır", "Yasemin Bulut", "Tolga Erdoğan", "Sıla Yalçın", "Onur Güneş"]
    HR_DEP = [("Laboratuvar", "Laborant", 3), ("Kalite", "Kalite Kontrolör", 3),
              ("Bakım", "Bakım Teknisyeni", 3), ("Muhasebe", "Muhasebe Uzmanı", 2),
              ("İdari", "İdari Personel", 3), ("Satınalma", "Satınalma Uzmanı", 2),
              ("Planlama", "Planlama Uzmanı", 2), ("Depo", "Depo Görevlisi", 2)]
    idari_personel = []
    ai = 0
    for dep, poz, adet in HR_DEP:
        for _ in range(adet):
            ad = _ADLAR[ai % len(_ADLAR)]
            ai += 1
            vard = "1" if dep in ("Muhasebe", "İdari", "Satınalma", "Planlama") else str(r2.randint(1, 3))
            cins = "Kadın" if ad.split()[0] in ("Elif", "Zeynep", "Fatma", "Ayşe", "Emine",
                                                "Merve", "Gamze", "Deniz", "Yasemin", "Sıla") else "Erkek"
            idari_personel.append((f"P{pcode:02d}", ad, vard, dep, cins))
            pcode += 1
    tum_personel = uretim_personel + idari_personel
    con.executemany("INSERT INTO personel VALUES (?,?,?,?,?)", tum_personel)

    # özlük + maaş
    con.execute(
        "CREATE TABLE personel_ozluk (personel_kodu VARCHAR PRIMARY KEY, tc_kimlik VARCHAR, "
        "ise_giris DATE, dogum_tarihi DATE, sgk_no VARCHAR, pozisyon VARCHAR, brut_maas DOUBLE, "
        "banka_kodu VARCHAR, medeni_hal VARCHAR, egitim VARCHAR)"
    )
    POZ_MAAS = {"Boyahane": ("Boya Operatörü", 26000), "Laboratuvar": ("Laborant", 29000),
                "Kalite": ("Kalite Kontrolör", 27000), "Bakım": ("Bakım Teknisyeni", 30000),
                "Muhasebe": ("Muhasebe Uzmanı", 34000), "İdari": ("İdari Personel", 32000),
                "Satınalma": ("Satınalma Uzmanı", 33000), "Planlama": ("Planlama Uzmanı", 31000),
                "Depo": ("Depo Görevlisi", 24000)}
    ozluk = []
    for p in tum_personel:
        poz, taban = POZ_MAAS.get(p[3], ("Personel", 26000))
        brut = taban + r2.randint(-2000, 6000)
        ise_giris = date(2015, 1, 1) + timedelta(days=r2.randint(0, 3800))
        dogum = date(1975, 1, 1) + timedelta(days=r2.randint(0, 9000))
        ozluk.append((p[0], f"***{r2.randint(100000, 999999)}**", ise_giris, dogum,
                      f"SGK{r2.randint(1000000, 9999999)}", poz, m2(brut),
                      r2.choice(["B01", "B02"]), r2.choice(["Evli", "Bekar"]),
                      r2.choice(["Lise", "Ön Lisans", "Lisans", "İlköğretim"])))
    con.executemany("INSERT INTO personel_ozluk VALUES (?,?,?,?,?,?,?,?,?,?)", ozluk)
    brut_by_pers = {o[0]: o[6] for o in ozluk}

    # puantaj (günlük devam) — model iş-günü mantığı (Pazar hariç, Cmt çalışılır)
    con.execute(
        "CREATE TABLE puantaj (id INTEGER PRIMARY KEY, tarih DATE, personel_kodu VARCHAR, "
        "vardiya VARCHAR, giris_saat VARCHAR, cikis_saat VARCHAR, calisilan_saat DOUBLE, "
        "mesai_saat DOUBLE, durum VARCHAR)"
    )
    puantaj_rows = []
    puid = 1
    vard_saat = {"1": ("08:00", "16:00"), "2": ("16:00", "24:00"), "3": ("00:00", "08:00")}
    for gun in range(0, SPAN + 1):
        gd = d(gun)
        wd = gd.weekday()  # 6 = Pazar
        for p in tum_personel:
            # Pazar hiç çalışılmaz (model _is_gunleri); idari ayrıca Cumartesi de çalışmaz
            if wd == 6:
                continue
            if wd == 5 and p[3] in ("Muhasebe", "İdari", "Satınalma", "Planlama"):
                continue
            rr = r2.random()
            if rr < 0.03:
                durum, cal, mesai, gs, cs = "rapor", 0.0, 0.0, "-", "-"
            elif rr < 0.06:
                durum, cal, mesai, gs, cs = "izin", 0.0, 0.0, "-", "-"
            elif rr < 0.075:
                durum, cal, mesai, gs, cs = "devamsiz", 0.0, 0.0, "-", "-"
            else:
                gs, cs = vard_saat.get(p[2], ("08:00", "16:00"))
                mesai = round(r2.choice([0, 0, 0, 1, 2]) * 1.0, 1)
                durum, cal = "calisti", round(8.0 + mesai, 1)
            puantaj_rows.append((puid, gd, p[0], p[2], gs, cs, cal, mesai, durum))
            puid += 1
    con.executemany("INSERT INTO puantaj VALUES (?,?,?,?,?,?,?,?,?)", puantaj_rows)

    # bordro (aylık) — 2024-01 .. 2026-06 (çok-yıl)
    con.execute(
        "CREATE TABLE bordro (id INTEGER PRIMARY KEY, donem VARCHAR, personel_kodu VARCHAR, "
        "brut_maas DOUBLE, sgk_isci DOUBLE, issizlik_isci DOUBLE, gelir_vergisi DOUBLE, "
        "damga_vergisi DOUBLE, mesai_ucreti DOUBLE, prim DOUBLE, net_maas DOUBLE, sgk_isveren DOUBLE)"
    )
    bordro_rows = []
    bid = 1
    bordro_donem_tutar = defaultdict(float)  # dönem → toplam brut+sgk_isveren (yevmiye için)
    for yil, ay in AY_ANAHTAR:
        donem = f"{yil}-{ay:02d}"
        for p in tum_personel:
            brut = brut_by_pers[p[0]]
            sgk_isci = m2(brut * 0.14)
            issizlik = m2(brut * 0.01)
            gv = m2((brut - sgk_isci - issizlik) * 0.15)
            damga = m2(brut * 0.00759)
            mesai_uc = m2(r2.choice([0, 0, 500, 900, 1400]))
            prim = m2(r2.choice([0, 0, 0, 1000, 2500]))
            net = m2(brut - sgk_isci - issizlik - gv - damga + mesai_uc + prim)
            sgk_isv = m2(brut * 0.2075)
            bordro_rows.append((bid, donem, p[0], brut, sgk_isci, issizlik, gv, damga,
                                mesai_uc, prim, net, sgk_isv))
            bordro_donem_tutar[donem] += brut + sgk_isv
            bid += 1
    con.executemany("INSERT INTO bordro VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", bordro_rows)

    # izinler
    con.execute(
        "CREATE TABLE izinler (id INTEGER PRIMARY KEY, personel_kodu VARCHAR, izin_tipi VARCHAR, "
        "baslangic DATE, bitis DATE, gun_sayisi INTEGER, durum VARCHAR)"
    )
    izin_rows = []
    for izid in range(1, 121):
        p = r2.choice(tum_personel)
        tip = r2.choice(["yillik", "yillik", "mazeret", "rapor", "ucretsiz"])
        bas = d(r2.randint(0, SPAN - 5))
        gun = r2.randint(1, 10)
        izin_rows.append((izid, p[0], tip, bas, bas + timedelta(days=gun), gun,
                          r2.choice(["onaylandi", "onaylandi", "beklemede"])))
    con.executemany("INSERT INTO izinler VALUES (?,?,?,?,?,?,?)", izin_rows)

    # ------------------------------------------------------------------ #
    # C5) STOK / DEPO — HAMLAR (iplik) + kimyasallar; çıkışlar partilerle  #
    #     tutarlı (partilerin ham tüketimi)                                #
    # ------------------------------------------------------------------ #
    con.execute(
        "CREATE TABLE stok_kartlari (stok_kodu VARCHAR PRIMARY KEY, stok_adi VARCHAR, "
        "grup VARCHAR, birim VARCHAR, kritik_stok DOUBLE, guncel_miktar DOUBLE, birim_maliyet DOUBLE)"
    )
    stok_kart_rows = []
    # iplik/ham kartları (modelin HAMLAR'ı)
    for hk in ham_kodlu:
        stok_kart_rows.append((f"STK-{hk[0]}", hk[1], "iplik", "kg", 500.0,
                               m2(r2.uniform(800, 6000)), m2(r2.uniform(85, 160))))
    # kimyasallar
    for k in KIMYASALLAR:
        stok_kart_rows.append((f"STK-{k[0]}", k[1], "boya_kimyasal", "kg", 200.0,
                               m2(r2.uniform(100, 3000)), m2(k[3])))
    stok_kart_rows.append(("STK-AMB-01", "Karton Koli", "yardimci", "adet", 500.0,
                           m2(r2.uniform(1000, 5000)), 12.0))
    stok_kart_rows.append(("STK-AMB-02", "Streç Film", "yardimci", "kg", 100.0,
                           m2(r2.uniform(200, 900)), 45.0))
    con.executemany("INSERT INTO stok_kartlari VALUES (?,?,?,?,?,?,?)", stok_kart_rows)
    stok_kodlari = [s[0] for s in stok_kart_rows]
    kimyasal_stok = [f"STK-{k[0]}" for k in KIMYASALLAR]
    iplik_stok = [f"STK-{hk[0]}" for hk in ham_kodlu]
    iplik_stok_by_ad = {hk[1]: f"STK-{hk[0]}" for hk in ham_kodlu}

    # stok hareketleri
    con.execute(
        "CREATE TABLE stok_hareketleri (id INTEGER PRIMARY KEY, tarih DATE, stok_kodu VARCHAR, "
        "depo_kodu VARCHAR, hareket_tipi VARCHAR, miktar DOUBLE, birim VARCHAR, "
        "birim_maliyet DOUBLE, kaynak VARCHAR, referans_no VARCHAR)"
    )
    sh_rows = []
    shid = 1
    # iplik/kimyasal girişleri (satınalma kaynaklı)
    for _ in range(1000):
        sk = r2.choice(kimyasal_stok + iplik_stok)
        depo = "D03" if sk in kimyasal_stok else "D02"
        sh_rows.append((shid, d(r2.randint(0, SPAN)), sk, depo, "giris",
                        m2(r2.uniform(100, 2000)), "kg", m2(r2.uniform(10, 150)),
                        "satinalma", f"SAS-{r2.randint(1, 400):04d}"))
        shid += 1
    # üretim tüketimi (iplik + kimyasal çıkışı) — partiler bazlı, ham tüketimiyle tutarlı
    for p in partiler:
        # iplik çıkışı: partinin ham_ad'ına karşılık gelen stok (kg ~ parti kg)
        ipsk = iplik_stok_by_ad.get(p["ham_ad"])
        if ipsk:
            sh_rows.append((shid, _parse_tarih(p["tarih"]), ipsk, "D02", "cikis", m2(p["kg"]),
                            "kg", m2(r2.uniform(85, 160)), "uretim", p["parti_no"]))
            shid += 1
        # kimyasal çıkışı (partinin kg'ının küçük payı)
        sk = r2.choice(kimyasal_stok)
        sh_rows.append((shid, _parse_tarih(p["tarih"]), sk, "D03", "cikis",
                        m2(p["kg"] * r2.uniform(0.02, 0.08)), "kg", m2(r2.uniform(10, 150)),
                        "uretim", p["parti_no"]))
        shid += 1
    con.executemany("INSERT INTO stok_hareketleri VALUES (?,?,?,?,?,?,?,?,?,?)", sh_rows)

    # top stok (mamul rulolar) — parti başına 2-5 top
    con.execute(
        "CREATE TABLE top_stok (top_no VARCHAR PRIMARY KEY, parti_no VARCHAR, ham_ad VARCHAR, "
        "renk VARCHAR, en_cm INTEGER, boy_m DOUBLE, agirlik_kg DOUBLE, depo_kodu VARCHAR, "
        "kalite_sinifi VARCHAR, durum VARCHAR)"
    )
    top_rows = []
    tno = 1
    for p in partiler:
        if r2.random() > 0.5:  # partilerin ~yarısı için top kaydı (ölçek kontrolü)
            continue
        n_top = r2.randint(2, 5)
        kalan = p["kg"]
        for _ in range(n_top):
            agir = m2(max(20, kalan / n_top * r2.uniform(0.8, 1.2)))
            gramaj = p["gramaj"]
            boy = m2(agir / (gramaj / 1000.0 * (p["en_cm"] or 180) / 100.0)) if gramaj else agir * 5
            top_rows.append((f"TOP-{tno:05d}", p["parti_no"], p["ham_ad"], p["renk_ad"],
                             p["en_cm"] or 180, boy, agir, "D04",
                             r2.choices(["1.kalite", "2.kalite", "iskarta"], weights=[85, 12, 3])[0],
                             r2.choice(["depoda", "depoda", "sevk_edildi"])))
            tno += 1
    con.executemany("INSERT INTO top_stok VALUES (?,?,?,?,?,?,?,?,?,?)", top_rows)

    # sayım
    con.execute(
        "CREATE TABLE sayimlar (id INTEGER PRIMARY KEY, tarih DATE, depo_kodu VARCHAR, "
        "stok_kodu VARCHAR, sistem_miktar DOUBLE, sayilan_miktar DOUBLE, fark DOUBLE, aciklama VARCHAR)"
    )
    sayim_rows = []
    for syid in range(1, 151):
        sk = r2.choice(stok_kodlari)
        sistem = m2(r2.uniform(100, 3000))
        sayilan = m2(sistem * r2.uniform(0.95, 1.03))
        sayim_rows.append((syid, d(r2.randint(0, SPAN)), r2.choice([dd[0] for dd in DEPOLAR]),
                           sk, sistem, sayilan, m2(sayilan - sistem),
                           r2.choice(["", "", "fire", "hatalı giriş", "sayım düzeltme"])))
    con.executemany("INSERT INTO sayimlar VALUES (?,?,?,?,?,?,?,?)", sayim_rows)

    # iplik lotları — modelin iplik tedarikçilerinden
    con.execute(
        "CREATE TABLE iplik_lotlari (lot_no VARCHAR PRIMARY KEY, ham_kodu VARCHAR, "
        "tedarikci_kodu VARCHAR, giris_tarihi DATE, miktar_kg DOUBLE, bobin_adet INTEGER, "
        "birim_fiyat DOUBLE)"
    )
    iplik_lot_rows = []
    for i in range(1, 301):
        hk = r2.choice(ham_kodlu)
        iplik_lot_rows.append((f"ILOT-{i:05d}", hk[0], r2.choice(iplik_ted),
                               d(r2.randint(0, SPAN)), m2(r2.uniform(500, 3000)),
                               r2.randint(20, 120), m2(r2.uniform(85, 160))))
    con.executemany("INSERT INTO iplik_lotlari VALUES (?,?,?,?,?,?,?)", iplik_lot_rows)

    # ------------------------------------------------------------------ #
    # C6) BAKIM — makineleri modelin MAKINELER'ine bağla                  #
    # ------------------------------------------------------------------ #
    bakim_operatorler = [p[0] for p in tum_personel if p[3] == "Bakım"] or [uretim_personel[0][0]]
    con.execute(
        "CREATE TABLE bakim_planlari (id INTEGER PRIMARY KEY, makine VARCHAR, bakim_tipi VARCHAR, "
        "periyot_gun INTEGER, son_bakim DATE, sonraki_bakim DATE, sorumlu VARCHAR)"
    )
    bakim_plan_rows = []
    bpi = 1
    for m in makine_kodlari:
        per = r2.choice([30, 60, 90])
        son = d(r2.randint(0, 60))
        bakim_plan_rows.append((bpi, m, r2.choice(["periyodik", "kestirimci"]), per, son,
                                son + timedelta(days=per), r2.choice(bakim_operatorler)))
        bpi += 1
    con.executemany("INSERT INTO bakim_planlari VALUES (?,?,?,?,?,?,?)", bakim_plan_rows)

    con.execute(
        "CREATE TABLE ariza_kayitlari (ariza_no VARCHAR PRIMARY KEY, tarih DATE, makine VARCHAR, "
        "ariza_tipi VARCHAR, durus_dakika INTEGER, mudahale_eden VARCHAR, yedek_parca_maliyet DOUBLE, "
        "aciklama VARCHAR, durum VARCHAR)"
    )
    ARIZA_TIP = ["pompa arızası", "vana kaçağı", "sensör hatası", "rezistans", "motor rulman",
                 "PLC haberleşme", "sıcaklık sapması", "elektrik kesintisi"]
    ariza_rows = []
    # arızaları modelin "Arıza" nedenli duruşlarıyla hizala — bakımla tutarlı
    ariza_durus = [x for x in durus if x["neden"] == "Arıza"]
    for i, x in enumerate(ariza_durus, start=1):
        ariza_rows.append((f"ARZ-{i:04d}", _parse_tarih(x["tarih"]), x["makine"],
                           r2.choice(ARIZA_TIP), int(x["sure_dk"]), r2.choice(bakim_operatorler),
                           m2(r2.uniform(0, 8000)), x["aciklama"],
                           r2.choice(["kapandi", "kapandi", "acik"])))
    con.executemany("INSERT INTO ariza_kayitlari VALUES (?,?,?,?,?,?,?,?,?)", ariza_rows)

    # ------------------------------------------------------------------ #
    # C7) ALIŞ / SATIŞ + İRSALİYE + FATURA + MUHASEBE                     #
    #     Satış: partiler ciro_tl'sinden (müşteri × ay). Enerji maliyeti:  #
    #     tesis+partiler enerji toplamından. Mizan dengeli.                #
    # ------------------------------------------------------------------ #
    KDV_ORANI = 0.20

    # teklifler (müşteri bazlı — logic korunur)
    con.execute(
        "CREATE TABLE teklifler (teklif_no VARCHAR PRIMARY KEY, tarih DATE, musteri_kodu VARCHAR, "
        "ham_ad VARCHAR, renk VARCHAR, miktar_kg DOUBLE, birim_fiyat DOUBLE, para_birimi VARCHAR, "
        "gecerlilik DATE, durum VARCHAR)"
    )
    teklif_rows = []
    for i in range(1, 151):
        mk = r2.choice(musteri_kodlari)
        t0 = r2.randint(0, SPAN - 15)
        _td = d(t0)
        teklif_rows.append((f"TKL-2026-{i:04d}", _td, mk, r2.choice(B.HAMLAR)["ad"],
                            r2.choice(B.RENKLER)["ad"], m2(r2.uniform(300, 3000)),
                            m2(r2.uniform(11, 15)), "TL", d(t0 + 15),
                            r2.choices(["kabul", "beklemede", "red"], weights=[55, 30, 15])[0]))
    con.executemany("INSERT INTO teklifler VALUES (?,?,?,?,?,?,?,?,?,?)", teklif_rows)

    # satınalma siparişleri (tedarikçiden iplik/kimyasal) — stok girişleriyle tutarlı
    con.execute(
        "CREATE TABLE satinalma_siparisleri (sas_no VARCHAR PRIMARY KEY, tarih DATE, tedarikci_kodu VARCHAR, "
        "stok_kodu VARCHAR, miktar DOUBLE, birim VARCHAR, birim_fiyat DOUBLE, tutar DOUBLE, "
        "para_birimi VARCHAR, teslim_tarihi DATE, durum VARCHAR)"
    )
    sas_rows = []
    for i in range(1, 401):
        tur = r2.choice(["iplik", "iplik", "boyarmadde", "kimyasal", "yardimci"])
        if tur == "iplik":
            ted = r2.choice(iplik_ted)
            sk = r2.choice(iplik_stok)
        elif tur in ("boyarmadde", "kimyasal"):
            ted = r2.choice(ted_by_tur.get("kimyasal", ted_kodlari) + ted_by_tur.get("boyarmadde", []))
            sk = r2.choice(kimyasal_stok)
        else:
            ted = r2.choice(ted_by_tur.get("yardimci", ted_kodlari))
            sk = r2.choice(["STK-AMB-01", "STK-AMB-02"])
        mik = m2(r2.uniform(200, 3000))
        bf = m2(r2.uniform(10, 150))
        t0 = r2.randint(0, SPAN)
        sas_rows.append((f"SAS-{i:04d}", d(t0), ted, sk, mik, "kg", bf, m2(mik * bf),
                         "TL", d(t0 + r2.randint(5, 30)),
                         r2.choice(["teslim", "teslim", "bekliyor"])))
    con.executemany("INSERT INTO satinalma_siparisleri VALUES (?,?,?,?,?,?,?,?,?,?,?)", sas_rows)

    # ---- SATIŞ FATURALARI: partilerin ciro_tl'sinden (müşteri × ay) ---- #
    con.execute(
        "CREATE TABLE faturalar (fatura_no VARCHAR PRIMARY KEY, tarih DATE, tur VARCHAR, "
        "cari_kodu VARCHAR, cari_tip VARCHAR, matrah DOUBLE, kdv_orani DOUBLE, kdv_tutari DOUBLE, "
        "toplam DOUBLE, para_birimi VARCHAR, kur DOUBLE, e_fatura_ettn VARCHAR, senaryo VARCHAR, "
        "irsaliye_no VARCHAR, durum VARCHAR, matrah_tl DOUBLE, kdv_tl DOUBLE, toplam_tl DOUBLE)"
    )
    con.execute(
        "CREATE TABLE fatura_satirlari (id INTEGER PRIMARY KEY, fatura_no VARCHAR, stok_kodu VARCHAR, "
        "aciklama VARCHAR, miktar DOUBLE, birim VARCHAR, birim_fiyat DOUBLE, tutar DOUBLE, kdv_orani DOUBLE)"
    )
    # müşteri × YIL × ay bazında ciro + kg topla (çok-yıl: yıl olmadan yıllar birleşirdi!)
    mus_ay = defaultdict(lambda: dict(ciro=0.0, kg=0.0, tarih=None))
    for p in partiler:
        k = (p["musteri_kod"], p["yil"], p["ay"])
        rec = mus_ay[k]
        rec["ciro"] += p["ciro_tl"]
        rec["kg"] += p["kg"]
        pt = _parse_tarih(p["tarih"])
        if rec["tarih"] is None or pt > rec["tarih"]:
            rec["tarih"] = pt  # ay-sonu faturası ~ ayın son üretim tarihi

    fatura_rows = []
    fsat_rows = []
    fsid = 1
    fno_ct = 1
    for (mus, yil, ay), rec in sorted(mus_ay.items()):
        matrah = m2(rec["ciro"])
        kdv = m2(matrah * KDV_ORANI)
        fatura_no = f"SFT-{yil}-{fno_ct:04d}"
        fatura_rows.append((fatura_no, rec["tarih"], "satis", mus, "musteri", matrah, KDV_ORANI,
                            kdv, m2(matrah + kdv), "TL", 1.0, ettn(), "TEMELFATURA",
                            f"IRS-C-{fno_ct:04d}", "onaylandi", matrah, kdv, m2(matrah + kdv)))
        birim = m2(matrah / rec["kg"]) if rec["kg"] else 0.0
        fsat_rows.append((fsid, fatura_no, "STK-MAM", f"Boyalı kumaş sevkiyatı ({ay}. ay)",
                          m2(rec["kg"]), "kg", birim, matrah, KDV_ORANI))
        fsid += 1
        fno_ct += 1

    # ---- ALIŞ FATURALARI: satınalmadan (teslim edilenler) ---- #
    ano = 1
    for sas in sas_rows:
        if sas[10] != "teslim":
            continue
        matrah = sas[7]
        kdv = m2(matrah * KDV_ORANI)
        fatura_no = f"AFT-2026-{ano:04d}"
        fatura_rows.append((fatura_no, sas[9], "alis", sas[2], "tedarikci", matrah, KDV_ORANI,
                            kdv, m2(matrah + kdv), "TL", 1.0, ettn(), "TEMELFATURA", "",
                            "onaylandi", matrah, kdv, m2(matrah + kdv)))
        fsat_rows.append((fsid, fatura_no, sas[3], "Hammadde/kimyasal alımı", sas[4], sas[5],
                          sas[6], matrah, KDV_ORANI))
        fsid += 1
        ano += 1
    con.executemany("INSERT INTO faturalar VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", fatura_rows)
    con.executemany("INSERT INTO fatura_satirlari VALUES (?,?,?,?,?,?,?,?,?)", fsat_rows)

    # irsaliyeler (çıkış = satış faturası, giriş = mal kabul)
    con.execute(
        "CREATE TABLE irsaliyeler (irsaliye_no VARCHAR PRIMARY KEY, tarih DATE, tur VARCHAR, "
        "cari_kodu VARCHAR, cari_tip VARCHAR, arac_plaka VARCHAR, sofor VARCHAR, "
        "toplam_kg DOUBLE, toplam_top INTEGER, referans_no VARCHAR, fatura_no VARCHAR, durum VARCHAR)"
    )
    irs_rows = []
    plaka = lambda: f"{r2.randint(1, 81):02d} {r2.choice('ABCDEFHK')}{r2.choice('ABCDEFHK')} {r2.randint(100, 999)}"
    soforlar = ["Recep Yol", "İsmail Tır", "Necati Kamyon", "Ali Şoför"]
    ino = 1
    for f in fatura_rows:
        if f[2] == "satis":
            irs_rows.append((f"IRS-C-{ino:04d}", f[1], "cikis", f[3], "musteri", plaka(),
                             r2.choice(soforlar), m2(f[5] / 12.0), r2.randint(3, 20), f[0], f[0],
                             "faturalandi"))
            ino += 1
    for sas in sas_rows:
        if sas[10] != "teslim":
            continue
        irs_rows.append((f"IRS-G-{ino:04d}", sas[9], "giris", sas[2], "tedarikci", plaka(),
                         r2.choice(soforlar), sas[4], 0, sas[0], "", "mal_kabul"))
        ino += 1
    con.executemany("INSERT INTO irsaliyeler VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", irs_rows)

    # cari hareketler (fatura borç/alacak + tahsilat/ödeme)
    con.execute(
        "CREATE TABLE cari_hareketler (id INTEGER PRIMARY KEY, tarih DATE, cari_kodu VARCHAR, "
        "cari_tip VARCHAR, evrak_tip VARCHAR, evrak_no VARCHAR, borc DOUBLE, alacak DOUBLE, "
        "para_birimi VARCHAR, aciklama VARCHAR)"
    )
    cari_rows = []
    chid = 1
    for f in fatura_rows:
        tl = f[17]
        if f[2] == "satis":  # müşteri borçlanır
            cari_rows.append((chid, f[1], f[3], "musteri", "fatura", f[0], tl, 0.0, "TL",
                              "Satış faturası")); chid += 1
            if r2.random() < 0.7:  # tahsilat
                t = f[1] + timedelta(days=r2.randint(15, 75))
                cari_rows.append((chid, min(t, END), f[3], "musteri", "tahsilat", f[0], 0.0, tl, "TL",
                                  "Tahsilat")); chid += 1
        else:  # alış → tedarikçiye borçlanılır
            cari_rows.append((chid, f[1], f[3], "tedarikci", "fatura", f[0], 0.0, tl, "TL",
                              "Alış faturası")); chid += 1
            if r2.random() < 0.7:
                t = f[1] + timedelta(days=r2.randint(15, 60))
                cari_rows.append((chid, min(t, END), f[3], "tedarikci", "odeme", f[0], tl, 0.0, "TL",
                                  "Ödeme")); chid += 1
    con.executemany("INSERT INTO cari_hareketler VALUES (?,?,?,?,?,?,?,?,?,?)", cari_rows)

    # ---- YEVMİYE: (a) satış (b) ENERJİ maliyeti (c) bordro (d) iplik alımı ---- #
    con.execute(
        "CREATE TABLE yevmiye_fisleri (fis_no VARCHAR PRIMARY KEY, tarih DATE, fis_tipi VARCHAR, "
        "aciklama VARCHAR, toplam_borc DOUBLE, toplam_alacak DOUBLE)"
    )
    con.execute(
        "CREATE TABLE yevmiye_satirlari (id INTEGER PRIMARY KEY, fis_no VARCHAR, hesap_kodu VARCHAR, "
        "aciklama VARCHAR, borc DOUBLE, alacak DOUBLE)"
    )
    yev_rows = []
    yevs_rows = []
    yid = 1
    ysid = 1

    def _fis(tarih, tip, aciklama, satirlar):
        """satirlar: [(hesap, aciklama, borc, alacak)] → dengeli fiş ekler."""
        nonlocal yid, ysid
        borc_top = m2(sum(s[2] for s in satirlar))
        alacak_top = m2(sum(s[3] for s in satirlar))
        fis_no = f"YEV-{yid:05d}"
        yev_rows.append((fis_no, tarih, tip, aciklama, borc_top, alacak_top))
        for hesap, ac, borc, alacak in satirlar:
            yevs_rows.append((ysid, fis_no, hesap, ac, m2(borc), m2(alacak)))
            ysid += 1
        yid += 1

    # (a) + (d) fatura tahakkukları
    for f in fatura_rows:
        matrah_tl, kdv_tl, toplam_tl = f[15], f[16], f[17]
        if f[2] == "satis":
            _fis(f[1], "mahsup", f"Satış faturası {f[0]}", [
                ("120", "Alıcılar", toplam_tl, 0.0),
                ("600", "Yurtiçi Satışlar", 0.0, matrah_tl),
                ("391", "Hesaplanan KDV", 0.0, kdv_tl)])
        else:  # (d) iplik/kimyasal alımı
            _fis(f[1], "mahsup", f"Alış faturası {f[0]}", [
                ("150", "İlk Madde ve Malzeme", matrah_tl, 0.0),
                ("191", "İndirilecek KDV", kdv_tl, 0.0),
                ("320", "Satıcılar", 0.0, toplam_tl)])

    # (b) ENERJİ maliyeti — aylık elektrik/doğalgaz/su/atıksu TL'si (tesis+partiler tutarlı)
    #     Tutar: partilerin o ay enerji_toplam_tl'si (proses) — 730 Genel Üretim Giderleri.
    enerji_ay = defaultdict(lambda: dict(el=0.0, dg=0.0, su=0.0, atiksu=0.0, tarih=None))
    for p in partiler:
        e = enerji_ay[(p["yil"], p["ay"])]
        e["el"] += p["elektrik_tl"]; e["dg"] += p["dogalgaz_tl"]
        e["su"] += p["su_tl"]; e["atiksu"] += p["atiksu_tl"]
        pt = _parse_tarih(p["tarih"])
        if e["tarih"] is None or pt > e["tarih"]:
            e["tarih"] = pt
    for yil, ay in AY_ANAHTAR:
        e = enerji_ay[(yil, ay)]
        el = m2(e["el"]); dg = m2(e["dg"]); su = m2(e["su"]); atiksu = m2(e["atiksu"])
        matrah = m2(el + dg + su + atiksu)
        kdv = m2(matrah * KDV_ORANI)
        _fis(e["tarih"], "mahsup", f"{yil}-{ay:02d} enerji/su gideri tahakkuku", [
            ("730", "Genel Üretim Giderleri - Elektrik", el, 0.0),
            ("730", "Genel Üretim Giderleri - Doğalgaz", dg, 0.0),
            ("730", "Genel Üretim Giderleri - Su", su, 0.0),
            ("730", "Genel Üretim Giderleri - Atıksu", atiksu, 0.0),
            ("191", "İndirilecek KDV", kdv, 0.0),
            ("320", "Satıcılar (Enerji/Su tedarikçileri)", 0.0, m2(matrah + kdv))])

    # (c) bordro tahakkuku (aylık) — 720 Direkt İşçilik + 361 SGK + 320 net
    for yil, ay in AY_ANAHTAR:
        donem = f"{yil}-{ay:02d}"
        tarih = date(yil, ay, 28)
        # dönem bordrosunu topla
        d_brut = d_sgk_isci = d_issiz = d_gv = d_damga = d_mesai = d_prim = d_net = d_sgkisv = 0.0
        for row in bordro_rows:
            if row[1] != donem:
                continue
            d_brut += row[3]; d_sgk_isci += row[4]; d_issiz += row[5]; d_gv += row[6]
            d_damga += row[7]; d_mesai += row[8]; d_prim += row[9]; d_net += row[10]; d_sgkisv += row[11]
        d_brut = m2(d_brut); d_mesai = m2(d_mesai); d_prim = m2(d_prim); d_sgkisv = m2(d_sgkisv)
        d_net = m2(d_net); d_sgk_isci = m2(d_sgk_isci); d_issiz = m2(d_issiz); d_gv = m2(d_gv); d_damga = m2(d_damga)
        borc = m2(d_brut + d_mesai + d_prim + d_sgkisv)
        # kesintiler + net + işveren SGK = borç (dengeli)
        _fis(tarih, "mahsup", f"{donem} bordro tahakkuku", [
            ("720", "Direkt İşçilik Gideri (brüt+mesai+prim)", m2(d_brut + d_mesai + d_prim), 0.0),
            ("720", "SGK İşveren Payı", d_sgkisv, 0.0),
            ("335", "Personele Borçlar (net ödenecek)", 0.0, d_net),
            ("361", "Ödenecek SGK Kesintileri", 0.0, m2(d_sgk_isci + d_issiz + d_sgkisv)),
            ("360", "Ödenecek Vergi ve Fonlar", 0.0, m2(d_gv + d_damga))])
    # (e) KİMYASAL SARFİYATI — aylık boya/yardımcı kimyasal maliyeti (partiler.kimyasal_tl):
    #     730 Genel Üretim Giderleri - Kimyasal (borç) / 150 İlk Madde ve Malzeme (alacak,
    #     stoktan çıkış). Böylece SMM + gerçek marj kimyasalı da içerir (fason maliyet kalemi).
    kimyasal_ay = defaultdict(lambda: dict(tl=0.0, tarih=None))
    for p in partiler:
        k = kimyasal_ay[(p["yil"], p["ay"])]
        k["tl"] += p.get("kimyasal_tl", 0.0)
        pt = _parse_tarih(p["tarih"])
        if k["tarih"] is None or pt > k["tarih"]:
            k["tarih"] = pt
    for yil, ay in AY_ANAHTAR:
        k = kimyasal_ay[(yil, ay)]
        tl = m2(k["tl"])
        if tl <= 0:
            continue
        _fis(k["tarih"], "mahsup", f"{yil}-{ay:02d} kimyasal sarfiyatı (proses)", [
            ("730", "Genel Üretim Giderleri - Kimyasal", tl, 0.0),
            ("150", "İlk Madde ve Malzeme (kimyasal çıkışı)", 0.0, tl)])

    con.executemany("INSERT INTO yevmiye_fisleri VALUES (?,?,?,?,?,?)", yev_rows)
    con.executemany("INSERT INTO yevmiye_satirlari VALUES (?,?,?,?,?,?)", yevs_rows)

    # banka hareketleri
    con.execute(
        "CREATE TABLE banka_hareketleri (id INTEGER PRIMARY KEY, tarih DATE, banka_kodu VARCHAR, "
        "islem_tipi VARCHAR, tutar DOUBLE, para_birimi VARCHAR, cari_kodu VARCHAR, aciklama VARCHAR)"
    )
    banka_rows = []
    bkid = 1
    for c in cari_rows:
        if c[4] in ("tahsilat", "odeme") and r2.random() < 0.6:
            bk = r2.choice([b[0] for b in BANKALAR])
            tip = "gelen_havale" if c[4] == "tahsilat" else "giden_havale"
            tutar = c[7] if c[4] == "tahsilat" else c[6]
            banka_rows.append((bkid, c[1], bk, tip, tutar, c[8], c[2], f"{c[4]} - {c[2]}"))
            bkid += 1
    con.executemany("INSERT INTO banka_hareketleri VALUES (?,?,?,?,?,?,?,?)", banka_rows)

    # kasa hareketleri
    con.execute(
        "CREATE TABLE kasa_hareketleri (id INTEGER PRIMARY KEY, tarih DATE, islem_tipi VARCHAR, "
        "tutar DOUBLE, aciklama VARCHAR)"
    )
    kasa_rows = []
    for kaid in range(1, 401):
        tip = r2.choice(["tahsilat", "tediye"])
        kasa_rows.append((kaid, d(r2.randint(0, SPAN)), tip, m2(r2.uniform(500, 25000)),
                          r2.choice(["nakit tahsilat", "kırtasiye", "yakıt", "avans", "küçük gider"])))
    con.executemany("INSERT INTO kasa_hareketleri VALUES (?,?,?,?,?)", kasa_rows)

    # çek/senet — alınan (müşteri) / verilen (tedarikçi)
    con.execute(
        "CREATE TABLE cek_senetler (id INTEGER PRIMARY KEY, tur VARCHAR, yon VARCHAR, tutar DOUBLE, "
        "para_birimi VARCHAR, kesim_tarihi DATE, vade DATE, cari_kodu VARCHAR, banka VARCHAR, durum VARCHAR)"
    )
    cs_rows = []
    for csid in range(1, 251):
        yon = r2.choice(["alinan", "verilen"])
        cari = r2.choice(musteri_kodlari) if yon == "alinan" else r2.choice(ted_kodlari)
        t0 = r2.randint(0, SPAN - 30)
        cs_rows.append((csid, r2.choice(["cek", "senet"]), yon, m2(r2.uniform(10000, 250000)),
                        "TL", d(t0), d(t0 + r2.randint(30, 120)), cari,
                        r2.choice([b[1] for b in BANKALAR]),
                        r2.choices(["portfoyde", "tahsil", "ciro", "karsiliksiz"],
                                   weights=[40, 40, 15, 5])[0]))
    con.executemany("INSERT INTO cek_senetler VALUES (?,?,?,?,?,?,?,?,?,?)", cs_rows)

    # fiyat listesi — müşteri fiyat bandına hizalı (model birim_fiyat × 10 fason kg→TL)
    con.execute(
        "CREATE TABLE fiyat_listesi (id INTEGER PRIMARY KEY, gecerli_tarih DATE, ham_ad VARCHAR, "
        "renk_derinlik VARCHAR, birim_fiyat_kg DOUBLE, para_birimi VARCHAR)"
    )
    fl_rows = []
    flid = 1
    for h in B.HAMLAR:
        for renk in ("Beyaz", "Açık", "Orta", "Koyu", "Siyah"):
            fl_rows.append((flid, date(2026, 1, 1), h["ad"], renk,
                            m2(r2.uniform(11, 15)), "TL"))
            flid += 1
    con.executemany("INSERT INTO fiyat_listesi VALUES (?,?,?,?,?,?)", fl_rows)

    con.execute("COMMIT")

    # ════════════════════════════════════════════════════════════════════ #
    # ÖZET                                                                   #
    # ════════════════════════════════════════════════════════════════════ #
    ozet = [
        ("=== ÜRETİM/OEE (model) ===",),
        "partiler", "makine_duruslari", "tamir_rework", "lab_olcumleri", "oee_vardiya",
        "uretim_aylik_ozet", "tesis_enerji_aylik",
        ("=== ENERJİ-MUHASEBE (YGG) ===",),
        "tep_ozet", "yakit_karmasi", "makine_enerji_aylik", "oek_pareto", "cusum",
        "sevkiyat_aylik", "su_bolum",
        ("=== REFERANS ===",),
        "musteriler", "makineler", "ham_kartlari", "kimyasallar", "tedarikciler",
        "hesap_plani", "banka_hesaplari", "depolar", "sertifikalar",
        ("=== İK ===",),
        "personel", "personel_ozluk", "puantaj", "bordro", "izinler",
        ("=== STOK ===",),
        "stok_kartlari", "stok_hareketleri", "top_stok", "sayimlar", "iplik_lotlari",
        ("=== BAKIM ===",),
        "bakim_planlari", "ariza_kayitlari",
        ("=== ALIŞ/SATIŞ/MUHASEBE ===",),
        "teklifler", "satinalma_siparisleri", "irsaliyeler", "faturalar", "fatura_satirlari",
        "cari_hareketler", "yevmiye_fisleri", "yevmiye_satirlari", "banka_hareketleri",
        "kasa_hareketleri", "cek_senetler", "fiyat_listesi",
    ]
    toplam_satir = 0
    tablo_sayisi = 0
    for t in ozet:
        if isinstance(t, tuple):
            print(f"\n{t[0]}")
            continue
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        toplam_satir += n
        tablo_sayisi += 1
        print(f"  {t:24s} {n:>7d} satır")
    print(f"\n  {'TOPLAM':24s} {toplam_satir:>7d} satır  ({tablo_sayisi} tablo)")
    # 🔴 ERP GENİŞLETMESİ — `build()` başta `DB.unlink()` yapar, yani bu çağrı
    # OLMAZSA genişletmenin 32 tablosu her yeniden üretimde **sessizce yok olur**.
    # *Bir üretecin çağrılmaması, onun yazılmamasıyla aynı sonucu verir — ama teşhisi
    # çok daha zordur, çünkü dosya yerinde durur.*
    from genisletme import genislet
    print("\n=== ERP GENİŞLETMESİ ===")
    for ad, adet in genislet(con).items():
        print(f"  {ad:28s} {adet:>8d} satır")

    con.close()
    print(f"OK → {DB}")


if __name__ == "__main__":
    build()
