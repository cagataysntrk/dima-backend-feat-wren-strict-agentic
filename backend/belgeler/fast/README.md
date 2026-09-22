# DIMA Fast Track — Developer Entry Point

Bu klasör üçüncü ürün yolunun branch-local otoritesidir.

## Amaç

Metabase'i analytics substrate olarak kullanıp Dima'yı:
- conversational analyst,
- bounded research,
- root-cause/driver analysis,
- evidence,
- dashboard,
- report,
- decision

ürünü haline getirmek.

Wren veya DimaSemanticSpec ilk ürünün kritik yolunda değildir.

## İlk okuma

1. DIMA_FAST_TRACK_ROADMAP.md
2. DIMA_FAST_SOURCE_LOCK.md
3. ../../../DIMA-FAST-DURUM.md
4. ../../../DIMA-FAST-OPERASYON.md
5. ../../../DIMA-FAST-DENETIM.md
6. aktif predev review

## Klasör düzeni

- predev/ — ticket başlamadan önce
- receipts/failures/ — RED/root-cause receipts
- receipts/decisions/ — architecture/product decisions
- receipts/live/ — real Metabase/model run receipts
- receipts/benchmarks/ — frozen gate sonuçları

Boş receipt klasörleri dosya gerektiğinde oluşturulur.

## En önemli kural

Source branches yalnız okunur.

Fast Track dışına write yok.
