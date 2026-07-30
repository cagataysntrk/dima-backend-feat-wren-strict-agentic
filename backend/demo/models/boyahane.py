# -*- coding: utf-8 -*-
"""Boyahane üretim + enerji + OEE veri modeli (SENTETİK demo).

TÜM adlar ve sayılar KURGUSALDIR — hiçbir müşterinin gerçek verisi kullanılmaz.
Yalnızca STRÜKTÜR gerçek bir Egemen/ISO-50001 boyahane raporlama sistemine benzetilmiştir
(gerçekçi kolonlar: vardiya-bazlı OEE, ÇE/ÖEK/TEP enerji muhasebesi, ΔE kalite). Değerler
sabit tohumlu RNG ile iç-tutarlı üretilir (enerji ∝ kapasite×üretim, GES artışı, yakıt
dönüşümü) → tekrar üretilebilir. 8 gömülü bulgu (demo senaryoları) generatörde tohumludur.

build_data.py bu modülü çağırır → partiler/oee/duruş/tamir/lab + enerji tablolarını (sözlük
listeleri) döner; build_data DuckDB'ye yazar + ERP katmanını (cari/fatura/bordro/stok) bunun
ÜZERİNE tutarlı biçimde kurar.
"""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, datetime, timedelta

RNG = random.Random(20260401)  # gen_config ile aynı tohum → mutabık

# ══════════════════════════════════════════════════════════════
# 1. SABİTLER (gerçek dosyalardan)
# ══════════════════════════════════════════════════════════════
# makine → hat + teknik parametre (Sabitler + Makine Bazlı Tüketim)
MAKINELER = {
    "RAM-1":            dict(hat="RAM 1",         teorik_hiz=34.0, kapasite_kg=1600, en_cm=190),
    "RAM-2":            dict(hat="RAM 2",         teorik_hiz=34.0, kapasite_kg=1600, en_cm=190),
    "RAM-3":            dict(hat="RAM 3",         teorik_hiz=34.0, kapasite_kg=1500, en_cm=185),
    "SANTEX":           dict(hat="Kuru Terbiye",  teorik_hiz=28.0, kapasite_kg=1200, en_cm=180),
    "ŞARDON-1":         dict(hat="Kuru Terbiye",  teorik_hiz=22.0, kapasite_kg=800,  en_cm=170),
    "FERRARO SANFOR-1": dict(hat="Kuru Terbiye",  teorik_hiz=26.0, kapasite_kg=1000, en_cm=180),
    "DİJİTAL BASKI":    dict(hat="Dijital Baskı", teorik_hiz=12.0, kapasite_kg=400,  en_cm=160),
    "ROTASYON BASKI":   dict(hat="Rotasyon Baskı", teorik_hiz=30.0, kapasite_kg=900, en_cm=175),
    "KONTİNÜ YIKAMA":   dict(hat="Kontinü Hat",   teorik_hiz=32.0, kapasite_kg=1400, en_cm=185),
    "KONTİNÜ KASAR":    dict(hat="Kontinü Hat",   teorik_hiz=30.0, kapasite_kg=1300, en_cm=185),
    "ÖRGÜ HAT":         dict(hat="Örgü",          teorik_hiz=18.0, kapasite_kg=700,  en_cm=0),
}
# makinenin ait olduğu ÖEK bölümü (enerji Pareto için)
MAKINE_BOLUM = {
    "RAM-1": "Boyahane", "RAM-2": "Boyahane", "RAM-3": "Boyahane",
    "SANTEX": "Kuru Terbiye", "ŞARDON-1": "Kuru Terbiye", "FERRARO SANFOR-1": "Kuru Terbiye",
    "DİJİTAL BASKI": "Baskı", "ROTASYON BASKI": "Baskı",
    "KONTİNÜ YIKAMA": "Kontinü Hat", "KONTİNÜ KASAR": "Kontinü Hat", "ÖRGÜ HAT": "Örgü",
}

VARDIYALAR = {1: dict(bas=8, ad="1. Vardiya (08-16)"), 2: dict(bas=16, ad="2. Vardiya (16-24)"),
              3: dict(bas=0, ad="3. Vardiya (00-08)")}
VS_DK = 480    # vardiya süresi
PID_DK = 40    # planlı duruş (30 yemek + 10 mola)

