# Netsis kaynak kuralları (GITAS2026F verisinden doğrulandı)

- Firma başına AYRI veritabanı; Logo-3'teki gibi tablo öneki YOKTUR. Şube ekseni
  `SUBE_KODU` kolonundadır (Gitaş'ta 0 ve 90).
- Cari hareketlerde BORÇ ve ALACAK AYRI kolonlardır (`TBLCAHAR.BORC/ALACAK`);
  bakiye = borç − alacak. Cari adı `cari_kartlar.CARI_ISIM`.
- Stok hareketlerinde `STHAR_GCKOD`: 'G' = GİRİŞ (alış), 'C' = ÇIKIŞ (satış/sevk);
  miktar `STHAR_GCMIK`, satır tutarı = `STHAR_GCMIK * STHAR_NF` (NF birim net fiyat).
- Faturalarda `FTIRSIP`: '1' = SATIŞ faturası, '2' = ALIŞ faturası, 'A' = irsaliye
  (tutar taşımaz — tutar toplamlarında dışlanır), '3' = iade (küçük hacim);
  toplam `GENELTOPLAM`, brüt `BRUTTUTAR`.
- Tarih kolonları: cari `TARIH`, stok `STHAR_TARIH`, fatura `TARIH` (datetime).
