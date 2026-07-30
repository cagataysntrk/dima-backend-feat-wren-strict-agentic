# Logo 3 serisi kaynak kuralları

- Tek DB çok firma/dönem tutar: tablolar `LG_<FFF>_<PP>_*` (dönemli) ve `LG_<FFF>_*`
  (kart/dönemsiz) öneklidir. Bu şirketin modelleri TEK firma/dönem kapsamına bağlıdır —
  başka firmanın tablosuna dokunulmaz.
- Cari hareketlerde `SIGN`: 0 = BORÇ, 1 = ALACAK; tutar `AMOUNT`. Bakiye = borç − alacak.
- Faturalarda `TRCODE`: 1 = mal alım faturası, 8 = toptan satış faturası;
  net tutar `NETTOTAL`, brüt `GROSSTOTAL`.
- Fatura satırlarında `IOCODE`: 1-2 = giriş (alım), 3-4 = çıkış (satış/sevk);
  miktar `AMOUNT`, satır tutarı `TOTAL`.
- `CANCELLED = 1` satırlar iptaldir; tüm toplamlarda dışlanır.
- Kimlikler `LOGICALREF` tabanlıdır: cari adı `cari_kartlar.DEFINITION_`, stok adı
  `stok_kartlari.NAME`; hareket tablolarındaki `CLIENTREF`/`STOCKREF` bu kartlara bağlanır.
- Tarih kolonu `DATE_` (datetime); alan adlarının sonundaki alt çizgi Logo adlandırmasıdır.