DURUS_NEDENLERI = ["Planlı Bakım", "Arıza", "Malzeme/Parti Bekleme", "Renk/Parti Değişimi",
                   "Kalite Kontrol Duruşu", "Enerji Kesintisi", "Diğer"]

# NOT: Tüm adlar/değerler SENTETİKtir — müşterinin gerçek verisi KULLANILMAZ (kurgusal).
MUSTERILER = [
    dict(kod="M1001", ad="AKDENİZ ÖRME TEKSTİL A.Ş.", tolerans=1.0, fiyat=1.35, pay=0.14),
    dict(kod="M1002", ad="EGE KNIT DIŞ TİCARET LTD. ŞTİ.", tolerans=1.2, fiyat=1.28, pay=0.19),
    dict(kod="M1003", ad="MAVİ İPLİK KONFEKSİYON A.Ş.", tolerans=0.6, fiyat=1.42, pay=0.11),
    dict(kod="M1004", ad="ANADOLU KUMAŞ SAN. TİC. LTD.", tolerans=1.5, fiyat=1.15, pay=0.13),
    dict(kod="M1005", ad="YILDIZ TEKSTİL İHRACAT A.Ş.", tolerans=1.2, fiyat=1.22, pay=0.12),
    dict(kod="M1006", ad="DENİZ GARMENT SAN. A.Ş.", tolerans=0.8, fiyat=1.38, pay=0.10),
    dict(kod="M1007", ad="TOROS ÖRME TİC. LTD. ŞTİ.", tolerans=1.4, fiyat=1.18, pay=0.09),
    dict(kod="M1008", ad="SİMGE TEKSTİL DIŞ TİC. A.Ş.", tolerans=0.9, fiyat=1.33, pay=0.12),
]
HAMLAR = [
    dict(ad="30/1 PMK PES ELASTAN SUPREM", grup="Örme Kumaş", gramaj=215, zorluk=1.00),
    dict(ad="36/1 PENYE FULL LYCRA SUPREM", grup="Örme Kumaş", gramaj=185, zorluk=1.15),
    dict(ad="70/68/2 PA FULL LYCRA", grup="Örme Kumaş", gramaj=200, zorluk=1.25),
    dict(ad="20/1 OE RİNG SUPREM", grup="Örme Kumaş", gramaj=240, zorluk=0.90),
    dict(ad="40/1 PENYE İNTERLOK", grup="Örme Kumaş", gramaj=210, zorluk=1.05),
    dict(ad="30/1 %95 PMK %5 EA RİBANA", grup="Örme Kumaş", gramaj=230, zorluk=1.10),
    dict(ad="50/1 VİSKON JERSEY", grup="Örme Kumaş", gramaj=160, zorluk=1.20),
]
RENKLER = [
    dict(ad="Beyaz", derinlik="Beyaz", zorluk=0.85, su_carpan=0.90, kimyasal=0.7),
    dict(ad="Açık", derinlik="Açık", zorluk=0.95, su_carpan=1.00, kimyasal=0.9),
    dict(ad="Orta", derinlik="Orta", zorluk=1.05, su_carpan=1.10, kimyasal=1.0),
    dict(ad="Koyu", derinlik="Koyu", zorluk=1.20, su_carpan=1.25, kimyasal=1.3),
    dict(ad="Siyah", derinlik="Koyu", zorluk=1.30, su_carpan=1.35, kimyasal=1.5),
]
ASAMALAR = ["ÖN FİKSE", "HT BOYAMA", "YIKAMA", "KURUTMA", "SANFOR", "KASAR"]
PERSONEL = {1: ["HASAN ÖZER", "MURAT DEMİR", "SEDA YILDIZ"],
            2: ["AYLİN BULUT", "ERHAN GÜNŞEBER", "KEMAL ARSLAN"],
            3: ["OSMAN ÇELİK", "FATİH KAYA", "BURAK ŞAHİN"]}
