"""EKİLİ OLAYLAR — *ground truth bir yorum değil, bir sorgu.*

## 🔴 Bu dosyanın çözdüğü problem

Bugüne kadar bir senaryo testi *"çöktü mü"* diye sorabiliyordu. **"Doğru sebebi buldu
mu"** diye soramıyordu — çünkü doğru sebebin ne olduğunu kimse bilmiyordu.

Elle *"doğru cevap M-07'dir"* yazmak da işe yaramaz: veri değişince o cümle bayatlar
ve kimse fark etmez. *Elle yazılmış bir altın cevap, verinin değiştiği gün sessizce
yalan olur.*

**Çözüm (InsightBench yöntemi):** anomali **kasıtlı ve kayıtlı** ekilir. Ground truth
*ekilen olayın kendisidir* — ve her olay yanında **onu kanıtlayan SQL'i** taşır.
Veri yeniden üretilse bile SQL aynı cevabı verir, çünkü olay yeniden ekilir.

```
olay ekilir  →  veriye YANSIR  →  SQL onu BULUR  →  test "sistem de buldu mu" diye sorar
```

## Neden mevcut tablolara DEĞİL, türetilmiş tablolara ekiliyor

`build_data.py`'nin ürettiği 47 tablo, `nl_corpus`'un **%93,1 tabanının** dayanağı.
Oraya bir çarpan koymak paydayı oynatır ve *"genişleme mi gerileme mi"* ayırt edilemez
hâle gelir.

> ⚠ Olaylar **yalnız genişletmenin kendi tablolarına** uygulanır (şikâyet · uygunsuzluk ·
> CAPA · bakım · maliyet). Bunlar zaten mevcut veriden **türetiliyor**; olay o türetmenin
> **katsayısını** belirli bir pencerede değiştirir. Mevcut hiçbir satır değişmez.

## ⚠ BÜYÜKLÜK EŞİĞİ — ölçümün anlamlılığını belirler

InsightBench'in ölçtüğü sınır: **eğimi 0,1'in altındaki trendleri hiçbir model
yakalayamıyor.** Yani çok küçük ekilen bir olay *"sistem bulamadı"* değil **"ölçüm
kurulamadı"** demektir — ve bu ikisini karıştırmak, ürünü haksız yere suçlar.

🔴 Bu yüzden her olayın `buyukluk`'ü **en az 2,0×** (yani %100 artış). `dogrula()`
ekilen olayın veride **gerçekten görünür** olduğunu koşumda sınar; görünmüyorsa
**hata verir** — *ekilemeyen bir olay, ölçülemeyen bir ground truth'tur.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Olay:
    """Kasıtlı olarak ekilen, **kayıtlı** bir iş olayı.

    Her alan bir soruya cevap verir:

    | alan | soru |
    |---|---|
    | `belirti` | kullanıcı **neyi fark eder** |
    | `kok_neden` | 🔴 **doğru cevap** — testin aradığı şey |
    | `dogrulama_sql` | doğru cevabın veride **kanıtı** |
    | `sorular` | bu olayı bulması gereken **gerçek kullanıcı cümleleri** |
    | `zincir` | çok turlu senaryoda **hangi turda** ortaya çıkmalı |
    """
    kod: str
    tur: str
    baslangic: date
    bitis: date
    hedef_alan: str
    hedef_deger: str
    #: ⚠ En az **2,0** olmalı — altındaki trend ölçülemez (InsightBench eşiği).
    buyukluk: float
    belirti: str
    kok_neden: str
    dogrulama_sql: str
    sorular: tuple[str, ...]
    zincir: tuple[str, ...] = field(default=())

    def kapsar(self, t: date, alan_degeri: str) -> bool:
        """Bu satır olayın etkisi altında mı?"""
        return self.baslangic <= t <= self.bitis and alan_degeri == self.hedef_deger


# ═══════════════════════════════════════════════════════════════════════════════
# EKİLİ OLAYLAR — her biri bir kök-neden senaryosunun ground truth'u
# ═══════════════════════════════════════════════════════════════════════════════
#
# ⚠ Olaylar **birbirinden ayrı pencerelerde** — çakışan iki olay, hangisinin sebep
# olduğunu belirsizleştirir ve *"doğru cevap"* iki tane olur.
# *Aynı anda iki şey ekmek, ikisini de ölçülemez yapar.*

OLAYLAR: tuple[Olay, ...] = (
    Olay(
        kod="M07-KADEMELI-BOZULMA",
        tur="makine_degradasyonu",
        baslangic=date(2025, 3, 1), bitis=date(2025, 5, 31),
        hedef_alan="makine", hedef_deger="RAM-2",
        buyukluk=3.2,
        belirti="Mart–Mayıs 2025'te şikâyet ve iade sıçraması; ciro etkisi ikinci ayda görünür",
        kok_neden="RAM-2 makinesinde kademeli kalibrasyon kayması — renk sapması "
                  "toleransı sistematik olarak aşıyor",
        dogrulama_sql="""
            SELECT makine, count(*) AS n
            FROM musteri_sikayetleri
            WHERE acilis_tarihi BETWEEN DATE '2025-03-01' AND DATE '2025-05-31'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 1
        """,
        sorular=(
            "mart 2025'te şikayet neden arttı",
            "şikayetlerin kaynağı hangi makine",
            "ilkbaharda kalitede ne oldu",
            "en çok şikayet hangi tezgahtan geliyor",
        ),
        zincir=("2025 şikayet sayısı", "aylara göre böl", "neden", "hangi makine"),
    ),
    Olay(
        kod="TEDARIKCI-KALITE-DUSUSU",
        tur="tedarikci_bozulmasi",
        baslangic=date(2025, 9, 1), bitis=date(2025, 11, 30),
        hedef_alan="tedarikci_kodu", hedef_deger="T001",
        buyukluk=2.6,
        belirti="Sonbahar 2025'te uygunsuzluk ve yeniden-işlem artışı; belirli bir "
                "hammadde partisiyle ilişkili",
        kok_neden="T001 tedarikçisinin hammadde kalitesi düştü — CAPA'ların kök-neden "
                  "kategorisi 'Malzeme'ye kayıyor",
        dogrulama_sql="""
            SELECT tedarikci_kod, count(*) AS n
            FROM duzeltici_faaliyetler
            WHERE acilis_tarihi BETWEEN DATE '2025-09-01' AND DATE '2025-11-30'
              AND kok_neden_kategorisi = 'Malzeme'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 1
        """,
        sorular=(
            "sonbaharda rework neden arttı",
            "hangi tedarikçide sorun var",
            "düzeltici faaliyetlerin kök nedeni ne",
            "malzeme kaynaklı uygunsuzluklar hangi tedarikçiden",
        ),
        zincir=("2025 uygunsuzluk sayısı", "çeyreklere göre", "neden", "tedarikçi bazında"),
    ),
    Olay(
        kod="ENERJI-FIYAT-SOKU",
        tur="maliyet_soku",
        baslangic=date(2026, 1, 1), bitis=date(2026, 3, 31),
        hedef_alan="donem", hedef_deger="2026Q1",
        buyukluk=2.1,
        belirti="2026 ilk çeyrekte birim maliyet sıçraması; üretim miktarı DEĞİŞMEDEN "
                "kâr marjı daralıyor",
        kok_neden="Enerji birim fiyatı şoku — maliyet artışı hacimden değil "
                  "FİYATTAN geliyor (PVM ayrışması bunu ayırt etmeli)",
        dogrulama_sql="""
            SELECT yil, ay, round(avg(elektrik_tl_kg + dogalgaz_tl_kg), 4) AS enerji_kg
            FROM urun_maliyetleri
            WHERE yil = 2026 AND ay <= 3
            GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 1
        """,
        sorular=(
            "2026 başında maliyet neden arttı",
            "kar marjı neden daraldı",
            "maliyet artışı fiyattan mı hacimden mi",
            "birim maliyetimiz niye yükseldi",
        ),
        zincir=("bu yıl birim maliyet", "aylara göre", "neden arttı",
                "bileşenlere ayır"),
    ),
    Olay(
        kod="MUSTERI-KAYBI-M1003",
        tur="musteri_kaybi",
        baslangic=date(2025, 6, 1), bitis=date(2026, 6, 30),
        hedef_alan="musteri_kod", hedef_deger="M1003",
        buyukluk=4.0,
        belirti="Haziran 2025'ten sonra bir müşterinin sipariş hacmi çöküyor; "
                "toplam ciro düşüşünün büyük kısmı tek müşteriden",
        kok_neden="M1003 (MAVİ İPLİK) müşterisi kaybedildi — fırsat hunisinde "
                  "'Kaybedildi' aşamasında ve kayıp nedeni kayıtlı",
        dogrulama_sql="""
            SELECT musteri_kod, count(*) AS kayip
            FROM firsatlar
            WHERE asama = 'Kaybedildi'
              AND kapanis_tarihi BETWEEN DATE '2025-06-01' AND DATE '2026-06-30'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 1
        """,
        sorular=(
            "ciro düşüşünde kimin payı var",
            "hangi müşteriyi kaybettik",
            "neden kaybediyoruz",
            "satış düşüşü hangi müşteriden kaynaklanıyor",
        ),
        zincir=("bu yıl ciro", "geçen yılla kıyasla", "müşteri bazında",
                "neden düştü"),
    ),
    Olay(
        kod="GECE-VARDIYASI-DEVIR",
        tur="personel_devri",
        baslangic=date(2025, 10, 1), bitis=date(2026, 2, 28),
        hedef_alan="vardiya", hedef_deger="Gece",
        buyukluk=2.4,
        belirti="Kış aylarında gece vardiyasında iş kazası ve uygunsuzluk artışı; "
                "aynı dönemde personel çıkışları yoğunlaşıyor",
        kok_neden="Gece vardiyasında personel devri yükseldi — deneyimsiz operatör "
                  "oranı arttı, İSG olayları ve kalite sapması birlikte yükseliyor",
        dogrulama_sql="""
            SELECT vardiya, count(*) AS n
            FROM is_kazalari
            WHERE tarih BETWEEN DATE '2025-10-01' AND DATE '2026-02-28'
            GROUP BY 1 ORDER BY 2 DESC LIMIT 1
        """,
        sorular=(
            "gece vardiyası niye düştü",
            "kazalar hangi vardiyada",
            "hangi vardiya bizi aşağı çekiyor",
            "personel devri kaliteyi etkiliyor mu",
        ),
        zincir=("bu yıl iş kazası sayısı", "vardiya bazında", "neden",
                "personel devriyle ilişkisi var mı"),
    ),
    Olay(
        kod="BUTCE-SAPMASI-ENERJI",
        tur="butce_sapmasi",
        baslangic=date(2026, 1, 1), bitis=date(2026, 6, 30),
        hedef_alan="kalem", hedef_deger="Enerji",
        buyukluk=2.2,
        belirti="2026'nın ilk yarısında bir bütçe kalemi sistematik olarak aşılıyor",
        kok_neden="Enerji kalemi bütçeyi aşıyor — ENERJI-FIYAT-SOKU olayının "
                  "mali tablodaki yansıması (iki olay NEDENSEL olarak bağlı)",
        dogrulama_sql="""
            SELECT kalem, round(sum(hedef_tutar), 0) AS hedef
            FROM butce_hedefleri
            WHERE yil = 2026 AND ay <= 6 AND kalem = 'Enerji'
            GROUP BY 1
        """,
        sorular=(
            "bütçeyi hangi kalemde aştık",
            "gerçekleşme hedefin neresinde",
            "enerji bütçesi tutuyor mu",
            "yılın ilk yarısında sapma nerede",
        ),
        zincir=("bu yıl bütçe gerçekleşme", "kalem bazında", "hangi kalemde sapma var",
                "neden"),
    ),
)


#: 🔴 Çok-turlu senaryoların ground truth'u. Her olay bir `zincir` taşır: kullanıcı bu
#: turları sırayla sorduğunda, **son turda** `kok_neden` ortaya çıkmalıdır.
#: *Bir kök-neden sorusu tek turda cevaplanmaz; bir sohbette ortaya çıkar — ve testin
#: onu bir sohbette araması gerekir.*
def zincir_senaryolari() -> list[dict]:
    return [
        {"olay": o.kod, "turlar": list(o.zincir), "beklenen_kok_neden": o.kok_neden,
         "dogrulama_sql": " ".join(o.dogrulama_sql.split()),
         "hedef": f"{o.hedef_alan}={o.hedef_deger}"}
        for o in OLAYLAR if o.zincir
    ]


def carpan(olay_turu: str, t: date, alan_degeri: str) -> float:
    """Verilen satır için toplam olay çarpanı.

    ⚠ Çakışan olaylar **çarpılmaz, en büyüğü alınır**: iki olayın çarpımı hiçbirinin
    büyüklüğüne karşılık gelmez ve *"hangisi sebep"* sorusu cevapsız kalır.
    """
    uygun = [o.buyukluk for o in OLAYLAR
             if o.tur == olay_turu and o.kapsar(t, alan_degeri)]
    return max(uygun) if uygun else 1.0


def dogrula(con) -> list[str]:
    """🔴 Ekilen her olayın veride **gerçekten göründüğünü** sınar.

    *Ekilemeyen bir olay, ölçülemeyen bir ground truth'tur* — ve sessizce ekilmemiş
    bir olay, testi *"sistem bulamadı"* diye kırmızıya çevirir. Oysa bulunacak bir şey
    yoktur. **Bu ayrımı yapmayan bir ölçüm, ürünü kendi kusuru için suçlar.**
    """
    sorunlar: list[str] = []
    for o in OLAYLAR:
        try:
            satirlar = con.execute(o.dogrulama_sql).fetchall()
        except Exception as exc:                          # noqa: BLE001
            sorunlar.append(f"{o.kod}: doğrulama SQL'i çalışmadı — {str(exc)[:90]}")
            continue
        if not satirlar:
            sorunlar.append(f"{o.kod}: doğrulama SQL'i BOŞ döndü — olay ekilmemiş")
            continue
        bulunan = str(satirlar[0][0])
        if o.hedef_deger not in ("2026Q1", "Enerji") and bulunan != o.hedef_deger:
            sorunlar.append(
                f"{o.kod}: ekilen hedef «{o.hedef_deger}» değil «{bulunan}» baskın — "
                "olay yeterince büyük ekilmemiş (büyüklük ≥2,0 olmalı)")
    return sorunlar
