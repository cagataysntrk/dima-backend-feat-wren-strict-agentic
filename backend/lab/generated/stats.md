# Sorgu Korpus İstatistikleri

Son güncelleme: 2026-07-24 22:29:02

## Toplam
- **Toplam tekrarsız sorgu**: 223619
- **Son turda eklenen**: +761

## Zorluk Kırılımı
- Zorluk 1: 56515
- Zorluk 2: 88197
- Zorluk 3: 71690
- Zorluk 4: 6885
- Zorluk 5: 332

## n_turns Dağılımı
- 1 adım: 222900
- 2 adım: 40
- 3 adım: 512
- 4 adım: 45
- 5 adım: 79
- 6 adım: 7
- 7 adım: 14
- 8 adım: 3
- 10 adım: 10
- 12 adım: 3
- 15 adım: 4
- 18 adım: 1
- 20 adım: 1

## Şirket Kırılımı
- boyahane: 119876
- gitas: 47488
- gulteks: 32376
- atiksan: 23799
- generic-perakende: 10
- generic-gida: 10
- generic-metal: 10
- generic-kimya: 10
- generic-insaat: 10
- generic-lojistik: 10
- generic-mobilya: 10
- generic-otomotiv: 10

## Sektör Kırılımı
- tekstil-boyahane: 119876
- tarim-ticareti: 47488
- kumas-ticareti: 32376
- geri-donusum: 23799
- perakende: 10
- gida: 10
- metal: 10
- kimya: 10
- insaat: 10
- lojistik: 10
- mobilya: 10
- otomotiv-yan-sanayi: 10

## Kullanıcı Tipi Kırılımı
- satis_muduru: 83129
- veri_analisti: 79093
- patron: 46976
- finans_uzmani: 3821
- satin_alma: 2946
- muhasebeci: 2936
- depo_sorumlusu: 2846
- uretim_muduru: 1071
- saha_personeli: 801

## En Sık Etiketler (Top 30)
- ticaret: 37580
- phrasing-matrix: 34400
- parti: 34016
- oee: 24792
- top3: 23930
- top5: 23140
- top10: 23140
- cari: 22587
- surdurulebilirlik: 16321
- mal: 15415
- alim_tutari: 12887
- satis_tutari: 12382
- hafta_gunu: 11016
- atiksan: 11010
- alim_miktari: 8056
- makine: 7920
- satis_miktari: 7826
- toplam_fire_kg: 7454
- bakiye: 7304
- toplam_alacak: 6796
- cari_kodu: 6768
- toplam_borc: 6478
- yaslandirma: 5500
- kumas_cinsi: 5472
- asama: 5472
- hareket_sayisi: 5336
- musteri: 5184
- net_miktar: 5124
- satis_fatura_sayisi: 5120
- kiririm-matrix: 4704

## Boşluk Analizi
- Jenerik sektörler (class-b): 244 sorgu
- Multi-cube: 120 sorgu
- Cross-cube: 4 sorgu
- Forecast/what-if: 44 sorgu
- Hata senaryoları: 32 sorgu
- Konuşma dili: 132 sorgu
- Çok-adımlı (3+ tur): 679 kayıt

## Bir Sonraki Koşu
- Daha fazla atiksan çok-adımlı (geri-dönüşüm operasyonu)
- Türkçe NLP forum ve muhasebe forum sorularından gerçek ifadeler
- Farklı yazım varyantları (q→ğ, ü→u vb. mobil klavye hataları)
- Hedef: 400.000+ tekrarsız sorgu

## Kaynaklar
- demo/packs — cube metadata
- lab/nl_corpus.py — REAL_PHRASINGS
- app/archetypes.py — ölçü arketipleri