TEDARIKCILER = [  # adlar kurgusal
    dict(kod="T-101", ad="KUZEY İPLİK SANAYİ A.Ş.", kalite=1.00, pay=0.28),
    dict(kod="T-204", ad="PAMUKKALE ÖRME LTD. ŞTİ.", kalite=1.00, pay=0.24),
    dict(kod="T-315", ad="SELÇUK TEKSTİL HAMMADDE A.Ş.", kalite=0.72, pay=0.18),  # SORUNLU (senaryo)
    dict(kod="T-427", ad="FIRAT İPLİK TİC. LTD.", kalite=1.02, pay=0.16),
    dict(kod="T-538", ad="GEDİZ ÖRME SAN. A.Ş.", kalite=0.98, pay=0.14),
]
TAMIR_SEBEPLERI = ["Renk Tutmadı (ΔE Yüksek)", "Abraj", "Leke", "En/Gramaj Sapması",
                   "Yıkama Haslığı Düşük", "Yüzey Hatası"]

# ── ÇOK-YIL AYLIK ÜRETİM + ENERJİ (2024 tam + 2025 tam + 2026 H1) — SENTETİK ──
# Sabit tohumlu RNG; iç-tutarlı (enerji ∝ kapasite×üretim). YoY hikayesi (YGG ile uyumlu):
# üretim ölçeği 2024<2025<2026, GES payı artar, biyokütle kazanı YALNIZ 2026 Nisan'da devrede.
# Tüm aylık config (yil, ay) ile anahtarlı. 2026 H1 büyüme eğrisi KORUNUR (_H1_2026).
YIL_AYLAR = {2024: range(1, 13), 2025: range(1, 13), 2026: range(1, 7)}
# yıl → (üretim ölçek çarpanı, GES aylık taban kWh, GES aylık ramp kWh, biyokütle başlangıç ayı[99=yok])
_YIL_PROFIL = {2024: (0.60, 6000, 1200, 99), 2025: (0.80, 20000, 2400, 99), 2026: (1.0, 30000, 26000, 4)}
AYLAR = range(1, 7)  # geriye-uyum sabiti (2026 H1); çok-yıl döngüsü YIL_AYLAR kullanır
_S = random.Random(424242)
_H1_2026 = [186000, 232000, 300000, 415000, 372000, 448000]  # 2026 H1 büyüme eğrisi (kg) — KORUNUR
_MEVSIM = [0.95, 0.98, 1.05, 1.10, 1.05, 1.02, 0.70, 0.72, 1.05, 1.12, 1.10, 1.00]  # 12-ay mevsimsellik

URETIM_KG, SEVKIYAT_KG = {}, {}
for _yil, _aylar in YIL_AYLAR.items():
    _olcek = _YIL_PROFIL[_yil][0]
    for _ay in _aylar:
        _base = _H1_2026[_ay - 1] if _yil == 2026 else round(300000 * _MEVSIM[_ay - 1] * _olcek)
        URETIM_KG[(_yil, _ay)] = round(_base * _S.uniform(0.97, 1.03), 1)
        SEVKIYAT_KG[(_yil, _ay)] = round(URETIM_KG[(_yil, _ay)] * _S.uniform(1.02, 1.10), 1)

_YOGUNLUK = {m: _S.uniform(14, 22) for m in MAKINELER}  # makine kWh/kg yoğunluğu (gerçekçi boyahane bandı)
ELEKTRIK = {m: {} for m in MAKINELER}
for _m in MAKINELER:
    for _yil, _aylar in YIL_AYLAR.items():
        _ref = URETIM_KG[(_yil, list(_aylar)[0])]  # yılın ilk ayı = referans
        for _ay in _aylar:
            ELEKTRIK[_m][(_yil, _ay)] = round(MAKINELER[_m]["kapasite_kg"] * _YOGUNLUK[_m]
                * (URETIM_KG[(_yil, _ay)] / _ref) * _S.uniform(0.90, 1.10), 1)
_DG_MAK = ["RAM-1", "RAM-2", "RAM-3", "SANTEX", "ROTASYON BASKI", "DİJİTAL BASKI"]  # ısıl proses
DOGALGAZ = {m: {k: round(ELEKTRIK[m][k] * _S.uniform(0.60, 0.80), 1) for k in ELEKTRIK[m]} for m in _DG_MAK}

