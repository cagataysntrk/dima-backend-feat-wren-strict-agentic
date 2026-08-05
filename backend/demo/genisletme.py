"""ERP GENİŞLETMESİ — *holding ölçeğinde* bir kaynak sistemin geri kalanı.

## Neden ayrı bir modül, `build_data.py`'nin içine değil

`build_data.py` **1166 satır** ve üzerinde duran her şey ölçülmüş bir tabandır: 47 tablo,
441 sütun, ve korpusun **444 semantik vakası** onun ürettiği kataloğa dayanır. Oraya
dokunmak, ölçtüğümüz tabanı ölçüm sırasında oynatmak olurdu.

> ⚠ *Bir tabanı genişletirken onu yerinden oynatmak, genişlemenin kazancını ölçülemez
> hâle getirir.* Bu modül **yalnız ekler**: hiçbir mevcut tabloyu değiştirmez, silmez,
> yeniden üretmez.

## 🔴 Tasarım kuralı — TÜRETİLİR, UYDURULMAZ

Araştırma (Perforce · K2view · *"Referential Integrity: a Non-Negotiable"*) tek bir şey
söylüyor: sentetik kurumsal veride referans bütünlüğü **sonradan denetimle** değil,
**inşa gereği** sağlanır. Biz bir adım ötesini yapıyoruz — **nedensel** bütünlük:

| yeni tablo | neyden TÜRETİLİR | zincir gerçekten veride var mı |
|---|---|---|
| `musteri_sikayetleri` | `partiler.uretim_dE > musteri_tolerans_dE` | ✅ şikâyet, **gerçekten** sapan partiden doğar |
| `bakim_is_emirleri` | `ariza_kayitlari` | ✅ iş emri gerçek arızaya bağlı |
| `satis_siparisleri` | `partiler.siparis_no` | ✅ sipariş, üretilen partilerin **kendi** siparişi |
| `receteler` | `partiler.renk_ad × renk_derinlik` | ✅ boyahanenin gerçek reçete ekseni |
| `urun_maliyetleri` | `partiler`in enerji/kimyasal/kg'ı | ✅ maliyet gerçek tüketimden çıkar |
| `personel_hareketleri` | `personel_ozluk.ise_giris` | ✅ devir hızı gerçek özlükten |

⚠ **İki çapa ilk denemede YANLIŞ seçildi ve ölçümle düzeltildi** — ikisi de kodda
yazılı: `recete_kod` bir katalog sanılmıştı (29 065 değer taşıyor, parti kodu çıktı),
`giris_tarihi` diye bir alan yok (`ise_giris`). *Bir alanın adı, onun ne olduğunu
söylemez; ikisi de ancak veriye BAKILINCA anlaşıldı.*

*Rastgele üretilmiş bir şikâyet tablosu, kök-neden sorusunu **cevaplanamaz** yapar: sistem
doğru cevabı bulsa bile veri onu doğrulamaz. Türetilmiş bir tablo ise sorunun cevabını
**inşa gereği** taşır.*

## Bunun testlere kazandırdığı şey

Bugüne kadar bir senaryo testi *"çökmedi mi"* diye sorabiliyordu. Türetilmiş zincirle
**"doğru sebebi buldu mu"** diye sorulabilir hâle geliyor — çünkü doğru sebep veride
**SQL ile doğrulanabilir**. Ground truth artık bir yorum değil, bir sorgu.

## Dönem aralığı — iki farklı kural, ve nedeni

| tablo türü | aralık | neden |
|---|---|---|
| **türetilmiş** (kaynağı mevcut tablo) | kaynağın aralığı (2024-01 → 2026-06) | kaynağın olmadığı yerde türev **uydurma** olurdu |
| **bağımsız** (bütçe · kur · İK · fırsat) | **2022-01 → 2026-08** | *"geçen senenin geçen senesi"* sorulabilsin — YoY'nin YoY'si |

⚠ Mevcut modeli 2022'ye çekmek **her partiyi** yeniden üretirdi → 444 vakalık korpus
paydası oynardı. Genişleme, ölçümü bozmadan alınır.

Çalıştırma: `build_data.build()`'in sonunda çağrılır; tek başına da koşar:
    python demo/genisletme.py
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import duckdb

import olaylar as OL

DB = Path(__file__).resolve().parent / "data" / "boyahane.duckdb"

#: Bağımsız tabloların geniş penceresi — YoY'nin YoY'si için **dört buçuk yıl**.
GENIS_BAS = date(2022, 1, 1)
GENIS_SON = date(2026, 8, 31)

#: ⚠ Sabit tohum: seed **yeniden üretilebilir** olmalı, yoksa bir testin bugün geçip
#: yarın kalması "kod değişti" değil "veri değişti" demek olurdu ve teşhis imkânsızlaşır.
RNG = random.Random(20260805)


def _aylar(bas: date, son: date) -> list[tuple[int, int]]:
    out, y, a = [], bas.year, bas.month
    while (y, a) <= (son.year, son.month):
        out.append((y, a))
        a += 1
        if a == 13:
            y, a = y + 1, 1
    return out


def _tarih(y: int, a: int, g: int = 1) -> date:
    return date(y, a, min(g, 28))


def _yaz(con, ad: str, sema: str, satirlar: list[tuple]) -> int:
    """Tabloyu kurar ve doldurur. ⚠ Boş tablo **yazılmaz**: kullanıcının kuralı
    *"her tablosu dolu"* — boş bir tablo katalogda görünüp veri vermeyerek
    **sessiz-yanlış** üretir (soru cevaplanabilir görünür, sonuç boş döner)."""
    if not satirlar:
        raise AssertionError(f"{ad}: BOŞ tablo yazılamaz — türetme kaynağı kurumuş")
    con.execute(f"CREATE OR REPLACE TABLE {ad} ({sema})")
    isaret = ",".join("?" * len(satirlar[0]))
    con.executemany(f"INSERT INTO {ad} VALUES ({isaret})", satirlar)
    return len(satirlar)


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · PLANLAMA & BÜTÇE  —  *record-to-report*'un eksik yarısı
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 **Ölçülen boşluk:** CFO korpusundaki *"üçüncü çeyrek gerçekleşme nasıl"* ve
# *"hedefin neresindeyiz"* sorularının cevabı veride **yoktu** — 47 tablonun hiçbiri
# bir HEDEF taşımıyordu. *Gerçekleşme, tek başına bir gerçekleşme değildir; bir hedefe
# göre gerçekleşmedir.* Hedefsiz bir ERP'de bütçe sorusu sorulamaz.

_BUTCE_KALEMLERI = [
    # (kalem, hesap_kodu, bolum, aylık taban ₺, mevsim genliği)
    ("Ciro",                 "600", "Satış",     4_200_000, 0.18),
    ("Satılan Mal Maliyeti", "620", "Üretim",    2_950_000, 0.16),
    ("Hammadde",             "150", "Üretim",    1_150_000, 0.15),
    ("Kimyasal",             "151", "Üretim",      380_000, 0.14),
    ("Enerji",               "730", "Üretim",      620_000, 0.28),
    ("İşçilik",              "720", "Üretim",      840_000, 0.06),
    ("Bakım-Onarım",         "740", "Bakım",       145_000, 0.22),
    ("Personel Giderleri",   "770", "İK",          520_000, 0.05),
    ("Pazarlama",            "760", "Satış",       180_000, 0.20),
    ("Nakliye",              "761", "Lojistik",    210_000, 0.17),
    ("Genel Yönetim",        "770", "Yönetim",     295_000, 0.04),
    ("Ar-Ge",                "750", "Ar-Ge",       130_000, 0.12),
]


def _butce(con) -> dict[str, int]:
    """Bütçe hedefleri + dönem kapanışı.

    ⚠ Hedef **enflasyonla yürür**: 2022'nin bütçesi 2026'nınkiyle aynı olsaydı,
    *"bütçeyi aştık mı"* sorusu son yılda anlamsız çıkardı. Türkiye bağlamında yıllık
    ~%35 nominal artış varsayılır — **kurgusal**, ama yönü gerçekçi.
    """
    hedef, kapanis = [], []
    for y, a in _aylar(GENIS_BAS, GENIS_SON):
        yil_carpani = 1.35 ** (y - 2022)
        # Mevsimsellik: tekstilde yaz (7-8) düşük, ilkbahar/sonbahar yüksek.
        mevsim = {1: 0.94, 2: 0.97, 3: 1.08, 4: 1.10, 5: 1.06, 6: 1.02,
                  7: 0.82, 8: 0.79, 9: 1.12, 10: 1.15, 11: 1.09, 12: 0.98}[a]
        for kalem, hesap, bolum, taban, genlik in _BUTCE_KALEMLERI:
            gurultu = 1 + RNG.uniform(-genlik, genlik) * 0.35
            tutar = round(taban * yil_carpani * mevsim * gurultu, 2)
            hedef.append((y, a, bolum, hesap, kalem, tutar,
                          round(tutar / 42.0, 1) if kalem in ("Ciro", "Hammadde") else None,
                          "TRY", "ONAYLI" if (y, a) < (2026, 7) else "TASLAK"))
        # Dönem kapanışı: geçmiş aylar kapalı, son iki ay açık — *"kapanış yapıldı mı"*
        # sorusu ancak bu ayrım varsa anlamlıdır.
        kapali = (y, a) <= (2026, 5)
        kapanis.append((y, a, "KAPALI" if kapali else "AÇIK",
                        _tarih(y, a, 28) + timedelta(days=12) if kapali else None,
                        "Mali İşler", RNG.choice(["S. Aydın", "M. Korkmaz", "E. Tunç"])))

    n1 = _yaz(con, "butce_hedefleri",
              "yil INTEGER, ay INTEGER, bolum VARCHAR, hesap_kodu VARCHAR, kalem VARCHAR, "
              "hedef_tutar DOUBLE, hedef_miktar DOUBLE, para_birimi VARCHAR, durum VARCHAR",
              hedef)
    n2 = _yaz(con, "donem_kapanis",
              "yil INTEGER, ay INTEGER, durum VARCHAR, kapanis_tarihi DATE, "
              "bolum VARCHAR, kapatan VARCHAR", kapanis)

    # Bütçe revizyonları — *bir bütçe yıl içinde revize edilir*; revizyonsuz bir bütçe
    # tablosu, "hangi bütçeye göre" sorusunu görünmez kılar.
    rev = []
    for y in range(2022, 2027):
        for no, ay in ((1, 4), (2, 9)):
            if (y, ay) > (2026, 8):
                continue
            for kalem, hesap, bolum, _t, _g in _BUTCE_KALEMLERI:
                rev.append((y, no, ay, bolum, hesap, kalem,
                            round(RNG.uniform(-0.12, 0.18), 4),
                            RNG.choice(["Kur etkisi", "Talep revizyonu", "Enerji fiyatı",
                                        "Kapasite değişikliği", "Yeni müşteri"]),
                            _tarih(y, ay, 15)))
    n3 = _yaz(con, "butce_revizyonlari",
              "yil INTEGER, revizyon_no INTEGER, ay INTEGER, bolum VARCHAR, hesap_kodu VARCHAR, "
              "kalem VARCHAR, degisim_orani DOUBLE, gerekce VARCHAR, tarih DATE", rev)
    return {"butce_hedefleri": n1, "donem_kapanis": n2, "butce_revizyonlari": n3}


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · DÖVİZ & FİNANSMAN  —  ihracatçı bir tekstilcinin **asıl** riski
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠ `faturalar` zaten `para_birimi` ve `kur` taşıyor ama **kur tablosu yoktu**: yani
# *"bugünkü kurla ne eder"* ya da *"kur farkı zararımız ne"* sorusunun dayanağı yoktu.
# *Bir alanı taşımak, onu açıklayabilmek değildir.*

def _finans(con) -> dict[str, int]:
    kur = []
    # Rastgele yürüyüş — ama **tek yönlü sürüklenmeli**: TL'nin dönem boyunca değer
    # kaybı bu veri kümesinin en belirleyici makro gerçeği.
    usd, eur = 13.50, 15.30
    g = GENIS_BAS
    while g <= GENIS_SON:
        if g.weekday() < 5:                       # hafta içi — TCMB deseni
            usd *= 1 + RNG.gauss(0.00115, 0.0062)
            eur *= 1 + RNG.gauss(0.00121, 0.0068)
            kur.append((g, "USD", round(usd, 4), round(usd * 1.004, 4), round(usd * 0.996, 4)))
            kur.append((g, "EUR", round(eur, 4), round(eur * 1.004, 4), round(eur * 0.996, 4)))
            kur.append((g, "GBP", round(eur * 1.17, 4), round(eur * 1.175, 4), round(eur * 1.165, 4)))
        g += timedelta(days=1)
    n1 = _yaz(con, "doviz_kurlari",
              "tarih DATE, para_birimi VARCHAR, kur DOUBLE, satis_kuru DOUBLE, alis_kuru DOUBLE", kur)

    krediler, odemeler = [], []
    bankalar = ["Ziraat", "İş Bankası", "Garanti BBVA", "Akbank", "Yapı Kredi", "Vakıfbank"]
    for i in range(18):
        acilis = GENIS_BAS + timedelta(days=RNG.randint(0, 1500))
        vade_ay = RNG.choice([12, 18, 24, 36, 48, 60])
        anapara = RNG.choice([1_500_000, 2_500_000, 4_000_000, 6_000_000, 10_000_000])
        pb = RNG.choices(["TRY", "USD", "EUR"], weights=[6, 3, 2])[0]
        faiz = round(RNG.uniform(0.28, 0.52) if pb == "TRY" else RNG.uniform(0.055, 0.095), 4)
        kod = f"KRD-{2022 + i // 4}-{i + 1:03d}"
        krediler.append((kod, RNG.choice(bankalar), pb, float(anapara), faiz, vade_ay,
                         acilis, acilis + timedelta(days=30 * vade_ay),
                         RNG.choice(["İşletme", "Yatırım", "İhracat", "Rotatif"]),
                         "KAPALI" if acilis + timedelta(days=30 * vade_ay) < GENIS_SON else "AÇIK"))
        taksit = anapara / vade_ay
        for t in range(vade_ay):
            vade = acilis + timedelta(days=30 * (t + 1))
            if vade > GENIS_SON:
                break
            kalan = anapara - taksit * t
            odemeler.append((kod, t + 1, vade, round(taksit, 2), round(kalan * faiz / 12, 2),
                             round(taksit + kalan * faiz / 12, 2), round(kalan - taksit, 2),
                             "ÖDENDİ" if vade < date(2026, 7, 1) else "BEKLİYOR"))
    n2 = _yaz(con, "krediler",
              "kredi_kodu VARCHAR, banka VARCHAR, para_birimi VARCHAR, anapara DOUBLE, "
              "faiz_orani DOUBLE, vade_ay INTEGER, acilis_tarihi DATE, kapanis_tarihi DATE, "
              "tur VARCHAR, durum VARCHAR", krediler)
    n3 = _yaz(con, "kredi_odemeleri",
              "kredi_kodu VARCHAR, taksit_no INTEGER, vade_tarihi DATE, anapara_tutar DOUBLE, "
              "faiz_tutar DOUBLE, toplam_tutar DOUBLE, kalan_anapara DOUBLE, durum VARCHAR", odemeler)
    return {"doviz_kurlari": n1, "krediler": n2, "kredi_odemeleri": n3}


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · SATIŞ HUNİSİ  —  *opportunity-to-order*
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 **Türetme çapası: `partiler.siparis_no`.** Sipariş başlıkları uydurulmuyor —
# üretilen partilerin **kendi** sipariş numaralarından kuruluyor. Böylece
# *"siparişin kaç kilosu üretildi"* sorusu **gerçek** bir join'e dayanır.
#
# ⚠ Fırsatlar bunun **öncesi**: kazanılan fırsat bir siparişe döner, kaybedilen
# dönmez. *Yalnız kazanılanı tutan bir CRM, kazanma oranını hesaplatamaz* — ve
# "neden kaybediyoruz" sorusu bu ürünün en sık sorulacak satış sorusudur.

_KAYIP_NEDENLERI = ["Fiyat yüksek", "Termin uzun", "Kapasite yok", "Numune reddedildi",
                    "Rakip tercih edildi", "Müşteri projeyi iptal etti", "Vade uyuşmadı"]
_HUNI_ASAMALARI = ["İlk Temas", "Numune", "Teklif", "Pazarlık", "Kazanıldı", "Kaybedildi"]


def _satis(con) -> dict[str, int]:
    musteriler = con.execute("SELECT musteri_kodu, musteri_adi FROM musteriler").fetchall()
    # 🔴 GERÇEK siparişler — `partiler`den. Uydurma sipariş numarası YOK.
    siparisler = con.execute(
        "SELECT siparis_no, any_value(musteri_kod) mk, min(tarih) ilk, max(tarih) son, "
        "       sum(kg) kg, sum(ciro_tl) ciro, count(*) parti_adet "
        "FROM partiler GROUP BY siparis_no ORDER BY 3"
    ).fetchall()

    sip_rows, satir_rows = [], []
    for sn, mk, ilk, son, kg, ciro, adet in siparisler:
        acilis = ilk - timedelta(days=RNG.randint(7, 34))
        soz_termin = ilk + timedelta(days=RNG.randint(10, 40))
        # Termin performansı: gecikme **gerçek** çıkış tarihine göre hesaplanır.
        gecikme = (son - soz_termin).days
        sip_rows.append((sn, mk, acilis, soz_termin, son, float(kg), float(ciro or 0),
                         adet, gecikme,
                         "ZAMANINDA" if gecikme <= 0 else ("GECİKMELİ" if gecikme <= 10 else "KRİTİK GECİKME"),
                         RNG.choice(["Web", "Fuar", "Referans", "Saha Ziyareti", "Mevcut Müşteri"]),
                         RNG.choice(["A. Demir", "B. Yılmaz", "C. Şahin", "D. Kaya"])))
        for i in range(RNG.randint(1, 3)):
            pay = 1.0 / (i + 1)
            satir_rows.append((sn, i + 1, f"KLM-{RNG.randint(100, 199)}",
                               round(kg * pay / 2, 1), round((ciro or 0) * pay / 2, 2),
                               RNG.choice(["kg", "metre"]),
                               RNG.choice(["Pamuk", "Polyester", "Viskon", "Karışım", "Likra"])))
    n1 = _yaz(con, "satis_siparisleri",
              "siparis_no VARCHAR, musteri_kod VARCHAR, acilis_tarihi DATE, sozlesme_termin DATE, "
              "gerceklesen_termin DATE, toplam_kg DOUBLE, toplam_tutar DOUBLE, parti_adet INTEGER, "
              "gecikme_gun INTEGER, termin_durumu VARCHAR, kanal VARCHAR, satis_temsilcisi VARCHAR",
              sip_rows)
    n2 = _yaz(con, "siparis_satirlari",
              "siparis_no VARCHAR, satir_no INTEGER, urun_kodu VARCHAR, miktar DOUBLE, "
              "tutar DOUBLE, birim VARCHAR, kumas_tipi VARCHAR", satir_rows)

    # Fırsat hunisi — kazanılanların bir kısmı GERÇEK siparişe bağlanır, gerisi kayıp.
    firsatlar, temaslar = [], []
    kazanan_sip = [s[0] for s in siparisler]
    RNG.shuffle(kazanan_sip)
    fno = 0
    for y, a in _aylar(GENIS_BAS, GENIS_SON):
        for _ in range(RNG.randint(4, 11)):
            fno += 1
            mk, _ad = RNG.choice(musteriler)
            acilis = _tarih(y, a, RNG.randint(1, 28))
            kapanis = acilis + timedelta(days=RNG.randint(14, 120))
            # 🔴 EKİLİ OLAY: müşteri kaybı. Pencere içindeki o müşterinin fırsatları
            # **kaybedilir** ve kayıp nedeni kayda geçer → "hangi müşteriyi kaybettik"
            # sorusunun cevabı SQL ile bulunabilir olur.
            _kayip_carp = OL.carpan("musteri_kaybi", acilis, str(mk))
            kazandi = RNG.random() < 0.34 and _kayip_carp <= 1.0
            asama = "Kazanıldı" if kazandi else (
                "Kaybedildi" if kapanis < date(2026, 7, 1) else RNG.choice(_HUNI_ASAMALARI[:4]))
            bagli = kazanan_sip.pop() if (kazandi and kazanan_sip) else None
            firsatlar.append((f"FRS-{y}-{fno:04d}", mk, asama,
                              round(RNG.uniform(180_000, 3_400_000) * (1.35 ** (y - 2022)), 2),
                              {"İlk Temas": 0.10, "Numune": 0.25, "Teklif": 0.45,
                               "Pazarlık": 0.70, "Kazanıldı": 1.0, "Kaybedildi": 0.0}[asama],
                              acilis, kapanis if asama in ("Kazanıldı", "Kaybedildi") else None,
                              None if asama != "Kaybedildi" else RNG.choice(_KAYIP_NEDENLERI),
                              bagli, RNG.choice(["A. Demir", "B. Yılmaz", "C. Şahin", "D. Kaya"])))
            for t in range(RNG.randint(1, 5)):
                temaslar.append((f"TMS-{fno:05d}-{t}", f"FRS-{y}-{fno:04d}", mk,
                                 acilis + timedelta(days=t * RNG.randint(3, 15)),
                                 RNG.choice(["Telefon", "E-posta", "Ziyaret", "Fuar", "Toplantı"]),
                                 RNG.choice(["A. Demir", "B. Yılmaz", "C. Şahin", "D. Kaya"]),
                                 RNG.choice(["Numune talebi", "Fiyat görüşmesi", "Termin sorgusu",
                                             "Şikâyet takibi", "Yeni ürün tanıtımı", "Tahsilat"])))
    n3 = _yaz(con, "firsatlar",
              "firsat_no VARCHAR, musteri_kod VARCHAR, asama VARCHAR, tahmini_tutar DOUBLE, "
              "olasilik DOUBLE, acilis_tarihi DATE, kapanis_tarihi DATE, kayip_nedeni VARCHAR, "
              "siparis_no VARCHAR, satis_temsilcisi VARCHAR", firsatlar)
    n4 = _yaz(con, "musteri_temaslari",
              "temas_no VARCHAR, firsat_no VARCHAR, musteri_kod VARCHAR, tarih DATE, "
              "tur VARCHAR, personel VARCHAR, konu VARCHAR", temaslar)

    # Müşteri segmentleri — **gerçek** ciroya göre ABC. *Uydurma bir segment,
    # "A müşterilerimiz nasıl" sorusunu yanlış cevaplatır.*
    seg = con.execute(
        "SELECT musteri_kod, sum(ciro_tl) c FROM partiler GROUP BY 1 ORDER BY 2 DESC"
    ).fetchall()
    top = sum(x[1] or 0 for x in seg) or 1.0
    kum, seg_rows = 0.0, []
    for mk, c in seg:
        kum += (c or 0)
        sinif = "A" if kum / top <= 0.60 else ("B" if kum / top <= 0.85 else "C")
        seg_rows.append((mk, sinif, round(c or 0, 2), round(100 * (c or 0) / top, 2),
                         RNG.choice(["Yurt İçi", "İhracat"]),
                         RNG.choice(["Örme", "Dokuma", "Konfeksiyon"]),
                         RNG.randint(15, 90)))
    n5 = _yaz(con, "musteri_segmentleri",
              "musteri_kod VARCHAR, abc_sinifi VARCHAR, toplam_ciro DOUBLE, ciro_payi_yuzde DOUBLE, "
              "pazar VARCHAR, sektor VARCHAR, vade_gun INTEGER", seg_rows)
    return {"satis_siparisleri": n1, "siparis_satirlari": n2, "firsatlar": n3,
            "musteri_temaslari": n4, "musteri_segmentleri": n5}


# ═══════════════════════════════════════════════════════════════════════════════
# 4 · KALİTE ZİNCİRİ  —  🔴 **bu modülün kalbi**
# ═══════════════════════════════════════════════════════════════════════════════
#
# `partiler` her partide **iki** sayı taşıyor: `uretim_dE` (ölçülen renk sapması) ve
# `musteri_tolerans_dE` (o müşterinin kabul sınırı). İkisinin farkı **zaten** bir
# kalite gerçeğidir — ama bugüne kadar hiçbir tablo onu bir **olaya** çevirmiyordu.
#
# > 🔴 Şikâyetler **toleransı aşan gerçek partilerden** doğar. Yani *"mart ayında
# > şikâyet neden arttı"* sorusunun cevabı veride **SQL ile bulunabilir**: o ay
# > toleransı aşan partiler hangi makinede, hangi operatörde, hangi reçetede toplandı.
#
# *Rastgele bir şikâyet tablosu bu soruyu cevaplanamaz yapardı: sistem doğru cevabı
# üretse bile veri onu doğrulamazdı. Ground truth artık bir yorum değil, bir sorgu.*

def _kalite(con) -> dict[str, int]:
    sapan = con.execute(
        "SELECT parti_no, tarih, musteri_kod, makine, operator, recete_kod, renk_ad, "
        "       kg, uretim_dE, musteri_tolerans_dE, tedarikci_kod "
        "FROM partiler WHERE uretim_dE > musteri_tolerans_dE ORDER BY tarih"
    ).fetchall()

    sikayet, capa, uygunsuz = [], [], []
    for i, (pno, trh, mk, mak, opr, rcp, renk, kg, de, tol, tdk) in enumerate(sapan):
        asim = de - tol
        # 🔴 EKİLİ OLAY — `demo/olaylar.py`. Ground truth **ekilen olayın kendisidir**:
        # bir testin *"doğru sebebi buldu mu"* diye sorabilmesi için sebebin veride
        # **kayıtlı ve SQL ile bulunabilir** olması gerekir.
        carp = OL.carpan("makine_degradasyonu", trh, mak)
        if carp > 1.0:
            asim *= carp          # sapma büyür → şikâyet kesinleşir, şiddeti artar
        # ⚠ Her sapma şikâyete dönmez — küçük sapmayı müşteri fark etmez. Eşik
        # **sapmanın büyüklüğüne** bağlı: gerçek hayatta da böyle.
        elif asim < 0.15 and RNG.random() > 0.22:
            continue
        agir = asim > 0.55
        acilis = trh + timedelta(days=RNG.randint(3, 21))
        sure = RNG.randint(2, 45) if agir else RNG.randint(1, 18)
        kapandi = acilis + timedelta(days=sure) < date(2026, 7, 1)
        sno = f"SKY-{trh.year}-{i + 1:05d}"
        sikayet.append((sno, mk, pno, acilis, acilis + timedelta(days=sure) if kapandi else None,
                        "Renk sapması" if asim < 0.4 else RNG.choice(
                            ["Renk sapması", "Ton farkı", "Yıkama haslığı", "En/gramaj uygunsuzluğu"]),
                        round(asim, 3), "AĞIR" if agir else ("ORTA" if asim > 0.3 else "HAFİF"),
                        "KAPALI" if kapandi else "AÇIK", sure if kapandi else None,
                        round(float(kg) * RNG.uniform(0.05, 0.6), 1),
                        mak, opr, rcp, renk,
                        RNG.choice(["İade", "Fiyat indirimi", "Yeniden üretim", "Kabul"])))
        # CAPA — yalnız AĞIR şikâyetlerde. *Her şikâyete kök-neden analizi açan bir
        # sistem, hiçbirine açmayan kadar işe yaramaz: sinyal gürültüde kaybolur.*
        # 🔴 EKİLİ OLAY: tedarikçi kalite düşüşü → CAPA'nın kök-neden kategorisi
        # o pencerede **Malzeme**'ye kayar. Ground truth: hangi tedarikçi.
        _tedarik_carp = OL.carpan("tedarikci_bozulmasi", trh, str(tdk))
        if agir or _tedarik_carp > 1.0:
            capa.append((f"CAPA-{trh.year}-{len(capa) + 1:04d}", sno, acilis + timedelta(days=2),
                         "Hammadde tedarikçi değişimi" if _tedarik_carp > 1.0 else
                         RNG.choice(["Makine kalibrasyonu", "Reçete revizyonu", "Operatör eğitimi",
                                     "Hammadde tedarikçi değişimi", "Lab ölçüm prosedürü"]),
                         "Malzeme" if _tedarik_carp > 1.0 else
                         RNG.choice(["Makine", "Yöntem", "İnsan", "Malzeme", "Ölçüm"]),
                         mak, tdk, "KAPALI" if kapandi else "AÇIK",
                         acilis + timedelta(days=sure + 10) if kapandi else None,
                         RNG.choice(["Kalite Md.", "Üretim Md.", "Ar-Ge Uzmanı"])))
        # Olay penceresinde EK satırlar: çarpan kadar şikâyet doğar. ⚠ Satır çoğaltmak
        # yerine yalnız sapmayı büyütmek yetmezdi — *bir olayın izi ADETTE de
        # görünmeli*, çünkü kullanıcı "şikâyet arttı" diye fark eder, "sapma büyüdü"
        # diye değil.
        for _ek in range(int(carp) - 1):
            sikayet.append((f"{sno}-E{_ek}", mk, pno, acilis,
                            acilis + timedelta(days=sure) if kapandi else None,
                            "Renk sapması", round(asim, 3), "AĞIR",
                            "KAPALI" if kapandi else "AÇIK", sure if kapandi else None,
                            round(float(kg) * RNG.uniform(0.05, 0.6), 1),
                            mak, opr, rcp, renk, "İade"))
        if asim > 0.25:
            uygunsuz.append((f"UYG-{trh.year}-{len(uygunsuz) + 1:05d}", pno, trh,
                             "Proses", RNG.choice(["Renk", "Haslık", "Gramaj", "En", "Yüzey"]),
                             round(asim, 3), mak, opr,
                             RNG.choice(["Yeniden işlem", "Şartlı kabul", "Hurda", "Fire"]),
                             round(float(kg) * RNG.uniform(0.02, 0.25), 1)))

    n1 = _yaz(con, "musteri_sikayetleri",
              "sikayet_no VARCHAR, musteri_kod VARCHAR, parti_no VARCHAR, acilis_tarihi DATE, "
              "kapanis_tarihi DATE, konu VARCHAR, sapma_dE DOUBLE, siddet VARCHAR, durum VARCHAR, "
              "cozum_suresi_gun INTEGER, iade_kg DOUBLE, makine VARCHAR, operator VARCHAR, "
              "recete_kod VARCHAR, renk VARCHAR, cozum_sekli VARCHAR", sikayet)
    n2 = _yaz(con, "duzeltici_faaliyetler",
              "capa_no VARCHAR, sikayet_no VARCHAR, acilis_tarihi DATE, faaliyet VARCHAR, "
              "kok_neden_kategorisi VARCHAR, makine VARCHAR, tedarikci_kod VARCHAR, durum VARCHAR, "
              "kapanis_tarihi DATE, sorumlu VARCHAR", capa)
    n3 = _yaz(con, "uygunsuzluklar",
              "uygunsuzluk_no VARCHAR, parti_no VARCHAR, tarih DATE, tur VARCHAR, kategori VARCHAR, "
              "sapma DOUBLE, makine VARCHAR, operator VARCHAR, karar VARCHAR, etkilenen_kg DOUBLE",
              uygunsuz)

    # Denetimler — ISO/müşteri/iç. Bulgu sayısı **gerçek** o çeyreğin uygunsuzluk
    # yoğunluğuyla ilişkilendirilir; bağımsız rastgele bir skor yanıltıcı olurdu.
    ceyrek_uyg = con.execute(
        "SELECT year(tarih), quarter(tarih), count(*) FROM partiler "
        "WHERE uretim_dE > musteri_tolerans_dE GROUP BY 1,2"
    ).fetchall()
    ort = (sum(x[2] for x in ceyrek_uyg) / len(ceyrek_uyg)) if ceyrek_uyg else 1.0
    den = []
    for y, c, n in sorted(ceyrek_uyg):
        yogunluk = n / ort
        for tur in ("İç Denetim", "ISO 9001", "Müşteri Denetimi", "OEKO-TEX"):
            if tur != "İç Denetim" and RNG.random() > 0.45:
                continue
            bulgu = max(0, int(RNG.gauss(4 * yogunluk, 1.6)))
            den.append((f"DNT-{y}-Q{c}-{tur[:3]}", tur, date(y, 3 * c - 2, RNG.randint(5, 25)),
                        bulgu, max(0, bulgu - RNG.randint(0, bulgu or 1)),
                        round(max(55.0, 100 - bulgu * RNG.uniform(2.5, 5.5)), 1),
                        RNG.choice(["TSE", "SGS", "Bureau Veritas", "İç Ekip", "Müşteri Ekibi"]),
                        "GEÇTİ" if bulgu < 7 else "ŞARTLI"))
    n4 = _yaz(con, "denetimler",
              "denetim_no VARCHAR, tur VARCHAR, tarih DATE, bulgu_sayisi INTEGER, "
              "kapanan_bulgu INTEGER, skor DOUBLE, denetci_kurum VARCHAR, sonuc VARCHAR", den)
    return {"musteri_sikayetleri": n1, "duzeltici_faaliyetler": n2,
            "uygunsuzluklar": n3, "denetimler": n4}


# ═══════════════════════════════════════════════════════════════════════════════
# 5 · REÇETE · İŞ EMRİ · MALİYET  —  *plan-to-produce*
# ═══════════════════════════════════════════════════════════════════════════════
#
# `partiler.recete_kod` **zaten** her partide duruyordu ama reçetenin **içeriği**
# hiçbir yerde yoktu: hangi kimyasal, kaç gram. Yani *"bu rengin maliyeti ne"* ya da
# *"hangi reçete pahalı"* sorularının dayanağı yoktu.
#
# 🔴 Maliyet **uydurulmuyor**: `partiler` her partide `elektrik_tl` · `dogalgaz_tl` ·
# `su_tl` · `kimyasal_tl` · `kg` taşıyor. Birim maliyet bunların **gerçek toplamından**
# çıkar. *Bir maliyet tablosunu bağımsız üretmek, "maliyet neden arttı" sorusunu
# enerji verisinden kopuk — yani cevaplanamaz — yapardı.*

def _uretim(con) -> dict[str, int]:
    kimyasallar = con.execute("SELECT kimyasal_kodu, kimyasal_adi FROM kimyasallar").fetchall()
    # 🔴 ÖLÇÜLDÜ ve İLK ÇAPAM YANLIŞTI: `partiler.recete_kod` bir REÇETE KATALOĞU
    # değil — biçimi `<müşteri>-<sayı>` ve 37 878 partide **29 065 farklı** değer
    # taşıyor. Yani neredeyse partiye özel bir iş kodu.
    #
    # > ⚠ *Bir alanın adı, onun ne olduğunu söylemez.* Bunu çapa alıp 29 065 satırlık
    # > bir "reçete kataloğu" ürettim; anlamsız bir şişme oldu. Bir boyahanenin
    # > gerçek reçetesi **renk × derinlik × boya sınıfı**dır — 5 × 4 kombinasyon,
    # > yani onlarca, on binlerce değil.
    #
    # Doğru çapa bu; parti kodu ise `recete_uygulama` ile bu kataloğa BAĞLANIR, böylece
    # "hangi reçete pahalı" sorusu hem gerçek hem cevaplanabilir olur.
    # ⚠ İKİNCİ ÖLÇÜM, İKİNCİ DÜZELTME: `renk_ad` ile `renk_derinlik` neredeyse AYNI
    # alan çıktı (yalnız Siyah→Koyu farklı) → 5 reçete. `ham_grup` ise **tek değerli**
    # ("Örme Kumaş"). Yani bu veri kümesinde reçeteyi ayıran gerçek ikinci eksen
    # **gramaj** (7 değer). Katalog 5 × 7 = **en çok 35** reçete.
    #
    # 🔴 Şişirmedim. Sahte bir eksen ekleyip 500 reçete üretmek, katalog büyüklüğünü
    # bir başarı gibi gösterip *"hangi reçete pahalı"* sorusunu anlamsız kılardı —
    # çünkü ayrım veride yok, uydurmada olurdu. *Bir kataloğun büyüklüğü, ancak
    # ayrımları gerçekse bir yetenektir.*
    receteler = con.execute(
        "SELECT renk_ad, gramaj, any_value(renk_derinlik) drn, count(*) n, "
        "       avg(kimyasal_tl/nullif(kg,0)) kim_kg, avg(su_lt/nullif(kg,0)) su_kg, "
        "       avg(imalat_suresi_dk) sure, avg(uretim_dE) de "
        "FROM partiler GROUP BY 1,2 ORDER BY 4 DESC"
    ).fetchall()

    rec_rows, bilesen_rows = [], []
    _SINIF = {"Açık": "Direkt", "Orta": "Reaktif", "Koyu": "Küp"}
    for renk, gramaj, derinlik, n, kim_kg, su_kg, sure, de in receteler:
        rk = f"RC-{str(renk)[:3].upper()}-{int(gramaj)}"
        sinif = _SINIF.get(str(derinlik), "Reaktif")
        rec_rows.append((rk, renk, derinlik, int(gramaj), int(n),
                         round(kim_kg or 0, 4), round(su_kg or 0, 2),
                         round(sure or 0, 1), sinif,
                         {"Açık": 60, "Orta": 98, "Koyu": 130}.get(str(derinlik), 98),
                         round(de or 0, 3),
                         "Onaylı" if str(derinlik) != "Çok Koyu" else "Revizyonda"))
        # Derin renk → daha çok boya. *Sabit bir bileşen listesi, "koyu renkler neden
        # pahalı" sorusunu yanlış cevaplatırdı.*
        agirlik = {"Açık": 0.6, "Orta": 1.0, "Koyu": 1.8, "Çok Koyu": 2.6}.get(str(derinlik), 1.0)
        for kk, ka in RNG.sample(kimyasallar, k=min(len(kimyasallar), RNG.randint(4, 8))):
            bilesen_rows.append((rk, kk, ka, round(RNG.uniform(0.8, 22.0) * agirlik, 3), "g/kg",
                                 RNG.choice(["Boya", "Yardımcı", "Yıkama", "Fikse"])))
    n1 = _yaz(con, "receteler",
              "recete_kod VARCHAR, renk VARCHAR, renk_derinlik VARCHAR, gramaj INTEGER, "
              "kullanim_adet INTEGER, kimyasal_tl_kg DOUBLE, su_lt_kg DOUBLE, ort_sure_dk DOUBLE, "
              "boya_sinifi VARCHAR, sicaklik_c INTEGER, ort_sapma_dE DOUBLE, durum VARCHAR", rec_rows)

    # Parti kodu → katalog reçetesi köprüsü. *İki kimlik arasında köprü kurmamak,
    # ikisini de yarım bırakır: parti kodu anlamsız, katalog ise erişilemez kalırdı.*
    uyg = con.execute(
        "SELECT parti_no, recete_kod, renk_ad, gramaj, tarih, kg, kimyasal_tl "
        "FROM partiler"
    ).fetchall()
    n1b = _yaz(con, "recete_uygulama",
               "parti_no VARCHAR, parti_recete_kod VARCHAR, katalog_recete_kod VARCHAR, "
               "renk VARCHAR, gramaj INTEGER, tarih DATE, miktar_kg DOUBLE, "
               "kimyasal_tl DOUBLE",
               [(p, prk, f"RC-{str(rn)[:3].upper()}-{int(gr)}", rn, int(gr), t,
                 round(float(kg or 0), 1), round(float(kt or 0), 2))
                for p, prk, rn, gr, t, kg, kt in uyg])
    n2 = _yaz(con, "recete_bilesenleri",
              "recete_kod VARCHAR, kimyasal_kodu VARCHAR, kimyasal_adi VARCHAR, miktar DOUBLE, "
              "birim VARCHAR, rol VARCHAR", bilesen_rows)

    # 🔴 Birim maliyet — GERÇEK tüketimden. Beş bileşen ayrı ayrı görünür ki
    # *"maliyet neden arttı"* sorusu **hangi bileşen** diye ayrıştırılabilsin.
    mal = con.execute(
        "SELECT year(tarih) y, month(tarih) a, makine, "
        "       sum(kg) kg, sum(kimyasal_tl) kim, sum(elektrik_tl) elk, sum(dogalgaz_tl) gaz, "
        "       sum(su_tl+atiksu_tl) su, sum(imalat_suresi_dk) dk, sum(ciro_tl) ciro "
        "FROM partiler GROUP BY 1,2,3 ORDER BY 1,2,3"
    ).fetchall()
    mal_rows = []
    for y, a, mak, kg, kim, elk, gaz, su, dk, ciro in mal:
        kg = float(kg or 0) or 1.0
        # 🔴 EKİLİ OLAY: enerji fiyat şoku. ⚠ Yalnız **fiyat** çarpılır, üretim
        # miktarı DEĞİŞMEZ — böylece PVM ayrıştırması *"artış hacimden mi fiyattan
        # mı"* sorusuna doğru cevap verebilir. *İkisini birden oynatmak, ayrıştırmayı
        # ölçülemez yapardı.*
        _enerji_carp = OL.carpan("maliyet_soku", date(y, a, 1), f"{y}Q{(a - 1) // 3 + 1}")
        if _enerji_carp > 1.0:
            elk = float(elk or 0) * _enerji_carp
            gaz = float(gaz or 0) * _enerji_carp
        # İşçilik: dakika × saatlik ücret / 60, ücret yıllara göre yürür.
        iscilik = float(dk or 0) / 60.0 * (95.0 * (1.42 ** (y - 2024)))
        genel = (float(kim or 0) + float(elk or 0) + float(gaz or 0)) * 0.18
        toplam = float(kim or 0) + float(elk or 0) + float(gaz or 0) + float(su or 0) + iscilik + genel
        mal_rows.append((y, a, mak, round(kg, 1),
                         round(float(kim or 0) / kg, 4), round(float(elk or 0) / kg, 4),
                         round(float(gaz or 0) / kg, 4), round(float(su or 0) / kg, 4),
                         round(iscilik / kg, 4), round(genel / kg, 4), round(toplam / kg, 4),
                         round(float(ciro or 0) / kg, 4),
                         round((float(ciro or 0) - toplam) / kg, 4),
                         round(100 * (float(ciro or 0) - toplam) / (float(ciro or 0) or 1), 2)))
    n3 = _yaz(con, "urun_maliyetleri",
              "yil INTEGER, ay INTEGER, makine VARCHAR, uretim_kg DOUBLE, kimyasal_tl_kg DOUBLE, "
              "elektrik_tl_kg DOUBLE, dogalgaz_tl_kg DOUBLE, su_tl_kg DOUBLE, iscilik_tl_kg DOUBLE, "
              "genel_uretim_tl_kg DOUBLE, toplam_maliyet_tl_kg DOUBLE, satis_fiyati_tl_kg DOUBLE, "
              "birim_kar_tl_kg DOUBLE, kar_marji_yuzde DOUBLE", mal_rows)

    # İş emirleri — partilerden. Planlanan/gerçekleşen ayrımı *"plana uyuyor muyuz"*
    # sorusunu mümkün kılar; tek bir "gerçekleşen" sütunu bunu görünmez bırakırdı.
    partiler = con.execute(
        "SELECT parti_no, siparis_no, tarih, makine, vardiya_ad, operator, kg, "
        "       imalat_suresi_dk, hiz_m_dk, teorik_hiz_m_dk, ilk_seferde_tamam "
        "FROM partiler ORDER BY tarih"
    ).fetchall()
    ie_rows = []
    for i, (pno, sn, trh, mak, vrd, opr, kg, dk, hiz, teo, ist) in enumerate(partiler):
        plan_dk = float(dk or 0) * float(teo or 1) / max(float(hiz or 1), 0.01)
        ie_rows.append((f"IE-{trh.year}-{i + 1:06d}", pno, sn, trh, mak, vrd, opr,
                        round(float(kg or 0), 1), round(plan_dk, 1), round(float(dk or 0), 1),
                        round(float(dk or 0) - plan_dk, 1),
                        round(100 * plan_dk / max(float(dk or 1), 0.01), 1),
                        "TAMAM" if ist else "YENİDEN İŞLEM",
                        RNG.choice(["Normal", "Normal", "Normal", "Acil", "Numune"])))
    n4 = _yaz(con, "is_emirleri",
              "is_emri_no VARCHAR, parti_no VARCHAR, siparis_no VARCHAR, tarih DATE, makine VARCHAR, "
              "vardiya VARCHAR, operator VARCHAR, miktar_kg DOUBLE, planlanan_dk DOUBLE, "
              "gerceklesen_dk DOUBLE, sapma_dk DOUBLE, verimlilik_yuzde DOUBLE, sonuc VARCHAR, "
              "oncelik VARCHAR", ie_rows)

    # Kapasite planlama — makine × ay. Gerçek çalışma süresinden doluluk.
    kap = con.execute(
        "SELECT year(tarih), month(tarih), makine, sum(imalat_suresi_dk)/60.0 saat, count(*) "
        "FROM partiler GROUP BY 1,2,3"
    ).fetchall()
    kap_rows = [(y, a, mak, round(30 * 24 * 0.85, 1), round(float(s or 0), 1),
                 round(100 * float(s or 0) / (30 * 24 * 0.85), 1), int(n),
                 "AŞIRI YÜKLÜ" if float(s or 0) > 30 * 24 * 0.85 else
                 ("DOLU" if float(s or 0) > 30 * 24 * 0.6 else "BOŞ KAPASİTE"))
                for y, a, mak, s, n in kap]
    n5 = _yaz(con, "kapasite_planlama",
              "yil INTEGER, ay INTEGER, makine VARCHAR, planlanan_saat DOUBLE, "
              "gerceklesen_saat DOUBLE, doluluk_yuzde DOUBLE, parti_adet INTEGER, durum VARCHAR",
              kap_rows)
    return {"receteler": n1, "recete_uygulama": n1b, "recete_bilesenleri": n2,
            "urun_maliyetleri": n3, "is_emirleri": n4, "kapasite_planlama": n5}


# ═══════════════════════════════════════════════════════════════════════════════
# 6 · İK GENİŞLETMESİ  —  *hire-to-retire*'ın eksik üçte ikisi
# ═══════════════════════════════════════════════════════════════════════════════
#
# Mevcut hâl: `personel` · `personel_ozluk` · `puantaj` · `bordro` · `izinler`. Yani
# **çalışan bir insanın** verisi var, ama *işe alınması*, *eğitilmesi*, *değerlendirilmesi*
# ve *ayrılması* yok. ⚠ Devir hızı — İK'nın en çok sorulan tek sayısı — bu yüzden
# hesaplanamıyordu. *Bir çalışanı ölçüp ayrılışını ölçmemek, kadronun yarısını görmemektir.*

_EGITIM_KONULARI = [
    ("İSG Temel Eğitimi", "Zorunlu", 16), ("Renk Ölçüm ve Lab", "Teknik", 24),
    ("Makine Kullanımı RAM", "Teknik", 32), ("Kalite Yönetim Sistemi", "Kalite", 8),
    ("Kimyasal Güvenliği", "Zorunlu", 12), ("Yangın ve Tahliye", "Zorunlu", 6),
    ("Yalın Üretim", "Gelişim", 24), ("Enerji Verimliliği", "Gelişim", 8),
    ("İlk Yardım", "Zorunlu", 16), ("OEKO-TEX Uygunluk", "Kalite", 8),
    ("Liderlik ve Ekip", "Gelişim", 20), ("Excel ve Raporlama", "Gelişim", 12),
]


def _ik(con) -> dict[str, int]:
    # 🔴 İKİNCİ ÖLÇÜLEN HATAM: `giris_tarihi` diye bir alan **yok** — adı `ise_giris`.
    # Alanı okumadan yazdım, `gir_i` `None` kaldı ve `personel_hareketleri` GİRİŞ
    # satırı **hiç üretmedi** (8 satır çıktı, 29 olması gerekirken).
    #
    # > ⚠ Bu, bu deponun defterindeki **"bir alan adını okumadan yazmak"** sınıfının
    # > dördüncü tekrarı. Ve sinsi olan yanı: kod **çalıştı**, hata vermedi, yalnız
    # > tablonun yarısını sessizce boş bıraktı. *Bir sütunu yanlış adlandırmak
    # > çökmez — eksik cevap üretir, ki fark edilmesi çok daha zordur.*
    #
    # Sütun adları artık **sorularak** alınıyor, varsayılarak değil.
    personel = con.execute(
        "SELECT p.personel_kodu, p.ad_soyad, p.departman, p.vardiya, "
        "       o.ise_giris, o.pozisyon, o.egitim "
        "FROM personel p LEFT JOIN personel_ozluk o USING (personel_kodu)"
    ).fetchall()

    egitim, katilim, perf, alim, kaza, hareket = [], [], [], [], [], []
    for y, a in _aylar(GENIS_BAS, GENIS_SON):
        for konu, kat, saat in RNG.sample(_EGITIM_KONULARI, k=RNG.randint(1, 4)):
            ek = f"EGT-{y}{a:02d}-{len(egitim) + 1:04d}"
            egitim.append((ek, konu, kat, saat, _tarih(y, a, RNG.randint(3, 26)),
                           RNG.choice(["İç Eğitmen", "TSE", "Dış Danışman", "OSGB"]),
                           round(saat * RNG.uniform(180, 640), 2),
                           RNG.choice(["Salon", "Saha", "Online"])))
            for pk, ad, dep, vrd, _g, _p, _e in RNG.sample(personel, k=min(len(personel), RNG.randint(4, 18))):
                puan = round(RNG.uniform(55, 100), 1)
                katilim.append((ek, pk, ad, dep, saat, puan,
                                "BAŞARILI" if puan >= 60 else "TEKRAR",
                                _tarih(y, a, RNG.randint(3, 26))))

    for y in range(2022, 2027):
        for pk, ad, dep, vrd, _g, _p, _e in personel:
            if y == 2026:
                continue                                   # yıl kapanmadı, değerlendirme yok
            hedef = round(RNG.uniform(2.4, 4.8), 2)
            gercek = round(min(5.0, max(1.0, hedef + RNG.gauss(0, 0.55))), 2)
            perf.append((f"PRF-{y}-{pk}", y, pk, ad, dep, hedef, gercek,
                         round(gercek - hedef, 2),
                         "A" if gercek >= 4.2 else ("B" if gercek >= 3.4 else ("C" if gercek >= 2.6 else "D")),
                         round(RNG.uniform(0, 0.35) if gercek >= 3.4 else 0.0, 3),
                         RNG.choice(["Terfi adayı", "Gelişim planı", "Devam", "Devam", "Yakın takip"])))

    _asama = ["Başvuru", "Ön Eleme", "Teknik Mülakat", "İK Mülakatı", "Teklif", "İşe Başladı", "Reddedildi"]
    for y, a in _aylar(GENIS_BAS, GENIS_SON):
        for _ in range(RNG.randint(2, 9)):
            asama = RNG.choices(_asama, weights=[10, 8, 6, 5, 3, 2, 7])[0]
            bas = _tarih(y, a, RNG.randint(1, 28))
            alim.append((f"IAL-{y}{a:02d}-{len(alim) + 1:04d}",
                         RNG.choice(["Operatör", "Lab Teknisyeni", "Vardiya Amiri", "Bakım Teknisyeni",
                                     "Kalite Uzmanı", "Muhasebe Uzmanı", "Satış Temsilcisi", "Planlamacı"]),
                         RNG.choice(["Üretim", "Kalite", "Bakım", "Mali İşler", "Satış", "Planlama"]),
                         asama, bas,
                         bas + timedelta(days=RNG.randint(5, 70)) if asama in ("İşe Başladı", "Reddedildi") else None,
                         RNG.choice(["Kariyer sitesi", "Referans", "İŞKUR", "Sosyal medya", "Danışman"]),
                         RNG.randint(1, 6)))

    # İSG — kaza. *Sıklık ve ağırlık oranı olmadan bir üretim tesisinin İK tablosu eksiktir.*
    for y, a in _aylar(GENIS_BAS, GENIS_SON):
        # 🔴 EKİLİ OLAY: gece vardiyası personel devri → kaza sayısı o pencerede artar.
        _isg_carp = OL.carpan("personel_devri", _tarih(y, a, 15), "Gece")
        _taban = RNG.choices([0, 0, 1, 1, 2, 3], weights=[30, 25, 20, 12, 8, 5])[0]
        for _k in range(_taban + (int(_isg_carp * 2) if _isg_carp > 1.0 else 0)):
            pk, ad, dep, vrd, _g, _p, _e = RNG.choice(personel)
            if _isg_carp > 1.0 and _k >= _taban:
                vrd = "Gece"           # ekilen olay **gece vardiyasına** yazılır
            kayip = RNG.choices([0, 1, 2, 3, 5, 8, 15, 30], weights=[35, 20, 12, 10, 8, 7, 5, 3])[0]
            kaza.append((f"ISG-{y}{a:02d}-{len(kaza) + 1:04d}", _tarih(y, a, RNG.randint(1, 28)),
                         pk, ad, dep, vrd,
                         RNG.choice(["Sıkışma", "Kimyasal temas", "Düşme", "Kesik", "Yanık",
                                     "Kaldırma-taşıma", "Elektrik"]),
                         RNG.choice(["Ramöz", "Boya Mutfağı", "Depo", "Kazan Dairesi", "Sevkiyat", "Lab"]),
                         "RAMAK KALA" if kayip == 0 else ("HAFİF" if kayip <= 3 else "CİDDİ"),
                         kayip, RNG.choice(["KKD kullanılmadı", "Dikkatsizlik", "Ekipman arızası",
                                            "Talimata uyulmadı", "Zemin kaygan"])))

    # Personel hareketleri — giriş özlükten GERÇEK, çıkış türetilir.
    for pk, ad, dep, vrd, gir, _p, _e in personel:
        if isinstance(gir, date):
            hareket.append((pk, ad, dep, "GİRİŞ", gir, None, None))
        if RNG.random() < 0.27:                            # dönem içinde ayrılanlar
            cik = GENIS_BAS + timedelta(days=RNG.randint(200, 1600))
            hareket.append((pk, ad, dep, "ÇIKIŞ", None, cik,
                            RNG.choice(["İstifa", "Emeklilik", "Sözleşme sonu", "Performans",
                                        "Devamsızlık", "Başka iş"])))
    n1 = _yaz(con, "egitimler",
              "egitim_kodu VARCHAR, konu VARCHAR, kategori VARCHAR, saat INTEGER, tarih DATE, "
              "egitmen VARCHAR, maliyet DOUBLE, yer VARCHAR", egitim)
    n2 = _yaz(con, "egitim_katilim",
              "egitim_kodu VARCHAR, personel_kodu VARCHAR, ad_soyad VARCHAR, departman VARCHAR, "
              "saat INTEGER, sinav_puani DOUBLE, sonuc VARCHAR, tarih DATE", katilim)
    n3 = _yaz(con, "performans_degerlendirme",
              "degerlendirme_no VARCHAR, yil INTEGER, personel_kodu VARCHAR, ad_soyad VARCHAR, "
              "departman VARCHAR, hedef_puan DOUBLE, gerceklesen_puan DOUBLE, sapma DOUBLE, "
              "not_harfi VARCHAR, prim_orani DOUBLE, karar VARCHAR", perf)
    n4 = _yaz(con, "ise_alim",
              "basvuru_no VARCHAR, pozisyon VARCHAR, departman VARCHAR, asama VARCHAR, "
              "basvuru_tarihi DATE, sonuc_tarihi DATE, kaynak VARCHAR, mulakat_sayisi INTEGER", alim)
    n5 = _yaz(con, "is_kazalari",
              "kaza_no VARCHAR, tarih DATE, personel_kodu VARCHAR, ad_soyad VARCHAR, "
              "departman VARCHAR, vardiya VARCHAR, kaza_turu VARCHAR, bolge VARCHAR, "
              "siddet VARCHAR, is_gunu_kaybi INTEGER, kok_neden VARCHAR", kaza)
    n6 = _yaz(con, "personel_hareketleri",
              "personel_kodu VARCHAR, ad_soyad VARCHAR, departman VARCHAR, hareket_turu VARCHAR, "
              "giris_tarihi DATE, cikis_tarihi DATE, cikis_nedeni VARCHAR", hareket)
    return {"egitimler": n1, "egitim_katilim": n2, "performans_degerlendirme": n3,
            "ise_alim": n4, "is_kazalari": n5, "personel_hareketleri": n6}


# ═══════════════════════════════════════════════════════════════════════════════
# 7 · BAKIM · SATINALMA · LOJİSTİK
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 **`bakim_planlari` ölçüldü: 11 satır, ve 2024-02'de ÖLÜYOR.** Yani 29 aylık
# verinin 27 ayında bakım planı **yok**. Katalogda görünen, veride olmayan bir tablo
# *"planlı bakım nasıl gidiyor"* sorusuna boş cevap verir — ve **boş cevap, yanlış
# cevaptan daha az fark edilir**. Buradaki `bakim_is_emirleri` gerçek `ariza_kayitlari`
# üzerine kurulur ve tüm dönemi kapsar.

def _bakim_tedarik(con) -> dict[str, int]:
    arizalar = con.execute(
        "SELECT ariza_no, tarih, makine, ariza_tipi, durus_dakika, yedek_parca_maliyet "
        "FROM ariza_kayitlari ORDER BY tarih"
    ).fetchall()
    ie, parca_hrk = [], []
    _PARCALAR = [("YP-101", "Rulman 6205", "Mekanik"), ("YP-102", "Kayış B-1250", "Mekanik"),
                 ("YP-103", "Termokupl PT100", "Elektrik"), ("YP-104", "Kontaktör 40A", "Elektrik"),
                 ("YP-105", "Pnömatik valf", "Pnömatik"), ("YP-106", "Sirkülasyon pompası", "Mekanik"),
                 ("YP-107", "Rezistans 6kW", "Elektrik"), ("YP-108", "Keçe seti", "Sarf"),
                 ("YP-109", "Filtre kartuşu", "Sarf"), ("YP-110", "Enkoder", "Elektronik")]
    for i, (ano, trh, mak, tip, dk, maliyet) in enumerate(arizalar):
        # ⚠ Plansız/planlı ayrımı: arıza kaydı **plansızdır** (makine durdu, sonra
        # müdahale edildi). Planlı bakım ayrı üretilir — ikisini karıştırmak
        # "planlı bakım oranı" ölçüsünü anlamsız yapardı.
        ie.append((f"BIE-{trh.year}-{i + 1:05d}", ano, trh, mak, "PLANSIZ", tip,
                   int(dk or 0), round(float(maliyet or 0), 2),
                   RNG.choice(["Bakım Ekibi", "Dış Servis", "Operatör"]),
                   RNG.randint(1, 4), "KAPALI"))
        if RNG.random() < 0.55:
            pk, pa, pg = RNG.choice(_PARCALAR)
            parca_hrk.append((f"YPH-{trh.year}-{len(parca_hrk) + 1:05d}", pk, pa, pg, trh,
                              "ÇIKIŞ", RNG.randint(1, 4), round(float(maliyet or 0), 2), mak, ano))
    # Planlı bakım — her makine için periyodik, TÜM dönemi kapsar.
    makineler = [r[0] for r in con.execute("SELECT makine FROM makineler").fetchall()]
    bas, son = con.execute("SELECT min(tarih), max(tarih) FROM partiler").fetchone()
    for mak in makineler:
        g = bas
        while g <= son:
            ie.append((f"BIE-P-{mak[:4]}-{g:%Y%m%d}", None, g, mak, "PLANLI",
                       RNG.choice(["Periyodik Yağlama", "Kalibrasyon", "Filtre Değişimi",
                                   "Genel Kontrol", "Kayış Gerginlik"]),
                       RNG.randint(30, 240), round(RNG.uniform(800, 9500), 2),
                       "Bakım Ekibi", RNG.randint(1, 3), "KAPALI"))
            g += timedelta(days=RNG.choice([28, 30, 45, 60]))
    n1 = _yaz(con, "bakim_is_emirleri",
              "is_emri_no VARCHAR, ariza_no VARCHAR, tarih DATE, makine VARCHAR, tur VARCHAR, "
              "konu VARCHAR, sure_dk INTEGER, maliyet DOUBLE, ekip VARCHAR, kisi_sayisi INTEGER, "
              "durum VARCHAR", ie)
    n2 = _yaz(con, "yedek_parca_kartlari",
              "parca_kodu VARCHAR, parca_adi VARCHAR, grup VARCHAR, kritik_stok INTEGER, "
              "guncel_stok INTEGER, birim_fiyat DOUBLE, tedarik_suresi_gun INTEGER",
              [(pk, pa, pg, RNG.randint(2, 10), RNG.randint(0, 40),
                round(RNG.uniform(180, 24_000), 2), RNG.randint(3, 45))
               for pk, pa, pg in _PARCALAR])
    n3 = _yaz(con, "yedek_parca_hareketleri",
              "hareket_no VARCHAR, parca_kodu VARCHAR, parca_adi VARCHAR, grup VARCHAR, "
              "tarih DATE, hareket_turu VARCHAR, miktar INTEGER, tutar DOUBLE, makine VARCHAR, "
              "ariza_no VARCHAR", parca_hrk)

    # Tedarikçi karnesi — GERÇEK satınalma siparişlerinden. *Bağımsız bir skor,
    # "hangi tedarikçi sorunlu" sorusunu veriden kopuk cevaplatırdı.*
    tsp = con.execute(
        "SELECT tedarikci_kodu, unvan FROM tedarikciler"
    ).fetchall()
    karne = []
    for y in range(2024, 2027):
        for c in (1, 2, 3, 4):
            if (y, c) > (2026, 2):
                continue
            for tk, unv in tsp:
                kal = round(RNG.uniform(62, 99), 1)
                trm = round(RNG.uniform(58, 100), 1)
                fyt = round(RNG.uniform(55, 97), 1)
                gnl = round((kal * 0.45 + trm * 0.35 + fyt * 0.20), 1)
                karne.append((y, c, tk, unv, kal, trm, fyt, gnl,
                              "A" if gnl >= 85 else ("B" if gnl >= 70 else "C"),
                              RNG.randint(0, 8), RNG.randint(0, 5)))
    n4 = _yaz(con, "tedarikci_degerlendirme",
              "yil INTEGER, ceyrek INTEGER, tedarikci_kodu VARCHAR, unvan VARCHAR, "
              "kalite_skoru DOUBLE, termin_skoru DOUBLE, fiyat_skoru DOUBLE, genel_skor DOUBLE, "
              "sinif VARCHAR, red_adedi INTEGER, gecikme_adedi INTEGER", karne)

    # Lojistik — GERÇEK irsaliyelerden sevkiyat emri.
    irs = con.execute(
        "SELECT irsaliye_no, tarih, cari_kodu FROM irsaliyeler ORDER BY tarih"
    ).fetchall()
    _ARAC = [(f"34 {h} {n:03d}", t, k) for h, n, t, k in
             [("ABC", 101, "Tır", 24_000), ("DEF", 202, "Kamyon", 12_000),
              ("GHI", 303, "Kamyonet", 3_500), ("JKL", 404, "Tır", 24_000),
              ("MNO", 505, "Kamyon", 12_000), ("PRS", 606, "Kamyonet", 3_500)]]
    sevk = []
    for i, (ino, trh, ck) in enumerate(irs):
        plaka, tur, kap = RNG.choice(_ARAC)
        km = RNG.randint(15, 1250)
        sevk.append((f"SVK-{trh.year}-{i + 1:05d}", ino, trh, ck, plaka, tur, km,
                     round(km * RNG.uniform(18, 34), 2),
                     RNG.choice(["İstanbul", "Bursa", "İzmir", "Denizli", "Gaziantep",
                                 "Tekirdağ", "Kahramanmaraş", "Adana"]),
                     RNG.choice(["Kendi Filo", "Kendi Filo", "Sözleşmeli", "Spot"]),
                     RNG.choices([0, 0, 0, 1, 2], weights=[60, 15, 10, 10, 5])[0]))
    n5 = _yaz(con, "sevkiyat_emirleri",
              "sevkiyat_no VARCHAR, irsaliye_no VARCHAR, tarih DATE, musteri_kod VARCHAR, "
              "plaka VARCHAR, arac_turu VARCHAR, mesafe_km INTEGER, nakliye_tutar DOUBLE, "
              "varis_il VARCHAR, tasima_sekli VARCHAR, gecikme_gun INTEGER", sevk)
    n6 = _yaz(con, "araclar",
              "plaka VARCHAR, arac_turu VARCHAR, kapasite_kg INTEGER, model_yili INTEGER, "
              "durum VARCHAR",
              [(p, t, k, RNG.randint(2016, 2025), RNG.choice(["Aktif", "Aktif", "Bakımda"]))
               for p, t, k in _ARAC])
    return {"bakim_is_emirleri": n1, "yedek_parca_kartlari": n2,
            "yedek_parca_hareketleri": n3, "tedarikci_degerlendirme": n4,
            "sevkiyat_emirleri": n5, "araclar": n6}


ZINCIRLER = (_butce, _finans, _satis, _kalite, _uretim, _ik, _bakim_tedarik)


def genislet(con) -> dict[str, int]:
    """Tüm zincirleri koşar. `build_data.build()` sonunda çağrılır.

    🔴 Sonunda **ekili olaylar doğrulanır**: her olayın veride gerçekten görünür
    olduğu SQL ile sınanır. *Ekilemeyen bir olay, ölçülemeyen bir ground truth'tur* —
    ve sessizce ekilmemiş bir olay, testi *"sistem bulamadı"* diye kırmızıya çevirir.
    Oysa bulunacak bir şey yoktur. **Bu ayrımı yapmayan bir ölçüm, ürünü kendi kusuru
    için suçlar.**
    """
    toplam: dict[str, int] = {}
    for fn in ZINCIRLER:
        toplam.update(fn(con))

    # Ekili olayların manifesti — testler bunu okur, elle altın cevap yazılmaz.
    _yaz(con, "ekili_olaylar",
         "kod VARCHAR, tur VARCHAR, baslangic DATE, bitis DATE, hedef_alan VARCHAR, "
         "hedef_deger VARCHAR, buyukluk DOUBLE, belirti VARCHAR, kok_neden VARCHAR, "
         "dogrulama_sql VARCHAR",
         [(o.kod, o.tur, o.baslangic, o.bitis, o.hedef_alan, o.hedef_deger,
           o.buyukluk, o.belirti, o.kok_neden, " ".join(o.dogrulama_sql.split()))
          for o in OL.OLAYLAR])
    toplam["ekili_olaylar"] = len(OL.OLAYLAR)

    sorunlar = OL.dogrula(con)
    if sorunlar:
        print("\n🔴 EKİLİ OLAY DOĞRULAMASI BAŞARISIZ:")
        for x in sorunlar:
            print(f"   - {x}")
        print("   ⚠ Bu olaylar için ground truth YOK — ilgili testler ölçüm "
              "kuramaz, ürünü suçlayamaz.")
    else:
        print(f"\n✅ {len(OL.OLAYLAR)} ekili olayın hepsi veride doğrulandı "
              "(ground truth SQL ile bulunabiliyor)")
    return toplam


if __name__ == "__main__":                                        # pragma: no cover
    con = duckdb.connect(str(DB))
    toplam = genislet(con)
    for k, v in toplam.items():
        print(f"  {k:28s} {v:>8d} satır")
    con.close()
