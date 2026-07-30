# Mikro V16 kaynak kuralları

- Cari hareketlerde `cha_tip`: 0 = BORÇ, 1 = ALACAK; tutar alanı `cha_meblag`.
  Bakiye = borç − alacak (pozitif bakiye: cari bize borçlu).
- Stok hareketlerinde `sth_tip`: 0 = GİRİŞ (alım/tedarik), 1 = ÇIKIŞ (satış/sevk);
  tutar `sth_tutar`, miktar `sth_miktar`.
- Fatura ayrı tablo DEĞİLDİR: alım/satım evrakları stok ve cari hareket
  tablolarında `*_evrak_tip`/`sth_evraktip` ile ayrışır.
- Cari kartın adı `cari_hesaplar.cari_unvan1`; hareket tablolarındaki kod alanları
  (`cha_kod`, `sth_cari_kodu`) bu karta bağlanır.
- Stok kartın adı `stoklar.sto_isim`; hareketteki `sth_stok_kod` bu karta bağlanır.
- Tarih alanları datetime'dır (`cha_tarihi`, `sth_tarih`); gün bazlı gruplama için
  tarihe indirgenerek kullanılır.