TESIS = {}  # tesis geneli: şebeke + GES (yıla/aya göre artar) + su/atıksu
for _yil, _aylar in YIL_AYLAR.items():
    _gesbaz, _gesramp = _YIL_PROFIL[_yil][1], _YIL_PROFIL[_yil][2]
    for _ay in _aylar:
        _mak_el = sum(ELEKTRIK[m][(_yil, _ay)] for m in ELEKTRIK)
        _sebeke = round(_mak_el * _S.uniform(1.8, 2.1), 0)  # metrelenmeyen yükler (aydınlatma/ofis/osmoz)
        _ges = round((_gesbaz + _ay * _gesramp) * _S.uniform(0.90, 1.10), 0)
        _kuyu = round(URETIM_KG[(_yil, _ay)] * _S.uniform(0.075, 0.085), 0)  # ~77 lt/kg
        TESIS[(_yil, _ay)] = dict(sebeke=_sebeke, ges=_ges,
            fatura=round((_sebeke + _ges) * 3.96 * _S.uniform(0.95, 1.05), 0),  # ~ELEKTRIK_TL_KWH
            kuyu_su=_kuyu, atiksu=round(_kuyu * _S.uniform(0.97, 1.03), 0))
# katı yakıt (biyokütle kazanı yalnız 2026 Nisan'da) + buhar + araç yakıtı — hepsi kurgusal
KATI_YAKIT, BUHAR_TON, KAZAN_DOGALGAZ, MOTORIN_LT, BENZIN_LT = {}, {}, {}, {}, {}
for _yil, _aylar in YIL_AYLAR.items():
    _biyoay = _YIL_PROFIL[_yil][3]
    for _ay in _aylar:
        _u = URETIM_KG[(_yil, _ay)]
        KATI_YAKIT[(_yil, _ay)] = ((0, 0) if _ay < _biyoay else
            (round(_u * _S.uniform(0.70, 0.85), 0), round(_u * _S.uniform(4.5, 5.5), 0)))  # (kg, TL)
        BUHAR_TON[(_yil, _ay)] = round(_u * _S.uniform(0.0050, 0.0058), 1)
        KAZAN_DOGALGAZ[(_yil, _ay)] = round((90000 if _ay < _biyoay else 16000) * _S.uniform(0.85, 1.15), 0)
        MOTORIN_LT[(_yil, _ay)] = round(_S.uniform(600, 1400), 0)
        BENZIN_LT[(_yil, _ay)] = round(_S.uniform(1300, 1800), 0)

# birim fiyatlar (YGG) + TEP çevrim katsayıları (Sabitler)
ELEKTRIK_TL_KWH, DOGALGAZ_TL_SM3, SU_TL_M3, ATIKSU_TL_M3 = 3.96, 14.20, 12.50, 12.80
KIMYASAL_TL_KG = 6.5         # boya+yardımcı kimyasal maliyeti (kg mamul başına baz, ~₺/kg)
FASON_CARPAN = 25            # kg×birim_fiyat×FASON_CARPAN → ~32 ₺/kg fason (2024-25 örme boyama)
KWH_PER_TEP = 11630.0        # 1 TEP = 11.630 kWh
DOGALGAZ_KWH_SM3 = 10.6      # doğalgaz alt ısıl değeri
TEP_KATI_KG = 3684.0 / 1e7   # fındık kabuğu 3684 kcal/kg → TEP/kg
TEP_MOTORIN_LT = 10200.0 / 1e7
TEP_BENZIN_LT = 10480.0 / 1e7
tep_elektrik = lambda kwh: kwh / KWH_PER_TEP
tep_dogalgaz = lambda sm3: sm3 * DOGALGAZ_KWH_SM3 / KWH_PER_TEP

# 8 gömülü bulgu (demo senaryoları)
BULGULAR = {
    "vardiya_baslangic_kaybi_dk": {1: 72, 2: 18, 3: 25},  # B1
    "santex_enerji_carpan": 1.34,                          # B2
    "vardiya_rft_carpan": {1: 1.00, 2: 0.97, 3: 0.88},     # B3
    "renk_gecis_ceza_dk": 38,                              # B5
    "ram3_koyu_performans": 0.79,                          # B6
    "ram2_kalibrasyon_donemi": (3, 4), "ram2_kalibrasyon_carpan": 0.86,  # B8
}
AYLAR = range(1, 7)


def _is_gunleri(yil, ay):
    d = date(yil, ay, 1); out = []
    while d.month == ay:
        if d.weekday() < 6:  # Pazar hariç (Cumartesi çalışılır)
            out.append(d)
        d += timedelta(days=1)
    return out


def _agirlikli(liste):
    top = sum(x["pay"] for x in liste); r = RNG.random() * top; k = 0
    for x in liste:
        k += x["pay"]
        if r <= k:
            return x
    return liste[-1]


def uret():
    """Tüm üretim + enerji + OEE tablolarını (dict listeleri) üretir → build_data yazar."""
    partiler, durus, tamir, lab = [], [], [], []
    parti_no, siparis_no = 1000, 300

    for yil, ay in [(y, a) for y, _aa in YIL_AYLAR.items() for a in _aa]:
        gunler = _is_gunleri(yil, ay)
        hedef_kg = URETIM_KG[(yil, ay)]  # (yıl,ay) mutabık toplam üretim
        el_top = sum(ELEKTRIK[m][(yil, ay)] for m in ELEKTRIK)
        paylar = {m: ELEKTRIK[m][(yil, ay)] / el_top for m in ELEKTRIK}
        for gun in gunler:
            for makine, mk in MAKINELER.items():
                if makine not in ELEKTRIK:
                    continue
                gun_hedef = hedef_kg * paylar[makine] / len(gunler)
                if gun_hedef < 50:
                    continue
                for vard, vinfo in VARDIYALAR.items():
                    vardiya_hedef = gun_hedef / 3
                    if vardiya_hedef < 30:
                        continue
                    bas = datetime(gun.year, gun.month, gun.day, vinfo["bas"], 0, 0)
                    kayip = max(5, int(RNG.gauss(BULGULAR["vardiya_baslangic_kaybi_dk"][vard], 8)))
                    imlec = bas + timedelta(minutes=kayip)
                    vbitis = bas + timedelta(minutes=VS_DK)
                    onceki_renk = None
                    vardiya_uretim = 0.0

                    while imlec < vbitis - timedelta(minutes=25) and vardiya_uretim < vardiya_hedef:
                        ham = RNG.choice(HAMLAR); renk = RNG.choice(RENKLER)
                        mus = _agirlikli(MUSTERILER); ted = _agirlikli(TEDARIKCILER)
                        asama = RNG.choice(ASAMALAR[:3] if "RAM" in makine else ASAMALAR)
                        kalan = vardiya_hedef - vardiya_uretim
                        kg = round(RNG.uniform(0.40, 1.0) * mk["kapasite_kg"], 1)
                        if kg > kalan * 1.25:
                            kg = round(max(120, kalan), 1)
                        metre = (round(kg / (ham["gramaj"] / 1000) / (mk["en_cm"] / 100), 1)
                                 if mk["en_cm"] else round(kg * 3.2, 1))
                        hiz = mk["teorik_hiz"] / ham["zorluk"] / renk["zorluk"]
                        if makine == "RAM-3" and renk["derinlik"] == "Koyu":
                            hiz *= BULGULAR["ram3_koyu_performans"]
                        if makine == "RAM-2" and yil == 2026 and ay in BULGULAR["ram2_kalibrasyon_donemi"]:
                            hiz *= BULGULAR["ram2_kalibrasyon_carpan"]
                        if vard == 3:
                            hiz *= 0.94
                        hiz = max(6.0, hiz * RNG.gauss(1.0, 0.07))
                        sure_dk = metre / hiz if mk["en_cm"] else kg / (hiz / 3)
                        sure_dk = max(18, round(sure_dk, 1))

                        gecis = 0
                        if onceki_renk == "Koyu" and renk["derinlik"] in ("Beyaz", "Açık"):
                            gecis = max(12, int(RNG.gauss(BULGULAR["renk_gecis_ceza_dk"], 9)))
                        elif onceki_renk and onceki_renk != renk["derinlik"]:
                            gecis = max(3, int(RNG.gauss(11, 4)))
                        if gecis:
                            durus.append(dict(tarih=gun.isoformat(), makine=makine, hat=mk["hat"],
                                vardiya=vard, baslangic=imlec.strftime("%d.%m.%Y %H:%M:%S"),
                                sure_dk=gecis, neden="Renk/Parti Değişimi",
                                aciklama=f"{onceki_renk} → {renk['derinlik']} geçişi"))
                            imlec += timedelta(minutes=gecis)
                        if RNG.random() < 0.055:
                            nd = RNG.choice(["Arıza", "Malzeme/Parti Bekleme", "Kalite Kontrol Duruşu",
                                             "Enerji Kesintisi", "Diğer"])
                            sd = int(abs(RNG.gauss(26, 16))) + 5
                            durus.append(dict(tarih=gun.isoformat(), makine=makine, hat=mk["hat"],
                                vardiya=vard, baslangic=imlec.strftime("%d.%m.%Y %H:%M:%S"),
                                sure_dk=sd, neden=nd, aciklama=""))
                            imlec += timedelta(minutes=sd)
                        if imlec + timedelta(minutes=sure_dk) > vbitis:
                            break
                        giris = imlec; cikis = imlec + timedelta(minutes=sure_dk)

                        rft = 0.925 * ted["kalite"] * BULGULAR["vardiya_rft_carpan"][vard]
                        if renk["derinlik"] == "Koyu":
                            rft *= 0.94
                        if mus["tolerans"] < 0.8:
                            rft *= 0.86
                        if makine == "SANTEX":
                            rft *= 0.96
                        tuttu = RNG.random() < min(0.985, rft)
                        parti_no += 1
                        if RNG.random() < 0.35:
                            siparis_no += 1
                        pno = f"({yil}) {parti_no}"
                        dE = (round(abs(RNG.gauss(0.45, 0.22)), 2) if tuttu
                              else round(mus["tolerans"] + abs(RNG.gauss(0.55, 0.35)), 2))
                        lab_dE = round(abs(RNG.gauss(0.28, 0.12)), 2)
                        lab.append(dict(parti=pno, tarih=gun.isoformat(), makine=makine,
                            musteri=mus["kod"], renk=renk["ad"], ham=ham["ad"], lab_dE=lab_dE,
                            uretim_dE=dE, sapma=round(dE - lab_dE, 2), tolerans=mus["tolerans"]))
                        if not tuttu:
                            sebep = RNG.choice(TAMIR_SEBEPLERI)
                            if renk["derinlik"] == "Koyu" and RNG.random() < 0.4:
                                sebep = "Abraj"
                            if ted["kalite"] < 0.8 and RNG.random() < 0.45:
                                sebep = "En/Gramaj Sapması"
                            tamir.append(dict(parti=pno, tarih=gun.isoformat(), makine=makine,
                                hat=mk["hat"], vardiya=vard, musteri=mus["kod"], musteri_ad=mus["ad"],
                                tedarikci=ted["kod"], tedarikci_ad=ted["ad"], renk=renk["ad"],
                                renk_derinlik=renk["derinlik"], ham=ham["ad"], sebep=sebep,
                                ek_sure_dk=round(sure_dk * RNG.uniform(0.55, 0.95), 1), kg=kg,
                                dE=dE, tolerans=mus["tolerans"]))
                        enerji_carpan = BULGULAR["santex_enerji_carpan"] if makine == "SANTEX" else 1.0
                        su_lt = kg * RNG.gauss(69, 8) * renk["su_carpan"]
                        partiler.append(dict(parti_no=pno, siparis_no=f"({yil}) {siparis_no}",
                            yil=yil,  # agregasyon iç-kullanımı (partiler tablosuna yazılmaz; tarih yıl taşır)
                            tarih=gun.isoformat(), ay=ay, makine=makine, hat=mk["hat"], vardiya=vard,
                            vardiya_ad=vinfo["ad"], operator=RNG.choice(PERSONEL[vard]),
                            musteri_kod=mus["kod"], musteri_ad=mus["ad"], musteri_tolerans_dE=mus["tolerans"],
                            birim_fiyat=mus["fiyat"], tedarikci_kod=ted["kod"], tedarikci_ad=ted["ad"],
                            ham_ad=ham["ad"], ham_grup=ham["grup"], gramaj=ham["gramaj"], renk_ad=renk["ad"],
                            renk_derinlik=renk["derinlik"], asama=asama,
                            recete_kod=f"{mus['kod'][1:]}-{RNG.randint(1000, 9999)}", kg=kg, metre=metre,
                            en_cm=mk["en_cm"], giris_tarihi=giris.strftime("%d.%m.%Y %H:%M:%S"),
                            cikis_tarihi=cikis.strftime("%d.%m.%Y %H:%M:%S"), imalat_suresi_dk=sure_dk,
                            hiz_m_dk=round(metre / sure_dk, 2) if mk["en_cm"] else 0.0,
                            teorik_hiz_m_dk=mk["teorik_hiz"], ilk_seferde_tamam=int(tuttu),
                            uretim_dE=dE, lab_dE=lab_dE, su_lt=round(su_lt, 1),
                            enerji_carpan=round(enerji_carpan, 3),
                            # Kimyasal maliyet: reçete/renk-derinliği (RENKLER.kimyasal) × ham
                            # zorluğu × kg — koyu/zor renk daha çok boya+yardımcı tüketir.
                            kimyasal_tl=round(kg * renk["kimyasal"] * ham["zorluk"] * KIMYASAL_TL_KG, 2)))
                        onceki_renk = renk["derinlik"]; vardiya_uretim += kg
                        imlec = cikis + timedelta(minutes=RNG.randint(1, 4))
                    durus.append(dict(tarih=gun.isoformat(), makine=makine, hat=mk["hat"], vardiya=vard,
                        baslangic=bas.strftime("%d.%m.%Y %H:%M:%S"), sure_dk=kayip,
                        neden="Malzeme/Parti Bekleme", aciklama="Vardiya başlangıcı — ilk parti gecikmesi"))

    _enerji_dagit(partiler)
    oee = _oee_hesapla(partiler, durus)
    aylik = _aylik_ozet(partiler)
    tesis = _tesis_enerji(partiler)
    return dict(partiler=partiler, durus=durus, tamir=tamir, lab=lab,
                oee=oee, aylik=aylik, tesis=tesis)


def _enerji_dagit(P):
    """Aylık makine elektrik/gaz'ı partilere (kg×carpan payına göre) dağıt — aylık toplam korunur."""
    agir = defaultdict(float)
    for p in P:
        agir[(p["makine"], p["yil"], p["ay"])] += p["kg"] * p["enerji_carpan"]
    for p in P:
        k = (p["makine"], p["yil"], p["ay"]); pay = (p["kg"] * p["enerji_carpan"]) / agir[k] if agir[k] else 0
        el = ELEKTRIK.get(p["makine"], {}).get((p["yil"], p["ay"]), 0) * pay
        dg = DOGALGAZ.get(p["makine"], {}).get((p["yil"], p["ay"]), 0) * pay
        p["elektrik_kwh"] = round(el, 2); p["dogalgaz_sm3"] = round(dg, 2)
        p["elektrik_tl"] = round(el * ELEKTRIK_TL_KWH, 2); p["dogalgaz_tl"] = round(dg * DOGALGAZ_TL_SM3, 2)
        p["su_m3"] = round(p["su_lt"] / 1000, 3); p["su_tl"] = round(p["su_lt"] / 1000 * SU_TL_M3, 2)
        p["atiksu_tl"] = round(p["su_lt"] / 1000 * 0.978 * ATIKSU_TL_M3, 2)
        p["enerji_toplam_tl"] = round(p["elektrik_tl"] + p["dogalgaz_tl"] + p["su_tl"] + p["atiksu_tl"], 2)
        p["kwh_kg"] = round(el / p["kg"], 3) if p["kg"] else 0
        p["sm3_kg"] = round(dg / p["kg"], 3) if p["kg"] else 0
        p["lt_kg"] = round(p["su_lt"] / p["kg"], 1) if p["kg"] else 0
        p["tep"] = round(tep_elektrik(el) + tep_dogalgaz(dg), 5)
        p["ciro_tl"] = round(p["kg"] * p["birim_fiyat"] * FASON_CARPAN, 2)  # fason kg→TL (~32 ₺/kg)


def _oee_hesapla(P, D):
    vg = defaultdict(lambda: dict(kg=0.0, hatali=0.0, cal=0.0, teo=0.0, n=0, rft=0))
    for p in P:
        v = vg[(p["tarih"], p["makine"], p["hat"], p["vardiya"])]
        v["kg"] += p["kg"]; v["n"] += 1; v["rft"] += p["ilk_seferde_tamam"]; v["cal"] += p["imalat_suresi_dk"]
        if p["metre"] and p["teorik_hiz_m_dk"]:
            v["teo"] += p["metre"] / p["teorik_hiz_m_dk"]
        if not p["ilk_seferde_tamam"]:
            v["hatali"] += p["kg"]
    dg2 = defaultdict(float)
    for r in D:
        dg2[(r["tarih"], r["makine"], r["vardiya"])] += r["sure_dk"]
    rows = []
    for (tarih, makine, hat, vard), v in sorted(vg.items()):
        pzd = dg2.get((tarih, makine, vard), 0); pus = VS_DK - PID_DK; cu = max(0, pus - pzd)
        ev = cu / pus if pus else 0
        pv = min(1.0, (v["teo"] / v["cal"]) if v["cal"] else 0)
        ks = (v["kg"] - v["hatali"]) / v["kg"] if v["kg"] else 0
        rows.append(dict(tarih=tarih, makine=makine, hat=hat, vardiya=vard, vardiya_suresi_dk=VS_DK,
            planli_durus_dk=PID_DK, planli_uretim_suresi_dk=pus, plansiz_durus_dk=round(pzd, 1),
            calisma_suresi_dk=round(cu, 1), uretim_kg=round(v["kg"], 1), hatali_kg=round(v["hatali"], 1),
            parti_sayisi=v["n"], ilk_seferde_tamam=v["rft"],
            rft_yuzde=round(v["rft"] / v["n"] * 100, 1) if v["n"] else 0,
            kullanilabilirlik_EV=round(ev, 4), performans_PV=round(pv, 4), kalite_KS=round(ks, 4),
            OEE=round(ev * pv * ks * 100, 2)))
    return rows


def _aylik_ozet(P):
    a = defaultdict(lambda: dict(kg=0.0, el=0.0, dg=0.0, su=0.0, ciro=0.0, rework=0, tep=0.0))
    for p in P:
        x = a[(p["yil"], p["ay"])]
        x["kg"] += p["kg"]; x["el"] += p["elektrik_kwh"]; x["dg"] += p["dogalgaz_sm3"]
        x["su"] += p["su_lt"]; x["ciro"] += p["ciro_tl"]; x["tep"] += p["tep"]
        if not p["ilk_seferde_tamam"]:
            x["rework"] += 1
    return [dict(yil=k[0], ay=k[1], uretim_kg=round(v["kg"], 0), sevkiyat_kg=SEVKIYAT_KG[k],
        elektrik_kwh=round(v["el"], 0), dogalgaz_sm3=round(v["dg"], 0), su_m3=round(v["su"] / 1000, 0),
        kwh_kg=round(v["el"] / v["kg"], 3), sm3_kg=round(v["dg"] / v["kg"], 3),
        lt_kg=round(v["su"] / v["kg"], 1), rework_parti=v["rework"], ciro_tl=round(v["ciro"], 0),
        tep_proses=round(v["tep"], 1)) for k, v in sorted(a.items())]


def _tesis_enerji(P):
    kg_ya = defaultdict(float)
    for p in P:
        kg_ya[(p["yil"], p["ay"])] += p["kg"]
    rows = []
    for (yil, ay), t in sorted(TESIS.items()):
        kg = kg_ya[(yil, ay)]
        if kg <= 0:
            continue  # o (yıl,ay)'da üretim yoksa tesis satırı yazma
        top_el = t["sebeke"] + t["ges"]
        rows.append(dict(yil=yil, ay=ay, uretim_kg=round(kg, 0), sevkiyat_kg=SEVKIYAT_KG[(yil, ay)],
            sebeke_kwh=t["sebeke"], ges_kwh=t["ges"], toplam_elektrik_kwh=top_el, fatura_tl=t["fatura"],
            birim_tl_kwh=round(t["fatura"] / top_el, 3), elektrik_kg=round(top_el / kg, 3),
            ges_payi_yuzde=round(t["ges"] / top_el * 100, 1), kuyu_su_m3=t["kuyu_su"],
            atiksu_m3=t["atiksu"], su_lt_kg=round(t["kuyu_su"] * 1000 / kg, 1)))
    return rows
